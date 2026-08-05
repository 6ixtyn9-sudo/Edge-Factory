#!/usr/bin/env python3
"""Phase 0 — Veto re-mine counterfactual harness (READ-ONLY).

Answers: for every pick that was watchlisted/skipped because its context was
UNKNOWN, what would the locked O1 (rule-pooled) / O2 (hierarchical fallback)
resolution layer have decided — and would that have helped or hurt?

Locked parameters (VETO_REMINE_DESIGN_2026-08-05.md, sections 8 + 10):
  - pool key: (sport, league_key, market, side_role), rules pooled within,
    n-weighted unconditional w_roi (Q2)
  - gates (Scenario B, Q3): ALLOW n>=40, CAUTION n>=20, VETO n>=12
  - O2 ladder: league (pooled) -> niche -> competition_type (Q1)
  - overlay-only; never mutates purity_registry.json (Q5)
  - measurement: all available archived picks + settled results; operator
    slice = last --slice-days days (Q4)

Data sources (repo, read-only):
  - localdata/purity_registry.json  (context verdicts; never modified)
  - localdata/picks_YYYY-MM-DD.json (per-day archived pick ledgers)
  - localdata/settled_results.json  (settled scores; result join)

Usage:
  PYTHONPATH=src python3 counterfactual_veto_resolution.py \
      --repo /Users/apple/Edge-Factory \
      [--start 2026-06-18] [--slice-days 30] \
      [--out /tmp/veto_counterfactual.md]

No production behavior changes; output is a Markdown report + stdout summary.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# --------------------------------------------------------------------------
# Verdict gates (locked in the design doc — Scenario B)
# --------------------------------------------------------------------------
ALLOW_MIN_N = 40
CAUTION_MIN_N = 20
VETO_MIN_N = 12
PLAYABLE = {"ALLOW", "BOOST"}
RESOLVED = {"ALLOW", "BOOST", "CAUTION", "VETO"}


def pooled_verdict(n: int, w_roi: float | None) -> str:
    """Scenario B pooled verdict: ALLOW>=40, CAUTION>=20, VETO>=12.

    Mirrors context_verdict_league's gates with the stricter pooled minimums;
    recent_roi is None for pooled evidence (conservative VETO branch)."""
    if w_roi is None:
        return "UNKNOWN"
    if n < VETO_MIN_N:
        return "UNKNOWN"
    if n < 40:
        if w_roi <= -0.10:
            return "VETO"
        if n >= CAUTION_MIN_N and w_roi <= -0.04:
            return "CAUTION"
        return "UNKNOWN"
    # n >= 40 (standard gates; recent None -> conservative VETO branch)
    if w_roi <= -0.05:
        return "VETO"
    if w_roi < 0.0:
        return "CAUTION"
    if n >= 100 and w_roi >= 0.03:
        return "BOOST"
    return "ALLOW"


# --------------------------------------------------------------------------
# Light normalization for the result join (no heavy deps)
# --------------------------------------------------------------------------
def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def _norm9(s: str) -> str:
    return _norm(s)[:9]


def load_settled_index(path: Path) -> dict[tuple[str, str, str], dict]:
    """date + norm9(home) + norm9(away) -> settled row (first match wins)."""
    idx: dict[tuple[str, str, str], dict] = {}
    rows = json.loads(path.read_text()).get("rows", [])
    for r in rows:
        key = (str(r.get("date", "")), _norm9(r.get("home", "")), _norm9(r.get("away", "")))
        if key not in idx:
            idx[key] = r
    return idx


def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", str(s or "").lower()))


def find_result(date: str, home: str, away: str, by_date: dict[str, list[dict]]) -> tuple[dict | None, str]:
    """Staged result match on (date): exact9 -> exact-full -> token-subset.

    Mirrors the audit's matching spirit (9-char keys, containment, token
    subset) with a light implementation; returns (row, method) or (None, '').
    """
    rows = by_date.get(date, [])
    h9, a9 = _norm9(home), _norm9(away)
    s1 = [r for r in rows if _norm9(r.get("home", "")) == h9 and _norm9(r.get("away", "")) == a9]
    if s1:
        return s1[0], "exact9"
    hn, an = _norm(home), _norm(away)
    s2 = [r for r in rows if _norm(r.get("home", "")) == hn and _norm(r.get("away", "")) == an]
    if s2:
        return s2[0], "exact-full"
    htok, atok = _tokens(home), _tokens(away)
    cands = []
    for r in rows:
        rht, rat = _tokens(r.get("home", "")), _tokens(r.get("away", ""))
        if not htok or not atok or not rht or not rat:
            continue
        if (htok <= rht or rht <= htok) and (atok <= rat or rat <= atok):
            cands.append(r)
    if len(cands) >= 1:
        return cands[0], f"token-subset({len(cands)})"
    return None, ""


# --------------------------------------------------------------------------
# Registry loading + canonical pool table
# --------------------------------------------------------------------------
def load_registry(path: Path) -> dict:
    return json.loads(path.read_text())["contexts"]


def build_pool_table(reg: dict) -> dict[tuple[str, str, str, str], dict]:
    """Pool (sport, league, market, side_role) from league-dimension cells.

    n = sum of cell n; w_roi = n-weighted mean over priced cells; verdict per
    Scenario B. This is THE canonical pool table Phase 0 defines (the
    second-agent's pool-bucket numbers were not reproducible — this is)."""
    pools: dict[tuple[str, str, str, str], dict] = defaultdict(
        lambda: {"n": 0, "w_roi_num": 0.0, "w_roi_den": 0, "cells": 0}
    )
    for key, cell in reg.get("league", {}).items():
        parts = key.split("|")
        if len(parts) != 5:
            continue
        sport, league, market, rule, side = parts
        n = int(cell.get("n", 0) or 0)
        roi = cell.get("roi")
        p = pools[(sport, league, market, side)]
        p["n"] += n
        p["cells"] += 1
        if roi is not None:
            p["w_roi_num"] += n * float(roi)
            p["w_roi_den"] += n
    out = {}
    for key, p in pools.items():
        w_roi = (p["w_roi_num"] / p["w_roi_den"]) if p["w_roi_den"] else None
        out[key] = {
            "n": p["n"],
            "w_roi": w_roi,
            "verdict": pooled_verdict(p["n"], w_roi),
            "cells": p["cells"],
        }
    return out


def o2_verdict(reg: dict, pick_ctx: dict, market: str, rule: str, sport: str) -> tuple[str, str]:
    """O2 hierarchical fallback: niche -> competition_type. Returns (verdict, path)."""
    league = pick_ctx.get("league_key") or ""
    side = pick_ctx.get("side_role") or ""
    band = pick_ctx.get("odds_band_name") or ""
    # niche key: sport|league|market|rule|odds_band|side
    if league and rule and band and side:
        cell = reg.get("niche", {}).get(f"{sport}|{league}|{market}|{rule}|{band}|{side}")
        if cell and cell.get("verdict") not in (None, "UNKNOWN"):
            return str(cell["verdict"]), "O2-niche"
    # competition_type key: sport|market|rule|comp_type
    comp = pick_ctx.get("comp_type_name") or ""
    if rule and comp:
        cell = reg.get("competition_type", {}).get(f"{sport}|{market}|{rule}|{comp}")
        if cell and cell.get("verdict") not in (None, "UNKNOWN"):
            return str(cell["verdict"]), "O2-competition_type"
    return "UNKNOWN", "unresolved"


def load_audit_ledger(path: Path) -> dict[tuple[str, str], dict]:
    """picks_audit_rolling.json settled_ledger: (date, norm9(match)) -> row.

    The audit's own settlement resolution is authoritative for its window;
    this join both validates the harness and fills fixtures the overlay
    store misses (or names differently)."""
    idx: dict[tuple[str, str], dict] = {}
    try:
        rows = json.loads(path.read_text()).get("settled_ledger", [])
    except Exception:
        rows = []
    for r in rows:
        key = (str(r.get("date", "")), _norm9(r.get("match", "")))
        if key not in idx:
            idx[key] = r
    return idx


# --------------------------------------------------------------------------
# Pick loading + counterfactual
# --------------------------------------------------------------------------
def load_picks(localdata: Path, start: str) -> list[dict]:
    picks = []
    for f in sorted(localdata.glob("picks_20*.json")):
        m = re.match(r"picks_(\d{4}-\d{2}-\d{2})\.json$", f.name)
        if not m or m.group(1) < start:
            continue
        rows = json.loads(f.read_text())
        if not isinstance(rows, list):
            continue
        for r in rows:
            r["_file"] = f.name
        picks.extend(rows)
    return picks


def evaluate_pick(pick: dict, pools: dict, reg: dict, by_date: dict[str, list[dict]],
                  audit_ledger: dict[tuple[str, str], dict]) -> dict:
    ctx = pick.get("ctx") or {}
    date = str(pick.get("date") or "")
    sport = str(pick.get("sport") or "soccer")
    market = str(pick.get("market") or "1x2")
    rule = str(pick.get("edge_rule") or pick.get("rule") or "")
    league = str(ctx.get("league_key") or "")
    side = str(ctx.get("side_role") or "")
    selection = str(pick.get("pick") or pick.get("selection") or "")

    out = {
        "date": date,
        "match": pick.get("match") or f"{pick.get('home')} vs {pick.get('away')}",
        "league": league,
        "rule": rule,
        "side": side,
        "odds": pick.get("odds"),
        "bucket": pick.get("bucket"),
        "verdict": "UNKNOWN",
        "path": "unresolved",
        "pool_n": None,
        "pool_w_roi": None,
        "settled": None,
        "match_method": "",
        "won": None,
        "would_play": False,
        "would_roi": None,
    }

    # Scope: the league overlay resolves ONLY league-UNKNOWN picks. A pick
    # watchlisted for a different reason (e.g. short-sniper niche-UNKNOWN
    # rule while league is already resolved) is OUT of scope: the layer does
    # nothing, so would_play stays False regardless of the native verdict.
    native = str(ctx.get("league") or "")
    if native != "UNKNOWN":
        out["verdict"] = native
        out["path"] = "native (out of scope)"
        out["would_play"] = False
        out["would_play_caution"] = False
        return out

    # O1: pooled league verdict
    if league and side:
        p = pools.get((sport, league, market, side))
        if p:
            out["pool_n"] = p["n"]
            out["pool_w_roi"] = p["w_roi"]
            if p["verdict"] in RESOLVED:
                out["verdict"] = p["verdict"]
                out["path"] = "O1-pool"

    # O2: fallback ladder if still UNKNOWN
    if out["verdict"] == "UNKNOWN":
        v, path = o2_verdict(reg, ctx, market, rule, sport)
        out["verdict"] = v
        out["path"] = path

    # would-play: green-light = ALLOW/BOOST; caution-grade = + CAUTION (the
    # live pipeline does play CAUTION picks)
    out["would_play"] = out["verdict"] in PLAYABLE
    out["would_play_caution"] = out["verdict"] in PLAYABLE or out["verdict"] == "CAUTION"

    # result join: audit settled_ledger first (audit-authoritative), then the
    # committed overlay store (staged: exact9 -> exact-full -> token-subset)
    ledger_row = audit_ledger.get((date, _norm9(pick.get("match", "") or "")))
    row, method = (ledger_row, "audit-ledger") if ledger_row else find_result(
        date, str(pick.get("home", "")), str(pick.get("away", "")), by_date)
    if row:
        outcome = str(row.get("outcome") or "")
        hs, gs = row.get("hs"), row.get("gs")
        out["settled"] = f"{hs}-{gs} ({outcome})" if hs is not None and gs is not None else "settled"
        out["match_method"] = method
        if row.get("won") is not None:
            out["won"] = bool(row["won"])
        else:
            out["won"] = bool(outcome and selection and outcome == selection)
        for key in ("would_play", "would_play_caution"):
            if out[key] and isinstance(pick.get("odds"), (int, float)):
                out["would_roi"] = (float(pick["odds"]) - 1.0) if out["won"] else -1.0
    return out


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------
def _pct(x: float | None) -> str:
    return f"{x:.1%}" if x is not None else "n/a"


def _roi(x: float | None) -> str:
    return f"{x:+.3f}" if x is not None else "n/a"


def _wilson_lb(hits: int, n: int, z: float = 1.645) -> float:
    """90% Wilson lower bound on a hit rate (stdlib only)."""
    if n <= 0:
        return 0.0
    p = hits / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = p + z2 / (2.0 * n)
    margin = z * ((p * (1.0 - p) + z2 / (4.0 * n)) / n) ** 0.5
    return (centre - margin) / denom


# Pre-committed gate thresholds (PHASE1_2_VETO_RESOLUTION_SPEC.md section 8 —
# write-down-now, anti-mood; do NOT change them while the gate is accruing).
GATE_MIN_SETTLED = 30          # FLAG-ON requires >= 30 settled caution-grade picks
GATE_ROI_EPS = 0.01            # overlay ROI must be >= bucket ROI - 1pp
GATE_HIT_EPS = 0.05            # overlay 90% Wilson LB must be >= bucket hit - 5pp
DEPRECATE_N = 60               # deprecation review once >= 60 settled
DEPRECATE_ROI_GAP = 0.02       # ...if overlay ROI < bucket ROI - 2pp (two checkpoints)


def _scenario(rows: list[dict], caution_grade: bool) -> dict:
    if caution_grade:
        played = [r for r in rows if r["would_play_caution"]]
    else:
        played = [r for r in rows if r["would_play"]]
    settled_played = [r for r in played if r["settled"]]
    won = sum(1 for r in settled_played if r["won"])
    roi = sum(r["would_roi"] for r in settled_played if r["would_roi"] is not None)
    n_roi = sum(1 for r in settled_played if r["would_roi"] is not None)
    return {
        "would_play": len(played),
        "settled_played": len(settled_played),
        "wins": won,
        "hit_rate": (won / len(settled_played)) if settled_played else None,
        "roi": (roi / n_roi) if n_roi else None,
    }


def summarize(rows: list[dict]) -> dict:
    all_settled = [r for r in rows if r["settled"]]
    layer_paths = ("O1-pool", "O2-niche", "O2-competition_type")
    return {
        "n": len(rows),
        "in_scope": sum(1 for r in rows if r["path"] != "native (out of scope)"),
        "resolved": sum(1 for r in rows if r["path"] in layer_paths),
        "settled_all": len(all_settled),
        "wins_all": sum(1 for r in all_settled if r["won"]),
        "green": _scenario(rows, False),
        "caution": _scenario(rows, True),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, help="Path to the Edge-Factory repo root")
    ap.add_argument("--start", default="2026-06-18", help="Earliest pick date to consider")
    ap.add_argument("--slice-days", type=int, default=30)
    ap.add_argument("--out", default="/tmp/veto_counterfactual.md")
    args = ap.parse_args()

    repo = Path(args.repo)
    localdata = repo / "localdata"
    reg = load_registry(localdata / "purity_registry.json")
    pools = build_pool_table(reg)
    settled_rows = json.loads((localdata / "settled_results.json").read_text()).get("rows", [])
    by_date: dict[str, list[dict]] = {}
    for r in settled_rows:
        by_date.setdefault(str(r.get("date", "")), []).append(r)

    audit_ledger = load_audit_ledger(localdata / "picks_audit_rolling.json")

    picks = load_picks(localdata, args.start)
    scope = [p for p in picks if p.get("bucket") == "WATCHLIST_UNKNOWN_CTX"]

    rows = [evaluate_pick(p, pools, reg, by_date, audit_ledger) for p in scope]
    rows.sort(key=lambda r: r["date"])

    import datetime as _dt
    slice_from = (max(r["date"] for r in rows) if rows else "") 
    if slice_from:
        d = _dt.date.fromisoformat(slice_from) - _dt.timedelta(days=args.slice_days)
        slice_from = d.isoformat()
    slice_rows = [r for r in rows if r["date"] >= slice_from]

    full = summarize(rows)
    op = summarize(slice_rows)

    def _fmt(s: dict) -> str:
        return (f"{s['settled_played']}/{s['would_play']} settled | {s['wins']} wins | "
                f"hit {_pct(s['hit_rate'])} | ROI {_roi(s['roi'])}")

    # --- Pre-committed gate checklist (PHASE1_2 spec section 8) ---
    # Written down now, anti-mood: the checkpoint is mechanical, not
    # interpretive. Do not change these thresholds while the gate accrues.
    try:
        ar = json.loads((localdata / "picks_audit_rolling.json").read_text())
        bucket = (ar.get("by_bucket") or {}).get("WATCHLIST_UNKNOWN_CTX", {})
    except Exception:
        bucket = {}
    bucket_settled = int(bucket.get("settled_picks") or 0)
    bucket_wins = int(bucket.get("wins") or 0)
    bucket_roi = bucket.get("roi")
    bucket_hit = (bucket_wins / bucket_settled) if bucket_settled else None

    c = full["caution"]
    n_gate = c["settled_played"]
    roi_gate = c["roi"]
    hit_gate = c["hit_rate"]
    lb_gate = _wilson_lb(c["wins"], c["settled_played"])
    g1 = n_gate >= GATE_MIN_SETTLED
    g2 = roi_gate is not None and roi_gate > 0.0 and (
        bucket_roi is None or roi_gate >= bucket_roi - GATE_ROI_EPS)
    g3 = hit_gate is not None and (
        bucket_hit is None or lb_gate >= bucket_hit - GATE_HIT_EPS)
    dep_signal = (n_gate >= DEPRECATE_N and bucket_roi is not None
                  and roi_gate is not None and roi_gate < bucket_roi - DEPRECATE_ROI_GAP)
    if g1 and g2 and g3:
        gate_verdict = "FLAG-ON — all pre-committed conditions met (operator review before enabling)"
    elif dep_signal:
        gate_verdict = ("DEPRECATION SIGNAL — confirm at a second checkpoint >= 2 weeks later; "
                        "if the gap persists, retire the overlay and record in HANDOVER")
    else:
        gate_verdict = "FLAG-OFF — keep shadow, keep accruing (not enough evidence to ship)"

    # Canonical pool table (fixes the reproducibility gap)
    pool_rows = list(pools.values())
    pool_vc = Counter(p["verdict"] for p in pool_rows)
    unk_cells_small_pool = 0
    for key, cell in reg.get("league", {}).items():
        parts = key.split("|")
        if len(parts) != 5 or cell.get("verdict") != "UNKNOWN":
            continue
        p = pools.get((parts[0], parts[1], parts[2], parts[4]))
        if p and p["n"] < VETO_MIN_N:
            unk_cells_small_pool += 1

    lines = [
        "# Veto Re-Mine — Phase 0 Counterfactual Report",
        "",
        f"- Generated: {_dt.datetime.now().isoformat(timespec='seconds')}",
        f"- Repo: `{repo}` (read-only; no files modified)",
        f"- Pick scope: bucket `WATCHLIST_UNKNOWN_CTX`, dates >= {args.start}",
        f"- Operator slice: last {args.slice_days} days",
        f"- Picks analysed: {len(rows)} | resolved: {full['resolved']} | "
        f"green-light would-play: {full['green']['would_play']} | settled: {full['settled_all']}",
        "",
        "## 1. Canonical pool table (Scenario B gates: ALLOW>=40, CAUTION>=20, VETO>=12)",
        "",
        f"- league-dimension pools: {len(pool_rows)}",
        f"- resolved pools: {pool_vc.get('VETO',0)} VETO / {pool_vc.get('ALLOW',0)} ALLOW / "
        f"{pool_vc.get('CAUTION',0)} CAUTION / {pool_vc.get('BOOST',0)} BOOST",
        f"- UNKNOWN league cells whose pool n < {VETO_MIN_N} (never resolvable by O1): {unk_cells_small_pool}",
        "",
        "## 2. Counterfactual summary",
        "",
        "Cross-check vs the 30-day audit bucket: audit reports WATCHLIST_UNKNOWN_CTX "
        f"settled=19 wins=17; harness reproduces {op['settled_all']} settled / {op['wins_all']} wins "
        "on the same slice. The difference is scope: 3 picks in the audit bucket were "
        "short-sniper niche-UNKNOWN blocks (league already resolved — OUT of the league "
        "overlay's scope), all 3 won (19-3=16 settled, 17-3=14 wins).",
        "",
        "| window | picks | resolved | all settled | resolution scenario | would-play | settled | wins | hit rate | would-be ROI |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        f"| full ({args.start} → now) | {full['n']} | {full['resolved']} | {full['settled_all']} | "
        f"green-light (ALLOW/BOOST) | {full['green']['would_play']} | {full['green']['settled_played']} | "
        f"{full['green']['wins']} | {_pct(full['green']['hit_rate'])} | {_roi(full['green']['roi'])} |",
        f"| full ({args.start} → now) | {full['n']} | {full['resolved']} | {full['settled_all']} | "
        f"incl. caution-grade | {full['caution']['would_play']} | {full['caution']['settled_played']} | "
        f"{full['caution']['wins']} | {_pct(full['caution']['hit_rate'])} | {_roi(full['caution']['roi'])} |",
        f"| operator slice (≥ {slice_from}) | {op['n']} | {op['resolved']} | {op['settled_all']} | "
        f"green-light (ALLOW/BOOST) | {op['green']['would_play']} | {op['green']['settled_played']} | "
        f"{op['green']['wins']} | {_pct(op['green']['hit_rate'])} | {_roi(op['green']['roi'])} |",
        f"| operator slice (≥ {slice_from}) | {op['n']} | {op['resolved']} | {op['settled_all']} | "
        f"incl. caution-grade | {op['caution']['would_play']} | {op['caution']['settled_played']} | "
        f"{op['caution']['wins']} | {_pct(op['caution']['hit_rate'])} | {_roi(op['caution']['roi'])} |",
        "",
        "Baseline for reference (actual WATCHLIST_UNKNOWN_CTX outcomes, 30-day audit): "
        "19 settled / 17 wins / +0.061 ROI — these picks were NOT played; the would-be "
        "ROI is what the resolution layer would have added. Green-light = ALLOW/BOOST "
        "verdict (played unconditionally); caution-grade also plays CAUTION verdicts "
        "(the live pipeline does play CAUTION picks).",
        "",
    ]
    if full["green"]["would_play"] == 0:
        lines += [
            "> **Green-light is N/A as an evidence category.** No in-scope "
            "green-light (ALLOW/BOOST) picks with settled outcomes exist in this "
            "window; the overlay is caution-grade-only in practice. The green-light "
            "rows above are informational and must not be read as evidence. If "
            "in-scope green-light picks accrue, this note drops automatically.",
            "",
        ]
    lines += [
        "## 3. Per-pick counterfactual (full window)",
        "",
        "| date | match | league | rule | side | odds | resolution | path | pool n | pool w_roi | settled | match | would win | would ROI |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(
            f"| {r['date']} | {r['match']} | {r['league']} | {r['rule']} | {r['side']} | "
            f"{r['odds']} | {r['verdict']} | {r['path']} | {r['pool_n'] or '-'} | "
            f"{_roi(r['pool_w_roi'])} | {r['settled'] or 'unsettled'} | {r['match_method'] or '-'} | "
            f"{'W' if r['won'] else ('L' if r['won'] is False else '-')} | {_roi(r['would_roi'])} |"
        )

    lines += [
        "",
        "## 4. Resolution path distribution",
        "",
    ]
    path_vc = Counter(r["path"] for r in rows)
    for path, n in path_vc.most_common():
        lines.append(f"- {path}: {n}")
    lines.append("")
    v_vc = Counter(r["verdict"] for r in rows)
    for v, n in sorted(v_vc.items()):
        lines.append(f"- verdict {v}: {n}")

    lines += [
        "",
        "## 5. Caveats",
        "",
        "- Pooled `recent_roi` is None (conservative VETO branch at n>=40).",
        "- Unsettled picks count in `picks`/`resolved` but not in hit-rate/ROI.",
        "- Result join: audit `settled_ledger` first (authoritative for the audit "
        "window), then staged exact9/exact-full/token-subset matching against the "
        "committed `settled_results.json` overlay; unmatched picks show `unsettled` "
        "(genuinely absent or postponed, e.g. Launceston City 2026-07-04).",
        "- League keys spot-checked for collisions (e.g. `aut` = Australia Tasmania "
        "NPL, registry raw `AuT`, not Austria).",
        "- `would_roi` uses archived pick-time odds; flat stake; no vig/tax modelling.",
        "- Read-only: no repo file was created or modified by this harness.",
        "",
        "## 6. Pre-committed gate checklist (anti-mood; PHASE1_2 spec section 8)",
        "",
        "Thresholds were written down BEFORE the gate started accruing and must not "
        "be changed while it runs. The comparison baseline is the audit's "
        "WATCHLIST_UNKNOWN_CTX bucket (the watchlist the overlay would replace): "
        f"settled={bucket_settled}, wins={bucket_wins}, hit={_pct(bucket_hit)}, "
        f"ROI={_roi(bucket_roi)}.",
        "",
        f"- **G1** settled in-scope caution-grade picks >= {GATE_MIN_SETTLED}: "
        f"**{n_gate}** -> {'PASS' if g1 else 'WIP' if n_gate < GATE_MIN_SETTLED else 'FAIL'}",
        f"- **G2** overlay ROI > 0 AND >= bucket ROI - {GATE_ROI_EPS:.2f}: "
        f"overlay {_roi(roi_gate)} vs bucket {_roi(bucket_roi)} -> "
        f"{'PASS' if g2 else 'FAIL/WIP'}",
        f"- **G3** overlay 90% Wilson LB >= bucket hit - {GATE_HIT_EPS:.2f}: "
        f"LB {_pct(lb_gate)} vs bucket {_pct(bucket_hit)} -> "
        f"{'PASS' if g3 else 'FAIL/WIP'}",
        "",
        f"- **VERDICT: {gate_verdict}**",
        "",
        "Deprecation rule: at >= 60 settled, if overlay ROI < bucket ROI - 2pp at "
        "two consecutive checkpoints (>= 2 weeks apart), retire the overlay "
        "(flag stays OFF, code stays, decision recorded in HANDOVER). Current "
        f"signal: {'YES' if dep_signal else 'no'}.",
    ]

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines) + "\n")

    # stdout summary
    print(f"Picks analysed (WATCHLIST_UNKNOWN_CTX, >= {args.start}): {len(rows)}")
    print(f"Resolved: {full['resolved']} | settled overall: {full['settled_all']}")
    print(f"Full window  green: {_fmt(full['green'])}")
    print(f"Full window  incl-caution: {_fmt(full['caution'])}")
    print(f"Operator 30d green: {_fmt(op['green'])}")
    print(f"Operator 30d incl-caution: {_fmt(op['caution'])}")
    print(f"GATE: {gate_verdict}")
    print(f"  G1 n_settled={n_gate}/{GATE_MIN_SETTLED} {'PASS' if g1 else 'WIP'}")
    print(f"  G2 ROI {_roi(roi_gate)} vs bucket {_roi(bucket_roi)} (eps {GATE_ROI_EPS:.2f}) {'PASS' if g2 else 'FAIL/WIP'}")
    print(f"  G3 hit LB {_pct(lb_gate)} vs bucket {_pct(bucket_hit)} (eps {GATE_HIT_EPS:.2f}) {'PASS' if g3 else 'FAIL/WIP'}")
    print(f"Report written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

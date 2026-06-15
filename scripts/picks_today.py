#!/usr/bin/env python3
"""Daily picks: live-fetch today+tomorrow, apply ONLY certified consensus
rules (unanimous + veto) for 1x2 / OU2.5 / BTTS, emit a slip.

    python3 scripts/picks_today.py            # today + tomorrow
    python3 scripts/picks_today.py 2026-06-13 # specific day(s)

Edge registry: reads localdata/edges_consensus.json (certified edges only).
If the registry is missing/empty/corrupt -> FALLBACK to the historically
certified thresholds (HANDOVER.md §4): 1x2 2-way unanimous avg_p>=70,
3-way unanimous avg_p>=65, VETO on any disagreement. OU/BTTS have NO
fallback: without certified edges those markets are skipped.

Purity registry: reads localdata/purity_registry.json (produced by
scripts/assay_purity.py). Picks are bucketed into:
  CERTIFIED_CLEAN, CAUTION, WATCHLIST_NO_ODDS, WATCHLIST_UNKNOWN_CTX,
  SKIPPED_VETO, SKIPPED_DEAD_EDGE
If purity_registry is missing -> all contexts = UNKNOWN -> WATCHLIST,
never crash (fresh clone guarantee).

MUST work with completely empty localdata/ (fresh clone): every source
fetch is individually fault-tolerant and a missing registry only means
fallback thresholds — never a crash.
"""
from __future__ import annotations

import importlib
import json
import re
import sys
from datetime import date, timedelta, datetime
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.util import norm_team  # noqa: E402

EDGES_PATH = ROOT / "localdata" / "edges_consensus.json"
PURITY_PATH = ROOT / "localdata" / "purity_registry.json"

# Live sources per market (adapters return raw site scales; see normalization
# below — vitibet/betclan/scoutingstats return 0-100, warehouse converts but
# the LIVE adapters do NOT, so we defensively normalize here).
SOURCES_1X2 = ["forebet", "zulubet", "statarea", "vitibet", "betclan", "bzzoiro"]
SOURCES_OU = ["forebet", "statarea", "scoutingstats", "bzzoiro"]
SOURCES_BTTS = ["forebet", "scoutingstats", "bzzoiro"]
ALL_SOURCES = ["forebet", "zulubet", "statarea", "vitibet", "betclan",
               "bzzoiro", "scoutingstats"]

# Per-source probability column for OU2.5 / BTTS (verified against
# src/edgefactory/warehouse.py + each source adapter — do not guess).
OU_COL = {"forebet": "p_over", "statarea": "p_o25",
          "scoutingstats": "p_o25", "bzzoiro": "p_o25"}
BTTS_COL = {"forebet": "p_gg", "scoutingstats": "p_gg", "bzzoiro": "p_gg"}

# Fallback thresholds — historically certified (HANDOVER.md §4),
# walk-forward survivors re-validated 2026-06-11. avg_p scale: percent.
FALLBACK_1X2 = {2: 70.0, 3: 65.0}

_RULE_NWAY = re.compile(r"(\d+)\s*way")
_RULE_THR = re.compile(r"avg_p\s*>=?\s*([\d.]+)")

# ---- purity buckets (Phase 4) ----
BUCKET_CERTIFIED = "CERTIFIED_CLEAN"
BUCKET_CAUTION = "CAUTION"
BUCKET_WL_ODDS = "WATCHLIST_NO_ODDS"
BUCKET_WL_CTX = "WATCHLIST_UNKNOWN_CTX"
BUCKET_SKIP_VETO = "SKIPPED_VETO"
BUCKET_SKIP_DEAD = "SKIPPED_DEAD_EDGE"

BUCKET_ORDER = [
    BUCKET_CERTIFIED,
    BUCKET_CAUTION,
    BUCKET_WL_ODDS,
    BUCKET_WL_CTX,
    BUCKET_SKIP_VETO,
    BUCKET_SKIP_DEAD,
]

BUCKET_LABELS = {
    BUCKET_CERTIFIED: "CERTIFIED CLEAN PICKS",
    BUCKET_CAUTION: "CAUTION PICKS",
    BUCKET_WL_ODDS: "WATCHLIST — NO ODDS",
    BUCKET_WL_CTX: "WATCHLIST — UNKNOWN CONTEXT",
    BUCKET_SKIP_VETO: "SKIPPED — VETO CONTEXT",
    BUCKET_SKIP_DEAD: "SKIPPED — DEAD EDGE",
}

# Odds bands – must match scripts/assay_purity.py
ODDS_BANDS = [
    (0.0, 1.10, "1.00-1.10"),
    (1.10, 1.20, "1.10-1.20"),
    (1.20, 1.35, "1.20-1.35"),
    (1.35, 1.50, "1.35-1.50"),
    (1.50, 1.75, "1.50-1.75"),
    (1.75, 2.00, "1.75-2.00"),
    (2.00, 2.50, "2.00-2.50"),
    (2.50, 999.0, "2.50+"),
]

def odds_band(odds: float | None) -> str:
    if odds is None:
        return "NO_ODDS"
    try:
        o = float(odds)
    except Exception:
        return "NO_ODDS"
    for lo, hi, name in ODDS_BANDS:
        if lo <= o < hi or (lo == 0.0 and o < hi):
            return name
    return "2.50+"


# ---------------------------------------------------------------- registry --
def load_thresholds():
    """Return ({n_way: thr} for 1x2, (n_way, thr)|None for ou, same for btts,
    used_fallback: bool). Never raises."""
    edges = []
    try:
        data = json.loads(EDGES_PATH.read_text())
        edges = [e for e in data.get("edges", [])
                 if e.get("status") == "certified"]
    except (OSError, json.JSONDecodeError, AttributeError):
        edges = []

    if not edges:
        return dict(FALLBACK_1X2), None, None, True

    t1x2: dict[int, float] = {}
    ou_best = btts_best = None
    for e in edges:
        rule = e.get("rule", "")
        market = e.get("market", "1x2")
        mn, mt = _RULE_NWAY.search(rule), _RULE_THR.search(rule)
        if not mn or not mt:
            continue
        n_way, thr = int(mn.group(1)), float(mt.group(1))
        if market == "1x2":
            t1x2[n_way] = min(t1x2.get(n_way, 999.0), thr)
        elif market == "ou_2.5":
            if ou_best is None or thr < ou_best[1]:
                ou_best = (n_way, thr)
        elif market == "btts":
            if btts_best is None or thr < btts_best[1]:
                btts_best = (n_way, thr)

    if not t1x2:  # registry has no usable 1x2 rule -> fallback for 1x2 only
        t1x2 = dict(FALLBACK_1X2)
    return t1x2, ou_best, btts_best, not bool(edges)


def load_edge_meta():
    """Return {rule: {'status': str, 'decay_verdict': str}}
    Never raises – missing file → empty dict (all edges assumed HEALTHY/certified).
    """
    try:
        data = json.loads(EDGES_PATH.read_text())
        out = {}
        for e in data.get("edges", []):
            rule = e.get("rule")
            if not rule:
                continue
            status = e.get("status", "certified")
            decay = e.get("decay", {})
            verdict = decay.get("verdict", "HEALTHY")
            out[rule] = {"status": status, "decay_verdict": verdict}
        return out
    except Exception:
        return {}


def thr_for(n_sources: int, t1x2: dict[int, float]):
    """Certified threshold for an n-source unanimous 1x2 consensus.
    Uses the largest certified n_way <= n_sources (e.g. 5 agreeing sources
    is at least as strong as the certified 3-way rule)."""
    eligible = [k for k in t1x2 if k <= n_sources]
    if not eligible:
        return None, None
    k = max(eligible)
    return k, t1x2[k]


# ---------------------------------------------------------------- purity --
def load_purity():
    """Load purity_registry.json. Never raises. Returns {} on missing/corrupt."""
    try:
        return json.loads(PURITY_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def lookup_context(purity: dict, pick: dict) -> dict:
    """Build context keys from pick, look up verdicts in purity registry.
    Returns {"league": verdict, "team_h": verdict, "team_a": verdict, "odds_band": verdict}
    Missing registry/keys → all "UNKNOWN" (graceful fallback).
    """
    ctx = purity.get("contexts", {}) if purity else {}
    league_ctx = ctx.get("league", {})
    team_ctx = ctx.get("team", {})
    odds_ctx = ctx.get("odds_band", {})

    sport = pick.get("sport", "soccer")
    league = pick.get("league") or "UNKNOWN"
    market = pick.get("market", "1x2")
    rule = pick.get("rule", "?")
    sel = pick.get("pick", "?")

    # league_context: sport|league|market|edge_family|selection_role
    league_key = f"{sport}|{league}|{market}|{rule}|{sel}"
    league_v = league_ctx.get(league_key, {}).get("verdict", "UNKNOWN")

    # team_context: sport|team|league|market|role
    home = pick.get("home", "")
    away = pick.get("away", "")
    team_h_key = f"{sport}|{norm_team(home)}|{league}|{market}|home"
    team_a_key = f"{sport}|{norm_team(away)}|{league}|{market}|away"
    team_h_v = team_ctx.get(team_h_key, {}).get("verdict", "UNKNOWN")
    team_a_v = team_ctx.get(team_a_key, {}).get("verdict", "UNKNOWN")

    # odds_band_context
    odds = pick.get("odds")
    band = odds_band(odds)
    odds_key = f"{sport}|{market}|{rule}|{band}"
    odds_v = odds_ctx.get(odds_key, {}).get("verdict", "UNKNOWN")

    return {
        "league": league_v,
        "team_h": team_h_v,
        "team_a": team_a_v,
        "odds_band": odds_v,
        "_keys": {
            "league": league_key,
            "team_h": team_h_key,
            "team_a": team_a_key,
            "odds_band": odds_key,
        }
    }


def bucket_pick(pick: dict, ctx: dict, edge_status: str = "certified", decay_verdict: str = "HEALTHY") -> str:
    """Bucket a pick according to purity / health rules (top-to-bottom).
    Returns one of the BUCKET_* constants.
    """
    # 1. edge status == "benched"
    if edge_status == "benched":
        return BUCKET_SKIP_DEAD
    # 2. edge decay verdict in (DEAD, DECAYING)
    if decay_verdict in ("DEAD", "DECAYING"):
        return BUCKET_SKIP_DEAD
    # 3. any context dimension == VETO
    if "VETO" in (ctx.get("league"), ctx.get("team_h"), ctx.get("team_a"), ctx.get("odds_band")):
        return BUCKET_SKIP_VETO
    # 4. odds is None
    if pick.get("odds") is None:
        return BUCKET_WL_ODDS
    # 5. any critical context == UNKNOWN  (critical = league_context for Phase 3)
    if ctx.get("league") == "UNKNOWN":
        return BUCKET_WL_CTX
    # 6. all contexts in (BOOST, ALLOW, UNKNOWN-non-critical)
    #    -> CERTIFIED_CLEAN or CAUTION
    vals = [ctx.get("league"), ctx.get("team_h"), ctx.get("team_a"), ctx.get("odds_band")]
    if "CAUTION" in vals:
        return BUCKET_CAUTION
    # BOOST / ALLOW / UNKNOWN (non-critical) → clean
    return BUCKET_CERTIFIED


# ------------------------------------------------------------------- fetch --
def fetch_all(day: str) -> dict[str, dict]:
    """Fetch every source for one day. Per-source failures are skipped.
    Returns {source: {(hkey, akey): row}} of UPCOMING matches only."""
    out: dict[str, dict] = {}
    for name in ALL_SOURCES:
        try:
            mod = importlib.import_module(f"edgefactory.sources.{name}")
            rows = mod.fetch_day(day)
        except Exception as e:  # import OR fetch failure: skip, never crash
            print(f"skip {name}: {e}", file=sys.stderr)
            continue
        by_key = {}
        for r in rows or []:
            home, away = r.get("home"), r.get("away")
            if not home or not away:
                continue
            if r.get("hs") not in (None, ""):       # already settled
                continue
            if name == "forebet" and r.get("status") == "FT":
                continue
            k = (norm_team(home), norm_team(away))
            if len(k[0]) < 4 or len(k[1]) < 4:
                continue
            by_key[k] = r
        out[name] = by_key
    return out


def _f(v):
    try:
        return None if v is None or v == "" else float(v)
    except (TypeError, ValueError):
        return None


def probs_1x2(row):
    """(p1, px, p2) normalized to 0-1. vitibet/betclan live adapters return
    0-100 (warehouse normalizes, live does NOT) — defensive: >1.5 -> /100."""
    p1, px, p2 = _f(row.get("p1")), _f(row.get("px")), _f(row.get("p2"))
    if p1 is None or px is None or p2 is None:
        return None
    if p1 > 1.5 or px > 1.5 or p2 > 1.5:
        p1, px, p2 = p1 / 100.0, px / 100.0, p2 / 100.0
    return p1, px, p2


def prob_single(row, col):
    p = _f(row.get(col))
    if p is None:
        return None
    if p > 1.5:
        p /= 100.0
    return p


def top_pick(p1, px, p2):
    best = max(p1, px, p2)
    return ("home" if best == p1 else ("draw" if best == px else "away")), best


# --------------------------------------------------------------- consensus --
def eval_1x2(day, data, t1x2):
    picks, vetoes = [], 0
    keys = set()
    for s in SOURCES_1X2:
        keys |= set(data.get(s, {}))
    for k in keys:
        sels, ps, used = [], [], []
        for s in SOURCES_1X2:
            row = data.get(s, {}).get(k)
            if not row:
                continue
            pr = probs_1x2(row)
            if pr is None:
                continue
            sel, pmax = top_pick(*pr)
            sels.append(sel)
            ps.append(pmax)
            used.append(s)
        if len(used) < 2:
            continue
        if len(set(sels)) > 1:
            vetoes += 1                 # VETO: disagreement = never bet
            continue
        n_way, thr = thr_for(len(used), t1x2)
        if thr is None:
            continue
        avg_p = mean(ps) * 100.0
        if avg_p < thr:
            continue
        fb = data.get("forebet", {}).get(k) or {}
        bz = data.get("bzzoiro", {}).get(k) or {}
        vb = data.get("vitibet", {}).get(k) or {}
        anchor = fb or next(data[s][k] for s in used if k in data.get(s, {}))
        sel = sels[0]
        odds = _f({"home": fb.get("odd1"), "draw": fb.get("oddx"),
                   "away": fb.get("odd2")}.get(sel)) if fb else None
        home = anchor.get("home")
        away = anchor.get("away")
        picks.append({
            "date": day, "market": "1x2",
            "match": f"{home} vs {away}",
            "home": home, "away": away,
            "sport": anchor.get("sport", "soccer"),
            "league": anchor.get("league"), "pick": sel,
            "avg_p": round(avg_p, 1), "odds": odds,
            "rule": f"{n_way}WAY-UNANIMOUS≥{thr:.0f}", "n_way": len(used),
            "confidence": _f(bz.get("confidence")),
            "model_version": bz.get("model_version"),
            "vitibet_index": _f(vb.get("index")),
            "sources_used": used,
        })
    return picks, vetoes, len(keys)


def eval_binary(day, data, market, sources, col_map, edge, yes_no, outcome_odds):
    """Shared OU2.5 / BTTS consensus. edge=(n_way_required, thr) or None
    (no certified edge -> market skipped, no fallback)."""
    if edge is None:
        return []
    n_req, thr = edge
    picks = []
    keys = set()
    for s in sources:
        keys |= set(data.get(s, {}))
    for k in keys:
        sels, confs, used = [], [], []
        for s in sources:
            row = data.get(s, {}).get(k)
            if not row:
                continue
            p = prob_single(row, col_map[s])
            if p is None:
                continue
            sel = yes_no[0] if p >= 0.5 else yes_no[1]
            sels.append(sel)
            confs.append(p if sel == yes_no[0] else 1.0 - p)
            used.append(s)
        if len(used) < max(2, n_req):
            continue
        if len(set(sels)) > 1:
            continue                      # unanimity required
        avg_p = mean(confs) * 100.0
        if avg_p < thr:
            continue
        fb = data.get("forebet", {}).get(k) or {}
        bz = data.get("bzzoiro", {}).get(k) or {}
        anchor = fb or next(data[s][k] for s in used if k in data.get(s, {}))
        sel = sels[0]
        odds = _f(fb.get(outcome_odds[sel])) if fb else None
        home = anchor.get("home")
        away = anchor.get("away")
        picks.append({
            "date": day, "market": market,
            "match": f"{home} vs {away}",
            "home": home, "away": away,
            "sport": anchor.get("sport", "soccer"),
            "league": anchor.get("league"), "pick": sel,
            "avg_p": round(avg_p, 1), "odds": odds,
            "rule": f"{market.upper()}-UNANIMOUS-{len(used)}WAY≥{thr:.0f}",
            "n_way": len(used),
            "confidence": _f(bz.get("confidence")),
            "model_version": bz.get("model_version"),
            "vitibet_index": None,
            "sources_used": used,
        })
    return picks


# --------------------------------------------------------------------- run --
def run_day(day, t1x2, ou_edge, btts_edge):
    data = fetch_all(day)
    picks, vetoes, n_up = eval_1x2(day, data, t1x2)
    picks += eval_binary(day, data, "ou_2.5", SOURCES_OU, OU_COL, ou_edge,
                         ("over", "under"),
                         {"over": "odd_over", "under": "odd_under"})
    picks += eval_binary(day, data, "btts", SOURCES_BTTS, BTTS_COL, btts_edge,
                         ("yes", "no"),
                         {"yes": "odd_gg", "no": "odd_ng"})
    picks.sort(key=lambda r: -r["avg_p"])
    return picks, vetoes, n_up


def print_buckets(buckets: dict, title_date: str = ""):
    """Print picks grouped by bucket, Phase 4 format."""
    total_cert = len(buckets.get(BUCKET_CERTIFIED, [])) + len(buckets.get(BUCKET_CAUTION, []))
    print(f"\nEdge Factory Picks — {title_date}" if title_date else "\nEdge Factory Picks")
    print("=" * 60)
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    for b in BUCKET_ORDER:
        picks = buckets.get(b, [])
        label = BUCKET_LABELS.get(b, b)
        print(f"{label}")
        print("=" * 60)
        if not picks:
            print("  (none)")
            print()
            continue
        for p in picks:
            o = f"@{p['odds']:.2f}" if p.get("odds") is not None else "@None"
            ctx = p.get("ctx", {})
            ctx_str = f"  league={ctx.get('league','?')}  team={ctx.get('team_h','?')}/{ctx.get('team_a','?')}  odds_band={ctx.get('odds_band','?')}"
            print(f"  [{p['rule']}] {p['match'][:45]:45s} -> {p['pick'].upper():5s}  avg {p['avg_p']:.0f}% {o}")
            if ctx:
                print(ctx_str)
        print()
    print("⚠️  Flat stakes only. Best odds inflate ROI (~halve it).")
    print("⚠️  Bet only what you can afford to lose.")


def main():
    days = sys.argv[1:] or [
        date.today().isoformat(),
        (date.today() + timedelta(days=1)).isoformat(),
    ]
    t1x2, ou_edge, btts_edge, fallback = load_thresholds()
    edge_meta = load_edge_meta()
    purity = load_purity()
    purity_missing = not bool(purity)

    if fallback:
        print("edge registry missing/empty -> fallback to certified "
              "thresholds: 1x2 2-way>=70 / 3-way>=65 + veto; OU/BTTS skipped",
              file=sys.stderr)
    if purity_missing:
        print("purity_registry.json missing – all contexts will be UNKNOWN → WATCHLIST",
              file=sys.stderr)

    all_picks: list = []
    total_vetoes = 0
    total_upcoming = 0
    for day in days:
        picks, vetoes, n_up = run_day(day, t1x2, ou_edge, btts_edge)
        total_vetoes += vetoes
        total_upcoming += n_up
        # bucket each pick
        for p in picks:
            rule = p.get("rule", "")
            meta = edge_meta.get(rule, {"status": "certified", "decay_verdict": "HEALTHY"})
            ctx = lookup_context(purity, p)
            bucket = bucket_pick(p, ctx,
                                 edge_status=meta.get("status", "certified"),
                                 decay_verdict=meta.get("decay_verdict", "HEALTHY"))
            p["ctx"] = {k: v for k, v in ctx.items() if not k.startswith("_")}
            p["bucket"] = bucket
            p["edge_status"] = meta.get("status", "certified")
            p["decay_verdict"] = meta.get("decay_verdict", "HEALTHY")
        all_picks.extend(picks)

    # group by bucket
    buckets: dict[str, list] = {b: [] for b in BUCKET_ORDER}
    for p in all_picks:
        b = p.get("bucket", BUCKET_CAUTION)
        buckets.setdefault(b, []).append(p)

    # sort within buckets by avg_p desc
    for b in buckets:
        buckets[b].sort(key=lambda r: -r.get("avg_p", 0))

    # print
    title = ", ".join(days) if days else date.today().isoformat()
    print_buckets(buckets, title_date=title)

    # summary line
    n_clean = len(buckets[BUCKET_CERTIFIED])
    n_caution = len(buckets[BUCKET_CAUTION])
    n_wl_odds = len(buckets[BUCKET_WL_ODDS])
    n_wl_ctx = len(buckets[BUCKET_WL_CTX])
    n_skip_veto = len(buckets[BUCKET_SKIP_VETO])
    n_skip_dead = len(buckets[BUCKET_SKIP_DEAD])
    print(f"\nSummary: CLEAN={n_clean} CAUTION={n_caution} "
          f"WATCHLIST_odds={n_wl_odds} WATCHLIST_ctx={n_wl_ctx} "
          f"SKIPPED_veto={n_skip_veto} SKIPPED_dead={n_skip_dead}  "
          f"({total_vetoes} unanimity-vetoes during consensus, {total_upcoming} upcoming matches scanned)",
          file=sys.stderr)

    # Write JSON for daily.py report generation and Supabase sync
    # includes bucket + ctx fields
    _json_path = ROOT / "localdata" / "picks_today.json"
    _json_path.parent.mkdir(parents=True, exist_ok=True)
    _json_path.write_text(json.dumps(all_picks, indent=2))


if __name__ == "__main__":
    main()

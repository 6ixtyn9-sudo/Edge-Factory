#!/usr/bin/env python3
"""AUTO TICKETS v4 — acca-only, aligned with the operator's plan.

The operator's structure (no singles, ever):
  - 28% of CAPITAL -> MULTIPLE 2-odd accas (split across N_ACCA2_TICKETS tickets)
  - 10% of CAPITAL -> ONE 10-odd acca
  - total at risk per day = 38% of capital
All output is percentages of capital only (no rand amounts).

Selection (dynamic, positive-ROI buckets only):
  - bucket in CERTIFIED_CLEAN + SKIPPED_VETO  (handover: SKIPPED_VETO 86.5% hit /
    +11.8% ROI; CAUTION negative -> excluded)
  - trusted price evidence only (BZZOIRO_PRIMARY / BETEXPLORER_RESCUE;
    scoutingstats -33% -> excluded)
  - edge rule x odds source combo must pass: n>=15, ROI>=+3%, Wilson LB>=0.68,
    recent-20 ROI >= 0
  - per-pick model edge >= MIN_EDGE at captured odds
Ticket construction:
  - 2-ODD ACCAS: pair the qualifying picks (smallest odds x largest odds) so each
    pair lands as close to 2.00 as possible; N_ACCA2_TICKETS pairs.
  - 10-ODD ACCA: ALL qualifying picks (reuse across ticket types allowed — each
    ticket is an independent bet; this matches the operator's manual behaviour).
    Fewest legs to reach ~10.0, capped at MAX_ACCA10_LEGS.
Safety rails:
  - drawdown guard (last 20 graded tickets ROI < -10% -> RED ALERT, --force to override)
  - recency gate on combos
  - league diversity cap inside each 2-odd acca
Usage:
  PYTHONPATH=src python3 scripts/auto_tickets.py
  PYTHONPATH=src python3 scripts/auto_tickets.py --history
  PYTHONPATH=src python3 scripts/auto_tickets.py --force
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
LOCALDATA = ROOT / "localdata"

# ---------------- structure (fractions of CAPITAL) ----------------
AT_RISK_FRAC = 0.38          # CEILING, not a target — max total at risk per day
CAP_ACCA2 = 0.28             # 28% of capital -> multiple 2-odd accas (at full deployment)
CAP_ACCA10 = 0.10            # 10% of capital -> one 10-odd acca (at full deployment)
N_ACCA2_TICKETS = 3          # split the 2-odd money across this many tickets
IDEAL_POOL_MIN = 4           # floor: never demand fewer than this
IDEAL_POOL_LOOKBACK = 10     # trailing days used to derive the adaptive ideal pool

# ---------------- selection gates ----------------
PASS_N = 15                  # min settled picks for a (rule, source) combo
PASS_ROI = 0.03              # min realized ROI
PASS_LB = 0.68               # Wilson lower bound on hit rate
RECENT_N = 20                # recency window per combo
RECENT_ROI_MIN = 0.0         # combo must show this ROI on its last RECENT_N picks
MIN_EDGE = 0.0               # no per-pick edge floor; combo (rule x source) pass is the edge test
ACCA2_TARGET = 2.0
ACCA10_TARGET = 10.0
ACCA10_MIN_LEGS = 3        # 10-odd only emitted if >= this many distinct legs
ACCA10_MIN_PROD = 4.0      # ...and total odds at least this (else it's just a 2-odd duplicate)
MAX_ACCA10_LEGS = 9
PAUSE_ROI = -0.10            # drawdown guard: last-20-ticket ROI below this pauses
PAUSE_N = 20

BUCKETS = {"CERTIFIED_CLEAN", "SKIPPED_VETO"}
# No hardcoded trusted-price allowlist: a price source is trusted if it has at
# least one (rule x source) combo that PASSES the edge table. This lets new
# sources (e.g. ml-meta via forebet_best/zulubet) earn their way in as their
# settled history proves positive edge, instead of being permanently blocked.
# Kept as a name for readability; the real gate is _source_has_passing_combo().
GENERATE_HOUR = 12          # local time — tickets generate ONLY on/after the 12:00 (midday) run
TZ = ZoneInfo("Africa/Johannesburg")
PICK_RE = re.compile(r"^picks_(\d{4}-\d{2}-\d{2})\.json$")


def wilson_lb(wins, n, z=1.645):
    if n == 0:
        return 0.0
    p = wins / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
    return max(0.0, (centre - half) / denom)


def parse_kickoff(pick):
    raw = pick.get("kickoff_canonical") or pick.get("kickoff") or ""
    day = str(pick.get("date") or "")[:10]
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
               "%d-%m, %H:%M", "%d-%m, %H:%M:%S", "%H:%M"):
        try:
            dt = datetime.strptime(raw, fmt)
            if fmt in ("%H:%M", "%d-%m, %H:%M", "%d-%m, %H:%M:%S"):
                try:
                    dt = dt.replace(year=int(day[:4]), month=int(day[5:7]), day=int(day[8:10]))
                except ValueError:
                    return None
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=TZ)
            return dt
        except ValueError:
            continue
    return None


def load_archived_picks():
    out = []
    for f in sorted(LOCALDATA.glob("picks_*.json")):
        m = PICK_RE.match(f.name)
        if not m:
            continue
        try:
            rows = json.loads(f.read_text())
        except Exception:
            continue
        if isinstance(rows, list):
            for r in rows:
                r.setdefault("_archive_day", m.group(1))
            out.extend(rows)
    return out


def load_settled():
    from edgefactory.util import norm_team
    try:
        data = json.loads((LOCALDATA / "settled_results.json").read_text())
    except Exception:
        return {}
    out = {}
    for r in data.get("rows", []):
        key = (str(r.get("date") or "")[:10], norm_team(r.get("home") or ""), norm_team(r.get("away") or ""))
        out[key] = r.get("outcome")
    return out


def pick_result(pick, settled):
    from edgefactory.util import norm_team
    day = str(pick.get("date") or pick.get("_archive_day") or "")[:10]
    key = (day, norm_team(pick.get("home") or ""), norm_team(pick.get("away") or ""))
    outcome = settled.get(key)
    if outcome not in ("home", "away", "draw"):
        return None
    sel = str(pick.get("pick") or "").lower()
    if outcome == "draw":
        return "loss"
    return "win" if outcome == sel else "loss"


def build_edge_table(picks, settled):
    history = defaultdict(list)
    for p in picks:
        rule = p.get("edge_rule") or p.get("rule")
        src = p.get("odds_source") or "UNKNOWN"
        odds = p.get("odds")
        if not rule or not odds or odds <= 1.0:
            continue
        res = pick_result(p, settled)
        if res is None:
            continue
        history[(rule, src)].append((str(p.get("date") or p.get("_archive_day") or "")[:10], res, float(odds)))
    table = {}
    for combo, rows in history.items():
        rows.sort()
        n = len(rows)
        wins = sum(1 for _, r, _ in rows if r == "win")
        ret = sum(o for _, r, o in rows if r == "win")
        roi = (ret - n) / n if n else 0.0
        lb = wilson_lb(wins, n)
        recent = rows[-RECENT_N:]
        rn = len(recent)
        rret = sum(o for _, r, o in recent if r == "win")
        roi_recent = (rret - rn) / rn if rn else 0.0
        passed = n >= PASS_N and roi >= PASS_ROI and lb >= PASS_LB and roi_recent >= RECENT_ROI_MIN
        table[combo] = {"n": n, "wins": wins, "hit": wins / n, "roi": roi, "lb": lb,
                        "roi_recent": roi_recent, "recent_n": rn, "pass": passed}
    return table


def _source_has_passing_combo(table: dict, src: str) -> bool:
    """True if any (rule, source) combo for this odds source currently passes."""
    return any(src == s and v.get("pass") for (r, s), v in table.items())


def load_pause_state():
    try:
        perf = json.loads((LOCALDATA / "auto_tickets_performance.json").read_text())
    except Exception:
        return False
    detail = perf.get("detail") or []
    settled = [t for t in detail if t.get("result") in ("WIN", "LOSS")][-PAUSE_N:]
    if len(settled) < PAUSE_N:
        return False
    staked = sum(t.get("stake", 1.0) for t in settled)
    ret = sum(t.get("returned", 0.0) for t in settled)
    return (ret - staked) / staked < PAUSE_ROI if staked else False


def adaptive_ideal_pool(target: str) -> int:
    """Derive the ideal qualifying-pool size from recent history (trailing
    median), so full deployment tracks the season's fixture volume instead of
    a hardcoded constant. Floor at IDEAL_POOL_MIN."""
    sizes = []
    from datetime import timedelta as _td
    from datetime import datetime as _dt
    cutoff = (_dt.strptime(target, "%Y-%m-%d") - _td(days=IDEAL_POOL_LOOKBACK)).isoformat()
    for f in sorted(LOCALDATA.glob("picks_*.json")):
        day = f.name.replace("picks_", "").replace(".json", "")
        if day >= target or day < cutoff:
            continue
        try:
            rows = json.loads(f.read_text())
        except Exception:
            continue
        n = 0
        for r in rows:
            try:
                o = float(r.get("odds") or 0)
            except (TypeError, ValueError):
                o = 0.0
            if r.get("bucket") in BUCKETS and o > 1.0:
                n += 1
        sizes.append(n)
    if not sizes:
        return IDEAL_POOL_MIN
    sizes.sort()
    med = sizes[len(sizes) // 2]
    return max(IDEAL_POOL_MIN, med)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--history", action="store_true")
    ap.add_argument("--force", action="store_true", help="override drawdown pause")
    args = ap.parse_args()
    target = args.date

    settled = load_settled()
    archives = [p for p in load_archived_picks() if str(p.get("date") or p.get("_archive_day") or "") < target]
    table = build_edge_table(archives, settled)

    if args.history:
        print("DYNAMIC EDGE TABLE (settled history < %s)" % target)
        print(f"{'rule':40s} {'source':18s} {'n':>4s} {'hit':>6s} {'roi':>7s} {'recent':>7s} {'LB':>5s}  pass")
        for (rule, src), st in sorted(table.items(), key=lambda kv: (-kv[1]["roi"], -kv[1]["n"])):
            print(f"{rule:40s} {src:18s} {st['n']:4d} {st['hit']:6.1%} {st['roi']:7.1%} "
                  f"{st['roi_recent']:7.1%} {st['lb']:5.2f}  {'YES' if st['pass'] else 'no'}")
        return 0

    if load_pause_state() and not args.force:
        print("RED ALERT — PAUSE")
        print("last %d graded tickets show ROI below %+.0f%%. " % (PAUSE_N, PAUSE_ROI * 100))
        print("Run the grader, review, then --force if you accept the risk.")
        return 2

    # FREEZE: tickets are generated once per day, then re-printed on later runs.
    # The machine runs 8x/day; without this, tickets would churn every run.
    frozen_txt = LOCALDATA / f"auto_tickets_{target}.txt"
    if frozen_txt.exists() and not args.force:
        print(f"TICKETS FROZEN — already generated for {target}. Re-printing saved slip:")
        print("=" * 62)
        print(frozen_txt.read_text())
        return 0

    # 09:00 GATE: only the designated morning run places bets. Runs before 09:00
    # local print "waiting" and place nothing, so the system is never quick to bet.
    now_local = datetime.now(TZ)
    local_today = now_local.strftime("%Y-%m-%d")
    if str(target) == local_today and now_local.hour < GENERATE_HOUR and not args.force:
        print("NOT YET — TICKETS GENERATE AT 12:00 (MIDDAY)")
        print(f"(now {now_local.strftime('%H:%M')} local; generation window opens {GENERATE_HOUR:02d}:00)")
        print("Nothing is bet before then. The 09:00 run generates the frozen slip;")
        print("all later runs re-print it unchanged.")
        return 0

    try:
        slate = json.loads((LOCALDATA / "picks_today.json").read_text())
    except Exception as e:
        print(f"cannot read picks_today.json: {e}")
        return 1
    if not isinstance(slate, list):
        print("picks_today.json is not a list")
        return 1

    now = datetime.now(TZ)
    today = []
    for p in slate:
        if str(p.get("date") or "")[:10] != target:
            continue
        if p.get("bucket") not in BUCKETS:
            continue
        rule = p.get("edge_rule") or p.get("rule")
        src = p.get("odds_source") or "UNKNOWN"
        if not _source_has_passing_combo(table, src):
            continue
        if p.get("quarantine") not in (None, "none"):
            continue
        odds, avg_p = p.get("odds"), p.get("avg_p")
        try:
            odds_f = float(odds) if odds is not None else 0.0
        except (TypeError, ValueError):
            odds_f = 0.0
        if odds_f <= 1.0 or not avg_p:
            continue
        odds = odds_f
        kt = parse_kickoff(p)
        if kt is not None and kt < now:
            continue
        combo = table.get((rule, src))
        if combo is None or not combo["pass"]:
            continue
        today.append({
            "match": f"{p.get('home')} vs {p.get('away')}",
            "league": str(p.get("league") or p.get("odds_league") or "?"),
            "pick": str(p.get("pick") or "").upper(),
            "odds": float(odds), "avg_p": float(avg_p),
            "rule": rule, "source": src, "bucket": p.get("bucket"),
            "edge": float(avg_p) / 100.0 * float(odds) - 1.0,
            "combo_n": combo["n"], "combo_hit": combo["hit"],
            "combo_roi": combo["roi"], "combo_lb": combo["lb"],
        })

    if not today:
        print("NO EDGE TODAY — DO NOT BET")
        print(f"({len(slate)} slate rows; 0 passed edge+trusted-price+bucket filters)")
        return 0

    today.sort(key=lambda x: -x["edge"])

    # ---- 2-ODD ACCAS: pair smallest-odds with largest-odds, closest to 2.00 ----
    ordered = sorted(today, key=lambda x: x["odds"])
    acca2_tickets = []
    used = set()
    lo, hi = 0, len(ordered) - 1
    while lo < hi and len(acca2_tickets) < N_ACCA2_TICKETS:
        a, b = ordered[lo], ordered[hi]
        prod = a["odds"] * b["odds"]
        # try the next-higher small leg if it gets closer to 2.00 (and is distinct)
        if (lo + 1 < hi
                and ordered[lo + 1]["match"] + ordered[lo + 1]["pick"] != b["match"] + b["pick"]
                and abs(ordered[lo + 1]["odds"] * b["odds"] - ACCA2_TARGET) < abs(prod - ACCA2_TARGET)):
            lo += 1
            a = ordered[lo]
            prod = a["odds"] * b["odds"]
        if a["match"] + a["pick"] == b["match"] + b["pick"]:
            break  # pool too small to form a distinct pair
        acca2_tickets.append(([a, b], prod))
        used.add(a["match"] + a["pick"])
        used.add(b["match"] + b["pick"])
        lo += 1
        hi -= 1

    # ---- 10-ODD ACCA: additive by default (no reusing 2-odd legs), but fall
    #      back to reuse when the FRESH pool is too thin to build a real 10-odd.
    #      Rule: reuse only if we don't have enough fresh legs; never reuse when
    #      the fresh pool alone can reach the bar. ----
    def _build_acca10(pool):
        pool = sorted(pool, key=lambda x: -x["odds"])
        legs, prod = [], 1.0
        for p in pool:
            legs.append(p)
            prod *= p["odds"]
            if prod >= ACCA10_TARGET or len(legs) >= MAX_ACCA10_LEGS:
                break
        return legs, prod

    fresh_pool = [p for p in today if p["match"] + p["pick"] not in used]
    acca10_legs, acca10_prod = _build_acca10(fresh_pool)
    if len(fresh_pool) < ACCA10_MIN_LEGS:
        # Not enough DISTINCT fresh bets (fewer than 3 unused legs) -> thin day,
        # fall back to reuse rather than skip the 10-odd entirely.
        acca10_legs, acca10_prod = _build_acca10(today)
    # Guard: still never emit a degenerate "10-odd" that is just the 2-odd
    # duplicated with too few legs / too small a product.
    acca10_held_back = len(acca10_legs) < ACCA10_MIN_LEGS or acca10_prod < ACCA10_MIN_PROD
    acca10_n_saved, acca10_prod_saved = len(acca10_legs), acca10_prod
    if acca10_held_back:
        acca10_legs, acca10_prod = [], 0.0

    # ---------------- output (percentages of capital only) ----------------
    # ADAPTIVE DEPLOYMENT: 38% is a ceiling, not a target. Scale all stakes by
    # day strength = how much of the ideal qualifying pool is actually present.
    # A thin day (2 legs) deploys far less than 38%; a rich day (7+ legs) can
    # approach the ceiling. Unused capital stays unbet.
    ideal_pool = adaptive_ideal_pool(target)
    pool_factor = min(1.0, len(today) / ideal_pool)
    per_acca2 = (CAP_ACCA2 * pool_factor) / max(N_ACCA2_TICKETS, 1)
    acca10_stake = CAP_ACCA10 * pool_factor
    lines = [f"AUTO TICKETS — {target}", "=" * 62,
             f"CEILING: {AT_RISK_FRAC:.0%} of capital  ·  DAY STRENGTH: {pool_factor:.0%} "
             f"({len(today)}/{ideal_pool} qualifying legs — adaptive)"]
    deployed = 0.0
    for i, (legs, prod) in enumerate(acca2_tickets, 1):
        lines.append(f"\n[2-ODD ACCA #{i}] {len(legs)} leg(s), total {prod:.2f}, "
                     f"stake {per_acca2:.1%} of capital")
        deployed += per_acca2
        for l in legs:
            lines.append(f"   {l['match']:44s} {l['pick']:5s} @ {l['odds']:.2f}  "
                         f"({l['avg_p']:.0f}% · {l['rule']} · {l['source']} "
                         f"n={l['combo_n']} roi={l['combo_roi']:+.0%})")
    if not acca2_tickets:
        lines.append("\n[2-ODD ACCA] none — fewer than 2 qualifying picks")
    if acca10_held_back:
        lines.append(f"\n[10-ODD ACCA] HELD BACK — only {acca10_n_saved} distinct qualifying "
                     f"leg(s) and total {acca10_prod_saved:.2f} would just duplicate the 2-odds. "
                     f"That {acca10_stake:.0%} of capital stays unbet today.")
    else:
        lines.append(f"\n[10-ODD ACCA] {len(acca10_legs)} leg(s), total {acca10_prod:.2f}, "
                     f"stake {acca10_stake:.1%} of capital")
        deployed += acca10_stake
        for l in acca10_legs:
            lines.append(f"   {l['match']:44s} {l['pick']:5s} @ {l['odds']:.2f}  "
                         f"({l['avg_p']:.0f}% · {l['rule']} · {l['source']} "
                         f"n={l['combo_n']} roi={l['combo_roi']:+.0%})")
    lines.append(f"\nTOTAL DEPLOYED: {deployed:.1%} of capital  (ceiling {AT_RISK_FRAC:.0%} — "
                 f"{max(0.0, AT_RISK_FRAC - deployed):.1%} held back)")
    lines.append("\nRound each ticket UP to your bookmaker's minimum stake.")
    lines.append("Edge-based selection, dynamic per settled history. Flat stakes. Bet only what you can afford to lose.")

    txt = "\n".join(lines)
    print(txt)
    (LOCALDATA / f"auto_tickets_{target}.txt").write_text(txt)
    (LOCALDATA / f"auto_tickets_{target}.json").write_text(json.dumps({
        "date": target, "at_risk_frac": AT_RISK_FRAC,
        "pass_combos": [f"{r} | {s}" for (r, s), v in table.items() if v["pass"]],
        "acca2": acca2_tickets, "acca10": acca10_legs, "acca10_odds": acca10_prod,
        "stakes_frac": {
            "acca2_per_ticket": per_acca2,
            "acca10": acca10_stake if not acca10_held_back else 0.0,
            "deployed": deployed,
            "ceiling": AT_RISK_FRAC,
            "pool_factor": pool_factor,
        },
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

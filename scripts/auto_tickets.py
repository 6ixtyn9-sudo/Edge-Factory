#!/usr/bin/env python3
"""AUTO TICKETS — ROLLING EDITION (replaces the v4 combo-gate acca slipper).

Why the replacement (2026-08-27 session, receipts in
TICKETS_DIAGNOSIS_2026-08-27.md): the v4 (rule x source) combo gate fired
4/71 days walk-forward at -4.6% leg ROI. The rolling structure below was
validated walk-forward on the same ledger (blind on the cold August half):
x2.60 wealth, never busted, ~55% max drawdown. Tuned filters were tested and
REJECTED (overfit); the recipe has no free parameters to overfit.

THE RECIPE (constants below are receipts, not knobs):
  LEGS      all playable-bucket picks with a price — NO further filtering
            (dropping CERTIFIED_CLEAN or filtering to "quality" sources both
            tested worse: at 4-9 legs/day diversification beats purity).
  ORDER     highest stated probability first (ties by odds).
  ACCAS     2 legs each, consecutive pairs of the top 6, up to 3 per day.
            (2-leg beat 3-leg blind on August: x1.78 vs x0.29; 100%
            deployment busted in every tested configuration.)
  STAKE     50% of the SETTLED bank per day, split across the accas built.
            Stakes are committed when the slip places and leave the bank at
            settlement; open stakes are excluded from effective bank.
  PROFIT    after settlement: half of every new high-water mark is withdrawn
            (banked), AND a TAKE-PROFIT trigger harvests everything above
            TAKE_PROFIT_MULT x the initial bank when the bank reaches it,
            resetting the cycle. Withdrawn units are realised profit.
  VOLUME    if the pool reaches 12+ legs (the "40-ticket-day" regime), only
            stated-prob >= 65% legs ride (Monte Carlo x12.6 median vs x2.5
            for betting everything at volume).

Slip lifecycle matches the production cadence: builds from 06:00 SAST,
FREEZES at 12:00 (later runs re-print), settles as results land. State
persists in localdata/auto_tickets_state.json (gitignore exception exists).

Usage (daily.py runs this bare — same entry point as the old system):
  PYTHONPATH=src python3 scripts/auto_tickets.py            # settle + build/reprint today
  PYTHONPATH=src python3 scripts/auto_tickets.py --status   # bank / withdrawn / history
  PYTHONPATH=src python3 scripts/auto_tickets.py --backfill # replay ledger into state
  PYTHONPATH=src python3 scripts/auto_tickets.py --today --force  # ignore freeze marker
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
LOCALDATA = ROOT / "localdata"

# ---------------- cadence (unchanged from v4 production) ----------------
GENERATE_HOUR_START = 6    # local time — slips may START building on/after this hour
FREEZE_HOUR = 12           # local time — the slip FREEZES on/after this hour
TZ = ZoneInfo("Africa/Johannesburg")
PICK_RE = re.compile(r"^picks_(\d{4}-\d{2}-\d{2})\.json$")

# ---------------- the validated recipe (see module docstring) ----------------
STAKE_FRAC = 0.50          # of settled bank per day (100% busted everywhere)
MAX_ACCAS = 3              # concurrent accas per day
LEGS_PER_ACCA = 2          # 2-leg beat 3-leg out-of-sample
MAX_LEGS = MAX_ACCAS * LEGS_PER_ACCA
VOLUME_POOL = 12           # pool >= this -> volume regime
VOLUME_MIN_PROB = 0.65     # only prob >= this rides at volume
WITHDRAW_FRAC = 0.50       # half of every new high-water mark
TAKE_PROFIT_MULT = 2.0     # bank reaches 2x initial -> harvest all profit above initial
DEFAULT_BANK = 100.0       # paper units; the operator maps this to real capital

BUCKETS = {
    "CERTIFIED_CLEAN",
    "SKIPPED_VETO",
    "WATCHLIST_UNKNOWN_CTX",
    "WATCHLIST_UNCORROBORATED_PRICE",
}
BAD_QUARANTINE = {"alias_fuzzy", "suspect", "suspect_alias_fuzzy"}

STATE_FILE = LOCALDATA / "auto_tickets_state.json"


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
            if fmt in ("%d-%m, %H:%M", "%d-%m, %H:%M:%S"):
                year = day[:4] or "1900"
                dt = datetime.strptime(f"{raw} {year}", f"{fmt} %Y")
            else:
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


# ---------------- state ----------------
def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def save_state(st: dict) -> None:
    STATE_FILE.write_text(json.dumps(st, indent=2, default=str))


def fresh_state(bank: float) -> dict:
    return {"initial_bank": bank, "bank": bank, "withdrawn": 0.0, "hwm": bank,
            "open_slips": [], "history": [], "events": []}


def effective_bank(st) -> float:
    return st["bank"] - sum(s["staked"] for s in st.get("open_slips", []))


def wealth(st) -> float:
    return st["bank"] + st["withdrawn"]


# ---------------- selection / planning ----------------
def playable_legs(rows, day=None, settled=None):
    """Playable, priced legs — the NO-FILTER set (validated)."""
    out = []
    for p in rows:
        if day is not None and str(p.get("date") or p.get("_archive_day") or "")[:10] != day:
            continue
        if p.get("bucket") not in BUCKETS:
            continue
        if str(p.get("quarantine") or "none").strip().lower() in BAD_QUARANTINE:
            continue
        ap = p.get("avg_p")
        try:
            odds = float(p.get("odds")) if p.get("odds") is not None else 0.0
        except (TypeError, ValueError):
            odds = 0.0
        if odds <= 1.0 or not ap:
            continue
        res = pick_result(p, settled) if settled is not None else None
        out.append({"match": f"{p.get('home')} vs {p.get('away')}",
                    "pick": str(p.get("pick") or "").upper(),
                    "prob": float(ap) / 100.0, "odds": odds,
                    "result": res, "row": p})
    out.sort(key=lambda l: (l["prob"], l["odds"]), reverse=True)
    return out


def plan_day(pool, bank):
    """Top legs by stated prob -> consecutive 2-leg accas -> 50% of bank split.
    Volume regime: pool >= VOLUME_POOL legs -> only prob >= VOLUME_MIN_PROB rides."""
    pool = sorted(pool, key=lambda l: (l["prob"], l["odds"]), reverse=True)
    if len(pool) >= VOLUME_POOL:
        pool = [l for l in pool if l["prob"] >= VOLUME_MIN_PROB]
    legs = pool[:MAX_LEGS]
    accas = [legs[i:i + LEGS_PER_ACCA] for i in range(0, len(legs) - 1, LEGS_PER_ACCA)][:MAX_ACCAS]
    accas = [a for a in accas if len(a) == LEGS_PER_ACCA]
    if not accas or bank <= 0:
        return []
    stake = bank * STAKE_FRAC / len(accas)
    plan = []
    for a in accas:
        prod = 1.0
        for l in a:
            prod *= l["odds"]
        plan.append({"legs": [{**{k: l[k] for k in ("match", "pick", "prob", "odds")},
                               "result": l.get("result")} for l in a],
                     "odds": round(prod, 2), "stake": round(stake, 4)})
    return plan


# ---------------- settlement (with profit banking + take-profit) ----------------
def _settle_bank(st, ret, staked, when):
    """Apply returns, the half-of-new-high withdrawal, and the TAKE-PROFIT
    trigger. Returns a list of human-readable event lines."""
    events = []
    st["bank"] += ret - staked
    if st["bank"] > st["hwm"]:
        take = (st["bank"] - st["hwm"]) * WITHDRAW_FRAC
        st["withdrawn"] += take
        st["bank"] -= take
        st["hwm"] = st["bank"]
        events.append(f"banked {take:.2f} at new high (bank {st['bank']:.2f})")
    if st["initial_bank"] and st["bank"] >= st["initial_bank"] * TAKE_PROFIT_MULT:
        profit = st["bank"] - st["initial_bank"]
        st["withdrawn"] += profit
        st["bank"] = st["initial_bank"]
        st["hwm"] = st["initial_bank"]
        st["events"].append({"date": when, "action": "TAKE_PROFIT",
                             "withdrawn": round(profit, 4), "bank_after": st["initial_bank"]})
        events.append(f"💰 TAKE PROFIT TRIGGERED — withdraw {profit:.2f} units "
                      f"(bank reset to base {st['initial_bank']:.2f}, cycle restarts)")
    return events


def settle_open_slips(st, settled, archives=None):
    """Grade every open slip whose legs are all settled. Returns event lines."""
    if archives is None:
        archives = load_archived_picks()
    index = {}
    for p in archives:
        day = str(p.get("date") or p.get("_archive_day") or "")[:10]
        index[(day, f"{p.get('home')} vs {p.get('away')}", str(p.get("pick") or "").upper())] = p
    lines, still_open = [], []
    for slip in st["open_slips"]:
        accas = []
        for a in slip["accas"]:
            legres = []
            for l in a["legs"]:
                p = index.get((slip["date"], l["match"], l["pick"]))
                legres.append(pick_result(p, settled) if p is not None else None)
            a = dict(a)
            a["results"] = legres
            a["won"] = all(r == "win" for r in legres) if legres and all(r for r in legres) else None
            accas.append(a)
        if accas and all(a["won"] is not None for a in accas):
            ret = sum(a["stake"] * a["odds"] for a in accas if a["won"])
            ev = _settle_bank(st, ret, slip["staked"], slip["date"])
            st["history"].append({"date": slip["date"], "staked": slip["staked"],
                                  "returned": round(ret, 4),
                                  "accas": [{"odds": a["odds"], "won": a["won"]} for a in accas],
                                  "bank": round(st["bank"], 4),
                                  "withdrawn": round(st["withdrawn"], 4)})
            lines.append(f"settled {slip['date']}: " + (" | ".join(ev) if ev else "no new high"))
        else:
            still_open.append(slip)
    st["open_slips"] = still_open
    save_state(st)
    return lines


# ---------------- commands ----------------
def cmd_backfill(args, st):
    """Replay the archived ledger through the engine (analysis / seeding)."""
    settled = load_settled()
    archives = load_archived_picks()
    days = sorted({str(p.get("date") or p.get("_archive_day") or "")[:10] for p in archives})
    days = [d for d in days if d < str(args.to or date.today()) and (not args.from_ or d >= args.from_)]
    st = fresh_state(args.bank) if (args.reset or not st) else st
    print(f"backfilling {days[0]}..{days[-1]} ({len(days)} days) at bank {st['bank']:.2f}")
    for d in days:
        pool = [l for l in playable_legs(archives, day=d, settled=settled) if l["result"]]
        if len(pool) < LEGS_PER_ACCA:
            continue
        plan = plan_day(pool, effective_bank(st))
        if not plan:
            continue
        staked = sum(a["stake"] for a in plan)
        ret = sum(a["stake"] * a["odds"] for a in plan
                  if all(l.get("result") == "win" for l in a["legs"]))
        _settle_bank(st, ret, staked, d)
        st["history"].append({"date": d, "staked": round(staked, 4), "returned": round(ret, 4),
                              "accas": [{"odds": a["odds"],
                                         "won": all(l.get("result") == "win" for l in a["legs"])}
                                        for a in plan],
                              "bank": round(st["bank"], 4),
                              "withdrawn": round(st["withdrawn"], 4)})
        if st["bank"] < 0.01:
            print(f"  BUSTED on {d}")
            break
    save_state(st)
    print_status(st)


def cmd_today(args, st):
    settled = load_settled()
    now = datetime.now(TZ)
    target = args.date or now.strftime("%Y-%m-%d")
    frozen = LOCALDATA / f"auto_tickets_{target}.frozen"
    slip_txt = LOCALDATA / f"auto_tickets_{target}.txt"
    if frozen.exists() and not args.force:
        print(f"TICKETS FROZEN — final slip for {target}. Re-printing saved slip:")
        print("=" * 62)
        if slip_txt.exists():
            print(slip_txt.read_text())
        return 0
    if str(target) == now.strftime("%Y-%m-%d") and now.hour < GENERATE_HOUR_START and not args.force:
        print(f"NOT YET — TICKETS START BUILDING AT {GENERATE_HOUR_START:02d}:00, FREEZE AT {FREEZE_HOUR:02d}:00")
        print(f"(now {now.strftime('%H:%M')} local)")
        return 0
    try:
        slate = json.loads((LOCALDATA / "picks_today.json").read_text())
    except Exception as e:
        print(f"cannot read picks_today.json: {e}")
        return 1
    pool = playable_legs(slate, day=target, settled=settled)
    pool = [l for l in pool
            if not (parse_kickoff(l["row"]) is not None and parse_kickoff(l["row"]) < now)]
    if len(pool) < LEGS_PER_ACCA:
        print(f"NO BET TODAY — {len(pool)} qualifying leg(s), need {LEGS_PER_ACCA}")
        print("(bank stays unbet; nothing to settle into a slip)")
        return 0
    bank_eff = effective_bank(st)
    plan = plan_day(pool, bank_eff)
    if not plan:
        print("NO BET TODAY — plan empty")
        return 0
    st["open_slips"].append({"date": target, "accas": plan,
                             "staked": round(sum(a["stake"] for a in plan), 4)})
    save_state(st)
    mult = wealth(st) / st["initial_bank"]
    lines = [f"AUTO TICKETS (ROLLING) — {target}", "=" * 62,
             f"bank {st['bank']:.2f} (committed {st['bank']-bank_eff:.2f}) · withdrawn {st['withdrawn']:.2f} "
             f"· wealth x{mult:.2f} · take-profit at bank {st['initial_bank']*TAKE_PROFIT_MULT:.2f}"]
    for i, a in enumerate(plan, 1):
        lines.append(f"\n[ACCA #{i}] @{a['odds']:.2f} — stake {a['stake']:.2f} "
                     f"({a['stake']/bank_eff:.1%} of effective bank)")
        for l in a["legs"]:
            lines.append(f"   {l['match']:46s} {l['pick']:5s} @ {l['odds']:.2f}  (stated {l['prob']:.0%})")
    lines.append(f"\ndeploying {STAKE_FRAC:.0%} of bank today · half of every new high is withdrawn at settlement "
                 f"· TAKE-PROFIT harvests everything above {TAKE_PROFIT_MULT:.0f}x the base bank.")
    lines.append("Round stakes to your bookmaker's minimum. Bet only what you can afford to lose.")
    txt = "\n".join(lines)
    print(txt)
    slip_txt.write_text(txt)
    if str(target) == now.strftime("%Y-%m-%d") and now.hour >= FREEZE_HOUR and not args.force:
        frozen.write_text(now.isoformat(timespec="seconds"))
        print(f"\nSTATUS: ✅ FROZEN at {now.strftime('%H:%M')} — FINAL slip; later runs re-print unchanged.")
    else:
        print(f"\nSTATUS: ⏳ DRAFT — regenerates each run until the {FREEZE_HOUR:02d}:00 freeze.")
    return 0


def print_status(st):
    if not st:
        print("no state yet — run bare (starts today at "
              f"{DEFAULT_BANK:.0f} units) or --backfill to replay history")
        return
    mult = wealth(st) / st["initial_bank"]
    accas = [a for h in st["history"] for a in h["accas"]]
    w = sum(1 for a in accas if a["won"])
    print(f"bank {st['bank']:.2f} · withdrawn {st['withdrawn']:.2f} · wealth x{mult:.2f} "
          f"· bet-days {len(st['history'])} · accas {w}W/{len(accas)-w}L "
          f"· open slips {len(st['open_slips'])} · take-profit at {st['initial_bank']*TAKE_PROFIT_MULT:.2f}")
    for e in st.get("events", []):
        print(f"  💰 {e['date']}: TAKE PROFIT — withdrew {e['withdrawn']:.2f}")
    for h in st["history"][-10:]:
        acc = " ".join(f"@{a['odds']:.2f}{'W' if a['won'] else 'L'}" for a in h["accas"])
        print(f"  {h['date']}  {acc:40s} bank {h['bank']:8.2f} (out {h['withdrawn']:7.2f})")


def main():
    ap = argparse.ArgumentParser(description="Rolling auto-tickets (validated acca engine)")
    ap.add_argument("--today", action="store_true", help="settle open slips, then build/reprint today")
    ap.add_argument("--settle", action="store_true", help="settle open slips only")
    ap.add_argument("--status", action="store_true", help="show bank / withdrawn / history")
    ap.add_argument("--backfill", action="store_true", help="replay archived ledger into state")
    ap.add_argument("--from", dest="from_", default=None)
    ap.add_argument("--to", default=None)
    ap.add_argument("--date", default=None)
    ap.add_argument("--bank", type=float, default=DEFAULT_BANK)
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    st = load_state()
    if args.backfill:
        cmd_backfill(args, st)
        return 0
    wants_today = args.today or args.force or not sys.argv[1:]
    if not st and (wants_today or args.settle):
        st = fresh_state(args.bank)   # first production run starts a fresh walk-forward
        save_state(st)
    if args.settle or wants_today:
        for line in settle_open_slips(st, load_settled()):
            print(line)
        if not wants_today:
            print_status(st)
            return 0
        return cmd_today(args, st)
    print_status(st)
    return 0


if __name__ == "__main__":
    sys.exit(main())

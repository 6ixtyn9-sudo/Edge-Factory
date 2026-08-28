#!/usr/bin/env python3
"""AUTO TICKETS — ROLLING EDITION, PERCENT-ONLY (operator doctrine: no amounts).

Everything this tool emits is a PERCENTAGE OF CAPITAL or a performance
multiple. There are no units, no rand amounts, no stakes in currency — the
operator maps percentages to money themselves.

Performance model: capital starts at 100 (%) and rolls. Settlements move the
bank percentage. Stakes are expressed as % of bank (and % of capital).

THE RECIPE (constants carry their validation receipts — see
TICKETS_DIAGNOSIS_2026-08-27.md and the 2026-08-27 HANDOVER addenda):
  LEGS      all playable-bucket picks with a price — NO further filtering.
  ORDER     highest stated probability first (ties by odds).
  ACCAS     2 legs each, consecutive pairs of the top 6, up to 3 per day.
  STAKE     50% of the bank per day, split across the accas built.
  PROFIT    no amounts are ever "withdrawn". Performance is tracked in %,
            and a TAKE-PROFIT NOTIFICATION fires when the bank reaches
            +100% above the cycle baseline (default): a loud 🔔 event is
            printed on every subsequent run, recorded in state/performance,
            and written to a persisted marker file. The cycle baseline then
            resets to the current bank so the next target is +100% again.
  VOLUME    pool >= 12 legs -> only stated-prob >= 65% legs ride.

Slip lifecycle matches the production cadence: builds from 06:00 SAST,
FREEZES at 12:00 (later runs re-print), settles as results land. State
persists in localdata/auto_tickets_state.json (gitignore exception exists).

Usage (daily.py runs this bare — same entry point as always):
  PYTHONPATH=src python3 scripts/auto_tickets.py            # settle + build/reprint today
  PYTHONPATH=src python3 scripts/auto_tickets.py --status   # performance / history
  PYTHONPATH=src python3 scripts/auto_tickets.py --backfill # replay ledger into state
  PYTHONPATH=src python3 scripts/auto_tickets.py --today --force
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

# ---------------- cadence (unchanged from production) ----------------
GENERATE_HOUR_START = 6    # local time — slips may START building on/after this hour
FREEZE_HOUR = 12           # local time — the slip FREEZES on/after this hour
TZ = ZoneInfo("Africa/Johannesburg")
PICK_RE = re.compile(r"^picks_(\d{4}-\d{2}-\d{2})\.json$")

# ---------------- the validated recipe (receipts, not knobs) ----------------
STAKE_FRAC = 0.50          # of bank per day (100% busted in every tested config)
MAX_ACCAS = 3              # concurrent accas per day
LEGS_PER_ACCA = 2          # 2-leg beat 3-leg out-of-sample
MAX_LEGS = MAX_ACCAS * LEGS_PER_ACCA
VOLUME_POOL = 12           # pool >= this -> volume regime
VOLUME_MIN_PROB = 0.65     # only prob >= this rides at volume
TAKE_PROFIT_GAIN = 1.00    # bank reaches baseline + 100% -> TAKE-PROFIT NOTIFICATION
BASE_PCT = 100.0           # capital starts at 100 (%) — everything is a percentage

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
            if fmt == "%H:%M":
                try:
                    dt = dt.replace(year=int(day[:4]), month=int(day[5:7]), day=int(day[8:10]))
                except ValueError:
                    return None
            elif fmt in ("%d-%m, %H:%M", "%d-%m, %H:%M:%S"):
                try:
                    base = datetime.strptime(day, "%Y-%m-%d").date()
                except ValueError:
                    return None
                cands = []
                for y in (int(day[:4]) - 1, int(day[:4]), int(day[:4]) + 1):
                    try:
                        c = dt.replace(year=y)
                    except ValueError:
                        continue
                    cands.append((abs((c.date() - base).days), c))
                if not cands:
                    return None
                dt = min(cands, key=lambda t: t[0])[1]
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


def _fold(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower().strip()


def _lookup_fallback(settled, day, home, away):
    from datetime import timedelta as _td
    from difflib import SequenceMatcher
    try:
        base = datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError:
        return None
    cands = [day, str(base - _td(days=1)), str(base + _td(days=1))]
    fh, fa = _fold(home), _fold(away)
    best, best_oc = 0.0, None
    for (d, h, a), oc in settled.items():
        if d not in cands:
            continue
        rh = SequenceMatcher(None, fh, _fold(h)).ratio()
        if rh < 0.8:
            continue
        ra = SequenceMatcher(None, fa, _fold(a)).ratio()
        if ra >= 0.8 and rh + ra > best:
            best, best_oc = rh + ra, oc
    return best_oc


def pick_result(pick, settled):
    from edgefactory.util import norm_team
    day = str(pick.get("date") or pick.get("_archive_day") or "")[:10]
    home = norm_team(pick.get("home") or "")
    away = norm_team(pick.get("away") or "")
    outcome = settled.get((day, home, away))
    if outcome is not None and outcome not in ("home", "away", "draw"):
        return "void"
    if outcome is None:
        outcome = _lookup_fallback(settled, day, home, away)
    if outcome is not None and outcome not in ("home", "away", "draw"):
        return "void"
    if outcome is None:
        return None
    sel = str(pick.get("pick") or "").lower()
    if outcome == "draw":
        return "loss"
    return "win" if outcome == sel else "loss"


# ---------------- state (all percentages of capital) ----------------
def load_state() -> dict:
    try:
        st = json.loads(STATE_FILE.read_text())
    except Exception:
        return {}
    slips = st.get("open_slips") or []
    if slips:
        seen, order = {}, []
        for sl in slips:
            d = sl.get("date")
            if d not in seen:
                seen[d] = sl; order.append(d)
        st["open_slips"] = [seen[d] for d in order]
    return st


def save_state(st: dict) -> None:
    STATE_FILE.write_text(json.dumps(st, indent=2, default=str))


def fresh_state() -> dict:
    return {"base_pct": BASE_PCT, "bank": BASE_PCT, "cycle_base": BASE_PCT,
            "open_slips": [], "history": [], "events": []}


def effective_bank(st) -> float:
    """Bank minus committed (open) stakes — in % of capital."""
    return st["bank"] - sum(s["staked_pct"] for s in st.get("open_slips", []))


def take_profit_target(st) -> float:
    return st["cycle_base"] * (1.0 + TAKE_PROFIT_GAIN)


# ---------------- selection / planning ----------------
def playable_legs(rows, day=None, settled=None):
    """Playable, priced legs — the NO-FILTER set (validated)."""
    out = []
    for p in rows:
        if day is not None and str(p.get("date") or p.get("_archive_day") or "")[:10] != day:
            continue
        if p.get("bucket") not in BUCKETS:
            continue
        q = str(p.get("price_quarantine_reason") or p.get("quarantine") or "none").strip().lower()
        if q in BAD_QUARANTINE and not p.get("odds_replaced"):
            continue   # suspect price unless betexplorer-rescued (rescue pops the reason)
        if str(p.get("price_evidence") or "").upper() == "SUSPECT_ALIAS_FUZZY" and not p.get("odds_replaced"):
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


def plan_day(pool, bank_pct):
    """Top legs by stated prob -> consecutive 2-leg accas -> 50% of bank split
    (stakes returned as % of capital). Volume regime applies at >= VOLUME_POOL."""
    pool = sorted(pool, key=lambda l: (l["prob"], l["odds"]), reverse=True)
    if len(pool) >= VOLUME_POOL:
        pool = [l for l in pool if l["prob"] >= VOLUME_MIN_PROB]
    legs = pool[:MAX_LEGS]
    accas = [legs[i:i + LEGS_PER_ACCA] for i in range(0, len(legs) - 1, LEGS_PER_ACCA)][:MAX_ACCAS]
    accas = [a for a in accas if len(a) == LEGS_PER_ACCA]
    if not accas or bank_pct <= 0:
        return []
    stake_pct = bank_pct * STAKE_FRAC / len(accas)
    plan = []
    for a in accas:
        prod = 1.0
        for l in a:
            prod *= l["odds"]
        plan.append({"legs": [{**{k: l[k] for k in ("match", "pick", "prob", "odds")},
                               "result": l.get("result")} for l in a],
                     "odds": round(prod, 2), "stake_pct": round(stake_pct, 4)})
    return plan


# ---------------- settlement + take-profit notification ----------------
def _apply_settlement(st, ret_pct, staked_pct, when):
    """Move the bank by the settled P&L (all %) and fire the TAKE-PROFIT
    NOTIFICATION when performance reaches the cycle target. No amounts are
    withdrawn — the operator acts on the notification. Returns event lines."""
    events = []
    st["bank"] += ret_pct - staked_pct
    if st["bank"] >= take_profit_target(st):
        gain_pct = st["bank"] - st["cycle_base"]
        st["cycle_base"] = st["bank"]
        note = (f"🔔 TAKE-PROFIT: performance +{gain_pct:.1f}% of capital this cycle "
                f"(bank now {st['bank']:.1f}%). ACT ON YOUR PLAN — bank it. "
                f"Next notification at {take_profit_target(st):.1f}%.")
        st["events"].append({"date": when, "action": "TAKE_PROFIT_NOTIFICATION",
                             "gain_pct": round(gain_pct, 2),
                             "bank_after_pct": round(st["bank"], 2),
                             "next_target_pct": round(take_profit_target(st), 2)})
        marker = LOCALDATA / f"auto_tickets_takeprofit_{when}.json"
        try:
            marker.write_text(json.dumps(st["events"][-1], indent=2))
        except Exception:
            pass
        events.append(note)
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
                r = pick_result(p, settled) if p is not None else None
                if r is None and p is not None:
                    kt = parse_kickoff(p)
                    if kt is not None and (datetime.now(TZ) - kt).days >= 5:
                        r = "void"
                legres.append(r)
            a = dict(a)
            a["results"] = legres
            if legres and all(r for r in legres):
                live = [l for l, r in zip(a["legs"], legres) if r != "void"]
                if not live:
                    a["won"] = True; a["odds"] = 1.0          # all void: stake back
                else:
                    a["won"] = all(r == "win" for r in legres if r != "void")
                    a["odds"] = round(math.prod(l["odds"] for l in live), 2)  # book-style: void drops out
            else:
                a["won"] = None
            accas.append(a)
        if accas and all(a["won"] is not None for a in accas):
            ret = sum(a["stake_pct"] * a["odds"] for a in accas if a["won"])
            ev = _apply_settlement(st, ret, slip["staked_pct"], slip["date"])
            st["history"].append({"date": slip["date"], "staked_pct": round(slip["staked_pct"], 4),
                                  "returned_pct": round(ret, 4),
                                  "accas": [{"odds": a["odds"], "won": a["won"]} for a in accas],
                                  "bank_pct": round(st["bank"], 4)})
            lines.append(f"settled {slip['date']}: bank {st['bank']:.1f}%"
                         + ((" | " + " | ".join(ev)) if ev else ""))
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
    st = fresh_state() if (args.reset or not st) else st
    print(f"backfilling {days[0]}..{days[-1]} ({len(days)} days) from bank {st['bank']:.1f}%")
    for d in days:
        pool = [l for l in playable_legs(archives, day=d, settled=settled) if l["result"]]
        if len(pool) < LEGS_PER_ACCA:
            continue
        plan = plan_day(pool, effective_bank(st))
        if not plan:
            continue
        staked = sum(a["stake_pct"] for a in plan)
        ret = sum(a["stake_pct"] * a["odds"] for a in plan
                  if all(l.get("result") == "win" for l in a["legs"]))
        _apply_settlement(st, ret, staked, d)
        st["history"].append({"date": d, "staked_pct": round(staked, 4),
                              "returned_pct": round(ret, 4),
                              "accas": [{"odds": a["odds"],
                                         "won": all(l.get("result") == "win" for l in a["legs"])}
                                        for a in plan],
                              "bank_pct": round(st["bank"], 4)})
        if st["bank"] < 1.0:
            print(f"  BUSTED on {d} (bank {st['bank']:.1f}%)")
            break
    save_state(st)
    print_status(st)


def upsert_slip(st, target, plan):
    st["open_slips"] = [s for s in st["open_slips"] if s["date"] != target]
    upsert_slip(st, target, plan)


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
        print("(bank stays unbet)")
        return 0
    bank_eff = effective_bank(st)
    plan = plan_day(pool, bank_eff)
    if not plan:
        print("NO BET TODAY — plan empty")
        return 0
    st["open_slips"].append({"date": target, "accas": plan,
                             "staked_pct": round(sum(a["stake_pct"] for a in plan), 4)})
    save_state(st)
    lines = [f"AUTO TICKETS (ROLLING) — {target}", "=" * 62,
             f"PERFORMANCE: bank {st['bank']:.1f}% of capital (x{st['bank']/st['base_pct']:.2f}) · "
             f"committed {st['bank']-bank_eff:.1f}% · next take-profit notification at {take_profit_target(st):.1f}%"]
    for i, a in enumerate(plan, 1):
        lines.append(f"\n[ACCA #{i}] @{a['odds']:.2f} — stake {a['stake_pct']:.1f}% of capital "
                     f"({a['stake_pct']/bank_eff:.1%} of bank)")
        for l in a["legs"]:
            lines.append(f"   {l['match']:46s} {l['pick']:5s} @ {l['odds']:.2f}  (stated {l['prob']:.0%})")
    lines.append(f"\ndeploying {STAKE_FRAC:.0%} of bank today · take-profit NOTIFICATION at "
                 f"+{TAKE_PROFIT_GAIN:.0%} per cycle (performance-based; you act on it).")
    lines.append("All figures are percentages of capital. Round to your bookmaker's minimum stake. "
                 "Bet only what you can afford to lose.")
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
        print("no state yet — run bare (starts today at 100%) or --backfill to replay history")
        return
    accas = [a for h in st["history"] for a in h["accas"]]
    w = sum(1 for a in accas if a["won"])
    print(f"bank {st['bank']:.1f}% of capital (x{st['bank']/st['base_pct']:.2f}) · "
          f"bet-days {len(st['history'])} · accas {w}W/{len(accas)-w}L · "
          f"open slips {len(st['open_slips'])} · next take-profit at {take_profit_target(st):.1f}%")
    for e in st.get("events", []):
        print(f"  🔔 {e['date']}: TAKE-PROFIT — +{e['gain_pct']:.1f}% that cycle "
              f"(bank {e['bank_after_pct']:.1f}%, next target {e['next_target_pct']:.1f}%)")
    for h in st["history"][-10:]:
        acc = " ".join(f"@{a['odds']:.2f}{'W' if a['won'] else 'L'}" for a in h["accas"])
        print(f"  {h['date']}  {acc:40s} bank {h['bank_pct']:7.1f}%")


def main():
    ap = argparse.ArgumentParser(description="Rolling auto-tickets (percent-only, validated acca engine)")
    ap.add_argument("--today", action="store_true", help="settle open slips, then build/reprint today")
    ap.add_argument("--settle", action="store_true", help="settle open slips only")
    ap.add_argument("--status", action="store_true", help="show performance / history")
    ap.add_argument("--backfill", action="store_true", help="replay archived ledger into state")
    ap.add_argument("--from", dest="from_", default=None)
    ap.add_argument("--to", default=None)
    ap.add_argument("--date", default=None)
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    st = load_state()
    if args.backfill:
        cmd_backfill(args, st)
        return 0
    wants_today = args.today or args.force or not sys.argv[1:]
    if not st and (wants_today or args.settle):
        st = fresh_state()   # first production run starts a fresh walk-forward at 100%
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

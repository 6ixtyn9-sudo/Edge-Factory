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


# Settled-donor priority order — mirrors audit_recent_picks.load_results_index.
# BetExplorer is the widest-league donor (lowest priority): it fills fixtures
# the probability sources never captured, but loses to them on a conflict.
_SETTLED_SOURCES = [
    (1, "forebet_settled"),
    (2, "bettingclosed_settled"),
    (3, "zulubet_settled"),
    (4, "statarea_settled"),
    (5, "scoutingstats_settled"),
    (6, "vitibet_settled"),
    (7, "betexplorer_settled"),
]


def _collect_settled_facts() -> tuple[dict, dict]:
    """(key_to_outcome, entries_by_date) from warehouse donors + shared overlay.

    key_to_outcome is the exact-lookup map (warehouse wins on conflict, then
    overlay fills gaps). entries_by_date keeps the FULL home/away names per
    date so alias-conflict detection can see every spelling of a fixture.
    """
    from edgefactory.util import norm_team

    key_to: dict = {}
    entries: dict[str, list[dict]] = {}
    wh = LOCALDATA / "warehouse.duckdb"
    if wh.exists():
        try:
            import duckdb
        except Exception:
            duckdb = None
        if duckdb is not None:
            con = None
            try:
                con = duckdb.connect(str(wh), read_only=True)
                tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
                for _prio, name in _SETTLED_SOURCES:
                    if name not in tables:
                        continue
                    try:
                        rows = con.execute(
                            f"SELECT date, home, away, outcome FROM {name} "
                            "WHERE hs IS NOT NULL AND gs IS NOT NULL"
                        ).fetchall()
                    except Exception:
                        continue
                    for day, home, away, outcome in rows:
                        d = str(day)[:10]
                        key_to.setdefault((d, norm_team(home), norm_team(away)), str(outcome))
                        entries.setdefault(d, []).append(
                            {"home": str(home), "away": str(away), "outcome": str(outcome)}
                        )
            except Exception:
                pass
            finally:
                if con is not None:
                    con.close()
    try:
        data = json.loads((LOCALDATA / "settled_results.json").read_text())
    except Exception:
        data = None
    if data:
        seen_sigs: set[tuple] = set()
        for r in data.get("rows", []):
            d = str(r.get("date") or "")[:10]
            home, away = r.get("home"), r.get("away")
            key_to.setdefault((d, norm_team(home), norm_team(away)), r.get("outcome"))
            sig = (d, str(home or "").lower(), str(away or "").lower())
            if sig not in seen_sigs:
                seen_sigs.add(sig)
                entries.setdefault(d, []).append(
                    {"home": str(home), "away": str(away), "outcome": str(r.get("outcome"))}
                )
    # Operator-verified scores outrank every donor and the overlay. Overwrite
    # the key and purge every alias-matching entry (any spelling) from the
    # alias scan so a bad donor row filed under an alternate spelling cannot
    # hold a leg as a conflict.
    from edgefactory.settlement import load_verified_results
    for v in load_verified_results():
        d = v["date"]
        h9, a9 = norm_team(v["home"]), norm_team(v["away"])
        key_to[(d, h9, a9)] = v["outcome"]
        alias_ids = {
            id(e)
            for e in _alias_candidate_entries(
                {"date": d, "home": v["home"], "away": v["away"]}, entries
            )
        }
        entries[d] = [e for e in entries.get(d, []) if id(e) not in alias_ids]
        entries.setdefault(d, []).append(
            {"home": v["home"], "away": v["away"], "outcome": v["outcome"]}
        )
    return key_to, entries


def load_settled():
    """Settled outcomes: warehouse donors first, shared overlay fills gaps.

    Keeps auto-ticket grading on the same result facts as the audit instead
    of overlay-only, so BetExplorer-settled fixtures grade here too.
    """
    return _collect_settled_facts()[0]


def load_settled_entries():
    """Per-date list of {home, away, outcome} for alias-conflict detection."""
    return _collect_settled_facts()[1]


def _fold(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower().strip()


# Rescheduled fallback window — mirrors the audit's ±3-day rescheduled scan.
# A fixture that moved 2 days (Hønefoss W 08-29 -> 08-31) still grades here;
# ±1 day missed it and froze the acca on a result the audit had already seen.
RESCHEDULE_WINDOW_DAYS = 3


def _lookup_fallback(settled, day, home, away):
    from datetime import timedelta as _td
    from difflib import SequenceMatcher
    try:
        base = datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError:
        return None
    cands = {str(base + _td(days=o))
             for o in range(-RESCHEDULE_WINDOW_DAYS, RESCHEDULE_WINDOW_DAYS + 1)}
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


def _ngram_sim(s1: str, s2: str, n: int = 2) -> float:
    """Bigram Jaccard similarity (same rule as the audit's fuzzy matcher)."""
    def grams(s: str) -> set[str]:
        clean = re.sub(r"[^a-z0-9]", "", s.lower())
        return {clean[i:i + n] for i in range(len(clean) - n + 1)} if len(clean) >= n else set()
    g1, g2 = grams(s1), grams(s2)
    if not g1 or not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)


_ALIAS_MIN_SIM = 0.40  # matches the audit's _FUZZY_MIN_SIM
_ALIAS_SIDE_MIN_SIM = 0.30  # per-side floor: key collisions (W-suffix teams) are not aliases


def _alias_candidate_entries(pick, entries_by_date) -> list[dict]:
    """Entries on the pick's date that alias-match both sides (orientation-
    checked). Mirrors the audit's ``_alias_candidate_results`` so the verified
    override can purge every spelling of a fixture, not just one normalized
    pair."""
    from edgefactory.util import norm_team

    day = str(pick.get("date") or pick.get("_archive_day") or "")[:10]
    home = str(pick.get("home") or "")
    away = str(pick.get("away") or "")
    home_keys = {norm_team(home)}
    away_keys = {norm_team(away)}
    out: list[dict] = []
    for e in entries_by_date.get(day, []):
        rh = str(e.get("home") or "")
        ra = str(e.get("away") or "")
        hk = norm_team(rh)
        ak = norm_team(ra)
        if not (hk in home_keys or ak in away_keys or hk in away_keys or ak in home_keys):
            continue
        sim_hh = _ngram_sim(home, rh)
        sim_aa = _ngram_sim(away, ra)
        if min(sim_hh, sim_aa) < _ALIAS_SIDE_MIN_SIM:
            continue
        if not (sim_hh > _ngram_sim(home, ra) and sim_aa > _ngram_sim(away, rh)):
            continue
        if _ngram_sim(f"{home} {away}", f"{rh} {ra}") < _ALIAS_MIN_SIM:
            continue
        out.append(e)
    return out


def alias_outcome_conflict(pick, entries_by_date) -> bool:
    """True when the fixture is filed under several spellings on its date with
    differing outcomes (Pafos vs Dinamo Tirana 2-2 draw vs 4-2 home).

    Fail-closed: a conflict keeps the leg unresolved instead of silently
    first-winning one spelling. Pre-filtered by shared team key, then
    orientation-checked by bigram similarity so genuinely different fixtures
    sharing a key fragment do not trigger a conflict.
    """
    outcomes = {
        str(e.get("outcome") or "")
        for e in _alias_candidate_entries(pick, entries_by_date)
        if str(e.get("outcome") or "") in ("home", "away", "draw")
    }
    return len(outcomes) > 1


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
        # Market guard: the validated recipe is 1X2 ONLY. Goals/OU picks
        # (first seen 2026-08-31, "Breidablik OVER") stay out until the
        # September O2.5 checkpoint passes its gate. Never before.
        if str(p.get("market") or "1x2").lower() != "1x2":
            continue
        if str(p.get("pick") or "").lower() in ("over", "under", "yes", "no"):
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


def _record_acca_settlement(st, slip_date, acca):
    """Append/update a per-day history entry for one settled acca.

    Per-acca settlement means a day's accas can settle across several runs (a
    stuck leg no longer freezes the whole day's stake). History stays grouped
    by date so the performance report still reads one line per bet-day.
    """
    won = bool(acca["won"])
    ret = round(acca["stake_pct"] * acca["odds"] if won else 0.0, 4)
    for h in st["history"]:
        if h["date"] == slip_date:
            h["staked_pct"] = round(h["staked_pct"] + acca["stake_pct"], 4)
            h["returned_pct"] = round(h["returned_pct"] + ret, 4)
            h["accas"].append({"odds": acca["odds"], "won": won})
            h["bank_pct"] = round(st["bank"], 4)
            return
    st["history"].append({
        "date": slip_date,
        "staked_pct": round(acca["stake_pct"], 4),
        "returned_pct": ret,
        "accas": [{"odds": acca["odds"], "won": won}],
        "bank_pct": round(st["bank"], 4),
    })


def settle_open_slips(st, settled, archives=None, entries_by_date=None):
    """Grade every acca whose legs are all settled; the bank moves per acca.

    An acca settles as soon as all its legs resolve — a single stuck leg no
    longer freezes the whole day's stake. A leg whose fixture is filed under
    several spellings with differing outcomes is held open (fail-closed) and
    surfaced as a conflict. Returns event lines.
    """
    if archives is None:
        archives = load_archived_picks()
    if entries_by_date is None:
        entries_by_date = load_settled_entries()
    index = {}
    for p in archives:
        day = str(p.get("date") or p.get("_archive_day") or "")[:10]
        index[(day, f"{p.get('home')} vs {p.get('away')}", str(p.get("pick") or "").upper())] = p
    lines, still_open = [], []
    for slip in st["open_slips"]:
        open_accas = []
        for a in slip["accas"]:
            legres = []
            conflicts = []
            for l in a["legs"]:
                p = index.get((slip["date"], l["match"], l["pick"]))
                if p is None:
                    r = None
                elif alias_outcome_conflict(p, entries_by_date):
                    # Fail-closed: donors disagree across spellings. Hold the
                    # leg instead of first-winning the exact-key spelling.
                    r = "conflict"
                    conflicts.append(l["match"])
                else:
                    r = pick_result(p, settled)
                    if r is None:
                        kt = parse_kickoff(p)
                        if kt is not None and (datetime.now(TZ) - kt).days >= 5:
                            r = "void"
                legres.append(r)
            a = dict(a)
            a["results"] = legres
            resolved = legres and all(r in ("win", "loss", "void") for r in legres)
            if resolved:
                live = [l for l, r in zip(a["legs"], legres) if r != "void"]
                if not live:
                    a["won"] = True; a["odds"] = 1.0          # all void: stake back
                else:
                    a["won"] = all(r == "win" for r in legres if r != "void")
                    a["odds"] = round(math.prod(l["odds"] for l in live), 2)  # book-style: void drops out
            else:
                a["won"] = None
            if a["won"] is None:
                if conflicts:
                    lines.append(
                        f"held {slip['date']} acca @{a['odds']:.2f}: conflict on "
                        f"{', '.join(conflicts)} (donor spellings disagree on outcome)"
                    )
                open_accas.append(a)
                continue
            ret = a["stake_pct"] * a["odds"] if a["won"] else 0.0
            ev = _apply_settlement(st, ret, a["stake_pct"], slip["date"])
            _record_acca_settlement(st, slip["date"], a)
            lines.append(f"settled {slip['date']} acca @{a['odds']:.2f}: bank {st['bank']:.1f}%"
                         + ((" | " + " | ".join(ev)) if ev else ""))
        if open_accas:
            slip = dict(slip)
            slip["accas"] = open_accas
            slip["staked_pct"] = round(sum(a["stake_pct"] for a in open_accas), 4)
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
    st["open_slips"].append({"date": target, "accas": plan,
                             "staked_pct": round(sum(a["stake_pct"] for a in plan), 4)})
    save_state(st)


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
    pool = [l for l in pool if not l.get("result")]
    # Cross-slate guard: a fixture already archived on an EARLIER day's slate
    # has already kicked off (late finishers carried into today's capture).
    past = set()
    for a in load_archived_picks():
        if str(a.get("date") or a.get("_archive_day") or "")[:10] < target:
            past.add((str(a.get("home") or "").strip().lower(),
                      str(a.get("away") or "").strip().lower()))
    pool = [l for l in pool
            if (str(l["row"].get("home") or "").strip().lower(),
                str(l["row"].get("away") or "").strip().lower()) not in past]
    if len(pool) < LEGS_PER_ACCA:
        print(f"NO BET TODAY — {len(pool)} qualifying leg(s), need {LEGS_PER_ACCA}")
        print("(bank stays unbet)")
        return 0
    bank_eff = effective_bank(st)
    plan = plan_day(pool, bank_eff)
    if not plan:
        print("NO BET TODAY — plan empty")
        return 0
    upsert_slip(st, target, plan)
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

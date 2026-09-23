#!/usr/bin/env python3
"""AUTO TICKETS — ROLLING EDITION, PERCENT-ONLY (operator doctrine: no amounts).

Everything this tool emits is a PERCENTAGE OF CAPITAL or a performance
multiple. There are no units, no rand amounts, no stakes in currency — the
operator maps percentages to money themselves.

Performance model: capital starts at 100 (%) and rolls. Settlements move the
bank percentage. A stake's printed denominator is always stated next to the
number ("% of capital", "% of free bank"); "bank" alone means total bank,
"free bank" = total bank minus committed (open) stakes.

THE RECIPE (constants carry their validation receipts — see
TICKETS_DIAGNOSIS_2026-08-27.md and the 2026-08-27 HANDOVER addenda):
  LEGS      all playable-bucket picks with a price — NO further filtering.
  ORDER     highest stated probability first (ties by odds).
  DEDUP     one match, one leg: after ranking, same-fixture duplicates
            (date + folded side-pair incl. '&'->'and') are dropped and the
            highest-stated twin survives (2026-09-22 Dagenham-and/& incident;
            upstream ledger identity untouched — the guard protects the card).
  ACCAS     2 legs each, consecutive pairs of the top 6, up to 3 per day.
  STAKE     1/3 of the bank per day, split across the accas built
            (2026-09-04 sizing audit: on the 52-day replay the growth-optimal
            fraction is ~40%, and the growth curve is FLAT from 30-50% while
            max drawdown climbs 62% -> 87%. 50% was past the peak: LOWER
            growth AND higher risk. 1/3 keeps 96% of peak growth at 67% DD.
            Raising the fraction stays rejected — 75% and 100% bust.)
  PROFIT    no amounts are ever "withdrawn". Performance is tracked in %,
            and a TAKE-PROFIT NOTIFICATION fires when the bank reaches
            +100% above the cycle baseline (default): a loud 🔔 event is
            printed on every subsequent run, recorded in state/performance,
            and written to a persisted marker file. The cycle baseline then
            resets to the current bank so the next target is +100% again.
  VOLUME    OFF. The saturated-day stated-prob gate was audited on
            2026-09-04 and proven to be a NO-OP in every configuration
            (0/57 days changed for any threshold 0.00-0.95): the pool is
            prob-sorted, so a prob filter only trims a suffix the top-6 never
            reached, and the completeness fallback restored it anyway. The
            machinery survives as GATE_MODE="acca" (per-acca conviction
            gate, the only shape that can bite) and is PRE-REGISTERED, not
            live — see the 2026-09-04 addendum, checkpoint ⑥.

Slip lifecycle matches the production cadence: builds from 06:00 SAST,
FREEZES at 09:00 (FREEZE_HOUR; later runs re-print), settles as results
land. Every build runs the LIVE KICKOFF GUARD: a leg whose kickoff is
missing/garbage, or clock-only (bare "HH:MM" or no-year day-month) in a
league region whose clock is far from SAST (Americas / Asia-Pacific — the
incident-#6 Vancouver class), or already started at build time, drops, and
each run prints the skip census. The fail-closed KICKOFF PROOF CONTRACT
exists as an OFF-by-default audit tool (replay_harness.py --kickoff-contract)
— it is not the live rule. State persists in localdata/auto_tickets_state.json
(gitignore exception exists).

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
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
LOCALDATA = ROOT / "localdata"

# ---------------- cadence (unchanged from production) ----------------
GENERATE_HOUR_START = 6    # local time — slips may START building on/after this hour
FREEZE_HOUR = 9            # local time — the slip FREEZES on/after this hour.
                             # Measured 2026-09-02: 09:00 freeze covers ~94% of leg
                             # kickoffs (noon ~86%, de-facto-14:00 ~76%); morning slate
                             # median-complete by 09:00; external cron's 09:00 SAST run
                             # lands the marker ~09:23, ahead of every observed bet time.
TZ = ZoneInfo("Africa/Johannesburg")
_UTC = ZoneInfo("UTC")
PICK_RE = re.compile(r"^picks_(\d{4}-\d{2}-\d{2})\.json$")

# ---------------------------------------------------------------------------
# KICKOFF GUARDS (incident #6 — 2026-09-06, Vancouver Whitecaps).
#
# On 2026-09-06 the engine staked ACCA #3 on "Vancouver Whitecaps vs St.
# Louis City" at 09:13 SAST. The match had kicked off at 2026-09-05 22:30 EDT
# = 02:30 UTC = 04:30 SAST — over ~4h45m before the ticket printed. Sixth
# ghost incident. The Vancouver row's kickoff field is the bare string
# "22:30" — no date, no offset, no zone (odds_source scoutingstats_odds,
# sole/uncorroborated). A row like that cannot say when the match starts, yet
# the 2026-09-04 patch (league-substring -> IANA zone table + SAST-default
# parsing) let it ride: it failed open on unprovable kickoffs AND mis-zoned
# west-coast fixtures even when its lookup "succeeded". Deleted, not extended.
#
# TWO layers, deliberately different in strength:
#
# 1. LIVE guard (cmd_today, this file), narrowed 2026-09-06 round 2 after the
#    region audit, and keyed to ingest normalisation from the 2026-09-06
#    follow-up session (Task A): when the row carries a resolved
#    `kickoff_utc` (an absolute instant emitted by picks_today.py — from the
#    pick's own offset/Z string or from a same-fixture source row that
#    declared one, e.g. scoutingstats "...Z" or vitibet "+02:00"; see
#    picks_today.attach_kickoff_normalisation), the guard judges ONLY that
#    instant: started at build -> drop (KO_SKIP_STARTED), still ahead -> ride.
#    The region rule is the FALLBACK for rows whose kickoff is CLOCK-ONLY
#    (bare "HH:MM" or yearless "DD-MM, HH:MM") AND whose league region's
#    clock is far from SAST (Americas / Asia-Pacific — a bare "22:30" MLS
#    clock read on the slate day is the incident class, off by up to 18h in
#    the fatal direction) and which normalisation could NOT resolve, or when
#    the kickoff is missing/garbage, or when the dated kickoff is already
#    at/past build time. Clock-only rows from Europe / Africa ride on the
#    SAST reading (their clocks are within ~1-2h of SAST; a wrong read errs
#    by an hour or two, in the safe direction on the historical evidence).
#    The region list ONLY answers "is the SAST reading of this clock
#    trustworthy?" — it never computes a kickoff instant, so a mis-hit drops
#    a leg that could have been bet (no-bet, harmless direction); it cannot
#    fabricate a wrong time. Rows carrying a full calendar date with a year
#    (naive "YYYY-MM-DD HH:MM" or an explicit-offset instant) are compared
#    with parse_kickoff and drop when already started: the feeds render dated
#    rows on a UTC+2 clock (Inter Miami's explicit +02:00 row; the wall-clock
#    evidence in the 2026-09-06 HANDOVER addendum). That rendering is the
#    feed contract — tested, never re-guessed from a league table. No 4h
#    lead buffer on the live path.
# 2. AUDIT contract (kickoff_contract; replay_harness.py --kickoff-contract,
#    OFF by default): the fail-closed standard — a leg rides only when its
#    kickoff is PROVEN by the row itself (explicit UTC offset/Z, or naive +
#    row-carried kickoff_tz) and is at least KICKOFF_MIN_LEAD_HOURS ahead.
#    This is the measurement instrument for the data-side fix (how many legs
#    cannot prove themselves today), NOT the live betting rule.
# ---------------------------------------------------------------------------
KICKOFF_MIN_LEAD_HOURS = 4.0    # AUDIT-ONLY lead. Proven kickoffs must clear
                                # this many hours or the audit contract drops
                                # them (result feeds lag). Never the live
                                # rule (2026-09-06 review).
KO_SKIP_NO_DATE = "missing / unparseable kickoff"
KO_SKIP_REMOTE_CLOCK = ("clock-only kickoff (bare time or no-year day-month) in a "
                        "league region far from SAST — SAST rendering untrusted")
KO_SKIP_UNPROVEN = "unprovable kickoff (no explicit offset or row-carried zone)"
KO_SKIP_STARTED = "already started (dated kickoff at/past build time)"
KO_SKIP_TOO_CLOSE = f"audit: kickoff under {KICKOFF_MIN_LEAD_HOURS:g}h away or already started (provable)"

# ---------------- the validated recipe (receipts, not knobs) ----------------
STAKE_FRAC = 1.0 / 4.0     # ARMED 2026-09-09 with PAIRING=barbell, MAX_ACCAS=2.
                           # Deliberate override of the pre-registered October bar
                           # on IN-SAMPLE evidence: 4/4 and 5/5 on the mined 75
                           # bet-days (full +0.0231, heavy +0.0113, pessimistic
                           # +0.0023 log/day; maxDD 73%->49%; both blind halves
                           # positive). ~90% of the settled level is optimism;
                           # ridden legs beat the close only 12.3%. Revert = 1.0/10.0.
STAKE_MODE = "per_acca"     # "per_day" preserves the validated fixed day risk;
                           # "per_acca" risks a fixed fraction per ticket while
                           # capping the day's total at STAKE_FRAC. Research only.
STAKE_PER_ACCA = None      # None -> STAKE_FRAC / MAX_ACCAS
STAKE_WEIGHTS = None       # None -> equal; e.g. "3,2,1" changes sizing, never selection
MAX_ACCAS = 2              # ARMED 2026-09-09 (barbell x2). Revert = 3.
MIN_ACCAS = 1              # cards with fewer accas are NO BET (1 preserves live)
LEGS_PER_ACCA = 2          # 2-leg beat 3-leg out-of-sample
MAX_LEGS = MAX_ACCAS * LEGS_PER_ACCA
PAIRING = "barbell"        # ARMED 2026-09-09. Revert = "consecutive".
MIN_LEG_ODDS = 1.20        # min odds per leg (2026-09-02..04 band evidence; the
                           # replay harness A/Bs this knob — never inline the number)
VOLUME_POOL = 12           # pool >= this -> volume regime (saturated day)
VOLUME_MIN_PROB = 0.65     # stated-prob threshold used by the volume regime
GATE_MODE = "off"          # how the volume regime bites on saturated days:
                           #   "off"  - no gate
                           #   "pool" - LEGACY pool-prefix filter. PROVEN NO-OP:
                           #            the pool is prob-sorted, so the filter only
                           #            ever trims a suffix, and the completeness
                           #            fallback restores it. 0/57 days differ for
                           #            ANY threshold 0.00-0.95 (audit 2026-09-04).
                           #   "acca" - per-acca gate: on saturated days an acca
                           #            rides only if BOTH legs clear VOLUME_MIN_PROB.
                           #            Same 50% total risk, spread over fewer,
                           #            higher-conviction accas. This one bites.
TAKE_PROFIT_GAIN = 1.00    # bank reaches baseline + 100% -> TAKE-PROFIT NOTIFICATION
BASE_PCT = 100.0           # capital starts at 100 (%) — everything is a percentage

BUCKETS = {
    "CERTIFIED_CLEAN",
    "SKIPPED_VETO",
    "WATCHLIST_UNKNOWN_CTX",
    "WATCHLIST_UNCORROBORATED_PRICE",
    # 2026-09-08 operator decision, taken against the evidence.
    # In-season n=91, ROI -0.6%, 80% interval -11.3%..+9.8%. The
    # bucket spread is reproduced by label-shuffling ~85-98% of the
    # time depending on window. SUSPECT_PRICE and NO_ODDS stay OUT:
    # they flag bad DATA, not weak edges.
    "CAUTION",
}
BAD_QUARANTINE = {"alias_fuzzy", "suspect", "suspect_alias_fuzzy"}

STATE_FILE = LOCALDATA / "auto_tickets_state.json"

# ---- bucket P&L tripwire (2026-09-23, operator-directed, red-teamed) ----
# The firing tripwire only asks "is this rule still firing?" — never "is
# this door still paying?" This block grades every deployed bucket on its
# trailing settled leg outcomes and throttles the deployment door
# accordingly. Constants are policy-level and deliberately visible.
PNL_WINDOW_DAYS = 21       # trailing calendar-day window of settled legs
PNL_MIN_N = 20             # below this, no verdict — "INSUFFICIENT", doors open
PNL_Z_BENCH = -2.0         # design z on mean (hit - stated_prob) residual
PNL_DEMOTE_STREAK = 2      # consecutive daily BLEEDING verdicts -> half stake
PNL_BENCH_STREAK = 4       # consecutive daily BLEEDING verdicts -> door closed
PNL_BENCH_ENABLED = True   # master kill-switch for the enforcement half only
BUCKET_PNL_FILE = LOCALDATA / "auto_tickets_bucket_pnl.json"

# ---- shipped-slice selection ladder (2026-09-23, operator-directed) ----
# These are deliberately separate from the door-level PNL tripwire above:
# the ladder changes ordering/filtering only; stakes remain the door's job.
SLICE_WINDOW_DAYS = 35       # 28d leaves CAUTION at n=11; 35d reaches n=17
SLICE_MIN_N = 12              # evidence floor; below it the ladder fails open
SLICE_Z_BENCH = -2.0           # strict bleeding bar; unchanged from door z
SLICE_DEMOTE_STREAK = 2        # hysteresis: two qualifying days to demote
SLICE_BENCH_STREAK = 4         # hysteresis: four BLEEDING days to bench
SLICE_DEMOTE_ON_COLD = True    # soft first-cycle policy: COLD can demote
SLICE_BENCH_ON_BLEED = False   # conservative first cycle: no slice benches
SLICE_DEMOTE_CAP = {"CAUTION": 0.70}  # only studied bucket/band cap
SLICE_DEMOTE_SHRINK = 0.95     # generic rank-only fallback for other buckets
SLICE_ENABLED = True            # kill-switch: evidence still reports, policy identity
SLICE_LEDGER_FILENAME = "auto_tickets_slice_ledger.jsonl"
SLICE_TRIPWIRE_FILENAME = "auto_tickets_slice_tripwire.json"
SLICE_LEDGER_FILE = LOCALDATA / SLICE_LEDGER_FILENAME
SLICE_TRIPWIRE_FILE = LOCALDATA / SLICE_TRIPWIRE_FILENAME


def bucket_pnl_verdict(n, resid_mean, resid_var):
    """One bucket's evidence classification (PURE — trivially replayable).

    INSUFFICIENT: too few settled legs to judge (fail-open for data
    poverty; benches are EARNED by evidence, never by silence).
    BLEEDING: realized-vs-stated gap negative at design z <= PNL_Z_BENCH
    with n >= PNL_MIN_N. COLD: gap negative but not past the bench bar.
    PAYING otherwise.
    """
    if n < PNL_MIN_N or resid_var <= 0:
        return "INSUFFICIENT"
    z = resid_mean / math.sqrt(resid_var)
    if z <= PNL_Z_BENCH:
        return "BLEEDING"
    if resid_mean < 0:
        return "COLD"
    return "PAYING"


def compute_bucket_pnl(today_text, *, archives=None, settled=None, path=None):
    """Grade trailing settled legs per bucket, advance the BLEEDING streak,
    persist the report, and return per-bucket deployment weights.

    Streak semantics (red-team requirements baked in):
    * the streak advances at most once per CALENDAR DAY (same-day reruns
      recompute the report but cannot compound the streak — intraday
      pipeline runs must not be able to bench anything);
    * a BLEEDING verdict increments the streak, anything else resets it;
    * weight ladder: streak >= PNL_BENCH_STREAK -> 0.0 (door closed);
      streak >= PNL_DEMOTE_STREAK -> 0.5 (half stake); else 1.0.
    """
    path = path or BUCKET_PNL_FILE
    archives = load_archived_picks() if archives is None else archives
    settled = load_settled() if settled is None else settled
    day_from = (datetime.strptime(today_text, "%Y-%m-%d") - timedelta(days=PNL_WINDOW_DAYS)).strftime("%Y-%m-%d")
    stats: dict[str, dict] = {
        b: {"n": 0, "wins": 0, "stated": 0.0, "sse_var": 0.0, "profit": 0.0}
        for b in sorted(BUCKETS)
    }
    for row in archives:
        day = str(row.get("date") or row.get("_archive_day") or "")[:10]
        if not (day_from <= day <= today_text):
            continue
        for leg in playable_legs([row], day=day, settled=settled):
            res = leg.get("result")
            if res not in ("win", "loss"):
                continue   # void/ungraded legs are invisible to P&L, never auto-loss
            b = str((leg.get("row") or {}).get("bucket") or "")
            if b not in stats:
                continue
            p = float(leg.get("prob") or 0.0)
            if p <= 0.0:
                continue   # realized-vs-stated needs a stated rate; a missing
                           # one would fabricate a fake -1 residual per leg
            hit = 1.0 if res == "win" else 0.0
            st = stats[b]
            st["n"] += 1
            st["wins"] += hit
            st["stated"] += p
            st["sse_var"] += p * (1.0 - p)
            st["profit"] += (float(leg["odds"]) - 1.0) if hit else -1.0
    try:
        prev = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        prev = {}
    prev_eval = str(prev.get("last_eval") or "")
    prev_b = (prev.get("buckets") or {})
    verdicts: dict[str, dict] = {}
    for b, st in stats.items():
        n = st["n"]
        resid_mean = (st["wins"] - st["stated"]) / n if n else 0.0
        resid_var = st["sse_var"] / (n * n) if n else 0.0
        verdict = bucket_pnl_verdict(n, resid_mean, resid_var)
        n_streak = int((prev_b.get(b) or {}).get("streak") or 0)
        if prev_eval < today_text:      # at most one streak step per day
            n_streak = n_streak + 1 if verdict == "BLEEDING" else 0
        weight = (0.0 if n_streak >= PNL_BENCH_STREAK else
                  0.5 if n_streak >= PNL_DEMOTE_STREAK else 1.0)
        verdicts[b] = {
            "n": n,
            "hit": round(st["wins"] / n, 4) if n else None,
            "stated": round(st["stated"] / n, 4) if n else None,
            "gap": round(resid_mean, 4) if n else None,
            "roi_flat": round(st["profit"] / n, 4) if n else None,
            "z": round(resid_mean / math.sqrt(resid_var), 3) if resid_var > 0 and n else None,
            "verdict": verdict, "streak": n_streak, "weight": weight,
        }
    report = {
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "last_eval": today_text,
        "window_days": PNL_WINDOW_DAYS,
        "window_from": day_from,
        "min_n": PNL_MIN_N, "z_bench": PNL_Z_BENCH,
        "demote_streak": PNL_DEMOTE_STREAK, "bench_streak": PNL_BENCH_STREAK,
        "enabled": PNL_BENCH_ENABLED,
        "buckets": verdicts,
    }
    try:
        path.write_text(json.dumps(report, indent=2))
    except OSError:
        pass
    return ({b: v["weight"] for b, v in verdicts.items()} if PNL_BENCH_ENABLED
            else {}), verdicts


_SLICE_BUCKET_ORDER = tuple(sorted(BUCKETS))
_SLICE_ROW_FIELDS = ("date", "home", "away", "match", "pick", "prob_stated",
                     "odds", "bucket", "src", "seeded", "shadow")
_SLIP_LEG_RE = re.compile(
    r"^\s{3}(?P<match>.+?)\s+(?P<pick>[A-Za-z]+)\s+@\s+"
    r"(?P<odds>[0-9]+(?:\.[0-9]+)?)\s+\(stated\s+"
    r"(?P<prob>[0-9]+(?:\.[0-9]+)?)%\)"
)


def _slice_ledger_path(path=None):
    return Path(path) if path is not None else LOCALDATA / SLICE_LEDGER_FILENAME


def _slice_state_path(path=None):
    return Path(path) if path is not None else LOCALDATA / SLICE_TRIPWIRE_FILENAME


def _slice_day(value):
    return str(value or "")[:10]


def _slice_row_key(row):
    """Identity for ledger replacement/double-count prevention.

    The key deliberately follows the same structure-only fold as settlement
    and card dedup. Raw display spelling is evidence, not fixture identity.
    """
    return _folded_leg_key(_slice_day(row.get("date")), row.get("home"),
                           row.get("away"), row.get("pick"))


def _slice_clean_row(row):
    """Return exactly the frozen ledger schema; never persist a result."""
    out = {
        "date": _slice_day(row.get("date")),
        "home": str(row.get("home") or ""),
        "away": str(row.get("away") or ""),
        "match": str(row.get("match") or ""),
        "pick": str(row.get("pick") or "").upper(),
        "prob_stated": float(row.get("prob_stated") or 0.0),
        "odds": float(row.get("odds") or 0.0),
        "bucket": str(row.get("bucket") or ""),
        "src": str(row.get("src") or ""),
        "seeded": bool(row.get("seeded")),
        "shadow": bool(row.get("shadow")),
    }
    return out


def read_slice_ledger(path=None):
    """Read the result-free ledger. Settlement is intentionally not cached."""
    ledger = _slice_ledger_path(path)
    try:
        text = ledger.read_text(encoding="utf-8")
    except OSError:
        return []
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict) or "result" in row:
            continue
        if any(k not in row for k in _SLICE_ROW_FIELDS):
            continue
        rows.append(_slice_clean_row(row))
    return rows


def write_slice_ledger(rows, path=None):
    """Write one canonical JSON object per line, with no score/result field."""
    ledger = _slice_ledger_path(path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    clean = [_slice_clean_row(row) for row in rows]
    with ledger.open("w", encoding="utf-8") as fh:
        for row in clean:
            fh.write(json.dumps(row, separators=(",", ":"), ensure_ascii=False)
                     + "\n")


def upsert_slice_day(rows, target, path=None, *, allow_empty=False):
    """Replace all real and shadow rows for one date, atomically by rewrite.

    An empty replacement set is normally a NO-OP, not a clear (2026-09-23
    review fix). Callers reach this with nothing to record for two very
    different reasons: a force-repick that genuinely ships no card, and a
    slip that failed to parse (unreadable file, or a leg line that no longer
    matches the frozen print format). Treating both as "this day shipped
    nothing" let a rerun between shipping and freezing delete the day's only
    printed-probability evidence — permanently, since ``ensure_slice_seeded``
    only seeds when the whole ledger is absent. A clear is therefore opt-in
    via ``allow_empty``, and the callers pass it only when no slip exists for
    the date at all.
    """
    target = _slice_day(target)
    ledger = read_slice_ledger(path)
    fresh = [_slice_clean_row(r) for r in rows
             if _slice_day(r.get("date")) == target]
    if not fresh and not allow_empty:
        return [r for r in ledger if _slice_day(r.get("date")) == target]
    existing = [r for r in ledger if _slice_day(r.get("date")) != target]
    merged = existing + fresh
    # Preserve first position while allowing a later real row to replace a
    # same-key shadow row. The caller orders real rows before shadow rows.
    out, positions = [], {}
    for row in merged:
        key = _slice_row_key(row)
        if key in positions:
            out[positions[key]] = row
        else:
            positions[key] = len(out)
            out.append(row)
    write_slice_ledger(out, path)
    return out


def _printed_prob_value(prob):
    """Probability represented by the frozen ``.0%`` slip print."""
    return float(f"{float(prob):.0%}".rstrip("%")) / 100.0


def _archive_index_for_slice(archives):
    """Identity-fold archive join; highest (avg_p, odds) wins a twin."""
    index = {}
    for row in archives:
        day = _slice_day(row.get("date") or row.get("_archive_day"))
        if not day:
            continue
        key = _folded_leg_key(day, row.get("home"), row.get("away"),
                              row.get("pick"))
        try:
            score = (float(row.get("avg_p") or 0.0),
                     float(row.get("odds") or 0.0))
        except (TypeError, ValueError):
            score = (0.0, 0.0)
        prior = index.get(key)
        if prior is None or score > prior[0]:
            index[key] = (score, row)
    return {key: row for key, (_score, row) in index.items()}


def _slice_row_from_archive(day, printed_match, pick, prob, odds, archive_row,
                            *, src="slip", seeded=False, shadow=False):
    home = str(archive_row.get("home") or printed_match.split(" vs ", 1)[0])
    away = str(archive_row.get("away") or printed_match.split(" vs ", 1)[-1])
    return {
        "date": day, "home": home, "away": away,
        "match": f"{home} vs {away}", "pick": str(pick).upper(),
        "prob_stated": float(prob), "odds": float(odds),
        "bucket": str(archive_row.get("bucket") or ""), "src": src,
        "seeded": bool(seeded), "shadow": bool(shadow),
    }


def parse_slip_slice_rows(slip_path, archive_index):
    """Parse frozen evidence and resolve bucket/result identity separately."""
    # The filename is auto_tickets_YYYY-MM-DD.txt; avoid trusting a line's
    # display date because the leg line itself intentionally has no date.
    name_match = re.search(r"(\d{4}-\d{2}-\d{2})", Path(slip_path).name)
    day = name_match.group(1) if name_match else ""
    rows, unresolved = [], []
    try:
        lines = Path(slip_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return rows, unresolved
    for line_no, line in enumerate(lines, 1):
        m = _SLIP_LEG_RE.match(line)
        if not m:
            continue
        printed_match = m.group("match").strip()
        parts = printed_match.split(" vs ", 1)
        if len(parts) != 2:
            unresolved.append({"file": str(slip_path), "line": line_no,
                               "match": printed_match})
            continue
        home, away = parts
        pick = m.group("pick").upper()
        key = _folded_leg_key(day, home, away, pick)
        archive_row = archive_index.get(key)
        if archive_row is None:
            unresolved.append({"file": str(slip_path), "line": line_no,
                               "match": printed_match, "pick": pick})
            continue
        rows.append(_slice_row_from_archive(
            day, printed_match, pick, float(m.group("prob")) / 100.0,
            float(m.group("odds")), archive_row,
        ))
    return rows, unresolved


def _replay_seed_rows(archives, settled, real_keys):
    """Rebuild the pre-slip seed through today's planner, not a new selector."""
    rows = []
    days = sorted({_slice_day(p.get("date") or p.get("_archive_day"))
                   for p in archives})
    for day in days:
        if not ("2026-06-25" <= day <= "2026-08-26"):
            continue
        pool = playable_legs(archives, day=day, settled=settled, floor=0.0)
        # This is the replay harness's settled-universe convention: unresolved
        # and void rows are not wager legs in the growth reconstruction.
        pool = [leg for leg in pool if leg.get("result")]
        if len(pool) < LEGS_PER_ACCA:
            continue
        plan = plan_day(pool, 100.0)
        pool_by_key = {_leg_key(leg): leg for leg in pool}
        for acca in plan:
            for leg in acca.get("legs", []):
                source = pool_by_key.get(_leg_key(leg))
                if source is None:
                    continue
                row = source.get("row") or {}
                item = _slice_row_from_archive(
                    day, leg.get("match") or "", leg.get("pick"),
                    float(leg.get("prob") or 0.0), float(leg.get("odds") or 0.0), row,
                    src="replay", seeded=True,
                )
                if _slice_row_key(item) in real_keys:
                    continue
                rows.append(item)
    return rows


def seed_slice_ledger(*, archives=None, settled=None, path=None,
                      localdata=None, today_text=None):
    """Create the deterministic replay+slip seed and return rows/unresolved.

    Real rows use only frozen slip probabilities. Replay rows use current
    ``avg_p`` through the live planner and are explicitly marked as a proxy.
    """
    archives = load_archived_picks() if archives is None else archives
    settled = load_settled() if settled is None else settled
    data_dir = LOCALDATA if localdata is None else Path(localdata)
    archive_index = _archive_index_for_slice(archives)
    real_rows, unresolved = [], []
    for slip in sorted(data_dir.glob("auto_tickets_*.txt")):
        day_match = re.search(r"(\d{4}-\d{2}-\d{2})", slip.name)
        if not day_match:
            continue
        day = day_match.group(1)
        if not ("2026-08-27" <= day <= (today_text or "9999-12-31")):
            continue
        rows, missing = parse_slip_slice_rows(slip, archive_index)
        real_rows.extend(rows)
        unresolved.extend(missing)
    real_keys = {_slice_row_key(row) for row in real_rows}
    replay_rows = _replay_seed_rows(archives, settled, real_keys)
    rows = sorted(replay_rows + real_rows,
                  key=lambda r: (_slice_day(r["date"]), r["src"],
                                 r["home"], r["away"], r["pick"]))
    if path is not None or not _slice_ledger_path().exists():
        write_slice_ledger(rows, path)
    return rows, unresolved


def ensure_slice_seeded(today_text):
    """Seed only when the result-free ledger is absent/empty."""
    path = _slice_ledger_path()
    if read_slice_ledger(path):
        return read_slice_ledger(path), []
    return seed_slice_ledger(today_text=today_text, path=path)


def _slice_verdict(n, gap, sse):
    if n < SLICE_MIN_N or sse <= 0.0:
        return "INSUFFICIENT"
    z = gap / (math.sqrt(sse) / n)
    if z <= SLICE_Z_BENCH:
        return "BLEEDING"
    if gap < 0.0:
        return "COLD"
    return "PAYING"


def _slice_action(bucket, verdict, demote_streak, bench_streak):
    benched = (SLICE_BENCH_ON_BLEED
               and bench_streak >= SLICE_BENCH_STREAK
               and verdict == "BLEEDING")
    demoted = demote_streak >= SLICE_DEMOTE_STREAK
    if benched:
        return "BENCHED"
    if demoted:
        return "DEMOTED"
    return "FULL"


def _slice_rank_caps(verdicts):
    caps, benches = {}, set()
    if not SLICE_ENABLED:
        return caps, benches
    for bucket, verdict in verdicts.items():
        if verdict.get("action") == "BENCHED":
            benches.add(bucket)
        elif verdict.get("action") == "DEMOTED":
            if bucket in SLICE_DEMOTE_CAP:
                caps[bucket] = float(SLICE_DEMOTE_CAP[bucket])
            else:
                caps[bucket] = {"shrink": float(SLICE_DEMOTE_SHRINK)}
    return caps, benches


def compute_bucket_slice(today_text, *, path=None, state_path=None,
                         settled=None):
    """Score the result-free shipped-slice ledger and advance ladder state.

    The return value is ``(policy, verdicts)``. ``policy`` contains
    ``rank_caps`` and ``bench_buckets`` for the current plan. Every score is
    read through ``pick_result`` at call time, so settlement lag and voids are
    handled exactly like the door tripwire.

    Enforcement basis (2026-09-23 review fix): the verdict that drives
    demotion/benching is computed ONLY from printed-slip evidence, i.e. rows
    whose ``prob_stated`` was read off a frozen slip line. The seeded replay
    rows carry ``prob_stated`` from the mutable archive ``avg_p`` — which the
    addendum measured as differing from the printed probability by more than
    0.55pp on 44/134 slips — so they are two different estimands and are
    reported as context (``n_seeded``/``seed_gap``) instead of being pooled
    into the verdict. Pooling them flipped CAUTION's in-window gap from
    -3.9pp to +8.0pp, and because ``SLICE_MIN_N`` exceeds the shipped-only n
    it was the replay half that could ever have convicted a bucket. Shadow
    rows remain in the enforcement basis on purpose: a demoted or benched
    bucket keeps no shipped legs, and counterfactual evidence is the only
    route back to FULL.
    """
    today_text = _slice_day(today_text)
    settled = load_settled() if settled is None else settled
    # Match the existing rolling-tripwire convention: a ``35d`` window is
    # the 35 preceding calendar days plus the evaluation day (the same
    # inclusive endpoint convention used by compute_bucket_pnl).
    day_from = (datetime.strptime(today_text, "%Y-%m-%d")
                - timedelta(days=SLICE_WINDOW_DAYS + 1)).strftime("%Y-%m-%d")
    # Two ledgers of record inside one pass: ``stats`` is the enforcement
    # basis (printed-slip probabilities only) and ``seed_stats`` is the
    # replay-proxy context, which can never move a verdict.
    def _blank_stats():
        return {"n": 0, "wins": 0, "stated": 0.0, "sse": 0.0, "profit": 0.0}

    stats = {b: _blank_stats() for b in _SLICE_BUCKET_ORDER}
    seed_stats = {b: _blank_stats() for b in _SLICE_BUCKET_ORDER}
    for row in read_slice_ledger(path):
        day = _slice_day(row.get("date"))
        if not (day_from <= day <= today_text):
            continue
        try:
            prob = float(row.get("prob_stated") or 0.0)
        except (TypeError, ValueError):
            continue
        if prob <= 0.0:
            continue
        result = pick_result({"date": day, "home": row.get("home"),
                              "away": row.get("away"),
                              "pick": row.get("pick")}, settled)
        if result not in ("win", "loss"):
            continue
        bucket = str(row.get("bucket") or "")
        if bucket not in stats:
            continue
        st = seed_stats[bucket] if row.get("seeded") else stats[bucket]
        hit = 1.0 if result == "win" else 0.0
        st["n"] += 1
        st["wins"] += hit
        st["stated"] += prob
        st["sse"] += prob * (1.0 - prob)
        try:
            odds = float(row.get("odds") or 0.0)
        except (TypeError, ValueError):
            odds = 0.0
        st["profit"] += (odds - 1.0) if hit else -1.0

    state_file = _slice_state_path(state_path)
    try:
        prior = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        prior = {}
    prior_eval = _slice_day(prior.get("last_eval"))
    prior_buckets = prior.get("buckets") or {}
    verdicts = {}
    for bucket in _SLICE_BUCKET_ORDER:
        st = stats[bucket]
        sd = seed_stats[bucket]
        n = st["n"]
        gap = (st["wins"] - st["stated"]) / n if n else 0.0
        z = gap / (math.sqrt(st["sse"]) / n) if n and st["sse"] > 0 else None
        verdict = _slice_verdict(n, gap, st["sse"])
        seed_gap = (sd["wins"] - sd["stated"]) / sd["n"] if sd["n"] else None
        old = prior_buckets.get(bucket) or {}
        demote = max(0, int(old.get("demote_streak") or old.get("streak") or 0))
        bench = max(0, int(old.get("bench_streak") or 0))
        if prior_eval < today_text:
            demote_delta = (verdict in ("COLD", "BLEEDING")
                            if SLICE_DEMOTE_ON_COLD else verdict == "BLEEDING")
            demote = max(0, demote + (1 if demote_delta else -1))
            bench = max(0, bench + (1 if verdict == "BLEEDING" else -1))
        action = (_slice_action(bucket, verdict, demote, bench)
                  if SLICE_ENABLED else "FULL")
        verdicts[bucket] = {
            "n": n,
            # Enforcement basis vs replay-proxy context, kept side by side so
            # the two estimands stay visible in every artifact.
            "n_shipped": n,
            "n_seeded": sd["n"],
            "n_all": n + sd["n"],
            "seed_gap": round(seed_gap, 4) if seed_gap is not None else None,
            "seed_roi_flat": (round(sd["profit"] / sd["n"], 4)
                              if sd["n"] else None),
            "hit": round(st["wins"] / n, 4) if n else None,
            "stated": round(st["stated"] / n, 4) if n else None,
            "gap": round(gap, 4) if n else None,
            "z": round(z, 3) if z is not None else None,
            "roi_flat": round(st["profit"] / n, 4) if n else None,
            "verdict": verdict,
            "demote_streak": demote,
            "bench_streak": bench,
            "streak": demote,
            "action": action,
            "rank_cap": (float(SLICE_DEMOTE_CAP[bucket])
                          if action == "DEMOTED" and bucket in SLICE_DEMOTE_CAP
                          else None),
        }
    rank_caps, bench_buckets = _slice_rank_caps(verdicts)
    report = {
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "last_eval": today_text,
        "window_days": SLICE_WINDOW_DAYS,
        "window_from": day_from,
        "min_n": SLICE_MIN_N,
        "z_bench": SLICE_Z_BENCH,
        "demote_streak": SLICE_DEMOTE_STREAK,
        "bench_streak": SLICE_BENCH_STREAK,
        "demote_on_cold": SLICE_DEMOTE_ON_COLD,
        "bench_on_bleed": SLICE_BENCH_ON_BLEED,
        "demote_cap": SLICE_DEMOTE_CAP,
        "demote_shrink": SLICE_DEMOTE_SHRINK,
        "enabled": SLICE_ENABLED,
        "evidence_basis": "printed-slip only; seeded replay rows are context",
        "buckets": verdicts,
    }
    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    except OSError:
        pass
    return ({"rank_caps": rank_caps,
             "bench_buckets": tuple(sorted(bench_buckets)),
             "enabled": SLICE_ENABLED}, verdicts)


def _slice_table_lines(verdicts):
    header = ("  bucket                                      n       gap       "
              "z verdict demote bench action")
    lines = [(f"SELECTION LADDER SLICE (trailing {SLICE_WINDOW_DAYS}d, "
              "printed-slip evidence only):"),
             header]
    for bucket in _SLICE_BUCKET_ORDER:
        v = verdicts[bucket]
        gap = "—" if v["gap"] is None else f"{v['gap']:+.1%}"
        z = "—" if v["z"] is None else f"{v['z']:+.2f}"
        seed = v.get("seed_gap")
        seed_note = (f"  | replay ctx (excluded): n={v['n_seeded']} "
                     f"gap={seed:+.1%}" if v.get("n_seeded") and seed is not None
                     else "  | replay ctx (excluded): none")
        lines.append(f"  {bucket:38s} {v['n']:3d} {gap:>9s} {z:>8s} "
                     f"{v['verdict']:11s} {v['demote_streak']:6d} "
                     f"{v['bench_streak']:5d} {v['action']}{seed_note}")
    return lines


def _slice_action_lines(verdicts):
    lines = []
    for bucket in _SLICE_BUCKET_ORDER:
        v = verdicts[bucket]
        if v["action"] == "FULL":
            continue
        if v["action"] == "DEMOTED":
            detail = (f"rank cap {v['rank_cap']:.2f}"
                      if v.get("rank_cap") is not None
                      else f"rank shrink x{SLICE_DEMOTE_SHRINK:.2f}")
        else:
            detail = "door bench"
        lines.append(
            f"SELECTION LADDER: {bucket} {v['action'].lower()} | {detail} | "
            f"slice streak {v['demote_streak']} | verdict {v['verdict']} | n {v['n']}"
        )
    return lines


def _slice_plan_rows(target, plan, pool_by_key, *, shadow=False):
    rows = []
    for acca in plan:
        for leg in acca.get("legs", []):
            source = pool_by_key.get(_leg_key(leg))
            if source is None:
                continue
            source_row = source.get("row") or {}
            home = str(source_row.get("home") or "")
            away = str(source_row.get("away") or "")
            rows.append({
                "date": _slice_day(target),
                "home": home, "away": away,
                "match": f"{home} vs {away}",
                "pick": str(leg.get("pick") or "").upper(),
                "prob_stated": _printed_prob_value(leg.get("prob") or 0.0),
                "odds": float(leg.get("odds") or 0.0),
                "bucket": str(source_row.get("bucket") or ""),
                "src": "slip", "seeded": False, "shadow": bool(shadow),
            })
    return rows


def _slice_shadow_rows(target, pure_plan, pool_by_key, real_keys,
                       diminished_buckets):
    rows = _slice_plan_rows(target, pure_plan, pool_by_key, shadow=True)
    return [row for row in rows
            if row["bucket"] in diminished_buckets
            and _slice_row_key(row) not in real_keys]


def wilson_lb(wins, n, z=1.645):
    if n == 0:
        return 0.0
    p = wins / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
    return max(0.0, (centre - half) / denom)


def parse_kickoff(pick):
    """SETTLEMENT parser + dated-row comparison for the live guard. NOT a bet-time proof.

    Used for settlement bookkeeping (void-age) and by the LIVE kickoff guard
    to compare rows whose kickoff carries a full calendar date: the feeds
    render dated kickoffs on a UTC+2 clock (== Africa/Johannesburg), and the
    guard drops legs already started at build time. It defaults naive
    timestamps to Africa/Johannesburg and therefore must NEVER be used as a
    zone *proof* — a bare time-only kickoff ("22:30", the incident-#6 class)
    has no date, and no zone may be assumed for it. Proven-instant logic
    lives in `parse_kickoff_proven` (audit contract only)."""
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


def kickoff_has_usable_date(pick) -> bool:
    """Does the row's kickoff carry a usable calendar date at all?

    True for a full ISO/naive date ("2026-09-06T20:15:00+02:00",
    "2026-09-06 15:30:00"). A yearless day-month listing ("05-09, 22:30")
    also counts as dated for parsing purposes — its region trust is decided
    separately (see kickoff_clock_region_is_remote). False for bare clock
    times ("22:30"), missing kickoffs and garbage.
    """
    raw = str(pick.get("kickoff_canonical") or pick.get("kickoff") or "").strip()
    if not raw:
        return False
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}", raw)
                or re.match(r"^\d{1,2}-\d{1,2},\s*\d{1,2}:\d{2}", raw))


# Clock-only kickoff rows (bare "HH:MM", yearless "DD-MM, HH:MM") carry no
# date/zone of their own: the engine reads the clock on the slate day in
# SAST. That reading is trustworthy only when the league's local clock is
# close to SAST. This list is NOT a kickoff-time computation — it only
# answers "is the SAST rendering of this clock safe to trust?" and a wrong
# answer drops a leg that could have been bet (harmless direction), it can
# never fabricate a wrong kickoff instant. Scope: Americas (clocks 4-11h
# west of SAST; a bare evening clock read on the slate day is the incident
# #6 failure, e.g. 22:30 EDT = 04:30 SAST next day) and Asia-Pacific (clocks
# 5-9h east of SAST; a bare evening clock reads up to 9h late). Europe /
# Africa clocks sit within ~1-2h of SAST and are trusted. The 2026-09-06
# region audit: 8 of 47 historical bare ridden legs were in this class and
# carry every historical near-miss (Suwon 08-07, Bolivar 08-12, Deportivo
# Moron 08-15, Broadmeadow 08-16, Penarol 08-16, Seattle 08-20, Sporting KC
# 08-30, Toluca 08-31 — plus Vancouver 09-06 itself).
_REMOTE_CLOCK_REGION_HINTS = (
    # Americas
    "usa", "united states", "mls", "major league soccer", "canada",
    "mexico", "liga mx", "honduras", "costa rica", "guatemala",
    "el salvador", "panama", "nicaragua", "peru", "colombia", "ecuador",
    "bolivia", "paraguay", "uruguay", "chile", "argentina", "brazil",
    "venezuela", "sudamericana", "libertadores",
    # Asia-Pacific
    "japan", "j-league", "south korea", "korea", "k-league", "china",
    "australia", "new zealand", "thailand", "vietnam", "indonesia",
    "malaysia", "philippines", "singapore", "india", "hong kong", "taiwan",
)


def kickoff_clock_region_is_remote(pick) -> bool:
    """Is this row's league region one whose local clock is far from SAST?

    Boolean only — it never computes or infers a kickoff time. Region text
    comes from the row's own league fields (league / league_raw /
    odds_league, incl. ctx). International cup strings (Champions League,
    friendlies, ...) without a region signal return False (kept; their bare
    clocks have only ~1-2h class error and the audit command lists every
    kept clock-only row for review).
    """
    vals = [pick.get("league"), pick.get("league_raw"), pick.get("odds_league")]
    ctx = pick.get("ctx") or {}
    vals += [ctx.get("league"), ctx.get("league_raw")]
    text = " ".join(str(v or "") for v in vals).lower()
    return any(hint in text for hint in _REMOTE_CLOCK_REGION_HINTS)


def _kickoff_is_clock_only(raw: str) -> bool:
    """bare 'HH:MM' or yearless day-month 'DD-MM, HH:MM' — no year, no zone."""
    return bool(re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", raw)
                or re.match(r"^\d{1,2}-\d{1,2},\s*\d{1,2}:\d{2}", raw))


_ZONED_ISO_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{1,2}:\d{2}(:\d{2}(\.\d+)?)?\s*(Z|[+-]\d{2}:?\d{2})$"
)


def _zoned_instant_utc(value) -> datetime | None:
    """UTC datetime from an EXPLICIT zone-bearing ISO string (offset or Z).

    None for anything naive or unparseable — a naive rendering names no zone,
    and defaulting one to Africa/Johannesburg is the incident-#6 fault class.
    """
    raw = str(value or "").strip()
    if not raw or not _ZONED_ISO_RE.match(raw):
        return None
    text = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    # tolerate "+0200" (no colon) if a source ever emits it
    text = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", text)
    if "+" not in text and "-" not in text[10:]:
        return None
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(_UTC)


def kickoff_utc_from_archived_row(row) -> tuple[str | None, str | None]:
    """Reconstruct what ingest normalisation WOULD have emitted for an
    ARCHIVED row (replay/audit only — picks_today.py emits the real fields
    live). Returns ``(kickoff_utc_iso, source)`` or ``(None, None)``.

    Two and only two archive-preserved witnesses are accepted:
      - the row's own kickoff string is a zoned ISO instant
        (source "offset_passthrough"); or
      - the row's price came from the scoutingstats feed and its
        odds_captured_at is a zoned ISO instant. The scoutingstats odds
        adapter has NO capture timestamp: it stores the fixture's starting_at
        kickoff string INTO captured_at (picks_today._scoutingstats_rows_to_odds
        sets captured_at = row kickoff), so for this one provider the archived
        odds_captured_at IS the odds row's kickoff — the same string ingest
        normalisation sees in data["scoutingstats"] at fetch time (source
        "derived_odds_row").

    Anything else is NOT resolved here: bzzoiro / betexplorer / theoddsapi
    odds_captured_at values are true capture timestamps (never kickoffs), and
    sibling prediction rows (vitibet "+02:00", bzzoiro event_date) are not
    archived — their witness existed only in the fetch-time data dict, so the
    live normalisation rescues those legs but history cannot replay them.
    """
    raw = str(row.get("kickoff_canonical") or row.get("kickoff") or "").strip()
    if raw:
        dt = _zoned_instant_utc(raw)
        if dt is not None:
            return dt.isoformat(), "offset_passthrough"
    if str(row.get("odds_source") or "") == "scoutingstats_odds":
        captured = str(row.get("odds_captured_at") or "").strip()
        if captured:
            dt = _zoned_instant_utc(captured)
            if dt is not None:
                return dt.isoformat(), "derived_odds_row"
    return None, None


def live_kickoff_guard(pool, now):
    """The LIVE kickoff guard (incident #6 fix; region-narrowed after the
    2026-09-06 round-2 audit, then keyed to ingest normalisation in Task A).

    0. A row carrying a resolved ``kickoff_utc`` (emitted by picks_today's
       ingest normalisation from an explicit zone-bearing witness) is judged
       ONLY on that absolute instant: already at/past build time -> drop as
       started; still ahead -> ride. No region guess is needed for it.
    Then, for rows normalisation could NOT resolve:
    1. Drops legs with a missing/garbage kickoff.
    2. Drops CLOCK-ONLY kickoffs (bare "HH:MM", yearless "DD-MM, HH:MM")
       whose league region's clock is far from SAST (Americas / Asia-
       Pacific): a bare "22:30" MLS clock read on the slate day is the
       Vancouver incident class. Clock-only rows from Europe/Africa ride
       (their clocks are within ~1-2h of SAST).
    3. Drops dated legs already at/past build time (dated rows compared on
       the feeds' UTC+2 rendering via parse_kickoff).

    Returns ``(kept_legs, drops)`` where drops maps reason -> fixture names.
    The region list NEVER computes a kickoff — a mis-hit drops a bettable
    leg (harmless), it cannot fabricate a wrong time. This is deliberately
    NOT the fail-closed proof standard — that lives in ``kickoff_contract``
    as the off-by-default audit instrument.
    """
    drops: dict[str, list[str]] = {}
    rideable, kept = [], []
    for leg in pool:
        pick = leg.get("row") if isinstance(leg, dict) and leg.get("row") else leg
        ku = _zoned_instant_utc(pick.get("kickoff_utc"))
        if ku is not None:
            if ku.astimezone(TZ) < now.astimezone(TZ):
                drops.setdefault(KO_SKIP_STARTED, []).append(leg["match"])
            else:
                kept.append(leg)
            continue
        raw = str(pick.get("kickoff_canonical") or pick.get("kickoff") or "").strip()
        if not raw or (not kickoff_has_usable_date(pick) and not _kickoff_is_clock_only(raw)):
            drops.setdefault(KO_SKIP_NO_DATE, []).append(leg["match"])
            continue
        if _kickoff_is_clock_only(raw) and kickoff_clock_region_is_remote(pick):
            drops.setdefault(KO_SKIP_REMOTE_CLOCK, []).append(leg["match"])
            continue
        rideable.append(leg)
    started = []
    for leg in rideable:
        pick = leg.get("row") if isinstance(leg, dict) and leg.get("row") else leg
        kt = parse_kickoff(pick)
        if kt is not None and kt.astimezone(TZ) < now.astimezone(TZ):
            started.append(leg)
        else:
            kept.append(leg)
    if started:
        drops[KO_SKIP_STARTED] = [l["match"] for l in started]
    return kept, drops


def parse_kickoff_proven(pick) -> datetime | None:
    """A kickoff PROVEN by the row itself, as UTC — or None. Never infers.

    Accepts, in order:
      - ``pick["kickoff_utc"]`` — an absolute instant that ingest
        normalisation emitted from an explicit zone-bearing witness
        (the pick's own offset/Z string, or a same-fixture source row that
        declared one; provenance is recorded in ``kickoff_source`` /
        ``kickoff_witness``, so the proof is reproducible from the row);
      - an ISO instant with an explicit offset or Z in the kickoff itself
        ("2026-09-06T20:15:00+02:00" is 20:15 SAST; "…T02:30:00Z" is
        02:30 UTC); or
      - a naive datetime that ALSO names a timezone as data in the row
        (`pick["kickoff_tz"]`, an IANA zone such as "America/Vancouver").

    Naive timestamps without an explicit zone return None: the source's zone
    is not known, and the old default of stamping Africa/Johannesburg is
    precisely the fault that let a 04:30 SAST kickoff look like 22:30 SAST.
    A zone that belongs to a stadium/league belongs in the data — never in a
    hand-maintained league-substring table. `parse_kickoff` (SAST-defaulting)
    exists for settlement bookkeeping only and is unusable for this proof.
    """
    ku = str(pick.get("kickoff_utc") or "").strip()
    if ku:
        dt = _zoned_instant_utc(ku)
        if dt is not None:
            return dt
    raw = str(pick.get("kickoff_canonical") or pick.get("kickoff") or "").strip()
    if not raw:
        return None
    text = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        # Naive. Provable only when (a) the string names a full calendar date
        # and (b) the row carries its own timezone. No assumptions otherwise.
        if not re.match(r"^\d{4}-\d{2}-\d{2}[T ]\d{1,2}:\d{2}", text):
            return None
        zname = str(pick.get("kickoff_tz") or "").strip()
        if not zname:
            return None
        try:
            dt = dt.replace(tzinfo=ZoneInfo(zname))
        except Exception:
            return None
    return dt.astimezone(_UTC)


def kickoff_contract(pool, build_at, *, min_lead_hours=None):
    """AUDIT-ONLY fail-closed kickoff standard (incident #6); NOT the live rule.

    Used by ``replay_harness.py --kickoff-contract`` to measure how much of
    history could NOT prove its kickoffs (the data-side fix's size). A leg
    rides only if its kickoff can be PROVEN (an absolute instant
    carried by the row) to be at least ``min_lead_hours`` (default
    KICKOFF_MIN_LEAD_HOURS) after ``build_at``. Cannot prove it -> the leg is
    dropped and counted, with up to three fixture names per reason.

    Returns ``(kept_legs, census)`` where census maps reason -> fixture list.
    No league dict, no substring lookup, no defaulted timezone anywhere.
    The LIVE path uses ``live_kickoff_guard`` instead — deliberately weaker
    in exactly the way the 2026-09-06 review demanded (dated rows ride on
    the feeds' UTC+2 rendering; only undatable and already-started legs
    drop).
    """
    min_lead = KICKOFF_MIN_LEAD_HOURS if min_lead_hours is None else float(min_lead_hours)
    build_utc = build_at.astimezone(_UTC)
    kept, dropped = [], {}
    for leg in pool:
        pick = leg.get("row") if isinstance(leg, dict) and leg.get("row") else leg
        kt = parse_kickoff_proven(pick)
        if kt is None:
            dropped.setdefault(KO_SKIP_UNPROVEN, []).append(leg["match"])
            continue
        lead_h = (kt - build_utc).total_seconds() / 3600.0
        if lead_h < min_lead:
            dropped.setdefault(KO_SKIP_TOO_CLOSE, []).append(
                f"{leg['match']} (proven {kt.astimezone(TZ).strftime('%Y-%m-%d %H:%M %Z')})")
            continue
        kept.append(leg)
    return kept, dropped


def canonical_build_instant(day: str) -> datetime:
    """The archive's canonical bet-build instant for a date: FREEZE_HOUR:00
    SAST — the ~09:0x cron freeze run that produced each day's final slip.
    History is evaluated at ONE well-defined instant (parity snapshot and
    strict-contract replays), never at cron jitter.
    """
    base = datetime.strptime(str(day)[:10], "%Y-%m-%d")
    return base.replace(hour=FREEZE_HOUR, minute=0, second=0, microsecond=0, tzinfo=TZ)


def format_skip_census(total_in, kept, census, *, title="KICKOFF GUARD") -> list[str]:
    """One printed block per run: how many legs were dropped from the build
    pool, and why (the live guard's skip census; the audit contract passes
    its own title)."""
    n_dropped = sum(len(v) for v in census.values())
    out = [f"{title} — {kept}/{total_in} qualifying legs kept; "
           f"{n_dropped} dropped:"]
    for reason in sorted(census):
        names = census[reason]
        more = f" (+{len(names) - 3} more)" if len(names) > 3 else ""
        shown = ", ".join(names[:3])
        out.append(f"  • {len(names)} {reason.lower()}: {shown}{more}")
    if not census:
        out.append("  • none — every qualifying leg carries a provable kickoff.")
    return out


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


_ALIAS_INDEX = None


def _alias_index() -> dict:
    """Curated team-name aliases, normalised into norm_team key space.

    Data, not fuzz: a wrong entry can only fail to find a result, never
    silently change one, because the exact lookup in pick_result runs first
    and this is consulted only after it returns None. Edit
    localdata/team_aliases.json to add a group.
    """
    global _ALIAS_INDEX
    if _ALIAS_INDEX is None:
        from edgefactory.util import norm_team
        try:
            groups = json.loads((LOCALDATA / "team_aliases.json").read_text())
        except Exception:
            groups = []
        idx: dict = {}
        for g in groups:
            keys = {norm_team(str(n)) for n in g if str(n).strip()}
            keys.discard("")
            for k in keys:
                idx.setdefault(k, set()).update(keys)
        _ALIAS_INDEX = idx
    return _ALIAS_INDEX


def _alias_variants(key: str) -> set:
    return set(_alias_index().get(key, ())) | {key}


def _lookup_fallback(settled, day, home, away):
    from datetime import timedelta as _td
    from difflib import SequenceMatcher
    try:
        base = datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError:
        return None
    cands = {str(base + _td(days=o))
             for o in range(-RESCHEDULE_WINDOW_DAYS, RESCHEDULE_WINDOW_DAYS + 1)}
    # Curated aliases before fuzzy: "Hearts" and "Heart of Midlothian" score
    # ~0.44 on SequenceMatcher and never clear the 0.8 bar (2026-09-06: a
    # winning acca sat unresolved and was 5 days from auto-voiding).
    hv, av = _alias_variants(home), _alias_variants(away)
    if len(hv) > 1 or len(av) > 1:
        for d in sorted(cands):
            for h2 in hv:
                for a2 in av:
                    oc = settled.get((d, h2, a2))
                    if oc is not None:
                        return oc
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


def effective_bank(st, exclude_date=None) -> float:
    """Bank minus committed (open) stakes — in % of capital.

    `exclude_date`: when sizing a date's own slip, that date's existing
    entry must NOT count as committed capital — upsert_slip deletes and
    replaces it (Task E, 2026-09-06: a force-repick counted its own morning
    draft as live money and converged to bank/4 instead of bank/3). Stakes
    on OTHER dates stay committed: they are genuinely live and settlement
    has not yet returned them.
    """
    committed = 0.0
    for s in st.get("open_slips", []):
        if exclude_date is not None and str(s.get("date") or "")[:10] == str(exclude_date)[:10]:
            continue
        committed += s.get("staked_pct", 0.0)
    return st["bank"] - committed


def take_profit_target(st) -> float:
    return st["cycle_base"] * (1.0 + TAKE_PROFIT_GAIN)


# ---------------- selection / planning ----------------
def playable_legs(rows, day=None, settled=None, floor=None):
    """Playable, priced legs — the NO-FILTER set (validated).

    `floor` overrides MIN_LEG_ODDS (replay harness only — live callers pass
    nothing so the validated floor applies). Never inline the number: the
    2026-09-04 audit found the harness had to regex-strip a hardcoded floor
    out of this function's source, which silently made lower-floor A/Bs
    no-ops. One constant, one code path.
    """
    floor = MIN_LEG_ODDS if floor is None else floor
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
        # Min leg odds floor (2026-09-02: Bayern @1.05 rode slot 1 pre-freeze).
        # Sub-1.10 legs cap their acca's payout below the recipe's economics:
        # the pairing math needs avg ~1.4+ per leg; a 1.05 leg makes slot 1
        # the worst-paying ticket by construction. Value lives in MIN_LEG_ODDS.
        if odds < floor:
            continue
        res = pick_result(p, settled) if settled is not None else None
        out.append({"match": f"{p.get('home')} vs {p.get('away')}",
                    "pick": str(p.get("pick") or "").upper(),
                    "prob": float(ap) / 100.0, "odds": odds,
                    "result": res, "row": p})
    out.sort(key=lambda l: (l["prob"], l["odds"]), reverse=True)
    return out


def _rule_of(leg):
    """The miner rule behind a leg, when the archived row is still attached."""
    return str((leg.get("row") or {}).get("rule") or "")


def _rank_capped_probability(leg, rank_caps):
    """Effective ordering probability for the selection ladder.

    Numeric values are hard caps (the studied CAUTION 0.70 cap). A mapping
    ``{"shrink": factor}`` is the generic rank-only fallback for a bucket
    without a studied cap. The raw probability remains the first tiebreaker,
    so a cap never changes the printed evidence or score.
    """
    raw = float(leg["prob"])
    bucket = str((leg.get("row") or {}).get("bucket") or "")
    if bucket not in rank_caps:
        return raw
    spec = rank_caps[bucket]
    if isinstance(spec, dict) and "shrink" in spec:
        return raw * float(spec["shrink"])
    return min(raw, float(spec))


def rank_legs(pool, rank="prob", rank_caps=None):
    """Order the pool. ``rank_caps=None`` is the live identity path.

    ``prob`` remains the live stated-probability order. When ``rank_caps`` is
    supplied, only its effective ordering key changes; ``(raw prob, odds)``
    preserves deterministic ordering among capped ties. Other rank modes are
    unchanged. This is selection-only: the returned leg dictionaries and
    their raw ``prob`` fields are untouched.
    """
    if rank == "ev":
        key = lambda l: (l["prob"] * l["odds"], l["prob"], l["odds"])   # noqa: E731
    elif rank == "rule3way":
        key = lambda l: (_rule_of(l).startswith("3way"),                # noqa: E731
                         l["prob"], l["odds"])
    elif rank_caps is not None and rank in ("prob", "probcap"):
        key = lambda l: (_rank_capped_probability(l, rank_caps),         # noqa: E731
                         l["prob"], l["odds"])
    else:
        key = lambda l: (l["prob"], l["odds"])                          # noqa: E731
    return sorted(pool, key=key, reverse=True)


def _fixture_fold(s) -> str:
    """Fold a team name for the intra-card SAME-FIXTURE guard (2026-09-22
    Dagenham incident), delegating to the shared identity module so the
    card guard and the upstream capture seam use ONE fold definition
    ('&' -> 'and' -> dropped glue token, accent/case folding). See
    edgefactory/identity.py."""
    from edgefactory.identity import team_identity_words

    return team_identity_words(s)


def _fixture_key(leg) -> tuple[str, str, str]:
    """(date, folded home, folded away) — the guard's fixture identity."""
    row = leg.get("row") or {}
    home = row.get("home") or ""
    away = row.get("away") or ""
    if not home and not away:
        parts = str(leg.get("match") or "").split(" vs ", 1)
        if len(parts) == 2:
            home, away = parts
    date = str(row.get("date") or row.get("_archive_day") or "")[:10]
    return (date, _fixture_fold(home), _fixture_fold(away))


def dedup_fixture_legs(ranked_pool) -> tuple[list, list]:
    """Drop later-ranked legs that share a fixture with an already-kept leg.
    Deterministic: the HIGHEST-RANKED duplicate survives. Two legs of one
    match on one card is correlated exposure masquerading as independent
    bets — a staking error, never an edge."""
    seen: set[tuple] = set()
    kept, dropped = [], []
    for leg in ranked_pool:
        k = _fixture_key(leg)
        if k in seen:
            dropped.append(leg)
            continue
        seen.add(k)
        kept.append(leg)
    return kept, dropped


def pair_legs(legs, pairing="consecutive", legs_per_acca=None):
    """Group ranked legs into accas. "consecutive" = live (1+2, 3+4, 5+6);
    "barbell" pairs strongest with weakest (1+6, 2+5, 3+4) to equalise acca
    odds — an A/B candidate only."""
    k = LEGS_PER_ACCA if legs_per_acca is None else legs_per_acca
    if pairing == "barbell" and k == 2:
        n = len(legs) - len(legs) % 2
        return [[legs[i], legs[n - 1 - i]] for i in range(n // 2)]
    accas = [legs[i:i + k] for i in range(0, len(legs), k)]
    return [a for a in accas if len(a) == k]


def select_accas(pool, *, floor=None, rank="prob", rank_caps=None, pairing=None,
                 max_accas=None, legs_per_acca=None, volume_pool=None,
                 volume_min=None, gate_mode=None, fallback=True,
                 saturated_accas=None, min_accas=None, fixture_report=None):
    """THE selection recipe — one code path for live and for the replay harness.

    Every knob defaults to the validated live value; the harness passes
    overrides. Returns a list of accas (each a list of legs), no staking.
    `min_accas` is a card-level gate: a smaller card is NO BET. After ranking,
    same-fixture duplicates are dropped (one match can never ride a card
    twice, 2026-09-22); callers may pass `fixture_report={}` to receive the
    dropped matches for the build log.
    """
    floor = MIN_LEG_ODDS if floor is None else floor
    k = LEGS_PER_ACCA if legs_per_acca is None else legs_per_acca
    max_accas = MAX_ACCAS if max_accas is None else max_accas
    min_accas = MIN_ACCAS if min_accas is None else min_accas
    pairing = PAIRING if pairing is None else pairing
    volume_pool = VOLUME_POOL if volume_pool is None else volume_pool
    volume_min = VOLUME_MIN_PROB if volume_min is None else volume_min
    gate_mode = GATE_MODE if gate_mode is None else gate_mode

    pool = rank_legs([l for l in pool if l["odds"] >= floor], rank,
                     rank_caps=rank_caps)
    pool, fixture_dupes = dedup_fixture_legs(pool)
    if fixture_report is not None:
        fixture_report["dropped"] = [l["match"] for l in fixture_dupes]
    saturated = len(pool) >= volume_pool
    if saturated and saturated_accas:
        max_accas = saturated_accas
    max_legs = max_accas * k

    if saturated and gate_mode == "pool":
        # LEGACY (pre-2026-09-04 threshold was MAX_LEGS*2, also a no-op).
        # Documented no-op — kept only so the harness can reproduce
        # pre-2026-09-04 behaviour with fallback=False (which does bite).
        gated = [l for l in pool if l["prob"] >= volume_min]
        if len(gated) >= max_legs or not fallback:
            pool = gated

    accas = pair_legs(pool[:max_legs], pairing, k)

    if saturated and gate_mode == "acca":
        # Per-acca conviction gate: an acca rides only if EVERY leg clears the
        # threshold. Total risk is unchanged (STAKE_FRAC is split across the
        # surviving accas) — this trades diversification for conviction.
        kept = [a for a in accas if all(l["prob"] >= volume_min for l in a)]
        if kept or not fallback:
            accas = kept
        # else: card-completeness fallback — an empty card is not an opinion.
    if len(accas) < min_accas:
        return []
    return accas


def _stake_weights(weights, n):
    """Return `n` positive numeric weights without touching card selection."""
    if weights is None:
        return None
    if isinstance(weights, str):
        try:
            parsed = [float(v.strip()) for v in weights.split(",") if v.strip()]
        except ValueError as exc:
            raise ValueError("stake weights must be comma-separated numbers") from exc
    else:
        try:
            parsed = [float(v) for v in weights]
        except (TypeError, ValueError) as exc:
            raise ValueError("stake weights must be a sequence of numbers") from exc
    if len(parsed) < n:
        raise ValueError(f"need at least {n} stake weights, got {len(parsed)}")
    parsed = parsed[:n]
    if any(not math.isfinite(v) or v <= 0 for v in parsed):
        raise ValueError("stake weights must be finite and greater than zero")
    return parsed


def plan_day(pool, bank_pct, *, stake_frac=None, stake_mode=None,
             stake_per_acca=None, weights=None, bucket_weights=None, **overrides):
    """Select a card and size it in one production/replay code path.

    ``per_day`` (live default) deploys STAKE_FRAC across however many accas
    were selected. ``per_acca`` deploys STAKE_PER_ACCA for each ticket, while
    never exceeding STAKE_FRAC in total. Optional weights redistribute that
    mode's total across accas; they cannot affect which legs are selected.
    Selection overrides are forwarded to :func:`select_accas`.

    ``bucket_weights`` (optional) is the P&L-tripwire deployment throttle:
    legs from a fully-benched (0.0) bucket are made invisible to selection
    (the door is closed — selection composes only from surviving buckets);
    afterwards acca weight = min over its legs' bucket weights, and a
    demoted (0.5) acca is staked at half. Empty/None means all doors open —
    the replay harness passes nothing and therefore replays true to history.
    """
    stake_frac = STAKE_FRAC if stake_frac is None else float(stake_frac)
    stake_mode = STAKE_MODE if stake_mode is None else stake_mode
    weights = STAKE_WEIGHTS if weights is None else weights
    if stake_per_acca is None:
        stake_per_acca = STAKE_PER_ACCA
    if stake_per_acca is None:
        stake_per_acca = stake_frac / MAX_ACCAS
    stake_per_acca = float(stake_per_acca)
    if stake_mode not in ("per_day", "per_acca"):
        raise ValueError("stake_mode must be 'per_day' or 'per_acca'")
    if not math.isfinite(stake_frac) or stake_frac < 0:
        raise ValueError("stake_frac must be finite and non-negative")
    if not math.isfinite(stake_per_acca) or stake_per_acca < 0:
        raise ValueError("stake_per_acca must be finite and non-negative")

    if bucket_weights:
        # Door closed before selection ever sees the pool: benching must
        # rebuild the whole card from surviving buckets, not just veto the
        # tickets that happened to contain a benched leg post-hoc (that
        # would throw away perfectly good survivor accas).
        pool = [l for l in pool
                if float(bucket_weights.get(
                    str((l.get("row") or {}).get("bucket") or ""), 1.0)) > 0.0]
    accas = select_accas(pool, **overrides)
    if bucket_weights:
        acca_weights = [
            min(float(bucket_weights.get(
                str((l.get("row") or {}).get("bucket") or ""), 1.0))
                for l in a)
            for a in accas]
    else:
        acca_weights = [1.0] * len(accas)
    if not accas or bank_pct <= 0:
        return []

    if stake_mode == "per_day":
        total_frac = stake_frac
    else:
        total_frac = min(stake_frac, stake_per_acca * len(accas))
    parsed_weights = _stake_weights(weights, len(accas))
    if parsed_weights is None:
        # Keep the live-default arithmetic byte-for-byte compatible with the
        # old plan_day implementation.
        stake_pcts = [bank_pct * total_frac / len(accas)] * len(accas)
    else:
        weight_total = sum(parsed_weights)
        stake_pcts = [bank_pct * total_frac * w / weight_total for w in parsed_weights]

    # Ticket stakes ship at four decimals. Independent rounding of a weighted
    # card can otherwise put it 0.0001 above the promised hard day cap.
    stake_pcts = [round(v, 4) for v in stake_pcts]
    rounded_cap = round(bank_pct * total_frac, 4)
    excess = round(sum(stake_pcts) - rounded_cap, 4)
    if excess > 0:
        stake_pcts[-1] = round(stake_pcts[-1] - excess, 4)

    plan = []
    for a, stake_pct, aw in zip(accas, stake_pcts, acca_weights):
        prod = 1.0
        for l in a:
            prod *= l["odds"]
        acca = {"legs": [{**{k: l[k] for k in ("match", "pick", "prob", "odds")},
                          "result": l.get("result")} for l in a],
                "odds": round(prod, 2),
                "stake_pct": round(stake_pct * aw, 4) if aw < 1.0 else stake_pct}
        if aw < 1.0:
            acca["bench_weight"] = aw
        plan.append(acca)
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


def _folded_leg_key(day, home, away, pick):
    """Folded identity key for leg<->archive matching (2026-09-23 stale-slip
    fix): exact display strings mismatch across naming generations
    ('Muharraq SC vs Manama Club' vs 'Muharraq vs Manama'), which silently
    froze the 2026-09-10 slip for 13 days because the 5-day void timer
    lives behind the row-found branch. Structure-stripped identity keys
    ('SC', 'Club' tokens out) make the match generation-proof; two
    same-club fixtures on one date cannot co-occur in one slate."""
    from edgefactory.identity import source_team_key_base

    return (str(day)[:10], source_team_key_base(home), source_team_key_base(away),
            str(pick or "").upper())


def _slip_day_anchor(slip_date):
    """Slip-date timestamp used as the 5-day void-timer fallback when a
    kickoff is missing/unparseable (or the archive row is entirely
    absent). Slip dates are the fixtures' own day by construction."""
    try:
        return datetime.strptime(str(slip_date)[:10], "%Y-%m-%d").replace(tzinfo=TZ)
    except ValueError:
        return None


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
        index[_folded_leg_key(day, p.get("home"), p.get("away"), p.get("pick"))] = p
    lines, still_open = [], []
    for slip in st["open_slips"]:
        open_accas = []
        for a in slip["accas"]:
            legres = []
            conflicts = []
            for l in a["legs"]:
                match = str(l.get("match") or "")
                parts = match.split(" vs ")
                if len(parts) == 2:
                    p = index.get(_folded_leg_key(slip["date"], parts[0], parts[1], l["pick"]))
                else:
                    p = None
                if p is None:
                    r = None
                    anchor = _slip_day_anchor(slip["date"])
                    if anchor is not None and (datetime.now(TZ) - anchor).days >= 5:
                        # Missing archive row AND slip older than the void
                        # horizon: fail closed on the slip-date timer.
                        r = "void"
                elif alias_outcome_conflict(p, entries_by_date):
                    # Fail-closed: donors disagree across spellings. Hold the
                    # leg instead of first-winning the exact-key spelling.
                    r = "conflict"
                    conflicts.append(l["match"])
                else:
                    r = pick_result(p, settled)
                    if r is None:
                        kt = parse_kickoff(p)
                        anchor = kt if kt is not None else _slip_day_anchor(slip["date"])
                        if anchor is not None and (datetime.now(TZ) - anchor).days >= 5:
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
            lines.append(f"settled {slip['date']} acca @{a['odds']:.2f} legs={legres}: bank {st['bank']:.1f}%"
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


def _leg_key(l) -> tuple[str, str]:
    return (str(l.get("match") or ""), str(l.get("pick") or "").upper())


def _acca_label(acca) -> str:
    legs = "; ".join(f"{m} {p}@{o:.2f}" for m, p, o in
                     ((l.get("match"), l.get("pick"), l.get("odds")) for l in acca.get("legs", [])))
    return f"@{acca.get('odds', 0.0):.2f} ({legs})"


def _replacement_lines(prior, plan) -> list[str]:
    """Leg-level diff of a slip being replaced.

    Returns [] when the card is materially identical — same legs, same acca
    positions, same stake. A silent repick prints nothing and the ticket
    reads exactly like any other day. Only real changes are announced, and
    only the parts that changed.
    """
    def index(accas):
        return {(l["match"], l["pick"]): (i, l["odds"])
                for i, a in enumerate(accas, 1) for l in a.get("legs", [])}
    old_accas = prior.get("accas", [])
    old, new = index(old_accas), index(plan)
    dropped = [k for k in old if k not in new]
    added = [k for k in new if k not in old]
    moved = [k for k in new if k in old and old[k][0] != new[k][0]]
    old_tot = round(float(prior.get("staked_pct")
                          or sum(a.get("stake_pct", 0.0) for a in old_accas)), 4)
    new_tot = round(sum(a["stake_pct"] for a in plan), 4)
    stake_moved = abs(new_tot - old_tot) >= 5e-5
    if not (dropped or added or moved or stake_moved):
        return []
    L = []
    if dropped:
        L.append(f"  DROPPED ({len(dropped)}) — if you already placed these, the engine will NOT grade them")
        for m, pk in dropped:
            L.append(f"      {m:44s} {pk:5s} @{old[(m, pk)][1]:.2f}")
    if added:
        L.append(f"  ADDED ({len(added)})")
        for m, pk in added:
            L.append(f"      {m:44s} {pk:5s} @{new[(m, pk)][1]:.2f}")
    if moved:
        L.append(f"  MOVED ({len(moved)}) — same bet, different acca")
        for m, pk in moved:
            L.append(f"      {m:44s} {pk:5s} @{new[(m, pk)][1]:.2f}"
                     f"   acca {old[(m, pk)][0]} → {new[(m, pk)][0]}")
    if stake_moved:
        L.append(f"  total stake {old_tot:.4f}% → {new_tot:.4f}% of capital")
    return L


def _printable_price_board(l, pool_by_key) -> list[dict]:
    """The pick row behind a printed leg (plan accas carry only the four
    printed keys; the pool leg holds the full enriched row)."""
    leg = pool_by_key.get(_leg_key(l))
    if leg is None:
        return []
    return (leg.get("row") or {}).get("price_board") or []


def _log_printed_price_boards(target: str, plan: list[dict],
                              pool_by_key: dict) -> int:
    """Task F (2026-09-06): append-only persistence of every price every
    source was showing at build time for every PRINTED leg, with source name
    and value. One JSON line per printed leg per run — never overwritten, no
    manual entry anywhere. Lines carry the engine's own printed odds/source
    beside the board so the actual-vs-quoted comparison needs no archive.
    Returns the number of legs logged."""
    records = []
    for i, a in enumerate(plan, 1):
        for l in a.get("legs", []):
            leg = pool_by_key.get(_leg_key(l))
            row = (leg or {}).get("row") or {}
            records.append({
                "date": str(target)[:10],
                "printed_at": datetime.now(TZ).replace(microsecond=0).isoformat(),
                "acca": i,
                "match": l.get("match"),
                "pick": str(l.get("pick") or "").upper(),
                "engine_odds": l.get("odds"),
                "odds_source": row.get("odds_source"),
                "price_evidence": row.get("price_evidence"),
                "price_board": row.get("price_board") or [],
            })
    if not records:
        return 0
    month = str(target)[:7]
    path = LOCALDATA / f"price_board_{month}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, default=str) + "\n")
    return len(records)


def _board_coverage_lines(target: str, plan: list[dict],
                          pool_by_key: dict) -> list[str]:
    """Task F: what the next-slate capture should cover. Every printed leg
    whose pick row was enriched at build carries its full price board, so on
    live slates coverage is 100% by construction — this prints the actual
    count for the card being written and the expectation for future slates."""
    n_legs = sum(len(a.get("legs", [])) for a in plan)
    if not n_legs:
        return []
    boards = [_printable_price_board(l, pool_by_key)
              for a in plan for l in a.get("legs", [])]
    covered = sum(1 for b in boards if b)
    sources: Counter = Counter()
    for b in boards:
        for e in b:
            s = str(e.get("source") or "unknown")
            if s and not e.get("chosen"):
                sources[s] += 1
    src_txt = ", ".join(f"{s} {n}" for s, n in sources.most_common()) or "none (only the engine's own price)"
    month = str(target)[:7]
    return [
        f"PRICE BOARD (automatic capture, Task F): build-time board persisted "
        f"for {covered} of {n_legs} printed legs",
        *([f"  corroborating sources on the card: {src_txt}"] if covered else []),
        f"  record: localdata/price_board_{month}.jsonl — expected coverage on "
        f"the next slate: 100% of printed legs with an odds source",
    ]


def cmd_today(args, st):
    settled = load_settled()
    now = datetime.now(TZ)
    target = args.date or now.strftime("%Y-%m-%d")
    frozen = LOCALDATA / f"auto_tickets_{target}.frozen"
    slip_txt = LOCALDATA / f"auto_tickets_{target}.txt"
    if frozen.exists() and not args.force:
        # A frozen rerun must not move ladder streaks, but it still upserts
        # today's real evidence row from the frozen slip. No line in the slip
        # is rewritten; the parser consumes the frozen leg print verbatim.
        ensure_slice_seeded(target)
        archive_index = _archive_index_for_slice(load_archived_picks())
        frozen_rows, _unresolved = parse_slip_slice_rows(slip_txt, archive_index)
        upsert_slice_day(frozen_rows, target)
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
    total_in = len(pool)
    census: dict[str, list[str]] = {}
    # LIVE KICKOFF GUARD (incident #6, revised 2026-09-06 round 2 after the
    # region audit): the Vancouver row's kickoff was the bare string "22:30"
    # — no date, no offset, no zone — in an MLS league whose local clock is
    # far from SAST; the deleted 2026-09-04 chain (SAST-defaulted parse +
    # league-substring -> IANA zone table) failed OPEN on it. The guard drops
    # missing/garbage kickoffs, clock-only kickoffs (bare or no-year
    # day-month) from remote-clock regions (Americas/Asia-Pacific — the
    # Vancouver class; Europe/Africa clock-only rows ride, their clocks are
    # within ~1-2h of SAST), and dated legs already started at build time.
    # It never assumes a zone for a remote clock and never computes a kickoff
    # from the region list; the fail-closed proof contract is NOT applied
    # here (it is the off-by-default --kickoff-contract audit instrument).
    pool, ko_drops = live_kickoff_guard(pool, now)
    for reason, names in ko_drops.items():
        census.setdefault(reason, []).extend(names)
    # Already-settled legs are finished matches: result known -> not a bet.
    settled_drops = [l["match"] for l in pool if l.get("result")]
    pool = [l for l in pool if not l.get("result")]
    if settled_drops:
        census["already settled (result known)"] = settled_drops
    # Cross-slate guard: a fixture already archived on an EARLIER day's slate
    # has already kicked off (late finishers carried into today's capture).
    past = set()
    for a in load_archived_picks():
        if str(a.get("date") or a.get("_archive_day") or "")[:10] < target:
            past.add((str(a.get("home") or "").strip().lower(),
                      str(a.get("away") or "").strip().lower()))
    cross_drops = [l["match"] for l in pool
                   if (str(l["row"].get("home") or "").strip().lower(),
                       str(l["row"].get("away") or "").strip().lower()) in past]
    pool = [l for l in pool
            if (str(l["row"].get("home") or "").strip().lower(),
                str(l["row"].get("away") or "").strip().lower()) not in past]
    if cross_drops:
        census["fixture already on an earlier day's slate (kicked off)"] = cross_drops
    # --- selection ladder + door P&L tripwires --------------------------
    # Door-level P&L remains the first policy call. Its bench filter and
    # stake weighting remain separate from the slice ladder's rank-only cap.
    pnl_weights, pnl_verdicts = compute_bucket_pnl(target)
    # Seed/read the result-free slice before scoring. Settlement is always a
    # read-time join, so an unsettled row never becomes an automatic loss.
    ensure_slice_seeded(target)
    slice_policy, slice_verdicts = compute_bucket_slice(target)
    base_pool = list(pool)  # shadow planning strips BOTH ladder and door policy
    door_pool = list(base_pool)
    benched_drops = [f"{l['match']} [{l['row'].get('bucket')}]" for l in door_pool
                     if pnl_weights.get(str(l["row"].get("bucket") or ""), 1.0) <= 0.0]
    if benched_drops:
        door_pool = [l for l in door_pool
                     if pnl_weights.get(str(l["row"].get("bucket") or ""), 1.0) > 0.0]
        census["P&L tripwire: bucket benched (BLEEDING streak >= "
              f"{PNL_BENCH_STREAK} days)"] = sorted(benched_drops)

    slice_benched = set(slice_policy.get("bench_buckets") or ())
    slice_bench_drops = [f"{l['match']} [{l['row'].get('bucket')}]" for l in door_pool
                         if str(l["row"].get("bucket") or "") in slice_benched]
    plan_pool = [l for l in door_pool
                 if str(l["row"].get("bucket") or "") not in slice_benched]
    if slice_bench_drops:
        census["SELECTION LADDER: slice bucket benched"] = sorted(slice_bench_drops)

    # The shadow plan is a second pure call. It deliberately strips both the
    # slice caps and the door bench/weights, then keeps only diminished-bucket
    # legs and removes any key already represented by today's real plan.
    diminished = {b for b, v in slice_verdicts.items()
                  if v.get("action") in ("DEMOTED", "BENCHED")}
    bank_eff = effective_bank(st, exclude_date=target)
    shadow_rows = []
    pure_shadow_plan = None
    base_pool_by_key = {_leg_key(l): l for l in base_pool}
    if diminished and len(base_pool) >= LEGS_PER_ACCA:
        pure_shadow_plan = plan_day(list(base_pool), bank_eff,
                                    fixture_report={})

    census_lines = format_skip_census(total_in, len(plan_pool), census)
    if not any(census.values()):
        census_lines = []
    if len(plan_pool) < LEGS_PER_ACCA:
        # --force-repick replaces prior same-day real+shadow rows even when
        # the new final plan is empty — but only if nothing actually shipped
        # for this date. A printed slip on disk is the frozen record of legs
        # already at the bookmaker, and that evidence must survive.
        upsert_slice_day(shadow_rows, target, allow_empty=not slip_txt.exists())
        print("\n".join(census_lines))
        print("\n".join(_slice_action_lines(slice_verdicts)))
        print("\n".join(_slice_table_lines(slice_verdicts)))
        print(f"NO BET TODAY — {len(plan_pool)} qualifying leg(s), need {LEGS_PER_ACCA}")
        print("(bank stays unbet)")
        return 0

    fixture_report: dict[str, list[str]] = {}
    plan = plan_day(plan_pool, bank_eff, fixture_report=fixture_report,
                    bucket_weights=pnl_weights,
                    rank_caps=slice_policy.get("rank_caps") or None)
    if not plan:
        upsert_slice_day(shadow_rows, target, allow_empty=not slip_txt.exists())
        print("\n".join(census_lines))
        print("\n".join(_slice_action_lines(slice_verdicts)))
        print("\n".join(_slice_table_lines(slice_verdicts)))
        print("NO BET TODAY — plan empty")
        return 0
    # Task E (2026-09-06): a force-repick REPLACES the target date's own
    # existing slip (upsert below deletes it) — so its stake was excluded
    # from committed capital above. The slip prints the card as-is.
    pool_by_key = base_pool_by_key
    real_rows = _slice_plan_rows(target, plan, pool_by_key)
    real_keys = {_slice_row_key(row) for row in real_rows}
    if pure_shadow_plan is not None:
        shadow_rows = _slice_shadow_rows(
            target, pure_shadow_plan, pool_by_key, real_keys, diminished,
        )
    upsert_slice_day(real_rows + shadow_rows, target)
    upsert_slip(st, target, plan)
    _log_printed_price_boards(target, plan, pool_by_key)   # Task F, append-only
    committed = st["bank"] - bank_eff
    lines = [f"AUTO TICKETS (ROLLING) — {target}", "=" * 62,
             f"PERFORMANCE: total bank {st['bank']:.1f}% of capital (x{st['bank']/st['base_pct']:.2f}) = "
             f"free bank {bank_eff:.1f}% + committed {committed:.1f}% · "
             f"next take-profit notification at {take_profit_target(st):.1f}%"]
    trip = [v for v in pnl_verdicts.values() if v["weight"] < 1.0]
    if trip:
        lines.append("P&L TRIPWIRE (trailing " + str(PNL_WINDOW_DAYS)
                     + "d, streak floors): "
                     + "; ".join(
                         f"{v_name} {v['verdict']} streak {v['streak']}"
                         f" (n={v['n']}, gap {v['gap']}, z {v['z']}) -> "
                         f"x{v['weight']}"
                         for v_name, v in sorted(
                             ((b, v) for b, v in pnl_verdicts.items()
                              if v['weight'] < 1.0),
                             key=lambda kv: kv[1]['weight'])))
    lines.extend(_slice_action_lines(slice_verdicts))
    lines.extend(_slice_table_lines(slice_verdicts))
    if shadow_rows:
        lines.append(f"SELECTION LADDER SHADOW: {len(shadow_rows)} diminished-bucket leg(s) logged")
    if fixture_report.get("dropped"):
        lines.append("SAME-FIXTURE DEDUP: dropped "
                     + "; ".join(fixture_report["dropped"])
                     + " (one match entered twice via a name-spelling split; "
                        "highest-stated twin kept)")
    for i, a in enumerate(plan, 1):
        demote_tag = (f" [TRIPWIRE-DEMOTED x{a['bench_weight']}]"
                      if a.get("bench_weight", 1.0) < 1.0 else "")
        lines.append(f"\n[ACCA #{i}] @{a['odds']:.2f} — stake {a['stake_pct']:.1f}% of capital "
                     f"({a['stake_pct']/bank_eff:.1%} of free bank){demote_tag}")
        for l in a["legs"]:
            lines.append(f"   {l['match']:46s} {l['pick']:5s} @ {l['odds']:.2f}  (stated {l['prob']:.0%})")
    day_staked = sum(a["stake_pct"] for a in plan)
    lines.append(f"\ndeploying {STAKE_FRAC:.0%} of free bank today "
                 f"= {day_staked:.1f}% of capital · take-profit NOTIFICATION at "
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

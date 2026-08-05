#!/usr/bin/env python3
"""capture_theodds.py — snapshot The Odds API prices for the frozen daily shortlist.

Audit-only by design: this captures prices (pick-time and near-close) for CLV;
nothing gates picks on this feed.

Wired into scripts/daily.py via --auto at the existing CLV capture points, so
the established commands cover everything:

    python3 scripts/daily.py --auto-run      # 3h service loop (official + intraday)
    python3 scripts/daily.py --auto-once     # one smart iteration (GitHub Actions)

Manual / debug usage:

    PYTHONPATH=src python3 scripts/capture_theodds.py --self-test           # offline, no key needed
    PYTHONPATH=src python3 scripts/capture_theodds.py --dry-run [--date D]  # coverage + cost estimate, 0 credits
    PYTHONPATH=src python3 scripts/capture_theodds.py [--date D]            # full snapshot now (all fixtures)
    PYTHONPATH=src python3 scripts/capture_theodds.py --auto [--date D]     # timing-driven (what daily.py calls)
    PYTHONPATH=src python3 scripts/capture_theodds.py --refresh-sports      # rebuild sport-key cache (free)
    PYTHONPATH=src python3 scripts/capture_theodds.py --usage               # per-key ring status

--auto semantics (idempotent across 3h iterations):
  * first snapshot per fixture: once per day, skipped near/after kickoff
  * close snapshot per fixture: once per day, only within ODDS_API_CLOSE_WINDOW_MIN
    (default 45) minutes before kickoff
  * an attempts ledger (localdata/theoddsapi_attempts_<date>.json) blocks
    re-tries for 6h per fixture/snapshot-type so failures cannot bleed credits
    every iteration.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import importlib
import json
import os
import sys
from datetime import date as _date
from datetime import datetime, timezone  # timedelta dropped: unused (red-team hygiene)
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO = Path(__file__).resolve().parents[1]
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA") or (REPO / "localdata"))
SOURCE_NAME = "theoddsapi_odds"
CLOSE_WINDOW_MIN = int(os.environ.get("ODDS_API_CLOSE_WINDOW_MIN", "45") or 45)
START_GRACE_MIN = 30          # don't first-capture a match this close to/after kickoff
ATTEMPT_RETRY_HOURS = 6       # failure cooldown per fixture/snapshot-type
KICKOFF_MISMATCH_MIN = 15     # pick-listed vs captured-API kickoff divergence guard


def _month_file(day: str) -> Path:
    return LOCALDATA / f"{SOURCE_NAME}_{day[:7]}.csv.gz"


def _read_month(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        with gzip.open(path, "rt", newline="") as fh:
            return list(csv.DictReader(fh))
    except Exception:
        return []


def _write_month(path: Path, rows: list[dict], columns: list[str]) -> None:
    tmp = path.with_suffix(".tmp")
    with gzip.open(tmp, "wt", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def append_rows(day: str, rows: list[dict], columns: list[str]) -> int:
    """Merge new rows into the monthly gz; full-row dedupe keeps both snapshots."""
    path = _month_file(day)
    existing = _read_month(path)
    seen = {tuple(str(r.get(c, "")) for c in columns) for r in existing}
    added = 0
    for r in rows:
        key = tuple(str(r.get(c, "")) for c in columns)
        if key not in seen:
            seen.add(key)
            existing.append(r)
            added += 1
    existing.sort(key=lambda r: (str(r.get("date")), str(r.get("kickoff")),
                                 str(r.get("home")), str(r.get("market")),
                                 str(r.get("selection")), str(r.get("bookmaker")),
                                 str(r.get("captured_at"))))
    if added:
        LOCALDATA.mkdir(parents=True, exist_ok=True)
        _write_month(path, existing, columns)
    return added


# ---------------------------------------------------------------- attempts ledger

def _attempts_path(day: str) -> Path:
    return LOCALDATA / f"theoddsapi_attempts_{day}.json"


def _load_attempts(day: str) -> dict:
    try:
        if _attempts_path(day).exists():
            data = json.loads(_attempts_path(day).read_text())
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _save_attempts(day: str, attempts: dict) -> None:
    try:
        LOCALDATA.mkdir(parents=True, exist_ok=True)
        path = _attempts_path(day)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(attempts, indent=2, sort_keys=True))
        os.replace(tmp, path)  # atomic: no torn attempts files on overlapping runs
    except Exception as exc:
        print(f"theoddsapi: attempts ledger write failed: {exc}", file=sys.stderr)


def _recent(iso_ts: str | None, hours: float) -> bool:
    if not iso_ts:
        return False
    try:
        ts = datetime.fromisoformat(str(iso_ts).replace("Z", "+00:00"))
    except ValueError:
        return False
    return (datetime.now(timezone.utc) - ts).total_seconds() < hours * 3600


def _fixture_key(f: dict) -> str:
    return f"{f.get('home')}|{f.get('away')}"


def _fixture_priced(f: dict, existing_rows: list[dict], match_fn) -> bool:
    """Fixture already has same-month odds rows — cross-feed name tolerant
    (pick 'Halmstad' vs stored 'Halmstads BK' must count as priced)."""
    for r in existing_rows:
        if match_fn(f.get("home"), r.get("home")) and match_fn(f.get("away"), r.get("away")):
            return True
    return False


def _fixture_row_kickoff(f: dict, existing_rows: list[dict], match_fn) -> datetime | None:
    """Kickoff (UTC) from already-captured rows for this fixture, if present.

    Team orientation tolerant (straight or swapped home/away). The picks listing
    occasionally carries a non-local (e.g. UK) kickoff time; the API commence_time
    on captured rows is authoritative, so the planner compares the two sources."""
    if not match_fn:
        return None
    for r in existing_rows or []:
        try:
            straight = match_fn(f.get("home"), r.get("home")) and match_fn(f.get("away"), r.get("away"))
            swapped = match_fn(f.get("home"), r.get("away")) and match_fn(f.get("away"), r.get("home"))
            if not (straight or swapped):
                continue
            iso = (r.get("kickoff") or "").replace("Z", "+00:00")
            if iso:
                return datetime.fromisoformat(iso)
        except Exception:
            continue
    return None


def plan_auto(fixtures: list[dict], existing_rows: list[dict], attempts: dict, *,
              now: datetime | None = None, kickoff_fn=None, match_fn=None) -> tuple[list[dict], dict, list[str]]:
    """Decide which fixtures need a snapshot this iteration.

    Returns (due_fixtures, updates, skip_lines). `updates` maps fixture key ->
    snapshot type so the caller can stamp the attempts ledger after the run.
    """
    now = now or datetime.now(timezone.utc)

    due: list[dict] = []
    updates: dict[str, str] = {}
    skips: list[str] = []
    for f in fixtures:
        fk = _fixture_key(f)
        rec = attempts.get(fk, {})
        kickoff = kickoff_fn(f) if kickoff_fn else None
        has_rows = _fixture_priced(f, existing_rows, match_fn) if match_fn else False

        # Kickoff divergence guard: if captured rows disagree with the listing by
        # more than KICKOFF_MISMATCH_MIN, plan from the EARLIER time — conservative
        # in both directions (never fire after a true kickoff). Surfaced as WARN.
        row_ko = _fixture_row_kickoff(f, existing_rows, match_fn) if has_rows else None
        if row_ko is not None and kickoff is not None:
            delta_m = abs((row_ko - kickoff).total_seconds()) / 60.0
            if delta_m > KICKOFF_MISMATCH_MIN:
                skips.append(
                    f"WARN kickoff-mismatch {fk}: pick lists {kickoff:%H:%MZ}, captured rows say "
                    f"{row_ko:%H:%MZ} (Δ={delta_m:.0f}m; planning from the earlier)")
                kickoff = min(kickoff, row_ko)

        in_close_window = False
        started = False
        if kickoff is not None:
            mins_to_kickoff = (kickoff - now).total_seconds() / 60.0
            in_close_window = -15 <= mins_to_kickoff <= CLOSE_WINDOW_MIN
            started = mins_to_kickoff < START_GRACE_MIN * -1

        if started:
            skips.append(f"{fk} (kickoff already passed)")
            continue

        if in_close_window and not rec.get("close_at") and not _recent(rec.get("close_fail_at"), ATTEMPT_RETRY_HOURS):
            due.append(f)
            updates[fk] = "close_at"
            continue

        if not has_rows and not rec.get("first_at") and not _recent(rec.get("fail_at"), ATTEMPT_RETRY_HOURS):
            if kickoff is not None and (kickoff - now).total_seconds() < START_GRACE_MIN * 60 and not in_close_window:
                skips.append(f"{fk} (too close to kickoff for first capture)")
                continue
            due.append(f)
            updates[fk] = "first_at"
            continue

        if has_rows or rec.get("first_at"):
            reason = "priced, close window not open" if kickoff else "priced"
        elif _recent(rec.get("fail_at"), ATTEMPT_RETRY_HOURS):
            reason = f"retry cooldown ({ATTEMPT_RETRY_HOURS}h after failed attempt)"
        else:
            reason = "waiting"
        skips.append(f"{fk} ({reason})")

    return due, updates, skips


def _self_test(mod) -> int:
    """Offline parse/match checks against embedded fixtures; no network."""
    sports = [
        {"key": "soccer_sweden_allsvenskan", "group": "Soccer", "title": "Allsvenskan", "active": True},
        {"key": "soccer_norway_eliteserien", "group": "Soccer", "title": "Eliteserien", "active": True},
    ]
    pick = {"home": "Halmstad", "away": "Sirius", "league": "Sweden Allsvenskan",
            "date": "2026-08-03", "kickoff": "03-08, 18:00"}
    events = [
        {"id": "evt_wrong", "sport_key": "soccer_sweden_allsvenskan",
         "commence_time": "2026-08-03T16:00:00Z", "home_team": "IK Sirius", "away_team": "Halmstads BK"},
        {"id": "evt_right", "sport_key": "soccer_sweden_allsvenskan",
         "commence_time": "2026-08-03T16:00:00Z", "home_team": "Halmstads BK", "away_team": "IK Sirius"},
    ]
    payload = {"id": "evt_right", "sport_key": "soccer_sweden_allsvenskan", "sport_title": "Allsvenskan",
               "bookmakers": [
                   {"key": "pinnacle", "title": "Pinnacle", "last_update": "2026-08-03T10:00:00Z",
                    "markets": [
                        {"key": "h2h", "last_update": "2026-08-03T10:00:00Z",
                         "outcomes": [{"name": "Halmstads BK", "price": 2.10},
                                      {"name": "Draw", "price": 3.40},
                                      {"name": "IK Sirius", "price": 3.25}]},
                        {"key": "totals", "last_update": "2026-08-03T10:00:00Z",
                         "outcomes": [{"name": "Over", "price": 1.95, "point": 2.5},
                                      {"name": "Under", "price": 1.85, "point": 2.5},
                                      {"name": "Over", "price": 9.0, "point": 4.5}]},
                        {"key": "totals_alt", "last_update": "2026-08-03T10:00:00Z",
                         "outcomes": [{"name": "Over", "price": 1.30, "point": 1.5}]},
                        {"key": "btts", "last_update": "2026-08-03T10:00:00Z",
                         "outcomes": [{"name": "Yes", "price": 1.95},
                                      {"name": "No", "price": 1.80}]},
                        {"key": "team_totals", "last_update": "2026-08-03T10:00:00Z",
                         "outcomes": [{"name": "Halmstads BK Over 1.5", "price": 1.30},
                                      {"name": "IK Sirius Under 1.5", "price": 2.10}]},
                        {"key": "double_chance", "last_update": "2026-08-03T10:00:00Z",
                         "outcomes": [{"name": "HomeOrDraw", "price": 1.05},
                                      {"name": "AwayOrDraw", "price": 4.50},
                                      {"name": "HomeOrAway", "price": 1.02}]},
                    ]}]}
    failures = []

    def check(label: str, cond: bool) -> None:
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        if not cond:
            failures.append(label)

    check("league resolves to sport key", mod.sport_key_for_league("Sweden Allsvenskan", sports) == "soccer_sweden_allsvenskan")
    check("uncovered league returns None", mod.sport_key_for_league("Belarus Vysshaya Liga", sports) is None)
    check("short league norm cannot false-hit", mod.sport_key_for_league("Ie2", sports + [{"key": "soccer_spl", "group": "Soccer", "title": "Scottish Premiership", "active": True}]) is None)
    ev = mod.match_event(pick, events)
    check("pair-constrained match ignores swapped fixture", ev is not None and ev["id"] == "evt_right")
    rows = mod.rows_from_event_odds(pick, events[1], payload)
    check("14 rows parsed (3x h2h + 3x totals incl 4.5 + 1x totals_alt@1.5 + 2x btts "
          "+ 2x team_totals + 3x double_chance)", len(rows) == 14)
    sel = {(r["market"], r["selection"]): r["odds"] for r in rows}
    check("h2h home price", sel.get(("1x2", "home")) == 2.10)
    check("h2h draw price", sel.get(("1x2", "draw")) == 3.40)
    check("ou_2.5 under price", sel.get(("ou_2.5", "under")) == 1.85)
    check("ou_4.5 over price", sel.get(("ou_4.5", "over")) == 9.0)
    check("ou_1.5 over price (totals_alt)", sel.get(("ou_1.5", "over")) == 1.30)
    check("btts yes price", sel.get(("btts", "yes")) == 1.95)
    check("btts no price", sel.get(("btts", "no")) == 1.80)
    check("team_totals home over 1.5", sel.get(("tt_home_1.5", "over")) == 1.30)
    check("team_totals away under 1.5", sel.get(("tt_away_1.5", "under")) == 2.10)
    check("double_chance 1x", sel.get(("dc", "1x")) == 1.05)
    check("double_chance 12", sel.get(("dc", "12")) == 1.02)
    check("unknown market ignored", all(r["market"] != "totals_alt" for r in rows))
    check("schema columns", set(mod.COLUMNS) == set(rows[0].keys()) if rows else False)

    # key rotation ring (offline, pure; ledger redirected so real state is untouched)
    import tempfile
    real_usage_file = mod.USAGE_FILE
    mod.USAGE_FILE = Path(tempfile.mkdtemp()) / "usage_test.json"
    os.environ["ODDS_API_KEYS"] = "aaa,bbb"
    mod.API_KEYS = ("aaa", "bbb")
    fp_a, fp_b = mod._key_fp("aaa"), mod._key_fp("bbb")
    ring = mod._key_ring()
    check("daily ring contains all keys", set(ring) == {"aaa", "bbb"} and len(ring) == 2)
    mod._mark_exhausted(fp_a, "test")
    active = mod._active_key()
    check("exhausted key skipped by active_key", active == "bbb")
    mod._mark_exhausted(fp_b, "test")
    check("ring fully exhausted -> None", mod._active_key() is None)
    mod.unmark_exhausted()
    check("unmark restores ring", mod._active_key() in ("aaa", "bbb"))
    mod.USAGE_FILE = real_usage_file
    del os.environ["ODDS_API_KEYS"]
    mod.API_KEYS = mod._parse_keys()

    # plan_auto: cross-feed priced check (pick names vs API-stored names)
    fix = [{"home": "Halmstad", "away": "Sirius", "kickoff": "03-08, 18:00", "date": "2026-08-03"}]
    existing = [{"home": "Halmstads BK", "away": "IK Sirius"}]
    due, updates, skips = plan_auto(fix, existing, {}, match_fn=mod._team_names_match)
    check("plan_auto: priced fixture (renamed by API) not re-due", not due)
    due, updates, skips = plan_auto(fix, [], {}, match_fn=mod._team_names_match)
    check("plan_auto: unpriced fixture due for first capture", len(due) == 1 and updates.get("Halmstad|Sirius") == "first_at")

    # year-boundary: fixture year comes from pick date, never wall-clock
    ny = mod._pick_kickoff_utc({"kickoff": "01-01, 12:00", "date": "2027-01-01"})
    check("kickoff year from pick date (Jan fixture in Dec run)", ny is not None and ny.year == 2027)
    yb = mod._pick_kickoff_utc({"kickoff": "31-12, 23:00", "date": "2026-12-31"})
    check("kickoff year from pick date (Dec 31 fixture)", yb is not None and yb.year == 2026)

    print(f"self-test: {'PASS' if not failures else 'FAIL'} ({len(failures)} failures)")
    return 0 if not failures else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=_date.today().isoformat(), help="match date YYYY-MM-DD (default: today)")
    ap.add_argument("--snapshot", default="adhoc", choices=["pick_time", "close", "adhoc"], help="label for manual runs")
    ap.add_argument("--auto", action="store_true", help="timing-driven mode called by daily.py (pick_time/close windows)")
    ap.add_argument("--dry-run", action="store_true", help="no network, no credits: coverage + cost estimate")
    ap.add_argument("--self-test", action="store_true", help="offline parse checks, no key needed")
    ap.add_argument("--refresh-sports", action="store_true", help="force sport-key cache rebuild (free)")
    ap.add_argument("--usage", action="store_true", help="print per-key ring status and exit")
    args = ap.parse_args()

    mod = importlib.import_module("edgefactory.sources.theoddsapi")

    if args.self_test:
        return _self_test(mod)

    if args.usage:
        status = mod.ledger_status()
        print(f"theoddsapi usage ({status['month']}): "
          f"{status['credits_local']}/{status['budget']} local credits across {status['n_keys']} key(s); "
          f"cost_per_event={status['cost_per_event']}")
        for k in status["keys"]:
            flag = " EXHAUSTED" if k["exhausted"] else ""
            print(f"  {k['fp']}: local={k['credits_local']}/{k['budget']} "
                  f"server_used={k['server_used']} server_remaining={k['server_remaining']}{flag}")
        return 0

    fixtures = mod.shortlist(args.date)
    print(f"date={args.date} shortlist={len(fixtures)} fixture(s)")

    if args.dry_run:
        sports = []
        if mod.SPORTS_CACHE_FILE.exists():
            try:
                sports = json.loads(mod.SPORTS_CACHE_FILE.read_text()).get("sports", [])
            except Exception:
                sports = []
        if not sports:
            print("sport-key cache: MISSING (first live run will fetch /sports — free)")
        covered = 0
        for f in fixtures:
            key = mod.sport_key_for_league(f.get("league"), sports) if sports else None
            mark = key or "UNKNOWN (league may not be covered)"
            covered += bool(key)
            print(f"  - {f['home']} vs {f['away']}  [{f['league']}] -> {mark}")
        est = (covered or len(fixtures)) * mod.cost_per_event()
        status = mod.ledger_status()
        print(f"estimated cost: ~{est} credit(s)/snapshot "
              f"({mod.cost_per_event()}/event = {len(mod.MARKETS)} markets x {len(mod.REGIONS)} regions)")
        print(f"ledger: {status['credits_local']}/{status['budget']} used this month across "
              f"{status['n_keys']} key(s); server_remaining={status['server_remaining']}")
        print("dry-run: 0 credits spent")
        return 0

    if not mod.enabled():
        print("No The Odds API keys configured. Set ODDS_API_KEYS in .env (see .env.example).", file=sys.stderr)
        return 2

    if args.refresh_sports:
        sports = mod.load_sports(refresh=True)
        print(f"sports cache refreshed: {len(sports)} active soccer keys")
        return 0

    # live fetch paths -------------------------------------------------------
    if args.auto:
        existing = _read_month(_month_file(args.date))
        attempts = _load_attempts(args.date)
        due, updates, skips = plan_auto(fixtures, existing, attempts,
                                        kickoff_fn=mod._pick_kickoff_utc,
                                        match_fn=mod._team_names_match)
        for line in skips:
            print(f"  skip {line}")
        if not due:
            print("auto: nothing due this iteration (0 credits)")
            return 0
        print(f"auto: {len(due)} fixture(s) due -> fetching")
    else:
        due = fixtures
        updates = {_fixture_key(f): "first_at" for f in fixtures}
        attempts = _load_attempts(args.date)

    try:
        rows, unmatched, matched = mod.fetch_fixtures(due, day=args.date)
    except Exception as exc:
        print(f"capture aborted: {exc}", file=sys.stderr)
        return 1

    added = append_rows(args.date, rows, mod.COLUMNS) if rows else 0
    now_iso = datetime.now(timezone.utc).isoformat()
    unmatched_keys = set()
    for line in unmatched:
        # "Home vs Away (reason)" -> fixture key. Fixture names contain no ' vs '.
        unmatched_keys.add(line.split(" (")[0])
    for f in due:
        fk = _fixture_key(f)
        snap_field = updates.get(fk)
        if not snap_field:
            continue
        rec = attempts.setdefault(fk, {})
        fail_field = "close_fail_at" if snap_field == "close_at" else "fail_at"
        if f"{f.get('home')} vs {f.get('away')}" in unmatched_keys:
            rec[fail_field] = now_iso
        else:
            rec[snap_field] = now_iso
    _save_attempts(args.date, attempts)

    status = mod.ledger_status()
    print(f"capture done: rows={len(rows)} new_appended={added} -> {_month_file(args.date).name}")
    print(f"ledger: {status['credits_local']}/{status['budget']} local across {status['n_keys']} key(s); "
          f"near-term remaining={status['server_remaining']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

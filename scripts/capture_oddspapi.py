#!/usr/bin/env python3
"""Bounded OddsPapi price capture for the enhancement overlay (Addendum 27.7).

Operator override 2026-08-05 authorizes OddsPapi as a real price source for
enhancement markets the other feeds do not price (team totals, double chance,
totals lines, btts, 1x2). This script performs BOUNDED, read-only capture of
OddsPapi odds into the unified schema used by `enh_pricing`:

    localdata/oddspapi_odds_YYYY-MM.csv.gz

Safety rails (operator-approved):
- FREE-TIER BOUNDED: OddsPapi free quota is small. Capture is limited to a
  bounded set of fixtures per run (--max-fixtures, default 20) and never
  broad-polls the whole day. Unmatched same-day picks are prioritized first,
  then enhancement-relevant fixtures.
- FLAG-GATED: daily.py invokes this only when
  EDGE_FACTORY_ODDSPAPI_PRICES=1. It follows the non-ticketable candidate
  build and can be used only by the final timestamp-qualified pricing pass,
  never as a rewrite of a ticketed card. Fail-soft: any error degrades to "no rows"
  and never raises into a caller.
- KEYS STAY LOCAL: ODDSPAPI_API_KEYS is read from .env; never printed,
  logged, committed, or placed in Actions.
- WALK-FORWARD ONLY: rows accumulate from activation forward; no backfill,
  no retrospective validation.
- No selection / certification / source-weight / push change. This is a
  price source for the enhancement overlay only.

Usage:
  PYTHONPATH=src python3 scripts/capture_oddspapi.py --date 2026-08-05 [--max-fixtures 20]
  PYTHONPATH=src python3 scripts/capture_oddspapi.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from edgefactory.sources.oddspapi_odds import (
    EXPECTED_PARSE_SKIPS,
    api_keys,
    fetch_fixtures,
    fetch_odds,
    load_market_type_map,
    market_catalog,
    market_catalog_entries,
    rows_from_odds_response,
)
from edgefactory.util import fold_ascii

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "localdata"

# Row schema generation for this store.
#
#   (blank)/1  rows written before 2026-10-03. The parser that produced them
#              read the outcome name from ``name`` only — but the live /odds
#              payload carries it at ``players.0.playerName`` — and took the
#              participants from /odds, which does not supply them. Every such
#              row was emitted with blank home/away and the selection
#              defaulted to "home" because the empty name compared equal to
#              the empty home name. 414 of them are in
#              localdata/oddspapi_odds_2026-10.csv.gz.
#   2          identity comes from the /fixtures record, outcome names are
#              read from name|playerName, empty names are refused, mainLine
#              is honoured and provider stamps are kept.
#   3          outcome identity is resolved from the provider's documented
#              outcome ids (catalog outcome names / the 101/102/103 mapping)
#              with a fail-closed ambiguity check, and the row RETAINS the
#              provider's outcome key + market id for audit. Generation-2
#              rows did not run the ambiguity check and did not retain the
#              outcome key, so their evidence can no longer be verified from
#              the CSV - they are superseded (counted stale, never deleted).
#
# Blank home/away is only the *symptom* of generation 1; the mislabelled
# selection is the defect. A reader that bypassed rows on blank participants
# alone would still trust a generation-1 row that happened to carry teams.
# Readers therefore gate on the generation, not on the symptom.
SCHEMA_VERSION = 3

COLUMNS = ["source", "source_type", "sport", "date", "kickoff", "league",
           "home", "away", "market", "selection", "odds", "bookmaker",
           "captured_at", "published_at", "provider_changed_at",
           "outcome_key", "bookmaker_market_id",
           "schema_version"]


def _out_path(day: str) -> Path:
    return OUT_DIR / f"oddspapi_odds_{day[:7]}.csv.gz"


def _census_path(day: str) -> Path:
    return OUT_DIR / f"oddspapi_market_census_{day[:7]}.json"


_STAMP_COLS = ("captured_at", "published_at", "provider_changed_at")

# Team-name normalisation for slate prioritisation: same standard as the
# coverage probe (fold_ascii + club-noise tokens), so an EXACT normalized
# pair match - never a fuzzy one - promotes a fixture.
_CLUB_NOISE = {"fc", "cf", "sc", "ac", "as", "pfc", "ofc", "gnk", "fk", "afc",
               "club", "the", "if", "bk", "sk", "ff", "u19", "u21", "ii"}


def _team_key(value: object) -> str:
    tokens = [t for t in str(fold_ascii(value)).lower().split() if t]
    meaningful = [t for t in tokens if t not in _CLUB_NOISE]
    return " ".join(meaningful or tokens)


def _fixture_pair(fixture: dict) -> tuple[str, str]:
    home = fixture.get("participant1Name") or fixture.get("home") or ""
    away = fixture.get("participant2Name") or fixture.get("away") or ""
    return _team_key(home), _team_key(away)


def _load_slate_pairs(day: str) -> set[tuple[str, str]]:
    """Normalized (home, away) pairs of the day's pick slate, if a built
    candidate/final slate exists on disk. Absent or unreadable -> empty."""
    path = OUT_DIR / "picks_today.json"
    try:
        raw = json.loads(path.read_text())
    except (OSError, ValueError):
        return set()
    picks = raw if isinstance(raw, list) else (
        raw.get("picks") if isinstance(raw, dict) else None)
    if not isinstance(picks, list):
        return set()
    pairs: set[tuple[str, str]] = set()
    for pick in picks:
        if not isinstance(pick, dict):
            continue
        if str(pick.get("date") or "")[:10] != str(day)[:10]:
            continue
        home, away = _team_key(pick.get("home")), _team_key(pick.get("away"))
        if home and away:
            pairs.add((home, away))
            pairs.add((away, home))  # orientation-independent
    return pairs


def _prioritise_slate_fixtures(fixtures: list[dict], day: str) -> tuple[list[dict], int]:
    """Put fixtures the day's slate actually covers first (stable order).

    The docstring has always promised "unmatched same-day picks are
    prioritized first"; the 2026-10-03 run showed what happens without it:
    the 20-fixture budget went to provider-ordered fixtures the slate never
    covered (BK Forward vs IK Sleipner has no pick on the card), so even the
    three healthy rows could only land in fixture_key_miss. Unmatched
    fixtures are NOT dropped - enhancement coverage keeps whatever budget
    remains after the slate fixtures.
    """
    try:
        slate = _load_slate_pairs(day)
    except Exception:  # noqa: BLE001 - prioritisation must never break capture
        return fixtures, 0
    if not slate:
        return fixtures, 0
    prioritised = [fx for fx in fixtures if _fixture_pair(fx) in slate]
    if not prioritised:
        return fixtures, 0
    rest = [fx for fx in fixtures if _fixture_pair(fx) not in slate]
    return prioritised + rest, len(prioritised)


def _classify_parse_skips(parse_skips: dict) -> dict:
    """Split per-reason skip counts into expected provider behaviour and
    everything else (defects / coverage loss). `outcome_inactive` and
    `market_inactive` are documented provider state flags - a suspended
    quote is not a price and skipping it is correct, so it is reported as
    expected, not as loss."""
    expected: dict[str, int] = {}
    loss: dict[str, int] = {}
    for reason, count in sorted(parse_skips.items()):
        if str(reason) in EXPECTED_PARSE_SKIPS:
            expected[str(reason)] = int(count)
        else:
            loss[str(reason)] = int(count)
    return {"expected": expected, "loss_or_diagnosis": loss}


def _persist_vocabulary_snapshot(day: str, catalog_entries: dict) -> str:
    """Persist the provider's served market vocabulary for source_health.

    ``localdata/source_health/odds_vocabulary/<day>+oddspapi.json`` holds
    the /markets catalog EXACTLY as served (id -> name / marketType /
    period / handicap / playerProp / outcomes), so a future classification
    change is rebuilt from captured evidence, never from guesswork. Content
    -deduped: when the served vocabulary is byte-identical to the newest
    existing snapshot, no new file is written ("unchanged"), so an idle
    catalog does not bloat the store. Provider data only - never
    credentials, never request URLs.
    """
    if not catalog_entries:
        return "absent"
    vdir = OUT_DIR / "source_health" / "odds_vocabulary"
    vdir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(
        json.dumps(catalog_entries, sort_keys=True).encode("utf-8")
    ).hexdigest()
    for path in sorted(vdir.glob("*+oddspapi.json")):
        try:
            previous = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if previous.get("digest") == digest:
            return "unchanged"
    payload = {
        "schema": 1,
        "source": "oddspapi",
        "day": str(day)[:10],
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "digest": digest,
        "catalog_size": len(catalog_entries),
        "markets": dict(sorted(catalog_entries.items())),
    }
    path = vdir / f"{str(day)[:10]}+oddspapi.json"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(path)
    return "written"


def _persist_market_census(day: str, census: dict, parse_skips: dict,
                           samples: list, catalog_entries: dict,
                           catalog_labels: dict) -> Path:
    """Persist the durable market-id census for the month.

    The enumeration of distinct market_id / type / label triples actually
    present in payloads previously existed only in the run log (masked by
    secret scrubbing on top). Persisting it makes the mapping auditable from
    the artefact alone: which ids the catalog classified, which are
    explicitly unsupported, which remain unknown, and the provider tuples
    behind unresolved 1X2 outcomes. Provider data only - never credentials.
    """
    path = _census_path(day)
    markets: dict[str, dict] = {}
    try:
        previous = json.loads(path.read_text())
        if isinstance(previous, dict) and previous.get("markets"):
            markets = dict(previous["markets"])
    except (OSError, ValueError):
        pass
    for mid, entry in census.items():
        label = catalog_labels.get(mid)
        catalog_entry = catalog_entries.get(mid) or {}
        markets[mid] = {
            "count": int(entry["count"]),
            "type": entry.get("type"),
            "label": label,
            "catalog": mid in catalog_entries,
            "period": catalog_entry.get("period"),
            "handicap": catalog_entry.get("handicap"),
            "market_type": catalog_entry.get("marketType"),
        }
    payload = {
        "schema": 1,
        "source": "oddspapi",
        "month": str(day)[:7],
        "last_run": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "catalog_size": len(catalog_entries),
        "markets": dict(sorted(markets.items())),
        "parse_skips": _classify_parse_skips(parse_skips),
        "unresolved_1x2_samples": samples[:20],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(path)
    return path


def _migrate_header(path: Path) -> None:
    """Rewrite an existing store whose header predates a new column.

    Appending wider rows to a narrower header silently shifts every value
    one column left for any later reader, so the file is rewritten (atomic
    tmp + replace) with the current header and blanks for the new fields.
    No row is dropped and no value is changed.
    """
    if not path.exists():
        return
    try:
        with gzip.open(path, "rt", newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            existing_header = list(reader.fieldnames or [])
            if existing_header == COLUMNS:
                return
            rows = [dict(r) for r in reader]
    except (OSError, csv.Error, EOFError):
        return
    tmp = path.with_suffix(path.suffix + ".tmp")
    with gzip.open(tmp, "wt", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in COLUMNS})
    tmp.replace(path)


def _append_rows(rows: list[dict], day: str) -> int:
    """Append rows to the unified store, deduped on the full row (idempotent re-runs)."""
    path = _out_path(day)
    path.parent.mkdir(parents=True, exist_ok=True)
    _migrate_header(path)
    # Stamp the generation on the way out so no write path can produce an
    # unmarked row. Migration deliberately leaves pre-existing rows blank.
    rows = [{**r, "schema_version": SCHEMA_VERSION} for r in rows]
    # Red-team F7 (fixed 2026-08-05): dedupe key EXCLUDES the timestamp
    # columns so re-capturing the same price does not append an unbounded
    # duplicate row per run. A genuinely changed price still appends.
    #
    # schema_version is deliberately IN the dedupe key: a corrected row must
    # never be suppressed because a row from the broken generation happens to
    # collide with it. Invalidation beats idempotence here.
    DEDUP_COLS = [c for c in COLUMNS if c not in _STAMP_COLS]
    seen: set[tuple] = set()
    if path.exists():
        with gzip.open(path, "rt", newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                seen.add(tuple(str(r.get(k) or "") for k in DEDUP_COLS))
    added = 0
    fresh = []
    for r in rows:
        key = tuple(str(r.get(k) or "") for k in DEDUP_COLS)
        if key in seen:
            continue
        seen.add(key)
        fresh.append(r)
        added += 1
    if fresh:
        with gzip.open(path, "at", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNS)
            if path.stat().st_size == 0:
                w.writeheader()
            for r in fresh:
                w.writerow({k: r.get(k) for k in COLUMNS})
    return added


def capture(day: str, max_fixtures: int = 20) -> dict:
    """Bounded capture for one day. Returns a stats dict; never raises."""
    stats = {"keys": 0, "fixtures": 0, "matched": 0, "rows": 0, "added": 0,
             "errors": [], "markets": {}}
    try:
        keys = api_keys()
        stats["keys"] = len(keys)
        if not keys:
            stats["errors"].append("no ODDSPAPI_API_KEYS configured")
            return stats
        fixtures = fetch_fixtures(day) or []
        stats["fixtures"] = len(fixtures)
        type_map = load_market_type_map()
        catalog = market_catalog()
        catalog_entries = market_catalog_entries()
        # The day's slate fixtures go first (stable order): the bounded budget
        # must price picks before it prices enhancement-only coverage. On
        # 2026-10-03 the provider-ordered first 20 fixtures contained no slate
        # fixture at all, which is why even healthy rows landed in
        # fixture_key_miss.
        fixtures, slate_n = _prioritise_slate_fixtures(fixtures, day)
        stats["slate_priority_fixtures"] = slate_n
        # Market-id census: every id actually present in the payloads, with
        # its classification and catalog label, persisted for the month. This
        # is the durable enumeration of market_id / type / label triples that
        # the run log previously showed only partially (and masked).
        census: dict[str, dict] = {}
        unresolved_samples: list = []
        for fx in fixtures[:max_fixtures]:
            fid = str(fx.get("fixtureId") or fx.get("id") or "")
            if not fid:
                continue
            try:
                odds = fetch_odds(fid)
            except Exception as exc:  # noqa: BLE001 - fail-soft
                stats["errors"].append(f"fetch {fid}: {type(exc).__name__}")
                continue
            if odds:
                books = (odds or {}).get("bookmakerOdds") or {}
                for _b, bd in books.items():
                    if not isinstance(bd, dict):
                        continue
                    for mid in (bd.get("markets") or {}).keys():
                        mid_s = str(mid)
                        slot = census.setdefault(
                            mid_s, {"count": 0, "type": type_map.get(mid_s)})
                        slot["count"] += 1
            # The /odds payload observed on 2026-10-03 carried no participant
            # names, so every emitted row was unjoinable. The /fixtures record
            # we already hold is the identity of record; pass it through and
            # fail closed when neither endpoint names the teams.
            parse_stats: dict = {}
            rows = rows_from_odds_response(
                odds,
                market_type_map=type_map,
                home=fx.get("participant1Name"),
                away=fx.get("participant2Name"),
                stats=parse_stats,
                market_catalog=catalog_entries,
            ) if odds else []
            for reason, count in parse_stats.items():
                if reason == "_unresolved_1x2_samples":
                    unresolved_samples.extend(count or [])
                    continue
                skips = stats.setdefault("parse_skips", {})
                skips[reason] = int(skips.get(reason) or 0) + int(count)
            if rows:
                stats["matched"] += 1
            stats["rows"] += len(rows)
            for r in rows:
                m = str(r.get("market") or "?")
                stats["markets"][m] = stats["markets"].get(m, 0) + 1
            stats["added"] += _append_rows(rows, day)
        # Durable market census: the distinct market ids the payloads
        # actually carried, their classification and catalog label, the
        # expected-vs-loss split of the parse skips, and the provider tuples
        # behind unresolved 1X2 outcomes. Written even when no rows were
        # emitted - a zero-yield capture is exactly when the census matters.
        try:
            census_path = _persist_market_census(
                day, census, stats.get("parse_skips") or {},
                unresolved_samples, catalog_entries, catalog)
            stats["market_census"] = str(census_path.name)
            stats["market_census_distinct"] = len(census)
            stats["parse_skips_classified"] = _classify_parse_skips(
                stats.get("parse_skips") or {})
        except Exception as exc:  # noqa: BLE001 - census must never break capture
            stats["errors"].append(f"census: {type(exc).__name__}")
        try:
            stats["odds_vocabulary"] = _persist_vocabulary_snapshot(day, catalog_entries)
        except Exception as exc:  # noqa: BLE001 - vocabulary must never break capture
            stats["errors"].append(f"vocabulary: {type(exc).__name__}")
        return stats
    except Exception as exc:  # noqa: BLE001 - never raises
        stats["errors"].append(f"capture: {type(exc).__name__}: {exc}")
        return stats


def self_test() -> int:
    """Offline self-test of the write path with a synthetic payload."""
    failures: list[str] = []

    def check(label: str, cond: bool) -> None:
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        if not cond:
            failures.append(label)

    sample = {
        "fixtureId": "fx_test_1",
        "participant1Name": "Halmstads BK",
        "participant2Name": "IK Sirius",
        "startTime": "2026-08-03T17:00:00Z",
        "tournamentName": "Allsvenskan",
        "categoryName": "Sweden",
        "bookmakerOdds": {
            "Pinnacle": {"markets": {
                "101": {"outcomes": {
                    "o1": {"players": {"0": {"bookmakerOutcomeId": "home", "price": 2.10}}},
                    "ox": {"players": {"0": {"bookmakerOutcomeId": "draw", "price": 3.40}}},
                    "o2": {"players": {"0": {"bookmakerOutcomeId": "away", "price": 3.25}}},
                }},
                "103": {"outcomes": {
                    "b1": {"players": {"0": {"name": "Yes", "price": 1.95}}},
                    "b2": {"players": {"0": {"name": "No", "price": 1.80}}},
                }},
                "108": {"outcomes": {
                    "d1": {"players": {"0": {"name": "HomeOrDraw", "price": 1.05}}},
                    "d2": {"players": {"0": {"name": "HomeOrAway", "price": 1.02}}},
                }},
                "115": {"outcomes": {
                    "t1": {"players": {"0": {"name": "Halmstads BK Over 1.5", "price": 1.30}}},
                    "t2": {"players": {"0": {"name": "IK Sirius Under 1.5", "price": 2.10}}},
                }},
                "107": {"outcomes": {
                    "t3": {"players": {"0": {"name": "Over 2.5", "price": 1.85}}},
                }},
            }},
        },
    }
    rows = rows_from_odds_response(sample, market_type_map={
        "101": "1x2", "103": "btts", "108": "double_chance",
        "115": "team_totals", "107": "totals",
    })
    check("10 rows parsed (3x 1x2 + 2x btts + 2x dc + 2x team_totals + 1x totals)",
          len(rows) == 10)
    markets = {(r["market"], r["selection"]) for r in rows}
    check("1x2 home/draw/away", {("1x2", "home"), ("1x2", "draw"), ("1x2", "away")} <= markets)
    check("btts yes/no", {("btts", "yes"), ("btts", "no")} <= markets)
    check("double chance 1x/12", {("dc", "1x"), ("dc", "12")} <= markets)
    check("team totals tt_home_1.5 over", ("tt_home_1.5", "over") in markets)
    check("team totals tt_away_1.5 under", ("tt_away_1.5", "under") in markets)
    check("totals ou_2.5 over", ("ou_2.5", "over") in markets)
    # schema_version is a property of the STORE, stamped on write, so the
    # parser is not expected to supply it. Everything else must be present.
    _PARSER_COLUMNS = [c for c in COLUMNS if c != "schema_version"]
    check("unified schema columns",
          all(set(_PARSER_COLUMNS) <= set(r.keys()) for r in rows))
    check("all source=oddspapi", all(r["source"] == "oddspapi" for r in rows))

    # write-path: append + dedupe
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        # redirect OUT_DIR
        global OUT_DIR
        _orig = OUT_DIR
        OUT_DIR = Path(td)
        try:
            added1 = _append_rows(rows, "2026-08-03")
            added2 = _append_rows(rows, "2026-08-03")
            with gzip.open(_out_path("2026-08-03"), "rt", newline="",
                           encoding="utf-8") as fh:
                stored = [dict(r) for r in csv.DictReader(fh)]
        finally:
            OUT_DIR = _orig
        check("append adds 10 then dedupes to 0", added1 == 10 and added2 == 0)
        check("every stored row carries the current generation",
              bool(stored) and all(
                  r.get("schema_version") == str(SCHEMA_VERSION) for r in stored))

    if failures:
        print(f"self-test: FAIL ({len(failures)} failures)")
        return 1
    print("self-test: PASS (0 failures)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    ap.add_argument("--max-fixtures", type=int, default=20)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    stats = capture(args.date, args.max_fixtures)
    print(json.dumps(stats, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

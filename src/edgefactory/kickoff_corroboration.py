"""Strict kickoff corroboration and timezone resolution engine.

Separates inferred clock conversions from verified authoritative kickoffs.
A bare clock from BetExplorer (or any provider) is never promoted to
an authoritative verified aware instant based on an assumed or guessed timezone.

Promotion to `witness_corroborated_aware_iso` requires:
  1. Validated fixture identity matching (home, away, date/calendar proximity).
  2. Independent, non-empty, recognized witness source:
     - Normalizes source family.
     - Strictly rejects circular self-corroboration (e.g. betexplorer vs betexplorer_odds).
     - Strictly rejects unrecognized, empty, or whitespace sources.
  3. Finite, positive tolerance window (e.g. <= 15 minutes, finite numbers only).
  4. Explicit aware ISO string from witness matching the fixture instant within tolerance.
  5. Mandatory comparison: comparison instant (assumed_fixture_utc or parsed fixture clock)
     is required for corroboration; missing or unparseable fixture clock fails closed.

For DST transitions (e.g. Europe/Prague spring forward gap or fall back fold),
conversions without explicit fold/gap evidence fail closed as ambiguous.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import re
import zlib
from datetime import date, datetime, time, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from edgefactory.identity import source_team_key, squad_marker_mismatch

TZ_UTC = timezone.utc
TZ_SAST = ZoneInfo("Africa/Johannesburg")
TZ_PRAGUE = ZoneInfo("Europe/Prague")
TZ_FIXED_UTC_PLUS_1 = timezone(datetime.fromisoformat("2026-01-01T01:00:00+01:00").utcoffset())

# Lineage families: canonical family mapping to prevent alias evasion
SOURCE_FAMILIES: dict[str, str] = {
    "betexplorer": "betexplorer",
    "betexplorer_odds": "betexplorer",
    "betexplorer_match": "betexplorer",
    "betexplorer_detail": "betexplorer",
    "betexplorerodds": "betexplorer",
    "theoddsapi": "theoddsapi",
    "the_odds_api": "theoddsapi",
    "theodds_api": "theoddsapi",
    "oddspapi": "oddspapi",
    "forebet": "forebet",
    "scoutingstats": "scoutingstats",
    "scouting_stats": "scoutingstats",
    "statarea": "statarea",
    "stat_area": "statarea",
    "vitibet": "vitibet",
    "bzzoiro": "bzzoiro",
    "pinnacle": "pinnacle",
    "betway": "betway",
    "warehouse": "warehouse",
    "warehouse_schedule": "warehouse",
}

MAX_PERMITTED_TOLERANCE_MINUTES = 30.0


def normalize_source_family(src: object) -> str | None:
    """Normalize a source string to its canonical lineage family.

    Strictly fails closed: returns None if the source is not in the recognized
    canonical lineage mapping.
    """
    if not src or not isinstance(src, str):
        return None
    # Normalize hyphens and spaces to underscores, then strip invalid characters
    cleaned = src.strip().lower()
    cleaned = re.sub(r"[\s\-]+", "_", cleaned)
    cleaned = re.sub(r"[^a-z0-9_]", "", cleaned)
    if not cleaned:
        return None
    # Check normalized form, and also compacted form (without underscores)
    compacted = cleaned.replace("_", "")
    return SOURCE_FAMILIES.get(cleaned) or SOURCE_FAMILIES.get(compacted)


def interpret_betexplorer_data_dt(
    data_dt: list[int] | tuple[int, ...],
    *,
    mode: str = "fixed_utc_plus_1"
) -> tuple[datetime | None, str]:
    """Evaluate a BetExplorer data_dt tuple [DD, MM, YYYY, HH, MM].

    mode:
      - 'fixed_utc_plus_1': fixed UTC+1 offset.
      - 'europe_prague': Prague local time.
        Strictly fails closed on DST nonexistent gap (spring forward) or ambiguous
        repeated fold (autumn fall back) unless explicitly disambiguated.
    """
    if not isinstance(data_dt, (list, tuple)) or len(data_dt) != 5:
        return None, "invalid_shape"

    dd, mm, yyyy, hh, minute = data_dt
    try:
        if mode == "fixed_utc_plus_1":
            local_dt = datetime(yyyy, mm, dd, hh, minute, 0, tzinfo=TZ_FIXED_UTC_PLUS_1)
            utc_dt = local_dt.astimezone(TZ_UTC)
            return utc_dt, "inferred_fixed_utc_plus_1"
        elif mode == "europe_prague":
            # Test for DST transition ambiguity or nonexistence in Europe/Prague
            # In Python, fold=0 and fold=1 allow detecting folds and gaps.
            dt0 = datetime(yyyy, mm, dd, hh, minute, 0, fold=0, tzinfo=TZ_PRAGUE)
            dt1 = datetime(yyyy, mm, dd, hh, minute, 0, fold=1, tzinfo=TZ_PRAGUE)

            # Check for gap (nonexistent local time):
            # If round-trip through UTC produces a different local time, it is in a gap
            utc0 = dt0.astimezone(TZ_UTC)
            if utc0.astimezone(TZ_PRAGUE).replace(tzinfo=None) != datetime(yyyy, mm, dd, hh, minute, 0):
                return None, "dst_gap_nonexistent_local_time"

            # Check for fold (ambiguous local time):
            if dt0.utcoffset() != dt1.utcoffset():
                return None, "dst_fold_ambiguous_local_time"

            return utc0, "inferred_europe_prague"
        else:
            return None, "unknown_mode"
    except Exception:
        return None, "invalid_date_values"


def verify_fixture_identity(
    fixture_home: object,
    fixture_away: object,
    witness_home: object,
    witness_away: object
) -> bool:
    """Validate that fixture and witness identify the exact same match."""
    fh_key = source_team_key(fixture_home)
    fa_key = source_team_key(fixture_away)
    wh_key = source_team_key(witness_home)
    wa_key = source_team_key(witness_away)

    if not (fh_key and fa_key and wh_key and wa_key):
        return False

    # Check for squad/age/women marker mismatches
    if squad_marker_mismatch(fixture_home, witness_home) or squad_marker_mismatch(fixture_away, witness_away):
        return False

    return fh_key == wh_key and fa_key == wa_key


def corroborate_kickoff_witness(
    fixture_clock: str | None,
    witness_kickoff_utc: str | datetime | None,
    *,
    witness_source: str,
    fixture_source: str = "betexplorer",
    assumed_fixture_utc: datetime | None = None,
    tolerance_minutes: float = 5.0,
    fixture_home: object = None,
    fixture_away: object = None,
    witness_home: object = None,
    witness_away: object = None
) -> dict:
    """Corroborate a fixture's timing against an independent schedule witness.

    Fails closed on:
      - Missing or unverified comparison instant (`assumed_fixture_utc` is required).
      - Invalid fixture identity (home/away mismatch or missing).
      - Missing, empty, or circular witness source.
      - Naive, missing, or unparseable witness kickoff timestamp.
      - Non-finite, negative, or excessive tolerance.
      - Timing discrepancy exceeding tolerance window.
    """
    out = {
        "corroborated": False,
        "authoritative_kickoff_utc": None,
        "provenance": "unverified_kickoff_timezone",
        "reason": "",
        "witness_source": str(witness_source).strip() if witness_source else "",
        "witness_family": None
    }

    # 1. Require validated fixture identity
    if not (fixture_home and fixture_away and witness_home and witness_away):
        out["reason"] = "missing_fixture_identity"
        return out
    if not verify_fixture_identity(fixture_home, fixture_away, witness_home, witness_away):
        out["reason"] = "fixture_identity_mismatch"
        return out

    # 2. Source lineage normalization & circularity guard
    fix_fam = normalize_source_family(fixture_source)
    wit_fam = normalize_source_family(witness_source)

    if not fix_fam:
        out["reason"] = "unrecognized_or_empty_fixture_source"
        return out

    if not wit_fam:
        out["reason"] = "unrecognized_or_empty_witness_source"
        return out
    out["witness_family"] = wit_fam

    if fix_fam == wit_fam:
        out["reason"] = "circular_corroboration_rejected"
        return out

    # 3. Tolerance validation (must be finite, non-negative, <= MAX)
    try:
        tol = float(tolerance_minutes)
        if not math.isfinite(tol) or tol < 0 or tol > MAX_PERMITTED_TOLERANCE_MINUTES:
            out["reason"] = "invalid_tolerance"
            return out
    except (TypeError, ValueError):
        out["reason"] = "invalid_tolerance"
        return out

    # 4. Mandatory comparison instant: assumed_fixture_utc must be provided and aware
    if assumed_fixture_utc is None:
        out["reason"] = "missing_comparison_instant"
        return out
    if not isinstance(assumed_fixture_utc, datetime) or assumed_fixture_utc.tzinfo is None:
        out["reason"] = "comparison_instant_not_aware_datetime"
        return out
    af_utc = assumed_fixture_utc.astimezone(TZ_UTC)

    # 5. Witness timestamp validation: must be aware UTC
    if witness_kickoff_utc is None:
        out["reason"] = "witness_kickoff_missing"
        return out

    w_dt: datetime | None = None
    if isinstance(witness_kickoff_utc, datetime):
        if witness_kickoff_utc.tzinfo is None:
            out["reason"] = "witness_kickoff_naive"
            return out
        w_dt = witness_kickoff_utc.astimezone(TZ_UTC)
    elif isinstance(witness_kickoff_utc, str):
        try:
            parsed = datetime.fromisoformat(witness_kickoff_utc.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                out["reason"] = "witness_kickoff_naive"
                return out
            w_dt = parsed.astimezone(TZ_UTC)
        except Exception:
            out["reason"] = "witness_kickoff_unparseable"
            return out
    else:
        out["reason"] = "witness_kickoff_invalid_type"
        return out

    # 6. Compare instants within tolerance
    diff_minutes = abs((af_utc - w_dt).total_seconds()) / 60.0
    if diff_minutes > tol:
        out["reason"] = f"tolerance_exceeded_diff_{diff_minutes:.1f}_min"
        return out

    # Verified!
    out["corroborated"] = True
    out["authoritative_kickoff_utc"] = w_dt.isoformat()
    out["provenance"] = "witness_corroborated_aware_iso"
    out["reason"] = f"witnessed_by_{wit_fam}"
    return out


def parse_iso_utc(ts: object) -> datetime | None:
    """Parse an ISO-8601 string into an aware UTC datetime, or None."""
    if not ts or not isinstance(ts, str):
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return None
        return dt.astimezone(TZ_UTC)
    except Exception:
        return None


def decision_cutoff_utc(day: str) -> datetime | None:
    """The explicit 09:00 Johannesburg decision on the ledger's decision day."""
    try:
        return datetime.combine(date.fromisoformat(day), time(9), TZ_SAST).astimezone(TZ_UTC)
    except (TypeError, ValueError):
        return None


def _schedule_archive_rows(reader, *, schedule_source):
    for ordinal, row in enumerate(reader, 1):
        if not schedule_source:
            yield ordinal, None, row
            continue
        # Capture keeps one current prediction per fixture. Only its clocks
        # retain history, so schedule evidence cannot change consensus units.
        history = json.loads(row.get("schedule_history") or "[]")
        if not isinstance(history, list) or any(not isinstance(r, dict) for r in history):
            raise ValueError("invalid retained source schedule history")
        yield ordinal, None, row
        for index, previous in enumerate(history):
            yield ordinal, index, previous


def load_schedule_witnesses(fixtures: list[dict], *, localdata: Path) -> tuple[dict, list[dict]]:
    """Read existing provider archives, never cards, warehouse labels or the network.

    Timestamped ScoutingStats/Vitibet response rows are schedule witnesses too;
    no generated pick, warehouse label, mtime or research ledger is consulted.
    Legacy source CSV rows without capture/origin receipts cannot corroborate.
    OddsPapi kickoff is provider startTime (oddspapi_odds.parse_odds_response).
    Legacy TheOddsAPI rows may inherit pick kickoff: require an explicit
    provider_commence_time origin before treating those rows as witnesses.
    The already-fetched OddsPapi fixture board supplies the same provider
    startTime without requiring an odds purchase for the fixture. Receipts bind
    immutable input bytes and the original CSV row or board JSON location.
    """
    wanted = {(source_team_key(f.get("home")), source_team_key(f.get("away")))
              for f in fixtures}
    # Capture writers partition by fixture decision day. Only months intersecting
    # the page's +/-1 calendar-day identity window can contain relevant rows.
    # Unknown page dates keep the conservative all-files behaviour.
    months = set()
    for fixture in fixtures:
        try:
            raw = fixture.get("data_dt")
            when = (date(raw[2], raw[1], raw[0]) if isinstance(raw, (list, tuple)) and len(raw) == 5
                    else date.fromisoformat(str(fixture.get("date"))))
            months.update((when + timedelta(days=d)).strftime("%Y-%m") for d in (-1, 0, 1))
        except (TypeError, ValueError, OverflowError):
            months.clear()
            break
    by_pair: dict[tuple, list[dict]] = {}
    receipts = []
    team_keys: dict[str, str] = {}
    for provider in ("oddspapi", "theoddsapi", "scoutingstats", "vitibet"):
        schedule_source = provider in ("scoutingstats", "vitibet")
        prefix = provider if schedule_source else f"{provider}_odds"
        for path in sorted(localdata.glob(f"{prefix}_????-??.csv.gz" if schedule_source else f"{prefix}_*.csv.gz")):
            month = re.fullmatch(rf"{prefix}_(\d{{4}}-\d{{2}})\.csv\.gz", path.name)
            canonical_month = month[1] if month else None
            try:
                if canonical_month:
                    date.fromisoformat(canonical_month + "-01")
            except ValueError:
                canonical_month = None
            if months and canonical_month and canonical_month not in months:
                continue
            # Bind the digest and parser to the SAME bytes, even if a capture
            # atomically replaces this archive while the audit is running.
            receipt = {"file": path.name, "source_family": provider, "rejections": {}}
            try:
                archive_bytes = path.read_bytes()
                receipt = {"file": path.name, "sha256": hashlib.sha256(archive_bytes).hexdigest(),
                           "source_family": provider, "rows_scanned": 0,
                           "matched_identity_rows": 0, "witness_records": 0,
                           "rejections": {}}
                seen = set()
                file_witnesses = {}
                with gzip.open(io.BytesIO(archive_bytes), "rt", newline="") as handle:
                    for ordinal, history_index, row in _schedule_archive_rows(
                            csv.DictReader(handle), schedule_source=schedule_source):
                        receipt["rows_scanned"] += 1
                        home, away = row.get("home", ""), row.get("away", "")
                        for name in (home, away):
                            if name not in team_keys:
                                team_keys[name] = source_team_key(name)
                        pair = (team_keys[home], team_keys[away])
                        if not all(pair) or pair not in wanted:
                            continue
                        receipt["matched_identity_rows"] += 1
                        reason = None
                        if normalize_source_family(row.get("source")) != provider:
                            reason = "archive_source_mismatch"
                        elif not schedule_source and (row.get("source_type") != "odds" or row.get("sport") != "soccer"):
                            reason = "unsupported_record_contract"
                        elif provider == "theoddsapi" and row.get("kickoff_origin") != "provider_commence_time":
                            reason = "provider_kickoff_origin_unproven"
                        if provider == "theoddsapi" and reason is None:
                            # A provider clock with pick-derived participants is not
                            # an independently identified event. Retain both origins.
                            if (row.get("fixture_identity_origin") != "provider_participants"
                                    or not str(row.get("provider_event_id") or "").strip()
                                    or parse_iso_utc(row.get("provider_commence_time")) != parse_iso_utc(row.get("kickoff"))):
                                reason = "provider_event_identity_or_clock_unproven"
                        if schedule_source and (row.get("kickoff_origin") != "provider_explicit_offset"
                                                or row.get("fixture_identity_origin") != "provider_participants"):
                            reason = "provider_schedule_origin_unproven"
                        kickoff = parse_iso_utc(row.get("kickoff"))
                        observed = parse_iso_utc(row.get("captured_at"))
                        if reason is None and (kickoff is None or observed is None):
                            reason = "invalid_witness_timestamp"
                        if reason:
                            counts = receipt["rejections"]
                            counts[reason] = counts.get(reason, 0) + 1
                            continue
                        key = (home, away, kickoff, observed)
                        if key in seen:
                            continue  # outcomes/books repeat the same schedule observation
                        seen.add(key)
                        record = {"source": provider, "home": home, "away": away,
                                  "league": row.get("league"),
                                  "kickoff_utc": kickoff.isoformat(),
                                  "observed_at_utc": observed.isoformat(),
                                  "file": path.name, "file_sha256": receipt["sha256"],
                                  "csv_data_row": ordinal,
                                  "row_sha256": hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest(),
                                  "kickoff_origin": ("provider_explicit_offset" if schedule_source else
                                                     "provider_startTime" if provider == "oddspapi"
                                                     else "provider_commence_time"),
                                  "fixture_identity_origin": row.get("fixture_identity_origin"),
                                  "provider_event_id": row.get("provider_event_id"),
                                  "provider_commence_time": row.get("provider_commence_time")}
                        if schedule_source:
                            record["schedule_row"] = row
                            if history_index is not None:
                                record["csv_history_index"] = history_index
                        file_witnesses.setdefault(pair, []).append(record)
                        receipt["witness_records"] += 1
                for pair, records in file_witnesses.items():
                    by_pair.setdefault(pair, []).extend(records)
            except (OSError, EOFError, ValueError, csv.Error, zlib.error):
                receipt["error"] = "unreadable_schedule_archive"
                receipt["witness_records"] = 0
            receipts.append(receipt)
    # Capture already retains the provider board, including fixtures whose odds
    # window has not opened or whose odds request was budget-deferred. Schedule
    # corroboration must not depend on buying another provider's odds first.
    path = localdata / "oddspapi_fixture_state.json"
    if path.exists():
        try:
            board_bytes = path.read_bytes()
            payload = json.loads(board_bytes)
            receipt = {"file": path.name, "sha256": hashlib.sha256(board_bytes).hexdigest(),
                       "source_family": "oddspapi", "rows_scanned": 0,
                       "matched_identity_rows": 0, "witness_records": 0, "rejections": {}}
            receipts.append(receipt)
            boards = payload.get("boards") if isinstance(payload, dict) else None
            for board_day, board in (boards or {}).items() if isinstance(boards, dict) else ():
                if not isinstance(board, dict) or not isinstance(board.get("fixtures"), list):
                    continue
                try:
                    if date.fromisoformat(board_day).isoformat() != board_day:
                        continue
                except (TypeError, ValueError):
                    continue
                observed = parse_iso_utc(board.get("fetched_at"))
                if observed is None:
                    continue
                for ordinal, row in enumerate(board["fixtures"]):
                    receipt["rows_scanned"] += 1
                    if not isinstance(row, dict):
                        continue
                    home, away = row.get("participant1Name"), row.get("participant2Name")
                    event_id = row.get("fixtureId")
                    if (not all(isinstance(v, str) and v.strip() for v in (home, away, event_id))
                            or (source_team_key(home), source_team_key(away)) not in wanted):
                        continue
                    receipt["matched_identity_rows"] += 1
                    kickoff = parse_iso_utc(row.get("startTime"))
                    if kickoff is None:
                        continue
                    record = {"source": "oddspapi", "home": home, "away": away,
                              "kickoff_utc": kickoff.isoformat(), "observed_at_utc": observed.isoformat(),
                              "file": path.name, "file_sha256": receipt["sha256"],
                              "json_pointer": f"/boards/{board_day}/fixtures/{ordinal}",
                              "board_fetched_at": board["fetched_at"], "board_fixture": row,
                              "row_sha256": hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest(),
                              "kickoff_origin": "provider_startTime", "provider_event_id": event_id,
                              "fixture_identity_origin": "provider_participants"}
                    by_pair.setdefault((source_team_key(home), source_team_key(away)), []).append(record)
                    receipt["witness_records"] += 1
        except (OSError, ValueError, TypeError):
            pass  # A missing/corrupt cache cannot erase existing archive witnesses.
    return by_pair, receipts


def resolve_schedule_witness(fixture: dict, cutoff: datetime, witnesses: dict) -> dict:
    """Corroborate preserved page evidence against independent, as-of witnesses.

    Try BOTH documented interpretations without selecting a site-wide default.
    Legacy container/pick dates are never substituted for the missing page date.
    Any conflicting same-fixture pre-cutoff schedule records leave it unresolved.
    A witness found after cutoff cannot retroactively establish replay eligibility.
    """
    out = {"status": "unresolved", "reason": "missing_raw_page_datetime",
           "kickoff_utc": None, "provenance": None, "witnesses": [],
           "interpretations": [], "late_witness_records": 0}
    raw = fixture.get("data_dt")
    if not isinstance(raw, (list, tuple)) or len(raw) != 5 or any(type(v) is not int for v in raw):
        return out
    dd, mm, year, hour, minute = raw
    try:
        raw_date = date(year, mm, dd).isoformat()
    except (ValueError, OverflowError):
        out["reason"] = "invalid_raw_page_datetime"
        return out
    if fixture.get("kickoff_date") not in (None, raw_date):
        out["reason"] = "raw_page_date_conflict"
        return out
    if fixture.get("kickoff") != f"{hour:02d}:{minute:02d}":
        out["reason"] = "raw_page_clock_conflict"
        return out
    interpretations = []
    for mode in ("fixed_utc_plus_1", "europe_prague"):
        instant, label = interpret_betexplorer_data_dt(raw, mode=mode)
        if instant is not None:
            interpretations.append((instant, label))
    if not interpretations:
        out["reason"] = "invalid_raw_page_datetime"
        return out
    pair = (source_team_key(fixture.get("home")), source_team_key(fixture.get("away")))
    matches = []
    for witness in witnesses.get(pair, []):
        if not verify_fixture_identity(fixture.get("home"), fixture.get("away"),
                                       witness["home"], witness["away"]):
            continue
        kickoff = parse_iso_utc(witness["kickoff_utc"])
        observed = parse_iso_utc(witness["observed_at_utc"])
        # Separate repeated fixtures on other dates; not a team-only join.
        if kickoff is None or abs((kickoff.date() - date.fromisoformat(raw_date)).days) > 1:
            continue
        if observed is None or observed >= kickoff:
            continue
        if observed >= cutoff:
            out["late_witness_records"] += 1
            continue
        matches.append(witness)
    if not matches:
        out["reason"] = "no_independent_pre_cutoff_witness"
        return out
    # Never choose whichever provider/observation happens to fit our hypothesis.
    if len({w["kickoff_utc"] for w in matches}) != 1:
        out["reason"] = "conflicting_schedule_witnesses"
        out["witnesses"] = matches
        return out
    accepted = []
    modes = set()
    for witness in matches:
        for assumed, label in interpretations:
            result = corroborate_kickoff_witness(
                fixture.get("kickoff"), witness["kickoff_utc"],
                witness_source=witness["source"], assumed_fixture_utc=assumed,
                fixture_home=fixture.get("home"), fixture_away=fixture.get("away"),
                witness_home=witness["home"], witness_away=witness["away"],
                tolerance_minutes=5.0)
            if result["corroborated"]:
                if witness not in accepted:
                    accepted.append(witness)
                modes.add(label)
    if not accepted:
        out["reason"] = "page_clock_witness_disagreement"
        out["witnesses"] = matches
        return out
    out.update(status="corroborated", reason="independent_pre_cutoff_schedule_witness",
               kickoff_utc=accepted[0]["kickoff_utc"],
               provenance="witness_corroborated_aware_iso", witnesses=accepted,
               interpretations=sorted(modes))
    return out

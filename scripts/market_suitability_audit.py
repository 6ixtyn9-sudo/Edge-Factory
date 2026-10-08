#!/usr/bin/env python3
"""Read-only prediction-to-outcome audit from retained local ledgers.

The only files this script writes are the requested report/CSV outputs in the
selected output directory. It does not call providers, load or run a prediction
model, change operational state, or settle new results.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
LOCAL_TZ = ZoneInfo("Africa/Johannesburg")

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from audit_recent_picks import (  # noqa: E402
    load_archived_picks_with_receipt,
)
from edgefactory.identity import source_team_key  # noqa: E402
from edgefactory.util import ledger_team_key  # noqa: E402


SELECTION_COLUMNS = [
    "selection_id",
    "fixture_id",
    "record_type",
    "population",
    "fixture_date",
    "home",
    "away",
    "market",
    "selection_side",
    "selected_team",
    "family",
    "primary_rule",
    "supporting_rule_signals",
    "other_snapshot_rule_signals",
    "decision_probability_pct",
    "decision_probability_field",
    "decision_time",
    "kickoff_time",
    "first_seen_time",
    "lead_minutes",
    "time_status",
    "result_status",
    "result_date",
    "score",
    "outcome_category",
    "market_1x2_result",
    "double_chance_result",
    "dnb_asian0_result",
    "asian_plus0_5_result",
    "asian_plus1_result",
    "main_send_receipt",
    "shadow_send_receipt",
    "publication_stage",
    "receipt_side_attribution",
    "ticketed",
    "ticket_leg_count",
    "linked_operational_selection_ids",
    "linked_verified_operational_selection_ids",
    "linked_archive_only_selection_ids",
    "linked_operational_side_relation",
    "linked_operational_publication_stage",
    "linked_operational_ticketed",
    "source_era",
    "model_key",
    "model_keys_seen",
    "model_version",
    "sources_used",
    "archive_snapshot_count",
    "archive_files",
    "snapshot_probability_min_pct",
    "snapshot_probability_max_pct",
    "odds_decimal",
    "bookmaker",
    "odds_source",
    "odds_captured_at",
    "price_evidence",
    "pre_kickoff_analysis_eligible",
    "exclusion_reason",
]

BREAKDOWN_COLUMNS = [
    "population",
    "dimension",
    "cell",
    "n",
    "n_scored",
    "n_pending",
    "n_ambiguous",
    "n_rescheduled",
    "n_missing_score",
    "n_excluded_time",
    "win",
    "draw",
    "loss_by_one",
    "loss_by_two_plus",
    "draw_prediction_hits",
    "draw_prediction_misses",
    "win_rate_scored",
    "avoid_defeat_n",
    "avoid_defeat_rate_scored",
    "avoid_heavy_loss_n",
    "avoid_heavy_loss_rate_scored",
    "market_1x2_win",
    "market_1x2_push",
    "market_1x2_loss",
    "double_chance_win",
    "double_chance_push",
    "double_chance_loss",
    "dnb_asian0_win",
    "dnb_asian0_push",
    "dnb_asian0_loss",
    "asian_plus0_5_win",
    "asian_plus0_5_push",
    "asian_plus0_5_loss",
    "asian_plus1_win",
    "asian_plus1_push",
    "asian_plus1_loss",
    "be_1x2_decimal_diagnostic",
    "be_double_chance_decimal_diagnostic",
    "be_dnb_asian0_decimal_diagnostic",
    "be_asian_plus0_5_decimal_diagnostic",
    "be_asian_plus1_decimal_diagnostic",
]

NOTE_COLUMNS = [
    "selection_id",
    "fixture_date",
    "fixture",
    "score",
    "market",
    "label",
    "engine",
    "promised_probability",
    "hit",
]


# -- small parsing/identity helpers -----------------------------------------
def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def parse_aware(value: Any) -> datetime | None:
    """Parse only an explicit-offset timestamp; naive times fail closed."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo is not None else None


def parse_ml_kickoff(row: dict[str, Any]) -> datetime | None:
    """Parse the three retained ML kickoff formats as SAST.

    The research ledger's kickoff strings are intentionally interpreted in
    Africa/Johannesburg, matching the prior read-only lead-time validation.
    """
    value = str(row.get("kickoff") or "").strip()
    anchor_text = str(row.get("date") or "")[:10]
    try:
        anchor = date.fromisoformat(anchor_text)
    except ValueError:
        return None

    if re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d(?::\d\d)?", value):
        try:
            return datetime.fromisoformat(value).replace(tzinfo=LOCAL_TZ)
        except ValueError:
            return None

    match = re.fullmatch(r"(\d\d)-(\d\d), (\d\d):(\d\d)", value)
    if match:
        day_num, month_num, hour, minute = map(int, match.groups())
        candidates: list[datetime] = []
        for year in (anchor.year - 1, anchor.year, anchor.year + 1):
            try:
                candidates.append(datetime(
                    year, month_num, day_num, hour, minute, tzinfo=LOCAL_TZ
                ))
            except ValueError:
                continue
        if candidates:
            return min(candidates, key=lambda item: abs((item.date() - anchor).days))
        return None

    if re.fullmatch(r"\d\d:\d\d", value):
        try:
            hour, minute = map(int, value.split(":"))
            return datetime.combine(anchor, time(hour, minute), tzinfo=LOCAL_TZ)
        except ValueError:
            return None
    return None


def norm_side(value: Any) -> str:
    return str(value or "").strip().lower()


def selection_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(row.get("date") or row.get("fixture_date") or "")[:10],
        ledger_team_key(row.get("home") or ""),
        ledger_team_key(row.get("away") or ""),
        norm_side(row.get("market") or "1x2"),
        norm_side(row.get("pick") or row.get("selection_side") or ""),
    )


def fixture_key(day: str, home: Any, away: Any) -> tuple[str, str, str]:
    return (
        str(day)[:10],
        ledger_team_key(home or ""),
        ledger_team_key(away or ""),
    )


def make_id(prefix: str, parts: Iterable[Any]) -> str:
    blob = "|".join(str(item or "") for item in parts)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}-{digest}"


def source_era(row: dict[str, Any]) -> str:
    version = str(row.get("model_version") or "unrecorded")
    sources = row.get("sources_used")
    if isinstance(sources, list):
        source_text = "+".join(sorted(str(item) for item in sources if item))
    else:
        source_text = str(sources or "unrecorded")
    return f"{version}|{source_text or 'unrecorded'}"


def rule_signals(row: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    for key in ("edge_rule", "rule", "display_rule"):
        value = str(row.get(key) or "").strip()
        if value and value not in signals:
            signals.append(value)
    for key in (
        "duplicate_rules_collapsed",
        "supporting_rules",
        "rule_signals",
        "support_rules",
    ):
        values = row.get(key)
        if isinstance(values, str):
            values = [values]
        if isinstance(values, (list, tuple, set)):
            for value in values:
                text = str(value or "").strip()
                if text and text not in signals:
                    signals.append(text)
    return signals


def row_time_status(row: dict[str, Any]) -> tuple[str, float | None]:
    decision = parse_aware(row.get("as_of"))
    kickoff = parse_aware(row.get("kickoff_utc"))
    if decision is None or kickoff is None:
        return "unverified_missing_or_naive_timestamp", None
    lead = (kickoff - decision).total_seconds() / 60.0
    if lead <= 0:
        return "post_kickoff_or_equal", lead
    return "pre_kickoff_verified", lead


def ml_time_status(row: dict[str, Any]) -> tuple[str, datetime | None, float | None]:
    decision = parse_aware(row.get("first_seen_at"))
    kickoff = parse_ml_kickoff(row)
    if decision is None or kickoff is None:
        return "unverified_missing_or_naive_timestamp", kickoff, None
    lead = (kickoff - decision).total_seconds() / 60.0
    if lead <= 0:
        return "post_kickoff_or_equal", kickoff, lead
    return "pre_kickoff_verified", kickoff, lead


def probability_band(value: Any) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if not math.isfinite(numeric) or numeric < 0 or numeric > 100:
        return "out_of_range"
    low = min(int(numeric // 10) * 10, 90)
    high = low + 10
    suffix = "100" if high == 100 else f"<{high:02d}"
    return f"{low:02d}-{suffix}"


def week_window(value: Any) -> str:
    parsed = parse_aware(value)
    if parsed is None:
        return "unknown"
    monday = parsed.date() - timedelta(days=parsed.date().weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.isoformat()}..{sunday.isoformat()}"


def _score_values(score: Any) -> tuple[int, int] | None:
    if not isinstance(score, dict):
        return None
    try:
        home = int(score.get("hs"))
        away = int(score.get("gs"))
    except (TypeError, ValueError):
        return None
    if home < 0 or away < 0:
        return None
    return home, away


def score_selection(
    home_score: int, away_score: int, side: str
) -> dict[str, str | None]:
    """Map one selected side to stored-score and five market outcomes."""
    side = norm_side(side)
    result: dict[str, str | None] = {
        "outcome_category": None,
        "market_1x2_result": None,
        "double_chance_result": None,
        "dnb_asian0_result": None,
        "asian_plus0_5_result": None,
        "asian_plus1_result": None,
    }
    if side == "draw":
        is_draw = home_score == away_score
        result["market_1x2_result"] = "win" if is_draw else "loss"
        return result
    if side == "home":
        difference = home_score - away_score
    elif side == "away":
        difference = away_score - home_score
    else:
        return result

    if difference > 0:
        category = "win"
    elif difference == 0:
        category = "draw"
    elif difference == -1:
        category = "loss_by_one"
    else:
        category = "loss_by_two_plus"
    result["outcome_category"] = category
    result["market_1x2_result"] = "win" if category == "win" else "loss"
    result["double_chance_result"] = (
        "win" if category in {"win", "draw"} else "loss"
    )
    result["dnb_asian0_result"] = {
        "win": "win",
        "draw": "push",
        "loss_by_one": "loss",
        "loss_by_two_plus": "loss",
    }[category]
    result["asian_plus0_5_result"] = result["double_chance_result"]
    result["asian_plus1_result"] = {
        "win": "win",
        "draw": "win",
        "loss_by_one": "push",
        "loss_by_two_plus": "loss",
    }[category]
    return result


def _audit_key(row: dict[str, Any]) -> tuple[str, str, str, str, str] | None:
    home = row.get("home")
    away = row.get("away")
    if not home or not away:
        match = str(row.get("match") or "")
        if " vs " not in match:
            return None
        home, away = match.split(" vs ", 1)
    selection = row.get("selection") or row.get("pick")
    if not selection:
        return None
    return (
        str(row.get("date") or "")[:10],
        ledger_team_key(home),
        ledger_team_key(away),
        norm_side(row.get("market") or "1x2"),
        norm_side(selection),
    )


# -- retained archives and evaluation stage ---------------------------------
def load_raw_pick_archives() -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    rows: list[dict[str, Any]] = []
    files_by_key: dict[str, list[str]] = defaultdict(list)
    pattern = re.compile(r"^picks_(morning_)?(\d{4}-\d\d-\d\d)\.json$")
    for path in sorted(LOCALDATA.glob("picks_*.json")):
        match = pattern.fullmatch(path.name)
        if not match:
            continue
        archive_day = match.group(2)
        data = read_json(path, [])
        if not isinstance(data, list):
            continue
        for item in data:
            if not isinstance(item, dict):
                continue
            row = dict(item)
            row.setdefault("date", archive_day)
            if str(row.get("date") or "")[:10] != archive_day:
                continue
            row["_archive_file"] = path.name
            rows.append(row)
            key = selection_key(row)
            key_text = "|".join(key)
            if path.name not in files_by_key[key_text]:
                files_by_key[key_text].append(path.name)
    return rows, files_by_key


def _row_probability(row: dict[str, Any]) -> float | None:
    value = row.get("avg_p")
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def archive_snapshot_metadata(rows: list[dict[str, Any]]) -> dict[str, Any]:
    as_of_values = [
        str(row.get("as_of")) for row in rows if row.get("as_of")
    ]
    probabilities = [
        value for value in (_row_probability(row) for row in rows)
        if value is not None
    ]
    signals = sorted({signal for row in rows for signal in rule_signals(row)})
    files = sorted({
        str(row.get("_archive_file") or "")
        for row in rows
        if row.get("_archive_file")
    })
    return {
        "archive_snapshot_count": len(rows),
        "archive_files": ";".join(files),
        "snapshot_probability_min_pct": min(probabilities) if probabilities else None,
        "snapshot_probability_max_pct": max(probabilities) if probabilities else None,
        "other_snapshot_rule_signals": signals,
        "archive_as_of_values": sorted(as_of_values),
    }


def load_evaluation_map(
    audit: dict[str, Any],
) -> dict[tuple[str, str, str, str, str], dict[str, Any]]:
    result: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for field, status in (
        ("settled_ledger", "settled"),
        ("ambiguous_examples", "ambiguous"),
        ("rescheduled_examples", "rescheduled"),
        ("unmatched_examples", "pending"),
    ):
        entries = audit.get(field, [])
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            key = _audit_key(entry)
            if key is None:
                continue
            current = dict(entry)
            current["_audit_status"] = status
            # Prefer a settled record, then a specifically classified exception.
            priority = {"settled": 0, "ambiguous": 1, "rescheduled": 2, "pending": 3}
            previous = result.get(key)
            if previous is None or priority[status] < priority[previous["_audit_status"]]:
                result[key] = current
    return result


def load_receipt_sets() -> tuple[set[tuple], set[tuple]]:
    main: set[tuple] = set()
    shadow: set[tuple] = set()
    paths = set(LOCALDATA.glob("sent_ledger_*.json"))
    paths.update(LOCALDATA.glob("shadow_sent_ledger_*.json"))
    for path in sorted(paths):
        is_shadow = path.name.startswith("shadow_sent_ledger_")
        is_main = path.name.startswith("sent_ledger_") and not is_shadow
        if not (is_main or is_shadow):
            continue
        data = read_json(path, [])
        if not isinstance(data, list):
            continue
        target = shadow if is_shadow else main
        for value in data:
            parts = str(value).split("|")
            if len(parts) < 3:
                continue
            day = parts[0][:10]
            market = parts[-1].strip().lower()
            fixture = "|".join(parts[1:-1]).strip()
            if " vs " not in fixture:
                continue
            home, away = fixture.split(" vs ", 1)
            target.add(fixture_key(day, home, away) + (market,))
    return main, shadow


def _exact_team_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def ticket_leg_count_for_selection(
    record: dict[str, Any],
    alias_counts: Counter[tuple[str, str, str, str, str]],
    exact_counts: Counter[tuple[str, str, str, str, str]],
    alias_multiplicity: Counter[tuple[str, str, str, str, str]],
) -> int:
    day = str(record.get("fixture_date") or "")[:10]
    market = norm_side(record.get("market") or "1x2")
    side = norm_side(record.get("selection_side"))
    alias_key = (
        day,
        source_team_key(record.get("home") or ""),
        source_team_key(record.get("away") or ""),
        market,
        side,
    )
    exact_key = (
        day,
        _exact_team_text(record.get("home")),
        _exact_team_text(record.get("away")),
        market,
        side,
    )
    exact_count = exact_counts.get(exact_key, 0)
    if exact_count:
        return exact_count
    if alias_multiplicity.get(alias_key, 0) == 1:
        return alias_counts.get(alias_key, 0)
    return 0


def load_ticket_counts() -> tuple[
    Counter[tuple[str, str, str, str, str]],
    Counter[tuple[str, str, str, str, str]],
]:
    counts: Counter[tuple[str, str, str, str, str]] = Counter()
    exact_counts: Counter[tuple[str, str, str, str, str]] = Counter()
    path = LOCALDATA / "auto_tickets_slice_ledger.jsonl"
    if not path.exists():
        return counts, exact_counts
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        if row.get("src") != "slip" or row.get("seeded") or row.get("shadow"):
            continue
        day = str(row.get("date") or "")[:10]
        market = "1x2"
        side = norm_side(row.get("pick"))
        key = (
            day,
            source_team_key(row.get("home") or ""),
            source_team_key(row.get("away") or ""),
            market,
            side,
        )
        exact_key = (
            day,
            _exact_team_text(row.get("home")),
            _exact_team_text(row.get("away")),
            market,
            side,
        )
        counts[key] += 1
        exact_counts[exact_key] += 1
    return counts, exact_counts


def classify_operational_status(
    row: dict[str, Any],
    audit_row: dict[str, Any] | None,
    same_day_cutoff: str,
    time_status: str,
) -> tuple[str, dict[str, Any] | None]:
    if audit_row is not None:
        return str(audit_row["_audit_status"]), audit_row
    day = str(row.get("date") or "")[:10]
    if day == str(same_day_cutoff)[:10]:
        return "same_day_cutoff_missing_score", None
    if time_status != "pre_kickoff_verified":
        return "not_score_eligible_due_time", None
    return "pending", None


def price_evidence(row: dict[str, Any], time_status: str) -> dict[str, Any]:
    """Return only the exact selected, explicit-book price stored on the row."""
    result = {
        "odds_decimal": None,
        "bookmaker": "",
        "odds_source": "",
        "odds_captured_at": "",
        "price_evidence": "",
    }
    board = row.get("price_board")
    if not isinstance(board, list):
        return result
    decision = parse_aware(row.get("as_of"))
    kickoff = parse_aware(row.get("kickoff_utc"))
    for quote in board:
        if not isinstance(quote, dict) or not quote.get("chosen"):
            continue
        if norm_side(quote.get("market")) != "1x2":
            continue
        if norm_side(quote.get("selection")) != norm_side(row.get("pick")):
            continue
        bookmaker = str(quote.get("bookmaker") or row.get("bookmaker") or "")
        source = str(quote.get("source") or row.get("odds_source") or "")
        # BetExplorer's retained label is a best-price proxy, not a named book.
        if not bookmaker or bookmaker.strip().lower() == "betexplorer_best":
            continue
        if quote.get("named_bookmaker") is not True:
            continue
        if quote.get("odds_kind") != "bookmaker":
            continue
        captured = parse_aware(quote.get("captured_at"))
        if (
            time_status != "pre_kickoff_verified"
            or decision is None
            or kickoff is None
            or captured is None
            or captured > decision
            or captured >= kickoff
        ):
            continue
        try:
            price = float(quote.get("odds"))
        except (TypeError, ValueError):
            continue
        if price <= 1:
            continue
        result.update({
            "odds_decimal": price,
            "bookmaker": bookmaker,
            "odds_source": source,
            "odds_captured_at": str(quote.get("captured_at") or ""),
            "price_evidence": "exact selected named-book 1x2 quote",
        })
        return result
    return result


def _base_record(
    *,
    record_type: str,
    population: str,
    row: dict[str, Any],
    day: str,
    market: str,
    side: str,
    family: str,
    probability_pct: Any,
    probability_field: str,
    decision_time: str,
    kickoff_time: str,
    time_status: str,
    lead_minutes: float | None,
) -> dict[str, Any]:
    home = str(row.get("home") or "")
    away = str(row.get("away") or "")
    fixture = fixture_key(day, home, away)
    side = norm_side(side)
    return {
        "selection_id": make_id("sel", (*fixture, market, side, family)),
        "fixture_id": make_id("fx", fixture),
        "record_type": record_type,
        "population": population,
        "fixture_date": str(day)[:10],
        "home": home,
        "away": away,
        "market": market,
        "selection_side": side,
        "selected_team": home if side == "home" else away if side == "away" else "",
        "family": family,
        "primary_rule": family,
        "supporting_rule_signals": "",
        "other_snapshot_rule_signals": "",
        "decision_probability_pct": probability_pct,
        "decision_probability_field": probability_field,
        "decision_time": decision_time,
        "kickoff_time": kickoff_time,
        "first_seen_time": "",
        "lead_minutes": round(lead_minutes, 2) if lead_minutes is not None else "",
        "time_status": time_status,
        "result_status": "not_scored",
        "result_date": "",
        "score": "",
        "outcome_category": "",
        "market_1x2_result": "",
        "double_chance_result": "",
        "dnb_asian0_result": "",
        "asian_plus0_5_result": "",
        "asian_plus1_result": "",
        "main_send_receipt": False,
        "shadow_send_receipt": False,
        "publication_stage": "no_retained_receipt",
        "receipt_side_attribution": "not_applicable",
        "ticketed": False,
        "ticket_leg_count": 0,
        "linked_operational_selection_ids": "",
        "linked_verified_operational_selection_ids": "",
        "linked_archive_only_selection_ids": "",
        "linked_operational_side_relation": "",
        "linked_operational_publication_stage": "",
        "linked_operational_ticketed": "",
        "source_era": "",
        "model_key": "",
        "model_keys_seen": "",
        "model_version": "",
        "sources_used": "",
        "archive_snapshot_count": 1,
        "archive_files": "",
        "snapshot_probability_min_pct": probability_pct,
        "snapshot_probability_max_pct": probability_pct,
        "odds_decimal": "",
        "bookmaker": "",
        "odds_source": "",
        "odds_captured_at": "",
        "price_evidence": "",
        "pre_kickoff_analysis_eligible": False,
        "exclusion_reason": "",
    }


def _set_score(record: dict[str, Any], score: Any, side: str) -> None:
    values = _score_values(score)
    if values is None:
        return
    home_score, away_score = values
    scored = score_selection(home_score, away_score, side)
    record["score"] = f"{home_score}-{away_score}"
    for key, value in scored.items():
        record[key] = value or ""


def build_operational_records(
    start: str,
    end: str,
    audit: dict[str, Any],
    raw_archives: list[dict[str, Any]],
    raw_files_by_key: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    selected, receipt = load_archived_picks_with_receipt(start, end)
    safe_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        safe_groups[selection_key(row)].append(row)

    raw_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in raw_archives:
        raw_groups[selection_key(row)].append(row)

    evaluation = load_evaluation_map(audit)
    main_receipts, shadow_receipts = load_receipt_sets()
    ticket_counts, exact_ticket_counts = load_ticket_counts()
    ticket_alias_multiplicity: Counter[tuple[str, str, str, str, str]] = Counter()
    for key, snapshots in safe_groups.items():
        day, _, _, market, side = key
        source = snapshots[0]
        alias_key = (
            day,
            source_team_key(source.get("home") or ""),
            source_team_key(source.get("away") or ""),
            market,
            side,
        )
        ticket_alias_multiplicity[alias_key] += 1
    cutoff = str(audit.get("same_day_cutoff") or "")[:10]
    start_day = date.fromisoformat(start)
    end_day = date.fromisoformat(end)

    records: list[dict[str, Any]] = []
    safe_ids: set[tuple] = set()
    fixture_side_counts: Counter[tuple] = Counter()

    # The audited 30-day rows are the performance population. Group duplicate
    # archive observations once and keep their rule signals in separate fields.
    for key, snapshots in safe_groups.items():
        source = dict(snapshots[0])
        day, home_key, away_key, market, side = key
        source.setdefault("market", market)
        source.setdefault("pick", side)
        source.setdefault("home", snapshots[0].get("home"))
        source.setdefault("away", snapshots[0].get("away"))
        time_status, lead = row_time_status(source)
        family = str(source.get("edge_rule") or source.get("rule") or "UNKNOWN")
        record = _base_record(
            record_type="operational_selection",
            population="operational_30d",
            row=source,
            day=day,
            market=market,
            side=side,
            family=family,
            probability_pct=_row_probability(source),
            probability_field="avg_p",
            decision_time=str(source.get("as_of") or ""),
            kickoff_time=str(source.get("kickoff_utc") or ""),
            time_status=time_status,
            lead_minutes=lead,
        )
        record["selection_id"] = make_id("op", key)
        record["primary_rule"] = family
        safe_signals = sorted({signal for item in snapshots for signal in rule_signals(item)})
        record["supporting_rule_signals"] = ";".join(safe_signals)
        all_snapshots = raw_groups.get(key, snapshots)
        metadata = archive_snapshot_metadata(all_snapshots)
        record.update({
            "archive_snapshot_count": metadata["archive_snapshot_count"],
            "archive_files": metadata["archive_files"],
            "snapshot_probability_min_pct": metadata["snapshot_probability_min_pct"],
            "snapshot_probability_max_pct": metadata["snapshot_probability_max_pct"],
            "other_snapshot_rule_signals": ";".join(
                signal for signal in metadata["other_snapshot_rule_signals"]
                if signal not in safe_signals
            ),
            "source_era": source_era(source),
            "model_version": str(source.get("model_version") or ""),
            "sources_used": ";".join(source.get("sources_used", []))
            if isinstance(source.get("sources_used"), list)
            else str(source.get("sources_used") or ""),
        })
        if record["archive_snapshot_count"] == 0:
            record["archive_snapshot_count"] = len(snapshots)

        audit_row = evaluation.get(key)
        status, audit_row = classify_operational_status(
            source, audit_row, cutoff, time_status
        )
        record["result_status"] = status
        if status == "rescheduled" and audit_row:
            shifted_score = {
                "hs": audit_row.get("rescheduled_hs"),
                "gs": audit_row.get("rescheduled_gs"),
            }
            if _score_values(shifted_score) is not None:
                hs, gs = _score_values(shifted_score) or (0, 0)
                record["score"] = f"{hs}-{gs} (shifted fixture)"
                record["result_date"] = str(audit_row.get("rescheduled_to") or "")
            record["exclusion_reason"] = (
                "Original scheduled-date result absent; shifted-date score is "
                "shown for context and excluded from the market comparison."
            )
        elif status == "same_day_cutoff_missing_score":
            record["exclusion_reason"] = (
                "The retained audit snapshot applied its same-day cutoff; no "
                "score is retained for this selection."
            )
        elif status == "pending":
            record["exclusion_reason"] = "No settled score retained; classified pending."
        elif status == "ambiguous":
            record["exclusion_reason"] = "Result join is ambiguous; no score assigned."
        elif status == "settled" and time_status == "pre_kickoff_verified" and audit_row:
            score = {"hs": audit_row.get("hs"), "gs": audit_row.get("gs")}
            if _score_values(score) is not None:
                _set_score(record, score, side)
                record["result_status"] = "settled"
            else:
                record["result_status"] = "missing_score"
                record["exclusion_reason"] = "Settled status without a retained score."
        elif time_status == "post_kickoff_or_equal":
            record["exclusion_reason"] = (
                "Decision timestamp is at or after kickoff; excluded from "
                "pre-kickoff outcome analysis."
            )
        elif time_status != "pre_kickoff_verified":
            record["exclusion_reason"] = (
                "No explicit-offset decision/kickoff pair; pre-kickoff status "
                "cannot be verified."
            )

        receipt_key = fixture_key(day, source.get("home"), source.get("away")) + (market,)
        record["main_send_receipt"] = receipt_key in main_receipts
        record["shadow_send_receipt"] = receipt_key in shadow_receipts
        if record["main_send_receipt"] and record["shadow_send_receipt"]:
            record["publication_stage"] = "main_and_shadow_receipt"
        elif record["main_send_receipt"]:
            record["publication_stage"] = "main_receipt_only"
        elif record["shadow_send_receipt"]:
            record["publication_stage"] = "shadow_receipt_only"
        else:
            record["publication_stage"] = "no_retained_receipt"
        record["receipt_side_attribution"] = "fixture_market_receipt"
        record["ticket_leg_count"] = ticket_leg_count_for_selection(
            record,
            ticket_counts,
            exact_ticket_counts,
            ticket_alias_multiplicity,
        )
        record["ticketed"] = record["ticket_leg_count"] > 0
        if not record["main_send_receipt"] and not record["shadow_send_receipt"]:
            record["exclusion_reason"] = "; ".join(filter(None, [
                record["exclusion_reason"],
                "No retained send receipt; this is not proof the pick was unpublished.",
            ]))
        if not record["ticketed"]:
            record["exclusion_reason"] = "; ".join(filter(None, [
                record["exclusion_reason"],
                "No matching actual slip leg; candidate-level ticket rejection "
                "reason is not retained.",
            ]))

        # A receipt key contains fixture/market, not side. Flag any event with
        # more than one archived selected side rather than attributing a receipt
        # directionally without evidence.
        fixture_side_counts[receipt_key] += 1
        record["pre_kickoff_analysis_eligible"] = (
            time_status == "pre_kickoff_verified"
            and market == "1x2"
            and start_day <= date.fromisoformat(day) <= end_day
        )
        safe_ids.add(key)
        records.append(record)

    for record in records:
        key = (
            record["fixture_date"],
            ledger_team_key(record["home"]),
            ledger_team_key(record["away"]),
            record["market"],
        )
        if fixture_side_counts[key] > 1:
            record["receipt_side_attribution"] = "fixture_market_only_multiple_sides"
            record["exclusion_reason"] = "; ".join(filter(None, [
                record["exclusion_reason"],
                "Receipt does not encode the side and this fixture/market has "
                "multiple retained selected sides.",
            ]))

    # Preserve every other dated archive selection once, but do not grade
    # mutable/out-of-window snapshots as historical performance.
    for key, snapshots in raw_groups.items():
        if key in safe_ids:
            continue
        day, _, _, market, side = key
        candidates = sorted(
            snapshots,
            key=lambda row: parse_aware(row.get("as_of"))
            or datetime.max.replace(tzinfo=LOCAL_TZ),
        )
        source = dict(candidates[0])
        time_status, lead = row_time_status(source)
        signals = sorted({signal for item in snapshots for signal in rule_signals(item)})
        source_family = str(source.get("edge_rule") or source.get("rule") or "UNKNOWN")
        if market != "1x2":
            population = "legacy_other_market_archive"
            record_type = "other_market_selection"
        elif date.fromisoformat(day) > end_day:
            population = "current_forward_archive"
            record_type = "operational_selection"
        elif start_day <= date.fromisoformat(day) <= end_day:
            population = "unsafe_or_unlinked_snapshot"
            record_type = "operational_selection"
        else:
            population = "legacy_archive_inventory"
            record_type = "operational_selection"
        record = _base_record(
            record_type=record_type,
            population=population,
            row=source,
            day=day,
            market=market,
            side=side,
            family=source_family,
            probability_pct=_row_probability(source),
            probability_field="avg_p",
            decision_time=str(source.get("as_of") or ""),
            kickoff_time=str(source.get("kickoff_utc") or ""),
            time_status=time_status,
            lead_minutes=lead,
        )
        record["selection_id"] = make_id("archive", key)
        metadata = archive_snapshot_metadata(snapshots)
        record.update({
            "archive_snapshot_count": metadata["archive_snapshot_count"],
            "archive_files": metadata["archive_files"],
            "snapshot_probability_min_pct": metadata["snapshot_probability_min_pct"],
            "snapshot_probability_max_pct": metadata["snapshot_probability_max_pct"],
            "supporting_rule_signals": ";".join(signals),
            "source_era": source_era(source),
            "model_version": str(source.get("model_version") or ""),
            "sources_used": ";".join(source.get("sources_used", []))
            if isinstance(source.get("sources_used"), list)
            else str(source.get("sources_used") or ""),
            "result_status": "not_scored_outside_verified_30d_join",
            "publication_stage": "no_retained_receipt",
            "receipt_side_attribution": "no_joined_receipt",
            "exclusion_reason": (
                "Retained archive row is kept for inventory, but it is outside "
                "the frozen 30-day outcome join or came from an unverified "
                "snapshot; no score or publication state is inferred."
            ),
        })
        if time_status != "pre_kickoff_verified":
            record["exclusion_reason"] += " Pre-kickoff status is not verified."
        elif population == "legacy_other_market_archive":
            record["exclusion_reason"] += (
                " The retained OU 2.5 rows have no kickoff_utc witness."
            )
        receipt_key = fixture_key(day, source.get("home"), source.get("away")) + (market,)
        record["main_send_receipt"] = receipt_key in main_receipts
        record["shadow_send_receipt"] = receipt_key in shadow_receipts
        if record["main_send_receipt"] and record["shadow_send_receipt"]:
            record["publication_stage"] = "main_and_shadow_receipt"
        elif record["main_send_receipt"]:
            record["publication_stage"] = "main_receipt_only"
        elif record["shadow_send_receipt"]:
            record["publication_stage"] = "shadow_receipt_only"
        record["receipt_side_attribution"] = "fixture_market_receipt"
        record["ticket_leg_count"] = ticket_counts.get(key, 0)
        record["ticketed"] = record["ticket_leg_count"] > 0
        if market != "1x2":
            record["selected_team"] = ""
        records.append(record)

    # Add the current 4-row 2026-10-08 slate, also visible in the 2-day export.
    # It is retained as forward tracking only and is not mixed into outcomes.
    for record in records:
        if record["population"] == "current_forward_archive":
            record["pre_kickoff_analysis_eligible"] = False
            if record["time_status"] == "pre_kickoff_verified":
                record["result_status"] = "pending_forward_tracking"
                record["exclusion_reason"] = (
                    "Current pre-kickoff record; no result is retained in the "
                    "source snapshot. It is forward tracking, not historical performance."
                )

    return records, selected, receipt


# -- research ML ledger ------------------------------------------------------
def build_ml_records(
    ml_ledger: dict[str, Any],
    operational_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    raw_rows = ml_ledger.get("rows", [])
    if not isinstance(raw_rows, list):
        return []

    verified_by_event: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    verified_by_side: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    archive_by_event: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    archive_by_side: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    verified_populations = {"operational_30d", "current_forward_archive"}
    archive_populations = {
        "legacy_archive_inventory", "unsafe_or_unlinked_snapshot",
    }
    for item in operational_records:
        if item.get("record_type") != "operational_selection":
            continue
        if item.get("market") != "1x2":
            continue
        population = item.get("population")
        if population not in verified_populations | archive_populations:
            continue
        event = fixture_key(
            item.get("fixture_date", ""),
            item.get("home"), item.get("away"),
        )
        if population in verified_populations:
            target_event, target_side = verified_by_event, verified_by_side
        else:
            target_event, target_side = archive_by_event, archive_by_side
        target_event[event].append(item)
        target_side[event + (norm_side(item.get("selection_side")),)].append(item)

    output: list[dict[str, Any]] = []
    for row in raw_rows:
        if not isinstance(row, dict):
            continue
        time_status, kickoff, lead = ml_time_status(row)
        family = str(row.get("family") or "ml-unknown")
        side = norm_side(row.get("pick"))
        market = norm_side(row.get("market") or "1x2")
        probability = row.get("ml_p")
        try:
            probability_pct = float(probability) * 100.0
        except (TypeError, ValueError):
            probability_pct = None
        event_day = kickoff.date().isoformat() if kickoff else str(row.get("date") or "")[:10]
        record = _base_record(
            record_type="ml_research_prediction",
            population=f"{family}_{'draw' if side == 'draw' else 'team'}",
            row=row,
            day=event_day,
            market=market,
            side=side,
            family=family,
            probability_pct=probability_pct,
            probability_field="ml_p",
            decision_time=str(row.get("first_seen_at") or ""),
            kickoff_time=kickoff.isoformat() if kickoff else str(row.get("kickoff") or ""),
            time_status=time_status,
            lead_minutes=lead,
        )
        record["selection_id"] = str(row.get("event_key") or make_id(
            "ml", (event_day, row.get("home"), row.get("away"), family, side)
        ))
        record["first_seen_time"] = str(row.get("first_seen_at") or "")
        record["primary_rule"] = str(row.get("edge_family") or family)
        record["result_status"] = str(row.get("status") or "unknown")
        record["model_key"] = str(row.get("model_key") or "")
        keys_seen = row.get("model_keys_seen")
        if isinstance(keys_seen, list):
            record["model_keys_seen"] = ";".join(str(item) for item in keys_seen)
        record["sources_used"] = ";".join(row.get("sources_used", []))
        record["source_era"] = str(row.get("model_key") or "unrecorded")
        record["result_date"] = str(row.get("result_date") or "")

        score = row.get("score")
        if record["result_status"] == "settled" and _score_values(score) is not None:
            _set_score(record, score, side)
        elif record["result_status"] == "conflict":
            record["result_status"] = "ambiguous"
            record["exclusion_reason"] = "Conflicting retained result claims."
        elif record["result_status"] == "pending":
            record["exclusion_reason"] = "No settled score in the retained research ledger."
        elif record["result_status"] == "settled":
            record["result_status"] = "missing_score"
            record["exclusion_reason"] = "Settled status without a retained score."

        record["pre_kickoff_analysis_eligible"] = (
            time_status == "pre_kickoff_verified" and market == "1x2"
        )
        if not record["pre_kickoff_analysis_eligible"]:
            record["exclusion_reason"] = "; ".join(filter(None, [
                record["exclusion_reason"],
                "Pre-kickoff ML status could not be verified.",
            ]))

        event = fixture_key(event_day, row.get("home"), row.get("away"))
        exact = verified_by_side.get(event + (side,), [])
        fixture_matches = verified_by_event.get(event, [])
        archive_exact = archive_by_side.get(event + (side,), [])
        archive_fixture = archive_by_event.get(event, [])
        if exact:
            links = exact
            relation = "same_side_exact_fixture_link"
        elif fixture_matches and side in {"home", "away"}:
            links = fixture_matches
            relation = "same_fixture_different_side"
        elif fixture_matches:
            links = fixture_matches
            relation = "same_fixture_draw_vs_team"
        elif archive_exact:
            links = archive_exact
            relation = "same_side_archive_only_link"
        elif archive_fixture:
            links = archive_fixture
            relation = "same_fixture_archive_only_link"
        else:
            links = []
            relation = "no_operational_fixture_link"
        record["linked_operational_selection_ids"] = ";".join(
            str(item["selection_id"]) for item in links
        )
        record["linked_verified_operational_selection_ids"] = ";".join(
            str(item["selection_id"]) for item in exact or fixture_matches
        )
        record["linked_archive_only_selection_ids"] = ";".join(
            str(item["selection_id"]) for item in archive_exact or archive_fixture
        )
        record["linked_operational_side_relation"] = relation
        if exact:
            record["linked_operational_publication_stage"] = ";".join(sorted({
                str(item.get("publication_stage") or "") for item in exact
            }))
            record["linked_operational_ticketed"] = any(
                bool(item.get("ticketed")) for item in exact
            )
        elif archive_exact or archive_fixture:
            record["linked_operational_publication_stage"] = (
                "not_attributed_archive_only"
            )
            record["linked_operational_ticketed"] = "not_attributed_archive_only"
        else:
            record["linked_operational_publication_stage"] = (
                "not_attributed_without_same_side_link" if links else "no_link"
            )
            record["linked_operational_ticketed"] = "not_attributed"
        if family in {"ml-meta", "ml-fade"}:
            record["exclusion_reason"] = "; ".join(filter(None, [
                record["exclusion_reason"],
                "Research-ledger row is not itself a publication or ticket record; "
                "linked operational stage is fixture/side matching only.",
            ]))
        output.append(record)
    return output


# -- separate other-market notes -------------------------------------------
def build_note_records(
    op_records: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    audit: dict[str, Any],
) -> list[dict[str, Any]]:
    op_by_key = {selection_key(row): row for row in selected}
    audit_rows = audit.get("settled_ledger", [])
    notes_by_key: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    if not isinstance(audit_rows, list):
        return []
    for row in audit_rows:
        if not isinstance(row, dict):
            continue
        key = _audit_key(row)
        if key is None:
            continue
        for note in row.get("notes_audit", []) or []:
            if isinstance(note, dict):
                notes_by_key[key].append(note)

    record_index = {
        (
            item["fixture_date"], ledger_team_key(item["home"]),
            ledger_team_key(item["away"]), item["market"], item["selection_side"],
        ): item for item in op_records
        if item.get("population") == "operational_30d"
    }
    output: list[dict[str, Any]] = []
    for key, notes in notes_by_key.items():
        source = op_by_key.get(key)
        record = record_index.get(key)
        if source is None or record is None:
            continue
        if not record.get("pre_kickoff_analysis_eligible"):
            continue
        score = str(record.get("score") or "")
        fixture = f"{source.get('home')} vs {source.get('away')}"
        for note in notes:
            output.append({
                "selection_id": record.get("selection_id", ""),
                "fixture_date": key[0],
                "fixture": fixture,
                "score": score,
                "market": str(note.get("market") or ""),
                "label": str(note.get("label") or ""),
                "engine": str(note.get("engine") or ""),
                "promised_probability": note.get("promised"),
                "hit": note.get("hit"),
            })
    return output


# -- aggregation -------------------------------------------------------------
def _result_value(row: dict[str, Any], key: str) -> str:
    return str(row.get(key) or "")


def break_even_price(wins: int, pushes: int, losses: int) -> float | None:
    if wins <= 0:
        return None
    return 1.0 + losses / wins


def aggregate_cell(
    population: str,
    dimension: str,
    cell: str,
    rows: list[dict[str, Any]],
    excluded_time: int = 0,
) -> dict[str, Any]:
    draw_population = population.endswith("_draw")
    if draw_population:
        scored = [
            row for row in rows
            if row.get("market_1x2_result") in {"win", "loss"}
        ]
    else:
        scored = [row for row in rows if row.get("outcome_category") in {
            "win", "draw", "loss_by_one", "loss_by_two_plus"
        }]
    categories = Counter(str(row.get("outcome_category")) for row in scored)
    draw_hits = sum(row.get("market_1x2_result") == "win" for row in scored)
    draw_misses = sum(row.get("market_1x2_result") == "loss" for row in scored)
    counts: dict[str, Counter[str]] = {
        "market_1x2": Counter(),
        "double_chance": Counter(),
        "dnb_asian0": Counter(),
        "asian_plus0_5": Counter(),
        "asian_plus1": Counter(),
    }
    for row in scored:
        for market in counts:
            result = _result_value(row, f"{market}_result")
            if result:
                counts[market][result] += 1

    n_scored = len(scored)
    wins = categories["win"]
    draws = categories["draw"]
    loss_one = categories["loss_by_one"]
    loss_two = categories["loss_by_two_plus"]

    def result_count(market: str, label: str) -> int:
        return counts[market][label]

    if draw_population:
        wins = draws = loss_one = loss_two = 0
    total_team = n_scored if not draw_population else 0
    scored_win_rate = (
        draw_hits / n_scored if draw_population and n_scored
        else wins / n_scored if n_scored else None
    )
    base: dict[str, Any] = {
        "population": population,
        "dimension": dimension,
        "cell": cell,
        "n": len(rows),
        "n_scored": n_scored,
        "n_pending": sum(row.get("result_status") == "pending" for row in rows),
        "n_ambiguous": sum(row.get("result_status") == "ambiguous" for row in rows),
        "n_rescheduled": sum(row.get("result_status") == "rescheduled" for row in rows),
        "n_missing_score": sum(row.get("result_status") in {
            "same_day_cutoff_missing_score", "missing_score"
        } for row in rows),
        "n_excluded_time": excluded_time,
        "win": wins,
        "draw": draws,
        "loss_by_one": loss_one,
        "loss_by_two_plus": loss_two,
        "draw_prediction_hits": draw_hits if draw_population else "",
        "draw_prediction_misses": draw_misses if draw_population else "",
        "win_rate_scored": scored_win_rate,
        "avoid_defeat_n": "" if draw_population else wins + draws,
        "avoid_defeat_rate_scored": (
            "" if draw_population
            else (wins + draws) / n_scored if n_scored else None
        ),
        "avoid_heavy_loss_n": "" if draw_population else n_scored - loss_two,
        "avoid_heavy_loss_rate_scored": (
            "" if draw_population
            else (n_scored - loss_two) / n_scored if n_scored else None
        ),
    }
    market_map = {
        "market_1x2": "market_1x2",
        "double_chance": "double_chance",
        "dnb_asian0": "dnb_asian0",
        "asian_plus0_5": "asian_plus0_5",
        "asian_plus1": "asian_plus1",
    }
    for market, prefix in market_map.items():
        for outcome in ("win", "push", "loss"):
            base[f"{prefix}_{outcome}"] = result_count(market, outcome)
    if draw_population:
        for market, prefix in market_map.items():
            if market != "market_1x2":
                for outcome in ("win", "push", "loss"):
                    base[f"{prefix}_{outcome}"] = ""
    base["be_1x2_decimal_diagnostic"] = break_even_price(
        result_count("market_1x2", "win"),
        result_count("market_1x2", "push"),
        result_count("market_1x2", "loss"),
    )
    base["be_double_chance_decimal_diagnostic"] = break_even_price(
        result_count("double_chance", "win"),
        result_count("double_chance", "push"),
        result_count("double_chance", "loss"),
    )
    base["be_dnb_asian0_decimal_diagnostic"] = break_even_price(
        result_count("dnb_asian0", "win"),
        result_count("dnb_asian0", "push"),
        result_count("dnb_asian0", "loss"),
    )
    base["be_asian_plus0_5_decimal_diagnostic"] = break_even_price(
        result_count("asian_plus0_5", "win"),
        result_count("asian_plus0_5", "push"),
        result_count("asian_plus0_5", "loss"),
    )
    base["be_asian_plus1_decimal_diagnostic"] = break_even_price(
        result_count("asian_plus1", "win"),
        result_count("asian_plus1", "push"),
        result_count("asian_plus1", "loss"),
    )
    # Keep the denominator visibly attached to every row, even when outcomes
    # are not team selections (for example the separate ML draw rows).
    base["n_team_scored"] = total_team
    return base


def build_breakdowns(records: list[dict[str, Any]], start: str, end: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    op = [
        row for row in records
        if row.get("population") == "operational_30d"
        and row.get("pre_kickoff_analysis_eligible")
    ]
    ml = [
        row for row in records
        if row.get("record_type") == "ml_research_prediction"
        and row.get("pre_kickoff_analysis_eligible")
    ]
    op_time_excluded = sum(
        row.get("population") == "operational_30d"
        and row.get("time_status") != "pre_kickoff_verified"
        for row in records
    )

    def add(population: str, dimension: str, rows: list[dict[str, Any]], field: str) -> None:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            value = row.get(field)
            if isinstance(value, bool):
                label = "ticketed" if value else "not_ticketed"
            else:
                label = str(value or "unknown")
            groups[label].append(row)
        for cell, members in sorted(groups.items()):
            output.append(aggregate_cell(population, dimension, cell, members))

    if op:
        output.append(aggregate_cell(
            "operational_30d", "overall_pre_kickoff", "all", op,
            excluded_time=op_time_excluded,
        ))
        add("operational_30d", "primary_rule_family", op, "primary_rule")
        add(
            "operational_30d", "probability_band_full_range", op,
            "probability_band",
        )
        add(
            "operational_30d", "publication_receipt_stage", op,
            "publication_stage",
        )
        add(
            "operational_30d", "ticket_stage", op,
            "ticketed",
        )
        add("operational_30d", "selected_team_side", op, "selection_side")
        add("operational_30d", "decision_time_week", op, "decision_week")
        add("operational_30d", "source_era", op, "source_era")

    # Full-range deciles are materialized even when a cell has n=0.
    deciles = [f"{start:02d}-<{start + 10:02d}" for start in range(0, 90, 10)]
    deciles.append("90-100")
    for population, rows in (
        ("operational_30d", op),
        ("ml-meta_team", [r for r in ml if r["population"] == "ml-meta_team"]),
        ("ml-meta_draw", [r for r in ml if r["population"] == "ml-meta_draw"]),
        ("ml-fade_team", [r for r in ml if r["population"] == "ml-fade_team"]),
    ):
        current = {str(row.get("probability_band")) for row in rows}
        for band in deciles:
            if band not in current:
                output.append(aggregate_cell(population, "probability_band_full_range", band, []))

    for population, rows in (
        ("ml-meta_team", [r for r in ml if r["population"] == "ml-meta_team"]),
        ("ml-meta_draw", [r for r in ml if r["population"] == "ml-meta_draw"]),
        ("ml-fade_team", [r for r in ml if r["population"] == "ml-fade_team"]),
    ):
        if rows:
            output.append(aggregate_cell(population, "overall_pre_kickoff", "all", rows))
            add(population, "probability_band_full_range", rows, "probability_band")
            team_rows = [
                row for row in rows
                if row.get("selection_side") in {"home", "away"}
            ]
            if team_rows:
                add(population, "selected_team_side", team_rows, "selection_side")
            add(population, "first_seen_week", rows, "decision_week")
            add(population, "model_key_source_era", rows, "model_key")
            same_side_links = [
                row for row in rows
                if row.get("linked_operational_side_relation")
                == "same_side_exact_fixture_link"
            ]
            add(
                population,
                "linked_operational_stage_same_side_only",
                same_side_links,
                "linked_operational_publication_stage",
            )
            add(
                population,
                "linked_operational_ticket_stage_same_side_only",
                same_side_links,
                "linked_operational_ticketed",
            )
            # Keep absent/mismatched operational links visible as their own cells.
            other_links = [
                row for row in rows
                if row.get("linked_operational_side_relation")
                != "same_side_exact_fixture_link"
            ]
            if other_links:
                link_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
                for row in other_links:
                    relation = str(
                        row.get("linked_operational_side_relation") or "unknown"
                    )
                    link_groups[relation].append(row)
                for cell, members in sorted(link_groups.items()):
                    output.append(aggregate_cell(
                        population, "linked_operational_stage_same_side_only",
                        cell, members,
                    ))

    # Include zero cells across all probability bands for each ML population.
    for population, rows in (
        ("ml-meta_team", [r for r in ml if r["population"] == "ml-meta_team"]),
        ("ml-meta_draw", [r for r in ml if r["population"] == "ml-meta_draw"]),
        ("ml-fade_team", [r for r in ml if r["population"] == "ml-fade_team"]),
    ):
        existing = {
            row["cell"] for row in output
            if row["population"] == population
            and row["dimension"] == "probability_band_full_range"
        }
        for band in deciles:
            if band not in existing:
                output.append(aggregate_cell(
                    population, "probability_band_full_range", band, []
                ))

    # Inventory-only archive populations have their own n/status cells; they
    # are never mixed into the verified performance cohorts.
    for population in (
        "current_forward_archive",
        "legacy_archive_inventory",
        "unsafe_or_unlinked_snapshot",
        "legacy_other_market_archive",
    ):
        rows = [row for row in records if row.get("population") == population]
        if rows:
            output.append(aggregate_cell(population, "inventory_only", "all", rows))
            add(population, "primary_rule_family", rows, "primary_rule")

    return output


def build_note_breakdowns(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for note in notes:
        grouped[str(note.get("market") or "unknown")].append(note)
    output: list[dict[str, Any]] = []
    for market, rows in sorted(grouped.items()):
        hits = sum(row.get("hit") is True for row in rows)
        misses = sum(row.get("hit") is False for row in rows)
        output.append({
            "population": "other_market_event_notes",
            "dimension": "market_note",
            "cell": market,
            "n": len(rows),
            "n_scored": hits + misses,
            "n_pending": 0,
            "n_ambiguous": 0,
            "n_rescheduled": 0,
            "n_missing_score": sum(row.get("hit") not in {True, False} for row in rows),
            "n_excluded_time": 0,
            "win": hits,
            "draw": 0,
            "loss_by_one": misses,
            "loss_by_two_plus": 0,
            "win_rate_scored": hits / (hits + misses) if hits + misses else None,
            "avoid_defeat_n": "",
            "avoid_defeat_rate_scored": "",
            "avoid_heavy_loss_n": "",
            "avoid_heavy_loss_rate_scored": "",
            "market_1x2_win": "",
            "market_1x2_push": "",
            "market_1x2_loss": "",
            "double_chance_win": "",
            "double_chance_push": "",
            "double_chance_loss": "",
            "dnb_asian0_win": "",
            "dnb_asian0_push": "",
            "dnb_asian0_loss": "",
            "asian_plus0_5_win": "",
            "asian_plus0_5_push": "",
            "asian_plus0_5_loss": "",
            "asian_plus1_win": "",
            "asian_plus1_push": "",
            "asian_plus1_loss": "",
            "be_1x2_decimal_diagnostic": "",
            "be_double_chance_decimal_diagnostic": "",
            "be_dnb_asian0_decimal_diagnostic": "",
            "be_asian_plus0_5_decimal_diagnostic": "",
            "be_asian_plus1_decimal_diagnostic": "",
        })
    return output


# -- market prices -----------------------------------------------------------
def find_price_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row for row in records
        if row.get("population") == "operational_30d"
        and row.get("pre_kickoff_analysis_eligible")
        and row.get("odds_decimal") not in (None, "")
    ]


def apply_operational_links_and_prices(records: list[dict[str, Any]]) -> None:
    # Price is read from the exact selected quote retained with the original
    # pick, not from a later best-price search or reconstructed price feed.
    for row in records:
        if row.get("population") != "operational_30d":
            continue
        raw = row.get("_raw_source")
        if not isinstance(raw, dict):
            continue
        quote = price_evidence(raw, str(row.get("time_status") or ""))
        row.update(quote)


def market_price_stats(price_rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in price_rows if row.get("market_1x2_result")]
    units = 0.0
    wins = draws = losses = 0
    for row in settled:
        result = row.get("market_1x2_result")
        if result == "win":
            wins += 1
            units += float(row["odds_decimal"]) - 1.0
        else:
            if row.get("outcome_category") == "draw":
                draws += 1
            losses += 1
            units -= 1.0
    n = len(settled)
    return {
        "n": n,
        "quote_rows": len(price_rows),
        "unscored_quote_rows": len(price_rows) - n,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "profit_units": round(units, 3),
        "roi": units / n if n else None,
    }


# -- output/summary ----------------------------------------------------------
def _csv_value(value: Any) -> Any:
    if isinstance(value, (list, tuple, set)):
        return ";".join(str(item) for item in value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key, "")) for key in columns})


def pct(numerator: int, denominator: int) -> str:
    return f"{100.0 * numerator / denominator:.1f}%" if denominator else "n/a"


def _md_escape(value: Any) -> str:
    text = str(value if value is not None else "")
    return text.replace("|", "\\|").replace("\n", " ")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(_md_escape(value) for value in row) + " |")
    return "\n".join(lines)


def _find_cell(
    breakdowns: list[dict[str, Any]], population: str, dimension: str
) -> list[dict[str, Any]]:
    return sorted(
        [row for row in breakdowns
         if row.get("population") == population
         and row.get("dimension") == dimension],
        key=lambda row: str(row.get("cell") or ""),
    )


def _outcome_rows(breakdowns: list[dict[str, Any]], population: str) -> list[Any] | None:
    rows = _find_cell(breakdowns, population, "overall_pre_kickoff")
    return rows[0] if rows else None


def build_markdown(
    *,
    as_of: str,
    start: str,
    end: str,
    op_records: list[dict[str, Any]],
    ml_records: list[dict[str, Any]],
    breakdowns: list[dict[str, Any]],
    notes: list[dict[str, Any]],
    archive_receipt: dict[str, Any],
    price_rows: list[dict[str, Any]],
    result_data: dict[str, Any],
    link_stats: dict[str, Any],
    raw_ou25_count: int,
) -> str:
    valid_op = [
        row for row in op_records
        if row.get("population") == "operational_30d"
        and row.get("pre_kickoff_analysis_eligible")
    ]
    op_all = [row for row in op_records if row.get("population") == "operational_30d"]
    op_settled = [row for row in valid_op if row.get("outcome_category")]
    op_counts = Counter(row.get("outcome_category") for row in op_settled)
    status_counts = Counter(row.get("result_status") for row in valid_op)
    prices = market_price_stats(price_rows)
    price_roi_text = (
        f"{prices['roi'] * 100:.1f}%" if prices["roi"] is not None else "n/a"
    )
    price_draw_word = "draw" if prices["draws"] == 1 else "draws"
    forward_pick_count = sum(
        row.get("population") == "current_forward_archive"
        for row in op_records
    )
    legacy_snapshot_count = sum(
        row.get("population")
        in {"legacy_archive_inventory", "unsafe_or_unlinked_snapshot"}
        for row in op_records
    )
    ou25_unique_count = sum(
        row.get("population") == "legacy_other_market_archive"
        for row in op_records
    )
    strict_pre_count = sum(
        row.get("time_status") == "pre_kickoff_verified" for row in op_all
    )
    post_equal_count = sum(
        row.get("time_status") == "post_kickoff_or_equal" for row in op_all
    )
    unverified_time_count = sum(
        row.get("time_status") == "unverified_missing_or_naive_timestamp"
        for row in op_all
    )
    ml_team_meta = _outcome_rows(breakdowns, "ml-meta_team") or {}
    ml_draw_meta = _outcome_rows(breakdowns, "ml-meta_draw") or {}
    ml_team_fade = _outcome_rows(breakdowns, "ml-fade_team") or {}
    ml_status_counts = Counter(row.get("result_status") for row in ml_records)
    ml_model_keys = {
        str(row.get("model_key")) for row in ml_records if row.get("model_key")
    }
    ml_multi_key_rows = sum(
        len(str(row.get("model_keys_seen") or "").split(";")) > 1
        for row in ml_records
    )
    ml_lead_values = [
        float(row["lead_minutes"])
        for row in ml_records
        if row.get("lead_minutes") not in (None, "")
    ]
    ml_lead_range = (
        f"{min(ml_lead_values):.2f}–{max(ml_lead_values):.1f}"
        if ml_lead_values else "unavailable"
    )

    ml_rows_by_population: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in ml_records:
        ml_rows_by_population[str(row.get("population"))].append(row)

    lines: list[str] = []
    lines += [
        f"# Recorded Prediction Market-Suitability Audit ({as_of})",
        "",
        "**Discovery only. No market pivot, model activation, rule change, "
        "ticket change, or deployment authorization.** All outcome comparisons "
        "are retrospective joins to retained pre-kickoff records; no historical "
        "fixtures were run through today's model.",
        "",
        "## Direct answer",
        "",
        f"The frozen 30-day operational archive ({start} to {end}) contains "
        f"**{len(valid_op)}** selections with an explicit decision timestamp "
        f"before kickoff. **{len(op_settled)}** have a retained settled score. "
        f"Among those, the selected team won **{op_counts['win']}/{len(op_settled)} "
        f"({pct(op_counts['win'], len(op_settled))})**, drew "
        f"**{op_counts['draw']}/{len(op_settled)}**, lost by one "
        f"**{op_counts['loss_by_one']}/{len(op_settled)}**, and lost by two or "
        f"more **{op_counts['loss_by_two_plus']}/{len(op_settled)}**. That is "
        f"**{pct(op_counts['win'] + op_counts['draw'], len(op_settled))} "
        "avoiding defeat** and **"
        f"{pct(len(op_settled) - op_counts['loss_by_two_plus'], len(op_settled))} "
        "avoiding a loss by 2+**. In this mixed-era sample, avoiding heavy "
        "defeat is the most frequent outcome; it is not a stable or validated "
        "performance estimate.",
        "",
        f"The separate ML ledger's `ml-meta` team picks scored "
        f"{ml_team_meta.get('win', 0)}/{ml_team_meta.get('n_scored', 0)} wins, "
        f"{ml_team_meta.get('draw', 0)} draws, "
        f"{ml_team_meta.get('loss_by_one', 0)} one-goal losses, and "
        f"{ml_team_meta.get('loss_by_two_plus', 0)} losses by 2+; `ml-fade` "
        f"scored {ml_team_fade.get('win', 0)}/"
        f"{ml_team_fade.get('n_scored', 0)} wins, "
        f"{ml_team_fade.get('draw', 0)} draws, "
        f"{ml_team_fade.get('loss_by_one', 0)} one-goal losses, and "
        f"{ml_team_fade.get('loss_by_two_plus', 0)} losses by 2+. Separate "
        f"`ml-meta` draw predictions hit {ml_draw_meta.get('draw_prediction_hits', 0)} "
        f"of {ml_draw_meta.get('n_scored', 0)} scored calls. The ledger has "
        f"{len(ml_model_keys)} first-recorded model keys; "
        f"{ml_multi_key_rows} rows list multiple keys. Do not pool these "
        "families or keys into a single model-performance claim.",
        "",
        f"{prices['quote_rows']} selections retain an exact, selected-side, "
        "named-book 1X2 price captured no later than decision and before kickoff; "
        f"{prices['n']} have settled scores and {prices['unscored_quote_rows']} "
        f"are unscored under the same-day cutoff. The settled subset contains "
        f"{prices['wins']} wins and {prices['draws']} {price_draw_word} "
        "(the draw loses on "
        f"1X2); mechanical flat-unit arithmetic at those captured quotes is "
        f"+{prices['profit_units']:.3f} units ({price_roi_text} on "
        f"n={prices['n']}). This is not an executable ROI: bookmaker "
        "access/execution is unverified. No market is shown to match the "
        "outcome ability at prices verified accessible to the operator. A "
        "broader 40-key alternative-quote join remains unreconciled to retained "
        "board keys. Earlier counts of 31 predecision/multi-source and 8 "
        "ticket-only matches do not establish selected prices or local "
        "availability, so they are excluded from ROI. No retained prices were "
        "found for double chance, DNB/Asian 0, Asian +0.5, or Asian +1. "
        "Therefore the "
        "alternative-market counts below are outcome diagnostics only, not "
        "achievable returns.",
        "",
        "## Scope, paths, and limitations",
        "",
        "| Retained path | Records | Treatment |",
        "|---|---:|---|",
        f"| Frozen 30-day operational pick archive | {len(op_all)} | One row per "
        "deduplicated 1X2 selection; immutable morning rows plus verified late "
        "additions. Main/shadow receipts and ticket legs joined separately. |",
        f"| Current {as_of} pick archive | "
        f"{forward_pick_count} "
        "| Retained pre-kickoff rows kept as forward tracking; no scores mixed "
        "into history. |",
        f"| ML research ledger | {len(ml_records)} | `ml-meta`, `ml-fade`, "
        "and draw predictions retained separately; first `model_key` preserved. |",
        f"| Older/non-verified operational snapshots | "
        f"{legacy_snapshot_count} "
        "| Kept in the selection CSV with exclusion reason; not performance-scored. |",
        f"| Older OU 2.5 picks | "
        f"{ou25_unique_count} "
        f"unique ({raw_ou25_count} raw archive rows) | Kept as a separate market; "
        "all lack a retained `kickoff_utc` witness. |",
        f"| Scored event-note predictions | {len(notes)} | Exported separately "
        "with no selected team; not treated as 1X2/DC/DNB/Asian tickets. |",
        "",
        f"Operational time audit: {len(op_all)} deduplicated 30-day selections; "
        f"{strict_pre_count} strictly pre-kickoff, {post_equal_count} post/equal, "
        f"and {unverified_time_count} without an explicit-offset "
        "decision/kickoff pair. The pre-kickoff "
        f"status counts are {dict(sorted(status_counts.items()))} (n={len(valid_op)}). "
        f"{status_counts['same_day_cutoff_missing_score']} same-day rows remain "
        "unscored under the retained audit cutoff; "
        f"{status_counts['rescheduled']} rescheduled rows are shown separately "
        "and excluded from the original-date market comparison.",
        "",
        "The archive stores score values but not a period marker. Accordingly, "
        "W/D/one-goal-loss/2+-loss below mean outcomes under the system's stored "
        "score join; **regulation-time status cannot be independently certified "
        "for every competition from these artifacts**. No extra-time inference "
        "was added.",
        "",
        "`edges_consensus.json` is a rule/validation registry, not a fixture-level "
        "historical prediction ledger. The operational event predictions are "
        "the retained `picks_*` rows; `ml_fade_research_ledger.json` is a distinct "
        "research path. `ou_2.5` archives and `event_notes` are kept separate. "
        "The older daily snapshots and unsafe regular-ledger revisions are "
        "inventory-only because the retained 30-day audit's frozen-output "
        "checks do not certify them as independent decision events.",
        "",
        "## Operational outcomes and same-sample market comparison",
        "",
        f"The same **n={len(op_settled)}** settled selected-team matches feed "
        "every row. W/D/L1/L2+ "
        "are team outcomes; `push` is specific to the market contract.",
        "",
    ]

    market_row = _outcome_rows(breakdowns, "operational_30d")
    if market_row:
        market_defs = [
            (
                "1X2",
                "market_1x2",
                "be_1x2_decimal_diagnostic",
                f"Strict sample: {prices['quote_rows']} prices; "
                f"{prices['n']} settled",
            ),
            (
                "Double chance / Asian +0.5",
                "double_chance",
                "be_double_chance_decimal_diagnostic",
                "No retained target-market quotes",
            ),
            (
                "DNB / Asian 0",
                "dnb_asian0",
                "be_dnb_asian0_decimal_diagnostic",
                "No retained target-market quotes",
            ),
            (
                "Asian +0.5",
                "asian_plus0_5",
                "be_asian_plus0_5_decimal_diagnostic",
                "No retained target-market quotes",
            ),
            (
                "Asian +1",
                "asian_plus1",
                "be_asian_plus1_decimal_diagnostic",
                "No retained target-market quotes",
            ),
        ]
        table_rows = []
        for label, prefix, be_key, price_note in market_defs:
            wins = int(market_row.get(f"{prefix}_win") or 0)
            pushes = int(market_row.get(f"{prefix}_push") or 0)
            losses = int(market_row.get(f"{prefix}_loss") or 0)
            be = market_row.get(be_key)
            table_rows.append([
                label,
                wins,
                pushes,
                losses,
                market_row.get("n_scored"),
                f"{float(be):.3f}" if be not in (None, "") else "n/a",
                price_note,
            ])
        lines += [
            md_table(
                [
                    "Market", "Wins", "Pushes", "Losses", "n",
                    "Break-even decimal price*", "Genuine price coverage",
                ],
                table_rows,
            ),
            "",
            "*Break-even-price diagnostics assume flat unit stakes and ignore "
            "commission/limits; they are not evidence those prices were offered "
            "or executable. Team outcomes are "
            f"{op_counts['win']}/{op_counts['draw']}/"
            f"{op_counts['loss_by_one']}/{op_counts['loss_by_two_plus']} "
            "(W/D/L1/L2+). The DC and Asian +0.5 rows are identical outcome "
            "rules on this sample.",
            "",
        ]

    lines += ["### Selected home/away team outcomes", ""]
    side_rows = _find_cell(breakdowns, "operational_30d", "selected_team_side")
    lines.append(md_table(
        [
            "Selected side", "n", "Scored", "Pending", "Ambiguous",
            "Rescheduled", "Missing score", "W", "D", "L1", "L2+",
            "Avoid defeat", "Avoid L2+",
        ],
        [[
            row["cell"], row["n"], row["n_scored"], row["n_pending"],
            row["n_ambiguous"], row["n_rescheduled"], row["n_missing_score"],
            row["win"], row["draw"], row["loss_by_one"],
            row["loss_by_two_plus"],
            f"{row['avoid_defeat_n']}/{row['n_scored']}",
            f"{row['avoid_heavy_loss_n']}/{row['n_scored']}",
        ] for row in side_rows],
    ) if side_rows else "No selected home/away team cells.")
    lines.append("")

    lines += ["### Outcome breakdown by primary operational rule", ""]
    rule_rows = _find_cell(breakdowns, "operational_30d", "primary_rule_family")
    lines.append(md_table(
        ["Primary rule family", "n", "Scored", "W", "D", "L1", "L2+", "Avoid defeat", "Avoid L2+"],
        [[
            row["cell"], row["n"], row["n_scored"], row["win"], row["draw"],
            row["loss_by_one"], row["loss_by_two_plus"],
            f"{row['avoid_defeat_n']}/{row['n_scored']}",
            f"{row['avoid_heavy_loss_n']}/{row['n_scored']}",
        ] for row in rule_rows],
    ) if rule_rows else "No operational rule cells.")
    lines.append("")

    lines += ["### Full-range operational probability bands", ""]
    prob_rows = _find_cell(breakdowns, "operational_30d", "probability_band_full_range")
    lines.append(md_table(
        ["avg_p band (%)", "n", "Scored", "W", "D", "L1", "L2+"],
        [[row["cell"], row["n"], row["n_scored"], row["win"], row["draw"],
          row["loss_by_one"], row["loss_by_two_plus"]] for row in prob_rows],
    ))
    lines.append("")

    lines += ["### Decision-time windows", ""]
    week_rows = _find_cell(breakdowns, "operational_30d", "decision_time_week")
    lines.append(md_table(
        ["SAST decision week", "n", "Scored", "W", "D", "L1", "L2+"],
        [[row["cell"], row["n"], row["n_scored"], row["win"], row["draw"],
          row["loss_by_one"], row["loss_by_two_plus"]] for row in week_rows],
    ))
    lines.append("")

    lines += ["### Publication-receipt and actual-ticket stages", ""]
    pub_rows = _find_cell(breakdowns, "operational_30d", "publication_receipt_stage")
    lines.append(md_table(
        [
            "Mutually exclusive receipt group", "n", "Scored", "Pending",
            "Ambiguous", "Rescheduled", "Missing score", "W", "D", "L1",
            "L2+",
        ],
        [[
            row["cell"], row["n"], row["n_scored"], row["n_pending"],
            row["n_ambiguous"], row["n_rescheduled"], row["n_missing_score"],
            row["win"], row["draw"], row["loss_by_one"],
            row["loss_by_two_plus"],
        ] for row in pub_rows],
    ))
    lines.append("")
    ticket_rows = _find_cell(breakdowns, "operational_30d", "ticket_stage")
    lines.append(md_table(
        [
            "Actual slip-leg match", "n", "Scored", "Pending", "Ambiguous",
            "Rescheduled", "Missing score", "W", "D", "L1", "L2+",
        ],
        [[
            row["cell"], row["n"], row["n_scored"], row["n_pending"],
            row["n_ambiguous"], row["n_rescheduled"], row["n_missing_score"],
            row["win"], row["draw"], row["loss_by_one"],
            row["loss_by_two_plus"],
        ] for row in ticket_rows],
    ))
    lines += [
        "",
        "Receipt keys identify fixture and market, not a side. No retained "
        "receipt is reported as `no retained receipt`, not proof of no send. "
        "Ticket attribution prefers exact retained team spelling; alias-aware "
        "fallback is used only when that fixture/side maps to one selection. "
        "For 2026-09-13 Viking/Kristiansund, the ticket ledger spells `Viking "
        "FK`; its one leg maps to the `2way-unanimous avg_p>=70` row. The "
        "earlier `Viking` `ml-meta avg_p>=65` decision remains a separate, "
        "timestamped selection and is not credited with that ticket leg. "
        "Repeated slip legs are counted on one row. An earlier 74-match "
        "ticket tally remains unreconciled to this 75-row match and is not "
        "used. The ledger retains no candidate-level rejection reason; "
        "non-ticketed rows are not labelled "
        "rejected.",
        "",
        "### Source-era breakdown (never pooled across eras)",
        "",
    ]
    era_rows = _find_cell(breakdowns, "operational_30d", "source_era")
    lines.append(md_table(
        ["model_version | sorted sources_used", "n", "Scored", "W", "D", "L1", "L2+"],
        [[row["cell"], row["n"], row["n_scored"], row["win"], row["draw"],
          row["loss_by_one"], row["loss_by_two_plus"]] for row in era_rows],
    ))
    lines += [
        "",
        "Operational picks do not retain a `model_key`; `model_version` and "
        "source mix above are the only available era labels. All detailed cells "
        f"include n in `market_suitability_breakdowns_{as_of}.csv`.",
        "",
        "## ML research ledger (separate populations; not additive)",
        "",
        "Every research row passed the stored first-seen-before-kickoff check "
        f"when kickoff text was parsed as SAST (lead range {ml_lead_range} "
        f"minutes). Status totals are {ml_status_counts['settled']} settled, "
        f"{ml_status_counts['pending']} pending, and "
        f"{ml_status_counts['ambiguous']} result conflicts. The first stored "
        f"`model_key` is preserved; {ml_multi_key_rows} rows list multiple "
        "keys in `model_keys_seen`. Matching to operational rows is exact "
        "fixture/date/side linking only, not proof that the model row caused "
        "publication.",
        "",
    ]

    ml_summary_rows = []
    for pop, label in (
        ("ml-meta_team", "ml-meta team-side picks"),
        ("ml-meta_draw", "ml-meta draw predictions"),
        ("ml-fade_team", "ml-fade team-side picks"),
    ):
        row = _outcome_rows(breakdowns, pop)
        population_rows = ml_rows_by_population.get(pop, [])
        if row and pop == "ml-meta_draw":
            ml_summary_rows.append([
                label, row["n"], row["n_scored"], "—", "—", "—", "—",
                row["n_pending"], row["n_ambiguous"], "not applicable",
                row["draw_prediction_hits"], row["draw_prediction_misses"],
            ])
        elif row:
            ml_summary_rows.append([
                label,
                row["n"],
                row["n_scored"],
                row["win"],
                row["draw"],
                row["loss_by_one"],
                row["loss_by_two_plus"],
                row["n_pending"],
                row["n_ambiguous"],
                f"{row['avoid_heavy_loss_n']}/{row['n_scored']}",
                "—",
                "—",
            ])
        elif population_rows:
            ml_summary_rows.append([
                label, len(population_rows), 0, 0, 0, 0, 0, 0, 0,
                "n/a", "—", "—",
            ])
    lines.append(md_table(
        [
            "Population", "n", "Scored", "W", "D", "L1", "L2+",
            "Pending", "Ambiguous", "Avoid L2+", "Draw hits", "Draw misses",
        ],
        ml_summary_rows,
    ))
    lines += ["", "### ML team picks by selected side", ""]
    ml_side_rows: list[list[Any]] = []
    for population, label in (
        ("ml-meta_team", "ml-meta"),
        ("ml-fade_team", "ml-fade"),
    ):
        for row in _find_cell(breakdowns, population, "selected_team_side"):
            ml_side_rows.append([
                label,
                row["cell"],
                row["n"],
                row["n_scored"],
                row["n_pending"],
                row["n_ambiguous"],
                row["n_missing_score"],
                row["win"],
                row["draw"],
                row["loss_by_one"],
                row["loss_by_two_plus"],
                f"{row['avoid_defeat_n']}/{row['n_scored']}",
                f"{row['avoid_heavy_loss_n']}/{row['n_scored']}",
            ])
    lines.append(md_table(
        [
            "Family", "Selected side", "n", "Scored", "Pending",
            "Ambiguous", "Missing score", "W", "D", "L1", "L2+",
            "Avoid defeat", "Avoid L2+",
        ],
        ml_side_rows,
    ))
    lines += ["", "### ML same-sample market outcomes (team picks only)", ""]
    ml_market_rows: list[list[Any]] = []
    for pop, label in (
        ("ml-meta_team", "ml-meta team"),
        ("ml-fade_team", "ml-fade team"),
    ):
        row = _outcome_rows(breakdowns, pop)
        if not row:
            continue
        for market_label, prefix, be_key in (
            ("1X2", "market_1x2", "be_1x2_decimal_diagnostic"),
            ("Double chance", "double_chance", "be_double_chance_decimal_diagnostic"),
            ("DNB / Asian 0", "dnb_asian0", "be_dnb_asian0_decimal_diagnostic"),
            ("Asian +0.5", "asian_plus0_5", "be_asian_plus0_5_decimal_diagnostic"),
            ("Asian +1", "asian_plus1", "be_asian_plus1_decimal_diagnostic"),
        ):
            break_even = row.get(be_key)
            ml_market_rows.append([
                label,
                market_label,
                row.get(f"{prefix}_win"),
                row.get(f"{prefix}_push"),
                row.get(f"{prefix}_loss"),
                row.get("n_scored"),
                f"{float(break_even):.3f}"
                if break_even not in (None, "") else "n/a",
            ])
    lines.append(md_table(
        [
            "Prediction family", "Market", "Wins", "Pushes", "Losses", "n",
            "Break-even price diagnostic",
        ],
        ml_market_rows,
    ))
    lines += [
        "",
        "These are outcome-only diagnostics over each family's own matched "
        "settled team selections; no real target-market quotes were retained.",
        "",
    ]
    draw_row = _outcome_rows(breakdowns, "ml-meta_draw")
    if draw_row:
        lines += [
            "",
            f"For `ml-meta`'s separate draw calls: "
            f"{draw_row['draw_prediction_hits']} draw hits and "
            f"{draw_row['draw_prediction_misses']} misses from "
            f"n={draw_row['n_scored']} scored; "
            f"{draw_row['n_pending']} pending. These are 1X2 draw predictions, "
            "not selected-team outcomes; no DC/DNB/Asian team market was assigned.",
        ]
    lines += [
        "",
        "The full model-key table, full-range probability deciles, first-seen "
        "weeks, and exact same-side linked-stage cells are in the breakdown CSV. "
        "All keys are listed there with n, outcome counts, and market diagnostics. "
        "Do not pool keys or treat this ledger's research rows as tickets.",
        "",
        "## Other-market predictions kept separate",
        "",
    ]

    note_summary = build_note_breakdowns(notes)
    if note_summary:
        lines.append(md_table(
            ["Retained note market", "n notes", "Scored", "Hits", "Misses", "Hit rate"],
            [[
                row["cell"], row["n"], row["n_scored"], row["win"],
                row["loss_by_one"],
                f"{row['win_rate_scored'] * 100:.1f}%"
                if row["win_rate_scored"] is not None else "n/a",
            ] for row in note_summary],
        ))
    else:
        lines.append("No scored event notes matched the pre-kickoff sample.")
    lines += [
        "",
        "These are ancillary event-note probabilities, not a selected team or "
        "the five target markets. Row-level note predictions are in the separate "
        "event-notes CSV; no ROI is inferred.",
        "",
        f"The {sum(r.get('population') == 'legacy_other_market_archive' for r in op_records)} "
        f"deduplicated `ou_2.5` selections represent {raw_ou25_count} raw archive "
        "rows and have no `kickoff_utc` timestamp; none is scored as a "
        "pre-match prediction. The "
        "retained October quote files contain 1X2/goal-total quotes, but no "
        "target-market quote records were found for double chance, DNB/Asian 0, "
        "or Asian +0.5/+1.",
        "",
        "## Early-stage coverage gap and isolated forward tracking",
        "",
        "The 30-day archives retain emitted selection rows and send receipts, "
        "but not a complete per-candidate evaluation/rejection ledger. "
        "`auto_tickets_slice_ledger.jsonl` stores actual slip legs only; a "
        "candidate-level ticket rejection reason was not found. A missing send "
        "receipt cannot prove non-publication.",
        "",
        "`src/edgefactory/scored_candidate_shadow.py` already provides an "
        "append-only, fail-soft, audit-only candidate ledger, wired at picks "
        "build/ticket stages. No retained `scored_candidate_shadow_*.jsonl` "
        "file was present in the local snapshot and the regular workflow report "
        "artifact did not cover JSONL. The daily workflow now has a dedicated "
        "30-day artifact for only those sidecar ledger files. This is evidence "
        "retention only: no model/source input, selection, ticket, or publication "
        "logic was changed and no workflow was dispatched.",
        "",
        "## Evidence files",
        "",
        f"- [Deduplicated selection/stage register](market_suitability_selections_{as_of}.csv)",
        f"- [All dimension and model-key breakdown cells]("
        f"market_suitability_breakdowns_{as_of}.csv)",
        f"- [Separate event-note market predictions](market_suitability_event_notes_{as_of}.csv)",
        f"- [Strict selected-price subset](market_suitability_prices_{as_of}.csv)",
        "",
        "Break-even prices are arithmetic diagnostics, not market offers. "
        "Outcome rates describe retained records and cannot authorize a market "
        "pivot or deployment. Validate untouched or subsequent forward data "
        "before any operational change.",
        "",
    ]
    return "\n".join(lines)


def build_price_csv_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        if row.get("odds_decimal") in (None, ""):
            continue
        output.append({
            "selection_id": row.get("selection_id"),
            "fixture_date": row.get("fixture_date"),
            "fixture": f"{row.get('home')} vs {row.get('away')}",
            "side": row.get("selection_side"),
            "probability_pct": row.get("decision_probability_pct"),
            "decision_time": row.get("decision_time"),
            "kickoff_time": row.get("kickoff_time"),
            "market": row.get("market"),
            "price_decimal": row.get("odds_decimal"),
            "bookmaker": row.get("bookmaker"),
            "source": row.get("odds_source"),
            "captured_at": row.get("odds_captured_at"),
            "result_status": row.get("result_status"),
            "score": row.get("score"),
            "outcome_category": row.get("outcome_category"),
            "market_1x2_result": row.get("market_1x2_result"),
            "exclusion_reason": row.get("exclusion_reason"),
            "executable_access_verified": False,
        })
    return output


def run_audit(as_of: str, output_dir: Path) -> dict[str, Any]:
    audit = read_json(LOCALDATA / "picks_audit_rolling.json", {})
    ml_ledger = read_json(LOCALDATA / "ml_fade_research_ledger.json", {})
    if not audit or not ml_ledger:
        raise SystemExit("Required retained local audit/ML ledger is missing.")
    start = str(audit.get("start") or "")[:10]
    end = str(audit.get("end") or "")[:10]
    if not start or not end:
        raise SystemExit("The rolling audit does not declare a date window.")

    raw_archives, files_by_key = load_raw_pick_archives()
    op_records, selected, archive_receipt = build_operational_records(
        start, end, audit, raw_archives, files_by_key
    )

    # Preserve raw references only during in-memory price and note joins.
    selected_by_key: dict[tuple, dict[str, Any]] = {}
    for row in selected:
        selected_by_key.setdefault(selection_key(row), row)
    for record in op_records:
        if record.get("population") == "operational_30d":
            key = (
                record["fixture_date"], ledger_team_key(record["home"]),
                ledger_team_key(record["away"]), record["market"],
                record["selection_side"],
            )
            record["_raw_source"] = selected_by_key.get(key, {})
    apply_operational_links_and_prices(op_records)

    ml_records = build_ml_records(ml_ledger, op_records)
    records = op_records + ml_records
    notes = build_note_records(op_records, selected, audit)
    breakdowns = build_breakdowns(records, start, end)
    breakdowns.extend(build_note_breakdowns(notes))

    # Add probability/week values used in grouping after all source rows are
    # joined; retain the original probabilities in the selection register.
    for row in records:
        try:
            value = float(row.get("decision_probability_pct"))
        except (TypeError, ValueError):
            value = None
        row["probability_band"] = probability_band(value) if value is not None else "unknown"
        row["decision_week"] = week_window(row.get("decision_time"))

    # Grouping consumes these transient fields; do it again now that they're set.
    breakdowns = build_breakdowns(records, start, end)
    breakdowns.extend(build_note_breakdowns(notes))

    price_rows = find_price_rows(records)
    price_stats = market_price_stats(price_rows)

    # Exact event/side link coverage for the audit narrative.
    link_stats: dict[str, Any] = {}
    for family in ("ml-meta", "ml-fade"):
        family_rows = [row for row in ml_records if row.get("family") == family]
        link_stats[family] = {
            "rows": len(family_rows),
            "same_side_links": sum(
                row.get("linked_operational_side_relation")
                == "same_side_exact_fixture_link" for row in family_rows
            ),
            "archive_only_same_side_links": sum(
                row.get("linked_operational_side_relation")
                == "same_side_archive_only_link" for row in family_rows
            ),
            "fixture_links": sum(
                row.get("linked_operational_side_relation")
                in {
                    "same_side_exact_fixture_link",
                    "same_fixture_different_side",
                    "same_fixture_draw_vs_team",
                } for row in family_rows
            ),
            "archive_only_fixture_links": sum(
                row.get("linked_operational_side_relation")
                in {
                    "same_side_archive_only_link",
                    "same_fixture_archive_only_link",
                } for row in family_rows
            ),
        }

    # Add the exact price sample size and link counts to the generated report.
    markdown = build_markdown(
        as_of=as_of,
        start=start,
        end=end,
        op_records=op_records,
        ml_records=ml_records,
        breakdowns=breakdowns,
        notes=notes,
        archive_receipt=archive_receipt,
        price_rows=price_rows,
        result_data=audit,
        link_stats=link_stats,
        raw_ou25_count=sum(
            norm_side(row.get("market")) == "ou_2.5"
            for row in raw_archives
        ),
    )
    markdown = markdown.replace(
        "Matching to operational rows is exact fixture/date/side linking only, "
        "not proof that the model row caused publication.",
        "Matching to operational rows is exact fixture/date/side linking only, "
        f"not proof that the model row caused publication. Exact same-side "
        f"links to frozen 30-day/current picks: ml-meta "
        f"{link_stats['ml-meta']['same_side_links']}/"
        f"{link_stats['ml-meta']['rows']}; ml-fade "
        f"{link_stats['ml-fade']['same_side_links']}/"
        f"{link_stats['ml-fade']['rows']}. Additional same-side links to "
        f"inventory-only snapshots: ml-meta "
        f"{link_stats['ml-meta']['archive_only_same_side_links']}; ml-fade "
        f"{link_stats['ml-fade']['archive_only_same_side_links']}.",
    )
    # Remove transient raw objects and computed helper values before export.
    for row in records:
        row.pop("_raw_source", None)
        row.pop("probability_band", None)
        row.pop("decision_week", None)
    for row in breakdowns:
        row.pop("n_team_scored", None)

    output_dir.mkdir(parents=True, exist_ok=True)
    selection_path = output_dir / f"market_suitability_selections_{as_of}.csv"
    breakdown_path = output_dir / f"market_suitability_breakdowns_{as_of}.csv"
    note_path = output_dir / f"market_suitability_event_notes_{as_of}.csv"
    price_path = output_dir / f"market_suitability_prices_{as_of}.csv"
    report_path = output_dir / f"MARKET-SUITABILITY-AUDIT-{as_of}.md"

    write_csv(selection_path, SELECTION_COLUMNS, records)
    write_csv(breakdown_path, BREAKDOWN_COLUMNS, breakdowns)
    write_csv(note_path, NOTE_COLUMNS, notes)
    write_csv(price_path, [
        "selection_id", "fixture_date", "fixture", "side", "probability_pct",
        "decision_time", "kickoff_time", "market", "price_decimal", "bookmaker",
        "source", "captured_at", "result_status", "score", "outcome_category",
        "market_1x2_result", "exclusion_reason", "executable_access_verified",
    ], build_price_csv_rows(price_rows))
    report_path.write_text(markdown, encoding="utf-8")
    return {
        "report": report_path,
        "selections": selection_path,
        "breakdowns": breakdown_path,
        "event_notes": note_path,
        "prices": price_path,
        "archive_receipt": archive_receipt,
        "operational_rows": len(op_records),
        "operational_safe": sum(
            row.get("population") == "operational_30d"
            and row.get("pre_kickoff_analysis_eligible") for row in op_records
        ),
        "ml_rows": len(ml_records),
        "note_rows": len(notes),
        "price_stats": price_stats,
        "link_stats": link_stats,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--as-of", default="2026-10-08",
        help="Date label for generated report filenames (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "docs" / "operator" / "audits",
        help="Output directory; localdata is read-only.",
    )
    args = parser.parse_args()
    date.fromisoformat(args.as_of)
    result = run_audit(args.as_of, args.output_dir)
    print(f"report: {result['report']}")
    print(f"selection rows: {result['selections']} ({result['operational_rows']} operational)")
    print(f"breakdowns: {result['breakdowns']}")
    print(f"event-note rows: {result['note_rows']}")
    print(f"strict named-book quotes: {result['price_stats']}")
    print(f"ML links: {result['link_stats']}")
    print(f"safe archive loader: {result['archive_receipt']}")


if __name__ == "__main__":
    main()

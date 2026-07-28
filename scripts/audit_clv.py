#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import importlib.util
import json
import os
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.clv import (  # noqa: E402
    beat_later_price,
    build_pick_id,
    implied_prob_delta,
    odds_to_implied_prob,
    raw_odds_delta,
    summarize_by,
    summarize_clv,
)

LOCALDATA = ROOT / "localdata"
SNAPSHOT_FIELDS = [
    "pick_id",
    "match_date",
    "home",
    "away",
    "league",
    "rule_name",
    "bucket",
    "market",
    "pick",
    "observed_odds",
    "implied_prob",
    "snapshot_label",
    "captured_at_utc",
    "odds_provider",
    "bookmaker",
    "source_run_date",
    "avg_p",
    "min_p",
    "edge_status",
    "live_odds_matched",
    "used_input_odds_fallback",
    "odds_match_method",
]


def _load_picks_today_module():
    path = ROOT / "scripts" / "picks_today.py"
    spec = importlib.util.spec_from_file_location("edgefactory_picks_today", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load scripts/picks_today.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"missing input file: {path}")
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError(f"expected JSON list in {path}")
    return [row for row in data if isinstance(row, dict)]


def _snapshot_path(run_date: str) -> Path:
    return LOCALDATA / f"clv_snapshots_{str(run_date)[:7]}.csv.gz"


def _unmatched_path(run_date: str) -> Path:
    return LOCALDATA / f"clv_unmatched_{run_date}.json"


def _read_snapshot_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with gzip.open(path, "rt", newline="") as fh:
        return list(csv.DictReader(fh))


def _write_snapshot_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=SNAPSHOT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in SNAPSHOT_FIELDS})


def _dedupe_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("pick_id") or ""),
        str(row.get("snapshot_label") or ""),
        str(row.get("source_run_date") or ""),
    )


def _coerce_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if out <= 1.0:
        return None
    return out


def _pick_rule_name(pick: dict[str, Any]) -> str:
    return str(
        pick.get("edge_rule")
        or pick.get("rule")
        or pick.get("display_rule")
        or "unknown-rule"
    )


def _capture_rows(run_date: str, label: str, input_path: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    picks = _read_json_list(input_path)
    picks_today = _load_picks_today_module()

    should_refresh = label != "pick_time"
    previous_refresh = os.environ.get("BZZOIRO_ODDS_REFRESH")
    if should_refresh:
        os.environ["BZZOIRO_ODDS_REFRESH"] = "1"

    try:
        odds_stats_by_date: dict[str, dict[str, int]] = {}
        odds_index_by_date: dict[str, dict] = {}
        picks_by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for pick in picks:
            picks_by_date[str(pick.get("date") or run_date)[:10]].append(pick)
        for match_date in sorted(picks_by_date):
            bzz_stats: dict[str, int] = {}
            scouting_stats: dict[str, int] = {}
            odds_index_by_date[match_date] = {
                "primary": picks_today.bzzoiro_odds_bundle(match_date, stats=bzz_stats),
                "secondary": picks_today.scoutingstats_odds_bundle(match_date, stats=scouting_stats),
            }
            odds_stats_by_date[match_date] = {
                "bzz_valid_keys": bzz_stats.get("valid_keys", 0),
                "scouting_valid_keys": scouting_stats.get("valid_keys", 0),
            }
    finally:
        if should_refresh:
            if previous_refresh is None:
                os.environ.pop("BZZOIRO_ODDS_REFRESH", None)
            else:
                os.environ["BZZOIRO_ODDS_REFRESH"] = previous_refresh

    captured_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows: list[dict[str, Any]] = []
    matched = 0
    missing = 0
    fallback = 0
    exact_matches = 0
    alias_time_matches = 0
    alias_unique_matches = 0
    bzz_matches = 0
    scouting_matches = 0
    betexplorer_matches = 0
    unmatched_details: list[dict[str, Any]] = []

    for pick in picks:
        match_date = str(pick.get("date") or run_date)[:10]
        rule_name = _pick_rule_name(pick)
        pick_id = build_pick_id(
            match_date,
            pick.get("home"),
            pick.get("away"),
            pick.get("market"),
            pick.get("pick"),
            rule_name,
        )
        live_pick = dict(pick)
        original_odds = _coerce_float(pick.get("odds"))
        odds_pair = odds_index_by_date.get(match_date, {})
        primary_odds = odds_pair.get("primary", {})
        secondary_odds = odds_pair.get("secondary", {})
        picks_today.enrich_with_live_odds([live_pick], primary_odds, secondary_odds)
        match_method = str(live_pick.get("odds_match_method") or "")
        live_odds_matched = match_method in {"exact", "alias_time", "alias_unique", "alias_fuzzy", "betexplorer"}
        if live_odds_matched:
            matched += 1
            if live_pick.get("odds_source") == picks_today.BZZOIRO_ODDS_SOURCE:
                bzz_matches += 1
            elif live_pick.get("odds_source") == picks_today.SCOUTINGSTATS_ODDS_SOURCE:
                scouting_matches += 1
            elif live_pick.get("odds_source") == picks_today.BETEXPLORER_ODDS_SOURCE:
                betexplorer_matches += 1
            if match_method == "exact":
                exact_matches += 1
            elif match_method == "alias_time":
                alias_time_matches += 1
            elif match_method == "alias_unique":
                alias_unique_matches += 1
            elif match_method == "betexplorer":
                pass  # counted in betexplorer_matches above
        else:
            unmatched_details.append(
                {
                    "date": match_date,
                    "kickoff": pick.get("kickoff"),
                    "home": pick.get("home"),
                    "away": pick.get("away"),
                    "league": pick.get("league"),
                    "market": pick.get("market"),
                    "pick": pick.get("pick"),
                    "rule_name": rule_name,
                    "match_method": match_method or "none",
                    "home_key": picks_today.odds_match_team_key(pick.get("home") or ""),
                    "away_key": picks_today.odds_match_team_key(pick.get("away") or ""),
                    "nearby_bzzoiro_candidates": picks_today.nearby_odds_candidates(pick, primary_odds),
                    "nearby_scoutingstats_candidates": picks_today.nearby_odds_candidates(pick, secondary_odds),
                }
            )
        observed_odds = _coerce_float(live_pick.get("odds"))
        if observed_odds is None:
            missing += 1
        elif match_method == "fallback" and original_odds is not None:
            fallback += 1

        row = {
            "pick_id": pick_id,
            "match_date": match_date,
            "home": pick.get("home") or "",
            "away": pick.get("away") or "",
            "league": pick.get("league") or "",
            "rule_name": rule_name,
            "bucket": pick.get("bucket") or "",
            "market": pick.get("market") or "",
            "pick": pick.get("pick") or "",
            "observed_odds": observed_odds if observed_odds is not None else "",
            "implied_prob": round(odds_to_implied_prob(observed_odds), 6) if observed_odds else "",
            "snapshot_label": label,
            "captured_at_utc": str(live_pick.get("odds_captured_at") or captured_at),
            "odds_provider": live_pick.get("odds_source") or "",
            "bookmaker": live_pick.get("bookmaker") or "",
            "source_run_date": run_date,
            "avg_p": pick.get("avg_p") if pick.get("avg_p") is not None else "",
            "min_p": pick.get("min_p") if pick.get("min_p") is not None else "",
            "edge_status": pick.get("edge_status") or "",
            "live_odds_matched": "1" if live_odds_matched else "0",
            "used_input_odds_fallback": "1" if (observed_odds is not None and match_method == "fallback" and original_odds is not None) else "0",
            "odds_match_method": match_method,
        }
        rows.append(row)

    unmatched_path = _unmatched_path(run_date)
    unmatched_path.write_text(json.dumps(unmatched_details, indent=2))

    return rows, {
        "picks_read": len(picks),
        "betexplorer_matches": betexplorer_matches,
        "live_odds_matched": matched,
        "exact_matches": exact_matches,
        "alias_time_matches": alias_time_matches,
        "alias_unique_matches": alias_unique_matches,
        "bzz_matches": bzz_matches,
        "scouting_matches": scouting_matches,
        "missing_odds": missing,
        "used_input_odds_fallback": fallback,
        "dates_seen": len(odds_stats_by_date),
        "unmatched_file": str(unmatched_path),
        "unmatched_count": len(unmatched_details),
    }


def capture(run_date: str, label: str, input_path: Path) -> int:
    rows, stats = _capture_rows(run_date, label, input_path)
    path = _snapshot_path(run_date)
    existing = _read_snapshot_rows(path)
    merged: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in existing:
        merged[_dedupe_key(row)] = row

    duplicates = 0
    written = 0
    for row in rows:
        key = _dedupe_key(row)
        if key in merged:
            duplicates += 1
            continue
        merged[key] = row
        written += 1

    ordered = sorted(
        merged.values(),
        key=lambda r: (
            str(r.get("source_run_date") or ""),
            str(r.get("match_date") or ""),
            str(r.get("pick_id") or ""),
            str(r.get("snapshot_label") or ""),
            str(r.get("captured_at_utc") or ""),
        ),
    )
    _write_snapshot_rows(path, ordered)

    print(f"CLV capture — {run_date} [{label}]")
    print(f"  picks read: {stats['picks_read']}")
    print(f"  live odds matched: {stats['live_odds_matched']}")
    print(f"    bzzoiro: {stats['bzz_matches']}")
    print(f"    scoutingstats: {stats['scouting_matches']}")
    print(f"    betexplorer: {stats.get('betexplorer_matches', 0)}")
    print(f"    exact: {stats['exact_matches']}")
    print(f"    alias_time: {stats['alias_time_matches']}")
    print(f"    alias_unique: {stats['alias_unique_matches']}")
    print(f"  input fallback used: {stats['used_input_odds_fallback']}")
    print(f"  missing odds: {stats['missing_odds']}")
    print(f"  rows written: {written}")
    print(f"  duplicates skipped: {duplicates}")
    print(f"  unmatched diagnostics: {stats['unmatched_count']} -> {stats['unmatched_file']}")
    print(f"  snapshot file: {path}")
    return 0


def _month_iter(start: str, end: str) -> list[str]:
    months: list[str] = []
    current = datetime.strptime(start[:7] + "-01", "%Y-%m-%d").date()
    end_month = datetime.strptime(end[:7] + "-01", "%Y-%m-%d").date()
    while current <= end_month:
        months.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months


def _load_report_rows(start: str, end: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for month in _month_iter(start, end):
        path = LOCALDATA / f"clv_snapshots_{month}.csv.gz"
        if not path.exists():
            continue
        for row in _read_snapshot_rows(path):
            run_date = str(row.get("source_run_date") or "")[:10]
            if start <= run_date <= end:
                rows.append(row)
    return rows


def _comparison_rows(snapshot_rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    by_pick: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in snapshot_rows:
        by_pick[str(row.get("pick_id") or "")].append(row)

    comparisons: list[dict[str, Any]] = []
    unmatched = 0
    insufficient_snapshots = 0
    for pick_id, rows in by_pick.items():
        rows.sort(key=lambda r: (str(r.get("captured_at_utc") or ""), str(r.get("snapshot_label") or "")))
        first = rows[0]
        first_odds = _coerce_float(first.get("observed_odds"))
        if first_odds is None:
            unmatched += 1

        comparable = len(rows) >= 2
        if comparable:
            last = rows[-1]
            last_odds = _coerce_float(last.get("observed_odds"))
            last_label = last.get("snapshot_label") or ""
        else:
            insufficient_snapshots += 1
            last_odds = None
            last_label = ""

        comparisons.append(
            {
                "pick_id": pick_id,
                "rule_name": first.get("rule_name") or "UNKNOWN",
                "bucket": first.get("bucket") or "UNKNOWN",
                "first_odds": first_odds,
                "last_odds": last_odds,
                "first_label": first.get("snapshot_label") or "",
                "last_label": last_label,
                "snapshot_count": len(rows),
                "raw_odds_delta": raw_odds_delta(first_odds, last_odds),
                "implied_prob_delta": implied_prob_delta(first_odds, last_odds),
                "beat_later_price": beat_later_price(first_odds, last_odds),
            }
        )
    return comparisons, {
        "unmatched_picks": unmatched,
        "insufficient_snapshots": insufficient_snapshots,
    }


def _write_report_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _write_report_md(path: Path, start: str, end: str, overall: dict[str, Any], by_rule: dict[str, dict], by_bucket: dict[str, dict], meta: dict[str, int]) -> None:
    lines = [
        f"# Edge Factory — CLV report ({start} to {end})",
        "",
        "## Overall",
        "",
        f"- total unique picks: {overall.get('total_picks', 0)}",
        f"- picks with at least two prices: {overall.get('with_two_prices', 0)}",
        f"- average raw odds delta: {overall.get('avg_raw_odds_delta')}",
        f"- average implied-probability delta: {overall.get('avg_implied_prob_delta')}",
        f"- beat-later-price rate: {overall.get('beat_later_price_rate')}",
        f"- beat-later-price sample: {overall.get('beat_later_price_n', 0)}",
        f"- unmatched picks: {meta.get('unmatched_picks', 0)}",
        f"- picks with fewer than two snapshots: {meta.get('insufficient_snapshots', 0)}",
        "",
        "## By rule",
        "",
    ]
    if not by_rule:
        lines.append("- none")
    else:
        for rule, summary in by_rule.items():
            lines.append(
                f"- `{rule}`: n={summary.get('total_picks', 0)}, "
                f"two_prices={summary.get('with_two_prices', 0)}, "
                f"avg_raw={summary.get('avg_raw_odds_delta')}, "
                f"avg_ip={summary.get('avg_implied_prob_delta')}, "
                f"beat_rate={summary.get('beat_later_price_rate')}"
            )
    lines.extend(["", "## By bucket", ""])
    if not by_bucket:
        lines.append("- none")
    else:
        for bucket, summary in by_bucket.items():
            lines.append(
                f"- `{bucket}`: n={summary.get('total_picks', 0)}, "
                f"two_prices={summary.get('with_two_prices', 0)}, "
                f"avg_raw={summary.get('avg_raw_odds_delta')}, "
                f"avg_ip={summary.get('avg_implied_prob_delta')}, "
                f"beat_rate={summary.get('beat_later_price_rate')}"
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def report(start: str, end: str) -> int:
    snapshot_rows = _load_report_rows(start, end)
    comparisons, meta = _comparison_rows(snapshot_rows)
    overall = summarize_clv(comparisons)
    by_rule = summarize_by(comparisons, "rule_name")
    by_bucket = summarize_by(comparisons, "bucket")

    payload = {
        "start": start,
        "end": end,
        "overall": overall,
        "by_rule": by_rule,
        "by_bucket": by_bucket,
        "meta": meta,
    }

    json_path = LOCALDATA / "clv_report_rolling.json"
    md_path = LOCALDATA / f"clv_report_{end}.md"
    _write_report_json(json_path, payload)
    _write_report_md(md_path, start, end, overall, by_rule, by_bucket, meta)

    print(f"CLV report — {start} to {end}")
    print(f"  total unique picks: {overall.get('total_picks', 0)}")
    print(f"  picks with at least two prices: {overall.get('with_two_prices', 0)}")
    print(f"  picks with fewer than two snapshots: {meta.get('insufficient_snapshots', 0)}")
    print(f"  average implied-probability delta: {overall.get('avg_implied_prob_delta')}")
    print(f"  beat-later-price rate: {overall.get('beat_later_price_rate')}")
    print(f"  json: {json_path}")
    print(f"  markdown: {md_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="CLV capture and report utility.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    cap = sub.add_parser("capture", help="Capture CLV odds snapshots for picks.")
    cap.add_argument("--date", required=True, help="Run date for picks (YYYY-MM-DD).")
    cap.add_argument("--label", required=True, help="Snapshot label, e.g. pick_time or latest.")
    cap.add_argument(
        "--input",
        default=str(LOCALDATA / "picks_today.json"),
        help="Path to input picks JSON (default: localdata/picks_today.json).",
    )

    rep = sub.add_parser("report", help="Build a CLV report from snapshot files.")
    rep.add_argument("--start", required=True, help="Start run date (YYYY-MM-DD).")
    rep.add_argument("--end", required=True, help="End run date (YYYY-MM-DD).")

    args = parser.parse_args()
    if args.cmd == "capture":
        return capture(args.date, args.label, Path(args.input))
    if args.cmd == "report":
        return report(args.start, args.end)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

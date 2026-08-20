#!/usr/bin/env python3
"""Certified operational-edge firing and source-capture freshness tripwire.

The detector is visibility-only.  It distinguishes rules the live picker can
actually emit from certified analytical variants, keeps future-planner rows out
of the historical firing window, and checks exact source files (so ``bzzoiro``
can never accidentally inspect ``bzzoiro_odds``).

Usage:
    PYTHONPATH=src python3 scripts/edge_firing_tripwire.py
    PYTHONPATH=src python3 scripts/edge_firing_tripwire.py \
        --edge-silent-days 21 --source-stale-days 7
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"

# Active CSV sources.  Roles are telemetry labels, not weights or selection
# changes.  BetExplorer remains absent because its capture is retired.
SOURCES = (
    ("forebet", "date", "core_voter"),
    ("statarea", "date", "core_voter"),
    ("scoutingstats", "date", "voter_and_price"),
    ("vitibet", "date", "thin_voter"),
    ("zulubet", "date", "core_voter"),
    ("predictz", "date", "shadow"),
    ("windrawwin", "date", "shadow"),
    ("afootballreport", "date", "research"),
    ("betclan", "date", "partial_voter"),
    ("freesupertips", "date", "not_ready"),
    ("bettingclosed", "date", "confirmation_results"),
    ("bzzoiro", "date", "model_voter"),
)

PICKS_GLOBS = ("picks_*.json", "picks_today.json", "picks_morning_*.json")
QUALIFIED_TOKENS = (
    "min_p",
    "home-only",
    "away-only",
    "odds-",
    "bc-confirms",
    "predictz-confirms",
    "windrawwin-confirms",
    "freesupertips-confirms",
)
RULE_NWAY = re.compile(r"(\d+)way", re.I)
RULE_THRESHOLD = re.compile(r">=\s*([\d.]+)")


def _source_files(ld: Path, name: str) -> list[Path]:
    """Return only this source's monthly files, with a legacy-file fallback.

    The old ``f"{name}*.csv.gz"`` pattern let the ``bzzoiro`` check select
    ``bzzoiro_odds_YYYY-MM.csv.gz``.  A four-digit year immediately after the
    source name is an unambiguous monthly capture file.
    """
    pattern = f"{name}_[0-9][0-9][0-9][0-9]-[0-9][0-9].csv.gz"
    monthly = sorted(ld.glob(pattern))
    if monthly:
        return monthly
    legacy = ld / f"{name}.csv.gz"
    return [legacy] if legacy.exists() else []


def _newest_source_date(ld: Path, name: str, date_col: str) -> tuple[str | None, str | None]:
    """Return ``(newest_row_date, newest_file)`` from the newest exact file."""
    files = _source_files(ld, name)
    if not files:
        return None, None
    newest = files[-1]
    max_date = None
    try:
        with gzip.open(newest, "rt", encoding="utf-8", errors="replace") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                value = str(row.get(date_col) or "")[:10]
                if len(value) == 10 and value.replace("-", "").isdigit():
                    if max_date is None or value > max_date:
                        max_date = value
    except OSError:
        return None, newest.name
    return max_date, newest.name


def _load_certified_edges(ld: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads((ld / "edges_consensus.json").read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return [
        edge
        for edge in data.get("edges", [])
        if isinstance(edge, dict) and edge.get("status") == "certified"
    ]


def _is_qualified(rule: str) -> bool:
    lowered = rule.lower()
    return any(token in lowered for token in QUALIFIED_TOKENS)


def _operational_edge_rules(edges: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """Return rules the current picker can emit and transparent exclusions.

    ``picks_today.load_thresholds`` prefers canonical unqualified consensus
    rules.  Qualified variants remain certified evidence for analysis/purity,
    but the picker cannot label an operational row with them.  Monitoring them
    as if they should fire created six permanent false alarms.
    """
    ml_rules: list[dict[str, Any]] = []
    canonical_1x2: dict[int, tuple[float, dict[str, Any]]] = {}
    canonical_binary: dict[str, tuple[float, dict[str, Any]]] = {}
    ignored: list[str] = []

    for edge in edges:
        rule = str(edge.get("rule") or "").strip()
        market = str(edge.get("market") or "1x2")
        if not rule:
            continue
        if "ml-meta" in rule.lower():
            ml_rules.append(edge)
            continue
        if _is_qualified(rule):
            ignored.append(rule)
            continue

        nway_match = RULE_NWAY.search(rule)
        threshold_match = RULE_THRESHOLD.search(rule)
        if not nway_match or not threshold_match:
            ignored.append(rule)
            continue
        n_way = int(nway_match.group(1))
        threshold = float(threshold_match.group(1))
        if market == "1x2":
            old = canonical_1x2.get(n_way)
            if old is None or threshold < old[0]:
                canonical_1x2[n_way] = (threshold, edge)
        else:
            old = canonical_binary.get(market)
            if old is None or threshold < old[0]:
                canonical_binary[market] = (threshold, edge)

    monitored = ml_rules
    monitored.extend(item[1] for item in canonical_1x2.values())
    monitored.extend(item[1] for item in canonical_binary.values())
    monitored.sort(key=lambda edge: str(edge.get("rule") or ""))
    ignored.sort()
    return monitored, ignored


def _load_pick_rows(ld: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen_files: set[Path] = set()
    for glob in PICKS_GLOBS:
        for path in sorted(ld.glob(glob)):
            if path in seen_files:
                continue
            seen_files.add(path)
            try:
                data = json.loads(path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(data, list):
                rows.extend(row for row in data if isinstance(row, dict))
    return rows


def _pick_day(row: dict[str, Any]) -> str:
    return str(row.get("date") or row.get("_archive_day") or "")[:10]


def _scan_edge_firing(
    ld: Path,
    rules: list[dict[str, Any]],
    silent_days: int,
    today: date,
) -> list[dict[str, Any]]:
    """Count operational firings in ``[today-silent_days, today]`` only."""
    picks = _load_pick_rows(ld)
    cutoff = (today - timedelta(days=silent_days)).isoformat()
    today_text = today.isoformat()
    findings: list[dict[str, Any]] = []

    for edge in rules:
        rule = str(edge.get("rule") or "")
        if not rule:
            continue
        matched = [
            pick
            for pick in picks
            if (pick.get("edge_rule") or pick.get("rule")) == rule
            and cutoff <= _pick_day(pick) <= today_text
        ]
        all_through_today = [
            pick
            for pick in picks
            if (pick.get("edge_rule") or pick.get("rule")) == rule
            and _pick_day(pick) <= today_text
        ]
        last = max((_pick_day(pick) for pick in all_through_today), default=None)
        findings.append(
            {
                "rule": rule,
                "decay": (edge.get("decay") or {}).get("verdict"),
                "n_last_window": len(matched),
                "last_fired": last,
                "silent": len(matched) == 0,
            }
        )
    return findings


def _ml_ceiling_check(ld: Path, findings_edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Classify a silent ML rule whose current maximum is >15pp below its bar."""
    state_path = ld / "ml_meta_state.json"
    if not state_path.exists():
        return []
    try:
        state = json.loads(state_path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    max_p = state.get("max_ml_p")
    if max_p is None:
        return []

    ceilings: list[dict[str, Any]] = []
    for finding in findings_edges:
        rule = str(finding.get("rule") or "")
        if "ml-meta" not in rule or not finding.get("silent"):
            continue
        match = RULE_THRESHOLD.search(rule)
        if not match:
            continue
        threshold = float(match.group(1))
        gap = threshold - float(max_p) * 100.0
        if gap > 15.0:
            ceilings.append(
                {
                    "rule": rule,
                    "live_max_ml_p": round(float(max_p) * 100.0, 1),
                    "threshold": threshold,
                    # Compatibility key retained for existing readers.
                    "lowest_threshold": threshold,
                    "gap_pp": round(gap, 1),
                    "ceiling": True,
                }
            )
    return ceilings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Operational-edge firing and source-capture freshness tripwire"
    )
    parser.add_argument("--edge-silent-days", type=int, default=14)
    parser.add_argument("--source-stale-days", type=int, default=7)
    parser.add_argument("--localdata", default=str(LOCALDATA))
    args = parser.parse_args()

    ld = Path(args.localdata)
    today = date.today()
    certified = _load_certified_edges(ld)
    operational, ignored = _operational_edge_rules(certified)
    edge_findings = _scan_edge_firing(ld, operational, args.edge_silent_days, today)
    ceilings = _ml_ceiling_check(ld, edge_findings)
    ceiling_by_rule = {item["rule"]: item for item in ceilings}

    findings: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "edge_silent_days": args.edge_silent_days,
        "source_stale_days": args.source_stale_days,
        "edges": edge_findings,
        "ceilings": ceilings,
        "ignored_non_operational_rules": ignored,
        "sources": [],
    }

    for item in sorted(edge_findings, key=lambda value: (value["silent"], value["rule"])):
        ceiling = ceiling_by_rule.get(item["rule"])
        if ceiling:
            print(
                f"  [🔇 CEILED] {item['rule']}: live max ml_p "
                f"{ceiling['live_max_ml_p']:.1f}% vs threshold "
                f"{ceiling['threshold']:.0f}% (gap {ceiling['gap_pp']:.1f}pp)"
            )
        else:
            flag = "🔇 SILENT" if item["silent"] else "ok"
            print(
                f"  [{flag}] {item['rule']}  decay={item['decay']}  "
                f"fired_last_{args.edge_silent_days}d={item['n_last_window']}  "
                f"last={item['last_fired'] or 'never'}"
            )

    if ignored:
        print(f"  [info] {len(ignored)} certified analytical rule(s) excluded from firing alarms")

    stale_cutoff = (today - timedelta(days=args.source_stale_days)).isoformat()
    for name, date_col, role in SOURCES:
        newest_date, newest_file = _newest_source_date(ld, name, date_col)
        if newest_date is None:
            status = "no files" if newest_file is None else f"unreadable ({newest_file})"
            print(f"  [..] {name} ({role}): {status}")
            findings["sources"].append(
                {
                    "name": name,
                    "role": role,
                    "newest_date": None,
                    "newest_file": newest_file,
                    "stale": None,
                }
            )
            continue
        stale = newest_date < stale_cutoff
        flag = "⚠️ STALE" if stale else "ok"
        print(f"  [{flag}] {name} ({role}): newest row {newest_date} (file {newest_file})")
        findings["sources"].append(
            {
                "name": name,
                "role": role,
                "newest_date": newest_date,
                "newest_file": newest_file,
                "stale": stale,
            }
        )

    # A CEILED edge is a more specific classification of the same silent edge;
    # count it once, not once as SILENT and again as CEILED.
    ceiling_rules = set(ceiling_by_rule)
    silent_only = [
        item for item in edge_findings if item["silent"] and item["rule"] not in ceiling_rules
    ]
    stale_sources = [item for item in findings["sources"] if item.get("stale")]
    findings["warn_count"] = len(silent_only) + len(ceilings) + len(stale_sources)

    out = ld / "edge_firing_tripwire.json"
    out.write_text(json.dumps(findings, indent=2, sort_keys=True))
    print(
        f"\n=== edge firing tripwire: {len(silent_only)} silent operational edge(s), "
        f"{len(ceilings)} ceiling(s), {len(stale_sources)} stale source cache(s), "
        f"{len(ignored)} analytical rule(s) excluded ==="
    )
    if findings["warn_count"]:
        print(
            "Warnings are visibility-only; they do not select bets. "
            "Repair capture cadence or an operational firing path—never lower a gate merely to clear a warning."
        )
    print(f"full findings -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

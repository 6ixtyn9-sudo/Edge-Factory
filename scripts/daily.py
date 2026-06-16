#!/usr/bin/env python3
"""Edge Factory — single trigger for the full nightly pipeline.

Usage
-----
  python3 scripts/daily.py
  python3 scripts/daily.py --picks-only
  python3 scripts/daily.py --date 2026-06-15
  python3 scripts/daily.py --picks-only --date 2026-06-15
  python3 scripts/daily.py --future-days 2

Steps (always in this order):
  1. capture_daily     — fetch latest data from all sources (D30 lookback)
  2. backfill_results  — fill missing hs/gs from donor sources (D30, auto)
  3. build_warehouse   — materialise CSVs into warehouse.duckdb
  4. mine_consensus    — walk-forward edge certification → edges_consensus.json
  5. decay_monitor     — 60-day health audit, auto-bench circuit breaker
  6. assay_purity      — context verdicts → purity_registry.json
  7. picks_today       — certified picks for target date → stdout + picks_today.json
  8. future planner    — runs picks_today engine for N days → picks_next_2days.json + picks_calendar.csv
  9. sync_supabase     — push edges + picks to Postgres read model

--picks-only skips steps 1–3 (useful when data is already fresh).

No separate scripts/picks_future.py is required: the future planner is intentionally
kept inline here to avoid another pipeline script drifting from picks_today.py.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "localdata"


def run(cmd: str, label: str | None = None) -> None:
    display = label or cmd
    print(f"\n>>> {display}")
    result = subprocess.run(cmd, shell=True, cwd=ROOT)
    if result.returncode != 0:
        print(f"\nFAILED: {display}")
        sys.exit(result.returncode)


def run_capture(cmd: str, label: str | None = None) -> str:
    """Run a command, stream stdout, and return captured stdout text.

    Used by the inline future planner so each date can reuse scripts/picks_today.py
    without importing private implementation details from it.
    """
    display = label or cmd
    print(f"\n>>> {display}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(result.stdout, end="")
    if result.returncode != 0:
        print(f"\nFAILED: {display}")
        sys.exit(result.returncode)
    return result.stdout


def generate_daily_report(target_date: str) -> None:
    """Write a human-readable .txt summary of picks_today.json."""
    picks_file = ROOT / "localdata" / "picks_today.json"
    report_file = REPORT_DIR / f"picks_{target_date}.txt"

    if not picks_file.exists():
        print("No picks file found — skipping report")
        return

    try:
        picks = json.loads(picks_file.read_text())
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"Edge Factory Picks — {target_date}",
            "=" * 60,
            f"Generated at: {now_ts}",
            "",
        ]

        buckets: dict[str, list[dict[str, Any]]] = {}
        for p in picks:
            b = p.get("bucket", "UNKNOWN")
            buckets.setdefault(b, []).append(p)

        bucket_order = [
            "CERTIFIED_CLEAN",
            "CAUTION",
            "WATCHLIST_NO_ODDS",
            "WATCHLIST_UNKNOWN_CTX",
            "SKIPPED_VETO",
            "SKIPPED_DEAD_EDGE",
        ]
        bucket_labels = {
            "CERTIFIED_CLEAN": "CERTIFIED CLEAN PICKS",
            "CAUTION": "CAUTION PICKS",
            "WATCHLIST_NO_ODDS": "WATCHLIST — NO ODDS",
            "WATCHLIST_UNKNOWN_CTX": "WATCHLIST — UNKNOWN CONTEXT",
            "SKIPPED_VETO": "SKIPPED — VETO CONTEXT",
            "SKIPPED_DEAD_EDGE": "SKIPPED — DEAD EDGE",
        }

        for b in bucket_order:
            bpicks = buckets.get(b, [])
            lines.append(f"\n{bucket_labels.get(b, b)}")
            lines.append("=" * 60)
            if not bpicks:
                lines.append("  (none)")
                continue

            for p in sorted(bpicks, key=lambda x: -float(x.get("avg_p") or 0)):
                if p.get("odds") is not None:
                    try:
                        odds = f"@{float(p['odds']):.2f}"
                    except (TypeError, ValueError):
                        odds = f"@{p['odds']}"
                    if p.get("odds_source") == "bzzoiro_odds" and p.get("bookmaker"):
                        odds += f" {p['bookmaker']}"
                    elif p.get("odds_source") == "zulubet":
                        odds += " zulubet"
                else:
                    odds = "@n/a"

                label = p.get("display_rule") or p.get("rule", "?")
                ctx = p.get("ctx", {}) or {}
                w_str = f"  w={p['w_score']:.2f}" if p.get("w_score") is not None else ""
                match = str(p.get("match", ""))[:42]
                pick = str(p.get("pick", "?")).upper()
                avg_p = float(p.get("avg_p") or 0)

                lines.append(
                    f"  [{label}] {match:42s} -> "
                    f"{pick:5s}  avg {avg_p:.0f}%{w_str} {odds}"
                )
                lines.append(
                    f"     bucket={b}  "
                    f"league={ctx.get('league_raw', 'UNKNOWN')}:{ctx.get('league', '?')}  "
                    f"odds_band={ctx.get('odds_band_name', '?')}:{ctx.get('odds_band', '?')}"
                )

        lines.append("")
        lines.append("⚠️  Flat stakes only. Best odds inflate ROI (~halve it).")
        lines.append("⚠️  Bet only what you can afford to lose.")

        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report_file.write_text("\n".join(lines))
        print(f"Daily report written: {report_file}")
    except Exception as exc:  # noqa: BLE001 - report generation must never kill pipeline
        print(f"Could not generate report: {exc}")


def _pick_date(pick: dict[str, Any], fallback: str) -> str:
    for key in ("date", "picked_for", "target_date", "match_date"):
        value = pick.get(key)
        if value:
            return str(value)[:10]
    return fallback


def write_future_outputs(all_picks: list[dict[str, Any]], days: int) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_file = REPORT_DIR / f"picks_next_{days}days.json"
    csv_file = REPORT_DIR / "picks_calendar.csv"

    json_file.write_text(json.dumps(all_picks, indent=2, sort_keys=True))

    fieldnames = [
        "date",
        "bucket",
        "match",
        "home",
        "away",
        "pick",
        "avg_p",
        "w_score",
        "odds",
        "bookmaker",
        "odds_source",
        "rule",
        "display_rule",
        "market_type",
        "odds_tier",
        "league_verdict",
        "team_verdict",
        "odds_band_verdict",
    ]

    with csv_file.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for p in all_picks:
            ctx = p.get("ctx", {}) or {}
            writer.writerow(
                {
                    "date": _pick_date(p, ""),
                    "bucket": p.get("bucket"),
                    "match": p.get("match"),
                    "home": p.get("home"),
                    "away": p.get("away"),
                    "pick": p.get("pick"),
                    "avg_p": p.get("avg_p"),
                    "w_score": p.get("w_score"),
                    "odds": p.get("odds"),
                    "bookmaker": p.get("bookmaker"),
                    "odds_source": p.get("odds_source"),
                    "rule": p.get("rule"),
                    "display_rule": p.get("display_rule"),
                    "market_type": p.get("market_type"),
                    "odds_tier": p.get("odds_tier"),
                    "league_verdict": ctx.get("league"),
                    "team_verdict": ctx.get("team"),
                    "odds_band_verdict": ctx.get("odds_band"),
                }
            )

    print(f"Future planner wrote: {json_file}")
    print(f"Future calendar wrote: {csv_file}")


def run_future_planner(start_date: str, days: int) -> None:
    """Inline N-day planner using scripts/picks_today.py as the only pick engine."""
    if days <= 0:
        print("future_days <= 0 — skipping future planner")
        return

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    all_picks: list[dict[str, Any]] = []
    picks_file = ROOT / "localdata" / "picks_today.json"

    for offset in range(days):
        target = (start + timedelta(days=offset)).isoformat()
        run_capture(
            f"PYTHONPATH=src python3 scripts/picks_today.py {target}",
            f"future planner: picks_today {target}",
        )

        if not picks_file.exists():
            print(f"No picks_today.json for {target}; continuing")
            continue

        try:
            day_picks = json.loads(picks_file.read_text())
            if not isinstance(day_picks, list):
                print(f"picks_today.json for {target} was not a list; continuing")
                continue
            for p in day_picks:
                if isinstance(p, dict):
                    p.setdefault("date", target)
                    p.setdefault("picked_for", target)
                    all_picks.append(p)
        except Exception as exc:  # noqa: BLE001 - keep planner robust across sparse future days
            print(f"Could not read picks for {target}: {exc}")

    all_picks.sort(
        key=lambda p: (
            _pick_date(p, "9999-99-99"),
            str(p.get("bucket", "")),
            -float(p.get("w_score") or 0),
            -float(p.get("avg_p") or 0),
            str(p.get("match", "")),
        )
    )
    write_future_outputs(all_picks, days)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Edge Factory full nightly pipeline trigger.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument(
        "--picks-only",
        action="store_true",
        help=(
            "Skip capture / backfill / warehouse build (data already fresh). "
            "Re-mines, audits, and generates picks."
        ),
    )
    ap.add_argument(
        "--date",
        default=None,
        help="Target date for picks_today (YYYY-MM-DD). Defaults to today.",
    )
    ap.add_argument(
        "--future-days",
        type=int,
        default=2,
        help="Days ahead for inline future planner (default: 2).",
    )
    args = ap.parse_args()

    target_date = args.date or date.today().isoformat()

    print("=== Edge Factory Daily Pipeline ===")
    print(f"    target date : {target_date}")
    print(f"    future_days : {args.future_days}")
    print(f"    mode        : {'picks-only (skip capture/backfill/build)' if args.picks_only else 'full run'}")
    print(f"    started at  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not args.picks_only:
        run("python3 scripts/capture_daily.py --skip-build", "capture_daily (D30 lookback)")
        run("python3 scripts/backfill_results.py --days 30", "backfill_results (D30)")
        run("python3 scripts/build_warehouse.py", "build_warehouse")

    run("python3 scripts/mine_consensus.py", "mine_consensus")
    run("PYTHONPATH=src python3 scripts/decay_monitor.py", "decay_monitor")
    run("PYTHONPATH=src python3 scripts/assay_purity.py", "assay_purity")
    run(f"PYTHONPATH=src python3 scripts/picks_today.py {target_date}", f"picks_today {target_date}")

    generate_daily_report(target_date)
    run_future_planner(target_date, args.future_days)

    run("python3 scripts/sync_supabase.py", "sync_supabase")

    print(f"\n=== Done — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Edge Factory — single trigger for the full daily pipeline.

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
  4. build_entities    — learn canonical league/team aliases → entity_registry.json
  5. mine_consensus    — walk-forward edge certification → edges_consensus.json
  6. decay_monitor     — 60-day health audit, auto-bench circuit breaker
  7. assay_purity      — context verdicts → purity_registry.json
  8. picks_today       — certified picks for target date → stdout + picks_today.json
  9. audit_clv         — capture pick-time and end-of-run CLV snapshots + rolling report (non-critical)
 10. audit_recent_picks — score archived daily picks against settled results (non-critical)
 11. future planner    — inline N-day per-date reports, reusing picks_today.py
 12. sync_supabase     — push target-date picks + certified edges to Postgres

--picks-only skips steps 1–3 (useful when data is already fresh).

No separate scripts/picks_future.py is required: the future planner is intentionally
kept inline here to avoid another pipeline script drifting from picks_today.py.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "localdata"
PICKS_TODAY_FILE = REPORT_DIR / "picks_today.json"
DEFAULT_LOCAL_TZ = "Africa/Johannesburg"


def local_tz() -> ZoneInfo:
    return ZoneInfo(DEFAULT_LOCAL_TZ)


def make_run_as_of() -> str:
    return datetime.now(local_tz()).isoformat(timespec="seconds")


def picks_env_prefix(run_as_of: str) -> str:
    return f"EDGE_FACTORY_RUN_AS_OF={shlex.quote(run_as_of)}"


def archived_picks_file(target_date: str) -> Path:
    return REPORT_DIR / f"picks_{target_date}.json"


def archive_target_picks(target_date: str, picks_text: str | None) -> None:
    if picks_text is None:
        return
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    archived_picks_file(target_date).write_text(picks_text)


def run(cmd: str, label: str | None = None) -> None:
    """Run a pipeline step and stream its output."""
    display = label or cmd
    print(f"\n>>> {display}")
    result = subprocess.run(cmd, shell=True, cwd=ROOT)
    if result.returncode != 0:
        print(f"\nFAILED: {display}")
        sys.exit(result.returncode)


def run_soft(cmd: str, label: str | None = None) -> None:
    """Run a non-critical step and continue on failure."""
    display = label or cmd
    print(f"\n>>> {display}")
    result = subprocess.run(cmd, shell=True, cwd=ROOT)
    if result.returncode != 0:
        print(f"WARNING: non-critical step failed: {display}")


def run_capture(cmd: str, label: str | None = None) -> str:
    """Run a command and return captured combined stdout/stderr.

    This is used only for the inline future planner. We keep future-date output
    concise, while still printing full output if the underlying picks engine fails.
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
    if result.returncode != 0:
        print(result.stdout, end="")
        print(f"\nFAILED: {display}")
        sys.exit(result.returncode)
    return result.stdout


def print_pick_run_summary(output: str) -> None:
    """Print a compact summary from picks_today.py output."""
    interesting_prefixes = (
        "Weighted consensus:",
        "bzzoiro_odds enrichment",
        "Summary:",
    )
    printed = False
    for line in output.splitlines():
        if line.startswith(interesting_prefixes):
            print(f"  {line}")
            printed = True
    if not printed:
        print("  picks_today completed")


def load_picks_file() -> list[dict[str, Any]]:
    if not PICKS_TODAY_FILE.exists():
        return []
    data = json.loads(PICKS_TODAY_FILE.read_text())
    if not isinstance(data, list):
        return []
    return [p for p in data if isinstance(p, dict)]


def tag_picks(picks: list[dict[str, Any]], target: str) -> list[dict[str, Any]]:
    tagged: list[dict[str, Any]] = []
    for pick in picks:
        p = dict(pick)
        p.setdefault("date", target)
        p.setdefault("picked_for", target)
        tagged.append(p)
    return tagged


def restore_target_picks(target_picks_text: str | None) -> None:
    """Restore picks_today.json to target-date picks before sync_supabase.

    The future planner has to call picks_today.py for tomorrow/next days, and
    picks_today.py always writes localdata/picks_today.json. Without this restore,
    sync_supabase would accidentally sync the last future day instead of the
    requested target date.
    """
    if target_picks_text is None:
        return
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    PICKS_TODAY_FILE.write_text(target_picks_text)


def format_kickoff(pick: dict[str, Any]) -> str:
    """Human report kickoff display. Always show missing kickoff explicitly."""
    for key in ("kickoff", "time", "start_time", "ko"):
        value = pick.get(key)
        if value not in (None, ""):
            return str(value)
    return "n/a"


def generate_daily_report(target_date: str) -> None:
    """Write a human-readable .txt summary of picks_today.json."""
    report_file = REPORT_DIR / f"picks_{target_date}.txt"

    if not PICKS_TODAY_FILE.exists():
        print("No picks file found — skipping report")
        return

    try:
        picks = load_picks_file()
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
            buckets.setdefault(str(b), []).append(p)

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
                kickoff = format_kickoff(p)
                pick = str(p.get("pick", "?")).upper()
                avg_p = float(p.get("avg_p") or 0)

                lines.append(
                    f"  [{label}] {match:42s} KO {kickoff:5s} -> "
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
    """Write the aggregate machine-readable future-picks file.

    Human-readable output stays date-native: localdata/picks_YYYY-MM-DD.txt.
    No calendar-style CSV is produced; it was redundant with the per-date reports.
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_file = REPORT_DIR / f"picks_next_{days}days.json"
    json_file.write_text(json.dumps(all_picks, indent=2, sort_keys=True))
    print(f"Future planner wrote: {json_file}")


def run_future_planner(start_date: str, days: int, target_picks: list[dict[str, Any]], run_as_of: str) -> None:
    """Inline N-day planner using scripts/picks_today.py as the only pick engine.

    The target day is not re-run. It is reused from the already generated
    picks_today.json, so stdout stays clean and the target-day report remains the
    primary visible pick output.
    """
    if days <= 0:
        print("future_days <= 0 — skipping future planner")
        return

    print(f"\n>>> future planner ({days}-day reports)")

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    all_picks: list[dict[str, Any]] = tag_picks(target_picks, start_date)
    print(f"  {start_date}: reused target picks ({len(target_picks)} rows)")

    for offset in range(1, days):
        target = (start + timedelta(days=offset)).isoformat()
        output = run_capture(
            f"{picks_env_prefix(run_as_of)} PYTHONPATH=src python3 scripts/picks_today.py {target}",
            f"future planner: picks_today {target}",
        )
        print_pick_run_summary(output)

        if not PICKS_TODAY_FILE.exists():
            print(f"  {target}: no picks_today.json; continuing")
            continue

        try:
            day_picks = load_picks_file()
            all_picks.extend(tag_picks(day_picks, target))
            generate_daily_report(target)
            print(f"  {target}: added {len(day_picks)} rows")
        except Exception as exc:  # noqa: BLE001 - keep planner robust across sparse future days
            print(f"  {target}: could not read picks: {exc}")

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
        description="Edge Factory full daily pipeline trigger.",
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
    ap.add_argument(
        "--backfill-days",
        type=int,
        default=30,
        help="Result backfill window for full runs (default: 30).",
    )
    ap.add_argument(
        "--force-repick",
        action="store_true",
        help="Ignore archived picks_YYYY-MM-DD.json and regenerate target-date picks.",
    )
    args = ap.parse_args()

    target_date = args.date or date.today().isoformat()
    run_as_of = make_run_as_of()

    print("=== Edge Factory Daily Pipeline ===")
    print(f"    target date : {target_date}")
    print(f"    future_days : {args.future_days}")
    print(f"    run_as_of   : {run_as_of}")
    print(f"    force_repick: {args.force_repick}")
    print(f"    backfill_days: {args.backfill_days if not args.picks_only else 'skipped'}")
    print(f"    mode        : {'picks-only (skip capture/backfill/build)' if args.picks_only else 'full run'}")
    print(f"    started at  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not args.picks_only:
        run("python3 scripts/capture_daily.py --skip-build", "capture_daily (D30 lookback)")
        run(
            f"python3 scripts/backfill_results.py --days {args.backfill_days}",
            f"backfill_results (D{args.backfill_days})",
        )
        run("python3 scripts/build_warehouse.py", "build_warehouse")

    run("PYTHONPATH=src python3 scripts/build_entity_registry.py", "build_entity_registry")
    run("python3 scripts/mine_consensus.py", "mine_consensus")
    run("PYTHONPATH=src python3 scripts/decay_monitor.py", "decay_monitor")
    run("PYTHONPATH=src python3 scripts/assay_purity.py", "assay_purity")

    target_archive = archived_picks_file(target_date)
    if target_archive.exists() and not args.force_repick:
        print(f"\n>>> restore frozen target picks {target_date}")
        target_picks_text = target_archive.read_text()
        restore_target_picks(target_picks_text)
        print(f"  reused archive: {target_archive}")
    else:
        run(
            f"{picks_env_prefix(run_as_of)} PYTHONPATH=src python3 scripts/picks_today.py {target_date}",
            f"picks_today {target_date}",
        )
        target_picks_text = PICKS_TODAY_FILE.read_text() if PICKS_TODAY_FILE.exists() else None
        archive_target_picks(target_date, target_picks_text)

    run_soft(
        f"PYTHONPATH=src python3 scripts/audit_clv.py capture --date {target_date} --label pick_time",
        f"audit_clv capture {target_date} [pick_time]",
    )
    clv_start = (datetime.strptime(target_date, "%Y-%m-%d").date() - timedelta(days=30)).isoformat()

    target_picks = load_picks_file()

    generate_daily_report(target_date)
    run_future_planner(target_date, args.future_days, target_picks, run_as_of)

    restore_target_picks(target_picks_text)
    run_soft(
        f"PYTHONPATH=src python3 scripts/audit_clv.py capture --date {target_date} --label end_of_run",
        f"audit_clv capture {target_date} [end_of_run]",
    )
    run_soft(
        f"PYTHONPATH=src python3 scripts/audit_clv.py report --start {clv_start} --end {target_date}",
        f"audit_clv report {clv_start}..{target_date}",
    )
    run_soft(
        f"PYTHONPATH=src python3 scripts/audit_recent_picks.py --end {target_date} --days 30",
        f"audit_recent_picks {target_date} [30d]",
    )
    run("python3 scripts/sync_supabase.py", "sync_supabase")

    print(f"\n=== Done — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Edge Factory — single trigger for the full nightly pipeline.

Usage
-----
  python3 scripts/daily.py                  # full run: capture → build → mine → … → sync
  python3 scripts/daily.py --picks-only     # skip capture+build; re-mine + picks for today
  python3 scripts/daily.py --date 2026-06-15          # picks for a specific date (full run)
  python3 scripts/daily.py --picks-only --date 2026-06-15  # re-mine + picks for a past date

Steps (always in this order):
  1. capture_daily     — fetch latest data from all sources (D30 lookback)
  2. build_warehouse   — materialise CSVs into warehouse.duckdb
  3. mine_consensus    — walk-forward edge certification → edges_consensus.json
  4. decay_monitor     — 60-day health audit, auto-bench circuit breaker
  5. assay_purity      — context verdicts → purity_registry.json
  6. picks_today       — certified picks for today (+ tomorrow) → stdout + picks_today.json
  7. sync_supabase     — push edges + picks to Postgres read model

--picks-only skips steps 1–2 (useful when data is already fresh).
"""

import argparse
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "localdata"


def run(cmd: str, label: str | None = None) -> None:
    display = label or cmd
    print(f"\n>>> {display}")
    result = subprocess.run(cmd, shell=True, cwd=ROOT)
    if result.returncode != 0:
        print(f"\nFAILED: {display}")
        sys.exit(result.returncode)


def generate_daily_report(target_date: str) -> None:
    """Write a human-readable .txt summary of picks_today.json."""
    picks_file = ROOT / "localdata" / "picks_today.json"
    report_file = REPORT_DIR / f"picks_{target_date}.txt"

    if not picks_file.exists():
        print("No picks file found — skipping report")
        return

    try:
        import json
        picks = json.loads(picks_file.read_text())

        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"Edge Factory Picks — {target_date}",
            "=" * 60,
            f"Generated at: {now_ts}",
            "",
        ]

        buckets: dict[str, list] = {}
        for p in picks:
            b = p.get("bucket", "UNKNOWN")
            buckets.setdefault(b, []).append(p)

        BUCKET_ORDER = [
            "CERTIFIED_CLEAN", "CAUTION",
            "WATCHLIST_NO_ODDS", "WATCHLIST_UNKNOWN_CTX",
            "SKIPPED_VETO", "SKIPPED_DEAD_EDGE",
        ]
        BUCKET_LABELS = {
            "CERTIFIED_CLEAN":    "CERTIFIED CLEAN PICKS",
            "CAUTION":            "CAUTION PICKS",
            "WATCHLIST_NO_ODDS":  "WATCHLIST — NO ODDS",
            "WATCHLIST_UNKNOWN_CTX": "WATCHLIST — UNKNOWN CONTEXT",
            "SKIPPED_VETO":       "SKIPPED — VETO CONTEXT",
            "SKIPPED_DEAD_EDGE":  "SKIPPED — DEAD EDGE",
        }

        for b in BUCKET_ORDER:
            bpicks = buckets.get(b, [])
            lines.append(f"\n{BUCKET_LABELS.get(b, b)}")
            lines.append("=" * 60)
            if not bpicks:
                lines.append("  (none)")
                continue
            for p in sorted(bpicks, key=lambda x: -x.get("avg_p", 0)):
                if p.get("odds") is not None:
                    try:
                        o = f"@{float(p['odds']):.2f}"
                    except (TypeError, ValueError):
                        o = f"@{p['odds']}"
                    if p.get("odds_source") == "bzzoiro_odds" and p.get("bookmaker"):
                        o += f" {p['bookmaker']}"
                    elif p.get("odds_source") == "zulubet":
                        o += " zulubet"
                else:
                    o = "@n/a"
                label = p.get("display_rule") or p.get("rule", "?")
                ctx = p.get("ctx", {}) or {}
                w_str = f"  w={p['w_score']:.2f}" if p.get("w_score") is not None else ""
                lines.append(
                    f"  [{label}] {p['match'][:42]:42s} -> "
                    f"{p['pick'].upper():5s}  avg {p['avg_p']:.0f}%{w_str} {o}"
                )
                lines.append(
                    f"     bucket={b}  "
                    f"league={ctx.get('league_raw','UNKNOWN')}:{ctx.get('league','?')}  "
                    f"odds_band={ctx.get('odds_band_name','?')}:{ctx.get('odds_band','?')}"
                )

        lines.append("")
        lines.append("⚠️  Flat stakes only. Best odds inflate ROI (~halve it).")
        lines.append("⚠️  Bet only what you can afford to lose.")

        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report_file.write_text("\n".join(lines))
        print(f"Daily report written: {report_file}")

    except Exception as e:
        print(f"Could not generate report: {e}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Edge Factory full pipeline trigger.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument(
        "--picks-only", action="store_true",
        help="Skip capture and warehouse build (data already fresh). "
             "Re-mines, audits, and generates picks.",
    )
    ap.add_argument(
        "--date", default=None,
        help="Target date for picks_today (YYYY-MM-DD). Defaults to today.",
    )
    args = ap.parse_args()

    target_date = args.date or date.today().isoformat()

    print("=== Edge Factory Pipeline ===")
    print(f"    target date : {target_date}")
    print(f"    mode        : {'picks-only (skip capture+build)' if args.picks_only else 'full run'}")
    print(f"    started at  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not args.picks_only:
        run("python3 scripts/capture_daily.py --skip-build", "capture_daily (D30 lookback)")
        run("python3 scripts/build_warehouse.py",            "build_warehouse")

    run("python3 scripts/mine_consensus.py",                 "mine_consensus")
    run("PYTHONPATH=src python3 scripts/decay_monitor.py",   "decay_monitor")
    run("PYTHONPATH=src python3 scripts/assay_purity.py",    "assay_purity")
    run(f"PYTHONPATH=src python3 scripts/picks_today.py {target_date}",
        f"picks_today {target_date}")

    generate_daily_report(target_date)

    run("python3 scripts/sync_supabase.py",                  "sync_supabase")

    print(f"\n=== Done — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")


if __name__ == "__main__":
    main()

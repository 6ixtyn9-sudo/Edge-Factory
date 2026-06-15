#!/usr/bin/env python3
"""Nightly pipeline entrypoint with daily report.

Runs the full sequence and generates a dated picks report.
"""

import subprocess
import sys
from pathlib import Path
from datetime import date, datetime

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "localdata"

def run(cmd):
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=ROOT)
    if result.returncode != 0:
        print(f"FAILED: {cmd}")
        sys.exit(result.returncode)

def generate_daily_report(today: str):
    """Create a simple human-readable report for the day."""
    picks_file = ROOT / "localdata" / "picks_today.json"
    report_file = REPORT_DIR / f"picks_{today}.txt"
    
    if not picks_file.exists():
        print("No picks file found — skipping report")
        return
    
    try:
        import json
        picks = json.loads(picks_file.read_text())
        
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"Edge Factory Picks — {today}",
            "=" * 60,
            f"Generated at: {now_ts}",
            "",
        ]
        
        for p in picks:
            o = f"@{p.get('odds', 'n/a')}"
            label = p.get("display_rule") or p.get("rule", "?")
            bucket = p.get("bucket", "?")
            ctx = p.get("ctx", {}) or {}
            ctx_line = (
                f"     bucket={bucket}  "
                f"league={ctx.get('league_raw', 'UNKNOWN')}:{ctx.get('league', '?')}  "
                f"odds_band={ctx.get('odds_band_name', '?')}:{ctx.get('odds_band', '?')}"
            )
            lines.append(f"  [{label}] {p['match'][:42]:42s} -> {p['pick'].upper():5s}  avg {p['avg_p']:.0f}% {o}")
            lines.append(ctx_line)
        
        lines.append("")
        lines.append("⚠️  Flat stakes only. Best odds inflate ROI (~halve it).")
        
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report_file.write_text("\n".join(lines))
        print(f"Daily report written: {report_file}")
        
    except Exception as e:
        print(f"Could not generate report: {e}")

def main():
    print("=== Edge Factory Nightly Run ===")
    
    run("python3 scripts/capture_daily.py --skip-build")
    run("python3 scripts/build_warehouse.py")
    run("python3 scripts/mine_consensus.py")
    run("PYTHONPATH=src python3 scripts/decay_monitor.py")
    run("PYTHONPATH=src python3 scripts/assay_purity.py")
    run("PYTHONPATH=src python3 scripts/picks_today.py")
    
    # Generate dated report
    today = date.today().isoformat()
    generate_daily_report(today)
    
    run("python3 scripts/sync_supabase.py")
    
    print("\n=== Nightly run complete ===")

if __name__ == "__main__":
    main()

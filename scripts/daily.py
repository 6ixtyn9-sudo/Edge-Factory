#!/usr/bin/env python3
"""Edge Factory — single orchestrator for autonomous daily maintenance and smart accumulating ledgers.

Usage
-----
  python3 scripts/daily.py
  python3 scripts/daily.py --picks-only
  python3 scripts/daily.py --date 2026-06-15
  python3 scripts/daily.py --future-days 2

Autonomous 3-Hour Background Service & Accumulating Ledger:
  python3 scripts/daily.py --auto-run
      Runs an autonomous service every 3 hours. Completely eliminates manual human involvement:
      - If today's official archive does not exist yet (06:00 / First Run): executes the complete heavy maintenance pipeline, builds DuckDB, locks the morning picks, and syncs to Supabase.
      - If today's archive already exists (Intraday Runs): automatically scans for newly appearing fixtures/odds (the late slate). It perfectly retains all existing locked morning picks to prevent intraday performance corruption, automatically appends any brand new certified bets to the official ledger, captures qualitative time-of-day CLV snapshots, and syncs late-slate discoveries directly to Supabase.

  python3 scripts/daily.py --auto-once
      Performs exactly one autonomous iteration of the smart accumulating schedule and exits.

Deliberate Human-Intervention Modes (Optional):
  python3 scripts/daily.py --forecast-refresh
      Performs a standalone non-official forecast refresh, saving to localdata/forecast_*.json without modifying official ledgers.

  python3 scripts/daily.py --promote-forecast localdata/forecast_2026-06-19_1100.json
      Promotes an external forecast file to overwrite the official tracked performance record.

  python3 scripts/daily.py --clv-only
      Runs CLV monitoring capture and rolling report without running miners or picks.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.util import (  # noqa: E402
    kickoff_date,
    ledger_team_key,
    honest_display_label,
    heal_ledger_labels,
    strip_retired_top_scores,
)

REPORT_DIR = ROOT / "localdata"
PICKS_TODAY_FILE = REPORT_DIR / "picks_today.json"
DEFAULT_LOCAL_TZ = "Africa/Johannesburg"

# Human-readable report buckets. This list must remain a superset of the engine's
# operational buckets: the official .txt report is an operator decision surface,
# so it may never silently omit rows that exist in the audited JSON ledger.
BUCKET_CERTIFIED_CLEAN = "CERTIFIED_CLEAN"
BUCKET_CAUTION = "CAUTION"
BUCKET_WATCHLIST_NO_ODDS = "WATCHLIST_NO_ODDS"
BUCKET_WATCHLIST_UNCORROBORATED_PRICE = "WATCHLIST_UNCORROBORATED_PRICE"
BUCKET_WATCHLIST_SUSPECT_PRICE = "WATCHLIST_SUSPECT_PRICE"
BUCKET_WATCHLIST_UNKNOWN_CTX = "WATCHLIST_UNKNOWN_CTX"
BUCKET_SKIPPED_VETO = "SKIPPED_VETO"
BUCKET_SKIPPED_DEAD_EDGE = "SKIPPED_DEAD_EDGE"

BUCKET_ORDER = [
    BUCKET_CERTIFIED_CLEAN,
    BUCKET_CAUTION,
    BUCKET_WATCHLIST_NO_ODDS,
    BUCKET_WATCHLIST_UNCORROBORATED_PRICE,
    BUCKET_WATCHLIST_SUSPECT_PRICE,
    BUCKET_WATCHLIST_UNKNOWN_CTX,
    BUCKET_SKIPPED_VETO,
    BUCKET_SKIPPED_DEAD_EDGE,
]

BUCKET_LABELS = {
    BUCKET_CERTIFIED_CLEAN: "CERTIFIED CLEAN PICKS",
    BUCKET_CAUTION: "CAUTION PICKS",
    BUCKET_WATCHLIST_NO_ODDS: "WATCHLIST — NO MATCHED ODDS",
    BUCKET_WATCHLIST_UNCORROBORATED_PRICE: "WATCHLIST — UNCORROBORATED SCOUTINGSTATS PRICE",
    BUCKET_WATCHLIST_SUSPECT_PRICE: "WATCHLIST — SUSPECT FUZZY PRICE MATCH",
    BUCKET_WATCHLIST_UNKNOWN_CTX: "WATCHLIST — UNKNOWN CONTEXT",
    BUCKET_SKIPPED_VETO: "SKIPPED — VETO CONTEXT",
    BUCKET_SKIPPED_DEAD_EDGE: "SKIPPED — DEAD EDGE",
}


def get_build_entity_registry_cmd() -> str:
    path = REPORT_DIR / "entity_registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            inputs = data.get("inputs", {})
            if inputs.get("full_scan_completed") is True:
                return "PYTHONPATH=src python3 scripts/build_entity_registry.py"
        except Exception:
            pass
    return "PYTHONPATH=src python3 scripts/build_entity_registry.py --full-scan"


def local_tz() -> ZoneInfo:
    return ZoneInfo(DEFAULT_LOCAL_TZ)


def make_run_as_of() -> str:
    return datetime.now(local_tz()).isoformat(timespec="seconds")


def picks_env_prefix(run_as_of: str) -> str:
    return f"EDGE_FACTORY_RUN_AS_OF={shlex.quote(run_as_of)}"


def result_refresh_day(target_date: str) -> str:
    """The intraday audit settles completed calendar-day fixtures only.

    Refreshing yesterday's existing result donors is bounded and avoids the
    D30 all-source capture sweep, while allowing late-final scores to enter the
    warehouse/overlay on the next three-hourly cadence.
    """
    return (datetime.strptime(target_date, "%Y-%m-%d").date() - timedelta(days=1)).isoformat()


def result_refresh_cmd(target_date: str) -> str:
    return (
        "PYTHONPATH=src python3 scripts/refresh_result_sources.py "
        f"--date {result_refresh_day(target_date)}"
    )


def archived_picks_file(target_date: str) -> Path:
    return REPORT_DIR / f"picks_{target_date}.json"


def get_actual_kickoff_date(pick: dict[str, Any], fallback: str) -> str:
    """Extract the real match date from kickoff time, fallback to provided date.

    Resolves ISO ``YYYY-MM-DD...`` and European ``DD-MM[, HH:MM]`` /
    ``DD.MM[.YYYY]`` kickoffs to a calendar date (year inferred from the
    fallback). Bare ``HH:MM`` kickoffs carry no date and fall back to the
    pick's own date field — a bare time cannot name a calendar day.
    """
    for key in ("kickoff", "time", "start_time", "ko"):
        val = pick.get(key)
        if val not in (None, ""):
            resolved = kickoff_date(val, fallback_date=fallback)
            if resolved:
                return resolved
    return _pick_date(pick, fallback)


def archive_picks_by_kickoff(picks: list[dict[str, Any]], fallback_date: str) -> None:
    """Distribute picks to archives based on their actual kickoff date.

    Each archived row is re-dated to its resolved kickoff date so the archive
    filename, the row's ``date`` field, and the audit's exact-date settlement
    all agree on one calendar day. Without this, a pick scanned a day early
    for a next-day fixture (kickoff ``DD-MM``) stays filed under the scan day
    and can never match the result donor's date.
    """
    if not picks:
        return
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Group picks by their actual date
    by_date: dict[str, list[dict[str, Any]]] = {}
    for p in picks:
        d = get_actual_kickoff_date(p, fallback_date)
        row = dict(p)
        row["date"] = d
        by_date.setdefault(d, []).append(row)

    for d, date_picks in by_date.items():
        archive_path = archived_picks_file(d)
        
        # Load existing archive to merge (avoid duplicates)
        existing: list[dict[str, Any]] = []
        if archive_path.exists():
            try:
                existing = json.loads(archive_path.read_text())
                if not isinstance(existing, list): existing = []
            except Exception:
                existing = []
        
        # Use our merge logic to add new picks or update existing ones
        merged, _, superseded = autonomous_intraday_merge(existing, date_picks)
        if superseded:
            print(f"  superseded {superseded} archived row(s) with fresh picks in {d} archive")
        healed = heal_ledger_labels(merged)
        if healed:
            print(f"  self-healed {healed} stale display labels in {d} archive")
        archive_path.write_text(json.dumps(merged, indent=2, sort_keys=True))


def morning_baseline_file(target_date: str) -> Path:
    return REPORT_DIR / f"picks_morning_{target_date}.json"


def official_run_marker_file(target_date: str) -> Path:
    """Completion marker for the heavy official pipeline.

    A dated picks archive is NOT a completion marker: the future planner
    deliberately creates ``picks_YYYY-MM-DD.json`` before that date so the
    odds-capture shortlist can price tomorrow's fixtures.  Using archive
    existence to select intraday mode starved capture_daily on the next day.
    """
    return REPORT_DIR / f"official_run_{target_date}.json"


def mark_official_run_complete(target_date: str, run_as_of: str) -> Path:
    """Atomically record a successful heavy official run, including empty slates."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = official_run_marker_file(target_date)
    payload = {
        "schema": 1,
        "target_date": target_date,
        "completed_at": datetime.now(local_tz()).isoformat(timespec="seconds"),
        "run_as_of": run_as_of,
        "pipeline": "official_heavy",
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(path)
    print(f"  official heavy-run marker: {path}")
    return path


def save_morning_baseline(target_date: str, picks_text: str | None, *, overwrite: bool = False) -> None:
    if picks_text is None:
        return
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = morning_baseline_file(target_date)
    if path.exists() and not overwrite:
        return
    path.write_text(picks_text)


def sync_repo_state() -> None:
    """Pull cloud-committed pipeline state (localdata) before local runs.

    The Actions bot commits localdata/ after every iteration; pulling first
    makes the local cadence start from the exact cloud state (frozen picks,
    sent ledgers, registries), so the archive-first logic restores the same
    morning slate instead of re-picking a divergent one. No-op in CI (GitHub
    Actions checkout is detached) and when .git is absent. Set
    EDGE_FACTORY_GIT_SYNC=0 to disable. Non-fatal by design."""
    try:
        if os.environ.get("EDGE_FACTORY_GIT_SYNC", "1").strip().lower() in {"0", "false", "no", "off"}:
            return
        if os.environ.get("GITHUB_ACTIONS", "").lower() == "true":
            return
        if not (ROOT / ".git").exists():
            return
        run_soft("git pull --rebase --autostash", "git state sync (cloud -> local)")
        run_soft("git fetch --prune", "git fetch --prune")
    except Exception as exc:  # a sync convenience must never kill the pipeline
        print(f">>> git state sync skipped (non-fatal): {exc}")


def sync_official_archive(target_date: str, label: str = "sync_supabase") -> None:
    archive = archived_picks_file(target_date)
    run_soft(
        f"python3 scripts/sync_supabase.py --picks {shlex.quote(str(archive))} --target-date {target_date} --replace-date",
        label,
    )


def capture_theodds_snapshot(target_date: str, trigger: str) -> None:
    """The Odds API price snapshot for the frozen shortlist (audit-only CLV).

    --auto is idempotent and attempt-guarded: first snapshot once per fixture
    per day, close snapshot once per fixture inside the pre-kickoff window;
    0 credits otherwise. Key rotation + monthly budget live in the adapter."""
    run_soft(
        f"PYTHONPATH=src python3 scripts/capture_theodds.py --date {target_date} --auto",
        f"theoddsapi capture {target_date} [{trigger}]",
    )


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
    try:
        data = json.loads(PICKS_TODAY_FILE.read_text())
        if not isinstance(data, list):
            return []
        return [p for p in data if isinstance(p, dict)]
    except Exception:
        return []


def tag_picks(picks: list[dict[str, Any]], target: str) -> list[dict[str, Any]]:
    tagged: list[dict[str, Any]] = []
    for pick in picks:
        p = dict(pick)
        p.setdefault("date", target)
        p.setdefault("picked_for", target)
        tagged.append(p)
    return tagged


def restore_target_picks(target_picks_text: str | None) -> None:
    """Restore picks_today.json to target-date picks before sync_supabase."""
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


def generate_daily_report(
    target_date: str,
    output_path: Path | None = None,
    header_title: str | None = None,
    source_picks: list[dict[str, Any]] | None = None,
    metadata_lines: list[str] | None = None,
) -> Path | None:
    """Write a human-readable .txt summary of picks_today.json or provided picks."""
    report_file = output_path or (REPORT_DIR / f"picks_{target_date}.txt")

    if source_picks is None and not PICKS_TODAY_FILE.exists():
        print("No picks file found — skipping report")
        return None

    try:
        picks = source_picks if source_picks is not None else load_picks_file()
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            header_title or f"Edge Factory Picks — {target_date}",
            "=" * 60,
            f"Generated at: {now_ts}",
        ]
        if metadata_lines:
            for meta_line in metadata_lines:
                lines.append(meta_line)
        lines.append("")

        buckets: dict[str, list[dict[str, Any]]] = {}
        for p in picks:
            b = p.get("bucket", "UNKNOWN")
            buckets.setdefault(str(b), []).append(p)

        bucket_order = list(BUCKET_ORDER)
        # Fail visible rather than producing a shorter operator report than the
        # machine ledger/audit. Unknown buckets are still rendered in order.
        for unknown_bucket in sorted(set(buckets) - set(bucket_order)):
            bucket_order.append(unknown_bucket)

        for b in bucket_order:
            bpicks = buckets.get(b, [])
            lines.append(f"\n{BUCKET_LABELS.get(b, b)}")
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

                # Derive from the exact rule string at render time: archived
                # rows may carry a pre-qualifier display_rule from older code
                # and the merge layer retains rows exactly (stale forever).
                label = honest_display_label(p)
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
                    f"league={ctx.get('league_key', 'UNKNOWN')}:{ctx.get('league', '?')}  "
                    f"odds_band={ctx.get('odds_band_name', '?')}:{ctx.get('odds_band', '?')}"
                )
                statistical_comment = strip_retired_top_scores(p.get("statistical_comment"))
                if statistical_comment:
                    lines.append(f"     {statistical_comment}")
                notes = p.get("event_notes", [])
                if notes:
                    event_text = " | ".join(
                        f"{note['label'].replace(' Goals', '')}: {note['probability']:.1%}"
                        for note in notes
                    )
                    lines.append(f"     🔥 Possible Events: {event_text}")

        rendered_count = sum(len(buckets.get(b, [])) for b in bucket_order)
        if rendered_count != len(picks):
            raise RuntimeError(
                f"daily report dropped picks: ledger={len(picks)} rendered={rendered_count}"
            )
        lines.append("")
        lines.append(f"Total archived picks in this report: {len(picks)}")
        lines.append("⚠️  Flat stakes only. Best odds inflate ROI (~halve it).")
        lines.append("⚠️  Bet only what you can afford to lose.")

        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report_file.write_text("\n".join(lines))
        print(f"Report written: {report_file}")
        return report_file
    except Exception as exc:  # noqa: BLE001 - report generation must never kill pipeline
        print(f"Could not generate report: {exc}")
        return None


def _pick_date(pick: dict[str, Any], fallback: str) -> str:
    for key in ("date", "picked_for", "target_date", "match_date"):
        value = pick.get(key)
        if value:
            return str(value)[:10]
    return fallback


def write_future_outputs(all_picks: list[dict[str, Any]], days: int, snapshot_as_of: str) -> None:
    """Write the aggregate machine-readable future-picks file plus forecast manifest."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_file = REPORT_DIR / f"picks_next_{days}days.json"
    json_file.write_text(json.dumps(all_picks, indent=2, sort_keys=True))
    manifest_file = REPORT_DIR / f"picks_next_{days}days_manifest.json"
    manifest = {
        "ledger_kind": "forecast",
        "snapshot_as_of": snapshot_as_of,
        "days": days,
        "row_count": len(all_picks),
    }
    manifest_file.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"Future planner wrote: {json_file}")
    print(f"Future planner manifest: {manifest_file}")


def run_future_planner(start_date: str, days: int, target_picks: list[dict[str, Any]], run_as_of: str) -> None:
    """Inline N-day planner using scripts/picks_today.py as the only pick engine."""
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
            # De-duplicate future picks against already captured picks to prevent midnight crossing
            merged_picks, new_added, _ = autonomous_intraday_merge(all_picks, day_picks)
            all_picks = merged_picks
            
            # Filter the merged ledger for only this target date to generate a clean, de-duplicated report
            day_specific_picks = [p for p in all_picks if _pick_date(p, "9999-99-99") == target]
            
            generate_daily_report(
                target,
                source_picks=day_specific_picks,
                metadata_lines=[f"Snapshot as of: {run_as_of}", "Ledger kind: forecast"],
            )
            print(f"  {target}: added {new_added} rows")
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
    write_future_outputs(all_picks, days, run_as_of)


def generate_forecast_report(target_date: str, flabel: str, picks: list[dict[str, Any]]) -> Path | None:
    """Generate a dedicated human-readable .txt summary for a forecast refresh."""
    output_path = REPORT_DIR / f"forecast_{target_date}_{flabel}.txt"
    title = f"Edge Factory Forecast Refresh — {target_date} [{flabel}]"
    return generate_daily_report(
        target_date,
        output_path=output_path,
        header_title=title,
        source_picks=picks,
        metadata_lines=[f"Snapshot as of: {datetime.now(local_tz()).isoformat(timespec='seconds')}", "Ledger kind: forecast"],
    )


def promote_forecast(forecast_arg: str, default_date: str) -> None:
    """Deliberately promote a non-official forecast JSON to become the official record."""
    path = Path(forecast_arg)
    if not path.exists():
        candidates = [
            REPORT_DIR / forecast_arg,
            REPORT_DIR / f"forecast_{forecast_arg}.json",
            REPORT_DIR / f"forecast_{default_date}_{forecast_arg}.json",
        ]
        for c in candidates:
            if c.exists():
                path = c
                break
    if not path.exists():
        print(f"❌ Could not find forecast file matching '{forecast_arg}'", file=sys.stderr)
        sys.exit(1)

    print(f"\n>>> Deliberate Promotion of Forecast: {path}")
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        print(f"❌ Forecast file does not contain a JSON list: {path}", file=sys.stderr)
        sys.exit(1)

    target_date = _pick_date(data[0] if data else {}, default_date)

    healed = heal_ledger_labels(data)
    if healed:
        print(f"  self-healed {healed} stale display labels during promotion")

    archive_file = archived_picks_file(target_date)
    text_content = json.dumps(data, indent=2, sort_keys=True)
    archive_file.write_text(text_content)
    PICKS_TODAY_FILE.write_text(text_content)
    print(f"  Promoted to official archive: {archive_file}")
    print(f"  Promoted to live ledger     : {PICKS_TODAY_FILE}")

    generate_daily_report(target_date)

    run_soft("python3 scripts/sync_supabase.py", "sync_supabase (Promoted Official Record)")
    run_soft(f"python3 scripts/notify.py --force --date {target_date}", "notify (Promoted Official Record)")
    print(f"✅ Forecast {path.name} successfully promoted to official record for {target_date}.")


def match_market_key(pick: dict[str, Any]) -> tuple[str, str, str, str]:
    """Deterministic event-market natural key for our autonomous ledger merger.
    
    To prevent 'midnight crossing' (same game appearing on two different dates),
    we ignore the explicit date field and rely on the match identity.
    """
    # The operational ledger key folds accents without changing the legacy
    # normalization used by certified miner joins.
    home = ledger_team_key(pick.get("home") or "")
    away = ledger_team_key(pick.get("away") or "")
    if not home or not away:
        match_str = str(pick.get("match") or "").lower().strip()
        home, away = match_str, match_str
    market = str(pick.get("market") or "1x2").lower()
    
    # We use a constant 'MATCH_DATE' placeholder because for the purpose of 
    # intraday/future merging, the identity of the teams + market is the 
    # primary unique identifier.
    return ("EVENT_ID", home, away, market)


def autonomous_intraday_merge(
    existing_ledger: list[dict[str, Any]],
    fresh_run: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int, int]:
    """The core autonomous accumulating ledger engine.

    Returns (merged_picks, newly_added_count, superseded_count).
    Retains all existing locked picks to protect Day 0 performance records,
    appends any brand new late-slate discoveries, and — when a FRESH pick
    collides with an existing row for the SAME fixture + market + match date —
    PREFERS THE FRESH ROW (the newer run is the current truth; this is what
    was hiding the ml-meta picks behind archived 3way rows for the same
    fixture). Midnight-crossing protection stays: a different match date means
    a different match, so the archived row is kept and the fresh one deduped.

    Existing ledgers are normalized on read. This is important because an old
    archive can already contain duplicate alias rows; merely replacing the
    first matching row would leave the second duplicate in place forever.
    """
    seen_match_keys: set[tuple[str, str, str, str]] = set()
    positions: dict[tuple[tuple[str, str, str, str], str], int] = {}
    merged: list[dict[str, Any]] = []
    superseded = 0

    for pick in existing_ledger:
        if not isinstance(pick, dict):
            continue
        key = match_market_key(pick)
        dated_key = (key, _pick_date(pick, ""))
        if dated_key in positions:
            # Repair a duplicate already frozen in the archive. First-frozen
            # wins until a fresh row for the same event replaces it below.
            superseded += 1
            continue
        positions[dated_key] = len(merged)
        seen_match_keys.add(key)
        merged.append(pick)

    new_added = 0
    for pick in fresh_run:
        if not isinstance(pick, dict):
            continue
        key = match_market_key(pick)
        dated_key = (key, _pick_date(pick, ""))
        existing_position = positions.get(dated_key)
        if existing_position is not None:
            merged[existing_position] = pick
            superseded += 1
            continue
        if key not in seen_match_keys:
            positions[dated_key] = len(merged)
            seen_match_keys.add(key)
            merged.append(pick)
            new_added += 1
        # A key collision on a different date is the midnight-crossing guard:
        # preserve the archived match and do not append a second copy.

    merged.sort(
        key=lambda p: (
            _pick_date(p, "9999-99-99"),
            str(p.get("bucket", "")),
            -float(p.get("w_score") or 0),
            -float(p.get("avg_p") or 0),
            str(p.get("match", "")),
        )
    )
    return merged, new_added, superseded


def get_qualitative_hour_label() -> str:
    """Return a qualitative intraday label for CLV capture based on local hour."""
    hour = datetime.now(local_tz()).hour
    if 10 <= hour < 14:
        return "midday"
    if 14 <= hour < 18:
        return "afternoon"
    if hour >= 18:
        return "evening"
    return "morning"


def run_pipeline(
    target_date: str,
    mode: str,  # "official", "autonomous_intraday", "forecast", "clv_only"
    future_days: int = 2,
    backfill_days: int = 30,
    force_repick: bool = False,
    picks_only: bool = False,
    forecast_label: str | None = None,
    clv_label: str | None = None,
) -> None:
    """Execute the pipeline according to the requested operational mode."""
    sync_repo_state()
    if mode == "clv_only":
        label = clv_label or "monitoring"
        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_clv.py capture --date {target_date} --label {label}",
            f"audit_clv capture {target_date} [{label}]",
        )
        capture_theodds_snapshot(target_date, label)
        clv_start = (datetime.strptime(target_date, "%Y-%m-%d").date() - timedelta(days=30)).isoformat()
        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_clv.py report --start {clv_start} --end {target_date}",
            f"audit_clv report {clv_start}..{target_date}",
        )
        return

    run_as_of = make_run_as_of()
    print(f"=== Edge Factory Pipeline ({mode.upper()}) ===")
    print(f"    target date : {target_date}")
    print(f"    future_days : {future_days}")
    print(f"    run_as_of   : {run_as_of}")
    print(f"    started at  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if mode == "official":
        if not picks_only:
            run("python3 scripts/capture_daily.py --skip-build", "capture_daily (D30 lookback)")
            run(
                f"python3 scripts/backfill_results.py --days {backfill_days}",
                f"backfill_results (D{backfill_days})",
            )
            run("python3 scripts/build_warehouse.py", "build_warehouse")

        run_soft(
            "PYTHONPATH=src python3 scripts/export_settled_results.py",
            "export_settled_results (Addendum 21 overlay)",
        )
        run(get_build_entity_registry_cmd(), "build_entity_registry")
        run("PYTHONPATH=src python3 scripts/mine_consensus.py", "mine_consensus")
        run("PYTHONPATH=src python3 scripts/decay_monitor.py", "decay_monitor")
        run("PYTHONPATH=src python3 scripts/assay_purity.py", "assay_purity")

        target_archive = archived_picks_file(target_date)
        if target_archive.exists() and not force_repick:
            print(f"\n>>> restore frozen target picks {target_date}")
            target_picks_text = target_archive.read_text()
            restore_target_picks(target_picks_text)
            save_morning_baseline(target_date, target_picks_text, overwrite=False)
            print(f"  reused archive: {target_archive}")
        else:
            run(
                f"{picks_env_prefix(run_as_of)} PYTHONPATH=src python3 scripts/picks_today.py {target_date}",
                f"picks_today {target_date}",
            )
            if PICKS_TODAY_FILE.exists():
                current_picks = load_picks_file()
                archive_picks_by_kickoff(current_picks, target_date)
                # STACKING: dispatch the merged archive (prior runs + fresh) instead
                # of the fresh snapshot, so bets found in earlier runs are never
                # dropped from the official record, reports, CLV, or WhatsApp dispatch.
                if target_archive.exists():
                    _raw = target_archive.read_text()
                    try:
                        _stacked = json.loads(_raw)
                    except Exception:
                        _stacked = None
                    if isinstance(_stacked, list) and _stacked:
                        target_picks_text = _raw
                        print(f">>> stacked ledger {target_date}: {len(_stacked)} official picks "
                              f"(prior archive + fresh merged; fresh had {len(current_picks)})")
                        restore_target_picks(target_picks_text)
                    else:
                        # Corrupt/empty archive: never dispatch garbage or a blank
                        # ledger — fall back to the fresh snapshot instead.
                        print(f">>> WARNING archive {target_archive} unreadable/empty; "
                              "dispatching fresh snapshot", file=sys.stderr)
                        target_picks_text = PICKS_TODAY_FILE.read_text()
                else:
                    target_picks_text = PICKS_TODAY_FILE.read_text()
            else:
                # Fresh run produced nothing (scrape/engine failure): never lose the stack.
                target_picks_text = target_archive.read_text() if target_archive.exists() else None
                if target_picks_text:
                    print(f">>> picks_today empty; restored stacked ledger {target_archive}")
                    restore_target_picks(target_picks_text)

            save_morning_baseline(target_date, target_picks_text, overwrite=force_repick)

        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_clv.py capture --date {target_date} --label pick_time",
            f"audit_clv capture {target_date} [pick_time]",
        )
        capture_theodds_snapshot(target_date, "pick_time")
        clv_start = (datetime.strptime(target_date, "%Y-%m-%d").date() - timedelta(days=30)).isoformat()

        target_picks = load_picks_file()

        generate_daily_report(target_date)
        run_future_planner(target_date, future_days, target_picks, run_as_of)

        restore_target_picks(target_picks_text)
        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_clv.py capture --date {target_date} --label end_of_run",
            f"audit_clv capture {target_date} [end_of_run]",
        )
        capture_theodds_snapshot(target_date, "end_of_run")
        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_clv.py report --start {clv_start} --end {target_date}",
            f"audit_clv report {clv_start}..{target_date}",
        )
        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_recent_picks.py --end {target_date} --days 30",
            f"audit_recent_picks {target_date} [30d]",
        )
        run_soft(
            "PYTHONPATH=src python3 scripts/auto_tickets.py",
            "auto_tickets (generate/freeze)",
        )
        run_soft(
            "PYTHONPATH=src python3 scripts/auto_tickets_grade.py",
            "auto_tickets_grade (settle past slips)",
        )
        run_soft(
            "PYTHONPATH=src python3 scripts/o25_tracker.py 2>&1 | tee localdata/o25_tracker_report.txt",
            "o25_tracker (goals surface + checkpoint gate)",
        )
        sync_official_archive(target_date, "sync_supabase")
        _notify(target_date, "notify (Smart Dispatch + empty-slate heartbeat)")
        if not picks_only:
            # This marker, rather than picks_YYYY-MM-DD.json, proves that the
            # heavy capture/build/mine path completed.  Future forecast
            # archives can exist without suppressing tomorrow's official run.
            mark_official_run_complete(target_date, run_as_of)
        else:
            print("  picks-only official run: heavy-run marker intentionally not written")
        print(f"\n=== Pipeline Official Run Complete — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    elif mode == "autonomous_intraday":
        # Completely hands-off accumulating ledger run. Capture_daily remains
        # the heavy D30 all-source path, but final scores can arrive after the
        # morning capture. Refresh yesterday's six existing result donors first,
        # then backfill/build/export before the audit consumes the facts.
        refresh_day = result_refresh_day(target_date)
        run_soft(
            result_refresh_cmd(target_date),
            f"refresh result donors ({refresh_day})",
        )
        run_soft(
            f"python3 scripts/backfill_results.py --days {backfill_days}",
            f"backfill_results (D{backfill_days})",
        )
        run_soft("python3 scripts/build_warehouse.py", "build_warehouse")
        run_soft(
            "PYTHONPATH=src python3 scripts/export_settled_results.py",
            "export_settled_results (Addendum 21 overlay)",
        )
        run(get_build_entity_registry_cmd(), "build_entity_registry")
        run("PYTHONPATH=src python3 scripts/mine_consensus.py", "mine_consensus")
        run("PYTHONPATH=src python3 scripts/decay_monitor.py", "decay_monitor")
        run("PYTHONPATH=src python3 scripts/assay_purity.py", "assay_purity")

        target_archive = archived_picks_file(target_date)
        try:
            existing_ledger = json.loads(target_archive.read_text())
            if not isinstance(existing_ledger, list):
                existing_ledger = []
        except Exception:
            existing_ledger = []

        print(f"\n>>> Autonomous Intraday Discovery Run {target_date}")
        run(
            f"{picks_env_prefix(run_as_of)} PYTHONPATH=src python3 scripts/picks_today.py {target_date}",
            f"picks_today {target_date} (Late Slate Scan)",
        )

        fresh_picks = load_picks_file()
        merged_picks, new_added, superseded = autonomous_intraday_merge(
            existing_ledger, fresh_picks
        )
        healed_labels = heal_ledger_labels(merged_picks)
        if healed_labels:
            print(f"  self-healed {healed_labels} stale display labels in live ledger")
        if superseded:
            print(f"  superseded {superseded} archived row(s) with fresh picks (same fixture+date)")

        print("\n=== Autonomous Accumulating Ledger Verdict ===")
        print(f"  Existing Locked Morning Picks : {len(existing_ledger)}")
        print(f"  Brand New Late-Slate Bets     : {new_added}")
        print(f"  Superseded with fresh         : {superseded}")
        print(f"  Total Active Official Ledger  : {len(merged_picks)}")

        ledger_changed = new_added > 0 or superseded > 0 or healed_labels > 0
        if ledger_changed:
            if new_added > 0:
                print(
                    "\n>>> Updating official frozen archives & production databases "
                    "with new discoveries..."
                )
            else:
                print("\n>>> Rewriting official frozen archive after dedupe/fresh-row repair...")
            merged_text = json.dumps(merged_picks, indent=2, sort_keys=True)
            target_archive.write_text(merged_text)
            PICKS_TODAY_FILE.write_text(merged_text)
            generate_daily_report(target_date)
            notify_label = (
                "notify (Autonomous Intraday Dispatch)"
                if new_added > 0
                else "notify (Silent Repair)"
            )
            _notify(target_date, notify_label)
        else:
            print("\n  No new matches/edges appeared. Locked official ledger unchanged.")
            restore_target_picks(target_archive.read_text())
            _notify(target_date, "notify (Silent Check)")

        sync_official_archive(target_date, "sync_supabase (Autonomous Accumulating Record)")
        try:
            current_target_picks = json.loads(target_archive.read_text())
            if not isinstance(current_target_picks, list):
                current_target_picks = []
        except Exception:
            current_target_picks = []
        run_future_planner(target_date, future_days, current_target_picks, run_as_of)
        restore_target_picks(target_archive.read_text())

        # Qualitative time-of-day CLV capture
        qlabel = get_qualitative_hour_label()
        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_clv.py capture --date {target_date} --label {qlabel}",
            f"audit_clv capture {target_date} [{qlabel}]",
        )
        capture_theodds_snapshot(target_date, qlabel)

        clv_start = (datetime.strptime(target_date, "%Y-%m-%d").date() - timedelta(days=30)).isoformat()
        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_clv.py report --start {clv_start} --end {target_date}",
            f"audit_clv report {clv_start}..{target_date}",
        )
        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_recent_picks.py --end {target_date} --days 30",
            f"audit_recent_picks {target_date} [30d]",
        )
        run_soft(
            "PYTHONPATH=src python3 scripts/auto_tickets.py",
            "auto_tickets (generate/freeze)",
        )
        run_soft(
            "PYTHONPATH=src python3 scripts/auto_tickets_grade.py",
            "auto_tickets_grade (settle past slips)",
        )
        run_soft(
            "PYTHONPATH=src python3 scripts/o25_tracker.py 2>&1 | tee localdata/o25_tracker_report.txt",
            "o25_tracker (goals surface + checkpoint gate)",
        )
        print(f"\n=== Autonomous Intraday Service Complete — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    elif mode == "forecast":
        # Fast non-official forecast refresh (Human research mode)
        run(get_build_entity_registry_cmd(), "build_entity_registry")
        run("PYTHONPATH=src python3 scripts/mine_consensus.py", "mine_consensus")
        run("PYTHONPATH=src python3 scripts/decay_monitor.py", "decay_monitor")
        run("PYTHONPATH=src python3 scripts/assay_purity.py", "assay_purity")

        flabel = forecast_label or datetime.now(local_tz()).strftime("%H%M")
        print(f"\n>>> forecast refresh {target_date} [{flabel}]")
        run(
            f"{picks_env_prefix(run_as_of)} PYTHONPATH=src python3 scripts/picks_today.py {target_date}",
            f"picks_today {target_date} (Forecast Mode)",
        )

        if not PICKS_TODAY_FILE.exists():
            print("❌ No picks_today.json generated during forecast refresh.")
            return

        forecast_picks = load_picks_file()

        json_path = REPORT_DIR / f"forecast_{target_date}_{flabel}.json"
        json_path.write_text(PICKS_TODAY_FILE.read_text())
        print(f"  Forecast JSON saved: {json_path}")

        txt_path = generate_forecast_report(target_date, flabel, forecast_picks)
        if txt_path:
            print(f"  Forecast TXT saved : {txt_path}")

        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_clv.py capture --date {target_date} --label forecast_{flabel} --input {json_path}",
            f"audit_clv capture {target_date} [forecast_{flabel}]",
        )

        qlabel = get_qualitative_hour_label()
        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_clv.py capture --date {target_date} --label {qlabel} --input {json_path}",
            f"audit_clv capture {target_date} [{qlabel}]",
        )

        clv_start = (datetime.strptime(target_date, "%Y-%m-%d").date() - timedelta(days=30)).isoformat()
        run_soft(
            f"PYTHONPATH=src python3 scripts/audit_clv.py report --start {clv_start} --end {target_date}",
            f"audit_clv report {clv_start}..{target_date}",
        )

        target_archive = archived_picks_file(target_date)
        if target_archive.exists():
            print(f"\n>>> Restoring live picks_today.json from official archive {target_archive}")
            restore_target_picks(target_archive.read_text())
        else:
            print("\n⚠️ No official archive exists for today yet. Live picks_today.json currently holds forecast refresh.")

        print(f"\n=== Pipeline Forecast Refresh Complete — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")


def run_smart_auto(future_days: int, backfill_days: int, force_repick: bool = False, picks_only: bool = False) -> None:
    """Determine operational state for the target date and execute autonomous accumulating run."""
    now = datetime.now(local_tz())
    target_date = now.strftime("%Y-%m-%d")

    target_archive = archived_picks_file(target_date)
    official_marker = official_run_marker_file(target_date)

    print(f"\n=== Smart Autonomous Schedule Execution — {now.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"    target date: {target_date}")
    print(f"    local time : {now.strftime('%H:%M:%S %Z')}")

    # Forecast archives are created one day early on purpose for odds capture.
    # They must never masquerade as proof that today's heavy official pipeline
    # ran.  Only the dedicated completion marker selects intraday mode.
    official_complete = official_marker.exists() and not force_repick
    print(f"    archive    : {'EXISTS (forecast/official rows available)' if target_archive.exists() else 'MISSING'}")
    print(f"    official   : {'COMPLETE (intraday mode)' if official_complete else 'MISSING/FORCED (heavy mode)'}")

    if not official_complete:
        print(f"\n>>> [Smart Auto] Case 1: No official heavy-run marker for {target_date}. Executing Official Full Run.")
        run_pipeline(
            target_date=target_date,
            mode="official",
            future_days=future_days,
            backfill_days=backfill_days,
            # A pre-existing archive may be yesterday's forecast shortlist.
            # Regenerate current-day truth during the official run.
            force_repick=True,
            picks_only=picks_only,
        )
    else:
        print(f"\n>>> [Smart Auto] Case 2: Official heavy run completed for {target_date}. Executing Intraday Accumulating Discovery & CLV Capture.")
        run_pipeline(
            target_date=target_date,
            mode="autonomous_intraday",
            future_days=future_days,
            backfill_days=backfill_days,
            force_repick=True, # Force repick inside the intraday logic to get fresh discoveries
            picks_only=True,   # Skip heavy warehouse build for speed during the day
        )

    # Truthfulness tripwire: certified-edge firing + source capture freshness.
    # WARN-only — silence can be legitimate — but silence is now visible and
    # persisted to localdata/edge_firing_tripwire.json instead of invisible.
    run_soft(
        "PYTHONPATH=src python3 scripts/edge_firing_tripwire.py",
        "edge firing tripwire (silence detector)",
    )


def _notify(target_date: str, label: str) -> None:
    """Run the notifier and surface delivery failures loudly.

    notify.py already exits non-zero on any failed channel; run_soft keeps the
    pipeline alive (a notify failure must not block state commits), but a
    failure ledger written today gets a prominent banner here so a green run
    can never silently mean 'message did not arrive'."""
    run_soft(f"python3 scripts/notify.py --date {target_date}", label)
    day = datetime.now(local_tz()).strftime("%Y-%m-%d")
    ledger = REPORT_DIR / f"notify_delivery_failures_{day}.json"
    if ledger.exists():
        try:
            n = len(json.loads(ledger.read_text()))
        except Exception:
            n = "?"
        print(f"❌ NOTIFICATION DELIVERY FAILURE: {n} failed channel(s) — see {ledger.name}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Edge Factory single orchestrator for autonomous daily maintenance, smart accumulating ledgers, and human research forecasts.",
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
        help="Target date for picks_today (YYYY-MM-DD). Defaults to today in local TZ.",
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
        help="Ignore archived picks_YYYY-MM-DD.json and regenerate official target-date picks.",
    )
    ap.add_argument(
        "--auto-run",
        action="store_true",
        help="Start the autonomous 3-hour accumulating background service.",
    )
    ap.add_argument(
        "--auto-once",
        action="store_true",
        help="Perform exactly one autonomous iteration of the smart accumulating schedule and exit.",
    )
    ap.add_argument(
        "--forecast-refresh",
        action="store_true",
        help="Execute a non-official forecast refresh (human research mode) to discover new fixtures/odds.",
    )
    ap.add_argument(
        "--forecast-label",
        default=None,
        help="Specific label or HHMM timestamp for forecast refresh (default: current HHMM).",
    )
    ap.add_argument(
        "--promote-forecast",
        default=None,
        help="Path or label of a forecast JSON file to promote to official tracked performance record.",
    )
    ap.add_argument(
        "--clv-only",
        action="store_true",
        help="Run only CLV monitoring capture and rolling report for the target date.",
    )
    ap.add_argument(
        "--clv-label",
        default=None,
        help="Snapshot label to use when --clv-only is passed.",
    )
    args = ap.parse_args()

    target_date = args.date or datetime.now(local_tz()).strftime("%Y-%m-%d")

    if args.promote_forecast:
        promote_forecast(args.promote_forecast, target_date)
        return

    if args.auto_run:
        print(f"=== Starting Edge Factory Autonomous 3-Hour Service ({DEFAULT_LOCAL_TZ}) ===")
        while True:
            try:
                run_smart_auto(args.future_days, args.backfill_days)
            except (Exception, SystemExit) as exc:
                print(
                    f"\n⚠️ [Auto-Run] Network/Scraping exception during automated execution: {exc}.\n"
                    "   (If your laptop is offline or asleep, live capture will naturally pause). Retrying on next scheduled window...",
                    file=sys.stderr,
                )

            next_run = datetime.now(local_tz()) + timedelta(hours=3)
            print(f"\n💤 Autonomous service resting. Next execution scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S %Z')} (in 3 hours)...")
            time.sleep(3 * 3600)

    if args.auto_once:
        run_smart_auto(args.future_days, args.backfill_days)
        return

    if args.clv_only:
        run_pipeline(
            target_date=target_date,
            mode="clv_only",
            clv_label=args.clv_label,
        )
        return

    if args.forecast_refresh:
        run_pipeline(
            target_date=target_date,
            mode="forecast",
            future_days=args.future_days,
            backfill_days=args.backfill_days,
            force_repick=True,
            picks_only=True,
            forecast_label=args.forecast_label,
        )
        return

    # Default: Smart Autonomous Run
    # This handles both the initial morning run and subsequent intraday discovery/merges automatically.
    run_smart_auto(
        future_days=args.future_days,
        backfill_days=args.backfill_days,
        force_repick=args.force_repick,
        picks_only=args.picks_only,
    )


if __name__ == "__main__":
    main()

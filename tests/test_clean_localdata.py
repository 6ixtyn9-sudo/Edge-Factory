from __future__ import annotations

from datetime import date

from scripts.clean_localdata import clean_localdata, files_to_prune


def test_cleanup_prunes_only_old_known_daily_outputs(tmp_path):
    old = date(2026, 8, 1)
    today = date(2026, 9, 25)
    names = [
        "clv_report_2026-08-01.md",
        "picks_morning_2026-08-01.json",
        "picks_audit_2026-08-01.md",
        "picks_2026-08-01.txt",
        "clv_unmatched_2026-08-01.json",
        "supabase_sync_manifest_2026-08-01.json",
        "theoddsapi_attempts_2026-08-01.json",
        "auto_tickets_2026-08-01.txt",
        "sent_ledger_2026-08-01.json",
        "shadow_sent_ledger_2026-08-01.json",
        "official_run_2026-08-01.json",
        "notify_delivery_failures_2026-08-01.json",
    ]
    for name in names:
        (tmp_path / name).write_text("old")

    # These are either within the retention window or deliberately not a
    # dated daily family.  Cleanup must not treat localdata as a blunt cache.
    for name in (
        "picks_2026-08-01.json",
        "picks_2026-09-01.json",
        "picks_today.json",
        "picks_audit_rolling.json",
        "auto_tickets_state.json",
        "forebet_2026-01.csv.gz",
        "model_2026-08-01.bin",
    ):
        (tmp_path / name).write_text("keep")

    stale = files_to_prune(tmp_path, keep_days=30, today=today)
    assert {p.name for p in stale} == set(names)
    removed = clean_localdata(tmp_path, keep_days=30, today=today)
    assert {p.name for p in removed} == set(names)
    assert (tmp_path / "picks_today.json").exists()
    assert (tmp_path / "forebet_2026-01.csv.gz").exists()
    assert (tmp_path / "model_2026-08-01.bin").exists()


def test_cleanup_keeps_the_entire_configured_window(tmp_path):
    for day in ("2026-08-27", "2026-08-28", "2026-08-29"):
        (tmp_path / f"picks_{day}.json").write_text("keep")
    (tmp_path / "picks_2026-08-26.json").write_text("old")

    clean_localdata(tmp_path, keep_days=3, today=date(2026, 8, 29))
    assert (tmp_path / "picks_2026-08-27.json").exists()
    assert (tmp_path / "picks_2026-08-28.json").exists()
    assert (tmp_path / "picks_2026-08-29.json").exists()
    # Pick archives are durable audit inputs and are intentionally retained;
    # cleanup only bounds the secondary per-day telemetry families.
    assert (tmp_path / "picks_2026-08-26.json").exists()

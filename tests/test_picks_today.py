"""Regression tests for the append-only per-day pick ledger (Addendum 27.18).

2026-08-05 failure mode: the evening three-hourly service re-ran the engine
for day 2026-08-05 after every fixture had kicked off; the fresh slate was
empty and the unconditional "freshest run wins" overwrite replaced a frozen
6-row ledger with []. The next audit lost 4 of 6 slate rows. merge_day_archive_rows
makes the per-day archive append-only: earlier frozen rows are never dropped,
and frozen pick-time payloads win identity conflicts.
"""

from scripts.picks_today import merge_day_archive_rows

DAY = "2026-08-05"


def _row(home, away, *, day=DAY, odds=1.50, bucket="SKIPPED_VETO", as_of=None, pick="home"):
    row = {
        "date": day,
        "home": home,
        "away": away,
        "market": "1x2",
        "pick": pick,
        "odds": odds,
        "bucket": bucket,
    }
    if as_of is not None:
        row["as_of"] = as_of
    return row


def test_empty_fresh_run_preserves_frozen_ledger():
    """The 2026-08-05 regression: post-kickoff rerun, fresh == []."""
    frozen = [
        _row("Spartak Moscow", "FC Orenburg", bucket="CAUTION", as_of="2026-08-05T07:35:06+02:00"),
        _row("Lazio", "Ostia Mare", as_of="2026-08-05T08:23:34+02:00"),
        _row("Panathinaikos", "CSKA 1948", as_of="2026-08-05T00:03:23+02:00"),
        _row("Napoli", "Osasuna", as_of="2026-08-05T15:30:00+02:00"),
    ]
    merged = merge_day_archive_rows(frozen, [], DAY)
    assert merged == frozen


def test_partial_fresh_run_keeps_kicked_off_rows():
    """A late scan that only re-derives still-upcoming fixtures must not drop
    the rows whose matches already kicked off."""
    frozen = [
        _row("Early Kickoff FC", "Dropped FC", as_of="2026-08-05T12:00:00+02:00"),
        _row("Late Kickoff FC", "Still Playing FC", as_of="2026-08-05T12:00:00+02:00"),
    ]
    fresh = [_row("Late Kickoff FC", "Still Playing FC", odds=1.61)]
    merged = merge_day_archive_rows(frozen, fresh, DAY)
    assert len(merged) == 2
    by_home = {r["home"]: r for r in merged}
    assert "Early Kickoff FC" in by_home
    # Frozen pick-time payload wins the conflict — never the refreshed rerun.
    assert by_home["Late Kickoff FC"]["odds"] == 1.50
    assert "as_of" in by_home["Late Kickoff FC"]


def test_late_slate_discovery_is_appended():
    frozen = [_row("Morning FC", "Baseline FC")]
    fresh = [
        _row("Morning FC", "Baseline FC"),
        _row("Discovery FC", "Late Addition FC"),
    ]
    merged = merge_day_archive_rows(frozen, fresh, DAY)
    assert [r["home"] for r in merged] == ["Morning FC", "Discovery FC"]


def test_identity_uses_audit_key_shape():
    """Identity mirrors audit _archive_pick_key: (date, home, away, market, pick).
    A same-match row with a different pick is a different ledger row."""
    frozen = [_row("Team A", "Team B", pick="home")]
    fresh = [_row("Team A", "Team B", pick="away", odds=2.40)]
    merged = merge_day_archive_rows(frozen, fresh, DAY)
    assert len(merged) == 2


def test_rows_dated_to_other_days_are_not_preserved():
    """Misfiled/foreign-day rows are dropped (the audit loader filters them
    the same way); same-day rows survive even without an as_of stamp."""
    frozen = [
        _row("Wrong Day FC", "Misfiled FC", day="2026-08-04"),
        _row("Legacy FC", "No Timestamp FC"),  # no as_of — must survive
        "junk-not-a-dict",
    ]
    merged = merge_day_archive_rows(frozen, [], DAY)
    assert [r["home"] for r in merged] == ["Legacy FC"]


def test_empty_existing_writes_fresh():
    fresh = [_row("Only Fresh FC", "No Prior FC")]
    assert merge_day_archive_rows([], fresh, DAY) == fresh

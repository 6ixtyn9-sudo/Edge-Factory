"""Regression tests for the operational pick + ticket surface.

Contracts pinned here, all live-pipeline-critical:

  1. merge_day_archive_rows append-only behaviour (HANDOVER
     addendum 27.18; 2026-08-05 silent-coverage-loss fix).
  2. collapse_final_operational_picks (the operational duplicate
     collapse; 2026-06-18 "AC Oulu vs IFK Mariehamn" leak).

The former Contract 2 (v4 grader stakes_frac display) and Contract 4
(load_pause_state) were removed with the v4 combo-gate slipper itself on
2026-08-27: auto_tickets.py is now the stateful rolling engine and
auto_tickets_grade.py reports from its state. Rolling-engine contracts
live in tests/test_auto_tickets_rolling.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from picks_today import (  # noqa: E402
    BUCKET_CERTIFIED,
    BUCKET_CAUTION,
    BUCKET_SKIP_VETO,
    collapse_final_operational_picks,
    fetch_historical_profile,
    merge_day_archive_rows,
    operational_team_key,
    OPERATIONAL_CLUB_TOKENS,
)

BUCKET_CLEAN = BUCKET_CERTIFIED  # local alias matches the test vocabulary
BUCKET_VETO = BUCKET_SKIP_VETO


def test_historical_profile_no_longer_queries_or_emits_top_scores():
    class Result:
        def __init__(self, row):
            self.row = row

        def fetchone(self):
            return self.row

    class FakeConnection:
        def __init__(self):
            self.queries = []

        def execute(self, query, _params=None):
            self.queries.append(query)
            if "MAX(avg_p)" in query:
                return Result((80.0,))
            return Result((100, 3.1, 0.65, 0.52, 0.72, 0.24))

    con = FakeConnection()
    comment = fetch_historical_profile(con, "home", 70.0, 3)

    assert "Avg Goals: 3.10" in comment
    assert "Top Scores" not in comment
    assert len(con.queries) == 2  # scale probe + active aggregate; no score query
    assert not any("GROUP BY 1" in query for query in con.queries)


# ============================================================
# Contract 1: append-only per-day pick ledger (Addendum 27.18)
# ============================================================

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


def test_archive_merge_collapses_accent_and_ascii_team_aliases():
    """Regression: the 2026-08-13 ledger stored Nordsjælland twice.

    One capture used the accented display spelling and an earlier capture used
    its ASCII form. Operational identity must be accent-safe without changing
    the legacy miner normalization.
    """
    frozen = [_row("FC Nordsjaelland", "Valur Reykjavik", odds=1.12)]
    fresh = [_row("FC Nordsjælland", "Valur Reykjavik", odds=1.14)]
    merged = merge_day_archive_rows(frozen, fresh, DAY)
    assert len(merged) == 1
    assert merged[0]["odds"] == 1.12  # first frozen payload remains authoritative


# ============================================================
# Contract 3: operational duplicate-collapse
# (Handover addenda 16, 18; 2026-06-18 "AC Oulu vs IFK Mariehamn" leak)
# ============================================================

DAY_COLLAPSE = "2026-06-18"
KO_COLLAPSE = "2026-06-18T18:00:00+02:00"


def _collapse_pick(home, away, *, bucket=BUCKET_CLEAN, market="1x2", pick="home",
                   w_score=0.95, avg_p=0.78, odds=1.50, kickoff=KO_COLLAPSE):
    return {
        "date": DAY_COLLAPSE,
        "home": home,
        "away": away,
        "market": market,
        "pick": pick,
        "bucket": bucket,
        "kickoff": kickoff,
        "odds": odds,
        "w_score": w_score,
        "avg_p": avg_p,
        "display_rule": "3way-unanimous-65",
        "match": f"{home} vs {away}",
    }


def test_ac_oulu_ifk_mariehamn_collapses_with_alias_form():
    """2026-06-18 operator-reported leak: 'AC Oulu vs IFK Mariehamn' was
    surfacing as a separate row from 'AC Oulu vs Mariehamn'. The collapse
    must merge them into a single operational row, and the representative
    must carry the worst bucket from either source."""
    picks = [
        _collapse_pick("AC Oulu", "IFK Mariehamn", bucket=BUCKET_CLEAN, odds=1.42),
        _collapse_pick("AC Oulu", "Mariehamn", bucket=BUCKET_CAUTION, odds=1.51),
    ]
    out, removed = collapse_final_operational_picks(picks)
    assert removed == 1
    assert len(out) == 1
    ctx = out[0].get("ctx") or {}
    assert ctx.get("duplicate_alias_collapse") == "true"
    assert out[0].get("duplicate_rows_collapsed") == 1
    # Worst bucket wins (CAUTION > CLEAN in severity).
    assert out[0]["bucket"] == BUCKET_CAUTION


def test_khovd_fc_and_khovd_western_remain_distinct():
    """Identity-bearing compound names must NOT collapse. The bigram Jaccard
    floor is what keeps them apart."""
    picks = [
        _collapse_pick("Khovd FC", "Ulaanbaatar FC", bucket=BUCKET_CLEAN, odds=1.60),
        _collapse_pick("Khovd Western", "Ulaanbaatar FC", bucket=BUCKET_CLEAN, odds=1.55),
    ]
    out, removed = collapse_final_operational_picks(picks)
    assert removed == 0
    assert len(out) == 2


def test_operational_team_key_strips_club_tokens_but_keeps_identity_suffixes():
    """The display-key helper strips AC/FC/IFK (and other
    OPERATIONAL_CLUB_TOKENS) but keeps the bare team name and identity-
    bearing suffixes."""
    for must_be_stripped in ("fc", "ac", "ifk", "afc", "cf", "sc"):
        assert must_be_stripped in OPERATIONAL_CLUB_TOKENS, (
            f"OPERATIONAL_CLUB_TOKENS lost {must_be_stripped!r}; "
            "verify the duplicate-collapse contract before ship."
        )
    for must_be_preserved in ("western", "u19", "b", "ii", "w", "east"):
        assert must_be_preserved not in OPERATIONAL_CLUB_TOKENS
    assert operational_team_key("AC Oulu") == "oulu"
    assert operational_team_key("Khovd FC") == "khovd"
    assert operational_team_key("IFK Mariehamn") == "mariehamn"
    assert operational_team_key("Khovd Western") == "khovdwestern"


def test_worst_bucket_wins_across_three_way_and_two_way_rules():
    """The collapse must merge a 3way pick and a 2way pick for the same
    real-world event (handover: 'same real-world event / same market /
    same pick collapses across 2-way and 3-way rules'). The worst bucket
    of the cluster wins."""
    picks = [
        _collapse_pick("Spartak Moscow", "FC Orenburg", bucket=BUCKET_CLEAN,
                       market="1x2", pick="home", odds=1.32, w_score=0.90),
        _collapse_pick("Spartak Moscow", "Orenburg", bucket=BUCKET_VETO,
                       market="1x2", pick="home", odds=1.30, w_score=0.88),
    ]
    out, removed = collapse_final_operational_picks(picks)
    assert removed == 1
    assert len(out) == 1
    assert out[0]["bucket"] == BUCKET_VETO


def test_kickoffs_outside_180_min_do_not_cluster():
    """``_same_event_cluster`` allows a 180-minute kickoff window. A 4-hour
    separation must NOT collapse even if the team names match perfectly:
    the rescheduling guard."""
    picks = [
        _collapse_pick("Resched FC", "Rival FC", bucket=BUCKET_CLEAN, odds=1.40,
                       kickoff="2026-06-18T14:00:00+02:00"),
        _collapse_pick("Resched FC", "Rival FC", bucket=BUCKET_CLEAN, odds=1.40,
                       kickoff="2026-06-18T18:00:00+02:00"),
    ]
    out, removed = collapse_final_operational_picks(picks)
    assert removed == 0
    assert len(out) == 2


def test_different_pick_side_does_not_collapse():
    """Two picks on the same fixture, same market, but DIFFERENT selection
    are not duplicates — they are opposite bets."""
    picks = [
        _collapse_pick("Same FC", "Same Team", bucket=BUCKET_CLEAN,
                       market="1x2", pick="home", odds=1.40),
        _collapse_pick("Same FC", "Same Team", bucket=BUCKET_CLEAN,
                       market="1x2", pick="away", odds=3.20),
    ]
    out, removed = collapse_final_operational_picks(picks)
    assert removed == 0
    assert len(out) == 2



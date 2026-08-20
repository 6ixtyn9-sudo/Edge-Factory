"""Regression tests for the operational pick + ticket surface.

Three contracts are pinned here, all live-pipeline-critical and
previously exercised only by the production code:

  1. merge_day_archive_rows append-only behaviour (HANDOVER
     addendum 27.18; 2026-08-05 silent-coverage-loss fix).
  2. auto_tickets_grade.display branches the stake/returned
     format on whether the slip carried a `stakes_frac` field.
     Legacy slips (pre-b1c1946 generator, no `stakes_frac`) used
     unit stakes; rendering them as percent-of-capital would say
     "staked 100% of capital" for any single ticket, which is
     wrong. R-prefix format is the honest rendering.
  3. collapse_final_operational_picks (the operational duplicate
     collapse; 2026-06-18 "AC Oulu vs IFK Mariehamn" leak).

The grader contract test does not exercise the full main()
function; it reaches into load_tickets() and exercises the
display-format decision that main() applies. That decision is
the regression we are guarding against.
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
# Contract 2: auto_tickets_grade format branch on stakes_frac
# (Regression: commit 526116e introduced a display bug for
#  legacy slips without stakes_frac; this test pins the fix.)
# ============================================================


def test_grader_marks_legacy_slip_stake_as_none(tmp_path, monkeypatch):
    """A legacy acca slip (no `stakes_frac`) is marked as legacy and its
    per-ticket stake is recorded as None. The operator's plan is
    adaptive (38% is a ceiling, not a target); the actual rand amount
    for a legacy slip is not recoverable from the slip alone because
    the adaptive pool_factor was not recorded. The grader does not
    invent a percent. The per-day display falls back to 'stake not
    recorded' with a transparent note.
    """
    import auto_tickets_grade

    legacy = {
        "date": "2026-08-09",
        "at_risk_frac": 0.38,
        "pass_combos": ["3way-unanimous-65 | bzzoiro_odds"],
        "acca2": [[[{"home": "A", "away": "B", "pick": "home", "odds": 1.5},
                    {"home": "C", "away": "D", "pick": "home", "odds": 1.6}], 2.4]],
        "acca10": [{"home": "E", "away": "F", "pick": "home", "odds": 1.7}],
        "acca10_odds": 1.7,
        # NOTE: no "stakes_frac" key — the legacy shape.
    }
    slip = tmp_path / "auto_tickets_2026-08-09.json"
    slip.write_text(json.dumps(legacy))

    monkeypatch.setattr(auto_tickets_grade, "LOCALDATA", tmp_path)
    monkeypatch.setattr(auto_tickets_grade, "load_settled", lambda: {})

    tickets, legacy_dates = auto_tickets_grade.load_tickets()
    # Legacy slip is in the legacy_dates set.
    assert "2026-08-09" in legacy_dates
    # Per-ticket stake is None, NOT a reconstructed value.
    for t in tickets:
        assert t["stake"] is None, (
            f"legacy slip must have stake=None, got {t['stake']!r}"
        )



def test_grader_uses_stakes_frac_when_present(tmp_path, monkeypatch):
    """A slip with `stakes_frac` (current generator) uses the recorded per-ticket
    percentages, NOT the at_risk_frac scaling. Display is % of capital."""
    import auto_tickets_grade

    new_slip = {
        "date": "2026-08-10",
        "at_risk_frac": 0.38,
        "pass_combos": ["3way-unanimous-65 | bzzoiro_odds"],
        "acca2": [[[{"home": "A", "away": "B", "pick": "home", "odds": 1.5},
                    {"home": "C", "away": "D", "pick": "home", "odds": 1.6}], 2.4]],
        "acca10": [],
        "acca10_odds": 0.0,
        "stakes_frac": {
            "acca2_per_ticket": 0.0933,
            "acca10": 0.10,
            "deployed": 0.1933,
            "ceiling": 0.38,
            "pool_factor": 0.51,
        },
    }
    slip = tmp_path / "auto_tickets_2026-08-10.json"
    slip.write_text(json.dumps(new_slip))

    monkeypatch.setattr(auto_tickets_grade, "LOCALDATA", tmp_path)
    monkeypatch.setattr(auto_tickets_grade, "load_settled", lambda: {})

    tickets, legacy_dates = auto_tickets_grade.load_tickets()
    assert "2026-08-10" not in legacy_dates
    # Stake is read from stakes_frac.acca2_per_ticket, NOT scaled.
    assert abs(tickets[0]["stake"] - 0.0933) < 1e-6


def test_grader_flags_v1v3_singles(tmp_path, monkeypatch):
    """A slip with a `singles` array (v1-v3 era) is flagged so the per-day
    display says 'stake not recorded'. The current operator plan has no
    singles; the unit 1.0 stake from v1-v3 is not rendered as a percent."""
    import auto_tickets_grade

    v1v3_slip = {
        "date": "2026-07-15",
        "singles": [{"home": "A", "away": "B", "pick": "home", "odds": 1.5}],
        "acca2": [],
        "acca10": [],
    }
    (tmp_path / "auto_tickets_2026-07-15.json").write_text(json.dumps(v1v3_slip))
    monkeypatch.setattr(auto_tickets_grade, "LOCALDATA", tmp_path)
    monkeypatch.setattr(auto_tickets_grade, "load_settled", lambda: {})

    tickets, legacy_dates = auto_tickets_grade.load_tickets()
    assert "2026-07-15" in legacy_dates
    # v1-v3 single stake is None, NOT rendered as a percent.
    assert tickets[0]["stake"] is None
    assert tickets[0]["type"] == "single"


def test_grader_main_renders_legacy_as_stake_not_recorded(tmp_path, monkeypatch, capsys):
    """End-to-end: a legacy acca slip on disk renders 'stake not
    recorded' in the per-day section. The 526116e bug rendered this
    as 'staked 100.00% of capital' (wrong); the operator's plan is
    adaptive (38% is a ceiling, not a target) and the actual rand
    amount is not recoverable from the slip alone. No currency
    rendering anywhere; no invented percent."""
    import auto_tickets_grade

    legacy = {
        "date": "2026-08-09",
        "at_risk_frac": 0.38,
        "pass_combos": [],
        "acca2": [[[{"home": "A", "away": "B", "pick": "home", "odds": 1.96}],
                   1.96]],
        "acca10": [{"home": "C", "away": "D", "pick": "home", "odds": 1.96}],
        "acca10_odds": 1.96,
    }
    (tmp_path / "auto_tickets_2026-08-09.json").write_text(json.dumps(legacy))
    monkeypatch.setattr(auto_tickets_grade, "LOCALDATA", tmp_path)
    monkeypatch.setattr(auto_tickets_grade, "load_settled", lambda: {})

    # Run main with no argv to avoid pytest passing this script's args.
    import sys
    saved = sys.argv
    sys.argv = ["auto_tickets_grade"]
    try:
        rc = auto_tickets_grade.main()
    finally:
        sys.argv = saved
    assert rc == 0
    out = capsys.readouterr().out
    # Per-day display says "stake not recorded" with a transparent note.
    assert "stake not recorded" in out, f"legacy slip should say 'stake not recorded': got\n{out}"
    assert "pre-adaptive slip" in out, f"legacy slip should carry the pre-adaptive note: got\n{out}"
    # The 526116e bug: "100.00% of capital" must NOT appear for a legacy
    # slip whose per-ticket stake is unknown.
    assert "100.00% of capital" not in out, f"526116e bug: must not render 100%: got\n{out}"
    # No currency rendering: "staked R" and "returned R" must not appear.
    assert "staked R" not in out, f"must not render as rand: got\n{out}"
    assert "returned R" not in out, f"must not render as rand: got\n{out}"
    # The pre-adaptive 19.33% reconstructed value must NOT appear.
    assert "19.33% of capital" not in out, f"must not invent a percent: got\n{out}"


def test_grader_main_renders_new_slip_in_percent_format(tmp_path, monkeypatch, capsys):
    """End-to-end: a new slip (with stakes_frac) renders as percent of capital.
    The deployed amount is the recorded stakes_frac total."""
    import auto_tickets_grade

    new_slip = {
        "date": "2026-08-10",
        "at_risk_frac": 0.38,
        "pass_combos": [],
        "acca2": [[[{"home": "A", "away": "B", "pick": "home", "odds": 1.96}],
                   1.96]],
        "acca10": [],
        "acca10_odds": 0.0,
        "stakes_frac": {
            "acca2_per_ticket": 0.0933,
            "acca10": 0.10,
            "deployed": 0.0933,
            "ceiling": 0.38,
            "pool_factor": 0.25,
        },
    }
    (tmp_path / "auto_tickets_2026-08-10.json").write_text(json.dumps(new_slip))
    monkeypatch.setattr(auto_tickets_grade, "LOCALDATA", tmp_path)
    monkeypatch.setattr(auto_tickets_grade, "load_settled", lambda: {})

    import sys
    saved = sys.argv
    sys.argv = ["auto_tickets_grade"]
    try:
        rc = auto_tickets_grade.main()
    finally:
        sys.argv = saved
    assert rc == 0
    out = capsys.readouterr().out
    assert "9.33% of capital" in out, f"new slip should render at 9.33% of capital: got\n{out}"


def test_grader_main_renders_v1v3_singles_as_stake_not_recorded(tmp_path, monkeypatch, capsys):
    """End-to-end: a v1-v3 single slip renders 'stake not recorded' in
    the per-day section. The current operator plan has no singles; the
    v1-v3 unit 1.0 stake is not rendered as a percent of capital
    (would be meaningless). Same display path as pre-adaptive acca
    slips: transparent note about why the stake is not recorded."""
    import auto_tickets_grade

    v1v3_slip = {
        "date": "2026-07-15",
        "singles": [{"home": "A", "away": "B", "pick": "home", "odds": 1.5}],
        "acca2": [],
        "acca10": [],
    }
    (tmp_path / "auto_tickets_2026-07-15.json").write_text(json.dumps(v1v3_slip))
    monkeypatch.setattr(auto_tickets_grade, "LOCALDATA", tmp_path)
    monkeypatch.setattr(auto_tickets_grade, "load_settled", lambda: {})

    import sys
    saved = sys.argv
    sys.argv = ["auto_tickets_grade"]
    try:
        rc = auto_tickets_grade.main()
    finally:
        sys.argv = saved
    assert rc == 0
    out = capsys.readouterr().out
    assert "stake not recorded" in out, f"v1-v3 slip should say 'stake not recorded': got\n{out}"
    # No currency rendering, no invented percent.
    assert "staked R" not in out
    assert "100.00% of capital" not in out


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


# ============================================================
# Contract 4: load_pause_state does not inflate staked on legacy
# tickets (auto_tickets.py::load_pause_state)
# (Regression: pre-fix default of 1.0 made legacy stake=None
#  tickets count as 100% of capital each, tripping the pause gate
#  on otherwise-healthy ROI. Verified: the gotcha was real but
#  low-likelihood because legacy slips are rare. The fix: 0.0
#  default, matching the "stake not recorded" contract.)
# ============================================================


def test_load_pause_state_treats_legacy_stake_none_as_zero(tmp_path, monkeypatch):
    """Legacy slip tickets (stake=None) must not inflate the
    pause-state staked total. Pre-fix default of 1.0 would
    treat each None as 100% of capital per ticket, dominating
    the ROI calculation. Post-fix: 0.0 default; legacy
    tickets contribute nothing to the rolling-20 ROI."""
    import auto_tickets

    # 20 settled tickets: 18 new (real stake) + 2 legacy (stake=None).
    # Without the fix, staked = 18*0.0933 + 2*1.0 = 3.68.
    # With the fix,    staked = 18*0.0933 + 2*0.0 = 1.68.
    detail = []
    for i in range(18):
        detail.append({
            "date": "2026-07-01", "type": "acca2", "result": "WIN",
            "odds": 1.96, "stake": 0.0933, "returned": 0.1829,
            "legs": ["A vs B home @1.96"],
        })
    for i in range(2):
        detail.append({
            "date": "2026-08-09", "type": "acca2", "result": "WIN",
            "odds": 1.96, "stake": None, "returned": 0.0,
            "legs": ["X vs Y home @1.96"],
        })
    perf_file = tmp_path / "auto_tickets_performance.json"
    perf_file.write_text(json.dumps({"detail": detail}))

    monkeypatch.setattr(auto_tickets, "LOCALDATA", tmp_path)
    paused = auto_tickets.load_pause_state()
    # With 18 real-stake WINs and 2 legacy WINs:
    # - pre-fix: staked=3.68, returned=3.29, ROI=-10.6% -> PAUSE=True
    # - post-fix: staked=1.68, returned=3.29, ROI=+95.8% -> PAUSE=False
    assert paused is False, \
        "legacy stake=None should not pause the pipeline (got paused=True)"


def test_load_pause_state_handles_short_history(tmp_path, monkeypatch):
    """With fewer than PAUSE_N=20 settled tickets, the function
    returns False (no pause). Pre-fix had the same behaviour;
    this test pins it so the legacy-stake fix doesn't break the
    short-history case."""
    import auto_tickets

    detail = [
        {"date": "2026-08-01", "type": "acca2", "result": "WIN",
         "odds": 1.96, "stake": 0.0933, "returned": 0.1829,
         "legs": ["A vs B"]},
    ]  # only 1 settled, PAUSE_N=20
    perf_file = tmp_path / "auto_tickets_performance.json"
    perf_file.write_text(json.dumps({"detail": detail}))

    monkeypatch.setattr(auto_tickets, "LOCALDATA", tmp_path)
    paused = auto_tickets.load_pause_state()
    assert paused is False


def test_load_pause_state_treats_missing_file_as_no_pause(tmp_path, monkeypatch):
    """If auto_tickets_performance.json is missing, the function
    returns False (fail-soft). The pipeline must not be paused
    by a missing performance file."""
    import auto_tickets
    monkeypatch.setattr(auto_tickets, "LOCALDATA", tmp_path)
    paused = auto_tickets.load_pause_state()
    assert paused is False

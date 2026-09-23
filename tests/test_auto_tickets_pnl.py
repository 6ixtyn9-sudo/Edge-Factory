"""Contract tests for the door-level bucket P&L tripwire.

This is the surface that turns a bucket's record into deployment weights
(1.0 / 0.5 / 0.0), i.e. the one that moves money. It had no tests at all until
the grading moved onto the shared assay engine, which is the point of this
file: the actuator must be pinned, and it must be pinned to the engine rather
than to a private bar.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
from edgefactory.assay import context_verdict_league
from edgefactory.config import GATES
from edgefactory.util import norm_team


TODAY = "2026-09-23"


def _alpha(i):
    """Two-letter prefix that stays distinct after norm_team() folding.

    norm_team() strips digits and punctuation, so index-based fixture names
    past i=25 collapse onto each other and quietly shrink n.
    """
    return chr(65 + (i // 26) % 26) + chr(65 + i % 26)


def _rows(n, *, wins=0, bucket="SKIPPED_VETO", day="2026-09-20", odds=1.50,
          avg_p=None, market="1x2", pick="HOME"):
    """n archive rows; the first `wins` of them settle as a win for `pick`.

    ``avg_p`` defaults to the exact realised hit rate, which is what makes the
    "calibrated but losing" case constructible: gap zero, ROI negative.
    """
    if avg_p is None:
        # playable_legs() drops any leg without a stated rate (falsy avg_p), so
        # an all-loss fixture must still claim one; 55% is a realistic claim and
        # leaves every non-degenerate case exactly calibrated (gap 0).
        avg_p = max(round(100.0 * wins / n, 4), 55.0) if n else 0.0
    rows, settled = [], {}
    for i in range(n):
        home, away = f"{_alpha(i)}Home FC", f"{_alpha(i).lower()}Away FC"
        rows.append({"date": day, "bucket": bucket, "home": home, "away": away,
                     "pick": pick, "avg_p": avg_p, "odds": odds,
                     "market": market})
        outcome = ("home" if pick == "HOME" else "away") if i < wins else (
            "away" if pick == "HOME" else "home")
        settled[(day, norm_team(home), norm_team(away))] = outcome
    return rows, settled


def _grade_expected(n, wins, odds):
    return round((wins * (odds - 1.0) - (n - wins)) / n, 4)


@pytest.fixture
def state(tmp_path):
    return tmp_path / "bucket_pnl.json"


# ---- the blindness this change removes -----------------------------------

def test_calibrated_but_losing_bucket_is_no_longer_paid_up(state):
    """The old verdict was a z-test on (hit - stated); this is the hole it left.

    30 of 40 legs hit at 1.30 and the stated probability is exactly that 75%,
    so the residual is zero: calibration says nothing is wrong. But 1.30 pays
    only above a 76.9% hit rate, so the bucket still loses. Grading the residual
    called that PAYING; the engine grades the same population CAUTION.
    """
    rows, settled = _rows(40, wins=30, bucket="CAUTION", odds=1.30)
    weights, verdicts = at.compute_bucket_pnl(
        TODAY, archives=rows, settled=settled, path=state)
    v = verdicts["CAUTION"]
    assert v["n"] == 40
    assert v["gap"] == pytest.approx(0.0, abs=1e-4)     # calibration: clean
    assert abs(v["z"]) < 0.3                             # old bar: nothing to see
    assert v["roi"] == _grade_expected(40, 30, 1.30) < 0.0   # money: negative
    assert v["verdict"] == "CAUTION"
    # CAUTION is a warning, not a throttle: weight only moves on VETO here.
    assert v["weight"] == 1.0 and weights["CAUTION"] == 1.0


def test_losing_bucket_at_the_door_reaches_veto_and_closes_it(state):
    rows, settled = _rows(40, wins=0, bucket="CAUTION", odds=1.50)
    assert rows[0]["avg_p"] == 55.0          # stated a rate, lost every one
    for i, day in enumerate(("2026-09-20", "2026-09-21", "2026-09-22",
                             "2026-09-23")):
        weights, verdicts = at.compute_bucket_pnl(
            day, archives=rows, settled=settled, path=state)
        v = verdicts["CAUTION"]
        assert v["verdict"] == "VETO"
        assert v["streak"] == i + 1
        expected = 1.0 if i + 1 < at.PNL_DEMOTE_STREAK else (
            0.0 if i + 1 >= at.PNL_BENCH_STREAK else 0.5)
        assert v["weight"] == pytest.approx(expected)
    assert weights["CAUTION"] == 0.0     # door closed on day four, earned


# ---- engine parity --------------------------------------------------------

@pytest.mark.parametrize("n,wins,odds,expected", [
    (11, 11, 1.50, "UNKNOWN"),       # below the engine's own small-n floor
    (12, 12, 1.25, "ALLOW"),
    (12, 0, 1.50, "VETO"),          # avg_p floors at 55%, so gap != 0 here
    (20, 14, 1.30, "CAUTION"),
    (40, 30, 1.30, "CAUTION"),
    (40, 0, 1.50, "VETO"),
    (120, 110, 1.35, "BOOST"),
])
def test_door_verdict_is_the_engine_verdict(state, n, wins, odds, expected):
    rows, settled = _rows(n, wins=wins, bucket="SKIPPED_VETO", odds=odds)
    weights, verdicts = at.compute_bucket_pnl(
        TODAY, archives=rows, settled=settled, path=state)
    v = verdicts["SKIPPED_VETO"]
    assert v["n"] == n
    assert v["verdict"] == expected
    assert v["verdict"] == context_verdict_league(
        v["n"], v["roi"], v["recent_roi"])


def test_recent_roi_withheld_below_the_system_recent_floor(state):
    """Recency confirms a verdict; it never manufactures one from few legs."""
    rows, settled = _rows(40, wins=30, bucket="SKIPPED_VETO", odds=1.30,
                          day="1999-01-01")            # outside any recent window
    _w, verdicts = at.compute_bucket_pnl(
        TODAY, archives=rows, settled=settled, path=state)
    v = verdicts["SKIPPED_VETO"]
    assert v["n"] == 40 and v["recent_n"] == 0
    assert v["recent_roi"] is None


def test_recent_roi_admitted_once_the_window_is_full(state):
    rows, settled = _rows(GATES.min_recent_n, wins=12, bucket="SKIPPED_VETO",
                          odds=1.50)
    _w, verdicts = at.compute_bucket_pnl(
        TODAY, archives=rows, settled=settled, path=state)
    assert verdicts["SKIPPED_VETO"]["recent_n"] == GATES.min_recent_n
    assert verdicts["SKIPPED_VETO"]["recent_roi"] is not None


# ---- streak semantics (unchanged, and the reason money is safe) ---------

def test_same_day_rerun_cannot_compound_the_streak(state):
    rows, settled = _rows(40, wins=0, bucket="CAUTION", odds=1.50)
    _w, first = at.compute_bucket_pnl(TODAY, archives=rows, settled=settled,
                                      path=state)
    _w, second = at.compute_bucket_pnl(TODAY, archives=rows, settled=settled,
                                       path=state)
    assert first["CAUTION"]["streak"] == second["CAUTION"]["streak"] == 1


def test_streak_resets_on_a_clean_verdict(state):
    state.write_text(json.dumps({
        "last_eval": "2026-09-22",
        "buckets": {"CAUTION": {"streak": 3}},
    }))
    rows, settled = _rows(40, wins=40, bucket="CAUTION", odds=1.50)
    weights, verdicts = at.compute_bucket_pnl(
        TODAY, archives=rows, settled=settled, path=state)
    assert verdicts["CAUTION"]["verdict"] == "ALLOW"
    assert verdicts["CAUTION"]["streak"] == 0
    assert weights["CAUTION"] == 1.0


def test_door_stays_open_below_the_evidence_floor(state):
    """'Benches are EARNED by evidence, never by silence.'"""
    rows, settled = _rows(9, wins=0, bucket="CAUTION", odds=1.50)
    weights, verdicts = at.compute_bucket_pnl(
        TODAY, archives=rows, settled=settled, path=state)
    assert verdicts["CAUTION"]["verdict"] == "UNKNOWN"
    assert verdicts["CAUTION"]["streak"] == 0
    assert weights["CAUTION"] == 1.0


def test_bench_tier_still_requires_a_current_veto(state, monkeypatch):
    """Streak alone must not close a door the engine no longer condemns."""
    monkeypatch.setattr(at, "PNL_DEMOTE_ON_CAUTION", True)
    state.write_text(json.dumps({
        "last_eval": "2026-09-22",
        "buckets": {"CAUTION": {"streak": at.PNL_BENCH_STREAK}},
    }))
    # CAUTION-grade, not VETO-grade: negative but above the -5%/-3% bars.
    rows, settled = _rows(40, wins=30, bucket="CAUTION", odds=1.30)
    weights, verdicts = at.compute_bucket_pnl(
        TODAY, archives=rows, settled=settled, path=state)
    v = verdicts["CAUTION"]
    assert v["verdict"] == "CAUTION"
    assert v["streak"] == at.PNL_BENCH_STREAK + 1     # past the bench floor...
    assert v["weight"] == pytest.approx(0.5)          # ...but still not closed
    assert weights["CAUTION"] == pytest.approx(0.5)


def test_kill_switch_disables_weights_but_not_evidence(state, monkeypatch):
    monkeypatch.setattr(at, "PNL_BENCH_ENABLED", False)
    rows, settled = _rows(40, wins=0, bucket="CAUTION", odds=1.50)
    _w, _first = at.compute_bucket_pnl(TODAY, archives=rows, settled=settled,
                                         path=state)
    state.write_text(json.dumps({
        "last_eval": "2026-09-22",
        "buckets": {"CAUTION": {"streak": at.PNL_BENCH_STREAK}},
    }))
    weights, verdicts = at.compute_bucket_pnl(
        TODAY, archives=rows, settled=settled, path=state)
    assert weights == {}                            # policy identity
    assert verdicts["CAUTION"]["verdict"] == "VETO"  # evidence still grades


def test_demote_on_caution_flag_advances_the_soft_tier(state, monkeypatch):
    monkeypatch.setattr(at, "PNL_DEMOTE_ON_CAUTION", True)
    rows, settled = _rows(40, wins=30, bucket="CAUTION", odds=1.30)
    _w, first = at.compute_bucket_pnl(TODAY, archives=rows, settled=settled,
                                      path=state)
    assert first["CAUTION"]["verdict"] == "CAUTION"
    assert first["CAUTION"]["streak"] == 1
    _w, second = at.compute_bucket_pnl(
        "2026-09-24", archives=rows, settled=settled, path=state)
    assert second["CAUTION"]["streak"] == 2
    assert second["CAUTION"]["weight"] == pytest.approx(0.5)


# ---- accounting ----------------------------------------------------------

def test_void_and_ungraded_legs_are_invisible_never_auto_loss(state):
    rows, settled = _rows(20, wins=10, bucket="CAUTION", odds=1.50)
    for i in range(15, 20):                          # 10 wins, 5 voids, 5 losses
        settled[list(settled)[i]] = " postponed"
    weights, verdicts = at.compute_bucket_pnl(
        TODAY, archives=rows, settled=settled, path=state)
    v = verdicts["CAUTION"]
    assert v["n"] == 15                              # voids excluded entirely
    assert v["hit"] == pytest.approx(10 / 15, rel=1e-4)
    assert weights["CAUTION"] == 1.0


def test_roi_is_priced_leg_accounting_not_pnl_over_n(state):
    """Matches assay_purity / decay_monitor: pnl / n_priced."""
    rows, settled = _rows(40, wins=20, bucket="CAUTION", odds=1.50)
    _w, verdicts = at.compute_bucket_pnl(TODAY, archives=rows, settled=settled,
                                         path=state)
    v = verdicts["CAUTION"]
    assert v["roi"] == _grade_expected(40, 20, 1.50)
    assert v["roi_flat"] == pytest.approx(v["roi"], rel=1e-9)  # all priced here


def test_pre_engine_state_file_reads_and_re_earns_from_scratch(state):
    """Deploying onto a machine holding the OLD report shape must not crash.

    The state file written before this change carried private `min_n`/`z_bench`
    keys and a PAYING/BLEEDING vocabulary, with streaks earned under a statistic
    that no longer exists. The reader takes only `last_eval` and the per-bucket
    streak, so it loads, rewrites in the engine shape, and drops the stale keys.
    A stored BLEEDING-era streak is therefore forgiven on the first new run: it
    was earned by a rule that could not see calibrated-but-losing, so honouring
    it would mean enforcing a dead test. A bucket that really is bleeding re-earns
    the streak from zero within PNL_DEMOTE_STREAK days.
    """
    state.write_text(json.dumps({
        "generated_at": "2026-09-22T11:00:00+02:00", "last_eval": "2026-09-22",
        "window_days": 21, "min_n": 20, "z_bench": -2.0, "enabled": True,
        "buckets": {"CAUTION": {"n": 49, "verdict": "BLEEDING", "streak": 2,
                                "weight": 0.5}},
    }))
    rows, settled = _rows(40, wins=30, bucket="CAUTION", odds=1.30)
    weights, verdicts = at.compute_bucket_pnl(
        TODAY, archives=rows, settled=settled, path=state)
    v = verdicts["CAUTION"]
    assert v["verdict"] == "CAUTION" and v["streak"] == 0
    assert v["weight"] == pytest.approx(1.0)
    assert weights["CAUTION"] == pytest.approx(1.0)
    report = json.loads(state.read_text())
    assert "min_n" not in report and "z_bench" not in report   # rewritten, not merged
    assert report["engine"].endswith("context_verdict_league")


def test_report_records_which_engine_graded_the_door(state):
    rows, settled = _rows(40, wins=20, bucket="CAUTION", odds=1.50)
    at.compute_bucket_pnl(TODAY, archives=rows, settled=settled, path=state)
    report = json.loads(state.read_text())
    assert report["engine"] == "edgefactory.assay.context_verdict_league"
    assert report["grade_engine"] == "edgefactory.assay.grade"
    assert report["population"] == "all playable archived legs (candidate universe)"
    assert report["recent_min_n"] == GATES.min_recent_n
    assert report["window_days"] == GATES.recent_window_days
    assert set(report["buckets"]["CAUTION"]) >= {"verdict", "roi", "recent_roi",
                                                 "wilson_lb", "grade", "streak",
                                                 "weight", "gap", "z"}


def test_works_with_no_state_and_no_archives(tmp_path):
    """CI-certifying runs must not die on an empty ledger."""
    path = tmp_path / "bucket_pnl.json"
    weights, verdicts = at.compute_bucket_pnl(TODAY, archives=[], settled={},
                                             path=path)
    assert set(verdicts) == set(at.BUCKETS)
    assert all(v["weight"] == 1.0 for v in verdicts.values())
    assert all(v["verdict"] == "UNKNOWN" for v in verdicts.values())
    assert weights and all(w == 1.0 for w in weights.values())

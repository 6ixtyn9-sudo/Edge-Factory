"""The replay harness must see what the builder saw.

Three faithfulness bugs were found while asking whether the 2026-10-25 card
(2 accas, both lost, −71.7pp — the lane's biggest single-day fall) had missed
something on the slate:

* **wrong pool.** ``build_universe`` called ``playable_legs`` without
  ``execution_safe=True`` and without ``live_kickoff_guard``. The live builder
  runs both, so every replay rode quotes no ticket could carry and legs that
  had already kicked off. On 2026-10-25 that put FC Tokyo (6-0 winner, kickoff
  09:00 SAST) on the replay card although the 09:56 freeze had already lost it.
* **wrong clock.** Replays guarded at the canonical 09:00 build for every day.
  A card that only froze at 09:56 (10-25), 10:09 (10-20) or 11:25 (10-22) is
  not the card a 09:00 build would have made.
* **wrong slate generation.** ``localdata`` keeps ``picks_morning_<day>.json``
  (the capture the build consumed) and ``picks_<day>.json`` (a later
  re-scoring). The archive loader reads only the latter, so replays ranked on
  re-scored probabilities *and* re-bucketed purity: 2026-10-25 Barcelona is
  73.0% / SKIPPED_VETO in the morning slate and 69.4% / CAUTION afterwards.

With all three fixed the harness rebuilds 2026-10-25's ledger card exactly
(``@2.18`` Barcelona + Union Saint-Gilloise, ``@1.78`` Strømmen + OFK).
"""
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
import replay_harness as rh  # noqa: E402

DAY = "2026-10-25"


@pytest.fixture(autouse=True)
def _sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(at, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(rh, "LOCALDATA", tmp_path)
    at.SETTLED_KEY_NAMES.clear()
    yield
    at.SETTLED_KEY_NAMES.clear()


def _row(home, away, pick="home", avg_p=70.0, odds=1.6, bucket="CERTIFIED_CLEAN",
         kickoff="2026-10-25T18:00:00+00:00"):
    return {"date": DAY, "home": home, "away": away, "pick": pick,
            "avg_p": avg_p, "odds": odds, "bucket": bucket, "market": "1x2",
            "kickoff_utc": kickoff, "odds_source": "pinnapi_odds"}


def _write_slates(tmp_path, morning_rows, later_rows):
    (tmp_path / f"picks_morning_{DAY}.json").write_text(json.dumps(morning_rows))
    (tmp_path / f"picks_{DAY}.json").write_text(json.dumps(later_rows))


# ---------------- the slate generation the build actually consumed ----------

def test_the_morning_slate_wins_over_the_end_of_day_rescoring(tmp_path):
    """Barcelona 73%/SKIPPED_VETO at build; 69%/CAUTION after the re-scoring."""
    _write_slates(
        tmp_path,
        [_row("Barcelona", "Real Madrid", avg_p=73.0, bucket="SKIPPED_VETO")],
        [_row("FC Barcelona", "Real Madrid", avg_p=69.4, bucket="CAUTION")])
    rows = rh.slate_generation(True)[DAY]
    assert len(rows) == 1
    assert rows[0]["avg_p"] == 73.0
    assert rows[0]["bucket"] == "SKIPPED_VETO"


def test_a_day_without_a_morning_capture_falls_back_to_the_archive(tmp_path):
    (tmp_path / f"picks_{DAY}.json").write_text(
        json.dumps([_row("Alpha", "Beta", avg_p=66.0)]))
    rows = rh.slate_generation(True)[DAY]
    assert len(rows) == 1 and rows[0]["avg_p"] == 66.0


def test_the_superset_generation_still_reads_the_archive(tmp_path):
    _write_slates(tmp_path, [_row("Alpha", "Beta", avg_p=70.0)],
                  [_row("Alpha", "Beta", avg_p=60.0)])
    rows = rh.slate_generation(False)[DAY]
    assert [r["avg_p"] for r in rows] == [60.0]


# ---------------- the clock a day's card was really built on ----------------

def _freeze(day, stamp):
    return {at.FROZEN_BOOK_KEY: {day: {"frozen_at": stamp, "final": True}}}


def test_the_build_instant_is_the_real_freeze_stamp():
    when = rh.build_instant_for(DAY, _freeze(DAY, f"{DAY}T09:56:00+02:00"))
    assert when == datetime(2026, 10, 25, 9, 56, tzinfo=at.TZ)


def test_an_unfrozen_day_falls_back_to_the_canonical_build():
    assert rh.build_instant_for(DAY, {}) == at.canonical_build_instant(DAY)


def test_a_naive_freeze_stamp_is_read_in_the_lane_zone():
    when = rh.build_instant_for(DAY, _freeze(DAY, f"{DAY}T09:56:00"))
    assert when == datetime(2026, 10, 25, 9, 56, tzinfo=at.TZ)


# ---------------- the pool the builder could actually bet ----------------

def test_a_leg_that_already_kicked_off_is_not_in_the_faithful_pool():
    """09:00 SAST kickoff, 09:56 freeze: the leg was gone (FC Tokyo, 6-0)."""
    rows = [_row("FC Tokyo", "Mito Hollyhock", kickoff="2026-10-25T07:00:00+00:00"),
            _row("Porto", "Braga", kickoff="2026-10-25T20:00:00+00:00")]
    state = _freeze(DAY, f"{DAY}T09:56:00+02:00")
    pool, drops = rh.live_pool(rows, {}, DAY, faithful=True, state=state)
    assert [l["match"] for l in pool] == ["Porto vs Braga"]
    assert drops == {at.KO_SKIP_STARTED: ["FC Tokyo vs Mito Hollyhock"]}


def test_the_same_pool_at_the_canonical_build_keeps_the_photo_finish_leg():
    """At 09:00 exactly the 09:00 kickoff had not yet passed."""
    rows = [_row("FC Tokyo", "Mito Hollyhock", kickoff="2026-10-25T07:00:00+00:00")]
    pool, _drops = rh.live_pool(rows, {}, DAY, faithful=True, state={})
    assert [l["match"] for l in pool] == ["FC Tokyo vs Mito Hollyhock"]


def test_the_unfaithful_pool_restores_the_superset():
    rows = [_row("FC Tokyo", "Mito Hollyhock", kickoff="2026-10-25T07:00:00+00:00")]
    pool, drops = rh.live_pool(rows, {}, DAY, faithful=False,
                               state=_freeze(DAY, f"{DAY}T09:56:00+02:00"))
    assert len(pool) == 1 and drops == {}


def test_the_faithful_pool_applies_the_execution_gate():
    """A sole-source quote cannot become a ticket, so it cannot ride a replay."""
    row = dict(_row("Alpha", "Beta"), odds_source="scoutingstats",
               price_evidence="SCOUTINGSTATS_SOLE", price_push_eligible=False,
               price_corroboration_sufficient=False)
    faithful, _ = rh.live_pool([row], {}, DAY, faithful=True, state={})
    superset, _ = rh.live_pool([row], {}, DAY, faithful=False, state={})
    assert faithful == [] and len(superset) == 1


# ---------------- parity comparison helpers ----------------

def test_card_equality_ignores_which_acca_is_printed_first():
    got = [frozenset({"a", "b"}), frozenset({"c", "d"})]
    want = [frozenset({"c", "d"}), frozenset({"a", "b"})]
    assert rh._card_equal(got, want)


def test_card_equality_ignores_naming_noise():
    """'Atalanta vs Pafos FC' and 'Atalanta vs Pafos' are one fixture."""
    got = rh._card_names([["Atalanta vs Pafos", "Lech Poznan vs Bayer Leverkusen"]])
    want = rh._card_names([["Atalanta vs Pafos FC", "Lech Poznan vs Bayer Leverkusen"]])
    assert rh._card_equal(got, want)


def test_card_equality_still_sees_a_substituted_leg():
    got = rh._card_names([["Alpha vs Beta", "Gamma vs Delta"]])
    want = rh._card_names([["Alpha vs Beta", "Epsilon vs Zeta"]])
    assert not rh._card_equal(got, want)


def test_the_ledger_reader_never_repairs_the_state(tmp_path, monkeypatch):
    """Parity must observe the ledger, not run load_state's repairs."""
    path = tmp_path / "state.json"
    path.write_text(json.dumps({"bank": 215.185722, "history": []}))
    monkeypatch.setattr(at, "STATE_FILE", path)
    before = path.read_bytes()
    assert rh._ledger_state()["bank"] == pytest.approx(215.185722)
    assert path.read_bytes() == before


# ---------------- the modes run end to end ----------------

def test_parity_reports_a_match_for_a_day_the_replay_rebuilds(tmp_path, capsys):
    legs = [_row("Alpha", "Beta", avg_p=74.0), _row("Gamma", "Delta", avg_p=73.0),
            _row("Epsilon", "Zeta", avg_p=72.0), _row("Eta", "Theta", avg_p=71.0)]
    for r in legs:
        r["outcome"] = r["pick"]
    _write_slates(tmp_path, legs, legs)
    settled = {(DAY, "alpha", "beta"): "home", (DAY, "gamma", "delta"): "home",
               (DAY, "epsilon", "zeta"): "home", (DAY, "eta", "theta"): "home"}
    plan = at.plan_day(
        [l for l in at.playable_legs(legs, day=DAY, settled=settled, floor=0.0,
                                     execution_safe=True) if l["result"]], 100.0)
    assert plan, "fixture needs a buildable card"
    cards = [[l["match"] for l in a["legs"]] for a in plan]
    (tmp_path / "state.json").write_text(json.dumps({
        "bank": 100.0,
        "history": [{"date": DAY, "staked_pct": 25.0, "returned_pct": 0.0,
                     "accas": [{"legs": [{"match": m} for m in acca]} for acca in cards]}],
        at.FROZEN_BOOK_KEY: {DAY: {"frozen_at": f"{DAY}T09:30:00+02:00"}},
    }))
    assert rh.cmd_parity([], settled) == 0
    out = capsys.readouterr().out
    assert "MATCH 1" in out and "DIFF 0" in out


def test_slate_prints_the_funnel_and_the_refused_winners(tmp_path, capsys):
    rows = [_row("Alpha", "Beta", avg_p=80.0, odds=1.20),      # below the floor
            _row("Gamma", "Delta", avg_p=74.0)]
    for r in rows:
        r["outcome"] = r["pick"]
    _write_slates(tmp_path, rows, rows)
    settled = {(DAY, "alpha", "beta"): "home", (DAY, "gamma", "delta"): "home"}
    assert rh.cmd_slate([], settled, DAY) == 0
    out = capsys.readouterr().out
    assert "archived candidate rows: 2" in out
    assert "min_odds_floor" in out
    assert "excluded legs that WON" in out and "Alpha vs Beta" in out

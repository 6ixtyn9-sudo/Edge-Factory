"""A settlement step that failed to publish must not wedge the next run.

2026-10-26: run 40238094510 settled the 2026-10-25 enhancement card and drafted
the 2026-10-26 slip, then had its state push rejected with a remote 500. The
next run restored that cache and ``scripts/phase5_persistence.py restore``
raised ``EvidenceMergeError: divergent enhancement financial histories:
different open positions, freeze locks or cycle state`` -- because HEAD still
carried the un-settled card while the cache carried the settlement *and* the
next draft. ``set -e`` killed the job at step one, so nothing else ran, and
every later run restored the same cache and hit the same wall.

The repair accepts exactly one settlement step (settled accas plus a fresh,
unfrozen draft) and keeps refusing everything else. These tests pin both
halves: the step that must be accepted, and the shortcuts that must not be.
"""
import json
import subprocess

import pytest

from scripts import phase5_persistence as persistence


def _leg(match, pick, odds):
    return {"match": match, "pick": pick, "odds": odds, "result": None}


def _acca(odds, stake, legs):
    return {"odds": odds, "stake_pct": stake, "legs": legs, "won": None}


@pytest.fixture
def settlement_step(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.name", "Test")
    git("config", "user.email", "test@example.invalid")

    won = _acca(2.42, 3.288, [_leg("A vs B", "under", 1.818),
                              _leg("C vs D", "home", 1.333)])
    lost = _acca(1.88, 3.288, [_leg("E vs F", "over", 1.33),
                               _leg("G vs H", "over", 1.41)])
    head = {
        "base_pct": 100.0,
        "bank": 39.4565,
        "cycle_base": 100.0,
        "events": [],
        "history": [{"date": "2026-10-24", "staked_pct": 13.1522,
                     "returned_pct": 0.0, "bank_pct": 39.4565,
                     "accas": [{"odds": 1.99, "stake_pct": 13.1522,
                                "returned_pct": 0.0, "won": False,
                                "legs": [_leg("Old vs Fixture", "home", 1.99)]}]}],
        "open_slips": [{"date": "2026-10-25", "staked_pct": 6.576, "accas": [won, lost]}],
        "frozen_by_date": {"2026-10-25": {"frozen_at": "2026-10-25T10:06:31+02:00",
                                          "final": True, "lock_source": "state"}},
    }
    # Settled: bank 39.4565 - 6.576 + 3.288 * 2.42 = 40.8348 (the lost acca
    # returns nothing).  The next card is drafted, not yet frozen.
    cache = json.loads(json.dumps(head))
    cache["bank"] = 39.4565 + 3.288 * 2.42 - 6.576
    settled_row = {"date": "2026-10-25", "staked_pct": 6.576,
                   "returned_pct": 3.288 * 2.42, "bank_pct": cache["bank"],
                   "accas": [
                       dict(won, won=True, returned_pct=3.288 * 2.42, legs=[
                           dict(won["legs"][0], result="win"),
                           dict(won["legs"][1], result="win")]),
                       dict(lost, won=False, returned_pct=0.0, legs=[
                           dict(lost["legs"][0], result="win"),
                           dict(lost["legs"][1], result="loss")]),
                   ]}
    # Deep-copied: a shared row dict would mutate HEAD along with the cache.
    cache["history"] = json.loads(json.dumps(head["history"])) + [settled_row]
    draft = _acca(2.11, 0.047 * cache["bank"], [_leg("New vs Card", "over", 1.30),
                                                _leg("Next vs Card", "over", 1.62)])
    cache["open_slips"] = [{"date": "2026-10-26", "staked_pct": draft["stake_pct"],
                            "accas": [draft]}]

    path = tmp_path / persistence.ENH_STATE
    path.parent.mkdir()

    def install(committed, cached):
        path.write_text(json.dumps(committed))
        git("add", ".")
        git("commit", "--allow-empty", "-qm", "settlement step fixture")
        path.write_text(json.dumps(cached))

    return tmp_path, path, head, cache, install


def test_settlement_plus_next_draft_survives_restore(settlement_step):
    repo, path, head, cache, install = settlement_step
    install(head, cache)
    persistence.restore_committed_localdata(repo)
    restored = json.loads(path.read_text())
    # The settlement is kept, the next draft is kept, the bank moved with it.
    assert restored["bank"] == pytest.approx(cache["bank"])
    assert [row["date"] for row in restored["history"]] == ["2026-10-24", "2026-10-25"]
    assert [slip["date"] for slip in restored["open_slips"]] == ["2026-10-26"]
    assert restored["frozen_by_date"] == head["frozen_by_date"]


def test_settlement_step_is_idempotent(settlement_step):
    repo, path, head, cache, install = settlement_step
    install(head, cache)
    persistence.restore_committed_localdata(repo)
    first = path.read_bytes()
    persistence._retain_financial_state(repo)
    assert path.read_bytes() == first


@pytest.mark.parametrize("change", [
    "bank_drift", "invented_day", "changed_committed_leg", "draft_on_frozen_day",
    "new_lock", "rewritten_history", "bad_won",
])
def test_only_a_true_settlement_step_is_accepted(settlement_step, change):
    repo, path, head, cache, install = settlement_step
    if change == "bank_drift":
        cache["bank"] += 5
    elif change == "invented_day":
        # A brand-new bet-day that closes no committed position.
        cache["history"].append({
            "date": "2026-10-25b", "staked_pct": 3.0, "returned_pct": 0.0,
            "bank_pct": cache["bank"],
            "accas": [dict(odds=2.0, stake_pct=3.0, returned_pct=0.0, won=False, legs=[])]})
        cache["bank"] -= 3.0
    elif change == "changed_committed_leg":
        cache["history"][1]["accas"][0]["legs"][0]["match"] = "Someone vs Else"
        cache["history"][1]["accas"][0]["legs"][0]["pick"] = "away"
    elif change == "draft_on_frozen_day":
        cache["open_slips"][0]["date"] = "2026-10-25"
    elif change == "new_lock":
        cache["frozen_by_date"]["2026-10-26"] = {"final": True, "frozen_at": None}
    elif change == "rewritten_history":
        cache["history"][0]["accas"][0]["odds"] = 9.99
    else:
        cache["history"][1]["accas"][0]["won"] = "yes"
    install(head, cache)
    before = path.read_bytes()
    with pytest.raises(persistence.EvidenceMergeError):
        persistence.restore_committed_localdata(repo)
    assert path.read_bytes() == before      # the conflicting cache is preserved


def test_cache_still_settles_when_the_push_only_lost_the_settlement(settlement_step):
    """No draft yet: the plain settlement extension must still restore."""
    repo, path, head, cache, install = settlement_step
    cache["open_slips"] = []
    install(head, cache)
    persistence.restore_committed_localdata(repo)
    restored = json.loads(path.read_text())
    assert restored["bank"] == pytest.approx(cache["bank"])
    assert restored["open_slips"] == []

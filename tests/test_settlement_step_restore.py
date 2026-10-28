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


def _reconciled(state, day='2026-10-25'):
    state['settled_enhancement_reconciliations'] = {
        day: {'confirmed_none_placed': True, 'removed_row_sha256': 'a' * 64,
              'receipt_sha256': 'b' * 64, 'bank_before_pct': 35., 'bank_after_pct': 39.}}


@pytest.mark.parametrize('cache_claims_applied', [False, True])
def test_old_cache_cannot_resurrect_reconciled_unplaced_settlement(settlement_step, cache_claims_applied):
    repo, path, head, cache, install = settlement_step
    head['open_slips'] = []
    head['frozen_by_date'] = {}
    _reconciled(head)
    cache['open_slips'] = []
    cache['frozen_by_date'] = {}
    if cache_claims_applied:
        _reconciled(cache)
    install(head, cache)
    before = path.read_bytes()
    # No original receipt file exists: the committed application book suffices.
    with pytest.raises(persistence.EvidenceMergeError, match='refusing to resurrect an unplaced bet'):
        persistence.restore_committed_localdata(repo)
    assert path.read_bytes() == before


def test_real_later_frozen_card_on_reconciled_date_can_still_settle(settlement_step):
    repo, path, head, cache, install = settlement_step
    _reconciled(head)
    install(head, cache)
    persistence.restore_committed_localdata(repo)
    restored = json.loads(path.read_text())
    assert restored['bank'] == pytest.approx(cache['bank'])
    assert restored['history'] == cache['history']
    assert restored['settled_enhancement_reconciliations'] == head['settled_enhancement_reconciliations']


def test_reconciliation_guard_rejects_topup_with_no_committed_position(settlement_step):
    repo, path, head, cache, install = settlement_step
    row = json.loads(json.dumps(cache['history'][-1]))
    row['accas'] = row['accas'][:1]
    row['staked_pct'] = row['accas'][0]['stake_pct']
    row['returned_pct'] = row['accas'][0]['returned_pct']
    head['history'].append(row)
    head['open_slips'] = []
    cache['open_slips'] = []
    cache['bank'] = head['bank'] - cache['history'][-1]['accas'][-1]['stake_pct']
    _reconciled(head)
    install(head, cache)
    with pytest.raises(persistence.EvidenceMergeError, match='reconciled date'):
        persistence.restore_committed_localdata(repo)


def test_reconciliation_guard_does_not_repair_already_committed_loss(settlement_step):
    repo, path, head, cache, install = settlement_step
    _reconciled(cache)
    install(cache, cache)
    persistence.restore_committed_localdata(repo)
    assert json.loads(path.read_text()) == cache


def test_forged_cached_reconciliation_cannot_block_a_valid_settlement(settlement_step):
    repo, path, head, cache, install = settlement_step
    _reconciled(cache)
    install(head, cache)
    persistence.restore_committed_localdata(repo)
    assert json.loads(path.read_text())['bank'] == pytest.approx(cache['bank'])


@pytest.mark.parametrize('change', ['not_frozen', 'settles_same_position_twice'])
def test_reconciled_date_requires_one_frozen_position_per_added_acca(settlement_step, change):
    repo, path, head, cache, install = settlement_step
    _reconciled(head)
    if change == 'not_frozen':
        head['frozen_by_date'] = {}
        cache['frozen_by_date'] = {}
    else:
        row = cache['history'][-1]
        row['accas'].append(json.loads(json.dumps(row['accas'][0])))
        row['staked_pct'] += row['accas'][0]['stake_pct']
        row['returned_pct'] += row['accas'][0]['returned_pct']
        cache['bank'] += row['accas'][0]['returned_pct'] - row['accas'][0]['stake_pct']
    install(head, cache)
    with pytest.raises(persistence.EvidenceMergeError, match='reconciled date'):
        persistence.restore_committed_localdata(repo)


@pytest.mark.parametrize('relative', [persistence.MAIN_STATE, persistence.ENH_STATE])
@pytest.mark.parametrize('cache_corrected', [False, True])
def test_HEAD_verified_regulation_regrade_survives_cache_restore(tmp_path, relative, cache_corrected):
    import copy
    from scripts import auto_tickets as at
    def git(*args):
        subprocess.run(['git', *args], cwd=tmp_path, check=True, capture_output=True)
    git('init', '-q')
    git('config', 'user.name', 'Test')
    git('config', 'user.email', 'test@example.invalid')
    day = '2026-10-27'
    fact = dict(date=day,home='RSD Alcalá',away='Las Palmas',hs=1,gs=1,outcome='draw',score_period='regulation')
    head = dict(bank=40., base_pct=100.,cycle_base=100.,events=[],open_slips=[],
                frozen_by_date={day:dict(final=True,frozen_at=day+'T09:30:00+02:00')},
                history=[dict(date=day,staked_pct=4.,returned_pct=9.8,bank_pct=40.,close_pct=40.,accas=[
                    dict(odds=2.45,stake_pct=4.,won=True,returned_pct=9.8,legs=[
                        dict(match='RSD Alcalá vs Las Palmas',pick='AWAY',odds=1.55,result='win'),
                        dict(match='AS Roma vs Cagliari',pick='HOME',odds=1.33,result='win')])])])
    config = tmp_path / 'Config/verified_results.json'
    config.parent.mkdir()
    config.write_text(json.dumps(dict(rows=[fact])))
    path = tmp_path / relative
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(head))
    git('add', '.')
    git('commit', '-qm', 'reviewed regulation result and original financial state')
    cache = copy.deepcopy(head)
    if cache_corrected:
        at.regrade_verified_settlements(cache, verified=[fact])
    path.write_text(json.dumps(cache))
    restored = json.loads(persistence._retain_financial_state(tmp_path, relative))
    assert restored['bank'] == pytest.approx(30.2)
    assert restored['history'][0]['returned_pct'] == 0.
    assert restored['frozen_by_date'] == head['frozen_by_date']
    # A cached approval is NOT authority. Unknown bank/stake changes still fail.
    cache['bank'] += 1.
    path.write_text(json.dumps(cache))
    with pytest.raises(persistence.EvidenceMergeError):
        persistence._retain_financial_state(tmp_path, relative)


def test_plain_script_finance_projection_works_without_root_PYTHONPATH(tmp_path):
    import os
    from pathlib import Path
    # Run the real script-module import layout in a child interpreter, isolated
    # from pytest's extra sys.path entries and in a non-repository cwd.
    script = Path(persistence.__file__).resolve()
    code = "import sys;sys.path.insert(0,sys.argv[1]);import phase5_persistence as p;from pathlib import Path;print(p._reviewed_financial_projection(Path(sys.argv[2]), {'bank':100,'history':[]}))"
    config = tmp_path/'Config/verified_results.json'
    config.parent.mkdir()
    config.write_text(json.dumps({'rows': []}))
    for args in [('init','-q'),('config','user.name','Test'),('config','user.email','test@example.invalid'),('add','.'),('commit','-qm','reviewed facts')]:
        subprocess.run(['git',*args],cwd=tmp_path,check=True,capture_output=True)
    import sys
    env = dict(os.environ)
    env.pop('PYTHONPATH',None)
    result = subprocess.run([sys.executable,'-c',code,str(script.parent),str(tmp_path)],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "'bank': 100" in result.stdout

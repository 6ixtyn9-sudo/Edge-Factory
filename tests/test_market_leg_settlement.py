"""A market selection is graded from the score, never from a 1x2 row.

2026-10-25: the enhancement card settled ``@2.19 legs=['loss','loss']`` and
``@1.88 legs=['win','loss']``.  Molde beat Fredrikstad 3-1 and Lillestrøm beat
Brann 3-2 -- both Over 2.5 winners -- yet both legs were booked as losses.
Two things could produce that, and both are repaired here:

* a leg carrying ``market`` (or any non-1x2 selection) was still graded from
  the archived pick row when one matched, where the outcome "home"/"away"/"draw"
  is compared with the selection "over" and can never be equal.  Any resolved
  fixture was therefore a guaranteed loss on that path;
* the score path read whatever row answered the key first, including a
  truncated nine-character key that belongs to a different fixture, without the
  identity guards the 1x2 path already applies.

Every settled market leg now also leaves a receipt naming the score it was
graded from, so a wrong score behind a booked loss is visible in the run log
instead of only in the bank.
"""
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402

DAY = "2026-10-25"


@pytest.fixture(autouse=True)
def _sandbox_state(tmp_path, monkeypatch):
    monkeypatch.setattr(at, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(at, "BUCKET_PNL_FILE", tmp_path / "bucket_pnl.json")
    at.SETTLED_KEY_NAMES.clear()
    yield
    at.SETTLED_KEY_NAMES.clear()


def _over_leg(match="Molde vs Fredrikstad", market="match_over_25", label="Match Over 2.5 Goals"):
    return {"match": match, "pick": "over", "odds": 1.44, "label": label,
            "market": market, "result": None}


_FROZEN_AT = datetime(2026, 10, 25, 9, 0, tzinfo=at.TZ)


def _state(legs, stake=3.288):
    st = {
        "base_pct": 100.0, "bank": 100.0, "cycle_base": 100.0,
        "history": [], "events": [],
        "open_slips": [{"date": DAY, "staked_pct": stake, "accas": [
            {"odds": 1.44, "stake_pct": stake, "results": [None] * len(legs),
             "won": None, "legs": legs}]}],
    }
    # A hand-built slip stands for a card that WAS frozen, hence placeable.
    # Only a frozen card settles; see settle_open_slips' unfrozen gate.
    at.record_freeze(st, DAY, _FROZEN_AT)
    return st


# --- the selection decides the grading path, not the presence of a market ---

@pytest.mark.parametrize("leg,expected", [
    ({"pick": "over", "market": "match_over_25"}, True),
    ({"pick": "under", "label": "Match Under 3.5 Goals"}, True),
    ({"pick": "yes", "label": "Both Teams to Score - Yes (BTTS-Yes)"}, True),
    ({"pick": "home", "market": "1x2"}, False),
    ({"pick": "away"}, False),
    ({"pick": "draw", "market": ""}, False),
])
def test_only_core_selections_can_be_graded_by_the_outcome_column(leg, expected):
    assert at.market_graded_selection(leg) is expected


@pytest.mark.parametrize("leg,market", [
    ({"label": "Match Over 2.5 Goals", "pick": "over"}, "match_over_25"),
    ({"label": "Match Over 1.5 Goals", "pick": "over"}, "match_over_15"),
    ({"label": "Match Under 3.5 Goals", "pick": "under"}, "match_under_35"),
    ({"label": "Home Team Over 0.5 Goals", "pick": "home"}, "home_over_05"),
    ({"label": "Away Team Under 2.5 Goals", "pick": "under"}, "away_under_25"),
    ({"label": "Home Team Under 1.5 Goals", "pick": "under"}, "home_under_15"),
    ({"label": "Both Teams to Score - Yes (BTTS-Yes)", "pick": "yes"}, "btts_yes"),
    ({"label": "Something unfamiliar", "pick": "over"}, None),
])
def test_a_frozen_label_still_names_its_market(leg, market):
    assert at.selection_market(leg) == market


def test_over_25_wins_on_a_four_goal_score_through_settlement():
    """The 2026-10-25 Molde leg: 3-1 is four goals, so Over 2.5 is a WIN."""
    scores = {(DAY, "molde", "fredrikstad"): (3, 1)}
    st = _state([_over_leg()])
    lines = at.settle_open_slips(st, {}, archives=[], entries_by_date={}, scores=scores)
    acca = st["history"][-1]["accas"][0]
    assert acca["won"] is True
    assert [leg["result"] for leg in acca["legs"]] == ["win"]
    assert any("legs=['win']" in line for line in lines)
    assert st["bank"] == pytest.approx(100.0 - 3.288 + 3.288 * 1.44)


def test_a_matching_archive_row_never_grades_a_market_leg():
    """The archived 1x2 row says "home" (1-0); the score says 3-1 (Over 2.5).

    Before the repair the row won the lookup and the comparison
    ``"home" == "over"`` booked a loss. The score must decide.
    """
    archives = [{"date": DAY, "home": "Molde", "away": "Fredrikstad", "pick": "over"}]
    settled = {(DAY, "molde", "fredrikstad"): "home"}
    scores = {(DAY, "molde", "fredrikstad"): (3, 1)}
    st = _state([_over_leg()])
    at.settle_open_slips(st, settled, archives=archives, entries_by_date={},
                         scores=scores)
    assert st["history"][-1]["accas"][0]["won"] is True


def test_a_market_leg_without_a_usable_market_is_held_not_lost():
    """No market and no parseable label: hold the leg, never book a loss."""
    leg = {"match": "Molde vs Fredrikstad", "pick": "over", "odds": 1.44,
           "result": None}
    scores = {(DAY, "molde", "fredrikstad"): (3, 1)}
    assert at.enhancement_leg_result(leg, DAY, scores) is None


def test_every_settled_market_leg_names_its_score():
    scores = {(DAY, "molde", "fredrikstad"): (3, 1)}
    at.MARKET_LEG_SETTLED.clear()
    at.settle_open_slips(_state([_over_leg()]), {}, archives=[],
                         entries_by_date={}, scores=scores)
    assert at.MARKET_LEG_SETTLED == [(DAY, "match_over_25", "over", "3-1",
                                      ("molde", "fredrikstad"), "win")]


# --- a truncated key may not answer a market leg with a neighbour's score ---

def test_narrow_key_of_another_fixture_cannot_grade_a_market_leg():
    home, away = "Lillestrøm SK", "SK Brann"
    narrow = at._narrow_result_keys(home, away)
    assert narrow, "fixture must have a truncated tier for this test to bite"
    hk, ak = sorted(narrow)[0]
    at.SETTLED_KEY_NAMES[(DAY, hk, ak)] = {("Lillestrøm 2", "Brann 2")}
    scores = {(DAY, hk, ak): (0, 0)}
    leg = _over_leg("Lillestrøm SK vs SK Brann")
    assert at.enhancement_leg_result(leg, DAY, scores) is None
    # The same row IS readable when the names behind the key are this fixture.
    at.SETTLED_KEY_NAMES[(DAY, hk, ak)] = {("Lillestrøm", "Brann")}
    assert at.enhancement_leg_result(leg, DAY, scores) == "loss"


def test_marker_boundary_blocks_a_marked_market_leg():
    """A women's/youth side may not settle on the senior side's score."""
    leg = _over_leg("Molde W vs Fredrikstad W")
    scores = {(DAY, "molde", "fredrikstad"): (3, 1)}
    assert at.enhancement_leg_result(leg, DAY, scores) is None


# --- only an operator-verified score may re-open a settled leg ---------------

def _settled_state():
    """The 2026-10-25 card as run 40238094510 booked it: 1W / 2L on a bad grade."""
    return {
        "base_pct": 100.0, "bank": 37.5495, "cycle_base": 100.0,
        "events": [], "open_slips": [],
        "history": [
            {"date": "2026-10-24", "staked_pct": 13.1522, "returned_pct": 0.0,
             "bank_pct": 39.4565, "accas": [
                 {"odds": 1.99, "stake_pct": 13.1522, "returned_pct": 0.0,
                  "won": False, "legs": [{"match": "A vs B", "pick": "home",
                                          "odds": 1.99, "result": "loss"}]}]},
            {"date": "2026-10-25", "staked_pct": 9.864, "returned_pct": 7.9569,
             "bank_pct": 37.5495, "accas": [
                 {"odds": 2.42, "stake_pct": 3.288, "returned_pct": 7.9569,
                  "won": True, "legs": [
                      dict(_over_leg("Konyaspor vs Gençlerbirliği",
                                     "away_under_25", "Away Team Under 2.5 Goals"),
                           pick="under", odds=1.818, result="win"),
                      dict(_over_leg("Batman vs Erenler", "home_over_05",
                                     "Home Team Over 0.5 Goals"),
                           pick="home", odds=1.333, result="win")]},
                 {"odds": 2.19, "stake_pct": 3.288, "returned_pct": 0.0,
                  "won": False, "legs": [
                      dict(_over_leg(), odds=1.44, result="loss"),
                      dict(_over_leg("Śląsk Wrocław vs Wieczysta Kraków"),
                           odds=1.52, result="loss")]},
                 {"odds": 1.88, "stake_pct": 3.288, "returned_pct": 0.0,
                  "won": False, "legs": [
                      dict(_over_leg("Sparta Rotterdam vs Ajax"), odds=1.33,
                           result="win"),
                      dict(_over_leg("Lillestrøm SK vs SK Brann"), odds=1.41,
                           result="loss")]}]},
        ],
    }


VERIFIED = [
    {"date": "2026-10-25", "home": "Molde", "away": "Fredrikstad", "hs": 3,
     "gs": 1, "outcome": "home"},
    {"date": "2026-10-25", "home": "Lillestrøm SK", "away": "SK Brann", "hs": 3,
     "gs": 2, "outcome": "home"},
]


def test_a_verified_score_repairs_the_day_and_the_bank():
    st = _settled_state()
    lines = at.regrade_verified_settlements(st, verified=VERIFIED)
    assert any("Molde vs Fredrikstad" in line and "loss -> win" in line
               for line in lines)
    assert any("Lillestrøm" in line and "loss -> win" in line for line in lines)
    # @2.19 stays lost (the Śląsk leg keeps it a loser); @1.88 is now a winner.
    assert st["history"][-1]["accas"][1]["won"] is False
    assert st["history"][-1]["accas"][2]["won"] is True
    assert st["history"][-1]["accas"][2]["returned_pct"] == pytest.approx(
        round(3.288 * 1.88, 4))
    assert st["history"][-1]["returned_pct"] == pytest.approx(7.9569 + 6.1814)
    assert st["bank"] == pytest.approx(43.7309)
    assert any("43.7309" in line for line in lines)


def test_the_regrade_is_idempotent():
    st = _settled_state()
    at.regrade_verified_settlements(st, verified=VERIFIED)
    bank = st["bank"]
    assert at.regrade_verified_settlements(st, verified=VERIFIED) == []
    assert st["bank"] == bank


def test_a_donor_row_cannot_move_a_settled_leg(monkeypatch):
    """No verified row for the fixture: nothing is re-opened."""
    st = _settled_state()
    monkeypatch.setattr("edgefactory.settlement.load_verified_results",
                        lambda *a, **k: [], raising=False)
    assert at.regrade_verified_settlements(st) == []
    assert st["bank"] == pytest.approx(37.5495)


def test_a_verified_row_never_touches_a_different_fixture():
    """Same date, same home name, different away club: refused."""
    st = _settled_state()
    wrong = [{"date": "2026-10-25", "home": "Molde", "away": "Start", "hs": 0,
              "gs": 0, "outcome": "draw"}]
    assert at.regrade_verified_settlements(st, verified=wrong) == []
    assert st["bank"] == pytest.approx(37.5495)


def test_a_void_or_pending_leg_holds_the_day_as_booked():
    st = _settled_state()
    st["history"][-1]["accas"][2]["legs"][0]["result"] = "void"
    lines = at.regrade_verified_settlements(st, verified=VERIFIED)
    assert any("regrade_verified_held" in line for line in lines)
    assert st["history"][-1]["accas"][2]["won"] is False
    assert st["bank"] == pytest.approx(37.5495)


def test_a_half_score_never_claims_the_key(tmp_path, monkeypatch):
    """A broken high-priority donor row must not hide the real score.

    The warehouse tier is read first and setdefault() wins ties, so a row whose
    score is not numeric used to store None and block the overlay's real score:
    the market leg stayed unsettled while the result was right there.
    """
    import duckdb
    import json

    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    con = duckdb.connect(str(tmp_path / "warehouse.duckdb"))
    con.execute("CREATE TABLE bettingclosed_settled "
                "(date VARCHAR, home VARCHAR, away VARCHAR, outcome VARCHAR, "
                " hs VARCHAR, gs VARCHAR)")
    con.execute("INSERT INTO bettingclosed_settled VALUES "
                "('2026-10-25', 'Molde', 'Fredrikstad', 'home', '1', '')")
    con.close()
    (tmp_path / "settled_results.json").write_text(json.dumps({"rows": [
        {"date": "2026-10-25", "home": "Molde", "away": "Fredrikstad",
         "hs": 3, "gs": 1, "outcome": "home"}]}))
    outcomes, _entries, scores = at._collect_settled_facts()
    assert scores[(DAY, "molde", "fredrikstad")] == (3, 1)
    assert at.enhancement_leg_result(_over_leg(), DAY, scores) == "win"


@pytest.mark.parametrize('market,pick', [('1x2', 'AWAY'), ('match_over_25', 'over')])
def test_unseparated_period_never_settles_or_times_out_as_a_void(tmp_path, monkeypatch, market, pick):
    import json
    import copy
    from edgefactory import settlement
    monkeypatch.setattr(settlement, 'load_verified_results', lambda: [])
    (tmp_path / 'settled_results.json').write_text(json.dumps(dict(rows=[
        dict(date=DAY,home='Cup Club',away='Away Club',hs=1,gs=3,outcome='away')],
        period_holds=[dict(date=DAY,home='Cup Club',away='Away Club',status='AET')])))
    facts = at.load_settled()
    assert not facts and facts.period_blocks
    leg = dict(match='Cup Club vs Away Club', market=market, pick=pick, odds=1.55)
    st = _state([leg])
    class Later(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 11, 15, 12, tzinfo=tz or at.TZ)
    monkeypatch.setattr(at, 'datetime', Later)
    before = copy.deepcopy(st)
    lines = at.settle_open_slips(st, facts, archives=[])
    assert st['bank'] == before['bank'] and not st['history']
    assert st['open_slips'] and any('regulation-time score unproven' in line for line in lines)


@pytest.mark.parametrize('market,pick', [('1x2', 'AWAY'), ('match_over_25', 'over')])
def test_operator_regulation_result_regrades_oct27_both_lanes_idempotently(market, pick):
    import copy
    day = '2026-10-27'
    verified = [dict(date=day,home='RSD Alcalá',away='Las Palmas',hs=1,gs=1,outcome='draw',score_period='regulation')]
    acca = dict(odds=2.45, stake_pct=4., returned_pct=9.8, won=True, legs=[
        dict(match='RSD Alcalá vs Las Palmas', market=market, pick=pick, odds=1.68, result='win'),
        dict(match='Levadia vs Tammeka', market='match_under_45', pick='under', odds=1.46, result='win')])
    state = dict(bank=40., history=[dict(date=day,staked_pct=4.,returned_pct=9.8,bank_pct=40.,close_pct=34.,accas=[acca]),
                                   dict(date='2026-10-28',staked_pct=0.,returned_pct=0.,bank_pct=40.,close_pct=34.,accas=[])],
                 open_slips=[dict(date='2026-10-28',staked_pct=3.,accas=[])], frozen_by_date={day: {'final': True}})
    frozen, opened = copy.deepcopy(state['frozen_by_date']), copy.deepcopy(state['open_slips'])
    lines = at.regrade_verified_settlements(state, verified=verified)
    assert state['bank'] == pytest.approx(30.2)
    assert state['history'][0]['accas'][0]['won'] is False
    assert state['history'][0]['returned_pct'] == 0.
    assert state['history'][0]['accas'][0]['legs'][0]['result'] == 'loss'
    assert state['history'][1]['close_pct'] == pytest.approx(24.2)
    assert state['open_slips'] == opened and state['frozen_by_date'] == frozen
    before = copy.deepcopy(state)
    assert at.regrade_verified_settlements(state, verified=verified) == []
    assert state == before and lines


def test_pending_verified_regrade_does_not_consume_a_later_applicable_correction():
    st = _settled_state()
    leg = st['history'][-1]['accas'][2]['legs'][0]
    leg['result'] = None
    original_wrong = st['history'][-1]['accas'][2]['legs'][1]['result']
    at.regrade_verified_settlements(st, verified=VERIFIED)
    assert st['history'][-1]['accas'][2]['legs'][1]['result'] == original_wrong
    leg['result'] = 'win'
    at.regrade_verified_settlements(st, verified=VERIFIED)
    assert st['history'][-1]['accas'][2]['won'] is True


def test_main_cli_runs_verified_regrade_before_settlement(monkeypatch):
    calls = []
    st = dict(bank=100., history=[], open_slips=[])
    monkeypatch.setattr(at, 'load_state', lambda *a: st)
    monkeypatch.setattr(at, 'regrade_verified_settlements', lambda state: calls.append('regrade') or [])
    monkeypatch.setattr(at, 'load_settled', lambda: {})
    monkeypatch.setattr(at, 'settle_open_slips', lambda *a, **k: calls.append('settle') or [])
    monkeypatch.setattr(at, 'print_status', lambda *a: None)
    monkeypatch.setattr(at, 'save_state', lambda *a: None)
    monkeypatch.setattr(sys, 'argv', ['auto_tickets.py', '--settle'])
    assert at.main() == 0
    assert calls == ['regrade', 'settle']


def test_settled_enh_evidence_is_retained_not_rederived_or_aliased():
    import copy
    leg = dict(_over_leg(), prob=.66, cohort_evidence={'rate': .66, 'n': 308},
               ml_rank_probability=.67, ml_model_key='retained-key', ml_model_schema='enh_score_logit_v2',
               ranking_basis='model', floor=1.3, floor_basis='inherited', league='Cup', shadow=False)
    st = _state([copy.deepcopy(leg)])
    # Exercise the real history writer, not just its helper.
    acca = st['open_slips'][0]['accas'][0]
    acca.update(won=True, returned_pct=round(acca['stake_pct']*acca['odds'],4))
    acca['legs'][0]['result'] = 'win'
    at._record_acca_settlement(st, DAY, acca)
    stored = st['history'][0]['accas'][0]['legs'][0]
    for key in ('prob','cohort_evidence','ml_rank_probability','ml_model_key','ml_model_schema',
                'ranking_basis','floor','floor_basis','league','shadow'):
        assert stored[key] == leg[key]
    acca['legs'][0]['cohort_evidence']['n'] = 999
    assert stored['cohort_evidence']['n'] == 308
    facts=[dict(date=DAY,home='Molde',away='Fredrikstad',hs=0,gs=0,outcome='draw')]
    at.regrade_verified_settlements(st,verified=facts)
    once=copy.deepcopy(st)
    assert at.regrade_verified_settlements(st,verified=facts)==[] and st==once
    assert st['history'][0]['accas'][0]['legs'][0]['ml_model_key']=='retained-key'


def test_legacy_settled_leg_shape_is_unchanged():
    assert at._settled_leg_record({'match':'A vs B','pick':'home','odds':1.5},'loss') == {
        'match':'A vs B','pick':'home','odds':1.5,'result':'loss'}

"""ml-fade research ledger + settlement — idempotency, bet-time immutability,
fail-closed settlement, and missing-data behavior.

Contracts pinned here:

  1. Re-running the pipeline never duplicates rows (stable event_key); the
     first-seen bet-time quote and prediction are NEVER overwritten.
  2. Settled/conflict rows are frozen — later information cannot reopen
     or re-price them.
  3. Settlement is fail-closed: exact or alias-confirmed identity, bounded
     date window, unanimous outcome signature; ambiguity -> conflict (loud);
     absence -> pending/unmatched, NEVER a silent win or loss.
  4. Missing prices shrink n_priced denominators; they are never treated as
     losses (or wins).
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from edgefactory.fade import FADE_FAMILY, PARENT_FAMILY  # noqa: E402
from edgefactory.ml_fade_research import (  # noqa: E402
    FadeResearchCollector,
    TeamMatcher,
    load_ledger,
    merge_candidates,
    price_stats,
    rows_by_family,
    save_ledger,
    settle_ledger,
    wilson_lb,
)

NOW = "2026-09-21T12:00:00+02:00"


def _candidates(**over) -> list[dict]:
    c = FadeResearchCollector()
    anchor = {"home": "Alpha FC", "away": "Beta United", "league": "L",
              "sport": "soccer", "kickoff": "2026-09-21T19:00:00+02:00"}
    anchor.update(over.pop("anchor", {}))
    c.record(day=over.pop("day", "2026-09-21"), anchor=anchor,
             fb=over.pop("fb", {"odd1": 2.10, "oddx": 3.3, "odd2": 3.60}),
             zb=over.pop("zb", {"odd1": 2.05, "oddx": 3.2, "odd2": 3.50}),
             used=["forebet", "zulubet"],
             majority_pick=over.pop("majority_pick", "home"),
             ml_p=over.pop("ml_p", 0.62), z_score=0.5,
             model=over.pop("model", None))
    return c.finalize()


def _fresh_ledger(cands) -> dict:
    ledger = {"schema": 1, "updated_at": None, "rows": []}
    merge_candidates(ledger, cands, now=NOW)
    return ledger


def test_merge_idempotent_first_quote_frozen():
    ledger = _fresh_ledger(_candidates())
    assert len(ledger["rows"]) == 2
    stats = merge_candidates(
        ledger,
        _candidates(zb={"odd1": 2.05, "oddx": 3.2, "odd2": 4.20}),
        now="2026-09-21T15:00:00+02:00")
    assert len(ledger["rows"]) == 2  # no duplicates
    assert stats.added_fade == 0 and stats.added_parent == 0
    fade = rows_by_family(ledger, FADE_FAMILY)[0]
    assert fade["first_odds_zulubet"] == pytest.approx(3.50)  # bet-time frozen
    assert fade["latest_odds_zulubet"] == pytest.approx(4.20)  # latest observed
    assert stats.repriced == 1
    assert fade["last_seen_at"] == "2026-09-21T15:00:00+02:00"


def test_parent_and_fade_distinct_rows_for_same_fixture():
    ledger = _fresh_ledger(_candidates())
    keys = {r["event_key"] for r in ledger["rows"]}
    assert len(keys) == 2
    fams = sorted(r["family"] for r in ledger["rows"])
    assert fams == [FADE_FAMILY, PARENT_FAMILY]


def test_malformed_candidate_skipped_and_counted():
    ledger = {"schema": 1, "updated_at": None, "rows": []}
    stats = merge_candidates(ledger, [{"family": FADE_FAMILY}], now=NOW)
    assert stats.skipped_malformed == 1
    assert ledger["rows"] == []


def test_settle_exact_match_win_and_loss():
    ledger = _fresh_ledger(_candidates())
    facts = [{"date": "2026-09-21", "home": "Alpha FC", "away": "Beta United",
              "hs": 2, "gs": 1, "outcome": "home", "src": "forebet_settled"}]
    stats = settle_ledger(ledger, facts, now=NOW, today=date(2026, 9, 22))
    assert stats.settled == 2
    parent = rows_by_family(ledger, PARENT_FAMILY)[0]
    fade = rows_by_family(ledger, FADE_FAMILY)[0]
    assert parent["graduation"] == "win"    # parent picked home
    assert fade["graduation"] == "loss"     # fade picked away
    assert fade["outcome"] == "home"
    assert fade["score"] == {"hs": 2, "gs": 1}
    assert fade["result_source"] == "forebet_settled"


def test_settle_alias_team_names():
    ledger = _fresh_ledger(_candidates(anchor={"home": "Hearts", "away": "Dundee United"}))
    matcher = TeamMatcher([["Hearts", "Heart of Midlothian"],
                           ["Dundee United", "Dundee Utd"]])
    facts = [{"date": "2026-09-21", "home": "Heart Of Midlothian",
              "away": "Dundee Utd", "hs": 0, "gs": 0, "outcome": "draw",
              "src": "zulubet_settled"}]
    stats = settle_ledger(ledger, facts, matcher=matcher, now=NOW,
                          today=date(2026, 9, 22))
    assert stats.settled == 2
    fade = rows_by_family(ledger, FADE_FAMILY)[0]
    assert fade["graduation"] == "loss"  # draw beats neither home nor away


def test_settle_accent_spelling_variants():
    ledger = _fresh_ledger(_candidates(anchor={"home": "Nordsjælland", "away": "Široki Brijeg"}))
    facts = [{"date": "2026-09-21", "home": "Nordsjaelland",
              "away": "Siroki Brijeg", "hs": 1, "gs": 2, "outcome": "away",
              "src": "forebet_settled"}]
    stats = settle_ledger(ledger, facts, now=NOW, today=date(2026, 9, 22))
    assert stats.settled == 2
    fade = rows_by_family(ledger, FADE_FAMILY)[0]
    assert fade["graduation"] == "win"  # fade of home parent = away


def test_postponement_date_window():
    # result lands 3 days later -> settles (postponement tolerance)
    ledger = _fresh_ledger(_candidates())
    facts = [{"date": "2026-09-24", "home": "Alpha FC", "away": "Beta United",
              "hs": 1, "gs": 0, "outcome": "home", "src": "forebet_settled"}]
    stats = settle_ledger(ledger, facts, now=NOW, today=date(2026, 9, 25))
    assert stats.settled == 2
    fade = rows_by_family(ledger, FADE_FAMILY)[0]
    assert fade["result_date"] == "2026-09-24"
    # 4 days later -> outside the window; nothing settles
    ledger2 = _fresh_ledger(_candidates())
    facts2 = [dict(facts[0], date="2026-09-25")]
    stats2 = settle_ledger(ledger2, facts2, now=NOW, today=date(2026, 9, 25))
    assert stats2.settled == 0


def test_conflicting_outcomes_fail_closed():
    ledger = _fresh_ledger(_candidates())
    facts = [
        {"date": "2026-09-21", "home": "Alpha FC", "away": "Beta United",
         "hs": 2, "gs": 1, "outcome": "home", "src": "a"},
        {"date": "2026-09-21", "home": "Alpha FC", "away": "Beta United",
         "hs": 0, "gs": 2, "outcome": "away", "src": "b"},
    ]
    stats = settle_ledger(ledger, facts, now=NOW, today=date(2026, 9, 22))
    assert stats.conflicts == 2
    assert stats.settled == 0
    fade = rows_by_family(ledger, FADE_FAMILY)[0]
    assert fade["status"] == "conflict"
    assert fade["graduation"] is None  # never guessed
    # frozen: later identical facts cannot quietly un-conflict the row
    stats2 = settle_ledger(ledger, facts, now=NOW, today=date(2026, 9, 23))
    assert rows_by_family(ledger, FADE_FAMILY)[0]["status"] == "conflict"
    assert stats2.already_frozen == 2


def test_unparseable_outcome_is_conflict_not_guess():
    ledger = _fresh_ledger(_candidates())
    facts = [{"date": "2026-09-21", "home": "Alpha FC", "away": "Beta United",
              "hs": None, "gs": None, "outcome": "void", "src": "a"}]
    stats = settle_ledger(ledger, facts, now=NOW, today=date(2026, 9, 22))
    assert stats.conflicts == 2
    assert rows_by_family(ledger, FADE_FAMILY)[0]["graduation"] is None


def test_late_facts_settle_unmatched_rows_then_freeze():
    ledger = _fresh_ledger(_candidates())
    # No fact by day 22 -> unmatched (visible staleness, not a loss)
    stats = settle_ledger(ledger, [], now=NOW, today=date(2026, 10, 20))
    assert stats.unmatched == 2
    fade = rows_by_family(ledger, FADE_FAMILY)[0]
    assert fade["status"] == "unmatched" and fade["graduation"] is None
    # Result eventually arrives (on the captured date): row settles once
    facts = [{"date": "2026-09-21", "home": "Alpha FC", "away": "Beta United",
              "hs": 1, "gs": 1, "outcome": "draw", "src": "forebet_settled"}]
    stats2 = settle_ledger(ledger, facts, now=NOW, today=date(2026, 10, 21))
    assert stats2.settled == 2
    assert rows_by_family(ledger, FADE_FAMILY)[0]["status"] == "settled"
    # a later capture attempt must not touch the frozen settled row
    merge_candidates(ledger, _candidates(zb={"odd2": 9.99}), now="2026-10-21T10:00:00+02:00")
    fade2 = rows_by_family(ledger, FADE_FAMILY)[0]
    assert fade2["first_odds_zulubet"] == pytest.approx(3.50)
    assert fade2["latest_odds_zulubet"] == pytest.approx(3.50)
    assert fade2["graduation"] == "loss"


def test_capture_rows_unchanged_by_settlement():
    """No outcome/closing-price leakage into candidate definition."""
    ledger = _fresh_ledger(_candidates())
    before = [{k: r.get(k) for k in ("pick", "avg_p", "ml_p", "first_odds_forebet",
                                     "first_odds_zulubet", "parent_ml_p")}
              for r in ledger["rows"]]
    facts = [{"date": "2026-09-21", "home": "Alpha FC", "away": "Beta United",
              "hs": 2, "gs": 1, "outcome": "home", "src": "a"}]
    settle_ledger(ledger, facts, now=NOW, today=date(2026, 9, 22))
    after = [{k: r.get(k) for k in ("pick", "avg_p", "ml_p", "first_odds_forebet",
                                    "first_odds_zulubet", "parent_ml_p")}
             for r in ledger["rows"]]
    assert before == after


def test_missing_prices_not_scored_as_losses_or_wins():
    cands = _candidates(zb={"odd1": None, "oddx": None, "odd2": None})
    ledger = _fresh_ledger(cands)
    facts = [{"date": "2026-09-21", "home": "Alpha FC", "away": "Beta United",
              "hs": 2, "gs": 1, "outcome": "home", "src": "a"}]
    settle_ledger(ledger, facts, now=NOW, today=date(2026, 9, 22))
    fades = rows_by_family(ledger, FADE_FAMILY)
    zb_stats = price_stats(fades, "first_odds_zulubet")
    fb_stats = price_stats(fades, "first_odds_forebet")
    assert zb_stats["n"] == 1 and zb_stats["n_priced"] == 0
    assert zb_stats["roi"] is None and zb_stats["pnl"] == 0
    assert fb_stats["n_priced"] == 1 and fb_stats["roi"] is not None


def test_ledger_round_trip_and_fail_closed_load(tmp_path):
    ledger = _fresh_ledger(_candidates())
    path = tmp_path / "ledger.json"
    save_ledger(path, ledger, now=NOW)
    again = load_ledger(path)
    assert len(again["rows"]) == 2
    assert again["rows"] == load_ledger(path)["rows"]  # deterministic
    # schema mismatch -> fail closed (no silent migration)
    path.write_text(json.dumps({"schema": 99, "rows": []}))
    with pytest.raises(ValueError):
        load_ledger(path)
    path.write_text(json.dumps({"schema": 1}))
    with pytest.raises(TypeError):
        load_ledger(path)
    # missing file -> empty v1 ledger (first run ever)
    assert load_ledger(tmp_path / "absent.json")["rows"] == []


def test_save_ordering_deterministic(tmp_path):
    ledger = _fresh_ledger(_candidates())
    p1, p2 = tmp_path / "a.json", tmp_path / "b.json"
    save_ledger(p1, ledger, now=NOW)
    save_ledger(p2, ledger, now=NOW)
    assert p1.read_text() == p2.read_text()


def test_wilson_lb_bounds():
    assert wilson_lb(0, 0) is None
    assert 0 < wilson_lb(8, 10) < 1
    assert wilson_lb(10, 10) < 1  # never touches 1
    assert wilson_lb(80, 100) < wilson_lb(90, 100)

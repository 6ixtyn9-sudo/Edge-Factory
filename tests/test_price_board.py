"""Task F (2026-09-06): automatic build-time price-board capture.

Replaces the D1 owner-input path: NO manual price entry exists anywhere.
enrich_with_live_odds persists, on every pick, every price every source
showed for that fixture+selection at build time (source name + value), and
cmd_today appends one JSONL record per printed leg per run. The engine's
chosen price never changes (board is written alongside, after the choice).
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
import scripts.picks_today as pt  # noqa: E402

ALLOW_CTX = {"league": "ALLOW", "league_key": "test league"}
VETO_CTX = {**ALLOW_CTX, "league": "VETO"}


def _pick(**extra):
    out = {
        "date": "2026-08-05",
        "home": "Alpha United",
        "away": "Beta City",
        "match": "Alpha United vs Beta City",
        "market": "1x2",
        "pick": "home",
        "avg_p": 78.0,
        "odds": 1.70,
        "odds_source": "forebet_best",
        "bookmaker": None,
        "kickoff": "18:00",
    }
    out.update(extra)
    return out


def _row(odds=2.10, bookmaker="AuditBook", captured_at="2026-08-05T10:00:00Z",
         home="Alpha United", away="Beta City", **extra):
    out = {
        "date": "2026-08-05", "home": home, "away": away,
        "market": "1x2", "selection": "home",
        "odds": odds, "bookmaker": bookmaker,
        "captured_at": captured_at, "league": "Test League",
        "kickoff": "18:00", "provider": None,
    }
    out.update(extra)
    return out


def _full_bundle(provider, rows):
    """Build-time bundle shape: market_candidates holds EVERY row per
    (date, market, selection); exact holds the chosen row per fixture."""
    mc = {}
    for r in rows:
        r = {**r, "provider": provider}
        mc.setdefault((r["date"], r["market"], r["selection"]), []).append(r)
    return {"provider": provider, "exact": {}, "time_candidates": {},
            "market_candidates": mc, "raw_rows_list": []}


# ---------------- enrich-side board capture (picks_today) ----------------

def test_board_records_every_source_row_and_marks_the_chosen_price(monkeypatch):
    """Sole-source case: primary had rows for the fixture but no join was
    made; secondary matched. The board must archive the primary's rows too
    (previously discarded) plus the chosen secondary price."""
    pick = _pick(odds=None, odds_source=None)
    primary = _full_bundle(pt.BZZOIRO_ODDS_SOURCE, [
        _row(odds=1.95, bookmaker="BookOne"),
        _row(odds=1.91, bookmaker="BookTwo"),
        _row(odds=1.80, bookmaker="BookThree", home="Other FC", away="Rival"),  # diff fixture
    ])
    secondary = _full_bundle(pt.SCOUTINGSTATS_ODDS_SOURCE,
                             [_row(odds=1.91, bookmaker=pt.SCOUTINGSTATS_ODDS_SOURCE)])

    def find(_pick_, bundle):
        return (None, None) if bundle is primary else (_row(odds=1.91,
                                                            bookmaker=pt.SCOUTINGSTATS_ODDS_SOURCE), "exact")

    monkeypatch.setattr(pt, "find_odds_row", find)
    assert pt.enrich_with_live_odds([pick], primary, secondary) == 1
    # engine choice untouched: sole scoutingstats price is retained + quarantined
    assert pick["odds"] == 1.91
    assert pick["price_evidence"] == pt.PRICE_EVIDENCE_SCOUTINGSTATS_SOLE
    board = pick["price_board"]
    assert len(board) == 3                      # two primary rows + chosen secondary
    assert "Other FC" not in {e.get("home") for e in board}   # other fixture excluded
    bzz = [e for e in board if e["source"] == pt.BZZOIRO_ODDS_SOURCE]
    assert sorted(e["odds"] for e in bzz) == [1.91, 1.95]
    ss = [e for e in board if e["source"] == pt.SCOUTINGSTATS_ODDS_SOURCE]
    assert len(ss) == 1 and ss[0]["odds"] == 1.91
    chosen = [e for e in board if e.get("chosen")]
    assert len(chosen) == 1
    assert chosen[0]["source"] == pt.SCOUTINGSTATS_ODDS_SOURCE
    assert chosen[0]["match_method"] == "exact"


def test_board_real_join_marks_the_exact_row_and_keeps_engine_price():
    """No monkeypatch: real find_odds_row through a real bundle. The chosen
    (best-bookmaker) row is flagged; every row the source showed remains."""
    pick = _pick(odds=None, odds_source=None)
    rows = [_row(odds=1.98, bookmaker="LowBook"),
            _row(odds=1.95, bookmaker="HighBook")]
    bundle = _full_bundle(pt.BZZOIRO_ODDS_SOURCE, rows)
    # exact index mirrors the real builder's preference (HighBook wins)
    bundle["exact"] = {(pick["date"], pt.odds_team_key(pick["home"]),
                        pt.odds_team_key(pick["away"]), "1x2", "home"): {**rows[1], "provider": pt.BZZOIRO_ODDS_SOURCE}}
    assert pt.enrich_with_live_odds([pick], bundle) == 1
    assert pick["odds"] == 1.95                       # engine price unchanged
    assert pick["price_evidence"] == pt.PRICE_EVIDENCE_BZZOIRO_PRIMARY
    board = pick["price_board"]
    assert len(board) == 2
    chosen = [e for e in board if e.get("chosen")]
    assert len(chosen) == 1 and chosen[0]["odds"] == 1.95
    assert chosen[0]["source"] == pt.BZZOIRO_ODDS_SOURCE


def test_board_plain_index_path_records_chosen_row():
    """The audit-refresh call shape (enrich_with_bzzoiro_odds with a plain
    exact index, no market_candidates) still records the chosen row."""
    pick = _pick(odds=None, odds_source=None)
    row = {**_row(odds=2.05), "provider": pt.BZZOIRO_ODDS_SOURCE}
    index = {(pick["date"], pt.odds_team_key(pick["home"]),
              pt.odds_team_key(pick["away"]), "1x2", "home"): row}
    assert pt.enrich_with_bzzoiro_odds([pick], index) == 1
    assert pick["odds"] == 2.05
    board = pick["price_board"]
    assert len(board) == 1
    assert board[0]["source"] == pt.BZZOIRO_ODDS_SOURCE
    assert board[0]["odds"] == 2.05 and board[0]["chosen"] is True


def test_board_is_re_derived_each_run_no_stale_rows(monkeypatch):
    pick = _pick(odds=None, odds_source=None)
    b1 = _full_bundle(pt.BZZOIRO_ODDS_SOURCE, [_row(odds=1.70)])
    b2 = _full_bundle(pt.BZZOIRO_ODDS_SOURCE, [_row(odds=1.60)])

    def find_a(_pick_, bundle):
        return (_row(odds=1.70), "exact")

    def find_b(_pick_, bundle):
        return (_row(odds=1.60), "exact")

    monkeypatch.setattr(pt, "find_odds_row", find_a)
    pt.enrich_with_live_odds([pick], b1)
    assert [e["odds"] for e in pick["price_board"]] == [1.70]
    monkeypatch.setattr(pt, "find_odds_row", find_b)
    pt.enrich_with_live_odds([pick], b2)
    assert [e["odds"] for e in pick["price_board"]] == [1.60]   # no stale rows


# ---------------- printed-leg append-only log (auto_tickets) ----------------

@pytest.fixture(autouse=True)
def _sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(at, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)


class _NoonClock(at.datetime):
    @classmethod
    def now(cls, tz=None):
        return at.datetime(2026, 9, 6, 12, 0, tzinfo=tz or at.TZ)


def _slate_rows_with_boards():
    rows = []
    for i, (home, away, ko) in enumerate([
            ("Sporting CP", "Portimonense", "2026-09-06T20:30:00+02:00"),
            ("Benfica", "Gil Vicente", "2026-09-06T20:45:00+02:00"),
            ("Porto", "Estoril Praia", "2026-09-06T21:00:00+02:00"),
            ("Braga", "Rio Ave", "2026-09-06T21:15:00+02:00"),
            ("Vitoria SC", "Moreirense", "2026-09-06T21:30:00+02:00"),
            ("Arouca", "Boavista", "2026-09-06T21:45:00+02:00"),
    ]):
        odds = 1.30 + i * 0.02
        source = (pt.SCOUTINGSTATS_ODDS_SOURCE if i < 2 else pt.BZZOIRO_ODDS_SOURCE)
        board = [{"source": pt.BZZOIRO_ODDS_SOURCE, "bookmaker": "BookOne",
                  "odds": odds - 0.01, "captured_at": "2026-09-06T08:00:00Z",
                  "league": "x", "kickoff": ko, "market": "1x2",
                  "selection": "home", "home": home, "away": away, "chosen": True}]
        rows.append({"date": "2026-09-06", "home": home, "away": away,
                     "kickoff": ko, "league": "Portugal,Primeira Liga",
                     "bucket": "CERTIFIED_CLEAN", "market": "1x2", "pick": "home",
                     "avg_p": 70.0 - i, "odds": odds, "quarantine": "none",
                     "edge_rule": "ml-consensus", "odds_source": source,
                     "price_evidence": "BZZOIRO_PRIMARY", "price_board": board})
    return rows


def test_every_printed_leg_is_logged_append_only_with_its_board(tmp_path, monkeypatch):
    monkeypatch.setattr(at, "datetime", _NoonClock)
    (at.LOCALDATA / "picks_today.json").write_text(
        json.dumps(_slate_rows_with_boards()))
    st = at.fresh_state()
    args = SimpleNamespace(date="2026-09-06", force=True)
    assert at.cmd_today(args, st) == 0
    log = at.LOCALDATA / "price_board_2026-09.jsonl"
    assert log.exists()
    lines = [json.loads(x) for x in log.read_text().splitlines()]
    assert len(lines) == 6                       # six printed legs
    assert len({ln["match"] for ln in lines}) == 6
    assert all(ln["date"] == "2026-09-06" and ln["engine_odds"] for ln in lines)
    assert all(ln["price_board"] for ln in lines)
    # engine odds/source appear next to the board (no archive needed later)
    ss_lines = [ln for ln in lines if ln["odds_source"] == pt.SCOUTINGSTATS_ODDS_SOURCE]
    assert len(ss_lines) == 2 and all(ln["price_board"] for ln in ss_lines)
    # a second run appends, never overwrites
    assert at.cmd_today(args, st) == 0
    lines2 = [json.loads(x) for x in log.read_text().splitlines()]
    assert len(lines2) == 12
    txt = (at.LOCALDATA / "auto_tickets_2026-09-06.txt").read_text()
    assert "PRICE BOARD (automatic capture, Task F): build-time board persisted for 6 of 6 printed legs" in txt
    assert "expected coverage on the next slate: 100%" in txt


def test_coverage_line_reports_zero_when_slate_has_no_boards(tmp_path, monkeypatch):
    monkeypatch.setattr(at, "datetime", _NoonClock)
    rows = _slate_rows_with_boards()
    for r in rows:
        r.pop("price_board", None)
    (at.LOCALDATA / "picks_today.json").write_text(json.dumps(rows))
    st = at.fresh_state()
    args = SimpleNamespace(date="2026-09-06", force=True)
    assert at.cmd_today(args, st) == 0
    txt = (at.LOCALDATA / "auto_tickets_2026-09-06.txt").read_text()
    assert "persisted for 0 of 6 printed legs" in txt

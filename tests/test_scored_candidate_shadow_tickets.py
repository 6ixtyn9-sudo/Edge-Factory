"""Scored-candidate shadow ledger — ticket-builder integration contracts.

Pins the two absolute requirements against the REAL cmd_today path:

* every scored slate candidate is persisted before selection and carries a
  final selected/rejected status after selection (with real, derivable
  rejection reasons);
* the ledger is pure observability: ticket output, selected legs, stakes,
  state and the printed card are byte-identical with the shadow ledger
  enabled, disabled, and even when every ledger write crashes.
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
from edgefactory import scored_candidate_shadow as scs  # noqa: E402

DAY = "2026-09-06"


@pytest.fixture(autouse=True)
def _sandbox_state(tmp_path, monkeypatch):
    monkeypatch.setattr(at, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(at, "BUCKET_PNL_FILE",
                        tmp_path / "auto_tickets_bucket_pnl.json")


class _NoonClock(at.datetime):
    @classmethod
    def now(cls, tz=None):
        return at.datetime(2026, 9, 6, 12, 0, tzinfo=tz or at.TZ)


def _slate_rows():
    """6 playable legs + 2 rows the live gates reject for distinct reasons."""
    rows = []
    for i, (home, away, ko) in enumerate([
            ("Sporting CP", "Portimonense", "2026-09-06T20:30:00+02:00"),
            ("Benfica", "Gil Vicente", "2026-09-06T20:45:00+02:00"),
            ("Porto", "Estoril Praia", "2026-09-06T21:00:00+02:00"),
            ("Braga", "Rio Ave", "2026-09-06T21:15:00+02:00"),
            ("Vitoria SC", "Moreirense", "2026-09-06T21:30:00+02:00"),
            ("Arouca", "Boavista", "2026-09-06T21:45:00+02:00"),
    ]):
        rows.append({"date": DAY, "home": home, "away": away,
                     "kickoff": ko, "league": "Portugal,Primeira Liga",
                     "bucket": "CERTIFIED_CLEAN", "market": "1x2",
                     "pick": "home", "avg_p": 70.0 - i,
                     "odds": 1.30 + i * 0.02, "quarantine": "none",
                     "edge_rule": "ml-consensus",
                     "odds_source": "bzzoiro_odds"})
    rows.append({"date": DAY, "home": "Famalicao", "away": "Casa Pia",
                 "kickoff": "2026-09-06T22:00:00+02:00",
                 "league": "Portugal,Primeira Liga",
                 "bucket": "CERTIFIED_CLEAN", "market": "1x2", "pick": "home",
                 "avg_p": 61.0, "odds": 1.05, "quarantine": "none",
                 "edge_rule": "ml-consensus", "odds_source": "bzzoiro_odds"})
    rows.append({"date": DAY, "home": "Estrela", "away": "Farense",
                 "kickoff": "2026-09-06T22:15:00+02:00",
                 "league": "Portugal,Primeira Liga",
                 "bucket": "CERTIFIED_CLEAN", "market": "1x2", "pick": "home",
                 "avg_p": 60.0, "odds": 1.50, "quarantine": "none",
                 "edge_rule": "ml-consensus",
                 "odds_source": "scoutingstats_odds"})
    return rows


def _run_today(monkeypatch, *, force=True):
    monkeypatch.setattr(at, "datetime", _NoonClock)
    (at.LOCALDATA / "picks_today.json").write_text(json.dumps(_slate_rows()))
    st = at.fresh_state()
    st["bank"] = 100.0
    args = SimpleNamespace(date=DAY, force=force)
    assert at.cmd_today(args, st) == 0
    return st


def _events():
    return scs.read_ledger(DAY, at.LOCALDATA)


# ------------------------------------------- every candidate is persisted --
def test_cmd_today_persists_every_scored_candidate_with_final_status(monkeypatch):
    st = _run_today(monkeypatch)
    events = _events()
    scored = [e for e in events if e["event_type"] == "scored_candidate"]
    statuses = [e for e in events if e["event_type"] == "candidate_status"]
    assert len(scored) == 8                      # all slate rows, not just legs
    assert len(statuses) == 8
    by_fixture = {e["fixture"]: e for e in statuses_join(scored, statuses)}
    ticket_legs = [e for e in by_fixture.values() if e["selected_on_ticket"]]
    assert len(ticket_legs) == at.MAX_ACCAS * at.LEGS_PER_ACCA
    # the real selected legs on the slip are exactly the ledger's ticket legs
    slip = next(s for s in st["open_slips"] if s["date"] == DAY)
    slip_matches = {leg["match"] for acca in slip["accas"]
                    for leg in acca["legs"]}
    assert {e["fixture"] for e in ticket_legs} == slip_matches
    # stake attribution matches the printed card
    acca_stakes = {a["stake_pct"] for a in slip["accas"]}
    assert {e["stake_pct_of_capital"] for e in ticket_legs} <= acca_stakes
    # the two gate-rejected rows carry their REAL derived reasons
    assert by_fixture["Famalicao vs Casa Pia"]["rejection_reasons"][0][
        "code"] == "min_odds_floor"
    assert by_fixture["Estrela vs Farense"]["rejection_reasons"][0][
        "code"] == "price_source_not_execution_eligible"
    # playable-but-not-selected legs carry the ladder's terminal rule
    not_selected = [e for e in by_fixture.values()
                    if not e["selected_on_ticket"]
                    and e["rejection_reasons"]
                    and e["rejection_reasons"][0]["code"]
                    == "stake_ladder_not_selected"]
    assert len(not_selected) == 2                # 6 playable - 4 ticketed


def statuses_join(scored, statuses):
    fixture_by_cid = {e["candidate_id"]: e["fixture"] for e in scored}
    out = []
    for s in statuses:
        merged = dict(s)
        merged["fixture"] = fixture_by_cid.get(s["candidate_id"])
        out.append(merged)
    return out


def test_ledger_reconciles_with_real_plan_counts(monkeypatch):
    st = _run_today(monkeypatch)
    report = scs.build_report(DAY, root=at.LOCALDATA, settled={})
    slip = next(s for s in st["open_slips"] if s["date"] == DAY)
    real_legs = sum(len(a["legs"]) for a in slip["accas"])
    assert report["counts"]["total_scored"] == 8
    assert report["counts"]["ticketed_legs"] == real_legs
    assert report["reconciliation"]["shadow_scored"] == 8
    assert report["snapshot_used"] == "draft"    # force run never freezes
    assert report["counts"]["pending"] == 8      # nothing settled -> no losses


# ---------------------------------------------- no betting behavior change --
def _public_outputs(tmp_path):
    slip = tmp_path / f"auto_tickets_{DAY}.txt"
    state = tmp_path / "state.json"
    return {
        "slip": slip.read_text() if slip.exists() else None,
        "state": json.loads(state.read_text()) if state.exists() else None,
    }


def test_identical_ticket_output_with_shadow_on_off_and_crashing(
        tmp_path, monkeypatch, capsys):
    runs = {}
    for mode in ("on", "off", "crash"):
        workdir = tmp_path / mode
        workdir.mkdir()
        monkeypatch.setattr(at, "STATE_FILE", workdir / "state.json")
        monkeypatch.setattr(at, "LOCALDATA", workdir)
        monkeypatch.setattr(at, "BUCKET_PNL_FILE",
                            workdir / "auto_tickets_bucket_pnl.json")
        if mode == "off":
            monkeypatch.setenv("EDGE_FACTORY_SCORED_SHADOW", "0")
        else:
            monkeypatch.delenv("EDGE_FACTORY_SCORED_SHADOW", raising=False)
        if mode == "crash":
            def _boom(*a, **k):
                raise OSError("ledger disk is gone")
            monkeypatch.setattr(scs, "_append_events", _boom)
        else:
            monkeypatch.setattr(scs, "_append_events",
                                scs.__dict__["_append_events"])
        st = _run_today(monkeypatch)
        out = capsys.readouterr().out
        runs[mode] = {"stdout": out, "state": st,
                      **_public_outputs(workdir),
                      "ledger_exists": scs.ledger_path(DAY, workdir).exists()}
    assert runs["on"]["stdout"] == runs["off"]["stdout"] == runs["crash"]["stdout"]
    assert runs["on"]["slip"] == runs["off"]["slip"] == runs["crash"]["slip"]
    assert runs["on"]["state"] == runs["off"]["state"] == runs["crash"]["state"]
    assert runs["on"]["ledger_exists"] is True
    assert runs["off"]["ledger_exists"] is False
    assert runs["crash"]["ledger_exists"] is False


def test_audit_failure_is_reported_separately_not_silently(tmp_path, monkeypatch, capsys):
    def _boom(*a, **k):
        raise OSError("ledger disk is gone")
    monkeypatch.setattr(scs, "_append_events", _boom)
    _run_today(monkeypatch)
    err = capsys.readouterr().err
    assert "scored-candidate shadow" in err
    assert "audit-only" in err


# ------------------------------------------------ frozen reprint statuses --
def test_frozen_rerun_records_frozen_statuses_and_report_uses_them(monkeypatch):
    class _FreezeClock(at.datetime):
        @classmethod
        def now(cls, tz=None):
            return at.datetime(2026, 9, 6, 9, 30, tzinfo=tz or at.TZ)

    monkeypatch.setattr(at, "datetime", _FreezeClock)
    (at.LOCALDATA / "picks_today.json").write_text(json.dumps(_slate_rows()))
    st = at.fresh_state()
    st["bank"] = 100.0
    args = SimpleNamespace(date=DAY, force=False)
    assert at.cmd_today(args, st) == 0           # builds AND freezes (>=09:00)
    assert at.is_frozen(st, DAY)
    assert at.cmd_today(args, st) == 0           # frozen reprint path
    report = scs.build_report(DAY, root=at.LOCALDATA, settled={})
    assert report["snapshot_used"] == "frozen"
    assert report["counts"]["ticketed_legs"] == at.MAX_ACCAS * at.LEGS_PER_ACCA
    # reprint appended a second frozen run; dedupe still counts 8 once
    assert report["counts"]["total_scored"] == 8

import json
from pathlib import Path
from edgefactory.sources import boggio


def payload():
    return {"data":[{"id":1,"home_team":"A","away_team":"B","start_date":"2026-10-03T12:00:00+00:00","last_update_at":"2026-10-03T00:00:00+00:00","prediction":"1","probabilities":{"1":0.6},"odds":{"1":1.8},"market":"classic"}]}

def test_parse_keeps_publication_and_capture_timestamps():
    rows, shaped=boggio.parse_predictions(payload(),day="2026-10-03")
    assert shaped and len(rows)==1
    assert rows[0]["published_at"].startswith("2026-10-03")
    assert rows[0]["captured_at"]
    assert "12h" in rows[0]["lookahead_note"]

def test_junk_fails_closed():
    assert boggio.parse_predictions({"unexpected":1},day="2026-10-03")==([],False)

def test_missing_key_is_inert(monkeypatch,tmp_path):
    monkeypatch.delenv("RAPIDAPI_KEY",raising=False); monkeypatch.setattr(boggio,"LOCALDATA",tmp_path)
    rows,stats=boggio.capture_day("2026-10-03")
    assert rows==[] and stats["status"]=="not_run"
    assert "RAPIDAPI_KEY" in stats["blocker"]

def test_cache_first(monkeypatch,tmp_path):
    monkeypatch.setenv("RAPIDAPI_KEY","boggio-secret"); monkeypatch.setattr(boggio,"LOCALDATA",tmp_path)
    path=boggio.persist_shadow("2026-10-03",[{"home":"A"}],{"status":"ok"},localdata=tmp_path)
    monkeypatch.setattr(boggio,"get_json",lambda *a,**k: (_ for _ in ()).throw(AssertionError("refetched")))
    rows,stats=boggio.capture_day("2026-10-03")
    assert stats["status"]=="cache_only" and rows==[{"home":"A"}]
    assert "boggio-secret" not in json.dumps(boggio.diagnostics())


# --- average-bookmaker price donor promotion (operator, 2026-10-03) ------


def test_rows_carry_an_average_book_price_with_truthful_labels():
    rows, _shaped = boggio.parse_predictions(payload(), day="2026-10-03")
    row = rows[0]
    assert row["odds"] == 1.8
    assert row["odds_kind"] == "provider_average"
    assert row["provider_role"] == "average_bookmaker_price_donor"
    assert row["bookmaker"] == "average_bookie_aggregate"
    assert row["price_independence_family"] == "boggio_average"


def test_boggio_is_never_a_named_bookmaker():
    rows, _ = boggio.parse_predictions(payload(), day="2026-10-03")
    # An average across books must not masquerade as a book that took a bet.
    assert rows[0]["named_bookmaker"] is False


def test_price_push_eligibility_follows_the_explicit_config(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR", "0")
    off, _ = boggio.parse_predictions(payload(), day="2026-10-03")
    assert off[0]["price_push_eligible"] is False
    monkeypatch.setenv("EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR", "1")
    on, _ = boggio.parse_predictions(payload(), day="2026-10-03")
    assert on[0]["price_push_eligible"] is True


def test_future_publication_stamp_loses_price_eligibility(monkeypatch):
    data = payload()
    data["data"][0]["last_update_at"] = "2099-01-01T00:00:00+00:00"
    rows, _ = boggio.parse_predictions(data, day="2026-10-03")
    assert rows[0]["timestamp_suspect"] is True
    assert rows[0]["price_push_eligible"] is False
    # The row stays visible: the safeguard withholds the price, not the evidence.
    assert rows[0]["published_at"] == "2099-01-01T00:00:00+00:00"


def test_unquoted_selection_yields_no_price_rather_than_a_guess():
    data = payload()
    data["data"][0]["odds"] = {"2": 4.0}
    rows, _ = boggio.parse_predictions(data, day="2026-10-03")
    assert rows[0]["odds"] is None
    assert rows[0]["price_push_eligible"] is False

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

from __future__ import annotations

from types import SimpleNamespace

from scripts import refresh_result_sources as refresh


def test_merge_final_score_preserves_pick_time_predictions():
    existing = {
        "date": "2026-08-04",
        "home": "Carabobo FC",
        "away": "Trujillanos FC",
        "p1": "0.66",
        "px": "0.21",
        "p2": "0.13",
        "hs": "",
        "gs": "",
    }
    fresh = {
        "date": "2026-08-04",
        "home": "Carabobo FC",
        "away": "Trujillanos FC",
        "p1": None,
        "px": None,
        "p2": None,
        "hs": 2,
        "gs": 0,
        "status": "FT",
    }

    merged, changed = refresh.merge_final_score(existing, fresh)

    assert changed is True
    assert (merged["p1"], merged["px"], merged["p2"]) == ("0.66", "0.21", "0.13")
    assert (merged["hs"], merged["gs"], merged["status"]) == ("2", "0", "FT")


def test_refresh_source_writes_only_settled_score_fields(tmp_path, monkeypatch):
    day = "2026-08-04"
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    path = localdata / "forebet_2026-08.csv.gz"
    baseline = {
        "date": day,
        "home": "Carabobo FC",
        "away": "Trujillanos FC",
        "p1": "0.66",
        "px": "0.21",
        "p2": "0.13",
        "hs": "",
        "gs": "",
        "status": "Pre-Game",
    }
    refresh._write_rows(
        path,
        list(baseline),
        {refresh.row_key(baseline): baseline},
    )

    calls = []

    def fetch_forebet(requested_day, markets=None):
        calls.append((requested_day, markets))
        return [
            {
                "date": day,
                "home": "Carabobo FC",
                "away": "Trujillanos FC",
                "p1": None,
                "px": None,
                "p2": None,
                "hs": 2,
                "gs": 0,
                "status": "FT",
            },
            {
                "date": day,
                "home": "No Score",
                "away": "Yet",
                "hs": None,
                "gs": None,
            },
        ]

    fake = SimpleNamespace(COLUMNS=list(baseline), fetch_day=fetch_forebet)
    monkeypatch.setattr(refresh.importlib, "import_module", lambda _: fake)

    receipt = refresh.refresh_source("forebet", day, localdata=localdata)
    _, rows = refresh.read_rows(path)
    row = rows[refresh.row_key(baseline)]

    assert receipt == {
        "source": "forebet", "status": "OK", "raw": 2,
        "scored": 1, "terminal_status": 0, "new": 0, "updated": 1,
    }
    assert calls == [(day, ("1x2",))]
    assert (row["p1"], row["px"], row["p2"]) == ("0.66", "0.21", "0.13")
    assert (row["hs"], row["gs"], row["status"]) == ("2", "0", "FT")


def test_refresh_source_reports_failure_without_raising(tmp_path, monkeypatch):
    monkeypatch.setattr(
        refresh.importlib,
        "import_module",
        lambda _: (_ for _ in ()).throw(RuntimeError("network unavailable")),
    )

    receipt = refresh.refresh_source("forebet", "2026-08-04", localdata=tmp_path)

    assert receipt["status"] == "ERROR:RuntimeError"
    assert receipt["raw"] == receipt["scored"] == receipt["terminal_status"] == receipt["new"] == receipt["updated"] == 0


def test_terminal_postponement_status_is_persisted_but_scheduled_is_not():
    existing = {
        "date": "2026-07-26", "home": "Super Nova", "away": "Riga",
        "p1": "0.25", "px": "0.12", "p2": "0.63", "hs": "", "gs": "", "status": "scheduled",
    }
    postponed = dict(existing, p1=None, px=None, p2=None, status="Postp.")
    merged, changed = refresh.merge_terminal_update(existing, postponed)

    assert changed is True
    assert (merged["p1"], merged["px"], merged["p2"]) == ("0.25", "0.12", "0.63")
    assert merged["status"] == "Postp."
    assert refresh.has_terminal_event_status(postponed) is True
    assert refresh.has_terminal_event_status(dict(existing, status="scheduled")) is False


def test_refresh_source_persists_positive_terminal_status(tmp_path, monkeypatch):
    day = "2026-07-26"
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    path = localdata / "forebet_2026-07.csv.gz"
    baseline = {
        "date": day, "home": "Super Nova", "away": "Riga",
        "p1": "0.25", "px": "0.12", "p2": "0.63", "hs": "", "gs": "", "status": "scheduled",
    }
    refresh._write_rows(path, list(baseline), {refresh.row_key(baseline): baseline})
    fake = SimpleNamespace(
        COLUMNS=list(baseline),
        fetch_day=lambda _day, markets=None: [{
            "date": day, "home": "Super Nova", "away": "Riga",
            "p1": None, "px": None, "p2": None, "hs": None, "gs": None, "status": "Postp.",
        }],
    )
    monkeypatch.setattr(refresh.importlib, "import_module", lambda _: fake)

    receipt = refresh.refresh_source("forebet", day, localdata=localdata)
    _, rows = refresh.read_rows(path)
    row = rows[refresh.row_key(baseline)]

    assert receipt["scored"] == 0
    assert receipt["terminal_status"] == 1
    assert receipt["updated"] == 1
    assert row["status"] == "Postp."
    assert (row["p1"], row["px"], row["p2"]) == ("0.25", "0.12", "0.63")

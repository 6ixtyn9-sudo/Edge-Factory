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

    fake = SimpleNamespace(
        COLUMNS=list(baseline),
        fetch_day=lambda _: [
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
        ],
    )
    monkeypatch.setattr(refresh.importlib, "import_module", lambda _: fake)

    receipt = refresh.refresh_source("forebet", day, localdata=localdata)
    _, rows = refresh.read_rows(path)
    row = rows[refresh.row_key(baseline)]

    assert receipt == {
        "source": "forebet", "status": "OK", "raw": 2,
        "settled": 1, "new": 0, "updated": 1,
    }
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
    assert receipt["raw"] == receipt["settled"] == receipt["new"] == receipt["updated"] == 0

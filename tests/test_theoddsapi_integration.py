"""The Odds API cached-board integration is time-safe and exact-join only."""
from __future__ import annotations

import csv
import gzip
from datetime import datetime, timezone

import scripts.picks_today as pt


DAY = "2026-10-03"


def _write_monthly_board(tmp_path, rows: list[dict], *, prefix: str = "theoddsapi_odds") -> None:
    path = tmp_path / f"{prefix}_2026-10.csv.gz"
    fields = [
        "source", "source_type", "sport", "date", "kickoff", "league",
        "home", "away", "market", "selection", "odds", "bookmaker", "captured_at",
    ]
    with gzip.open(path, "wt", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _row(**overrides) -> dict:
    row = {
        "source": "theoddsapi", "source_type": "odds", "sport": "soccer",
        "date": DAY, "kickoff": f"{DAY}T18:00:00+00:00", "league": "Example League",
        "home": "Albacete", "away": "Eibar", "market": "1x2", "selection": "away",
        "odds": "2.14", "bookmaker": "Betfair",
        "captured_at": f"{DAY}T07:00:00+00:00",
    }
    row.update(overrides)
    return row


def _pick(home: str, away: str, selection: str) -> dict:
    return {"date": DAY, "home": home, "away": away, "market": "1x2", "pick": selection}


def test_cached_theodds_named_book_is_selectable_and_uses_narrow_aliases(tmp_path, monkeypatch):
    _write_monthly_board(tmp_path, [
        _row(away="SD Eibar"),
        _row(home="Grimsby Town", away="Shrewsbury Town", selection="home", odds="1.91"),
    ])
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    stats: dict = {}
    bundle = pt.theoddsapi_odds_bundle(
        DAY, not_after=datetime(2026, 10, 3, 8, tzinfo=timezone.utc), stats=stats,
    )

    assert stats["raw_rows"] == stats["usable_rows"] == 2
    for pick in (_pick("Albacete", "Eibar", "away"),
                 _pick("Grimsby", "Shrewsbury", "home")):
        row, method, source = pt.select_price_source(pick, [bundle])
        assert source == "theoddsapi"
        assert method == "exact"
        assert row["named_bookmaker"] is True
        assert row["bookmaker"] == "Betfair"

    priced = [_pick("Albacete", "Eibar", "away")]
    pt.enrich_with_live_odds(priced, {}, donor_bundles=[bundle])
    assert priced[0]["price_evidence"] == pt.PRICE_EVIDENCE_NAMED_BOOKMAKER
    assert priced[0]["price_disclosure"] == "TheOddsAPI named-book price (Betfair)"


def test_cached_theodds_kickoff_date_overrides_capture_date(tmp_path, monkeypatch):
    # Raw The Odds API vocabulary: h2h plus the outcome's team name.
    _write_monthly_board(tmp_path, [_row(
        date="2026-10-04", market="h2h", selection="Albacete",
        kickoff="2026-10-03T23:30:00-02:00",
    )])
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    stats: dict = {}
    bundle = pt.theoddsapi_odds_bundle(
        DAY, not_after=datetime(2026, 10, 3, 8, tzinfo=timezone.utc), stats=stats,
    )

    assert stats["raw_rows"] == stats["usable_rows"] == 1
    row, method, source = pt.select_price_source(
        _pick("Albacete", "Eibar", "home"), [bundle]
    )
    assert (source, method, row["date"]) == ("theoddsapi", "exact", DAY)


def test_cached_theodds_price_cannot_time_travel_or_lose_timestamp(tmp_path, monkeypatch):
    _write_monthly_board(tmp_path, [
        _row(captured_at=f"{DAY}T09:00:01+00:00"),
        _row(captured_at="", bookmaker="Pinnacle"),
        _row(captured_at="2026-10-02T06:00:00+00:00", bookmaker="Matchbook"),
    ])
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    stats: dict = {}
    bundle = pt.theoddsapi_odds_bundle(
        DAY, not_after=datetime(2026, 10, 3, 9, tzinfo=timezone.utc), stats=stats,
    )

    assert stats["raw_rows"] == 3
    assert stats["after_build_rows"] == 1
    assert stats["invalid_timestamp_rows"] == 1
    assert stats["stale_rows"] == 1
    assert stats["usable_rows"] == 0
    assert pt.select_price_source(_pick("Albacete", "Eibar", "away"), [bundle]) == (None, None, None)


def test_cached_oddspapi_board_uses_its_raw_source_alias_and_registry_provider(tmp_path, monkeypatch):
    _write_monthly_board(
        tmp_path,
        [_row(source="oddspapi", bookmaker="Pinnacle", odds="2.22")],
        prefix="oddspapi_odds",
    )
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    stats: dict = {}
    bundle = pt.oddspapi_odds_bundle(
        DAY, not_after=datetime(2026, 10, 3, 8, tzinfo=timezone.utc), stats=stats,
    )
    row, method, source = pt.select_price_source(_pick("Albacete", "SD Eibar", "away"), [bundle])
    assert stats["status"] == "cache_only"
    assert stats["raw_rows"] == stats["usable_rows"] == 1
    assert (source, method, row["bookmaker"], row["named_bookmaker"]) == (
        "oddspapi_odds", "exact", "Pinnacle", True,
    )


def test_cached_betexplorer_snapshot_joins_as_the_highest_contributor(tmp_path, monkeypatch):
    payload = {
        "schema": 1,
        "date": DAY,
        "fixtures": {
            "fixture": {
                "cached_at": f"{DAY}T07:00:00+00:00",
                "rows": [_row(source="ignored", bookmaker="betexplorer_best", odds="2.35")],
            },
        },
    }
    (tmp_path / f"betexplorer_odds_cache_{DAY}.json").write_text(__import__("json").dumps(payload))
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    stats: dict = {}
    bundle = pt.betexplorer_cached_odds_bundle(
        DAY, not_after=datetime(2026, 10, 3, 8, tzinfo=timezone.utc), stats=stats,
    )
    row, method, source = pt.select_price_source(_pick("Albacete", "SD Eibar", "away"), [bundle])
    assert stats["status"] == "cache_only"
    assert stats["raw_rows"] == stats["usable_rows"] == 1
    assert (source, method, row["bookmaker"]) == ("betexplorer_odds", "exact", "betexplorer_best")

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "export_settled_results",
    Path(__file__).resolve().parents[1] / "scripts" / "export_settled_results.py",
)
export_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export_mod)

_DDL = "(date VARCHAR, home VARCHAR, away VARCHAR, hs INTEGER, gs INTEGER, outcome VARCHAR)"


def _con():
    import duckdb

    con = duckdb.connect(":memory:")
    con.execute(f"CREATE TABLE forebet_settled {_DDL}")
    con.execute(f"CREATE TABLE zulubet_settled {_DDL}")
    return con


def test_priority_dedup_keeps_highest_priority_source_row():
    con = _con()
    con.execute("INSERT INTO forebet_settled VALUES ('2026-08-02','South Hobart','Ulverstone',2,0,'home')")
    con.execute("INSERT INTO zulubet_settled VALUES ('2026-08-02','South Hobart','Ulverstone',9,9,'away')")
    rows = export_mod.build_overlay_rows(con, "2026-08-01")
    assert len(rows) == 1
    assert rows[0]["src"] == "forebet_settled"
    assert rows[0]["hs"] == 2 and rows[0]["gs"] == 0


def test_rolling_window_excludes_old_rows():
    con = _con()
    con.execute("INSERT INTO forebet_settled VALUES ('2026-05-01','Alpha','Beta',1,0,'home')")
    con.execute("INSERT INTO forebet_settled VALUES ('2026-08-01','Gamma','Delta',0,0,'draw')")
    rows = export_mod.build_overlay_rows(con, "2026-06-01")
    assert [r["date"] for r in rows] == ["2026-08-01"]


def test_no_settled_views_exports_nothing():
    import duckdb

    con = duckdb.connect(":memory:")
    con.execute("CREATE TABLE something_else (x INTEGER)")
    assert export_mod.build_overlay_rows(con, "2026-01-01") == []


def test_self_test_passes():
    assert export_mod.self_test() == 0


def _row(date, home, away, hs=1, gs=0, outcome="home", src="forebet_settled"):
    return {"date": date, "home": home, "away": away, "hs": hs, "gs": gs,
            "outcome": outcome, "src": src}


def test_merge_carries_inbound_only_rows_forward():
    wh = [_row("2026-08-03", "Celtic", "Dundee")]
    inbound = [_row("2026-07-11", "South Hobart", "Ulverstone", hs=2)]
    rows, carried = export_mod.merge_overlay_rows(wh, inbound, "2026-06-01")
    assert len(rows) == 2 and carried == 1
    assert [r["date"] for r in rows] == ["2026-07-11", "2026-08-03"]


def test_merge_warehouse_wins_conflict_and_drops_stale_inbound():
    wh = [_row("2026-08-03", "Celtic", "Dundee", hs=1)]
    inbound = [
        _row("2026-08-03", "Celtic", "Dundee", hs=9, gs=9, outcome="away", src="zulubet_settled"),
        _row("2026-01-01", "Too", "Old", outcome="draw", src="overlay"),
    ]
    rows, carried = export_mod.merge_overlay_rows(wh, inbound, "2026-06-01")
    assert len(rows) == 1 and carried == 0 and rows[0]["hs"] == 1


def _disp(date, home, away, disposition="POSTPONED", src="source_status:forebet"):
    return {"date": date, "home": home, "away": away, "disposition": disposition, "src": src}


def test_build_overlay_dispositions_exports_only_terminal_status():
    import duckdb

    con = duckdb.connect(":memory:")
    con.execute("CREATE TABLE forebet (date VARCHAR, home VARCHAR, away VARCHAR, status VARCHAR)")
    con.execute("INSERT INTO forebet VALUES ('2026-08-08','Belshina','Dinamo Minsk','Postp.')")
    con.execute("INSERT INTO forebet VALUES ('2026-08-08','Live','Club','scheduled')")
    con.execute("INSERT INTO forebet VALUES ('2026-08-08','Blank','Score','')")
    con.execute("INSERT INTO forebet VALUES ('2026-05-01','Too','Old','Postponed')")
    rows = export_mod.build_overlay_dispositions(con, "2026-07-01")
    assert len(rows) == 1
    assert rows[0]["home"] == "Belshina"
    assert rows[0]["disposition"] == "POSTPONED"
    assert rows[0]["src"] == "source_status:forebet"


def test_inbound_dispositions_drop_nonterminal_and_merge_warehouse_wins():
    wh = [_disp("2026-08-08", "Belshina", "Dinamo Minsk", "POSTPONED")]
    inbound = [
        _disp("2026-08-08", "Belshina", "Dinamo Minsk", "CANCELLED", src="overlay"),
        _disp("2026-08-11", "Junior", "Pereira", "POSTPONED", src="overlay"),
        _disp("2026-01-01", "Too", "Old", "POSTPONED", src="overlay"),
        {"date": "2026-08-08", "home": "Not", "away": "Terminal", "disposition": "SCHEDULED", "src": "overlay"},
    ]
    parsed = []
    # reuse merge after filtering the way load_inbound_dispositions would
    from pathlib import Path
    import json
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settled_results.json"
        path.write_text(json.dumps({"schema": 1, "rows": [], "dispositions": inbound}))
        parsed = export_mod.load_inbound_dispositions(path)
    assert [r["home"] for r in parsed] == ["Belshina", "Junior", "Too"]
    rows, carried = export_mod.merge_overlay_dispositions(wh, parsed, "2026-07-01")
    by_home = {r["home"]: r for r in rows}
    assert by_home["Belshina"]["disposition"] == "POSTPONED"
    assert by_home["Junior"]["src"] == "overlay"
    assert "Too" not in by_home
    assert carried == 1

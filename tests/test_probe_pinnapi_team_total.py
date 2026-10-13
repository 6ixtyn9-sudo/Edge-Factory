"""The pinnapi probe's team-total diagnostic: counts and value-whitelisted shapes only."""
import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parents[1] / "scripts" / "probe_pinnapi.py"
_spec = importlib.util.spec_from_file_location("probe_pinnapi", _PATH)
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)


def test_team_total_sample_counts_and_never_echoes_strings():
    data = {"events": [
        {"starts": "2026-10-13T19:00", "periods": {"num_0": {
            "team_total": {"home": {"over": {"points": 1.5, "price": 1.9}}}, "team_totals": {}}}},
        {"starts": "2026-10-14T19:00", "periods": {"num_0": {
            "team_totals": [{"name": "free text provider", "line": 2.5, "over": 1.8}]}}},
        {"starts": "2026-10-13T20:00", "periods": {"num_0": {"money_line": {}}}},
    ]}
    out = probe._team_total_sample(data, {"2026-10-13"})
    assert out["events_with_num_0"] == 3
    assert out["team_total_populated"] == 1
    assert out["team_total_populated_on_slate_date"] == 1
    assert out["team_totals_populated"] == 1
    assert out.get("team_totals_populated_on_slate_date", 0) == 0
    assert out["shapes"]["team_total"] == {"home": {"over": {"points": 1.5, "price": 1.9}}}
    assert out["shapes"]["team_totals"]["first"]["name"] == "str"
    assert "free text provider" not in str(out)

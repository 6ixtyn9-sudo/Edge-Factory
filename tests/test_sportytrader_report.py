from __future__ import annotations

import json
from pathlib import Path

from importlib.util import module_from_spec, spec_from_file_location

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("report_sportytrader_7pct", ROOT / "scripts" / "report_sportytrader_7pct.py")
reporter = module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(reporter)


def test_report_measures_named_book_within_seven_percent(tmp_path):
    day = "2026-10-02"
    pick = {
        "date": day, "home": "Alpha United", "away": "Beta City",
        "market": "1x2", "pick": "home", "odds": 1.50,
        "price_push_eligible": True, "bucket": "CLEAN",
    }
    (tmp_path / f"picks_morning_{day}.json").write_text(json.dumps([pick]))
    shadow = {
        "rows": [{
            "date": day, "home": "Alpha United", "away": "Beta City",
            "market": "1x2", "selection": "home", "odds": 1.55,
            "bookmaker": "Bet365", "captured_at": "2026-10-02T08:00:00Z",
        }]
    }
    (tmp_path / f"sportytrader_odds_shadow_{day}.json").write_text(json.dumps(shadow))
    result = reporter.build_report(tmp_path, 1)
    assert result["test_7pct"] == {
        "eligible": 1, "gained": 1, "rate": 1.0, "max_deviation": 0.07,
    }


def test_report_does_not_count_quote_outside_seven_percent(tmp_path):
    day = "2026-10-02"
    (tmp_path / f"picks_morning_{day}.json").write_text(json.dumps([{
        "date": day, "home": "Alpha", "away": "Beta", "market": "1x2",
        "pick": "home", "odds": 1.50, "price_push_eligible": True,
    }]))
    (tmp_path / f"sportytrader_odds_shadow_{day}.json").write_text(json.dumps({"rows": [{
        "date": day, "home": "Alpha", "away": "Beta", "market": "1x2",
        "selection": "home", "odds": 1.62, "bookmaker": "Book", "captured_at": "now",
    }]}))
    result = reporter.build_report(tmp_path, 1)
    assert result["money_relevant"] == 1
    assert result["gained_sportytrader_within_7pct"] == 0

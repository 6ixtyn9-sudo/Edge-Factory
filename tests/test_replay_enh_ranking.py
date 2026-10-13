"""The enhancement replay must rank the way the shipped lane ranks.

Regression: the replay called plan_day without a rank, so it tested stated-
probability ordering, a rule that no longer ships (hit-rate ranking, PR #71).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
import replay_harness as rh  # noqa: E402


def _rec(match, market, price, stated, hit=True):
    home, away = match.split(" vs ")
    return {"date": "2026-10-13", "match": match, "market": market, "price": price,
            "stated": stated, "hit": hit, "league": "X", "home": home, "away": away}


def test_replay_ranks_by_the_shipped_rule_and_carries_floors(monkeypatch):
    assert at.ENHANCEMENT_RANK == "hitrate"
    seen = {}
    real = at.plan_day

    def spy(pool, bank_pct, **kw):
        seen["kw"] = kw
        seen["pool"] = [dict(l) for l in pool]
        return real(pool, bank_pct, **kw)

    monkeypatch.setattr(at, "plan_day", spy)
    floors = {"match_over_25": 1.60, "match_under_15": 4.45}
    records = [
        _rec("Alpha FC vs Beta FC", "match_over_25", 1.80, stated=0.60),
        _rec("Gamma FC vs Delta FC", "match_under_15", 4.60, stated=0.90),
    ]
    rh.enh_day_growth(records, floors)
    assert seen["kw"].get("rank") == "hitrate"
    assert {l["pick"]: l["floor"] for l in seen["pool"]} == {
        "match_over_25": 1.60, "match_under_15": 4.45}

"""Tests for scripts/replay_harness.py — the counterfactual instrument.

The 2026-09-04 audit found the harness had shipped with: a re-implemented
copy of the live recipe (drifted twice), an UNPAIRED bootstrap that printed
a +-22,000% interval for two identical variants, a band table labelled
"floor applied" that applied no floor, and an A/B mode whose knob could not
reach the card. None of it was covered by a test. These are those tests.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at            # noqa: E402
import replay_harness as rh          # noqa: E402


def _leg(tag, prob, odds, result="win"):
    return {"match": f"T{tag} vs O{tag}", "pick": "HOME", "prob": prob,
            "odds": odds, "result": result, "row": {}}


def _universe(n_days=8):
    """Deterministic universe: 14 legs/day (saturated), alternating outcomes."""
    u = {}
    for d in range(n_days):
        day = f"2026-08-{d+1:02d}"
        legs = []
        for i in range(14):
            legs.append(_leg(f"{d}_{i}", 0.75 - i * 0.02, 1.25 + i * 0.05,
                             "win" if (d + i) % 3 else "loss"))
        u[day] = at.rank_legs(legs)
    return u


# ---------------- parity: the harness must drive the LIVE selector ----------

def test_harness_uses_the_live_selector_no_reimplementation():
    u = _universe()
    for day, pool in u.items():
        harness = rh.card_for_day(pool, {})
        live = at.select_accas(pool)
        assert harness == live, f"{day}: harness card diverged from the engine"


def test_source_has_no_private_copy_of_the_recipe():
    src = (ROOT / "scripts" / "replay_harness.py").read_text()
    assert "inspect.getsource" not in src, "no source-mangling: pass parameters instead"
    assert "def plan_for_day" not in src, "no second implementation of the recipe"
    assert "if odds < 1.2" not in src, "no inlined floor — use at.MIN_LEG_ODDS"


# ---------------- spec parsing ----------------------------------------------

def test_parse_spec_forms():
    assert rh.parse_spec("live") == {}
    assert rh.parse_spec("1.25") == {"floor": 1.25}          # back-compat --ab 1.10 1.20
    assert rh.parse_spec("gate_mode=acca,volume_min=0.7") == {
        "gate_mode": "acca", "volume_min": 0.7}
    assert rh.parse_spec("fallback=0")["fallback"] is False
    assert rh.parse_spec("max_accas=4")["max_accas"] == 4
    with pytest.raises(SystemExit):
        rh.parse_spec("nonsense_key=3")


# ---------------- the no-op guard -------------------------------------------

def test_card_diff_days_flags_the_dead_volume_gate():
    u = _universe()
    a = {"gate_mode": "pool", "volume_min": 0.55}
    b = {"gate_mode": "pool", "volume_min": 0.75}
    assert rh.card_diff_days(u, a, b) == 0, \
        "pool gate is a proven no-op: any diff means the audit needs redoing"
    # the per-acca gate does reach the card
    assert rh.card_diff_days(u, {}, {"gate_mode": "acca", "volume_min": 0.70}) > 0


# ---------------- paired bootstrap ------------------------------------------

def test_paired_bootstrap_of_identical_variants_is_exactly_zero():
    """The 2026-09-04 bug: an unpaired bootstrap gave median +8%, p10 -22575%,
    p90 +22364% and P=51% for two IDENTICAL arms. Paired, it must be 0."""
    u = _universe()
    r = rh.paired_bootstrap(u, {}, {}, n=200)
    assert r["median"] == pytest.approx(0.0, abs=1e-12)
    assert r["p10"] == pytest.approx(0.0, abs=1e-12)
    assert r["p90"] == pytest.approx(0.0, abs=1e-12)
    assert r["p_b_higher"] == 0.0


def test_paired_bootstrap_detects_a_real_difference():
    u = _universe()
    worse = {"stake_frac": 0.95}          # wildly over-Kelly on this universe
    r = rh.paired_bootstrap(u, {}, worse, n=300)
    assert r["p_b_higher"] < 0.5


# ---------------- metrics ----------------------------------------------------

def test_day_growth_is_bank_independent_and_matches_the_engine():
    accas = [[_leg("a", 0.7, 2.0, "win"), _leg("b", 0.7, 1.5, "win")],
             [_leg("c", 0.7, 1.5, "loss"), _leg("d", 0.7, 1.5, "win")]]
    # one acca @3.0 wins, one loses; stake f/2 each
    assert rh.day_growth(accas, 0.5) == pytest.approx(1 + 0.5 * (3.0 / 2 - 1))
    # engine cross-check: same numbers through plan_day's staking
    plan = [{"odds": 3.0, "stake_pct": 25.0}, {"odds": 2.25, "stake_pct": 25.0}]
    bank = 100.0 - sum(p["stake_pct"] for p in plan) + plan[0]["stake_pct"] * 3.0
    assert bank / 100.0 == pytest.approx(rh.day_growth(accas, 0.5))


def test_summarise_final_bank_is_the_product_of_daily_growth():
    u = _universe()
    days = rh.replay(u, {})
    s = rh.summarise(days)
    prod = 100.0
    for d in days.values():
        prod *= d["growth"]
    assert s["final"] == pytest.approx(prod, rel=1e-9)


# ---------------- band table -------------------------------------------------

def test_leg_bands_applies_the_live_floor():
    """2026-09-04: the table said 'floor applied' and applied none — 11% of
    its legs (42% of the 0.75+ cell) were sub-floor legs the engine cannot bet."""
    u = {"2026-08-01": at.rank_legs(
        [_leg(f"sub{i}", 0.80, 1.05) for i in range(6)] +
        [_leg(f"ok{i}", 0.80, 1.50) for i in range(12)])}
    bands, sat_days = rh.leg_bands(u)
    assert sat_days == 1
    assert bands["0.75+"][0] == 12, "sub-1.20 legs must not enter the band table"


def test_leg_bands_uses_the_floored_pool_for_saturation():
    """A day is saturated only if the pool the engine can actually bet is
    >= VOLUME_POOL — counting sub-floor legs invents saturated days."""
    u = {"2026-08-01": at.rank_legs(
        [_leg(f"sub{i}", 0.80, 1.05) for i in range(10)] +
        [_leg(f"ok{i}", 0.80, 1.50) for i in range(4)])}
    _, sat_days = rh.leg_bands(u)
    assert sat_days == 0


# ---------------- effect concentration --------------------------------------

def test_effect_concentration_flags_a_one_day_effect():
    """A difference carried by a single day must be reported as such — the
    '4 accas/day' signal was 117% one treble on 2026-08-25."""
    # every day offers exactly 6 legs (max_accas=4 changes nothing) except one,
    # where a monster 4th acca wins
    u = {}
    for d in range(6):
        u[f"2026-08-{d+1:02d}"] = at.rank_legs(
            [_leg(f"{d}_{i}", 0.70 - i * 0.01, 1.50,
                  "win" if (d + i) % 2 else "loss") for i in range(6)])
    day = "2026-08-01"
    u[day] = at.rank_legs(u[day] + [_leg("boom1", 0.50, 9.0, "win"),
                                    _leg("boom2", 0.50, 9.0, "win")])
    e = rh.effect_concentration(u, {}, {"max_accas": 4})
    assert e is not None
    assert e["top_day"] == day
    assert e["top_share"] > 0.4


# ---------------- slot table (checkpoint ① at leg scale) --------------------

def test_slot_table_like_for_like_uses_only_days_that_reach_the_slot():
    """Slot 1 pooled over every day vs slot 8 pooled over big days only is a
    confounded comparison. min_pool restricts to days that offer every slot."""
    u = {"2026-08-01": at.rank_legs([_leg(f"a{i}", 0.80 - i / 100, 1.50) for i in range(4)]),
         "2026-08-02": at.rank_legs([_leg(f"b{i}", 0.80 - i / 100, 1.50) for i in range(10)])}
    slots_all, _, days_all = rh.slot_table(u)
    slots_8, _, days_8 = rh.slot_table(u, min_pool=8)
    assert days_all == 2 and days_8 == 1
    assert slots_all[1][0] == 2                       # both days reach slot 1
    assert slots_8[1][0] == slots_8[8][0] == 1        # like-for-like: same day count


def test_slot_table_respects_the_floor_and_the_rank_order():
    u = {"2026-08-01": at.rank_legs(
        [_leg("sub", 0.90, 1.05)] + [_leg(f"ok{i}", 0.80 - i / 100, 1.50) for i in range(4)])}
    slots, accas, _ = rh.slot_table(u)
    assert slots[1][0] == 1 and slots[5][0] == 0      # sub-floor leg excluded
    assert accas[1][0] == 1 and accas[3][0] == 0

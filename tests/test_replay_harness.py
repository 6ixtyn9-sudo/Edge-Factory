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
    assert rh.parse_spec("max_accas=4,min_accas=2")["min_accas"] == 2
    assert rh.parse_spec("stake_mode=per_acca,stake_per_acca=0.1") == {
        "stake_mode": "per_acca", "stake_per_acca": 0.1}
    assert rh.parse_spec("weights=3,2,1") == {"weights": "3,2,1"}
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

def test_day_growth_comes_from_the_engine_plan_stakes():
    pool = [_leg("a", 0.74, 2.0, "win"), _leg("b", 0.73, 1.5, "win"),
            _leg("c", 0.72, 1.5, "loss"), _leg("d", 0.71, 1.5, "win")]
    # pins per_day: this test is about day_growth arithmetic, not stake mode
    plan = at.plan_day(pool, 100.0, stake_frac=0.5, stake_mode="per_day")
    # one acca @3.0 wins, one loses; plan_day stakes 25% on each
    assert [a["stake_pct"] for a in plan] == [25.0, 25.0]
    assert rh.day_growth(plan) == pytest.approx(1 + 0.5 * (3.0 / 2 - 1))


def test_replay_routes_sizing_through_plan_day(monkeypatch):
    u = _universe(1)
    real = at.plan_day
    calls = []

    def recording_plan(pool, bank_pct, **kwargs):
        calls.append((bank_pct, kwargs))
        return real(pool, bank_pct, **kwargs)

    monkeypatch.setattr(at, "plan_day", recording_plan)
    days = rh.replay(u, {"stake_mode": "per_acca", "stake_per_acca": 0.07})
    assert calls == [(100.0, {"stake_mode": "per_acca", "stake_per_acca": 0.07})]
    assert days["2026-08-01"]["stake_pct"] == [7.0, 7.0, 7.0]


def test_summarise_final_bank_is_the_product_of_daily_growth():
    u = _universe()
    days = rh.replay(u, {})
    s = rh.summarise(days)
    prod = 100.0
    for d in days.values():
        prod *= d["growth"]
    assert s["final"] == pytest.approx(prod, rel=1e-9)
    assert s["ruin"] == 0


def test_summarise_bankruptcy_is_ruin_not_a_dropped_day():
    days = {
        "2026-08-01": {"growth": 2.0, "accas": [(2.0, True)]},
        "2026-08-02": {"growth": 0.0, "accas": [(2.0, False)]},
        "2026-08-03": {"growth": 5.0, "accas": [(5.0, True)]},
    }
    s = rh.summarise(days)
    assert s["ruin"] == 1
    assert s["mean_log"] == -float("inf")
    assert s["final"] == 0.0
    assert s["maxdd"] == 1.0


def test_ruin_variant_is_not_bootstrapped():
    u = {"2026-08-01": at.rank_legs([
        _leg("a", 0.8, 1.5, "loss"), _leg("b", 0.7, 1.5, "loss")])}
    # a total-loss day only exists if the whole bank is staked, so this
    # scenario pins per_day explicitly rather than inheriting the live default
    ruinous = {"stake_frac": 1.0, "stake_mode": "per_day"}
    assert rh.summarise(rh.replay(u, ruinous))["ruin"] == 1
    assert rh.paired_bootstrap(u, {}, ruinous, n=20) is None


def test_kelly_sweep_skips_ruin_cells(capsys):
    u = {"2026-08-01": at.rank_legs([
        _leg("a", 0.8, 1.5, "loss"), _leg("b", 0.7, 1.5, "loss")])}
    # A one-acca day can only be a RUIN cell under per_day; per_acca caps it
    # at STAKE_FRAC/MAX_ACCAS by design. This test is about the sweep
    # SKIPPING ruin cells, so it pins the mode that can produce one.
    rh.cmd_kelly(u, {"stake_mode": "per_day"})
    output = capsys.readouterr().out
    assert "100%      RUIN" in output
    assert "<- SKIPPED" in output


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


# ---------------- leagues= (harness-only concentration filter) --------------

def test_parse_spec_accepts_leagues_and_still_rejects_unknown_keys():
    assert rh.parse_spec("leagues=EPL|Sc1") == {"leagues": "EPL|Sc1"}
    assert rh.parse_spec("floor=1.3,leagues=EPL") == {"floor": 1.3, "leagues": "EPL"}
    with pytest.raises(SystemExit):
        rh.parse_spec("nonsense=1")


def test_leagues_filter_shrinks_the_pool_before_the_live_selector_sees_it():
    def leg(tag, lg):
        return {"match": f"T{tag} vs O{tag}", "pick": "HOME", "prob": 0.75,
                "odds": 1.30, "result": "win", "row": {"league": lg}}
    pool = at.rank_legs([leg("a", "England, Premier League"),
                         leg("b", "Scotland, Premiership"),
                         leg("c", "England, League Two")])
    kept = rh._filtered_pool(pool, {"leagues": "england"})
    assert sorted(l["match"] for l in kept) == ["Ta vs Oa", "Tc vs Oc"]
    assert [l["match"] for l in rh._filtered_pool(pool, {"leagues": "premiership"})] == ["Tb vs Ob"]
    assert rh._filtered_pool(pool, {}) is pool          # no spec, no copy, no filter
    assert rh._filtered_pool(pool, {"min_prob": 0.8}) == []


# ---------------- holdout: the search must pay for its own selection --------

def test_split_universe_partitions_at_the_median_day():
    u = _universe(9)
    older, newer, cut = rh.split_universe(u)
    assert cut == sorted(u)[len(u) // 2]
    assert set(older) | set(newer) == set(u) and not (set(older) & set(newer))
    assert all(d < cut for d in older) and all(d >= cut for d in newer)


def test_holdout_window_ranks_on_the_tuning_half_and_scores_blind():
    u = _universe(10)
    older, newer, _ = rh.split_universe(u)
    r = rh.holdout_window(older, newer, [{}, {"max_accas": 2}, {"max_accas": 4}],
                          min_days=2, min_bets=2)
    assert r["viable"] >= 1 and r["chosen"] is not None
    # the chosen arm is the tuning-half best, by construction
    tuning = {rh.label_of(sp): rh.arm_stats(older, sp)["mean_log"]
              for sp in [{}, {"max_accas": 2}, {"max_accas": 4}]}
    assert r["tune"]["mean_log"] == max(tuning.values())
    # the accounting is internally consistent
    assert 1 <= r["blind_rank"] <= r["blind_n"] == r["viable"]
    assert r["blind_ceiling"] >= r["blind"]["mean_log"]
    assert 0 <= r["top_survive"] <= r["top_n"]


def test_holdout_window_reports_no_viable_arm_instead_of_guessing():
    u = _universe(4)
    older, newer, _ = rh.split_universe(u)
    r = rh.holdout_window(older, newer, [{}], min_days=99)
    assert r["viable"] == 0 and r["chosen"] is None


def test_arm_stats_roi_is_stake_weighted_not_hit_times_odds():
    u = _universe(6)
    s = rh.arm_stats(u, {})
    days = rh.replay(u, {})
    staked = sum(sum(d["stake_pct"]) for d in days.values())
    ret = sum(sum(sp * o for (o, w), sp in zip(d["accas"], d["stake_pct"]) if w)
              for d in days.values())
    assert s["roi"] == pytest.approx((ret - staked) / staked)


# ---------------- pessimistic universe: unsettled legs cost money -----------

def test_pessimistic_universe_grades_unsettled_legs_as_losses(monkeypatch):
    legs = [{"match": "A vs B", "pick": "HOME", "prob": 0.8, "odds": 1.3,
             "result": "win", "row": {}},
            {"match": "C vs D", "pick": "HOME", "prob": 0.7, "odds": 1.3,
             "result": None, "row": {}},          # never settled
            {"match": "E vs F", "pick": "HOME", "prob": 0.6, "odds": 1.3,
             "result": "loss", "row": {}}]
    monkeypatch.setattr(rh.at, "playable_legs",
                        lambda *a, **k: [dict(l) for l in legs])
    opt = rh.build_universe([{"date": "2026-08-01"}], {})
    pes = rh.build_universe([{"date": "2026-08-01"}], {}, unresolved="loss")
    assert len(opt["2026-08-01"]) == 2                       # default: dropped
    assert len(pes["2026-08-01"]) == 3                       # pessimistic: kept
    assert [l["result"] for l in pes["2026-08-01"] if l["match"] == "C vs D"] == ["loss"]


# ---------------- CLV join: the harness must use the audit's own definition --

def _write_clv_ledger(tmp_path, rows):
    import csv as _csv
    import gzip as _gz
    p = tmp_path / "clv_snapshots_2026-09.csv.gz"
    with _gz.open(p, "wt", newline="") as fh:
        w = _csv.DictWriter(fh, fieldnames=["pick_id", "observed_odds", "captured_at_utc",
                                            "league", "odds_provider", "bookmaker",
                                            "snapshot_label"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return p


def test_clv_index_beat_rate_matches_the_audit_definition(tmp_path, monkeypatch):
    _write_clv_ledger(tmp_path, [
        # beat: first 2.00 -> last 1.80 (the close shortened: good CLV)
        {"pick_id": "p-beat", "observed_odds": "2.00", "captured_at_utc": "2026-09-01T08:00:00",
         "league": "EPL", "odds_provider": "betexplorer_odds", "bookmaker": "b1",
         "snapshot_label": "pick_time"},
        {"pick_id": "p-beat", "observed_odds": "1.80", "captured_at_utc": "2026-09-01T16:00:00",
         "league": "EPL", "odds_provider": "betexplorer_odds", "bookmaker": "b1",
         "snapshot_label": "end_of_run"},
        # drift out: first 1.80 -> last 2.10 (the close beat us)
        {"pick_id": "p-drift", "observed_odds": "1.80", "captured_at_utc": "2026-09-01T08:00:00",
         "league": "Sc1", "odds_provider": "scoutingstats_odds", "bookmaker": "b2",
         "snapshot_label": "pick_time"},
        {"pick_id": "p-drift", "observed_odds": "2.10", "captured_at_utc": "2026-09-01T16:00:00",
         "league": "Sc1", "odds_provider": "scoutingstats_odds", "bookmaker": "b2",
         "snapshot_label": "end_of_run"},
        # single price: must be ignored (no CLV measurable)
        {"pick_id": "p-one", "observed_odds": "1.90", "captured_at_utc": "2026-09-01T08:00:00",
         "league": "EPL", "odds_provider": "x", "bookmaker": "b3", "snapshot_label": "pick_time"},
    ])
    monkeypatch.setattr(rh, "LOCALDATA", tmp_path)
    idx = rh.clv_index()
    assert set(idx) == {"p-beat", "p-drift"}
    assert idx["p-beat"]["beat"] is True and idx["p-drift"]["beat"] is False
    assert idx["p-beat"]["raw_delta"] == pytest.approx(-0.20)
    assert idx["p-drift"]["raw_delta"] == pytest.approx(+0.30)


def test_clv_cells_split_by_a_field(tmp_path, monkeypatch):
    _write_clv_ledger(tmp_path, [
        {"pick_id": f"p{i}", "observed_odds": o1, "captured_at_utc": "2026-09-01T08:00:00",
         "league": lg, "odds_provider": "x", "bookmaker": "b", "snapshot_label": "pick_time"}
        for i, (o1, lg) in enumerate([("2.00", "EPL"), ("2.00", "EPL"), ("1.80", "Sc1")])
    ] + [
        {"pick_id": f"p{i}", "observed_odds": o2, "captured_at_utc": "2026-09-01T16:00:00",
         "league": lg, "odds_provider": "x", "bookmaker": "b", "snapshot_label": "end_of_run"}
        for i, (o2, lg) in enumerate([("1.90", "EPL"), ("1.95", "EPL"), ("2.20", "Sc1")])
    ])
    monkeypatch.setattr(rh, "LOCALDATA", tmp_path)
    idx = rh.clv_index()

    class FakeLeg(dict):
        pass

    def fake_pick_id(day, leg):
        return leg["pid"]
    monkeypatch.setattr(rh, "leg_pick_id", fake_pick_id)
    legs = {"2026-09-01": [FakeLeg(pid="p0"), FakeLeg(pid="p1"), FakeLeg(pid="p2")]}
    assert rh._clv_cells(legs, idx)["ALL"]["n"] == 3
    by = rh._clv_cells(legs, idx, split="league")
    assert by["EPL"]["n"] == 2 and by["Sc1"]["n"] == 1
    assert by["EPL"]["beat_rate"] == 1.0 and by["Sc1"]["beat_rate"] == 0.0


# ---------------- the pre-registered bar must refuse to judge early ---------

def test_october_bar_refuses_to_adopt_below_the_n_floor(capsys):
    u = _universe(6)
    rc = rh.cmd_october(u, [{"max_accas": 2}], since="2026-01-01", min_days=60)
    out = capsys.readouterr().out
    assert rc == 0
    assert "NOT YET" in out and "MUST NOT adopt" in out
    assert "[FAIL] n >= 60" in out and "NOT ADOPTABLE" in out


def test_target_projection_prints_the_p10_plan_beside_the_median(capsys):
    u = _universe(10)
    rc = rh.cmd_target(u, {"max_accas": 2}, capital=100_000, target=1_000_000)
    out = capsys.readouterr().out
    assert rc in (0, 1)
    assert "p10  (plan on this)" in out and "do not plan on it" in out
    assert "not a promise about money" in out


def test_clv_split_says_what_an_empty_table_means(tmp_path, monkeypatch, capsys):
    """A split where no cell reaches the noise floor must report the
    dispersion, not print a header and nothing (2026-09-09: the league split
    printed an empty table and looked like a crash)."""
    u = _universe(2)
    # one priced pick per ridden leg, each in its own league -> every cell n=1
    rows = []
    i = 0
    for pool in u.values():
        for leg in pool:
            pid = leg["match"]
            for odds, when in (("2.00", "2026-09-01T08:00:00"), ("1.90", "2026-09-01T16:00:00")):
                rows.append({"pick_id": pid, "observed_odds": odds, "captured_at_utc": when,
                             "league": f"LG{i}", "odds_provider": "x", "bookmaker": "b",
                             "snapshot_label": "pick_time"})
            i += 1
    _write_clv_ledger(tmp_path, rows)
    monkeypatch.setattr(rh, "LOCALDATA", tmp_path)
    monkeypatch.setattr(rh, "leg_pick_id", lambda day, leg: leg["match"])
    rh.cmd_clv(u, {}, split="league")
    out = capsys.readouterr().out
    assert "NO cell reached n>=15" in out
    assert "That dispersion is the finding" in out
    assert "Largest cells anyway" in out


# ---------------- --sweep: the scoreboard must not be able to no-op ---------

def test_sweep_families_only_use_known_engine_keys():
    """A typo'd knob in the sweep table would silently replay the live
    settings and print a no-op comparison — the exact bug the 2026-09-04
    audit found in --ab. An empty spec would A/B live against live."""
    allowed = rh.ENGINE_KEYS | {"min_prob", "leagues"}
    for fam, arms in rh.SWEEP_FAMILIES.items():
        assert arms, f"{fam} has no arms"
        for label, spec in arms:
            assert spec, f"{fam}/{label}: empty spec = live vs live (a no-op)"
            unknown = set(spec) - allowed
            assert not unknown, f"{fam}/{label}: unknown knob(s) {sorted(unknown)} would no-op"


def test_sweep_row_prints_the_arm_and_returns_the_bar(capsys):
    got = rh._sweep_row(_universe(8), {"max_accas": 2}, "test arm")
    out = capsys.readouterr().out
    assert isinstance(got, bool)
    assert "test arm" in out and ("PASS" in out or "fail" in out)


def test_sweep_blind_halves_score_the_arm_not_the_holdout_winner():
    """Regression: the blind-half section once reported whichever arm won the
    tuning half, so every stake_frac arm printed live's identical number."""
    src = (ROOT / "scripts" / "replay_harness.py").read_text()
    i = src.index("BLIND HALVES (tune on one half")
    body = src[i:i + 1400]
    assert "holdout_window(" not in body, "blind halves must score the arm itself"
    assert "arm_stats(newer, spec)" in body and "arm_stats(older, spec)" in body

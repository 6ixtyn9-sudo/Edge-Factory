"""Contract tests for the shipped-slice selection ladder.

The ladder is deliberately tested separately from the door-level P&L tripwire:
its enforcement changes ordering/filtering only, while settlement is always a
read-time join against the supplied result facts.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
from edgefactory.util import norm_team  # noqa: E402


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(at, "SLICE_ENABLED", True)
    monkeypatch.setattr(at, "SLICE_BENCH_ON_BLEED", False)
    return tmp_path


def _row(day, bucket, i, prob=0.80, pick="HOME", shadow=False, seeded=False,
         src=None):
    home = f"{chr(65 + i)}Home Fixture {bucket}"
    away = f"{chr(97 + i)}Away Fixture {bucket}"
    return {
        "date": day, "home": home, "away": away,
        "match": f"{home} vs {away}", "pick": pick,
        "prob_stated": prob, "odds": 1.50, "bucket": bucket,
        "src": src or ("replay" if seeded else "slip"),
        "seeded": seeded, "shadow": shadow,
    }


def _settled(rows, outcomes):
    return {
        (r["date"], norm_team(r["home"]), norm_team(r["away"])): outcome
        for r, outcome in zip(rows, outcomes)
    }


def test_ledger_schema_has_no_result_and_force_upsert_replaces_day(sandbox):
    path = sandbox / "ledger.jsonl"
    first = [_row("2026-09-23", "CAUTION", 1),
             _row("2026-09-23", "CAUTION", 2, shadow=True)]
    at.write_slice_ledger(first, path)
    raw = path.read_text().splitlines()
    assert len(raw) == 2
    assert all("result" not in json.loads(line) for line in raw)

    replacement = [_row("2026-09-23", "CAUTION", 3)]
    at.upsert_slice_day(replacement, "2026-09-23", path)
    rows = at.read_slice_ledger(path)
    assert len(rows) == 1
    assert rows[0]["home"].startswith("DHome")


def test_same_day_compute_does_not_compound_streak_and_cold_demotes_on_day_two(sandbox):
    rows = [_row("2026-09-22", "CAUTION", i, prob=0.90)
            for i in range(12)]
    outcomes = ["home"] * 10 + ["away"] * 2
    path = sandbox / "ledger.jsonl"
    state = sandbox / "state.json"
    at.write_slice_ledger(rows, path)
    settled = _settled(rows, outcomes)

    policy1, verdicts1 = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state, settled=settled,
    )
    assert verdicts1["CAUTION"]["verdict"] == "COLD"
    assert verdicts1["CAUTION"]["demote_streak"] == 1
    assert policy1["rank_caps"] == {}

    policy_same, verdicts_same = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state, settled=settled,
    )
    assert verdicts_same["CAUTION"]["demote_streak"] == 1
    assert policy_same["rank_caps"] == {}

    policy2, verdicts2 = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state, settled=settled,
    )
    assert verdicts2["CAUTION"]["demote_streak"] == 2
    assert verdicts2["CAUTION"]["action"] == "DEMOTED"
    assert policy2["rank_caps"]["CAUTION"] == pytest.approx(0.70)


def test_insufficient_void_and_zero_probability_fail_open(sandbox):
    rows = [_row("2026-09-23", "CAUTION", 0, prob=0.0),
            _row("2026-09-23", "CAUTION", 1, prob=0.80),
            _row("2026-09-23", "CAUTION", 2, prob=0.80)]
    path = sandbox / "ledger.jsonl"
    state = sandbox / "state.json"
    at.write_slice_ledger(rows, path)
    settled = _settled(rows, ["home", "void", "home"])
    policy, verdicts = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state, settled=settled,
    )
    assert verdicts["CAUTION"]["n"] == 1
    assert verdicts["CAUTION"]["verdict"] == "INSUFFICIENT"
    assert verdicts["CAUTION"]["demote_streak"] == 0
    assert policy["rank_caps"] == {}
    assert policy["bench_buckets"] == ()


def test_rank_cap_changes_selection_but_not_stakes(sandbox):
    pool = []
    for i, prob in enumerate((0.74, 0.73, 0.72, 0.71)):
        pool.append({
            "match": f"Caution Home {i} vs Caution Away {i}",
            "pick": "HOME", "prob": prob, "odds": 1.40,
            "result": None,
            "row": {"home": f"Caution Home {i}",
                    "away": f"Caution Away {i}", "bucket": "CAUTION"},
        })
    for i, prob in enumerate((0.71, 0.70, 0.69, 0.68)):
        pool.append({
            "match": f"SV Home {i} vs SV Away {i}",
            "pick": "HOME", "prob": prob, "odds": 1.40,
            "result": None,
            "row": {"home": f"SV Home {i}",
                    "away": f"SV Away {i}", "bucket": "SKIPPED_VETO"},
        })
    live = at.plan_day(pool, 100.0)
    capped = at.plan_day(pool, 100.0, rank_caps={"CAUTION": 0.70})
    assert [a["stake_pct"] for a in capped] == pytest.approx(
        [a["stake_pct"] for a in live]
    )
    assert sum(a["stake_pct"] for a in capped) == pytest.approx(
        sum(a["stake_pct"] for a in live)
    )
    assert capped[0]["legs"][0]["match"].startswith("SV")
    assert all("row" not in leg for acca in capped for leg in acca["legs"])


def test_default_rank_and_plan_are_identity_when_caps_are_none(sandbox):
    pool = [{
        "match": f"Home {i} vs Away {i}", "pick": "HOME",
        "prob": 0.70 - i / 100, "odds": 1.30 + i / 100,
        "result": None,
        "row": {"home": f"Home {i}", "away": f"Away {i}",
                "bucket": "CAUTION"},
    } for i in range(6)]
    assert at.rank_legs(pool) == at.rank_legs(pool, rank_caps=None)
    assert at.plan_day(pool, 123.456) == at.plan_day(
        pool, 123.456, rank_caps=None,
    )


def test_shadow_rows_exclude_real_keys_and_strip_both_policies(sandbox):
    pool = []
    for i, bucket in enumerate(("CAUTION", "SKIPPED_VETO", "CAUTION", "SKIPPED_VETO")):
        pool.append({
            "match": f"Home {i} vs Away {i}", "pick": "HOME",
            "prob": 0.80 - i / 100, "odds": 1.40,
            "result": None,
            "row": {"home": f"Home {i}", "away": f"Away {i}",
                    "bucket": bucket},
        })
    pure = at.plan_day(list(pool), 100.0)
    by_key = {at._leg_key(l): l for l in pool}
    real = at._slice_plan_rows("2026-09-23", pure, by_key)
    real_keys = {at._slice_row_key(r) for r in real[:1]}
    shadow = at._slice_shadow_rows(
        "2026-09-23", pure, by_key, real_keys, {"CAUTION"},
    )
    assert all(r["shadow"] for r in shadow)
    assert all(r["bucket"] == "CAUTION" for r in shadow)
    assert not any(at._slice_row_key(r) in real_keys for r in shadow)


def test_kill_switch_returns_identity_policy(sandbox, monkeypatch):
    monkeypatch.setattr(at, "SLICE_ENABLED", False)
    rows = [_row("2026-09-22", "CAUTION", i, prob=0.85)
            for i in range(12)]
    path = sandbox / "ledger.jsonl"
    state = sandbox / "state.json"
    at.write_slice_ledger(rows, path)
    settled = _settled(rows, ["home"] * 12)
    policy, verdicts = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state, settled=settled,
    )
    assert verdicts["CAUTION"]["verdict"] == "PAYING"
    assert verdicts["CAUTION"]["action"] == "FULL"
    assert policy["rank_caps"] == {}
    assert policy["bench_buckets"] == ()


def test_ledger_scores_late_settlement_without_mutating_rows(sandbox):
    row = _row("2026-09-23", "CAUTION", 1, prob=0.60)
    path = sandbox / "ledger.jsonl"
    state = sandbox / "state.json"
    at.write_slice_ledger([row], path)
    empty, first = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state, settled={},
    )
    assert first["CAUTION"]["n"] == 0
    settled = _settled([row], ["home"])
    later, second = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state, settled=settled,
    )
    assert second["CAUTION"]["n"] == 1
    assert "result" not in json.loads(path.read_text().splitlines()[0])
    assert later["rank_caps"] == {}


def test_benched_bucket_promotes_on_evidence(monkeypatch, sandbox):
    monkeypatch.setattr(at, "SLICE_BENCH_ON_BLEED", True)
    path = sandbox / "ledger.jsonl"
    state = sandbox / "state.json"
    state.write_text(json.dumps({
        "last_eval": "2026-09-22",
        "buckets": {"CAUTION": {"demote_streak": 1, "bench_streak": 4}},
    }))
    rows = [_row("2026-09-23", "CAUTION", i, prob=0.60, shadow=True)
            for i in range(12)]
    at.write_slice_ledger(rows, path)
    settled = _settled(rows, ["home"] * 12)
    policy, verdicts = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state, settled=settled,
    )
    assert verdicts["CAUTION"]["bench_streak"] == 3
    assert verdicts["CAUTION"]["action"] == "FULL"
    assert "CAUTION" not in policy["bench_buckets"]


def test_seeded_replay_rows_are_context_and_cannot_flip_a_verdict(sandbox):
    """Review fix 2026-09-23: two estimands, never pooled into one verdict.

    CAUTION's shipped legs are bleeding on printed probability. The seeded
    replay block is favourable but carries ``avg_p`` proxies rather than the
    frozen slip print, so it must widen the report and never decide. On the
    old pooled basis these same rows scored CAUTION PAYING.
    """
    real = [_row("2026-09-22", "CAUTION", i, prob=0.60) for i in range(12)]
    seed = []
    for i in range(20):
        r = _row("2026-09-22", "CAUTION", i, prob=0.50, seeded=True)
        r["home"], r["away"] = f"S{i}Home CAUTION", f"S{i}Away CAUTION"
        r["match"] = f"{r['home']} vs {r['away']}"
        seed.append(r)
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    at.write_slice_ledger(real + seed, path)
    settled = _settled(real + seed, ["away"] * 12 + ["home"] * 20)

    _policy, verdicts = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state, settled=settled,
    )
    cau = verdicts["CAUTION"]
    assert cau["n"] == 12 and cau["n_shipped"] == 12
    assert cau["n_seeded"] == 20 and cau["n_all"] == 32
    assert cau["verdict"] == "BLEEDING" and cau["gap"] < 0.0
    assert cau["seed_gap"] > 0.0
    # The exact hazard: pooling the replay half flips the sign of the gap.
    pooled_gap = ((20 - (0.60 * 12 + 0.50 * 20)) / 32)
    assert pooled_gap > 0.0 > cau["gap"]
    table = "\n".join(at._slice_table_lines(verdicts))
    assert "replay ctx (excluded): n=20" in table


def test_seeded_rows_alone_cannot_meet_the_min_n_bar(sandbox):
    """Conviction must be earned by printed evidence, not by the seed."""
    seed = [_row("2026-09-22", "CAUTION", i, prob=0.30, seeded=True)
            for i in range(12)]
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    at.write_slice_ledger(seed, path)
    settled = _settled(seed, ["away"] * 12)

    policy, verdicts = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state, settled=settled,
    )
    assert verdicts["CAUTION"]["n"] == 0
    assert verdicts["CAUTION"]["n_seeded"] == 12
    assert verdicts["CAUTION"]["verdict"] == "INSUFFICIENT"
    assert verdicts["CAUTION"]["demote_streak"] == 0
    assert policy["rank_caps"] == {} and policy["bench_buckets"] == ()


def test_empty_upsert_preserves_the_day_unless_nothing_shipped(sandbox):
    """Review fix 2026-09-23: an empty replacement is a no-op, not a clear."""
    path = sandbox / "ledger.jsonl"
    today = [_row("2026-09-23", "CAUTION", i) for i in range(3)]
    prior = [_row("2026-09-22", "CAUTION", 5)]
    at.write_slice_ledger(today + prior, path)

    # A failed/partial slip parse must never delete the day's evidence.
    returned = at.upsert_slice_day([], "2026-09-23", path)
    assert len(returned) == 3
    assert len(at.read_slice_ledger(path)) == 4

    # A genuine no-bet day that never shipped is still cleared, so stale rows
    # cannot keep counting as shipped evidence.
    at.upsert_slice_day([], "2026-09-23", path, allow_empty=True)
    assert [r["date"] for r in at.read_slice_ledger(path)] == ["2026-09-22"]

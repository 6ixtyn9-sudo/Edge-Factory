"""Contract tests for the shipped-slice selection ladder.

The ladder is deliberately tested separately from the door-level P&L tripwire:
its enforcement changes ordering/filtering only, while settlement is always a
read-time join against the supplied result facts.

Grading is delegated to the shared assay engine, so these tests assert
*parity* with edgefactory.assay rather than with a private bar: the point is
that the bucket verdict cannot drift away from the verdict the edges get.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
from edgefactory.assay import context_verdict_league
from edgefactory.config import GATES
from edgefactory.util import norm_team  # noqa: E402


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(at, "SLICE_ENABLED", True)
    monkeypatch.setattr(at, "SLICE_BENCH_ON_VETO", False)
    monkeypatch.setattr(at, "SLICE_DEMOTE_ON_CAUTION", True)
    return tmp_path


def _row(day, bucket, i, prob=0.80, pick="HOME", shadow=False, seeded=False,
         odds=1.50, src=None, name=None):
    tag = "" if name is None else name
    home = f"{chr(65 + i)}Home{tag} Fixture {bucket}"
    away = f"{chr(97 + i)}Away{tag} Fixture {bucket}"
    return {
        "date": day, "home": home, "away": away,
        "match": f"{home} vs {away}", "pick": pick,
        "prob_stated": prob, "odds": odds, "bucket": bucket,
        "src": src or ("replay" if seeded else "slip"),
        "seeded": seeded, "shadow": shadow,
    }


def _alpha(i):
    """Two-letter prefix that stays distinct after norm_team() folding."""
    return chr(65 + (i // 26) % 26) + chr(65 + i % 26)


def _rows_with_roi(bucket, n, wins, odds, *, day="2026-09-22", prob=0.90):
    """Build n HOME-pick rows; pair with ["home"]*wins + ["away"]*(n-wins).

    Picks stay HOME throughout on purpose: pick_result grades an "away"
    settlement as a win for an AWAY pick, so varying the pick alongside the
    outcome would silently turn losses into wins. Fixture names are spelled in
    letters because norm_team() strips digits and punctuation, which would
    fold rows past i=25 onto each other and quietly shrink n.
    """
    rows = []
    for i in range(n):
        tag = _alpha(i)
        home = f"{tag}Home Fixture {bucket}"
        away = f"{tag.lower()}Away Fixture {bucket}"
        rows.append({"date": day, "home": home, "away": away,
                     "match": f"{home} vs {away}", "pick": "HOME",
                     "prob_stated": prob, "odds": odds, "bucket": bucket,
                     "src": "slip", "seeded": False, "shadow": False})
    return rows


def _settled(rows, outcomes):
    return {
        (r["date"], norm_team(r["home"]), norm_team(r["away"])): outcome
        for r, outcome in zip(rows, outcomes)
    }


def _grade(rows, outcomes):
    """Independent expected ROI for the same rows, same accounting as the code."""
    pnl = sum((r["odds"] - 1.0) if o == "home" else -1.0
              for r, o in zip(rows, outcomes) if r["odds"] > 0)
    priced = sum(1 for r in rows if r["odds"] > 0)
    return round(pnl / priced, 4) if priced else None


# ---- ledger plumbing ------------------------------------------------------

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


def test_ledger_scores_late_settlement_without_mutating_rows(sandbox):
    row = _row("2026-09-23", "CAUTION", 1, prob=0.60)
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
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


# ---- assay-engine parity --------------------------------------------------

@pytest.mark.parametrize("n,wins,odds,expected", [
    # n below the engine's own small-n floor: fail open, no private floor.
    (9, 3, 1.10, "UNKNOWN"),
    # 12 <= n < 40 early gates: CAUTION at roi <= -4%, VETO at roi <= -10%.
    (12, 10, 1.14, "CAUTION"),
    (12, 0, 1.50, "VETO"),
    (12, 12, 1.50, "ALLOW"),
    # n >= 40 standard gates.
    (40, 34, 1.10, "VETO"),      # -6.5% lifetime, recent-confirmed
    (40, 0, 1.50, "VETO"),
    (40, 40, 1.30, "ALLOW"),
    (100, 100, 1.30, "BOOST"),
])
def test_bucket_verdict_is_the_engine_verdict(sandbox, n, wins, odds, expected):
    """The ladder must not grade a bucket differently from the edges.

    The expected labels restate context_verdict_league's current gates on
    purpose: if the shared engine is retuned, this test should notice that the
    ladder's behaviour moved with it, not that it quietly diverged.
    """
    rows = _rows_with_roi("CAUTION", n, wins, odds)
    outcomes = ["home"] * wins + ["away"] * (n - wins)
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    at.write_slice_ledger(rows, path)
    _policy, verdicts = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state, settled=_settled(rows, outcomes),
    )
    got = verdicts["CAUTION"]
    assert got["roi"] == _grade(rows, outcomes)
    assert got["verdict"] == expected
    assert got["verdict"] == context_verdict_league(
        got["n"], got["roi"], got["recent_roi"],
    )


def test_recent_roi_is_admitted_only_at_the_system_recent_floor(sandbox):
    """Recency may confirm a verdict, never manufacture one from few legs."""
    rows = _rows_with_roi("SKIPPED_VETO", 40, 34, 1.30)
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    at.write_slice_ledger(rows, path)
    _policy, verdicts = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state,
        settled=_settled(rows, ["home"] * 34 + ["away"] * 6),
    )
    v = verdicts["SKIPPED_VETO"]
    assert v["recent_n"] == 40
    assert v["recent_roi"] is not None           # >= GATES.min_recent_n

    thin = rows[:20]
    at.write_slice_ledger(thin, path)
    _p2, v2 = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state,
        settled=_settled(thin, ["home"] * 17 + ["away"] * 3),
    )
    assert v2["SKIPPED_VETO"]["recent_n"] == 20
    assert v2["SKIPPED_VETO"]["recent_roi"] is None   # below 30 -> withheld
    assert v2["SKIPPED_VETO"]["grade"] == "UNGRADED"  # assay.grade small-n rule


def test_bucket_can_be_rewarded_not_only_punished(sandbox):
    """BOOST is now expressible; the old z-ladder only had punishments."""
    rows = _rows_with_roi("CERTIFIED_CLEAN", 100, 100, 1.30)
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    at.write_slice_ledger(rows, path)
    policy, verdicts = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state,
        settled=_settled(rows, ["home"] * 100),
    )
    v = verdicts["CERTIFIED_CLEAN"]
    assert v["verdict"] == "BOOST" and v["action"] == "FULL"
    assert v["grade"] in ("PLATINUM", "GOLD")
    assert policy["rank_caps"] == {}


# ---- enforcement ----------------------------------------------------------

def test_streak_does_not_compound_same_day_and_caution_demotes_on_day_two(sandbox):
    """CAUTION here is an ROI verdict, not a calibration verdict."""
    rows = _rows_with_roi("CAUTION", 12, 10, 1.14, day="2026-09-22")
    outcomes = ["home"] * 10 + ["away"] * 2
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    at.write_slice_ledger(rows, path)
    settled = _settled(rows, outcomes)
    assert _grade(rows, outcomes) <= -0.04       # the engine's CAUTION bar

    policy1, verdicts1 = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state, settled=settled)
    assert verdicts1["CAUTION"]["verdict"] == "CAUTION"
    assert verdicts1["CAUTION"]["demote_streak"] == 1
    assert policy1["rank_caps"] == {}

    policy_same, verdicts_same = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state, settled=settled)
    assert verdicts_same["CAUTION"]["demote_streak"] == 1   # one step per day
    assert policy_same["rank_caps"] == {}

    policy2, verdicts2 = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state, settled=settled)
    assert verdicts2["CAUTION"]["demote_streak"] == 2
    assert verdicts2["CAUTION"]["action"] == "DEMOTED"
    assert policy2["rank_caps"]["CAUTION"] == pytest.approx(0.70)


def test_zero_probability_and_unsettled_fail_open(sandbox):
    rows = [_row("2026-09-23", "CAUTION", 0, prob=0.0),
            _row("2026-09-23", "CAUTION", 1, prob=0.80),
            _row("2026-09-23", "CAUTION", 2, prob=0.80)]
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    at.write_slice_ledger(rows, path)
    settled = _settled(rows, ["home", "void", "home"])
    policy, verdicts = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state, settled=settled)
    assert verdicts["CAUTION"]["n"] == 1
    assert verdicts["CAUTION"]["verdict"] == "UNKNOWN"
    assert verdicts["CAUTION"]["demote_streak"] == 0
    assert policy["rank_caps"] == {}
    assert policy["bench_buckets"] == ()


def test_kill_switch_returns_identity_policy(sandbox, monkeypatch):
    monkeypatch.setattr(at, "SLICE_ENABLED", False)
    rows = _rows_with_roi("CAUTION", 12, 0, 1.50)
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    at.write_slice_ledger(rows, path)
    policy, verdicts = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state,
        settled=_settled(rows, ["away"] * 12))
    assert verdicts["CAUTION"]["verdict"] == "VETO"    # evidence still reports
    assert verdicts["CAUTION"]["action"] == "FULL"     # policy is identity
    assert policy["rank_caps"] == {}
    assert policy["bench_buckets"] == ()


def test_bench_stays_off_but_reports_would_bench(sandbox, monkeypatch):
    rows = _rows_with_roi("CAUTION", 12, 0, 1.50)
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    state.write_text(json.dumps({
        "last_eval": "2026-09-22",
        "buckets": {"CAUTION": {"demote_streak": 4, "bench_streak": 4}},
    }))
    at.write_slice_ledger(rows, path)
    policy, verdicts = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state,
        settled=_settled(rows, ["away"] * 12))
    v = verdicts["CAUTION"]
    assert v["verdict"] == "VETO" and v["bench_streak"] == 5
    assert v["would_bench"] is True and v["action"] == "DEMOTED"
    assert policy["bench_buckets"] == ()

    monkeypatch.setattr(at, "SLICE_BENCH_ON_VETO", True)
    _policy2, verdicts2 = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state,
        settled=_settled(rows, ["away"] * 12))
    assert verdicts2["CAUTION"]["action"] == "BENCHED"


def test_benched_bucket_promotes_on_evidence(monkeypatch, sandbox):
    monkeypatch.setattr(at, "SLICE_BENCH_ON_VETO", True)
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    state.write_text(json.dumps({
        "last_eval": "2026-09-22",
        "buckets": {"CAUTION": {"demote_streak": 1, "bench_streak": 4}},
    }))
    rows = [_row("2026-09-23", "CAUTION", i, prob=0.60, shadow=True)
            for i in range(12)]
    at.write_slice_ledger(rows, path)
    settled = _settled(rows, ["home"] * 12)
    policy, verdicts = at.compute_bucket_slice(
        "2026-09-23", path=path, state_path=state, settled=settled)
    assert verdicts["CAUTION"]["bench_streak"] == 3
    assert verdicts["CAUTION"]["action"] == "FULL"
    assert "CAUTION" not in policy["bench_buckets"]


# ---- estimand separation + selection-only enforcement ---------------------

def test_seeded_replay_rows_are_context_and_cannot_soften_a_verdict(sandbox):
    """Review fix 2026-09-23: two estimands, never pooled into one verdict.

    CAUTION's shipped legs lose money outright. The seeded replay block is
    profitable but carries ``avg_p`` proxies rather than the frozen slip print,
    so it widens the report and must never reach the verdict. On the old pooled
    basis these same rows dragged the bucket off VETO and onto the weaker
    CAUTION bar — which is the difference between a benchable bucket and one
    that only gets ranked lower.
    """
    real = _rows_with_roi("CAUTION", 12, 0, 1.50)
    seed = [_rows_with_roi("CAUTION", 1, 0, 1.50)[0] | {
        "home": f"Seed{_alpha(i)}Home", "away": f"seed{_alpha(i)}Away",
        "match": f"Seed{_alpha(i)}Home vs seed{_alpha(i)}Away",
        "prob_stated": 0.50, "seeded": True, "src": "replay"}
        for i in range(20)]
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    at.write_slice_ledger(real + seed, path)
    settled = _settled(real + seed, ["away"] * 12 + ["home"] * 20)

    _policy, verdicts = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state, settled=settled)
    cau = verdicts["CAUTION"]
    assert cau["n"] == 12 and cau["n_shipped"] == 12
    assert cau["n_seeded"] == 20 and cau["n_all"] == 32
    assert cau["verdict"] == "VETO"
    assert cau["roi"] < -0.10 and cau["seed_roi"] > 0.0
    # What the pooled basis would have scored, and the bar it lands on.
    pooled_roi = round((20 * 0.50 - 12 * 1.0) / 32, 4)
    assert pooled_roi > cau["roi"]
    assert context_verdict_league(32, pooled_roi, None) == "CAUTION"
    table = "\n".join(at._slice_table_lines(verdicts))
    assert "replay ctx (excluded): n=20" in table


def test_seeded_rows_alone_never_reach_the_engine_floor(sandbox):
    """Conviction must be earned by printed evidence, not by the seed."""
    seed = [_row("2026-09-22", "CAUTION", i, prob=0.30, seeded=True)
            for i in range(12)]
    path, state = sandbox / "ledger.jsonl", sandbox / "state.json"
    at.write_slice_ledger(seed, path)
    policy, verdicts = at.compute_bucket_slice(
        "2026-09-22", path=path, state_path=state,
        settled=_settled(seed, ["away"] * 12))
    assert verdicts["CAUTION"]["n"] == 0
    assert verdicts["CAUTION"]["n_seeded"] == 12
    assert verdicts["CAUTION"]["verdict"] == "UNKNOWN"
    assert verdicts["CAUTION"]["demote_streak"] == 0
    assert policy["rank_caps"] == {} and policy["bench_buckets"] == ()


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


def test_ledger_round_trips_line_separator_lookalikes(sandbox):
    """json.dumps(ensure_ascii=False) may emit U+0085/U+2028/U+2029 raw.

    Those are legal inside a JSON string, but str.splitlines() treats them as
    line breaks, so a fixture name carrying one used to split its own record in
    half and the row disappeared as a silent JSONDecodeError.
    """
    path = sandbox / "ledger.jsonl"
    rows = [_row("2026-09-23", "CAUTION", 1), _row("2026-09-23", "CAUTION", 2),
            _row("2026-09-23", "CAUTION", 3)]
    rows[1]["home"] = "KF\u0085 Fram"
    rows[2]["away"] = "Fram\u2028\u2029 KF"
    at.write_slice_ledger(rows, path)
    assert len(path.read_text(encoding="utf-8").split("\n")) == 4  # 3 + trailing
    back = at.read_slice_ledger(path)
    assert len(back) == 3, "a row was silently dropped by the reader"
    assert back[1]["home"] == rows[1]["home"]
    assert back[2]["away"] == rows[2]["away"]


def test_report_records_which_engine_graded_it(sandbox):
    """Provenance: the artifact must say who produced the verdict."""
    rows = _rows_with_roi("CAUTION", 12, 10, 1.14)
    path = sandbox / "ledger.jsonl"
    state = sandbox / "state.json"
    at.write_slice_ledger(rows, path)
    at.compute_bucket_slice("2026-09-22", path=path, state_path=state,
                            settled=_settled(rows, ["home"] * 10 + ["away"] * 2))
    report = json.loads(state.read_text())
    assert report["engine"] == "edgefactory.assay.context_verdict_league"
    assert report["grade_engine"] == "edgefactory.assay.grade"
    assert report["recent_min_n"] == GATES.min_recent_n
    assert report["recent_window_days"] == GATES.recent_window_days
    assert report["evidence_basis"].startswith("printed-slip only")

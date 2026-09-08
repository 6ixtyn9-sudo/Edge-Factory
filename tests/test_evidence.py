"""The evidence report must measure without touching anything.

The seal test is the point of this file: it pins the sha256 of the
pre-registered question list. If someone edits a hypothesis after seeing
October's data, this test fails and says so. That is the only mechanical
defence against rewriting the question to fit the answer.
"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ev():
    return _load(ROOT / "scripts" / "evidence.py", "evidence_under_test")


# --------------------------------------------------------------------------
# 1. the seal
# --------------------------------------------------------------------------
# amended 2026-09-08 to add Q6 (marginal acca). Legitimate: no
# out-of-sample data existed on that date, so no question was
# edited to fit an answer. Any change AFTER 2026-10-01 is not.
SEAL = "dcf8232f72f94163"


def test_preregistration_is_sealed(ev):
    """Pinned 2026-09-08. A failure here means a question was edited.

    That is not automatically wrong, but it must be a deliberate, reviewed
    act with a new date, never a quiet amendment while data is arriving.
    """
    import hashlib
    got = hashlib.sha256(ev.PREREGISTRATION.encode()).hexdigest()[:16]
    assert got == SEAL, (
        f"pre-registration changed: {got} != {SEAL}. If this is intended, "
        "update SEAL and say in the commit message which question moved "
        "and why.")


def test_preregistration_keeps_the_two_adoption_slots_closed(ev):
    text = ev.PREREGISTRATION
    assert "Q1" in text and "Q2" in text and "Q6" in text
    assert "Q3-Q6 are DIAGNOSTIC and cost no adoption slot" in text
    assert "p10 > 0" in text and "maxDD <= live" in text


def test_out_of_sample_date_is_explicit(ev):
    assert "2026-10-01" in ev.PREREGISTRATION


# --------------------------------------------------------------------------
# 2. it measures, it does not adopt
# --------------------------------------------------------------------------
def test_evidence_never_writes_to_the_engine(ev):
    """Functional, not a source grep.

    Section 4 legitimately widens BUCKETS for the length of one gather so
    that EXCLUDED buckets can be measured -- you cannot audit a filter
    using only the rows it let through. What matters is that the engine is
    handed back exactly as it was found, including when the report raises.
    """
    at = ev._load_engine()
    before = ev.engine_fingerprint(at)
    ev.report(at, "2099-01-01", None, "EMPTY")
    assert ev.engine_fingerprint(at) == before

    with ev._all_buckets(at) as live:
        assert set(at.BUCKETS) >= set(live), "filter should widen, not narrow"
    assert ev.engine_fingerprint(at) == before, "BUCKETS not restored"

    class Boom(Exception):
        pass
    with pytest.raises(Boom):
        with ev._all_buckets(at):
            raise Boom()
    assert ev.engine_fingerprint(at) == before, "not restored after an exception"


def test_no_live_constant_is_reassigned_outside_the_bucket_window():
    src = (ROOT / "scripts" / "evidence.py").read_text()
    for const in ("STAKE_FRAC", "STAKE_MODE", "MAX_ACCAS", "MIN_LEG_ODDS",
                  "MIN_ACCAS", "LEGS_PER_ACCA"):
        assert f"at.{const} =" not in src, f"evidence.py assigns to {const}"
        assert f'setattr(at, "{const}"' not in src


def test_daily_pipeline_does_not_invoke_the_evidence_report():
    """Reporting is out-of-band. It must never sit on the money path.

    Checks for real invocation, not the English word 'evidence', which
    appears legitimately in comments throughout the pipeline.
    """
    for name in ("daily.py", "auto_tickets.py", "picks_today.py"):
        p = ROOT / "scripts" / name
        if not p.exists():
            continue
        src = p.read_text()
        for pattern in ("import evidence", "from evidence",
                        "evidence.py", "evidence.main("):
            assert pattern not in src, f"{name} invokes the report: {pattern}"


# --------------------------------------------------------------------------
# 3. the arithmetic
# --------------------------------------------------------------------------
def _leg(odds, result):
    return {"match": "a vs b", "pick": "HOME", "odds": odds,
            "prob": 0.7, "result": result, "row": {"bucket": "SKIPPED_VETO"}}


def test_roi_of_is_flat_stake_return_on_stake(ev):
    # two legs, one wins at 2.00: stake 2, return 2 -> 0%
    assert ev.roi_of([_leg(2.0, "win"), _leg(2.0, "loss")]) == pytest.approx(0.0)
    # both win at 1.50: stake 2, return 3 -> +50%
    assert ev.roi_of([_leg(1.5, "win"), _leg(1.5, "win")]) == pytest.approx(50.0)
    # both lose -> -100%
    assert ev.roi_of([_leg(1.5, "loss"), _leg(1.5, "loss")]) == pytest.approx(-100.0)
    assert ev.roi_of([]) is None


def test_bootstrap_reports_resolution_not_just_a_point_estimate(ev):
    legs = [_leg(1.5, "win")] * 70 + [_leg(1.5, "loss")] * 30
    b = ev.bootstrap_roi(legs, n=2000, seed=1)
    assert b["roi"] == pytest.approx(5.0, abs=1e-9)
    assert b["p10"] < b["roi"] < b["p90"]
    assert b["min_resolvable"] > 0
    # n_needed scales as (z*se/roi)^2 -- a thin edge needs a big sample
    assert b["n_needed"] > 0


def test_a_thinner_edge_needs_a_bigger_sample(ev):
    fat = [_leg(1.5, "win")] * 80 + [_leg(1.5, "loss")] * 20
    thin = [_leg(1.5, "win")] * 68 + [_leg(1.5, "loss")] * 32
    nf = ev.bootstrap_roi(fat, n=2000, seed=1)["n_needed"]
    nt = ev.bootstrap_roi(thin, n=2000, seed=1)["n_needed"]
    assert nt > nf, "a smaller edge must demand more evidence, not less"


def test_n_needed_is_none_when_there_is_nothing_to_prove(ev):
    losing = [_leg(1.5, "win")] * 50 + [_leg(1.5, "loss")] * 50
    assert ev.bootstrap_roi(losing, n=500, seed=1)["n_needed"] is None


# --------------------------------------------------------------------------
# 4. it survives the window it was built for: October, with no data yet
# --------------------------------------------------------------------------
def test_empty_window_reports_cleanly_instead_of_crashing(ev):
    at = ev._load_engine()
    text, blob = ev.report(at, "2099-01-01", None, "EMPTY")
    assert "no data in this window" in text
    assert blob["days"] == 0


def test_json_blob_round_trips(ev, tmp_path):
    out = tmp_path / "e.json"
    ev.main(["--since", "2099-01-01", "--json", str(out)])
    blob = json.loads(out.read_text())
    assert blob["seal"] == SEAL
    assert "engine" in blob and "STAKE_FRAC" in blob["engine"]


def test_engine_fingerprint_records_what_was_measured(ev):
    at = ev._load_engine()
    fp = ev.engine_fingerprint(at)
    for k in ("STAKE_FRAC", "STAKE_MODE", "MAX_ACCAS", "MIN_LEG_ODDS", "BUCKETS"):
        assert k in fp, f"{k} missing; a report you cannot attribute is useless"
    assert isinstance(fp["BUCKETS"], list)

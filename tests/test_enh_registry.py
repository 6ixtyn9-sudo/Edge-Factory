"""Enhancement certification registry tests — state machine, idempotence, flock integrity."""
import json
from concurrent.futures import ThreadPoolExecutor

from edgefactory.enh_registry import (all_statuses, record_outcome, registry_path,
                                      status_for, wilson_lb)

MKT = "match_over_25"


def _read(root):
    return json.loads(registry_path(root).read_text())


def test_shadow_default(tmp_path):
    assert status_for(MKT, tmp_path) == "SHADOW"
    assert all_statuses(tmp_path) == {}


def test_unpriced_never_advances(tmp_path):
    res = record_outcome(tmp_path, date_="2026-08-03", match="A vs B", market=MKT,
                         price=None, hit=True, source="")
    assert res["recorded"] is True
    assert res["status"] == "SHADOW"
    assert _read(tmp_path)["markets"]["match_over_25@v1"]["n"] == 0


def test_first_priced_moves_to_paper(tmp_path):
    res = record_outcome(tmp_path, date_="2026-08-03", match="A vs B", market=MKT,
                         price=1.50, hit=True, source="theoddsapi")
    assert res["status"] == "PAPER"


def test_idempotent_by_key(tmp_path):
    for _ in range(2):
        record_outcome(tmp_path, date_="2026-08-03", match="A vs B", market=MKT,
                       price=1.50, hit=True, source="theoddsapi")
    assert _read(tmp_path)["markets"]["match_over_25@v1"]["n"] == 1


def test_eligible_transition(tmp_path):
    # 30 priced recs, 27 hits @1.50: wilsonLB95 ~0.758 >= mean breakeven 0.667
    # (multi_source=True here: this test pins the Wilson-gate mechanics; the
    # N5 verification floor is pinned by its own tests below)
    for i in range(30):
        res = record_outcome(tmp_path, date_="2026-08-03", match=f"A{i} vs B{i}", market=MKT,
                             price=1.50, hit=(i < 27), source="theoddsapi",
                             multi_source=True)
    assert res["status"] == "ELIGIBLE"
    entry = _read(tmp_path)["markets"]["match_over_25@v1"]
    assert "wilsonLB95" in entry["status_reason"]


def test_stays_paper_when_evidence_insufficient(tmp_path):
    for i in range(30):
        res = record_outcome(tmp_path, date_="2026-08-03", match=f"A{i} vs B{i}", market=MKT,
                             price=1.50, hit=(i < 18), source="theoddsapi")
    assert res["status"] == "PAPER"


def test_benched_circuit_breaker(tmp_path):
    for i in range(30):  # earn ELIGIBLE
        record_outcome(tmp_path, date_="2026-08-03", match=f"W{i} vs X{i}", market=MKT,
                       price=1.50, hit=True, source="theoddsapi", today="2026-08-03",
                       multi_source=True)
    status = None
    for i in range(30):  # rolling window turns sharply unprofitable
        status = record_outcome(tmp_path, date_="2026-08-03", match=f"L{i} vs M{i}", market=MKT,
                                price=1.50, hit=False, source="theoddsapi", today="2026-08-03")["status"]
    assert status == "BENCHED"


def test_benched_circuit_breaker_window_is_injected(tmp_path):
    # RT: the BENCHED circuit reads a rolling 60-day window against the
    # evaluation date. With the date injected, the same evidence is stable
    # forever: inside the window -> BENCHED; beyond the window -> not benched.
    # Dates are computed relative to today so the test can never go stale
    # (the hardcoded 2026-08-03/2026-10-04 pair would silently drift).
    from datetime import date, timedelta
    anchor = date.today()
    inside = anchor.isoformat()
    beyond = (anchor + timedelta(days=61)).isoformat()
    for today, expect_benched in ((inside, True), (beyond, False)):
        root = tmp_path / today.replace("-", "")
        for i in range(30):
            record_outcome(root, date_=inside, match=f"W{i} vs X{i}", market=MKT,
                           price=1.50, hit=True, source="theoddsapi", today=today,
                           multi_source=True)
        status = None
        for i in range(30):
            status = record_outcome(root, date_=inside, match=f"L{i} vs M{i}", market=MKT,
                                    price=1.50, hit=False, source="theoddsapi", today=today)["status"]
        if expect_benched:
            assert status == "BENCHED"
        else:
            assert status == "ELIGIBLE"  # losses fell out of the 60-day window


def test_concurrent_records_are_not_lost(tmp_path):
    def job(k):
        for j in range(5):
            record_outcome(tmp_path, date_="2026-08-03", match=f"T{k}-{j} vs U", market=MKT,
                           price=1.60, hit=(j % 2 == 0), source="theoddsapi")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(job, range(8)))
    entry = _read(tmp_path)["markets"]["match_over_25@v1"]
    assert entry["n"] == 40 and len(entry["processed"]) == 40


def test_corrupt_file_recovers(tmp_path):
    registry_path(tmp_path).parent.mkdir(parents=True, exist_ok=True)
    registry_path(tmp_path).write_text("{ not json")
    assert status_for(MKT, tmp_path) == "SHADOW"
    res = record_outcome(tmp_path, date_="2026-08-03", match="A vs B", market=MKT,
                         price=1.70, hit=True, source="theoddsapi")
    assert res["recorded"] is True
    assert res["status"] == "PAPER"


def test_corrupt_file_is_quarantined(tmp_path):
    # RT-4: corruption must be recoverable AND auditable — never silently wiped.
    reg = registry_path(tmp_path)
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text("{ not json")
    assert status_for(MKT, tmp_path) == "SHADOW"
    quarantined = list(reg.parent.glob("enhancement_registry.corrupt-*.json"))
    assert len(quarantined) == 1 and quarantined[0].read_text() == "{ not json"
    res = record_outcome(tmp_path, date_="2026-08-03", match="A vs B", market=MKT,
                         price=1.70, hit=True, source="theoddsapi")
    assert res["recorded"] is True and res["status"] == "PAPER"
    assert _read(tmp_path)["markets"]["match_over_25@v1"]["n"] == 1


def test_non_finite_price_never_advances(tmp_path):
    # RT-2: inf would poison profit/breakeven sums; NaN slips past naive guards.
    res = record_outcome(tmp_path, date_="2026-08-03", match="A vs B", market=MKT,
                         price=float("inf"), hit=True, source="theoddsapi")
    assert res["recorded"] is True and res["status"] == "SHADOW"
    assert _read(tmp_path)["markets"]["match_over_25@v1"]["n"] == 0
    res = record_outcome(tmp_path, date_="2026-08-04", match="A vs B", market=MKT,
                         price=float("nan"), hit=True, source="theoddsapi")
    assert res["recorded"] is True
    assert _read(tmp_path)["markets"]["match_over_25@v1"]["n"] == 0


def test_wilson_lb_monotonic():
    assert wilson_lb(0, 0) == 0.0
    assert wilson_lb(9, 10) < wilson_lb(90, 100)  # wider CI (lower LB) on small n
    assert wilson_lb(27, 30) > 2 / 3  # the eligibility bar used in tests above


# --- Governance N5 (Addendum 27.11): multi-source verification floor ---


def test_stays_paper_without_multi_source_verification(tmp_path):
    # 30 priced outcomes, 30 hits @1.50 (Wilson clears easily), but ZERO
    # multi-source outcomes -> must stay PAPER with a transparent reason.
    for i in range(30):
        record_outcome(tmp_path, date_="2026-08-03", match=f"W{i} vs X{i}", market=MKT,
                       price=1.50, hit=True, source="theoddsapi", today="2026-08-03")
    entry = _read(tmp_path)["markets"]["match_over_25@v1"]
    assert entry["status"] == "PAPER"
    assert "multi-source" in (entry.get("status_reason") or "")
    assert entry.get("multi_n", 0) == 0


def test_eligible_requires_multi_source_floor(tmp_path):
    # 30 priced outcomes, 30 hits @1.50, exactly 8 of 30 multi-source
    # (ceil(30 * 0.25) = 8) -> ELIGIBLE; reason records the verification.
    for i in range(30):
        record_outcome(tmp_path, date_="2026-08-03", match=f"W{i} vs X{i}", market=MKT,
                       price=1.50, hit=True, source="theoddsapi", today="2026-08-03",
                       multi_source=(i < 8))
    entry = _read(tmp_path)["markets"]["match_over_25@v1"]
    assert entry["status"] == "ELIGIBLE"
    assert entry.get("multi_n") == 8
    assert "multi-source 8/8" in entry["status_reason"]


def test_below_multi_source_floor_stays_paper(tmp_path):
    # 30 priced outcomes, 30 hits @1.50, only 7 of 30 multi-source -> PAPER
    for i in range(30):
        record_outcome(tmp_path, date_="2026-08-03", match=f"W{i} vs X{i}", market=MKT,
                       price=1.50, hit=True, source="theoddsapi", today="2026-08-03",
                       multi_source=(i < 7))
    entry = _read(tmp_path)["markets"]["match_over_25@v1"]
    assert entry["status"] == "PAPER"
    assert "7/8" in entry["status_reason"]

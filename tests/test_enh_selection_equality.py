"""Enhancement selection must be identical with the candidate log on, off, or broken.

The overlay is run with a stub database connection (every lookup returns nothing)
and a stubbed price lookup, so it reaches the priced/eligible branch without any
network or local data. Only the two log keys may differ between runs.
"""
import pytest

import scripts.picks_today as pt

LOG_KEYS = ("enh_candidate_log", "enh_cluster_id")

PICK = {"home": "Alpha FC", "away": "Beta United", "date": "2026-10-18",
        "league": "Test League", "pick": "1", "avg_p": 0.62, "n_way": 3,
        "market": "1x2", "odds": 1.9, "kickoff": "20:00"}


class _StubCon:
    def execute(self, *a, **k):
        class _R:
            def fetchone(self_inner):
                return None

            def fetchall(self_inner):
                return []
        return _R()


def _fake_attach(pick, index, **kw):
    """Price every candidate at 1.50, except home_under_35 at 1.20 (below the minimum)."""
    market = pick.get("recommended_enhancement")
    price = 1.20 if market == "home_under_35" else 1.50
    pick["enhancement_price"] = price
    pick["enhancement_priced"] = True
    pick["enhancement_price_source"] = "test"
    pick["enhancement_price_book"] = "test"
    return pick


@pytest.fixture
def priced(monkeypatch):
    monkeypatch.setattr(pt, "attach_enhancement_price", _fake_attach)
    monkeypatch.setattr(pt, "ENH_CANDIDATE_LOG_ENABLED", True)
    return monkeypatch


def _run(pick=PICK):
    return pt.compute_dynamic_enhancement(_StubCon(), dict(pick), {})


def _selection(out):
    return {k: v for k, v in out.items() if k not in LOG_KEYS}


def test_selection_identical_with_and_without_logging(priced):
    on = _run()
    priced.setattr(pt, "ENH_CANDIDATE_LOG_ENABLED", False)
    off = _run()
    # The path under test really ran: a priced eligible candidate was chosen.
    assert on["recommended_enhancement"] is not None
    assert on["event_notes"]
    assert _selection(on) == _selection(off)


def test_logging_off_stores_empty_log(priced):
    priced.setattr(pt, "ENH_CANDIDATE_LOG_ENABLED", False)
    out = _run()
    assert out["enh_candidate_log"] == []


def test_logging_exception_does_not_change_selection(priced):
    reference = _run()  # logging on, normal
    priced.setattr(pt, "ENH_CANDIDATE_LOG_ENABLED", False)
    off = _run()
    priced.setattr(pt, "ENH_CANDIDATE_LOG_ENABLED", True)

    def _boom(*a, **k):
        raise RuntimeError("simulated logging failure")

    priced.setattr(pt, "_build_enh_log_entry", _boom)
    broken = _run()  # must not raise
    assert _selection(broken) == _selection(off) == _selection(reference)
    assert broken["enh_candidate_log"] == []  # every row failed to build, none stored

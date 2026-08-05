"""Test hermeticity (red-team F3 + audit N1, fixed 2026-08-05).

The production modules call load_dotenv() at import time (theoddsapi.py:62,
bzzoiro*.py, db.py, capture_theodds.py) and some tests RELOAD modules, which
re-reads .env. A per-test delenv runs too late. So we neutralize
dotenv.load_dotenv for the ENTIRE session BEFORE any src module is imported
(conftest imports before test modules), and additionally strip the env knobs
the module defaults depend on. Result: the suite is deterministic in CI and
locally regardless of the operator's ambient .env.
"""
import dotenv

dotenv.load_dotenv = lambda *a, **k: False  # noqa: E731 - session-wide neutralization

import pytest  # noqa: E402

_ENV_KNOBS = (
    "ODDS_API_MARKETS",
    "ODDS_API_TOTAL_POINTS",
    "ODDS_API_REGIONS",
    "ODDS_API_MONTHLY_BUDGET",
    "ODDS_API_CLOSE_WINDOW_MIN",
    "ODDS_API_KEYS",
    "ODDS_API_BASE",
    "EDGE_FACTORY_ENGINE_AWARE_DEBIAS",
    "EDGE_FACTORY_VETO_RESOLUTION",
    "EDGE_FACTORY_ODDSPAPI_PRICES",
    "EDGE_FACTORY_LOCALDATA",
    "ODDSPAPI_API_KEYS",
)


@pytest.fixture(autouse=True)
def _hermetic_env(monkeypatch):
    for knob in _ENV_KNOBS:
        monkeypatch.delenv(knob, raising=False)
    yield

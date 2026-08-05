"""Test hermeticity (red-team F3, fixed 2026-08-05).

The production modules call load_dotenv() at import (e.g.
src/edgefactory/sources/theoddsapi.py), so tests would otherwise read the
operator's local .env and pass/fail depending on the machine. This autouse
fixture removes the environment knobs the module defaults depend on before
each test and restores them after, making the suite deterministic in CI and
locally regardless of ambient .env.
"""
import pytest

_ENV_KNOBS = (
    "ODDS_API_MARKETS",
    "ODDS_API_TOTAL_POINTS",
    "ODDS_API_REGIONS",
    "ODDS_API_MONTHLY_BUDGET",
    "ODDS_API_CLOSE_WINDOW_MIN",
    "EDGE_FACTORY_ENGINE_AWARE_DEBIAS",
    "EDGE_FACTORY_VETO_RESOLUTION",
    "EDGE_FACTORY_ODDSPAPI_PRICES",
)


@pytest.fixture(autouse=True)
def _hermetic_env(monkeypatch):
    for knob in _ENV_KNOBS:
        monkeypatch.delenv(knob, raising=False)
    yield

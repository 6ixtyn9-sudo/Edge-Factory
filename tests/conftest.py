"""Test hermeticity (red-team F3 + audit N1, fixed 2026-08-05).

The production modules call load_dotenv() at import time (theoddsapi.py:62,
bzzoiro*.py, db.py, capture_theodds.py) and some tests RELOAD modules, which
re-reads .env. A per-test delenv runs too late. So we neutralize
dotenv.load_dotenv for the ENTIRE session BEFORE any src module is imported
(conftest imports before test modules), and additionally strip the env knobs
the module defaults depend on. Result: the suite is deterministic in CI and
locally regardless of the operator's ambient .env.

2026-09-24, after the first Actions run of the regression step (7 failures on a
runner, 0 locally): the strip must also happen at MODULE scope, not only in the
per-test fixture. Two mechanisms the fixture alone cannot reach, both observed:

  * import-time binding — `theoddsapi.MONTHLY_BUDGET` is computed from
    ODDS_API_MONTHLY_BUDGET when the module is first imported, which is after
    conftest but before any fixture runs; and
  * subprocess inheritance — the ml-fade CLI tests spawn real python processes,
    which inherit THIS process's env, so a knob that is only removed for the
    duration of a test still leaks into the child.

Popping here is safe for tests that want a knob: the autouse fixture still runs
per test, and a test body that calls setenv() (or reloads a module) sets the
value it needs after both strips.
"""
import os

import pytest

# Neutralize dotenv BEFORE importing anything from src (see docstring).
import dotenv  # noqa: E402

dotenv.load_dotenv = lambda *a, **k: False  # noqa: E731 - session-wide neutralization

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
    # Transport selection. forebet._cloud_fetch_mode() (sources/forebet.py:45)
    # short-circuits to the relay fetcher on any Actions runner, which walks
    # past the two transports a test patches — so on CI the same assertions
    # silently run against live scraped data instead of the ladder under test.
    "GITHUB_ACTIONS",
    "EDGE_FACTORY_FOREBET_CLOUD",
    # Delivery families. scripts/notify.py:370-380 treats one env var as one
    # family; a runner whose job env maps TELEGRAM_* (or Twilio/Meta/Callmebot)
    # secrets grows a second family, and the per-family barrier/masking
    # expectations in test_notify invert for reasons unrelated to the code.
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "CALLMEBOT_APIKEY",
    "CALLMEBOT_PHONE",
    "WHATSAPP_TOKEN",
    "WHATSAPP_PHONE_NUMBER_ID",
    "WHATSAPP_RECIPIENT",
    "WHATSAPP_TEMPLATE_NAME",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_WHATSAPP_NUMBER",
    # Persistence endpoints: with these present, db/notify tests take the live
    # Supabase path instead of the local stub.
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "SUPABASE_SERVICE_KEY",
)

for _knob in _ENV_KNOBS:
    os.environ.pop(_knob, None)  # module scope: see the docstring above


@pytest.fixture(autouse=True)
def _hermetic_env(monkeypatch):
    for knob in _ENV_KNOBS:
        monkeypatch.delenv(knob, raising=False)
    yield

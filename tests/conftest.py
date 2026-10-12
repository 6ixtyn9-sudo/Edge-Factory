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
import pathlib
import sys

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

# Gitignored runtime state gets neutralized too, for the same reason. The nightly
# cache step (actions/cache/restore, path: localdata) unpacks
# localdata/entity_registry.json into the runner's checkout; the "Restore
# committed data" guard that follows only re-checks-out git-TRACKED localdata
# files, and `git clean -fd` deliberately spares ignored ones, so an untracked
# registry built by some earlier run survives into the test run. entities.py
# consults it before the identity fallback (entities.py:88-99), which is exactly
# how the two league-canonicalization tests in test_ml_fade_contexts.py flipped on
# a runner while staying green on every clean checkout. Point the path at a file
# that never exists: the fallback is what those tests are about.
_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))
try:
    from edgefactory import entities as _entities  # noqa: E402
except Exception:  # pragma: no cover - src not importable at all: nothing to pin
    pass
else:
    _entities.ENTITY_REGISTRY_PATH = _ROOT / "localdata" / "_absent_during_tests_.json"
    _entities.clear_entity_caches()


@pytest.fixture(autouse=True)
def _hermetic_env(monkeypatch):
    for knob in _ENV_KNOBS:
        monkeypatch.delenv(knob, raising=False)
    yield


# ---- module budget globals (2026-10-12, round-5 close-out A2) --------------
#
# The BetExplorer adapter sizes its network work with module-level budgets, and
# two PRODUCTION call sites clamp one of them with a bare rebind, not a scoped
# change: scripts/capture_betexplorer.py (capture(): `source._MAX_FETCHES_PER_RUN
# = limit`) and scripts/picks_today.py (the enrichment entry point:
# `_be_mod._MAX_FETCHES_PER_RUN = max(0, int(max_fetches))`). Both are
# deliberate for a real run - one process, one run - but a TEST that exercises
# either entry point leaves the global at the test's own small value, and the
# next test in the process then sees a budget it never asked for. Found the hard
# way: the round-5 census test called capture(max_fixtures=1) and the politeness
# cache test's second read was refused by the leftover budget of 1
# (5 passed in isolation, 1 failed in suite order).
#
# Rather than rely on every test remembering (monkeypatch only restores what it
# itself patched), the suite snapshots the budgets before each test and puts
# them back after. This is the systemic half of A2; the session-end assertion
# below is the alarm if anything else ever moves them.
_BUDGET_GLOBALS = (
    "_MAX_FETCHES_PER_RUN", "_MAX_REQUESTS_PER_RUN", "_MARKET_INTERVAL",
    "_MAX_MARKET_ROWS", "_MAX_MARKET_LINES", "_MAX_H2H_ROWS",
    "_MAX_STANDINGS_ROWS", "_MAX_LAST_RESULT_ROWS", "_MAX_BOOKS_RETAINED",
    "_MAX_MARKET_BOOKS_PER_LINE",
)


#: Run-scoped scalars with the same failure mode as the budgets: a test that
#: sets one leaves it set for the rest of the process unless it restores it.
_RUN_STATE_GLOBALS = (
    "_request_count", "_fetch_count", "_be_429", "_be_cached",
    "_be_cooling_down", "_market_requests", "_market_budget_stop",
)


def _odds_module():
    try:
        from edgefactory.sources import betexplorer_odds as be  # noqa: PLC0415
    except Exception:  # pragma: no cover - src not importable: nothing to guard
        return None
    return be


@pytest.fixture(autouse=True)
def _restore_budget_globals():
    be = _odds_module()
    if be is None:
        yield
        return
    names = _BUDGET_GLOBALS + _RUN_STATE_GLOBALS
    before = {name: getattr(be, name) for name in names if hasattr(be, name)}
    yield
    for name, value in before.items():
        setattr(be, name, value)


@pytest.fixture(scope="session", autouse=True)
def _budgets_end_at_their_defaults():
    """Session-end alarm: the budgets a run would see must be the defaults.

    If a test moves one and something prevents the per-test restore (a module
    reload, a fixture running outside this conftest, a new pattern), the suite
    reports it here instead of silently under-budgeting later tests.
    """
    defaults = {name: getattr(_odds_module(), name) for name in _BUDGET_GLOBALS}
    yield
    be = _odds_module()
    drifted = {name: (defaults[name], getattr(be, name))
               for name in _BUDGET_GLOBALS if getattr(be, name) != defaults[name]}
    assert not drifted, (
        f"module budgets left below their defaults after the suite: {drifted}. "
        "Somewhere a test (or a production entry point called from one) rebound a "
        "budget global without restoring it - see tests/conftest.py, A2 of the "
        "2026-10-12 close-out.")

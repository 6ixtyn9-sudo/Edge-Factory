#!/usr/bin/env bash
# A2 of the 2026-10-12 close-out: the leak-class sweep for module-global
# budget rebinds.
#
# The census test of round 5 called capture(max_fixtures=1) and the politeness
# cache test failed only in full-suite order, because capture() clamps
# be._MAX_FETCHES_PER_RUN with a bare assignment - a run-scoped change to a
# process-global. This script prints:
#   * every production site that rebinds a budget global (the mechanism);
#   * every rebind of a budget global anywhere in tests/ (a bare assignment is
#     the failure mode; monkeypatch.setattr is scoped and restores itself);
#   * the systemic guard the suite now carries (tests/conftest.py);
#   * the test that pins the restored dated claim.
#
# Run from the repository root:
#   bash handoff/round5_form_h2h_2026-10-12/a2_leak_sweep.sh
set -uo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"
TIP="$(git rev-parse --short HEAD)"

echo "=== A2: module-global budget rebinds, sweep at $TIP ==="
echo

echo '$ grep -rn "source\._MAX_FETCHES_PER_RUN *=\|_be_mod\._MAX_FETCHES_PER_RUN *=" scripts/'
grep -rn "source\._MAX_FETCHES_PER_RUN *=\|_be_mod\._MAX_FETCHES_PER_RUN *=" scripts/ || true
cat <<'TXT'

  ^ the two PRODUCTION sites (capture_betexplorer.capture and the picks_today
    enrichment entry point). Both are deliberate for one real run in one
    process; neither restores the previous value, which is why a TEST that
    calls either entry point changes the budget of every later test in the
    same process. Reported here; the production semantics are left alone on
    purpose - changing them is behaviour, not hygiene.
TXT
echo

echo '$ grep -rnE "^[^#]*\b(_MAX_[A-Z_]+|_MARKET_[A-Z_]+) *=([^=]|$)" tests/   # bare rebinds, assignments only'
if grep -rnE "^[^#]*\b(_MAX_[A-Z_]+|_MARKET_[A-Z_]+) *=([^=]|$)" tests/; then
  cat <<'TXT'
  ^ FOUND. Disposition of each, so "wrapped or explained" is checkable:
    * tests/test_oddspapi_catalog_resolution.py -- the oddspapi catalog
      module's own caches, in a DIFFERENT module from the BetExplorer adapter.
      That test restores them in a `finally` (grep the file for
      "restore the module-level caches") to the module's documented empty /
      fallback state, not to a snapshot: the caches are meant to be empty
      between runs, so restoring to the default IS the correct restore.
      Reason recorded here rather than wrapped; it is the same file's own
      documented pattern (added 2026-07 before this round).
    * every other budget global in tests/ is touched only through
      monkeypatch.setattr (below) or through the production entry points the
      conftest guard covers.
TXT
else
  echo "  (none: no test rebinds a budget global with a bare assignment)"
fi
echo

echo '$ grep -rn "setattr(be, \"_MAX\|setattr(be, \"_MARKET\|setattr(_be_mod" tests/'
grep -rn "setattr(be, \"_MAX\|setattr(be, \"_MARKET\|setattr(_be_mod" tests/ || true
cat <<'TXT'

  ^ monkeypatch.setattr is scoped: pytest restores it at the end of the test
    that made the change, so these need no further wrapping.
TXT
echo

echo '$ grep -n "be\._" tests/*.py  |  grep -v "monkeypatch|assert|#|getattr|setattr"'
grep -n "be\._" tests/*.py | grep -v "monkeypatch\|assert\|#\|getattr\|setattr" || true
cat <<'TXT'

  ^ direct attribute touches with no setter in sight: cache clears (run-scoped
    memory the tests themselves populate) and _fetch(...) calls. The one
    ASSIGNMENT this list used to contain - test_betexplorer_match_detail.py's
    be._request_count = 4 - is now a monkeypatch.setattr, so pytest restores it.
TXT
echo

echo '$ grep -rn "_fixture_cache.clear()\|_match_cache.clear()" tests/ | wc -l'
grep -rn "_fixture_cache.clear()\|_match_cache.clear()" tests/ | wc -l
cat <<'TXT'

  ^ cache clears: run-scoped MEMORY, not budgets - cleared by the tests that
    populate them (the census test and the detail tests).
TXT
echo

echo "== the systemic guard the suite now carries =="
echo '$ grep -n "_restore_budget_globals\|_budgets_end_at_their_defaults\|_BUDGET_GLOBALS" tests/conftest.py'
grep -n "_restore_budget_globals\|_budgets_end_at_their_defaults\|_BUDGET_GLOBALS" tests/conftest.py
cat <<'TXT'

  * _restore_budget_globals (autouse, function-scoped): snapshots the budget
    globals before EVERY test and puts them back after it, so no test can
    inherit another test's value - even when the change came from a production
    entry point the test merely called.
  * _budgets_end_at_their_defaults (autouse, session-scoped): the alarm. If the
    suite ever ends with a budget that is not what a real run would see, the
    session fails and names the drifted globals, instead of quietly
    under-budgeting later tests.
TXT
echo

echo "== the dated claim this sweep also protects =="
echo '$ grep -n "the wrapper.s receipt" tests/test_betexplorer_match_detail.py'
grep -n "the wrapper's receipt" tests/test_betexplorer_match_detail.py || true
cat <<'TXT'

  ^ the comment belongs to
    tests/test_betexplorer_match_detail.py::test_receipt_keeps_the_row_refusal_census
    and is PINNED by tests/test_dated_claims_ledger.py, whose scan is the only
    reason the comment form matters.
TXT
echo
echo '$ PYTHONPATH=src .venv/bin/python -m pytest tests/test_dated_claims_ledger.py -q -p no:randomly'
PYTHONPATH=src .venv/bin/python -m pytest tests/test_dated_claims_ledger.py -q -p no:randomly 2>&1 | tail -2

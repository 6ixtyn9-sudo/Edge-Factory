# Execution receipt: authorized fallback-origin fix and failing contract tests

**Date:** 2026-10-09 (SAST)<br>
**Baseline:** `8c49c55ab37c2f1de00528f83a346881c4df00b7`<br>
**Implementation commit:** `6c3699df50fb19efd7c52dc45c85117d4480e8ea`<br>
**Branch:** `arena/11e63d6d-edge-factory` — pushed; not merged or deployed.

## Authorization and order

The latest user-supplied operator decision explicitly authorizes, independently of Gate A:

1. Correct `load_thresholds()`'s fallback flag and add a certified-OU-only regression.
2. Add failing qualifier/electorate certification-contract tests; do not change live selection.

These changes were implemented, tested, committed and pushed **before** the C1 specification/control publication. Recorder, hooks, ignore rules, index publication, workflow edits, live routing, operational schema migration and long-term retention were explicitly excluded and remain untouched.

## Production change (one narrow function)

`scripts/picks_today.py::load_thresholds()` now sets `is_fallback = not bool(t1x2)` **before** installing fallback entries in its second fallback branch, and returns that flag. The early empty-registry fallback still returns `True`. This accurately reports a default 1X2 floor even when a certified OU/BTTS/unparseable edge makes `edges` nonempty.

No thresholds, parsed entries, model, qualification predicate, source election, selected rows, archive payloads or frozen identities changed. The existing caller consumes the flag only for a stderr fallback warning, not selection. Consequently the warning now appears for non-1X2-only registries where previously suppressed. Its incumbent text still says registry missing/empty and OU/BTTS skipped; that wording is too narrow for this newly exposed branch (OU/BTTS entries are retained). It was not rewritten or used as a selection gate in this narrowly scoped patch.

An isolated comparison executed the pinned old `load_thresholds` function against the changed one on identical temporary inputs. First three returned values (1X2 entries, OU, BTTS) were exactly equal in all seven cases:

| Input | Old flag | New flag |
|---|---|---|
| Missing | True | True |
| Empty | True | True |
| Certified OU only | False | True |
| Certified BTTS only | False | True |
| Nonparseable certified entry | False | True |
| Certified 1X2 | False | False |
| Mixed certified 1X2/OU | False | False |

This is function-output equivalence, not full pipeline replay or deployment verification.

## Tests and actual outcomes

`tests/test_picks_today.py` adds three hermetic registry controls: certified OU-only (assert `True` plus exact fallback/OU preservation), missing registry (True), certified 1X2 registry (False).

`tests/test_consensus_contract_gaps.py` uses real registry parsing and `eval_1x2` on a single synthetic fixture, pre-Forebet-retirement date, non-cup/non-friendly league, explicitly uniform `source_weights={}` and no serving model/fade rules or warehouse. Positive controls require one emitted certified row. Negative controls prohibit stamping the historical/qualified label on an unsupported signal; they do not decide a new routing contract or require blanket suppression of independent signals.

| Case | Result |
|---|---|
| Min-p valid 60/72/72 | Pass |
| Home-only home | Pass |
| Odds inclusive lower 1.20 / inside upper 1.74 | Two passes |
| Historical fb/zb/sa / fb/zb valid electorate | Two passes |
| Min-p invalid 56/72/72, average 66.7 | **Fail: certified label still emitted** |
| Home-only away | **Fail: certified label still emitted** |
| Odds below lower 1.19 / at exclusive upper 1.75 | **Two failures: certified label still emitted** |
| Statarea/Vitibet/Bzzoiro / Statarea/Vitibet substitute electorate | **Two failures: historical label still emitted** |

The six failures are intentional unresolved contracts, **not skipped or xfailed**. A run including this file is red until separately authorized live-policy work fixes the contracts. No failure was “repaired” by weakening assertions or changing selection.

Executed commands:

```sh
# Before fix: OU-only regression failed at is_fallback is True (actual False).
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_picks_today.py -k certified_ou_only_registry_reports_1x2_fallback
# After fix: 30 passed.
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_picks_today.py
# Contract suite: 6 failed, 6 passed, exit 1, all final failures at contract assertions.
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q --tb=short -p no:cacheprovider tests/test_consensus_contract_gaps.py
# Related regression selection: 160 passed.
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_picks_today.py tests/test_scored_candidate_shadow_picks.py tests/test_phase5_registry_protection.py tests/test_audit_recent_picks.py tests/test_sync_supabase.py tests/test_kickoff_contract.py tests/test_identity_adversarial.py
```

During test construction, the first contract-harness run failed at `source_weights=None` (`.get` on None), including positive controls. The fixture was corrected to pass explicit uniform weights, as the production caller does. No unrelated optional-argument production fix was made. The rerun reached and failed only the six intended contract assertions.

The sandbox initially had no pytest. Installed existing `requirements.txt` into ignored `.venv`; no dependency manifest/lock changes. Versions include CPython 3.11.2, pytest 9.1.1, duckdb 1.5.6, pandas 3.0.6, numpy 2.4.6. Repository requirements are unpinned; this is not a pinned production replay environment. No full regression suite, provider requests, model fitting, operational pipeline, warehouse replay, live export or notification delivery was run. No production localdata was written.

## Remaining boundary

Qualifier/electorate **repair** is not authorized here; tests expose it. Gate A's implementation/acceptance and live activation remain blocked. The [C1 specification/control](GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md) is an independent documentation/layout deliverable, not permission to implement the recorder or index publisher.

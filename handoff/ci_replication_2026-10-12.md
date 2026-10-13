# CI replication, 2026-10-12 — what a GitHub Actions run would have done, run locally

**Why this file exists.** The operator asked, before merging PR #61, why the
branch's workflow was not triggered to catch mistakes while there is still time
to fix them. The short answer is in §1 (the run cannot be triggered from here,
and it would not have tested this work); this file is the substitute: the
workflow's own regression command, run locally against the frozen content, plus
a stricter variant that the workflow does not run.

## 1. Why the workflow could not be used as asked

* `gh pr checks 61` reports one check, `Workers Builds: edge-factory-source-relay`
  (Cloudflare, external), **FAILURE**; `mergeStateStatus: UNSTABLE`,
  `mergeable: MERGEABLE` — so it is not a merge blocker. The worker's files are
  byte-identical between the branch and `origin/main` (`git diff --stat origin/main 8e50de2 -- relay/`
  → empty) and the same check reads **success** on `origin/main`'s head
  (`dda42ee`) — so the red mark is not attributable to any content difference
  visible here; the build detail lives behind the Cloudflare dashboard, which
  this sandbox cannot reach.
* The repository's workflows are `daily.yml` (name: Autonomous Edge Factory
  3-Hour Service; trigger: **workflow_dispatch only**),
  `forebet-browser-diagnostic.yml` and `source-probe-dispatch.yml`. Nothing
  runs on push or pull_request, so no check was ever going to run on a push.
* Dispatching is not available from here (Actions write is not granted to this
  sandbox's token — 403 in every earlier round), and it would be the wrong
  instrument anyway: a dispatch on this branch would `checkout` the **remote**
  branch state, which is `8e50de2` — rounds 4–5 were never pushed (standing
  rule: no push before #61 merges) — so it would test the old tree. Worse, the
  service job ends with `Persist pipeline state to git`, i.e. it **pushes state
  commits to the ref it ran on**; on this branch that would move PR #61's head
  (forbidden) and write live pipeline state (scratch-only rule).
* What the substitute cannot cover: the runner image, Python 3.13 (this sandbox
  has 3.11.2; nothing removed in 3.12/3.13 is imported anywhere — grep below),
  unpinned `requirements.txt` resolution at run time, and the service job's live
  network with secrets. A post-merge dispatch of `daily.yml` on `main` (or on a
  branch ref chosen in the GitHub UI) remains the only way to exercise those.

## 2. The regression job's own command, run here

The workflow's job `regression-tests` ends with:

    PYTHONPATH=src python3 -m pytest tests/ -q

Run in this sandbox after `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
(exactly the job's install), on the frozen content:

    2907 passed in 60.00s

## 3. The stricter variant the workflow does NOT run (shuffled order)

The job runs tests in collection order; pytest-randomly is not in
`requirements.txt`. Installing it and shuffling is strictly stronger — and it
found a real, **pre-existing** order coupling:

    seed 1:  1 failed, 2906 passed
    seed 2:  1 failed, 2906 passed
    seed 3:  2907 passed

    FAILED tests/test_oddspapi_quota_honesty.py::test_429_on_the_board_stops_the_capture_and_writes_quota_evidence
    KeyError: 'retry_after_s'

Mechanism, measured: the test monkeypatched `cap.fetch_fixtures` to raise the
429 **directly**, skipping `oddspapi_odds._get_json` — the only place that calls
`_record_rate_limit` in shipped code (`src/edgefactory/sources/oddspapi_odds.py:79`).
The receipt's `rate_limit` is read from the module global
(`rate_limit_diagnostics()`), so the assertion only held when an earlier test in
the same file had recorded a 429 first. Proof it is not this round's:

    8e50de2 (pristine base), same file, shuffled:  1 failed   -> identical failure
    fixed order, same file:                        4 passed

Fix (one test file, production code untouched): the test now stubs the
**transport** (`urllib.request.urlopen`) and keeps the real `fetch_fixtures`, so
the path exercised is transport → recorder → receipt — the same path production
uses. Mutation check that the assertion still bites: with
`op._record_rate_limit` replaced by a no-op (pytest plugin), the test FAILS as
before; with the real recorder it passes in any order.

After the fix:

    file alone, fixed order      4 passed
    file alone, shuffled         4 passed
    full suite, fixed order      2907 passed
    full suite, seeds 1,2,3,7,13 2907 passed (five runs)

## 4. What this pass changed, exactly

* `tests/test_oddspapi_quota_honesty.py` — 19 insertions, 2 deletions (§3). A
  **test-only** change, outside the nine files the C-gate tracks; it must be
  named in the push report and the PR description.
* Nothing else. No shipped module was touched; the frozen nine-file table and
  the 32-file bundle are unchanged (`sha256sum -c SHA256SUMS.txt` → 32/32 OK).

## 5. Latent observation, NOT fixed (operator's call)

In `scripts/capture_oddspapi.py`, the fixtures-429 handler reads the module
global (`stats["rate_limit"] = rate_limit_diagnostics()`) rather than recording
the exception it just caught. Production is correct today only because the
transport layer records first. If that call ever moves or a caller raises the
429 from anywhere else, the receipt silently loses the quota evidence — the
exact failure the round-2 test was written to prevent. The one-line belt-and-
braces fix would be to call `_record_rate_limit(exc)` in the handler before
reading the diagnostics (idempotent in production, same values). Not applied:
it changes a shipped module outside the reviewed set, the live path is correct,
and the freeze permits only A4 and the push-report items. Recorded here so the
decision is visible rather than silent.

## 6. Cleanup

`git worktree add /tmp/base_quota 8e50de2` (used for the pristine-base proof)
was removed and pruned; `git worktree list` shows only the main checkout.

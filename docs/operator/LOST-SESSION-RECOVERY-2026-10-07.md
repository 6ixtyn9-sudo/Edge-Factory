# Lost session recovery — 2026-10-07

## Summary

The 2026-10-07 handoff instructed the next session to land 12 unpushed commits
(`c55fb51` … `83ab61b`) from `arena/eda5708c-edge-factory`, then complete five
work-order tasks verified by `scripts/verify_work_order.py`.

**Those commits do not exist on the remote and are not recoverable from a
clone.** Everything the handoff depended on — the work order, the open-issues
register, and the verifier — was created only in those commits and was never
pushed. One piece of the lost work has been reconstructed from independent
evidence (see below); the rest cannot be, because the evidence that specified
it was itself in the lost commits.

## Evidence that the commits are gone

Run against a full (un-shallowed) clone with all pull refs fetched:

| Check | Result |
| --- | --- |
| `git cat-file -t c55fb51 / 83ab61b / 75dfd3c / e858897` | `Not a valid object name` (all four) |
| `git ls-remote --heads origin` | `refs/heads/main` only — the source branch was deleted after PR #40 merged |
| `git ls-remote origin` | 42 refs: `main` + `refs/pull/*/head`; none carry the commits |
| `git log --all -- <each missing file>` | 0 commits touching any of them |

The four files named in the handoff have never existed in this repository's
history:

- `docs/operator/WORK-ORDER-2026-10-07.md`
- `docs/operator/OPEN-ISSUES-2026-10-06.md`
- `scripts/verify_work_order.py`
- `docs/_handoff_prompt_2026-10-07_work_order.md`

PR #40 (`arena/eda5708c-edge-factory`) merged at 2026-10-06T06:09Z. The lost
commits were authored after that merge and were never pushed, so GitHub never
received them. A deleted *pushed* branch is usually recoverable via
`refs/pull/*`; never-pushed commits are not.

## What was reconstructed, and on what evidence

Only the SharpAPI origin-credential fix (lost commit `75dfd3c`). It is the one
item whose full contract survives **outside** the lost commits, in operator-
authored comments on `main` (`f6d3444`, `.github/workflows/daily.yml`):

> SharpAPI authenticates TWICE: RAPIDAPI_KEY gets the request through the
> gateway, then SharpAPI's own origin checks X-API-Key separately. […] Set the
> repository secret SHARPAPI_KEY to the SharpAPI key. Unset, the header is
> omitted entirely rather than sent blank.

Corroborated by the production symptom also recorded there: 401 with
SharpAPI's own envelope `{"error":{"code":"disabled_api_key"}}` rather than the
gateway's `{"message":"Endpoint ... does not exist"}` — two services, two error
shapes, so the request reached the origin and the path resolves.

The workflow exported `SHARPAPI_KEY`; no code read it. Confirmed by
`grep -rn "SHARPAPI_KEY" --include=*.py` returning nothing before the fix.

This is a **reconstruction from the documented contract, not a recovery** of
`75dfd3c`. It will differ from the original in implementation detail and test
naming. It has not been exercised against the live provider from here (no
network); the claim that it resolves the 401 is inferred from the provider's
own error envelope, not observed.

## Also fixed, because the above makes it reachable

`parse_snapshot` in the SharpAPI adapter referenced an undefined name when a
market failed canonicalisation, raising `NameError` and aborting the whole
snapshot rather than dropping one row. Unreachable while every request 401'd;
live the moment authentication succeeds. The sibling Pinnacle adapter already
had the correct form, so this was a transcription slip, not a design choice.

Reproduced before the fix:

    NameError: name 'failure' is not defined

## Pre-existing suite failure (not introduced here)

`tests/test_betminer_404_disambiguation.py::test_committed_receipts_are_still_readable`
fails on untouched `main`. A dated failure receipt the operator deleted
(`6bc2c113`) was re-persisted by a later pipeline run (`7a76e298`) carrying a
`provider_message` the test asserts is absent.

This is the WO-2 subject — a failure receipt caching itself and outliving its
own deletion — and it is already costing a red suite. It is recorded here
rather than fixed, because the work order that specified the intended
behaviour is among the lost files.

## What a replacement work order still needs to specify

These were described by title in the handoff but their evidence and acceptance
criteria were inline in the lost document. None should be attempted without it:

- **WO-1 — Pinnacle discards every price.** The adapter requires a
  `markets`/`odds` list of dicts carrying `price`/`odds`. If the provider sends
  a different shape, every row drops. *The actual payload shape is unknown
  here:* there is no Pinnacle ledger in `localdata/` and no retained sample, so
  the real shape cannot be read off the repository. Guessing it would be
  fabrication.
- **WO-2 — Failure receipts cache themselves.** Live symptom above; intended
  behaviour unspecified.
- **WO-3 — Three health labels assert unsupported causes.** Which three is not
  derivable from the repository.
- **WO-4 — Persistent 60-minute kickoff disagreement.** Direction and affected
  source unspecified.
- **WO-5 — Selection-constant guard.** The guard lived in the lost verifier.

## Recommendation

Do not reconstruct `scripts/verify_work_order.py` from the handoff summary. The
operator's framing is that the verifier *is* the contract — "not my judgement
and not yours" — and that checks must not be weakened to pass. A verifier
written by the agent it grades inverts that: "ALL PASS" would then only mean
the agent satisfied checks it authored from the same guesses that produced the
code. The verifier has to come from the operator.

# Regulation-time settlement correction — 28 October 2026

## Confirmed incident

RSD Alcalá–Las Palmas on 27 October finished **1–1 after 90 minutes plus stoppage time**, then **1–3 after extra time**. Standard match 1×2 and full-match goal markets use the regulation score, not the qualification result. Therefore Las Palmas 1×2 and Match Over 2.5 both **lose**. The operator supplied resolved purchased bookmaker slips confirming both losses (R5 stake each, R0 paid each).

Independent evidence retained in `Config/verified_results.json`:

- [Canarias7 live report](https://www.canarias7.es/deportes/ud-las-palmas/rsd-alcala-palmas-partido-goles-resultado-directo-20261027170037-di.html): explicitly ends regulation at 1–1 before extra time begins; the subsequent 95′ and 104′/105′ goals belong to extra time.
- [elDiario report](https://www.eldiario.es/canariasahora/Deportes/futbol/palmas-pasa-copa-prorroga_1_13620328.html): the equaliser sends the match to extra time, where Las Palmas scores twice.

The published shared overlay had exported `bettingclosed_settled` **1–3 / away** without period metadata. Its blob was `15be39650aee39475aa73b2fda5dcc4903958b8c`. Replaying that same bad fact consistently cannot validate the settlement.

## Existing machinery corrected

- Shared regulation-score helpers reject known AET/PEN aggregates, malformed goal pairs, partial explicit regulation pairs, and inappropriate live/terminal scores. Explicit regulation scores can resolve AET/PEN fixtures. Stoppage time remains part of regulation; there is **no simplistic “minute > 90” cutoff** and no guessed subtraction of extra-time goals.
- BetExplorer's live/archive result parsers and Bettingclosed's result-cell parser preserve period markers, including HTML attribute-only markers. Existing backfill/refresh writers retain the metadata.
- Warehouse views, result export, ticket settlement, audit indexing, form archives and Main/ENH historical labels are guarded. Cross-donor and persistent overlay period holds prevent a known aggregate from returning through a higher-priority or metadata-free copy. Squad identities remain distinct.
- Known unresolved regulation facts stay held, rather than turning into an age-based void. Reviewed configuration facts outrank donors.
- Reviewed historical labels apply only to already observed, same-squad fixtures within the requested window and optional review-time bound. They do not fabricate observations or market votes.
- Existing verified regrading now runs for Main as well as ENH, and through the existing grading CLI. It updates the affected leg, accumulator payout, history totals, subsequent closing balances and bank idempotently. Held corrections do not partially mutate legs; a confirmed losing leg can resolve an accumulator even if another leg remains unknown.
- Existing persistence compares HEAD/cache after the same deterministic correction using **only HEAD-committed verified facts**. Cached approvals are not authority; unknown bank/stake/frozen-identity changes still fail the existing checks. This also works with the workflow's direct script invocation, without repository-root `PYTHONPATH`.

No new scripts, services or workflow changes. No staking/selection-policy changes.

## Read-only financial reconciliation

Dry run against both remote state files pinned to main commit **`b6c52d7c67fd1037c623b7d14abb877e62411dd8`**:

| Lane | State blob | Recorded bank before | Projected bank after | Incorrect payout removed |
| --- | --- | ---: | ---: | ---: |
| Main | `878278909ca2cefa71b9db178acc5ae85d6ccfa1` | 358.466335 | **283.0761** | 75.3902 |
| ENH | `b3b2286559fceded2869ccd30c4a25e7899b718e` | 40.348665 | **29.8879** | 10.4608 |

These are **system bank/stake accounting units, not the bookmaker's R5 cash stakes**. Existing regrader rounding is four decimals.

Main's affected accumulator is @2.08, stake 36.2453, previously returned 75.3902; corrected return is zero. The other October 27 Main accumulator and its 65.604 return are unchanged. ENH's affected accumulator is @2.45, stake 4.2697, previously returned 10.4608; corrected return is zero. ENH's recorded 11 wins / 20 losses becomes 10 wins / 21 losses.

Assertions on the real copied states verified:

1. History lengths are identical; **only October 27 changes**.
2. Every top-level value other than `history` and `bank` is identical, including open slips and frozen records. No October 28 draft is resized.
3. A second regrade returns no changes and leaves the entire corrected state identical.
4. The unrelated phantom/unplaced case is not credited, removed or recreated.

**Deployment status:** these were temporary-copy dry runs only. This patch does not replace financial files with stale snapshots. The correction is booked through existing regrade/persistence paths after the reviewed configuration and code are merged and an existing pipeline/grade run executes. No merge or workflow dispatch was performed as part of this fix. Do not describe the live banks as already corrected before that execution is confirmed.

## Validation

Final full suite, after SQL/Python parity hardening:

```text
PYTHONPATH=src:. .venv/bin/python -m pytest -q
4726 passed, 1 skipped in 288.30s
```

Regression coverage includes dotted/hyphenated AET/PEN markers, actual source HTML parsing, stoppage time, separate regulation scores, strict malformed/partial goal pairs, raw SQL/Python agreement, preserved forecasts, donor/overlay bypass, squad separation, hold export round trips, no timeout void, both-lane October 27 regrading, atomicity/idempotence, observed-only/review-bounded training labels, trusted-HEAD cache restoration, unknown-bank rejection, and direct-script imports without `PYTHONPATH`.

`git diff --check` passes. Local production warehouse is unavailable: synthetic warehouse tests and real remote state-copy reconciliation are not a claim of complete production coverage.

## Remaining limits / operator verification

- Missing historical period metadata is **not proof** a legacy aggregate is a regulation score. Known flags are preserved and veto unsafe copies; absent flags cannot be reconstructed automatically. Add independently reviewed regulation facts through the existing configuration when needed.
- After merge and an operator-triggered or scheduled existing run, inspect `regrade_verified` / `regrade_verified_bank` logs and the durable state: affected losses, zero payouts, expected bank delta, preserved unrelated history/frozen identities, and a no-op second pass.
- Do not dispatch workflows automatically, merge without approval, alter staking, or use this correction to rewrite unrelated history.

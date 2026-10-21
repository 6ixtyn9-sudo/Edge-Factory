# Integrity remediation — 21 October 2026

## Status and boundaries

Implemented code corrections, targeted historical recovery and report repairs on `arena/a911e4c0-edge-factory`, based on `56f990fd110cbe8fa857f3a9f51022324ee3de37`.

**Independent second-agent review is pending.** This environment exposes no second-agent invocation tool. The companion [review request](INTEGRITY-SECOND-AGENT-REVIEW-2026-10-21.md) is a handoff, not an executed review or approval.

This is not a production deployment receipt, a newly reproduced historical mining certification, or an exhaustive guarantee that every possible numeric fallback in the repository has been eliminated. No workflow was dispatched; no live source, odds or notification call was made for this remediation; no settlement or ticket resizing was executed. Existing statistical gates, cohort competition, ML freeze, activation boundaries and benches are unchanged.

## ENH financial recovery

The published ENH report had only one settled day and a bank of **114.5%**. The preceding published report contains six settled days and a precise bank of **71.69957599999998%**. Financial state was cache-only and ignored, while its reports were committed. Missing/unreadable state could become an empty dictionary and subsequently a fresh 100% bank. The artifacts establish lost history and the reset hazard; they do **not** establish the exact runner/cache event that originally caused the loss.

Recovery uses the original precise bank, not a recalculation from rounded report rows:

| Component | Percent of original capital |
|---|---:|
| Original six-day bank | 71.69957599999998 |
| Actual Oct 20 stake | 12.5 |
| Actual Oct 20 return | 27.0 |
| Actual later net | +14.5 |
| Recovered bank | **86.19957599999998** |

Restored history covers Oct 14–20: **7 winning / 8 losing accumulators over seven bet-days**. Report display is now **86.2%**, not 114.5%. A rounding residual of `-0.0001240000000279906` percentage points versus summing the rounded daily rows is disclosed, not silently balanced with an invented transaction.

The Oct 21 published open accumulator remains **14.3125% at 2.71**, with Bayern–Arsenal O2.5 at 1.66 and Como–Manchester United O2.5 at 1.63. No stake was retrospectively recomputed against the recovered bank. Unknown historical freeze times are JSON null; recovered date locks prevent rewriting the settled dates or published open ticket. This is a conservative recommendation lock, not a new assertion that the operator placed a bet at an invented time.

Durable evidence:

- `2026-10-21-enh-recovery/before-reset.json`: source report from `ca77539c4d223302496c8b342d0ded4f12cf4e6a`.
- `2026-10-21-enh-recovery/after-reset.json`: report from `bd9277036db86d3f43cf2a46f017742062a1c813`.
- `2026-10-21-enh-recovery/receipt.json`: source SHA-256 digests and reconciliation.
- `localdata/enhancement_tickets_state.json`: recovered durable state and embedded receipt.

The state is now explicitly tracked, writes are atomic, and missing published financial history or malformed/non-finite banks fail closed rather than initializing a replacement bank. Cache restoration preserves reconciled financial extensions, including additional accumulators settled on an existing day. Stale subsets cannot truncate history. Divergent histories, unreconciled bank changes or differing open positions on stale-state recovery stop for investigation rather than silently choosing a version.

## Findings and remedies

| Finding | Implemented correction | Evidence / remaining limitation |
|---|---|---|
| F1: purity ROI and gate populations | Valid finite odds greater than one define both P&L and priced n across all context families; unpriced losses cannot lower priced ROI or inflate sample gates. Reports retain `n_settled` separately. Missing odds columns produce UNKNOWN, not synthetic losses. | Regression: three priced wins plus 36 unpriced losses produce ROI 1.10, priced n=3, settled n=39 and UNKNOWN. Legacy verdicts are held out of selection and veto loaders pending a real re-assay. |
| F2: enhancement retention | Removed record and processed-key truncation; deduplication also checks retained date/match identities. Incomplete ledgers cannot certify or derive data floors. Full price precision is retained for new observations. | Recovered 47 authentic observations; all 16 market entries now have cumulative n equal to retained n. See recovery below. |
| F3: mining input provenance | Existing miner records deterministic query-row digests, source table/count/date coverage and exclusive window; accepted new contracts reference a shared manifest. Incumbent revalidation evidence is separate from the preserved historical baseline. | Digests identify inputs but cannot recreate missing historical bytes. Current historical certification remains explicitly locally unreproduced. No invented historical snapshot or fresh certification is claimed. |
| F3b: exact-contract purity coverage | Assay emits exact-contract availability; the committed registry explicitly marks all current certified contract contexts unverified pending priced-only assay. | Missing source views are unavailable, never mapped to a pooled unrelated context. Complete operational inputs are needed to regenerate evidence. |
| F4: absence represented as zero | New pick writer nulls absent enhancement probabilities, validates selected cohort evidence and stamps build SHA/UTC time. | Immutable retained archives are not rewritten or backfilled with fabricated provenance. This corrects new output, not historical decision-time facts. |
| F5: ambiguous denominators | Audit JSON and human reports distinguish settled hit-rate n, valid-priced ROI n, fixture secondary outcomes and actual enhancement returns. Slice reports disclose retained versus cumulative samples. | These are different populations; percentages should not be interpreted as interchangeable estimates. |
| F6: unidentified observations | Eligible settled probability-source views reject missing/short/equal canonical team identities; scoutingstats also requires both final score fields. | Raw capture remains intact for audit. Identity filtering does not claim that every retained source observation is otherwise correct. |
| F7: duplicate main performance day | Regenerated main report from unchanged state with `--no-settle`; duplicate Oct 11 display removed. Duplicate financial history dates now raise rather than print a misleading ledger. | Main financial state is unchanged. |
| F8: mixed probability scales | Consensus2/3 normalize each complete source vector to percentage units, accepting coherent fractional or percentage sums only. Invalid/nonfinite/out-of-range vectors yield NULL. | Actual warehouse-view test covers 60% versus 0.6 and rejects unidentified rows. Four-way pre-existing guard was not replaced. |
| F9: missing hit rate becomes 100% | Removed missing-rate default; strict finite probability parsing preserves genuine zero and rejects strings, booleans and nonfinite values. Invalid enhancement pool probabilities are excluded. | Regression distinguishes missing from measured zero. |
| F10: build/deployment identity | New pick rows carry their actual Git SHA and UTC build time; deployment facts remain separated from code/test facts. | Last checked Worker deployment is base `56f990fd`, build `fb3e97b3-1185-4d0d-8d5c-59fa9004ff61`, version `59aa325a-452a-47a0-8a6f-5bd5256897a7`. Scheduled Python run `39541618593` used older `bd927703`. Neither proves this remediation ran in production. |

## Authentic registry recovery, not reconstructed outcomes

`match_over_25@v1` retained 400 observations but counted 447. Nine historical GitHub snapshots contain the missing 47. Only those missing records were appended; the existing 400 records retain their original order/content. The receipt includes every recovered record, the source commits and snapshot SHA-256 digests:

`2026-10-21-enh-recovery/registry-record-recovery.json`

Independently recomputed from all 447 records:

- n: **447**
- hits: **293**
- profit: **1.737 units**
- multi-source n: **84**
- inverse-price sum: **292.9454842380397**, versus original stored **292.9454842380396**; only floating-point summation residual.

All original cumulative counters remain unchanged. Historical missing bucket/source detail is still unknown; it was not manufactured. All 16 market entries were checked, not only O2.5. Recovery does not alter market competition or authorize a new market.

## Validation and operational follow-up

Focused frozen-source regression: **139 passed in 19.95 seconds** across integrity remediation, post-Forebet serving, enhancement lane and Phase 5 persistence audit tests. The focused suite includes a deliberately different historical baseline to ensure today's digest is not falsely attached as proof of preserved old statistics. The old ignored-state test was changed to assert durability, not deleted or skipped.

The final full-suite receipt is appended below after the frozen-source run finishes. Every pre-existing top-level localdata file is SHA-256 checked before/after testing to detect test leakage into real financial/report artifacts. Temporary financial tests use scratch lanes and repositories.

Operational closure still requires:

1. An independent reviewer to execute the companion review request, not simply agree with this report.
2. The complete operational warehouse/source history to run a priced-only exact-contract assay and reproduce mining evidence where the required source snapshots actually exist. A hash manifest alone is not the dataset.
3. Normal approved deployment and actual runtime verification of the resulting build. Do not settle/replay historical tickets or dispatch a workflow merely to manufacture a completion receipt.

These limitations are explicit unresolved verification/data dependencies, not replacement numeric values.

### Final frozen-source receipt

`PYTHONPATH=src .venv/bin/python -m pytest -q`: **3607 passed, 0 failed, 0 skipped in 179.35 seconds**. The immutable prelogging baseline commit was fetched without switching branches, so its 300-case parity check ran rather than being skipped. The same process then checked every baseline localdata SHA-256: **no artifact changes**, exit 0. `git diff --check` is clean. The unchanged workflow/main-bank files were checked separately. These are local regression receipts, not an independent review or production run.

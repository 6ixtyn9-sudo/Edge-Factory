# Enhancement payout remediation — 22 October 2026

## Scope

Use the existing cohort resolver, enhancement registry, candidate notes, selector,
audit, replay, and unplaced-ticket reset/rebuild. No new registry, miner, workflow,
calibration model, or staking policy. Main-lane selection is unchanged.

`STAKE_FRAC=.25`, shared `plan_day` / `_stake_weights`, per-acca sizing defaults,
and the two-leg format remain unchanged. Admission can change the number of
qualifying tickets; it does not introduce fixed slots or a different risk cap.

## Corrected evidence contract

- Exact-parent cohort frequency stays in `enhancement_cohort_rate` and the
  descriptive profile. New `enhancement_probability` and note `probability`
  values remain null: no calibrated individual-fixture forecast exists here.
- Candidate generation retains its existing cohort/price eligibility band and
  ordering as a **descriptive shortlist**, not staking permission. Each priced
  alternative carries its own original quote metadata and receipt. Live board
  rendering uses the slip's actual admission function.
- Live admission uses the existing registry's retained records, matched exactly
  on parent contract, parent selection, league, market, named bookmaker, source,
  and quoted decimal price. No price bins, nearest-neighbour fallback, global
  calibration, invented team parameters, or arbitrary price ceiling.
- Matching outcomes need original capture <= decision < kickoff timestamps,
  an earlier fixture date, and a registry recording timestamp before the new
  decision. Missing legacy provenance is not backfilled. Duplicate fixtures do
  not increase n; incomplete or benched ledgers cannot qualify.
- The existing minimum priced sample (30) and Wilson lower endpoint are reused.
  The actual leg price must pay above that lower endpoint's breakeven. This is
  a **context-conditioned historical sample**, not a calibrated fixture model.
- The shared selector compares complete two-leg tickets over all retained
  alternatives before cutting slots. Only same-book/same-source combinations
  qualify; the joint lower bound is `max(0, LB1 + LB2 - 1)`, not `p1 * p2`.
  Its product with the ticket's decimal payout must exceed one. A fixture cannot
  appear twice, including through another market. Unsupported tickets never
  return through the volume fallback.
- Exchange fee/acca terms are absent from the capture contract. Known exchange
  quotes cannot certify net payouts. Fixed-odds prices are not replaced by
  fabricated commission-adjusted prices.
- Existing settlement auditing records the original competing quotes, including
  NO BET days, into the same registry. Existing replay reports current supported
  cards separately from explicitly labelled legacy floor counterfactuals.

These are conservative admission checks, **not proof of future profitability**.
Wilson endpoints describe sampling uncertainty, not fixture calibration,
post-selection simultaneous coverage, or protection against distribution shift.
Exact matching can leave sparse or empty cells; no fallback disguises that gap.

## Actual evidence and current unplaced slate

Read-only audit before operational reconciliation:

- 38 archived parent fixtures; 76 retained priced market alternatives examined.
- 64 alternatives lack qualifying quote-conditioned outcome evidence.
- 12 fail the existing BetExplorer admission-receipt requirement.
- The registry retains 562 priced outcomes; **zero** have the required original
  quote context. Those observations remain useful descriptive history, not
  certified conditional probabilities. No registry refresh or migration invents
  missing fields.
- No supported complete acca. The existing warehouse is absent, so a fresh exact
  parent rebuild is also unavailable. The rebuild path must persist explicit
  **NO BET**, rather than erase the shared main slate or reuse an old ENH card.

The user explicitly confirmed the current tickets were unplaced. Reconcile only
22 October through the existing hash-witnessed reset receipt and rebuild command.
The receipt retains the withdrawn text; state reconciliation retains the removed
unplaced slip. Cancellation is not a loss, return, bank reset, or settlement.
Placed/settled history and main-lane artifacts must remain byte-identical.

## Validation and operating boundary

Before reconciliation: all 863 baseline localdata hashes matched. AST comparison
confirmed `plan_day` and `_stake_weights` unchanged. Real-registry unit tests cover
missing/mismatched/late/duplicate/truncated evidence, actual payout rejection,
full-pool alternative-market competition, non-independent acca rejection, and
unchanged sizing. Lifecycle tests use explicitly synthetic prior quote cells;
they are not evidence of real-world coverage or an edge.

Completed results:

- Full regression suite: **3,792 passed in 175.76 seconds**, before operational
  reconciliation. No incomplete or interrupted run is counted as validation.
- Existing enhancement replay: **0 current supported accas on 0 days**. This is
  an evidence-availability result, not an ROI improvement claim. The legacy
  cohort-parity audit is also explicitly labelled as a historical counterfactual.
- Existing `--enhancements --rebuild-unplaced --date 2026-10-22` completed:
  old unplaced card withdrawn, explicit NO BET persisted, no fresh slate invented.
- Bank remains **80.1656**, all **8** settled-history entries and other accounting
  fields are identical. The removed unplaced entry is retained in the existing
  reset audit; its original ticket text and hash are in the approval receipt.
- **861/863** original localdata hashes remain identical. The only changed
  baseline files are the authorized current ENH ticket and ENH state. The new
  reset receipt is additive. Main-lane state/tickets, prediction data, registry,
  and all historical-ticket hashes are unchanged.

No production workflow dispatch, merge, or independent-agent sign-off occurred.

## Evidence-recovery follow-up (22 October)

The absence of the new registry fields was **not proof that the underlying
archives and captures were absent**. The read-only recovery function in the
existing `audit_enh_market_competition.py` now follows the authoritative
morning/late-addition archive loader, exact predecision API quote rules, and
exact-parent validation. Its report is
`enh-evidence-recovery-2026-10-22.json` beside this note; input hashes and CSV-line
witnesses make the joins inspectable.

Local recovery found:

- All **562** registry fixtures have an archived pick counterpart.
- **75** have an archived matching price, named book and source.
- **23** also have an exact, timely API capture; **16** agree with the retained
  result overlay. These are progressively narrower counts, not new forecasts.
- **6** records have a matching post-Forebet parent archive. Just **one** has a
  linked quote, agreeing overlay and valid exact-parent context: Real Betis–
  Feyenoord, Over 2.5 at Betsson 1.36, contract
  `pfc_d94d447efe0742440e953722`. That contract is not currently active.
- Across the prior post-Forebet candidate pool, **4** quote/parent links were
  recovered. Local independent raw donor scores are unavailable for all four;
  none can be promoted from overlay agreement alone. Historical result
  availability has not been established or backdated.

The existing warehouse builder reconstructed a **77 MB scratch warehouse** from
tracked inputs in 126.3 seconds. Statarea, Zulubet and independent BetExplorer
results are available; ScoutingStats, Vitibet and other untracked current-source
inputs remain absent locally. Forebet/convenience donor tables were not used to
certify recovered results. No warehouse binary or raw export is committed.

### Restored-cache verification completed (supersedes the local access blocker)

The user installed and ran the supplied export workflow on `main`. Run
[39741429582](https://github.com/6ixtyn9-sudo/Edge-Factory/actions/runs/39741429582)
**succeeded**, restoring `localdata-v2-39719907033` (166,070,142 bytes). The workflow
revision was `5c71cf0f3e1fd37d0fe17c51373fb3a0a2cb53e4`; its checkout pinned the
audit code at `c9931ac4a1c2d8913911eef0fb02b16412235fd0`.

The runner built an isolated **99 MB scratch warehouse in 171.2 seconds** and
passed the restored-localdata hash assertion. Unlike the partial local checkout,
the cache contained **11,855 ScoutingStats, 43,825 Vitibet and 19,787 BettingClosed
rows**. These table counts are source availability, not counts of independently
timed betting evidence. The prior claim that the cache audit remained blocked is
superseded; no further permission change or workflow run is required for this
audit.

The cache-backed results were:

- **562** archived fixtures, **75** original price/book/source matches,
  **23** exact predecision quote joins, **16** agreeing result-overlay links and
  **6** matching post-Forebet parent archives.
- **One** registry record passed both the full exact-parent link and independent
  raw-score agreement: the retired Betis contract above. Raw donor scores now
  independently agree on **Betis 1–0 Feyenoord**. The contract remains inactive;
  `result_availability_before_decision` remains unknown, not backdated.
- The archived post-Forebet candidate pool yielded **4** quote-and-parent links;
  **43** attempts lacked a matching valid predecision quote. The largest
  raw-result-backed exact cell was **1**, with `raw_results_checked: true`.

An exact cell here separates contract, parent selection, league, bookmaker,
source, decimal price and enhancement market. This scoped sample is below the
existing minimum of 30; **it does not prove that the warehouse lacks historical
results or that every possible strategy has been mined**. Registry-link counts
also require exact-name overlay agreement, which can undercount links when the
overlay uses different aliases even if a raw result exists. This audit is not a
new probability calibration or exhaustive remine.

The compact actual result was retrieved from check-run **119699310901** via the
GitHub annotations API and is preserved under `cache_verification` in the JSON
report; top-level recovery values retain the earlier partial-local baseline.
The checks API rendered escaped Unicode as invalid backslash-plus-letter
sequences; the recorded normalization removes only those invalid prefixes to
parse the actual JSON, preserving valid escapes and numeric values.
Artifact **12409074644**, `warehouse-inputs-39741429582`, is 3,942,764 bytes with
API-verified SHA256
`79c86861148820b27974d5e42f291088a8acaaea0e7da496482419e53f3993fc`.
Its ZIP has not been downloaded into this agent checkout; cache processing and
verification occurred on the runner. Earlier App permission and external
artifact-download failures remain historical facts, not a current audit blocker.

No daily/production workflow, registry promotion, cache save or operational
rebuild was performed by this audit. No staking, bank or ticket state was changed.

All **864 operational files** matched their pre-recovery hashes. No bank,
settled history, registry, picks, current NO BET, price capture, or prediction
CSV was changed. No selection threshold or staking rule was relaxed.

Recovery validation: **3,798 passed, 1 skipped in 166.02 seconds**. A prior
registry version at commit `f0544f5846bc99c7d65f0b34d824f0ccc39e7732` also retains
the Betis losing outcome at 1.36. This is an additional content witness, not a
claim that a commit timestamp proves publication time or independent score
origin. No historical availability field was backdated.

## Daily restore failure follow-up (run 39742606419)

The daily run stopped before its main pipeline at `_retain_financial_state` with
`divergent enhancement financial histories`. This is separate from the successful
read-only cache audit above. The subsequent always-run Phase 5 explanation and
artifact upload do not mean the daily pipeline succeeded or trained a model.

The cache key was created on 22 October at 05:26:11Z. Its producing run's Git
snapshot, `54acbcea0bbda022005886d398bf6b5775517798`, contains bank
110.67395099999999 and an incorrect 21 October Bayern/Como settlement. Correction
`ed5db57e2315f3fc81a9375b7c5594f8cbd5ea8e` restores the placed Japan-ticket
settlement and bank **80.1656**. Commit
`c623c0830c5f300a3667dc9b8ee695a09dc0b393` subsequently withdraws the
operator-confirmed unplaced 22 October card. Neither history is an append-only
extension of the other, so the original guard deliberately rejects it.

The existing `integrity_recovery` metadata now contains an exact cache
supersession receipt. The existing persistence helper may restore committed
state only if **both** the superseded cache and retained HEAD financial hashes
match that committed receipt. Each fingerprint binds base, bank, cycle base,
full settled history, events, full open positions and freeze locks. Descriptive
floor metadata is excluded. A cached receipt is never trusted. An unknown bank,
leg, stake, settlement, position or lock still fails closed, retaining the cache
for artifact inspection. Existing append-only ledger/bank checks are unchanged.

Validation:

- Historical replay in an isolated temporary Git repository: restoring the
  producing run's committed snapshot recovered the exact current state bytes,
  bank **80.1656**, **8** settled days and **no** open slips.
- **49** targeted tests passed, including 15 new supersession cases covering
  acceptance, unknown financial/position/lock changes, receipt provenance and
  descriptive metadata.
- Full suite: **3,814 passed in 181.15 seconds**. This is not a live-run success.
- **863/864** original localdata files remained byte-identical. The only changed
  file is ENH state, adding the receipt; its financial fingerprint, bank, history,
  positions and locks are unchanged. The empty test-created usage lock was
  removed. No ticket, prediction input, registry or staking code changed.

The failed run's artifact could not be downloaded from external storage. Thus
this repair is verified against the producing run's Git snapshot, **not against
uninspected cache bytes**. A different actual fingerprint remains an error and
is now included in its diagnostic. No cache deletion, workflow edit, production
dispatch, new settlement or automatic merge was performed. Runner-side recovery
is not yet witnessed; after merge it requires a **new main-branch run**, not a
rerun pinned to the old failing checkout.

## Runner restore verified; null event-note display failure (run 39746363896)

The new main-branch run at `ec75c73939f9045f7fb279264f06016f32c29734`
**passed financial restoration** (861 tracked files restored; Phase 5 ledgers
unioned) and `history_completeness_verified`, then completed warehouse build,
mining, decay and purity assay. This supersedes the earlier statement that the
financial restore repair had not yet been witnessed on a runner. The overall
run nevertheless **failed**, not succeeded:
https://github.com/6ixtyn9-sudo/Edge-Factory/actions/runs/39746363896.

`picks_today.print_buckets` still formatted `event_notes[].probability` using
`:.1%`, although current notes intentionally store null there. Descriptive
`cohort_rate` is separate and must not fill that missing fixture forecast. The
daily TXT report contained the same assumption (caught and silently returning
no report). Both now use a small shared formatter in the existing util module.
For example: `Match Over 2.5: fixture probability unavailable; descriptive cohort
rate 59.1% (n=3022)`. Finite legacy probabilities, including observed zero, are
labelled **recorded probability**, not certified forecasts. Malformed/missing
values have no numeric stand-ins. Cohort sample size is shown only when supplied
as a positive integer. The TXT report now actually includes the event-note text
it previously computed without appending; vetoed rows retain their shadow label.

Validation: **82 targeted tests passed**; full suite **3,834 passed, 1 skipped in
152.93 seconds**. There are 21 new cases, including both renderers with current
null notes, missing fields, finite legacy zero, invalid values, shadow labelling
and nonmutation of input evidence. All **864 operational files** remained
byte-identical; the empty test-created usage lock was removed. No admission,
staking, financial state, registry, price or ticket changes. No production run
was dispatched, and end-to-end runner completion remains unverified for this
new rendering fix. Provider failures, sparse quote joins and alias warnings in
the log are separate issues, not repaired or hidden by this display change.

## Cold-start correction — operator instruction, 22 October

**This section supersedes the exact-price-cell admission policy above.** Those
sections remain a record of the earlier implementation/audit, not the current
rule. Production run [39751440277](https://github.com/6ixtyn9-sudo/Edge-Factory/actions/runs/39751440277)
completed successfully on `294c3949afad732882b97db03c24894348c96463`:
financial restore and the null-probability rendering repair are runner-witnessed.
Its ENH NO BET was an admission result, not a failed pipeline.

The prior policy required 30 historical outcomes simultaneously matching the
parent, selection, league, market, bookmaker, source and **exact decimal price**.
Authentic quote capture on NO BET days could theoretically populate those cells,
but no viable bootstrap time or real-world complete-card coverage was shown.
Treating that as an ordinary data shortage was wrong: the admission change
itself fragmented usable existing cohort history into effectively empty cells.

### Corrected existing machinery

- The same exact-parent, all-outcome, pre-date cohort with **n >= 100** supplies
  historical market frequency. Active-contract generation and absence-of-model,
  Forebet, inherited or winner-only fallback remain unchanged.
- `enhancement_cohort_evidence(..., priced=True)` now attaches a validated
  **current** quote and the existing Wilson lower endpoint of that cohort.
  It does not read the priced registry for permission, require any placed bets,
  or condition history on bookmaker, league or exact odds. Original priced
  outcomes remain in the existing registry for realized ROI/audit purposes.
- Rates already persist at four decimal places. The bound uses the **lowest
  integer hit count compatible with that rounding** and the supplied n. An
  impossible rate/count combination cannot authorize a payout. This lower
  compatible count is labelled `cohort_min_hits`, not an observed priced count.
- Evidence is labelled `cohort_payout_bound`, with `cohort_lower_bound`; there
  is no `conditional_rate` or invented `priced_n`. Fixture forecast fields stay
  null. Historical cohort rate still drives ranking, not claimed calibration.
- An actual price must clear the existing minimum and satisfy
  `cohort_lower_bound * odds > 1`. Full-pool competing two-leg tickets retain
  the same-book/source, distinct-fixture and non-independence checks:
  `max(0, LB1 + LB2 - 1) * odds1 * odds2 > 1`. No threshold was reduced to force
  today's card. Existing cohort rate band, staking and accumulator format stay.
- Current quote provenance still must establish named bookmaker/source and
  `capture <= decision < kickoff`. Rejection receipts, exchange restrictions,
  source policy, kickoff/result guards and financial integrity are not bypassed.
  `invalid_execution_quote_context` replaces the misleading historical-cell
  rejection for absent/invalid current quote context.
- Live board and replay use the corrected shared resolver. Selected market/book
  identity survives planning so an alternative with the same `over`/`under`
  selection cannot overwrite the winning market's evidence during carry.
- Fresh normal NO BET results now overwrite stale TXT reasons, without opening
  a position or freezing the date. A later qualifying run may still build a card.
  This fixes why the committed TXT continued saying “warehouse unavailable”
  after the successful runner reported 76 historical-cell rejections.

This is a **cohort-based payout policy**, not evidence that the cohort frequency
is a calibrated conditional probability for today's fixture or quote. Applying
it assumes the exact-parent cohort is relevant to the new fixture. Wilson
sampling uncertainty does not cover drift, market-selection bias, calibration,
or all uncertainty from transporting that cohort. The pair screen does not
claim simultaneous 95% coverage or guaranteed positive future returns.

### Actual captured-slate check, not just favourable unit fixtures

Read-only GitHub `main:localdata/picks_today.json` snapshot:

- Git blob `3fd9e9d8a556d4b4d9ed9b13588f011f13e1c757` (1,256,646 bytes).
- SHA256 `e0c70933020b63675a409cbc63f1e1fb9a6dfdeb869a5c992b12f98901fe1723`.
- **38 rows / 76 market evaluations**. Original resolver: **0 eligible**.
- Corrected resolver: **6 eligible**, **17 payout-not-supported**,
  **53 invalid current quote contexts**. Missing original capture/kickoff fields
  were not reconstructed from results or filled from another quote.
- **0 complete supported accas**. Only Pafos–Riga O2.5 @1.81 and
  Lech Poznań–Sunderland O2.5 @1.88 form an eligible, distinct-fixture same-book
  pair (LeoVegas SE / theoddsapi). Their cohort lower endpoints are
  0.5736982610 and 0.5471583190. The retained pair lower screen is
  **0.1208565800 × 3.4028 = 0.4112507705**, below 1. No independence product
  was substituted to get a bet. Other eligible markets included match unders;
  this was not an Over-only comparison.

This checks the **captured** slate's admission, not executable prices now:
current kickoff/result timing was not applied, nothing was placed/rebuilt, and
no ROI improvement is claimed. It proves removal of the blanket history gate,
not that today's slate ought to pass the remaining ticket checks.

### Validation and deployment boundary

- **238 targeted tests passed**, followed by **135 integration/cohort/lifecycle
  tests passed** after adding the full-chain bootstrap regression.
- Final full suite: **3,845 passed, 1 skipped in 176.40 seconds**.
- A new integration test uses the real contract resolver, synthetic settled
  source rows, real temporary quote CSV/price join, candidate generation, live
  leg admission and complete acca selection with **no priced registry at all**.
  Separate tests retain rejection of insufficient payouts, missing/bad quote
  timestamps, model evidence, same-fixture pairs and unsupported dependence.
- Removed the artificial all-win historical-price seeding helper from existing
  lifecycle tests. Their explicitly synthetic cohort is now what supports their
  cards; these tests are not production profitability/coverage evidence.
- `_stake_weights` AST is identical. `plan_day` AST is identical outside the acca
  metadata construction that retains selected market/book; all sizing arithmetic
  is unchanged. Tests compare baseline and ENH stake percentages.
- All **863 remaining operational files** are byte-identical. The only planned
  operational deletion is the user-named
  `localdata/autobets_enh_tickets_2026-10-22_reset.json`; no bank, settled
  history, open position, price archive, registry or ticket is rewritten here.

No production workflow dispatched, no independent-agent sign-off, and no
runner-witnessed deployment of this new admission correction yet. The earlier
successful run validates the prior restore/render fixes, not this change.

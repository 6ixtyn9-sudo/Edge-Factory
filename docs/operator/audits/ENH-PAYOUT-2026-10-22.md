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

## Accumulator veto removal — operator instruction, 22 October

**Supersedes the remaining hard joint-payout veto in the preceding section.**
The operator explicitly requested action after the cold-start correction still
left all real complete tickets blocked. The Fréchet expression
`max(0, LB1 + LB2 - 1) * combined_odds > 1` is removed from live/replay selection,
not replaced with a fabricated independence product or joint probability.
Unknown dependence is no longer treated as measured worst-case dependence.
This restores accumulator operation, **not a claim of positive joint EV**.

Existing machinery and retained boundaries:

- Individual cohort-backed leg payout admission, n >= 100, source/book/quote
  receipts and timing checks are unchanged. No new market threshold or model.
- Within each executable bookmaker/source group, the shared ranked order,
  `dedup_fixture_legs` and `pair_legs` recipe build complete two-leg tickets.
  The configured barbell/consecutive setting is honoured. Complete candidates
  compete in the existing leg-ranked order, not an invented joint-return score.
  Selection repeats on unused fixtures; alternatives in other book/source
  groups remain available until a ticket is selected. Source-specific quote
  alternatives are no longer prematurely collapsed in initial deduplication.
- Same-fixture exposure within/across tickets, mixed-book/source tickets,
  missing cohort provenance and singles remain disallowed. A valid source pair
  can replace a higher-ranked alternative that has no compatible partner.
- `plan_day`, `_stake_weights`, `enhancement_legs`, `apply_enhancement_timing`
  and `upsert_slip` are AST-identical to the pre-change versions. No staking,
  financial lifecycle, placed-ticket or settled-history change.
- Fresh NO BET explanations no longer imply rejection by a joint-payout model.

Actual captured-slate comparison uses the **same** 38-row Git blob
`3fd9e9d8a556d4b4d9ed9b13588f011f13e1c757` and SHA256
`e0c70933020b63675a409cbc63f1e1fb9a6dfdeb869a5c992b12f98901fe1723`:
individual verdicts stay **6 eligible / 17 insufficient leg payout / 53 invalid
quote contexts**. Complete tickets change **0 -> 1**: Pafos–Riga O2.5 @1.81
and Lech Poznań–Sunderland O2.5 @1.88, LeoVegas (SE)/theoddsapi, combined
**3.4028**, displayed **3.40**. No operational rebuild/placement or present-time
quote/result validation was performed; this is a captured-slate comparison.

Validation: **3,851 passed, 1 skipped in 182.49 seconds**. Regressions cover
real captured rate/count/price inputs admitting that pair; shared barbell and
consecutive pairing parity; unchanged stake percentages; same-fixture,
book/source compatibility and source-alternative rescue; plus existing lifecycle,
freeze, settlement, provenance and insufficient individual-payout checks.
The early-loss lifecycle test now pins scores to the restored barbell pairing
rather than the removed joint-veto selector's consecutive pair order.

The existing `replay_harness.py --enhancements` completed, but its current-policy
historical reconstruction still yields **0 accas on 0 days** because usable
archived predecision evidence is missing. Legacy floor comparisons are explicitly
counterfactual. **No historical ROI improvement or validation of the near-miss
hypothesis is claimed**; no hindsight line substitutions were promoted.
All remaining operational files are byte-identical (empty test lock removed).
No new registry, pipeline, workflow dispatch or independent-agent sign-off.
This correction still requires merge and a new production run to be witnessed.

## Full goal-market wiring, including BTTS — 22 October

The operator challenged the repeated O2.5 recommendation and required match,
home and away totals **and BTTS Yes/No**, not just a demonstration that the
previously retained pair can pass. The captured O2.5 pair is **not established
as the best card across adequately captured competing markets**.

Confirmed defects and corrections in the existing machinery:

1. Six generated, measured team markets had no `MARKET_PRICE_MAP` entry:
   **home/away Under 0.5, Over 2.5 and Over 3.5**. Add the corresponding existing
   `tt_home_*` / `tt_away_*` slots; no new market statistics or probabilities.
2. TheOddsAPI parsed standard `team_totals` but ignored
   `alternate_team_totals`. Both now use the same participant-aware parser.
   The default retained point list now includes **0.5**, not only 1.5–4.5.
3. The workflow's fallback request was only `h2h,totals,team_totals` and the env
   example only `h2h,totals`. Neither asked for the alternate match ladder or
   BTTS. Module and example are corrected; the workflow change is explicitly
   pending manual apply because the GitHub App cannot push workflow edits.
   The required request is
   `h2h,totals,alternate_totals,btts,team_totals,alternate_team_totals,double_chance`
   and point list `0.5,1.5,2.5,3.5,4.5`. Keeping 1.5 in a parser allowlist did
   **not** make a standard-totals request fetch the alternate line.

The old workflow narrowing was intentional credit rationing, not proof that
alternate markets did not exist. This operator-requested expansion removes that
code/workflow divergence once manually applied. The env audit records both
settings as PENDING_WORKFLOW_APPLY, not ACCEPTED credit-rationing exceptions.

**Budget tradeoff:** existing monthly limits, key rotation, attempts cooldown,
first/close snapshot schedule and source admission policies are unchanged.
The existing estimator counts each requested market: the broader default is
**7 estimated credits per event at one region**, versus the old workflow's 3.
It can therefore cover fewer fixtures inside the same cap. This is not a free
coverage claim, a budget increase or authority to retry already-captured games.
Explicit `ODDS_API_MARKETS` / `ODDS_API_TOTAL_POINTS` secrets/env overrides still
win; a deliberately narrow existing override must be updated separately.
Provider/plan support and actual returned coverage remain runner-unverified.
No paid requests were made here.

### Read-only real-data trace

The existing `scripts/audit_enh_market_competition.py` now accepts:

```bash
EDGE_FACTORY_ENH_BOARD=1 EDGE_FACTORY_ODDSPAPI_PRICES=1 \
python scripts/audit_enh_market_competition.py --wiring --day 2026-10-22 \
  --picks PATH_TO_ORIGINAL_CAPTURED_SLATE --out PATH_OUTSIDE_LOCALDATA
```

It traces all **26 cohort-backed markets**: match O/U1.5–4.5, home/away
O/U0.5–3.5 and BTTS Yes/No, with raw store counts, matched current-store quotes,
recorded candidate reasons, retained notes and stored individual-leg verdicts.
It reuses the existing price loader/join and live admission, records input
hashes, leaves absent stores/evidence null, and never rebuilds evidence or writes
operational state. A current-store price is not labelled betting permission.

Against the same 38-row snapshot and raw stores, verified against main Git blobs
`ecab0d5f229000b40d9e66f4ce6f61cb759ffeda` (TheOddsAPI) and
`52d688a49091fee9a02e5ac6803cf5e901d8e0da` (OddsPapi):

- TheOddsAPI's day rows are **1,035 1X2 + 328 O/U2.5**, with no other market.
- OddsPapi has **98,653 rows across 28 fixtures**, including the broader team
  ladder. This does not establish coverage of every fixture in the slate.
- Match O1.5 has matched store quotes on **8/38** fixtures; **0/8** meet 1.30.
  U1.5 has 8 above-minimum prices, but all 38 recorded cohort rates are below
  the existing candidate band. These are captured-store findings, **not a claim
  that no bookmaker offers qualifying 1.5 prices**.
- Most team-total slots match quotes on **6/38** fixtures (home U3.5: 5/38).
  For each usual team slot, 22 lookups lack a matching market/timing witness and
  10 have no fixture quote in the index. "Unpriced" was not a measured defeat
  by O2.5 in an adequately priced competition.
- BTTS Yes and No each have **3 matched, above-minimum quotes** from BetExplorer
  and **3 retained notes**. All six stored leg evaluations fail the individual
  cohort-payout check, not a missing BTTS mapping. The remaining fixture BTTS
  lookups lack usable quotes. BTTS statistics, quote availability and permission
  remain separate facts; no forced BTTS switch was added.

Fixtures sharing a parent contract/selection may share the cohort rates; those
are not team-specific calibrated forecasts. Restricted pricing can then make
one market repeatedly win. The fixes do not invent a new team model to disguise
that limitation. Existing rate bands and individual payout checks are unchanged.

Validation includes all **26 market paths** from an offline provider payload,
through actual CSV serialization, price index, real settled-cohort resolver,
candidate notes and complete same-book acca. It verifies that each market can
win over the competing O2.5 input when its genuine synthetic evidence/ranking
supports it, with null fixture forecasts. Tests also bind workflow/example
request defaults to module defaults (or explicit pending manual deployment), retain explicit line restrictions and
credit accounting, and check that the wiring audit makes no operational writes.
Initial wiring targeted set: **192 passed in 10.37 seconds**. These synthetic tests prove
wiring, not coverage, near-miss recovery or future profitability.

Repository secret-name inspection was denied by the integration (HTTP 403).
No secret was read or modified. Thus absence of a narrow deployed override is
**not verified**; changing a fallback alone cannot override an existing secret.

Pre-push wiring validation with the proposed aligned workflow:
**3,888 passed, 1 skipped in 179.28 seconds**; **259 targeted tests passed**.
The push was then rejected for missing `workflows` permission. The workflow
file is restored unchanged, and the existing audit explicitly records the two
pending manual settings. No claim of an applied workflow correction is made. All **863 operational files** remain byte-identical;
only an empty test-created usage lock was removed. No staking, financial state,
settled history, open position, registry or ticket was rewritten. No production
capture, workflow dispatch, independent-agent sign-off or merge was performed.

### Required manual workflow apply

The GitHub App rejected the workflow-bearing push, so this PR carries the code
and mappings but **does not modify `.github/workflows/daily.yml`**. Replace only
these two env entries in that existing workflow (retaining indentation):

```yaml
ODDS_API_MARKETS: ${{ secrets.ODDS_API_MARKETS || 'h2h,totals,alternate_totals,btts,team_totals,alternate_team_totals,double_chance' }}
ODDS_API_TOTAL_POINTS: ${{ secrets.ODDS_API_TOTAL_POINTS || '0.5,1.5,2.5,3.5,4.5' }}
```

Any explicitly configured narrower secrets must also be updated securely by the
repository owner; their presence/value could not be inspected here. Do not post
credentials. Once the workflow values agree, remove their two
`PENDING_WORKFLOW_APPLY` entries; the existing stale-entry test enforces that
cleanup. Parser/mapping fixes can be reviewed independently, but broader capture
is **not deployed** merely by merging this code-only PR.

## Manual workflow applied; remove stale pending entries (run 39768911859)

The new run checks out `20360c20911202312532766402d8338d92ee9184`, with
expanded market and point workflow fallbacks matching the code defaults.
Its separate **Regression tests (flag, never gate)** job reports **2 failed,
3,886 passed, 1 skipped**. Both failures correctly detect that
`ODDS_API_MARKETS` and `ODDS_API_TOTAL_POINTS` are still listed in
`PENDING_WORKFLOW_APPLY` despite the manual step being complete.

Remove only those two stale pending entries. Do not weaken the stale-entry or
workflow/code agreement tests, move the entries into ACCEPTED, or change any
market, price gate, budget, staking, freeze or financial history. The actual
configured secret overrides remain uninspected; matching fallback expressions
alone do not prove a secret is absent or aligned.

Verification: **49 targeted tests passed**; `audit_env_drift.py --strict`
reports **zero pending and zero unreviewed** divergences. At investigation time
the production `run-autonomous-agent` job was independently in progress in
`Execute Autonomous Smart Schedule`; this regression failure is not evidence
that ENH generation or the production job failed. No cancellation, dispatch,
financial-state rewrite or workflow edit was performed by this cleanup.

Full cleanup regression: **3,888 passed, 1 skipped in 183.93 seconds**.
All **863 operational files** remained byte-identical; the empty test lock was
removed. Runner-side validation of the cleanup requires a new checkout after
merge; rerunning the old failing job retains its old pending entries.

## Scope-aware capture repair after production completion

Run `39768911859` completed production successfully and persisted a nonempty
ENH slip frozen at **14:12 SAST**: Pafos–Riga O2.5 at 1.81 and Lech–Sunderland
O2.5 at 1.88, LeoVegas (SE)/TheOddsAPI, stake 10.0207% of capital. This
supersedes the earlier NO BET/unfrozen observation, not the historical fact
that NO BET itself creates no lock. The saved quotes were captured around
00:24 SAST. This result does not prove fresh, exhaustive market competition.

The capture log shows 23 fixtures skipped as priced, 13 on retry cooldown and
two already started. The existing planner treated any quote as sufficient
regardless of the requested markets/retained point lines. OddsPapi separately
reported its daily allowance exhausted; neither an allowance increase nor a
cooldown bypass is authorized here.

Repair the existing TheOddsAPI attempts ledger/planner, not a new pipeline:

- Record a deterministic request/parser scope for markets, regions, retained
  total points and bookmaker filters. Order changes alone are not new scope.
- A previously priced fixture with old/unknown scope becomes due once for the
  current scope, subject to existing kickoff guards and failure cooldowns.
  The normal provider fetch retains its existing budget enforcement.
- Only returned fixture/date-matching rows stamp success and scope. Empty,
  aborted and unprocessed partial-batch fixtures get failure cooldowns, never
  fabricated first/close success. Preserve prior successful records.
- A scoped response need not contain every requested market. Record the
  request as scoped success if it returns prices; do not repurchase forever
  just because BTTS or team totals were unavailable. Request scope is not a
  provider-availability or qualified-coverage claim.
- Include requested markets/point lines and scope in the existing capture
  receipt. Keep the final pricing pass's predecision timestamp cutoff.

Correct only the ENH renderer's deployment percentage to sum of actual planned
stakes divided by the available bank. A single shared-recipe acca is 12.5% of
free bank, not the 25% daily allocation setting. Stake calculations, selection,
financial records and saved/frozen ticket bytes are not changed. A saved frozen
slip remains write-once and is not rewritten merely to correct its old footer.

Targeted planner, production-entrypoint, parser, orchestration and ENH lane
verification: **151 tests passed** (offline, mocked provider calls). Includes
one-time scope upgrades, canonical scope identity, both failure cooldowns,
kickoff protection, partial/empty/aborted fetches and actual deployment display.
No workflow edit, provider request, dispatch, freeze reset or financial write.

Final full regression: **3,898 passed, 1 skipped in 155.29 seconds**. All **863
tracked operational files** verified byte-identical before/after tests.

## 23 October follow-up — unplaced-record removal and simulation feasibility

The operator reversed retention of today's withdrawn, unplaced recommendation.
Its old slips/freeze/supersession payload has been removed from today's reset
marker. Only the receipt digest, approval time and unplaced confirmation remain
for stale-cache invalidation. The existing reset path no longer copies withdrawn
recommendations into new markers. Disposable repair scratch copies were deleted.
Prior Git commits were not rewritten. Other dates, settled history, bank, staking
and today's replacement card were not changed by this follow-up.

An offline feasibility check inspected **129 dated picks archives** and reused
`replay_harness.enh_day_growth(..., supported=True)`; no provider calls or workflow
runs. Only **21/22 October** contain completed-date exact-contract cohort notes
(116/78). The 21 October freeze timestamp is unavailable. On 22 October, **13 of
38** contract rows were built by the recorded 14:12 SAST freeze; their **44** notes
all fail executable quote-context validation, even with sample/rate eligibility
relaxed in memory for this diagnostic. The other **25** rows were built later and
cannot establish what was selectable at the original decision. No missing quote
timestamps or decision clocks were invented. All operational files were hashed
before/after this read-only check and were unchanged.

The retained registry has **578 priced completed records, none with
`price_context`**; supported replay therefore forms **zero admissible accas**.
This is an evidence gap, **not** measured zero return, losses, or proof that the
live lane cannot bet. The two completed note sets also have minimum cohort n of
178/142: they cannot demonstrate coverage gained by reducing minimum n to 30.
No threshold-profitability sweep or "optimal" setting is justified by these
inputs. Current 60–90% / n>=30 / Wilson-lower-bound-times-odds >0.8 settings remain
provisional and unchanged. The 0.8 screen does not prove positive expected value;
cohort rates are not calibrated fixture or joint accumulator probabilities.

A useful comparison needs authentic predecision candidate snapshots, their
witnessed quotes and resolved outcomes across a substantially broader period,
including rejected candidates. Reuse the existing selector/replay, fix two-leg
pairing and staking, compare eligibility thresholds chronologically, and judge
held-out growth, drawdown, betting frequency and sample size together. Do not
select a winner from missing contexts, selected-only cohorts or later builds.

### 2026-10-23 cache regression repair

Run `39957621669` restored cache `localdata-v2-39915917068` and pushed
`5ec19be`. Settled history and bank reconciled, but the first cache-extension
branch did not compare open positions or freeze locks. It resurrected withdrawn
positions while leaving the approved printed card unchanged.

Repair restores only October 23 open positions, freeze and minimal approval
marker from `ce3f4cc4f455e5df49136e6a00af2568836d531f`. Bank, settled history,
stakes, other dates and the printed replacement card are unchanged. The deleted
standalone reset receipt is not recreated; no withdrawn ticket payload is added.
The existing hash-only cache-supersession mechanism binds the regressed financial
snapshot to this exact repair. Unknown cached positions still fail closed.
The guard now verifies full positions, locks and cycle state before either ledger
extension path, and preserves committed approval metadata. Financial changes in
older caches without an exact receipt require investigation, not automatic choice.

Validation: 72 targeted tests passed; full suite 4260 passed, 1 skipped
(184.60s). Actual-state isolated Git restore checks retained the approved state
for both the exact withdrawn snapshot and repaired snapshot, and refused an
unknown selection without modifying its evidence. Performance reports rendered
with `--lane enh --no-settle`; no selection, settlement, provider capture,
workflow dispatch, cache deletion or bank reset performed by this repair.

### 2026-10-23 older fallback cache: exact published-snapshot recovery

Run `39983064456` checked out repair merge `60cec03`, restored
`localdata-v2-39897962348`, and failed closed before the daily pipeline.
The reports artifact (`12514785690`) download was attempted but unavailable
in this environment; its cached financial snapshot was NOT inspected directly.

The cache-producing run `39897962348` succeeded and published state in commit
`8a252dc36783c4e70a9d769693ff327af27f2301`. That authenticated Git snapshot
has exactly the same bank, base, cycle, events and settled history as the repair;
only October 23 has an obsolete open draft and different lock/approval state.
Other-date positions and locks match. There is no financial update to recover
from that published snapshot. This is not a claim of lifetime history completeness.

Update only the existing hash-bound supersession receipt to authorize that exact
published financial fingerprint:
`312474ab96fc062a59e78fb82eb695378c3dcf5844ccda3c18244c43885bd1a9`.
The retained fingerprint stays
`10277496612cc5a0e59c6de6868e7ceb05a2c57443fea97533a47199735ffe60`.
No guard/code change, hash wildcard, cache-prefix exemption, withdrawn payload,
new financial ledger or standalone reset receipt is added. This replaces the
previous exact source authorization; it does not allow arbitrary earlier caches.

Validation: 72 existing targeted tests passed (2.72s). Isolated temporary Git
checks using the published source and current repair accepted the exact source,
kept the repair idempotent, and refused seven bank/history/market/selection/stake/
freeze/forged-cached-receipt variants without modifying their evidence. All
operational finance and other recovery metadata remain unchanged. Full suite
not rerun for this receipt/documentation-only change.

Runtime recovery remains unconfirmed: the restored cache must have exactly the
published financial fingerprint above. If its pre-push snapshot differs, the
existing guard will still stop; obtain the artifact state rather than authorize
an unseen difference. No cache deletion or workflow restart was performed.

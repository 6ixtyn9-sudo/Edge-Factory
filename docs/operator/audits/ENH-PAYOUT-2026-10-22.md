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

The latest listed main-branch cache is `localdata-v2-39719907033` (166,070,142
bytes). Its contents have **not** been recovered: external artifact download
failed, pushing the existing export workflow's read-only annotation step was
refused for lack of `workflows` permission, and dispatching even the unmodified
exporter returned HTTP 403, `Resource not accessible by integration`. The
annotation step remains a local, unpublished workflow edit. No daily/production
workflow was dispatched. GitHub connection permissions must be updated before
claiming a completed cache audit.

All **864 operational files** matched their pre-recovery hashes. No bank,
settled history, registry, picks, current NO BET, price capture, or prediction
CSV was changed. No selection threshold or staking rule was relaxed.

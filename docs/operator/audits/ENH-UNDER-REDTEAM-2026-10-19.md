# Enhancement unders: red-team report

> **Policy supersession, 19 October:** the operator subsequently authorized broader cohort competition ON by default. See [current disposition](../REALIZED-STATS-UNDERS-2026-10-19.md). The default-off recommendation below is historical, not the current code default. No demonstrated ROI uplift remains the statistical finding; numerical receipts have been refreshed for current code hashes. The replay P&L defect identified below is now fixed.

**Date:** 2026-10-19 · **Verdict: NOT VALIDATED — DO NOT PROMOTE**

The proposed selection expansion has **not demonstrated an ROI improvement**.
Keep the display fix; default to the incumbent selector. Do not lift the
handover's enhancement betting hold. No new forward preregistration, stake
change, EV gate, or deployment was adopted.

## 1. What the handover required

Read the handover's cohort design (Addendum 17), earlier EV-selection experiment
(8 August), calibration caveat (12 August), and 19 October ROI measurement and
standing constraints. The later repository heading dated 23 October is not
independent future evidence as of this audit's date.

Load-bearing lessons:

- Winner-conditioned descriptive stats cannot be probabilities for betting.
- Honest calibration does not itself create value; no invented historical odds.
- Stored outcomes and stakes establish ledger performance, not unlocked cards.
- Counterfactual replays are relative diagnostics, not actual placement records.
- Same-input A/B needs different cards before it can claim a measured effect.
- No band/cap/bucket/stake changes from favourable subsets; enhancement hold stands.

## 2. Actual retained enhancement ledger, 14–18 October

Source: `localdata/autobets_enh_tickets_performance.json`, not a recreated card.

| Measurement | Value |
|---|---:|
| Settled bet-days | 5 |
| Settled accumulators | 13 (6 wins / 7 losses) |
| Stakes, percentage points of original capital | 111.8088 |
| Returns, same units | 93.7513 |
| Net, same units | −18.0575 |
| **Stake-weighted ROI: returns / stakes − 1** | **−16.15%** |
| Flat, equal-stake accumulator ROI | −2.46% |
| Reported bank | 81.9424% of starting capital |
| Exploratory day-block bootstrap 95% interval for stake-weighted ROI | −79.10% to +58.78% |

Bank change (about −18.1% of original capital) is **not** stake-weighted ROI.
The bootstrap resamples the five dates, not 13 supposedly independent accas;
it is extremely weak with five blocks and is not validation. Two accas lack
leg identities; no bookmaker placement receipts are verified. These are stored
software-ledger figures, not independently proven actual bets.

## 3. What could actually be compared

Read-only audit window: 14–18 October. **No refit on today's warehouse.**

| Coverage check | Count |
|---|---:|
| Archived parent rows | 130 |
| No archived all-outcome cohort rates | 49 |
| Snapshot within 30 minutes of kickoff or already started | 1 |
| Retained cohort snapshots | 80 |
| Snapshots with any strict captured quote | 19 |
| Under-market rates inside the existing probability band | 220 |
| Under-market quotes clearing 1.30 | 24 |
| Under candidates newly admitted by relaxed filters | 22 |
| **Fixture selections changed by the proposal** | **0** |

These are fixture/market candidate counts, not 22 new bets. Higher-rate incumbents
still outranked the newly admitted candidates on the available boards.

For both arms, quotes must have exact full-name, same-orientation identities;
a zoned capture timestamp at/before the archived decision and strictly before
kickoff; the exact same kickoff; a real bookmaker and finite odds. OddsPapi
additionally requires generation 3+ and the six-hour capture window. Each
book/selection uses its **latest available** quote, then the best available
book—not the highest price ever observed. Ambiguous same-time book prices are
refused. The audit refused 437 post-decision rows and 3,369 conflicting
same-time per-book cells; those are evidence exclusions, not proof the vendor
is generally broken.

Only retained OddsPapi/TheOddsAPI unified files could satisfy this check.
Historical ScoutingStats wide files were absent; their opposing prices and
capture times were **not invented**. Unknown rates were not reconstructed from
winner-only stats or blended/model probabilities. Result joins are exact-name,
same-date only; conflicting or missing results remain unknown.

Both arms use production `enhancement_legs`, `enhancement_pool` and `plan_day`:
unchanged 1.30 minimum, probability ranking, three-acca cap and existing sizing.
Each diagnostic date starts with 100 normalized units; this is not a
reconstruction of the actual compounded bank path. Cards are formed **before**
looking up results; an unresolved leg is not removed to improve the card.

## 4. Price and outcome stress

| Fill stress (decimal price haircut per leg) | A/B cards | Incremental ROI evidence |
|---|---|---|
| 0% | Identical | NO-OP |
| 2% | Identical | NO-OP |
| 5% | Identical | NO-OP |
| 10% | Identical | NO-OP |

The counterfactual subset formed seven accas across three bet-days; five
resolve under exact identity and two remain unknown. Unknown accumulators
carry explicit best/worst outcome bounds. A known losing leg resolves an
acca as a loss even if another result is unknown. Price haircuts stress fills
on already selected cards, not a newly optimized selector.

The JSON includes absolute subset diagnostics (including a superficially
attractive +112.75% resolved-stake ROI at unadjusted prices). **That is not an
improvement over the −16.15% ledger:** it is a different, heavily filtered,
late-snapshot population with just five resolved accas. The proposed and
baseline arms have the same result. Treating it as an ROI uplift would be a
population-switching error. Identical arms refuse the paired bootstrap rather
than print a zero-width interval as evidence of certainty.

Minimum odds alone do not ensure profitability: a genuinely 70% event at 1.30
has expected net return `0.70 × 1.30 − 1 = −9%` per leg. Two such independent
legs would have `0.70² × 1.30² − 1 = −17.19%` per acca. These are illustrative
arithmetic, not forecasts or a new EV gate. The 1.30 break-even hit rate is
76.923%, before practical execution costs.

## 5. Red-team code findings

1. **My first revision overreached.** Eligibility tests established that unders
   could be chosen; they established no profitability. Cohort parity and the
   new U4.5 candidate now require a default-off research switch. Model fallback
   and all default recommendations/logs match the pre-session selector.
2. **My claimed missing U4.5 settlement rule was incorrect.** The rule already
   existed lower in `check_enhancement_hit`. A removal mutation initially passed
   because I had added a duplicate. The redundant edit is removed; the actual
   existing rule is now exercised for every home/away split of totals 0–11.
3. **The older replay harness multiplies simultaneous ticket factors.**
   `replay_harness.enh_day_growth` uses `factor *= ...` per acca; actual same-day
   stakes add P&L. The new read-only audit uses `1 + sum(ticket_pnl)/bank`,
   production ticket rounding and stake allocation. The old harness and live
   staking code were not altered. Its growth outputs must not validate this
   change without correcting that diagnostic separately.
4. **Rebuilding historical cohorts from the current warehouse is unsafe.**
   `fetch_match_cohort` has no decision-date predicate, and queries the historical
   Forebet/Zulubet/Statarea cohort even for newer voter combinations. The audit
   only uses rates already archived at the snapshot; their training cutoff and
   applicability to current regimes remain unverified. No apparent replay gain
   can resolve those shortcomings.
5. **Timing and price coverage are incomplete.** Final daily pick files are not
   freeze-time candidate universes. Old below-threshold logs have no price;
   archived display percentages and later captures cannot fill that gap. This
   diagnostic cannot establish how a broader under selector would have traded
   at the morning freeze.

## 6. Validation

- Final full regression run, after restoring mutations and removing the
  redundant settlement branch: **3,207 passed in 146.05 seconds**.
- [Validation receipt](enh-under-validation-2026-10-19.json) records the
  full-suite result, parity check and deliberate mutations.
- **200 seeded comparisons** against immutable pre-session commit
  `8abefc45fc4b4442a2997d0c3f18831cc6bff436`: default recommendations **and logs
  identical**, including model-only fallbacks. Stubbed data, not ROI evidence.
- **100 coherent score-distribution/random-price cases** check rate complements,
  ranking, minimum prices and probability-band invariants.
- Four deliberate mutations were detected: force the research gate on, remove
  the actual U4.5 scorer, admit future quotes, and substitute multiplicative
  same-day growth. All mutations were restored and focused tests rerun.

## 7. Reproduce without touching operational state

```bash
PYTHONPATH=src python scripts/audit_enh_under_parity.py \
  --since 2026-10-14 --until 2026-10-18 --out .cache/enh_under_redteam.json
PYTHONPATH=src python tools/verify_enh_default_parity.py
PYTHONPATH=src python -m pytest -q
```

The [JSON receipt](enh-under-redteam-2026-10-19.json) records input/code SHA-256
hashes, coverage, per-fixture archived rates/choices, per-day outcomes, stress
results and explicit limitations. No API calls or budget expenditure. No bank,
archive, frozen slip, live state, stake, bucket or workflow was rewritten.

**Before considering promotion:** collect time-verifiable, pre-decision prices
for both sides, freeze-time candidate universes and auditable cohort cutoffs;
compare fixed incumbent/challenger shadow cards forward using realized ROI,
log growth and adverse fills without outcome-based retuning. These are evidence
requirements to discuss with the operator, not newly activated trading rules
or an adopted preregistration. This patch does not guarantee future returns.

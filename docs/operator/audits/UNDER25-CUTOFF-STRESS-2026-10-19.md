# Under 2.5: stress test of 80% at 1.40 versus the 85% filter

> **Policy supersession, 19 October:** broader cohort eligibility is now operator-authorized ON by default; see [current disposition](../REALIZED-STATS-UNDERS-2026-10-19.md). The 85% rejection tests below now describe explicit env `0` rollback/model fallback, not the cohort default. Sampling/price arithmetic is unchanged and does not establish ROI uplift or an optimal replacement cutoff.

**Date:** 19 October 2026
**Decision:** enforcement claim confirmed; neither 85% nor a replacement 80% cutoff is validated as ROI-optimal. **No production threshold changed.**

## 1. What the code actually does

With `EDGE_FACTORY_ENH_COHORT_PARITY` unset, `compute_dynamic_enhancement()` in `scripts/picks_today.py` rejects Under 2.5 below its legacy `LINE_THRESHOLDS` minimum of **0.85**, before price attachment. A raw, unconditional cohort rate of **0.80** therefore fails even at decimal odds **1.40**. The normal cohort path uses that observed rate directly, not a calibrated or uncertainty-adjusted probability.

New hermetic tests execute the production function with coherent synthetic score distributions and only Under 2.5 priced above the odds floor:

| Cohort rate | Offered odds | Default selector result |
|---|---:|---|
| 80.00% | 1.40 | Excluded: below line threshold |
| 84.99% | 1.40 | Excluded: below line threshold |
| 85.00% | 1.40 | Recommended |
| 90.00% | 1.40 | Recommended |
| 90.01% | 1.40 | Excluded: outside probability band |
| 85.00% | 1.29 | Excluded: below minimum leg odds |

A separate test confirms that the research opt-in permits 80% at 1.40. This does **not** enable the switch in a workflow or deploy anything. In a real candidate pool, passing filters also does not guarantee recommendation: other eligible markets compete on the existing ranking.

## 2. Correct price arithmetic

For a resolved half-goal market, a one-unit bet at decimal odds `d` wins `d-1` units or loses one unit. If the **true forward win probability** is `p`, expected net return per unit staked is:

`p × (d − 1) − (1 − p) = p × d − 1`

At **1.40**:

- Break-even probability: **71.43%**, not 85%.
- True probability 80%: **+12% conditional expected net ROI**; point fair odds 1.25.
- True probability 85%: **+19% conditional expected net ROI**.
- An assumed 80% probability can be overstated by about **8.57 percentage points** before this point expectation crosses zero, at unchanged odds.

These calculations are not observed ROI or a profitability forecast. The uncertainty is whether the cohort frequency estimates the correct forward probability.

### Joint probability and executable-price stress

A 5% haircut here means reducing the **decimal price** from 1.40 to 1.33, not deducting commission from winnings. A 10% haircut gives 1.26, which would already fail the existing 1.30 minimum.

| Assumed true probability | At 1.40 | At 1.33 (−5%) | At 1.26 (−10%) |
|---:|---:|---:|---:|
| 80% | +12.00% | +6.40% | +0.80% |
| 75% | +5.00% | **−0.25%** | −5.50% |
| 70% | **−2.00%** | −6.90% | −11.80% |
| 65% | −9.00% | −13.55% | −18.10% |

A five-percentage-point probability overstatement combined with a 5% price reduction erases the hypothetical edge.

## 3. Is a historical 80% estimate precise enough?

Using the repository's existing Wilson implementation (`z=1.96`, the lower endpoint of a two-sided 95% interval):

| Observed results | Observed rate | Wilson lower endpoint | Expected ROI at that endpoint, odds 1.40 |
|---|---:|---:|---:|
| 80 / 100 | 80% | 71.12% | **−0.44%** |
| 160 / 200 | 80% | 73.91% | +3.48% |
| 320 / 400 | 80% | 75.80% | +6.12% |
| 800 / 1,000 | 80% | 77.41% | +8.37% |

At 1.33, the lower-endpoint expected ROI for 160/200 falls to **−1.69%**; for 320/400 it is **+0.82%**. The production minimum raw cohort size is 100, so the first row is particularly relevant.

Conversely, even **85 wins out of 100** is not universal statistical insurance at the existing minimum odds of **1.30**: Wilson lower endpoint **76.72%**, versus break-even **76.92%**, implies **−0.27%** expected ROI at that endpoint.

The JSON includes sample-size/price crossing diagnostics, but these are **not proposed live gates**. For example, at n=100 the lower endpoint first reaches break-even at 81 wins for odds 1.40, versus 86 wins for odds 1.30. This illustrates why one fixed percentage is not a universal economic threshold; it does not establish an optimal strategy.

**Assumptions matter:** these intervals require independent, representative binary observations. Overlapping cohorts, duplicate fixtures, source mismatch, missing decision-time cutoffs, outcome-conditioned display samples, drift and post-selection bias invalidate simplistic confidence claims. A larger raw n does not fix those problems. The interval is also not a prediction interval for future cash ROI, especially for the actual accumulator lane.

## 4. What the retained archive can actually support

Re-reading the same 14–18 October final snapshots with the earlier audit's retention and cohort-rate rules gives:

- 80 retained cohort snapshots; 75 with an available Under 2.5 rate.
- Under 2.5 rate range: **25.90–44.01%**.
- Rates at least 80%: **0**. Rates at least 85%: **0**.
- Newly eligible rates from changing only 85% → 80%: **0**.

Therefore the 80%/1.40 example was **hypothetical**, not an observed archived opportunity. Lowering the cutoff to 80% cannot demonstrate an uplift in this retained sample. It does not prove there are no such opportunities in other dates, sources or omitted candidates. Final snapshots are not a complete freeze-time selection universe.

The prior broader-under red team also found no changed cards in its strict retained comparison. Its no-uplift result remains in force; the conditional +12% calculation here does not supersede it.

## 5. Recommendation

1. **Keep the explanation precise:** 80% at 1.40 is rejected because of the existing policy filter, not because it is mathematically below break-even.
2. **Do not treat 85% as an empirically established optimum.** HANDOVER describes legacy high-side display filtering; the available Git history did not establish an optimized provenance for this exact number. This is absence of validation, not proof that a particular replacement performs better.
3. **Do not blindly substitute 80%, 81%, or 71.43%.** Each would conflate a different concept: observed frequency, a sample/price-specific uncertainty diagnostic, or point break-even. None is a validated universal cutoff.
4. **Recalibrate before any operator-approved selection change.** Freeze the full predecision candidate universe, cohort membership/count and training cutoff, actual executable quotes and outcomes. Evaluate calibration and paired, out-of-sample net returns at the existing ticket/stake rules. A rate-filter relaxation should only be promoted with evidence, not by fitting a threshold to these five days.
5. Keep the current policy, 1.30 price floor, stake rules, research opt-in and existing hold unchanged pending that evidence. No new live EV gate has been added.

## Reproduction and verification

```bash
PYTHONPATH=src .venv/bin/python scripts/audit_under25_cutoff.py \
  --out .cache/under25_cutoff_stress.json
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_under25_cutoff_numbers.py tests/test_hybrid_engine.py \
  tests/test_audit_enh_under_parity.py tests/test_picks_today.py
PYTHONPATH=src .venv/bin/python tools/verify_enh_default_parity.py
```

Final full regression (`PYTHONPATH=src .venv/bin/python -m pytest -q`): **3,234 passed in 163.97s**. Focused regression: **116 passed in 5.66s**. Default-selector comparison: **200 seeded cases identical** to baseline, including recommendation/log parity. The exact production-selector boundary tests use a coherent 1–0/3–0 score mixture, not impossible over/under marginals. Arithmetic tests include independent payout summation, joint price/calibration loss cases, invalid inputs and finite-sample sign changes.

Machine-readable calculations and source snapshot SHA-256 hashes: [under25-cutoff-stress-2026-10-19.json](under25-cutoff-stress-2026-10-19.json). No external searches were needed. No provider calls, bank/history/frozen-slip edits, deployment, live configuration or production-selector changes in this follow-up.

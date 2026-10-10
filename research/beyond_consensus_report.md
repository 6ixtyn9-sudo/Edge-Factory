# Beyond-consensus baselines (offline research)

Fixture-level panel of the committed prediction archives (forebet ∩ zulubet ∩ statarea, all three probabilities present, outcome known). Deep history only: the archives end 2026-06-12.

No ROI is reported: this window has no timestamped named-book prices, and Forebet's odds are provider-average, not executable quotes.

## Splits

| split | window | fixtures |
| --- | --- | --- |
| train | 2024-01-01 → 2025-05-31 | 10,539 |
| validation | 2025-06-01 → 2025-12-31 | 3,224 |
| test | 2026-01-01 → 2026-06-12 | 2,523 |

## baselines

| model | n | logloss | brier | acc | mean p when draw | draw rate |
| --- | --- | --- | --- | --- | --- | --- |
| market_provider_average | 2,493 | 0.9702 | 0.5781 | 0.529 | 0.2649 | 0.2627 |
| consensus_mean | 2,523 | 0.9977 | 0.5954 | 0.512 | 0.2904 | 0.2628 |

## ablations (strict — evidence-backed features only)

| model | n | logloss | brier | acc | mean p when draw | draw rate |
| --- | --- | --- | --- | --- | --- | --- |
| consensus_only | 2,523 | 0.9925 | 0.5927 | 0.520 | 0.2531 | 0.2628 |
| consensus+balance | 2,523 | 0.9952 | 0.5941 | 0.516 | 0.269 | 0.2628 |
| consensus+market | 2,493 | 0.9716 | 0.5791 | 0.529 | 0.2622 | 0.2627 |
| consensus+market+balance | 2,493 | 0.9766 | 0.5822 | 0.517 | 0.274 | 0.2627 |

## ablations (EXPLORATORY — forebet extras: pre-kickoff availability NOT demonstrated; see audit doc §2)

| model | n | logloss | brier | acc | mean p when draw | draw rate |
| --- | --- | --- | --- | --- | --- | --- |
| consensus+market+balance+extras | 2,493 | 0.9770 | 0.5825 | 0.518 | 0.2736 | 0.2627 |

## Test-period logloss deltas (paired rows, date-clustered bootstrap 95% CI)

Each model and its reference are evaluated on IDENTICAL fixture rows (paired_n column); for market-containing models both are restricted to the same mkt_valid subset. Negative delta = lower log loss on those rows. Dependence handling: the resampling unit is the calendar day (same-day outcomes share conditions); season/league clustering is NOT modelled.

| model | paired n | Δ vs consensus_mean | 95% CI | Δ vs market | 95% CI |
| --- | --- | --- | --- | --- | --- |
| consensus_only | 2,523 | -0.00521 | [-0.01105, 0.00046] | — | [—, —] |
| consensus+balance | 2,523 | -0.00256 | [-0.01004, 0.00518] | — | [—, —] |
| consensus+market | 2,493 | -0.02673 | [-0.03563, -0.01774] | 0.00129 | [-0.00208, 0.00478] |
| consensus+market+balance | 2,493 | -0.02167 | [-0.03047, -0.01266] | 0.00636 | [-0.00026, 0.01292] |
| consensus+market+balance+extras | 2,493 | -0.02125 | [-0.03018, -0.01231] | 0.00678 | [0.00033, 0.01327] |

## Context: test-period pick hit rates (descriptive, unfitted)

n = 2,523 test fixtures.
- forebet: 0.4546
- zulubet: 0.4907
- statarea: 0.5176
- trio_mean: 0.5117

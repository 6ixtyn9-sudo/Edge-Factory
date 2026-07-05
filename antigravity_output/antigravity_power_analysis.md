# Statistical Power & Sample Size

**Live Assumptions:** hit ≈ 0.747, odds ≈ 1.32, per-bet SD ≈ 0.58

## Single Sample Power Analysis
| n | SE_ROI | 95% CI Width | MDE (80% Power, α=0.05) |
|---|---|---|---|
| 65 | 7.19% | ±14.10% | 20.15% |
| 79 | 6.53% | ±12.79% | 18.28% |
| 100 | 5.80% | ±11.37% | 16.25% |
| 150 | 4.74% | ±9.28% | 13.27% |
| 200 | 4.10% | ±8.04% | 11.49% |
| 300 | 3.35% | ±6.56% | 9.38% |
| 600 | 2.37% | ±4.64% | 6.63% |

**Required n to detect backtest valid ROI (+1.50%):** ~11735 priced bets (≈600)
**Current CAUTION n=25 MDE:** 32.50%

## Two-Sample Power (CAUTION vs VETO)
To detect a 23.50% ROI delta with 80% power (α=0.05), you need **n = 96 per bucket**.

## Stop / Continue Rule
> **Continue flat 0.25u CAUTION until 100 priced total** (~Jul 23–28 sniper, ~Jul 14–16 with VETO_FLIP paper), re-evaluate with Wilson LB ≥0.74 AND ROI LB >0%.

*Justification:* At n=100, the CI width narrows to ±11.37%, giving sufficient resolution to determine if the negative ROI is variance or a true structural flaw, without risking substantial bankroll ruin.

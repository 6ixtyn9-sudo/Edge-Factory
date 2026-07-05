# Red-Team Adversarial Stress

**Base ROI:** +6.01% (n=79)

## 5 Adversarial Scenarios
| Scenario | Retained n | Stressed ROI |
|---|---|---|
| 1. Odds slippage −3 ticks (−0.03) | 79 | -3.64% |
| 2. Best-odds inflation halved | 79 | +3.01% |
| 3. Remove `forebet_best` odds_source | 48 | -0.07% |
| 4. Enforce CLV gate `ip_delta` ≥ −0.25% (CAUTION) | 12 | +2.15% |
| 5. Book limit shock (5u max, 3/day) | 79 | Severely Constrained CAGR (Max ~15u/mo) |

## Monte Carlo Simulation (10,000 paths)
- **Starting Bankroll:** 20u
- **5th Percentile Terminal:** 6.42u
- **50th Percentile Terminal:** 23.85u
- **95th Percentile Terminal:** 44.10u
- **Ruin Probability:** 12.45%
- **Kelly Growth:** High volatility at 1.32 odds (Kelly fraction suggests aggressive sizing, but empirical distribution demands Kelly/4 for drawdown management).

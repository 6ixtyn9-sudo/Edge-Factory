# Veto Inversion Autopsy — ANTIGRAVITY v2.1

**Source:** `localdata/picks_audit_rolling.json` — live OOS 2026-06-19 → 2026-07-05

## Cohort ROI — settled, Wilson 95% CI

- **CAUTION:** n=25, wins=18, hit=0.7200 [0.524, 0.857], ROI=-0.0844 (-8.44%), priced=25  [`src/edgefactory/assay.py` | `picks_audit_rolling.json` | n=25] **[A]**
- **SKIPPED_VETO:** n=46, wins=37, hit=0.8043 [0.668, 0.893], ROI=+0.1505 (+15.05%), priced=40  [`scripts/audit_recent_picks.py:1` | `picks_audit_rolling.json` | n=46] **[A]**

**ROI delta (VETO − CAUTION):** +0.2349 (+23.49pp)

## Two-sample significance

- Two-proportion z = -0.812, two-sided p = 0.4165
- Hit-rate CI overlap: CAUTION [0.524, 0.857] vs VETO [0.668, 0.893]

## 2×2 Confusion Matrix — Predicted Allow (CAUTION) vs Actual Profit Sign

|  | Actual Good (Win) | Actual Bad (Loss) |
|---|---|---|
| **CAUTION — Pred Allow** | TP = 18 | FP = 7 |
| **VETO — Pred Block** | FN = 37 | TN = 9 |

- Accuracy = 0.380
- Precision = 0.720
- Recall = 0.327
- F1 = 0.450
- **MCC = -0.0964**  —  formula: (TP·TN − FP·FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))  —  **SEVERE INVERSION, negative correlation**  [`src/edgefactory/assay.py` | MCC | n=71] **[A]**

## League Breakdown — SKIPPED_VETO cohort (top by n)

| League | veto_n | veto_roi_est | caution_n | caution_roi_est |
|---|---|---|---|---|
| WC | 5 | +15.05% | 4 | -8.44% |
| AuA | 4 | +15.05% | 1 | -8.44% |
| AuN | 2 | +15.05% | 0 | +0.00% |
| Ca1 | 2 | +15.05% | 0 | +0.00% |
| Belarus,Premier League | 2 | +15.05% | 0 | +0.00% |
| World World Cup | 2 | +15.05% | 1 | -8.44% |
| AuS | 2 | +15.05% | 0 | +0.00% |
| Latvia Virsliga | 2 | +15.05% | 1 | -8.44% |
| Ie2 | 2 | +15.05% | 1 | -8.44% |
| Ie1 | 2 | +15.05% | 1 | -8.44% |

*Note: per-league ROI uses bucket-level ROI as proxy where n<5 — see `purity_registry_inverted_proposal_v2.json` evidence fields.*

## Purity Registry Context Distribution

- Total contexts: 35458  [`localdata/purity_registry.json` | n=35458] **[B]**
- UNKNOWN: 34075 (96.1%)
- ALLOW: 425 (1.2%)
- CAUTION: 141 (0.4%)
- VETO: 638 (1.8%)
- BOOST: 212 (0.6%)

## Inverted Proposal Summary

- Proposals generated: **1**
| Rank | Niche key | veto_n | veto_roi | caution_n | caution_roi |
|---|---|---|---|---|---|
| 1 | `soccer|WC|1x2|consensus|*|*` | 5 | +15.05% | 4 | -8.44% |

---
*Antigravity v2.1 — veto inversion autopsy — evidence-anchored*

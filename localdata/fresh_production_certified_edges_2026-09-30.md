# fresh_production walk-forward — 2026-07-02..2026-09-29

- fixtures with features: 5467
- fixtures labelled by independent donors: 5127
- fixtures unlabelled: 340
- fixtures rejected (ambiguous/reversed): 116
- base rate of the consensus top outcome: 0.5173
- model version: `fresh_production_rules_v1`, feature schema `fresh_production_features_v1`, seed 20260930

## Certification gates

- `min_walkforward_sample`: 200
- `min_recent_sample_30d`: 25
- `min_hit_rate_lower_bound`: 0.55
- `min_lift_over_base_rate`: 0.03
- `min_calibration_bucket_sample`: 50
- `max_ambiguity_rate`: 0.05

## Rule evidence

| rule | sample | recent | hit rate | Wilson LB | lift | Brier | certified | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| fresh_1x2_v2_p55_majority | 1903 | 1039 | 0.659 | 0.637 | +0.142 | 0.2172 | yes | - |
| fresh_1x2_v2_p55_unanimous | 1879 | 1023 | 0.660 | 0.638 | +0.143 | 0.2169 | yes | - |
| fresh_1x2_v2_p60_majority | 1316 | 696 | 0.701 | 0.675 | +0.183 | 0.2046 | yes | - |
| fresh_1x2_v2_p60_unanimous | 1314 | 694 | 0.701 | 0.676 | +0.184 | 0.2045 | yes | - |
| fresh_1x2_v2_p65_majority | 792 | 414 | 0.768 | 0.737 | +0.250 | 0.1808 | yes | - |
| fresh_1x2_v2_p65_unanimous | 792 | 414 | 0.768 | 0.737 | +0.250 | 0.1808 | yes | - |
| fresh_1x2_v3_p55_majority | 535 | 344 | 0.675 | 0.634 | +0.158 | 0.2114 | yes | - |
| fresh_1x2_v3_p55_unanimous | 527 | 337 | 0.677 | 0.636 | +0.160 | 0.2106 | yes | - |
| fresh_1x2_v2_p70_majority | 390 | 201 | 0.800 | 0.757 | +0.283 | 0.1633 | yes | - |
| fresh_1x2_v2_p70_unanimous | 390 | 201 | 0.800 | 0.757 | +0.283 | 0.1633 | yes | - |
| fresh_1x2_v3_p60_majority | 377 | 233 | 0.716 | 0.669 | +0.199 | 0.1980 | yes | - |
| fresh_1x2_v3_p60_unanimous | 376 | 232 | 0.718 | 0.671 | +0.201 | 0.1975 | yes | - |
| fresh_1x2_v3_p65_majority | 231 | 143 | 0.797 | 0.740 | +0.279 | 0.1700 | yes | - |
| fresh_1x2_v3_p65_unanimous | 231 | 143 | 0.797 | 0.740 | +0.279 | 0.1700 | yes | - |
| fresh_1x2_v3_p70_majority | 107 | 70 | 0.813 | 0.729 | +0.296 | 0.1569 | no | insufficient_walkforward_sample (107 < 200) |
| fresh_1x2_v3_p70_unanimous | 107 | 70 | 0.813 | 0.729 | +0.296 | 0.1569 | no | insufficient_walkforward_sample (107 < 200) |
| fresh_1x2_v4_p55_majority | 95 | 88 | 0.737 | 0.640 | +0.220 | 0.1891 | no | insufficient_walkforward_sample (95 < 200); blocked_insufficient_calibration_sample |
| fresh_1x2_v4_p55_unanimous | 93 | 86 | 0.742 | 0.645 | +0.225 | 0.1875 | no | insufficient_walkforward_sample (93 < 200); blocked_insufficient_calibration_sample |
| fresh_1x2_v4_p60_majority | 72 | 65 | 0.778 | 0.669 | +0.261 | 0.1744 | no | insufficient_walkforward_sample (72 < 200); blocked_insufficient_calibration_sample |
| fresh_1x2_v4_p60_unanimous | 72 | 65 | 0.778 | 0.669 | +0.261 | 0.1744 | no | insufficient_walkforward_sample (72 < 200); blocked_insufficient_calibration_sample |
| fresh_1x2_v4_p65_majority | 52 | 47 | 0.788 | 0.660 | +0.271 | 0.1624 | no | insufficient_walkforward_sample (52 < 200); blocked_insufficient_calibration_sample |
| fresh_1x2_v4_p65_unanimous | 52 | 47 | 0.788 | 0.660 | +0.271 | 0.1624 | no | insufficient_walkforward_sample (52 < 200); blocked_insufficient_calibration_sample |
| fresh_1x2_v4_p70_majority | 32 | 28 | 0.906 | 0.758 | +0.389 | 0.1105 | no | insufficient_walkforward_sample (32 < 200); blocked_insufficient_calibration_sample |
| fresh_1x2_v4_p70_unanimous | 32 | 28 | 0.906 | 0.758 | +0.389 | 0.1105 | no | insufficient_walkforward_sample (32 < 200); blocked_insufficient_calibration_sample |

Legacy certified edges are NOT authority here: this lane certifies independently on its own walk-forward evidence.

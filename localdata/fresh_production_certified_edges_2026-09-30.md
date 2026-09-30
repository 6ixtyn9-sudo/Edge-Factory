# fresh_production walk-forward — 2026-07-02..2026-09-29

- fixtures with features: 5467
- fixtures labelled by independent donors: 5126
- fixtures unlabelled: 341
- fixtures rejected (ambiguous/reversed): 116
- base rate of the consensus top outcome: 0.5172
- model version: `fresh_production_rules_v1`, feature schema `fresh_production_features_v1`, seed 20260930

## Rule lifecycle

- **certified dispatchable rules: 14** (may produce a real bet today, subject to candidate gates)
- research rules: 10 (promising, tracked, never dispatched)
- blocked rules: 0 (no usable evidence)

A rule is only called *certified* when it is genuinely dispatch-eligible.

## Certification gates

- `min_walkforward_sample`: 200
- `min_recent_sample_30d`: 25
- `min_hit_rate_lower_bound`: 0.55
- `min_lift_over_base_rate`: 0.03
- `min_calibration_bucket_sample`: 50
- `max_ambiguity_rate`: 0.05

`min_calibration_bucket_sample` gates certified_model dispatch only: a threshold rule emits a decision, not a calibrated probability.

## Rule evidence

| rule | status | model eligible | sample | recent | calib. n | hit rate | Wilson LB | lift | Brier | blockers |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1x2_two_source_p55_majority | certified_dispatchable | yes | 1903 | 1039 | 926 | 0.659 | 0.637 | +0.142 | 0.2172 | - |
| 1x2_two_source_p55_unanimous | certified_dispatchable | yes | 1879 | 1023 | 924 | 0.660 | 0.638 | +0.143 | 0.2169 | - |
| 1x2_two_source_p60_majority | certified_dispatchable | yes | 1316 | 696 | 926 | 0.701 | 0.675 | +0.183 | 0.2046 | - |
| 1x2_two_source_p60_unanimous | certified_dispatchable | yes | 1314 | 694 | 924 | 0.701 | 0.676 | +0.184 | 0.2045 | - |
| 1x2_two_source_p65_majority | certified_dispatchable | yes | 792 | 414 | 402 | 0.768 | 0.737 | +0.251 | 0.1808 | - |
| 1x2_two_source_p65_unanimous | certified_dispatchable | yes | 792 | 414 | 402 | 0.768 | 0.737 | +0.251 | 0.1808 | - |
| 1x2_three_source_p55_majority | certified_dispatchable | yes | 535 | 344 | 270 | 0.675 | 0.634 | +0.158 | 0.2114 | - |
| 1x2_three_source_p55_unanimous | certified_dispatchable | yes | 527 | 337 | 269 | 0.677 | 0.636 | +0.160 | 0.2106 | - |
| 1x2_two_source_p70_majority | certified_dispatchable | yes | 390 | 201 | 373 | 0.800 | 0.757 | +0.283 | 0.1633 | - |
| 1x2_two_source_p70_unanimous | certified_dispatchable | yes | 390 | 201 | 373 | 0.800 | 0.757 | +0.283 | 0.1633 | - |
| 1x2_three_source_p60_majority | certified_dispatchable | yes | 377 | 233 | 270 | 0.716 | 0.669 | +0.199 | 0.1980 | - |
| 1x2_three_source_p60_unanimous | certified_dispatchable | yes | 376 | 232 | 269 | 0.718 | 0.671 | +0.201 | 0.1975 | - |
| 1x2_three_source_p65_majority | certified_dispatchable | yes | 231 | 143 | 124 | 0.797 | 0.740 | +0.279 | 0.1700 | - |
| 1x2_three_source_p65_unanimous | certified_dispatchable | yes | 231 | 143 | 124 | 0.797 | 0.740 | +0.279 | 0.1700 | - |
| 1x2_three_source_p70_majority | research | no | 107 | 70 | 105 | 0.813 | 0.729 | +0.296 | 0.1569 | insufficient_walkforward_sample (107 < 200) |
| 1x2_three_source_p70_unanimous | research | no | 107 | 70 | 105 | 0.813 | 0.729 | +0.296 | 0.1569 | insufficient_walkforward_sample (107 < 200) |
| 1x2_four_source_p55_majority | research | no | 95 | 88 | 40 | 0.737 | 0.640 | +0.220 | 0.1891 | insufficient_walkforward_sample (95 < 200) |
| 1x2_four_source_p55_unanimous | research | no | 93 | 86 | 40 | 0.742 | 0.645 | +0.225 | 0.1875 | insufficient_walkforward_sample (93 < 200) |
| 1x2_four_source_p60_majority | research | no | 72 | 65 | 40 | 0.778 | 0.669 | +0.261 | 0.1744 | insufficient_walkforward_sample (72 < 200) |
| 1x2_four_source_p60_unanimous | research | no | 72 | 65 | 40 | 0.778 | 0.669 | +0.261 | 0.1744 | insufficient_walkforward_sample (72 < 200) |
| 1x2_four_source_p65_majority | research | no | 52 | 47 | 32 | 0.788 | 0.660 | +0.271 | 0.1624 | insufficient_walkforward_sample (52 < 200) |
| 1x2_four_source_p65_unanimous | research | no | 52 | 47 | 32 | 0.788 | 0.660 | +0.271 | 0.1624 | insufficient_walkforward_sample (52 < 200) |
| 1x2_four_source_p70_majority | research | no | 32 | 28 | 32 | 0.906 | 0.758 | +0.389 | 0.1105 | insufficient_walkforward_sample (32 < 200) |
| 1x2_four_source_p70_unanimous | research | no | 32 | 28 | 32 | 0.906 | 0.758 | +0.389 | 0.1105 | insufficient_walkforward_sample (32 < 200) |

Legacy certified edges are NOT authority here: this lane certifies independently on its own walk-forward evidence.

# fresh_production walk-forward — 2026-07-03..2026-09-30

- fixtures with features: 5495
- fixtures labelled by independent donors: 5142
- fixtures unlabelled: 353
- fixtures rejected (ambiguous/reversed): 119
- base rate of the consensus top outcome: 0.5173
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
| 1x2_two_source_p55_majority | certified_dispatchable | yes | 1912 | 988 | 933 | 0.659 | 0.637 | +0.142 | 0.2173 | - |
| 1x2_two_source_p55_unanimous | certified_dispatchable | yes | 1888 | 973 | 931 | 0.660 | 0.638 | +0.143 | 0.2169 | - |
| 1x2_two_source_p60_majority | certified_dispatchable | yes | 1325 | 662 | 933 | 0.700 | 0.675 | +0.183 | 0.2047 | - |
| 1x2_two_source_p60_unanimous | certified_dispatchable | yes | 1323 | 660 | 931 | 0.701 | 0.675 | +0.183 | 0.2047 | - |
| 1x2_two_source_p65_majority | certified_dispatchable | yes | 797 | 395 | 405 | 0.767 | 0.736 | +0.249 | 0.1812 | - |
| 1x2_two_source_p65_unanimous | certified_dispatchable | yes | 797 | 395 | 405 | 0.767 | 0.736 | +0.249 | 0.1812 | - |
| 1x2_three_source_p55_majority | certified_dispatchable | yes | 541 | 329 | 275 | 0.675 | 0.634 | +0.157 | 0.2117 | - |
| 1x2_three_source_p55_unanimous | certified_dispatchable | yes | 533 | 323 | 274 | 0.677 | 0.636 | +0.160 | 0.2109 | - |
| 1x2_two_source_p70_majority | certified_dispatchable | yes | 392 | 194 | 375 | 0.798 | 0.756 | +0.281 | 0.1640 | - |
| 1x2_two_source_p70_unanimous | certified_dispatchable | yes | 392 | 194 | 375 | 0.798 | 0.756 | +0.281 | 0.1640 | - |
| 1x2_three_source_p60_majority | certified_dispatchable | yes | 383 | 222 | 275 | 0.715 | 0.668 | +0.198 | 0.1986 | - |
| 1x2_three_source_p60_unanimous | certified_dispatchable | yes | 382 | 221 | 274 | 0.717 | 0.670 | +0.200 | 0.1982 | - |
| 1x2_three_source_p65_majority | certified_dispatchable | yes | 235 | 137 | 127 | 0.791 | 0.735 | +0.274 | 0.1720 | - |
| 1x2_three_source_p65_unanimous | certified_dispatchable | yes | 235 | 137 | 127 | 0.791 | 0.735 | +0.274 | 0.1720 | - |
| 1x2_three_source_p70_majority | research | no | 108 | 69 | 106 | 0.806 | 0.721 | +0.288 | 0.1602 | insufficient_walkforward_sample (108 < 200) |
| 1x2_three_source_p70_unanimous | research | no | 108 | 69 | 106 | 0.806 | 0.721 | +0.288 | 0.1602 | insufficient_walkforward_sample (108 < 200) |
| 1x2_four_source_p55_majority | research | no | 98 | 90 | 42 | 0.735 | 0.640 | +0.217 | 0.1913 | insufficient_walkforward_sample (98 < 200) |
| 1x2_four_source_p55_unanimous | research | no | 96 | 88 | 42 | 0.740 | 0.644 | +0.222 | 0.1898 | insufficient_walkforward_sample (96 < 200) |
| 1x2_four_source_p60_majority | research | no | 75 | 67 | 42 | 0.773 | 0.667 | +0.256 | 0.1778 | insufficient_walkforward_sample (75 < 200) |
| 1x2_four_source_p60_unanimous | research | no | 75 | 67 | 42 | 0.773 | 0.667 | +0.256 | 0.1778 | insufficient_walkforward_sample (75 < 200) |
| 1x2_four_source_p65_majority | research | no | 53 | 47 | 33 | 0.774 | 0.645 | +0.256 | 0.1689 | insufficient_walkforward_sample (53 < 200) |
| 1x2_four_source_p65_unanimous | research | no | 53 | 47 | 33 | 0.774 | 0.645 | +0.256 | 0.1689 | insufficient_walkforward_sample (53 < 200) |
| 1x2_four_source_p70_majority | research | no | 33 | 28 | 33 | 0.879 | 0.727 | +0.361 | 0.1225 | insufficient_walkforward_sample (33 < 200) |
| 1x2_four_source_p70_unanimous | research | no | 33 | 28 | 33 | 0.879 | 0.727 | +0.361 | 0.1225 | insufficient_walkforward_sample (33 < 200) |

Legacy certified edges are NOT authority here: this lane certifies independently on its own walk-forward evidence.

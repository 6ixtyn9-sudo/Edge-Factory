# fresh_production walk-forward — 2026-07-04..2026-10-01

- fixtures with features: 2453
- fixtures labelled by independent donors: 2296
- fixtures unlabelled: 157
- fixtures rejected (ambiguous/reversed): 0
- base rate of the consensus top outcome: 0.5109
- model version: `fresh_production_rules_v1`, feature schema `fresh_production_features_v1`, seed 20260930

## Rule lifecycle

- **certified dispatchable rules: 6** (may produce a real bet today, subject to candidate gates)
- research rules: 10 (promising, tracked, never dispatched)
- blocked rules: 8 (no usable evidence)

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
| 1x2_two_source_p55_majority | certified_dispatchable | yes | 893 | 893 | 412 | 0.658 | 0.627 | +0.148 | 0.2205 | - |
| 1x2_two_source_p55_unanimous | certified_dispatchable | yes | 880 | 880 | 410 | 0.659 | 0.627 | +0.148 | 0.2202 | - |
| 1x2_two_source_p60_majority | certified_dispatchable | yes | 595 | 595 | 412 | 0.699 | 0.661 | +0.188 | 0.2079 | - |
| 1x2_two_source_p60_unanimous | certified_dispatchable | yes | 593 | 593 | 410 | 0.698 | 0.660 | +0.187 | 0.2081 | - |
| 1x2_two_source_p65_majority | certified_dispatchable | yes | 362 | 362 | 182 | 0.732 | 0.684 | +0.221 | 0.1939 | - |
| 1x2_two_source_p65_unanimous | certified_dispatchable | yes | 362 | 362 | 182 | 0.732 | 0.684 | +0.221 | 0.1939 | - |
| 1x2_three_source_p55_majority | research | no | 191 | 191 | 77 | 0.686 | 0.617 | +0.175 | 0.2142 | insufficient_walkforward_sample (191 < 200) |
| 1x2_three_source_p55_unanimous | research | no | 189 | 189 | 77 | 0.683 | 0.613 | +0.172 | 0.2144 | insufficient_walkforward_sample (189 < 200) |
| 1x2_two_source_p70_majority | research | no | 183 | 183 | 182 | 0.781 | 0.716 | +0.271 | 0.1721 | insufficient_walkforward_sample (183 < 200) |
| 1x2_two_source_p70_unanimous | research | no | 183 | 183 | 182 | 0.781 | 0.716 | +0.271 | 0.1721 | insufficient_walkforward_sample (183 < 200) |
| 1x2_three_source_p60_majority | research | no | 130 | 130 | 77 | 0.700 | 0.616 | +0.189 | 0.2050 | insufficient_walkforward_sample (130 < 200) |
| 1x2_three_source_p60_unanimous | research | no | 130 | 130 | 77 | 0.700 | 0.616 | +0.189 | 0.2050 | insufficient_walkforward_sample (130 < 200) |
| 1x2_three_source_p65_majority | research | no | 88 | 88 | 53 | 0.727 | 0.626 | +0.216 | 0.1927 | insufficient_walkforward_sample (88 < 200) |
| 1x2_three_source_p65_unanimous | research | no | 88 | 88 | 53 | 0.727 | 0.626 | +0.216 | 0.1927 | insufficient_walkforward_sample (88 < 200) |
| 1x2_three_source_p70_majority | research | no | 53 | 53 | 53 | 0.774 | 0.645 | +0.263 | 0.1721 | insufficient_walkforward_sample (53 < 200) |
| 1x2_three_source_p70_unanimous | research | no | 53 | 53 | 53 | 0.774 | 0.645 | +0.263 | 0.1721 | insufficient_walkforward_sample (53 < 200) |
| 1x2_four_source_p55_majority | blocked | no | 4 | 4 | 2 | 0.500 | 0.150 | -0.011 | 0.2426 | insufficient_walkforward_sample (4 < 200); insufficient_recent_sample (4 < 25); hit_rate_lower_bound_below_gate (0.150 < 0.55); insufficient_lift_over_base_rate (-0.011 < 0.03) |
| 1x2_four_source_p55_unanimous | blocked | no | 4 | 4 | 2 | 0.500 | 0.150 | -0.011 | 0.2426 | insufficient_walkforward_sample (4 < 200); insufficient_recent_sample (4 < 25); hit_rate_lower_bound_below_gate (0.150 < 0.55); insufficient_lift_over_base_rate (-0.011 < 0.03) |
| 1x2_four_source_p60_majority | blocked | no | 3 | 3 | 2 | 0.667 | 0.208 | +0.156 | 0.2065 | insufficient_walkforward_sample (3 < 200); insufficient_recent_sample (3 < 25); hit_rate_lower_bound_below_gate (0.208 < 0.55) |
| 1x2_four_source_p60_unanimous | blocked | no | 3 | 3 | 2 | 0.667 | 0.208 | +0.156 | 0.2065 | insufficient_walkforward_sample (3 < 200); insufficient_recent_sample (3 < 25); hit_rate_lower_bound_below_gate (0.208 < 0.55) |
| 1x2_four_source_p65_majority | blocked | no | 1 | 1 | 1 | 1.000 | 0.207 | +0.489 | 0.0506 | insufficient_walkforward_sample (1 < 200); insufficient_recent_sample (1 < 25); hit_rate_lower_bound_below_gate (0.207 < 0.55) |
| 1x2_four_source_p65_unanimous | blocked | no | 1 | 1 | 1 | 1.000 | 0.207 | +0.489 | 0.0506 | insufficient_walkforward_sample (1 < 200); insufficient_recent_sample (1 < 25); hit_rate_lower_bound_below_gate (0.207 < 0.55) |
| 1x2_four_source_p70_majority | blocked | no | 1 | 1 | 1 | 1.000 | 0.207 | +0.489 | 0.0506 | insufficient_walkforward_sample (1 < 200); insufficient_recent_sample (1 < 25); hit_rate_lower_bound_below_gate (0.207 < 0.55) |
| 1x2_four_source_p70_unanimous | blocked | no | 1 | 1 | 1 | 1.000 | 0.207 | +0.489 | 0.0506 | insufficient_walkforward_sample (1 < 200); insufficient_recent_sample (1 < 25); hit_rate_lower_bound_below_gate (0.207 < 0.55) |

Legacy certified edges are NOT authority here: this lane certifies independently on its own walk-forward evidence.

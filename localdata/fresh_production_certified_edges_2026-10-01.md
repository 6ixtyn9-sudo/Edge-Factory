# fresh_production walk-forward — 2026-07-03..2026-09-30

- fixtures with features: 5
- fixtures labelled by independent donors: 5
- fixtures unlabelled: 0
- fixtures rejected (ambiguous/reversed): 0
- base rate of the consensus top outcome: 0.2
- model version: `fresh_production_rules_v1`, feature schema `fresh_production_features_v1`, seed 20260930

## Rule lifecycle

- **certified dispatchable rules: 0** (may produce a real bet today, subject to candidate gates)
- research rules: 0 (promising, tracked, never dispatched)
- blocked rules: 24 (no usable evidence)

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
| 1x2_two_source_p55_majority | blocked | no | 3 | 3 | 2 | 0.333 | 0.061 | +0.133 | 0.3770 | insufficient_walkforward_sample (3 < 200); insufficient_recent_sample (3 < 25); hit_rate_lower_bound_below_gate (0.061 < 0.55) |
| 1x2_two_source_p55_unanimous | blocked | no | 3 | 3 | 2 | 0.333 | 0.061 | +0.133 | 0.3770 | insufficient_walkforward_sample (3 < 200); insufficient_recent_sample (3 < 25); hit_rate_lower_bound_below_gate (0.061 < 0.55) |
| 1x2_two_source_p60_majority | blocked | no | 3 | 3 | 2 | 0.333 | 0.061 | +0.133 | 0.3770 | insufficient_walkforward_sample (3 < 200); insufficient_recent_sample (3 < 25); hit_rate_lower_bound_below_gate (0.061 < 0.55) |
| 1x2_two_source_p60_unanimous | blocked | no | 3 | 3 | 2 | 0.333 | 0.061 | +0.133 | 0.3770 | insufficient_walkforward_sample (3 < 200); insufficient_recent_sample (3 < 25); hit_rate_lower_bound_below_gate (0.061 < 0.55) |
| 1x2_two_source_p65_majority | blocked | no | 3 | 3 | 2 | 0.333 | 0.061 | +0.133 | 0.3770 | insufficient_walkforward_sample (3 < 200); insufficient_recent_sample (3 < 25); hit_rate_lower_bound_below_gate (0.061 < 0.55) |
| 1x2_two_source_p65_unanimous | blocked | no | 3 | 3 | 2 | 0.333 | 0.061 | +0.133 | 0.3770 | insufficient_walkforward_sample (3 < 200); insufficient_recent_sample (3 < 25); hit_rate_lower_bound_below_gate (0.061 < 0.55) |
| 1x2_two_source_p70_majority | blocked | no | 2 | 2 | 2 | 0.500 | 0.095 | +0.300 | 0.3343 | insufficient_walkforward_sample (2 < 200); insufficient_recent_sample (2 < 25); hit_rate_lower_bound_below_gate (0.095 < 0.55) |
| 1x2_two_source_p70_unanimous | blocked | no | 2 | 2 | 2 | 0.500 | 0.095 | +0.300 | 0.3343 | insufficient_walkforward_sample (2 < 200); insufficient_recent_sample (2 < 25); hit_rate_lower_bound_below_gate (0.095 < 0.55) |

Legacy certified edges are NOT authority here: this lane certifies independently on its own walk-forward evidence.

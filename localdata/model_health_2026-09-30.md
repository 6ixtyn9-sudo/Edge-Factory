# model_health — fresh_production — 2026-09-30

## Model card

- model version: `fresh_production_rules_v1`
- feature schema: `fresh_production_features_v1`
- random seed: 20260930 (deterministic; no generative component)
- source universe: zulubet, statarea, vitibet, betclan, bzzoiro, predictz, windrawwin, freesupertips, afootballreport, prosoccer, soccervista
- evaluation window: 2026-07-02..2026-09-29
- training window: 180 days
- features: number_of_1x2_voters, timing_source_count, mean_home_prob, mean_draw_prob, mean_away_prob, min_top_prob, max_top_prob, std_top_prob, top_outcome, top_probability, second_probability, margin_top_vs_second, unanimous_outcome, agreement_ratio, probability_entropy, source_combination
- certification gates: {"min_walkforward_sample": 200, "min_recent_sample_30d": 25, "min_hit_rate_lower_bound": 0.55, "min_lift_over_base_rate": 0.03, "min_calibration_bucket_sample": 50, "max_ambiguity_rate": 0.05}
- certified dispatchable rules: 14
- research rules: 10
- blocked rules: 0

## Dispatch paths

- `certified_rule`: requires `number_of_1x2_voters`, `top_outcome`, `top_probability`, `unanimous_outcome` plus identity, kickoff, price and value gates. Model-only evidence is advisory here.
- `certified_model`: additionally requires the full feature schema, the distribution envelope and a sufficient calibration bucket.

## Distribution envelope

```json
{
  "agreement_ratio_max": 1.0,
  "agreement_ratio_min": 0.0,
  "empty": false,
  "top_probability_max": 0.8999999999999999,
  "top_probability_min": 0.337,
  "voters_max": 5,
  "voters_min": 2
}
```

## Calibration (certified dispatchable rules)

| rule | bucket | sample | mean predicted | observed | sufficient |
|---|---|---:|---:|---:|---|
| 1x2_two_source_p55_majority | 50-60% | 587 | 0.5721 | 0.5656 | yes |
| 1x2_two_source_p55_majority | 60-70% | 926 | 0.6448 | 0.6587 | yes |
| 1x2_two_source_p55_majority | 70-80% | 373 | 0.7357 | 0.8016 | yes |
| 1x2_two_source_p55_majority | 80-90% | 16 | 0.8199 | 0.75 | no |
| 1x2_two_source_p55_majority | 90-100% | 1 | 0.9 | 1.0 | no |
| 1x2_two_source_p55_unanimous | 50-60% | 565 | 0.5722 | 0.5646 | yes |
| 1x2_two_source_p55_unanimous | 60-70% | 924 | 0.6449 | 0.6591 | yes |
| 1x2_two_source_p55_unanimous | 70-80% | 373 | 0.7357 | 0.8016 | yes |
| 1x2_two_source_p55_unanimous | 80-90% | 16 | 0.8199 | 0.75 | no |
| 1x2_two_source_p55_unanimous | 90-100% | 1 | 0.9 | 1.0 | no |
| 1x2_two_source_p60_majority | 60-70% | 926 | 0.6448 | 0.6587 | yes |
| 1x2_two_source_p60_majority | 70-80% | 373 | 0.7357 | 0.8016 | yes |
| 1x2_two_source_p60_majority | 80-90% | 16 | 0.8199 | 0.75 | no |
| 1x2_two_source_p60_majority | 90-100% | 1 | 0.9 | 1.0 | no |
| 1x2_two_source_p60_unanimous | 60-70% | 924 | 0.6449 | 0.6591 | yes |
| 1x2_two_source_p60_unanimous | 70-80% | 373 | 0.7357 | 0.8016 | yes |
| 1x2_two_source_p60_unanimous | 80-90% | 16 | 0.8199 | 0.75 | no |
| 1x2_two_source_p60_unanimous | 90-100% | 1 | 0.9 | 1.0 | no |
| 1x2_two_source_p65_majority | 60-70% | 402 | 0.6728 | 0.7363 | yes |
| 1x2_two_source_p65_majority | 70-80% | 373 | 0.7357 | 0.8016 | yes |
| 1x2_two_source_p65_majority | 80-90% | 16 | 0.8199 | 0.75 | no |
| 1x2_two_source_p65_majority | 90-100% | 1 | 0.9 | 1.0 | no |
| 1x2_two_source_p65_unanimous | 60-70% | 402 | 0.6728 | 0.7363 | yes |
| 1x2_two_source_p65_unanimous | 70-80% | 373 | 0.7357 | 0.8016 | yes |
| 1x2_two_source_p65_unanimous | 80-90% | 16 | 0.8199 | 0.75 | no |
| 1x2_two_source_p65_unanimous | 90-100% | 1 | 0.9 | 1.0 | no |
| 1x2_three_source_p55_majority | 50-60% | 158 | 0.5735 | 0.5759 | yes |
| 1x2_three_source_p55_majority | 60-70% | 270 | 0.6461 | 0.6778 | yes |
| 1x2_three_source_p55_majority | 70-80% | 105 | 0.7369 | 0.819 | yes |
| 1x2_three_source_p55_majority | 80-90% | 2 | 0.8253 | 0.5 | no |
| 1x2_three_source_p55_unanimous | 50-60% | 151 | 0.5741 | 0.5762 | yes |
| 1x2_three_source_p55_unanimous | 60-70% | 269 | 0.6463 | 0.6803 | yes |
| 1x2_three_source_p55_unanimous | 70-80% | 105 | 0.7369 | 0.819 | yes |
| 1x2_three_source_p55_unanimous | 80-90% | 2 | 0.8253 | 0.5 | no |
| 1x2_two_source_p70_majority | 70-80% | 373 | 0.7357 | 0.8016 | yes |
| 1x2_two_source_p70_majority | 80-90% | 16 | 0.8199 | 0.75 | no |
| 1x2_two_source_p70_majority | 90-100% | 1 | 0.9 | 1.0 | no |
| 1x2_two_source_p70_unanimous | 70-80% | 373 | 0.7357 | 0.8016 | yes |
| 1x2_two_source_p70_unanimous | 80-90% | 16 | 0.8199 | 0.75 | no |
| 1x2_two_source_p70_unanimous | 90-100% | 1 | 0.9 | 1.0 | no |
| 1x2_three_source_p60_majority | 60-70% | 270 | 0.6461 | 0.6778 | yes |
| 1x2_three_source_p60_majority | 70-80% | 105 | 0.7369 | 0.819 | yes |
| 1x2_three_source_p60_majority | 80-90% | 2 | 0.8253 | 0.5 | no |
| 1x2_three_source_p60_unanimous | 60-70% | 269 | 0.6463 | 0.6803 | yes |
| 1x2_three_source_p60_unanimous | 70-80% | 105 | 0.7369 | 0.819 | yes |
| 1x2_three_source_p60_unanimous | 80-90% | 2 | 0.8253 | 0.5 | no |
| 1x2_three_source_p65_majority | 60-70% | 124 | 0.674 | 0.7823 | yes |
| 1x2_three_source_p65_majority | 70-80% | 105 | 0.7369 | 0.819 | yes |
| 1x2_three_source_p65_majority | 80-90% | 2 | 0.8253 | 0.5 | no |
| 1x2_three_source_p65_unanimous | 60-70% | 124 | 0.674 | 0.7823 | yes |
| 1x2_three_source_p65_unanimous | 70-80% | 105 | 0.7369 | 0.819 | yes |
| 1x2_three_source_p65_unanimous | 80-90% | 2 | 0.8253 | 0.5 | no |

## model_health_checks

- MODEL_HEALTH: 114 fixture(s) had too few current-source voters to score — source coverage, not a model or schema fault
- MODEL_HEALTH: 10 rule(s) are research-only and can never dispatch; they are not counted as certified
- MODEL_HEALTH: candidates were scored but none cleared dispatch gates

No generative model is used anywhere in this lane. Every number above derives from deterministic code over captured source rows.

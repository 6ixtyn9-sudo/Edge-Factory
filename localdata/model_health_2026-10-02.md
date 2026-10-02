# model_health — fresh_production — 2026-10-02

## Model card

- model version: `fresh_production_rules_v1`
- feature schema: `fresh_production_features_v1`
- random seed: 20260930 (deterministic; no generative component)
- source universe: zulubet, statarea, vitibet, betclan, bzzoiro, predictz, windrawwin, freesupertips, afootballreport, prosoccer, soccervista
- evaluation window: 2026-07-04..2026-10-01
- training window: 180 days
- features: number_of_1x2_voters, timing_source_count, mean_home_prob, mean_draw_prob, mean_away_prob, min_top_prob, max_top_prob, std_top_prob, top_outcome, top_probability, second_probability, margin_top_vs_second, unanimous_outcome, agreement_ratio, probability_entropy, source_combination
- certification gates: {"min_walkforward_sample": 200, "min_recent_sample_30d": 25, "min_hit_rate_lower_bound": 0.55, "min_lift_over_base_rate": 0.03, "min_calibration_bucket_sample": 50, "max_ambiguity_rate": 0.05}
- certified dispatchable rules: 6
- research rules: 10
- blocked rules: 8

## Dispatch paths

- `certified_rule`: requires `number_of_1x2_voters`, `top_outcome`, `top_probability`, `unanimous_outcome` plus identity, kickoff, price and value gates. Model-only evidence is advisory here.
- `certified_model`: additionally requires the full feature schema, the distribution envelope and a sufficient calibration bucket.

## Distribution envelope

```json
{
  "agreement_ratio_max": 1.0,
  "agreement_ratio_min": 0.0,
  "empty": false,
  "top_probability_max": 0.8,
  "top_probability_min": 0.33999999999999997,
  "voters_max": 4,
  "voters_min": 2
}
```

## Calibration (certified dispatchable rules)

| rule | bucket | sample | mean predicted | observed | sufficient |
|---|---|---:|---:|---:|---|
| 1x2_two_source_p55_majority | 50-60% | 298 | 0.5729 | 0.5772 | yes |
| 1x2_two_source_p55_majority | 60-70% | 412 | 0.6443 | 0.6626 | yes |
| 1x2_two_source_p55_majority | 70-80% | 182 | 0.7338 | 0.7802 | yes |
| 1x2_two_source_p55_majority | 80-90% | 1 | 0.8 | 1.0 | no |
| 1x2_two_source_p55_unanimous | 50-60% | 287 | 0.573 | 0.5784 | yes |
| 1x2_two_source_p55_unanimous | 60-70% | 410 | 0.6445 | 0.661 | yes |
| 1x2_two_source_p55_unanimous | 70-80% | 182 | 0.7338 | 0.7802 | yes |
| 1x2_two_source_p55_unanimous | 80-90% | 1 | 0.8 | 1.0 | no |
| 1x2_two_source_p60_majority | 60-70% | 412 | 0.6443 | 0.6626 | yes |
| 1x2_two_source_p60_majority | 70-80% | 182 | 0.7338 | 0.7802 | yes |
| 1x2_two_source_p60_majority | 80-90% | 1 | 0.8 | 1.0 | no |
| 1x2_two_source_p60_unanimous | 60-70% | 410 | 0.6445 | 0.661 | yes |
| 1x2_two_source_p60_unanimous | 70-80% | 182 | 0.7338 | 0.7802 | yes |
| 1x2_two_source_p60_unanimous | 80-90% | 1 | 0.8 | 1.0 | no |
| 1x2_two_source_p65_majority | 60-70% | 179 | 0.6724 | 0.6816 | yes |
| 1x2_two_source_p65_majority | 70-80% | 182 | 0.7338 | 0.7802 | yes |
| 1x2_two_source_p65_majority | 80-90% | 1 | 0.8 | 1.0 | no |
| 1x2_two_source_p65_unanimous | 60-70% | 179 | 0.6724 | 0.6816 | yes |
| 1x2_two_source_p65_unanimous | 70-80% | 182 | 0.7338 | 0.7802 | yes |
| 1x2_two_source_p65_unanimous | 80-90% | 1 | 0.8 | 1.0 | no |

## model_health_checks

- MODEL_HEALTH: 135 fixture(s) had too few current-source voters to score — source coverage, not a model or schema fault
- MODEL_HEALTH: 10 rule(s) are research-only and can never dispatch; they are not counted as certified

No generative model is used anywhere in this lane. Every number above derives from deterministic code over captured source rows.

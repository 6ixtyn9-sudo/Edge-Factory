# model_health — fresh_production — 2026-10-01

## Model card

- model version: `fresh_production_rules_v1`
- feature schema: `fresh_production_features_v1`
- random seed: 20260930 (deterministic; no generative component)
- source universe: zulubet, statarea, vitibet, betclan, bzzoiro, predictz, windrawwin, freesupertips, afootballreport, prosoccer, soccervista
- evaluation window: 2026-07-03..2026-09-30
- training window: 180 days
- features: number_of_1x2_voters, timing_source_count, mean_home_prob, mean_draw_prob, mean_away_prob, min_top_prob, max_top_prob, std_top_prob, top_outcome, top_probability, second_probability, margin_top_vs_second, unanimous_outcome, agreement_ratio, probability_entropy, source_combination
- certification gates: {"min_walkforward_sample": 200, "min_recent_sample_30d": 25, "min_hit_rate_lower_bound": 0.55, "min_lift_over_base_rate": 0.03, "min_calibration_bucket_sample": 50, "max_ambiguity_rate": 0.05}
- certified dispatchable rules: 0
- research rules: 0
- blocked rules: 24

## Dispatch paths

- `certified_rule`: requires `number_of_1x2_voters`, `top_outcome`, `top_probability`, `unanimous_outcome` plus identity, kickoff, price and value gates. Model-only evidence is advisory here.
- `certified_model`: additionally requires the full feature schema, the distribution envelope and a sufficient calibration bucket.

## Distribution envelope

```json
{
  "agreement_ratio_max": 1.0,
  "agreement_ratio_min": 0.5,
  "empty": false,
  "top_probability_max": 0.77,
  "top_probability_min": 0.39603960396039606,
  "voters_max": 2,
  "voters_min": 2
}
```

## Calibration (certified dispatchable rules)

No certified dispatchable rule: no probability is used for dispatch.

## model_health_checks

- MODEL_HEALTH: 25 fixture(s) had too few current-source voters to score — source coverage, not a model or schema fault
- MODEL_HEALTH: no fresh_production rule is certified dispatchable — the lane abstains by design

No generative model is used anywhere in this lane. Every number above derives from deterministic code over captured source rows.

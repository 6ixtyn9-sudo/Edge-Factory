# source_health — fresh_production — 2026-10-01

- fixture groups today: 94
- groups with >= 2 current-source voters: 25
- groups with a trusted kickoff: 67
- groups flagged ambiguous: 6
- groups flagged reversed-orientation risk: 0

## Current production source universe

| source | role |
|---|---|
| afootballreport | shadow_fresh_production_voter |
| betclan | fresh_production_live_voter |
| betexplorer_odds | pricing_provider |
| betexplorer_results | result_donor |
| bettingclosed | result_donor |
| bzzoiro | fresh_production_live_voter |
| bzzoiro_odds | pricing_provider |
| freesupertips | shadow_fresh_production_voter |
| oddspapi_odds | pricing_provider |
| predictz | shadow_fresh_production_voter |
| prosoccer | shadow_fresh_production_voter |
| scoutingstats | timing_provider |
| soccervista | shadow_fresh_production_voter |
| statarea | fresh_production_live_voter |
| theoddsapi_odds | pricing_provider |
| vitibet | fresh_production_live_voter |
| windrawwin | shadow_fresh_production_voter |
| zulubet | fresh_production_live_voter |

## pricing_health

| stage | count |
|---|---:|
| candidate_count_before_pricing | 25 |
| candidate_count_with_any_price | 25 |
| candidate_count_exact_price | 23 |
| candidate_count_alias_price | 2 |
| candidate_count_suspect_price_rejected | 2 |
| candidate_count_missing_price | 0 |
| candidate_count_with_positive_edge | 12 |
| candidate_count_with_negative_edge | 13 |

Price tiers used: `dedicated_pricing_feed` × 16, `source_embedded_price` × 9

| pricing bundle | rows |
|---|---:|
| bzzoiro_odds | 0 |
| scoutingstats_odds | 185 |
| source_embedded | 178 |

## source_health_warnings

- SOURCE_HEALTH: 2 candidate(s) matched a price only through a fuzzy fixture join and were rejected for dispatch

## legacy_baseline / historical_reference

Sources below are NOT part of the fresh production universe. They are listed only so their exclusion is auditable.

| source | classification |
|---|---|
| forebet | blocked_predictor |

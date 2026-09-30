# FRESH PRODUCTION PICKS — 2026-09-30

## FRESH PRODUCTION — NO PICKS

The lane abstained. Blocker counts across 142 candidate(s):

| blocker | candidates |
|---|---:|
| `insufficient_voter_quorum` | 113 |
| `missing_odds` | 5 |
| `insufficient_edge_versus_price` | 17 |
| `missing_trusted_kickoff` | 7 |
| `kickoff_guard` | 18 |
| `no_certified_fresh_production_rule_matched` | 17 |
| `suspect_price` | 2 |

### Candidate-to-bet conversion

| stage | count |
|---|---:|
| candidate_count_before_pricing | 29 |
| candidate_count_with_any_price | 24 |
| candidate_count_exact_price | 22 |
| candidate_count_alias_price | 2 |
| candidate_count_suspect_price_rejected | 2 |
| candidate_count_missing_price | 5 |
| candidate_count_with_positive_edge | 6 |
| candidate_count_with_negative_edge | 18 |

Price tiers used: `source_embedded_price` × 16, `dedicated_pricing_feed` × 8

### Top rejected candidates

| fixture | selection | prob | odds | implied | edge | rule | blockers |
|---|---|---:|---:|---:|---:|---|---|
| Mexico vs Peru | home | 0.714 | 1.55 | 0.6452 | 0.0684 | fresh_1x2_v2_p70_majority | kickoff_guard: inside_30m_lead_or_started [already_started_or_inside_lead] |
| Cienciano vs Club Deportivo Los Chankas | home | 0.673 | 1.45 | 0.6897 | -0.0163 | fresh_1x2_v2_p65_majority | insufficient_edge_versus_price: probability 0.6734 vs implied 0.6897 at odds 1.45 (scoutingstats_odds) gives edge -0.0163, threshold 0.02 |
| Bahrain vs Yemen | home | 0.653 | 1.7 | 0.5882 | 0.0651 | fresh_1x2_v3_p65_majority | kickoff_guard: inside_30m_lead_or_started [already_started_or_inside_lead] |
| Lithuania vs Andorra | home | 0.646 | 1.7 | 0.5882 | 0.0578 | fresh_1x2_v2_p60_unanimous | kickoff_guard: inside_30m_lead_or_started [already_started_or_inside_lead] |
| Uzbekistan U23 vs Japan U23 | away | 0.615 | 1.73 | 0.578 | 0.037 | fresh_1x2_v2_p60_unanimous | missing_trusted_kickoff: kickoff_present_but_parser_missed (1 kickoff observation(s) from non-timing sources) |
| Union San Felipe vs San Luis | away | 0.590 | - | - | - | fresh_1x2_v2_p55_unanimous | missing_odds: no usable 1X2 price for this selection; bundles searched=bzzoiro_odds,scoutingstats_odds,source_embedded_odds; exact=False alias=False fuzzy_rejected=False embedded_source_price=False |
| Afc Fylde vs Carlisle | - | 0.000 | - | - | - | - | insufficient_voter_quorum: 1 current-source 1X2 voter(s), 2 required (betclan) |
| Águila vs Inter | - | 0.000 | - | - | - | - | insufficient_voter_quorum: 1 current-source 1X2 voter(s), 2 required (vitibet) |
| Aktobe W vs Ajax W | - | 0.000 | - | - | - | - | insufficient_voter_quorum: 1 current-source 1X2 voter(s), 2 required (zulubet) |
| Albania U19 vs Lithuania U19 | - | 0.000 | - | - | - | - | insufficient_voter_quorum: 1 current-source 1X2 voter(s), 2 required (zulubet) |

Abstention is the correct outcome when evidence is insufficient.

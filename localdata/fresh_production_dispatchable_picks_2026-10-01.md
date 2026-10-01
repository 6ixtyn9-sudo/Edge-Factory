# FRESH PRODUCTION PICKS — 2026-10-01

## FRESH PRODUCTION — NO PICKS

The lane abstained. Blocker counts across 115 candidate(s):

| blocker | candidates |
|---|---:|
| `insufficient_voter_quorum` | 79 |
| `missing_odds` | 6 |
| `insufficient_edge_versus_price` | 18 |
| `kickoff_guard` | 10 |
| `no_certified_fresh_production_rule_matched` | 13 |
| `ambiguous_or_missing_identity` | 18 |
| `suspect_price` | 2 |

### Candidate-to-bet conversion

| stage | count |
|---|---:|
| candidate_count_before_pricing | 36 |
| candidate_count_with_any_price | 30 |
| candidate_count_exact_price | 28 |
| candidate_count_alias_price | 2 |
| candidate_count_suspect_price_rejected | 2 |
| candidate_count_missing_price | 6 |
| candidate_count_with_positive_edge | 13 |
| candidate_count_with_negative_edge | 17 |

Price tiers used: `source_embedded_price` × 15, `dedicated_pricing_feed` × 15

### Top rejected candidates

| fixture | selection | prob | odds | implied | edge | rule | blockers |
|---|---|---:|---:|---:|---:|---|---|
| Azerbaijan vs Liechtenstein | home | 0.800 | 1.12 | 0.8929 | -0.0927 | 1x2_two_source_p70_majority | insufficient_edge_versus_price: probability 0.8002 vs implied 0.8929 at odds 1.12 (scoutingstats_odds) gives edge -0.0927, threshold 0.02 |
| Miami FC vs Sporting JAX | home | 0.756 | 1.56 | 0.641 | 0.1154 | 1x2_two_source_p70_majority | kickoff_guard: inside_30m_lead_or_started [already_started_or_inside_lead] |
| Atlético Ottawa vs Cavalry FC | away | 0.749 | 1.6 | 0.625 | 0.1236 | 1x2_two_source_p70_majority | kickoff_guard: inside_30m_lead_or_started [already_started_or_inside_lead] |
| Bnei Yehuda vs Maccabi Kiryat Gat | home | 0.730 | - | - | - | 1x2_two_source_p70_majority | missing_odds: no usable 1X2 price for this selection; bundles searched=bzzoiro_odds,scoutingstats_odds,source_embedded_odds; exact=False alias=False fuzzy_rejected=False embedded_source_price=False |
| Indonesia vs Bangladesh | home | 0.685 | 1.03 | 0.9709 | -0.2859 | 1x2_two_source_p65_majority | insufficient_edge_versus_price: probability 0.6850 vs implied 0.9709 at odds 1.03 (source_embedded_odds) gives edge -0.2859, threshold 0.02 |
| Maccabi Kabilio Jaffa vs Hapoel Acre | home | 0.645 | - | - | - | 1x2_two_source_p60_unanimous | missing_odds: no usable 1X2 price for this selection; bundles searched=bzzoiro_odds,scoutingstats_odds,source_embedded_odds; exact=False alias=False fuzzy_rejected=False embedded_source_price=False |
| Envigado vs Orsomarso | home | 0.640 | - | - | - | 1x2_two_source_p60_unanimous | missing_odds: no usable 1X2 price for this selection; bundles searched=bzzoiro_odds,scoutingstats_odds,source_embedded_odds; exact=False alias=False fuzzy_rejected=False embedded_source_price=False |
| Guinea vs Kenya | home | 0.640 | 1.57 | 0.6369 | 0.0031 | 1x2_two_source_p60_unanimous | insufficient_edge_versus_price: probability 0.6400 vs implied 0.6369 at odds 1.57 (scoutingstats_odds) gives edge +0.0031, threshold 0.02 |
| Ashdod vs Maccabi Herzliya | home | 0.615 | 1.5 | 0.6667 | -0.0514 | 1x2_two_source_p60_majority | insufficient_edge_versus_price: probability 0.6153 vs implied 0.6667 at odds 1.5 (source_embedded_odds) gives edge -0.0514, threshold 0.02 |
| Brooklyn vs Detroit City | away | 0.585 | 1.82 | 0.5495 | 0.0355 | 1x2_two_source_p55_unanimous | kickoff_guard: inside_30m_lead_or_started [already_started_or_inside_lead] |

Abstention is the correct outcome when evidence is insufficient.

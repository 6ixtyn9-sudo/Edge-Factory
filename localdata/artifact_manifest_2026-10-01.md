# artifact_manifest — data_retention — 2026-10-01

- policy: `fresh_production` (keep-days 30, keep-latest 3, target date 2026-10-01)
- files considered: 521
- files deleted: 0
- bytes deleted: 0
- unmatched files left alone: 279
- dry run: no

## Why nothing was removed

Nothing was old enough: every matched generated artifact is either the current target date, inside the newest-per-prefix window, or within the retention window. Unmatched files are never eligible.

## Kept (by reason)

| reason | files |
|---|---:|
| current_target_date | 36 |
| within_last_30_days | 134 |
| within_last_7_days | 22 |
| within_newest_3_for_prefix | 50 |

## Largest generated prefixes

| prefix | bytes |
|---|---:|
| picks_audit | 978217 |
| picks | 442707 |
| source_settlement_coverage | 319495 |
| clv_unmatched | 243578 |
| source_funnel | 127401 |
| fresh_production_candidate_picks | 77185 |
| artifact_manifest | 72192 |
| clv_report | 59847 |
| ml_fade_research_report | 34947 |
| shadow_sent_ledger | 20269 |

## Never eligible for deletion

- .git/ and all version history
- source code, tests, Config/, HANDOVER.md
- raw source captures (*.csv.gz, monthly archives)
- settled result overlays (settled_results.json)
- warehouse inputs and rolling state/ledger files
- alias and entity registries (team_aliases.json, registries)
- durable pick archives (picks_DATE.json, picks_morning_DATE.json)
- the current target date's artifacts
- the newest N dates for every generated prefix
- any file whose name does not match a known generated prefix

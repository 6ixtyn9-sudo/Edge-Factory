# artifact_manifest — data_retention — 2026-09-30

- policy: `fresh_production` (keep-days 30, keep-latest 3, target date 2026-09-30)
- files considered: 571
- files deleted: 0
- bytes deleted: 0
- unmatched files left alone: 353
- dry run: no

## Why nothing was removed

Nothing was old enough: every matched generated artifact is either the current target date, inside the newest-per-prefix window, or within the retention window. Unmatched files are never eligible.

## Kept (by reason)

| reason | files |
|---|---:|
| current_target_date | 37 |
| within_last_30_days | 134 |
| within_last_7_days | 20 |
| within_newest_3_for_prefix | 27 |

## Largest generated prefixes

| prefix | bytes |
|---|---:|
| picks_audit | 992906 |
| picks | 446001 |
| clv_unmatched | 285624 |
| fresh_production_candidate_picks | 283477 |
| source_settlement_coverage | 159031 |
| source_funnel | 62092 |
| clv_report | 59683 |
| fresh_production_walkforward | 34482 |
| artifact_manifest | 34434 |
| fresh_production_certified_edges | 33405 |

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

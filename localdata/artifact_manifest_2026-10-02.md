# artifact_manifest — data_retention — 2026-10-02

- policy: `fresh_production` (keep-days 30, keep-latest 3, target date 2026-10-02)
- files considered: 577
- files deleted: 0
- bytes deleted: 0
- unmatched files left alone: 313
- dry run: no

## Why nothing was removed

Nothing was old enough: every matched generated artifact is either the current target date, inside the newest-per-prefix window, or within the retention window. Unmatched files are never eligible.

## Kept (by reason)

| reason | files |
|---|---:|
| current_target_date | 33 |
| within_last_30_days | 133 |
| within_last_7_days | 20 |
| within_newest_3_for_prefix | 78 |

## Largest generated prefixes

| prefix | bytes |
|---|---:|
| picks_audit | 987509 |
| fresh_production_candidate_picks | 472876 |
| picks | 439528 |
| source_settlement_coverage | 400663 |
| clv_unmatched | 212611 |
| source_funnel | 200582 |
| artifact_manifest | 114952 |
| clv_report | 60279 |
| fresh_production_walkforward | 53710 |
| fresh_production_certified_edges | 51574 |

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

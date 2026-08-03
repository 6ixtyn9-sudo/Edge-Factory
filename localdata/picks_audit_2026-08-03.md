# Edge Factory — Recent picks audit (2026-07-05 to 2026-08-03)

## Overall

- archived pick rows: 87
- archived pick dates: 25
- settled picks: 74
- eligible prior 1x2 picks: 84
- unmatched result picks: 10
- ambiguous result picks: 0
- wins: 58
- hit rate: 0.783784
- priced picks: 72
- ROI: 0.052569

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-03
- same-day rows excluded: 3

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 53 / 74 matches (71.6%)
- **Both Teams to Score (BTTS)**: occurred in 40 / 74 matches (54.1%)
- **Selected Team Over 1.5 Goals**: occurred in 58 / 74 matches (78.4%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 15
- **Total Hits**: 10
- **Overall Hit Rate**: 66.7%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `goal_range_2_3`: recommended=1, hits=0, hit_rate=0.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=1, hits=0, hit_rate=0.0%
- `match_over_25`: recommended=7, hits=4, hit_rate=57.1%

## By rule

- `2way-unanimous avg_p>=70`: settled=30, wins=23, hit_rate=0.766667, ROI=0.1225
- `3way-unanimous avg_p>=65`: settled=20, wins=14, hit_rate=0.7, ROI=-0.10725
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.176667
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=16, wins=10, hit_rate=0.625, ROI=0.054375
- `SKIPPED_VETO`: settled=45, wins=38, hit_rate=0.844444, ROI=0.076778
- `WATCHLIST_NO_ODDS`: settled=2, wins=1, hit_rate=0.5, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=11, wins=9, hit_rate=0.818182, ROI=-0.049091

## By odds source

- `UNKNOWN`: settled=2, wins=1, hit_rate=0.5, ROI=None
- `betexplorer_odds`: settled=40, wins=34, hit_rate=0.85, ROI=0.09725
- `bzzoiro_odds`: settled=19, wins=17, hit_rate=0.894737, ROI=0.262368
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=10, wins=5, hit_rate=0.5, ROI=-0.331
- `zulubet`: settled=1, wins=0, hit_rate=0.0, ROI=-1.0

## By odds match method

- `alias_fuzzy`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.183333
- `betexplorer`: settled=40, wins=34, hit_rate=0.85, ROI=0.09725
- `exact`: settled=26, wins=20, hit_rate=0.769231, ROI=0.085577
- `fallback`: settled=3, wins=1, hit_rate=0.333333, ROI=-0.593333
- `none`: settled=2, wins=1, hit_rate=0.5, ROI=None
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:


## Unmatched result examples

- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — South Hobart vs Ulverstone -> HOME @ 1.02 (unmatched_result); keys=['southhoba']/['ulverston']
- 2026-08-02 `CAUTION` `2way-unanimous avg_p>=70` — AIK Stockholm vs Orgryte IS -> HOME @ 1.52 (unmatched_result); keys=['aikstockh']/['orgryteis']
- 2026-08-02 `CAUTION` `2way-unanimous avg_p>=70` — Dinamo Brest vs Belshina -> HOME @ 1.32 (unmatched_result); keys=['dinamobre']/['belshina', 'belshinab']
- 2026-08-02 `CAUTION` `2way-unanimous avg_p>=70` — Kongsvinger vs Strommen -> HOME @ 1.33 (unmatched_result); keys=['kongsving']/['strommen']
- 2026-08-02 `CAUTION` `3way-unanimous avg_p>=65` — Noah vs Syunik -> HOME @ 1.31 (unmatched_result); keys=['noah']/['syunik']
- 2026-08-02 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Independiente del Valle vs Deportivo Cuenca -> HOME @ 1.33 (unmatched_result); keys=['independi']/['cuenca']
- 2026-08-02 `SKIPPED_VETO` `3way-unanimous avg_p>=65` — Ludogorets vs Botev Vratsa -> HOME @ 1.4 (unmatched_result); keys=['ludogoret']/['botevvrat']
- 2026-08-02 `SKIPPED_VETO` `3way-unanimous avg_p>=65` — ODD Ballklubb vs Asane -> HOME @ 1.4 (unmatched_result); keys=['oddballkl']/['asane']
- 2026-08-02 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Dunajska Streda vs Dukla Banska Bystrica -> HOME @ None (unmatched_result); keys=['dunajskas']/['duklabans']
- 2026-08-02 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous avg_p>=70` — Clarence Zebras vs Ulverstone -> HOME @ 1.23 (unmatched_result); keys=['clarencez']/['ulverston']

## Ambiguous result examples

- none

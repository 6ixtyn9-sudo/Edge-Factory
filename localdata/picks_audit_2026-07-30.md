# Edge Factory — Recent picks audit (2026-07-01 to 2026-07-30)

## Overall

- archived pick rows: 49
- archived pick dates: 17
- settled picks: 45
- eligible prior 1x2 picks: 45
- unmatched result picks: 0
- ambiguous result picks: 0
- wins: 39
- hit rate: 0.866667
- priced picks: 45
- ROI: 0.136444

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-30
- same-day rows excluded: 4

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 30 / 45 matches (66.7%)
- **Both Teams to Score (BTTS)**: occurred in 23 / 45 matches (51.1%)
- **Selected Team Over 1.5 Goals**: occurred in 36 / 45 matches (80.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 1
- **Total Hits**: 1
- **Overall Hit Rate**: 100.0%

### Breakdown by Enhancement Type:
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%

## By rule

- `2way-unanimous avg_p>=70`: settled=15, wins=14, hit_rate=0.933333, ROI=0.315333
- `3way-unanimous avg_p>=65`: settled=6, wins=4, hit_rate=0.666667, ROI=-0.181667
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.176667
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=6, wins=5, hit_rate=0.833333, ROI=0.493333
- `SKIPPED_VETO`: settled=33, wins=29, hit_rate=0.878788, ROI=0.109394
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333, ROI=-0.071667

## By odds source

- `betexplorer_odds`: settled=31, wins=27, hit_rate=0.870968, ROI=0.109355
- `bzzoiro_odds`: settled=8, wins=8, hit_rate=1.0, ROI=0.47
- `forebet_best`: settled=1, wins=1, hit_rate=1.0, ROI=0.22
- `scoutingstats_odds`: settled=5, wins=3, hit_rate=0.6, ROI=-0.246

## By odds match method

- `betexplorer`: settled=31, wins=27, hit_rate=0.870968, ROI=0.109355
- `exact`: settled=13, wins=11, hit_rate=0.846154, ROI=0.194615
- `fallback`: settled=1, wins=1, hit_rate=1.0, ROI=0.22
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:


## Unmatched result examples

- none

## Ambiguous result examples

- none

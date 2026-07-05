# Edge Factory — Recent picks audit (2026-06-06 to 2026-07-05)

## Overall

- archived pick rows: 91
- archived pick dates: 17
- settled picks: 79
- eligible prior 1x2 picks: 81
- unmatched result picks: 2
- ambiguous result picks: 0
- wins: 59
- hit rate: 0.746835
- priced picks: 65
- ROI: 0.060123

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-05
- same-day rows excluded: 10

## By rule

- `2way-unanimous avg_p>=65`: settled=18, wins=12, hit_rate=0.666667, ROI=-0.082941
- `2way-unanimous avg_p>=70`: settled=17, wins=14, hit_rate=0.823529, ROI=0.07
- `3way-unanimous avg_p>=65`: settled=32, wins=22, hit_rate=0.6875, ROI=0.039214
- `3way-unanimous min_p>=60 avg_p>=60`: settled=12, wins=11, hit_rate=0.916667, ROI=0.326364

## By bucket

- `CAUTION`: settled=25, wins=18, hit_rate=0.72, ROI=-0.08444
- `SKIPPED_VETO`: settled=46, wins=37, hit_rate=0.804348, ROI=0.150475
- `WATCHLIST_NO_ODDS`: settled=8, wins=4, hit_rate=0.5, ROI=None

## By odds source

- `UNKNOWN`: settled=14, wins=8, hit_rate=0.571429, ROI=None
- `bzzoiro_odds`: settled=14, wins=11, hit_rate=0.785714, ROI=0.084143
- `forebet_best`: settled=31, wins=26, hit_rate=0.83871, ROI=0.154194
- `scoutingstats_odds`: settled=6, wins=5, hit_rate=0.833333, ROI=0.07
- `zulubet`: settled=14, wins=9, hit_rate=0.642857, ROI=-0.176429

## By odds match method

- `exact`: settled=20, wins=16, hit_rate=0.8, ROI=0.0799
- `fallback`: settled=45, wins=35, hit_rate=0.777778, ROI=0.051333
- `none`: settled=14, wins=8, hit_rate=0.571429, ROI=None

## Unmatched result examples

- 2026-06-20 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Tuggeranong United vs Canberra White Eagles -> HOME @ 1.4 (unmatched_result); keys=['tuggerano']/['canberraw']
- 2026-07-04 `WATCHLIST_UNKNOWN_CTX` `3way-unanimous min_p>=60 avg_p>=60` — Launceston City vs Launceston United -> HOME @ 1.08 (unmatched_result); keys=['launcesto', 'launcestoncity']/['launcesto', 'launcestonunit']

## Ambiguous result examples

- none

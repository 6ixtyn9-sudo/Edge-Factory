# Edge Factory — Recent picks audit (2026-06-04 to 2026-07-03)

## Overall

- archived pick rows: 68
- archived pick dates: 15
- settled picks: 56
- eligible prior 1x2 picks: 57
- unmatched result picks: 1
- ambiguous result picks: 0
- wins: 42
- hit rate: 0.75
- priced picks: 44
- ROI: 0.060182

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-03
- same-day rows excluded: 11

## By rule

- `2way-unanimous avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.131429
- `2way-unanimous avg_p>=70`: settled=17, wins=14, hit_rate=0.823529, ROI=0.07
- `3way-unanimous avg_p>=65`: settled=32, wins=22, hit_rate=0.6875, ROI=0.039214

## By bucket

- `CAUTION`: settled=23, wins=17, hit_rate=0.73913, ROI=-0.054826
- `SKIPPED_VETO`: settled=25, wins=21, hit_rate=0.84, ROI=0.186143
- `WATCHLIST_NO_ODDS`: settled=8, wins=4, hit_rate=0.5, ROI=None

## By odds source

- `UNKNOWN`: settled=12, wins=7, hit_rate=0.583333, ROI=None
- `bzzoiro_odds`: settled=12, wins=9, hit_rate=0.75, ROI=0.052333
- `forebet_best`: settled=20, wins=16, hit_rate=0.8, ROI=0.0785
- `scoutingstats_odds`: settled=3, wins=3, hit_rate=1.0, ROI=0.15
- `zulubet`: settled=9, wins=7, hit_rate=0.777778, ROI=0.0

## By odds match method

- `exact`: settled=15, wins=12, hit_rate=0.8, ROI=0.071867
- `fallback`: settled=29, wins=23, hit_rate=0.793103, ROI=0.054138
- `none`: settled=12, wins=7, hit_rate=0.583333, ROI=None

## Unmatched result examples

- 2026-06-20 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Tuggeranong United vs Canberra White Eagles -> HOME @ 1.4 (unmatched_result); keys=['tuggerano']/['canberraw']

## Ambiguous result examples

- none

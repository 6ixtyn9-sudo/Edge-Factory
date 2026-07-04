# Edge Factory — Recent picks audit (2026-06-05 to 2026-07-04)

## Overall

- archived pick rows: 81
- archived pick dates: 16
- settled picks: 66
- eligible prior 1x2 picks: 69
- unmatched result picks: 3
- ambiguous result picks: 0
- wins: 51
- hit rate: 0.772727
- priced picks: 52
- ROI: 0.131115

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-04
- same-day rows excluded: 12

## By rule

- `2way-unanimous avg_p>=65`: settled=8, wins=6, hit_rate=0.75, ROI=0.131429
- `2way-unanimous avg_p>=70`: settled=17, wins=14, hit_rate=0.823529, ROI=0.07
- `3way-unanimous avg_p>=65`: settled=32, wins=22, hit_rate=0.6875, ROI=0.039214
- `3way-unanimous min_p>=60 avg_p>=60`: settled=9, wins=9, hit_rate=1.0, ROI=0.52125

## By bucket

- `CAUTION`: settled=23, wins=17, hit_rate=0.73913, ROI=-0.054826
- `SKIPPED_VETO`: settled=35, wins=30, hit_rate=0.857143, ROI=0.278586
- `WATCHLIST_NO_ODDS`: settled=8, wins=4, hit_rate=0.5, ROI=None

## By odds source

- `UNKNOWN`: settled=14, wins=8, hit_rate=0.571429, ROI=None
- `bzzoiro_odds`: settled=13, wins=10, hit_rate=0.769231, ROI=0.073692
- `forebet_best`: settled=25, wins=21, hit_rate=0.84, ROI=0.1776
- `scoutingstats_odds`: settled=5, wins=5, hit_rate=1.0, ROI=0.284
- `zulubet`: settled=9, wins=7, hit_rate=0.777778, ROI=0.0

## By odds match method

- `exact`: settled=18, wins=15, hit_rate=0.833333, ROI=0.132111
- `fallback`: settled=34, wins=28, hit_rate=0.823529, ROI=0.130588
- `none`: settled=14, wins=8, hit_rate=0.571429, ROI=None

## Unmatched result examples

- 2026-06-20 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Tuggeranong United vs Canberra White Eagles -> HOME @ 1.4 (unmatched_result); keys=['tuggerano']/['canberraw']
- 2026-07-03 `CAUTION` `2way-unanimous avg_p>=65` — Riga vs FS Jelgava -> HOME @ 1.15 (unmatched_result); keys=['riga']/['fsjelgava']
- 2026-07-03 `SKIPPED_VETO` `2way-unanimous avg_p>=65` — Sirius vs Mjallby AIF -> HOME @ 1.67 (unmatched_result); keys=['sirius']/['mjallbyai']

## Ambiguous result examples

- none

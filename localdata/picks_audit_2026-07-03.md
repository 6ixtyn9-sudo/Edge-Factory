# Edge Factory — Recent picks audit (2026-06-04 to 2026-07-03)

## Overall

- archived pick rows: 65
- archived pick dates: 15
- settled picks: 52
- wins: 40
- hit rate: 0.769231
- priced picks: 43
- ROI: 0.084837

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-03
- same-day rows excluded: 8

## By rule

- `2way-unanimous avg_p>=65`: settled=6, wins=6, hit_rate=1.0, ROI=0.32
- `2way-unanimous avg_p>=70`: settled=14, wins=12, hit_rate=0.857143, ROI=0.07
- `3way-unanimous avg_p>=65`: settled=32, wins=22, hit_rate=0.6875, ROI=0.039214

## By bucket

- `CAUTION`: settled=23, wins=17, hit_rate=0.73913, ROI=-0.054826
- `SKIPPED_VETO`: settled=23, wins=21, hit_rate=0.913043, ROI=0.24545
- `WATCHLIST_NO_ODDS`: settled=6, wins=2, hit_rate=0.333333, ROI=None

## By odds source

- `UNKNOWN`: settled=9, wins=5, hit_rate=0.555556, ROI=None
- `bzzoiro_odds`: settled=12, wins=9, hit_rate=0.75, ROI=0.052333
- `forebet_best`: settled=20, wins=16, hit_rate=0.8, ROI=0.0785
- `scoutingstats_odds`: settled=3, wins=3, hit_rate=1.0, ROI=0.15
- `zulubet`: settled=8, wins=7, hit_rate=0.875, ROI=0.125

## By odds match method

- `exact`: settled=15, wins=12, hit_rate=0.8, ROI=0.071867
- `fallback`: settled=28, wins=23, hit_rate=0.821429, ROI=0.091786
- `none`: settled=9, wins=5, hit_rate=0.555556, ROI=None

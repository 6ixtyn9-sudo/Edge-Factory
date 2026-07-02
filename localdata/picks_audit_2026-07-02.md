# Edge Factory — Recent picks audit (2026-06-03 to 2026-07-02)

## Overall

- archived pick rows: 56
- archived pick dates: 14
- settled picks: 48
- wins: 37
- hit rate: 0.770833
- priced picks: 40
- ROI: 0.07095

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-02
- same-day rows excluded: 4

## By rule

- `2way-unanimous avg_p>=65`: settled=6, wins=6, hit_rate=1.0, ROI=0.32
- `2way-unanimous avg_p>=70`: settled=14, wins=12, hit_rate=0.857143, ROI=0.07
- `3way-unanimous avg_p>=65`: settled=28, wins=19, hit_rate=0.678571, ROI=0.01152

## By bucket

- `CAUTION`: settled=22, wins=16, hit_rate=0.727273, ROI=-0.063682
- `SKIPPED_VETO`: settled=21, wins=19, hit_rate=0.904762, ROI=0.2355
- `WATCHLIST_NO_ODDS`: settled=5, wins=2, hit_rate=0.4, ROI=None

## By odds source

- `UNKNOWN`: settled=8, wins=5, hit_rate=0.625, ROI=None
- `bzzoiro_odds`: settled=11, wins=8, hit_rate=0.727273, ROI=0.024364
- `forebet_best`: settled=20, wins=16, hit_rate=0.8, ROI=0.0785
- `scoutingstats_odds`: settled=2, wins=2, hit_rate=1.0, ROI=0.155
- `zulubet`: settled=7, wins=6, hit_rate=0.857143, ROI=0.098571

## By odds match method

- `exact`: settled=13, wins=10, hit_rate=0.769231, ROI=0.044462
- `fallback`: settled=27, wins=22, hit_rate=0.814815, ROI=0.083704
- `none`: settled=8, wins=5, hit_rate=0.625, ROI=None

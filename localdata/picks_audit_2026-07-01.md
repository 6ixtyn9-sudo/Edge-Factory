# Edge Factory — Recent picks audit (2026-06-02 to 2026-07-01)

## Overall

- archived pick rows: 52
- archived pick dates: 13
- settled picks: 44
- wins: 33
- hit rate: 0.75
- priced picks: 36
- ROI: 0.032444

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-01
- same-day rows excluded: 4

## By rule

- `2way-unanimous avg_p>=65`: settled=4, wins=4, hit_rate=1.0, ROI=0.2625
- `2way-unanimous avg_p>=70`: settled=14, wins=12, hit_rate=0.857143, ROI=0.07
- `3way-unanimous avg_p>=65`: settled=26, wins=17, hit_rate=0.653846, ROI=-0.022261

## By bucket

- `CAUTION`: settled=22, wins=16, hit_rate=0.727273, ROI=-0.063682
- `SKIPPED_VETO`: settled=17, wins=15, hit_rate=0.882353, ROI=0.1835
- `WATCHLIST_NO_ODDS`: settled=5, wins=2, hit_rate=0.4, ROI=None

## By odds source

- `UNKNOWN`: settled=8, wins=5, hit_rate=0.625, ROI=None
- `bzzoiro_odds`: settled=10, wins=7, hit_rate=0.7, ROI=-0.0052
- `forebet_best`: settled=17, wins=13, hit_rate=0.764706, ROI=0.012941
- `scoutingstats_odds`: settled=2, wins=2, hit_rate=1.0, ROI=0.155
- `zulubet`: settled=7, wins=6, hit_rate=0.857143, ROI=0.098571

## By odds match method

- `exact`: settled=12, wins=9, hit_rate=0.75, ROI=0.0215
- `fallback`: settled=24, wins=19, hit_rate=0.791667, ROI=0.037917
- `none`: settled=8, wins=5, hit_rate=0.625, ROI=None

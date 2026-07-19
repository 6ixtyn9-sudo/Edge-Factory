# Edge Factory — Recent picks audit (2026-06-20 to 2026-07-19)

## Overall

- archived pick rows: 31
- archived pick dates: 11
- settled picks: 29
- eligible prior 1x2 picks: 31
- unmatched result picks: 2
- ambiguous result picks: 0
- wins: 21
- hit rate: 0.724138
- priced picks: 29
- ROI: -0.097586

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-19
- same-day rows excluded: 0

## By rule

- `2way-unanimous avg_p>=70`: settled=9, wins=6, hit_rate=0.666667, ROI=-0.124444
- `3way-unanimous avg_p>=65`: settled=3, wins=1, hit_rate=0.333333, ROI=-0.646667
- `3way-unanimous home-only avg_p>=60`: settled=1, wins=1, hit_rate=1.0, ROI=0.32
- `3way-unanimous home-only avg_p>=65`: settled=16, wins=13, hit_rate=0.8125, ROI=-0.005625

## By bucket

- `CAUTION`: settled=7, wins=3, hit_rate=0.428571, ROI=-0.341429
- `SKIPPED_VETO`: settled=18, wins=15, hit_rate=0.833333, ROI=0.023889
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.2175

## By odds source

- `betexplorer_odds`: settled=20, wins=16, hit_rate=0.8, ROI=-0.046
- `bzzoiro_odds`: settled=4, wins=4, hit_rate=1.0, ROI=0.44
- `scoutingstats_odds`: settled=5, wins=1, hit_rate=0.2, ROI=-0.734

## By odds match method

- `betexplorer`: settled=20, wins=16, hit_rate=0.8, ROI=-0.046
- `exact`: settled=9, wins=5, hit_rate=0.555556, ROI=-0.212222

## Unmatched result examples

- 2026-07-11 `CAUTION` `2way-unanimous avg_p>=70` — Guangzhou E-Power vs Hebei Kungfu -> HOME @ 2.29 (unmatched_result); keys=['guangzhou']/['hebeikung']
- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Shaanxi Union vs Meizhou Kejia -> HOME @ 1.49 (unmatched_result); keys=['shaanxiun']/['meizhouke']

## Ambiguous result examples

- none

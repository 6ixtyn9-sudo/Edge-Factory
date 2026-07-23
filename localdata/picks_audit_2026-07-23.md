# Edge Factory — Recent picks audit (2026-06-24 to 2026-07-23)

## Overall

- archived pick rows: 44
- archived pick dates: 15
- settled picks: 40
- eligible prior 1x2 picks: 42
- unmatched result picks: 2
- ambiguous result picks: 0
- wins: 31
- hit rate: 0.775
- priced picks: 40
- ROI: 0.0065

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-23
- same-day rows excluded: 2

## By rule

- `2way-unanimous avg_p>=70`: settled=11, wins=8, hit_rate=0.727273, ROI=-0.043636
- `3way-unanimous avg_p>=65`: settled=3, wins=1, hit_rate=0.333333, ROI=-0.646667
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=16, wins=13, hit_rate=0.8125, ROI=-0.005625

## By bucket

- `CAUTION`: settled=7, wins=3, hit_rate=0.428571, ROI=-0.341429
- `SKIPPED_VETO`: settled=28, wins=24, hit_rate=0.857143, ROI=0.117857
- `WATCHLIST_UNKNOWN_CTX`: settled=5, wins=4, hit_rate=0.8, ROI=-0.13

## By odds source

- `betexplorer_odds`: settled=28, wins=23, hit_rate=0.821429, ROI=0.0125
- `bzzoiro_odds`: settled=6, wins=6, hit_rate=1.0, ROI=0.56
- `scoutingstats_odds`: settled=6, wins=2, hit_rate=0.333333, ROI=-0.575

## By odds match method

- `betexplorer`: settled=28, wins=23, hit_rate=0.821429, ROI=0.0125
- `exact`: settled=12, wins=8, hit_rate=0.666667, ROI=-0.0075

## Unmatched result examples

- 2026-07-11 `CAUTION` `2way-unanimous avg_p>=70` — Guangzhou E-Power vs Hebei Kungfu -> HOME @ 2.29 (unmatched_result); keys=['guangzhou']/['hebeikung']
- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Shaanxi Union vs Meizhou Kejia -> HOME @ 1.49 (unmatched_result); keys=['shaanxiun']/['meizhouke']

## Ambiguous result examples

- none

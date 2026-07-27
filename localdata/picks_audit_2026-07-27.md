# Edge Factory — Recent picks audit (2026-06-28 to 2026-07-27)

## Overall

- archived pick rows: 53
- archived pick dates: 17
- settled picks: 45
- eligible prior 1x2 picks: 47
- unmatched result picks: 2
- ambiguous result picks: 0
- wins: 35
- hit rate: 0.777778
- priced picks: 45
- ROI: 0.017778

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-27
- same-day rows excluded: 6

## By rule

- `2way-unanimous avg_p>=70`: settled=14, wins=11, hit_rate=0.785714, ROI=0.066429
- `3way-unanimous avg_p>=65`: settled=5, wins=2, hit_rate=0.4, ROI=-0.562
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=16, wins=13, hit_rate=0.8125, ROI=-0.005625

## By bucket

- `CAUTION`: settled=8, wins=4, hit_rate=0.5, ROI=-0.16625
- `SKIPPED_VETO`: settled=31, wins=26, hit_rate=0.83871, ROI=0.082581
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333, ROI=-0.071667

## By odds source

- `betexplorer_odds`: settled=29, wins=24, hit_rate=0.827586, ROI=0.016552
- `bzzoiro_odds`: settled=9, wins=8, hit_rate=0.888889, ROI=0.394444
- `scoutingstats_odds`: settled=7, wins=3, hit_rate=0.428571, ROI=-0.461429

## By odds match method

- `betexplorer`: settled=29, wins=24, hit_rate=0.827586, ROI=0.016552
- `exact`: settled=16, wins=11, hit_rate=0.6875, ROI=0.02

## Unmatched result examples

- 2026-07-11 `CAUTION` `2way-unanimous avg_p>=70` — Guangzhou E-Power vs Hebei Kungfu -> HOME @ 2.29 (unmatched_result); keys=['guangzhou']/['hebeikung']
- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Shaanxi Union vs Meizhou Kejia -> HOME @ 1.49 (unmatched_result); keys=['shaanxiun']/['meizhouke']

## Ambiguous result examples

- none

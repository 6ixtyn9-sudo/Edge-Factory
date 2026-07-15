# Edge Factory — Recent picks audit (2026-06-16 to 2026-07-15)

## Overall

- archived pick rows: 27
- archived pick dates: 10
- settled picks: 23
- eligible prior 1x2 picks: 25
- unmatched result picks: 2
- ambiguous result picks: 0
- wins: 17
- hit rate: 0.73913
- priced picks: 23
- ROI: -0.085217

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-15
- same-day rows excluded: 2

## By rule

- `2way-unanimous avg_p>=70`: settled=7, wins=4, hit_rate=0.571429, ROI=-0.267143
- `3way-unanimous home-only avg_p>=65`: settled=16, wins=13, hit_rate=0.8125, ROI=-0.005625

## By bucket

- `CAUTION`: settled=6, wins=2, hit_rate=0.333333, ROI=-0.521667
- `SKIPPED_VETO`: settled=14, wins=13, hit_rate=0.928571, ROI=0.15
- `WATCHLIST_UNKNOWN_CTX`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.31

## By odds source

- `betexplorer_odds`: settled=15, wins=13, hit_rate=0.866667, ROI=0.046
- `bzzoiro_odds`: settled=3, wins=3, hit_rate=1.0, ROI=0.34
- `scoutingstats_odds`: settled=5, wins=1, hit_rate=0.2, ROI=-0.734

## By odds match method

- `betexplorer`: settled=15, wins=13, hit_rate=0.866667, ROI=0.046
- `exact`: settled=8, wins=4, hit_rate=0.5, ROI=-0.33125

## Unmatched result examples

- 2026-07-11 `CAUTION` `2way-unanimous avg_p>=70` — Guangzhou E-Power vs Hebei Kungfu -> HOME @ 2.29 (unmatched_result); keys=['guangzhou']/['hebeikung']
- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Shaanxi Union vs Meizhou Kejia -> HOME @ 1.49 (unmatched_result); keys=['shaanxiun']/['meizhouke']

## Ambiguous result examples

- none

# Edge Factory — Recent picks audit (2026-06-14 to 2026-07-13)

## Overall

- archived pick rows: 19
- archived pick dates: 8
- settled picks: 16
- eligible prior 1x2 picks: 18
- unmatched result picks: 2
- ambiguous result picks: 0
- wins: 11
- hit rate: 0.6875
- priced picks: 16
- ROI: -0.12125

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-13
- same-day rows excluded: 1

## By rule

- `2way-unanimous avg_p>=70`: settled=5, wins=3, hit_rate=0.6, ROI=-0.244
- `3way-unanimous home-only avg_p>=65`: settled=11, wins=8, hit_rate=0.727273, ROI=-0.065455

## By bucket

- `CAUTION`: settled=6, wins=2, hit_rate=0.333333, ROI=-0.521667
- `SKIPPED_VETO`: settled=8, wins=7, hit_rate=0.875, ROI=0.14
- `WATCHLIST_UNKNOWN_CTX`: settled=2, wins=2, hit_rate=1.0, ROI=0.035

## By odds source

- `betexplorer_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.08875
- `bzzoiro_odds`: settled=3, wins=3, hit_rate=1.0, ROI=0.34
- `scoutingstats_odds`: settled=5, wins=1, hit_rate=0.2, ROI=-0.734

## By odds match method

- `betexplorer`: settled=8, wins=7, hit_rate=0.875, ROI=0.08875
- `exact`: settled=8, wins=4, hit_rate=0.5, ROI=-0.33125

## Unmatched result examples

- 2026-07-11 `CAUTION` `2way-unanimous avg_p>=70` — Guangzhou E-Power vs Hebei Kungfu -> HOME @ 2.29 (unmatched_result); keys=['guangzhou']/['hebeikung']
- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Shaanxi Union vs Meizhou Kejia -> HOME @ 1.49 (unmatched_result); keys=['shaanxiun']/['meizhouke']

## Ambiguous result examples

- none

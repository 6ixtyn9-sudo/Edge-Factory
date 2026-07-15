# Edge Factory — Recent picks audit (2026-06-15 to 2026-07-14)

## Overall

- archived pick rows: 25
- archived pick dates: 9
- settled picks: 17
- eligible prior 1x2 picks: 19
- unmatched result picks: 2
- ambiguous result picks: 0
- wins: 11
- hit rate: 0.647059
- priced picks: 17
- ROI: -0.172941

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-14
- same-day rows excluded: 6

## By rule

- `2way-unanimous avg_p>=70`: settled=6, wins=3, hit_rate=0.5, ROI=-0.37
- `3way-unanimous home-only avg_p>=65`: settled=11, wins=8, hit_rate=0.727273, ROI=-0.065455

## By bucket

- `CAUTION`: settled=6, wins=2, hit_rate=0.333333, ROI=-0.521667
- `SKIPPED_VETO`: settled=8, wins=7, hit_rate=0.875, ROI=0.14
- `WATCHLIST_UNKNOWN_CTX`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.31

## By odds source

- `betexplorer_odds`: settled=9, wins=7, hit_rate=0.777778, ROI=-0.032222
- `bzzoiro_odds`: settled=3, wins=3, hit_rate=1.0, ROI=0.34
- `scoutingstats_odds`: settled=5, wins=1, hit_rate=0.2, ROI=-0.734

## By odds match method

- `betexplorer`: settled=9, wins=7, hit_rate=0.777778, ROI=-0.032222
- `exact`: settled=8, wins=4, hit_rate=0.5, ROI=-0.33125

## Unmatched result examples

- 2026-07-11 `CAUTION` `2way-unanimous avg_p>=70` — Guangzhou E-Power vs Hebei Kungfu -> HOME @ 2.29 (unmatched_result); keys=['guangzhou']/['hebeikung']
- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Shaanxi Union vs Meizhou Kejia -> HOME @ 1.49 (unmatched_result); keys=['shaanxiun']/['meizhouke']

## Ambiguous result examples

- none

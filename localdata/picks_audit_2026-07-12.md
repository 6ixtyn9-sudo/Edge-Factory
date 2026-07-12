# Edge Factory — Recent picks audit (2026-06-13 to 2026-07-12)

## Overall

- archived pick rows: 18
- archived pick dates: 7
- settled picks: 14
- eligible prior 1x2 picks: 16
- unmatched result picks: 2
- ambiguous result picks: 0
- wins: 10
- hit rate: 0.714286
- priced picks: 14
- ROI: -0.089286

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-12
- same-day rows excluded: 2

## By rule

- `2way-unanimous avg_p>=70`: settled=5, wins=3, hit_rate=0.6, ROI=-0.244
- `3way-unanimous home-only avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=-0.003333

## By bucket

- `CAUTION`: settled=5, wins=2, hit_rate=0.4, ROI=-0.426
- `SKIPPED_VETO`: settled=7, wins=6, hit_rate=0.857143, ROI=0.115714
- `WATCHLIST_UNKNOWN_CTX`: settled=2, wins=2, hit_rate=1.0, ROI=0.035

## By odds source

- `betexplorer_odds`: settled=7, wins=6, hit_rate=0.857143, ROI=0.057143
- `bzzoiro_odds`: settled=3, wins=3, hit_rate=1.0, ROI=0.34
- `scoutingstats_odds`: settled=4, wins=1, hit_rate=0.25, ROI=-0.6675

## By odds match method

- `betexplorer`: settled=7, wins=6, hit_rate=0.857143, ROI=0.057143
- `exact`: settled=7, wins=4, hit_rate=0.571429, ROI=-0.235714

## Unmatched result examples

- 2026-07-11 `CAUTION` `2way-unanimous avg_p>=70` — Guangzhou E-Power vs Hebei Kungfu -> HOME @ 2.29 (unmatched_result); keys=['guangzhou']/['hebeikung']
- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Shaanxi Union vs Meizhou Kejia -> HOME @ 1.49 (unmatched_result); keys=['shaanxiun']/['meizhouke']

## Ambiguous result examples

- none

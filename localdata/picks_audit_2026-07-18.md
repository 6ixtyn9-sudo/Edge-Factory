# Edge Factory — Recent picks audit (2026-06-19 to 2026-07-18)

## Overall

- archived pick rows: 31
- archived pick dates: 11
- settled picks: 25
- eligible prior 1x2 picks: 27
- unmatched result picks: 2
- ambiguous result picks: 0
- wins: 19
- hit rate: 0.76
- priced picks: 25
- ROI: -0.036

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-18
- same-day rows excluded: 4

## By rule

- `2way-unanimous avg_p>=70`: settled=8, wins=5, hit_rate=0.625, ROI=-0.14125
- `3way-unanimous home-only avg_p>=60`: settled=1, wins=1, hit_rate=1.0, ROI=0.32
- `3way-unanimous home-only avg_p>=65`: settled=16, wins=13, hit_rate=0.8125, ROI=-0.005625

## By bucket

- `CAUTION`: settled=7, wins=3, hit_rate=0.428571, ROI=-0.341429
- `SKIPPED_VETO`: settled=15, wins=14, hit_rate=0.933333, ROI=0.161333
- `WATCHLIST_UNKNOWN_CTX`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.31

## By odds source

- `betexplorer_odds`: settled=16, wins=14, hit_rate=0.875, ROI=0.063125
- `bzzoiro_odds`: settled=4, wins=4, hit_rate=1.0, ROI=0.44
- `scoutingstats_odds`: settled=5, wins=1, hit_rate=0.2, ROI=-0.734

## By odds match method

- `betexplorer`: settled=16, wins=14, hit_rate=0.875, ROI=0.063125
- `exact`: settled=9, wins=5, hit_rate=0.555556, ROI=-0.212222

## Unmatched result examples

- 2026-07-11 `CAUTION` `2way-unanimous avg_p>=70` — Guangzhou E-Power vs Hebei Kungfu -> HOME @ 2.29 (unmatched_result); keys=['guangzhou']/['hebeikung']
- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Shaanxi Union vs Meizhou Kejia -> HOME @ 1.49 (unmatched_result); keys=['shaanxiun']/['meizhouke']

## Ambiguous result examples

- none

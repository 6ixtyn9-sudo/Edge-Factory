# Edge Factory — Recent picks audit (2026-06-29 to 2026-07-28)

## Overall

- archived pick rows: 54
- archived pick dates: 18
- settled picks: 52
- eligible prior 1x2 picks: 53
- unmatched result picks: 1
- ambiguous result picks: 0
- wins: 42
- hit rate: 0.807692
- priced picks: 52
- ROI: 0.087692

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-28
- same-day rows excluded: 1

## By rule

- `2way-unanimous avg_p>=70`: settled=19, wins=16, hit_rate=0.842105, ROI=0.183684
- `3way-unanimous avg_p>=65`: settled=7, wins=4, hit_rate=0.571429, ROI=-0.23
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=16, wins=13, hit_rate=0.8125, ROI=-0.005625

## By bucket

- `CAUTION`: settled=11, wins=7, hit_rate=0.636364, ROI=0.105455
- `SKIPPED_VETO`: settled=35, wins=30, hit_rate=0.857143, ROI=0.109429
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333, ROI=-0.071667

## By odds source

- `betexplorer_odds`: settled=34, wins=29, hit_rate=0.852941, ROI=0.092647
- `bzzoiro_odds`: settled=10, wins=9, hit_rate=0.9, ROI=0.442
- `forebet_best`: settled=1, wins=1, hit_rate=1.0, ROI=0.22
- `scoutingstats_odds`: settled=7, wins=3, hit_rate=0.428571, ROI=-0.461429

## By odds match method

- `betexplorer`: settled=34, wins=29, hit_rate=0.852941, ROI=0.092647
- `exact`: settled=17, wins=12, hit_rate=0.705882, ROI=0.07
- `fallback`: settled=1, wins=1, hit_rate=1.0, ROI=0.22

## Unmatched result examples

- 2026-07-27 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Metta / LU vs Tukums II -> HOME @ 1.07 (unmatched_result); keys=['mettalu']/['tukums', 'tukumsii']

## Ambiguous result examples

- none

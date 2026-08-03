# Edge Factory — Recent picks audit (2026-06-26 to 2026-07-25)

## Overall

- archived pick rows: 138
- archived pick dates: 30
- settled picks: 113
- eligible prior 1x2 picks: 127
- unmatched result picks: 14
- ambiguous result picks: 0
- wins: 82
- hit rate: 0.725664
- priced picks: 102
- ROI: -0.020755

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-25
- same-day rows excluded: 11

## By rule

- `2way-unanimous avg_p>=65`: settled=11, wins=7, hit_rate=0.636364, ROI=-0.216364
- `2way-unanimous avg_p>=70`: settled=34, wins=23, hit_rate=0.676471, ROI=-0.137407
- `3way-unanimous avg_p>=65`: settled=30, wins=19, hit_rate=0.633333, ROI=-0.085074
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=16, wins=13, hit_rate=0.8125, ROI=-0.005625
- `3way-unanimous min_p>=60 avg_p>=60`: settled=12, wins=11, hit_rate=0.916667, ROI=0.326364

## By bucket

- `CAUTION`: settled=26, wins=12, hit_rate=0.461538, ROI=-0.339
- `SKIPPED_VETO`: settled=72, wins=59, hit_rate=0.819444, ROI=0.096373
- `WATCHLIST_NO_ODDS`: settled=6, wins=3, hit_rate=0.5, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=9, wins=8, hit_rate=0.888889, ROI=0.026667

## By odds source

- `UNKNOWN`: settled=11, wins=7, hit_rate=0.636364, ROI=None
- `betexplorer_odds`: settled=43, wins=33, hit_rate=0.767442, ROI=-0.026047
- `bzzoiro_odds`: settled=20, wins=17, hit_rate=0.85, ROI=0.21265
- `forebet_best`: settled=18, wins=15, hit_rate=0.833333, ROI=0.157778
- `scoutingstats_odds`: settled=13, wins=7, hit_rate=0.538462, ROI=-0.312308
- `zulubet`: settled=8, wins=3, hit_rate=0.375, ROI=-0.50375

## By odds match method

- `betexplorer`: settled=43, wins=33, hit_rate=0.767442, ROI=-0.026047
- `exact`: settled=33, wins=24, hit_rate=0.727273, ROI=0.005848
- `fallback`: settled=26, wins=18, hit_rate=0.692308, ROI=-0.045769
- `none`: settled=11, wins=7, hit_rate=0.636364, ROI=None

## Unmatched result examples

- 2026-06-26 `CAUTION` `2way-unanimous avg_p>=70` — Scotland Mabvuku vs Manica Diamonds FC -> HOME @ 1.33 (unmatched_result); keys=['scotlandm']/['manicadia']
- 2026-06-30 `SKIPPED_VETO` `2way-unanimous avg_p>=65` — Azam vs Dodoma Jiji -> HOME @ 1.35 (unmatched_result); keys=['azam']/['dodomajij']
- 2026-07-01 `SKIPPED_VETO` `2way-unanimous avg_p>=65` — Charlotte Independence vs Corpus Christi -> HOME @ 1.55 (unmatched_result); keys=['charlotte']/['corpuschr']
- 2026-07-03 `CAUTION` `2way-unanimous avg_p>=65` — Riga vs FS Jelgava -> HOME @ 1.15 (unmatched_result); keys=['riga']/['fsjelgava']
- 2026-07-03 `SKIPPED_VETO` `2way-unanimous avg_p>=65` — Sirius vs Mjallby AIF -> HOME @ 1.67 (unmatched_result); keys=['sirius', 'iksirius']/['mjallbyai']
- 2026-07-03 `SKIPPED_VETO` `2way-unanimous avg_p>=65` — Muras United vs Asiagoal -> HOME @ None (unmatched_result); keys=['murasunit']/['asiagoal']
- 2026-07-04 `SKIPPED_VETO` `2way-unanimous avg_p>=65` — Adelaide City vs Para Hills Knights -> HOME @ 1.02 (unmatched_result); keys=['adelaidec']/['parahills']
- 2026-07-04 `SKIPPED_VETO` `2way-unanimous avg_p>=65` — Hunters vs Scotland Mabvuku -> AWAY @ 1.9 (unmatched_result); keys=['hunters']/['scotlandm']
- 2026-07-04 `WATCHLIST_UNKNOWN_CTX` `3way-unanimous min_p>=60 avg_p>=60` — Launceston City vs Launceston United -> HOME @ 1.08 (unmatched_result); keys=['launcesto', 'launcestoncity']/['launcesto', 'launcestonunit']
- 2026-07-11 `CAUTION` `2way-unanimous avg_p>=70` — Guangzhou E-Power vs Hebei Kungfu -> HOME @ 2.29 (unmatched_result); keys=['guangzhou']/['hebeikung']
- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — South Hobart vs Ulverstone -> HOME @ 1.02 (unmatched_result); keys=['southhoba']/['ulverston']
- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Shaanxi Union vs Meizhou Kejia -> HOME @ 1.49 (unmatched_result); keys=['shaanxiun']/['meizhouke']
- 2026-07-19 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — FC Levadia Tallinn vs Tammeka -> HOME @ None (unmatched_result); keys=['levadiata']/['tammeka']
- 2026-07-24 `CAUTION` `2way-unanimous avg_p>=70` — Vasteras SK FK vs Orgryte IS -> HOME @ 2.06 (unmatched_result); keys=['vasterass']/['orgryteis']

## Ambiguous result examples

- none

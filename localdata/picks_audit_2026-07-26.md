# Edge Factory — Recent picks audit (2026-06-27 to 2026-07-26)

## Overall

- archived pick rows: 143
- archived pick dates: 30
- settled picks: 118
- eligible prior 1x2 picks: 133
- unmatched result picks: 15
- ambiguous result picks: 0
- wins: 85
- hit rate: 0.720339
- priced picks: 107
- ROI: -0.036299

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-26
- same-day rows excluded: 10

## By rule

- `2way-unanimous avg_p>=65`: settled=11, wins=7, hit_rate=0.636364, ROI=-0.216364
- `2way-unanimous avg_p>=70`: settled=35, wins=24, hit_rate=0.685714, ROI=-0.125862
- `3way-unanimous avg_p>=65`: settled=34, wins=21, hit_rate=0.617647, ROI=-0.137467
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=16, wins=13, hit_rate=0.8125, ROI=-0.005625
- `3way-unanimous min_p>=60 avg_p>=60`: settled=12, wins=11, hit_rate=0.916667, ROI=0.326364

## By bucket

- `CAUTION`: settled=30, wins=14, hit_rate=0.466667, ROI=-0.308133
- `SKIPPED_VETO`: settled=73, wins=59, hit_rate=0.808219, ROI=0.075294
- `WATCHLIST_NO_ODDS`: settled=6, wins=4, hit_rate=0.666667, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=9, wins=8, hit_rate=0.888889, ROI=0.026667

## By odds source

- `UNKNOWN`: settled=11, wins=8, hit_rate=0.727273, ROI=None
- `betexplorer_odds`: settled=45, wins=35, hit_rate=0.777778, ROI=-0.011111
- `bzzoiro_odds`: settled=21, wins=17, hit_rate=0.809524, ROI=0.184095
- `forebet_best`: settled=17, wins=15, hit_rate=0.882353, ROI=0.225882
- `scoutingstats_odds`: settled=16, wins=7, hit_rate=0.4375, ROI=-0.44125
- `zulubet`: settled=8, wins=3, hit_rate=0.375, ROI=-0.50375

## By odds match method

- `betexplorer`: settled=45, wins=35, hit_rate=0.777778, ROI=-0.011111
- `exact`: settled=37, wins=24, hit_rate=0.648649, ROI=-0.086324
- `fallback`: settled=25, wins=18, hit_rate=0.72, ROI=-0.0076
- `none`: settled=11, wins=8, hit_rate=0.727273, ROI=None

## Unmatched result examples

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
- 2026-07-25 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Maribor vs Brinje-Grosuplje -> HOME @ 1.46 (unmatched_result); keys=['maribor']/['brinjegro']
- 2026-07-25 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Coquimbo Unido vs Universidad de Concepcion -> HOME @ None (unmatched_result); keys=['coquimbou']/['universid']
- 2026-07-25 `WATCHLIST_UNKNOWN_CTX` `3way-unanimous avg_p>=65` — Always Ready vs San Antonio Bulo Bulo -> HOME @ 1.09 (unmatched_result); keys=['alwaysrea']/['sanantoni']

## Ambiguous result examples

- none

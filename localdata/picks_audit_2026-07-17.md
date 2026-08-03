# Edge Factory — Recent picks audit (2026-06-18 to 2026-07-17)

## Overall

- archived pick rows: 126
- archived pick dates: 29
- settled picks: 106
- eligible prior 1x2 picks: 121
- unmatched result picks: 15
- ambiguous result picks: 0
- wins: 77
- hit rate: 0.726415
- priced picks: 94
- ROI: -0.003319

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-17
- same-day rows excluded: 5

## By rule

- `2way-unanimous avg_p>=65`: settled=11, wins=7, hit_rate=0.636364, ROI=-0.216364
- `2way-unanimous avg_p>=70`: settled=29, wins=19, hit_rate=0.655172, ROI=-0.17
- `3way-unanimous avg_p>=65`: settled=37, wins=26, hit_rate=0.702703, ROI=0.060242
- `3way-unanimous home-only avg_p>=60`: settled=1, wins=1, hit_rate=1.0, ROI=0.32
- `3way-unanimous home-only avg_p>=65`: settled=16, wins=13, hit_rate=0.8125, ROI=-0.005625
- `3way-unanimous min_p>=60 avg_p>=60`: settled=12, wins=11, hit_rate=0.916667, ROI=0.326364

## By bucket

- `CAUTION`: settled=35, wins=21, hit_rate=0.6, ROI=-0.1946
- `SKIPPED_VETO`: settled=59, wins=49, hit_rate=0.830508, ROI=0.129611
- `WATCHLIST_NO_ODDS`: settled=7, wins=3, hit_rate=0.428571, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=5, wins=4, hit_rate=0.8, ROI=-0.1

## By odds source

- `UNKNOWN`: settled=12, wins=7, hit_rate=0.583333, ROI=None
- `betexplorer_odds`: settled=26, wins=20, hit_rate=0.769231, ROI=-0.000385
- `bzzoiro_odds`: settled=18, wins=15, hit_rate=0.833333, ROI=0.163222
- `forebet_best`: settled=26, wins=21, hit_rate=0.807692, ROI=0.101154
- `scoutingstats_odds`: settled=11, wins=6, hit_rate=0.545455, ROI=-0.295455
- `zulubet`: settled=13, wins=8, hit_rate=0.615385, ROI=-0.201538

## By odds match method

- `betexplorer`: settled=26, wins=20, hit_rate=0.769231, ROI=-0.000385
- `exact`: settled=29, wins=21, hit_rate=0.724138, ROI=-0.010759
- `fallback`: settled=39, wins=29, hit_rate=0.74359, ROI=0.000256
- `none`: settled=12, wins=7, hit_rate=0.583333, ROI=None

## Unmatched result examples

- 2026-06-20 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Tuggeranong United vs Canberra White Eagles -> HOME @ 1.4 (unmatched_result); keys=['tuggerano']/['canberraw']
- 2026-06-24 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Mtibwa Sugar vs Simba -> AWAY @ None (unmatched_result); keys=['mtibwasug']/['simba']
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
- 2026-07-16 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Vestri vs Qarabag -> AWAY @ 1.12 (unmatched_result); keys=['vestri']/['qarabag']

## Ambiguous result examples

- none

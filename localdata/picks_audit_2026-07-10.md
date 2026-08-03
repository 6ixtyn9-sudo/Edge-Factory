# Edge Factory — Recent picks audit (2026-06-11 to 2026-07-10)

## Overall

- archived pick rows: 94
- archived pick dates: 22
- settled picks: 78
- eligible prior 1x2 picks: 89
- unmatched result picks: 11
- ambiguous result picks: 0
- wins: 57
- hit rate: 0.730769
- priced picks: 66
- ROI: 0.02103

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-10
- same-day rows excluded: 5

## By rule

- `2way-unanimous avg_p>=65`: settled=11, wins=7, hit_rate=0.636364, ROI=-0.216364
- `2way-unanimous avg_p>=70`: settled=18, wins=13, hit_rate=0.722222, ROI=-0.115455
- `3way-unanimous avg_p>=65`: settled=32, wins=22, hit_rate=0.6875, ROI=0.039214
- `3way-unanimous home-only avg_p>=65`: settled=5, wins=4, hit_rate=0.8, ROI=0.07
- `3way-unanimous min_p>=60 avg_p>=60`: settled=12, wins=11, hit_rate=0.916667, ROI=0.326364

## By bucket

- `CAUTION`: settled=27, wins=17, hit_rate=0.62963, ROI=-0.187074
- `SKIPPED_VETO`: settled=43, wins=36, hit_rate=0.837209, ROI=0.168132
- `WATCHLIST_NO_ODDS`: settled=7, wins=3, hit_rate=0.428571, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=1, wins=1, hit_rate=1.0, ROI=0.05

## By odds source

- `UNKNOWN`: settled=12, wins=7, hit_rate=0.583333, ROI=None
- `betexplorer_odds`: settled=5, wins=4, hit_rate=0.8, ROI=0.072
- `bzzoiro_odds`: settled=15, wins=12, hit_rate=0.8, ROI=0.106533
- `forebet_best`: settled=26, wins=21, hit_rate=0.807692, ROI=0.101154
- `scoutingstats_odds`: settled=8, wins=5, hit_rate=0.625, ROI=-0.1975
- `zulubet`: settled=12, wins=8, hit_rate=0.666667, ROI=-0.135

## By odds match method

- `betexplorer`: settled=5, wins=4, hit_rate=0.8, ROI=0.072
- `exact`: settled=23, wins=17, hit_rate=0.73913, ROI=0.000783
- `fallback`: settled=38, wins=29, hit_rate=0.763158, ROI=0.026579
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

## Ambiguous result examples

- none

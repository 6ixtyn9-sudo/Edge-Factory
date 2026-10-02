# Edge Factory — CLV report (2026-09-02 to 2026-10-02)

## Overall

- total unique picks: 1064
- picks with at least two prices: 871
- average raw odds delta: -0.002388
- average implied-probability delta: 0.001105
- beat-later-price rate: 0.132032
- beat-later-price sample: 871
- unmatched picks: 77
- picks with fewer than two snapshots: 113

## By rule

- `1x2_two_source_p55_majority`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `1x2_two_source_p55_unanimous`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `1x2_two_source_p60_majority`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `1x2_two_source_p60_unanimous`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `1x2_two_source_p65_majority`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `1x2_two_source_p70_majority`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `2way-unanimous avg_p>=60`: n=135, two_prices=99, avg_raw=-0.00101, avg_ip=0.000416, beat_rate=0.080808
- `2way-unanimous avg_p>=70`: n=148, two_prices=98, avg_raw=-0.001735, avg_ip=0.00121, beat_rate=0.214286
- `ml-meta avg_p>=55`: n=550, two_prices=498, avg_raw=-0.003313, avg_ip=0.001484, beat_rate=0.148594
- `ml-meta avg_p>=60`: n=107, two_prices=81, avg_raw=-0.000988, avg_ip=0.000401, beat_rate=0.074074
- `ml-meta avg_p>=65`: n=39, two_prices=26, avg_raw=-0.002692, avg_ip=0.000739, beat_rate=0.076923
- `ml-meta avg_p>=70`: n=23, two_prices=11, avg_raw=-0.001818, avg_ip=0.002205, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=42, two_prices=39, avg_raw=0.0, avg_ip=-7.1e-05, beat_rate=0.076923

## By bucket

- `CAUTION`: n=93, two_prices=83, avg_raw=-0.001566, avg_ip=0.001571, beat_rate=0.180723
- `CERTIFIED_CLEAN`: n=135, two_prices=121, avg_raw=-0.002727, avg_ip=0.001261, beat_rate=0.157025
- `PRODUCTION_CERTIFIED`: n=4, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `SKIPPED_VETO`: n=521, two_prices=446, avg_raw=-0.002197, avg_ip=0.001, beat_rate=0.152466
- `WATCHLIST_NO_ODDS`: n=61, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=25, two_prices=17, avg_raw=0.000588, avg_ip=-0.000367, beat_rate=0.058824
- `WATCHLIST_UNCORROBORATED_PRICE`: n=215, two_prices=190, avg_raw=-0.003421, avg_ip=0.001263, beat_rate=0.057895
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

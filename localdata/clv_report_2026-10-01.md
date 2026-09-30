# Edge Factory — CLV report (2026-09-01 to 2026-10-01)

## Overall

- total unique picks: 1079
- picks with at least two prices: 886
- average raw odds delta: -0.001941
- average implied-probability delta: 0.000965
- beat-later-price rate: 0.130926
- beat-later-price sample: 886
- unmatched picks: 77
- picks with fewer than two snapshots: 113

## By rule

- `1x2_two_source_p55_unanimous`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `1x2_two_source_p60_unanimous`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `1x2_two_source_p70_majority`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `2way-unanimous avg_p>=60`: n=135, two_prices=99, avg_raw=-0.00101, avg_ip=0.000416, beat_rate=0.080808
- `2way-unanimous avg_p>=70`: n=152, two_prices=102, avg_raw=-0.00098, avg_ip=0.000794, beat_rate=0.205882
- `ml-meta avg_p>=55`: n=562, two_prices=510, avg_raw=-0.002667, avg_ip=0.001312, beat_rate=0.147059
- `ml-meta avg_p>=60`: n=107, two_prices=81, avg_raw=-0.000988, avg_ip=0.000401, beat_rate=0.074074
- `ml-meta avg_p>=65`: n=39, two_prices=26, avg_raw=-0.002692, avg_ip=0.000739, beat_rate=0.076923
- `ml-meta avg_p>=70`: n=23, two_prices=11, avg_raw=-0.001818, avg_ip=0.002205, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=48, two_prices=45, avg_raw=0.0, avg_ip=-6.2e-05, beat_rate=0.066667

## By bucket

- `CAUTION`: n=96, two_prices=86, avg_raw=0.002674, avg_ip=0.000154, beat_rate=0.174419
- `CERTIFIED_CLEAN`: n=129, two_prices=115, avg_raw=-0.00287, avg_ip=0.001327, beat_rate=0.165217
- `PRODUCTION_CERTIFIED`: n=4, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `SKIPPED_VETO`: n=532, two_prices=457, avg_raw=-0.002144, avg_ip=0.000998, beat_rate=0.150985
- `WATCHLIST_NO_ODDS`: n=61, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=25, two_prices=17, avg_raw=0.000588, avg_ip=-0.000367, beat_rate=0.058824
- `WATCHLIST_UNCORROBORATED_PRICE`: n=222, two_prices=197, avg_raw=-0.003299, avg_ip=0.001218, beat_rate=0.055838
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

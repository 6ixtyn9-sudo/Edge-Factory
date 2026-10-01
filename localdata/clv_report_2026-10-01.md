# Edge Factory — CLV report (2026-09-01 to 2026-10-01)

## Overall

- total unique picks: 1089
- picks with at least two prices: 895
- average raw odds delta: -0.002156
- average implied-probability delta: 0.001054
- beat-later-price rate: 0.132961
- beat-later-price sample: 895
- unmatched picks: 78
- picks with fewer than two snapshots: 113

## By rule

- `2way-unanimous avg_p>=60`: n=143, two_prices=106, avg_raw=-0.001698, avg_ip=0.000729, beat_rate=0.084906
- `2way-unanimous avg_p>=70`: n=152, two_prices=102, avg_raw=-0.00098, avg_ip=0.000794, beat_rate=0.205882
- `ml-meta avg_p>=55`: n=565, two_prices=513, avg_raw=-0.002865, avg_ip=0.001393, beat_rate=0.148148
- `ml-meta avg_p>=60`: n=108, two_prices=82, avg_raw=-0.000976, avg_ip=0.000396, beat_rate=0.073171
- `ml-meta avg_p>=65`: n=40, two_prices=27, avg_raw=-0.004444, avg_ip=0.001946, beat_rate=0.111111
- `ml-meta avg_p>=70`: n=23, two_prices=11, avg_raw=-0.001818, avg_ip=0.002205, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=9, two_prices=8, avg_raw=0.005, avg_ip=-0.004537, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=48, two_prices=45, avg_raw=0.0, avg_ip=-6.2e-05, beat_rate=0.066667

## By bucket

- `CAUTION`: n=101, two_prices=91, avg_raw=0.001648, avg_ip=0.000542, beat_rate=0.175824
- `CERTIFIED_CLEAN`: n=131, two_prices=117, avg_raw=-0.002821, avg_ip=0.001304, beat_rate=0.162393
- `SKIPPED_VETO`: n=537, two_prices=461, avg_raw=-0.002169, avg_ip=0.001003, beat_rate=0.151844
- `WATCHLIST_NO_ODDS`: n=61, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=25, two_prices=17, avg_raw=0.000588, avg_ip=-0.000367, beat_rate=0.058824
- `WATCHLIST_UNCORROBORATED_PRICE`: n=224, two_prices=199, avg_raw=-0.003819, avg_ip=0.001434, beat_rate=0.060302
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

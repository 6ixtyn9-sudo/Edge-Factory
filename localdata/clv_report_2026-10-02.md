# Edge Factory — CLV report (2026-09-02 to 2026-10-02)

## Overall

- total unique picks: 1078
- picks with at least two prices: 884
- average raw odds delta: -0.002387
- average implied-probability delta: 0.001093
- beat-later-price rate: 0.133484
- beat-later-price sample: 884
- unmatched picks: 78
- picks with fewer than two snapshots: 113

## By rule

- `2way-unanimous avg_p>=60`: n=148, two_prices=111, avg_raw=-0.0, avg_ip=-6.2e-05, beat_rate=0.081081
- `2way-unanimous avg_p>=70`: n=148, two_prices=98, avg_raw=-0.001735, avg_ip=0.00121, beat_rate=0.214286
- `ml-meta avg_p>=55`: n=557, two_prices=505, avg_raw=-0.003485, avg_ip=0.001553, beat_rate=0.148515
- `ml-meta avg_p>=60`: n=110, two_prices=84, avg_raw=-0.000952, avg_ip=0.000387, beat_rate=0.071429
- `ml-meta avg_p>=65`: n=40, two_prices=27, avg_raw=-0.004444, avg_ip=0.001946, beat_rate=0.111111
- `ml-meta avg_p>=70`: n=23, two_prices=11, avg_raw=-0.001818, avg_ip=0.002205, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=9, two_prices=8, avg_raw=0.005, avg_ip=-0.004537, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=42, two_prices=39, avg_raw=0.0, avg_ip=-7.1e-05, beat_rate=0.076923

## By bucket

- `CAUTION`: n=98, two_prices=88, avg_raw=-0.002386, avg_ip=0.001891, beat_rate=0.181818
- `CERTIFIED_CLEAN`: n=131, two_prices=117, avg_raw=-0.002821, avg_ip=0.001304, beat_rate=0.162393
- `SKIPPED_VETO`: n=536, two_prices=460, avg_raw=-0.001783, avg_ip=0.000801, beat_rate=0.15
- `WATCHLIST_NO_ODDS`: n=61, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=25, two_prices=17, avg_raw=0.000588, avg_ip=-0.000367, beat_rate=0.058824
- `WATCHLIST_UNCORROBORATED_PRICE`: n=217, two_prices=192, avg_raw=-0.003958, avg_ip=0.001487, beat_rate=0.0625
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

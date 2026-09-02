# Edge Factory — CLV report (2026-08-03 to 2026-09-02)

## Overall

- total unique picks: 669
- picks with at least two prices: 598
- average raw odds delta: 0.005462
- average implied-probability delta: -0.000661
- beat-later-price rate: 0.157191
- beat-later-price sample: 598
- unmatched picks: 37
- picks with fewer than two snapshots: 34

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=166, two_prices=147, avg_raw=0.000435, avg_ip=-0.000287, beat_rate=0.14966
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=24, two_prices=23, avg_raw=-0.001304, avg_ip=-0.000123, beat_rate=0.043478
- `ml-meta avg_p>=55`: n=322, two_prices=299, avg_raw=0.001204, avg_ip=0.000357, beat_rate=0.190635
- `ml-meta avg_p>=60`: n=50, two_prices=40, avg_raw=0.0796, avg_ip=-0.015119, beat_rate=0.025
- `ml-meta avg_p>=65`: n=17, two_prices=10, avg_raw=-0.0132, avg_ip=0.006587, beat_rate=0.3
- `ml-meta avg_p>=70`: n=17, two_prices=14, avg_raw=0.014286, avg_ip=-0.006837, beat_rate=0.142857
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=19, two_prices=17, avg_raw=0.000588, avg_ip=-0.000302, beat_rate=0.0

## By bucket

- `CAUTION`: n=98, two_prices=90, avg_raw=0.007778, avg_ip=-0.001845, beat_rate=0.144444
- `CERTIFIED_CLEAN`: n=51, two_prices=47, avg_raw=0.059319, avg_ip=-0.009095, beat_rate=0.234043
- `SKIPPED_VETO`: n=353, two_prices=338, avg_raw=-0.000538, avg_ip=0.000449, beat_rate=0.180473
- `WATCHLIST_NO_ODDS`: n=34, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=12, two_prices=8, avg_raw=-0.005, avg_ip=0.003987, beat_rate=0.125
- `WATCHLIST_UNCORROBORATED_PRICE`: n=100, two_prices=95, avg_raw=-0.001263, avg_ip=0.000934, beat_rate=0.084211
- `WATCHLIST_UNKNOWN_CTX`: n=21, two_prices=20, avg_raw=0.006, avg_ip=-0.003723, beat_rate=0.0

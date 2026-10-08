# Edge Factory — CLV report (2026-09-08 to 2026-10-08)

## Overall

- total unique picks: 980
- picks with at least two prices: 763
- average raw odds delta: -0.0027
- average implied-probability delta: 0.001324
- beat-later-price rate: 0.119266
- beat-later-price sample: 763
- unmatched picks: 98
- picks with fewer than two snapshots: 117

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=113, two_prices=74, avg_raw=-0.001351, avg_ip=0.000953, beat_rate=0.189189
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=466, two_prices=411, avg_raw=-0.004404, avg_ip=0.002169, beat_rate=0.138686
- `ml-meta avg_p>=60`: n=118, two_prices=91, avg_raw=-0.000989, avg_ip=0.000412, beat_rate=0.065934
- `ml-meta avg_p>=65`: n=40, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=16, two_prices=7, avg_raw=-0.002857, avg_ip=0.003465, beat_rate=0.142857
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=10, avg_raw=0.006, avg_ip=-0.00541, beat_rate=0.0

## By bucket

- `CAUTION`: n=78, two_prices=69, avg_raw=-0.000725, avg_ip=0.000705, beat_rate=0.15942
- `CERTIFIED_CLEAN`: n=125, two_prices=115, avg_raw=-0.002174, avg_ip=0.00123, beat_rate=0.130435
- `SKIPPED_VETO`: n=494, two_prices=403, avg_raw=-0.002134, avg_ip=0.001186, beat_rate=0.129032
- `WATCHLIST_NO_ODDS`: n=77, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=11, two_prices=5, avg_raw=0.026, avg_ip=-0.010754, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=185, two_prices=160, avg_raw=-0.006375, avg_ip=0.00243, beat_rate=0.075
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

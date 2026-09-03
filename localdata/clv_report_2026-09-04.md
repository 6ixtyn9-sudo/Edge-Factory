# Edge Factory — CLV report (2026-08-05 to 2026-09-04)

## Overall

- total unique picks: 691
- picks with at least two prices: 622
- average raw odds delta: 0.005347
- average implied-probability delta: -0.00077
- beat-later-price rate: 0.149518
- beat-later-price sample: 622
- unmatched picks: 38
- picks with fewer than two snapshots: 31

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=170, two_prices=149, avg_raw=0.000564, avg_ip=-0.000349, beat_rate=0.14094
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=19, two_prices=19, avg_raw=0.002632, avg_ip=-0.001494, beat_rate=0.0
- `ml-meta avg_p>=55`: n=339, two_prices=317, avg_raw=0.000946, avg_ip=0.000231, beat_rate=0.18612
- `ml-meta avg_p>=60`: n=52, two_prices=43, avg_raw=0.074279, avg_ip=-0.01418, beat_rate=0.023256
- `ml-meta avg_p>=65`: n=17, two_prices=10, avg_raw=-0.0132, avg_ip=0.006587, beat_rate=0.3
- `ml-meta avg_p>=70`: n=17, two_prices=14, avg_raw=0.015, avg_ip=-0.007491, beat_rate=0.071429
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=23, two_prices=21, avg_raw=0.000476, avg_ip=-0.000245, beat_rate=0.0

## By bucket

- `CAUTION`: n=107, two_prices=98, avg_raw=0.007959, avg_ip=-0.001955, beat_rate=0.122449
- `CERTIFIED_CLEAN`: n=53, two_prices=50, avg_raw=0.05596, avg_ip=-0.008649, beat_rate=0.22
- `SKIPPED_VETO`: n=360, two_prices=346, avg_raw=-0.000266, avg_ip=0.000149, beat_rate=0.17341
- `WATCHLIST_NO_ODDS`: n=35, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=12, two_prices=9, avg_raw=-0.017778, avg_ip=0.008826, beat_rate=0.222222
- `WATCHLIST_UNCORROBORATED_PRICE`: n=106, two_prices=101, avg_raw=-0.001188, avg_ip=0.000879, beat_rate=0.079208
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=18, avg_raw=0.006667, avg_ip=-0.004136, beat_rate=0.0

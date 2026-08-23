# Edge Factory — CLV report (2026-07-24 to 2026-08-23)

## Overall

- total unique picks: 421
- picks with at least two prices: 383
- average raw odds delta: 0.002509
- average implied-probability delta: -0.001055
- beat-later-price rate: 0.13577
- beat-later-price sample: 383
- unmatched picks: 22
- picks with fewer than two snapshots: 15

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=127, two_prices=115, avg_raw=0.001687, avg_ip=-0.001167, beat_rate=0.130435
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=44, two_prices=42, avg_raw=0.005119, avg_ip=-0.002892, beat_rate=0.02381
- `ml-meta avg_p>=55`: n=155, two_prices=143, avg_raw=0.004196, avg_ip=-0.001344, beat_rate=0.174825
- `ml-meta avg_p>=60`: n=25, two_prices=23, avg_raw=0.008435, avg_ip=-0.003795, beat_rate=0.0
- `ml-meta avg_p>=65`: n=8, two_prices=4, avg_raw=-0.003, avg_ip=0.004583, beat_rate=0.5
- `ml-meta avg_p>=70`: n=11, two_prices=10, avg_raw=0.015, avg_ip=-0.006102, beat_rate=0.1
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=1, two_prices=1, avg_raw=0.01, avg_ip=-0.008817, beat_rate=0.0

## By bucket

- `CAUTION`: n=71, two_prices=66, avg_raw=0.003182, avg_ip=-2.6e-05, beat_rate=0.121212
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=224, two_prices=216, avg_raw=0.003347, avg_ip=-0.001966, beat_rate=0.148148
- `WATCHLIST_NO_ODDS`: n=21, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=51, two_prices=49, avg_raw=-0.001224, avg_ip=0.001039, beat_rate=0.081633
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

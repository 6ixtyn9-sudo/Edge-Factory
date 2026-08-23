# Edge Factory — CLV report (2026-07-24 to 2026-08-23)

## Overall

- total unique picks: 433
- picks with at least two prices: 387
- average raw odds delta: 0.002457
- average implied-probability delta: -0.001021
- beat-later-price rate: 0.134367
- beat-later-price sample: 387
- unmatched picks: 22
- picks with fewer than two snapshots: 23

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=129, two_prices=116, avg_raw=0.001672, avg_ip=-0.001157, beat_rate=0.12931
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=44, two_prices=42, avg_raw=0.005119, avg_ip=-0.002892, beat_rate=0.02381
- `ml-meta avg_p>=55`: n=155, two_prices=143, avg_raw=0.004196, avg_ip=-0.001344, beat_rate=0.174825
- `ml-meta avg_p>=60`: n=32, two_prices=26, avg_raw=0.007462, avg_ip=-0.003357, beat_rate=0.0
- `ml-meta avg_p>=65`: n=9, two_prices=4, avg_raw=-0.003, avg_ip=0.004583, beat_rate=0.5
- `ml-meta avg_p>=70`: n=12, two_prices=10, avg_raw=0.015, avg_ip=-0.006102, beat_rate=0.1
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=73, two_prices=66, avg_raw=0.003182, avg_ip=-2.6e-05, beat_rate=0.121212
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=232, two_prices=220, avg_raw=0.003241, avg_ip=-0.00189, beat_rate=0.145455
- `WATCHLIST_NO_ODDS`: n=21, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=53, two_prices=49, avg_raw=-0.001224, avg_ip=0.001039, beat_rate=0.081633
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

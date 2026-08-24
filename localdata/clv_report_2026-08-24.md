# Edge Factory — CLV report (2026-07-25 to 2026-08-24)

## Overall

- total unique picks: 439
- picks with at least two prices: 399
- average raw odds delta: 0.002484
- average implied-probability delta: -0.001037
- beat-later-price rate: 0.132832
- beat-later-price sample: 399
- unmatched picks: 22
- picks with fewer than two snapshots: 17

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=131, two_prices=118, avg_raw=0.001644, avg_ip=-0.001137, beat_rate=0.127119
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=44, two_prices=42, avg_raw=0.005119, avg_ip=-0.002892, beat_rate=0.02381
- `ml-meta avg_p>=55`: n=159, two_prices=147, avg_raw=0.003878, avg_ip=-0.001194, beat_rate=0.176871
- `ml-meta avg_p>=60`: n=32, two_prices=30, avg_raw=0.0088, avg_ip=-0.00408, beat_rate=0.0
- `ml-meta avg_p>=65`: n=9, two_prices=5, avg_raw=-0.0024, avg_ip=0.003666, beat_rate=0.4
- `ml-meta avg_p>=70`: n=12, two_prices=10, avg_raw=0.015, avg_ip=-0.006102, beat_rate=0.1
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=72, two_prices=67, avg_raw=0.003582, avg_ip=-0.000202, beat_rate=0.119403
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=238, two_prices=229, avg_raw=0.003157, avg_ip=-0.001845, beat_rate=0.144105
- `WATCHLIST_NO_ODDS`: n=21, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=54, two_prices=51, avg_raw=-0.001176, avg_ip=0.000998, beat_rate=0.078431
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

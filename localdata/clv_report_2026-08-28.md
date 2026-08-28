# Edge Factory — CLV report (2026-07-29 to 2026-08-28)

## Overall

- total unique picks: 502
- picks with at least two prices: 451
- average raw odds delta: 0.002353
- average implied-probability delta: -0.000711
- beat-later-price rate: 0.137472
- beat-later-price sample: 451
- unmatched picks: 23
- picks with fewer than two snapshots: 27

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=136, two_prices=121, avg_raw=0.001025, avg_ip=-0.000572, beat_rate=0.140496
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=41, two_prices=39, avg_raw=0.005513, avg_ip=-0.003114, beat_rate=0.025641
- `ml-meta avg_p>=55`: n=208, two_prices=191, avg_raw=0.003508, avg_ip=-0.000664, beat_rate=0.172775
- `ml-meta avg_p>=60`: n=38, two_prices=34, avg_raw=0.008941, avg_ip=-0.004209, beat_rate=0.0
- `ml-meta avg_p>=65`: n=14, two_prices=8, avg_raw=-0.0015, avg_ip=0.002291, beat_rate=0.25
- `ml-meta avg_p>=70`: n=13, two_prices=11, avg_raw=0.013636, avg_ip=-0.005547, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=81, two_prices=74, avg_raw=0.006351, avg_ip=-0.00149, beat_rate=0.108108
- `CERTIFIED_CLEAN`: n=28, two_prices=25, avg_raw=-0.00088, avg_ip=0.00132, beat_rate=0.28
- `SKIPPED_VETO`: n=278, two_prices=264, avg_raw=0.002133, avg_ip=-0.000882, beat_rate=0.159091
- `WATCHLIST_NO_ODDS`: n=22, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=61, two_prices=58, avg_raw=-0.001034, avg_ip=0.000878, beat_rate=0.068966
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

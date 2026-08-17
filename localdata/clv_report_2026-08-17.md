# Edge Factory — CLV report (2026-07-18 to 2026-08-17)

## Overall

- total unique picks: 301
- picks with at least two prices: 264
- average raw odds delta: 0.003186
- average implied-probability delta: -0.00143
- beat-later-price rate: 0.143939
- beat-later-price sample: 264
- unmatched picks: 15
- picks with fewer than two snapshots: 23

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=101, two_prices=92, avg_raw=0.002326, avg_ip=-0.001656, beat_rate=0.141304
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=9, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=83, two_prices=68, avg_raw=0.011324, avg_ip=-0.004049, beat_rate=0.220588
- `ml-meta avg_p>=60`: n=4, two_prices=2, avg_raw=0.002, avg_ip=-0.000962, beat_rate=0.0
- `ml-meta avg_p>=65`: n=5, two_prices=3, avg_raw=-0.004, avg_ip=0.006111, beat_rate=0.666667
- `ml-meta avg_p>=70`: n=4, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=53, two_prices=47, avg_raw=0.000638, avg_ip=0.000928, beat_rate=0.148936
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=165, two_prices=151, avg_raw=0.005649, avg_ip=-0.002906, beat_rate=0.13245
- `WATCHLIST_NO_ODDS`: n=14, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=5, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=21, two_prices=20, avg_raw=-0.008, avg_ip=0.003579, beat_rate=0.2
- `WATCHLIST_UNKNOWN_CTX`: n=21, two_prices=20, avg_raw=0.007, avg_ip=-0.004342, beat_rate=0.0

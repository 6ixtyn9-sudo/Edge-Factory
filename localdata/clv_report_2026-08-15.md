# Edge Factory — CLV report (2026-07-16 to 2026-08-15)

## Overall

- total unique picks: 255
- picks with at least two prices: 235
- average raw odds delta: 0.003451
- average implied-probability delta: -0.001511
- beat-later-price rate: 0.140426
- beat-later-price sample: 235
- unmatched picks: 10
- picks with fewer than two snapshots: 10

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=92, two_prices=85, avg_raw=0.001459, avg_ip=-0.001059, beat_rate=0.141176
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=9, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=52, two_prices=50, avg_raw=0.0156, avg_ip=-0.005761, beat_rate=0.24
- `ml-meta avg_p>=60`: n=2, two_prices=1, avg_raw=0.004, avg_ip=-0.001924, beat_rate=0.0
- `ml-meta avg_p>=65`: n=3, two_prices=2, avg_raw=0.019, avg_ip=-0.004455, beat_rate=0.5
- `ml-meta avg_p>=70`: n=2, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=40, two_prices=38, avg_raw=0.002632, avg_ip=0.000358, beat_rate=0.131579
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=145, two_prices=138, avg_raw=0.006254, avg_ip=-0.003292, beat_rate=0.123188
- `WATCHLIST_NO_ODDS`: n=9, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=5, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=14, two_prices=14, avg_raw=-0.011429, avg_ip=0.005112, beat_rate=0.285714
- `WATCHLIST_UNKNOWN_CTX`: n=20, two_prices=19, avg_raw=0.001579, avg_ip=-0.001003, beat_rate=0.0

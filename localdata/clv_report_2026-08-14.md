# Edge Factory — CLV report (2026-07-15 to 2026-08-14)

## Overall

- total unique picks: 228
- picks with at least two prices: 211
- average raw odds delta: 0.003085
- average implied-probability delta: -0.001524
- beat-later-price rate: 0.132701
- beat-later-price sample: 211
- unmatched picks: 6
- picks with fewer than two snapshots: 11

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=89, two_prices=83, avg_raw=0.001494, avg_ip=-0.001085, beat_rate=0.144578
- `2way-unanimous min_p>=60 avg_p>=65`: n=4, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=34, two_prices=32, avg_raw=0.018125, avg_ip=-0.007201, beat_rate=0.25
- `ml-meta avg_p>=60`: n=2, two_prices=1, avg_raw=0.004, avg_ip=-0.001924, beat_rate=0.0
- `ml-meta avg_p>=65`: n=3, two_prices=1, avg_raw=0.078, avg_ip=-0.032953, beat_rate=0.0
- `ml-meta avg_p>=70`: n=2, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=34, two_prices=30, avg_raw=0.003, avg_ip=0.00034, beat_rate=0.1
- `CERTIFIED_CLEAN`: n=20, two_prices=20, avg_raw=-0.0011, avg_ip=0.00165, beat_rate=0.35
- `SKIPPED_VETO`: n=134, two_prices=128, avg_raw=0.00557, avg_ip=-0.00326, beat_rate=0.109375
- `WATCHLIST_NO_ODDS`: n=6, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=12, two_prices=12, avg_raw=-0.013333, avg_ip=0.005964, beat_rate=0.333333
- `WATCHLIST_UNKNOWN_CTX`: n=19, two_prices=18, avg_raw=0.001667, avg_ip=-0.001058, beat_rate=0.0

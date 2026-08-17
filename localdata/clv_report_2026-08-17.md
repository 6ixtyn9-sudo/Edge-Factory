# Edge Factory — CLV report (2026-07-18 to 2026-08-17)

## Overall

- total unique picks: 301
- picks with at least two prices: 275
- average raw odds delta: 0.003131
- average implied-probability delta: -0.001367
- beat-later-price rate: 0.145455
- beat-later-price sample: 275
- unmatched picks: 15
- picks with fewer than two snapshots: 10

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=101, two_prices=93, avg_raw=0.002301, avg_ip=-0.001638, beat_rate=0.139785
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=9, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=83, two_prices=77, avg_raw=0.01026, avg_ip=-0.003555, beat_rate=0.220779
- `ml-meta avg_p>=60`: n=4, two_prices=3, avg_raw=0.001333, avg_ip=-0.000641, beat_rate=0.0
- `ml-meta avg_p>=65`: n=5, two_prices=3, avg_raw=-0.004, avg_ip=0.006111, beat_rate=0.666667
- `ml-meta avg_p>=70`: n=4, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=53, two_prices=50, avg_raw=0.0006, avg_ip=0.000872, beat_rate=0.14
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=165, two_prices=158, avg_raw=0.005525, avg_ip=-0.002768, beat_rate=0.139241
- `WATCHLIST_NO_ODDS`: n=14, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=5, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=21, two_prices=21, avg_raw=-0.007619, avg_ip=0.003408, beat_rate=0.190476
- `WATCHLIST_UNKNOWN_CTX`: n=21, two_prices=20, avg_raw=0.007, avg_ip=-0.004342, beat_rate=0.0

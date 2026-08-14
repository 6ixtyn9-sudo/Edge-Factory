# Edge Factory — CLV report (2026-07-15 to 2026-08-14)

## Overall

- total unique picks: 228
- picks with at least two prices: 213
- average raw odds delta: 0.003197
- average implied-probability delta: -0.00148
- beat-later-price rate: 0.13615
- beat-later-price sample: 213
- unmatched picks: 6
- picks with fewer than two snapshots: 9

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=89, two_prices=83, avg_raw=0.001494, avg_ip=-0.001085, beat_rate=0.144578
- `2way-unanimous min_p>=60 avg_p>=65`: n=4, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=34, two_prices=33, avg_raw=0.019697, avg_ip=-0.007521, beat_rate=0.242424
- `ml-meta avg_p>=60`: n=2, two_prices=1, avg_raw=0.004, avg_ip=-0.001924, beat_rate=0.0
- `ml-meta avg_p>=65`: n=3, two_prices=2, avg_raw=0.019, avg_ip=-0.004455, beat_rate=0.5
- `ml-meta avg_p>=70`: n=2, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=34, two_prices=32, avg_raw=0.00375, avg_ip=0.000515, beat_rate=0.125
- `CERTIFIED_CLEAN`: n=20, two_prices=20, avg_raw=-0.0011, avg_ip=0.00165, beat_rate=0.35
- `SKIPPED_VETO`: n=134, two_prices=128, avg_raw=0.00557, avg_ip=-0.00326, beat_rate=0.109375
- `WATCHLIST_NO_ODDS`: n=6, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=12, two_prices=12, avg_raw=-0.013333, avg_ip=0.005964, beat_rate=0.333333
- `WATCHLIST_UNKNOWN_CTX`: n=19, two_prices=18, avg_raw=0.001667, avg_ip=-0.001058, beat_rate=0.0

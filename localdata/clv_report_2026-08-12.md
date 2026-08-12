# Edge Factory — CLV report (2026-07-13 to 2026-08-12)

## Overall

- total unique picks: 185
- picks with at least two prices: 174
- average raw odds delta: -0.00131
- average implied-probability delta: 0.000365
- beat-later-price rate: 0.114943
- beat-later-price sample: 174
- unmatched picks: 6
- picks with fewer than two snapshots: 5

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=80, two_prices=74, avg_raw=-0.001122, avg_ip=0.00043, beat_rate=0.135135
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=6, two_prices=6, avg_raw=-0.001667, avg_ip=-0.000344, beat_rate=0.333333

## By bucket

- `CAUTION`: n=26, two_prices=25, avg_raw=-0.0048, avg_ip=0.002862, beat_rate=0.12
- `CERTIFIED_CLEAN`: n=12, two_prices=12, avg_raw=-0.0275, avg_ip=0.009867, beat_rate=0.5
- `SKIPPED_VETO`: n=110, two_prices=107, avg_raw=0.002168, avg_ip=-0.001189, beat_rate=0.084112
- `WATCHLIST_NO_ODDS`: n=6, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=10, two_prices=10, avg_raw=-0.004, avg_ip=0.001977, beat_rate=0.2
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=17, avg_raw=0.001765, avg_ip=-0.001121, beat_rate=0.0

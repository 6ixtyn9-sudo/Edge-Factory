# Edge Factory — CLV report (2026-07-14 to 2026-08-13)

## Overall

- total unique picks: 208
- picks with at least two prices: 194
- average raw odds delta: -0.001361
- average implied-probability delta: 0.000349
- beat-later-price rate: 0.118557
- beat-later-price sample: 194
- unmatched picks: 6
- picks with fewer than two snapshots: 8

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=87, two_prices=81, avg_raw=-0.000901, avg_ip=0.000292, beat_rate=0.123457
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=19, two_prices=18, avg_raw=-0.003333, avg_ip=0.000687, beat_rate=0.277778
- `ml-meta avg_p>=60`: n=1, two_prices=1, avg_raw=0.004, avg_ip=-0.001924, beat_rate=0.0
- `ml-meta avg_p>=65`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=70`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None

## By bucket

- `CAUTION`: n=28, two_prices=27, avg_raw=-0.001111, avg_ip=0.001552, beat_rate=0.074074
- `CERTIFIED_CLEAN`: n=15, two_prices=15, avg_raw=-0.022, avg_ip=0.007893, beat_rate=0.4
- `SKIPPED_VETO`: n=125, two_prices=119, avg_raw=0.001311, avg_ip=-0.000969, beat_rate=0.10084
- `WATCHLIST_NO_ODDS`: n=6, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=12, two_prices=12, avg_raw=-0.0075, avg_ip=0.003487, beat_rate=0.25
- `WATCHLIST_UNKNOWN_CTX`: n=19, two_prices=18, avg_raw=0.001667, avg_ip=-0.001058, beat_rate=0.0

# Edge Factory — CLV report (2026-07-14 to 2026-08-13)

## Overall

- total unique picks: 197
- picks with at least two prices: 184
- average raw odds delta: -0.001435
- average implied-probability delta: 0.000377
- beat-later-price rate: 0.11413
- beat-later-price sample: 184
- unmatched picks: 6
- picks with fewer than two snapshots: 7

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=83, two_prices=77, avg_raw=-0.001078, avg_ip=0.000413, beat_rate=0.12987
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=12, two_prices=12, avg_raw=-0.004167, avg_ip=0.000481, beat_rate=0.25
- `ml-meta avg_p>=60`: n=1, two_prices=1, avg_raw=0.004, avg_ip=-0.001924, beat_rate=0.0
- `ml-meta avg_p>=65`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=70`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None

## By bucket

- `CAUTION`: n=26, two_prices=25, avg_raw=-0.002, avg_ip=0.002057, beat_rate=0.08
- `CERTIFIED_CLEAN`: n=14, two_prices=14, avg_raw=-0.023571, avg_ip=0.008457, beat_rate=0.428571
- `SKIPPED_VETO`: n=119, two_prices=114, avg_raw=0.001544, avg_ip=-0.001081, beat_rate=0.087719
- `WATCHLIST_NO_ODDS`: n=6, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=11, two_prices=11, avg_raw=-0.008182, avg_ip=0.003804, beat_rate=0.272727
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=17, avg_raw=0.001765, avg_ip=-0.001121, beat_rate=0.0

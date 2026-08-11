# Edge Factory — CLV report (2026-07-12 to 2026-08-11)

## Overall

- total unique picks: 179
- picks with at least two prices: 168
- average raw odds delta: -0.000881
- average implied-probability delta: 0.000203
- beat-later-price rate: 0.095238
- beat-later-price sample: 168
- unmatched picks: 6
- picks with fewer than two snapshots: 5

## By rule

- `2way+bc-confirms avg_p>=60`: n=34, two_prices=32, avg_raw=-0.009688, avg_ip=0.004375, beat_rate=0.1875
- `2way-unanimous avg_p>=70`: n=79, two_prices=73, avg_raw=-0.000863, avg_ip=0.000298, beat_rate=0.123288
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=7, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=26, two_prices=25, avg_raw=-0.0036, avg_ip=0.002231, beat_rate=0.08
- `CERTIFIED_CLEAN`: n=11, two_prices=11, avg_raw=-0.027273, avg_ip=0.00998, beat_rate=0.454545
- `SKIPPED_VETO`: n=107, two_prices=104, avg_raw=0.002231, avg_ip=-0.001213, beat_rate=0.076923
- `WATCHLIST_NO_ODDS`: n=6, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=8, two_prices=8, avg_raw=-0.0025, avg_ip=0.001708, beat_rate=0.125
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=17, avg_raw=0.001765, avg_ip=-0.001121, beat_rate=0.0

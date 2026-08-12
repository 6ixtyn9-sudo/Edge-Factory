# Edge Factory — CLV report (2026-07-13 to 2026-08-12)

## Overall

- total unique picks: 185
- picks with at least two prices: 167
- average raw odds delta: -0.001186
- average implied-probability delta: 0.000332
- beat-later-price rate: 0.101796
- beat-later-price sample: 167
- unmatched picks: 6
- picks with fewer than two snapshots: 12

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=32, avg_raw=-0.01125, avg_ip=0.005045, beat_rate=0.21875
- `2way-unanimous avg_p>=70`: n=80, two_prices=73, avg_raw=-0.000863, avg_ip=0.000298, beat_rate=0.123288
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=6, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=26, two_prices=24, avg_raw=-0.004583, avg_ip=0.002857, beat_rate=0.083333
- `CERTIFIED_CLEAN`: n=12, two_prices=12, avg_raw=-0.0275, avg_ip=0.009867, beat_rate=0.5
- `SKIPPED_VETO`: n=110, two_prices=103, avg_raw=0.002252, avg_ip=-0.001224, beat_rate=0.07767
- `WATCHLIST_NO_ODDS`: n=6, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=10, two_prices=8, avg_raw=-0.0025, avg_ip=0.001708, beat_rate=0.125
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=17, avg_raw=0.001765, avg_ip=-0.001121, beat_rate=0.0

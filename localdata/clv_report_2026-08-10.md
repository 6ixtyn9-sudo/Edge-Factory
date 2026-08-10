# Edge Factory — CLV report (2026-07-11 to 2026-08-10)

## Overall

- total unique picks: 175
- picks with at least two prices: 165
- average raw odds delta: -0.000473
- average implied-probability delta: -5.7e-05
- beat-later-price rate: 0.090909
- beat-later-price sample: 165
- unmatched picks: 5
- picks with fewer than two snapshots: 5

## By rule

- `2way+bc-confirms avg_p>=60`: n=27, two_prices=25, avg_raw=-0.0088, avg_ip=0.003417, beat_rate=0.2
- `2way-unanimous avg_p>=70`: n=80, two_prices=75, avg_raw=-0.001107, avg_ip=0.000438, beat_rate=0.12
- `3way-unanimous avg_p>=65`: n=47, two_prices=45, avg_raw=0.005, avg_ip=-0.002838, beat_rate=0.022222
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=11, two_prices=11, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=26, two_prices=25, avg_raw=-0.0032, avg_ip=0.001022, beat_rate=0.04
- `CERTIFIED_CLEAN`: n=9, two_prices=9, avg_raw=-0.024444, avg_ip=0.00949, beat_rate=0.555556
- `SKIPPED_VETO`: n=109, two_prices=106, avg_raw=0.002, avg_ip=-0.001085, beat_rate=0.075472
- `WATCHLIST_NO_ODDS`: n=5, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=7, two_prices=7, avg_raw=-0.002857, avg_ip=0.001952, beat_rate=0.142857
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.001875, avg_ip=-0.001191, beat_rate=0.0

# Edge Factory — CLV report (2026-06-12 to 2026-07-12)

## Overall

- total unique picks: 112
- picks with at least two prices: 91
- average raw odds delta: 0.038132
- average implied-probability delta: -0.007908
- beat-later-price rate: 0.0
- beat-later-price sample: 91
- unmatched picks: 16
- picks with fewer than two snapshots: 6

## By rule

- `2way-unanimous avg_p>=65`: n=20, two_prices=16, avg_raw=0.000625, avg_ip=-0.000356, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=27, two_prices=16, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=33, two_prices=29, avg_raw=0.103103, avg_ip=-0.018448, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=11, two_prices=11, avg_raw=0.041818, avg_ip=-0.015665, beat_rate=0.0
- `3way-unanimous min_p>=60 avg_p>=60`: n=21, two_prices=19, avg_raw=0.000526, avg_ip=-0.000351, beat_rate=0.0

## By bucket

- `CAUTION`: n=35, two_prices=34, avg_raw=0.000882, avg_ip=-0.000626, beat_rate=0.0
- `SKIPPED_VETO`: n=64, two_prices=54, avg_raw=0.063704, avg_ip=-0.012933, beat_rate=0.0
- `WATCHLIST_NO_ODDS`: n=10, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

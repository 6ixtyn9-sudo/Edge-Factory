# Edge Factory — CLV report (2026-06-08 to 2026-07-08)

## Overall

- total unique picks: 100
- picks with at least two prices: 80
- average raw odds delta: 0.043375
- average implied-probability delta: -0.008996
- beat-later-price rate: 0.0
- beat-later-price sample: 80
- unmatched picks: 16
- picks with fewer than two snapshots: 5

## By rule

- `2way-unanimous avg_p>=65`: n=20, two_prices=16, avg_raw=0.000625, avg_ip=-0.000356, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=22, two_prices=12, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=33, two_prices=29, avg_raw=0.103103, avg_ip=-0.018448, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=4, two_prices=4, avg_raw=0.115, avg_ip=-0.043078, beat_rate=0.0
- `3way-unanimous min_p>=60 avg_p>=60`: n=21, two_prices=19, avg_raw=0.000526, avg_ip=-0.000351, beat_rate=0.0

## By bucket

- `CAUTION`: n=31, two_prices=31, avg_raw=0.000968, avg_ip=-0.000686, beat_rate=0.0
- `SKIPPED_VETO`: n=58, two_prices=48, avg_raw=0.071667, avg_ip=-0.01455, beat_rate=0.0
- `WATCHLIST_NO_ODDS`: n=10, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

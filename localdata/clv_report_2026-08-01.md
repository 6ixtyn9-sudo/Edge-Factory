# Edge Factory — CLV report (2026-07-02 to 2026-08-01)

## Overall

- total unique picks: 118
- picks with at least two prices: 107
- average raw odds delta: 0.007056
- average implied-probability delta: -0.003021
- beat-later-price rate: 0.009346
- beat-later-price sample: 107
- unmatched picks: 4
- picks with fewer than two snapshots: 8

## By rule

- `2way-unanimous avg_p>=65`: n=14, two_prices=11, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=31, two_prices=28, avg_raw=0.001071, avg_ip=-0.000693, beat_rate=0.035714
- `3way-unanimous avg_p>=65`: n=26, two_prices=24, avg_raw=0.010625, avg_ip=-0.005202, beat_rate=0.0
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=16, two_prices=16, avg_raw=0.02875, avg_ip=-0.010769, beat_rate=0.0
- `3way-unanimous min_p>=60 avg_p>=60`: n=21, two_prices=19, avg_raw=0.000526, avg_ip=-0.000351, beat_rate=0.0

## By bucket

- `CAUTION`: n=16, two_prices=15, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `SKIPPED_VETO`: n=88, two_prices=80, avg_raw=0.009062, avg_ip=-0.003802, beat_rate=0.0125
- `WATCHLIST_NO_ODDS`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=12, two_prices=12, avg_raw=0.0025, avg_ip=-0.001588, beat_rate=0.0

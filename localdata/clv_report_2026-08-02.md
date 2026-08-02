# Edge Factory — CLV report (2026-07-03 to 2026-08-02)

## Overall

- total unique picks: 120
- picks with at least two prices: 109
- average raw odds delta: 0.006927
- average implied-probability delta: -0.002965
- beat-later-price rate: 0.009174
- beat-later-price sample: 109
- unmatched picks: 4
- picks with fewer than two snapshots: 8

## By rule

- `2way-unanimous avg_p>=65`: n=13, two_prices=10, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=36, two_prices=32, avg_raw=0.000938, avg_ip=-0.000606, beat_rate=0.03125
- `3way-unanimous avg_p>=65`: n=24, two_prices=23, avg_raw=0.011087, avg_ip=-0.005429, beat_rate=0.0
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=16, two_prices=16, avg_raw=0.02875, avg_ip=-0.010769, beat_rate=0.0
- `3way-unanimous min_p>=60 avg_p>=60`: n=21, two_prices=19, avg_raw=0.000526, avg_ip=-0.000351, beat_rate=0.0

## By bucket

- `CAUTION`: n=18, two_prices=17, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `SKIPPED_VETO`: n=87, two_prices=79, avg_raw=0.009177, avg_ip=-0.00385, beat_rate=0.012658
- `WATCHLIST_NO_ODDS`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=13, two_prices=13, avg_raw=0.002308, avg_ip=-0.001465, beat_rate=0.0

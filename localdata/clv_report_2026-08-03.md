# Edge Factory — CLV report (2026-07-04 to 2026-08-03)

## Overall

- total unique picks: 116
- picks with at least two prices: 108
- average raw odds delta: 0.005972
- average implied-probability delta: -0.002603
- beat-later-price rate: 0.037037
- beat-later-price sample: 108
- unmatched picks: 2
- picks with fewer than two snapshots: 7

## By rule

- `2way-unanimous avg_p>=65`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=39, two_prices=35, avg_raw=0.000286, avg_ip=-0.000271, beat_rate=0.057143
- `3way-unanimous avg_p>=65`: n=29, two_prices=28, avg_raw=0.005893, avg_ip=-0.003309, beat_rate=0.071429
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=16, two_prices=16, avg_raw=0.02875, avg_ip=-0.010769, beat_rate=0.0
- `3way-unanimous min_p>=60 avg_p>=60`: n=12, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.0

## By bucket

- `CAUTION`: n=19, two_prices=18, avg_raw=-0.004444, avg_ip=0.001419, beat_rate=0.055556
- `SKIPPED_VETO`: n=81, two_prices=76, avg_raw=0.009276, avg_ip=-0.003872, beat_rate=0.026316
- `WATCHLIST_NO_ODDS`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=14, avg_raw=0.001429, avg_ip=-0.000885, beat_rate=0.071429

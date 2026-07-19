# Edge Factory — CLV report (2026-06-19 to 2026-07-19)

## Overall

- total unique picks: 124
- picks with at least two prices: 103
- average raw odds delta: 0.033689
- average implied-probability delta: -0.006987
- beat-later-price rate: 0.0
- beat-later-price sample: 103
- unmatched picks: 16
- picks with fewer than two snapshots: 6

## By rule

- `2way-unanimous avg_p>=65`: n=20, two_prices=16, avg_raw=0.000625, avg_ip=-0.000356, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=30, two_prices=19, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=36, two_prices=32, avg_raw=0.093438, avg_ip=-0.016718, beat_rate=0.0
- `3way-unanimous home-only avg_p>=60`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=16, two_prices=16, avg_raw=0.02875, avg_ip=-0.010769, beat_rate=0.0
- `3way-unanimous min_p>=60 avg_p>=60`: n=21, two_prices=19, avg_raw=0.000526, avg_ip=-0.000351, beat_rate=0.0

## By bucket

- `CAUTION`: n=35, two_prices=34, avg_raw=0.000882, avg_ip=-0.000626, beat_rate=0.0
- `SKIPPED_VETO`: n=74, two_prices=64, avg_raw=0.05375, avg_ip=-0.010912, beat_rate=0.0
- `WATCHLIST_NO_ODDS`: n=10, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

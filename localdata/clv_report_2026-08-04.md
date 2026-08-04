# Edge Factory — CLV report (2026-07-05 to 2026-08-04)

## Overall

- total unique picks: 108
- picks with at least two prices: 100
- average raw odds delta: 0.00645
- average implied-probability delta: -0.002811
- beat-later-price rate: 0.03
- beat-later-price sample: 100
- unmatched picks: 2
- picks with fewer than two snapshots: 7

## By rule

- `2way-unanimous avg_p>=65`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `2way-unanimous avg_p>=70`: n=43, two_prices=39, avg_raw=0.000256, avg_ip=-0.000243, beat_rate=0.051282
- `3way-unanimous avg_p>=65`: n=29, two_prices=28, avg_raw=0.00625, avg_ip=-0.003547, beat_rate=0.035714
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=16, two_prices=16, avg_raw=0.02875, avg_ip=-0.010769, beat_rate=0.0
- `3way-unanimous min_p>=60 avg_p>=60`: n=8, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=18, two_prices=17, avg_raw=-0.004706, avg_ip=0.001503, beat_rate=0.058824
- `SKIPPED_VETO`: n=74, two_prices=69, avg_raw=0.010072, avg_ip=-0.004168, beat_rate=0.028986
- `WATCHLIST_NO_ODDS`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=14, avg_raw=0.002143, avg_ip=-0.001361, beat_rate=0.0

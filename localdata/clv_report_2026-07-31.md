# Edge Factory — CLV report (2026-07-01 to 2026-07-31)

## Overall

- total unique picks: 116
- picks with at least two prices: 106
- average raw odds delta: 0.006085
- average implied-probability delta: -0.002709
- beat-later-price rate: 0.0
- beat-later-price sample: 106
- unmatched picks: 4
- picks with fewer than two snapshots: 7

## By rule

- `2way-unanimous avg_p>=65`: n=16, two_prices=13, avg_raw=0.000769, avg_ip=-0.000438, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=30, two_prices=27, avg_raw=0.001481, avg_ip=-0.000974, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=23, two_prices=22, avg_raw=0.005682, avg_ip=-0.003461, beat_rate=0.0
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=16, two_prices=16, avg_raw=0.02875, avg_ip=-0.010769, beat_rate=0.0
- `3way-unanimous min_p>=60 avg_p>=60`: n=21, two_prices=19, avg_raw=0.000526, avg_ip=-0.000351, beat_rate=0.0

## By bucket

- `CAUTION`: n=16, two_prices=15, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `SKIPPED_VETO`: n=89, two_prices=82, avg_raw=0.0075, avg_ip=-0.003269, beat_rate=0.0
- `WATCHLIST_NO_ODDS`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=9, two_prices=9, avg_raw=0.003333, avg_ip=-0.002117, beat_rate=0.0

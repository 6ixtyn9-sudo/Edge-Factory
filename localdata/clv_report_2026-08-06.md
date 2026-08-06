# Edge Factory — CLV report (2026-07-07 to 2026-08-06)

## Overall

- total unique picks: 109
- picks with at least two prices: 102
- average raw odds delta: 0.006775
- average implied-probability delta: -0.002956
- beat-later-price rate: 0.029412
- beat-later-price sample: 102
- unmatched picks: 1
- picks with fewer than two snapshots: 6

## By rule

- `2way-unanimous avg_p>=70`: n=48, two_prices=44, avg_raw=0.001273, avg_ip=-0.000679, beat_rate=0.045455
- `3way-unanimous avg_p>=65`: n=36, two_prices=34, avg_raw=0.005147, avg_ip=-0.002921, beat_rate=0.029412
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=15, two_prices=15, avg_raw=0.030667, avg_ip=-0.011487, beat_rate=0.0

## By bucket

- `CAUTION`: n=17, two_prices=16, avg_raw=-0.005, avg_ip=0.001597, beat_rate=0.0625
- `SKIPPED_VETO`: n=75, two_prices=71, avg_raw=0.010437, avg_ip=-0.004338, beat_rate=0.028169
- `WATCHLIST_NO_ODDS`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNCORROBORATED_PRICE`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNKNOWN_CTX`: n=15, two_prices=14, avg_raw=0.002143, avg_ip=-0.001361, beat_rate=0.0

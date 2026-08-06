# Edge Factory — CLV report (2026-07-07 to 2026-08-06)

## Overall

- total unique picks: 110
- picks with at least two prices: 103
- average raw odds delta: 0.007757
- average implied-probability delta: -0.003463
- beat-later-price rate: 0.029126
- beat-later-price sample: 103
- unmatched picks: 1
- picks with fewer than two snapshots: 6

## By rule

- `2way-unanimous avg_p>=70`: n=49, two_prices=45, avg_raw=0.0032, avg_ip=-0.001542, beat_rate=0.044444
- `3way-unanimous avg_p>=65`: n=36, two_prices=34, avg_raw=0.005735, avg_ip=-0.003382, beat_rate=0.029412
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=15, two_prices=15, avg_raw=0.030667, avg_ip=-0.011487, beat_rate=0.0

## By bucket

- `CAUTION`: n=17, two_prices=16, avg_raw=-0.005, avg_ip=0.001597, beat_rate=0.0625
- `SKIPPED_VETO`: n=76, two_prices=72, avg_raw=0.011792, avg_ip=-0.005044, beat_rate=0.027778
- `WATCHLIST_NO_ODDS`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNCORROBORATED_PRICE`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNKNOWN_CTX`: n=15, two_prices=14, avg_raw=0.002143, avg_ip=-0.001361, beat_rate=0.0

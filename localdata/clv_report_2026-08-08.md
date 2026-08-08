# Edge Factory — CLV report (2026-07-09 to 2026-08-08)

## Overall

- total unique picks: 127
- picks with at least two prices: 106
- average raw odds delta: 0.003387
- average implied-probability delta: -0.001841
- beat-later-price rate: 0.028302
- beat-later-price sample: 106
- unmatched picks: 2
- picks with fewer than two snapshots: 20

## By rule

- `2way-unanimous avg_p>=70`: n=66, two_prices=50, avg_raw=0.00328, avg_ip=-0.001604, beat_rate=0.04
- `3way-unanimous avg_p>=65`: n=39, two_prices=35, avg_raw=0.005571, avg_ip=-0.003285, beat_rate=0.028571
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=12, two_prices=12, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=17, two_prices=15, avg_raw=-0.005333, avg_ip=0.001703, beat_rate=0.066667
- `SKIPPED_VETO`: n=90, two_prices=74, avg_raw=0.005527, avg_ip=-0.002726, beat_rate=0.027027
- `WATCHLIST_NO_ODDS`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNCORROBORATED_PRICE`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.001875, avg_ip=-0.001191, beat_rate=0.0

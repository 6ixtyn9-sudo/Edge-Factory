# Edge Factory — CLV report (2026-07-07 to 2026-08-06)

## Overall

- total unique picks: 109
- picks with at least two prices: 96
- average raw odds delta: 0.006719
- average implied-probability delta: -0.002928
- beat-later-price rate: 0.03125
- beat-later-price sample: 96
- unmatched picks: 1
- picks with fewer than two snapshots: 12

## By rule

- `2way-unanimous avg_p>=70`: n=48, two_prices=41, avg_raw=0.000244, avg_ip=-0.000231, beat_rate=0.04878
- `3way-unanimous avg_p>=65`: n=36, two_prices=31, avg_raw=0.005645, avg_ip=-0.003204, beat_rate=0.032258
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=15, two_prices=15, avg_raw=0.030667, avg_ip=-0.011487, beat_rate=0.0

## By bucket

- `CAUTION`: n=17, two_prices=15, avg_raw=-0.005333, avg_ip=0.001703, beat_rate=0.066667
- `SKIPPED_VETO`: n=75, two_prices=67, avg_raw=0.010373, avg_ip=-0.004293, beat_rate=0.029851
- `WATCHLIST_NO_ODDS`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNCORROBORATED_PRICE`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=15, two_prices=14, avg_raw=0.002143, avg_ip=-0.001361, beat_rate=0.0

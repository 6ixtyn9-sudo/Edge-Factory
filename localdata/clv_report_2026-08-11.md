# Edge Factory — CLV report (2026-07-12 to 2026-08-11)

## Overall

- total unique picks: 173
- picks with at least two prices: 159
- average raw odds delta: -0.000491
- average implied-probability delta: -4.9e-05
- beat-later-price rate: 0.09434
- beat-later-price sample: 159
- unmatched picks: 6
- picks with fewer than two snapshots: 9

## By rule

- `2way+bc-confirms avg_p>=60`: n=28, two_prices=25, avg_raw=-0.0096, avg_ip=0.003929, beat_rate=0.2
- `2way-unanimous avg_p>=70`: n=79, two_prices=72, avg_raw=-0.000875, avg_ip=0.000302, beat_rate=0.125
- `3way-unanimous avg_p>=65`: n=49, two_prices=46, avg_raw=0.004891, avg_ip=-0.002776, beat_rate=0.021739
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=7, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=24, two_prices=23, avg_raw=-0.00087, avg_ip=0.000609, beat_rate=0.043478
- `CERTIFIED_CLEAN`: n=9, two_prices=9, avg_raw=-0.033333, avg_ip=0.012197, beat_rate=0.555556
- `SKIPPED_VETO`: n=107, two_prices=102, avg_raw=0.002275, avg_ip=-0.001236, beat_rate=0.078431
- `WATCHLIST_NO_ODDS`: n=6, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=8, two_prices=7, avg_raw=-0.002857, avg_ip=0.001952, beat_rate=0.142857
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.001875, avg_ip=-0.001191, beat_rate=0.0

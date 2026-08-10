# Edge Factory — CLV report (2026-07-11 to 2026-08-10)

## Overall

- total unique picks: 172
- picks with at least two prices: 162
- average raw odds delta: -6e-06
- average implied-probability delta: -0.000243
- beat-later-price rate: 0.08642
- beat-later-price sample: 162
- unmatched picks: 5
- picks with fewer than two snapshots: 5

## By rule

- `2way+bc-confirms avg_p>=60`: n=25, two_prices=23, avg_raw=-0.007391, avg_ip=0.003061, beat_rate=0.217391
- `2way-unanimous avg_p>=70`: n=79, two_prices=74, avg_raw=-0.000757, avg_ip=0.000243, beat_rate=0.108108
- `3way-unanimous avg_p>=65`: n=47, two_prices=45, avg_raw=0.005, avg_ip=-0.002838, beat_rate=0.022222
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=11, two_prices=11, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=26, two_prices=25, avg_raw=-0.0032, avg_ip=0.001022, beat_rate=0.04
- `CERTIFIED_CLEAN`: n=8, two_prices=8, avg_raw=-0.02125, avg_ip=0.0088, beat_rate=0.625
- `SKIPPED_VETO`: n=108, two_prices=105, avg_raw=0.002276, avg_ip=-0.001237, beat_rate=0.066667
- `WATCHLIST_NO_ODDS`: n=5, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=6, two_prices=6, avg_raw=-0.003333, avg_ip=0.002277, beat_rate=0.166667
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.001875, avg_ip=-0.001191, beat_rate=0.0

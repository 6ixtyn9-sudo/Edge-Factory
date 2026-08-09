# Edge Factory — CLV report (2026-07-10 to 2026-08-09)

## Overall

- total unique picks: 168
- picks with at least two prices: 158
- average raw odds delta: 0.0005
- average implied-probability delta: -0.000455
- beat-later-price rate: 0.06962
- beat-later-price sample: 158
- unmatched picks: 5
- picks with fewer than two snapshots: 5

## By rule

- `2way+bc-confirms avg_p>=60`: n=21, two_prices=19, avg_raw=-0.004737, avg_ip=0.001994, beat_rate=0.105263
- `2way-unanimous avg_p>=70`: n=79, two_prices=74, avg_raw=-0.000757, avg_ip=0.000243, beat_rate=0.108108
- `3way-unanimous avg_p>=65`: n=47, two_prices=45, avg_raw=0.005, avg_ip=-0.002838, beat_rate=0.022222
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=11, two_prices=11, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=25, two_prices=24, avg_raw=-0.003333, avg_ip=0.001065, beat_rate=0.041667
- `CERTIFIED_CLEAN`: n=5, two_prices=5, avg_raw=-0.018, avg_ip=0.007578, beat_rate=0.4
- `SKIPPED_VETO`: n=108, two_prices=105, avg_raw=0.002276, avg_ip=-0.001237, beat_rate=0.066667
- `WATCHLIST_NO_ODDS`: n=5, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=6, two_prices=6, avg_raw=-0.003333, avg_ip=0.002277, beat_rate=0.166667
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.001875, avg_ip=-0.001191, beat_rate=0.0

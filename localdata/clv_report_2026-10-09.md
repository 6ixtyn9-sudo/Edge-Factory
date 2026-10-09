# Edge Factory — CLV report (2026-09-09 to 2026-10-09)

## Overall

- total unique picks: 987
- picks with at least two prices: 767
- average raw odds delta: -0.003051
- average implied-probability delta: 0.001493
- beat-later-price rate: 0.121252
- beat-later-price sample: 767
- unmatched picks: 102
- picks with fewer than two snapshots: 117

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=118, two_prices=77, avg_raw=-0.001818, avg_ip=0.001283, beat_rate=0.194805
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=464, two_prices=409, avg_raw=-0.004963, avg_ip=0.002422, beat_rate=0.141809
- `ml-meta avg_p>=60`: n=122, two_prices=94, avg_raw=-0.000957, avg_ip=0.000399, beat_rate=0.06383
- `ml-meta avg_p>=65`: n=40, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=15, two_prices=6, avg_raw=-0.006667, avg_ip=0.005413, beat_rate=0.166667
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=15, two_prices=11, avg_raw=0.005455, avg_ip=-0.004918, beat_rate=0.0

## By bucket

- `CAUTION`: n=77, two_prices=69, avg_raw=-0.000725, avg_ip=0.000705, beat_rate=0.15942
- `CERTIFIED_CLEAN`: n=126, two_prices=116, avg_raw=-0.003448, avg_ip=0.001748, beat_rate=0.12931
- `SKIPPED_VETO`: n=502, two_prices=408, avg_raw=-0.002377, avg_ip=0.001333, beat_rate=0.132353
- `WATCHLIST_NO_ODDS`: n=80, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=9, two_prices=5, avg_raw=0.022, avg_ip=-0.00911, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=183, two_prices=158, avg_raw=-0.006456, avg_ip=0.00246, beat_rate=0.075949
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

# Edge Factory — CLV report (2026-09-09 to 2026-10-09)

## Overall

- total unique picks: 976
- picks with at least two prices: 762
- average raw odds delta: -0.003018
- average implied-probability delta: 0.001466
- beat-later-price rate: 0.120735
- beat-later-price sample: 762
- unmatched picks: 98
- picks with fewer than two snapshots: 115

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=113, two_prices=75, avg_raw=-0.001333, avg_ip=0.00094, beat_rate=0.186667
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=460, two_prices=407, avg_raw=-0.004988, avg_ip=0.002434, beat_rate=0.142506
- `ml-meta avg_p>=60`: n=120, two_prices=93, avg_raw=-0.000968, avg_ip=0.000403, beat_rate=0.064516
- `ml-meta avg_p>=65`: n=40, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=15, two_prices=6, avg_raw=-0.006667, avg_ip=0.005413, beat_rate=0.166667
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=15, two_prices=11, avg_raw=0.005455, avg_ip=-0.004918, beat_rate=0.0

## By bucket

- `CAUTION`: n=76, two_prices=68, avg_raw=-0.000735, avg_ip=0.000715, beat_rate=0.161765
- `CERTIFIED_CLEAN`: n=125, two_prices=116, avg_raw=-0.003448, avg_ip=0.001748, beat_rate=0.12931
- `SKIPPED_VETO`: n=497, two_prices=405, avg_raw=-0.002296, avg_ip=0.001273, beat_rate=0.130864
- `WATCHLIST_NO_ODDS`: n=77, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=8, two_prices=4, avg_raw=0.0275, avg_ip=-0.011388, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=183, two_prices=158, avg_raw=-0.006456, avg_ip=0.00246, beat_rate=0.075949
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

# Edge Factory — CLV report (2026-09-07 to 2026-10-07)

## Overall

- total unique picks: 980
- picks with at least two prices: 767
- average raw odds delta: -0.003103
- average implied-probability delta: 0.001508
- beat-later-price rate: 0.123859
- beat-later-price sample: 767
- unmatched picks: 96
- picks with fewer than two snapshots: 115

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=114, two_prices=76, avg_raw=-0.001842, avg_ip=0.001156, beat_rate=0.197368
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=471, two_prices=417, avg_raw=-0.005012, avg_ip=0.002448, beat_rate=0.143885
- `ml-meta avg_p>=60`: n=112, two_prices=87, avg_raw=-0.001034, avg_ip=0.000431, beat_rate=0.068966
- `ml-meta avg_p>=65`: n=40, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=16, two_prices=7, avg_raw=-0.002857, avg_ip=0.003465, beat_rate=0.142857
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=10, avg_raw=0.006, avg_ip=-0.00541, beat_rate=0.0

## By bucket

- `CAUTION`: n=81, two_prices=73, avg_raw=-0.001233, avg_ip=0.000903, beat_rate=0.164384
- `CERTIFIED_CLEAN`: n=123, two_prices=114, avg_raw=-0.002807, avg_ip=0.001447, beat_rate=0.140351
- `SKIPPED_VETO`: n=498, two_prices=407, avg_raw=-0.002629, avg_ip=0.001434, beat_rate=0.132678
- `WATCHLIST_NO_ODDS`: n=76, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=11, two_prices=6, avg_raw=0.021667, avg_ip=-0.008962, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=181, two_prices=156, avg_raw=-0.006538, avg_ip=0.002492, beat_rate=0.076923
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

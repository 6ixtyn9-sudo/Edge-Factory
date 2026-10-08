# Edge Factory — CLV report (2026-09-07 to 2026-10-07)

## Overall

- total unique picks: 987
- picks with at least two prices: 771
- average raw odds delta: -0.003087
- average implied-probability delta: 0.0015
- beat-later-price rate: 0.123217
- beat-later-price sample: 771
- unmatched picks: 97
- picks with fewer than two snapshots: 117

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=115, two_prices=76, avg_raw=-0.001842, avg_ip=0.001156, beat_rate=0.197368
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=473, two_prices=419, avg_raw=-0.004988, avg_ip=0.002436, beat_rate=0.143198
- `ml-meta avg_p>=60`: n=116, two_prices=89, avg_raw=-0.001011, avg_ip=0.000421, beat_rate=0.067416
- `ml-meta avg_p>=65`: n=40, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=16, two_prices=7, avg_raw=-0.002857, avg_ip=0.003465, beat_rate=0.142857
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=10, avg_raw=0.006, avg_ip=-0.00541, beat_rate=0.0

## By bucket

- `CAUTION`: n=81, two_prices=73, avg_raw=-0.001233, avg_ip=0.000903, beat_rate=0.164384
- `CERTIFIED_CLEAN`: n=125, two_prices=116, avg_raw=-0.002759, avg_ip=0.001422, beat_rate=0.137931
- `SKIPPED_VETO`: n=500, two_prices=407, avg_raw=-0.002629, avg_ip=0.001434, beat_rate=0.132678
- `WATCHLIST_NO_ODDS`: n=76, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=12, two_prices=6, avg_raw=0.021667, avg_ip=-0.008962, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=183, two_prices=158, avg_raw=-0.006456, avg_ip=0.00246, beat_rate=0.075949
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

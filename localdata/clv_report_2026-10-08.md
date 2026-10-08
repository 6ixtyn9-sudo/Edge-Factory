# Edge Factory — CLV report (2026-09-08 to 2026-10-08)

## Overall

- total unique picks: 983
- picks with at least two prices: 768
- average raw odds delta: -0.002865
- average implied-probability delta: 0.001403
- beat-later-price rate: 0.121094
- beat-later-price sample: 768
- unmatched picks: 98
- picks with fewer than two snapshots: 115

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=113, two_prices=74, avg_raw=-0.001351, avg_ip=0.000953, beat_rate=0.189189
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=469, two_prices=416, avg_raw=-0.004687, avg_ip=0.002305, beat_rate=0.141827
- `ml-meta avg_p>=60`: n=118, two_prices=91, avg_raw=-0.000989, avg_ip=0.000412, beat_rate=0.065934
- `ml-meta avg_p>=65`: n=40, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=16, two_prices=7, avg_raw=-0.002857, avg_ip=0.003465, beat_rate=0.142857
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=10, avg_raw=0.006, avg_ip=-0.00541, beat_rate=0.0

## By bucket

- `CAUTION`: n=78, two_prices=70, avg_raw=-0.000714, avg_ip=0.000695, beat_rate=0.157143
- `CERTIFIED_CLEAN`: n=126, two_prices=117, avg_raw=-0.002735, avg_ip=0.001463, beat_rate=0.136752
- `SKIPPED_VETO`: n=496, two_prices=405, avg_raw=-0.002296, avg_ip=0.001273, beat_rate=0.130864
- `WATCHLIST_NO_ODDS`: n=77, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=11, two_prices=5, avg_raw=0.026, avg_ip=-0.010754, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=185, two_prices=160, avg_raw=-0.006375, avg_ip=0.00243, beat_rate=0.075
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

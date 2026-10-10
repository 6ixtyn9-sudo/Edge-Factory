# Edge Factory — CLV report (2026-09-09 to 2026-10-09)

## Overall

- total unique picks: 988
- picks with at least two prices: 769
- average raw odds delta: -0.003043
- average implied-probability delta: 0.001489
- beat-later-price rate: 0.120936
- beat-later-price sample: 769
- unmatched picks: 102
- picks with fewer than two snapshots: 116

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=118, two_prices=77, avg_raw=-0.001818, avg_ip=0.001283, beat_rate=0.194805
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=465, two_prices=410, avg_raw=-0.004951, avg_ip=0.002416, beat_rate=0.141463
- `ml-meta avg_p>=60`: n=122, two_prices=95, avg_raw=-0.000947, avg_ip=0.000395, beat_rate=0.063158
- `ml-meta avg_p>=65`: n=40, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=15, two_prices=6, avg_raw=-0.006667, avg_ip=0.005413, beat_rate=0.166667
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=15, two_prices=11, avg_raw=0.005455, avg_ip=-0.004918, beat_rate=0.0

## By bucket

- `CAUTION`: n=77, two_prices=69, avg_raw=-0.000725, avg_ip=0.000705, beat_rate=0.15942
- `CERTIFIED_CLEAN`: n=126, two_prices=117, avg_raw=-0.003419, avg_ip=0.001733, beat_rate=0.128205
- `SKIPPED_VETO`: n=503, two_prices=409, avg_raw=-0.002372, avg_ip=0.00133, beat_rate=0.132029
- `WATCHLIST_NO_ODDS`: n=80, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=9, two_prices=5, avg_raw=0.022, avg_ip=-0.00911, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=183, two_prices=158, avg_raw=-0.006456, avg_ip=0.00246, beat_rate=0.075949
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

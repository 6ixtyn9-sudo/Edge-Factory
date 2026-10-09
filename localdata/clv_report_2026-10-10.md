# Edge Factory — CLV report (2026-09-10 to 2026-10-10)

## Overall

- total unique picks: 1014
- picks with at least two prices: 785
- average raw odds delta: -0.002573
- average implied-probability delta: 0.001194
- beat-later-price rate: 0.105732
- beat-later-price sample: 785
- unmatched picks: 119
- picks with fewer than two snapshots: 109

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=124, two_prices=81, avg_raw=-0.001111, avg_ip=0.000868, beat_rate=0.17284
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=478, two_prices=415, avg_raw=-0.004313, avg_ip=0.001985, beat_rate=0.120482
- `ml-meta avg_p>=60`: n=128, two_prices=99, avg_raw=-0.000505, avg_ip=0.000157, beat_rate=0.050505
- `ml-meta avg_p>=65`: n=46, two_prices=31, avg_raw=0.0, avg_ip=0.000161, beat_rate=0.064516
- `ml-meta avg_p>=70`: n=10, two_prices=6, avg_raw=-0.006667, avg_ip=0.005413, beat_rate=0.166667
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=15, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0

## By bucket

- `CAUTION`: n=77, two_prices=69, avg_raw=-0.001739, avg_ip=0.001205, beat_rate=0.15942
- `CERTIFIED_CLEAN`: n=129, two_prices=121, avg_raw=-0.003058, avg_ip=0.001469, beat_rate=0.115702
- `SKIPPED_VETO`: n=510, two_prices=415, avg_raw=-0.001711, avg_ip=0.000949, beat_rate=0.113253
- `WATCHLIST_NO_ODDS`: n=90, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=10, two_prices=5, avg_raw=0.022, avg_ip=-0.00911, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=188, two_prices=164, avg_raw=-0.00561, avg_ip=0.00196, beat_rate=0.060976
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

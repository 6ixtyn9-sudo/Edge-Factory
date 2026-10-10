# Edge Factory — CLV report (2026-09-10 to 2026-10-10)

## Overall

- total unique picks: 1031
- picks with at least two prices: 791
- average raw odds delta: -0.0011
- average implied-probability delta: 0.000828
- beat-later-price rate: 0.10493
- beat-later-price sample: 791
- unmatched picks: 127
- picks with fewer than two snapshots: 113

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=126, two_prices=82, avg_raw=-0.001098, avg_ip=0.000857, beat_rate=0.170732
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=487, two_prices=419, avg_raw=-0.004153, avg_ip=0.001944, beat_rate=0.119332
- `ml-meta avg_p>=60`: n=132, two_prices=99, avg_raw=-0.000505, avg_ip=0.000157, beat_rate=0.050505
- `ml-meta avg_p>=65`: n=48, two_prices=32, avg_raw=0.034375, avg_ip=-0.008386, beat_rate=0.0625
- `ml-meta avg_p>=70`: n=10, two_prices=6, avg_raw=-0.006667, avg_ip=0.005413, beat_rate=0.166667
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=15, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0

## By bucket

- `CAUTION`: n=78, two_prices=70, avg_raw=-0.001714, avg_ip=0.001187, beat_rate=0.157143
- `CERTIFIED_CLEAN`: n=131, two_prices=123, avg_raw=0.006341, avg_ip=-0.00085, beat_rate=0.113821
- `SKIPPED_VETO`: n=518, two_prices=418, avg_raw=-0.001699, avg_ip=0.000942, beat_rate=0.11244
- `WATCHLIST_NO_ODDS`: n=96, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=10, two_prices=5, avg_raw=0.022, avg_ip=-0.00911, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=188, two_prices=164, avg_raw=-0.00561, avg_ip=0.00196, beat_rate=0.060976
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

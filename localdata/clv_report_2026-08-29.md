# Edge Factory — CLV report (2026-07-30 to 2026-08-29)

## Overall

- total unique picks: 553
- picks with at least two prices: 501
- average raw odds delta: 0.008285
- average implied-probability delta: -0.001692
- beat-later-price rate: 0.139721
- beat-later-price sample: 501
- unmatched picks: 27
- picks with fewer than two snapshots: 23

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=148, two_prices=132, avg_raw=0.001545, avg_ip=-0.000872, beat_rate=0.136364
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=40, two_prices=38, avg_raw=0.005658, avg_ip=-0.003196, beat_rate=0.026316
- `ml-meta avg_p>=55`: n=244, two_prices=225, avg_raw=0.003556, avg_ip=-0.000649, beat_rate=0.173333
- `ml-meta avg_p>=60`: n=42, two_prices=39, avg_raw=0.081641, avg_ip=-0.015507, beat_rate=0.025641
- `ml-meta avg_p>=65`: n=14, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=13, two_prices=11, avg_raw=0.013636, avg_ip=-0.005547, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=85, two_prices=78, avg_raw=0.006538, avg_ip=-0.001672, beat_rate=0.115385
- `CERTIFIED_CLEAN`: n=37, two_prices=36, avg_raw=0.084111, avg_ip=-0.013984, beat_rate=0.222222
- `SKIPPED_VETO`: n=300, two_prices=288, avg_raw=0.001781, avg_ip=-0.000643, beat_rate=0.166667
- `WATCHLIST_NO_ODDS`: n=26, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=7, two_prices=6, avg_raw=-0.006667, avg_ip=0.005316, beat_rate=0.166667
- `WATCHLIST_UNCORROBORATED_PRICE`: n=72, two_prices=68, avg_raw=-0.000147, avg_ip=0.000486, beat_rate=0.058824
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

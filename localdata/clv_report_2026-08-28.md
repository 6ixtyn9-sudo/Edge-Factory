# Edge Factory — CLV report (2026-07-29 to 2026-08-28)

## Overall

- total unique picks: 505
- picks with at least two prices: 462
- average raw odds delta: 0.002708
- average implied-probability delta: -0.000808
- beat-later-price rate: 0.140693
- beat-later-price sample: 462
- unmatched picks: 23
- picks with fewer than two snapshots: 19

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=136, two_prices=123, avg_raw=0.001333, avg_ip=-0.000721, beat_rate=0.138211
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=41, two_prices=39, avg_raw=0.005513, avg_ip=-0.003114, beat_rate=0.025641
- `ml-meta avg_p>=55`: n=211, two_prices=198, avg_raw=0.004394, avg_ip=-0.000965, beat_rate=0.176768
- `ml-meta avg_p>=60`: n=38, two_prices=35, avg_raw=0.007257, avg_ip=-0.003196, beat_rate=0.028571
- `ml-meta avg_p>=65`: n=14, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=13, two_prices=11, avg_raw=0.013636, avg_ip=-0.005547, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=81, two_prices=75, avg_raw=0.0068, avg_ip=-0.001739, beat_rate=0.12
- `CERTIFIED_CLEAN`: n=29, two_prices=29, avg_raw=0.004414, avg_ip=-0.000623, beat_rate=0.241379
- `SKIPPED_VETO`: n=279, two_prices=269, avg_raw=0.002093, avg_ip=-0.000796, beat_rate=0.163569
- `WATCHLIST_NO_ODDS`: n=22, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=62, two_prices=59, avg_raw=-0.001017, avg_ip=0.000863, beat_rate=0.067797
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

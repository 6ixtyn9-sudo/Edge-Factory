# Edge Factory — CLV report (2026-07-30 to 2026-08-29)

## Overall

- total unique picks: 549
- picks with at least two prices: 498
- average raw odds delta: 0.008516
- average implied-probability delta: -0.001781
- beat-later-price rate: 0.13253
- beat-later-price sample: 498
- unmatched picks: 27
- picks with fewer than two snapshots: 22

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=148, two_prices=131, avg_raw=0.001405, avg_ip=-0.000745, beat_rate=0.129771
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=40, two_prices=38, avg_raw=0.005658, avg_ip=-0.003196, beat_rate=0.026316
- `ml-meta avg_p>=55`: n=240, two_prices=223, avg_raw=0.004081, avg_ip=-0.000909, beat_rate=0.161435
- `ml-meta avg_p>=60`: n=42, two_prices=39, avg_raw=0.081641, avg_ip=-0.015507, beat_rate=0.025641
- `ml-meta avg_p>=65`: n=14, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=13, two_prices=11, avg_raw=0.013636, avg_ip=-0.005547, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=84, two_prices=77, avg_raw=0.006623, avg_ip=-0.001694, beat_rate=0.116883
- `CERTIFIED_CLEAN`: n=36, two_prices=35, avg_raw=0.087371, avg_ip=-0.014599, beat_rate=0.2
- `SKIPPED_VETO`: n=297, two_prices=285, avg_raw=0.002011, avg_ip=-0.000761, beat_rate=0.157895
- `WATCHLIST_NO_ODDS`: n=26, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=7, two_prices=6, avg_raw=-0.006667, avg_ip=0.005316, beat_rate=0.166667
- `WATCHLIST_UNCORROBORATED_PRICE`: n=73, two_prices=70, avg_raw=-0.000143, avg_ip=0.000472, beat_rate=0.057143
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

# Edge Factory — CLV report (2026-07-29 to 2026-08-28)

## Overall

- total unique picks: 503
- picks with at least two prices: 459
- average raw odds delta: 0.002508
- average implied-probability delta: -0.000768
- beat-later-price rate: 0.141612
- beat-later-price sample: 459
- unmatched picks: 23
- picks with fewer than two snapshots: 20

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=136, two_prices=123, avg_raw=0.001333, avg_ip=-0.000721, beat_rate=0.138211
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=41, two_prices=39, avg_raw=0.005513, avg_ip=-0.003114, beat_rate=0.025641
- `ml-meta avg_p>=55`: n=209, two_prices=195, avg_raw=0.003744, avg_ip=-0.000744, beat_rate=0.179487
- `ml-meta avg_p>=60`: n=38, two_prices=35, avg_raw=0.0084, avg_ip=-0.003916, beat_rate=0.028571
- `ml-meta avg_p>=65`: n=14, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=13, two_prices=11, avg_raw=0.013636, avg_ip=-0.005547, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=81, two_prices=75, avg_raw=0.006133, avg_ip=-0.001396, beat_rate=0.12
- `CERTIFIED_CLEAN`: n=28, two_prices=28, avg_raw=0.002071, avg_ip=0.000157, beat_rate=0.25
- `SKIPPED_VETO`: n=279, two_prices=268, avg_raw=0.002175, avg_ip=-0.000901, beat_rate=0.164179
- `WATCHLIST_NO_ODDS`: n=22, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=61, two_prices=58, avg_raw=-0.001034, avg_ip=0.000878, beat_rate=0.068966
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

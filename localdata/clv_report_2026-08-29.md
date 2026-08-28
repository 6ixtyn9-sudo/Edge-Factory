# Edge Factory — CLV report (2026-07-30 to 2026-08-29)

## Overall

- total unique picks: 540
- picks with at least two prices: 494
- average raw odds delta: 0.002532
- average implied-probability delta: -0.000756
- beat-later-price rate: 0.131579
- beat-later-price sample: 494
- unmatched picks: 27
- picks with fewer than two snapshots: 18

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=145, two_prices=131, avg_raw=0.001252, avg_ip=-0.000677, beat_rate=0.129771
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=40, two_prices=38, avg_raw=0.005658, avg_ip=-0.003196, beat_rate=0.026316
- `ml-meta avg_p>=55`: n=236, two_prices=221, avg_raw=0.003937, avg_ip=-0.000864, beat_rate=0.158371
- `ml-meta avg_p>=60`: n=40, two_prices=37, avg_raw=0.006865, avg_ip=-0.003023, beat_rate=0.027027
- `ml-meta avg_p>=65`: n=14, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=13, two_prices=11, avg_raw=0.013636, avg_ip=-0.005547, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=83, two_prices=77, avg_raw=0.006623, avg_ip=-0.001694, beat_rate=0.116883
- `CERTIFIED_CLEAN`: n=33, two_prices=33, avg_raw=0.003879, avg_ip=-0.000548, beat_rate=0.212121
- `SKIPPED_VETO`: n=293, two_prices=284, avg_raw=0.001982, avg_ip=-0.000754, beat_rate=0.15493
- `WATCHLIST_NO_ODDS`: n=26, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=7, two_prices=6, avg_raw=-0.006667, avg_ip=0.005316, beat_rate=0.166667
- `WATCHLIST_UNCORROBORATED_PRICE`: n=72, two_prices=69, avg_raw=-0.00087, avg_ip=0.000738, beat_rate=0.057971
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

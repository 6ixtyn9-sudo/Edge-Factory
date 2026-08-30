# Edge Factory — CLV report (2026-07-31 to 2026-08-30)

## Overall

- total unique picks: 594
- picks with at least two prices: 536
- average raw odds delta: 0.007119
- average implied-probability delta: -0.001284
- beat-later-price rate: 0.143657
- beat-later-price sample: 536
- unmatched picks: 32
- picks with fewer than two snapshots: 24

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=158, two_prices=140, avg_raw=0.001029, avg_ip=-0.000581, beat_rate=0.135714
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=35, two_prices=33, avg_raw=0.00303, avg_ip=-0.001562, beat_rate=0.030303
- `ml-meta avg_p>=55`: n=276, two_prices=255, avg_raw=0.002275, avg_ip=-0.000182, beat_rate=0.176471
- `ml-meta avg_p>=60`: n=44, two_prices=40, avg_raw=0.0796, avg_ip=-0.015119, beat_rate=0.025
- `ml-meta avg_p>=65`: n=15, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=14, two_prices=12, avg_raw=0.0175, avg_ip=-0.00874, beat_rate=0.083333
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=91, two_prices=84, avg_raw=0.00381, avg_ip=-0.000453, beat_rate=0.142857
- `CERTIFIED_CLEAN`: n=41, two_prices=40, avg_raw=0.0767, avg_ip=-0.013528, beat_rate=0.225
- `SKIPPED_VETO`: n=317, two_prices=304, avg_raw=0.001243, avg_ip=-0.00036, beat_rate=0.164474
- `WATCHLIST_NO_ODDS`: n=30, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=7, two_prices=6, avg_raw=-0.006667, avg_ip=0.005316, beat_rate=0.166667
- `WATCHLIST_UNCORROBORATED_PRICE`: n=83, two_prices=78, avg_raw=-0.000385, avg_ip=0.000549, beat_rate=0.064103
- `WATCHLIST_UNKNOWN_CTX`: n=25, two_prices=24, avg_raw=0.005, avg_ip=-0.003102, beat_rate=0.0

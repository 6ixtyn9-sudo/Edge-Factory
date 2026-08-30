# Edge Factory — CLV report (2026-07-31 to 2026-08-30)

## Overall

- total unique picks: 585
- picks with at least two prices: 519
- average raw odds delta: 0.007642
- average implied-probability delta: -0.001418
- beat-later-price rate: 0.138728
- beat-later-price sample: 519
- unmatched picks: 30
- picks with fewer than two snapshots: 34

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=156, two_prices=138, avg_raw=0.001043, avg_ip=-0.00059, beat_rate=0.137681
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=35, two_prices=33, avg_raw=0.00303, avg_ip=-0.001562, beat_rate=0.030303
- `ml-meta avg_p>=55`: n=270, two_prices=240, avg_raw=0.003292, avg_ip=-0.000576, beat_rate=0.166667
- `ml-meta avg_p>=60`: n=43, two_prices=40, avg_raw=0.0796, avg_ip=-0.015119, beat_rate=0.025
- `ml-meta avg_p>=65`: n=15, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=14, two_prices=12, avg_raw=0.0125, avg_ip=-0.005085, beat_rate=0.083333
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=91, two_prices=82, avg_raw=0.006098, avg_ip=-0.001494, beat_rate=0.121951
- `CERTIFIED_CLEAN`: n=40, two_prices=38, avg_raw=0.079684, avg_ip=-0.013248, beat_rate=0.210526
- `SKIPPED_VETO`: n=311, two_prices=294, avg_raw=0.001252, avg_ip=-0.000343, beat_rate=0.166667
- `WATCHLIST_NO_ODDS`: n=28, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=7, two_prices=6, avg_raw=-0.006667, avg_ip=0.005316, beat_rate=0.166667
- `WATCHLIST_UNCORROBORATED_PRICE`: n=83, two_prices=75, avg_raw=-0.000133, avg_ip=0.000441, beat_rate=0.053333
- `WATCHLIST_UNKNOWN_CTX`: n=25, two_prices=24, avg_raw=0.005, avg_ip=-0.003102, beat_rate=0.0

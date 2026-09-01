# Edge Factory — CLV report (2026-08-02 to 2026-09-01)

## Overall

- total unique picks: 642
- picks with at least two prices: 571
- average raw odds delta: 0.005107
- average implied-probability delta: -0.00052
- beat-later-price rate: 0.154116
- beat-later-price sample: 571
- unmatched picks: 38
- picks with fewer than two snapshots: 33

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=167, two_prices=147, avg_raw=9.5e-05, avg_ip=-0.000117, beat_rate=0.142857
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=27, two_prices=26, avg_raw=-0.001154, avg_ip=-0.000109, beat_rate=0.038462
- `ml-meta avg_p>=55`: n=303, two_prices=277, avg_raw=-0.000217, avg_ip=0.000837, beat_rate=0.194946
- `ml-meta avg_p>=60`: n=48, two_prices=40, avg_raw=0.0796, avg_ip=-0.015119, beat_rate=0.025
- `ml-meta avg_p>=65`: n=15, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=15, two_prices=12, avg_raw=0.0175, avg_ip=-0.00874, beat_rate=0.083333
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=15, two_prices=13, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=100, two_prices=91, avg_raw=0.003626, avg_ip=-0.000482, beat_rate=0.142857
- `CERTIFIED_CLEAN`: n=46, two_prices=43, avg_raw=0.065535, avg_ip=-0.01018, beat_rate=0.232558
- `SKIPPED_VETO`: n=335, two_prices=319, avg_raw=-0.000633, avg_ip=0.000457, beat_rate=0.178683
- `WATCHLIST_NO_ODDS`: n=35, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=8, two_prices=6, avg_raw=-0.006667, avg_ip=0.005316, beat_rate=0.166667
- `WATCHLIST_UNCORROBORATED_PRICE`: n=96, two_prices=91, avg_raw=-0.001209, avg_ip=0.000893, beat_rate=0.076923
- `WATCHLIST_UNKNOWN_CTX`: n=22, two_prices=21, avg_raw=0.005714, avg_ip=-0.003546, beat_rate=0.0

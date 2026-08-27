# Edge Factory — CLV report (2026-07-28 to 2026-08-27)

## Overall

- total unique picks: 476
- picks with at least two prices: 433
- average raw odds delta: 0.00245
- average implied-probability delta: -0.000741
- beat-later-price rate: 0.143187
- beat-later-price sample: 433
- unmatched picks: 23
- picks with fewer than two snapshots: 19

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=133, two_prices=120, avg_raw=0.001033, avg_ip=-0.000577, beat_rate=0.141667
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=42, two_prices=40, avg_raw=0.005375, avg_ip=-0.003036, beat_rate=0.025
- `ml-meta avg_p>=55`: n=190, two_prices=177, avg_raw=0.003785, avg_ip=-0.000717, beat_rate=0.186441
- `ml-meta avg_p>=60`: n=35, two_prices=32, avg_raw=0.0095, avg_ip=-0.004473, beat_rate=0.0
- `ml-meta avg_p>=65`: n=12, two_prices=7, avg_raw=-0.001714, avg_ip=0.002619, beat_rate=0.285714
- `ml-meta avg_p>=70`: n=12, two_prices=10, avg_raw=0.015, avg_ip=-0.006102, beat_rate=0.1
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=79, two_prices=73, avg_raw=0.006438, avg_ip=-0.00151, beat_rate=0.109589
- `CERTIFIED_CLEAN`: n=23, two_prices=23, avg_raw=-0.000957, avg_ip=0.001434, beat_rate=0.304348
- `SKIPPED_VETO`: n=263, two_prices=253, avg_raw=0.002225, avg_ip=-0.000921, beat_rate=0.166008
- `WATCHLIST_NO_ODDS`: n=22, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=57, two_prices=54, avg_raw=-0.001111, avg_ip=0.000943, beat_rate=0.074074
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

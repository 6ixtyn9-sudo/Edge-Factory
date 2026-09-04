# Edge Factory — CLV report (2026-08-06 to 2026-09-05)

## Overall

- total unique picks: 766
- picks with at least two prices: 690
- average raw odds delta: 0.004994
- average implied-probability delta: -0.000761
- beat-later-price rate: 0.146377
- beat-later-price sample: 690
- unmatched picks: 44
- picks with fewer than two snapshots: 32

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=176, two_prices=152, avg_raw=0.000684, avg_ip=-0.000392, beat_rate=0.151316
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=16, two_prices=16, avg_raw=0.003125, avg_ip=-0.001774, beat_rate=0.0
- `ml-meta avg_p>=55`: n=391, two_prices=367, avg_raw=0.000981, avg_ip=0.000137, beat_rate=0.174387
- `ml-meta avg_p>=60`: n=53, two_prices=44, avg_raw=0.072591, avg_ip=-0.013858, beat_rate=0.022727
- `ml-meta avg_p>=65`: n=17, two_prices=10, avg_raw=-0.0132, avg_ip=0.006587, beat_rate=0.3
- `ml-meta avg_p>=70`: n=17, two_prices=14, avg_raw=0.015, avg_ip=-0.007491, beat_rate=0.071429
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=42, two_prices=38, avg_raw=0.001316, avg_ip=-0.000548, beat_rate=0.026316

## By bucket

- `CAUTION`: n=107, two_prices=98, avg_raw=0.008265, avg_ip=-0.001812, beat_rate=0.142857
- `CERTIFIED_CLEAN`: n=59, two_prices=56, avg_raw=0.048536, avg_ip=-0.006975, beat_rate=0.232143
- `SKIPPED_VETO`: n=396, two_prices=380, avg_raw=0.000205, avg_ip=-0.000133, beat_rate=0.168421
- `WATCHLIST_NO_ODDS`: n=39, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=17, two_prices=14, avg_raw=-0.011429, avg_ip=0.005674, beat_rate=0.142857
- `WATCHLIST_UNCORROBORATED_PRICE`: n=130, two_prices=124, avg_raw=-0.000968, avg_ip=0.000716, beat_rate=0.064516
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=18, avg_raw=0.006667, avg_ip=-0.004136, beat_rate=0.0

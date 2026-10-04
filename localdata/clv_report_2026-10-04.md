# Edge Factory — CLV report (2026-09-04 to 2026-10-04)

## Overall

- total unique picks: 1139
- picks with at least two prices: 906
- average raw odds delta: -0.00277
- average implied-probability delta: 0.001325
- beat-later-price rate: 0.130243
- beat-later-price sample: 906
- unmatched picks: 112
- picks with fewer than two snapshots: 121

## By rule

- `2way-unanimous avg_p>=60`: n=202, two_prices=136, avg_raw=-0.000735, avg_ip=0.000259, beat_rate=0.080882
- `2way-unanimous avg_p>=70`: n=143, two_prices=95, avg_raw=-0.001579, avg_ip=0.001116, beat_rate=0.210526
- `ml-meta avg_p>=55`: n=570, two_prices=507, avg_raw=-0.004339, avg_ip=0.00206, beat_rate=0.147929
- `ml-meta avg_p>=60`: n=111, two_prices=86, avg_raw=-0.001047, avg_ip=0.000436, beat_rate=0.069767
- `ml-meta avg_p>=65`: n=41, two_prices=29, avg_raw=0.0, avg_ip=0.000173, beat_rate=0.068966
- `ml-meta avg_p>=70`: n=21, two_prices=9, avg_raw=-0.002222, avg_ip=0.002695, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=11, two_prices=9, avg_raw=0.006667, avg_ip=-0.006011, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=38, two_prices=35, avg_raw=-0.000286, avg_ip=6.8e-05, beat_rate=0.085714

## By bucket

- `CAUTION`: n=99, two_prices=90, avg_raw=-0.002444, avg_ip=0.001905, beat_rate=0.177778
- `CERTIFIED_CLEAN`: n=135, two_prices=120, avg_raw=-0.003083, avg_ip=0.001465, beat_rate=0.158333
- `SKIPPED_VETO`: n=552, two_prices=467, avg_raw=-0.002099, avg_ip=0.001072, beat_rate=0.14561
- `WATCHLIST_NO_ODDS`: n=87, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=23, two_prices=14, avg_raw=0.009286, avg_ip=-0.003841, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=232, two_prices=205, avg_raw=-0.00522, avg_ip=0.001984, beat_rate=0.068293
- `WATCHLIST_UNKNOWN_CTX`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

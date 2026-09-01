# Edge Factory — CLV report (2026-08-03 to 2026-09-02)

## Overall

- total unique picks: 656
- picks with at least two prices: 590
- average raw odds delta: 0.005434
- average implied-probability delta: -0.000619
- beat-later-price rate: 0.155932
- beat-later-price sample: 590
- unmatched picks: 37
- picks with fewer than two snapshots: 29

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=166, two_prices=147, avg_raw=0.000435, avg_ip=-0.000287, beat_rate=0.14966
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=24, two_prices=23, avg_raw=-0.001304, avg_ip=-0.000123, beat_rate=0.043478
- `ml-meta avg_p>=55`: n=314, two_prices=292, avg_raw=0.000582, avg_ip=0.000665, beat_rate=0.195205
- `ml-meta avg_p>=60`: n=48, two_prices=40, avg_raw=0.0796, avg_ip=-0.015119, beat_rate=0.025
- `ml-meta avg_p>=65`: n=16, two_prices=10, avg_raw=-0.0012, avg_ip=0.001833, beat_rate=0.2
- `ml-meta avg_p>=70`: n=16, two_prices=13, avg_raw=0.016154, avg_ip=-0.008068, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=19, two_prices=17, avg_raw=0.000588, avg_ip=-0.000302, beat_rate=0.0

## By bucket

- `CAUTION`: n=97, two_prices=89, avg_raw=0.007753, avg_ip=-0.001809, beat_rate=0.146067
- `CERTIFIED_CLEAN`: n=48, two_prices=46, avg_raw=0.061261, avg_ip=-0.009516, beat_rate=0.217391
- `SKIPPED_VETO`: n=346, two_prices=332, avg_raw=-0.000789, avg_ip=0.000565, beat_rate=0.180723
- `WATCHLIST_NO_ODDS`: n=34, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=10, two_prices=8, avg_raw=-0.005, avg_ip=0.003987, beat_rate=0.125
- `WATCHLIST_UNCORROBORATED_PRICE`: n=100, two_prices=95, avg_raw=-0.001263, avg_ip=0.000934, beat_rate=0.084211
- `WATCHLIST_UNKNOWN_CTX`: n=21, two_prices=20, avg_raw=0.006, avg_ip=-0.003723, beat_rate=0.0

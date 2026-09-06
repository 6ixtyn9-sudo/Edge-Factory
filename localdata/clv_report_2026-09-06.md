# Edge Factory — CLV report (2026-08-07 to 2026-09-06)

## Overall

- total unique picks: 855
- picks with at least two prices: 746
- average raw odds delta: 0.004024
- average implied-probability delta: -0.000457
- beat-later-price rate: 0.152815
- beat-later-price sample: 746
- unmatched picks: 55
- picks with fewer than two snapshots: 57

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=188, two_prices=157, avg_raw=-0.000318, avg_ip=0.000129, beat_rate=0.159236
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=13, two_prices=13, avg_raw=0.002308, avg_ip=-0.000979, beat_rate=0.0
- `ml-meta avg_p>=55`: n=440, two_prices=403, avg_raw=0.000347, avg_ip=0.0003, beat_rate=0.181141
- `ml-meta avg_p>=60`: n=61, two_prices=45, avg_raw=0.070978, avg_ip=-0.01355, beat_rate=0.022222
- `ml-meta avg_p>=65`: n=20, two_prices=11, avg_raw=-0.012, avg_ip=0.005988, beat_rate=0.272727
- `ml-meta avg_p>=70`: n=22, two_prices=16, avg_raw=0.013125, avg_ip=-0.006555, beat_rate=0.0625
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=116, two_prices=106, avg_raw=0.005849, avg_ip=-0.000667, beat_rate=0.160377
- `CERTIFIED_CLEAN`: n=70, two_prices=59, avg_raw=0.046576, avg_ip=-0.007145, beat_rate=0.237288
- `SKIPPED_VETO`: n=423, two_prices=400, avg_raw=-0.00039, avg_ip=9.9e-05, beat_rate=0.1775
- `WATCHLIST_NO_ODDS`: n=47, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=24, two_prices=17, avg_raw=-0.009412, avg_ip=0.004672, beat_rate=0.117647
- `WATCHLIST_UNCORROBORATED_PRICE`: n=155, two_prices=146, avg_raw=-0.001164, avg_ip=0.000731, beat_rate=0.068493
- `WATCHLIST_UNKNOWN_CTX`: n=20, two_prices=18, avg_raw=0.006667, avg_ip=-0.004136, beat_rate=0.0

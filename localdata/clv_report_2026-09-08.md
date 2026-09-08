# Edge Factory — CLV report (2026-08-09 to 2026-09-08)

## Overall

- total unique picks: 868
- picks with at least two prices: 757
- average raw odds delta: 0.003701
- average implied-probability delta: -0.000325
- beat-later-price rate: 0.155878
- beat-later-price sample: 757
- unmatched picks: 55
- picks with fewer than two snapshots: 57

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=178, two_prices=144, avg_raw=0.0, avg_ip=6e-06, beat_rate=0.173611
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=8, two_prices=8, avg_raw=0.00125, avg_ip=-0.000479, beat_rate=0.0
- `ml-meta avg_p>=55`: n=467, two_prices=429, avg_raw=-0.00021, avg_ip=0.000528, beat_rate=0.179487
- `ml-meta avg_p>=60`: n=62, two_prices=48, avg_raw=0.066542, avg_ip=-0.012703, beat_rate=0.020833
- `ml-meta avg_p>=65`: n=20, two_prices=11, avg_raw=-0.012, avg_ip=0.005988, beat_rate=0.272727
- `ml-meta avg_p>=70`: n=22, two_prices=16, avg_raw=0.013125, avg_ip=-0.006555, beat_rate=0.0625
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=120, two_prices=109, avg_raw=0.005596, avg_ip=-0.000631, beat_rate=0.155963
- `CERTIFIED_CLEAN`: n=75, two_prices=65, avg_raw=0.0412, avg_ip=-0.006123, beat_rate=0.230769
- `SKIPPED_VETO`: n=425, two_prices=397, avg_raw=-0.00072, avg_ip=0.000293, beat_rate=0.186398
- `WATCHLIST_NO_ODDS`: n=46, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=19, avg_raw=-0.008421, avg_ip=0.004181, beat_rate=0.105263
- `WATCHLIST_UNCORROBORATED_PRICE`: n=158, two_prices=151, avg_raw=-0.001126, avg_ip=0.000707, beat_rate=0.066225
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.008125, avg_ip=-0.005084, beat_rate=0.0

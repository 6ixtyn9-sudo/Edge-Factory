# Edge Factory — CLV report (2026-08-08 to 2026-09-07)

## Overall

- total unique picks: 864
- picks with at least two prices: 760
- average raw odds delta: 0.00395
- average implied-probability delta: -0.000442
- beat-later-price rate: 0.153947
- beat-later-price sample: 760
- unmatched picks: 55
- picks with fewer than two snapshots: 51

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=189, two_prices=156, avg_raw=-0.000513, avg_ip=0.000236, beat_rate=0.166667
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=12, two_prices=12, avg_raw=0.0025, avg_ip=-0.00106, beat_rate=0.0
- `ml-meta avg_p>=55`: n=448, two_prices=416, avg_raw=0.000409, avg_ip=0.000262, beat_rate=0.180288
- `ml-meta avg_p>=60`: n=62, two_prices=48, avg_raw=0.066542, avg_ip=-0.012703, beat_rate=0.020833
- `ml-meta avg_p>=65`: n=20, two_prices=11, avg_raw=-0.012, avg_ip=0.005988, beat_rate=0.272727
- `ml-meta avg_p>=70`: n=22, two_prices=16, avg_raw=0.013125, avg_ip=-0.006555, beat_rate=0.0625
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=119, two_prices=108, avg_raw=0.006019, avg_ip=-0.000797, beat_rate=0.148148
- `CERTIFIED_CLEAN`: n=72, two_prices=62, avg_raw=0.044323, avg_ip=-0.006799, beat_rate=0.225806
- `SKIPPED_VETO`: n=428, two_prices=406, avg_raw=-0.000483, avg_ip=0.000165, beat_rate=0.184729
- `WATCHLIST_NO_ODDS`: n=47, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=25, two_prices=19, avg_raw=-0.008421, avg_ip=0.004181, beat_rate=0.105263
- `WATCHLIST_UNCORROBORATED_PRICE`: n=155, two_prices=148, avg_raw=-0.001149, avg_ip=0.000722, beat_rate=0.067568
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=17, avg_raw=0.007647, avg_ip=-0.004785, beat_rate=0.0

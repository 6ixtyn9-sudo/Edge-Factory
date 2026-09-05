# Edge Factory — CLV report (2026-08-06 to 2026-09-05)

## Overall

- total unique picks: 795
- picks with at least two prices: 711
- average raw odds delta: 0.004819
- average implied-probability delta: -0.000698
- beat-later-price rate: 0.151899
- beat-later-price sample: 711
- unmatched picks: 48
- picks with fewer than two snapshots: 36

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=183, two_prices=157, avg_raw=0.001045, avg_ip=-0.000425, beat_rate=0.152866
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=16, two_prices=16, avg_raw=0.003125, avg_ip=-0.001774, beat_rate=0.0
- `ml-meta avg_p>=55`: n=402, two_prices=377, avg_raw=0.000769, avg_ip=0.000218, beat_rate=0.183024
- `ml-meta avg_p>=60`: n=55, two_prices=45, avg_raw=0.070978, avg_ip=-0.01355, beat_rate=0.022222
- `ml-meta avg_p>=65`: n=20, two_prices=11, avg_raw=-0.012, avg_ip=0.005988, beat_rate=0.272727
- `ml-meta avg_p>=70`: n=19, two_prices=16, avg_raw=0.013125, avg_ip=-0.006555, beat_rate=0.0625
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=46, two_prices=40, avg_raw=0.001, avg_ip=-0.000424, beat_rate=0.05

## By bucket

- `CAUTION`: n=110, two_prices=101, avg_raw=0.008119, avg_ip=-0.001524, beat_rate=0.148515
- `CERTIFIED_CLEAN`: n=62, two_prices=58, avg_raw=0.047379, avg_ip=-0.007268, beat_rate=0.241379
- `SKIPPED_VETO`: n=407, two_prices=389, avg_raw=7.2e-05, avg_ip=-4.7e-05, beat_rate=0.174807
- `WATCHLIST_NO_ODDS`: n=41, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=19, two_prices=14, avg_raw=-0.011429, avg_ip=0.005674, beat_rate=0.142857
- `WATCHLIST_UNCORROBORATED_PRICE`: n=138, two_prices=131, avg_raw=-0.000992, avg_ip=0.000707, beat_rate=0.068702
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=18, avg_raw=0.006667, avg_ip=-0.004136, beat_rate=0.0

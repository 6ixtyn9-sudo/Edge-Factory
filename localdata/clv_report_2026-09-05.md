# Edge Factory — CLV report (2026-08-06 to 2026-09-05)

## Overall

- total unique picks: 803
- picks with at least two prices: 712
- average raw odds delta: 0.004573
- average implied-probability delta: -0.000602
- beat-later-price rate: 0.15309
- beat-later-price sample: 712
- unmatched picks: 50
- picks with fewer than two snapshots: 43

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=184, two_prices=157, avg_raw=-3.8e-05, avg_ip=8e-06, beat_rate=0.159236
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=16, two_prices=16, avg_raw=0.003125, avg_ip=-0.001774, beat_rate=0.0
- `ml-meta avg_p>=55`: n=405, two_prices=377, avg_raw=0.000769, avg_ip=0.000218, beat_rate=0.183024
- `ml-meta avg_p>=60`: n=56, two_prices=45, avg_raw=0.070978, avg_ip=-0.01355, beat_rate=0.022222
- `ml-meta avg_p>=65`: n=20, two_prices=11, avg_raw=-0.012, avg_ip=0.005988, beat_rate=0.272727
- `ml-meta avg_p>=70`: n=22, two_prices=16, avg_raw=0.013125, avg_ip=-0.006555, beat_rate=0.0625
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=46, two_prices=41, avg_raw=0.000976, avg_ip=-0.000413, beat_rate=0.04878

## By bucket

- `CAUTION`: n=110, two_prices=101, avg_raw=0.006436, avg_ip=-0.000852, beat_rate=0.158416
- `CERTIFIED_CLEAN`: n=65, two_prices=58, avg_raw=0.047379, avg_ip=-0.007268, beat_rate=0.241379
- `SKIPPED_VETO`: n=409, two_prices=389, avg_raw=7.2e-05, avg_ip=-4.7e-05, beat_rate=0.174807
- `WATCHLIST_NO_ODDS`: n=42, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=20, two_prices=14, avg_raw=-0.011429, avg_ip=0.005674, beat_rate=0.142857
- `WATCHLIST_UNCORROBORATED_PRICE`: n=139, two_prices=132, avg_raw=-0.000985, avg_ip=0.000702, beat_rate=0.068182
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=18, avg_raw=0.006667, avg_ip=-0.004136, beat_rate=0.0

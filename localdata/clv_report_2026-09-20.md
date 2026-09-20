# Edge Factory — CLV report (2026-08-21 to 2026-09-20)

## Overall

- total unique picks: 1169
- picks with at least two prices: 989
- average raw odds delta: 0.001335
- average implied-probability delta: 0.000476
- beat-later-price rate: 0.140546
- beat-later-price sample: 989
- unmatched picks: 75
- picks with fewer than two snapshots: 105

## By rule

- `2way-unanimous avg_p>=70`: n=233, two_prices=171, avg_raw=-0.001579, avg_ip=0.001151, beat_rate=0.175439
- `ml-meta avg_p>=55`: n=666, two_prices=610, avg_raw=-0.002541, avg_ip=0.001433, beat_rate=0.159016
- `ml-meta avg_p>=60`: n=136, two_prices=106, avg_raw=0.028302, avg_ip=-0.004887, beat_rate=0.056604
- `ml-meta avg_p>=65`: n=33, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=33, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=108, two_prices=97, avg_raw=0.004124, avg_ip=-0.000445, beat_rate=0.175258
- `CERTIFIED_CLEAN`: n=116, two_prices=101, avg_raw=0.024752, avg_ip=-0.003116, beat_rate=0.188119
- `SKIPPED_VETO`: n=595, two_prices=537, avg_raw=-0.001806, avg_ip=0.001067, beat_rate=0.162011
- `WATCHLIST_NO_ODDS`: n=65, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=28, two_prices=19, avg_raw=-0.001579, avg_ip=0.001351, beat_rate=0.105263
- `WATCHLIST_UNCORROBORATED_PRICE`: n=243, two_prices=221, avg_raw=-0.00267, avg_ip=0.001071, beat_rate=0.058824
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.083333

# Edge Factory — CLV report (2026-09-06 to 2026-10-06)

## Overall

- total unique picks: 1044
- picks with at least two prices: 813
- average raw odds delta: -0.002964
- average implied-probability delta: 0.001393
- beat-later-price rate: 0.125461
- beat-later-price sample: 813
- unmatched picks: 101
- picks with fewer than two snapshots: 128

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=124, two_prices=80, avg_raw=-0.00075, avg_ip=0.000659, beat_rate=0.2
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=508, two_prices=447, avg_raw=-0.004832, avg_ip=0.002278, beat_rate=0.145414
- `ml-meta avg_p>=60`: n=118, two_prices=87, avg_raw=-0.001034, avg_ip=0.000431, beat_rate=0.068966
- `ml-meta avg_p>=65`: n=38, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=16, two_prices=7, avg_raw=-0.002857, avg_ip=0.003465, beat_rate=0.142857
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=9, avg_raw=0.006667, avg_ip=-0.006011, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=13, two_prices=13, avg_raw=-0.003077, avg_ip=0.00109, beat_rate=0.076923

## By bucket

- `CAUTION`: n=88, two_prices=79, avg_raw=-0.001139, avg_ip=0.000835, beat_rate=0.151899
- `CERTIFIED_CLEAN`: n=128, two_prices=116, avg_raw=-0.002759, avg_ip=0.001422, beat_rate=0.137931
- `SKIPPED_VETO`: n=520, two_prices=423, avg_raw=-0.00253, avg_ip=0.001307, beat_rate=0.141844
- `WATCHLIST_NO_ODDS`: n=81, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=17, two_prices=12, avg_raw=0.010833, avg_ip=-0.004481, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=198, two_prices=171, avg_raw=-0.006199, avg_ip=0.002356, beat_rate=0.076023
- `WATCHLIST_UNKNOWN_CTX`: n=12, two_prices=10, avg_raw=0.0, avg_ip=0.0, beat_rate=0.1

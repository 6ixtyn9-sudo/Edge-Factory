# Edge Factory — CLV report (2026-09-06 to 2026-10-06)

## Overall

- total unique picks: 1045
- picks with at least two prices: 823
- average raw odds delta: -0.002928
- average implied-probability delta: 0.001376
- beat-later-price rate: 0.123937
- beat-later-price sample: 823
- unmatched picks: 101
- picks with fewer than two snapshots: 119

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=125, two_prices=81, avg_raw=-0.000741, avg_ip=0.000651, beat_rate=0.197531
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=508, two_prices=452, avg_raw=-0.004779, avg_ip=0.002252, beat_rate=0.143805
- `ml-meta avg_p>=60`: n=118, two_prices=90, avg_raw=-0.001, avg_ip=0.000417, beat_rate=0.066667
- `ml-meta avg_p>=65`: n=38, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=16, two_prices=7, avg_raw=-0.002857, avg_ip=0.003465, beat_rate=0.142857
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=10, avg_raw=0.006, avg_ip=-0.00541, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=13, two_prices=13, avg_raw=-0.003077, avg_ip=0.00109, beat_rate=0.076923

## By bucket

- `CAUTION`: n=88, two_prices=79, avg_raw=-0.001139, avg_ip=0.000835, beat_rate=0.151899
- `CERTIFIED_CLEAN`: n=128, two_prices=118, avg_raw=-0.002712, avg_ip=0.001398, beat_rate=0.135593
- `SKIPPED_VETO`: n=521, two_prices=429, avg_raw=-0.002494, avg_ip=0.001289, beat_rate=0.13986
- `WATCHLIST_NO_ODDS`: n=81, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=17, two_prices=12, avg_raw=0.010833, avg_ip=-0.004481, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=198, two_prices=173, avg_raw=-0.006127, avg_ip=0.002329, beat_rate=0.075145
- `WATCHLIST_UNKNOWN_CTX`: n=12, two_prices=10, avg_raw=0.0, avg_ip=0.0, beat_rate=0.1

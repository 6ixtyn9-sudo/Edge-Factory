# Edge Factory — CLV report (2026-09-06 to 2026-10-06)

## Overall

- total unique picks: 1045
- picks with at least two prices: 827
- average raw odds delta: -0.002914
- average implied-probability delta: 0.00137
- beat-later-price rate: 0.123337
- beat-later-price sample: 827
- unmatched picks: 101
- picks with fewer than two snapshots: 115

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=125, two_prices=82, avg_raw=-0.000732, avg_ip=0.000643, beat_rate=0.195122
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=508, two_prices=452, avg_raw=-0.004779, avg_ip=0.002252, beat_rate=0.143805
- `ml-meta avg_p>=60`: n=118, two_prices=92, avg_raw=-0.000978, avg_ip=0.000408, beat_rate=0.065217
- `ml-meta avg_p>=65`: n=38, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=16, two_prices=7, avg_raw=-0.002857, avg_ip=0.003465, beat_rate=0.142857
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=11, avg_raw=0.005455, avg_ip=-0.004918, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=13, two_prices=13, avg_raw=-0.003077, avg_ip=0.00109, beat_rate=0.076923

## By bucket

- `CAUTION`: n=88, two_prices=79, avg_raw=-0.001139, avg_ip=0.000835, beat_rate=0.151899
- `CERTIFIED_CLEAN`: n=128, two_prices=119, avg_raw=-0.002689, avg_ip=0.001386, beat_rate=0.134454
- `SKIPPED_VETO`: n=521, two_prices=432, avg_raw=-0.002477, avg_ip=0.00128, beat_rate=0.138889
- `WATCHLIST_NO_ODDS`: n=81, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=17, two_prices=12, avg_raw=0.010833, avg_ip=-0.004481, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=198, two_prices=173, avg_raw=-0.006127, avg_ip=0.002329, beat_rate=0.075145
- `WATCHLIST_UNKNOWN_CTX`: n=12, two_prices=10, avg_raw=0.0, avg_ip=0.0, beat_rate=0.1

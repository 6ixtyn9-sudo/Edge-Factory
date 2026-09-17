# Edge Factory — CLV report (2026-08-18 to 2026-09-17)

## Overall

- total unique picks: 996
- picks with at least two prices: 841
- average raw odds delta: 0.00176
- average implied-probability delta: 0.00044
- beat-later-price rate: 0.148633
- beat-later-price sample: 841
- unmatched picks: 66
- picks with fewer than two snapshots: 91

## By rule

- `2way-unanimous avg_p>=70`: n=197, two_prices=150, avg_raw=-0.000467, avg_ip=0.000543, beat_rate=0.16
- `ml-meta avg_p>=55`: n=567, two_prices=512, avg_raw=-0.003086, avg_ip=0.001714, beat_rate=0.171875
- `ml-meta avg_p>=60`: n=100, two_prices=81, avg_raw=0.037284, avg_ip=-0.006519, beat_rate=0.074074
- `ml-meta avg_p>=65`: n=31, two_prices=16, avg_raw=-0.00375, avg_ip=0.000669, beat_rate=0.0625
- `ml-meta avg_p>=70`: n=32, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=7, two_prices=6, avg_raw=0.001667, avg_ip=-0.001556, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=107, two_prices=95, avg_raw=0.005684, avg_ip=-0.001084, beat_rate=0.147368
- `CERTIFIED_CLEAN`: n=92, two_prices=74, avg_raw=0.036351, avg_ip=-0.004989, beat_rate=0.202703
- `SKIPPED_VETO`: n=502, two_prices=460, avg_raw=-0.00263, avg_ip=0.001332, beat_rate=0.180435
- `WATCHLIST_NO_ODDS`: n=54, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.004444, avg_ip=0.002071, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=200, two_prices=182, avg_raw=-0.002582, avg_ip=0.00109, beat_rate=0.054945
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.083333

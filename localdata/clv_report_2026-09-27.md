# Edge Factory — CLV report (2026-08-28 to 2026-09-27)

## Overall

- total unique picks: 1214
- picks with at least two prices: 1000
- average raw odds delta: 0.00031
- average implied-probability delta: 0.000744
- beat-later-price rate: 0.137
- beat-later-price sample: 1000
- unmatched picks: 90
- picks with fewer than two snapshots: 122

## By rule

- `2way-unanimous avg_p>=60`: n=114, two_prices=80, avg_raw=-0.00275, avg_ip=0.000508, beat_rate=0.0625
- `2way-unanimous avg_p>=70`: n=197, two_prices=139, avg_raw=-0.001295, avg_ip=0.000817, beat_rate=0.18705
- `ml-meta avg_p>=55`: n=652, two_prices=592, avg_raw=-0.003497, avg_ip=0.001742, beat_rate=0.157095
- `ml-meta avg_p>=60`: n=120, two_prices=89, avg_raw=0.031461, avg_ip=-0.004822, beat_rate=0.078652
- `ml-meta avg_p>=65`: n=39, two_prices=27, avg_raw=-0.002593, avg_ip=0.000711, beat_rate=0.074074
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=115, two_prices=103, avg_raw=-0.001359, avg_ip=0.001273, beat_rate=0.194175
- `CERTIFIED_CLEAN`: n=145, two_prices=129, avg_raw=0.019457, avg_ip=-0.002466, beat_rate=0.170543
- `SKIPPED_VETO`: n=589, two_prices=513, avg_raw=-0.002671, avg_ip=0.0013, beat_rate=0.153996
- `WATCHLIST_NO_ODDS`: n=74, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=253, two_prices=226, avg_raw=-0.003097, avg_ip=0.001196, beat_rate=0.061947
- `WATCHLIST_UNKNOWN_CTX`: n=11, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.111111

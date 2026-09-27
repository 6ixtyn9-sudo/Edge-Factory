# Edge Factory — CLV report (2026-08-28 to 2026-09-27)

## Overall

- total unique picks: 1202
- picks with at least two prices: 996
- average raw odds delta: 0.000361
- average implied-probability delta: 0.000728
- beat-later-price rate: 0.136546
- beat-later-price sample: 996
- unmatched picks: 85
- picks with fewer than two snapshots: 120

## By rule

- `2way-unanimous avg_p>=60`: n=106, two_prices=80, avg_raw=-0.00275, avg_ip=0.000508, beat_rate=0.0625
- `2way-unanimous avg_p>=70`: n=197, two_prices=139, avg_raw=-0.001295, avg_ip=0.000817, beat_rate=0.18705
- `ml-meta avg_p>=55`: n=650, two_prices=590, avg_raw=-0.003424, avg_ip=0.001717, beat_rate=0.155932
- `ml-meta avg_p>=60`: n=120, two_prices=89, avg_raw=0.031461, avg_ip=-0.004822, beat_rate=0.078652
- `ml-meta avg_p>=65`: n=37, two_prices=25, avg_raw=-0.0028, avg_ip=0.000768, beat_rate=0.08
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=115, two_prices=103, avg_raw=-0.001359, avg_ip=0.001273, beat_rate=0.194175
- `CERTIFIED_CLEAN`: n=144, two_prices=128, avg_raw=0.019609, avg_ip=-0.002486, beat_rate=0.171875
- `SKIPPED_VETO`: n=582, two_prices=511, avg_raw=-0.002583, avg_ip=0.001269, beat_rate=0.152642
- `WATCHLIST_NO_ODDS`: n=71, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=253, two_prices=226, avg_raw=-0.003097, avg_ip=0.001196, beat_rate=0.061947
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

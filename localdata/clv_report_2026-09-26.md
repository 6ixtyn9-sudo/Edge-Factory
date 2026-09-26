# Edge Factory — CLV report (2026-08-27 to 2026-09-26)

## Overall

- total unique picks: 1182
- picks with at least two prices: 979
- average raw odds delta: 0.000215
- average implied-probability delta: 0.000826
- beat-later-price rate: 0.143003
- beat-later-price sample: 979
- unmatched picks: 82
- picks with fewer than two snapshots: 120

## By rule

- `2way-unanimous avg_p>=60`: n=89, two_prices=65, avg_raw=-0.003385, avg_ip=0.000625, beat_rate=0.076923
- `2way-unanimous avg_p>=70`: n=199, two_prices=141, avg_raw=-0.001277, avg_ip=0.000806, beat_rate=0.184397
- `ml-meta avg_p>=55`: n=647, two_prices=588, avg_raw=-0.00369, avg_ip=0.001864, beat_rate=0.163265
- `ml-meta avg_p>=60`: n=119, two_prices=88, avg_raw=0.031818, avg_ip=-0.004876, beat_rate=0.079545
- `ml-meta avg_p>=65`: n=37, two_prices=25, avg_raw=-0.0028, avg_ip=0.000768, beat_rate=0.08
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=7, two_prices=6, avg_raw=0.001667, avg_ip=-0.001556, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=111, two_prices=99, avg_raw=-0.001212, avg_ip=0.001217, beat_rate=0.20202
- `CERTIFIED_CLEAN`: n=140, two_prices=124, avg_raw=0.020242, avg_ip=-0.002566, beat_rate=0.177419
- `SKIPPED_VETO`: n=573, two_prices=502, avg_raw=-0.002968, avg_ip=0.001479, beat_rate=0.163347
- `WATCHLIST_NO_ODDS`: n=68, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=253, two_prices=226, avg_raw=-0.003097, avg_ip=0.001196, beat_rate=0.061947
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

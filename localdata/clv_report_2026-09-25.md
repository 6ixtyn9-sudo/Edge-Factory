# Edge Factory — CLV report (2026-08-26 to 2026-09-25)

## Overall

- total unique picks: 1127
- picks with at least two prices: 936
- average raw odds delta: 0.000694
- average implied-probability delta: 0.000706
- beat-later-price rate: 0.147436
- beat-later-price sample: 936
- unmatched picks: 76
- picks with fewer than two snapshots: 115

## By rule

- `2way-unanimous avg_p>=60`: n=51, two_prices=38, avg_raw=-0.006316, avg_ip=0.000645, beat_rate=0.078947
- `2way-unanimous avg_p>=70`: n=201, two_prices=143, avg_raw=-0.001678, avg_ip=0.001135, beat_rate=0.188811
- `ml-meta avg_p>=55`: n=634, two_prices=577, avg_raw=-0.002946, avg_ip=0.001637, beat_rate=0.166378
- `ml-meta avg_p>=60`: n=118, two_prices=86, avg_raw=0.033023, avg_ip=-0.005231, beat_rate=0.081395
- `ml-meta avg_p>=65`: n=33, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=102, two_prices=92, avg_raw=0.001848, avg_ip=-0.000133, beat_rate=0.195652
- `CERTIFIED_CLEAN`: n=128, two_prices=113, avg_raw=0.022212, avg_ip=-0.002816, beat_rate=0.19469
- `SKIPPED_VETO`: n=554, two_prices=487, avg_raw=-0.002752, avg_ip=0.001493, beat_rate=0.168378
- `WATCHLIST_NO_ODDS`: n=63, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=244, two_prices=217, avg_raw=-0.003226, avg_ip=0.001245, beat_rate=0.064516
- `WATCHLIST_UNKNOWN_CTX`: n=9, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.142857

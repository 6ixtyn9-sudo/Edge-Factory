# Edge Factory — CLV report (2026-08-24 to 2026-09-23)

## Overall

- total unique picks: 1086
- picks with at least two prices: 904
- average raw odds delta: 0.000907
- average implied-probability delta: 0.000726
- beat-later-price rate: 0.149336
- beat-later-price sample: 904
- unmatched picks: 70
- picks with fewer than two snapshots: 112

## By rule

- `2way-unanimous avg_p>=60`: n=12, two_prices=9, avg_raw=0.022222, avg_ip=-0.013688, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=208, two_prices=150, avg_raw=-0.001667, avg_ip=0.00119, beat_rate=0.186667
- `ml-meta avg_p>=55`: n=626, two_prices=569, avg_raw=-0.00348, avg_ip=0.001901, beat_rate=0.168717
- `ml-meta avg_p>=60`: n=117, two_prices=85, avg_raw=0.033647, avg_ip=-0.005416, beat_rate=0.070588
- `ml-meta avg_p>=65`: n=33, two_prices=20, avg_raw=-0.003, avg_ip=0.000535, beat_rate=0.05
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=98, two_prices=87, avg_raw=0.003793, avg_ip=-0.000633, beat_rate=0.183908
- `CERTIFIED_CLEAN`: n=124, two_prices=108, avg_raw=0.021389, avg_ip=-0.002288, beat_rate=0.194444
- `SKIPPED_VETO`: n=544, two_prices=483, avg_raw=-0.00236, avg_ip=0.001464, beat_rate=0.171843
- `WATCHLIST_NO_ODDS`: n=60, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=225, two_prices=200, avg_raw=-0.00345, avg_ip=0.001286, beat_rate=0.065
- `WATCHLIST_UNKNOWN_CTX`: n=8, two_prices=6, avg_raw=0.0, avg_ip=0.0, beat_rate=0.166667

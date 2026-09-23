# Edge Factory — CLV report (2026-08-24 to 2026-09-23)

## Overall

- total unique picks: 1090
- picks with at least two prices: 911
- average raw odds delta: 0.000604
- average implied-probability delta: 0.000824
- beat-later-price rate: 0.151482
- beat-later-price sample: 911
- unmatched picks: 70
- picks with fewer than two snapshots: 109

## By rule

- `2way-unanimous avg_p>=60`: n=13, two_prices=10, avg_raw=0.003, avg_ip=-0.007675, beat_rate=0.1
- `2way-unanimous avg_p>=70`: n=208, two_prices=150, avg_raw=-0.001667, avg_ip=0.00119, beat_rate=0.186667
- `ml-meta avg_p>=55`: n=628, two_prices=574, avg_raw=-0.003624, avg_ip=0.001969, beat_rate=0.170732
- `ml-meta avg_p>=60`: n=117, two_prices=85, avg_raw=0.033647, avg_ip=-0.005416, beat_rate=0.070588
- `ml-meta avg_p>=65`: n=34, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=99, two_prices=88, avg_raw=0.001818, avg_ip=-9.8e-05, beat_rate=0.193182
- `CERTIFIED_CLEAN`: n=124, two_prices=109, avg_raw=0.020826, avg_ip=-0.001985, beat_rate=0.201835
- `SKIPPED_VETO`: n=545, two_prices=485, avg_raw=-0.002474, avg_ip=0.001494, beat_rate=0.173196
- `WATCHLIST_NO_ODDS`: n=60, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=227, two_prices=203, avg_raw=-0.003399, avg_ip=0.001267, beat_rate=0.064039
- `WATCHLIST_UNKNOWN_CTX`: n=8, two_prices=6, avg_raw=0.0, avg_ip=0.0, beat_rate=0.166667

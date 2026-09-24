# Edge Factory — CLV report (2026-08-25 to 2026-09-24)

## Overall

- total unique picks: 1100
- picks with at least two prices: 917
- average raw odds delta: 0.000807
- average implied-probability delta: 0.000697
- beat-later-price rate: 0.147219
- beat-later-price sample: 917
- unmatched picks: 70
- picks with fewer than two snapshots: 113

## By rule

- `2way-unanimous avg_p>=60`: n=25, two_prices=20, avg_raw=0.0015, avg_ip=-0.003837, beat_rate=0.05
- `2way-unanimous avg_p>=70`: n=203, two_prices=145, avg_raw=-0.001517, avg_ip=0.001014, beat_rate=0.186207
- `ml-meta avg_p>=55`: n=631, two_prices=575, avg_raw=-0.003339, avg_ip=0.001827, beat_rate=0.166957
- `ml-meta avg_p>=60`: n=117, two_prices=85, avg_raw=0.033647, avg_ip=-0.005416, beat_rate=0.070588
- `ml-meta avg_p>=65`: n=34, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=103, two_prices=91, avg_raw=0.001758, avg_ip=-9.5e-05, beat_rate=0.186813
- `CERTIFIED_CLEAN`: n=125, two_prices=110, avg_raw=0.020636, avg_ip=-0.001967, beat_rate=0.2
- `SKIPPED_VETO`: n=545, two_prices=482, avg_raw=-0.002095, avg_ip=0.001273, beat_rate=0.16805
- `WATCHLIST_NO_ODDS`: n=60, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=232, two_prices=208, avg_raw=-0.003317, avg_ip=0.001237, beat_rate=0.0625
- `WATCHLIST_UNKNOWN_CTX`: n=8, two_prices=6, avg_raw=0.0, avg_ip=0.0, beat_rate=0.166667

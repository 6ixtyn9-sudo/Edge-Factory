# Edge Factory — CLV report (2026-08-25 to 2026-09-24)

## Overall

- total unique picks: 1092
- picks with at least two prices: 913
- average raw odds delta: 0.000811
- average implied-probability delta: 0.0007
- beat-later-price rate: 0.147864
- beat-later-price sample: 913
- unmatched picks: 70
- picks with fewer than two snapshots: 109

## By rule

- `2way-unanimous avg_p>=60`: n=21, two_prices=18, avg_raw=0.001667, avg_ip=-0.004264, beat_rate=0.055556
- `2way-unanimous avg_p>=70`: n=203, two_prices=145, avg_raw=-0.001517, avg_ip=0.001014, beat_rate=0.186207
- `ml-meta avg_p>=55`: n=627, two_prices=573, avg_raw=-0.003351, avg_ip=0.001833, beat_rate=0.167539
- `ml-meta avg_p>=60`: n=117, two_prices=85, avg_raw=0.033647, avg_ip=-0.005416, beat_rate=0.070588
- `ml-meta avg_p>=65`: n=34, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=102, two_prices=91, avg_raw=0.001758, avg_ip=-9.5e-05, beat_rate=0.186813
- `CERTIFIED_CLEAN`: n=125, two_prices=110, avg_raw=0.020636, avg_ip=-0.001967, beat_rate=0.2
- `SKIPPED_VETO`: n=540, two_prices=480, avg_raw=-0.002104, avg_ip=0.001278, beat_rate=0.16875
- `WATCHLIST_NO_ODDS`: n=60, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=230, two_prices=206, avg_raw=-0.00335, avg_ip=0.001249, beat_rate=0.063107
- `WATCHLIST_UNKNOWN_CTX`: n=8, two_prices=6, avg_raw=0.0, avg_ip=0.0, beat_rate=0.166667

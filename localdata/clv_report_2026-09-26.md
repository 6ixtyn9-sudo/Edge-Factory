# Edge Factory — CLV report (2026-08-27 to 2026-09-26)

## Overall

- total unique picks: 1150
- picks with at least two prices: 952
- average raw odds delta: 0.000179
- average implied-probability delta: 0.000843
- beat-later-price rate: 0.144958
- beat-later-price sample: 952
- unmatched picks: 80
- picks with fewer than two snapshots: 118

## By rule

- `2way-unanimous avg_p>=60`: n=77, two_prices=59, avg_raw=-0.004576, avg_ip=0.000735, beat_rate=0.067797
- `2way-unanimous avg_p>=70`: n=199, two_prices=141, avg_raw=-0.001277, avg_ip=0.000806, beat_rate=0.184397
- `ml-meta avg_p>=55`: n=635, two_prices=575, avg_raw=-0.003774, avg_ip=0.001906, beat_rate=0.166957
- `ml-meta avg_p>=60`: n=115, two_prices=84, avg_raw=0.033333, avg_ip=-0.005109, beat_rate=0.083333
- `ml-meta avg_p>=65`: n=34, two_prices=22, avg_raw=-0.002727, avg_ip=0.000487, beat_rate=0.045455
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=105, two_prices=95, avg_raw=-0.001158, avg_ip=0.00109, beat_rate=0.2
- `CERTIFIED_CLEAN`: n=132, two_prices=117, avg_raw=0.021453, avg_ip=-0.002719, beat_rate=0.188034
- `SKIPPED_VETO`: n=560, two_prices=490, avg_raw=-0.003143, avg_ip=0.001538, beat_rate=0.165306
- `WATCHLIST_NO_ODDS`: n=66, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=250, two_prices=222, avg_raw=-0.003153, avg_ip=0.001217, beat_rate=0.063063
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

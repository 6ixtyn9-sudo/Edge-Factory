# Edge Factory — CLV report (2026-08-11 to 2026-09-10)

## Overall

- total unique picks: 864
- picks with at least two prices: 753
- average raw odds delta: 0.003823
- average implied-probability delta: -0.00025
- beat-later-price rate: 0.159363
- beat-later-price sample: 753
- unmatched picks: 55
- picks with fewer than two snapshots: 57

## By rule

- `2way+bc-confirms avg_p>=60`: n=8, two_prices=8, avg_raw=-0.015, avg_ip=0.0079, beat_rate=0.25
- `2way-unanimous avg_p>=70`: n=168, two_prices=135, avg_raw=0.000422, avg_ip=-0.000143, beat_rate=0.155556
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=494, two_prices=458, avg_raw=-0.000546, avg_ip=0.000789, beat_rate=0.187773
- `ml-meta avg_p>=60`: n=64, two_prices=50, avg_raw=0.06308, avg_ip=-0.011756, beat_rate=0.04
- `ml-meta avg_p>=65`: n=22, two_prices=13, avg_raw=-0.010154, avg_ip=0.005067, beat_rate=0.230769
- `ml-meta avg_p>=70`: n=29, two_prices=18, avg_raw=0.010556, avg_ip=-0.004479, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=5, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=114, two_prices=105, avg_raw=0.005905, avg_ip=-0.000874, beat_rate=0.161905
- `CERTIFIED_CLEAN`: n=70, two_prices=60, avg_raw=0.050467, avg_ip=-0.008574, beat_rate=0.2
- `SKIPPED_VETO`: n=434, two_prices=405, avg_raw=-0.001257, avg_ip=0.00066, beat_rate=0.192593
- `WATCHLIST_NO_ODDS`: n=46, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=26, two_prices=18, avg_raw=-0.007778, avg_ip=0.003956, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=158, two_prices=150, avg_raw=-0.001667, avg_ip=0.00107, beat_rate=0.073333
- `WATCHLIST_UNKNOWN_CTX`: n=16, two_prices=15, avg_raw=0.008667, avg_ip=-0.005423, beat_rate=0.0

# Edge Factory — CLV report (2026-08-14 to 2026-09-13)

## Overall

- total unique picks: 990
- picks with at least two prices: 847
- average raw odds delta: 0.004189
- average implied-probability delta: -0.000492
- beat-later-price rate: 0.146399
- beat-later-price sample: 847
- unmatched picks: 71
- picks with fewer than two snapshots: 73

## By rule

- `2way-unanimous avg_p>=70`: n=193, two_prices=151, avg_raw=0.000795, avg_ip=-0.000205, beat_rate=0.145695
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=586, two_prices=532, avg_raw=0.000395, avg_ip=0.000418, beat_rate=0.165414
- `ml-meta avg_p>=60`: n=75, two_prices=57, avg_raw=0.054912, avg_ip=-0.010031, beat_rate=0.087719
- `ml-meta avg_p>=65`: n=27, two_prices=17, avg_raw=-0.004824, avg_ip=0.002065, beat_rate=0.176471
- `ml-meta avg_p>=70`: n=30, two_prices=20, avg_raw=0.0095, avg_ip=-0.004031, beat_rate=0.1
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=122, two_prices=110, avg_raw=0.005545, avg_ip=-0.001139, beat_rate=0.154545
- `CERTIFIED_CLEAN`: n=82, two_prices=68, avg_raw=0.049676, avg_ip=-0.009267, beat_rate=0.191176
- `SKIPPED_VETO`: n=495, two_prices=459, avg_raw=-0.000828, avg_ip=0.000611, beat_rate=0.183007
- `WATCHLIST_NO_ODDS`: n=58, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=29, two_prices=19, avg_raw=-0.004211, avg_ip=0.001962, beat_rate=0.105263
- `WATCHLIST_UNCORROBORATED_PRICE`: n=190, two_prices=178, avg_raw=-0.000618, avg_ip=0.000576, beat_rate=0.044944
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=13, avg_raw=0.01, avg_ip=-0.006257, beat_rate=0.0

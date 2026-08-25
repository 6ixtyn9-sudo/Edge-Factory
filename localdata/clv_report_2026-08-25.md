# Edge Factory — CLV report (2026-07-26 to 2026-08-25)

## Overall

- total unique picks: 449
- picks with at least two prices: 404
- average raw odds delta: 0.002156
- average implied-probability delta: -0.000857
- beat-later-price rate: 0.136139
- beat-later-price sample: 404
- unmatched picks: 23
- picks with fewer than two snapshots: 21

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=133, two_prices=120, avg_raw=0.001533, avg_ip=-0.000983, beat_rate=0.133333
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=44, two_prices=42, avg_raw=0.005119, avg_ip=-0.002892, beat_rate=0.02381
- `ml-meta avg_p>=55`: n=166, two_prices=150, avg_raw=0.003067, avg_ip=-0.000827, beat_rate=0.18
- `ml-meta avg_p>=60`: n=32, two_prices=30, avg_raw=0.0088, avg_ip=-0.00408, beat_rate=0.0
- `ml-meta avg_p>=65`: n=10, two_prices=5, avg_raw=-0.0024, avg_ip=0.003666, beat_rate=0.4
- `ml-meta avg_p>=70`: n=12, two_prices=10, avg_raw=0.015, avg_ip=-0.006102, beat_rate=0.1
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=74, two_prices=67, avg_raw=0.003582, avg_ip=-0.000202, beat_rate=0.119403
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=244, two_prices=233, avg_raw=0.002588, avg_ip=-0.001523, beat_rate=0.150215
- `WATCHLIST_NO_ODDS`: n=22, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=55, two_prices=52, avg_raw=-0.001154, avg_ip=0.000979, beat_rate=0.076923
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

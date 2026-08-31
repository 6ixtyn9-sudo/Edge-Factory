# Edge Factory — CLV report (2026-08-01 to 2026-08-31)

## Overall

- total unique picks: 617
- picks with at least two prices: 547
- average raw odds delta: 0.005861
- average implied-probability delta: -0.000809
- beat-later-price rate: 0.146252
- beat-later-price sample: 547
- unmatched picks: 35
- picks with fewer than two snapshots: 34

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=168, two_prices=147, avg_raw=0.001048, avg_ip=-0.000601, beat_rate=0.122449
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=31, two_prices=30, avg_raw=-0.001, avg_ip=-9.5e-05, beat_rate=0.033333
- `ml-meta avg_p>=55`: n=290, two_prices=262, avg_raw=0.000344, avg_ip=0.000602, beat_rate=0.187023
- `ml-meta avg_p>=60`: n=47, two_prices=40, avg_raw=0.0796, avg_ip=-0.015119, beat_rate=0.025
- `ml-meta avg_p>=65`: n=15, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=14, two_prices=12, avg_raw=0.0175, avg_ip=-0.00874, beat_rate=0.083333
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=92, two_prices=85, avg_raw=0.004235, avg_ip=-0.000706, beat_rate=0.141176
- `CERTIFIED_CLEAN`: n=43, two_prices=41, avg_raw=0.068, avg_ip=-0.010422, beat_rate=0.243902
- `SKIPPED_VETO`: n=329, two_prices=309, avg_raw=0.000252, avg_ip=4.6e-05, beat_rate=0.165049
- `WATCHLIST_NO_ODDS`: n=33, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=7, two_prices=6, avg_raw=-0.006667, avg_ip=0.005316, beat_rate=0.166667
- `WATCHLIST_UNCORROBORATED_PRICE`: n=88, two_prices=82, avg_raw=-0.00122, avg_ip=0.000895, beat_rate=0.073171
- `WATCHLIST_UNKNOWN_CTX`: n=25, two_prices=24, avg_raw=0.005, avg_ip=-0.003102, beat_rate=0.0

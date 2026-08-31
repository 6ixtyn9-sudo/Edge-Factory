# Edge Factory — CLV report (2026-08-01 to 2026-08-31)

## Overall

- total unique picks: 633
- picks with at least two prices: 556
- average raw odds delta: 0.005658
- average implied-probability delta: -0.000745
- beat-later-price rate: 0.151079
- beat-later-price sample: 556
- unmatched picks: 37
- picks with fewer than two snapshots: 39

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=168, two_prices=148, avg_raw=0.000905, avg_ip=-0.000525, beat_rate=0.128378
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=31, two_prices=30, avg_raw=-0.001, avg_ip=-9.5e-05, beat_rate=0.033333
- `ml-meta avg_p>=55`: n=297, two_prices=270, avg_raw=0.000185, avg_ip=0.00065, beat_rate=0.192593
- `ml-meta avg_p>=60`: n=48, two_prices=40, avg_raw=0.0796, avg_ip=-0.015119, beat_rate=0.025
- `ml-meta avg_p>=65`: n=15, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=15, two_prices=12, avg_raw=0.0175, avg_ip=-0.00874, beat_rate=0.083333
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=7, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None

## By bucket

- `CAUTION`: n=97, two_prices=85, avg_raw=0.004235, avg_ip=-0.000706, beat_rate=0.141176
- `CERTIFIED_CLEAN`: n=44, two_prices=42, avg_raw=0.066381, avg_ip=-0.010173, beat_rate=0.238095
- `SKIPPED_VETO`: n=333, two_prices=316, avg_raw=8.9e-05, avg_ip=0.000109, beat_rate=0.170886
- `WATCHLIST_NO_ODDS`: n=35, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=7, two_prices=6, avg_raw=-0.006667, avg_ip=0.005316, beat_rate=0.166667
- `WATCHLIST_UNCORROBORATED_PRICE`: n=92, two_prices=83, avg_raw=-0.001325, avg_ip=0.000979, beat_rate=0.084337
- `WATCHLIST_UNKNOWN_CTX`: n=25, two_prices=24, avg_raw=0.005, avg_ip=-0.003102, beat_rate=0.0

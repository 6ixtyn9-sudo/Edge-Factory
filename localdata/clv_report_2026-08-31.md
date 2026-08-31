# Edge Factory — CLV report (2026-08-01 to 2026-08-31)

## Overall

- total unique picks: 633
- picks with at least two prices: 568
- average raw odds delta: 0.005081
- average implied-probability delta: -0.000492
- beat-later-price rate: 0.15493
- beat-later-price sample: 568
- unmatched picks: 37
- picks with fewer than two snapshots: 27

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=168, two_prices=148, avg_raw=9.5e-05, avg_ip=-0.000116, beat_rate=0.141892
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=31, two_prices=30, avg_raw=-0.001, avg_ip=-9.5e-05, beat_rate=0.033333
- `ml-meta avg_p>=55`: n=297, two_prices=275, avg_raw=-0.000327, avg_ip=0.000908, beat_rate=0.196364
- `ml-meta avg_p>=60`: n=48, two_prices=40, avg_raw=0.0796, avg_ip=-0.015119, beat_rate=0.025
- `ml-meta avg_p>=65`: n=15, two_prices=9, avg_raw=-0.001333, avg_ip=0.002037, beat_rate=0.222222
- `ml-meta avg_p>=70`: n=15, two_prices=12, avg_raw=0.0175, avg_ip=-0.00874, beat_rate=0.083333
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=7, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=97, two_prices=90, avg_raw=0.003667, avg_ip=-0.000488, beat_rate=0.144444
- `CERTIFIED_CLEAN`: n=45, two_prices=43, avg_raw=0.065535, avg_ip=-0.01018, beat_rate=0.232558
- `SKIPPED_VETO`: n=334, two_prices=320, avg_raw=-0.000725, avg_ip=0.000512, beat_rate=0.178125
- `WATCHLIST_NO_ODDS`: n=35, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=7, two_prices=6, avg_raw=-0.006667, avg_ip=0.005316, beat_rate=0.166667
- `WATCHLIST_UNCORROBORATED_PRICE`: n=90, two_prices=85, avg_raw=-0.001294, avg_ip=0.000956, beat_rate=0.082353
- `WATCHLIST_UNKNOWN_CTX`: n=25, two_prices=24, avg_raw=0.005, avg_ip=-0.003102, beat_rate=0.0

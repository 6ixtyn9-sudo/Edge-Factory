# Edge Factory — CLV report (2026-07-19 to 2026-08-18)

## Overall

- total unique picks: 298
- picks with at least two prices: 271
- average raw odds delta: 0.00314
- average implied-probability delta: -0.001426
- beat-later-price rate: 0.151292
- beat-later-price sample: 271
- unmatched picks: 15
- picks with fewer than two snapshots: 11

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=100, two_prices=92, avg_raw=0.002326, avg_ip=-0.001656, beat_rate=0.141304
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=46, two_prices=44, avg_raw=0.005114, avg_ip=-0.002902, beat_rate=0.022727
- `3way-unanimous home-only avg_p>=60`: n=9, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=84, two_prices=77, avg_raw=0.008961, avg_ip=-0.003109, beat_rate=0.233766
- `ml-meta avg_p>=60`: n=4, two_prices=3, avg_raw=0.031333, avg_ip=-0.01564, beat_rate=0.0
- `ml-meta avg_p>=65`: n=5, two_prices=3, avg_raw=-0.004, avg_ip=0.006111, beat_rate=0.666667
- `ml-meta avg_p>=70`: n=4, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=54, two_prices=50, avg_raw=0.0024, avg_ip=-2.8e-05, beat_rate=0.14
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=162, two_prices=155, avg_raw=0.004987, avg_ip=-0.002599, beat_rate=0.148387
- `WATCHLIST_NO_ODDS`: n=14, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=5, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=21, two_prices=21, avg_raw=-0.007619, avg_ip=0.003408, beat_rate=0.190476
- `WATCHLIST_UNKNOWN_CTX`: n=20, two_prices=19, avg_raw=0.007368, avg_ip=-0.004571, beat_rate=0.0

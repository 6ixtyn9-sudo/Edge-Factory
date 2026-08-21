# Edge Factory — CLV report (2026-07-22 to 2026-08-21)

## Overall

- total unique picks: 338
- picks with at least two prices: 305
- average raw odds delta: 0.00279
- average implied-probability delta: -0.001295
- beat-later-price rate: 0.147541
- beat-later-price sample: 305
- unmatched picks: 18
- picks with fewer than two snapshots: 14

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=111, two_prices=100, avg_raw=0.00224, avg_ip=-0.001583, beat_rate=0.13
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=46, two_prices=44, avg_raw=0.005114, avg_ip=-0.002902, beat_rate=0.022727
- `ml-meta avg_p>=55`: n=112, two_prices=103, avg_raw=0.005243, avg_ip=-0.001877, beat_rate=0.203883
- `ml-meta avg_p>=60`: n=8, two_prices=7, avg_raw=0.016286, avg_ip=-0.00814, beat_rate=0.0
- `ml-meta avg_p>=65`: n=7, two_prices=3, avg_raw=-0.004, avg_ip=0.006111, beat_rate=0.666667
- `ml-meta avg_p>=70`: n=6, two_prices=5, avg_raw=0.03, avg_ip=-0.011901, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=2, avg_raw=-0.015, avg_ip=0.010506, beat_rate=0.5

## By bucket

- `CAUTION`: n=65, two_prices=60, avg_raw=0.002667, avg_ip=-0.000181, beat_rate=0.133333
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=173, two_prices=167, avg_raw=0.00379, avg_ip=-0.002283, beat_rate=0.155689
- `WATCHLIST_NO_ODDS`: n=17, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=33, two_prices=31, avg_raw=-0.001935, avg_ip=0.001642, beat_rate=0.129032
- `WATCHLIST_UNKNOWN_CTX`: n=22, two_prices=20, avg_raw=0.007, avg_ip=-0.004342, beat_rate=0.0

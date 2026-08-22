# Edge Factory — CLV report (2026-07-23 to 2026-08-22)

## Overall

- total unique picks: 395
- picks with at least two prices: 358
- average raw odds delta: 0.002656
- average implied-probability delta: -0.001105
- beat-later-price rate: 0.142458
- beat-later-price sample: 358
- unmatched picks: 22
- picks with fewer than two snapshots: 14

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=121, two_prices=110, avg_raw=0.001764, avg_ip=-0.00122, beat_rate=0.136364
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=46, two_prices=44, avg_raw=0.005114, avg_ip=-0.002902, beat_rate=0.022727
- `ml-meta avg_p>=55`: n=150, two_prices=138, avg_raw=0.004348, avg_ip=-0.001392, beat_rate=0.181159
- `ml-meta avg_p>=60`: n=11, two_prices=9, avg_raw=0.020444, avg_ip=-0.009207, beat_rate=0.0
- `ml-meta avg_p>=65`: n=8, two_prices=4, avg_raw=-0.003, avg_ip=0.004583, beat_rate=0.5
- `ml-meta avg_p>=70`: n=9, two_prices=8, avg_raw=0.01875, avg_ip=-0.007438, beat_rate=0.0
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25

## By bucket

- `CAUTION`: n=68, two_prices=63, avg_raw=0.003333, avg_ip=-2.7e-05, beat_rate=0.126984
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=208, two_prices=201, avg_raw=0.003547, avg_ip=-0.00207, beat_rate=0.154229
- `WATCHLIST_NO_ODDS`: n=21, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=44, two_prices=42, avg_raw=-0.001429, avg_ip=0.001212, beat_rate=0.095238
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

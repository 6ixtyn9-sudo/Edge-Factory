# Edge Factory — CLV report (2026-07-21 to 2026-08-20)

## Overall

- total unique picks: 320
- picks with at least two prices: 288
- average raw odds delta: 0.001948
- average implied-probability delta: -0.000952
- beat-later-price rate: 0.152778
- beat-later-price sample: 288
- unmatched picks: 17
- picks with fewer than two snapshots: 14

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=104, two_prices=95, avg_raw=0.002253, avg_ip=-0.001604, beat_rate=0.136842
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=46, two_prices=44, avg_raw=0.005114, avg_ip=-0.002902, beat_rate=0.022727
- `3way-unanimous home-only avg_p>=60`: n=8, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=95, two_prices=86, avg_raw=0.005116, avg_ip=-0.001741, beat_rate=0.22093
- `ml-meta avg_p>=60`: n=8, two_prices=7, avg_raw=0.012, avg_ip=-0.006434, beat_rate=0.142857
- `ml-meta avg_p>=65`: n=7, two_prices=3, avg_raw=-0.004, avg_ip=0.006111, beat_rate=0.666667
- `ml-meta avg_p>=70`: n=4, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=2, avg_raw=-0.015, avg_ip=0.010506, beat_rate=0.5

## By bucket

- `CAUTION`: n=61, two_prices=56, avg_raw=0.0025, avg_ip=-0.000205, beat_rate=0.125
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=166, two_prices=159, avg_raw=0.003101, avg_ip=-0.001838, beat_rate=0.157233
- `WATCHLIST_NO_ODDS`: n=16, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=5, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=30, two_prices=28, avg_raw=-0.006786, avg_ip=0.002983, beat_rate=0.178571
- `WATCHLIST_UNKNOWN_CTX`: n=20, two_prices=19, avg_raw=0.007368, avg_ip=-0.004571, beat_rate=0.0

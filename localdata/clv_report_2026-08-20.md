# Edge Factory — CLV report (2026-07-21 to 2026-08-20)

## Overall

- total unique picks: 319
- picks with at least two prices: 287
- average raw odds delta: 0.002059
- average implied-probability delta: -0.001
- beat-later-price rate: 0.15331
- beat-later-price sample: 287
- unmatched picks: 17
- picks with fewer than two snapshots: 14

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=104, two_prices=95, avg_raw=0.002253, avg_ip=-0.001604, beat_rate=0.136842
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=46, two_prices=44, avg_raw=0.005114, avg_ip=-0.002902, beat_rate=0.022727
- `3way-unanimous home-only avg_p>=60`: n=8, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=95, two_prices=86, avg_raw=0.005465, avg_ip=-0.001893, beat_rate=0.22093
- `ml-meta avg_p>=60`: n=8, two_prices=7, avg_raw=0.012, avg_ip=-0.006434, beat_rate=0.142857
- `ml-meta avg_p>=65`: n=7, two_prices=3, avg_raw=-0.004, avg_ip=0.006111, beat_rate=0.666667
- `ml-meta avg_p>=70`: n=4, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=-0.03, avg_ip=0.021011, beat_rate=1.0

## By bucket

- `CAUTION`: n=61, two_prices=56, avg_raw=0.0025, avg_ip=-0.000205, beat_rate=0.125
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=166, two_prices=159, avg_raw=0.003101, avg_ip=-0.001838, beat_rate=0.157233
- `WATCHLIST_NO_ODDS`: n=16, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=5, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=29, two_prices=27, avg_raw=-0.005926, avg_ip=0.002609, beat_rate=0.185185
- `WATCHLIST_UNKNOWN_CTX`: n=20, two_prices=19, avg_raw=0.007368, avg_ip=-0.004571, beat_rate=0.0

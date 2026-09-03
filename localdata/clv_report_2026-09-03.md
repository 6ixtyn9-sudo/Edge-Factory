# Edge Factory — CLV report (2026-08-04 to 2026-09-03)

## Overall

- total unique picks: 674
- picks with at least two prices: 604
- average raw odds delta: 0.005407
- average implied-probability delta: -0.000714
- beat-later-price rate: 0.153974
- beat-later-price sample: 604
- unmatched picks: 38
- picks with fewer than two snapshots: 32

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=168, two_prices=147, avg_raw=0.000571, avg_ip=-0.000354, beat_rate=0.142857
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=20, two_prices=19, avg_raw=0.002632, avg_ip=-0.001494, beat_rate=0.0
- `ml-meta avg_p>=55`: n=329, two_prices=307, avg_raw=0.000782, avg_ip=0.000393, beat_rate=0.192182
- `ml-meta avg_p>=60`: n=50, two_prices=41, avg_raw=0.077902, avg_ip=-0.014872, beat_rate=0.02439
- `ml-meta avg_p>=65`: n=17, two_prices=10, avg_raw=-0.0132, avg_ip=0.006587, beat_rate=0.3
- `ml-meta avg_p>=70`: n=17, two_prices=14, avg_raw=0.015, avg_ip=-0.007491, beat_rate=0.071429
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=19, two_prices=17, avg_raw=0.000588, avg_ip=-0.000302, beat_rate=0.0

## By bucket

- `CAUTION`: n=99, two_prices=90, avg_raw=0.008667, avg_ip=-0.002129, beat_rate=0.133333
- `CERTIFIED_CLEAN`: n=51, two_prices=48, avg_raw=0.058292, avg_ip=-0.009009, beat_rate=0.229167
- `SKIPPED_VETO`: n=355, two_prices=341, avg_raw=-0.000446, avg_ip=0.00029, beat_rate=0.175953
- `WATCHLIST_NO_ODDS`: n=35, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=12, two_prices=9, avg_raw=-0.017778, avg_ip=0.008826, beat_rate=0.222222
- `WATCHLIST_UNCORROBORATED_PRICE`: n=102, two_prices=97, avg_raw=-0.001237, avg_ip=0.000915, beat_rate=0.082474
- `WATCHLIST_UNKNOWN_CTX`: n=20, two_prices=19, avg_raw=0.006316, avg_ip=-0.003919, beat_rate=0.0

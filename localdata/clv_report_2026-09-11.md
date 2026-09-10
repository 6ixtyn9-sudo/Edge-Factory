# Edge Factory — CLV report (2026-08-12 to 2026-09-11)

## Overall

- total unique picks: 884
- picks with at least two prices: 770
- average raw odds delta: 0.003882
- average implied-probability delta: -0.000306
- beat-later-price rate: 0.157143
- beat-later-price sample: 770
- unmatched picks: 56
- picks with fewer than two snapshots: 59

## By rule

- `2way+bc-confirms avg_p>=60`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=173, two_prices=140, avg_raw=0.000336, avg_ip=-7.4e-05, beat_rate=0.157143
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=509, two_prices=471, avg_raw=-0.000531, avg_ip=0.000782, beat_rate=0.186837
- `ml-meta avg_p>=60`: n=69, two_prices=54, avg_raw=0.058407, avg_ip=-0.010885, beat_rate=0.037037
- `ml-meta avg_p>=65`: n=25, two_prices=16, avg_raw=-0.00825, avg_ip=0.004117, beat_rate=0.1875
- `ml-meta avg_p>=70`: n=29, two_prices=18, avg_raw=0.010556, avg_ip=-0.004479, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=5, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=115, two_prices=106, avg_raw=0.006604, avg_ip=-0.001299, beat_rate=0.160377
- `CERTIFIED_CLEAN`: n=70, two_prices=60, avg_raw=0.050967, avg_ip=-0.008718, beat_rate=0.183333
- `SKIPPED_VETO`: n=449, two_prices=418, avg_raw=-0.001218, avg_ip=0.000657, beat_rate=0.191388
- `WATCHLIST_NO_ODDS`: n=47, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=25, two_prices=17, avg_raw=-0.008235, avg_ip=0.004189, beat_rate=0.117647
- `WATCHLIST_UNCORROBORATED_PRICE`: n=163, two_prices=155, avg_raw=-0.001613, avg_ip=0.001035, beat_rate=0.070968
- `WATCHLIST_UNKNOWN_CTX`: n=15, two_prices=14, avg_raw=0.009286, avg_ip=-0.00581, beat_rate=0.0

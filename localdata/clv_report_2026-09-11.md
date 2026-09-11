# Edge Factory — CLV report (2026-08-12 to 2026-09-11)

## Overall

- total unique picks: 905
- picks with at least two prices: 786
- average raw odds delta: 0.003739
- average implied-probability delta: -0.000269
- beat-later-price rate: 0.164122
- beat-later-price sample: 786
- unmatched picks: 57
- picks with fewer than two snapshots: 62

## By rule

- `2way+bc-confirms avg_p>=60`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=178, two_prices=144, avg_raw=-2.1e-05, avg_ip=9e-05, beat_rate=0.166667
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=520, two_prices=481, avg_raw=-0.000644, avg_ip=0.000847, beat_rate=0.191268
- `ml-meta avg_p>=60`: n=72, two_prices=56, avg_raw=0.0565, avg_ip=-0.010626, beat_rate=0.071429
- `ml-meta avg_p>=65`: n=27, two_prices=16, avg_raw=-0.005125, avg_ip=0.002194, beat_rate=0.1875
- `ml-meta avg_p>=70`: n=29, two_prices=18, avg_raw=0.010556, avg_ip=-0.004479, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=5, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=118, two_prices=108, avg_raw=0.006111, avg_ip=-0.001112, beat_rate=0.166667
- `CERTIFIED_CLEAN`: n=74, two_prices=63, avg_raw=0.050603, avg_ip=-0.008802, beat_rate=0.206349
- `SKIPPED_VETO`: n=460, two_prices=427, avg_raw=-0.00152, avg_ip=0.000733, beat_rate=0.199063
- `WATCHLIST_NO_ODDS`: n=48, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=25, two_prices=17, avg_raw=-0.008235, avg_ip=0.004189, beat_rate=0.117647
- `WATCHLIST_UNCORROBORATED_PRICE`: n=165, two_prices=157, avg_raw=-0.001592, avg_ip=0.001022, beat_rate=0.070064
- `WATCHLIST_UNKNOWN_CTX`: n=15, two_prices=14, avg_raw=0.009286, avg_ip=-0.00581, beat_rate=0.0

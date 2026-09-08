# Edge Factory — CLV report (2026-08-10 to 2026-09-09)

## Overall

- total unique picks: 846
- picks with at least two prices: 744
- average raw odds delta: 0.003954
- average implied-probability delta: -0.000357
- beat-later-price rate: 0.157258
- beat-later-price sample: 744
- unmatched picks: 53
- picks with fewer than two snapshots: 50

## By rule

- `2way+bc-confirms avg_p>=60`: n=14, two_prices=14, avg_raw=-0.019286, avg_ip=0.008824, beat_rate=0.357143
- `2way-unanimous avg_p>=70`: n=168, two_prices=137, avg_raw=0.00073, avg_ip=-0.000322, beat_rate=0.153285
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=479, two_prices=445, avg_raw=-0.000337, avg_ip=0.00066, beat_rate=0.18427
- `ml-meta avg_p>=60`: n=62, two_prices=48, avg_raw=0.066542, avg_ip=-0.012703, beat_rate=0.020833
- `ml-meta avg_p>=65`: n=20, two_prices=11, avg_raw=-0.012, avg_ip=0.005988, beat_rate=0.272727
- `ml-meta avg_p>=70`: n=23, two_prices=17, avg_raw=0.013529, avg_ip=-0.006653, beat_rate=0.058824
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=113, two_prices=104, avg_raw=0.005865, avg_ip=-0.000661, beat_rate=0.163462
- `CERTIFIED_CLEAN`: n=71, two_prices=62, avg_raw=0.045452, avg_ip=-0.007138, beat_rate=0.241935
- `SKIPPED_VETO`: n=418, two_prices=394, avg_raw=-0.000599, avg_ip=0.000256, beat_rate=0.185279
- `WATCHLIST_NO_ODDS`: n=44, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=26, two_prices=18, avg_raw=-0.007778, avg_ip=0.003956, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=157, two_prices=150, avg_raw=-0.0016, avg_ip=0.001035, beat_rate=0.066667
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.008125, avg_ip=-0.005084, beat_rate=0.0

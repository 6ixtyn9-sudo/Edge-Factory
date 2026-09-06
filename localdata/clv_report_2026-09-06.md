# Edge Factory — CLV report (2026-08-07 to 2026-09-06)

## Overall

- total unique picks: 862
- picks with at least two prices: 755
- average raw odds delta: 0.004003
- average implied-probability delta: -0.000464
- beat-later-price rate: 0.150993
- beat-later-price sample: 755
- unmatched picks: 55
- picks with fewer than two snapshots: 53

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=192, two_prices=159, avg_raw=-0.000377, avg_ip=0.000163, beat_rate=0.163522
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=13, two_prices=13, avg_raw=0.002308, avg_ip=-0.000979, beat_rate=0.0
- `ml-meta avg_p>=55`: n=442, two_prices=408, avg_raw=0.000417, avg_ip=0.000258, beat_rate=0.176471
- `ml-meta avg_p>=60`: n=62, two_prices=47, avg_raw=0.067957, avg_ip=-0.012973, beat_rate=0.021277
- `ml-meta avg_p>=65`: n=20, two_prices=11, avg_raw=-0.012, avg_ip=0.005988, beat_rate=0.272727
- `ml-meta avg_p>=70`: n=22, two_prices=16, avg_raw=0.013125, avg_ip=-0.006555, beat_rate=0.0625
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=117, two_prices=106, avg_raw=0.006132, avg_ip=-0.000812, beat_rate=0.150943
- `CERTIFIED_CLEAN`: n=71, two_prices=61, avg_raw=0.045049, avg_ip=-0.006911, beat_rate=0.229508
- `SKIPPED_VETO`: n=428, two_prices=403, avg_raw=-0.000437, avg_ip=0.00013, beat_rate=0.17866
- `WATCHLIST_NO_ODDS`: n=47, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=24, two_prices=18, avg_raw=-0.008889, avg_ip=0.004413, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=155, two_prices=148, avg_raw=-0.001149, avg_ip=0.000722, beat_rate=0.067568
- `WATCHLIST_UNKNOWN_CTX`: n=20, two_prices=19, avg_raw=0.006842, avg_ip=-0.004281, beat_rate=0.0

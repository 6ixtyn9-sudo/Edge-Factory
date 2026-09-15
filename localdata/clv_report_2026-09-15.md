# Edge Factory — CLV report (2026-08-16 to 2026-09-15)

## Overall

- total unique picks: 990
- picks with at least two prices: 844
- average raw odds delta: 0.002062
- average implied-probability delta: 0.000293
- beat-later-price rate: 0.149289
- beat-later-price sample: 844
- unmatched picks: 67
- picks with fewer than two snapshots: 80

## By rule

- `2way-unanimous avg_p>=70`: n=193, two_prices=151, avg_raw=0.0, avg_ip=0.000289, beat_rate=0.152318
- `ml-meta avg_p>=55`: n=575, two_prices=521, avg_raw=-0.002764, avg_ip=0.001542, beat_rate=0.172745
- `ml-meta avg_p>=60`: n=97, two_prices=74, avg_raw=0.042297, avg_ip=-0.007726, beat_rate=0.067568
- `ml-meta avg_p>=65`: n=27, two_prices=16, avg_raw=-0.0075, avg_ip=0.00275, beat_rate=0.125
- `ml-meta avg_p>=70`: n=30, two_prices=20, avg_raw=0.0095, avg_ip=-0.004031, beat_rate=0.1
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=115, two_prices=102, avg_raw=0.005392, avg_ip=-0.001097, beat_rate=0.147059
- `CERTIFIED_CLEAN`: n=81, two_prices=66, avg_raw=0.045455, avg_ip=-0.00778, beat_rate=0.19697
- `SKIPPED_VETO`: n=499, two_prices=461, avg_raw=-0.003015, avg_ip=0.001559, beat_rate=0.186551
- `WATCHLIST_NO_ODDS`: n=55, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.004444, avg_ip=0.002071, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=199, two_prices=185, avg_raw=-0.002541, avg_ip=0.001072, beat_rate=0.054054
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=12, avg_raw=0.010833, avg_ip=-0.006779, beat_rate=0.0

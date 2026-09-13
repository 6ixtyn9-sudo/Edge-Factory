# Edge Factory — CLV report (2026-08-15 to 2026-09-14)

## Overall

- total unique picks: 983
- picks with at least two prices: 840
- average raw odds delta: 0.003083
- average implied-probability delta: -1.8e-05
- beat-later-price rate: 0.147619
- beat-later-price sample: 840
- unmatched picks: 71
- picks with fewer than two snapshots: 73

## By rule

- `2way-unanimous avg_p>=70`: n=192, two_prices=150, avg_raw=-0.000467, avg_ip=0.000517, beat_rate=0.146667
- `2way-unanimous min_p>=60 avg_p>=65`: n=7, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=579, two_prices=525, avg_raw=-0.00099, avg_ip=0.000965, beat_rate=0.169524
- `ml-meta avg_p>=60`: n=82, two_prices=64, avg_raw=0.048906, avg_ip=-0.008934, beat_rate=0.078125
- `ml-meta avg_p>=65`: n=26, two_prices=16, avg_raw=-0.0075, avg_ip=0.00275, beat_rate=0.125
- `ml-meta avg_p>=70`: n=29, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=118, two_prices=107, avg_raw=0.004953, avg_ip=-0.001073, beat_rate=0.149533
- `CERTIFIED_CLEAN`: n=80, two_prices=66, avg_raw=0.045455, avg_ip=-0.00778, beat_rate=0.19697
- `SKIPPED_VETO`: n=491, two_prices=454, avg_raw=-0.001938, avg_ip=0.001221, beat_rate=0.187225
- `WATCHLIST_NO_ODDS`: n=58, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=29, two_prices=19, avg_raw=-0.004211, avg_ip=0.001962, beat_rate=0.105263
- `WATCHLIST_UNCORROBORATED_PRICE`: n=193, two_prices=181, avg_raw=-0.000608, avg_ip=0.000567, beat_rate=0.044199
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=13, avg_raw=0.01, avg_ip=-0.006257, beat_rate=0.0

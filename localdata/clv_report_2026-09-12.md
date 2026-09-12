# Edge Factory — CLV report (2026-08-13 to 2026-09-12)

## Overall

- total unique picks: 948
- picks with at least two prices: 819
- average raw odds delta: 0.00406
- average implied-probability delta: -0.000443
- beat-later-price rate: 0.152625
- beat-later-price sample: 819
- unmatched picks: 63
- picks with fewer than two snapshots: 67

## By rule

- `2way-unanimous avg_p>=70`: n=191, two_prices=153, avg_raw=0.000569, avg_ip=-0.000184, beat_rate=0.150327
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=551, two_prices=505, avg_raw=-2e-05, avg_ip=0.000584, beat_rate=0.176238
- `ml-meta avg_p>=60`: n=72, two_prices=56, avg_raw=0.056429, avg_ip=-0.010592, beat_rate=0.071429
- `ml-meta avg_p>=65`: n=26, two_prices=16, avg_raw=-0.005125, avg_ip=0.002194, beat_rate=0.1875
- `ml-meta avg_p>=70`: n=29, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=123, two_prices=111, avg_raw=0.006306, avg_ip=-0.001349, beat_rate=0.162162
- `CERTIFIED_CLEAN`: n=77, two_prices=65, avg_raw=0.049046, avg_ip=-0.008531, beat_rate=0.2
- `SKIPPED_VETO`: n=477, two_prices=444, avg_raw=-0.00084, avg_ip=0.000494, beat_rate=0.186937
- `WATCHLIST_NO_ODDS`: n=51, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=28, two_prices=18, avg_raw=-0.007778, avg_ip=0.003956, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=177, two_prices=167, avg_raw=-0.001078, avg_ip=0.000792, beat_rate=0.053892
- `WATCHLIST_UNKNOWN_CTX`: n=15, two_prices=14, avg_raw=0.009286, avg_ip=-0.00581, beat_rate=0.0

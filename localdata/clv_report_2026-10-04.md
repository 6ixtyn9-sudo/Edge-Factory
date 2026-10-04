# Edge Factory — CLV report (2026-09-04 to 2026-10-04)

## Overall

- total unique picks: 1142
- picks with at least two prices: 910
- average raw odds delta: -0.002758
- average implied-probability delta: 0.001319
- beat-later-price rate: 0.12967
- beat-later-price sample: 910
- unmatched picks: 113
- picks with fewer than two snapshots: 120

## By rule

- `2way-unanimous avg_p>=60`: n=203, two_prices=139, avg_raw=-0.000719, avg_ip=0.000253, beat_rate=0.079137
- `2way-unanimous avg_p>=70`: n=143, two_prices=95, avg_raw=-0.001579, avg_ip=0.001116, beat_rate=0.210526
- `ml-meta avg_p>=55`: n=572, two_prices=508, avg_raw=-0.004331, avg_ip=0.002056, beat_rate=0.147638
- `ml-meta avg_p>=60`: n=111, two_prices=86, avg_raw=-0.001047, avg_ip=0.000436, beat_rate=0.069767
- `ml-meta avg_p>=65`: n=41, two_prices=29, avg_raw=0.0, avg_ip=0.000173, beat_rate=0.068966
- `ml-meta avg_p>=70`: n=21, two_prices=9, avg_raw=-0.002222, avg_ip=0.002695, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=11, two_prices=9, avg_raw=0.006667, avg_ip=-0.006011, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=38, two_prices=35, avg_raw=-0.000286, avg_ip=6.8e-05, beat_rate=0.085714

## By bucket

- `CAUTION`: n=99, two_prices=90, avg_raw=-0.002444, avg_ip=0.001905, beat_rate=0.177778
- `CERTIFIED_CLEAN`: n=136, two_prices=122, avg_raw=-0.003033, avg_ip=0.001441, beat_rate=0.155738
- `SKIPPED_VETO`: n=553, two_prices=467, avg_raw=-0.002099, avg_ip=0.001072, beat_rate=0.14561
- `WATCHLIST_NO_ODDS`: n=88, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=23, two_prices=15, avg_raw=0.008667, avg_ip=-0.003585, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=231, two_prices=205, avg_raw=-0.00522, avg_ip=0.001984, beat_rate=0.068293
- `WATCHLIST_UNKNOWN_CTX`: n=12, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.111111

# Edge Factory — CLV report (2026-08-10 to 2026-09-09)

## Overall

- total unique picks: 864
- picks with at least two prices: 752
- average raw odds delta: 0.003793
- average implied-probability delta: -0.000288
- beat-later-price rate: 0.160904
- beat-later-price sample: 752
- unmatched picks: 54
- picks with fewer than two snapshots: 59

## By rule

- `2way+bc-confirms avg_p>=60`: n=14, two_prices=14, avg_raw=-0.019286, avg_ip=0.008824, beat_rate=0.357143
- `2way-unanimous avg_p>=70`: n=169, two_prices=137, avg_raw=0.000365, avg_ip=-0.000114, beat_rate=0.160584
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=487, two_prices=450, avg_raw=-0.000422, avg_ip=0.000698, beat_rate=0.188889
- `ml-meta avg_p>=60`: n=64, two_prices=49, avg_raw=0.065184, avg_ip=-0.012444, beat_rate=0.020408
- `ml-meta avg_p>=65`: n=22, two_prices=13, avg_raw=-0.010154, avg_ip=0.005067, beat_rate=0.230769
- `ml-meta avg_p>=70`: n=28, two_prices=17, avg_raw=0.013529, avg_ip=-0.006653, beat_rate=0.058824
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=114, two_prices=105, avg_raw=0.005714, avg_ip=-0.000605, beat_rate=0.171429
- `CERTIFIED_CLEAN`: n=72, two_prices=63, avg_raw=0.04473, avg_ip=-0.007025, beat_rate=0.238095
- `SKIPPED_VETO`: n=431, two_prices=399, avg_raw=-0.000792, avg_ip=0.000362, beat_rate=0.190476
- `WATCHLIST_NO_ODDS`: n=45, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=26, two_prices=18, avg_raw=-0.007778, avg_ip=0.003956, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=159, two_prices=151, avg_raw=-0.001589, avg_ip=0.001028, beat_rate=0.066225
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.008125, avg_ip=-0.005084, beat_rate=0.0

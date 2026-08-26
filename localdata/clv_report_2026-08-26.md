# Edge Factory — CLV report (2026-07-27 to 2026-08-26)

## Overall

- total unique picks: 470
- picks with at least two prices: 425
- average raw odds delta: 0.002096
- average implied-probability delta: -0.000736
- beat-later-price rate: 0.136471
- beat-later-price sample: 425
- unmatched picks: 23
- picks with fewer than two snapshots: 21

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=135, two_prices=122, avg_raw=0.001016, avg_ip=-0.000567, beat_rate=0.139344
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=44, two_prices=42, avg_raw=0.005119, avg_ip=-0.002892, beat_rate=0.02381
- `ml-meta avg_p>=55`: n=180, two_prices=167, avg_raw=0.003234, avg_ip=-0.000836, beat_rate=0.173653
- `ml-meta avg_p>=60`: n=35, two_prices=31, avg_raw=0.008516, avg_ip=-0.003949, beat_rate=0.0
- `ml-meta avg_p>=65`: n=12, two_prices=6, avg_raw=-0.002, avg_ip=0.003055, beat_rate=0.333333
- `ml-meta avg_p>=70`: n=12, two_prices=10, avg_raw=0.015, avg_ip=-0.006102, beat_rate=0.1
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25
- `ml-meta avg_p>=80`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=80, two_prices=73, avg_raw=0.005616, avg_ip=-0.00108, beat_rate=0.109589
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=257, two_prices=246, avg_raw=0.001841, avg_ip=-0.001042, beat_rate=0.154472
- `WATCHLIST_NO_ODDS`: n=22, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=57, two_prices=54, avg_raw=-0.001111, avg_ip=0.000943, beat_rate=0.074074
- `WATCHLIST_UNKNOWN_CTX`: n=26, two_prices=25, avg_raw=0.006, avg_ip=-0.00374, beat_rate=0.0

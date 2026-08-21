# Edge Factory — CLV report (2026-07-22 to 2026-08-21)

## Overall

- total unique picks: 341
- picks with at least two prices: 306
- average raw odds delta: 0.003598
- average implied-probability delta: -0.001678
- beat-later-price rate: 0.143791
- beat-later-price sample: 306
- unmatched picks: 19
- picks with fewer than two snapshots: 16

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=111, two_prices=101, avg_raw=0.002218, avg_ip=-0.001567, beat_rate=0.128713
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=46, two_prices=44, avg_raw=0.005114, avg_ip=-0.002902, beat_rate=0.022727
- `ml-meta avg_p>=55`: n=114, two_prices=103, avg_raw=0.00767, avg_ip=-0.003027, beat_rate=0.194175
- `ml-meta avg_p>=60`: n=8, two_prices=7, avg_raw=0.016286, avg_ip=-0.00814, beat_rate=0.0
- `ml-meta avg_p>=65`: n=7, two_prices=3, avg_raw=-0.004, avg_ip=0.006111, beat_rate=0.666667
- `ml-meta avg_p>=70`: n=6, two_prices=5, avg_raw=0.03, avg_ip=-0.011901, beat_rate=0.0
- `ml-meta avg_p>=75`: n=3, two_prices=2, avg_raw=-0.015, avg_ip=0.010506, beat_rate=0.5

## By bucket

- `CAUTION`: n=66, two_prices=60, avg_raw=0.005667, avg_ip=-0.001333, beat_rate=0.116667
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=174, two_prices=167, avg_raw=0.00421, avg_ip=-0.002578, beat_rate=0.155689
- `WATCHLIST_NO_ODDS`: n=18, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=33, two_prices=31, avg_raw=-0.001935, avg_ip=0.001642, beat_rate=0.129032
- `WATCHLIST_UNKNOWN_CTX`: n=22, two_prices=21, avg_raw=0.006667, avg_ip=-0.004135, beat_rate=0.0

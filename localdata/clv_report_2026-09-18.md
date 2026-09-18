# Edge Factory — CLV report (2026-08-19 to 2026-09-18)

## Overall

- total unique picks: 1028
- picks with at least two prices: 870
- average raw odds delta: 0.001471
- average implied-probability delta: 0.000534
- beat-later-price rate: 0.148276
- beat-later-price sample: 870
- unmatched picks: 70
- picks with fewer than two snapshots: 90

## By rule

- `2way-unanimous avg_p>=70`: n=205, two_prices=155, avg_raw=-0.001484, avg_ip=0.001127, beat_rate=0.180645
- `ml-meta avg_p>=55`: n=588, two_prices=531, avg_raw=-0.003107, avg_ip=0.001695, beat_rate=0.167608
- `ml-meta avg_p>=60`: n=104, two_prices=84, avg_raw=0.035952, avg_ip=-0.006287, beat_rate=0.071429
- `ml-meta avg_p>=65`: n=31, two_prices=19, avg_raw=-0.003158, avg_ip=0.000564, beat_rate=0.052632
- `ml-meta avg_p>=70`: n=32, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=7, two_prices=6, avg_raw=0.001667, avg_ip=-0.001556, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=105, two_prices=95, avg_raw=0.004737, avg_ip=-0.000659, beat_rate=0.157895
- `CERTIFIED_CLEAN`: n=94, two_prices=78, avg_raw=0.034487, avg_ip=-0.004734, beat_rate=0.192308
- `SKIPPED_VETO`: n=523, two_prices=477, avg_raw=-0.002558, avg_ip=0.001309, beat_rate=0.176101
- `WATCHLIST_NO_ODDS`: n=58, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.004444, avg_ip=0.002071, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=207, two_prices=190, avg_raw=-0.003, avg_ip=0.001271, beat_rate=0.063158
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.083333

# Edge Factory — CLV report (2026-08-20 to 2026-09-19)

## Overall

- total unique picks: 1087
- picks with at least two prices: 920
- average raw odds delta: 0.001348
- average implied-probability delta: 0.00055
- beat-later-price rate: 0.143478
- beat-later-price sample: 920
- unmatched picks: 74
- picks with fewer than two snapshots: 93

## By rule

- `2way-unanimous avg_p>=70`: n=219, two_prices=164, avg_raw=-0.001463, avg_ip=0.001069, beat_rate=0.176829
- `ml-meta avg_p>=55`: n=618, two_prices=563, avg_raw=-0.002948, avg_ip=0.001652, beat_rate=0.161634
- `ml-meta avg_p>=60`: n=117, two_prices=91, avg_raw=0.032967, avg_ip=-0.005692, beat_rate=0.065934
- `ml-meta avg_p>=65`: n=32, two_prices=20, avg_raw=-0.003, avg_ip=0.000535, beat_rate=0.05
- `ml-meta avg_p>=70`: n=32, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=104, two_prices=95, avg_raw=0.004526, avg_ip=-0.000553, beat_rate=0.157895
- `CERTIFIED_CLEAN`: n=106, two_prices=91, avg_raw=0.028791, avg_ip=-0.003795, beat_rate=0.175824
- `SKIPPED_VETO`: n=554, two_prices=502, avg_raw=-0.002331, avg_ip=0.001258, beat_rate=0.171315
- `WATCHLIST_NO_ODDS`: n=64, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.004444, avg_ip=0.002071, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=218, two_prices=200, avg_raw=-0.00285, avg_ip=0.001207, beat_rate=0.06
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.083333

# Edge Factory — CLV report (2026-08-20 to 2026-09-19)

## Overall

- total unique picks: 1090
- picks with at least two prices: 921
- average raw odds delta: 0.00126
- average implied-probability delta: 0.00059
- beat-later-price rate: 0.145494
- beat-later-price sample: 921
- unmatched picks: 74
- picks with fewer than two snapshots: 95

## By rule

- `2way-unanimous avg_p>=70`: n=219, two_prices=164, avg_raw=-0.001524, avg_ip=0.001123, beat_rate=0.176829
- `ml-meta avg_p>=55`: n=621, two_prices=564, avg_raw=-0.003067, avg_ip=0.0017, beat_rate=0.164894
- `ml-meta avg_p>=60`: n=117, two_prices=91, avg_raw=0.032967, avg_ip=-0.005692, beat_rate=0.065934
- `ml-meta avg_p>=65`: n=32, two_prices=20, avg_raw=-0.003, avg_ip=0.000535, beat_rate=0.05
- `ml-meta avg_p>=70`: n=32, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=104, two_prices=95, avg_raw=0.004526, avg_ip=-0.000553, beat_rate=0.157895
- `CERTIFIED_CLEAN`: n=106, two_prices=91, avg_raw=0.028571, avg_ip=-0.003702, beat_rate=0.186813
- `SKIPPED_VETO`: n=557, two_prices=504, avg_raw=-0.00244, avg_ip=0.00131, beat_rate=0.172619
- `WATCHLIST_NO_ODDS`: n=64, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.004444, avg_ip=0.002071, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=218, two_prices=199, avg_raw=-0.002864, avg_ip=0.001213, beat_rate=0.060302
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.083333

# Edge Factory — CLV report (2026-09-10 to 2026-10-10)

## Overall

- total unique picks: 1001
- picks with at least two prices: 773
- average raw odds delta: -0.002561
- average implied-probability delta: 0.001176
- beat-later-price rate: 0.10608
- beat-later-price sample: 773
- unmatched picks: 117
- picks with fewer than two snapshots: 113

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=122, two_prices=78, avg_raw=-0.000641, avg_ip=0.000539, beat_rate=0.166667
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=467, two_prices=406, avg_raw=-0.004409, avg_ip=0.002029, beat_rate=0.123153
- `ml-meta avg_p>=60`: n=128, two_prices=98, avg_raw=-0.00051, avg_ip=0.000159, beat_rate=0.05102
- `ml-meta avg_p>=65`: n=45, two_prices=32, avg_raw=0.0, avg_ip=0.000156, beat_rate=0.0625
- `ml-meta avg_p>=70`: n=10, two_prices=6, avg_raw=-0.006667, avg_ip=0.005413, beat_rate=0.166667
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=16, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0

## By bucket

- `CAUTION`: n=76, two_prices=67, avg_raw=-0.001791, avg_ip=0.001241, beat_rate=0.164179
- `CERTIFIED_CLEAN`: n=125, two_prices=117, avg_raw=-0.003162, avg_ip=0.001519, beat_rate=0.119658
- `SKIPPED_VETO`: n=505, two_prices=410, avg_raw=-0.001634, avg_ip=0.000891, beat_rate=0.112195
- `WATCHLIST_NO_ODDS`: n=88, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=9, two_prices=4, avg_raw=0.0275, avg_ip=-0.011388, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=188, two_prices=164, avg_raw=-0.00561, avg_ip=0.00196, beat_rate=0.060976
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

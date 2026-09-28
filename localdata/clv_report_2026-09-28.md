# Edge Factory — CLV report (2026-08-29 to 2026-09-28)

## Overall

- total unique picks: 1196
- picks with at least two prices: 976
- average raw odds delta: 9.2e-05
- average implied-probability delta: 0.000828
- beat-later-price rate: 0.139344
- beat-later-price sample: 976
- unmatched picks: 91
- picks with fewer than two snapshots: 128

## By rule

- `2way-unanimous avg_p>=60`: n=119, two_prices=83, avg_raw=-0.002651, avg_ip=0.000489, beat_rate=0.060241
- `2way-unanimous avg_p>=70`: n=192, two_prices=134, avg_raw=-0.001642, avg_ip=0.000994, beat_rate=0.19403
- `ml-meta avg_p>=55`: n=639, two_prices=576, avg_raw=-0.003993, avg_ip=0.001922, beat_rate=0.161458
- `ml-meta avg_p>=60`: n=117, two_prices=86, avg_raw=0.03314, avg_ip=-0.005353, beat_rate=0.069767
- `ml-meta avg_p>=65`: n=38, two_prices=25, avg_raw=-0.0028, avg_ip=0.000768, beat_rate=0.08
- `ml-meta avg_p>=70`: n=25, two_prices=12, avg_raw=0.003333, avg_ip=-0.001634, beat_rate=0.083333
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=112, two_prices=100, avg_raw=-0.0018, avg_ip=0.001513, beat_rate=0.19
- `CERTIFIED_CLEAN`: n=144, two_prices=126, avg_raw=0.01873, avg_ip=-0.00212, beat_rate=0.174603
- `SKIPPED_VETO`: n=580, two_prices=500, avg_raw=-0.0028, avg_ip=0.001319, beat_rate=0.158
- `WATCHLIST_NO_ODDS`: n=74, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=248, two_prices=221, avg_raw=-0.003167, avg_ip=0.001223, beat_rate=0.063348
- `WATCHLIST_UNKNOWN_CTX`: n=11, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.111111

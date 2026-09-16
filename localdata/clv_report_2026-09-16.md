# Edge Factory — CLV report (2026-08-17 to 2026-09-16)

## Overall

- total unique picks: 989
- picks with at least two prices: 846
- average raw odds delta: 0.001903
- average implied-probability delta: 0.000365
- beat-later-price rate: 0.150118
- beat-later-price sample: 846
- unmatched picks: 65
- picks with fewer than two snapshots: 79

## By rule

- `2way-unanimous avg_p>=70`: n=192, two_prices=149, avg_raw=-0.00047, avg_ip=0.000546, beat_rate=0.161074
- `ml-meta avg_p>=55`: n=570, two_prices=517, avg_raw=-0.002979, avg_ip=0.001666, beat_rate=0.174081
- `ml-meta avg_p>=60`: n=100, two_prices=82, avg_raw=0.037927, avg_ip=-0.006989, beat_rate=0.073171
- `ml-meta avg_p>=65`: n=27, two_prices=16, avg_raw=-0.00375, avg_ip=0.000669, beat_rate=0.0625
- `ml-meta avg_p>=70`: n=31, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=7, two_prices=6, avg_raw=0.001667, avg_ip=-0.001556, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=110, two_prices=98, avg_raw=0.006429, avg_ip=-0.00151, beat_rate=0.142857
- `CERTIFIED_CLEAN`: n=86, two_prices=72, avg_raw=0.039028, avg_ip=-0.005851, beat_rate=0.194444
- `SKIPPED_VETO`: n=503, two_prices=465, avg_raw=-0.002774, avg_ip=0.001395, beat_rate=0.184946
- `WATCHLIST_NO_ODDS`: n=53, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.004444, avg_ip=0.002071, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=196, two_prices=181, avg_raw=-0.002597, avg_ip=0.001096, beat_rate=0.055249
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.083333

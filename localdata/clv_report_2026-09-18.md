# Edge Factory — CLV report (2026-08-19 to 2026-09-18)

## Overall

- total unique picks: 1040
- picks with at least two prices: 883
- average raw odds delta: 0.001574
- average implied-probability delta: 0.000509
- beat-later-price rate: 0.146093
- beat-later-price sample: 883
- unmatched picks: 70
- picks with fewer than two snapshots: 87

## By rule

- `2way-unanimous avg_p>=70`: n=209, two_prices=158, avg_raw=-0.001392, avg_ip=0.001049, beat_rate=0.170886
- `ml-meta avg_p>=55`: n=592, two_prices=539, avg_raw=-0.002876, avg_ip=0.001659, beat_rate=0.166976
- `ml-meta avg_p>=60`: n=107, two_prices=86, avg_raw=0.035116, avg_ip=-0.00614, beat_rate=0.069767
- `ml-meta avg_p>=65`: n=32, two_prices=19, avg_raw=-0.003158, avg_ip=0.000564, beat_rate=0.052632
- `ml-meta avg_p>=70`: n=32, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=7, two_prices=6, avg_raw=0.001667, avg_ip=-0.001556, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=106, two_prices=96, avg_raw=0.004687, avg_ip=-0.000653, beat_rate=0.15625
- `CERTIFIED_CLEAN`: n=96, two_prices=81, avg_raw=0.034074, avg_ip=-0.004859, beat_rate=0.185185
- `SKIPPED_VETO`: n=530, two_prices=484, avg_raw=-0.002438, avg_ip=0.001309, beat_rate=0.173554
- `WATCHLIST_NO_ODDS`: n=58, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.004444, avg_ip=0.002071, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=209, two_prices=192, avg_raw=-0.002969, avg_ip=0.001257, beat_rate=0.0625
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.083333

# Edge Factory — CLV report (2026-08-17 to 2026-09-16)

## Overall

- total unique picks: 982
- picks with at least two prices: 837
- average raw odds delta: 0.002079
- average implied-probability delta: 0.000305
- beat-later-price rate: 0.145759
- beat-later-price sample: 837
- unmatched picks: 65
- picks with fewer than two snapshots: 81

## By rule

- `2way-unanimous avg_p>=70`: n=192, two_prices=148, avg_raw=-0.000676, avg_ip=0.000762, beat_rate=0.155405
- `ml-meta avg_p>=55`: n=564, two_prices=510, avg_raw=-0.002804, avg_ip=0.001551, beat_rate=0.170588
- `ml-meta avg_p>=60`: n=99, two_prices=81, avg_raw=0.039012, avg_ip=-0.007254, beat_rate=0.061728
- `ml-meta avg_p>=65`: n=27, two_prices=16, avg_raw=-0.00375, avg_ip=0.000669, beat_rate=0.0625
- `ml-meta avg_p>=70`: n=31, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=7, two_prices=6, avg_raw=0.001667, avg_ip=-0.001556, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=109, two_prices=96, avg_raw=0.006667, avg_ip=-0.0016, beat_rate=0.135417
- `CERTIFIED_CLEAN`: n=83, two_prices=69, avg_raw=0.043623, avg_ip=-0.007529, beat_rate=0.188406
- `SKIPPED_VETO`: n=501, two_prices=461, avg_raw=-0.002972, avg_ip=0.001516, beat_rate=0.180043
- `WATCHLIST_NO_ODDS`: n=53, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.004444, avg_ip=0.002071, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=196, two_prices=181, avg_raw=-0.002597, avg_ip=0.001096, beat_rate=0.055249
- `WATCHLIST_UNKNOWN_CTX`: n=13, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.083333

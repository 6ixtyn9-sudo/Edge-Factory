# Edge Factory — CLV report (2026-09-05 to 2026-10-05)

## Overall

- total unique picks: 1115
- picks with at least two prices: 887
- average raw odds delta: -0.002965
- average implied-probability delta: 0.001406
- beat-later-price rate: 0.124014
- beat-later-price sample: 887
- unmatched picks: 111
- picks with fewer than two snapshots: 117

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=135, two_prices=89, avg_raw=-0.00191, avg_ip=0.001274, beat_rate=0.202247
- `ml-meta avg_p>=55`: n=555, two_prices=493, avg_raw=-0.004584, avg_ip=0.002166, beat_rate=0.141988
- `ml-meta avg_p>=60`: n=111, two_prices=86, avg_raw=-0.001047, avg_ip=0.000436, beat_rate=0.069767
- `ml-meta avg_p>=65`: n=41, two_prices=29, avg_raw=0.0, avg_ip=0.000173, beat_rate=0.068966
- `ml-meta avg_p>=70`: n=21, two_prices=9, avg_raw=-0.002222, avg_ip=0.002695, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=11, two_prices=9, avg_raw=0.006667, avg_ip=-0.006011, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=32, two_prices=30, avg_raw=-0.001667, avg_ip=0.000602, beat_rate=0.066667

## By bucket

- `CAUTION`: n=92, two_prices=83, avg_raw=-0.003012, avg_ip=0.001897, beat_rate=0.168675
- `CERTIFIED_CLEAN`: n=136, two_prices=122, avg_raw=-0.002377, avg_ip=0.001098, beat_rate=0.139344
- `SKIPPED_VETO`: n=542, two_prices=456, avg_raw=-0.002522, avg_ip=0.001321, beat_rate=0.140351
- `WATCHLIST_NO_ODDS`: n=86, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=23, two_prices=15, avg_raw=0.008667, avg_ip=-0.003585, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=224, two_prices=199, avg_raw=-0.005377, avg_ip=0.002044, beat_rate=0.070352
- `WATCHLIST_UNKNOWN_CTX`: n=12, two_prices=10, avg_raw=0.0, avg_ip=0.0, beat_rate=0.1

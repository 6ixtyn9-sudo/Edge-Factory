# Edge Factory — CLV report (2026-08-21 to 2026-09-20)

## Overall

- total unique picks: 1169
- picks with at least two prices: 956
- average raw odds delta: 0.001402
- average implied-probability delta: 0.000491
- beat-later-price rate: 0.140167
- beat-later-price sample: 956
- unmatched picks: 75
- picks with fewer than two snapshots: 139

## By rule

- `2way-unanimous avg_p>=70`: n=233, two_prices=170, avg_raw=-0.001471, avg_ip=0.001083, beat_rate=0.170588
- `ml-meta avg_p>=55`: n=666, two_prices=579, avg_raw=-0.002677, avg_ip=0.001529, beat_rate=0.160622
- `ml-meta avg_p>=60`: n=136, two_prices=105, avg_raw=0.028571, avg_ip=-0.004933, beat_rate=0.057143
- `ml-meta avg_p>=65`: n=33, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=33, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=108, two_prices=95, avg_raw=0.003789, avg_ip=-0.000384, beat_rate=0.168421
- `CERTIFIED_CLEAN`: n=116, two_prices=97, avg_raw=0.026804, avg_ip=-0.003473, beat_rate=0.175258
- `SKIPPED_VETO`: n=596, two_prices=520, avg_raw=-0.001885, avg_ip=0.001098, beat_rate=0.165385
- `WATCHLIST_NO_ODDS`: n=65, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=28, two_prices=19, avg_raw=-0.004211, avg_ip=0.001962, beat_rate=0.105263
- `WATCHLIST_UNCORROBORATED_PRICE`: n=242, two_prices=211, avg_raw=-0.002701, avg_ip=0.001144, beat_rate=0.056872
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.083333

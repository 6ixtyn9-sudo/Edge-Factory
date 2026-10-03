# Edge Factory — CLV report (2026-09-03 to 2026-10-03)

## Overall

- total unique picks: 1121
- picks with at least two prices: 901
- average raw odds delta: -0.002697
- average implied-probability delta: 0.001233
- beat-later-price rate: 0.132075
- beat-later-price sample: 901
- unmatched picks: 104
- picks with fewer than two snapshots: 116

## By rule

- `2way-unanimous avg_p>=60`: n=186, two_prices=130, avg_raw=-0.000769, avg_ip=0.000271, beat_rate=0.084615
- `2way-unanimous avg_p>=70`: n=146, two_prices=97, avg_raw=-0.001546, avg_ip=0.001093, beat_rate=0.206186
- `ml-meta avg_p>=55`: n=567, two_prices=508, avg_raw=-0.004173, avg_ip=0.00188, beat_rate=0.149606
- `ml-meta avg_p>=60`: n=110, two_prices=85, avg_raw=-0.001059, avg_ip=0.000441, beat_rate=0.070588
- `ml-meta avg_p>=65`: n=40, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=21, two_prices=9, avg_raw=-0.002222, avg_ip=0.002695, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=11, two_prices=9, avg_raw=0.006667, avg_ip=-0.006011, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=38, two_prices=35, avg_raw=-0.000286, avg_ip=6.8e-05, beat_rate=0.085714

## By bucket

- `CAUTION`: n=98, two_prices=89, avg_raw=-0.002472, avg_ip=0.001926, beat_rate=0.179775
- `CERTIFIED_CLEAN`: n=131, two_prices=118, avg_raw=-0.003136, avg_ip=0.00149, beat_rate=0.161017
- `SKIPPED_VETO`: n=551, two_prices=467, avg_raw=-0.001927, avg_ip=0.00088, beat_rate=0.147752
- `WATCHLIST_NO_ODDS`: n=80, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=22, two_prices=14, avg_raw=0.009286, avg_ip=-0.003841, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=229, two_prices=203, avg_raw=-0.005271, avg_ip=0.002004, beat_rate=0.068966
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

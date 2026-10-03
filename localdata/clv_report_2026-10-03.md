# Edge Factory — CLV report (2026-09-03 to 2026-10-03)

## Overall

- total unique picks: 1119
- picks with at least two prices: 899
- average raw odds delta: -0.002214
- average implied-probability delta: 0.001022
- beat-later-price rate: 0.125695
- beat-later-price sample: 899
- unmatched picks: 104
- picks with fewer than two snapshots: 116

## By rule

- `2way-unanimous avg_p>=60`: n=185, two_prices=129, avg_raw=-0.0, avg_ip=-5.3e-05, beat_rate=0.069767
- `2way-unanimous avg_p>=70`: n=146, two_prices=97, avg_raw=-0.001546, avg_ip=0.001093, beat_rate=0.206186
- `ml-meta avg_p>=55`: n=566, two_prices=507, avg_raw=-0.003471, avg_ip=0.001552, beat_rate=0.142012
- `ml-meta avg_p>=60`: n=110, two_prices=85, avg_raw=-0.001059, avg_ip=0.000441, beat_rate=0.070588
- `ml-meta avg_p>=65`: n=40, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=21, two_prices=9, avg_raw=-0.002222, avg_ip=0.002695, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=11, two_prices=9, avg_raw=0.004444, avg_ip=-0.004033, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=38, two_prices=35, avg_raw=-0.000286, avg_ip=6.8e-05, beat_rate=0.085714

## By bucket

- `CAUTION`: n=98, two_prices=89, avg_raw=-0.002472, avg_ip=0.001926, beat_rate=0.179775
- `CERTIFIED_CLEAN`: n=128, two_prices=115, avg_raw=-0.002696, avg_ip=0.001281, beat_rate=0.156522
- `SKIPPED_VETO`: n=553, two_prices=469, avg_raw=-0.001791, avg_ip=0.000802, beat_rate=0.142857
- `WATCHLIST_NO_ODDS`: n=80, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=22, two_prices=14, avg_raw=0.009286, avg_ip=-0.003841, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=228, two_prices=202, avg_raw=-0.003713, avg_ip=0.001376, beat_rate=0.054455
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

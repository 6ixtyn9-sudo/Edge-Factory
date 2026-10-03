# Edge Factory — CLV report (2026-09-03 to 2026-10-03)

## Overall

- total unique picks: 1117
- picks with at least two prices: 889
- average raw odds delta: -0.002238
- average implied-probability delta: 0.001034
- beat-later-price rate: 0.127109
- beat-later-price sample: 889
- unmatched picks: 104
- picks with fewer than two snapshots: 134

## By rule

- `2way-unanimous avg_p>=60`: n=184, two_prices=125, avg_raw=-0.0, avg_ip=-5.5e-05, beat_rate=0.072
- `2way-unanimous avg_p>=70`: n=146, two_prices=97, avg_raw=-0.001546, avg_ip=0.001093, beat_rate=0.206186
- `ml-meta avg_p>=55`: n=565, two_prices=502, avg_raw=-0.003506, avg_ip=0.001567, beat_rate=0.143426
- `ml-meta avg_p>=60`: n=110, two_prices=85, avg_raw=-0.001059, avg_ip=0.000441, beat_rate=0.070588
- `ml-meta avg_p>=65`: n=40, two_prices=27, avg_raw=0.0, avg_ip=0.000185, beat_rate=0.074074
- `ml-meta avg_p>=70`: n=21, two_prices=9, avg_raw=-0.002222, avg_ip=0.002695, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=11, two_prices=9, avg_raw=0.004444, avg_ip=-0.004033, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=38, two_prices=35, avg_raw=-0.000286, avg_ip=6.8e-05, beat_rate=0.085714

## By bucket

- `CAUTION`: n=98, two_prices=88, avg_raw=-0.0025, avg_ip=0.001948, beat_rate=0.181818
- `CERTIFIED_CLEAN`: n=127, two_prices=114, avg_raw=-0.002719, avg_ip=0.001292, beat_rate=0.157895
- `SKIPPED_VETO`: n=550, two_prices=463, avg_raw=-0.001814, avg_ip=0.000812, beat_rate=0.144708
- `WATCHLIST_NO_ODDS`: n=80, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=22, two_prices=14, avg_raw=0.009286, avg_ip=-0.003841, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=230, two_prices=200, avg_raw=-0.00375, avg_ip=0.00139, beat_rate=0.055
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

# Edge Factory — CLV report (2026-08-22 to 2026-09-21)

## Overall

- total unique picks: 1148
- picks with at least two prices: 968
- average raw odds delta: 0.000919
- average implied-probability delta: 0.000637
- beat-later-price rate: 0.139463
- beat-later-price sample: 968
- unmatched picks: 73
- picks with fewer than two snapshots: 107

## By rule

- `2way-unanimous avg_p>=70`: n=228, two_prices=167, avg_raw=-0.001557, avg_ip=0.001125, beat_rate=0.173653
- `ml-meta avg_p>=55`: n=650, two_prices=595, avg_raw=-0.003092, avg_ip=0.001629, beat_rate=0.157983
- `ml-meta avg_p>=60`: n=138, two_prices=107, avg_raw=0.028037, avg_ip=-0.004841, beat_rate=0.056075
- `ml-meta avg_p>=65`: n=34, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=31, two_prices=17, avg_raw=0.002353, avg_ip=-0.001242, beat_rate=0.117647
- `ml-meta avg_p>=75`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=104, two_prices=93, avg_raw=0.004086, avg_ip=-0.000826, beat_rate=0.172043
- `CERTIFIED_CLEAN`: n=118, two_prices=103, avg_raw=0.023592, avg_ip=-0.00284, beat_rate=0.194175
- `SKIPPED_VETO`: n=583, two_prices=525, avg_raw=-0.002381, avg_ip=0.001412, beat_rate=0.16
- `WATCHLIST_NO_ODDS`: n=63, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=241, two_prices=217, avg_raw=-0.00318, avg_ip=0.001186, beat_rate=0.059908
- `WATCHLIST_UNKNOWN_CTX`: n=12, two_prices=10, avg_raw=0.001, avg_ip=-0.000666, beat_rate=0.1

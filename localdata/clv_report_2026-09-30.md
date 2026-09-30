# Edge Factory — CLV report (2026-08-31 to 2026-09-30)

## Overall

- total unique picks: 1117
- picks with at least two prices: 916
- average raw odds delta: -0.002205
- average implied-probability delta: 0.001096
- beat-later-price rate: 0.135371
- beat-later-price sample: 916
- unmatched picks: 83
- picks with fewer than two snapshots: 118

## By rule

- `2way-unanimous avg_p>=60`: n=135, two_prices=99, avg_raw=-0.00101, avg_ip=0.000416, beat_rate=0.080808
- `2way-unanimous avg_p>=70`: n=163, two_prices=111, avg_raw=-0.002162, avg_ip=0.00137, beat_rate=0.216216
- `ml-meta avg_p>=55`: n=582, two_prices=528, avg_raw=-0.002879, avg_ip=0.001414, beat_rate=0.151515
- `ml-meta avg_p>=60`: n=108, two_prices=81, avg_raw=-0.000988, avg_ip=0.000401, beat_rate=0.074074
- `ml-meta avg_p>=65`: n=39, two_prices=26, avg_raw=-0.002692, avg_ip=0.000739, beat_rate=0.076923
- `ml-meta avg_p>=70`: n=24, two_prices=11, avg_raw=-0.001818, avg_ip=0.002205, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=103, two_prices=92, avg_raw=0.002174, avg_ip=0.000319, beat_rate=0.173913
- `CERTIFIED_CLEAN`: n=131, two_prices=117, avg_raw=-0.002564, avg_ip=0.001215, beat_rate=0.162393
- `SKIPPED_VETO`: n=552, two_prices=477, avg_raw=-0.002662, avg_ip=0.001239, beat_rate=0.157233
- `WATCHLIST_NO_ODDS`: n=66, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=26, two_prices=17, avg_raw=0.000588, avg_ip=-0.000367, beat_rate=0.058824
- `WATCHLIST_UNCORROBORATED_PRICE`: n=229, two_prices=203, avg_raw=-0.003251, avg_ip=0.001221, beat_rate=0.059113
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

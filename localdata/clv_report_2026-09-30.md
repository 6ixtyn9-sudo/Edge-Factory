# Edge Factory — CLV report (2026-08-31 to 2026-09-30)

## Overall

- total unique picks: 1115
- picks with at least two prices: 913
- average raw odds delta: -0.002245
- average implied-probability delta: 0.001113
- beat-later-price rate: 0.135816
- beat-later-price sample: 913
- unmatched picks: 82
- picks with fewer than two snapshots: 119

## By rule

- `2way-unanimous avg_p>=60`: n=135, two_prices=98, avg_raw=-0.00102, avg_ip=0.000421, beat_rate=0.081633
- `2way-unanimous avg_p>=70`: n=163, two_prices=111, avg_raw=-0.002162, avg_ip=0.00137, beat_rate=0.216216
- `ml-meta avg_p>=55`: n=581, two_prices=526, avg_raw=-0.002947, avg_ip=0.001443, beat_rate=0.152091
- `ml-meta avg_p>=60`: n=108, two_prices=81, avg_raw=-0.000988, avg_ip=0.000401, beat_rate=0.074074
- `ml-meta avg_p>=65`: n=38, two_prices=26, avg_raw=-0.002692, avg_ip=0.000739, beat_rate=0.076923
- `ml-meta avg_p>=70`: n=24, two_prices=11, avg_raw=-0.001818, avg_ip=0.002205, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=103, two_prices=92, avg_raw=0.002174, avg_ip=0.000319, beat_rate=0.173913
- `CERTIFIED_CLEAN`: n=131, two_prices=116, avg_raw=-0.002586, avg_ip=0.001225, beat_rate=0.163793
- `SKIPPED_VETO`: n=551, two_prices=476, avg_raw=-0.002731, avg_ip=0.001268, beat_rate=0.157563
- `WATCHLIST_NO_ODDS`: n=66, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=26, two_prices=17, avg_raw=0.000588, avg_ip=-0.000367, beat_rate=0.058824
- `WATCHLIST_UNCORROBORATED_PRICE`: n=228, two_prices=202, avg_raw=-0.003267, avg_ip=0.001227, beat_rate=0.059406
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

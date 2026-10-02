# Edge Factory — CLV report (2026-09-02 to 2026-10-02)

## Overall

- total unique picks: 1073
- picks with at least two prices: 877
- average raw odds delta: -0.002611
- average implied-probability delta: 0.001198
- beat-later-price rate: 0.13455
- beat-later-price sample: 877
- unmatched picks: 78
- picks with fewer than two snapshots: 115

## By rule

- `2way-unanimous avg_p>=60`: n=147, two_prices=109, avg_raw=-0.001651, avg_ip=0.000709, beat_rate=0.082569
- `2way-unanimous avg_p>=70`: n=148, two_prices=98, avg_raw=-0.001735, avg_ip=0.00121, beat_rate=0.214286
- `ml-meta avg_p>=55`: n=555, two_prices=502, avg_raw=-0.003506, avg_ip=0.001563, beat_rate=0.149402
- `ml-meta avg_p>=60`: n=108, two_prices=82, avg_raw=-0.000976, avg_ip=0.000396, beat_rate=0.073171
- `ml-meta avg_p>=65`: n=40, two_prices=27, avg_raw=-0.004444, avg_ip=0.001946, beat_rate=0.111111
- `ml-meta avg_p>=70`: n=23, two_prices=11, avg_raw=-0.001818, avg_ip=0.002205, beat_rate=0.090909
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=9, two_prices=8, avg_raw=0.005, avg_ip=-0.004537, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=42, two_prices=39, avg_raw=0.0, avg_ip=-7.1e-05, beat_rate=0.076923

## By bucket

- `CAUTION`: n=98, two_prices=88, avg_raw=-0.002386, avg_ip=0.001891, beat_rate=0.181818
- `CERTIFIED_CLEAN`: n=130, two_prices=116, avg_raw=-0.002845, avg_ip=0.001315, beat_rate=0.163793
- `SKIPPED_VETO`: n=532, two_prices=454, avg_raw=-0.002203, avg_ip=0.000997, beat_rate=0.151982
- `WATCHLIST_NO_ODDS`: n=61, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=25, two_prices=17, avg_raw=0.000588, avg_ip=-0.000367, beat_rate=0.058824
- `WATCHLIST_UNCORROBORATED_PRICE`: n=217, two_prices=192, avg_raw=-0.003958, avg_ip=0.001487, beat_rate=0.0625
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

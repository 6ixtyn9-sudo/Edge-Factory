# Edge Factory — CLV report (2026-07-23 to 2026-08-22)

## Overall

- total unique picks: 381
- picks with at least two prices: 345
- average raw odds delta: 0.002814
- average implied-probability delta: -0.001205
- beat-later-price rate: 0.13913
- beat-later-price sample: 345
- unmatched picks: 22
- picks with fewer than two snapshots: 13

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=119, two_prices=108, avg_raw=0.001889, avg_ip=-0.001328, beat_rate=0.12963
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=46, two_prices=44, avg_raw=0.005114, avg_ip=-0.002902, beat_rate=0.022727
- `ml-meta avg_p>=55`: n=141, two_prices=129, avg_raw=0.005271, avg_ip=-0.001775, beat_rate=0.178295
- `ml-meta avg_p>=60`: n=10, two_prices=9, avg_raw=0.012667, avg_ip=-0.006331, beat_rate=0.0
- `ml-meta avg_p>=65`: n=7, two_prices=3, avg_raw=-0.004, avg_ip=0.006111, beat_rate=0.666667
- `ml-meta avg_p>=70`: n=8, two_prices=7, avg_raw=0.021429, avg_ip=-0.008501, beat_rate=0.0
- `ml-meta avg_p>=75`: n=4, two_prices=4, avg_raw=-0.0075, avg_ip=0.005253, beat_rate=0.25

## By bucket

- `CAUTION`: n=67, two_prices=62, avg_raw=0.002581, avg_ip=0.000359, beat_rate=0.129032
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=199, two_prices=193, avg_raw=0.004109, avg_ip=-0.00242, beat_rate=0.145078
- `WATCHLIST_NO_ODDS`: n=21, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=6, two_prices=5, avg_raw=-0.008, avg_ip=0.00638, beat_rate=0.2
- `WATCHLIST_UNCORROBORATED_PRICE`: n=41, two_prices=39, avg_raw=-0.001538, avg_ip=0.001305, beat_rate=0.102564
- `WATCHLIST_UNKNOWN_CTX`: n=25, two_prices=24, avg_raw=0.005833, avg_ip=-0.003618, beat_rate=0.0

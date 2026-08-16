# Edge Factory — CLV report (2026-07-17 to 2026-08-16)

## Overall

- total unique picks: 287
- picks with at least two prices: 260
- average raw odds delta: 0.003081
- average implied-probability delta: -0.001361
- beat-later-price rate: 0.146154
- beat-later-price sample: 260
- unmatched picks: 14
- picks with fewer than two snapshots: 13

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=100, two_prices=92, avg_raw=0.002109, avg_ip=-0.001531, beat_rate=0.141304
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=9, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=71, two_prices=66, avg_raw=0.010606, avg_ip=-0.003576, beat_rate=0.242424
- `ml-meta avg_p>=60`: n=3, two_prices=2, avg_raw=0.002, avg_ip=-0.000962, beat_rate=0.0
- `ml-meta avg_p>=65`: n=5, two_prices=2, avg_raw=0.019, avg_ip=-0.004455, beat_rate=0.5
- `ml-meta avg_p>=70`: n=4, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=49, two_prices=46, avg_raw=0.000652, avg_ip=0.000948, beat_rate=0.152174
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=157, two_prices=148, avg_raw=0.005628, avg_ip=-0.002884, beat_rate=0.135135
- `WATCHLIST_NO_ODDS`: n=13, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=5, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=20, two_prices=20, avg_raw=-0.008, avg_ip=0.003579, beat_rate=0.2
- `WATCHLIST_UNKNOWN_CTX`: n=21, two_prices=20, avg_raw=0.006, avg_ip=-0.003768, beat_rate=0.0

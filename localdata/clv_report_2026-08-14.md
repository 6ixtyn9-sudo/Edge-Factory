# Edge Factory — CLV report (2026-07-15 to 2026-08-14)

## Overall

- total unique picks: 215
- picks with at least two prices: 190
- average raw odds delta: -8.9e-05
- average implied-probability delta: -0.000189
- beat-later-price rate: 0.142105
- beat-later-price sample: 190
- unmatched picks: 6
- picks with fewer than two snapshots: 19

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=89, two_prices=80, avg_raw=0.000175, avg_ip=-0.000245, beat_rate=0.15
- `3way-unanimous avg_p>=65`: n=49, two_prices=47, avg_raw=0.004787, avg_ip=-0.002717, beat_rate=0.021277
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=25, two_prices=20, avg_raw=0.005, avg_ip=-0.002402, beat_rate=0.35
- `ml-meta avg_p>=60`: n=2, two_prices=1, avg_raw=0.004, avg_ip=-0.001924, beat_rate=0.0
- `ml-meta avg_p>=65`: n=3, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=70`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None

## By bucket

- `CAUTION`: n=35, two_prices=27, avg_raw=0.001481, avg_ip=0.001001, beat_rate=0.111111
- `CERTIFIED_CLEAN`: n=15, two_prices=15, avg_raw=-0.022, avg_ip=0.007893, beat_rate=0.4
- `SKIPPED_VETO`: n=125, two_prices=115, avg_raw=0.003504, avg_ip=-0.002033, beat_rate=0.121739
- `WATCHLIST_NO_ODDS`: n=6, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=12, two_prices=12, avg_raw=-0.013333, avg_ip=0.005964, beat_rate=0.333333
- `WATCHLIST_UNKNOWN_CTX`: n=19, two_prices=18, avg_raw=0.001667, avg_ip=-0.001058, beat_rate=0.0

# Edge Factory — CLV report (2026-07-20 to 2026-08-19)

## Overall

- total unique picks: 309
- picks with at least two prices: 274
- average raw odds delta: 0.002996
- average implied-probability delta: -0.001334
- beat-later-price rate: 0.153285
- beat-later-price sample: 274
- unmatched picks: 16
- picks with fewer than two snapshots: 19

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=103, two_prices=92, avg_raw=0.002326, avg_ip=-0.001656, beat_rate=0.141304
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=46, two_prices=44, avg_raw=0.005114, avg_ip=-0.002902, beat_rate=0.022727
- `3way-unanimous home-only avg_p>=60`: n=9, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=87, two_prices=78, avg_raw=0.008846, avg_ip=-0.003069, beat_rate=0.230769
- `ml-meta avg_p>=60`: n=7, two_prices=4, avg_raw=0.0235, avg_ip=-0.01173, beat_rate=0.0
- `ml-meta avg_p>=65`: n=6, two_prices=3, avg_raw=-0.004, avg_ip=0.006111, beat_rate=0.666667
- `ml-meta avg_p>=70`: n=4, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=-0.03, avg_ip=0.021011, beat_rate=1.0

## By bucket

- `CAUTION`: n=59, two_prices=52, avg_raw=0.002308, avg_ip=-2.7e-05, beat_rate=0.134615
- `CERTIFIED_CLEAN`: n=22, two_prices=22, avg_raw=-0.001, avg_ip=0.0015, beat_rate=0.318182
- `SKIPPED_VETO`: n=165, two_prices=156, avg_raw=0.004763, avg_ip=-0.002448, beat_rate=0.153846
- `WATCHLIST_NO_ODDS`: n=15, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=5, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=23, two_prices=21, avg_raw=-0.007619, avg_ip=0.003408, beat_rate=0.190476
- `WATCHLIST_UNKNOWN_CTX`: n=20, two_prices=19, avg_raw=0.007368, avg_ip=-0.004571, beat_rate=0.0

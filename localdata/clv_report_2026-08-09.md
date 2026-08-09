# Edge Factory — CLV report (2026-07-10 to 2026-08-09)

## Overall

- total unique picks: 164
- picks with at least two prices: 155
- average raw odds delta: 0.001671
- average implied-probability delta: -0.000973
- beat-later-price rate: 0.032258
- beat-later-price sample: 155
- unmatched picks: 5
- picks with fewer than two snapshots: 4

## By rule

- `2way+bc-confirms avg_p>=60`: n=21, two_prices=19, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=77, two_prices=73, avg_raw=0.000603, avg_ip=-0.000369, beat_rate=0.054795
- `3way-unanimous avg_p>=65`: n=45, two_prices=43, avg_raw=0.005, avg_ip=-0.002881, beat_rate=0.023256
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=11, two_prices=11, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=22, two_prices=22, avg_raw=-0.003636, avg_ip=0.001161, beat_rate=0.045455
- `CERTIFIED_CLEAN`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `SKIPPED_VETO`: n=107, two_prices=104, avg_raw=0.002971, avg_ip=-0.001513, beat_rate=0.038462
- `WATCHLIST_NO_ODDS`: n=5, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=6, two_prices=6, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.001875, avg_ip=-0.001191, beat_rate=0.0

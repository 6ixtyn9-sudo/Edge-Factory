# Edge Factory — CLV report (2026-07-11 to 2026-08-10)

## Overall

- total unique picks: 177
- picks with at least two prices: 167
- average raw odds delta: -0.000467
- average implied-probability delta: -4.6e-05
- beat-later-price rate: 0.08982
- beat-later-price sample: 167
- unmatched picks: 5
- picks with fewer than two snapshots: 5

## By rule

- `2way+bc-confirms avg_p>=60`: n=27, two_prices=25, avg_raw=-0.0096, avg_ip=0.003929, beat_rate=0.2
- `2way-unanimous avg_p>=70`: n=81, two_prices=76, avg_raw=-0.000829, avg_ip=0.000286, beat_rate=0.118421
- `3way-unanimous avg_p>=65`: n=48, two_prices=46, avg_raw=0.004891, avg_ip=-0.002776, beat_rate=0.021739
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=11, two_prices=11, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=26, two_prices=25, avg_raw=-0.0008, avg_ip=0.00056, beat_rate=0.04
- `CERTIFIED_CLEAN`: n=9, two_prices=9, avg_raw=-0.033333, avg_ip=0.012197, beat_rate=0.555556
- `SKIPPED_VETO`: n=110, two_prices=107, avg_raw=0.002168, avg_ip=-0.001179, beat_rate=0.074766
- `WATCHLIST_NO_ODDS`: n=5, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=7, two_prices=7, avg_raw=-0.002857, avg_ip=0.001952, beat_rate=0.142857
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=17, avg_raw=0.001765, avg_ip=-0.001121, beat_rate=0.0

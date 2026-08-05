# Edge Factory — CLV report (2026-07-06 to 2026-08-05)

## Overall

- total unique picks: 104
- picks with at least two prices: 96
- average raw odds delta: 0.006927
- average implied-probability delta: -0.003006
- beat-later-price rate: 0.03125
- beat-later-price sample: 96
- unmatched picks: 1
- picks with fewer than two snapshots: 7

## By rule

- `2way-unanimous avg_p>=70`: n=45, two_prices=41, avg_raw=0.000244, avg_ip=-0.000231, beat_rate=0.04878
- `3way-unanimous avg_p>=65`: n=33, two_prices=30, avg_raw=0.0065, avg_ip=-0.003558, beat_rate=0.033333
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=16, two_prices=16, avg_raw=0.02875, avg_ip=-0.010769, beat_rate=0.0

## By bucket

- `CAUTION`: n=17, two_prices=16, avg_raw=-0.005, avg_ip=0.001597, beat_rate=0.0625
- `SKIPPED_VETO`: n=71, two_prices=66, avg_raw=0.010833, avg_ip=-0.00447, beat_rate=0.030303
- `WATCHLIST_NO_ODDS`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=15, two_prices=14, avg_raw=0.002143, avg_ip=-0.001361, beat_rate=0.0

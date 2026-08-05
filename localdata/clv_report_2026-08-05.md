# Edge Factory — CLV report (2026-07-06 to 2026-08-05)

## Overall

- total unique picks: 103
- picks with at least two prices: 93
- average raw odds delta: 0.006935
- average implied-probability delta: -0.003023
- beat-later-price rate: 0.032258
- beat-later-price sample: 93
- unmatched picks: 1
- picks with fewer than two snapshots: 9

## By rule

- `2way-unanimous avg_p>=70`: n=45, two_prices=39, avg_raw=0.000256, avg_ip=-0.000243, beat_rate=0.051282
- `3way-unanimous avg_p>=65`: n=32, two_prices=29, avg_raw=0.006034, avg_ip=-0.003424, beat_rate=0.034483
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=16, two_prices=16, avg_raw=0.02875, avg_ip=-0.010769, beat_rate=0.0

## By bucket

- `CAUTION`: n=17, two_prices=15, avg_raw=-0.005333, avg_ip=0.001703, beat_rate=0.066667
- `SKIPPED_VETO`: n=70, two_prices=64, avg_raw=0.010859, avg_ip=-0.004494, beat_rate=0.03125
- `WATCHLIST_NO_ODDS`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNKNOWN_CTX`: n=15, two_prices=14, avg_raw=0.002143, avg_ip=-0.001361, beat_rate=0.0

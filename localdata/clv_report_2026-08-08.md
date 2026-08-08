# Edge Factory — CLV report (2026-07-09 to 2026-08-08)

## Overall

- total unique picks: 130
- picks with at least two prices: 121
- average raw odds delta: 0.002967
- average implied-probability delta: -0.001613
- beat-later-price rate: 0.024793
- beat-later-price sample: 121
- unmatched picks: 3
- picks with fewer than two snapshots: 6

## By rule

- `2way-unanimous avg_p>=70`: n=67, two_prices=62, avg_raw=0.002645, avg_ip=-0.001294, beat_rate=0.032258
- `3way-unanimous avg_p>=65`: n=41, two_prices=38, avg_raw=0.005132, avg_ip=-0.003026, beat_rate=0.026316
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=12, two_prices=12, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=17, two_prices=16, avg_raw=-0.005, avg_ip=0.001597, beat_rate=0.0625
- `SKIPPED_VETO`: n=92, two_prices=88, avg_raw=0.004648, avg_ip=-0.002292, beat_rate=0.022727
- `WATCHLIST_NO_ODDS`: n=3, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNCORROBORATED_PRICE`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.001875, avg_ip=-0.001191, beat_rate=0.0

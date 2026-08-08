# Edge Factory — CLV report (2026-07-09 to 2026-08-08)

## Overall

- total unique picks: 131
- picks with at least two prices: 123
- average raw odds delta: 0.002106
- average implied-probability delta: -0.001226
- beat-later-price rate: 0.04065
- beat-later-price sample: 123
- unmatched picks: 3
- picks with fewer than two snapshots: 5

## By rule

- `2way-unanimous avg_p>=70`: n=68, two_prices=63, avg_raw=0.000698, avg_ip=-0.000428, beat_rate=0.063492
- `3way-unanimous avg_p>=65`: n=41, two_prices=39, avg_raw=0.005513, avg_ip=-0.003176, beat_rate=0.025641
- `3way-unanimous home-only avg_p>=60`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous home-only avg_p>=65`: n=12, two_prices=12, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=17, two_prices=16, avg_raw=-0.005, avg_ip=0.001597, beat_rate=0.0625
- `SKIPPED_VETO`: n=92, two_prices=89, avg_raw=0.003472, avg_ip=-0.001768, beat_rate=0.044944
- `WATCHLIST_NO_ODDS`: n=3, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_UNCORROBORATED_PRICE`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=17, avg_raw=0.001765, avg_ip=-0.001121, beat_rate=0.0

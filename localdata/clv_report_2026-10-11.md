# Edge Factory — CLV report (2026-09-11 to 2026-10-11)

## Overall

- total unique picks: 1078
- picks with at least two prices: 833
- average raw odds delta: -0.000936
- average implied-probability delta: 0.000717
- beat-later-price rate: 0.094838
- beat-later-price sample: 833
- unmatched picks: 135
- picks with fewer than two snapshots: 110

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=123, two_prices=80, avg_raw=-0.001, avg_ip=0.000766, beat_rate=0.1625
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=505, two_prices=435, avg_raw=-0.004, avg_ip=0.001857, beat_rate=0.110345
- `ml-meta avg_p>=60`: n=146, two_prices=112, avg_raw=-8.9e-05, avg_ip=5.1e-05, beat_rate=0.044643
- `ml-meta avg_p>=65`: n=51, two_prices=34, avg_raw=0.032353, avg_ip=-0.007893, beat_rate=0.058824
- `ml-meta avg_p>=70`: n=9, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=15, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=3, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=8, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=4, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=83, two_prices=74, avg_raw=-0.001486, avg_ip=0.001006, beat_rate=0.135135
- `CERTIFIED_CLEAN`: n=143, two_prices=135, avg_raw=0.005778, avg_ip=-0.000774, beat_rate=0.103704
- `SKIPPED_VETO`: n=547, two_prices=447, avg_raw=-0.001409, avg_ip=0.00077, beat_rate=0.098434
- `WATCHLIST_NO_ODDS`: n=100, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=11, two_prices=6, avg_raw=0.018333, avg_ip=-0.007592, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=184, two_prices=160, avg_raw=-0.00575, avg_ip=0.002009, beat_rate=0.0625
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

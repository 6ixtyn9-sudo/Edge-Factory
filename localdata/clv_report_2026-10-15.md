# Edge Factory — CLV report (2026-09-15 to 2026-10-15)

## Overall

- total unique picks: 964
- picks with at least two prices: 741
- average raw odds delta: -0.003158
- average implied-probability delta: 0.000993
- beat-later-price rate: 0.089069
- beat-later-price sample: 741
- unmatched picks: 127
- picks with fewer than two snapshots: 97

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=88, two_prices=55, avg_raw=-0.002, avg_ip=0.001075, beat_rate=0.163636
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=385, two_prices=334, avg_raw=-0.00503, avg_ip=0.002334, beat_rate=0.10479
- `ml-meta avg_p>=60`: n=184, two_prices=144, avg_raw=-0.010764, avg_ip=0.001004, beat_rate=0.0625
- `ml-meta avg_p>=65`: n=43, two_prices=29, avg_raw=0.036207, avg_ip=-0.008193, beat_rate=0.068966
- `ml-meta avg_p>=70`: n=6, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=12, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+statarea] avg_p>=70`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=9, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=6, two_prices=6, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=74, two_prices=68, avg_raw=-0.0025, avg_ip=0.001525, beat_rate=0.132353
- `CERTIFIED_CLEAN`: n=137, two_prices=132, avg_raw=-0.006136, avg_ip=0.000686, beat_rate=0.098485
- `SKIPPED_VETO`: n=505, two_prices=403, avg_raw=-0.002084, avg_ip=0.000796, beat_rate=0.086849
- `WATCHLIST_NO_ODDS`: n=89, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=10, two_prices=6, avg_raw=0.008333, avg_ip=-0.001936, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=139, two_prices=121, avg_raw=-0.004628, avg_ip=0.001864, beat_rate=0.066116
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

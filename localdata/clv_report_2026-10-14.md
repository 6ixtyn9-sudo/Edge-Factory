# Edge Factory — CLV report (2026-09-14 to 2026-10-14)

## Overall

- total unique picks: 971
- picks with at least two prices: 752
- average raw odds delta: -0.00375
- average implied-probability delta: 0.001197
- beat-later-price rate: 0.094415
- beat-later-price sample: 752
- unmatched picks: 123
- picks with fewer than two snapshots: 95

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=90, two_prices=57, avg_raw=-0.002632, avg_ip=0.001494, beat_rate=0.175439
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=397, two_prices=345, avg_raw=-0.006145, avg_ip=0.00266, beat_rate=0.113043
- `ml-meta avg_p>=60`: n=179, two_prices=143, avg_raw=-0.010839, avg_ip=0.001011, beat_rate=0.062937
- `ml-meta avg_p>=65`: n=44, two_prices=29, avg_raw=0.036207, avg_ip=-0.008193, beat_rate=0.068966
- `ml-meta avg_p>=70`: n=7, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=11, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=8, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=72, two_prices=66, avg_raw=-0.002576, avg_ip=0.001571, beat_rate=0.136364
- `CERTIFIED_CLEAN`: n=137, two_prices=133, avg_raw=-0.00609, avg_ip=0.00068, beat_rate=0.097744
- `SKIPPED_VETO`: n=507, two_prices=409, avg_raw=-0.002347, avg_ip=0.000952, beat_rate=0.09291
- `WATCHLIST_NO_ODDS`: n=88, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=10, two_prices=6, avg_raw=0.008333, avg_ip=-0.001936, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=147, two_prices=127, avg_raw=-0.007244, avg_ip=0.002531, beat_rate=0.07874
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

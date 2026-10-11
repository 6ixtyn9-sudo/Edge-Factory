# Edge Factory — CLV report (2026-09-11 to 2026-10-11)

## Overall

- total unique picks: 1070
- picks with at least two prices: 821
- average raw odds delta: -0.000999
- average implied-probability delta: 0.000739
- beat-later-price rate: 0.096224
- beat-later-price sample: 821
- unmatched picks: 135
- picks with fewer than two snapshots: 116

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=123, two_prices=80, avg_raw=-0.001, avg_ip=0.000766, beat_rate=0.1625
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=500, two_prices=430, avg_raw=-0.004047, avg_ip=0.001879, beat_rate=0.111628
- `ml-meta avg_p>=60`: n=143, two_prices=109, avg_raw=-0.000459, avg_ip=0.000143, beat_rate=0.045872
- `ml-meta avg_p>=65`: n=51, two_prices=34, avg_raw=0.032353, avg_ip=-0.007893, beat_rate=0.058824
- `ml-meta avg_p>=70`: n=9, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=15, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=3, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=8, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=4, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None

## By bucket

- `CAUTION`: n=83, two_prices=74, avg_raw=-0.001486, avg_ip=0.001006, beat_rate=0.135135
- `CERTIFIED_CLEAN`: n=142, two_prices=134, avg_raw=0.005821, avg_ip=-0.00078, beat_rate=0.104478
- `SKIPPED_VETO`: n=540, two_prices=436, avg_raw=-0.001537, avg_ip=0.000812, beat_rate=0.100917
- `WATCHLIST_NO_ODDS`: n=100, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=10, two_prices=5, avg_raw=0.022, avg_ip=-0.00911, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=185, two_prices=161, avg_raw=-0.005714, avg_ip=0.001996, beat_rate=0.062112
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

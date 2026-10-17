# Edge Factory — CLV report (2026-09-18 to 2026-10-18)

## Overall

- total unique picks: 974
- picks with at least two prices: 752
- average raw odds delta: -0.006036
- average implied-probability delta: 0.001486
- beat-later-price rate: 0.075798
- beat-later-price sample: 752
- unmatched picks: 136
- picks with fewer than two snapshots: 88

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=70, two_prices=43, avg_raw=-0.002093, avg_ip=0.001379, beat_rate=0.093023
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=354, two_prices=307, avg_raw=-0.003355, avg_ip=0.001679, beat_rate=0.094463
- `ml-meta avg_p>=60`: n=222, two_prices=174, avg_raw=-0.022236, avg_ip=0.003276, beat_rate=0.051724
- `ml-meta avg_p>=65`: n=37, two_prices=25, avg_raw=0.0416, avg_ip=-0.009262, beat_rate=0.08
- `ml-meta avg_p>=70`: n=2, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=13, two_prices=10, avg_raw=0.005, avg_ip=-0.004476, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=16, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+statarea+vitibet] avg_p>=65`: n=4, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+statarea] avg_p>=70`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=16, two_prices=15, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=19, two_prices=16, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=7, two_prices=6, avg_raw=-0.09, avg_ip=0.03567, beat_rate=0.333333

## By bucket

- `CAUTION`: n=70, two_prices=65, avg_raw=-0.008615, avg_ip=0.003665, beat_rate=0.123077
- `CERTIFIED_CLEAN`: n=137, two_prices=134, avg_raw=-0.003351, avg_ip=-0.000503, beat_rate=0.08209
- `SKIPPED_VETO`: n=520, two_prices=415, avg_raw=-0.007518, avg_ip=0.00187, beat_rate=0.077108
- `WATCHLIST_NO_ODDS`: n=91, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=14, two_prices=10, avg_raw=0.005, avg_ip=-0.001161, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=133, two_prices=117, avg_raw=-0.003932, avg_ip=0.00156, beat_rate=0.051282
- `WATCHLIST_UNKNOWN_CTX`: n=9, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

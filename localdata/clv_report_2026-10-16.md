# Edge Factory — CLV report (2026-09-16 to 2026-10-16)

## Overall

- total unique picks: 955
- picks with at least two prices: 730
- average raw odds delta: -0.006547
- average implied-probability delta: 0.001649
- beat-later-price rate: 0.090411
- beat-later-price sample: 730
- unmatched picks: 128
- picks with fewer than two snapshots: 97

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=81, two_prices=49, avg_raw=-0.004286, avg_ip=0.002291, beat_rate=0.163265
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=380, two_prices=329, avg_raw=-0.004043, avg_ip=0.002008, beat_rate=0.103343
- `ml-meta avg_p>=60`: n=184, two_prices=140, avg_raw=-0.029708, avg_ip=0.004476, beat_rate=0.071429
- `ml-meta avg_p>=65`: n=41, two_prices=28, avg_raw=0.037143, avg_ip=-0.008269, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=5, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=14, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+statarea] avg_p>=70`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=9, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=7, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=6, two_prices=5, avg_raw=-0.014, avg_ip=0.009039, beat_rate=0.2

## By bucket

- `CAUTION`: n=72, two_prices=67, avg_raw=-0.002836, avg_ip=0.001722, beat_rate=0.134328
- `CERTIFIED_CLEAN`: n=138, two_prices=134, avg_raw=-0.00574, avg_ip=0.000619, beat_rate=0.097015
- `SKIPPED_VETO`: n=500, two_prices=395, avg_raw=-0.00838, avg_ip=0.002004, beat_rate=0.091139
- `WATCHLIST_NO_ODDS`: n=89, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=12, two_prices=6, avg_raw=0.008333, avg_ip=-0.001936, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=134, two_prices=117, avg_raw=-0.004786, avg_ip=0.001928, beat_rate=0.068376
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

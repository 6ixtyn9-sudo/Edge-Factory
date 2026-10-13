# Edge Factory — CLV report (2026-09-12 to 2026-10-12)

## Overall

- total unique picks: 1058
- picks with at least two prices: 815
- average raw odds delta: -0.000896
- average implied-probability delta: 0.000703
- beat-later-price rate: 0.087117
- beat-later-price sample: 815
- unmatched picks: 136
- picks with fewer than two snapshots: 108

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=113, two_prices=73, avg_raw=-0.000411, avg_ip=0.00052, beat_rate=0.150685
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=486, two_prices=418, avg_raw=-0.004019, avg_ip=0.001839, beat_rate=0.105263
- `ml-meta avg_p>=60`: n=153, two_prices=116, avg_raw=-0.000172, avg_ip=0.000112, beat_rate=0.025862
- `ml-meta avg_p>=65`: n=46, two_prices=31, avg_raw=0.033871, avg_ip=-0.007664, beat_rate=0.064516
- `ml-meta avg_p>=70`: n=9, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=15, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=8, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=8, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=79, two_prices=72, avg_raw=-0.000972, avg_ip=0.000791, beat_rate=0.125
- `CERTIFIED_CLEAN`: n=140, two_prices=133, avg_raw=0.004887, avg_ip=-0.00055, beat_rate=0.090226
- `SKIPPED_VETO`: n=541, two_prices=439, avg_raw=-0.001116, avg_ip=0.000697, beat_rate=0.088838
- `WATCHLIST_NO_ODDS`: n=98, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=13, two_prices=7, avg_raw=0.015714, avg_ip=-0.006507, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=176, two_prices=152, avg_raw=-0.006053, avg_ip=0.002115, beat_rate=0.065789
- `WATCHLIST_UNKNOWN_CTX`: n=11, two_prices=10, avg_raw=-0.001, avg_ip=0.000689, beat_rate=0.1

# Edge Factory — CLV report (2026-09-17 to 2026-10-17)

## Overall

- total unique picks: 979
- picks with at least two prices: 751
- average raw odds delta: -0.006497
- average implied-probability delta: 0.0017
- beat-later-price rate: 0.082557
- beat-later-price sample: 751
- unmatched picks: 133
- picks with fewer than two snapshots: 95

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=76, two_prices=46, avg_raw=-0.005217, avg_ip=0.003122, beat_rate=0.152174
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=365, two_prices=315, avg_raw=-0.003873, avg_ip=0.001874, beat_rate=0.098413
- `ml-meta avg_p>=60`: n=218, two_prices=169, avg_raw=-0.022894, avg_ip=0.003373, beat_rate=0.053254
- `ml-meta avg_p>=65`: n=41, two_prices=28, avg_raw=0.037143, avg_ip=-0.008269, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=3, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=13, two_prices=10, avg_raw=0.005, avg_ip=-0.004476, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=16, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+statarea] avg_p>=70`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=13, two_prices=12, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=13, two_prices=12, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=7, two_prices=6, avg_raw=-0.09, avg_ip=0.03567, beat_rate=0.333333

## By bucket

- `CAUTION`: n=71, two_prices=66, avg_raw=-0.009848, avg_ip=0.004221, beat_rate=0.136364
- `CERTIFIED_CLEAN`: n=143, two_prices=139, avg_raw=-0.004094, avg_ip=-0.00011, beat_rate=0.086331
- `SKIPPED_VETO`: n=515, two_prices=406, avg_raw=-0.007759, avg_ip=0.001969, beat_rate=0.081281
- `WATCHLIST_NO_ODDS`: n=91, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=14, two_prices=10, avg_raw=0.005, avg_ip=-0.001161, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=136, two_prices=119, avg_raw=-0.004706, avg_ip=0.001896, beat_rate=0.067227
- `WATCHLIST_UNKNOWN_CTX`: n=9, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

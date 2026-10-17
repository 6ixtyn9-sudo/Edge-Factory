# Edge Factory — CLV report (2026-09-17 to 2026-10-17)

## Overall

- total unique picks: 974
- picks with at least two prices: 740
- average raw odds delta: -0.005958
- average implied-probability delta: 0.001497
- beat-later-price rate: 0.082432
- beat-later-price sample: 740
- unmatched picks: 133
- picks with fewer than two snapshots: 105

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=76, two_prices=46, avg_raw=-0.005217, avg_ip=0.003122, beat_rate=0.152174
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=365, two_prices=315, avg_raw=-0.003873, avg_ip=0.001874, beat_rate=0.098413
- `ml-meta avg_p>=60`: n=213, two_prices=159, avg_raw=-0.024334, avg_ip=0.003585, beat_rate=0.056604
- `ml-meta avg_p>=65`: n=41, two_prices=28, avg_raw=0.037143, avg_ip=-0.008269, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=3, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=13, two_prices=10, avg_raw=0.005, avg_ip=-0.004476, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=16, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+statarea] avg_p>=70`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=13, two_prices=12, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=13, two_prices=12, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=7, two_prices=6, avg_raw=-0.011667, avg_ip=0.007533, beat_rate=0.166667

## By bucket

- `CAUTION`: n=71, two_prices=66, avg_raw=-0.002727, avg_ip=0.001663, beat_rate=0.121212
- `CERTIFIED_CLEAN`: n=141, two_prices=135, avg_raw=-0.004216, avg_ip=-0.000114, beat_rate=0.088889
- `SKIPPED_VETO`: n=513, two_prices=402, avg_raw=-0.007836, avg_ip=0.001989, beat_rate=0.08209
- `WATCHLIST_NO_ODDS`: n=91, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=13, two_prices=8, avg_raw=0.00625, avg_ip=-0.001452, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=136, two_prices=118, avg_raw=-0.004746, avg_ip=0.001912, beat_rate=0.067797
- `WATCHLIST_UNKNOWN_CTX`: n=9, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

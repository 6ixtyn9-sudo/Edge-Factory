# Edge Factory — CLV report (2026-09-19 to 2026-10-19)

## Overall

- total unique picks: 948
- picks with at least two prices: 725
- average raw odds delta: -0.006454
- average implied-probability delta: 0.001578
- beat-later-price rate: 0.077241
- beat-later-price sample: 725
- unmatched picks: 138
- picks with fewer than two snapshots: 88

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=58, two_prices=36, avg_raw=-0.002778, avg_ip=0.001892, beat_rate=0.111111
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=330, two_prices=283, avg_raw=-0.004099, avg_ip=0.001884, beat_rate=0.09894
- `ml-meta avg_p>=60`: n=218, two_prices=171, avg_raw=-0.022626, avg_ip=0.003333, beat_rate=0.052632
- `ml-meta avg_p>=65`: n=36, two_prices=25, avg_raw=0.0416, avg_ip=-0.009262, beat_rate=0.08
- `ml-meta avg_p>=70`: n=2, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=13, two_prices=10, avg_raw=0.005, avg_ip=-0.004476, beat_rate=0.0
- `unanimous[betclan+bzzoiro+statarea+vitibet+zulubet] avg_p>=65`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[betclan+bzzoiro+statarea+vitibet] avg_p>=65`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `unanimous[betclan+vitibet] avg_p>=70`: n=21, two_prices=10, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+statarea+vitibet] avg_p>=65`: n=5, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+statarea] avg_p>=70`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=16, two_prices=15, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet+zulubet] avg_p>=65`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=22, two_prices=17, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=7, two_prices=6, avg_raw=-0.09, avg_ip=0.03567, beat_rate=0.333333

## By bucket

- `CAUTION`: n=68, two_prices=63, avg_raw=-0.008889, avg_ip=0.003782, beat_rate=0.126984
- `CERTIFIED_CLEAN`: n=133, two_prices=130, avg_raw=-0.004224, avg_ip=-0.00024, beat_rate=0.084615
- `SKIPPED_VETO`: n=513, two_prices=402, avg_raw=-0.007861, avg_ip=0.001906, beat_rate=0.077114
- `WATCHLIST_NO_ODDS`: n=86, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=14, two_prices=10, avg_raw=0.005, avg_ip=-0.001161, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=125, two_prices=110, avg_raw=-0.004182, avg_ip=0.001659, beat_rate=0.054545
- `WATCHLIST_UNKNOWN_CTX`: n=9, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

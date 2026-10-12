# Edge Factory — CLV report (2026-09-12 to 2026-10-12)

## Overall

- total unique picks: 1049
- picks with at least two prices: 808
- average raw odds delta: -0.000903
- average implied-probability delta: 0.000709
- beat-later-price rate: 0.087871
- beat-later-price sample: 808
- unmatched picks: 136
- picks with fewer than two snapshots: 106

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=113, two_prices=73, avg_raw=-0.000411, avg_ip=0.00052, beat_rate=0.150685
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=486, two_prices=418, avg_raw=-0.004019, avg_ip=0.001839, beat_rate=0.105263
- `ml-meta avg_p>=60`: n=144, two_prices=109, avg_raw=-0.000183, avg_ip=0.000119, beat_rate=0.027523
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
- `CERTIFIED_CLEAN`: n=138, two_prices=131, avg_raw=0.004962, avg_ip=-0.000558, beat_rate=0.091603
- `SKIPPED_VETO`: n=536, two_prices=436, avg_raw=-0.001124, avg_ip=0.000702, beat_rate=0.08945
- `WATCHLIST_NO_ODDS`: n=98, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=12, two_prices=6, avg_raw=0.018333, avg_ip=-0.007592, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=176, two_prices=152, avg_raw=-0.006053, avg_ip=0.002115, beat_rate=0.065789
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

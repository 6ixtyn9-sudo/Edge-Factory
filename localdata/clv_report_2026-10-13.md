# Edge Factory — CLV report (2026-09-13 to 2026-10-13)

## Overall

- total unique picks: 1006
- picks with at least two prices: 773
- average raw odds delta: -0.001358
- average implied-probability delta: 0.000919
- beat-later-price rate: 0.09185
- beat-later-price sample: 773
- unmatched picks: 132
- picks with fewer than two snapshots: 103

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=96, two_prices=60, avg_raw=-0.001667, avg_ip=0.00115, beat_rate=0.183333
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=444, two_prices=385, avg_raw=-0.005013, avg_ip=0.002273, beat_rate=0.114286
- `ml-meta avg_p>=60`: n=161, two_prices=121, avg_raw=-0.000165, avg_ip=0.000107, beat_rate=0.024793
- `ml-meta avg_p>=65`: n=46, two_prices=31, avg_raw=0.033871, avg_ip=-0.007664, beat_rate=0.064516
- `ml-meta avg_p>=70`: n=8, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=14, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=9, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=8, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[statarea+vitibet] avg_p>=70`: n=5, two_prices=5, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `unanimous[vitibet+zulubet] avg_p>=70`: n=2, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0

## By bucket

- `CAUTION`: n=74, two_prices=68, avg_raw=-0.0025, avg_ip=0.001525, beat_rate=0.132353
- `CERTIFIED_CLEAN`: n=134, two_prices=130, avg_raw=0.005, avg_ip=-0.000562, beat_rate=0.092308
- `SKIPPED_VETO`: n=522, two_prices=419, avg_raw=-0.001695, avg_ip=0.000947, beat_rate=0.093079
- `WATCHLIST_NO_ODDS`: n=95, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=10, two_prices=6, avg_raw=0.018333, avg_ip=-0.007592, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=161, two_prices=139, avg_raw=-0.006619, avg_ip=0.002312, beat_rate=0.071942
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

# Edge Factory — CLV report (2026-09-10 to 2026-10-10)

## Overall

- total unique picks: 1037
- picks with at least two prices: 794
- average raw odds delta: -0.001096
- average implied-probability delta: 0.000825
- beat-later-price rate: 0.104534
- beat-later-price sample: 794
- unmatched picks: 128
- picks with fewer than two snapshots: 116

## By rule

- `2way-unanimous avg_p>=60`: n=207, two_prices=142, avg_raw=-0.000704, avg_ip=0.000248, beat_rate=0.077465
- `2way-unanimous avg_p>=70`: n=126, two_prices=82, avg_raw=-0.001098, avg_ip=0.000857, beat_rate=0.170732
- `3way-unanimous avg_p>=65`: n=4, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=55`: n=488, two_prices=421, avg_raw=-0.004133, avg_ip=0.001935, beat_rate=0.118765
- `ml-meta avg_p>=60`: n=132, two_prices=100, avg_raw=-0.0005, avg_ip=0.000155, beat_rate=0.05
- `ml-meta avg_p>=65`: n=49, two_prices=32, avg_raw=0.034375, avg_ip=-0.008386, beat_rate=0.0625
- `ml-meta avg_p>=70`: n=10, two_prices=6, avg_raw=-0.006667, avg_ip=0.005413, beat_rate=0.166667
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=15, two_prices=11, avg_raw=0.004545, avg_ip=-0.004069, beat_rate=0.0
- `unanimous[betclan+vitibet] avg_p>=70`: n=1, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `unanimous[bzzoiro+vitibet] avg_p>=70`: n=3, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None

## By bucket

- `CAUTION`: n=80, two_prices=72, avg_raw=-0.001667, avg_ip=0.001154, beat_rate=0.152778
- `CERTIFIED_CLEAN`: n=134, two_prices=126, avg_raw=0.00619, avg_ip=-0.00083, beat_rate=0.111111
- `SKIPPED_VETO`: n=524, two_prices=421, avg_raw=-0.001686, avg_ip=0.000935, beat_rate=0.111639
- `WATCHLIST_NO_ODDS`: n=96, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=10, two_prices=5, avg_raw=0.022, avg_ip=-0.00911, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=183, two_prices=159, avg_raw=-0.005786, avg_ip=0.002021, beat_rate=0.062893
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=9, avg_raw=-0.001111, avg_ip=0.000765, beat_rate=0.111111

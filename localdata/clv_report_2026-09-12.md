# Edge Factory — CLV report (2026-08-13 to 2026-09-12)

## Overall

- total unique picks: 938
- picks with at least two prices: 809
- average raw odds delta: 0.003714
- average implied-probability delta: -0.000278
- beat-later-price rate: 0.154512
- beat-later-price sample: 809
- unmatched picks: 62
- picks with fewer than two snapshots: 69

## By rule

- `2way-unanimous avg_p>=70`: n=190, two_prices=150, avg_raw=0.000113, avg_ip=1.9e-05, beat_rate=0.153333
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=544, two_prices=500, avg_raw=-0.00052, avg_ip=0.000803, beat_rate=0.178
- `ml-meta avg_p>=60`: n=72, two_prices=55, avg_raw=0.057455, avg_ip=-0.010784, beat_rate=0.072727
- `ml-meta avg_p>=65`: n=26, two_prices=16, avg_raw=-0.005125, avg_ip=0.002194, beat_rate=0.1875
- `ml-meta avg_p>=70`: n=28, two_prices=18, avg_raw=0.010556, avg_ip=-0.004479, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=5, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=122, two_prices=110, avg_raw=0.005455, avg_ip=-0.000936, beat_rate=0.163636
- `CERTIFIED_CLEAN`: n=74, two_prices=62, avg_raw=0.051419, avg_ip=-0.008944, beat_rate=0.209677
- `SKIPPED_VETO`: n=475, two_prices=440, avg_raw=-0.001348, avg_ip=0.000705, beat_rate=0.188636
- `WATCHLIST_NO_ODDS`: n=51, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.007778, avg_ip=0.003956, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=174, two_prices=166, avg_raw=-0.001084, avg_ip=0.000797, beat_rate=0.054217
- `WATCHLIST_UNKNOWN_CTX`: n=15, two_prices=13, avg_raw=0.01, avg_ip=-0.006257, beat_rate=0.0

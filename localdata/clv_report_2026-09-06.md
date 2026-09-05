# Edge Factory — CLV report (2026-08-07 to 2026-09-06)

## Overall

- total unique picks: 842
- picks with at least two prices: 746
- average raw odds delta: 0.004118
- average implied-probability delta: -0.000449
- beat-later-price rate: 0.146113
- beat-later-price sample: 746
- unmatched picks: 54
- picks with fewer than two snapshots: 44

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=185, two_prices=157, avg_raw=-0.000892, avg_ip=0.000389, beat_rate=0.159236
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=13, two_prices=13, avg_raw=0.002308, avg_ip=-0.000979, beat_rate=0.0
- `ml-meta avg_p>=55`: n=434, two_prices=403, avg_raw=0.000645, avg_ip=0.000247, beat_rate=0.171216
- `ml-meta avg_p>=60`: n=57, two_prices=45, avg_raw=0.070978, avg_ip=-0.01355, beat_rate=0.022222
- `ml-meta avg_p>=65`: n=20, two_prices=11, avg_raw=-0.012, avg_ip=0.005988, beat_rate=0.272727
- `ml-meta avg_p>=70`: n=22, two_prices=16, avg_raw=0.013125, avg_ip=-0.006555, beat_rate=0.0625
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.000769, avg_ip=-0.000326, beat_rate=0.038462

## By bucket

- `CAUTION`: n=115, two_prices=106, avg_raw=0.006132, avg_ip=-0.000812, beat_rate=0.150943
- `CERTIFIED_CLEAN`: n=67, two_prices=59, avg_raw=0.046576, avg_ip=-0.007145, beat_rate=0.237288
- `SKIPPED_VETO`: n=420, two_prices=400, avg_raw=-0.00039, avg_ip=0.000187, beat_rate=0.17
- `WATCHLIST_NO_ODDS`: n=46, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=23, two_prices=17, avg_raw=-0.009412, avg_ip=0.004672, beat_rate=0.117647
- `WATCHLIST_UNCORROBORATED_PRICE`: n=153, two_prices=146, avg_raw=-0.00089, avg_ip=0.000634, beat_rate=0.061644
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=18, avg_raw=0.006667, avg_ip=-0.004136, beat_rate=0.0

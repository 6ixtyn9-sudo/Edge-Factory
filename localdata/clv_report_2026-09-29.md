# Edge Factory — CLV report (2026-08-30 to 2026-09-29)

## Overall

- total unique picks: 1167
- picks with at least two prices: 954
- average raw odds delta: -0.002977
- average implied-probability delta: 0.00135
- beat-later-price rate: 0.140461
- beat-later-price sample: 954
- unmatched picks: 87
- picks with fewer than two snapshots: 125

## By rule

- `2way-unanimous avg_p>=60`: n=134, two_prices=97, avg_raw=-0.002268, avg_ip=0.000378, beat_rate=0.072165
- `2way-unanimous avg_p>=70`: n=178, two_prices=124, avg_raw=-0.002097, avg_ip=0.001287, beat_rate=0.201613
- `ml-meta avg_p>=55`: n=612, two_prices=553, avg_raw=-0.004087, avg_ip=0.001939, beat_rate=0.162749
- `ml-meta avg_p>=60`: n=113, two_prices=82, avg_raw=-0.000976, avg_ip=0.000396, beat_rate=0.073171
- `ml-meta avg_p>=65`: n=39, two_prices=26, avg_raw=-0.002692, avg_ip=0.000739, beat_rate=0.076923
- `ml-meta avg_p>=70`: n=25, two_prices=12, avg_raw=0.003333, avg_ip=-0.001634, beat_rate=0.083333
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=109, two_prices=97, avg_raw=-0.001856, avg_ip=0.00156, beat_rate=0.195876
- `CERTIFIED_CLEAN`: n=136, two_prices=121, avg_raw=-0.004463, avg_ip=0.001804, beat_rate=0.173554
- `SKIPPED_VETO`: n=577, two_prices=496, avg_raw=-0.002782, avg_ip=0.001284, beat_rate=0.157258
- `WATCHLIST_NO_ODDS`: n=70, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=26, two_prices=17, avg_raw=0.000588, avg_ip=-0.000367, beat_rate=0.058824
- `WATCHLIST_UNCORROBORATED_PRICE`: n=238, two_prices=212, avg_raw=-0.003538, avg_ip=0.001359, beat_rate=0.066038
- `WATCHLIST_UNKNOWN_CTX`: n=11, two_prices=9, avg_raw=0.0, avg_ip=0.0, beat_rate=0.111111

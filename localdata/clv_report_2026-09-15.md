# Edge Factory — CLV report (2026-08-16 to 2026-09-15)

## Overall

- total unique picks: 994
- picks with at least two prices: 852
- average raw odds delta: 0.002054
- average implied-probability delta: 0.000285
- beat-later-price rate: 0.149061
- beat-later-price sample: 852
- unmatched picks: 67
- picks with fewer than two snapshots: 76

## By rule

- `2way-unanimous avg_p>=70`: n=193, two_prices=152, avg_raw=-6.6e-05, avg_ip=0.000332, beat_rate=0.157895
- `ml-meta avg_p>=55`: n=575, two_prices=521, avg_raw=-0.002764, avg_ip=0.001542, beat_rate=0.172745
- `ml-meta avg_p>=60`: n=99, two_prices=80, avg_raw=0.039375, avg_ip=-0.007293, beat_rate=0.0625
- `ml-meta avg_p>=65`: n=28, two_prices=17, avg_raw=-0.007059, avg_ip=0.002589, beat_rate=0.117647
- `ml-meta avg_p>=70`: n=31, two_prices=20, avg_raw=0.0095, avg_ip=-0.004031, beat_rate=0.1
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=115, two_prices=104, avg_raw=0.005481, avg_ip=-0.001188, beat_rate=0.144231
- `CERTIFIED_CLEAN`: n=82, two_prices=68, avg_raw=0.044118, avg_ip=-0.007551, beat_rate=0.191176
- `SKIPPED_VETO`: n=502, two_prices=464, avg_raw=-0.002996, avg_ip=0.001549, beat_rate=0.185345
- `WATCHLIST_NO_ODDS`: n=55, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.004444, avg_ip=0.002071, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=199, two_prices=185, avg_raw=-0.002541, avg_ip=0.001072, beat_rate=0.054054
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=13, avg_raw=0.009231, avg_ip=-0.005727, beat_rate=0.076923

# Edge Factory — CLV report (2026-08-05 to 2026-09-04)

## Overall

- total unique picks: 705
- picks with at least two prices: 633
- average raw odds delta: 0.005049
- average implied-probability delta: -0.000745
- beat-later-price rate: 0.157978
- beat-later-price sample: 633
- unmatched picks: 40
- picks with fewer than two snapshots: 32

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=172, two_prices=149, avg_raw=0.000698, avg_ip=-0.000399, beat_rate=0.154362
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=19, two_prices=19, avg_raw=0.002632, avg_ip=-0.001494, beat_rate=0.0
- `ml-meta avg_p>=55`: n=350, two_prices=328, avg_raw=0.000488, avg_ip=0.00025, beat_rate=0.192073
- `ml-meta avg_p>=60`: n=52, two_prices=43, avg_raw=0.074279, avg_ip=-0.01418, beat_rate=0.023256
- `ml-meta avg_p>=65`: n=17, two_prices=10, avg_raw=-0.0132, avg_ip=0.006587, beat_rate=0.3
- `ml-meta avg_p>=70`: n=17, two_prices=14, avg_raw=0.015, avg_ip=-0.007491, beat_rate=0.071429
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=24, two_prices=21, avg_raw=0.0, avg_ip=3.2e-05, beat_rate=0.047619

## By bucket

- `CAUTION`: n=107, two_prices=98, avg_raw=0.005714, avg_ip=-0.001202, beat_rate=0.153061
- `CERTIFIED_CLEAN`: n=55, two_prices=52, avg_raw=0.052462, avg_ip=-0.007672, beat_rate=0.25
- `SKIPPED_VETO`: n=368, two_prices=354, avg_raw=0.000192, avg_ip=-0.000137, beat_rate=0.175141
- `WATCHLIST_NO_ODDS`: n=37, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=12, two_prices=9, avg_raw=-0.017778, avg_ip=0.008826, beat_rate=0.222222
- `WATCHLIST_UNCORROBORATED_PRICE`: n=108, two_prices=102, avg_raw=-0.001176, avg_ip=0.00087, beat_rate=0.078431
- `WATCHLIST_UNKNOWN_CTX`: n=18, two_prices=18, avg_raw=0.006667, avg_ip=-0.004136, beat_rate=0.0

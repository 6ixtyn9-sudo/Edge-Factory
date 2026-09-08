# Edge Factory — CLV report (2026-08-09 to 2026-09-08)

## Overall

- total unique picks: 873
- picks with at least two prices: 767
- average raw odds delta: 0.003784
- average implied-probability delta: -0.000372
- beat-later-price rate: 0.15515
- beat-later-price sample: 767
- unmatched picks: 55
- picks with fewer than two snapshots: 52

## By rule

- `2way+bc-confirms avg_p>=60`: n=35, two_prices=33, avg_raw=-0.010909, avg_ip=0.004892, beat_rate=0.212121
- `2way-unanimous avg_p>=70`: n=179, two_prices=146, avg_raw=0.0, avg_ip=6e-06, beat_rate=0.171233
- `2way-unanimous min_p>=60 avg_p>=65`: n=11, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `3way-unanimous avg_p>=65`: n=8, two_prices=8, avg_raw=0.00125, avg_ip=-0.000479, beat_rate=0.0
- `ml-meta avg_p>=55`: n=470, two_prices=436, avg_raw=-2.3e-05, avg_ip=0.000446, beat_rate=0.178899
- `ml-meta avg_p>=60`: n=62, two_prices=48, avg_raw=0.066542, avg_ip=-0.012703, beat_rate=0.020833
- `ml-meta avg_p>=65`: n=20, two_prices=11, avg_raw=-0.012, avg_ip=0.005988, beat_rate=0.272727
- `ml-meta avg_p>=70`: n=23, two_prices=17, avg_raw=0.013529, avg_ip=-0.006653, beat_rate=0.058824
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=3, two_prices=3, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=121, two_prices=111, avg_raw=0.005495, avg_ip=-0.00062, beat_rate=0.153153
- `CERTIFIED_CLEAN`: n=75, two_prices=66, avg_raw=0.041788, avg_ip=-0.00651, beat_rate=0.242424
- `SKIPPED_VETO`: n=429, two_prices=404, avg_raw=-0.000708, avg_ip=0.000288, beat_rate=0.183168
- `WATCHLIST_NO_ODDS`: n=46, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=28, two_prices=20, avg_raw=-0.007, avg_ip=0.003561, beat_rate=0.1
- `WATCHLIST_UNCORROBORATED_PRICE`: n=157, two_prices=150, avg_raw=-0.001133, avg_ip=0.000712, beat_rate=0.066667
- `WATCHLIST_UNKNOWN_CTX`: n=17, two_prices=16, avg_raw=0.008125, avg_ip=-0.005084, beat_rate=0.0

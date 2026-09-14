# Edge Factory — CLV report (2026-08-15 to 2026-09-14)

## Overall

- total unique picks: 995
- picks with at least two prices: 850
- average raw odds delta: 0.002482
- average implied-probability delta: 0.000175
- beat-later-price rate: 0.151765
- beat-later-price sample: 850
- unmatched picks: 71
- picks with fewer than two snapshots: 75

## By rule

- `2way-unanimous avg_p>=70`: n=192, two_prices=150, avg_raw=-0.000733, avg_ip=0.000691, beat_rate=0.153333
- `2way-unanimous min_p>=60 avg_p>=65`: n=7, two_prices=4, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=55`: n=588, two_prices=533, avg_raw=-0.001801, avg_ip=0.00121, beat_rate=0.174484
- `ml-meta avg_p>=60`: n=84, two_prices=66, avg_raw=0.047424, avg_ip=-0.008663, beat_rate=0.075758
- `ml-meta avg_p>=65`: n=27, two_prices=16, avg_raw=-0.0075, avg_ip=0.00275, beat_rate=0.125
- `ml-meta avg_p>=70`: n=29, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=118, two_prices=107, avg_raw=0.004953, avg_ip=-0.001073, beat_rate=0.149533
- `CERTIFIED_CLEAN`: n=81, two_prices=67, avg_raw=0.044776, avg_ip=-0.007664, beat_rate=0.19403
- `SKIPPED_VETO`: n=497, two_prices=460, avg_raw=-0.002174, avg_ip=0.001354, beat_rate=0.191304
- `WATCHLIST_NO_ODDS`: n=58, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=29, two_prices=19, avg_raw=-0.004211, avg_ip=0.001962, beat_rate=0.105263
- `WATCHLIST_UNCORROBORATED_PRICE`: n=198, two_prices=184, avg_raw=-0.002554, avg_ip=0.001078, beat_rate=0.054348
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=13, avg_raw=0.01, avg_ip=-0.006257, beat_rate=0.0

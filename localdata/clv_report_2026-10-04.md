# Edge Factory — CLV report (2026-09-04 to 2026-10-04)

## Overall

- total unique picks: 1132
- picks with at least two prices: 901
- average raw odds delta: -0.002786
- average implied-probability delta: 0.001333
- beat-later-price rate: 0.130966
- beat-later-price sample: 901
- unmatched picks: 111
- picks with fewer than two snapshots: 122

## By rule

- `2way-unanimous avg_p>=60`: n=197, two_prices=134, avg_raw=-0.000746, avg_ip=0.000263, beat_rate=0.08209
- `2way-unanimous avg_p>=70`: n=143, two_prices=95, avg_raw=-0.001579, avg_ip=0.001116, beat_rate=0.210526
- `ml-meta avg_p>=55`: n=569, two_prices=505, avg_raw=-0.004356, avg_ip=0.002068, beat_rate=0.148515
- `ml-meta avg_p>=60`: n=111, two_prices=86, avg_raw=-0.001047, avg_ip=0.000436, beat_rate=0.069767
- `ml-meta avg_p>=65`: n=40, two_prices=28, avg_raw=0.0, avg_ip=0.000179, beat_rate=0.071429
- `ml-meta avg_p>=70`: n=21, two_prices=9, avg_raw=-0.002222, avg_ip=0.002695, beat_rate=0.111111
- `ml-meta avg_p>=75`: n=2, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `ml-meta avg_p>=80`: n=11, two_prices=9, avg_raw=0.006667, avg_ip=-0.006011, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=38, two_prices=35, avg_raw=-0.000286, avg_ip=6.8e-05, beat_rate=0.085714

## By bucket

- `CAUTION`: n=99, two_prices=90, avg_raw=-0.002444, avg_ip=0.001905, beat_rate=0.177778
- `CERTIFIED_CLEAN`: n=133, two_prices=119, avg_raw=-0.003109, avg_ip=0.001477, beat_rate=0.159664
- `SKIPPED_VETO`: n=551, two_prices=464, avg_raw=-0.002112, avg_ip=0.001079, beat_rate=0.146552
- `WATCHLIST_NO_ODDS`: n=86, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=22, two_prices=14, avg_raw=0.009286, avg_ip=-0.003841, beat_rate=0.0
- `WATCHLIST_UNCORROBORATED_PRICE`: n=231, two_prices=204, avg_raw=-0.005245, avg_ip=0.001994, beat_rate=0.068627
- `WATCHLIST_UNKNOWN_CTX`: n=10, two_prices=8, avg_raw=0.0, avg_ip=0.0, beat_rate=0.125

# Edge Factory — CLV report (2026-08-18 to 2026-09-17)

## Overall

- total unique picks: 1002
- picks with at least two prices: 849
- average raw odds delta: 0.001484
- average implied-probability delta: 0.000562
- beat-later-price rate: 0.151943
- beat-later-price sample: 849
- unmatched picks: 66
- picks with fewer than two snapshots: 87

## By rule

- `2way-unanimous avg_p>=70`: n=197, two_prices=151, avg_raw=-0.001457, avg_ip=0.001097, beat_rate=0.178808
- `ml-meta avg_p>=55`: n=570, two_prices=515, avg_raw=-0.003204, avg_ip=0.001748, beat_rate=0.172816
- `ml-meta avg_p>=60`: n=103, two_prices=82, avg_raw=0.036829, avg_ip=-0.00644, beat_rate=0.073171
- `ml-meta avg_p>=65`: n=31, two_prices=19, avg_raw=-0.003158, avg_ip=0.000564, beat_rate=0.052632
- `ml-meta avg_p>=70`: n=32, two_prices=19, avg_raw=0.01, avg_ip=-0.004243, beat_rate=0.105263
- `ml-meta avg_p>=75`: n=5, two_prices=5, avg_raw=-0.006, avg_ip=0.004202, beat_rate=0.2
- `ml-meta avg_p>=80`: n=7, two_prices=6, avg_raw=0.001667, avg_ip=-0.001556, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=107, two_prices=96, avg_raw=0.004687, avg_ip=-0.000653, beat_rate=0.15625
- `CERTIFIED_CLEAN`: n=92, two_prices=77, avg_raw=0.034935, avg_ip=-0.004795, beat_rate=0.194805
- `SKIPPED_VETO`: n=508, two_prices=461, avg_raw=-0.00269, avg_ip=0.001381, beat_rate=0.182213
- `WATCHLIST_NO_ODDS`: n=54, two_prices=0, avg_raw=None, avg_ip=None, beat_rate=None
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=-0.004444, avg_ip=0.002071, beat_rate=0.111111
- `WATCHLIST_UNCORROBORATED_PRICE`: n=200, two_prices=185, avg_raw=-0.003081, avg_ip=0.001305, beat_rate=0.064865
- `WATCHLIST_UNKNOWN_CTX`: n=14, two_prices=12, avg_raw=0.000833, avg_ip=-0.000555, beat_rate=0.083333

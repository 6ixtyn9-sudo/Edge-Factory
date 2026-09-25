# Edge Factory — CLV report (2026-08-26 to 2026-09-25)

## Overall

- total unique picks: 1122
- picks with at least two prices: 935
- average raw odds delta: 0.000428
- average implied-probability delta: 0.000832
- beat-later-price rate: 0.148663
- beat-later-price sample: 935
- unmatched picks: 76
- picks with fewer than two snapshots: 111

## By rule

- `2way-unanimous avg_p>=60`: n=49, two_prices=37, avg_raw=-0.006486, avg_ip=0.000662, beat_rate=0.081081
- `2way-unanimous avg_p>=70`: n=201, two_prices=143, avg_raw=-0.001678, avg_ip=0.001135, beat_rate=0.188811
- `ml-meta avg_p>=55`: n=631, two_prices=577, avg_raw=-0.00331, avg_ip=0.001802, beat_rate=0.168111
- `ml-meta avg_p>=60`: n=118, two_prices=86, avg_raw=0.032558, avg_ip=-0.004975, beat_rate=0.081395
- `ml-meta avg_p>=65`: n=33, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=102, two_prices=92, avg_raw=0.001848, avg_ip=-0.000133, beat_rate=0.195652
- `CERTIFIED_CLEAN`: n=128, two_prices=113, avg_raw=0.020354, avg_ip=-0.001974, beat_rate=0.20354
- `SKIPPED_VETO`: n=550, two_prices=487, avg_raw=-0.002834, avg_ip=0.001538, beat_rate=0.168378
- `WATCHLIST_NO_ODDS`: n=63, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=243, two_prices=216, avg_raw=-0.003241, avg_ip=0.001251, beat_rate=0.064815
- `WATCHLIST_UNKNOWN_CTX`: n=9, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.142857

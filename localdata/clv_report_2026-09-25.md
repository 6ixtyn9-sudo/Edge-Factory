# Edge Factory — CLV report (2026-08-26 to 2026-09-25)

## Overall

- total unique picks: 1121
- picks with at least two prices: 931
- average raw odds delta: 0.000741
- average implied-probability delta: 0.000686
- beat-later-price rate: 0.146079
- beat-later-price sample: 931
- unmatched picks: 76
- picks with fewer than two snapshots: 113

## By rule

- `2way-unanimous avg_p>=60`: n=48, two_prices=35, avg_raw=-0.005429, avg_ip=9.3e-05, beat_rate=0.057143
- `2way-unanimous avg_p>=70`: n=201, two_prices=143, avg_raw=-0.001678, avg_ip=0.001135, beat_rate=0.188811
- `ml-meta avg_p>=55`: n=631, two_prices=576, avg_raw=-0.003003, avg_ip=0.001658, beat_rate=0.166667
- `ml-meta avg_p>=60`: n=118, two_prices=85, avg_raw=0.033647, avg_ip=-0.005416, beat_rate=0.070588
- `ml-meta avg_p>=65`: n=33, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=102, two_prices=92, avg_raw=0.002065, avg_ip=-0.000222, beat_rate=0.184783
- `CERTIFIED_CLEAN`: n=128, two_prices=113, avg_raw=0.021416, avg_ip=-0.002525, beat_rate=0.19469
- `SKIPPED_VETO`: n=551, two_prices=484, avg_raw=-0.002541, avg_ip=0.001406, beat_rate=0.167355
- `WATCHLIST_NO_ODDS`: n=63, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=241, two_prices=215, avg_raw=-0.003256, avg_ip=0.001257, beat_rate=0.065116
- `WATCHLIST_UNKNOWN_CTX`: n=9, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.142857

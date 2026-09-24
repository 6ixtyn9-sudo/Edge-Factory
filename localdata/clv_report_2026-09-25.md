# Edge Factory — CLV report (2026-08-26 to 2026-09-25)

## Overall

- total unique picks: 1110
- picks with at least two prices: 926
- average raw odds delta: 0.000864
- average implied-probability delta: 0.000663
- beat-later-price rate: 0.144708
- beat-later-price sample: 926
- unmatched picks: 76
- picks with fewer than two snapshots: 108

## By rule

- `2way-unanimous avg_p>=60`: n=43, two_prices=33, avg_raw=0.000909, avg_ip=-0.002326, beat_rate=0.030303
- `2way-unanimous avg_p>=70`: n=201, two_prices=143, avg_raw=-0.001678, avg_ip=0.001135, beat_rate=0.188811
- `ml-meta avg_p>=55`: n=625, two_prices=572, avg_raw=-0.003217, avg_ip=0.001765, beat_rate=0.166084
- `ml-meta avg_p>=60`: n=118, two_prices=86, avg_raw=0.033256, avg_ip=-0.005353, beat_rate=0.069767
- `ml-meta avg_p>=65`: n=33, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=26, two_prices=13, avg_raw=0.003077, avg_ip=-0.001508, beat_rate=0.076923
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=6, two_prices=5, avg_raw=0.002, avg_ip=-0.001867, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=101, two_prices=91, avg_raw=0.001758, avg_ip=-9.5e-05, beat_rate=0.186813
- `CERTIFIED_CLEAN`: n=126, two_prices=111, avg_raw=0.02045, avg_ip=-0.001949, beat_rate=0.198198
- `SKIPPED_VETO`: n=547, two_prices=484, avg_raw=-0.001942, avg_ip=0.001187, beat_rate=0.163223
- `WATCHLIST_NO_ODDS`: n=63, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=237, two_prices=213, avg_raw=-0.003286, avg_ip=0.001269, beat_rate=0.065728
- `WATCHLIST_UNKNOWN_CTX`: n=9, two_prices=7, avg_raw=0.0, avg_ip=0.0, beat_rate=0.142857

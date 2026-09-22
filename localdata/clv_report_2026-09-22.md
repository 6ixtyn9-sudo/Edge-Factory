# Edge Factory — CLV report (2026-08-23 to 2026-09-22)

## Overall

- total unique picks: 1104
- picks with at least two prices: 921
- average raw odds delta: 0.000988
- average implied-probability delta: 0.000647
- beat-later-price rate: 0.143322
- beat-later-price sample: 921
- unmatched picks: 70
- picks with fewer than two snapshots: 113

## By rule

- `2way-unanimous avg_p>=60`: n=6, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `2way-unanimous avg_p>=70`: n=216, two_prices=156, avg_raw=-0.001603, avg_ip=0.001145, beat_rate=0.179487
- `ml-meta avg_p>=55`: n=618, two_prices=562, avg_raw=-0.003132, avg_ip=0.001659, beat_rate=0.163701
- `ml-meta avg_p>=60`: n=135, two_prices=105, avg_raw=0.027905, avg_ip=-0.004687, beat_rate=0.057143
- `ml-meta avg_p>=65`: n=34, two_prices=21, avg_raw=-0.002857, avg_ip=0.00051, beat_rate=0.047619
- `ml-meta avg_p>=70`: n=29, two_prices=15, avg_raw=0.002667, avg_ip=-0.001408, beat_rate=0.133333
- `ml-meta avg_p>=75`: n=1, two_prices=1, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `ml-meta avg_p>=80`: n=8, two_prices=7, avg_raw=0.001429, avg_ip=-0.001334, beat_rate=0.0
- `ou25-unanimous-2way-sa avg_p>=70`: n=57, two_prices=52, avg_raw=0.0, avg_ip=-5.3e-05, beat_rate=0.057692

## By bucket

- `CAUTION`: n=102, two_prices=91, avg_raw=0.003626, avg_ip=-0.000581, beat_rate=0.175824
- `CERTIFIED_CLEAN`: n=120, two_prices=103, avg_raw=0.023592, avg_ip=-0.00284, beat_rate=0.194175
- `SKIPPED_VETO`: n=556, two_prices=494, avg_raw=-0.002368, avg_ip=0.001398, beat_rate=0.163968
- `WATCHLIST_NO_ODDS`: n=60, two_prices=2, avg_raw=0.0, avg_ip=0.0, beat_rate=0.0
- `WATCHLIST_SUSPECT_PRICE`: n=27, two_prices=18, avg_raw=0.000556, avg_ip=-0.000346, beat_rate=0.055556
- `WATCHLIST_UNCORROBORATED_PRICE`: n=231, two_prices=207, avg_raw=-0.003333, avg_ip=0.001243, beat_rate=0.062802
- `WATCHLIST_UNKNOWN_CTX`: n=8, two_prices=6, avg_raw=0.0, avg_ip=0.0, beat_rate=0.166667

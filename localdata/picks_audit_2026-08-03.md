# Edge Factory — Recent picks audit (2026-07-05 to 2026-08-03)

## Overall

- archived pick rows: 90
- archived pick dates: 25
- settled picks: 84
- eligible prior 1x2 picks: 84
- unmatched result picks: 0
- ambiguous result picks: 0
- wins: 66
- hit rate: 0.785714
- priced picks: 81
- ROI: 0.046852

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-03
- same-day rows excluded: 6

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 59 / 84 matches (70.2%)
- **Both Teams to Score (BTTS)**: occurred in 43 / 84 matches (51.2%)
- **Selected Team Over 1.5 Goals**: occurred in 64 / 84 matches (76.2%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 24
- **Total Hits**: 14
- **Overall Hit Rate**: 58.3%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `goal_range_2_3`: recommended=4, hits=1, hit_rate=25.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=5, hits=2, hit_rate=40.0%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## By rule

- `2way-unanimous avg_p>=70`: settled=37, wins=28, hit_rate=0.756757, ROI=0.068529
- `3way-unanimous avg_p>=65`: settled=23, wins=17, hit_rate=0.73913, ROI=-0.045
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.176667
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=20, wins=12, hit_rate=0.6, ROI=-0.025
- `SKIPPED_VETO`: settled=49, wins=42, hit_rate=0.857143, ROI=0.09398
- `WATCHLIST_NO_ODDS`: settled=3, wins=2, hit_rate=0.666667, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=12, wins=10, hit_rate=0.833333, ROI=-0.025833

## By odds source

- `UNKNOWN`: settled=3, wins=2, hit_rate=0.666667, ROI=None
- `betexplorer_odds`: settled=44, wins=38, hit_rate=0.863636, ROI=0.108409
- `bzzoiro_odds`: settled=21, wins=18, hit_rate=0.857143, ROI=0.20881
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=12, wins=6, hit_rate=0.5, ROI=-0.331667
- `zulubet`: settled=2, wins=1, hit_rate=0.5, ROI=-0.3

## By odds match method

- `alias_fuzzy`: settled=4, wins=2, hit_rate=0.5, ROI=-0.3875
- `betexplorer`: settled=44, wins=38, hit_rate=0.863636, ROI=0.108409
- `exact`: settled=29, wins=22, hit_rate=0.758621, ROI=0.067414
- `fallback`: settled=4, wins=2, hit_rate=0.5, ROI=-0.345
- `none`: settled=3, wins=2, hit_rate=0.666667, ROI=None
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-02: AIK Stockholm vs Orgryte IS (Actual Score: **0-3**)
- **1X2 Pick**: Selected `HOME` @ 1.52 -> 🔴 LOST (Expected prob: 76.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 4-0 (11.7%), [🔴 MISS] 2-1 (11.7%)

### 2026-08-02: Dinamo Brest vs Belshina (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.32 -> 🟢 WON (Expected prob: 75.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.0%), [🔴 MISS] 3-0 (11.8%)

### 2026-08-02: Kongsvinger vs Strommen (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 75.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.0%), [🔴 MISS] 3-0 (11.8%)

### 2026-08-02: Noah vs Syunik (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.31 -> 🟢 WON (Expected prob: 68.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.3%), [🟢 HIT] 3-0 (12.9%)

### 2026-08-02: Independiente del Valle vs Deportivo Cuenca (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 80.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 92.2% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (19.6%), [🔴 MISS] 3-1 (14.5%)

### 2026-08-02: Ludogorets vs Botev Vratsa (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 69.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (15.0%), [🔴 MISS] 3-0 (13.8%)

### 2026-08-02: ODD Ballklubb vs Asane (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 68.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.4%), [🔴 MISS] 3-0 (13.1%)

### 2026-08-02: Dunajska Streda vs Dukla Banska Bystrica (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (13.5%), [🔴 MISS] 3-0 (13.3%)

### 2026-08-02: Clarence Zebras vs Ulverstone (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.23 -> 🟢 WON (Expected prob: 75.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.0%), [🔴 MISS] 3-0 (11.8%)


## Unmatched result examples

- none

## Ambiguous result examples

- none

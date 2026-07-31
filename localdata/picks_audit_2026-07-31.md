# Edge Factory — Recent picks audit (2026-07-02 to 2026-07-31)

## Overall

- archived pick rows: 54
- archived pick dates: 18
- settled picks: 50
- eligible prior 1x2 picks: 50
- unmatched result picks: 0
- ambiguous result picks: 0
- wins: 44
- hit rate: 0.88
- priced picks: 50
- ROI: 0.1427

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-31
- same-day rows excluded: 4

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 35 / 50 matches (70.0%)
- **Both Teams to Score (BTTS)**: occurred in 25 / 50 matches (50.0%)
- **Selected Team Over 1.5 Goals**: occurred in 41 / 50 matches (82.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 6
- **Total Hits**: 6
- **Overall Hit Rate**: 100.0%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%

## By rule

- `2way-unanimous avg_p>=70`: settled=17, wins=16, hit_rate=0.941176, ROI=0.304706
- `3way-unanimous avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=-0.060556
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.176667
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=6, wins=5, hit_rate=0.833333, ROI=0.493333
- `SKIPPED_VETO`: settled=36, wins=32, hit_rate=0.888889, ROI=0.115417
- `WATCHLIST_UNKNOWN_CTX`: settled=8, wins=7, hit_rate=0.875, ROI=0.0025

## By odds source

- `betexplorer_odds`: settled=31, wins=27, hit_rate=0.870968, ROI=0.109355
- `bzzoiro_odds`: settled=13, wins=13, hit_rate=1.0, ROI=0.365769
- `forebet_best`: settled=1, wins=1, hit_rate=1.0, ROI=0.22
- `scoutingstats_odds`: settled=5, wins=3, hit_rate=0.6, ROI=-0.246

## By odds match method

- `alias_fuzzy`: settled=2, wins=2, hit_rate=1.0, ROI=0.225
- `betexplorer`: settled=31, wins=27, hit_rate=0.870968, ROI=0.109355
- `exact`: settled=16, wins=14, hit_rate=0.875, ROI=0.192187
- `fallback`: settled=1, wins=1, hit_rate=1.0, ROI=0.22
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-07-30: Benfica vs FC ST. Gallen (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.17 -> 🟢 WON (Expected prob: 80.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.8% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 92.3% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.9%), [🔴 MISS] 3-0 (13.1%)

### 2026-07-30: Hibernian vs Malisheva (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 71.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (13.8%), [🔴 MISS] 2-0 (13.4%)

### 2026-07-30: FC Sion vs BATE Borisov (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.125 -> 🟢 WON (Expected prob: 68.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.2% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (15.5%), [🔴 MISS] 1-0 (13.3%)

### 2026-07-30: SC Braga vs Železničar Pančevo (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.21 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.5% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (12.5%), [🔴 MISS] 1-0 (12.3%)

### 2026-07-30: Austria Vienna vs FK Liepaja (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (14.3%), [🔴 MISS] 3-0 (13.2%)


## Unmatched result examples

- none

## Ambiguous result examples

- none

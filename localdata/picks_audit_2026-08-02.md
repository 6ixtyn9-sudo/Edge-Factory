# Edge Factory — Recent picks audit (2026-07-04 to 2026-08-02)

## Overall

- archived pick rows: 65
- archived pick dates: 20
- settled picks: 59
- eligible prior 1x2 picks: 59
- unmatched result picks: 0
- ambiguous result picks: 0
- wins: 51
- hit rate: 0.864407
- priced picks: 59
- ROI: 0.124831

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-02
- same-day rows excluded: 6

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 40 / 59 matches (67.8%)
- **Both Teams to Score (BTTS)**: occurred in 29 / 59 matches (49.2%)
- **Selected Team Over 1.5 Goals**: occurred in 48 / 59 matches (81.4%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 15
- **Total Hits**: 10
- **Overall Hit Rate**: 66.7%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `goal_range_2_3`: recommended=1, hits=0, hit_rate=0.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=1, hits=0, hit_rate=0.0%
- `match_over_25`: recommended=7, hits=4, hit_rate=57.1%

## By rule

- `2way-unanimous avg_p>=70`: settled=19, wins=18, hit_rate=0.947368, ROI=0.297368
- `3way-unanimous avg_p>=65`: settled=16, wins=12, hit_rate=0.75, ROI=-0.049063
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.176667
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=6, wins=5, hit_rate=0.833333, ROI=0.493333
- `SKIPPED_VETO`: settled=42, wins=37, hit_rate=0.880952, ROI=0.117738
- `WATCHLIST_UNKNOWN_CTX`: settled=11, wins=9, hit_rate=0.818182, ROI=-0.049091

## By odds source

- `betexplorer_odds`: settled=36, wins=32, hit_rate=0.888889, ROI=0.134722
- `bzzoiro_odds`: settled=15, wins=14, hit_rate=0.933333, ROI=0.287
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=6, wins=4, hit_rate=0.666667, ROI=-0.168333

## By odds match method

- `alias_fuzzy`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.183333
- `betexplorer`: settled=36, wins=32, hit_rate=0.888889, ROI=0.134722
- `exact`: settled=18, wins=16, hit_rate=0.888889, ROI=0.213611
- `fallback`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-01: Universitatea Craiova vs Petrolul Ploiesti (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 72.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.6% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (14.6%), [🔴 MISS] 2-0 (12.8%)

### 2026-08-01: Gandzasar vs Ararat-Armenia (Actual Score: **3-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.39 -> 🟢 WON (Expected prob: 69.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 32.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 92.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.4% (Actual: 4 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (18.1%), [🔴 MISS] 0-1 (16.6%)

### 2026-08-01: Cruzeiro W vs Botafogo W (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 74.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.8%), [🔴 MISS] 1-0 (12.6%)

### 2026-08-01: Volna Nizhegorodskaya vs Arsenal-2 Tula (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 69.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (15.3%), [🔴 MISS] 3-0 (13.4%)

### 2026-08-01: Monaro Panthers vs O'Connor Knights (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.09 -> 🔴 LOST (Expected prob: 69.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (15.3%), [🔴 MISS] 3-0 (13.4%)


## Unmatched result examples

- none

## Ambiguous result examples

- none

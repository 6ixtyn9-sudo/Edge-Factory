# Edge Factory — Recent picks audit (2026-07-03 to 2026-08-01)

## Overall

- archived pick rows: 59
- archived pick dates: 19
- settled picks: 54
- eligible prior 1x2 picks: 54
- unmatched result picks: 0
- ambiguous result picks: 0
- wins: 47
- hit rate: 0.87037
- priced picks: 54
- ROI: 0.129352

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-01
- same-day rows excluded: 5

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 37 / 54 matches (68.5%)
- **Both Teams to Score (BTTS)**: occurred in 27 / 54 matches (50.0%)
- **Selected Team Over 1.5 Goals**: occurred in 44 / 54 matches (81.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 10
- **Total Hits**: 8
- **Overall Hit Rate**: 80.0%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_25`: recommended=4, hits=2, hit_rate=50.0%

## By rule

- `2way-unanimous avg_p>=70`: settled=18, wins=17, hit_rate=0.944444, ROI=0.301667
- `3way-unanimous avg_p>=65`: settled=12, wins=9, hit_rate=0.75, ROI=-0.07875
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.176667
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=6, wins=5, hit_rate=0.833333, ROI=0.493333
- `SKIPPED_VETO`: settled=40, wins=35, hit_rate=0.875, ROI=0.100125
- `WATCHLIST_UNKNOWN_CTX`: settled=8, wins=7, hit_rate=0.875, ROI=0.0025

## By odds source

- `betexplorer_odds`: settled=34, wins=30, hit_rate=0.882353, ROI=0.124706
- `bzzoiro_odds`: settled=14, wins=13, hit_rate=0.928571, ROI=0.268214
- `forebet_best`: settled=1, wins=1, hit_rate=1.0, ROI=0.22
- `scoutingstats_odds`: settled=5, wins=3, hit_rate=0.6, ROI=-0.246

## By odds match method

- `alias_fuzzy`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.183333
- `betexplorer`: settled=34, wins=30, hit_rate=0.882353, ROI=0.124706
- `exact`: settled=16, wins=14, hit_rate=0.875, ROI=0.192187
- `fallback`: settled=1, wins=1, hit_rate=1.0, ROI=0.22
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-07-31: Dinamo Zagreb vs Slaven Belupo (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 77.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (12.7%), [🔴 MISS] 3-0 (11.6%)

### 2026-07-31: Sparta Praha vs Zlin (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.23 -> 🟢 WON (Expected prob: 76.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (14.4%), [🟢 HIT] 3-1 (10.5%)

### 2026-07-31: Finn Harps vs Cork City (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.37 -> 🟢 WON (Expected prob: 68.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.7% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (20.3%), [🔴 MISS] 0-1 (15.3%)

### 2026-07-31: Dundee Utd vs Rangers (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.65 -> 🔴 LOST (Expected prob: 65.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.5% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.3% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (18.8%), [🔴 MISS] 0-1 (13.7%)


## Unmatched result examples

- none

## Ambiguous result examples

- none

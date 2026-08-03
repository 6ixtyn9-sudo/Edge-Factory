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
- **Total Hits**: 16
- **Overall Hit Rate**: 66.7%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `goal_range_2_3`: recommended=4, hits=1, hit_rate=25.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=5, hits=4, hit_rate=80.0%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **212** | scored: 212

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 21 | 21 | 20 | 95.2% | 95.4% | -0.2% | 0.04387 |
| `goal_range_2_3` | 19 | 19 | 7 | 36.8% | 46.2% | -9.3% | 0.238706 |
| `btts_yes` | 17 | 17 | 7 | 41.2% | 52.5% | -11.3% | 0.24082 |
| `exact_2` | 17 | 17 | 4 | 23.5% | 24.6% | -1.1% | 0.182352 |
| `match_over_25` | 15 | 15 | 9 | 60.0% | 56.8% | +3.2% | 0.297849 |
| `away_under_25` | 14 | 14 | 13 | 92.9% | 88.4% | +4.5% | 0.06791 |
| `exact_4` | 13 | 13 | 5 | 38.5% | 17.0% | +21.5% | 0.285153 |
| `match_over_35` | 12 | 12 | 7 | 58.3% | 40.3% | +18.1% | 0.308884 |
| `goal_range_4_6` | 11 | 11 | 5 | 45.5% | 35.3% | +10.1% | 0.263665 |
| `exact_3` | 10 | 10 | 0 | 0.0% | 22.3% | -22.3% | 0.049515 |
| `home_over_05` | 10 | 10 | 10 | 100.0% | 83.3% | +16.7% | 0.028759 |
| `home_under_35` | 9 | 9 | 6 | 66.7% | 94.3% | -27.6% | 0.295675 |
| `goal_range_4_5` | 7 | 7 | 4 | 57.1% | 31.2% | +26.0% | 0.330817 |
| `exact_5` | 6 | 6 | 1 | 16.7% | 13.6% | +3.1% | 0.150536 |
| `match_over_15` | 6 | 6 | 5 | 83.3% | 86.8% | -3.5% | 0.153114 |
| `match_over_45` | 6 | 6 | 1 | 16.7% | 30.6% | -13.9% | 0.205088 |
| `btts_no` | 5 | 5 | 3 | 60.0% | 57.6% | +2.4% | 0.230294 |
| `exact_1` | 3 | 3 | 1 | 33.3% | 21.8% | +11.6% | 0.219319 ⚠️low-n |
| `away_over_05` | 2 | 2 | 1 | 50.0% | 83.2% | -33.2% | 0.367464 ⚠️low-n |
| `goal_range_6_plus` | 2 | 2 | 0 | 0.0% | 27.1% | -27.1% | 0.075286 ⚠️low-n |
| `goal_range_7_plus` | 2 | 2 | 0 | 0.0% | 15.1% | -15.1% | 0.023681 ⚠️low-n |
| `home_under_25` | 2 | 2 | 1 | 50.0% | 87.3% | -37.3% | 0.409172 ⚠️low-n |
| `away_under_15` | 1 | 1 | 1 | 100.0% | 81.9% | +18.1% | 0.032593 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels reading "Win + …" (`match_over_15`, `match_over_25`, `btts_yes`) are cosmetic: promised %, captured price and scoring are all plain-market (FIX-2). Cosmetic label cleanup is queued for the hardening pass.

### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 23 | 15.8% | 30.4% | +14.7% |
| 0.2-0.3 | 41 | 24.5% | 22.0% | -2.5% |
| 0.3-0.4 | 20 | 34.1% | 60.0% | +25.9% |
| 0.4-0.5 | 32 | 46.0% | 40.6% | -5.4% |
| 0.5-0.6 | 23 | 53.9% | 34.8% | -19.1% |
| 0.6-0.7 | 4 | 66.6% | 100.0% | +33.4% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 28 | 84.7% | 89.3% | +4.6% |
| 0.9-1.0 | 37 | 94.5% | 86.5% | -8.0% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=24, MAE=1.094167 goals, bias=-0.406667 (realized − promised), promised avg 3.781667 vs realized 3.375

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 48 | 14.0% | 10.4% | -3.6% | 0.097298 |
| Away Over 1.5 | 24 | 19.0% | 16.7% | -2.3% | 0.108031 |
| BTTS-Yes | 24 | 40.2% | 37.5% | -2.7% | 0.24031 |
| Home Over 1.5 | 24 | 78.6% | 70.8% | -7.7% | 0.215266 |
| Over 2.5 | 24 | 73.4% | 70.8% | -2.6% | 0.208913 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 16 | 9.1% | 12.5% | +3.4% |
| 0.1-0.2 | 55 | 13.4% | 10.9% | -2.4% |
| 0.2-0.3 | 1 | 20.3% | 0.0% | -20.3% |
| 0.3-0.4 | 13 | 38.2% | 46.2% | +8.0% |
| 0.4-0.5 | 11 | 42.7% | 27.3% | -15.4% |
| 0.6-0.7 | 4 | 66.8% | 75.0% | +8.2% |
| 0.7-0.8 | 20 | 74.7% | 70.0% | -4.7% |
| 0.8-0.9 | 16 | 86.8% | 87.5% | +0.7% |
| 0.9-1.0 | 8 | 90.8% | 50.0% | -40.8% |

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
  - **🔥 Possible Events (graded)**: [🟢 HIT] Goal Range 2-3 (47.0%), [🔴 MISS] Home Win + BTTS (Yes) (52.0%), [🟢 HIT] Home Team Under 3.5 Goals (95.0%), [🟢 HIT] Away Team Under 3.5 Goals (95.0%), [🔴 MISS] Exact Goals: 2 (25.7%), [🔴 MISS] Exact Goals: 1 (20.5%)

### 2026-08-02: Dinamo Brest vs Belshina (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.32 -> 🟢 WON (Expected prob: 75.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.0%), [🔴 MISS] 3-0 (11.8%)
  - **🔥 Possible Events (graded)**: [🟢 HIT] Home Win + Over 1.5 (88.6%), [🟢 HIT] Home Win + Over 2.5 (74.2%), [🟢 HIT] Goal Range 4-6 (49.2%), [🟢 HIT] Match Over 3.5 Goals (67.5%), [🟢 HIT] Both Teams to Score - No (BTTS-No) (66.8%), [🔴 MISS] Match Over 4.5 Goals (48.7%), [🟢 HIT] Goal Range 4-5 (36.0%), [🔴 MISS] Goal Range 6+ (31.5%), [🟢 HIT] Exact Goals: 4 (18.7%), [🔴 MISS] Goal Range 7+ (18.2%), [🔴 MISS] Exact Goals: 5 (17.3%)

### 2026-08-02: Kongsvinger vs Strommen (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 75.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.0%), [🔴 MISS] 3-0 (11.8%)
  - **🔥 Possible Events (graded)**: [🟢 HIT] Home Win + Over 1.5 (86.8%), [🟢 HIT] Home Win + Over 2.5 (68.1%), [🟢 HIT] Home Win + BTTS (Yes) (64.1%), [🟢 HIT] Home Team Over 0.5 Goals (85.3%), [🟢 HIT] Match Over 3.5 Goals (39.6%), [🟢 HIT] Away Team Under 3.5 Goals (91.8%), [🔴 MISS] Goal Range 2-3 (43.2%), [🟢 HIT] Goal Range 4-6 (35.1%), [🟢 HIT] Goal Range 4-5 (29.1%), [🔴 MISS] Exact Goals: 3 (22.3%), [🔴 MISS] Match Over 4.5 Goals (21.8%), [🟢 HIT] Exact Goals: 4 (17.8%), [🔴 MISS] Exact Goals: 5 (11.3%)

### 2026-08-02: Noah vs Syunik (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.31 -> 🟢 WON (Expected prob: 68.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.3%), [🟢 HIT] 3-0 (12.9%)
  - **🔥 Possible Events (graded)**: [🟢 HIT] Home Win + Over 1.5 (80.8%), [🔴 MISS] Home Win + BTTS (Yes) (51.7%), [🔴 MISS] Away Team Over 0.5 Goals (83.9%), [🟢 HIT] Home Team Over 0.5 Goals (80.8%), [🔴 MISS] Match Over 3.5 Goals (45.4%), [🔴 MISS] Goal Range 4-6 (39.2%), [🟢 HIT] Home Win + Over 2.5 (37.3%), [🔴 MISS] Goal Range 4-5 (31.7%), [🔴 MISS] Match Over 4.5 Goals (26.7%), [🔴 MISS] Exact Goals: 4 (18.8%), [🔴 MISS] Exact Goals: 5 (13.0%)

### 2026-08-02: Independiente del Valle vs Deportivo Cuenca (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 80.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 92.2% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (19.6%), [🔴 MISS] 3-1 (14.5%)
  - **🔥 Possible Events (graded)**: [🔴 MISS] Goal Range 2-3 (46.5%), [🟢 HIT] Away Team Under 3.5 Goals (98.1%), [🟢 HIT] Home Team Under 3.5 Goals (95.3%), [🟢 HIT] Away Team Under 2.5 Goals (93.8%), [🟢 HIT] Away Team Under 1.5 Goals (81.9%), [🟢 HIT] Both Teams to Score - No (BTTS-No) (58.1%), [🔴 MISS] Home Win + BTTS (Yes) (41.9%), [🟢 HIT] Goal Range 0-1 (35.2%), [🔴 MISS] Exact Goals: 2 (26.8%), [🟢 HIT] Exact Goals: 1 (24.3%), [🔴 MISS] Exact Goals: 0 (11.0%)

### 2026-08-02: Ludogorets vs Botev Vratsa (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 69.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (15.0%), [🔴 MISS] 3-0 (13.8%)
  - **🔥 Possible Events (graded)**: [🟢 HIT] Home Win + Over 2.5 (48.5%), [🟢 HIT] Goal Range 2-3 (46.9%), [🟢 HIT] Away Team Under 3.5 Goals (97.5%), [🟢 HIT] Away Team Under 2.5 Goals (91.5%), [🔴 MISS] Both Teams to Score - No (BTTS-No) (56.1%), [🟢 HIT] Home Win + BTTS (Yes) (43.9%), [🔴 MISS] Exact Goals: 2 (25.2%)

### 2026-08-02: ODD Ballklubb vs Asane (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 68.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.4%), [🔴 MISS] 3-0 (13.1%)
  - **🔥 Possible Events (graded)**: [🔴 MISS] Goal Range 2-3 (47.0%), [🟢 HIT] Home Win + BTTS (Yes) (52.0%), [🔴 MISS] Home Team Under 3.5 Goals (95.0%), [🟢 HIT] Away Team Under 3.5 Goals (95.0%), [🔴 MISS] Exact Goals: 2 (25.7%), [🔴 MISS] Exact Goals: 1 (20.5%)

### 2026-08-02: Dunajska Streda vs Dukla Banska Bystrica (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (13.5%), [🔴 MISS] 3-0 (13.3%)
  - **🔥 Possible Events (graded)**: [🔴 MISS] Home Win + Over 2.5 (56.3%), [🟢 HIT] Goal Range 2-3 (46.5%), [🔴 MISS] Home Win + BTTS (Yes) (54.1%), [🟢 HIT] Home Team Under 3.5 Goals (94.7%), [🟢 HIT] Away Team Under 3.5 Goals (94.6%), [🟢 HIT] Away Team Under 2.5 Goals (85.1%), [🟢 HIT] Exact Goals: 2 (24.4%), [🔴 MISS] Exact Goals: 3 (22.1%)

### 2026-08-02: Clarence Zebras vs Ulverstone (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.23 -> 🟢 WON (Expected prob: 75.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.0%), [🔴 MISS] 3-0 (11.8%)
  - **🔥 Possible Events (graded)**: [🔴 MISS] Home Win + Over 1.5 (90.1%), [🔴 MISS] Home Win + Over 2.5 (74.0%), [🔴 MISS] Home Win + BTTS (Yes) (53.9%), [🟢 HIT] Home Team Over 0.5 Goals (82.1%), [🔴 MISS] Match Over 3.5 Goals (47.2%), [🟢 HIT] Away Team Under 3.5 Goals (91.5%), [🟢 HIT] Away Team Under 2.5 Goals (86.6%), [🔴 MISS] Goal Range 4-6 (40.4%), [🔴 MISS] Goal Range 4-5 (32.4%), [🔴 MISS] Match Over 4.5 Goals (28.2%), [🔴 MISS] Exact Goals: 4 (19.0%), [🔴 MISS] Exact Goals: 5 (13.4%)


## Unmatched result examples

- none

## Ambiguous result examples

- none

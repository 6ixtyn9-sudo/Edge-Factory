# Edge Factory — Recent picks audit (2026-07-06 to 2026-08-04)

## Overall

- archived pick rows: 92
- archived pick dates: 26
- settled picks: 88
- eligible prior 1x2 picks: 90
- unmatched result picks: 2
- ambiguous result picks: 0
- wins: 69
- hit rate: 0.784091
- priced picks: 85
- ROI: 0.050765

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-04
- same-day rows excluded: 2

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 62 / 88 matches (70.5%)
- **Both Teams to Score (BTTS)**: occurred in 46 / 88 matches (52.3%)
- **Selected Team Over 1.5 Goals**: occurred in 67 / 88 matches (76.1%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 29
- **Total Hits**: 18
- **Overall Hit Rate**: 62.1%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `btts_yes`: recommended=2, hits=1, hit_rate=50.0%
- `goal_range_2_3`: recommended=8, hits=2, hit_rate=25.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=4, hits=4, hit_rate=100.0%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **251** | scored: 251

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 25 | 25 | 24 | 96.0% | 95.5% | +0.5% | 0.037097 |
| `goal_range_2_3` | 25 | 25 | 8 | 32.0% | 46.1% | -14.1% | 0.234496 |
| `btts_yes` | 22 | 22 | 10 | 45.5% | 52.4% | -6.9% | 0.235481 |
| `exact_2` | 22 | 22 | 5 | 22.7% | 24.6% | -1.8% | 0.17663 |
| `away_under_25` | 16 | 16 | 15 | 93.8% | 88.3% | +5.4% | 0.061203 |
| `exact_4` | 15 | 15 | 6 | 40.0% | 16.7% | +23.3% | 0.296699 |
| `exact_3` | 14 | 14 | 0 | 0.0% | 22.2% | -22.2% | 0.049487 |
| `match_over_25` | 14 | 14 | 9 | 64.3% | 55.6% | +8.7% | 0.28006 |
| `home_under_35` | 13 | 13 | 10 | 76.9% | 93.7% | -16.8% | 0.206569 |
| `match_over_35` | 13 | 13 | 8 | 61.5% | 39.1% | +22.4% | 0.31135 |
| `goal_range_4_6` | 12 | 12 | 6 | 50.0% | 34.5% | +15.5% | 0.276418 |
| `home_over_05` | 11 | 11 | 11 | 100.0% | 84.0% | +16.0% | 0.026541 |
| `goal_range_4_5` | 8 | 8 | 4 | 50.0% | 30.1% | +19.9% | 0.295245 |
| `btts_no` | 7 | 7 | 4 | 57.1% | 56.0% | +1.1% | 0.230831 |
| `exact_5` | 7 | 7 | 1 | 14.3% | 12.7% | +1.6% | 0.129561 |
| `match_over_45` | 7 | 7 | 2 | 28.6% | 27.7% | +0.8% | 0.265591 |
| `match_over_15` | 5 | 5 | 5 | 100.0% | 86.2% | +13.8% | 0.021197 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `away_over_05` | 2 | 2 | 1 | 50.0% | 83.2% | -33.2% | 0.367464 ⚠️low-n |
| `goal_range_6_plus` | 2 | 2 | 0 | 0.0% | 27.1% | -27.1% | 0.075286 ⚠️low-n |
| `goal_range_7_plus` | 2 | 2 | 0 | 0.0% | 15.1% | -15.1% | 0.023681 ⚠️low-n |
| `home_under_25` | 2 | 2 | 1 | 50.0% | 87.3% | -37.3% | 0.409172 ⚠️low-n |
| `away_under_15` | 1 | 1 | 1 | 100.0% | 81.9% | +18.1% | 0.032593 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored (FIX-2 + label honesty, Addendum 16): `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor (Addendum 17) · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| legacy | 251 | 133 | 53.0% | 52.0% | +1.0% | 0.183294 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 27 | 15.5% | 33.3% | +17.8% |
| 0.2-0.3 | 53 | 24.2% | 18.9% | -5.3% |
| 0.3-0.4 | 23 | 34.2% | 60.9% | +26.6% |
| 0.4-0.5 | 38 | 46.2% | 39.5% | -6.8% |
| 0.5-0.6 | 27 | 53.6% | 37.0% | -16.6% |
| 0.6-0.7 | 5 | 65.3% | 100.0% | +34.7% |
| 0.7-0.8 | 3 | 74.5% | 66.7% | -7.9% |
| 0.8-0.9 | 31 | 85.1% | 90.3% | +5.2% |
| 0.9-1.0 | 44 | 94.5% | 90.9% | -3.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=29, MAE=1.20931 goals, bias=-0.345172 (realized − promised), promised avg 3.758966 vs realized 3.413793

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 58 | 14.4% | 8.6% | -5.8% | 0.085154 |
| Away Over 1.5 | 29 | 22.7% | 24.1% | +1.4% | 0.172289 |
| BTTS-Yes | 29 | 39.5% | 41.4% | +1.9% | 0.242218 |
| Home Over 1.5 | 29 | 74.3% | 69.0% | -5.3% | 0.180408 |
| Over 2.5 | 29 | 73.1% | 69.0% | -4.1% | 0.221169 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 19 | 8.5% | 15.8% | +7.3% |
| 0.1-0.2 | 66 | 13.6% | 10.6% | -3.0% |
| 0.2-0.3 | 2 | 21.1% | 0.0% | -21.1% |
| 0.3-0.4 | 19 | 37.8% | 47.4% | +9.6% |
| 0.4-0.5 | 10 | 42.6% | 30.0% | -12.6% |
| 0.6-0.7 | 6 | 67.3% | 83.3% | +16.0% |
| 0.7-0.8 | 22 | 74.3% | 68.2% | -6.1% |
| 0.8-0.9 | 22 | 86.6% | 81.8% | -4.8% |
| 0.9-1.0 | 8 | 90.8% | 50.0% | -40.8% |

## By rule

- `2way-unanimous avg_p>=70`: settled=37, wins=28, hit_rate=0.756757, ROI=0.078824
- `3way-unanimous avg_p>=65`: settled=27, wins=20, hit_rate=0.740741, ROI=-0.032037
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.176667
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=21, wins=12, hit_rate=0.571429, ROI=-0.071429
- `SKIPPED_VETO`: settled=52, wins=45, hit_rate=0.865385, ROI=0.117981
- `WATCHLIST_NO_ODDS`: settled=3, wins=2, hit_rate=0.666667, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=12, wins=10, hit_rate=0.833333, ROI=-0.026667

## By odds source

- `UNKNOWN`: settled=3, wins=2, hit_rate=0.666667, ROI=None
- `betexplorer_odds`: settled=44, wins=38, hit_rate=0.863636, ROI=0.116136
- `bzzoiro_odds`: settled=24, wins=20, hit_rate=0.833333, ROI=0.167292
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=12, wins=6, hit_rate=0.5, ROI=-0.331667
- `zulubet`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.016667

## By odds match method

- `alias_fuzzy`: settled=6, wins=3, hit_rate=0.5, ROI=-0.356667
- `betexplorer`: settled=44, wins=38, hit_rate=0.863636, ROI=0.116136
- `exact`: settled=30, wins=23, hit_rate=0.766667, ROI=0.0725
- `fallback`: settled=5, wins=3, hit_rate=0.6, ROI=-0.166
- `none`: settled=3, wins=2, hit_rate=0.666667, ROI=None
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-03: FCSB vs Farul Constanta (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.81 -> 🔴 LOST (Expected prob: 66.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.9%), [🔴 MISS] 1-0 (14.3%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Goal Range 2-3**: expected 46.4% (Actual: 4 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 53.8% (Actual: BTTS-Yes)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.2% (Actual: 2 home goals)
    - [🔴 MISS] **Exact Goals: 2**: expected 24.3% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.1% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 15.1% (Actual: 4 goals)

### 2026-08-03: Halmstad vs Sirius (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.41 -> 🟢 WON (Expected prob: 79.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 81.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 32.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 89.0% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 0-3 (22.0%), [🔴 MISS] 1-2 (11.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Goal Range 2-3**: expected 47.0% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 52.0% (Actual: BTTS-No)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.0% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.0% (Actual: 2 away goals)
    - [🟢 HIT] **Exact Goals: 2**: expected 25.7% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 1**: expected 20.5% (Actual: 2 goals)

### 2026-08-03: Transinvest 2 vs Babrungas (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.19 -> 🟢 WON (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.3% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 87.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 0-3 (13.6%), [🔴 MISS] 1-2 (13.4%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Goal Range 2-3**: expected 46.9% (Actual: 1 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.1% (Actual: BTTS-No)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.6% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.0% (Actual: 1 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 53.9% (Actual: BTTS-No)
    - [🔴 MISS] **Exact Goals: 2**: expected 25.2% (Actual: 1 goals)

### 2026-08-03: Cork City vs Athlone Town (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 69.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (15.0%), [🔴 MISS] 3-0 (13.8%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Goal Range 2-3**: expected 46.6% (Actual: 5 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.6% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.7% (Actual: 2 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 50.1% (Actual: BTTS-Yes)
    - [🔴 MISS] **Exact Goals: 2**: expected 24.5% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.0% (Actual: 5 goals)

### 2026-08-03: Hammarby Talang vs Arlanda (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.3%), [🔴 MISS] 1-0 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 60.1% (Actual: BTTS-Yes)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.6% (Actual: 5 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.1% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.1% (Actual: 1 away goals)
    - [🔴 MISS] **Goal Range 2-3**: expected 44.9% (Actual: 6 goals)
    - [🟢 HIT] **Goal Range 4-6**: expected 31.8% (Actual: 6 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 26.8% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 2**: expected 22.5% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.4% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.3% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 16.8% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 10.0% (Actual: 6 goals)

### 2026-08-03: Celtic vs Dundee (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 80.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 92.6% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (18.5%), [🔴 MISS] 3-1 (14.8%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 51.9% (Actual: BTTS-No)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.5% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 37.8% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.9% (Actual: 0 away goals)
    - [🔴 MISS] **Goal Range 2-3**: expected 43.9% (Actual: 1 goals)
    - [🔴 MISS] **Goal Range 4-6**: expected 33.8% (Actual: 1 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 28.2% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.4% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 17.4% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 10.8% (Actual: 1 goals)


## Unmatched result examples

- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — South Hobart vs Ulverstone -> HOME @ 1.02 (unmatched_result); keys=['southhoba']/['ulverston']
- 2026-08-02 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous avg_p>=70` — Clarence Zebras vs Ulverstone -> HOME @ 1.23 (unmatched_result); keys=['clarencez']/['ulverston']

## Ambiguous result examples

- none

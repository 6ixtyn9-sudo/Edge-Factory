# Edge Factory — Recent picks audit (2026-09-03 to 2026-10-02)

## Overall

- archived pick rows: 593
- archived pick dates: 30
- immutable morning-baseline rows: 593
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 28
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 569
- eligible prior picks: 589
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 1
- ambiguous result picks: 3
- wins: 384
- hit rate: +67.5%
- priced picks: 525
- ROI: -3.5%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-02
- same-day rows excluded: 4

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 334 / 539 matches (62.0%)
- **Both Teams to Score (BTTS)**: occurred in 299 / 539 matches (55.5%)
- **Selected Team Over 1.5 Goals**: occurred in 353 / 539 matches (65.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 569
- **Total Hits**: 451
- **Overall Hit Rate**: 79.3%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=19, hits=17, hit_rate=89.5%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=158, hits=153, hit_rate=96.8%
- `home_over_05`: recommended=24, hits=17, hit_rate=70.8%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=30, hits=29, hit_rate=96.7%
- `match_over_15`: recommended=33, hits=24, hit_rate=72.7%
- `match_over_25`: recommended=230, hits=149, hit_rate=64.8%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2262** | scored: 2262

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 564 | 564 | 349 | 61.9% | 45.1% | +16.8% | 0.263144 |
| `match_over_45` | 444 | 444 | 118 | 26.6% | 23.8% | +2.8% | 0.191377 |
| `away_under_35` | 395 | 395 | 384 | 97.2% | 95.9% | +1.3% | 0.027092 |
| `away_under_25` | 361 | 361 | 329 | 91.1% | 91.9% | -0.7% | 0.080912 |
| `home_under_35` | 159 | 159 | 155 | 97.5% | 93.9% | +3.6% | 0.026689 |
| `home_under_25` | 133 | 133 | 124 | 93.2% | 90.5% | +2.7% | 0.06345 |
| `home_over_05` | 80 | 80 | 70 | 87.5% | 83.2% | +4.3% | 0.109471 |
| `away_over_05` | 33 | 33 | 30 | 90.9% | 87.8% | +3.1% | 0.083325 |
| `match_over_15` | 33 | 33 | 24 | 72.7% | 84.4% | -11.7% | 0.213961 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `home_under_15` | 13 | 13 | 9 | 69.2% | 81.6% | -12.3% | 0.232124 |
| `away_under_15` | 11 | 11 | 9 | 81.8% | 82.9% | -1.1% | 0.158576 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2068 | 1485 | 71.8% | 66.5% | +5.3% | 0.137169 |
| model | 194 | 133 | 68.6% | 62.8% | +5.7% | 0.182275 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 108 | 19.2% | 17.6% | -1.6% |
| 0.2-0.3 | 291 | 24.2% | 26.8% | +2.6% |
| 0.3-0.4 | 81 | 33.5% | 51.9% | +18.4% |
| 0.4-0.5 | 492 | 44.4% | 60.6% | +16.2% |
| 0.5-0.6 | 69 | 51.9% | 65.2% | +13.3% |
| 0.8-0.9 | 305 | 85.7% | 86.9% | +1.1% |
| 0.9-1.0 | 916 | 94.4% | 95.1% | +0.7% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=538, MAE=1.58381 goals, bias=-0.232621 (realized − promised), promised avg 3.517007 vs realized 3.284387

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 538 | 31.3% | 34.8% | +3.5% | 0.222648 |
| BTTS-Yes | 538 | 41.7% | 55.4% | +13.7% | 0.26504 |
| Home Over 1.5 | 538 | 63.6% | 54.5% | -9.1% | 0.242175 |
| Over 2.5 | 538 | 69.5% | 61.9% | -7.6% | 0.241524 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 223 | 8.7% | 23.3% | +14.7% |
| 0.1-0.2 | 318 | 10.4% | 24.5% | +14.1% |
| 0.2-0.3 | 4 | 26.1% | 75.0% | +48.9% |
| 0.3-0.4 | 96 | 37.3% | 50.0% | +12.7% |
| 0.4-0.5 | 434 | 42.9% | 56.5% | +13.5% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 373 | 66.9% | 60.3% | -6.6% |
| 0.7-0.8 | 147 | 74.4% | 65.3% | -9.1% |
| 0.8-0.9 | 511 | 84.5% | 65.2% | -19.3% |
| 0.9-1.0 | 45 | 92.6% | 68.9% | -23.7% |

## By rule

- `2way-unanimous avg_p>=60`: settled=89, wins=58, hit_rate=0.651685, ROI=-0.122933
- `2way-unanimous avg_p>=70`: settled=81, wins=61, hit_rate=0.753086, ROI=-0.040937
- `ml-meta avg_p>=55`: settled=300, wins=188, hit_rate=0.626667, ROI=-0.038201
- `ml-meta avg_p>=60`: settled=49, wins=42, hit_rate=0.857143, ROI=0.180204
- `ml-meta avg_p>=65`: settled=12, wins=10, hit_rate=0.833333, ROI=0.029091
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=5, wins=5, hit_rate=1.0, ROI=0.07
- `ou25-unanimous-2way-sa avg_p>=70`: settled=30, wins=18, hit_rate=0.6, ROI=-0.153103

## By bucket

- `CAUTION`: settled=49, wins=30, hit_rate=0.612245, ROI=-0.044694
- `CERTIFIED_CLEAN`: settled=58, wins=41, hit_rate=0.706897, ROI=0.105345
- `SKIPPED_VETO`: settled=279, wins=185, hit_rate=0.663082, ROI=-0.081784
- `WATCHLIST_NO_ODDS`: settled=32, wins=24, hit_rate=0.75, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=14, wins=9, hit_rate=0.642857, ROI=0.074167
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=133, wins=92, hit_rate=0.691729, ROI=-0.008346
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=44, wins=33, hit_rate=0.75, ROI=None
- `betexplorer_odds`: settled=169, wins=113, hit_rate=0.668639, ROI=-0.044438
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=75, wins=53, hit_rate=0.706667, ROI=0.056933
- `scoutingstats_odds`: settled=271, wins=176, hit_rate=0.649446, ROI=-0.067232
- `zulubet`: settled=2, wins=2, hit_rate=1.0, ROI=0.335

## By odds match method

- `alias_fuzzy`: settled=22, wins=15, hit_rate=0.681818, ROI=0.014211
- `betexplorer`: settled=169, wins=113, hit_rate=0.668639, ROI=-0.044438
- `exact`: settled=279, wins=183, hit_rate=0.655914, ROI=-0.057527
- `fallback`: settled=58, wins=42, hit_rate=0.724138, ROI=0.080517
- `none`: settled=41, wins=31, hit_rate=0.756098, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 169 | 113 | 0.668639 | 169 | -0.044438 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 271 | 176 | 0.649446 | 271 | -0.067232 |
| Source fallback (`SOURCE_FALLBACK`) | 58 | 42 | 0.724138 | 58 | 0.080517 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 22 | 15 | 0.681818 | 19 | 0.014211 |
| No usable price (`UNMATCHED`) | 41 | 31 | 0.756098 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 279 | 185 | 0.663082 | 269 | -0.081784 |
| **trusted evidence only** | 100 | 69 | 0.69 | 100 | -0.0656 |
| **soft evidence only** | 179 | 116 | 0.648045 | 169 | -0.091361 |
| evidence: BETEXPLORER_RESCUE | 95 | 64 | 0.673684 | 95 | -0.090316 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: SCOUTINGSTATS_SOLE | 138 | 84 | 0.608696 | 138 | -0.123986 |
| evidence: SOURCE_FALLBACK | 24 | 19 | 0.791667 | 24 | 0.095417 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.088571 |
| evidence: UNMATCHED | 9 | 7 | 0.777778 | 0 | None |
| odds band: <1.50 | 168 | 127 | 0.755952 | 168 | -0.042738 |
| odds band: 1.50-2.00 | 95 | 46 | 0.484211 | 95 | -0.183895 |
| odds band: 2.00-3.00 | 6 | 4 | 0.666667 | 6 | 0.441667 |
| odds band: unpriced | 10 | 8 | 0.8 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.29 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.4 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.49 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 14 | 10 | 0.714286 | 14 | -0.047857 |
| veto reason: context VETO in ['league'] | 22 | 16 | 0.727273 | 17 | 0.032353 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 63 | 44 | 0.698413 | 63 | -0.103016 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.085 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 8 | 0.727273 | 11 | -0.129091 |
| veto reason: context VETO in ['team_a'] | 46 | 25 | 0.543478 | 44 | -0.173182 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.128571 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.218 |
| veto reason: context VETO in ['team_h', 'team_a'] | 12 | 6 | 0.5 | 12 | -0.154167 |
| veto reason: context VETO in ['team_h'] | 52 | 34 | 0.653846 | 50 | -0.0174 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 30 | 19 | 0.633333 | 30 | -0.030667 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 18 | 11 | 0.611111 | 18 | -0.015 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 276 | 193 | 0.699275 | 235 | -0.002851 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 22 | 15 | 0.681818 | 19 | 0.014211 | 22 | 1.589545 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 271 | 176 | 0.649446 | 271 | -0.067232 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-01: Miami FC vs Sporting JAX (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.73 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.8% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 86.6% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 31.0% (Actual: 5 goals)

### 2026-10-01: Atlético Ottawa vs Cavalry FC (Actual Score: **3-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.71 -> 🔴 LOST (Expected prob: 73.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 34.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 94.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.4% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.1% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 87.2% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.6% (Actual: 5 goals)

### 2026-10-01: Brooklyn vs Detroit City (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 2.05 -> 🟢 WON (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.4% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.2% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.5% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.2% (Actual: 4 goals)

### 2026-10-01: Wales vs Norway (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🔴 LOST (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 82.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.7% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.8% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.1% (Actual: 3 goals)

### 2026-10-01: Atletico Nacional vs Junior (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 59.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.8% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.2% (Actual: 4 goals)

### 2026-10-01: Argentina vs Bolivia (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.07 -> 🟢 WON (Expected prob: 82.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 36.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 95.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.9% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.8% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.9% (Actual: 4 goals)

### 2026-10-01: Germany vs Serbia (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 77.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.8% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 33.0% (Actual: 2 goals)

### 2026-10-01: Bnei Yehuda vs Maccabi Kiryat Gat (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.0% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.4% (Actual: 3 goals)

### 2026-10-01: Malta vs Gibraltar (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🔴 LOST (Expected prob: 71.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 51.3% (Actual: 2 goals)

### 2026-10-01: Maccabi Kabilio Jaffa vs Hapoel Acre (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 64.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.2% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 82.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.5% (Actual: 1 goals)

### 2026-10-01: Azerbaijan vs Liechtenstein (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.12 -> 🔴 LOST (Expected prob: 84.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 88.9% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 48.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 96.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 92.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.7% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 38.0% (Actual: 0 goals)

### 2026-10-01: Sacramento Republic vs Las Vegas Lights FC (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🟢 WON (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.8% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 83.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 5 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 3-3 Go Ahead Eagles [draw])
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])
- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova FC 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca W 4-1 Santos Laguna W [home])

## Pending / Unmatched Result Examples

- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-26 `SKIPPED_VETO` `ml-meta avg_p>=55` — Crawley Town vs Barnet -> AWAY @ 1.66 (pending_or_unmatched_result); keys=['crawleyto']/['barnet']
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Milevsko vs Spartak Sobeslav -> AWAY @ 1.57 (pending_or_unmatched_result); keys=['milevsko']/['spartakso']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Polanka nad Odrou vs Frydek-Mistek -> AWAY @ 1.48 (pending_or_unmatched_result); keys=['polankana']/['frydekmis']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Brommapojkarna W vs Malmö FF W -> AWAY @ 1.4 (pending_or_unmatched_result); keys=['brommapoj']/['malmff', 'malmoffw']
- 2026-09-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — Plateau United vs Inter Lagos -> HOME @ 1.33 (pending_or_unmatched_result); keys=['plateauun']/['interlago']
- 2026-10-01 `CAUTION` `2way-unanimous avg_p>=60` — Envigado vs Orsomarso -> HOME @ 1.64 (pending_or_unmatched_result); keys=['envigado']/['orsomarso']

## Ambiguous result examples

- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

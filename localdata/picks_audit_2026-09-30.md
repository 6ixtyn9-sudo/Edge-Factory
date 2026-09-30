# Edge Factory — Recent picks audit (2026-09-01 to 2026-09-30)

## Overall

- archived pick rows: 591
- archived pick dates: 30
- immutable morning-baseline rows: 591
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 30
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 568
- eligible prior picks: 588
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 1
- ambiguous result picks: 3
- wins: 384
- hit rate: +67.6%
- priced picks: 526
- ROI: -3.5%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-30
- same-day rows excluded: 3

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 328 / 531 matches (61.8%)
- **Both Teams to Score (BTTS)**: occurred in 293 / 531 matches (55.2%)
- **Selected Team Over 1.5 Goals**: occurred in 348 / 531 matches (65.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 568
- **Total Hits**: 452
- **Overall Hit Rate**: 79.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=19, hits=17, hit_rate=89.5%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=153, hits=148, hit_rate=96.7%
- `home_over_05`: recommended=24, hits=17, hit_rate=70.8%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=27, hits=26, hit_rate=96.3%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=227, hits=148, hit_rate=65.2%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2267** | scored: 2267

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 562 | 562 | 347 | 61.7% | 45.2% | +16.6% | 0.262719 |
| `match_over_45` | 446 | 446 | 119 | 26.7% | 23.7% | +3.0% | 0.192463 |
| `away_under_35` | 391 | 391 | 380 | 97.2% | 95.9% | +1.3% | 0.027349 |
| `away_under_25` | 358 | 358 | 326 | 91.1% | 91.9% | -0.9% | 0.081474 |
| `home_under_35` | 162 | 162 | 158 | 97.5% | 94.0% | +3.5% | 0.026194 |
| `home_under_25` | 133 | 133 | 124 | 93.2% | 90.6% | +2.7% | 0.064025 |
| `home_over_05` | 85 | 85 | 75 | 88.2% | 83.4% | +4.9% | 0.10422 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `away_over_05` | 33 | 33 | 30 | 90.9% | 87.8% | +3.1% | 0.083325 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `home_under_15` | 13 | 13 | 9 | 69.2% | 81.6% | -12.3% | 0.232124 |
| `away_under_15` | 5 | 5 | 5 | 100.0% | 80.5% | +19.5% | 0.038162 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2046 | 1467 | 71.7% | 66.6% | +5.1% | 0.135814 |
| model | 221 | 157 | 71.0% | 63.2% | +7.9% | 0.18089 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 113 | 19.2% | 18.6% | -0.6% |
| 0.2-0.3 | 288 | 24.2% | 27.1% | +2.9% |
| 0.3-0.4 | 80 | 33.5% | 51.2% | +17.8% |
| 0.4-0.5 | 489 | 44.4% | 60.3% | +16.0% |
| 0.5-0.6 | 71 | 52.0% | 64.8% | +12.8% |
| 0.8-0.9 | 306 | 85.7% | 87.9% | +2.2% |
| 0.9-1.0 | 920 | 94.4% | 95.0% | +0.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=530, MAE=1.576283 goals, bias=-0.234434 (realized − promised), promised avg 3.515566 vs realized 3.281132

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 530 | 31.9% | 35.3% | +3.4% | 0.225833 |
| BTTS-Yes | 530 | 41.6% | 55.1% | +13.5% | 0.265202 |
| Home Over 1.5 | 530 | 63.0% | 54.2% | -8.8% | 0.239687 |
| Over 2.5 | 530 | 69.5% | 61.7% | -7.8% | 0.241407 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 220 | 8.7% | 23.6% | +14.9% |
| 0.1-0.2 | 312 | 10.4% | 24.7% | +14.3% |
| 0.2-0.3 | 7 | 24.6% | 57.1% | +32.5% |
| 0.3-0.4 | 93 | 37.3% | 51.6% | +14.3% |
| 0.4-0.5 | 427 | 42.9% | 55.7% | +12.8% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 369 | 66.9% | 59.9% | -7.0% |
| 0.7-0.8 | 143 | 74.3% | 65.0% | -9.3% |
| 0.8-0.9 | 505 | 84.5% | 65.3% | -19.1% |
| 0.9-1.0 | 43 | 92.5% | 69.8% | -22.8% |

## By rule

- `2way-unanimous avg_p>=60`: settled=81, wins=53, hit_rate=0.654321, ROI=-0.126176
- `2way-unanimous avg_p>=70`: settled=82, wins=62, hit_rate=0.756098, ROI=-0.036462
- `ml-meta avg_p>=55`: settled=299, wins=187, hit_rate=0.625418, ROI=-0.041667
- `ml-meta avg_p>=60`: settled=49, wins=42, hit_rate=0.857143, ROI=0.180204
- `ml-meta avg_p>=65`: settled=11, wins=9, hit_rate=0.818182, ROI=0.065455
- `ml-meta avg_p>=70`: settled=4, wins=3, hit_rate=0.75, ROI=-0.17
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=4, wins=4, hit_rate=1.0, ROI=0.07
- `ou25-unanimous-2way-sa avg_p>=70`: settled=37, wins=23, hit_rate=0.621622, ROI=-0.135

## By bucket

- `CAUTION`: settled=45, wins=28, hit_rate=0.622222, ROI=-0.043778
- `CERTIFIED_CLEAN`: settled=57, wins=41, hit_rate=0.719298, ROI=0.128421
- `SKIPPED_VETO`: settled=279, wins=184, hit_rate=0.659498, ROI=-0.084244
- `WATCHLIST_NO_ODDS`: settled=32, wins=24, hit_rate=0.75, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=16, wins=11, hit_rate=0.6875, ROI=0.098571
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=135, wins=93, hit_rate=0.688889, ROI=-0.016222
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=42, wins=31, hit_rate=0.738095, ROI=None
- `betexplorer_odds`: settled=162, wins=108, hit_rate=0.666667, ROI=-0.053951
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=78, wins=56, hit_rate=0.717949, ROI=0.069359
- `scoutingstats_odds`: settled=276, wins=180, hit_rate=0.652174, ROI=-0.065652
- `zulubet`: settled=2, wins=2, hit_rate=1.0, ROI=0.335

## By odds match method

- `alias_fuzzy`: settled=24, wins=17, hit_rate=0.708333, ROI=0.03619
- `betexplorer`: settled=162, wins=108, hit_rate=0.666667, ROI=-0.053951
- `exact`: settled=284, wins=187, hit_rate=0.658451, ROI=-0.056162
- `fallback`: settled=59, wins=43, hit_rate=0.728814, ROI=0.090169
- `none`: settled=39, wins=29, hit_rate=0.74359, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 162 | 108 | 0.666667 | 162 | -0.053951 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 276 | 180 | 0.652174 | 276 | -0.065652 |
| Source fallback (`SOURCE_FALLBACK`) | 59 | 43 | 0.728814 | 59 | 0.090169 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 24 | 17 | 0.708333 | 21 | 0.03619 |
| No usable price (`UNMATCHED`) | 39 | 29 | 0.74359 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 279 | 184 | 0.659498 | 271 | -0.084244 |
| **trusted evidence only** | 99 | 67 | 0.676768 | 99 | -0.086566 |
| **soft evidence only** | 180 | 117 | 0.65 | 172 | -0.082907 |
| evidence: BETEXPLORER_RESCUE | 94 | 62 | 0.659574 | 94 | -0.11266 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: SCOUTINGSTATS_SOLE | 141 | 87 | 0.617021 | 141 | -0.112979 |
| evidence: SOURCE_FALLBACK | 24 | 19 | 0.791667 | 24 | 0.095417 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.088571 |
| evidence: UNMATCHED | 7 | 5 | 0.714286 | 0 | None |
| odds band: <1.50 | 168 | 128 | 0.761905 | 168 | -0.036012 |
| odds band: 1.50-2.00 | 97 | 46 | 0.474227 | 97 | -0.200309 |
| odds band: 2.00-3.00 | 6 | 4 | 0.666667 | 6 | 0.441667 |
| odds band: unpriced | 8 | 6 | 0.75 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.21 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.4 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.49 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 14 | 10 | 0.714286 | 14 | -0.047857 |
| veto reason: context VETO in ['league'] | 22 | 16 | 0.727273 | 17 | 0.032353 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 62 | 44 | 0.709677 | 62 | -0.085645 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.085 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 8 | 0.727273 | 11 | -0.129091 |
| veto reason: context VETO in ['team_a'] | 44 | 23 | 0.522727 | 43 | -0.190233 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.128571 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.218 |
| veto reason: context VETO in ['team_h', 'team_a'] | 14 | 6 | 0.428571 | 14 | -0.275 |
| veto reason: context VETO in ['team_h'] | 49 | 31 | 0.632653 | 48 | -0.029583 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 26 | 17 | 0.653846 | 26 | -0.026923 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 18 | 11 | 0.611111 | 18 | -0.015 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 268 | 187 | 0.697761 | 229 | -0.005459 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 24 | 17 | 0.708333 | 21 | 0.03619 | 24 | 1.562083 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 276 | 180 | 0.652174 | 276 | -0.065652 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-29: Spain vs Croatia (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 75.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.2% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.3% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 34.3% (Actual: 5 goals)

### 2026-09-29: San Marino vs Albania (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.06 -> 🟢 WON (Expected prob: 75.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 90.0% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.4% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.2% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.2% (Actual: 3 goals)

### 2026-09-29: Lesotho vs Morocco (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.04 -> 🟢 WON (Expected prob: 74.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 87.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.9% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.1% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.1% (Actual: 2 goals)

### 2026-09-29: South Sudan vs Egypt (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.17 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.8% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.7% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.0% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.5% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.0% (Actual: 5 goals)

### 2026-09-29: Somalia vs Ivory Coast (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.05 -> 🟢 WON (Expected prob: 70.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.2% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.7% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.1% (Actual: 2 goals)

### 2026-09-29: Botafogo SP vs Ponte Preta (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.23 -> 🟢 WON (Expected prob: 69.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.7% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.4% (Actual: 2 goals)

### 2026-09-29: Ethiopia vs Senegal (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.37 -> 🟢 WON (Expected prob: 68.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 37.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.4% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.1% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.9% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.8% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.2% (Actual: 1 goals)

### 2026-09-29: Boreham Wood vs Kidderminster Harriers (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.46 -> 🟢 WON (Expected prob: 67.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.4% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.7% (Actual: 4 goals)

### 2026-09-29: Czech Republic vs England (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.34 -> 🟢 WON (Expected prob: 66.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.6% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 81.1% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.2% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.7% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.8% (Actual: 2 goals)

### 2026-09-29: Australia vs Brazil (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🟢 WON (Expected prob: 66.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.1% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.4% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.6% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.1% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.7% (Actual: 6 goals)

### 2026-09-29: Necaxa W vs Toluca W (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.04 -> 🟢 WON (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.3% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.9% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.1% (Actual: 4 goals)

### 2026-09-29: Slovakia vs Kazakhstan (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 65.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.5% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.5% (Actual: 3 goals)

### 2026-09-29: Woking vs Solihull Moors (Actual Score: **2-4**)
- **1X2 Pick**: Selected `HOME` @ 1.91 -> 🔴 LOST (Expected prob: 64.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.7% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.4% (Actual: 6 goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 96.9% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.3% (Actual: 6 goals)

### 2026-09-29: Liberia vs Mali (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.44 -> 🟢 WON (Expected prob: 63.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.3% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.5% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.5% (Actual: 1 goals)

### 2026-09-29: FK Vozdovac vs FK Napredak (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.95 -> 🔴 LOST (Expected prob: 60.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.2% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.8% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.5% (Actual: 0 goals)

### 2026-09-29: Gateshead vs Altrincham (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.75 -> 🟢 WON (Expected prob: 58.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.1% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.6% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.7% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.9% (Actual: 1 goals)


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

- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-26 `SKIPPED_VETO` `ml-meta avg_p>=55` — Crawley Town vs Barnet -> AWAY @ 1.66 (pending_or_unmatched_result); keys=['crawleyto']/['barnet']
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Milevsko vs Spartak Sobeslav -> AWAY @ 1.57 (pending_or_unmatched_result); keys=['milevsko']/['spartakso']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Polanka nad Odrou vs Frydek-Mistek -> AWAY @ 1.48 (pending_or_unmatched_result); keys=['polankana']/['frydekmis']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Brommapojkarna W vs Malmö FF W -> AWAY @ 1.4 (pending_or_unmatched_result); keys=['brommapoj']/['malmff', 'malmoffw']
- 2026-09-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — Plateau United vs Inter Lagos -> HOME @ 1.33 (pending_or_unmatched_result); keys=['plateauun']/['interlago']

## Ambiguous result examples

- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

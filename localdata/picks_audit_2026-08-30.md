# Edge Factory — Recent picks audit (2026-08-01 to 2026-08-30)

## Overall

- archived pick rows: 466
- archived pick dates: 30
- immutable morning-baseline rows: 338
- verified official late-slate additions: 13
- regular-ledger-only legacy rows: 115
- unsafe regular ledgers ignored: 12
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 417
- eligible prior 1x2 picks: 436
- pending/unmatched result picks: 9
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 1
- wins: 294
- hit rate: +70.5%
- priced picks: 393
- ROI: -0.1%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-30
- same-day rows excluded: 30

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 264 / 417 matches (63.3%)
- **Both Teams to Score (BTTS)**: occurred in 219 / 417 matches (52.5%)
- **Selected Team Over 1.5 Goals**: occurred in 294 / 417 matches (70.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 417
- **Total Hits**: 310
- **Overall Hit Rate**: 74.3%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=140, hits=127, hit_rate=90.7%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=10, hits=10, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=206, hits=135, hit_rate=65.5%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2381** | scored: 2381

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 357 | 357 | 227 | 63.6% | 46.4% | +17.2% | 0.264378 |
| `away_under_35` | 322 | 322 | 314 | 97.5% | 98.0% | -0.5% | 0.023323 |
| `away_under_25` | 306 | 306 | 288 | 94.1% | 94.1% | +0.0% | 0.056076 |
| `home_over_05` | 305 | 305 | 279 | 91.5% | 86.6% | +4.8% | 0.080183 |
| `match_over_45` | 298 | 298 | 83 | 27.9% | 24.7% | +3.2% | 0.203295 |
| `away_under_15` | 114 | 114 | 94 | 82.5% | 81.4% | +1.1% | 0.144539 |
| `match_over_35` | 92 | 92 | 34 | 37.0% | 43.7% | -6.7% | 0.239 |
| `home_under_35` | 89 | 89 | 87 | 97.8% | 94.9% | +2.8% | 0.022805 |
| `home_under_25` | 77 | 77 | 70 | 90.9% | 91.9% | -1.0% | 0.082729 |
| `exact_4` | 60 | 60 | 14 | 23.3% | 18.3% | +5.1% | 0.18257 |
| `goal_range_4_6` | 58 | 58 | 23 | 39.7% | 38.1% | +1.6% | 0.244063 |
| `goal_range_4_5` | 57 | 57 | 18 | 31.6% | 31.0% | +0.5% | 0.218232 |
| `exact_5` | 56 | 56 | 5 | 8.9% | 12.6% | -3.7% | 0.083591 |
| `btts_no` | 39 | 39 | 16 | 41.0% | 52.8% | -11.8% | 0.253285 |
| `btts_yes` | 34 | 34 | 17 | 50.0% | 50.7% | -0.7% | 0.251005 |
| `exact_3` | 25 | 25 | 4 | 16.0% | 22.2% | -6.2% | 0.138545 |
| `away_over_05` | 22 | 22 | 19 | 86.4% | 86.0% | +0.3% | 0.117067 |
| `goal_range_2_3` | 17 | 17 | 5 | 29.4% | 46.2% | -16.8% | 0.232291 |
| `exact_2` | 16 | 16 | 3 | 18.8% | 24.7% | -5.9% | 0.155183 |
| `home_under_15` | 12 | 12 | 11 | 91.7% | 81.2% | +10.5% | 0.08671 |
| `goal_range_6_plus` | 9 | 9 | 1 | 11.1% | 18.7% | -7.6% | 0.102748 |
| `match_over_15` | 7 | 7 | 6 | 85.7% | 86.2% | -0.5% | 0.135507 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | 33.3% | 13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2120 | 1475 | 69.6% | 66.4% | +3.2% | 0.130667 |
| legacy | 182 | 89 | 48.9% | 52.7% | -3.8% | 0.169699 |
| model | 79 | 57 | 72.2% | 53.9% | +18.2% | 0.266623 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 178 | 16.5% | 18.5% | +2.1% |
| 0.2-0.3 | 282 | 25.0% | 27.7% | +2.7% |
| 0.3-0.4 | 222 | 35.6% | 43.2% | +7.6% |
| 0.4-0.5 | 277 | 45.5% | 54.5% | +9.0% |
| 0.5-0.6 | 154 | 53.0% | 55.2% | +2.2% |
| 0.6-0.7 | 10 | 64.2% | 80.0% | +15.8% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 420 | 84.3% | 88.1% | +3.8% |
| 0.9-1.0 | 834 | 95.5% | 95.7% | +0.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=416, MAE=1.525721 goals, bias=-0.236875 (realized − promised), promised avg 3.580625 vs realized 3.34375

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 416 | 26.1% | 34.4% | +8.3% | 0.194544 |
| BTTS-Yes | 416 | 41.3% | 52.6% | +11.3% | 0.263208 |
| Home Over 1.5 | 416 | 69.2% | 59.9% | -9.3% | 0.236829 |
| Over 2.5 | 416 | 70.5% | 63.2% | -7.3% | 0.235378 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 274 | 8.9% | 21.9% | +13.0% |
| 0.1-0.2 | 144 | 10.5% | 28.5% | +18.0% |
| 0.2-0.3 | 4 | 21.2% | 25.0% | +3.8% |
| 0.3-0.4 | 107 | 37.7% | 54.2% | +16.5% |
| 0.4-0.5 | 303 | 43.0% | 52.1% | +9.1% |
| 0.6-0.7 | 235 | 66.8% | 59.6% | -7.2% |
| 0.7-0.8 | 166 | 74.7% | 66.3% | -8.4% |
| 0.8-0.9 | 376 | 84.9% | 69.9% | -14.9% |
| 0.9-1.0 | 55 | 91.8% | 78.2% | -13.6% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=117, wins=94, hit_rate=0.803419, ROI=0.072336
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=30, wins=23, hit_rate=0.766667, ROI=0.066
- `ml-meta avg_p>=55`: settled=187, wins=118, hit_rate=0.631016, ROI=-0.044213
- `ml-meta avg_p>=60`: settled=24, wins=19, hit_rate=0.791667, ROI=0.114583
- `ml-meta avg_p>=65`: settled=5, wins=4, hit_rate=0.8, ROI=0.035
- `ml-meta avg_p>=70`: settled=8, wins=7, hit_rate=0.875, ROI=0.1875
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06

## By bucket

- `CAUTION`: settled=70, wins=45, hit_rate=0.642857, ROI=0.002429
- `CERTIFIED_CLEAN`: settled=27, wins=14, hit_rate=0.518519, ROI=-0.233333
- `SKIPPED_VETO`: settled=215, wins=156, hit_rate=0.725581, ROI=0.008558
- `WATCHLIST_NO_ODDS`: settled=23, wins=18, hit_rate=0.782609, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=3, hit_rate=0.6, ROI=-0.0825
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=57, wins=41, hit_rate=0.719298, ROI=0.057018
- `WATCHLIST_UNKNOWN_CTX`: settled=20, wins=17, hit_rate=0.85, ROI=0.0395

## By odds source

- `UNKNOWN`: settled=24, wins=18, hit_rate=0.75, ROI=None
- `betexplorer_odds`: settled=145, wins=103, hit_rate=0.710345, ROI=-0.010207
- `bzzoiro_odds`: settled=79, wins=51, hit_rate=0.64557, ROI=-0.04557
- `forebet_best`: settled=23, wins=16, hit_rate=0.695652, ROI=-0.022609
- `scoutingstats_odds`: settled=135, wins=95, hit_rate=0.703704, ROI=0.009037
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=16, wins=11, hit_rate=0.6875, ROI=-0.034667
- `betexplorer`: settled=145, wins=103, hit_rate=0.710345, ROI=-0.010207
- `exact`: settled=210, wins=144, hit_rate=0.685714, ROI=-0.004571
- `fallback`: settled=23, wins=18, hit_rate=0.782609, ROI=0.103478
- `none`: settled=23, wins=18, hit_rate=0.782609, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 145 | 103 | 0.710345 | 145 | -0.010207 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 75 | 49 | 0.653333 | 75 | -0.029067 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 135 | 95 | 0.703704 | 135 | 0.009037 |
| Source fallback (`SOURCE_FALLBACK`) | 23 | 18 | 0.782609 | 23 | 0.103478 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 16 | 11 | 0.6875 | 15 | -0.034667 |
| No usable price (`UNMATCHED`) | 23 | 18 | 0.782609 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 215 | 156 | 0.725581 | 215 | 0.008558 |
| **trusted evidence only** | 119 | 87 | 0.731092 | 119 | 0.008739 |
| **soft evidence only** | 96 | 69 | 0.71875 | 96 | 0.008333 |
| evidence: BETEXPLORER_RESCUE | 75 | 56 | 0.746667 | 75 | -0.008533 |
| evidence: BZZOIRO_PRIMARY | 44 | 31 | 0.704545 | 44 | 0.038182 |
| evidence: SCOUTINGSTATS_SOLE | 76 | 53 | 0.697368 | 76 | -0.016447 |
| evidence: SOURCE_FALLBACK | 11 | 8 | 0.727273 | 11 | 0.021818 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 8 | 0.888889 | 9 | 0.201111 |
| odds band: <1.50 | 148 | 117 | 0.790541 | 148 | 0.0225 |
| odds band: 1.50-2.00 | 62 | 36 | 0.580645 | 62 | -0.044194 |
| odds band: 2.00-3.00 | 5 | 3 | 0.6 | 5 | 0.25 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.05 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.66 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 7 | 4 | 0.571429 | 7 | -0.192857 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 50 | 42 | 0.84 | 50 | 0.1288 |
| veto reason: context VETO in ['team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 12 | 10 | 0.833333 | 12 | 0.096667 |
| veto reason: context VETO in ['team_a'] | 32 | 23 | 0.71875 | 32 | 0.082813 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 14 | 12 | 0.857143 | 14 | 0.18 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.15 |
| veto reason: context VETO in ['team_h', 'team_a'] | 15 | 8 | 0.533333 | 15 | -0.22 |
| veto reason: context VETO in ['team_h'] | 48 | 31 | 0.645833 | 48 | -0.063958 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 40 | 26 | 0.65 | 40 | 0.0265 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0025 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 7 | 6 | 0.857143 | 7 | 0.294286 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 266 | 188 | 0.706767 | 243 | -0.005267 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 16 | 11 | 0.6875 | 15 | -0.034667 | 12 | 1.37625 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 135 | 95 | 0.703704 | 135 | 0.009037 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-29: Ordabasy vs FC Kyzyl-Zhar SK (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.34 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.6% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.9% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.6% (Actual: 3 goals)

### 2026-08-29: Rosengard W vs Hacken W (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.3 -> 🟢 WON (Expected prob: 60.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.4% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 94.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.6% (Actual: 1 goals)

### 2026-08-29: IF Elfsborg vs Degerfors IF (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 61.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.5% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 2 goals)

### 2026-08-29: San Diego Wave FC (w) vs Racing Louisville (w) (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 57.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.1% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 2 away goals)

### 2026-08-29: Fakel Voronezh vs Zenit (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.51 -> 🟢 WON (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.9% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 96.1% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 1 goals)

### 2026-08-29: Krasnodar vs FC Rostov (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 58.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.7% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 0 away goals)

### 2026-08-29: Celtic vs Falkirk FC (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 73.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 57.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.5% (Actual: 3 goals)

### 2026-08-29: Galatasaray vs Göztepe (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 73.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.6% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.5% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.8% (Actual: 5 goals)

### 2026-08-29: Dinamo Minsk vs FC Baranovichi (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🔴 LOST (Expected prob: 72.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 54.7% (Actual: 1 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 86.0% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.8% (Actual: 1 goals)

### 2026-08-29: Lyon vs Le Havre (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.49 -> 🔴 LOST (Expected prob: 71.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 54.7% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.1% (Actual: 2 goals)

### 2026-08-29: LASK Linz vs SCR Altach (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.1% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.9% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.9% (Actual: 3 goals)

### 2026-08-29: Afturelding vs Vestri (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.29 -> 🟢 WON (Expected prob: 69.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 53.6% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.3% (Actual: 2 goals)

### 2026-08-29: Borussia Dortmund vs Hamburger SV (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 69.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 54.2% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.3% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.3% (Actual: 2 goals)

### 2026-08-29: Juventus vs Parma (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 66.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.9% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.6% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.2% (Actual: 2 goals)

### 2026-08-29: Kawasaki Frontale vs JEF United Chiba (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 65.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.1% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.9% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.9% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.4% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.2% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.8% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.8% (Actual: 6 goals)

### 2026-08-29: Polonia Warszawa vs Lechia Gdansk (Actual Score: **2-4**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🔴 LOST (Expected prob: 63.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.8% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.0% (Actual: 2 home goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 95.0% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.2% (Actual: 6 goals)

### 2026-08-29: RB Leipzig vs Borussia M'gladbach (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🟢 WON (Expected prob: 63.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.2% (Actual: 3 goals)

### 2026-08-29: Walsall FC vs Accrington Stanley (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.85 -> 🟢 WON (Expected prob: 56.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.7% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 2 away goals)

### 2026-08-29: SV Elversberg vs Bayer Leverkusen (Actual Score: **3-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.61 -> 🔴 LOST (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.3% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.9% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.4% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 92.1% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.1% (Actual: 5 goals)

### 2026-08-29: Tokyo Verdy vs Kashima Antlers (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.72 -> 🟢 WON (Expected prob: 55.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.3% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.3% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.8% (Actual: 2 goals)

### 2026-08-29: Colchester Utd vs Rochdale (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 2.2 -> 🟢 WON (Expected prob: 55.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.0% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.7% (Actual: 1 goals)

### 2026-08-29: Partick vs Queens Park (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.32 -> 🔴 LOST (Expected prob: 64.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.5% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.1% (Actual: 0 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 84.4% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 0 goals)

### 2026-08-29: Toktogul vs Kara-Balta (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 74.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 55.4% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.7% (Actual: 2 goals)

### 2026-08-29: Ayr Utd vs Morton (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 58.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.1% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.5% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 1 away goals)

### 2026-08-29: BSC Young Boys vs FC Basel 1893 (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 55.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.6% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 3 away goals)

### 2026-08-29: Académico Viseu vs Porto (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.33 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 88.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.9% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.6% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 94.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.0% (Actual: 3 goals)

### 2026-08-29: Ferroviária SP vs Confiança (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 70.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 52.8% (Actual: 1 goals)

### 2026-08-29: Liverpool vs Nottingham Forest (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 66.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.4% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.4% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.0% (Actual: 4 goals)

### 2026-08-29: Hamilton Academical vs Cove Rangers (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 65.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.2% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.9% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.8% (Actual: 1 goals)

### 2026-08-29: Ascoli vs Carrarese Calcio (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.9 -> 🔴 LOST (Expected prob: 64.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.9% (Actual: 2 goals)

### 2026-08-29: Barnet vs Cheltenham (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🔴 LOST (Expected prob: 60.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.7% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.8% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.1% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 4 goals)

### 2026-08-29: Leganes vs Eldense (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.9 -> 🟢 WON (Expected prob: 56.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.4% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.4% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.8% (Actual: 0 away goals)

### 2026-08-29: Shimizu S-Pulse vs Kashiwa Reysol (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.0 -> 🟢 WON (Expected prob: 55.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.9% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.1% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.0% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.8% (Actual: 1 goals)

### 2026-08-29: Montrose FC vs Queen of the South (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 2.0 -> 🟢 WON (Expected prob: 55.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.0% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.5% (Actual: 3 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 9 |
- 2026-08-08 `POSTPONED` `SKIPPED_VETO` — Belshina vs Dinamo Minsk (verified_disposition); excluded from win/loss/ROI
- 2026-08-11 `POSTPONED` `WATCHLIST_UNCORROBORATED_PRICE` — Junior vs Pereira (verified_disposition); excluded from win/loss/ROI
- 2026-08-15 `POSTPONED` `SKIPPED_VETO` — Slavia Sofia vs Levski Sofia (verified_disposition); excluded from win/loss/ROI
- 2026-08-16 `POSTPONED` `SKIPPED_VETO` — SC Braga vs Gil Vicente (verified_disposition); excluded from win/loss/ROI
- 2026-08-17 `POSTPONED` `SKIPPED_VETO` — Bucaramanga vs Deportivo Pasto (verified_disposition); excluded from win/loss/ROI
- 2026-08-21 `POSTPONED` `SKIPPED_VETO` — Shamrock Rovers vs Shelbourne FC (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — Rangers vs St Mirren (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — St Johnstone vs Celtic (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — Hibernian vs Kilmarnock (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (pending_or_unmatched_result); keys=['charlesto']/['miami', 'miamiii']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-08-29 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hønefoss W vs Fortuna Ålesund W -> AWAY @ 1.2 (pending_or_unmatched_result); keys=['hnefoss', 'honefossw']/['fortunale', 'fortunaal']
- 2026-08-29 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — LSK Kvinner W vs Bodø / Glimt W -> HOME @ None (pending_or_unmatched_result); keys=['lskkvinne']/['bodglimt', 'bodoglimt']
- 2026-08-29 `WATCHLIST_SUSPECT_PRICE` `ml-meta avg_p>=55` — Inter Miami CF vs Montreal Impact -> HOME @ 1.38 (pending_or_unmatched_result); keys=['intermiam']/['montreali']
- 2026-08-29 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Viking vs Aalesund -> HOME @ 1.3 (pending_or_unmatched_result); keys=['viking', 'vikingfk']/['aalesund', 'aalesundf']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)

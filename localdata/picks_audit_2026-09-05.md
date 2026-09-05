# Edge Factory — Recent picks audit (2026-08-07 to 2026-09-05)

## Overall

- archived pick rows: 557
- archived pick dates: 30
- immutable morning-baseline rows: 443
- verified official late-slate additions: 6
- regular-ledger-only legacy rows: 108
- unsafe regular ledgers ignored: 18
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 476
- eligible prior picks: 496
- pending/unmatched result picks: 5
- rescheduled result picks (settled ±3d): 4
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 325
- hit rate: +68.3%
- priced picks: 447
- ROI: -1.6%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-05
- same-day rows excluded: 61

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 295 / 456 matches (64.7%)
- **Both Teams to Score (BTTS)**: occurred in 248 / 456 matches (54.4%)
- **Selected Team Over 1.5 Goals**: occurred in 317 / 456 matches (69.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 476
- **Total Hits**: 362
- **Overall Hit Rate**: 76.1%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=16, hits=14, hit_rate=87.5%
- `away_under_35`: recommended=8, hits=8, hit_rate=100.0%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=140, hits=126, hit_rate=90.0%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=12, hits=12, hit_rate=100.0%
- `match_over_15`: recommended=35, hits=30, hit_rate=85.7%
- `match_over_25`: recommended=254, hits=168, hit_rate=66.1%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2445** | scored: 2445

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 432 | 432 | 280 | 64.8% | 46.8% | +18.0% | 0.261674 |
| `away_under_35` | 359 | 359 | 352 | 98.1% | 98.0% | +0.0% | 0.018762 |
| `match_over_45` | 354 | 354 | 102 | 28.8% | 24.5% | +4.3% | 0.207854 |
| `away_under_25` | 343 | 343 | 322 | 93.9% | 94.0% | -0.1% | 0.05806 |
| `home_over_05` | 337 | 337 | 304 | 90.2% | 86.3% | +3.9% | 0.089851 |
| `away_under_15` | 120 | 120 | 96 | 80.0% | 81.4% | -1.4% | 0.160263 |
| `home_under_35` | 109 | 109 | 108 | 99.1% | 95.7% | +3.4% | 0.010772 |
| `home_under_25` | 94 | 94 | 86 | 91.5% | 91.7% | -0.2% | 0.07879 |
| `match_over_35` | 67 | 67 | 21 | 31.3% | 43.6% | -12.3% | 0.223707 |
| `match_over_15` | 35 | 35 | 30 | 85.7% | 85.8% | -0.1% | 0.124162 |
| `exact_4` | 33 | 33 | 6 | 18.2% | 18.6% | -0.5% | 0.148523 |
| `exact_5` | 33 | 33 | 3 | 9.1% | 12.8% | -3.7% | 0.083359 |
| `goal_range_4_5` | 33 | 33 | 9 | 27.3% | 31.5% | -4.2% | 0.198394 |
| `goal_range_4_6` | 33 | 33 | 11 | 33.3% | 38.9% | -5.5% | 0.224491 |
| `btts_no` | 19 | 19 | 6 | 31.6% | 51.6% | -20.0% | 0.255557 |
| `away_over_05` | 18 | 18 | 16 | 88.9% | 86.0% | +2.9% | 0.101394 |
| `home_under_15` | 11 | 11 | 10 | 90.9% | 81.3% | +9.6% | 0.091092 |
| `exact_3` | 7 | 7 | 3 | 42.9% | 22.2% | +20.7% | 0.28836 |
| `goal_range_6_plus` | 7 | 7 | 1 | 14.3% | 16.3% | -2.0% | 0.110594 |
| `goal_range_7_plus` | 1 | 1 | 1 | 100.0% | 10.5% | +89.5% | 0.800604 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2298 | 1652 | 71.9% | 68.6% | +3.2% | 0.128913 |
| model | 147 | 115 | 78.2% | 64.1% | +14.2% | 0.185992 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 150 | 17.4% | 19.3% | +2.0% |
| 0.2-0.3 | 255 | 25.2% | 30.6% | +5.4% |
| 0.3-0.4 | 175 | 35.5% | 40.0% | +4.5% |
| 0.4-0.5 | 283 | 45.4% | 59.7% | +14.3% |
| 0.5-0.6 | 151 | 53.0% | 62.3% | +9.2% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 496 | 84.4% | 87.3% | +2.9% |
| 0.9-1.0 | 930 | 95.6% | 95.8% | +0.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=455, MAE=1.536593 goals, bias=-0.208945 (realized − promised), promised avg 3.567187 vs realized 3.358242

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 455 | 27.3% | 36.5% | +9.2% | 0.214554 |
| BTTS-Yes | 455 | 41.5% | 54.5% | +13.0% | 0.266613 |
| Home Over 1.5 | 455 | 67.8% | 58.9% | -8.9% | 0.239464 |
| Over 2.5 | 455 | 70.4% | 64.6% | -5.7% | 0.229181 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 286 | 8.9% | 24.1% | +15.2% |
| 0.1-0.2 | 170 | 10.5% | 30.0% | +19.5% |
| 0.2-0.3 | 7 | 21.9% | 28.6% | +6.7% |
| 0.3-0.4 | 96 | 37.5% | 57.3% | +19.8% |
| 0.4-0.5 | 351 | 43.1% | 53.8% | +10.8% |
| 0.6-0.7 | 270 | 66.8% | 61.1% | -5.7% |
| 0.7-0.8 | 169 | 74.9% | 67.5% | -7.4% |
| 0.8-0.9 | 415 | 84.7% | 68.2% | -16.5% |
| 0.9-1.0 | 56 | 91.7% | 85.7% | -6.0% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=127, wins=97, hit_rate=0.76378, ROI=0.088673
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=12, wins=9, hit_rate=0.75, ROI=0.0875
- `ml-meta avg_p>=55`: settled=227, wins=142, hit_rate=0.625551, ROI=-0.061659
- `ml-meta avg_p>=60`: settled=27, wins=21, hit_rate=0.777778, ROI=0.092593
- `ml-meta avg_p>=65`: settled=6, wins=5, hit_rate=0.833333, ROI=0.158
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06
- `ou25-unanimous-2way-sa avg_p>=70`: settled=20, wins=12, hit_rate=0.6, ROI=-0.166

## By bucket

- `CAUTION`: settled=82, wins=54, hit_rate=0.658537, ROI=0.052195
- `CERTIFIED_CLEAN`: settled=33, wins=17, hit_rate=0.515152, ROI=-0.240606
- `SKIPPED_VETO`: settled=233, wins=163, hit_rate=0.699571, ROI=-0.009524
- `WATCHLIST_NO_ODDS`: settled=26, wins=19, hit_rate=0.730769, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=8, wins=6, hit_rate=0.75, ROI=0.077143
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=80, wins=54, hit_rate=0.675, ROI=-0.033625
- `WATCHLIST_UNKNOWN_CTX`: settled=14, wins=12, hit_rate=0.857143, ROI=0.047143

## By odds source

- `UNKNOWN`: settled=29, wins=19, hit_rate=0.655172, ROI=None
- `betexplorer_odds`: settled=158, wins=108, hit_rate=0.683544, ROI=-0.039937
- `bzzoiro_odds`: settled=67, wins=42, hit_rate=0.626866, ROI=-0.050149
- `forebet_best`: settled=41, wins=31, hit_rate=0.756098, ROI=0.113415
- `scoutingstats_odds`: settled=175, wins=119, hit_rate=0.68, ROI=-0.026286
- `zulubet`: settled=6, wins=6, hit_rate=1.0, ROI=0.378333

## By odds match method

- `alias_fuzzy`: settled=15, wins=12, hit_rate=0.8, ROI=0.126429
- `betexplorer`: settled=158, wins=108, hit_rate=0.683544, ROI=-0.039937
- `exact`: settled=242, wins=161, hit_rate=0.665289, ROI=-0.032893
- `fallback`: settled=33, wins=25, hit_rate=0.757576, ROI=0.156061
- `none`: settled=28, wins=19, hit_rate=0.678571, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 158 | 108 | 0.683544 | 158 | -0.039937 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 67 | 42 | 0.626866 | 67 | -0.050149 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 175 | 119 | 0.68 | 175 | -0.026286 |
| Source fallback (`SOURCE_FALLBACK`) | 33 | 25 | 0.757576 | 33 | 0.156061 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 15 | 12 | 0.8 | 14 | 0.126429 |
| No usable price (`UNMATCHED`) | 28 | 19 | 0.678571 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 233 | 163 | 0.699571 | 231 | -0.009524 |
| **trusted evidence only** | 119 | 85 | 0.714286 | 119 | -0.013613 |
| **soft evidence only** | 114 | 78 | 0.684211 | 112 | -0.005179 |
| evidence: BETEXPLORER_RESCUE | 81 | 59 | 0.728395 | 81 | -0.032963 |
| evidence: BZZOIRO_PRIMARY | 38 | 26 | 0.684211 | 38 | 0.027632 |
| evidence: SCOUTINGSTATS_SOLE | 95 | 65 | 0.684211 | 95 | -0.020105 |
| evidence: SOURCE_FALLBACK | 10 | 7 | 0.7 | 10 | 0.01 |
| evidence: SUSPECT_ALIAS_FUZZY | 7 | 6 | 0.857143 | 7 | 0.175714 |
| evidence: UNMATCHED | 2 | 0 | 0.0 | 0 | None |
| odds band: <1.50 | 150 | 116 | 0.773333 | 150 | 0.0024 |
| odds band: 1.50-2.00 | 76 | 44 | 0.578947 | 76 | -0.050132 |
| odds band: 2.00-3.00 | 5 | 3 | 0.6 | 5 | 0.25 |
| odds band: unpriced | 2 | 0 | 0.0 | 0 | None |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.05 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.66 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 11 | 7 | 0.636364 | 10 | 0.054 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 48 | 39 | 0.8125 | 48 | 0.070833 |
| veto reason: context VETO in ['team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 9 | 0.818182 | 11 | 0.05 |
| veto reason: context VETO in ['team_a'] | 36 | 24 | 0.666667 | 35 | 0.057429 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.3025 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 14 | 12 | 0.857143 | 14 | 0.182143 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.134 |
| veto reason: context VETO in ['team_h', 'team_a'] | 18 | 8 | 0.444444 | 18 | -0.320556 |
| veto reason: context VETO in ['team_h'] | 53 | 33 | 0.622642 | 53 | -0.07717 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 47 | 30 | 0.638298 | 47 | 0.015106 |
| contrast CAUTION: BZZOIRO_PRIMARY | 19 | 12 | 0.631579 | 19 | -0.014737 |
| contrast CAUTION: SOURCE_FALLBACK | 16 | 12 | 0.75 | 16 | 0.240625 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 286 | 194 | 0.678322 | 258 | -0.017519 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 15 | 12 | 0.8 | 14 | 0.126429 | 15 | 1.361 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 175 | 119 | 0.68 | 175 | -0.026286 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-04: Sport Huancayo II vs Binacional (Actual Score: **7-0**)
- **1X2 Pick**: Selected `HOME` @ 3.0 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.7% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 7 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 85.6% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.3% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.3% (Actual: 7 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.0% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.6% (Actual: 7 goals)

### 2026-09-04: Al-Ahli Jeddah vs Al-Riyadh (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.34 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 85.7% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.3% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.9% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.6% (Actual: 5 goals)

### 2026-09-04: Lyon vs Auxerre (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.52 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 87.5% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.0% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.2% (Actual: 4 goals)

### 2026-09-04: Arda Kardzhali vs Botev Plovdiv (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 2.1 -> 🔴 LOST (Expected prob: 59.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 81.1% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.0% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.1% (Actual: 5 goals)

### 2026-09-04: FC Rosengard vs Laholms FK (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 56.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 84.7% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.1% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.8% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.4% (Actual: 6 goals)

### 2026-09-04: Usti nad Labem vs Slavia Praha B (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.48 -> 🔴 LOST (Expected prob: 78.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 86.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 51.3% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.9% (Actual: 2 goals)

### 2026-09-04: FC Rosengard vs Laholms FK (Actual Score: **4-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.5 -> 🟢 WON (Expected prob: 73.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 80.2% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.5% (Actual: 6 goals)
    - [🔴 MISS] **Home Team Under 3.5 Goals**: expected 94.3% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.0% (Actual: 6 goals)

### 2026-09-04: FC Aarau vs Rapperswil (Actual Score: **3-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4 -> 🟢 WON (Expected prob: 70.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 89.5% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.4% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.8% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.3% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.9% (Actual: 5 goals)

### 2026-09-04: Tekstilshchik Iv. vs Torpedo Moscow (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.57 -> 🟢 WON (Expected prob: 63.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.9% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 82.9% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.3% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.6% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.9% (Actual: 5 goals)

### 2026-09-04: NK Varazdin vs Istra 1961 (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🔴 LOST (Expected prob: 57.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 80.5% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.9% (Actual: 0 goals)

### 2026-09-04: Noah vs Gandzasar (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.09 -> 🟢 WON (Expected prob: 81.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.4% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 95.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 83.4% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.2% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.2% (Actual: 5 goals)

### 2026-09-04: CD Olimpia vs Platense FC (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.41 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 85.8% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.2% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.9% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.5% (Actual: 5 goals)

### 2026-09-04: GAP Connah's Quay vs Haverfordwest (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🔴 LOST (Expected prob: 72.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 85.9% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 51.4% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.4% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.5% (Actual: 2 goals)

### 2026-09-04: Heracles vs De Graafschap (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.43 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 87.6% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.4% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.1% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.1% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.7% (Actual: 5 goals)

### 2026-09-04: Real Betis vs Real Madrid (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.38 -> 🔴 LOST (Expected prob: 61.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 84.2% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.3% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.8% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.5% (Actual: 1 goals)

### 2026-09-04: Fredrikstad vs Bodo/Glimt (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.3 -> 🟢 WON (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 83.3% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.5% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.3% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.1% (Actual: 3 goals)

### 2026-09-04: Paris Saint Germain vs Monaco (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🔴 LOST (Expected prob: 60.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 81.8% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.0% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.1% (Actual: 3 goals)

### 2026-09-04: Porto vs Moreirense FC (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.18 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 86.1% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.6% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.5% (Actual: 3 goals)

### 2026-09-04: Caernarfon Town vs Flint Town Utd (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 61.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 82.5% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.5% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.8% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 3 goals)

### 2026-09-04: Polissya Zhy vs Kudrivka (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 64.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.4% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 82.1% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.9% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.4% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.2% (Actual: 6 goals)

### 2026-09-04: Almere City vs Jong Ajax (Actual Score: **0-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.28 -> 🔴 LOST (Expected prob: 76.9%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 82.6% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.1% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.2% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.4% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.4% (Actual: 1 goals)


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

## Rescheduled Fixture Examples

- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (rescheduled → 2026-08-24; actual Charleston Battery 5-0 Miami FC II [home])
- 2026-08-29 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hønefoss W vs Fortuna Ålesund W -> AWAY @ 1.2 (rescheduled → 2026-08-31; actual Hønefoss W 0-1 Fortuna Ålesund W [away])
- 2026-08-29 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — LSK Kvinner W vs Bodø / Glimt W -> HOME @ None (rescheduled → 2026-09-01; actual LSK Kvinner W 1-1 Bodø / Glimt W [draw])
- 2026-08-29 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Viking vs Aalesund -> HOME @ 1.3 (rescheduled → 2026-08-30; actual Viking 2-1 Aalesund [home])

## Pending / Unmatched Result Examples

- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)

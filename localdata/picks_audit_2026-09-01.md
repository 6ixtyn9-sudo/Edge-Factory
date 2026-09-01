# Edge Factory — Recent picks audit (2026-08-03 to 2026-09-01)

## Overall

- archived pick rows: 482
- archived pick dates: 30
- immutable morning-baseline rows: 354
- verified official late-slate additions: 13
- regular-ledger-only legacy rows: 115
- unsafe regular ledgers ignored: 14
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 458
- eligible prior picks: 477
- pending/unmatched result picks: 5
- rescheduled result picks (settled ±3d): 3
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 316
- hit rate: +69.0%
- priced picks: 429
- ROI: -1.5%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-01
- same-day rows excluded: 5

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 288 / 449 matches (64.1%)
- **Both Teams to Score (BTTS)**: occurred in 244 / 449 matches (54.3%)
- **Selected Team Over 1.5 Goals**: occurred in 315 / 449 matches (70.2%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 458
- **Total Hits**: 341
- **Overall Hit Rate**: 74.5%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=5, hits=1, hit_rate=20.0%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=141, hits=128, hit_rate=90.8%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=11, hits=11, hit_rate=100.0%
- `match_over_15`: recommended=2, hits=2, hit_rate=100.0%
- `match_over_25`: recommended=250, hits=165, hit_rate=66.0%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2497** | scored: 2497

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 400 | 400 | 257 | 64.2% | 46.5% | +17.7% | 0.261877 |
| `away_under_35` | 352 | 352 | 344 | 97.7% | 98.0% | -0.3% | 0.02161 |
| `match_over_45` | 337 | 337 | 93 | 27.6% | 24.6% | +3.0% | 0.201744 |
| `away_under_25` | 333 | 333 | 312 | 93.7% | 94.1% | -0.4% | 0.059679 |
| `home_over_05` | 332 | 332 | 300 | 90.4% | 86.5% | +3.9% | 0.088472 |
| `away_under_15` | 123 | 123 | 98 | 79.7% | 81.4% | -1.7% | 0.162248 |
| `home_under_35` | 101 | 101 | 100 | 99.0% | 95.3% | +3.7% | 0.011316 |
| `home_under_25` | 88 | 88 | 81 | 92.0% | 91.8% | +0.3% | 0.074029 |
| `match_over_35` | 86 | 86 | 31 | 36.0% | 43.4% | -7.3% | 0.235839 |
| `exact_4` | 54 | 54 | 12 | 22.2% | 18.3% | +3.9% | 0.17562 |
| `goal_range_4_5` | 52 | 52 | 16 | 30.8% | 30.8% | -0.1% | 0.215302 |
| `goal_range_4_6` | 52 | 52 | 21 | 40.4% | 37.9% | +2.5% | 0.247356 |
| `exact_5` | 51 | 51 | 5 | 9.8% | 12.5% | -2.7% | 0.089769 |
| `btts_no` | 35 | 35 | 14 | 40.0% | 52.0% | -12.0% | 0.256147 |
| `exact_3` | 22 | 22 | 4 | 18.2% | 22.2% | -4.0% | 0.150708 |
| `away_over_05` | 21 | 21 | 19 | 90.5% | 86.0% | +4.4% | 0.089524 |
| `btts_yes` | 21 | 21 | 12 | 57.1% | 49.5% | +7.6% | 0.255451 |
| `home_under_15` | 12 | 12 | 11 | 91.7% | 81.2% | +10.5% | 0.08671 |
| `exact_2` | 7 | 7 | 1 | 14.3% | 24.2% | -9.9% | 0.128152 |
| `goal_range_2_3` | 7 | 7 | 1 | 14.3% | 46.0% | -31.7% | 0.220378 |
| `goal_range_6_plus` | 7 | 7 | 1 | 14.3% | 16.3% | -2.0% | 0.110594 |
| `match_over_15` | 2 | 2 | 2 | 100.0% | 82.2% | +17.8% | 0.031803 ⚠️low-n |
| `exact_1` | 1 | 1 | 0 | 0.0% | 20.5% | -20.5% | 0.042112 ⚠️low-n |
| `goal_range_7_plus` | 1 | 1 | 1 | 100.0% | 10.5% | +89.5% | 0.800604 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2327 | 1626 | 69.9% | 66.8% | +3.0% | 0.131977 |
| model | 119 | 86 | 72.3% | 58.5% | +13.8% | 0.219023 |
| legacy | 51 | 24 | 47.1% | 49.2% | -2.1% | 0.13958 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 178 | 16.7% | 19.1% | +2.4% |
| 0.2-0.3 | 283 | 25.1% | 27.9% | +2.8% |
| 0.3-0.4 | 218 | 35.5% | 42.2% | +6.7% |
| 0.4-0.5 | 287 | 45.6% | 57.1% | +11.6% |
| 0.5-0.6 | 161 | 53.0% | 59.6% | +6.6% |
| 0.6-0.7 | 6 | 62.5% | 66.7% | +4.2% |
| 0.8-0.9 | 455 | 84.3% | 87.0% | +2.7% |
| 0.9-1.0 | 909 | 95.5% | 95.8% | +0.3% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=448, MAE=1.538638 goals, bias=-0.216406 (realized − promised), promised avg 3.575781 vs realized 3.359375

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 448 | 27.0% | 36.2% | +9.2% | 0.207608 |
| BTTS-Yes | 448 | 41.4% | 54.5% | +13.1% | 0.266099 |
| Home Over 1.5 | 448 | 68.2% | 59.2% | -9.1% | 0.236802 |
| Over 2.5 | 448 | 70.5% | 64.1% | -6.5% | 0.23217 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 292 | 8.8% | 23.3% | +14.4% |
| 0.1-0.2 | 158 | 10.5% | 29.7% | +19.3% |
| 0.2-0.3 | 4 | 21.2% | 25.0% | +3.8% |
| 0.3-0.4 | 107 | 37.5% | 57.0% | +19.6% |
| 0.4-0.5 | 335 | 43.0% | 53.7% | +10.7% |
| 0.6-0.7 | 257 | 66.8% | 60.7% | -6.1% |
| 0.7-0.8 | 174 | 74.8% | 66.7% | -8.1% |
| 0.8-0.9 | 406 | 84.8% | 68.7% | -16.1% |
| 0.9-1.0 | 59 | 91.8% | 84.7% | -7.1% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=132, wins=103, hit_rate=0.780303, ROI=0.083136
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=23, wins=17, hit_rate=0.73913, ROI=0.03087
- `ml-meta avg_p>=55`: settled=209, wins=130, hit_rate=0.62201, ROI=-0.068442
- `ml-meta avg_p>=60`: settled=25, wins=20, hit_rate=0.8, ROI=0.132
- `ml-meta avg_p>=65`: settled=5, wins=4, hit_rate=0.8, ROI=0.035
- `ml-meta avg_p>=70`: settled=9, wins=8, hit_rate=0.888889, ROI=0.182222
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06
- `ou25-unanimous-2way-sa avg_p>=70`: settled=9, wins=5, hit_rate=0.555556, ROI=-0.2

## By bucket

- `CAUTION`: settled=76, wins=49, hit_rate=0.644737, ROI=0.006184
- `CERTIFIED_CLEAN`: settled=29, wins=15, hit_rate=0.517241, ROI=-0.246897
- `SKIPPED_VETO`: settled=233, wins=166, hit_rate=0.712446, ROI=0.001429
- `WATCHLIST_NO_ODDS`: settled=26, wins=19, hit_rate=0.730769, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=6, wins=4, hit_rate=0.666667, ROI=0.01
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=71, wins=48, hit_rate=0.676056, ROI=-0.023803
- `WATCHLIST_UNKNOWN_CTX`: settled=17, wins=15, hit_rate=0.882353, ROI=0.08

## By odds source

- `UNKNOWN`: settled=29, wins=19, hit_rate=0.655172, ROI=None
- `betexplorer_odds`: settled=153, wins=107, hit_rate=0.699346, ROI=-0.021634
- `bzzoiro_odds`: settled=76, wins=49, hit_rate=0.644737, ROI=-0.046711
- `forebet_best`: settled=32, wins=23, hit_rate=0.71875, ROI=0.0175
- `scoutingstats_odds`: settled=158, wins=108, hit_rate=0.683544, ROI=-0.023671
- `zulubet`: settled=10, wins=10, hit_rate=1.0, ROI=0.34

## By odds match method

- `alias_fuzzy`: settled=16, wins=12, hit_rate=0.75, ROI=0.057333
- `betexplorer`: settled=153, wins=107, hit_rate=0.699346, ROI=-0.021634
- `exact`: settled=231, wins=155, hit_rate=0.670996, ROI=-0.02974
- `fallback`: settled=30, wins=23, hit_rate=0.766667, ROI=0.089333
- `none`: settled=28, wins=19, hit_rate=0.678571, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 153 | 107 | 0.699346 | 153 | -0.021634 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 73 | 47 | 0.643836 | 73 | -0.042877 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 158 | 108 | 0.683544 | 158 | -0.023671 |
| Source fallback (`SOURCE_FALLBACK`) | 30 | 23 | 0.766667 | 30 | 0.089333 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 16 | 12 | 0.75 | 15 | 0.057333 |
| No usable price (`UNMATCHED`) | 28 | 19 | 0.678571 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 233 | 166 | 0.712446 | 231 | 0.001429 |
| **trusted evidence only** | 123 | 89 | 0.723577 | 123 | -0.000813 |
| **soft evidence only** | 110 | 77 | 0.7 | 108 | 0.003981 |
| evidence: BETEXPLORER_RESCUE | 81 | 60 | 0.740741 | 81 | -0.010247 |
| evidence: BZZOIRO_PRIMARY | 42 | 29 | 0.690476 | 42 | 0.017381 |
| evidence: SCOUTINGSTATS_SOLE | 87 | 60 | 0.689655 | 87 | -0.023563 |
| evidence: SOURCE_FALLBACK | 12 | 9 | 0.75 | 12 | 0.055833 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 8 | 0.888889 | 9 | 0.201111 |
| evidence: UNMATCHED | 2 | 0 | 0.0 | 0 | None |
| odds band: <1.50 | 152 | 120 | 0.789474 | 152 | 0.018289 |
| odds band: 1.50-2.00 | 74 | 43 | 0.581081 | 74 | -0.05 |
| odds band: 2.00-3.00 | 5 | 3 | 0.6 | 5 | 0.25 |
| odds band: unpriced | 2 | 0 | 0.0 | 0 | None |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.05 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.66 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 11 | 7 | 0.636364 | 10 | 0.054 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 51 | 43 | 0.843137 | 51 | 0.122353 |
| veto reason: context VETO in ['team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 9 | 0.818182 | 11 | 0.055455 |
| veto reason: context VETO in ['team_a'] | 36 | 25 | 0.694444 | 35 | 0.084857 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 13 | 11 | 0.846154 | 13 | 0.163077 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.055 |
| veto reason: context VETO in ['team_h', 'team_a'] | 16 | 8 | 0.5 | 16 | -0.26875 |
| veto reason: context VETO in ['team_h'] | 55 | 34 | 0.618182 | 55 | -0.104364 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 43 | 27 | 0.627907 | 43 | -0.008605 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0025 |
| contrast CAUTION: SOURCE_FALLBACK | 12 | 9 | 0.75 | 12 | 0.149167 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 1 | 0 | 0.0 | 1 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 284 | 196 | 0.690141 | 256 | -0.014688 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 16 | 12 | 0.75 | 15 | 0.057333 | 13 | 1.376538 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 158 | 108 | 0.683544 | 158 | -0.023671 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-31: Arda Kardzhali vs Botev Vratsa (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 73.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 54.8% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.6% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.2% (Actual: 2 goals)

### 2026-08-31: Flint Town Utd vs GAP Connah's Quay (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.65 -> 🟢 WON (Expected prob: 78.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 81.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 35.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 91.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.5% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.7% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.8% (Actual: 3 goals)

### 2026-08-31: Omonia Nicosia vs Omonia Aradippou (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.15 -> 🔴 LOST (Expected prob: 76.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.6% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 55.4% (Actual: 0 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 86.6% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.6% (Actual: 0 goals)

### 2026-08-31: Harrogate Town vs Gateshead (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 55.4% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.4% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.0% (Actual: 3 goals)

### 2026-08-31: Hønefoss W vs Fortuna Ålesund W (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.18 -> 🟢 WON (Expected prob: 72.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 32.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.4% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.5% (Actual: 1 goals)

### 2026-08-31: Chester FC vs Morecambe (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 72.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.7% (Actual: 1 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 86.8% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.6% (Actual: 1 goals)

### 2026-08-31: Aston Villa vs Arsenal (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.5 -> 🟢 WON (Expected prob: 61.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.7% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.1% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.6% (Actual: 1 goals)

### 2026-08-31: FK Liepaja vs Riga FC (Actual Score: **3-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.5 -> 🔴 LOST (Expected prob: 59.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.3% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 92.1% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.9% (Actual: 5 goals)

### 2026-08-31: Forest Green vs Altrincham (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🔴 LOST (Expected prob: 58.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 3 goals)

### 2026-08-31: Worthing FC vs Boreham Wood (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.61 -> 🟢 WON (Expected prob: 56.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.2% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.0% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.7% (Actual: 5 goals)

### 2026-08-31: Dagenham and Redbridge vs Slough Town (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 74.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 51.5% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.8% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.6% (Actual: 1 goals)

### 2026-08-31: Torpedo Kutaisi vs Meshakhte Tkibuli (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 71.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 53.1% (Actual: 2 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 87.4% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.4% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 82.6% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.5% (Actual: 2 goals)

### 2026-08-31: Benfica vs Estoril (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 77.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.7% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.8% (Actual: 3 goals)

### 2026-08-31: Toluca vs FC Juarez (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 76.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.9% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.0% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.8% (Actual: 4 goals)

### 2026-08-31: Barcelona vs Rayo Vallecano (Actual Score: **5-2**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 75.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.4% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 55.7% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.4% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 81.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 32.9% (Actual: 7 goals)

### 2026-08-31: Monterrey vs Atletico San Luis (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 56.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.7% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 3 away goals)

### 2026-08-31: Uxbridge vs Wimborne Town (Actual Score: **0-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.55 -> 🔴 LOST (Expected prob: 84.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.8% (Actual: 0 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.8% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.4% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.3% (Actual: 0 goals)

### 2026-08-31: Three Bridges vs Carshalton (Actual Score: **3-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.61 -> 🟢 WON (Expected prob: 81.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.9% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.6% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.2% (Actual: 5 goals)

### 2026-08-31: Real Bedford vs Leighton Town (Actual Score: **3-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.44 -> 🟢 WON (Expected prob: 78.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.6% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.0% (Actual: 5 goals)

### 2026-08-31: Sholing vs Gosport Borough (Actual Score: **1-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.59 -> 🔴 LOST (Expected prob: 73.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.7% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.6% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.3% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.8% (Actual: 1 goals)

### 2026-08-31: Fortaleza vs Operário PR (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `UNDER` @ 1.68 -> 🟢 WON (Expected prob: 70.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.8% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.9% (Actual: 1 away goals)

### 2026-08-31: Breidablik vs Stjarnan FC (Actual Score: **0-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.25 -> 🔴 LOST (Expected prob: 80.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 54.2% (Actual: 2 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 87.2% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.7% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.6% (Actual: 2 goals)

### 2026-08-31: Benfica vs Estoril (Actual Score: **2-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.25 -> 🟢 WON (Expected prob: 74.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.1% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.6% (Actual: 3 goals)

### 2026-08-31: Barcelona vs Rayo Vallecano (Actual Score: **5-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.22 -> 🟢 WON (Expected prob: 71.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.4% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.3% (Actual: 7 goals)

### 2026-08-31: Dagenham & Redbridge vs Slough Town (Actual Score: **1-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.44 -> 🔴 LOST (Expected prob: 71.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.9% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.9% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.5% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.1% (Actual: 1 goals)


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
- 2026-08-29 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Viking vs Aalesund -> HOME @ 1.3 (rescheduled → 2026-08-30; actual Viking 2-1 Aalesund [home])

## Pending / Unmatched Result Examples

- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-08-29 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — LSK Kvinner W vs Bodø / Glimt W -> HOME @ None (pending_or_unmatched_result); keys=['lskkvinne']/['bodglimt', 'bodoglimt']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)

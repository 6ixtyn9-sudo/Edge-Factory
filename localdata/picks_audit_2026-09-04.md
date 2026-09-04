# Edge Factory — Recent picks audit (2026-08-06 to 2026-09-04)

## Overall

- archived pick rows: 503
- archived pick dates: 30
- immutable morning-baseline rows: 382
- verified official late-slate additions: 6
- regular-ledger-only legacy rows: 115
- unsafe regular ledgers ignored: 17
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 462
- eligible prior picks: 482
- pending/unmatched result picks: 5
- rescheduled result picks (settled ±3d): 4
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 318
- hit rate: +68.8%
- priced picks: 433
- ROI: -1.3%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-04
- same-day rows excluded: 21

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 285 / 446 matches (63.9%)
- **Both Teams to Score (BTTS)**: occurred in 239 / 446 matches (53.6%)
- **Selected Team Over 1.5 Goals**: occurred in 310 / 446 matches (69.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 462
- **Total Hits**: 349
- **Overall Hit Rate**: 75.5%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=17, hits=15, hit_rate=88.2%
- `away_under_35`: recommended=8, hits=8, hit_rate=100.0%
- `btts_yes`: recommended=4, hits=2, hit_rate=50.0%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=141, hits=128, hit_rate=90.8%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=12, hits=12, hit_rate=100.0%
- `match_over_15`: recommended=15, hits=12, hit_rate=80.0%
- `match_over_25`: recommended=254, hits=168, hit_rate=66.1%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2408** | scored: 2408

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 415 | 415 | 266 | 64.1% | 46.7% | +17.4% | 0.261414 |
| `away_under_35` | 349 | 349 | 341 | 97.7% | 98.0% | -0.3% | 0.021784 |
| `match_over_45` | 343 | 343 | 95 | 27.7% | 24.5% | +3.2% | 0.202435 |
| `away_under_25` | 333 | 333 | 313 | 94.0% | 94.0% | -0.0% | 0.057 |
| `home_over_05` | 329 | 329 | 297 | 90.3% | 86.4% | +3.9% | 0.089333 |
| `away_under_15` | 119 | 119 | 95 | 79.8% | 81.4% | -1.6% | 0.161306 |
| `home_under_35` | 104 | 104 | 104 | 100.0% | 95.6% | +4.4% | 0.002743 |
| `home_under_25` | 91 | 91 | 83 | 91.2% | 91.7% | -0.5% | 0.081181 |
| `match_over_35` | 74 | 74 | 24 | 32.4% | 43.7% | -11.2% | 0.227847 |
| `exact_4` | 40 | 40 | 7 | 17.5% | 18.6% | -1.1% | 0.144292 |
| `exact_5` | 40 | 40 | 4 | 10.0% | 12.7% | -2.7% | 0.091191 |
| `goal_range_4_5` | 40 | 40 | 11 | 27.5% | 31.3% | -3.8% | 0.201157 |
| `goal_range_4_6` | 40 | 40 | 14 | 35.0% | 38.6% | -3.6% | 0.230433 |
| `btts_no` | 24 | 24 | 10 | 41.7% | 51.6% | -9.9% | 0.253196 |
| `away_over_05` | 19 | 19 | 17 | 89.5% | 86.0% | +3.5% | 0.097009 |
| `match_over_15` | 15 | 15 | 12 | 80.0% | 87.6% | -7.6% | 0.167646 |
| `home_under_15` | 11 | 11 | 10 | 90.9% | 81.3% | +9.6% | 0.091092 |
| `exact_3` | 10 | 10 | 3 | 30.0% | 22.2% | +7.8% | 0.216669 |
| `goal_range_6_plus` | 7 | 7 | 1 | 14.3% | 16.3% | -2.0% | 0.110594 |
| `btts_yes` | 4 | 4 | 2 | 50.0% | 49.3% | +0.7% | 0.243208 ⚠️low-n |
| `goal_range_7_plus` | 1 | 1 | 1 | 100.0% | 10.5% | +89.5% | 0.800604 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2274 | 1605 | 70.6% | 67.9% | +2.7% | 0.129102 |
| model | 134 | 105 | 78.4% | 61.5% | +16.8% | 0.200602 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 161 | 17.1% | 18.6% | +1.5% |
| 0.2-0.3 | 252 | 25.2% | 29.0% | +3.8% |
| 0.3-0.4 | 192 | 35.5% | 40.1% | +4.6% |
| 0.4-0.5 | 278 | 45.4% | 58.3% | +12.8% |
| 0.5-0.6 | 150 | 53.0% | 62.0% | +9.0% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 461 | 84.4% | 87.0% | +2.6% |
| 0.9-1.0 | 909 | 95.6% | 95.8% | +0.3% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=445, MAE=1.536674 goals, bias=-0.236944 (realized − promised), promised avg 3.569528 vs realized 3.332584

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 445 | 27.6% | 36.4% | +8.9% | 0.210301 |
| BTTS-Yes | 445 | 41.4% | 53.7% | +12.3% | 0.265536 |
| Home Over 1.5 | 445 | 67.6% | 58.7% | -8.9% | 0.241457 |
| Over 2.5 | 445 | 70.4% | 63.8% | -6.6% | 0.232493 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 285 | 8.9% | 23.9% | +15.0% |
| 0.1-0.2 | 161 | 10.5% | 29.8% | +19.3% |
| 0.2-0.3 | 7 | 21.9% | 28.6% | +6.7% |
| 0.3-0.4 | 99 | 37.5% | 57.6% | +20.1% |
| 0.4-0.5 | 338 | 43.1% | 52.7% | +9.6% |
| 0.6-0.7 | 262 | 66.8% | 60.3% | -6.5% |
| 0.7-0.8 | 167 | 74.8% | 66.5% | -8.4% |
| 0.8-0.9 | 406 | 84.8% | 68.2% | -16.5% |
| 0.9-1.0 | 55 | 91.7% | 85.5% | -6.2% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=125, wins=96, hit_rate=0.768, ROI=0.078378
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=15, wins=12, hit_rate=0.8, ROI=0.105333
- `ml-meta avg_p>=55`: settled=218, wins=136, hit_rate=0.623853, ROI=-0.062067
- `ml-meta avg_p>=60`: settled=25, wins=20, hit_rate=0.8, ROI=0.132
- `ml-meta avg_p>=65`: settled=6, wins=5, hit_rate=0.833333, ROI=0.158
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06
- `ou25-unanimous-2way-sa avg_p>=70`: settled=16, wins=10, hit_rate=0.625, ROI=-0.13875

## By bucket

- `CAUTION`: settled=75, wins=49, hit_rate=0.653333, ROI=0.0316
- `CERTIFIED_CLEAN`: settled=31, wins=16, hit_rate=0.516129, ROI=-0.242258
- `SKIPPED_VETO`: settled=231, wins=164, hit_rate=0.709957, ROI=0.002271
- `WATCHLIST_NO_ODDS`: settled=26, wins=19, hit_rate=0.730769, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=8, wins=6, hit_rate=0.75, ROI=0.077143
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=77, wins=52, hit_rate=0.675325, ROI=-0.030519
- `WATCHLIST_UNKNOWN_CTX`: settled=14, wins=12, hit_rate=0.857143, ROI=0.047143

## By odds source

- `UNKNOWN`: settled=29, wins=19, hit_rate=0.655172, ROI=None
- `betexplorer_odds`: settled=152, wins=105, hit_rate=0.690789, ROI=-0.031776
- `bzzoiro_odds`: settled=71, wins=46, hit_rate=0.647887, ROI=-0.033099
- `forebet_best`: settled=35, wins=26, hit_rate=0.742857, ROI=0.048571
- `scoutingstats_odds`: settled=169, wins=116, hit_rate=0.686391, ROI=-0.015148
- `zulubet`: settled=6, wins=6, hit_rate=1.0, ROI=0.378333

## By odds match method

- `alias_fuzzy`: settled=15, wins=12, hit_rate=0.8, ROI=0.126429
- `betexplorer`: settled=152, wins=105, hit_rate=0.690789, ROI=-0.031776
- `exact`: settled=240, wins=162, hit_rate=0.675, ROI=-0.020458
- `fallback`: settled=27, wins=20, hit_rate=0.740741, ROI=0.081481
- `none`: settled=28, wins=19, hit_rate=0.678571, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 152 | 105 | 0.690789 | 152 | -0.031776 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 71 | 46 | 0.647887 | 71 | -0.033099 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 169 | 116 | 0.686391 | 169 | -0.015148 |
| Source fallback (`SOURCE_FALLBACK`) | 27 | 20 | 0.740741 | 27 | 0.081481 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 15 | 12 | 0.8 | 14 | 0.126429 |
| No usable price (`UNMATCHED`) | 28 | 19 | 0.678571 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 231 | 164 | 0.709957 | 229 | 0.002271 |
| **trusted evidence only** | 120 | 87 | 0.725 | 120 | -0.005 |
| **soft evidence only** | 111 | 77 | 0.693694 | 109 | 0.010275 |
| evidence: BETEXPLORER_RESCUE | 79 | 58 | 0.734177 | 79 | -0.029494 |
| evidence: BZZOIRO_PRIMARY | 41 | 29 | 0.707317 | 41 | 0.042195 |
| evidence: SCOUTINGSTATS_SOLE | 92 | 64 | 0.695652 | 92 | -0.002283 |
| evidence: SOURCE_FALLBACK | 10 | 7 | 0.7 | 10 | 0.01 |
| evidence: SUSPECT_ALIAS_FUZZY | 7 | 6 | 0.857143 | 7 | 0.175714 |
| evidence: UNMATCHED | 2 | 0 | 0.0 | 0 | None |
| odds band: <1.50 | 148 | 117 | 0.790541 | 148 | 0.020811 |
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
| veto reason: context VETO in ['odds_band'] | 46 | 38 | 0.826087 | 46 | 0.09413 |
| veto reason: context VETO in ['team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 10 | 8 | 0.8 | 10 | 0.025 |
| veto reason: context VETO in ['team_a'] | 36 | 25 | 0.694444 | 35 | 0.089429 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 13 | 11 | 0.846154 | 13 | 0.163077 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.134 |
| veto reason: context VETO in ['team_h', 'team_a'] | 19 | 9 | 0.473684 | 19 | -0.299474 |
| veto reason: context VETO in ['team_h'] | 54 | 34 | 0.62963 | 54 | -0.073333 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 1 | 1 | 1.0 | 1 | 0.19 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 44 | 28 | 0.636364 | 44 | 0.019318 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0025 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 8 | 0.727273 | 11 | 0.133636 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 278 | 190 | 0.683453 | 250 | -0.01992 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 15 | 12 | 0.8 | 14 | 0.126429 | 15 | 1.361 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 169 | 116 | 0.686391 | 169 | -0.015148 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-03: Toulouse vs Lille (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.22 -> 🟢 WON (Expected prob: 55.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 85.8% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.6% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.7% (Actual: 1 goals)

### 2026-09-03: Charleston Battery vs Hartford Athletic (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.51 -> 🔴 LOST (Expected prob: 55.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 83.6% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.4% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.2% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.2% (Actual: 3 goals)

### 2026-09-03: Gent vs OH Leuven (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🟢 WON (Expected prob: 73.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 92.5% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 52.9% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.7% (Actual: 1 goals)

### 2026-09-03: Bursaspor vs Istanbulspor AS (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 59.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 85.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.1% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.1% (Actual: 4 goals)

### 2026-09-03: Lugano vs Servette (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.95 -> 🟢 WON (Expected prob: 58.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 85.4% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.4% (Actual: 1 goals)


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

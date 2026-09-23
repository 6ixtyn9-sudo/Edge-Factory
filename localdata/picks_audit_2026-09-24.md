# Edge Factory — Recent picks audit (2026-08-26 to 2026-09-24)

## Overall

- archived pick rows: 604
- archived pick dates: 30
- immutable morning-baseline rows: 604
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 575
- eligible prior picks: 592
- pending/unmatched result picks: 6
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 3
- wins: 381
- hit rate: +66.3%
- priced picks: 538
- ROI: -3.9%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-24
- same-day rows excluded: 12

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 334 / 529 matches (63.1%)
- **Both Teams to Score (BTTS)**: occurred in 301 / 529 matches (56.9%)
- **Selected Team Over 1.5 Goals**: occurred in 344 / 529 matches (65.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 575
- **Total Hits**: 441
- **Overall Hit Rate**: 76.7%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=114, hits=110, hit_rate=96.5%
- `home_over_05`: recommended=30, hits=23, hit_rate=76.7%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=12, hits=11, hit_rate=91.7%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=283, hits=185, hit_rate=65.4%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2399** | scored: 2399

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 568 | 568 | 357 | 62.9% | 46.2% | +16.7% | 0.260308 |
| `match_over_45` | 441 | 441 | 123 | 27.9% | 23.9% | +4.0% | 0.199779 |
| `away_under_35` | 409 | 409 | 399 | 97.6% | 96.3% | +1.3% | 0.023922 |
| `away_under_25` | 371 | 371 | 341 | 91.9% | 93.0% | -1.0% | 0.074655 |
| `home_over_05` | 170 | 170 | 150 | 88.2% | 84.0% | +4.2% | 0.105814 |
| `home_under_35` | 155 | 155 | 151 | 97.4% | 94.9% | +2.5% | 0.026383 |
| `home_under_25` | 129 | 129 | 117 | 90.7% | 91.7% | -1.0% | 0.083396 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `away_under_15` | 33 | 33 | 24 | 72.7% | 80.9% | -8.2% | 0.209009 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 30 | 30 | 27 | 90.0% | 88.4% | +1.6% | 0.088004 |
| `home_under_15` | 14 | 14 | 10 | 71.4% | 81.5% | -10.1% | 0.218222 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2142 | 1568 | 73.2% | 68.5% | +4.7% | 0.136154 |
| model | 257 | 182 | 70.8% | 63.8% | +7.0% | 0.171799 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 128 | 19.2% | 21.1% | +1.9% |
| 0.2-0.3 | 262 | 24.6% | 28.6% | +4.0% |
| 0.3-0.4 | 84 | 33.2% | 47.6% | +14.4% |
| 0.4-0.5 | 456 | 44.7% | 61.4% | +16.7% |
| 0.5-0.6 | 112 | 52.7% | 65.2% | +12.5% |
| 0.8-0.9 | 340 | 84.5% | 85.3% | +0.8% |
| 0.9-1.0 | 1017 | 94.7% | 94.9% | +0.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=529, MAE=1.594442 goals, bias=-0.186465 (realized − promised), promised avg 3.513497 vs realized 3.327032

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 529 | 30.3% | 35.5% | +5.3% | 0.242584 |
| BTTS-Yes | 529 | 41.9% | 56.9% | +15.0% | 0.268629 |
| Home Over 1.5 | 529 | 64.7% | 56.5% | -8.2% | 0.250068 |
| Over 2.5 | 529 | 69.6% | 63.1% | -6.5% | 0.235741 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 220 | 8.9% | 26.4% | +17.5% |
| 0.1-0.2 | 310 | 10.4% | 27.7% | +17.4% |
| 0.2-0.3 | 7 | 23.8% | 71.4% | +47.7% |
| 0.3-0.4 | 90 | 37.3% | 56.7% | +19.3% |
| 0.4-0.5 | 430 | 43.2% | 56.7% | +13.6% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 355 | 66.7% | 61.7% | -5.0% |
| 0.7-0.8 | 155 | 74.5% | 65.2% | -9.4% |
| 0.8-0.9 | 501 | 84.5% | 64.5% | -20.0% |
| 0.9-1.0 | 47 | 92.4% | 74.5% | -17.9% |

## By rule

- `2way-unanimous avg_p>=60`: settled=4, wins=3, hit_rate=0.75, ROI=-0.1725
- `2way-unanimous avg_p>=70`: settled=118, wins=86, hit_rate=0.728814, ROI=-0.005579
- `ml-meta avg_p>=55`: settled=334, wins=203, hit_rate=0.607784, ROI=-0.068692
- `ml-meta avg_p>=60`: settled=53, wins=44, hit_rate=0.830189, ROI=0.136981
- `ml-meta avg_p>=65`: settled=10, wins=8, hit_rate=0.8, ROI=0.103
- `ml-meta avg_p>=70`: settled=6, wins=5, hit_rate=0.833333, ROI=0.016667
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=3, wins=3, hit_rate=1.0, ROI=0.086667
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=48, wins=35, hit_rate=0.729167, ROI=0.095625
- `CERTIFIED_CLEAN`: settled=53, wins=38, hit_rate=0.716981, ROI=0.117925
- `SKIPPED_VETO`: settled=279, wins=179, hit_rate=0.641577, ROI=-0.095495
- `WATCHLIST_NO_ODDS`: settled=29, wins=19, hit_rate=0.655172, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.117333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=147, wins=97, hit_rate=0.659864, ROI=-0.047619
- `WATCHLIST_UNKNOWN_CTX`: settled=2, wins=1, hit_rate=0.5, ROI=-0.38

## By odds source

- `UNKNOWN`: settled=37, wins=23, hit_rate=0.621622, ROI=None
- `betexplorer_odds`: settled=152, wins=99, hit_rate=0.651316, ROI=-0.073026
- `bzzoiro_odds`: settled=7, wins=6, hit_rate=0.857143, ROI=0.231429
- `forebet_best`: settled=64, wins=47, hit_rate=0.734375, ROI=0.106094
- `scoutingstats_odds`: settled=314, wins=205, hit_rate=0.652866, ROI=-0.059268
- `zulubet`: settled=1, wins=1, hit_rate=1.0, ROI=0.07

## By odds match method

- `alias_fuzzy`: settled=26, wins=19, hit_rate=0.730769, ROI=0.09
- `betexplorer`: settled=152, wins=99, hit_rate=0.651316, ROI=-0.073026
- `exact`: settled=321, wins=211, hit_rate=0.657321, ROI=-0.052928
- `fallback`: settled=42, wins=31, hit_rate=0.738095, ROI=0.114048
- `none`: settled=34, wins=21, hit_rate=0.617647, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 152 | 99 | 0.651316 | 152 | -0.073026 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 7 | 6 | 0.857143 | 7 | 0.231429 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 314 | 205 | 0.652866 | 314 | -0.059268 |
| Source fallback (`SOURCE_FALLBACK`) | 42 | 31 | 0.738095 | 42 | 0.114048 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 26 | 19 | 0.730769 | 23 | 0.09 |
| No usable price (`UNMATCHED`) | 34 | 21 | 0.617647 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 279 | 179 | 0.641577 | 273 | -0.095495 |
| **trusted evidence only** | 85 | 52 | 0.611765 | 85 | -0.179059 |
| **soft evidence only** | 194 | 127 | 0.654639 | 188 | -0.057713 |
| evidence: BETEXPLORER_RESCUE | 81 | 48 | 0.592593 | 81 | -0.209506 |
| evidence: BZZOIRO_PRIMARY | 4 | 4 | 1.0 | 4 | 0.4375 |
| evidence: SCOUTINGSTATS_SOLE | 167 | 108 | 0.646707 | 167 | -0.069521 |
| evidence: SOURCE_FALLBACK | 13 | 10 | 0.769231 | 13 | 0.034615 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 8 | 0.03875 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 162 | 122 | 0.753086 | 162 | -0.046049 |
| odds band: 1.50-2.00 | 103 | 49 | 0.475728 | 103 | -0.20835 |
| odds band: 2.00-3.00 | 8 | 5 | 0.625 | 8 | 0.35625 |
| odds band: unpriced | 6 | 3 | 0.5 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.21 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a'] | 6 | 1 | 0.166667 | 6 | -0.786667 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.1 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 4 | 2 | 0.5 | 4 | -0.2025 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.41 |
| veto reason: context VETO in ['league', 'team_h'] | 12 | 8 | 0.666667 | 12 | -0.139167 |
| veto reason: context VETO in ['league'] | 15 | 12 | 0.8 | 13 | 0.314615 |
| veto reason: context VETO in ['niche'] | 9 | 7 | 0.777778 | 9 | 0.071111 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.273333 |
| veto reason: context VETO in ['odds_band'] | 47 | 33 | 0.702128 | 47 | -0.130426 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 10 | 7 | 0.7 | 10 | -0.131 |
| veto reason: context VETO in ['team_a'] | 49 | 24 | 0.489796 | 47 | -0.227447 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 10 | 9 | 0.9 | 10 | 0.22 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.103333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 15 | 7 | 0.466667 | 15 | -0.211333 |
| veto reason: context VETO in ['team_h'] | 59 | 35 | 0.59322 | 58 | -0.097931 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 27 | 21 | 0.777778 | 27 | 0.118889 |
| contrast CAUTION: BZZOIRO_PRIMARY | 2 | 1 | 0.5 | 2 | -0.315 |
| contrast CAUTION: SOURCE_FALLBACK | 19 | 13 | 0.684211 | 19 | 0.105789 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 235 | 157 | 0.668085 | 201 | -0.023333 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 26 | 19 | 0.730769 | 23 | 0.09 | 26 | 1.569231 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 314 | 205 | 0.652866 | 314 | -0.059268 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-23: Barau vs Abia Warriors (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.63 -> 🟢 WON (Expected prob: 56.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.3% (Actual: 2 goals)

### 2026-09-23: Hamilton Academical vs Cowdenbeath (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.13 -> 🟢 WON (Expected prob: 63.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.7% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.9% (Actual: 1 goals)

### 2026-09-23: Azerbaijan vs Tajikistan (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🟢 WON (Expected prob: 59.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.7% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 1 goals)

### 2026-09-23: Kashiwa Reysol vs FC Imabari (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.17 -> 🟢 WON (Expected prob: 71.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.3% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.2% (Actual: 4 goals)

### 2026-09-23: Chelsea W vs Austria Wien W (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.02 -> 🟢 WON (Expected prob: 68.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 86.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.4% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.5% (Actual: 1 goals)

### 2026-09-23: Gibraltar vs Sao Tome and Principe (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.46 -> 🔴 LOST (Expected prob: 68.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.5% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 86.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.4% (Actual: 0 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.3% (Actual: 0 goals)

### 2026-09-23: Enyimba vs Sporting Lagos (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.85 -> 🔴 LOST (Expected prob: 58.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 5 goals)

### 2026-09-23: Shooting Stars SC vs Katsina United (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 56.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.8% (Actual: 2 goals)

### 2026-09-23: Barcelona W vs Paris W (Actual Score: **5-2**)
- **1X2 Pick**: Selected `HOME` @ 1.02 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.0% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.1% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.5% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 30.0% (Actual: 7 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-08-29 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hønefoss W vs Fortuna Ålesund W -> AWAY @ 1.2 (rescheduled → 2026-08-31; actual Hønefoss W 0-1 Fortuna Ålesund W [away])
- 2026-08-29 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — LSK Kvinner W vs Bodø / Glimt W -> HOME @ None (rescheduled → 2026-09-01; actual LSK Kvinner W 1-1 Bodø / Glimt W [draw])
- 2026-08-29 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Viking vs Aalesund -> HOME @ 1.3 (rescheduled → 2026-08-30; actual Viking 2-1 Aalesund [home])
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 3-3 Go Ahead Eagles [draw])
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])

## Pending / Unmatched Result Examples

- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']

## Ambiguous result examples

- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)
- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

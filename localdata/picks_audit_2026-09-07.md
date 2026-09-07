# Edge Factory — Recent picks audit (2026-08-09 to 2026-09-07)

## Overall

- archived pick rows: 585
- archived pick dates: 30
- immutable morning-baseline rows: 496
- verified official late-slate additions: 6
- regular-ledger-only legacy rows: 83
- unsafe regular ledgers ignored: 20
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 556
- eligible prior picks: 579
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 5
- voided postponed/cancelled/abandoned events: 8
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 368
- hit rate: +66.2%
- priced picks: 523
- ROI: -4.1%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-07
- same-day rows excluded: 6

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 327 / 510 matches (64.1%)
- **Both Teams to Score (BTTS)**: occurred in 280 / 510 matches (54.9%)
- **Selected Team Over 1.5 Goals**: occurred in 345 / 510 matches (67.6%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 556
- **Total Hits**: 414
- **Overall Hit Rate**: 74.5%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=15, hits=13, hit_rate=86.7%
- `away_under_35`: recommended=23, hits=23, hit_rate=100.0%
- `home_over_05`: recommended=140, hits=121, hit_rate=86.4%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=16, hits=16, hit_rate=100.0%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=309, hits=203, hit_rate=65.7%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2611** | scored: 2611

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 517 | 517 | 331 | 64.0% | 47.0% | +17.0% | 0.259234 |
| `away_under_35` | 409 | 409 | 400 | 97.8% | 97.9% | -0.1% | 0.021005 |
| `match_over_45` | 403 | 403 | 115 | 28.5% | 24.1% | +4.4% | 0.205107 |
| `away_under_25` | 383 | 383 | 357 | 93.2% | 93.9% | -0.7% | 0.063712 |
| `home_over_05` | 364 | 364 | 324 | 89.0% | 85.6% | +3.4% | 0.098516 |
| `home_under_35` | 150 | 150 | 148 | 98.7% | 95.7% | +3.0% | 0.014193 |
| `away_under_15` | 116 | 116 | 92 | 79.3% | 81.4% | -2.1% | 0.164537 |
| `home_under_25` | 111 | 111 | 102 | 91.9% | 91.8% | +0.1% | 0.074865 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 43 | 43 | 13 | 30.2% | 42.4% | -12.2% | 0.220197 |
| `away_over_05` | 17 | 17 | 15 | 88.2% | 85.9% | +2.4% | 0.106374 |
| `home_under_15` | 12 | 12 | 11 | 91.7% | 81.3% | +10.4% | 0.0865 |
| `exact_4` | 9 | 9 | 2 | 22.2% | 18.8% | +3.4% | 0.173784 |
| `exact_5` | 9 | 9 | 2 | 22.2% | 13.2% | +9.1% | 0.180594 |
| `goal_range_4_5` | 9 | 9 | 4 | 44.4% | 32.0% | +12.4% | 0.261055 |
| `goal_range_4_6` | 9 | 9 | 4 | 44.4% | 39.7% | +4.8% | 0.247034 |
| `btts_no` | 4 | 4 | 0 | 0.0% | 50.4% | -50.4% | 0.25387 ⚠️low-n |
| `goal_range_6_plus` | 3 | 3 | 0 | 0.0% | 15.4% | -15.4% | 0.023834 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2381 | 1784 | 74.9% | 71.2% | +3.8% | 0.127894 |
| model | 230 | 170 | 73.9% | 64.4% | +9.5% | 0.169197 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 116 | 18.5% | 21.6% | +3.1% |
| 0.2-0.3 | 274 | 25.0% | 30.3% | +5.3% |
| 0.3-0.4 | 120 | 35.7% | 42.5% | +6.8% |
| 0.4-0.5 | 346 | 45.5% | 62.1% | +16.6% |
| 0.5-0.6 | 145 | 53.2% | 64.8% | +11.7% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 548 | 84.3% | 86.1% | +1.8% |
| 0.9-1.0 | 1057 | 95.6% | 95.6% | +0.0% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=509, MAE=1.541415 goals, bias=-0.187819 (realized − promised), promised avg 3.531631 vs realized 3.343811

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 509 | 28.2% | 37.7% | +9.5% | 0.220881 |
| BTTS-Yes | 509 | 41.6% | 55.0% | +13.4% | 0.265269 |
| Home Over 1.5 | 509 | 66.7% | 56.8% | -9.9% | 0.253422 |
| Over 2.5 | 509 | 69.8% | 64.0% | -5.8% | 0.231437 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 296 | 8.9% | 25.3% | +16.4% |
| 0.1-0.2 | 214 | 10.4% | 29.9% | +19.5% |
| 0.2-0.3 | 7 | 21.9% | 28.6% | +6.7% |
| 0.3-0.4 | 102 | 37.5% | 52.9% | +15.5% |
| 0.4-0.5 | 399 | 43.1% | 55.6% | +12.5% |
| 0.6-0.7 | 330 | 66.8% | 61.5% | -5.3% |
| 0.7-0.8 | 163 | 74.8% | 66.9% | -7.9% |
| 0.8-0.9 | 471 | 84.5% | 66.9% | -17.6% |
| 0.9-1.0 | 54 | 91.8% | 79.6% | -12.1% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=119, wins=91, hit_rate=0.764706, ROI=0.084717
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=7, wins=5, hit_rate=0.714286, ROI=0.07
- `ml-meta avg_p>=55`: settled=293, wins=178, hit_rate=0.607509, ROI=-0.082186
- `ml-meta avg_p>=60`: settled=28, wins=22, hit_rate=0.785714, ROI=0.098929
- `ml-meta avg_p>=65`: settled=6, wins=5, hit_rate=0.833333, ROI=0.158
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=87, wins=57, hit_rate=0.655172, ROI=0.038046
- `CERTIFIED_CLEAN`: settled=38, wins=20, hit_rate=0.526316, ROI=-0.219474
- `SKIPPED_VETO`: settled=262, wins=175, hit_rate=0.667939, ROI=-0.048566
- `WATCHLIST_NO_ODDS`: settled=28, wins=20, hit_rate=0.714286, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=15, wins=10, hit_rate=0.666667, ROI=-0.023571
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=115, wins=76, hit_rate=0.66087, ROI=-0.042435
- `WATCHLIST_UNKNOWN_CTX`: settled=11, wins=10, hit_rate=0.909091, ROI=0.109091

## By odds source

- `UNKNOWN`: settled=33, wins=21, hit_rate=0.636364, ROI=None
- `betexplorer_odds`: settled=168, wins=113, hit_rate=0.672619, ROI=-0.051964
- `bzzoiro_odds`: settled=60, wins=36, hit_rate=0.6, ROI=-0.084833
- `forebet_best`: settled=57, wins=41, hit_rate=0.719298, ROI=0.055088
- `scoutingstats_odds`: settled=233, wins=152, hit_rate=0.652361, ROI=-0.05382
- `zulubet`: settled=5, wins=5, hit_rate=1.0, ROI=0.33

## By odds match method

- `alias_fuzzy`: settled=25, wins=18, hit_rate=0.72, ROI=0.014167
- `betexplorer`: settled=168, wins=113, hit_rate=0.672619, ROI=-0.051964
- `exact`: settled=293, wins=188, hit_rate=0.641638, ROI=-0.060171
- `fallback`: settled=38, wins=28, hit_rate=0.736842, ROI=0.117105
- `none`: settled=32, wins=21, hit_rate=0.65625, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 168 | 113 | 0.672619 | 168 | -0.051964 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 60 | 36 | 0.6 | 60 | -0.084833 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 233 | 152 | 0.652361 | 233 | -0.05382 |
| Source fallback (`SOURCE_FALLBACK`) | 38 | 28 | 0.736842 | 38 | 0.117105 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 25 | 18 | 0.72 | 24 | 0.014167 |
| No usable price (`UNMATCHED`) | 32 | 21 | 0.65625 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 262 | 175 | 0.667939 | 258 | -0.048566 |
| **trusted evidence only** | 119 | 83 | 0.697479 | 119 | -0.03563 |
| **soft evidence only** | 143 | 92 | 0.643357 | 139 | -0.05964 |
| evidence: BETEXPLORER_RESCUE | 86 | 61 | 0.709302 | 86 | -0.05093 |
| evidence: BZZOIRO_PRIMARY | 33 | 22 | 0.666667 | 33 | 0.004242 |
| evidence: SCOUTINGSTATS_SOLE | 118 | 76 | 0.644068 | 118 | -0.064915 |
| evidence: SOURCE_FALLBACK | 11 | 7 | 0.636364 | 11 | -0.118182 |
| evidence: SUSPECT_ALIAS_FUZZY | 10 | 8 | 0.8 | 10 | 0.067 |
| evidence: UNMATCHED | 4 | 1 | 0.25 | 0 | None |
| odds band: <1.50 | 162 | 122 | 0.753086 | 162 | -0.028148 |
| odds band: 1.50-2.00 | 89 | 48 | 0.539326 | 89 | -0.105281 |
| odds band: 2.00-3.00 | 7 | 4 | 0.571429 | 7 | 0.2 |
| odds band: unpriced | 4 | 1 | 0.25 | 0 | None |
| veto reason: context VETO in ['league', 'niche'] | 2 | 2 | 1.0 | 1 | 0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 4 | 4 | 1.0 | 4 | 0.12 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.595 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_h'] | 3 | 1 | 0.333333 | 3 | -0.516667 |
| veto reason: context VETO in ['league'] | 12 | 8 | 0.666667 | 11 | 0.092727 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 54 | 42 | 0.777778 | 54 | 0.021481 |
| veto reason: context VETO in ['team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 7 | 0.777778 | 9 | -0.032222 |
| veto reason: context VETO in ['team_a'] | 42 | 24 | 0.571429 | 40 | -0.04325 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.3025 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 14 | 13 | 0.928571 | 14 | 0.273571 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.086 |
| veto reason: context VETO in ['team_h', 'team_a'] | 20 | 9 | 0.45 | 20 | -0.2985 |
| veto reason: context VETO in ['team_h'] | 62 | 36 | 0.580645 | 62 | -0.13629 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 50 | 32 | 0.64 | 50 | 0.0078 |
| contrast CAUTION: BZZOIRO_PRIMARY | 18 | 11 | 0.611111 | 18 | -0.048889 |
| contrast CAUTION: SOURCE_FALLBACK | 19 | 14 | 0.736842 | 19 | 0.2 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 298 | 198 | 0.66443 | 266 | -0.035226 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 25 | 18 | 0.72 | 24 | 0.014167 | 25 | 1.4886 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 233 | 152 | 0.652361 | 233 | -0.05382 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-06: Deportivo Tachira vs Rayo Zuliano (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.6% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.4% (Actual: 4 goals)

### 2026-09-06: Inter Miami vs Atlanta United FC (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 72.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.8% (Actual: 4 goals)

### 2026-09-06: Yverdon-Sport vs FC Stade Nyonnais (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🟢 WON (Expected prob: 69.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.3% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.6% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.2% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 26.8% (Actual: 5 goals)

### 2026-09-06: Gresford Athletic vs Mold Alexandra (Actual Score: **1-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.45 -> 🟢 WON (Expected prob: 58.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.9% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.6% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.2% (Actual: 6 goals)

### 2026-09-06: Gresford Athletic vs Mold Alexandra (Actual Score: **1-5**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.5 -> 🟢 WON (Expected prob: 71.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.7% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.9% (Actual: 1 home goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 90.6% (Actual: 5 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.2% (Actual: 6 goals)

### 2026-09-06: Yangpyeong FC vs Siheung Citizen (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.75 -> 🟢 WON (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.0% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.6% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.0% (Actual: 4 goals)

### 2026-09-06: Tukums II vs Leevon / PPK (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.44 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.9% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 32.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.8% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.7% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.1% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 81.0% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.4% (Actual: 3 goals)

### 2026-09-06: Rudes vs HNK Hajduk Split (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.28 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.8% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 36.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.3% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.1% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 4 goals)

### 2026-09-06: Valencia vs Barcelona (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.28 -> 🟢 WON (Expected prob: 69.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 31.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.7% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.7% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.4% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.3% (Actual: 5 goals)

### 2026-09-06: Tampa Bay Rowdies vs Brooklyn FC (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 68.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.3% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.2% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.5% (Actual: 2 goals)

### 2026-09-06: Vitória vs Casa Pia AC (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🔴 LOST (Expected prob: 64.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.8% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.6% (Actual: 0 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 83.6% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 0 goals)

### 2026-09-06: Molde vs KFUM Oslo (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 63.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.3% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.9% (Actual: 2 goals)

### 2026-09-06: Lokomotiv Sofia vs Ludogorets (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🟢 WON (Expected prob: 62.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.2% (Actual: 3 goals)

### 2026-09-06: Ponte Preta vs São Bernardo SP (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.33 -> 🟢 WON (Expected prob: 61.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.6% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.1% (Actual: 2 goals)

### 2026-09-06: Cerezo Osaka vs Tokyo Verdy (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🔴 LOST (Expected prob: 61.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.1% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 82.9% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.8% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 0 goals)

### 2026-09-06: Heerenveen vs AZ Alkmaar (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.82 -> 🟢 WON (Expected prob: 58.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.7% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.3% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.7% (Actual: 5 goals)

### 2026-09-06: Stjarnan FC vs IBV Vestmannaeyjar (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.79 -> 🔴 LOST (Expected prob: 57.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.2% (Actual: 4 goals)

### 2026-09-06: Modena FC vs Avellino (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🔴 LOST (Expected prob: 57.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.3% (Actual: 1 goals)

### 2026-09-06: Nagoya Grampus vs Machida Zelvia (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 2.15 -> 🟢 WON (Expected prob: 57.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.7% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.5% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.6% (Actual: 4 goals)

### 2026-09-06: Vikingur Reykjavik vs Fram Reykjavik (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.49 -> 🔴 LOST (Expected prob: 56.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.2% (Actual: 4 goals)

### 2026-09-06: Kashiwa Reysol vs Yokohama F. Marinos (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🔴 LOST (Expected prob: 55.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.5% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.0% (Actual: 2 goals)

### 2026-09-06: Ferencvaros vs Ujpest FC (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 58.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.0% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.7% (Actual: 4 goals)

### 2026-09-06: Persib Bandung vs PSM Makassar (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 57.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.3% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.2% (Actual: 4 goals)

### 2026-09-06: Thisted FC vs Nykobing FC (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 59.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.9% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.9% (Actual: 3 goals)

### 2026-09-06: Brondby vs Randers FC (Actual Score: **0-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 55.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 92.3% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 3 goals)

### 2026-09-06: FC Dallas vs Sporting Kansas City (Actual Score: **4-3**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🟢 WON (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.6% (Actual: 7 goals)

### 2026-09-06: Molde vs KFUM Oslo (Actual Score: **2-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.36 -> 🔴 LOST (Expected prob: 79.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.3% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.0% (Actual: 2 goals)

### 2026-09-06: Inter Miami CF vs Atlanta United (Actual Score: **2-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.85 -> 🟢 WON (Expected prob: 77.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.2% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.0% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.7% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 4 goals)

### 2026-09-06: Vikingur Reykjavik vs Fram Reykjavik (Actual Score: **2-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.3 -> 🟢 WON (Expected prob: 77.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.4% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.0% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 90.2% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.8% (Actual: 4 goals)

### 2026-09-06: Vancouver Whitecaps vs St. Louis City (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🔴 LOST (Expected prob: 64.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.7% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 3 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 4 goals)

### 2026-09-06: Vissel Kobe vs V-Varen Nagasaki (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 64.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.9% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.2% (Actual: 4 goals)

### 2026-09-06: Tottenham W vs West Ham W (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 59.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.4% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 4 goals)

### 2026-09-06: Universitario vs CD Comerciantes (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🔴 LOST (Expected prob: 57.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.2% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.4% (Actual: 4 goals)

### 2026-09-06: FC Sion vs FC Thun (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🟢 WON (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.2% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.1% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.6% (Actual: 5 goals)

### 2026-09-06: Deportivo Garcilaso vs Atletico Grau (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 56.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.4% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.7% (Actual: 6 goals)

### 2026-09-06: Almeria vs Cadiz (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 56.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.8% (Actual: 5 goals)

### 2026-09-06: Sarpsborg 08 vs Valerenga (Actual Score: **2-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4 -> 🟢 WON (Expected prob: 78.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.3% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.4% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.7% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.2% (Actual: 4 goals)

### 2026-09-06: KA Akureyri vs Breidablik (Actual Score: **2-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.3 -> 🟢 WON (Expected prob: 74.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.6% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.6% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.9% (Actual: 3 goals)

### 2026-09-06: FC Sion vs FC Thun (Actual Score: **3-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.44 -> 🟢 WON (Expected prob: 72.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.1% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.3% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.9% (Actual: 5 goals)

### 2026-09-06: Kristiansund BK vs Tromso (Actual Score: **2-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.7 -> 🔴 LOST (Expected prob: 72.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.8% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.3% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 2 goals)

### 2026-09-06: Olympique Marseille vs Paris FC (Actual Score: **2-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.61 -> 🟢 WON (Expected prob: 71.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.6% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.3% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 39.8% (Actual: 5 goals)

### 2026-09-06: SC Telstar vs Cambuur (Actual Score: **2-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.44 -> 🟢 WON (Expected prob: 70.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.7% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.8% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.2% (Actual: 4 goals)

### 2026-09-06: Valencia vs Barcelona (Actual Score: **0-5**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.36 -> 🟢 WON (Expected prob: 70.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.1% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 39.2% (Actual: 5 goals)

### 2026-09-06: Sporting Cristal vs Los Chankas (Actual Score: **5-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.44 -> 🟢 WON (Expected prob: 70.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.1% (Actual: 5 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 8 |
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
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])

## Pending / Unmatched Result Examples

- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (pending_or_unmatched_result); keys=['utrecht']/['goaheadea']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)

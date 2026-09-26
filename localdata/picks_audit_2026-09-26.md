# Edge Factory — Recent picks audit (2026-08-28 to 2026-09-26)

## Overall

- archived pick rows: 649
- archived pick dates: 30
- immutable morning-baseline rows: 649
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 30
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 596
- eligible prior picks: 612
- pending/unmatched result picks: 5
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 3
- wins: 394
- hit rate: +66.1%
- priced picks: 552
- ROI: -3.7%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-26
- same-day rows excluded: 37

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 340 / 550 matches (61.8%)
- **Both Teams to Score (BTTS)**: occurred in 310 / 550 matches (56.4%)
- **Selected Team Over 1.5 Goals**: occurred in 355 / 550 matches (64.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 596
- **Total Hits**: 452
- **Overall Hit Rate**: 75.8%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=121, hits=117, hit_rate=96.7%
- `home_over_05`: recommended=27, hits=20, hit_rate=74.1%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=13, hits=12, hit_rate=92.3%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=299, hits=191, hit_rate=63.9%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2451** | scored: 2451

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 589 | 589 | 363 | 61.6% | 46.1% | +15.5% | 0.260277 |
| `match_over_45` | 460 | 460 | 122 | 26.5% | 23.9% | +2.6% | 0.193095 |
| `away_under_35` | 419 | 419 | 408 | 97.4% | 96.2% | +1.2% | 0.02562 |
| `away_under_25` | 381 | 381 | 349 | 91.6% | 92.6% | -1.0% | 0.07748 |
| `home_under_35` | 164 | 164 | 160 | 97.6% | 94.7% | +2.9% | 0.025362 |
| `home_over_05` | 157 | 157 | 138 | 87.9% | 83.9% | +4.0% | 0.107996 |
| `home_under_25` | 134 | 134 | 121 | 90.3% | 91.5% | -1.2% | 0.086535 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 30 | 30 | 27 | 90.0% | 88.4% | +1.6% | 0.088004 |
| `away_under_15` | 24 | 24 | 18 | 75.0% | 80.8% | -5.8% | 0.194155 |
| `home_under_15` | 14 | 14 | 10 | 71.4% | 81.5% | -10.1% | 0.218222 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2194 | 1585 | 72.2% | 68.0% | +4.2% | 0.135926 |
| model | 257 | 182 | 70.8% | 63.8% | +7.0% | 0.171799 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 126 | 19.2% | 19.8% | +0.6% |
| 0.2-0.3 | 282 | 24.5% | 27.0% | +2.4% |
| 0.3-0.4 | 85 | 33.2% | 47.1% | +13.8% |
| 0.4-0.5 | 479 | 44.8% | 60.8% | +16.0% |
| 0.5-0.6 | 110 | 52.6% | 61.8% | +9.2% |
| 0.8-0.9 | 343 | 84.8% | 85.7% | +0.9% |
| 0.9-1.0 | 1026 | 94.7% | 94.8% | +0.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=550, MAE=1.601127 goals, bias=-0.232873 (realized − promised), promised avg 3.514691 vs realized 3.281818

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 550 | 30.8% | 35.8% | +5.0% | 0.238012 |
| BTTS-Yes | 550 | 41.8% | 56.4% | +14.5% | 0.267939 |
| Home Over 1.5 | 550 | 64.1% | 55.3% | -8.9% | 0.25471 |
| Over 2.5 | 550 | 69.6% | 61.8% | -7.8% | 0.241553 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 232 | 8.9% | 26.3% | +17.4% |
| 0.1-0.2 | 319 | 10.4% | 27.0% | +16.6% |
| 0.2-0.3 | 7 | 23.8% | 71.4% | +47.7% |
| 0.3-0.4 | 94 | 37.3% | 56.4% | +19.1% |
| 0.4-0.5 | 447 | 43.1% | 56.2% | +13.0% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 373 | 66.8% | 61.1% | -5.7% |
| 0.7-0.8 | 159 | 74.6% | 62.3% | -12.4% |
| 0.8-0.9 | 520 | 84.5% | 64.0% | -20.5% |
| 0.9-1.0 | 48 | 92.4% | 72.9% | -19.5% |

## By rule

- `2way-unanimous avg_p>=60`: settled=28, wins=19, hit_rate=0.678571, ROI=-0.032381
- `2way-unanimous avg_p>=70`: settled=115, wins=84, hit_rate=0.730435, ROI=-0.00413
- `ml-meta avg_p>=55`: settled=335, wins=203, hit_rate=0.60597, ROI=-0.06618
- `ml-meta avg_p>=60`: settled=53, wins=44, hit_rate=0.830189, ROI=0.139623
- `ml-meta avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.074444
- `ml-meta avg_p>=70`: settled=6, wins=5, hit_rate=0.833333, ROI=0.016667
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=3, wins=3, hit_rate=1.0, ROI=0.086667
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=48, wins=33, hit_rate=0.6875, ROI=0.041042
- `CERTIFIED_CLEAN`: settled=54, wins=39, hit_rate=0.722222, ROI=0.123333
- `SKIPPED_VETO`: settled=285, wins=182, hit_rate=0.638596, ROI=-0.091522
- `WATCHLIST_NO_ODDS`: settled=33, wins=21, hit_rate=0.636364, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.117333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=155, wins=104, hit_rate=0.670968, ROI=-0.034839
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.07

## By odds source

- `UNKNOWN`: settled=44, wins=27, hit_rate=0.613636, ROI=None
- `betexplorer_odds`: settled=158, wins=103, hit_rate=0.651899, ROI=-0.064367
- `bzzoiro_odds`: settled=5, wins=4, hit_rate=0.8, ROI=0.2
- `forebet_best`: settled=65, wins=48, hit_rate=0.738462, ROI=0.114615
- `scoutingstats_odds`: settled=322, wins=210, hit_rate=0.652174, ROI=-0.060559
- `zulubet`: settled=2, wins=2, hit_rate=1.0, ROI=0.335

## By odds match method

- `alias_fuzzy`: settled=26, wins=19, hit_rate=0.730769, ROI=0.09
- `betexplorer`: settled=158, wins=103, hit_rate=0.651899, ROI=-0.064367
- `exact`: settled=327, wins=214, hit_rate=0.654434, ROI=-0.056575
- `fallback`: settled=44, wins=33, hit_rate=0.75, ROI=0.1375
- `none`: settled=41, wins=25, hit_rate=0.609756, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 158 | 103 | 0.651899 | 158 | -0.064367 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 5 | 4 | 0.8 | 5 | 0.2 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 322 | 210 | 0.652174 | 322 | -0.060559 |
| Source fallback (`SOURCE_FALLBACK`) | 44 | 33 | 0.75 | 44 | 0.1375 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 26 | 19 | 0.730769 | 23 | 0.09 |
| No usable price (`UNMATCHED`) | 41 | 25 | 0.609756 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 285 | 182 | 0.638596 | 276 | -0.091522 |
| **trusted evidence only** | 87 | 54 | 0.62069 | 87 | -0.145977 |
| **soft evidence only** | 198 | 128 | 0.646465 | 189 | -0.066455 |
| evidence: BETEXPLORER_RESCUE | 84 | 51 | 0.607143 | 84 | -0.169048 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.5 |
| evidence: SCOUTINGSTATS_SOLE | 167 | 106 | 0.634731 | 167 | -0.084431 |
| evidence: SOURCE_FALLBACK | 14 | 11 | 0.785714 | 14 | 0.087857 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 8 | 0.03875 |
| evidence: UNMATCHED | 8 | 4 | 0.5 | 0 | None |
| odds band: <1.50 | 160 | 118 | 0.7375 | 160 | -0.0635 |
| odds band: 1.50-2.00 | 108 | 54 | 0.5 | 108 | -0.166204 |
| odds band: 2.00-3.00 | 8 | 5 | 0.625 | 8 | 0.35625 |
| odds band: unpriced | 9 | 5 | 0.555556 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.21 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a'] | 7 | 2 | 0.285714 | 7 | -0.58 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.1 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 4 | 2 | 0.5 | 4 | -0.2025 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.41 |
| veto reason: context VETO in ['league', 'team_h'] | 13 | 9 | 0.692308 | 13 | -0.065385 |
| veto reason: context VETO in ['league'] | 18 | 14 | 0.777778 | 13 | 0.314615 |
| veto reason: context VETO in ['niche'] | 9 | 7 | 0.777778 | 9 | 0.071111 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.273333 |
| veto reason: context VETO in ['odds_band'] | 49 | 33 | 0.673469 | 49 | -0.152041 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 6 | 0.666667 | 9 | -0.17 |
| veto reason: context VETO in ['team_a'] | 51 | 26 | 0.509804 | 49 | -0.19898 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.196667 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.103333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 15 | 7 | 0.466667 | 15 | -0.176667 |
| veto reason: context VETO in ['team_h'] | 58 | 34 | 0.586207 | 57 | -0.102456 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 28 | 20 | 0.714286 | 28 | 0.031786 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 19 | 13 | 0.684211 | 19 | 0.109474 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 248 | 165 | 0.665323 | 207 | -0.015072 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 26 | 19 | 0.730769 | 23 | 0.09 | 26 | 1.569231 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 322 | 210 | 0.652174 | 322 | -0.060559 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-25: Vänersborgs IF vs Ahlafors (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.41 -> 🟢 WON (Expected prob: 57.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.8% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.2% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.1% (Actual: 3 goals)

### 2026-09-25: Burkina Faso vs Benin (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🔴 LOST (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.4% (Actual: 2 goals)

### 2026-09-25: Inverness CT vs Morton (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🟢 WON (Expected prob: 68.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.4% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.4% (Actual: 2 goals)

### 2026-09-25: Haiti vs Trinidad & Tobago (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 66.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.3% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.7% (Actual: 5 goals)

### 2026-09-25: Schöningen vs Drochtersen / Assel (Actual Score: **3-3**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.3% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.5% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.3% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 86.3% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.5% (Actual: 6 goals)

### 2026-09-25: Tasmania Berlin vs Carl Zeiss Jena (Actual Score: **1-5**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 64.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.6% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.3% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.4% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.5% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.1% (Actual: 6 goals)

### 2026-09-25: Mozambique vs Senegal (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🔴 LOST (Expected prob: 63.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.6% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 85.7% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.3% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.1% (Actual: 2 goals)

### 2026-09-25: Bayern Munchen II vs Schwaben Augsburg (Actual Score: **4-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.0% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 89.3% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.7% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.2% (Actual: 7 goals)

### 2026-09-25: Landvetter IS vs Torslanda IK (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.78 -> 🟢 WON (Expected prob: 61.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.4% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.7% (Actual: 4 goals)

### 2026-09-25: Turkey vs France (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.39 -> 🟢 WON (Expected prob: 61.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.7% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.4% (Actual: 1 goals)

### 2026-09-25: Treaty United vs Finn Harps (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🟢 WON (Expected prob: 55.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.3% (Actual: 3 goals)

### 2026-09-25: Slavoj Vysehrad vs Sokol Hostouň (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 35.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 87.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.7% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.5% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.5% (Actual: 3 goals)

### 2026-09-25: Parndorf vs Favoritner AC (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 65.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.5% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 1 goals)

### 2026-09-25: Karvina II vs Líšeň II (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 63.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.6% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.4% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.0% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.0% (Actual: 4 goals)

### 2026-09-25: Baťov vs Nove Sady (Actual Score: **3-5**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 61.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.9% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.1% (Actual: 8 goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 5 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 89.2% (Actual: 5 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.8% (Actual: 8 goals)

### 2026-09-25: FC Dordrecht vs Almere City (Actual Score: **3-2**)
- **1X2 Pick**: Selected `AWAY` @ 2.1 -> 🔴 LOST (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 35.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 94.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 87.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.0% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.2% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.6% (Actual: 5 goals)

### 2026-09-25: Morocco vs Gabon (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.18 -> 🟢 WON (Expected prob: 67.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.4% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.1% (Actual: 2 goals)

### 2026-09-25: Girona vs Albacete (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 66.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.3% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.2% (Actual: 2 goals)

### 2026-09-25: Nigeria vs Madagascar (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 65.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.4% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.1% (Actual: 3 goals)


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

- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']

## Ambiguous result examples

- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)
- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

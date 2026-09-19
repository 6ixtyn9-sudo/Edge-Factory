# Edge Factory — Recent picks audit (2026-08-22 to 2026-09-20)

## Overall

- archived pick rows: 657
- archived pick dates: 30
- immutable morning-baseline rows: 657
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 591
- eligible prior picks: 615
- pending/unmatched result picks: 9
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 396
- hit rate: +67.0%
- priced picks: 552
- ROI: -4.0%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-20
- same-day rows excluded: 42

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 350 / 545 matches (64.2%)
- **Both Teams to Score (BTTS)**: occurred in 304 / 545 matches (55.8%)
- **Selected Team Over 1.5 Goals**: occurred in 364 / 545 matches (66.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 591
- **Total Hits**: 447
- **Overall Hit Rate**: 75.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=22, hits=21, hit_rate=95.5%
- `away_under_35`: recommended=98, hits=94, hit_rate=95.9%
- `home_over_05`: recommended=43, hits=33, hit_rate=76.7%
- `home_under_25`: recommended=21, hits=20, hit_rate=95.2%
- `home_under_35`: recommended=11, hits=10, hit_rate=90.9%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=317, hits=211, hit_rate=66.6%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2531** | scored: 2531

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 584 | 584 | 373 | 63.9% | 46.6% | +17.3% | 0.258897 |
| `match_over_45` | 446 | 446 | 130 | 29.1% | 23.8% | +5.3% | 0.206515 |
| `away_under_35` | 423 | 423 | 409 | 96.7% | 96.7% | -0.0% | 0.031435 |
| `away_under_25` | 395 | 395 | 366 | 92.7% | 93.3% | -0.7% | 0.068421 |
| `home_over_05` | 220 | 220 | 194 | 88.2% | 84.3% | +3.8% | 0.105784 |
| `home_under_35` | 163 | 163 | 159 | 97.5% | 95.2% | +2.4% | 0.024874 |
| `home_under_25` | 131 | 131 | 119 | 90.8% | 91.7% | -0.9% | 0.082495 |
| `away_under_15` | 47 | 47 | 36 | 76.6% | 81.0% | -4.4% | 0.183582 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 30 | 30 | 27 | 90.0% | 88.4% | +1.6% | 0.088004 |
| `home_under_15` | 14 | 14 | 10 | 71.4% | 81.5% | -10.0% | 0.218277 |
| `double_chance` | 2 | 2 | 2 | 100.0% | 83.3% | +16.7% | 0.027978 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2256 | 1677 | 74.3% | 69.5% | +4.8% | 0.134061 |
| model | 275 | 197 | 71.6% | 63.7% | +8.0% | 0.181283 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 132 | 19.1% | 22.0% | +2.8% |
| 0.2-0.3 | 271 | 24.8% | 31.0% | +6.2% |
| 0.3-0.4 | 76 | 33.3% | 47.4% | +14.1% |
| 0.4-0.5 | 457 | 44.9% | 62.1% | +17.2% |
| 0.5-0.6 | 125 | 53.0% | 66.4% | +13.4% |
| 0.6-0.7 | 2 | 64.7% | 100.0% | +35.3% |
| 0.8-0.9 | 389 | 84.4% | 85.9% | +1.5% |
| 0.9-1.0 | 1079 | 95.0% | 94.7% | -0.3% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=544, MAE=1.589522 goals, bias=-0.125625 (realized − promised), promised avg 3.519007 vs realized 3.393382

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 544 | 30.1% | 36.8% | +6.6% | 0.229825 |
| BTTS-Yes | 544 | 41.7% | 55.9% | +14.2% | 0.267606 |
| Home Over 1.5 | 544 | 64.8% | 57.2% | -7.6% | 0.25183 |
| Over 2.5 | 544 | 69.6% | 64.2% | -5.5% | 0.230524 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 237 | 8.8% | 27.4% | +18.6% |
| 0.1-0.2 | 309 | 10.4% | 27.5% | +17.1% |
| 0.2-0.3 | 10 | 22.8% | 50.0% | +27.2% |
| 0.3-0.4 | 102 | 37.4% | 57.8% | +20.4% |
| 0.4-0.5 | 429 | 43.2% | 55.5% | +12.3% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 363 | 66.7% | 61.4% | -5.2% |
| 0.7-0.8 | 160 | 74.5% | 68.1% | -6.4% |
| 0.8-0.9 | 514 | 84.4% | 66.1% | -18.3% |
| 0.9-1.0 | 51 | 92.4% | 78.4% | -13.9% |

## By rule

- `2way-unanimous avg_p>=70`: settled=127, wins=97, hit_rate=0.76378, ROI=0.02219
- `ml-meta avg_p>=55`: settled=344, wins=208, hit_rate=0.604651, ROI=-0.083659
- `ml-meta avg_p>=60`: settled=51, wins=42, hit_rate=0.823529, ROI=0.137451
- `ml-meta avg_p>=65`: settled=8, wins=7, hit_rate=0.875, ROI=0.22
- `ml-meta avg_p>=70`: settled=9, wins=8, hit_rate=0.888889, ROI=0.031111
- `ml-meta avg_p>=75`: settled=2, wins=2, hit_rate=1.0, ROI=0.1
- `ml-meta avg_p>=80`: settled=4, wins=4, hit_rate=1.0, ROI=0.08
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=49, wins=36, hit_rate=0.734694, ROI=0.105714
- `CERTIFIED_CLEAN`: settled=44, wins=31, hit_rate=0.704545, ROI=0.1
- `SKIPPED_VETO`: settled=301, wins=195, hit_rate=0.647841, ROI=-0.08722
- `WATCHLIST_NO_ODDS`: settled=31, wins=22, hit_rate=0.709677, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=16, wins=11, hit_rate=0.6875, ROI=0.050714
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=144, wins=95, hit_rate=0.659722, ROI=-0.056181
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=6, hit_rate=1.0, ROI=0.221667

## By odds source

- `UNKNOWN`: settled=39, wins=26, hit_rate=0.666667, ROI=None
- `betexplorer_odds`: settled=159, wins=108, hit_rate=0.679245, ROI=-0.055157
- `bzzoiro_odds`: settled=7, wins=7, hit_rate=1.0, ROI=0.532857
- `forebet_best`: settled=64, wins=46, hit_rate=0.71875, ROI=0.064375
- `scoutingstats_odds`: settled=321, wins=208, hit_rate=0.647975, ROI=-0.066511
- `zulubet`: settled=1, wins=1, hit_rate=1.0, ROI=0.07

## By odds match method

- `alias_fuzzy`: settled=25, wins=18, hit_rate=0.72, ROI=0.046364
- `betexplorer`: settled=159, wins=108, hit_rate=0.679245, ROI=-0.055157
- `exact`: settled=328, wins=215, hit_rate=0.655488, ROI=-0.05372
- `fallback`: settled=43, wins=31, hit_rate=0.72093, ROI=0.073721
- `none`: settled=36, wins=24, hit_rate=0.666667, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 159 | 108 | 0.679245 | 159 | -0.055157 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 7 | 7 | 1.0 | 7 | 0.532857 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 321 | 208 | 0.647975 | 321 | -0.066511 |
| Source fallback (`SOURCE_FALLBACK`) | 43 | 31 | 0.72093 | 43 | 0.073721 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 25 | 18 | 0.72 | 22 | 0.046364 |
| No usable price (`UNMATCHED`) | 36 | 24 | 0.666667 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 301 | 195 | 0.647841 | 295 | -0.08722 |
| **trusted evidence only** | 94 | 62 | 0.659574 | 94 | -0.122234 |
| **soft evidence only** | 207 | 133 | 0.642512 | 201 | -0.070846 |
| evidence: BETEXPLORER_RESCUE | 90 | 58 | 0.644444 | 90 | -0.152556 |
| evidence: BZZOIRO_PRIMARY | 4 | 4 | 1.0 | 4 | 0.56 |
| evidence: SCOUTINGSTATS_SOLE | 177 | 113 | 0.638418 | 177 | -0.074915 |
| evidence: SOURCE_FALLBACK | 16 | 11 | 0.6875 | 16 | -0.080625 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 8 | 0.03875 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 173 | 132 | 0.763006 | 173 | -0.035491 |
| odds band: 1.50-2.00 | 112 | 54 | 0.482143 | 112 | -0.200804 |
| odds band: 2.00-3.00 | 10 | 6 | 0.6 | 10 | 0.29 |
| odds band: unpriced | 6 | 3 | 0.5 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 3 | 1.0 | 2 | 0.305 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 5 | 1.0 | 5 | 0.146 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 11 | 4 | 0.363636 | 11 | -0.573636 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.25 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 4 | 2 | 0.5 | 4 | -0.2025 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['league', 'team_h'] | 13 | 9 | 0.692308 | 13 | -0.093846 |
| veto reason: context VETO in ['league'] | 19 | 13 | 0.684211 | 17 | 0.074118 |
| veto reason: context VETO in ['niche'] | 8 | 6 | 0.75 | 8 | 0.09 |
| veto reason: context VETO in ['odds_band', 'niche'] | 4 | 4 | 1.0 | 4 | 0.26 |
| veto reason: context VETO in ['odds_band'] | 47 | 34 | 0.723404 | 47 | -0.09617 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 12 | 10 | 0.833333 | 12 | 0.03 |
| veto reason: context VETO in ['team_a'] | 46 | 24 | 0.521739 | 44 | -0.143409 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 1 | 0.25 | 4 | -0.64 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.221818 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.446667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.054286 |
| veto reason: context VETO in ['team_h', 'team_a'] | 18 | 8 | 0.444444 | 18 | -0.243333 |
| veto reason: context VETO in ['team_h'] | 64 | 38 | 0.59375 | 63 | -0.103651 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 28 | 20 | 0.714286 | 28 | 0.026786 |
| contrast CAUTION: BZZOIRO_PRIMARY | 2 | 2 | 1.0 | 2 | 0.495 |
| contrast CAUTION: SOURCE_FALLBACK | 19 | 14 | 0.736842 | 19 | 0.181053 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 245 | 170 | 0.693878 | 209 | -0.008947 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 25 | 18 | 0.72 | 22 | 0.046364 | 25 | 1.5612 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 321 | 208 | 0.647975 | 321 | -0.066511 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-19: Dumbarton FC vs Spartans FC (Actual Score: **3-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.7 -> 🔴 LOST (Expected prob: 57.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 91.9% (Actual: 3 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.9% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.2% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.3% (Actual: 3 goals)

### 2026-09-19: Eldense vs Eibar (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 2.37 -> 🟢 WON (Expected prob: 58.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.8% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.3% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.3% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 3 goals)

### 2026-09-19: BSC Young Boys vs Servette FC (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.77 -> 🟢 WON (Expected prob: 57.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.8% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.5% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.0% (Actual: 5 goals)

### 2026-09-19: Istra 1961 vs HNK Gorica (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.9 -> 🔴 LOST (Expected prob: 56.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.7% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.0% (Actual: 1 goals)

### 2026-09-19: FK Jelgava vs Riga FC (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🟢 WON (Expected prob: 69.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 32.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.6% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.9% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.0% (Actual: 1 goals)

### 2026-09-19: MSK Zilina vs AS Trencin (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 61.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.9% (Actual: 3 goals)

### 2026-09-19: Throttur Reykjavik vs Fylkir (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.77 -> 🟢 WON (Expected prob: 60.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.5% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.6% (Actual: 1 goals)

### 2026-09-19: KFC Komarno vs Slovan Bratislava (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.66 -> 🟢 WON (Expected prob: 60.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.2% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.8% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.3% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.6% (Actual: 3 goals)

### 2026-09-19: Apollon Limassol vs APOEL (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 2.08 -> 🔴 LOST (Expected prob: 59.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.7% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.7% (Actual: 4 goals)

### 2026-09-19: Unirea Slobozia vs Chindia Targoviste (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.9 -> 🟢 WON (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.5% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.1% (Actual: 1 goals)

### 2026-09-19: Monterrey W vs Necaxa W (Actual Score: **10-0**)
- **1X2 Pick**: Selected `HOME` @ 1.02 -> 🟢 WON (Expected prob: 80.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.6% (Actual: 10 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.5% (Actual: 10 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.2% (Actual: 10 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.8% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.4% (Actual: 10 goals)

### 2026-09-19: Real Madrid W vs Valencia W (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.08 -> 🟢 WON (Expected prob: 82.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 82.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 92.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 86.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.7% (Actual: 4 goals)

### 2026-09-19: Sevilla vs Barcelona (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.2 -> 🟢 WON (Expected prob: 72.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 26.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 88.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.2% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.9% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.3% (Actual: 4 goals)

### 2026-09-19: Cove Rangers vs Ross County (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🟢 WON (Expected prob: 70.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 36.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 94.1% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.0% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.0% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.0% (Actual: 2 goals)

### 2026-09-19: Grimsby vs Crawley Town (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 70.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.6% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.1% (Actual: 2 goals)

### 2026-09-19: Sligo Rovers vs St Patricks Dublin (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.4 -> 🟢 WON (Expected prob: 70.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 36.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 95.5% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.0% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.3% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.9% (Actual: 1 goals)

### 2026-09-19: Stirling Albion vs Clyde FC (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.75 -> 🔴 LOST (Expected prob: 64.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.5% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.8% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.4% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.1% (Actual: 2 goals)

### 2026-09-19: Motor Lublin vs Gornik Zabrze (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.95 -> 🔴 LOST (Expected prob: 63.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.1% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.2% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.4% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.6% (Actual: 0 goals)

### 2026-09-19: Bromley FC vs Huddersfield (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.57 -> 🔴 LOST (Expected prob: 63.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.6% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.2% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.0% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.7% (Actual: 3 goals)

### 2026-09-19: FC Tokyo vs Nagoya Grampus (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🟢 WON (Expected prob: 63.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.7% (Actual: 1 goals)

### 2026-09-19: AFC Fylde vs Altrincham (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🔴 LOST (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.8% (Actual: 3 goals)

### 2026-09-19: Stenhousemuir FC vs Arbroath FC (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.95 -> 🟢 WON (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.8% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.9% (Actual: 1 goals)

### 2026-09-19: FC Elva vs FC Tallinn (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🔴 LOST (Expected prob: 61.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.9% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.4% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 2 goals)

### 2026-09-19: Varbergs BoIS vs IK Brage (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🟢 WON (Expected prob: 58.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.1% (Actual: 5 goals)

### 2026-09-19: Fagiano Okayama vs Kyoto Sanga (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.85 -> 🔴 LOST (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.8% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.1% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.6% (Actual: 3 goals)

### 2026-09-19: Walsall FC vs Port Vale (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 2.45 -> 🟢 WON (Expected prob: 56.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.6% (Actual: 2 goals)

### 2026-09-19: FC Luzern vs Grasshoppers (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🟢 WON (Expected prob: 55.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.6% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.6% (Actual: 6 goals)

### 2026-09-19: Maccabi Netanya vs Maccabi Tel Aviv (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.42 -> 🟢 WON (Expected prob: 63.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.4% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.7% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.8% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.8% (Actual: 3 goals)

### 2026-09-19: Gateshead vs Southend (Actual Score: **1-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.54 -> 🟢 WON (Expected prob: 59.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.3% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.4% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.9% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.3% (Actual: 7 goals)

### 2026-09-19: Kilmarnock vs Hearts (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.65 -> 🔴 LOST (Expected prob: 55.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.9% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.6% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.0% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 2 goals)

### 2026-09-19: Brann W vs Bodø / Glimt W (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 82.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.8% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 94.2% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.0% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.4% (Actual: 4 goals)

### 2026-09-19: Scotland Mabvuku vs AGAMA (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.6% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.3% (Actual: 0 away goals)
    - [🟢 HIT] **Double Chance 1X**: expected 82.1% (Actual: home (3-0))
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.7% (Actual: 3 goals)

### 2026-09-19: Rijnsburgse Boys vs Quick Boys (Actual Score: **3-1**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 32.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 95.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.2% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.1% (Actual: 1 away goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 87.8% (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.2% (Actual: 4 goals)

### 2026-09-19: Leevon / PPK vs Rīgas FS II (Actual Score: **6-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.3% (Actual: 9 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 6 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.7% (Actual: 9 goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 3 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.2% (Actual: 9 goals)

### 2026-09-19: Hamilton Academical vs Queen of the South (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.2% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 30.1% (Actual: 5 goals)

### 2026-09-19: Molde vs Aalesund (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.4% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.1% (Actual: 3 goals)

### 2026-09-19: The New Saints vs Llandudno (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.3% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.7% (Actual: 3 goals)

### 2026-09-19: Kristiansund BK vs Rosenborg BK (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.5 -> 🟢 WON (Expected prob: 62.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.5% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.4% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.9% (Actual: 4 goals)

### 2026-09-19: Wrexham FC vs Southampton (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.25 -> 🔴 LOST (Expected prob: 57.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.1% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.4% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.2% (Actual: 3 goals)

### 2026-09-19: Maribor vs Aluminij (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🔴 LOST (Expected prob: 63.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.3% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.3% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.2% (Actual: 4 goals)

### 2026-09-19: Arsenal (w) vs Manchester United Women (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🔴 LOST (Expected prob: 63.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.2% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.0% (Actual: 2 goals)

### 2026-09-19: Maccabi Haifa vs Ironi Tiberias (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 63.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.4% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.2% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.0% (Actual: 5 goals)

### 2026-09-19: FC Sion vs FC Zurich (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🔴 LOST (Expected prob: 56.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.3% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.1% (Actual: 2 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 3 |
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — Rangers vs St Mirren (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — St Johnstone vs Celtic (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — Hibernian vs Kilmarnock (verified_disposition); excluded from win/loss/ROI

## Rescheduled Fixture Examples

- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (rescheduled → 2026-08-24; actual Charleston Battery 5-0 Miami FC II [home])
- 2026-08-29 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hønefoss W vs Fortuna Ålesund W -> AWAY @ 1.2 (rescheduled → 2026-08-31; actual Hønefoss W 0-1 Fortuna Ålesund W [away])
- 2026-08-29 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — LSK Kvinner W vs Bodø / Glimt W -> HOME @ None (rescheduled → 2026-09-01; actual LSK Kvinner W 1-1 Bodø / Glimt W [draw])
- 2026-08-29 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Viking vs Aalesund -> HOME @ 1.3 (rescheduled → 2026-08-30; actual Viking 2-1 Aalesund [home])
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 3-3 Go Ahead Eagles [draw])
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])

## Pending / Unmatched Result Examples

- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
- 2026-09-19 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — VfB Oldenburg vs SSV Jeddeloh -> HOME @ None (pending_or_unmatched_result); keys=['vfboldenb']/['ssvjeddel']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)
- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

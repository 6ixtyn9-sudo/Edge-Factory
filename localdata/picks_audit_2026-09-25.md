# Edge Factory — Recent picks audit (2026-08-27 to 2026-09-25)

## Overall

- archived pick rows: 619
- archived pick dates: 30
- immutable morning-baseline rows: 619
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 583
- eligible prior picks: 600
- pending/unmatched result picks: 6
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 3
- wins: 386
- hit rate: +66.2%
- priced picks: 546
- ROI: -3.9%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-25
- same-day rows excluded: 19

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 333 / 537 matches (62.0%)
- **Both Teams to Score (BTTS)**: occurred in 299 / 537 matches (55.7%)
- **Selected Team Over 1.5 Goals**: occurred in 345 / 537 matches (64.2%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 583
- **Total Hits**: 444
- **Overall Hit Rate**: 76.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=118, hits=114, hit_rate=96.6%
- `home_over_05`: recommended=27, hits=20, hit_rate=74.1%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=12, hits=11, hit_rate=91.7%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=290, hits=187, hit_rate=64.5%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2418** | scored: 2418

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 576 | 576 | 356 | 61.8% | 46.2% | +15.6% | 0.259849 |
| `match_over_45` | 449 | 449 | 118 | 26.3% | 23.9% | +2.4% | 0.191772 |
| `away_under_35` | 415 | 415 | 405 | 97.6% | 96.2% | +1.4% | 0.023628 |
| `away_under_25` | 377 | 377 | 347 | 92.0% | 92.8% | -0.7% | 0.073884 |
| `home_over_05` | 163 | 163 | 143 | 87.7% | 84.0% | +3.8% | 0.109399 |
| `home_under_35` | 156 | 156 | 152 | 97.4% | 94.9% | +2.6% | 0.026292 |
| `home_under_25` | 130 | 130 | 118 | 90.8% | 91.6% | -0.9% | 0.08302 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 30 | 30 | 27 | 90.0% | 88.4% | +1.6% | 0.088004 |
| `away_under_15` | 29 | 29 | 22 | 75.9% | 80.9% | -5.0% | 0.189004 |
| `home_under_15` | 14 | 14 | 10 | 71.4% | 81.5% | -10.1% | 0.218222 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2161 | 1567 | 72.5% | 68.3% | +4.2% | 0.134251 |
| model | 257 | 182 | 70.8% | 63.8% | +7.0% | 0.171799 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 127 | 19.2% | 19.7% | +0.5% |
| 0.2-0.3 | 269 | 24.6% | 26.8% | +2.2% |
| 0.3-0.4 | 86 | 33.2% | 46.5% | +13.3% |
| 0.4-0.5 | 464 | 44.7% | 60.8% | +16.0% |
| 0.5-0.6 | 112 | 52.7% | 62.5% | +9.8% |
| 0.8-0.9 | 341 | 84.7% | 85.9% | +1.3% |
| 0.9-1.0 | 1019 | 94.7% | 94.9% | +0.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=537, MAE=1.597747 goals, bias=-0.242961 (realized − promised), promised avg 3.516704 vs realized 3.273743

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 537 | 30.2% | 35.2% | +5.0% | 0.23766 |
| BTTS-Yes | 537 | 41.9% | 55.7% | +13.8% | 0.266542 |
| Home Over 1.5 | 537 | 64.8% | 55.3% | -9.5% | 0.254659 |
| Over 2.5 | 537 | 69.6% | 62.0% | -7.6% | 0.24057 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 225 | 8.9% | 25.8% | +16.9% |
| 0.1-0.2 | 313 | 10.4% | 26.8% | +16.5% |
| 0.2-0.3 | 7 | 23.8% | 71.4% | +47.7% |
| 0.3-0.4 | 91 | 37.3% | 54.9% | +17.6% |
| 0.4-0.5 | 437 | 43.1% | 55.6% | +12.5% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 361 | 66.7% | 60.9% | -5.8% |
| 0.7-0.8 | 157 | 74.7% | 63.1% | -11.6% |
| 0.8-0.9 | 506 | 84.5% | 63.8% | -20.7% |
| 0.9-1.0 | 50 | 92.3% | 72.0% | -20.3% |

## By rule

- `2way-unanimous avg_p>=60`: settled=12, wins=9, hit_rate=0.75, ROI=-0.016667
- `2way-unanimous avg_p>=70`: settled=117, wins=85, hit_rate=0.726496, ROI=-0.010106
- `ml-meta avg_p>=55`: settled=337, wins=205, hit_rate=0.608309, ROI=-0.066543
- `ml-meta avg_p>=60`: settled=52, wins=43, hit_rate=0.826923, ROI=0.134808
- `ml-meta avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.074444
- `ml-meta avg_p>=70`: settled=6, wins=5, hit_rate=0.833333, ROI=0.016667
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=3, wins=3, hit_rate=1.0, ROI=0.086667
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=48, wins=33, hit_rate=0.6875, ROI=0.041042
- `CERTIFIED_CLEAN`: settled=53, wins=38, hit_rate=0.716981, ROI=0.117925
- `SKIPPED_VETO`: settled=281, wins=180, hit_rate=0.640569, ROI=-0.093345
- `WATCHLIST_NO_ODDS`: settled=29, wins=19, hit_rate=0.655172, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.117333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=151, wins=101, hit_rate=0.668874, ROI=-0.035166
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.07

## By odds source

- `UNKNOWN`: settled=37, wins=23, hit_rate=0.621622, ROI=None
- `betexplorer_odds`: settled=158, wins=102, hit_rate=0.64557, ROI=-0.077215
- `bzzoiro_odds`: settled=5, wins=4, hit_rate=0.8, ROI=0.2
- `forebet_best`: settled=63, wins=46, hit_rate=0.730159, ROI=0.099365
- `scoutingstats_odds`: settled=318, wins=209, hit_rate=0.657233, ROI=-0.053491
- `zulubet`: settled=2, wins=2, hit_rate=1.0, ROI=0.335

## By odds match method

- `alias_fuzzy`: settled=26, wins=19, hit_rate=0.730769, ROI=0.09
- `betexplorer`: settled=158, wins=102, hit_rate=0.64557, ROI=-0.077215
- `exact`: settled=323, wins=213, hit_rate=0.659443, ROI=-0.049567
- `fallback`: settled=42, wins=31, hit_rate=0.738095, ROI=0.115714
- `none`: settled=34, wins=21, hit_rate=0.617647, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 158 | 102 | 0.64557 | 158 | -0.077215 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 5 | 4 | 0.8 | 5 | 0.2 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 318 | 209 | 0.657233 | 318 | -0.053491 |
| Source fallback (`SOURCE_FALLBACK`) | 42 | 31 | 0.738095 | 42 | 0.115714 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 26 | 19 | 0.730769 | 23 | 0.09 |
| No usable price (`UNMATCHED`) | 34 | 21 | 0.617647 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 281 | 180 | 0.640569 | 275 | -0.093345 |
| **trusted evidence only** | 87 | 53 | 0.609195 | 87 | -0.16931 |
| **soft evidence only** | 194 | 127 | 0.654639 | 188 | -0.058191 |
| evidence: BETEXPLORER_RESCUE | 84 | 50 | 0.595238 | 84 | -0.193214 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.5 |
| evidence: SCOUTINGSTATS_SOLE | 167 | 108 | 0.646707 | 167 | -0.07006 |
| evidence: SOURCE_FALLBACK | 13 | 10 | 0.769231 | 13 | 0.034615 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 8 | 0.03875 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 161 | 120 | 0.745342 | 161 | -0.05646 |
| odds band: 1.50-2.00 | 106 | 52 | 0.490566 | 106 | -0.183302 |
| odds band: 2.00-3.00 | 8 | 5 | 0.625 | 8 | 0.35625 |
| odds band: unpriced | 6 | 3 | 0.5 | 0 | None |
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
| veto reason: context VETO in ['league'] | 15 | 12 | 0.8 | 13 | 0.314615 |
| veto reason: context VETO in ['niche'] | 9 | 7 | 0.777778 | 9 | 0.071111 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.273333 |
| veto reason: context VETO in ['odds_band'] | 46 | 31 | 0.673913 | 46 | -0.168696 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 10 | 7 | 0.7 | 10 | -0.131 |
| veto reason: context VETO in ['team_a'] | 50 | 25 | 0.5 | 48 | -0.21125 |
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
| contrast CAUTION: BETEXPLORER_RESCUE | 28 | 20 | 0.714286 | 28 | 0.031786 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 19 | 13 | 0.684211 | 19 | 0.109474 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 239 | 158 | 0.661088 | 205 | -0.030927 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 26 | 19 | 0.730769 | 23 | 0.09 | 26 | 1.569231 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 318 | 209 | 0.657233 | 318 | -0.053491 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-24: Hapoel Rishon LeZion vs Maccabi Ahi Nazareth (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🟢 WON (Expected prob: 75.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 52.2% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.6% (Actual: 1 goals)

### 2026-09-24: Alianza vs Fuerte San Francisco (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.3% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.9% (Actual: 4 goals)

### 2026-09-24: America de Cali vs Águilas Doradas (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.59 -> 🟢 WON (Expected prob: 60.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.3% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.0% (Actual: 1 goals)

### 2026-09-24: Luís Ángel Firpo vs Cacahuatique (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.49 -> 🔴 LOST (Expected prob: 55.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.2% (Actual: 0 goals)

### 2026-09-24: Firpo vs Cacahuatique (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.41 -> 🔴 LOST (Expected prob: 77.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.5% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.8% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.2% (Actual: 0 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 86.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.4% (Actual: 0 goals)

### 2026-09-24: Masar vs Proxy (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 69.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 86.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.7% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.8% (Actual: 1 goals)

### 2026-09-24: Cameroon vs Comoros (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 66.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.6% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.9% (Actual: 4 goals)

### 2026-09-24: Hapoel Acre vs Hapoel Afula (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.82 -> 🟢 WON (Expected prob: 62.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.5% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.4% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 3 goals)

### 2026-09-24: Ironi Modi'in vs FC Ashdod (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.66 -> 🟢 WON (Expected prob: 58.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.8% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 85.7% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.7% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 4 goals)

### 2026-09-24: Portugal vs Wales (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 74.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 53.9% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 34.2% (Actual: 1 goals)

### 2026-09-24: Liechtenstein vs Lithuania (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.3 -> 🟢 WON (Expected prob: 71.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.5% (Actual: 2 goals)

### 2026-09-24: Austria vs Israel (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 65.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.2% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.0% (Actual: 4 goals)

### 2026-09-24: Tunisia vs Uganda (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🔴 LOST (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.0% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 2 goals)

### 2026-09-24: DR Congo vs Equatorial Guinea (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 61.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.7% (Actual: 2 goals)

### 2026-09-24: Norway vs Denmark (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🟢 WON (Expected prob: 58.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.8% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 5 goals)

### 2026-09-24: Rivers United vs Kun Khalifat FC (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🟢 WON (Expected prob: 76.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.9% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.4% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.3% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.1% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 31.9% (Actual: 5 goals)

### 2026-09-24: United Arab Emirates vs Yemen (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🟢 WON (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.4% (Actual: 4 goals)


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

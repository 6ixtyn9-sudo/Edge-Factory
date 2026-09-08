# Edge Factory — Recent picks audit (2026-08-11 to 2026-09-09)

## Overall

- archived pick rows: 561
- archived pick dates: 30
- immutable morning-baseline rows: 478
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 83
- unsafe regular ledgers ignored: 21
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 524
- eligible prior picks: 549
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 8
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 347
- hit rate: +66.2%
- priced picks: 492
- ROI: -3.5%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-09
- same-day rows excluded: 12

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 303 / 478 matches (63.4%)
- **Both Teams to Score (BTTS)**: occurred in 259 / 478 matches (54.2%)
- **Selected Team Over 1.5 Goals**: occurred in 323 / 478 matches (67.6%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 524
- **Total Hits**: 387
- **Overall Hit Rate**: 73.9%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=5, hits=4, hit_rate=80.0%
- `away_under_35`: recommended=31, hits=31, hit_rate=100.0%
- `home_over_05`: recommended=111, hits=94, hit_rate=84.7%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=16, hits=16, hit_rate=100.0%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=315, hits=205, hit_rate=65.1%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2392** | scored: 2392

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 514 | 514 | 324 | 63.0% | 47.3% | +15.8% | 0.256393 |
| `away_under_35` | 391 | 391 | 383 | 98.0% | 97.9% | +0.0% | 0.01944 |
| `match_over_45` | 373 | 373 | 107 | 28.7% | 23.9% | +4.7% | 0.205145 |
| `away_under_25` | 366 | 366 | 342 | 93.4% | 94.0% | -0.5% | 0.061649 |
| `home_over_05` | 338 | 338 | 299 | 88.5% | 85.2% | +3.3% | 0.102234 |
| `home_under_35` | 143 | 143 | 141 | 98.6% | 95.6% | +3.0% | 0.01485 |
| `away_under_15` | 104 | 104 | 83 | 79.8% | 81.4% | -1.6% | 0.161472 |
| `home_under_25` | 104 | 104 | 96 | 92.3% | 91.6% | +0.7% | 0.071002 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `home_under_15` | 9 | 9 | 9 | 100.0% | 81.2% | +18.8% | 0.035416 |
| `away_over_05` | 7 | 7 | 6 | 85.7% | 82.0% | +3.7% | 0.127131 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2166 | 1658 | 76.5% | 72.4% | +4.2% | 0.124599 |
| model | 226 | 166 | 73.5% | 64.5% | +9.0% | 0.167526 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 99 | 19.0% | 21.2% | +2.2% |
| 0.2-0.3 | 244 | 25.0% | 31.1% | +6.2% |
| 0.3-0.4 | 60 | 34.9% | 41.7% | +6.8% |
| 0.4-0.5 | 346 | 45.5% | 62.4% | +16.9% |
| 0.5-0.6 | 133 | 53.3% | 67.7% | +14.3% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 515 | 84.2% | 86.0% | +1.8% |
| 0.9-1.0 | 990 | 95.7% | 96.0% | +0.3% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=477, MAE=1.551216 goals, bias=-0.174822 (realized − promised), promised avg 3.510252 vs realized 3.33543

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 477 | 28.1% | 36.7% | +8.6% | 0.214754 |
| BTTS-Yes | 477 | 41.7% | 54.3% | +12.6% | 0.264065 |
| Home Over 1.5 | 477 | 66.7% | 57.2% | -9.4% | 0.255028 |
| Over 2.5 | 477 | 69.6% | 63.3% | -6.2% | 0.233657 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 259 | 8.9% | 25.5% | +16.6% |
| 0.1-0.2 | 219 | 10.4% | 28.3% | +17.9% |
| 0.2-0.3 | 7 | 21.9% | 28.6% | +6.7% |
| 0.3-0.4 | 95 | 37.4% | 53.7% | +16.2% |
| 0.4-0.5 | 374 | 43.3% | 54.5% | +11.3% |
| 0.6-0.7 | 317 | 66.7% | 60.9% | -5.8% |
| 0.7-0.8 | 147 | 74.7% | 66.0% | -8.7% |
| 0.8-0.9 | 445 | 84.4% | 67.0% | -17.4% |
| 0.9-1.0 | 45 | 91.7% | 80.0% | -11.7% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=6, wins=4, hit_rate=0.666667, ROI=-0.041667
- `2way-unanimous avg_p>=70`: settled=106, wins=82, hit_rate=0.773585, ROI=0.100753
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `ml-meta avg_p>=55`: settled=308, wins=186, hit_rate=0.603896, ROI=-0.084846
- `ml-meta avg_p>=60`: settled=28, wins=22, hit_rate=0.785714, ROI=0.098929
- `ml-meta avg_p>=65`: settled=6, wins=5, hit_rate=0.833333, ROI=0.158
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=78, wins=52, hit_rate=0.666667, ROI=0.061667
- `CERTIFIED_CLEAN`: settled=31, wins=19, hit_rate=0.612903, ROI=-0.08129
- `SKIPPED_VETO`: settled=251, wins=166, hit_rate=0.661355, ROI=-0.060729
- `WATCHLIST_NO_ODDS`: settled=26, wins=18, hit_rate=0.692308, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=16, wins=10, hit_rate=0.625, ROI=0.019286
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=112, wins=73, hit_rate=0.651786, ROI=-0.051696
- `WATCHLIST_UNKNOWN_CTX`: settled=10, wins=9, hit_rate=0.9, ROI=0.1

## By odds source

- `UNKNOWN`: settled=32, wins=19, hit_rate=0.59375, ROI=None
- `betexplorer_odds`: settled=156, wins=104, hit_rate=0.666667, ROI=-0.060769
- `bzzoiro_odds`: settled=46, wins=31, hit_rate=0.673913, ROI=0.031087
- `forebet_best`: settled=56, wins=41, hit_rate=0.732143, ROI=0.085
- `scoutingstats_odds`: settled=231, wins=149, hit_rate=0.645022, ROI=-0.064242
- `zulubet`: settled=3, wins=3, hit_rate=1.0, ROI=0.3

## By odds match method

- `alias_fuzzy`: settled=26, wins=18, hit_rate=0.692308, ROI=0.039167
- `betexplorer`: settled=156, wins=104, hit_rate=0.666667, ROI=-0.060769
- `exact`: settled=277, wins=180, hit_rate=0.649819, ROI=-0.048412
- `fallback`: settled=35, wins=26, hit_rate=0.742857, ROI=0.134857
- `none`: settled=30, wins=19, hit_rate=0.633333, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 156 | 104 | 0.666667 | 156 | -0.060769 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 46 | 31 | 0.673913 | 46 | 0.031087 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 231 | 149 | 0.645022 | 231 | -0.064242 |
| Source fallback (`SOURCE_FALLBACK`) | 35 | 26 | 0.742857 | 35 | 0.134857 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 26 | 18 | 0.692308 | 24 | 0.039167 |
| No usable price (`UNMATCHED`) | 30 | 19 | 0.633333 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 251 | 166 | 0.661355 | 247 | -0.060729 |
| **trusted evidence only** | 107 | 74 | 0.691589 | 107 | -0.049907 |
| **soft evidence only** | 144 | 92 | 0.638889 | 140 | -0.069 |
| evidence: BETEXPLORER_RESCUE | 81 | 56 | 0.691358 | 81 | -0.080494 |
| evidence: BZZOIRO_PRIMARY | 26 | 18 | 0.692308 | 26 | 0.045385 |
| evidence: SCOUTINGSTATS_SOLE | 119 | 76 | 0.638655 | 119 | -0.07605 |
| evidence: SOURCE_FALLBACK | 11 | 7 | 0.636364 | 11 | -0.116364 |
| evidence: SUSPECT_ALIAS_FUZZY | 10 | 8 | 0.8 | 10 | 0.067 |
| evidence: UNMATCHED | 4 | 1 | 0.25 | 0 | None |
| odds band: <1.50 | 156 | 117 | 0.75 | 156 | -0.035705 |
| odds band: 1.50-2.00 | 83 | 44 | 0.53012 | 83 | -0.118434 |
| odds band: 2.00-3.00 | 8 | 4 | 0.5 | 8 | 0.05 |
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
| veto reason: context VETO in ['league'] | 11 | 7 | 0.636364 | 10 | 0.032 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 49 | 39 | 0.795918 | 49 | 0.034694 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.2 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 7 | 0.777778 | 9 | -0.032222 |
| veto reason: context VETO in ['team_a'] | 39 | 22 | 0.564103 | 37 | -0.056216 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.3025 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 13 | 12 | 0.923077 | 13 | 0.243846 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.208 |
| veto reason: context VETO in ['team_h', 'team_a'] | 20 | 10 | 0.5 | 20 | -0.2125 |
| veto reason: context VETO in ['team_h'] | 61 | 35 | 0.57377 | 61 | -0.143443 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 44 | 28 | 0.636364 | 44 | 0.012045 |
| contrast CAUTION: BZZOIRO_PRIMARY | 17 | 11 | 0.647059 | 17 | 0.007059 |
| contrast CAUTION: SOURCE_FALLBACK | 17 | 13 | 0.764706 | 17 | 0.244706 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 267 | 180 | 0.674157 | 237 | -0.014051 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 26 | 18 | 0.692308 | 24 | 0.039167 | 26 | 1.517885 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 231 | 149 | 0.645022 | 231 | -0.064242 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-08: Ilves vs FF Jaro (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 62.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.8% (Actual: 2 goals)

### 2026-09-08: FC Lahti vs IFK Mariehamn (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 57.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.1% (Actual: 3 goals)

### 2026-09-08: Larne vs Bangor FC (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🟢 WON (Expected prob: 63.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.3% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.5% (Actual: 1 goals)

### 2026-09-08: Borussia Dortmund vs Villarreal (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🟢 WON (Expected prob: 58.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.8% (Actual: 5 goals)

### 2026-09-08: Wrexham FC vs Burnley (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 2.05 -> 🔴 LOST (Expected prob: 57.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.8% (Actual: 2 goals)

### 2026-09-08: Macclesfield vs Scarborough (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🔴 LOST (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.3% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.2% (Actual: 0 goals)

### 2026-09-08: Trans Narva vs Flora Tallinn (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.55 -> 🔴 LOST (Expected prob: 66.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 91.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.5% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.4% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.9% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.7% (Actual: 4 goals)

### 2026-09-08: Dagenham and Redbridge vs Dover (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 59.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.2% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 1 goals)

### 2026-09-08: Salisbury City vs Slough Town (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 67.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.1% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.7% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.7% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.7% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.2% (Actual: 6 goals)

### 2026-09-08: South Shields vs Marine (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 59.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.3% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 3 goals)

### 2026-09-08: AFC Telford Utd vs Oxford City (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 2.7 -> 🔴 LOST (Expected prob: 55.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.1% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.9% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.9% (Actual: 1 goals)


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
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual Utrecht 3-3 Go Ahead Eagles [draw])
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])

## Pending / Unmatched Result Examples

- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)

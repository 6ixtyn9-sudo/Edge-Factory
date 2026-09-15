# Edge Factory — Recent picks audit (2026-08-18 to 2026-09-16)

## Overall

- archived pick rows: 584
- archived pick dates: 30
- immutable morning-baseline rows: 574
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 10
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 546
- eligible prior picks: 570
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 4
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 365
- hit rate: +66.8%
- priced picks: 515
- ROI: -4.3%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-16
- same-day rows excluded: 14

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 319 / 500 matches (63.8%)
- **Both Teams to Score (BTTS)**: occurred in 271 / 500 matches (54.2%)
- **Selected Team Over 1.5 Goals**: occurred in 339 / 500 matches (67.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 546
- **Total Hits**: 391
- **Overall Hit Rate**: 71.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=1, hits=0, hit_rate=0.0%
- `away_under_35`: recommended=80, hits=76, hit_rate=95.0%
- `home_over_05`: recommended=43, hits=33, hit_rate=76.7%
- `home_under_25`: recommended=1, hits=1, hit_rate=100.0%
- `home_under_35`: recommended=10, hits=9, hit_rate=90.0%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=332, hits=214, hit_rate=64.5%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2401** | scored: 2401

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 539 | 539 | 342 | 63.5% | 47.5% | +16.0% | 0.256885 |
| `match_over_45` | 405 | 405 | 120 | 29.6% | 23.9% | +5.8% | 0.211641 |
| `away_under_35` | 397 | 397 | 383 | 96.5% | 97.4% | -1.0% | 0.032767 |
| `away_under_25` | 366 | 366 | 338 | 92.3% | 93.4% | -1.1% | 0.071142 |
| `home_over_05` | 250 | 250 | 221 | 88.4% | 84.5% | +3.9% | 0.103608 |
| `home_under_35` | 155 | 155 | 151 | 97.4% | 95.6% | +1.8% | 0.025376 |
| `home_under_25` | 115 | 115 | 105 | 91.3% | 91.7% | -0.4% | 0.079119 |
| `away_under_15` | 54 | 54 | 42 | 77.8% | 81.0% | -3.2% | 0.176049 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 29 | 29 | 26 | 89.7% | 88.7% | +0.9% | 0.08967 |
| `home_under_15` | 15 | 15 | 11 | 73.3% | 81.4% | -8.1% | 0.206266 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2132 | 1594 | 74.8% | 70.5% | +4.3% | 0.133363 |
| model | 269 | 194 | 72.1% | 64.5% | +7.6% | 0.182836 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 120 | 19.1% | 24.2% | +5.0% |
| 0.2-0.3 | 244 | 24.9% | 32.0% | +7.1% |
| 0.3-0.4 | 71 | 33.1% | 40.8% | +7.7% |
| 0.4-0.5 | 398 | 45.4% | 61.8% | +16.4% |
| 0.5-0.6 | 139 | 53.3% | 66.2% | +12.9% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 416 | 84.3% | 86.1% | +1.7% |
| 0.9-1.0 | 1008 | 95.4% | 94.5% | -0.8% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=499, MAE=1.594048 goals, bias=-0.149559 (realized − promised), promised avg 3.522305 vs realized 3.372745

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 499 | 29.8% | 37.5% | +7.6% | 0.217628 |
| BTTS-Yes | 499 | 41.6% | 54.3% | +12.8% | 0.266399 |
| Home Over 1.5 | 499 | 65.1% | 57.7% | -7.4% | 0.2596 |
| Over 2.5 | 499 | 69.7% | 63.7% | -6.0% | 0.233185 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 234 | 8.8% | 27.4% | +18.5% |
| 0.1-0.2 | 268 | 10.4% | 28.4% | +17.9% |
| 0.2-0.3 | 9 | 22.4% | 44.4% | +22.0% |
| 0.3-0.4 | 97 | 37.4% | 56.7% | +19.3% |
| 0.4-0.5 | 389 | 43.2% | 53.7% | +10.5% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 331 | 66.7% | 61.3% | -5.3% |
| 0.7-0.8 | 148 | 74.7% | 66.9% | -7.8% |
| 0.8-0.9 | 468 | 84.4% | 67.3% | -17.1% |
| 0.9-1.0 | 51 | 92.1% | 76.5% | -15.7% |

## By rule

- `2way-unanimous avg_p>=70`: settled=112, wins=84, hit_rate=0.75, ROI=0.024592
- `ml-meta avg_p>=55`: settled=320, wins=196, hit_rate=0.6125, ROI=-0.084868
- `ml-meta avg_p>=60`: settled=45, wins=37, hit_rate=0.822222, ROI=0.122667
- `ml-meta avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.2
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.148
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=2, wins=2, hit_rate=1.0, ROI=0.05
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=58, wins=44, hit_rate=0.758621, ROI=0.158793
- `CERTIFIED_CLEAN`: settled=31, wins=22, hit_rate=0.709677, ROI=0.067419
- `SKIPPED_VETO`: settled=274, wins=175, hit_rate=0.638686, ROI=-0.112687
- `WATCHLIST_NO_ODDS`: settled=23, wins=15, hit_rate=0.652174, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.056667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=136, wins=90, hit_rate=0.661765, ROI=-0.041838
- `WATCHLIST_UNKNOWN_CTX`: settled=7, wins=7, hit_rate=1.0, ROI=0.221429

## By odds source

- `UNKNOWN`: settled=31, wins=19, hit_rate=0.612903, ROI=None
- `betexplorer_odds`: settled=152, wins=104, hit_rate=0.684211, ROI=-0.054145
- `bzzoiro_odds`: settled=8, wins=8, hit_rate=1.0, ROI=0.5
- `forebet_best`: settled=61, wins=45, hit_rate=0.737705, ROI=0.077049
- `scoutingstats_odds`: settled=294, wins=189, hit_rate=0.642857, ROI=-0.077075

## By odds match method

- `alias_fuzzy`: settled=25, wins=18, hit_rate=0.72, ROI=0.020909
- `betexplorer`: settled=152, wins=104, hit_rate=0.684211, ROI=-0.054145
- `exact`: settled=302, wins=197, hit_rate=0.652318, ROI=-0.061788
- `fallback`: settled=39, wins=29, hit_rate=0.74359, ROI=0.108718
- `none`: settled=28, wins=17, hit_rate=0.607143, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 152 | 104 | 0.684211 | 152 | -0.054145 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 8 | 1.0 | 8 | 0.5 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 294 | 189 | 0.642857 | 294 | -0.077075 |
| Source fallback (`SOURCE_FALLBACK`) | 39 | 29 | 0.74359 | 39 | 0.108718 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 25 | 18 | 0.72 | 22 | 0.020909 |
| No usable price (`UNMATCHED`) | 28 | 17 | 0.607143 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 274 | 175 | 0.638686 | 268 | -0.112687 |
| **trusted evidence only** | 89 | 59 | 0.662921 | 89 | -0.121124 |
| **soft evidence only** | 185 | 116 | 0.627027 | 179 | -0.108492 |
| evidence: BETEXPLORER_RESCUE | 86 | 56 | 0.651163 | 86 | -0.142093 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.48 |
| evidence: SCOUTINGSTATS_SOLE | 158 | 99 | 0.626582 | 158 | -0.107405 |
| evidence: SOURCE_FALLBACK | 14 | 9 | 0.642857 | 14 | -0.147143 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.055714 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 166 | 124 | 0.746988 | 166 | -0.051988 |
| odds band: 1.50-2.00 | 95 | 45 | 0.473684 | 95 | -0.220737 |
| odds band: 2.00-3.00 | 7 | 3 | 0.428571 | 7 | -0.085714 |
| odds band: unpriced | 6 | 3 | 0.5 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 3 | 1.0 | 2 | 0.305 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 5 | 1.0 | 5 | 0.146 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 11 | 4 | 0.363636 | 11 | -0.573636 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 4 | 2 | 0.5 | 4 | -0.2025 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['league', 'team_h'] | 10 | 7 | 0.7 | 10 | -0.093 |
| veto reason: context VETO in ['league'] | 14 | 9 | 0.642857 | 12 | -0.005 |
| veto reason: context VETO in ['niche'] | 6 | 4 | 0.666667 | 6 | -0.056667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.24 |
| veto reason: context VETO in ['odds_band'] | 44 | 32 | 0.727273 | 44 | -0.071591 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.2 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 10 | 8 | 0.8 | 10 | 0.029 |
| veto reason: context VETO in ['team_a'] | 42 | 22 | 0.52381 | 40 | -0.14375 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 1 | 0.25 | 4 | -0.64 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.221818 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.446667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.123333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 16 | 7 | 0.4375 | 16 | -0.286875 |
| veto reason: context VETO in ['team_h'] | 61 | 35 | 0.57377 | 60 | -0.174833 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 35 | 25 | 0.714286 | 35 | 0.062571 |
| contrast CAUTION: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.512 |
| contrast CAUTION: SOURCE_FALLBACK | 18 | 14 | 0.777778 | 18 | 0.247778 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 227 | 158 | 0.696035 | 199 | 5e-05 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 25 | 18 | 0.72 | 22 | 0.020909 | 25 | 1.5388 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 294 | 189 | 0.642857 | 294 | -0.077075 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-15: Antigua GFC vs Suchitepéquez (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 79.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.7% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.9% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.9% (Actual: 5 goals)

### 2026-09-15: MSV Duisburg vs TSV Havelse (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.0% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.4% (Actual: 3 goals)

### 2026-09-15: Toluca W vs Tijuana W (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ 1.46 -> 🟢 WON (Expected prob: 62.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.2% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.8% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.8% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.5% (Actual: 6 goals)

### 2026-09-15: The New Saints vs Flint Town Utd (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.1 -> 🟢 WON (Expected prob: 76.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.2% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.4% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 90.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 34.8% (Actual: 5 goals)

### 2026-09-15: America De Cali vs Deportivo Pasto (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🔴 LOST (Expected prob: 73.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.3% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.2% (Actual: 1 goals)

### 2026-09-15: Elche vs Real Madrid (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.22 -> 🟢 WON (Expected prob: 72.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 26.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 92.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 88.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.4% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.0% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.1% (Actual: 5 goals)

### 2026-09-15: Young Africans vs Geita Gold (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.05 -> 🟢 WON (Expected prob: 71.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.4% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.1% (Actual: 1 goals)

### 2026-09-15: Barry Town vs Ammanford (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.18 -> 🔴 LOST (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.8% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.8% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.9% (Actual: 4 goals)

### 2026-09-15: Pen-y-Bont FC vs Briton Ferry (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 63.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.8% (Actual: 5 goals)

### 2026-09-15: Motherwell vs Aberdeen (Actual Score: **0-4**)
- **1X2 Pick**: Selected `HOME` @ 1.83 -> 🔴 LOST (Expected prob: 59.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.1% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 93.7% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.9% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.4% (Actual: 4 goals)

### 2026-09-15: Hibernian vs Kilmarnock (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 57.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.7% (Actual: 1 goals)

### 2026-09-15: Middlesbrough vs Millwall (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🔴 LOST (Expected prob: 57.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.5% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.1% (Actual: 4 goals)

### 2026-09-15: Fram Reykjavik vs Breidablik (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 55.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.7% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 90.8% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.0% (Actual: 4 goals)

### 2026-09-15: Holywell Town vs Colwyn Bay (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.51 -> 🟢 WON (Expected prob: 59.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.7% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.1% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 82.4% (Actual: 5 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.6% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.8% (Actual: 5 goals)

### 2026-09-15: Ross County vs Queen of the South (Actual Score: **8-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 72.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.1% (Actual: 8 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.4% (Actual: 8 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.4% (Actual: 8 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.2% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 31.9% (Actual: 8 goals)

### 2026-09-15: Instituto Córdoba vs Estudiantes Río Cuarto (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.5% (Actual: 3 goals)

### 2026-09-15: Landskrona BoIS vs GIF Sundsvall (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 60.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.7% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.6% (Actual: 4 goals)

### 2026-09-15: Reading vs Brentford (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.3 -> 🟢 WON (Expected prob: 63.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 83.1% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.5% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.8% (Actual: 3 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 4 |
- 2026-08-21 `POSTPONED` `SKIPPED_VETO` — Shamrock Rovers vs Shelbourne FC (verified_disposition); excluded from win/loss/ROI
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

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)
- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

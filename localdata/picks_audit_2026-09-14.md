# Edge Factory — Recent picks audit (2026-08-16 to 2026-09-14)

## Overall

- archived pick rows: 596
- archived pick dates: 30
- immutable morning-baseline rows: 542
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 54
- unsafe regular ledgers ignored: 25
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 557
- eligible prior picks: 584
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 6
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 371
- hit rate: +66.6%
- priced picks: 520
- ROI: -4.0%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-14
- same-day rows excluded: 12

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 326 / 511 matches (63.8%)
- **Both Teams to Score (BTTS)**: occurred in 279 / 511 matches (54.6%)
- **Selected Team Over 1.5 Goals**: occurred in 346 / 511 matches (67.7%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 557
- **Total Hits**: 400
- **Overall Hit Rate**: 71.8%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=15, hits=14, hit_rate=93.3%
- `away_under_35`: recommended=68, hits=65, hit_rate=95.6%
- `home_over_05`: recommended=59, hits=48, hit_rate=81.4%
- `home_under_35`: recommended=13, hits=12, hit_rate=92.3%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=341, hits=219, hit_rate=64.2%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2486** | scored: 2486

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 550 | 550 | 349 | 63.5% | 47.5% | +16.0% | 0.257331 |
| `away_under_35` | 409 | 409 | 396 | 96.8% | 97.8% | -1.0% | 0.029413 |
| `match_over_45` | 401 | 401 | 117 | 29.2% | 23.8% | +5.3% | 0.209356 |
| `away_under_25` | 378 | 378 | 349 | 92.3% | 93.6% | -1.3% | 0.071359 |
| `home_over_05` | 284 | 284 | 252 | 88.7% | 84.5% | +4.2% | 0.101247 |
| `home_under_35` | 157 | 157 | 153 | 97.5% | 95.6% | +1.8% | 0.025068 |
| `home_under_25` | 115 | 115 | 105 | 91.3% | 91.7% | -0.4% | 0.079161 |
| `away_under_15` | 76 | 76 | 58 | 76.3% | 81.3% | -5.0% | 0.184122 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 24 | 24 | 22 | 91.7% | 89.2% | +2.5% | 0.070708 |
| `home_under_15` | 16 | 16 | 12 | 75.0% | 81.4% | -6.4% | 0.1956 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2217 | 1668 | 75.2% | 71.2% | +4.1% | 0.131743 |
| model | 269 | 194 | 72.1% | 64.5% | +7.6% | 0.182836 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 119 | 19.1% | 24.4% | +5.3% |
| 0.2-0.3 | 244 | 24.9% | 31.6% | +6.6% |
| 0.3-0.4 | 69 | 33.2% | 40.6% | +7.4% |
| 0.4-0.5 | 404 | 45.4% | 61.9% | +16.5% |
| 0.5-0.6 | 143 | 53.3% | 65.7% | +12.5% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 469 | 84.2% | 85.7% | +1.5% |
| 0.9-1.0 | 1033 | 95.6% | 94.8% | -0.8% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=510, MAE=1.592784 goals, bias=-0.134118 (realized − promised), promised avg 3.516471 vs realized 3.382353

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 510 | 29.4% | 37.3% | +7.9% | 0.220988 |
| BTTS-Yes | 510 | 41.7% | 54.7% | +13.0% | 0.265139 |
| Home Over 1.5 | 510 | 65.5% | 57.8% | -7.6% | 0.257302 |
| Over 2.5 | 510 | 69.7% | 63.7% | -6.0% | 0.233968 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 252 | 8.9% | 26.6% | +17.7% |
| 0.1-0.2 | 261 | 10.4% | 29.1% | +18.7% |
| 0.2-0.3 | 8 | 21.9% | 37.5% | +15.6% |
| 0.3-0.4 | 100 | 37.4% | 53.0% | +15.6% |
| 0.4-0.5 | 398 | 43.3% | 55.3% | +12.0% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 340 | 66.7% | 61.8% | -4.9% |
| 0.7-0.8 | 150 | 74.7% | 66.0% | -8.7% |
| 0.8-0.9 | 479 | 84.4% | 67.6% | -16.7% |
| 0.9-1.0 | 51 | 92.2% | 72.5% | -19.6% |

## By rule

- `2way-unanimous avg_p>=70`: settled=113, wins=84, hit_rate=0.743363, ROI=0.018469
- `ml-meta avg_p>=55`: settled=340, wins=212, hit_rate=0.623529, ROI=-0.063062
- `ml-meta avg_p>=60`: settled=32, wins=25, hit_rate=0.78125, ROI=0.0775
- `ml-meta avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.05
- `ml-meta avg_p>=70`: settled=11, wins=10, hit_rate=0.909091, ROI=0.172727
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=2, wins=2, hit_rate=1.0, ROI=0.05
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=68, wins=49, hit_rate=0.720588, ROI=0.121471
- `CERTIFIED_CLEAN`: settled=28, wins=19, hit_rate=0.678571, ROI=0.022143
- `SKIPPED_VETO`: settled=273, wins=175, hit_rate=0.641026, ROI=-0.099326
- `WATCHLIST_NO_ODDS`: settled=29, wins=20, hit_rate=0.689655, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.056667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=135, wins=89, hit_rate=0.659259, ROI=-0.041111
- `WATCHLIST_UNKNOWN_CTX`: settled=7, wins=7, hit_rate=1.0, ROI=0.221429

## By odds source

- `UNKNOWN`: settled=37, wins=24, hit_rate=0.648649, ROI=None
- `betexplorer_odds`: settled=161, wins=109, hit_rate=0.677019, ROI=-0.054472
- `bzzoiro_odds`: settled=17, wins=15, hit_rate=0.882353, ROI=0.358235
- `forebet_best`: settled=59, wins=43, hit_rate=0.728814, ROI=0.073729
- `scoutingstats_odds`: settled=283, wins=180, hit_rate=0.636042, ROI=-0.079364

## By odds match method

- `alias_fuzzy`: settled=25, wins=18, hit_rate=0.72, ROI=0.020909
- `betexplorer`: settled=161, wins=109, hit_rate=0.677019, ROI=-0.054472
- `exact`: settled=300, wins=195, hit_rate=0.65, ROI=-0.054567
- `fallback`: settled=37, wins=27, hit_rate=0.72973, ROI=0.105135
- `none`: settled=34, wins=22, hit_rate=0.647059, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 161 | 109 | 0.677019 | 161 | -0.054472 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 17 | 15 | 0.882353 | 17 | 0.358235 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 283 | 180 | 0.636042 | 283 | -0.079364 |
| Source fallback (`SOURCE_FALLBACK`) | 37 | 27 | 0.72973 | 37 | 0.105135 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 25 | 18 | 0.72 | 22 | 0.020909 |
| No usable price (`UNMATCHED`) | 34 | 22 | 0.647059 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 273 | 175 | 0.641026 | 267 | -0.099326 |
| **trusted evidence only** | 99 | 68 | 0.686869 | 99 | -0.071818 |
| **soft evidence only** | 174 | 107 | 0.614943 | 168 | -0.115536 |
| evidence: BETEXPLORER_RESCUE | 91 | 61 | 0.67033 | 91 | -0.105385 |
| evidence: BZZOIRO_PRIMARY | 8 | 7 | 0.875 | 8 | 0.31 |
| evidence: SCOUTINGSTATS_SOLE | 148 | 91 | 0.614865 | 148 | -0.114257 |
| evidence: SOURCE_FALLBACK | 13 | 8 | 0.615385 | 13 | -0.162308 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.055714 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 164 | 122 | 0.743902 | 164 | -0.048049 |
| odds band: 1.50-2.00 | 96 | 47 | 0.489583 | 96 | -0.187917 |
| odds band: 2.00-3.00 | 7 | 3 | 0.428571 | 7 | -0.085714 |
| odds band: unpriced | 6 | 3 | 0.5 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: context VETO in ['league', 'niche'] | 2 | 2 | 1.0 | 1 | 0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 5 | 1.0 | 5 | 0.146 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 10 | 4 | 0.4 | 10 | -0.531 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.063333 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['league', 'team_h'] | 8 | 5 | 0.625 | 8 | -0.15625 |
| veto reason: context VETO in ['league'] | 11 | 7 | 0.636364 | 9 | -0.007778 |
| veto reason: context VETO in ['niche'] | 5 | 3 | 0.6 | 5 | -0.118 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.24 |
| veto reason: context VETO in ['odds_band'] | 47 | 35 | 0.744681 | 47 | -0.03766 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.2 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.12 |
| veto reason: context VETO in ['team_a'] | 45 | 22 | 0.488889 | 43 | -0.205116 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 1 | 0.25 | 4 | -0.64 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.221818 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.446667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.123333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 18 | 9 | 0.5 | 18 | -0.200556 |
| veto reason: context VETO in ['team_h'] | 63 | 37 | 0.587302 | 62 | -0.128548 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 42 | 28 | 0.666667 | 42 | 0.011667 |
| contrast CAUTION: BZZOIRO_PRIMARY | 9 | 8 | 0.888889 | 9 | 0.401111 |
| contrast CAUTION: SOURCE_FALLBACK | 17 | 13 | 0.764706 | 17 | 0.244706 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 249 | 173 | 0.694779 | 215 | 0.005628 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 25 | 18 | 0.72 | 22 | 0.020909 | 25 | 1.5388 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 283 | 180 | 0.636042 | 283 | -0.079364 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-13: Colorado Rapids vs Montreal Impact (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🟢 WON (Expected prob: 57.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.6% (Actual: 1 goals)

### 2026-09-13: PAOK vs Aris Thessalonikis (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.51 -> 🟢 WON (Expected prob: 66.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.0% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.2% (Actual: 2 goals)

### 2026-09-13: Valur Reykjavik vs Thor Akureyri (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.2% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.0% (Actual: 5 goals)

### 2026-09-13: Suwon City FC vs Cheonan City (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.58 -> 🔴 LOST (Expected prob: 56.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.0% (Actual: 2 goals)

### 2026-09-13: Levante vs Barcelona (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.14 -> 🟢 WON (Expected prob: 74.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.3% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 18.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 94.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.5% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.8% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.4% (Actual: 6 goals)

### 2026-09-13: Volna Nizhegorodskaya vs Kvant Obninsk (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.05 -> 🟢 WON (Expected prob: 86.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 100.0% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 100.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 92.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.6% (Actual: 1 goals)

### 2026-09-13: Benfica vs Gil Vicente (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🟢 WON (Expected prob: 77.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.2% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.1% (Actual: 4 goals)

### 2026-09-13: PSV Eindhoven vs Sparta Rotterdam (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.19 -> 🟢 WON (Expected prob: 72.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.0% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.5% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 31.3% (Actual: 5 goals)

### 2026-09-13: RB Leipzig vs Hamburger SV (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 71.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.7% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.8% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 31.1% (Actual: 5 goals)

### 2026-09-13: Botev Vratsa vs Levski Sofia (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.4 -> 🔴 LOST (Expected prob: 69.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 31.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 83.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected 80.4% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 94.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.5% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.5% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.3% (Actual: 0 goals)

### 2026-09-13: Stromsgodset IF vs Sandnes Ulf (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 65.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.3% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.5% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.0% (Actual: 5 goals)

### 2026-09-13: Busan I'Park vs Gimhae City (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 63.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.2% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.3% (Actual: 2 goals)

### 2026-09-13: Teplice vs Slavia Praha (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.55 -> 🟢 WON (Expected prob: 59.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 88.1% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.3% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.7% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.2% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.3% (Actual: 2 goals)

### 2026-09-13: Prachuap vs Sukhothai FC (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 59.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.6% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.4% (Actual: 1 goals)

### 2026-09-13: Galatasaray vs Kocaelispor (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.0% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.3% (Actual: 1 goals)

### 2026-09-13: Stjarnan FC vs IBV Vestmannaeyjar (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.69 -> 🟢 WON (Expected prob: 57.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.1% (Actual: 2 goals)

### 2026-09-13: Heerenveen vs SC Telstar (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 56.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.6% (Actual: 0 goals)

### 2026-09-13: Sassuolo vs Juventus (Actual Score: **3-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.61 -> 🔴 LOST (Expected prob: 56.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 87.1% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.4% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 91.3% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.7% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.6% (Actual: 5 goals)

### 2026-09-13: SV Elversberg vs Bayern Munich (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.2 -> 🟢 WON (Expected prob: 61.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.5% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 90.3% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.7% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.8% (Actual: 3 goals)

### 2026-09-13: BFC Daugavpils vs Rigas Futbola skola (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.29 -> 🟢 WON (Expected prob: 59.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 88.6% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.3% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.0% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.3% (Actual: 3 goals)

### 2026-09-13: Viktoria Plzen vs Sigma Olomouc (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 58.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 92.3% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 5 goals)

### 2026-09-13: Stade Brestois 29 vs Paris Saint Germain (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 58.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 95.1% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.8% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.6% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 81.0% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.3% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.0% (Actual: 1 goals)

### 2026-09-13: Sporting Kansas City vs Los Angeles FC (Actual Score: **3-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.71 -> 🔴 LOST (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.1% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 88.0% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.5% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 91.6% (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.3% (Actual: 4 goals)

### 2026-09-13: HNK Hajduk Split vs NK Slaven Belupo (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 75.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 77.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 89.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.9% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.8% (Actual: 1 goals)

### 2026-09-13: IF Elfsborg vs Kalmar FF (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 56.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.4% (Actual: 1 goals)

### 2026-09-13: Viking FK vs Kristiansund BK (Actual Score: **8-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 9 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 8 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.9% (Actual: 9 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.9% (Actual: 9 goals)

### 2026-09-13: PEC Zwolle vs Feyenoord (Actual Score: **0-7**)
- **1X2 Pick**: Selected `AWAY` @ 1.45 -> 🟢 WON (Expected prob: 65.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.5% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.0% (Actual: 7 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 89.4% (Actual: 7 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.4% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.5% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.4% (Actual: 7 goals)

### 2026-09-13: Neom Sc vs Al-Fateh (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 63.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.1% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.6% (Actual: 6 goals)

### 2026-09-13: Excelsior vs Utrecht (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 2.2 -> 🔴 LOST (Expected prob: 56.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.2% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.4% (Actual: 3 goals)

### 2026-09-13: Viking vs Kristiansund BK (Actual Score: **8-1**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🟢 WON (Expected prob: 69.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.4% (Actual: 9 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 8 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.4% (Actual: 9 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.8% (Actual: 9 goals)

### 2026-09-13: Legia Warszawa vs Widzew Lodz (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🔴 LOST (Expected prob: 56.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.8% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.3% (Actual: 2 goals)

### 2026-09-13: Radomlje vs Maribor (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.65 -> 🟢 WON (Expected prob: 55.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 86.1% (Actual: 3 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.0% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.2% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 3 goals)

### 2026-09-13: Moss vs Haugesund (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.55 -> 🟢 WON (Expected prob: 55.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.9% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 86.2% (Actual: 4 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.2% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.0% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.1% (Actual: 5 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 6 |
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
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 3-3 Go Ahead Eagles [draw])
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
- 2026-09-13 `SKIPPED_VETO` `ml-meta avg_p>=55` — Flamengo vs Corinthians -> HOME @ 1.33 (pending_or_unmatched_result); keys=['flamengo']/['corinthia']
- 2026-09-13 `SKIPPED_VETO` `ml-meta avg_p>=55` — Colo Colo vs Deportes Concepción -> HOME @ 1.42 (pending_or_unmatched_result); keys=['colocolo']/['deportesc']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)
- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

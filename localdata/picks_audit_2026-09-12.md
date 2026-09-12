# Edge Factory — Recent picks audit (2026-08-14 to 2026-09-12)

## Overall

- archived pick rows: 594
- archived pick dates: 30
- immutable morning-baseline rows: 511
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 83
- unsafe regular ledgers ignored: 25
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 528
- eligible prior picks: 554
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 7
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 352
- hit rate: +66.7%
- priced picks: 494
- ROI: -2.9%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-12
- same-day rows excluded: 40

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 307 / 482 matches (63.7%)
- **Both Teams to Score (BTTS)**: occurred in 256 / 482 matches (53.1%)
- **Selected Team Over 1.5 Goals**: occurred in 327 / 482 matches (67.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 528
- **Total Hits**: 380
- **Overall Hit Rate**: 72.0%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=4, hits=4, hit_rate=100.0%
- `away_under_35`: recommended=34, hits=34, hit_rate=100.0%
- `home_over_05`: recommended=93, hits=77, hit_rate=82.8%
- `home_under_25`: recommended=1, hits=1, hit_rate=100.0%
- `home_under_35`: recommended=15, hits=14, hit_rate=93.3%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=322, hits=208, hit_rate=64.6%
- `match_over_35`: recommended=16, hits=8, hit_rate=50.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2410** | scored: 2410

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 521 | 521 | 330 | 63.3% | 47.5% | +15.9% | 0.25669 |
| `away_under_35` | 393 | 393 | 383 | 97.5% | 97.9% | -0.4% | 0.023533 |
| `match_over_45` | 372 | 372 | 107 | 28.8% | 23.9% | +4.9% | 0.206326 |
| `away_under_25` | 364 | 364 | 337 | 92.6% | 93.9% | -1.3% | 0.068989 |
| `home_over_05` | 321 | 321 | 283 | 88.2% | 84.9% | +3.3% | 0.104833 |
| `home_under_35` | 145 | 145 | 141 | 97.2% | 95.8% | +1.4% | 0.02681 |
| `home_under_25` | 103 | 103 | 95 | 92.2% | 91.6% | +0.7% | 0.071663 |
| `away_under_15` | 96 | 96 | 76 | 79.2% | 81.5% | -2.3% | 0.165307 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 31 | 31 | 15 | 48.4% | 37.8% | +10.6% | 0.281875 |
| `home_under_15` | 13 | 13 | 10 | 76.9% | 81.4% | -4.5% | 0.179679 |
| `away_over_05` | 8 | 8 | 7 | 87.5% | 84.9% | +2.6% | 0.11806 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2158 | 1636 | 75.8% | 71.8% | +4.0% | 0.129903 |
| model | 252 | 182 | 72.2% | 64.5% | +7.8% | 0.176725 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 105 | 19.1% | 21.9% | +2.8% |
| 0.2-0.3 | 235 | 25.0% | 31.5% | +6.5% |
| 0.3-0.4 | 73 | 34.2% | 42.5% | +8.3% |
| 0.4-0.5 | 367 | 45.5% | 62.7% | +17.2% |
| 0.5-0.6 | 139 | 53.3% | 65.5% | +12.2% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 501 | 84.2% | 85.4% | +1.2% |
| 0.9-1.0 | 985 | 95.7% | 95.2% | -0.5% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=481, MAE=1.552682 goals, bias=-0.169439 (realized − promised), promised avg 3.512474 vs realized 3.343035

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 481 | 28.0% | 37.2% | +9.2% | 0.213304 |
| BTTS-Yes | 481 | 41.7% | 53.2% | +11.5% | 0.261816 |
| Home Over 1.5 | 481 | 66.8% | 57.6% | -9.2% | 0.258859 |
| Over 2.5 | 481 | 69.6% | 63.6% | -6.0% | 0.232362 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 249 | 8.9% | 25.7% | +16.8% |
| 0.1-0.2 | 234 | 10.4% | 29.1% | +18.6% |
| 0.2-0.3 | 7 | 21.9% | 28.6% | +6.7% |
| 0.3-0.4 | 91 | 37.5% | 53.8% | +16.4% |
| 0.4-0.5 | 381 | 43.3% | 53.3% | +10.0% |
| 0.6-0.7 | 319 | 66.6% | 60.8% | -5.8% |
| 0.7-0.8 | 146 | 74.7% | 67.1% | -7.5% |
| 0.8-0.9 | 450 | 84.4% | 67.3% | -17.0% |
| 0.9-1.0 | 47 | 91.9% | 78.7% | -13.1% |

## By rule

- `2way-unanimous avg_p>=70`: settled=104, wins=79, hit_rate=0.759615, ROI=0.079889
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `ml-meta avg_p>=55`: settled=313, wins=193, hit_rate=0.616613, ROI=-0.065556
- `ml-meta avg_p>=60`: settled=31, wins=24, hit_rate=0.774194, ROI=0.073548
- `ml-meta avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.0775
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=2, wins=2, hit_rate=1.0, ROI=0.05
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=73, wins=50, hit_rate=0.684932, ROI=0.090548
- `CERTIFIED_CLEAN`: settled=32, wins=19, hit_rate=0.59375, ROI=-0.119375
- `SKIPPED_VETO`: settled=252, wins=166, hit_rate=0.65873, ROI=-0.067782
- `WATCHLIST_NO_ODDS`: settled=28, wins=19, hit_rate=0.678571, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=16, wins=10, hit_rate=0.625, ROI=0.019286
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=119, wins=81, hit_rate=0.680672, ROI=-0.01
- `WATCHLIST_UNKNOWN_CTX`: settled=8, wins=7, hit_rate=0.875, ROI=0.06875

## By odds source

- `UNKNOWN`: settled=34, wins=20, hit_rate=0.588235, ROI=None
- `betexplorer_odds`: settled=160, wins=103, hit_rate=0.64375, ROI=-0.096937
- `bzzoiro_odds`: settled=32, wins=25, hit_rate=0.78125, ROI=0.215
- `forebet_best`: settled=58, wins=42, hit_rate=0.724138, ROI=0.068276
- `scoutingstats_odds`: settled=244, wins=162, hit_rate=0.663934, ROI=-0.039836

## By odds match method

- `alias_fuzzy`: settled=24, wins=16, hit_rate=0.666667, ROI=0.010909
- `betexplorer`: settled=160, wins=103, hit_rate=0.64375, ROI=-0.096937
- `exact`: settled=276, wins=187, hit_rate=0.677536, ROI=-0.01029
- `fallback`: settled=36, wins=26, hit_rate=0.722222, ROI=0.103333
- `none`: settled=32, wins=20, hit_rate=0.625, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 160 | 103 | 0.64375 | 160 | -0.096937 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 32 | 25 | 0.78125 | 32 | 0.215 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 244 | 162 | 0.663934 | 244 | -0.039836 |
| Source fallback (`SOURCE_FALLBACK`) | 36 | 26 | 0.722222 | 36 | 0.103333 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 24 | 16 | 0.666667 | 22 | 0.010909 |
| No usable price (`UNMATCHED`) | 32 | 20 | 0.625 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 252 | 166 | 0.65873 | 248 | -0.067782 |
| **trusted evidence only** | 103 | 71 | 0.68932 | 103 | -0.057961 |
| **soft evidence only** | 149 | 95 | 0.637584 | 145 | -0.074759 |
| evidence: BETEXPLORER_RESCUE | 87 | 58 | 0.666667 | 87 | -0.115402 |
| evidence: BZZOIRO_PRIMARY | 16 | 13 | 0.8125 | 16 | 0.254375 |
| evidence: SCOUTINGSTATS_SOLE | 125 | 81 | 0.648 | 125 | -0.06824 |
| evidence: SOURCE_FALLBACK | 12 | 7 | 0.583333 | 12 | -0.19 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 8 | -0.00375 |
| evidence: UNMATCHED | 4 | 1 | 0.25 | 0 | None |
| odds band: <1.50 | 157 | 119 | 0.757962 | 157 | -0.025159 |
| odds band: 1.50-2.00 | 83 | 42 | 0.506024 | 83 | -0.159759 |
| odds band: 2.00-3.00 | 8 | 4 | 0.5 | 8 | 0.05 |
| odds band: unpriced | 4 | 1 | 0.25 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: context VETO in ['league', 'niche'] | 2 | 2 | 1.0 | 1 | 0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 4 | 4 | 1.0 | 4 | 0.12 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 9 | 4 | 0.444444 | 9 | -0.478889 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.595 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['league', 'team_h'] | 4 | 2 | 0.5 | 4 | -0.2675 |
| veto reason: context VETO in ['league'] | 10 | 6 | 0.6 | 9 | -0.007778 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 47 | 36 | 0.765957 | 47 | -0.008936 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.2 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.12 |
| veto reason: context VETO in ['team_a'] | 40 | 20 | 0.5 | 38 | -0.157368 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.3025 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 14 | 13 | 0.928571 | 14 | 0.255714 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.208 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 9 | 0.529412 | 17 | -0.153529 |
| veto reason: context VETO in ['team_h'] | 62 | 37 | 0.596774 | 62 | -0.120806 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 43 | 27 | 0.627907 | 43 | -0.005349 |
| contrast CAUTION: BZZOIRO_PRIMARY | 13 | 10 | 0.769231 | 13 | 0.206154 |
| contrast CAUTION: SOURCE_FALLBACK | 17 | 13 | 0.764706 | 17 | 0.244706 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 260 | 174 | 0.669231 | 228 | -0.021535 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 24 | 16 | 0.666667 | 22 | 0.010909 | 24 | 1.527292 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 244 | 162 | 0.663934 | 244 | -0.039836 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-11: Burgos CF vs AD Ceuta (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.68 -> 🟢 WON (Expected prob: 60.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.1% (Actual: 4 goals)

### 2026-09-11: FC Copenhagen vs AC Horsens (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🟢 WON (Expected prob: 68.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 42.9% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.1% (Actual: 2 goals)

### 2026-09-11: Al-Qadisiyah vs Al-Ettifaq (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🔴 LOST (Expected prob: 67.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.3% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 42.2% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 95.9% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.5% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.0% (Actual: 6 goals)

### 2026-09-11: AZ Alkmaar vs Willem II Tilburg (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.17 -> 🔴 LOST (Expected prob: 78.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 92.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.2% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.5% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 52.5% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.5% (Actual: 2 goals)

### 2026-09-11: Ammanford vs Caernarfon Town (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.18 -> 🟢 WON (Expected prob: 78.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 81.4% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 91.4% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 38.4% (Actual: 5 goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 90.8% (Actual: 5 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 85.1% (Actual: 5 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.7% (Actual: 5 goals)

### 2026-09-11: Cork City vs Cobh Ramblers (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🔴 LOST (Expected prob: 62.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.9% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 95.0% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.2% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.8% (Actual: 5 goals)

### 2026-09-11: Rapperswil vs Yverdon-Sport (Actual Score: **2-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.98 -> 🔴 LOST (Expected prob: 60.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.7% (Actual: 2 goals)
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected 87.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 38.6% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.2% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.8% (Actual: 2 home goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 82.0% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.9% (Actual: 2 goals)

### 2026-09-11: Adelaide City vs West Torrens (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.87 -> 🔴 LOST (Expected prob: 55.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 32.0% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.2% (Actual: 4 goals)

### 2026-09-11: Besiktas vs Erzurum BB (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 61.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 35.7% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.3% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 3 goals)

### 2026-09-11: Tampines Rovers vs Balestier Khalsa (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.31 -> 🟢 WON (Expected prob: 60.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 35.5% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.4% (Actual: 2 goals)

### 2026-09-11: Wexford Youths vs Finn Harps (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.41 -> 🔴 LOST (Expected prob: 60.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.2% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.2% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 4 goals)

### 2026-09-11: Denbigh Town vs Bala Town (Actual Score: **5-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.75 -> 🔴 LOST (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.0% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 85.8% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.2% (Actual: 7 goals)
    - [🔴 MISS] **Home Team Under 3.5 Goals**: expected 93.1% (Actual: 5 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 90.0% (Actual: 5 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.7% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.2% (Actual: 7 goals)

### 2026-09-11: Bodø / Glimt W vs Fortuna Ålesund W (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 77.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 80.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 92.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 53.9% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 85.0% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.3% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.2% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.3% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 82.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.1% (Actual: 2 goals)

### 2026-09-11: Ogre United vs FK Liepaja (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 55.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 85.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.0% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.8% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.3% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.1% (Actual: 4 goals)

### 2026-09-11: Emmen vs De Graafschap (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 2.0 -> 🔴 LOST (Expected prob: 74.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.6% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 50.7% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.4% (Actual: 3 goals)

### 2026-09-11: Sport Recife vs Ponte Preta (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🟢 WON (Expected prob: 74.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 53.7% (Actual: 2 goals)

### 2026-09-11: AC Pisa vs Virtus Entella (Actual Score: **1-4**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🔴 LOST (Expected prob: 63.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 36.4% (Actual: 5 goals)

### 2026-09-11: Cienciano vs Montevideo City Torque (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 67.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 41.4% (Actual: 2 goals)

### 2026-09-11: Galway United vs Bohemians FC (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.8 -> 🟢 WON (Expected prob: 58.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 87.0% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.5% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.8% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.3% (Actual: 2 home goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 81.3% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.1% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.0% (Actual: 5 goals)

### 2026-09-11: Kyoto Sanga vs Kashiwa Reysol (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.8 -> 🟢 WON (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 86.9% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.3% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.8% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.8% (Actual: 2 home goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 81.0% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.0% (Actual: 5 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 7 |
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

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)
- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

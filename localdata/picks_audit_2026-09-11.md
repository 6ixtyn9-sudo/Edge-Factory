# Edge Factory — Recent picks audit (2026-08-13 to 2026-09-11)

## Overall

- archived pick rows: 567
- archived pick dates: 30
- immutable morning-baseline rows: 484
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 83
- unsafe regular ledgers ignored: 24
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 521
- eligible prior picks: 547
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 7
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 349
- hit rate: +67.0%
- priced picks: 489
- ROI: -2.6%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-11
- same-day rows excluded: 20

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 303 / 475 matches (63.8%)
- **Both Teams to Score (BTTS)**: occurred in 253 / 475 matches (53.3%)
- **Selected Team Over 1.5 Goals**: occurred in 321 / 475 matches (67.6%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 521
- **Total Hits**: 380
- **Overall Hit Rate**: 72.9%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=34, hits=34, hit_rate=100.0%
- `home_over_05`: recommended=99, hits=83, hit_rate=83.8%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=18, hits=17, hit_rate=94.4%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=319, hits=208, hit_rate=65.2%
- `match_over_35`: recommended=5, hits=1, hit_rate=20.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2377** | scored: 2377

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 518 | 518 | 328 | 63.3% | 47.4% | +16.0% | 0.256712 |
| `away_under_35` | 391 | 391 | 382 | 97.7% | 97.9% | -0.2% | 0.021541 |
| `match_over_45` | 366 | 366 | 104 | 28.4% | 23.9% | +4.5% | 0.203695 |
| `away_under_25` | 362 | 362 | 339 | 93.6% | 94.0% | -0.3% | 0.059848 |
| `home_over_05` | 327 | 327 | 289 | 88.4% | 85.0% | +3.3% | 0.102966 |
| `home_under_35` | 144 | 144 | 141 | 97.9% | 95.7% | +2.2% | 0.021086 |
| `away_under_15` | 102 | 102 | 81 | 79.4% | 81.5% | -2.0% | 0.163935 |
| `home_under_25` | 102 | 102 | 94 | 92.2% | 91.5% | +0.6% | 0.07235 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 11 | 11 | 4 | 36.4% | 34.4% | +2.0% | 0.220486 |
| `home_under_15` | 9 | 9 | 9 | 100.0% | 81.3% | +18.7% | 0.034943 |
| `away_over_05` | 2 | 2 | 2 | 100.0% | 80.6% | +19.4% | 0.03763 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2137 | 1632 | 76.4% | 72.2% | +4.2% | 0.125154 |
| model | 240 | 175 | 72.9% | 64.5% | +8.4% | 0.170805 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 101 | 19.1% | 20.8% | +1.7% |
| 0.2-0.3 | 235 | 25.0% | 31.1% | +6.1% |
| 0.3-0.4 | 63 | 34.3% | 39.7% | +5.4% |
| 0.4-0.5 | 358 | 45.5% | 62.6% | +17.1% |
| 0.5-0.6 | 133 | 53.3% | 67.7% | +14.3% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 500 | 84.2% | 86.0% | +1.8% |
| 0.9-1.0 | 982 | 95.7% | 95.8% | +0.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=474, MAE=1.551835 goals, bias=-0.181203 (realized − promised), promised avg 3.510316 vs realized 3.329114

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 474 | 27.9% | 36.1% | +8.2% | 0.209305 |
| BTTS-Yes | 474 | 41.7% | 53.4% | +11.7% | 0.262848 |
| Home Over 1.5 | 474 | 66.8% | 57.4% | -9.5% | 0.256231 |
| Over 2.5 | 474 | 69.5% | 63.7% | -5.8% | 0.231098 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 250 | 8.9% | 25.6% | +16.7% |
| 0.1-0.2 | 226 | 10.4% | 27.0% | +16.6% |
| 0.2-0.3 | 7 | 21.9% | 28.6% | +6.7% |
| 0.3-0.4 | 92 | 37.4% | 55.4% | +18.0% |
| 0.4-0.5 | 373 | 43.3% | 53.1% | +9.8% |
| 0.6-0.7 | 316 | 66.6% | 60.4% | -6.2% |
| 0.7-0.8 | 144 | 74.6% | 68.1% | -6.6% |
| 0.8-0.9 | 444 | 84.4% | 67.1% | -17.3% |
| 0.9-1.0 | 44 | 91.9% | 79.5% | -12.3% |

## By rule

- `2way-unanimous avg_p>=70`: settled=102, wins=78, hit_rate=0.764706, ROI=0.091348
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `ml-meta avg_p>=55`: settled=314, wins=195, hit_rate=0.621019, ROI=-0.065619
- `ml-meta avg_p>=60`: settled=28, wins=22, hit_rate=0.785714, ROI=0.098929
- `ml-meta avg_p>=65`: settled=6, wins=5, hit_rate=0.833333, ROI=0.158
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=2, wins=2, hit_rate=1.0, ROI=0.05
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=75, wins=51, hit_rate=0.68, ROI=0.080667
- `CERTIFIED_CLEAN`: settled=30, wins=18, hit_rate=0.6, ROI=-0.112
- `SKIPPED_VETO`: settled=252, wins=168, hit_rate=0.666667, ROI=-0.056331
- `WATCHLIST_NO_ODDS`: settled=26, wins=18, hit_rate=0.692308, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=16, wins=10, hit_rate=0.625, ROI=0.019286
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=114, wins=77, hit_rate=0.675439, ROI=-0.021754
- `WATCHLIST_UNKNOWN_CTX`: settled=8, wins=7, hit_rate=0.875, ROI=0.06875

## By odds source

- `UNKNOWN`: settled=32, wins=19, hit_rate=0.59375, ROI=None
- `betexplorer_odds`: settled=154, wins=102, hit_rate=0.662338, ROI=-0.072468
- `bzzoiro_odds`: settled=41, wins=30, hit_rate=0.731707, ROI=0.113415
- `forebet_best`: settled=56, wins=41, hit_rate=0.732143, ROI=0.085
- `scoutingstats_odds`: settled=238, wins=157, hit_rate=0.659664, ROI=-0.047017

## By odds match method

- `alias_fuzzy`: settled=23, wins=15, hit_rate=0.652174, ROI=0.001905
- `betexplorer`: settled=154, wins=102, hit_rate=0.662338, ROI=-0.072468
- `exact`: settled=279, wins=187, hit_rate=0.670251, ROI=-0.023441
- `fallback`: settled=35, wins=26, hit_rate=0.742857, ROI=0.134857
- `none`: settled=30, wins=19, hit_rate=0.633333, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 154 | 102 | 0.662338 | 154 | -0.072468 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 41 | 30 | 0.731707 | 41 | 0.113415 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 238 | 157 | 0.659664 | 238 | -0.047017 |
| Source fallback (`SOURCE_FALLBACK`) | 35 | 26 | 0.742857 | 35 | 0.134857 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 23 | 15 | 0.652174 | 21 | 0.001905 |
| No usable price (`UNMATCHED`) | 30 | 19 | 0.633333 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 252 | 168 | 0.666667 | 248 | -0.056331 |
| **trusted evidence only** | 106 | 75 | 0.707547 | 106 | -0.035377 |
| **soft evidence only** | 146 | 93 | 0.636986 | 142 | -0.071972 |
| evidence: BETEXPLORER_RESCUE | 83 | 58 | 0.698795 | 83 | -0.074096 |
| evidence: BZZOIRO_PRIMARY | 23 | 17 | 0.73913 | 23 | 0.104348 |
| evidence: SCOUTINGSTATS_SOLE | 124 | 80 | 0.645161 | 124 | -0.070242 |
| evidence: SOURCE_FALLBACK | 11 | 7 | 0.636364 | 11 | -0.116364 |
| evidence: SUSPECT_ALIAS_FUZZY | 7 | 5 | 0.714286 | 7 | -0.032857 |
| evidence: UNMATCHED | 4 | 1 | 0.25 | 0 | None |
| odds band: <1.50 | 158 | 120 | 0.759494 | 158 | -0.023797 |
| odds band: 1.50-2.00 | 82 | 43 | 0.52439 | 82 | -0.12939 |
| odds band: 2.00-3.00 | 8 | 4 | 0.5 | 8 | 0.05 |
| odds band: unpriced | 4 | 1 | 0.25 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: context VETO in ['league', 'niche'] | 2 | 2 | 1.0 | 1 | 0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 4 | 4 | 1.0 | 4 | 0.12 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.595 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_h'] | 4 | 2 | 0.5 | 4 | -0.2675 |
| veto reason: context VETO in ['league'] | 10 | 6 | 0.6 | 9 | -0.007778 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 48 | 37 | 0.770833 | 48 | -0.004583 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.2 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 7 | 0.777778 | 9 | -0.004444 |
| veto reason: context VETO in ['team_a'] | 38 | 21 | 0.552632 | 36 | -0.079444 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.3025 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 15 | 14 | 0.933333 | 15 | 0.252 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.208 |
| veto reason: context VETO in ['team_h', 'team_a'] | 19 | 10 | 0.526316 | 19 | -0.171053 |
| veto reason: context VETO in ['team_h'] | 61 | 36 | 0.590164 | 61 | -0.120492 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 43 | 27 | 0.627907 | 43 | -0.005349 |
| contrast CAUTION: BZZOIRO_PRIMARY | 15 | 11 | 0.733333 | 15 | 0.141333 |
| contrast CAUTION: SOURCE_FALLBACK | 17 | 13 | 0.764706 | 17 | 0.244706 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 260 | 177 | 0.680769 | 230 | -0.007783 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 23 | 15 | 0.652174 | 21 | 0.001905 | 23 | 1.540652 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 238 | 157 | 0.659664 | 238 | -0.047017 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-10: Dinamo Tbilisi vs Meshakhte Tkibuli (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🔴 LOST (Expected prob: 62.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 34.6% (Actual: 0 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.0% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.8% (Actual: 0 goals)

### 2026-09-10: Comunicaciones vs CD Marquense (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 55.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.5% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.6% (Actual: 2 goals)

### 2026-09-10: Panathinaikos vs Kifisia (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🟢 WON (Expected prob: 61.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 34.2% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.2% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.4% (Actual: 4 goals)

### 2026-09-10: Los Angeles FC vs New York Red Bulls (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 60.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 34.2% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.4% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.3% (Actual: 2 goals)

### 2026-09-10: Vancouver Whitecaps vs Los Angeles Galaxy (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 59.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 33.3% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.4% (Actual: 3 goals)

### 2026-09-10: Radnik Surdulica vs Crvena Zvezda (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.27 -> 🔴 LOST (Expected prob: 58.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.9% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 34.0% (Actual: 0 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.8% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 81.1% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.6% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.0% (Actual: 0 goals)

### 2026-09-10: BFC Dynamo vs Tasmania Berlin (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.0% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 44.8% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.0% (Actual: 4 goals)


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

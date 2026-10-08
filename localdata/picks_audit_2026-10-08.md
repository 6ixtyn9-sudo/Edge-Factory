# Edge Factory — Recent picks audit (2026-09-09 to 2026-10-08)

## Overall

- archived pick rows: 538
- archived pick dates: 30
- immutable morning-baseline rows: 535
- verified official late-slate additions: 5
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 28
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 516
- eligible prior picks: 534
- pending/unmatched result picks: 9
- rescheduled result picks (settled ±3d): 6
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 3
- wins: 359
- hit rate: +69.6%
- priced picks: 454
- ROI: -1.2%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-08
- same-day rows excluded: 4

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 322 / 516 matches (62.4%)
- **Both Teams to Score (BTTS)**: occurred in 279 / 516 matches (54.1%)
- **Selected Team Over 1.5 Goals**: occurred in 341 / 516 matches (66.1%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 516
- **Total Hits**: 419
- **Overall Hit Rate**: 81.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=21, hits=19, hit_rate=90.5%
- `away_under_25`: recommended=25, hits=24, hit_rate=96.0%
- `away_under_35`: recommended=168, hits=161, hit_rate=95.8%
- `home_over_05`: recommended=4, hits=3, hit_rate=75.0%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=31, hits=30, hit_rate=96.8%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=208, hits=136, hit_rate=65.4%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%
- `match_over_45`: recommended=1, hits=1, hit_rate=100.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2021** | scored: 2021

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 507 | 507 | 315 | 62.1% | 44.9% | +17.3% | 0.264171 |
| `match_over_45` | 416 | 416 | 104 | 25.0% | 23.9% | +1.1% | 0.184657 |
| `away_under_35` | 359 | 359 | 347 | 96.7% | 95.5% | +1.2% | 0.032568 |
| `away_under_25` | 334 | 334 | 303 | 90.7% | 91.0% | -0.3% | 0.084234 |
| `home_under_35` | 128 | 128 | 124 | 96.9% | 93.5% | +3.3% | 0.033595 |
| `home_under_25` | 126 | 126 | 116 | 92.1% | 90.0% | +2.1% | 0.073905 |
| `away_over_05` | 44 | 44 | 39 | 88.6% | 86.0% | +2.7% | 0.099451 |
| `away_under_15` | 33 | 33 | 24 | 72.7% | 82.0% | -9.3% | 0.206955 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `home_over_05` | 19 | 19 | 17 | 89.5% | 84.0% | +5.5% | 0.108551 |
| `home_under_15` | 12 | 12 | 8 | 66.7% | 81.6% | -14.9% | 0.248468 |
| `match_over_15` | 7 | 7 | 6 | 85.7% | 82.9% | +2.8% | 0.120946 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1917 | 1348 | 70.3% | 65.3% | +5.0% | 0.140564 |
| model | 104 | 72 | 69.2% | 63.8% | +5.4% | 0.207174 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 90 | 19.2% | 18.9% | -0.3% |
| 0.2-0.3 | 280 | 24.1% | 24.3% | +0.2% |
| 0.3-0.4 | 79 | 33.2% | 48.1% | +14.9% |
| 0.4-0.5 | 454 | 44.2% | 60.8% | +16.5% |
| 0.5-0.6 | 53 | 51.6% | 66.0% | +14.4% |
| 0.8-0.9 | 304 | 86.5% | 87.5% | +1.0% |
| 0.9-1.0 | 761 | 94.1% | 94.6% | +0.5% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=515, MAE=1.575961 goals, bias=-0.268816 (realized − promised), promised avg 3.546485 vs realized 3.27767

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 515 | 31.3% | 33.8% | +2.5% | 0.209183 |
| BTTS-Yes | 515 | 41.3% | 54.0% | +12.7% | 0.264735 |
| Home Over 1.5 | 515 | 63.7% | 54.2% | -9.5% | 0.23784 |
| Over 2.5 | 515 | 69.8% | 62.3% | -7.4% | 0.240336 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 232 | 8.6% | 22.4% | +13.9% |
| 0.1-0.2 | 286 | 10.4% | 22.0% | +11.6% |
| 0.2-0.3 | 7 | 26.7% | 71.4% | +44.7% |
| 0.3-0.4 | 101 | 37.3% | 51.5% | +14.2% |
| 0.4-0.5 | 403 | 42.7% | 54.3% | +11.7% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 344 | 67.0% | 60.2% | -6.8% |
| 0.7-0.8 | 151 | 74.3% | 66.9% | -7.4% |
| 0.8-0.9 | 485 | 84.6% | 65.2% | -19.5% |
| 0.9-1.0 | 50 | 92.4% | 74.0% | -18.4% |

## By rule

- `2way-unanimous avg_p>=60`: settled=130, wins=81, hit_rate=0.623077, ROI=-0.142371
- `2way-unanimous avg_p>=70`: settled=65, wins=49, hit_rate=0.753846, ROI=-0.077143
- `ml-meta avg_p>=55`: settled=241, wins=161, hit_rate=0.66805, ROI=0.013722
- `ml-meta avg_p>=60`: settled=56, wins=47, hit_rate=0.839286, ROI=0.155179
- `ml-meta avg_p>=65`: settled=14, wins=12, hit_rate=0.857143, ROI=0.041538
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=7, wins=7, hit_rate=1.0, ROI=0.066667

## By bucket

- `CAUTION`: settled=37, wins=20, hit_rate=0.540541, ROI=-0.176081
- `CERTIFIED_CLEAN`: settled=60, wins=46, hit_rate=0.766667, ROI=0.18385
- `SKIPPED_VETO`: settled=255, wins=180, hit_rate=0.705882, ROI=-0.040788
- `WATCHLIST_NO_ODDS`: settled=46, wins=30, hit_rate=0.652174, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=5, hit_rate=1.0, ROI=0.653333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=109, wins=75, hit_rate=0.688073, ROI=-0.017706
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=62, wins=44, hit_rate=0.709677, ROI=None
- `betexplorer_odds`: settled=151, wins=106, hit_rate=0.701987, ROI=-0.012318
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=50, wins=36, hit_rate=0.72, ROI=0.0462
- `oddspapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.765
- `scoutingstats_odds`: settled=225, wins=149, hit_rate=0.662222, ROI=-0.055111
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=9, wins=8, hit_rate=0.888889, ROI=0.228889
- `zulubet`: settled=9, wins=7, hit_rate=0.777778, ROI=0.067778

## By odds match method

- `alias_fuzzy`: settled=12, wins=11, hit_rate=0.916667, ROI=0.333333
- `betexplorer`: settled=140, wins=96, hit_rate=0.685714, ROI=-0.022071
- `exact`: settled=255, wins=176, hit_rate=0.690196, ROI=-0.02131
- `fallback`: settled=50, wins=35, hit_rate=0.7, ROI=-0.0016
- `none`: settled=59, wins=41, hit_rate=0.694915, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 140 | 96 | 0.685714 | 140 | -0.022071 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 22 | 20 | 0.909091 | 22 | 0.218 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 225 | 149 | 0.662222 | 225 | -0.055111 |
| Source fallback (`SOURCE_FALLBACK`) | 50 | 35 | 0.7 | 50 | -0.0016 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 12 | 11 | 0.916667 | 9 | 0.333333 |
| No usable price (`UNMATCHED`) | 59 | 41 | 0.694915 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 255 | 180 | 0.705882 | 241 | -0.040788 |
| **trusted evidence only** | 95 | 70 | 0.736842 | 95 | -0.022 |
| **soft evidence only** | 160 | 110 | 0.6875 | 146 | -0.053014 |
| evidence: BETEXPLORER_RESCUE | 80 | 55 | 0.6875 | 80 | -0.07675 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 10 | 10 | 1.0 | 10 | 0.203 |
| evidence: SCOUTINGSTATS_SOLE | 116 | 74 | 0.637931 | 116 | -0.090259 |
| evidence: SOURCE_FALLBACK | 24 | 19 | 0.791667 | 24 | 0.070417 |
| evidence: SUSPECT_ALIAS_FUZZY | 7 | 6 | 0.857143 | 6 | 0.173333 |
| evidence: UNMATCHED | 13 | 11 | 0.846154 | 0 | None |
| odds band: <1.50 | 152 | 122 | 0.802632 | 152 | 0.004671 |
| odds band: 1.50-2.00 | 86 | 43 | 0.5 | 86 | -0.163256 |
| odds band: 2.00-3.00 | 3 | 3 | 1.0 | 3 | 1.166667 |
| odds band: unpriced | 14 | 12 | 0.857143 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.4 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 0 | 0.0 | 2 | -1.0 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 12 | 10 | 0.833333 | 12 | 0.110833 |
| veto reason: context VETO in ['league'] | 24 | 17 | 0.708333 | 19 | -0.024737 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 54 | 41 | 0.759259 | 54 | -0.028704 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.085 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 14 | 11 | 0.785714 | 14 | -0.017857 |
| veto reason: context VETO in ['team_a'] | 40 | 25 | 0.625 | 36 | -0.083333 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.137143 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 11 | 6 | 0.545455 | 11 | -0.159091 |
| veto reason: context VETO in ['team_h'] | 44 | 30 | 0.681818 | 40 | -0.00625 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 23 | 14 | 0.608696 | 23 | -0.073043 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 2 | 1 | 0.5 | 2 | -0.1175 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.327273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 276 | 196 | 0.710145 | 217 | 0.013622 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 12 | 11 | 0.916667 | 9 | 0.333333 | 12 | 1.506667 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 225 | 149 | 0.662222 | 225 | -0.055111 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 3 | 3 | 1.0 | 3 | 0.28 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-07: Ponte Preta vs Juventude (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🟢 WON (Expected prob: 75.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.8% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.0% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.0% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.5% (Actual: 2 goals)

### 2026-10-07: FC Tokyo vs Shonan Bellmare (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 58.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.9% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.2% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.6% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.3% (Actual: 4 goals)

### 2026-10-07: Urawa vs Omiya Ardija (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.741 -> 🟢 WON (Expected prob: 55.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 63.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.6% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.2% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.1% (Actual: 5 goals)

### 2026-10-07: CR Belouizdad vs Khenchela (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.34 -> 🟢 WON (Expected prob: 67.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 86.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.3% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 95.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.8% (Actual: 1 goals)

### 2026-10-07: CS Constantine vs US Biskra (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🟢 WON (Expected prob: 63.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.3% (Actual: 4 goals)

### 2026-10-07: Mexico vs Chile (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🔴 LOST (Expected prob: 61.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 92.3% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.4% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 2 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])
- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova FC 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca W 4-1 Santos Laguna W [home])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ None (rescheduled → 2026-10-03; actual Tampa Bay Rowdies 1-2 Miami FC [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Brooklyn vs Rhode Island FC -> AWAY @ None (rescheduled → 2026-10-03; actual Brooklyn 1-3 Rhode Island [away])

## Pending / Unmatched Result Examples

- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-26 `SKIPPED_VETO` `ml-meta avg_p>=55` — Crawley Town vs Barnet -> AWAY @ 1.66 (pending_or_unmatched_result); keys=['crawleyto']/['barnet']
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Milevsko vs Spartak Sobeslav -> AWAY @ 1.57 (pending_or_unmatched_result); keys=['milevsko']/['spartakso']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Polanka nad Odrou vs Frydek-Mistek -> AWAY @ 1.48 (pending_or_unmatched_result); keys=['polankana']/['frydekmis']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Brommapojkarna W vs Malmö FF W -> AWAY @ 1.4 (pending_or_unmatched_result); keys=['brommapoj']/['malmoff', 'malmoffww']
- 2026-09-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — Plateau United vs Inter Lagos -> HOME @ 1.33 (pending_or_unmatched_result); keys=['plateauun']/['interlago']
- 2026-10-03 `CAUTION` `2way-unanimous avg_p>=60` — Sri Lanka vs Djibouti -> HOME @ 2.6 (pending_or_unmatched_result); keys=['srilanka']/['djibouti']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Rheindorf Altach II vs Hohenems -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['hohenems']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kufstein vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['kufstein']/['imst']

## Ambiguous result examples

- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

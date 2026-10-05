# Edge Factory — Recent picks audit (2026-09-06 to 2026-10-05)

## Overall

- archived pick rows: 587
- archived pick dates: 30
- immutable morning-baseline rows: 589
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 559
- eligible prior picks: 582
- pending/unmatched result picks: 12
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 3
- wins: 384
- hit rate: +68.7%
- priced picks: 495
- ROI: -1.7%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-05
- same-day rows excluded: 5

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 341 / 547 matches (62.3%)
- **Both Teams to Score (BTTS)**: occurred in 297 / 547 matches (54.3%)
- **Selected Team Over 1.5 Goals**: occurred in 361 / 547 matches (66.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 559
- **Total Hits**: 456
- **Overall Hit Rate**: 81.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=21, hits=19, hit_rate=90.5%
- `away_under_25`: recommended=25, hits=24, hit_rate=96.0%
- `away_under_35`: recommended=182, hits=176, hit_rate=96.7%
- `home_over_05`: recommended=9, hits=8, hit_rate=88.9%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=34, hits=33, hit_rate=97.1%
- `match_over_25`: recommended=236, hits=156, hit_rate=66.1%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%
- `match_over_45`: recommended=1, hits=1, hit_rate=100.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2182** | scored: 2182

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 550 | 550 | 344 | 62.5% | 44.9% | +17.6% | 0.264009 |
| `match_over_45` | 445 | 445 | 110 | 24.7% | 23.8% | +1.0% | 0.183085 |
| `away_under_35` | 388 | 388 | 377 | 97.2% | 95.7% | +1.5% | 0.027558 |
| `away_under_25` | 359 | 359 | 327 | 91.1% | 91.3% | -0.2% | 0.08144 |
| `home_under_35` | 147 | 147 | 143 | 97.3% | 94.0% | +3.3% | 0.029471 |
| `home_under_25` | 136 | 136 | 126 | 92.6% | 90.2% | +2.5% | 0.068815 |
| `away_over_05` | 43 | 43 | 38 | 88.4% | 86.1% | +2.3% | 0.100904 |
| `away_under_15` | 34 | 34 | 25 | 73.5% | 81.9% | -8.4% | 0.202036 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `home_over_05` | 31 | 31 | 28 | 90.3% | 82.4% | +7.9% | 0.095319 |
| `home_under_15` | 13 | 13 | 9 | 69.2% | 81.6% | -12.3% | 0.232124 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2046 | 1447 | 70.7% | 65.6% | +5.1% | 0.137966 |
| model | 136 | 97 | 71.3% | 63.4% | +7.9% | 0.183243 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 97 | 19.2% | 18.6% | -0.6% |
| 0.2-0.3 | 304 | 24.1% | 24.0% | -0.1% |
| 0.3-0.4 | 79 | 33.4% | 50.6% | +17.2% |
| 0.4-0.5 | 493 | 44.3% | 61.3% | +16.9% |
| 0.5-0.6 | 55 | 51.7% | 65.5% | +13.7% |
| 0.8-0.9 | 305 | 86.3% | 87.5% | +1.3% |
| 0.9-1.0 | 849 | 94.3% | 95.2% | +0.9% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=546, MAE=1.570513 goals, bias=-0.263626 (realized − promised), promised avg 3.529194 vs realized 3.265568

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 546 | 31.3% | 35.0% | +3.7% | 0.215368 |
| BTTS-Yes | 546 | 41.4% | 54.2% | +12.8% | 0.263974 |
| Home Over 1.5 | 546 | 63.5% | 53.8% | -9.7% | 0.239267 |
| Over 2.5 | 546 | 69.5% | 62.3% | -7.3% | 0.240136 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 237 | 8.6% | 23.2% | +14.6% |
| 0.1-0.2 | 312 | 10.4% | 23.1% | +12.7% |
| 0.2-0.3 | 5 | 25.7% | 60.0% | +34.3% |
| 0.3-0.4 | 105 | 37.3% | 51.4% | +14.2% |
| 0.4-0.5 | 432 | 42.8% | 54.9% | +12.1% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 375 | 67.0% | 60.3% | -6.7% |
| 0.7-0.8 | 152 | 74.2% | 67.1% | -7.1% |
| 0.8-0.9 | 518 | 84.5% | 65.3% | -19.3% |
| 0.9-1.0 | 47 | 92.4% | 72.3% | -20.0% |

## By rule

- `2way-unanimous avg_p>=60`: settled=129, wins=80, hit_rate=0.620155, ROI=-0.14875
- `2way-unanimous avg_p>=70`: settled=67, wins=50, hit_rate=0.746269, ROI=-0.081373
- `ml-meta avg_p>=55`: settled=277, wins=181, hit_rate=0.65343, ROI=-0.004034
- `ml-meta avg_p>=60`: settled=50, wins=42, hit_rate=0.84, ROI=0.1632
- `ml-meta avg_p>=65`: settled=14, wins=12, hit_rate=0.857143, ROI=0.041538
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=7, wins=7, hit_rate=1.0, ROI=0.066667
- `ou25-unanimous-2way-sa avg_p>=70`: settled=12, wins=10, hit_rate=0.833333, ROI=0.22

## By bucket

- `CAUTION`: settled=43, wins=24, hit_rate=0.55814, ROI=-0.160116
- `CERTIFIED_CLEAN`: settled=58, wins=45, hit_rate=0.775862, ROI=0.193621
- `SKIPPED_VETO`: settled=270, wins=184, hit_rate=0.681481, ROI=-0.066381
- `WATCHLIST_NO_ODDS`: settled=48, wins=31, hit_rate=0.645833, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=12, wins=9, hit_rate=0.75, ROI=0.254444
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=124, wins=88, hit_rate=0.709677, ROI=0.017661
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=64, wins=44, hit_rate=0.6875, ROI=None
- `betexplorer_odds`: settled=163, wins=111, hit_rate=0.680982, ROI=-0.040798
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=62, wins=46, hit_rate=0.741935, ROI=0.09
- `oddspapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.765
- `scoutingstats_odds`: settled=252, wins=168, hit_rate=0.666667, ROI=-0.045437
- `theoddsapi`: settled=2, wins=2, hit_rate=1.0, ROI=0.63
- `zulubet`: settled=7, wins=5, hit_rate=0.714286, ROI=-0.032857

## By odds match method

- `alias_fuzzy`: settled=19, wins=15, hit_rate=0.789474, ROI=0.219333
- `betexplorer`: settled=155, wins=104, hit_rate=0.670968, ROI=-0.041677
- `exact`: settled=271, wins=185, hit_rate=0.682657, ROI=-0.027472
- `fallback`: settled=54, wins=39, hit_rate=0.722222, ROI=0.038148
- `none`: settled=60, wins=41, hit_rate=0.683333, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 155 | 104 | 0.670968 | 155 | -0.041677 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 11 | 10 | 0.909091 | 11 | 0.166818 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 252 | 168 | 0.666667 | 252 | -0.045437 |
| Source fallback (`SOURCE_FALLBACK`) | 54 | 39 | 0.722222 | 54 | 0.038148 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 19 | 15 | 0.789474 | 15 | 0.219333 |
| No usable price (`UNMATCHED`) | 60 | 41 | 0.683333 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 270 | 184 | 0.681481 | 257 | -0.066381 |
| **trusted evidence only** | 97 | 67 | 0.690722 | 97 | -0.07268 |
| **soft evidence only** | 173 | 117 | 0.676301 | 160 | -0.062562 |
| evidence: BETEXPLORER_RESCUE | 89 | 59 | 0.662921 | 89 | -0.104157 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 3 | 3 | 1.0 | 3 | 0.066667 |
| evidence: SCOUTINGSTATS_SOLE | 128 | 80 | 0.625 | 128 | -0.106563 |
| evidence: SOURCE_FALLBACK | 26 | 21 | 0.807692 | 26 | 0.101154 |
| evidence: SUSPECT_ALIAS_FUZZY | 7 | 6 | 0.857143 | 6 | 0.166667 |
| evidence: UNMATCHED | 12 | 10 | 0.833333 | 0 | None |
| odds band: <1.50 | 158 | 124 | 0.78481 | 158 | -0.013987 |
| odds band: 1.50-2.00 | 94 | 45 | 0.478723 | 94 | -0.196809 |
| odds band: 2.00-3.00 | 5 | 4 | 0.8 | 5 | 0.73 |
| odds band: unpriced | 13 | 11 | 0.846154 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.29 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.4 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.49 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 12 | 10 | 0.833333 | 12 | 0.110833 |
| veto reason: context VETO in ['league'] | 23 | 16 | 0.695652 | 18 | -0.046111 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 58 | 43 | 0.741379 | 58 | -0.04 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.39 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 14 | 11 | 0.785714 | 14 | -0.017857 |
| veto reason: context VETO in ['team_a'] | 47 | 28 | 0.595745 | 43 | -0.123488 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.11 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 4 | 2 | 0.5 | 4 | -0.335 |
| veto reason: context VETO in ['team_h', 'team_a'] | 10 | 5 | 0.5 | 10 | -0.169 |
| veto reason: context VETO in ['team_h'] | 46 | 29 | 0.630435 | 43 | -0.064419 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 27 | 16 | 0.592593 | 27 | -0.111111 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 2 | 1 | 0.5 | 2 | -0.1175 |
| contrast CAUTION: SOURCE_FALLBACK | 13 | 7 | 0.538462 | 13 | -0.203846 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 286 | 199 | 0.695804 | 226 | -0.003252 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 19 | 15 | 0.789474 | 15 | 0.219333 | 19 | 1.587895 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 252 | 168 | 0.666667 | 252 | -0.045437 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 2 | 2 | 1.0 | 2 | 0.17 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-04: Spokane Velocity vs Portland Hearts Of Pine (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.59 -> 🔴 LOST (Expected prob: 63.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.7% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.0% (Actual: 6 goals)

### 2026-10-04: Portugal vs Norway (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.765 -> 🟢 WON (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.3% (Actual: 1 away goals)

### 2026-10-04: Netherlands vs Serbia (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.17 -> 🟢 WON (Expected prob: 79.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 34.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.9% (Actual: 2 home goals)

### 2026-10-04: Barcelona (w) vs Real Madrid (w) (Actual Score: **7-0**)
- **1X2 Pick**: Selected `HOME` @ 1.13 -> 🟢 WON (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 7 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.2% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.9% (Actual: 7 goals)

### 2026-10-04: Argentina vs Burkina Faso (Actual Score: **7-0**)
- **1X2 Pick**: Selected `HOME` @ 1.02 -> 🟢 WON (Expected prob: 77.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.4% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.3% (Actual: 7 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 31.7% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 86.7% (Actual: 0 away goals)

### 2026-10-04: West Ham (w) vs Chelsea (w) (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.16 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.7% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.9% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.1% (Actual: 3 goals)

### 2026-10-04: Hammarby W vs Brommapojkarna W (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.09 -> 🟢 WON (Expected prob: 64.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.0% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.3% (Actual: 2 goals)

### 2026-10-04: Niger Tornadoes FC vs Kun Khalifat FC (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 62.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.0% (Actual: 1 goals)

### 2026-10-04: Huracan vs Aldosivi (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🟢 WON (Expected prob: 57.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.0% (Actual: 1 goals)

### 2026-10-04: Wales vs Denmark (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.9 -> 🟢 WON (Expected prob: 56.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.6% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.3% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.8% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.6% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.4% (Actual: 1 goals)

### 2026-10-04: Castellon vs AD Ceuta (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 75.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 81.0% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.8% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.6% (Actual: 2 goals)

### 2026-10-04: Unicov vs Polanka Nad Odrou (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 67.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.4% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.7% (Actual: 4 goals)

### 2026-10-04: Chicago Red Stars (w) vs Denver Summit Fc (w) (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.2% (Actual: 3 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.5% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.1% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.1% (Actual: 3 goals)

### 2026-10-04: Audace Cerignola vs Team Altamura (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🔴 LOST (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.1% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.1% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.9% (Actual: 0 goals)

### 2026-10-04: Greece vs Germany (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.83 -> 🔴 LOST (Expected prob: 56.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.8% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.6% (Actual: 0 goals)
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected 80.0% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.3% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.0% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 0 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])
- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova FC 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca W 4-1 Santos Laguna W [home])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ None (rescheduled → 2026-10-03; actual Tampa Bay Rowdies 1-2 Miami FC [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Brooklyn vs Rhode Island FC -> AWAY @ None (rescheduled → 2026-10-03; actual Brooklyn 1-3 Rhode Island [away])

## Pending / Unmatched Result Examples

- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
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

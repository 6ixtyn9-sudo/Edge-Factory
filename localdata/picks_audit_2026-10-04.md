# Edge Factory — Recent picks audit (2026-09-05 to 2026-10-04)

## Overall

- archived pick rows: 645
- archived pick dates: 30
- immutable morning-baseline rows: 645
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 605
- eligible prior picks: 628
- pending/unmatched result picks: 13
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 1
- ambiguous result picks: 3
- wins: 405
- hit rate: +66.9%
- priced picks: 541
- ROI: -4.3%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-04
- same-day rows excluded: 17

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 357 / 579 matches (61.7%)
- **Both Teams to Score (BTTS)**: occurred in 316 / 579 matches (54.6%)
- **Selected Team Over 1.5 Goals**: occurred in 375 / 579 matches (64.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 605
- **Total Hits**: 482
- **Overall Hit Rate**: 79.7%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=20, hits=18, hit_rate=90.0%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=184, hits=178, hit_rate=96.7%
- `home_over_05`: recommended=23, hits=17, hit_rate=73.9%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=34, hits=33, hit_rate=97.1%
- `match_over_15`: recommended=8, hits=4, hit_rate=50.0%
- `match_over_25`: recommended=261, hits=170, hit_rate=65.1%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2387** | scored: 2387

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 599 | 599 | 369 | 61.6% | 45.1% | +16.5% | 0.262632 |
| `match_over_45` | 478 | 478 | 118 | 24.7% | 23.7% | +0.9% | 0.18249 |
| `away_under_35` | 424 | 424 | 412 | 97.2% | 95.8% | +1.3% | 0.02761 |
| `away_under_25` | 389 | 389 | 355 | 91.3% | 91.5% | -0.3% | 0.080061 |
| `home_under_35` | 165 | 165 | 160 | 97.0% | 94.1% | +2.9% | 0.031797 |
| `home_under_25` | 140 | 140 | 129 | 92.1% | 90.3% | +1.8% | 0.072517 |
| `home_over_05` | 64 | 64 | 55 | 85.9% | 82.9% | +3.0% | 0.121034 |
| `away_over_05` | 41 | 41 | 37 | 90.2% | 86.4% | +3.9% | 0.089254 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_under_15` | 30 | 30 | 22 | 73.3% | 82.0% | -8.7% | 0.202989 |
| `home_under_15` | 13 | 13 | 9 | 69.2% | 81.6% | -12.3% | 0.232124 |
| `match_over_15` | 8 | 8 | 4 | 50.0% | 82.8% | -32.8% | 0.357732 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2200 | 1559 | 70.9% | 66.1% | +4.7% | 0.137654 |
| model | 187 | 128 | 68.4% | 62.9% | +5.6% | 0.176753 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 107 | 19.2% | 16.8% | -2.4% |
| 0.2-0.3 | 323 | 24.1% | 24.5% | +0.4% |
| 0.3-0.4 | 85 | 33.4% | 49.4% | +16.0% |
| 0.4-0.5 | 530 | 44.4% | 60.6% | +16.1% |
| 0.5-0.6 | 65 | 51.9% | 64.6% | +12.7% |
| 0.8-0.9 | 333 | 86.0% | 86.2% | +0.2% |
| 0.9-1.0 | 944 | 94.4% | 95.1% | +0.8% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=578, MAE=1.567924 goals, bias=-0.273737 (realized − promised), promised avg 3.521142 vs realized 3.247405

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 578 | 30.8% | 34.3% | +3.5% | 0.214968 |
| BTTS-Yes | 578 | 41.5% | 54.5% | +13.0% | 0.263971 |
| Home Over 1.5 | 578 | 64.0% | 53.8% | -10.2% | 0.251698 |
| Over 2.5 | 578 | 69.5% | 61.6% | -7.9% | 0.242726 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 246 | 8.6% | 23.6% | +14.9% |
| 0.1-0.2 | 335 | 10.4% | 23.6% | +13.2% |
| 0.2-0.3 | 5 | 25.7% | 60.0% | +34.3% |
| 0.3-0.4 | 109 | 37.3% | 52.3% | +15.0% |
| 0.4-0.5 | 460 | 42.8% | 55.0% | +12.2% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 402 | 66.9% | 60.2% | -6.7% |
| 0.7-0.8 | 157 | 74.3% | 65.0% | -9.3% |
| 0.8-0.9 | 548 | 84.5% | 64.2% | -20.3% |
| 0.9-1.0 | 49 | 92.4% | 69.4% | -23.0% |

## By rule

- `2way-unanimous avg_p>=60`: settled=123, wins=77, hit_rate=0.626016, ROI=-0.117204
- `2way-unanimous avg_p>=70`: settled=74, wins=55, hit_rate=0.743243, ROI=-0.096491
- `ml-meta avg_p>=55`: settled=308, wins=194, hit_rate=0.62987, ROI=-0.040952
- `ml-meta avg_p>=60`: settled=50, wins=42, hit_rate=0.84, ROI=0.166
- `ml-meta avg_p>=65`: settled=14, wins=12, hit_rate=0.857143, ROI=0.041538
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=7, wins=7, hit_rate=1.0, ROI=0.066667
- `ou25-unanimous-2way-sa avg_p>=70`: settled=26, wins=16, hit_rate=0.615385, ROI=-0.1336

## By bucket

- `CAUTION`: settled=42, wins=23, hit_rate=0.547619, ROI=-0.182143
- `CERTIFIED_CLEAN`: settled=60, wins=45, hit_rate=0.75, ROI=0.163
- `SKIPPED_VETO`: settled=295, wins=195, hit_rate=0.661017, ROI=-0.089324
- `WATCHLIST_NO_ODDS`: settled=47, wins=31, hit_rate=0.659574, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=15, wins=10, hit_rate=0.666667, ROI=0.074167
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=142, wins=98, hit_rate=0.690141, ROI=-0.00662
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=64, wins=44, hit_rate=0.6875, ROI=None
- `betexplorer_odds`: settled=168, wins=113, hit_rate=0.672619, ROI=-0.044226
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=69, wins=48, hit_rate=0.695652, ROI=0.01913
- `scoutingstats_odds`: settled=287, wins=186, hit_rate=0.648084, ROI=-0.071115
- `theoddsapi`: settled=2, wins=2, hit_rate=1.0, ROI=0.63
- `zulubet`: settled=7, wins=5, hit_rate=0.714286, ROI=-0.035714

## By odds match method

- `alias_fuzzy`: settled=25, wins=18, hit_rate=0.72, ROI=0.052381
- `betexplorer`: settled=165, wins=110, hit_rate=0.666667, ROI=-0.04703
- `exact`: settled=300, wins=198, hit_rate=0.66, ROI=-0.0555
- `fallback`: settled=55, wins=38, hit_rate=0.690909, ROI=-0.000545
- `none`: settled=60, wins=41, hit_rate=0.683333, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 165 | 110 | 0.666667 | 165 | -0.04703 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 5 | 5 | 1.0 | 5 | 0.318 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 287 | 186 | 0.648084 | 287 | -0.071115 |
| Source fallback (`SOURCE_FALLBACK`) | 55 | 38 | 0.690909 | 55 | -0.000545 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 25 | 18 | 0.72 | 21 | 0.052381 |
| No usable price (`UNMATCHED`) | 60 | 41 | 0.683333 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 295 | 195 | 0.661017 | 281 | -0.089324 |
| **trusted evidence only** | 101 | 69 | 0.683168 | 101 | -0.073069 |
| **soft evidence only** | 194 | 126 | 0.649485 | 180 | -0.098444 |
| evidence: BETEXPLORER_RESCUE | 95 | 63 | 0.663158 | 95 | -0.099158 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 1 | 1 | 1.0 | 1 | 0.02 |
| evidence: SCOUTINGSTATS_SOLE | 145 | 88 | 0.606897 | 145 | -0.134276 |
| evidence: SOURCE_FALLBACK | 26 | 20 | 0.769231 | 26 | 0.059231 |
| evidence: SUSPECT_ALIAS_FUZZY | 10 | 8 | 0.8 | 9 | 0.023333 |
| evidence: UNMATCHED | 13 | 10 | 0.769231 | 0 | None |
| odds band: <1.50 | 172 | 131 | 0.761628 | 172 | -0.04064 |
| odds band: 1.50-2.00 | 103 | 49 | 0.475728 | 103 | -0.201553 |
| odds band: 2.00-3.00 | 6 | 4 | 0.666667 | 6 | 0.441667 |
| odds band: unpriced | 14 | 11 | 0.785714 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 5 | 4 | 0.8 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.29 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.4 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.49 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 14 | 10 | 0.714286 | 14 | -0.047857 |
| veto reason: context VETO in ['league'] | 24 | 17 | 0.708333 | 19 | -0.018421 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 64 | 46 | 0.71875 | 64 | -0.070156 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.39 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 14 | 11 | 0.785714 | 14 | -0.017857 |
| veto reason: context VETO in ['team_a'] | 49 | 26 | 0.530612 | 44 | -0.204091 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.11 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.218 |
| veto reason: context VETO in ['team_h', 'team_a'] | 12 | 6 | 0.5 | 12 | -0.1575 |
| veto reason: context VETO in ['team_h'] | 56 | 35 | 0.625 | 54 | -0.069074 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 27 | 16 | 0.592593 | 27 | -0.111111 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 14 | 7 | 0.5 | 14 | -0.260714 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 292 | 200 | 0.684932 | 232 | -0.018448 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 25 | 18 | 0.72 | 21 | 0.052381 | 25 | 1.5696 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 287 | 186 | 0.648084 | 287 | -0.071115 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 1 | 1 | 1.0 | 1 | 0.25 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-03: Piteå W vs Norrköping W (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 2.07 -> 🔴 LOST (Expected prob: 64.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.0% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.9% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.3% (Actual: 2 goals)

### 2026-10-03: Stromsgodset vs Asane (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.15 -> 🟢 WON (Expected prob: 74.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 81.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.7% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.7% (Actual: 1 goals)

### 2026-10-03: Cuiaba vs Ponte Preta (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 79.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.2% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 38.1% (Actual: 2 goals)

### 2026-10-03: Iceland vs Bulgaria (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 62.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 3 goals)

### 2026-10-03: Croatia vs England (Actual Score: **0-7**)
- **1X2 Pick**: Selected `AWAY` @ 1.78 -> 🟢 WON (Expected prob: 58.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 7 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.7% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.3% (Actual: 7 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.6% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.4% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.2% (Actual: 7 goals)

### 2026-10-03: Spain vs Czech Republic (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.05 -> 🟢 WON (Expected prob: 80.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 34.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.3% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 4 goals)

### 2026-10-03: Spain vs Czechia (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.07 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.1% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.1% (Actual: 4 goals)

### 2026-10-03: India vs Brazil (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.02 -> 🟢 WON (Expected prob: 73.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 24.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.2% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.1% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.4% (Actual: 4 goals)

### 2026-10-03: Hamilton Academical vs Peterhead (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.3% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.8% (Actual: 3 goals)

### 2026-10-03: Switzerland vs Slovenia (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🟢 WON (Expected prob: 71.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.8% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 83.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.3% (Actual: 3 goals)

### 2026-10-03: Caernarfon Town vs Barry Town (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🔴 LOST (Expected prob: 69.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.9% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.8% (Actual: 1 goals)

### 2026-10-03: Dorking Wanderers vs Chatham Town (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 67.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.0% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.1% (Actual: 1 goals)

### 2026-10-03: FYR Macedonia vs Scotland (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.76 -> 🟢 WON (Expected prob: 66.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.6% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.5% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.7% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.4% (Actual: 2 goals)

### 2026-10-03: The New Saints vs Cambrian & Clydach (Actual Score: **9-0**)
- **1X2 Pick**: Selected `HOME` @ 1.1 -> 🟢 WON (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.6% (Actual: 9 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 9 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.5% (Actual: 9 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.1% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.4% (Actual: 9 goals)

### 2026-10-03: Cittadella vs AlbinoLeffe (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🔴 LOST (Expected prob: 65.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.4% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 81.2% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.8% (Actual: 3 goals)

### 2026-10-03: Gateshead vs Worthing (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.3 -> 🟢 WON (Expected prob: 65.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.3% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.6% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.2% (Actual: 3 goals)

### 2026-10-03: Morton vs Raith Rovers (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.5% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.4% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.5% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.2% (Actual: 3 goals)

### 2026-10-03: Ull/Kisa vs Kjelsås (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.25 -> 🟢 WON (Expected prob: 64.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.2% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 81.0% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.2% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.3% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.7% (Actual: 3 goals)

### 2026-10-03: Albacete vs Eibar (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 64.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.4% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.9% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.2% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.9% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.8% (Actual: 4 goals)

### 2026-10-03: Briton Ferry vs Colwyn Bay (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.57 -> 🔴 LOST (Expected prob: 63.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.6% (Actual: 1 goals)
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected 80.5% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.8% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.8% (Actual: 1 goals)

### 2026-10-03: Grimsby vs Shrewsbury (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 61.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 3 goals)

### 2026-10-03: Haugesund vs Stabaek (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.85 -> 🟢 WON (Expected prob: 60.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.7% (Actual: 2 goals)

### 2026-10-03: Partick vs Arbroath (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.7% (Actual: 3 goals)

### 2026-10-03: Russia vs Namibia (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 80.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.2% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.1% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.4% (Actual: 0 away goals)
    - [🔴 MISS] **Home Team Under 3.5 Goals**: expected 96.4% (Actual: 6 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 away goals)

### 2026-10-03: Grorud vs Lorenskog (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.9% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.4% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.8% (Actual: 4 goals)

### 2026-10-03: Boise vs Greenville Triumph SC (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.6% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.9% (Actual: 1 goals)

### 2026-10-03: Atletico Goianiense vs America Mineiro (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.0% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.3% (Actual: 2 goals)

### 2026-10-03: York United vs Cavalry FC (Actual Score: **3-1**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 68.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 37.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 91.7% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.3% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 81.3% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.0% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 90.0% (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.6% (Actual: 4 goals)

### 2026-10-03: Middelfart vs FA 2000 (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 67.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.4% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.7% (Actual: 1 goals)

### 2026-10-03: Skeid vs Honefoss (Actual Score: **4-3**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.6% (Actual: 3 away goals)
    - [🔴 MISS] **Home Team Under 3.5 Goals**: expected 98.2% (Actual: 4 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 89.9% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.3% (Actual: 7 goals)

### 2026-10-03: Livingston vs Ayr Utd (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 64.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.0% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.9% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.3% (Actual: 3 goals)

### 2026-10-03: Pors Grenland vs Vidar (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 63.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.8% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.3% (Actual: 5 goals)

### 2026-10-03: Annan Athletic vs Stirling Albion (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 62.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.5% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.0% (Actual: 1 goals)

### 2026-10-03: Forge FC vs HFX Wanderers (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.1% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.1% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.9% (Actual: 6 goals)

### 2026-10-03: Spartans vs Kelty Hearts (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.4% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.9% (Actual: 2 goals)

### 2026-10-03: Deportes Tolima vs Chico (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 61.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.0% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.9% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 0 goals)

### 2026-10-03: Kano Pillars FC vs Sporting Lagos (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 58.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.4% (Actual: 2 goals)

### 2026-10-03: Magallanes vs Curico Unido (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.5% (Actual: 1 goals)

### 2026-10-03: Deportivo Cali vs Alianza Valledupar (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 69.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.2% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.5% (Actual: 4 goals)

### 2026-10-03: Belarus vs San Marino (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.07 -> 🟢 WON (Expected prob: 79.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.1% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.2% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.9% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.1% (Actual: 4 goals)

### 2026-10-03: Ross County vs Alloa Athletic (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.4% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.8% (Actual: 5 goals)

### 2026-10-03: Amiens vs Villefranche (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🟢 WON (Expected prob: 68.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.5% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.3% (Actual: 3 goals)

### 2026-10-03: Deportivo Maldonado vs Central Espanol (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 68.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.6% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.3% (Actual: 3 goals)

### 2026-10-03: Grosseto vs Sambenedettese (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🔴 LOST (Expected prob: 67.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.2% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.8% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.3% (Actual: 3 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.7% (Actual: 4 goals)

### 2026-10-03: Boreham Wood vs Altrincham (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🟢 WON (Expected prob: 65.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.5% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.6% (Actual: 4 goals)

### 2026-10-03: Ospitaletto vs Renate (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 2.1 -> 🔴 LOST (Expected prob: 65.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.1% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 82.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.2% (Actual: 2 goals)

### 2026-10-03: Ebbsfleet United vs Sholing FC (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🔴 LOST (Expected prob: 64.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 81.1% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.1% (Actual: 3 goals)

### 2026-10-03: Salisbury FC vs Dulwich Hamlet (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 63.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.9% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.7% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.6% (Actual: 5 goals)

### 2026-10-03: Harrogate Town vs AFC Hornchurch (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 61.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 3 goals)

### 2026-10-03: Boca Juniors vs Union Santa Fe (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 60.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.8% (Actual: 3 goals)

### 2026-10-03: Salford City vs Fleetwood Town (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.5% (Actual: 1 goals)

### 2026-10-03: Colombia vs Paraguay (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🔴 LOST (Expected prob: 61.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.3% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.4% (Actual: 1 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 3-3 Go Ahead Eagles [draw])
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])
- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova FC 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca W 4-1 Santos Laguna W [home])

## Pending / Unmatched Result Examples

- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-26 `SKIPPED_VETO` `ml-meta avg_p>=55` — Crawley Town vs Barnet -> AWAY @ 1.66 (pending_or_unmatched_result); keys=['crawleyto']/['barnet']
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Milevsko vs Spartak Sobeslav -> AWAY @ 1.57 (pending_or_unmatched_result); keys=['milevsko']/['spartakso']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Polanka nad Odrou vs Frydek-Mistek -> AWAY @ 1.48 (pending_or_unmatched_result); keys=['polankana']/['frydekmis']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Brommapojkarna W vs Malmö FF W -> AWAY @ 1.4 (pending_or_unmatched_result); keys=['brommapoj']/['malmff', 'malmoffw']
- 2026-09-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — Plateau United vs Inter Lagos -> HOME @ 1.33 (pending_or_unmatched_result); keys=['plateauun']/['interlago']
- 2026-10-03 `CAUTION` `2way-unanimous avg_p>=60` — Sri Lanka vs Djibouti -> HOME @ 2.6 (pending_or_unmatched_result); keys=['srilanka']/['djibouti']
- 2026-10-03 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ 1.36 (pending_or_unmatched_result); keys=['tampabayr']/['miami']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Rheindorf Altach II vs Hohenems -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['hohenems']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kufstein vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['kufstein']/['imst']

## Ambiguous result examples

- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

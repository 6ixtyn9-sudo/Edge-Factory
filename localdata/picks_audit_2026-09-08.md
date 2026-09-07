# Edge Factory — Recent picks audit (2026-08-10 to 2026-09-08)

## Overall

- archived pick rows: 558
- archived pick dates: 30
- immutable morning-baseline rows: 473
- verified official late-slate additions: 2
- regular-ledger-only legacy rows: 83
- unsafe regular ledgers ignored: 20
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 522
- eligible prior picks: 546
- pending/unmatched result picks: 7
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 8
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 345
- hit rate: +66.1%
- priced picks: 491
- ROI: -4.0%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-08
- same-day rows excluded: 12

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 303 / 476 matches (63.7%)
- **Both Teams to Score (BTTS)**: occurred in 256 / 476 matches (53.8%)
- **Selected Team Over 1.5 Goals**: occurred in 322 / 476 matches (67.6%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 522
- **Total Hits**: 383
- **Overall Hit Rate**: 73.4%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=6, hits=4, hit_rate=66.7%
- `away_under_35`: recommended=24, hits=24, hit_rate=100.0%
- `home_over_05`: recommended=116, hits=99, hit_rate=85.3%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=16, hits=16, hit_rate=100.0%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=312, hits=203, hit_rate=65.1%
- `match_over_35`: recommended=2, hits=0, hit_rate=0.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2385** | scored: 2385

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 506 | 506 | 322 | 63.6% | 47.3% | +16.4% | 0.25755 |
| `away_under_35` | 388 | 388 | 380 | 97.9% | 97.9% | +0.1% | 0.019608 |
| `match_over_45` | 373 | 373 | 107 | 28.7% | 24.0% | +4.7% | 0.205556 |
| `away_under_25` | 362 | 362 | 337 | 93.1% | 94.0% | -0.9% | 0.064716 |
| `home_over_05` | 342 | 342 | 303 | 88.6% | 85.2% | +3.4% | 0.101321 |
| `home_under_35` | 142 | 142 | 140 | 98.6% | 95.6% | +3.0% | 0.014952 |
| `away_under_15` | 105 | 105 | 83 | 79.0% | 81.4% | -2.4% | 0.166216 |
| `home_under_25` | 103 | 103 | 95 | 92.2% | 91.6% | +0.6% | 0.071543 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `home_under_15` | 9 | 9 | 9 | 100.0% | 81.2% | +18.8% | 0.035416 |
| `away_over_05` | 8 | 8 | 6 | 75.0% | 82.9% | -7.9% | 0.211136 |
| `match_over_35` | 4 | 4 | 0 | 0.0% | 37.2% | -37.2% | 0.138303 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2155 | 1646 | 76.4% | 72.4% | +4.0% | 0.125512 |
| model | 230 | 170 | 73.9% | 64.4% | +9.5% | 0.169197 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 95 | 19.0% | 22.1% | +3.1% |
| 0.2-0.3 | 248 | 25.0% | 30.6% | +5.7% |
| 0.3-0.4 | 67 | 35.1% | 41.8% | +6.7% |
| 0.4-0.5 | 335 | 45.6% | 63.0% | +17.4% |
| 0.5-0.6 | 133 | 53.3% | 67.7% | +14.3% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 521 | 84.2% | 85.8% | +1.6% |
| 0.9-1.0 | 981 | 95.7% | 95.8% | +0.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=475, MAE=1.551537 goals, bias=-0.178021 (realized − promised), promised avg 3.519074 vs realized 3.341053

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 475 | 28.1% | 36.8% | +8.7% | 0.219005 |
| BTTS-Yes | 475 | 41.7% | 53.9% | +12.2% | 0.263247 |
| Home Over 1.5 | 475 | 66.7% | 57.3% | -9.4% | 0.251481 |
| Over 2.5 | 475 | 69.7% | 63.6% | -6.1% | 0.232499 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 267 | 8.9% | 25.1% | +16.2% |
| 0.1-0.2 | 209 | 10.4% | 29.2% | +18.8% |
| 0.2-0.3 | 7 | 21.9% | 28.6% | +6.7% |
| 0.3-0.4 | 96 | 37.4% | 52.1% | +14.6% |
| 0.4-0.5 | 371 | 43.2% | 54.4% | +11.2% |
| 0.6-0.7 | 312 | 66.7% | 60.9% | -5.8% |
| 0.7-0.8 | 149 | 74.7% | 66.4% | -8.2% |
| 0.8-0.9 | 442 | 84.5% | 67.0% | -17.5% |
| 0.9-1.0 | 47 | 91.8% | 80.9% | -11.0% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=12, wins=6, hit_rate=0.5, ROI=-0.301667
- `2way-unanimous avg_p>=70`: settled=108, wins=83, hit_rate=0.768519, ROI=0.093053
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=1, wins=1, hit_rate=1.0, ROI=0.2
- `ml-meta avg_p>=55`: settled=297, wins=180, hit_rate=0.606061, ROI=-0.083852
- `ml-meta avg_p>=60`: settled=28, wins=22, hit_rate=0.785714, ROI=0.098929
- `ml-meta avg_p>=65`: settled=6, wins=5, hit_rate=0.833333, ROI=0.158
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=79, wins=52, hit_rate=0.658228, ROI=0.048228
- `CERTIFIED_CLEAN`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.150606
- `SKIPPED_VETO`: settled=249, wins=165, hit_rate=0.662651, ROI=-0.058735
- `WATCHLIST_NO_ODDS`: settled=26, wins=18, hit_rate=0.692308, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=14, wins=10, hit_rate=0.714286, ROI=0.097692
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=110, wins=71, hit_rate=0.645455, ROI=-0.061091
- `WATCHLIST_UNKNOWN_CTX`: settled=11, wins=10, hit_rate=0.909091, ROI=0.109091

## By odds source

- `UNKNOWN`: settled=31, wins=19, hit_rate=0.612903, ROI=None
- `betexplorer_odds`: settled=156, wins=104, hit_rate=0.666667, ROI=-0.063397
- `bzzoiro_odds`: settled=51, wins=32, hit_rate=0.627451, ROI=-0.040196
- `forebet_best`: settled=54, wins=40, hit_rate=0.740741, ROI=0.093333
- `scoutingstats_odds`: settled=226, wins=146, hit_rate=0.646018, ROI=-0.061549
- `zulubet`: settled=4, wins=4, hit_rate=1.0, ROI=0.2525

## By odds match method

- `alias_fuzzy`: settled=24, wins=18, hit_rate=0.75, ROI=0.084348
- `betexplorer`: settled=156, wins=104, hit_rate=0.666667, ROI=-0.063397
- `exact`: settled=277, wins=178, hit_rate=0.642599, ROI=-0.057617
- `fallback`: settled=35, wins=26, hit_rate=0.742857, ROI=0.117429
- `none`: settled=30, wins=19, hit_rate=0.633333, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 156 | 104 | 0.666667 | 156 | -0.063397 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 51 | 32 | 0.627451 | 51 | -0.040196 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 226 | 146 | 0.646018 | 226 | -0.061549 |
| Source fallback (`SOURCE_FALLBACK`) | 35 | 26 | 0.742857 | 35 | 0.117429 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 24 | 18 | 0.75 | 23 | 0.084348 |
| No usable price (`UNMATCHED`) | 30 | 19 | 0.633333 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 249 | 165 | 0.662651 | 245 | -0.058735 |
| **trusted evidence only** | 109 | 75 | 0.688073 | 109 | -0.053853 |
| **soft evidence only** | 140 | 90 | 0.642857 | 136 | -0.062647 |
| evidence: BETEXPLORER_RESCUE | 82 | 57 | 0.695122 | 82 | -0.07378 |
| evidence: BZZOIRO_PRIMARY | 27 | 18 | 0.666667 | 27 | 0.006667 |
| evidence: SCOUTINGSTATS_SOLE | 116 | 75 | 0.646552 | 116 | -0.061983 |
| evidence: SOURCE_FALLBACK | 10 | 6 | 0.6 | 10 | -0.2 |
| evidence: SUSPECT_ALIAS_FUZZY | 10 | 8 | 0.8 | 10 | 0.067 |
| evidence: UNMATCHED | 4 | 1 | 0.25 | 0 | None |
| odds band: <1.50 | 157 | 117 | 0.745223 | 157 | -0.039745 |
| odds band: 1.50-2.00 | 81 | 43 | 0.530864 | 81 | -0.117901 |
| odds band: 2.00-3.00 | 7 | 4 | 0.571429 | 7 | 0.2 |
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
| veto reason: context VETO in ['odds_band'] | 51 | 40 | 0.784314 | 51 | 0.022941 |
| veto reason: context VETO in ['team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 7 | 0.777778 | 9 | -0.032222 |
| veto reason: context VETO in ['team_a'] | 38 | 21 | 0.552632 | 36 | -0.061667 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.3025 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 13 | 12 | 0.923077 | 13 | 0.243846 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.208 |
| veto reason: context VETO in ['team_h', 'team_a'] | 19 | 9 | 0.473684 | 19 | -0.261579 |
| veto reason: context VETO in ['team_h'] | 60 | 35 | 0.583333 | 60 | -0.129167 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 44 | 28 | 0.636364 | 44 | 0.012045 |
| contrast CAUTION: BZZOIRO_PRIMARY | 18 | 11 | 0.611111 | 18 | -0.048889 |
| contrast CAUTION: SOURCE_FALLBACK | 17 | 13 | 0.764706 | 17 | 0.244706 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 272 | 181 | 0.665441 | 242 | -0.032355 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 24 | 18 | 0.75 | 23 | 0.084348 | 24 | 1.518125 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 226 | 146 | 0.646018 | 226 | -0.061549 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-07: Rigas Futbola skola vs FK Liepaja (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🔴 LOST (Expected prob: 55.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.7% (Actual: 0 goals)

### 2026-09-07: Pafos vs Olympiakos Nicosia (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.39 -> 🔴 LOST (Expected prob: 71.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.2% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.2% (Actual: 0 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 82.5% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.9% (Actual: 0 goals)

### 2026-09-07: Riga FC vs BFC Daugavpils (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.29 -> 🔴 LOST (Expected prob: 66.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.5% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.1% (Actual: 2 goals)

### 2026-09-07: Hapoel Tel Aviv vs Hapoel Ramat Gan (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 64.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.6% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.9% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.0% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.2% (Actual: 4 goals)

### 2026-09-07: Kalmar FF vs Djurgårdens (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.8 -> 🟢 WON (Expected prob: 61.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.2% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.3% (Actual: 1 goals)


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
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 1-3 Go Ahead Eagles [away])
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

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)

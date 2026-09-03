# Edge Factory — Recent picks audit (2026-08-05 to 2026-09-03)

## Overall

- archived pick rows: 488
- archived pick dates: 30
- immutable morning-baseline rows: 363
- verified official late-slate additions: 10
- regular-ledger-only legacy rows: 115
- unsafe regular ledgers ignored: 16
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 463
- eligible prior picks: 483
- pending/unmatched result picks: 5
- rescheduled result picks (settled ±3d): 4
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 318
- hit rate: +68.7%
- priced picks: 434
- ROI: -2.0%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-03
- same-day rows excluded: 5

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 287 / 447 matches (64.2%)
- **Both Teams to Score (BTTS)**: occurred in 242 / 447 matches (54.1%)
- **Selected Team Over 1.5 Goals**: occurred in 313 / 447 matches (70.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 463
- **Total Hits**: 351
- **Overall Hit Rate**: 75.8%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=17, hits=15, hit_rate=88.2%
- `away_under_35`: recommended=8, hits=8, hit_rate=100.0%
- `btts_yes`: recommended=10, hits=6, hit_rate=60.0%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=141, hits=128, hit_rate=90.8%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=12, hits=12, hit_rate=100.0%
- `match_over_15`: recommended=10, hits=10, hit_rate=100.0%
- `match_over_25`: recommended=254, hits=168, hit_rate=66.1%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2452** | scored: 2452

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 413 | 413 | 265 | 64.2% | 46.6% | +17.6% | 0.261134 |
| `away_under_35` | 351 | 351 | 343 | 97.7% | 98.0% | -0.3% | 0.02166 |
| `match_over_45` | 345 | 345 | 96 | 27.8% | 24.6% | +3.3% | 0.20315 |
| `away_under_25` | 334 | 334 | 313 | 93.7% | 94.1% | -0.4% | 0.059562 |
| `home_over_05` | 332 | 332 | 300 | 90.4% | 86.5% | +3.9% | 0.088495 |
| `away_under_15` | 121 | 121 | 96 | 79.3% | 81.4% | -2.1% | 0.164317 |
| `home_under_35` | 103 | 103 | 102 | 99.0% | 95.6% | +3.5% | 0.010921 |
| `home_under_25` | 90 | 90 | 82 | 91.1% | 91.7% | -0.6% | 0.082009 |
| `match_over_35` | 80 | 80 | 27 | 33.8% | 43.6% | -9.9% | 0.232112 |
| `exact_4` | 46 | 46 | 9 | 19.6% | 18.5% | +1.0% | 0.158297 |
| `goal_range_4_5` | 46 | 46 | 13 | 28.3% | 31.1% | -2.9% | 0.20598 |
| `goal_range_4_6` | 46 | 46 | 17 | 37.0% | 38.3% | -1.4% | 0.237647 |
| `exact_5` | 45 | 45 | 4 | 8.9% | 12.7% | -3.8% | 0.082713 |
| `btts_no` | 28 | 28 | 11 | 39.3% | 51.8% | -12.5% | 0.256747 |
| `away_over_05` | 19 | 19 | 17 | 89.5% | 86.0% | +3.5% | 0.097009 |
| `exact_3` | 13 | 13 | 4 | 30.8% | 22.2% | +8.6% | 0.22087 |
| `home_under_15` | 11 | 11 | 10 | 90.9% | 81.3% | +9.6% | 0.091092 |
| `btts_yes` | 10 | 10 | 6 | 60.0% | 49.4% | +10.6% | 0.267576 |
| `match_over_15` | 10 | 10 | 10 | 100.0% | 88.1% | +11.9% | 0.014684 |
| `goal_range_6_plus` | 7 | 7 | 1 | 14.3% | 16.3% | -2.0% | 0.110594 |
| `exact_2` | 1 | 1 | 0 | 0.0% | 22.8% | -22.8% | 0.051983 ⚠️low-n |
| `goal_range_7_plus` | 1 | 1 | 1 | 100.0% | 10.5% | +89.5% | 0.800604 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2308 | 1616 | 70.0% | 67.3% | +2.7% | 0.130057 |
| model | 144 | 111 | 77.1% | 60.6% | +16.5% | 0.210855 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 170 | 17.0% | 18.8% | +1.8% |
| 0.2-0.3 | 262 | 25.2% | 29.4% | +4.2% |
| 0.3-0.4 | 207 | 35.5% | 40.1% | +4.6% |
| 0.4-0.5 | 281 | 45.5% | 58.4% | +12.9% |
| 0.5-0.6 | 156 | 53.0% | 60.9% | +7.9% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 458 | 84.4% | 87.1% | +2.7% |
| 0.9-1.0 | 913 | 95.6% | 95.7% | +0.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=446, MAE=1.530964 goals, bias=-0.226031 (realized − promised), promised avg 3.575807 vs realized 3.349776

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 446 | 27.3% | 36.3% | +9.0% | 0.20827 |
| BTTS-Yes | 446 | 41.4% | 54.3% | +12.9% | 0.266439 |
| Home Over 1.5 | 446 | 67.9% | 59.2% | -8.7% | 0.239618 |
| Over 2.5 | 446 | 70.5% | 64.1% | -6.4% | 0.231477 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 288 | 8.9% | 23.6% | +14.7% |
| 0.1-0.2 | 159 | 10.5% | 30.2% | +19.7% |
| 0.2-0.3 | 7 | 21.9% | 28.6% | +6.7% |
| 0.3-0.4 | 100 | 37.5% | 58.0% | +20.5% |
| 0.4-0.5 | 338 | 43.0% | 53.3% | +10.2% |
| 0.6-0.7 | 259 | 66.8% | 60.6% | -6.2% |
| 0.7-0.8 | 171 | 74.9% | 66.7% | -8.2% |
| 0.8-0.9 | 405 | 84.8% | 68.6% | -16.1% |
| 0.9-1.0 | 57 | 91.8% | 86.0% | -5.8% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=127, wins=98, hit_rate=0.771654, ROI=0.077788
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=18, wins=13, hit_rate=0.722222, ROI=0.016667
- `ml-meta avg_p>=55`: settled=214, wins=133, hit_rate=0.621495, ROI=-0.070784
- `ml-meta avg_p>=60`: settled=25, wins=20, hit_rate=0.8, ROI=0.132
- `ml-meta avg_p>=65`: settled=6, wins=5, hit_rate=0.833333, ROI=0.158
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06
- `ou25-unanimous-2way-sa avg_p>=70`: settled=16, wins=10, hit_rate=0.625, ROI=-0.13875

## By bucket

- `CAUTION`: settled=75, wins=49, hit_rate=0.653333, ROI=0.0196
- `CERTIFIED_CLEAN`: settled=30, wins=16, hit_rate=0.533333, ROI=-0.217
- `SKIPPED_VETO`: settled=233, wins=164, hit_rate=0.703863, ROI=-0.009957
- `WATCHLIST_NO_ODDS`: settled=26, wins=19, hit_rate=0.730769, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=8, wins=6, hit_rate=0.75, ROI=0.077143
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=77, wins=52, hit_rate=0.675325, ROI=-0.030519
- `WATCHLIST_UNKNOWN_CTX`: settled=14, wins=12, hit_rate=0.857143, ROI=0.047143

## By odds source

- `UNKNOWN`: settled=29, wins=19, hit_rate=0.655172, ROI=None
- `betexplorer_odds`: settled=153, wins=106, hit_rate=0.69281, ROI=-0.032484
- `bzzoiro_odds`: settled=72, wins=46, hit_rate=0.638889, ROI=-0.046528
- `forebet_best`: settled=35, wins=26, hit_rate=0.742857, ROI=0.048571
- `scoutingstats_odds`: settled=166, wins=113, hit_rate=0.680723, ROI=-0.026988
- `zulubet`: settled=8, wins=8, hit_rate=1.0, ROI=0.32625

## By odds match method

- `alias_fuzzy`: settled=15, wins=12, hit_rate=0.8, ROI=0.126429
- `betexplorer`: settled=153, wins=106, hit_rate=0.69281, ROI=-0.032484
- `exact`: settled=238, wins=159, hit_rate=0.668067, ROI=-0.032899
- `fallback`: settled=29, wins=22, hit_rate=0.758621, ROI=0.087586
- `none`: settled=28, wins=19, hit_rate=0.678571, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 153 | 106 | 0.69281 | 153 | -0.032484 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 72 | 46 | 0.638889 | 72 | -0.046528 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 166 | 113 | 0.680723 | 166 | -0.026988 |
| Source fallback (`SOURCE_FALLBACK`) | 29 | 22 | 0.758621 | 29 | 0.087586 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 15 | 12 | 0.8 | 14 | 0.126429 |
| No usable price (`UNMATCHED`) | 28 | 19 | 0.678571 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 233 | 164 | 0.703863 | 231 | -0.009957 |
| **trusted evidence only** | 124 | 89 | 0.717742 | 124 | -0.012258 |
| **soft evidence only** | 109 | 75 | 0.688073 | 107 | -0.00729 |
| evidence: BETEXPLORER_RESCUE | 82 | 60 | 0.731707 | 82 | -0.027439 |
| evidence: BZZOIRO_PRIMARY | 42 | 29 | 0.690476 | 42 | 0.017381 |
| evidence: SCOUTINGSTATS_SOLE | 89 | 61 | 0.685393 | 89 | -0.023933 |
| evidence: SOURCE_FALLBACK | 11 | 8 | 0.727273 | 11 | 0.010909 |
| evidence: SUSPECT_ALIAS_FUZZY | 7 | 6 | 0.857143 | 7 | 0.175714 |
| evidence: UNMATCHED | 2 | 0 | 0.0 | 0 | None |
| odds band: <1.50 | 150 | 118 | 0.786667 | 150 | 0.014 |
| odds band: 1.50-2.00 | 76 | 43 | 0.565789 | 76 | -0.074342 |
| odds band: 2.00-3.00 | 5 | 3 | 0.6 | 5 | 0.25 |
| odds band: unpriced | 2 | 0 | 0.0 | 0 | None |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.05 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.66 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 11 | 7 | 0.636364 | 10 | 0.054 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 48 | 40 | 0.833333 | 48 | 0.105625 |
| veto reason: context VETO in ['team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 9 | 0.818182 | 11 | 0.055455 |
| veto reason: context VETO in ['team_a'] | 35 | 24 | 0.685714 | 34 | 0.081471 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 13 | 11 | 0.846154 | 13 | 0.163077 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.055 |
| veto reason: context VETO in ['team_h', 'team_a'] | 18 | 8 | 0.444444 | 18 | -0.35 |
| veto reason: context VETO in ['team_h'] | 54 | 33 | 0.611111 | 54 | -0.109444 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 1 | 1 | 1.0 | 1 | 0.19 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 43 | 27 | 0.627907 | 43 | -0.008605 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0025 |
| contrast CAUTION: SOURCE_FALLBACK | 12 | 9 | 0.75 | 12 | 0.149167 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 282 | 193 | 0.684397 | 254 | -0.022756 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 15 | 12 | 0.8 | 14 | 0.126429 | 15 | 1.361 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 166 | 113 | 0.680723 | 166 | -0.026988 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-02: Flora Tallinn vs Tammeka Tartu (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 68.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.7% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.0% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.3% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 26.4% (Actual: 5 goals)

### 2026-09-02: VfL Osnabruck vs Bayern Munich (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.05 -> 🟢 WON (Expected prob: 79.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 20.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 80.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 80.0% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 86.5% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.5% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.0% (Actual: 5 goals)

### 2026-09-02: Celtic vs Aberdeen (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 74.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 93.5% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.7% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 33.7% (Actual: 3 goals)

### 2026-09-02: Slavia Sofia vs Levski Sofia (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.33 -> 🟢 WON (Expected prob: 68.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 35.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 84.7% (Actual: 3 goals)

### 2026-09-02: Grasshoppers vs St Gallen (Actual Score: **2-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.7 -> 🔴 LOST (Expected prob: 59.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 87.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.9% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.5% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.2% (Actual: 2 goals)

### 2026-09-02: Falkirk FC vs Rangers (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.6 -> 🟢 WON (Expected prob: 58.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 87.5% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 3 goals)

### 2026-09-02: Nestos Chrisoupolis vs AEK Athens FC (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.12 -> 🟢 WON (Expected prob: 72.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 28.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 87.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.8% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 85.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.9% (Actual: 2 goals)

### 2026-09-02: Flora Tallinn vs Tammeka Tartu (Actual Score: **3-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.38 -> 🟢 WON (Expected prob: 72.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 89.5% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.2% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.8% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 86.8% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.0% (Actual: 5 goals)

### 2026-09-02: VfL Osnabruck vs Bayern Munich (Actual Score: **1-4**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.11 -> 🟢 WON (Expected prob: 71.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 86.5% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.5% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.0% (Actual: 5 goals)

### 2026-09-02: Flamengo vs Mirassol (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 71.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 90.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.4% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.2% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.7% (Actual: 2 goals)

### 2026-09-02: Celtic vs Aberdeen (Actual Score: **3-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4 -> 🟢 WON (Expected prob: 71.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 88.6% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.1% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 86.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 3 goals)

### 2026-09-02: FC Luzern vs FC Vaduz (Actual Score: **2-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.33 -> 🟢 WON (Expected prob: 71.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 86.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 85.3% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.2% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.4% (Actual: 3 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 9 |
- 2026-08-08 `POSTPONED` `SKIPPED_VETO` — Belshina vs Dinamo Minsk (verified_disposition); excluded from win/loss/ROI
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

## Pending / Unmatched Result Examples

- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)

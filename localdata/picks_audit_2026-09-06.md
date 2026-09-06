# Edge Factory — Recent picks audit (2026-08-08 to 2026-09-06)

## Overall

- archived pick rows: 598
- archived pick dates: 30
- immutable morning-baseline rows: 490
- verified official late-slate additions: 6
- regular-ledger-only legacy rows: 102
- unsafe regular ledgers ignored: 19
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 530
- eligible prior picks: 551
- pending/unmatched result picks: 6
- rescheduled result picks (settled ±3d): 4
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 349
- hit rate: +65.8%
- priced picks: 497
- ROI: -5.2%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-06
- same-day rows excluded: 47

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 316 / 496 matches (63.7%)
- **Both Teams to Score (BTTS)**: occurred in 271 / 496 matches (54.6%)
- **Selected Team Over 1.5 Goals**: occurred in 334 / 496 matches (67.3%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 530
- **Total Hits**: 392
- **Overall Hit Rate**: 74.0%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=16, hits=14, hit_rate=87.5%
- `away_under_35`: recommended=15, hits=15, hit_rate=100.0%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=148, hits=129, hit_rate=87.2%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=12, hits=12, hit_rate=100.0%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=285, hits=184, hit_rate=64.6%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2640** | scored: 2640

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 488 | 488 | 308 | 63.1% | 46.8% | +16.3% | 0.260379 |
| `away_under_35` | 397 | 397 | 389 | 98.0% | 97.9% | +0.1% | 0.019534 |
| `match_over_45` | 392 | 392 | 112 | 28.6% | 24.3% | +4.2% | 0.205393 |
| `away_under_25` | 376 | 376 | 352 | 93.6% | 93.9% | -0.3% | 0.060288 |
| `home_over_05` | 364 | 364 | 325 | 89.3% | 85.9% | +3.3% | 0.096189 |
| `home_under_35` | 132 | 132 | 130 | 98.5% | 95.5% | +2.9% | 0.015895 |
| `away_under_15` | 121 | 121 | 97 | 80.2% | 81.4% | -1.2% | 0.159269 |
| `home_under_25` | 102 | 102 | 93 | 91.2% | 91.7% | -0.5% | 0.080996 |
| `match_over_35` | 61 | 61 | 20 | 32.8% | 43.4% | -10.6% | 0.221103 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `exact_4` | 27 | 27 | 6 | 22.2% | 18.7% | +3.6% | 0.173849 |
| `exact_5` | 27 | 27 | 3 | 11.1% | 12.9% | -1.8% | 0.098253 |
| `goal_range_4_5` | 27 | 27 | 9 | 33.3% | 31.5% | +1.8% | 0.220625 |
| `goal_range_4_6` | 27 | 27 | 10 | 37.0% | 38.9% | -1.9% | 0.230614 |
| `away_over_05` | 18 | 18 | 16 | 88.9% | 86.0% | +2.9% | 0.101394 |
| `btts_no` | 16 | 16 | 4 | 25.0% | 51.4% | -26.4% | 0.258121 |
| `home_under_15` | 11 | 11 | 10 | 90.9% | 81.3% | +9.6% | 0.091092 |
| `exact_3` | 5 | 5 | 3 | 60.0% | 22.1% | +37.9% | 0.383968 |
| `goal_range_6_plus` | 5 | 5 | 1 | 20.0% | 16.4% | +3.6% | 0.144682 |
| `goal_range_7_plus` | 1 | 1 | 1 | 100.0% | 10.5% | +89.5% | 0.800604 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2440 | 1775 | 72.7% | 69.4% | +3.3% | 0.130243 |
| model | 200 | 148 | 74.0% | 63.7% | +10.3% | 0.177403 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 149 | 17.7% | 20.1% | +2.5% |
| 0.2-0.3 | 273 | 25.1% | 30.8% | +5.7% |
| 0.3-0.4 | 168 | 35.5% | 42.3% | +6.8% |
| 0.4-0.5 | 326 | 45.5% | 58.9% | +13.4% |
| 0.5-0.6 | 155 | 53.1% | 62.6% | +9.5% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 539 | 84.3% | 86.3% | +1.9% |
| 0.9-1.0 | 1025 | 95.6% | 95.7% | +0.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=495, MAE=1.544364 goals, bias=-0.227273 (realized − promised), promised avg 3.552525 vs realized 3.325253

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 495 | 27.3% | 35.6% | +8.2% | 0.215374 |
| BTTS-Yes | 495 | 41.6% | 54.7% | +13.2% | 0.266306 |
| Home Over 1.5 | 495 | 67.7% | 57.8% | -10.0% | 0.254585 |
| Over 2.5 | 495 | 70.1% | 63.6% | -6.5% | 0.232498 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 299 | 8.9% | 24.4% | +15.5% |
| 0.1-0.2 | 197 | 10.4% | 29.4% | +19.0% |
| 0.2-0.3 | 7 | 21.9% | 28.6% | +6.7% |
| 0.3-0.4 | 102 | 37.6% | 56.9% | +19.3% |
| 0.4-0.5 | 385 | 43.1% | 54.3% | +11.2% |
| 0.6-0.7 | 305 | 66.8% | 60.0% | -6.8% |
| 0.7-0.8 | 173 | 74.8% | 67.6% | -7.2% |
| 0.8-0.9 | 454 | 84.6% | 66.3% | -18.3% |
| 0.9-1.0 | 58 | 91.8% | 81.0% | -10.7% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=129, wins=97, hit_rate=0.751938, ROI=0.060702
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=11, wins=8, hit_rate=0.727273, ROI=0.075455
- `ml-meta avg_p>=55`: settled=265, wins=160, hit_rate=0.603774, ROI=-0.090119
- `ml-meta avg_p>=60`: settled=28, wins=22, hit_rate=0.785714, ROI=0.098929
- `ml-meta avg_p>=65`: settled=6, wins=5, hit_rate=0.833333, ROI=0.158
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06
- `ou25-unanimous-2way-sa avg_p>=70`: settled=34, wins=18, hit_rate=0.529412, ROI=-0.281818

## By bucket

- `CAUTION`: settled=83, wins=54, hit_rate=0.650602, ROI=0.039518
- `CERTIFIED_CLEAN`: settled=37, wins=19, hit_rate=0.513514, ROI=-0.245676
- `SKIPPED_VETO`: settled=259, wins=174, hit_rate=0.671815, ROI=-0.045137
- `WATCHLIST_NO_ODDS`: settled=28, wins=21, hit_rate=0.75, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=11, wins=7, hit_rate=0.636364, ROI=-0.086
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=100, wins=64, hit_rate=0.64, ROI=-0.0782
- `WATCHLIST_UNKNOWN_CTX`: settled=12, wins=10, hit_rate=0.833333, ROI=0.016667

## By odds source

- `UNKNOWN`: settled=33, wins=22, hit_rate=0.666667, ROI=None
- `betexplorer_odds`: settled=166, wins=112, hit_rate=0.674699, ROI=-0.050663
- `bzzoiro_odds`: settled=65, wins=40, hit_rate=0.615385, ROI=-0.060462
- `forebet_best`: settled=48, wins=33, hit_rate=0.6875, ROI=0.008125
- `scoutingstats_odds`: settled=213, wins=137, hit_rate=0.643192, ROI=-0.07277
- `zulubet`: settled=5, wins=5, hit_rate=1.0, ROI=0.33

## By odds match method

- `alias_fuzzy`: settled=20, wins=14, hit_rate=0.7, ROI=-0.025789
- `betexplorer`: settled=166, wins=112, hit_rate=0.674699, ROI=-0.050663
- `exact`: settled=278, wins=177, hit_rate=0.636691, ROI=-0.069892
- `fallback`: settled=34, wins=24, hit_rate=0.705882, ROI=0.074412
- `none`: settled=32, wins=22, hit_rate=0.6875, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 166 | 112 | 0.674699 | 166 | -0.050663 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 65 | 40 | 0.615385 | 65 | -0.060462 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 213 | 137 | 0.643192 | 213 | -0.07277 |
| Source fallback (`SOURCE_FALLBACK`) | 34 | 24 | 0.705882 | 34 | 0.074412 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 20 | 14 | 0.7 | 19 | -0.025789 |
| No usable price (`UNMATCHED`) | 32 | 22 | 0.6875 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 259 | 174 | 0.671815 | 255 | -0.045137 |
| **trusted evidence only** | 123 | 87 | 0.707317 | 123 | -0.021789 |
| **soft evidence only** | 136 | 87 | 0.639706 | 132 | -0.066894 |
| evidence: BETEXPLORER_RESCUE | 86 | 62 | 0.72093 | 86 | -0.039302 |
| evidence: BZZOIRO_PRIMARY | 37 | 25 | 0.675676 | 37 | 0.018919 |
| evidence: SCOUTINGSTATS_SOLE | 113 | 73 | 0.646018 | 113 | -0.067965 |
| evidence: SOURCE_FALLBACK | 10 | 6 | 0.6 | 10 | -0.152 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 9 | 0.041111 |
| evidence: UNMATCHED | 4 | 1 | 0.25 | 0 | None |
| odds band: <1.50 | 164 | 122 | 0.743902 | 164 | -0.037256 |
| odds band: 1.50-2.00 | 85 | 48 | 0.564706 | 85 | -0.066471 |
| odds band: 2.00-3.00 | 6 | 3 | 0.5 | 6 | 0.041667 |
| odds band: unpriced | 4 | 1 | 0.25 | 0 | None |
| veto reason: context VETO in ['league', 'niche'] | 2 | 2 | 1.0 | 1 | 0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.05 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.66 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_h'] | 3 | 1 | 0.333333 | 3 | -0.516667 |
| veto reason: context VETO in ['league'] | 12 | 8 | 0.666667 | 11 | 0.092727 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 55 | 42 | 0.763636 | 55 | 0.004545 |
| veto reason: context VETO in ['team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 10 | 8 | 0.8 | 10 | 0.02 |
| veto reason: context VETO in ['team_a'] | 41 | 25 | 0.609756 | 39 | -0.001026 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.3025 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 14 | 12 | 0.857143 | 14 | 0.182143 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.153333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 20 | 9 | 0.45 | 20 | -0.2985 |
| veto reason: context VETO in ['team_h'] | 60 | 36 | 0.6 | 60 | -0.112833 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 47 | 30 | 0.638298 | 47 | 0.015106 |
| contrast CAUTION: BZZOIRO_PRIMARY | 19 | 12 | 0.631579 | 19 | -0.014737 |
| contrast CAUTION: SOURCE_FALLBACK | 17 | 12 | 0.705882 | 17 | 0.167647 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 297 | 198 | 0.666667 | 265 | -0.037019 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 20 | 14 | 0.7 | 19 | -0.025789 | 20 | 1.42025 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 213 | 137 | 0.643192 | 213 | -0.07277 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-05: Grotta vs Volsungur (Actual Score: **0-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.36 -> 🔴 LOST (Expected prob: 70.5%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 54.3% (Actual: 2 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 82.2% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.9% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.5% (Actual: 2 goals)

### 2026-09-05: AEK Athens vs Aris Thessalonikis (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.39 -> 🟢 WON (Expected prob: 70.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.7% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.3% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.1% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.8% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.2% (Actual: 5 goals)

### 2026-09-05: Apollon Limassol vs Anorthosis FC (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.46 -> 🟢 WON (Expected prob: 65.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.1% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 4 goals)

### 2026-09-05: Concordia Chiajna vs CS Afumati (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 59.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.1% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.1% (Actual: 3 goals)

### 2026-09-05: Kozarmisleny SE vs Mezokovesdi SE (Actual Score: **2-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.98 -> 🔴 LOST (Expected prob: 57.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.5% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.7% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 2 goals)

### 2026-09-05: FC Schalke 04 vs Bayern München (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.16 -> 🔴 LOST (Expected prob: 80.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 84.8% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 30.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.9% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 93.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.3% (Actual: 0 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.4% (Actual: 0 goals)

### 2026-09-05: Dinamo Zagreb vs HNK Gorica (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🟢 WON (Expected prob: 80.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 93.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.8% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.7% (Actual: 1 goals)

### 2026-09-05: Chelsea W vs Aston Villa W (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🔴 LOST (Expected prob: 77.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 77.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 51.0% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 33.2% (Actual: 2 goals)

### 2026-09-05: Stabaek vs Moss (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🔴 LOST (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.4% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 92.0% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 30.1% (Actual: 5 goals)

### 2026-09-05: Manchester City vs Coventry (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.17 -> 🟢 WON (Expected prob: 72.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 87.7% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 52.8% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.6% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.8% (Actual: 1 goals)

### 2026-09-05: Manchester City vs Coventry City (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🟢 WON (Expected prob: 71.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 51.2% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.5% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.5% (Actual: 1 goals)

### 2026-09-05: Haugesund vs Sogndal (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 68.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.0% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.4% (Actual: 2 goals)

### 2026-09-05: BSC Young Boys vs FC Luzern (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 66.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.3% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.1% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.0% (Actual: 6 goals)

### 2026-09-05: East Fife vs Ross County (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.44 -> 🔴 LOST (Expected prob: 65.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 91.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.6% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.0% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.9% (Actual: 4 goals)

### 2026-09-05: Hansa Rostock vs SV Wehen (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🔴 LOST (Expected prob: 65.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.4% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.0% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.6% (Actual: 2 goals)

### 2026-09-05: Lens vs Lorient (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🔴 LOST (Expected prob: 62.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 83.6% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.0% (Actual: 1 goals)

### 2026-09-05: St Mirren vs Celtic (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.48 -> 🟢 WON (Expected prob: 62.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.2% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.6% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.2% (Actual: 3 goals)

### 2026-09-05: Dumbarton FC vs Elgin City (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.83 -> 🔴 LOST (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.8% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.6% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.9% (Actual: 3 goals)

### 2026-09-05: Rosenborg BK vs HamKam (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 61.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.2% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.9% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.3% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 4 goals)

### 2026-09-05: Werder Bremen vs RB Leipzig (Actual Score: **3-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.72 -> 🔴 LOST (Expected prob: 61.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.6% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 89.8% (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.8% (Actual: 4 goals)

### 2026-09-05: Busan I'Park vs Ansan Greeners (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🔴 LOST (Expected prob: 60.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 82.1% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.9% (Actual: 1 goals)

### 2026-09-05: Gateshead vs Solihull Moors (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 2.4 -> 🔴 LOST (Expected prob: 58.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.2% (Actual: 2 goals)

### 2026-09-05: Reims vs Guingamp (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🔴 LOST (Expected prob: 57.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.1% (Actual: 4 goals)

### 2026-09-05: Clyde FC vs Edinburgh City (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.73 -> 🟢 WON (Expected prob: 56.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 5 goals)

### 2026-09-05: Motor Lublin vs Legia Warszawa (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.8 -> 🟢 WON (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.6% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.2% (Actual: 5 goals)

### 2026-09-05: Brentford vs Sunderland (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🔴 LOST (Expected prob: 56.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.0% (Actual: 2 goals)

### 2026-09-05: Truro City vs Chesham United (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🟢 WON (Expected prob: 56.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.6% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.4% (Actual: 4 goals)

### 2026-09-05: Fleetwood Town vs Shrewsbury (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.95 -> 🟢 WON (Expected prob: 55.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.4% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.1% (Actual: 2 goals)

### 2026-09-05: West Ham vs Derby (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.39 -> 🟢 WON (Expected prob: 59.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 82.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.3% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.8% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.2% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.9% (Actual: 3 goals)

### 2026-09-05: Partick vs Ayr Utd (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 59.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 81.5% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.8% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.8% (Actual: 1 goals)

### 2026-09-05: Maritimo vs Benfica (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.25 -> 🟢 WON (Expected prob: 58.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 83.5% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.5% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 3 goals)

### 2026-09-05: FC Fredericia vs Esbjerg (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 58.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 81.1% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.6% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.1% (Actual: 1 goals)

### 2026-09-05: VfL Wolfsburg vs Energie Cottbus (Actual Score: **4-4**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🔴 LOST (Expected prob: 58.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 81.2% (Actual: 8 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.1% (Actual: 4 home goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.9% (Actual: 8 goals)

### 2026-09-05: The New Saints vs Barry Town (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 58.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 80.8% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.8% (Actual: 1 goals)

### 2026-09-05: Utsiktens BK vs Lunds BK (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.33 -> 🔴 LOST (Expected prob: 57.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.9% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.3% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.0% (Actual: 2 goals)

### 2026-09-05: Hardrock vs TelOne FC (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 76.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.6% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.2% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.8% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 30.6% (Actual: 5 goals)

### 2026-09-05: BSC Young Boys vs FC Luzern (Actual Score: **3-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ n/a -> 🟢 WON (Expected prob: 77.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.9% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 90.8% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.8% (Actual: 6 goals)

### 2026-09-05: Borussia M'gladbach vs SV Elversberg (Actual Score: **3-4**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6 -> 🟢 WON (Expected prob: 74.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 84.9% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.8% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.3% (Actual: 7 goals)

### 2026-09-05: Erzurum BB vs Konyaspor (Actual Score: **1-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 2.02 -> 🔴 LOST (Expected prob: 73.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.8% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 37.6% (Actual: 1 goals)

### 2026-09-05: Hansa Rostock vs SV Wehen (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.53 -> 🔴 LOST (Expected prob: 71.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.5% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 86.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 2 goals)

### 2026-09-05: Kongsvinger vs Raufoss (Actual Score: **9-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 76.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.5% (Actual: 10 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.9% (Actual: 9 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.5% (Actual: 10 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.0% (Actual: 9 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 32.7% (Actual: 10 goals)

### 2026-09-05: Bedford Town vs Radcliffe Borough (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🟢 WON (Expected prob: 61.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.6% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.3% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.4% (Actual: 1 goals)

### 2026-09-05: CA Bizertin vs Olympique Béja (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🔴 LOST (Expected prob: 61.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.0% (Actual: 2 goals)

### 2026-09-05: Aberdeen vs Kilmarnock (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🔴 LOST (Expected prob: 60.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.5% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 83.3% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.7% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.1% (Actual: 0 goals)

### 2026-09-05: Maccabi Haifa vs Hapoel Petah Tikva (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 59.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.4% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.1% (Actual: 3 goals)

### 2026-09-05: Scarborough vs AFC Telford Utd (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.9 -> 🔴 LOST (Expected prob: 59.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 82.3% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.9% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.3% (Actual: 1 goals)

### 2026-09-05: Brann vs Lillestrom SK (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🔴 LOST (Expected prob: 58.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 3 goals)

### 2026-09-05: Waldhof Mannheim vs Verl (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 2.15 -> 🔴 LOST (Expected prob: 56.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 80.1% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.2% (Actual: 1 goals)

### 2026-09-05: FC Seoul vs Incheon United (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.9 -> 🟢 WON (Expected prob: 55.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.5% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.9% (Actual: 1 goals)

### 2026-09-05: Bandirmaspor vs Boluspor (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 63.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.4% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.2% (Actual: 6 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.0% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.2% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.6% (Actual: 6 goals)

### 2026-09-05: Hereford vs Spennymoor Town (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🟢 WON (Expected prob: 55.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.1% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 3 goals)

### 2026-09-05: Kongsvinger vs Raufoss (Actual Score: **9-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.2 -> 🟢 WON (Expected prob: 81.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.4% (Actual: 10 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.6% (Actual: 9 home goals)
    - [🔴 MISS] **Home Team Under 3.5 Goals**: expected 92.0% (Actual: 9 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.3% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.0% (Actual: 10 goals)

### 2026-09-05: Koninklijke HFC vs Jong Sparta Rotterdam (Actual Score: **2-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4 -> 🟢 WON (Expected prob: 79.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.2% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.3% (Actual: 4 goals)

### 2026-09-05: Young Boys vs FC Luzern (Actual Score: **3-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.25 -> 🟢 WON (Expected prob: 78.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.6% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 90.8% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.5% (Actual: 6 goals)

### 2026-09-05: Haugesund vs Sogndal (Actual Score: **2-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.2 -> 🔴 LOST (Expected prob: 77.4%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.2% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.4% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.3% (Actual: 2 goals)

### 2026-09-05: Schalke 04 vs FC Bayern München (Actual Score: **0-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.22 -> 🔴 LOST (Expected prob: 77.4%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.3% (Actual: 0 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.4% (Actual: 0 goals)

### 2026-09-05: FC Fredericia vs Esbjerg (Actual Score: **1-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.36 -> 🔴 LOST (Expected prob: 73.8%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.0% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.1% (Actual: 1 goals)

### 2026-09-05: Sandnes ULF vs Ranheim (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.3 -> 🔴 LOST (Expected prob: 73.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.0% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.7% (Actual: 2 goals)

### 2026-09-05: Scunthorpe Utd vs Harrogate Town (Actual Score: **0-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.66 -> 🔴 LOST (Expected prob: 70.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.0% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.1% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 36.2% (Actual: 2 goals)

### 2026-09-05: Holstein Kiel vs Nürnberg (Actual Score: **2-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.57 -> 🟢 WON (Expected prob: 70.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 90.0% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.4% (Actual: 4 goals)


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
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (pending_or_unmatched_result); keys=['utrecht']/['goaheadea']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)

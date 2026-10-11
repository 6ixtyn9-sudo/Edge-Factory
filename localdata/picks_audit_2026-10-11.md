# Edge Factory — Recent picks audit (2026-09-12 to 2026-10-11)

## Overall

- archived pick rows: 618
- archived pick dates: 30
- immutable morning-baseline rows: 615
- verified official late-slate additions: 5
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 558
- eligible prior picks: 574
- pending/unmatched result picks: 9
- rescheduled result picks (settled ±3d): 6
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 1
- wins: 390
- hit rate: +69.9%
- priced picks: 478
- ROI: +0.4%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-11
- same-day rows excluded: 44

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 342 / 558 matches (61.3%)
- **Both Teams to Score (BTTS)**: occurred in 300 / 558 matches (53.8%)
- **Selected Team Over 1.5 Goals**: occurred in 368 / 558 matches (65.9%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 558
- **Total Hits**: 461
- **Overall Hit Rate**: 82.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=24, hits=21, hit_rate=87.5%
- `away_under_25`: recommended=25, hits=24, hit_rate=96.0%
- `away_under_35`: recommended=191, hits=184, hit_rate=96.3%
- `home_over_05`: recommended=18, hits=15, hit_rate=83.3%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=33, hits=33, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=224, hits=146, hit_rate=65.2%
- `match_over_35`: recommended=2, hits=0, hit_rate=0.0%
- `match_over_45`: recommended=1, hits=1, hit_rate=100.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2168** | scored: 2168

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 553 | 553 | 337 | 60.9% | 44.8% | +16.1% | 0.262653 |
| `match_over_45` | 445 | 445 | 108 | 24.3% | 23.8% | +0.5% | 0.181031 |
| `away_under_35` | 395 | 395 | 385 | 97.5% | 95.3% | +2.1% | 0.025756 |
| `away_under_25` | 370 | 370 | 342 | 92.4% | 90.7% | +1.7% | 0.070265 |
| `home_under_35` | 139 | 139 | 137 | 98.6% | 94.0% | +4.5% | 0.018049 |
| `home_under_25` | 134 | 134 | 124 | 92.5% | 89.6% | +2.9% | 0.070075 |
| `away_over_05` | 50 | 50 | 45 | 90.0% | 84.7% | +5.3% | 0.09111 |
| `away_under_15` | 33 | 33 | 24 | 72.7% | 82.0% | -9.3% | 0.206955 |
| `home_over_05` | 31 | 31 | 27 | 87.1% | 87.9% | -0.9% | 0.11813 |
| `match_over_15` | 7 | 7 | 6 | 85.7% | 82.9% | +2.8% | 0.120946 |
| `home_under_15` | 6 | 6 | 5 | 83.3% | 81.6% | +1.7% | 0.148552 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |
| `match_over_35` | 2 | 2 | 0 | 0.0% | 32.4% | -32.4% | 0.10523 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2073 | 1472 | 71.0% | 65.9% | +5.1% | 0.132746 |
| model | 95 | 70 | 73.7% | 64.6% | +9.1% | 0.173275 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 98 | 19.2% | 18.4% | -0.8% |
| 0.2-0.3 | 301 | 24.1% | 23.6% | -0.5% |
| 0.3-0.4 | 59 | 33.0% | 45.8% | +12.8% |
| 0.4-0.5 | 487 | 44.2% | 59.5% | +15.3% |
| 0.5-0.6 | 55 | 51.4% | 70.9% | +19.5% |
| 0.8-0.9 | 348 | 86.7% | 89.4% | +2.6% |
| 0.9-1.0 | 820 | 94.0% | 95.9% | +1.8% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=557, MAE=1.561472 goals, bias=-0.314614 (realized − promised), promised avg 3.539031 vs realized 3.224417

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 557 | 30.9% | 32.7% | +1.8% | 0.19843 |
| BTTS-Yes | 557 | 41.4% | 53.7% | +12.3% | 0.264717 |
| Home Over 1.5 | 557 | 64.0% | 53.5% | -10.5% | 0.236238 |
| Over 2.5 | 557 | 69.7% | 61.2% | -8.5% | 0.244422 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 238 | 8.6% | 21.8% | +13.3% |
| 0.1-0.2 | 321 | 10.4% | 19.6% | +9.2% |
| 0.2-0.3 | 8 | 26.4% | 75.0% | +48.6% |
| 0.3-0.4 | 104 | 37.3% | 51.9% | +14.6% |
| 0.4-0.5 | 440 | 42.6% | 53.6% | +11.0% |
| 0.5-0.6 | 3 | 52.2% | 33.3% | -18.9% |
| 0.6-0.7 | 375 | 66.9% | 59.2% | -7.7% |
| 0.7-0.8 | 162 | 74.4% | 65.4% | -8.9% |
| 0.8-0.9 | 523 | 84.5% | 65.0% | -19.5% |
| 0.9-1.0 | 54 | 92.3% | 74.1% | -18.3% |

## By rule

- `2way-unanimous avg_p>=60`: settled=130, wins=81, hit_rate=0.623077, ROI=-0.142371
- `2way-unanimous avg_p>=70`: settled=72, wins=56, hit_rate=0.777778, ROI=-0.042963
- `ml-meta avg_p>=55`: settled=262, wins=176, hit_rate=0.671756, ROI=0.048233
- `ml-meta avg_p>=60`: settled=63, wins=51, hit_rate=0.809524, ROI=0.112131
- `ml-meta avg_p>=65`: settled=19, wins=15, hit_rate=0.789474, ROI=-0.029333
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=9, wins=9, hit_rate=1.0, ROI=0.08375

## By bucket

- `CAUTION`: settled=38, wins=22, hit_rate=0.578947, ROI=-0.096184
- `CERTIFIED_CLEAN`: settled=65, wins=46, hit_rate=0.707692, ROI=0.104169
- `SKIPPED_VETO`: settled=278, wins=201, hit_rate=0.723022, ROI=-0.004241
- `WATCHLIST_NO_ODDS`: settled=56, wins=36, hit_rate=0.642857, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=6, wins=6, hit_rate=1.0, ROI=0.653333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=111, wins=76, hit_rate=0.684685, ROI=-0.017568
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=80, wins=55, hit_rate=0.6875, ROI=None
- `betexplorer_odds`: settled=148, wins=108, hit_rate=0.72973, ROI=0.019865
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=48, wins=35, hit_rate=0.729167, ROI=0.064792
- `oddspapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.765
- `scoutingstats_odds`: settled=230, wins=152, hit_rate=0.66087, ROI=-0.048043
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=25, wins=20, hit_rate=0.8, ROI=0.1916
- `zulubet`: settled=16, wins=10, hit_rate=0.625, ROI=-0.141875

## By odds match method

- `alias_fuzzy`: settled=15, wins=13, hit_rate=0.866667, ROI=0.217273
- `betexplorer`: settled=123, wins=87, hit_rate=0.707317, ROI=0.015691
- `exact`: settled=291, wins=203, hit_rate=0.697595, ROI=-0.003622
- `fallback`: settled=53, wins=36, hit_rate=0.679245, ROI=-0.029245
- `none`: settled=76, wins=51, hit_rate=0.671053, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 123 | 87 | 0.707317 | 123 | 0.015691 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 52 | 43 | 0.826923 | 52 | 0.1405 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 230 | 152 | 0.66087 | 230 | -0.048043 |
| Source fallback (`SOURCE_FALLBACK`) | 53 | 36 | 0.679245 | 53 | -0.029245 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 15 | 13 | 0.866667 | 11 | 0.217273 |
| No usable price (`UNMATCHED`) | 76 | 51 | 0.671053 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 278 | 201 | 0.723022 | 257 | -0.004241 |
| **trusted evidence only** | 107 | 84 | 0.785047 | 107 | 0.045701 |
| **soft evidence only** | 171 | 117 | 0.684211 | 150 | -0.039867 |
| evidence: BETEXPLORER_RESCUE | 70 | 50 | 0.714286 | 70 | -0.038 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 32 | 29 | 0.90625 | 32 | 0.172812 |
| evidence: SCOUTINGSTATS_SOLE | 119 | 76 | 0.638655 | 119 | -0.076471 |
| evidence: SOURCE_FALLBACK | 23 | 19 | 0.826087 | 23 | 0.116957 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 8 | 0.05375 |
| evidence: UNMATCHED | 20 | 15 | 0.75 | 0 | None |
| odds band: <1.50 | 161 | 131 | 0.813665 | 161 | 0.019379 |
| odds band: 1.50-2.00 | 93 | 51 | 0.548387 | 93 | -0.082903 |
| odds band: 2.00-3.00 | 3 | 3 | 1.0 | 3 | 1.166667 |
| odds band: unpriced | 21 | 16 | 0.761905 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.193333 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 0 | 0.0 | 2 | -1.0 |
| veto reason: context VETO in ['league', 'team_h'] | 11 | 9 | 0.818182 | 11 | 0.077273 |
| veto reason: context VETO in ['league'] | 28 | 20 | 0.714286 | 23 | -0.003478 |
| veto reason: context VETO in ['niche'] | 10 | 9 | 0.9 | 10 | 0.224 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 53 | 41 | 0.773585 | 53 | -0.015283 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.193333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.556667 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 14 | 11 | 0.785714 | 14 | -0.035 |
| veto reason: context VETO in ['team_a'] | 51 | 37 | 0.72549 | 45 | 0.068222 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.103333 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 16 | 10 | 0.625 | 15 | 0.020667 |
| veto reason: context VETO in ['team_h'] | 49 | 33 | 0.673469 | 41 | -0.017561 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 21 | 13 | 0.619048 | 21 | -0.050952 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 5 | 4 | 0.8 | 5 | 0.403 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.327273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 306 | 221 | 0.722222 | 230 | 0.0522 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 15 | 13 | 0.866667 | 11 | 0.217273 | 15 | 1.524667 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 230 | 152 | 0.66087 | 230 | -0.048043 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 7 | 4 | 0.571429 | 7 | -0.232857 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-10: RB Leipzig vs Eintracht Frankfurt (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 66.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.9% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.0% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.3% (Actual: 6 goals)

### 2026-10-10: Samsunspor vs Trabzonspor (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 2.06 -> 🟢 WON (Expected prob: 56.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.6% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.5% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.0% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 3 goals)

### 2026-10-10: Crawley Town vs Chesterfield (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.67 -> 🔴 LOST (Expected prob: 59.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.4% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.8% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.2% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 4 goals)

### 2026-10-10: Once Caldas vs Llaneros (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.52 -> 🟢 WON (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.5% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.2% (Actual: 1 goals)

### 2026-10-10: FC Tokyo vs Urawa (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.76 -> 🟢 WON (Expected prob: 55.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 63.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.0% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.6% (Actual: 3 goals)

### 2026-10-10: Ansbach vs Nürnberg II (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🟢 WON (Expected prob: 65.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.2% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.3% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.1% (Actual: 1 goals)

### 2026-10-10: Rosenborg vs Sandefjord (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🔴 LOST (Expected prob: 64.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.0% (Actual: 2 goals)

### 2026-10-10: Vilzing vs Buchbach (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 2.76 -> 🔴 LOST (Expected prob: 58.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.1% (Actual: 2 goals)

### 2026-10-10: Bodo/Glimt vs Kristiansund BK (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.09 -> 🟢 WON (Expected prob: 84.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 86.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 93.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 86.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.1% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.8% (Actual: 4 goals)

### 2026-10-10: Barcelona vs Getafe (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.09 -> 🟢 WON (Expected prob: 80.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 37.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 88.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 38.8% (Actual: 3 goals)

### 2026-10-10: Maccabi Tel Aviv vs Bnei Sakhnin (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🔴 LOST (Expected prob: 78.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.5% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 92.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 88.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.4% (Actual: 0 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.4% (Actual: 0 goals)

### 2026-10-10: Rangers vs Kilmarnock (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.17 -> 🟢 WON (Expected prob: 76.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.6% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.8% (Actual: 4 goals)

### 2026-10-10: FC Augsburg vs Bayern Munich (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.2 -> 🔴 LOST (Expected prob: 75.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 24.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 97.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 90.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.4% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 90.3% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.9% (Actual: 4 goals)

### 2026-10-10: Inter vs Parma (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.15 -> 🟢 WON (Expected prob: 74.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.5% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 33.0% (Actual: 3 goals)

### 2026-10-10: Spezia vs Gubbio (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 74.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.4% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.5% (Actual: 2 goals)

### 2026-10-10: Buriram United vs Rayong FC (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 73.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.6% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.0% (Actual: 5 goals)

### 2026-10-10: Vasco da Gama vs Remo (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.34 -> 🔴 LOST (Expected prob: 72.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.1% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.1% (Actual: 0 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.2% (Actual: 0 goals)

### 2026-10-10: Stockport County FC vs Barnsley (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.47 -> 🟢 WON (Expected prob: 70.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.1% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.8% (Actual: 4 goals)

### 2026-10-10: Paris Saint Germain vs Le Mans (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.12 -> 🟢 WON (Expected prob: 69.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.3% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.9% (Actual: 4 goals)

### 2026-10-10: Real Madrid vs Villarreal (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 65.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.5% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.1% (Actual: 1 goals)

### 2026-10-10: Lille vs Le Havre (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 63.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.9% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.2% (Actual: 1 goals)

### 2026-10-10: FC Lugano vs FC Luzern (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.67 -> 🟢 WON (Expected prob: 63.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.0% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.0% (Actual: 4 goals)

### 2026-10-10: Slask Wroclaw vs Lech Poznan (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.63 -> 🟢 WON (Expected prob: 57.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.6% (Actual: 4 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.3% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.9% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.7% (Actual: 5 goals)

### 2026-10-10: Botev Plovdiv vs Slavia Sofia (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 57.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.6% (Actual: 1 goals)

### 2026-10-10: SC Paderborn 07 vs VfB Stuttgart (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.64 -> 🟢 WON (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.5% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.9% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 2 goals)

### 2026-10-10: FCSB vs Otelul Galati (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 68.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.8% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.8% (Actual: 1 goals)

### 2026-10-10: Raith Rovers vs Queens Park (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 63.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.4% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.9% (Actual: 2 goals)

### 2026-10-10: Monaco vs Toulouse (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 61.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 4 goals)

### 2026-10-10: Montrose vs Ross County (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.42 -> 🟢 WON (Expected prob: 60.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.4% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.7% (Actual: 5 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.3% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.4% (Actual: 5 goals)

### 2026-10-10: Arsenal vs Leeds (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 58.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 3 goals)

### 2026-10-10: Clyde vs Dumbarton (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 57.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.8% (Actual: 3 goals)

### 2026-10-10: 1899 Hoffenheim vs Hamburger SV (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.7% (Actual: 5 goals)

### 2026-10-10: Vasas vs Kisvarda (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 56.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.8% (Actual: 2 goals)

### 2026-10-10: AFC Fylde vs Scunthorpe (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 56.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.9% (Actual: 2 goals)

### 2026-10-10: Kairat Almaty vs Zhetysu (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 78.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 92.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 88.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.9% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.5% (Actual: 1 goals)

### 2026-10-10: Cetatea Suceava vs Dumbravita (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.4% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.6% (Actual: 4 goals)

### 2026-10-10: Al-Tadhamon vs Al-Qadsia (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 70.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 36.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.9% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 81.7% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.1% (Actual: 2 goals)

### 2026-10-10: Ferencvarosi TC vs Debreceni VSC (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 68.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.5% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.5% (Actual: 2 goals)

### 2026-10-10: Bari vs Giugliano (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 62.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 2 goals)

### 2026-10-10: Trelleborgs FF vs Kristianstad FC (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 62.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.0% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 2 goals)

### 2026-10-10: York vs Northampton (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 59.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.6% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.4% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.6% (Actual: 2 goals)

### 2026-10-10: Cobresal vs Universidad De Concepcion (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.1% (Actual: 2 goals)

### 2026-10-10: Genk vs Kortrijk (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 58.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.8% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.7% (Actual: 3 goals)

### 2026-10-10: Grazer AK vs Red Bull Salzburg (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 57.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.4% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.3% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected 80.0% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.9% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.9% (Actual: 0 goals)

### 2026-10-10: Dacia Buiucani vs Sheriff Tiraspol (Actual Score: **2-5**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 57.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.1% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.1% (Actual: 5 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.9% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.5% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.3% (Actual: 7 goals)

### 2026-10-10: RAAL La Louvière vs Club Brugge KV (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.4% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.3% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.4% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 26.3% (Actual: 5 goals)

### 2026-10-10: Maritimo vs FC Porto (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.33 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 36.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.8% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 81.5% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.6% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.1% (Actual: 3 goals)

### 2026-10-10: FC Halifax Town vs Gateshead (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 68.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.2% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 26.0% (Actual: 5 goals)

### 2026-10-10: Leixoes vs FC Porto B (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🔴 LOST (Expected prob: 65.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.4% (Actual: 3 goals)

### 2026-10-10: Worthing vs Solihull Moors (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🟢 WON (Expected prob: 61.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.2% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.1% (Actual: 5 goals)

### 2026-10-10: Casa Pia vs Santa Clara (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.85 -> 🟢 WON (Expected prob: 59.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.3% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.2% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.1% (Actual: 1 goals)

### 2026-10-10: Penarol vs Progreso (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🔴 LOST (Expected prob: 62.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.0% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 2 goals)

### 2026-10-10: Philadelphia Union vs Real Salt Lake (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 60.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.2% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 3 goals)

### 2026-10-10: Ironi Tiberias vs Hapoel Beer Sheva (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🟢 WON (Expected prob: 59.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.9% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.6% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.7% (Actual: 2 goals)

### 2026-10-10: Inter Miami vs DC United (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 59.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.1% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.5% (Actual: 4 goals)

### 2026-10-10: Radomlje vs FC Koper (Actual Score: **3-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.72 -> 🔴 LOST (Expected prob: 57.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.7% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 81.4% (Actual: 3 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 85.6% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.0% (Actual: 6 goals)

### 2026-10-10: Zemplin Michalovce vs Dunajska Streda (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.61 -> 🟢 WON (Expected prob: 57.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.0% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.2% (Actual: 3 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.1% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.8% (Actual: 3 goals)


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

- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

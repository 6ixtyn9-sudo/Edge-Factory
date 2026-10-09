# Edge Factory — Recent picks audit (2026-09-10 to 2026-10-09)

## Overall

- archived pick rows: 545
- archived pick dates: 30
- immutable morning-baseline rows: 542
- verified official late-slate additions: 5
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 512
- eligible prior picks: 529
- pending/unmatched result picks: 9
- rescheduled result picks (settled ±3d): 6
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 352
- hit rate: +68.8%
- priced picks: 449
- ROI: -2.3%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-09
- same-day rows excluded: 16

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 318 / 512 matches (62.1%)
- **Both Teams to Score (BTTS)**: occurred in 279 / 512 matches (54.5%)
- **Selected Team Over 1.5 Goals**: occurred in 339 / 512 matches (66.2%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 512
- **Total Hits**: 415
- **Overall Hit Rate**: 81.1%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=21, hits=19, hit_rate=90.5%
- `away_under_25`: recommended=25, hits=24, hit_rate=96.0%
- `away_under_35`: recommended=165, hits=158, hit_rate=95.8%
- `home_over_05`: recommended=8, hits=6, hit_rate=75.0%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=29, hits=29, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=205, hits=133, hit_rate=64.9%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%
- `match_over_45`: recommended=1, hits=1, hit_rate=100.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2002** | scored: 2002

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 503 | 503 | 311 | 61.8% | 44.9% | +17.0% | 0.264036 |
| `match_over_45` | 413 | 413 | 103 | 24.9% | 23.9% | +1.1% | 0.18444 |
| `away_under_35` | 355 | 355 | 344 | 96.9% | 95.4% | +1.5% | 0.030632 |
| `away_under_25` | 334 | 334 | 303 | 90.7% | 91.0% | -0.2% | 0.084349 |
| `home_under_35` | 125 | 125 | 122 | 97.6% | 93.4% | +4.2% | 0.026983 |
| `home_under_25` | 124 | 124 | 114 | 91.9% | 90.0% | +2.0% | 0.074902 |
| `away_over_05` | 44 | 44 | 39 | 88.6% | 86.0% | +2.7% | 0.099451 |
| `away_under_15` | 33 | 33 | 24 | 72.7% | 82.0% | -9.3% | 0.206955 |
| `match_over_35` | 28 | 28 | 13 | 46.4% | 38.4% | +8.1% | 0.275875 |
| `home_over_05` | 22 | 22 | 19 | 86.4% | 86.1% | +0.2% | 0.129344 |
| `home_under_15` | 11 | 11 | 7 | 63.6% | 81.6% | -17.9% | 0.26803 |
| `match_over_15` | 7 | 7 | 6 | 85.7% | 82.9% | +2.8% | 0.120946 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1912 | 1344 | 70.3% | 65.4% | +4.9% | 0.140492 |
| model | 90 | 63 | 70.0% | 63.6% | +6.4% | 0.204597 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 89 | 19.2% | 19.1% | -0.1% |
| 0.2-0.3 | 278 | 24.1% | 24.1% | +0.0% |
| 0.3-0.4 | 74 | 33.3% | 48.6% | +15.4% |
| 0.4-0.5 | 449 | 44.2% | 60.6% | +16.4% |
| 0.5-0.6 | 54 | 51.6% | 64.8% | +13.2% |
| 0.8-0.9 | 306 | 86.6% | 87.6% | +1.0% |
| 0.9-1.0 | 752 | 94.0% | 94.7% | +0.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=511, MAE=1.576301 goals, bias=-0.263542 (realized − promised), promised avg 3.539472 vs realized 3.27593

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 511 | 31.2% | 33.9% | +2.7% | 0.209351 |
| BTTS-Yes | 511 | 41.4% | 54.4% | +13.0% | 0.26539 |
| Home Over 1.5 | 511 | 63.7% | 54.4% | -9.3% | 0.238213 |
| Over 2.5 | 511 | 69.7% | 62.0% | -7.7% | 0.241749 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 229 | 8.6% | 22.7% | +14.1% |
| 0.1-0.2 | 284 | 10.4% | 22.2% | +11.8% |
| 0.2-0.3 | 7 | 26.7% | 71.4% | +44.7% |
| 0.3-0.4 | 97 | 37.3% | 50.5% | +13.2% |
| 0.4-0.5 | 404 | 42.7% | 55.0% | +12.3% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 345 | 67.0% | 60.3% | -6.7% |
| 0.7-0.8 | 147 | 74.3% | 66.0% | -8.3% |
| 0.8-0.9 | 482 | 84.6% | 65.4% | -19.2% |
| 0.9-1.0 | 48 | 92.4% | 72.9% | -19.4% |

## By rule

- `2way-unanimous avg_p>=60`: settled=130, wins=81, hit_rate=0.623077, ROI=-0.142371
- `2way-unanimous avg_p>=70`: settled=65, wins=49, hit_rate=0.753846, ROI=-0.086042
- `ml-meta avg_p>=55`: settled=238, wins=155, hit_rate=0.651261, ROI=-0.004996
- `ml-meta avg_p>=60`: settled=56, wins=47, hit_rate=0.839286, ROI=0.155179
- `ml-meta avg_p>=65`: settled=14, wins=12, hit_rate=0.857143, ROI=0.041538
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=6, wins=6, hit_rate=1.0, ROI=0.072

## By bucket

- `CAUTION`: settled=37, wins=20, hit_rate=0.540541, ROI=-0.172027
- `CERTIFIED_CLEAN`: settled=61, wins=45, hit_rate=0.737705, ROI=0.146246
- `SKIPPED_VETO`: settled=253, wins=177, hit_rate=0.699605, ROI=-0.047029
- `WATCHLIST_NO_ODDS`: settled=47, wins=31, hit_rate=0.659574, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=5, hit_rate=1.0, ROI=0.653333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=105, wins=71, hit_rate=0.67619, ROI=-0.030857
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=63, wins=45, hit_rate=0.714286, ROI=None
- `betexplorer_odds`: settled=149, wins=103, hit_rate=0.691275, ROI=-0.022148
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=50, wins=36, hit_rate=0.72, ROI=0.0462
- `oddspapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.765
- `scoutingstats_odds`: settled=219, wins=143, hit_rate=0.652968, ROI=-0.064018
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=9, wins=8, hit_rate=0.888889, ROI=0.228889
- `zulubet`: settled=12, wins=8, hit_rate=0.666667, ROI=-0.084167

## By odds match method

- `alias_fuzzy`: settled=14, wins=12, hit_rate=0.857143, ROI=0.216364
- `betexplorer`: settled=136, wins=92, hit_rate=0.676471, ROI=-0.029926
- `exact`: settled=251, wins=171, hit_rate=0.681275, ROI=-0.029936
- `fallback`: settled=51, wins=35, hit_rate=0.686275, ROI=-0.021176
- `none`: settled=60, wins=42, hit_rate=0.7, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 136 | 92 | 0.676471 | 136 | -0.029926 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 24 | 21 | 0.875 | 24 | 0.180667 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 219 | 143 | 0.652968 | 219 | -0.064018 |
| Source fallback (`SOURCE_FALLBACK`) | 51 | 35 | 0.686275 | 51 | -0.021176 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 14 | 12 | 0.857143 | 11 | 0.216364 |
| No usable price (`UNMATCHED`) | 60 | 42 | 0.7 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 253 | 177 | 0.699605 | 239 | -0.047029 |
| **trusted evidence only** | 93 | 68 | 0.731183 | 93 | -0.027634 |
| **soft evidence only** | 160 | 109 | 0.68125 | 146 | -0.059384 |
| evidence: BETEXPLORER_RESCUE | 78 | 53 | 0.679487 | 78 | -0.084872 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 10 | 10 | 1.0 | 10 | 0.203 |
| evidence: SCOUTINGSTATS_SOLE | 114 | 72 | 0.631579 | 114 | -0.094561 |
| evidence: SOURCE_FALLBACK | 24 | 19 | 0.791667 | 24 | 0.070417 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 8 | 0.0525 |
| evidence: UNMATCHED | 13 | 11 | 0.846154 | 0 | None |
| odds band: <1.50 | 148 | 118 | 0.797297 | 148 | -0.003041 |
| odds band: 1.50-2.00 | 88 | 44 | 0.5 | 88 | -0.162386 |
| odds band: 2.00-3.00 | 3 | 3 | 1.0 | 3 | 1.166667 |
| odds band: unpriced | 14 | 12 | 0.857143 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.4 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 0 | 0.0 | 2 | -1.0 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 11 | 9 | 0.818182 | 11 | 0.077273 |
| veto reason: context VETO in ['league'] | 25 | 18 | 0.72 | 20 | -0.0045 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 53 | 40 | 0.754717 | 53 | -0.035849 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.085 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.556667 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 14 | 11 | 0.785714 | 14 | -0.017857 |
| veto reason: context VETO in ['team_a'] | 41 | 25 | 0.609756 | 37 | -0.108108 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.105 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 11 | 6 | 0.545455 | 11 | -0.159091 |
| veto reason: context VETO in ['team_h'] | 45 | 31 | 0.688889 | 41 | 0.012195 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 22 | 13 | 0.590909 | 22 | -0.094091 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 3 | 2 | 0.666667 | 3 | 0.101667 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.327273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 275 | 194 | 0.705455 | 215 | 0.007051 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 14 | 12 | 0.857143 | 11 | 0.216364 | 14 | 1.534286 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 219 | 143 | 0.652968 | 219 | -0.064018 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 4 | 3 | 0.75 | 4 | -0.04 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-08: Sepahan FC vs Fajr Sepasi (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.54 -> 🟢 WON (Expected prob: 57.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.4% (Actual: 6 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.6% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 7 goals)

### 2026-10-08: KuPS vs AC Oulu (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 63.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 91.6% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.3% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.0% (Actual: 1 goals)

### 2026-10-08: Ghazl El Mehalla vs Abu Qair Semad (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 2.4 -> 🔴 LOST (Expected prob: 55.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 63.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.5% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.2% (Actual: 2 goals)

### 2026-10-08: Shamrock Rovers vs Drogheda United (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🟢 WON (Expected prob: 65.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.0% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 92.5% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.1% (Actual: 4 goals)

### 2026-10-08: Cruzeiro vs Sao Paulo (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🟢 WON (Expected prob: 56.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.1% (Actual: 2 goals)

### 2026-10-08: MC Oran vs ES Setif (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.98 -> 🔴 LOST (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.6% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.1% (Actual: 0 goals)

### 2026-10-08: Shakhter Karagandy vs Akademiya Ontustik (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 72.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.3% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 93.2% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.1% (Actual: 2 goals)


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

- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

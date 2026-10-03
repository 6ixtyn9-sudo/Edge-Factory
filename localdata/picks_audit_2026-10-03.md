# Edge Factory — Recent picks audit (2026-09-04 to 2026-10-03)

## Overall

- archived pick rows: 634
- archived pick dates: 30
- immutable morning-baseline rows: 634
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 574
- eligible prior picks: 593
- pending/unmatched result picks: 9
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 1
- ambiguous result picks: 3
- wins: 384
- hit rate: +66.9%
- priced picks: 530
- ROI: -4.6%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-03
- same-day rows excluded: 41

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 338 / 544 matches (62.1%)
- **Both Teams to Score (BTTS)**: occurred in 304 / 544 matches (55.9%)
- **Selected Team Over 1.5 Goals**: occurred in 357 / 544 matches (65.6%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 574
- **Total Hits**: 458
- **Overall Hit Rate**: 79.8%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=19, hits=17, hit_rate=89.5%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=165, hits=159, hit_rate=96.4%
- `home_over_05`: recommended=24, hits=17, hit_rate=70.8%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=31, hits=30, hit_rate=96.8%
- `match_over_15`: recommended=28, hits=22, hit_rate=78.6%
- `match_over_25`: recommended=232, hits=151, hit_rate=65.1%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2275** | scored: 2275

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 569 | 569 | 353 | 62.0% | 45.1% | +16.9% | 0.26305 |
| `match_over_45` | 450 | 450 | 120 | 26.7% | 23.7% | +2.9% | 0.192083 |
| `away_under_35` | 399 | 399 | 387 | 97.0% | 95.9% | +1.1% | 0.029181 |
| `away_under_25` | 365 | 365 | 332 | 91.0% | 91.8% | -0.9% | 0.082403 |
| `home_under_35` | 159 | 159 | 155 | 97.5% | 93.9% | +3.5% | 0.026658 |
| `home_under_25` | 133 | 133 | 124 | 93.2% | 90.5% | +2.8% | 0.063498 |
| `home_over_05` | 77 | 77 | 67 | 87.0% | 83.2% | +3.8% | 0.112583 |
| `away_over_05` | 33 | 33 | 30 | 90.9% | 87.8% | +3.1% | 0.083325 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `match_over_15` | 28 | 28 | 22 | 78.6% | 84.0% | -5.4% | 0.167602 |
| `away_under_15` | 13 | 13 | 11 | 84.6% | 82.8% | +1.9% | 0.139111 |
| `home_under_15` | 13 | 13 | 9 | 69.2% | 81.6% | -12.3% | 0.232124 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2081 | 1494 | 71.8% | 66.4% | +5.4% | 0.137344 |
| model | 194 | 133 | 68.6% | 62.8% | +5.7% | 0.182275 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 107 | 19.2% | 18.7% | -0.5% |
| 0.2-0.3 | 298 | 24.1% | 26.5% | +2.4% |
| 0.3-0.4 | 81 | 33.5% | 51.9% | +18.4% |
| 0.4-0.5 | 498 | 44.4% | 60.6% | +16.3% |
| 0.5-0.6 | 68 | 51.9% | 66.2% | +14.3% |
| 0.8-0.9 | 306 | 85.8% | 87.6% | +1.8% |
| 0.9-1.0 | 917 | 94.4% | 95.0% | +0.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=543, MAE=1.580442 goals, bias=-0.232339 (realized − promised), promised avg 3.51779 vs realized 3.285451

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 543 | 31.2% | 34.8% | +3.6% | 0.222136 |
| BTTS-Yes | 543 | 41.6% | 55.8% | +14.2% | 0.265869 |
| Home Over 1.5 | 543 | 63.6% | 54.7% | -8.9% | 0.243043 |
| Over 2.5 | 543 | 69.5% | 62.1% | -7.4% | 0.240592 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 225 | 8.6% | 23.1% | +14.5% |
| 0.1-0.2 | 321 | 10.4% | 24.9% | +14.5% |
| 0.2-0.3 | 4 | 26.1% | 75.0% | +48.9% |
| 0.3-0.4 | 99 | 37.3% | 50.5% | +13.2% |
| 0.4-0.5 | 436 | 42.9% | 56.9% | +14.0% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 378 | 66.9% | 60.3% | -6.6% |
| 0.7-0.8 | 146 | 74.4% | 65.8% | -8.7% |
| 0.8-0.9 | 516 | 84.5% | 65.3% | -19.2% |
| 0.9-1.0 | 46 | 92.6% | 69.6% | -23.0% |

## By rule

- `2way-unanimous avg_p>=60`: settled=93, wins=60, hit_rate=0.645161, ROI=-0.127722
- `2way-unanimous avg_p>=70`: settled=80, wins=60, hit_rate=0.75, ROI=-0.05127
- `ml-meta avg_p>=55`: settled=300, wins=186, hit_rate=0.62, ROI=-0.052042
- `ml-meta avg_p>=60`: settled=51, wins=43, hit_rate=0.843137, ROI=0.166667
- `ml-meta avg_p>=65`: settled=12, wins=10, hit_rate=0.833333, ROI=0.029091
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=5, wins=5, hit_rate=1.0, ROI=0.07
- `ou25-unanimous-2way-sa avg_p>=70`: settled=30, wins=18, hit_rate=0.6, ROI=-0.153103

## By bucket

- `CAUTION`: settled=49, wins=29, hit_rate=0.591837, ROI=-0.09
- `CERTIFIED_CLEAN`: settled=58, wins=42, hit_rate=0.724138, ROI=0.134138
- `SKIPPED_VETO`: settled=284, wins=185, hit_rate=0.651408, ROI=-0.099489
- `WATCHLIST_NO_ODDS`: settled=32, wins=24, hit_rate=0.75, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=14, wins=9, hit_rate=0.642857, ROI=0.074167
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=133, wins=92, hit_rate=0.691729, ROI=-0.008346
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=44, wins=33, hit_rate=0.75, ROI=None
- `betexplorer_odds`: settled=173, wins=115, hit_rate=0.66474, ROI=-0.05185
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=75, wins=53, hit_rate=0.706667, ROI=0.056933
- `scoutingstats_odds`: settled=271, wins=174, hit_rate=0.642066, ROI=-0.079594
- `zulubet`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.11

## By odds match method

- `alias_fuzzy`: settled=22, wins=15, hit_rate=0.681818, ROI=0.014211
- `betexplorer`: settled=173, wins=115, hit_rate=0.66474, ROI=-0.05185
- `exact`: settled=279, wins=181, hit_rate=0.648746, ROI=-0.069534
- `fallback`: settled=59, wins=42, hit_rate=0.711864, ROI=0.062203
- `none`: settled=41, wins=31, hit_rate=0.756098, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 173 | 115 | 0.66474 | 173 | -0.05185 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 271 | 174 | 0.642066 | 271 | -0.079594 |
| Source fallback (`SOURCE_FALLBACK`) | 59 | 42 | 0.711864 | 59 | 0.062203 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 22 | 15 | 0.681818 | 19 | 0.014211 |
| No usable price (`UNMATCHED`) | 41 | 31 | 0.756098 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 284 | 185 | 0.651408 | 274 | -0.099489 |
| **trusted evidence only** | 104 | 71 | 0.682692 | 104 | -0.071827 |
| **soft evidence only** | 180 | 114 | 0.633333 | 170 | -0.116412 |
| evidence: BETEXPLORER_RESCUE | 99 | 66 | 0.666667 | 99 | -0.095859 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: SCOUTINGSTATS_SOLE | 138 | 82 | 0.594203 | 138 | -0.148261 |
| evidence: SOURCE_FALLBACK | 25 | 19 | 0.76 | 25 | 0.0516 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.088571 |
| evidence: UNMATCHED | 9 | 7 | 0.777778 | 0 | None |
| odds band: <1.50 | 169 | 126 | 0.745562 | 169 | -0.05645 |
| odds band: 1.50-2.00 | 99 | 47 | 0.474747 | 99 | -0.205758 |
| odds band: 2.00-3.00 | 6 | 4 | 0.666667 | 6 | 0.441667 |
| odds band: unpriced | 10 | 8 | 0.8 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.29 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.4 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.49 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 14 | 10 | 0.714286 | 14 | -0.047857 |
| veto reason: context VETO in ['league'] | 22 | 16 | 0.727273 | 17 | 0.032353 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 63 | 44 | 0.698413 | 63 | -0.103016 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.085 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 8 | 0.727273 | 11 | -0.129091 |
| veto reason: context VETO in ['team_a'] | 47 | 24 | 0.510638 | 45 | -0.221778 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.128571 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.218 |
| veto reason: context VETO in ['team_h', 'team_a'] | 12 | 6 | 0.5 | 12 | -0.1575 |
| veto reason: context VETO in ['team_h'] | 55 | 35 | 0.636364 | 53 | -0.051509 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 30 | 18 | 0.6 | 30 | -0.104667 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 18 | 11 | 0.611111 | 18 | -0.015 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 281 | 195 | 0.69395 | 240 | -0.013042 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 22 | 15 | 0.681818 | 19 | 0.014211 | 22 | 1.589545 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 271 | 174 | 0.642066 | 271 | -0.079594 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-02: Bayer Leverkusen (w) vs Werder Bremen (w) (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.67 -> 🟢 WON (Expected prob: 60.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.0% (Actual: 5 goals)

### 2026-10-02: Helmond Sport vs Heracles (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.49 -> 🔴 LOST (Expected prob: 77.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 34.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 94.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 93.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.5% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.9% (Actual: 4 goals)

### 2026-10-02: Belgium vs Türkiye (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 66.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.5% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.4% (Actual: 3 goals)

### 2026-10-02: Bray Wanderers vs Cobh Ramblers (Actual Score: **1-4**)
- **1X2 Pick**: Selected `HOME` @ 1.64 -> 🔴 LOST (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.6% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 96.8% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 90.3% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.4% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.2% (Actual: 5 goals)

### 2026-10-02: Seattle Sounders vs Sporting Kansas City (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 64.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.0% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.9% (Actual: 3 goals)

### 2026-10-02: France vs Italy (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🔴 LOST (Expected prob: 63.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.0% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.2% (Actual: 2 goals)

### 2026-10-02: Belgium vs Turkey (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.56 -> 🟢 WON (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.6% (Actual: 3 goals)

### 2026-10-02: South Korea vs Venezuela (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.68 -> 🔴 LOST (Expected prob: 58.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.5% (Actual: 0 goals)

### 2026-10-02: Faroe Islands vs Slovakia (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🔴 LOST (Expected prob: 60.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.0% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.7% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.6% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.2% (Actual: 2 goals)


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

## Ambiguous result examples

- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

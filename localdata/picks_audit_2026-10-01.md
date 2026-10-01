# Edge Factory — Recent picks audit (2026-09-02 to 2026-10-01)

## Overall

- archived pick rows: 601
- archived pick dates: 30
- immutable morning-baseline rows: 601
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 568
- eligible prior picks: 588
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 1
- ambiguous result picks: 3
- wins: 386
- hit rate: +68.0%
- priced picks: 526
- ROI: -3.0%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-01
- same-day rows excluded: 13

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 330 / 534 matches (61.8%)
- **Both Teams to Score (BTTS)**: occurred in 294 / 534 matches (55.1%)
- **Selected Team Over 1.5 Goals**: occurred in 351 / 534 matches (65.7%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 568
- **Total Hits**: 453
- **Overall Hit Rate**: 79.8%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=19, hits=17, hit_rate=89.5%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=154, hits=149, hit_rate=96.8%
- `home_over_05`: recommended=24, hits=17, hit_rate=70.8%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=28, hits=27, hit_rate=96.4%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=225, hits=147, hit_rate=65.3%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2268** | scored: 2268

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 562 | 562 | 348 | 61.9% | 45.1% | +16.8% | 0.262907 |
| `match_over_45` | 445 | 445 | 120 | 27.0% | 23.7% | +3.3% | 0.193819 |
| `away_under_35` | 392 | 392 | 381 | 97.2% | 95.9% | +1.3% | 0.027281 |
| `away_under_25` | 359 | 359 | 327 | 91.1% | 91.9% | -0.8% | 0.081278 |
| `home_under_35` | 161 | 161 | 157 | 97.5% | 94.0% | +3.5% | 0.026361 |
| `home_under_25` | 133 | 133 | 125 | 94.0% | 90.5% | +3.4% | 0.057765 |
| `home_over_05` | 84 | 84 | 74 | 88.1% | 83.4% | +4.7% | 0.105184 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `away_over_05` | 33 | 33 | 30 | 90.9% | 87.8% | +3.1% | 0.083325 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `home_under_15` | 13 | 13 | 9 | 69.2% | 81.6% | -12.3% | 0.232124 |
| `away_under_15` | 7 | 7 | 6 | 85.7% | 81.7% | +4.0% | 0.140133 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2056 | 1477 | 71.8% | 66.6% | +5.2% | 0.136144 |
| model | 212 | 151 | 71.2% | 63.2% | +8.0% | 0.181139 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 112 | 19.2% | 18.8% | -0.4% |
| 0.2-0.3 | 289 | 24.2% | 27.3% | +3.1% |
| 0.3-0.4 | 79 | 33.4% | 51.9% | +18.5% |
| 0.4-0.5 | 490 | 44.3% | 60.4% | +16.1% |
| 0.5-0.6 | 70 | 52.0% | 65.7% | +13.8% |
| 0.8-0.9 | 308 | 85.7% | 87.7% | +1.9% |
| 0.9-1.0 | 920 | 94.4% | 95.1% | +0.7% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=533, MAE=1.578743 goals, bias=-0.229962 (realized − promised), promised avg 3.515141 vs realized 3.285178

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 533 | 31.8% | 35.5% | +3.7% | 0.224803 |
| BTTS-Yes | 533 | 41.6% | 55.0% | +13.4% | 0.264874 |
| Home Over 1.5 | 533 | 63.1% | 54.0% | -9.0% | 0.23821 |
| Over 2.5 | 533 | 69.5% | 61.7% | -7.7% | 0.241219 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 221 | 8.7% | 23.5% | +14.8% |
| 0.1-0.2 | 314 | 10.4% | 24.5% | +14.1% |
| 0.2-0.3 | 7 | 24.6% | 57.1% | +32.5% |
| 0.3-0.4 | 94 | 37.3% | 51.1% | +13.8% |
| 0.4-0.5 | 429 | 42.9% | 55.7% | +12.8% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 371 | 66.9% | 59.8% | -7.1% |
| 0.7-0.8 | 144 | 74.3% | 65.3% | -9.1% |
| 0.8-0.9 | 508 | 84.5% | 65.6% | -18.9% |
| 0.9-1.0 | 43 | 92.5% | 69.8% | -22.8% |

## By rule

- `2way-unanimous avg_p>=60`: settled=82, wins=54, hit_rate=0.658537, ROI=-0.12029
- `2way-unanimous avg_p>=70`: settled=82, wins=62, hit_rate=0.756098, ROI=-0.036462
- `ml-meta avg_p>=55`: settled=301, wins=189, hit_rate=0.627907, ROI=-0.037621
- `ml-meta avg_p>=60`: settled=49, wins=42, hit_rate=0.857143, ROI=0.180204
- `ml-meta avg_p>=65`: settled=11, wins=9, hit_rate=0.818182, ROI=0.065455
- `ml-meta avg_p>=70`: settled=4, wins=3, hit_rate=0.75, ROI=-0.17
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=4, wins=4, hit_rate=1.0, ROI=0.07
- `ou25-unanimous-2way-sa avg_p>=70`: settled=34, wins=22, hit_rate=0.647059, ROI=-0.097576

## By bucket

- `CAUTION`: settled=45, wins=28, hit_rate=0.622222, ROI=-0.043778
- `CERTIFIED_CLEAN`: settled=58, wins=41, hit_rate=0.706897, ROI=0.108966
- `SKIPPED_VETO`: settled=279, wins=185, hit_rate=0.663082, ROI=-0.078487
- `WATCHLIST_NO_ODDS`: settled=32, wins=24, hit_rate=0.75, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=16, wins=11, hit_rate=0.6875, ROI=0.098571
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=134, wins=94, hit_rate=0.701493, ROI=0.00194
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=42, wins=31, hit_rate=0.738095, ROI=None
- `betexplorer_odds`: settled=163, wins=109, hit_rate=0.668712, ROI=-0.050184
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=78, wins=56, hit_rate=0.717949, ROI=0.069359
- `scoutingstats_odds`: settled=275, wins=181, hit_rate=0.658182, ROI=-0.056982
- `zulubet`: settled=2, wins=2, hit_rate=1.0, ROI=0.335

## By odds match method

- `alias_fuzzy`: settled=24, wins=17, hit_rate=0.708333, ROI=0.03619
- `betexplorer`: settled=163, wins=109, hit_rate=0.668712, ROI=-0.050184
- `exact`: settled=283, wins=188, hit_rate=0.664311, ROI=-0.047703
- `fallback`: settled=59, wins=43, hit_rate=0.728814, ROI=0.090169
- `none`: settled=39, wins=29, hit_rate=0.74359, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 163 | 109 | 0.668712 | 163 | -0.050184 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 275 | 181 | 0.658182 | 275 | -0.056982 |
| Source fallback (`SOURCE_FALLBACK`) | 59 | 43 | 0.728814 | 59 | 0.090169 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 24 | 17 | 0.708333 | 21 | 0.03619 |
| No usable price (`UNMATCHED`) | 39 | 29 | 0.74359 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 279 | 185 | 0.663082 | 271 | -0.078487 |
| **trusted evidence only** | 99 | 68 | 0.686869 | 99 | -0.070808 |
| **soft evidence only** | 180 | 117 | 0.65 | 172 | -0.082907 |
| evidence: BETEXPLORER_RESCUE | 94 | 63 | 0.670213 | 94 | -0.096064 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: SCOUTINGSTATS_SOLE | 141 | 87 | 0.617021 | 141 | -0.112979 |
| evidence: SOURCE_FALLBACK | 24 | 19 | 0.791667 | 24 | 0.095417 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.088571 |
| evidence: UNMATCHED | 7 | 5 | 0.714286 | 0 | None |
| odds band: <1.50 | 168 | 128 | 0.761905 | 168 | -0.036012 |
| odds band: 1.50-2.00 | 97 | 47 | 0.484536 | 97 | -0.184227 |
| odds band: 2.00-3.00 | 6 | 4 | 0.666667 | 6 | 0.441667 |
| odds band: unpriced | 8 | 6 | 0.75 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.21 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.4 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.49 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 14 | 10 | 0.714286 | 14 | -0.047857 |
| veto reason: context VETO in ['league'] | 22 | 16 | 0.727273 | 17 | 0.032353 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 62 | 44 | 0.709677 | 62 | -0.085645 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.085 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 8 | 0.727273 | 11 | -0.129091 |
| veto reason: context VETO in ['team_a'] | 45 | 24 | 0.533333 | 44 | -0.173182 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.128571 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.218 |
| veto reason: context VETO in ['team_h', 'team_a'] | 13 | 6 | 0.461538 | 13 | -0.219231 |
| veto reason: context VETO in ['team_h'] | 49 | 31 | 0.632653 | 48 | -0.029583 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 26 | 17 | 0.653846 | 26 | -0.026923 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 18 | 11 | 0.611111 | 18 | -0.015 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 269 | 188 | 0.698885 | 230 | -0.003 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 24 | 17 | 0.708333 | 21 | 0.03619 | 24 | 1.562083 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 275 | 181 | 0.658182 | 275 | -0.056982 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-30: Defensor Sporting vs Plaza Colonia (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🔴 LOST (Expected prob: 56.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 82.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.7% (Actual: 1 goals)

### 2026-09-30: Enyimba vs Shooting Stars (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.56 -> 🟢 WON (Expected prob: 59.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 87.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.0% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.2% (Actual: 6 goals)

### 2026-09-30: Eritrea vs South Africa (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.28 -> 🟢 WON (Expected prob: 74.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.9% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 87.6% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.6% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.1% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.9% (Actual: 5 goals)

### 2026-09-30: Lithuania vs Andorra (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 59.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 3 goals)


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
- 2026-09-30 `SKIPPED_VETO` `ml-meta avg_p>=65` — Cerro Porteno vs Rubio Nu -> HOME @ None (pending_or_unmatched_result); keys=['cerroport']/['rubionu']

## Ambiguous result examples

- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

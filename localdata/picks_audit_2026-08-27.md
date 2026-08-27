# Edge Factory — Recent picks audit (2026-07-29 to 2026-08-27)

## Overall

- archived pick rows: 389
- archived pick dates: 30
- immutable morning-baseline rows: 258
- verified official late-slate additions: 13
- regular-ledger-only legacy rows: 118
- unsafe regular ledgers ignored: 11
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 366
- eligible prior 1x2 picks: 382
- pending/unmatched result picks: 7
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 357
- ambiguous result picks: 0
- wins: 262
- hit rate: +71.6%
- priced picks: 346
- ROI: -0.6%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-27
- same-day rows excluded: 7

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 238 / 366 matches (65.0%)
- **Both Teams to Score (BTTS)**: occurred in 190 / 366 matches (51.9%)
- **Selected Team Over 1.5 Goals**: occurred in 262 / 366 matches (71.6%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 366
- **Total Hits**: 283
- **Overall Hit Rate**: 77.3%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=8, hits=8, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=137, hits=124, hit_rate=90.5%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=10, hits=10, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=151, hits=104, hit_rate=68.9%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2163** | scored: 2163

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 298 | 298 | 194 | 65.1% | 45.9% | +19.2% | 0.266834 |
| `away_under_35` | 283 | 283 | 276 | 97.5% | 98.0% | -0.4% | 0.023086 |
| `away_under_25` | 266 | 266 | 251 | 94.4% | 93.8% | +0.6% | 0.053952 |
| `home_over_05` | 262 | 262 | 241 | 92.0% | 86.9% | +5.0% | 0.076411 |
| `match_over_45` | 249 | 249 | 72 | 28.9% | 24.8% | +4.1% | 0.208813 |
| `away_under_15` | 99 | 99 | 81 | 81.8% | 81.5% | +0.4% | 0.148179 |
| `match_over_35` | 98 | 98 | 38 | 38.8% | 43.0% | -4.2% | 0.244783 |
| `home_under_35` | 79 | 79 | 75 | 94.9% | 94.5% | +0.5% | 0.047572 |
| `exact_4` | 67 | 67 | 17 | 25.4% | 18.0% | +7.3% | 0.196872 |
| `home_under_25` | 65 | 65 | 61 | 93.8% | 91.4% | +2.5% | 0.0595 |
| `goal_range_4_6` | 63 | 63 | 26 | 41.3% | 37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | 33.9% | 30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | 10.5% | 12.6% | -2.1% | 0.096166 |
| `btts_no` | 40 | 40 | 17 | 42.5% | 52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | 50.0% | 50.9% | -0.9% | 0.248905 |
| `exact_3` | 32 | 32 | 4 | 12.5% | 22.2% | -9.7% | 0.119085 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `exact_2` | 24 | 24 | 5 | 20.8% | 24.5% | -3.7% | 0.166543 |
| `away_over_05` | 22 | 22 | 19 | 86.4% | 86.0% | +0.3% | 0.117067 |
| `home_under_15` | 10 | 10 | 9 | 90.0% | 81.1% | +8.9% | 0.097339 |
| `goal_range_6_plus` | 9 | 9 | 1 | 11.1% | 18.7% | -7.6% | 0.102748 |
| `match_over_15` | 8 | 8 | 7 | 87.5% | 85.7% | +1.8% | 0.122786 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | 33.3% | 13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1825 | 1260 | 69.0% | 65.6% | +3.5% | 0.130665 |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| model | 75 | 54 | 72.0% | 53.5% | +18.5% | 0.276534 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 177 | 16.3% | 20.3% | +4.1% |
| 0.2-0.3 | 264 | 25.0% | 27.7% | +2.7% |
| 0.3-0.4 | 228 | 35.5% | 44.7% | +9.2% |
| 0.4-0.5 | 246 | 45.2% | 52.8% | +7.6% |
| 0.5-0.6 | 140 | 53.0% | 56.4% | +3.5% |
| 0.6-0.7 | 10 | 64.2% | 80.0% | +15.8% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 369 | 84.4% | 88.3% | +3.9% |
| 0.9-1.0 | 725 | 95.4% | 95.7% | +0.4% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=364, MAE=1.4925 goals, bias=-0.213874 (realized − promised), promised avg 3.601236 vs realized 3.387363

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 364 | 25.9% | 33.5% | +7.6% | 0.188357 |
| BTTS-Yes | 364 | 41.2% | 52.2% | +10.9% | 0.261771 |
| Home Over 1.5 | 364 | 69.5% | 60.7% | -8.8% | 0.228043 |
| Over 2.5 | 364 | 70.8% | 64.8% | -6.0% | 0.228182 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 243 | 8.8% | 21.0% | +12.2% |
| 0.1-0.2 | 123 | 10.5% | 27.6% | +17.2% |
| 0.2-0.3 | 3 | 20.5% | 0.0% | -20.5% |
| 0.3-0.4 | 98 | 37.6% | 54.1% | +16.4% |
| 0.4-0.5 | 261 | 43.0% | 51.7% | +8.7% |
| 0.6-0.7 | 195 | 66.8% | 59.0% | -7.8% |
| 0.7-0.8 | 154 | 74.7% | 70.1% | -4.6% |
| 0.8-0.9 | 324 | 84.9% | 70.4% | -14.5% |
| 0.9-1.0 | 55 | 91.9% | 81.8% | -10.0% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=109, wins=90, hit_rate=0.825688, ROI=0.08403
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=37, wins=28, hit_rate=0.756757, ROI=0.030405
- `ml-meta avg_p>=55`: settled=145, wins=90, hit_rate=0.62069, ROI=-0.075652
- `ml-meta avg_p>=60`: settled=20, wins=17, hit_rate=0.85, ROI=0.204
- `ml-meta avg_p>=65`: settled=4, wins=3, hit_rate=0.75, ROI=-0.046667
- `ml-meta avg_p>=70`: settled=7, wins=6, hit_rate=0.857143, ROI=0.122857
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06

## By bucket

- `CAUTION`: settled=66, wins=41, hit_rate=0.621212, ROI=-0.022121
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=190, wins=140, hit_rate=0.736842, ROI=0.011937
- `WATCHLIST_NO_ODDS`: settled=19, wins=17, hit_rate=0.894737, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=3, hit_rate=0.6, ROI=-0.0825
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=44, wins=33, hit_rate=0.75, ROI=0.073636
- `WATCHLIST_UNKNOWN_CTX`: settled=21, wins=19, hit_rate=0.904762, ROI=0.106667

## By odds source

- `UNKNOWN`: settled=20, wins=17, hit_rate=0.85, ROI=None
- `betexplorer_odds`: settled=129, wins=95, hit_rate=0.736434, ROI=0.024341
- `bzzoiro_odds`: settled=87, wins=58, hit_rate=0.666667, ROI=-0.038989
- `forebet_best`: settled=19, wins=12, hit_rate=0.631579, ROI=-0.138947
- `scoutingstats_odds`: settled=100, wins=69, hit_rate=0.69, ROI=-0.0284
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=18, wins=12, hit_rate=0.666667, ROI=-0.112353
- `betexplorer`: settled=129, wins=95, hit_rate=0.736434, ROI=0.024341
- `exact`: settled=179, wins=122, hit_rate=0.681564, ROI=-0.024536
- `fallback`: settled=21, wins=16, hit_rate=0.761905, ROI=0.058571
- `none`: settled=19, wins=17, hit_rate=0.894737, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 129 | 95 | 0.736434 | 129 | 0.024341 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 79 | 53 | 0.670886 | 79 | -0.019646 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 100 | 69 | 0.69 | 100 | -0.0284 |
| Source fallback (`SOURCE_FALLBACK`) | 21 | 16 | 0.761905 | 21 | 0.058571 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 18 | 12 | 0.666667 | 17 | -0.112353 |
| No usable price (`UNMATCHED`) | 19 | 17 | 0.894737 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 190 | 140 | 0.736842 | 190 | 0.011937 |
| **trusted evidence only** | 116 | 90 | 0.775862 | 116 | 0.063431 |
| **soft evidence only** | 74 | 50 | 0.675676 | 74 | -0.068784 |
| evidence: BETEXPLORER_RESCUE | 68 | 55 | 0.808824 | 68 | 0.074265 |
| evidence: BZZOIRO_PRIMARY | 48 | 35 | 0.729167 | 48 | 0.048083 |
| evidence: SCOUTINGSTATS_SOLE | 54 | 35 | 0.648148 | 54 | -0.098148 |
| evidence: SOURCE_FALLBACK | 11 | 8 | 0.727273 | 11 | 0.021818 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 9 | -0.003333 |
| odds band: <1.50 | 134 | 108 | 0.80597 | 134 | 0.036104 |
| odds band: 1.50-2.00 | 53 | 30 | 0.566038 | 53 | -0.068302 |
| odds band: 2.00-3.00 | 3 | 2 | 0.666667 | 3 | 0.35 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.3 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.495 |
| veto reason: context VETO in ['league', 'team_a'] | 6 | 3 | 0.5 | 6 | -0.431667 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.48 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 9 | 5 | 0.555556 | 9 | -0.246667 |
| veto reason: context VETO in ['niche'] | 2 | 1 | 0.5 | 2 | -0.14 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: context VETO in ['odds_band'] | 46 | 40 | 0.869565 | 46 | 0.17587 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.183909 |
| veto reason: context VETO in ['team_a'] | 29 | 22 | 0.758621 | 29 | 0.133448 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.222222 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 4 | 2 | 0.5 | 4 | -0.26 |
| veto reason: context VETO in ['team_h', 'team_a'] | 13 | 6 | 0.461538 | 13 | -0.36 |
| veto reason: context VETO in ['team_h'] | 43 | 29 | 0.674419 | 43 | -0.051744 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 37 | 23 | 0.621622 | 37 | 0.001892 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0025 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 6 | 5 | 0.833333 | 6 | 0.236667 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 248 | 181 | 0.729839 | 229 | 0.012306 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 18 | 12 | 0.666667 | 17 | -0.112353 | 10 | 1.3545 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 100 | 69 | 0.69 | 100 | -0.0284 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-26: Real Madrid vs Real Sociedad (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.37 -> 🟢 WON (Expected prob: 71.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.8% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.3% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.2% (Actual: 5 goals)

### 2026-08-26: Lokomotiv Tashkent vs FC Bunyodkor (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.3% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.5% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.8% (Actual: 5 goals)

### 2026-08-26: Newcastle vs West Brom (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 68.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.7% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.5% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.0% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.9% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 81.1% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 26.2% (Actual: 5 goals)

### 2026-08-26: Haugesund vs Egersund (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 56.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.4% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.2% (Actual: 3 goals)

### 2026-08-26: Tottenham vs Charlton Athletic (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.4% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.1% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 30.1% (Actual: 6 goals)

### 2026-08-26: Stabaek vs Ranheim (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.4% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.8% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.3% (Actual: 6 goals)

### 2026-08-26: Stromsgodset vs Hodd (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.29 -> 🟢 WON (Expected prob: 58.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.8% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.7% (Actual: 4 goals)

### 2026-08-26: Richards Bay vs Kaizer Chiefs (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.9 -> 🔴 LOST (Expected prob: 55.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.7% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.0% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 4 goals)

### 2026-08-26: Mamelodi Sundowns vs AmaZulu (Actual Score: **5-2**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 63.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.0% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.1% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 82.6% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.0% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.0% (Actual: 7 goals)


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

## Pending / Unmatched Result Examples

- 2026-08-15 `WATCHLIST_NO_ODDS` `2way-unanimous min_p>=60 avg_p>=65` — Kara-Balta vs Bars -> AWAY @ None (pending_or_unmatched_result); keys=['karabalta', 'kyrgyzalt', 'kyrgyzaltyn']/['bars']
- 2026-08-15 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous min_p>=60 avg_p>=65` — Olympic Kingsway vs Sorrento FC -> HOME @ 1.24 (pending_or_unmatched_result); keys=['olympicki']/['sorrento']
- 2026-08-17 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hamrun Spartans vs Mosta -> HOME @ 1.18 (pending_or_unmatched_result); keys=['hamrunspa']/['mosta']
- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (pending_or_unmatched_result); keys=['charlesto']/['miami', 'miamiii']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']

## Ambiguous result examples

- none

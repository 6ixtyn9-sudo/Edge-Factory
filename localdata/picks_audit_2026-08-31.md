# Edge Factory — Recent picks audit (2026-08-02 to 2026-08-31)

## Overall

- archived pick rows: 477
- archived pick dates: 30
- immutable morning-baseline rows: 349
- verified official late-slate additions: 13
- regular-ledger-only legacy rows: 115
- unsafe regular ledgers ignored: 13
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 443
- eligible prior 1x2 picks: 461
- pending/unmatched result picks: 8
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 1
- wins: 307
- hit rate: +69.3%
- priced picks: 416
- ROI: -1.6%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-31
- same-day rows excluded: 16

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 285 / 443 matches (64.3%)
- **Both Teams to Score (BTTS)**: occurred in 240 / 443 matches (54.2%)
- **Selected Team Over 1.5 Goals**: occurred in 312 / 443 matches (70.4%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 443
- **Total Hits**: 331
- **Overall Hit Rate**: 74.7%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=4, hits=4, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=8, hits=2, hit_rate=25.0%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=140, hits=127, hit_rate=90.7%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=11, hits=11, hit_rate=100.0%
- `match_over_15`: recommended=6, hits=5, hit_rate=83.3%
- `match_over_25`: recommended=232, hits=155, hit_rate=66.8%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2478** | scored: 2478

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 383 | 383 | 248 | 64.8% | 46.5% | +18.2% | 0.262505 |
| `away_under_35` | 339 | 339 | 331 | 97.6% | 98.0% | -0.4% | 0.022421 |
| `away_under_25` | 324 | 324 | 304 | 93.8% | 94.1% | -0.3% | 0.058625 |
| `home_over_05` | 322 | 322 | 294 | 91.3% | 86.5% | +4.8% | 0.081395 |
| `match_over_45` | 321 | 321 | 87 | 27.1% | 24.6% | +2.5% | 0.199122 |
| `away_under_15` | 121 | 121 | 98 | 81.0% | 81.4% | -0.4% | 0.153833 |
| `home_under_35` | 97 | 97 | 95 | 97.9% | 95.3% | +2.7% | 0.020911 |
| `match_over_35` | 90 | 90 | 33 | 36.7% | 43.7% | -7.0% | 0.235359 |
| `home_under_25` | 84 | 84 | 78 | 92.9% | 91.8% | +1.0% | 0.067116 |
| `exact_4` | 58 | 58 | 14 | 24.1% | 18.3% | +5.8% | 0.187777 |
| `goal_range_4_5` | 56 | 56 | 18 | 32.1% | 31.0% | +1.2% | 0.219886 |
| `goal_range_4_6` | 56 | 56 | 23 | 41.1% | 38.1% | +3.0% | 0.247453 |
| `exact_5` | 55 | 55 | 5 | 9.1% | 12.6% | -3.5% | 0.08465 |
| `btts_no` | 38 | 38 | 16 | 42.1% | 52.7% | -10.6% | 0.251721 |
| `btts_yes` | 29 | 29 | 15 | 51.7% | 50.1% | +1.6% | 0.252892 |
| `exact_3` | 24 | 24 | 4 | 16.7% | 22.2% | -5.5% | 0.142245 |
| `away_over_05` | 22 | 22 | 19 | 86.4% | 85.9% | +0.4% | 0.117477 |
| `goal_range_2_3` | 13 | 13 | 4 | 30.8% | 46.1% | -15.3% | 0.231979 |
| `exact_2` | 12 | 12 | 2 | 16.7% | 24.7% | -8.1% | 0.14457 |
| `home_under_15` | 12 | 12 | 11 | 91.7% | 81.2% | +10.5% | 0.08671 |
| `goal_range_6_plus` | 8 | 8 | 1 | 12.5% | 18.2% | -5.7% | 0.109142 |
| `match_over_15` | 6 | 6 | 5 | 83.3% | 85.1% | -1.8% | 0.157276 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 2 | 2 | 1 | 50.0% | 14.4% | +35.6% | 0.416909 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2260 | 1580 | 69.9% | 66.7% | +3.2% | 0.130471 |
| legacy | 136 | 68 | 50.0% | 51.3% | -1.3% | 0.166437 |
| model | 82 | 60 | 73.2% | 54.8% | +18.4% | 0.261122 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 183 | 16.6% | 18.6% | +2.0% |
| 0.2-0.3 | 286 | 25.0% | 27.6% | +2.6% |
| 0.3-0.4 | 223 | 35.5% | 43.0% | +7.5% |
| 0.4-0.5 | 290 | 45.6% | 55.9% | +10.3% |
| 0.5-0.6 | 157 | 53.0% | 59.2% | +6.2% |
| 0.6-0.7 | 10 | 64.2% | 80.0% | +15.8% |
| 0.7-0.8 | 2 | 74.1% | 50.0% | -24.1% |
| 0.8-0.9 | 446 | 84.3% | 87.9% | +3.6% |
| 0.9-1.0 | 881 | 95.5% | 95.7% | +0.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=442, MAE=1.52 goals, bias=-0.213982 (realized − promised), promised avg 3.575973 vs realized 3.361991

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 442 | 26.3% | 35.5% | +9.2% | 0.203318 |
| BTTS-Yes | 442 | 41.4% | 54.3% | +12.9% | 0.26611 |
| Home Over 1.5 | 442 | 68.9% | 59.5% | -9.4% | 0.235333 |
| Over 2.5 | 442 | 70.5% | 64.3% | -6.2% | 0.230874 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 286 | 8.9% | 22.7% | +13.9% |
| 0.1-0.2 | 158 | 10.5% | 29.1% | +18.7% |
| 0.2-0.3 | 4 | 21.2% | 25.0% | +3.8% |
| 0.3-0.4 | 109 | 37.6% | 56.9% | +19.3% |
| 0.4-0.5 | 327 | 43.0% | 53.5% | +10.5% |
| 0.6-0.7 | 253 | 66.8% | 60.1% | -6.7% |
| 0.7-0.8 | 174 | 74.7% | 68.4% | -6.4% |
| 0.8-0.9 | 398 | 84.8% | 69.6% | -15.2% |
| 0.9-1.0 | 59 | 91.8% | 79.7% | -12.1% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=128, wins=100, hit_rate=0.78125, ROI=0.063362
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=26, wins=20, hit_rate=0.769231, ROI=0.07
- `ml-meta avg_p>=55`: settled=204, wins=126, hit_rate=0.617647, ROI=-0.073144
- `ml-meta avg_p>=60`: settled=25, wins=20, hit_rate=0.8, ROI=0.132
- `ml-meta avg_p>=65`: settled=5, wins=4, hit_rate=0.8, ROI=0.035
- `ml-meta avg_p>=70`: settled=9, wins=8, hit_rate=0.888889, ROI=0.182222
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06

## By bucket

- `CAUTION`: settled=74, wins=47, hit_rate=0.635135, ROI=-0.01527
- `CERTIFIED_CLEAN`: settled=29, wins=15, hit_rate=0.517241, ROI=-0.246897
- `SKIPPED_VETO`: settled=227, wins=163, hit_rate=0.718062, ROI=0.002965
- `WATCHLIST_NO_ODDS`: settled=25, wins=19, hit_rate=0.76, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=6, wins=4, hit_rate=0.666667, ROI=0.01
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=64, wins=43, hit_rate=0.671875, ROI=-0.012188
- `WATCHLIST_UNKNOWN_CTX`: settled=18, wins=16, hit_rate=0.888889, ROI=0.088333

## By odds source

- `UNKNOWN`: settled=27, wins=19, hit_rate=0.703704, ROI=None
- `betexplorer_odds`: settled=153, wins=108, hit_rate=0.705882, ROI=-0.014706
- `bzzoiro_odds`: settled=78, wins=50, hit_rate=0.641026, ROI=-0.053205
- `forebet_best`: settled=25, wins=18, hit_rate=0.72, ROI=-0.0
- `scoutingstats_odds`: settled=149, wins=101, hit_rate=0.677852, ROI=-0.027919
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=17, wins=12, hit_rate=0.705882, ROI=-0.00875
- `betexplorer`: settled=153, wins=108, hit_rate=0.705882, ROI=-0.014706
- `exact`: settled=223, wins=149, hit_rate=0.668161, ROI=-0.030897
- `fallback`: settled=24, wins=19, hit_rate=0.791667, ROI=0.105
- `none`: settled=26, wins=19, hit_rate=0.730769, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 153 | 108 | 0.705882 | 153 | -0.014706 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 74 | 48 | 0.648649 | 74 | -0.036892 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 149 | 101 | 0.677852 | 149 | -0.027919 |
| Source fallback (`SOURCE_FALLBACK`) | 24 | 19 | 0.791667 | 24 | 0.105 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 17 | 12 | 0.705882 | 16 | -0.00875 |
| No usable price (`UNMATCHED`) | 26 | 19 | 0.730769 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 227 | 163 | 0.718062 | 226 | 0.002965 |
| **trusted evidence only** | 122 | 89 | 0.729508 | 122 | 0.008197 |
| **soft evidence only** | 105 | 74 | 0.704762 | 104 | -0.003173 |
| evidence: BETEXPLORER_RESCUE | 79 | 59 | 0.746835 | 79 | -0.001646 |
| evidence: BZZOIRO_PRIMARY | 43 | 30 | 0.697674 | 43 | 0.026279 |
| evidence: SCOUTINGSTATS_SOLE | 84 | 58 | 0.690476 | 84 | -0.028333 |
| evidence: SOURCE_FALLBACK | 11 | 8 | 0.727273 | 11 | 0.021818 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 8 | 0.888889 | 9 | 0.201111 |
| evidence: UNMATCHED | 1 | 0 | 0.0 | 0 | None |
| odds band: <1.50 | 153 | 121 | 0.79085 | 153 | 0.022418 |
| odds band: 1.50-2.00 | 68 | 39 | 0.573529 | 68 | -0.058971 |
| odds band: 2.00-3.00 | 5 | 3 | 0.6 | 5 | 0.25 |
| odds band: unpriced | 1 | 0 | 0.0 | 0 | None |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.05 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.66 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 9 | 5 | 0.555556 | 8 | -0.09 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 52 | 43 | 0.826923 | 52 | 0.102692 |
| veto reason: context VETO in ['team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 9 | 0.818182 | 11 | 0.055455 |
| veto reason: context VETO in ['team_a'] | 35 | 26 | 0.742857 | 35 | 0.122857 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 14 | 12 | 0.857143 | 14 | 0.18 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.055 |
| veto reason: context VETO in ['team_h', 'team_a'] | 16 | 8 | 0.5 | 16 | -0.26875 |
| veto reason: context VETO in ['team_h'] | 52 | 33 | 0.634615 | 52 | -0.0825 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 44 | 28 | 0.636364 | 44 | -0.005455 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0025 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 7 | 6 | 0.857143 | 7 | 0.294286 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 277 | 194 | 0.700361 | 251 | -0.009801 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 17 | 12 | 0.705882 | 16 | -0.00875 | 13 | 1.376538 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 149 | 101 | 0.677852 | 149 | -0.027919 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-30: Viking vs Aalesund (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 81.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.8% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.2% (Actual: 3 goals)

### 2026-08-30: Union Omaha vs New York Cosmos (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🔴 LOST (Expected prob: 73.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 57.5% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.1% (Actual: 2 goals)

### 2026-08-30: Houston Dynamo vs San Jose Earthquakes (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 62.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.8% (Actual: 0 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 84.3% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.8% (Actual: 0 goals)

### 2026-08-30: Sporting Kansas City vs Vancouver Whitecaps (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.4 -> 🟢 WON (Expected prob: 61.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.7% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.8% (Actual: 3 goals)

### 2026-08-30: Trelleborgs FF vs Utsiktens BK (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🟢 WON (Expected prob: 76.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 55.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.4% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.7% (Actual: 3 goals)

### 2026-08-30: Swit Skolwin vs GKS Tychy (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.61 -> 🔴 LOST (Expected prob: 55.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.2% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 2 goals)

### 2026-08-30: Real Madrid vs Malaga (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.09 -> 🟢 WON (Expected prob: 77.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.5% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.8% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.4% (Actual: 4 goals)

### 2026-08-30: CSKA-Sofia vs Cherno More Varna (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.6% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.3% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.8% (Actual: 4 goals)

### 2026-08-30: FC Eindhoven vs Heracles (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.65 -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 32.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.2% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.7% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.1% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.4% (Actual: 4 goals)

### 2026-08-30: Argentinos Juniors vs CA Aldosivi (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.2% (Actual: 3 goals)

### 2026-08-30: Tasmania Berlin vs Greifswalder (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 95.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.7% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.3% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.9% (Actual: 4 goals)

### 2026-08-30: Gwangju FC vs FC Seoul (Actual Score: **2-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.5 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 31.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 92.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.8% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 94.0% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.9% (Actual: 7 goals)

### 2026-08-30: Slovan Bratislava vs Zemplin Michalovce (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🔴 LOST (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.1% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.7% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.9% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 81.0% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.8% (Actual: 3 goals)

### 2026-08-30: Utrecht vs PSV Eindhoven (Actual Score: **1-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.63 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.8% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 36.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.7% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.1% (Actual: 6 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.8% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.0% (Actual: 7 goals)

### 2026-08-30: Fram Reykjavik vs KA Akureyri (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 62.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.3% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.4% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.8% (Actual: 4 goals)

### 2026-08-30: Real Mallorca vs AD Ceuta (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.2% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.9% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.6% (Actual: 3 goals)

### 2026-08-30: Arka Gdynia vs Polonia Bytom (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🔴 LOST (Expected prob: 60.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.7% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 2 goals)

### 2026-08-30: Bodo/Glimt vs Rosenborg BK (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 57.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.1% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.5% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.5% (Actual: 2 away goals)

### 2026-08-30: Karmiotissa vs Pafos (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.2 -> 🟢 WON (Expected prob: 55.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.8% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 3 goals)

### 2026-08-30: St Gallen vs FC Thun (Actual Score: **3-4**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🔴 LOST (Expected prob: 57.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.0% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.8% (Actual: 3 home goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 97.7% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 4 away goals)

### 2026-08-30: FC Nizhny Novgorod vs Volga Ulyanovsk (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.0% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.0% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 81.2% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.8% (Actual: 4 goals)

### 2026-08-30: FC Sochi vs FC Chelyabinsk (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 55.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.3% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.7% (Actual: 3 goals)

### 2026-08-30: Feyenoord vs ADO Den Haag (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🔴 LOST (Expected prob: 76.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.2% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.8% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.9% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.9% (Actual: 4 goals)

### 2026-08-30: FCSB vs UTA Arad (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🔴 LOST (Expected prob: 64.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.7% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 95.9% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 82.1% (Actual: 3 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.1% (Actual: 4 goals)

### 2026-08-30: Tromso vs Sarpsborg 08 (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🔴 LOST (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.0% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.6% (Actual: 0 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 82.5% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.3% (Actual: 0 goals)

### 2026-08-30: Club America vs Puebla (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 64.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.2% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 82.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 2 goals)

### 2026-08-30: Portland Timbers vs Austin FC (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🔴 LOST (Expected prob: 58.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.6% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.0% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 2 away goals)

### 2026-08-30: Egersund vs Asane (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🔴 LOST (Expected prob: 57.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.5% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.8% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.5% (Actual: 2 away goals)

### 2026-08-30: Cagliari vs Inter (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.42 -> 🟢 WON (Expected prob: 55.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.9% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.1% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.9% (Actual: 1 goals)

### 2026-08-30: Denver Summit Fc (w) vs Chicago Red Stars (w) (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.4% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.1% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 55.0% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.1% (Actual: 6 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 30.5% (Actual: 7 goals)


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

- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (pending_or_unmatched_result); keys=['charlesto']/['miami', 'miamiii']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-08-29 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hønefoss W vs Fortuna Ålesund W -> AWAY @ 1.2 (pending_or_unmatched_result); keys=['hnefoss', 'honefossw']/['fortunale', 'fortunaal']
- 2026-08-29 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — LSK Kvinner W vs Bodø / Glimt W -> HOME @ None (pending_or_unmatched_result); keys=['lskkvinne']/['bodglimt', 'bodoglimt']
- 2026-08-29 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Viking vs Aalesund -> HOME @ 1.3 (pending_or_unmatched_result); keys=['viking', 'vikingfk']/['aalesund', 'aalesundf']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)

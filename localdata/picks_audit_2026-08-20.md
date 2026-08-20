# Edge Factory — Recent picks audit (2026-07-22 to 2026-08-20)

## Overall

- archived pick rows: 301
- archived pick dates: 30
- immutable morning-baseline rows: 157
- verified official late-slate additions: 26
- regular-ledger-only legacy rows: 118
- unsafe regular ledgers ignored: 5
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 282
- eligible prior 1x2 picks: 292
- pending/unmatched result picks: 8
- voided postponed/cancelled/abandoned events: 2
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 5
- ambiguous result picks: 0
- wins: 199
- hit rate: +70.6%
- priced picks: 264
- ROI: -1.4%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-20
- same-day rows excluded: 9

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 184 / 282 matches (65.2%)
- **Both Teams to Score (BTTS)**: occurred in 153 / 282 matches (54.3%)
- **Selected Team Over 1.5 Goals**: occurred in 198 / 282 matches (70.2%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 250
- **Total Hits**: 203
- **Overall Hit Rate**: 81.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=121, hits=111, hit_rate=91.7%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=9, hits=9, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=52, hits=38, hit_rate=73.1%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1635** | scored: 1635

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 200 | 200 | 197 | 98.5% | 97.8% | +0.7% | 0.014336 |
| `away_under_25` | 187 | 187 | 175 | 93.6% | 93.7% | -0.1% | 0.061013 |
| `home_over_05` | 182 | 182 | 170 | 93.4% | 87.6% | +5.8% | 0.066484 |
| `match_over_25` | 181 | 181 | 116 | 64.1% | 43.1% | +21.0% | 0.278505 |
| `match_over_45` | 165 | 165 | 43 | 26.1% | 25.1% | +1.0% | 0.196481 |
| `match_over_35` | 98 | 98 | 38 | 38.8% | 43.0% | -4.2% | 0.244783 |
| `away_under_15` | 76 | 76 | 62 | 81.6% | 81.6% | -0.0% | 0.149114 |
| `exact_4` | 67 | 67 | 17 | 25.4% | 18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | 41.3% | 37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | 33.9% | 30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | 10.5% | 12.6% | -2.1% | 0.096166 |
| `home_under_35` | 48 | 48 | 44 | 91.7% | 94.3% | -2.7% | 0.076232 |
| `btts_no` | 40 | 40 | 17 | 42.5% | 52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | 50.0% | 50.9% | -0.9% | 0.248905 |
| `home_under_25` | 36 | 36 | 33 | 91.7% | 91.3% | +0.3% | 0.077319 |
| `exact_3` | 32 | 32 | 4 | 12.5% | 22.2% | -9.7% | 0.119085 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `exact_2` | 24 | 24 | 5 | 20.8% | 24.5% | -3.7% | 0.166543 |
| `away_over_05` | 22 | 22 | 19 | 86.4% | 86.0% | +0.3% | 0.117067 |
| `goal_range_6_plus` | 9 | 9 | 1 | 11.1% | 18.7% | -7.6% | 0.102748 |
| `home_under_15` | 8 | 8 | 7 | 87.5% | 81.2% | +6.3% | 0.112258 |
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
| hybrid_cohort | 1322 | 865 | 65.4% | 62.9% | +2.5% | 0.134867 |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| model | 50 | 36 | 72.0% | 50.5% | +21.5% | 0.262086 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 154 | 15.9% | 20.1% | +4.2% |
| 0.2-0.3 | 210 | 24.8% | 24.3% | -0.5% |
| 0.3-0.4 | 221 | 35.6% | 45.2% | +9.6% |
| 0.4-0.5 | 180 | 44.7% | 50.0% | +5.3% |
| 0.5-0.6 | 94 | 52.6% | 46.8% | -5.7% |
| 0.6-0.7 | 5 | 65.3% | 100.0% | +34.7% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 258 | 84.4% | 88.4% | +4.0% |
| 0.9-1.0 | 509 | 95.3% | 95.5% | +0.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=249, MAE=1.448193 goals, bias=-0.34257 (realized − promised), promised avg 3.627711 vs realized 3.285141

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 249 | 22.9% | 30.1% | +7.2% | 0.197745 |
| BTTS-Yes | 249 | 41.4% | 54.2% | +12.8% | 0.2651 |
| Home Over 1.5 | 249 | 72.7% | 61.0% | -11.7% | 0.219049 |
| Over 2.5 | 249 | 71.2% | 64.3% | -6.9% | 0.232389 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 177 | 8.9% | 19.2% | +10.3% |
| 0.1-0.2 | 73 | 10.4% | 27.4% | +17.0% |
| 0.3-0.4 | 66 | 37.8% | 54.5% | +16.7% |
| 0.4-0.5 | 182 | 42.8% | 53.8% | +11.0% |
| 0.6-0.7 | 125 | 66.9% | 58.4% | -8.5% |
| 0.7-0.8 | 114 | 74.7% | 69.3% | -5.4% |
| 0.8-0.9 | 216 | 85.1% | 68.5% | -16.6% |
| 0.9-1.0 | 43 | 92.0% | 79.1% | -12.9% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=100, wins=80, hit_rate=0.8, ROI=0.078055
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=51, wins=37, hit_rate=0.72549, ROI=-0.0183
- `ml-meta avg_p>=55`: settled=81, wins=49, hit_rate=0.604938, ROI=-0.066364
- `ml-meta avg_p>=60`: settled=5, wins=4, hit_rate=0.8, ROI=0.078
- `ml-meta avg_p>=65`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.25
- `ml-meta avg_p>=70`: settled=1, wins=1, hit_rate=1.0, ROI=0.42
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.16

## By bucket

- `CAUTION`: settled=63, wins=36, hit_rate=0.571429, ROI=-0.090952
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=137, wins=104, hit_rate=0.759124, ROI=0.046993
- `WATCHLIST_NO_ODDS`: settled=17, wins=15, hit_rate=0.882353, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=4, wins=2, hit_rate=0.5, ROI=-0.156667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=22, wins=17, hit_rate=0.772727, ROI=0.115909
- `WATCHLIST_UNKNOWN_CTX`: settled=18, wins=16, hit_rate=0.888889, ROI=0.081111

## By odds source

- `UNKNOWN`: settled=18, wins=15, hit_rate=0.833333, ROI=None
- `betexplorer_odds`: settled=99, wins=73, hit_rate=0.737374, ROI=0.04404
- `bzzoiro_odds`: settled=89, wins=58, hit_rate=0.651685, ROI=-0.056989
- `forebet_best`: settled=9, wins=6, hit_rate=0.666667, ROI=-0.095556
- `scoutingstats_odds`: settled=56, wins=36, hit_rate=0.642857, ROI=-0.104821
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=16, wins=11, hit_rate=0.6875, ROI=-0.07
- `betexplorer`: settled=99, wins=73, hit_rate=0.737374, ROI=0.04404
- `exact`: settled=137, wins=89, hit_rate=0.649635, ROI=-0.066438
- `fallback`: settled=13, wins=11, hit_rate=0.846154, ROI=0.165385
- `none`: settled=17, wins=15, hit_rate=0.882353, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 99 | 73 | 0.737374 | 99 | 0.04404 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 81 | 53 | 0.654321 | 81 | -0.039901 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 56 | 36 | 0.642857 | 56 | -0.104821 |
| Source fallback (`SOURCE_FALLBACK`) | 13 | 11 | 0.846154 | 13 | 0.165385 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 16 | 11 | 0.6875 | 15 | -0.07 |
| No usable price (`UNMATCHED`) | 17 | 15 | 0.882353 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 137 | 104 | 0.759124 | 137 | 0.046993 |
| **trusted evidence only** | 98 | 75 | 0.765306 | 98 | 0.065388 |
| **soft evidence only** | 39 | 29 | 0.74359 | 39 | 0.000769 |
| evidence: BETEXPLORER_RESCUE | 48 | 40 | 0.833333 | 48 | 0.1375 |
| evidence: BZZOIRO_PRIMARY | 50 | 35 | 0.7 | 50 | -0.00384 |
| evidence: SCOUTINGSTATS_SOLE | 24 | 15 | 0.625 | 24 | -0.1575 |
| evidence: SOURCE_FALLBACK | 7 | 7 | 1.0 | 7 | 0.405714 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 7 | 0.875 | 8 | 0.12125 |
| odds band: <1.50 | 102 | 82 | 0.803922 | 102 | 0.04449 |
| odds band: 1.50-2.00 | 34 | 21 | 0.617647 | 34 | 0.026471 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.0 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.305 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 5 | 4 | 0.8 | 5 | 0.07 |
| veto reason: context VETO in ['odds_band'] | 40 | 33 | 0.825 | 40 | 0.12275 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.169125 |
| veto reason: context VETO in ['team_a'] | 23 | 17 | 0.73913 | 23 | 0.07913 |
| veto reason: context VETO in ['team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.35 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.2275 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.013333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 9 | 4 | 0.444444 | 9 | -0.397778 |
| veto reason: context VETO in ['team_h'] | 29 | 20 | 0.689655 | 29 | -0.020172 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| contrast CAUTION: BETEXPLORER_RESCUE | 31 | 20 | 0.645161 | 31 | 0.023871 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0435 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 7 | 1 | 0.142857 | 7 | -0.757143 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 210 | 152 | 0.72381 | 193 | 0.016984 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 16 | 11 | 0.6875 | 15 | -0.07 | 8 | 1.359375 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 56 | 36 | 0.642857 | 56 | -0.104821 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-19: Persepolis FC vs Esteghlal Khuzestan (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 74.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.1% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.3% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.5% (Actual: 5 goals)

### 2026-08-19: Vila Nova vs Ponte Preta (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 64.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.4% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.0% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.3% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.5% (Actual: 6 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.7% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.2% (Actual: 6 goals)

### 2026-08-19: Sao Paulo vs Bolívar (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.9% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.3% (Actual: 4 goals)

### 2026-08-19: Celtic vs Lask Linz (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 55.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 46.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.8% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.3% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.3% (Actual: 0 away goals)

### 2026-08-19: Barcelona vs Al Ahly Cairo (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 85.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 94.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 100.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 94.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.0% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 1 away goals)

### 2026-08-19: Atletico Madrid vs Malaga (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 60.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.8% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.1% (Actual: 2 goals)

### 2026-08-19: Deportes Tolima vs Independiente Del Valle (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.45 -> 🟢 WON (Expected prob: 55.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.6% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.1% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.2% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.5% (Actual: 0 home goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 2 |
- 2026-07-25 `POSTPONED` `WATCHLIST_NO_ODDS` — Coquimbo Unido vs Universidad de Concepcion (verified_disposition); excluded from win/loss/ROI
- 2026-07-26 `POSTPONED` `SKIPPED_VETO` — Super Nova vs Riga (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- 2026-08-08 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Belshina vs Dinamo Minsk -> AWAY @ 1.32 (pending_or_unmatched_result); keys=['belshina', 'belshinab']/['dinamomin']
- 2026-08-11 `WATCHLIST_UNCORROBORATED_PRICE` `2way+bc-confirms avg_p>=60` — Junior vs Pereira -> HOME @ 1.33 (pending_or_unmatched_result); keys=['junior']/['pereira']
- 2026-08-15 `SKIPPED_VETO` `2way-unanimous min_p>=60 avg_p>=65` — Slavia Sofia vs Levski Sofia -> AWAY @ 1.36 (pending_or_unmatched_result); keys=['slaviasof']/['levskisof']
- 2026-08-15 `WATCHLIST_NO_ODDS` `2way-unanimous min_p>=60 avg_p>=65` — Kara-Balta vs Bars -> AWAY @ None (pending_or_unmatched_result); keys=['karabalta']/['bars']
- 2026-08-15 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous min_p>=60 avg_p>=65` — Olympic Kingsway vs Sorrento FC -> HOME @ 1.24 (pending_or_unmatched_result); keys=['olympicki']/['sorrento']
- 2026-08-16 `SKIPPED_VETO` `ml-meta avg_p>=55` — SC Braga vs Gil Vicente -> HOME @ 1.7 (pending_or_unmatched_result); keys=['braga']/['gilvicent']
- 2026-08-17 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hamrun Spartans vs Mosta -> HOME @ 1.18 (pending_or_unmatched_result); keys=['hamrunspa']/['mosta']
- 2026-08-17 `SKIPPED_VETO` `ml-meta avg_p>=55` — Bucaramanga vs Deportivo Pasto -> HOME @ 1.61 (pending_or_unmatched_result); keys=['bucaraman']/['pasto']

## Ambiguous result examples

- none

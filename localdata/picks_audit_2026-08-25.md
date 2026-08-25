# Edge Factory — Recent picks audit (2026-07-27 to 2026-08-25)

## Overall

- archived pick rows: 380
- archived pick dates: 30
- immutable morning-baseline rows: 246
- verified official late-slate additions: 16
- regular-ledger-only legacy rows: 118
- unsafe regular ledgers ignored: 10
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 359
- eligible prior 1x2 picks: 375
- pending/unmatched result picks: 7
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 7
- ambiguous result picks: 0
- wins: 258
- hit rate: +71.9%
- priced picks: 340
- ROI: +0.0%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-25
- same-day rows excluded: 5

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 229 / 359 matches (63.8%)
- **Both Teams to Score (BTTS)**: occurred in 180 / 359 matches (50.1%)
- **Selected Team Over 1.5 Goals**: occurred in 254 / 359 matches (70.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 353
- **Total Hits**: 270
- **Overall Hit Rate**: 76.5%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=131, hits=118, hit_rate=90.1%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=9, hits=9, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=145, hits=98, hit_rate=67.6%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2096** | scored: 2096

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 284 | 284 | 181 | 63.7% | 45.8% | +17.9% | 0.2666 |
| `away_under_35` | 271 | 271 | 265 | 97.8% | 97.9% | -0.2% | 0.020533 |
| `away_under_25` | 254 | 254 | 240 | 94.5% | 93.7% | +0.7% | 0.052915 |
| `home_over_05` | 251 | 251 | 230 | 91.6% | 87.0% | +4.6% | 0.078728 |
| `match_over_45` | 239 | 239 | 67 | 28.0% | 24.8% | +3.2% | 0.20474 |
| `match_over_35` | 98 | 98 | 38 | 38.8% | 43.0% | -4.2% | 0.244783 |
| `away_under_15` | 95 | 95 | 79 | 83.2% | 81.5% | +1.7% | 0.139511 |
| `home_under_35` | 77 | 77 | 73 | 94.8% | 94.4% | +0.4% | 0.048791 |
| `exact_4` | 67 | 67 | 17 | 25.4% | 18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | 41.3% | 37.4% | +3.8% | 0.250203 |
| `home_under_25` | 63 | 63 | 58 | 92.1% | 91.3% | +0.7% | 0.074651 |
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
| hybrid_cohort | 1758 | 1202 | 68.4% | 65.3% | +3.1% | 0.130193 |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| model | 75 | 54 | 72.0% | 53.5% | +18.5% | 0.276534 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 173 | 16.2% | 19.7% | +3.4% |
| 0.2-0.3 | 259 | 24.9% | 27.4% | +2.5% |
| 0.3-0.4 | 227 | 35.5% | 44.5% | +9.0% |
| 0.4-0.5 | 237 | 45.3% | 51.5% | +6.2% |
| 0.5-0.6 | 135 | 53.0% | 54.8% | +1.8% |
| 0.6-0.7 | 10 | 64.2% | 80.0% | +15.8% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 354 | 84.5% | 88.4% | +4.0% |
| 0.9-1.0 | 697 | 95.3% | 95.7% | +0.4% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=351, MAE=1.503704 goals, bias=-0.254986 (realized − promised), promised avg 3.605413 vs realized 3.350427

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 351 | 26.1% | 33.0% | +7.0% | 0.185775 |
| BTTS-Yes | 351 | 41.2% | 51.3% | +10.1% | 0.259935 |
| Home Over 1.5 | 351 | 69.3% | 59.5% | -9.8% | 0.229084 |
| Over 2.5 | 351 | 70.9% | 63.8% | -7.1% | 0.232195 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 238 | 8.8% | 20.2% | +11.3% |
| 0.1-0.2 | 115 | 10.5% | 27.0% | +16.5% |
| 0.2-0.3 | 3 | 20.5% | 0.0% | -20.5% |
| 0.3-0.4 | 94 | 37.6% | 52.1% | +14.5% |
| 0.4-0.5 | 252 | 43.0% | 51.2% | +8.2% |
| 0.6-0.7 | 188 | 66.8% | 58.0% | -8.9% |
| 0.7-0.8 | 148 | 74.7% | 68.9% | -5.8% |
| 0.8-0.9 | 312 | 84.9% | 69.6% | -15.4% |
| 0.9-1.0 | 54 | 91.9% | 81.5% | -10.4% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=110, wins=91, hit_rate=0.827273, ROI=0.083693
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=40, wins=31, hit_rate=0.775, ROI=0.067875
- `ml-meta avg_p>=55`: settled=136, wins=84, hit_rate=0.617647, ROI=-0.072077
- `ml-meta avg_p>=60`: settled=19, wins=16, hit_rate=0.842105, ROI=0.201579
- `ml-meta avg_p>=65`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.25
- `ml-meta avg_p>=70`: settled=7, wins=6, hit_rate=0.857143, ROI=0.122857
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06

## By bucket

- `CAUTION`: settled=64, wins=39, hit_rate=0.609375, ROI=-0.032344
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=189, wins=141, hit_rate=0.746032, ROI=0.023693
- `WATCHLIST_NO_ODDS`: settled=18, wins=16, hit_rate=0.888889, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=3, hit_rate=0.6, ROI=-0.0825
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=41, wins=31, hit_rate=0.756098, ROI=0.09122
- `WATCHLIST_UNKNOWN_CTX`: settled=21, wins=19, hit_rate=0.904762, ROI=0.106667

## By odds source

- `UNKNOWN`: settled=19, wins=16, hit_rate=0.842105, ROI=None
- `betexplorer_odds`: settled=128, wins=95, hit_rate=0.742188, ROI=0.029922
- `bzzoiro_odds`: settled=87, wins=58, hit_rate=0.666667, ROI=-0.031632
- `forebet_best`: settled=19, wins=12, hit_rate=0.631579, ROI=-0.155263
- `scoutingstats_odds`: settled=95, wins=66, hit_rate=0.694737, ROI=-0.018526
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=18, wins=12, hit_rate=0.666667, ROI=-0.112353
- `betexplorer`: settled=128, wins=95, hit_rate=0.742188, ROI=0.029922
- `exact`: settled=174, wins=119, hit_rate=0.683908, ROI=-0.015356
- `fallback`: settled=21, wins=16, hit_rate=0.761905, ROI=0.04381
- `none`: settled=18, wins=16, hit_rate=0.888889, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 128 | 95 | 0.742188 | 128 | 0.029922 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 79 | 53 | 0.670886 | 79 | -0.011544 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 95 | 66 | 0.694737 | 95 | -0.018526 |
| Source fallback (`SOURCE_FALLBACK`) | 21 | 16 | 0.761905 | 21 | 0.04381 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 18 | 12 | 0.666667 | 17 | -0.112353 |
| No usable price (`UNMATCHED`) | 18 | 16 | 0.888889 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 189 | 141 | 0.746032 | 189 | 0.023693 |
| **trusted evidence only** | 116 | 91 | 0.784483 | 116 | 0.075586 |
| **soft evidence only** | 73 | 50 | 0.684932 | 73 | -0.058767 |
| evidence: BETEXPLORER_RESCUE | 68 | 56 | 0.823529 | 68 | 0.092941 |
| evidence: BZZOIRO_PRIMARY | 48 | 35 | 0.729167 | 48 | 0.051 |
| evidence: SCOUTINGSTATS_SOLE | 52 | 34 | 0.653846 | 52 | -0.090769 |
| evidence: SOURCE_FALLBACK | 12 | 9 | 0.75 | 12 | 0.038333 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 9 | -0.003333 |
| odds band: <1.50 | 134 | 109 | 0.813433 | 134 | 0.045134 |
| odds band: 1.50-2.00 | 52 | 30 | 0.576923 | 52 | -0.050385 |
| odds band: 2.00-3.00 | 3 | 2 | 0.666667 | 3 | 0.35 |
| veto reason: context VETO in ['league', 'odds_band'] | 4 | 3 | 0.75 | 4 | -0.1275 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.495 |
| veto reason: context VETO in ['league', 'team_a'] | 7 | 4 | 0.571429 | 7 | -0.322857 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.48 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 9 | 6 | 0.666667 | 9 | -0.095556 |
| veto reason: context VETO in ['niche'] | 2 | 1 | 0.5 | 2 | -0.14 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: context VETO in ['odds_band'] | 44 | 38 | 0.863636 | 44 | 0.163636 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.183909 |
| veto reason: context VETO in ['team_a'] | 29 | 22 | 0.758621 | 29 | 0.133448 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.2125 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 4 | 2 | 0.5 | 4 | -0.26 |
| veto reason: context VETO in ['team_h', 'team_a'] | 13 | 6 | 0.461538 | 13 | -0.36 |
| veto reason: context VETO in ['team_h'] | 41 | 28 | 0.682927 | 41 | -0.033049 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 36 | 22 | 0.611111 | 36 | -0.014167 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0275 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 5 | 4 | 0.8 | 5 | 0.178 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 246 | 180 | 0.731707 | 228 | 0.016833 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 18 | 12 | 0.666667 | 17 | -0.112353 | 10 | 1.3545 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 95 | 66 | 0.694737 | 95 | -0.018526 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-24: Jong Utrecht vs Heracles (Actual Score: **1-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.55 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.4% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 88.5% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.1% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.5% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.1% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.6% (Actual: 7 goals)

### 2026-08-24: VSG Altglienicke vs Wolfsburg (Actual Score: **3-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.2 -> 🔴 LOST (Expected prob: 73.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 34.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 94.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.1% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.9% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 92.3% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 26.4% (Actual: 6 goals)

### 2026-08-24: Brondby vs Silkeborg (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.6% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.5% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.8% (Actual: 4 goals)

### 2026-08-24: Necaxa W vs América W (Actual Score: **0-7**)
- **1X2 Pick**: Selected `AWAY` @ 1.01 -> 🟢 WON (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.1% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-No**: expected 36.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 7 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.5% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.6% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 95.4% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 80.7% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.6% (Actual: 7 goals)

### 2026-08-24: Hallescher FC vs Schalke 04 (Actual Score: **2-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🟢 WON (Expected prob: 65.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 91.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.1% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.9% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.4% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.8% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.9% (Actual: 7 goals)

### 2026-08-24: Osasuna vs Levante (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🔴 LOST (Expected prob: 59.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 84.6% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.5% (Actual: 0 goals)

### 2026-08-24: Gil Vicente vs Casa Pia AC (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.79 -> 🟢 WON (Expected prob: 58.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.4% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.6% (Actual: 2 goals)

### 2026-08-24: Maccabi Netanya vs Bnei Sakhnin (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🔴 LOST (Expected prob: 59.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 84.6% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.8% (Actual: 0 goals)

### 2026-08-24: Universitario vs Club Deportivo Los Chankas (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.9% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.7% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 82.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.7% (Actual: 3 goals)


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
- 2026-08-15 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous min_p>=60 avg_p>=65` — Olympic Kingsway vs Sorrento FC -> HOME @ 1.24 (pending_or_unmatched_result); keys=['olympicki']/['sorrento', 'sorrentoc']
- 2026-08-17 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hamrun Spartans vs Mosta -> HOME @ 1.18 (pending_or_unmatched_result); keys=['hamrunspa']/['mosta']
- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (pending_or_unmatched_result); keys=['charlesto']/['miami', 'miamiii']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']

## Ambiguous result examples

- none

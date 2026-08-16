# Edge Factory — Recent picks audit (2026-07-18 to 2026-08-16)

## Overall

- archived pick rows: 284
- archived pick dates: 30
- immutable morning-baseline rows: 160
- verified official late-slate additions: 27
- regular-ledger-only legacy rows: 97
- unsafe regular ledgers ignored: 4
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 246
- eligible prior 1x2 picks: 254
- pending/unmatched result picks: 5
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 5
- ambiguous result picks: 0
- wins: 174
- hit rate: +70.7%
- priced picks: 235
- ROI: -2.6%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-16
- same-day rows excluded: 30

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 157 / 246 matches (63.8%)
- **Both Teams to Score (BTTS)**: occurred in 130 / 246 matches (52.8%)
- **Selected Team Over 1.5 Goals**: occurred in 171 / 246 matches (69.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 199
- **Total Hits**: 160
- **Overall Hit Rate**: 80.4%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=105, hits=96, hit_rate=91.4%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=6, hits=6, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=20, hits=13, hit_rate=65.0%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1389** | scored: 1389

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 157 | 157 | 154 | +98.1% | +97.5% | +0.5% | 0.018214 |
| `away_under_25` | 144 | 144 | 137 | +95.1% | +93.4% | +1.7% | 0.047559 |
| `home_over_05` | 140 | 140 | 130 | +92.9% | +88.5% | +4.4% | 0.06925 |
| `match_over_45` | 138 | 138 | 32 | +23.2% | +25.1% | -2.0% | 0.183774 |
| `match_over_25` | 130 | 130 | 76 | +58.5% | +41.6% | +16.8% | 0.281044 |
| `match_over_35` | 98 | 98 | 38 | +38.8% | +43.0% | -4.2% | 0.244783 |
| `exact_4` | 67 | 67 | 17 | +25.4% | +18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | +41.3% | +37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | +33.9% | +30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | +10.5% | +12.6% | -2.1% | 0.096166 |
| `away_under_15` | 51 | 51 | 44 | +86.3% | +81.4% | +4.9% | 0.120013 |
| `home_under_35` | 41 | 41 | 37 | +90.2% | +94.4% | -4.1% | 0.088645 |
| `btts_no` | 40 | 40 | 17 | +42.5% | +52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | +50.0% | +50.9% | -0.9% | 0.248905 |
| `exact_3` | 32 | 32 | 4 | +12.5% | +22.2% | -9.7% | 0.119085 |
| `home_under_25` | 29 | 29 | 26 | +89.7% | +91.5% | -1.8% | 0.093888 |
| `goal_range_2_3` | 26 | 26 | 8 | +30.8% | +46.1% | -15.4% | 0.233772 |
| `exact_2` | 24 | 24 | 5 | +20.8% | +24.5% | -3.7% | 0.166543 |
| `away_over_05` | 22 | 22 | 19 | +86.4% | +86.0% | +0.3% | 0.117067 |
| `goal_range_6_plus` | 9 | 9 | 1 | +11.1% | +18.7% | -7.6% | 0.102748 |
| `match_over_15` | 8 | 8 | 7 | +87.5% | +85.7% | +1.8% | 0.122786 |
| `home_under_15` | 7 | 7 | 6 | +85.7% | +81.3% | +4.5% | 0.123207 |
| `exact_1` | 4 | 4 | 1 | +25.0% | +21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | +33.3% | +13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | +0.0% | +11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | +100.0% | +35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1081 | 665 | +61.5% | +60.3% | +1.2% | 0.135166 |
| legacy | 263 | 136 | +51.7% | +52.1% | -0.4% | 0.183796 |
| model | 45 | 31 | +68.9% | +49.1% | +19.8% | 0.267661 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 149 | +15.8% | +20.1% | +4.3% |
| 0.2-0.3 | 191 | +24.7% | +22.5% | -2.2% |
| 0.3-0.4 | 217 | +35.7% | +44.7% | +9.0% |
| 0.4-0.5 | 143 | +44.6% | +43.4% | -1.2% |
| 0.5-0.6 | 81 | +52.5% | +40.7% | -11.8% |
| 0.6-0.7 | 5 | +65.3% | +100.0% | +34.7% |
| 0.7-0.8 | 4 | +74.4% | +50.0% | -24.4% |
| 0.8-0.9 | 186 | +84.6% | +88.7% | +4.1% |
| 0.9-1.0 | 413 | +95.0% | +95.6% | +0.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=198, MAE=1.442273 goals, bias=-0.518939 (realized − promised), promised avg 3.660354 vs realized 3.141414

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 396 | +15.0% | +10.4% | -4.7% | 0.095238 |
| Away Over 1.5 | 198 | +23.3% | +29.3% | +6.0% | 0.186499 |
| BTTS-Yes | 198 | +41.1% | +52.0% | +10.9% | 0.263462 |
| Home Over 1.5 | 198 | +72.7% | +58.6% | -14.1% | 0.230089 |
| Over 2.5 | 198 | +71.6% | +60.6% | -10.9% | 0.246123 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 142 | +8.8% | +18.3% | +9.5% |
| 0.1-0.2 | 447 | +14.4% | +11.9% | -2.5% |
| 0.2-0.3 | 5 | +20.6% | +20.0% | -0.6% |
| 0.3-0.4 | 60 | +37.7% | +58.3% | +20.6% |
| 0.4-0.5 | 138 | +42.6% | +49.3% | +6.7% |
| 0.6-0.7 | 92 | +67.1% | +52.2% | -14.9% |
| 0.7-0.8 | 97 | +74.6% | +67.0% | -7.6% |
| 0.8-0.9 | 168 | +85.4% | +66.1% | -19.3% |
| 0.9-1.0 | 39 | +91.7% | +79.5% | -12.2% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=92, wins=74, hit_rate=0.804348, ROI=0.084035
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=55, wins=39, hit_rate=0.709091, ROI=-0.042685
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.272222
- `ml-meta avg_p>=55`: settled=49, wins=27, hit_rate=0.55102, ROI=-0.18
- `ml-meta avg_p>=65`: settled=1, wins=1, hit_rate=1.0, ROI=0.5

## By bucket

- `CAUTION`: settled=48, wins=27, hit_rate=0.5625, ROI=-0.108333
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=130, wins=100, hit_rate=0.769231, ROI=0.0476
- `WATCHLIST_NO_ODDS`: settled=10, wins=9, hit_rate=0.9, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=4, wins=2, hit_rate=0.5, ROI=-0.156667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=13, wins=9, hit_rate=0.692308, ROI=-0.046923
- `WATCHLIST_UNKNOWN_CTX`: settled=20, wins=18, hit_rate=0.9, ROI=0.088

## By odds source

- `UNKNOWN`: settled=11, wins=9, hit_rate=0.818182, ROI=None
- `betexplorer_odds`: settled=94, wins=71, hit_rate=0.755319, ROI=0.034574
- `bzzoiro_odds`: settled=81, wins=52, hit_rate=0.641975, ROI=-0.072247
- `forebet_best`: settled=9, wins=6, hit_rate=0.666667, ROI=-0.095556
- `scoutingstats_odds`: settled=40, wins=25, hit_rate=0.625, ROI=-0.164
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=16, wins=11, hit_rate=0.6875, ROI=-0.07
- `betexplorer`: settled=94, wins=71, hit_rate=0.755319, ROI=0.034574
- `exact`: settled=113, wins=72, hit_rate=0.637168, ROI=-0.093558
- `fallback`: settled=13, wins=11, hit_rate=0.846154, ROI=0.165385
- `none`: settled=10, wins=9, hit_rate=0.9, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 94 | 71 | 0.755319 | 94 | 0.034574 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 73 | 47 | 0.643836 | 73 | -0.054959 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 40 | 25 | 0.625 | 40 | -0.164 |
| Source fallback (`SOURCE_FALLBACK`) | 13 | 11 | 0.846154 | 13 | 0.165385 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 16 | 11 | 0.6875 | 15 | -0.07 |
| No usable price (`UNMATCHED`) | 10 | 9 | 0.9 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 130 | 100 | 0.769231 | 130 | 0.0476 |
| **trusted evidence only** | 98 | 74 | 0.755102 | 98 | 0.037633 |
| **soft evidence only** | 32 | 26 | 0.8125 | 32 | 0.078125 |
| evidence: BETEXPLORER_RESCUE | 52 | 42 | 0.807692 | 52 | 0.071923 |
| evidence: BZZOIRO_PRIMARY | 46 | 32 | 0.695652 | 46 | -0.00113 |
| evidence: SCOUTINGSTATS_SOLE | 17 | 12 | 0.705882 | 17 | -0.077059 |
| evidence: SOURCE_FALLBACK | 7 | 7 | 1.0 | 7 | 0.405714 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 7 | 0.875 | 8 | 0.12125 |
| odds band: <1.50 | 102 | 81 | 0.794118 | 102 | 0.020471 |
| odds band: 1.50-2.00 | 26 | 17 | 0.653846 | 26 | 0.073846 |
| odds band: 2.00-3.00 | 2 | 2 | 1.0 | 2 | 1.09 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.136 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 7 | 5 | 0.714286 | 7 | -0.082857 |
| veto reason: context VETO in ['odds_band'] | 42 | 33 | 0.785714 | 42 | 0.057143 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.130429 |
| veto reason: context VETO in ['team_a'] | 19 | 16 | 0.842105 | 19 | 0.263158 |
| veto reason: context VETO in ['team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.35 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.2275 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.013333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 6 | 2 | 0.333333 | 6 | -0.593333 |
| veto reason: context VETO in ['team_h'] | 23 | 16 | 0.695652 | 23 | -0.062826 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| contrast CAUTION: BETEXPLORER_RESCUE | 20 | 14 | 0.7 | 20 | 0.1095 |
| contrast CAUTION: BZZOIRO_PRIMARY | 16 | 10 | 0.625 | 16 | -0.003125 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 7 | 1 | 0.142857 | 7 | -0.757143 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 190 | 138 | 0.726316 | 180 | 0.007711 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 16 | 11 | 0.6875 | 15 | -0.07 | 8 | 1.359375 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 40 | 25 | 0.625 | 40 | -0.164 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-15: Bolivar vs San Antonio Bulo Bulo (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 2.85 -> 🟢 WON (Expected prob: 80.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 92.0% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (19.3%), [🔴 MISS] 3-1 (14.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +84.4% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.6% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +21.0% (Actual: 5 goals)

### 2026-08-15: O'Connor Knights vs Canberra White Eagles (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.91 -> 🟢 WON (Expected prob: 68.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (15.0%), [🔴 MISS] 1-0 (13.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +93.2% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +44.9% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +25.6% (Actual: 4 goals)

### 2026-08-15: Ludogorets Razgrad vs Botev Plovdiv (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.62 -> 🟢 WON (Expected prob: 64.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (17.7%), [🔴 MISS] 1-0 (15.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.0% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +42.9% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +20.1% (Actual: 2 goals)

### 2026-08-15: Al-Ittihad Jeddah vs Al Kholood (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.49 -> 🔴 LOST (Expected prob: 63.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.7%), [🔴 MISS] 1-0 (15.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +85.4% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +42.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +19.3% (Actual: 2 goals)

### 2026-08-15: Rio Ave vs FC Porto (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.45 -> 🟢 WON (Expected prob: 62.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 2 goals)
  - **Top Scores**: [🟢 HIT] 0-2 (16.2%), [🔴 MISS] 1-2 (14.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +93.7% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +91.1% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +44.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +22.1% (Actual: 2 goals)

### 2026-08-15: Torreense vs Penafiel (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.81 -> 🔴 LOST (Expected prob: 57.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (18.2%), [🔴 MISS] 2-1 (17.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.6% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +40.4% (Actual: 4 goals)

### 2026-08-15: Launceston City vs Clarence Zebras (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.83 -> 🔴 LOST (Expected prob: 58.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.7%), [🔴 MISS] 2-1 (17.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +83.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +42.5% (Actual: 2 goals)

### 2026-08-15: Tekstilshtik Ivanovo vs FC Nizhny Novgorod (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.42 -> 🟢 WON (Expected prob: 56.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.4% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 1-2 (17.0%), [🔴 MISS] 0-2 (16.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +93.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +89.5% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +42.2% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +18.1% (Actual: 4 goals)

### 2026-08-15: Vancouver FC vs Pacific (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.46 -> 🔴 LOST (Expected prob: 66.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.9%), [🔴 MISS] 1-0 (14.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +92.0% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +97.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +83.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +41.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +22.1% (Actual: 2 goals)

### 2026-08-15: Karlstad BK vs Assyriska FF (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.51 -> 🔴 LOST (Expected prob: 57.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (18.1%), [🔴 MISS] 2-1 (17.3%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +87.2% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.8% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.8% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +37.9% (Actual: 2 goals)

### 2026-08-15: West Torrens Birkalla vs Adelaide United II (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.05 -> 🟢 WON (Expected prob: 77.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.7%), [🔴 MISS] 4-0 (11.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +46.5% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.4% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +91.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +27.8% (Actual: 3 goals)

### 2026-08-15: East Kilbride vs Cove Rangers (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (12.2%), [🔴 MISS] 2-0 (12.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +50.7% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +89.3% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +27.8% (Actual: 3 goals)

### 2026-08-15: Mallorca vs Valladolid (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.82 -> 🟢 WON (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.1%), [🔴 MISS] 2-1 (17.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +83.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +41.1% (Actual: 2 goals)

### 2026-08-15: Huddersfield vs AFC Wimbledon (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.67 -> 🟢 WON (Expected prob: 57.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (18.2%), [🔴 MISS] 2-1 (17.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.7% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.4% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +40.5% (Actual: 3 goals)

### 2026-08-15: Godoy Cruz vs Deportivo Maipu (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🔴 LOST (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (18.8%), [🔴 MISS] 1-0 (18.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +81.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +40.0% (Actual: 3 goals)

### 2026-08-15: JEF United Chiba vs Machida Zelvia (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 2.0 -> 🟢 WON (Expected prob: 55.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 4 goals)
  - **Top Scores**: [🔴 MISS] 1-2 (17.2%), [🔴 MISS] 0-2 (16.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +92.3% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +88.9% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +42.7% (Actual: 4 goals)

### 2026-08-15: Oviedo vs Granada CF (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.82 -> 🔴 LOST (Expected prob: 55.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 46.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (19.1%), [🔴 MISS] 1-0 (19.1%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +81.2% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +39.9% (Actual: 0 goals)

### 2026-08-15: Middlesbrough vs Lincoln (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🟢 WON (Expected prob: 58.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.2%), [🟢 HIT] 2-1 (17.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +88.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +38.1% (Actual: 3 goals)

### 2026-08-15: Torino vs Carrarese (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.43 -> 🟢 WON (Expected prob: 58.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 1-0 (17.7%), [🔴 MISS] 2-1 (17.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.7% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +41.0% (Actual: 1 goals)

### 2026-08-15: Sparta Praha vs Teplice (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 57.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.7%), [🔴 MISS] 2-1 (17.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +83.0% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +41.3% (Actual: 5 goals)

### 2026-08-15: Brindabella Blues vs Cooma Tigers (Actual Score: **1-6**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 78.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 83.0% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 36.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 91.5% (Actual: 6 goals)
  - **Top Scores**: [🔴 MISS] 0-3 (18.4%), [🔴 MISS] 1-2 (13.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +50.2% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +81.1% (Actual: 6 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +91.7% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +89.9% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected +82.3% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +30.6% (Actual: 7 goals)

### 2026-08-15: Union Saint-Gilloise vs Zulte Waregem (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 76.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.7% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 4-0 (11.9%), [🔴 MISS] 2-1 (11.9%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +52.4% (Actual: 0 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +88.2% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +91.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +30.4% (Actual: 0 goals)

### 2026-08-15: Slovan Bratislava vs MFK Ruzomberok (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 67.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.5% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.0% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (14.8%), [🔴 MISS] 1-0 (14.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +92.7% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.7% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +42.8% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +24.4% (Actual: 5 goals)

### 2026-08-15: Al-Nassr vs Al-Fateh (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.12 -> 🟢 WON (Expected prob: 80.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (20.0%), [🔴 MISS] 3-1 (13.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.0% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +93.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +43.9% (Actual: 3 goals)

### 2026-08-15: Deportivo Moron vs Almagro (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🟢 WON (Expected prob: 62.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (17.7%), [🔴 MISS] 1-0 (16.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +84.4% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +83.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +40.2% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +18.4% (Actual: 2 goals)

### 2026-08-15: South Shields vs Chorley (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 56.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (18.5%), [🟢 HIT] 2-1 (18.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +40.8% (Actual: 3 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 3 |
- 2026-07-19 `POSTPONED` `WATCHLIST_NO_ODDS` — FC Levadia Tallinn vs Tammeka (verified_disposition); excluded from win/loss/ROI
- 2026-07-25 `POSTPONED` `WATCHLIST_NO_ODDS` — Coquimbo Unido vs Universidad de Concepcion (verified_disposition); excluded from win/loss/ROI
- 2026-07-26 `POSTPONED` `SKIPPED_VETO` — Super Nova vs Riga (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- 2026-08-08 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Belshina vs Dinamo Minsk -> AWAY @ 1.32 (pending_or_unmatched_result); keys=['belshina', 'belshinab']/['dinamomin']
- 2026-08-11 `WATCHLIST_UNCORROBORATED_PRICE` `2way+bc-confirms avg_p>=60` — Junior vs Pereira -> HOME @ 1.33 (pending_or_unmatched_result); keys=['junior']/['pereira']
- 2026-08-15 `SKIPPED_VETO` `2way-unanimous min_p>=60 avg_p>=65` — Slavia Sofia vs Levski Sofia -> AWAY @ 1.36 (pending_or_unmatched_result); keys=['slaviasof']/['levskisof']
- 2026-08-15 `WATCHLIST_NO_ODDS` `2way-unanimous min_p>=60 avg_p>=65` — Kara-Balta vs Bars -> AWAY @ None (pending_or_unmatched_result); keys=['karabalta']/['bars']
- 2026-08-15 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous min_p>=60 avg_p>=65` — Olympic Kingsway vs Sorrento FC -> HOME @ 1.24 (pending_or_unmatched_result); keys=['olympicki']/['sorrento']

## Ambiguous result examples

- none

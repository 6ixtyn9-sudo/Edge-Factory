# Edge Factory — Recent picks audit (2026-07-09 to 2026-08-07)

## Overall

- archived pick rows: 144
- archived pick dates: 30
- immutable morning-baseline rows: 91
- verified official late-slate additions: 28
- regular-ledger-only legacy rows: 25
- unsafe regular ledgers ignored: 3
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 137
- eligible prior 1x2 picks: 140
- pending/unmatched result picks: 0
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 6
- ambiguous result picks: 0
- wins: 106
- hit rate: 0.773723
- priced picks: 132
- ROI: 0.02097

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-07
- same-day rows excluded: 4

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 92 / 137 matches (67.2%)
- **Both Teams to Score (BTTS)**: occurred in 65 / 137 matches (47.4%)
- **Selected Team Over 1.5 Goals**: occurred in 102 / 137 matches (74.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 51
- **Total Hits**: 33
- **Overall Hit Rate**: 64.7%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=2, hits=2, hit_rate=100.0%
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `home_over_05`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **474** | scored: 474

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 41 | 41 | 39 | 95.1% | 96.2% | -1.1% | 0.044407 |
| `btts_yes` | 38 | 38 | 19 | 50.0% | 50.9% | -0.9% | 0.248905 |
| `exact_4` | 34 | 34 | 11 | 32.4% | 17.4% | +14.9% | 0.2438 |
| `match_over_35` | 31 | 31 | 17 | 54.8% | 41.6% | +13.2% | 0.290335 |
| `away_under_25` | 30 | 30 | 28 | 93.3% | 90.7% | +2.6% | 0.065632 |
| `goal_range_4_6` | 30 | 30 | 15 | 50.0% | 35.8% | +14.2% | 0.278487 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `goal_range_4_5` | 26 | 26 | 11 | 42.3% | 30.1% | +12.2% | 0.267862 |
| `home_over_05` | 26 | 26 | 26 | 100.0% | 87.0% | +13.0% | 0.018964 |
| `exact_3` | 25 | 25 | 1 | 4.0% | 22.2% | -18.2% | 0.071688 |
| `exact_2` | 24 | 24 | 5 | 20.8% | 24.5% | -3.7% | 0.166543 |
| `exact_5` | 24 | 24 | 3 | 12.5% | 12.3% | +0.2% | 0.113775 |
| `match_over_25` | 24 | 24 | 14 | 58.3% | 49.3% | +9.1% | 0.293131 |
| `match_over_45` | 24 | 24 | 6 | 25.0% | 26.5% | -1.5% | 0.21159 |
| `btts_no` | 21 | 21 | 11 | 52.4% | 53.8% | -1.4% | 0.250526 |
| `home_under_35` | 17 | 17 | 13 | 76.5% | 94.0% | -17.5% | 0.208375 |
| `match_over_15` | 8 | 8 | 7 | 87.5% | 85.7% | +1.8% | 0.122786 |
| `away_over_05` | 5 | 5 | 4 | 80.0% | 85.2% | -5.2% | 0.157967 |
| `away_under_15` | 5 | 5 | 4 | 80.0% | 80.9% | -0.9% | 0.15875 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `home_under_25` | 4 | 4 | 3 | 75.0% | 89.6% | -14.6% | 0.208021 ⚠️low-n |
| `goal_range_6_plus` | 2 | 2 | 0 | 0.0% | 27.1% | -27.1% | 0.075286 ⚠️low-n |
| `goal_range_7_plus` | 2 | 2 | 0 | 0.0% | 15.1% | -15.1% | 0.023681 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |
| `home_under_15` | 1 | 1 | 1 | 100.0% | 80.4% | +19.6% | 0.038519 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| hybrid_cohort | 183 | 96 | 52.5% | 49.1% | +3.4% | 0.163624 |
| model | 28 | 16 | 57.1% | 45.4% | +11.8% | 0.298173 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 64 | 15.4% | 26.6% | +11.2% |
| 0.2-0.3 | 88 | 24.6% | 21.6% | -3.0% |
| 0.3-0.4 | 66 | 34.9% | 51.5% | +16.7% |
| 0.4-0.5 | 63 | 46.1% | 42.9% | -3.2% |
| 0.5-0.6 | 47 | 53.2% | 40.4% | -12.8% |
| 0.6-0.7 | 5 | 65.3% | 100.0% | +34.7% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 48 | 84.7% | 91.7% | +7.0% |
| 0.9-1.0 | 89 | 94.5% | 91.0% | -3.5% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=50, MAE=1.2802 goals, bias=-0.3274 (realized − promised), promised avg 3.8074 vs realized 3.48

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 100 | 14.3% | 8.0% | -6.3% | 0.078144 |
| Away Over 1.5 | 50 | 23.4% | 26.0% | +2.6% | 0.137634 |
| BTTS-Yes | 50 | 39.8% | 46.0% | +6.2% | 0.253707 |
| Home Over 1.5 | 50 | 73.8% | 64.0% | -9.8% | 0.185064 |
| Over 2.5 | 50 | 73.8% | 66.0% | -7.8% | 0.230366 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 36 | 8.5% | 13.9% | +5.4% |
| 0.1-0.2 | 110 | 13.5% | 8.2% | -5.4% |
| 0.2-0.3 | 4 | 20.8% | 25.0% | +4.2% |
| 0.3-0.4 | 27 | 37.6% | 55.6% | +17.9% |
| 0.4-0.5 | 23 | 42.4% | 34.8% | -7.6% |
| 0.6-0.7 | 10 | 67.3% | 60.0% | -7.3% |
| 0.7-0.8 | 36 | 74.5% | 66.7% | -7.8% |
| 0.8-0.9 | 40 | 86.6% | 80.0% | -6.6% |
| 0.9-1.0 | 14 | 91.9% | 64.3% | -27.6% |

## By rule

- `2way-unanimous avg_p>=70`: settled=67, wins=53, hit_rate=0.791045, ROI=0.045286
- `3way-unanimous avg_p>=65`: settled=48, wins=34, hit_rate=0.708333, ROI=-0.052447
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=12, wins=10, hit_rate=0.833333, ROI=-0.0325

## By bucket

- `CAUTION`: settled=34, wins=19, hit_rate=0.558824, ROI=-0.116471
- `SKIPPED_VETO`: settled=78, wins=65, hit_rate=0.833333, ROI=0.068949
- `WATCHLIST_NO_ODDS`: settled=5, wins=4, hit_rate=0.8, ROI=None
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=1, wins=1, hit_rate=1.0, ROI=0.2
- `WATCHLIST_UNKNOWN_CTX`: settled=19, wins=17, hit_rate=0.894737, ROI=0.060526

## By odds source

- `UNKNOWN`: settled=5, wins=4, hit_rate=0.8, ROI=None
- `betexplorer_odds`: settled=70, wins=58, hit_rate=0.828571, ROI=0.070714
- `bzzoiro_odds`: settled=35, wins=29, hit_rate=0.828571, ROI=0.159657
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=19, wins=9, hit_rate=0.473684, ROI=-0.395789
- `zulubet`: settled=6, wins=5, hit_rate=0.833333, ROI=0.088333

## By odds match method

- `alias_fuzzy`: settled=8, wins=5, hit_rate=0.625, ROI=-0.23
- `betexplorer`: settled=70, wins=58, hit_rate=0.828571, ROI=0.070714
- `exact`: settled=46, wins=33, hit_rate=0.717391, ROI=-0.002
- `fallback`: settled=8, wins=6, hit_rate=0.75, ROI=-0.03125
- `none`: settled=5, wins=4, hit_rate=0.8, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 70 | 58 | 0.828571 | 70 | 0.070714 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 27 | 24 | 0.888889 | 27 | 0.275111 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 19 | 9 | 0.473684 | 19 | -0.395789 |
| Source fallback (`SOURCE_FALLBACK`) | 8 | 6 | 0.75 | 8 | -0.03125 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 8 | 5 | 0.625 | 8 | -0.23 |
| No usable price (`UNMATCHED`) | 5 | 4 | 0.8 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 78 | 65 | 0.833333 | 78 | 0.068949 |
| **trusted evidence only** | 65 | 55 | 0.846154 | 65 | 0.090585 |
| **soft evidence only** | 13 | 10 | 0.769231 | 13 | -0.039231 |
| evidence: BETEXPLORER_RESCUE | 47 | 40 | 0.851064 | 47 | 0.083191 |
| evidence: BZZOIRO_PRIMARY | 18 | 15 | 0.833333 | 18 | 0.109889 |
| evidence: SCOUTINGSTATS_SOLE | 5 | 3 | 0.6 | 5 | -0.282 |
| evidence: SOURCE_FALLBACK | 4 | 4 | 1.0 | 4 | 0.2975 |
| evidence: SUSPECT_ALIAS_FUZZY | 4 | 3 | 0.75 | 4 | -0.0725 |
| odds band: <1.50 | 71 | 60 | 0.84507 | 71 | 0.05307 |
| odds band: 1.50-2.00 | 6 | 4 | 0.666667 | 6 | 0.071667 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.17 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 5 | 3 | 0.6 | 5 | -0.334 |
| veto reason: context VETO in ['odds_band'] | 34 | 27 | 0.794118 | 34 | 0.054706 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.331 |
| veto reason: context VETO in ['team_a'] | 5 | 5 | 1.0 | 5 | 0.4 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.41 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: context VETO in ['team_h'] | 7 | 6 | 0.857143 | 7 | 0.022143 |
| veto reason: short-odds away favourite 1.05 | 1 | 1 | 1.0 | 1 | 0.05 |
| veto reason: short-odds away favourite 1.07 | 1 | 1 | 1.0 | 1 | 0.07 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| contrast CAUTION: BETEXPLORER_RESCUE | 12 | 8 | 0.666667 | 12 | 0.038333 |
| contrast CAUTION: BZZOIRO_PRIMARY | 8 | 8 | 1.0 | 8 | 0.65375 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 10 | 2 | 0.2 | 10 | -0.697 |
| contrast CAUTION: SOURCE_FALLBACK | 2 | 1 | 0.5 | 2 | -0.34 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 110 | 92 | 0.836364 | 105 | 0.115505 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 8 | 5 | 0.625 | 8 | -0.23 | 0 | None |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 19 | 9 | 0.473684 | 19 | -0.395789 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-06: Valur Reykjavik vs FC Nordsjaelland (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.33 -> 🟢 WON (Expected prob: 67.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 2 goals)
  - **Top Scores**: [🟢 HIT] 0-2 (20.5%), [🔴 MISS] 0-1 (15.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 86.6% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 40.2% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.3% (Actual: 0 home goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.0% (Actual: BTTS-No)
    - [🔴 MISS] **Goal Range 4-6**: expected 35.9% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 29.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.3% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.2% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.0% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 11.6% (Actual: 2 goals)

### 2026-08-06: Paide vs Rapid Vienna (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.19 -> 🟢 WON (Expected prob: 78.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 82.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 36.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 91.3% (Actual: 4 goals)
  - **Top Scores**: [🔴 MISS] 0-3 (17.4%), [🔴 MISS] 1-2 (13.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 52.6% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 36.6% (Actual: 5 goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 93.8% (Actual: 4 away goals)
    - [🟢 HIT] **Goal Range 4-6**: expected 33.0% (Actual: 5 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 27.6% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.4% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.5% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 17.1% (Actual: 5 goals)
    - [🟢 HIT] **Exact Goals: 5**: expected 10.5% (Actual: 5 goals)

### 2026-08-06: FC Lugano vs NSI Runavik (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.13 -> 🟢 WON (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (12.6%), [🔴 MISS] 1-0 (12.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.4% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.7% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 50.6% (Actual: BTTS-No)
    - [🔴 MISS] **Goal Range 4-6**: expected 38.9% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 37.3% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.4% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.7% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.8% (Actual: 2 goals)

### 2026-08-06: SC Braga vs Dinamo Minsk (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.12 -> 🟢 WON (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 77.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (12.6%), [🟢 HIT] 1-0 (11.3%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.4% (Actual: BTTS-No)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 50.0% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 53.6% (Actual: BTTS-No)
    - [🔴 MISS] **Goal Range 4-6**: expected 39.1% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 37.0% (Actual: 1 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.7% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.9% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.7% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.9% (Actual: 1 goals)

### 2026-08-06: FC Thun vs Vikingur Reykjavik (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.43 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.4%), [🔴 MISS] 2-1 (13.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 50.6% (Actual: BTTS-No)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 92.1% (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.9% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.1% (Actual: 0 away goals)
    - [🔴 MISS] **Goal Range 4-6**: expected 39.8% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 37.1% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 32.1% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.9% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.9% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 13.2% (Actual: 3 goals)

### 2026-08-06: Ajax vs Shelbourne (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.08 -> 🟢 WON (Expected prob: 68.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.4%), [🔴 MISS] 1-0 (12.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 47.4% (Actual: BTTS-Yes)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.5% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 41.4% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.2% (Actual: 1 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.6% (Actual: BTTS-Yes)
    - [🟢 HIT] **Goal Range 4-6**: expected 37.0% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 30.4% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.9% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.1% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 18.3% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.1% (Actual: 4 goals)

### 2026-08-06: Twente vs Dunajska Streda (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.8% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.0%), [🔴 MISS] 3-0 (12.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 92.6% (Actual: 6 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 46.4% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.3% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 50.5% (Actual: BTTS-No)
    - [🟢 HIT] **Goal Range 4-6**: expected 39.0% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 37.2% (Actual: 6 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.6% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.5% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.7% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.9% (Actual: 6 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 3 |
- 2026-07-19 `POSTPONED` `WATCHLIST_NO_ODDS` — FC Levadia Tallinn vs Tammeka (verified_disposition); excluded from win/loss/ROI
- 2026-07-25 `POSTPONED` `WATCHLIST_NO_ODDS` — Coquimbo Unido vs Universidad de Concepcion (verified_disposition); excluded from win/loss/ROI
- 2026-07-26 `POSTPONED` `SKIPPED_VETO` — Super Nova vs Riga (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- none

## Ambiguous result examples

- none

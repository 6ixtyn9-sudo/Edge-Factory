# Edge Factory — Recent picks audit (2026-07-11 to 2026-08-09)

## Overall

- archived pick rows: 197
- archived pick dates: 30
- immutable morning-baseline rows: 123
- verified official late-slate additions: 28
- regular-ledger-only legacy rows: 46
- unsafe regular ledgers ignored: 3
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 154
- eligible prior 1x2 picks: 158
- pending/unmatched result picks: 1
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 6
- ambiguous result picks: 0
- wins: 121
- hit rate: 0.785714
- priced picks: 147
- ROI: 0.040939

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-09
- same-day rows excluded: 39

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 105 / 154 matches (68.2%)
- **Both Teams to Score (BTTS)**: occurred in 75 / 154 matches (48.7%)
- **Selected Team Over 1.5 Goals**: occurred in 117 / 154 matches (76.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 75
- **Total Hits**: 55
- **Overall Hit Rate**: 73.3%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=3, hits=3, hit_rate=100.0%
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=24, hits=23, hit_rate=95.8%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **741** | scored: 741

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 64 | 64 | 62 | 96.9% | 96.6% | +0.3% | 0.028787 |
| `exact_4` | 58 | 58 | 15 | 25.9% | 17.9% | +8.0% | 0.200455 |
| `match_over_35` | 55 | 55 | 25 | 45.5% | 43.4% | +2.0% | 0.264005 |
| `goal_range_4_6` | 54 | 54 | 22 | 40.7% | 37.1% | +3.7% | 0.250732 |
| `away_under_25` | 53 | 53 | 50 | 94.3% | 91.7% | +2.6% | 0.05623 |
| `goal_range_4_5` | 50 | 50 | 16 | 32.0% | 30.7% | +1.3% | 0.223239 |
| `home_over_05` | 49 | 49 | 48 | 98.0% | 88.9% | +9.1% | 0.030846 |
| `exact_5` | 48 | 48 | 4 | 8.3% | 12.5% | -4.2% | 0.080335 |
| `match_over_45` | 48 | 48 | 10 | 20.8% | 26.9% | -6.1% | 0.180219 |
| `match_over_25` | 43 | 43 | 27 | 62.8% | 43.9% | +18.9% | 0.301093 |
| `btts_yes` | 38 | 38 | 19 | 50.0% | 50.9% | -0.9% | 0.248905 |
| `btts_no` | 36 | 36 | 17 | 47.2% | 53.0% | -5.8% | 0.25281 |
| `exact_3` | 32 | 32 | 4 | 12.5% | 22.2% | -9.7% | 0.119085 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `exact_2` | 24 | 24 | 5 | 20.8% | 24.5% | -3.7% | 0.166543 |
| `home_under_35` | 18 | 18 | 14 | 77.8% | 94.0% | -16.2% | 0.197013 |
| `away_under_15` | 10 | 10 | 9 | 90.0% | 80.8% | +9.2% | 0.0979 |
| `match_over_15` | 8 | 8 | 7 | 87.5% | 85.7% | +1.8% | 0.122786 |
| `away_over_05` | 6 | 6 | 5 | 83.3% | 85.5% | -2.2% | 0.134428 |
| `goal_range_6_plus` | 6 | 6 | 1 | 16.7% | 20.3% | -3.6% | 0.142205 |
| `home_under_25` | 5 | 5 | 4 | 80.0% | 88.9% | -8.9% | 0.170341 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | 33.3% | 13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |
| `home_under_15` | 1 | 1 | 1 | 100.0% | 80.4% | +19.6% | 0.038519 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 440 | 216 | 49.1% | 49.0% | +0.1% | 0.150291 |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| model | 38 | 24 | 63.2% | 46.1% | +17.0% | 0.280314 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 116 | 15.5% | 19.8% | +4.4% |
| 0.2-0.3 | 119 | 24.9% | 21.8% | -3.0% |
| 0.3-0.4 | 130 | 35.0% | 44.6% | +9.7% |
| 0.4-0.5 | 87 | 45.6% | 40.2% | -5.4% |
| 0.5-0.6 | 66 | 52.8% | 40.9% | -11.9% |
| 0.6-0.7 | 5 | 65.3% | 100.0% | +34.7% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 61 | 84.7% | 93.4% | +8.7% |
| 0.9-1.0 | 153 | 94.5% | 93.5% | -1.0% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=74, MAE=1.327162 goals, bias=-0.435541 (realized − promised), promised avg 3.813919 vs realized 3.378378

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 148 | 14.1% | 10.1% | -3.9% | 0.093343 |
| Away Over 1.5 | 74 | 19.9% | 27.0% | +7.1% | 0.161742 |
| BTTS-Yes | 74 | 40.4% | 47.3% | +6.9% | 0.258306 |
| Home Over 1.5 | 74 | 77.5% | 67.6% | -9.9% | 0.179525 |
| Over 2.5 | 74 | 74.0% | 66.2% | -7.8% | 0.228838 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 53 | 8.7% | 15.1% | +6.4% |
| 0.1-0.2 | 165 | 13.4% | 11.5% | -1.9% |
| 0.2-0.3 | 4 | 20.8% | 25.0% | +4.2% |
| 0.3-0.4 | 33 | 37.6% | 60.6% | +23.0% |
| 0.4-0.5 | 41 | 42.6% | 36.6% | -6.0% |
| 0.6-0.7 | 13 | 67.4% | 61.5% | -5.8% |
| 0.7-0.8 | 56 | 74.7% | 66.1% | -8.6% |
| 0.8-0.9 | 58 | 86.7% | 77.6% | -9.1% |
| 0.9-1.0 | 21 | 91.8% | 76.2% | -15.6% |

## By rule

- `2way-unanimous avg_p>=70`: settled=81, wins=66, hit_rate=0.814815, ROI=0.08164
- `3way-unanimous avg_p>=65`: settled=52, wins=37, hit_rate=0.711538, ROI=-0.047745
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=11, wins=9, hit_rate=0.818182, ROI=-0.04

## By bucket

- `CAUTION`: settled=31, wins=19, hit_rate=0.612903, ROI=-0.02871
- `SKIPPED_VETO`: settled=94, wins=77, hit_rate=0.819149, ROI=0.065404
- `WATCHLIST_NO_ODDS`: settled=7, wins=6, hit_rate=0.857143, ROI=None
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=1, wins=1, hit_rate=1.0, ROI=0.2
- `WATCHLIST_UNKNOWN_CTX`: settled=21, wins=18, hit_rate=0.857143, ROI=0.026667

## By odds source

- `UNKNOWN`: settled=7, wins=6, hit_rate=0.857143, ROI=None
- `betexplorer_odds`: settled=73, wins=61, hit_rate=0.835616, ROI=0.08274
- `bzzoiro_odds`: settled=42, wins=35, hit_rate=0.833333, ROI=0.174238
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=24, wins=12, hit_rate=0.5, ROI=-0.362917
- `zulubet`: settled=6, wins=6, hit_rate=1.0, ROI=0.358333

## By odds match method

- `alias_fuzzy`: settled=8, wins=5, hit_rate=0.625, ROI=-0.23
- `betexplorer`: settled=73, wins=61, hit_rate=0.835616, ROI=0.08274
- `exact`: settled=58, wins=42, hit_rate=0.724138, ROI=0.007724
- `fallback`: settled=8, wins=7, hit_rate=0.875, ROI=0.17125
- `none`: settled=7, wins=6, hit_rate=0.857143, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 73 | 61 | 0.835616 | 73 | 0.08274 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 34 | 30 | 0.882353 | 34 | 0.269353 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 24 | 12 | 0.5 | 24 | -0.362917 |
| Source fallback (`SOURCE_FALLBACK`) | 8 | 7 | 0.875 | 8 | 0.17125 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 8 | 5 | 0.625 | 8 | -0.23 |
| No usable price (`UNMATCHED`) | 7 | 6 | 0.857143 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 94 | 77 | 0.819149 | 94 | 0.065404 |
| **trusted evidence only** | 75 | 63 | 0.84 | 75 | 0.096373 |
| **soft evidence only** | 19 | 14 | 0.736842 | 19 | -0.056842 |
| evidence: BETEXPLORER_RESCUE | 52 | 44 | 0.846154 | 52 | 0.083462 |
| evidence: BZZOIRO_PRIMARY | 23 | 19 | 0.826087 | 23 | 0.125565 |
| evidence: SCOUTINGSTATS_SOLE | 10 | 6 | 0.6 | 10 | -0.26 |
| evidence: SOURCE_FALLBACK | 5 | 5 | 1.0 | 5 | 0.362 |
| evidence: SUSPECT_ALIAS_FUZZY | 4 | 3 | 0.75 | 4 | -0.0725 |
| odds band: <1.50 | 83 | 69 | 0.831325 | 83 | 0.046361 |
| odds band: 1.50-2.00 | 10 | 7 | 0.7 | 10 | 0.112 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.17 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 5 | 3 | 0.6 | 5 | -0.334 |
| veto reason: context VETO in ['odds_band'] | 38 | 30 | 0.789474 | 38 | 0.047368 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 5 | 5 | 1.0 | 5 | 0.3666 |
| veto reason: context VETO in ['team_a'] | 9 | 7 | 0.777778 | 9 | 0.093333 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.06 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.255 |
| veto reason: context VETO in ['team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: context VETO in ['team_h'] | 11 | 10 | 0.909091 | 11 | 0.165 |
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
| contrast CAUTION: BETEXPLORER_RESCUE | 9 | 7 | 0.777778 | 9 | 0.214444 |
| contrast CAUTION: BZZOIRO_PRIMARY | 9 | 9 | 1.0 | 9 | 0.647778 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 10 | 2 | 0.2 | 10 | -0.697 |
| contrast CAUTION: SOURCE_FALLBACK | 1 | 1 | 1.0 | 1 | 0.32 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 122 | 104 | 0.852459 | 115 | 0.14407 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 8 | 5 | 0.625 | 8 | -0.23 | 0 | None |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 24 | 12 | 0.5 | 24 | -0.362917 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-08: Servette FC vs Grasshopper-Club (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.5%), [🔴 MISS] 3-0 (13.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.5% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.8% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.4% (Actual: 1 away goals)
    - [🔴 MISS] **Goal Range 4-6**: expected 38.6% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.3% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.3% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.3% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.6% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.7% (Actual: 3 goals)

### 2026-08-08: PSV Eindhoven vs Fortuna Sittard (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.21 -> 🔴 LOST (Expected prob: 83.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 84.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 94.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 92.3% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 4-0 (17.9%), [🔴 MISS] 3-1 (12.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.1% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 46.3% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 86.4% (Actual: 2 away goals)
    - [🟢 HIT] **Goal Range 4-6**: expected 39.8% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.2% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 32.1% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.4% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 18.9% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 13.2% (Actual: 4 goals)

### 2026-08-08: Monaro Panthers vs Belconnen United (Actual Score: **7-0**)
- **1X2 Pick**: Selected `HOME` @ 1.08 -> 🟢 WON (Expected prob: 76.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.5% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.7% (Actual: 7 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.1%), [🔴 MISS] 4-0 (11.4%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Goal Range 4-6**: expected 45.1% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 94.7% (Actual: 7 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 54.4% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.7% (Actual: 7 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 34.9% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 33.1% (Actual: 7 goals)
    - [🟢 HIT] **Goal Range 6+**: expected 20.7% (Actual: 7 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 19.5% (Actual: 7 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 15.4% (Actual: 7 goals)
    - [🟢 HIT] **Goal Range 7+**: expected 10.5% (Actual: 7 goals)

### 2026-08-08: Podbeskidzie vs Lechia Gdansk (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🔴 LOST (Expected prob: 75.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.0%), [🔴 MISS] 2-1 (11.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.7% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 50.8% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.1% (Actual: 2 away goals)
    - [🟢 HIT] **Goal Range 4-6**: expected 40.6% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 38.9% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 32.6% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.2% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 19.0% (Actual: 4 goals)
    - [🔴 MISS] **Goal Range 6+**: expected 15.0% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 13.5% (Actual: 4 goals)

### 2026-08-08: Boreham Wood vs Tamworth (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🔴 LOST (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.6% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (12.2%), [🔴 MISS] 1-0 (12.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 92.5% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 48.0% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 3 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 50.8% (Actual: BTTS-Yes)
    - [🟢 HIT] **Goal Range 4-6**: expected 39.1% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 37.7% (Actual: 6 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.7% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.1% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.7% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.9% (Actual: 6 goals)

### 2026-08-08: FK Sarajevo vs Radnik Bijeljina (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🔴 LOST (Expected prob: 72.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.8% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.6%), [🔴 MISS] 3-0 (13.1%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 91.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 45.6% (Actual: 0 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.9% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 52.1% (Actual: BTTS-No)
    - [🔴 MISS] **Goal Range 4-6**: expected 37.8% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 35.8% (Actual: 0 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 30.8% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.3% (Actual: 0 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.4% (Actual: 0 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.4% (Actual: 0 goals)

### 2026-08-08: Rosario Central vs Aldosivi (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.49 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.5%), [🔴 MISS] 3-0 (13.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.3% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.5% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.2% (Actual: 1 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.4% (Actual: BTTS-Yes)
    - [🔴 MISS] **Goal Range 4-6**: expected 36.9% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 30.2% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.0% (Actual: 3 goals)
    - [🟢 HIT] **Exact Goals: 3**: expected 22.1% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.2% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.0% (Actual: 3 goals)

### 2026-08-08: AZ Alkmaar vs ADO Den Haag (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 70.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (13.4%), [🔴 MISS] 3-0 (13.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 92.9% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 45.1% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 0 away goals)
    - [🔴 MISS] **Goal Range 4-6**: expected 39.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 36.7% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.6% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.7% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.9% (Actual: 2 goals)

### 2026-08-08: Dinamo Bucuresti vs FC Voluntari (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.4%), [🔴 MISS] 3-0 (12.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.6% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 45.0% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.6% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 50.9% (Actual: BTTS-No)
    - [🟢 HIT] **Goal Range 4-6**: expected 38.0% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 35.7% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 31.0% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.3% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 18.5% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.5% (Actual: 4 goals)

### 2026-08-08: Farul Constanta vs Csikszereda (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.46 -> 🟢 WON (Expected prob: 70.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (14.8%), [🔴 MISS] 3-0 (13.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.1% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 45.2% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.8% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 2 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.8% (Actual: BTTS-Yes)
    - [🟢 HIT] **Goal Range 4-6**: expected 39.9% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.7% (Actual: 5 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 32.1% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.8% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.9% (Actual: 5 goals)
    - [🟢 HIT] **Exact Goals: 5**: expected 13.2% (Actual: 5 goals)

### 2026-08-08: Ceara vs Ponte Preta (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 70.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (13.4%), [🔴 MISS] 2-1 (13.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.6% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.6% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.0% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.1% (Actual: BTTS-No)
    - [🔴 MISS] **Goal Range 4-6**: expected 38.2% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 35.9% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.6% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.5% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.6% (Actual: 2 goals)

### 2026-08-08: Ross County vs Montrose (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.4%), [🟢 HIT] 2-1 (13.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.8% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.7% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.0% (Actual: 1 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 50.1% (Actual: BTTS-Yes)
    - [🔴 MISS] **Goal Range 4-6**: expected 38.9% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.6% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.7% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.7% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.9% (Actual: 3 goals)

### 2026-08-08: Valerenga vs Bodo/Glimt (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.49 -> 🟢 WON (Expected prob: 69.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 32.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (18.3%), [🔴 MISS] 0-1 (16.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 87.1% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.5% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.8% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.0% (Actual: 1 home goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.7% (Actual: BTTS-Yes)
    - [🔴 MISS] **Goal Range 4-6**: expected 37.3% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 30.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.0% (Actual: 3 goals)
    - [🟢 HIT] **Exact Goals: 3**: expected 22.0% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.3% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.2% (Actual: 3 goals)

### 2026-08-08: Viking vs Sarpsborg 08 FF (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.39 -> 🟢 WON (Expected prob: 68.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.4%), [🔴 MISS] 1-0 (13.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.7% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 40.9% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 1 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.6% (Actual: BTTS-Yes)
    - [🔴 MISS] **Goal Range 4-6**: expected 36.6% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 35.0% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 30.1% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.4% (Actual: 3 goals)
    - [🟢 HIT] **Exact Goals: 3**: expected 22.1% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.2% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 11.9% (Actual: 3 goals)

### 2026-08-08: St. Truiden vs Lommel United (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.58 -> 🔴 LOST (Expected prob: 67.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.8%), [🔴 MISS] 1-0 (14.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.8% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 39.2% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.9% (Actual: 1 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.9% (Actual: BTTS-Yes)
    - [🔴 MISS] **Goal Range 4-6**: expected 35.2% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 29.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.7% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.3% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 17.8% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 11.4% (Actual: 2 goals)

### 2026-08-08: Jerv vs Vidar (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 77.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.3% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 4-0 (12.6%), [🔴 MISS] 3-0 (12.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.5% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 48.4% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.0% (Actual: 0 away goals)
    - [🟢 HIT] **Goal Range 4-6**: expected 36.7% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 35.8% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 30.1% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.8% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.1% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 18.2% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.0% (Actual: 4 goals)

### 2026-08-08: Spartak Trnava vs Dukla Banska Bystrica (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (14.2%), [🟢 HIT] 3-0 (13.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.3% (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.7% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.1% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.1% (Actual: BTTS-No)
    - [🔴 MISS] **Goal Range 4-6**: expected 38.0% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.1% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.0% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.5% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.5% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.5% (Actual: 3 goals)

### 2026-08-08: The Strongest vs Independiente Petrolero (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🔴 LOST (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.0%), [🔴 MISS] 3-0 (12.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 93.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 46.2% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.9% (Actual: 2 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 51.0% (Actual: BTTS-Yes)
    - [🔴 MISS] **Goal Range 4-6**: expected 38.4% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.5% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.2% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.3% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.6% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.6% (Actual: 3 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 3 |
- 2026-07-19 `POSTPONED` `WATCHLIST_NO_ODDS` — FC Levadia Tallinn vs Tammeka (verified_disposition); excluded from win/loss/ROI
- 2026-07-25 `POSTPONED` `WATCHLIST_NO_ODDS` — Coquimbo Unido vs Universidad de Concepcion (verified_disposition); excluded from win/loss/ROI
- 2026-07-26 `POSTPONED` `SKIPPED_VETO` — Super Nova vs Riga (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- 2026-08-08 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Belshina vs Dinamo Minsk -> AWAY @ 1.32 (pending_or_unmatched_result); keys=['belshina', 'belshinab']/['dinamomin']

## Ambiguous result examples

- none

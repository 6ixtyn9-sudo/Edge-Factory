# Edge Factory — Recent picks audit (2026-07-08 to 2026-08-06)

## Overall

- archived pick rows: 140
- archived pick dates: 30
- immutable morning-baseline rows: 92
- verified official late-slate additions: 28
- regular-ledger-only legacy rows: 20
- unsafe regular ledgers ignored: 3
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 131
- eligible prior 1x2 picks: 134
- pending/unmatched result picks: 0
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 6
- ambiguous result picks: 0
- wins: 100
- hit rate: 0.763359
- priced picks: 126
- ROI: 0.012921

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-06
- same-day rows excluded: 6

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 89 / 131 matches (67.9%)
- **Both Teams to Score (BTTS)**: occurred in 63 / 131 matches (48.1%)
- **Selected Team Over 1.5 Goals**: occurred in 97 / 131 matches (74.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 44
- **Total Hits**: 28
- **Overall Hit Rate**: 63.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=1, hits=1, hit_rate=100.0%
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=9, hits=5, hit_rate=55.6%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **398** | scored: 398

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 35 | 35 | 34 | 97.1% | 96.0% | +1.1% | 0.026828 |
| `btts_yes` | 34 | 34 | 17 | 50.0% | 51.1% | -1.1% | 0.249576 |
| `exact_4` | 27 | 27 | 10 | 37.0% | 17.2% | +19.9% | 0.274769 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `away_under_25` | 25 | 25 | 23 | 92.0% | 90.1% | +1.9% | 0.077988 |
| `exact_2` | 24 | 24 | 5 | 20.8% | 24.5% | -3.7% | 0.166543 |
| `match_over_35` | 24 | 24 | 14 | 58.3% | 40.9% | +17.4% | 0.297002 |
| `goal_range_4_6` | 23 | 23 | 12 | 52.2% | 35.3% | +16.8% | 0.284586 |
| `exact_3` | 22 | 22 | 1 | 4.5% | 22.2% | -17.7% | 0.074729 |
| `home_over_05` | 21 | 21 | 21 | 100.0% | 85.9% | +14.1% | 0.021872 |
| `match_over_25` | 20 | 20 | 12 | 60.0% | 51.7% | +8.3% | 0.298443 |
| `goal_range_4_5` | 19 | 19 | 9 | 47.4% | 29.9% | +17.4% | 0.28764 |
| `exact_5` | 17 | 17 | 2 | 11.8% | 12.3% | -0.5% | 0.107872 |
| `match_over_45` | 17 | 17 | 4 | 23.5% | 26.7% | -3.1% | 0.207887 |
| `btts_no` | 16 | 16 | 7 | 43.8% | 54.4% | -10.7% | 0.252496 |
| `home_under_35` | 16 | 16 | 12 | 75.0% | 94.1% | -19.1% | 0.221023 |
| `match_over_15` | 8 | 8 | 7 | 87.5% | 85.7% | +1.8% | 0.122786 |
| `away_under_15` | 5 | 5 | 4 | 80.0% | 80.9% | -0.9% | 0.15875 |
| `away_over_05` | 4 | 4 | 3 | 75.0% | 84.9% | -9.9% | 0.192942 ⚠️low-n |
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
| hybrid_cohort | 116 | 65 | 56.0% | 49.6% | +6.4% | 0.18183 |
| model | 19 | 10 | 52.6% | 50.4% | +2.3% | 0.228447 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 49 | 15.3% | 28.6% | +13.2% |
| 0.2-0.3 | 78 | 24.4% | 21.8% | -2.6% |
| 0.3-0.4 | 48 | 34.7% | 56.2% | +21.6% |
| 0.4-0.5 | 55 | 46.1% | 43.6% | -2.5% |
| 0.5-0.6 | 40 | 53.5% | 35.0% | -18.5% |
| 0.6-0.7 | 5 | 65.3% | 100.0% | +34.7% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 47 | 84.6% | 91.5% | +6.8% |
| 0.9-1.0 | 72 | 94.6% | 90.3% | -4.3% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=43, MAE=1.244419 goals, bias=-0.297907 (realized − promised), promised avg 3.809535 vs realized 3.511628

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 86 | 14.3% | 7.0% | -7.4% | 0.071691 |
| Away Over 1.5 | 43 | 22.0% | 25.6% | +3.5% | 0.158215 |
| BTTS-Yes | 43 | 39.8% | 48.8% | +9.0% | 0.257992 |
| Home Over 1.5 | 43 | 75.3% | 65.1% | -10.2% | 0.195267 |
| Over 2.5 | 43 | 73.8% | 67.4% | -6.3% | 0.22536 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 31 | 8.6% | 16.1% | +7.5% |
| 0.1-0.2 | 95 | 13.6% | 8.4% | -5.2% |
| 0.2-0.3 | 3 | 20.9% | 0.0% | -20.9% |
| 0.3-0.4 | 24 | 37.7% | 54.2% | +16.4% |
| 0.4-0.5 | 19 | 42.5% | 42.1% | -0.4% |
| 0.6-0.7 | 9 | 67.6% | 66.7% | -1.0% |
| 0.7-0.8 | 31 | 74.5% | 67.7% | -6.7% |
| 0.8-0.9 | 33 | 86.6% | 78.8% | -7.8% |
| 0.9-1.0 | 13 | 91.9% | 61.5% | -30.4% |

## By rule

- `2way-unanimous avg_p>=70`: settled=63, wins=49, hit_rate=0.777778, ROI=0.032254
- `3way-unanimous avg_p>=65`: settled=45, wins=31, hit_rate=0.688889, ROI=-0.068068
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=13, wins=11, hit_rate=0.846154, ROI=-0.003846

## By bucket

- `CAUTION`: settled=33, wins=18, hit_rate=0.545455, ROI=-0.13
- `SKIPPED_VETO`: settled=74, wins=61, hit_rate=0.824324, ROI=0.064432
- `WATCHLIST_NO_ODDS`: settled=5, wins=4, hit_rate=0.8, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=19, wins=17, hit_rate=0.894737, ROI=0.060526

## By odds source

- `UNKNOWN`: settled=5, wins=4, hit_rate=0.8, ROI=None
- `betexplorer_odds`: settled=69, wins=57, hit_rate=0.826087, ROI=0.072754
- `bzzoiro_odds`: settled=31, wins=25, hit_rate=0.806452, ROI=0.147677
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=18, wins=8, hit_rate=0.444444, ROI=-0.428889
- `zulubet`: settled=6, wins=5, hit_rate=0.833333, ROI=0.088333

## By odds match method

- `alias_fuzzy`: settled=8, wins=5, hit_rate=0.625, ROI=-0.23
- `betexplorer`: settled=69, wins=57, hit_rate=0.826087, ROI=0.072754
- `exact`: settled=41, wins=28, hit_rate=0.682927, ROI=-0.031756
- `fallback`: settled=8, wins=6, hit_rate=0.75, ROI=-0.03125
- `none`: settled=5, wins=4, hit_rate=0.8, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 69 | 57 | 0.826087 | 69 | 0.072754 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 23 | 20 | 0.869565 | 23 | 0.279043 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 18 | 8 | 0.444444 | 18 | -0.428889 |
| Source fallback (`SOURCE_FALLBACK`) | 8 | 6 | 0.75 | 8 | -0.03125 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 8 | 5 | 0.625 | 8 | -0.23 |
| No usable price (`UNMATCHED`) | 5 | 4 | 0.8 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 74 | 61 | 0.824324 | 74 | 0.064432 |
| **trusted evidence only** | 61 | 51 | 0.836066 | 61 | 0.086525 |
| **soft evidence only** | 13 | 10 | 0.769231 | 13 | -0.039231 |
| evidence: BETEXPLORER_RESCUE | 46 | 39 | 0.847826 | 46 | 0.086522 |
| evidence: BZZOIRO_PRIMARY | 15 | 12 | 0.8 | 15 | 0.086533 |
| evidence: SCOUTINGSTATS_SOLE | 5 | 3 | 0.6 | 5 | -0.282 |
| evidence: SOURCE_FALLBACK | 4 | 4 | 1.0 | 4 | 0.2975 |
| evidence: SUSPECT_ALIAS_FUZZY | 4 | 3 | 0.75 | 4 | -0.0725 |
| odds band: <1.50 | 67 | 56 | 0.835821 | 67 | 0.047134 |
| odds band: 1.50-2.00 | 6 | 4 | 0.666667 | 6 | 0.071667 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.17 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 5 | 3 | 0.6 | 5 | -0.334 |
| veto reason: context VETO in ['odds_band'] | 34 | 27 | 0.794118 | 34 | 0.052059 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.331 |
| veto reason: context VETO in ['team_a'] | 4 | 4 | 1.0 | 4 | 0.47 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.41 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h'] | 6 | 5 | 0.833333 | 6 | 0.004167 |
| veto reason: short-odds away favourite 1.05 | 1 | 1 | 1.0 | 1 | 0.05 |
| veto reason: short-odds away favourite 1.07 | 1 | 1 | 1.0 | 1 | 0.07 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.19 | 1 | 1 | 1.0 | 1 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| contrast CAUTION: BETEXPLORER_RESCUE | 12 | 8 | 0.666667 | 12 | 0.038333 |
| contrast CAUTION: BZZOIRO_PRIMARY | 7 | 7 | 1.0 | 7 | 0.7 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 10 | 2 | 0.2 | 10 | -0.697 |
| contrast CAUTION: SOURCE_FALLBACK | 2 | 1 | 0.5 | 2 | -0.34 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 105 | 87 | 0.828571 | 100 | 0.11188 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 8 | 5 | 0.625 | 8 | -0.23 | 0 | None |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 18 | 8 | 0.444444 | 18 | -0.428889 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-05: Panathinaikos vs CSKA 1948 (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.17 -> 🔴 LOST (Expected prob: 74.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.5% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (12.2%), [🔴 MISS] 1-0 (11.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.2% (Actual: BTTS-Yes)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.1% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 50.1% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.8% (Actual: 1 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.8% (Actual: BTTS-Yes)
    - [🔴 MISS] **Goal Range 4-6**: expected 38.3% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 35.9% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.2% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.3% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.6% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.6% (Actual: 2 goals)

### 2026-08-05: Fenerbahçe vs Sturm Graz (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (12.6%), [🔴 MISS] 1-0 (12.6%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.7% (Actual: BTTS-No)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 92.5% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.8% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 50.3% (Actual: BTTS-No)
    - [🔴 MISS] **Goal Range 4-6**: expected 39.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 37.6% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.9% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.5% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.8% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 13.1% (Actual: 2 goals)

### 2026-08-05: Spartak Moscow vs FC Orenburg (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.32 -> 🟢 WON (Expected prob: 77.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.5% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.1% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.7%), [🔴 MISS] 4-0 (11.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 50.0% (Actual: BTTS-Yes)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.4% (Actual: 5 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 49.2% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 1 away goals)
    - [🟢 HIT] **Goal Range 4-6**: expected 37.8% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.1% (Actual: 6 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 30.9% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.7% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.5% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.4% (Actual: 6 goals)

### 2026-08-05: Lazio vs Ostia Mare (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.02 -> 🟢 WON (Expected prob: 81.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 95.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (20.3%), [🔴 MISS] 3-1 (14.1%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 58.4% (Actual: BTTS-No)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.8% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 34.1% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 0 away goals)
    - [🔴 MISS] **Home Team Under 3.5 Goals**: expected 92.2% (Actual: 4 home goals)
    - [🟢 HIT] **Goal Range 4-6**: expected 31.0% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 26.2% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 2**: expected 22.8% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.4% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 16.5% (Actual: 4 goals)

### 2026-08-05: Napoli vs Osasuna (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🟢 WON (Expected prob: 68.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.4%), [🔴 MISS] 1-0 (13.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.1% (Actual: BTTS-Yes)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.9% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 40.7% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.7% (Actual: 1 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.9% (Actual: BTTS-Yes)
    - [🔴 MISS] **Goal Range 4-6**: expected 35.6% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 29.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.3% (Actual: 3 goals)
    - [🟢 HIT] **Exact Goals: 3**: expected 22.2% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 17.9% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 11.5% (Actual: 3 goals)

### 2026-08-05: Arsenal vs Real Betis (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.63 -> 🔴 LOST (Expected prob: 67.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.8%), [🔴 MISS] 1-0 (14.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.9% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 39.2% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 96.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.6% (Actual: 3 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Goal Range 4-6**: expected 35.0% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 29.0% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.7% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.3% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 17.7% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 11.3% (Actual: 4 goals)


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

# Edge Factory — Recent picks audit (2026-07-08 to 2026-08-06)

## Overall

- archived pick rows: 134
- archived pick dates: 30
- immutable morning-baseline rows: 92
- verified official late-slate additions: 24
- regular-ledger-only legacy rows: 18
- unsafe regular ledgers ignored: 3
- settled picks: 127
- eligible prior 1x2 picks: 130
- pending/unmatched result picks: 0
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 6
- ambiguous result picks: 0
- wins: 97
- hit rate: 0.76378
- priced picks: 122
- ROI: 0.012852

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-06
- same-day rows excluded: 4

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 85 / 127 matches (66.9%)
- **Both Teams to Score (BTTS)**: occurred in 60 / 127 matches (47.2%)
- **Selected Team Over 1.5 Goals**: occurred in 94 / 127 matches (74.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 40
- **Total Hits**: 25
- **Overall Hit Rate**: 62.5%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=1, hits=1, hit_rate=100.0%
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=5, hits=2, hit_rate=40.0%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **351** | scored: 351

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 31 | 31 | 30 | 96.8% | 95.7% | +1.1% | 0.030246 |
| `btts_yes` | 30 | 30 | 14 | 46.7% | 51.2% | -4.5% | 0.243982 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `exact_2` | 23 | 23 | 5 | 21.7% | 24.6% | -2.8% | 0.171524 |
| `exact_4` | 23 | 23 | 8 | 34.8% | 17.1% | +17.7% | 0.259942 |
| `away_under_25` | 22 | 22 | 21 | 95.5% | 89.4% | +6.0% | 0.046438 |
| `match_over_35` | 20 | 20 | 11 | 55.0% | 41.0% | +14.0% | 0.294998 |
| `exact_3` | 19 | 19 | 0 | 0.0% | 22.2% | -22.2% | 0.049443 |
| `goal_range_4_6` | 19 | 19 | 9 | 47.4% | 35.4% | +11.9% | 0.270188 |
| `match_over_25` | 19 | 19 | 11 | 57.9% | 52.5% | +5.4% | 0.292675 |
| `home_over_05` | 17 | 17 | 17 | 100.0% | 85.3% | +14.7% | 0.023309 |
| `goal_range_4_5` | 15 | 15 | 7 | 46.7% | 30.2% | +16.5% | 0.282347 |
| `home_under_35` | 15 | 15 | 12 | 80.0% | 94.2% | -14.2% | 0.179139 |
| `btts_no` | 14 | 14 | 7 | 50.0% | 54.6% | -4.6% | 0.247466 |
| `exact_5` | 14 | 14 | 2 | 14.3% | 12.4% | +1.9% | 0.128024 |
| `match_over_45` | 14 | 14 | 3 | 21.4% | 27.1% | -5.6% | 0.207168 |
| `match_over_15` | 8 | 8 | 7 | 87.5% | 85.7% | +1.8% | 0.122786 |
| `away_over_05` | 4 | 4 | 3 | 75.0% | 84.9% | -9.9% | 0.192942 ⚠️low-n |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `home_under_25` | 4 | 4 | 3 | 75.0% | 89.6% | -14.6% | 0.208021 ⚠️low-n |
| `away_under_15` | 3 | 3 | 3 | 100.0% | 81.1% | +18.9% | 0.035603 ⚠️low-n |
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
| hybrid_cohort | 79 | 44 | 55.7% | 49.6% | +6.1% | 0.166515 |
| model | 9 | 4 | 44.4% | 52.8% | -8.4% | 0.095335 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 42 | 15.4% | 28.6% | +13.2% |
| 0.2-0.3 | 68 | 24.4% | 19.1% | -5.3% |
| 0.3-0.4 | 40 | 34.6% | 52.5% | +17.9% |
| 0.4-0.5 | 51 | 46.2% | 41.2% | -5.0% |
| 0.5-0.6 | 36 | 53.4% | 36.1% | -17.3% |
| 0.6-0.7 | 5 | 65.3% | 100.0% | +34.7% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 43 | 84.8% | 93.0% | +8.2% |
| 0.9-1.0 | 62 | 94.5% | 91.9% | -2.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=39, MAE=1.285128 goals, bias=-0.371282 (realized − promised), promised avg 3.807179 vs realized 3.435897

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 78 | 14.3% | 7.7% | -6.6% | 0.076687 |
| Away Over 1.5 | 39 | 23.3% | 25.6% | +2.3% | 0.152779 |
| BTTS-Yes | 39 | 39.7% | 46.2% | +6.4% | 0.253393 |
| Home Over 1.5 | 39 | 73.9% | 64.1% | -9.8% | 0.195762 |
| Over 2.5 | 39 | 73.8% | 64.1% | -9.7% | 0.24096 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 28 | 8.5% | 14.3% | +5.8% |
| 0.1-0.2 | 87 | 13.6% | 9.2% | -4.4% |
| 0.2-0.3 | 2 | 21.1% | 0.0% | -21.1% |
| 0.3-0.4 | 23 | 37.7% | 52.2% | +14.5% |
| 0.4-0.5 | 16 | 42.7% | 37.5% | -5.2% |
| 0.6-0.7 | 8 | 67.5% | 62.5% | -5.0% |
| 0.7-0.8 | 28 | 74.5% | 64.3% | -10.2% |
| 0.8-0.9 | 31 | 86.6% | 80.6% | -6.0% |
| 0.9-1.0 | 11 | 91.7% | 54.5% | -37.2% |

## By rule

- `2way-unanimous avg_p>=70`: settled=61, wins=47, hit_rate=0.770492, ROI=0.027421
- `3way-unanimous avg_p>=65`: settled=43, wins=30, hit_rate=0.697674, ROI=-0.064643
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=13, wins=11, hit_rate=0.846154, ROI=-0.003846

## By bucket

- `CAUTION`: settled=32, wins=17, hit_rate=0.53125, ROI=-0.144062
- `SKIPPED_VETO`: settled=71, wins=59, hit_rate=0.830986, ROI=0.070817
- `WATCHLIST_NO_ODDS`: settled=5, wins=4, hit_rate=0.8, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=19, wins=17, hit_rate=0.894737, ROI=0.060526

## By odds source

- `UNKNOWN`: settled=5, wins=4, hit_rate=0.8, ROI=None
- `betexplorer_odds`: settled=68, wins=56, hit_rate=0.823529, ROI=0.063235
- `bzzoiro_odds`: settled=30, wins=25, hit_rate=0.833333, ROI=0.185933
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=18, wins=8, hit_rate=0.444444, ROI=-0.428889
- `zulubet`: settled=4, wins=3, hit_rate=0.75, ROI=0.0475

## By odds match method

- `alias_fuzzy`: settled=8, wins=5, hit_rate=0.625, ROI=-0.23
- `betexplorer`: settled=68, wins=56, hit_rate=0.823529, ROI=0.063235
- `exact`: settled=40, wins=28, hit_rate=0.7, ROI=-0.00755
- `fallback`: settled=6, wins=4, hit_rate=0.666667, ROI=-0.098333
- `none`: settled=5, wins=4, hit_rate=0.8, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 68 | 56 | 0.823529 | 68 | 0.063235 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 22 | 20 | 0.909091 | 22 | 0.337182 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 18 | 8 | 0.444444 | 18 | -0.428889 |
| Source fallback (`SOURCE_FALLBACK`) | 6 | 4 | 0.666667 | 6 | -0.098333 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 8 | 5 | 0.625 | 8 | -0.23 |
| No usable price (`UNMATCHED`) | 5 | 4 | 0.8 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 71 | 59 | 0.830986 | 71 | 0.070817 |
| **trusted evidence only** | 59 | 50 | 0.847458 | 59 | 0.094203 |
| **soft evidence only** | 12 | 9 | 0.75 | 12 | -0.044167 |
| evidence: BETEXPLORER_RESCUE | 45 | 38 | 0.844444 | 45 | 0.072444 |
| evidence: BZZOIRO_PRIMARY | 14 | 12 | 0.857143 | 14 | 0.164143 |
| evidence: SCOUTINGSTATS_SOLE | 5 | 3 | 0.6 | 5 | -0.282 |
| evidence: SOURCE_FALLBACK | 3 | 3 | 1.0 | 3 | 0.39 |
| evidence: SUSPECT_ALIAS_FUZZY | 4 | 3 | 0.75 | 4 | -0.0725 |
| odds band: <1.50 | 66 | 55 | 0.833333 | 66 | 0.047545 |
| odds band: 1.50-2.00 | 4 | 3 | 0.75 | 4 | 0.1775 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.17 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 5 | 3 | 0.6 | 5 | -0.334 |
| veto reason: context VETO in ['odds_band'] | 32 | 25 | 0.78125 | 32 | 0.032188 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.331 |
| veto reason: context VETO in ['team_a'] | 4 | 4 | 1.0 | 4 | 0.47 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.41 |
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
| contrast CAUTION: SOURCE_FALLBACK | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 101 | 84 | 0.831683 | 96 | 0.115917 | 0 | None |
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

# Edge Factory — Recent picks audit (2026-07-10 to 2026-08-08)

## Overall

- archived pick rows: 161
- archived pick dates: 30
- immutable morning-baseline rows: 90
- verified official late-slate additions: 27
- regular-ledger-only legacy rows: 44
- unsafe regular ledgers ignored: 3
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 141
- eligible prior 1x2 picks: 144
- pending/unmatched result picks: 0
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 6
- ambiguous result picks: 0
- wins: 111
- hit rate: 0.787234
- priced picks: 136
- ROI: 0.041824

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-08
- same-day rows excluded: 17

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 93 / 141 matches (66.0%)
- **Both Teams to Score (BTTS)**: occurred in 66 / 141 matches (46.8%)
- **Selected Team Over 1.5 Goals**: occurred in 105 / 141 matches (74.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 57
- **Total Hits**: 39
- **Overall Hit Rate**: 68.4%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=2, hits=2, hit_rate=100.0%
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `home_over_05`: recommended=8, hits=8, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **539** | scored: 539

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 47 | 47 | 45 | 95.7% | 96.3% | -0.6% | 0.038872 |
| `exact_4` | 40 | 40 | 11 | 27.5% | 17.6% | +9.9% | 0.212413 |
| `btts_yes` | 38 | 38 | 19 | 50.0% | 50.9% | -0.9% | 0.248905 |
| `match_over_35` | 37 | 37 | 18 | 48.6% | 42.3% | +6.3% | 0.283823 |
| `away_under_25` | 36 | 36 | 34 | 94.4% | 90.9% | +3.5% | 0.055913 |
| `goal_range_4_6` | 36 | 36 | 16 | 44.4% | 36.3% | +8.1% | 0.264895 |
| `goal_range_4_5` | 32 | 32 | 11 | 34.4% | 30.3% | +4.0% | 0.23608 |
| `home_over_05` | 32 | 32 | 32 | 100.0% | 87.6% | +12.4% | 0.017223 |
| `exact_5` | 30 | 30 | 3 | 10.0% | 12.4% | -2.4% | 0.094287 |
| `match_over_45` | 30 | 30 | 7 | 23.3% | 26.6% | -3.3% | 0.202423 |
| `match_over_25` | 28 | 28 | 15 | 53.6% | 47.7% | +5.9% | 0.278241 |
| `exact_3` | 27 | 27 | 1 | 3.7% | 22.2% | -18.5% | 0.070033 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `btts_no` | 24 | 24 | 13 | 54.2% | 53.6% | +0.6% | 0.249445 |
| `exact_2` | 24 | 24 | 5 | 20.8% | 24.5% | -3.7% | 0.166543 |
| `home_under_35` | 17 | 17 | 13 | 76.5% | 94.0% | -17.5% | 0.208375 |
| `match_over_15` | 8 | 8 | 7 | 87.5% | 85.7% | +1.8% | 0.122786 |
| `away_over_05` | 5 | 5 | 4 | 80.0% | 85.2% | -5.2% | 0.157967 |
| `away_under_15` | 5 | 5 | 4 | 80.0% | 80.9% | -0.9% | 0.15875 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_6_plus` | 4 | 4 | 0 | 0.0% | 21.5% | -21.5% | 0.05033 ⚠️low-n |
| `home_under_25` | 4 | 4 | 3 | 75.0% | 89.6% | -14.6% | 0.208021 ⚠️low-n |
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
| hybrid_cohort | 248 | 120 | 48.4% | 48.8% | -0.4% | 0.146189 |
| model | 28 | 16 | 57.1% | 45.4% | +11.8% | 0.298173 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 78 | 15.5% | 21.8% | +6.3% |
| 0.2-0.3 | 96 | 24.7% | 20.8% | -3.8% |
| 0.3-0.4 | 80 | 34.9% | 45.0% | +10.1% |
| 0.4-0.5 | 69 | 45.8% | 40.6% | -5.2% |
| 0.5-0.6 | 52 | 53.1% | 40.4% | -12.7% |
| 0.6-0.7 | 5 | 65.3% | 100.0% | +34.7% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 51 | 84.8% | 92.2% | +7.3% |
| 0.9-1.0 | 104 | 94.5% | 92.3% | -2.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=56, MAE=1.374464 goals, bias=-0.434821 (realized − promised), promised avg 3.809821 vs realized 3.375

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 112 | 14.2% | 8.9% | -5.3% | 0.084365 |
| Away Over 1.5 | 56 | 21.9% | 25.0% | +3.1% | 0.138223 |
| BTTS-Yes | 56 | 40.0% | 42.9% | +2.8% | 0.248876 |
| Home Over 1.5 | 56 | 75.4% | 64.3% | -11.1% | 0.1933 |
| Over 2.5 | 56 | 73.9% | 62.5% | -11.4% | 0.248495 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 41 | 8.5% | 14.6% | +6.1% |
| 0.1-0.2 | 123 | 13.5% | 8.9% | -4.6% |
| 0.2-0.3 | 4 | 20.8% | 25.0% | +4.2% |
| 0.3-0.4 | 29 | 37.7% | 55.2% | +17.5% |
| 0.4-0.5 | 27 | 42.5% | 29.6% | -12.9% |
| 0.6-0.7 | 11 | 67.4% | 63.6% | -3.8% |
| 0.7-0.8 | 41 | 74.6% | 61.0% | -13.7% |
| 0.8-0.9 | 43 | 86.6% | 76.7% | -9.9% |
| 0.9-1.0 | 17 | 91.7% | 70.6% | -21.1% |

## By rule

- `2way-unanimous avg_p>=70`: settled=71, wins=58, hit_rate=0.816901, ROI=0.083627
- `3way-unanimous avg_p>=65`: settled=49, wins=35, hit_rate=0.714286, ROI=-0.046771
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=11, wins=9, hit_rate=0.818182, ROI=-0.04

## By bucket

- `CAUTION`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.089697
- `SKIPPED_VETO`: settled=82, wins=69, hit_rate=0.841463, ROI=0.084
- `WATCHLIST_NO_ODDS`: settled=5, wins=4, hit_rate=0.8, ROI=None
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=1, wins=1, hit_rate=1.0, ROI=0.2
- `WATCHLIST_UNKNOWN_CTX`: settled=20, wins=18, hit_rate=0.9, ROI=0.078

## By odds source

- `UNKNOWN`: settled=5, wins=4, hit_rate=0.8, ROI=None
- `betexplorer_odds`: settled=69, wins=58, hit_rate=0.84058, ROI=0.088986
- `bzzoiro_odds`: settled=37, wins=31, hit_rate=0.837838, ROI=0.166432
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=21, wins=11, hit_rate=0.52381, ROI=-0.332381
- `zulubet`: settled=7, wins=6, hit_rate=0.857143, ROI=0.164286

## By odds match method

- `alias_fuzzy`: settled=8, wins=5, hit_rate=0.625, ROI=-0.23
- `betexplorer`: settled=69, wins=58, hit_rate=0.84058, ROI=0.088986
- `exact`: settled=50, wins=37, hit_rate=0.74, ROI=0.02036
- `fallback`: settled=9, wins=7, hit_rate=0.777778, ROI=0.041111
- `none`: settled=5, wins=4, hit_rate=0.8, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 69 | 58 | 0.84058 | 69 | 0.088986 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 29 | 26 | 0.896552 | 29 | 0.275793 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 21 | 11 | 0.52381 | 21 | -0.332381 |
| Source fallback (`SOURCE_FALLBACK`) | 9 | 7 | 0.777778 | 9 | 0.041111 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 8 | 5 | 0.625 | 8 | -0.23 |
| No usable price (`UNMATCHED`) | 5 | 4 | 0.8 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 82 | 69 | 0.841463 | 82 | 0.084 |
| **trusted evidence only** | 66 | 56 | 0.848485 | 66 | 0.094515 |
| **soft evidence only** | 16 | 13 | 0.8125 | 16 | 0.040625 |
| evidence: BETEXPLORER_RESCUE | 47 | 40 | 0.851064 | 47 | 0.083191 |
| evidence: BZZOIRO_PRIMARY | 19 | 16 | 0.842105 | 19 | 0.122526 |
| evidence: SCOUTINGSTATS_SOLE | 7 | 5 | 0.714286 | 7 | -0.124286 |
| evidence: SOURCE_FALLBACK | 5 | 5 | 1.0 | 5 | 0.362 |
| evidence: SUSPECT_ALIAS_FUZZY | 4 | 3 | 0.75 | 4 | -0.0725 |
| odds band: <1.50 | 74 | 63 | 0.851351 | 74 | 0.062946 |
| odds band: 1.50-2.00 | 7 | 5 | 0.714286 | 7 | 0.15 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.17 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 5 | 3 | 0.6 | 5 | -0.334 |
| veto reason: context VETO in ['odds_band'] | 34 | 27 | 0.794118 | 34 | 0.054706 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 4 | 4 | 1.0 | 4 | 0.33575 |
| veto reason: context VETO in ['team_a'] | 5 | 5 | 1.0 | 5 | 0.4 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.41 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: context VETO in ['team_h'] | 10 | 9 | 0.9 | 10 | 0.1315 |
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
| contrast CAUTION: BETEXPLORER_RESCUE | 11 | 8 | 0.727273 | 11 | 0.132727 |
| contrast CAUTION: BZZOIRO_PRIMARY | 8 | 8 | 1.0 | 8 | 0.65375 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 10 | 2 | 0.2 | 10 | -0.697 |
| contrast CAUTION: SOURCE_FALLBACK | 2 | 1 | 0.5 | 2 | -0.34 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 112 | 95 | 0.848214 | 107 | 0.135589 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 8 | 5 | 0.625 | 8 | -0.23 | 0 | None |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 21 | 11 | 0.52381 | 21 | -0.332381 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-07: Levski Sofia vs Lokomotiv Plovdiv (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🟢 WON (Expected prob: 80.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 36.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 94.2% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (17.5%), [🔴 MISS] 3-1 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.4% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.2% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 53.8% (Actual: BTTS-No)
    - [🔴 MISS] **Goal Range 4-6**: expected 35.8% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 29.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.7% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.2% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 17.9% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 11.6% (Actual: 2 goals)

### 2026-08-07: The New Saints vs Haverfordwest County (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 76.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (12.1%), [🔴 MISS] 3-0 (11.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.6% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 51.8% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.2% (Actual: BTTS-No)
    - [🔴 MISS] **Goal Range 4-6**: expected 40.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 37.8% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 32.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.8% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 19.0% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 6+**: expected 15.1% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 13.6% (Actual: 2 goals)

### 2026-08-07: Suwon Bluewings vs Gimhae City (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 71.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.5%), [🔴 MISS] 3-0 (13.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.6% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 0 away goals)
    - [🔴 MISS] **Goal Range 4-6**: expected 37.8% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 35.7% (Actual: 1 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 30.8% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.2% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.4% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.4% (Actual: 1 goals)

### 2026-08-07: Adelaide City vs Playford City Patriots (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.62 -> 🟢 WON (Expected prob: 70.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.4%), [🔴 MISS] 2-1 (13.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.8% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.8% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.4% (Actual: 0 away goals)
    - [🔴 MISS] **Goal Range 4-6**: expected 39.5% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 37.1% (Actual: 1 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 31.9% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.8% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.8% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 13.1% (Actual: 1 goals)

### 2026-08-07: Club Brugge KV vs Kortrijk (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🟢 WON (Expected prob: 75.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.0%), [🔴 MISS] 2-1 (11.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 92.6% (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 51.6% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 86.2% (Actual: 0 away goals)
    - [🔴 MISS] **Goal Range 4-6**: expected 42.1% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.1% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 33.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.9% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 19.3% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 6+**: expected 16.7% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 14.2% (Actual: 3 goals)

### 2026-08-07: Lions vs Brisbane Roar II (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 66.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.9%), [🔴 MISS] 1-0 (14.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.7% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 39.1% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.1% (Actual: 2 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.4% (Actual: BTTS-Yes)
    - [🟢 HIT] **Goal Range 4-6**: expected 35.9% (Actual: 6 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 29.6% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.7% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.2% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 18.0% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 11.6% (Actual: 6 goals)


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

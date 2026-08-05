# Edge Factory — Recent picks audit (2026-07-06 to 2026-08-04)

## Overall

- archived pick rows: 92
- archived pick dates: 26
- settled picks: 90
- eligible prior 1x2 picks: 90
- unmatched result picks: 0
- settled via shared overlay facts: 6
- ambiguous result picks: 0
- wins: 71
- hit rate: 0.788889
- priced picks: 87
- ROI: 0.052471

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-04
- same-day rows excluded: 2

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 62 / 90 matches (68.9%)
- **Both Teams to Score (BTTS)**: occurred in 46 / 90 matches (51.1%)
- **Selected Team Over 1.5 Goals**: occurred in 68 / 90 matches (75.6%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 30
- **Total Hits**: 18
- **Overall Hit Rate**: 60.0%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `btts_yes`: recommended=2, hits=1, hit_rate=50.0%
- `goal_range_2_3`: recommended=8, hits=2, hit_rate=25.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=5, hits=4, hit_rate=80.0%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **263** | scored: 263

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 26 | 26 | 25 | 96.2% | 95.3% | +0.8% | 0.035946 |
| `goal_range_2_3` | 25 | 25 | 8 | 32.0% | 46.1% | -14.1% | 0.234496 |
| `btts_yes` | 23 | 23 | 10 | 43.5% | 52.5% | -9.0% | 0.237859 |
| `exact_2` | 22 | 22 | 5 | 22.7% | 24.6% | -1.8% | 0.17663 |
| `away_under_25` | 17 | 17 | 16 | 94.1% | 88.2% | +5.9% | 0.058662 |
| `exact_4` | 16 | 16 | 6 | 37.5% | 16.9% | +20.6% | 0.280408 |
| `match_over_25` | 15 | 15 | 9 | 60.0% | 56.8% | +3.2% | 0.297849 |
| `exact_3` | 14 | 14 | 0 | 0.0% | 22.2% | -22.2% | 0.049487 |
| `match_over_35` | 14 | 14 | 8 | 57.1% | 39.7% | +17.4% | 0.305019 |
| `goal_range_4_6` | 13 | 13 | 6 | 46.2% | 34.9% | +11.2% | 0.267681 |
| `home_under_35` | 13 | 13 | 10 | 76.9% | 93.7% | -16.8% | 0.206569 |
| `home_over_05` | 12 | 12 | 12 | 100.0% | 83.9% | +16.1% | 0.027014 |
| `goal_range_4_5` | 9 | 9 | 4 | 44.4% | 30.4% | +14.1% | 0.274121 |
| `exact_5` | 8 | 8 | 1 | 12.5% | 12.8% | -0.3% | 0.115624 |
| `match_over_45` | 8 | 8 | 2 | 25.0% | 27.8% | -2.8% | 0.242338 |
| `btts_no` | 7 | 7 | 4 | 57.1% | 56.0% | +1.1% | 0.230831 |
| `match_over_15` | 6 | 6 | 5 | 83.3% | 86.8% | -3.5% | 0.153114 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `away_over_05` | 2 | 2 | 1 | 50.0% | 83.2% | -33.2% | 0.367464 ⚠️low-n |
| `goal_range_6_plus` | 2 | 2 | 0 | 0.0% | 27.1% | -27.1% | 0.075286 ⚠️low-n |
| `goal_range_7_plus` | 2 | 2 | 0 | 0.0% | 15.1% | -15.1% | 0.023681 ⚠️low-n |
| `home_under_25` | 2 | 2 | 1 | 50.0% | 87.3% | -37.3% | 0.409172 ⚠️low-n |
| `away_under_15` | 1 | 1 | 1 | 100.0% | 81.9% | +18.1% | 0.032593 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 29 | 15.6% | 31.0% | +15.5% |
| 0.2-0.3 | 54 | 24.3% | 18.5% | -5.7% |
| 0.3-0.4 | 24 | 34.1% | 58.3% | +24.2% |
| 0.4-0.5 | 40 | 46.1% | 37.5% | -8.6% |
| 0.5-0.6 | 28 | 53.6% | 35.7% | -17.9% |
| 0.6-0.7 | 5 | 65.3% | 100.0% | +34.7% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 33 | 85.1% | 90.9% | +5.8% |
| 0.9-1.0 | 46 | 94.4% | 89.1% | -5.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=30, MAE=1.268 goals, bias=-0.432667 (realized − promised), promised avg 3.766 vs realized 3.333333

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 60 | 14.3% | 8.3% | -6.0% | 0.082788 |
| Away Over 1.5 | 30 | 22.3% | 23.3% | +1.0% | 0.166872 |
| BTTS-Yes | 30 | 39.6% | 40.0% | +0.4% | 0.240422 |
| Home Over 1.5 | 30 | 74.8% | 66.7% | -8.2% | 0.201756 |
| Over 2.5 | 30 | 73.3% | 66.7% | -6.6% | 0.23439 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 20 | 8.6% | 15.0% | +6.4% |
| 0.1-0.2 | 68 | 13.5% | 10.3% | -3.2% |
| 0.2-0.3 | 2 | 21.1% | 0.0% | -21.1% |
| 0.3-0.4 | 19 | 37.8% | 47.4% | +9.6% |
| 0.4-0.5 | 11 | 42.7% | 27.3% | -15.4% |
| 0.6-0.7 | 6 | 67.3% | 83.3% | +16.0% |
| 0.7-0.8 | 23 | 74.5% | 65.2% | -9.3% |
| 0.8-0.9 | 22 | 86.6% | 81.8% | -4.8% |
| 0.9-1.0 | 9 | 90.8% | 44.4% | -46.4% |

## By rule

- `2way-unanimous avg_p>=70`: settled=39, wins=30, hit_rate=0.769231, ROI=0.081389
- `3way-unanimous avg_p>=65`: settled=27, wins=20, hit_rate=0.740741, ROI=-0.032037
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.176667
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=21, wins=12, hit_rate=0.571429, ROI=-0.071429
- `SKIPPED_VETO`: settled=53, wins=46, hit_rate=0.867925, ROI=0.116132
- `WATCHLIST_NO_ODDS`: settled=3, wins=2, hit_rate=0.666667, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=13, wins=11, hit_rate=0.846154, ROI=-0.006923

## By odds source

- `UNKNOWN`: settled=3, wins=2, hit_rate=0.666667, ROI=None
- `betexplorer_odds`: settled=46, wins=40, hit_rate=0.869565, ROI=0.116522
- `bzzoiro_odds`: settled=24, wins=20, hit_rate=0.833333, ROI=0.167292
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=12, wins=6, hit_rate=0.5, ROI=-0.331667
- `zulubet`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.016667

## By odds match method

- `alias_fuzzy`: settled=6, wins=3, hit_rate=0.5, ROI=-0.356667
- `betexplorer`: settled=46, wins=40, hit_rate=0.869565, ROI=0.116522
- `exact`: settled=30, wins=23, hit_rate=0.766667, ROI=0.0725
- `fallback`: settled=5, wins=3, hit_rate=0.6, ROI=-0.166
- `none`: settled=3, wins=2, hit_rate=0.666667, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 46 | 40 | 0.869565 | 46 | 0.116522 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 18 | 17 | 0.944444 | 18 | 0.341944 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 12 | 6 | 0.5 | 12 | -0.331667 |
| Source fallback (`SOURCE_FALLBACK`) | 5 | 3 | 0.6 | 5 | -0.166 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 6 | 3 | 0.5 | 6 | -0.356667 |
| No usable price (`UNMATCHED`) | 3 | 2 | 0.666667 | 0 | None |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 72 | 62 | 0.861111 | 69 | 0.154855 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 6 | 3 | 0.5 | 6 | -0.356667 | 0 | None |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 12 | 6 | 0.5 | 12 | -0.331667 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-03: FCSB vs Farul Constanta (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.81 -> 🔴 LOST (Expected prob: 66.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.9%), [🔴 MISS] 1-0 (14.3%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Goal Range 2-3**: expected 46.4% (Actual: 4 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 53.8% (Actual: BTTS-Yes)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.2% (Actual: 2 home goals)
    - [🔴 MISS] **Exact Goals: 2**: expected 24.3% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.1% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 15.1% (Actual: 4 goals)

### 2026-08-03: Halmstad vs Sirius (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.41 -> 🟢 WON (Expected prob: 79.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 81.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 32.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 89.0% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 0-3 (22.0%), [🔴 MISS] 1-2 (11.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Goal Range 2-3**: expected 47.0% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 52.0% (Actual: BTTS-No)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.0% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.0% (Actual: 2 away goals)
    - [🟢 HIT] **Exact Goals: 2**: expected 25.7% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 1**: expected 20.5% (Actual: 2 goals)

### 2026-08-03: Transinvest 2 vs Babrungas (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.19 -> 🟢 WON (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.3% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 87.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 0-3 (13.6%), [🔴 MISS] 1-2 (13.4%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Goal Range 2-3**: expected 46.9% (Actual: 1 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.1% (Actual: BTTS-No)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.6% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.0% (Actual: 1 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 53.9% (Actual: BTTS-No)
    - [🔴 MISS] **Exact Goals: 2**: expected 25.2% (Actual: 1 goals)

### 2026-08-03: Cork City vs Athlone Town (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 69.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (15.0%), [🔴 MISS] 3-0 (13.8%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Goal Range 2-3**: expected 46.6% (Actual: 5 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.6% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.7% (Actual: 2 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 50.1% (Actual: BTTS-Yes)
    - [🔴 MISS] **Exact Goals: 2**: expected 24.5% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.0% (Actual: 5 goals)

### 2026-08-03: Hammarby Talang vs Arlanda (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.3%), [🔴 MISS] 1-0 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 60.1% (Actual: BTTS-Yes)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.6% (Actual: 5 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.1% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.1% (Actual: 1 away goals)
    - [🔴 MISS] **Goal Range 2-3**: expected 44.9% (Actual: 6 goals)
    - [🟢 HIT] **Goal Range 4-6**: expected 31.8% (Actual: 6 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 26.8% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 2**: expected 22.5% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.4% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.3% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 16.8% (Actual: 6 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 10.0% (Actual: 6 goals)

### 2026-08-03: Celtic vs Dundee (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 80.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 92.6% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (18.5%), [🔴 MISS] 3-1 (14.8%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 51.9% (Actual: BTTS-No)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.5% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 37.8% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.9% (Actual: 0 away goals)
    - [🔴 MISS] **Goal Range 2-3**: expected 43.9% (Actual: 1 goals)
    - [🔴 MISS] **Goal Range 4-6**: expected 33.8% (Actual: 1 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 28.2% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.4% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 17.4% (Actual: 1 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 10.8% (Actual: 1 goals)


## Unmatched result examples

- none

## Ambiguous result examples

- none

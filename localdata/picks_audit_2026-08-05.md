# Edge Factory — Recent picks audit (2026-07-07 to 2026-08-05)

## Overall

- archived pick rows: 94
- archived pick dates: 27
- settled picks: 92
- eligible prior 1x2 picks: 92
- unmatched result picks: 0
- settled via shared overlay facts: 6 (Addendum 21)
- ambiguous result picks: 0
- wins: 73
- hit rate: 0.793478
- priced picks: 89
- ROI: 0.055899

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-05
- same-day rows excluded: 2

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 64 / 92 matches (69.6%)
- **Both Teams to Score (BTTS)**: occurred in 47 / 92 matches (51.1%)
- **Selected Team Over 1.5 Goals**: occurred in 70 / 92 matches (76.1%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 32
- **Total Hits**: 19
- **Overall Hit Rate**: 59.4%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `btts_yes`: recommended=2, hits=1, hit_rate=50.0%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=6, hits=5, hit_rate=83.3%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **287** | scored: 287

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 28 | 28 | 27 | 96.4% | 95.5% | +0.9% | 0.033423 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `btts_yes` | 25 | 25 | 11 | 44.0% | 52.1% | -8.1% | 0.239324 |
| `exact_2` | 23 | 23 | 5 | 21.7% | 24.6% | -2.8% | 0.171524 |
| `away_under_25` | 19 | 19 | 18 | 94.7% | 88.6% | +6.1% | 0.053212 |
| `exact_4` | 18 | 18 | 7 | 38.9% | 16.8% | +22.0% | 0.28756 |
| `exact_3` | 16 | 16 | 0 | 0.0% | 22.2% | -22.2% | 0.049388 |
| `match_over_25` | 16 | 16 | 10 | 62.5% | 55.6% | +6.9% | 0.304679 |
| `match_over_35` | 15 | 15 | 9 | 60.0% | 40.1% | +19.9% | 0.30448 |
| `goal_range_4_6` | 14 | 14 | 7 | 50.0% | 35.1% | +14.9% | 0.276616 |
| `home_over_05` | 14 | 14 | 14 | 100.0% | 84.1% | +15.9% | 0.026526 |
| `home_under_35` | 13 | 13 | 10 | 76.9% | 93.7% | -16.8% | 0.206569 |
| `goal_range_4_5` | 10 | 10 | 5 | 50.0% | 30.4% | +19.6% | 0.294941 |
| `btts_no` | 9 | 9 | 5 | 55.6% | 55.2% | +0.3% | 0.236462 |
| `exact_5` | 9 | 9 | 1 | 11.1% | 12.7% | -1.6% | 0.104434 |
| `match_over_45` | 9 | 9 | 2 | 22.2% | 27.7% | -5.5% | 0.223621 |
| `match_over_15` | 7 | 7 | 6 | 85.7% | 86.1% | -0.4% | 0.135941 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `away_over_05` | 2 | 2 | 1 | 50.0% | 83.2% | -33.2% | 0.367464 ⚠️low-n |
| `away_under_15` | 2 | 2 | 2 | 100.0% | 81.0% | +19.0% | 0.036228 ⚠️low-n |
| `goal_range_6_plus` | 2 | 2 | 0 | 0.0% | 27.1% | -27.1% | 0.075286 ⚠️low-n |
| `goal_range_7_plus` | 2 | 2 | 0 | 0.0% | 15.1% | -15.1% | 0.023681 ⚠️low-n |
| `home_under_25` | 2 | 2 | 1 | 50.0% | 87.3% | -37.3% | 0.409172 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored (FIX-2 + label honesty, Addendum 16): `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor (Addendum 17) · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| hybrid_cohort | 15 | 11 | 73.3% | 51.6% | +21.7% | 0.202095 |
| model | 9 | 4 | 44.4% | 52.8% | -8.4% | 0.095335 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 32 | 15.5% | 31.2% | +15.7% |
| 0.2-0.3 | 58 | 24.2% | 17.2% | -7.0% |
| 0.3-0.4 | 27 | 34.2% | 63.0% | +28.8% |
| 0.4-0.5 | 44 | 46.2% | 38.6% | -7.5% |
| 0.5-0.6 | 30 | 53.6% | 36.7% | -16.9% |
| 0.6-0.7 | 5 | 65.3% | 100.0% | +34.7% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 38 | 85.0% | 92.1% | +7.1% |
| 0.9-1.0 | 49 | 94.5% | 89.8% | -4.7% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=32, MAE=1.20625 goals, bias=-0.388125 (realized − promised), promised avg 3.794375 vs realized 3.40625

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 64 | 14.3% | 7.8% | -6.5% | 0.078769 |
| Away Over 1.5 | 32 | 21.6% | 21.9% | +0.3% | 0.157149 |
| BTTS-Yes | 32 | 39.7% | 40.6% | +0.9% | 0.240884 |
| Home Over 1.5 | 32 | 75.9% | 68.8% | -7.1% | 0.189705 |
| Over 2.5 | 32 | 73.6% | 68.8% | -4.9% | 0.222675 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 21 | 8.7% | 14.3% | +5.6% |
| 0.1-0.2 | 73 | 13.5% | 9.6% | -3.9% |
| 0.2-0.3 | 2 | 21.1% | 0.0% | -21.1% |
| 0.3-0.4 | 19 | 37.8% | 47.4% | +9.6% |
| 0.4-0.5 | 13 | 42.6% | 30.8% | -11.8% |
| 0.6-0.7 | 6 | 67.3% | 83.3% | +16.0% |
| 0.7-0.8 | 24 | 74.5% | 66.7% | -7.8% |
| 0.8-0.9 | 24 | 86.5% | 83.3% | -3.2% |
| 0.9-1.0 | 10 | 91.3% | 50.0% | -41.3% |

## By rule

- `2way-unanimous avg_p>=70`: settled=41, wins=32, hit_rate=0.780488, ROI=0.087895
- `3way-unanimous avg_p>=65`: settled=27, wins=20, hit_rate=0.740741, ROI=-0.032037
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.176667
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=21, wins=12, hit_rate=0.571429, ROI=-0.071429
- `SKIPPED_VETO`: settled=54, wins=47, hit_rate=0.87037, ROI=0.11713
- `WATCHLIST_NO_ODDS`: settled=3, wins=2, hit_rate=0.666667, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=14, wins=12, hit_rate=0.857143, ROI=0.010714

## By odds source

- `UNKNOWN`: settled=3, wins=2, hit_rate=0.666667, ROI=None
- `betexplorer_odds`: settled=46, wins=40, hit_rate=0.869565, ROI=0.116522
- `bzzoiro_odds`: settled=25, wins=21, hit_rate=0.84, ROI=0.1674
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=12, wins=6, hit_rate=0.5, ROI=-0.331667
- `zulubet`: settled=4, wins=3, hit_rate=0.75, ROI=0.0475

## By odds match method

- `alias_fuzzy`: settled=7, wins=4, hit_rate=0.571429, ROI=-0.281429
- `betexplorer`: settled=46, wins=40, hit_rate=0.869565, ROI=0.116522
- `exact`: settled=30, wins=23, hit_rate=0.766667, ROI=0.0725
- `fallback`: settled=6, wins=4, hit_rate=0.666667, ROI=-0.098333
- `none`: settled=3, wins=2, hit_rate=0.666667, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 46 | 40 | 0.869565 | 46 | 0.116522 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 18 | 17 | 0.944444 | 18 | 0.341944 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 12 | 6 | 0.5 | 12 | -0.331667 |
| Source fallback (`SOURCE_FALLBACK`) | 6 | 4 | 0.666667 | 6 | -0.098333 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 7 | 4 | 0.571429 | 7 | -0.281429 |
| No usable price (`UNMATCHED`) | 3 | 2 | 0.666667 | 0 | None |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 73 | 63 | 0.863014 | 70 | 0.156071 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 7 | 4 | 0.571429 | 7 | -0.281429 | 0 | None |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 12 | 6 | 0.5 | 12 | -0.331667 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-04: Dinamo Zagreb vs Kauno Žalgiris (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.17 -> 🟢 WON (Expected prob: 82.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 84.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 95.5% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 88.6% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 4-0 (15.9%), [🔴 MISS] 3-0 (11.4%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Goal Range 2-3**: expected 46.4% (Actual: 5 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 48.1% (Actual: BTTS-No)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.8% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.9% (Actual: BTTS-No)
    - [🔴 MISS] **Exact Goals: 2**: expected 24.3% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.1% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 15.1% (Actual: 5 goals)

### 2026-08-04: Montana vs Nesebar (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.6%), [🔴 MISS] 3-0 (13.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 81.9% (Actual: 4 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 47.0% (Actual: BTTS-Yes)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.8% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 45.5% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.0% (Actual: 1 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.0% (Actual: BTTS-Yes)
    - [🟢 HIT] **Goal Range 4-6**: expected 37.3% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.2% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 30.6% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.2% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.0% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 18.3% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 12.2% (Actual: 4 goals)


## Unmatched result examples

- none

## Ambiguous result examples

- none

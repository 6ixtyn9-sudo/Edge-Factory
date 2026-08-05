# Edge Factory — Recent picks audit (2026-07-07 to 2026-08-05)

## Overall

- archived pick rows: 136
- archived pick dates: 30
- immutable morning-baseline rows: 94
- verified official late-slate additions: 28
- regular-ledger-only legacy rows: 14
- unsafe regular ledgers ignored: 3
- settled picks: 128
- eligible prior 1x2 picks: 131
- unmatched result picks: 3
- settled via shared overlay facts: 6 (Addendum 21)
- ambiguous result picks: 0
- wins: 99
- hit rate: 0.773438
- priced picks: 123
- ROI: 0.029252

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-05
- same-day rows excluded: 5

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 87 / 128 matches (68.0%)
- **Both Teams to Score (BTTS)**: occurred in 61 / 128 matches (47.7%)
- **Selected Team Over 1.5 Goals**: occurred in 95 / 128 matches (74.2%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 38
- **Total Hits**: 24
- **Overall Hit Rate**: 63.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=1, hits=1, hit_rate=100.0%
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=3, hits=1, hit_rate=33.3%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **327** | scored: 327

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 29 | 29 | 28 | 96.6% | 95.6% | +0.9% | 0.032274 |
| `btts_yes` | 28 | 28 | 13 | 46.4% | 51.4% | -5.0% | 0.242237 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `exact_2` | 23 | 23 | 5 | 21.7% | 24.6% | -2.8% | 0.171524 |
| `exact_4` | 21 | 21 | 8 | 38.1% | 17.0% | +21.1% | 0.281371 |
| `away_under_25` | 20 | 20 | 19 | 95.0% | 89.0% | +6.0% | 0.050623 |
| `exact_3` | 19 | 19 | 0 | 0.0% | 22.2% | -22.2% | 0.049443 |
| `match_over_35` | 18 | 18 | 11 | 61.1% | 40.1% | +21.0% | 0.3011 |
| `goal_range_4_6` | 17 | 17 | 9 | 52.9% | 35.0% | +17.9% | 0.28418 |
| `match_over_25` | 17 | 17 | 11 | 64.7% | 54.4% | +10.3% | 0.311209 |
| `home_over_05` | 15 | 15 | 15 | 100.0% | 84.5% | +15.5% | 0.025388 |
| `home_under_35` | 15 | 15 | 12 | 80.0% | 94.2% | -14.2% | 0.179139 |
| `goal_range_4_5` | 13 | 13 | 7 | 53.8% | 30.0% | +23.8% | 0.310486 |
| `btts_no` | 12 | 12 | 6 | 50.0% | 55.0% | -5.0% | 0.243975 |
| `exact_5` | 12 | 12 | 2 | 16.7% | 12.3% | +4.3% | 0.146612 |
| `match_over_45` | 12 | 12 | 3 | 25.0% | 26.7% | -1.7% | 0.227251 |
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

Labels render plain-market exactly as promised, priced and scored (FIX-2 + label honesty, Addendum 16): `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor (Addendum 17) · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| hybrid_cohort | 55 | 36 | 65.5% | 49.5% | +15.9% | 0.191396 |
| model | 9 | 4 | 44.4% | 52.8% | -8.4% | 0.095335 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 38 | 15.3% | 31.6% | +16.2% |
| 0.2-0.3 | 67 | 24.3% | 19.4% | -4.9% |
| 0.3-0.4 | 33 | 34.6% | 63.6% | +29.1% |
| 0.4-0.5 | 48 | 46.1% | 41.7% | -4.4% |
| 0.5-0.6 | 33 | 53.6% | 36.4% | -17.3% |
| 0.6-0.7 | 5 | 65.3% | 100.0% | +34.7% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 43 | 84.8% | 93.0% | +8.2% |
| 0.9-1.0 | 56 | 94.6% | 91.1% | -3.5% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=37, MAE=1.251622 goals, bias=-0.288378 (realized − promised), promised avg 3.801892 vs realized 3.513514

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 74 | 14.4% | 8.1% | -6.3% | 0.080035 |
| Away Over 1.5 | 37 | 24.1% | 27.0% | +3.0% | 0.160554 |
| BTTS-Yes | 37 | 39.6% | 45.9% | +6.3% | 0.253212 |
| Home Over 1.5 | 37 | 73.1% | 64.9% | -8.2% | 0.184555 |
| Over 2.5 | 37 | 73.7% | 67.6% | -6.1% | 0.222005 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 26 | 8.4% | 15.4% | +7.0% |
| 0.1-0.2 | 83 | 13.7% | 9.6% | -4.0% |
| 0.2-0.3 | 2 | 21.1% | 0.0% | -21.1% |
| 0.3-0.4 | 23 | 37.7% | 52.2% | +14.5% |
| 0.4-0.5 | 14 | 42.9% | 35.7% | -7.2% |
| 0.6-0.7 | 8 | 67.5% | 62.5% | -5.0% |
| 0.7-0.8 | 26 | 74.3% | 69.2% | -5.1% |
| 0.8-0.9 | 29 | 86.5% | 82.8% | -3.7% |
| 0.9-1.0 | 11 | 91.7% | 54.5% | -37.2% |

## By rule

- `2way-unanimous avg_p>=70`: settled=61, wins=47, hit_rate=0.770492, ROI=0.028649
- `3way-unanimous avg_p>=65`: settled=42, wins=30, hit_rate=0.714286, ROI=-0.041829
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=33, wins=18, hit_rate=0.545455, ROI=-0.123333
- `SKIPPED_VETO`: settled=71, wins=60, hit_rate=0.84507, ROI=0.091803
- `WATCHLIST_NO_ODDS`: settled=5, wins=4, hit_rate=0.8, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=19, wins=17, hit_rate=0.894737, ROI=0.060526

## By odds source

- `UNKNOWN`: settled=5, wins=4, hit_rate=0.8, ROI=None
- `betexplorer_odds`: settled=68, wins=57, hit_rate=0.838235, ROI=0.086912
- `bzzoiro_odds`: settled=31, wins=26, hit_rate=0.83871, ROI=0.193484
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=18, wins=8, hit_rate=0.444444, ROI=-0.428889
- `zulubet`: settled=4, wins=3, hit_rate=0.75, ROI=0.0475

## By odds match method

- `alias_fuzzy`: settled=8, wins=5, hit_rate=0.625, ROI=-0.23
- `betexplorer`: settled=68, wins=57, hit_rate=0.838235, ROI=0.086912
- `exact`: settled=41, wins=29, hit_rate=0.707317, ROI=0.002878
- `fallback`: settled=6, wins=4, hit_rate=0.666667, ROI=-0.098333
- `none`: settled=5, wins=4, hit_rate=0.8, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 68 | 57 | 0.838235 | 68 | 0.086912 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 23 | 21 | 0.913043 | 23 | 0.340783 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 18 | 8 | 0.444444 | 18 | -0.428889 |
| Source fallback (`SOURCE_FALLBACK`) | 6 | 4 | 0.666667 | 6 | -0.098333 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 8 | 5 | 0.625 | 8 | -0.23 |
| No usable price (`UNMATCHED`) | 5 | 4 | 0.8 | 0 | None |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 102 | 86 | 0.843137 | 97 | 0.135649 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 8 | 5 | 0.625 | 8 | -0.23 | 0 | None |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 18 | 8 | 0.444444 | 18 | -0.428889 | 0 | None |
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

### 2026-08-04: BG Pathum United vs Aston Villa (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.2 -> 🟢 WON (Expected prob: 73.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 35.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 87.1% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 0-3 (13.8%), [🔴 MISS] 0-2 (13.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 82.5% (Actual: 4 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 85.5% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 42.6% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.4% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.1% (Actual: 1 home goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.1% (Actual: BTTS-Yes)
    - [🟢 HIT] **Goal Range 4-6**: expected 36.0% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 35.5% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 29.7% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.2% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.2% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected 18.0% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 11.7% (Actual: 4 goals)

### 2026-08-04: Newport County vs Roma (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.06 -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 4 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (15.0%), [🔴 MISS] 0-3 (15.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 87.4% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 38.8% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.1% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.7% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 80.4% (Actual: 1 home goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 55.4% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 44.6% (Actual: BTTS-Yes)
    - [🟢 HIT] **Goal Range 4-6**: expected 34.0% (Actual: 5 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected 28.3% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.5% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.4% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 17.4% (Actual: 5 goals)
    - [🟢 HIT] **Exact Goals: 5**: expected 10.9% (Actual: 5 goals)

### 2026-08-04: Carabobo FC vs Trujillanos FC (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🟢 WON (Expected prob: 65.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (17.5%), [🔴 MISS] 1-0 (14.9%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.8% (Actual: BTTS-No)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.3% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 38.6% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.5% (Actual: 0 away goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 54.2% (Actual: BTTS-No)
    - [🔴 MISS] **Goal Range 4-6**: expected 33.7% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected 28.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.6% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 3**: expected 22.4% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected 17.4% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected 10.8% (Actual: 2 goals)


## Unmatched result examples

- 2026-07-19 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — FC Levadia Tallinn vs Tammeka -> HOME @ None (unmatched_result); keys=['levadiata']/['tammeka']
- 2026-07-25 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Coquimbo Unido vs Universidad de Concepcion -> HOME @ None (unmatched_result); keys=['coquimbou']/['universid']
- 2026-07-26 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Super Nova vs Riga -> AWAY @ 1.26 (unmatched_result); keys=['supernova']/['riga']

## Ambiguous result examples

- none

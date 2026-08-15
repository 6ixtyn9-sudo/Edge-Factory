# Edge Factory — Recent picks audit (2026-07-17 to 2026-08-15)

## Overall

- archived pick rows: 258
- archived pick dates: 30
- immutable morning-baseline rows: 162
- verified official late-slate additions: 30
- regular-ledger-only legacy rows: 66
- unsafe regular ledgers ignored: 4
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 224
- eligible prior 1x2 picks: 230
- pending/unmatched result picks: 3
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 5
- ambiguous result picks: 0
- wins: 158
- hit rate: +70.5%
- priced picks: 214
- ROI: -5.1%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-15
- same-day rows excluded: 28

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 146 / 224 matches (65.2%)
- **Both Teams to Score (BTTS)**: occurred in 119 / 224 matches (53.1%)
- **Selected Team Over 1.5 Goals**: occurred in 156 / 224 matches (69.6%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 172
- **Total Hits**: 136
- **Overall Hit Rate**: 79.1%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=85, hits=78, hit_rate=91.8%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=16, hits=10, hit_rate=62.5%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1263** | scored: 1263

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 134 | 134 | 131 | +97.8% | +97.4% | +0.4% | 0.021269 |
| `match_over_45` | 125 | 125 | 29 | +23.2% | +25.3% | -2.1% | 0.185033 |
| `away_under_25` | 122 | 122 | 115 | +94.3% | +93.2% | +1.0% | 0.055588 |
| `home_over_05` | 117 | 117 | 110 | +94.0% | +89.0% | +5.0% | 0.060542 |
| `match_over_25` | 104 | 104 | 62 | +59.6% | +41.4% | +18.3% | 0.287186 |
| `match_over_35` | 98 | 98 | 38 | +38.8% | +43.0% | -4.2% | 0.244783 |
| `exact_4` | 67 | 67 | 17 | +25.4% | +18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | +41.3% | +37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | +33.9% | +30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | +10.5% | +12.6% | -2.1% | 0.096166 |
| `away_under_15` | 42 | 42 | 35 | +83.3% | +81.2% | +2.1% | 0.138878 |
| `btts_no` | 40 | 40 | 17 | +42.5% | +52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | +50.0% | +50.9% | -0.9% | 0.248905 |
| `home_under_35` | 37 | 37 | 33 | +89.2% | +94.5% | -5.4% | 0.09764 |
| `exact_3` | 32 | 32 | 4 | +12.5% | +22.2% | -9.7% | 0.119085 |
| `goal_range_2_3` | 26 | 26 | 8 | +30.8% | +46.1% | -15.4% | 0.233772 |
| `home_under_25` | 25 | 25 | 22 | +88.0% | +91.7% | -3.7% | 0.10725 |
| `exact_2` | 24 | 24 | 5 | +20.8% | +24.5% | -3.7% | 0.166543 |
| `away_over_05` | 21 | 21 | 18 | +85.7% | +86.3% | -0.6% | 0.120937 |
| `goal_range_6_plus` | 9 | 9 | 1 | +11.1% | +18.7% | -7.6% | 0.102748 |
| `match_over_15` | 8 | 8 | 7 | +87.5% | +85.7% | +1.8% | 0.122786 |
| `home_under_15` | 6 | 6 | 5 | +83.3% | +81.1% | +2.3% | 0.138501 |
| `exact_1` | 4 | 4 | 1 | +25.0% | +21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | +33.3% | +13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | +0.0% | +11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | +100.0% | +35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 958 | 567 | +59.2% | +58.5% | +0.7% | 0.140341 |
| legacy | 263 | 136 | +51.7% | +52.1% | -0.4% | 0.183796 |
| model | 42 | 28 | +66.7% | +47.2% | +19.4% | 0.278725 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 146 | +15.7% | +20.5% | +4.8% |
| 0.2-0.3 | 183 | +24.8% | +22.4% | -2.4% |
| 0.3-0.4 | 211 | +35.7% | +45.0% | +9.3% |
| 0.4-0.5 | 124 | +45.0% | +41.1% | -3.8% |
| 0.5-0.6 | 78 | +52.6% | +39.7% | -12.8% |
| 0.6-0.7 | 5 | +65.3% | +100.0% | +34.7% |
| 0.7-0.8 | 4 | +74.4% | +50.0% | -24.4% |
| 0.8-0.9 | 153 | +84.6% | +88.2% | +3.6% |
| 0.9-1.0 | 359 | +94.9% | +95.0% | +0.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=171, MAE=1.46731 goals, bias=-0.50848 (realized − promised), promised avg 3.689766 vs realized 3.181287

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 342 | +14.8% | +10.2% | -4.6% | 0.094518 |
| Away Over 1.5 | 171 | +23.6% | +29.8% | +6.2% | 0.200187 |
| BTTS-Yes | 171 | +40.9% | +52.6% | +11.8% | 0.264597 |
| Home Over 1.5 | 171 | +72.5% | +59.1% | -13.5% | 0.231298 |
| Over 2.5 | 171 | +71.9% | +61.4% | -10.5% | 0.244888 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 123 | +8.8% | +19.5% | +10.7% |
| 0.1-0.2 | 386 | +14.2% | +11.9% | -2.3% |
| 0.2-0.3 | 4 | +20.8% | +25.0% | +4.2% |
| 0.3-0.4 | 56 | +37.7% | +57.1% | +19.5% |
| 0.4-0.5 | 115 | +42.4% | +50.4% | +8.0% |
| 0.6-0.7 | 73 | +67.3% | +54.8% | -12.5% |
| 0.7-0.8 | 90 | +74.7% | +65.6% | -9.1% |
| 0.8-0.9 | 145 | +85.7% | +65.5% | -20.2% |
| 0.9-1.0 | 34 | +91.7% | +79.4% | -12.3% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=92, wins=73, hit_rate=0.793478, ROI=0.040388
- `2way-unanimous min_p>=60 avg_p>=65`: settled=4, wins=3, hit_rate=0.75, ROI=0.0475
- `3way-unanimous avg_p>=65`: settled=55, wins=39, hit_rate=0.709091, ROI=-0.042685
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.272222
- `ml-meta avg_p>=55`: settled=30, wins=15, hit_rate=0.5, ROI=-0.282333
- `ml-meta avg_p>=65`: settled=1, wins=1, hit_rate=1.0, ROI=0.5

## By bucket

- `CAUTION`: settled=43, wins=23, hit_rate=0.534884, ROI=-0.181395
- `CERTIFIED_CLEAN`: settled=19, wins=9, hit_rate=0.473684, ROI=-0.31
- `SKIPPED_VETO`: settled=120, wins=92, hit_rate=0.766667, ROI=0.032233
- `WATCHLIST_NO_ODDS`: settled=10, wins=9, hit_rate=0.9, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=2, wins=1, hit_rate=0.5, ROI=-0.4
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=10, wins=6, hit_rate=0.6, ROI=-0.196
- `WATCHLIST_UNKNOWN_CTX`: settled=20, wins=18, hit_rate=0.9, ROI=0.088

## By odds source

- `UNKNOWN`: settled=10, wins=9, hit_rate=0.9, ROI=None
- `betexplorer_odds`: settled=88, wins=67, hit_rate=0.761364, ROI=0.019659
- `bzzoiro_odds`: settled=73, wins=47, hit_rate=0.643836, ROI=-0.084822
- `forebet_best`: settled=7, wins=4, hit_rate=0.571429, ROI=-0.217143
- `scoutingstats_odds`: settled=35, wins=20, hit_rate=0.571429, ROI=-0.246857
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=14, wins=10, hit_rate=0.714286, ROI=-0.098571
- `betexplorer`: settled=88, wins=67, hit_rate=0.761364, ROI=0.019659
- `exact`: settled=100, wins=62, hit_rate=0.62, ROI=-0.12992
- `fallback`: settled=12, wins=10, hit_rate=0.833333, ROI=0.151667
- `none`: settled=10, wins=9, hit_rate=0.9, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 88 | 67 | 0.761364 | 88 | 0.019659 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 65 | 42 | 0.646154 | 65 | -0.066954 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 35 | 20 | 0.571429 | 35 | -0.246857 |
| Source fallback (`SOURCE_FALLBACK`) | 12 | 10 | 0.833333 | 12 | 0.151667 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 14 | 10 | 0.714286 | 14 | -0.098571 |
| No usable price (`UNMATCHED`) | 10 | 9 | 0.9 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 120 | 92 | 0.766667 | 120 | 0.032233 |
| **trusted evidence only** | 92 | 69 | 0.75 | 92 | 0.015522 |
| **soft evidence only** | 28 | 23 | 0.821429 | 28 | 0.087143 |
| evidence: BETEXPLORER_RESCUE | 51 | 41 | 0.803922 | 51 | 0.066667 |
| evidence: BZZOIRO_PRIMARY | 41 | 28 | 0.682927 | 41 | -0.048098 |
| evidence: SCOUTINGSTATS_SOLE | 14 | 10 | 0.714286 | 14 | -0.074286 |
| evidence: SOURCE_FALLBACK | 6 | 6 | 1.0 | 6 | 0.418333 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 7 | 0.875 | 8 | 0.12125 |
| odds band: <1.50 | 97 | 76 | 0.783505 | 97 | 0.00266 |
| odds band: 1.50-2.00 | 22 | 15 | 0.681818 | 22 | 0.110455 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.136 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 7 | 5 | 0.714286 | 7 | -0.082857 |
| veto reason: context VETO in ['odds_band'] | 40 | 31 | 0.775 | 40 | 0.042 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.130429 |
| veto reason: context VETO in ['team_a'] | 17 | 14 | 0.823529 | 17 | 0.195882 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.212857 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.013333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 5 | 2 | 0.4 | 5 | -0.512 |
| veto reason: context VETO in ['team_h'] | 20 | 14 | 0.7 | 20 | -0.08475 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| contrast CAUTION: BETEXPLORER_RESCUE | 17 | 11 | 0.647059 | 17 | -0.058235 |
| contrast CAUTION: BZZOIRO_PRIMARY | 13 | 9 | 0.692308 | 13 | 0.117692 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 8 | 1 | 0.125 | 8 | -0.7875 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 175 | 128 | 0.731429 | 165 | -0.004861 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 14 | 10 | 0.714286 | 14 | -0.098571 | 6 | 1.340833 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 35 | 20 | 0.571429 | 35 | -0.246857 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-14: Epitsentr Dunayivtsi vs Veres Rivne (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 2.11 -> 🔴 LOST (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.5% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (19.0%), [🔴 MISS] 2-1 (18.6%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +86.0% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +37.2% (Actual: 0 goals)

### 2026-08-14: Legia Warszawa vs Radomiak Radom (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.63 -> 🟢 WON (Expected prob: 64.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.6% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.7%), [🔴 MISS] 1-0 (15.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.4% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +97.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.7% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +40.1% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +19.8% (Actual: 5 goals)

### 2026-08-14: Oakleigh Cannons vs Green Gully SC (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🟢 WON (Expected prob: 62.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.5%), [🔴 MISS] 1-0 (16.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +90.5% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +39.0% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +18.2% (Actual: 5 goals)

### 2026-08-14: Dukla Praha vs Slavia Praha B (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.68 -> 🔴 LOST (Expected prob: 58.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.1%), [🔴 MISS] 2-1 (16.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +88.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.9% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected +95.6% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +80.1% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +38.2% (Actual: 4 goals)

### 2026-08-14: Red Star vs FC Sochaux (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.93 -> 🔴 LOST (Expected prob: 57.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (18.1%), [🔴 MISS] 2-1 (17.3%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +87.0% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +37.5% (Actual: 0 goals)

### 2026-08-14: Universitario de Vinto vs Real Tomayapo (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.56 -> 🔴 LOST (Expected prob: 57.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (18.4%), [🔴 MISS] 2-1 (17.9%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +86.8% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +37.6% (Actual: 1 goals)

### 2026-08-14: Cagliari vs Arezzo (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 67.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.4%), [🟢 HIT] 1-0 (13.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +92.6% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +97.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +43.2% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.4% (Actual: 1 goals)

### 2026-08-14: Galatasaray vs Çorum FK (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.29 -> 🔴 LOST (Expected prob: 79.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 37.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 94.3% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.5%), [🔴 MISS] 3-1 (14.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +93.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.3% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +81.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +43.9% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +25.0% (Actual: 4 goals)

### 2026-08-14: Shandong Luneng vs Qingdao Jonoon (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (14.3%), [🔴 MISS] 3-0 (13.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +45.2% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +94.2% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +26.8% (Actual: 4 goals)

### 2026-08-14: Lask Linz vs Ried (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.5%), [🔴 MISS] 3-0 (12.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +45.4% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +93.6% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +26.6% (Actual: 5 goals)

### 2026-08-14: Tractor Sazi vs Paykan (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🟢 WON (Expected prob: 65.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.7% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (17.1%), [🔴 MISS] 1-0 (15.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.4% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +83.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +40.3% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +22.4% (Actual: 2 goals)

### 2026-08-14: The New Saints vs Briton Ferry (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.18 -> 🟢 WON (Expected prob: 62.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.2%), [🟢 HIT] 1-0 (16.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +90.4% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +39.5% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +18.7% (Actual: 1 goals)

### 2026-08-14: Fiorentina vs Benevento Calcio (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.31 -> 🟢 WON (Expected prob: 60.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.2%), [🔴 MISS] 2-0 (17.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +89.4% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +38.4% (Actual: 5 goals)

### 2026-08-14: CSKA 1948 vs Cherno More Varna (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🟢 WON (Expected prob: 59.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (17.1%), [🔴 MISS] 1-0 (17.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +88.4% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.6% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +38.1% (Actual: 5 goals)

### 2026-08-14: Parma vs Catania (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 57.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.6%), [🔴 MISS] 2-1 (17.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +87.3% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +38.1% (Actual: 2 goals)


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
- 2026-08-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Lindome GIF vs BK Astrio -> HOME @ 1.33 (pending_or_unmatched_result); keys=['lindomegi']/['bkastrio']

## Ambiguous result examples

- none

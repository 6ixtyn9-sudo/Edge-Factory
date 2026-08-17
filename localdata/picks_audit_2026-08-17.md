# Edge Factory — Recent picks audit (2026-07-19 to 2026-08-17)

## Overall

- archived pick rows: 294
- archived pick dates: 30
- immutable morning-baseline rows: 156
- verified official late-slate additions: 27
- regular-ledger-only legacy rows: 111
- unsafe regular ledgers ignored: 4
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 272
- eligible prior 1x2 picks: 281
- pending/unmatched result picks: 6
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 5
- ambiguous result picks: 0
- wins: 190
- hit rate: +69.9%
- priced picks: 257
- ROI: -3.1%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-17
- same-day rows excluded: 13

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 178 / 272 matches (65.4%)
- **Both Teams to Score (BTTS)**: occurred in 148 / 272 matches (54.4%)
- **Selected Team Over 1.5 Goals**: occurred in 190 / 272 matches (69.9%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 229
- **Total Hits**: 186
- **Overall Hit Rate**: 81.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=120, hits=110, hit_rate=91.7%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=8, hits=8, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=33, hits=23, hit_rate=69.7%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1541** | scored: 1541

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 184 | 184 | 181 | +98.4% | +97.7% | +0.7% | 0.015571 |
| `away_under_25` | 171 | 171 | 160 | +93.6% | +93.7% | -0.1% | 0.061078 |
| `home_over_05` | 167 | 167 | 155 | +92.8% | +87.9% | +4.9% | 0.070343 |
| `match_over_25` | 160 | 160 | 100 | +62.5% | +42.3% | +20.2% | 0.282017 |
| `match_over_45` | 153 | 153 | 37 | +24.2% | +25.2% | -1.1% | 0.186861 |
| `match_over_35` | 98 | 98 | 38 | +38.8% | +43.0% | -4.2% | 0.244783 |
| `away_under_15` | 70 | 70 | 57 | +81.4% | +81.6% | -0.2% | 0.150029 |
| `exact_4` | 67 | 67 | 17 | +25.4% | +18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | +41.3% | +37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | +33.9% | +30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | +10.5% | +12.6% | -2.1% | 0.096166 |
| `home_under_35` | 44 | 44 | 40 | +90.9% | +94.3% | -3.4% | 0.082885 |
| `btts_no` | 40 | 40 | 17 | +42.5% | +52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | +50.0% | +50.9% | -0.9% | 0.248905 |
| `exact_3` | 32 | 32 | 4 | +12.5% | +22.2% | -9.7% | 0.119085 |
| `home_under_25` | 32 | 32 | 29 | +90.6% | +91.4% | -0.8% | 0.085962 |
| `goal_range_2_3` | 26 | 26 | 8 | +30.8% | +46.1% | -15.4% | 0.233772 |
| `exact_2` | 24 | 24 | 5 | +20.8% | +24.5% | -3.7% | 0.166543 |
| `away_over_05` | 22 | 22 | 19 | +86.4% | +86.0% | +0.3% | 0.117067 |
| `goal_range_6_plus` | 9 | 9 | 1 | +11.1% | +18.7% | -7.6% | 0.102748 |
| `home_under_15` | 8 | 8 | 7 | +87.5% | +81.2% | +6.3% | 0.112258 |
| `match_over_15` | 8 | 8 | 7 | +87.5% | +85.7% | +1.8% | 0.122786 |
| `exact_1` | 4 | 4 | 1 | +25.0% | +21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | +33.3% | +13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | +0.0% | +11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | +100.0% | +35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1233 | 789 | +64.0% | +62.1% | +1.9% | 0.136287 |
| legacy | 263 | 136 | +51.7% | +52.1% | -0.4% | 0.183796 |
| model | 45 | 31 | +68.9% | +49.1% | +19.8% | 0.267661 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 150 | +15.8% | +20.0% | +4.2% |
| 0.2-0.3 | 202 | +24.8% | +22.8% | -2.0% |
| 0.3-0.4 | 221 | +35.6% | +45.2% | +9.6% |
| 0.4-0.5 | 166 | +44.5% | +48.2% | +3.7% |
| 0.5-0.6 | 87 | +52.4% | +43.7% | -8.8% |
| 0.6-0.7 | 5 | +65.3% | +100.0% | +34.7% |
| 0.7-0.8 | 4 | +74.4% | +50.0% | -24.4% |
| 0.8-0.9 | 235 | +84.4% | +87.7% | +3.2% |
| 0.9-1.0 | 471 | +95.2% | +95.3% | +0.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=228, MAE=1.443684 goals, bias=-0.392105 (realized − promised), promised avg 3.637719 vs realized 3.245614

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 456 | +15.2% | +10.1% | -5.1% | 0.093371 |
| Away Over 1.5 | 228 | +22.5% | +30.3% | +7.8% | 0.198228 |
| BTTS-Yes | 228 | +41.4% | +54.4% | +13.0% | 0.264371 |
| Home Over 1.5 | 228 | +73.3% | +59.6% | -13.6% | 0.22983 |
| Over 2.5 | 228 | +71.3% | +63.2% | -8.2% | 0.236469 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 163 | +8.9% | +19.6% | +10.7% |
| 0.1-0.2 | 516 | +14.5% | +12.0% | -2.5% |
| 0.2-0.3 | 5 | +20.6% | +20.0% | -0.6% |
| 0.3-0.4 | 64 | +37.8% | +54.7% | +16.9% |
| 0.4-0.5 | 164 | +42.8% | +54.3% | +11.5% |
| 0.6-0.7 | 111 | +66.9% | +56.8% | -10.2% |
| 0.7-0.8 | 108 | +74.8% | +68.5% | -6.2% |
| 0.8-0.9 | 196 | +85.2% | +66.8% | -18.4% |
| 0.9-1.0 | 41 | +91.7% | +78.0% | -13.7% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=98, wins=78, hit_rate=0.795918, ROI=0.073367
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=52, wins=38, hit_rate=0.730769, ROI=-0.007157
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.272222
- `ml-meta avg_p>=55`: settled=68, wins=37, hit_rate=0.544118, ROI=-0.177273
- `ml-meta avg_p>=60`: settled=1, wins=1, hit_rate=1.0, ROI=0.3
- `ml-meta avg_p>=65`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.25
- `ml-meta avg_p>=70`: settled=1, wins=1, hit_rate=1.0, ROI=0.42

## By bucket

- `CAUTION`: settled=57, wins=31, hit_rate=0.54386, ROI=-0.133684
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=139, wins=106, hit_rate=0.76259, ROI=0.044302
- `WATCHLIST_NO_ODDS`: settled=14, wins=12, hit_rate=0.857143, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=4, wins=2, hit_rate=0.5, ROI=-0.156667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=18, wins=13, hit_rate=0.722222, ROI=0.007778
- `WATCHLIST_UNKNOWN_CTX`: settled=19, wins=17, hit_rate=0.894737, ROI=0.089474

## By odds source

- `UNKNOWN`: settled=15, wins=12, hit_rate=0.8, ROI=None
- `betexplorer_odds`: settled=102, wins=77, hit_rate=0.754902, ROI=0.052647
- `bzzoiro_odds`: settled=85, wins=54, hit_rate=0.635294, ROI=-0.081435
- `forebet_best`: settled=9, wins=6, hit_rate=0.666667, ROI=-0.095556
- `scoutingstats_odds`: settled=50, wins=30, hit_rate=0.6, ROI=-0.1874
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=16, wins=11, hit_rate=0.6875, ROI=-0.07
- `betexplorer`: settled=102, wins=77, hit_rate=0.754902, ROI=0.052647
- `exact`: settled=127, wins=79, hit_rate=0.622047, ROI=-0.113795
- `fallback`: settled=13, wins=11, hit_rate=0.846154, ROI=0.165385
- `none`: settled=14, wins=12, hit_rate=0.857143, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 102 | 77 | 0.754902 | 102 | 0.052647 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 77 | 49 | 0.636364 | 77 | -0.066 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 50 | 30 | 0.6 | 50 | -0.1874 |
| Source fallback (`SOURCE_FALLBACK`) | 13 | 11 | 0.846154 | 13 | 0.165385 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 16 | 11 | 0.6875 | 15 | -0.07 |
| No usable price (`UNMATCHED`) | 14 | 12 | 0.857143 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 139 | 106 | 0.76259 | 139 | 0.044302 |
| **trusted evidence only** | 102 | 79 | 0.77451 | 102 | 0.070765 |
| **soft evidence only** | 37 | 27 | 0.72973 | 37 | -0.028649 |
| evidence: BETEXPLORER_RESCUE | 54 | 46 | 0.851852 | 54 | 0.146667 |
| evidence: BZZOIRO_PRIMARY | 48 | 33 | 0.6875 | 48 | -0.014625 |
| evidence: SCOUTINGSTATS_SOLE | 22 | 13 | 0.590909 | 22 | -0.221364 |
| evidence: SOURCE_FALLBACK | 7 | 7 | 1.0 | 7 | 0.405714 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 7 | 0.875 | 8 | 0.12125 |
| odds band: <1.50 | 107 | 86 | 0.803738 | 107 | 0.042037 |
| odds band: 1.50-2.00 | 30 | 18 | 0.6 | 30 | -0.017333 |
| odds band: 2.00-3.00 | 2 | 2 | 1.0 | 2 | 1.09 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.136 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 6 | 5 | 0.833333 | 6 | 0.07 |
| veto reason: context VETO in ['odds_band'] | 43 | 35 | 0.813953 | 43 | 0.106047 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.130429 |
| veto reason: context VETO in ['team_a'] | 23 | 17 | 0.73913 | 23 | 0.102174 |
| veto reason: context VETO in ['team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.35 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.2275 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.013333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 7 | 3 | 0.428571 | 7 | -0.448571 |
| veto reason: context VETO in ['team_h'] | 27 | 18 | 0.666667 | 27 | -0.089074 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| contrast CAUTION: BETEXPLORER_RESCUE | 27 | 17 | 0.62963 | 27 | 0.007037 |
| contrast CAUTION: BZZOIRO_PRIMARY | 18 | 11 | 0.611111 | 18 | -0.026111 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 7 | 1 | 0.142857 | 7 | -0.757143 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 206 | 149 | 0.723301 | 192 | 0.012698 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 16 | 11 | 0.6875 | 15 | -0.07 | 8 | 1.359375 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 50 | 30 | 0.6 | 50 | -0.1874 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-16: Always Ready vs Real Potosi (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 76.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.5% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.1%), [🔴 MISS] 3-0 (11.4%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +52.7% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +88.6% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +30.3% (Actual: 2 goals)

### 2026-08-16: Rapid Vienna vs Grazer AK (Actual Score: **8-0**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🟢 WON (Expected prob: 66.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 8 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 8 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.4%), [🔴 MISS] 1-0 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +45.7% (Actual: 8 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +85.9% (Actual: 8 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +84.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +22.3% (Actual: 8 goals)

### 2026-08-16: Portland Thorns W vs Orlando Pride W (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.98 -> 🟢 WON (Expected prob: 64.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.9%), [🔴 MISS] 1-0 (15.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +87.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +43.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +20.1% (Actual: 3 goals)

### 2026-08-16: Lyngby vs FC Midtjylland (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.77 -> 🔴 LOST (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-2 (17.6%), [🔴 MISS] 0-2 (15.9%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +45.1% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +93.8% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +90.6% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +18.6% (Actual: 2 goals)

### 2026-08-16: Sao Paulo vs Coritiba (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🔴 LOST (Expected prob: 55.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (19.1%), [🔴 MISS] 1-0 (19.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +81.0% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +41.0% (Actual: 2 goals)

### 2026-08-16: Seoul E-Land FC vs Ansan Greeners (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 60.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.3%), [🔴 MISS] 1-0 (17.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +83.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +83.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +42.1% (Actual: 4 goals)

### 2026-08-16: North Carolina Courage (w) vs Houston Dash (w) (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.58 -> 🔴 LOST (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (18.8%), [🔴 MISS] 1-0 (18.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +81.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.9% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected +94.4% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +80.1% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +41.5% (Actual: 5 goals)

### 2026-08-16: Odense vs AC Horsens (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.74 -> 🔴 LOST (Expected prob: 55.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 46.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (19.1%), [🔴 MISS] 1-0 (19.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +85.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +36.9% (Actual: 3 goals)

### 2026-08-16: Chicago Fire vs Portland Timbers (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.58 -> 🟢 WON (Expected prob: 55.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (19.2%), [🟢 HIT] 2-1 (19.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +80.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.3% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +41.5% (Actual: 3 goals)

### 2026-08-16: Rangers vs St Mirren (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 73.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.6% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (12.7%), [🔴 MISS] 1-0 (11.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +51.3% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.5% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +30.5% (Actual: 6 goals)

### 2026-08-16: Broadmeadow Magic vs Charlestown Azzurri (Actual Score: **8-0**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 76.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.1% (Actual: 8 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.9% (Actual: 8 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (15.2%), [🔴 MISS] 3-1 (12.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +52.7% (Actual: 8 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +89.6% (Actual: 8 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +92.0% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +31.3% (Actual: 8 goals)

### 2026-08-16: Feyenoord vs Go Ahead Eagles (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 74.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.7%), [🔴 MISS] 1-0 (12.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +50.9% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +88.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.1% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +80.6% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +28.2% (Actual: 4 goals)

### 2026-08-16: CSKA Sofia vs Botev Vratsa (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🟢 WON (Expected prob: 73.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.4% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.6% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (13.2%), [🔴 MISS] 1-0 (11.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +49.7% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.0% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +97.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +85.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +29.6% (Actual: 5 goals)

### 2026-08-16: Penarol vs Central Espanol (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.4%), [🔴 MISS] 3-0 (12.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +48.2% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.0% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +84.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +26.7% (Actual: 3 goals)

### 2026-08-16: Monterrey vs FC Juarez (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.4%), [🔴 MISS] 2-1 (13.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +50.0% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +87.6% (Actual: 6 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +84.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +27.2% (Actual: 7 goals)

### 2026-08-16: Lazio vs Mantova (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🔴 LOST (Expected prob: 69.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (14.7%), [🔴 MISS] 3-0 (13.7%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +49.4% (Actual: 2 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +87.5% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.0% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +82.0% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +26.3% (Actual: 2 goals)

### 2026-08-16: Deportivo Tachira FC vs Monagas SC (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 59.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (17.3%), [🔴 MISS] 1-0 (17.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +83.2% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.2% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +82.5% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +42.1% (Actual: 5 goals)

### 2026-08-16: Los Angeles FC vs San Diego (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 57.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (18.2%), [🔴 MISS] 2-1 (17.4%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +82.3% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +42.4% (Actual: 1 goals)

### 2026-08-16: Hansa Rostock vs Waldhof Mannheim (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🔴 LOST (Expected prob: 57.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (18.2%), [🔴 MISS] 2-1 (17.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.2% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected +94.8% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +81.5% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +42.2% (Actual: 6 goals)

### 2026-08-16: FH Hafnarfjordur vs Vikingur Reykjavik (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.56 -> 🟢 WON (Expected prob: 55.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 4 goals)
  - **Top Scores**: [🔴 MISS] 1-2 (17.2%), [🔴 MISS] 0-2 (16.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +92.8% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +87.6% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +43.9% (Actual: 6 goals)

### 2026-08-16: KR Reykjavik vs Breidablik (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.7% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (19.3%), [🔴 MISS] 2-1 (19.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.3% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.2% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected +93.1% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +40.7% (Actual: 6 goals)

### 2026-08-16: Preston Lions vs Dandenong Thunder (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 78.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 3-0 (13.0%), [🔴 MISS] 2-0 (13.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +50.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +84.0% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +89.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +28.0% (Actual: 3 goals)

### 2026-08-16: HJK Helsinki vs FF Jaro (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 67.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.5%), [🔴 MISS] 1-0 (13.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +47.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +83.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +22.9% (Actual: 3 goals)

### 2026-08-16: Atvidabergs FF vs Skovde AIK (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 57.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (18.2%), [🟢 HIT] 2-1 (17.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.0% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +42.3% (Actual: 3 goals)

### 2026-08-16: Trelleborgs FF vs Eskilsminne IF (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (19.3%), [🔴 MISS] 2-1 (19.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +81.6% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.8% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected +93.9% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +40.1% (Actual: 4 goals)

### 2026-08-16: Twente vs PEC Zwolle (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 74.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (12.7%), [🔴 MISS] 2-0 (12.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +50.9% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +88.5% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +28.3% (Actual: 4 goals)

### 2026-08-16: Chippa United vs Orlando Pirates (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.28 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 37.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.4% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (15.1%), [🔴 MISS] 0-1 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +94.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +93.7% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected +81.1% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +41.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +21.7% (Actual: 3 goals)

### 2026-08-16: Sarpsborg 08 FF vs Sandefjord (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🔴 LOST (Expected prob: 58.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.2%), [🔴 MISS] 2-1 (17.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.8% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.5% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +82.3% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +42.8% (Actual: 3 goals)

### 2026-08-16: Las Vegas Lights FC vs Brooklyn (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🟢 WON (Expected prob: 55.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 46.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **Top Scores**: [🟢 HIT] 2-1 (19.1%), [🔴 MISS] 1-0 (19.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +81.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +40.5% (Actual: 3 goals)

### 2026-08-16: FC Nordsjaelland vs Silkeborg (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 59.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (17.3%), [🟢 HIT] 1-0 (17.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +83.7% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +43.3% (Actual: 1 goals)


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
- 2026-08-16 `SKIPPED_VETO` `ml-meta avg_p>=55` — SC Braga vs Gil Vicente -> HOME @ 1.7 (pending_or_unmatched_result); keys=['braga']/['gilvicent']

## Ambiguous result examples

- none

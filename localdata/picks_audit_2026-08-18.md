# Edge Factory — Recent picks audit (2026-07-20 to 2026-08-18)

## Overall

- archived pick rows: 294
- archived pick dates: 30
- immutable morning-baseline rows: 156
- verified official late-slate additions: 27
- regular-ledger-only legacy rows: 111
- unsafe regular ledgers ignored: 4
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 281
- eligible prior 1x2 picks: 291
- pending/unmatched result picks: 8
- voided postponed/cancelled/abandoned events: 2
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 5
- ambiguous result picks: 0
- wins: 198
- hit rate: +70.5%
- priced picks: 264
- ROI: -1.7%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-18
- same-day rows excluded: 3

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 184 / 281 matches (65.5%)
- **Both Teams to Score (BTTS)**: occurred in 152 / 281 matches (54.1%)
- **Selected Team Over 1.5 Goals**: occurred in 197 / 281 matches (70.1%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 240
- **Total Hits**: 195
- **Overall Hit Rate**: 81.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=121, hits=111, hit_rate=91.7%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=9, hits=9, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=42, hits=30, hit_rate=71.4%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1591** | scored: 1591

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 192 | 192 | 189 | +98.4% | +97.8% | +0.7% | 0.014927 |
| `away_under_25` | 179 | 179 | 168 | +93.9% | +93.7% | +0.1% | 0.05849 |
| `home_over_05` | 175 | 175 | 163 | +93.1% | +87.7% | +5.4% | 0.068284 |
| `match_over_25` | 171 | 171 | 108 | +63.2% | +42.7% | +20.5% | 0.280836 |
| `match_over_45` | 159 | 159 | 39 | +24.5% | +25.1% | -0.6% | 0.188236 |
| `match_over_35` | 98 | 98 | 38 | +38.8% | +43.0% | -4.2% | 0.244783 |
| `away_under_15` | 73 | 73 | 60 | +82.2% | +81.6% | +0.6% | 0.145305 |
| `exact_4` | 67 | 67 | 17 | +25.4% | +18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | +41.3% | +37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | +33.9% | +30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | +10.5% | +12.6% | -2.1% | 0.096166 |
| `home_under_35` | 47 | 47 | 43 | +91.5% | +94.3% | -2.8% | 0.077804 |
| `btts_no` | 40 | 40 | 17 | +42.5% | +52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | +50.0% | +50.9% | -0.9% | 0.248905 |
| `home_under_25` | 35 | 35 | 32 | +91.4% | +91.3% | +0.1% | 0.079321 |
| `exact_3` | 32 | 32 | 4 | +12.5% | +22.2% | -9.7% | 0.119085 |
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
| hybrid_cohort | 1283 | 832 | +64.8% | +62.6% | +2.3% | 0.134568 |
| legacy | 263 | 136 | +51.7% | +52.1% | -0.4% | 0.183796 |
| model | 45 | 31 | +68.9% | +49.1% | +19.8% | 0.267661 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 152 | +15.9% | +19.7% | +3.9% |
| 0.2-0.3 | 206 | +24.8% | +23.3% | -1.5% |
| 0.3-0.4 | 221 | +35.6% | +45.2% | +9.6% |
| 0.4-0.5 | 174 | +44.6% | +49.4% | +4.8% |
| 0.5-0.6 | 90 | +52.5% | +44.4% | -8.0% |
| 0.6-0.7 | 5 | +65.3% | +100.0% | +34.7% |
| 0.7-0.8 | 4 | +74.4% | +50.0% | -24.4% |
| 0.8-0.9 | 247 | +84.4% | +88.3% | +3.9% |
| 0.9-1.0 | 492 | +95.3% | +95.5% | +0.3% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=239, MAE=1.438494 goals, bias=-0.375481 (realized − promised), promised avg 3.626527 vs realized 3.251046

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 478 | +15.2% | +10.0% | -5.2% | 0.093156 |
| Away Over 1.5 | 239 | +22.8% | +30.5% | +7.7% | 0.199309 |
| BTTS-Yes | 239 | +41.4% | +54.0% | +12.5% | 0.263221 |
| Home Over 1.5 | 239 | +72.8% | +59.8% | -13.0% | 0.223507 |
| Over 2.5 | 239 | +71.2% | +63.6% | -7.6% | 0.235558 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 170 | +8.9% | +18.8% | +9.9% |
| 0.1-0.2 | 542 | +14.6% | +12.2% | -2.4% |
| 0.2-0.3 | 5 | +20.6% | +20.0% | -0.6% |
| 0.3-0.4 | 66 | +37.8% | +54.5% | +16.7% |
| 0.4-0.5 | 173 | +42.8% | +53.8% | +10.9% |
| 0.6-0.7 | 119 | +66.9% | +58.0% | -8.9% |
| 0.7-0.8 | 111 | +74.7% | +68.5% | -6.2% |
| 0.8-0.9 | 207 | +85.2% | +67.6% | -17.5% |
| 0.9-1.0 | 41 | +91.7% | +78.0% | -13.7% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=97, wins=77, hit_rate=0.793814, ROI=0.071494
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=51, wins=37, hit_rate=0.72549, ROI=-0.0183
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.272222
- `ml-meta avg_p>=55`: settled=78, wins=46, hit_rate=0.589744, ROI=-0.106216
- `ml-meta avg_p>=60`: settled=2, wins=2, hit_rate=1.0, ROI=0.335
- `ml-meta avg_p>=65`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.25
- `ml-meta avg_p>=70`: settled=1, wins=1, hit_rate=1.0, ROI=0.42

## By bucket

- `CAUTION`: settled=59, wins=33, hit_rate=0.559322, ROI=-0.10339
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=144, wins=110, hit_rate=0.763889, ROI=0.054153
- `WATCHLIST_NO_ODDS`: settled=16, wins=14, hit_rate=0.875, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=4, wins=2, hit_rate=0.5, ROI=-0.156667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=19, wins=14, hit_rate=0.736842, ROI=0.033684
- `WATCHLIST_UNKNOWN_CTX`: settled=18, wins=16, hit_rate=0.888889, ROI=0.081111

## By odds source

- `UNKNOWN`: settled=17, wins=14, hit_rate=0.823529, ROI=None
- `betexplorer_odds`: settled=104, wins=78, hit_rate=0.75, ROI=0.054615
- `bzzoiro_odds`: settled=89, wins=58, hit_rate=0.651685, ROI=-0.048449
- `forebet_best`: settled=9, wins=6, hit_rate=0.666667, ROI=-0.095556
- `scoutingstats_odds`: settled=51, wins=31, hit_rate=0.607843, ROI=-0.173922
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=16, wins=11, hit_rate=0.6875, ROI=-0.07
- `betexplorer`: settled=104, wins=78, hit_rate=0.75, ROI=0.054615
- `exact`: settled=132, wins=84, hit_rate=0.636364, ROI=-0.085924
- `fallback`: settled=13, wins=11, hit_rate=0.846154, ROI=0.165385
- `none`: settled=16, wins=14, hit_rate=0.875, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 104 | 78 | 0.75 | 104 | 0.054615 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 81 | 53 | 0.654321 | 81 | -0.030519 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 51 | 31 | 0.607843 | 51 | -0.173922 |
| Source fallback (`SOURCE_FALLBACK`) | 13 | 11 | 0.846154 | 13 | 0.165385 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 16 | 11 | 0.6875 | 15 | -0.07 |
| No usable price (`UNMATCHED`) | 16 | 14 | 0.875 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 144 | 110 | 0.763889 | 144 | 0.054153 |
| **trusted evidence only** | 107 | 83 | 0.775701 | 107 | 0.082785 |
| **soft evidence only** | 37 | 27 | 0.72973 | 37 | -0.028649 |
| evidence: BETEXPLORER_RESCUE | 56 | 47 | 0.839286 | 56 | 0.140536 |
| evidence: BZZOIRO_PRIMARY | 51 | 36 | 0.705882 | 51 | 0.019373 |
| evidence: SCOUTINGSTATS_SOLE | 22 | 13 | 0.590909 | 22 | -0.221364 |
| evidence: SOURCE_FALLBACK | 7 | 7 | 1.0 | 7 | 0.405714 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 7 | 0.875 | 8 | 0.12125 |
| odds band: <1.50 | 108 | 87 | 0.805556 | 108 | 0.044056 |
| odds band: 1.50-2.00 | 34 | 21 | 0.617647 | 34 | 0.025294 |
| odds band: 2.00-3.00 | 2 | 2 | 1.0 | 2 | 1.09 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.136 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 6 | 5 | 0.833333 | 6 | 0.07 |
| veto reason: context VETO in ['odds_band'] | 44 | 36 | 0.818182 | 44 | 0.109545 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.130429 |
| veto reason: context VETO in ['team_a'] | 23 | 17 | 0.73913 | 23 | 0.102174 |
| veto reason: context VETO in ['team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.35 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.2275 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.013333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 9 | 4 | 0.444444 | 9 | -0.397778 |
| veto reason: context VETO in ['team_h'] | 29 | 20 | 0.689655 | 29 | -0.020172 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| contrast CAUTION: BETEXPLORER_RESCUE | 28 | 18 | 0.642857 | 28 | 0.028214 |
| contrast CAUTION: BZZOIRO_PRIMARY | 19 | 12 | 0.631579 | 19 | 0.023684 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 7 | 1 | 0.142857 | 7 | -0.757143 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 214 | 156 | 0.728972 | 198 | 0.027061 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 16 | 11 | 0.6875 | 15 | -0.07 | 8 | 1.359375 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 51 | 31 | 0.607843 | 51 | -0.173922 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-17: Olancho FC vs Juticalpa (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🟢 WON (Expected prob: 72.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (14.2%), [🔴 MISS] 2-0 (13.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +55.4% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +87.4% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +83.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +28.9% (Actual: 1 goals)

### 2026-08-17: Universitatea Cluj vs UTA Arad (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 2.1 -> 🟢 WON (Expected prob: 57.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.7%), [🟢 HIT] 2-1 (17.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +46.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.4% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.0% (Actual: 1 away goals)

### 2026-08-17: Almeria vs CD Eldense (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.37 -> 🟢 WON (Expected prob: 61.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.2%), [🔴 MISS] 1-0 (16.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +46.7% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +84.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +18.5% (Actual: 3 goals)

### 2026-08-17: Sassuolo vs Cesena (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.56 -> 🟢 WON (Expected prob: 63.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.7%), [🔴 MISS] 1-0 (15.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +48.4% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +85.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +19.6% (Actual: 3 goals)

### 2026-08-17: Casa Pia vs Benfica (Actual Score: **0-7**)
- **1X2 Pick**: Selected `AWAY` @ 1.26 -> 🟢 WON (Expected prob: 63.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.4% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.5% (Actual: 7 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (16.1%), [🔴 MISS] 1-2 (14.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +50.7% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +95.5% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +92.6% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +22.4% (Actual: 7 goals)

### 2026-08-17: Afturelding vs HK Kopavogur (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🔴 LOST (Expected prob: 59.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (17.3%), [🔴 MISS] 1-0 (17.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +48.1% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +84.3% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.0% (Actual: 2 away goals)

### 2026-08-17: Fram Reykjavik vs Stjarnan (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.95 -> 🟢 WON (Expected prob: 55.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 46.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (19.1%), [🔴 MISS] 1-0 (19.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +46.3% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +81.8% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +92.8% (Actual: 1 away goals)

### 2026-08-17: Arda Kardzhali vs Lokomotiv Sofia (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.87 -> 🟢 WON (Expected prob: 55.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (19.3%), [🔴 MISS] 2-1 (19.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +80.8% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.3% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +44.9% (Actual: 4 goals)

### 2026-08-17: Brondby vs SonderjyskE (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 69.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (14.7%), [🔴 MISS] 3-0 (13.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +54.2% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +87.3% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.7% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +26.5% (Actual: 5 goals)

### 2026-08-17: Anagennisi Karditsas vs Aris Thessalonikis (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 1-2 (17.1%), [🟢 HIT] 0-2 (15.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +93.4% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +89.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +43.9% (Actual: 2 goals)

### 2026-08-17: Zalaegerszegi TE vs Ferencvarosi TC (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.5 -> 🟢 WON (Expected prob: 60.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-2 (17.7%), [🔴 MISS] 0-2 (16.2%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +49.5% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +94.1% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +90.9% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +20.4% (Actual: 1 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 2 |
- 2026-07-25 `POSTPONED` `WATCHLIST_NO_ODDS` — Coquimbo Unido vs Universidad de Concepcion (verified_disposition); excluded from win/loss/ROI
- 2026-07-26 `POSTPONED` `SKIPPED_VETO` — Super Nova vs Riga (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- 2026-08-08 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Belshina vs Dinamo Minsk -> AWAY @ 1.32 (pending_or_unmatched_result); keys=['belshina', 'belshinab']/['dinamomin']
- 2026-08-11 `WATCHLIST_UNCORROBORATED_PRICE` `2way+bc-confirms avg_p>=60` — Junior vs Pereira -> HOME @ 1.33 (pending_or_unmatched_result); keys=['junior']/['pereira']
- 2026-08-15 `SKIPPED_VETO` `2way-unanimous min_p>=60 avg_p>=65` — Slavia Sofia vs Levski Sofia -> AWAY @ 1.36 (pending_or_unmatched_result); keys=['slaviasof']/['levskisof']
- 2026-08-15 `WATCHLIST_NO_ODDS` `2way-unanimous min_p>=60 avg_p>=65` — Kara-Balta vs Bars -> AWAY @ None (pending_or_unmatched_result); keys=['karabalta']/['bars']
- 2026-08-15 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous min_p>=60 avg_p>=65` — Olympic Kingsway vs Sorrento FC -> HOME @ 1.24 (pending_or_unmatched_result); keys=['olympicki']/['sorrento']
- 2026-08-16 `SKIPPED_VETO` `ml-meta avg_p>=55` — SC Braga vs Gil Vicente -> HOME @ 1.7 (pending_or_unmatched_result); keys=['braga']/['gilvicent']
- 2026-08-17 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hamrun Spartans vs Mosta -> HOME @ 1.18 (pending_or_unmatched_result); keys=['hamrunspa']/['mosta']
- 2026-08-17 `SKIPPED_VETO` `ml-meta avg_p>=55` — Bucaramanga vs Deportivo Pasto -> HOME @ 1.61 (pending_or_unmatched_result); keys=['bucaraman']/['pasto']

## Ambiguous result examples

- none

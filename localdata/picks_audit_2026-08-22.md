# Edge Factory — Recent picks audit (2026-07-24 to 2026-08-22)

## Overall

- archived pick rows: 363
- archived pick dates: 30
- immutable morning-baseline rows: 220
- verified official late-slate additions: 25
- regular-ledger-only legacy rows: 118
- unsafe regular ledgers ignored: 7
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 310
- eligible prior 1x2 picks: 322
- pending/unmatched result picks: 10
- voided postponed/cancelled/abandoned events: 2
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 8
- ambiguous result picks: 0
- wins: 220
- hit rate: +71.0%
- priced picks: 291
- ROI: +0.1%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-22
- same-day rows excluded: 41

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 197 / 310 matches (63.5%)
- **Both Teams to Score (BTTS)**: occurred in 160 / 310 matches (51.6%)
- **Selected Team Over 1.5 Goals**: occurred in 217 / 310 matches (70.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 282
- **Total Hits**: 219
- **Overall Hit Rate**: 77.7%

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
- `match_over_25`: recommended=84, hits=54, hit_rate=64.3%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1777** | scored: 1777

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 223 | 223 | 220 | 98.7% | 97.9% | +0.8% | 0.012908 |
| `match_over_25` | 213 | 213 | 132 | 62.0% | 44.6% | +17.4% | 0.274852 |
| `away_under_25` | 209 | 209 | 197 | 94.3% | 93.6% | +0.6% | 0.055143 |
| `home_over_05` | 205 | 205 | 190 | 92.7% | 87.4% | +5.3% | 0.071118 |
| `match_over_45` | 185 | 185 | 45 | 24.3% | 25.0% | -0.7% | 0.188426 |
| `match_over_35` | 98 | 98 | 38 | 38.8% | 43.0% | -4.2% | 0.244783 |
| `away_under_15` | 81 | 81 | 67 | 82.7% | 81.5% | +1.2% | 0.142252 |
| `exact_4` | 67 | 67 | 17 | 25.4% | 18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | 41.3% | 37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | 33.9% | 30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | 10.5% | 12.6% | -2.1% | 0.096166 |
| `home_under_35` | 56 | 56 | 52 | 92.9% | 94.4% | -1.5% | 0.065742 |
| `home_under_25` | 44 | 44 | 41 | 93.2% | 91.4% | +1.7% | 0.064534 |
| `btts_no` | 40 | 40 | 17 | 42.5% | 52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | 50.0% | 50.9% | -0.9% | 0.248905 |
| `exact_3` | 32 | 32 | 4 | 12.5% | 22.2% | -9.7% | 0.119085 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `exact_2` | 24 | 24 | 5 | 20.8% | 24.5% | -3.7% | 0.166543 |
| `away_over_05` | 22 | 22 | 19 | 86.4% | 86.0% | +0.3% | 0.117067 |
| `goal_range_6_plus` | 9 | 9 | 1 | 11.1% | 18.7% | -7.6% | 0.102748 |
| `home_under_15` | 9 | 9 | 8 | 88.9% | 81.2% | +7.7% | 0.104019 |
| `match_over_15` | 8 | 8 | 7 | 87.5% | 85.7% | +1.8% | 0.122786 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | 33.3% | 13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1461 | 969 | 66.3% | 63.9% | +2.4% | 0.130648 |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| model | 53 | 37 | 69.8% | 51.8% | +18.0% | 0.264287 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 160 | 16.0% | 20.0% | +4.0% |
| 0.2-0.3 | 220 | 24.8% | 23.6% | -1.1% |
| 0.3-0.4 | 225 | 35.6% | 44.4% | +8.9% |
| 0.4-0.5 | 193 | 45.0% | 49.2% | +4.2% |
| 0.5-0.6 | 110 | 52.8% | 49.1% | -3.7% |
| 0.6-0.7 | 8 | 64.0% | 75.0% | +11.0% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 289 | 84.4% | 88.6% | +4.1% |
| 0.9-1.0 | 568 | 95.3% | 96.0% | +0.7% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=281, MAE=1.479146 goals, bias=-0.37573 (realized − promised), promised avg 3.614164 vs realized 3.238434

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 281 | 23.6% | 30.6% | +7.0% | 0.185164 |
| BTTS-Yes | 281 | 41.5% | 51.6% | +10.1% | 0.259759 |
| Home Over 1.5 | 281 | 72.0% | 59.8% | -12.2% | 0.226946 |
| Over 2.5 | 281 | 71.0% | 62.6% | -8.4% | 0.239604 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 198 | 8.9% | 18.7% | +9.8% |
| 0.1-0.2 | 84 | 10.4% | 26.2% | +15.8% |
| 0.3-0.4 | 72 | 37.8% | 50.0% | +12.2% |
| 0.4-0.5 | 208 | 42.9% | 51.9% | +9.0% |
| 0.6-0.7 | 146 | 66.9% | 58.2% | -8.6% |
| 0.7-0.8 | 125 | 74.8% | 66.4% | -8.4% |
| 0.8-0.9 | 244 | 85.1% | 68.4% | -16.6% |
| 0.9-1.0 | 47 | 91.9% | 78.7% | -13.2% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=104, wins=83, hit_rate=0.798077, ROI=0.082372
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=49, wins=36, hit_rate=0.734694, ROI=-0.000938
- `ml-meta avg_p>=55`: settled=104, wins=66, hit_rate=0.634615, ROI=-0.0294
- `ml-meta avg_p>=60`: settled=5, wins=4, hit_rate=0.8, ROI=0.078
- `ml-meta avg_p>=65`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.25
- `ml-meta avg_p>=70`: settled=3, wins=3, hit_rate=1.0, ROI=0.56
- `ml-meta avg_p>=75`: settled=2, wins=1, hit_rate=0.5, ROI=-0.42

## By bucket

- `CAUTION`: settled=71, wins=43, hit_rate=0.605634, ROI=-0.032254
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=149, wins=113, hit_rate=0.758389, ROI=0.040322
- `WATCHLIST_NO_ODDS`: settled=18, wins=15, hit_rate=0.833333, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=3, hit_rate=0.6, ROI=-0.0825
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=28, wins=21, hit_rate=0.75, ROI=0.119286
- `WATCHLIST_UNKNOWN_CTX`: settled=18, wins=16, hit_rate=0.888889, ROI=0.081111

## By odds source

- `UNKNOWN`: settled=19, wins=15, hit_rate=0.789474, ROI=None
- `betexplorer_odds`: settled=112, wins=83, hit_rate=0.741071, ROI=0.051786
- `bzzoiro_odds`: settled=89, wins=59, hit_rate=0.662921, ROI=-0.034517
- `forebet_best`: settled=13, wins=9, hit_rate=0.692308, ROI=-0.076923
- `scoutingstats_odds`: settled=66, wins=43, hit_rate=0.651515, ROI=-0.079242
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=17, wins=12, hit_rate=0.705882, ROI=-0.056875
- `betexplorer`: settled=112, wins=83, hit_rate=0.741071, ROI=0.051786
- `exact`: settled=147, wins=97, hit_rate=0.659864, ROI=-0.043959
- `fallback`: settled=16, wins=13, hit_rate=0.8125, ROI=0.116875
- `none`: settled=18, wins=15, hit_rate=0.833333, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 112 | 83 | 0.741071 | 112 | 0.051786 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 81 | 54 | 0.666667 | 81 | -0.01521 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 66 | 43 | 0.651515 | 66 | -0.079242 |
| Source fallback (`SOURCE_FALLBACK`) | 16 | 13 | 0.8125 | 16 | 0.116875 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 17 | 12 | 0.705882 | 16 | -0.056875 |
| No usable price (`UNMATCHED`) | 18 | 15 | 0.833333 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 149 | 113 | 0.758389 | 149 | 0.040322 |
| **trusted evidence only** | 104 | 80 | 0.769231 | 104 | 0.066423 |
| **soft evidence only** | 45 | 33 | 0.733333 | 45 | -0.02 |
| evidence: BETEXPLORER_RESCUE | 56 | 46 | 0.821429 | 56 | 0.111607 |
| evidence: BZZOIRO_PRIMARY | 48 | 34 | 0.708333 | 48 | 0.013708 |
| evidence: SCOUTINGSTATS_SOLE | 29 | 19 | 0.655172 | 29 | -0.127931 |
| evidence: SOURCE_FALLBACK | 8 | 7 | 0.875 | 8 | 0.23 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 7 | 0.875 | 8 | 0.12125 |
| odds band: <1.50 | 111 | 90 | 0.810811 | 111 | 0.050252 |
| odds band: 1.50-2.00 | 37 | 22 | 0.594595 | 37 | -0.015405 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.0 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.305 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.335 |
| veto reason: context VETO in ['league'] | 4 | 4 | 1.0 | 4 | 0.4025 |
| veto reason: context VETO in ['odds_band'] | 44 | 37 | 0.840909 | 44 | 0.139773 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.169125 |
| veto reason: context VETO in ['team_a'] | 23 | 17 | 0.73913 | 23 | 0.07913 |
| veto reason: context VETO in ['team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.35 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.2 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.013333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 10 | 5 | 0.5 | 10 | -0.347 |
| veto reason: context VETO in ['team_h'] | 36 | 24 | 0.666667 | 36 | -0.069306 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 36 | 24 | 0.666667 | 36 | 0.070278 |
| contrast CAUTION: BZZOIRO_PRIMARY | 22 | 15 | 0.681818 | 22 | 0.091818 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 7 | 1 | 0.142857 | 7 | -0.757143 |
| contrast CAUTION: SOURCE_FALLBACK | 4 | 3 | 0.75 | 4 | 0.115 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 227 | 165 | 0.726872 | 209 | 0.030804 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 17 | 12 | 0.705882 | 16 | -0.056875 | 9 | 1.335 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 66 | 43 | 0.651515 | 66 | -0.079242 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-21: Alashkert vs Gandzasar (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.46 -> 🟢 WON (Expected prob: 64.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.5% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 3 goals)

### 2026-08-21: Vejle vs Esbjerg (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.58 -> 🟢 WON (Expected prob: 56.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.6% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.5% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.5% (Actual: 2 away goals)

### 2026-08-21: Standard Liège vs RAAL La Louvière (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.88 -> 🟢 WON (Expected prob: 55.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.0% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 0 away goals)

### 2026-08-21: IFK Kumla vs Husqvarna FF (Actual Score: **2-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.5 -> 🟢 WON (Expected prob: 59.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.2% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.4% (Actual: 8 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.2% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.4% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.0% (Actual: 8 goals)

### 2026-08-21: Botafogo vs Cienciano (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.11 -> 🟢 WON (Expected prob: 73.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 77.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 58.6% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.0% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.7% (Actual: 1 goals)

### 2026-08-21: Arsenal vs Coventry City (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.18 -> 🟢 WON (Expected prob: 79.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 36.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 94.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.3% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.4% (Actual: 3 goals)

### 2026-08-21: Ararat vs Pyunik Yerevan (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.29 -> 🟢 WON (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 87.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 58.9% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.9% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.2% (Actual: 2 goals)

### 2026-08-21: Arsenal vs Coventry (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.19 -> 🟢 WON (Expected prob: 73.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.8% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.8% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.5% (Actual: 3 goals)

### 2026-08-21: FC Haka vs SJK Akatemia (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 72.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 61.5% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.8% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.1% (Actual: 2 goals)

### 2026-08-21: Al Riyadh SC vs Al Nassr (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.25 -> 🟢 WON (Expected prob: 68.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.3% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.2% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.7% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 94.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 80.5% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.4% (Actual: 4 goals)

### 2026-08-21: Zamalek SC vs Al-Ittihad Alexandria (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 62.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.2% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.3% (Actual: 0 goals)

### 2026-08-21: FK Sarajevo vs BSK Banja Luka (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.19 -> 🟢 WON (Expected prob: 59.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.3% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.8% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.4% (Actual: 1 goals)

### 2026-08-21: Treaty United vs Cork City (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.49 -> 🔴 LOST (Expected prob: 58.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.4% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.7% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.7% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.1% (Actual: 4 goals)

### 2026-08-21: Kashiwa Reysol vs V-Varen Nagasaki (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 58.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.1% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.1% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.8% (Actual: 2 away goals)

### 2026-08-21: Motorlet Praha vs Dukla Praha B (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🔴 LOST (Expected prob: 58.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.0% (Actual: 0 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 83.4% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.1% (Actual: 0 away goals)

### 2026-08-21: Cardiff Met vs The New Saints (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.39 -> 🟢 WON (Expected prob: 57.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.5% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.3% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.8% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.8% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.3% (Actual: 5 goals)

### 2026-08-21: Bari vs Cavese (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.34 -> 🟢 WON (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.3% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.3% (Actual: 0 away goals)

### 2026-08-21: SV Horn vs Donau (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 74.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 58.9% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.4% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.4% (Actual: 2 goals)

### 2026-08-21: Levadia Tallinn vs Trans Narva (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 62.6% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.8% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.1% (Actual: 4 goals)

### 2026-08-21: FC Tokyo vs JEF United Chiba (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 63.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.3% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.0% (Actual: 2 goals)

### 2026-08-21: Corinthians vs Rosario Central (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 2.15 -> 🟢 WON (Expected prob: 70.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 57.0% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.9% (Actual: 1 goals)

### 2026-08-21: Drogheda United vs St. Patricks Athletic (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.61 -> 🟢 WON (Expected prob: 56.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.8% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.2% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.7% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.6% (Actual: 2 goals)

### 2026-08-21: Stockholm Internazionale vs Järfälla (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 75.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 61.4% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.8% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.6% (Actual: 2 goals)


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
- 2026-08-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Union Berlin W vs Bayern Munich W -> AWAY @ 1.17 (pending_or_unmatched_result); keys=['unionberl']/['bayernmun']
- 2026-08-21 `SKIPPED_VETO` `ml-meta avg_p>=55` — Shamrock Rovers vs Shelbourne FC -> HOME @ 1.8 (pending_or_unmatched_result); keys=['shamrockr']/['shelbourn']

## Ambiguous result examples

- none

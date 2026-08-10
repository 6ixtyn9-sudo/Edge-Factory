# Edge Factory — Recent picks audit (2026-07-12 to 2026-08-10)

## Overall

- archived pick rows: 196
- archived pick dates: 30
- immutable morning-baseline rows: 122
- verified official late-slate additions: 28
- regular-ledger-only legacy rows: 46
- unsafe regular ledgers ignored: 3
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 185
- eligible prior 1x2 picks: 189
- pending/unmatched result picks: 1
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 2
- ambiguous result picks: 0
- wins: 139
- hit rate: +75.1%
- priced picks: 176
- ROI: +0.4%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-10
- same-day rows excluded: 7

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 125 / 185 matches (67.6%)
- **Both Teams to Score (BTTS)**: occurred in 96 / 185 matches (51.9%)
- **Selected Team Over 1.5 Goals**: occurred in 134 / 185 matches (72.4%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 114
- **Total Hits**: 88
- **Overall Hit Rate**: 77.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=12, hits=12, hit_rate=100.0%
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=49, hits=46, hit_rate=93.9%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%
- `match_over_35`: recommended=5, hits=1, hit_rate=20.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **990** | scored: 990

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_35` | 94 | 94 | 38 | +40.4% | +43.2% | -2.8% | 0.249314 |
| `away_under_35` | 89 | 89 | 86 | +96.6% | +97.0% | -0.4% | 0.031761 |
| `match_over_45` | 82 | 82 | 18 | +22.0% | +26.3% | -4.4% | 0.181476 |
| `away_under_25` | 78 | 78 | 74 | +94.9% | +92.4% | +2.5% | 0.050881 |
| `home_over_05` | 74 | 74 | 71 | +95.9% | +89.5% | +6.5% | 0.046876 |
| `exact_4` | 67 | 67 | 17 | +25.4% | +18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | +41.3% | +37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | +33.9% | +30.9% | +3.0% | 0.229007 |
| `match_over_25` | 59 | 59 | 37 | +62.7% | +42.2% | +20.5% | 0.301519 |
| `exact_5` | 57 | 57 | 6 | +10.5% | +12.6% | -2.1% | 0.096166 |
| `btts_no` | 40 | 40 | 17 | +42.5% | +52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | +50.0% | +50.9% | -0.9% | 0.248905 |
| `exact_3` | 32 | 32 | 4 | +12.5% | +22.2% | -9.7% | 0.119085 |
| `home_under_35` | 27 | 27 | 23 | +85.2% | +95.2% | -10.0% | 0.131559 |
| `goal_range_2_3` | 26 | 26 | 8 | +30.8% | +46.1% | -15.4% | 0.233772 |
| `exact_2` | 24 | 24 | 5 | +20.8% | +24.5% | -3.7% | 0.166543 |
| `away_under_15` | 22 | 22 | 19 | +86.4% | +81.0% | +5.4% | 0.120558 |
| `away_over_05` | 15 | 15 | 14 | +93.3% | +87.3% | +6.0% | 0.061723 |
| `home_under_25` | 14 | 14 | 12 | +85.7% | +91.8% | -6.1% | 0.128543 |
| `goal_range_6_plus` | 9 | 9 | 1 | +11.1% | +18.7% | -7.6% | 0.102748 |
| `match_over_15` | 8 | 8 | 7 | +87.5% | +85.7% | +1.8% | 0.122786 |
| `exact_1` | 4 | 4 | 1 | +25.0% | +21.5% | +3.5% | 0.175017 ⚠️low-n |
| `home_under_15` | 4 | 4 | 3 | +75.0% | +81.2% | -6.2% | 0.189446 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | +33.3% | +13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | +0.0% | +11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | +100.0% | +35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 689 | 368 | +53.4% | +53.2% | +0.2% | 0.148565 |
| legacy | 263 | 136 | +51.7% | +52.1% | -0.4% | 0.183796 |
| model | 38 | 24 | +63.2% | +46.1% | +17.0% | 0.280314 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 137 | +15.5% | +19.7% | +4.2% |
| 0.2-0.3 | 149 | +24.8% | +22.1% | -2.7% |
| 0.3-0.4 | 183 | +35.4% | +44.3% | +8.9% |
| 0.4-0.5 | 103 | +45.3% | +38.8% | -6.5% |
| 0.5-0.6 | 78 | +52.6% | +39.7% | -12.8% |
| 0.6-0.7 | 5 | +65.3% | +100.0% | +34.7% |
| 0.7-0.8 | 4 | +74.4% | +50.0% | -24.4% |
| 0.8-0.9 | 92 | +84.8% | +92.4% | +7.6% |
| 0.9-1.0 | 239 | +94.7% | +93.7% | -0.9% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=113, MAE=1.391062 goals, bias=-0.47354 (realized − promised), promised avg 3.765575 vs realized 3.292035

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 226 | +14.2% | +9.7% | -4.5% | 0.090565 |
| Away Over 1.5 | 113 | +22.9% | +32.7% | +9.8% | 0.187187 |
| BTTS-Yes | 113 | +40.6% | +53.1% | +12.5% | 0.267097 |
| Home Over 1.5 | 113 | +74.0% | +60.2% | -13.8% | 0.221265 |
| Over 2.5 | 113 | +73.2% | +65.5% | -7.7% | 0.232697 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 84 | +8.8% | +19.0% | +10.2% |
| 0.1-0.2 | 251 | +13.7% | +11.6% | -2.1% |
| 0.2-0.3 | 4 | +20.8% | +25.0% | +4.2% |
| 0.3-0.4 | 41 | +37.8% | +61.0% | +23.2% |
| 0.4-0.5 | 72 | +42.3% | +48.6% | +6.3% |
| 0.6-0.7 | 35 | +67.7% | +62.9% | -4.9% |
| 0.7-0.8 | 71 | +75.0% | +66.2% | -8.8% |
| 0.8-0.9 | 92 | +86.2% | +70.7% | -15.5% |
| 0.9-1.0 | 28 | +91.7% | +75.0% | -16.7% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=21, wins=13, hit_rate=0.619048, ROI=-0.157895
- `2way-unanimous avg_p>=70`: settled=89, wins=70, hit_rate=0.786517, ROI=0.037747
- `3way-unanimous avg_p>=65`: settled=58, wins=41, hit_rate=0.706897, ROI=-0.037632
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=-0.008571

## By bucket

- `CAUTION`: settled=38, wins=22, hit_rate=0.578947, ROI=-0.105526
- `CERTIFIED_CLEAN`: settled=5, wins=1, hit_rate=0.2, ROI=-0.674
- `SKIPPED_VETO`: settled=105, wins=84, hit_rate=0.8, ROI=0.059981
- `WATCHLIST_NO_ODDS`: settled=9, wins=8, hit_rate=0.888889, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=2, wins=1, hit_rate=0.5, ROI=-0.4
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=6, wins=6, hit_rate=1.0, ROI=0.34
- `WATCHLIST_UNKNOWN_CTX`: settled=20, wins=17, hit_rate=0.85, ROI=0.027

## By odds source

- `UNKNOWN`: settled=9, wins=8, hit_rate=0.888889, ROI=None
- `betexplorer_odds`: settled=84, wins=66, hit_rate=0.785714, ROI=0.028333
- `bzzoiro_odds`: settled=49, wins=37, hit_rate=0.755102, ROI=0.075061
- `forebet_best`: settled=6, wins=3, hit_rate=0.5, ROI=-0.313333
- `scoutingstats_odds`: settled=30, wins=18, hit_rate=0.6, ROI=-0.209
- `zulubet`: settled=7, wins=7, hit_rate=1.0, ROI=0.398571

## By odds match method

- `alias_fuzzy`: settled=10, wins=6, hit_rate=0.6, ROI=-0.264
- `betexplorer`: settled=84, wins=66, hit_rate=0.785714, ROI=0.028333
- `exact`: settled=71, wins=50, hit_rate=0.704225, ROI=-0.010592
- `fallback`: settled=11, wins=9, hit_rate=0.818182, ROI=0.155455
- `none`: settled=9, wins=8, hit_rate=0.888889, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 84 | 66 | 0.785714 | 84 | 0.028333 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 41 | 32 | 0.780488 | 41 | 0.134585 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 30 | 18 | 0.6 | 30 | -0.209 |
| Source fallback (`SOURCE_FALLBACK`) | 11 | 9 | 0.818182 | 11 | 0.155455 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 10 | 6 | 0.6 | 10 | -0.264 |
| No usable price (`UNMATCHED`) | 9 | 8 | 0.888889 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 105 | 84 | 0.8 | 105 | 0.059981 |
| **trusted evidence only** | 83 | 67 | 0.807229 | 83 | 0.069253 |
| **soft evidence only** | 22 | 17 | 0.772727 | 22 | 0.025 |
| evidence: BETEXPLORER_RESCUE | 56 | 46 | 0.821429 | 56 | 0.0625 |
| evidence: BZZOIRO_PRIMARY | 27 | 21 | 0.777778 | 27 | 0.083259 |
| evidence: SCOUTINGSTATS_SOLE | 12 | 8 | 0.666667 | 12 | -0.139167 |
| evidence: SOURCE_FALLBACK | 6 | 6 | 1.0 | 6 | 0.418333 |
| evidence: SUSPECT_ALIAS_FUZZY | 4 | 3 | 0.75 | 4 | -0.0725 |
| odds band: <1.50 | 86 | 71 | 0.825581 | 86 | 0.044395 |
| odds band: 1.50-2.00 | 18 | 12 | 0.666667 | 18 | 0.072222 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.17 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 6 | 4 | 0.666667 | 6 | -0.161667 |
| veto reason: context VETO in ['odds_band'] | 37 | 28 | 0.756757 | 37 | 0.018378 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 5 | 5 | 1.0 | 5 | 0.3666 |
| veto reason: context VETO in ['team_a'] | 14 | 11 | 0.785714 | 14 | 0.123571 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 4 | 3 | 0.75 | 4 | 0.12 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.013333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.46 |
| veto reason: context VETO in ['team_h'] | 13 | 11 | 0.846154 | 13 | 0.085769 |
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
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| contrast CAUTION: BETEXPLORER_RESCUE | 15 | 10 | 0.666667 | 15 | -0.033333 |
| contrast CAUTION: BZZOIRO_PRIMARY | 9 | 9 | 1.0 | 9 | 0.647778 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 9 | 1 | 0.111111 | 9 | -0.811111 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 145 | 115 | 0.793103 | 136 | 0.070647 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 10 | 6 | 0.6 | 10 | -0.264 | 2 | 1.24 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 30 | 18 | 0.6 | 30 | -0.209 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-09: Broadmeadow vs Kahibah (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.32 -> 🔴 LOST (Expected prob: 74.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 81.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (12.7%), [🔴 MISS] 2-1 (10.7%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +94.6% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +53.5% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +92.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +41.2% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +33.4% (Actual: 1 goals)

### 2026-08-09: Sheriff Tiraspol vs Dacia Buiucani (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.32 -> 🟢 WON (Expected prob: 73.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 1-0 (12.7%), [🔴 MISS] 2-0 (12.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +89.2% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +47.9% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +37.8% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +28.4% (Actual: 1 goals)

### 2026-08-09: PEC Zwolle vs Ajax (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.49 -> 🟢 WON (Expected prob: 69.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 37.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.5% (Actual: 2 goals)
  - **Top Scores**: [🟢 HIT] 0-2 (15.8%), [🔴 MISS] 0-1 (14.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +89.9% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +39.6% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +98.4% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +95.1% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected +80.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.2% (Actual: 2 goals)

### 2026-08-09: Shirak FC vs Noah (Actual Score: **3-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.3 -> 🟢 WON (Expected prob: 67.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.6% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 91.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.7% (Actual: 4 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (16.2%), [🔴 MISS] 0-1 (15.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +88.8% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +39.1% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +98.2% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected +95.3% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected +80.8% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +23.0% (Actual: 7 goals)

### 2026-08-09: Hammarby TTF vs FBK Karlstad (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.37 -> 🔴 LOST (Expected prob: 66.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.4% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.5%), [🔴 MISS] 1-0 (15.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.2% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +39.1% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.9% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.7% (Actual: 2 goals)

### 2026-08-09: Athletic Club Boise vs Forward Madison (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 4.0 -> 🔴 LOST (Expected prob: 61.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 83.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (16.3%), [🔴 MISS] 0-1 (16.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +87.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +36.9% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +98.1% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +93.0% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +21.9% (Actual: 3 goals)

### 2026-08-09: Benfica vs Academico Viseu (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🔴 LOST (Expected prob: 78.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.8% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.4% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (13.4%), [🔴 MISS] 4-0 (12.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +52.2% (Actual: 4 goals)

### 2026-08-09: Malmö FF vs Degerfors IF (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 71.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.7%), [🔴 MISS] 3-0 (13.3%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +45.0% (Actual: 3 goals)

### 2026-08-09: Universitatea Craiova vs FC Argeș Pitești (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.67 -> 🔴 LOST (Expected prob: 68.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 86.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (15.1%), [🔴 MISS] 1-0 (13.8%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +91.9% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +42.5% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +35.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +26.2% (Actual: 1 goals)

### 2026-08-09: Benjamín Aceval vs 3 de Noviembre (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.63 -> 🟢 WON (Expected prob: 66.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (15.6%), [🔴 MISS] 1-0 (14.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +90.7% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +39.8% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +24.2% (Actual: 3 goals)

### 2026-08-09: Zenit vs Rodina Moscow (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🔴 LOST (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.4% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.5%), [🔴 MISS] 1-0 (15.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +39.0% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.3% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +81.7% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.7% (Actual: 3 goals)

### 2026-08-09: FC Porto vs Alverca (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.21 -> 🟢 WON (Expected prob: 76.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 4-0 (11.9%), [🔴 MISS] 2-1 (11.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.9% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +51.0% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.5% (Actual: 0 away goals)
    - [🔴 MISS] **Goal Range 4-6**: expected +39.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +37.7% (Actual: 2 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected +32.0% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +30.0% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected +18.8% (Actual: 2 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected +13.1% (Actual: 2 goals)

### 2026-08-09: HNK Hajduk Split vs Istra 1961 (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.39 -> 🔴 LOST (Expected prob: 76.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.3% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 4-0 (11.9%), [🔴 MISS] 2-1 (11.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +90.0% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +50.6% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.8% (Actual: 2 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected +50.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Goal Range 4-6**: expected +38.7% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +36.9% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected +31.5% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +29.7% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected +18.7% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected +12.8% (Actual: 4 goals)

### 2026-08-09: Riga FC vs Ogre United (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 76.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 4-0 (11.9%), [🔴 MISS] 2-1 (11.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +93.1% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +51.6% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +92.1% (Actual: 1 away goals)
    - [🟢 HIT] **Goal Range 4-6**: expected +40.7% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +38.5% (Actual: 5 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected +32.6% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +30.5% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected +19.0% (Actual: 5 goals)
    - [🔴 MISS] **Goal Range 6+**: expected +15.1% (Actual: 5 goals)
    - [🟢 HIT] **Exact Goals: 5**: expected +13.6% (Actual: 5 goals)

### 2026-08-09: Haugesund vs Raufoss (Actual Score: **7-2**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.9% (Actual: 9 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.8% (Actual: 7 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (11.8%), [🔴 MISS] 3-0 (11.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +89.0% (Actual: 7 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +50.2% (Actual: 9 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.5% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +92.7% (Actual: 2 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected +50.1% (Actual: BTTS-Yes)
    - [🔴 MISS] **Goal Range 4-6**: expected +39.8% (Actual: 9 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +38.0% (Actual: 9 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected +32.1% (Actual: 9 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +29.5% (Actual: 9 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected +18.9% (Actual: 9 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected +13.2% (Actual: 9 goals)

### 2026-08-09: Vikingur Reykjavik vs IBV Vestmannaeyjar (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.31 -> 🔴 LOST (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (12.6%), [🔴 MISS] 3-0 (12.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +93.8% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +48.4% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +91.1% (Actual: 2 away goals)
    - [🟢 HIT] **Goal Range 4-6**: expected +41.1% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +38.4% (Actual: 4 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected +32.8% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +29.0% (Actual: 4 goals)
    - [🟢 HIT] **Exact Goals: 4**: expected +19.1% (Actual: 4 goals)
    - [🔴 MISS] **Goal Range 6+**: expected +15.5% (Actual: 4 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected +13.7% (Actual: 4 goals)

### 2026-08-09: FC Sion vs FC Vaduz (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.47 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (12.2%), [🔴 MISS] 1-0 (12.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.5% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +48.1% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.2% (Actual: 2 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected +50.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Goal Range 4-6**: expected +39.1% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +37.3% (Actual: 5 goals)
    - [🟢 HIT] **Goal Range 4-5**: expected +31.7% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +28.1% (Actual: 5 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected +18.7% (Actual: 5 goals)
    - [🟢 HIT] **Exact Goals: 5**: expected +12.9% (Actual: 5 goals)

### 2026-08-09: Lech Poznan vs Piast Gliwice (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.62 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.5%), [🟢 HIT] 3-0 (13.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +92.1% (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +44.8% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.4% (Actual: 0 away goals)
    - [🔴 MISS] **Goal Range 4-6**: expected +38.3% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +36.1% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected +31.2% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +27.3% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected +18.6% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected +12.6% (Actual: 3 goals)

### 2026-08-09: Rangers vs Hibernian (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.58 -> 🔴 LOST (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.5%), [🔴 MISS] 3-0 (13.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.1% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +44.8% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.0% (Actual: 2 away goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected +50.5% (Actual: BTTS-Yes)
    - [🔴 MISS] **Goal Range 4-6**: expected +38.4% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +36.2% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected +31.2% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +27.3% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected +18.6% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected +12.7% (Actual: 3 goals)

### 2026-08-09: Charlestown City vs Maitland FC (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.63 -> 🟢 WON (Expected prob: 69.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 32.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.4% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (18.1%), [🔴 MISS] 0-1 (16.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +90.2% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +45.6% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +95.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +90.1% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +35.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +26.9% (Actual: 3 goals)

### 2026-08-09: Juticalpa vs CD Olimpia (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.25 -> 🟢 WON (Expected prob: 66.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.5% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (18.9%), [🔴 MISS] 0-1 (14.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +88.0% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +39.9% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +98.6% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +95.3% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected +82.8% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.8% (Actual: 4 goals)

### 2026-08-09: Palmeiras vs Internacional (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🔴 LOST (Expected prob: 65.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.7% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.4%), [🔴 MISS] 1-0 (14.9%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +38.7% (Actual: 0 goals)

### 2026-08-09: Deportivo Moron vs Acassuso (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 64.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.6%), [🔴 MISS] 1-0 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +90.2% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +37.6% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +21.8% (Actual: 5 goals)

### 2026-08-09: Septemvri Sofia vs CSKA-Sofia (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.49 -> 🟢 WON (Expected prob: 64.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (17.1%), [🔴 MISS] 0-1 (15.4%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +37.9% (Actual: 3 goals)

### 2026-08-09: FC St. Pauli vs SpVgg Greuther Furth (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🔴 LOST (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.0% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.6%), [🔴 MISS] 1-0 (15.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +89.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +36.8% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +21.4% (Actual: 2 goals)

### 2026-08-09: Trujillanos FC vs Deportivo Tachira (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.7 -> 🟢 WON (Expected prob: 61.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.9% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 0-1 (16.1%), [🔴 MISS] 0-2 (15.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +87.0% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +36.5% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +98.6% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +93.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +21.9% (Actual: 4 goals)

### 2026-08-09: Debreceni VSC vs Nyiregyhaza (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 63.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.3% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.4%), [🟢 HIT] 1-0 (14.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +88.3% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +37.4% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +21.3% (Actual: 1 goals)

### 2026-08-09: FC Astana vs Okzhetpes (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.6%), [🔴 MISS] 1-0 (15.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +89.3% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +36.8% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +21.4% (Actual: 3 goals)

### 2026-08-09: Levadia Tallinn vs Nõmme United (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 68.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.6% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.0% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (14.8%), [🔴 MISS] 1-0 (14.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.5% (Actual: 5 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +41.9% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.4% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +35.5% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +25.7% (Actual: 5 goals)

### 2026-08-09: FBC Melgar vs FC Cajamarca (Actual Score: **2-4**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🔴 LOST (Expected prob: 61.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.0% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 4 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.5%), [🔴 MISS] 1-0 (15.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +88.9% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +36.4% (Actual: 6 goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected +98.7% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected +94.5% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +80.3% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +20.9% (Actual: 6 goals)

### 2026-08-09: Slavia Praha vs Pardubice (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 77.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.3% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 4-0 (12.6%), [🔴 MISS] 3-0 (12.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +92.0% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +51.0% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +96.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +91.3% (Actual: 1 away goals)
    - [🔴 MISS] **Goal Range 4-6**: expected +41.2% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +38.4% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 4-5**: expected +32.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +29.1% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 4**: expected +19.1% (Actual: 3 goals)
    - [🔴 MISS] **Goal Range 6+**: expected +15.7% (Actual: 3 goals)
    - [🔴 MISS] **Exact Goals: 5**: expected +13.8% (Actual: 3 goals)

### 2026-08-09: Epitsentr Dunayivtsi vs Shakhtar Donetsk (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.33 -> 🟢 WON (Expected prob: 65.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.7% (Actual: 2 goals)
  - **Top Scores**: [🟢 HIT] 0-2 (16.1%), [🔴 MISS] 0-1 (15.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +89.4% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +39.6% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +97.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +93.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.6% (Actual: 2 goals)

### 2026-08-09: Corinthians W vs Santos W (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 64.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.6%), [🔴 MISS] 1-0 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +90.6% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected +37.7% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.8% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +21.8% (Actual: 5 goals)

### 2026-08-09: Asane vs Kongsvinger (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.48 -> 🟢 WON (Expected prob: 64.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (16.6%), [🔴 MISS] 0-1 (15.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +88.8% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +38.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +98.2% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +93.1% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +22.5% (Actual: 3 goals)

### 2026-08-09: São Paulo W vs RB Bragantino W (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 64.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.9% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.2%), [🟢 HIT] 1-0 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +37.8% (Actual: 1 goals)

### 2026-08-09: KuPS vs Turku PS (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🔴 LOST (Expected prob: 75.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.6% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (12.0%), [🔴 MISS] 3-0 (11.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +90.3% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +51.3% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +96.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +91.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +40.3% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +30.7% (Actual: 2 goals)

### 2026-08-09: FK Jablonec vs Slovácko (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.64 -> 🟢 WON (Expected prob: 75.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 76.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (11.8%), [🔴 MISS] 3-1 (11.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +87.9% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +49.9% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +37.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +29.3% (Actual: 1 goals)

### 2026-08-09: Anderlecht vs RAAL La Louvière (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🟢 WON (Expected prob: 67.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.5%), [🔴 MISS] 1-0 (13.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.5% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +40.0% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.4% (Actual: 3 goals)

### 2026-08-09: Sparta Rotterdam vs Feyenoord (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.66 -> 🟢 WON (Expected prob: 66.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (18.3%), [🟢 HIT] 0-1 (14.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +87.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +40.7% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +96.5% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +92.5% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.8% (Actual: 1 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 3 |
- 2026-07-19 `POSTPONED` `WATCHLIST_NO_ODDS` — FC Levadia Tallinn vs Tammeka (verified_disposition); excluded from win/loss/ROI
- 2026-07-25 `POSTPONED` `WATCHLIST_NO_ODDS` — Coquimbo Unido vs Universidad de Concepcion (verified_disposition); excluded from win/loss/ROI
- 2026-07-26 `POSTPONED` `SKIPPED_VETO` — Super Nova vs Riga (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- 2026-08-08 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Belshina vs Dinamo Minsk -> AWAY @ 1.32 (pending_or_unmatched_result); keys=['belshina', 'belshinab']/['dinamomin']

## Ambiguous result examples

- none

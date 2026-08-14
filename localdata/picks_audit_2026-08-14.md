# Edge Factory — Recent picks audit (2026-07-16 to 2026-08-14)

## Overall

- archived pick rows: 233
- archived pick dates: 30
- immutable morning-baseline rows: 146
- verified official late-slate additions: 30
- regular-ledger-only legacy rows: 57
- unsafe regular ledgers ignored: 3
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 217
- eligible prior 1x2 picks: 222
- pending/unmatched result picks: 2
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 5
- ambiguous result picks: 0
- wins: 154
- hit rate: +71.0%
- priced picks: 207
- ROI: -4.8%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-14
- same-day rows excluded: 11

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 143 / 217 matches (65.9%)
- **Both Teams to Score (BTTS)**: occurred in 114 / 217 matches (52.5%)
- **Selected Team Over 1.5 Goals**: occurred in 152 / 217 matches (70.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 157
- **Total Hits**: 124
- **Overall Hit Rate**: 79.0%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=72, hits=68, hit_rate=94.4%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=14, hits=8, hit_rate=57.1%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1184** | scored: 1184

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 119 | 119 | 116 | +97.5% | +97.2% | +0.2% | 0.023932 |
| `match_over_45` | 117 | 117 | 26 | +22.2% | +25.5% | -3.3% | 0.179539 |
| `away_under_25` | 107 | 107 | 101 | +94.4% | +92.8% | +1.5% | 0.054598 |
| `home_over_05` | 102 | 102 | 98 | +96.1% | +88.8% | +7.2% | 0.046343 |
| `match_over_35` | 98 | 98 | 38 | +38.8% | +43.0% | -4.2% | 0.244783 |
| `match_over_25` | 89 | 89 | 54 | +60.7% | +41.6% | +19.1% | 0.29224 |
| `exact_4` | 67 | 67 | 17 | +25.4% | +18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | +41.3% | +37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | +33.9% | +30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | +10.5% | +12.6% | -2.1% | 0.096166 |
| `btts_no` | 40 | 40 | 17 | +42.5% | +52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | +50.0% | +50.9% | -0.9% | 0.248905 |
| `home_under_35` | 37 | 37 | 33 | +89.2% | +94.5% | -5.4% | 0.09764 |
| `exact_3` | 32 | 32 | 4 | +12.5% | +22.2% | -9.7% | 0.119085 |
| `away_under_15` | 31 | 31 | 26 | +83.9% | +81.0% | +2.8% | 0.136628 |
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
| hybrid_cohort | 879 | 506 | +57.6% | +56.9% | +0.6% | 0.14058 |
| legacy | 263 | 136 | +51.7% | +52.1% | -0.4% | 0.183796 |
| model | 42 | 28 | +66.7% | +47.2% | +19.4% | 0.278725 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 143 | +15.7% | +19.6% | +3.9% |
| 0.2-0.3 | 178 | +24.8% | +22.5% | -2.3% |
| 0.3-0.4 | 202 | +35.6% | +45.0% | +9.5% |
| 0.4-0.5 | 118 | +45.1% | +39.8% | -5.2% |
| 0.5-0.6 | 78 | +52.6% | +39.7% | -12.8% |
| 0.6-0.7 | 5 | +65.3% | +100.0% | +34.7% |
| 0.7-0.8 | 4 | +74.4% | +50.0% | -24.4% |
| 0.8-0.9 | 135 | +84.7% | +90.4% | +5.6% |
| 0.9-1.0 | 321 | +94.8% | +94.7% | -0.0% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=156, MAE=1.445769 goals, bias=-0.509359 (realized − promised), promised avg 3.714487 vs realized 3.205128

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 312 | +14.7% | +10.3% | -4.4% | 0.094323 |
| Away Over 1.5 | 156 | +25.0% | +31.4% | +6.4% | 0.207742 |
| BTTS-Yes | 156 | +40.7% | +53.2% | +12.5% | 0.265661 |
| Home Over 1.5 | 156 | +71.4% | +59.0% | -12.4% | 0.225697 |
| Over 2.5 | 156 | +72.3% | +62.2% | -10.2% | 0.243322 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 116 | +8.8% | +19.8% | +11.1% |
| 0.1-0.2 | 348 | +14.1% | +12.1% | -2.0% |
| 0.2-0.3 | 4 | +20.8% | +25.0% | +4.2% |
| 0.3-0.4 | 55 | +37.7% | +56.4% | +18.7% |
| 0.4-0.5 | 101 | +42.4% | +51.5% | +9.1% |
| 0.6-0.7 | 62 | +67.5% | +56.5% | -11.0% |
| 0.7-0.8 | 86 | +74.8% | +65.1% | -9.6% |
| 0.8-0.9 | 131 | +85.9% | +66.4% | -19.5% |
| 0.9-1.0 | 33 | +91.8% | +78.8% | -13.0% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=96, wins=76, hit_rate=0.791667, ROI=0.036213
- `3way-unanimous avg_p>=65`: settled=59, wins=42, hit_rate=0.711864, ROI=-0.033534
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.272222
- `ml-meta avg_p>=55`: settled=20, wins=9, hit_rate=0.45, ROI=-0.35

## By bucket

- `CAUTION`: settled=44, wins=24, hit_rate=0.545455, ROI=-0.162727
- `CERTIFIED_CLEAN`: settled=13, wins=6, hit_rate=0.461538, ROI=-0.336154
- `SKIPPED_VETO`: settled=116, wins=88, hit_rate=0.758621, ROI=0.019034
- `WATCHLIST_NO_ODDS`: settled=10, wins=9, hit_rate=0.9, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=2, wins=1, hit_rate=0.5, ROI=-0.4
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=10, wins=6, hit_rate=0.6, ROI=-0.196
- `WATCHLIST_UNKNOWN_CTX`: settled=22, wins=20, hit_rate=0.909091, ROI=0.099545

## By odds source

- `UNKNOWN`: settled=10, wins=9, hit_rate=0.9, ROI=None
- `betexplorer_odds`: settled=90, wins=70, hit_rate=0.777778, ROI=0.038333
- `bzzoiro_odds`: settled=67, wins=43, hit_rate=0.641791, ROI=-0.089433
- `forebet_best`: settled=6, wins=3, hit_rate=0.5, ROI=-0.313333
- `scoutingstats_odds`: settled=33, wins=18, hit_rate=0.545455, ROI=-0.280909
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=13, wins=9, hit_rate=0.692308, ROI=-0.133846
- `betexplorer`: settled=90, wins=70, hit_rate=0.777778, ROI=0.038333
- `exact`: settled=92, wins=56, hit_rate=0.608696, ROI=-0.145891
- `fallback`: settled=12, wins=10, hit_rate=0.833333, ROI=0.151667
- `none`: settled=10, wins=9, hit_rate=0.9, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 90 | 70 | 0.777778 | 90 | 0.038333 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 59 | 38 | 0.644068 | 59 | -0.070373 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 33 | 18 | 0.545455 | 33 | -0.280909 |
| Source fallback (`SOURCE_FALLBACK`) | 12 | 10 | 0.833333 | 12 | 0.151667 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 13 | 9 | 0.692308 | 13 | -0.133846 |
| No usable price (`UNMATCHED`) | 10 | 9 | 0.9 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 116 | 88 | 0.758621 | 116 | 0.019034 |
| **trusted evidence only** | 91 | 68 | 0.747253 | 91 | 0.00833 |
| **soft evidence only** | 25 | 20 | 0.8 | 25 | 0.058 |
| evidence: BETEXPLORER_RESCUE | 53 | 42 | 0.792453 | 53 | 0.045283 |
| evidence: BZZOIRO_PRIMARY | 38 | 26 | 0.684211 | 38 | -0.043211 |
| evidence: SCOUTINGSTATS_SOLE | 12 | 8 | 0.666667 | 12 | -0.139167 |
| evidence: SOURCE_FALLBACK | 6 | 6 | 1.0 | 6 | 0.418333 |
| evidence: SUSPECT_ALIAS_FUZZY | 7 | 6 | 0.857143 | 7 | 0.087143 |
| odds band: <1.50 | 94 | 73 | 0.776596 | 94 | -0.007468 |
| odds band: 1.50-2.00 | 21 | 14 | 0.666667 | 21 | 0.082381 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.136 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 7 | 5 | 0.714286 | 7 | -0.082857 |
| veto reason: context VETO in ['odds_band'] | 41 | 31 | 0.756098 | 41 | 0.023171 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.130429 |
| veto reason: context VETO in ['team_a'] | 16 | 13 | 0.8125 | 16 | 0.164375 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.136 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.013333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 5 | 2 | 0.4 | 5 | -0.512 |
| veto reason: context VETO in ['team_h'] | 17 | 12 | 0.705882 | 17 | -0.072647 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| contrast CAUTION: BETEXPLORER_RESCUE | 18 | 12 | 0.666667 | 18 | -0.019444 |
| contrast CAUTION: BZZOIRO_PRIMARY | 13 | 9 | 0.692308 | 13 | 0.117692 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 8 | 1 | 0.125 | 8 | -0.7875 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 171 | 127 | 0.74269 | 161 | 0.006944 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 13 | 9 | 0.692308 | 13 | -0.133846 | 5 | 1.302 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 33 | 18 | 0.545455 | 33 | -0.280909 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-13: Ilves vs HNK Rijeka (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.8 -> 🔴 LOST (Expected prob: 55.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-2 (17.7%), [🔴 MISS] 0-2 (16.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +90.4% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +87.8% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +40.5% (Actual: 2 goals)

### 2026-08-13: Santos vs Macara (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 55.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (19.3%), [🟢 HIT] 2-1 (19.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +85.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.3% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +37.0% (Actual: 3 goals)

### 2026-08-13: FC Urartu vs Syunik (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 62.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.2%), [🔴 MISS] 1-0 (16.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +89.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.7% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +39.7% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +18.5% (Actual: 3 goals)

### 2026-08-13: NSI Runavik vs FC Lugano (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.364 -> 🔴 LOST (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 95.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (15.1%), [🔴 MISS] 0-1 (14.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +90.5% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +89.5% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +41.4% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +22.5% (Actual: 4 goals)

### 2026-08-13: Omonia Nicosia vs Lincoln Red Imps (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 71.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (13.9%), [🔴 MISS] 2-0 (13.5%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +46.8% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +93.4% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +28.1% (Actual: 1 goals)

### 2026-08-13: FC Nordsjælland vs Valur Reykjavik (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.12 -> 🟢 WON (Expected prob: 70.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.4%), [🔴 MISS] 3-0 (13.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +45.8% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +93.4% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.8% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +26.4% (Actual: 5 goals)

### 2026-08-13: Shelbourne FC vs Ajax (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.18 -> 🔴 LOST (Expected prob: 69.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 32.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 92.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.4% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (18.1%), [🔴 MISS] 0-1 (16.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +93.2% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +92.1% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +40.7% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +24.8% (Actual: 4 goals)

### 2026-08-13: St Gallen vs Sheriff Tiraspol (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 67.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.3% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (16.4%), [🔴 MISS] 1-0 (13.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +92.1% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +97.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +82.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +42.8% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +22.5% (Actual: 6 goals)

### 2026-08-13: Dinamo Minsk vs Sporting Braga (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.43 -> 🔴 LOST (Expected prob: 65.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.9% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.4% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (18.4%), [🔴 MISS] 0-1 (13.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +93.4% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +92.5% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +40.6% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +22.5% (Actual: 0 goals)

### 2026-08-13: Midtjylland vs Bohemians FC (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 63.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.0% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.5%), [🔴 MISS] 1-0 (16.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +90.5% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +96.7% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +82.1% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +39.7% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +19.1% (Actual: 5 goals)

### 2026-08-13: FC Sion vs FC Noah (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 63.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.3%), [🔴 MISS] 1-0 (16.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +89.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.6% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +39.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +18.7% (Actual: 3 goals)

### 2026-08-13: Rangers vs Jagiellonia (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.606 -> 🔴 LOST (Expected prob: 56.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.0% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-1 (18.3%), [🔴 MISS] 1-0 (18.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +38.0% (Actual: 2 goals)

### 2026-08-13: Dunajska Streda vs Twente (Actual Score: **3-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.57 -> 🔴 LOST (Expected prob: 56.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.3% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 1-2 (16.9%), [🔴 MISS] 0-2 (16.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +92.1% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected +90.0% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +40.6% (Actual: 6 goals)


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

## Ambiguous result examples

- none

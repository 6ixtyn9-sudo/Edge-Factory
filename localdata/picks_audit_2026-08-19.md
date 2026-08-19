# Edge Factory — Recent picks audit (2026-07-21 to 2026-08-19)

## Overall

- archived pick rows: 300
- archived pick dates: 30
- immutable morning-baseline rows: 155
- verified official late-slate additions: 27
- regular-ledger-only legacy rows: 118
- unsafe regular ledgers ignored: 4
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 283
- eligible prior 1x2 picks: 293
- pending/unmatched result picks: 8
- voided postponed/cancelled/abandoned events: 2
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 5
- ambiguous result picks: 0
- wins: 199
- hit rate: +70.3%
- priced picks: 266
- ROI: -2.0%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-19
- same-day rows excluded: 7

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 186 / 283 matches (65.7%)
- **Both Teams to Score (BTTS)**: occurred in 154 / 283 matches (54.4%)
- **Selected Team Over 1.5 Goals**: occurred in 199 / 283 matches (70.3%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 243
- **Total Hits**: 198
- **Overall Hit Rate**: 81.5%

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
- `match_over_25`: recommended=45, hits=33, hit_rate=73.3%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1603** | scored: 1603

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 194 | 194 | 191 | +98.5% | +97.8% | +0.7% | 0.014774 |
| `away_under_25` | 181 | 181 | 169 | +93.4% | +93.7% | -0.4% | 0.062878 |
| `home_over_05` | 177 | 177 | 165 | +93.2% | +87.7% | +5.6% | 0.067792 |
| `match_over_25` | 174 | 174 | 111 | +63.8% | +42.8% | +21.0% | 0.280135 |
| `match_over_45` | 161 | 161 | 41 | +25.5% | +25.1% | +0.4% | 0.193477 |
| `match_over_35` | 98 | 98 | 38 | +38.8% | +43.0% | -4.2% | 0.244783 |
| `away_under_15` | 74 | 74 | 60 | +81.1% | +81.6% | -0.5% | 0.152177 |
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
| hybrid_cohort | 1293 | 840 | +65.0% | +62.7% | +2.3% | 0.135692 |
| legacy | 263 | 136 | +51.7% | +52.1% | -0.4% | 0.183796 |
| model | 47 | 33 | +70.2% | +48.7% | +21.5% | 0.272379 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 153 | +15.9% | +20.3% | +4.4% |
| 0.2-0.3 | 207 | +24.8% | +23.7% | -1.1% |
| 0.3-0.4 | 221 | +35.6% | +45.2% | +9.6% |
| 0.4-0.5 | 176 | +44.6% | +50.0% | +5.4% |
| 0.5-0.6 | 91 | +52.5% | +45.1% | -7.5% |
| 0.6-0.7 | 5 | +65.3% | +100.0% | +34.7% |
| 0.7-0.8 | 4 | +74.4% | +50.0% | -24.4% |
| 0.8-0.9 | 250 | +84.4% | +88.0% | +3.6% |
| 0.9-1.0 | 496 | +95.3% | +95.4% | +0.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=242, MAE=1.447769 goals, bias=-0.343719 (realized − promised), promised avg 3.624711 vs realized 3.280992

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 484 | +15.3% | +9.9% | -5.3% | 0.092385 |
| Away Over 1.5 | 242 | +23.0% | +31.0% | +8.0% | 0.20028 |
| BTTS-Yes | 242 | +41.4% | +54.5% | +13.2% | 0.26544 |
| Home Over 1.5 | 242 | +72.6% | +60.3% | -12.3% | 0.224818 |
| Over 2.5 | 242 | +71.1% | +64.0% | -7.1% | 0.233854 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 173 | +8.9% | +19.7% | +10.7% |
| 0.1-0.2 | 548 | +14.6% | +12.2% | -2.4% |
| 0.2-0.3 | 6 | +20.8% | +16.7% | -4.1% |
| 0.3-0.4 | 66 | +37.8% | +54.5% | +16.7% |
| 0.4-0.5 | 175 | +42.8% | +54.3% | +11.5% |
| 0.6-0.7 | 121 | +66.9% | +58.7% | -8.2% |
| 0.7-0.8 | 112 | +74.7% | +68.8% | -6.0% |
| 0.8-0.9 | 210 | +85.2% | +68.1% | -17.1% |
| 0.9-1.0 | 41 | +91.7% | +78.0% | -13.7% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=97, wins=77, hit_rate=0.793814, ROI=0.071494
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=51, wins=37, hit_rate=0.72549, ROI=-0.0183
- `3way-unanimous home-only avg_p>=60`: settled=8, wins=7, hit_rate=0.875, ROI=0.2475
- `ml-meta avg_p>=55`: settled=79, wins=47, hit_rate=0.594937, ROI=-0.096133
- `ml-meta avg_p>=60`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.11
- `ml-meta avg_p>=65`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.25
- `ml-meta avg_p>=70`: settled=1, wins=1, hit_rate=1.0, ROI=0.42
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.16

## By bucket

- `CAUTION`: settled=61, wins=34, hit_rate=0.557377, ROI=-0.105738
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=143, wins=109, hit_rate=0.762238, ROI=0.051245
- `WATCHLIST_NO_ODDS`: settled=16, wins=14, hit_rate=0.875, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=4, wins=2, hit_rate=0.5, ROI=-0.156667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=20, wins=15, hit_rate=0.75, ROI=0.04
- `WATCHLIST_UNKNOWN_CTX`: settled=18, wins=16, hit_rate=0.888889, ROI=0.081111

## By odds source

- `UNKNOWN`: settled=17, wins=14, hit_rate=0.823529, ROI=None
- `betexplorer_odds`: settled=105, wins=78, hit_rate=0.742857, ROI=0.046286
- `bzzoiro_odds`: settled=89, wins=58, hit_rate=0.651685, ROI=-0.048449
- `forebet_best`: settled=9, wins=6, hit_rate=0.666667, ROI=-0.095556
- `scoutingstats_odds`: settled=52, wins=32, hit_rate=0.615385, ROI=-0.1675
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=16, wins=11, hit_rate=0.6875, ROI=-0.07
- `betexplorer`: settled=105, wins=78, hit_rate=0.742857, ROI=0.046286
- `exact`: settled=133, wins=85, hit_rate=0.639098, ROI=-0.084075
- `fallback`: settled=13, wins=11, hit_rate=0.846154, ROI=0.165385
- `none`: settled=16, wins=14, hit_rate=0.875, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 105 | 78 | 0.742857 | 105 | 0.046286 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 81 | 53 | 0.654321 | 81 | -0.030519 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 52 | 32 | 0.615385 | 52 | -0.1675 |
| Source fallback (`SOURCE_FALLBACK`) | 13 | 11 | 0.846154 | 13 | 0.165385 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 16 | 11 | 0.6875 | 15 | -0.07 |
| No usable price (`UNMATCHED`) | 16 | 14 | 0.875 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 143 | 109 | 0.762238 | 143 | 0.051245 |
| **trusted evidence only** | 106 | 82 | 0.773585 | 106 | 0.079132 |
| **soft evidence only** | 37 | 27 | 0.72973 | 37 | -0.028649 |
| evidence: BETEXPLORER_RESCUE | 55 | 46 | 0.836364 | 55 | 0.134545 |
| evidence: BZZOIRO_PRIMARY | 51 | 36 | 0.705882 | 51 | 0.019373 |
| evidence: SCOUTINGSTATS_SOLE | 22 | 13 | 0.590909 | 22 | -0.221364 |
| evidence: SOURCE_FALLBACK | 7 | 7 | 1.0 | 7 | 0.405714 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 7 | 0.875 | 8 | 0.12125 |
| odds band: <1.50 | 107 | 86 | 0.803738 | 107 | 0.040075 |
| odds band: 1.50-2.00 | 34 | 21 | 0.617647 | 34 | 0.025294 |
| odds band: 2.00-3.00 | 2 | 2 | 1.0 | 2 | 1.09 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.136 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 6 | 5 | 0.833333 | 6 | 0.07 |
| veto reason: context VETO in ['odds_band'] | 43 | 35 | 0.813953 | 43 | 0.101163 |
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
| contrast CAUTION: BETEXPLORER_RESCUE | 30 | 19 | 0.633333 | 30 | 0.014667 |
| contrast CAUTION: BZZOIRO_PRIMARY | 19 | 12 | 0.631579 | 19 | 0.023684 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 7 | 1 | 0.142857 | 7 | -0.757143 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 215 | 156 | 0.725581 | 199 | 0.022804 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 16 | 11 | 0.6875 | 15 | -0.07 | 8 | 1.359375 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 52 | 32 | 0.615385 | 52 | -0.1675 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-18: Palestino vs Huachipato (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 57.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.7%), [🔴 MISS] 2-1 (17.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +47.8% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.9% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.6% (Actual: 1 away goals)

### 2026-08-18: Pachuca vs Puebla (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🔴 LOST (Expected prob: 63.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.5%), [🔴 MISS] 1-0 (16.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +49.3% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +85.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected +95.2% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +80.9% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +19.2% (Actual: 5 goals)

### 2026-08-18: FC Heidenheim vs Bayern Munich (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.16 -> 🟢 WON (Expected prob: 75.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.0% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 17.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 96.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 89.3% (Actual: 4 goals)
  - **Top Scores**: [🔴 MISS] 0-3 (21.4%), [🔴 MISS] 0-5 (14.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +56.4% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +24.7% (Actual: 6 goals)


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

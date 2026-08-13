# Edge Factory — Recent picks audit (2026-07-15 to 2026-08-13)

## Overall

- archived pick rows: 224
- archived pick dates: 30
- immutable morning-baseline rows: 148
- verified official late-slate additions: 30
- regular-ledger-only legacy rows: 46
- unsafe regular ledgers ignored: 3
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 206
- eligible prior 1x2 picks: 211
- pending/unmatched result picks: 2
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 5
- ambiguous result picks: 0
- wins: 149
- hit rate: +72.3%
- priced picks: 196
- ROI: -2.7%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-13
- same-day rows excluded: 13

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 135 / 206 matches (65.5%)
- **Both Teams to Score (BTTS)**: occurred in 106 / 206 matches (51.5%)
- **Selected Team Over 1.5 Goals**: occurred in 144 / 206 matches (69.9%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 144
- **Total Hits**: 112
- **Overall Hit Rate**: 77.8%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=66, hits=62, hit_rate=93.9%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=12, hits=7, hit_rate=58.3%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1122** | scored: 1122

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 111 | 111 | 108 | +97.3% | +97.2% | +0.1% | 0.025636 |
| `match_over_45` | 108 | 108 | 23 | +21.3% | +25.7% | -4.4% | 0.174983 |
| `away_under_25` | 99 | 99 | 93 | +93.9% | +92.6% | +1.3% | 0.058835 |
| `match_over_35` | 98 | 98 | 38 | +38.8% | +43.0% | -4.2% | 0.244783 |
| `home_over_05` | 94 | 94 | 90 | +95.7% | +88.7% | +7.0% | 0.049356 |
| `match_over_25` | 76 | 76 | 45 | +59.2% | +41.7% | +17.5% | 0.291533 |
| `exact_4` | 67 | 67 | 17 | +25.4% | +18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | +41.3% | +37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | +33.9% | +30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | +10.5% | +12.6% | -2.1% | 0.096166 |
| `btts_no` | 40 | 40 | 17 | +42.5% | +52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | +50.0% | +50.9% | -0.9% | 0.248905 |
| `exact_3` | 32 | 32 | 4 | +12.5% | +22.2% | -9.7% | 0.119085 |
| `home_under_35` | 32 | 32 | 28 | +87.5% | +95.0% | -7.5% | 0.111764 |
| `goal_range_2_3` | 26 | 26 | 8 | +30.8% | +46.1% | -15.4% | 0.233772 |
| `away_under_15` | 25 | 25 | 21 | +84.0% | +81.0% | +3.0% | 0.135344 |
| `exact_2` | 24 | 24 | 5 | +20.8% | +24.5% | -3.7% | 0.166543 |
| `away_over_05` | 21 | 21 | 18 | +85.7% | +86.3% | -0.6% | 0.120937 |
| `home_under_25` | 20 | 20 | 18 | +90.0% | +92.0% | -2.0% | 0.091825 |
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
| hybrid_cohort | 817 | 456 | +55.8% | +55.9% | -0.1% | 0.1417 |
| legacy | 263 | 136 | +51.7% | +52.1% | -0.4% | 0.183796 |
| model | 42 | 28 | +66.7% | +47.2% | +19.4% | 0.278725 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 140 | +15.6% | +19.3% | +3.7% |
| 0.2-0.3 | 172 | +24.8% | +22.1% | -2.7% |
| 0.3-0.4 | 197 | +35.5% | +44.2% | +8.6% |
| 0.4-0.5 | 110 | +45.2% | +38.2% | -7.1% |
| 0.5-0.6 | 78 | +52.6% | +39.7% | -12.8% |
| 0.6-0.7 | 5 | +65.3% | +100.0% | +34.7% |
| 0.7-0.8 | 4 | +74.4% | +50.0% | -24.4% |
| 0.8-0.9 | 122 | +84.7% | +91.0% | +6.3% |
| 0.9-1.0 | 294 | +94.7% | +94.2% | -0.5% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=143, MAE=1.446923 goals, bias=-0.548462 (realized − promised), promised avg 3.737273 vs realized 3.188811

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 286 | +14.5% | +10.8% | -3.7% | 0.098301 |
| Away Over 1.5 | 143 | +23.7% | +31.5% | +7.7% | 0.209827 |
| BTTS-Yes | 143 | +40.7% | +51.7% | +11.0% | 0.263036 |
| Home Over 1.5 | 143 | +72.9% | +58.0% | -14.8% | 0.217101 |
| Over 2.5 | 143 | +72.7% | +61.5% | -11.2% | 0.245548 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 109 | +8.8% | +19.3% | +10.5% |
| 0.1-0.2 | 316 | +14.0% | +12.3% | -1.6% |
| 0.2-0.3 | 4 | +20.8% | +25.0% | +4.2% |
| 0.3-0.4 | 51 | +37.8% | +56.9% | +19.0% |
| 0.4-0.5 | 92 | +42.3% | +48.9% | +6.6% |
| 0.6-0.7 | 52 | +67.6% | +53.8% | -13.7% |
| 0.7-0.8 | 83 | +74.8% | +65.1% | -9.8% |
| 0.8-0.9 | 118 | +86.0% | +66.1% | -19.9% |
| 0.9-1.0 | 33 | +91.8% | +78.8% | -13.0% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=95, wins=76, hit_rate=0.8, ROI=0.055034
- `3way-unanimous avg_p>=65`: settled=59, wins=42, hit_rate=0.711864, ROI=-0.033534
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `ml-meta avg_p>=55`: settled=9, wins=3, hit_rate=0.333333, ROI=-0.474444

## By bucket

- `CAUTION`: settled=43, wins=24, hit_rate=0.55814, ROI=-0.136279
- `CERTIFIED_CLEAN`: settled=12, wins=5, hit_rate=0.416667, ROI=-0.399167
- `SKIPPED_VETO`: settled=108, wins=84, hit_rate=0.777778, ROI=0.046278
- `WATCHLIST_NO_ODDS`: settled=10, wins=9, hit_rate=0.9, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=2, wins=1, hit_rate=0.5, ROI=-0.4
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=9, wins=6, hit_rate=0.666667, ROI=-0.106667
- `WATCHLIST_UNKNOWN_CTX`: settled=22, wins=20, hit_rate=0.909091, ROI=0.099545

## By odds source

- `UNKNOWN`: settled=10, wins=9, hit_rate=0.9, ROI=None
- `betexplorer_odds`: settled=88, wins=69, hit_rate=0.784091, ROI=0.047159
- `bzzoiro_odds`: settled=59, wins=39, hit_rate=0.661017, ROI=-0.05122
- `forebet_best`: settled=6, wins=3, hit_rate=0.5, ROI=-0.313333
- `scoutingstats_odds`: settled=32, wins=18, hit_rate=0.5625, ROI=-0.258437
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=13, wins=9, hit_rate=0.692308, ROI=-0.133846
- `betexplorer`: settled=88, wins=69, hit_rate=0.784091, ROI=0.047159
- `exact`: settled=83, wins=52, hit_rate=0.626506, ROI=-0.11388
- `fallback`: settled=12, wins=10, hit_rate=0.833333, ROI=0.151667
- `none`: settled=10, wins=9, hit_rate=0.9, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 88 | 69 | 0.784091 | 88 | 0.047159 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 51 | 34 | 0.666667 | 51 | -0.023176 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 32 | 18 | 0.5625 | 32 | -0.258437 |
| Source fallback (`SOURCE_FALLBACK`) | 12 | 10 | 0.833333 | 12 | 0.151667 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 13 | 9 | 0.692308 | 13 | -0.133846 |
| No usable price (`UNMATCHED`) | 10 | 9 | 0.9 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 108 | 84 | 0.777778 | 108 | 0.046278 |
| **trusted evidence only** | 83 | 64 | 0.771084 | 83 | 0.042747 |
| **soft evidence only** | 25 | 20 | 0.8 | 25 | 0.058 |
| evidence: BETEXPLORER_RESCUE | 52 | 42 | 0.807692 | 52 | 0.067692 |
| evidence: BZZOIRO_PRIMARY | 31 | 22 | 0.709677 | 31 | 0.000903 |
| evidence: SCOUTINGSTATS_SOLE | 12 | 8 | 0.666667 | 12 | -0.139167 |
| evidence: SOURCE_FALLBACK | 6 | 6 | 1.0 | 6 | 0.418333 |
| evidence: SUSPECT_ALIAS_FUZZY | 7 | 6 | 0.857143 | 7 | 0.087143 |
| odds band: <1.50 | 88 | 70 | 0.795455 | 88 | 0.01975 |
| odds band: 1.50-2.00 | 19 | 13 | 0.684211 | 19 | 0.109474 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 4 | 0.8 | 5 | 0.136 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 7 | 5 | 0.714286 | 7 | -0.082857 |
| veto reason: context VETO in ['odds_band'] | 41 | 31 | 0.756098 | 41 | 0.026098 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 6 | 6 | 1.0 | 6 | 0.318833 |
| veto reason: context VETO in ['team_a'] | 15 | 12 | 0.8 | 15 | 0.167333 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 4 | 3 | 0.75 | 4 | 0.12 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.013333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 3 | 1 | 0.333333 | 3 | -0.64 |
| veto reason: context VETO in ['team_h'] | 14 | 11 | 0.785714 | 14 | 0.008214 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| contrast CAUTION: BETEXPLORER_RESCUE | 18 | 12 | 0.666667 | 18 | -0.019444 |
| contrast CAUTION: BZZOIRO_PRIMARY | 12 | 9 | 0.75 | 12 | 0.235833 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 8 | 1 | 0.125 | 8 | -0.7875 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 161 | 122 | 0.757764 | 151 | 0.031709 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 13 | 9 | 0.692308 | 13 | -0.133846 | 5 | 1.302 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 32 | 18 | 0.5625 | 32 | -0.258437 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-12: Tigre vs Montevideo City Torque (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.83 -> 🔴 LOST (Expected prob: 55.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 46.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (19.1%), [🔴 MISS] 2-1 (19.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.3% (Actual: 1 away goals)

### 2026-08-12: Charlestown City vs Edgeworth Eagles (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.57 -> 🟢 WON (Expected prob: 67.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 2 goals)
  - **Top Scores**: [🟢 HIT] 0-2 (19.4%), [🔴 MISS] 0-1 (15.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +83.4% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +90.4% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +40.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +22.8% (Actual: 2 goals)

### 2026-08-12: North Sunshine Eagles vs Heidelberg United (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.35 -> 🔴 LOST (Expected prob: 60.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.0% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 1-2 (17.6%), [🔴 MISS] 0-2 (16.6%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected +83.1% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +91.3% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +90.7% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +40.9% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +19.7% (Actual: 0 goals)

### 2026-08-12: Rapid Vienna vs Paide (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.08 -> 🟢 WON (Expected prob: 79.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 37.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 93.4% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (15.3%), [🔴 MISS] 3-0 (14.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +46.1% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +90.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +92.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +26.8% (Actual: 2 goals)

### 2026-08-12: Palmeiras vs Cerro Porteno (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🔴 LOST (Expected prob: 73.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 76.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (13.5%), [🔴 MISS] 2-0 (12.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.0% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +36.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +29.7% (Actual: 2 goals)

### 2026-08-12: Deportivo La Coruna vs Real Madrid (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.43 -> 🟢 WON (Expected prob: 72.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (15.2%), [🟢 HIT] 0-1 (14.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +81.8% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +92.5% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +90.4% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected +81.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +41.6% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.1% (Actual: 1 goals)

### 2026-08-12: Weston Bears vs Adamstown Rosebuds (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.0%), [🔴 MISS] 3-0 (12.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +47.3% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.3% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.4% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +26.6% (Actual: 6 goals)

### 2026-08-12: Arsenal vs Como (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.49 -> 🔴 LOST (Expected prob: 66.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.3%), [🔴 MISS] 1-0 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +91.0% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +81.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +41.3% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +21.9% (Actual: 2 goals)

### 2026-08-12: Paris Saint Germain vs Aston Villa (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.78 -> 🟢 WON (Expected prob: 57.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-0 (17.6%), [🟢 HIT] 2-1 (17.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +85.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +38.0% (Actual: 3 goals)

### 2026-08-12: AmaZulu vs Orlando Pirates (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🔴 LOST (Expected prob: 58.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 1-2 (17.3%), [🔴 MISS] 0-2 (16.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +81.4% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +91.7% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +91.3% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +38.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +18.3% (Actual: 2 goals)

### 2026-08-12: Bolivar vs Sao Paulo (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🔴 LOST (Expected prob: 60.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.3%), [🔴 MISS] 1-0 (17.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +82.6% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +18.3% (Actual: 2 goals)

### 2026-08-12: FC Copenhagen vs Debreceni VSC (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🟢 WON (Expected prob: 77.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.4% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.7% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.5% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 3-0 (12.8%), [🔴 MISS] 4-0 (12.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +48.8% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +89.3% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +93.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +89.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +27.7% (Actual: 6 goals)


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

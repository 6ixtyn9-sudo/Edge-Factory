# Edge Factory — Recent picks audit (2026-07-28 to 2026-08-26)

## Overall

- archived pick rows: 383
- archived pick dates: 30
- immutable morning-baseline rows: 252
- verified official late-slate additions: 13
- regular-ledger-only legacy rows: 118
- unsafe regular ledgers ignored: 11
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 358
- eligible prior 1x2 picks: 374
- pending/unmatched result picks: 7
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 7
- ambiguous result picks: 0
- wins: 255
- hit rate: +71.2%
- priced picks: 338
- ROI: -1.1%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-26
- same-day rows excluded: 9

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 230 / 358 matches (64.2%)
- **Both Teams to Score (BTTS)**: occurred in 182 / 358 matches (50.8%)
- **Selected Team Over 1.5 Goals**: occurred in 254 / 358 matches (70.9%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 358
- **Total Hits**: 275
- **Overall Hit Rate**: 76.8%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=134, hits=121, hit_rate=90.3%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=9, hits=9, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=147, hits=100, hit_rate=68.0%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2118** | scored: 2118

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 289 | 289 | 185 | 64.0% | 45.8% | +18.2% | 0.266575 |
| `away_under_35` | 275 | 275 | 268 | 97.5% | 97.9% | -0.5% | 0.023749 |
| `away_under_25` | 258 | 258 | 243 | 94.2% | 93.7% | +0.4% | 0.055546 |
| `home_over_05` | 255 | 255 | 234 | 91.8% | 87.0% | +4.8% | 0.077896 |
| `match_over_45` | 242 | 242 | 66 | 27.3% | 24.8% | +2.5% | 0.200871 |
| `match_over_35` | 98 | 98 | 38 | 38.8% | 43.0% | -4.2% | 0.244783 |
| `away_under_15` | 95 | 95 | 79 | 83.2% | 81.5% | +1.7% | 0.139511 |
| `home_under_35` | 78 | 78 | 74 | 94.9% | 94.4% | +0.5% | 0.04818 |
| `exact_4` | 67 | 67 | 17 | 25.4% | 18.0% | +7.3% | 0.196872 |
| `home_under_25` | 64 | 64 | 60 | 93.8% | 91.3% | +2.4% | 0.060354 |
| `goal_range_4_6` | 63 | 63 | 26 | 41.3% | 37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | 33.9% | 30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | 10.5% | 12.6% | -2.1% | 0.096166 |
| `btts_no` | 40 | 40 | 17 | 42.5% | 52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | 50.0% | 50.9% | -0.9% | 0.248905 |
| `exact_3` | 32 | 32 | 4 | 12.5% | 22.2% | -9.7% | 0.119085 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `exact_2` | 24 | 24 | 5 | 20.8% | 24.5% | -3.7% | 0.166543 |
| `away_over_05` | 22 | 22 | 19 | 86.4% | 86.0% | +0.3% | 0.117067 |
| `home_under_15` | 10 | 10 | 9 | 90.0% | 81.1% | +8.9% | 0.097339 |
| `goal_range_6_plus` | 9 | 9 | 1 | 11.1% | 18.7% | -7.6% | 0.102748 |
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
| hybrid_cohort | 1780 | 1218 | 68.4% | 65.4% | +3.0% | 0.129777 |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| model | 75 | 54 | 72.0% | 53.5% | +18.5% | 0.276534 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 174 | 16.2% | 19.5% | +3.3% |
| 0.2-0.3 | 261 | 24.9% | 26.8% | +1.9% |
| 0.3-0.4 | 227 | 35.5% | 44.5% | +9.0% |
| 0.4-0.5 | 241 | 45.3% | 51.9% | +6.6% |
| 0.5-0.6 | 136 | 53.0% | 55.1% | +2.2% |
| 0.6-0.7 | 10 | 64.2% | 80.0% | +15.8% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 358 | 84.5% | 88.5% | +4.1% |
| 0.9-1.0 | 707 | 95.3% | 95.6% | +0.3% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=356, MAE=1.488567 goals, bias=-0.258174 (realized − promised), promised avg 3.60368 vs realized 3.345506

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 356 | 26.0% | 33.1% | +7.1% | 0.185582 |
| BTTS-Yes | 356 | 41.2% | 51.1% | +9.9% | 0.259961 |
| Home Over 1.5 | 356 | 69.3% | 59.8% | -9.5% | 0.230471 |
| Over 2.5 | 356 | 70.9% | 64.0% | -6.8% | 0.231146 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 241 | 8.8% | 20.7% | +11.9% |
| 0.1-0.2 | 117 | 10.5% | 26.5% | +16.0% |
| 0.2-0.3 | 3 | 20.5% | 0.0% | -20.5% |
| 0.3-0.4 | 95 | 37.6% | 52.6% | +15.1% |
| 0.4-0.5 | 256 | 43.0% | 50.8% | +7.8% |
| 0.6-0.7 | 191 | 66.8% | 58.1% | -8.7% |
| 0.7-0.8 | 150 | 74.8% | 69.3% | -5.4% |
| 0.8-0.9 | 316 | 84.9% | 69.6% | -15.3% |
| 0.9-1.0 | 55 | 91.9% | 81.8% | -10.0% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=108, wins=89, hit_rate=0.824074, ROI=0.080636
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=38, wins=29, hit_rate=0.763158, ROI=0.039868
- `ml-meta avg_p>=55`: settled=139, wins=85, hit_rate=0.611511, ROI=-0.086591
- `ml-meta avg_p>=60`: settled=19, wins=16, hit_rate=0.842105, ROI=0.201579
- `ml-meta avg_p>=65`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.25
- `ml-meta avg_p>=70`: settled=7, wins=6, hit_rate=0.857143, ROI=0.122857
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06

## By bucket

- `CAUTION`: settled=62, wins=37, hit_rate=0.596774, ROI=-0.052742
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=188, wins=138, hit_rate=0.734043, ROI=0.009032
- `WATCHLIST_NO_ODDS`: settled=19, wins=17, hit_rate=0.894737, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=3, hit_rate=0.6, ROI=-0.0825
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=42, wins=32, hit_rate=0.761905, ROI=0.095
- `WATCHLIST_UNKNOWN_CTX`: settled=21, wins=19, hit_rate=0.904762, ROI=0.106667

## By odds source

- `UNKNOWN`: settled=20, wins=17, hit_rate=0.85, ROI=None
- `betexplorer_odds`: settled=126, wins=92, hit_rate=0.730159, ROI=0.015397
- `bzzoiro_odds`: settled=86, wins=57, hit_rate=0.662791, ROI=-0.042116
- `forebet_best`: settled=18, wins=11, hit_rate=0.611111, ROI=-0.176111
- `scoutingstats_odds`: settled=97, wins=67, hit_rate=0.690722, ROI=-0.025876
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=18, wins=12, hit_rate=0.666667, ROI=-0.112353
- `betexplorer`: settled=126, wins=92, hit_rate=0.730159, ROI=0.015397
- `exact`: settled=175, wins=119, hit_rate=0.68, ROI=-0.024526
- `fallback`: settled=20, wins=15, hit_rate=0.75, ROI=0.035
- `none`: settled=19, wins=17, hit_rate=0.894737, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 126 | 92 | 0.730159 | 126 | 0.015397 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 78 | 52 | 0.666667 | 78 | -0.022846 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 97 | 67 | 0.690722 | 97 | -0.025876 |
| Source fallback (`SOURCE_FALLBACK`) | 20 | 15 | 0.75 | 20 | 0.035 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 18 | 12 | 0.666667 | 17 | -0.112353 |
| No usable price (`UNMATCHED`) | 19 | 17 | 0.894737 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 188 | 138 | 0.734043 | 188 | 0.009032 |
| **trusted evidence only** | 115 | 89 | 0.773913 | 115 | 0.062678 |
| **soft evidence only** | 73 | 49 | 0.671233 | 73 | -0.075479 |
| evidence: BETEXPLORER_RESCUE | 67 | 54 | 0.80597 | 67 | 0.071045 |
| evidence: BZZOIRO_PRIMARY | 48 | 35 | 0.729167 | 48 | 0.051 |
| evidence: SCOUTINGSTATS_SOLE | 53 | 34 | 0.641509 | 53 | -0.107925 |
| evidence: SOURCE_FALLBACK | 11 | 8 | 0.727273 | 11 | 0.021818 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 9 | -0.003333 |
| odds band: <1.50 | 132 | 106 | 0.80303 | 132 | 0.032333 |
| odds band: 1.50-2.00 | 53 | 30 | 0.566038 | 53 | -0.068302 |
| odds band: 2.00-3.00 | 3 | 2 | 0.666667 | 3 | 0.35 |
| veto reason: context VETO in ['league', 'odds_band'] | 4 | 3 | 0.75 | 4 | -0.1275 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.495 |
| veto reason: context VETO in ['league', 'team_a'] | 6 | 3 | 0.5 | 6 | -0.431667 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.48 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 9 | 5 | 0.555556 | 9 | -0.246667 |
| veto reason: context VETO in ['niche'] | 2 | 1 | 0.5 | 2 | -0.14 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: context VETO in ['odds_band'] | 43 | 37 | 0.860465 | 43 | 0.165814 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.183909 |
| veto reason: context VETO in ['team_a'] | 29 | 22 | 0.758621 | 29 | 0.133448 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.222222 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 4 | 2 | 0.5 | 4 | -0.26 |
| veto reason: context VETO in ['team_h', 'team_a'] | 13 | 6 | 0.461538 | 13 | -0.36 |
| veto reason: context VETO in ['team_h'] | 43 | 29 | 0.674419 | 43 | -0.051744 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 35 | 21 | 0.6 | 35 | -0.024 |
| contrast CAUTION: BZZOIRO_PRIMARY | 19 | 12 | 0.631579 | 19 | -0.016842 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 5 | 4 | 0.8 | 5 | 0.178 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 243 | 176 | 0.72428 | 224 | 0.00383 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 18 | 12 | 0.666667 | 17 | -0.112353 | 10 | 1.3545 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 97 | 67 | 0.690722 | 97 | -0.025876 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-25: Alloa Athletic vs Motherwell Youth (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.13 -> 🟢 WON (Expected prob: 77.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.7% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.5% (Actual: 3 goals)

### 2026-08-25: Afturelding vs Grotta (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 60.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.4% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 2 goals)

### 2026-08-25: Watford vs Peterborough (Actual Score: **1-5**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🔴 LOST (Expected prob: 57.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.3% (Actual: 1 home goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 5 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 5 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.1% (Actual: 6 goals)

### 2026-08-25: Ross County vs Banks O' Dee (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 57.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.4% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.2% (Actual: 4 goals)

### 2026-08-25: Al-Ettifaq vs Al-Nassr (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.25 -> 🟢 WON (Expected prob: 72.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.8% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 94.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.2% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.6% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.0% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.4% (Actual: 5 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 9 |
- 2026-08-08 `POSTPONED` `SKIPPED_VETO` — Belshina vs Dinamo Minsk (verified_disposition); excluded from win/loss/ROI
- 2026-08-11 `POSTPONED` `WATCHLIST_UNCORROBORATED_PRICE` — Junior vs Pereira (verified_disposition); excluded from win/loss/ROI
- 2026-08-15 `POSTPONED` `SKIPPED_VETO` — Slavia Sofia vs Levski Sofia (verified_disposition); excluded from win/loss/ROI
- 2026-08-16 `POSTPONED` `SKIPPED_VETO` — SC Braga vs Gil Vicente (verified_disposition); excluded from win/loss/ROI
- 2026-08-17 `POSTPONED` `SKIPPED_VETO` — Bucaramanga vs Deportivo Pasto (verified_disposition); excluded from win/loss/ROI
- 2026-08-21 `POSTPONED` `SKIPPED_VETO` — Shamrock Rovers vs Shelbourne FC (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — Rangers vs St Mirren (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — St Johnstone vs Celtic (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — Hibernian vs Kilmarnock (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- 2026-08-15 `WATCHLIST_NO_ODDS` `2way-unanimous min_p>=60 avg_p>=65` — Kara-Balta vs Bars -> AWAY @ None (pending_or_unmatched_result); keys=['karabalta', 'kyrgyzalt', 'kyrgyzaltyn']/['bars']
- 2026-08-15 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous min_p>=60 avg_p>=65` — Olympic Kingsway vs Sorrento FC -> HOME @ 1.24 (pending_or_unmatched_result); keys=['olympicki']/['sorrento', 'sorrentoc']
- 2026-08-17 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hamrun Spartans vs Mosta -> HOME @ 1.18 (pending_or_unmatched_result); keys=['hamrunspa']/['mosta']
- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (pending_or_unmatched_result); keys=['charlesto']/['miami', 'miamiii']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']

## Ambiguous result examples

- none

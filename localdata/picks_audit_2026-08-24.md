# Edge Factory — Recent picks audit (2026-07-26 to 2026-08-24)

## Overall

- archived pick rows: 385
- archived pick dates: 30
- immutable morning-baseline rows: 249
- verified official late-slate additions: 18
- regular-ledger-only legacy rows: 118
- unsafe regular ledgers ignored: 8
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 359
- eligible prior 1x2 picks: 376
- pending/unmatched result picks: 7
- voided postponed/cancelled/abandoned events: 10
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 9
- ambiguous result picks: 0
- wins: 257
- hit rate: +71.6%
- priced picks: 339
- ROI: +0.1%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-24
- same-day rows excluded: 9

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 230 / 359 matches (64.1%)
- **Both Teams to Score (BTTS)**: occurred in 184 / 359 matches (51.3%)
- **Selected Team Over 1.5 Goals**: occurred in 253 / 359 matches (70.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 344
- **Total Hits**: 263
- **Overall Hit Rate**: 76.5%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=128, hits=117, hit_rate=91.4%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=9, hits=9, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=139, hits=92, hit_rate=66.2%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2056** | scored: 2056

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 275 | 275 | 175 | 63.6% | 45.8% | +17.9% | 0.267751 |
| `away_under_35` | 266 | 266 | 260 | 97.7% | 97.9% | -0.2% | 0.020915 |
| `away_under_25` | 249 | 249 | 235 | 94.4% | 93.7% | +0.6% | 0.053916 |
| `home_over_05` | 246 | 246 | 227 | 92.3% | 87.1% | +5.2% | 0.074301 |
| `match_over_45` | 233 | 233 | 63 | 27.0% | 24.8% | +2.3% | 0.199779 |
| `match_over_35` | 98 | 98 | 38 | 38.8% | 43.0% | -4.2% | 0.244783 |
| `away_under_15` | 94 | 94 | 78 | 83.0% | 81.5% | +1.5% | 0.140674 |
| `home_under_35` | 73 | 73 | 69 | 94.5% | 94.3% | +0.2% | 0.051376 |
| `exact_4` | 67 | 67 | 17 | 25.4% | 18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | 41.3% | 37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | 33.9% | 30.9% | +3.0% | 0.229007 |
| `home_under_25` | 59 | 59 | 55 | 93.2% | 91.2% | +2.0% | 0.065074 |
| `exact_5` | 57 | 57 | 6 | 10.5% | 12.6% | -2.1% | 0.096166 |
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
| hybrid_cohort | 1718 | 1170 | 68.1% | 65.1% | +3.0% | 0.129206 |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| model | 75 | 54 | 72.0% | 53.5% | +18.5% | 0.276534 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 173 | 16.2% | 19.7% | +3.4% |
| 0.2-0.3 | 253 | 24.9% | 26.5% | +1.6% |
| 0.3-0.4 | 227 | 35.5% | 44.5% | +9.0% |
| 0.4-0.5 | 232 | 45.3% | 51.7% | +6.5% |
| 0.5-0.6 | 131 | 53.0% | 53.4% | +0.4% |
| 0.6-0.7 | 10 | 64.2% | 80.0% | +15.8% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 347 | 84.5% | 88.8% | +4.3% |
| 0.9-1.0 | 679 | 95.3% | 95.7% | +0.4% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=342, MAE=1.481988 goals, bias=-0.272924 (realized − promised), promised avg 3.606257 vs realized 3.333333

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 342 | 25.6% | 32.7% | +7.2% | 0.190306 |
| BTTS-Yes | 342 | 41.2% | 51.5% | +10.2% | 0.259556 |
| Home Over 1.5 | 342 | 69.9% | 59.6% | -10.2% | 0.225833 |
| Over 2.5 | 342 | 70.9% | 63.7% | -7.2% | 0.233201 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 232 | 8.9% | 19.8% | +11.0% |
| 0.1-0.2 | 112 | 10.5% | 27.7% | +17.2% |
| 0.2-0.3 | 3 | 20.5% | 0.0% | -20.5% |
| 0.3-0.4 | 90 | 37.7% | 51.1% | +13.4% |
| 0.4-0.5 | 247 | 43.0% | 51.8% | +8.8% |
| 0.6-0.7 | 184 | 66.8% | 58.7% | -8.2% |
| 0.7-0.8 | 143 | 74.8% | 67.8% | -6.9% |
| 0.8-0.9 | 303 | 84.9% | 69.3% | -15.6% |
| 0.9-1.0 | 54 | 91.9% | 81.5% | -10.4% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=112, wins=91, hit_rate=0.8125, ROI=0.082186
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=42, wins=32, hit_rate=0.761905, ROI=0.053452
- `ml-meta avg_p>=55`: settled=132, wins=82, hit_rate=0.621212, ROI=-0.067619
- `ml-meta avg_p>=60`: settled=19, wins=16, hit_rate=0.842105, ROI=0.201579
- `ml-meta avg_p>=65`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.25
- `ml-meta avg_p>=70`: settled=7, wins=6, hit_rate=0.857143, ROI=0.122857
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06

## By bucket

- `CAUTION`: settled=70, wins=43, hit_rate=0.614286, ROI=-0.025857
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=184, wins=137, hit_rate=0.744565, ROI=0.02037
- `WATCHLIST_NO_ODDS`: settled=19, wins=16, hit_rate=0.842105, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=3, hit_rate=0.6, ROI=-0.0825
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=40, wins=31, hit_rate=0.775, ROI=0.1185
- `WATCHLIST_UNKNOWN_CTX`: settled=20, wins=18, hit_rate=0.9, ROI=0.101

## By odds source

- `UNKNOWN`: settled=20, wins=16, hit_rate=0.8, ROI=None
- `betexplorer_odds`: settled=124, wins=92, hit_rate=0.741935, ROI=0.033871
- `bzzoiro_odds`: settled=88, wins=59, hit_rate=0.670455, ROI=-0.028545
- `forebet_best`: settled=19, wins=12, hit_rate=0.631579, ROI=-0.155263
- `scoutingstats_odds`: settled=97, wins=67, hit_rate=0.690722, ROI=-0.021237
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=18, wins=12, hit_rate=0.666667, ROI=-0.112353
- `betexplorer`: settled=124, wins=92, hit_rate=0.741935, ROI=0.033871
- `exact`: settled=177, wins=121, hit_rate=0.683616, ROI=-0.015435
- `fallback`: settled=21, wins=16, hit_rate=0.761905, ROI=0.04381
- `none`: settled=19, wins=16, hit_rate=0.842105, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 124 | 92 | 0.741935 | 124 | 0.033871 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 80 | 54 | 0.675 | 80 | -0.0084 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 97 | 67 | 0.690722 | 97 | -0.021237 |
| Source fallback (`SOURCE_FALLBACK`) | 21 | 16 | 0.761905 | 21 | 0.04381 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 18 | 12 | 0.666667 | 17 | -0.112353 |
| No usable price (`UNMATCHED`) | 19 | 16 | 0.842105 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 184 | 137 | 0.744565 | 184 | 0.02037 |
| **trusted evidence only** | 111 | 87 | 0.783784 | 111 | 0.072414 |
| **soft evidence only** | 73 | 50 | 0.684932 | 73 | -0.058767 |
| evidence: BETEXPLORER_RESCUE | 64 | 53 | 0.828125 | 64 | 0.099687 |
| evidence: BZZOIRO_PRIMARY | 47 | 34 | 0.723404 | 47 | 0.035277 |
| evidence: SCOUTINGSTATS_SOLE | 52 | 34 | 0.653846 | 52 | -0.090769 |
| evidence: SOURCE_FALLBACK | 12 | 9 | 0.75 | 12 | 0.038333 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 9 | -0.003333 |
| odds band: <1.50 | 132 | 107 | 0.810606 | 132 | 0.042864 |
| odds band: 1.50-2.00 | 49 | 28 | 0.571429 | 49 | -0.060408 |
| odds band: 2.00-3.00 | 3 | 2 | 0.666667 | 3 | 0.35 |
| veto reason: context VETO in ['league', 'odds_band'] | 4 | 3 | 0.75 | 4 | -0.1275 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.495 |
| veto reason: context VETO in ['league', 'team_a'] | 7 | 4 | 0.571429 | 7 | -0.322857 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.48 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 7 | 5 | 0.714286 | 7 | -0.031429 |
| veto reason: context VETO in ['niche'] | 2 | 1 | 0.5 | 2 | -0.14 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: context VETO in ['odds_band'] | 45 | 38 | 0.844444 | 45 | 0.137333 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 10 | 9 | 0.9 | 10 | 0.2013 |
| veto reason: context VETO in ['team_a'] | 28 | 21 | 0.75 | 28 | 0.118571 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.2125 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 4 | 2 | 0.5 | 4 | -0.26 |
| veto reason: context VETO in ['team_h', 'team_a'] | 11 | 5 | 0.454545 | 11 | -0.406364 |
| veto reason: context VETO in ['team_h'] | 41 | 28 | 0.682927 | 41 | -0.033049 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 37 | 23 | 0.621622 | 37 | 0.000541 |
| contrast CAUTION: BZZOIRO_PRIMARY | 22 | 15 | 0.681818 | 22 | 0.071818 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 4 | 1 | 0.25 | 4 | -0.575 |
| contrast CAUTION: SOURCE_FALLBACK | 5 | 4 | 0.8 | 5 | 0.178 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 244 | 178 | 0.729508 | 225 | 0.019769 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 18 | 12 | 0.666667 | 17 | -0.112353 | 10 | 1.3545 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 97 | 67 | 0.690722 | 97 | -0.021237 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-23: Palmeiras vs Vasco da Gama (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.62 -> 🟢 WON (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.6% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.2% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.5% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.2% (Actual: 5 goals)

### 2026-08-23: Washington Spirit (w) vs Orlando Pride (w) (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🔴 LOST (Expected prob: 63.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 85.4% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.9% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.4% (Actual: 1 goals)

### 2026-08-23: IFK Trelleborg vs Lilla Torg (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.43 -> 🟢 WON (Expected prob: 57.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.0% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.3% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.3% (Actual: 0 away goals)

### 2026-08-23: Bahlinger SC vs Magdeburg (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.06 -> 🟢 WON (Expected prob: 81.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.7% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.6% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.6% (Actual: 4 goals)

### 2026-08-23: TSV Schott Mainz vs Borussia M'gladbach (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.01 -> 🟢 WON (Expected prob: 79.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.0% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 20.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 80.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 80.0% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.5% (Actual: 5 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 80.1% (Actual: 0 home goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 92.1% (Actual: 5 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.3% (Actual: 5 goals)

### 2026-08-23: SSV Jeddeloh vs Heidenheim (Actual Score: **5-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.11 -> 🔴 LOST (Expected prob: 75.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.0% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 17.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 96.4% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 89.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.3% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 90.8% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.7% (Actual: 7 goals)

### 2026-08-23: Universitatea Craiova vs FC Voluntari (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 76.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.2% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.4% (Actual: 4 goals)

### 2026-08-23: Phönix Lübeck vs Paderborn (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.17 -> 🟢 WON (Expected prob: 74.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 95.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 87.3% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.0% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.3% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 26.7% (Actual: 6 goals)

### 2026-08-23: HB Torshavn vs 07 Vestur (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🔴 LOST (Expected prob: 72.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.0% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 51.2% (Actual: 0 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 89.8% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.6% (Actual: 0 goals)

### 2026-08-23: PAOK vs Levadiakos (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 71.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.9% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.2% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.8% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.0% (Actual: 4 goals)

### 2026-08-23: Manchester City vs Bournemouth (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 67.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.8% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.8% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.1% (Actual: 3 goals)

### 2026-08-23: BSC Young Boys vs FC Vaduz (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.9% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.7% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.8% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.9% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.8% (Actual: 6 goals)

### 2026-08-23: KA Akureyri vs KR Reykjavik (Actual Score: **3-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.48 -> 🟢 WON (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.6% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.7% (Actual: 8 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.3% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 92.8% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.7% (Actual: 8 goals)

### 2026-08-23: Porto vs FC Arouca (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.0% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.2% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.7% (Actual: 2 goals)

### 2026-08-23: Go Ahead Eagles vs ADO Den Haag (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🟢 WON (Expected prob: 61.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.1% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.6% (Actual: 4 goals)

### 2026-08-23: Frosinone vs Juventus (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.45 -> 🟢 WON (Expected prob: 61.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.2% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.9% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.7% (Actual: 1 goals)

### 2026-08-23: Elche vs Barcelona (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.3 -> 🟢 WON (Expected prob: 55.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.5% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.5% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.7% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.2% (Actual: 5 goals)

### 2026-08-23: Los Angeles FC vs Portland Timbers (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🔴 LOST (Expected prob: 55.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.2% (Actual: 2 goals)

### 2026-08-23: Zrinjski vs Zeljeznicar Sarajevo (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.6% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 83.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.1% (Actual: 2 goals)

### 2026-08-23: Cambuur vs Feyenoord (Actual Score: **2-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.28 -> 🟢 WON (Expected prob: 72.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 30.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 87.8% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.2% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.1% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 85.4% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.6% (Actual: 7 goals)

### 2026-08-23: Midtjylland vs Randers FC (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 65.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.6% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.0% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.1% (Actual: 1 goals)

### 2026-08-23: Gyori ETO FC vs Zalaegerszegi TE (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 65.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.7% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.8% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.7% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.6% (Actual: 3 goals)

### 2026-08-23: Crvena Zvezda vs Cukaricki Belgrade (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 60.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.3% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.9% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.0% (Actual: 4 goals)

### 2026-08-23: Atalanta vs Sassuolo (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 55.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.6% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.2% (Actual: 3 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 10 |
- 2026-07-26 `POSTPONED` `SKIPPED_VETO` — Super Nova vs Riga (verified_disposition); excluded from win/loss/ROI
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

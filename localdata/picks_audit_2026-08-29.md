# Edge Factory — Recent picks audit (2026-07-31 to 2026-08-29)

## Overall

- archived pick rows: 440
- archived pick dates: 30
- immutable morning-baseline rows: 312
- verified official late-slate additions: 13
- regular-ledger-only legacy rows: 115
- unsafe regular ledgers ignored: 12
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 387
- eligible prior 1x2 picks: 402
- pending/unmatched result picks: 5
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 1
- wins: 274
- hit rate: +70.8%
- priced picks: 366
- ROI: -1.5%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-29
- same-day rows excluded: 38

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 251 / 387 matches (64.9%)
- **Both Teams to Score (BTTS)**: occurred in 206 / 387 matches (53.2%)
- **Selected Team Over 1.5 Goals**: occurred in 277 / 387 matches (71.6%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 387
- **Total Hits**: 296
- **Overall Hit Rate**: 76.5%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=138, hits=125, hit_rate=90.6%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=10, hits=10, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=178, hits=123, hit_rate=69.1%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2271** | scored: 2271

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 327 | 327 | 214 | 65.4% | 46.1% | +19.3% | 0.265932 |
| `away_under_35` | 300 | 300 | 293 | 97.7% | 98.0% | -0.3% | 0.021792 |
| `away_under_25` | 283 | 283 | 266 | 94.0% | 94.0% | +0.0% | 0.056974 |
| `home_over_05` | 282 | 282 | 258 | 91.5% | 86.8% | +4.7% | 0.079791 |
| `match_over_45` | 274 | 274 | 79 | 28.8% | 24.7% | +4.1% | 0.207911 |
| `away_under_15` | 109 | 109 | 90 | 82.6% | 81.4% | +1.1% | 0.14379 |
| `match_over_35` | 95 | 95 | 35 | 36.8% | 43.3% | -6.5% | 0.238157 |
| `home_under_35` | 85 | 85 | 83 | 97.6% | 94.7% | +3.0% | 0.023952 |
| `home_under_25` | 72 | 72 | 66 | 91.7% | 91.6% | +0.1% | 0.076765 |
| `exact_4` | 63 | 63 | 15 | 23.8% | 18.2% | +5.6% | 0.185768 |
| `goal_range_4_6` | 61 | 61 | 24 | 39.3% | 37.6% | +1.7% | 0.242669 |
| `goal_range_4_5` | 58 | 58 | 19 | 32.8% | 30.9% | +1.8% | 0.223946 |
| `exact_5` | 56 | 56 | 5 | 8.9% | 12.6% | -3.7% | 0.083591 |
| `btts_no` | 40 | 40 | 17 | 42.5% | 52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | 50.0% | 50.9% | -0.9% | 0.248905 |
| `exact_3` | 28 | 28 | 4 | 14.3% | 22.2% | -7.9% | 0.129032 |
| `away_over_05` | 22 | 22 | 19 | 86.4% | 86.0% | +0.3% | 0.117067 |
| `goal_range_2_3` | 21 | 21 | 8 | 38.1% | 46.2% | -8.1% | 0.239118 |
| `exact_2` | 20 | 20 | 5 | 25.0% | 24.5% | +0.5% | 0.188054 |
| `home_under_15` | 12 | 12 | 11 | 91.7% | 81.2% | +10.5% | 0.08671 |
| `goal_range_6_plus` | 9 | 9 | 1 | 11.1% | 18.7% | -7.6% | 0.102748 |
| `match_over_15` | 7 | 7 | 6 | 85.7% | 86.2% | -0.5% | 0.135507 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | 33.3% | 13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1967 | 1368 | 69.5% | 66.0% | +3.6% | 0.131322 |
| legacy | 225 | 115 | 51.1% | 52.6% | -1.4% | 0.174187 |
| model | 79 | 57 | 72.2% | 53.9% | +18.2% | 0.266623 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 175 | 16.4% | 18.9% | +2.5% |
| 0.2-0.3 | 275 | 24.9% | 28.4% | +3.4% |
| 0.3-0.4 | 225 | 35.5% | 43.6% | +8.0% |
| 0.4-0.5 | 261 | 45.4% | 55.6% | +10.2% |
| 0.5-0.6 | 149 | 52.9% | 56.4% | +3.4% |
| 0.6-0.7 | 10 | 64.2% | 80.0% | +15.8% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 396 | 84.3% | 87.9% | +3.5% |
| 0.9-1.0 | 776 | 95.4% | 95.9% | +0.4% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=386, MAE=1.503497 goals, bias=-0.195725 (realized − promised), promised avg 3.592098 vs realized 3.396373

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 386 | 26.5% | 34.5% | +7.9% | 0.188583 |
| BTTS-Yes | 386 | 41.2% | 53.4% | +12.2% | 0.264774 |
| Home Over 1.5 | 386 | 68.7% | 60.4% | -8.4% | 0.231653 |
| Over 2.5 | 386 | 70.7% | 64.8% | -5.9% | 0.229669 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 258 | 8.8% | 20.9% | +12.1% |
| 0.1-0.2 | 130 | 10.5% | 29.2% | +18.8% |
| 0.2-0.3 | 4 | 21.2% | 25.0% | +3.8% |
| 0.3-0.4 | 102 | 37.6% | 55.9% | +18.2% |
| 0.4-0.5 | 278 | 43.0% | 52.5% | +9.5% |
| 0.6-0.7 | 214 | 66.8% | 61.2% | -5.6% |
| 0.7-0.8 | 157 | 74.8% | 67.5% | -7.2% |
| 0.8-0.9 | 344 | 84.9% | 70.9% | -13.9% |
| 0.9-1.0 | 57 | 91.7% | 78.9% | -12.8% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=110, wins=90, hit_rate=0.818182, ROI=0.080891
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=33, wins=25, hit_rate=0.757576, ROI=0.047879
- `ml-meta avg_p>=55`: settled=163, wins=101, hit_rate=0.619632, ROI=-0.086026
- `ml-meta avg_p>=60`: settled=22, wins=18, hit_rate=0.818182, ROI=0.156818
- `ml-meta avg_p>=65`: settled=5, wins=4, hit_rate=0.8, ROI=0.035
- `ml-meta avg_p>=70`: settled=8, wins=7, hit_rate=0.875, ROI=0.1875
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06

## By bucket

- `CAUTION`: settled=68, wins=43, hit_rate=0.632353, ROI=-0.006912
- `CERTIFIED_CLEAN`: settled=23, wins=10, hit_rate=0.434783, ROI=-0.370435
- `SKIPPED_VETO`: settled=203, wins=148, hit_rate=0.729064, ROI=0.004631
- `WATCHLIST_NO_ODDS`: settled=20, wins=18, hit_rate=0.9, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=3, hit_rate=0.6, ROI=-0.0825
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=48, wins=35, hit_rate=0.729167, ROI=0.045625
- `WATCHLIST_UNKNOWN_CTX`: settled=20, wins=17, hit_rate=0.85, ROI=0.0395

## By odds source

- `UNKNOWN`: settled=21, wins=18, hit_rate=0.857143, ROI=None
- `betexplorer_odds`: settled=138, wins=100, hit_rate=0.724638, ROI=0.00529
- `bzzoiro_odds`: settled=80, wins=51, hit_rate=0.6375, ROI=-0.0575
- `forebet_best`: settled=21, wins=14, hit_rate=0.666667, ROI=-0.069048
- `scoutingstats_odds`: settled=116, wins=80, hit_rate=0.689655, ROI=-0.033448
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=16, wins=10, hit_rate=0.625, ROI=-0.129333
- `betexplorer`: settled=138, wins=100, hit_rate=0.724638, ROI=0.00529
- `exact`: settled=191, wins=129, hit_rate=0.675393, ROI=-0.031728
- `fallback`: settled=22, wins=17, hit_rate=0.772727, ROI=0.085
- `none`: settled=20, wins=18, hit_rate=0.9, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 138 | 100 | 0.724638 | 138 | 0.00529 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 75 | 49 | 0.653333 | 75 | -0.029067 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 116 | 80 | 0.689655 | 116 | -0.033448 |
| Source fallback (`SOURCE_FALLBACK`) | 22 | 17 | 0.772727 | 22 | 0.085 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 16 | 10 | 0.625 | 15 | -0.129333 |
| No usable price (`UNMATCHED`) | 20 | 18 | 0.9 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 203 | 148 | 0.729064 | 203 | 0.004631 |
| **trusted evidence only** | 117 | 89 | 0.760684 | 117 | 0.047863 |
| **soft evidence only** | 86 | 59 | 0.686047 | 86 | -0.054186 |
| evidence: BETEXPLORER_RESCUE | 73 | 58 | 0.794521 | 73 | 0.053699 |
| evidence: BZZOIRO_PRIMARY | 44 | 31 | 0.704545 | 44 | 0.038182 |
| evidence: SCOUTINGSTATS_SOLE | 66 | 44 | 0.666667 | 66 | -0.080152 |
| evidence: SOURCE_FALLBACK | 11 | 8 | 0.727273 | 11 | 0.021818 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 9 | 0.043333 |
| odds band: <1.50 | 142 | 114 | 0.802817 | 142 | 0.037324 |
| odds band: 1.50-2.00 | 57 | 32 | 0.561404 | 57 | -0.077368 |
| odds band: 2.00-3.00 | 4 | 2 | 0.5 | 4 | 0.0125 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.05 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.495 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.66 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.48 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 7 | 4 | 0.571429 | 7 | -0.192857 |
| veto reason: context VETO in ['niche'] | 2 | 1 | 0.5 | 2 | -0.14 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: context VETO in ['odds_band'] | 50 | 42 | 0.84 | 50 | 0.1318 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.196364 |
| veto reason: context VETO in ['team_a'] | 31 | 23 | 0.741935 | 31 | 0.117742 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 12 | 10 | 0.833333 | 12 | 0.141667 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 4 | 2 | 0.5 | 4 | -0.26 |
| veto reason: context VETO in ['team_h', 'team_a'] | 14 | 7 | 0.5 | 14 | -0.321429 |
| veto reason: context VETO in ['team_h'] | 46 | 30 | 0.652174 | 46 | -0.079565 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 38 | 24 | 0.631579 | 38 | 0.011053 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0025 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 7 | 6 | 0.857143 | 7 | 0.294286 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 255 | 184 | 0.721569 | 235 | 0.001787 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 16 | 10 | 0.625 | 15 | -0.129333 | 11 | 1.372273 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 116 | 80 | 0.689655 | 116 | -0.033448 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-28: Fylkir FC vs Grotta (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🟢 WON (Expected prob: 61.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.4% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.3% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.3% (Actual: 4 goals)

### 2026-08-28: Torns IF vs IFK Trelleborg (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.64 -> 🟢 WON (Expected prob: 73.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 23.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.1% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.0% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 90.5% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.6% (Actual: 3 goals)

### 2026-08-28: Cork City vs Wexford Youths (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.37 -> 🟢 WON (Expected prob: 63.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.3% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.6% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.8% (Actual: 2 goals)

### 2026-08-28: Akron Togliatti vs CSKA Moscow (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.67 -> 🔴 LOST (Expected prob: 62.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.9% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 95.9% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.4% (Actual: 4 goals)

### 2026-08-28: CSKA 1948 vs Lokomotiv Plovdiv (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 74.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 53.0% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.3% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.2% (Actual: 2 goals)

### 2026-08-28: Al Khaleej Club vs Al Hilal (Actual Score: **1-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.2 -> 🟢 WON (Expected prob: 72.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 32.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.6% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.3% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.6% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 80.6% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.7% (Actual: 6 goals)

### 2026-08-28: Milan vs Venezia (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 70.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 53.3% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.2% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.0% (Actual: 2 goals)

### 2026-08-28: The New Saints vs Colwyn Bay (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 66.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.2% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.1% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.1% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.9% (Actual: 6 goals)

### 2026-08-28: Crystal Palace vs Manchester City (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.66 -> 🟢 WON (Expected prob: 64.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.4% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.7% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.8% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.9% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 94.5% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.5% (Actual: 5 goals)

### 2026-08-28: Bohemians FC vs Sligo Rovers (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 63.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.2% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.5% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.8% (Actual: 3 goals)

### 2026-08-28: CD Comerciantes vs FC Cajamarca (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🔴 LOST (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.8% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.2% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.1% (Actual: 5 goals)

### 2026-08-28: Aldershot Town vs Harrogate Town (Actual Score: **3-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.9 -> 🔴 LOST (Expected prob: 59.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.9% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.3% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 94.0% (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.2% (Actual: 4 goals)

### 2026-08-28: Ansan Greeners vs Daegu FC (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.4 -> 🟢 WON (Expected prob: 59.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.0% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 95.8% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.1% (Actual: 3 goals)

### 2026-08-28: Universitatea Cluj vs Petrolul Ploiesti (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 2.11 -> 🔴 LOST (Expected prob: 58.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.3% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 3 away goals)

### 2026-08-28: St Patricks Dublin vs Waterford United (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🔴 LOST (Expected prob: 56.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.2% (Actual: 2 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 80.9% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 2 away goals)

### 2026-08-28: Holywell Town vs Caernarfon Town (Actual Score: **3-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.28 -> 🟢 WON (Expected prob: 68.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.4% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 35.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 92.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.7% (Actual: 8 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.7% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 87.4% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.7% (Actual: 8 goals)

### 2026-08-28: Qatar SC vs Al Sadd SC (Actual Score: **2-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.42 -> 🟢 WON (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.5% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.2% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.4% (Actual: 8 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.2% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.2% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.2% (Actual: 8 goals)

### 2026-08-28: Bayern München vs VfB Stuttgart (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 79.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.2% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.3% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.6% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.5% (Actual: 6 goals)

### 2026-08-28: Legia Warszawa vs Slask Wroclaw (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🔴 LOST (Expected prob: 66.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.8% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.3% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.7% (Actual: 2 goals)

### 2026-08-28: Pen-y-Bont FC vs Flint Town Utd (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 64.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.6% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.1% (Actual: 2 goals)

### 2026-08-28: Scunthorpe Utd vs Solihull Moors (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🟢 WON (Expected prob: 57.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.4% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.5% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 1 away goals)


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

- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (pending_or_unmatched_result); keys=['charlesto']/['miami', 'miamiii']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)

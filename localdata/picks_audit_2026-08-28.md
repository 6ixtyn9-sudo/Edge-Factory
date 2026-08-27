# Edge Factory — Recent picks audit (2026-07-30 to 2026-08-28)

## Overall

- archived pick rows: 407
- archived pick dates: 30
- immutable morning-baseline rows: 279
- verified official late-slate additions: 13
- regular-ledger-only legacy rows: 115
- unsafe regular ledgers ignored: 11
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 369
- eligible prior 1x2 picks: 386
- pending/unmatched result picks: 8
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 6
- ambiguous result picks: 0
- wins: 266
- hit rate: +72.1%
- priced picks: 349
- ROI: +0.1%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-28
- same-day rows excluded: 21

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 241 / 369 matches (65.3%)
- **Both Teams to Score (BTTS)**: occurred in 191 / 369 matches (51.8%)
- **Selected Team Over 1.5 Goals**: occurred in 265 / 369 matches (71.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 369
- **Total Hits**: 285
- **Overall Hit Rate**: 77.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=8, hits=8, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=137, hits=124, hit_rate=90.5%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=10, hits=10, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=157, hits=109, hit_rate=69.4%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2198** | scored: 2198

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 304 | 304 | 199 | 65.5% | 46.0% | +19.5% | 0.26649 |
| `away_under_35` | 289 | 289 | 282 | 97.6% | 98.0% | -0.4% | 0.022617 |
| `away_under_25` | 272 | 272 | 257 | 94.5% | 93.8% | +0.7% | 0.052818 |
| `home_over_05` | 268 | 268 | 246 | 91.8% | 86.9% | +4.9% | 0.077972 |
| `match_over_45` | 255 | 255 | 75 | 29.4% | 24.8% | +4.6% | 0.211461 |
| `away_under_15` | 104 | 104 | 85 | 81.7% | 81.5% | +0.3% | 0.148953 |
| `match_over_35` | 98 | 98 | 38 | 38.8% | 43.0% | -4.2% | 0.244783 |
| `home_under_35` | 79 | 79 | 75 | 94.9% | 94.5% | +0.5% | 0.047572 |
| `exact_4` | 67 | 67 | 17 | 25.4% | 18.0% | +7.3% | 0.196872 |
| `home_under_25` | 65 | 65 | 61 | 93.8% | 91.4% | +2.5% | 0.0595 |
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
| hybrid_cohort | 1860 | 1289 | 69.3% | 65.7% | +3.6% | 0.13097 |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| model | 75 | 54 | 72.0% | 53.5% | +18.5% | 0.276534 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 178 | 16.3% | 20.2% | +3.9% |
| 0.2-0.3 | 268 | 25.0% | 28.4% | +3.4% |
| 0.3-0.4 | 229 | 35.5% | 44.5% | +9.1% |
| 0.4-0.5 | 248 | 45.2% | 53.2% | +8.0% |
| 0.5-0.6 | 144 | 53.0% | 56.9% | +4.0% |
| 0.6-0.7 | 10 | 64.2% | 80.0% | +15.8% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 380 | 84.4% | 88.2% | +3.7% |
| 0.9-1.0 | 737 | 95.4% | 95.8% | +0.4% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=368, MAE=1.497283 goals, bias=-0.209076 (realized − promised), promised avg 3.60038 vs realized 3.391304

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 368 | 25.7% | 33.2% | +7.4% | 0.186294 |
| BTTS-Yes | 368 | 41.2% | 51.9% | +10.7% | 0.261494 |
| Home Over 1.5 | 368 | 69.6% | 61.1% | -8.5% | 0.22608 |
| Over 2.5 | 368 | 70.8% | 65.2% | -5.6% | 0.227129 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 246 | 8.8% | 20.7% | +11.9% |
| 0.1-0.2 | 124 | 10.5% | 27.4% | +16.9% |
| 0.2-0.3 | 3 | 20.5% | 0.0% | -20.5% |
| 0.3-0.4 | 99 | 37.7% | 54.5% | +16.9% |
| 0.4-0.5 | 264 | 43.0% | 51.1% | +8.1% |
| 0.6-0.7 | 196 | 66.8% | 59.7% | -7.1% |
| 0.7-0.8 | 157 | 74.7% | 70.1% | -4.7% |
| 0.8-0.9 | 327 | 84.9% | 70.9% | -14.0% |
| 0.9-1.0 | 56 | 91.7% | 80.4% | -11.4% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=109, wins=89, hit_rate=0.816514, ROI=0.0762
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=36, wins=28, hit_rate=0.777778, ROI=0.059028
- `ml-meta avg_p>=55`: settled=149, wins=95, hit_rate=0.637584, ROI=-0.057887
- `ml-meta avg_p>=60`: settled=20, wins=17, hit_rate=0.85, ROI=0.204
- `ml-meta avg_p>=65`: settled=4, wins=3, hit_rate=0.75, ROI=-0.046667
- `ml-meta avg_p>=70`: settled=7, wins=6, hit_rate=0.857143, ROI=0.122857
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06

## By bucket

- `CAUTION`: settled=66, wins=41, hit_rate=0.621212, ROI=-0.022121
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=193, wins=144, hit_rate=0.746114, ROI=0.024378
- `WATCHLIST_NO_ODDS`: settled=19, wins=17, hit_rate=0.894737, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=3, hit_rate=0.6, ROI=-0.0825
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=44, wins=33, hit_rate=0.75, ROI=0.073636
- `WATCHLIST_UNKNOWN_CTX`: settled=21, wins=19, hit_rate=0.904762, ROI=0.106667

## By odds source

- `UNKNOWN`: settled=20, wins=17, hit_rate=0.85, ROI=None
- `betexplorer_odds`: settled=132, wins=99, hit_rate=0.75, ROI=0.040833
- `bzzoiro_odds`: settled=85, wins=56, hit_rate=0.658824, ROI=-0.042412
- `forebet_best`: settled=19, wins=12, hit_rate=0.631579, ROI=-0.138947
- `scoutingstats_odds`: settled=102, wins=71, hit_rate=0.696078, ROI=-0.023922
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=17, wins=11, hit_rate=0.647059, ROI=-0.1275
- `betexplorer`: settled=132, wins=99, hit_rate=0.75, ROI=0.040833
- `exact`: settled=180, wins=123, hit_rate=0.683333, ROI=-0.022639
- `fallback`: settled=21, wins=16, hit_rate=0.761905, ROI=0.058571
- `none`: settled=19, wins=17, hit_rate=0.894737, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 132 | 99 | 0.75 | 132 | 0.040833 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 78 | 52 | 0.666667 | 78 | -0.020962 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 102 | 71 | 0.696078 | 102 | -0.023922 |
| Source fallback (`SOURCE_FALLBACK`) | 21 | 16 | 0.761905 | 21 | 0.058571 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 17 | 11 | 0.647059 | 16 | -0.1275 |
| No usable price (`UNMATCHED`) | 19 | 17 | 0.894737 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 193 | 144 | 0.746114 | 193 | 0.024378 |
| **trusted evidence only** | 118 | 93 | 0.788136 | 118 | 0.08072 |
| **soft evidence only** | 75 | 51 | 0.68 | 75 | -0.064267 |
| evidence: BETEXPLORER_RESCUE | 71 | 59 | 0.830986 | 71 | 0.102817 |
| evidence: BZZOIRO_PRIMARY | 47 | 34 | 0.723404 | 47 | 0.04734 |
| evidence: SCOUTINGSTATS_SOLE | 56 | 37 | 0.660714 | 56 | -0.0875 |
| evidence: SOURCE_FALLBACK | 11 | 8 | 0.727273 | 11 | 0.021818 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 8 | -0.02 |
| odds band: <1.50 | 137 | 112 | 0.817518 | 137 | 0.053102 |
| odds band: 1.50-2.00 | 53 | 30 | 0.566038 | 53 | -0.068302 |
| odds band: 2.00-3.00 | 3 | 2 | 0.666667 | 3 | 0.35 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.05 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.495 |
| veto reason: context VETO in ['league', 'team_a'] | 6 | 3 | 0.5 | 6 | -0.431667 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.48 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 8 | 5 | 0.625 | 8 | -0.12375 |
| veto reason: context VETO in ['niche'] | 2 | 1 | 0.5 | 2 | -0.14 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: context VETO in ['odds_band'] | 48 | 41 | 0.854167 | 48 | 0.153958 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.196364 |
| veto reason: context VETO in ['team_a'] | 29 | 22 | 0.758621 | 29 | 0.133448 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 10 | 9 | 0.9 | 10 | 0.243 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 4 | 2 | 0.5 | 4 | -0.26 |
| veto reason: context VETO in ['team_h', 'team_a'] | 14 | 7 | 0.5 | 14 | -0.321429 |
| veto reason: context VETO in ['team_h'] | 44 | 30 | 0.681818 | 44 | -0.046932 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 37 | 23 | 0.621622 | 37 | 0.001892 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0025 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 6 | 5 | 0.833333 | 6 | 0.236667 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 250 | 184 | 0.736 | 231 | 0.02158 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 17 | 11 | 0.647059 | 16 | -0.1275 | 10 | 1.3545 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 102 | 71 | 0.696078 | 102 | -0.023922 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-27: Real Potosí vs Real Tomayapo (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🔴 LOST (Expected prob: 79.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 77.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 52.3% (Actual: 1 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 87.9% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.2% (Actual: 1 goals)

### 2026-08-27: Fulham vs AFC Wimbledon (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.18 -> 🟢 WON (Expected prob: 75.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.7% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.8% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.0% (Actual: 3 goals)

### 2026-08-27: Freiburg vs Motherwell (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 70.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.3% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.1% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.1% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.4% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.6% (Actual: 5 goals)

### 2026-08-27: Riga vs KI Klaksvik (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.43 -> 🟢 WON (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.1% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.2% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.1% (Actual: 3 goals)

### 2026-08-27: Pafos vs Dinamo Tirana (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 65.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.5% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.1% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.5% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.2% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 82.4% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.0% (Actual: 6 goals)

### 2026-08-27: Brighton vs Tromso (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 62.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.4% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.6% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.1% (Actual: 4 goals)


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
- 2026-08-15 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous min_p>=60 avg_p>=65` — Olympic Kingsway vs Sorrento FC -> HOME @ 1.24 (pending_or_unmatched_result); keys=['olympicki']/['sorrento']
- 2026-08-17 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hamrun Spartans vs Mosta -> HOME @ 1.18 (pending_or_unmatched_result); keys=['hamrunspa']/['mosta']
- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (pending_or_unmatched_result); keys=['charlesto']/['miami', 'miamiii']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']

## Ambiguous result examples

- none

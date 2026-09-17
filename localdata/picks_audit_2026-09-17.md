# Edge Factory — Recent picks audit (2026-08-19 to 2026-09-17)

## Overall

- archived pick rows: 589
- archived pick dates: 30
- immutable morning-baseline rows: 582
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 7
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 557
- eligible prior picks: 581
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 4
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 376
- hit rate: +67.5%
- priced picks: 524
- ROI: -3.4%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-17
- same-day rows excluded: 8

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 323 / 511 matches (63.2%)
- **Both Teams to Score (BTTS)**: occurred in 272 / 511 matches (53.2%)
- **Selected Team Over 1.5 Goals**: occurred in 347 / 511 matches (67.9%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 557
- **Total Hits**: 400
- **Overall Hit Rate**: 71.8%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=3, hits=2, hit_rate=66.7%
- `away_under_35`: recommended=83, hits=79, hit_rate=95.2%
- `home_over_05`: recommended=43, hits=33, hit_rate=76.7%
- `home_under_25`: recommended=4, hits=4, hit_rate=100.0%
- `home_under_35`: recommended=11, hits=10, hit_rate=90.9%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=334, hits=214, hit_rate=64.1%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2435** | scored: 2435

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 550 | 550 | 346 | 62.9% | 47.4% | +15.5% | 0.256758 |
| `match_over_45` | 414 | 414 | 121 | 29.2% | 23.9% | +5.4% | 0.208784 |
| `away_under_35` | 402 | 402 | 388 | 96.5% | 97.4% | -0.8% | 0.032439 |
| `away_under_25` | 371 | 371 | 344 | 92.7% | 93.4% | -0.7% | 0.067827 |
| `home_over_05` | 248 | 248 | 219 | 88.3% | 84.5% | +3.8% | 0.104245 |
| `home_under_35` | 157 | 157 | 153 | 97.5% | 95.6% | +1.9% | 0.025177 |
| `home_under_25` | 119 | 119 | 109 | 91.6% | 91.7% | -0.1% | 0.076787 |
| `away_under_15` | 53 | 53 | 42 | 79.2% | 81.0% | -1.7% | 0.167035 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 29 | 29 | 26 | 89.7% | 88.7% | +0.9% | 0.08967 |
| `home_under_15` | 15 | 15 | 11 | 73.3% | 81.4% | -8.1% | 0.206266 |
| `double_chance` | 1 | 1 | 1 | 100.0% | 84.6% | +15.4% | 0.023822 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2163 | 1616 | 74.7% | 70.4% | +4.3% | 0.132356 |
| model | 272 | 193 | 71.0% | 64.1% | +6.8% | 0.181036 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 123 | 19.1% | 23.6% | +4.5% |
| 0.2-0.3 | 248 | 24.8% | 31.0% | +6.2% |
| 0.3-0.4 | 73 | 33.1% | 42.5% | +9.4% |
| 0.4-0.5 | 408 | 45.3% | 61.0% | +15.8% |
| 0.5-0.6 | 140 | 53.2% | 66.4% | +13.2% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 418 | 84.4% | 86.4% | +2.0% |
| 0.9-1.0 | 1020 | 95.3% | 94.7% | -0.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=510, MAE=1.609 goals, bias=-0.164569 (realized − promised), promised avg 3.525353 vs realized 3.360784

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 510 | 29.8% | 37.1% | +7.2% | 0.214591 |
| BTTS-Yes | 510 | 41.6% | 53.3% | +11.7% | 0.263748 |
| Home Over 1.5 | 510 | 65.1% | 57.5% | -7.7% | 0.255224 |
| Over 2.5 | 510 | 69.7% | 63.1% | -6.6% | 0.235471 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 237 | 8.8% | 26.2% | +17.3% |
| 0.1-0.2 | 275 | 10.4% | 27.6% | +17.2% |
| 0.2-0.3 | 9 | 22.4% | 44.4% | +22.0% |
| 0.3-0.4 | 100 | 37.4% | 55.0% | +17.6% |
| 0.4-0.5 | 398 | 43.2% | 53.0% | +9.8% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 337 | 66.7% | 60.8% | -5.9% |
| 0.7-0.8 | 153 | 74.7% | 66.0% | -8.7% |
| 0.8-0.9 | 477 | 84.4% | 67.3% | -17.1% |
| 0.9-1.0 | 53 | 92.2% | 77.4% | -14.8% |

## By rule

- `2way-unanimous avg_p>=70`: settled=116, wins=88, hit_rate=0.758621, ROI=0.0298
- `ml-meta avg_p>=55`: settled=326, wins=201, hit_rate=0.616564, ROI=-0.075903
- `ml-meta avg_p>=60`: settled=45, wins=38, hit_rate=0.844444, ROI=0.151556
- `ml-meta avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.2
- `ml-meta avg_p>=70`: settled=11, wins=10, hit_rate=0.909091, ROI=0.14
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=3, wins=3, hit_rate=1.0, ROI=0.1
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=57, wins=44, hit_rate=0.77193, ROI=0.172982
- `CERTIFIED_CLEAN`: settled=32, wins=23, hit_rate=0.71875, ROI=0.080938
- `SKIPPED_VETO`: settled=283, wins=183, hit_rate=0.646643, ROI=-0.09935
- `WATCHLIST_NO_ODDS`: settled=25, wins=17, hit_rate=0.68, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.056667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=136, wins=90, hit_rate=0.661765, ROI=-0.038824
- `WATCHLIST_UNKNOWN_CTX`: settled=7, wins=7, hit_rate=1.0, ROI=0.221429

## By odds source

- `UNKNOWN`: settled=33, wins=21, hit_rate=0.636364, ROI=None
- `betexplorer_odds`: settled=154, wins=106, hit_rate=0.688312, ROI=-0.053506
- `bzzoiro_odds`: settled=11, wins=11, hit_rate=1.0, ROI=0.518182
- `forebet_best`: settled=61, wins=45, hit_rate=0.737705, ROI=0.077049
- `scoutingstats_odds`: settled=298, wins=193, hit_rate=0.647651, ROI=-0.067483

## By odds match method

- `alias_fuzzy`: settled=25, wins=18, hit_rate=0.72, ROI=0.020909
- `betexplorer`: settled=154, wins=106, hit_rate=0.688312, ROI=-0.053506
- `exact`: settled=309, wins=204, hit_rate=0.660194, ROI=-0.046634
- `fallback`: settled=39, wins=29, hit_rate=0.74359, ROI=0.108718
- `none`: settled=30, wins=19, hit_rate=0.633333, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 154 | 106 | 0.688312 | 154 | -0.053506 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 11 | 11 | 1.0 | 11 | 0.518182 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 298 | 193 | 0.647651 | 298 | -0.067483 |
| Source fallback (`SOURCE_FALLBACK`) | 39 | 29 | 0.74359 | 39 | 0.108718 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 25 | 18 | 0.72 | 22 | 0.020909 |
| No usable price (`UNMATCHED`) | 30 | 19 | 0.633333 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 283 | 183 | 0.646643 | 277 | -0.09935 |
| **trusted evidence only** | 94 | 63 | 0.670213 | 94 | -0.108936 |
| **soft evidence only** | 189 | 120 | 0.634921 | 183 | -0.094426 |
| evidence: BETEXPLORER_RESCUE | 89 | 58 | 0.651685 | 89 | -0.144719 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.528 |
| evidence: SCOUTINGSTATS_SOLE | 162 | 103 | 0.635802 | 162 | -0.091543 |
| evidence: SOURCE_FALLBACK | 14 | 9 | 0.642857 | 14 | -0.147143 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.055714 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 170 | 128 | 0.752941 | 170 | -0.047235 |
| odds band: 1.50-2.00 | 99 | 48 | 0.484848 | 99 | -0.200909 |
| odds band: 2.00-3.00 | 8 | 4 | 0.5 | 8 | 0.05 |
| odds band: unpriced | 6 | 3 | 0.5 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 3 | 1.0 | 2 | 0.305 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 5 | 1.0 | 5 | 0.146 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 11 | 4 | 0.363636 | 11 | -0.573636 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 4 | 2 | 0.5 | 4 | -0.2025 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['league', 'team_h'] | 12 | 8 | 0.666667 | 12 | -0.115 |
| veto reason: context VETO in ['league'] | 15 | 10 | 0.666667 | 13 | 0.049231 |
| veto reason: context VETO in ['niche'] | 6 | 4 | 0.666667 | 6 | -0.056667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 4 | 4 | 1.0 | 4 | 0.26 |
| veto reason: context VETO in ['odds_band'] | 45 | 33 | 0.733333 | 45 | -0.069556 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 9 | 0.818182 | 11 | 0.031818 |
| veto reason: context VETO in ['team_a'] | 42 | 22 | 0.52381 | 40 | -0.14375 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 1 | 0.25 | 4 | -0.64 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.221818 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.446667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.123333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 16 | 7 | 0.4375 | 16 | -0.286875 |
| veto reason: context VETO in ['team_h'] | 63 | 37 | 0.587302 | 62 | -0.149839 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 34 | 25 | 0.735294 | 34 | 0.083529 |
| contrast CAUTION: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.512 |
| contrast CAUTION: SOURCE_FALLBACK | 18 | 14 | 0.777778 | 18 | 0.247778 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 234 | 165 | 0.705128 | 204 | 0.008333 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 25 | 18 | 0.72 | 22 | 0.020909 | 25 | 1.5388 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 298 | 193 | 0.647651 | 298 | -0.067483 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-16: Spartak Moscow vs Fakel Voronezh (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 63.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.3% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.1% (Actual: 1 goals)

### 2026-09-16: Atletico Madrid vs Osasuna (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 58.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.2% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.4% (Actual: 4 goals)

### 2026-09-16: Bayer Leverkusen vs NK Celje (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 82.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 76.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 95.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.5% (Actual: 2 goals)

### 2026-09-16: Barcelona vs Racing Santander (Actual Score: **7-2**)
- **1X2 Pick**: Selected `HOME` @ 1.06 -> 🟢 WON (Expected prob: 73.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.2% (Actual: 9 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.7% (Actual: 7 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.6% (Actual: 9 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 32.9% (Actual: 9 goals)

### 2026-09-16: FC Differdange 03 vs Swift Hesperange (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.02 -> 🟢 WON (Expected prob: 81.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 93.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.4% (Actual: 3 goals)

### 2026-09-16: Lokomotiv Sofia vs CSKA-Sofia (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.55 -> 🟢 WON (Expected prob: 72.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 32.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.7% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.5% (Actual: 2 goals)

### 2026-09-16: Lugano vs St Gallen (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 2.0 -> 🟢 WON (Expected prob: 57.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.0% (Actual: 5 goals)

### 2026-09-16: Scunthorpe Utd vs Boreham Wood (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.7 -> 🟢 WON (Expected prob: 55.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.5% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.1% (Actual: 3 goals)

### 2026-09-16: Sturm Graz vs Rennes (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.98 -> 🔴 LOST (Expected prob: 59.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.7% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.0% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.6% (Actual: 0 goals)

### 2026-09-16: Rivers United vs Warri Wolves (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.32 -> 🟢 WON (Expected prob: 57.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.1% (Actual: 0 away goals)
    - [🟢 HIT] **Double Chance 1X**: expected 84.6% (Actual: home (2-0))
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.4% (Actual: 2 goals)

### 2026-09-16: Vis Pesaro vs Reggiana (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.83 -> 🟢 WON (Expected prob: 55.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.7% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.3% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.1% (Actual: 5 goals)

### 2026-09-16: UNA Strassen vs US Rumelange (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 81.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 93.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.0% (Actual: 2 goals)

### 2026-09-16: Phönix Lübeck vs Todesfelde (Actual Score: **9-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 73.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.4% (Actual: 9 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 9 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.9% (Actual: 9 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 30.3% (Actual: 9 goals)

### 2026-09-16: Kidderminster vs Gateshead (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 64.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.6% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.4% (Actual: 1 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 4 |
- 2026-08-21 `POSTPONED` `SKIPPED_VETO` — Shamrock Rovers vs Shelbourne FC (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — Rangers vs St Mirren (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — St Johnstone vs Celtic (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — Hibernian vs Kilmarnock (verified_disposition); excluded from win/loss/ROI

## Rescheduled Fixture Examples

- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (rescheduled → 2026-08-24; actual Charleston Battery 5-0 Miami FC II [home])
- 2026-08-29 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hønefoss W vs Fortuna Ålesund W -> AWAY @ 1.2 (rescheduled → 2026-08-31; actual Hønefoss W 0-1 Fortuna Ålesund W [away])
- 2026-08-29 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — LSK Kvinner W vs Bodø / Glimt W -> HOME @ None (rescheduled → 2026-09-01; actual LSK Kvinner W 1-1 Bodø / Glimt W [draw])
- 2026-08-29 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Viking vs Aalesund -> HOME @ 1.3 (rescheduled → 2026-08-30; actual Viking 2-1 Aalesund [home])
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 3-3 Go Ahead Eagles [draw])
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])

## Pending / Unmatched Result Examples

- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)
- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

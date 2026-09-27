# Edge Factory — Recent picks audit (2026-08-29 to 2026-09-27)

## Overall

- archived pick rows: 660
- archived pick dates: 30
- immutable morning-baseline rows: 660
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 611
- eligible prior picks: 628
- pending/unmatched result picks: 6
- rescheduled result picks (settled ±3d): 9
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 402
- hit rate: +65.8%
- priced picks: 563
- ROI: -4.5%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-27
- same-day rows excluded: 32

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 348 / 565 matches (61.6%)
- **Both Teams to Score (BTTS)**: occurred in 314 / 565 matches (55.6%)
- **Selected Team Over 1.5 Goals**: occurred in 361 / 565 matches (63.9%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 611
- **Total Hits**: 468
- **Overall Hit Rate**: 76.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=139, hits=134, hit_rate=96.4%
- `home_over_05`: recommended=27, hits=20, hit_rate=74.1%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=21, hits=20, hit_rate=95.2%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=288, hits=182, hit_rate=63.2%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2491** | scored: 2491

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 604 | 604 | 371 | 61.4% | 45.9% | +15.5% | 0.261091 |
| `match_over_45` | 473 | 473 | 122 | 25.8% | 23.9% | +1.9% | 0.189401 |
| `away_under_35` | 428 | 428 | 416 | 97.2% | 96.2% | +1.0% | 0.027295 |
| `away_under_25` | 390 | 390 | 356 | 91.3% | 92.4% | -1.1% | 0.07972 |
| `home_under_35` | 169 | 169 | 165 | 97.6% | 94.4% | +3.2% | 0.025021 |
| `home_over_05` | 145 | 145 | 127 | 87.6% | 83.9% | +3.7% | 0.110524 |
| `home_under_25` | 138 | 138 | 127 | 92.0% | 91.0% | +1.1% | 0.073471 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 32 | 32 | 29 | 90.6% | 88.0% | +2.7% | 0.084847 |
| `away_under_15` | 20 | 20 | 14 | 70.0% | 80.9% | -10.9% | 0.22534 |
| `home_under_15` | 13 | 13 | 9 | 69.2% | 81.6% | -12.3% | 0.232124 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2236 | 1606 | 71.8% | 67.6% | +4.2% | 0.135685 |
| model | 255 | 181 | 71.0% | 63.8% | +7.1% | 0.17344 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 124 | 19.2% | 19.4% | +0.2% |
| 0.2-0.3 | 296 | 24.4% | 26.0% | +1.6% |
| 0.3-0.4 | 87 | 33.2% | 47.1% | +13.9% |
| 0.4-0.5 | 498 | 44.6% | 60.4% | +15.8% |
| 0.5-0.6 | 105 | 52.7% | 61.9% | +9.2% |
| 0.8-0.9 | 351 | 85.1% | 86.0% | +0.9% |
| 0.9-1.0 | 1030 | 94.6% | 94.9% | +0.3% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=565, MAE=1.584779 goals, bias=-0.260885 (realized − promised), promised avg 3.517522 vs realized 3.256637

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 565 | 31.1% | 35.9% | +4.9% | 0.240136 |
| BTTS-Yes | 565 | 41.7% | 55.6% | +13.8% | 0.266661 |
| Home Over 1.5 | 565 | 63.9% | 53.8% | -10.1% | 0.251626 |
| Over 2.5 | 565 | 69.6% | 61.6% | -8.0% | 0.242063 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 243 | 8.8% | 26.3% | +17.5% |
| 0.1-0.2 | 324 | 10.4% | 25.9% | +15.5% |
| 0.2-0.3 | 7 | 24.6% | 57.1% | +32.5% |
| 0.3-0.4 | 97 | 37.3% | 54.6% | +17.4% |
| 0.4-0.5 | 458 | 43.0% | 55.7% | +12.6% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 385 | 66.8% | 60.3% | -6.6% |
| 0.7-0.8 | 161 | 74.6% | 63.4% | -11.2% |
| 0.8-0.9 | 535 | 84.5% | 63.6% | -21.0% |
| 0.9-1.0 | 49 | 92.4% | 71.4% | -21.0% |

## By rule

- `2way-unanimous avg_p>=60`: settled=53, wins=34, hit_rate=0.641509, ROI=-0.110476
- `2way-unanimous avg_p>=70`: settled=112, wins=81, hit_rate=0.723214, ROI=-0.015506
- `ml-meta avg_p>=55`: settled=330, wins=200, hit_rate=0.606061, ROI=-0.065489
- `ml-meta avg_p>=60`: settled=51, wins=43, hit_rate=0.843137, ROI=0.157451
- `ml-meta avg_p>=65`: settled=10, wins=8, hit_rate=0.8, ROI=0.05
- `ml-meta avg_p>=70`: settled=5, wins=4, hit_rate=0.8, ROI=-0.108
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=3, wins=3, hit_rate=1.0, ROI=0.086667
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=54, wins=35, hit_rate=0.648148, ROI=-0.016852
- `CERTIFIED_CLEAN`: settled=55, wins=38, hit_rate=0.690909, ROI=0.078
- `SKIPPED_VETO`: settled=285, wins=184, hit_rate=0.645614, ROI=-0.084109
- `WATCHLIST_NO_ODDS`: settled=36, wins=23, hit_rate=0.638889, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.117333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=159, wins=106, hit_rate=0.666667, ROI=-0.044465
- `WATCHLIST_UNKNOWN_CTX`: settled=5, wins=4, hit_rate=0.8, ROI=-0.016

## By odds source

- `UNKNOWN`: settled=48, wins=30, hit_rate=0.625, ROI=None
- `betexplorer_odds`: settled=158, wins=103, hit_rate=0.651899, ROI=-0.062468
- `bzzoiro_odds`: settled=5, wins=4, hit_rate=0.8, ROI=0.2
- `forebet_best`: settled=78, wins=55, hit_rate=0.705128, ROI=0.043462
- `scoutingstats_odds`: settled=320, wins=208, hit_rate=0.65, ROI=-0.063531
- `zulubet`: settled=2, wins=2, hit_rate=1.0, ROI=0.335

## By odds match method

- `alias_fuzzy`: settled=26, wins=19, hit_rate=0.730769, ROI=0.067826
- `betexplorer`: settled=158, wins=103, hit_rate=0.651899, ROI=-0.062468
- `exact`: settled=325, wins=212, hit_rate=0.652308, ROI=-0.059477
- `fallback`: settled=57, wins=40, hit_rate=0.701754, ROI=0.04386
- `none`: settled=45, wins=28, hit_rate=0.622222, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 158 | 103 | 0.651899 | 158 | -0.062468 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 5 | 4 | 0.8 | 5 | 0.2 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 320 | 208 | 0.65 | 320 | -0.063531 |
| Source fallback (`SOURCE_FALLBACK`) | 57 | 40 | 0.701754 | 57 | 0.04386 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 26 | 19 | 0.730769 | 23 | 0.067826 |
| No usable price (`UNMATCHED`) | 45 | 28 | 0.622222 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 285 | 184 | 0.645614 | 275 | -0.084109 |
| **trusted evidence only** | 87 | 54 | 0.62069 | 87 | -0.146782 |
| **soft evidence only** | 198 | 130 | 0.656566 | 188 | -0.055106 |
| evidence: BETEXPLORER_RESCUE | 84 | 51 | 0.607143 | 84 | -0.169881 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.5 |
| evidence: SCOUTINGSTATS_SOLE | 161 | 102 | 0.63354 | 161 | -0.08236 |
| evidence: SOURCE_FALLBACK | 19 | 16 | 0.842105 | 19 | 0.163158 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 8 | -0.025 |
| evidence: UNMATCHED | 9 | 5 | 0.555556 | 0 | None |
| odds band: <1.50 | 160 | 119 | 0.74375 | 160 | -0.056063 |
| odds band: 1.50-2.00 | 108 | 54 | 0.5 | 108 | -0.166759 |
| odds band: 2.00-3.00 | 7 | 5 | 0.714286 | 7 | 0.55 |
| odds band: unpriced | 10 | 6 | 0.6 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.21 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.1 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.49 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.41 |
| veto reason: context VETO in ['league', 'team_h'] | 13 | 9 | 0.692308 | 13 | -0.065385 |
| veto reason: context VETO in ['league'] | 22 | 18 | 0.818182 | 16 | 0.308125 |
| veto reason: context VETO in ['niche'] | 9 | 7 | 0.777778 | 9 | 0.071111 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.273333 |
| veto reason: context VETO in ['odds_band'] | 51 | 35 | 0.686275 | 51 | -0.12451 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 10 | 6 | 0.6 | 10 | -0.253 |
| veto reason: context VETO in ['team_a'] | 48 | 24 | 0.5 | 46 | -0.21087 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 7 | 1.0 | 7 | 0.357143 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.054286 |
| veto reason: context VETO in ['team_h', 'team_a'] | 15 | 7 | 0.466667 | 15 | -0.176667 |
| veto reason: context VETO in ['team_h'] | 56 | 33 | 0.589286 | 55 | -0.090364 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 30 | 21 | 0.7 | 30 | 0.021 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 23 | 14 | 0.608696 | 23 | -0.023478 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 265 | 175 | 0.660377 | 220 | -0.028955 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 26 | 19 | 0.730769 | 23 | 0.067826 | 26 | 1.549615 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 320 | 208 | 0.65 | 320 | -0.063531 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-26: Sollentuna FK vs Stockholm Internazionale (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.5 -> 🟢 WON (Expected prob: 73.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 34.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.1% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.5% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 85.3% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.3% (Actual: 3 goals)

### 2026-09-26: Ústí nad Labem II vs Újezd Praha 4 (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.6 -> 🔴 LOST (Expected prob: 70.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.6% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 36.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.2% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.1% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.8% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.2% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.1% (Actual: 2 goals)

### 2026-09-26: Banik Sokolov vs Ostrov (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 69.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 86.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.3% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.4% (Actual: 3 goals)

### 2026-09-26: Vänersborgs FK vs Husqvarna FF (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.52 -> 🟢 WON (Expected prob: 66.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.2% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.3% (Actual: 3 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.3% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.8% (Actual: 4 goals)

### 2026-09-26: AIK W vs Växjö W (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 65.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.7% (Actual: 3 goals)

### 2026-09-26: Cavalry FC vs Supra du Québec (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ 1.52 -> 🟢 WON (Expected prob: 65.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.5% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.7% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.7% (Actual: 6 goals)

### 2026-09-26: Opava U19 vs Slovacko U19 (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🔴 LOST (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.3% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.4% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.0% (Actual: 6 goals)

### 2026-09-26: Southend vs Barrow (Actual Score: **2-4**)
- **1X2 Pick**: Selected `HOME` @ 1.71 -> 🔴 LOST (Expected prob: 62.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.7% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.6% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.9% (Actual: 6 goals)

### 2026-09-26: Brabrand IF vs Nykøbing FC (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.65 -> 🔴 LOST (Expected prob: 62.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.5% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.2% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 81.0% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.8% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.7% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.7% (Actual: 2 goals)

### 2026-09-26: Volga Ulyanovsk vs FK Leningradets (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.76 -> 🔴 LOST (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.5% (Actual: 1 goals)

### 2026-09-26: Skellefteå FF vs Gottne IF (Actual Score: **0-3**)
- **1X2 Pick**: Selected `HOME` @ 1.56 -> 🔴 LOST (Expected prob: 56.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.1% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 88.0% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.7% (Actual: 3 goals)

### 2026-09-26: Trefelin BGC vs The New Saints (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.04 -> 🟢 WON (Expected prob: 75.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 17.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 96.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 89.3% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.0% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 37.3% (Actual: 4 goals)

### 2026-09-26: Norrköping W vs Hacken W (Actual Score: **0-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.21 -> 🟢 WON (Expected prob: 77.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.0% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 93.3% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.0% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.4% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.0% (Actual: 6 goals)

### 2026-09-26: Solihull Moors vs Boreham Wood (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.5 -> 🟢 WON (Expected prob: 70.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.9% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 31.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.5% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.9% (Actual: 3 goals)

### 2026-09-26: Stabæk W vs Brann W (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.27 -> 🟢 WON (Expected prob: 67.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.3% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.3% (Actual: 1 goals)

### 2026-09-26: FK Vidar vs Mjondalen IF (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.45 -> 🟢 WON (Expected prob: 66.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.8% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.5% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.8% (Actual: 4 goals)

### 2026-09-26: Stockport County vs Peterborough (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 66.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.4% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.7% (Actual: 1 goals)

### 2026-09-26: Sotra SK vs Pors Grenland (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 64.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.2% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.2% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.3% (Actual: 5 goals)

### 2026-09-26: Cardiff Met vs Caernarfon Town (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.9 -> 🔴 LOST (Expected prob: 64.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.5% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.5% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.7% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.7% (Actual: 4 goals)

### 2026-09-26: RSV Eintracht vs Chemnitzer FC (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 63.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.4% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.5% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.0% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.7% (Actual: 4 goals)

### 2026-09-26: Cambridge United vs AFC Wimbledon (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🔴 LOST (Expected prob: 61.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.0% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.0% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.3% (Actual: 2 goals)

### 2026-09-26: Wienerberg vs Scheiblingkirchen (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.45 -> 🟢 WON (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 82.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.2% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 85.6% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.4% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.9% (Actual: 4 goals)

### 2026-09-26: Wealdstone vs Gateshead (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 56.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.1% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.4% (Actual: 4 goals)

### 2026-09-26: MŠK Považská Bystrica vs MFK Bytča (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 58.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.3% (Actual: 5 goals)

### 2026-09-26: FC Kitzbühel vs Rheindorf Altach II (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 64.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.1% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.2% (Actual: 4 goals)

### 2026-09-26: SC Imst vs Lochau (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 63.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.2% (Actual: 3 goals)

### 2026-09-26: Holesov vs FK Kozlovice (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 61.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.1% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 83.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.8% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 85.1% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.4% (Actual: 2 goals)

### 2026-09-26: Peñarol vs Boston River (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 68.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.6% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.2% (Actual: 3 goals)

### 2026-09-26: Granada vs FC Andorra (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 2.2 -> 🔴 LOST (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.6% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.8% (Actual: 5 goals)

### 2026-09-26: Kozakken Boys vs Koninklijke HFC (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🔴 LOST (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.0% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.2% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.8% (Actual: 2 goals)

### 2026-09-26: Ballymena United vs Portadown FC (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 61.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.2% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.0% (Actual: 2 goals)

### 2026-09-26: Iceland vs Estonia (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🔴 LOST (Expected prob: 60.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.3% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.0% (Actual: 2 goals)

### 2026-09-26: Slovakia vs Moldova (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 59.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.0% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 2 goals)

### 2026-09-26: San Marino vs Finland (Actual Score: **0-7**)
- **1X2 Pick**: Selected `AWAY` @ 1.07 -> 🟢 WON (Expected prob: 72.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.4% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-No**: expected 29.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 87.8% (Actual: 7 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.7% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.2% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.6% (Actual: 7 goals)

### 2026-09-26: FK Krimice vs Jiskra Domažlice II (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 76.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.4% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.3% (Actual: 1 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-08-29 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hønefoss W vs Fortuna Ålesund W -> AWAY @ 1.2 (rescheduled → 2026-08-31; actual Hønefoss W 0-1 Fortuna Ålesund W [away])
- 2026-08-29 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — LSK Kvinner W vs Bodø / Glimt W -> HOME @ None (rescheduled → 2026-09-01; actual LSK Kvinner W 1-1 Bodø / Glimt W [draw])
- 2026-08-29 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Viking vs Aalesund -> HOME @ 1.3 (rescheduled → 2026-08-30; actual Viking 2-1 Aalesund [home])
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 3-3 Go Ahead Eagles [draw])
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])
- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova FC 2-0 Londrina [home])

## Pending / Unmatched Result Examples

- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-26 `SKIPPED_VETO` `ml-meta avg_p>=55` — Crawley Town vs Barnet -> AWAY @ 1.66 (pending_or_unmatched_result); keys=['crawleyto']/['barnet']

## Ambiguous result examples

- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

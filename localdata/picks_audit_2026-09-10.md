# Edge Factory — Recent picks audit (2026-08-12 to 2026-09-10)

## Overall

- archived pick rows: 559
- archived pick dates: 30
- immutable morning-baseline rows: 476
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 83
- unsafe regular ledgers ignored: 22
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 526
- eligible prior picks: 551
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 7
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 3
- wins: 351
- hit rate: +66.7%
- priced picks: 495
- ROI: -2.9%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-10
- same-day rows excluded: 8

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 303 / 480 matches (63.1%)
- **Both Teams to Score (BTTS)**: occurred in 258 / 480 matches (53.8%)
- **Selected Team Over 1.5 Goals**: occurred in 322 / 480 matches (67.1%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 526
- **Total Hits**: 387
- **Overall Hit Rate**: 73.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=4, hits=3, hit_rate=75.0%
- `away_under_35`: recommended=34, hits=34, hit_rate=100.0%
- `home_over_05`: recommended=103, hits=87, hit_rate=84.5%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=18, hits=17, hit_rate=94.4%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=321, hits=209, hit_rate=65.1%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2397** | scored: 2397

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 521 | 521 | 328 | 63.0% | 47.3% | +15.6% | 0.256122 |
| `away_under_35` | 393 | 393 | 384 | 97.7% | 97.9% | -0.2% | 0.021446 |
| `match_over_45` | 370 | 370 | 106 | 28.6% | 23.9% | +4.7% | 0.204759 |
| `away_under_25` | 364 | 364 | 341 | 93.7% | 93.9% | -0.3% | 0.05956 |
| `home_over_05` | 333 | 333 | 295 | 88.6% | 85.1% | +3.5% | 0.101309 |
| `home_under_35` | 145 | 145 | 142 | 97.9% | 95.7% | +2.3% | 0.021038 |
| `home_under_25` | 105 | 105 | 97 | 92.4% | 91.5% | +0.9% | 0.070529 |
| `away_under_15` | 103 | 103 | 82 | 79.6% | 81.5% | -1.8% | 0.162673 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `home_under_15` | 9 | 9 | 9 | 100.0% | 81.3% | +18.7% | 0.034861 |
| `away_over_05` | 6 | 6 | 5 | 83.3% | 81.8% | +1.5% | 0.143461 |
| `match_over_35` | 5 | 5 | 2 | 40.0% | 32.6% | +7.4% | 0.244817 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2157 | 1650 | 76.5% | 72.3% | +4.2% | 0.124649 |
| model | 240 | 175 | 72.9% | 64.5% | +8.4% | 0.170805 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 100 | 19.0% | 21.0% | +2.0% |
| 0.2-0.3 | 240 | 25.0% | 31.2% | +6.2% |
| 0.3-0.4 | 61 | 34.5% | 41.0% | +6.5% |
| 0.4-0.5 | 357 | 45.5% | 62.2% | +16.7% |
| 0.5-0.6 | 133 | 53.3% | 67.7% | +14.3% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 509 | 84.2% | 86.1% | +1.8% |
| 0.9-1.0 | 992 | 95.7% | 95.9% | +0.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=479, MAE=1.560459 goals, bias=-0.190146 (realized − promised), promised avg 3.513737 vs realized 3.323591

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 479 | 28.2% | 35.9% | +7.7% | 0.21024 |
| BTTS-Yes | 479 | 41.7% | 53.9% | +12.2% | 0.263302 |
| Home Over 1.5 | 479 | 66.6% | 56.8% | -9.8% | 0.256631 |
| Over 2.5 | 479 | 69.6% | 63.0% | -6.5% | 0.233925 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 256 | 8.9% | 24.6% | +15.7% |
| 0.1-0.2 | 225 | 10.4% | 27.6% | +17.1% |
| 0.2-0.3 | 7 | 21.9% | 28.6% | +6.7% |
| 0.3-0.4 | 96 | 37.4% | 54.2% | +16.8% |
| 0.4-0.5 | 374 | 43.3% | 54.0% | +10.7% |
| 0.6-0.7 | 317 | 66.6% | 59.9% | -6.7% |
| 0.7-0.8 | 148 | 74.6% | 66.9% | -7.8% |
| 0.8-0.9 | 447 | 84.4% | 66.4% | -18.0% |
| 0.9-1.0 | 46 | 91.8% | 80.4% | -11.4% |

## By rule

- `2way-unanimous avg_p>=70`: settled=105, wins=81, hit_rate=0.771429, ROI=0.099785
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `ml-meta avg_p>=55`: settled=316, wins=194, hit_rate=0.613924, ROI=-0.07402
- `ml-meta avg_p>=60`: settled=28, wins=22, hit_rate=0.785714, ROI=0.098929
- `ml-meta avg_p>=65`: settled=6, wins=5, hit_rate=0.833333, ROI=0.158
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=2, wins=2, hit_rate=1.0, ROI=0.05
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=75, wins=51, hit_rate=0.68, ROI=0.080667
- `CERTIFIED_CLEAN`: settled=31, wins=19, hit_rate=0.612903, ROI=-0.09
- `SKIPPED_VETO`: settled=254, wins=169, hit_rate=0.665354, ROI=-0.05716
- `WATCHLIST_NO_ODDS`: settled=25, wins=17, hit_rate=0.68, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=16, wins=10, hit_rate=0.625, ROI=0.019286
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=116, wins=77, hit_rate=0.663793, ROI=-0.038621
- `WATCHLIST_UNKNOWN_CTX`: settled=9, wins=8, hit_rate=0.888889, ROI=0.087778

## By odds source

- `UNKNOWN`: settled=31, wins=18, hit_rate=0.580645, ROI=None
- `betexplorer_odds`: settled=154, wins=103, hit_rate=0.668831, ROI=-0.062857
- `bzzoiro_odds`: settled=45, wins=31, hit_rate=0.688889, ROI=0.054
- `forebet_best`: settled=56, wins=41, hit_rate=0.732143, ROI=0.085
- `scoutingstats_odds`: settled=238, wins=156, hit_rate=0.655462, ROI=-0.052395
- `zulubet`: settled=2, wins=2, hit_rate=1.0, ROI=0.255

## By odds match method

- `alias_fuzzy`: settled=25, wins=17, hit_rate=0.68, ROI=0.023913
- `betexplorer`: settled=154, wins=103, hit_rate=0.668831, ROI=-0.062857
- `exact`: settled=283, wins=187, hit_rate=0.660777, ROI=-0.035477
- `fallback`: settled=35, wins=26, hit_rate=0.742857, ROI=0.134857
- `none`: settled=29, wins=18, hit_rate=0.62069, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 154 | 103 | 0.668831 | 154 | -0.062857 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 45 | 31 | 0.688889 | 45 | 0.054 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 238 | 156 | 0.655462 | 238 | -0.052395 |
| Source fallback (`SOURCE_FALLBACK`) | 35 | 26 | 0.742857 | 35 | 0.134857 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 25 | 17 | 0.68 | 23 | 0.023913 |
| No usable price (`UNMATCHED`) | 29 | 18 | 0.62069 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 254 | 169 | 0.665354 | 250 | -0.05716 |
| **trusted evidence only** | 108 | 75 | 0.694444 | 108 | -0.049074 |
| **soft evidence only** | 146 | 94 | 0.643836 | 142 | -0.06331 |
| evidence: BETEXPLORER_RESCUE | 82 | 57 | 0.695122 | 82 | -0.079024 |
| evidence: BZZOIRO_PRIMARY | 26 | 18 | 0.692308 | 26 | 0.045385 |
| evidence: SCOUTINGSTATS_SOLE | 122 | 79 | 0.647541 | 122 | -0.065492 |
| evidence: SOURCE_FALLBACK | 11 | 7 | 0.636364 | 11 | -0.116364 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 9 | 0.031111 |
| evidence: UNMATCHED | 4 | 1 | 0.25 | 0 | None |
| odds band: <1.50 | 159 | 120 | 0.754717 | 159 | -0.030566 |
| odds band: 1.50-2.00 | 83 | 44 | 0.53012 | 83 | -0.118434 |
| odds band: 2.00-3.00 | 8 | 4 | 0.5 | 8 | 0.05 |
| odds band: unpriced | 4 | 1 | 0.25 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: context VETO in ['league', 'niche'] | 2 | 2 | 1.0 | 1 | 0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 4 | 4 | 1.0 | 4 | 0.12 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.595 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_h'] | 4 | 2 | 0.5 | 4 | -0.2675 |
| veto reason: context VETO in ['league'] | 10 | 6 | 0.6 | 9 | -0.007778 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 49 | 39 | 0.795918 | 49 | 0.032857 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.2 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 7 | 0.777778 | 9 | -0.032222 |
| veto reason: context VETO in ['team_a'] | 39 | 22 | 0.564103 | 37 | -0.056216 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.3025 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 14 | 13 | 0.928571 | 14 | 0.25 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.208 |
| veto reason: context VETO in ['team_h', 'team_a'] | 20 | 10 | 0.5 | 20 | -0.2125 |
| veto reason: context VETO in ['team_h'] | 61 | 35 | 0.57377 | 61 | -0.143443 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 42 | 27 | 0.642857 | 42 | 0.018333 |
| contrast CAUTION: BZZOIRO_PRIMARY | 16 | 11 | 0.6875 | 16 | 0.07 |
| contrast CAUTION: SOURCE_FALLBACK | 17 | 13 | 0.764706 | 17 | 0.244706 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 263 | 178 | 0.676806 | 234 | -0.010812 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 25 | 17 | 0.68 | 23 | 0.023913 | 25 | 1.5198 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 238 | 156 | 0.655462 | 238 | -0.052395 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-09: Pyramids vs El Gouna (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.39 -> 🟢 WON (Expected prob: 57.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.7% (Actual: 1 goals)

### 2026-09-09: Barcelona vs Feyenoord (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.11 -> 🟢 WON (Expected prob: 68.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.5% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.3% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.7% (Actual: 5 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 33.7% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 26.1% (Actual: 6 goals)

### 2026-09-09: Kairat Almaty vs Zhenys (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🟢 WON (Expected prob: 81.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 93.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.0% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.6% (Actual: 3 goals)

### 2026-09-09: Twente vs SC Telstar (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 69.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 86.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.6% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.3% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 34.7% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.9% (Actual: 1 goals)

### 2026-09-09: Levadia Tallinn vs FC Kuressaare (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.13 -> 🟢 WON (Expected prob: 65.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.1% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.1% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 31.7% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.9% (Actual: 4 goals)

### 2026-09-09: St Johnstone vs Celtic (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.48 -> 🟢 WON (Expected prob: 62.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.5% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 31.7% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.5% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 81.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 1 goals)

### 2026-09-09: Rangers vs St Mirren (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 56.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.7% (Actual: 1 goals)

### 2026-09-09: Paris Saint Germain vs Slovan Bratislava (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.04 -> 🟢 WON (Expected prob: 82.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.2% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 95.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Under 3.5 Goals**: expected 96.3% (Actual: 6 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.7% (Actual: 7 goals)

### 2026-09-09: Al Nassr vs Abha Club (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 79.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 34.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.8% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 31.1% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.7% (Actual: 3 goals)

### 2026-09-09: Moreirense vs Benfica (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.16 -> 🟢 WON (Expected prob: 77.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 85.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 14.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 92.9% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 90.4% (Actual: 4 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.4% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.7% (Actual: 4 goals)

### 2026-09-09: Boca Juniors vs Sao Paulo (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.95 -> 🟢 WON (Expected prob: 57.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.5% (Actual: 1 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 7 |
- 2026-08-15 `POSTPONED` `SKIPPED_VETO` — Slavia Sofia vs Levski Sofia (verified_disposition); excluded from win/loss/ROI
- 2026-08-16 `POSTPONED` `SKIPPED_VETO` — SC Braga vs Gil Vicente (verified_disposition); excluded from win/loss/ROI
- 2026-08-17 `POSTPONED` `SKIPPED_VETO` — Bucaramanga vs Deportivo Pasto (verified_disposition); excluded from win/loss/ROI
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

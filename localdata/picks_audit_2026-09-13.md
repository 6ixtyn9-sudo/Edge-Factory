# Edge Factory — Recent picks audit (2026-08-15 to 2026-09-13)

## Overall

- archived pick rows: 613
- archived pick dates: 30
- immutable morning-baseline rows: 530
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 83
- unsafe regular ledgers ignored: 25
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 552
- eligible prior picks: 578
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 7
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 365
- hit rate: +66.1%
- priced picks: 515
- ROI: -3.8%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-13
- same-day rows excluded: 35

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 324 / 506 matches (64.0%)
- **Both Teams to Score (BTTS)**: occurred in 277 / 506 matches (54.7%)
- **Selected Team Over 1.5 Goals**: occurred in 345 / 506 matches (68.2%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 552
- **Total Hits**: 395
- **Overall Hit Rate**: 71.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=8, hits=8, hit_rate=100.0%
- `away_under_35`: recommended=54, hits=51, hit_rate=94.4%
- `home_over_05`: recommended=79, hits=66, hit_rate=83.5%
- `home_under_25`: recommended=1, hits=1, hit_rate=100.0%
- `home_under_35`: recommended=16, hits=15, hit_rate=93.8%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=333, hits=212, hit_rate=63.7%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2488** | scored: 2488

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 544 | 544 | 346 | 63.6% | 47.5% | +16.1% | 0.258206 |
| `away_under_35` | 410 | 410 | 397 | 96.8% | 97.8% | -1.0% | 0.029339 |
| `match_over_45` | 393 | 393 | 110 | 28.0% | 23.9% | +4.1% | 0.203393 |
| `away_under_25` | 378 | 378 | 350 | 92.6% | 93.7% | -1.1% | 0.068945 |
| `home_over_05` | 306 | 306 | 271 | 88.6% | 84.6% | +3.9% | 0.102342 |
| `home_under_35` | 153 | 153 | 149 | 97.4% | 95.7% | +1.7% | 0.025578 |
| `home_under_25` | 110 | 110 | 102 | 92.7% | 91.6% | +1.1% | 0.067485 |
| `away_under_15` | 86 | 86 | 68 | 79.1% | 81.4% | -2.3% | 0.166398 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `home_under_15` | 17 | 17 | 13 | 76.5% | 81.5% | -5.1% | 0.185565 |
| `away_over_05` | 15 | 15 | 14 | 93.3% | 89.5% | +3.9% | 0.064387 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2221 | 1676 | 75.5% | 71.5% | +4.0% | 0.12939 |
| model | 267 | 193 | 72.3% | 64.7% | +7.5% | 0.181093 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 115 | 19.1% | 22.6% | +3.5% |
| 0.2-0.3 | 242 | 25.0% | 30.6% | +5.6% |
| 0.3-0.4 | 70 | 33.4% | 40.0% | +6.6% |
| 0.4-0.5 | 394 | 45.4% | 62.4% | +17.1% |
| 0.5-0.6 | 144 | 53.2% | 65.3% | +12.0% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 492 | 84.2% | 86.0% | +1.8% |
| 0.9-1.0 | 1026 | 95.6% | 95.0% | -0.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=505, MAE=1.548119 goals, bias=-0.157901 (realized − promised), promised avg 3.516317 vs realized 3.358416

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 505 | 28.7% | 37.0% | +8.4% | 0.218773 |
| BTTS-Yes | 505 | 41.7% | 54.9% | +13.2% | 0.265086 |
| Home Over 1.5 | 505 | 66.2% | 58.2% | -8.0% | 0.253387 |
| Over 2.5 | 505 | 69.7% | 64.0% | -5.7% | 0.232259 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 257 | 8.9% | 26.1% | +17.2% |
| 0.1-0.2 | 250 | 10.4% | 28.8% | +18.4% |
| 0.2-0.3 | 8 | 21.9% | 37.5% | +15.6% |
| 0.3-0.4 | 99 | 37.4% | 54.5% | +17.1% |
| 0.4-0.5 | 396 | 43.3% | 55.1% | +11.7% |
| 0.6-0.7 | 333 | 66.6% | 61.9% | -4.8% |
| 0.7-0.8 | 152 | 74.7% | 65.8% | -8.9% |
| 0.8-0.9 | 472 | 84.4% | 68.0% | -16.4% |
| 0.9-1.0 | 53 | 91.8% | 75.5% | -16.4% |

## By rule

- `2way-unanimous avg_p>=70`: settled=115, wins=85, hit_rate=0.73913, ROI=0.0388
- `2way-unanimous min_p>=60 avg_p>=65`: settled=5, wins=4, hit_rate=0.8, ROI=0.08
- `ml-meta avg_p>=55`: settled=331, wins=204, hit_rate=0.616314, ROI=-0.066677
- `ml-meta avg_p>=60`: settled=31, wins=24, hit_rate=0.774194, ROI=0.073548
- `ml-meta avg_p>=65`: settled=8, wins=6, hit_rate=0.75, ROI=0.017143
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.176
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=2, wins=2, hit_rate=1.0, ROI=0.05
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=75, wins=53, hit_rate=0.706667, ROI=0.118
- `CERTIFIED_CLEAN`: settled=27, wins=17, hit_rate=0.62963, ROI=-0.054074
- `SKIPPED_VETO`: settled=264, wins=169, hit_rate=0.640152, ROI=-0.092008
- `WATCHLIST_NO_ODDS`: settled=29, wins=20, hit_rate=0.689655, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=18, wins=12, hit_rate=0.666667, ROI=0.058667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=131, wins=87, hit_rate=0.664122, ROI=-0.036489
- `WATCHLIST_UNKNOWN_CTX`: settled=8, wins=7, hit_rate=0.875, ROI=0.06875

## By odds source

- `UNKNOWN`: settled=37, wins=23, hit_rate=0.621622, ROI=None
- `betexplorer_odds`: settled=160, wins=106, hit_rate=0.6625, ROI=-0.0675
- `bzzoiro_odds`: settled=26, wins=21, hit_rate=0.807692, ROI=0.272308
- `forebet_best`: settled=58, wins=42, hit_rate=0.724138, ROI=0.074655
- `scoutingstats_odds`: settled=271, wins=173, hit_rate=0.638376, ROI=-0.075277

## By odds match method

- `alias_fuzzy`: settled=26, wins=18, hit_rate=0.692308, ROI=0.022273
- `betexplorer`: settled=160, wins=106, hit_rate=0.6625, ROI=-0.0675
- `exact`: settled=297, wins=194, hit_rate=0.653199, ROI=-0.044848
- `fallback`: settled=36, wins=26, hit_rate=0.722222, ROI=0.106667
- `none`: settled=33, wins=21, hit_rate=0.636364, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 160 | 106 | 0.6625 | 160 | -0.0675 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 26 | 21 | 0.807692 | 26 | 0.272308 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 271 | 173 | 0.638376 | 271 | -0.075277 |
| Source fallback (`SOURCE_FALLBACK`) | 36 | 26 | 0.722222 | 36 | 0.106667 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 26 | 18 | 0.692308 | 22 | 0.022273 |
| No usable price (`UNMATCHED`) | 33 | 21 | 0.636364 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 264 | 169 | 0.640152 | 259 | -0.092008 |
| **trusted evidence only** | 100 | 69 | 0.69 | 100 | -0.0566 |
| **soft evidence only** | 164 | 100 | 0.609756 | 159 | -0.114277 |
| evidence: BETEXPLORER_RESCUE | 87 | 58 | 0.666667 | 87 | -0.115632 |
| evidence: BZZOIRO_PRIMARY | 13 | 11 | 0.846154 | 13 | 0.338462 |
| evidence: SCOUTINGSTATS_SOLE | 140 | 86 | 0.614286 | 140 | -0.111571 |
| evidence: SOURCE_FALLBACK | 12 | 7 | 0.583333 | 12 | -0.18 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.055714 |
| evidence: UNMATCHED | 4 | 1 | 0.25 | 0 | None |
| odds band: <1.50 | 159 | 118 | 0.742138 | 159 | -0.045849 |
| odds band: 1.50-2.00 | 92 | 45 | 0.48913 | 92 | -0.18413 |
| odds band: 2.00-3.00 | 8 | 4 | 0.5 | 8 | 0.05 |
| odds band: unpriced | 5 | 2 | 0.4 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: context VETO in ['league', 'niche'] | 2 | 2 | 1.0 | 1 | 0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 5 | 1.0 | 5 | 0.146 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 10 | 4 | 0.4 | 10 | -0.531 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.595 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['league', 'team_h'] | 6 | 3 | 0.5 | 6 | -0.265 |
| veto reason: context VETO in ['league'] | 10 | 6 | 0.6 | 9 | -0.007778 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.24 |
| veto reason: context VETO in ['odds_band'] | 46 | 34 | 0.73913 | 46 | -0.043261 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.2 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 2 | 1 | 0.5 | 2 | -0.375 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 8 | 7 | 0.875 | 8 | 0.12 |
| veto reason: context VETO in ['team_a'] | 42 | 21 | 0.5 | 40 | -0.16325 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.3025 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 12 | 11 | 0.916667 | 12 | 0.230833 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.17 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.208 |
| veto reason: context VETO in ['team_h', 'team_a'] | 19 | 9 | 0.473684 | 19 | -0.242632 |
| veto reason: context VETO in ['team_h'] | 65 | 38 | 0.584615 | 64 | -0.130781 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 45 | 30 | 0.666667 | 45 | 0.044667 |
| contrast CAUTION: BZZOIRO_PRIMARY | 13 | 10 | 0.769231 | 13 | 0.206154 |
| contrast CAUTION: SOURCE_FALLBACK | 17 | 13 | 0.764706 | 17 | 0.244706 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 255 | 174 | 0.682353 | 222 | 0.000541 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 26 | 18 | 0.692308 | 22 | 0.022273 | 26 | 1.538462 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 271 | 173 | 0.638376 | 271 | -0.075277 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-12: CSKA 1948 vs Dunav Ruse (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.34 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.8% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.6% (Actual: 3 goals)

### 2026-09-12: Stranraer FC vs Dumbarton FC (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.8% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.6% (Actual: 4 goals)

### 2026-09-12: Zenit vs Lokomotiv Moscow (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.37 -> 🟢 WON (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.7% (Actual: 3 goals)

### 2026-09-12: Edinburgh City vs Stirling Albion (Actual Score: **7-3**)
- **1X2 Pick**: Selected `HOME` @ 1.84 -> 🟢 WON (Expected prob: 57.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 10 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.5% (Actual: 7 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.2% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.9% (Actual: 10 goals)

### 2026-09-12: CS Dinamo București vs Concordia Chiajna (Actual Score: **2-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.15 -> 🟢 WON (Expected prob: 78.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 82.0% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 31.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 95.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 90.2% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 94.0% (Actual: 5 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.8% (Actual: 7 goals)

### 2026-09-12: Braintree Town vs Maidstone United (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.7 -> 🔴 LOST (Expected prob: 77.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 34.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 95.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 92.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.9% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.4% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.0% (Actual: 2 home goals)

### 2026-09-12: Chelsea vs Hull City (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🔴 LOST (Expected prob: 75.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.7% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.8% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.4% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.9% (Actual: 4 goals)

### 2026-09-12: Casa Pia AC vs Porto (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.25 -> 🟢 WON (Expected prob: 73.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 22.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 95.1% (Actual: 4 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.9% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.7% (Actual: 5 goals)

### 2026-09-12: Borussia Dortmund vs Paderborn (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 72.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.9% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 80.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.5% (Actual: 3 goals)

### 2026-09-12: Dunkerque vs Saint-Etienne (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.75 -> 🔴 LOST (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 35.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 93.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 94.3% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.6% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.3% (Actual: 2 home goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 84.4% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 3 goals)

### 2026-09-12: Arsenal Sarandi vs UAI Urquiza (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 70.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.6% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.6% (Actual: 2 goals)

### 2026-09-12: Glentoran Belfast vs Bangor FC (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🔴 LOST (Expected prob: 70.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.7% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.9% (Actual: 2 goals)

### 2026-09-12: Liverpool vs Fulham (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🔴 LOST (Expected prob: 68.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.8% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 86.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.4% (Actual: 0 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.7% (Actual: 0 goals)

### 2026-09-12: Sunderland vs Arsenal (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.48 -> 🟢 WON (Expected prob: 64.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.5% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 97.6% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.7% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.7% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 2 goals)

### 2026-09-12: Blackpool vs Bromley FC (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🔴 LOST (Expected prob: 62.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.8% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.4% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.8% (Actual: 4 goals)

### 2026-09-12: Walsall FC vs Rochdale (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🔴 LOST (Expected prob: 61.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.5% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.4% (Actual: 0 goals)

### 2026-09-12: Clyde FC vs Kelty Hearts (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.91 -> 🟢 WON (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.2% (Actual: 5 goals)

### 2026-09-12: Machida Zelvia vs Yokohama F. Marinos (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🔴 LOST (Expected prob: 60.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.3% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 2 goals)

### 2026-09-12: Freiburg vs Borussia M'gladbach (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🟢 WON (Expected prob: 59.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.3% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.1% (Actual: 5 goals)

### 2026-09-12: Harrogate Town vs Tamworth (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🟢 WON (Expected prob: 58.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.3% (Actual: 4 goals)

### 2026-09-12: Southampton vs Bristol City (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🟢 WON (Expected prob: 56.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.8% (Actual: 5 goals)

### 2026-09-12: Eastleigh vs Boreham Wood (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🔴 LOST (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 94.7% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.5% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.3% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.1% (Actual: 2 goals)

### 2026-09-12: Sparta Praha vs FK Jablonec (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 57.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.9% (Actual: 2 goals)

### 2026-09-12: Rapid Bucuresti vs FC Voluntari (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 56.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.4% (Actual: 3 goals)

### 2026-09-12: Chippa United vs Mamelodi Sundowns (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.28 -> 🔴 LOST (Expected prob: 55.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.6% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 91.7% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.1% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 81.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.8% (Actual: 2 goals)

### 2026-09-12: Kalju Nomme vs Trans Narva (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 72.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 51.2% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.8% (Actual: 2 goals)

### 2026-09-12: AS Trencin vs Dunajska Streda (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.61 -> 🟢 WON (Expected prob: 64.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.9% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 95.4% (Actual: 4 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.5% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 94.1% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 81.0% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.5% (Actual: 5 goals)

### 2026-09-12: CSKA-Sofia vs Arda Kardzhali (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 58.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.9% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.2% (Actual: 5 goals)

### 2026-09-12: Real Madrid vs Rayo Vallecano (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.11 -> 🟢 WON (Expected prob: 80.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 36.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.6% (Actual: 5 goals)

### 2026-09-12: Crusaders Belfast vs Limavady United (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 2.25 -> 🔴 LOST (Expected prob: 78.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 92.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.5% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.5% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.6% (Actual: 3 goals)

### 2026-09-12: Al Khaleej Club vs Al Nassr (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.18 -> 🔴 LOST (Expected prob: 77.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 81.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 36.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 91.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.0% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 95.6% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.9% (Actual: 2 goals)

### 2026-09-12: Twente vs ADO Den Haag (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 77.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 52.6% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.8% (Actual: 2 goals)

### 2026-09-12: Sheffield Wednesday vs Wigan Athletic (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 65.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.4% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.7% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.3% (Actual: 0 goals)

### 2026-09-12: Alemannia Aachen vs Jahn Regensburg (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🔴 LOST (Expected prob: 61.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.5% (Actual: 4 goals)

### 2026-09-12: Barnet vs Accrington Stanley (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 60.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.3% (Actual: 3 goals)

### 2026-09-12: Stockport County vs Leicester City (Actual Score: **3-4**)
- **1X2 Pick**: Selected `HOME` @ 1.83 -> 🔴 LOST (Expected prob: 60.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 94.1% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.1% (Actual: 7 goals)

### 2026-09-12: Forest Green vs Gateshead (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 59.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.8% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.7% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 4 goals)

### 2026-09-12: Boluspor vs Pendikspor (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.4 -> 🔴 LOST (Expected prob: 58.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 93.9% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.4% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.3% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 81.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.4% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.0% (Actual: 2 goals)

### 2026-09-12: Palmeiras vs Sao Paulo (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🟢 WON (Expected prob: 56.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 33.0% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.5% (Actual: 2 goals)

### 2026-09-12: IFK Goteborg vs Halmstad (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 55.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 31.9% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.6% (Actual: 3 goals)


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
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

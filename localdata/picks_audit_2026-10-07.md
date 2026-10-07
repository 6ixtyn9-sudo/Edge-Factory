# Edge Factory — Recent picks audit (2026-09-08 to 2026-10-07)

## Overall

- archived pick rows: 543
- archived pick dates: 30
- immutable morning-baseline rows: 543
- verified official late-slate additions: 2
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 28
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 521
- eligible prior picks: 540
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 6
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 3
- wins: 360
- hit rate: +69.1%
- priced picks: 458
- ROI: -1.8%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-07
- same-day rows excluded: 3

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 324 / 521 matches (62.2%)
- **Both Teams to Score (BTTS)**: occurred in 284 / 521 matches (54.5%)
- **Selected Team Over 1.5 Goals**: occurred in 343 / 521 matches (65.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 521
- **Total Hits**: 425
- **Overall Hit Rate**: 81.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=21, hits=19, hit_rate=90.5%
- `away_under_25`: recommended=25, hits=24, hit_rate=96.0%
- `away_under_35`: recommended=176, hits=169, hit_rate=96.0%
- `home_over_05`: recommended=1, hits=1, hit_rate=100.0%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=30, hits=29, hit_rate=96.7%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=209, hits=137, hit_rate=65.6%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%
- `match_over_45`: recommended=1, hits=1, hit_rate=100.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2039** | scored: 2039

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 512 | 512 | 317 | 61.9% | 44.9% | +17.0% | 0.263693 |
| `match_over_45` | 420 | 420 | 105 | 25.0% | 23.8% | +1.2% | 0.184426 |
| `away_under_35` | 364 | 364 | 352 | 96.7% | 95.5% | +1.2% | 0.032107 |
| `away_under_25` | 339 | 339 | 308 | 90.9% | 91.1% | -0.2% | 0.083002 |
| `home_under_35` | 129 | 129 | 125 | 96.9% | 93.6% | +3.3% | 0.033333 |
| `home_under_25` | 127 | 127 | 117 | 92.1% | 90.0% | +2.1% | 0.073334 |
| `away_over_05` | 44 | 44 | 39 | 88.6% | 86.0% | +2.7% | 0.099451 |
| `away_under_15` | 33 | 33 | 24 | 72.7% | 82.0% | -9.3% | 0.206955 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `home_over_05` | 16 | 16 | 15 | 93.8% | 81.9% | +11.8% | 0.076392 |
| `home_under_15` | 12 | 12 | 8 | 66.7% | 81.6% | -14.9% | 0.248468 |
| `match_over_15` | 7 | 7 | 6 | 85.7% | 82.9% | +2.8% | 0.120946 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1935 | 1361 | 70.3% | 65.3% | +5.0% | 0.139709 |
| model | 104 | 72 | 69.2% | 63.8% | +5.4% | 0.207174 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 93 | 19.2% | 18.3% | -0.9% |
| 0.2-0.3 | 281 | 24.0% | 24.6% | +0.5% |
| 0.3-0.4 | 79 | 33.2% | 48.1% | +14.9% |
| 0.4-0.5 | 459 | 44.3% | 60.6% | +16.3% |
| 0.5-0.6 | 53 | 51.6% | 66.0% | +14.4% |
| 0.8-0.9 | 302 | 86.4% | 87.4% | +1.0% |
| 0.9-1.0 | 772 | 94.1% | 94.8% | +0.7% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=520, MAE=1.577538 goals, bias=-0.277615 (realized − promised), promised avg 3.543 vs realized 3.265385

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 520 | 31.2% | 33.3% | +2.1% | 0.20709 |
| BTTS-Yes | 520 | 41.3% | 54.4% | +13.1% | 0.265696 |
| Home Over 1.5 | 520 | 63.7% | 54.2% | -9.5% | 0.239736 |
| Over 2.5 | 520 | 69.7% | 62.1% | -7.6% | 0.240457 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 231 | 8.6% | 22.5% | +13.9% |
| 0.1-0.2 | 292 | 10.4% | 21.6% | +11.2% |
| 0.2-0.3 | 7 | 26.7% | 71.4% | +44.7% |
| 0.3-0.4 | 101 | 37.3% | 53.5% | +16.1% |
| 0.4-0.5 | 408 | 42.7% | 54.4% | +11.7% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 350 | 67.0% | 59.4% | -7.6% |
| 0.7-0.8 | 150 | 74.2% | 68.0% | -6.2% |
| 0.8-0.9 | 490 | 84.6% | 64.9% | -19.7% |
| 0.9-1.0 | 50 | 92.4% | 74.0% | -18.4% |

## By rule

- `2way-unanimous avg_p>=60`: settled=130, wins=81, hit_rate=0.623077, ROI=-0.142371
- `2way-unanimous avg_p>=70`: settled=64, wins=48, hit_rate=0.75, ROI=-0.08625
- `ml-meta avg_p>=55`: settled=250, wins=165, hit_rate=0.66, ROI=0.003298
- `ml-meta avg_p>=60`: settled=53, wins=45, hit_rate=0.849057, ROI=0.162264
- `ml-meta avg_p>=65`: settled=14, wins=12, hit_rate=0.857143, ROI=0.041538
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=7, wins=7, hit_rate=1.0, ROI=0.066667

## By bucket

- `CAUTION`: settled=37, wins=20, hit_rate=0.540541, ROI=-0.176081
- `CERTIFIED_CLEAN`: settled=60, wins=46, hit_rate=0.766667, ROI=0.181167
- `SKIPPED_VETO`: settled=257, wins=180, hit_rate=0.700389, ROI=-0.048025
- `WATCHLIST_NO_ODDS`: settled=46, wins=30, hit_rate=0.652174, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=7, wins=5, hit_rate=0.714286, ROI=0.24
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=110, wins=76, hit_rate=0.690909, ROI=-0.015909
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=63, wins=44, hit_rate=0.698413, ROI=None
- `betexplorer_odds`: settled=153, wins=108, hit_rate=0.705882, ROI=-0.005098
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=52, wins=37, hit_rate=0.711538, ROI=0.039038
- `oddspapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.765
- `scoutingstats_odds`: settled=229, wins=151, hit_rate=0.659389, ROI=-0.061485
- `theoddsapi`: settled=8, wins=7, hit_rate=0.875, ROI=0.2125
- `zulubet`: settled=7, wins=5, hit_rate=0.714286, ROI=-0.032857

## By odds match method

- `alias_fuzzy`: settled=13, wins=10, hit_rate=0.769231, ROI=0.184444
- `betexplorer`: settled=142, wins=98, hit_rate=0.690141, ROI=-0.014155
- `exact`: settled=257, wins=176, hit_rate=0.684825, ROI=-0.031965
- `fallback`: settled=50, wins=35, hit_rate=0.7, ROI=0.0028
- `none`: settled=59, wins=41, hit_rate=0.694915, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 142 | 98 | 0.690141 | 142 | -0.014155 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 20 | 18 | 0.9 | 20 | 0.18475 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 229 | 151 | 0.659389 | 229 | -0.061485 |
| Source fallback (`SOURCE_FALLBACK`) | 50 | 35 | 0.7 | 50 | 0.0028 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 13 | 10 | 0.769231 | 9 | 0.184444 |
| No usable price (`UNMATCHED`) | 59 | 41 | 0.694915 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 257 | 180 | 0.700389 | 243 | -0.048025 |
| **trusted evidence only** | 94 | 69 | 0.734043 | 94 | -0.026064 |
| **soft evidence only** | 163 | 111 | 0.680982 | 149 | -0.061879 |
| evidence: BETEXPLORER_RESCUE | 80 | 55 | 0.6875 | 80 | -0.07675 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 9 | 9 | 1.0 | 9 | 0.185556 |
| evidence: SCOUTINGSTATS_SOLE | 119 | 75 | 0.630252 | 119 | -0.103613 |
| evidence: SOURCE_FALLBACK | 25 | 20 | 0.8 | 25 | 0.0964 |
| evidence: SUSPECT_ALIAS_FUZZY | 6 | 5 | 0.833333 | 5 | 0.14 |
| evidence: UNMATCHED | 13 | 11 | 0.846154 | 0 | None |
| odds band: <1.50 | 151 | 121 | 0.801325 | 151 | 0.000993 |
| odds band: 1.50-2.00 | 88 | 44 | 0.5 | 88 | -0.162727 |
| odds band: 2.00-3.00 | 4 | 3 | 0.75 | 4 | 0.625 |
| odds band: unpriced | 14 | 12 | 0.857143 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.4 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 0 | 0.0 | 2 | -1.0 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 12 | 10 | 0.833333 | 12 | 0.110833 |
| veto reason: context VETO in ['league'] | 23 | 16 | 0.695652 | 18 | -0.046111 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 54 | 41 | 0.759259 | 54 | -0.028704 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.39 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 14 | 11 | 0.785714 | 14 | -0.017857 |
| veto reason: context VETO in ['team_a'] | 41 | 26 | 0.634146 | 37 | -0.077297 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.137143 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 12 | 7 | 0.583333 | 12 | -0.085833 |
| veto reason: context VETO in ['team_h'] | 44 | 29 | 0.659091 | 40 | -0.03975 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 23 | 14 | 0.608696 | 23 | -0.073043 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 2 | 1 | 0.5 | 2 | -0.1175 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.327273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 277 | 197 | 0.711191 | 218 | 0.016766 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 13 | 10 | 0.769231 | 9 | 0.184444 | 13 | 1.512308 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 229 | 151 | 0.659389 | 229 | -0.061485 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 2 | 2 | 1.0 | 2 | 0.17 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-06: England vs Czech Republic (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.13 -> 🟢 WON (Expected prob: 78.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 86.4% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.3% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.3% (Actual: 3 goals)

### 2026-10-06: India vs Uruguay (Actual Score: **1-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.03 -> 🟢 WON (Expected prob: 80.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 86.5% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 29.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 94.6% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 95.3% (Actual: 6 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.3% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.9% (Actual: 1 home goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 86.0% (Actual: 6 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.4% (Actual: 7 goals)

### 2026-10-06: Albania vs San Marino (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.03 -> 🟢 WON (Expected prob: 78.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 80.8% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.2% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.2% (Actual: 3 goals)

### 2026-10-06: Croatia vs Spain (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.28 -> 🟢 WON (Expected prob: 73.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 28.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 84.2% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.4% (Actual: 3 goals)

### 2026-10-06: Angola vs Malawi (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 59.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.6% (Actual: 4 goals)

### 2026-10-06: Grenada vs Bonaire (Actual Score: **1-4**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🔴 LOST (Expected prob: 70.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 83.9% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.2% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.3% (Actual: 1 home goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 90.1% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.8% (Actual: 5 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])
- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova FC 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca W 4-1 Santos Laguna W [home])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ None (rescheduled → 2026-10-03; actual Tampa Bay Rowdies 1-2 Miami FC [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Brooklyn vs Rhode Island FC -> AWAY @ None (rescheduled → 2026-10-03; actual Brooklyn 1-3 Rhode Island [away])

## Pending / Unmatched Result Examples

- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-26 `SKIPPED_VETO` `ml-meta avg_p>=55` — Crawley Town vs Barnet -> AWAY @ 1.66 (pending_or_unmatched_result); keys=['crawleyto']/['barnet']
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Milevsko vs Spartak Sobeslav -> AWAY @ 1.57 (pending_or_unmatched_result); keys=['milevsko']/['spartakso']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Polanka nad Odrou vs Frydek-Mistek -> AWAY @ 1.48 (pending_or_unmatched_result); keys=['polankana']/['frydekmis']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Brommapojkarna W vs Malmö FF W -> AWAY @ 1.4 (pending_or_unmatched_result); keys=['brommapoj']/['malmoff', 'malmoffww']
- 2026-09-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — Plateau United vs Inter Lagos -> HOME @ 1.33 (pending_or_unmatched_result); keys=['plateauun']/['interlago']
- 2026-10-03 `CAUTION` `2way-unanimous avg_p>=60` — Sri Lanka vs Djibouti -> HOME @ 2.6 (pending_or_unmatched_result); keys=['srilanka']/['djibouti']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Rheindorf Altach II vs Hohenems -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['hohenems']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kufstein vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['kufstein']/['imst']

## Ambiguous result examples

- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

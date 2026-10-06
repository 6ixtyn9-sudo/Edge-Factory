# Edge Factory — Recent picks audit (2026-09-07 to 2026-10-06)

## Overall

- archived pick rows: 546
- archived pick dates: 30
- immutable morning-baseline rows: 548
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 520
- eligible prior picks: 540
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 3
- wins: 357
- hit rate: +68.7%
- priced picks: 458
- ROI: -2.1%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-06
- same-day rows excluded: 6

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 319 / 520 matches (61.3%)
- **Both Teams to Score (BTTS)**: occurred in 280 / 520 matches (53.8%)
- **Selected Team Over 1.5 Goals**: occurred in 339 / 520 matches (65.2%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 520
- **Total Hits**: 422
- **Overall Hit Rate**: 81.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=21, hits=19, hit_rate=90.5%
- `away_under_25`: recommended=25, hits=24, hit_rate=96.0%
- `away_under_35`: recommended=176, hits=170, hit_rate=96.6%
- `home_over_05`: recommended=1, hits=1, hit_rate=100.0%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=30, hits=29, hit_rate=96.7%
- `match_over_15`: recommended=3, hits=2, hit_rate=66.7%
- `match_over_25`: recommended=212, hits=137, hit_rate=64.6%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%
- `match_over_45`: recommended=1, hits=1, hit_rate=100.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2033** | scored: 2033

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 511 | 511 | 312 | 61.1% | 44.9% | +16.2% | 0.263144 |
| `match_over_45` | 419 | 419 | 104 | 24.8% | 23.8% | +1.0% | 0.18354 |
| `away_under_35` | 363 | 363 | 353 | 97.2% | 95.6% | +1.7% | 0.027124 |
| `away_under_25` | 339 | 339 | 310 | 91.4% | 91.2% | +0.3% | 0.078396 |
| `home_under_35` | 129 | 129 | 125 | 96.9% | 93.6% | +3.3% | 0.033316 |
| `home_under_25` | 127 | 127 | 117 | 92.1% | 90.0% | +2.1% | 0.073252 |
| `away_over_05` | 44 | 44 | 39 | 88.6% | 86.0% | +2.7% | 0.099451 |
| `away_under_15` | 34 | 34 | 25 | 73.5% | 81.9% | -8.4% | 0.202036 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `home_over_05` | 16 | 16 | 14 | 87.5% | 81.6% | +5.9% | 0.11797 |
| `home_under_15` | 12 | 12 | 8 | 66.7% | 81.6% | -14.9% | 0.248468 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |
| `match_over_15` | 3 | 3 | 2 | 66.7% | 81.7% | -15.0% | 0.246771 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1937 | 1359 | 70.2% | 65.3% | +4.8% | 0.138763 |
| model | 96 | 67 | 69.8% | 63.3% | +6.5% | 0.199826 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 92 | 19.2% | 18.5% | -0.7% |
| 0.2-0.3 | 283 | 24.0% | 24.0% | -0.0% |
| 0.3-0.4 | 77 | 33.3% | 49.4% | +16.1% |
| 0.4-0.5 | 460 | 44.3% | 59.8% | +15.5% |
| 0.5-0.6 | 51 | 51.7% | 64.7% | +13.1% |
| 0.8-0.9 | 295 | 86.4% | 87.1% | +0.7% |
| 0.9-1.0 | 775 | 94.2% | 95.2% | +1.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=519, MAE=1.586956 goals, bias=-0.300135 (realized − promised), promised avg 3.537129 vs realized 3.236994

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 519 | 31.1% | 32.8% | +1.7% | 0.207324 |
| BTTS-Yes | 519 | 41.4% | 53.8% | +12.4% | 0.26409 |
| Home Over 1.5 | 519 | 63.8% | 53.9% | -9.9% | 0.24284 |
| Over 2.5 | 519 | 69.6% | 61.3% | -8.4% | 0.244042 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 230 | 8.6% | 22.2% | +13.6% |
| 0.1-0.2 | 292 | 10.4% | 21.6% | +11.2% |
| 0.2-0.3 | 5 | 25.7% | 60.0% | +34.3% |
| 0.3-0.4 | 103 | 37.4% | 53.4% | +16.0% |
| 0.4-0.5 | 407 | 42.7% | 53.8% | +11.1% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 353 | 67.0% | 58.9% | -8.1% |
| 0.7-0.8 | 147 | 74.2% | 66.7% | -7.5% |
| 0.8-0.9 | 491 | 84.6% | 64.4% | -20.2% |
| 0.9-1.0 | 47 | 92.4% | 72.3% | -20.0% |

## By rule

- `2way-unanimous avg_p>=60`: settled=130, wins=81, hit_rate=0.623077, ROI=-0.142371
- `2way-unanimous avg_p>=70`: settled=63, wins=47, hit_rate=0.746032, ROI=-0.088723
- `ml-meta avg_p>=55`: settled=253, wins=166, hit_rate=0.656126, ROI=-6.2e-05
- `ml-meta avg_p>=60`: settled=50, wins=42, hit_rate=0.84, ROI=0.1632
- `ml-meta avg_p>=65`: settled=14, wins=12, hit_rate=0.857143, ROI=0.041538
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=7, wins=7, hit_rate=1.0, ROI=0.066667

## By bucket

- `CAUTION`: settled=38, wins=20, hit_rate=0.526316, ROI=-0.197763
- `CERTIFIED_CLEAN`: settled=60, wins=46, hit_rate=0.766667, ROI=0.181167
- `SKIPPED_VETO`: settled=255, wins=176, hit_rate=0.690196, ROI=-0.056777
- `WATCHLIST_NO_ODDS`: settled=46, wins=30, hit_rate=0.652174, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=8, wins=6, hit_rate=0.75, ROI=0.352
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=109, wins=76, hit_rate=0.697248, ROI=-0.006881
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=62, wins=43, hit_rate=0.693548, ROI=None
- `betexplorer_odds`: settled=155, wins=107, hit_rate=0.690323, ROI=-0.024581
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=53, wins=38, hit_rate=0.716981, ROI=0.053396
- `oddspapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.765
- `scoutingstats_odds`: settled=229, wins=152, hit_rate=0.663755, ROI=-0.055371
- `theoddsapi`: settled=5, wins=4, hit_rate=0.8, ROI=0.252
- `zulubet`: settled=7, wins=5, hit_rate=0.714286, ROI=-0.032857

## By odds match method

- `alias_fuzzy`: settled=14, wins=11, hit_rate=0.785714, ROI=0.246
- `betexplorer`: settled=145, wins=98, hit_rate=0.675862, ROI=-0.034552
- `exact`: settled=253, wins=173, hit_rate=0.683794, ROI=-0.028794
- `fallback`: settled=50, wins=35, hit_rate=0.7, ROI=0.0028
- `none`: settled=58, wins=40, hit_rate=0.689655, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 145 | 98 | 0.675862 | 145 | -0.034552 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 16 | 14 | 0.875 | 16 | 0.201562 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 229 | 152 | 0.663755 | 229 | -0.055371 |
| Source fallback (`SOURCE_FALLBACK`) | 50 | 35 | 0.7 | 50 | 0.0028 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 14 | 11 | 0.785714 | 10 | 0.246 |
| No usable price (`UNMATCHED`) | 58 | 40 | 0.689655 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 255 | 176 | 0.690196 | 242 | -0.056777 |
| **trusted evidence only** | 92 | 65 | 0.706522 | 92 | -0.053478 |
| **soft evidence only** | 163 | 111 | 0.680982 | 150 | -0.0588 |
| evidence: BETEXPLORER_RESCUE | 82 | 55 | 0.670732 | 82 | -0.099268 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 5 | 5 | 1.0 | 5 | 0.24 |
| evidence: SCOUTINGSTATS_SOLE | 120 | 76 | 0.633333 | 120 | -0.099417 |
| evidence: SOURCE_FALLBACK | 25 | 20 | 0.8 | 25 | 0.0964 |
| evidence: SUSPECT_ALIAS_FUZZY | 6 | 5 | 0.833333 | 5 | 0.14 |
| evidence: UNMATCHED | 12 | 10 | 0.833333 | 0 | None |
| odds band: <1.50 | 150 | 118 | 0.786667 | 150 | -0.0128 |
| odds band: 1.50-2.00 | 88 | 44 | 0.5 | 88 | -0.162727 |
| odds band: 2.00-3.00 | 4 | 3 | 0.75 | 4 | 0.625 |
| odds band: unpriced | 13 | 11 | 0.846154 | 0 | None |
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
| veto reason: context VETO in ['odds_band'] | 53 | 39 | 0.735849 | 53 | -0.049245 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.39 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 14 | 11 | 0.785714 | 14 | -0.017857 |
| veto reason: context VETO in ['team_a'] | 42 | 27 | 0.642857 | 38 | -0.064737 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.137143 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 4 | 2 | 0.5 | 4 | -0.335 |
| veto reason: context VETO in ['team_h', 'team_a'] | 11 | 6 | 0.545455 | 11 | -0.105455 |
| veto reason: context VETO in ['team_h'] | 43 | 28 | 0.651163 | 40 | -0.03975 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| contrast CAUTION: BETEXPLORER_RESCUE | 24 | 14 | 0.583333 | 24 | -0.111667 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 2 | 1 | 0.5 | 2 | -0.1175 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.327273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 275 | 192 | 0.698182 | 217 | 0.000853 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 14 | 11 | 0.785714 | 10 | 0.246 | 14 | 1.525714 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 229 | 152 | 0.663755 | 229 | -0.055371 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 2 | 2 | 1.0 | 2 | 0.17 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-05: Montenegro vs Armenia (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.58 -> 🔴 LOST (Expected prob: 65.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.6% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 82.0% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.6% (Actual: 0 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 84.7% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.2% (Actual: 0 goals)

### 2026-10-05: Moss vs Kongsvinger (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.75 -> 🟢 WON (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 81.2% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.2% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.8% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.5% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.0% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.5% (Actual: 2 goals)

### 2026-10-05: Cyprus vs Latvia (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.64 -> 🟢 WON (Expected prob: 57.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 3 goals)

### 2026-10-05: Italy vs Turkey (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.47 -> 🟢 WON (Expected prob: 64.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 81.9% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.6% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.9% (Actual: 4 goals)

### 2026-10-05: France vs Belgium (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 55.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.4% (Actual: 5 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
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

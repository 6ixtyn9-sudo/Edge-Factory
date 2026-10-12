# Edge Factory — Recent picks audit (2026-09-13 to 2026-10-12)

## Overall

- archived pick rows: 585
- archived pick dates: 30
- immutable morning-baseline rows: 582
- verified official late-slate additions: 5
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 561
- eligible prior picks: 578
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 6
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 1
- wins: 397
- hit rate: +70.8%
- priced picks: 478
- ROI: +2.8%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-12
- same-day rows excluded: 7

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 341 / 561 matches (60.8%)
- **Both Teams to Score (BTTS)**: occurred in 297 / 561 matches (52.9%)
- **Selected Team Over 1.5 Goals**: occurred in 371 / 561 matches (66.1%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 561
- **Total Hits**: 466
- **Overall Hit Rate**: 83.1%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=22, hits=19, hit_rate=86.4%
- `away_under_25`: recommended=25, hits=24, hit_rate=96.0%
- `away_under_35`: recommended=193, hits=188, hit_rate=97.4%
- `home_over_05`: recommended=18, hits=15, hit_rate=83.3%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=37, hits=36, hit_rate=97.3%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=225, hits=146, hit_rate=64.9%
- `match_over_45`: recommended=1, hits=1, hit_rate=100.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2178** | scored: 2178

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 557 | 557 | 337 | 60.5% | 44.8% | +15.7% | 0.261769 |
| `match_over_45` | 448 | 448 | 109 | 24.3% | 23.8% | +0.5% | 0.180642 |
| `away_under_35` | 395 | 395 | 387 | 98.0% | 95.2% | +2.8% | 0.021194 |
| `away_under_25` | 373 | 373 | 345 | 92.5% | 90.5% | +2.0% | 0.069833 |
| `home_under_35` | 146 | 146 | 142 | 97.3% | 94.3% | +3.0% | 0.029633 |
| `home_under_25` | 137 | 137 | 126 | 92.0% | 89.4% | +2.6% | 0.074882 |
| `away_over_05` | 48 | 48 | 42 | 87.5% | 82.8% | +4.7% | 0.111269 |
| `away_under_15` | 32 | 32 | 23 | 71.9% | 82.0% | -10.2% | 0.212233 |
| `home_over_05` | 30 | 30 | 26 | 86.7% | 88.2% | -1.5% | 0.12081 |
| `match_over_15` | 7 | 7 | 6 | 85.7% | 82.9% | +2.8% | 0.120946 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |
| `home_under_15` | 2 | 2 | 2 | 100.0% | 81.0% | +19.0% | 0.036266 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2098 | 1488 | 70.9% | 65.8% | +5.1% | 0.133718 |
| model | 80 | 59 | 73.8% | 63.6% | +10.1% | 0.158049 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 96 | 19.1% | 17.7% | -1.4% |
| 0.2-0.3 | 307 | 24.1% | 23.8% | -0.3% |
| 0.3-0.4 | 55 | 33.0% | 47.3% | +14.2% |
| 0.4-0.5 | 496 | 44.2% | 59.1% | +14.8% |
| 0.5-0.6 | 51 | 51.4% | 72.5% | +21.1% |
| 0.8-0.9 | 368 | 86.9% | 89.7% | +2.8% |
| 0.9-1.0 | 805 | 93.9% | 95.8% | +1.8% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=560, MAE=1.563036 goals, bias=-0.317429 (realized − promised), promised avg 3.531714 vs realized 3.214286

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 560 | 30.8% | 33.8% | +3.0% | 0.196367 |
| BTTS-Yes | 560 | 41.4% | 52.9% | +11.5% | 0.262648 |
| Home Over 1.5 | 560 | 64.1% | 52.7% | -11.4% | 0.235975 |
| Over 2.5 | 560 | 69.5% | 60.7% | -8.8% | 0.246096 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 235 | 8.6% | 21.7% | +13.1% |
| 0.1-0.2 | 327 | 10.4% | 19.9% | +9.4% |
| 0.2-0.3 | 7 | 26.9% | 71.4% | +44.5% |
| 0.3-0.4 | 100 | 37.3% | 50.0% | +12.7% |
| 0.4-0.5 | 448 | 42.6% | 53.1% | +10.6% |
| 0.5-0.6 | 3 | 52.2% | 33.3% | -18.9% |
| 0.6-0.7 | 382 | 66.8% | 58.6% | -8.2% |
| 0.7-0.8 | 162 | 74.3% | 65.4% | -8.9% |
| 0.8-0.9 | 527 | 84.5% | 65.1% | -19.5% |
| 0.9-1.0 | 49 | 92.4% | 75.5% | -16.9% |

## By rule

- `2way-unanimous avg_p>=60`: settled=130, wins=81, hit_rate=0.623077, ROI=-0.142371
- `2way-unanimous avg_p>=70`: settled=62, wins=51, hit_rate=0.822581, ROI=0.026444
- `ml-meta avg_p>=55`: settled=256, wins=176, hit_rate=0.6875, ROI=0.090039
- `ml-meta avg_p>=60`: settled=73, wins=55, hit_rate=0.753425, ROI=0.039714
- `ml-meta avg_p>=65`: settled=21, wins=17, hit_rate=0.809524, ROI=-0.010625
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=9, wins=9, hit_rate=1.0, ROI=0.08375
- `unanimous[bzzoiro+vitibet] avg_p>=70`: settled=5, wins=5, hit_rate=1.0, ROI=0.47
- `unanimous[statarea+vitibet] avg_p>=70`: settled=2, wins=1, hit_rate=0.5, ROI=0.195

## By bucket

- `CAUTION`: settled=41, wins=24, hit_rate=0.585366, ROI=-0.062437
- `CERTIFIED_CLEAN`: settled=73, wins=49, hit_rate=0.671233, ROI=0.048147
- `SKIPPED_VETO`: settled=279, wins=206, hit_rate=0.738351, ROI=0.035386
- `WATCHLIST_NO_ODDS`: settled=59, wins=39, hit_rate=0.661017, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=4, wins=4, hit_rate=1.0, ROI=0.675
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=101, wins=72, hit_rate=0.712871, ROI=0.023861
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=83, wins=57, hit_rate=0.686747, ROI=None
- `betexplorer_odds`: settled=145, wins=105, hit_rate=0.724138, ROI=0.008
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=46, wins=33, hit_rate=0.717391, ROI=0.044565
- `oddspapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.765
- `pinnapi_odds`: settled=15, wins=8, hit_rate=0.533333, ROI=0.050873
- `scoutingstats_odds`: settled=204, wins=142, hit_rate=0.696078, ROI=-0.000147
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=38, wins=31, hit_rate=0.815789, ROI=0.236053
- `zulubet`: settled=19, wins=11, hit_rate=0.578947, ROI=-0.190526

## By odds match method

- `alias_fuzzy`: settled=13, wins=10, hit_rate=0.769231, ROI=0.070909
- `betexplorer`: settled=117, wins=81, hit_rate=0.692308, ROI=-0.010342
- `exact`: settled=296, wins=215, hit_rate=0.726351, ROI=0.054963
- `fallback`: settled=54, wins=36, hit_rate=0.666667, ROI=-0.043519
- `none`: settled=81, wins=55, hit_rate=0.679012, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 117 | 81 | 0.692308 | 117 | -0.010342 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 83 | 65 | 0.783133 | 83 | 0.163965 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 204 | 142 | 0.696078 | 204 | -0.000147 |
| Source fallback (`SOURCE_FALLBACK`) | 54 | 36 | 0.666667 | 54 | -0.043519 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 13 | 10 | 0.769231 | 11 | 0.070909 |
| No usable price (`UNMATCHED`) | 81 | 55 | 0.679012 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 279 | 206 | 0.738351 | 257 | 0.035386 |
| **trusted evidence only** | 123 | 96 | 0.780488 | 123 | 0.080198 |
| **soft evidence only** | 156 | 110 | 0.705128 | 134 | -0.005746 |
| evidence: BETEXPLORER_RESCUE | 68 | 48 | 0.705882 | 68 | -0.054706 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 50 | 43 | 0.86 | 50 | 0.231286 |
| evidence: SCOUTINGSTATS_SOLE | 103 | 70 | 0.679612 | 103 | -0.023689 |
| evidence: SOURCE_FALLBACK | 22 | 18 | 0.818182 | 22 | 0.101818 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 6 | 0.666667 | 9 | -0.063333 |
| evidence: UNMATCHED | 22 | 16 | 0.727273 | 0 | None |
| odds band: <1.50 | 156 | 129 | 0.826923 | 156 | 0.032372 |
| odds band: 1.50-2.00 | 93 | 54 | 0.580645 | 93 | -0.035223 |
| odds band: 2.00-3.00 | 8 | 7 | 0.875 | 8 | 0.915 |
| odds band: unpriced | 22 | 16 | 0.727273 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['competition_type'] | 4 | 3 | 0.75 | 4 | 0.4475 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.39 |
| veto reason: context VETO in ['league', 'team_a'] | 4 | 1 | 0.25 | 4 | -0.585 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 4 | 3 | 0.75 | 4 | 0.015 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 0 | 0.0 | 2 | -1.0 |
| veto reason: context VETO in ['league', 'team_h'] | 9 | 8 | 0.888889 | 9 | 0.152222 |
| veto reason: context VETO in ['league'] | 28 | 20 | 0.714286 | 23 | -0.003478 |
| veto reason: context VETO in ['niche'] | 10 | 9 | 0.9 | 10 | 0.224 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.32 |
| veto reason: context VETO in ['odds_band'] | 51 | 40 | 0.784314 | 51 | -0.005098 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.193333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 2 | 1 | 0.5 | 2 | -0.335 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 14 | 11 | 0.785714 | 14 | -0.035 |
| veto reason: context VETO in ['team_a'] | 53 | 37 | 0.698113 | 46 | 0.058354 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.365 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.054286 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.04 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 12 | 0.705882 | 16 | 0.166875 |
| veto reason: context VETO in ['team_h'] | 47 | 34 | 0.723404 | 39 | 0.07 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 18 | 10 | 0.555556 | 18 | -0.128333 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 11 | 9 | 0.818182 | 11 | 0.395464 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.327273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 335 | 240 | 0.716418 | 254 | 0.057949 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 13 | 10 | 0.769231 | 11 | 0.070909 | 13 | 1.541538 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 204 | 142 | 0.696078 | 204 | -0.000147 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 9 | 5 | 0.555556 | 9 | -0.22 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-11: Sparta Praha vs Pardubice (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7407 -> 🟢 WON (Expected prob: 69.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.6% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.5% (Actual: 2 goals)

### 2026-10-11: Cherno More Varna vs Levski Sofia (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.6944 -> 🟢 WON (Expected prob: 62.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.2% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 81.6% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 2 goals)

### 2026-10-11: SC Freiburg vs FC Schalke 04 (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🟢 WON (Expected prob: 59.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.4% (Actual: 3 goals)

### 2026-10-11: Rennes vs Auxerre (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 58.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.6% (Actual: 5 goals)

### 2026-10-11: Gwangju FC vs Ulsan Hyundai FC (Actual Score: **4-3**)
- **1X2 Pick**: Selected `AWAY` @ 2.33 -> 🔴 LOST (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.8% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 4 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 88.2% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.8% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.5% (Actual: 7 goals)

### 2026-10-11: Lazio vs Monza (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🟢 WON (Expected prob: 55.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 63.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.6% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.6% (Actual: 4 goals)

### 2026-10-11: Almeria vs Leganes (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.63 -> 🟢 WON (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.4% (Actual: 3 goals)

### 2026-10-11: El Paso Locomotive vs Orange County SC (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7937 -> 🟢 WON (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.8% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 3 goals)

### 2026-10-11: Lusitania Lourosa vs Chaves (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 2.32 -> 🔴 LOST (Expected prob: 58.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.3% (Actual: 2 goals)

### 2026-10-11: UCSA vs Yarud Mariupol' (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.65 -> 🟢 WON (Expected prob: 64.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.6% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.7% (Actual: 3 goals)

### 2026-10-11: Stabaek vs Strommen (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3937 -> 🔴 LOST (Expected prob: 63.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.9% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.1% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.4% (Actual: 4 goals)

### 2026-10-11: St. Pauli II vs HSC Hannover (Actual Score: **3-4**)
- **1X2 Pick**: Selected `HOME` @ 1.76 -> 🔴 LOST (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 90.8% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.4% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.2% (Actual: 7 goals)

### 2026-10-11: Sandnes ULF vs Haugesund (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.82 -> 🔴 LOST (Expected prob: 61.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.5% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.2% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 81.3% (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.1% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 2 goals)

### 2026-10-11: Lorenskog vs Trygg-lade (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.565 -> 🔴 LOST (Expected prob: 60.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 90.1% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.9% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.1% (Actual: 6 goals)

### 2026-10-11: Flamengo vs Fluminense (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.51 -> 🟢 WON (Expected prob: 59.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.7% (Actual: 1 goals)

### 2026-10-11: Benfica vs Vitória SC (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 78.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.4% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.2% (Actual: 2 goals)

### 2026-10-11: River Plate vs Estudiantes de Rio Cuarto (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.19 -> 🟢 WON (Expected prob: 77.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 77.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.0% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.6% (Actual: 1 goals)

### 2026-10-11: BK Hacken vs Orgryte IS (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🟢 WON (Expected prob: 74.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.5% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 33.8% (Actual: 3 goals)

### 2026-10-11: Suwon Bluewings vs Ansan Greeners (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 74.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.7% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.2% (Actual: 5 goals)

### 2026-10-11: Vidar vs Brattvag (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 2.39 -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 32.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.2% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.7% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.5% (Actual: 4 goals)

### 2026-10-11: Tokyo Verdy vs Sanfrecce Hiroshima (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 2.05 -> 🟢 WON (Expected prob: 71.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 71.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.2% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.5% (Actual: 2 goals)

### 2026-10-11: Slovan Liberec vs Slovacko (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.9615 -> 🔴 LOST (Expected prob: 71.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.8% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.2% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.7% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.5% (Actual: 2 goals)

### 2026-10-11: Real Betis vs Osasuna (Actual Score: **5-2**)
- **1X2 Pick**: Selected `HOME` @ 1.54 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.3% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.8% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.4% (Actual: 7 goals)

### 2026-10-11: Farense vs Feirense (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 2.05 -> 🟢 WON (Expected prob: 64.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.7% (Actual: 3 goals)

### 2026-10-11: Southampton vs Portsmouth (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.62 -> 🟢 WON (Expected prob: 61.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 1 goals)

### 2026-10-11: Kawasaki Frontale vs Nagoya Grampus (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.84 -> 🔴 LOST (Expected prob: 60.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.8% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.6% (Actual: 3 goals)

### 2026-10-11: Motherwell vs Celtic (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.64 -> 🟢 WON (Expected prob: 59.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 81.3% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.1% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.0% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.9% (Actual: 2 goals)

### 2026-10-11: FC St. Pauli vs Karlsruher SC (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7143 -> 🟢 WON (Expected prob: 57.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.6% (Actual: 2 goals)

### 2026-10-11: Club America vs Monterrey (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.95 -> 🔴 LOST (Expected prob: 57.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.6% (Actual: 2 goals)

### 2026-10-11: Brondby vs Lyngby (Actual Score: **5-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 66.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.3% (Actual: 7 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.6% (Actual: 7 goals)

### 2026-10-11: Sao Paulo vs Vitoria (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.71 -> 🟢 WON (Expected prob: 62.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.8% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.8% (Actual: 3 goals)

### 2026-10-11: Vllaznia Shkodër vs Dinamo Tirana (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 2.0 -> 🔴 LOST (Expected prob: 62.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.2% (Actual: 1 goals)
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected 81.6% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.2% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.5% (Actual: 1 goals)

### 2026-10-11: Vikingur Reykjavik vs IA Akranes (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4608 -> 🔴 LOST (Expected prob: 61.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.2% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.1% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.2% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 4 goals)

### 2026-10-11: Grasshopper-Club vs BSC Young Boys (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.58 -> 🟢 WON (Expected prob: 61.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 80.8% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.1% (Actual: 2 goals)

### 2026-10-11: Palmeiras vs Corinthians (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 59.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.9% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.4% (Actual: 5 goals)

### 2026-10-11: Sliema Wanderers vs Gzira United (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 57.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.3% (Actual: 2 goals)

### 2026-10-11: PSS Sleman vs PSM Makassar (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 2.33 -> 🟢 WON (Expected prob: 55.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 63.9% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.6% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.2% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.1% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.8% (Actual: 3 goals)

### 2026-10-11: Kjelsas vs Rana FK (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 65.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.1% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.6% (Actual: 2 goals)

### 2026-10-11: AC Trento vs Folgore Caratese (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 55.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.6% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.4% (Actual: 1 goals)

### 2026-10-11: Csakvar vs Kecskemeti TE (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 83.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.3% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 3 goals)

### 2026-10-11: FK Partizan vs Novi Pazar (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 55.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 63.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.6% (Actual: 1 goals)

### 2026-10-11: Besiktas vs Kocaelispor (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 67.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.9% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.9% (Actual: 3 goals)

### 2026-10-11: Kongsvinger vs Ranheim (Actual Score: **6-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 55.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.0% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.2% (Actual: 6 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.5% (Actual: 2 away goals)
    - [🔴 MISS] **Home Team Under 3.5 Goals**: expected 91.2% (Actual: 6 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.8% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.7% (Actual: 8 goals)


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

- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-26 `SKIPPED_VETO` `ml-meta avg_p>=55` — Crawley Town vs Barnet -> AWAY @ 1.66 (pending_or_unmatched_result); keys=['crawleyto']/['barnet']
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Milevsko vs Spartak Sobeslav -> AWAY @ 1.57 (pending_or_unmatched_result); keys=['milevsko']/['spartakso']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Polanka nad Odrou vs Frydek-Mistek -> AWAY @ 1.48 (pending_or_unmatched_result); keys=['polankana']/['frydekmis']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Brommapojkarna W vs Malmö FF W -> AWAY @ 1.4 (pending_or_unmatched_result); keys=['brommapoj']/['malmoff', 'malmoffww']
- 2026-09-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — Plateau United vs Inter Lagos -> HOME @ 1.33 (pending_or_unmatched_result); keys=['plateauun']/['interlago']
- 2026-10-03 `CAUTION` `2way-unanimous avg_p>=60` — Sri Lanka vs Djibouti -> HOME @ 2.6 (pending_or_unmatched_result); keys=['srilanka']/['djibouti']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Rheindorf Altach II vs Hohenems -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['hohenems']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kufstein vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['kufstein']/['imst']
- 2026-10-11 `SKIPPED_VETO` `ml-meta avg_p>=60` — Atletico Nacional vs Deportivo Pasto -> HOME @ 2.1 (pending_or_unmatched_result); keys=['nacional']/['pasto']

## Ambiguous result examples

- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

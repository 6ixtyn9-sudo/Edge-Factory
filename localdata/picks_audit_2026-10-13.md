# Edge Factory — Recent picks audit (2026-09-14 to 2026-10-13)

## Overall

- archived pick rows: 568
- archived pick dates: 30
- immutable morning-baseline rows: 565
- verified official late-slate additions: 5
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 539
- eligible prior picks: 556
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 6
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 1
- wins: 383
- hit rate: +71.1%
- priced picks: 455
- ROI: +3.8%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-13
- same-day rows excluded: 12

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 333 / 539 matches (61.8%)
- **Both Teams to Score (BTTS)**: occurred in 283 / 539 matches (52.5%)
- **Selected Team Over 1.5 Goals**: occurred in 361 / 539 matches (67.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 539
- **Total Hits**: 446
- **Overall Hit Rate**: 82.7%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=15, settled=15, hit_rate=86.7%, priced_n=0, registry_processed=47, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `away_under_25`: recommended=25, settled=25, hit_rate=96.0%, priced_n=1, registry_processed=25, class=priced
- `away_under_35`: recommended=179, settled=179, hit_rate=97.2%, priced_n=1, registry_processed=251, class=priced
- `home_over_05`: recommended=18, settled=18, hit_rate=83.3%, priced_n=0, registry_processed=181, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_25`: recommended=33, settled=33, hit_rate=93.9%, priced_n=0, registry_processed=36, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_35`: recommended=38, settled=38, hit_rate=97.4%, priced_n=0, registry_processed=56, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=7, settled=7, hit_rate=85.7%, priced_n=6, registry_processed=54, class=priced
- `match_over_25`: recommended=219, settled=219, hit_rate=64.4%, priced_n=140, registry_processed=571, class=priced
- `match_over_35`: recommended=4, settled=4, hit_rate=100.0%, priced_n=2, registry_processed=29, class=priced
- `match_over_45`: recommended=1, settled=1, hit_rate=100.0%, priced_n=1, registry_processed=1, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2091** | scored: 2091

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 533 | 533 | 327 | 61.4% | 44.8% | +16.5% | 0.263174 |
| `match_over_45` | 431 | 431 | 104 | 24.1% | 23.9% | +0.2% | 0.179697 |
| `away_under_35` | 381 | 381 | 373 | 97.9% | 95.1% | +2.8% | 0.021961 |
| `away_under_25` | 358 | 358 | 330 | 92.2% | 90.4% | +1.8% | 0.072599 |
| `home_under_35` | 139 | 139 | 135 | 97.1% | 94.4% | +2.7% | 0.030799 |
| `home_under_25` | 128 | 128 | 119 | 93.0% | 89.2% | +3.8% | 0.066758 |
| `away_over_05` | 38 | 38 | 33 | 86.8% | 81.5% | +5.3% | 0.120367 |
| `away_under_15` | 32 | 32 | 23 | 71.9% | 82.0% | -10.2% | 0.212233 |
| `home_over_05` | 29 | 29 | 25 | 86.2% | 88.5% | -2.3% | 0.123664 |
| `match_over_35` | 10 | 10 | 9 | 90.0% | 42.4% | +47.6% | 0.338909 |
| `match_over_15` | 7 | 7 | 6 | 85.7% | 82.9% | +2.8% | 0.120946 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |
| `home_under_15` | 2 | 2 | 1 | 50.0% | 81.6% | -31.6% | 0.35753 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2013 | 1430 | 71.0% | 65.6% | +5.5% | 0.136095 |
| model | 78 | 57 | 73.1% | 64.4% | +8.6% | 0.148977 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 89 | 19.1% | 16.9% | -2.3% |
| 0.2-0.3 | 299 | 24.2% | 23.7% | -0.4% |
| 0.3-0.4 | 59 | 33.5% | 50.8% | +17.4% |
| 0.4-0.5 | 476 | 44.3% | 60.5% | +16.2% |
| 0.5-0.6 | 51 | 51.4% | 70.6% | +19.2% |
| 0.8-0.9 | 360 | 86.9% | 89.4% | +2.6% |
| 0.9-1.0 | 757 | 93.9% | 95.8% | +1.8% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=538, MAE=1.53987 goals, bias=-0.303327 (realized − promised), promised avg 3.537528 vs realized 3.234201

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 538 | 30.4% | 33.8% | +3.5% | 0.198473 |
| BTTS-Yes | 538 | 41.4% | 52.4% | +11.0% | 0.261445 |
| Home Over 1.5 | 538 | 64.6% | 53.7% | -10.9% | 0.230541 |
| Over 2.5 | 538 | 69.6% | 61.7% | -7.9% | 0.242683 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 226 | 8.6% | 22.6% | +14.0% |
| 0.1-0.2 | 313 | 10.4% | 19.5% | +9.1% |
| 0.2-0.3 | 7 | 26.9% | 71.4% | +44.5% |
| 0.3-0.4 | 96 | 37.3% | 49.0% | +11.6% |
| 0.4-0.5 | 432 | 42.5% | 52.8% | +10.3% |
| 0.5-0.6 | 2 | 53.3% | 50.0% | -3.3% |
| 0.6-0.7 | 361 | 66.8% | 60.1% | -6.7% |
| 0.7-0.8 | 161 | 74.4% | 65.2% | -9.1% |
| 0.8-0.9 | 505 | 84.6% | 65.7% | -18.8% |
| 0.9-1.0 | 49 | 92.1% | 77.6% | -14.6% |

## By rule

- `2way-unanimous avg_p>=60`: settled=130, wins=81, hit_rate=0.623077, ROI=-0.142371
- `2way-unanimous avg_p>=70`: settled=59, wins=48, hit_rate=0.813559, ROI=0.019535
- `ml-meta avg_p>=55`: settled=229, wins=158, hit_rate=0.689956, ROI=0.109933
- `ml-meta avg_p>=60`: settled=76, wins=58, hit_rate=0.763158, ROI=0.067465
- `ml-meta avg_p>=65`: settled=20, wins=16, hit_rate=0.8, ROI=-0.03
- `ml-meta avg_p>=70`: settled=2, wins=1, hit_rate=0.5, ROI=-0.47
- `ml-meta avg_p>=80`: settled=9, wins=9, hit_rate=1.0, ROI=0.08375
- `unanimous[betclan+vitibet] avg_p>=70`: settled=5, wins=5, hit_rate=1.0, ROI=0.403333
- `unanimous[bzzoiro+vitibet] avg_p>=70`: settled=5, wins=5, hit_rate=1.0, ROI=0.47
- `unanimous[statarea+vitibet] avg_p>=70`: settled=3, wins=1, hit_rate=0.333333, ROI=-0.203333
- `unanimous[vitibet+zulubet] avg_p>=70`: settled=1, wins=1, hit_rate=1.0, ROI=0.5263

## By bucket

- `CAUTION`: settled=40, wins=23, hit_rate=0.575, ROI=-0.080497
- `CERTIFIED_CLEAN`: settled=72, wins=49, hit_rate=0.680556, ROI=0.080971
- `SKIPPED_VETO`: settled=267, wins=199, hit_rate=0.745318, ROI=0.049846
- `WATCHLIST_NO_ODDS`: settled=59, wins=39, hit_rate=0.661017, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=3, wins=3, hit_rate=1.0, ROI=1.05
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=94, wins=67, hit_rate=0.712766, ROI=0.019468
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=84, wins=58, hit_rate=0.690476, ROI=None
- `betexplorer_odds`: settled=138, wins=100, hit_rate=0.724638, ROI=0.00471
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=44, wins=31, hit_rate=0.704545, ROI=0.038636
- `oddspapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.765
- `pinnapi_odds`: settled=19, wins=12, hit_rate=0.631579, ROI=0.223495
- `scoutingstats_odds`: settled=185, wins=129, hit_rate=0.697297, ROI=0.003351
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=39, wins=32, hit_rate=0.820513, ROI=0.244615
- `zulubet`: settled=19, wins=11, hit_rate=0.578947, ROI=-0.190526

## By odds match method

- `alias_fuzzy`: settled=12, wins=9, hit_rate=0.75, ROI=0.048
- `betexplorer`: settled=106, wins=73, hit_rate=0.688679, ROI=-0.01717
- `exact`: settled=286, wins=210, hit_rate=0.734266, ROI=0.07368
- `fallback`: settled=53, wins=35, hit_rate=0.660377, ROI=-0.045283
- `none`: settled=82, wins=56, hit_rate=0.682927, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 106 | 73 | 0.688679 | 106 | -0.01717 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 92 | 73 | 0.793478 | 92 | 0.19307 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 185 | 129 | 0.697297 | 185 | 0.003351 |
| Source fallback (`SOURCE_FALLBACK`) | 53 | 35 | 0.660377 | 53 | -0.045283 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 12 | 9 | 0.75 | 10 | 0.048 |
| No usable price (`UNMATCHED`) | 82 | 56 | 0.682927 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 267 | 199 | 0.745318 | 244 | 0.049846 |
| **trusted evidence only** | 123 | 97 | 0.788618 | 123 | 0.095548 |
| **soft evidence only** | 144 | 102 | 0.708333 | 121 | 0.003388 |
| evidence: BETEXPLORER_RESCUE | 61 | 43 | 0.704918 | 61 | -0.058852 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 57 | 49 | 0.859649 | 57 | 0.233726 |
| evidence: SCOUTINGSTATS_SOLE | 91 | 62 | 0.681319 | 91 | -0.013297 |
| evidence: SOURCE_FALLBACK | 21 | 17 | 0.809524 | 21 | 0.104286 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 6 | 0.666667 | 9 | -0.063333 |
| evidence: UNMATCHED | 23 | 17 | 0.73913 | 0 | None |
| odds band: <1.50 | 148 | 122 | 0.824324 | 148 | 0.03277 |
| odds band: 1.50-2.00 | 88 | 53 | 0.602273 | 88 | -8.6e-05 |
| odds band: 2.00-3.00 | 8 | 7 | 0.875 | 8 | 0.915 |
| odds band: unpriced | 23 | 17 | 0.73913 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['competition_type'] | 10 | 8 | 0.8 | 8 | 0.25 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.39 |
| veto reason: context VETO in ['league', 'team_a'] | 4 | 1 | 0.25 | 4 | -0.585 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 4 | 3 | 0.75 | 4 | 0.015 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_h'] | 7 | 6 | 0.857143 | 7 | 0.147143 |
| veto reason: context VETO in ['league'] | 27 | 19 | 0.703704 | 23 | -0.003478 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.19375 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.32 |
| veto reason: context VETO in ['odds_band'] | 48 | 37 | 0.770833 | 48 | -0.019375 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.37315 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.193333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 13 | 10 | 0.769231 | 13 | -0.063077 |
| veto reason: context VETO in ['team_a'] | 50 | 36 | 0.72 | 43 | 0.100607 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.365 |
| veto reason: context VETO in ['team_h', 'niche'] | 2 | 2 | 1.0 | 2 | 0.29 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.054286 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.44 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.32 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 12 | 0.705882 | 16 | 0.166875 |
| veto reason: context VETO in ['team_h'] | 45 | 33 | 0.733333 | 37 | 0.083243 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 17 | 9 | 0.529412 | 17 | -0.174706 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 11 | 9 | 0.818182 | 11 | 0.395464 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.327273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 333 | 240 | 0.720721 | 251 | 0.072559 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 12 | 9 | 0.75 | 10 | 0.048 | 12 | 1.561667 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 185 | 129 | 0.697297 | 185 | 0.003351 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 9 | 5 | 0.555556 | 9 | -0.22 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-12: Livyi Bereh vs Zorya Luhansk (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 2.75 -> 🟢 WON (Expected prob: 61.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 31.0% (Actual: 4 goals)

### 2026-10-12: Antigua GFC vs Coban Imperial (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6452 -> 🟢 WON (Expected prob: 58.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.8% (Actual: 3 goals)

### 2026-10-12: Always Ready vs Independiente Petrolero (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 83.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 83.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 93.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.2% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 37.5% (Actual: 2 goals)

### 2026-10-12: Pyunik Yerevan vs BKMA (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.21 -> 🟢 WON (Expected prob: 78.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.2% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.6% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 48.9% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 30.9% (Actual: 5 goals)

### 2026-10-12: AEK Larnaca FC vs Omonia Aradippou (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.43 -> 🟢 WON (Expected prob: 75.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.9% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 51.3% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 32.8% (Actual: 1 goals)

### 2026-10-12: Forge vs York United (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.0% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 47.7% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.8% (Actual: 5 goals)

### 2026-10-12: PAOK vs Kalamata (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.21 -> 🔴 LOST (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.3% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 47.6% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 93.1% (Actual: 3 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.7% (Actual: 4 goals)

### 2026-10-12: Club Universidad de Chile vs Nublense (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.6% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 47.0% (Actual: 6 goals)

### 2026-10-12: St. Louis City vs Los Angeles Galaxy (Actual Score: **6-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5263 -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.1% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 6 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.7% (Actual: 8 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 39.1% (Actual: 8 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.4% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.4% (Actual: 8 goals)

### 2026-10-12: Hapoel Kfar Saba vs FC Ashdod (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.46 -> 🟢 WON (Expected prob: 61.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.1% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 38.7% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.0% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.2% (Actual: 2 home goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 82.4% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.1% (Actual: 6 goals)

### 2026-10-12: Hapoel Rishon LeZion vs Maccabi Kabilio Jaffa (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5618 -> 🟢 WON (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.4% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.6% (Actual: 3 goals)

### 2026-10-12: Ludogorets Razgrad vs Arda Kardzhali (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 60.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 33.9% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.9% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.8% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.4% (Actual: 5 goals)

### 2026-10-12: IF Elfsborg vs Halmstad (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 65.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.5% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 38.7% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.7% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.3% (Actual: 4 goals)


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

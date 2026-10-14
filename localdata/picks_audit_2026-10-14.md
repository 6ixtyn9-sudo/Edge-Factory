# Edge Factory — Recent picks audit (2026-09-15 to 2026-10-14)

## Overall

- archived pick rows: 560
- archived pick dates: 30
- immutable morning-baseline rows: 557
- verified official late-slate additions: 5
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 540
- eligible prior picks: 556
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 5
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 1
- wins: 382
- hit rate: +70.7%
- priced picks: 454
- ROI: +4.0%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-14
- same-day rows excluded: 4

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 334 / 540 matches (61.9%)
- **Both Teams to Score (BTTS)**: occurred in 283 / 540 matches (52.4%)
- **Selected Team Over 1.5 Goals**: occurred in 361 / 540 matches (66.9%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 540
- **Total Hits**: 447
- **Overall Hit Rate**: 82.8%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=12, settled=12, hit_rate=91.7%, priced_n=0, registry_processed=47, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `away_under_25`: recommended=24, settled=24, hit_rate=100.0%, priced_n=1, registry_processed=25, class=priced
- `away_under_35`: recommended=178, settled=178, hit_rate=97.2%, priced_n=1, registry_processed=252, class=priced
- `home_over_05`: recommended=18, settled=18, hit_rate=83.3%, priced_n=0, registry_processed=181, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_25`: recommended=33, settled=33, hit_rate=93.9%, priced_n=0, registry_processed=36, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_35`: recommended=38, settled=38, hit_rate=97.4%, priced_n=0, registry_processed=56, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=13, settled=13, hit_rate=92.3%, priced_n=11, registry_processed=60, class=priced
- `match_over_25`: recommended=214, settled=214, hit_rate=63.6%, priced_n=135, registry_processed=571, class=priced
- `match_over_35`: recommended=9, settled=9, hit_rate=77.8%, priced_n=7, registry_processed=34, class=priced
- `match_over_45`: recommended=1, settled=1, hit_rate=100.0%, priced_n=1, registry_processed=1, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2090** | scored: 2090

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 530 | 530 | 324 | 61.1% | 44.8% | +16.3% | 0.263278 |
| `match_over_45` | 428 | 428 | 104 | 24.3% | 23.9% | +0.4% | 0.181196 |
| `away_under_35` | 378 | 378 | 370 | 97.9% | 95.1% | +2.7% | 0.022037 |
| `away_under_25` | 354 | 354 | 326 | 92.1% | 90.3% | +1.8% | 0.073251 |
| `home_under_35` | 139 | 139 | 135 | 97.1% | 94.5% | +2.7% | 0.030725 |
| `home_under_25` | 127 | 127 | 118 | 92.9% | 89.1% | +3.8% | 0.06737 |
| `away_over_05` | 35 | 35 | 31 | 88.6% | 80.8% | +7.7% | 0.106568 |
| `away_under_15` | 32 | 32 | 23 | 71.9% | 82.0% | -10.2% | 0.212233 |
| `home_over_05` | 27 | 27 | 23 | 85.2% | 88.9% | -3.8% | 0.130426 |
| `match_over_35` | 20 | 20 | 16 | 80.0% | 45.2% | +34.8% | 0.302922 |
| `match_over_15` | 15 | 15 | 13 | 86.7% | 85.2% | +1.5% | 0.113233 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |
| `home_under_15` | 2 | 2 | 1 | 50.0% | 81.6% | -31.6% | 0.35753 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2008 | 1425 | 71.0% | 65.5% | +5.5% | 0.137158 |
| model | 82 | 61 | 74.4% | 65.1% | +9.3% | 0.146953 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 90 | 19.1% | 17.8% | -1.4% |
| 0.2-0.3 | 297 | 24.2% | 24.2% | +0.1% |
| 0.3-0.4 | 59 | 33.7% | 50.8% | +17.2% |
| 0.4-0.5 | 477 | 44.3% | 60.4% | +16.1% |
| 0.5-0.6 | 55 | 51.5% | 69.1% | +17.6% |
| 0.8-0.9 | 364 | 86.9% | 89.3% | +2.4% |
| 0.9-1.0 | 748 | 94.0% | 95.9% | +1.9% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=538, MAE=1.540539 goals, bias=-0.292844 (realized − promised), promised avg 3.538197 vs realized 3.245353

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 538 | 30.2% | 34.0% | +3.8% | 0.198569 |
| BTTS-Yes | 538 | 41.3% | 52.2% | +10.9% | 0.261253 |
| Home Over 1.5 | 538 | 64.7% | 53.5% | -11.2% | 0.233206 |
| Over 2.5 | 538 | 69.6% | 61.7% | -7.9% | 0.24263 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 224 | 8.6% | 22.3% | +13.7% |
| 0.1-0.2 | 315 | 10.4% | 20.0% | +9.6% |
| 0.2-0.3 | 7 | 26.9% | 71.4% | +44.5% |
| 0.3-0.4 | 96 | 37.3% | 47.9% | +10.6% |
| 0.4-0.5 | 432 | 42.5% | 52.8% | +10.3% |
| 0.5-0.6 | 2 | 53.3% | 50.0% | -3.3% |
| 0.6-0.7 | 360 | 66.8% | 60.0% | -6.8% |
| 0.7-0.8 | 162 | 74.3% | 65.4% | -8.9% |
| 0.8-0.9 | 506 | 84.6% | 65.6% | -19.0% |
| 0.9-1.0 | 48 | 92.1% | 77.1% | -15.1% |

## By rule

- `2way-unanimous avg_p>=60`: settled=130, wins=81, hit_rate=0.623077, ROI=-0.142371
- `2way-unanimous avg_p>=70`: settled=57, wins=46, hit_rate=0.807018, ROI=0.010244
- `ml-meta avg_p>=55`: settled=227, wins=157, hit_rate=0.69163, ROI=0.113444
- `ml-meta avg_p>=60`: settled=80, wins=59, hit_rate=0.7375, ROI=0.076892
- `ml-meta avg_p>=65`: settled=20, wins=16, hit_rate=0.8, ROI=-0.03
- `ml-meta avg_p>=70`: settled=2, wins=1, hit_rate=0.5, ROI=-0.47
- `ml-meta avg_p>=80`: settled=9, wins=9, hit_rate=1.0, ROI=0.08375
- `unanimous[betclan+vitibet] avg_p>=70`: settled=6, wins=6, hit_rate=1.0, ROI=0.403333
- `unanimous[bzzoiro+vitibet] avg_p>=70`: settled=5, wins=5, hit_rate=1.0, ROI=0.47
- `unanimous[statarea+vitibet] avg_p>=70`: settled=3, wins=1, hit_rate=0.333333, ROI=-0.203333
- `unanimous[vitibet+zulubet] avg_p>=70`: settled=1, wins=1, hit_rate=1.0, ROI=0.5263

## By bucket

- `CAUTION`: settled=40, wins=23, hit_rate=0.575, ROI=-0.080497
- `CERTIFIED_CLEAN`: settled=72, wins=49, hit_rate=0.680556, ROI=0.102637
- `SKIPPED_VETO`: settled=271, wins=200, hit_rate=0.738007, ROI=0.04562
- `WATCHLIST_NO_ODDS`: settled=59, wins=39, hit_rate=0.661017, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=3, wins=3, hit_rate=1.0, ROI=1.05
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=91, wins=65, hit_rate=0.714286, ROI=0.024066
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=86, wins=59, hit_rate=0.686047, ROI=None
- `betexplorer_odds`: settled=143, wins=103, hit_rate=0.72028, ROI=0.001189
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=44, wins=31, hit_rate=0.704545, ROI=0.038636
- `oddspapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.765
- `pinnapi_odds`: settled=19, wins=12, hit_rate=0.631579, ROI=0.223495
- `scoutingstats_odds`: settled=177, wins=122, hit_rate=0.689266, ROI=-0.001412
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=39, wins=32, hit_rate=0.820513, ROI=0.244615
- `zulubet`: settled=21, wins=13, hit_rate=0.619048, ROI=-0.061429

## By odds match method

- `alias_fuzzy`: settled=14, wins=11, hit_rate=0.785714, ROI=0.089091
- `betexplorer`: settled=104, wins=71, hit_rate=0.682692, ROI=-0.027212
- `exact`: settled=285, wins=208, hit_rate=0.729825, ROI=0.072745
- `fallback`: settled=54, wins=36, hit_rate=0.666667, ROI=-0.010556
- `none`: settled=83, wins=56, hit_rate=0.674699, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 104 | 71 | 0.682692 | 104 | -0.027212 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 99 | 78 | 0.787879 | 99 | 0.184772 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 177 | 122 | 0.689266 | 177 | -0.001412 |
| Source fallback (`SOURCE_FALLBACK`) | 54 | 36 | 0.666667 | 54 | -0.010556 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 14 | 11 | 0.785714 | 11 | 0.089091 |
| No usable price (`UNMATCHED`) | 83 | 56 | 0.674699 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 271 | 200 | 0.738007 | 246 | 0.04562 |
| **trusted evidence only** | 129 | 101 | 0.782946 | 129 | 0.089476 |
| **soft evidence only** | 142 | 99 | 0.697183 | 117 | -0.002735 |
| evidence: BETEXPLORER_RESCUE | 61 | 43 | 0.704918 | 61 | -0.058852 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 63 | 53 | 0.84127 | 63 | 0.208133 |
| evidence: SCOUTINGSTATS_SOLE | 86 | 57 | 0.662791 | 86 | -0.028372 |
| evidence: SOURCE_FALLBACK | 21 | 17 | 0.809524 | 21 | 0.104286 |
| evidence: SUSPECT_ALIAS_FUZZY | 11 | 8 | 0.727273 | 10 | -0.007 |
| evidence: UNMATCHED | 24 | 17 | 0.708333 | 0 | None |
| odds band: <1.50 | 148 | 119 | 0.804054 | 148 | 0.007635 |
| odds band: 1.50-2.00 | 90 | 56 | 0.622222 | 90 | 0.030804 |
| odds band: 2.00-3.00 | 8 | 7 | 0.875 | 8 | 0.915 |
| odds band: unpriced | 25 | 18 | 0.72 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['competition_type'] | 11 | 9 | 0.818182 | 8 | 0.25 |
| veto reason: context VETO in ['league', 'niche'] | 2 | 1 | 0.5 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 4 | 1 | 0.25 | 4 | -0.585 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 4 | 3 | 0.75 | 4 | 0.015 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_h'] | 8 | 7 | 0.875 | 8 | 0.165 |
| veto reason: context VETO in ['league'] | 27 | 19 | 0.703704 | 23 | -0.003478 |
| veto reason: context VETO in ['niche'] | 11 | 8 | 0.727273 | 11 | 0.01 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.32 |
| veto reason: context VETO in ['odds_band'] | 48 | 37 | 0.770833 | 48 | -0.019375 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.37315 |
| veto reason: context VETO in ['team_a', 'niche'] | 4 | 3 | 0.75 | 4 | 0.3175 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 13 | 10 | 0.769231 | 13 | -0.063077 |
| veto reason: context VETO in ['team_a'] | 49 | 35 | 0.714286 | 42 | 0.093002 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.365 |
| veto reason: context VETO in ['team_h', 'niche'] | 2 | 2 | 1.0 | 2 | 0.29 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.054286 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.44 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.32 |
| veto reason: context VETO in ['team_h', 'team_a'] | 18 | 13 | 0.722222 | 17 | 0.186471 |
| veto reason: context VETO in ['team_h'] | 44 | 31 | 0.704545 | 35 | 0.078286 |
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
| No price quarantine (`NONE`) | 339 | 243 | 0.716814 | 256 | 0.069267 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 14 | 11 | 0.785714 | 11 | 0.089091 | 14 | 1.57825 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 177 | 122 | 0.689266 | 177 | -0.001412 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 10 | 6 | 0.6 | 10 | -0.015 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-13: Germany W vs Japan W (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.74 -> 🟢 WON (Expected prob: 71.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 51.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.5% (Actual: 3 goals)

### 2026-10-13: Eichstätt vs Vilzing (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 2.83 -> 🟢 WON (Expected prob: 61.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 87.3% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 41.7% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.2% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.8% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.0% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.9% (Actual: 5 goals)

### 2026-10-13: Viking vs Bayern München (Actual Score: **3-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.11 -> 🔴 LOST (Expected prob: 80.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 81.4% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.0% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.0% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 37.5% (Actual: 6 goals)

### 2026-10-13: Inter vs Club Brugge (Actual Score: **3-4**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🔴 LOST (Expected prob: 73.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.4% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.5% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 55.4% (Actual: 7 goals)

### 2026-10-13: Ebbsfleet United vs AFC Totton (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.4% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 56.6% (Actual: 5 goals)

### 2026-10-13: Arsenal vs Lille (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 91.8% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 54.4% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.9% (Actual: 3 goals)

### 2026-10-13: Galatasaray vs Barcelona (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.29 -> 🟢 WON (Expected prob: 70.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.4% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 87.2% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 52.5% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.3% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.2% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.4% (Actual: 5 goals)

### 2026-10-13: Wolves vs Bolton (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.43 -> 🔴 LOST (Expected prob: 68.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 91.7% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.3% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 48.2% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 92.4% (Actual: 3 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.7% (Actual: 4 goals)

### 2026-10-13: Birmingham vs Preston (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.59 -> 🟢 WON (Expected prob: 63.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 40.2% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 86.7% (Actual: 4 goals)

### 2026-10-13: Cardiff vs Watford (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.69 -> 🟢 WON (Expected prob: 62.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 85.7% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 39.2% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.5% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.0% (Actual: 6 goals)

### 2026-10-13: USM Alger vs JS Saoura (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 63.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 40.2% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 85.6% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.4% (Actual: 1 goals)

### 2026-10-13: Hansa Rostock vs SV Meppen (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 61.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.1% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.1% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 2 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

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

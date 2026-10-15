# Edge Factory — Recent picks audit (2026-09-17 to 2026-10-16)

## Overall

- archived pick rows: 557
- archived pick dates: 30
- immutable morning-baseline rows: 554
- verified official late-slate additions: 5
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 26
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 543
- eligible prior picks: 553
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 5
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 0
- wins: 383
- hit rate: +70.5%
- priced picks: 455
- ROI: +4.6%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-16
- same-day rows excluded: 4

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 335 / 543 matches (61.7%)
- **Both Teams to Score (BTTS)**: occurred in 289 / 543 matches (53.2%)
- **Selected Team Over 1.5 Goals**: occurred in 362 / 543 matches (66.7%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 541
- **Total Hits**: 446
- **Overall Hit Rate**: 82.4%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=12, settled=12, hit_rate=91.7%, priced_n=0, registry_processed=47, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `away_under_15`: recommended=1, settled=1, hit_rate=100.0%, priced_n=1, registry_processed=1, class=priced
- `away_under_25`: recommended=23, settled=23, hit_rate=95.7%, priced_n=2, registry_processed=26, class=priced
- `away_under_35`: recommended=170, settled=170, hit_rate=97.6%, priced_n=1, registry_processed=255, class=priced
- `btts_no`: recommended=2, settled=2, hit_rate=50.0%, priced_n=2, registry_processed=2, class=priced
- `btts_yes`: recommended=1, settled=1, hit_rate=100.0%, priced_n=1, registry_processed=14, class=priced
- `home_over_05`: recommended=19, settled=19, hit_rate=84.2%, priced_n=1, registry_processed=182, class=priced
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced
- `home_under_25`: recommended=29, settled=29, hit_rate=93.1%, priced_n=0, registry_processed=36, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_35`: recommended=38, settled=38, hit_rate=97.4%, priced_n=0, registry_processed=57, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=15, settled=15, hit_rate=93.3%, priced_n=13, registry_processed=62, class=priced
- `match_over_25`: recommended=218, settled=218, hit_rate=63.8%, priced_n=142, registry_processed=589, class=priced
- `match_over_35`: recommended=10, settled=10, hit_rate=80.0%, priced_n=8, registry_processed=35, class=priced
- `match_over_45`: recommended=1, settled=1, hit_rate=100.0%, priced_n=1, registry_processed=1, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2114** | scored: 2114

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 530 | 530 | 324 | 61.1% | 45.6% | +15.5% | 0.259981 |
| `match_over_45` | 415 | 415 | 95 | 22.9% | 23.9% | -1.0% | 0.175049 |
| `away_under_35` | 364 | 364 | 357 | 98.1% | 95.3% | +2.8% | 0.020235 |
| `away_under_25` | 341 | 341 | 314 | 92.1% | 90.2% | +1.9% | 0.073212 |
| `home_under_35` | 137 | 137 | 133 | 97.1% | 94.6% | +2.5% | 0.030994 |
| `home_under_25` | 121 | 121 | 112 | 92.6% | 89.0% | +3.5% | 0.070201 |
| `match_over_35` | 44 | 44 | 27 | 61.4% | 44.1% | +17.3% | 0.285412 |
| `away_under_15` | 35 | 35 | 25 | 71.4% | 82.1% | -10.7% | 0.214304 |
| `away_over_05` | 33 | 33 | 29 | 87.9% | 80.7% | +7.2% | 0.111227 |
| `home_over_05` | 28 | 28 | 24 | 85.7% | 88.9% | -3.2% | 0.126195 |
| `btts_yes` | 21 | 21 | 12 | 57.1% | 46.4% | +10.7% | 0.253336 |
| `btts_no` | 20 | 20 | 9 | 45.0% | 54.3% | -9.3% | 0.258307 |
| `match_over_15` | 18 | 18 | 15 | 83.3% | 84.8% | -1.5% | 0.13419 |
| `home_under_15` | 4 | 4 | 3 | 75.0% | 81.7% | -6.7% | 0.195262 ⚠️low-n |
| `double_chance` | 2 | 2 | 1 | 50.0% | 83.3% | -33.3% | 0.373866 ⚠️low-n |
| `home_over_15` | 1 | 1 | 1 | 100.0% | 81.9% | +18.1% | 0.032904 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2027 | 1415 | 69.8% | 65.0% | +4.8% | 0.139678 |
| model | 87 | 66 | 75.9% | 65.2% | +10.7% | 0.162135 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 85 | 19.1% | 17.6% | -1.5% |
| 0.2-0.3 | 291 | 24.2% | 23.4% | -0.8% |
| 0.3-0.4 | 70 | 34.2% | 47.1% | +12.9% |
| 0.4-0.5 | 482 | 44.4% | 59.5% | +15.1% |
| 0.5-0.6 | 86 | 52.9% | 60.5% | +7.5% |
| 0.6-0.7 | 9 | 62.1% | 66.7% | +4.6% |
| 0.7-0.8 | 7 | 72.9% | 85.7% | +12.8% |
| 0.8-0.9 | 370 | 86.8% | 88.6% | +1.8% |
| 0.9-1.0 | 714 | 94.1% | 96.1% | +2.0% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=541, MAE=1.523253 goals, bias=-0.322921 (realized − promised), promised avg 3.544732 vs realized 3.221811

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 541 | 30.6% | 33.3% | +2.7% | 0.194396 |
| BTTS-Yes | 541 | 41.2% | 53.0% | +11.8% | 0.263251 |
| Home Over 1.5 | 541 | 64.5% | 53.2% | -11.2% | 0.23251 |
| Over 2.5 | 541 | 69.6% | 61.6% | -8.1% | 0.242619 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 226 | 8.6% | 22.6% | +14.0% |
| 0.1-0.2 | 316 | 10.4% | 18.4% | +7.9% |
| 0.2-0.3 | 6 | 27.1% | 66.7% | +39.6% |
| 0.3-0.4 | 102 | 37.3% | 50.0% | +12.7% |
| 0.4-0.5 | 430 | 42.4% | 53.5% | +11.1% |
| 0.5-0.6 | 2 | 53.3% | 50.0% | -3.3% |
| 0.6-0.7 | 363 | 66.9% | 59.2% | -7.6% |
| 0.7-0.8 | 160 | 74.4% | 66.2% | -8.1% |
| 0.8-0.9 | 508 | 84.6% | 65.6% | -19.1% |
| 0.9-1.0 | 51 | 92.1% | 76.5% | -15.6% |

## By rule

- `2way-unanimous avg_p>=60`: settled=134, wins=84, hit_rate=0.626866, ROI=-0.128081
- `2way-unanimous avg_p>=70`: settled=49, wins=39, hit_rate=0.795918, ROI=0.005714
- `ml-meta avg_p>=55`: settled=215, wins=150, hit_rate=0.697674, ROI=0.123451
- `ml-meta avg_p>=60`: settled=95, wins=68, hit_rate=0.715789, ROI=0.081402
- `ml-meta avg_p>=65`: settled=21, wins=17, hit_rate=0.809524, ROI=-0.01625
- `ml-meta avg_p>=70`: settled=1, wins=0, hit_rate=0.0, ROI=-1.0
- `ml-meta avg_p>=80`: settled=8, wins=8, hit_rate=1.0, ROI=0.067143
- `unanimous[betclan+vitibet] avg_p>=70`: settled=8, wins=7, hit_rate=0.875, ROI=0.072
- `unanimous[bzzoiro+vitibet] avg_p>=70`: settled=6, wins=6, hit_rate=1.0, ROI=0.4283
- `unanimous[statarea+vitibet] avg_p>=70`: settled=4, wins=2, hit_rate=0.5, ROI=-0.1028
- `unanimous[vitibet+zulubet] avg_p>=70`: settled=2, wins=2, hit_rate=1.0, ROI=0.40125

## By bucket

- `CAUTION`: settled=42, wins=24, hit_rate=0.571429, ROI=-0.078614
- `CERTIFIED_CLEAN`: settled=79, wins=53, hit_rate=0.670886, ROI=0.081391
- `SKIPPED_VETO`: settled=268, wins=201, hit_rate=0.75, ROI=0.074178
- `WATCHLIST_NO_ODDS`: settled=60, wins=39, hit_rate=0.65, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=4, wins=3, hit_rate=0.75, ROI=0.025
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=86, wins=60, hit_rate=0.697674, ROI=0.001744
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=88, wins=60, hit_rate=0.681818, ROI=None
- `betexplorer_odds`: settled=146, wins=105, hit_rate=0.719178, ROI=0.004178
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=5, wins=4, hit_rate=0.8, ROI=0.094
- `forebet_best`: settled=42, wins=29, hit_rate=0.690476, ROI=0.032143
- `oddspapi_odds`: settled=4, wins=3, hit_rate=0.75, ROI=0.17625
- `pinnapi_odds`: settled=32, wins=22, hit_rate=0.6875, ROI=0.230725
- `scoutingstats_odds`: settled=160, wins=110, hit_rate=0.6875, ROI=-0.001563
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=41, wins=34, hit_rate=0.829268, ROI=0.262927
- `zulubet`: settled=23, wins=14, hit_rate=0.608696, ROI=-0.058696

## By odds match method

- `alias_fuzzy`: settled=15, wins=11, hit_rate=0.733333, ROI=-0.001667
- `betexplorer`: settled=100, wins=68, hit_rate=0.68, ROI=-0.0242
- `exact`: settled=290, wins=212, hit_rate=0.731034, ROI=0.080618
- `fallback`: settled=53, wins=35, hit_rate=0.660377, ROI=0.000377
- `none`: settled=85, wins=57, hit_rate=0.670588, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 100 | 68 | 0.68 | 100 | -0.0242 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 5 | 4 | 0.8 | 5 | 0.094 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 124 | 97 | 0.782258 | 124 | 0.182574 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 160 | 110 | 0.6875 | 160 | -0.001563 |
| Source fallback (`SOURCE_FALLBACK`) | 53 | 35 | 0.660377 | 53 | 0.000377 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 15 | 11 | 0.733333 | 12 | -0.001667 |
| No usable price (`UNMATCHED`) | 85 | 57 | 0.670588 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 268 | 201 | 0.75 | 242 | 0.074178 |
| **trusted evidence only** | 138 | 109 | 0.789855 | 138 | 0.117979 |
| **soft evidence only** | 130 | 92 | 0.707692 | 104 | 0.016058 |
| evidence: BETEXPLORER_RESCUE | 57 | 40 | 0.701754 | 57 | -0.060351 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.273333 |
| evidence: NAMED_BOOKMAKER_PRICE | 78 | 66 | 0.846154 | 78 | 0.242322 |
| evidence: SCOUTINGSTATS_SOLE | 74 | 50 | 0.675676 | 74 | -0.005405 |
| evidence: SOURCE_FALLBACK | 20 | 16 | 0.8 | 20 | 0.107 |
| evidence: SUSPECT_ALIAS_FUZZY | 11 | 8 | 0.727273 | 10 | -0.007 |
| evidence: UNMATCHED | 25 | 18 | 0.72 | 0 | None |
| odds band: <1.50 | 150 | 121 | 0.806667 | 150 | 0.018757 |
| odds band: 1.50-2.00 | 83 | 54 | 0.650602 | 83 | 0.08214 |
| odds band: 2.00-3.00 | 8 | 6 | 0.75 | 8 | 0.665 |
| odds band: >=3.00 | 1 | 1 | 1.0 | 1 | 3.0 |
| odds band: unpriced | 26 | 19 | 0.730769 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['competition_type'] | 13 | 11 | 0.846154 | 10 | 0.23488 |
| veto reason: context VETO in ['league', 'niche'] | 2 | 1 | 0.5 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 4 | 1 | 0.25 | 4 | -0.585 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.2762 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 4 | 3 | 0.75 | 4 | 0.015 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.6452 |
| veto reason: context VETO in ['league', 'team_h'] | 4 | 4 | 1.0 | 4 | 0.3625 |
| veto reason: context VETO in ['league'] | 24 | 17 | 0.708333 | 20 | -0.0195 |
| veto reason: context VETO in ['niche'] | 11 | 8 | 0.727273 | 11 | 0.01 |
| veto reason: context VETO in ['odds_band'] | 47 | 35 | 0.744681 | 47 | -0.042553 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 3 | 2 | 0.666667 | 3 | -0.084567 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 9 | 0.818182 | 11 | 0.010909 |
| veto reason: context VETO in ['team_a'] | 54 | 40 | 0.740741 | 47 | 0.13457 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 3 | 3 | 1.0 | 3 | 0.3166 |
| veto reason: context VETO in ['team_h', 'niche'] | 2 | 2 | 1.0 | 2 | 0.29 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.054286 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.44 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.32 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 13 | 0.764706 | 16 | 0.260625 |
| veto reason: context VETO in ['team_h'] | 43 | 32 | 0.744186 | 33 | 0.212727 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 17 | 9 | 0.529412 | 17 | -0.143529 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 14 | 11 | 0.785714 | 14 | 0.288443 |
| contrast CAUTION: SOURCE_FALLBACK | 10 | 4 | 0.4 | 10 | -0.39 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 357 | 255 | 0.714286 | 272 | 0.075144 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 15 | 11 | 0.733333 | 12 | -0.001667 | 15 | 1.602367 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 160 | 110 | 0.6875 | 160 | -0.001563 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 11 | 7 | 0.636364 | 11 | 0.071818 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-15: Sparta Praha vs Lillestrom (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 3.34 -> 🔴 LOST (Expected prob: 65.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 59.7% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.1% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 38.1% (Actual: 2 goals)

### 2026-10-15: Atalanta vs Pafos FC (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3676 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 68.7% (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.8% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.2% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 45.7% (Actual: 4 goals)

### 2026-10-15: Brann vs Lincoln Red Imps FC (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 80.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 37.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 88.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 55.2% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 37.4% (Actual: 3 goals)

### 2026-10-15: Riga FC vs Kairat Almaty (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.9091 -> 🔴 LOST (Expected prob: 65.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 80.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 59.7% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.1% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 38.1% (Actual: 2 goals)

### 2026-10-15: Bournemouth vs Sturm Graz (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 79.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 72.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 57.9% (Actual: 3 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 55.1% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 44.9% (Actual: BTTS-No)

### 2026-10-15: AZ Alkmaar vs Hapoel Beer Sheva (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 4.0 -> 🟢 WON (Expected prob: 77.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 37.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 73.2% (Actual: 3 goals)

### 2026-10-15: Benfica vs Celtic (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2392 -> 🟢 WON (Expected prob: 74.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 72.7% (Actual: 5 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.8% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 52.8% (Actual: 5 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.2% (Actual: BTTS-Yes)

### 2026-10-15: Nashville SC vs Sporting Kansas City (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2198 -> 🟢 WON (Expected prob: 77.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.9% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 87.4% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 4 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 73.5% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 55.8% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 35.3% (Actual: 4 goals)

### 2026-10-15: Twente vs FC Thun (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.1988 -> 🟢 WON (Expected prob: 74.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 52.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 59.2% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 34.0% (Actual: 1 goals)

### 2026-10-15: Panathinaikos vs FK Borac Banja Luka (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 65.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 60.9% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.1% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 39.3% (Actual: 3 goals)

### 2026-10-15: Los Angeles FC vs Austin FC (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 61.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.6% (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 50.8% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.2% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 34.6% (Actual: 4 goals)

### 2026-10-15: CSKA Sofia vs Monaco (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.4695 -> 🟢 WON (Expected prob: 69.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 64.0% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 61.9% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.8% (Actual: 3 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 38.1% (Actual: BTTS-Yes)

### 2026-10-15: Lech Poznan vs Bayer Leverkusen (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.6452 -> 🟢 WON (Expected prob: 67.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 60.7% (Actual: 4 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 56.6% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 43.4% (Actual: BTTS-No)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 43.1% (Actual: 4 goals)

### 2026-10-15: SC Freiburg vs FK Jablonec (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 77.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 37.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.3% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 73.5% (Actual: 5 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 57.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 55.8% (Actual: 5 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 42.3% (Actual: BTTS-Yes)


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

- none

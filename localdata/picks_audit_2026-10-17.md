# Edge Factory — Recent picks audit (2026-09-18 to 2026-10-17)

## Overall

- archived pick rows: 741
- archived pick dates: 30
- immutable morning-baseline rows: 576
- late-slate additions (regular-ledger rows not in the morning baseline): 167, of which on days whose regular ledger was rewritten: 162
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 694
- eligible prior picks: 707
- pending/unmatched result picks: 13
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 0
- wins: 482
- hit rate: +69.5%
- priced picks: 587
- ROI: +3.7%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-17
- same-day rows excluded: 34

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 421 / 694 matches (60.7%)
- **Both Teams to Score (BTTS)**: occurred in 374 / 694 matches (53.9%)
- **Selected Team Over 1.5 Goals**: occurred in 458 / 694 matches (66.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 685
- **Total Hits**: 562
- **Overall Hit Rate**: 82.0%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, settled=18, hit_rate=94.4%, priced_n=1, registry_processed=53, class=priced
- `away_under_15`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced
- `away_under_25`: recommended=26, settled=26, hit_rate=96.2%, priced_n=3, registry_processed=35, class=priced
- `away_under_35`: recommended=219, settled=219, hit_rate=97.3%, priced_n=1, registry_processed=305, class=priced
- `btts_no`: recommended=3, settled=3, hit_rate=66.7%, priced_n=3, registry_processed=3, class=priced
- `btts_yes`: recommended=3, settled=3, hit_rate=100.0%, priced_n=3, registry_processed=16, class=priced
- `home_over_05`: recommended=23, settled=23, hit_rate=87.0%, priced_n=1, registry_processed=186, class=priced
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced
- `home_under_25`: recommended=28, settled=28, hit_rate=92.9%, priced_n=0, registry_processed=40, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_35`: recommended=55, settled=55, hit_rate=98.2%, priced_n=0, registry_processed=74, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=18, settled=18, hit_rate=88.9%, priced_n=14, registry_processed=65, class=priced
- `match_over_25`: recommended=269, settled=269, hit_rate=62.1%, priced_n=175, registry_processed=647, class=priced
- `match_over_35`: recommended=17, settled=17, hit_rate=76.5%, priced_n=11, registry_processed=42, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2673** | scored: 2673

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 670 | 670 | 404 | 60.3% | 45.7% | +14.6% | 0.260721 |
| `match_over_45` | 517 | 517 | 114 | 22.1% | 23.7% | -1.6% | 0.17217 |
| `away_under_35` | 448 | 448 | 439 | 98.0% | 95.4% | +2.6% | 0.020647 |
| `away_under_25` | 419 | 419 | 389 | 92.8% | 90.1% | +2.7% | 0.067436 |
| `home_under_35` | 180 | 180 | 175 | 97.2% | 94.5% | +2.7% | 0.029209 |
| `home_under_25` | 153 | 153 | 141 | 92.2% | 88.8% | +3.3% | 0.073875 |
| `match_over_35` | 69 | 69 | 38 | 55.1% | 41.7% | +13.4% | 0.272586 |
| `away_over_05` | 44 | 44 | 39 | 88.6% | 81.0% | +7.7% | 0.106313 |
| `away_under_15` | 37 | 37 | 27 | 73.0% | 82.0% | -9.1% | 0.204729 |
| `btts_yes` | 37 | 37 | 23 | 62.2% | 47.5% | +14.6% | 0.246441 |
| `home_over_05` | 34 | 34 | 30 | 88.2% | 89.1% | -0.8% | 0.105948 |
| `btts_no` | 33 | 33 | 14 | 42.4% | 53.6% | -11.1% | 0.25326 |
| `match_over_15` | 22 | 22 | 18 | 81.8% | 84.8% | -3.0% | 0.148204 |
| `home_under_15` | 5 | 5 | 4 | 80.0% | 81.7% | -1.7% | 0.163042 |
| `double_chance` | 4 | 4 | 3 | 75.0% | 84.9% | -9.9% | 0.196269 ⚠️low-n |
| `home_over_15` | 1 | 1 | 1 | 100.0% | 81.9% | +18.1% | 0.032904 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2570 | 1779 | 69.2% | 64.6% | +4.7% | 0.13867 |
| model | 103 | 80 | 77.7% | 65.6% | +12.1% | 0.178757 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 115 | 19.2% | 20.9% | +1.7% |
| 0.2-0.3 | 356 | 24.1% | 21.3% | -2.7% |
| 0.3-0.4 | 103 | 34.7% | 47.6% | +12.9% |
| 0.4-0.5 | 614 | 44.5% | 58.6% | +14.2% |
| 0.5-0.6 | 113 | 53.0% | 59.3% | +6.2% |
| 0.6-0.7 | 17 | 62.6% | 64.7% | +2.1% |
| 0.7-0.8 | 8 | 73.1% | 75.0% | +1.9% |
| 0.8-0.9 | 468 | 86.9% | 90.0% | +3.1% |
| 0.9-1.0 | 879 | 94.1% | 96.1% | +2.0% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=692, MAE=1.523974 goals, bias=-0.323512 (realized − promised), promised avg 3.538829 vs realized 3.215318

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 692 | 31.7% | 32.7% | +1.0% | 0.202376 |
| BTTS-Yes | 692 | 41.3% | 53.8% | +12.4% | 0.265257 |
| Home Over 1.5 | 692 | 63.3% | 53.8% | -9.5% | 0.232829 |
| Over 2.5 | 692 | 69.6% | 60.5% | -9.0% | 0.245614 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 288 | 8.6% | 21.9% | +13.3% |
| 0.1-0.2 | 404 | 10.5% | 19.8% | +9.3% |
| 0.2-0.3 | 9 | 24.8% | 55.6% | +30.7% |
| 0.3-0.4 | 120 | 37.1% | 50.8% | +13.8% |
| 0.4-0.5 | 560 | 42.4% | 54.3% | +11.9% |
| 0.5-0.6 | 2 | 53.3% | 50.0% | -3.3% |
| 0.6-0.7 | 474 | 66.9% | 58.2% | -8.6% |
| 0.7-0.8 | 196 | 74.4% | 64.8% | -9.6% |
| 0.8-0.9 | 650 | 84.5% | 64.5% | -20.1% |
| 0.9-1.0 | 65 | 92.2% | 81.5% | -10.7% |

## By rule

- `2way-unanimous avg_p>=60`: settled=164, wins=106, hit_rate=0.646341, ROI=-0.097951
- `2way-unanimous avg_p>=70`: settled=59, wins=45, hit_rate=0.762712, ROI=0.032195
- `ml-meta avg_p>=55`: settled=277, wins=190, hit_rate=0.685921, ROI=0.091024
- `ml-meta avg_p>=60`: settled=134, wins=89, hit_rate=0.664179, ROI=0.026871
- `ml-meta avg_p>=65`: settled=24, wins=20, hit_rate=0.833333, ROI=0.006667
- `ml-meta avg_p>=70`: settled=1, wins=0, hit_rate=0.0, ROI=-1.0
- `ml-meta avg_p>=80`: settled=8, wins=8, hit_rate=1.0, ROI=0.067143
- `unanimous[betclan+vitibet] avg_p>=70`: settled=12, wins=11, hit_rate=0.916667, ROI=0.344633
- `unanimous[bzzoiro+vitibet] avg_p>=70`: settled=6, wins=6, hit_rate=1.0, ROI=0.4283
- `unanimous[statarea+vitibet] avg_p>=70`: settled=5, wins=3, hit_rate=0.6, ROI=-0.05706
- `unanimous[vitibet+zulubet] avg_p>=70`: settled=4, wins=4, hit_rate=1.0, ROI=0.260625

## By bucket

- `CAUTION`: settled=53, wins=30, hit_rate=0.566038, ROI=-0.10494
- `CERTIFIED_CLEAN`: settled=100, wins=65, hit_rate=0.65, ROI=0.051699
- `SKIPPED_VETO`: settled=346, wins=254, hit_rate=0.734104, ROI=0.062369
- `WATCHLIST_NO_ODDS`: settled=73, wins=48, hit_rate=0.657534, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=13, wins=8, hit_rate=0.615385, ROI=0.077778
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=103, wins=72, hit_rate=0.699029, ROI=0.014272
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333, ROI=-0.001667

## By odds source

- `UNKNOWN`: settled=107, wins=71, hit_rate=0.663551, ROI=None
- `betexplorer_odds`: settled=199, wins=143, hit_rate=0.718593, ROI=-0.006533
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=6, wins=5, hit_rate=0.833333, ROI=0.191667
- `forebet_best`: settled=53, wins=38, hit_rate=0.716981, ROI=0.054906
- `oddspapi_odds`: settled=5, wins=3, hit_rate=0.6, ROI=-0.059
- `pinnapi_odds`: settled=45, wins=27, hit_rate=0.6, ROI=0.095351
- `scoutingstats_odds`: settled=189, wins=130, hit_rate=0.687831, ROI=0.010847
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=46, wins=38, hit_rate=0.826087, ROI=0.272609
- `zulubet`: settled=42, wins=25, hit_rate=0.595238, ROI=-0.026905

## By odds match method

- `alias_fuzzy`: settled=31, wins=19, hit_rate=0.612903, ROI=-0.033077
- `betexplorer`: settled=131, wins=89, hit_rate=0.679389, ROI=-0.034198
- `exact`: settled=361, wins=259, hit_rate=0.717452, ROI=0.066972
- `fallback`: settled=69, wins=47, hit_rate=0.681159, ROI=0.038261
- `none`: settled=102, wins=68, hit_rate=0.666667, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 131 | 89 | 0.679389 | 131 | -0.034198 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 6 | 5 | 0.833333 | 6 | 0.191667 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 165 | 123 | 0.745455 | 165 | 0.123981 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 189 | 130 | 0.687831 | 189 | 0.010847 |
| Source fallback (`SOURCE_FALLBACK`) | 69 | 47 | 0.681159 | 69 | 0.038261 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 31 | 19 | 0.612903 | 26 | -0.033077 |
| No usable price (`UNMATCHED`) | 102 | 68 | 0.666667 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 346 | 254 | 0.734104 | 316 | 0.062369 |
| **trusted evidence only** | 182 | 142 | 0.78022 | 182 | 0.105323 |
| **soft evidence only** | 164 | 112 | 0.682927 | 134 | 0.00403 |
| evidence: BETEXPLORER_RESCUE | 73 | 52 | 0.712329 | 73 | -0.058904 |
| evidence: BZZOIRO_PRIMARY | 4 | 4 | 1.0 | 4 | 0.375 |
| evidence: NAMED_BOOKMAKER_PRICE | 105 | 86 | 0.819048 | 105 | 0.209226 |
| evidence: SCOUTINGSTATS_SOLE | 86 | 58 | 0.674419 | 86 | 0.006744 |
| evidence: SOURCE_FALLBACK | 31 | 23 | 0.741935 | 31 | 0.049032 |
| evidence: SUSPECT_ALIAS_FUZZY | 18 | 11 | 0.611111 | 17 | -0.091765 |
| evidence: UNMATCHED | 29 | 20 | 0.689655 | 0 | None |
| odds band: <1.50 | 188 | 151 | 0.803191 | 188 | 0.010591 |
| odds band: 1.50-2.00 | 109 | 69 | 0.633028 | 109 | 0.051905 |
| odds band: 2.00-3.00 | 16 | 12 | 0.75 | 16 | 0.69125 |
| odds band: >=3.00 | 3 | 1 | 0.333333 | 3 | 0.333333 |
| odds band: unpriced | 30 | 21 | 0.7 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['competition_type'] | 18 | 16 | 0.888889 | 15 | 0.330313 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.335 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_a'] | 6 | 1 | 0.166667 | 6 | -0.723333 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.2762 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 5 | 3 | 0.6 | 5 | -0.188 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.26 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 5 | 4 | 0.8 | 5 | 0.09 |
| veto reason: context VETO in ['league'] | 31 | 20 | 0.645161 | 26 | -0.143462 |
| veto reason: context VETO in ['niche'] | 14 | 10 | 0.714286 | 14 | 0.012857 |
| veto reason: context VETO in ['odds_band'] | 63 | 45 | 0.714286 | 63 | -0.040476 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 3 | 2 | 0.666667 | 3 | -0.084567 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 12 | 10 | 0.833333 | 12 | 0.113333 |
| veto reason: context VETO in ['team_a'] | 69 | 50 | 0.724638 | 60 | 0.105413 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 5 | 5 | 1.0 | 5 | 0.2903 |
| veto reason: context VETO in ['team_h', 'niche'] | 6 | 5 | 0.833333 | 6 | 0.205 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 8 | 6 | 0.75 | 8 | -0.04125 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.44 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.13 |
| veto reason: context VETO in ['team_h', 'team_a'] | 19 | 15 | 0.789474 | 18 | 0.323889 |
| veto reason: context VETO in ['team_h'] | 53 | 38 | 0.716981 | 42 | 0.176429 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.08 | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: short-odds away favourite 1.16 | 2 | 2 | 1.0 | 2 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 23 | 12 | 0.521739 | 23 | -0.183478 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 18 | 13 | 0.722222 | 18 | 0.181011 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.327273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 458 | 323 | 0.70524 | 356 | 0.051789 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 31 | 19 | 0.612903 | 26 | -0.033077 | 31 | 1.680203 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 189 | 130 | 0.687831 | 189 | 0.010847 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 16 | 10 | 0.625 | 16 | 0.115625 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-16: Finn Harps vs Bray Wanderers (Actual Score: **2-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.4032 -> 🔴 LOST (Expected prob: 62.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-16: Fremad Amager vs Nykobing FC (Actual Score: **3-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.78 -> 🔴 LOST (Expected prob: 61.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-16: Internacional Palmira vs Orsomarso (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 4.12 -> 🔴 LOST (Expected prob: 60.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-16: Al-Qadisiyah vs Abha (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.1259 -> 🟢 WON (Expected prob: 77.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-16: Energie Cottbus vs 1. FC Nürnberg (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.9804 -> 🔴 LOST (Expected prob: 62.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 62.1% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 51.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 48.7% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 39.6% (Actual: 2 goals)

### 2026-10-16: Alashkert vs Syunik (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 80.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 37.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.3% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 92.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 52.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.6% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 38.8% (Actual: 6 goals)

### 2026-10-16: Heerenveen vs Excelsior (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.58 -> 🟢 WON (Expected prob: 62.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.9% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 57.2% (Actual: 4 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.8% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 48.2% (Actual: BTTS-No)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.2% (Actual: 4 goals)

### 2026-10-16: Yantra 2019 vs Lokomotiv Plovdiv (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🟢 WON (Expected prob: 68.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 36.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-16: Stade Nyonnais vs FC Basel 1893 (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.15 -> 🟢 WON (Expected prob: 64.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.9% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 61.9% (Actual: 3 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 53.6% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.4% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 40.7% (Actual: 3 goals)

### 2026-10-16: Laval vs Clermont Foot (Actual Score: **3-3**)
- **1X2 Pick**: Selected `AWAY` @ 3.36 -> 🔴 LOST (Expected prob: 60.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 81.5% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 60.2% (Actual: 6 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 50.5% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.5% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 37.4% (Actual: 6 goals)

### 2026-10-16: Rapid Vienna vs TSV Hartberg (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.26 -> 🟢 WON (Expected prob: 80.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 36.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 88.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 63.1% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.2% (Actual: 4 goals)

### 2026-10-16: SV Lafnitz vs Gleisdorf 09 (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🟢 WON (Expected prob: 61.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.4% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.7% (Actual: 6 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 51.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 48.7% (Actual: BTTS-Yes)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-09-20 `CERTIFIED_CLEAN` `ml-meta avg_p>=55` — Juticalpa vs CD Marathon -> AWAY @ 3.65 (rescheduled → 2026-09-21; actual Juticalpa 3-2 CD Marathón [home])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])
- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova FC 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca W 4-1 Santos Laguna W [home])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ None (rescheduled → 2026-10-03; actual Tampa Bay Rowdies 1-2 Miami FC [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Brooklyn vs Rhode Island FC -> AWAY @ None (rescheduled → 2026-10-03; actual Brooklyn 1-3 Rhode Island [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kano Pillars FC vs Sporting Lagos -> HOME @ None (rescheduled → 2026-10-03; actual Kano Pillars 1-1 Sporting Lagos [draw])

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
- 2026-10-09 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Real Cundinamarca vs Real Santander -> HOME @ None (pending_or_unmatched_result); keys=['cundinama']/['santander']
- 2026-10-11 `SKIPPED_VETO` `ml-meta avg_p>=60` — Atletico Nacional vs Deportivo Pasto -> HOME @ 2.1 (pending_or_unmatched_result); keys=['nacional']/['pasto']
- 2026-10-11 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Ranger's vs Carroi -> HOME @ None (pending_or_unmatched_result); keys=['rangers']/['carroi']
- 2026-10-16 `CERTIFIED_CLEAN` `ml-meta avg_p>=60` — MTK Budapest vs Vasas -> HOME @ 2.51 (pending_or_unmatched_result); keys=['mtkbudape']/['vasas']

## Ambiguous result examples

- none

# Edge Factory — Recent picks audit (2026-09-19 to 2026-10-18)

## Overall

- archived pick rows: 746
- archived pick dates: 30
- immutable morning-baseline rows: 572
- late-slate additions (regular-ledger rows not in the morning baseline): 176, of which on days whose regular ledger was rewritten: 171
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 710
- eligible prior picks: 722
- pending/unmatched result picks: 12
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 0
- wins: 487
- hit rate: +68.6%
- priced picks: 601
- ROI: +2.3%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-18
- same-day rows excluded: 24

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 423 / 710 matches (59.6%)
- **Both Teams to Score (BTTS)**: occurred in 376 / 710 matches (53.0%)
- **Selected Team Over 1.5 Goals**: occurred in 460 / 710 matches (64.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 690
- **Total Hits**: 553
- **Overall Hit Rate**: 80.1%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, settled=18, hit_rate=94.4%, priced_n=1, registry_processed=53, class=priced
- `away_under_15`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced
- `away_under_25`: recommended=17, settled=17, hit_rate=94.1%, priced_n=3, registry_processed=35, class=priced
- `away_under_35`: recommended=208, settled=208, hit_rate=97.1%, priced_n=1, registry_processed=305, class=priced
- `btts_no`: recommended=6, settled=6, hit_rate=33.3%, priced_n=6, registry_processed=6, class=priced
- `btts_yes`: recommended=4, settled=4, hit_rate=100.0%, priced_n=4, registry_processed=17, class=priced
- `home_over_05`: recommended=23, settled=23, hit_rate=87.0%, priced_n=1, registry_processed=186, class=priced
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced
- `home_under_25`: recommended=26, settled=26, hit_rate=92.3%, priced_n=0, registry_processed=40, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_35`: recommended=55, settled=55, hit_rate=98.2%, priced_n=0, registry_processed=74, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=21, settled=21, hit_rate=85.7%, priced_n=17, registry_processed=68, class=priced
- `match_over_25`: recommended=288, settled=288, hit_rate=61.1%, priced_n=202, registry_processed=677, class=priced
- `match_over_35`: recommended=18, settled=18, hit_rate=77.8%, priced_n=12, registry_processed=43, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2692** | scored: 2692

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 671 | 671 | 398 | 59.3% | 46.7% | +12.6% | 0.259431 |
| `match_over_45` | 499 | 499 | 109 | 21.8% | 23.7% | -1.8% | 0.171153 |
| `away_under_35` | 420 | 420 | 411 | 97.9% | 95.5% | +2.3% | 0.021663 |
| `away_under_25` | 391 | 391 | 363 | 92.8% | 89.9% | +2.9% | 0.067571 |
| `home_under_35` | 177 | 177 | 172 | 97.2% | 94.6% | +2.6% | 0.029551 |
| `home_under_25` | 149 | 149 | 137 | 91.9% | 88.7% | +3.2% | 0.075698 |
| `match_over_35` | 100 | 100 | 52 | 52.0% | 42.4% | +9.6% | 0.272003 |
| `btts_yes` | 70 | 70 | 39 | 55.7% | 46.9% | +8.8% | 0.241222 |
| `btts_no` | 65 | 65 | 31 | 47.7% | 54.1% | -6.4% | 0.247076 |
| `away_over_05` | 44 | 44 | 39 | 88.6% | 81.0% | +7.7% | 0.106313 |
| `away_under_15` | 37 | 37 | 27 | 73.0% | 82.0% | -9.1% | 0.204729 |
| `home_over_05` | 34 | 34 | 30 | 88.2% | 89.1% | -0.8% | 0.105948 |
| `match_over_15` | 25 | 25 | 20 | 80.0% | 84.7% | -4.7% | 0.163001 |
| `home_under_15` | 5 | 5 | 4 | 80.0% | 81.7% | -1.7% | 0.163042 |
| `double_chance` | 4 | 4 | 3 | 75.0% | 84.9% | -9.9% | 0.196269 ⚠️low-n |
| `home_over_15` | 1 | 1 | 1 | 100.0% | 81.9% | +18.1% | 0.032904 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2588 | 1755 | 67.8% | 63.8% | +4.0% | 0.144926 |
| model | 104 | 81 | 77.9% | 66.0% | +11.9% | 0.174532 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 108 | 19.1% | 21.3% | +2.1% |
| 0.2-0.3 | 347 | 24.0% | 20.7% | -3.3% |
| 0.3-0.4 | 114 | 35.0% | 47.4% | +12.3% |
| 0.4-0.5 | 628 | 44.6% | 57.2% | +12.5% |
| 0.5-0.6 | 158 | 53.6% | 57.0% | +3.4% |
| 0.6-0.7 | 35 | 63.3% | 62.9% | -0.4% |
| 0.7-0.8 | 15 | 72.8% | 60.0% | -12.8% |
| 0.8-0.9 | 471 | 86.9% | 89.8% | +2.9% |
| 0.9-1.0 | 816 | 94.2% | 96.1% | +1.8% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=708, MAE=1.562274 goals, bias=-0.376822 (realized − promised), promised avg 3.546314 vs realized 3.169492

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 708 | 32.4% | 33.1% | +0.7% | 0.209824 |
| BTTS-Yes | 708 | 41.1% | 52.8% | +11.7% | 0.264247 |
| Home Over 1.5 | 708 | 62.7% | 52.7% | -10.0% | 0.238674 |
| Over 2.5 | 708 | 69.6% | 59.5% | -10.2% | 0.249721 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 295 | 8.6% | 22.4% | +13.7% |
| 0.1-0.2 | 413 | 10.5% | 20.3% | +9.9% |
| 0.2-0.3 | 9 | 24.8% | 55.6% | +30.7% |
| 0.3-0.4 | 128 | 37.0% | 49.2% | +12.2% |
| 0.4-0.5 | 568 | 42.2% | 53.5% | +11.3% |
| 0.5-0.6 | 2 | 53.3% | 50.0% | -3.3% |
| 0.6-0.7 | 482 | 67.0% | 56.8% | -10.1% |
| 0.7-0.8 | 205 | 74.5% | 64.4% | -10.1% |
| 0.8-0.9 | 663 | 84.6% | 63.5% | -21.1% |
| 0.9-1.0 | 67 | 92.0% | 77.6% | -14.4% |

## By rule

- `2way-unanimous avg_p>=60`: settled=164, wins=106, hit_rate=0.646341, ROI=-0.097951
- `2way-unanimous avg_p>=70`: settled=49, wins=37, hit_rate=0.755102, ROI=0.000286
- `ml-meta avg_p>=55`: settled=255, wins=173, hit_rate=0.678431, ROI=0.076693
- `ml-meta avg_p>=60`: settled=169, wins=107, hit_rate=0.633136, ROI=-0.003034
- `ml-meta avg_p>=65`: settled=24, wins=20, hit_rate=0.833333, ROI=0.006667
- `ml-meta avg_p>=70`: settled=1, wins=0, hit_rate=0.0, ROI=-1.0
- `ml-meta avg_p>=80`: settled=8, wins=8, hit_rate=1.0, ROI=0.067143
- `unanimous[betclan+vitibet] avg_p>=70`: settled=14, wins=13, hit_rate=0.928571, ROI=0.35017
- `unanimous[bzzoiro+vitibet] avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.25344
- `unanimous[statarea+vitibet] avg_p>=70`: settled=11, wins=9, hit_rate=0.818182, ROI=0.09005
- `unanimous[vitibet+zulubet] avg_p>=70`: settled=5, wins=5, hit_rate=1.0, ROI=0.3925

## By bucket

- `CAUTION`: settled=53, wins=30, hit_rate=0.566038, ROI=-0.098525
- `CERTIFIED_CLEAN`: settled=108, wins=70, hit_rate=0.648148, ROI=0.049073
- `SKIPPED_VETO`: settled=357, wins=260, hit_rate=0.728291, ROI=0.049188
- `WATCHLIST_NO_ODDS`: settled=72, wins=46, hit_rate=0.638889, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=15, wins=9, hit_rate=0.6, ROI=0.033636
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=99, wins=67, hit_rate=0.676768, ROI=-0.028384
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333, ROI=-0.001667

## By odds source

- `UNKNOWN`: settled=109, wins=71, hit_rate=0.651376, ROI=None
- `betexplorer_odds`: settled=201, wins=146, hit_rate=0.726368, ROI=0.006318
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=6, wins=5, hit_rate=0.833333, ROI=0.191667
- `forebet_best`: settled=50, wins=35, hit_rate=0.7, ROI=0.0286
- `oddspapi_odds`: settled=5, wins=3, hit_rate=0.6, ROI=-0.059
- `pinnapi_odds`: settled=53, wins=33, hit_rate=0.622642, ROI=0.089792
- `scoutingstats_odds`: settled=178, wins=120, hit_rate=0.674157, ROI=-0.018708
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=60, wins=46, hit_rate=0.766667, ROI=0.1655
- `zulubet`: settled=46, wins=26, hit_rate=0.565217, ROI=-0.056739

## By odds match method

- `alias_fuzzy`: settled=34, wins=21, hit_rate=0.617647, ROI=-0.0425
- `betexplorer`: settled=122, wins=83, hit_rate=0.680328, ROI=-0.033279
- `exact`: settled=383, wins=272, hit_rate=0.710183, ROI=0.049099
- `fallback`: settled=68, wins=44, hit_rate=0.647059, ROI=0.000147
- `none`: settled=103, wins=67, hit_rate=0.650485, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 122 | 83 | 0.680328 | 122 | -0.033279 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 6 | 5 | 0.833333 | 6 | 0.191667 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 198 | 146 | 0.737374 | 198 | 0.103359 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 178 | 120 | 0.674157 | 178 | -0.018708 |
| Source fallback (`SOURCE_FALLBACK`) | 68 | 44 | 0.647059 | 68 | 0.000147 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 34 | 21 | 0.617647 | 28 | -0.0425 |
| No usable price (`UNMATCHED`) | 103 | 67 | 0.650485 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 357 | 260 | 0.728291 | 324 | 0.049188 |
| **trusted evidence only** | 199 | 154 | 0.773869 | 199 | 0.093301 |
| **soft evidence only** | 158 | 106 | 0.670886 | 125 | -0.02104 |
| evidence: BETEXPLORER_RESCUE | 68 | 48 | 0.705882 | 68 | -0.066765 |
| evidence: BZZOIRO_PRIMARY | 4 | 4 | 1.0 | 4 | 0.375 |
| evidence: NAMED_BOOKMAKER_PRICE | 127 | 102 | 0.80315 | 127 | 0.170133 |
| evidence: SCOUTINGSTATS_SOLE | 79 | 53 | 0.670886 | 79 | -0.006582 |
| evidence: SOURCE_FALLBACK | 29 | 20 | 0.689655 | 29 | -0.018966 |
| evidence: SUSPECT_ALIAS_FUZZY | 19 | 12 | 0.631579 | 17 | -0.091765 |
| evidence: UNMATCHED | 31 | 21 | 0.677419 | 0 | None |
| odds band: <1.50 | 195 | 157 | 0.805128 | 195 | 0.015821 |
| odds band: 1.50-2.00 | 109 | 68 | 0.623853 | 109 | 0.035247 |
| odds band: 2.00-3.00 | 16 | 11 | 0.6875 | 16 | 0.563125 |
| odds band: >=3.00 | 4 | 1 | 0.25 | 4 | 0.0 |
| odds band: unpriced | 33 | 23 | 0.69697 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['competition_type'] | 26 | 23 | 0.884615 | 21 | 0.252129 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.335 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_a'] | 6 | 1 | 0.166667 | 6 | -0.723333 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.2762 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 9 | 5 | 0.555556 | 8 | -0.10875 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.26 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 4 | 3 | 0.75 | 4 | 0.0725 |
| veto reason: context VETO in ['league'] | 29 | 16 | 0.551724 | 24 | -0.3175 |
| veto reason: context VETO in ['niche'] | 12 | 8 | 0.666667 | 12 | -0.073333 |
| veto reason: context VETO in ['odds_band'] | 61 | 43 | 0.704918 | 61 | -0.043934 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 4 | 3 | 0.75 | 4 | 0.000525 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 9 | 0.818182 | 11 | 0.119091 |
| veto reason: context VETO in ['team_a'] | 70 | 51 | 0.728571 | 61 | 0.107513 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 8 | 8 | 1.0 | 8 | 0.300763 |
| veto reason: context VETO in ['team_h', 'niche'] | 7 | 6 | 0.857143 | 7 | 0.212857 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 8 | 6 | 0.75 | 8 | -0.04125 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.44 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.13 |
| veto reason: context VETO in ['team_h', 'team_a'] | 21 | 16 | 0.761905 | 20 | 0.277215 |
| veto reason: context VETO in ['team_h'] | 52 | 38 | 0.730769 | 41 | 0.173171 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.08 | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: short-odds away favourite 1.16 | 2 | 2 | 1.0 | 2 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 22 | 11 | 0.5 | 22 | -0.214545 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 19 | 14 | 0.736842 | 19 | 0.192537 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.287273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 479 | 335 | 0.699374 | 376 | 0.046051 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 34 | 21 | 0.617647 | 28 | -0.0425 | 34 | 1.668165 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 178 | 120 | 0.674157 | 178 | -0.018708 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 19 | 11 | 0.578947 | 19 | 0.040526 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-17: Athletic Club W vs Valencia W (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.92 -> 🟢 WON (Expected prob: 72.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 86.6% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 70.3% (Actual: 1 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 55.3% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 48.4% (Actual: 1 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 44.7% (Actual: BTTS-No)

### 2026-10-17: Salford City vs Crawley Town (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 69.6% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 55.7% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.4% (Actual: 3 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 44.3% (Actual: BTTS-Yes)

### 2026-10-17: Slavia Praha vs Hradec Kralove (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🔴 LOST (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 77.3% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 72.4% (Actual: 0 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 54.3% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 51.6% (Actual: 0 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.7% (Actual: BTTS-No)

### 2026-10-17: Philadelphia Union vs Charlotte (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🔴 LOST (Expected prob: 64.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.8% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.2% (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 36.8% (Actual: 4 goals)

### 2026-10-17: Genclerbirligi vs Galatasaray (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.43 -> 🟢 WON (Expected prob: 69.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 64.0% (Actual: 1 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 61.9% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.8% (Actual: 1 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 38.1% (Actual: BTTS-No)

### 2026-10-17: Kashima Antlers vs V-Varen Nagasaki (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.56 -> 🟢 WON (Expected prob: 61.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 56.6% (Actual: 2 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 50.8% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.2% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 34.6% (Actual: 2 goals)

### 2026-10-17: Villarreal vs Elche (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.51 -> 🔴 LOST (Expected prob: 60.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.9% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 56.2% (Actual: 0 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.0% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.0% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 34.5% (Actual: 0 goals)

### 2026-10-17: Stockport County FC vs Bromley (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.26 -> 🟢 WON (Expected prob: 77.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 72.3% (Actual: 1 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 57.1% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 54.8% (Actual: 1 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 42.9% (Actual: BTTS-No)

### 2026-10-17: ADO Den Haag vs PSV Eindhoven (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.29 -> 🔴 LOST (Expected prob: 76.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 94.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 91.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: Hapoel Tel Aviv vs Ironi Tiberias (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.23 -> 🟢 WON (Expected prob: 76.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 74.1% (Actual: 1 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 56.5% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 54.0% (Actual: 1 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 43.5% (Actual: BTTS-No)

### 2026-10-17: Cavalry FC vs Pacific FC (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.17 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.7% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.0% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 53.3% (Actual: 6 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 47.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 34.7% (Actual: 6 goals)

### 2026-10-17: Telstar vs Feyenoord (Actual Score: **3-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.35 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.7% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 95.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 89.0% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 74.5% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.9% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 42.2% (Actual: 7 goals)

### 2026-10-17: Sanfrecce Hiroshima vs Kyoto Sanga (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3546 -> 🟢 WON (Expected prob: 73.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 72.3% (Actual: 3 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 54.6% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 51.3% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.4% (Actual: BTTS-No)

### 2026-10-17: Manchester City vs Ipswich (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 71.2% (Actual: 5 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 54.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 49.3% (Actual: 5 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.1% (Actual: BTTS-Yes)

### 2026-10-17: Viking vs Fredrikstad (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: Fenerbahce vs Alanyaspor (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.32 -> 🟢 WON (Expected prob: 72.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 69.9% (Actual: 3 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 55.6% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.7% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 44.4% (Actual: BTTS-No)

### 2026-10-17: Tiszakecske FC vs Csakvar (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 68.9% (Actual: 1 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 54.3% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.2% (Actual: 1 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.7% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.9% (Actual: 1 goals)

### 2026-10-17: Queen Of The South vs Ross County (Actual Score: **1-7**)
- **1X2 Pick**: Selected `AWAY` @ 1.2558 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.4% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 35.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.2% (Actual: 7 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 65.5% (Actual: 8 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 60.6% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 49.8% (Actual: 8 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 39.4% (Actual: BTTS-Yes)

### 2026-10-17: Ham-Kam vs Bodo/Glimt (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.26 -> 🟢 WON (Expected prob: 69.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 64.1% (Actual: 2 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 60.6% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 49.0% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 39.4% (Actual: BTTS-No)

### 2026-10-17: Bayern Munich vs RB Leipzig (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.26 -> 🟢 WON (Expected prob: 67.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.9% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 54.1% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 40.0% (Actual: 7 goals)

### 2026-10-17: Inter Turku vs AC Oulu (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🔴 LOST (Expected prob: 64.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.8% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.5% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 54.1% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.9% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 37.8% (Actual: 3 goals)

### 2026-10-17: Betis vs Barcelona (Actual Score: **2-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.45 -> 🟢 WON (Expected prob: 64.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.5% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.7% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 47.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 40.2% (Actual: 7 goals)

### 2026-10-17: Kashiwa Reysol vs Nagoya Grampus (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.64 -> 🔴 LOST (Expected prob: 64.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 58.9% (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.4% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.6% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 36.5% (Actual: 4 goals)

### 2026-10-17: Eastleigh vs Brentwood Town (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 64.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.8% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.2% (Actual: 5 goals)

### 2026-10-17: Middlesbrough vs Cardiff (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 63.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 58.1% (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 47.1% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 36.1% (Actual: 4 goals)

### 2026-10-17: Clyde vs Annan Athletic (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7143 -> 🟢 WON (Expected prob: 62.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: Maccabi Petah Tikva vs Maccabi Haifa (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.3745 -> 🟢 WON (Expected prob: 62.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 62.1% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 51.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 48.7% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 39.6% (Actual: 3 goals)

### 2026-10-17: Altrincham vs FC Utd Of Manchester (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 71.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.7% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: Salisbury FC vs Eastbourne Borough (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 71.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 68.3% (Actual: 3 goals)

### 2026-10-17: Boreham Wood vs Woking (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 61.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.2% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.8% (Actual: 5 goals)

### 2026-10-17: Tokyo Verdy vs FC Tokyo (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.71 -> 🟢 WON (Expected prob: 62.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 82.3% (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 62.2% (Actual: 4 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.7% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 48.3% (Actual: BTTS-No)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 39.5% (Actual: 4 goals)

### 2026-10-17: Real Madrid (w) vs Espanyol (w) (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.19 -> 🟢 WON (Expected prob: 69.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 44.0% (Actual: 4 goals)

### 2026-10-17: AS Roma vs Genoa (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 64.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 58.4% (Actual: 2 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 53.1% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.9% (Actual: BTTS-No)

### 2026-10-17: Hartford Athletic vs Brooklyn (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.4115 -> 🔴 LOST (Expected prob: 61.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.2% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.8% (Actual: 5 goals)

### 2026-10-17: Kolos Kovalivka II vs UCSA (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.84 -> 🔴 LOST (Expected prob: 61.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.5% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.2% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: FC BW Linz vs FC Liefering (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 75.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 78.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.6% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: Atletico-MG vs Coritiba (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: Union Berlin vs Borussia Dortmund (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.63 -> 🔴 LOST (Expected prob: 69.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.7% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 64.0% (Actual: 0 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 61.9% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.8% (Actual: 0 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 38.1% (Actual: BTTS-No)

### 2026-10-17: Venezia vs Napoli (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.75 -> 🔴 LOST (Expected prob: 68.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.3% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 62.6% (Actual: 1 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 59.5% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 44.9% (Actual: 1 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 40.5% (Actual: BTTS-No)

### 2026-10-17: Austria Lustenau vs Lask Linz (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.369 -> 🟢 WON (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.8% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 61.4% (Actual: 4 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 55.2% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 44.8% (Actual: BTTS-No)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 42.0% (Actual: 4 goals)

### 2026-10-17: Bologna vs Inter (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.62 -> 🟢 WON (Expected prob: 62.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 62.2% (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 51.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 48.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 39.5% (Actual: 4 goals)

### 2026-10-17: Al Wihdat vs Al Hussein (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 2.3 -> 🔴 LOST (Expected prob: 61.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.5% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: Maringá vs Ferroviária (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 4.18 -> 🔴 LOST (Expected prob: 60.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 81.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 60.2% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 50.5% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.5% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 37.4% (Actual: 2 goals)

### 2026-10-17: Petrocub vs Dacia Buiucani (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 60.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: Doma United vs Kun Khalifat (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 60.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: VfL Wolfsburg vs 1. FC Heidenheim (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.67 -> 🟢 WON (Expected prob: 63.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 58.2% (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.4% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 47.6% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 36.0% (Actual: 4 goals)

### 2026-10-17: Broadmeadow Magic vs Wests APIA (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.4 -> 🔴 LOST (Expected prob: 61.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.0% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-17: Barrow vs Gloucester City (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 63.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.3% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 58.2% (Actual: 0 goals)


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

## Ambiguous result examples

- none

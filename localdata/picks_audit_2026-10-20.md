# Edge Factory — Recent picks audit (2026-09-21 to 2026-10-20)

## Overall

- archived pick rows: 668
- archived pick dates: 30
- immutable morning-baseline rows: 492
- late-slate additions (regular-ledger rows not in the morning baseline): 178, of which on days whose regular ledger was rewritten: 150
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 26
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 626
- eligible prior picks: 640
- pending/unmatched result picks: 11
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 21
- ambiguous result picks: 0
- wins: 437
- hit rate: +69.8%
- priced picks: 517
- ROI: +3.0%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-20
- same-day rows excluded: 28

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 374 / 626 matches (59.7%)
- **Both Teams to Score (BTTS)**: occurred in 325 / 626 matches (51.9%)
- **Selected Team Over 1.5 Goals**: occurred in 415 / 626 matches (66.3%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 597
- **Total Hits**: 470
- **Overall Hit Rate**: 78.7%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, settled=18, hit_rate=94.4%, priced_n=1, registry_processed=53, class=priced
- `away_under_15`: recommended=5, settled=5, hit_rate=100.0%, priced_n=5, registry_processed=5, class=priced
- `away_under_25`: recommended=3, settled=3, hit_rate=66.7%, priced_n=3, registry_processed=35, class=priced
- `away_under_35`: recommended=176, settled=176, hit_rate=96.6%, priced_n=1, registry_processed=305, class=priced
- `btts_no`: recommended=7, settled=7, hit_rate=42.9%, priced_n=7, registry_processed=7, class=priced
- `btts_yes`: recommended=5, settled=5, hit_rate=100.0%, priced_n=5, registry_processed=18, class=priced
- `home_over_05`: recommended=23, settled=23, hit_rate=87.0%, priced_n=1, registry_processed=186, class=priced
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced
- `home_under_35`: recommended=51, settled=51, hit_rate=98.0%, priced_n=0, registry_processed=74, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=23, settled=23, hit_rate=87.0%, priced_n=19, registry_processed=70, class=priced
- `match_over_25`: recommended=264, settled=264, hit_rate=60.6%, priced_n=188, registry_processed=689, class=priced
- `match_over_35`: recommended=18, settled=18, hit_rate=77.8%, priced_n=12, registry_processed=43, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2362** | scored: 2362

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 576 | 576 | 343 | 59.5% | 47.8% | +11.7% | 0.256749 |
| `match_over_45` | 407 | 407 | 90 | 22.1% | 24.0% | -1.9% | 0.172961 |
| `away_under_35` | 354 | 354 | 345 | 97.5% | 95.9% | +1.5% | 0.024882 |
| `away_under_25` | 340 | 340 | 314 | 92.4% | 89.8% | +2.6% | 0.071321 |
| `home_under_35` | 143 | 143 | 138 | 96.5% | 95.5% | +1.0% | 0.034544 |
| `match_over_35` | 116 | 116 | 61 | 52.6% | 43.2% | +9.3% | 0.269828 |
| `home_under_25` | 109 | 109 | 102 | 93.6% | 87.8% | +5.7% | 0.063804 |
| `btts_yes` | 87 | 87 | 51 | 58.6% | 46.9% | +11.7% | 0.24424 |
| `btts_no` | 81 | 81 | 36 | 44.4% | 54.1% | -9.6% | 0.250332 |
| `away_over_05` | 43 | 43 | 38 | 88.4% | 81.0% | +7.4% | 0.107863 |
| `away_under_15` | 39 | 39 | 29 | 74.4% | 82.1% | -7.7% | 0.195647 |
| `home_over_05` | 34 | 34 | 30 | 88.2% | 89.1% | -0.8% | 0.105948 |
| `match_over_15` | 27 | 27 | 22 | 81.5% | 84.8% | -3.3% | 0.152402 |
| `home_under_15` | 4 | 4 | 3 | 75.0% | 81.9% | -6.9% | 0.19469 ⚠️low-n |
| `double_chance` | 1 | 1 | 0 | 0.0% | 84.6% | -84.6% | 0.715598 ⚠️low-n |
| `home_over_15` | 1 | 1 | 1 | 100.0% | 81.9% | +18.1% | 0.032904 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2268 | 1529 | 67.4% | 63.8% | +3.6% | 0.150456 |
| model | 94 | 74 | 78.7% | 67.1% | +11.6% | 0.173829 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 75 | 19.1% | 24.0% | +4.9% |
| 0.2-0.3 | 296 | 24.2% | 20.6% | -3.6% |
| 0.3-0.4 | 106 | 35.4% | 48.1% | +12.7% |
| 0.4-0.5 | 551 | 44.8% | 57.2% | +12.3% |
| 0.5-0.6 | 171 | 53.7% | 53.2% | -0.5% |
| 0.6-0.7 | 45 | 63.7% | 64.4% | +0.8% |
| 0.7-0.8 | 23 | 72.7% | 69.6% | -3.1% |
| 0.8-0.9 | 443 | 86.9% | 89.6% | +2.8% |
| 0.9-1.0 | 652 | 94.7% | 95.9% | +1.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=624, MAE=1.579231 goals, bias=-0.389103 (realized − promised), promised avg 3.573397 vs realized 3.184295

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 624 | 30.7% | 32.7% | +2.0% | 0.194671 |
| BTTS-Yes | 624 | 41.0% | 51.8% | +10.8% | 0.263236 |
| Home Over 1.5 | 624 | 64.6% | 53.0% | -11.5% | 0.23229 |
| Over 2.5 | 624 | 69.9% | 59.6% | -10.3% | 0.249422 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 269 | 8.6% | 22.7% | +14.1% |
| 0.1-0.2 | 355 | 10.5% | 17.5% | +7.0% |
| 0.2-0.3 | 8 | 24.6% | 50.0% | +25.4% |
| 0.3-0.4 | 118 | 37.1% | 48.3% | +11.2% |
| 0.4-0.5 | 495 | 42.0% | 52.5% | +10.5% |
| 0.5-0.6 | 2 | 53.3% | 50.0% | -3.3% |
| 0.6-0.7 | 406 | 67.0% | 55.7% | -11.3% |
| 0.7-0.8 | 197 | 74.6% | 66.5% | -8.1% |
| 0.8-0.9 | 580 | 84.7% | 65.2% | -19.6% |
| 0.9-1.0 | 66 | 92.0% | 75.8% | -16.2% |

## By rule

- `2way-unanimous avg_p>=60`: settled=164, wins=106, hit_rate=0.646341, ROI=-0.097951
- `2way-unanimous avg_p>=70`: settled=26, wins=20, hit_rate=0.769231, ROI=-0.008421
- `ml-meta avg_p>=55`: settled=192, wins=140, hit_rate=0.729167, ROI=0.153795
- `ml-meta avg_p>=60`: settled=152, wins=93, hit_rate=0.611842, ROI=-0.037924
- `ml-meta avg_p>=65`: settled=22, wins=18, hit_rate=0.818182, ROI=-0.031875
- `ml-meta avg_p>=70`: settled=1, wins=0, hit_rate=0.0, ROI=-1.0
- `ml-meta avg_p>=80`: settled=7, wins=7, hit_rate=1.0, ROI=0.075
- `unanimous[betclan+vitibet] avg_p>=70`: settled=17, wins=16, hit_rate=0.941176, ROI=0.3409
- `unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65`: settled=1, wins=1, hit_rate=1.0, ROI=0.25
- `unanimous[bzzoiro+statarea+vitibet] avg_p>=65`: settled=4, wins=3, hit_rate=0.75, ROI=-0.1135
- `unanimous[bzzoiro+vitibet] avg_p>=70`: settled=13, wins=9, hit_rate=0.692308, ROI=-0.035815
- `unanimous[statarea+vitibet+zulubet] avg_p>=65`: settled=2, wins=1, hit_rate=0.5, ROI=-0.025
- `unanimous[statarea+vitibet] avg_p>=70`: settled=20, wins=18, hit_rate=0.9, ROI=0.16666
- `unanimous[vitibet+zulubet] avg_p>=70`: settled=5, wins=5, hit_rate=1.0, ROI=0.3925

## By bucket

- `CAUTION`: settled=47, wins=28, hit_rate=0.595745, ROI=-0.044719
- `CERTIFIED_CLEAN`: settled=88, wins=56, hit_rate=0.636364, ROI=0.016135
- `SKIPPED_VETO`: settled=335, wins=249, hit_rate=0.743284, ROI=0.059691
- `WATCHLIST_NO_ODDS`: settled=67, wins=43, hit_rate=0.641791, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=14, wins=8, hit_rate=0.571429, ROI=-0.068
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=69, wins=48, hit_rate=0.695652, ROI=-0.014783
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333, ROI=-0.001667

## By odds source

- `UNKNOWN`: settled=109, wins=73, hit_rate=0.669725, ROI=None
- `betexplorer_odds`: settled=177, wins=131, hit_rate=0.740113, ROI=0.004689
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=4, wins=4, hit_rate=1.0, ROI=0.4625
- `forebet_best`: settled=40, wins=28, hit_rate=0.7, ROI=0.0025
- `oddspapi_odds`: settled=6, wins=4, hit_rate=0.666667, ROI=0.0125
- `pinnapi_odds`: settled=58, wins=37, hit_rate=0.637931, ROI=0.089662
- `scoutingstats_odds`: settled=122, wins=84, hit_rate=0.688525, ROI=-0.02123
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=63, wins=48, hit_rate=0.761905, ROI=0.162222
- `zulubet`: settled=45, wins=26, hit_rate=0.577778, ROI=-0.035778

## By odds match method

- `alias_fuzzy`: settled=31, wins=20, hit_rate=0.645161, ROI=-0.039167
- `betexplorer`: settled=90, wins=63, hit_rate=0.7, ROI=-0.032222
- `exact`: settled=342, wins=247, hit_rate=0.722222, ROI=0.057738
- `fallback`: settled=61, wins=39, hit_rate=0.639344, ROI=-0.009344
- `none`: settled=102, wins=68, hit_rate=0.666667, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 90 | 63 | 0.7 | 90 | -0.032222 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 4 | 4 | 1.0 | 4 | 0.4625 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 215 | 158 | 0.734884 | 215 | 0.092867 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 122 | 84 | 0.688525 | 122 | -0.02123 |
| Source fallback (`SOURCE_FALLBACK`) | 61 | 39 | 0.639344 | 61 | -0.009344 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 31 | 20 | 0.645161 | 24 | -0.039167 |
| No usable price (`UNMATCHED`) | 102 | 68 | 0.666667 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 335 | 249 | 0.743284 | 297 | 0.059691 |
| **trusted evidence only** | 203 | 157 | 0.773399 | 203 | 0.095361 |
| **soft evidence only** | 132 | 92 | 0.69697 | 94 | -0.01734 |
| evidence: BETEXPLORER_RESCUE | 56 | 40 | 0.714286 | 56 | -0.052679 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.4 |
| evidence: NAMED_BOOKMAKER_PRICE | 144 | 114 | 0.791667 | 144 | 0.146585 |
| evidence: SCOUTINGSTATS_SOLE | 53 | 36 | 0.679245 | 53 | -0.029623 |
| evidence: SOURCE_FALLBACK | 27 | 19 | 0.703704 | 27 | 0.007407 |
| evidence: SUSPECT_ALIAS_FUZZY | 17 | 12 | 0.705882 | 14 | -0.018571 |
| evidence: UNMATCHED | 35 | 25 | 0.714286 | 0 | None |
| odds band: <1.50 | 191 | 151 | 0.790576 | 191 | -0.001328 |
| odds band: 1.50-2.00 | 88 | 60 | 0.681818 | 88 | 0.130931 |
| odds band: 2.00-3.00 | 14 | 9 | 0.642857 | 14 | 0.461429 |
| odds band: >=3.00 | 4 | 1 | 0.25 | 4 | 0.0 |
| odds band: unpriced | 38 | 28 | 0.736842 | 0 | None |
| veto reason: context VETO in ['competition_type'] | 40 | 34 | 0.85 | 31 | 0.142697 |
| veto reason: context VETO in ['league', 'niche'] | 2 | 2 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.3881 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 7 | 5 | 0.714286 | 6 | 0.188333 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.265 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 4 | 3 | 0.75 | 4 | 0.0725 |
| veto reason: context VETO in ['league'] | 26 | 15 | 0.576923 | 21 | -0.287619 |
| veto reason: context VETO in ['niche'] | 10 | 6 | 0.6 | 10 | -0.186 |
| veto reason: context VETO in ['odds_band'] | 57 | 39 | 0.684211 | 57 | -0.064912 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 6 | 5 | 0.833333 | 6 | 0.20035 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.212222 |
| veto reason: context VETO in ['team_a'] | 59 | 46 | 0.779661 | 50 | 0.195616 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 12 | 10 | 0.833333 | 11 | 0.066918 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 4 | 1.0 | 4 | 0.4775 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.098571 |
| veto reason: context VETO in ['team_h', 'team_a', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.62 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 13 | 0.764706 | 16 | 0.266519 |
| veto reason: context VETO in ['team_h'] | 47 | 34 | 0.723404 | 36 | 0.123889 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.08 | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: short-odds away favourite 1.16 | 2 | 2 | 1.0 | 2 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 18 | 9 | 0.5 | 18 | -0.2 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 19 | 14 | 0.736842 | 19 | 0.192537 |
| contrast CAUTION: SOURCE_FALLBACK | 10 | 5 | 0.5 | 10 | -0.216 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 453 | 321 | 0.708609 | 352 | 0.05141 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 31 | 20 | 0.645161 | 24 | -0.039167 | 31 | 1.645084 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 122 | 84 | 0.688525 | 122 | -0.02123 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 19 | 11 | 0.578947 | 19 | 0.040526 | 0 | None |
| stale_quote (`stale_quote`) | 1 | 1 | 1.0 | 0 | None | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-19: Bursaspor vs Pendikspor (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3937 -> 🟢 WON (Expected prob: 71.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 68.9% (Actual: 2 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 54.3% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.2% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.7% (Actual: BTTS-No)

### 2026-10-19: Mes Shahr-e Babak vs Persepolis FC (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.37 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.4% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 84.3% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 65.3% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 47.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.8% (Actual: 3 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| CANCELLED | 1 |
| POSTPONED | 2 |
- 2026-09-22 `POSTPONED` `SKIPPED_VETO` — MC Alger vs MC Oran (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-09-26 `POSTPONED` `SKIPPED_VETO` — Crawley Town vs Barnet (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-03 `CANCELLED` `CAUTION` — Sri Lanka vs Djibouti (source_status:scoutingstats); excluded from win/loss/ROI

## Rescheduled Fixture Examples

- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego 1904 [draw])
- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca (w) 4-1 Santos Laguna (w) [home])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ None (rescheduled → 2026-10-03; actual Tampa Bay Rowdies 1-2 Miami FC [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Brooklyn vs Rhode Island FC -> AWAY @ None (rescheduled → 2026-10-03; actual Brooklyn 1-3 Rhode Island [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kano Pillars FC vs Sporting Lagos -> HOME @ None (rescheduled → 2026-10-03; actual Kano Pillars 1-1 Sporting Lagos [draw])
- 2026-10-18 `SKIPPED_VETO` `unanimous[bzzoiro+vitibet] avg_p>=70` — Hartford Athletic vs Brooklyn -> HOME @ 1.44 (rescheduled → 2026-10-17; actual Hartford Athletic 2-3 Brooklyn [away])

## Pending / Unmatched Result Examples

- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Milevsko vs Spartak Sobeslav -> AWAY @ 1.57 (pending_or_unmatched_result); keys=['milevsko']/['spartakso']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Polanka nad Odrou vs Frydek-Mistek -> AWAY @ 1.48 (pending_or_unmatched_result); keys=['polankana']/['frydekmis']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Brommapojkarna W vs Malmö FF W -> AWAY @ 1.4 (pending_or_unmatched_result); keys=['brommapoj']/['malmoff', 'malmoffww']
- 2026-09-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — Plateau United vs Inter Lagos -> HOME @ 1.33 (pending_or_unmatched_result); keys=['plateauun']/['interlago']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Rheindorf Altach II vs Hohenems -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['hohenems']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kufstein vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['kufstein']/['imst']
- 2026-10-09 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Real Cundinamarca vs Real Santander -> HOME @ None (pending_or_unmatched_result); keys=['cundinama']/['santander']
- 2026-10-11 `SKIPPED_VETO` `ml-meta avg_p>=60` — Atletico Nacional vs Deportivo Pasto -> HOME @ 2.1 (pending_or_unmatched_result); keys=['nacional']/['pasto']
- 2026-10-11 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Ranger's vs Carroi -> HOME @ None (pending_or_unmatched_result); keys=['rangers']/['carroi']
- 2026-10-18 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Wolfurt vs Schwaz -> AWAY @ None (pending_or_unmatched_result); keys=['wolfurt']/['schwaz']
- 2026-10-18 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Rheindorf Altach II vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['imst']

## Ambiguous result examples

- none

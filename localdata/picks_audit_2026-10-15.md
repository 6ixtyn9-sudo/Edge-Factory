# Edge Factory — Recent picks audit (2026-09-16 to 2026-10-15)

## Overall

- archived pick rows: 567
- archived pick dates: 30
- immutable morning-baseline rows: 564
- verified official late-slate additions: 5
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 536
- eligible prior picks: 553
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 5
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 379
- hit rate: +70.7%
- priced picks: 450
- ROI: +4.5%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-15
- same-day rows excluded: 14

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 326 / 536 matches (60.8%)
- **Both Teams to Score (BTTS)**: occurred in 279 / 536 matches (52.1%)
- **Selected Team Over 1.5 Goals**: occurred in 356 / 536 matches (66.4%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 534
- **Total Hits**: 439
- **Overall Hit Rate**: 82.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=12, settled=12, hit_rate=91.7%, priced_n=0, registry_processed=47, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `away_under_25`: recommended=25, settled=25, hit_rate=96.0%, priced_n=2, registry_processed=26, class=priced
- `away_under_35`: recommended=170, settled=170, hit_rate=97.6%, priced_n=1, registry_processed=252, class=priced
- `btts_no`: recommended=2, settled=2, hit_rate=50.0%, priced_n=2, registry_processed=2, class=priced
- `home_over_05`: recommended=18, settled=18, hit_rate=83.3%, priced_n=0, registry_processed=181, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_15`: recommended=1, settled=1, hit_rate=100.0%, priced_n=1, registry_processed=1, class=priced
- `home_under_25`: recommended=32, settled=32, hit_rate=93.8%, priced_n=0, registry_processed=36, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_35`: recommended=38, settled=38, hit_rate=97.4%, priced_n=0, registry_processed=56, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=14, settled=14, hit_rate=92.9%, priced_n=12, registry_processed=61, class=priced
- `match_over_25`: recommended=211, settled=211, hit_rate=62.6%, priced_n=133, registry_processed=577, class=priced
- `match_over_35`: recommended=10, settled=10, hit_rate=80.0%, priced_n=8, registry_processed=35, class=priced
- `match_over_45`: recommended=1, settled=1, hit_rate=100.0%, priced_n=1, registry_processed=1, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2072** | scored: 2072

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 523 | 523 | 315 | 60.2% | 45.1% | +15.2% | 0.262565 |
| `match_over_45` | 417 | 417 | 97 | 23.3% | 23.8% | -0.5% | 0.176116 |
| `away_under_35` | 365 | 365 | 358 | 98.1% | 95.2% | +2.9% | 0.020239 |
| `away_under_25` | 342 | 342 | 315 | 92.1% | 90.2% | +1.9% | 0.072921 |
| `home_under_35` | 138 | 138 | 134 | 97.1% | 94.5% | +2.6% | 0.030907 |
| `home_under_25` | 124 | 124 | 115 | 92.7% | 89.1% | +3.7% | 0.068715 |
| `away_over_05` | 33 | 33 | 29 | 87.9% | 80.7% | +7.2% | 0.111227 |
| `away_under_15` | 32 | 32 | 23 | 71.9% | 82.0% | -10.2% | 0.212233 |
| `match_over_35` | 30 | 30 | 21 | 70.0% | 43.0% | +27.0% | 0.307402 |
| `home_over_05` | 27 | 27 | 23 | 85.2% | 88.9% | -3.8% | 0.130426 |
| `match_over_15` | 17 | 17 | 14 | 82.4% | 85.0% | -2.7% | 0.139906 |
| `btts_no` | 9 | 9 | 6 | 66.7% | 53.2% | +13.5% | 0.239286 |
| `btts_yes` | 9 | 9 | 3 | 33.3% | 47.4% | -14.0% | 0.23413 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |
| `home_under_15` | 3 | 3 | 2 | 66.7% | 81.9% | -15.3% | 0.248507 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1983 | 1392 | 70.2% | 65.2% | +5.0% | 0.137601 |
| model | 89 | 65 | 73.0% | 63.9% | +9.1% | 0.1615 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 89 | 19.1% | 18.0% | -1.2% |
| 0.2-0.3 | 289 | 24.2% | 23.2% | -1.0% |
| 0.3-0.4 | 64 | 33.8% | 51.6% | +17.7% |
| 0.4-0.5 | 475 | 44.4% | 58.9% | +14.6% |
| 0.5-0.6 | 66 | 52.1% | 66.7% | +14.6% |
| 0.6-0.7 | 3 | 60.5% | 33.3% | -27.1% |
| 0.7-0.8 | 2 | 72.3% | 50.0% | -22.3% |
| 0.8-0.9 | 363 | 86.9% | 88.7% | +1.8% |
| 0.9-1.0 | 721 | 94.0% | 96.1% | +2.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=534, MAE=1.565936 goals, bias=-0.314813 (realized − promised), promised avg 3.539532 vs realized 3.224719

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 534 | 30.8% | 33.1% | +2.3% | 0.195027 |
| BTTS-Yes | 534 | 41.3% | 51.9% | +10.6% | 0.260448 |
| Home Over 1.5 | 534 | 64.1% | 53.0% | -11.1% | 0.232664 |
| Over 2.5 | 534 | 69.6% | 60.7% | -8.9% | 0.246596 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 223 | 8.6% | 21.5% | +13.0% |
| 0.1-0.2 | 312 | 10.4% | 18.9% | +8.5% |
| 0.2-0.3 | 6 | 27.1% | 66.7% | +39.6% |
| 0.3-0.4 | 98 | 37.3% | 46.9% | +9.7% |
| 0.4-0.5 | 427 | 42.4% | 52.7% | +10.3% |
| 0.5-0.6 | 2 | 53.3% | 50.0% | -3.3% |
| 0.6-0.7 | 360 | 66.9% | 58.9% | -8.0% |
| 0.7-0.8 | 157 | 74.3% | 64.3% | -10.0% |
| 0.8-0.9 | 503 | 84.6% | 65.4% | -19.2% |
| 0.9-1.0 | 48 | 92.3% | 75.0% | -17.3% |

## By rule

- `2way-unanimous avg_p>=60`: settled=130, wins=81, hit_rate=0.623077, ROI=-0.142371
- `2way-unanimous avg_p>=70`: settled=52, wins=43, hit_rate=0.826923, ROI=0.049167
- `ml-meta avg_p>=55`: settled=222, wins=156, hit_rate=0.702703, ROI=0.133731
- `ml-meta avg_p>=60`: settled=83, wins=58, hit_rate=0.698795, ROI=0.044162
- `ml-meta avg_p>=65`: settled=20, wins=16, hit_rate=0.8, ROI=-0.03
- `ml-meta avg_p>=70`: settled=2, wins=1, hit_rate=0.5, ROI=-0.47
- `ml-meta avg_p>=80`: settled=9, wins=9, hit_rate=1.0, ROI=0.08375
- `unanimous[betclan+vitibet] avg_p>=70`: settled=8, wins=7, hit_rate=0.875, ROI=0.072
- `unanimous[bzzoiro+vitibet] avg_p>=70`: settled=5, wins=5, hit_rate=1.0, ROI=0.47
- `unanimous[statarea+vitibet] avg_p>=70`: settled=3, wins=1, hit_rate=0.333333, ROI=-0.203333
- `unanimous[vitibet+zulubet] avg_p>=70`: settled=2, wins=2, hit_rate=1.0, ROI=0.40125

## By bucket

- `CAUTION`: settled=39, wins=22, hit_rate=0.564103, ROI=-0.089728
- `CERTIFIED_CLEAN`: settled=77, wins=52, hit_rate=0.675325, ROI=0.09844
- `SKIPPED_VETO`: settled=266, wins=199, hit_rate=0.74812, ROI=0.065388
- `WATCHLIST_NO_ODDS`: settled=59, wins=39, hit_rate=0.661017, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=4, wins=3, hit_rate=0.75, ROI=0.025
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=87, wins=61, hit_rate=0.701149, ROI=0.008276
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=86, wins=59, hit_rate=0.686047, ROI=None
- `betexplorer_odds`: settled=144, wins=103, hit_rate=0.715278, ROI=-0.003125
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=42, wins=29, hit_rate=0.690476, ROI=0.032143
- `oddspapi_odds`: settled=3, wins=2, hit_rate=0.666667, ROI=0.101667
- `pinnapi_odds`: settled=23, wins=15, hit_rate=0.652174, ROI=0.184483
- `scoutingstats_odds`: settled=165, wins=115, hit_rate=0.69697, ROI=0.014909
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=40, wins=33, hit_rate=0.825, ROI=0.2575
- `zulubet`: settled=23, wins=14, hit_rate=0.608696, ROI=-0.058696

## By odds match method

- `alias_fuzzy`: settled=15, wins=11, hit_rate=0.733333, ROI=-0.001667
- `betexplorer`: settled=100, wins=68, hit_rate=0.68, ROI=-0.031
- `exact`: settled=285, wins=209, hit_rate=0.733333, ROI=0.082067
- `fallback`: settled=53, wins=35, hit_rate=0.660377, ROI=0.000377
- `none`: settled=83, wins=56, hit_rate=0.674699, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 100 | 68 | 0.68 | 100 | -0.031 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 111 | 86 | 0.774775 | 111 | 0.164316 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 165 | 115 | 0.69697 | 165 | 0.014909 |
| Source fallback (`SOURCE_FALLBACK`) | 53 | 35 | 0.660377 | 53 | 0.000377 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 15 | 11 | 0.733333 | 12 | -0.001667 |
| No usable price (`UNMATCHED`) | 83 | 56 | 0.674699 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 266 | 199 | 0.74812 | 241 | 0.065388 |
| **trusted evidence only** | 133 | 104 | 0.781955 | 133 | 0.089839 |
| **soft evidence only** | 133 | 95 | 0.714286 | 108 | 0.035278 |
| evidence: BETEXPLORER_RESCUE | 59 | 42 | 0.711864 | 59 | -0.052542 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 69 | 57 | 0.826087 | 69 | 0.18882 |
| evidence: SCOUTINGSTATS_SOLE | 78 | 54 | 0.692308 | 78 | 0.022308 |
| evidence: SOURCE_FALLBACK | 20 | 16 | 0.8 | 20 | 0.107 |
| evidence: SUSPECT_ALIAS_FUZZY | 11 | 8 | 0.727273 | 10 | -0.007 |
| evidence: UNMATCHED | 24 | 17 | 0.708333 | 0 | None |
| odds band: <1.50 | 146 | 118 | 0.808219 | 146 | 0.014974 |
| odds band: 1.50-2.00 | 86 | 56 | 0.651163 | 86 | 0.08433 |
| odds band: 2.00-3.00 | 9 | 7 | 0.777778 | 9 | 0.702222 |
| odds band: unpriced | 25 | 18 | 0.72 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['competition_type'] | 12 | 10 | 0.833333 | 9 | 0.238889 |
| veto reason: context VETO in ['league', 'niche'] | 2 | 1 | 0.5 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 4 | 1 | 0.25 | 4 | -0.585 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.2762 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 4 | 3 | 0.75 | 4 | 0.015 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h'] | 6 | 5 | 0.833333 | 6 | 0.166667 |
| veto reason: context VETO in ['league'] | 24 | 17 | 0.708333 | 20 | -0.0045 |
| veto reason: context VETO in ['niche'] | 11 | 8 | 0.727273 | 11 | 0.01 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.32 |
| veto reason: context VETO in ['odds_band'] | 47 | 36 | 0.765957 | 47 | -0.020851 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 3 | 2 | 0.666667 | 3 | -0.084567 |
| veto reason: context VETO in ['team_a', 'niche'] | 4 | 3 | 0.75 | 4 | 0.3175 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 12 | 10 | 0.833333 | 12 | 0.015 |
| veto reason: context VETO in ['team_a'] | 51 | 37 | 0.72549 | 44 | 0.122639 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.365 |
| veto reason: context VETO in ['team_h', 'niche'] | 2 | 2 | 1.0 | 2 | 0.29 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.054286 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.44 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.32 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 13 | 0.764706 | 16 | 0.260625 |
| veto reason: context VETO in ['team_h'] | 42 | 31 | 0.738095 | 33 | 0.143636 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 16 | 8 | 0.5 | 16 | -0.204375 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 12 | 10 | 0.833333 | 12 | 0.389217 |
| contrast CAUTION: SOURCE_FALLBACK | 10 | 4 | 0.4 | 10 | -0.39 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 345 | 246 | 0.713043 | 262 | 0.065111 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 15 | 11 | 0.733333 | 12 | -0.001667 | 15 | 1.602367 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 165 | 115 | 0.69697 | 165 | 0.014909 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 11 | 7 | 0.636364 | 11 | 0.071818 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-14: Atletico Mineiro vs Montevideo City Torque (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3205 -> 🟢 WON (Expected prob: 73.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 86.6% (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 71.6% (Actual: 3 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 54.6% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 49.8% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.4% (Actual: BTTS-No)

### 2026-10-14: Kheybar Khorramabad vs Persepolis FC (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.51 -> 🔴 LOST (Expected prob: 64.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.9% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.3% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-14: CS Cartagines vs Puntarenas FC (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.54 -> 🟢 WON (Expected prob: 62.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 32.5% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.6% (Actual: 4 goals)

### 2026-10-14: Mito Hollyhock vs FC Tokyo (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.89 -> 🔴 LOST (Expected prob: 66.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 82.5% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 81.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 60.6% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 42.5% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.7% (Actual: 1 goals)

### 2026-10-14: Spartakos Kitiou vs Digenis Ypsonas (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.94 -> 🟢 WON (Expected prob: 66.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-14: Stabaek vs Sandnes ULF (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 64.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.2% (Actual: 5 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 36.8% (Actual: 5 goals)

### 2026-10-14: Stromsgodset vs Kongsvinger (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.77 -> 🟢 WON (Expected prob: 62.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 51.5% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.1% (Actual: 6 goals)

### 2026-10-14: Dukagjini vs Vushtrria (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.15 -> 🟢 WON (Expected prob: 81.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 94.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 55.7% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 44.3% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.4% (Actual: 1 goals)

### 2026-10-14: Lask Linz vs Liverpool (Actual Score: **3-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.2762 -> 🟢 WON (Expected prob: 76.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.4% (Actual: 9 goals)
  - [🔴 MISS] **BTTS-No**: expected 33.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 94.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 92.0% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 87.1% (Actual: 6 away goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 53.2% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.1% (Actual: 9 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 30.9% (Actual: 9 goals)

### 2026-10-14: Junior vs Deportivo Pereira (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🔴 LOST (Expected prob: 74.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.6% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 72.9% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 53.6% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.6% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.4% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 34.7% (Actual: 2 goals)

### 2026-10-14: Lincoln vs West Ham (Actual Score: **0-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.73 -> 🟢 WON (Expected prob: 66.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.7% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.1% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 60.6% (Actual: 6 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 56.4% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 43.6% (Actual: BTTS-No)

### 2026-10-14: Aston Villa vs Fenerbahçe (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ 1.76 -> 🟢 WON (Expected prob: 60.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.0% (Actual: 6 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.0% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.0% (Actual: BTTS-No)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 33.9% (Actual: 6 goals)

### 2026-10-14: Bodo/Glimt vs Borussia Dortmund (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 2.05 -> 🔴 LOST (Expected prob: 61.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 60.2% (Actual: 1 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.1% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 48.9% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 37.2% (Actual: 1 goals)

### 2026-10-14: Trans Narva vs Kuressaare (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.96 -> 🔴 LOST (Expected prob: 60.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 56.2% (Actual: 1 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 51.0% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.0% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 34.5% (Actual: 1 goals)


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
- 2026-10-14 `SKIPPED_VETO` `ml-meta avg_p>=60` — Slovan Bratislava vs VfB Stuttgart (ambiguous_alias_result)

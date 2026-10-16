# Edge Factory — Recent picks audit (2026-09-17 to 2026-10-16)

## Overall

- archived pick rows: 720
- archived pick dates: 30
- immutable morning-baseline rows: 554
- late-slate additions (regular-ledger rows not in the morning baseline): 168, of which on days whose regular ledger was rewritten: 163
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 699
- eligible prior picks: 713
- pending/unmatched result picks: 12
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 489
- hit rate: +70.0%
- priced picks: 589
- ROI: +4.2%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-16
- same-day rows excluded: 7

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 424 / 699 matches (60.7%)
- **Both Teams to Score (BTTS)**: occurred in 373 / 699 matches (53.4%)
- **Selected Team Over 1.5 Goals**: occurred in 462 / 699 matches (66.1%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 695
- **Total Hits**: 572
- **Overall Hit Rate**: 82.3%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, settled=18, hit_rate=94.4%, priced_n=1, registry_processed=53, class=priced
- `away_under_15`: recommended=1, settled=1, hit_rate=100.0%, priced_n=1, registry_processed=1, class=priced
- `away_under_25`: recommended=32, settled=32, hit_rate=96.9%, priced_n=3, registry_processed=35, class=priced
- `away_under_35`: recommended=220, settled=220, hit_rate=97.3%, priced_n=1, registry_processed=305, class=priced
- `btts_no`: recommended=3, settled=3, hit_rate=66.7%, priced_n=3, registry_processed=3, class=priced
- `btts_yes`: recommended=1, settled=1, hit_rate=100.0%, priced_n=1, registry_processed=14, class=priced
- `home_over_05`: recommended=23, settled=23, hit_rate=87.0%, priced_n=1, registry_processed=186, class=priced
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced
- `home_under_25`: recommended=33, settled=33, hit_rate=93.9%, priced_n=0, registry_processed=40, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_35`: recommended=54, settled=54, hit_rate=98.1%, priced_n=0, registry_processed=73, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=17, settled=17, hit_rate=88.2%, priced_n=13, registry_processed=64, class=priced
- `match_over_25`: recommended=272, settled=272, hit_rate=62.5%, priced_n=175, registry_processed=643, class=priced
- `match_over_35`: recommended=17, settled=17, hit_rate=76.5%, priced_n=11, registry_processed=42, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2714** | scored: 2714

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 680 | 680 | 409 | 60.1% | 45.6% | +14.5% | 0.26087 |
| `match_over_45` | 532 | 532 | 120 | 22.6% | 23.7% | -1.2% | 0.174019 |
| `away_under_35` | 461 | 461 | 452 | 98.0% | 95.3% | +2.8% | 0.020212 |
| `away_under_25` | 432 | 432 | 401 | 92.8% | 90.2% | +2.6% | 0.067448 |
| `home_under_35` | 182 | 182 | 177 | 97.3% | 94.5% | +2.8% | 0.029029 |
| `home_under_25` | 157 | 157 | 145 | 92.4% | 88.9% | +3.5% | 0.072163 |
| `match_over_35` | 64 | 64 | 35 | 54.7% | 42.0% | +12.7% | 0.270296 |
| `away_over_05` | 44 | 44 | 39 | 88.6% | 81.0% | +7.7% | 0.106313 |
| `away_under_15` | 37 | 37 | 27 | 73.0% | 82.0% | -9.1% | 0.20467 |
| `home_over_05` | 34 | 34 | 30 | 88.2% | 89.1% | -0.8% | 0.105948 |
| `btts_yes` | 30 | 30 | 18 | 60.0% | 46.7% | +13.3% | 0.25102 |
| `btts_no` | 28 | 28 | 12 | 42.9% | 53.9% | -11.0% | 0.254563 |
| `match_over_15` | 21 | 21 | 17 | 81.0% | 85.0% | -4.1% | 0.153634 |
| `double_chance` | 6 | 6 | 5 | 83.3% | 85.0% | -1.6% | 0.138534 |
| `home_under_15` | 5 | 5 | 4 | 80.0% | 81.7% | -1.7% | 0.163042 |
| `home_over_15` | 1 | 1 | 1 | 100.0% | 81.9% | +18.1% | 0.032904 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2616 | 1817 | 69.5% | 64.7% | +4.8% | 0.137873 |
| model | 98 | 75 | 76.5% | 66.5% | +10.1% | 0.174276 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 116 | 19.2% | 20.7% | +1.5% |
| 0.2-0.3 | 369 | 24.1% | 22.0% | -2.1% |
| 0.3-0.4 | 100 | 34.5% | 47.0% | +12.5% |
| 0.4-0.5 | 621 | 44.4% | 58.6% | +14.2% |
| 0.5-0.6 | 107 | 53.0% | 59.8% | +6.8% |
| 0.6-0.7 | 13 | 62.8% | 61.5% | -1.3% |
| 0.7-0.8 | 8 | 73.1% | 75.0% | +1.9% |
| 0.8-0.9 | 470 | 86.9% | 90.0% | +3.1% |
| 0.9-1.0 | 910 | 94.1% | 96.2% | +2.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=697, MAE=1.528723 goals, bias=-0.320373 (realized − promised), promised avg 3.537016 vs realized 3.216643

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 697 | 31.2% | 32.3% | +1.1% | 0.196841 |
| BTTS-Yes | 697 | 41.4% | 53.2% | +11.9% | 0.264343 |
| Home Over 1.5 | 697 | 63.8% | 53.5% | -10.2% | 0.231786 |
| Over 2.5 | 697 | 69.6% | 60.5% | -9.0% | 0.245599 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 289 | 8.6% | 21.8% | +13.2% |
| 0.1-0.2 | 408 | 10.5% | 18.6% | +8.2% |
| 0.2-0.3 | 9 | 24.8% | 55.6% | +30.7% |
| 0.3-0.4 | 119 | 37.1% | 51.3% | +14.1% |
| 0.4-0.5 | 566 | 42.4% | 53.5% | +11.1% |
| 0.5-0.6 | 2 | 53.3% | 50.0% | -3.3% |
| 0.6-0.7 | 475 | 66.9% | 58.3% | -8.5% |
| 0.7-0.8 | 200 | 74.4% | 64.5% | -9.9% |
| 0.8-0.9 | 657 | 84.5% | 64.7% | -19.9% |
| 0.9-1.0 | 63 | 92.2% | 81.0% | -11.3% |

## By rule

- `2way-unanimous avg_p>=60`: settled=164, wins=106, hit_rate=0.646341, ROI=-0.097951
- `2way-unanimous avg_p>=70`: settled=64, wins=51, hit_rate=0.796875, ROI=0.047273
- `ml-meta avg_p>=55`: settled=286, wins=195, hit_rate=0.681818, ROI=0.085954
- `ml-meta avg_p>=60`: settled=126, wins=86, hit_rate=0.68254, ROI=0.057517
- `ml-meta avg_p>=65`: settled=25, wins=21, hit_rate=0.84, ROI=0.013158
- `ml-meta avg_p>=70`: settled=1, wins=0, hit_rate=0.0, ROI=-1.0
- `ml-meta avg_p>=80`: settled=8, wins=8, hit_rate=1.0, ROI=0.067143
- `unanimous[betclan+vitibet] avg_p>=70`: settled=11, wins=10, hit_rate=0.909091, ROI=0.360212
- `unanimous[bzzoiro+vitibet] avg_p>=70`: settled=6, wins=6, hit_rate=1.0, ROI=0.4283
- `unanimous[statarea+vitibet] avg_p>=70`: settled=4, wins=2, hit_rate=0.5, ROI=-0.1028
- `unanimous[vitibet+zulubet] avg_p>=70`: settled=4, wins=4, hit_rate=1.0, ROI=0.260625

## By bucket

- `CAUTION`: settled=52, wins=30, hit_rate=0.576923, ROI=-0.087727
- `CERTIFIED_CLEAN`: settled=101, wins=67, hit_rate=0.663366, ROI=0.068118
- `SKIPPED_VETO`: settled=346, wins=254, hit_rate=0.734104, ROI=0.066517
- `WATCHLIST_NO_ODDS`: settled=74, wins=50, hit_rate=0.675676, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=12, wins=7, hit_rate=0.583333, ROI=-0.051429
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=108, wins=76, hit_rate=0.703704, ROI=0.017407
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333, ROI=-0.001667

## By odds source

- `UNKNOWN`: settled=110, wins=74, hit_rate=0.672727, ROI=None
- `betexplorer_odds`: settled=202, wins=144, hit_rate=0.712871, ROI=-0.013812
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=6, wins=5, hit_rate=0.833333, ROI=0.191667
- `forebet_best`: settled=54, wins=38, hit_rate=0.703704, ROI=0.03537
- `oddspapi_odds`: settled=5, wins=3, hit_rate=0.6, ROI=-0.059
- `pinnapi_odds`: settled=40, wins=26, hit_rate=0.65, ROI=0.204122
- `scoutingstats_odds`: settled=197, wins=137, hit_rate=0.695431, ROI=0.018071
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=46, wins=38, hit_rate=0.826087, ROI=0.272609
- `zulubet`: settled=37, wins=22, hit_rate=0.594595, ROI=-0.019459

## By odds match method

- `alias_fuzzy`: settled=29, wins=18, hit_rate=0.62069, ROI=-0.04
- `betexplorer`: settled=137, wins=93, hit_rate=0.678832, ROI=-0.036642
- `exact`: settled=361, wins=262, hit_rate=0.725762, ROI=0.079255
- `fallback`: settled=68, wins=46, hit_rate=0.676471, ROI=0.031029
- `none`: settled=104, wins=70, hit_rate=0.673077, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 137 | 93 | 0.678832 | 137 | -0.036642 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 6 | 5 | 0.833333 | 6 | 0.191667 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 157 | 119 | 0.757962 | 157 | 0.148923 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 197 | 137 | 0.695431 | 197 | 0.018071 |
| Source fallback (`SOURCE_FALLBACK`) | 68 | 46 | 0.676471 | 68 | 0.031029 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 29 | 18 | 0.62069 | 23 | -0.04 |
| No usable price (`UNMATCHED`) | 104 | 70 | 0.673077 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 346 | 254 | 0.734104 | 315 | 0.066517 |
| **trusted evidence only** | 180 | 140 | 0.777778 | 180 | 0.104682 |
| **soft evidence only** | 166 | 114 | 0.686747 | 135 | 0.01563 |
| evidence: BETEXPLORER_RESCUE | 76 | 54 | 0.710526 | 76 | -0.059868 |
| evidence: BZZOIRO_PRIMARY | 4 | 4 | 1.0 | 4 | 0.375 |
| evidence: NAMED_BOOKMAKER_PRICE | 100 | 82 | 0.82 | 100 | 0.218928 |
| evidence: SCOUTINGSTATS_SOLE | 89 | 61 | 0.685393 | 89 | 0.018876 |
| evidence: SOURCE_FALLBACK | 30 | 22 | 0.733333 | 30 | 0.033 |
| evidence: SUSPECT_ALIAS_FUZZY | 17 | 11 | 0.647059 | 16 | -0.035 |
| evidence: UNMATCHED | 30 | 20 | 0.666667 | 0 | None |
| odds band: <1.50 | 189 | 152 | 0.804233 | 189 | 0.014207 |
| odds band: 1.50-2.00 | 109 | 68 | 0.623853 | 109 | 0.038602 |
| odds band: 2.00-3.00 | 16 | 12 | 0.75 | 16 | 0.69125 |
| odds band: >=3.00 | 1 | 1 | 1.0 | 1 | 3.0 |
| odds band: unpriced | 31 | 21 | 0.677419 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['competition_type'] | 16 | 14 | 0.875 | 13 | 0.354523 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.335 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_a'] | 6 | 1 | 0.166667 | 6 | -0.723333 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.2762 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 5 | 3 | 0.6 | 5 | -0.188 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.26 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 5 | 4 | 0.8 | 5 | 0.09 |
| veto reason: context VETO in ['league'] | 29 | 20 | 0.689655 | 24 | -0.072083 |
| veto reason: context VETO in ['niche'] | 15 | 10 | 0.666667 | 14 | 0.012857 |
| veto reason: context VETO in ['odds_band'] | 65 | 47 | 0.723077 | 65 | -0.027692 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 3 | 2 | 0.666667 | 3 | -0.084567 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 12 | 10 | 0.833333 | 12 | 0.113333 |
| veto reason: context VETO in ['team_a'] | 68 | 49 | 0.720588 | 59 | 0.098217 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 5 | 5 | 1.0 | 5 | 0.2903 |
| veto reason: context VETO in ['team_h', 'niche'] | 5 | 4 | 0.8 | 5 | 0.13 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 8 | 6 | 0.75 | 8 | -0.04125 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.44 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.13 |
| veto reason: context VETO in ['team_h', 'team_a'] | 20 | 16 | 0.8 | 19 | 0.341579 |
| veto reason: context VETO in ['team_h'] | 55 | 39 | 0.709091 | 44 | 0.152273 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.08 | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: short-odds away favourite 1.16 | 2 | 2 | 1.0 | 2 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 23 | 12 | 0.521739 | 23 | -0.183478 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 17 | 13 | 0.764706 | 17 | 0.250482 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.327273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 459 | 325 | 0.708061 | 355 | 0.055834 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 29 | 18 | 0.62069 | 23 | -0.04 | 29 | 1.6224 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 197 | 137 | 0.695431 | 197 | 0.018071 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 14 | 9 | 0.642857 | 14 | 0.165714 | 0 | None |
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

### 2026-10-15: NEC Nijmegen vs Levski Sofia (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.9091 -> 🔴 LOST (Expected prob: 60.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 56.0% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 51.0% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.0% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 33.9% (Actual: 2 goals)

### 2026-10-15: Marquense vs Mixco (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 4.59 -> 🔴 LOST (Expected prob: 60.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 89.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 80.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 59.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 36.3% (Actual: 2 goals)

### 2026-10-15: St. Truiden vs FC Iberia 1999 (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.21 -> 🟢 WON (Expected prob: 76.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 74.1% (Actual: 2 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 56.5% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 43.5% (Actual: BTTS-No)

### 2026-10-15: Brighton vs Kauno Žalgiris (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.03 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 53.8% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.2% (Actual: BTTS-No)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 45.7% (Actual: 4 goals)

### 2026-10-15: Dinamo Minsk vs Slavia Mozyr (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4717 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-15: Torreense vs Sunderland (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🟢 WON (Expected prob: 60.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.8% (Actual: 3 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 50.1% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 35.7% (Actual: 3 goals)

### 2026-10-15: LD Alajuelense vs CS Herediano (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 60.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-15: Egnatia Rrogozhinë vs FC Midtjylland (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.5348 -> 🔴 LOST (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 61.1% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 51.8% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 48.2% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 38.8% (Actual: 2 goals)

### 2026-10-15: Caen vs La Roche VF (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 2.26 -> 🟢 WON (Expected prob: 60.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.2% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 51.0% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 49.0% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 34.5% (Actual: 3 goals)


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

- 2026-09-18 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Wiener SC vs Leobendorf (ambiguous_alias_result)
- 2026-10-10 `SKIPPED_VETO` `ml-meta avg_p>=60` — Brusque vs Paysandu (ambiguous_alias_result)

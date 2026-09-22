# Edge Factory — Recent picks audit (2026-08-24 to 2026-09-22)

## Overall

- archived pick rows: 597
- archived pick dates: 30
- immutable morning-baseline rows: 597
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 30
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 576
- eligible prior picks: 593
- pending/unmatched result picks: 5
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 382
- hit rate: +66.3%
- priced picks: 538
- ROI: -3.9%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-22
- same-day rows excluded: 4

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 338 / 530 matches (63.8%)
- **Both Teams to Score (BTTS)**: occurred in 302 / 530 matches (57.0%)
- **Selected Team Over 1.5 Goals**: occurred in 347 / 530 matches (65.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 576
- **Total Hits**: 443
- **Overall Hit Rate**: 76.9%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=109, hits=105, hit_rate=96.3%
- `home_over_05`: recommended=36, hits=27, hit_rate=75.0%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=12, hits=11, hit_rate=91.7%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=283, hits=188, hit_rate=66.4%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2414** | scored: 2414

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 569 | 569 | 361 | 63.4% | 46.2% | +17.3% | 0.260577 |
| `match_over_45` | 440 | 440 | 123 | 28.0% | 23.8% | +4.1% | 0.200517 |
| `away_under_35` | 408 | 408 | 397 | 97.3% | 96.4% | +1.0% | 0.026299 |
| `away_under_25` | 370 | 370 | 341 | 92.2% | 93.1% | -0.9% | 0.072891 |
| `home_over_05` | 179 | 179 | 157 | 87.7% | 84.1% | +3.6% | 0.109351 |
| `home_under_35` | 157 | 157 | 153 | 97.5% | 95.0% | +2.4% | 0.025979 |
| `home_under_25` | 133 | 133 | 121 | 91.0% | 91.8% | -0.8% | 0.081017 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `away_under_15` | 34 | 34 | 25 | 73.5% | 81.0% | -7.5% | 0.20375 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 30 | 30 | 27 | 90.0% | 88.4% | +1.6% | 0.088004 |
| `home_under_15` | 15 | 15 | 11 | 73.3% | 81.4% | -8.1% | 0.206155 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2157 | 1585 | 73.5% | 68.6% | +4.8% | 0.136328 |
| model | 257 | 182 | 70.8% | 63.8% | +7.0% | 0.171799 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 128 | 19.2% | 21.1% | +1.9% |
| 0.2-0.3 | 263 | 24.6% | 29.3% | +4.6% |
| 0.3-0.4 | 82 | 33.2% | 46.3% | +13.1% |
| 0.4-0.5 | 456 | 44.7% | 62.1% | +17.4% |
| 0.5-0.6 | 113 | 52.7% | 65.5% | +12.8% |
| 0.8-0.9 | 341 | 84.4% | 85.3% | +0.9% |
| 0.9-1.0 | 1031 | 94.8% | 94.8% | -0.0% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=530, MAE=1.584321 goals, bias=-0.169717 (realized − promised), promised avg 3.513113 vs realized 3.343396

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 530 | 30.5% | 35.7% | +5.2% | 0.237827 |
| BTTS-Yes | 530 | 41.8% | 57.0% | +15.1% | 0.269162 |
| Home Over 1.5 | 530 | 64.5% | 56.8% | -7.7% | 0.251245 |
| Over 2.5 | 530 | 69.6% | 63.8% | -5.8% | 0.23317 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 223 | 8.9% | 26.9% | +18.0% |
| 0.1-0.2 | 308 | 10.4% | 27.3% | +16.9% |
| 0.2-0.3 | 7 | 23.8% | 71.4% | +47.7% |
| 0.3-0.4 | 93 | 37.3% | 58.1% | +20.8% |
| 0.4-0.5 | 428 | 43.2% | 56.5% | +13.4% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 355 | 66.7% | 62.0% | -4.7% |
| 0.7-0.8 | 157 | 74.6% | 66.9% | -7.7% |
| 0.8-0.9 | 501 | 84.5% | 64.9% | -19.6% |
| 0.9-1.0 | 47 | 92.4% | 74.5% | -18.0% |

## By rule

- `2way-unanimous avg_p>=70`: settled=124, wins=92, hit_rate=0.741935, ROI=0.010594
- `ml-meta avg_p>=55`: settled=336, wins=202, hit_rate=0.60119, ROI=-0.080031
- `ml-meta avg_p>=60`: settled=52, wins=43, hit_rate=0.826923, ROI=0.137115
- `ml-meta avg_p>=65`: settled=9, wins=8, hit_rate=0.888889, ROI=0.225556
- `ml-meta avg_p>=70`: settled=5, wins=5, hit_rate=1.0, ROI=0.22
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=3, wins=3, hit_rate=1.0, ROI=0.086667
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=48, wins=35, hit_rate=0.729167, ROI=0.095625
- `CERTIFIED_CLEAN`: settled=50, wins=35, hit_rate=0.7, ROI=0.0938
- `SKIPPED_VETO`: settled=281, wins=181, hit_rate=0.644128, ROI=-0.089164
- `WATCHLIST_NO_ODDS`: settled=30, wins=20, hit_rate=0.666667, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.117333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=148, wins=97, hit_rate=0.655405, ROI=-0.0525
- `WATCHLIST_UNKNOWN_CTX`: settled=2, wins=2, hit_rate=1.0, ROI=0.23

## By odds source

- `UNKNOWN`: settled=38, wins=24, hit_rate=0.631579, ROI=None
- `betexplorer_odds`: settled=150, wins=100, hit_rate=0.666667, ROI=-0.055333
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.30125
- `forebet_best`: settled=63, wins=46, hit_rate=0.730159, ROI=0.102063
- `scoutingstats_odds`: settled=316, wins=204, hit_rate=0.64557, ROI=-0.067722
- `zulubet`: settled=1, wins=1, hit_rate=1.0, ROI=0.07

## By odds match method

- `alias_fuzzy`: settled=26, wins=19, hit_rate=0.730769, ROI=0.09
- `betexplorer`: settled=150, wins=100, hit_rate=0.666667, ROI=-0.055333
- `exact`: settled=324, wins=211, hit_rate=0.651235, ROI=-0.058611
- `fallback`: settled=41, wins=30, hit_rate=0.731707, ROI=0.108049
- `none`: settled=35, wins=22, hit_rate=0.628571, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 150 | 100 | 0.666667 | 150 | -0.055333 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.30125 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 316 | 204 | 0.64557 | 316 | -0.067722 |
| Source fallback (`SOURCE_FALLBACK`) | 41 | 30 | 0.731707 | 41 | 0.108049 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 26 | 19 | 0.730769 | 23 | 0.09 |
| No usable price (`UNMATCHED`) | 35 | 22 | 0.628571 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 281 | 181 | 0.644128 | 275 | -0.089164 |
| **trusted evidence only** | 87 | 56 | 0.643678 | 87 | -0.12977 |
| **soft evidence only** | 194 | 125 | 0.64433 | 188 | -0.070372 |
| evidence: BETEXPLORER_RESCUE | 82 | 51 | 0.621951 | 82 | -0.168659 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.508 |
| evidence: SCOUTINGSTATS_SOLE | 168 | 107 | 0.636905 | 168 | -0.081131 |
| evidence: SOURCE_FALLBACK | 12 | 9 | 0.75 | 12 | 0.0075 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 8 | 0.03875 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 161 | 122 | 0.757764 | 161 | -0.03882 |
| odds band: 1.50-2.00 | 106 | 51 | 0.481132 | 106 | -0.199245 |
| odds band: 2.00-3.00 | 8 | 5 | 0.625 | 8 | 0.35625 |
| odds band: unpriced | 6 | 3 | 0.5 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.21 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a'] | 6 | 1 | 0.166667 | 6 | -0.786667 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.1 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 4 | 2 | 0.5 | 4 | -0.2025 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.41 |
| veto reason: context VETO in ['league', 'team_h'] | 12 | 8 | 0.666667 | 12 | -0.139167 |
| veto reason: context VETO in ['league'] | 16 | 12 | 0.75 | 14 | 0.220714 |
| veto reason: context VETO in ['niche'] | 7 | 6 | 0.857143 | 7 | 0.182857 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.273333 |
| veto reason: context VETO in ['odds_band'] | 46 | 33 | 0.717391 | 46 | -0.102391 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 8 | 0.727273 | 11 | -0.118182 |
| veto reason: context VETO in ['team_a'] | 48 | 24 | 0.5 | 46 | -0.201304 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.227273 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.103333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 8 | 0.470588 | 17 | -0.198824 |
| veto reason: context VETO in ['team_h'] | 60 | 35 | 0.583333 | 59 | -0.113898 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 27 | 21 | 0.777778 | 27 | 0.118889 |
| contrast CAUTION: BZZOIRO_PRIMARY | 2 | 1 | 0.5 | 2 | -0.315 |
| contrast CAUTION: SOURCE_FALLBACK | 19 | 13 | 0.684211 | 19 | 0.105789 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 234 | 159 | 0.679487 | 199 | -0.007337 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 26 | 19 | 0.730769 | 23 | 0.09 | 26 | 1.569231 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 316 | 204 | 0.64557 | 316 | -0.067722 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-21: Kvant Obninsk vs Avangard Kursk (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.42 -> 🔴 LOST (Expected prob: 57.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.1% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.4% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.1% (Actual: 2 goals)

### 2026-09-21: Spezia vs Vis Pesaro (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 76.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.7% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 33.3% (Actual: 4 goals)

### 2026-09-21: Deportivo Toluca vs Santos Laguna (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🔴 LOST (Expected prob: 74.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.2% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 91.1% (Actual: 3 away goals)
    - [🔴 MISS] **Double Chance 1X**: expected 84.6% (Actual: away (2-3))
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 35.3% (Actual: 5 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-08-29 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hønefoss W vs Fortuna Ålesund W -> AWAY @ 1.2 (rescheduled → 2026-08-31; actual Hønefoss W 0-1 Fortuna Ålesund W [away])
- 2026-08-29 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — LSK Kvinner W vs Bodø / Glimt W -> HOME @ None (rescheduled → 2026-09-01; actual LSK Kvinner W 1-1 Bodø / Glimt W [draw])
- 2026-08-29 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Viking vs Aalesund -> HOME @ 1.3 (rescheduled → 2026-08-30; actual Viking 2-1 Aalesund [home])
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 3-3 Go Ahead Eagles [draw])
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])

## Pending / Unmatched Result Examples

- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)
- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

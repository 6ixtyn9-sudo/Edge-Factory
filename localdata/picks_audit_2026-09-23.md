# Edge Factory — Recent picks audit (2026-08-25 to 2026-09-23)

## Overall

- archived pick rows: 597
- archived pick dates: 30
- immutable morning-baseline rows: 597
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 571
- eligible prior picks: 588
- pending/unmatched result picks: 6
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 3
- wins: 378
- hit rate: +66.2%
- priced picks: 533
- ROI: -4.1%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-23
- same-day rows excluded: 9

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 335 / 525 matches (63.8%)
- **Both Teams to Score (BTTS)**: occurred in 301 / 525 matches (57.3%)
- **Selected Team Over 1.5 Goals**: occurred in 343 / 525 matches (65.3%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 571
- **Total Hits**: 439
- **Overall Hit Rate**: 76.9%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=109, hits=105, hit_rate=96.3%
- `home_over_05`: recommended=33, hits=26, hit_rate=78.8%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=12, hits=11, hit_rate=91.7%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=281, hits=185, hit_rate=65.8%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2388** | scored: 2388

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 564 | 564 | 358 | 63.5% | 46.2% | +17.3% | 0.260864 |
| `match_over_45` | 438 | 438 | 123 | 28.1% | 23.8% | +4.2% | 0.200843 |
| `away_under_35` | 404 | 404 | 393 | 97.3% | 96.3% | +1.0% | 0.026569 |
| `away_under_25` | 366 | 366 | 336 | 91.8% | 93.1% | -1.3% | 0.075662 |
| `home_over_05` | 174 | 174 | 154 | 88.5% | 84.0% | +4.5% | 0.103972 |
| `home_under_35` | 156 | 156 | 152 | 97.4% | 94.9% | +2.5% | 0.026221 |
| `home_under_25` | 130 | 130 | 118 | 90.8% | 91.8% | -1.0% | 0.082792 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `away_under_15` | 33 | 33 | 24 | 72.7% | 80.9% | -8.2% | 0.209009 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 30 | 30 | 27 | 90.0% | 88.4% | +1.6% | 0.088004 |
| `home_under_15` | 14 | 14 | 10 | 71.4% | 81.5% | -10.1% | 0.218222 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2131 | 1564 | 73.4% | 68.5% | +4.9% | 0.136948 |
| model | 257 | 182 | 70.8% | 63.8% | +7.0% | 0.171799 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 128 | 19.2% | 21.1% | +1.9% |
| 0.2-0.3 | 260 | 24.6% | 29.2% | +4.6% |
| 0.3-0.4 | 83 | 33.2% | 47.0% | +13.8% |
| 0.4-0.5 | 453 | 44.7% | 62.3% | +17.5% |
| 0.5-0.6 | 111 | 52.7% | 64.9% | +12.1% |
| 0.8-0.9 | 335 | 84.4% | 85.4% | +1.0% |
| 0.9-1.0 | 1018 | 94.7% | 94.7% | -0.0% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=525, MAE=1.58459 goals, bias=-0.167029 (realized − promised), promised avg 3.513695 vs realized 3.346667

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 525 | 30.5% | 35.8% | +5.3% | 0.242838 |
| BTTS-Yes | 525 | 41.8% | 57.3% | +15.5% | 0.26939 |
| Home Over 1.5 | 525 | 64.4% | 56.8% | -7.7% | 0.249355 |
| Over 2.5 | 525 | 69.6% | 63.8% | -5.8% | 0.233307 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 219 | 8.9% | 26.9% | +18.1% |
| 0.1-0.2 | 307 | 10.4% | 27.7% | +17.3% |
| 0.2-0.3 | 7 | 23.8% | 71.4% | +47.7% |
| 0.3-0.4 | 91 | 37.3% | 57.1% | +19.8% |
| 0.4-0.5 | 425 | 43.2% | 57.2% | +14.0% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 353 | 66.7% | 62.3% | -4.4% |
| 0.7-0.8 | 153 | 74.6% | 66.0% | -8.6% |
| 0.8-0.9 | 496 | 84.5% | 64.7% | -19.8% |
| 0.9-1.0 | 48 | 92.4% | 75.0% | -17.4% |

## By rule

- `2way-unanimous avg_p>=60`: settled=1, wins=1, hit_rate=1.0, ROI=0.12
- `2way-unanimous avg_p>=70`: settled=120, wins=88, hit_rate=0.733333, ROI=-0.001546
- `ml-meta avg_p>=55`: settled=332, wins=201, hit_rate=0.605422, ROI=-0.074088
- `ml-meta avg_p>=60`: settled=52, wins=43, hit_rate=0.826923, ROI=0.137115
- `ml-meta avg_p>=65`: settled=10, wins=8, hit_rate=0.8, ROI=0.103
- `ml-meta avg_p>=70`: settled=6, wins=5, hit_rate=0.833333, ROI=0.016667
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=3, wins=3, hit_rate=1.0, ROI=0.086667
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=48, wins=35, hit_rate=0.729167, ROI=0.095625
- `CERTIFIED_CLEAN`: settled=50, wins=35, hit_rate=0.7, ROI=0.0938
- `SKIPPED_VETO`: settled=277, wins=178, hit_rate=0.642599, ROI=-0.092952
- `WATCHLIST_NO_ODDS`: settled=30, wins=20, hit_rate=0.666667, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.117333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=147, wins=97, hit_rate=0.659864, ROI=-0.046054
- `WATCHLIST_UNKNOWN_CTX`: settled=2, wins=1, hit_rate=0.5, ROI=-0.38

## By odds source

- `UNKNOWN`: settled=38, wins=24, hit_rate=0.631579, ROI=None
- `betexplorer_odds`: settled=148, wins=97, hit_rate=0.655405, ROI=-0.07027
- `bzzoiro_odds`: settled=7, wins=6, hit_rate=0.857143, ROI=0.231429
- `forebet_best`: settled=63, wins=46, hit_rate=0.730159, ROI=0.102063
- `scoutingstats_odds`: settled=314, wins=204, hit_rate=0.649682, ROI=-0.061783
- `zulubet`: settled=1, wins=1, hit_rate=1.0, ROI=0.07

## By odds match method

- `alias_fuzzy`: settled=26, wins=19, hit_rate=0.730769, ROI=0.09
- `betexplorer`: settled=148, wins=97, hit_rate=0.655405, ROI=-0.07027
- `exact`: settled=321, wins=210, hit_rate=0.654206, ROI=-0.055389
- `fallback`: settled=41, wins=30, hit_rate=0.731707, ROI=0.108049
- `none`: settled=35, wins=22, hit_rate=0.628571, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 148 | 97 | 0.655405 | 148 | -0.07027 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 7 | 6 | 0.857143 | 7 | 0.231429 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 314 | 204 | 0.649682 | 314 | -0.061783 |
| Source fallback (`SOURCE_FALLBACK`) | 41 | 30 | 0.731707 | 41 | 0.108049 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 26 | 19 | 0.730769 | 23 | 0.09 |
| No usable price (`UNMATCHED`) | 35 | 22 | 0.628571 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 277 | 178 | 0.642599 | 271 | -0.092952 |
| **trusted evidence only** | 84 | 53 | 0.630952 | 84 | -0.154286 |
| **soft evidence only** | 193 | 125 | 0.647668 | 187 | -0.065401 |
| evidence: BETEXPLORER_RESCUE | 80 | 49 | 0.6125 | 80 | -0.183875 |
| evidence: BZZOIRO_PRIMARY | 4 | 4 | 1.0 | 4 | 0.4375 |
| evidence: SCOUTINGSTATS_SOLE | 167 | 107 | 0.640719 | 167 | -0.075629 |
| evidence: SOURCE_FALLBACK | 12 | 9 | 0.75 | 12 | 0.0075 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 8 | 0.03875 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 160 | 121 | 0.75625 | 160 | -0.041125 |
| odds band: 1.50-2.00 | 103 | 49 | 0.475728 | 103 | -0.20835 |
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
| veto reason: context VETO in ['league'] | 15 | 12 | 0.8 | 13 | 0.314615 |
| veto reason: context VETO in ['niche'] | 7 | 6 | 0.857143 | 7 | 0.182857 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.273333 |
| veto reason: context VETO in ['odds_band'] | 45 | 32 | 0.711111 | 45 | -0.114444 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 10 | 7 | 0.7 | 10 | -0.131 |
| veto reason: context VETO in ['team_a'] | 49 | 24 | 0.489796 | 47 | -0.227447 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.227273 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.103333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 15 | 7 | 0.466667 | 15 | -0.211333 |
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
| No price quarantine (`NONE`) | 231 | 155 | 0.670996 | 196 | -0.022194 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 26 | 19 | 0.730769 | 23 | 0.09 | 26 | 1.569231 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 314 | 204 | 0.649682 | 314 | -0.061783 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-22: Clachnacuddin vs Ross County (Actual Score: **1-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.12 -> 🟢 WON (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.3% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.1% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.1% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.2% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.9% (Actual: 6 goals)

### 2026-09-22: Gala Fairydean vs Spartans FC (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.15 -> 🔴 LOST (Expected prob: 66.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.8% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 38.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.5% (Actual: 0 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.6% (Actual: 0 goals)

### 2026-09-22: East Kilbride vs Celtic II (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🔴 LOST (Expected prob: 74.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 81.0% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.5% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 88.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 55.6% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.1% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 85.9% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 35.0% (Actual: 6 goals)


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
- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']

## Ambiguous result examples

- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)
- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

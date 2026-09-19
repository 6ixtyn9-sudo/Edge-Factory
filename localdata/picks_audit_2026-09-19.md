# Edge Factory — Recent picks audit (2026-08-21 to 2026-09-19)

## Overall

- archived pick rows: 640
- archived pick dates: 30
- immutable morning-baseline rows: 640
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 30
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 572
- eligible prior picks: 596
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 4
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 389
- hit rate: +68.0%
- priced picks: 536
- ROI: -2.9%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-19
- same-day rows excluded: 44

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 335 / 526 matches (63.7%)
- **Both Teams to Score (BTTS)**: occurred in 282 / 526 matches (53.6%)
- **Selected Team Over 1.5 Goals**: occurred in 359 / 526 matches (68.3%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 572
- **Total Hits**: 418
- **Overall Hit Rate**: 73.1%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=10, hits=9, hit_rate=90.0%
- `away_under_35`: recommended=92, hits=88, hit_rate=95.7%
- `home_over_05`: recommended=43, hits=33, hit_rate=76.7%
- `home_under_25`: recommended=7, hits=7, hit_rate=100.0%
- `home_under_35`: recommended=11, hits=10, hit_rate=90.9%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=330, hits=213, hit_rate=64.5%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2474** | scored: 2474

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 565 | 565 | 358 | 63.4% | 47.1% | +16.3% | 0.258561 |
| `match_over_45` | 426 | 426 | 127 | 29.8% | 23.9% | +5.9% | 0.21068 |
| `away_under_35` | 415 | 415 | 401 | 96.6% | 97.0% | -0.4% | 0.031753 |
| `away_under_25` | 385 | 385 | 357 | 92.7% | 93.4% | -0.7% | 0.067754 |
| `home_over_05` | 236 | 236 | 209 | 88.6% | 84.5% | +4.1% | 0.102764 |
| `home_under_35` | 155 | 155 | 151 | 97.4% | 95.5% | +1.9% | 0.02551 |
| `home_under_25` | 120 | 120 | 110 | 91.7% | 91.6% | +0.0% | 0.076251 |
| `away_under_15` | 51 | 51 | 40 | 78.4% | 80.9% | -2.5% | 0.172183 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 29 | 29 | 26 | 89.7% | 88.7% | +0.9% | 0.08967 |
| `home_under_15` | 15 | 15 | 11 | 73.3% | 81.4% | -8.1% | 0.206266 |
| `double_chance` | 1 | 1 | 1 | 100.0% | 84.6% | +15.4% | 0.023822 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2206 | 1649 | 74.8% | 70.1% | +4.7% | 0.133356 |
| model | 268 | 191 | 71.3% | 63.6% | +7.6% | 0.182565 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 124 | 19.1% | 23.4% | +4.3% |
| 0.2-0.3 | 257 | 24.9% | 31.9% | +7.0% |
| 0.3-0.4 | 77 | 33.2% | 44.2% | +10.9% |
| 0.4-0.5 | 425 | 45.1% | 62.1% | +17.0% |
| 0.5-0.6 | 136 | 53.2% | 64.7% | +11.5% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 405 | 84.4% | 86.4% | +2.0% |
| 0.9-1.0 | 1045 | 95.2% | 94.7% | -0.4% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=525, MAE=1.603371 goals, bias=-0.135714 (realized − promised), promised avg 3.522381 vs realized 3.386667

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 525 | 29.4% | 36.8% | +7.4% | 0.213485 |
| BTTS-Yes | 525 | 41.6% | 53.7% | +12.1% | 0.264004 |
| Home Over 1.5 | 525 | 65.5% | 57.9% | -7.6% | 0.252506 |
| Over 2.5 | 525 | 69.7% | 63.6% | -6.1% | 0.233936 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 238 | 8.8% | 27.3% | +18.5% |
| 0.1-0.2 | 289 | 10.4% | 26.3% | +15.9% |
| 0.2-0.3 | 9 | 22.4% | 44.4% | +22.0% |
| 0.3-0.4 | 102 | 37.4% | 55.9% | +18.4% |
| 0.4-0.5 | 411 | 43.2% | 53.3% | +10.0% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 346 | 66.6% | 61.6% | -5.1% |
| 0.7-0.8 | 159 | 74.7% | 66.0% | -8.6% |
| 0.8-0.9 | 494 | 84.5% | 67.6% | -16.8% |
| 0.9-1.0 | 51 | 92.2% | 78.4% | -13.8% |

## By rule

- `2way-unanimous avg_p>=70`: settled=122, wins=93, hit_rate=0.762295, ROI=0.025825
- `ml-meta avg_p>=55`: settled=337, wins=210, hit_rate=0.623145, ROI=-0.067134
- `ml-meta avg_p>=60`: settled=44, wins=37, hit_rate=0.840909, ROI=0.146818
- `ml-meta avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.2
- `ml-meta avg_p>=70`: settled=11, wins=10, hit_rate=0.909091, ROI=0.14
- `ml-meta avg_p>=75`: settled=2, wins=2, hit_rate=1.0, ROI=0.1
- `ml-meta avg_p>=80`: settled=3, wins=3, hit_rate=1.0, ROI=0.1
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=52, wins=40, hit_rate=0.769231, ROI=0.165385
- `CERTIFIED_CLEAN`: settled=35, wins=24, hit_rate=0.685714, ROI=0.033429
- `SKIPPED_VETO`: settled=295, wins=193, hit_rate=0.654237, ROI=-0.089204
- `WATCHLIST_NO_ODDS`: settled=28, wins=19, hit_rate=0.678571, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.056667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=138, wins=94, hit_rate=0.681159, ROI=-0.014783
- `WATCHLIST_UNKNOWN_CTX`: settled=7, wins=7, hit_rate=1.0, ROI=0.221429

## By odds source

- `UNKNOWN`: settled=36, wins=23, hit_rate=0.638889, ROI=None
- `betexplorer_odds`: settled=156, wins=108, hit_rate=0.692308, ROI=-0.050897
- `bzzoiro_odds`: settled=7, wins=7, hit_rate=1.0, ROI=0.532857
- `forebet_best`: settled=64, wins=47, hit_rate=0.734375, ROI=0.07625
- `scoutingstats_odds`: settled=308, wins=203, hit_rate=0.659091, ROI=-0.053214
- `zulubet`: settled=1, wins=1, hit_rate=1.0, ROI=0.07

## By odds match method

- `alias_fuzzy`: settled=25, wins=18, hit_rate=0.72, ROI=0.020909
- `betexplorer`: settled=156, wins=108, hit_rate=0.692308, ROI=-0.050897
- `exact`: settled=315, wins=210, hit_rate=0.666667, ROI=-0.04019
- `fallback`: settled=43, wins=32, hit_rate=0.744186, ROI=0.104419
- `none`: settled=33, wins=21, hit_rate=0.636364, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 156 | 108 | 0.692308 | 156 | -0.050897 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 7 | 7 | 1.0 | 7 | 0.532857 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 308 | 203 | 0.659091 | 308 | -0.053214 |
| Source fallback (`SOURCE_FALLBACK`) | 43 | 32 | 0.744186 | 43 | 0.104419 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 25 | 18 | 0.72 | 22 | 0.020909 |
| No usable price (`UNMATCHED`) | 33 | 21 | 0.636364 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 295 | 193 | 0.654237 | 289 | -0.089204 |
| **trusted evidence only** | 96 | 65 | 0.677083 | 96 | -0.101563 |
| **soft evidence only** | 199 | 128 | 0.643216 | 193 | -0.083057 |
| evidence: BETEXPLORER_RESCUE | 92 | 61 | 0.663043 | 92 | -0.130326 |
| evidence: BZZOIRO_PRIMARY | 4 | 4 | 1.0 | 4 | 0.56 |
| evidence: SCOUTINGSTATS_SOLE | 170 | 109 | 0.641176 | 170 | -0.084412 |
| evidence: SOURCE_FALLBACK | 16 | 11 | 0.6875 | 16 | -0.080625 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.055714 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 178 | 135 | 0.758427 | 178 | -0.043258 |
| odds band: 1.50-2.00 | 102 | 50 | 0.490196 | 102 | -0.191471 |
| odds band: 2.00-3.00 | 9 | 5 | 0.555556 | 9 | 0.161111 |
| odds band: unpriced | 6 | 3 | 0.5 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 3 | 1.0 | 2 | 0.305 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 5 | 1.0 | 5 | 0.146 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 11 | 4 | 0.363636 | 11 | -0.573636 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 4 | 2 | 0.5 | 4 | -0.2025 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['league', 'team_h'] | 13 | 9 | 0.692308 | 13 | -0.093846 |
| veto reason: context VETO in ['league'] | 18 | 13 | 0.722222 | 16 | 0.139375 |
| veto reason: context VETO in ['niche'] | 8 | 6 | 0.75 | 8 | 0.09 |
| veto reason: context VETO in ['odds_band', 'niche'] | 4 | 4 | 1.0 | 4 | 0.26 |
| veto reason: context VETO in ['odds_band'] | 47 | 34 | 0.723404 | 47 | -0.093617 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 9 | 0.818182 | 11 | -0.003636 |
| veto reason: context VETO in ['team_a'] | 42 | 22 | 0.52381 | 40 | -0.1495 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 1 | 0.25 | 4 | -0.64 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.221818 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.446667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.123333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 8 | 0.470588 | 17 | -0.231176 |
| veto reason: context VETO in ['team_h'] | 66 | 39 | 0.590909 | 65 | -0.140462 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 31 | 23 | 0.741935 | 31 | 0.086129 |
| contrast CAUTION: BZZOIRO_PRIMARY | 2 | 2 | 1.0 | 2 | 0.495 |
| contrast CAUTION: SOURCE_FALLBACK | 19 | 15 | 0.789474 | 19 | 0.26 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 239 | 168 | 0.702929 | 206 | 0.001359 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 25 | 18 | 0.72 | 22 | 0.020909 | 25 | 1.5388 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 308 | 203 | 0.659091 | 308 | -0.053214 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-18: FC Haka vs Klubi 04 (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.8% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 2 goals)

### 2026-09-18: FC Lahti vs FF Jaro (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🔴 LOST (Expected prob: 67.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.5% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.4% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.6% (Actual: 2 goals)

### 2026-09-18: Bayern München vs Union Berlin (Actual Score: **7-0**)
- **1X2 Pick**: Selected `HOME` @ 1.05 -> 🟢 WON (Expected prob: 84.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 94.4% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 100.0% (Actual: 7 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 94.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.2% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.9% (Actual: 7 goals)

### 2026-09-18: Bolívar vs Gualberto Villarroel SJ (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.07 -> 🟢 WON (Expected prob: 80.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.1% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.8% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 93.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.6% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.3% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.5% (Actual: 6 goals)

### 2026-09-18: Shkendija 79 vs Bashkimi Kumanovo (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.06 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.6% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.1% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 30.1% (Actual: 5 goals)

### 2026-09-18: Ammanford vs Pen-y-Bont FC (Actual Score: **1-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.16 -> 🟢 WON (Expected prob: 66.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.8% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.2% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.2% (Actual: 6 goals)

### 2026-09-18: Groningen vs PEC Zwolle (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 61.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.2% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 3 goals)

### 2026-09-18: Bohemians FC vs Drogheda Utd (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 58.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.4% (Actual: 3 goals)

### 2026-09-18: Bray Wanderers vs Treaty United (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 58.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.3% (Actual: 2 goals)

### 2026-09-18: Monaco vs Lens (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 2.05 -> 🟢 WON (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.8% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.0% (Actual: 3 goals)

### 2026-09-18: Espanyol vs Elche (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.83 -> 🔴 LOST (Expected prob: 55.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.8% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 92.3% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 39.9% (Actual: 4 goals)

### 2026-09-18: Caernarfon Town vs Cambrian and Clydach (Actual Score: **9-1**)
- **1X2 Pick**: Selected `HOME` @ 1.41 -> 🟢 WON (Expected prob: 56.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 10 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 9 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.6% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.4% (Actual: 10 goals)

### 2026-09-18: Flamengo vs Independiente del Valle (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 55.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.3% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.0% (Actual: 2 goals)

### 2026-09-18: Arema FC vs Persik Kediri (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🔴 LOST (Expected prob: 55.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.0% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.7% (Actual: 2 goals)

### 2026-09-18: Shamrock Rovers vs Waterford United (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 55.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.6% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.1% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.3% (Actual: 5 goals)

### 2026-09-18: Rekord Bielsko-Biala vs Swit Skolwin (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🟢 WON (Expected prob: 55.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.8% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.2% (Actual: 3 goals)

### 2026-09-18: FC Dornbirn vs Lauterach (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.9% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 52.7% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 31.1% (Actual: 1 goals)

### 2026-09-18: GrIFK vs MuSa (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 70.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.0% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.0% (Actual: 2 goals)

### 2026-09-18: Manchester City (w) vs Liverpool (w) (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.7% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.4% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.3% (Actual: 6 goals)

### 2026-09-18: Wisla Krakow vs Slask Wroclaw (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 60.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.3% (Actual: 3 goals)

### 2026-09-18: Yeovil Town vs Solihull Moors (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.9 -> 🟢 WON (Expected prob: 56.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.4% (Actual: 5 goals)

### 2026-09-18: Hapoel Tel Aviv vs Hapoel Petah Tikva (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 62.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.1% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.5% (Actual: 3 goals)

### 2026-09-18: Alianza Atletico vs Comerciantes Unidos (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 39.8% (Actual: 3 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 4 |
- 2026-08-21 `POSTPONED` `SKIPPED_VETO` — Shamrock Rovers vs Shelbourne FC (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — Rangers vs St Mirren (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — St Johnstone vs Celtic (verified_disposition); excluded from win/loss/ROI
- 2026-08-22 `POSTPONED` `SKIPPED_VETO` — Hibernian vs Kilmarnock (verified_disposition); excluded from win/loss/ROI

## Rescheduled Fixture Examples

- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (rescheduled → 2026-08-24; actual Charleston Battery 5-0 Miami FC II [home])
- 2026-08-29 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hønefoss W vs Fortuna Ålesund W -> AWAY @ 1.2 (rescheduled → 2026-08-31; actual Hønefoss W 0-1 Fortuna Ålesund W [away])
- 2026-08-29 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — LSK Kvinner W vs Bodø / Glimt W -> HOME @ None (rescheduled → 2026-09-01; actual LSK Kvinner W 1-1 Bodø / Glimt W [draw])
- 2026-08-29 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Viking vs Aalesund -> HOME @ 1.3 (rescheduled → 2026-08-30; actual Viking 2-1 Aalesund [home])
- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 3-3 Go Ahead Eagles [draw])
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])

## Pending / Unmatched Result Examples

- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
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

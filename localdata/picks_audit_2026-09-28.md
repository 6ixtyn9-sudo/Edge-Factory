# Edge Factory — Recent picks audit (2026-08-30 to 2026-09-28)

## Overall

- archived pick rows: 627
- archived pick dates: 30
- immutable morning-baseline rows: 627
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 30
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 602
- eligible prior picks: 622
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 1
- ambiguous result picks: 3
- wins: 397
- hit rate: +65.9%
- priced picks: 554
- ROI: -5.4%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-28
- same-day rows excluded: 5

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 348 / 556 matches (62.6%)
- **Both Teams to Score (BTTS)**: occurred in 313 / 556 matches (56.3%)
- **Selected Team Over 1.5 Goals**: occurred in 361 / 556 matches (64.9%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 602
- **Total Hits**: 474
- **Overall Hit Rate**: 78.7%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=154, hits=149, hit_rate=96.8%
- `home_over_05`: recommended=25, hits=18, hit_rate=72.0%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=24, hits=23, hit_rate=95.8%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=263, hits=172, hit_rate=65.4%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2430** | scored: 2430

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 595 | 595 | 371 | 62.4% | 45.6% | +16.8% | 0.262036 |
| `match_over_45` | 470 | 470 | 122 | 26.0% | 23.8% | +2.1% | 0.189221 |
| `away_under_35` | 424 | 424 | 413 | 97.4% | 96.0% | +1.4% | 0.025331 |
| `away_under_25` | 384 | 384 | 350 | 91.1% | 92.1% | -1.0% | 0.080904 |
| `home_under_35` | 167 | 167 | 163 | 97.6% | 94.2% | +3.4% | 0.02546 |
| `home_under_25` | 133 | 133 | 123 | 92.5% | 90.8% | +1.7% | 0.069892 |
| `home_over_05` | 118 | 118 | 102 | 86.4% | 83.8% | +2.7% | 0.118125 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 32 | 32 | 29 | 90.6% | 88.0% | +2.7% | 0.084847 |
| `away_under_15` | 15 | 15 | 10 | 66.7% | 81.0% | -14.3% | 0.246834 |
| `home_under_15` | 13 | 13 | 9 | 69.2% | 81.6% | -12.3% | 0.232124 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2169 | 1557 | 71.8% | 67.2% | +4.6% | 0.136249 |
| model | 261 | 186 | 71.3% | 63.8% | +7.4% | 0.172326 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 124 | 19.2% | 17.7% | -1.5% |
| 0.2-0.3 | 294 | 24.4% | 26.9% | +2.5% |
| 0.3-0.4 | 87 | 33.3% | 48.3% | +15.0% |
| 0.4-0.5 | 500 | 44.5% | 61.0% | +16.5% |
| 0.5-0.6 | 93 | 52.5% | 64.5% | +12.0% |
| 0.8-0.9 | 337 | 85.4% | 85.8% | +0.3% |
| 0.9-1.0 | 995 | 94.5% | 95.1% | +0.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=555, MAE=1.562234 goals, bias=-0.237081 (realized − promised), promised avg 3.519964 vs realized 3.282883

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 555 | 31.0% | 35.9% | +4.8% | 0.234703 |
| BTTS-Yes | 555 | 41.7% | 56.2% | +14.5% | 0.267773 |
| Home Over 1.5 | 555 | 63.9% | 54.4% | -9.5% | 0.246992 |
| Over 2.5 | 555 | 69.6% | 62.5% | -7.1% | 0.238266 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 234 | 8.7% | 25.6% | +16.9% |
| 0.1-0.2 | 323 | 10.4% | 25.7% | +15.3% |
| 0.2-0.3 | 7 | 24.6% | 57.1% | +32.5% |
| 0.3-0.4 | 92 | 37.2% | 56.5% | +19.4% |
| 0.4-0.5 | 453 | 43.0% | 56.1% | +13.1% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 378 | 66.8% | 60.8% | -6.0% |
| 0.7-0.8 | 158 | 74.5% | 65.2% | -9.3% |
| 0.8-0.9 | 524 | 84.5% | 64.5% | -20.0% |
| 0.9-1.0 | 50 | 92.4% | 72.0% | -20.4% |

## By rule

- `2way-unanimous avg_p>=60`: settled=66, wins=41, hit_rate=0.621212, ROI=-0.163208
- `2way-unanimous avg_p>=70`: settled=104, wins=76, hit_rate=0.730769, ROI=-0.014634
- `ml-meta avg_p>=55`: settled=316, wins=192, hit_rate=0.607595, ROI=-0.076743
- `ml-meta avg_p>=60`: settled=50, wins=43, hit_rate=0.86, ROI=0.1876
- `ml-meta avg_p>=65`: settled=10, wins=8, hit_rate=0.8, ROI=0.05
- `ml-meta avg_p>=70`: settled=5, wins=4, hit_rate=0.8, ROI=-0.108
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=4, wins=4, hit_rate=1.0, ROI=0.07
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=55, wins=34, hit_rate=0.618182, ROI=-0.055273
- `CERTIFIED_CLEAN`: settled=56, wins=39, hit_rate=0.696429, ROI=0.082321
- `SKIPPED_VETO`: settled=284, wins=183, hit_rate=0.644366, ROI=-0.090912
- `WATCHLIST_NO_ODDS`: settled=36, wins=26, hit_rate=0.722222, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=16, wins=11, hit_rate=0.6875, ROI=0.098571
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=150, wins=100, hit_rate=0.666667, ROI=-0.0542
- `WATCHLIST_UNKNOWN_CTX`: settled=5, wins=4, hit_rate=0.8, ROI=-0.016

## By odds source

- `UNKNOWN`: settled=48, wins=33, hit_rate=0.6875, ROI=None
- `betexplorer_odds`: settled=159, wins=102, hit_rate=0.641509, ROI=-0.079245
- `bzzoiro_odds`: settled=6, wins=5, hit_rate=0.833333, ROI=0.275
- `forebet_best`: settled=84, wins=60, hit_rate=0.714286, ROI=0.055238
- `scoutingstats_odds`: settled=303, wins=195, hit_rate=0.643564, ROI=-0.080957
- `zulubet`: settled=2, wins=2, hit_rate=1.0, ROI=0.335

## By odds match method

- `alias_fuzzy`: settled=24, wins=17, hit_rate=0.708333, ROI=0.03619
- `betexplorer`: settled=159, wins=102, hit_rate=0.641509, ROI=-0.079245
- `exact`: settled=309, wins=200, hit_rate=0.647249, ROI=-0.074045
- `fallback`: settled=65, wins=47, hit_rate=0.723077, ROI=0.07
- `none`: settled=45, wins=31, hit_rate=0.688889, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 159 | 102 | 0.641509 | 159 | -0.079245 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 6 | 5 | 0.833333 | 6 | 0.275 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 303 | 195 | 0.643564 | 303 | -0.080957 |
| Source fallback (`SOURCE_FALLBACK`) | 65 | 47 | 0.723077 | 65 | 0.07 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 24 | 17 | 0.708333 | 21 | 0.03619 |
| No usable price (`UNMATCHED`) | 45 | 31 | 0.688889 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 284 | 183 | 0.644366 | 274 | -0.090912 |
| **trusted evidence only** | 89 | 56 | 0.629213 | 89 | -0.134944 |
| **soft evidence only** | 195 | 127 | 0.651282 | 185 | -0.06973 |
| evidence: BETEXPLORER_RESCUE | 86 | 53 | 0.616279 | 86 | -0.157093 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.5 |
| evidence: SCOUTINGSTATS_SOLE | 153 | 95 | 0.620915 | 153 | -0.10719 |
| evidence: SOURCE_FALLBACK | 25 | 21 | 0.84 | 25 | 0.1648 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.088571 |
| evidence: UNMATCHED | 9 | 5 | 0.555556 | 0 | None |
| odds band: <1.50 | 162 | 121 | 0.746914 | 162 | -0.052222 |
| odds band: 1.50-2.00 | 106 | 52 | 0.490566 | 106 | -0.180189 |
| odds band: 2.00-3.00 | 6 | 4 | 0.666667 | 6 | 0.441667 |
| odds band: unpriced | 10 | 6 | 0.6 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.21 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.1 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.49 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 14 | 10 | 0.714286 | 14 | -0.047857 |
| veto reason: context VETO in ['league'] | 25 | 18 | 0.72 | 19 | 0.101579 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 56 | 39 | 0.696429 | 56 | -0.107679 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.085 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 6 | 0.666667 | 9 | -0.17 |
| veto reason: context VETO in ['team_a'] | 48 | 25 | 0.520833 | 46 | -0.168478 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 6 | 6 | 1.0 | 6 | 0.316667 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.111667 |
| veto reason: context VETO in ['team_h', 'team_a'] | 15 | 6 | 0.4 | 15 | -0.323333 |
| veto reason: context VETO in ['team_h'] | 53 | 31 | 0.584906 | 52 | -0.104038 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 31 | 20 | 0.645161 | 31 | -0.048387 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 23 | 14 | 0.608696 | 23 | -0.023478 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 275 | 185 | 0.672727 | 230 | -0.027826 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 24 | 17 | 0.708333 | 21 | 0.03619 | 24 | 1.562083 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 303 | 195 | 0.643564 | 303 | -0.080957 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-27: Xelaju vs Comunicaciones (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.58 -> 🔴 LOST (Expected prob: 68.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.2% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 26.2% (Actual: 5 goals)

### 2026-09-27: Union Brescia vs Dolomiti Bellunesi (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.34 -> 🔴 LOST (Expected prob: 61.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 2 goals)

### 2026-09-27: Juárez W vs Tijuana W (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.51 -> 🟢 WON (Expected prob: 61.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.3% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.9% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.0% (Actual: 6 goals)

### 2026-09-27: Trelleborgs FF vs Ängelholms FF (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 70.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.8% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.3% (Actual: 5 goals)

### 2026-09-27: Ravenna vs Gubbio (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🟢 WON (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.3% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 2 goals)

### 2026-09-27: Denmark vs Wales (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 62.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.9% (Actual: 2 goals)

### 2026-09-27: Linero vs Torns IF (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.72 -> 🟢 WON (Expected prob: 58.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.8% (Actual: 6 goals)

### 2026-09-27: Serbia vs Netherlands (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.38 -> 🟢 WON (Expected prob: 56.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.7% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 3 goals)

### 2026-09-27: Puebla W vs Monterrey W (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.02 -> 🟢 WON (Expected prob: 80.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.9% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.2% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 36.9% (Actual: 3 goals)

### 2026-09-27: Kano Pillars vs Enyimba (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 71.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.5% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.6% (Actual: 0 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.6% (Actual: 0 goals)

### 2026-09-27: Vancouver Whitecaps vs DC United (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.29 -> 🔴 LOST (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.5% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.1% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.9% (Actual: 6 goals)

### 2026-09-27: Nashville SC vs Toronto FC (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 69.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 72.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.4% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.5% (Actual: 2 goals)

### 2026-09-27: Fratria vs Spartak Pleven (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 67.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.4% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.1% (Actual: 3 goals)

### 2026-09-27: Germany vs Greece (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.43 -> 🔴 LOST (Expected prob: 67.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.9% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.7% (Actual: 1 goals)

### 2026-09-27: Houston Dynamo vs Sporting Kansas City (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.63 -> 🔴 LOST (Expected prob: 64.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.3% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.9% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 22.4% (Actual: 2 goals)

### 2026-09-27: Portmore United vs Humble Lions (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.18 -> 🟢 WON (Expected prob: 63.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.4% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 22.2% (Actual: 5 goals)

### 2026-09-27: Deportes Concepción vs Curicó Unido (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.34 -> 🟢 WON (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 2 goals)

### 2026-09-27: Portland Thorns (w) vs Houston Dash (w) (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🔴 LOST (Expected prob: 61.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.4% (Actual: 2 goals)

### 2026-09-27: Manchester United Women vs West Ham (w) (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 61.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.1% (Actual: 3 goals)

### 2026-09-27: Envigado vs Depor FC (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.4% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.6% (Actual: 3 goals)

### 2026-09-27: Austria vs Kosovo (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.63 -> 🟢 WON (Expected prob: 59.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.4% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.6% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 4 goals)

### 2026-09-27: Unión Comercio vs Molinos El Pirata (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 56.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.6% (Actual: 2 goals)

### 2026-09-27: Eibar vs Las Palmas (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.95 -> 🟢 WON (Expected prob: 56.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.1% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.2% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.1% (Actual: 5 goals)

### 2026-09-27: Hohenems vs Kufstein (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 81.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.5% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 94.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.6% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.3% (Actual: 4 goals)

### 2026-09-27: Kroměříž II vs Tatran Všechovice (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.6% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 85.5% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.0% (Actual: 3 goals)

### 2026-09-27: FK Kaluga vs Dinamo Kirov (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 56.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.0% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.7% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.7% (Actual: 3 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-09-05 `WATCHLIST_UNCORROBORATED_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Utrecht vs Go Ahead Eagles -> OVER @ 1.5 (rescheduled → 2026-09-08; actual FC Utrecht 3-3 Go Ahead Eagles [draw])
- 2026-09-06 `WATCHLIST_SUSPECT_PRICE` `ou25-unanimous-2way-sa avg_p>=70` — Philadelphia Union vs Montreal Impact -> OVER @ 1.44 (rescheduled → 2026-09-05; actual Philadelphia Union 2-0 Montreal Impact [home])
- 2026-09-07 `CAUTION` `ml-meta avg_p>=55` — Cruz Azul vs Santos Laguna -> HOME @ 1.41 (rescheduled → 2026-09-06; actual Cruz Azul 1-0 Santos Laguna [home])
- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])
- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova FC 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca W 4-1 Santos Laguna W [home])

## Pending / Unmatched Result Examples

- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
- 2026-09-22 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — MC Alger vs MC Oran -> HOME @ 1.45 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-26 `SKIPPED_VETO` `ml-meta avg_p>=55` — Crawley Town vs Barnet -> AWAY @ 1.66 (pending_or_unmatched_result); keys=['crawleyto']/['barnet']
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Milevsko vs Spartak Sobeslav -> AWAY @ 1.57 (pending_or_unmatched_result); keys=['milevsko']/['spartakso']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Polanka nad Odrou vs Frydek-Mistek -> AWAY @ 1.48 (pending_or_unmatched_result); keys=['polankana']/['frydekmis']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Brommapojkarna W vs Malmö FF W -> AWAY @ 1.4 (pending_or_unmatched_result); keys=['brommapoj']/['malmff', 'malmoffw']
- 2026-09-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — Plateau United vs Inter Lagos -> HOME @ 1.33 (pending_or_unmatched_result); keys=['plateauun']/['interlago']

## Ambiguous result examples

- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)
- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

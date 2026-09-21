# Edge Factory — Recent picks audit (2026-08-23 to 2026-09-21)

## Overall

- archived pick rows: 620
- archived pick dates: 30
- immutable morning-baseline rows: 620
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 30
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 596
- eligible prior picks: 616
- pending/unmatched result picks: 9
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 400
- hit rate: +67.1%
- priced picks: 558
- ROI: -2.9%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-21
- same-day rows excluded: 4

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 351 / 550 matches (63.8%)
- **Both Teams to Score (BTTS)**: occurred in 310 / 550 matches (56.4%)
- **Selected Team Over 1.5 Goals**: occurred in 363 / 550 matches (66.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 596
- **Total Hits**: 457
- **Overall Hit Rate**: 76.7%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=109, hits=105, hit_rate=96.3%
- `home_over_05`: recommended=43, hits=33, hit_rate=76.7%
- `home_under_25`: recommended=32, hits=30, hit_rate=93.8%
- `home_under_35`: recommended=12, hits=11, hit_rate=91.7%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=297, hits=197, hit_rate=66.3%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2511** | scored: 2511

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 589 | 589 | 374 | 63.5% | 46.2% | +17.3% | 0.260826 |
| `match_over_45` | 457 | 457 | 130 | 28.4% | 23.8% | +4.7% | 0.203513 |
| `away_under_35` | 424 | 424 | 412 | 97.2% | 96.4% | +0.7% | 0.027319 |
| `away_under_25` | 384 | 384 | 356 | 92.7% | 93.2% | -0.5% | 0.068152 |
| `home_over_05` | 196 | 196 | 171 | 87.2% | 84.2% | +3.0% | 0.112409 |
| `home_under_35` | 162 | 162 | 158 | 97.5% | 95.0% | +2.5% | 0.025271 |
| `home_under_25` | 136 | 136 | 123 | 90.4% | 91.8% | -1.3% | 0.085732 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `away_under_15` | 40 | 40 | 30 | 75.0% | 81.0% | -6.0% | 0.193841 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 30 | 30 | 27 | 90.0% | 88.4% | +1.6% | 0.088004 |
| `home_under_15` | 15 | 15 | 11 | 73.3% | 81.4% | -8.1% | 0.206155 |
| `double_chance` | 2 | 2 | 2 | 100.0% | 83.3% | +16.7% | 0.027978 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2244 | 1654 | 73.7% | 68.8% | +4.9% | 0.135576 |
| model | 267 | 189 | 70.8% | 63.6% | +7.2% | 0.178413 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 132 | 19.2% | 21.2% | +2.0% |
| 0.2-0.3 | 278 | 24.7% | 30.2% | +5.6% |
| 0.3-0.4 | 80 | 33.2% | 46.2% | +13.1% |
| 0.4-0.5 | 476 | 44.8% | 62.4% | +17.6% |
| 0.5-0.6 | 113 | 52.6% | 64.6% | +12.0% |
| 0.8-0.9 | 363 | 84.4% | 85.4% | +1.0% |
| 0.9-1.0 | 1069 | 94.8% | 94.9% | +0.0% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=549, MAE=1.595355 goals, bias=-0.15867 (realized − promised), promised avg 3.515683 vs realized 3.357013

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 549 | 30.5% | 35.3% | +4.9% | 0.230084 |
| BTTS-Yes | 549 | 41.7% | 56.5% | +14.8% | 0.269189 |
| Home Over 1.5 | 549 | 64.5% | 57.4% | -7.1% | 0.254618 |
| Over 2.5 | 549 | 69.6% | 63.8% | -5.8% | 0.233174 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 236 | 8.9% | 27.5% | +18.7% |
| 0.1-0.2 | 314 | 10.4% | 26.8% | +16.4% |
| 0.2-0.3 | 9 | 22.9% | 55.6% | +32.6% |
| 0.3-0.4 | 102 | 37.3% | 58.8% | +21.5% |
| 0.4-0.5 | 436 | 43.2% | 55.7% | +12.6% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 368 | 66.7% | 62.0% | -4.7% |
| 0.7-0.8 | 162 | 74.5% | 66.7% | -7.8% |
| 0.8-0.9 | 521 | 84.5% | 65.5% | -19.0% |
| 0.9-1.0 | 47 | 92.4% | 74.5% | -17.9% |

## By rule

- `2way-unanimous avg_p>=70`: settled=127, wins=94, hit_rate=0.740157, ROI=0.006442
- `ml-meta avg_p>=55`: settled=338, wins=205, hit_rate=0.606509, ROI=-0.072809
- `ml-meta avg_p>=60`: settled=64, wins=54, hit_rate=0.84375, ROI=0.17125
- `ml-meta avg_p>=65`: settled=9, wins=8, hit_rate=0.888889, ROI=0.225556
- `ml-meta avg_p>=70`: settled=7, wins=6, hit_rate=0.857143, ROI=0.015714
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=4, wins=4, hit_rate=1.0, ROI=0.08
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=50, wins=37, hit_rate=0.74, ROI=0.1128
- `CERTIFIED_CLEAN`: settled=50, wins=35, hit_rate=0.7, ROI=0.0938
- `SKIPPED_VETO`: settled=293, wins=191, hit_rate=0.651877, ROI=-0.080314
- `WATCHLIST_NO_ODDS`: settled=30, wins=20, hit_rate=0.666667, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.117333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=154, wins=103, hit_rate=0.668831, ROI=-0.036429
- `WATCHLIST_UNKNOWN_CTX`: settled=2, wins=2, hit_rate=1.0, ROI=0.23

## By odds source

- `UNKNOWN`: settled=38, wins=24, hit_rate=0.631579, ROI=None
- `betexplorer_odds`: settled=155, wins=103, hit_rate=0.664516, ROI=-0.061742
- `bzzoiro_odds`: settled=9, wins=8, hit_rate=0.888889, ROI=0.336667
- `forebet_best`: settled=65, wins=48, hit_rate=0.738462, ROI=0.105692
- `scoutingstats_odds`: settled=328, wins=216, hit_rate=0.658537, ROI=-0.050335
- `zulubet`: settled=1, wins=1, hit_rate=1.0, ROI=0.07

## By odds match method

- `alias_fuzzy`: settled=26, wins=19, hit_rate=0.730769, ROI=0.09
- `betexplorer`: settled=155, wins=103, hit_rate=0.664516, ROI=-0.061742
- `exact`: settled=337, wins=224, hit_rate=0.664688, ROI=-0.04
- `fallback`: settled=43, wins=32, hit_rate=0.744186, ROI=0.113256
- `none`: settled=35, wins=22, hit_rate=0.628571, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 155 | 103 | 0.664516 | 155 | -0.061742 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 9 | 8 | 0.888889 | 9 | 0.336667 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 328 | 216 | 0.658537 | 328 | -0.050335 |
| Source fallback (`SOURCE_FALLBACK`) | 43 | 32 | 0.744186 | 43 | 0.113256 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 26 | 19 | 0.730769 | 23 | 0.09 |
| No usable price (`UNMATCHED`) | 35 | 22 | 0.628571 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 293 | 191 | 0.651877 | 287 | -0.080314 |
| **trusted evidence only** | 91 | 59 | 0.648352 | 91 | -0.127033 |
| **soft evidence only** | 202 | 132 | 0.653465 | 196 | -0.058622 |
| evidence: BETEXPLORER_RESCUE | 86 | 54 | 0.627907 | 86 | -0.163953 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.508 |
| evidence: SCOUTINGSTATS_SOLE | 174 | 113 | 0.649425 | 174 | -0.062644 |
| evidence: SOURCE_FALLBACK | 14 | 10 | 0.714286 | 14 | -0.064286 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 8 | 0.03875 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 170 | 130 | 0.764706 | 170 | -0.029412 |
| odds band: 1.50-2.00 | 109 | 53 | 0.486239 | 109 | -0.191743 |
| odds band: 2.00-3.00 | 8 | 5 | 0.625 | 8 | 0.35625 |
| odds band: unpriced | 6 | 3 | 0.5 | 0 | None |
| veto reason: UNRECORDED | 2 | 2 | 1.0 | 2 | 0.075 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.13 |
| veto reason: context VETO in ['league', 'odds_band'] | 4 | 4 | 1.0 | 4 | 0.1725 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 7 | 1 | 0.142857 | 7 | -0.817143 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.25 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 4 | 2 | 0.5 | 4 | -0.2025 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['league', 'team_h'] | 13 | 9 | 0.692308 | 13 | -0.093846 |
| veto reason: context VETO in ['league'] | 17 | 13 | 0.764706 | 15 | 0.217333 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.25 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.273333 |
| veto reason: context VETO in ['odds_band'] | 46 | 33 | 0.717391 | 46 | -0.10413 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 12 | 9 | 0.75 | 12 | -0.078333 |
| veto reason: context VETO in ['team_a'] | 50 | 26 | 0.52 | 48 | -0.178333 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 12 | 11 | 0.916667 | 12 | 0.233333 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.103333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 8 | 0.470588 | 17 | -0.198824 |
| veto reason: context VETO in ['team_h'] | 62 | 36 | 0.580645 | 61 | -0.118361 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 28 | 21 | 0.75 | 28 | 0.078929 |
| contrast CAUTION: BZZOIRO_PRIMARY | 3 | 2 | 0.666667 | 3 | -0.003333 |
| contrast CAUTION: SOURCE_FALLBACK | 19 | 14 | 0.736842 | 19 | 0.181053 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 242 | 165 | 0.681818 | 207 | -0.008068 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 26 | 19 | 0.730769 | 23 | 0.09 | 26 | 1.569231 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 328 | 216 | 0.658537 | 328 | -0.050335 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-20: Nice vs Lille (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.12 -> 🔴 LOST (Expected prob: 59.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.3% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.9% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.3% (Actual: 3 goals)

### 2026-09-20: Persijap Jepara vs Persib Bandung (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.46 -> 🟢 WON (Expected prob: 59.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.1% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.8% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.1% (Actual: 3 goals)

### 2026-09-20: Saprissa vs CS Herediano (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.71 -> 🟢 WON (Expected prob: 66.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 85.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.2% (Actual: 2 goals)

### 2026-09-20: Sporting Kansas City vs Philadelphia Union (Actual Score: **3-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.6 -> 🟢 WON (Expected prob: 58.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 91.7% (Actual: 3 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.8% (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.6% (Actual: 7 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.0% (Actual: 7 goals)

### 2026-09-20: Kongsvinger vs Hodd (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 65.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.2% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.2% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.8% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.1% (Actual: 6 goals)

### 2026-09-20: Tvaakers IF vs Trelleborgs FF (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.71 -> 🟢 WON (Expected prob: 63.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.1% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.1% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.2% (Actual: 1 goals)

### 2026-09-20: Leeds vs Crystal Palace (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.73 -> 🔴 LOST (Expected prob: 58.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.6% (Actual: 0 goals)

### 2026-09-20: Karcagi SE vs Kozarmisleny SE (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.83 -> 🔴 LOST (Expected prob: 55.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 80.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.8% (Actual: 2 goals)

### 2026-09-20: Trans Narva vs Levadia Tallinn (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.27 -> 🔴 LOST (Expected prob: 80.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 83.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 31.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 92.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.3% (Actual: 2 goals)

### 2026-09-20: AZ Alkmaar vs SC Telstar (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.26 -> 🟢 WON (Expected prob: 73.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 89.1% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 52.5% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 34.3% (Actual: 1 goals)

### 2026-09-20: Marumo Gallants vs Orlando Pirates (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🟢 WON (Expected prob: 72.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 32.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 95.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.5% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 80.9% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.4% (Actual: 2 goals)

### 2026-09-20: Fenerbahçe vs Eyüpspor (Actual Score: **8-0**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 72.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.5% (Actual: 8 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.6% (Actual: 8 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.0% (Actual: 8 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 31.3% (Actual: 8 goals)

### 2026-09-20: Jeonbuk Motors vs Gwangju FC (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🔴 LOST (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.0% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.9% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 85.2% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.1% (Actual: 4 goals)

### 2026-09-20: Manchester City vs Sunderland (Actual Score: **5-3**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.6% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.2% (Actual: 8 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.0% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.7% (Actual: 8 goals)

### 2026-09-20: Kalamata vs Panathinaikos (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🟢 WON (Expected prob: 68.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.1% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.9% (Actual: 1 goals)

### 2026-09-20: Feyenoord vs Utrecht (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🟢 WON (Expected prob: 67.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.9% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.3% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.3% (Actual: 5 goals)

### 2026-09-20: Lokomotiv Plovdiv vs CSKA-Sofia (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.5 -> 🔴 LOST (Expected prob: 64.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.7% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.9% (Actual: 2 goals)

### 2026-09-20: Milan vs Lecce (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 62.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.2% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.6% (Actual: 3 goals)

### 2026-09-20: Brann vs Bodo/Glimt (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.61 -> 🔴 LOST (Expected prob: 60.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.8% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.3% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.9% (Actual: 3 goals)

### 2026-09-20: Pohang Steelers vs FC Seoul (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.8 -> 🔴 LOST (Expected prob: 55.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 83.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.8% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.0% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.0% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 3 goals)

### 2026-09-20: Bayer Leverkusen vs RB Leipzig (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.95 -> 🟢 WON (Expected prob: 59.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.5% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.7% (Actual: 2 goals)

### 2026-09-20: Villarreal vs Levante (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 58.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.0% (Actual: 4 goals)

### 2026-09-20: Chonburi FC vs Buriram United (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🟢 WON (Expected prob: 55.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.6% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.6% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.3% (Actual: 1 goals)

### 2026-09-20: Greifswalder vs Luckenwalde (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.5% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.2% (Actual: 4 goals)

### 2026-09-20: SV Wehen vs MSV Duisburg (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 2.05 -> 🟢 WON (Expected prob: 59.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.3% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.5% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.9% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.9% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.7% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.3% (Actual: 5 goals)

### 2026-09-20: Crvena Zvezda vs Radnicki Nis (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.14 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.0% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.6% (Actual: 3 goals)

### 2026-09-20: Haugesund vs Strommen (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.0% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.0% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.3% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 30.5% (Actual: 6 goals)

### 2026-09-20: Dender vs Patro Eisden (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🟢 WON (Expected prob: 73.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 50.3% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.1% (Actual: 1 goals)

### 2026-09-20: Raufoss vs Stromsgodset (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.28 -> 🟢 WON (Expected prob: 72.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 32.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.6% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.6% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.0% (Actual: 2 goals)

### 2026-09-20: Lech Poznan vs Radomiak Radom (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 68.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.4% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.9% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.0% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 85.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.2% (Actual: 6 goals)

### 2026-09-20: Ujpest FC vs Zalaegerszegi TE (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🟢 WON (Expected prob: 66.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.7% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 85.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.4% (Actual: 3 goals)

### 2026-09-20: Tromso vs HamKam (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 63.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.0% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.9% (Actual: 5 goals)

### 2026-09-20: St. Louis City vs Toronto FC (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🟢 WON (Expected prob: 62.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 85.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.1% (Actual: 4 goals)

### 2026-09-20: Stabaek vs Sogndal (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 61.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.7% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.1% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.7% (Actual: 3 goals)

### 2026-09-20: Nyiregyhaza vs Ferencvaros (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.75 -> 🔴 LOST (Expected prob: 55.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 83.6% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.7% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.1% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.3% (Actual: 2 goals)

### 2026-09-20: Sagamihara vs Giravanz K. (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.85 -> 🔴 LOST (Expected prob: 59.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.4% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 3 goals)

### 2026-09-20: Sukhothai FC vs Port FC (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🔴 LOST (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.1% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.9% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.4% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.1% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.2% (Actual: 3 goals)

### 2026-09-20: Viking vs Lillestrom (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 56.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.7% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.2% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.1% (Actual: 3 goals)

### 2026-09-20: Lausanne-Sport vs Lugano (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.85 -> 🟢 WON (Expected prob: 56.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.6% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.6% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.4% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.0% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.9% (Actual: 4 goals)

### 2026-09-20: FC Dallas vs Austin FC (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🔴 LOST (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.3% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.9% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 40.9% (Actual: 0 goals)

### 2026-09-20: Slavia Praha vs Viktoria Plzen (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.45 -> 🟢 WON (Expected prob: 55.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.7% (Actual: 3 goals)


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

## Pending / Unmatched Result Examples

- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']
- 2026-09-06 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Heart of Midlothian vs Dundee -> HOME @ None (pending_or_unmatched_result); keys=['heartofmi']/['dundee']
- 2026-09-06 `WATCHLIST_NO_ODDS` `ml-meta avg_p>=60` — Club America vs Club Tijuana -> HOME @ None (pending_or_unmatched_result); keys=['america']/['tijuana']
- 2026-09-08 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Young Africans vs Geita Gold -> HOME @ None (pending_or_unmatched_result); keys=['youngafri']/['geitagold']
- 2026-09-20 `SKIPPED_VETO` `ml-meta avg_p>=55` — Chicago Red Stars (w) vs Washington Spirit (w) -> AWAY @ 1.3 (pending_or_unmatched_result); keys=['chicagore']/['washingto']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)
- 2026-09-09 `SKIPPED_VETO` `ml-meta avg_p>=80` — VfB Stuttgart vs Viking (ambiguous_alias_result)
- 2026-09-10 `SKIPPED_VETO` `ml-meta avg_p>=70` — Bayern Munich vs Bodo/Glimt (ambiguous_alias_result)

# Edge Factory — Recent picks audit (2026-08-20 to 2026-09-18)

## Overall

- archived pick rows: 605
- archived pick dates: 30
- immutable morning-baseline rows: 605
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 29
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 558
- eligible prior picks: 582
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 4
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 376
- hit rate: +67.4%
- priced picks: 524
- ROI: -3.9%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-18
- same-day rows excluded: 23

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 324 / 512 matches (63.3%)
- **Both Teams to Score (BTTS)**: occurred in 271 / 512 matches (52.9%)
- **Selected Team Over 1.5 Goals**: occurred in 347 / 512 matches (67.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 558
- **Total Hits**: 403
- **Overall Hit Rate**: 72.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=4, hits=3, hit_rate=75.0%
- `away_under_35`: recommended=83, hits=79, hit_rate=95.2%
- `home_over_05`: recommended=43, hits=33, hit_rate=76.7%
- `home_under_25`: recommended=7, hits=7, hit_rate=100.0%
- `home_under_35`: recommended=11, hits=10, hit_rate=90.9%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=331, hits=213, hit_rate=64.4%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2432** | scored: 2432

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 551 | 551 | 347 | 63.0% | 47.3% | +15.7% | 0.256959 |
| `match_over_45` | 417 | 417 | 122 | 29.3% | 23.9% | +5.4% | 0.208302 |
| `away_under_35` | 401 | 401 | 387 | 96.5% | 97.3% | -0.8% | 0.032593 |
| `away_under_25` | 370 | 370 | 343 | 92.7% | 93.4% | -0.7% | 0.067998 |
| `home_over_05` | 243 | 243 | 214 | 88.1% | 84.4% | +3.6% | 0.105974 |
| `home_under_35` | 157 | 157 | 153 | 97.5% | 95.5% | +1.9% | 0.025217 |
| `home_under_25` | 121 | 121 | 111 | 91.7% | 91.6% | +0.1% | 0.075687 |
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
| hybrid_cohort | 2163 | 1614 | 74.6% | 70.2% | +4.4% | 0.132807 |
| model | 269 | 190 | 70.6% | 64.0% | +6.7% | 0.181931 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 123 | 19.1% | 23.6% | +4.5% |
| 0.2-0.3 | 251 | 24.9% | 31.1% | +6.2% |
| 0.3-0.4 | 73 | 33.1% | 42.5% | +9.4% |
| 0.4-0.5 | 411 | 45.3% | 61.3% | +16.1% |
| 0.5-0.6 | 138 | 53.2% | 65.9% | +12.7% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 412 | 84.4% | 86.2% | +1.8% |
| 0.9-1.0 | 1019 | 95.3% | 94.7% | -0.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=511, MAE=1.60863 goals, bias=-0.164521 (realized − promised), promised avg 3.522642 vs realized 3.358121

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 511 | 30.1% | 37.4% | +7.3% | 0.214261 |
| BTTS-Yes | 511 | 41.6% | 53.0% | +11.4% | 0.263199 |
| Home Over 1.5 | 511 | 64.9% | 56.9% | -7.9% | 0.255972 |
| Over 2.5 | 511 | 69.7% | 63.2% | -6.5% | 0.235217 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 235 | 8.8% | 26.4% | +17.5% |
| 0.1-0.2 | 278 | 10.4% | 27.3% | +16.9% |
| 0.2-0.3 | 9 | 22.4% | 44.4% | +22.0% |
| 0.3-0.4 | 100 | 37.4% | 55.0% | +17.6% |
| 0.4-0.5 | 399 | 43.2% | 52.6% | +9.4% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 337 | 66.7% | 60.8% | -5.9% |
| 0.7-0.8 | 155 | 74.7% | 66.5% | -8.3% |
| 0.8-0.9 | 479 | 84.5% | 67.2% | -17.2% |
| 0.9-1.0 | 51 | 92.0% | 76.5% | -15.5% |

## By rule

- `2way-unanimous avg_p>=70`: settled=117, wins=89, hit_rate=0.760684, ROI=0.0255
- `ml-meta avg_p>=55`: settled=328, wins=202, hit_rate=0.615854, ROI=-0.080096
- `ml-meta avg_p>=60`: settled=43, wins=36, hit_rate=0.837209, ROI=0.14186
- `ml-meta avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.2
- `ml-meta avg_p>=70`: settled=11, wins=10, hit_rate=0.909091, ROI=0.14
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=3, wins=3, hit_rate=1.0, ROI=0.1
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=55, wins=42, hit_rate=0.763636, ROI=0.166182
- `CERTIFIED_CLEAN`: settled=34, wins=24, hit_rate=0.705882, ROI=0.063824
- `SKIPPED_VETO`: settled=283, wins=183, hit_rate=0.646643, ROI=-0.100505
- `WATCHLIST_NO_ODDS`: settled=26, wins=18, hit_rate=0.692308, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.056667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=136, wins=90, hit_rate=0.661765, ROI=-0.047279
- `WATCHLIST_UNKNOWN_CTX`: settled=7, wins=7, hit_rate=1.0, ROI=0.221429

## By odds source

- `UNKNOWN`: settled=34, wins=22, hit_rate=0.647059, ROI=None
- `betexplorer_odds`: settled=154, wins=106, hit_rate=0.688312, ROI=-0.051688
- `bzzoiro_odds`: settled=10, wins=10, hit_rate=1.0, ROI=0.528
- `forebet_best`: settled=62, wins=45, hit_rate=0.725806, ROI=0.059677
- `scoutingstats_odds`: settled=298, wins=193, hit_rate=0.647651, ROI=-0.072416

## By odds match method

- `alias_fuzzy`: settled=25, wins=18, hit_rate=0.72, ROI=0.020909
- `betexplorer`: settled=154, wins=106, hit_rate=0.688312, ROI=-0.051688
- `exact`: settled=308, wins=203, hit_rate=0.659091, ROI=-0.052922
- `fallback`: settled=40, wins=29, hit_rate=0.725, ROI=0.081
- `none`: settled=31, wins=20, hit_rate=0.645161, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 154 | 106 | 0.688312 | 154 | -0.051688 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 10 | 10 | 1.0 | 10 | 0.528 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 298 | 193 | 0.647651 | 298 | -0.072416 |
| Source fallback (`SOURCE_FALLBACK`) | 40 | 29 | 0.725 | 40 | 0.081 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 25 | 18 | 0.72 | 22 | 0.020909 |
| No usable price (`UNMATCHED`) | 31 | 20 | 0.645161 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 283 | 183 | 0.646643 | 277 | -0.100505 |
| **trusted evidence only** | 94 | 63 | 0.670213 | 94 | -0.108936 |
| **soft evidence only** | 189 | 120 | 0.634921 | 183 | -0.096175 |
| evidence: BETEXPLORER_RESCUE | 89 | 58 | 0.651685 | 89 | -0.144719 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.528 |
| evidence: SCOUTINGSTATS_SOLE | 162 | 103 | 0.635802 | 162 | -0.093519 |
| evidence: SOURCE_FALLBACK | 14 | 9 | 0.642857 | 14 | -0.147143 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.055714 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 170 | 128 | 0.752941 | 170 | -0.049176 |
| odds band: 1.50-2.00 | 99 | 48 | 0.484848 | 99 | -0.200808 |
| odds band: 2.00-3.00 | 8 | 4 | 0.5 | 8 | 0.05 |
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
| veto reason: context VETO in ['league', 'team_h'] | 12 | 8 | 0.666667 | 12 | -0.115 |
| veto reason: context VETO in ['league'] | 15 | 10 | 0.666667 | 13 | 0.049231 |
| veto reason: context VETO in ['niche'] | 6 | 4 | 0.666667 | 6 | -0.056667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 4 | 4 | 1.0 | 4 | 0.26 |
| veto reason: context VETO in ['odds_band'] | 45 | 33 | 0.733333 | 45 | -0.069556 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.143333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 10 | 8 | 0.8 | 10 | -0.009 |
| veto reason: context VETO in ['team_a'] | 41 | 21 | 0.512195 | 39 | -0.164103 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 1 | 0.25 | 4 | -0.64 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.221818 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.446667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.123333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 8 | 0.470588 | 17 | -0.231176 |
| veto reason: context VETO in ['team_h'] | 64 | 38 | 0.59375 | 63 | -0.145714 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 33 | 24 | 0.727273 | 33 | 0.07697 |
| contrast CAUTION: BZZOIRO_PRIMARY | 4 | 4 | 1.0 | 4 | 0.535 |
| contrast CAUTION: SOURCE_FALLBACK | 18 | 14 | 0.777778 | 18 | 0.247778 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 235 | 165 | 0.702128 | 204 | 0.002745 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 25 | 18 | 0.72 | 22 | 0.020909 | 25 | 1.5388 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 298 | 193 | 0.647651 | 298 | -0.072416 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-17: FC Atyrau vs Ordabasy (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.58 -> 🟢 WON (Expected prob: 58.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.1% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.8% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.1% (Actual: 3 goals)

### 2026-09-17: Vasalunds IF vs Hammarby TTF (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.72 -> 🔴 LOST (Expected prob: 57.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.4% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.4% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.8% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.4% (Actual: 0 goals)

### 2026-09-17: Manchester City vs Norwich City (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.11 -> 🟢 WON (Expected prob: 71.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 50.4% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.6% (Actual: 5 goals)

### 2026-09-17: Real Betis vs Getafe (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🟢 WON (Expected prob: 58.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.4% (Actual: 1 goals)

### 2026-09-17: FC Nizhny Novgorod vs Leningradets (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.4% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.3% (Actual: 6 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.4% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.6% (Actual: 6 goals)

### 2026-09-17: Vålerenga W vs Haugesund W (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 70.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.7% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.1% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.1% (Actual: 3 goals)

### 2026-09-17: Juventus FC vs NEC Nijmegen (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.2% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 43.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.2% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.6% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.3% (Actual: 5 goals)

### 2026-09-17: Zeleznicar Pancevo vs Crvena Zvezda (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.4 -> 🟢 WON (Expected prob: 55.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.9% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.8% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 3 goals)


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

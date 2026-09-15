# Edge Factory — Recent picks audit (2026-08-17 to 2026-09-15)

## Overall

- archived pick rows: 583
- archived pick dates: 30
- immutable morning-baseline rows: 560
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 23
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 540
- eligible prior picks: 565
- pending/unmatched result picks: 8
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 5
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 4
- wins: 363
- hit rate: +67.2%
- priced picks: 507
- ROI: -3.3%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-15
- same-day rows excluded: 18

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 312 / 494 matches (63.2%)
- **Both Teams to Score (BTTS)**: occurred in 267 / 494 matches (54.0%)
- **Selected Team Over 1.5 Goals**: occurred in 335 / 494 matches (67.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 540
- **Total Hits**: 385
- **Overall Hit Rate**: 71.3%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=1, hits=0, hit_rate=0.0%
- `away_under_35`: recommended=72, hits=69, hit_rate=95.8%
- `home_over_05`: recommended=44, hits=34, hit_rate=77.3%
- `home_under_35`: recommended=11, hits=10, hit_rate=90.9%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=333, hits=214, hit_rate=64.3%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2390** | scored: 2390

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 533 | 533 | 335 | 62.9% | 47.6% | +15.3% | 0.255879 |
| `match_over_45` | 398 | 398 | 115 | 28.9% | 23.8% | +5.1% | 0.207956 |
| `away_under_35` | 392 | 392 | 379 | 96.7% | 97.6% | -0.9% | 0.030782 |
| `away_under_25` | 361 | 361 | 335 | 92.8% | 93.5% | -0.7% | 0.06736 |
| `home_over_05` | 259 | 259 | 229 | 88.4% | 84.5% | +4.0% | 0.103346 |
| `home_under_35` | 157 | 157 | 153 | 97.5% | 95.6% | +1.8% | 0.02508 |
| `home_under_25` | 115 | 115 | 105 | 91.3% | 91.7% | -0.4% | 0.079034 |
| `away_under_15` | 57 | 57 | 45 | 78.9% | 81.0% | -2.0% | 0.16863 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 27 | 27 | 24 | 88.9% | 89.2% | -0.3% | 0.094113 |
| `home_under_15` | 15 | 15 | 11 | 73.3% | 81.4% | -8.1% | 0.206266 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2121 | 1586 | 74.8% | 70.8% | +4.0% | 0.130857 |
| model | 269 | 194 | 72.1% | 64.5% | +7.6% | 0.182836 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 120 | 19.1% | 24.2% | +5.1% |
| 0.2-0.3 | 240 | 24.9% | 31.2% | +6.4% |
| 0.3-0.4 | 68 | 33.2% | 39.7% | +6.5% |
| 0.4-0.5 | 392 | 45.5% | 61.2% | +15.8% |
| 0.5-0.6 | 139 | 53.3% | 65.5% | +12.1% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 424 | 84.3% | 86.1% | +1.8% |
| 0.9-1.0 | 1002 | 95.4% | 94.8% | -0.6% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=493, MAE=1.594442 goals, bias=-0.169899 (realized − promised), promised avg 3.518783 vs realized 3.348884

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 493 | 30.1% | 37.1% | +7.1% | 0.216863 |
| BTTS-Yes | 493 | 41.6% | 54.2% | +12.6% | 0.265523 |
| Home Over 1.5 | 493 | 64.8% | 57.6% | -7.2% | 0.257057 |
| Over 2.5 | 493 | 69.7% | 63.1% | -6.6% | 0.235972 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 235 | 8.8% | 26.4% | +17.6% |
| 0.1-0.2 | 261 | 10.4% | 28.4% | +17.9% |
| 0.2-0.3 | 8 | 21.9% | 37.5% | +15.6% |
| 0.3-0.4 | 98 | 37.4% | 56.1% | +18.7% |
| 0.4-0.5 | 383 | 43.3% | 53.8% | +10.5% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 329 | 66.7% | 60.8% | -5.9% |
| 0.7-0.8 | 144 | 74.7% | 66.0% | -8.7% |
| 0.8-0.9 | 463 | 84.4% | 67.6% | -16.8% |
| 0.9-1.0 | 50 | 92.2% | 74.0% | -18.2% |

## By rule

- `2way-unanimous avg_p>=70`: settled=108, wins=81, hit_rate=0.75, ROI=0.029362
- `ml-meta avg_p>=55`: settled=325, wins=204, hit_rate=0.627692, ROI=-0.060163
- `ml-meta avg_p>=60`: settled=38, wins=30, hit_rate=0.789474, ROI=0.082632
- `ml-meta avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.2
- `ml-meta avg_p>=70`: settled=10, wins=9, hit_rate=0.9, ROI=0.148
- `ml-meta avg_p>=75`: settled=4, wins=3, hit_rate=0.75, ROI=-0.16
- `ml-meta avg_p>=80`: settled=2, wins=2, hit_rate=1.0, ROI=0.05
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=59, wins=45, hit_rate=0.762712, ROI=0.181017
- `CERTIFIED_CLEAN`: settled=30, wins=21, hit_rate=0.7, ROI=0.054333
- `SKIPPED_VETO`: settled=269, wins=174, hit_rate=0.64684, ROI=-0.094829
- `WATCHLIST_NO_ODDS`: settled=25, wins=17, hit_rate=0.68, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=17, wins=12, hit_rate=0.705882, ROI=0.056667
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=133, wins=87, hit_rate=0.654135, ROI=-0.050075
- `WATCHLIST_UNKNOWN_CTX`: settled=7, wins=7, hit_rate=1.0, ROI=0.221429

## By odds source

- `UNKNOWN`: settled=33, wins=21, hit_rate=0.636364, ROI=None
- `betexplorer_odds`: settled=152, wins=103, hit_rate=0.677632, ROI=-0.058882
- `bzzoiro_odds`: settled=13, wins=13, hit_rate=1.0, ROI=0.550769
- `forebet_best`: settled=59, wins=43, hit_rate=0.728814, ROI=0.073729
- `scoutingstats_odds`: settled=283, wins=183, hit_rate=0.646643, ROI=-0.068728

## By odds match method

- `alias_fuzzy`: settled=25, wins=18, hit_rate=0.72, ROI=0.020909
- `betexplorer`: settled=152, wins=103, hit_rate=0.677632, ROI=-0.058882
- `exact`: settled=296, wins=196, hit_rate=0.662162, ROI=-0.04152
- `fallback`: settled=37, wins=27, hit_rate=0.72973, ROI=0.105135
- `none`: settled=30, wins=19, hit_rate=0.633333, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 152 | 103 | 0.677632 | 152 | -0.058882 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 13 | 13 | 1.0 | 13 | 0.550769 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 283 | 183 | 0.646643 | 283 | -0.068728 |
| Source fallback (`SOURCE_FALLBACK`) | 37 | 27 | 0.72973 | 37 | 0.105135 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 25 | 18 | 0.72 | 22 | 0.020909 |
| No usable price (`UNMATCHED`) | 30 | 19 | 0.633333 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 269 | 174 | 0.64684 | 263 | -0.094829 |
| **trusted evidence only** | 93 | 62 | 0.666667 | 93 | -0.103763 |
| **soft evidence only** | 176 | 112 | 0.636364 | 170 | -0.089941 |
| evidence: BETEXPLORER_RESCUE | 87 | 56 | 0.643678 | 87 | -0.146897 |
| evidence: BZZOIRO_PRIMARY | 6 | 6 | 1.0 | 6 | 0.521667 |
| evidence: SCOUTINGSTATS_SOLE | 150 | 96 | 0.64 | 150 | -0.085267 |
| evidence: SOURCE_FALLBACK | 13 | 8 | 0.615385 | 13 | -0.162308 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.055714 |
| evidence: UNMATCHED | 5 | 2 | 0.4 | 0 | None |
| odds band: <1.50 | 163 | 122 | 0.748466 | 163 | -0.047485 |
| odds band: 1.50-2.00 | 93 | 46 | 0.494624 | 93 | -0.178495 |
| odds band: 2.00-3.00 | 7 | 3 | 0.428571 | 7 | -0.085714 |
| odds band: unpriced | 6 | 3 | 0.5 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 3 | 1.0 | 2 | 0.305 |
| veto reason: context VETO in ['league', 'odds_band'] | 5 | 5 | 1.0 | 5 | 0.146 |
| veto reason: context VETO in ['league', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 11 | 4 | 0.363636 | 11 | -0.573636 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.063333 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['league', 'team_h'] | 8 | 5 | 0.625 | 8 | -0.15625 |
| veto reason: context VETO in ['league'] | 11 | 7 | 0.636364 | 9 | -0.007778 |
| veto reason: context VETO in ['niche'] | 6 | 4 | 0.666667 | 6 | -0.056667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 3 | 3 | 1.0 | 3 | 0.24 |
| veto reason: context VETO in ['odds_band'] | 44 | 32 | 0.727273 | 44 | -0.066818 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.2 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.143333 |
| veto reason: context VETO in ['team_a'] | 42 | 22 | 0.52381 | 40 | -0.14375 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 1 | 0.25 | 4 | -0.64 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 11 | 10 | 0.909091 | 11 | 0.221818 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.446667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.123333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 8 | 0.470588 | 17 | -0.237059 |
| veto reason: context VETO in ['team_h'] | 62 | 37 | 0.596774 | 61 | -0.125738 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 35 | 25 | 0.714286 | 35 | 0.071143 |
| contrast CAUTION: BZZOIRO_PRIMARY | 7 | 7 | 1.0 | 7 | 0.575714 |
| contrast CAUTION: SOURCE_FALLBACK | 17 | 13 | 0.764706 | 17 | 0.244706 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 232 | 162 | 0.698276 | 202 | 0.010396 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 25 | 18 | 0.72 | 22 | 0.020909 | 25 | 1.5388 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 283 | 183 | 0.646643 | 283 | -0.068728 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-14: Real Tomayapo vs Bolívar (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.51 -> 🟢 WON (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 89.3% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.5% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.7% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.4% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.4% (Actual: 3 goals)

### 2026-09-14: Guadalajara Chivas vs UNAM Pumas (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.4% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 41.1% (Actual: 3 goals)

### 2026-09-14: Bodo/Glimt vs Sandefjord (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 72.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.4% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.5% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.1% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 32.1% (Actual: 5 goals)

### 2026-09-14: Ludogorets vs Septemvri Sofia (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.18 -> 🟢 WON (Expected prob: 71.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.9% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 30.4% (Actual: 3 goals)

### 2026-09-14: Como vs Parma (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 71.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.3% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 91.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.0% (Actual: 3 goals)

### 2026-09-14: Kayserispor vs Istanbulspor AS (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 68.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.9% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.5% (Actual: 4 goals)

### 2026-09-14: Inter vs Udinese (Actual Score: **5-3**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 64.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.9% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.7% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 3 away goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.5% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 8 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 21.5% (Actual: 8 goals)

### 2026-09-14: Gaziantep vs Fenerbahçe (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🔴 LOST (Expected prob: 62.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected 90.4% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 93.9% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.8% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 44.4% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.3% (Actual: 0 goals)

### 2026-09-14: Vikingur Reykjavik vs Keflavik (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 76.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.4% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.1% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.4% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 90.6% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.1% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 33.0% (Actual: 5 goals)

### 2026-09-14: FC Porto B vs FC Vizela (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.95 -> 🔴 LOST (Expected prob: 59.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 87.9% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 92.8% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.5% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.1% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.1% (Actual: 4 goals)

### 2026-09-14: SC Braga vs Estoril (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 60.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.1% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.3% (Actual: 1 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 5 |
- 2026-08-17 `POSTPONED` `SKIPPED_VETO` — Bucaramanga vs Deportivo Pasto (verified_disposition); excluded from win/loss/ROI
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

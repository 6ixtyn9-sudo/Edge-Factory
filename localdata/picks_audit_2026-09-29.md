# Edge Factory — Recent picks audit (2026-08-31 to 2026-09-29)

## Overall

- archived pick rows: 613
- archived pick dates: 30
- immutable morning-baseline rows: 613
- verified official late-slate additions: 0
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 30
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 577
- eligible prior picks: 597
- pending/unmatched result picks: 10
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 1
- ambiguous result picks: 3
- wins: 385
- hit rate: +66.7%
- priced picks: 532
- ROI: -4.3%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-29
- same-day rows excluded: 16

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 329 / 531 matches (62.0%)
- **Both Teams to Score (BTTS)**: occurred in 296 / 531 matches (55.7%)
- **Selected Team Over 1.5 Goals**: occurred in 344 / 531 matches (64.8%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 577
- **Total Hits**: 456
- **Overall Hit Rate**: 79.0%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_25`: recommended=24, hits=23, hit_rate=95.8%
- `away_under_35`: recommended=155, hits=150, hit_rate=96.8%
- `home_over_05`: recommended=25, hits=18, hit_rate=72.0%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=25, hits=24, hit_rate=96.0%
- `match_over_15`: recommended=43, hits=34, hit_rate=79.1%
- `match_over_25`: recommended=236, hits=152, hit_rate=64.4%
- `match_over_35`: recommended=18, hits=8, hit_rate=44.4%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2311** | scored: 2311

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 570 | 570 | 352 | 61.8% | 45.4% | +16.4% | 0.262887 |
| `match_over_45` | 451 | 451 | 120 | 26.6% | 23.8% | +2.8% | 0.192788 |
| `away_under_35` | 406 | 406 | 396 | 97.5% | 96.0% | +1.6% | 0.024079 |
| `away_under_25` | 367 | 367 | 335 | 91.3% | 92.0% | -0.7% | 0.079679 |
| `home_under_35` | 160 | 160 | 156 | 97.5% | 94.0% | +3.5% | 0.02658 |
| `home_under_25` | 127 | 127 | 117 | 92.1% | 90.7% | +1.4% | 0.072935 |
| `home_over_05` | 99 | 99 | 85 | 85.9% | 83.6% | +2.2% | 0.122608 |
| `match_over_15` | 43 | 43 | 34 | 79.1% | 85.3% | -6.2% | 0.167617 |
| `match_over_35` | 33 | 33 | 15 | 45.5% | 37.5% | +8.0% | 0.271169 |
| `away_over_05` | 31 | 31 | 28 | 90.3% | 88.2% | +2.1% | 0.086311 |
| `home_under_15` | 13 | 13 | 9 | 69.2% | 81.6% | -12.3% | 0.232124 |
| `away_under_15` | 8 | 8 | 6 | 75.0% | 80.8% | -5.8% | 0.195763 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2053 | 1472 | 71.7% | 66.9% | +4.8% | 0.136884 |
| model | 258 | 183 | 70.9% | 63.7% | +7.3% | 0.172978 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 117 | 19.2% | 19.7% | +0.5% |
| 0.2-0.3 | 286 | 24.3% | 26.9% | +2.6% |
| 0.3-0.4 | 83 | 33.4% | 49.4% | +16.0% |
| 0.4-0.5 | 486 | 44.4% | 60.9% | +16.5% |
| 0.5-0.6 | 82 | 52.3% | 61.0% | +8.7% |
| 0.8-0.9 | 311 | 85.6% | 86.2% | +0.6% |
| 0.9-1.0 | 946 | 94.4% | 95.1% | +0.7% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=530, MAE=1.578792 goals, bias=-0.240755 (realized − promised), promised avg 3.518113 vs realized 3.277358

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 530 | 31.2% | 35.1% | +3.9% | 0.228957 |
| BTTS-Yes | 530 | 41.7% | 55.7% | +14.0% | 0.266399 |
| Home Over 1.5 | 530 | 63.8% | 54.3% | -9.4% | 0.248153 |
| Over 2.5 | 530 | 69.6% | 61.9% | -7.7% | 0.241115 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 221 | 8.8% | 24.4% | +15.7% |
| 0.1-0.2 | 311 | 10.4% | 25.4% | +15.0% |
| 0.2-0.3 | 7 | 24.6% | 57.1% | +32.5% |
| 0.3-0.4 | 87 | 37.3% | 54.0% | +16.7% |
| 0.4-0.5 | 433 | 43.0% | 55.9% | +12.9% |
| 0.5-0.6 | 1 | 50.0% | 0.0% | -50.0% |
| 0.6-0.7 | 364 | 66.9% | 60.7% | -6.2% |
| 0.7-0.8 | 147 | 74.5% | 63.3% | -11.2% |
| 0.8-0.9 | 503 | 84.5% | 64.6% | -19.9% |
| 0.9-1.0 | 46 | 92.5% | 69.6% | -23.0% |

## By rule

- `2way-unanimous avg_p>=60`: settled=68, wins=42, hit_rate=0.617647, ROI=-0.166182
- `2way-unanimous avg_p>=70`: settled=92, wins=69, hit_rate=0.75, ROI=-0.014306
- `ml-meta avg_p>=55`: settled=303, wins=188, hit_rate=0.620462, ROI=-0.050616
- `ml-meta avg_p>=60`: settled=49, wins=42, hit_rate=0.857143, ROI=0.180204
- `ml-meta avg_p>=65`: settled=10, wins=8, hit_rate=0.8, ROI=0.05
- `ml-meta avg_p>=70`: settled=4, wins=3, hit_rate=0.75, ROI=-0.17
- `ml-meta avg_p>=75`: settled=1, wins=1, hit_rate=1.0, ROI=0.05
- `ml-meta avg_p>=80`: settled=4, wins=4, hit_rate=1.0, ROI=0.07
- `ou25-unanimous-2way-sa avg_p>=70`: settled=46, wins=28, hit_rate=0.608696, ROI=-0.148

## By bucket

- `CAUTION`: settled=51, wins=32, hit_rate=0.627451, ROI=-0.034118
- `CERTIFIED_CLEAN`: settled=57, wins=41, hit_rate=0.719298, ROI=0.128421
- `SKIPPED_VETO`: settled=272, wins=175, hit_rate=0.643382, ROI=-0.095703
- `WATCHLIST_NO_ODDS`: settled=34, wins=25, hit_rate=0.735294, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=16, wins=11, hit_rate=0.6875, ROI=0.098571
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=143, wins=98, hit_rate=0.685315, ROI=-0.028671
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=45, wins=32, hit_rate=0.711111, ROI=None
- `betexplorer_odds`: settled=152, wins=97, hit_rate=0.638158, ROI=-0.082566
- `bzzoiro_odds`: settled=6, wins=5, hit_rate=0.833333, ROI=0.275
- `forebet_best`: settled=84, wins=61, hit_rate=0.72619, ROI=0.082976
- `scoutingstats_odds`: settled=288, wins=188, hit_rate=0.652778, ROI=-0.067257
- `zulubet`: settled=2, wins=2, hit_rate=1.0, ROI=0.335

## By odds match method

- `alias_fuzzy`: settled=24, wins=17, hit_rate=0.708333, ROI=0.03619
- `betexplorer`: settled=152, wins=97, hit_rate=0.638158, ROI=-0.082566
- `exact`: settled=294, wins=193, hit_rate=0.656463, ROI=-0.060272
- `fallback`: settled=65, wins=48, hit_rate=0.738462, ROI=0.105846
- `none`: settled=42, wins=30, hit_rate=0.714286, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 152 | 97 | 0.638158 | 152 | -0.082566 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 6 | 5 | 0.833333 | 6 | 0.275 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 288 | 188 | 0.652778 | 288 | -0.067257 |
| Source fallback (`SOURCE_FALLBACK`) | 65 | 48 | 0.738462 | 65 | 0.105846 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 24 | 17 | 0.708333 | 21 | 0.03619 |
| No usable price (`UNMATCHED`) | 42 | 30 | 0.714286 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 272 | 175 | 0.643382 | 263 | -0.095703 |
| **trusted evidence only** | 86 | 53 | 0.616279 | 86 | -0.155814 |
| **soft evidence only** | 186 | 122 | 0.655914 | 177 | -0.066497 |
| evidence: BETEXPLORER_RESCUE | 83 | 50 | 0.60241 | 83 | -0.179518 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.5 |
| evidence: SCOUTINGSTATS_SOLE | 145 | 90 | 0.62069 | 145 | -0.10531 |
| evidence: SOURCE_FALLBACK | 25 | 21 | 0.84 | 25 | 0.1648 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 6 | 0.75 | 7 | -0.088571 |
| evidence: UNMATCHED | 8 | 5 | 0.625 | 0 | None |
| odds band: <1.50 | 157 | 116 | 0.738854 | 157 | -0.063376 |
| odds band: 1.50-2.00 | 100 | 49 | 0.49 | 100 | -0.1787 |
| odds band: 2.00-3.00 | 6 | 4 | 0.666667 | 6 | 0.441667 |
| odds band: unpriced | 9 | 6 | 0.666667 | 0 | None |
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
| veto reason: context VETO in ['league'] | 24 | 18 | 0.75 | 19 | 0.095263 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 54 | 37 | 0.685185 | 54 | -0.117037 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 1 | 0.5 | 2 | -0.085 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 6 | 0.666667 | 9 | -0.17 |
| veto reason: context VETO in ['team_a'] | 45 | 22 | 0.488889 | 43 | -0.218605 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 2 | 0.5 | 4 | -0.355 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 6 | 6 | 1.0 | 6 | 0.316667 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 5 | 3 | 0.6 | 5 | -0.218 |
| veto reason: context VETO in ['team_h', 'team_a'] | 14 | 6 | 0.428571 | 14 | -0.275 |
| veto reason: context VETO in ['team_h'] | 49 | 29 | 0.591837 | 48 | -0.087292 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 27 | 18 | 0.666667 | 27 | -0.007407 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: SOURCE_FALLBACK | 23 | 14 | 0.608696 | 23 | -0.023478 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 265 | 180 | 0.679245 | 223 | -0.018027 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 24 | 17 | 0.708333 | 21 | 0.03619 | 24 | 1.562083 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 288 | 188 | 0.652778 | 288 | -0.067257 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-28: Club León vs FC Juárez (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 70.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.4% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.9% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.8% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.4% (Actual: 3 goals)

### 2026-09-28: Curaçao vs Nicaragua (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🟢 WON (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.9% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.8% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 40.3% (Actual: 7 goals)

### 2026-09-28: Club Necaxa vs Club América (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.9 -> 🟢 WON (Expected prob: 56.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.3% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.1% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.6% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 18.7% (Actual: 6 goals)

### 2026-09-28: Hapoel Kfar Saba vs Bnei Yehuda (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.51 -> 🟢 WON (Expected prob: 67.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.5% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 88.9% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.5% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.3% (Actual: 3 goals)

### 2026-09-28: Tigres UANL W vs Atlético San Luis W (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.07 -> 🔴 LOST (Expected prob: 63.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.5% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.9% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.8% (Actual: 2 goals)


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

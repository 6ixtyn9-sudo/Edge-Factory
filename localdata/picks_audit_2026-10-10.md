# Edge Factory — Recent picks audit (2026-09-11 to 2026-10-10)

## Overall

- archived pick rows: 594
- archived pick dates: 30
- immutable morning-baseline rows: 591
- verified official late-slate additions: 5
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 26
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 521
- eligible prior picks: 537
- pending/unmatched result picks: 9
- rescheduled result picks (settled ±3d): 6
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 1
- wins: 359
- hit rate: +68.9%
- priced picks: 457
- ROI: -1.5%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-10
- same-day rows excluded: 57

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 324 / 521 matches (62.2%)
- **Both Teams to Score (BTTS)**: occurred in 285 / 521 matches (54.7%)
- **Selected Team Over 1.5 Goals**: occurred in 345 / 521 matches (66.2%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 521
- **Total Hits**: 425
- **Overall Hit Rate**: 81.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=21, hits=19, hit_rate=90.5%
- `away_under_25`: recommended=25, hits=24, hit_rate=96.0%
- `away_under_35`: recommended=165, hits=158, hit_rate=95.8%
- `home_over_05`: recommended=18, hits=15, hit_rate=83.3%
- `home_under_25`: recommended=33, hits=31, hit_rate=93.9%
- `home_under_35`: recommended=31, hits=31, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=207, hits=133, hit_rate=64.3%
- `match_over_35`: recommended=13, hits=7, hit_rate=53.8%
- `match_over_45`: recommended=1, hits=1, hit_rate=100.0%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2036** | scored: 2036

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 512 | 512 | 317 | 61.9% | 44.8% | +17.1% | 0.264499 |
| `match_over_45` | 416 | 416 | 105 | 25.2% | 23.9% | +1.4% | 0.186491 |
| `away_under_35` | 363 | 363 | 352 | 97.0% | 95.4% | +1.6% | 0.030055 |
| `away_under_25` | 341 | 341 | 310 | 90.9% | 90.8% | +0.1% | 0.083005 |
| `home_under_35` | 127 | 127 | 124 | 97.6% | 93.5% | +4.2% | 0.026581 |
| `home_under_25` | 125 | 125 | 115 | 92.0% | 89.9% | +2.1% | 0.07453 |
| `away_over_05` | 44 | 44 | 39 | 88.6% | 86.0% | +2.7% | 0.099451 |
| `away_under_15` | 33 | 33 | 24 | 72.7% | 82.0% | -9.3% | 0.206955 |
| `home_over_05` | 33 | 33 | 29 | 87.9% | 87.6% | +0.3% | 0.113059 |
| `match_over_35` | 22 | 22 | 11 | 50.0% | 39.1% | +10.9% | 0.29651 |
| `home_under_15` | 10 | 10 | 6 | 60.0% | 81.6% | -21.6% | 0.291265 |
| `match_over_15` | 7 | 7 | 6 | 85.7% | 82.9% | +2.8% | 0.120946 |
| `double_chance` | 3 | 3 | 2 | 66.7% | 83.7% | -17.1% | 0.257185 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1939 | 1371 | 70.7% | 65.6% | +5.1% | 0.140235 |
| model | 97 | 69 | 71.1% | 64.5% | +6.6% | 0.195724 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 89 | 19.2% | 20.2% | +1.1% |
| 0.2-0.3 | 281 | 24.1% | 24.2% | +0.1% |
| 0.3-0.4 | 71 | 33.4% | 50.7% | +17.3% |
| 0.4-0.5 | 455 | 44.2% | 60.7% | +16.4% |
| 0.5-0.6 | 54 | 51.6% | 64.8% | +13.2% |
| 0.8-0.9 | 321 | 86.7% | 87.9% | +1.2% |
| 0.9-1.0 | 765 | 94.0% | 94.8% | +0.8% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=520, MAE=1.575135 goals, bias=-0.263135 (realized − promised), promised avg 3.541981 vs realized 3.278846

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 520 | 31.1% | 34.0% | +2.9% | 0.211991 |
| BTTS-Yes | 520 | 41.4% | 54.6% | +13.2% | 0.265427 |
| Home Over 1.5 | 520 | 63.8% | 54.4% | -9.4% | 0.236861 |
| Over 2.5 | 520 | 69.7% | 62.1% | -7.6% | 0.242554 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 232 | 8.6% | 22.4% | +13.9% |
| 0.1-0.2 | 290 | 10.4% | 22.8% | +12.3% |
| 0.2-0.3 | 7 | 26.7% | 71.4% | +44.7% |
| 0.3-0.4 | 99 | 37.2% | 49.5% | +12.3% |
| 0.4-0.5 | 410 | 42.7% | 55.6% | +12.9% |
| 0.5-0.6 | 2 | 51.6% | 0.0% | -51.6% |
| 0.6-0.7 | 350 | 66.9% | 60.9% | -6.1% |
| 0.7-0.8 | 149 | 74.4% | 65.1% | -9.3% |
| 0.8-0.9 | 490 | 84.6% | 65.1% | -19.5% |
| 0.9-1.0 | 51 | 92.4% | 74.5% | -17.9% |

## By rule

- `2way-unanimous avg_p>=60`: settled=130, wins=81, hit_rate=0.623077, ROI=-0.142371
- `2way-unanimous avg_p>=70`: settled=68, wins=51, hit_rate=0.75, ROI=-0.084231
- `ml-meta avg_p>=55`: settled=241, wins=158, hit_rate=0.655602, ROI=0.013754
- `ml-meta avg_p>=60`: settled=58, wins=48, hit_rate=0.827586, ROI=0.138966
- `ml-meta avg_p>=65`: settled=14, wins=12, hit_rate=0.857143, ROI=0.041538
- `ml-meta avg_p>=70`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.266667
- `ml-meta avg_p>=80`: settled=7, wins=7, hit_rate=1.0, ROI=0.081667

## By bucket

- `CAUTION`: settled=36, wins=20, hit_rate=0.555556, ROI=-0.149028
- `CERTIFIED_CLEAN`: settled=62, wins=45, hit_rate=0.725806, ROI=0.127758
- `SKIPPED_VETO`: settled=261, wins=184, hit_rate=0.704981, ROI=-0.033618
- `WATCHLIST_NO_ODDS`: settled=47, wins=30, hit_rate=0.638298, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=5, hit_rate=1.0, ROI=0.653333
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=106, wins=72, hit_rate=0.679245, ROI=-0.025377
- `WATCHLIST_UNKNOWN_CTX`: settled=4, wins=3, hit_rate=0.75, ROI=-0.08

## By odds source

- `UNKNOWN`: settled=64, wins=44, hit_rate=0.6875, ROI=None
- `betexplorer_odds`: settled=151, wins=106, hit_rate=0.701987, ROI=-0.01
- `bzzoiro_odds`: settled=8, wins=7, hit_rate=0.875, ROI=0.27125
- `forebet_best`: settled=50, wins=36, hit_rate=0.72, ROI=0.0462
- `oddspapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.765
- `scoutingstats_odds`: settled=220, wins=145, hit_rate=0.659091, ROI=-0.051591
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=12, wins=10, hit_rate=0.833333, ROI=0.159167
- `zulubet`: settled=14, wins=9, hit_rate=0.642857, ROI=-0.128571

## By odds match method

- `alias_fuzzy`: settled=15, wins=13, hit_rate=0.866667, ROI=0.215833
- `betexplorer`: settled=132, wins=90, hit_rate=0.681818, ROI=-0.021212
- `exact`: settled=261, wins=180, hit_rate=0.689655, ROI=-0.017142
- `fallback`: settled=52, wins=35, hit_rate=0.673077, ROI=-0.04
- `none`: settled=61, wins=41, hit_rate=0.672131, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 132 | 90 | 0.681818 | 132 | -0.021212 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 8 | 7 | 0.875 | 8 | 0.27125 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 33 | 28 | 0.848485 | 33 | 0.142606 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 220 | 145 | 0.659091 | 220 | -0.051591 |
| Source fallback (`SOURCE_FALLBACK`) | 52 | 35 | 0.673077 | 52 | -0.04 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 15 | 13 | 0.866667 | 12 | 0.215833 |
| No usable price (`UNMATCHED`) | 61 | 41 | 0.672131 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 261 | 184 | 0.704981 | 246 | -0.033618 |
| **trusted evidence only** | 99 | 73 | 0.737374 | 99 | -0.019495 |
| **soft evidence only** | 162 | 111 | 0.685185 | 147 | -0.043129 |
| evidence: BETEXPLORER_RESCUE | 76 | 51 | 0.671053 | 76 | -0.096711 |
| evidence: BZZOIRO_PRIMARY | 5 | 5 | 1.0 | 5 | 0.404 |
| evidence: NAMED_BOOKMAKER_PRICE | 18 | 17 | 0.944444 | 18 | 0.188889 |
| evidence: SCOUTINGSTATS_SOLE | 114 | 73 | 0.640351 | 114 | -0.075965 |
| evidence: SOURCE_FALLBACK | 24 | 19 | 0.791667 | 24 | 0.070417 |
| evidence: SUSPECT_ALIAS_FUZZY | 10 | 8 | 0.8 | 9 | 0.07 |
| evidence: UNMATCHED | 14 | 11 | 0.785714 | 0 | None |
| odds band: <1.50 | 152 | 122 | 0.802632 | 152 | 0.003487 |
| odds band: 1.50-2.00 | 91 | 47 | 0.516484 | 91 | -0.135165 |
| odds band: 2.00-3.00 | 3 | 3 | 1.0 | 3 | 1.166667 |
| odds band: unpriced | 15 | 12 | 0.8 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.39 |
| veto reason: context VETO in ['league', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: context VETO in ['league', 'team_a'] | 6 | 1 | 0.166667 | 6 | -0.723333 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 2 | 1 | 0.5 | 2 | -0.4 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 2 | 0 | 0.0 | 2 | -1.0 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: context VETO in ['league', 'team_h'] | 11 | 9 | 0.818182 | 11 | 0.077273 |
| veto reason: context VETO in ['league'] | 26 | 19 | 0.730769 | 21 | 0.013333 |
| veto reason: context VETO in ['niche'] | 8 | 7 | 0.875 | 8 | 0.205 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.285 |
| veto reason: context VETO in ['odds_band'] | 52 | 40 | 0.769231 | 52 | -0.017308 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.193333 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 3 | 1 | 0.333333 | 3 | -0.556667 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 13 | 10 | 0.769231 | 13 | -0.044615 |
| veto reason: context VETO in ['team_a'] | 46 | 30 | 0.652174 | 42 | -0.05881 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.14 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.103333 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.026667 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.113333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 13 | 7 | 0.538462 | 12 | -0.096667 |
| veto reason: context VETO in ['team_h'] | 45 | 31 | 0.688889 | 41 | 0.013902 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 21 | 13 | 0.619048 | 21 | -0.050952 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 3 | 2 | 0.666667 | 3 | 0.101667 |
| contrast CAUTION: SOURCE_FALLBACK | 11 | 5 | 0.454545 | 11 | -0.327273 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 281 | 198 | 0.704626 | 220 | 0.014345 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 15 | 13 | 0.866667 | 12 | 0.215833 | 15 | 1.514 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 220 | 145 | 0.659091 | 220 | -0.051591 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 5 | 3 | 0.6 | 5 | -0.232 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-09: FC Nordsjaelland vs Odense (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🔴 LOST (Expected prob: 60.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.9% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.8% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 89.5% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.8% (Actual: 0 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 0 goals)

### 2026-10-09: Antigua GFC vs Municipal (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.58 -> 🔴 LOST (Expected prob: 55.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 67.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.2% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 83.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 98.1% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.7% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 43.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.5% (Actual: 2 goals)

### 2026-10-09: Cork City vs Finn Harps (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.13 -> 🟢 WON (Expected prob: 84.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 86.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 93.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 86.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 93.4% (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 85.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 38.6% (Actual: 2 goals)

### 2026-10-09: Karmiotissa vs Omonia Nicosia (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.21 -> 🟢 WON (Expected prob: 81.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 84.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 92.3% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.0% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 92.1% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 38.3% (Actual: 3 goals)

### 2026-10-09: PSV Eindhoven vs Heerenveen (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.26 -> 🟢 WON (Expected prob: 77.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.6% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 87.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.9% (Actual: 2 goals)

### 2026-10-09: Zlin vs Slavia Praha (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.28 -> 🟢 WON (Expected prob: 75.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 78.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.3% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.8% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 97.0% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 86.4% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.3% (Actual: 1 goals)

### 2026-10-09: Borussia Dortmund vs Werder Bremen (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.37 -> 🔴 LOST (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.9% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 93.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.2% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 27.6% (Actual: 4 goals)

### 2026-10-09: Fluminense vs Coritiba (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.47 -> 🟢 WON (Expected prob: 64.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.1% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.6% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.7% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.2% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 21.0% (Actual: 4 goals)

### 2026-10-09: Galatasaray vs Kasimpasa (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 61.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.7% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.0% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.4% (Actual: 4 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 4 goals)

### 2026-10-09: Corvinul Hunedoara vs FC Voluntari (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🟢 WON (Expected prob: 61.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.3% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.3% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 43.0% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.0% (Actual: 5 goals)

### 2026-10-09: Palmeiras vs Bahia (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.59 -> 🟢 WON (Expected prob: 56.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.8% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.9% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.2% (Actual: 1 goals)

### 2026-10-09: Shelbourne vs Sligo Rovers (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.37 -> 🟢 WON (Expected prob: 63.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.3% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 91.0% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.8% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.6% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 44.1% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.2% (Actual: 6 goals)

### 2026-10-09: Athlone Town vs Treaty United (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 57.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.4% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.6% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 3 goals)

### 2026-10-09: Penybont FC vs Barry Town (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🟢 WON (Expected prob: 56.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.1% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 94.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 4 goals)

### 2026-10-09: Vejle vs Hvidovre (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 57.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.0% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.4% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.6% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 42.1% (Actual: 3 goals)

### 2026-10-09: Montpellier vs Grenoble Foot 38 (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 89.8% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 42.2% (Actual: 2 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-09-14 `SKIPPED_VETO` `ml-meta avg_p>=55` — Vancouver Whitecaps vs Austin FC -> HOME @ 1.3 (rescheduled → 2026-09-13; actual Vancouver Whitecaps 1-2 Austin FC [away])
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

## Ambiguous result examples

- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Isidro Metapán vs Cacahuatique (ambiguous_alias_result)

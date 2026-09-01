# Edge Factory — Recent picks audit (2026-08-04 to 2026-09-02)

## Overall

- archived pick rows: 488
- archived pick dates: 30
- immutable morning-baseline rows: 360
- verified official late-slate additions: 13
- regular-ledger-only legacy rows: 115
- unsafe regular ledgers ignored: 15
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 456
- eligible prior picks: 476
- pending/unmatched result picks: 5
- rescheduled result picks (settled ±3d): 4
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 2
- wins: 312
- hit rate: +68.4%
- priced picks: 427
- ROI: -2.4%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-09-02
- same-day rows excluded: 12

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 286 / 444 matches (64.4%)
- **Both Teams to Score (BTTS)**: occurred in 241 / 444 matches (54.3%)
- **Selected Team Over 1.5 Goals**: occurred in 311 / 444 matches (70.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 456
- **Total Hits**: 342
- **Overall Hit Rate**: 75.0%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=8, hits=8, hit_rate=100.0%
- `btts_yes`: recommended=11, hits=6, hit_rate=54.5%
- `goal_range_2_3`: recommended=1, hits=0, hit_rate=0.0%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=141, hits=128, hit_rate=90.8%
- `home_under_25`: recommended=3, hits=3, hit_rate=100.0%
- `home_under_35`: recommended=11, hits=11, hit_rate=100.0%
- `match_over_15`: recommended=2, hits=2, hit_rate=100.0%
- `match_over_25`: recommended=253, hits=167, hit_rate=66.0%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2459** | scored: 2459

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 404 | 404 | 259 | 64.1% | 46.5% | +17.6% | 0.261906 |
| `away_under_35` | 348 | 348 | 340 | 97.7% | 98.0% | -0.3% | 0.021825 |
| `match_over_45` | 338 | 338 | 93 | 27.5% | 24.6% | +2.9% | 0.20144 |
| `away_under_25` | 331 | 331 | 310 | 93.7% | 94.1% | -0.5% | 0.05994 |
| `home_over_05` | 331 | 331 | 299 | 90.3% | 86.5% | +3.8% | 0.088699 |
| `away_under_15` | 123 | 123 | 98 | 79.7% | 81.4% | -1.7% | 0.162248 |
| `home_under_35` | 99 | 99 | 98 | 99.0% | 95.5% | +3.5% | 0.011311 |
| `home_under_25` | 89 | 89 | 81 | 91.0% | 91.8% | -0.8% | 0.082712 |
| `match_over_35` | 84 | 84 | 30 | 35.7% | 43.5% | -7.8% | 0.234744 |
| `exact_4` | 51 | 51 | 11 | 21.6% | 18.4% | +3.2% | 0.170665 |
| `goal_range_4_5` | 50 | 50 | 16 | 32.0% | 31.0% | +1.0% | 0.220887 |
| `goal_range_4_6` | 50 | 50 | 20 | 40.0% | 38.1% | +1.9% | 0.245659 |
| `exact_5` | 49 | 49 | 5 | 10.2% | 12.6% | -2.4% | 0.092989 |
| `btts_no` | 33 | 33 | 13 | 39.4% | 52.0% | -12.7% | 0.2576 |
| `away_over_05` | 21 | 21 | 19 | 90.5% | 86.0% | +4.4% | 0.089524 |
| `exact_3` | 18 | 18 | 4 | 22.2% | 22.2% | +0.0% | 0.173217 |
| `btts_yes` | 15 | 15 | 9 | 60.0% | 48.4% | +11.6% | 0.265843 |
| `home_under_15` | 12 | 12 | 11 | 91.7% | 81.2% | +10.5% | 0.08671 |
| `goal_range_6_plus` | 7 | 7 | 1 | 14.3% | 16.3% | -2.0% | 0.110594 |
| `exact_2` | 2 | 2 | 0 | 0.0% | 23.6% | -23.6% | 0.055595 ⚠️low-n |
| `match_over_15` | 2 | 2 | 2 | 100.0% | 82.2% | +17.8% | 0.031803 ⚠️low-n |
| `goal_range_2_3` | 1 | 1 | 0 | 0.0% | 46.4% | -46.4% | 0.215658 ⚠️low-n |
| `goal_range_7_plus` | 1 | 1 | 1 | 100.0% | 10.5% | +89.5% | 0.800604 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2331 | 1628 | 69.8% | 66.8% | +3.0% | 0.132256 |
| model | 128 | 92 | 71.9% | 58.8% | +13.1% | 0.215929 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 174 | 16.8% | 19.0% | +2.1% |
| 0.2-0.3 | 270 | 25.2% | 28.9% | +3.7% |
| 0.3-0.4 | 215 | 35.5% | 41.9% | +6.4% |
| 0.4-0.5 | 282 | 45.5% | 58.2% | +12.6% |
| 0.5-0.6 | 157 | 53.1% | 59.9% | +6.8% |
| 0.6-0.7 | 5 | 63.0% | 60.0% | -3.0% |
| 0.8-0.9 | 452 | 84.3% | 86.9% | +2.7% |
| 0.9-1.0 | 904 | 95.6% | 95.7% | +0.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=443, MAE=1.530068 goals, bias=-0.212235 (realized − promised), promised avg 3.573409 vs realized 3.361174

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 443 | 27.0% | 35.9% | +8.9% | 0.206111 |
| BTTS-Yes | 443 | 41.5% | 54.4% | +12.9% | 0.266303 |
| Home Over 1.5 | 443 | 68.2% | 59.4% | -8.9% | 0.239258 |
| Over 2.5 | 443 | 70.5% | 64.3% | -6.2% | 0.230464 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 288 | 8.9% | 23.3% | +14.4% |
| 0.1-0.2 | 157 | 10.5% | 29.9% | +19.5% |
| 0.2-0.3 | 4 | 21.2% | 25.0% | +3.8% |
| 0.3-0.4 | 101 | 37.5% | 57.4% | +19.9% |
| 0.4-0.5 | 336 | 43.0% | 53.6% | +10.5% |
| 0.6-0.7 | 256 | 66.8% | 60.5% | -6.3% |
| 0.7-0.8 | 171 | 74.8% | 67.3% | -7.6% |
| 0.8-0.9 | 401 | 84.8% | 68.6% | -16.2% |
| 0.9-1.0 | 58 | 91.8% | 86.2% | -5.6% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=130, wins=101, hit_rate=0.776923, ROI=0.079397
- `2way-unanimous min_p>=60 avg_p>=65`: settled=9, wins=7, hit_rate=0.777778, ROI=0.061429
- `3way-unanimous avg_p>=65`: settled=19, wins=14, hit_rate=0.736842, ROI=0.028421
- `ml-meta avg_p>=55`: settled=210, wins=130, hit_rate=0.619048, ROI=-0.0731
- `ml-meta avg_p>=60`: settled=25, wins=20, hit_rate=0.8, ROI=0.132
- `ml-meta avg_p>=65`: settled=5, wins=4, hit_rate=0.8, ROI=0.035
- `ml-meta avg_p>=70`: settled=9, wins=8, hit_rate=0.888889, ROI=0.182222
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23
- `ml-meta avg_p>=80`: settled=1, wins=1, hit_rate=1.0, ROI=0.06
- `ou25-unanimous-2way-sa avg_p>=70`: settled=12, wins=6, hit_rate=0.5, ROI=-0.286667

## By bucket

- `CAUTION`: settled=75, wins=49, hit_rate=0.653333, ROI=0.0196
- `CERTIFIED_CLEAN`: settled=29, wins=15, hit_rate=0.517241, ROI=-0.246897
- `SKIPPED_VETO`: settled=230, wins=162, hit_rate=0.704348, ROI=-0.009737
- `WATCHLIST_NO_ODDS`: settled=26, wins=19, hit_rate=0.730769, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=6, wins=4, hit_rate=0.666667, ROI=0.01
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=74, wins=49, hit_rate=0.662162, ROI=-0.045
- `WATCHLIST_UNKNOWN_CTX`: settled=16, wins=14, hit_rate=0.875, ROI=0.07125

## By odds source

- `UNKNOWN`: settled=29, wins=19, hit_rate=0.655172, ROI=None
- `betexplorer_odds`: settled=152, wins=105, hit_rate=0.690789, ROI=-0.032237
- `bzzoiro_odds`: settled=73, wins=47, hit_rate=0.643836, ROI=-0.043562
- `forebet_best`: settled=32, wins=23, hit_rate=0.71875, ROI=0.0175
- `scoutingstats_odds`: settled=161, wins=109, hit_rate=0.677019, ROI=-0.033416
- `zulubet`: settled=9, wins=9, hit_rate=1.0, ROI=0.316667

## By odds match method

- `alias_fuzzy`: settled=14, wins=11, hit_rate=0.785714, ROI=0.111538
- `betexplorer`: settled=152, wins=105, hit_rate=0.690789, ROI=-0.032237
- `exact`: settled=233, wins=155, hit_rate=0.665236, ROI=-0.037468
- `fallback`: settled=29, wins=22, hit_rate=0.758621, ROI=0.073448
- `none`: settled=28, wins=19, hit_rate=0.678571, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 152 | 105 | 0.690789 | 152 | -0.032237 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 72 | 46 | 0.638889 | 72 | -0.046528 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 161 | 109 | 0.677019 | 161 | -0.033416 |
| Source fallback (`SOURCE_FALLBACK`) | 29 | 22 | 0.758621 | 29 | 0.073448 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 14 | 11 | 0.785714 | 13 | 0.111538 |
| No usable price (`UNMATCHED`) | 28 | 19 | 0.678571 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 230 | 162 | 0.704348 | 228 | -0.009737 |
| **trusted evidence only** | 122 | 87 | 0.713115 | 122 | -0.013852 |
| **soft evidence only** | 108 | 75 | 0.694444 | 106 | -0.005 |
| evidence: BETEXPLORER_RESCUE | 80 | 58 | 0.725 | 80 | -0.03025 |
| evidence: BZZOIRO_PRIMARY | 42 | 29 | 0.690476 | 42 | 0.017381 |
| evidence: SCOUTINGSTATS_SOLE | 87 | 60 | 0.689655 | 87 | -0.023563 |
| evidence: SOURCE_FALLBACK | 11 | 8 | 0.727273 | 11 | 0.010909 |
| evidence: SUSPECT_ALIAS_FUZZY | 8 | 7 | 0.875 | 8 | 0.175 |
| evidence: UNMATCHED | 2 | 0 | 0.0 | 0 | None |
| odds band: <1.50 | 149 | 117 | 0.785235 | 149 | 0.011946 |
| odds band: 1.50-2.00 | 74 | 42 | 0.567568 | 74 | -0.070946 |
| odds band: 2.00-3.00 | 5 | 3 | 0.6 | 5 | 0.25 |
| odds band: unpriced | 2 | 0 | 0.0 | 0 | None |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.05 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.01 |
| veto reason: context VETO in ['league', 'team_a'] | 8 | 4 | 0.5 | 8 | -0.41375 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.66 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league'] | 11 | 7 | 0.636364 | 10 | 0.054 |
| veto reason: context VETO in ['niche'] | 3 | 1 | 0.333333 | 3 | -0.426667 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 2 | 1.0 | 2 | 0.235 |
| veto reason: context VETO in ['odds_band'] | 48 | 40 | 0.833333 | 48 | 0.101667 |
| veto reason: context VETO in ['team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.6 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 11 | 9 | 0.818182 | 11 | 0.055455 |
| veto reason: context VETO in ['team_a'] | 36 | 25 | 0.694444 | 35 | 0.084857 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 13 | 11 | 0.846154 | 13 | 0.163077 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.3 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.055 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 8 | 0.470588 | 17 | -0.311765 |
| veto reason: context VETO in ['team_h'] | 55 | 34 | 0.618182 | 55 | -0.104364 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 2 | 2 | 1.0 | 2 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 1 | 1 | 1.0 | 1 | 0.19 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 43 | 27 | 0.627907 | 43 | -0.008605 |
| contrast CAUTION: BZZOIRO_PRIMARY | 20 | 13 | 0.65 | 20 | 0.0025 |
| contrast CAUTION: SOURCE_FALLBACK | 12 | 9 | 0.75 | 12 | 0.149167 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 281 | 192 | 0.683274 | 253 | -0.02419 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 14 | 11 | 0.785714 | 13 | 0.111538 | 13 | 1.376538 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 161 | 109 | 0.677019 | 161 | -0.033416 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-09-01: Motor Lublin vs Legia Warszawa (Actual Score: **3-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.74 -> 🔴 LOST (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.6% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 99.0% (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 92.0% (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.7% (Actual: 3 goals)

### 2026-09-01: KR Reykjavik vs Vikingur Reykjavik (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.2 -> 🔴 LOST (Expected prob: 83.0%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 55.7% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.7% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 36.1% (Actual: 2 goals)

### 2026-09-01: Zürich vs Young Boys (Actual Score: **2-4**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.36 -> 🟢 WON (Expected prob: 71.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.8% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 96.6% (Actual: 2 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 19.9% (Actual: 6 goals)

### 2026-09-01: Lincoln City vs Blackburn Rovers (Actual Score: **0-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.9 -> 🔴 LOST (Expected prob: 70.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.7% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 88.3% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 41.2% (Actual: 0 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 9 |
- 2026-08-08 `POSTPONED` `SKIPPED_VETO` — Belshina vs Dinamo Minsk (verified_disposition); excluded from win/loss/ROI
- 2026-08-11 `POSTPONED` `WATCHLIST_UNCORROBORATED_PRICE` — Junior vs Pereira (verified_disposition); excluded from win/loss/ROI
- 2026-08-15 `POSTPONED` `SKIPPED_VETO` — Slavia Sofia vs Levski Sofia (verified_disposition); excluded from win/loss/ROI
- 2026-08-16 `POSTPONED` `SKIPPED_VETO` — SC Braga vs Gil Vicente (verified_disposition); excluded from win/loss/ROI
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

## Pending / Unmatched Result Examples

- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Lokomotiv Sofia vs CSKA-Sofia -> AWAY @ 1.61 (pending_or_unmatched_result); keys=['lokomotiv']/['cskasofia']
- 2026-08-23 `SKIPPED_VETO` `ml-meta avg_p>=60` — Panathinaikos vs Kifisia -> HOME @ 1.27 (pending_or_unmatched_result); keys=['panathina']/['kifisia']
- 2026-08-23 `WATCHLIST_UNCORROBORATED_PRICE` `2way-unanimous avg_p>=70` — Paris Saint Germain vs Rennes -> HOME @ 5.5 (pending_or_unmatched_result); keys=['parissain']/['rennes']
- 2026-08-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — MC Alger vs MC Oran -> HOME @ 1.44 (pending_or_unmatched_result); keys=['mcalger']/['mcoran']
- 2026-09-01 `CAUTION` `ml-meta avg_p>=55` — Gor Mahia vs Murang'a SEAL -> HOME @ 1.43 (pending_or_unmatched_result); keys=['gormahia']/['murangase']

## Ambiguous result examples

- 2026-08-24 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — VSG Altglienicke vs Wolfsburg (ambiguous_alias_result)
- 2026-08-28 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Pen-y-Bont FC vs Flint Town Utd (ambiguous_alias_result)

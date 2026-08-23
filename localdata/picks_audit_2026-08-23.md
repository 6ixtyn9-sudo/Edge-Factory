# Edge Factory — Recent picks audit (2026-07-25 to 2026-08-23)

## Overall

- archived pick rows: 387
- archived pick dates: 30
- immutable morning-baseline rows: 244
- verified official late-slate additions: 25
- regular-ledger-only legacy rows: 118
- unsafe regular ledgers ignored: 7
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 343
- eligible prior 1x2 picks: 360
- pending/unmatched result picks: 15
- voided postponed/cancelled/abandoned events: 2
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 10
- ambiguous result picks: 0
- wins: 242
- hit rate: +70.6%
- priced picks: 321
- ROI: -1.5%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-23
- same-day rows excluded: 27

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 220 / 343 matches (64.1%)
- **Both Teams to Score (BTTS)**: occurred in 176 / 343 matches (51.3%)
- **Selected Team Over 1.5 Goals**: occurred in 240 / 343 matches (70.0%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 318
- **Total Hits**: 244
- **Overall Hit Rate**: 76.7%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, hits=16, hit_rate=88.9%
- `away_under_35`: recommended=7, hits=7, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=121, hits=111, hit_rate=91.7%
- `home_under_25`: recommended=2, hits=2, hit_rate=100.0%
- `home_under_35`: recommended=9, hits=9, hit_rate=100.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=120, hits=79, hit_rate=65.8%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1935** | scored: 1935

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 249 | 249 | 157 | 63.1% | 45.7% | +17.4% | 0.268242 |
| `away_under_35` | 246 | 246 | 241 | 98.0% | 97.9% | +0.1% | 0.019121 |
| `away_under_25` | 231 | 231 | 217 | 93.9% | 93.7% | +0.3% | 0.057885 |
| `home_over_05` | 227 | 227 | 211 | 93.0% | 87.2% | +5.8% | 0.069447 |
| `match_over_45` | 212 | 212 | 55 | 25.9% | 24.9% | +1.1% | 0.194169 |
| `match_over_35` | 98 | 98 | 38 | 38.8% | 43.0% | -4.2% | 0.244783 |
| `away_under_15` | 88 | 88 | 73 | 83.0% | 81.5% | +1.5% | 0.140877 |
| `exact_4` | 67 | 67 | 17 | 25.4% | 18.0% | +7.3% | 0.196872 |
| `home_under_35` | 67 | 67 | 63 | 94.0% | 94.3% | -0.3% | 0.055641 |
| `goal_range_4_6` | 63 | 63 | 26 | 41.3% | 37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | 33.9% | 30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | 10.5% | 12.6% | -2.1% | 0.096166 |
| `home_under_25` | 54 | 54 | 51 | 94.4% | 91.3% | +3.2% | 0.05425 |
| `btts_no` | 40 | 40 | 17 | 42.5% | 52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | 50.0% | 50.9% | -0.9% | 0.248905 |
| `exact_3` | 32 | 32 | 4 | 12.5% | 22.2% | -9.7% | 0.119085 |
| `goal_range_2_3` | 26 | 26 | 8 | 30.8% | 46.1% | -15.4% | 0.233772 |
| `exact_2` | 24 | 24 | 5 | 20.8% | 24.5% | -3.7% | 0.166543 |
| `away_over_05` | 22 | 22 | 19 | 86.4% | 86.0% | +0.3% | 0.117067 |
| `goal_range_6_plus` | 9 | 9 | 1 | 11.1% | 18.7% | -7.6% | 0.102748 |
| `home_under_15` | 9 | 9 | 8 | 88.9% | 81.2% | +7.7% | 0.104019 |
| `match_over_15` | 8 | 8 | 7 | 87.5% | 85.7% | +1.8% | 0.122786 |
| `exact_1` | 4 | 4 | 1 | 25.0% | 21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | 33.3% | 13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | 0.0% | 11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | 100.0% | 35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1607 | 1083 | 67.4% | 64.7% | +2.7% | 0.129465 |
| legacy | 263 | 136 | 51.7% | 52.1% | -0.4% | 0.183796 |
| model | 65 | 47 | 72.3% | 52.9% | +19.5% | 0.265477 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 168 | 16.1% | 19.6% | +3.5% |
| 0.2-0.3 | 237 | 24.9% | 25.3% | +0.4% |
| 0.3-0.4 | 227 | 35.5% | 44.5% | +9.0% |
| 0.4-0.5 | 208 | 45.2% | 49.5% | +4.4% |
| 0.5-0.6 | 129 | 53.1% | 53.5% | +0.4% |
| 0.6-0.7 | 10 | 64.2% | 80.0% | +15.8% |
| 0.7-0.8 | 4 | 74.4% | 50.0% | -24.4% |
| 0.8-0.9 | 320 | 84.4% | 89.1% | +4.6% |
| 0.9-1.0 | 632 | 95.3% | 95.7% | +0.4% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=317, MAE=1.473628 goals, bias=-0.302461 (realized − promised), promised avg 3.608454 vs realized 3.305994

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 317 | 25.1% | 32.8% | +7.7% | 0.196995 |
| BTTS-Yes | 317 | 41.4% | 51.4% | +10.0% | 0.258313 |
| Home Over 1.5 | 317 | 70.3% | 59.0% | -11.4% | 0.220402 |
| Over 2.5 | 317 | 71.0% | 63.4% | -7.6% | 0.234794 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 218 | 8.9% | 18.8% | +9.9% |
| 0.1-0.2 | 101 | 10.5% | 28.7% | +18.3% |
| 0.2-0.3 | 1 | 21.4% | 0.0% | -21.4% |
| 0.3-0.4 | 81 | 37.7% | 49.4% | +11.7% |
| 0.4-0.5 | 233 | 43.0% | 52.4% | +9.4% |
| 0.6-0.7 | 167 | 66.9% | 58.1% | -8.8% |
| 0.7-0.8 | 136 | 74.8% | 67.6% | -7.1% |
| 0.8-0.9 | 278 | 85.0% | 68.7% | -16.3% |
| 0.9-1.0 | 53 | 91.9% | 81.1% | -10.7% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=33, wins=19, hit_rate=0.575758, ROI=-0.213548
- `2way-unanimous avg_p>=70`: settled=111, wins=90, hit_rate=0.810811, ROI=0.08043
- `2way-unanimous min_p>=60 avg_p>=65`: settled=7, wins=6, hit_rate=0.857143, ROI=0.238333
- `3way-unanimous avg_p>=65`: settled=49, wins=36, hit_rate=0.734694, ROI=-0.000938
- `ml-meta avg_p>=55`: settled=125, wins=77, hit_rate=0.616, ROI=-0.070924
- `ml-meta avg_p>=60`: settled=7, wins=5, hit_rate=0.714286, ROI=0.0
- `ml-meta avg_p>=65`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.25
- `ml-meta avg_p>=70`: settled=5, wins=5, hit_rate=1.0, ROI=0.37
- `ml-meta avg_p>=75`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.23

## By bucket

- `CAUTION`: settled=71, wins=42, hit_rate=0.591549, ROI=-0.061268
- `CERTIFIED_CLEAN`: settled=21, wins=9, hit_rate=0.428571, ROI=-0.375714
- `SKIPPED_VETO`: settled=172, wins=127, hit_rate=0.738372, ROI=0.013651
- `WATCHLIST_NO_ODDS`: settled=21, wins=18, hit_rate=0.857143, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=5, wins=3, hit_rate=0.6, ROI=-0.0825
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=32, wins=24, hit_rate=0.75, ROI=0.098125
- `WATCHLIST_UNKNOWN_CTX`: settled=21, wins=19, hit_rate=0.904762, ROI=0.100476

## By odds source

- `UNKNOWN`: settled=22, wins=18, hit_rate=0.818182, ROI=None
- `betexplorer_odds`: settled=122, wins=92, hit_rate=0.754098, ROI=0.051967
- `bzzoiro_odds`: settled=88, wins=58, hit_rate=0.659091, ROI=-0.046955
- `forebet_best`: settled=16, wins=10, hit_rate=0.625, ROI=-0.149375
- `scoutingstats_odds`: settled=84, wins=53, hit_rate=0.630952, ROI=-0.102262
- `zulubet`: settled=11, wins=11, hit_rate=1.0, ROI=0.345455

## By odds match method

- `alias_fuzzy`: settled=18, wins=12, hit_rate=0.666667, ROI=-0.112353
- `betexplorer`: settled=122, wins=92, hit_rate=0.754098, ROI=0.051967
- `exact`: settled=164, wins=106, hit_rate=0.646341, ROI=-0.066354
- `fallback`: settled=18, wins=14, hit_rate=0.777778, ROI=0.082222
- `none`: settled=21, wins=18, hit_rate=0.857143, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 122 | 92 | 0.754098 | 122 | 0.051967 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 80 | 53 | 0.6625 | 80 | -0.02865 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 84 | 53 | 0.630952 | 84 | -0.102262 |
| Source fallback (`SOURCE_FALLBACK`) | 18 | 14 | 0.777778 | 18 | 0.082222 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 18 | 12 | 0.666667 | 17 | -0.112353 |
| No usable price (`UNMATCHED`) | 21 | 18 | 0.857143 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 172 | 127 | 0.738372 | 172 | 0.013651 |
| **trusted evidence only** | 109 | 85 | 0.779817 | 109 | 0.069523 |
| **soft evidence only** | 63 | 42 | 0.666667 | 63 | -0.083016 |
| evidence: BETEXPLORER_RESCUE | 61 | 51 | 0.836066 | 61 | 0.113443 |
| evidence: BZZOIRO_PRIMARY | 48 | 34 | 0.708333 | 48 | 0.013708 |
| evidence: SCOUTINGSTATS_SOLE | 44 | 27 | 0.613636 | 44 | -0.151136 |
| evidence: SOURCE_FALLBACK | 10 | 8 | 0.8 | 10 | 0.145 |
| evidence: SUSPECT_ALIAS_FUZZY | 9 | 7 | 0.777778 | 9 | -0.003333 |
| odds band: <1.50 | 123 | 99 | 0.804878 | 123 | 0.036407 |
| odds band: 1.50-2.00 | 46 | 26 | 0.565217 | 46 | -0.06913 |
| odds band: 2.00-3.00 | 3 | 2 | 0.666667 | 3 | 0.35 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.19 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 6 | 4 | 0.666667 | 6 | -0.21 |
| veto reason: context VETO in ['league'] | 6 | 4 | 0.666667 | 6 | -0.065 |
| veto reason: context VETO in ['niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: context VETO in ['odds_band'] | 45 | 38 | 0.844444 | 45 | 0.142667 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.183667 |
| veto reason: context VETO in ['team_a'] | 26 | 19 | 0.730769 | 26 | 0.100769 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 3 | -0.07 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 6 | 0.857143 | 7 | 0.2 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 4 | 2 | 0.5 | 4 | -0.26 |
| veto reason: context VETO in ['team_h', 'team_a'] | 11 | 5 | 0.454545 | 11 | -0.406364 |
| veto reason: context VETO in ['team_h'] | 39 | 27 | 0.692308 | 39 | -0.021923 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.18 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: BETEXPLORER_RESCUE | 37 | 24 | 0.648649 | 37 | 0.041351 |
| contrast CAUTION: BZZOIRO_PRIMARY | 21 | 14 | 0.666667 | 21 | 0.045714 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 7 | 1 | 0.142857 | 7 | -0.757143 |
| contrast CAUTION: SOURCE_FALLBACK | 4 | 3 | 0.75 | 4 | 0.115 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 241 | 177 | 0.73444 | 220 | 0.025127 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 18 | 12 | 0.666667 | 17 | -0.112353 | 10 | 1.3545 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 84 | 53 | 0.630952 | 84 | -0.102262 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-22: West Ham vs Charlton (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🔴 LOST (Expected prob: 55.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.2% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.8% (Actual: 2 away goals)

### 2026-08-22: SV Wehen vs Bayer Leverkusen (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.15 -> 🟢 WON (Expected prob: 77.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 85.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 14.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 92.9% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 49.8% (Actual: 4 goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 92.2% (Actual: 4 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 91.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.6% (Actual: 4 goals)

### 2026-08-22: Eintracht Trier vs RB Leipzig (Actual Score: **0-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.04 -> 🟢 WON (Expected prob: 74.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.4% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 21.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 92.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.8% (Actual: 6 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 28.8% (Actual: 6 goals)

### 2026-08-22: Canberra White Eagles vs Monaro Panthers (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.18 -> 🟢 WON (Expected prob: 77.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 81.5% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 95.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 92.6% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.8% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 90.1% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 87.1% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 31.2% (Actual: 5 goals)

### 2026-08-22: Levski Sofia vs Spartak Varna (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ 1.27 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.2% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.3% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.5% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.0% (Actual: 6 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.9% (Actual: 6 goals)

### 2026-08-22: Dandenong Thunder vs Oakleigh Cannons (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.13 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 70.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 35.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.0% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.9% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.4% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.0% (Actual: 0 home goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 24.0% (Actual: 5 goals)

### 2026-08-22: Fenerbahçe vs Konyaspor (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 69.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.9% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.6% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.0% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.5% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.8% (Actual: 2 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.6% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 25.9% (Actual: 6 goals)

### 2026-08-22: Ludogorets vs Slavia Sofia (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 68.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.5% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 86.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 52.0% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 96.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.2% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 24.4% (Actual: 2 goals)

### 2026-08-22: Inter vs Monza (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 67.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 86.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.5% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.6% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.7% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.2% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 23.5% (Actual: 5 goals)

### 2026-08-22: Lens vs Auxerre (Actual Score: **5-2**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 63.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.3% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.0% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.5% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.7% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.1% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 20.0% (Actual: 7 goals)

### 2026-08-22: Heerenveen vs PEC Zwolle (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🔴 LOST (Expected prob: 59.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 82.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.1% (Actual: 2 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 84.6% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.5% (Actual: 2 away goals)

### 2026-08-22: Beijing Guoan vs Yunnan Yukun (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🔴 LOST (Expected prob: 58.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.9% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 48.1% (Actual: 6 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 84.8% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 3 away goals)

### 2026-08-22: Espanyol vs Real Madrid (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.44 -> 🟢 WON (Expected prob: 57.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.1% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.5% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.5% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.2% (Actual: 3 goals)

### 2026-08-22: Kashima Antlers vs Avispa Fukuoka (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🟢 WON (Expected prob: 57.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.2% (Actual: 5 goals)

### 2026-08-22: Birmingham City vs Bristol City (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🔴 LOST (Expected prob: 56.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 81.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 46.3% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 2 away goals)

### 2026-08-22: Hull City vs Manchester United (Actual Score: **2-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.36 -> 🔴 LOST (Expected prob: 56.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 88.7% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 51.8% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.3% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.3% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.4% (Actual: 2 goals)

### 2026-08-22: Piast Gliwice vs Legia Warszawa (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.0 -> 🔴 LOST (Expected prob: 55.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 88.6% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 49.4% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.4% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.0% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.2% (Actual: 2 goals)

### 2026-08-22: East Fife vs Hamilton Academical (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.83 -> 🔴 LOST (Expected prob: 55.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.0% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.0% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 83.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 51.6% (Actual: 0 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 94.5% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 90.4% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.3% (Actual: 0 goals)

### 2026-08-22: Worthing FC vs Wealdstone (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 2.05 -> 🟢 WON (Expected prob: 55.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.7% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 46.0% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.8% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.2% (Actual: 0 away goals)

### 2026-08-22: Erzgebirge Aue vs Hoffenheim (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.13 -> 🟢 WON (Expected prob: 70.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 31.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 93.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.7% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.0% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.6% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 91.1% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 25.3% (Actual: 4 goals)

### 2026-08-22: Borussia Dortmund vs Bayern Munich (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.61 -> 🟢 WON (Expected prob: 64.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 52.4% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.2% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 23.4% (Actual: 3 goals)

### 2026-08-22: SG Sonnenhof vs Arminia Bielefeld (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🔴 LOST (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 43.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 89.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 51.6% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 93.2% (Actual: 2 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 89.3% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 20.8% (Actual: 4 goals)

### 2026-08-22: Znicz Pruszkow vs Swit Skolwin (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🔴 LOST (Expected prob: 57.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.5% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 44.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.1% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.1% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 1 away goals)

### 2026-08-22: Cheonan City vs Suwon Bluewings (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.5 -> 🟢 WON (Expected prob: 55.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.2% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.0% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 48.6% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected 95.6% (Actual: 0 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 92.3% (Actual: 0 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.1% (Actual: 1 goals)

### 2026-08-22: Stabæk W vs Bodø / Glimt W (Actual Score: **7-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 78.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.3% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 92.9% (Actual: 7 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 58.7% (Actual: 8 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 82.7% (Actual: 7 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 97.2% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 81.5% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.9% (Actual: 8 goals)

### 2026-08-22: Ural vs Tekstilshtik Ivanovo (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 59.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.3% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 47.8% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 83.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 18.2% (Actual: 2 goals)

### 2026-08-22: Suwon City FC vs Gimhae City (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 55.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 80.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 45.5% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.1% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.9% (Actual: 0 away goals)

### 2026-08-22: Al Ain vs Khor Fakkan Club (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 75.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 57.9% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.3% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 98.8% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 92.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.8% (Actual: 2 goals)

### 2026-08-22: Al Ahli vs Abha Club (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🟢 WON (Expected prob: 71.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 57.2% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 89.7% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.7% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.0% (Actual: 4 goals)

### 2026-08-22: Fluminense vs Remo (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 62.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 47.2% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.5% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 95.3% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 19.0% (Actual: 3 goals)

### 2026-08-22: Albacete vs Real Sociedad B (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.83 -> 🔴 LOST (Expected prob: 55.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 45.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 81.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 45.7% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 81.2% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 93.0% (Actual: 2 away goals)

### 2026-08-22: Al-Ahli Jeddah vs Abha (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 79.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.4% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 37.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 93.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 53.0% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 86.9% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 91.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 26.0% (Actual: 4 goals)

### 2026-08-22: Canberra FC vs Belconnen United (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.23 -> 🟢 WON (Expected prob: 76.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 44.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.3% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 68.2% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 90.5% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 95.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 90.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 33.1% (Actual: 4 goals)

### 2026-08-22: AEK Athens vs Iraklis 1908 FC (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.21 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 77.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 55.0% (Actual: 4 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 85.7% (Actual: 4 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected 99.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 94.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.1% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 29.1% (Actual: 4 goals)

### 2026-08-22: Canberra Olympic vs Brindabella Blues (Actual Score: **5-4**)
- **1X2 Pick**: Selected `HOME` @ 1.23 -> 🟢 WON (Expected prob: 73.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.7% (Actual: 9 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.4% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 61.2% (Actual: 9 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 88.4% (Actual: 5 home goals)
    - [🔴 MISS] **Away Team Under 3.5 Goals**: expected 98.5% (Actual: 4 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 93.9% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 29.5% (Actual: 9 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 2 |
- 2026-07-25 `POSTPONED` `WATCHLIST_NO_ODDS` — Coquimbo Unido vs Universidad de Concepcion (verified_disposition); excluded from win/loss/ROI
- 2026-07-26 `POSTPONED` `SKIPPED_VETO` — Super Nova vs Riga (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- 2026-08-08 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Belshina vs Dinamo Minsk -> AWAY @ 1.32 (pending_or_unmatched_result); keys=['belshina', 'belshinab']/['dinamomin']
- 2026-08-11 `WATCHLIST_UNCORROBORATED_PRICE` `2way+bc-confirms avg_p>=60` — Junior vs Pereira -> HOME @ 1.33 (pending_or_unmatched_result); keys=['junior']/['pereira']
- 2026-08-15 `SKIPPED_VETO` `2way-unanimous min_p>=60 avg_p>=65` — Slavia Sofia vs Levski Sofia -> AWAY @ 1.36 (pending_or_unmatched_result); keys=['slaviasof']/['levskisof']
- 2026-08-15 `WATCHLIST_NO_ODDS` `2way-unanimous min_p>=60 avg_p>=65` — Kara-Balta vs Bars -> AWAY @ None (pending_or_unmatched_result); keys=['karabalta']/['bars']
- 2026-08-15 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous min_p>=60 avg_p>=65` — Olympic Kingsway vs Sorrento FC -> HOME @ 1.24 (pending_or_unmatched_result); keys=['olympicki']/['sorrento']
- 2026-08-16 `SKIPPED_VETO` `ml-meta avg_p>=55` — SC Braga vs Gil Vicente -> HOME @ 1.7 (pending_or_unmatched_result); keys=['braga']/['gilvicent']
- 2026-08-17 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Hamrun Spartans vs Mosta -> HOME @ 1.18 (pending_or_unmatched_result); keys=['hamrunspa']/['mosta']
- 2026-08-17 `SKIPPED_VETO` `ml-meta avg_p>=55` — Bucaramanga vs Deportivo Pasto -> HOME @ 1.61 (pending_or_unmatched_result); keys=['bucaraman']/['pasto']
- 2026-08-21 `SKIPPED_VETO` `ml-meta avg_p>=55` — Shamrock Rovers vs Shelbourne FC -> HOME @ 1.8 (pending_or_unmatched_result); keys=['shamrockr']/['shelbourn']
- 2026-08-22 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Rangers vs St Mirren -> HOME @ 1.3 (pending_or_unmatched_result); keys=['rangers']/['stmirren']
- 2026-08-22 `SKIPPED_VETO` `ml-meta avg_p>=55` — St Johnstone vs Celtic -> AWAY @ 1.42 (pending_or_unmatched_result); keys=['stjohnsto']/['celtic']
- 2026-08-22 `SKIPPED_VETO` `ml-meta avg_p>=55` — Hibernian vs Kilmarnock -> HOME @ 1.66 (pending_or_unmatched_result); keys=['hibernian']/['kilmarnoc']
- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Rhode Island vs Monterey Bay -> HOME @ 1.44 (pending_or_unmatched_result); keys=['rhodeisla']/['montereyb']
- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Inter Miami CF vs Toronto FC -> HOME @ 1.36 (pending_or_unmatched_result); keys=['intermiam']/['toronto']
- 2026-08-22 `WATCHLIST_UNCORROBORATED_PRICE` `ml-meta avg_p>=55` — Charleston Battery vs Miami FC II -> HOME @ 1.42 (pending_or_unmatched_result); keys=['charlesto']/['miami', 'miamiii']

## Ambiguous result examples

- none

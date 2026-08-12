# Edge Factory — Recent picks audit (2026-07-14 to 2026-08-12)

## Overall

- archived pick rows: 212
- archived pick dates: 30
- immutable morning-baseline rows: 129
- verified official late-slate additions: 30
- regular-ledger-only legacy rows: 53
- unsafe regular ledgers ignored: 3
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 199
- eligible prior 1x2 picks: 205
- pending/unmatched result picks: 3
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 4
- ambiguous result picks: 0
- wins: 148
- hit rate: +74.4%
- priced picks: 189
- ROI: -0.6%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-12
- same-day rows excluded: 7

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 134 / 199 matches (67.3%)
- **Both Teams to Score (BTTS)**: occurred in 100 / 199 matches (50.3%)
- **Selected Team Over 1.5 Goals**: occurred in 144 / 199 matches (72.4%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 131
- **Total Hits**: 101
- **Overall Hit Rate**: 77.1%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=14, hits=13, hit_rate=92.9%
- `away_under_35`: recommended=6, hits=6, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=61, hits=57, hit_rate=93.4%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1062** | scored: 1062

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 102 | 102 | 99 | +97.1% | +97.1% | -0.1% | 0.027827 |
| `match_over_35` | 98 | 98 | 38 | +38.8% | +43.0% | -4.2% | 0.244783 |
| `match_over_45` | 97 | 97 | 20 | +20.6% | +26.0% | -5.4% | 0.17301 |
| `away_under_25` | 90 | 90 | 84 | +93.3% | +92.6% | +0.8% | 0.06423 |
| `home_over_05` | 86 | 86 | 82 | +95.3% | +88.8% | +6.5% | 0.0524 |
| `exact_4` | 67 | 67 | 17 | +25.4% | +18.0% | +7.3% | 0.196872 |
| `match_over_25` | 66 | 66 | 42 | +63.6% | +41.6% | +22.0% | 0.303913 |
| `goal_range_4_6` | 63 | 63 | 26 | +41.3% | +37.4% | +3.8% | 0.250203 |
| `goal_range_4_5` | 59 | 59 | 20 | +33.9% | +30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | +10.5% | +12.6% | -2.1% | 0.096166 |
| `btts_no` | 40 | 40 | 17 | +42.5% | +52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | +50.0% | +50.9% | -0.9% | 0.248905 |
| `exact_3` | 32 | 32 | 4 | +12.5% | +22.2% | -9.7% | 0.119085 |
| `home_under_35` | 29 | 29 | 25 | +86.2% | +95.4% | -9.2% | 0.12251 |
| `goal_range_2_3` | 26 | 26 | 8 | +30.8% | +46.1% | -15.4% | 0.233772 |
| `away_under_15` | 24 | 24 | 20 | +83.3% | +80.9% | +2.4% | 0.139569 |
| `exact_2` | 24 | 24 | 5 | +20.8% | +24.5% | -3.7% | 0.166543 |
| `away_over_05` | 17 | 17 | 15 | +88.2% | +87.2% | +1.0% | 0.103186 |
| `home_under_25` | 16 | 16 | 14 | +87.5% | +92.1% | -4.6% | 0.11284 |
| `goal_range_6_plus` | 9 | 9 | 1 | +11.1% | +18.7% | -7.6% | 0.102748 |
| `match_over_15` | 8 | 8 | 7 | +87.5% | +85.7% | +1.8% | 0.122786 |
| `home_under_15` | 5 | 5 | 4 | +80.0% | +81.0% | -1.0% | 0.159213 |
| `exact_1` | 4 | 4 | 1 | +25.0% | +21.5% | +3.5% | 0.175017 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | +33.3% | +13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | +0.0% | +11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | +100.0% | +35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 757 | 412 | +54.4% | +54.7% | -0.3% | 0.14592 |
| legacy | 263 | 136 | +51.7% | +52.1% | -0.4% | 0.183796 |
| model | 42 | 28 | +66.7% | +47.2% | +19.4% | 0.278725 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 137 | +15.5% | +19.7% | +4.2% |
| 0.2-0.3 | 164 | +24.8% | +21.3% | -3.4% |
| 0.3-0.4 | 194 | +35.5% | +44.3% | +8.9% |
| 0.4-0.5 | 103 | +45.3% | +38.8% | -6.5% |
| 0.5-0.6 | 78 | +52.6% | +39.7% | -12.8% |
| 0.6-0.7 | 5 | +65.3% | +100.0% | +34.7% |
| 0.7-0.8 | 4 | +74.4% | +50.0% | -24.4% |
| 0.8-0.9 | 110 | +84.8% | +90.9% | +6.1% |
| 0.9-1.0 | 267 | +94.8% | +93.6% | -1.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=130, MAE=1.408923 goals, bias=-0.510462 (realized − promised), promised avg 3.756615 vs realized 3.246154

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 260 | +14.4% | +10.4% | -4.0% | 0.095321 |
| Away Over 1.5 | 130 | +22.8% | +33.1% | +10.2% | 0.20703 |
| BTTS-Yes | 130 | +40.7% | +51.5% | +10.9% | 0.263952 |
| Home Over 1.5 | 130 | +73.9% | +60.0% | -13.9% | 0.216011 |
| Over 2.5 | 130 | +73.0% | +64.6% | -8.3% | 0.234161 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 100 | +8.8% | +21.0% | +12.2% |
| 0.1-0.2 | 286 | +13.9% | +11.9% | -2.0% |
| 0.2-0.3 | 4 | +20.8% | +25.0% | +4.2% |
| 0.3-0.4 | 47 | +37.9% | +59.6% | +21.7% |
| 0.4-0.5 | 83 | +42.2% | +47.0% | +4.8% |
| 0.6-0.7 | 44 | +67.7% | +59.1% | -8.6% |
| 0.7-0.8 | 78 | +74.8% | +66.7% | -8.1% |
| 0.8-0.9 | 107 | +86.1% | +69.2% | -17.0% |
| 0.9-1.0 | 31 | +91.8% | +77.4% | -14.4% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=32, wins=18, hit_rate=0.5625, ROI=-0.230667
- `2way-unanimous avg_p>=70`: settled=92, wins=73, hit_rate=0.793478, ROI=0.047565
- `3way-unanimous avg_p>=65`: settled=59, wins=42, hit_rate=0.711864, ROI=-0.033534
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=5, wins=5, hit_rate=1.0, ROI=0.126
- `ml-meta avg_p>=55`: settled=1, wins=1, hit_rate=1.0, ROI=0.38

## By bucket

- `CAUTION`: settled=41, wins=23, hit_rate=0.560976, ROI=-0.125854
- `CERTIFIED_CLEAN`: settled=10, wins=4, hit_rate=0.4, ROI=-0.436
- `SKIPPED_VETO`: settled=108, wins=86, hit_rate=0.796296, ROI=0.058222
- `WATCHLIST_NO_ODDS`: settled=10, wins=9, hit_rate=0.9, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=2, wins=1, hit_rate=0.5, ROI=-0.4
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=7, wins=6, hit_rate=0.857143, ROI=0.148571
- `WATCHLIST_UNKNOWN_CTX`: settled=21, wins=19, hit_rate=0.904762, ROI=0.092857

## By odds source

- `UNKNOWN`: settled=10, wins=9, hit_rate=0.9, ROI=None
- `betexplorer_odds`: settled=89, wins=71, hit_rate=0.797753, ROI=0.05191
- `bzzoiro_odds`: settled=55, wins=38, hit_rate=0.690909, ROI=-0.014582
- `forebet_best`: settled=6, wins=3, hit_rate=0.5, ROI=-0.313333
- `scoutingstats_odds`: settled=30, wins=18, hit_rate=0.6, ROI=-0.209
- `zulubet`: settled=9, wins=9, hit_rate=1.0, ROI=0.365556

## By odds match method

- `alias_fuzzy`: settled=11, wins=7, hit_rate=0.636364, ROI=-0.204545
- `betexplorer`: settled=89, wins=71, hit_rate=0.797753, ROI=0.05191
- `exact`: settled=77, wins=51, hit_rate=0.662338, ROI=-0.067948
- `fallback`: settled=12, wins=10, hit_rate=0.833333, ROI=0.151667
- `none`: settled=10, wins=9, hit_rate=0.9, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 89 | 71 | 0.797753 | 89 | 0.05191 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 47 | 33 | 0.702128 | 47 | 0.022085 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 30 | 18 | 0.6 | 30 | -0.209 |
| Source fallback (`SOURCE_FALLBACK`) | 12 | 10 | 0.833333 | 12 | 0.151667 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 11 | 7 | 0.636364 | 11 | -0.204545 |
| No usable price (`UNMATCHED`) | 10 | 9 | 0.9 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 108 | 86 | 0.796296 | 108 | 0.058222 |
| **trusted evidence only** | 85 | 68 | 0.8 | 85 | 0.062918 |
| **soft evidence only** | 23 | 18 | 0.782609 | 23 | 0.04087 |
| evidence: BETEXPLORER_RESCUE | 57 | 47 | 0.824561 | 57 | 0.07193 |
| evidence: BZZOIRO_PRIMARY | 28 | 21 | 0.75 | 28 | 0.044571 |
| evidence: SCOUTINGSTATS_SOLE | 12 | 8 | 0.666667 | 12 | -0.139167 |
| evidence: SOURCE_FALLBACK | 6 | 6 | 1.0 | 6 | 0.418333 |
| evidence: SUSPECT_ALIAS_FUZZY | 5 | 4 | 0.8 | 5 | 0.02 |
| odds band: <1.50 | 89 | 73 | 0.820225 | 89 | 0.042787 |
| odds band: 1.50-2.00 | 18 | 12 | 0.666667 | 18 | 0.072222 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.146667 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 7 | 5 | 0.714286 | 7 | -0.082857 |
| veto reason: context VETO in ['odds_band'] | 40 | 30 | 0.75 | 40 | 0.01475 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 5 | 5 | 1.0 | 5 | 0.3666 |
| veto reason: context VETO in ['team_a'] | 14 | 11 | 0.785714 | 14 | 0.123571 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 4 | 3 | 0.75 | 4 | 0.12 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 3 | 2 | 0.666667 | 3 | -0.013333 |
| veto reason: context VETO in ['team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.46 |
| veto reason: context VETO in ['team_h'] | 13 | 11 | 0.846154 | 13 | 0.085769 |
| veto reason: short-odds away favourite 1.05 | 1 | 1 | 1.0 | 1 | 0.05 |
| veto reason: short-odds away favourite 1.07 | 1 | 1 | 1.0 | 1 | 0.07 |
| veto reason: short-odds away favourite 1.11 | 1 | 1 | 1.0 | 1 | 0.11 |
| veto reason: short-odds away favourite 1.12 | 1 | 1 | 1.0 | 1 | 0.12 |
| veto reason: short-odds away favourite 1.13 | 1 | 1 | 1.0 | 1 | 0.13 |
| veto reason: short-odds away favourite 1.15 | 1 | 1 | 1.0 | 1 | 0.15 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.19 | 2 | 2 | 1.0 | 2 | 0.19 |
| veto reason: short-odds away favourite 1.22 | 1 | 1 | 1.0 | 1 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: short-odds away favourite 1.25 | 1 | 1 | 1.0 | 1 | 0.25 |
| contrast CAUTION: BETEXPLORER_RESCUE | 17 | 11 | 0.647059 | 17 | -0.038235 |
| contrast CAUTION: BZZOIRO_PRIMARY | 11 | 9 | 0.818182 | 11 | 0.348182 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 8 | 1 | 0.125 | 8 | -0.7875 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 158 | 123 | 0.778481 | 148 | 0.050527 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 11 | 7 | 0.636364 | 11 | -0.204545 | 3 | 1.316667 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 30 | 18 | 0.6 | 30 | -0.209 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-11: FK Crvena Zvezda vs Hapoel Beer Sheva (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 71.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.4%), [🔴 MISS] 3-0 (13.2%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected +88.3% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.6% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.2% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +37.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +27.8% (Actual: 2 goals)

### 2026-08-11: Institute FC vs Ballinamallard Utd (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🔴 LOST (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 66.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 83.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.5%), [🔴 MISS] 1-0 (16.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +83.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.5% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.0% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +20.0% (Actual: 3 goals)

### 2026-08-11: Slovan Bratislava vs Mjallby AIF (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.85 -> 🟢 WON (Expected prob: 60.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 83.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (17.5%), [🔴 MISS] 1-0 (16.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +83.3% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.5% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.0% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +20.0% (Actual: 2 goals)

### 2026-08-11: Lyon vs Sparta Praha (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.38 -> 🟢 WON (Expected prob: 66.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.3%), [🔴 MISS] 1-0 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.4% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.4% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +95.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected +80.6% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.0% (Actual: 3 goals)

### 2026-08-11: Celje vs Ararat-Armenia (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 71.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (13.5%), [🔴 MISS] 3-0 (13.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.6% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.0% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.5% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected +36.7% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +27.4% (Actual: 2 goals)

### 2026-08-11: Kauno Žalgiris vs Dinamo Zagreb (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.39 -> 🟢 WON (Expected prob: 66.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 69.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 85.4% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (16.2%), [🔴 MISS] 0-1 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected +82.9% (Actual: 2 away goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +98.3% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +94.7% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected +80.4% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.3% (Actual: 3 goals)

### 2026-08-11: Rops vs KuPS Akatemia (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (14.2%), [🔴 MISS] 3-0 (13.1%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +86.7% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.4% (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.3% (Actual: 1 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +37.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +27.7% (Actual: 3 goals)

### 2026-08-11: East Kilbride vs Kilmarnock II (Actual Score: **5-3**)
- **1X2 Pick**: Selected `HOME` @ 1.21 -> 🟢 WON (Expected prob: 80.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.2% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 38.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 91.7% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 92.2% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (19.4%), [🔴 MISS] 3-1 (14.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +88.1% (Actual: 5 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +99.0% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected +94.1% (Actual: 3 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +36.6% (Actual: 8 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected +27.8% (Actual: 8 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 3 |
- 2026-07-19 `POSTPONED` `WATCHLIST_NO_ODDS` — FC Levadia Tallinn vs Tammeka (verified_disposition); excluded from win/loss/ROI
- 2026-07-25 `POSTPONED` `WATCHLIST_NO_ODDS` — Coquimbo Unido vs Universidad de Concepcion (verified_disposition); excluded from win/loss/ROI
- 2026-07-26 `POSTPONED` `SKIPPED_VETO` — Super Nova vs Riga (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- 2026-08-08 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Belshina vs Dinamo Minsk -> AWAY @ 1.32 (pending_or_unmatched_result); keys=['belshina', 'belshinab']/['dinamomin']
- 2026-08-11 `CAUTION` `2way+bc-confirms avg_p>=60` — Clachnacuddin vs Dundee Utd Youth -> HOME @ 1.3 (pending_or_unmatched_result); keys=['clachnacu']/['dundeeutd']
- 2026-08-11 `WATCHLIST_UNCORROBORATED_PRICE` `2way+bc-confirms avg_p>=60` — Junior vs Pereira -> HOME @ 1.33 (pending_or_unmatched_result); keys=['junior']/['pereira']

## Ambiguous result examples

- none

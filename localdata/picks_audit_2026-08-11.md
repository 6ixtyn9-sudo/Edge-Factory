# Edge Factory — Recent picks audit (2026-07-13 to 2026-08-11)

## Overall

- archived pick rows: 199
- archived pick dates: 30
- immutable morning-baseline rows: 120
- verified official late-slate additions: 30
- regular-ledger-only legacy rows: 49
- unsafe regular ledgers ignored: 3
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 191
- eligible prior 1x2 picks: 196
- pending/unmatched result picks: 2
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 4
- ambiguous result picks: 0
- wins: 141
- hit rate: +73.8%
- priced picks: 182
- ROI: -1.3%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-11
- same-day rows excluded: 3

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 128 / 191 matches (67.0%)
- **Both Teams to Score (BTTS)**: occurred in 96 / 191 matches (50.3%)
- **Selected Team Over 1.5 Goals**: occurred in 137 / 191 matches (71.7%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 122
- **Total Hits**: 93
- **Overall Hit Rate**: 76.2%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=13, hits=12, hit_rate=92.3%
- `away_under_35`: recommended=6, hits=6, hit_rate=100.0%
- `away_under_45`: recommended=3, hits=3, hit_rate=100.0%
- `btts_yes`: recommended=13, hits=7, hit_rate=53.8%
- `goal_range_2_3`: recommended=9, hits=2, hit_rate=22.2%
- `goal_range_4_6`: recommended=1, hits=0, hit_rate=0.0%
- `home_over_05`: recommended=53, hits=50, hit_rate=94.3%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=7, hits=6, hit_rate=85.7%
- `match_over_25`: recommended=9, hits=5, hit_rate=55.6%
- `match_over_35`: recommended=7, hits=1, hit_rate=14.3%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1020** | scored: 1020

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_35` | 98 | 98 | 38 | +38.8% | +43.0% | -4.2% | 0.244783 |
| `away_under_35` | 94 | 94 | 91 | +96.8% | +97.1% | -0.3% | 0.0301 |
| `match_over_45` | 88 | 88 | 18 | +20.5% | +26.2% | -5.7% | 0.17307 |
| `away_under_25` | 83 | 83 | 78 | +94.0% | +92.5% | +1.5% | 0.058716 |
| `home_over_05` | 78 | 78 | 75 | +96.2% | +89.2% | +7.0% | 0.045699 |
| `exact_4` | 67 | 67 | 17 | +25.4% | +18.0% | +7.3% | 0.196872 |
| `goal_range_4_6` | 63 | 63 | 26 | +41.3% | +37.4% | +3.8% | 0.250203 |
| `match_over_25` | 61 | 61 | 39 | +63.9% | +42.0% | +22.0% | 0.304886 |
| `goal_range_4_5` | 59 | 59 | 20 | +33.9% | +30.9% | +3.0% | 0.229007 |
| `exact_5` | 57 | 57 | 6 | +10.5% | +12.6% | -2.1% | 0.096166 |
| `btts_no` | 40 | 40 | 17 | +42.5% | +52.7% | -10.2% | 0.252916 |
| `btts_yes` | 38 | 38 | 19 | +50.0% | +50.9% | -0.9% | 0.248905 |
| `exact_3` | 32 | 32 | 4 | +12.5% | +22.2% | -9.7% | 0.119085 |
| `home_under_35` | 28 | 28 | 24 | +85.7% | +95.3% | -9.6% | 0.126875 |
| `goal_range_2_3` | 26 | 26 | 8 | +30.8% | +46.1% | -15.4% | 0.233772 |
| `exact_2` | 24 | 24 | 5 | +20.8% | +24.5% | -3.7% | 0.166543 |
| `away_under_15` | 23 | 23 | 19 | +82.6% | +81.0% | +1.6% | 0.143995 |
| `away_over_05` | 16 | 16 | 14 | +87.5% | +87.5% | +0.0% | 0.107813 |
| `home_under_25` | 15 | 15 | 13 | +86.7% | +92.0% | -5.3% | 0.120176 |
| `goal_range_6_plus` | 9 | 9 | 1 | +11.1% | +18.7% | -7.6% | 0.102748 |
| `match_over_15` | 8 | 8 | 7 | +87.5% | +85.7% | +1.8% | 0.122786 |
| `exact_1` | 4 | 4 | 1 | +25.0% | +21.5% | +3.5% | 0.175017 ⚠️low-n |
| `home_under_15` | 4 | 4 | 3 | +75.0% | +81.2% | -6.2% | 0.189446 ⚠️low-n |
| `goal_range_7_plus` | 3 | 3 | 1 | +33.3% | +13.5% | +19.8% | 0.282655 ⚠️low-n |
| `exact_0` | 1 | 1 | 0 | +0.0% | +11.0% | -11.0% | 0.012054 ⚠️low-n |
| `goal_range_0_1` | 1 | 1 | 1 | +100.0% | +35.2% | +64.8% | 0.419464 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 719 | 385 | +53.5% | +53.8% | -0.3% | 0.148175 |
| legacy | 263 | 136 | +51.7% | +52.1% | -0.4% | 0.183796 |
| model | 38 | 24 | +63.2% | +46.1% | +17.0% | 0.280314 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 137 | +15.5% | +19.7% | +4.2% |
| 0.2-0.3 | 155 | +24.8% | +21.3% | -3.5% |
| 0.3-0.4 | 189 | +35.4% | +43.9% | +8.5% |
| 0.4-0.5 | 103 | +45.3% | +38.8% | -6.5% |
| 0.5-0.6 | 78 | +52.6% | +39.7% | -12.8% |
| 0.6-0.7 | 5 | +65.3% | +100.0% | +34.7% |
| 0.7-0.8 | 4 | +74.4% | +50.0% | -24.4% |
| 0.8-0.9 | 99 | +84.8% | +90.9% | +6.1% |
| 0.9-1.0 | 250 | +94.7% | +93.6% | -1.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=121, MAE=1.40595 goals, bias=-0.540165 (realized − promised), promised avg 3.755041 vs realized 3.214876

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 242 | +14.3% | +10.3% | -4.0% | 0.094953 |
| Away Over 1.5 | 121 | +23.2% | +32.2% | +9.0% | 0.201332 |
| BTTS-Yes | 121 | +40.6% | +51.2% | +10.6% | 0.263797 |
| Home Over 1.5 | 121 | +73.5% | +59.5% | -14.0% | 0.21918 |
| Over 2.5 | 121 | +73.0% | +64.5% | -8.5% | 0.235039 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 92 | +8.8% | +19.6% | +10.8% |
| 0.1-0.2 | 267 | +13.8% | +12.0% | -1.8% |
| 0.2-0.3 | 4 | +20.8% | +25.0% | +4.2% |
| 0.3-0.4 | 44 | +37.8% | +59.1% | +21.3% |
| 0.4-0.5 | 77 | +42.2% | +46.8% | +4.6% |
| 0.6-0.7 | 40 | +67.7% | +57.5% | -10.2% |
| 0.7-0.8 | 74 | +74.9% | +67.6% | -7.3% |
| 0.8-0.9 | 99 | +86.1% | +68.7% | -17.5% |
| 0.9-1.0 | 29 | +91.6% | +75.9% | -15.8% |

## By rule

- `2way+bc-confirms avg_p>=60`: settled=26, wins=14, hit_rate=0.538462, ROI=-0.27
- `2way-unanimous avg_p>=70`: settled=91, wins=71, hit_rate=0.78022, ROI=0.030624
- `3way-unanimous avg_p>=65`: settled=59, wins=42, hit_rate=0.711864, ROI=-0.033534
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=5, wins=5, hit_rate=1.0, ROI=0.126

## By bucket

- `CAUTION`: settled=38, wins=22, hit_rate=0.578947, ROI=-0.105526
- `CERTIFIED_CLEAN`: settled=8, wins=2, hit_rate=0.25, ROI=-0.60625
- `SKIPPED_VETO`: settled=106, wins=84, hit_rate=0.792453, ROI=0.051491
- `WATCHLIST_NO_ODDS`: settled=9, wins=8, hit_rate=0.888889, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=2, wins=1, hit_rate=0.5, ROI=-0.4
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=7, wins=6, hit_rate=0.857143, ROI=0.148571
- `WATCHLIST_UNKNOWN_CTX`: settled=21, wins=18, hit_rate=0.857143, ROI=0.035238

## By odds source

- `UNKNOWN`: settled=9, wins=8, hit_rate=0.888889, ROI=None
- `betexplorer_odds`: settled=85, wins=67, hit_rate=0.788235, ROI=0.032235
- `bzzoiro_odds`: settled=54, wins=38, hit_rate=0.703704, ROI=0.003667
- `forebet_best`: settled=6, wins=3, hit_rate=0.5, ROI=-0.313333
- `scoutingstats_odds`: settled=30, wins=18, hit_rate=0.6, ROI=-0.209
- `zulubet`: settled=7, wins=7, hit_rate=1.0, ROI=0.398571

## By odds match method

- `alias_fuzzy`: settled=10, wins=6, hit_rate=0.6, ROI=-0.264
- `betexplorer`: settled=85, wins=67, hit_rate=0.788235, ROI=0.032235
- `exact`: settled=76, wins=51, hit_rate=0.671053, ROI=-0.055684
- `fallback`: settled=11, wins=9, hit_rate=0.818182, ROI=0.155455
- `none`: settled=9, wins=8, hit_rate=0.888889, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 85 | 67 | 0.788235 | 85 | 0.032235 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 46 | 33 | 0.717391 | 46 | 0.044304 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 30 | 18 | 0.6 | 30 | -0.209 |
| Source fallback (`SOURCE_FALLBACK`) | 11 | 9 | 0.818182 | 11 | 0.155455 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 10 | 6 | 0.6 | 10 | -0.264 |
| No usable price (`UNMATCHED`) | 9 | 8 | 0.888889 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 106 | 84 | 0.792453 | 106 | 0.051491 |
| **trusted evidence only** | 84 | 67 | 0.797619 | 84 | 0.058429 |
| **soft evidence only** | 22 | 17 | 0.772727 | 22 | 0.025 |
| evidence: BETEXPLORER_RESCUE | 56 | 46 | 0.821429 | 56 | 0.065357 |
| evidence: BZZOIRO_PRIMARY | 28 | 21 | 0.75 | 28 | 0.044571 |
| evidence: SCOUTINGSTATS_SOLE | 12 | 8 | 0.666667 | 12 | -0.139167 |
| evidence: SOURCE_FALLBACK | 6 | 6 | 1.0 | 6 | 0.418333 |
| evidence: SUSPECT_ALIAS_FUZZY | 4 | 3 | 0.75 | 4 | -0.0725 |
| odds band: <1.50 | 87 | 71 | 0.816092 | 87 | 0.03423 |
| odds band: 1.50-2.00 | 18 | 12 | 0.666667 | 18 | 0.072222 |
| odds band: 2.00-3.00 | 1 | 1 | 1.0 | 1 | 1.18 |
| veto reason: context VETO in ['league', 'odds_band'] | 6 | 5 | 0.833333 | 6 | 0.146667 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['league', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.33 |
| veto reason: context VETO in ['league'] | 6 | 4 | 0.666667 | 6 | -0.161667 |
| veto reason: context VETO in ['odds_band'] | 39 | 29 | 0.74359 | 39 | 0.003846 |
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
| contrast CAUTION: BETEXPLORER_RESCUE | 15 | 10 | 0.666667 | 15 | -0.033333 |
| contrast CAUTION: BZZOIRO_PRIMARY | 10 | 9 | 0.9 | 10 | 0.483 |
| contrast CAUTION: SCOUTINGSTATS_SOLE | 8 | 1 | 0.125 | 8 | -0.7875 |
| contrast CAUTION: SOURCE_FALLBACK | 3 | 2 | 0.666667 | 3 | -0.013333 |
| contrast CAUTION: SUSPECT_ALIAS_FUZZY | 2 | 0 | 0.0 | 2 | -1.0 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 151 | 117 | 0.774834 | 142 | 0.04569 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 10 | 6 | 0.6 | 10 | -0.264 | 2 | 1.24 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 30 | 18 | 0.6 | 30 | -0.209 | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-08-10: FC Botoșani vs Corvinul Hunedoara (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 2.25 -> 🔴 LOST (Expected prob: 60.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.8% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.6%), [🔴 MISS] 1-0 (15.6%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +35.9% (Actual: 0 goals)

### 2026-08-10: Vasteras SK FK vs Djurgårdens (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.86 -> 🔴 LOST (Expected prob: 67.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.6% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.3% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (16.5%), [🔴 MISS] 0-1 (14.9%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected +89.4% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +39.2% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected +98.0% (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected +94.5% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +23.1% (Actual: 1 goals)

### 2026-08-10: Sepsi OSK Sfantu Gheorghe vs FCSB (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.98 -> 🔴 LOST (Expected prob: 63.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.4% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.7% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 0-2 (16.3%), [🔴 MISS] 0-1 (15.3%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +37.6% (Actual: 0 goals)

### 2026-08-10: Plymouth Argyle vs Exeter City (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.52 -> 🟢 WON (Expected prob: 60.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 84.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 0 goals)
  - **Top Scores**: [🟢 HIT] 2-0 (17.6%), [🔴 MISS] 1-0 (15.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +84.7% (Actual: 2 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected +35.9% (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.6% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.2% (Actual: 0 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +20.5% (Actual: 2 goals)

### 2026-08-10: Sirius vs IF Brommapojkarna (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🔴 LOST (Expected prob: 80.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 36.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 94.2% (Actual: 2 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.5%), [🔴 MISS] 3-1 (14.6%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.3% (Actual: 2 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +88.6% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +22.2% (Actual: 4 goals)

### 2026-08-10: Mura vs Radomlje (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.9 -> 🔴 LOST (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.1% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.9% (Actual: 3 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (17.0%), [🔴 MISS] 1-0 (14.9%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +84.6% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.7% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected +93.9% (Actual: 3 away goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected +81.2% (Actual: 3 away goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +22.5% (Actual: 4 goals)

### 2026-08-10: Flora II vs Nõmme Kalju II (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.47 -> 🟢 WON (Expected prob: 71.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (13.5%), [🟢 HIT] 3-0 (13.2%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +84.2% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +97.1% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +93.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +36.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +27.4% (Actual: 3 goals)

### 2026-08-10: Alashkert vs BKMA (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 71.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.1% (Actual: 0 goals)
  - **Top Scores**: [🔴 MISS] 2-0 (14.6%), [🟢 HIT] 3-0 (13.0%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected +84.6% (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 3.5 Goals**: expected +98.3% (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected +94.8% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected +35.9% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected +28.1% (Actual: 3 goals)


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 3 |
- 2026-07-19 `POSTPONED` `WATCHLIST_NO_ODDS` — FC Levadia Tallinn vs Tammeka (verified_disposition); excluded from win/loss/ROI
- 2026-07-25 `POSTPONED` `WATCHLIST_NO_ODDS` — Coquimbo Unido vs Universidad de Concepcion (verified_disposition); excluded from win/loss/ROI
- 2026-07-26 `POSTPONED` `SKIPPED_VETO` — Super Nova vs Riga (verified_disposition); excluded from win/loss/ROI

## Pending / Unmatched Result Examples

- 2026-08-08 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Belshina vs Dinamo Minsk -> AWAY @ 1.32 (pending_or_unmatched_result); keys=['belshina', 'belshinab']/['dinamomin']
- 2026-08-10 `CERTIFIED_CLEAN` `2way+bc-confirms avg_p>=60` — Rīgas FS vs Grobiņa -> HOME @ 1.11 (pending_or_unmatched_result); keys=['rgasfs', 'rigasfs']/['grobia', 'grobina']

## Ambiguous result examples

- none

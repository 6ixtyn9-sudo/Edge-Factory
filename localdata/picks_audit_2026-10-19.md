# Edge Factory — Recent picks audit (2026-09-20 to 2026-10-19)

## Overall

- archived pick rows: 702
- archived pick dates: 30
- immutable morning-baseline rows: 529
- late-slate additions (regular-ledger rows not in the morning baseline): 175, of which on days whose regular ledger was rewritten: 170
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 26
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 687
- eligible prior picks: 701
- pending/unmatched result picks: 14
- rescheduled result picks (settled ±3d): 8
- voided postponed/cancelled/abandoned events: 0
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 0
- ambiguous result picks: 0
- wins: 479
- hit rate: +69.7%
- priced picks: 576
- ROI: +2.9%

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-19
- same-day rows excluded: 1

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 411 / 687 matches (59.8%)
- **Both Teams to Score (BTTS)**: occurred in 360 / 687 matches (52.4%)
- **Selected Team Over 1.5 Goals**: occurred in 453 / 687 matches (65.9%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 658
- **Total Hits**: 523
- **Overall Hit Rate**: 79.5%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, settled=18, hit_rate=94.4%, priced_n=1, registry_processed=53, class=priced
- `away_under_15`: recommended=5, settled=5, hit_rate=100.0%, priced_n=5, registry_processed=5, class=priced
- `away_under_25`: recommended=5, settled=5, hit_rate=80.0%, priced_n=3, registry_processed=35, class=priced
- `away_under_35`: recommended=199, settled=199, hit_rate=97.0%, priced_n=1, registry_processed=305, class=priced
- `btts_no`: recommended=7, settled=7, hit_rate=42.9%, priced_n=7, registry_processed=7, class=priced
- `btts_yes`: recommended=5, settled=5, hit_rate=100.0%, priced_n=5, registry_processed=18, class=priced
- `home_over_05`: recommended=23, settled=23, hit_rate=87.0%, priced_n=1, registry_processed=186, class=priced
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced
- `home_under_25`: recommended=12, settled=12, hit_rate=91.7%, priced_n=0, registry_processed=40, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_35`: recommended=55, settled=55, hit_rate=98.2%, priced_n=0, registry_processed=74, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=22, settled=22, hit_rate=86.4%, priced_n=18, registry_processed=69, class=priced
- `match_over_25`: recommended=285, settled=285, hit_rate=61.1%, priced_n=205, registry_processed=688, class=priced
- `match_over_35`: recommended=18, settled=18, hit_rate=77.8%, priced_n=12, registry_processed=43, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0%, priced_n=2, registry_processed=2, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2573** | scored: 2573

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 637 | 637 | 380 | 59.7% | 47.4% | +12.2% | 0.25714 |
| `match_over_45` | 458 | 458 | 104 | 22.7% | 23.8% | -1.1% | 0.175938 |
| `away_under_35` | 391 | 391 | 382 | 97.7% | 95.7% | +2.0% | 0.022893 |
| `away_under_25` | 364 | 364 | 338 | 92.9% | 89.7% | +3.1% | 0.067435 |
| `home_under_35` | 162 | 162 | 157 | 96.9% | 95.0% | +1.9% | 0.031503 |
| `home_under_25` | 131 | 131 | 122 | 93.1% | 88.2% | +4.9% | 0.066772 |
| `match_over_35` | 114 | 114 | 61 | 53.5% | 43.2% | +10.3% | 0.270596 |
| `btts_yes` | 86 | 86 | 51 | 59.3% | 46.9% | +12.4% | 0.244648 |
| `btts_no` | 80 | 80 | 35 | 43.8% | 54.1% | -10.3% | 0.250847 |
| `away_over_05` | 43 | 43 | 38 | 88.4% | 81.0% | +7.4% | 0.107863 |
| `away_under_15` | 39 | 39 | 29 | 74.4% | 82.1% | -7.7% | 0.195647 |
| `home_over_05` | 34 | 34 | 30 | 88.2% | 89.1% | -0.8% | 0.105948 |
| `match_over_15` | 26 | 26 | 21 | 80.8% | 84.8% | -4.0% | 0.157316 |
| `home_under_15` | 5 | 5 | 4 | 80.0% | 81.7% | -1.7% | 0.163042 |
| `double_chance` | 2 | 2 | 1 | 50.0% | 86.6% | -36.6% | 0.3642 ⚠️low-n |
| `home_over_15` | 1 | 1 | 1 | 100.0% | 81.9% | +18.1% | 0.032904 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2477 | 1680 | 67.8% | 63.6% | +4.2% | 0.148805 |
| model | 96 | 74 | 77.1% | 66.5% | +10.6% | 0.173229 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 93 | 19.1% | 23.7% | +4.5% |
| 0.2-0.3 | 324 | 24.1% | 21.3% | -2.8% |
| 0.3-0.4 | 111 | 35.2% | 47.7% | +12.5% |
| 0.4-0.5 | 606 | 44.8% | 57.8% | +13.0% |
| 0.5-0.6 | 175 | 53.6% | 53.1% | -0.5% |
| 0.6-0.7 | 43 | 63.5% | 65.1% | +1.6% |
| 0.7-0.8 | 23 | 72.7% | 69.6% | -3.1% |
| 0.8-0.9 | 466 | 86.9% | 89.9% | +3.0% |
| 0.9-1.0 | 732 | 94.4% | 96.2% | +1.7% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=685, MAE=1.57492 goals, bias=-0.368905 (realized − promised), promised avg 3.558686 vs realized 3.189781

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 685 | 31.6% | 32.4% | +0.8% | 0.20132 |
| BTTS-Yes | 685 | 41.1% | 52.3% | +11.2% | 0.263212 |
| Home Over 1.5 | 685 | 63.6% | 53.6% | -10.0% | 0.232591 |
| Over 2.5 | 685 | 69.8% | 59.7% | -10.1% | 0.249256 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 292 | 8.6% | 22.6% | +14.0% |
| 0.1-0.2 | 393 | 10.5% | 18.6% | +8.1% |
| 0.2-0.3 | 8 | 24.6% | 50.0% | +25.4% |
| 0.3-0.4 | 127 | 37.1% | 48.0% | +11.0% |
| 0.4-0.5 | 547 | 42.1% | 53.2% | +11.1% |
| 0.5-0.6 | 2 | 53.3% | 50.0% | -3.3% |
| 0.6-0.7 | 454 | 67.0% | 56.6% | -10.4% |
| 0.7-0.8 | 209 | 74.6% | 65.6% | -9.0% |
| 0.8-0.9 | 641 | 84.7% | 64.9% | -19.8% |
| 0.9-1.0 | 67 | 92.0% | 74.6% | -17.4% |

## By rule

- `2way-unanimous avg_p>=60`: settled=164, wins=106, hit_rate=0.646341, ROI=-0.097951
- `2way-unanimous avg_p>=70`: settled=36, wins=28, hit_rate=0.777778, ROI=0.010741
- `ml-meta avg_p>=55`: settled=228, wins=161, hit_rate=0.70614, ROI=0.113065
- `ml-meta avg_p>=60`: settled=168, wins=107, hit_rate=0.636905, ROI=-0.006564
- `ml-meta avg_p>=65`: settled=23, wins=19, hit_rate=0.826087, ROI=-0.014118
- `ml-meta avg_p>=70`: settled=1, wins=0, hit_rate=0.0, ROI=-1.0
- `ml-meta avg_p>=80`: settled=7, wins=7, hit_rate=1.0, ROI=0.075
- `unanimous[betclan+vitibet] avg_p>=70`: settled=16, wins=15, hit_rate=0.9375, ROI=0.338475
- `unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65`: settled=1, wins=1, hit_rate=1.0, ROI=0.25
- `unanimous[bzzoiro+statarea+vitibet] avg_p>=65`: settled=4, wins=3, hit_rate=0.75, ROI=-0.1135
- `unanimous[bzzoiro+vitibet] avg_p>=70`: settled=13, wins=9, hit_rate=0.692308, ROI=-0.035815
- `unanimous[statarea+vitibet+zulubet] avg_p>=65`: settled=2, wins=1, hit_rate=0.5, ROI=-0.025
- `unanimous[statarea+vitibet] avg_p>=70`: settled=19, wins=17, hit_rate=0.894737, ROI=0.150443
- `unanimous[vitibet+zulubet] avg_p>=70`: settled=5, wins=5, hit_rate=1.0, ROI=0.3925

## By bucket

- `CAUTION`: settled=51, wins=30, hit_rate=0.588235, ROI=-0.063173
- `CERTIFIED_CLEAN`: settled=98, wins=63, hit_rate=0.642857, ROI=0.031326
- `SKIPPED_VETO`: settled=356, wins=263, hit_rate=0.738764, ROI=0.053662
- `WATCHLIST_NO_ODDS`: settled=69, wins=45, hit_rate=0.652174, ROI=None
- `WATCHLIST_SUSPECT_PRICE`: settled=15, wins=9, hit_rate=0.6, ROI=0.033636
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=92, wins=64, hit_rate=0.695652, ROI=-0.005109
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333, ROI=-0.001667

## By odds source

- `UNKNOWN`: settled=111, wins=75, hit_rate=0.675676, ROI=None
- `betexplorer_odds`: settled=192, wins=141, hit_rate=0.734375, ROI=0.003958
- `boggio`: settled=1, wins=1, hit_rate=1.0, ROI=0.52
- `bzzoiro_odds`: settled=6, wins=5, hit_rate=0.833333, ROI=0.191667
- `forebet_best`: settled=46, wins=33, hit_rate=0.717391, ROI=0.050652
- `oddspapi_odds`: settled=5, wins=3, hit_rate=0.6, ROI=-0.059
- `pinnapi_odds`: settled=57, wins=36, hit_rate=0.631579, ROI=0.084328
- `scoutingstats_odds`: settled=160, wins=110, hit_rate=0.6875, ROI=-0.011375
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0, ROI=0.741
- `theoddsapi`: settled=63, wins=48, hit_rate=0.761905, ROI=0.162222
- `zulubet`: settled=45, wins=26, hit_rate=0.577778, ROI=-0.035778

## By odds match method

- `alias_fuzzy`: settled=33, wins=21, hit_rate=0.636364, ROI=-0.034231
- `betexplorer`: settled=105, wins=73, hit_rate=0.695238, ROI=-0.028286
- `exact`: settled=380, wins=272, hit_rate=0.715789, ROI=0.050139
- `fallback`: settled=65, wins=43, hit_rate=0.661538, ROI=0.024769
- `none`: settled=104, wins=70, hit_rate=0.673077, ROI=None

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 1 | 1 | 1.0 | 1 | 0.52 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 105 | 73 | 0.695238 | 105 | -0.028286 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 6 | 5 | 0.833333 | 6 | 0.191667 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 213 | 156 | 0.732394 | 213 | 0.090154 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 160 | 110 | 0.6875 | 160 | -0.011375 |
| Source fallback (`SOURCE_FALLBACK`) | 65 | 43 | 0.661538 | 65 | 0.024769 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 33 | 21 | 0.636364 | 26 | -0.034231 |
| No usable price (`UNMATCHED`) | 104 | 70 | 0.673077 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 356 | 263 | 0.738764 | 318 | 0.053662 |
| **trusted evidence only** | 207 | 160 | 0.772947 | 207 | 0.092872 |
| **soft evidence only** | 149 | 103 | 0.691275 | 111 | -0.019459 |
| evidence: BETEXPLORER_RESCUE | 61 | 44 | 0.721311 | 61 | -0.042951 |
| evidence: BZZOIRO_PRIMARY | 4 | 4 | 1.0 | 4 | 0.375 |
| evidence: NAMED_BOOKMAKER_PRICE | 142 | 112 | 0.788732 | 142 | 0.143272 |
| evidence: SCOUTINGSTATS_SOLE | 68 | 46 | 0.676471 | 68 | -0.019853 |
| evidence: SOURCE_FALLBACK | 28 | 20 | 0.714286 | 28 | 0.016071 |
| evidence: SUSPECT_ALIAS_FUZZY | 18 | 12 | 0.666667 | 15 | -0.084 |
| evidence: UNMATCHED | 35 | 25 | 0.714286 | 0 | None |
| odds band: <1.50 | 201 | 159 | 0.791045 | 201 | -0.001081 |
| odds band: 1.50-2.00 | 98 | 65 | 0.663265 | 98 | 0.099203 |
| odds band: 2.00-3.00 | 15 | 10 | 0.666667 | 15 | 0.504 |
| odds band: >=3.00 | 4 | 1 | 0.25 | 4 | 0.0 |
| odds band: unpriced | 38 | 28 | 0.736842 | 0 | None |
| veto reason: context VETO in ['competition_type'] | 38 | 32 | 0.842105 | 29 | 0.126203 |
| veto reason: context VETO in ['league', 'niche'] | 3 | 2 | 0.666667 | 2 | -0.335 |
| veto reason: context VETO in ['league', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.26 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.3881 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 7 | 5 | 0.714286 | 6 | 0.188333 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 3 | 3 | 1.0 | 3 | 0.26 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 4 | 3 | 0.75 | 4 | 0.0725 |
| veto reason: context VETO in ['league'] | 27 | 15 | 0.555556 | 22 | -0.32 |
| veto reason: context VETO in ['niche'] | 12 | 8 | 0.666667 | 12 | -0.073333 |
| veto reason: context VETO in ['odds_band'] | 58 | 40 | 0.689655 | 58 | -0.058621 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 6 | 5 | 0.833333 | 6 | 0.20035 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 10 | 8 | 0.8 | 10 | 0.091 |
| veto reason: context VETO in ['team_a'] | 66 | 50 | 0.757576 | 57 | 0.146154 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 12 | 10 | 0.833333 | 11 | 0.066918 |
| veto reason: context VETO in ['team_h', 'niche'] | 7 | 6 | 0.857143 | 7 | 0.212857 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 8 | 6 | 0.75 | 8 | -0.04125 |
| veto reason: context VETO in ['team_h', 'team_a', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.44 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 2 | 1 | 0.5 | 2 | -0.375 |
| veto reason: context VETO in ['team_h', 'team_a'] | 19 | 15 | 0.789474 | 18 | 0.326906 |
| veto reason: context VETO in ['team_h'] | 48 | 35 | 0.729167 | 37 | 0.146216 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.08 | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: short-odds away favourite 1.16 | 2 | 2 | 1.0 | 2 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: BETEXPLORER_RESCUE | 21 | 11 | 0.52381 | 21 | -0.177143 |
| contrast CAUTION: BZZOIRO_PRIMARY | 1 | 0 | 0.0 | 1 | -1.0 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 19 | 14 | 0.736842 | 19 | 0.192537 |
| contrast CAUTION: SOURCE_FALLBACK | 10 | 5 | 0.5 | 10 | -0.216 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 474 | 336 | 0.708861 | 371 | 0.050519 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 33 | 21 | 0.636364 | 26 | -0.034231 | 33 | 1.645382 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 160 | 110 | 0.6875 | 160 | -0.011375 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 19 | 11 | 0.578947 | 19 | 0.040526 | 0 | None |
| stale_quote (`stale_quote`) | 1 | 1 | 1.0 | 0 | None | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-18: Igdir FK vs Boluspor (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.19 -> 🟢 WON (Expected prob: 78.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 79.0% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.5% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 91.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 71.8% (Actual: 1 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 55.6% (Actual: BTTS-No)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 54.8% (Actual: 1 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 44.4% (Actual: BTTS-No)

### 2026-10-18: Riga FC vs SK Super Nova (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.7% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 73.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 53.3% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 47.3% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 34.7% (Actual: 3 goals)

### 2026-10-18: Twente vs Utrecht (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.37 -> 🔴 LOST (Expected prob: 74.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.8% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 88.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 91.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 73.8% (Actual: 3 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 53.3% (Actual: 3 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 47.3% (Actual: BTTS-Yes)

### 2026-10-18: Panathinaikos vs Asteras Tripolis (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.23 -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.4% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.9% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 72.4% (Actual: 6 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 54.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 51.6% (Actual: 6 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.7% (Actual: BTTS-Yes)

### 2026-10-18: Kongsvinger vs Sandnes ULF (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2857 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.7% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.6% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 54.9% (Actual: BTTS-No)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 49.3% (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.1% (Actual: BTTS-No)

### 2026-10-18: Molde vs Start (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3195 -> 🟢 WON (Expected prob: 72.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.6% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.4% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 71.2% (Actual: 7 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 54.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 49.1% (Actual: 7 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.1% (Actual: BTTS-Yes)

### 2026-10-18: Seoul E-Land FC vs Gimhae City (Actual Score: **6-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.1% (Actual: 8 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.7% (Actual: 6 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 70.3% (Actual: 8 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 55.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 48.4% (Actual: 8 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 44.7% (Actual: BTTS-Yes)

### 2026-10-18: Red Bull Salzburg vs SCR Altach (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 74.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 88.2% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-18: Hartford Athletic vs Brooklyn (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🔴 LOST (Expected prob: 71.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.2% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 68.3% (Actual: 5 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 54.2% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 46.3% (Actual: 5 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.8% (Actual: BTTS-Yes)

### 2026-10-18: Seattle Sounders vs CF Montreal (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.39 -> 🔴 LOST (Expected prob: 70.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 73.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 82.4% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 68.0% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.8% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.2% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 45.6% (Actual: 2 goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected 28.3% (Actual: 2 goals)

### 2026-10-18: Brighton vs Crystal Palace (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5 -> 🟢 WON (Expected prob: 70.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.3% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 67.1% (Actual: 5 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 54.0% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.0% (Actual: BTTS-No)

### 2026-10-18: Cruz Azul vs FC Juarez (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.34 -> 🟢 WON (Expected prob: 69.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.9% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-No**: expected 39.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.8% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 82.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 67.1% (Actual: 5 goals)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected 54.0% (Actual: BTTS-No)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.0% (Actual: BTTS-No)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 44.8% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 4.5 Goals**: expected 27.3% (Actual: 5 goals)

### 2026-10-18: Toluca vs Atletico San Luis (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🔴 LOST (Expected prob: 67.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.9% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 82.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 62.0% (Actual: 2 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 54.1% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.9% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 40.0% (Actual: 2 goals)

### 2026-10-18: Lech Poznan vs Korona Kielce (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4425 -> 🟢 WON (Expected prob: 60.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.7% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 82.3% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-18: PAOK vs Iraklis 1908 FC (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 74.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-18: HNK Hajduk Split vs NK Varazdin (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 67.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 70.3% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 40.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 86.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-18: Halmstad vs Hammarby (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.25 -> 🟢 WON (Expected prob: 69.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 69.8% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 34.1% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 91.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 85.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-18: Bari vs Crotone (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🔴 LOST (Expected prob: 63.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 66.3% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 41.1% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 84.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-18: Asane vs Stabaek (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.33 -> 🟢 WON (Expected prob: 60.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 68.1% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 89.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 84.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-18: Tampines Rovers FC vs Young Lions (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 81.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 94.7% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 61.7% (Actual: BTTS-Yes)

### 2026-10-18: BKMA vs Ararat-Armenia (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.23 -> 🟢 WON (Expected prob: 76.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 80.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 33.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.6% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 92.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-18: JS Kabylie vs US Biskra (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 76.7% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.0% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 87.7% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 73.6% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 53.3% (Actual: 5 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 47.3% (Actual: BTTS-Yes)

### 2026-10-18: Real Madrid vs Sevilla (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 80.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 73.6% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 53.3% (Actual: 5 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 52.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 47.3% (Actual: BTTS-Yes)

### 2026-10-18: Terengganu vs Johor Darul Takzim (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 72.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 32.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 94.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-18: Lyon vs Nice (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.95 -> 🟢 WON (Expected prob: 66.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 61.8% (Actual: 3 goals)

### 2026-10-18: Kayserispor vs Batman Petrolspor (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.6803 -> 🔴 LOST (Expected prob: 66.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 61.1% (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 54.2% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.8% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 39.6% (Actual: 4 goals)


## Event Disposition / Void Audit

- none

## Rescheduled Fixture Examples

- 2026-09-20 `CERTIFIED_CLEAN` `ml-meta avg_p>=55` — Juticalpa vs CD Marathon -> AWAY @ 3.65 (rescheduled → 2026-09-21; actual Juticalpa 3-2 CD Marathón [home])
- 2026-09-21 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Inter Miami vs San Diego -> HOME @ 1.4 (rescheduled → 2026-09-20; actual Inter Miami CF 2-2 San Diego [draw])
- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova FC 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca W 4-1 Santos Laguna W [home])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ None (rescheduled → 2026-10-03; actual Tampa Bay Rowdies 1-2 Miami FC [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Brooklyn vs Rhode Island FC -> AWAY @ None (rescheduled → 2026-10-03; actual Brooklyn 1-3 Rhode Island [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kano Pillars FC vs Sporting Lagos -> HOME @ None (rescheduled → 2026-10-03; actual Kano Pillars 1-1 Sporting Lagos [draw])
- 2026-10-18 `SKIPPED_VETO` `unanimous[bzzoiro+vitibet] avg_p>=70` — Hartford Athletic vs Brooklyn -> HOME @ 1.44 (rescheduled → 2026-10-17; actual Hartford Athletic 2-3 Brooklyn [away])

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
- 2026-10-09 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Real Cundinamarca vs Real Santander -> HOME @ None (pending_or_unmatched_result); keys=['cundinama']/['santander']
- 2026-10-11 `SKIPPED_VETO` `ml-meta avg_p>=60` — Atletico Nacional vs Deportivo Pasto -> HOME @ 2.1 (pending_or_unmatched_result); keys=['nacional']/['pasto']
- 2026-10-11 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Ranger's vs Carroi -> HOME @ None (pending_or_unmatched_result); keys=['rangers']/['carroi']
- 2026-10-18 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Wolfurt vs Schwaz -> AWAY @ None (pending_or_unmatched_result); keys=['wolfurt']/['schwaz']
- 2026-10-18 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Rheindorf Altach II vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['imst']

## Ambiguous result examples

- none

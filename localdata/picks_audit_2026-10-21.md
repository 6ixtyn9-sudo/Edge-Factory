# Edge Factory — Recent picks audit (2026-09-22 to 2026-10-21)

## Overall

- archived pick rows: 704
- archived pick dates: 30
- immutable morning-baseline rows: 529
- late-slate additions (regular-ledger rows not in the morning baseline): 177, of which on days whose regular ledger was rewritten: 149
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 26
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 649
- eligible prior picks: 663
- pending/unmatched result picks: 11
- rescheduled result picks (settled ±3d): 6
- voided postponed/cancelled/abandoned events: 3
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 25
- ambiguous result picks: 0
- wins: 453
- hit rate: +69.8% (wins/settled: 453/649)
- priced picks: 534
- ROI: +3.8% (P&L / 534 priced picks)

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-21
- same-day rows excluded: 41

Fixture-level secondary rates below score the fixture behind every settled pick; they are not enhancement-bet returns.
## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 391 / 649 matches (60.2%)
- **Both Teams to Score (BTTS)**: occurred in 341 / 649 matches (52.5%)
- **Selected Team Over 1.5 Goals**: occurred in 429 / 645 matches (66.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 597
- **Total Hits**: 469
- **Overall Hit Rate**: 78.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, settled=18, hit_rate=94.4% (hits=17/recommended=18), priced_n=1, priced_ROI=0.64 (denominator=1), registry_processed=53, class=priced
- `away_under_15`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=5, priced_ROI=2.034 (denominator=5), registry_processed=5, class=priced
- `away_under_25`: recommended=3, settled=3, hit_rate=66.7% (hits=2/recommended=3), priced_n=3, priced_ROI=0.423 (denominator=3), registry_processed=35, class=priced
- `away_under_35`: recommended=175, settled=175, hit_rate=96.6% (hits=169/recommended=175), priced_n=1, priced_ROI=0.435 (denominator=1), registry_processed=305, class=priced
- `btts_no`: recommended=8, settled=8, hit_rate=37.5% (hits=3/recommended=8), priced_n=6, priced_ROI=-0.541667 (denominator=6), registry_processed=8, class=priced
- `btts_yes`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=3, priced_ROI=0.853333 (denominator=3), registry_processed=18, class=priced
- `home_over_05`: recommended=23, settled=23, hit_rate=87.0% (hits=20/recommended=23), priced_n=1, priced_ROI=0.38 (denominator=1), registry_processed=186, class=priced
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=0.381 (denominator=2), registry_processed=2, class=priced
- `home_under_25`: recommended=1, settled=1, hit_rate=0.0% (hits=0/recommended=1), priced_n=1, priced_ROI=-1.0 (denominator=1), registry_processed=41, class=priced
- `home_under_35`: recommended=51, settled=51, hit_rate=98.0% (hits=50/recommended=51), priced_n=0, priced_ROI=None (denominator=0), registry_processed=74, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=24, settled=24, hit_rate=87.5% (hits=21/recommended=24), priced_n=18, priced_ROI=0.08 (denominator=18), registry_processed=71, class=priced
- `match_over_25`: recommended=262, settled=262, hit_rate=60.7% (hits=159/recommended=262), priced_n=179, priced_ROI=-0.042011 (denominator=179), registry_processed=691, class=priced
- `match_over_35`: recommended=18, settled=18, hit_rate=77.8% (hits=14/recommended=18), priced_n=11, priced_ROI=1.036364 (denominator=11), registry_processed=43, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=4.0 (denominator=2), registry_processed=2, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2367** | scored: 2367

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 574 | 574 | 342 | 59.6% | 47.8% | +11.7% | 0.256372 |
| `match_over_45` | 403 | 403 | 89 | 22.1% | 23.9% | -1.8% | 0.173046 |
| `away_under_35` | 350 | 350 | 341 | 97.4% | 95.9% | +1.5% | 0.025132 |
| `away_under_25` | 336 | 336 | 311 | 92.6% | 89.8% | +2.8% | 0.06958 |
| `home_under_35` | 142 | 142 | 137 | 96.5% | 95.6% | +0.9% | 0.034736 |
| `match_over_35` | 120 | 120 | 65 | 54.2% | 43.2% | +10.9% | 0.271709 |
| `home_under_25` | 109 | 109 | 101 | 92.7% | 87.8% | +4.8% | 0.070658 |
| `btts_yes` | 92 | 92 | 55 | 59.8% | 47.1% | +12.7% | 0.248418 |
| `btts_no` | 85 | 85 | 36 | 42.4% | 54.1% | -11.7% | 0.252474 |
| `away_over_05` | 43 | 43 | 38 | 88.4% | 81.0% | +7.4% | 0.107863 |
| `away_under_15` | 39 | 39 | 29 | 74.4% | 82.1% | -7.7% | 0.195647 |
| `home_over_05` | 34 | 34 | 30 | 88.2% | 89.1% | -0.8% | 0.105948 |
| `match_over_15` | 28 | 28 | 23 | 82.1% | 84.7% | -2.5% | 0.148163 |
| `home_under_15` | 4 | 4 | 3 | 75.0% | 81.9% | -6.9% | 0.19469 ⚠️low-n |
| `match_under_25` | 4 | 4 | 0 | 0.0% | 36.1% | -36.1% | 0.132836 ⚠️low-n |
| `match_under_35` | 3 | 3 | 0 | 0.0% | 56.4% | -56.4% | 0.322031 ⚠️low-n |
| `home_over_15` | 1 | 1 | 1 | 100.0% | 81.9% | +18.1% | 0.032904 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2271 | 1527 | 67.2% | 63.6% | +3.6% | 0.151223 |
| model | 96 | 74 | 77.1% | 67.3% | +9.8% | 0.182554 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 75 | 19.1% | 24.0% | +4.9% |
| 0.2-0.3 | 295 | 24.2% | 20.7% | -3.5% |
| 0.3-0.4 | 109 | 35.6% | 47.7% | +12.1% |
| 0.4-0.5 | 555 | 44.8% | 57.5% | +12.6% |
| 0.5-0.6 | 173 | 53.7% | 51.4% | -2.3% |
| 0.6-0.7 | 51 | 63.4% | 62.7% | -0.7% |
| 0.7-0.8 | 23 | 72.7% | 69.6% | -3.1% |
| 0.8-0.9 | 440 | 86.8% | 89.5% | +2.7% |
| 0.9-1.0 | 646 | 94.7% | 96.0% | +1.3% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=624, MAE=1.582949 goals, bias=-0.381987 (realized − promised), promised avg 3.574295 vs realized 3.192308

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 624 | 30.7% | 32.7% | +2.0% | 0.192292 |
| BTTS-Yes | 624 | 40.9% | 51.8% | +10.8% | 0.263657 |
| Home Over 1.5 | 624 | 64.6% | 52.9% | -11.7% | 0.233402 |
| Over 2.5 | 624 | 69.9% | 59.8% | -10.2% | 0.248819 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 269 | 8.6% | 22.3% | +13.7% |
| 0.1-0.2 | 355 | 10.5% | 17.5% | +7.0% |
| 0.2-0.3 | 8 | 24.6% | 50.0% | +25.4% |
| 0.3-0.4 | 119 | 37.1% | 48.7% | +11.6% |
| 0.4-0.5 | 493 | 42.0% | 52.5% | +10.6% |
| 0.5-0.6 | 3 | 54.1% | 33.3% | -20.7% |
| 0.6-0.7 | 407 | 67.0% | 56.0% | -11.0% |
| 0.7-0.8 | 195 | 74.6% | 66.2% | -8.5% |
| 0.8-0.9 | 581 | 84.8% | 65.2% | -19.5% |
| 0.9-1.0 | 66 | 92.0% | 75.8% | -16.3% |

## By rule

Counts are frozen PICK ROWS, not bets: rows filed under SKIPPED_VETO / WATCHLIST_* are included and were never cardable. Cardable-only counts are in `## By bucket`.

- `2way-unanimous avg_p>=60`: hit_rate 0.646341 (106/164 settled) · ROI -0.097951 (122 priced)
- `2way-unanimous avg_p>=70`: PROVISIONAL (settled n=24 < 30) — hit_rate 0.791667 (19/24 settled) · ROI 0.037647 (17 priced)
- `ml-meta avg_p>=55`: hit_rate 0.73545 (139/189 settled) · ROI 0.164667 (162 priced)
- `ml-meta avg_p>=60`: hit_rate 0.611842 (93/152 settled) · ROI -0.037924 (136 priced)
- `ml-meta avg_p>=65`: PROVISIONAL (settled n=22 < 30) — hit_rate 0.818182 (18/22 settled) · ROI -0.031875 (16 priced)
- `ml-meta avg_p>=70`: PROVISIONAL (settled n=1 < 30) — hit_rate 0.0 (0/1 settled) · ROI -1.0 (1 priced)
- `ml-meta avg_p>=80`: PROVISIONAL (settled n=7 < 30) — hit_rate 1.0 (7/7 settled) · ROI 0.075 (6 priced)
- `pfc_0f100c9da356ed1c05d9c642`: 1x2 single[scoutingstats] avg_p>=60 [contract · benched, activated 2026-10-20, certified valid n=566] — PROVISIONAL (settled n=4 < 30) — hit_rate 0.75 (3/4 settled) · ROI 0.0973 (4 priced)
- `pfc_14ee12458803822df3013bcd`: 1x2 single[zulubet] avg_p>=45 [contract · benched, activated 2026-10-20, certified valid n=1488] — PROVISIONAL (settled n=1 < 30) — hit_rate 0.0 (0/1 settled) · ROI unavailable (0 priced)
- `pfc_234f16641d9893e8ec2a01f0`: 1x2 unanimous[vitibet+zulubet] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=427] — PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI 0.07 (2 priced)
- `pfc_2bd498a3472b7bbd71982ece`: 1x2 unanimous[vitibet+zulubet] avg_p>=55 [contract · benched, activated 2026-10-20, certified valid n=358] — PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI -1.0 (1 priced)
- `pfc_35f7e50bf23db96c2d3dd59d`: 1x2 single[zulubet] avg_p>=60 [contract · benched, activated 2026-10-20, certified valid n=633] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI unavailable (0 priced)
- `pfc_3bfaf30507905754f7faab2a`: 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 [contract · benched, activated 2026-10-20, certified valid n=645] — PROVISIONAL (settled n=1 < 30) — hit_rate 0.0 (0/1 settled) · ROI -1.0 (1 priced)
- `pfc_439097cb9bb700e9996c0b07`: 1x2 single[scoutingstats] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=1235] — PROVISIONAL (settled n=6 < 30) — hit_rate 0.666667 (4/6 settled) · ROI 0.116167 (6 priced)
- `pfc_4cf3df8552488297d7ccf526`: 1x2 single[zulubet] avg_p>=50 [contract · benched, activated 2026-10-20, certified valid n=1241] — PROVISIONAL (settled n=4 < 30) — hit_rate 0.5 (2/4 settled) · ROI 0.9 (2 priced)
- `pfc_b011652ec3e473fbc0afbb6a`: 1x2 unanimous[vitibet+zulubet] avg_p>=45 [contract · certified, activated 2026-10-20, certified valid n=488] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI 1.6 (1 priced)
- `pfc_c8cbcf76ea758fd6de596ae1`: 1x2 single[zulubet] avg_p>=70 [contract · benched, activated 2026-10-20, certified valid n=242] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI unavailable (0 priced)
- `unanimous[betclan+statarea+vitibet] avg_p>=65`: PROVISIONAL (settled n=2 < 30) — hit_rate 1.0 (2/2 settled) · ROI 0.5 (2 priced)
- `unanimous[betclan+vitibet] avg_p>=70`: PROVISIONAL (settled n=17 < 30) — hit_rate 0.941176 (16/17 settled) · ROI 0.3409 (13 priced)
- `unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65`: PROVISIONAL (settled n=2 < 30) — hit_rate 1.0 (2/2 settled) · ROI 0.18 (2 priced)
- `unanimous[bzzoiro+statarea+vitibet] avg_p>=65`: PROVISIONAL (settled n=5 < 30) — hit_rate 0.6 (3/5 settled) · ROI -0.335125 (4 priced)
- `unanimous[bzzoiro+vitibet+zulubet] avg_p>=65`: PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI 0.15 (1 priced)
- `unanimous[bzzoiro+vitibet] avg_p>=70`: PROVISIONAL (settled n=13 < 30) — hit_rate 0.692308 (9/13 settled) · ROI -0.035815 (13 priced)
- `unanimous[statarea+vitibet+zulubet] avg_p>=65`: PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI -0.025 (2 priced)
- `unanimous[statarea+vitibet] avg_p>=70`: PROVISIONAL (settled n=20 < 30) — hit_rate 0.9 (18/20 settled) · ROI 0.16666 (15 priced)
- `unanimous[vitibet+zulubet] avg_p>=70`: PROVISIONAL (settled n=5 < 30) — hit_rate 1.0 (5/5 settled) · ROI 0.3925 (5 priced)

## By bucket

- `CAUTION`: settled=54, wins=33, hit_rate=0.611111 (settled n=54), ROI=-0.002713 (priced n=54)
- `CERTIFIED_CLEAN`: settled=87, wins=55, hit_rate=0.632184 (settled n=87), ROI=0.008275 (priced n=87)
- `SKIPPED_VETO`: settled=348, wins=257, hit_rate=0.738506 (settled n=348), ROI=0.060779 (priced n=307)
- `WATCHLIST_NO_ODDS`: settled=68, wins=44, hit_rate=0.647059 (settled n=68), ROI=None (priced n=0)
- `WATCHLIST_SUSPECT_PRICE`: settled=16, wins=10, hit_rate=0.625 (settled n=16), ROI=-0.068 (priced n=10)
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=70, wins=49, hit_rate=0.7 (settled n=70), ROI=0.025429 (priced n=70)
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333 (settled n=6), ROI=-0.001667 (priced n=6)

## By odds source

- `UNKNOWN`: settled=115, wins=77, hit_rate=0.669565 (settled n=115), ROI=None (priced n=0)
- `betexplorer_odds`: settled=178, wins=133, hit_rate=0.747191 (settled n=178), ROI=0.010899 (priced n=178)
- `boggio`: settled=2, wins=2, hit_rate=1.0 (settled n=2), ROI=0.486 (priced n=2)
- `bzzoiro_odds`: settled=4, wins=4, hit_rate=1.0 (settled n=4), ROI=0.4625 (priced n=4)
- `forebet_best`: settled=39, wins=28, hit_rate=0.717949 (settled n=39), ROI=0.028205 (priced n=39)
- `oddspapi_odds`: settled=9, wins=5, hit_rate=0.555556 (settled n=9), ROI=-0.036111 (priced n=9)
- `pinnapi_odds`: settled=70, wins=44, hit_rate=0.628571 (settled n=70), ROI=0.071066 (priced n=70)
- `scoutingstats_odds`: settled=122, wins=85, hit_rate=0.696721 (settled n=122), ROI=0.011967 (priced n=122)
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0 (settled n=1), ROI=0.741 (priced n=1)
- `theoddsapi`: settled=64, wins=48, hit_rate=0.75 (settled n=64), ROI=0.144063 (priced n=64)
- `zulubet`: settled=45, wins=26, hit_rate=0.577778 (settled n=45), ROI=-0.035778 (priced n=45)

## By odds match method

- `alias_fuzzy`: settled=33, wins=22, hit_rate=0.666667 (settled n=33), ROI=-0.039167 (priced n=24)
- `betexplorer`: settled=88, wins=62, hit_rate=0.704545 (settled n=88), ROI=-0.029545 (priced n=88)
- `exact`: settled=362, wins=260, hit_rate=0.718232 (settled n=362), ROI=0.064731 (priced n=362)
- `fallback`: settled=60, wins=39, hit_rate=0.65 (settled n=60), ROI=0.007167 (priced n=60)
- `none`: settled=106, wins=70, hit_rate=0.660377 (settled n=106), ROI=None (priced n=0)

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 2 | 2 | 1.0 | 2 | 0.486 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 88 | 62 | 0.704545 | 88 | -0.029545 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 4 | 4 | 1.0 | 4 | 0.4625 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 234 | 169 | 0.722222 | 234 | 0.08184 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 122 | 85 | 0.696721 | 122 | 0.011967 |
| Source fallback (`SOURCE_FALLBACK`) | 60 | 39 | 0.65 | 60 | 0.007167 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 33 | 22 | 0.666667 | 24 | -0.039167 |
| No usable price (`UNMATCHED`) | 106 | 70 | 0.660377 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 348 | 257 | 0.738506 | 307 | 0.060779 |
| **trusted evidence only** | 214 | 164 | 0.766355 | 214 | 0.088968 |
| **soft evidence only** | 134 | 93 | 0.69403 | 93 | -0.004086 |
| evidence: BETEXPLORER_RESCUE | 55 | 40 | 0.727273 | 55 | -0.035455 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.4 |
| evidence: NAMED_BOOKMAKER_PRICE | 156 | 121 | 0.775641 | 156 | 0.126854 |
| evidence: SCOUTINGSTATS_SOLE | 52 | 36 | 0.692308 | 52 | -0.006154 |
| evidence: SOURCE_FALLBACK | 27 | 19 | 0.703704 | 27 | 0.007407 |
| evidence: SUSPECT_ALIAS_FUZZY | 17 | 12 | 0.705882 | 14 | -0.018571 |
| evidence: UNMATCHED | 38 | 26 | 0.684211 | 0 | None |
| odds band: <1.50 | 193 | 154 | 0.797927 | 193 | 0.008422 |
| odds band: 1.50-2.00 | 94 | 63 | 0.670213 | 94 | 0.110998 |
| odds band: 2.00-3.00 | 16 | 10 | 0.625 | 16 | 0.4125 |
| odds band: >=3.00 | 4 | 1 | 0.25 | 4 | 0.0 |
| odds band: unpriced | 41 | 29 | 0.707317 | 0 | None |
| veto reason: context VETO in ['competition_type'] | 46 | 39 | 0.847826 | 36 | 0.1301 |
| veto reason: context VETO in ['league', 'niche'] | 4 | 3 | 0.75 | 3 | -0.100333 |
| veto reason: context VETO in ['league', 'odds_band'] | 3 | 1 | 0.333333 | 3 | -0.506667 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.3881 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 6 | 4 | 0.666667 | 5 | 0.186 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.265 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 4 | 3 | 0.75 | 4 | 0.0725 |
| veto reason: context VETO in ['league'] | 29 | 16 | 0.551724 | 22 | -0.248718 |
| veto reason: context VETO in ['niche'] | 10 | 6 | 0.6 | 10 | -0.186 |
| veto reason: context VETO in ['odds_band'] | 59 | 41 | 0.694915 | 59 | -0.029937 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 6 | 5 | 0.833333 | 6 | 0.20035 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.212222 |
| veto reason: context VETO in ['team_a'] | 59 | 46 | 0.779661 | 50 | 0.195616 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 12 | 10 | 0.833333 | 11 | 0.066918 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 4 | 1.0 | 4 | 0.4775 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.098571 |
| veto reason: context VETO in ['team_h', 'team_a', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.62 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 13 | 0.764706 | 16 | 0.266519 |
| veto reason: context VETO in ['team_h'] | 47 | 34 | 0.723404 | 36 | 0.123889 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.08 | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: short-odds away favourite 1.16 | 2 | 2 | 1.0 | 2 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: APPROVED_DONOR_PRICE | 1 | 1 | 1.0 | 1 | 0.452 |
| contrast CAUTION: BETEXPLORER_RESCUE | 18 | 9 | 0.5 | 18 | -0.2 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 26 | 18 | 0.692308 | 26 | 0.160058 |
| contrast CAUTION: SOURCE_FALLBACK | 9 | 5 | 0.555556 | 9 | -0.128889 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 474 | 334 | 0.704641 | 369 | 0.051579 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 33 | 22 | 0.666667 | 24 | -0.039167 | 33 | 1.633809 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 122 | 85 | 0.696721 | 122 | 0.011967 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 19 | 11 | 0.578947 | 19 | 0.040526 | 0 | None |
| stale_quote (`stale_quote`) | 1 | 1 | 1.0 | 0 | None | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-20: AS Roma vs Slovan Bratislava (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.15 -> 🟢 WON (Expected prob: 83.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 83.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 55.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 94.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 83.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected 87.4% (Actual: 4 home goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected 65.0% (Actual: BTTS-No)

### 2026-10-20: Manchester City vs AEK Athens FC (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.11 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 79.7% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 42.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 89.0% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 53.2% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 52.0% (Actual: 6 goals)
    - [🔴 MISS] **Match Under 3.5 Goals**: expected 48.0% (Actual: 6 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.8% (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 27.0% (Actual: 6 goals)

### 2026-10-20: El Geish vs Pyramids FC (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.45 -> 🟢 WON (Expected prob: 67.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.5% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 39.1% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 86.1% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 81.6% (Actual: 5 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 60.4% (Actual: 5 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 56.3% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 43.7% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 41.8% (Actual: 5 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 39.6% (Actual: 5 goals)

### 2026-10-20: Huddersfield vs Peterborough (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 66.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 67.9% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 85.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 61.1% (Actual: 5 goals)
    - [🔴 MISS] **Match Under 3.5 Goals**: expected 60.9% (Actual: 5 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 54.1% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 45.9% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 39.1% (Actual: 5 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 38.9% (Actual: 5 goals)

### 2026-10-20: Barnet vs Swindon Town (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🔴 LOST (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 85.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 89.7% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 61.3% (Actual: 4 goals)
    - [🔴 MISS] **Match Under 3.5 Goals**: expected 60.3% (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected 54.0% (Actual: BTTS-Yes)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 46.0% (Actual: BTTS-Yes)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 39.7% (Actual: 4 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 38.7% (Actual: 4 goals)

### 2026-10-20: Al Taawoun vs Al-Qadsiah (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.452 -> 🟢 WON (Expected prob: 63.2%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Cúcuta Deportivo vs Atlético Nacional (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.5848 -> 🔴 LOST (Expected prob: 60.5%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Tadley Calleva vs Aldershot Town (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.5405 -> 🟢 WON (Expected prob: 58.9%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Chesterfield vs Colchester United (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5988 -> 🔴 LOST (Expected prob: 58.1%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Hajer vs Al Najma (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.6329 -> 🟢 WON (Expected prob: 55.7%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Bromley vs Leicester City (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.7299 -> 🟢 WON (Expected prob: 54.7%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Paris Saint Germain vs Barcelona (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 2.6 -> 🟢 WON (Expected prob: 46.5%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Oxford United vs Wigan (Actual Score: **2-1**)
- **1X2 Pick**: Selected `DRAW` @ 3.53 -> 🔴 LOST (Expected prob: 51.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Yeovil Town vs Leatherhead (Actual Score: **5-2**)
- **1X2 Pick**: Selected `HOME` @ 1.369 -> 🟢 WON (Expected prob: 66.2%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Luton Town vs Barnsley (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5682 -> 🟢 WON (Expected prob: 60.3%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Ebbsfleet United vs Horsham (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4484 -> 🔴 LOST (Expected prob: 60.7%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Gloucester City vs Barrow (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.7937 -> 🟢 WON (Expected prob: 51.3%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Liverpool U19 vs Villarreal U19 (Actual Score: **4-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 61.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: FC Porto vs PSV Eindhoven (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.81 -> 🔴 LOST (Expected prob: 62.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Fenerbahçe vs Slavia Praha (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 2.42 -> 🔴 LOST (Expected prob: 62.5%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: ASA Targu Mures vs Chindia Targoviste (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 2.14 -> 🟢 WON (Expected prob: 62.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Larne vs Linfield (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.9804 -> 🔴 LOST (Expected prob: 53.4%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Ario Eslamshahr vs Naft Bandar Abbas (Actual Score: **4-0**)
- **1X2 Pick**: Selected `DRAW` @ n/a -> 🔴 LOST (Expected prob: 56.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Masr vs Future FC (Actual Score: **3-2**)
- **1X2 Pick**: Selected `DRAW` @ n/a -> 🔴 LOST (Expected prob: 55.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Stuttgart U19 vs Atlético Madrid U19 (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 54.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: Sabah FA vs Borussia Dortmund (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 82.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: SSC Napoli vs Bodo/Glimt (Actual Score: **4-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 61.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-20: VfB Stuttgart vs Atletico Madrid (Actual Score: **1-1**)
- **1X2 Pick**: Selected `DRAW` @ 3.8 -> 🟢 WON (Expected prob: 50.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| CANCELLED | 1 |
| POSTPONED | 2 |
- 2026-09-22 `POSTPONED` `SKIPPED_VETO` — MC Alger vs MC Oran (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-09-26 `POSTPONED` `SKIPPED_VETO` — Crawley Town vs Barnet (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-03 `CANCELLED` `CAUTION` — Sri Lanka vs Djibouti (source_status:scoutingstats); excluded from win/loss/ROI

## Rescheduled Fixture Examples

- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca (w) 4-1 Santos Laguna (w) [home])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ None (rescheduled → 2026-10-03; actual Tampa Bay Rowdies 1-2 Miami FC [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Brooklyn vs Rhode Island FC -> AWAY @ None (rescheduled → 2026-10-03; actual Brooklyn 1-3 Rhode Island [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kano Pillars FC vs Sporting Lagos -> HOME @ None (rescheduled → 2026-10-03; actual Kano Pillars 1-1 Sporting Lagos [draw])
- 2026-10-18 `SKIPPED_VETO` `unanimous[bzzoiro+vitibet] avg_p>=70` — Hartford Athletic vs Brooklyn -> HOME @ 1.44 (rescheduled → 2026-10-17; actual Hartford Athletic 2-3 Brooklyn [away])

## Pending / Unmatched Result Examples

- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Milevsko vs Spartak Sobeslav -> AWAY @ 1.57 (pending_or_unmatched_result); keys=['milevsko']/['spartakso']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Polanka nad Odrou vs Frydek-Mistek -> AWAY @ 1.48 (pending_or_unmatched_result); keys=['polankana']/['frydekmis']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Brommapojkarna W vs Malmö FF W -> AWAY @ 1.4 (pending_or_unmatched_result); keys=['brommapoj']/['malmoff', 'malmoffww']
- 2026-09-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — Plateau United vs Inter Lagos -> HOME @ 1.33 (pending_or_unmatched_result); keys=['plateauun']/['interlago']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Rheindorf Altach II vs Hohenems -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['hohenems']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kufstein vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['kufstein']/['imst']
- 2026-10-09 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Real Cundinamarca vs Real Santander -> HOME @ None (pending_or_unmatched_result); keys=['cundinama']/['santander']
- 2026-10-11 `SKIPPED_VETO` `ml-meta avg_p>=60` — Atletico Nacional vs Deportivo Pasto -> HOME @ 2.1 (pending_or_unmatched_result); keys=['nacional']/['pasto']
- 2026-10-11 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Ranger's vs Carroi -> HOME @ None (pending_or_unmatched_result); keys=['rangers']/['carroi']
- 2026-10-18 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Wolfurt vs Schwaz -> AWAY @ None (pending_or_unmatched_result); keys=['wolfurt']/['schwaz']
- 2026-10-18 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Rheindorf Altach II vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['imst']

## Ambiguous result examples

- none

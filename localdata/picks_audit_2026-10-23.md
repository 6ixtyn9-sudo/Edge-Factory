# Edge Factory — Recent picks audit (2026-09-24 to 2026-10-23)

## Overall

- archived pick rows: 793
- archived pick dates: 30
- immutable morning-baseline rows: 629
- late-slate additions (regular-ledger rows not in the morning baseline): 166, of which on days whose regular ledger was rewritten: 138
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 25
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 699
- eligible prior picks: 718
- pending/unmatched result picks: 16
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 2
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 24
- ambiguous result picks: 1
- wins: 479
- hit rate: +68.5% (wins/settled: 479/699)
- priced picks: 574
- ROI: +4.0% (P&L / 574 priced picks)

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-23
- same-day rows excluded: 75

Fixture-level secondary rates below score the fixture behind every settled pick; they are not enhancement-bet returns.
## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 424 / 699 matches (60.7%)
- **Both Teams to Score (BTTS)**: occurred in 370 / 699 matches (52.9%)
- **Selected Team Over 1.5 Goals**: occurred in 462 / 695 matches (66.5%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 596
- **Total Hits**: 462
- **Overall Hit Rate**: 77.5%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, settled=18, hit_rate=94.4% (hits=17/recommended=18), priced_n=1, priced_ROI=0.64 (denominator=1), registry_processed=53, class=priced
- `away_under_15`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=4, priced_ROI=2.4075 (denominator=4), registry_processed=5, class=priced
- `away_under_25`: recommended=4, settled=4, hit_rate=50.0% (hits=2/recommended=4), priced_n=4, priced_ROI=0.06725 (denominator=4), registry_processed=36, class=priced
- `away_under_35`: recommended=166, settled=166, hit_rate=96.4% (hits=160/recommended=166), priced_n=1, priced_ROI=0.435 (denominator=1), registry_processed=305, class=priced
- `btts_no`: recommended=8, settled=8, hit_rate=37.5% (hits=3/recommended=8), priced_n=5, priced_ROI=-0.45 (denominator=5), registry_processed=8, class=priced
- `btts_yes`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=3, priced_ROI=0.853333 (denominator=3), registry_processed=18, class=priced
- `home_over_05`: recommended=24, settled=24, hit_rate=87.5% (hits=21/recommended=24), priced_n=2, priced_ROI=0.345 (denominator=2), registry_processed=187, class=priced
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=0.381 (denominator=2), registry_processed=2, class=priced
- `home_under_25`: recommended=1, settled=1, hit_rate=0.0% (hits=0/recommended=1), priced_n=1, priced_ROI=-1.0 (denominator=1), registry_processed=41, class=priced
- `home_under_35`: recommended=50, settled=50, hit_rate=98.0% (hits=49/recommended=50), priced_n=0, priced_ROI=None (denominator=0), registry_processed=74, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=25, settled=25, hit_rate=88.0% (hits=22/recommended=25), priced_n=18, priced_ROI=0.155222 (denominator=18), registry_processed=72, class=priced
- `match_over_25`: recommended=264, settled=264, hit_rate=59.8% (hits=158/recommended=264), priced_n=186, priced_ROI=-0.048226 (denominator=186), registry_processed=706, class=priced
- `match_over_35`: recommended=18, settled=18, hit_rate=77.8% (hits=14/recommended=18), priced_n=11, priced_ROI=1.036364 (denominator=11), registry_processed=43, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=4.0 (denominator=2), registry_processed=2, class=priced
- `match_under_45`: recommended=4, settled=4, hit_rate=50.0% (hits=2/recommended=4), priced_n=4, priced_ROI=0.0575 (denominator=4), registry_processed=4, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2383** | scored: 2383

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 573 | 573 | 342 | 59.7% | 48.3% | +11.4% | 0.256917 |
| `match_over_45` | 384 | 384 | 85 | 22.1% | 23.9% | -1.8% | 0.17409 |
| `away_under_35` | 332 | 332 | 323 | 97.3% | 96.0% | +1.3% | 0.026385 |
| `away_under_25` | 323 | 323 | 297 | 92.0% | 89.5% | +2.5% | 0.071913 |
| `home_under_35` | 138 | 138 | 133 | 96.4% | 95.7% | +0.7% | 0.035546 |
| `match_over_35` | 127 | 127 | 68 | 53.5% | 42.8% | +10.8% | 0.270867 |
| `home_under_25` | 108 | 108 | 100 | 92.6% | 87.7% | +4.9% | 0.07212 |
| `btts_yes` | 92 | 92 | 55 | 59.8% | 47.1% | +12.7% | 0.248418 |
| `btts_no` | 85 | 85 | 36 | 42.4% | 54.1% | -11.7% | 0.252474 |
| `away_over_05` | 45 | 45 | 39 | 86.7% | 80.0% | +6.6% | 0.114247 |
| `away_under_15` | 45 | 45 | 31 | 68.9% | 77.3% | -8.4% | 0.194701 |
| `home_over_05` | 39 | 39 | 33 | 84.6% | 86.0% | -1.4% | 0.118549 |
| `match_over_15` | 30 | 30 | 24 | 80.0% | 84.3% | -4.3% | 0.160763 |
| `match_under_25` | 26 | 26 | 10 | 38.5% | 40.8% | -2.3% | 0.238415 |
| `home_under_15` | 10 | 10 | 8 | 80.0% | 69.9% | +10.1% | 0.22758 |
| `match_under_35` | 9 | 9 | 3 | 33.3% | 62.4% | -29.0% | 0.291151 |
| `home_over_15` | 7 | 7 | 2 | 28.6% | 44.7% | -16.1% | 0.22064 |
| `away_over_15` | 5 | 5 | 4 | 80.0% | 59.7% | +20.3% | 0.215626 |
| `match_under_45` | 5 | 5 | 3 | 60.0% | 80.6% | -20.6% | 0.28987 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2287 | 1522 | 66.6% | 63.2% | +3.4% | 0.156734 |
| model | 96 | 74 | 77.1% | 67.3% | +9.8% | 0.182554 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 71 | 19.1% | 25.4% | +6.2% |
| 0.2-0.3 | 286 | 24.2% | 21.0% | -3.2% |
| 0.3-0.4 | 122 | 35.8% | 47.5% | +11.8% |
| 0.4-0.5 | 556 | 44.7% | 57.2% | +12.5% |
| 0.5-0.6 | 196 | 54.3% | 51.5% | -2.8% |
| 0.6-0.7 | 70 | 63.5% | 58.6% | -4.9% |
| 0.7-0.8 | 35 | 73.8% | 68.6% | -5.2% |
| 0.8-0.9 | 423 | 86.7% | 89.4% | +2.6% |
| 0.9-1.0 | 624 | 94.7% | 95.8% | +1.1% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=638, MAE=1.569232 goals, bias=-0.343777 (realized − promised), promised avg 3.549107 vs realized 3.205329

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 638 | 31.4% | 33.9% | +2.4% | 0.191955 |
| BTTS-Yes | 638 | 41.6% | 52.5% | +10.9% | 0.263702 |
| Home Over 1.5 | 638 | 63.3% | 52.5% | -10.8% | 0.230439 |
| Over 2.5 | 638 | 69.4% | 60.3% | -9.0% | 0.247273 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 259 | 8.6% | 22.4% | +13.8% |
| 0.1-0.2 | 344 | 10.5% | 17.4% | +6.9% |
| 0.2-0.3 | 43 | 24.4% | 27.9% | +3.5% |
| 0.3-0.4 | 116 | 37.1% | 49.1% | +12.0% |
| 0.4-0.5 | 475 | 42.0% | 53.1% | +11.1% |
| 0.5-0.6 | 76 | 55.6% | 63.2% | +7.5% |
| 0.6-0.7 | 423 | 66.7% | 57.2% | -9.5% |
| 0.7-0.8 | 192 | 74.6% | 66.1% | -8.5% |
| 0.8-0.9 | 559 | 84.8% | 65.5% | -19.3% |
| 0.9-1.0 | 65 | 92.1% | 75.4% | -16.7% |

## By rule

Counts are frozen PICK ROWS, not bets: rows filed under SKIPPED_VETO / WATCHLIST_* are included and were never cardable. Cardable-only counts are in `## By bucket`.

- `2way-unanimous avg_p>=60`: hit_rate 0.643312 (101/157 settled) · ROI -0.098783 (115 priced)
- `2way-unanimous avg_p>=70`: PROVISIONAL (settled n=24 < 30) — hit_rate 0.791667 (19/24 settled) · ROI 0.037647 (17 priced)
- `ml-meta avg_p>=55`: hit_rate 0.727273 (128/176 settled) · ROI 0.166551 (149 priced)
- `ml-meta avg_p>=60`: hit_rate 0.609272 (92/151 settled) · ROI -0.039168 (135 priced)
- `ml-meta avg_p>=65`: PROVISIONAL (settled n=21 < 30) — hit_rate 0.857143 (18/21 settled) · ROI 0.032667 (15 priced)
- `ml-meta avg_p>=80`: PROVISIONAL (settled n=7 < 30) — hit_rate 1.0 (7/7 settled) · ROI 0.075 (6 priced)
- `pfc_0ad08cd1b2e75a2c9051189e`: 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 [contract · benched, activated 2026-10-20, certified valid n=438] — PROVISIONAL (settled n=4 < 30) — hit_rate 0.75 (3/4 settled) · ROI 0.5525 (4 priced)
- `pfc_0b290b623e2a54ea7df3006c`: 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=201] — PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI 0.165 (2 priced)
- `pfc_0f100c9da356ed1c05d9c642`: 1x2 single[scoutingstats] avg_p>=60 [contract · benched, activated 2026-10-20, certified valid n=566] — PROVISIONAL (settled n=4 < 30) — hit_rate 0.75 (3/4 settled) · ROI 0.0973 (4 priced)
- `pfc_14ee12458803822df3013bcd`: 1x2 single[zulubet] avg_p>=45 [contract · benched, activated 2026-10-20, certified valid n=1488] — PROVISIONAL (settled n=1 < 30) — hit_rate 0.0 (0/1 settled) · ROI unavailable (0 priced)
- `pfc_1607fec83282d02c5254c2bf`: 1x2 single[zulubet] avg_p>=55 [contract · certified, activated 2026-10-20, certified valid n=864] — PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI -0.2396 (2 priced)
- `pfc_234f16641d9893e8ec2a01f0`: 1x2 unanimous[vitibet+zulubet] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=427] — PROVISIONAL (settled n=3 < 30) — hit_rate 0.666667 (2/3 settled) · ROI 0.4 (3 priced)
- `pfc_2bd498a3472b7bbd71982ece`: 1x2 unanimous[vitibet+zulubet] avg_p>=55 [contract · benched, activated 2026-10-20, certified valid n=358] — PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI -1.0 (1 priced)
- `pfc_35f7e50bf23db96c2d3dd59d`: 1x2 single[zulubet] avg_p>=60 [contract · benched, activated 2026-10-20, certified valid n=633] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI unavailable (0 priced)
- `pfc_3bfaf30507905754f7faab2a`: 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 [contract · benched, activated 2026-10-20, certified valid n=645] — PROVISIONAL (settled n=1 < 30) — hit_rate 0.0 (0/1 settled) · ROI -1.0 (1 priced)
- `pfc_439097cb9bb700e9996c0b07`: 1x2 single[scoutingstats] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=1235] — hit_rate 0.636364 (28/44 settled) · ROI -0.015746 (37 priced)
- `pfc_4a1f2bb2278d13c8189148d0`: 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 [contract · benched, activated 2026-10-20, certified valid n=426] — PROVISIONAL (settled n=7 < 30) — hit_rate 0.571429 (4/7 settled) · ROI 0.111429 (7 priced)
- `pfc_4cf3df8552488297d7ccf526`: 1x2 single[zulubet] avg_p>=50 [contract · benched, activated 2026-10-20, certified valid n=1241] — PROVISIONAL (settled n=4 < 30) — hit_rate 0.5 (2/4 settled) · ROI 0.9 (2 priced)
- `pfc_5208b9e15194a691590430ad`: 1x2 unanimous[statarea+zulubet] avg_p>=40 [contract · benched, activated 2026-10-20, certified valid n=278] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI 0.44 (1 priced)
- `pfc_5954379f3a12700edcfd8387`: 1x2 single[zulubet] avg_p>=65 [contract · benched, activated 2026-10-20, certified valid n=443] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI unavailable (0 priced)
- `pfc_5a9d3d3426ee7a4e63461d75`: 1x2 unanimous[statarea+zulubet] avg_p>=55 [contract · benched, activated 2026-10-21, certified valid n=222] — PROVISIONAL (settled n=2 < 30) — hit_rate 0.0 (0/2 settled) · ROI -1.0 (1 priced)
- `pfc_b011652ec3e473fbc0afbb6a`: 1x2 unanimous[vitibet+zulubet] avg_p>=45 [contract · candidate, activated 2026-10-20, certified valid n=488] — PROVISIONAL (settled n=2 < 30) — hit_rate 1.0 (2/2 settled) · ROI 1.64 (2 priced)
- `pfc_c8cbcf76ea758fd6de596ae1`: 1x2 single[zulubet] avg_p>=70 [contract · benched, activated 2026-10-20, certified valid n=242] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI unavailable (0 priced)
- `pfc_d94d447efe0742440e953722`: 1x2 unanimous[scoutingstats+statarea] avg_p>=40 [contract · benched, activated 2026-10-21, certified valid n=822] — PROVISIONAL (settled n=13 < 30) — hit_rate 0.384615 (5/13 settled) · ROI -0.173658 (12 priced)
- `unanimous[betclan+statarea+vitibet] avg_p>=65`: PROVISIONAL (settled n=2 < 30) — hit_rate 1.0 (2/2 settled) · ROI 0.5 (2 priced)
- `unanimous[betclan+vitibet] avg_p>=70`: PROVISIONAL (settled n=17 < 30) — hit_rate 0.941176 (16/17 settled) · ROI 0.3409 (13 priced)
- `unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65`: PROVISIONAL (settled n=2 < 30) — hit_rate 1.0 (2/2 settled) · ROI 0.18 (2 priced)
- `unanimous[bzzoiro+statarea+vitibet] avg_p>=65`: PROVISIONAL (settled n=5 < 30) — hit_rate 0.6 (3/5 settled) · ROI -0.335125 (4 priced)
- `unanimous[bzzoiro+vitibet+zulubet] avg_p>=65`: PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI 0.15 (1 priced)
- `unanimous[bzzoiro+vitibet] avg_p>=70`: PROVISIONAL (settled n=13 < 30) — hit_rate 0.692308 (9/13 settled) · ROI -0.035815 (13 priced)
- `unanimous[statarea+vitibet+zulubet] avg_p>=65`: PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI -0.025 (2 priced)
- `unanimous[statarea+vitibet] avg_p>=70`: PROVISIONAL (settled n=21 < 30) — hit_rate 0.904762 (19/21 settled) · ROI 0.17175 (16 priced)
- `unanimous[vitibet+zulubet] avg_p>=70`: PROVISIONAL (settled n=5 < 30) — hit_rate 1.0 (5/5 settled) · ROI 0.3925 (5 priced)

## By bucket

- `CAUTION`: settled=66, wins=42, hit_rate=0.636364 (settled n=66), ROI=0.073032 (priced n=66)
- `CERTIFIED_CLEAN`: settled=84, wins=51, hit_rate=0.607143 (settled n=84), ROI=-0.024635 (priced n=84)
- `SKIPPED_VETO`: settled=380, wins=273, hit_rate=0.718421 (settled n=380), ROI=0.055646 (priced n=336)
- `WATCHLIST_NO_ODDS`: settled=70, wins=45, hit_rate=0.642857 (settled n=70), ROI=None (priced n=0)
- `WATCHLIST_SUSPECT_PRICE`: settled=21, wins=13, hit_rate=0.619048 (settled n=21), ROI=-0.068 (priced n=10)
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=72, wins=49, hit_rate=0.680556 (settled n=72), ROI=0.011806 (priced n=72)
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=6, hit_rate=1.0 (settled n=6), ROI=0.201667 (priced n=6)

## By odds source

- `UNKNOWN`: settled=125, wins=83, hit_rate=0.664 (settled n=125), ROI=None (priced n=0)
- `betexplorer_odds`: settled=169, wins=128, hit_rate=0.757396 (settled n=169), ROI=0.026036 (priced n=169)
- `boggio`: settled=2, wins=2, hit_rate=1.0 (settled n=2), ROI=0.486 (priced n=2)
- `bzzoiro_odds`: settled=4, wins=4, hit_rate=1.0 (settled n=4), ROI=0.4625 (priced n=4)
- `forebet_best`: settled=37, wins=26, hit_rate=0.702703 (settled n=37), ROI=-0.002432 (priced n=37)
- `oddspapi_odds`: settled=9, wins=5, hit_rate=0.555556 (settled n=9), ROI=-0.036111 (priced n=9)
- `pinnapi_odds`: settled=109, wins=66, hit_rate=0.605505 (settled n=109), ROI=0.070092 (priced n=109)
- `scoutingstats_odds`: settled=121, wins=83, hit_rate=0.68595 (settled n=121), ROI=0.007769 (priced n=121)
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0 (settled n=1), ROI=0.741 (priced n=1)
- `theoddsapi`: settled=77, wins=55, hit_rate=0.714286 (settled n=77), ROI=0.107922 (priced n=77)
- `zulubet`: settled=45, wins=26, hit_rate=0.577778 (settled n=45), ROI=-0.035778 (priced n=45)

## By odds match method

- `alias_fuzzy`: settled=41, wins=27, hit_rate=0.658537 (settled n=41), ROI=-0.039167 (priced n=24)
- `betexplorer`: settled=72, wins=51, hit_rate=0.708333 (settled n=72), ROI=-0.014722 (priced n=72)
- `exact`: settled=420, wins=293, hit_rate=0.697619 (settled n=420), ROI=0.060924 (priced n=420)
- `fallback`: settled=58, wins=37, hit_rate=0.637931 (settled n=58), ROI=-0.013103 (priced n=58)
- `none`: settled=108, wins=71, hit_rate=0.657407 (settled n=108), ROI=None (priced n=0)

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 2 | 2 | 1.0 | 2 | 0.486 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 72 | 51 | 0.708333 | 72 | -0.014722 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 4 | 4 | 1.0 | 4 | 0.4625 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 293 | 204 | 0.696246 | 293 | 0.074491 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 121 | 83 | 0.68595 | 121 | 0.007769 |
| Source fallback (`SOURCE_FALLBACK`) | 58 | 37 | 0.637931 | 58 | -0.013103 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 41 | 27 | 0.658537 | 24 | -0.039167 |
| No usable price (`UNMATCHED`) | 108 | 71 | 0.657407 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 380 | 273 | 0.718421 | 336 | 0.055646 |
| **trusted evidence only** | 248 | 182 | 0.733871 | 248 | 0.080069 |
| **soft evidence only** | 132 | 91 | 0.689394 | 88 | -0.013182 |
| evidence: BETEXPLORER_RESCUE | 45 | 34 | 0.755556 | 45 | 0.02 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.4 |
| evidence: NAMED_BOOKMAKER_PRICE | 200 | 145 | 0.725 | 200 | 0.088786 |
| evidence: SCOUTINGSTATS_SOLE | 49 | 34 | 0.693878 | 49 | 0.001837 |
| evidence: SOURCE_FALLBACK | 25 | 17 | 0.68 | 25 | -0.0396 |
| evidence: SUSPECT_ALIAS_FUZZY | 20 | 14 | 0.7 | 14 | -0.018571 |
| evidence: UNMATCHED | 38 | 26 | 0.684211 | 0 | None |
| odds band: <1.50 | 190 | 152 | 0.8 | 190 | 0.016115 |
| odds band: 1.50-2.00 | 113 | 73 | 0.646018 | 113 | 0.078631 |
| odds band: 2.00-3.00 | 29 | 16 | 0.551724 | 29 | 0.232759 |
| odds band: >=3.00 | 4 | 1 | 0.25 | 4 | 0.0 |
| odds band: unpriced | 44 | 31 | 0.704545 | 0 | None |
| veto reason: context VETO in ['competition_type'] | 47 | 39 | 0.829787 | 37 | 0.099557 |
| veto reason: context VETO in ['league', 'niche'] | 8 | 5 | 0.625 | 5 | -0.4602 |
| veto reason: context VETO in ['league', 'odds_band', 'niche'] | 4 | 0 | 0.0 | 4 | -1.0 |
| veto reason: context VETO in ['league', 'odds_band'] | 8 | 4 | 0.5 | 8 | -0.086887 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.3881 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 6 | 4 | 0.666667 | 5 | 0.186 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.265 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 4 | 3 | 0.75 | 4 | 0.0725 |
| veto reason: context VETO in ['league'] | 37 | 21 | 0.567568 | 29 | -0.174255 |
| veto reason: context VETO in ['niche'] | 11 | 6 | 0.545455 | 11 | -0.236955 |
| veto reason: context VETO in ['odds_band'] | 74 | 51 | 0.689189 | 74 | 0.048741 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 6 | 5 | 0.833333 | 6 | 0.20035 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.212222 |
| veto reason: context VETO in ['team_a'] | 56 | 44 | 0.785714 | 47 | 0.222996 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 13 | 11 | 0.846154 | 12 | 0.082017 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 3 | 1.0 | 3 | 0.446667 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.098571 |
| veto reason: context VETO in ['team_h', 'team_a', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.62 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 13 | 0.764706 | 16 | 0.266519 |
| veto reason: context VETO in ['team_h'] | 44 | 32 | 0.727273 | 33 | 0.155758 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.08 | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 2 | 2 | 1.0 | 2 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: APPROVED_DONOR_PRICE | 1 | 1 | 1.0 | 1 | 0.452 |
| contrast CAUTION: BETEXPLORER_RESCUE | 18 | 9 | 0.5 | 18 | -0.2 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 38 | 27 | 0.710526 | 38 | 0.240213 |
| contrast CAUTION: SOURCE_FALLBACK | 9 | 5 | 0.555556 | 9 | -0.128889 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 517 | 357 | 0.690522 | 410 | 0.0538 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 41 | 27 | 0.658537 | 24 | -0.039167 | 41 | 1.609259 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 121 | 83 | 0.68595 | 121 | 0.007769 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 19 | 11 | 0.578947 | 19 | 0.040526 | 0 | None |
| stale_quote (`stale_quote`) | 1 | 1 | 1.0 | 0 | None | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-22: Juventus vs Rennes (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5882 -> 🔴 LOST (Expected prob: 64.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 63.4% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 51.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 67.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 75.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Trabzonspor vs Hearts (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3484 -> 🟢 WON (Expected prob: 73.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Ferencvárosi vs Torreense (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 71.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.1% (Actual: 5 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 40.9% (Actual: 5 goals)

### 2026-10-22: Union Saint-Gilloise vs Hapoel Be'er Sheva (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.41 -> 🟢 WON (Expected prob: 70.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 40.9% (Actual: 4 goals)

### 2026-10-22: Llaneros vs Deportivo Cali (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 2.68 -> 🟢 WON (Expected prob: 48.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 71.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 60.4% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Atlas vs América (Actual Score: **2-5**)
- **1X2 Pick**: Selected `AWAY` @ 2.05 -> 🟢 WON (Expected prob: 47.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 54.6% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 72.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 55.3% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Under 4.5 Goals**: expected 83.4% (Actual: 7 goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 72.5% (Actual: 2 home goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 70.7% (Actual: 5 away goals)
    - [🔴 MISS] **Match Under 3.5 Goals**: expected 69.7% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 62.3% (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 55.3% (Actual: 5 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.6% (Actual: 7 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 45.4% (Actual: 7 goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 44.7% (Actual: 5 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 30.3% (Actual: 7 goals)
    - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 27.5% (Actual: 2 home goals)

### 2026-10-22: Beşiktaş vs Crystal Palace (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 2.07 -> 🔴 LOST (Expected prob: 45.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 57.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 56.8% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 70.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Monaco vs SC Freiburg (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 2.25 -> 🟢 WON (Expected prob: 42.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 57.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 56.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 70.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Pachuca vs Cruz Azul (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 2.26 -> 🟢 WON (Expected prob: 42.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 54.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 72.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 55.3% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Under 4.5 Goals**: expected 83.4% (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 72.5% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 70.7% (Actual: 2 away goals)
    - [🟢 HIT] **Match Under 3.5 Goals**: expected 69.7% (Actual: 3 goals)
    - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 55.3% (Actual: 2 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 54.6% (Actual: 3 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 45.4% (Actual: 3 goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 44.7% (Actual: 2 away goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 30.3% (Actual: 3 goals)
    - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 27.5% (Actual: 1 home goals)

### 2026-10-22: Ajax vs Atalanta (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 2.07 -> 🟢 WON (Expected prob: 38.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 57.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 57.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 56.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 70.6% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Barranquilla vs America de Cali (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.5208 -> 🟢 WON (Expected prob: 65.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 60.7% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 51.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 74.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 61.5% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 65.4% (Actual: 4 away goals)
    - [🔴 MISS] **Match Under 3.5 Goals**: expected 62.0% (Actual: 4 goals)
    - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 61.5% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 60.7% (Actual: 4 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 59.5% (Actual: 0 home goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 39.3% (Actual: 4 goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 38.5% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 38.0% (Actual: 4 goals)
    - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 25.3% (Actual: 0 home goals)

### 2026-10-22: Columbus Crew vs St. Louis City (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 2.35 -> 🔴 LOST (Expected prob: 60.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.6% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 77.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Lincoln Red Imps vs FC Twente (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.22 -> 🟢 WON (Expected prob: 77.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Jablonec vs Brighton & Hove Albion (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 75.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 57.8% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Toluca vs Tijuana (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.28 -> 🔴 LOST (Expected prob: 74.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Santa Fe vs Jaguares de Córdoba (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 73.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Al Shahaniya vs Al Sadd (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.27 -> 🟢 WON (Expected prob: 71.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Omonia Nicosia vs Benfica (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.3484 -> 🟢 WON (Expected prob: 70.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Lillestrøm vs Real Sociedad (Actual Score: **0-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.53 -> 🟢 WON (Expected prob: 65.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.8% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 57.8% (Actual: 6 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 42.2% (Actual: 6 goals)

### 2026-10-22: Celje vs Salzburg (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.5988 -> 🔴 LOST (Expected prob: 61.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.8% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Inter Club d'Escaldes vs Universitatea Craiova (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.63 -> 🟢 WON (Expected prob: 59.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.8% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 57.8% (Actual: 4 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 42.2% (Actual: 4 goals)

### 2026-10-22: Pafos FC vs Riga (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.67 -> 🔴 LOST (Expected prob: 59.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected 40.9% (Actual: 2 goals)

### 2026-10-22: FC Midtjylland vs Sint-Truiden (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.68 -> 🔴 LOST (Expected prob: 57.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 59.1% (Actual: 1 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected 40.9% (Actual: 1 goals)

### 2026-10-22: Kairat vs Panathinaikos (Actual Score: **1-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.69 -> 🟢 WON (Expected prob: 57.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.8% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 57.8% (Actual: 6 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 42.2% (Actual: 6 goals)

### 2026-10-22: Kauno Žalgiris vs Brann (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.7634 -> 🟢 WON (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Lech Poznań vs Sunderland (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.81 -> 🔴 LOST (Expected prob: 55.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 57.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 57.8% (Actual: 2 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected 42.2% (Actual: 2 goals)

### 2026-10-22: Viktoria Plzeň vs Levski Sofia (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.7813 -> 🔴 LOST (Expected prob: 54.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Borac Banja Luka vs KuPS (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.813 -> 🟢 WON (Expected prob: 53.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Getafe vs Lugano (Actual Score: **2-5**)
- **1X2 Pick**: Selected `HOME` @ 1.97 -> 🔴 LOST (Expected prob: 52.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 59.1% (Actual: 7 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 40.9% (Actual: 7 goals)

### 2026-10-22: Puebla vs Monterrey (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.8621 -> 🟢 WON (Expected prob: 51.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Under 4.5 Goals**: expected 79.6% (Actual: 5 goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.7% (Actual: 1 home goals)
    - [🔴 MISS] **Away Team Under 2.5 Goals**: expected 66.1% (Actual: 4 away goals)
    - [🔴 MISS] **Match Under 3.5 Goals**: expected 64.5% (Actual: 5 goals)
    - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.2% (Actual: 4 away goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 58.1% (Actual: 1 home goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 57.8% (Actual: 5 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 42.2% (Actual: 5 goals)
    - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 36.8% (Actual: 4 away goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected 35.5% (Actual: 5 goals)

### 2026-10-22: Sporting Braga vs Gent (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.96 -> 🟢 WON (Expected prob: 50.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected 40.9% (Actual: 2 goals)

### 2026-10-22: Palmeiras vs Fluminense (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.74 -> 🔴 LOST (Expected prob: 61.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 62.2% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 67.6% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 78.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 62.2% (Actual: 1 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected 37.8% (Actual: 1 goals)

### 2026-10-22: Nordsjælland vs CSKA Sofia (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3846 -> 🔴 LOST (Expected prob: 62.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 57.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 56.8% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 70.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: FK Jablonec vs Brighton (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 74.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 61.3% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 46.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 81.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 70.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 61.3% (Actual: 0 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected 38.7% (Actual: 0 goals)

### 2026-10-22: Olympiacos F.C. vs Sparta Praha (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 62.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-22: Công an Hà Nội vs Đông Á Thanh Hoá (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🔴 LOST (Expected prob: 74.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| CANCELLED | 1 |
| POSTPONED | 1 |
- 2026-09-26 `POSTPONED` `SKIPPED_VETO` — Crawley Town vs Barnet (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-03 `CANCELLED` `CAUTION` — Sri Lanka vs Djibouti (source_status:scoutingstats); excluded from win/loss/ROI

## Rescheduled Fixture Examples

- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca (w) 4-1 Santos Laguna (w) [home])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ None (rescheduled → 2026-10-03; actual Tampa Bay Rowdies 1-2 Miami FC [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Brooklyn vs Rhode Island FC -> AWAY @ None (rescheduled → 2026-10-03; actual Brooklyn 1-3 Rhode Island [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kano Pillars FC vs Sporting Lagos -> HOME @ None (rescheduled → 2026-10-03; actual Kano Pillars 1-1 Sporting Lagos [draw])
- 2026-10-18 `SKIPPED_VETO` `unanimous[bzzoiro+vitibet] avg_p>=70` — Hartford Athletic vs Brooklyn -> HOME @ 1.44 (rescheduled → 2026-10-17; actual Hartford Athletic 2-3 Brooklyn [away])
- 2026-10-21 `WATCHLIST_UNCORROBORATED_PRICE` `pfc_439097cb9bb700e9996c0b07` — Cerro Porteño vs Sportivo Ameliano -> HOME @ 1.65 (rescheduled → 2026-10-18; actual Cerro Porteno 2-2 Sportivo Ameliano [draw])

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
- 2026-10-21 `CAUTION` `pfc_439097cb9bb700e9996c0b07` — Sporting JAX vs Louisville City -> AWAY @ 1.37 (pending_or_unmatched_result); keys=['jax']/['louisvill']
- 2026-10-21 `WATCHLIST_UNCORROBORATED_PRICE` `pfc_439097cb9bb700e9996c0b07` — Olimpia vs 2 de Mayo -> HOME @ 1.44 (pending_or_unmatched_result); keys=['olimpia']/['demayo']
- 2026-10-21 `WATCHLIST_UNKNOWN_CTX` `pfc_444d408c4ccd3a4bf4fb020c` — Sporting CP vs LASK Linz -> HOME @ 1.2101 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['lasklinz']
- 2026-10-22 `SKIPPED_VETO` `pfc_439097cb9bb700e9996c0b07` — Al Ahli vs Al Khaleej -> HOME @ 1.33 (pending_or_unmatched_result); keys=['alahli']/['alkhaleej']
- 2026-10-22 `SKIPPED_VETO` `pfc_234f16641d9893e8ec2a01f0` — Sporting JAX vs Louisville City FC -> AWAY @ 1.27 (pending_or_unmatched_result); keys=['jax']/['louisvill']

## Ambiguous result examples

- 2026-10-21 `SKIPPED_VETO` `pfc_439097cb9bb700e9996c0b07` — Guadalajara vs Necaxa (ambiguous_alias_result)

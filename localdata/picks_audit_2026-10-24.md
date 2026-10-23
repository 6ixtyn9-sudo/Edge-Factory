# Edge Factory — Recent picks audit (2026-09-25 to 2026-10-24)

## Overall

- archived pick rows: 971
- archived pick dates: 30
- immutable morning-baseline rows: 807
- late-slate additions (regular-ledger rows not in the morning baseline): 166, of which on days whose regular ledger was rewritten: 138
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 25
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 751
- eligible prior picks: 776
- pending/unmatched result picks: 21
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 2
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 25
- ambiguous result picks: 2
- wins: 511
- hit rate: +68.0% (wins/settled: 511/751)
- priced picks: 606
- ROI: +3.6% (P&L / 606 priced picks)

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-24
- same-day rows excluded: 195

Fixture-level secondary rates below score the fixture behind every settled pick; they are not enhancement-bet returns.
## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 461 / 746 matches (61.8%)
- **Both Teams to Score (BTTS)**: occurred in 400 / 746 matches (53.6%)
- **Selected Team Over 1.5 Goals**: occurred in 495 / 742 matches (66.7%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 599
- **Total Hits**: 462
- **Overall Hit Rate**: 77.1%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=19, settled=19, hit_rate=89.5% (hits=17/recommended=19), priced_n=1, priced_ROI=0.64 (denominator=1), registry_processed=59, class=priced
- `away_under_15`: recommended=6, settled=6, hit_rate=100.0% (hits=6/recommended=6), priced_n=5, priced_ROI=2.01 (denominator=5), registry_processed=8, class=priced
- `away_under_25`: recommended=5, settled=5, hit_rate=60.0% (hits=3/recommended=5), priced_n=5, priced_ROI=0.2078 (denominator=5), registry_processed=37, class=priced
- `away_under_35`: recommended=161, settled=161, hit_rate=96.3% (hits=155/recommended=161), priced_n=1, priced_ROI=0.435 (denominator=1), registry_processed=305, class=priced
- `btts_no`: recommended=8, settled=8, hit_rate=37.5% (hits=3/recommended=8), priced_n=5, priced_ROI=-0.45 (denominator=5), registry_processed=12, class=priced
- `btts_yes`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=3, priced_ROI=0.853333 (denominator=3), registry_processed=22, class=priced
- `home_over_05`: recommended=24, settled=24, hit_rate=87.5% (hits=21/recommended=24), priced_n=2, priced_ROI=0.345 (denominator=2), registry_processed=187, class=priced
- `home_over_15`: recommended=1, settled=1, hit_rate=100.0% (hits=1/recommended=1), priced_n=0, priced_ROI=None (denominator=0), registry_processed=5, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=0.381 (denominator=2), registry_processed=8, class=priced
- `home_under_25`: recommended=1, settled=1, hit_rate=0.0% (hits=0/recommended=1), priced_n=1, priced_ROI=-1.0 (denominator=1), registry_processed=47, class=priced
- `home_under_35`: recommended=50, settled=50, hit_rate=98.0% (hits=49/recommended=50), priced_n=0, priced_ROI=None (denominator=0), registry_processed=75, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=25, settled=25, hit_rate=88.0% (hits=22/recommended=25), priced_n=18, priced_ROI=0.155222 (denominator=18), registry_processed=72, class=priced
- `match_over_25`: recommended=263, settled=263, hit_rate=60.5% (hits=159/recommended=263), priced_n=192, priced_ROI=-0.037083 (denominator=192), registry_processed=720, class=priced
- `match_over_35`: recommended=18, settled=18, hit_rate=77.8% (hits=14/recommended=18), priced_n=11, priced_ROI=1.036364 (denominator=11), registry_processed=49, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=4.0 (denominator=2), registry_processed=3, class=priced
- `match_under_35`: recommended=4, settled=4, hit_rate=0.0% (hits=0/recommended=4), priced_n=4, priced_ROI=-1.0 (denominator=4), registry_processed=5, class=priced
- `match_under_45`: recommended=5, settled=5, hit_rate=60.0% (hits=3/recommended=5), priced_n=4, priced_ROI=0.0575 (denominator=4), registry_processed=7, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2417** | scored: 2417 | without promised % (legacy rows): 98

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 572 | 556 | 334 | 60.1% | 48.4% | +11.7% | 0.257049 |
| `match_over_45` | 370 | 369 | 84 | 22.8% | 23.8% | -1.1% | 0.177409 |
| `away_under_35` | 318 | 318 | 309 | 97.2% | 96.0% | +1.2% | 0.027471 |
| `away_under_25` | 310 | 309 | 283 | 91.6% | 89.5% | +2.1% | 0.074597 |
| `home_under_35` | 137 | 136 | 131 | 96.3% | 95.7% | +0.6% | 0.035978 |
| `match_over_35` | 133 | 127 | 68 | 53.5% | 42.8% | +10.8% | 0.270867 |
| `home_under_25` | 112 | 106 | 98 | 92.5% | 87.7% | +4.8% | 0.07311 |
| `btts_yes` | 96 | 92 | 55 | 59.8% | 47.1% | +12.7% | 0.248418 |
| `btts_no` | 89 | 85 | 36 | 42.4% | 54.1% | -11.7% | 0.252474 |
| `away_over_05` | 51 | 45 | 39 | 86.7% | 80.0% | +6.6% | 0.114247 |
| `away_under_15` | 48 | 45 | 31 | 68.9% | 77.3% | -8.4% | 0.194701 |
| `home_over_05` | 39 | 39 | 33 | 84.6% | 86.0% | -1.4% | 0.118549 |
| `match_over_15` | 30 | 30 | 24 | 80.0% | 84.3% | -4.3% | 0.160763 |
| `match_under_25` | 42 | 26 | 10 | 38.5% | 40.8% | -2.3% | 0.238415 |
| `home_under_15` | 16 | 10 | 8 | 80.0% | 69.9% | +10.1% | 0.22758 |
| `match_under_35` | 15 | 9 | 3 | 33.3% | 62.4% | -29.0% | 0.291151 |
| `home_over_15` | 12 | 7 | 2 | 28.6% | 44.7% | -16.1% | 0.22064 |
| `away_over_15` | 7 | 5 | 4 | 80.0% | 59.7% | +20.3% | 0.215626 |
| `match_under_45` | 8 | 5 | 3 | 60.0% | 80.6% | -20.6% | 0.28987 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2223 | 1481 | 66.6% | 63.1% | +3.5% | 0.158577 |
| model | 96 | 74 | 77.1% | 67.3% | +9.8% | 0.182554 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 69 | 19.1% | 26.1% | +7.0% |
| 0.2-0.3 | 276 | 24.2% | 21.7% | -2.4% |
| 0.3-0.4 | 119 | 35.9% | 47.9% | +12.0% |
| 0.4-0.5 | 543 | 44.7% | 57.3% | +12.5% |
| 0.5-0.6 | 192 | 54.3% | 52.1% | -2.3% |
| 0.6-0.7 | 70 | 63.5% | 58.6% | -4.9% |
| 0.7-0.8 | 35 | 73.8% | 68.6% | -5.2% |
| 0.8-0.9 | 411 | 86.7% | 89.1% | +2.3% |
| 0.9-1.0 | 604 | 94.7% | 95.7% | +1.0% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=690, MAE=1.569319 goals, bias=-0.247551 (realized − promised), promised avg 3.499725 vs realized 3.252174

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 690 | 31.8% | 34.5% | +2.7% | 0.197472 |
| BTTS-Yes | 690 | 42.8% | 53.2% | +10.4% | 0.262994 |
| Home Over 1.5 | 690 | 62.1% | 53.3% | -8.8% | 0.224384 |
| Over 2.5 | 690 | 68.3% | 61.7% | -6.5% | 0.24242 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 251 | 8.6% | 22.7% | +14.1% |
| 0.1-0.2 | 335 | 10.5% | 17.6% | +7.1% |
| 0.2-0.3 | 99 | 23.8% | 26.3% | +2.4% |
| 0.3-0.4 | 122 | 36.6% | 48.4% | +11.7% |
| 0.4-0.5 | 468 | 41.9% | 53.4% | +11.5% |
| 0.5-0.6 | 220 | 55.8% | 62.7% | +6.9% |
| 0.6-0.7 | 472 | 66.2% | 59.3% | -6.9% |
| 0.7-0.8 | 186 | 74.5% | 67.2% | -7.3% |
| 0.8-0.9 | 545 | 84.8% | 65.5% | -19.3% |
| 0.9-1.0 | 62 | 92.1% | 77.4% | -14.7% |

## By rule

Counts are frozen PICK ROWS, not bets: rows filed under SKIPPED_VETO / WATCHLIST_* are included and were never cardable. Cardable-only counts are in `## By bucket`.

- `2way-unanimous avg_p>=60`: hit_rate 0.637584 (95/149 settled) · ROI -0.110748 (107 priced)
- `2way-unanimous avg_p>=70`: PROVISIONAL (settled n=24 < 30) — hit_rate 0.791667 (19/24 settled) · ROI 0.037647 (17 priced)
- `ml-meta avg_p>=55`: hit_rate 0.724551 (121/167 settled) · ROI 0.166686 (140 priced)
- `ml-meta avg_p>=60`: hit_rate 0.609272 (92/151 settled) · ROI -0.039168 (135 priced)
- `ml-meta avg_p>=65`: PROVISIONAL (settled n=21 < 30) — hit_rate 0.857143 (18/21 settled) · ROI 0.032667 (15 priced)
- `ml-meta avg_p>=80`: PROVISIONAL (settled n=7 < 30) — hit_rate 1.0 (7/7 settled) · ROI 0.075 (6 priced)
- `pfc_0ad08cd1b2e75a2c9051189e`: 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 [contract · benched, activated 2026-10-20, certified valid n=438] — PROVISIONAL (settled n=4 < 30) — hit_rate 0.75 (3/4 settled) · ROI 0.5525 (4 priced)
- `pfc_0b290b623e2a54ea7df3006c`: 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=201] — PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI 0.165 (2 priced)
- `pfc_0f100c9da356ed1c05d9c642`: 1x2 single[scoutingstats] avg_p>=60 [contract · benched, activated 2026-10-20, certified valid n=566] — PROVISIONAL (settled n=4 < 30) — hit_rate 0.75 (3/4 settled) · ROI 0.0973 (4 priced)
- `pfc_14ee12458803822df3013bcd`: 1x2 single[zulubet] avg_p>=45 [contract · benched, activated 2026-10-20, certified valid n=1488] — PROVISIONAL (settled n=1 < 30) — hit_rate 0.0 (0/1 settled) · ROI unavailable (0 priced)
- `pfc_1607fec83282d02c5254c2bf`: 1x2 single[zulubet] avg_p>=55 [contract · certified, activated 2026-10-20, certified valid n=864] — PROVISIONAL (settled n=6 < 30) — hit_rate 0.333333 (2/6 settled) · ROI -0.493067 (3 priced)
- `pfc_234f16641d9893e8ec2a01f0`: 1x2 unanimous[vitibet+zulubet] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=427] — PROVISIONAL (settled n=5 < 30) — hit_rate 0.8 (4/5 settled) · ROI 0.336775 (4 priced)
- `pfc_27e0f725859bc708f95c58a3`: ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 [contract · certified, activated 2026-10-23, certified valid n=347] — PROVISIONAL (settled n=5 < 30) — hit_rate 1.0 (5/5 settled) · ROI 0.55188 (5 priced)
- `pfc_2bd498a3472b7bbd71982ece`: 1x2 unanimous[vitibet+zulubet] avg_p>=55 [contract · benched, activated 2026-10-20, certified valid n=358] — PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI -1.0 (1 priced)
- `pfc_35f7e50bf23db96c2d3dd59d`: 1x2 single[zulubet] avg_p>=60 [contract · benched, activated 2026-10-20, certified valid n=633] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI unavailable (0 priced)
- `pfc_3bfaf30507905754f7faab2a`: 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 [contract · benched, activated 2026-10-20, certified valid n=645] — PROVISIONAL (settled n=1 < 30) — hit_rate 0.0 (0/1 settled) · ROI -1.0 (1 priced)
- `pfc_439097cb9bb700e9996c0b07`: 1x2 single[scoutingstats] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=1235] — hit_rate 0.663043 (61/92 settled) · ROI 0.024194 (69 priced)
- `pfc_4a1f2bb2278d13c8189148d0`: 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 [contract · benched, activated 2026-10-20, certified valid n=426] — PROVISIONAL (settled n=7 < 30) — hit_rate 0.571429 (4/7 settled) · ROI 0.111429 (7 priced)
- `pfc_4cf3df8552488297d7ccf526`: 1x2 single[zulubet] avg_p>=50 [contract · benched, activated 2026-10-20, certified valid n=1241] — PROVISIONAL (settled n=4 < 30) — hit_rate 0.5 (2/4 settled) · ROI 0.9 (2 priced)
- `pfc_5208b9e15194a691590430ad`: 1x2 unanimous[statarea+zulubet] avg_p>=40 [contract · benched, activated 2026-10-20, certified valid n=278] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI 0.44 (1 priced)
- `pfc_5954379f3a12700edcfd8387`: 1x2 single[zulubet] avg_p>=65 [contract · benched, activated 2026-10-20, certified valid n=443] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI unavailable (0 priced)
- `pfc_5a9d3d3426ee7a4e63461d75`: 1x2 unanimous[statarea+zulubet] avg_p>=55 [contract · benched, activated 2026-10-21, certified valid n=222] — PROVISIONAL (settled n=3 < 30) — hit_rate 0.333333 (1/3 settled) · ROI -0.3452 (2 priced)
- `pfc_73b036a8ee8dd5a4dea48134`: 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 [contract · candidate, activated 2026-10-23, certified valid n=436] — PROVISIONAL (settled n=9 < 30) — hit_rate 0.333333 (3/9 settled) · ROI -0.361111 (9 priced)
- `pfc_b011652ec3e473fbc0afbb6a`: 1x2 unanimous[vitibet+zulubet] avg_p>=45 [contract · certified, activated 2026-10-24, certified valid n=511] — PROVISIONAL (settled n=2 < 30) — hit_rate 1.0 (2/2 settled) · ROI 1.64 (2 priced)
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

- `CAUTION`: settled=74, wins=49, hit_rate=0.662162 (settled n=74), ROI=0.104222 (priced n=74)
- `CERTIFIED_CLEAN`: settled=85, wins=51, hit_rate=0.6 (settled n=85), ROI=-0.036109 (priced n=85)
- `SKIPPED_VETO`: settled=410, wins=293, hit_rate=0.714634 (settled n=410), ROI=0.044747 (priced n=363)
- `WATCHLIST_NO_ODDS`: settled=72, wins=45, hit_rate=0.625 (settled n=72), ROI=None (priced n=0)
- `WATCHLIST_SUSPECT_PRICE`: settled=36, wins=21, hit_rate=0.583333 (settled n=36), ROI=-0.068 (priced n=10)
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=69, wins=47, hit_rate=0.681159 (settled n=69), ROI=0.013478 (priced n=69)
- `WATCHLIST_UNKNOWN_CTX`: settled=5, wins=5, hit_rate=1.0 (settled n=5), ROI=0.188 (priced n=5)

## By odds source

- `UNKNOWN`: settled=145, wins=94, hit_rate=0.648276 (settled n=145), ROI=None (priced n=0)
- `betexplorer_odds`: settled=167, wins=128, hit_rate=0.766467 (settled n=167), ROI=0.027066 (priced n=167)
- `boggio`: settled=2, wins=2, hit_rate=1.0 (settled n=2), ROI=0.486 (priced n=2)
- `bzzoiro_odds`: settled=4, wins=4, hit_rate=1.0 (settled n=4), ROI=0.4625 (priced n=4)
- `forebet_best`: settled=37, wins=26, hit_rate=0.702703 (settled n=37), ROI=-0.002432 (priced n=37)
- `oddspapi_odds`: settled=9, wins=5, hit_rate=0.555556 (settled n=9), ROI=-0.036111 (priced n=9)
- `pinnapi_odds`: settled=134, wins=81, hit_rate=0.604478 (settled n=134), ROI=0.051404 (priced n=134)
- `scoutingstats_odds`: settled=122, wins=84, hit_rate=0.688525 (settled n=122), ROI=0.008361 (priced n=122)
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0 (settled n=1), ROI=0.741 (priced n=1)
- `theoddsapi`: settled=86, wins=61, hit_rate=0.709302 (settled n=86), ROI=0.101279 (priced n=86)
- `zulubet`: settled=44, wins=25, hit_rate=0.568182 (settled n=44), ROI=-0.050227 (priced n=44)

## By odds match method

- `alias_fuzzy`: settled=58, wins=37, hit_rate=0.637931 (settled n=58), ROI=-0.039167 (priced n=24)
- `betexplorer`: settled=63, wins=45, hit_rate=0.714286 (settled n=63), ROI=-0.018413 (priced n=63)
- `exact`: settled=462, wins=321, hit_rate=0.694805 (settled n=462), ROI=0.055273 (priced n=462)
- `fallback`: settled=57, wins=36, hit_rate=0.631579 (settled n=57), ROI=-0.02386 (priced n=57)
- `none`: settled=111, wins=72, hit_rate=0.648649 (settled n=111), ROI=None (priced n=0)

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 2 | 2 | 1.0 | 2 | 0.486 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 63 | 45 | 0.714286 | 63 | -0.018413 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 4 | 4 | 1.0 | 4 | 0.4625 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 334 | 231 | 0.691617 | 334 | 0.064952 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 122 | 84 | 0.688525 | 122 | 0.008361 |
| Source fallback (`SOURCE_FALLBACK`) | 57 | 36 | 0.631579 | 57 | -0.02386 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 58 | 37 | 0.637931 | 24 | -0.039167 |
| No usable price (`UNMATCHED`) | 111 | 72 | 0.648649 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 410 | 293 | 0.714634 | 363 | 0.044747 |
| **trusted evidence only** | 271 | 196 | 0.723247 | 271 | 0.064218 |
| **soft evidence only** | 139 | 97 | 0.697842 | 92 | -0.012609 |
| evidence: BETEXPLORER_RESCUE | 41 | 31 | 0.756098 | 41 | -0.003171 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.4 |
| evidence: NAMED_BOOKMAKER_PRICE | 227 | 162 | 0.713656 | 227 | 0.071952 |
| evidence: SCOUTINGSTATS_SOLE | 53 | 37 | 0.698113 | 53 | 0.001698 |
| evidence: SOURCE_FALLBACK | 25 | 17 | 0.68 | 25 | -0.0396 |
| evidence: SUSPECT_ALIAS_FUZZY | 22 | 16 | 0.727273 | 14 | -0.018571 |
| evidence: UNMATCHED | 39 | 27 | 0.692308 | 0 | None |
| odds band: <1.50 | 201 | 163 | 0.810945 | 201 | 0.026976 |
| odds band: 1.50-2.00 | 122 | 77 | 0.631148 | 122 | 0.05517 |
| odds band: 2.00-3.00 | 36 | 18 | 0.5 | 36 | 0.113611 |
| odds band: >=3.00 | 4 | 1 | 0.25 | 4 | 0.0 |
| odds band: unpriced | 47 | 34 | 0.723404 | 0 | None |
| veto reason: context VETO in ['competition_type'] | 47 | 39 | 0.829787 | 37 | 0.099557 |
| veto reason: context VETO in ['league', 'niche'] | 9 | 6 | 0.666667 | 6 | -0.282483 |
| veto reason: context VETO in ['league', 'odds_band', 'niche'] | 4 | 0 | 0.0 | 4 | -1.0 |
| veto reason: context VETO in ['league', 'odds_band'] | 14 | 6 | 0.428571 | 14 | -0.218936 |
| veto reason: context VETO in ['league', 'team_a'] | 4 | 0 | 0.0 | 4 | -1.0 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.3881 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 6 | 4 | 0.666667 | 5 | 0.186 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.265 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 3 | 2 | 0.666667 | 3 | -0.176667 |
| veto reason: context VETO in ['league'] | 47 | 29 | 0.617021 | 36 | -0.164261 |
| veto reason: context VETO in ['niche'] | 13 | 8 | 0.615385 | 13 | -0.154869 |
| veto reason: context VETO in ['odds_band'] | 85 | 58 | 0.682353 | 85 | 0.052509 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 6 | 5 | 0.833333 | 6 | 0.20035 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.212222 |
| veto reason: context VETO in ['team_a'] | 55 | 43 | 0.781818 | 46 | 0.215887 |
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
| veto reason: short-odds away favourite 1.25 | 3 | 3 | 1.0 | 3 | 0.25 |
| veto reason: short-odds away favourite 1.27 | 2 | 2 | 1.0 | 2 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: APPROVED_DONOR_PRICE | 1 | 1 | 1.0 | 1 | 0.452 |
| contrast CAUTION: BETEXPLORER_RESCUE | 15 | 8 | 0.533333 | 15 | -0.146 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 50 | 36 | 0.72 | 50 | 0.224208 |
| contrast CAUTION: SOURCE_FALLBACK | 8 | 4 | 0.5 | 8 | -0.22 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 551 | 378 | 0.686025 | 441 | 0.048132 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 58 | 37 | 0.637931 | 24 | -0.039167 | 58 | 1.608648 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 122 | 84 | 0.688525 | 122 | 0.008361 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 19 | 11 | 0.578947 | 19 | 0.040526 | 0 | None |
| stale_quote (`stale_quote`) | 1 | 1 | 1.0 | 0 | None | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-23: Atletico Nacional vs Deportivo Pasto (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3096 -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 63.6% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 51.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 67.3% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 75.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 1.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected n/a (Actual: 0 away goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🟢 HIT] **Home Team Over 2.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 0.5 Goals**: expected n/a (Actual: 0 away goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🔴 MISS] **Match Over 4.5 Goals**: expected n/a (Actual: 3 goals)

### 2026-10-23: Caernarfon Town vs Briton Ferry (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3247 -> 🟢 WON (Expected prob: 66.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Flamengo vs Estudiantes (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3802 -> 🔴 LOST (Expected prob: 62.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Under 4.5 Goals**: expected n/a (Actual: 0 goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected n/a (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected n/a (Actual: 0 home goals)
    - [🔴 MISS] **Home Team Over 1.5 Goals**: expected n/a (Actual: 0 home goals)
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected n/a (Actual: 0 away goals)
    - [🟢 HIT] **Away Team Under 0.5 Goals**: expected n/a (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected n/a (Actual: 0 home goals)
    - [🔴 MISS] **Home Team Over 2.5 Goals**: expected n/a (Actual: 0 home goals)

### 2026-10-23: Portadown vs Linfield (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.4115 -> 🟢 WON (Expected prob: 61.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.9% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Kapfenberger SV vs St. Pölten (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.565 -> 🔴 LOST (Expected prob: 60.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 57.9% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Vitória Guimarães vs Marítimo (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.641 -> 🟢 WON (Expected prob: 60.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Bolton Wanderers vs Middlesbrough (Actual Score: **1-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.64 -> 🟢 WON (Expected prob: 59.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.9% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 6 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 6 goals)

### 2026-10-23: Galway United vs St Patrick's (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.5848 -> 🔴 LOST (Expected prob: 57.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 57.9% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: FC Volendam vs Jong FC Utrecht (Actual Score: **6-2**)
- **1X2 Pick**: Selected `HOME` @ 1.6135 -> 🟢 WON (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 8 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 6 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: First Vienna vs Floridsdorfer AC (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6494 -> 🟢 WON (Expected prob: 54.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Pineto vs Gubbio (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7463 -> 🟢 WON (Expected prob: 51.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Radnički Kragujevac vs Radnik Surdulica (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7463 -> 🟢 WON (Expected prob: 50.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Always Ready vs The Strongest (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6667 -> 🔴 LOST (Expected prob: 70.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.6% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 77.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🔴 MISS] **Home Team Over 1.5 Goals**: expected n/a (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected n/a (Actual: 1 home goals)
    - [🟢 HIT] **Match Under 3.5 Goals**: expected n/a (Actual: 2 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected n/a (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🔴 MISS] **Away Team Under 0.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected n/a (Actual: 2 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected n/a (Actual: 2 goals)
    - [🔴 MISS] **Home Team Over 2.5 Goals**: expected n/a (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected n/a (Actual: 1 home goals)

### 2026-10-23: MC Alger vs Enugu Rangers (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.05 -> 🟢 WON (Expected prob: 89.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Mamelodi Sundowns vs Wiliete (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.15 -> 🔴 LOST (Expected prob: 86.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected n/a (Actual: 2 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected n/a (Actual: 2 goals)

### 2026-10-23: Orlando Pirates vs African Stars (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.11 -> 🟢 WON (Expected prob: 81.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 4 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 4 goals)

### 2026-10-23: Shamrock Rovers vs Sligo Rovers (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.15 -> 🟢 WON (Expected prob: 79.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Under 3.5 Goals**: expected n/a (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 4 goals)
    - [🔴 MISS] **Both Teams to Score - Yes (BTTS-Yes)**: expected n/a (Actual: BTTS-No)
    - [🟢 HIT] **Both Teams to Score - No (BTTS-No)**: expected n/a (Actual: BTTS-No)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 4 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected n/a (Actual: 4 goals)

### 2026-10-23: Petro de Luanda vs Scotland Mabvuku (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 76.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Al Faisaly vs Al Nassr (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.25 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.9% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Under 3.5 Goals**: expected n/a (Actual: 4 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 4 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected n/a (Actual: BTTS-Yes)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected n/a (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 4 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected n/a (Actual: 4 goals)

### 2026-10-23: Al Sailiya vs Al Rayyan (Actual Score: **1-6**)
- **1X2 Pick**: Selected `AWAY` @ 1.25 -> 🟢 WON (Expected prob: 71.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.9% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 6 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Under 3.5 Goals**: expected n/a (Actual: 7 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 7 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected n/a (Actual: BTTS-Yes)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected n/a (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 7 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected n/a (Actual: 7 goals)

### 2026-10-23: Inter Kashi vs East Bengal (Actual Score: **1-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.25 -> 🟢 WON (Expected prob: 69.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.9% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Under 3.5 Goals**: expected n/a (Actual: 6 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 6 goals)
    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected n/a (Actual: BTTS-Yes)
    - [🔴 MISS] **Both Teams to Score - No (BTTS-No)**: expected n/a (Actual: BTTS-Yes)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 6 goals)
    - [🟢 HIT] **Match Over 3.5 Goals**: expected n/a (Actual: 6 goals)

### 2026-10-23: Oddevold vs GIF Sundsvall (Actual Score: **7-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 65.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 7 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Al Ahli vs Al Khaleej (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2632 -> 🟢 WON (Expected prob: 63.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Go Ahead Eagles vs Telstar (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.63 -> 🟢 WON (Expected prob: 62.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 5 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 5 goals)

### 2026-10-23: Nancy vs Laval (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 58.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Deportivo Alavés vs Málaga (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7634 -> 🔴 LOST (Expected prob: 57.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Bohemians vs Shelbourne (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5848 -> 🔴 LOST (Expected prob: 56.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Rot-Weiss Essen vs Jahn Regensburg (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6061 -> 🟢 WON (Expected prob: 53.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Al Shamal SC vs Qatar SC (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.7692 -> 🔴 LOST (Expected prob: 52.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Derry City vs Dundalk (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🟢 WON (Expected prob: 51.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Hvidovre vs HB Køge (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.8065 -> 🔴 LOST (Expected prob: 50.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Olympique Akbou vs CS Constantine (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.8 -> 🟢 WON (Expected prob: 50.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Dynamo Kyiv vs Kudrivka (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.1471 -> 🟢 WON (Expected prob: 72.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.9% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 51.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 77.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Under 3.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🟢 HIT] **Match Under 4.5 Goals**: expected n/a (Actual: 4 goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🔴 MISS] **Away Team Under 0.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🟢 HIT] **Home Team Over 2.5 Goals**: expected n/a (Actual: 3 home goals)

### 2026-10-23: VfB Stuttgart vs Borussia M'gladbach (Actual Score: **2-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.28 -> 🟢 WON (Expected prob: 74.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.0% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.8% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: IK Oddevold vs GIF Sundsvall (Actual Score: **7-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.56 -> 🟢 WON (Expected prob: 60.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.0% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.1% (Actual: 7 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 7 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 7 goals)

### 2026-10-23: Atlético Nacional vs Deportivo Pasto (Actual Score: **3-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6494 -> 🟢 WON (Expected prob: 55.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.8% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected n/a (Actual: 0 away goals)
    - [🔴 MISS] **Home Team Under 2.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🟢 HIT] **Home Team Over 1.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🔴 MISS] **Away Team Over 1.5 Goals**: expected n/a (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Over 2.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Under 0.5 Goals**: expected n/a (Actual: 0 away goals)

### 2026-10-23: Motor Lublin vs Zagłębie Lubin (Actual Score: **2-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.83 -> 🟢 WON (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 4 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 4 goals)

### 2026-10-23: Shimshon Tel Aviv vs Nordia Jerusalem (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 56.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.5% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.9% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.8% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 77.4% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: IK Oddevold vs GIF Sundsvall (Actual Score: **7-0**)
- **1X2 Pick**: Selected `HOME` @ 1.41 -> 🟢 WON (Expected prob: 65.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.1% (Actual: 7 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 56.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.2% (Actual: 7 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 69.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 7 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 7 goals)

### 2026-10-23: Alanyaspor vs Kocaelispor (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 2.0 -> 🔴 LOST (Expected prob: 49.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 56.3% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.2% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 69.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Motor Lublin vs Zagłębie Lubin (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 2.05 -> 🔴 LOST (Expected prob: 47.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.1% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 56.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.2% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 69.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 4 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 4 goals)

### 2026-10-23: JS Omrane vs Olympique Béja (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.9 -> 🔴 LOST (Expected prob: 47.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 57.1% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 56.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 69.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: IF Elfsborg vs Malmö FF (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 2.18 -> 🔴 LOST (Expected prob: 45.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 57.1% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 56.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.2% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 69.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected n/a (Actual: 0 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected n/a (Actual: 0 goals)

### 2026-10-23: Torino vs Monza (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 2.19 -> 🟢 WON (Expected prob: 44.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 56.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.2% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 69.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Brisbane Roar vs Perth Glory (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 2.15 -> 🟢 WON (Expected prob: 43.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 56.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 69.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🟢 HIT] **Match Under 4.5 Goals**: expected n/a (Actual: 3 goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected n/a (Actual: 2 home goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🟢 HIT] **Match Under 3.5 Goals**: expected n/a (Actual: 3 goals)
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 3 goals)
    - [🟢 HIT] **Home Team Over 1.5 Goals**: expected n/a (Actual: 2 home goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected n/a (Actual: 2 home goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected n/a (Actual: 3 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected n/a (Actual: 3 goals)
    - [🔴 MISS] **Away Team Under 0.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🔴 MISS] **Away Team Over 1.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🔴 MISS] **Home Team Over 2.5 Goals**: expected n/a (Actual: 2 home goals)

### 2026-10-23: Widzew Łódź vs Górnik Zabrze (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.5 -> 🔴 LOST (Expected prob: 40.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 57.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 54.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 69.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 54.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected n/a (Actual: 2 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected n/a (Actual: 2 goals)

### 2026-10-23: FC Corvinul Hunedoara vs FC Universitatea Cluj (Actual Score: **0-3**)
- **1X2 Pick**: Selected `HOME` @ 2.49 -> 🔴 LOST (Expected prob: 38.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 56.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.2% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 69.0% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Chernomorets 1919 Burgas vs Sportist Svoge (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 72.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.5% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.9% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 77.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Bylis vs Pogradeci (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 55.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.5% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.8% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 77.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Polissya Zhytomyr vs Obolon'-Brovar (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 77.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: VfB Stuttgart vs Borussia Mönchengladbach (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 70.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Thể Công-Viettel vs Bac Ninh (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 62.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Amstetten vs Rapid Wien II (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 61.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: UTC Cajamarca vs Melgar (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 58.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.9% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Västerås SK vs Halmstad (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 56.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Team Altamura vs Potenza Calcio (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 55.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.9% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Colwyn Bay vs Cardiff MU (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 54.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: FC Den Bosch vs MVV Maastricht (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 54.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Europa vs Real Zaragoza (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 52.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 57.9% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Boluspor vs Vanspor FK (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 51.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 57.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Almere City vs Roda JC Kerkrade (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 51.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Austria Salzburg vs Blau-Weiß Linz (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 50.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 57.9% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 77.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.4% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Jong AZ vs Helmond Sport (Actual Score: **5-4**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 50.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 9 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 5 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Polessya vs Obolon'-Brovar (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 82.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.9% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 51.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.7% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 77.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: The New Saints vs Ammanford (Actual Score: **9-0**)
- **1X2 Pick**: Selected `HOME` @ 1.01 -> 🟢 WON (Expected prob: 94.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 9 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 9 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: CA Bizertin vs Hammam-Sousse (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 56.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: JS Omrane vs Olympique Béja (Actual Score: **0-0**)
- **Over/Under 2.5 Pick**: Selected `UNDER` @ 1.44 -> 🟢 WON (Expected prob: 62.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 40.8% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 49.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 63.3% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-23: Zrinjski vs Radnik Bijeljina (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.21 -> 🟢 WON (Expected prob: 75.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
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
- 2026-10-22 `SKIPPED_VETO` `pfc_234f16641d9893e8ec2a01f0` — Sporting JAX vs Louisville City FC -> AWAY @ 1.27 (pending_or_unmatched_result); keys=['jax']/['louisvill']
- 2026-10-23 `CAUTION` `pfc_439097cb9bb700e9996c0b07` — Cruzeiro vs Remo -> HOME @ 1.3676 (pending_or_unmatched_result); keys=['cruzeiro', 'mgcruzeir']/['remo']
- 2026-10-23 `CAUTION` `pfc_439097cb9bb700e9996c0b07` — Gateshead vs Tamworth -> AWAY @ 1.6803 (pending_or_unmatched_result); keys=['gateshead']/['tamworth']
- 2026-10-23 `CAUTION` `pfc_439097cb9bb700e9996c0b07` — Independiente del Valle vs Universidad Católica -> HOME @ 1.5882 (pending_or_unmatched_result); keys=['independi']/['universid']
- 2026-10-23 `SKIPPED_VETO` `pfc_439097cb9bb700e9996c0b07` — Holywell vs Penybont -> AWAY @ 1.23 (pending_or_unmatched_result); keys=['holywell']/['penybont']
- 2026-10-23 `SKIPPED_VETO` `pfc_439097cb9bb700e9996c0b07` — Gimnasia La Plata vs Sarmiento -> HOME @ 1.641 (pending_or_unmatched_result); keys=['gimnasial']/['sarmiento']
- 2026-10-23 `SKIPPED_VETO` `pfc_439097cb9bb700e9996c0b07` — Operário PR vs Athletic Club -> HOME @ None (pending_or_unmatched_result); keys=['operariop']/[]

## Ambiguous result examples

- 2026-10-21 `SKIPPED_VETO` `pfc_439097cb9bb700e9996c0b07` — Guadalajara vs Necaxa (ambiguous_alias_result)
- 2026-10-23 `SKIPPED_VETO` `pfc_439097cb9bb700e9996c0b07` — Waterford United vs Drogheda United (ambiguous_alias_result)

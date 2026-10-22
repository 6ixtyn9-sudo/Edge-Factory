# Edge Factory — Recent picks audit (2026-09-23 to 2026-10-22)

## Overall

- archived pick rows: 734
- archived pick dates: 30
- immutable morning-baseline rows: 563
- late-slate additions (regular-ledger rows not in the morning baseline): 173, of which on days whose regular ledger was rewritten: 145
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 26
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 678
- eligible prior picks: 696
- pending/unmatched result picks: 15
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 2
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 25
- ambiguous result picks: 1
- wins: 470
- hit rate: +69.3% (wins/settled: 470/678)
- priced picks: 558
- ROI: +4.1% (P&L / 558 priced picks)

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-22
- same-day rows excluded: 38

Fixture-level secondary rates below score the fixture behind every settled pick; they are not enhancement-bet returns.
## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 406 / 678 matches (59.9%)
- **Both Teams to Score (BTTS)**: occurred in 354 / 678 matches (52.2%)
- **Selected Team Over 1.5 Goals**: occurred in 444 / 674 matches (65.9%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 596
- **Total Hits**: 468
- **Overall Hit Rate**: 78.5%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, settled=18, hit_rate=94.4% (hits=17/recommended=18), priced_n=1, priced_ROI=0.64 (denominator=1), registry_processed=53, class=priced
- `away_under_15`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=5, priced_ROI=2.034 (denominator=5), registry_processed=5, class=priced
- `away_under_25`: recommended=3, settled=3, hit_rate=66.7% (hits=2/recommended=3), priced_n=3, priced_ROI=0.423 (denominator=3), registry_processed=35, class=priced
- `away_under_35`: recommended=173, settled=173, hit_rate=96.5% (hits=167/recommended=173), priced_n=1, priced_ROI=0.435 (denominator=1), registry_processed=305, class=priced
- `btts_no`: recommended=8, settled=8, hit_rate=37.5% (hits=3/recommended=8), priced_n=6, priced_ROI=-0.541667 (denominator=6), registry_processed=8, class=priced
- `btts_yes`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=3, priced_ROI=0.853333 (denominator=3), registry_processed=18, class=priced
- `home_over_05`: recommended=24, settled=24, hit_rate=87.5% (hits=21/recommended=24), priced_n=2, priced_ROI=0.345 (denominator=2), registry_processed=187, class=priced
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=0.381 (denominator=2), registry_processed=2, class=priced
- `home_under_25`: recommended=1, settled=1, hit_rate=0.0% (hits=0/recommended=1), priced_n=1, priced_ROI=-1.0 (denominator=1), registry_processed=41, class=priced
- `home_under_35`: recommended=51, settled=51, hit_rate=98.0% (hits=50/recommended=51), priced_n=0, priced_ROI=None (denominator=0), registry_processed=74, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=25, settled=25, hit_rate=88.0% (hits=22/recommended=25), priced_n=19, priced_ROI=0.094421 (denominator=19), registry_processed=72, class=priced
- `match_over_25`: recommended=260, settled=260, hit_rate=60.4% (hits=157/recommended=260), priced_n=180, priced_ROI=-0.045889 (denominator=180), registry_processed=694, class=priced
- `match_over_35`: recommended=18, settled=18, hit_rate=77.8% (hits=14/recommended=18), priced_n=11, priced_ROI=1.036364 (denominator=11), registry_processed=43, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=4.0 (denominator=2), registry_processed=2, class=priced
- `match_under_45`: recommended=1, settled=1, hit_rate=100.0% (hits=1/recommended=1), priced_n=1, priced_ROI=1.01 (denominator=1), registry_processed=1, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2378** | scored: 2378

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 573 | 573 | 338 | 59.0% | 48.0% | +11.0% | 0.256566 |
| `match_over_45` | 397 | 397 | 87 | 21.9% | 23.9% | -2.0% | 0.172584 |
| `away_under_35` | 345 | 345 | 336 | 97.4% | 96.0% | +1.4% | 0.025458 |
| `away_under_25` | 332 | 332 | 308 | 92.8% | 89.7% | +3.1% | 0.068418 |
| `home_under_35` | 140 | 140 | 135 | 96.4% | 95.6% | +0.8% | 0.035121 |
| `match_over_35` | 123 | 123 | 65 | 52.8% | 43.1% | +9.8% | 0.268462 |
| `home_under_25` | 110 | 110 | 102 | 92.7% | 87.6% | +5.1% | 0.071144 |
| `btts_yes` | 92 | 92 | 55 | 59.8% | 47.1% | +12.7% | 0.248418 |
| `btts_no` | 85 | 85 | 36 | 42.4% | 54.1% | -11.7% | 0.252474 |
| `away_over_05` | 45 | 45 | 39 | 86.7% | 80.0% | +6.6% | 0.114247 |
| `away_under_15` | 41 | 41 | 31 | 75.6% | 80.9% | -5.3% | 0.197056 |
| `home_over_05` | 36 | 36 | 31 | 86.1% | 88.2% | -2.1% | 0.109767 |
| `match_over_15` | 30 | 30 | 24 | 80.0% | 84.3% | -4.3% | 0.160763 |
| `match_under_25` | 10 | 10 | 4 | 40.0% | 39.7% | +0.3% | 0.227268 |
| `home_under_15` | 7 | 7 | 6 | 85.7% | 68.1% | +17.6% | 0.232176 |
| `match_under_35` | 5 | 5 | 2 | 40.0% | 59.0% | -19.0% | 0.248225 |
| `home_over_15` | 4 | 4 | 1 | 25.0% | 58.1% | -33.1% | 0.219844 ⚠️low-n |
| `match_under_45` | 2 | 2 | 2 | 100.0% | 78.4% | +21.6% | 0.046591 ⚠️low-n |
| `away_over_15` | 1 | 1 | 0 | 0.0% | 62.9% | -62.9% | 0.39591 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2282 | 1528 | 67.0% | 63.5% | +3.5% | 0.152534 |
| model | 96 | 74 | 77.1% | 67.3% | +9.8% | 0.182554 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 74 | 19.1% | 24.3% | +5.2% |
| 0.2-0.3 | 292 | 24.2% | 20.5% | -3.6% |
| 0.3-0.4 | 114 | 35.7% | 47.4% | +11.7% |
| 0.4-0.5 | 555 | 44.8% | 57.3% | +12.5% |
| 0.5-0.6 | 181 | 53.9% | 50.3% | -3.7% |
| 0.6-0.7 | 58 | 63.4% | 62.1% | -1.3% |
| 0.7-0.8 | 29 | 73.8% | 72.4% | -1.4% |
| 0.8-0.9 | 436 | 86.8% | 89.7% | +2.9% |
| 0.9-1.0 | 639 | 94.7% | 95.9% | +1.2% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=618, MAE=1.582104 goals, bias=-0.385599 (realized − promised), promised avg 3.574919 vs realized 3.18932

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 618 | 30.7% | 32.5% | +1.9% | 0.190276 |
| BTTS-Yes | 618 | 40.9% | 51.8% | +10.8% | 0.263819 |
| Home Over 1.5 | 618 | 64.6% | 52.9% | -11.7% | 0.234345 |
| Over 2.5 | 618 | 70.0% | 59.5% | -10.4% | 0.249714 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 266 | 8.6% | 22.2% | +13.6% |
| 0.1-0.2 | 352 | 10.5% | 17.3% | +6.8% |
| 0.2-0.3 | 8 | 24.6% | 50.0% | +25.4% |
| 0.3-0.4 | 118 | 37.1% | 49.2% | +12.0% |
| 0.4-0.5 | 488 | 42.0% | 52.5% | +10.5% |
| 0.5-0.6 | 3 | 54.1% | 33.3% | -20.7% |
| 0.6-0.7 | 402 | 67.0% | 55.7% | -11.3% |
| 0.7-0.8 | 195 | 74.6% | 66.2% | -8.5% |
| 0.8-0.9 | 575 | 84.8% | 65.2% | -19.6% |
| 0.9-1.0 | 65 | 92.1% | 75.4% | -16.7% |

## By rule

Counts are frozen PICK ROWS, not bets: rows filed under SKIPPED_VETO / WATCHLIST_* are included and were never cardable. Cardable-only counts are in `## By bucket`.

- `2way-unanimous avg_p>=60`: hit_rate 0.645963 (104/161 settled) · ROI -0.095294 (119 priced)
- `2way-unanimous avg_p>=70`: PROVISIONAL (settled n=24 < 30) — hit_rate 0.791667 (19/24 settled) · ROI 0.037647 (17 priced)
- `ml-meta avg_p>=55`: hit_rate 0.73262 (137/187 settled) · ROI 0.162226 (160 priced)
- `ml-meta avg_p>=60`: hit_rate 0.611842 (93/152 settled) · ROI -0.037924 (136 priced)
- `ml-meta avg_p>=65`: PROVISIONAL (settled n=21 < 30) — hit_rate 0.857143 (18/21 settled) · ROI 0.032667 (15 priced)
- `ml-meta avg_p>=80`: PROVISIONAL (settled n=7 < 30) — hit_rate 1.0 (7/7 settled) · ROI 0.075 (6 priced)
- `pfc_0ad08cd1b2e75a2c9051189e`: 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 [contract · certified, activated 2026-10-20, certified valid n=438] — PROVISIONAL (settled n=3 < 30) — hit_rate 0.666667 (2/3 settled) · ROI 0.38 (3 priced)
- `pfc_0b290b623e2a54ea7df3006c`: 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=201] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI 1.33 (1 priced)
- `pfc_0f100c9da356ed1c05d9c642`: 1x2 single[scoutingstats] avg_p>=60 [contract · benched, activated 2026-10-20, certified valid n=566] — PROVISIONAL (settled n=4 < 30) — hit_rate 0.75 (3/4 settled) · ROI 0.0973 (4 priced)
- `pfc_14ee12458803822df3013bcd`: 1x2 single[zulubet] avg_p>=45 [contract · benched, activated 2026-10-20, certified valid n=1488] — PROVISIONAL (settled n=1 < 30) — hit_rate 0.0 (0/1 settled) · ROI unavailable (0 priced)
- `pfc_234f16641d9893e8ec2a01f0`: 1x2 unanimous[vitibet+zulubet] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=427] — PROVISIONAL (settled n=3 < 30) — hit_rate 0.666667 (2/3 settled) · ROI 0.4 (3 priced)
- `pfc_2bd498a3472b7bbd71982ece`: 1x2 unanimous[vitibet+zulubet] avg_p>=55 [contract · benched, activated 2026-10-20, certified valid n=358] — PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI -1.0 (1 priced)
- `pfc_35f7e50bf23db96c2d3dd59d`: 1x2 single[zulubet] avg_p>=60 [contract · benched, activated 2026-10-20, certified valid n=633] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI unavailable (0 priced)
- `pfc_3bfaf30507905754f7faab2a`: 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 [contract · benched, activated 2026-10-20, certified valid n=645] — PROVISIONAL (settled n=1 < 30) — hit_rate 0.0 (0/1 settled) · ROI -1.0 (1 priced)
- `pfc_439097cb9bb700e9996c0b07`: 1x2 single[scoutingstats] avg_p>=50 [contract · certified, activated 2026-10-20, certified valid n=1235] — PROVISIONAL (settled n=19 < 30) — hit_rate 0.631579 (12/19 settled) · ROI 0.015131 (16 priced)
- `pfc_4a1f2bb2278d13c8189148d0`: 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 [contract · certified, activated 2026-10-20, certified valid n=426] — PROVISIONAL (settled n=2 < 30) — hit_rate 0.5 (1/2 settled) · ROI -0.39 (2 priced)
- `pfc_4cf3df8552488297d7ccf526`: 1x2 single[zulubet] avg_p>=50 [contract · benched, activated 2026-10-20, certified valid n=1241] — PROVISIONAL (settled n=4 < 30) — hit_rate 0.5 (2/4 settled) · ROI 0.9 (2 priced)
- `pfc_5208b9e15194a691590430ad`: 1x2 unanimous[statarea+zulubet] avg_p>=40 [contract · certified, activated 2026-10-20, certified valid n=278] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI 0.44 (1 priced)
- `pfc_5954379f3a12700edcfd8387`: 1x2 single[zulubet] avg_p>=65 [contract · benched, activated 2026-10-20, certified valid n=443] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI unavailable (0 priced)
- `pfc_b011652ec3e473fbc0afbb6a`: 1x2 unanimous[vitibet+zulubet] avg_p>=45 [contract · certified, activated 2026-10-20, certified valid n=488] — PROVISIONAL (settled n=1 < 30) — hit_rate 1.0 (1/1 settled) · ROI 1.6 (1 priced)
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

- `CAUTION`: settled=56, wins=34, hit_rate=0.607143 (settled n=56), ROI=-0.010327 (priced n=56)
- `CERTIFIED_CLEAN`: settled=86, wins=54, hit_rate=0.627907 (settled n=86), ROI=0.005231 (priced n=86)
- `SKIPPED_VETO`: settled=368, wins=268, hit_rate=0.728261 (settled n=368), ROI=0.063304 (priced n=327)
- `WATCHLIST_NO_ODDS`: settled=69, wins=45, hit_rate=0.652174 (settled n=69), ROI=None (priced n=0)
- `WATCHLIST_SUSPECT_PRICE`: settled=20, wins=12, hit_rate=0.6 (settled n=20), ROI=-0.068 (priced n=10)
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=73, wins=51, hit_rate=0.69863 (settled n=73), ROI=0.027534 (priced n=73)
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=6, hit_rate=1.0 (settled n=6), ROI=0.201667 (priced n=6)

## By odds source

- `UNKNOWN`: settled=120, wins=80, hit_rate=0.666667 (settled n=120), ROI=None (priced n=0)
- `betexplorer_odds`: settled=176, wins=133, hit_rate=0.755682 (settled n=176), ROI=0.025568 (priced n=176)
- `boggio`: settled=2, wins=2, hit_rate=1.0 (settled n=2), ROI=0.486 (priced n=2)
- `bzzoiro_odds`: settled=4, wins=4, hit_rate=1.0 (settled n=4), ROI=0.4625 (priced n=4)
- `forebet_best`: settled=39, wins=28, hit_rate=0.717949 (settled n=39), ROI=0.028205 (priced n=39)
- `oddspapi_odds`: settled=9, wins=5, hit_rate=0.555556 (settled n=9), ROI=-0.036111 (priced n=9)
- `pinnapi_odds`: settled=92, wins=55, hit_rate=0.597826 (settled n=92), ROI=0.039934 (priced n=92)
- `scoutingstats_odds`: settled=123, wins=86, hit_rate=0.699187 (settled n=123), ROI=0.017236 (priced n=123)
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0 (settled n=1), ROI=0.741 (priced n=1)
- `theoddsapi`: settled=67, wins=50, hit_rate=0.746269 (settled n=67), ROI=0.150597 (priced n=67)
- `zulubet`: settled=45, wins=26, hit_rate=0.577778 (settled n=45), ROI=-0.035778 (priced n=45)

## By odds match method

- `alias_fuzzy`: settled=37, wins=24, hit_rate=0.648649 (settled n=37), ROI=-0.039167 (priced n=24)
- `betexplorer`: settled=83, wins=59, hit_rate=0.710843 (settled n=83), ROI=-0.013735 (priced n=83)
- `exact`: settled=391, wins=277, hit_rate=0.70844 (settled n=391), ROI=0.06333 (priced n=391)
- `fallback`: settled=60, wins=39, hit_rate=0.65 (settled n=60), ROI=0.007167 (priced n=60)
- `none`: settled=107, wins=71, hit_rate=0.663551 (settled n=107), ROI=None (priced n=0)

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 2 | 2 | 1.0 | 2 | 0.486 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 83 | 59 | 0.710843 | 83 | -0.013735 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 4 | 4 | 1.0 | 4 | 0.4625 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 262 | 185 | 0.706107 | 262 | 0.075648 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 123 | 86 | 0.699187 | 123 | 0.017236 |
| Source fallback (`SOURCE_FALLBACK`) | 60 | 39 | 0.65 | 60 | 0.007167 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 37 | 24 | 0.648649 | 24 | -0.039167 |
| No usable price (`UNMATCHED`) | 107 | 71 | 0.663551 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 368 | 268 | 0.728261 | 327 | 0.063304 |
| **trusted evidence only** | 236 | 176 | 0.745763 | 236 | 0.087501 |
| **soft evidence only** | 132 | 92 | 0.69697 | 91 | 0.000549 |
| evidence: BETEXPLORER_RESCUE | 52 | 38 | 0.730769 | 52 | -0.023462 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.4 |
| evidence: NAMED_BOOKMAKER_PRICE | 181 | 135 | 0.745856 | 181 | 0.114201 |
| evidence: SCOUTINGSTATS_SOLE | 50 | 35 | 0.7 | 50 | 0.0022 |
| evidence: SOURCE_FALLBACK | 27 | 19 | 0.703704 | 27 | 0.007407 |
| evidence: SUSPECT_ALIAS_FUZZY | 17 | 12 | 0.705882 | 14 | -0.018571 |
| evidence: UNMATCHED | 38 | 26 | 0.684211 | 0 | None |
| odds band: <1.50 | 193 | 155 | 0.803109 | 193 | 0.018049 |
| odds band: 1.50-2.00 | 101 | 67 | 0.663366 | 101 | 0.103632 |
| odds band: 2.00-3.00 | 29 | 16 | 0.551724 | 29 | 0.232759 |
| odds band: >=3.00 | 4 | 1 | 0.25 | 4 | 0.0 |
| odds band: unpriced | 41 | 29 | 0.707317 | 0 | None |
| veto reason: context VETO in ['competition_type'] | 46 | 39 | 0.847826 | 36 | 0.1301 |
| veto reason: context VETO in ['league', 'niche'] | 5 | 3 | 0.6 | 4 | -0.32525 |
| veto reason: context VETO in ['league', 'odds_band', 'niche'] | 4 | 0 | 0.0 | 4 | -1.0 |
| veto reason: context VETO in ['league', 'odds_band'] | 6 | 3 | 0.5 | 6 | -0.076417 |
| veto reason: context VETO in ['league', 'team_a'] | 5 | 1 | 0.2 | 5 | -0.668 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.3881 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 6 | 4 | 0.666667 | 5 | 0.186 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.265 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 4 | 3 | 0.75 | 4 | 0.0725 |
| veto reason: context VETO in ['league'] | 30 | 16 | 0.533333 | 23 | -0.281383 |
| veto reason: context VETO in ['niche'] | 12 | 8 | 0.666667 | 12 | -0.073042 |
| veto reason: context VETO in ['odds_band'] | 72 | 50 | 0.694444 | 72 | 0.03919 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 6 | 5 | 0.833333 | 6 | 0.20035 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.212222 |
| veto reason: context VETO in ['team_a'] | 57 | 45 | 0.789474 | 48 | 0.2221 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 13 | 11 | 0.846154 | 12 | 0.082017 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 3 | 1.0 | 3 | 0.446667 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 7 | 5 | 0.714286 | 7 | -0.098571 |
| veto reason: context VETO in ['team_h', 'team_a', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.62 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a'] | 17 | 13 | 0.764706 | 16 | 0.266519 |
| veto reason: context VETO in ['team_h'] | 45 | 33 | 0.733333 | 34 | 0.156176 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.08 | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: short-odds away favourite 1.16 | 2 | 2 | 1.0 | 2 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: APPROVED_DONOR_PRICE | 1 | 1 | 1.0 | 1 | 0.452 |
| contrast CAUTION: BETEXPLORER_RESCUE | 18 | 9 | 0.5 | 18 | -0.2 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 28 | 19 | 0.678571 | 28 | 0.133204 |
| contrast CAUTION: SOURCE_FALLBACK | 9 | 5 | 0.555556 | 9 | -0.128889 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 498 | 348 | 0.698795 | 392 | 0.053984 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 37 | 24 | 0.648649 | 24 | -0.039167 | 37 | 1.627911 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 123 | 86 | 0.699187 | 123 | 0.017236 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 19 | 11 | 0.578947 | 19 | 0.040526 | 0 | None |
| stale_quote (`stale_quote`) | 1 | 1 | 1.0 | 0 | None | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-21: V-Varen Nagasaki vs Sanfrecce Hiroshima (Actual Score: **4-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.4785 -> 🔴 LOST (Expected prob: 62.7%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Jeddah vs Al Jabalain (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.5682 -> 🟢 WON (Expected prob: 56.1%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Real Madrid vs RB Leipzig (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2481 -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 73.6% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 41.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 87.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 90.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Sogndal vs Raufoss (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 64.9%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Reading vs Leyton Orient (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5435 -> 🟢 WON (Expected prob: 60.5%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Fagiano Okayama vs Mito Hollyhock (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7634 -> 🟢 WON (Expected prob: 53.3%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Millonarios vs Once Caldas (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6897 -> 🔴 LOST (Expected prob: 51.8%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 1.5 Goals**: expected 79.8% (Actual: 2 goals)
    - [🟢 HIT] **Match Under 4.5 Goals**: expected 79.3% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected 64.8% (Actual: 1 home goals)
    - [🟢 HIT] **Match Under 3.5 Goals**: expected 62.9% (Actual: 2 goals)
    - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.3% (Actual: 1 home goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected 59.7% (Actual: 1 away goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected 40.9% (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 37.7% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 37.1% (Actual: 2 goals)

### 2026-10-21: Yokohama F. Marinos vs Tokyo Verdy (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.8696 -> 🔴 LOST (Expected prob: 50.8%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Juárez vs Atlante (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.33 -> 🟢 WON (Expected prob: 52.3%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Under 4.5 Goals**: expected 77.5% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 74.2% (Actual: 0 home goals)
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected 64.6% (Actual: 1 away goals)
    - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 62.9% (Actual: 1 away goals)
    - [🟢 HIT] **Match Under 3.5 Goals**: expected 62.9% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 59.6% (Actual: 1 goals)
    - [🔴 MISS] **Home Team Over 0.5 Goals**: expected 57.9% (Actual: 0 home goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected 40.4% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 37.1% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 37.1% (Actual: 1 away goals)
    - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 25.8% (Actual: 0 home goals)

### 2026-10-21: Malacateco vs Comunicaciones (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 2.06 -> 🟢 WON (Expected prob: 50.5%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected 87.9% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 1.5 Goals**: expected 79.6% (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.9% (Actual: 0 away goals)
    - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.6% (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 59.0% (Actual: 1 goals)
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected 58.3% (Actual: 0 away goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected 41.0% (Actual: 1 goals)
    - [🔴 MISS] **Match Over 3.5 Goals**: expected 37.5% (Actual: 1 goals)
    - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 37.4% (Actual: 1 home goals)

### 2026-10-21: FC Tokyo vs Kashiwa Reysol (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 2.16 -> 🔴 LOST (Expected prob: 52.9%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Ceramica Cleopatra vs Petrojet (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 2.1 -> 🟢 WON (Expected prob: 50.6%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Club Brugge vs Lens (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 2.04 -> 🟢 WON (Expected prob: 47.6%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: FC Bayern München vs Arsenal (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 2.13 -> 🔴 LOST (Expected prob: 42.7%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 57.4% (Actual: 4 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 42.6% (Actual: 4 goals)

### 2026-10-21: Real Betis vs Feyenoord (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🟢 WON (Expected prob: 58.6%)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected 56.1% (Actual: 1 goals)
    - [🟢 HIT] **Match Under 2.5 Goals**: expected 43.9% (Actual: 1 goals)

### 2026-10-21: Ventforet Kofu vs Yokohama (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.7246 -> 🟢 WON (Expected prob: 53.2%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Kyoto Sanga vs Kashima Antlers (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.9346 -> 🔴 LOST (Expected prob: 48.2%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Tokushima Vortis vs Vanraure Hachinohe (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.9434 -> 🔴 LOST (Expected prob: 47.8%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Tegevajaro Miyazaki vs Blaublitz Akita (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.9615 -> 🟢 WON (Expected prob: 47.3%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Júbilo Iwata vs Oita Trinita (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 2.03 -> 🔴 LOST (Expected prob: 46.5%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Omiya Ardija vs Kataller Toyama (Actual Score: **0-3**)
- **1X2 Pick**: Selected `HOME` @ 2.13 -> 🔴 LOST (Expected prob: 44.7%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Shonan Bellmare vs Iwaki (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 2.24 -> 🔴 LOST (Expected prob: 43.8%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Montevideo City Torque vs Atlético Mineiro (Actual Score: **2-0**)
- **1X2 Pick**: Selected `AWAY` @ 2.38 -> 🔴 LOST (Expected prob: 42.7%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Como vs Manchester United (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 2.26 -> 🟢 WON (Expected prob: 41.4%)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected 56.1% (Actual: 5 goals)
    - [🔴 MISS] **Match Under 2.5 Goals**: expected 43.9% (Actual: 5 goals)

### 2026-10-21: Kawasaki Frontale vs Vissel Kobe (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 2.36 -> 🟢 WON (Expected prob: 40.9%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Montedio Yamagata vs Consadole Sapporo (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 2.34 -> 🔴 LOST (Expected prob: 40.7%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Vegalta Sendai vs FC Imabari (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 60.5%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Guadalajara W vs Necaxa W (Actual Score: **7-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 82.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Inter vs Shakhtar Donetsk (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 78.3%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Al Ahly vs Olympic El Qanah (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 72.7%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Urawa Reds vs JEF United (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 56.3%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Levante vs Athletic Club (Actual Score: **3-1**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 43.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Kagoshima United vs Kochi United (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 58.6%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Cerro Porteño vs Sportivo Ameliano (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.65 -> 🔴 LOST (Expected prob: 54.4%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Roasso Kumamoto vs Gainare Tottori (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7 -> 🟢 WON (Expected prob: 53.0%)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-21: Aston Villa vs Viking (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 75.2%)
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
- 2026-10-21 `SKIPPED_VETO` `pfc_439097cb9bb700e9996c0b07` — Cincinnati vs DC United -> HOME @ None (pending_or_unmatched_result); keys=['cincinnat']/['dcunited']
- 2026-10-21 `WATCHLIST_UNCORROBORATED_PRICE` `pfc_439097cb9bb700e9996c0b07` — Olimpia vs 2 de Mayo -> HOME @ 1.44 (pending_or_unmatched_result); keys=['olimpia']/['demayo']
- 2026-10-21 `WATCHLIST_UNKNOWN_CTX` `pfc_444d408c4ccd3a4bf4fb020c` — Sporting CP vs LASK Linz -> HOME @ 1.2101 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['lasklinz']

## Ambiguous result examples

- 2026-10-21 `SKIPPED_VETO` `pfc_439097cb9bb700e9996c0b07` — Guadalajara vs Necaxa (ambiguous_alias_result)

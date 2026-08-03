# Edge Factory — Recent picks audit (2026-07-05 to 2026-08-03)

## Overall

- archived pick rows: 90
- archived pick dates: 25
- settled picks: 74
- eligible prior 1x2 picks: 84
- unmatched result picks: 10
- ambiguous result picks: 0
- wins: 58
- hit rate: 0.783784
- priced picks: 72
- ROI: 0.052569

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-08-03
- same-day rows excluded: 6

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 53 / 74 matches (71.6%)
- **Both Teams to Score (BTTS)**: occurred in 40 / 74 matches (54.1%)
- **Selected Team Over 1.5 Goals**: occurred in 58 / 74 matches (78.4%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 15
- **Total Hits**: 11
- **Overall Hit Rate**: 73.3%

### Breakdown by Enhancement Type:
- `away_under_35`: recommended=5, hits=5, hit_rate=100.0%
- `goal_range_2_3`: recommended=1, hits=0, hit_rate=0.0%
- `home_under_45`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_15`: recommended=1, hits=1, hit_rate=100.0%
- `match_over_25`: recommended=7, hits=4, hit_rate=57.1%

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **127** | scored: 127

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `away_under_35` | 14 | 14 | 13 | 92.9% | 95.8% | -2.9% | 0.06418 |
| `goal_range_2_3` | 13 | 13 | 4 | 30.8% | 46.2% | -15.4% | 0.235565 |
| `exact_2` | 12 | 12 | 3 | 25.0% | 24.2% | +0.8% | 0.188516 |
| `away_under_25` | 10 | 10 | 9 | 90.0% | 88.0% | +2.0% | 0.089951 |
| `btts_yes` | 9 | 9 | 4 | 44.4% | 53.3% | -8.8% | 0.23606 |
| `exact_4` | 9 | 9 | 3 | 33.3% | 16.3% | +17.1% | 0.255488 |
| `match_over_25` | 9 | 9 | 5 | 55.6% | 54.9% | +0.6% | 0.308534 |
| `exact_3` | 8 | 8 | 0 | 0.0% | 22.3% | -22.3% | 0.049605 |
| `match_over_35` | 8 | 8 | 5 | 62.5% | 35.4% | +27.1% | 0.350803 |
| `goal_range_4_6` | 7 | 7 | 3 | 42.9% | 32.1% | +10.8% | 0.272209 |
| `home_over_05` | 7 | 7 | 7 | 100.0% | 83.6% | +16.4% | 0.028111 |
| `home_under_35` | 5 | 5 | 3 | 60.0% | 93.7% | -33.7% | 0.350216 |
| `goal_range_4_5` | 3 | 3 | 2 | 66.7% | 29.7% | +37.0% | 0.399278 ⚠️low-n |
| `btts_no` | 2 | 2 | 1 | 50.0% | 53.5% | -3.5% | 0.275611 ⚠️low-n |
| `exact_5` | 2 | 2 | 1 | 50.0% | 13.2% | +36.8% | 0.41284 ⚠️low-n |
| `home_under_25` | 2 | 2 | 1 | 50.0% | 87.3% | -37.3% | 0.409172 ⚠️low-n |
| `match_over_15` | 2 | 2 | 2 | 100.0% | 87.3% | +12.7% | 0.019317 ⚠️low-n |
| `match_over_45` | 2 | 2 | 1 | 50.0% | 29.1% | +20.9% | 0.39756 ⚠️low-n |
| `away_over_05` | 1 | 1 | 1 | 100.0% | 82.6% | +17.4% | 0.030429 ⚠️low-n |
| `goal_range_6_plus` | 1 | 1 | 0 | 0.0% | 22.7% | -22.7% | 0.051598 ⚠️low-n |
| `goal_range_7_plus` | 1 | 1 | 0 | 0.0% | 11.9% | -11.9% | 0.014147 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored (FIX-2 + label honesty, Addendum 16): `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 13 | 15.7% | 38.5% | +22.8% |
| 0.2-0.3 | 27 | 24.4% | 22.2% | -2.2% |
| 0.3-0.4 | 11 | 33.0% | 63.6% | +30.6% |
| 0.4-0.5 | 18 | 46.1% | 38.9% | -7.2% |
| 0.5-0.6 | 15 | 53.7% | 40.0% | -13.7% |
| 0.7-0.8 | 2 | 74.7% | 50.0% | -24.7% |
| 0.8-0.9 | 18 | 85.0% | 88.9% | +3.9% |
| 0.9-1.0 | 23 | 94.7% | 87.0% | -7.7% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5 / exact Top Score) — calibration, not a direction call).

- **Avg Goals forecast**: n=15, MAE=0.982667 goals, bias=-0.076 (realized − promised), promised avg 3.742667 vs realized 3.666667

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Top Scores (exact) | 30 | 14.4% | 10.0% | -4.4% | 0.095394 |
| Away Over 1.5 | 15 | 24.6% | 13.3% | -11.2% | 0.060309 |
| BTTS-Yes | 15 | 39.4% | 40.0% | +0.6% | 0.243162 |
| Home Over 1.5 | 15 | 72.2% | 80.0% | +7.8% | 0.11855 |
| Over 2.5 | 15 | 72.5% | 73.3% | +0.9% | 0.196848 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 11 | 8.9% | 9.1% | +0.2% |
| 0.1-0.2 | 33 | 13.7% | 9.1% | -4.6% |
| 0.2-0.3 | 1 | 20.3% | 0.0% | -20.3% |
| 0.3-0.4 | 9 | 37.7% | 44.4% | +6.8% |
| 0.4-0.5 | 6 | 42.0% | 33.3% | -8.6% |
| 0.6-0.7 | 4 | 66.8% | 75.0% | +8.2% |
| 0.7-0.8 | 11 | 74.6% | 72.7% | -1.8% |
| 0.8-0.9 | 12 | 86.7% | 83.3% | -3.4% |
| 0.9-1.0 | 3 | 90.6% | 100.0% | +9.4% |

## By rule

- `2way-unanimous avg_p>=70`: settled=30, wins=23, hit_rate=0.766667, ROI=0.1225
- `3way-unanimous avg_p>=65`: settled=20, wins=14, hit_rate=0.7, ROI=-0.10725
- `3way-unanimous home-only avg_p>=60`: settled=9, wins=8, hit_rate=0.888889, ROI=0.176667
- `3way-unanimous home-only avg_p>=65`: settled=15, wins=13, hit_rate=0.866667, ROI=0.060667

## By bucket

- `CAUTION`: settled=16, wins=10, hit_rate=0.625, ROI=0.054375
- `SKIPPED_VETO`: settled=45, wins=38, hit_rate=0.844444, ROI=0.076778
- `WATCHLIST_NO_ODDS`: settled=2, wins=1, hit_rate=0.5, ROI=None
- `WATCHLIST_UNKNOWN_CTX`: settled=11, wins=9, hit_rate=0.818182, ROI=-0.049091

## By odds source

- `UNKNOWN`: settled=2, wins=1, hit_rate=0.5, ROI=None
- `betexplorer_odds`: settled=40, wins=34, hit_rate=0.85, ROI=0.09725
- `bzzoiro_odds`: settled=19, wins=17, hit_rate=0.894737, ROI=0.262368
- `forebet_best`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
- `scoutingstats_odds`: settled=10, wins=5, hit_rate=0.5, ROI=-0.331
- `zulubet`: settled=1, wins=0, hit_rate=0.0, ROI=-1.0

## By odds match method

- `alias_fuzzy`: settled=3, wins=2, hit_rate=0.666667, ROI=-0.183333
- `betexplorer`: settled=40, wins=34, hit_rate=0.85, ROI=0.09725
- `exact`: settled=26, wins=20, hit_rate=0.769231, ROI=0.085577
- `fallback`: settled=3, wins=1, hit_rate=0.333333, ROI=-0.593333
- `none`: settled=2, wins=1, hit_rate=0.5, ROI=None
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:


## Unmatched result examples

- 2026-07-11 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — South Hobart vs Ulverstone -> HOME @ 1.02 (unmatched_result); keys=['southhoba']/['ulverston']
- 2026-08-02 `CAUTION` `2way-unanimous avg_p>=70` — AIK Stockholm vs Orgryte IS -> HOME @ 1.52 (unmatched_result); keys=['aikstockh']/['orgryteis']
- 2026-08-02 `CAUTION` `2way-unanimous avg_p>=70` — Dinamo Brest vs Belshina -> HOME @ 1.32 (unmatched_result); keys=['dinamobre']/['belshina', 'belshinab']
- 2026-08-02 `CAUTION` `2way-unanimous avg_p>=70` — Kongsvinger vs Strommen -> HOME @ 1.33 (unmatched_result); keys=['kongsving']/['strommen']
- 2026-08-02 `CAUTION` `3way-unanimous avg_p>=65` — Noah vs Syunik -> HOME @ 1.31 (unmatched_result); keys=['noah']/['syunik']
- 2026-08-02 `SKIPPED_VETO` `2way-unanimous avg_p>=70` — Independiente del Valle vs Deportivo Cuenca -> HOME @ 1.33 (unmatched_result); keys=['independi']/['cuenca']
- 2026-08-02 `SKIPPED_VETO` `3way-unanimous avg_p>=65` — Ludogorets vs Botev Vratsa -> HOME @ 1.4 (unmatched_result); keys=['ludogoret']/['botevvrat']
- 2026-08-02 `SKIPPED_VETO` `3way-unanimous avg_p>=65` — ODD Ballklubb vs Asane -> HOME @ 1.4 (unmatched_result); keys=['oddballkl']/['asane']
- 2026-08-02 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Dunajska Streda vs Dukla Banska Bystrica -> HOME @ None (unmatched_result); keys=['dunajskas']/['duklabans']
- 2026-08-02 `WATCHLIST_UNKNOWN_CTX` `2way-unanimous avg_p>=70` — Clarence Zebras vs Ulverstone -> HOME @ 1.23 (unmatched_result); keys=['clarencez']/['ulverston']

## Ambiguous result examples

- none

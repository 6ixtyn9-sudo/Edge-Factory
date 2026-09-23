# ML-Fade Research Checkpoint — 2026-09-23

**RESEARCH-ONLY — definitions FROZEN at 2026-09-20 and never change. This report cannot certify, promote, or alter any operational pick, ticket, gate, or registry entry.**

Checkpoint due because: settled fade rows grew by 82 (>= 50).

## Accrual (cumulative, plus new since last checkpoint)

| family | rows | settled | pending | conflict | unmatched | new |
|---|---|---|---|---|---|---|
| ml-meta | 173 | 121 | 52 | 0 | 0 | +119 |
| ml-fade | 132 | 87 | 45 | 0 | 0 | +92 |

## Fixed price variants (first-seen bet-time quotes)

### ml-meta

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 121 | 41 | 33.9% | 26.1% | 14 | -3.6% |
| fb-only | 121 | 41 | 33.9% | 26.1% | 90 | -17.5% |

### ml-fade

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 87 | 21 | 24.1% | 16.4% | 12 | 21.6% |
| fb-only | 87 | 21 | 24.1% | 16.4% | 61 | -17.9% |

## Reference accumulators (frozen grids — research contexts)

| family | grid | variant | rows | settled | priced | hit | ROI | Wilson LB |
|---|---|---|---|---|---|---|---|---|
| ml-meta | avg_p>=55 | zb-only | 14 | 10 | 1 | 40.0% | -100.0% | 16.8% |
| ml-meta | avg_p>=55 | fb-only | 14 | 10 | 7 | 40.0% | -66.9% | 16.8% |
| ml-meta | avg_p>=60 | zb-only | 7 | 7 | 1 | 42.9% | -100.0% | 15.8% |
| ml-meta | avg_p>=60 | fb-only | 7 | 7 | 4 | 42.9% | -71.5% | 15.8% |
| ml-meta | avg_p>=65 | zb-only | 4 | 4 | 1 | 25.0% | -100.0% | 4.6% |
| ml-meta | avg_p>=65 | fb-only | 4 | 4 | 2 | 25.0% | -100.0% | 4.6% |
| ml-meta | avg_p>=70 | zb-only | 2 | 2 | 1 | 50.0% | -100.0% | 9.5% |
| ml-meta | avg_p>=70 | fb-only | 2 | 2 | 0 | 50.0% | — | 9.5% |
| ml-fade | parent avg_p>=55 | zb-only | 16 | 10 | 1 | 10.0% | -100.0% | 1.8% |
| ml-fade | parent avg_p>=55 | fb-only | 16 | 10 | 7 | 10.0% | 21.4% | 1.8% |
| ml-fade | parent avg_p>=60 | zb-only | 8 | 7 | 1 | 14.3% | -100.0% | 2.6% |
| ml-fade | parent avg_p>=60 | fb-only | 8 | 7 | 4 | 14.3% | 112.5% | 2.6% |
| ml-fade | parent avg_p>=65 | zb-only | 4 | 4 | 1 | 25.0% | -100.0% | 4.6% |
| ml-fade | parent avg_p>=65 | fb-only | 4 | 4 | 2 | 25.0% | 325.0% | 4.6% |
| ml-fade | parent avg_p>=70 | zb-only | 2 | 2 | 1 | 0.0% | -100.0% | 0.0% |
| ml-fade | parent avg_p>=70 | fb-only | 2 | 2 | 0 | 0.0% | — | 0.0% |

## Automatic rule-candidate signal (research heuristic — NOT certification)

**Status: OBSERVING**

- unmet gate: settled fade rows 87 < 200
- unmet gate: zb-only n_priced 12 < 150
- unmet gate: zb-only wilson_lb 0.1636 < 0.55
- unmet gate: fb-only n_priced 61 < 150
- unmet gate: fb-only wilson_lb 0.1636 < 0.55
- unmet gate: fb-only roi -0.1792 <= 0.0

> automatic research heuristic only — certification remains the existing walk-forward machinery, untouched.

## Warnings

- 🚨 FADE PRICE COVERAGE LOW (zb-only): 14% of settled fade rows carry a first-seen zb-only quote (< 90% threshold)
- 🚨 FADE PRICE COVERAGE LOW (fb-only): 70% of settled fade rows carry a first-seen fb-only quote (< 90% threshold)

## Frozen full-population studies

The frozen, unmodified research scripts were re-run at this checkpoint; outputs archived:
- `contexts` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_contexts_2026-09-23.txt`
- `price_study` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_price_study_2026-09-23.txt`

## Provenance

- serving model key: `a584ef59212a`
- frozen serving method drifted: **False**
- stale model keys present in ledger: ['029a51a6c9a2', '20b346abc92f', '4c87eebc1768', '563da1602950', '5995600039ad', '5fcf03a68b29', '633faa446086', '643e3c399c35', '749fc72ea111', '75384507e4ef', '78d95eb0a42d', '960856b6997f', '964834d0144a', 'aab5095b04eb', 'b15203feada1', 'bcddb8d1a667', 'bfa38ffed58d', 'c79f1af99a3e', 'd5a82837085c', 'd6b2476de931', 'f399fe11bec0']
- ledger: `localdata/ml_fade_research_ledger.json` (tracked; bot commits each run)
- state: `localdata/ml_fade_research_state.json` (tracked; checkpoint history)
- policy: `ML_FADE_RESEARCH_POLICY.md`

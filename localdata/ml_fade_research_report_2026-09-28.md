# ML-Fade Research Checkpoint — 2026-09-28

**RESEARCH-ONLY — definitions FROZEN at 2026-09-20 and never change. This report cannot certify, promote, or alter any operational pick, ticket, gate, or registry entry.**

Checkpoint due because: settled fade rows grew by 111 (>= 50).

## Accrual (cumulative, plus new since last checkpoint)

| family | rows | settled | pending | conflict | unmatched | new |
|---|---|---|---|---|---|---|
| ml-meta | 803 | 707 | 95 | 1 | 0 | +110 |
| ml-fade | 654 | 569 | 84 | 1 | 0 | +96 |

## Fixed price variants (first-seen bet-time quotes)

### ml-meta

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 707 | 319 | 45.1% | 41.5% | 45 | -7.7% |
| fb-only | 707 | 319 | 45.1% | 41.5% | 478 | -6.8% |

### ml-fade

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 569 | 135 | 23.7% | 20.4% | 42 | -29.2% |
| fb-only | 569 | 135 | 23.7% | 20.4% | 336 | -28.1% |

## Reference accumulators (frozen grids — research contexts)

| family | grid | variant | rows | settled | priced | hit | ROI | Wilson LB |
|---|---|---|---|---|---|---|---|---|
| ml-meta | avg_p>=55 | zb-only | 49 | 41 | 1 | 68.3% | -100.0% | 53.0% |
| ml-meta | avg_p>=55 | fb-only | 49 | 41 | 27 | 68.3% | -20.4% | 53.0% |
| ml-meta | avg_p>=60 | zb-only | 28 | 22 | 1 | 68.2% | -100.0% | 47.3% |
| ml-meta | avg_p>=60 | fb-only | 28 | 22 | 13 | 68.2% | -26.1% | 47.3% |
| ml-meta | avg_p>=65 | zb-only | 17 | 12 | 1 | 75.0% | -100.0% | 46.8% |
| ml-meta | avg_p>=65 | fb-only | 17 | 12 | 8 | 75.0% | -13.2% | 46.8% |
| ml-meta | avg_p>=70 | zb-only | 10 | 6 | 1 | 83.3% | -100.0% | 43.6% |
| ml-meta | avg_p>=70 | fb-only | 10 | 6 | 4 | 83.3% | 8.5% | 43.6% |
| ml-fade | parent avg_p>=55 | zb-only | 54 | 46 | 1 | 8.7% | -100.0% | 3.4% |
| ml-fade | parent avg_p>=55 | fb-only | 54 | 46 | 27 | 8.7% | -5.2% | 3.4% |
| ml-fade | parent avg_p>=60 | zb-only | 31 | 25 | 1 | 8.0% | -100.0% | 2.2% |
| ml-fade | parent avg_p>=60 | fb-only | 31 | 25 | 13 | 8.0% | 23.1% | 2.2% |
| ml-fade | parent avg_p>=65 | zb-only | 17 | 12 | 1 | 8.3% | -100.0% | 1.5% |
| ml-fade | parent avg_p>=65 | fb-only | 17 | 12 | 8 | 8.3% | 6.2% | 1.5% |
| ml-fade | parent avg_p>=70 | zb-only | 10 | 6 | 1 | 0.0% | -100.0% | 0.0% |
| ml-fade | parent avg_p>=70 | fb-only | 10 | 6 | 4 | 0.0% | -100.0% | 0.0% |

## Automatic rule-candidate signal (research heuristic — NOT certification)

**Status: OBSERVING**

- unmet gate: zb-only n_priced 42 < 150
- unmet gate: zb-only wilson_lb 0.2041 < 0.55
- unmet gate: zb-only roi -0.2921 <= 0.0
- unmet gate: fb-only wilson_lb 0.2041 < 0.55
- unmet gate: fb-only roi -0.2807 <= 0.0
- unmet gate: 1 unresolved conflict row(s) in fade family

> automatic research heuristic only — certification remains the existing walk-forward machinery, untouched.

## Warnings

- 🚨 FADE PRICE COVERAGE LOW (zb-only): 7% of settled fade rows carry a first-seen zb-only quote (< 90% threshold)
- 🚨 FADE PRICE COVERAGE LOW (fb-only): 59% of settled fade rows carry a first-seen fb-only quote (< 90% threshold)
- 🚨 UNRESOLVED CONFLICTS (ml-meta): 1 row(s) hold contradictory result claims — human review required, never auto-resolved
- 🚨 UNRESOLVED CONFLICTS (ml-fade): 1 row(s) hold contradictory result claims — human review required, never auto-resolved

## Frozen full-population studies

The frozen, unmodified research scripts were re-run at this checkpoint; outputs archived:
- `contexts` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_contexts_2026-09-28.txt`
- `price_study` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_price_study_2026-09-28.txt`

## Provenance

- serving model key: `6c20c7fcd357`
- frozen serving method drifted: **False**
- stale model keys present in ledger: ['00676495f942', '01f98ed9936b', '029a51a6c9a2', '0485aef21613', '06b6903f96dc', '0ab793d02c02', '11d2a701a456', '14c59a6211ef', '20b346abc92f', '24ae7edfc7e7', '289e086d84db', '323c100d7524', '35b61895a181', '40e00cc32eba', '41972eca6848', '41f0e1e5dec5', '42516a50a15b', '46280f3b01bf', '4c87eebc1768', '4f6460868f97', '533a9a4932b6', '563da1602950', '5995600039ad', '5fcf03a68b29', '604a0ae8437c', '633faa446086', '643e3c399c35', '6adbf860bf0e', '706aa1c05083', '711ff65e0e5e', '71800f16e755', '749fc72ea111', '75384507e4ef', '7672bc23a439', '78d95eb0a42d', '7b717377ba79', '7b7a7d43aa97', '817a56b94bbd', '960856b6997f', '964834d0144a', '99ecaeba1b8f', '9bf3a04f1fc7', 'a2c8a5099e3f', 'a584ef59212a', 'a6c7db2fcf23', 'aab5095b04eb', 'b09668105711', 'b15203feada1', 'ba2499eccbd3', 'bcddb8d1a667', 'bd2eb96cafec', 'bfa38ffed58d', 'c79f1af99a3e', 'd1a3a03ba50f', 'd2a004e29202', 'd59968d42bf4', 'd5a82837085c', 'd6b2476de931', 'e08a036da4c6', 'f399fe11bec0']
- ledger: `localdata/ml_fade_research_ledger.json` (tracked; bot commits each run)
- state: `localdata/ml_fade_research_state.json` (tracked; checkpoint history)
- policy: HANDOVER.md, 'ML-FADE RESEARCH GUARDRAIL' (frozen 2026-09-20)

# ML-Fade Research Checkpoint — 2026-09-26

**RESEARCH-ONLY — definitions FROZEN at 2026-09-20 and never change. This report cannot certify, promote, or alter any operational pick, ticket, gate, or registry entry.**

Checkpoint due because: settled fade rows grew by 64 (>= 50).

## Accrual (cumulative, plus new since last checkpoint)

| family | rows | settled | pending | conflict | unmatched | new |
|---|---|---|---|---|---|---|
| ml-meta | 692 | 272 | 419 | 1 | 0 | +433 |
| ml-fade | 547 | 214 | 332 | 1 | 0 | +349 |

## Fixed price variants (first-seen bet-time quotes)

### ml-meta

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 272 | 117 | 43.0% | 37.3% | 37 | -7.5% |
| fb-only | 272 | 117 | 43.0% | 37.3% | 193 | -9.8% |

### ml-fade

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 214 | 45 | 21.0% | 16.1% | 37 | -19.6% |
| fb-only | 214 | 45 | 21.0% | 16.1% | 136 | -35.5% |

## Reference accumulators (frozen grids — research contexts)

| family | grid | variant | rows | settled | priced | hit | ROI | Wilson LB |
|---|---|---|---|---|---|---|---|---|
| ml-meta | avg_p>=55 | zb-only | 41 | 18 | 1 | 55.6% | -100.0% | 33.7% |
| ml-meta | avg_p>=55 | fb-only | 41 | 18 | 12 | 55.6% | -34.5% | 33.7% |
| ml-meta | avg_p>=60 | zb-only | 22 | 9 | 1 | 44.4% | -100.0% | 18.9% |
| ml-meta | avg_p>=60 | fb-only | 22 | 9 | 4 | 44.4% | -71.5% | 18.9% |
| ml-meta | avg_p>=65 | zb-only | 12 | 4 | 1 | 25.0% | -100.0% | 4.6% |
| ml-meta | avg_p>=65 | fb-only | 12 | 4 | 2 | 25.0% | -100.0% | 4.6% |
| ml-meta | avg_p>=70 | zb-only | 6 | 2 | 1 | 50.0% | -100.0% | 9.5% |
| ml-meta | avg_p>=70 | fb-only | 6 | 2 | 0 | 50.0% | — | 9.5% |
| ml-fade | parent avg_p>=55 | zb-only | 43 | 20 | 1 | 5.0% | -100.0% | 0.9% |
| ml-fade | parent avg_p>=55 | fb-only | 43 | 20 | 12 | 5.0% | -29.2% | 0.9% |
| ml-fade | parent avg_p>=60 | zb-only | 23 | 10 | 1 | 10.0% | -100.0% | 1.8% |
| ml-fade | parent avg_p>=60 | fb-only | 23 | 10 | 4 | 10.0% | 112.5% | 1.8% |
| ml-fade | parent avg_p>=65 | zb-only | 12 | 4 | 1 | 25.0% | -100.0% | 4.6% |
| ml-fade | parent avg_p>=65 | fb-only | 12 | 4 | 2 | 25.0% | 325.0% | 4.6% |
| ml-fade | parent avg_p>=70 | zb-only | 6 | 2 | 1 | 0.0% | -100.0% | 0.0% |
| ml-fade | parent avg_p>=70 | fb-only | 6 | 2 | 0 | 0.0% | — | 0.0% |

## Automatic rule-candidate signal (research heuristic — NOT certification)

**Status: OBSERVING**

- unmet gate: zb-only n_priced 37 < 150
- unmet gate: zb-only wilson_lb 0.161 < 0.55
- unmet gate: zb-only roi -0.1965 <= 0.0
- unmet gate: fb-only n_priced 136 < 150
- unmet gate: fb-only wilson_lb 0.161 < 0.55
- unmet gate: fb-only roi -0.3554 <= 0.0
- unmet gate: 1 unresolved conflict row(s) in fade family

> automatic research heuristic only — certification remains the existing walk-forward machinery, untouched.

## Warnings

- 🚨 FADE PRICE COVERAGE LOW (zb-only): 17% of settled fade rows carry a first-seen zb-only quote (< 90% threshold)
- 🚨 FADE PRICE COVERAGE LOW (fb-only): 64% of settled fade rows carry a first-seen fb-only quote (< 90% threshold)
- 🚨 UNRESOLVED CONFLICTS (ml-meta): 1 row(s) hold contradictory result claims — human review required, never auto-resolved
- 🚨 UNRESOLVED CONFLICTS (ml-fade): 1 row(s) hold contradictory result claims — human review required, never auto-resolved

## Frozen full-population studies

The frozen, unmodified research scripts were re-run at this checkpoint; outputs archived:
- `contexts` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_contexts_2026-09-26.txt`
- `price_study` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_price_study_2026-09-26.txt`

## Provenance

- serving model key: `41972eca6848`
- frozen serving method drifted: **False**
- stale model keys present in ledger: ['029a51a6c9a2', '0485aef21613', '0ab793d02c02', '11d2a701a456', '14c59a6211ef', '20b346abc92f', '24ae7edfc7e7', '323c100d7524', '35b61895a181', '41f0e1e5dec5', '42516a50a15b', '46280f3b01bf', '4c87eebc1768', '4f6460868f97', '533a9a4932b6', '563da1602950', '5995600039ad', '5fcf03a68b29', '604a0ae8437c', '633faa446086', '643e3c399c35', '706aa1c05083', '711ff65e0e5e', '71800f16e755', '749fc72ea111', '75384507e4ef', '7672bc23a439', '78d95eb0a42d', '7b717377ba79', '7b7a7d43aa97', '817a56b94bbd', '960856b6997f', '964834d0144a', '99ecaeba1b8f', '9bf3a04f1fc7', 'a2c8a5099e3f', 'a584ef59212a', 'a6c7db2fcf23', 'aab5095b04eb', 'b09668105711', 'b15203feada1', 'bcddb8d1a667', 'bfa38ffed58d', 'c79f1af99a3e', 'd1a3a03ba50f', 'd2a004e29202', 'd59968d42bf4', 'd5a82837085c', 'd6b2476de931', 'f399fe11bec0']
- ledger: `localdata/ml_fade_research_ledger.json` (tracked; bot commits each run)
- state: `localdata/ml_fade_research_state.json` (tracked; checkpoint history)
- policy: HANDOVER.md, 'ML-FADE RESEARCH GUARDRAIL' (frozen 2026-09-20)

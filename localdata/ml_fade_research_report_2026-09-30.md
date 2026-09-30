# ML-Fade Research Checkpoint — 2026-09-30

**RESEARCH-ONLY — definitions FROZEN at 2026-09-20 and never change. This report cannot certify, promote, or alter any operational pick, ticket, gate, or registry entry.**

Checkpoint due because: settled fade rows grew by 73 (>= 50).

## Accrual (cumulative, plus new since last checkpoint)

| family | rows | settled | pending | conflict | unmatched | new |
|---|---|---|---|---|---|---|
| ml-meta | 851 | 792 | 58 | 1 | 0 | +85 |
| ml-fade | 695 | 642 | 52 | 1 | 0 | +74 |

## Fixed price variants (first-seen bet-time quotes)

### ml-meta

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 792 | 365 | 46.1% | 42.6% | 55 | -6.6% |
| fb-only | 792 | 365 | 46.1% | 42.6% | 526 | -8.8% |

### ml-fade

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 642 | 148 | 23.1% | 20.0% | 51 | -38.5% |
| fb-only | 642 | 148 | 23.1% | 20.0% | 371 | -27.5% |

## Reference accumulators (frozen grids — research contexts)

| family | grid | variant | rows | settled | priced | hit | ROI | Wilson LB |
|---|---|---|---|---|---|---|---|---|
| ml-meta | avg_p>=55 | zb-only | 57 | 51 | 2 | 74.5% | -47.5% | 61.1% |
| ml-meta | avg_p>=55 | fb-only | 57 | 51 | 29 | 74.5% | -17.5% | 61.1% |
| ml-meta | avg_p>=60 | zb-only | 34 | 30 | 2 | 76.7% | -47.5% | 59.1% |
| ml-meta | avg_p>=60 | fb-only | 34 | 30 | 14 | 76.7% | -22.6% | 59.1% |
| ml-meta | avg_p>=65 | zb-only | 20 | 18 | 2 | 83.3% | -47.5% | 60.8% |
| ml-meta | avg_p>=65 | fb-only | 20 | 18 | 9 | 83.3% | -9.3% | 60.8% |
| ml-meta | avg_p>=70 | zb-only | 11 | 10 | 1 | 90.0% | -100.0% | 59.6% |
| ml-meta | avg_p>=70 | fb-only | 11 | 10 | 5 | 90.0% | 11.2% | 59.6% |
| ml-fade | parent avg_p>=55 | zb-only | 62 | 56 | 2 | 7.1% | -100.0% | 2.8% |
| ml-fade | parent avg_p>=55 | fb-only | 62 | 56 | 29 | 7.1% | -11.7% | 2.8% |
| ml-fade | parent avg_p>=60 | zb-only | 37 | 33 | 2 | 6.1% | -100.0% | 1.7% |
| ml-fade | parent avg_p>=60 | fb-only | 37 | 33 | 14 | 6.1% | 14.3% | 1.7% |
| ml-fade | parent avg_p>=65 | zb-only | 20 | 18 | 2 | 5.6% | -100.0% | 1.0% |
| ml-fade | parent avg_p>=65 | fb-only | 20 | 18 | 9 | 5.6% | -5.6% | 1.0% |
| ml-fade | parent avg_p>=70 | zb-only | 11 | 10 | 1 | 0.0% | -100.0% | -0.0% |
| ml-fade | parent avg_p>=70 | fb-only | 11 | 10 | 5 | 0.0% | -100.0% | -0.0% |

## Automatic rule-candidate signal (research heuristic — NOT certification)

**Status: OBSERVING**

- unmet gate: zb-only n_priced 51 < 150
- unmet gate: zb-only wilson_lb 0.1996 < 0.55
- unmet gate: zb-only roi -0.3853 <= 0.0
- unmet gate: fb-only wilson_lb 0.1996 < 0.55
- unmet gate: fb-only roi -0.2747 <= 0.0
- unmet gate: 1 unresolved conflict row(s) in fade family

> automatic research heuristic only — certification remains the existing walk-forward machinery, untouched.

## Warnings

- 🚨 FADE PRICE COVERAGE LOW (zb-only): 8% of settled fade rows carry a first-seen zb-only quote (< 90% threshold)
- 🚨 FADE PRICE COVERAGE LOW (fb-only): 58% of settled fade rows carry a first-seen fb-only quote (< 90% threshold)
- 🚨 UNRESOLVED CONFLICTS (ml-meta): 1 row(s) hold contradictory result claims — human review required, never auto-resolved
- 🚨 UNRESOLVED CONFLICTS (ml-fade): 1 row(s) hold contradictory result claims — human review required, never auto-resolved

## Frozen full-population studies

The frozen, unmodified research scripts were re-run at this checkpoint; outputs archived:
- `contexts` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_contexts_2026-09-30.txt`
- `price_study` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_price_study_2026-09-30.txt`

## Provenance

- serving model key: `6a8cf5e0f006`
- frozen serving method drifted: **False**
- stale model keys present in ledger: ['00676495f942', '01f98ed9936b', '029a51a6c9a2', '0485aef21613', '06b6903f96dc', '09b94efe5419', '0ab793d02c02', '0e5362528d7b', '1013c0e4e535', '11d2a701a456', '14c59a6211ef', '20b346abc92f', '24ae7edfc7e7', '27f1e9ebab85', '289e086d84db', '29f20ae26d96', '323c100d7524', '35b61895a181', '363e7bfaa219', '40e00cc32eba', '41972eca6848', '41f0e1e5dec5', '42516a50a15b', '46280f3b01bf', '4c87eebc1768', '4f6460868f97', '533a9a4932b6', '563da1602950', '5995600039ad', '5ac0bb041e10', '5fcf03a68b29', '604a0ae8437c', '633faa446086', '643e3c399c35', '6adbf860bf0e', '6c20c7fcd357', '706aa1c05083', '711ff65e0e5e', '71800f16e755', '749fc72ea111', '75384507e4ef', '7672bc23a439', '78d95eb0a42d', '7b717377ba79', '7b7a7d43aa97', '7c9f64dcebd4', '817a56b94bbd', '921a1b4ae272', '960856b6997f', '964834d0144a', '966cc28a600a', '99ecaeba1b8f', '9bf3a04f1fc7', 'a03d6bad2781', 'a2c8a5099e3f', 'a584ef59212a', 'a6c7db2fcf23', 'aab5095b04eb', 'ad967c7878dd', 'b09668105711', 'b15203feada1', 'ba2499eccbd3', 'bcddb8d1a667', 'bd2eb96cafec', 'bfa38ffed58d', 'c614bd726cdd', 'c78eabfffe02', 'c79f1af99a3e', 'c822740cdb3f', 'd1a3a03ba50f', 'd2a004e29202', 'd59968d42bf4', 'd5a82837085c', 'd6b2476de931', 'e08a036da4c6', 'e62f7c6399fa', 'f399fe11bec0']
- ledger: `localdata/ml_fade_research_ledger.json` (tracked; bot commits each run)
- state: `localdata/ml_fade_research_state.json` (tracked; checkpoint history)
- policy: HANDOVER.md, 'ML-FADE RESEARCH GUARDRAIL' (frozen 2026-09-20)

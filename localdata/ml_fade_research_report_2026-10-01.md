# ML-Fade Research Checkpoint — 2026-10-01

**RESEARCH-ONLY — definitions FROZEN at 2026-09-20 and never change. This report cannot certify, promote, or alter any operational pick, ticket, gate, or registry entry.**

Checkpoint due because: monthly checkpoint (last 2026-09, now 2026-10).

## Accrual (cumulative, plus new since last checkpoint)

| family | rows | settled | pending | conflict | unmatched | new |
|---|---|---|---|---|---|---|
| ml-meta | 859 | 805 | 53 | 1 | 0 | +24 |
| ml-fade | 703 | 655 | 47 | 1 | 0 | +24 |

## Fixed price variants (first-seen bet-time quotes)

### ml-meta

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 805 | 374 | 46.5% | 43.0% | 59 | -3.6% |
| fb-only | 805 | 374 | 46.5% | 43.0% | 526 | -8.8% |

### ml-fade

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 655 | 149 | 22.7% | 19.7% | 55 | -43.0% |
| fb-only | 655 | 149 | 22.7% | 19.7% | 371 | -27.5% |

## Reference accumulators (frozen grids — research contexts)

| family | grid | variant | rows | settled | priced | hit | ROI | Wilson LB |
|---|---|---|---|---|---|---|---|---|
| ml-meta | avg_p>=55 | zb-only | 58 | 53 | 2 | 73.6% | -47.5% | 60.4% |
| ml-meta | avg_p>=55 | fb-only | 58 | 53 | 29 | 73.6% | -17.5% | 60.4% |
| ml-meta | avg_p>=60 | zb-only | 35 | 31 | 2 | 77.4% | -47.5% | 60.2% |
| ml-meta | avg_p>=60 | fb-only | 35 | 31 | 14 | 77.4% | -22.6% | 60.2% |
| ml-meta | avg_p>=65 | zb-only | 21 | 18 | 2 | 83.3% | -47.5% | 60.8% |
| ml-meta | avg_p>=65 | fb-only | 21 | 18 | 9 | 83.3% | -9.3% | 60.8% |
| ml-meta | avg_p>=70 | zb-only | 12 | 10 | 1 | 90.0% | -100.0% | 59.6% |
| ml-meta | avg_p>=70 | fb-only | 12 | 10 | 5 | 90.0% | 11.2% | 59.6% |
| ml-fade | parent avg_p>=55 | zb-only | 63 | 58 | 2 | 8.6% | -100.0% | 3.7% |
| ml-fade | parent avg_p>=55 | fb-only | 63 | 58 | 29 | 8.6% | -11.7% | 3.7% |
| ml-fade | parent avg_p>=60 | zb-only | 38 | 34 | 2 | 5.9% | -100.0% | 1.6% |
| ml-fade | parent avg_p>=60 | fb-only | 38 | 34 | 14 | 5.9% | 14.3% | 1.6% |
| ml-fade | parent avg_p>=65 | zb-only | 21 | 18 | 2 | 5.6% | -100.0% | 1.0% |
| ml-fade | parent avg_p>=65 | fb-only | 21 | 18 | 9 | 5.6% | -5.6% | 1.0% |
| ml-fade | parent avg_p>=70 | zb-only | 12 | 10 | 1 | 0.0% | -100.0% | -0.0% |
| ml-fade | parent avg_p>=70 | fb-only | 12 | 10 | 5 | 0.0% | -100.0% | -0.0% |

## Automatic rule-candidate signal (research heuristic — NOT certification)

**Status: OBSERVING**

- unmet gate: zb-only n_priced 55 < 150
- unmet gate: zb-only wilson_lb 0.197 < 0.55
- unmet gate: zb-only roi -0.43 <= 0.0
- unmet gate: fb-only wilson_lb 0.197 < 0.55
- unmet gate: fb-only roi -0.2747 <= 0.0
- unmet gate: 1 unresolved conflict row(s) in fade family

> automatic research heuristic only — certification remains the existing walk-forward machinery, untouched.

## Warnings

- 🚨 FADE PRICE COVERAGE LOW (zb-only): 8% of settled fade rows carry a first-seen zb-only quote (< 90% threshold)
- 🚨 FADE PRICE COVERAGE LOW (fb-only): 57% of settled fade rows carry a first-seen fb-only quote (< 90% threshold)
- 🚨 UNRESOLVED CONFLICTS (ml-meta): 1 row(s) hold contradictory result claims — human review required, never auto-resolved
- 🚨 UNRESOLVED CONFLICTS (ml-fade): 1 row(s) hold contradictory result claims — human review required, never auto-resolved

## Frozen full-population studies

The frozen, unmodified research scripts were re-run at this checkpoint; outputs archived:
- `contexts` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_contexts_2026-10-01.txt`
- `price_study` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_price_study_2026-10-01.txt`

## Provenance

- serving model key: `fcbb07f55a92`
- frozen serving method drifted: **False**
- stale model keys present in ledger: ['00676495f942', '01f98ed9936b', '029a51a6c9a2', '0485aef21613', '06b6903f96dc', '09b94efe5419', '0ab793d02c02', '0cc23b9d9934', '0e5362528d7b', '1013c0e4e535', '11d2a701a456', '14c59a6211ef', '20b346abc92f', '24ae7edfc7e7', '27f1e9ebab85', '289e086d84db', '29f20ae26d96', '323c100d7524', '35b61895a181', '363e7bfaa219', '40e00cc32eba', '41972eca6848', '41f0e1e5dec5', '42516a50a15b', '46280f3b01bf', '46efa845f2f1', '4c87eebc1768', '4f6460868f97', '533a9a4932b6', '563da1602950', '5693629e03b1', '5995600039ad', '5ac0bb041e10', '5fcf03a68b29', '604a0ae8437c', '633faa446086', '643e3c399c35', '6a8cf5e0f006', '6adbf860bf0e', '6c20c7fcd357', '706aa1c05083', '711ff65e0e5e', '71800f16e755', '749fc72ea111', '75384507e4ef', '7672bc23a439', '78d95eb0a42d', '7b717377ba79', '7b7a7d43aa97', '7c9f64dcebd4', '817a56b94bbd', '921a1b4ae272', '960856b6997f', '964834d0144a', '966cc28a600a', '99ecaeba1b8f', '9bf3a04f1fc7', 'a03d6bad2781', 'a2c8a5099e3f', 'a584ef59212a', 'a6c7db2fcf23', 'aab5095b04eb', 'ad967c7878dd', 'b09668105711', 'b15203feada1', 'ba2499eccbd3', 'bcddb8d1a667', 'bd2eb96cafec', 'bfa38ffed58d', 'c614bd726cdd', 'c78eabfffe02', 'c79f1af99a3e', 'c822740cdb3f', 'd1a3a03ba50f', 'd2a004e29202', 'd59968d42bf4', 'd5a82837085c', 'd6b2476de931', 'e08a036da4c6', 'e62f7c6399fa', 'eec36bca3ccb', 'f399fe11bec0']
- ledger: `localdata/ml_fade_research_ledger.json` (tracked; bot commits each run)
- state: `localdata/ml_fade_research_state.json` (tracked; checkpoint history)
- policy: HANDOVER.md, 'ML-FADE RESEARCH GUARDRAIL' (frozen 2026-09-20)

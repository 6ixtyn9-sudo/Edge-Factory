# ML-Fade Research Checkpoint — 2026-10-04

**RESEARCH-ONLY — definitions FROZEN at 2026-09-20 and never change. This report cannot certify, promote, or alter any operational pick, ticket, gate, or registry entry.**

Checkpoint due because: settled fade rows grew by 141 (>= 50).

## Accrual (cumulative, plus new since last checkpoint)

| family | rows | settled | pending | conflict | unmatched | new |
|---|---|---|---|---|---|---|
| ml-meta | 1119 | 1004 | 114 | 1 | 0 | +103 |
| ml-fade | 950 | 846 | 103 | 1 | 0 | +98 |

## Fixed price variants (first-seen bet-time quotes)

### ml-meta

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 1004 | 490 | 48.8% | 45.7% | 90 | -11.5% |
| fb-only | 1004 | 490 | 48.8% | 45.7% | 526 | -8.8% |

### ml-fade

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 846 | 193 | 22.8% | 20.1% | 82 | -42.0% |
| fb-only | 846 | 193 | 22.8% | 20.1% | 371 | -27.5% |

## Reference accumulators (frozen grids — research contexts)

| family | grid | variant | rows | settled | priced | hit | ROI | Wilson LB |
|---|---|---|---|---|---|---|---|---|
| ml-meta | avg_p>=55 | zb-only | 91 | 81 | 5 | 75.3% | -7.8% | 64.9% |
| ml-meta | avg_p>=55 | fb-only | 91 | 81 | 29 | 75.3% | -17.5% | 64.9% |
| ml-meta | avg_p>=60 | zb-only | 59 | 52 | 5 | 82.7% | -7.8% | 70.3% |
| ml-meta | avg_p>=60 | fb-only | 59 | 52 | 14 | 82.7% | -22.6% | 70.3% |
| ml-meta | avg_p>=65 | zb-only | 36 | 31 | 5 | 90.3% | -7.8% | 75.1% |
| ml-meta | avg_p>=65 | fb-only | 36 | 31 | 9 | 90.3% | -9.3% | 75.1% |
| ml-meta | avg_p>=70 | zb-only | 20 | 17 | 3 | 94.1% | -29.0% | 73.0% |
| ml-meta | avg_p>=70 | fb-only | 20 | 17 | 5 | 94.1% | 11.2% | 73.0% |
| ml-fade | parent avg_p>=55 | zb-only | 96 | 86 | 5 | 10.5% | -100.0% | 5.6% |
| ml-fade | parent avg_p>=55 | fb-only | 96 | 86 | 29 | 10.5% | -11.7% | 5.6% |
| ml-fade | parent avg_p>=60 | zb-only | 62 | 55 | 5 | 7.3% | -100.0% | 2.9% |
| ml-fade | parent avg_p>=60 | fb-only | 62 | 55 | 14 | 7.3% | 14.3% | 2.9% |
| ml-fade | parent avg_p>=65 | zb-only | 36 | 31 | 5 | 3.2% | -100.0% | 0.6% |
| ml-fade | parent avg_p>=65 | fb-only | 36 | 31 | 9 | 3.2% | -5.6% | 0.6% |
| ml-fade | parent avg_p>=70 | zb-only | 20 | 17 | 3 | 0.0% | -100.0% | 0.0% |
| ml-fade | parent avg_p>=70 | fb-only | 20 | 17 | 5 | 0.0% | -100.0% | 0.0% |

## Automatic rule-candidate signal (research heuristic — NOT certification)

**Status: OBSERVING**

- unmet gate: zb-only n_priced 82 < 150
- unmet gate: zb-only wilson_lb 0.2011 < 0.55
- unmet gate: zb-only roi -0.4205 <= 0.0
- unmet gate: fb-only wilson_lb 0.2011 < 0.55
- unmet gate: fb-only roi -0.2747 <= 0.0
- unmet gate: 1 unresolved conflict row(s) in fade family

> automatic research heuristic only — certification remains the existing walk-forward machinery, untouched.

## Warnings

- 🚨 FADE PRICE COVERAGE LOW (zb-only): 10% of settled fade rows carry a first-seen zb-only quote (< 90% threshold)
- 🚨 FADE PRICE COVERAGE LOW (fb-only): 44% of settled fade rows carry a first-seen fb-only quote (< 90% threshold)
- 🚨 UNRESOLVED CONFLICTS (ml-meta): 1 row(s) hold contradictory result claims — human review required, never auto-resolved
- 🚨 UNRESOLVED CONFLICTS (ml-fade): 1 row(s) hold contradictory result claims — human review required, never auto-resolved

## Frozen full-population studies

The frozen, unmodified research scripts were re-run at this checkpoint; outputs archived:
- `contexts` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_contexts_2026-10-04.txt`
- `price_study` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_price_study_2026-10-04.txt`

## Provenance

- serving model key: `2d079b344523`
- frozen serving method drifted: **False**
- stale model keys present in ledger: ['00676495f942', '01f98ed9936b', '029a51a6c9a2', '0485aef21613', '0604afced653', '06b6903f96dc', '09b94efe5419', '0ab793d02c02', '0cc23b9d9934', '0e5362528d7b', '1013c0e4e535', '11d2a701a456', '14c59a6211ef', '1d56b43096da', '1e65b4a180c2', '20b346abc92f', '24ae7edfc7e7', '27f1e9ebab85', '289e086d84db', '29f20ae26d96', '2c253ffa0fd0', '323c100d7524', '35b61895a181', '363e7bfaa219', '37ae4bfdef24', '40e00cc32eba', '41972eca6848', '41f0e1e5dec5', '42516a50a15b', '45eca8e57492', '46280f3b01bf', '46efa845f2f1', '4c87eebc1768', '4d10a2d4ee61', '4f6460868f97', '4fd7d8dd9e0b', '533a9a4932b6', '563da1602950', '5693629e03b1', '5995600039ad', '5ac0bb041e10', '5b558789f6ce', '5fcf03a68b29', '604a0ae8437c', '633faa446086', '643e3c399c35', '6a8cf5e0f006', '6adbf860bf0e', '6c20c7fcd357', '706aa1c05083', '711ff65e0e5e', '71800f16e755', '749fc72ea111', '75384507e4ef', '7672bc23a439', '779b2d7a80fb', '78d95eb0a42d', '7b717377ba79', '7b7a7d43aa97', '7c9f64dcebd4', '817a56b94bbd', '8cfd9453d765', '911f98ec0648', '921a1b4ae272', '9538bfae4c37', '960856b6997f', '964834d0144a', '966cc28a600a', '975b37babe8f', '99ecaeba1b8f', '9bf3a04f1fc7', 'a03d6bad2781', 'a0859f7be9ae', 'a2c8a5099e3f', 'a584ef59212a', 'a6c7db2fcf23', 'a9131e5c724b', 'aab5095b04eb', 'ad967c7878dd', 'adb262cfc611', 'b09668105711', 'b15203feada1', 'b5af4621e122', 'ba2499eccbd3', 'bcddb8d1a667', 'bd2eb96cafec', 'bfa38ffed58d', 'c3e93ab0178c', 'c536b63c8e45', 'c614bd726cdd', 'c78eabfffe02', 'c79f1af99a3e', 'c822740cdb3f', 'cdf3b3c8ad8a', 'd1a3a03ba50f', 'd2a004e29202', 'd59968d42bf4', 'd5a82837085c', 'd6b2476de931', 'dd2d5e716bdc', 'dd6b4f69831c', 'de52d7cc65ff', 'e08a036da4c6', 'e5d24fd82623', 'e62f7c6399fa', 'ee316a5e00b9', 'eec36bca3ccb', 'f399fe11bec0']
- ledger: `localdata/ml_fade_research_ledger.json` (tracked; bot commits each run)
- state: `localdata/ml_fade_research_state.json` (tracked; checkpoint history)
- policy: HANDOVER.md, 'ML-FADE RESEARCH GUARDRAIL' (frozen 2026-09-20)

# ML-Fade Research Checkpoint — 2026-10-01

**RESEARCH-ONLY — definitions FROZEN at 2026-09-20 and never change. This report cannot certify, promote, or alter any operational pick, ticket, gate, or registry entry.**

Checkpoint due because: monthly checkpoint (last 2026-09, now 2026-10).

## Accrual (cumulative, plus new since last checkpoint)

| family | rows | settled | pending | conflict | unmatched | new |
|---|---|---|---|---|---|---|
| ml-meta | 884 | 812 | 71 | 1 | 0 | +49 |
| ml-fade | 727 | 662 | 64 | 1 | 0 | +48 |

## Fixed price variants (first-seen bet-time quotes)

### ml-meta

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 812 | 380 | 46.8% | 43.4% | 63 | -1.5% |
| fb-only | 812 | 380 | 46.8% | 43.4% | 526 | -8.8% |

### ml-fade

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 662 | 150 | 22.7% | 19.6% | 59 | -40.1% |
| fb-only | 662 | 150 | 22.7% | 19.6% | 371 | -27.5% |

## Reference accumulators (frozen grids — research contexts)

| family | grid | variant | rows | settled | priced | hit | ROI | Wilson LB |
|---|---|---|---|---|---|---|---|---|
| ml-meta | avg_p>=55 | zb-only | 59 | 56 | 3 | 75.0% | -29.3% | 62.3% |
| ml-meta | avg_p>=55 | fb-only | 59 | 56 | 29 | 75.0% | -17.5% | 62.3% |
| ml-meta | avg_p>=60 | zb-only | 36 | 34 | 3 | 79.4% | -29.3% | 63.2% |
| ml-meta | avg_p>=60 | fb-only | 36 | 34 | 14 | 79.4% | -22.6% | 63.2% |
| ml-meta | avg_p>=65 | zb-only | 22 | 20 | 3 | 85.0% | -29.3% | 64.0% |
| ml-meta | avg_p>=65 | fb-only | 22 | 20 | 9 | 85.0% | -9.3% | 64.0% |
| ml-meta | avg_p>=70 | zb-only | 13 | 11 | 2 | 90.9% | -46.5% | 62.3% |
| ml-meta | avg_p>=70 | fb-only | 13 | 11 | 5 | 90.9% | 11.2% | 62.3% |
| ml-fade | parent avg_p>=55 | zb-only | 64 | 61 | 3 | 8.2% | -100.0% | 3.6% |
| ml-fade | parent avg_p>=55 | fb-only | 64 | 61 | 29 | 8.2% | -11.7% | 3.6% |
| ml-fade | parent avg_p>=60 | zb-only | 39 | 37 | 3 | 5.4% | -100.0% | 1.5% |
| ml-fade | parent avg_p>=60 | fb-only | 39 | 37 | 14 | 5.4% | 14.3% | 1.5% |
| ml-fade | parent avg_p>=65 | zb-only | 22 | 20 | 3 | 5.0% | -100.0% | 0.9% |
| ml-fade | parent avg_p>=65 | fb-only | 22 | 20 | 9 | 5.0% | -5.6% | 0.9% |
| ml-fade | parent avg_p>=70 | zb-only | 13 | 11 | 2 | 0.0% | -100.0% | 0.0% |
| ml-fade | parent avg_p>=70 | fb-only | 13 | 11 | 5 | 0.0% | -100.0% | 0.0% |

## Automatic rule-candidate signal (research heuristic — NOT certification)

**Status: OBSERVING**

- unmet gate: zb-only n_priced 59 < 150
- unmet gate: zb-only wilson_lb 0.1963 < 0.55
- unmet gate: zb-only roi -0.4005 <= 0.0
- unmet gate: fb-only wilson_lb 0.1963 < 0.55
- unmet gate: fb-only roi -0.2747 <= 0.0
- unmet gate: 1 unresolved conflict row(s) in fade family

> automatic research heuristic only — certification remains the existing walk-forward machinery, untouched.

## Warnings

- 🚨 FADE PRICE COVERAGE LOW (zb-only): 9% of settled fade rows carry a first-seen zb-only quote (< 90% threshold)
- 🚨 FADE PRICE COVERAGE LOW (fb-only): 56% of settled fade rows carry a first-seen fb-only quote (< 90% threshold)
- 🚨 UNRESOLVED CONFLICTS (ml-meta): 1 row(s) hold contradictory result claims — human review required, never auto-resolved
- 🚨 UNRESOLVED CONFLICTS (ml-fade): 1 row(s) hold contradictory result claims — human review required, never auto-resolved

## Frozen full-population studies

The frozen, unmodified research scripts were re-run at this checkpoint; outputs archived:
- `contexts` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_contexts_2026-10-01.txt`
- `price_study` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_price_study_2026-10-01.txt`

## Provenance

- serving model key: `9846927cd287`
- frozen serving method drifted: **False**
- stale model keys present in ledger: ['00676495f942', '01f98ed9936b', '029a51a6c9a2', '0485aef21613', '06b6903f96dc', '09b94efe5419', '0ab793d02c02', '0c25c5f8f35d', '0cc23b9d9934', '0e5362528d7b', '1013c0e4e535', '1094c7739021', '11d2a701a456', '14c59a6211ef', '20b346abc92f', '24ae7edfc7e7', '27f1e9ebab85', '289e086d84db', '29f20ae26d96', '31bcbfa4a254', '323c100d7524', '35b61895a181', '363e7bfaa219', '40e00cc32eba', '41972eca6848', '41f0e1e5dec5', '42516a50a15b', '46280f3b01bf', '46efa845f2f1', '4c87eebc1768', '4f6460868f97', '533a9a4932b6', '563da1602950', '568097547b04', '5693629e03b1', '5995600039ad', '5ac0bb041e10', '5fcf03a68b29', '604a0ae8437c', '633faa446086', '643e3c399c35', '6a8cf5e0f006', '6adbf860bf0e', '6c20c7fcd357', '706aa1c05083', '711ff65e0e5e', '71800f16e755', '749fc72ea111', '75384507e4ef', '7672bc23a439', '783886e74e3b', '78d95eb0a42d', '7b717377ba79', '7b7a7d43aa97', '7c9f64dcebd4', '817a56b94bbd', '8ed17d7be9da', '921a1b4ae272', '960856b6997f', '964834d0144a', '966cc28a600a', '99ecaeba1b8f', '9a7ed48cb66e', '9bf3a04f1fc7', 'a03d6bad2781', 'a2c8a5099e3f', 'a584ef59212a', 'a6c7db2fcf23', 'aab5095b04eb', 'ad967c7878dd', 'b09668105711', 'b15203feada1', 'b21c5a913543', 'ba2499eccbd3', 'bcddb8d1a667', 'bd2eb96cafec', 'bfa38ffed58d', 'c5d3e028fe59', 'c614bd726cdd', 'c78eabfffe02', 'c79f1af99a3e', 'c822740cdb3f', 'd1a3a03ba50f', 'd1d7a24e87a1', 'd2a004e29202', 'd59968d42bf4', 'd5a82837085c', 'd6b2476de931', 'dd37234b45d0', 'e08a036da4c6', 'e62f7c6399fa', 'ec8d7ffa3a66', 'eec36bca3ccb', 'f399fe11bec0']
- ledger: `localdata/ml_fade_research_ledger.json` (tracked; bot commits each run)
- state: `localdata/ml_fade_research_state.json` (tracked; checkpoint history)
- policy: HANDOVER.md, 'ML-FADE RESEARCH GUARDRAIL' (frozen 2026-09-20)

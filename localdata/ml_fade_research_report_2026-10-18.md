# ML-Fade Research Checkpoint — 2026-10-18

**RESEARCH-ONLY — definitions FROZEN at 2026-09-20 and never change. This report cannot certify, promote, or alter any operational pick, ticket, gate, or registry entry.**

Checkpoint due because: settled fade rows grew by 248 (>= 50).

## Accrual (cumulative, plus new since last checkpoint)

| family | rows | settled | pending | conflict | unmatched | new |
|---|---|---|---|---|---|---|
| ml-meta | 2419 | 2182 | 227 | 0 | 10 | +258 |
| ml-fade | 2189 | 1961 | 220 | 0 | 8 | +253 |

## Fixed price variants (first-seen bet-time quotes)

### ml-meta

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 2182 | 1112 | 51.0% | 48.9% | 316 | 0.3% |
| fb-only | 2182 | 1112 | 51.0% | 48.9% | 526 | -8.8% |

### ml-fade

| variant | settled | wins | hit | Wilson LB | priced | ROI |
|---|---|---|---|---|---|---|
| zb-only | 1961 | 455 | 23.2% | 21.4% | 270 | -43.5% |
| fb-only | 1961 | 455 | 23.2% | 21.4% | 371 | -27.5% |

## Reference accumulators (frozen grids — research contexts)

| family | grid | variant | rows | settled | priced | hit | ROI | Wilson LB |
|---|---|---|---|---|---|---|---|---|
| ml-meta | avg_p>=55 | zb-only | 400 | 366 | 100 | 68.9% | 2.9% | 63.9% |
| ml-meta | avg_p>=55 | fb-only | 400 | 366 | 29 | 68.9% | -17.5% | 63.9% |
| ml-meta | avg_p>=60 | zb-only | 249 | 229 | 70 | 72.5% | 17.3% | 66.4% |
| ml-meta | avg_p>=60 | fb-only | 249 | 229 | 14 | 72.5% | -22.6% | 66.4% |
| ml-meta | avg_p>=65 | zb-only | 129 | 116 | 25 | 81.0% | 4.3% | 73.0% |
| ml-meta | avg_p>=65 | fb-only | 129 | 116 | 9 | 81.0% | -9.3% | 73.0% |
| ml-meta | avg_p>=70 | zb-only | 66 | 60 | 7 | 85.0% | -11.1% | 73.9% |
| ml-meta | avg_p>=70 | fb-only | 66 | 60 | 5 | 85.0% | 11.2% | 73.9% |
| ml-fade | parent avg_p>=55 | zb-only | 406 | 371 | 100 | 11.6% | -47.4% | 8.7% |
| ml-fade | parent avg_p>=55 | fb-only | 406 | 371 | 29 | 11.6% | -11.7% | 8.7% |
| ml-fade | parent avg_p>=60 | zb-only | 252 | 232 | 70 | 9.9% | -50.9% | 6.7% |
| ml-fade | parent avg_p>=60 | fb-only | 252 | 232 | 14 | 9.9% | 14.3% | 6.7% |
| ml-fade | parent avg_p>=65 | zb-only | 129 | 116 | 25 | 5.2% | -39.6% | 2.4% |
| ml-fade | parent avg_p>=65 | fb-only | 129 | 116 | 9 | 5.2% | -5.6% | 2.4% |
| ml-fade | parent avg_p>=70 | zb-only | 66 | 60 | 7 | 3.3% | 60.0% | 0.9% |
| ml-fade | parent avg_p>=70 | fb-only | 66 | 60 | 5 | 3.3% | -100.0% | 0.9% |

## Automatic rule-candidate signal (research heuristic — NOT certification)

**Status: OBSERVING**

- unmet gate: zb-only wilson_lb 0.2139 < 0.55
- unmet gate: zb-only roi -0.4346 <= 0.0
- unmet gate: fb-only wilson_lb 0.2139 < 0.55
- unmet gate: fb-only roi -0.2747 <= 0.0

> automatic research heuristic only — certification remains the existing walk-forward machinery, untouched.

## Warnings

- 🚨 FADE PRICE COVERAGE LOW (zb-only): 14% of settled fade rows carry a first-seen zb-only quote (< 90% threshold)
- 🚨 FADE PRICE COVERAGE LOW (fb-only): 19% of settled fade rows carry a first-seen fb-only quote (< 90% threshold)

## Frozen full-population studies

The frozen, unmodified research scripts were re-run at this checkpoint; outputs archived:
- `contexts` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_contexts_2026-10-18.txt`
- `price_study` → `/home/runner/work/Edge-Factory/Edge-Factory/localdata/ml_fade_checkpoint_price_study_2026-10-18.txt`

## Provenance

- serving model key: `a45beab0c878`
- frozen serving method drifted: **False**
- stale model keys present in ledger: ['00676495f942', '01f98ed9936b', '0272bd8f1cd7', '029a51a6c9a2', '02ea491a5f62', '0485aef21613', '0604afced653', '06b6903f96dc', '08aeb4b8a18c', '09b94efe5419', '0ab793d02c02', '0cc23b9d9934', '0e5362528d7b', '1013c0e4e535', '11d2a701a456', '14bc4546f165', '14c59a6211ef', '1d56b43096da', '1e65b4a180c2', '20b346abc92f', '24ae7edfc7e7', '27f1e9ebab85', '289e086d84db', '29f20ae26d96', '2c253ffa0fd0', '2d079b344523', '323c100d7524', '35543e935cd1', '35b61895a181', '363e7bfaa219', '37ae4bfdef24', '38627074e261', '38e7dc65022b', '39f146eb3303', '3b4310716316', '3fb8dd932849', '40e00cc32eba', '41972eca6848', '41f0e1e5dec5', '42516a50a15b', '4470a017188d', '45eca8e57492', '46280f3b01bf', '46652a740186', '46efa845f2f1', '4c87eebc1768', '4d10a2d4ee61', '4f6460868f97', '4fd7d8dd9e0b', '533a9a4932b6', '53f885e081ad', '55ba654f8c0f', '563da1602950', '5693629e03b1', '5995600039ad', '5ac0bb041e10', '5b558789f6ce', '5d1079eb812a', '5fcf03a68b29', '604a0ae8437c', '633faa446086', '643e3c399c35', '6555f88848c4', '66712e636b73', '674fee773653', '6a8cf5e0f006', '6adbf860bf0e', '6bc050bc15a5', '6c20c7fcd357', '706aa1c05083', '711ff65e0e5e', '71800f16e755', '72a3636a2534', '749fc72ea111', '75384507e4ef', '7672bc23a439', '779b2d7a80fb', '78d95eb0a42d', '7b717377ba79', '7b7a7d43aa97', '7c6dcf6bb34c', '7c9f64dcebd4', '817a56b94bbd', '8cfd9453d765', '911f98ec0648', '921a1b4ae272', '9538bfae4c37', '960856b6997f', '964834d0144a', '966cc28a600a', '975b37babe8f', '99ecaeba1b8f', '9bf3a04f1fc7', 'a03d6bad2781', 'a0859f7be9ae', 'a2c8a5099e3f', 'a584ef59212a', 'a6c7db2fcf23', 'a9131e5c724b', 'aab5095b04eb', 'ad967c7878dd', 'adb262cfc611', 'b09668105711', 'b15203feada1', 'b5af4621e122', 'b8ce6565d83e', 'ba2499eccbd3', 'bcddb8d1a667', 'bd2eb96cafec', 'bfa38ffed58d', 'bfc4c0a46661', 'c3e93ab0178c', 'c4a84c6e8fa9', 'c536b63c8e45', 'c614bd726cdd', 'c78eabfffe02', 'c79f1af99a3e', 'c822740cdb3f', 'c843e11a70e8', 'cbbffcbe4987', 'cdf3b3c8ad8a', 'd1a3a03ba50f', 'd2a004e29202', 'd3d09fdb2147', 'd452872aa0aa', 'd59968d42bf4', 'd5a82837085c', 'd6b2476de931', 'dd2d5e716bdc', 'dd6b4f69831c', 'de52d7cc65ff', 'e08a036da4c6', 'e572f306101c', 'e5d24fd82623', 'e62f7c6399fa', 'e740450ae922', 'ee316a5e00b9', 'eec36bca3ccb', 'f26119bb92a4', 'f399fe11bec0', 'f7c6dd3c6810', 'facf9d7026ee', 'fe7746eb27d2']
- ledger: `localdata/ml_fade_research_ledger.json` (tracked; bot commits each run)
- state: `localdata/ml_fade_research_state.json` (tracked; checkpoint history)
- policy: HANDOVER.md, 'ML-FADE RESEARCH GUARDRAIL' (frozen 2026-09-20)

# Why the auto tickets have gone quiet — full diagnosis (2026-08-27)

*All numbers below are computed directly from `localdata/` archives (71 pick ledgers, 2026-06-19 → 2026-08-28) and `settled_results.json` (36,584 settled matches). Walk-forward backtests use only data available *before* each day — same discipline as the live gate.*

---

## 1. TL;DR

1. **Nothing is broken.** The pipeline runs 8×/day, picks keep firing (270 `ml-meta` picks in the last 14 days per the tripwire), settlement is ~90% complete, and there is **no RED-ALERT pause**. The machine is silent *on purpose*.
2. **The silence has one mechanical cause:** since 2026-08-01, exactly **one** (rule × source) combo passes all five gates — `ml-meta avg_p>=55` × `bzzoiro_odds` — and that combo supplies **~0.8 playable legs/day**. A 2-odd acca needs 2 legs, the 10-odd needs ≥3. So: "NO EDGE TODAY".
3. **Is nothing good enough?** Close to true at combo level, and the all-bets record backs the gate up: 519 settled priced picks, 71.1% hit, **flat ROI −1.3%**. CLV over the last month: **13.5% beat-later-price rate, average implied-prob delta ≈ −0.09%** — the picks are not beating the market. The gate is starving because the food is negative-EV, not because the gate is cruel.
4. **But the gate unit is wrong.** Pooling evidence at **source level** instead of (rule × source) would have fired **19 of 71 days** walk-forward with **+3.9% leg ROI / +4.7% acca2 ROI**; excluding betexplorer/scoutingstats legs from tickets: **17 fireable days, +7.0% leg ROI, +31.9% acca2 ROI (22 tickets, 72.7% hit)**. Promising — not yet statistically proven (Wilson 90% LB ≈ 0.55 vs 0.50 needed).

---

## 2. Why the tickets stopped firing — the exact chain

The gate (`scripts/auto_tickets.py`) requires each (rule × odds_source) combo to have: n≥15 settled, lifetime ROI ≥ +3%, last-20 ROI ≥ 0, newest settle ≤ 30d, Wilson LB ≥ 0.50.

**Reconstructed per-day for all of August:** on every single day 08-01 → 08-28 the *only* passing combo was `ml-meta avg_p>=55` × `bzzoiro_odds`.

The funnel on a typical day (e.g. 08-27: 7 playable-bucket picks → 0 pass-combo hits):

| filter stage | what dies | evidence |
|---|---|---|
| bucket / quarantine | CAUTION + suspect picks excluded | CAUTION bucket ROI **−9.2%** (n=128) — correct exclusion |
| combo ROI ≥ +3% | betexplorer combos | betexplorer source ROI **−0.2%** (n=195), last-20 −9% |
| combo ROI ≥ +3% | scoutingstats combos | scoutingstats source ROI **−12.8%** (n=125) — worst source |
| n ≥ 15 per combo | forebet_best | **+8.0% lifetime (n=52)** but fragmented across 14 rules → no single (rule×source) cell reaches n=15 |
| freshness ≤ 30d | zulubet | stale since 06-12 (tripwire), ROI −2.5% |
| last leg supply | bzzoiro `ml-meta avg_p>=55` | Aug: 83 bzzoiro picks → 57 playable → **only 21 carry the passing rule** (~0.8/day) |

The two slips that *did* fire (08-09 ✅✅, 08-13 ❌ −100%) came from this same thin bzzoiro stream in its hot week (08-12 → 08-17 had 2–5 legs/day). Since then the pool is back to 0–1 legs/day.

**Important:** the status-quo gate's own out-of-sample record is bad — walk-forward, the combo gate fired only **4/71 days** and its fired legs went **−4.6% ROI** (5 acca2 tickets, −27%). The one combo that passes is passing on ~35 settled picks of momentum, not on a deep edge.

---

## 3. Performance of ALL bets (every settled priced pick, flat 1u)

**Overall: n=519, hit 71.1%, ROI −1.3%.** You are paying the vig, not beating the market.

### By bucket
| bucket | n | hit | ROI |
|---|---|---|---|
| SKIPPED_VETO | 296 | 75.0% | **+2.7%** |
| WATCHLIST_UNKNOWN_CTX | 31 | 87.1% | **+4.3%** |
| WATCHLIST_UNCORROBORATED_PRICE | 44 | 72.7% | +1.5% |
| CAUTION | 128 | 60.2% | **−9.2%** |
| CERTIFIED_CLEAN | 16 | 50.0% | −28.3% |
| WATCHLIST_SUSPECT_PRICE | 4 | 75.0% | −9.2% |

### By source
| source | n | hit | ROI | verdict |
|---|---|---|---|---|
| forebet_best | 52 | 76.9% | **+8.0%** | good, but starved (n fragmented across rules; cache stale since 06-12) |
| bzzoiro_odds | 120 | 72.5% | **+5.2%** | good; last-20 +36% |
| betexplorer_odds | 195 | 73.8% | −0.2% | break-even; useful as *corroboration*, not as ticket legs |
| zulubet | 27 | 74.1% | −2.5% | stale capture since 06-12 |
| scoutingstats_odds | 125 | 62.4% | **−12.8%** | toxic as legs |

### By odds band (where the edge actually lives)
| odds | n | hit | ROI |
|---|---|---|---|
| < 1.30 | 167 | 86.8% | **+2.1%** |
| 1.30–1.60 | 231 | 68.4% | −3.0% |
| 1.60–2.00 | 107 | 54.2% | **−7.4%** |
| > 2.00 | 14 | 57.1% | +33.1% (noise, n=14) |

### Trend & CLV
- Monthly ROI: Jun +3.2% (n=36) → Jul −0.9% (n=132) → **Aug −1.9% (n=351)** — fading as volume grows.
- CLV (07-27→08-26, 428 two-price picks): beat-later-price rate **13.5%**, avg implied-prob delta −0.09%. The prices taken are *not* better than later prices. No market-beating edge is present in price capture today.

---

## 4. Walk-forward backtest of alternative gates (71 days)

Gates rebuilt daily using only prior data; same bucket/quarantine filters; acca2 = smallest×largest pairing, ≤3 tickets/day.

| strategy | fireable days | legs | leg hit | leg ROI | acca2 tickets | acca2 ROI |
|---|---|---|---|---|---|---|
| **status quo (rule×source combo)** | 4 / 71 | 19 | 68.4% | **−4.6%** | 5 | −27.0% |
| rule-family pooled | 1 / 71 | 4 | 50.0% | −42.2% | 1 | −100% |
| source pooled | 19 / 71 | 79 | 75.9% | **+3.9%** | 27 | +4.7% |
| **source pooled, betexplorer+scoutingstats legs excluded** | **17 / 71** | 63 | 77.8% | **+7.0%** | **22 (72.7% hit)** | **+31.9%** |

OOS contribution in the best variant: bzzoiro legs +7.9% (n=43), forebet legs +5.2% (n=20).

**Honesty check:** 22 tickets at ~2.0 odds, 16 wins → Wilson 90% LB on hit rate ≈ **0.55** (need >0.50). Borderline significant, and it is the best of four variants tried (selection bias inflates it). This is *probation-grade* evidence, not proof.

---

## 5. Recommended course of action

1. **Do not lower the gates.** Every stream currently failing them has negative realized ROI. Forcing tickets (‑-force, PASS_ROI < 3%, n<15) converts the silence into a slow bleed. The 08-13 forced-window ticket already went −100%.
2. **Change the gate unit from (rule×source) to source level** — same thresholds (n≥15–20, ROI≥+3%, last-20≥0, fresh≤30d, Wilson LB≥0.50 at source level). This unfreezes forebet_best (the +8% source currently benched purely by sample fragmentation) and bzzoiro, and it would have fired ~2.5–3 days/week instead of ~0.4.
3. **Leg filter: tickets take bzzoiro + forebet legs only** while their OOS record accumulates; betexplorer stays in the factory for corroboration/pricing, never as a leg; scoutingstats stays out of tickets entirely.
4. **Kill or halve the 10-odd acca.** The 1.60–2.00 odds band is −7.4%; a 10-odd needs 6–9 thin legs compounded, and the graded 10-odd sample is n=1. Highest-variance, lowest-EV part of the plan. Redirect that 10% to nothing (bank it) until CLV turns positive.
5. **Fix the supply side (this is the real starver):** forebet/statarea/zulubet caches are stale since 06-12 (tripwire). forebet is one of only two +EV sources — restoring that capture directly feeds the only streams worth betting. Also fix the tripwire's `bzzoiro: no files` visibility (it *is* producing picks — the monitor can't see its adapter).
6. **Make CLV the KPI, not ticket ROI.** At 519 settled picks the ROI signal says break-even; CLV says no edge. If after another ~300 picks the beat-rate is still <30% with ~0 CLV delta, no ticket structure can win — the improvement has to come from earlier/sharper price capture, not from the slip.
7. **Probation sizing for the new gate:** cap deployment at half the ceiling (~19% of capital, i.e. 3 × ~4.7% acca2 tickets, no 10-odd) for the first 30 graded tickets, then review against the backtest (+31.9% is the *hoped* ceiling, +4–5% is the conservative read).

## 6. What NOT to do

- Don't whitelist sources by name *without* the ROI gate (scoutingstats and betexplorer both fail as legs).
- Don't re-add CAUTION/SUSPECT buckets to increase volume (−9.2% and worse).
- Don't chase the >2.00 odds band (+33% on n=14 is a coin-flip artifact).
- Don't read "NO EDGE TODAY" as a malfunction to be fixed by betting more.

# Why the auto tickets have gone quiet — full diagnosis (2026-08-27, rev 2)

*rev 2: corrected the forebet/statarea/zulubet supply-side claim after reading HANDOVER.md end-to-end (08-20 addenda series), and added the full every-bucket audit incl. veto-reason decomposition, WATCHLIST_NO_ODDS, price-evidence and the veto-overlay shadow. All numbers computed from `localdata/` (71 pick ledgers 2026-06-19→08-28, `settled_results.json` 36,584 matches). Walk-forward backtests use only data available before each day.*

---

## 1. TL;DR

1. **Nothing is broken.** Pipeline runs 8×/day, all six voter sources vote daily, settlement ~90% complete, no RED-ALERT pause. The machine is silent *by design*.
2. **One mechanical cause:** since 2026-08-01 exactly one (rule × source) combo passes all five gates — `ml-meta avg_p>=55` × `bzzoiro_odds` — and it supplies ~0.8 playable legs/day. A 2-odd acca needs 2 legs → "NO EDGE TODAY" nearly every day.
3. **All-bets record:** 519 settled priced picks, 71.1% hit, flat ROI **−1.3%**. CLV (last 30d): 13.5% beat-later-price rate, avg implied-prob delta ≈ −0.09% — not beating the market. **Every bucket's ROI fades toward break-even as n grows** (SKIPPED_VETO: Jun +18.3% → Jul +6.1% → Aug +0.1%).
4. **Veto audit (new):** the veto layer is half right. Home-team, league, niche and combined vetoes are protective (−4% to −43%). **Away-side and odds-band vetoes are discarding winners**: `team_a` +10.3% (n=33), `team_a+odds_band` +18.2% (n=12, 91.7% hit), `odds_band`-only +6.9% (n=75), short-odds away favourites **15/15 won** (+~15%). The 2026-06-27 "aggressively veto away favourites" thesis is contradicted by the counterfactual ledger.
5. **Gate-unit change is still the best lever:** pooling evidence at **source level** walk-forward fires 19/71 days (+3.9% leg ROI, +4.7% acca2); excluding betexplorer/scoutingstats legs: **17 days, +7.0% legs, +31.9% acca2 (22 tickets, 72.7% hit)** — probation-grade, not proof (Wilson 90% LB ≈ 0.55 vs 0.50 needed).
6. **Forebet is NOT dead (corrected):** live voting recovered on 2026-08-21 via the qualified Jina relay (19–30 votes/day since). What remains stale is the **deep history cache** (`forebet.csv.gz`, `statarea.csv.gz`, `zulubet.csv.gz` all end 2026-06-12) — a mining-depth issue, not a live-capture failure. See §6.

---

## 2. Why the tickets stopped firing — the exact chain

Gate (`scripts/auto_tickets.py`): each (rule × odds_source) combo needs n≥15 settled, lifetime ROI ≥ +3%, last-20 ROI ≥ 0, newest settle ≤ 30d, Wilson LB ≥ 0.50.

**Reconstructed per-day for all of August:** on every day 08-01 → 08-28 the *only* passing combo was `ml-meta avg_p>=55` × `bzzoiro_odds`.

Typical day (08-27: 7 playable-bucket picks → 0 pass-combo hits):

| stage | what dies | evidence |
|---|---|---|
| bucket / quarantine | CAUTION, suspect-price excluded | CAUTION −9.2% (n=128) — correct |
| combo ROI ≥ +3% | betexplorer combos | betexplorer source ROI −0.2% (n=195), last-20 −9% |
| combo ROI ≥ +3% | scoutingstats combos | scoutingstats source ROI −12.8% (n=125) — worst |
| n ≥ 15 per combo | forebet_best | +8.0% lifetime (n=52) fragmented across 14 rules → no single cell reaches n=15 |
| freshness ≤ 30d | zulubet | last settled 08-12; ROI −2.5% anyway |
| leg supply | bzzoiro `ml-meta avg_p>=55` | Aug: 83 bzzoiro picks → 57 playable → **21 carry the passing rule** (~0.8/day) |

The 08-09 ✅✅ / 08-13 ❌ slips came from this stream's one hot week (08-12→08-17: 2–5 legs/day). Walk-forward, the status-quo gate fired **4/71 days** and its fired legs went **−4.6%** OOS — the passing combo is passing on ~35 picks of momentum, not a deep edge.

Why legs are structurally scarce (2026-08-04 funnel receipt, HANDOVER): only **15 fixtures/day reach 2+ valid 1X2 voters, 6 reach 3+**; Forebet was solo-voter on 116/128 valid rows. Consensus edges need voter overlap, so small daily pools are architectural, not a bug.

---

## 3. EVERY bucket — the full audit (settled picks, flat 1u)

| bucket | priced n | hit | ROI | unpriced n | hit |
|---|---|---|---|---|---|
| SKIPPED_VETO | 296 | 75.0% | **+2.7%** | 5 | 80.0% |
| CAUTION | 128 | 60.2% | **−9.2%** | – | – |
| WATCHLIST_UNCORROBORATED_PRICE | 44 | 72.7% | +1.5% | – | – |
| WATCHLIST_UNKNOWN_CTX | 31 | **87.1%** | **+4.3%** | – | – |
| WATCHLIST_NO_ODDS | 0 | – | n/a | 29 | **75.9%** |
| CERTIFIED_CLEAN | 16 | 50.0% | −28.3% | – | – |
| WATCHLIST_SUSPECT_PRICE | 4 | 75.0% | −9.2% | 1 | 0% |

Notes:
- **SKIPPED_VETO is the single biggest pool and mildly positive** — but fading: Jun +18.3% (n=14) → Jul +6.1% (n=88) → **Aug +0.1% (n=194)**. It is converging to break-even like everything else.
- **WATCHLIST_UNKNOWN_CTX is the best small bucket** (87.1% hit, +4.3%); Jul +6.5% → Aug +1.9% — also fading, and already inside the playable set. The Addendum-27 resolution overlay's shadow sample is still tiny (UNKNOWN_CTX with verdict field: ALLOW 4, CAUTION 6, VETO 3 — far below the pre-committed n≥30 gate).
- **WATCHLIST_NO_ODDS** carries real predictive signal (75.9% hit on 29 graded) — a pricing candidate pool, not a betting pool.
- **CERTIFIED_CLEAN's −28.3%** is a pre-08-10 artifact (decay-aware bucketing fixed the optimistic stamping; the bucket now must be earned).

### 3a. Veto-reason decomposition — what the veto is throwing away (counterfactual)

Protective vetoes (keep them):

| veto reason | n | hit | ROI |
|---|---|---|---|
| team_h | 47 | 68.1% | −4.2% |
| league | 15 | 60.0% | −15.4% |
| team_h+team_a | 14 | 50.0% | **−28.0%** |
| team_h+odds_band+team_a etc. | 4–11 | 50–82% | −7.7% to −26% |
| niche | 3 | 33.3% | −43.3% |

Value-destroying vetoes (they discard winners):

| veto reason | n | hit | ROI |
|---|---|---|---|
| odds_band only (≥1.25 sniper rule) | 75 | 80.0% | **+6.9%** |
| team_a only | 33 | 72.7% | **+10.3%** |
| team_a+odds_band | 12 | 91.7% | **+18.2%** |
| short-odds away favourite (1.05–1.28) | 15 | **100%** | +5% to +28% each |
| unlabelled skips (pre-08-10 certified era) | 40 | 82.5% | +15.0% |

Honesty: 15/15 at avg ~1.15 odds is p≈0.13 under the implied rate — suggestive, not proof. But three independent away-side cuts all pointing +10–18% with n≈120 combined is a real pattern, consistent with the 08-05 addendum's finding ("the 3 out-of-scope short-sniper picks ALL WON, +16.7%").

### 3b. Price-evidence and bucket × source cuts

| price_evidence | n | hit | ROI |
|---|---|---|---|
| (none) | 189 | 75.7% | +0.6% |
| BETEXPLORER_RESCUE | 131 | 70.2% | −1.9% |
| SCOUTINGSTATS_SOLE | 98 | 65.3% | −7.0% |
| BZZOIRO_PRIMARY | 74 | 66.2% | −1.6% |
| SOURCE_FALLBACK | 18 | 77.8% | +15.9% |
| SUSPECT_ALIAS_FUZZY | 9 | 77.8% | −1.2% |

Bucket × source (n / ROI): **SKIPPED_VETO × forebet_best +16% (n=30)**, × bzzoiro +9% (n=73), × betexplorer +4% (n=114), × zulubet +6% (n=15), × scoutingstats **−14% (n=64)**. CAUTION × scoutingstats −61% (n=14). The veto-bucket × good-source cell is the richest vein in the ledger — which is exactly what a source-level ticket gate would unlock.

---

## 4. Walk-forward backtest of alternative gates (71 days)

| strategy | fireable days | legs | leg hit | leg ROI | acca2 tickets | acca2 ROI |
|---|---|---|---|---|---|---|
| **status quo (rule×source)** | 4 / 71 | 19 | 68.4% | **−4.6%** | 5 | −27.0% |
| rule-family pooled | 1 / 71 | 4 | 50.0% | −42.2% | 1 | −100% |
| source pooled | 19 / 71 | 79 | 75.9% | +3.9% | 27 | +4.7% |
| **source pooled, betexplorer+scoutingstats legs excluded** | **17 / 71** | 63 | 77.8% | **+7.0%** | **22 (72.7% hit)** | **+31.9%** |

OOS legs in the best variant: bzzoiro +7.9% (n=43), forebet +5.2% (n=20). **Honesty:** 22 tickets → Wilson 90% LB on hit ≈ 0.55 (need >0.50); it is also the best of four variants (selection bias inflates). Probation-grade.

---

## 5. Recommended course of action (rev 2)

1. **Do not lower the ROI/n gates.** Everything failing them is negative-EV. Forcing tickets converts silence into bleed.
2. **Change the gate unit from (rule×source) to source level** (n≥15–20, ROI≥+3%, last-20≥0, fresh≤30d, Wilson LB≥0.50 at source level, same bucket/quarantine filters). Un-benches forebet_best (+8%, currently failing only on sample fragmentation) and bzzoiro. Fireable days go ~0.4/week → ~2.5–3/week.
3. **Leg filter: bzzoiro + forebet legs only** while their OOS record accumulates; scoutingstats never rides (−12.8% source, −14% even inside the veto bucket); betexplorer prices but never rides (−0.2%, last-20 −9%, −8.1% OOS legs).
4. **Kill or halve the 10-odd acca** until CLV turns positive (highest-variance, lowest-EV component; graded n=1).
5. **Audit the away-side and odds-band vetoes through the pre-committed counterfactual process** (`scripts/counterfactual_veto_resolution.py`, Addendum 27 discipline — thresholds fixed in advance, no mood edits). The `team_a`/`odds_band`/away-favourite vetoes are discarding the +EV half of the veto bucket. This is the only place in the ledger with a consistent +10–18% counterfactual signal. Do NOT just delete the vetoes — run the gate.
6. **Probation sizing:** cap at ~19% of capital (3 × ~4.7% acca2, no 10-odd) for the first 30 graded tickets, then review vs the backtest.
7. **Make CLV the KPI.** At 519 settled picks ROI says break-even and CLV says no edge. If beat-rate stays <30% with ~0 delta after another ~300 picks, the fix must come from price capture, not slip structure.

## 6. Supply-side status — CORRECTED (was wrong in rev 1)

**Rev 1 said:** "forebet/statarea/zulubet capture stale since 06-12 — your best source is firing on fumes." **That was wrong.** The HANDOVER 08-20 addenda + today's data show:

- **2026-08-20 run #502** fixed the sentinel bug that had starved heavy capture (morning baselines missing 08-15→08-20, monthly caches stuck at 08-04/06); 11/12 monitored caches refreshed.
- **Forebet on GitHub runners** was provider-blocked; browser-TLS fallback failed (run #503 → latency containment), then a **Jina Reader relay was qualified byte-identical and deployed**. Receipt in the ledgers: forebet votes 0/day 08-16→08-20, then **19–30/day from 08-21**; forebet_best-priced picks resumed 08-21. Forebet is live and voting.
- **What is still stale today:** the deep history files `forebet.csv.gz`, `statarea.csv.gz`, `zulubet.csv.gz` end **2026-06-12** (tripwire still flags all three). These feed warehouse/mining/calibration *history* — not live voting, and not the auto-ticket gate (which accrues from settled pick ledgers, and those are current). The relay addendum left "monthly-cache confirmation" pending the next heavy run; it has not landed. Action: one investigation into why the heavy run's cache refresh isn't extending those three files — a mining-depth repair, not an emergency.
- Forebet legs are scarce (~0.85/day) mainly because of **fixture-key overlap** (solo-voter on 116/128 rows, 2026-08-04 funnel receipt), not capture.

## 7. What NOT to do

- Don't whitelist sources by name without the ROI gate (scoutingstats and betexplorer both fail as legs).
- Don't re-add CAUTION/SUSPECT buckets (−9.2% and worse).
- Don't delete the home/league/niche vetoes (they are protective); don't keep the away/odds-band vetoes on faith either — gate them.
- Don't chase the >2.00 odds band (+33% on n=14 is noise).
- Don't read "NO EDGE TODAY" as a malfunction to fix by betting more.

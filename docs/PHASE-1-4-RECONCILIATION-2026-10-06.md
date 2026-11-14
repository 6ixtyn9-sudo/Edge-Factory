# Phases 1–4 reconciled against HANDOVER.md and docs/operator — 2026-10-06

**Status: STOP-WORK NOTICE on Phases 1, 3, 4. Phase 0 done. Phase 2 reduced to
one shipped item; the rest of Phase 2 rests on a false premise.**

The one-shot handoff prompt (`docs/_handoff_prompt_2026-10-06_oneshot.md`) and
the diagnosis it derives from (`docs/diagnosis_no_autobets_2026-10-06.md`) were
written from the CI log and the source tree. Neither was checked against
`HANDOVER.md` or `docs/operator/`. Having now read those, **most of Phases 1–4
is either explicitly prohibited by a standing operator constraint, or was
already measured and refuted by a pinned checkpoint.** Executing the prompt as
written would have reverted deliberate decisions while reporting it as repair.

This document is the reconciliation. Each phase is judged against the governing
record, with the citation.

---

## Standing constraints the prompt did not account for

From `docs/operator/README.md` (§ "Standing constraints", unchanged by any
document in that tree):

> no proxies / stealth / CAPTCHA bypass; `EDGE_FACTORY_FOREBET_BROWSER=off`;
> `scripts/auto_tickets.py` is the sole owner of tickets and staking;
> **abstention is valid**; single production lane; no `edge >= 0` hard gate;
> **no production re-mine without explicit operator promotion**; gap-only
> mining.

From the 2026-10-02 strategy directive (`HANDOVER.md`):

> gate price quality now (C), recalibrate next (B), no hard edge gate until
> calibration is fixed; **no re-mine until the input layer is repaired**;
> one-lane production; **shadow re-mine only after provenance/regime splits
> exist**.

And, most directly:

> **A no-bet day is a valid, successful outcome.** `NO BET TODAY` and
> `insufficient_voter_quorum` are results, not failures. Nothing may be
> relaxed — not price corroboration, not the kickoff guard, not the quorum —
> to manufacture a card.

The investigation was framed as "why no autobets, what are we missing". The
governing doctrine's answer is that **2026-10-06 producing no card is not
prima facie a defect.** One qualifying leg against `LEGS_PER_ACCA=2` is the
abstention contract working. That reframes everything below from "restore the
bets" to "is any individual gate wrong, on evidence".

---

## Phase 0 — reproduce · DONE, matches exactly

Re-ran the rejection breakdown against live `localdata/` with the venv rebuilt:

```
MIN_LEG_ODDS 1.2 LEGS_PER_ACCA 2 MIN_ACCAS 1 MAX_ACCAS 2
Argentina v Benin       1.01 betexplorer_odds   -> min_odds_floor
England   v Czech Rep.  1.13 theoddsapi         -> min_odds_floor
Albania   v San Marino  1.03 betexplorer_odds   -> min_odds_floor
India     v Uruguay     1.03 betexplorer_odds   -> min_odds_floor
Croatia   v Spain       1.28 theoddsapi         -> None          <-- sole qualifier
Angola    v Malawi      1.36 scoutingstats_odds -> price_source_not_execution_eligible
Algeria   v Niger       1.22 scoutingstats_odds -> price_source_not_execution_eligible
Grenada   v Bonaire     1.61 scoutingstats_odds -> price_source_not_execution_eligible
```

Zero drift from the snapshot in the prompt. Note the three `scoutingstats_odds`
legs are **quarantined by design** (`PRICE-SOURCE-ROLES.md`: audit-only price,
"may print a ticket price? **no**"), and the containment that put them there is
the 2026-10-02 item-3 stale-board fix — the board stopped refreshing
2026-09-04 and the adapter fabricated `captured_at` from kickoff. Those three
legs are not lost coverage; they are a stale feed being correctly refused.

---

## Phase 1 — re-anchor the consensus views · DO NOT SHIP

**Finding stands, remedy prohibited.** The mismatch is real and I confirmed it
at source level:

- `warehouse.py:370-445` — `consensus2 = forebet ⋈ zulubet`, `consensus3 = +
  statarea`, `consensus4 = + vitibet`.
- `assay_purity.py:175` / `decay_monitor.py:84` —
  `v_consensus2 = SELECT *, fb_pick AS pick FROM consensus2`. **The certified
  pick is literally Forebet's pick** and the join requires a Forebet row.
- `picks_today.py:4346` — serve side calls `thr_for(len(used), t1x2)`, keyed on
  the **count** of voters, not their identity; `avg_p = mean(ps)` over whichever
  of the six `SOURCES_1X2` showed up.

So `2way-unanimous avg_p>=70` is certified on forebet×zulubet and served on any
two voters. Post-2026-06-12 it is never forebet×zulubet.

**Why it must not be "fixed" here.** Re-pointing or re-naming those views
forces recertification of every rule — that is a production re-mine, which
`README.md` forbids without explicit operator promotion and the 2026-10-02
directive defers until the input layer is repaired. The views are also
*deliberately* legacy; the comment says so in the code
("retained for historical rule continuity"), and the designed replacement
already exists: the 2026-09-30 addendum shipped weighted consensus that
"accepts probability-only voters such as Statarea and Vitibet … and requires at
least two votes on each fixture", with all rules still passing the unchanged
walk-forward / Wilson-LB / ROI gates. A non-Forebet path is built. The open
question is promotion, which is the operator's call, not a refactor.

**What is legitimately missing:** nothing stops someone *measuring* the
estimator gap read-only and reporting it. That is a worthwhile next step and
needs no promotion. It is not what the prompt asked for.

---

## Phase 2 — price triage · PREMISE IS WRONG; one item shipped

The prompt says the price famine is dead feeds plus TheOddsAPI league-key
coverage, with ~96% of quota idle. **The receipts say the binding constraint is
the fixture JOIN, not supply and not quota.**

`docs/operator/PRICE-COVERAGE-IMPLEMENTATION-2026-10-04.md`, from
`source_health_2026-10-03.json`:

```
betexplorer  be_raw=21     be_usable=21     be_matched=0
oddspapi     op_raw=30468  op_usable=30022  op_matched=0
             join_miss_counts: market_unsupported=10820 out_of_window=19202
theoddsapi   oa_raw=589    oa_usable=589    oa_matched=0
```

30,022 usable OddsPAPI rows and 589 usable TheOddsAPI rows matched **zero**
fixtures. Prices are arriving in volume and failing to join. Adding league keys
buys more unmatched rows.

The league-key theory is independently refuted by
`PRICE-COVERAGE-2026-10-04.md`, which shows **0.0% ever-priced** for
mainstream competitions TheOddsAPI certainly carries — `Sc1` (Rangers vs
St Mirren, 15 picks), `Germany Bundesliga` (Bayern vs Stuttgart), `Cz1`
(Sparta Praha), `Gr1` (PAOK), `It2` (Palermo), `Jp1`, `L1`, `L2`. If this were
a key-coverage gap those would be priced. It is an identity/window problem —
precisely what `JOIN-REPAIR-2026-10-03.md`, `JOIN-REPAIR-ROUND-2.md`,
`IDENTITY-COLLISION-AUDIT-2026-10-05.md` and
`FIXTURE-IDENTITY-SPLIT-2026-10-05.md` have been working through. The last of
those landed 2026-10-05, one day before the no-bet day, and re-keyed every
team normalizer (`norm_team("Türkiye")` was `"trkiye"` — diacritics deleted,
not transliterated).

**Cap increases are already declined, with reasoning**, in the same doc:
BetExplorer's ceiling was *already* raised to 24 (default 12, proposed secret
18); OddsPAPI was explicitly left at 20 because "raising 20 → 40 before
improving exact slate/provider overlap would mostly buy provider-order
leftovers"; TheOddsAPI got no increase because quota was never binding — the
real unknown was why auto mode marked only 2 of 24 shortlist fixtures due, and
`skip_reasons`/`due_reasons` were added to find out. The prompt's items 2 and 3
would re-litigate a decision made on better evidence than the prompt had.

**`forebet_best` is not a bug.** `PRICE-SOURCE-ROLES.md` lists it as a
first-class role — "Historical source fallback · may print a ticket price?
**no by default** — explicit opt-in only" — gated by
`EDGE_FACTORY_ALLOW_SOURCE_FALLBACK=0`, "default is abstain". The 72 rejections
are the abstain contract executing. Removing the label would delete a
deliberate, documented signal.

### Shipped: `8f992d6` — the one item that survives

`known()`/`spec()` disagreement, exactly as the prompt described it and with
the prompt's own "~0 legs, diagnostic honesty" framing.

- `price_sources.resolvable()` added — `REGISTRY ∪ VOTE_ONLY_SOURCES`.
  `known()` deliberately **not** widened: its five other callers (picks_today
  donor ranking, scored_candidate_shadow provenance) mean "is in REGISTRY".
- `auto_tickets.py:1570` now gates on `resolvable()`, so `zulubet`, `statarea`,
  `vitibet`, `betclan` log `price_source_not_execution_eligible` instead of
  `price_source_unregistered`.
- 14 tests, verified load-bearing (4 fail against the old predicate).
  `test_relabelling_recovers_zero_legs` pins that no leg became playable.
- Full suite **1400 passed**.

---

## Phase 3 — retrain ml-meta without the leakage features · PROHIBITED

**This was measured two years of ledger-time ago and the verdict is pinned.**
`HANDOVER.md:7077` — *"checkpoint ⑫ — the ml-meta train/serve mismatch.
MEASURED. Verdict: real defect, benign direction, **DO NOT "fix" it blind**."*

The leakage finding is correct and already documented there line-by-line
(`ht_diff +0.2395`, `ht_total +0.1910`, computed live as 0 before kickoff).
What the prompt missed is the measurement that followed:

| scope | ml-meta | 2way-unanimous |
|---|---|---|
| in-season playable | n=277, +5.2pp under-confident, ROI +0.0% | n=132, +2.5pp, −1.5% |
| legs that rode | n=81, realised **75.3%**, ROI **+7.0%** | n=79, 70.9%, **−6.0%** |

The features are **constants at serve, not noise** — their coefficients drop
out of the logit and the other 24 features carry the ranking. The damage is to
*calibration*, and it is one-directional: the model **understates** itself, by
+1.8pp at the 55–60 band rising to +14.4pp above 70. So `>=55` is admitting
matches whose true win rate is ~67%.

> **Removing `ht_diff`/`ht_total` and retraining, without re-tuning the
> threshold, would most likely make live performance WORSE.** A correctly
> calibrated model would raise its stated probabilities to match reality, and
> `>=55` would then admit a wider, weaker set of matches than it does today.

The prompt instructs exactly the prohibited action: retrain, drop the features,
report the new baseline. Two standing prohibitions apply verbatim —
*"Do not retrain silently. A retrain without a threshold re-derivation is a
live behaviour change disguised as a bug fix."*

The sanctioned path is four steps, and step 3 is **shadow both models for
n ≥ 60 in-season bet-days** before pricing. It also cannot be shortcut by
backtest: checkpoint ⑪ (Ground 4) found *"the warehouse cannot replay ml-meta
at all"*, so a retrained model **can only be judged on new live bet-days**.

There is no honest offline deliverable here. The prompt's acceptance criterion
— "report the honest, serve-realistic baseline" — is not obtainable by the
method it specifies.

---

## Phase 4 — decay-monitor redesign · BLOCKED ON DATA, AND ON PHASE 3

The statistical criticism is sound: with baseline n≈2678 and recent n≈123 the
second clause of `r_p < b_lb and r_lb < 0.90·b_lb` is nearly free, so the test
collapses to a one-sided comparison that double-counts uncertainty, and
`should_bench()` has no symmetric rescue for strongly positive ROI.

But the prompt requires "backtest against full settled history using the
Phase-3 honest baseline". Both inputs are unavailable:

1. **Phase 3 cannot produce that baseline** (above).
2. **The settled history stops.** `SOURCE-TRIAGE.md` TR-1 (HIGH): *"all
   committed prediction series (forebet/zulubet/statarea) end 2026-06-12"*.
   I confirmed the archives on disk — `forebet.csv.gz`, `zulubet.csv.gz`,
   `statarea.csv.gz` — and there is **no `warehouse.duckdb` in the checkout**
   at all; it is runner-cache only. `vitibet` has no committed series (TR-2).
   A decay backtest run here would grade a pre-June world with the two current
   live voters partly missing.

Additionally the dependency is circular as written: decay baselines are
computed from the certified stats that Phase 1 would change, and Phase 1 is
prohibited.

---

## What I recommend instead

Ordered by value per unit of risk, all inside the standing constraints:

1. **Treat the JOIN as the price problem.** The instrumentation already exists
   (`coverage unmatched_causes: never_attempted / attempted_no_quote /
   quote_not_joined`). Pull one production run's receipts and attribute the
   30,022 unmatched OddsPAPI rows. This needs no promotion, no cap change and
   no new credentials, and it is where the legs actually are.
2. **Measure the Phase-1 estimator gap read-only** and report rule-by-rule
   certified-view vs served-view. Produces the evidence an operator would need
   to authorise a re-mine, without performing one.
3. **Re-derive the decay test offline as a proposal with synthetic power
   curves**, not a backtest — honest about the data gap, no code shipped.
4. **Leave ml-meta alone** until someone funds the 60-bet-day shadow.

None of these is "restore live auto-betting this session". On the governing
evidence, that outcome was not available this session, and the abstention on
2026-10-06 was the system behaving as designed.

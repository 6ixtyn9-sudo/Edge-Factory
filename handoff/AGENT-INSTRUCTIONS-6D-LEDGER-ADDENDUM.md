# Edge Factory — round 6D addendum: the measurement ledger vs the certification ledger

**Recorded in-repo 2026-10-12 from the round-6D relay text as received in the operator's
message (same day, 20:36 local).** Items 1–3 of §3 are **proposals awaiting the operator's
ruling** — nothing in shipped behaviour changes until that ruling lands, and per §Status it
must not block the R3 proof, the `w6` re-run, or the R4 handover.

**From:** the reviewer (operator's side) · **Date:** 2026-10-12 · **To:** the agent
**Status:** small, additive, **must not block** the R3 proof, the `w6` re-run, or the R4 handover.

## 1. The operator's question, measured

Operator: *"the system has way way way more enhanced measurements than what i see here, everyday i
get to see them when i look at picks performance, howcome you see so less? is it because those are
not priced? you dont need price to see the hit rate though"*

**Yes — and the gap is now measured.** Two different ledgers:

| Ledger | What it counts | Size |
|---|---|---|
| **`audit_recent_picks.py` performance view** (`enh_stats["by_enhancement"]`) | **every enhancement recommendation**, priced or not (`recommended`, `hits`, `hit_rate`, plus a priced subset `priced_n` / `priced_roi`) | 2026-08 **556** recs (127 priced) · 09 **861** (170) · 10 (13d) **310** (90) |
| **`localdata/enhancement_registry.json`** | **priced settled outcomes only** — the certification ledger the floors derive from | **409** records, all priced (`processed` == `records` == `n` == 409) |

The reason is one line of caller code: `for oc in priced_outcomes:` (`audit_recent_picks.py` ~1981).
The registry module itself **supports** unpriced outcomes — `record_outcome` appends them to
`processed` and never lets them advance certification ("Unpriced outcomes NEVER advance
certification: probability without price is not evidence") — but the caller filters before calling,
so the registry has never seen one.

**The operator is right that hit rate does not need a price.** The performance view already computes
it over all ~1,700 recommendations; the registry is blind to ~78% of them.

## 2. Why the gap is mostly not fixable by wiring alone (measured, October, 13 days: 310 recs / 90 priced)

| label | recs | priced | % |
|---|---|---|---|
| Match Over 2.5 Goals | 115 | 66 | 57% |
| **Away Team Under 3.5 Goals** | 99 | **0** | 0% |
| **Home Team Under 3.5 Goals** | 31 | **0** | 0% |
| Match Over 3.5 Goals | 19 | 11 | 58% |
| **Home Team Over 0.5 Goals** | 16 | **0** | 0% |
| **Away Team Over 0.5 Goals** | 14 | **0** | 0% |
| Match Over 1.5 Goals | 8 | 5 | 62% |
| team-total unders (2.5/1.5), Match Over 4.5 | 8 | 8 | 100% |

The unpriced tail is dominated by **team-total markets** — and BetExplorer has no tab for those (its
tabs are 1x2 / OU / AH / DNB / DC / BTTS). Match-level over/under labels get priced ~57–62%; team
totals essentially never (two exceptions in the whole registry, both 2026-10-04). So a large share of
those "missing" measurements **cannot become priced evidence from the current price source at all** —
they are hit-rate-only, permanently, unless a new source carries team totals (a separate operator
decision, out of scope here).

## 3. The addendum work (report-only; certification untouched)

1. **Record unpriced settled outcomes too**, through the registry's existing `processed`-only path —
   a `record_outcome(..., price=None, ...)` call for each settled recommendation that had no price.
   Guardrails: `n`, `hits`, `records`, `profit`, `inv_price_sum` and every status transition must be
   **byte-identical** before/after on the committed registry; `processed` grows by exactly the
   unpriced keys; state the `MAX_PROCESSED_KEYS` trim in the proof. Add a test that an unpriced
   outcome never moves a status.
2. **Reconcile the two numbers in one place**: print, per label, `recommended` vs `processed` vs
   `priced_n` and the delta, so the performance view and the registry can no longer diverge silently.
3. **Label the never-priceable class** in the performance view (`team_total` label class → "no price
   source; hit-rate only") so nobody waits for those to graduate.
4. **Say it in the PR body, one line:** the registry is the *certification* ledger (price required, by
   design); the performance view is the *measurement* ledger (price not required). Both are correct;
   they measure different things.

**Not in scope**: pricing team totals, changing certification gates, or re-deriving any floor from
unpriced history. Floors still come only from realised (hit, price) pairs — the over_15 lesson stands
(72.7% hit, −5.78u).

## 4. Does this change the round-5 verdict?

No — but it strengthens the record. The signal test ran on the 409 priced; a hit-rate-only question
(does form/H2H move the hit rate?) could now run on the full ~1,700 with more power, at zero network
cost. If you can do that cheaply **after** the handover, note it as a follow-up; do not hold the
dispatch for it.

# Veto Re-Mine — Design Doc (v0.1, REVIEW ONLY — no decision made)

Date: 2026-08-05 · Status: **design-first step per Addendum 19 #2**. Nothing in
this doc authorizes a code change. It defines the problem, the evidence, the
candidate approaches with tradeoffs, the guardrails, the success metric, and
the open questions that must be answered before any implementation.

**Updated 2026-08-05 (evening):** open questions Q1–Q5 resolved by an
independent second-agent review (section 10) and independently cross-checked
against the live repo (section 10.2). Phase 0 parameters are locked pending
operator sign-off.

---

## 1. Problem statement

Purity context verdicts gate picks (VETO blocks, ALLOW/BOOST passes, CAUTION
warns, **UNKNOWN → watchlist/skip**). UNKNOWN is the structural cause of empty
certified buckets: on 2026-08-03 the night run produced **0 certified, 14
vetoes / 417 matches**. The 2026-08-05 audit shows the same shape in the
30-day window:

| bucket | settled | wins | hit rate | ROI |
| --- | --- | --- | --- | --- |
| `SKIPPED_VETO` | 71 | 60 | 0.845 | +0.092 |
| `WATCHLIST_UNKNOWN_CTX` | 19 | 17 | 0.895 | +0.061 |
| `WATCHLIST_NO_ODDS` | 5 | 4 | 0.800 | — |
| `CAUTION` | 33 | 18 | 0.545 | −0.123 |

Interesting and important: the UNKNOWN-adjacent surface (WATCHLIST_UNKNOWN_CTX)
has been *profitable* (17/19, +6.1%) in this window — evidence that UNKNOWN is
currently **throwing away good picks**, not protecting against bad ones. This
is exactly why the re-mine must be evidence-led: it is not obviously "loosen
UNKNOWN" (which could manufacture yield that then reverts), it is "resolve
UNKNOWN with pooled evidence and verify walk-forward."

## 2. Current evidence (2026-08-05 registry, generated 11:06Z)

`purity_registry.json`: 36,490 context cells across 5 dimensions.
`window_days = 36500` (i.e., full history; `recent_roi` is the recent window).

| dimension | total | UNKNOWN | UNKNOWN % | ALLOW | BOOST | CAUTION | VETO |
| --- | --- | --- | --- | --- | --- | --- | --- |
| league | 4,219 | 3,175 | **75%** | 400 | 11 | 136 | 497 |
| niche | 9,880 | 8,995 | **91%** | 238 | 203 | 43 | 401 |
| team | 22,279 | 19,346 | **87%** | 1,245 | 10 | 244 | 1,434 |
| odds_band | 97 | 24 | 25% | 19 | 6 | 12 | 36 |
| competition_type | 15 | 2 | 13% | 2 | 2 | 7 | 2 |

## 3. Current verdict mechanics (why UNKNOWN happens)

`src/edgefactory/assay.py` — league verdict (`context_verdict_league`):

- `roi is None` → **UNKNOWN** (no priced settled bets in the cell)
- `n < 12` → **UNKNOWN**
- `12 ≤ n < 40` early gates: VETO if roi ≤ −0.10 · CAUTION if ≤ −0.04 ·
  ALLOW if ≥ +0.01 · else **UNKNOWN** (roi ∈ (−0.04, +0.01))
- `n ≥ 40` standard: VETO if roi ≤ −0.05 and recent ≤ −0.03 · CAUTION if roi
  < 0 or recent ≤ −0.05 · BOOST if n ≥ 100 and roi ≥ +0.03 and recent ≥ 0 ·
  else ALLOW

Team verdict: n<8 UNKNOWN, 8–24 early, ≥25 standard. Odds-band: 20–59 early.
Niche: parallel to league. So **UNKNOWN = thin n (n<12/8/20) or a mid-zone ROI
with no verdict, or no priced ROI at all**. Most league UNKNOWN cells are the
n<12 / no-ROI case: individual rule×odds-band×role cells are too fine-grained
to accumulate n alone.

Certification context (edges_consensus.json, 2026-08-05): **11 certified + 19
candidate** edges; gates `min_n_train 340, min_n_valid 120, split 2025-06-01,
recent_window 60d`. The certified edge count recovered (older baseline
9/1/8); the *pick-day yield* is still limited by context UNKNOWN vetoes.

## 4. Candidate approaches (options, not decisions)

### O1 — Evidence pooling across edges per league (Addendum 19 direction)
Pool the existing per-cell records within a league **across rule and odds-band
(not across home/away role)** to build a league-level n/roi/recent_roi, then
apply the same verdict gates. A cell at n=7 × 4 rules becomes n=28 — above the
n=12 floor, into the early-gate zone, and for strong leagues past n=40.

- Pros: uses existing settled evidence; no new capture; directly raises n.
- Cons: pools heterogeneous rules (an edge with −30% ROI can hide inside a
  league pool); dimension bleed is the exact failure that forced the niche
  dimension. Must pool *per side_role* and gate pooling by homogeneity
  (e.g., only pool when per-rule cells agree in sign, or weight by n).

### O2 — Hierarchical fallback: league → niche → competition_type (direction)
Resolve UNKNOWN by consulting the next broader dimension: if the league cell is
UNKNOWN, fall back to the niche cell; if that is UNKNOWN, to competition_type.
**Directional and monotone:** only UNKNOWN may be resolved; a VETO at any
upstream level is never downgraded by a broader ALLOW (VETO wins over
everything); specific wins over broad (a non-UNKNOWN specific verdict is never
overridden).

- Pros: principled; directly uses the dimension stack; reversible.
- Cons: niche is 91% UNKNOWN — the fallback often skips to competition_type
  (only 15 cells, mostly ALLOW/CAUTION) — so the fallback ladder is short in
  practice today; competition_type ALLOW is a weak signal (2 cells).

### O3 — Longer / smarter windows
Registry already uses full history (36,500d). The real lever is the **recent
window**: `recent_roi` is None below 30 recent bets. Pooling (O1) also lifts
recent n. No separate window change is proposed; O1/O2 subsume this.

### O4 — Per-trigger counterfactual (Phase 0 — measurement FIRST, mandatory)
For every pick that was skipped/watchlisted due to UNKNOWN context, compute
counterfactually what each candidate resolution (O1 pool, O2 fallback) *would
have* verdict-ed it, then score against settled results. Deliverable: a
read-only report — "if we had resolved UNKNOWN via O1/O2 with parameters P,
the 30-day window would have added/rejected X picks at Y hit-rate/ROI."
Addendum 8's deferred "per-trigger counterfactual on SKIPPED_VETO" is this.

- Pros: zero risk; converts "3,175 UNKNOWN" into a concrete decision table;
  is the walk-forward evidence base for any parameter choice.
- Cons: needs settled results joined to vetoed picks (available: veto_reason
  confirmed present in archived slates ≥ 2026-07-21; settled_results.json).

**Recommendation (for operator approval): O4 first, then O1+O2 as a
resolution layer evaluated by O4's harness — not a registry re-mine.** A
resolution layer (compute fallback verdict on the fly) is reversible and
auditable; a registry re-mine bakes a choice into stored data and is harder to
unwind. No decision is made in this doc.

## 5. Guardrails (non-negotiable, carried from Addendum 19 / golden rules)

1. **Never relax verdicts to manufacture yield.** Yield is the success
   *metric*, never the *method*.
2. **UNKNOWN is the only resolvable state.** VETO/CAUTION/ALLOW/BOOST at a
   specific level are never overridden by broader evidence. Monotone veto.
3. **Role separation:** pool within home/away role only (context keys carry
   `side_role`); never pool across roles.
4. **Walk-forward only.** Any proposed resolution is measured on
   post-2025-06-01 validation data, never on a mini-backtest of the same
   window that motivated it.
5. **Wilson lower bound, never raw hit rate**, for any threshold decision.
6. **ROI alongside hit rate, always.**
7. **Registry stays the single source of truth** for stored verdicts; the
   resolution layer is a transparent overlay, logged per pick (verdict + basis
   + evidence n), never silent.
8. **Entity-overrides proposals wait** (Lithuania 1 Lyga, Sweden Allsvenskan):
   they are the first consumers of the counterfactual table, not a substitute
   for it.

## 6. Success metric & stop conditions

- **Primary:** walk-forward delta in *certified picks/day* (baseline: settled
  ≈128 picks/30d ≈ 4.3/day, SKIPPED_VETO 71 of them) — measured on the
  post-split window with the counterfactual harness, not vibes.
- **Co-requisites (all must hold, else STOP):** newly-resolved picks do not
  drag window hit rate below the certified-edge Wilson lower bound; their ROI
  ≥ 0 over ≥ 30 settled outcomes; no VETO was downgraded anywhere; the
  UNKNOWN-resolved surface's realized performance matches the counterfactual
  within tolerance (±5pp) after 2–3 days of live runs.
- **Stop conditions:** any of the co-requisites fails, or the resolution layer
  shows instability (verdict flapping between runs), or the harness reveals
  look-ahead leakage. On stop: disable the layer (one-line flag), audit, re-do
  the design doc.

## 7. Phases

| Phase | Deliverable | Gate to advance |
| --- | --- | --- |
| **0 — Counterfactual harness** (read-only) | Script + report: for each UNKNOWN-skipped/watchlisted pick in the window, resolution verdict under the locked O1/O2 rules (pool key `sport|league|market|side_role`, n-weighted unconditional pooling per Q2, gates ALLOW≥40 / CAUTION≥20 / VETO≥12 per Q3, O2 ladder league→niche→competition_type), scored vs settled results. Measurement on **all available settled results (2026-05-07 → now, ~3 months — the store does not reach 2025-06-01)**, operator-facing table on the **30-day slice** (per Q4). Overlay-only, registry never mutated (per Q5). | Operator reviews table; parameter ranges chosen from evidence, not priors |
| **1 — Design confirmation** | Updated doc: exact pooling rule (homogeneity test, min pooled n, role split), fallback ladder order, defaults; unit-test list. | Operator sign-off on params; no code shipped before sign-off |
| **2 — Resolution layer implementation** | `assay.py`/`picks_today.py` overlay function + tests (fixture purity registry + fixture settled results); flag-gated OFF by default (same pattern as the debias flag). | Full suite green + battery + fresh-tree rehearsal (standing protocol) |
| **3 — Ship & measure** | Payload per protocol; flag ON in CI only after 2–3 days of shadow-mode receipts; then walk-forward delta report. | Delta ≥ threshold AND co-requisites; else STOP + rollback |

## 8. Open questions — RESOLVED by second-agent review (2026-08-05)

All five questions were answered by an independent second-agent review with a
verification protocol, then independently cross-checked against the live repo
(section 10). Decisions:

1. **Pooling scope** → rule-pool within league only; competition_type only via
   O2's fallback ladder (never in O1). [HIGH]
2. **Homogeneity** → pool n-weighted unconditionally; **no sign-agreement
   requirement** (8/10 top pools are mixed-sign; disagreement is systematic —
   consensus rules vs other rule families). [HIGH]
3. **Minimum pooled n** → Scenario B: ALLOW ≥ 40, CAUTION ≥ 20, VETO ≥ 12
   (unchanged). [HIGH]
4. **Counterfactual window** → measurement on all available settled results
   (2026-05-07 → now, ~3 months — the store does NOT reach the 2025-06-01
   split); operator-facing table on 30-day slice. [MEDIUM — data thinness]
5. **Registry mutation vs overlay** → read-only overlay at pick time;
   registry untouched. [HIGH]

## 9. Risks

- **Dimension bleed recurrence** (the niche dimension exists because league
  was too broad): mitigated by role separation + sign-agreement + monotone
  veto + overlay (reversible).
- **Manufactured yield:** mitigated by guardrail 1 + co-requisite measurement
  + stop conditions.
- **Harness leakage** (using post-split results to tune pre-split rules):
  mitigated by Phase 0 using only the walk-forward split and by pre-registering
  parameters in Phase 1 before Phase 2 coding.
- **Scope creep:** Phase 0 is read-only; no assay/picks change before Phase 2.

---

*Next step when approved: build the Phase 0 counterfactual harness (read-only
script + report), which is also the first consumer of `picks_audit_rolling`
veto attribution data. No production behavior changes at any phase until the
gates above pass.*

---

## 10. Second-agent review — decisions + independent cross-check (2026-08-05)

### 10.1 Review summary (independent agent, base `6ccb18f`)

Reviewed by a second agent with a mandatory verification protocol
(recompute-everything, [VERIFIED]/[INFERENCE]/[JUDGMENT] tagging, read-only).
Snapshot: purity_registry `generated_at 2026-08-05T11:12:06Z`,
settled_results 2026-05-07 → 2026-08-04, edges split 2025-06-01.

| Q | Decision | Confidence | One-line rationale |
| --- | --- | --- | --- |
| Q1 | Rule-pool within league only; competition_type only via O2 fallback | HIGH | 15 competition_type cells, 2 UNKNOWN; cross-league ROI divergence makes direct competition-pooling harmful |
| Q2 | No sign-agreement; n-weighted unconditional pooling | HIGH | 8/10 top pools mixed-sign; disagreement systematic (consensus vs other rules); sign-agreement would starve ~80% of pools |
| Q3 | Scenario B: ALLOW ≥40, CAUTION ≥20, VETO ≥12 | HIGH | Resolves ~1,985/3,176 UNKNOWN cells (62.5%) vs 72.5% at current gates; preserves all 350 VETO pools; stricter gate fits the least-specific verdict |
| Q4 | All available settled results (~3 months) for harness; 30-day slice for operator table | MEDIUM | settled_results.json only spans 2026-05-07 → now; 128-pick window is thin |
| Q5 | Read-only overlay at pick time; registry untouched | HIGH | Registry is bot-generated daily; overlay keeps single-source-of-truth, is reversible and per-pick auditable |

Key findings the review surfaced:
- **settled_results.json only reaches back to 2026-05-07 (~3 months)** — the
  "full post-split window (14 months)" does not exist in the committed store.
  (A deeper warehouse may exist locally, but `*.duckdb` is gitignored; on a
  fresh clone only the 3-month store is available.)
- **797 of 3,176 UNKNOWN league cells (25.1%) sit in pools too small
  (n<12) to ever resolve via pooling** — these need O2's fallback or stay
  UNKNOWN.

### 10.2 Independent cross-check (performed 2026-08-05 against `6ccb18f`)

Every decision-relevant number was recomputed from the live repo. Results:

| Claim | Cross-check | Status |
| --- | --- | --- |
| League UNKNOWN 3,176 / team 19,340 (vs prompt-context 3,175 / 19,346) | recomputed: 3,176 / 19,340 | ✅ agent correct (prompt context stale by 1 / 6 — bot-regeneration drift) |
| settled_results 38,958 rows, 2026-05-07→08-04, last-30d 11,375 | recomputed: identical | ✅ |
| competition_type: 15 cells, 2 UNKNOWN | recomputed: identical | ✅ |
| competition_type n range 280–1,708 | actual: **1–27,364** (the two UNKNOWN cells are `youth` n=1 and n=4) | ⚠️ agent's n-range inaccurate; conclusion unaffected (2 tiny youth cells resolve nothing) |
| epl\|1x2\|home: 13 rules, 5 neg / 8 pos, w_roi −0.0388 | recomputed: identical | ✅ |
| it1\|1x2\|home: 13 rules, all 13 neg, w_roi −0.1141 | recomputed: identical | ✅ |
| es1\|1x2\|home: all 13 positive | actual: **11 pos / 2 neg** (v_consensus2_base −0.042, v_consensus3_base −0.040), w_roi +0.0179 | ⚠️ minor inaccuracy; qualitative point (strong positive pool) holds |
| Q3 scenario cell resolutions A 2,304 / B 1,985 / C 1,937 | recomputed: 2,301 / 1,982 / 1,934 (within 3 cells) | ✅ |
| Q3 pool-level verdict mixes (A 653 = 350 VETO + 199 ALLOW + 68 CAUTION + 36 BOOST; B 539; C 521) | recomputed: A 652 = 350 VETO + 198 ALLOW + 68 CAUTION + 36 BOOST; B 538; C 520 | ✅ within 1 pool; VETO=350 exact |
| UNKNOWN cells in pools with pooled n<12 = 797 (25.1%) | recomputed: identical | ✅ |
| Pool n-bucket distribution (n≥12: 188; ≥20: 180; ≥40: 160; ≥100: 103) | **not reproducible** under any tested definition (my counts: ≥12: 353–674 depending on definition; priced-n≥12: 663) | ❌ agent statistic unverifiable — do NOT quote; Phase 0 computes the canonical pool table itself |

**Cross-check verdict:** the five decisions are supported; three secondary
evidence items are inaccurate or unreproducible (competition_type n-range,
es1 sign split, pool n-bucket distribution). None change a decision. The
canonical pool table for Phase 0 must be computed by the harness script, not
taken from either this review or this doc.

### 10.3 Assumptions carried into Phase 0 (from the review's assumptions)

- Pool key: `(sport, league, market, side_role)` — rules pooled within; odds
  band NOT in the key (registry league dimension has no odds_band segment).
- Pooled `recent_roi = None` initially (conservative; VETO at n≥40 uses the
  `recent is None` branch). Revisit if pooled recent evidence is available.
- O2 ladder semantics: first non-UNKNOWN verdict up league → niche →
  competition_type; VETO never downgraded; specific non-UNKNOWN never
  overridden.
- The O4 harness is the source of the missing evidence for Q2/Q3 (per-cell
  pooled-vs-native performance) — no such audit exists yet.

### 10.4 Next step (pending operator sign-off)

Build the **Phase 0 counterfactual harness** (read-only script + report) with
the locked parameters above: pool table from the live registry, resolution
verdict per locked gates, O2 ladder, scored against settled results
(2026-05-07 → now), operator table on the 30-day slice, overlay-only
semantics. No production behavior change at any phase.

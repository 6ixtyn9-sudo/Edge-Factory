# NEXT-AGENT BRIEF — DRAW MINING (2026-10-07)

Forward-looking brief. Not a past-state doc. Written by the session that closed
the Fade/Draw arithmetic pass on 2026-10-07, after re-measuring every figure
below against the committed ledger. Committed on the session branch
`arena/438d7dd2-edge-factory` — see DELIVERY at the end.

**Line anchors are perishable — the landmark wins.** Anchors are `file:line`
plus a searchable landmark; several drifted by a line or two while this brief
was being written. If the number and the landmark disagree, re-resolve by
search and treat the disagreement as drift, not as a contradiction.

## MISSION

The operator asks: *"should we emit draws as well, make them part of the
system, see if they certify — because most selections die due to draws; and
should we probably remine the system if we do?"*

Answer that with measurements. **The task is almost certainly NOT "add draws to
the system"** — see PREMISES below, which were verified on 2026-10-07. A draw
that is already emitted, already graded, and already unreachable is a different
problem from a draw that is missing, and the fix is different too. Establish
which problem you actually have before proposing anything.

This mission is separate from the ticket/slate visibility brief
(`docs/operator/NEXT-AGENT-BRIEF-2026-10-07.md`, already in the tree on this
branch). The two are sequential, not overlapping — do not conflate them.

## PREMISES (verified 2026-10-07 — REFUTE THEM BEFORE BUILDING ON THEM)

All figures below are OBSERVED on `localdata/ml_fade_research_ledger.json`
(2,258 rows; 2,108 settled) as committed at `6f52b92`. Re-derive before use.

1. **Draws are already emitted as selections.** 208 ledger rows have
   `pick == "draw"`; all 208 are family `ml-meta`; 199 settled (45 win / 154
   loss); 9 pending. Date range 2026-09-20 → 2026-10-07. Today's own day
   included: Avispa Fukuoka v Yokohama FC, `pick == "draw"`, `avg_p` 26.4.
   So "emit draws as well" is already satisfied — find out why they never
   surface, do not re-implement them.
2. **The draw selection is structurally unreachable by the certified band.**
   `avg_p` across those 208 draw rows: min 10.0, **max 33.4**, mean 16.7.
   The certified ml-meta rules are `avg_p>=55/60/65/80`. A draw selection has
   never been within 21 points of the lowest certified threshold. Read the
   registry entry (`localdata/edges_consensus.json`, rule `ml-meta avg_p>=55`):
   `where: "ml_p*100 >= 55"` — a threshold on `ml_p` with **no pick
   constraint**. Draws are already admissible to the rule; the bar is what
   excludes them. Confirm this reading before you propose a schema change.
3. **The already-emitted draw picks are deeply unprofitable** at their own
   forebet price (`first_odds_forebet`): 157 priced, hit 20.4% (32 wins), avg
   price 3.51, break-even implied by those prices 29.4% (mean of 1/price),
   flat-stake ROI **−30.9%**. Every price band negative, measured on
   `[2.5,3.0)` n=19 ROI −40.0%, `[3.0,3.5)` n=77 ROI −28.7%, `[3.5,∞)` n=61
   ROI −30.8%. **Band convention: lower-inclusive, upper-exclusive** (`[lo,
   hi)`) — 12 of the 157 priced rows sit exactly on an edge (6 at 3.0, 6 at
   3.5, 0 at 2.5; draw prices cluster on short decimals, so edge collisions
   are structural, not coincidence). The opposite convention `(lo, hi]`
   moves only those 12 rows and yields 25 / 77 / 55 at −54.4% / −28.7% /
   −23.3% — **the verdict (every band negative) survives both conventions**;
   only the per-band numbers move. Any band table you publish must state its
   boundary convention, or it is not reproducible even when every figure in
   it is right. **Soft forebet prices, not execution** — redo on the
   execution-eligible path before any of this is called economics.
4. **The operator's premise needs one correction, and it matters.** Draws are
   22.0% of ml-meta outcomes (250 of 1,137) but cause **35.6%** of ml-meta
   losses (205 of 576). Restricted to side picks (home/away only), draws cause
   **48.6%** of losses (205 of 422). So "disproportionately lethal" is
   measured-true and worth acting on; "most selections die due to draws" is
   **not** supported as stated. State the correction in the report — the
   framing changes the task.
5. **The draw is excluded from the fade family by design, and the arithmetic
   closes exactly.** Settled ml-meta 1,137 = 938 binary-pick rows (every one
   paired to a fade row; 0 unpaired) + 199 draw-pick rows (every one
   fade-excluded; 0 draw picks carry a fade row). `fade.py:39-41` — `"draw"`
   is deliberately ABSENT from `INVERSE_SELECTION`: no honest binary inverse
   exists. Re-derive this decomposition; if it does not close to 1,137, your
   pairing is wrong and every number downstream is wrong.

## THE QUESTIONS TO ANSWER

### Q1. What is the current state, exactly?
Establish, with queries and counts in the report: are draws emitted (yes/no),
graded (yes/no), priced (which column), and under which rule identity. If the
answer is "already emitted", say so plainly — an "add draws" proposal written
against a system that already has them is this codebase's recurring failure.

### Q2. Why has no draw rule ever certified? Distinguish two causes.

- **(a) Unreachable threshold** — the band is calibrated for 3-way favourites;
  draws never reach it. Measurable: the max `avg_p` over draw picks.
- **(b) Negative economics** — the picks lose at the price they get.

These have opposite implications. (a) means no test has ever been run and the
question is open. (b) means it has been tested, repeatedly, and it lost.
Measure which, on the **full appraisal population** — not on the committed
ledger alone.

> **Population warning.** The certified entry carries `train.n = 4549`,
> `valid.n = 2665` (hit 68.92%, avg_odds 1.94, Wilson LB 67.56% on train).
> The committed ledger holds 1,137 settled ml-meta rows. The appraisal
> population is therefore a **warehouse view** (`view: "ml_meta_settled"`),
> not the committed JSON. Locate that population and measure there. Do not
> conclude from 1,137 rows what a 4,549-row appraisal would say, and do not
> report a soft-price ROI as if it were the appraisal's.

Then run the falsifiable test the question implies: **a draw rule at a
draw-plausible band.** Score `avg_p>=25/28/30` (and any band the data suggests)
on train/valid with Wilson LB and ROI, min-sample gates respected, using the
existing appraisal machinery (`src/edgefactory/assay.py`,
`src/edgefactory/enh_registry.py`) — do not hand-roll a scorer.

### Q3. Is the interesting rule even a threshold rule?
Test this reframe explicitly, because it is where an actual draw edge could
live. The current emission only ever picks a draw when the draw is the model's
*most likely single outcome* — mean stated confidence 16.7%, i.e. a
weak-conviction generator by construction. A draw at ≥3.0 only needs ~33% to
break even, so **conviction is the wrong axis for this market.** The untested
formulation is a **draw-value rule**: model draw probability versus the
price-implied draw probability (`warehouse.py` exposes the draw column as
`oddx` — `warehouse.py:66/88/125/136/179`; `ml_fade_research.py:300` maps
`draw -> oddx`). Mine that disagreement, and report whether any band survives
train/valid + decay.

### Q4. If one did certify, what does it break? (REMAP ONLY — DO NOT CHANGE)
Read-only mapping of the blast radius, because "remine the system" is the real
question behind the operator's ask:

- **Rule identity.** `src/edgefactory/warehouse_replay.py:72` — `class
  RuleSpec` has exactly five fields: `rule`, `kind`, `needs_sources`, `view`,
  `note` (the declared instances are at `:83-104`). There is **no
  pick/selection dimension**. A rule cannot currently be named "the draw side
  of X", so a draw rule has no identity to certify under. That is a structural
  blocker, not a config change — report it, do not add the field.
- **One-pick-per-fixture.** `scripts/picks_today.py` emits ONE pick at the
  highest qualifying threshold, with `"pick": majority_pick` (`:4362`; a second
  emission site at `:4444`) and `"avg_p": round(ml_p * 100.0, 1)` (`:4363`). A
  draw rule on the same fixture as a side rule produces two mutually exclusive
  picks. Which wins? Is the collapse deterministic? Read it; do not change it.
- **ACCA construction.** `LEGS_PER_ACCA = 2` (`scripts/auto_tickets.py:190`),
  `PAIRING = "barbell"` (`:192`), `MIN_LEG_ODDS = 1.20` (`:193`), `BUCKETS`
  (`:211`). A ~3.5 draw leg clears the odds floor. Check for a same-fixture /
  same-market leg guard before asserting correlated legs could be paired.
- **The fade family.** Its inverse is undefined for a draw parent
  (`fade.py:39-41`, `inverse_selection` at `fade.py:48`, `fade_odds_column` at
  `fade.py:57`). Draws becoming first-class does NOT create a fade of a draw.
  Also note the docstring on `fade_avg_p` (`fade.py:62-69`) claims the fade
  "wins exactly when the parent selection loses" — false on draw **outcomes**
  (its own parenthetical excuses only draw *parents*): on the 205 draw
  settlements in the paired set, both sides lose. Measured: when the parent
  pick loses, the fade wins only 51.4% (217 of 422); overall fade settled wins
  are 223 of 971. Correct that docstring only if licensed; otherwise report it.
- **Appraisal populations.** If draws enter as a family, do the walk-forward
  splits, min-sample gates and decay windows (`assay.py:14` `wilson_bounds`,
  `:40` `grade`, `:60` `decay_verdict`, `:117` `should_bench`) still hold their
  meaning? State it; do not retune.

## PRE-REGISTERED VERDICT BAR

State this before measuring, so the verdict cannot be negotiated afterwards
(mirrors the house style at `warehouse_replay.py:43-50`, the `GATE_MIN_*`
pass bar):

Recommend a draw rule as a **candidate** ONLY IF, on the appraisal population:

1. `min_n` is met on train AND valid;
2. the **Wilson lower bound** on the hit rate exceeds the break-even implied by
   that rule's own prices — not merely `roi > 0`;
3. it survives the train/valid split AND the live decay window.

Otherwise the verdict is **"draws stay graded-but-uncertified"**, and the
report must name the cause from Q2. The already-emitted draw picks at −30.9%
are the **null hypothesis**, not a baseline to beat by a hair.

## HARD RULES (grouped by what breaking them costs)

**Silent-wrong-answer class — check twice.**

- `avg_p` is 0–100; `ml_p` is 0–1. The unit mismatch has produced an empty
  result set twice in one session. Assert the scale at every band boundary.
- **Pair parent↔fade by `(date, home, away, model_key)` and confirm
  `pick == parent_pick` and `parent_ml_p == ml_p`.** A fixture can carry two
  ml-meta rows (different `model_key` — see `model_keys_seen`) — a plain
  per-fixture dict silently overwrites and produces phantom contradictions.
  This bug produced 16 "both-lost non-draw" rows that did not exist.
- A superseded record retains the ORIGINAL slip. Never read one as the day's
  outcome; check the slip file plus `auto_tickets_state.json` history.
- A rounded display value is never an exact bound (raw 0.5015 renders `50.1%`).
- The committed research ledger is a **slice**, not the appraisal population.
- Fuzzy matching is DIAGNOSTIC ONLY — reported, never a join path.

**Scope fence — this is a finding task.**

- Do NOT touch settlement, staking, bank arithmetic, or any
  gate/floor/cap/quorum/threshold/veto rule. Do not lower a threshold, a
  stale-days value, or `min_n` to let a draw through — that is the one change
  that would make this whole exercise worthless.
- No emission change, no registry change, no new family, no schema change.
  Propose exact entries (rule name, view, `where`, threshold) in the write-up
  and STOP.
- `Config/verified_results.json` and `localdata/team_aliases.json` are
  off-limits.
- Do not modify `.github/workflows/`; output the complete file instead.
- No new vendors or sources; no raised call caps; no lowered intervals. No
  vendor network in the sandbox — prove contracts with MOCKED responses only.

**Evidence discipline.**

- Verify by re-derivation, not restatement. Separate OBSERVED from INFERRED;
  state the boundary and scope of every claim; name the price basis (soft
  forebet vs execution-eligible) on every ROI line.
- Never assert wiring by text search — match structurally (AST) and assert
  against specific returned values.
- An identifier that asserts more than its measurement supports is this
  codebase's recurring failure. `avg_p` on a fade row is one such instance;
  a draw edge named after its conviction level would be another.
- Report sign, not significance: name `n` on every cell. Small cells are
  direction, never proof.
- A guard nobody has watched fail is not known to work: break it, watch red,
  restore, watch green.

**Delivery discipline.**

- Full suite must pass, 0 failed, no test deleted. Report the collected count
  with the baseline named. Measured on this branch (`e8de243`, i.e. with the
  ticket/slate brief in the tree): **2393 passed**, `def test_` floor **1534**
  (checked by `scripts/verify_work_order.py`). `tests/test_docs_links.py`
  parametrizes one case per Markdown file, so **each added doc moves the
  count by exactly +1** — this brief is the +1 on top of 2393, i.e. expect
  **2394 passed** with it in the tree.
- **Do not create a new findings doc — append to the existing
  `docs/operator/FINDINGS-2026-10-07.md`.** Doc volume is a real cost.
- Do not add tests unless the finding itself licenses them.
- Never force-push. On non-fast-forward: fetch, confirm the remote holds the
  work, `reset --soft`, re-commit forward. Never `git clean`, `git reset
  --hard`, or revert. Never use backticks inside a `git commit -m` heredoc.
- Update `docs/operator/DATED-CLAIMS.md` if and only if a claim there is now
  falsified.
- Do not write Markdown links to files you have not verified exist
  (`tests/test_docs_links.py` fails on dead relative links; fenced code blocks
  are exempt — keep paths in code spans or fences).

## ENVIRONMENT

- The checkout you inherit may be a shallow single-commit snapshot of `main`
  (the pipeline rewrites `main` each run — compare content, never ancestry;
  fetch and re-resolve the tip, never hardcode it). The PR #44 merge tree
  `f23a68b` and the nine branch commits `d6d163d…79f3945` may NOT exist
  locally — read production artefacts via `git show <tip>:<path>`.
- If you start from the session branch `arena/438d7dd2-edge-factory`, the
  ticket/slate brief (`docs/operator/NEXT-AGENT-BRIEF-2026-10-07.md`) is
  already in the tree — read it; it is the previous mission, not this one.
- No `.venv`, no pytest, no python-dotenv in a fresh workspace. System
  `python3` imports nothing here; `PYTHONPATH=src python3` imports
  `edgefactory`. `import auto_tickets` needs a `dotenv.py` stub providing
  `load_dotenv` on `PYTHONPATH`. To get the suite: `python3 -m venv .venv &&
  .venv/bin/pip install -r requirements.txt`, then
  `PYTHONPATH=src .venv/bin/python -m pytest tests/ -q`. `/tmp` is not
  persisted — recreate stubs.
- `localdata/*` is gitignored (`.gitignore:10`) except
  `!localdata/ml_fade_research_ledger.json` (`:136`). The shadow ledger
  (`scored_candidate_shadow_*.jsonl`) and `price_board_*.jsonl` are
  runner-only — do not go looking for them in git.
- `localdata/` in the working tree is production state. Read it; do not
  hand-edit it.

## REPORT FORMAT

1. What I verified vs what I was told (premises 1–5: confirmed / refuted /
   amended).
2. Q1 answer: the current state of draw emission, with counts and anchors.
3. Q2: cause (a) / (b), the band sweep, train/valid/Wilson/ROI table, `n` per
   cell.
4. Q3: the draw-value formulation and its verdict against the pre-registered
   bar.
5. Q4: the remine surface, read-only, with the specific things that would
   break.
6. Verdict against the pre-registered bar, stated in one sentence.
7. Proposed exact registry entries (if any), written out, not applied.
8. What I did NOT do and why.

## DELIVERY

This brief is committed on `arena/438d7dd2-edge-factory` and pushed. A fresh
session based on `main` will NOT see it (the pipeline rewrites `main` as a
single-commit snapshot and does not carry session branches). Hand it over by
starting the new session from this branch, or by pasting this file's contents
as the first message of the new session — it is written to be self-contained.
If a workspace ever holds a second, divergent copy of this file, the branch
version is authoritative — the pushed one is the superset.

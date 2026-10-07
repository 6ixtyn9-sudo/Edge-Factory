# NEXT-AGENT BRIEF — ML AUDIT & DRAW-PROOFING (2026-10-07)

Companion to `docs/operator/NEXT-AGENT-BRIEF-DRAW-MINING-2026-10-07.md` (the
draw-value rule mission). Two missions below, both operator-approved on
2026-10-07. Neither may move a threshold; both exist to produce the finding
that would license one.

Operator's words that scope this work: *"if it works, it's a small price to pay
for something that will compound, and if it doesn't, we can always revert...
just make sure the commit comments are clearly described."* That is a
requirement, not a preference — see COMMIT HYGIENE.

**Line anchors are perishable — the landmark wins.** Anchors are `file:line`
plus a searchable landmark; several drifted while this brief was written. If
the number and the landmark disagree, re-resolve by search and treat the
disagreement as drift, not as a contradiction.

---

# MISSION A — DRAW-PROOFING REPLAY (the ACCA complaint)

## Why it exists (measured 2026-10-07)

Method, so it can be reproduced exactly: parse every slip in
`localdata/auto_tickets_2*.txt`; join each leg to
`localdata/settled_results.json` on the same date by exact team names, falling
back to diacritic-folded names (NFD strip + casefold). NO fuzzy matching, NO
±3-day reschedule fallback — the pipeline's own grader has both, this replay
deliberately has neither, so its coverage is a lower bound. **0 donor
conflicts** among the joined legs.

Measured (40 slips, **2026-08-27 → 2026-10-06**; 2026-09-30 had no slip):

- 87 ACCAs parsed, all 2-leg (`LEGS_PER_ACCA = 2`, `scripts/auto_tickets.py:190`); 174 legs.
- **148 legs joined (85.1%), 26 unmatched.**
- **64 ACCAs fully joined: 40 won / 24 lost (62.5%).**
- **17 of 24 losing ACCAs (70.8%) had a leg that drew.**
- **16 of 24 (66.7%) would have WON if the drawn leg had been voided.** All 16
  are the identical shape: one leg won, the other drew.
- **65.4% of all ACCA leg failures were draws** (17 draw-deaths vs 9 outright
  losses).
- Leg hit rate on joined legs: **77.7%** (n=148). At independence that predicts
  a 60.4% ACCA win rate; actual 62.5% — no hidden ACCA-level defect. Draw
  exposure is leg exposure, compounded.
- **Zero draw legs have ever appeared on a slip** (grep across all 40) — the
  ACCA construction has never carried one.
- Cross-check against the pipeline's own settlement
  (`localdata/auto_tickets_state.json` history): every fully-joined ACCA that
  matches a pipeline record by (date, combined odds) agrees with the pipeline's
  won flag — **54 agree, 0 disagree.** The pipeline settled 86 ACCAs (51 won /
  35 lost) over the 40 bet days; the 64 here are the exact-join subset.

Draw concentration across the 148 joined legs (22 drew, 14.9%):

| leg price | n | drew |
|---|---|---|
| 1.00–1.25 | 28 | 10.7% |
| 1.25–1.45 | 73 | **6.8%** |
| 1.45–1.70 | 40 | **30.0%** |
| 1.70–2.10 | 6 | 33.3% |
| 2.10+ | 1 | 0.0% |

| stated confidence | n | drew |
|---|---|---|
| <60% | 7 | 28.6% |
| 60–68% | 45 | **24.4%** |
| 68–75% | 62 | **8.1%** |
| 75%+ | 34 | 11.8% |

**Direction, not proof** — 22 draws, in-sample on the archived window. State
that limit in every claim built on it. And note the confound: longer-odds legs
are genuinely less certain, so part of the 30% is the market working, not a
hidden pattern. That is exactly why Task A3 exists.

## Task A1 — price every draw-handling market exactly
DNB is not the only one. The warehouse exposes `odd1` / `oddx` / `odd2` per
settled row (`src/edgefactory/warehouse.py:66/88/125/136/179`), and the
committed prediction histories (`localdata/forebet.csv.gz`,
`localdata/zulubet.csv.gz`, `localdata/statarea.csv.gz`) carry them. Derive,
for every archived leg:

- **DNB / Asian 0.0** — void on draw; the ACCA collapses to its remaining legs.
- **Double Chance (1X / X2)** — WINS on the draw; the ACCA stays whole at a
  lower price.
- **Asian ±0.25** — split-stake partial cover, if derivable from the same
  columns.

Re-price every leg, recompute each ACCA's combined odds and payout under each
market, and A/B against the as-bet slips at the same stake schedule, same legs,
same days.

## Task A2 — the floor (measure; DO NOT change)
`MIN_LEG_ODDS = 1.20` (`scripts/auto_tickets.py:193`) is global. Under DNB/DC,
short favourites collapse toward 1.02–1.10 and would fail it. Report how many
archived legs fall below 1.20 under each market, and in which price bands. The
operator's read — "the 1.2 min odds should not be global" — is a **hypothesis
to test**, not an instruction to edit. The count is what would license a
per-market floor.

## Task A3 — is the draw mispriced, or merely volatile?
For each price band, compare the **realised** draw rate against the rate
implied by `oddx`. If realised ≫ implied, the draw is underpriced and
avoiding/covering those legs is +EV. If they match, the market is right and
only variance changes — draw-proofing is then a comfort blanket that costs
return. Answer it explicitly; it decides whether Mission A is a strategy.

## Pre-registered bar for Mission A
Recommend a draw-proofed construction as a **candidate** ONLY IF, over the same
archived window at the same stake schedule: total return ≥ the as-bet return,
AND the take-profit ladder is not delayed past the point where it changes
compounding. Otherwise the verdict is "measured, not adopted", and the report
says which clause failed.

---

# MISSION B — ML AUDIT (operator-approved)

## Premises (verified 2026-10-07 — REFUTE BEFORE BUILDING ON THEM)

- **26 features; 2 are permanently zero.** `FROZEN_FEATURE_COLS`
  (`src/edgefactory/ml_fade_research.py:99`) lists 26; `ml_ht_diff` and
  `ml_ht_total` have distinct values `[0]` across all 2,258 research-ledger
  rows (the frozen serve-time contract pins them pre-match,
  `ml_fade_research.py:92-98`). Functionally a 24-input model.
- **No independent football data** — no Elo, form, lineups, xG, rest, weather,
  referee, H2H, or market movement. The only football-shaped inputs are the
  tipsters' own predicted-score / goals aggregates harvested into
  `consensus3`. It is a confirmatory meta-model over tipster consensus, not a
  match predictor.
- **Exactly one model class has ever existed in the tree:**
  `LogisticRegression(max_iter=1000, random_state=42)`
  (`scripts/mine_consensus.py:610`). Greps for GradientBoosting / RandomForest
  / XGB / LGBM / HistGradient return nothing.
- **No scaler, no calibration, no ablation.** Greps for StandardScaler /
  calibration_curve / brier_score / log_loss return nothing outside tests.
- **Live vs paper.** The pipeline's own books
  (`localdata/auto_tickets_state.json`,
  `localdata/auto_tickets_performance.json`): bank 100 → **163.36** over 40
  bet days, staked **1028.00%**, returned **1091.36%**, **+6.2% ROI** at
  execution prices. The registry claims **+33.2%** valid at scraped prices
  (`localdata/edges_consensus.json`, rule `ml-meta avg_p>=55`). **The gap is
  execution price, not model quality** — start every recommendation from that.
- **Source coverage — the model sees 3 of the 7 voting sources.** The replay
  harness's own note: "live votes any 2 of 7"
  (`src/edgefactory/warehouse_replay.py:89`).
  `ON_DISK_PREDICTION_SOURCES = {"forebet","zulubet","statarea"}`
  (`warehouse_replay.py:58`) plus
  `MISSING_PREDICTION_SOURCES = ("vitibet","bzzoiro","betclan","scoutingstats")`
  (`:67`) sum to 7. The warehouse builds `consensus2` (forebet×zulubet,
  `warehouse.py:376`), `consensus3` (+statarea, `:394`), `consensus4`
  (+vitibet, `:422`); the model trains on **consensus3 only** — its
  `ml_meta_settled` view joins `consensus3`
  (`scripts/mine_consensus.py:619-621`). 26 source rows run daily
  (`DAILY_SOURCES`, `src/edgefactory/source_health.py:93`); 28 modules sit in
  `src/edgefactory/sources/`.

## Task B1 — calibrate (cheapest, highest leverage, DO FIRST)
`ml_p` is raw logistic output, and nothing in the tree ever checked that "70%"
means 70%. Fit Platt/isotonic on a held-out slice; measure with a reliability
curve and Brier score. `ml_p` drives every certified threshold (55/60/65/80),
the fade's stated confidence (`fade_avg_p` = 1 − ml_p, `src/edgefactory/fade.py:62-69`),
and the volume regime's stated-prob gate (`VOLUME_MIN_PROB = 0.65`,
`scripts/auto_tickets.py:196`). **Report which picks change band** — does
calibration move any pick across a threshold? That is the actionable output.

## Task B2 — the two dead features
Ablate `ht_diff` / `ht_total`; confirm coefficients ≈ 0; report whether the
frozen contract is the only thing keeping them.

## Task B3 — scaling and hyperparameters
StandardScaler before the fit (absent today, so the L2 penalty shrinks
features according to their units), then a search over C and penalty. No new
data required.

## Task B4 — source coverage, staged — MEASURE FIRST
`consensus4` is *defined* at `warehouse.py:422` but materializes only where a
`vitibet_settled` table exists. In the committed tree the only prediction
histories are `forebet.csv.gz`, `zulubet.csv.gz`, `statarea.csv.gz` — vitibet's
history, if it exists at all, lives in the runner's cache, not in git. So:
(i) measure whether a `vitibet_settled` table can be built at all in this
checkout; if yes, measure what a 4-source retrain does — the cheapest real
information gain available. (ii) For bzzoiro / betclan / scoutingstats,
quantify what capture would be needed and how long to accumulate a trainable
history. **Report the plan; do not add captures unilaterally.**

## Task B5 — model class, only after B1–B4
Compare against the logistic baseline under the same split and appraisal bar.
Report whether the gain, if any, survives the cost below.

## THE COST — state it in every proposal
The frozen serve-time contract exists to keep historical rows comparable. A
changed feature set or algorithm **invalidates comparability with every
settled row and every certified threshold calibrated on them**. Any change
therefore requires: a new `model_key`, a **shadow period** scoring old and new
side by side, and **no threshold movement until the shadow certifies**.
"Expensive but worth it if it works" is the operator's accepted position — but
the shadow protocol is what makes it revertible, so it is not optional.

---

# COMMIT HYGIENE (operator requirement)

One commit per change. The message must name **what changed** and **what it
invalidates**, so any future agent can bisect the history and roll back to
2026-10-07. No backticks inside a `git commit -m` heredoc. Never force-push; on
non-fast-forward: fetch, confirm the remote holds the work, `reset --soft`,
re-commit forward. Never `git clean`, `git reset --hard`, or revert.

# HARD RULES

- Floors and thresholds measured, never guessed. No gate / floor / cap /
  quorum / veto / stale-days value moves in this work.
- No new vendors or sources; no raised call caps; no lowered intervals. No
  vendor network — prove contracts with MOCKED responses only. Never log
  request headers.
- Fuzzy matching is DIAGNOSTIC ONLY — never a join path. Diacritic folding is
  normalisation and must be stated.
- `avg_p` is 0–100, `ml_p` is 0–1. Assert the scale at every band boundary.
  State the boundary convention of every band table.
- Report `n` on every cell. Separate OBSERVED from INFERRED, and state the
  scope of every claim. An identifier asserting more than its measurement
  supports is this codebase's recurring failure.
- Verify by re-derivation, not restatement. Never assert wiring by text search
  — match structurally (AST) and assert against specific returned values.
- Zero draw legs have ever appeared on a slip. If a proposal puts one there,
  that is a bigger change than it looks — say so explicitly.
- **Do not create another findings doc — append to
  `docs/operator/FINDINGS-2026-10-07.md`.** Doc volume is a real cost.
- Full suite must pass, 0 failed, no test deleted; report the collected count
  with the baseline named. Measured on this branch (`fcf388a`, with the two
  existing briefs): **2394 passed**, `def test_` floor **1534**
  (`scripts/verify_work_order.py`). `tests/test_docs_links.py` parametrizes one
  case per Markdown file, so **each added doc moves the count by exactly +1** —
  this brief is the +1 on top of 2394, i.e. expect **2395 passed**.
- Read merged code via `git show 6f52b92:<path>` if `f23a68b` is absent. The
  pipeline rewrites `main` each run — compare content hashes, never ancestry.
- No `.venv`, no pytest, no python-dotenv by default; `/tmp` is not persisted.
  `PYTHONPATH=src .venv/bin/python` after
  `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

# REPORT FORMAT

1. Mission A: the A/B table (as-bet vs each draw-handling market), the floor
   count, the mispricing verdict.
2. Mission B: calibration result first (which picks move), then B2–B5.
3. Verdict against each pre-registered bar, one sentence each.
4. Proposed exact entries (rule name, view, `where`, threshold) — written out,
   not applied.
5. What I did NOT do and why.

# DELIVERY

This brief is committed on `arena/438d7dd2-edge-factory` and pushed. A fresh
session based on `main` will NOT see it (the pipeline rewrites `main` as a
single-commit snapshot and does not carry session branches). Hand it over by
starting the new session from this branch — it already carries the two earlier
briefs — or by pasting this file's contents as a message of the new session.
If a workspace ever holds a second, divergent copy of this file, the branch
version is authoritative — the pushed one is the superset.

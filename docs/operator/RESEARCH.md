# Research and frozen safeguards

[Operator handbook](README.md) · [Sources](SOURCES.md) ·
[Recovery](RECOVERY.md) · [Evidence](DATED-CLAIMS.md)

Research does not promote itself. A retrospective optimum, statistical pass,
green test suite, storage inventory or parity result is not production
certification. Do not change a serving model, electorate, threshold, stake or
frozen receipt under a documentation/research task. Harness probes belong in
`scripts/replay_harness.py`, not a new parallel harness.

## Current-contract re-mining

Use the **existing** `scripts/mine_consensus.py`, not a second miner/registry.
Without `--activate` it writes research output; the installed `remine_only`
mode rebuilds the warehouse from restored cache and uses this non-activating
path. Ordinary authorized daily paths use the existing guarded activation.

The post-Forebet scan excludes Forebet as voter/result donor and uses exact
date + oriented `source_team_key` identities. It evaluates observed subsets,
singles/unanimity/strict-majority/disagreement-follow predicates and supported
FT/HT/line-specific markets. Two-voter ties are not majorities; categorical
tips do not acquire fabricated probabilities; FT results cannot supply HT.
Completed-history windows and the exclusive `as_of` must be reported. Searching
many recipes against validation is model selection, not untouched forward proof.

Activation uses shared `consensus_contracts` predicates in mining, picking,
assay and decay; exact IDs bind schema/market/electorate/strategy/followed
source/threshold. Labels and source-count guesses cannot substitute for the
structured recipe. Under `operating_contract: post_forebet_v1`, missing or
zero eligible contracts do not revive legacy guessed operating points.

The existing acceptance boundary is unchanged: train/validation counts **and
priced counts** at least 340/120, train ROI ≥−0.10, validation ROI ≥0, validation
Wilson lower bound ≥0.50, finite returns and exact recreation of complete
reported statistics before the atomic write. Missing incumbent/history or zero
passes preserves the incumbent; a cold-cache gap is not failed certification.

New contracts start **WATCH** with forward-only decay from the original
activation date. Revalidation cannot erase a bench, reset an activation date
or inherit another contract's purity contexts. Unpriced predictions are not
synthetic losses. Historical donor-price ROI is not execution-safe ROI:
newly selected rows start unpriced and must pass the existing live quote gates.
Frozen ML payload/rules remain protected; this migration does not reactivate ML.

## ML-FADE RESEARCH GUARDRAIL

Consolidated without changing the policy frozen **2026-09-20** and its
**2026-09-21 wall-clock** clarification. The predeclared home-fade avg_p≥65
slice remains **INSUFFICIENT EVIDENCE / not yet**; no label shopping.

A checkpoint is due when any fixed condition holds:

1. No checkpoint has ever run.
2. The SAST calendar month advanced.
3. Settled ml-fade rows increased by **at least 50**.
4. **At least 30 distinct capture days** accrued since the last checkpoint.

Evaluate due checkpoints only after the **09:00 SAST wall-clock freeze** via
`checkpoint_eval_window_open` in `scripts/daily.py`. Intraday runs
settle/monitor/defer without consuming due-ness. The early 2026-09-21 bootstrap
is real history: never rerun or erase it to improve the record.

Rerun `research_ml_fade_contexts.py` and `research_ml_fade_price_study.py`
**unmodified**. Fixed price variants use first-seen bet-time ZuluBet-only and
Forebet-only prices; keep the avg_p/parent_ml_p **55/60/65/70** accumulator grids
for both ml-meta parent and ml-fade families. Automatic **research-candidate**
signal requires all of:

- At least 200 settled fade rows and no unresolved fade conflicts.
- For **each** fixed price variant: at least 150 priced rows, Wilson lower bound
  at least 0.55 and ROI strictly positive.

That signal never certifies or changes operational behavior. Always report
accrual stalls, price-coverage gaps, unresolved conflicts and model drift.
Policy amendments require an explicit documented commit recording operator
direction, updating **this section and `edgefactory.ml_fade_checkpoint`
constants together**—never a reaction to interim performance.

Manual commands (research/state outputs, not a production promotion):

```sh
PYTHONPATH=src python3 scripts/ml_fade_research_eval.py
PYTHONPATH=src python3 scripts/ml_fade_research_eval.py --settle-monitor-only
# Explicit diagnostic rerun only; not a way to erase/replace the frozen cadence:
PYTHONPATH=src python3 scripts/ml_fade_research_eval.py --force-checkpoint --skip-studies
```

## Incumbent train/serve and label contracts

The historical checkpoint-12 finding was a real train/serve mismatch:
`ht_diff`/`ht_total` learned actual half-time scores but were pinned to zero
pre-kickoff. The resulting probability scale/operating cut was load-bearing.
Do not “repair” it by silently retraining, changing feature construction or
carrying the old cut onto a new calibration. Retrain **and** rederive cuts as
one explicitly authorized, fully certified change. Research fits are not that
promotion. Current vector construction requires actual values or recorded
finite training means; do not restore guessed 0/0.5/1.5/75% fallbacks.

The original comparison did **not** establish ml-meta superiority: the two
families were statistically indistinguishable on that sample. Do not upgrade
that conclusion. Incumbent guards and mutation tripwires remain binding.

A displayed legacy source-count rule can name the operating floor, not the
individual pick's model tier. Changing a stored `rule` to make a label look
better changes eligibility; display-only edits may be healed back. Treat that
as a policy change, not cosmetic cleanup. Bench/health interpretation must use
the actual structured contract/floor-holder and recent **priced** observations.

## Veto-resolution precommitment

The former Addendum-27 policy is retained here. The pure overlay pools rules
within `(sport, league_key, market, side_role)` using n-weighted unconditional
ROI; its O1/O2 ladder is pooled league → niche → competition type.
Scenario-B sample gates: ALLOW ≥40, CAUTION ≥20, VETO ≥12. It never rewrites
`purity_registry.json`. `EDGE_FACTORY_VETO_RESOLUTION` is flag-gated; do not
turn it on merely because shadow fields exist.

Scope is **league-UNKNOWN** picks only; a niche-UNKNOWN short-sniper block whose
league is already resolved is outside this gate. Checkpoints use the same
window for overlay and comparison bucket and report resolved/unresolved shares
and O1/O2 mix. A composition shift after another overlay ships must be disclosed.

FLAG-ON requires **all**:

1. At least 30 settled in-scope caution-grade picks.
2. Overlay ROI >0 and at least bucket ROI minus **1 percentage point**.
3. Overlay hit-rate **90% Wilson lower bound** at least bucket hit rate minus
   **5 percentage points**.

Any failure means remain OFF/shadow. While OFF, at ≥60 settled, if both ROI and
hit-rate gates still fail and overlay ROI is below bucket ROI by **more than
2 percentage points**, confirm at a second checkpoint **at least two weeks
apart**, then deprecate (flag stays OFF; retain code/audit evidence). Thresholds
are fixed while accruing. If ever activated, use its separately monitored live
lifecycle and revert OFF if the same performance standard fails.

Engine-aware debias acts at note/probability construction; veto resolution acts
at context→bucket. Their counters are independent, but a shifted future cohort
is not automatically comparable. Define interactions before a third overlay.
The existing read-only `counterfactual_veto_resolution.py` prints the gates;
its output alone does not authorize activation.

## Phase 5: frozen ML-era certification

The authoritative original nine-clause pre-registration is
[Findings §9.0, with the narrow §9.3 amendment](FINDINGS-2026-10-07.md).
It is retained because the certifier cites it and appends qualitative status
changes there. Earlier dated diagnoses in that file are not current status.

Keep declared and realized source sets separate. `K` is the fixed 32-column
contract in `phase5_k`, shared by fit and score. Dark feeds retain their columns
and availability flags; missing probabilities use enumerated era-train means,
not fabricated votes/zeros. Timing-contaminated sources are excluded explicitly.

The frozen bar includes 90-day continuity (no gap >7 days), ≥95% trailing-30-day
capture success, complete capture timestamps, ≥99% pre-kickoff timing, ≥95%
marker-aware exact joins on a fixed 200-fixture audit, unchanged sample/ROI/
Wilson gates, paired overlap, coverage, independence and rollback/sequencing.
Paired fixture-date bootstrap is **10,000 reps, seed 42, two-sided 95%**;
upper bounds on candidate−comparator must be ≤**+0.002 Brier** and
≤**+0.005 logloss**. At most one activation per 30 days, each era once; incumbent
entry/cuts remain immutable.

The clause-5 amendment permits only the named **“incumbent-coefficients arm on
the same era-local paired inputs with the same enumerated fallbacks”**; it is
not true forward-incumbent performance and does not silently amend clauses
4/6/7. Missing era evaluator, fixed identity audit, overlap/coverage comparator
or parked-Forebet independence evidence remain explicit blockers. Waiting alone
cannot repair an undefined comparator. `not_yet_due` is distinct from failure.

Candidate fit → full certification → recorded same-certificate revert dry run
(no older than 24h) → explicitly confirmed activation → explicitly confirmed
promotion is the guarded path, **not** an instruction to execute it now.
`scripts/phase5_activate.py` exposes status/kill-switch/revert/restore commands;
consult `--help` and distinguish resolver config from a promoted live registry.
Promotion verifies the guard, keeps byte-for-byte reconciliation backups and
benches incumbent-derived ml-fade cuts. No speculative handover can clear gates.

## ML/consensus sidecar proposal

The [Gate-A schema/storage specification](GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md)
is retained as a historical contract, not installed functionality. The temporary
recorder/hooks were **removed from the release**; no recorder is shipped or
activated. Design approval was not implementation acceptance or publication
permission. The independent external D1–D7 record is not interchangeable with
this repository's transferred/re-reviewed D1–D5 record.

Any future proposal must preserve operational rows/IDs/order, electorate,
registry/model/price/ticket/bank semantics and fail-soft bounded audit-only work.
No audit field becomes a qualification input. A compact index is metadata, not
recoverable bytes or replayability; missing verified export dependencies means
non-replayable. No ignore, upload, workflow or data-publication permission is
created by retaining the spec. The prior release disposition and full old work
orders remain in Git at the [pre-cleanup snapshot](https://github.com/6ixtyn9-sudo/Edge-Factory/tree/30e9372aab33e1e9444c1f5fd3b916df91ca7f0e/docs/operator).

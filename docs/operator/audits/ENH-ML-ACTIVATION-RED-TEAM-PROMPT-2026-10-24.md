# Paste to Z.ai — red-team the LIVE three-acca ENH ML capacity repair

You are the independent adversarial engineer. Review actual source and run tests; do not rubber-stamp this description. Correctness, production coverage and profitability are separate questions.

## Target and the earlier review mistake

- Repository: `6ixtyn9-sudo/Edge-Factory`.
- Branch: `arena/5c4275c0-edge-factory`; compare its latest head against `9a4088a0657710627c1e29c73735b3913200303c` (merge of PR149).
- PR149 is already merged. This is its follow-up, not another change to that closed PR.
- **Trace the live call site, not just function defaults.** Main uses `MAX_ACCAS=2`; `cmd_enhancement` passes `max_accas=ENH_MAX_ACCAS`, which is **3**. Armed pairing is **barbell**, each acca has **two legs**, and `GATE_MODE='off'`.
- Prior reviews treated `max_accas=3` as non-live. That was wrong. The previous `remaining == 2` repair left the live ENH first decision unprotected. P2-1 rank-group separation and P2-3 optional-fit containment remain closed; do not reopen the census or redesign the model.

## Reproduce the real defect first

Already-admitted offers `(fixture, book, cohort, ML)`:
`(A,X,.70,.95), (B,X,.70,.94), (A,Y,.70,.95), (C,Y,.90,None), (B,Z,.70,.94), (D,Z,.89,None)`.
All odds 2.0, `match_over_25`, common source, valid `cohort_payout_bound` contexts; row home identities A/B/C/D and a common away team/date.

With active ML, **max_accas=3**, min_accas=1, k=2 and gate off, the baseline selects only AX/BX although AY/CY + BZ/DZ are possible. Add `(E,W,.85,None),(F,W,.84,None)`: baseline selects **two**, although **three** are possible. Also test X={A,B,C}, Y={A,B,D}, W={E,F}, where all initial X/Y recipe pairs share A/B. Both barbell and consecutive must work. Do not claim a third acca is possible on only four distinct fixtures.

## Implementation to attack

Only existing machinery: `scripts/auto_tickets.py:select_accas`, existing test files, HANDOVER and this prompt. No new dependency, script, service or training path.

- With active ML ordering and **two OR three slots remaining**, compute residual achievable pair capacity before committing the recipe's best pair.
- Preserve that recipe pair if it does not reduce achievable capacity. Otherwise prefer a capacity-preserving existing recipe pair. If none works, choose a pair from a capacity witness. Rescue can deliberately depart from barbell/consecutive; this is not a global optimization of ML score or odds.
- The local `completion` helper operates on the existing executable book/source groups after fixture deduplication and exclusions. It returns an exact capacity witness capped at three pairs, not a joint success probability.
- Fast path: maximal greedy matching fills the request. Otherwise its endpoints form a vertex cover of at most four fixtures. Collapse identical fixture edges to their highest-ranked executable quote pair, retain all cover-cover edges, and at most `2*limit` outside neighbours per cover vertex. This bounds the rescue graph to **30 edges**, search depth **3**.
- Independently prove or break that bound and kernel: replacing a discarded outside matched neighbour with a retained unused neighbour must preserve matching feasibility. Confirm every returned edge retains its OWN complete quote context and no metadata is borrowed between books, sources or markets.
- This protects active ML cards capped at three under live gate-off settings. No general first-decision guarantee for caps above three or after nondefault conviction gates. Exact ML-off and unscored greedy behavior intentionally remain unchanged, including baseline underfill.

## Required checks

1. Trace `cmd_enhancement` through admission, pool, actual `ENH_MAX_ACCAS=3` override, selector, staking, evidence carry and draft. A regression exercises that real command with controlled ML inference and real execution-safe cohort/quote checks, isolated in a temporary directory. It is NOT a production-model fit.
2. Verify both old failing counterexamples, three feasible pairs, only two feasible pairs, missing/invalid/zero scores, equal-rank/input shuffles and no feasible pair. No fabrication of volume or six-fixture exposure from duplicates.
3. Verify maximum attainable count capped at three against an independent oracle, not the production helper. Existing tests enumerate **all 32,768 simple graphs on six fixtures per pairing mode**, using independent vertex-subset DP. They also cover 300 shuffled larger graphs per mode and high-degree truncated-neighbour cases with positive/negative certificates. Test book AND source separation, odd cycles and >6 external neighbours.
4. Keep already-feasible barbell/consecutive recipes, exact ML-off/unscored behavior, Main's two-acca default, fixture exclusivity and input immutability. High ML must not override admission, source/quote timing, N30, measured-rate band, minimum odds or payout evidence.
5. Verify unchanged shared staking: Main default 2, ENH max 3, total cap **25% of free bank**. Live `per_acca` uses a nominal 12.5% per slot but caps the card at 25%; three accas share that capped total. A repair can increase actual deployment from 12.5% to 25%; do not confuse unchanged policy/cap with unchanged deployed exposure. Frozen/settled records remain untouched.
6. Inspect runtime: no slate-size exponential search. Arena synthetic means (10 repeats, not production): 519 quote legs across 173 hidden-alternative groups ~57 ms; 404 high-degree quote legs ~21 ms. Reproduce/challenge on larger synthetic populations and label limits.

## Run existing tests only

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_enhancement_evidence_integrity.py -k 'three_acca or live_three'
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_enhancement_lane.py -k uses_three_slot
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_enhancement_evidence_integrity.py -k enh_ml
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q
```

Arena receipt: **4,350 passed, 1 skipped in 219.82s**. New cases: 17 evidence-integrity + 1 live-command regression. The full-run XML includes 50 `enh_ml` cases in the evidence-integrity file. Earlier receipts came from earlier environments: reconcile collection IDs in the SAME environment before asserting an exact count offset. Inline cross-head probes also matched baseline selection AND staking in 7,200 Main/rollback/unscored configurations; these were synthetic checks, not production observations.

## Return one compact engineering verdict

PASS / PASS WITH LIMITS / BLOCK; actual head and inspected scope; defects with executable evidence and minimal fixes; commands/results and same-environment collection delta; merge recommendation and remaining limits. Be explicit about the live three-acca call site. Do not equate capacity correctness with optimal ranking, calibrated predictions or profit.

Production fit/status census, actual activation coverage, same-day flag-off comparison and economic benefit remain unobserved in Arena. No production fit, workflow dispatch, merge, operational record changes or cash placement is authorized by this prompt. No new audit scripts or parallel pipeline; add discovered regressions to existing tests.

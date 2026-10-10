# Acceptance checklist: ML/consensus provenance and routing

**Date:** 2026-10-09  
**Proposal:** [revision 4](PROPOSAL-ML-CONSENSUS-PROVENANCE-2026-10-09.md)<br>
**Evidence:** [review synthesis](REVIEW-SYNTHESIS-ML-CONSENSUS-2026-10-09.md)

**Audit-design disposition:** APPROVE WITH CHANGES (conditional).  
**Audit implementation:** NOT IMPLEMENTED / NOT ACCEPTED.  
**Live routing:** NOT APPROVED FOR ACTIVATION.

Unchecked items are requirements, not claims of completed acceptance tests. The original two isolated probes reproduced provenance-induced archive rejection and existing shadow signal-ID collision. Later separately authorized [fallback/contract tests](EXECUTION-FALLBACK-CONTRACT-TESTS-2026-10-09.md) reproduce qualifier/electorate gaps and test the narrow fallback-origin fix; C1 adds an isolated layout/staging control. None establishes parity or acceptance of an audit implementation that does not yet exist.

## Gate A — Schema and storage contract, before coding

**Submitted draft:** [mcp-audit/v1 schema/storage specification](GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md). Draft 3 records [renewed A1–A3 technical approval and separate review scopes](GATE-A-REVIEW-DISPOSITION-2026-10-09.md). **A1–A4 design approval is complete; C1 is independently confirmed.** The confirmations cover path/staging only, not implementation acceptance. Recorder/publisher/hook implementation remains explicitly unauthorized. Design approval is recorded above; the unchecked items continue to express implementation/persistence/acceptance prerequisites, not an outstanding C1 confirmation request.

- [ ] Approve a separate versioned sidecar stream and bounded retention/persistence contract; no unreviewed workflow changes or large tracked datasets.
- [ ] Preserve operational rows, archives, exported payloads, IDs, models, rules, thresholds, prices, tickets and frozen state unchanged.
- [ ] Preserve canonical whole-payload equality; do not exclude provenance fields from the comparison as a workaround.
- [ ] Define shared fixture-occurrence/selection reference, distinct signal IDs and per-build observation IDs. Preserve ambiguity/squad boundaries; do not replace existing operational candidate IDs.
- [ ] Capture emission path, target selection and election contract, actual target electors, observed/imputed feature inputs, model/guard receipt, feature-contract version and immutable input-snapshot reference.
- [ ] Capture consensus electorate, qualifying average, nominal/effective competition-adjusted thresholds, registry/fallback origin and electorate-certification match status with reasons/unknown states.
- [ ] Define fade receipts separately: parent model score is the qualification basis; legacy complementary display is not certified opposite-side 1X2 probability.
- [ ] Obtain explicit approval for this schema/storage design. Conditional review approval is not implementation acceptance.

## Gate B — Reproducible adversarial controls

Use synthetic inputs, temporary registries/state and mocks; no providers, model fitting, operational-state writes or historical rewrites.

- [ ] Pin current selector collision and genuine ML highest-certified-tier behaviour as baseline controls.
- [ ] No model + 70% consensus: distinguish baseline ML-labelled emission, family-separated synthetic emission and exact historical-elector policy. Do not label these controls a production replay.
- [ ] Model 62.3% / source average 78%: distinct signal evidence survives; one unchanged operational selection under baseline instrumentation.
- [ ] Certified cuts 55/60/65/80 with 70/75 benched: model 78% qualifies at 65. Preserve actual tier semantics.
- [ ] Statarea/Vitibet/Bzzoiro agreement with Forebet/Zulubet absent: certified historical-trio equivalence false. Cover named two-way mismatch too.
- [ ] Historical electors agree plus dissenting extra voter: isolate exact-elector versus all-available-voter semantics.
- [ ] Parked Forebet: normal fetch exclusion and zero effective weight remain unchanged; direct replay inputs apply date eligibility explicitly.
- [ ] Qualified min-p rule with 56/72/72, and home-only with away: proposed predicate policy rejects; audit stage retains baseline output.
- [ ] Non-1X2-only registry causing 1X2 defaults with misleading legacy fallback flag: record actual origin; proposed policy cannot silently enable fallback.
- [ ] Same fixture/selection/rule from two emission paths: distinct signals survive consolidation and link to the existing representative.
- [ ] Equal-rank representative permutations: deterministic audit evidence; exact baseline output for each ordering. Do not introduce a new operational tie-break in this stage.
- [ ] Archive morning/regular metadata counterexample: sidecar on/off/failure preserves admitted additions and unsafe-date receipts.
- [ ] Full Supabase source payloads, scalar fields, manifests, notification bodies and identity/dedupe remain unchanged.
- [ ] Scoring-hook failure controls: serialization, missing receipts, disk writes, exception handling and shared-object mutation cannot alter selection or downstream payloads.
- [ ] Model guard failures, missing inputs, opposing signals, kickoff guards, price quarantine, source eligibility, odds floors, squad identity and frozen-ticket locks remain intact.
- [ ] Fade draw handling and legacy complement remain unchanged; a draw is not counted as an opposite-side win.

Attach commands, code revision, inputs and expected/actual outputs for each control. Reviewer-reported experiments must be rerunnable rather than treated as implemented tests.

## Gate C — Sidecar implementation acceptance

- [ ] Hooks collect copied evidence at computation/emission before collapse, including electorate-match evidence; no later inference from the survivor.
- [ ] Signal/observation collection is deterministic, bounded and fail-soft; no production consumer reads sidecar fields for qualification.
- [ ] Enabled, disabled and hook-failure modes pass all parity controls, including canonical admission, payloads, research ledgers, ticket/state output and notification identities.
- [ ] Separate audit reports reconcile true inference counts, per-path emissions, overlaps and representative links without rewriting existing ML logs or `ml_meta_state.json`.
- [ ] Inspect decay narrowly: its guarded prediction exports/views are not archived-label populations. Preserve its dependencies and ML-fade research checkpoint behaviour.
- [ ] Run relevant repository regression tests and record failures/limitations accurately.
- [ ] Obtain acceptance for audit implementation only. No live routing permission follows from passing this gate.

## Gate D — Pinned comparison

- [ ] Compare baseline, family-only routing and exact-supported-contract policy on identical inputs.
- [ ] Pin sources, model/guard/activation state, feature contract and derived inputs (including rolling-hit-rate warehouse facts), registry, purity/context/debias/veto state, entity overrides, source retirement policy, as-of and price receipts.
- [ ] Pin historical ticket/bank/ladder/freeze state for ticket replay. Use a temporary copy and unchanged ticket engine.
- [ ] Missing required point-in-time dependencies make a date non-replayable for the affected comparison; partial diagnostics remain explicitly partial.
- [ ] Attribute additions/removals to family, floor, electorate, qualifier, fallback, context, price or collapse; report overlapping/opposing signals and no-bet outcomes.
- [ ] Separate model-only, consensus-only and overlap outcomes, priced/settled denominators, uncertainty and execution-safe versus research-price results.
- [ ] Do not pool unlike probability meanings, double-count supporting signals, cherry-pick ROI thresholds or claim guaranteed return improvement.

## Gate E — Live policy decision (currently blocked)

- [ ] Choose supported historical-elector/predicate enforcement **or** a separately identified available-voter contract with required evidence and promotion. No inherited certified name merely to preserve volume.
- [ ] Specify qualifier, fallback, representative, exact edge reference, probability and context precedence. No blended scores or bucket-based label shopping.
- [ ] Explain required-elector abstention separately from blanket suppression; independently qualified model signals stay independent.
- [ ] Review all consumers before changing operational schema, rules or labels; future schema migration needs separate prospective approval.
- [ ] Explain same-input differences and preserve safety invariants. Correctness may justify change without proven ROI uplift, but not unsupported certification.
- [ ] Record explicit operator approval, prospective version boundary and rollback plan. Neither supplied review grants activation.

## Gate F — Activation and rollback evidence

- [ ] Frozen cards, original bet-time evidence and historical IDs remain immutable across activation and rollback.
- [ ] Audit disable and routing rollback preserve incumbent model, price safeguards, staking settings and locks while retaining evidence.
- [ ] No automatic model promotion, electorate substitution, relaxed gates, archive rewrite or new dual production lane.
- [ ] Record implementation revision, activation decision, test receipts and unresolved limitations in a new operator decision entry.

**Immediate next decision:** explicit authorization for any further implementation scope; C1 is satisfied and needs no further review loop. Recorder, hooks and publisher remain unauthorized. Separately authorized fallback/test work is complete ([execution receipt](EXECUTION-FALLBACK-CONTRACT-TESTS-2026-10-09.md)); its six failing contract assertions do not accept an implementation or authorize routing.

**Suite status:** the six new contract failures remain unsuppressed. The full suite is not green; passing related selections do not grant acceptance.

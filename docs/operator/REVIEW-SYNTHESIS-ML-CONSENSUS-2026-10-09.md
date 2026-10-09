# Independent-review synthesis: ML/consensus provenance proposal

**Date:** 2026-10-09  
**Status:** documentation only; no live-change authorization  
**Proposal:** [revision 4](PROPOSAL-ML-CONSENSUS-PROVENANCE-2026-10-09.md)<br>
**Local code baseline:** `01f580c1f41b78883d7c807e354ba76903bbd026`

The user supplied two independent reviews in chat. This document summarizes their material claims and dispositions; it is **not** a claim that the review agents' experiments were all repeated here. Review identifiers below are local labels, not independently verified agent identities.

## Current verdicts supplied (supersede initial review)

| Reviewer | Audit design | Live routing |
|---|---|---|
| Review 1 | Approve with changes; not implementation acceptance | Reject activation now |
| Review 2 | Conditional approval with changes; revision-3 documentation amendments addressed | Not approved for activation |

Review 1 initially said Approve / Approve with changes. Its supplied follow-up supersedes those verdicts. There is **no current live-activation split**. Both reviewers endorse staged provenance and comparison, reject profitability promises, and require explicit electorate semantics. Neither approves audit-hook implementation automatically.

**Scope limitations:** Review 1 originally reported a different checkout (`a189fd4` plus local commits); its latest follow-up says it read the synthesis, but not the revision-3 proposal or checklist, and reports corrections committed elsewhere as `714f8cc`. That external commit was not fetched or verified here. Review 2 now reports reading all three documents pinned to `0dac025` and checking its four-file documentation-only scope. This scope is independently confirmed by local `git show --stat`. Its earlier 991-file hash inventory and full synthetic test harness remain reviewer-reported, not independently reproduced here.

## Accepted findings and amendments

| Finding | Source / verification here | Revision-2 disposition |
|---|---|---|
| Selector collision, named historical trio vs available-voter evaluator | Both reviews; code and decision receipt inspected here | Retain mechanism; expand to named two-way electorate too |
| `avg_p` mixes source averages and model probabilities | Both reviews; literals inspected here | Explicit finding; do not pool meanings or infer model confidence from source average |
| Provenance added to regular rows changes canonical late-addition admission | Review 2; temporary-directory control reproduced here | First stage sidecar-only; frozen-payload comparison unchanged |
| Full pick copied into Supabase `source_payload` | Review 2; code inspected here, sync control not rerun | Full payload/manifests included in parity contract |
| Model/consensus emissions with same fixture/selection/rule share existing shadow ID | Review 2; same-ID in-memory control reproduced here | Separate signal and observation identities; retain existing operational IDs |
| Equal representative tuples make survival order-sensitive | Review 2 experiment; tuple/max logic inspected, evaluator tie not rerun | Deterministic evidence, baseline parity per ordering; new representative policy separate |
| `min_p` and home-only violations | Review 2 synthetic controls; full controls not rerun | Add explicit proposed-policy tests and predicate requirements |
| Historical trio plus dissenting extra voter can be rejected | Review 2 synthetic control; live all-voter agreement inspected | Isolate exact-elector vs available-voter policy in comparison |
| OU-only registry can enable 1X2 fallback while `is_fallback=False` | Review 2 control; branch structure inspected, control not rerun | Explicit fallback-origin receipt and adversarial test |
| ML-labelled counts include consensus emissions | Review 2; `n_ml` and `ml_meta_state.json` code inspected here | Sidecar inference/emission counts; existing state unchanged in audit stage |
| Fade qualifies on parent probability, displays complement | Review 2; fade code inspected here | Parent/target/qualification receipts; complement is not opposite-side 1X2 probability because draws exist |
| Replay needs guard, derived features, identity, context and ticket state | Review 2; rolling-hit-rate dependency inspected | Expanded point-in-time manifest; missing dependencies declared |
| Decay uses guarded prediction exports, not archived labels | Review 1; decay view/export code inspected here | Record bounded observation; include fade research and state consumers |

## Attribution clarification and policy boundary

### Separated-routing observation and distinct-record discrepancy

Review 1 withdraws its earlier claim that the separated-routing outcome was untested. The observation is sufficient on **Review 2's reported synthetic control**: no model, Statarea/Vitibet/Bzzoiro agreement at 70%, then in-memory family separation, produced one unanimous≥65 candidate. This is the primary attribution used here, not a historical replay or a prediction of production removals.

Review 1 also says the sentence formerly block-quoted here does not occur in its decision-record version. In **our pinned baseline**, `git show 01f580c1f41b78883d7c807e354ba76903bbd026:docs/operator/DECISIONS-2026-10-09.md` contains the no-model/current-path/Option-A/Option-B observation at lines 57–59. See [the exact source version](https://github.com/6ixtyn9-sudo/Edge-Factory/blob/01f580c1f41b78883d7c807e354ba76903bbd026/docs/operator/DECISIONS-2026-10-09.md#L49-L59). That file was not edited in proposal commit `0dac025` or this correction.

The subsequent supplied retraction resolves the nature of the discrepancy: **two independently written records share a path**, rather than a demonstrated revision history of one document. The external copy is reported as local-only at `e489654`; its bytes and full commit identity have not been retrieved here. Our record's §1 already says it transfers/re-reviews positions and is not a verbatim copy of the unavailable other-workspace document. Do not assign authorship of our record to that agent. The flattened block quote remains removed; direct reviewer-control attribution is sufficient. No additional evaluator control was rerun for this correction.

Review 1 also withdraws its broad claim that every ROI figure conditioned on `avg_p` is mixed. Both score kinds use percentage units, but represent different estimands. Untyped pooling can mix them; verified model exports and provenance-stratified cohorts require separate analysis. This aligns with revision 3's formulation.

### Can a mismatch flag justify live family-only routing?

Review 1 recommends family separation with a retained legacy label and `electorate_matched_certification=false`, while saying generic available-voter consensus stays shadow-only pending certification. Those conditions leave the operational treatment ambiguous: continuing executable generic-voter picks under a historical rule plus a false flag does not make certification valid.

Revision 2 accepts the flag **in sidecar evidence before comparisons**, not as authorization. Family-only routing and exact-elector enforcement remain separate comparison variants. Activation must specify what happens to unsupported-electorate signals. Exact enforcement may make parked historical consensus families dormant; it does not imply that all independent model/other valid candidates disappear. The blanket-suppression counterexample must not be conflated with exact enforcement of one rule family.

Correctness approval need not wait for a proven ROI uplift, but it does need an honest contract, explained effects, unchanged safety constraints and explicit operator acceptance.

## Local verification receipts

Executed with `PYTHONDONTWRITEBYTECODE=1`, in-memory records and a `TemporaryDirectory`; no provider calls or production pipeline commands.

1. **Canonical loader:** one morning row and its identical regular copy plus a late row gave `verified_late_additions=1`. Adding `prediction_provenance_version` and `emission_path` only to the regular copy gave `verified_late_additions=0` and `unsafe_regular_ledger_dates=['2026-10-08']`.
2. **Shadow identity:** `candidate_id(model_record, day) == candidate_id(consensus_record, day)` returned `True` for equal fixture/selection/rule and different emission paths.

These establish the storage/identity risks, not a full model, sync or ticket replay. Remaining reviewer controls should be implemented as reproducible temporary-state tests before instrumentation is called behaviour-preserving.

## Agreed next patch order (not executed)

1. Approve sidecar schema, signal/observation identities and bounded persistence contract.
2. Add archive, identity, ordering, qualifier, fallback, fade and hook-failure controls.
3. Add sidecar-only scoring/emission hooks and reports; no operational-object mutation.
4. Verify enabled/disabled/failure parity, including archive admission and full sync payloads.
5. Compare baseline, family-only routing and exact-contract policy on pinned inputs.
6. Resolve electorate, predicates, fallback and representative semantics.
7. Obtain separate approval for prospective versioned live activation and rollback.

**Current decision:** revise proposal only. No code, model, threshold, electorate, ticket or operational archive has been changed.


## Supplied reconciliation response (revision 3)

Disposition: **audit design approved with changes; live activation not approved**. This is conditional design agreement, not a passed implementation gate.

Accepted clarifications:

- Separated routing was observed in a synthetic control, not a historical policy replay.
- `avg_p` mixes meanings/calibration, not numerical units. Untyped pooling may mix estimands; verified exports and stratified cohorts are not automatically mixed.
- Local code inspection confirms `run_day()` zeros Forebet's effective weight after cutoff as well as `fetch_all()` excluding it. Roster retention for history is not inherently defective.
- Electorate mismatch was broadly anticipated by the original controls, but now has a mandatory concrete case.
- Required-elector abstention is not automatically the withdrawn blanket-suppression bug; independent model signals remain independent.
- Sidecar-only capture, distinct signals, per-ordering baseline parity, precise fade receipts and an expanded replay manifest remain prerequisites.

The [acceptance checklist](CHECKLIST-ML-CONSENSUS-PROVENANCE-2026-10-09.md) is the implementation handoff. No audit hooks, new tests, full replay or live routing were implemented in this documentation revision.


## Publication follow-up (revision 4)

Both current verdicts are conditional audit-design approval and no live activation. Review 2 reports no further blocking documentation correction after reading revision 3, and identifies **Gate A** as the next design deliverable: a concrete schema/storage specification with identity derivation, missing receipts, persistence/retention bounds and fail-soft hook interface, submitted for approval before coding.

This follow-up corrects review-status reporting and clarifies source-version attribution only. The proposal, checklist and handbook links are updated accordingly; acceptance boxes stay unchecked. No Gate A specification, audit implementation, new control suite, full replay or production change was performed.


## Distinct-record clarification after revision 4

The latest supplied follow-ups accept the pinned source and current conditional
verdicts; one explicitly retracts the misquotation accusation after reading our
record's §1. References to the other workspace's `e489654`, retraction sections,
convergent numerical findings and D6/D7 numbering remain **reviewer-reported**,
not newly verified experiments or imported decisions. The pasted agent labels
have varied across rounds; track claims by their supplied text and verified
source rather than infer a permanent identity from those labels.

The [handbook](README.md) now names the repository's transferred/re-reviewed
D1–D5 record as the local reference, distinguishes the unavailable independent
D1–D7 record, and requires source-qualified references. This does not reconcile
or approve external D6/D7 decisions. Gate A remains the next design deliverable;
no concrete schema, hooks, controls or deployment are authorized by this update.

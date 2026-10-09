# Independent-review synthesis: ML/consensus provenance proposal

**Date:** 2026-10-09  
**Status:** documentation only; no live-change authorization  
**Proposal:** [revision 3](PROPOSAL-ML-CONSENSUS-PROVENANCE-2026-10-09.md)  
**Local code baseline:** `01f580c1f41b78883d7c807e354ba76903bbd026`

The user supplied two independent reviews in chat. This document summarizes their material claims and dispositions; it is **not** a claim that the review agents' experiments were all repeated here. Review identifiers below are local labels, not independently verified agent identities.

## Verdicts supplied

| Reviewer | Audit stage | Live routing |
|---|---|---|
| Review 1 | Approve | Approve with changes |
| Review 2 | Approve with changes | Reject activation now; support intended correction after prerequisites |

Neither review authorizes immediate activation. Both endorse staged provenance and comparison, reject profitability promises, and require explicit electorate semantics.

**Scope limitations:** Review 1 reports a different checkout (`a189fd4` plus local commits). Both reviewed pasted proposal text rather than a proposal file in their checkout. Review 2 reports isolated synthetic evaluator controls, no full replay, and 991 repository hashes unchanged; that hash inventory and its full test harness were not supplied or independently verified here.

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

## Two disagreements requiring care

### Was the separated-routing control observed?

Review 1 calls the prior separated-routing outcome untested. However, the cited `DECISIONS-2026-10-09.md` §3 explicitly records:

> No-model 70% fixture: current path returns an ML-labelled candidate; Option A returns a unanimous candidate; Option B returns zero candidates.

Review 2 independently reports the family-separated control as well. Revision 2 retains this as an **attributed prior observation**, not a new result from this session. None of these controls demonstrates production-policy performance.

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

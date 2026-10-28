# ENH ML attribution and honest reporting — 28 October 2026

## Scope and authorization

Operator: “proceed with whats solid,” following review of two external audits.

This patch implements evidence preservation, explanation and read-only evaluation through existing components. It does **not** introduce fit rejection, z-score gates, an EV veto, an odds ceiling, a calibration policy, a new script/service/registry, or a registry backfill. It does not alter selection/staking policy or rewrite frozen or historical financial positions. No workflow or configuration changes.

## Changes

### Evidence survives the financial-history writer

`auto_tickets._settled_leg_record` now copies existing ENH cohort/model/ranking evidence when present, including `prob`, `cohort_evidence`, `ml_rank_probability`, `ml_model_key`, `ml_model_schema`, `ranking_basis`, `ml_ordering_active`, floor metadata, league, shadow and kickoff provenance. Nested evidence is deep-copied so later mutation cannot rewrite the stored snapshot.

Legacy legs are not enriched by guessing. Ordinary Main legs retain their old record shape. Verified regrading preserves enriched fields and remains idempotent.

The existing `enhancement_legs` → `enhancement_pool` → `_carry_lane_evidence` path carries the model schema. The shared selector reports its actual ML-active state and whether capacity rescue was checked or changed the chosen pair. These are observations, not selection inputs. The planner stores each leg's actual ranking basis, independent of the environment used to read the card later.

### Cards explain the ordering basis

New ENH cards retain the existing parent-cohort clause and “not fixture probability” warning, then show the model score/schema/key prefix or cohort ordering. Mixed coverage explicitly distinguishes the unscored cohort group under an active ML policy. Legacy records without the ranking-policy evidence remain “provenance unavailable”; no current environment flag is used to invent the old policy. The summary's retained model-key count concerns the card, not all fitted models in the warehouse.

### Existing decision-parity report gains same-receipt comparisons

Run the existing command:

```sh
PYTHONPATH=src python scripts/replay_harness.py --decision-parity
```

For valid ENH receipts, `ml_comparison` runs the shipped `plan_ticket_decision` twice on the **same prepared pool, captured options and captured bank**, changing only `ml_enabled`. It reports:

- Both execution identities, selected quotes, compound odds and actual planner-sized stakes.
- Added/removed execution legs and their symmetric difference (these counts include book/quote changes, not just fixture changes).
- Model-schema counts, retained model keys, available descriptive fit diagnostics, and model/cohort disagreement.
- Whether each arm engaged ML ordering, checked capacity rescue, or changed a pair through rescue. The comparison does not claim to isolate a causal model effect from that pairing difference.
- Known outcomes and accumulator payouts only when independently retained frozen ledger identity and freeze time match the receipt. The existing `_graded_acca` handles loss/void rules and shipped odds rounding.

Drafts remain selection comparisons, **not executed or settled money**. Results are joined only on the same date and exact match/market/selection. Outcomes absent from the retained ledger remain unknown. A confirmed losing leg can resolve a losing accumulator; otherwise incomplete outcomes do not become a zero return. No provider, result resolver, settlement or training call runs inside this comparison. In particular, this patch does **not** multiply leg probabilities to present a fabricated joint expected return.

The ENH report also gains `attributed_scores`: fixture-balanced descriptive Brier and log-loss results, separated by retained model schema, with record/fixture counts and missing-attribution denominators. These describe booked legs only, not selection uplift or an independent sample. Log-loss clips probabilities to `[1e-15, 1-1e-15]`. No minimum sample is represented as proof of calibration or profitability.

### Legacy replay is explicitly unproven

`_slate_rows` now shares the existing archive loader's morning-authority/late-addition resolution. It does **not** splice a later model or priced note into an earlier baseline row. Main archive-loading policy and the certification registry writer are unchanged.

Legacy ML coverage reports schema, model key, source archive when established, build timestamp and `UNPROVEN_ARCHIVE`. Unknown provenance stays null. Mixed schemas suppress the pooled ML delta. The false “single-feature logistic, therefore equivalent by construction” explanation has been removed. Equal aggregate bet/hit counts no longer imply equal cards. Authentic decision receipts are the preferred matched-evaluation boundary.

An additional reporting defect was found during implementation: the legacy score map used only `(day, contract, market)`, so one fixture could overwrite another fixture's score on the same contract. The read-only replay key now includes both fixture participants; regression coverage pins distinct scores on the same day/contract/market.

### Fit support is described, not gated

`enhancement_cohort` adds a sibling `ml_fit_adequacy` block with sample size, class counts/minimum, served dimensions, stored coefficient count and **mean rows per class**. The latter is deliberately not called EPV. None is a threshold or validation verdict.

This block is outside `ml_model`, hence outside its hash and input-receipt binding. The actual learner, inputs, regularization, model payload and probabilities remain unchanged. Future captured pool rows carry these descriptors into the existing report; legacy descriptors are unavailable rather than reconstructed.

### Checkout/config provenance is bounded honestly

New decision receipts include `execution_provenance`: checkout HEAD and relevant file hashes at receipt capture, alongside the event SHA/run ID when available. A frozen receipt remains write-once.

`phase5_persistence.persist_localdata` records its **pre-persist HEAD**, verified-results file hash and event SHA in the existing persistence commit message **before commit/pull/rebase**. A concurrent-rebase regression verifies the original observation survives the rebase. Missing optional config provenance does not prevent publishing.

These fields identify their capture boundary. They do **not** claim that the GitHub event SHA or pre-persist HEAD proves the revision used by every earlier subprocess. Recording a hash is not an approval or a score-fact authenticity check.

## Validation

Final full suite:

```text
PYTHONPATH=src:. .venv/bin/python -m pytest -q
4738 passed, 1 skipped in 260.69s
```

Focused coverage includes provenance retention/deep-copy, legacy history shape, idempotent enriched regrading, ranking display independent of environment, mixed coverage, fixture-specific replay scores, morning authority and late additions without later-evidence splicing, mixed-schema delta suppression, counterfactual missing outcomes, void/early-loss payouts, visible capacity rescue, descriptive scoring denominators, descriptor/hash isolation, and provenance surviving a concurrent persistence rebase.

Additional read-only baseline comparisons:

- Both ML-on and ML-off plans for the retained October 28 ENH receipt have **identical execution identities and stakes** under pre-patch and patched planners.
- A synthetic 100-row fit produces an **exactly identical complete model payload and hashes** under pre-patch and patched cohort functions. Only the sibling diagnostics are added.
- Existing receipt parity remains **PARTIAL**, not a historical pass: the October 28 draft matches, but legacy receipts remain missing. Temporary report output was kept outside the repository.
- `git diff --check` passes. No tracked `localdata`, `Config` or workflow files were changed.

One intermediate full run found a test double assuming every subprocess call was a pick rebuild. The double now distinguishes the new read-only Git provenance query from the single rebuild; no extra prediction build/provider call was introduced. The final full suite above passes.

## Remaining gaps / not authorized by these changes

- Do not interpret the external audits' “ML never changed a settled card” assertion as proven by incomplete archives. No attribution is invented for old history.
- The certification registry may still omit authentic decision-time ENH evidence when only a rewritten daily archive survives. Safely repairing that requires an authenticated decision source, not merely a richer later row. No registry population/floor backfill or dedup migration was performed here.
- Counterfactual markets not actually booked often lack outcomes in the financial ledger. This patch reports that coverage gap; it does not manufacture a complete P&L comparison.
- Historical result/period provenance and missing production warehouse data remain limitations. Correct replay of a captured input does not prove that input was right.
- This is observability and correctness work, **not model tuning or evidence of profitable uplift**. Further ranking/model changes require their own evidence and approval.
- No merge or workflow dispatch is included. The separate regulation correction remains the existing reviewed regrade/persistence path, not a financial edit in this patch.

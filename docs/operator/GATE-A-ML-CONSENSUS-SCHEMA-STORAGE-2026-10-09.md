# Gate A: ML/consensus sidecar schema and storage specification

**Date:** 2026-10-09 (SAST)<br>
**Specification:** `mcp-audit/v1`, draft 1<br>
**Status:** PROPOSED — explicit Gate A approval requested; not implementation acceptance.<br>
**Parent:** [revision-4 proposal](PROPOSAL-ML-CONSENSUS-PROVENANCE-2026-10-09.md), [acceptance checklist](CHECKLIST-ML-CONSENSUS-PROVENANCE-2026-10-09.md)<br>
**Inspected code baseline:** `01f580c1f41b78883d7c807e354ba76903bbd026`; documentation through `d0bcd02`.<br>
**Scope of this publication:** documentation only. No recorder, hooks, operational schema, storage integration, workflow changes or replay were implemented.

## 1. Approval boundary

Approve the contract below before writing audit code. Approval would authorize a separately reviewed implementation and synthetic failure/parity controls, not acceptance of that implementation or live activation. Gates B–F remain unchecked. The repository's transferred/re-reviewed D1–D5 [decision record](DECISIONS-2026-10-09.md) is the local reference; this document does not import the independent external D1–D7 record.

Non-negotiable invariants:

- Operational rows and their nested dictionaries, full exported/source payloads, existing IDs, representative choice, order, archive admission/equality, model/guard decisions, registry, thresholds, prices, notifications, tickets and frozen state remain unchanged.
- No sidecar field enters an operational row, research ledger, Supabase pick payload or selection predicate. No production consumer consults this stream for qualification.
- Capture evidence when it is computed; never reconstruct lost model/consensus evidence from the collapsed survivor. A mismatch annotation does not repair certification or authorize routing.
- No model promotion, new tie-break, reclassification of historical rows, workflow edits or alteration of another audit ledger under this approval.

## 2. Record model and serialization

One UTF-8 JSON object per LF-terminated line; no NaN/Infinity. Writer uses schema-specific immutable primitive values, never live pick dictionaries. Records are append-only within a build segment. Corrections are new records referring to the superseded receipt, never edits. JSON field order and stream arrival order have no analytical meaning; sequence and representative mappings preserve operational ordering explicitly.

All IDs use full lowercase SHA-256, not truncated hashes. Define `H(tag, object)` as SHA-256 of UTF-8 `tag + "\n" + C(object)`. `C` recursively sorts object keys, preserves array order, uses compact separators, `ensure_ascii=False`, and `allow_nan=False`; identity material is restricted to strings, integers, booleans, arrays, objects and null (no floats). Preserve raw text separately; do not trim/case-fold identity fields except through the explicitly versioned identity contract. Content digests use the same encoding with captured finite numeric values; producer/runtime version is pinned because numeric serialization is not claimed cross-language canonical. Raw dependencies have separate byte-level digests.

### 2.1 Common envelope (all fields required)

| Field | Type / meaning |
|---|---|
| `schema_version` | Literal `mcp-audit/v1` |
| `record_type` | `build_open`, `signal_observation`, `representative_link`, `diagnostic`, `build_close` |
| `build_id` | `mcb1:<sha256>`; §3 |
| `record_id` | `mcr1:<sha256>` = H(`mcp-record-v1`, entire record excluding `record_id`) |
| `sequence` | Nonnegative integer; unique, increasing within one producer/build |
| `recorded_at_utc` | RFC3339 UTC timestamp, audit timing only |
| `body` | Typed body below; no arbitrary operational row dump |

Unknown record types/major schema versions are rejected by offline readers. Unknown required semantics are not silently accepted. New optional extensions require a minor-contract review and explicitly namespaced extension area; v1 has none. A future schema must not rewrite v1 receipts.

### 2.2 Evidence wrapper

Every computed receipt and every dependency reference uses the following discriminated wrapper:

- `{"state":"observed","value":<typed value>,"reason":null}`: copied at the actual computation point.
- `{"state":"missing","value":null,"reason":<code>}`: expected receipt unavailable.
- `{"state":"not_applicable","value":null,"reason":<code>}`: genuinely not part of this emission path.
- `{"state":"failed","value":null,"reason":<code>}`: capture/computation failed; not a substitute operational result.

Reasons are enum codes, not exception text or secrets: `hook_not_reached`, `receipt_not_exposed`, `dependency_unavailable`, `ambiguous_identity`, `no_inference`, `path_not_applicable`, `serialization_error`, `size_limit`, `writer_error`, `budget_exceeded`, `capture_error`. Additions require review. Unknown is never 0, an empty electorate, false certification, an invented feature-contract version or a synthetic model prediction. A missing wrapper makes the record invalid; a valid missing receipt makes the relevant analysis incomplete.

Dependency `value` is `{logical_name, version, sha256, size_bytes, as_of_utc, location_ref}`. Unavailable members have explicit nulls plus `missing_members` and cannot establish complete replayability. `location_ref` is a credential-free relative content-addressed or approved artifact reference, not an expiring signed URL. A digest alone does not prove bytes are retrievable.

## 3. Identity derivation (sidecar only)

### 3.1 Build and occurrence references

`build_id = "mcb1:" + H("mcp-build-v1", {producer, invocation_id, trading_date, code_sha})`. CI producer is a job identifier, invocation includes run ID, run attempt and invocation counter. Local producer uses a newly allocated invocation UUID. Restart/re-execution gets a new invocation; retrying an existing completed artifact does not. Synthetic harnesses pin invocation IDs explicitly. Open receipt pins source state separately; changing model/input snapshots changes observations, not the logical signal identity.

Fixture-occurrence identity material:

```
{identity_contract, entity_map_sha256, trading_date,
 home_entity_key, away_entity_key, competition_key,
 squad_discriminators, kickoff_anchor}
```

`kickoff_anchor` contains the captured UTC instant and timezone/normalization contract, or explicit nulls. `squad_discriminators` preserves women's/youth/reserve qualifiers for each side. No new fuzzy aliasing or reschedule merging is introduced. This uses a reviewed sidecar identity contract, pinned entity-map bytes and captured existing normalization results; it does not call an ID-producing routine that can mutate operational state.

`occurrence_ref` is a wrapper whose observed value is `{id, material, strength}`; `id = "mco1:" + H("mcp-occurrence-v1", material)`. `strength` is `anchored` or `partial`. Missing kickoff/competition/entity/squad evidence must be enumerated in `missing_identity_members`. A partial reference is only usable inside this build; include `{build_id, fixture_input_ordinal}` in its hash material. Never unify partial references across builds. Multiple source records believed to represent one fixture may be linked by an explicit captured input-group reference; do not infer a cross-build equivalence from matching date/team text. Ambiguous fixtures remain separate and are excluded from comparisons needing assured occurrence equivalence. Raw date/team/competition/kickoff strings are retained in the identity receipt for diagnosis.

`selection_ref = "mcq1:" + H("mcp-selection-v1", {occurrence_id, market, selection, line})`: market/selection use an enumerated, versioned vocabulary (`1X2` with `home`, `draw`, `away` initially); line is null for 1X2. No home/away swapping. Non-1X2 paths are unsupported for v1 instrumentation, not silently mapped to 1X2.

### 3.2 Signal and observation identities

`signal_id = "mcs1:" + H("mcp-signal-v1", {selection_ref, emission_path, rule_contract_id, model_contract_id, feature_contract_id, election_contract_id, qualification_contract_id})`.

- `emission_path`: `model_certified_tier`, `consensus_unanimous`, `model_fade`. A legacy ML label on consensus remains `consensus_unanimous`.
- Contract IDs are versioned semantic identifiers or immutable contract digests, not display labels. A rule receipt includes raw label and parsed qualifiers. Model contract is not the mutable fitted-model blob digest; that digest belongs in evidence. Paths not using a contract use an explicit null plus a `not_applicable` receipt.
- A required contract that cannot be identified makes identity partial; hash a tagged unknown contract plus build/attempt ordinal and flag `identity_complete=false`. It cannot be used for cross-build signal aggregation. Never guess it from the surviving rule label.
- Scores, price, bucket, fitted-model snapshot and timestamps are observation evidence, not logical signal identity. Distinct paths for the same fixture/selection/rule cannot collide.

`observation_id = "mcv1:" + H("mcp-observation-v1", {build_id, signal_id, emission_attempt_ordinal})`. Every evaluated emission attempt gets a monotonically assigned ordinal in that build; two attempts for the same signal remain distinct. Retransmission preserves the observation and record IDs. Duplicate record IDs with identical bytes are deduplicable; different bytes for the same ID are corruption, quarantined offline. Existing `scs1`, pick/ticket/notification IDs are optional read-only link receipts, never substituted for these identities.

Deterministic evidence means the same pinned inputs/contracts yield the same logical IDs and evidence digests, with set-valued evidence sorted by source ID. Build IDs, timestamps and observation ordinals are intentionally run-specific. Original evaluation/arrival order is separately retained. Do not promise byte equality across permutations or a new representative tie-break.

## 4. Typed bodies and computation-point receipts

### 4.1 `build_open`

Required body fields: `trading_date` (ISO date), `producer` (string), `invocation_id` (string), `code_sha` (full Git SHA), `dirty_patch_sha256` (wrapper), `runtime` (Python/platform/dependency-lock references), `audit_config` (enablement, budgets, storage contract), `input_manifest` (array of dependency wrappers), `coverage_scope` (supported paths/markets and instrumented computation points), `operational_comparator_contract` (whole-payload comparator version/reference).

The input manifest inventories source snapshots and date eligibility/retirement policy; model blob, guard and activation receipts; feature contract and warehouse-derived rolling-hit-rate facts; registry, entity overrides, purity/context/debias/veto state; as-of, competition/price facts; and ticket/bank/ladder/freeze state when ticket replay is in scope. It records missing dependencies, not just paths. Guard rejection/missing model is an observed baseline decision when actually known, not a fabricated inference. No fetching, fitting or repairing dependencies from audit hooks.

### 4.2 `signal_observation`

Required fields: `observation_id`, `signal_id`, `identity_complete` (boolean), `occurrence_ref`, `selection_ref` (wrapper), `emission_path`, `emission_attempt_ordinal`, `input_order` (captured evaluation ordinal), `rule_receipt`, `model_receipt`, `consensus_receipt`, `fade_receipt`, `context_price_receipt`, `input_snapshot_refs`, `inference_attempt_ref` (wrapper), `baseline_decision`, `operational_links`, `evidence_sha256`. All receipt fields use §2.2 wrappers. `evidence_sha256` covers body except IDs/digest, build-specific ordinals and operational links; it does not claim input permutation invariance for order-sensitive evidence.

Typed observed receipt values (each member below is required; unavailable subreceipts use §2.2 wrappers, not invented defaults). Receipt values carry `missing_members` and `failed_members` arrays so a partially observed receipt is not mistaken for complete evidence:

| Receipt | Required captured value members |
|---|---|
| `rule_receipt` | raw/display rule, registry entry ID/digest, family and parsed market/side/min-p qualifiers, nominal cut, effective competition-adjusted cut, adjustment receipt, origin (`registry`, `default_1x2_fallback`, `other`), legacy fallback flag, certification contract reference |
| `model_receipt` | model/feature/election/qualification contract IDs, model bytes reference, guard/activation decisions and references, feature names **in model order**, actual vector `x`, imputation mask, trained fallback means actually used, transformed `z` when used, target selection, target-election predicate and actual electors, all feature suppliers with observed/missing/available flags, inference score (`value`, `unit=percent`, `meaning=model_target_probability`), tier evaluated/selected and qualifying predicate result |
| `consensus_receipt` | election contract ID, actual eligible electorate, observed suppliers/votes/sides/probabilities, missing/abstaining/ineligible sources with reasons and date-eligibility receipt, agreement predicate/result, qualifying average (`value`, `unit=percent`, `meaning=source_average`), actual averaging members and weights/denominator, nominal/effective thresholds, supported historical certification electors/predicate, certification comparison |
| `fade_receipt` | parent observation reference or explicit missing reference, parent target, parent model score/threshold/predicate, emitted opposite target, legacy complementary display (`meaning=legacy_parent_complement`), contract reference, settlement convention `draw_loses_parent_and_fade` |
| `context_price_receipt` | copied baseline context/debias/veto/competition decisions and their dependency references; captured price/provider/as-of/quarantine/floor result when evaluated; wrappers for decisions not yet reached |

`baseline_decision` is `{state: emitted|not_emitted|unknown, reason_code, emitted_row_ordinal}`; emitted ordinal is null unless emitted. An emission observation is not necessarily a selected operational pick. Missing capture does not change a baseline decision. Inference execution without a qualified emission must still be counted through captured inference attempt receipts/diagnostics, rather than treating emitted-signal count as inference count.

Certification comparison is `{status: matched|mismatched|unknown|not_applicable, reasons, required_electors, actual_electors, required_predicate_ref, actual_predicate_ref}`. Reasons include missing required elector, extra voter predicate, qualifier mismatch, threshold mismatch, fallback-origin mismatch or unavailable contract/evidence. Compare actual eligible voters and the actual qualifying predicate, not static source roster or label alone. A known electorate mismatch can be recorded even if other comparison inputs are missing; enumerate which facts are known and which remain unknown. Required-elector abstention does not suppress independent model evidence.

Set-valued elector/supplier arrays have unique stable source IDs and canonical source-ID ordering, plus separate captured iteration ordinals when evaluation used order. Numbers are copied in their actual units and meaning; do not normalize/round for identity or infer calibration equivalence. Derived features include the actual values used, not merely declared source names. Sensitive credentials, provider auth headers and unbounded exception messages are prohibited.

### 4.3 `representative_link`

Capture after the **unchanged** final consolidation. Required body: `collapse_contract_ref`, `input_row_ordinals`, `supporting_observation_ids`, `unlinked_input_ordinals`, `representative_input_ordinal` (wrapper), `output_row_ordinal`, `operational_identity` (wrapper), `precollapse_row_sha256` (wrapper), `final_whole_row_sha256`, `link_state` (`complete`, `partial`, `missing`), `reason_codes`.

Hashes here are read-only whole-row serialization receipts, not replacement canonical equality keys. Preserve the exact baseline clustering, representative and output order for each original input ordering. Link all known supporting signal observations without adding a list to the operational row. Final bucket/duplicate metadata may derive from other inputs; do not attribute those changes solely to the representative. If a safe mapping cannot be captured without changing collapse behavior, use partial/missing links; do not infer the winner by matching final labels/scores. A later implementation must prove that read-only row ordinals and the representative mapping do not alter clustering, alias guards or ties. Reimplementing collapse in the recorder is prohibited.

### 4.4 `diagnostic` and `build_close`

Diagnostic body: `stage`, `code`, `affected_observation_id` (wrapper), `count`, `coverage_effect`, `inference_attempt_receipt` (wrapper). An observed inference attempt receipt contains a build-unique attempt ordinal, occurrence/target references, model/feature/guard references and executed/skipped status; emission observations reference it to avoid double-counting shared inference. No diagnostic affects operational exit status or logs used as qualification state.

Close body: `last_sequence`, `counts_by_record_type`, `inference_attempts_observed`, `emissions_by_path`, `dropped_counts_by_reason`, `coverage` (`complete`, `partial`, `unknown`), `close_reason`, `segment_bytes`, `segments` (names, byte digests and sizes), `persistence_state` (`local_only`, `export_verified`, `failed`, `unknown`). A separate export manifest attests upload status after closing; never modify a closed receipt to claim export. Before close, rotate to a separate final close segment. Its `segments` list hashes preceding finalized segments only; manifest hashes every final file including the close segment (no self-hash cycle).

No close receipt, missing segment, dropped event, partial link or required missing dependency means incomplete coverage for the affected analysis. Absence of a sidecar is **unknown/not instrumented**, not zero signals or a clean pass. Complete capture is not complete historical replay: readers independently check retrievable point-in-time dependencies and mark affected comparisons non-replayable.

## 5. Fail-soft hook interface and resource limits

Proposed interface (descriptive, not executable API):

```
open_build(copied_build_receipt) -> audit_handle_or_disabled
try_capture(handle, stage, bounded_primitive_receipt) -> void
try_link(handle, bounded_primitive_link_receipt) -> void
try_close(handle) -> void
```

Default is **OFF** under a new flag `EDGE_FACTORY_MCP_AUDIT`; only explicit `1` enables it. Do not inherit default-ON `EDGE_FACTORY_SCORED_SHADOW` behavior or reuse its recorder/IDs. Enablement is audit-only and prospective, after implementation acceptance.

Hooks have no return value consumed by selection, no I/O/network/model work on the scoring thread, and no mutation of any caller object. Capture finite, size-checked primitive values directly where feature vectors, guard results, electors, thresholds and fade parent scores are available. Allocate copies of required small arrays; never deep-copy an arbitrary graph, call arbitrary `repr`, recompute model features, or pass a mutable object to an asynchronous writer. Serialization/hashing/disk I/O run in a separate best-effort writer using a bounded nonblocking queue. Writer startup, queue enqueue and close failures disable/drop audit collection only. Catch ordinary capture/writer exceptions at the audit boundary; do not swallow baseline scoring exceptions or process termination signals.

Proposed hard resource bounds (approval requested):

| Resource | v1 bound / overflow behavior |
|---|---|
| Receipt | 256 KiB serialized; maximum 512 features and 64 suppliers; otherwise drop with reason, never truncate into a seemingly complete receipt |
| Queue | 128 receipts and 8 MiB aggregate reserved byte budget, whichever first; nonblocking drop on full |
| Build | 10,000 records or 32 MiB, whichever first; reserved 64 KiB within budget for close/diagnostics |
| Local spool | 512 MiB total and maximum 30 days; §6 |
| Shutdown | At most 1 second best-effort writer drain; no synchronous fallback on scoring path; unfinished build partial |

These are proposed safety limits, not measured runtime guarantees. Gate B/C must measure disabled/enabled/failed capture overhead (target p99 <1 ms per capture on a pinned representative workload) and prove bounded memory, no blocking queue/disk work and no shared-object mutation. A post-call clock check is not a hard latency guarantee; unexpected long operations must be eliminated by design and tests. If bounds cannot accommodate the actual contract, revise Gate A rather than silently weakening coverage. Use bounded, best-effort diagnostic counters; if even diagnostics fail, the missing close/coverage receipts must expose incompleteness. Audit failure must not withhold picks or alter pipeline return status. No Python mechanism is claimed to isolate whole-process OOM or host failure; resource stress tests and honest residual-risk reporting are required.

## 6. Storage, export, retention and recovery

### 6.1 Proposed layout and ownership

Use a new, separate, **untracked** spool:

```
localdata/ml_consensus_audit/v1/YYYY-MM-DD/<build_id>/
  records-000001.jsonl
  build-manifest.json
  inputs/<sha256>                 # only approved, bounded dependency copies
```

Schema documents/test fixtures are tracked; production receipts and datasets are not. Each invocation owns a separate directory; one writer per segment, no shared-file append, no Phase5/scored-candidate ledger reuse. Paths are validated under this root; no symlink traversal or deletion outside it. Input snapshots already stored durably may be referenced instead of copied, but retrievability must be verified. Required bytes that exceed budget are recorded as missing, not silently fetched later. This spool is ignored by existing `localdata/*` rules; ignored does not mean protected or persisted.

**Observed integration gap:** `scripts/phase5_persistence.py` protects/merges only named existing paths; its cleanup is not an allowlist for this new directory. `.github/workflows/daily.yml` caches `localdata`, but cache is opportunistic, not durable storage. Main artifacts select top-level txt/json/md and explicit Phase5 directories; the separate scored-candidate artifact selects only its existing JSONL family. Neither uploads this layout. `clean_localdata.py`'s dated telemetry retention is a separate mechanism, not a storage contract for it.

### 6.2 Proposed durable route — blocked pending explicit integration review

Proposed stage-one route is a **dedicated per-invocation CI artifact**, named `ML-Consensus-Audit-v1-<run_id>-<attempt>-<invocation>`, with 30-day retention and all completed/partial segments plus checksum/coverage manifest. Upload is best-effort/always-run and cannot gate operational output. Proposed integration must use audit-only failure handling and report export failure separately without changing the operational job conclusion. It must occur before any cleanup that could remove the spool. A separate, reviewed persistence exclusion protects the new directory through cleanup until upload/expiry; it must not add it to git staging/union merges. Local runs explicitly export the same manifest bundle; otherwise marked local-only.

This requires later review of workflow and cleanup integration. The GitHub App workflow-write constraint documented in the operator handbook requires an authorized maintainer route for workflow edits; this publication makes **none**. Do not sidestep it by nesting this stream in an existing Phase5 artifact directory or hiding data in top-level report JSON. Without that approved route, implementation may be tested in temporary storage only; production enablement is blocked. Cache recovery must not be advertised as durable acceptance.

Thirty days is a bounded investigation window, not indefinite replay preservation. Long-term pinned comparison packages require a separately approved external archive/retention owner; none is selected here. Before a replay decision relies on receipts, export the required bundles/dependencies, verify digests and document the independent retention location. Expired/missing bytes make affected comparisons non-replayable, even if their digests remain in a report.

### 6.3 Atomicity, limits and corruption

Append complete lines in the writer; rotate at 4 MiB (a single bounded line may exceed the rollover target). Finalize manifest by temp-file plus atomic rename, including byte hashes, sizes, ordered segment list, coverage and dependency availability. Partial/crashed builds retain discoverable partial files. Offline readers ignore an unterminated tail as corruption and report its coverage loss; they never "repair" bytes or merge it into an operational archive.

Export receipt records artifact name/ID, retention deadline, manifest digest and verification result; an upload attempt is not verification. Download/checksum verification may be a separate audit job, never a scoring hook. No verified download means export remains unverified. Deduplicate exact IDs/bytes only; conflicting record IDs or manifest hashes are quarantined with explicit diagnostics. No last-write-wins across invocations.

Spool cleanup only targets this validated root, oldest finalized builds first. Keep within both 30 days and 512 MiB, inclusive of dependency copies. Delete acknowledged-export builds first. If bounds require deleting an unexported finalized build, record a loss manifest when possible and mark retention loss; never silently count it as complete. Active builds are not deleted; when space cannot safely be reclaimed, new audit writes stop with partial/failed coverage rather than blocking operational execution. An expired artifact is unavailable even if a cache happens to contain some old bytes; any recovered bytes need fresh manifest verification. No unbounded preservation exception or large tracked data dump.

## 7. Required acceptance receipts (not executed)

Before Gate C acceptance, provide commands, pinned code/input hashes and expected/actual results for:

1. Schema validation for every body/wrapper; unknown versions, bad enum/types, nonfinite floats, oversized receipt, malformed tails and duplicate-ID corruption rejected offline.
2. Same occurrence/selection/rule from model and consensus: distinct signals, two observations, one unchanged baseline operational representative. Repeated attempts remain distinct; upload retry deduplicates exact records.
3. Missing kickoff/competition and women/youth/reserve ambiguity: no unsupported cross-build merge. Alias-map or contract revision changes references explicitly.
4. Actual `x`/imputations/`z`, guard/activation, exact election, weighted-average denominator, qualifier/effective threshold and fallback-origin receipts match computed inputs in synthetic controls.
5. Fade parent qualification/display distinction, independent inference counts, required-elector abstention and observed/missing/mismatched certification states.
6. Equal-rank input permutations: preserved baseline representative/full payload **per ordering**, evidence/link completeness without imposing new sort or operational ID.
7. Disabled/enabled/serialization failure/queue saturation/disk failure/startup failure/shutdown timeout: whole-payload, archive admission/unsafe-date receipts, ticket/state, price guards, research outputs and notifications identical to baseline.
8. Cleanup/upload ordering, checksum verification, lost export, 30-day expiry, size cap, interrupted append, recovery and concurrent invocations; no new data staged into Git or mixed into another ledger.
9. Dependency missing/expired cases: affected replay comparisons non-replayable, partial diagnostics explicitly partial. No retrospective filling from current state.

Only documentation whitespace, links and contract consistency are checked at publication. No executable schema validator, implementation test, export verification or full replay is claimed here.

## 8. Decision requested from reviewers/operator

Approve or amend explicitly:

- **A1:** v1 envelope/typed receipts, missing-evidence semantics and computation-point capture (§2/§4).
- **A2:** sidecar-only identities, partial-identity isolation and exact baseline representative links (§3/§4.3).
- **A3:** default-OFF fail-soft interface, resource/latency targets and residual-risk tests (§5).
- **A4:** untracked bounded spool, dedicated artifact route, authorized maintainer integration prerequisite and 30-day retention/expiry semantics (§6).

**Current disposition:** all four decisions pending. Publication is not Gate A approval. After approval, implement only audit collection and adversarial controls on this branch; obtain Gate C acceptance before prospective audit enablement. Live routing, operational schema migration and longer-term storage remain separate approvals.

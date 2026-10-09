# Gate A: ML/consensus sidecar schema and storage specification

**Date:** 2026-10-09 (SAST)<br>
**Specification:** `mcp-audit/v1`, draft 3 — separates index publication; refusal-only unexported retention<br>
**Status:** AMENDED / APPROVAL PENDING — A1–A3 have renewed technical design approval; A4 amendment and operator authorization remain pending; not implementation acceptance.<br>
**Parent:** [revision-4 proposal](PROPOSAL-ML-CONSENSUS-PROVENANCE-2026-10-09.md), [acceptance checklist](CHECKLIST-ML-CONSENSUS-PROVENANCE-2026-10-09.md)<br>
**Inspected code baseline:** `01f580c1f41b78883d7c807e354ba76903bbd026`; draft-2 review pin `49a83da64e1ff0ea103177abd69ce6cba5188d0c`.<br>
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

All hashes use full lowercase SHA-256. There are two distinct hash domains:

- **Logical identity:** `HI(tag, object)` = SHA-256 of UTF-8 `tag + "\n" + CI(object)`. `CI` accepts only exact strings, signed-64-bit integers, booleans, arrays/objects and null, **no floats**. Its schema fixes every key and preimage (§3/§9). Preserve raw text separately; no unspecified trimming, case folding or removal of fields named `id`.
- **Content:** `HC(tag, object)` uses the same encoding with `CC(object)`, which additionally allows finite binary64 floats. `record_id` and `evidence_sha256` are content digests, not float-free identities. Raw dependency and file digests hash bytes directly, without JSON conversion or a tag.

`CI`/`CC` use recursively sorted object keys, preserve array order (unless a specified set projection sorts it), compact separators, `ensure_ascii=False`, `allow_nan=False`, strict UTF-8 without BOM, and no Unicode normalization. Reject duplicate object keys, lone surrogates, nonfinite numbers, numeric subclasses and out-of-range integers. Pin CPython version/build and dependency/runtime contract; no cross-language canonical float claim. Preserve `-0.0` if computed. Canonical record bytes are `CC(complete_record) + "\n"`. Noncanonical encodings (including reordered keys, alternate float spellings or CRLF) are rejected by v1 readers as encoding errors, not accepted as a second encoding of one record. Canonical exact duplicate bytes are deduplicable; different accepted bytes with the same record ID mean corruption. File digests include their actual LF bytes; logical/content preimages do not include a trailing LF.

### 2.1 Common envelope (all fields required)

| Field | Type / meaning |
|---|---|
| `schema_version` | Literal `mcp-audit/v1` |
| `record_type` | `build_open`, `inference_observation`, `signal_observation`, `representative_link`, `diagnostic`, `build_close` |
| `build_id` | `mcb1:<sha256>`; §3 |
| `record_id` | `mcr1:<sha256>` = HC(`mcp-record-v1`, complete envelope with only its top-level `/record_id` omitted) |
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

Reasons are enum codes, not exception text or secrets: `hook_not_reached`, `receipt_not_exposed`, `dependency_unavailable`, `ambiguous_identity`, `no_inference`, `path_not_applicable`, `serialization_error`, `size_limit`, `writer_error`, `budget_exceeded`, `capture_error`, `startup_not_ready`, `queue_contention`, `closing`, `fallback_origin_unavailable`, `dependency_expired`, `abandoned_build`, `quota_unavailable`, `invariant_breach`. Additions require review. Unknown is never 0, an empty electorate, false certification, an invented feature-contract version or a synthetic model prediction. A missing wrapper makes the record invalid; a valid missing receipt makes the relevant analysis incomplete.

Dependency `value` is `{logical_name, version, sha256, size_bytes, as_of_utc, location_ref, owner_role, verification, expires_at_utc, missing_members}`. `verification` is `verified_bytes`, `unverified`, `expired` or `unavailable`, based on an external verification receipt, not an upload attempt. Unavailable members have explicit nulls plus `missing_members` and cannot establish complete replayability. `location_ref` is a credential-free relative content-addressed or approved artifact reference, not an expiring signed URL. A digest alone does not prove bytes are retrievable.

## 3. Identity derivation (sidecar only)

### 3.1 Build and occurrence references

`build_id = "mcb1:" + HI("mcp-build-v1", {producer, invocation_id, trading_date, code_sha})`. CI producer is a job identifier, invocation includes run ID, run attempt and invocation counter. Local producer uses a newly allocated invocation UUID. Restart/re-execution gets a new invocation; retrying an existing completed artifact does not. Synthetic harnesses pin invocation IDs explicitly. Open receipt pins source state separately; changing model/input snapshots changes observations, not the logical signal identity.

Fixture-occurrence identity material:

```
{identity_contract, entity_map_sha256, trading_date,
 home_entity_key, away_entity_key, competition_key,
 squad_discriminators, kickoff_anchor}
```

`kickoff_anchor` is exactly `{utc, timezone, normalization_contract}`; `squad_discriminators` is exactly `{home, away}`, whose values are explicit squad tags (`senior`, `women`, `u21`, etc.) or null. `utc` is the captured RFC3339 UTC instant, or null; the other members are strings or null. `squad_discriminators` preserves women's/youth/reserve qualifiers for each side. No new fuzzy aliasing or reschedule merging is introduced. This uses a reviewed sidecar identity contract, pinned entity-map bytes and captured existing normalization results; it does not call an ID-producing routine that can mutate operational state.

`occurrence_ref` is a wrapper whose observed value is exactly `{id, material, strength, missing_identity_members, raw_identity}`; `id = "mco1:" + HI("mcp-occurrence-v1", material)`. `strength` is `anchored` or `partial`. Missing kickoff/competition/entity/squad evidence must be enumerated in `missing_identity_members`. A partial reference is only usable inside this build; add the exact key `partial_scope: {build_id, fixture_input_ordinal}` to its hash material (omit that key entirely for anchored references). Never unify partial references across builds. Multiple source records believed to represent one fixture may be linked by an explicit captured input-group reference; do not infer a cross-build equivalence from matching date/team text. Ambiguous fixtures remain separate and are excluded from comparisons needing assured occurrence equivalence. Raw date/team/competition/kickoff strings are retained in the identity receipt for diagnosis.

`selection_ref` is a §2.2 wrapper whose observed value is the ID string `"mcq1:" + HI("mcp-selection-v1", {occurrence_id, market, selection, line})`: market/selection use an enumerated, versioned vocabulary (`1X2` with `home`, `draw`, `away` initially); line is null for 1X2. No home/away swapping. Non-1X2 paths are unsupported for v1 instrumentation, not silently mapped to 1X2.

### 3.2 Signal and observation identities

`signal_id = "mcs1:" + HI("mcp-signal-v1", {selection_ref, emission_path, rule_contract_id, model_contract_id, feature_contract_id, election_contract_id, qualification_contract_id})`. Here `selection_ref` means its **observed ID string**, not its wrapper. All contract-ID values are exact strings or the path-specific nulls below; field names shown are literal JSON keys.

- `emission_path`: `model_certified_tier`, `consensus_unanimous`, `model_fade`. A legacy ML label on consensus remains `consensus_unanimous`.
- Contract IDs are versioned semantic identifiers or immutable contract digests, not display labels. A rule receipt includes raw label and parsed qualifiers. Model contract is not the mutable fitted-model blob digest; that digest belongs in evidence. Paths not using a contract use an explicit null plus a `not_applicable` receipt.
- A required contract that cannot be identified makes identity partial; put the exact string `unknown:<field_name>` in each unavailable required contract field, add `partial_scope: {build_id, emission_attempt_ordinal}` to the signal preimage, hash that object, and flag `identity_complete=false`. It cannot be used for cross-build signal aggregation. Never guess it from the surviving rule label.
- Applicable contracts: `model_certified_tier` and `model_fade` require all five contract-ID fields; `consensus_unanimous` requires rule/election/qualification IDs and has null model/feature IDs. An unknown selection gets a build/attempt-scoped tagged string and incomplete identity, never a guessed selection. An inherited partial occurrence also makes `identity_complete=false`; it already carries build isolation through the selection ID.
- Scores, price, bucket, fitted-model snapshot and timestamps are observation evidence, not logical signal identity. **Equal signal IDs do not imply equal fitted models**; readers must stratify model analyses by verified fitted-model byte digest (and guard/activation versions) and exclude unverifiable snapshots. Distinct paths for the same fixture/selection/rule cannot collide.

`observation_id = "mcv1:" + HI("mcp-observation-v1", {build_id, signal_id, emission_attempt_ordinal})`. Every evaluated emission attempt gets a monotonically assigned ordinal in that build; two attempts for the same signal remain distinct. Retransmission preserves the observation and record IDs. Duplicate record IDs with identical bytes are deduplicable; different bytes for the same ID are corruption, quarantined offline. Existing `scs1`, pick/ticket/notification IDs are optional read-only link receipts, never substituted for these identities.

Deterministic evidence means the same complete pinned inputs/contracts and computation order yield the same logical IDs and projected evidence digests, with set-valued evidence sorted by source ID. Build IDs, timestamps and observation ordinals are intentionally run-specific. Original evaluation/arrival order is separately retained. Do not promise byte equality across permutations or a new representative tie-break.

## 4. Typed bodies and computation-point receipts

### 4.1 `build_open`

Required body fields: `trading_date` (ISO date), `producer` (string), `invocation_id` (string), `code_sha` (full Git SHA), `dirty_patch_sha256` (wrapper), `runtime` (Python/platform/dependency-lock references), `audit_config` (enablement, budgets, storage contract), `input_manifest` (unique-name entries `{logical_name, receipt:<dependency wrapper>}`), `coverage_scope` (supported paths/markets and instrumented computation points), `operational_comparator_contract` (whole-payload comparator version/reference).

The input manifest inventories source snapshots and date eligibility/retirement policy; model blob, guard and activation receipts; feature contract and warehouse-derived rolling-hit-rate facts; registry, entity overrides, purity/context/debias/veto state; as-of, competition/price facts; and ticket/bank/ladder/freeze state when ticket replay is in scope. It records missing dependencies, not just paths. Guard rejection/missing model is an observed baseline decision when actually known, not a fabricated inference. No fetching, fitting or repairing dependencies from audit hooks.

### 4.2 `signal_observation`

Required fields: `observation_id`, `signal_id`, `identity_complete` (boolean), `occurrence_ref`, `selection_ref` (wrapper), `emission_path`, `emission_attempt_ordinal`, `input_order` (captured evaluation ordinal), `rule_receipt`, `model_receipt`, `consensus_receipt`, `fade_receipt`, `context_price_receipt`, `input_snapshot_refs` (unique-name entries `{logical_name, receipt:<wrapper>}`), `inference_attempt_ref` (wrapper whose observed value is an `mci1` ID string), `baseline_decision`, `operational_links`, `evidence_sha256`. All receipt fields use §2.2 wrappers. `evidence_sha256` is HC(`mcp-evidence-v1`, the exact positive projection in §4.5). No generic recursive ID stripping is permitted. It does not claim input permutation invariance for order-sensitive evidence.

Typed observed receipt values (each member below is required; unavailable subreceipts use §2.2 wrappers, not invented defaults). Receipt values carry `missing_members` and `failed_members` arrays so a partially observed receipt is not mistaken for complete evidence:

| Receipt | Required captured value members |
|---|---|
| `rule_receipt` | raw/display rule, registry entry ID/digest, family and parsed market/side/min-p qualifiers, nominal cut, effective competition-adjusted cut, adjustment receipt, origin (`registry`, `default_1x2_fallback`, `other`), legacy fallback flag, certification contract reference |
| `model_receipt` | model/feature/election/qualification contract IDs, model bytes dependency-name reference and `model_bytes_sha256` (wrapper for observed digest), guard/activation decisions and references, feature names **in model order**, actual vector `x`, imputation mask, per-feature actual fallback value/origin receipts (§4.2a), actual linear logit `z` when used, target selection, target-election predicate and actual electors, all feature suppliers with observed/missing/available flags, raw inference score (`value`, `unit=fraction`, `meaning=model_target_probability`), qualification score (`value`, `unit=percent`, `basis=raw_times_100`, no extra rounding), display score (`value`, `unit=percent`, `basis` identifying the actual rounding operation), tier evaluated/selected and qualifying predicate result |
| `consensus_receipt` | election contract ID, actual eligible electorate, observed suppliers/votes/sides/probabilities, missing/abstaining/ineligible sources with reasons and date-eligibility receipt, agreement predicate/result, qualifying average (`value`, `unit=percent`, `meaning=source_average`), actual averaging members and weights/denominator, nominal/effective thresholds, supported historical certification electors/predicate, certification comparison |
| `fade_receipt` | `parent_observation_ref` (wrapper for the emitted parent observation, or missing if none emitted), `parent_inference_ref` (wrapper for the full parent inference), `parent_model_receipt` (full semantic copied model receipt, not just its run ID), parent target, parent model score/threshold/predicate, emitted opposite target, legacy complementary display (`meaning=legacy_parent_complement`), contract reference, settlement convention `draw_loses_parent_and_fade` |
| `context_price_receipt` | copied baseline context/debias/veto/competition decisions and their dependency references; captured price/provider/as-of/quarantine/floor result when evaluated; wrappers for decisions not yet reached |

`baseline_decision` is `{state: emitted|not_emitted|unknown, reason_code, emitted_row_ordinal}`; emitted ordinal is null unless emitted. An emission observation is not necessarily a selected operational pick. Missing capture does not change a baseline decision. Every executed inference gets a full `inference_observation` (§4.2a), independent of emission; emitted-signal count is not inference count.

Certification comparison is `{status: matched|mismatched|unknown|not_applicable, reasons, required_electors, actual_electors, required_predicate_ref, actual_predicate_ref}`. Reasons include missing required elector, extra voter predicate, qualifier mismatch, threshold mismatch, fallback-origin mismatch or unavailable contract/evidence. Compare actual eligible voters and the actual qualifying predicate, not static source roster or label alone. A known electorate mismatch can be recorded even if other comparison inputs are missing; enumerate which facts are known and which remain unknown. Required-elector abstention does not suppress independent model evidence.

Set-valued elector/supplier arrays have unique stable source IDs and canonical source-ID ordering, plus separate captured iteration ordinals when evaluation used order. Numbers are copied in their actual units and meaning; do not normalize/round for identity or infer calibration equivalence. Derived features include the actual values used, not merely declared source names. Sensitive credentials, provider auth headers and unbounded exception messages are prohibited.

### 4.2a Full non-emitting inference and fallback evidence

Add `inference_observation` as a first-class body, not a minimal diagnostic. Required fields: `inference_id`, `inference_attempt_ordinal`, `occurrence_ref`, `target_selection_ref`, `execution_state` (`executed`, `skipped`, `unknown`), `model_receipt`, `input_snapshot_refs`, `evidence_sha256`. `inference_id = "mci1:" + HI("mcp-inference-v1", {build_id, inference_attempt_ordinal})`. Increment once per actual baseline inference attempt, not per evaluated tier. The writer resolves this ID from an audit-only ordinal token (§5.2).

Executed inference requires the complete copied model evidence: actual ordered `x`, imputed-column mask, `z`, target/election and suppliers, raw fraction score, qualification percentage and fallback origins, even when **no rule emits**. Not-yet-computed tier/display fields use `not_applicable` wrappers. Skipped/guard-rejected attempts retain observed guard/skip reasons; uncomputed score/vector is missing or not applicable, never zero. Dropped or missing full evidence means incomplete inference coverage; an aggregate diagnostic count cannot replace it. Signal/fade observations reference this record and may repeat its copied model receipt; a missing parent/inference record is reported, not fabricated.

For each feature actually imputed, record `{feature_name, stage, value, unit, origin, dependency_name, origin_verification}`. `stage` distinguishes source feature assembly from vector imputation. `origin` is `code_default`, `model_payload_override`, `caller_override`, `unknown_column_zero_default`, or `unknown`; `origin_verification` is `observed`, `unverified` or `missing`. Capture actual precedence (`default_fallbacks` → payload overrides → caller overrides → `means.get(col, 0.0)` for an unknown column), without changing it. Availability=0 is an observed source flag, not automatically an imputation. A payload override is not called a **trained mean** unless its training provenance is verified; a code default is never so described. If origin is not exposed, retain the observed actual value and an explicit missing origin wrapper/reason. Missing origins reduce completeness; no audit-only recomputation of `x` or fallback selection.

### 4.3 `representative_link`

Capture after the **unchanged** final consolidation. Required body: `collapse_contract_ref`, `input_row_ordinals`, `supporting_observation_ids`, `unlinked_input_ordinals`, `representative_input_ordinal` (wrapper), `output_row_ordinal`, `operational_identity` (wrapper), `precollapse_row_sha256` (wrapper), `final_whole_row_sha256`, `link_state` (`complete`, `partial`, `missing`), `reason_codes`.

Hashes here are read-only whole-row serialization receipts, not replacement canonical equality keys. Preserve the exact baseline clustering, representative and output order for each original input ordering. Link all known supporting signal observations without adding a list to the operational row. Final bucket/duplicate metadata may derive from other inputs; do not attribute those changes solely to the representative. If a safe mapping cannot be captured without changing collapse behavior, use partial/missing links; do not infer the winner by matching final labels/scores. A later implementation must prove that read-only row ordinals and the representative mapping do not alter clustering, alias guards or ties. Reimplementing collapse in the recorder is prohibited.

### 4.4 `diagnostic` and `build_close`

Diagnostic body: `stage`, `code`, `affected_observation_id` (wrapper), `count`, `coverage_effect`. It contains bounded loss/count information, **not a replacement for full inference evidence**. No diagnostic affects operational exit status or logs used as qualification state.

Close body: `last_sequence`, `counts_by_record_type`, `inference_attempts_observed`, `emissions_by_path`, `dropped_counts_by_reason`, `coverage` (`complete`, `partial`, `unknown`), `close_reason`, `replay_capabilities`, `export_route_state`, `segment_bytes`, `segments` (names, byte digests and sizes), `persistence_state` (`local_only`, `failed`, `unknown`). `last_sequence` equals the close envelope's sequence; counts include that close record. Before closing, rotate to a separate final close segment. Its `segments` list covers preceding finalized record segments only, and `segment_bytes` is the sum of **those preceding segments' actual bytes including LF**. The close segment is not in its own inventory. The manifest later hashes every final segment including close; §6.4 defines the exact lifecycle.

`export_route_state` is `unprovisioned`, `provisioned_unverified` or `verified_available`; capture the known resource state, not an assumed steward or future upload. `replay_capabilities` explicitly lists scoring-only, selection/context, full policy and ticket comparison states (`non_replayable`, `unverified`, `replayable`) with missing dependency/export reasons. **With no export route/steward, every durable replay capability is `non_replayable` at close**, even if copied computational evidence is complete. Local diagnostic evidence may be useful, but is not accepted durable replay evidence.

`export_verified` is **not a close-state value**: final export happens after close. Verification belongs exclusively in a later external export receipt. No close receipt, missing segment, dropped event, partial link or required missing dependency means incomplete coverage for the affected analysis. Absence of a sidecar is **unknown/not instrumented**, not zero signals or a clean pass. Complete capture is not complete historical replay: readers independently check retrievable point-in-time dependencies and mark affected comparisons non-replayable.

### 4.5 Exact semantic evidence projection

Receipts must keep run-specific references only in the designated fields below. Dependency references inside rule/model/consensus/context receipts are **logical dependency-name strings** resolving through `input_snapshot_refs`, not embedded artifact locations. Model receipt contracts and fitted-model byte references are semantic and retained. No run/observation IDs are permitted in those receipt values. Nested `parent_model_receipt` must obey the same semantic-only model schema (no inference/run IDs anywhere); a violation is invalid, not silently stripped. Array iteration ordinals used by the computation remain evidence; they are not discarded as incidental run counters.

For `signal_observation`, create exactly this new object from these JSON pointers (missing wrappers remain wrappers, not omitted):

| Projection key | Source pointer / operation |
|---|---|
| `identity_complete` | `/body/identity_complete` |
| `occurrence_ref` | `/body/occurrence_ref` in full, including partial material when applicable |
| `selection_ref` | `/body/selection_ref` in full |
| `emission_path` | `/body/emission_path` |
| `rule_receipt` | `/body/rule_receipt` in full |
| `model_receipt` | `/body/model_receipt` in full |
| `consensus_receipt` | `/body/consensus_receipt` in full |
| `fade_receipt` | `/body/fade_receipt`, with exactly `/value/parent_observation_ref` and `/value/parent_inference_ref` removed if observed; `parent_model_receipt` remains |
| `context_price_receipt` | `/body/context_price_receipt` in full |
| `inputs` | Each `/body/input_snapshot_refs/<i>` becomes exactly `{logical_name: entry.logical_name, receipt: D(entry.receipt)}`, sorted by unique outer logical dependency name |

`D(wrapper)` preserves a non-observed wrapper exactly. For an observed wrapper it emits exactly `{state:"observed", reason:null, value:{logical_name, version, sha256, size_bytes, as_of_utc, missing_members}}` with values from that dependency. Retrieval location, owner, verification timing and expiry are excluded **only here**, not from content/manifest receipts. Missing dependencies must still carry their logical name: each snapshot array entry is `{logical_name, receipt:<wrapper>}`; apply `D` to `/receipt` and retain the outer name. Duplicate logical names or inconsistent outer/observed inner logical names invalidate the record.

For `inference_observation`, the projection is exactly `{occurrence_ref, target_selection_ref, execution_state, model_receipt, inputs}`, copied from matching body fields with the same `D` transformation. Its content digest uses the separate tag `mcp-inference-evidence-v1`.

Excluded by this positive projection: the envelope; `/body/{observation_id,signal_id,emission_attempt_ordinal,input_order,inference_attempt_ref,baseline_decision,operational_links,evidence_sha256}` for a signal; `/body/{inference_id,inference_attempt_ordinal,evidence_sha256}` for inference; and the two designated fade parent run references. Contract IDs, snapshot SHA-256 values, as-of evidence, actual ordered vector and parent model evidence remain. An anchored complete observation can have identical projected evidence across runs despite different nested inference/fade run references. **Partial occurrence/selection references remain intentionally build-scoped**; do not assert cross-build digest equivalence for them.

## 5. Fail-soft hook interface and resource limits

Proposed interface (descriptive, not implemented):

```
open_build(copied_build_receipt) -> audit_handle_or_disabled
try_capture(handle, stage, schema_bounded_primitive_receipt) -> void
try_link(handle, schema_bounded_primitive_link_receipt) -> void
try_close(handle) -> void
```

Default is **OFF** under new flag `EDGE_FACTORY_MCP_AUDIT`; only explicit `1` enables it. Do not inherit default-ON `EDGE_FACTORY_SCORED_SHADOW`, its recorder or its IDs. Prospective enablement follows implementation acceptance and the storage prerequisites below.

### 5.1 Reserve before copying; bounded producer work

The producer may pass only exact built-in primitive types, not subclasses: `None`, `bool`, signed-64-bit `int`, finite `float`, `str`, `list`/`tuple`, `dict` with exact-string keys. No arbitrary `repr`, callbacks, generic deep-copy, live object graph or network/model/disk work. Input copies are schema-shaped, never whole operational picks. The caller supplies an audit-only stable view of the small computed values; if mutation is detected or stability cannot be assured, drop capture. The baseline object is never frozen or locked by audit code.

Reject re-entrant capture with a producer-local guard; the hook may not invoke itself. Check pinned interpreter/build and active GIL at startup, refusing unsupported runtimes. Caps per capture: depth 12, 4,096 total nodes (including mapping keys), 1,024 total string code points across keys/values, 4,096 total strict UTF-8 string bytes, maximum 512 features, 64 suppliers (subsets of the total node count, not additional allowances). Per string: 1,024 code points; per key: 128 code points. Larger metadata is a separate bounded receipt or dependency reference, not silently truncated. Reject cycles, invalid Unicode and limits at the first violation; no traversal past caps. This smaller metadata bound is a proposed amendment and needs corpus/contract capacity tests. Numeric vectors remain supported; if an actual required receipt does not fit, revise the contract rather than claim complete capture.

Admission reserves a conservative maximum **before allocating the private copy**, under an audit-only lock acquired nonblocking; lock contention drops. Exactly one capture may be in-flight per producer. A single bounded walk validates/copies and increments limits; no measure-then-copy two-pass race. The immutable private representation uses tagged tuples and plain primitives, no nested mutable mappings handed to the writer. Abort/drop/refund on any capture exception or detected mutation; the copied values, not a prior measurement of the source, determine the charge. Where concurrent mutation cannot be detected reliably, inputs must already be stable schema locals; tests must prove that hooks never pass concurrently changing containers. No source reference survives capture.

For the initially supported **pinned CPython GIL build on Linux**, reserve and charge:

- `R = 1,024 + 256*N + 8*U` bytes, where `N` is total copied nodes and `U` is total string code points. This is a conservative **accounted retained-object budget**, not a process-RSS bound.
- Maximum `R_max = 1,024 + 256*4,096 + 8*1,024 = 1,057,792` bytes. Reserve `R_max` first; refund to `R` only after successful copy. Do not refund a partially built copy before it is discarded.
- Serialized upper estimate `S = 32*N + 6*U + 1,024` includes a conservative structural/numeric allowance and framing. Maximum `S_max = 138,240` bytes (<256 KiB). `ensure_ascii=False` makes six bytes/code point sufficient for escaping; strict UTF-8 forbids lone surrogates. Final envelope/ID overhead must fit the extra 1,024 bytes or fail capture. Writer checks actual canonical record length ≤`S` and ≤256 KiB; any estimate violation latches FAILED, drops the receipt with incomplete coverage and disables further capture until an approved fix, not a truncation path.

The 256-per-node coefficient includes tuple/header/reference slots, primitive storage and copying overhead on the supported runtime; **it is a proposed conservative coefficient, not measured calibration**. Gate C must pin the exact interpreter/build and verify worst-case allocations with `tracemalloc` plus structural tests (including transient partial copies); if it undercounts, refuse audit startup until an approved revised coefficient/contract exists. `sys.getsizeof` alone is not the proof. Excludes caller-owned baseline objects, allocator fragmentation and process RSS; free-threaded/other runtimes require separate calibration. The 8 MiB limit bounds accounted admitted private copies **including producer reservations, queued and writer-in-flight objects**, not merely serialized bytes. Retain tokens until the writer drops its last reference. At maximum reserved size the pool admits only seven simultaneous receipts, not 128; 128 is a count ceiling, never a capacity promise. Before encoding, the single writer reserves `S` plus bounded sorting/framing scratch from its separate 2 MiB pool while `R` remains charged. Writer scratch is separately capped at 2 MiB, including canonical-sort/serialization buffers; streaming/bounded encoding must meet that cap, not build arbitrary extra trees.

### 5.2 Tokens, lifecycle and contention

Producer supplies audit-only `{build_invocation_token, fixture_input_ordinal, inference_attempt_ordinal, emission_attempt_ordinal, row_input_ordinal}` tokens through separate local bookkeeping, never operational row fields. Hashing/serialization/link-ID resolution occurs in the writer. Capture all baseline emission ordinals before enqueue, even on drops; a later link to a dropped ordinal stays missing. The writer maps only captured tokens to IDs, never reruns collapse or infers links from labels. Fade references the captured parent inference/emission ordinal; unknown parent evidence remains missing. Capture baseline representative/input ordinal mapping read-only at the actual collapse, without changing its order/algorithm; parity proof remains mandatory.

State machine: `DISABLED`, `STARTING`, `READY`, `CLOSING`, `CLOSED`, `FAILED`, `ABORTED`. Teardown timeout latches ABORTED; late producers discard/refund, and that build can never later finalize as complete or transition to CLOSED. Startup is asynchronous with no caller wait for disk/quota readiness; before READY, attempted events drop with `startup_not_ready` and a bounded pre-READY counter; coverage is partial if any dropped attempt occurred, not merely because the build passed through STARTING. Other missing receipts/dependencies can independently reduce coverage. Only READY accepts reservations. Startup failure releases reservations and disables collection. READY transitions and counter/queue operations share an audit-only nonblocking critical section; no scoring-thread wait for lock contention. Reserve counts/bytes atomically; enqueue only if still READY. Close races refund/drop producer captures that have not enqueued. Queue publication and closed-state checks are atomic under that lock.

`try_close` is idempotent, sets a close-request flag without waiting, and does not synchronously join on the scoring path. The writer checks the flag and outstanding producer reservations; it drains admitted receipts before a close segment. A reserved control slot/counter area (outside the 128 receipt count but **inside** the 8 MiB accounting) prevents a full queue hiding shutdown/loss counts. Close-state transition/control publication uses a separate nonblocking retry by the writer if producer contention prevents immediate transition. No receipt may enqueue after CLOSING. Seal close/manifest only after every in-flight producer has refunded/released its reservation and the queue is drained. Timeout before that barrier leaves an unclosed/partial build, never a final complete manifest. Drop counters are best-effort: if nonblocking counter publication itself fails, set coverage unknown when detectable; if exact attempts-minus-captured cannot be reconciled, do not claim exact loss counts or complete coverage. Audit teardown outside scoring waits at most one second; if unfinished, report partial when possible and abandon audit work, with no synchronous I/O fallback. Host shutdown may leave no close receipt, which readers classify incomplete. Ordinary audit exceptions never swallow baseline scoring exceptions or termination signals.

| Resource | Bound / overflow behavior |
|---|---|
| Record | 256 KiB actual canonical bytes; schema caps above; drop rather than truncate |
| Captures | 128 queued/in-flight receipts and 8 MiB accounted retained reservations, whichever first; nonblocking drop |
| Writer scratch | 2 MiB separately accounted; startup/runtime invariant tests required |
| Record stream | 10,000 records or 32 MiB including close/control records; reserve 64 KiB within this for close/diagnostics |
| Small local input copies | Separate 4 MiB **total per build**, each ≤1 MiB; large inputs referenced by default (§6.2) |
| Manifest/control files | 64 KiB per build reserved separately; separately published compact index has an 8 KiB cap (§6.3) |
| Local spool | 512 MiB accounted spool bytes plus unused reservations, exported-build retention target 30 days; unexported evidence preserved with refusal-only admission (§6.4) |
| Audit teardown | Best-effort drain ≤1 second outside scoring; unfinished evidence partial |

Disabled/enabled/failed capture p99 target <1 ms on pinned representative workloads remains an **unmeasured acceptance target**. A clock check after blocking work cannot establish isolation. Prove bounded traversal, no blocking queue/disk work, no shared-object mutation and no operational-output changes. No whole-process OOM/host-failure isolation claim is made; record residual risks. Limits/failures affect audit coverage only, never whether picks are emitted or the operational exit status.

## 6. Storage, export, retention and recovery

### 6.1 Layout and corrected current-tree claims

Separate spool (bulk files always untracked):

```
localdata/ml_consensus_audit/v1/YYYY-MM-DD/<build_id>/
  records-000001.jsonl
  build-manifest.json
  inputs/<sha256>                 # bounded small copies only
  reservation.json               # audit-local quota control
  owner.lock                     # audit-local liveness control
```

Schema documents/test fixtures are tracked; bulk production receipts/datasets are not. Each invocation owns its directory; one writer per segment, no shared append or existing Phase5/scored-candidate ledger reuse. Validate all paths under this root and reject symlink traversal. Full build IDs contain a colon; this initial Linux-only contract must not silently normalize them on another platform.

Verified locally by source inspection and read-only `git check-ignore`, **not cleanup execution**:

| Mechanism | Exact current behavior / consequence |
|---|---|
| `.gitignore:10` | `localdata/*` ignores the parent spool directory; nested files are ignored. Re-inclusion requires each ignored ancestor to be re-included, not a lone deep negation. |
| `clean_localdata.py:165–166` | Top-level `iterdir`, files-only, non-symlink, known filename patterns; **cannot reach nested spool**. No exclusion needed. |
| `phase5_persistence.py:185–188` | `git clean -fd localdata/` with named existing exclusions, **no `-x`/`-X`**. Normally preserves this ignored spool; absence from exclusions is not evidence it deletes it. No exclusion required for currently ignored bulk. |
| Same helper `:172–183` / `:302–305` | Restores ordinary tracked localdata from HEAD, then persistence uses `git add -A localdata/`. New ignored files are not staged; explicitly re-included indices could be staged. Only named Phase5 JSONL paths receive special unions; other conflicts are warnings/fail-soft, not guaranteed recovery. |
| `daily.yml:207–212,221` | Top-level report globs and explicit Phase5 dirs/scored-candidate JSONL do not match the new layout. Artifact gap is real. |
| Cache | Opportunistic restore/save of `localdata`; not durable export or proof of complete bytes. New runner/checkout lifecycle and cache loss can lose ignored files even though current cleanup preserves them. |

**Removed prerequisite:** a cleanup exclusion for the current ignored nested spool. Keep checkout/cache loss, future cleanup changes and export gaps as separate risks. Detailed manifests remain ignored in draft 3. A separate eligible compact index is nonignored and can be cleaned while untracked; the pilot must commit publication before any persistence restore/clean (§6.3). This is a separate publication risk, not a reason to add an exclusion for ignored bulk.

### 6.2 Input bytes: default reference above 1 MiB, separate durability owner

The 32 MiB limit covers **record segments**, not a full warehouse snapshot. Small copied inputs have a separate 4 MiB build budget; any dependency >1 MiB is referenced by default. A dependency ≤1 MiB may also be referenced; copying never forces exhaustion of stream space. Capture derived rolling-hit-rate/query results actually used as bounded evidence plus query/code/as-of provenance. This can support a specified scoring-only comparison; it cannot substitute for the warehouse bytes required by a full historical policy/ticket replay.

The review reports a 78 MB warehouse from its CI log. That log/size was not independently rerun here; it is sufficient as a capacity example, not a locally measured input size. A 78 MB input is not copied into the 32 MiB stream. A fitted-model snapshot, even small, needs verified bytes; recorded path or model contract ID is not enough.

**Named proposed location for large dependency bytes:** GitHub Actions artifacts in repository `6ixtyn9-sudo/Edge-Factory`, artifact name `ML-Consensus-Inputs-v1-<run_id>-<attempt>-<invocation>`, requested retention 30 days, entries `inputs/<sha256>` with immutable raw bytes plus a checksum manifest. Record repository, run ID, artifact ID, entry path, SHA-256, size and UTC retention deadline in `location_ref`. Local runs use an explicitly operator-owned exported bundle with a verified content-addressed path. Live `localdata/warehouse.duckdb`, cache keys and expiring signed URLs are not durable locations. Source snapshots must correspond to immutable/closed byte versions actually used; do not copy a concurrently mutating DuckDB file and call it point-in-time evidence.

**Accountability:** the operator authorizing audit enablement must assign an identified repository maintainer as **audit export steward**, recorded in audit configuration. That steward owns input/record upload, download-and-digest verification, expiry monitoring and pre-expiry export for any approved comparison. Unassigned steward or unprovisioned location blocks production evidence enablement. This names a concrete proposed repository/artifact route and responsible role, **not an existing uploaded object or a silently appointed person**. Artifact creation/verification remains unimplemented; **no steward is assigned and no export route is provisioned**. Evidence-complete production enablement is blocked on these missing resources, not merely awaiting a review verdict. No present retrievability is claimed.

Dependencies are `verified_bytes` only after bytes are downloaded/rehashed against pinned source digests by the steward's independent verification step. Missing/unverified/expired bytes mark the affected comparison non-replayable **at build/report time**, not first discovered at Gate E. Record separate capabilities for scoring-only, selection/context, full policy and ticket replay, with missing dependencies per capability. Missing whole warehouse does not erase an observed vector, nor does observed `x` prove full pipeline replayability. Whole-pipeline replay and long-term retention stay separate approvals.

### 6.3 Explicit route choice: compact index pilot versus durable evidence

**Proposed A4 choice, awaiting approval:** permit a bounded **compact-index-only Git pilot** without a workflow edit, but do **not** accept it as an alternative to durable byte export. Retain dedicated per-invocation input and record artifacts as the evidence route. This removes a workflow edit from the *index pilot's* critical path only; evidence-complete production enablement still requires demonstrated bulk export. No record segment, input blob or quota/lock file is to be un-ignored or staged.

**Separate paths/names, never dual-use:** every detailed `build-manifest.json` stays ignored under `localdata/ml_consensus_audit/**`, regardless of size or pilot eligibility. The only prospective stageable pilot outputs are:

```
localdata/ml_consensus_index/v1/compact-index_YYYY-MM-DD_01.json
... slots 02 through 08 for the same trading date ...
```

Each compact file is a distinct typed index, not a renamed detailed manifest. It includes schema/build IDs, original detailed-manifest byte digest, exact segment digests/sizes and input summaries, coverage/replay capabilities, and **observed** export-route state. It cannot claim verification of its own later upload. Complete compact serialization must fit **8 KiB including LF**, else no eligible file is created; do not truncate. The ignored detailed manifest can be 64 KiB independently. Re-inclusion targets only `compact-index_YYYY-MM-DD_0[1-8].json` after explicit ancestor negations and re-ignoring all other descendants in the separate index directory. No spool ancestor/manifest/record/input/control-file exceptions. Git patterns do not enforce content size or a pilot window: those are publisher admission rules, never assumptions about `git add -A localdata/`.

Proposed pilot limit remains 30 days, eight unique indices/trading date, 240 files and ≤1.875 MiB raw payload additions. Git history overhead must be monitored separately. Continuing a pilot requires explicit approval. Slots are immutable: one slot binds one build and digest; a retry for that build returns the same committed index, never claims a new slot or overwrites it. A ninth build, compact index >8 KiB, detailed manifest >64 KiB, failed validation or date outside the authorized window creates **no stageable compact file**. A valid detailed manifest between 8 and 64 KiB remains ignored; it may have an independently admitted ≤8 KiB compact index only if the full compact inventory fits. Size never causes the detailed manifest itself to become eligible. Detailed manifests are always ignored, including after failed compact admission.

**R1 publication boundary:** do not ship an ignore-only setup expecting a later run to commit its first index. Pilot bootstrap must publish the exact index-directory `.gitignore` rules and an admitted initial compact index **in the same Git commit**, before any `phase5_persistence` invocation. Subsequent compact publications must also be locally committed before restore/clean; broad persistence is a later push path, not an admission gate. This is a separate audit-publication integration requiring explicit authorization/tests; no `.gitignore` changes, index outputs or commits of runtime data occur in this documentation amendment.

Publisher transaction (audit-only, never scoring):

1. Serialize/validate the complete candidate in **ignored** staging storage; measure actual canonical byte length. On size/content failure, retain an ignored refusal diagnostic within the same spool/control quota, no eligible filename. Hold audit publisher lock and an exclusive persistence/checkout coordination barrier; count committed slots **plus pending transaction reservations** for the authorized date/window. If the barrier cannot be guaranteed against every restore/clean/staging caller, refuse pilot enablement. Existing `phase5_persistence.py` does **not** implement this barrier; integration must review all invocations or use a separately serialized operator publication phase. Do not assume its broad staging validates content.
2. Reconcile build→slot mapping against HEAD, pending journal and any unpushed local commits. Allocate one of eight fixed slots atomically under that lock; no free slot means refusal. Journal the build/digest/slot transaction in ignored storage durably, charged against the existing 512 MiB spool/control quotas; no separate unbounded publication spool. A crash-reserved slot counts until recovered, never optimistically reissued. Concurrent publishers cannot claim the same slot. Reconcile upstream before assigning slots to independent hosts; the pilot initially permits **one serialized publication authority**, not distributed allocation; CI jobs do not autonomously publish indices before that authority/coordination integration is accepted. Unknown upstream/ambiguous ownership means refusal.
3. Publish the admitted canonical compact file atomically to its separate eligible path and stage **that exact path**; bootstrap additionally stages exact ignore rules. Locally commit while holding the coordination barrier. No broad Git staging during this step; unrelated operational changes cannot be included. If commit fails, remove the untracked eligible file before releasing the barrier; keep the candidate/journal ignored. On a crash in the rename→commit window, startup must recover/remove the eligible uncommitted file **before any persistence helper**. No eligible refused file may escape into later broad staging.
4. Verify the local commit contains only admitted paths/digests (and exact bootstrap ignore changes where applicable). Mark journal committed; release barrier. Push only through the authorized branch/session route. Push failure leaves a **tracked locally committed** index, not a vulnerable untracked file; durability remains `not_published` until remote commit/file download is verified. Retry identical commit/index, no slot rewrite. Checkout/reset/rebase must respect the coordination barrier and retain the ignored journal/candidate for recovery; unsupported conflicts stay failures, not invented Phase5 union support.

This requires future publication integration proof; documenting a transaction does not make rename+Git commit globally atomic. **A crash that leaves a nonignored untracked file must not allow broad staging or cleanup before recovery.** If coordination/recovery cannot be demonstrated, defer the pilot and keep all files ignored. No `assume-unchanged`/`skip-worktree` tricks, ignored-size inference, truncation or dependence on the persistence helper inspecting JSON.

Acceptance controls must include ninth publication, oversized detailed and compact manifests, retry idempotence, failed validation/commit/push, crash after reservation/rename/stage/commit, simultaneous publishers, bootstrap `.gitignore`+index single commit, and restore/clean ordering. After each control, broad `git add -A localdata/` may stage **only** admitted eligible compact indices; never the ninth/oversized/refused compact index or any detailed manifest/record/input/control file. Test actual coordination and crash recovery, not just filename patterns.

A compact Git index is durable **metadata only after verified push**; it cannot recover bulk or establish replayability. A later independent external export receipt verifies the detailed manifest/bundle; neither detailed manifest nor compact index is modified to insert future success. With no export resources, close and index explicitly report `non_replayable` and `unprovisioned`. Reviewer statements that an index pilot may proceed are technical recommendations, not operator authorization.

**Evidence route:** dedicated record artifact `ML-Consensus-Audit-v1-<run_id>-<attempt>-<invocation>`, containing completed and partial canonical segments, immutable manifest and bounded local input copies, with 30-day retention measured from artifact creation (expiry is recorded; a requested retention is not proof the repository policy grants it). Input artifact (§6.2) may be separate to avoid the spool's local quotas. Upload is audit-only, best-effort/always-run, after close and before runner disposal, and must not alter the operational job conclusion. It requires authorized maintainer workflow integration or an explicitly approved **external audit-only uploader** that has no scoring-thread work or effect on operational job outcome. Neither route is implemented or assumed available here. Workflow edits obey the handbook's GitHub App constraint; do not hide bulk in an existing Phase5/report artifact.

Without a demonstrated evidence-export route, implementation after amended Gate A approval may use temporary storage and the separately approved index pilot; complete-evidence production enablement remains blocked. Cache is not the route. Thirty days is the exported-artifact investigation window, not permanent preservation or permission to delete unexported local evidence. Expired objects are unavailable; comparisons needing them remain non-replayable unless a separately approved retained export exists and its digests/retrievability are verified.

### 6.4 Global reservation, liveness, close → manifest → export

Initial supported storage is a local Linux filesystem with reliable `flock`; verify filesystem type against a calibrated allowlist at startup. Unsupported/network/FUSE/compressed or speculative-allocation filesystems disable audit writes until separately validated. Locks are worker-only, never on scoring thread. Acquire nonblocking exclusive locks: one global quota lock, one per-build owner lock held by an open file descriptor for the live writer. Use close-on-exec and an `after_in_child` at-fork handler that closes inherited audit descriptors; prohibit unsupported fork patterns while the audit writer is live; any necessary child process must close inherited audit descriptors immediately. A leaked descriptor that still holds the lock cannot be overridden based on age; it blocks reclaim and triggers audit-capacity refusal. Do not use classic process-wide POSIX record locks whose ownership can be released by closing a different descriptor. Acquire owner then quota in a fixed order; a collector already holding quota may only try owner **nonblocking**, never wait.

Quota invariant: **accounted spool bytes + unused reservations ≤512 MiB**. This is an enforceable admission/write-accounting bound, **not a whole-filesystem physical-allocation guarantee**. Charge each file's planned logical bytes rounded up to the calibrated filesystem allocation unit plus an 8 KiB per-file allowance; charge directories 8 KiB each, and compare with measured `st_blocks*512`. The filesystem/profile acceptance test must show these allowances dominate actual observed allocations for the supported workload; otherwise refuse startup or propose larger approved allowances. Per-build physical allocation drift outside this model is an invariant breach, stops further audit writes/admission and triggers safe reconciliation, never silently relaxes the cap. Inode/global filesystem metadata, allocator behavior and external writers are residual risks; do not claim the spec itself controls them.

Reserve one build's full maximum (32 MiB stream + 4 MiB small inputs + 64 KiB manifest/control + **1 MiB filesystem-accounting overhead**) under the global lock before READY: **37 MiB +64 KiB per build**. The earlier 36 MiB allowance omitted block/directory accounting. Cap files at 64 and directories at 8 per build; bounded rollover/input names/control files must fit those counts. Quota/control root bookkeeping has its own included 64 KiB allocation. At most 13 maximum build reservations fit in an otherwise empty 512 MiB spool; count/bytes must both pass. Before each write/rename, the worker computes/reserves the charged growth (including temp-file duplication), refuses overflow and retains the allocation until durable deletion/finalization. The full slot covers its build bytes exactly once: `charged_build = max(reservation, measured_usage)` while live; `unused = max(0, reservation - accounted_usage)`. No independent writer may optimistically spend the same unused space. Accounting updates occur under quota lock; workers never wait on that lock from scoring.

A finalized/abandoned build is charged `max(logical-rounded-plus-overhead, measured allocated bytes)`; a live build is charged at least its full reserved slot. No worker may write past its per-build allocation. Small input copies, temporary files, directories, lock/reservation files and manifests are included; writer memory scratch is not disk usage. If lock/admission/recovery fails, audit stays disabled/partial. Larger input artifacts are stored outside this local spool by the export steward, never secretly charged as a 32 MiB local record.

Each `reservation.json` pins allocation, build/host/boot invocation identifiers and ownership. A global ledger is a recoverable **cache**, not authority: recompute accounted usage and unused live reservations from validated per-build metadata under quota lock at admission/recovery. Write control updates with temp/fsync/atomic rename/directory fsync, charged within control quota. A crash or incoherent reservation ledger triggers recomputation or fail-soft audit refusal, never an optimistic downward adjustment or operational interruption. During recovery, charge each live build at least `max(full allocation, measured accounted usage)` and each finalized/abandoned build its measured accounted usage; include root controls. If a writer exceeds its allocation, latch an invariant breach and refuse admission, never silently expand its allowance. An owner-locked build without valid reservation evidence is conservatively charged its full allocation or blocks admission. Two new 37 MiB +64 KiB allocations against 480 MiB cannot both pass; in fact neither fits. Uncontrolled external writes/corrupt cache may arrive already over cap; refuse new writes and safely reclaim eligible builds, never claim a retroactive hard bound on files created outside this contract.

States:

- **Live-owned:** local writer holds `owner.lock`; never delete, even if timestamps/heartbeat are old.
- **Finalized:** owner released after immutable manifest; eligible for expiry/size cleanup.
- **Abandoned/unclosed:** owner lock can be acquired nonblocking on this local spool and no finalized manifest exists. Boot/host/PID-start identifiers are diagnostics, not permission to delete. A foreign cache-restored directory is a local copy, not a live remote shared spool; acquire its local lock before classifying it abandoned. Never infer death merely from a stale heartbeat.

Collector holds an eligible build owner lock through classification and any permitted deletion, with accounting serialized under quota lock. **R3 refusal-only retention:** never automatically delete an **unexported finalized build** or an unexported abandoned partial, regardless of age or size pressure. Acknowledge export only after independent byte verification (§6.4 lifecycle), not upload success or a durable compact index. Exported finalized/abandoned builds are reclaimable under the 30-day/size policy only after explicit nonblocking owner-lock acquisition; live-owned builds are never deleted. Abandoned means that lock is acquired, never inferred from heartbeat/staleness. Preserve partial coverage even if abandoned data is acknowledged-exported.

If safe exported reclamation cannot make room, **stop accepting audit builds/writes**; report `quota_unavailable`/partial or unknown coverage through reserved controls where possible, otherwise the missing close exposes incompleteness. Do not evict unexported evidence to keep auditing. Unexported reservations are reconciled to measured accounted bytes only after ownership lock is acquired; reclaim unused capacity, not stored evidence. Age alone cannot release ownership or remove data.

This intentionally changes draft 2's maximum-30-day local rule: 30 days applies to exported-build expiry/reclamation; unexported local evidence can outlive it, **but cannot grow past admitted quotas**. Exhaustion disables auditing rather than extending the quota. Cache/runner disposal still can lose ignored bytes outside this collector's control; no local preservation promise is durable export, long-term retention approval, or a guaranteed backup. Unassigned resources keep those builds non-replayable. Pre-existing unsafe/cache paths or over-cap external writes cause audit refusal/safe exported-only reconciliation, never operational-file deletion or optimistic quota relaxation.

Lifecycle:

1. Writer emits canonical full lines; segment rollover target 4 MiB, bounded single line may cross it. Digest actual bytes including LF. Unterminated tail is corruption/coverage loss, never repaired into an operational archive.
2. Rotate to a separate close segment. Close inventories **preceding segments only**; its `last_sequence` and record counts include itself (§4.4).
3. Finalize `build-manifest.json` with **all** final record-segment digests including close, bounded input-copy digests and dependency location/availability summaries. Manifest excludes **itself**, locks/reservations, temp files and the later export receipt from its own file-hash inventory. Compute manifest raw-byte digest separately. Atomic temp/rename; partial failure leaves no complete-manifest claim. Detailed `build-manifest.json` may be up to 64 KiB and is always ignored. A separately named complete compact index must fit 8 KiB and pass atomic publication admission, otherwise no eligible index file exists (§6.3). No conflicting bytes under the same build/manifest name.
4. After close, upload the manifest and inventoried files. Upload success alone is `unverified`, not final verification. Index may already have been persisted with a declared name; do not edit it to insert a later success.
5. Independent download verifies manifest raw-byte digest and each inventoried file, plus separately referenced input artifact bytes. Produce an **external export receipt** with repository/run/artifact IDs, manifest digest, byte verification result/time, steward identity and retention deadline. It is not in its own bundle/manifest inventory. Missing receipt or missing bytes means export unverified; expiry downgrades availability even if an old success receipt exists. This prevents all self-hash cycles.

No last-write-wins across invocations; canonical exact duplicates only. Conflicting IDs/digests quarantine offline. Long-term retained comparisons require separately approved storage, owner and verified export before expiry; no long-term archive has been adopted here.

## 7. Required acceptance receipts (not executed)

Before Gate C acceptance, provide commands, pinned code/input hashes and expected/actual results for:

1. Schema validation for every body/wrapper; unknown versions, bad enum/types, nonfinite floats, oversized receipt, malformed tails and duplicate-ID corruption rejected offline.
2. Same occurrence/selection/rule from model and consensus: distinct signals, two observations, one unchanged baseline operational representative. Repeated attempts remain distinct; upload retry deduplicates exact records.
3. Missing kickoff/competition and women/youth/reserve ambiguity: no unsupported cross-build merge. Alias-map or contract revision changes references explicitly.
4. Actual `x`/imputations/`z`, guard/activation, exact election, weighted-average denominator, qualifier/effective threshold and fallback-origin receipts match computed inputs in synthetic controls.
5. Fade parent qualification/display distinction, independent inference counts, required-elector abstention and observed/missing/mismatched certification states.
6. Equal-rank input permutations: preserved baseline representative/full payload **per ordering**, evidence/link completeness without imposing new sort or operational ID.
7. Disabled/enabled/serialization failure/queue saturation/disk failure/startup failure/shutdown timeout: whole-payload, archive admission/unsafe-date receipts, ticket/state, price guards, research outputs and notifications identical to baseline.
8. Correct current cleanup behavior, separate compact-index admission/staging (ninth, oversized, retries, crashes, concurrent publishers, bootstrap/restore barrier), failed-push recovery, no detailed-manifest/bulk staging; upload/download checksums, missing/expired export, 30-day limits, concurrent global quota/lock ownership, abandoned/cache-restored builds, interrupted append/ledger crash injection. No record segments or input datasets staged into Git or mixed into another ledger.
9. Dependency missing/expired cases: affected replay comparisons non-replayable, partial diagnostics explicitly partial. No retrospective filling from current state.

Also require canonical hash vectors (§9), cross-run nested-reference projection tests, full non-emitting evidence, fallback precedence, Unicode/subclass/huge-int/depth/node boundary tests, capture mutation/close races, allocation calibration and reservation invariants. These supplement, **never weaken §7 items 6 and 7**, permutation parity and the full failure matrix.

Only documentation whitespace, links and the illustrative hash/ignore calculations are checked at publication. No executable schema validator, implementation test, export verification or full replay is claimed here.

## 8. Decision requested from reviewers/operator

Approve or amend explicitly:

- **A1:** v1 envelope/typed receipts, missing-evidence semantics and computation-point capture (§2/§4).
- **A2:** sidecar-only identities, partial-identity isolation and exact baseline representative links (§3/§4.3).
- **A3:** default-OFF fail-soft interface, resource/latency targets and residual-risk tests (§5).
- **A4:** corrected cleanup claims; default >1 MiB references with named but unprovisioned input artifact/steward; separate compact-index publication boundary (not byte durability); refusal-only unexported retention, shared quota/liveness and exact export lifecycle (§6).

**Current disposition:** both supplied draft-2 reviews renew A1–A3 technical design approval; one read the pinned draft and recalculated ten vectors, the other reviewed reconciliation/repository facts rather than draft 2 line by line. A4 requires a corrected compact-index publication boundary; the latter review additionally recommends R1–R4 resource/retention rulings. Draft 3 adopts those amendments for explicit review, **not as operator authorization**. See the [attributed disposition record](GATE-A-REVIEW-DISPOSITION-2026-10-09.md). Gate A completion and permission to code remain pending. Only after explicit operator authorization may implementation/control work begin; Gate C acceptance is required before prospective audit enablement. Evidence-complete production enablement remains blocked on unassigned steward/unprovisioned export resources. Live routing, operational schema migration and long-term retention remain separate approvals.

## 9. Worked preimages and illustrative calculations

These CPython 3.11.2 `json.dumps`/SHA-256 calculations are **documentation examples**, not an implemented recorder, schema validation or parity tests. Tags and preimages below are exact; `HI` applies to logical IDs, `HC` to record/numeric content. Unprefixed output is a content digest. Each code block is the compact preimage JSON **after** the tag and LF; the preimage has no trailing LF. Every listed string is synthetic, not an operational entity/model/fixture ID.

### Build

Tag: `mcp-build-v1`

```json
{"code_sha":"0000000000000000000000000000000000000000","invocation_id":"case-1","producer":"synthetic","trading_date":"2026-10-09"}
```

Result: `mcb1:0ddae9d12a49cb1580ec22d947615f6f15b725e2375640b1b1164626ef13d7d7`

### Anchored occurrence

Tag: `mcp-occurrence-v1`

```json
{"away_entity_key":"away-senior","competition_key":"test-league","entity_map_sha256":"1111111111111111111111111111111111111111111111111111111111111111","home_entity_key":"home-senior","identity_contract":"occurrence-v1","kickoff_anchor":{"normalization_contract":"utc-v1","timezone":"UTC","utc":"2026-10-09T18:00:00Z"},"squad_discriminators":{"away":"senior","home":"senior"},"trading_date":"2026-10-09"}
```

Result: `mco1:375e084723e9c629a029491b8ec0cc274fdb64f76689fcf589a63fc3747505c0`

### Selection

Tag: `mcp-selection-v1`

```json
{"line":null,"market":"1X2","occurrence_id":"mco1:375e084723e9c629a029491b8ec0cc274fdb64f76689fcf589a63fc3747505c0","selection":"home"}
```

Result: `mcq1:95adac52602b59e35bea1b6cf8c2533c6eb7c2f445272180b7bdcaa90e2685f3`

### Model signal

Tag: `mcp-signal-v1`

```json
{"election_contract_id":"historical-majority-v1","emission_path":"model_certified_tier","feature_contract_id":"k-v1","model_contract_id":"model-target-v1","qualification_contract_id":"tier-v1","rule_contract_id":"legacy-ml55-v1","selection_ref":"mcq1:95adac52602b59e35bea1b6cf8c2533c6eb7c2f445272180b7bdcaa90e2685f3"}
```

Result: `mcs1:00daf9293cbfce3a6acc2cb0ef584a1243c3d0cb521e7b75e6af3c5b198b76e9`

### Consensus signal (same selection / legacy rule)

Tag: `mcp-signal-v1`

```json
{"election_contract_id":"all-eligible-v1","emission_path":"consensus_unanimous","feature_contract_id":null,"model_contract_id":null,"qualification_contract_id":"unanimous-v1","rule_contract_id":"legacy-ml55-v1","selection_ref":"mcq1:95adac52602b59e35bea1b6cf8c2533c6eb7c2f445272180b7bdcaa90e2685f3"}
```

Result: `mcs1:fdb6abde4853607a2f74f150cbc88602bdb77553cf62e2c4108c2f71f75f2cfe`

### Observation

Tag: `mcp-observation-v1`

```json
{"build_id":"mcb1:0ddae9d12a49cb1580ec22d947615f6f15b725e2375640b1b1164626ef13d7d7","emission_attempt_ordinal":2,"signal_id":"mcs1:00daf9293cbfce3a6acc2cb0ef584a1243c3d0cb521e7b75e6af3c5b198b76e9"}
```

Result: `mcv1:a7addfe36013a1874b28948f19b952e1fc0710a7fb5a1e59d8798d76a6dcb733`

### Inference

Tag: `mcp-inference-v1`

```json
{"build_id":"mcb1:0ddae9d12a49cb1580ec22d947615f6f15b725e2375640b1b1164626ef13d7d7","inference_attempt_ordinal":1}
```

Result: `mci1:0f0cacdcc601ea03fdf6630c6c7c5eeb7aed7beebafd1423bdb0f901b6286924`

### Partial occurrence

Tag: `mcp-occurrence-v1`

```json
{"away_entity_key":"away-senior","competition_key":"test-league","entity_map_sha256":"1111111111111111111111111111111111111111111111111111111111111111","home_entity_key":"home-senior","identity_contract":"occurrence-v1","kickoff_anchor":{"normalization_contract":"utc-v1","timezone":"UTC","utc":null},"partial_scope":{"build_id":"mcb1:0ddae9d12a49cb1580ec22d947615f6f15b725e2375640b1b1164626ef13d7d7","fixture_input_ordinal":0},"squad_discriminators":{"away":"senior","home":"senior"},"trading_date":"2026-10-09"}
```

Result: `mco1:c46bf9fd4f8bc21657e4ad02841873116fddf612a3184a007d64a251164ae8e9`

### Canonical diagnostic content record

Tag: `mcp-record-v1`

```json
{"body":{"affected_observation_id":{"reason":"hook_not_reached","state":"missing","value":null},"code":"size_limit","count":1,"coverage_effect":"partial","stage":"capture"},"build_id":"mcb1:0ddae9d12a49cb1580ec22d947615f6f15b725e2375640b1b1164626ef13d7d7","record_type":"diagnostic","recorded_at_utc":"2026-10-09T18:01:00Z","schema_version":"mcp-audit/v1","sequence":3}
```

Result: `mcr1:12fdbf40b1f6dd761f1932c0728cc8ab6871cfc0a99504585549c5eaab9e2b0d`

### Numeric content serialization fixture (not a record schema fixture)

Tag: `mcp-content-example-v1`

```json
{"qualification":62.3,"raw":0.623,"x":[0.5,-0.0],"z":0.502}
```

Result: `af24ac3fbf20ef264e5d6c1c70e95ac4efc877c015e80a3f4f795340ac1fa1be`

For the diagnostic example, insert the resulting `record_id` into the object and serialize the entire envelope canonically, then append LF. Reordered-key encodings fail the canonical-line rule even though parsed objects could hash identically. The numeric fixture demonstrates allowed content floats; giving the same object to `HI` is invalid before hashing. Score conversion uses actual baseline floating-point operations (`ml_p * 100.0`), not decimal arithmetic chosen to reproduce a rounded display.

### Exact incomplete-identity variants

Anchored occurrence uses **only** the eight keys in the worked example; partial occurrence adds **only** `partial_scope`. Missing values stay null in their specified members. `occurrence_ref.value` carries `missing_identity_members` and `raw_identity` outside `material` (these are not occurrence-ID preimage members). `raw_identity` is exactly `{date,home,away,competition,kickoff}`, with captured strings or null; `missing_identity_members` is empty for complete anchored evidence. Enumerate missing members as sorted JSON-pointer strings relative to material. Squad values must come from pinned normalization evidence, not bare senior defaults.

For a required missing selection, use signal preimage `selection_ref="unknown:selection_ref"` and add `partial_scope:{build_id,emission_attempt_ordinal}`. For required missing contracts, use `"unknown:<literal_contract_field_name>"` in just those fields and the same partial scope; path-specific not-applicable contracts remain null. Complete signal preimage has exactly the seven keys shown; partial scope is the only extra key. Partial selection/occurrence IDs cannot be generalized across builds. Rule/election/qualification IDs in the example are synthetic contract identifiers; implementing their real versioned definitions needs the approved contract registry, not a guess from legacy labels.

### Nested-reference projection example

Let `body_A` and `body_B` have identical **anchored complete** semantic fields from §4.5 but different `/body/inference_attempt_ref/value`, `/body/fade_receipt/value/parent_observation_ref/value` and `/body/fade_receipt/value/parent_inference_ref/value`. Also give them different envelopes, ordinals and artifact retrieval locations. The positive projection removes precisely those run-specific differences; `P(body_A) == P(body_B)` and `HC("mcp-evidence-v1", P(body_A))` is identical. Their complete `record_id` values differ. If `model_receipt` fitted-model SHA-256, ordered `x`, actual score or fade `parent_model_receipt` changes, the projection changes and evidence digests differ. This is not recursive field-name stripping. Equal `signal_id` with different fitted-model digests **requires model-stratified analysis**. Partial occurrence examples intentionally retain build scope and do not satisfy this equivalence.

Resource illustration: 128 individually small serialized receipts need not fit the 8 MiB retained-object/reservation pool. The maximum conservative slot is 1,057,792 bytes; only seven fit before control reservations. After a successful bounded copy, refund to the actual formula charge; cap count and total independently. This is accounting arithmetic, **not measured Python heap/RSS or latency**. A build reservation is 37 MiB +64 KiB; 480 MiB already charged leaves 32 MiB, so no such full reservation fits, much less two.

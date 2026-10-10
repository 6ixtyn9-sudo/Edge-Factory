# Audit implementation progress — 2026-10-09

**Incomplete implementation; no activation or acceptance.** This receipt is not
another design approval request. The authorized package remains unfinished.

Implemented a temporary-directory-only development collector and an optional,
read-only `mcp_audit` inference hook in `eval_1x2`. The production entry point
never constructs a handle. Only `EDGE_FACTORY_MCP_AUDIT=1` permits the explicit
temporary collector. Hashing, JSON and file writes run on its writer thread.
It captures the actual vector, imputed names, logit, raw fraction and qualifying
percentage even without emitting a rule. Fallback origins are explicitly
missing, not recomputed or claimed verified.

Executed: `tests/test_ml_consensus_audit.py tests/test_picks_today.py`:
**33 passed**. Controls cover OFF/no payload construction, immutable copy and
selected primitive limits, one non-emitting inference, enabled/disabled and
raising-recorder evaluator return parity, and partial/non-replayable close.
These are small synthetic controls, not historical replay or full acceptance.

## Outstanding work / acceptance gaps

- Complete schema validation and dependency inventories. Current development
  receipt values are partial; they are **not accepted v1 evidence** merely
  because their envelope uses the proposed schema tag.
- Capture fallback precedence at the actual vector builder, full election and
  supplier facts, guard decisions, rule/consensus/fade emissions, and actual
  collapse mapping. Signal/link writer branches are scaffolding, not hooked or
  accepted. No claim that the authorized hooks package is complete.
- Replace the bounded single-message mailbox with the specified atomic
  lifecycle/admission implementation; prove concurrent close/abort/refund
  behavior. Counters are best-effort and not exact loss accounting.
- Calibrate retained memory, writer scratch and latency on pinned runtime;
  exercise feature/metadata capacity, complete failure matrix, permutations,
  payload/archive equality and frozen-record invariance. Current tests do not
  establish these acceptance criteria.
- Temporary storage does not implement shared disk quota, reservation journal,
  owner locks, crash recovery or durable export. These must not be inferred
  from per-record limits or temporary directory ownership.
- Export route/steward remains unprovisioned. All current builds are partial
  and explicitly non-replayable, with no production activation API.

Production ignore rules, workflows, index publication, routing, thresholds,
model computation, and historical data were not changed. Six intentional
qualifier/electorate contract failures remain unsuppressed and unrepaired.

## Follow-up implementation and execution

This section supersedes the earlier implementation inventory, not the remaining
acceptance requirements. The test environment is captured in
`controls/audit-test-environment-2026-10-09.txt` (CPython 3.11.2, Linux).
Its SHA-256 is `f8f3d5131f0046ff937536035f01b8a54cd8c67e3effebe6e1bfe2fdbb3abd96`.

### Added and exercised

- Replaced the single-message mailbox with a bounded deque. One audit-only
  producer lock owns admission, copy, publication and refunds; acquisition is
  nonblocking on producers. The writer may wait on that lock. Worst-case
  reservations are retained through writer completion, including in-flight
  records. Payload factories execute only after admission. Close rejects new
  captures and drains accepted ones; failures release queued reservations.
- Active-GIL check, latched startup/shutdown abort, streaming segment digests,
  record-count and byte capacity reserved for close. Ordinary producer and
  serialization exceptions drop evidence rather than alter evaluator results.
- Actual per-column fallback origins from `feature_vector`, preserving its
  return tuple and default→payload→caller precedence. Origins accompany the
  vector in one inference receipt; there is no component reassembly workaround.
- Read-only ML-main, ML-fade and unanimous-consensus emission hooks capturing
  emitted rows plus actual thresholds and score operands. Fade captures the
  parent's qualification probability separately from its displayed score.
- Collapse capture from the **same selected object** chosen by the baseline
  `max`, without rerunning the representative election. The development hook
  records pre-sort cluster output ordinal, not a claimed final output link.
  Additional traversal has explicit limits and drops on oversized inputs.
- Offline development reader checks schema tag, segment inventory, digests,
  sizes, canonical lines, sequence/build identifiers, duplicate identities,
  record limits and open/close framing. This is not full approved-v1 validation.
- The schema tag is now `mcp-audit/development-v1`: partial development bodies
  must not masquerade as accepted `mcp-audit/v1` evidence.

### Executed results

```
.venv/bin/python -m pytest -q tests/test_ml_consensus_audit.py tests/test_picks_today.py tests/test_ml_fade*.py tests/test_phase5_k_candidate.py
217 passed in 13.53s

.venv/bin/python -m pytest -q tests
6 failed, 2557 passed in 54.67s

git diff --check
(no output; success)
```

The six failures are exactly the existing four unsupported-qualifier and two
substitute-electorate assertions in `test_consensus_contract_gaps.py`. They
remain unsuppressed. No new suite failures were observed. The focused controls
include real-writer capture of all three emission paths, enabled/disabled
return and input equality, both equal-rank permutations, startup/disk failure,
queue no-overwrite, admission-before-factory, refund, close and latched timeout,
fallback precedence, and offline segment corruption rejection.

### Remaining implementation gaps, not requests for approval

The authorized work is **still not fully delivered**. These are engineering
work outstanding, not external blockers or reasons to reopen design approval:

- Full approved-v1 body/wrapper validation, model/guard/activation/dependency
  receipts, complete non-emitting guard decisions and certification annotations.
- Full copied parent semantic receipt and evidence hashes for every emission;
  the experimental emission format currently captures operands and raw output.
- Cross-stage ordinals and final sorted output links across evaluator invocations
  and mixed-market inputs. Current ordinals are evaluator-local; do not combine
  different evaluations and infer valid run-wide links.
- Shared disk accounting, ownership/reservation/recovery controls and calibrated
  filesystem/runtime profiles. Caller-owned temporary directories do not prove
  these invariants. No automatic evidence reclamation is implemented.
- Receipt capacity tests for representative large models, allocation/scratch
  calibration, pinned representative p99 latency, full concurrent race matrix,
  and the unchanged §7.6/§7.7 whole-payload/archive/ticket/notification matrix.
  Passing all existing tests is not equivalent to executing that acceptance.
- Accurate exact attempt/drop accounting is not asserted; counters remain
  best-effort and every build remains partial/non-replayable.

The genuine external blocker remains the unprovisioned export route/steward.
No production activation, index publication, ignore/workflow changes, live
routing repair, retention integration or historical migration was performed.

## Acceptance execution and capacity blocker (latest)

**Status: not accepted v1; default-OFF temporary implementation only.** This
section supersedes earlier test counts. A concrete capacity conflict is now
reproduced rather than left as an unmeasured concern. It does not erase the
remaining semantic-receipt work listed below.

### Additional implementation

- Worker-only `TemporarySpool` shared reservation accounting, nonblocking Linux
  `flock`, 512 MiB cap, 37 MiB +64 KiB live slots, 64 KiB root charge, bounded
  file/directory inventories and measured-allocation checks. Ownership must be
  acquired to reconcile abandoned unused reservations. **No stored evidence is
  reclaimed**, whether old, abandoned or unexported. No cache is trusted as
  accounting authority. Symlinks, hardlinks, unknown entries and overflow refuse
  admission. Reservation writes use fsync/atomic replacement. Descriptors close
  on exec/fork; a child cannot reuse the inherited writer. The temporary-only
  API deliberately does not claim production filesystem-profile acceptance.
- Producer refunds maximum admission to actual retained charge after copying.
  Writer checks the serialized estimate and latches failure on violation.
  Scoring hooks no longer call `Event.set()` (which hides a blocking lock).
  Timed waits are worker-only. Public ABORTED state cannot be overwritten by a
  racing writer. Runtime is pinned to the tested CPython GIL build.
- Distinct namespaces across repeated evaluations prevent local ordinal/ID
  reuse; model-loader decisions record missing guard detail explicitly.
  Emissions use a positive projection, **not whole operational row dumps**.
  Collapse additionally captures actual pre-sort→final-sort order without
  changing sorting or choosing the representative again.
- Dependency inventory lists missing logical inputs explicitly rather than
  returning an empty inventory. No original model-byte digest is fabricated
  from a reserialized model object.
- Offline reader now verifies record/evidence hashes, envelope/type rules,
  wrappers, dependency-name agreement, close counts and preceding-segment
  inventory. Removed unused signal/link preparation scaffolding that was not
  connected to the experimental hooks. Development records remain explicitly
  `mcp-audit/development-v1`, not falsely labelled accepted v1.

### Commands and results

```
.venv/bin/python -m pytest -q tests/test_ml_consensus_audit*.py tests/test_ml_consensus_storage.py
30 passed in 0.38s

.venv/bin/python -m pytest -q tests
6 failed, 2575 passed in 62.18s

git diff --check
(no output; success)
```

The full-suite failures are still **only** the same six intentional contract
assertions. No suppression, policy repair or assertion weakening occurred.
The current installed package inventory is
`controls/audit-completion-environment-2026-10-09.txt`, SHA-256
`56383463be4dc83d2a94abe714d8b38954f0c293b7d89897ccd11d8e2d690268`.

The seven-state paired matrix executes actual inference/emission, pre-match
filtering, collapse, first-frozen archive merge, research capture, accumulator
selection, ticket-state persistence and write-once freeze. It compares whole
serialized test payloads and **exact persisted ticket bytes** against the
no-handle run. It includes nonempty ticket selection and checks input and
frozen-record invariance. It does not execute the complete daily CLI, remote
notifications, source export or unsafe-date publisher admission; therefore it
is substantial synthetic parity evidence, **not a substitute for all §7.7**.

Quota controls demonstrate 13 simultaneous live reservations, refusal of the
14th, no unexported/abandoned evidence deletion, quota-lock contention refusal,
symlink refusal, growth overflow, conservative live charging when reservation
metadata is absent, and child-descriptor isolation. They are not a tested
production publisher/export lifecycle.

### Reproduced contract-capacity blocker

```
.venv/bin/python docs/operator/controls/audit_resource_control.py
```

On CPython `3.11.2 (main, Apr 8 2026, 01:58:00) [GCC 12.2.0]`, Linux
6.1.158+, the 26-column legacy feature contract, with missing vector inputs,
produces actual fallback values/origins at `feature_vector`'s callback. Encoding
just the §4.2a full per-feature fallback receipts requires **4,441 string code
points**, while §5.1 permits **1,024 across keys and values**. The receipt also
correctly marks unexposed units missing. `freeze` rejects with `string limit`.
Fixture content SHA-256:
`e25cabec78afc7ce85eeeb64bfcb8e3d9b8a6c0eea14d14d89ecaedfe09c1ce2`.
This is a synthetic capacity control, not historical replay or a claim that all
26 live feature columns are normally absent. It is enough to disprove support
for this valid full-fallback shape under the unchanged cap. Adding the rest of
the model receipt or a copied fade parent cannot make it fit.

The separate numeric-512-feature probe reports:

- Immutable retained-size upper sum 16,799 bytes; accounted charge 132,872.
- JSON bytes 2,969; serialized estimate 17,510.
- Observed thaw+JSON peak 44,582 bytes (below the separate 2 MiB budget).
- One 2,000-sample run: copy-only p99 269.886 µs. This is **not** a whole-hook,
  full-model or representative-production p99 measurement or an RSS bound.

The test `test_capacity_contract_refuses_full_fallbacks` pins refusal. No
truncation, component reassembly, relaxed cap or complete-coverage claim was
introduced. Under the approved instruction to revise the contract when full
receipts do not fit, **accepted full-receipt implementation needs a reviewed
bounded representation/budget revision and renewed calibration**. This is a
specific contract blocker, not another generic request to authorize coding.

### What remains unaccepted

The existing experimental receipt shapes still do not supply all approved-v1
semantic model/guard/activation, full copied fade-parent, certification and
source-assembly fallback evidence. Dependency availability is missing rather
than established; cross-evaluation collapse links remain partial. Those facts
are not repaired by hashes, quota controls or the passing regression suite.
Full §7.6/§7.7 acceptance remains unchecked for the missing complete-evidence
paths. The capacity conflict must not be hidden by declaring the narrower
experimental format complete.

Separately, the external export steward/route is still unprovisioned. Production
activation, workflow/ignore edits, index publication and historical migration
remain untouched. No new operational input or consumer of the sidecar exists.

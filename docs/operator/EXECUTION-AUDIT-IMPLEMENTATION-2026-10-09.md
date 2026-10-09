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

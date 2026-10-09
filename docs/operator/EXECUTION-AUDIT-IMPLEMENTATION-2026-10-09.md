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

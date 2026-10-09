# Gate A review reconciliation and draft-3 disposition

**Date:** 2026-10-09 (SAST)<br>
**Status:** draft 3; A1–A3 renewed technical design approval; A4 amendment and operator authorization pending.<br>
**Original reviewed version:** `b7dac06e945f6e9c4b322b7b314d4b90a0c0701f` ([pinned draft 1](https://github.com/6ixtyn9-sudo/Edge-Factory/blob/b7dac06e945f6e9c4b322b7b314d4b90a0c0701f/docs/operator/GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md)).<br>
**Amended specification:** [draft 3](GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md).

## 1. Source identity and verdict history (draft 1)

Two supplied reviews are recorded separately by content, not by permanent agent identity. This is an assistant-authored reconciliation, **not** a verbatim import of a reviewer's decision file and **not** operator authorization.

| Supplied review | A1 | A2 | A3 | A4 | Authorization boundary |
|---|---|---|---|---|---|
| S1 — storage-verification/decision report | Approve | Approve | Approve | Approve with amendments | A4.1 before recorder code; A4.2 removed; A4.3 explicitly decided; parity/failure controls unchanged |
| S2 — pinned-spec contract review | Amend | Approve with clarifications | Amend | Approve architecture, amend lifecycle | Gate A conditional; no authorization to code yet |

S1 reports `docs/operator/GATE-A-DECISION-2026-10-09.md` committed at `d3dfe5c`. Neither that file nor that object is available in this session's checkout (`git cat-file -t d3dfe5c` fails). Its location/full commit/bytes are unverified here; do not call it a decision committed on this branch or adopt its document identity. This reconciliation uses a distinct filename and preserves that attribution. No external commit was fetched or imported.

S2's 37,926 serialized / 102,594 estimated resident-byte illustration is reviewer-reported, not a recorder benchmark reproduced here. S1's 78 MB warehouse and 396-vs-437 sensitivity are reviewer-reported controls/log observations, not newly run measurements. Neither review establishes implementation acceptance, export verification, replay completeness or live routing authorization.

## 2. Amendments made in draft 2

| Request | Draft-2 resolution | Still requires proof/approval |
|---|---|---|
| S2 A1.1: float-free logical IDs versus numeric content | §2 separates `HI`/`HC`; record/content floats allowed; canonical LF record bytes and noncanonical rejection specified | Exact runtime encoding/schema and hash-vector implementation |
| S2 A1.2: nested evidence projection | §4.5 positive JSON-pointer projection; excludes designated inference/fade run references and retrieval metadata only, retains semantic model/dependency IDs and parent evidence | Projection tests, no generic ID stripping, partial identities remain build-local |
| S2 A1.3: raw probability/fallback provenance | Raw fraction, actual qualification percentage and rounded display separated; per-feature actual fallback value/stage/origin/verification, including defaults/overrides/unknown-column zero | Actual capture/precedence with no scoring changes |
| S2 A1.4: non-emitting inference | First-class full `inference_observation` independent of rule emission; minimal diagnostics cannot substitute | Executed-but-no-emission vector/score/target/guard coverage |
| S2 A2 clarifications | Exact preimages/wrappers/null/partial cases and worked SHA-256 examples; ordinal-only producer tokens, writer-side IDs; fitted-model-stratified analysis mandatory | Real contract registry, safe baseline collapse ordinal mapping, unchanged IDs/payloads |
| S2 A3 accounting | Reserve conservative maximum before private copy; explicit node/string/depth caps, retained-object charge separate from serialized estimate, in-flight reservations included; startup/close/contention/abort semantics | Runtime allocation calibration, queue/mutation/close races, p99 measurement and disabled/enabled/failure parity |
| S1 A4.1: oversized dependency bytes | >1 MiB reference default; separate record/small-copy budgets, named input artifact repository/path and export-steward prerequisite; replay capabilities checked early | Route provisioned, steward assigned by operator, immutable bytes uploaded/download-verified, expiry monitoring |
| S1 A4.2 / S2 A4.1: cleanup overstatement | Remove exclusion prerequisite for currently ignored nested spool; top-level cleaner cannot recurse; `git clean -fd` normally preserves ignored files | Index re-inclusion creates different untracked/nonignored first-stage risk; pilot ordering/failure recovery tests |
| S1 A4.3: manifest-only Git route | Explicitly propose bounded manifest-only index pilot, not bulk tracking or proof of byte durability; dedicated artifacts retained for evidence | Approve pilot limits/ancestor ignores/immutable publication, index push verification; bulk-export approval still needed for evidence-complete enablement |
| S2 A4.2: shared quotas/abandoned builds | Global worker-side lock/reservations, charged-usage recovery, full per-build allocation, local owner `flock`, no heartbeat-only death inference, abandoned partials reclaimable | Concurrency/crash/accounting/filesystem-profile/lock-inheritance tests and honest external-write residual risks |
| S2 A4.3: export lifecycle | No `export_verified` close state; close inventories preceding segments; manifest inventories close too but not itself/later export receipt; verification only after independent download | Full close/manifest/upload/verification/expiry failure tests |

**Correction acknowledged:** draft 1's absent-exclusion language was too strong. The new stream lacks a durable artifact route, but absence from existing Phase5 exclusions does not prove current cleanup deletes ignored bulk. `clean_localdata.py` needs no new nested-spool exclusion. A newly re-included untracked manifest needs separate ordering/recovery analysis; that is not the same claim.

**Storage choice made for review, not implemented:** bounded compact-index pilot is an index-only option. Bulk segments and dependency bytes remain untracked; a committed digest/index cannot recover them. Therefore the workflow blocker is removed only from the index pilot, not from evidence-complete production enablement. The artifact route may be replaced by an explicitly approved external audit-only uploader, but no uploader is assumed provisioned. Long-term retention is not adopted. Draft 2 proposed unexported eviction as a potential evidence-loss policy. **Superseded by draft 3:** refusal-only retention; no automatic unexported finalized/abandoned evidence eviction.

## 3. Verification actually performed for this amendment

Read-only source inspection:

- `.gitignore:10,133–144`; read-only `git check-ignore -v` confirms the proposed nested spool is ignored.
- `clean_localdata.py:165–176`: top-level files-only pattern traversal.
- `phase5_persistence.py:172–188,302–305`: ordinary tracked-file restore, `git clean -fd` (no `-x`/`-X`), `git add -A localdata/`; only existing named JSONL paths get conflict unions.
- `daily.yml:207–212,221`: new artifact layout not matched.
- `phase5_k.feature_vector`: code defaults, payload overrides, caller overrides, unknown-column `means.get(col, 0.0)` precedence.
- `picks_today.py:4498–4503,4580,4593`: actual vector/logit/fraction inference, qualification `ml_p * 100.0`, separately rounded percentage display.

Illustrative documentation checks only:

- CPython 3.11.2 JSON/SHA-256 checks of ten worked preimages, including numeric content; synthetic model and consensus IDs differ. Illustrative positive projection equality survives changed nested inference/fade run references and retrieval locations; a changed raw score changes the projection. These calculations do not constitute schema or recorder tests.
- Isolated temporary Git repo ignore-rule example: re-include every ancestor plus **only** `build-manifest.json`; record segments, input copies and lock/reservation files stay ignored. This is not implemented production staging/cleanup integration.
- Documentation whitespace, local links/fences and unchecked acceptance boxes.

No cleanup, providers, model fitting, production pipeline, operational-state write, executable schema/recorder, latency/allocation benchmark, adversarial failure suite, replay or artifact upload/download verification was run. The specification's quota/memory coefficients and lifecycle are proposed contracts awaiting implementation proof, not experimentally established guarantees.

## 4. Renewed draft-2 reviews — current supplied verdicts

The renewed reviews concern [draft 2 pinned to `49a83da`](https://github.com/6ixtyn9-sudo/Edge-Factory/blob/49a83da64e1ff0ea103177abd69ce6cba5188d0c/docs/operator/GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md).

| Review (content-linked to above) | A1 | A2 | A3 | A4 | Actual reported scope |
|---|---|---|---|---|---|
| S2 — pinned-spec contract/staging review, pasted first in latest message | Approve as design | Approve as design | Approve design subject to acceptance gates | Amend index-publication boundary | Read pinned draft 2; independently matched all ten hash vectors; isolated nine-manifest/oversized broad-staging control |
| S1 — storage-facts/rulings review, pasted after “agent 2” | Approve renewed | Approve renewed | Approve renewed | Approve with operator rulings | **Did not read draft 2 line by line**; read reconciliation and independently verified cleanup, ignores, artifacts and cleaner facts |

Do not collapse these scopes or treat a pasted agent number as a stable identity. S2's staging result (nine manifests staged, including an oversized one, no record segments) is reviewer-reported, not a production failure or a local recorder test. It correctly exposes draft 2's dual-use filename: Git cannot enforce size/count eligibility when all detailed manifests share a re-included name.

S1 reports a renewed decision file `GATE-A-DECISION-DRAFT2-2026-10-09.md` at local-only `4764711`. As with its earlier `d3dfe5c` decision, no document is imported or adopted as local authority. No further external-record reconciliation is needed to amend A4. Its “operator rulings” are **supplied reviewer recommendations**, not authority to assign an owner, provision resources, code or activate. No operator authorization has been given in this exchange.

## 5. Draft-3 A4 resolution

- **Separate publication path/name:** all detailed `localdata/ml_consensus_audit/**/build-manifest.json` remain ignored. Only separately typed `localdata/ml_consensus_index/v1/compact-index_YYYY-MM-DD_01.json` through slot `08` may become eligible, after size/count/window admission. No stageable oversized/ninth/refused compact file; detailed manifest content can never fall into the index allowlist.
- **R1 ordering:** bootstrap ignore rules and first admitted compact index must be locally committed together before any persistence helper. Subsequent publication also commits before restore/clean. Documented publisher lock/coordination barrier, ignored candidate/journal, atomic slot reservation, exact-path stage/commit and crash recovery must prevent broad staging or cleanup in the rename→commit window. Existing persistence has no such barrier; future integration must prove it or the pilot is deferred. No code or ignore change is implemented here.
- **R2 resources:** explicitly no steward assigned/no export route provisioned. Evidence-complete production enablement is blocked. Close and compact index must say `unprovisioned` and durable replay capabilities `non_replayable` before any analysis. Full copied evidence can still support local diagnostics; it cannot assert durable replay acceptance.
- **R3 refusal-only retention:** never automatically evict unexported finalized or abandoned evidence. Reclaim verified-export builds only after owner-lock acquisition; otherwise stop auditing at quota exhaustion with incomplete coverage. Thirty days becomes an exported retention/reclamation target, not an unexported deletion deadline. Runner/cache loss is still outside collector guarantees; long-term retention remains separately unapproved.
- **R4 quota:** retain separate retained-object/serialized accounting and shared spool reservations. Abandoned classification/reclamation requires explicit lock acquisition, never heartbeat/staleness alone.

A4 implementation must test ninth slot, oversized detailed/compact manifests, retries, failed validation/commit/push, crashes before/after publication/staging/commit, concurrent publishers, bootstrap single commit and restore/clean coordination. Broad `git add -A localdata/` must find only eligible compact indices, never detailed manifests/bulk or refused compact outputs. Existing §7 items 6 and 7 remain unchanged, not traded for storage acceptance.

## 6. Verification for draft 3 and next decision

An isolated temporary Git repository demonstrates the **new path separation only**: nine ignored detailed manifests (including >8 KiB), eight separately allowlisted compact indices, and ignored rejected-candidate/control/record files; broad staging selects exactly eight compact indices. A slot-09 name is ignored. This is an ignore/staging layout control, **not** proof of the proposed publisher's admission, concurrency or crash/commit barrier. Those require implementation tests after authorization. The old `build-manifest.json` allowlist example in §3 describes draft-2 checks, now superseded.

Rechecked ten documentation hash vectors, local links/fences, whitespace and unchanged §7 permutation/failure controls. No production cleanup, persistence, ignore/workflow changes, recorder, benchmark, replay, export verification or historical mutation occurred.

**Decision requested:** technical review of draft-3 A4's separate compact-index publication and refusal-only lifecycle, then explicit **operator** Gate A completion/authorization before coding. A1–A3 design approvals do not accept their future implementation. Pilot integration remains proposed; evidence-complete production enablement remains blocked on missing steward/export resources. The [acceptance checklist](CHECKLIST-ML-CONSENSUS-PROVENANCE-2026-10-09.md) stays unchecked. Live routing, operational schema migration and long-term retention are not approved.

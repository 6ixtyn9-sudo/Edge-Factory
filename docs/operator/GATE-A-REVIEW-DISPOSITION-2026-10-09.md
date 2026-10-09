# Gate A review reconciliation and draft-2 disposition

**Date:** 2026-10-09 (SAST)<br>
**Status:** documentation-only amendment; renewed approval required before coding.<br>
**Reviewed version:** `b7dac06e945f6e9c4b322b7b314d4b90a0c0701f` ([pinned draft 1](https://github.com/6ixtyn9-sudo/Edge-Factory/blob/b7dac06e945f6e9c4b322b7b314d4b90a0c0701f/docs/operator/GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md)).<br>
**Amended specification:** [draft 2](GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md).

## 1. Source identity and current verdicts

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

**Storage choice made for review, not implemented:** bounded compact-index pilot is an index-only option. Bulk segments and dependency bytes remain untracked; a committed digest/index cannot recover them. Therefore the workflow blocker is removed only from the index pilot, not from evidence-complete production enablement. The artifact route may be replaced by an explicitly approved external audit-only uploader, but no uploader is assumed provisioned. Long-term retention is not adopted. Unexported-build eviction under quota/expiry is explicitly a potential evidence-loss policy, not guaranteed preservation; refusal-only retention can be chosen by renewed review instead.

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

## 4. Decision requested

Renew explicit A1–A4 review of draft 2, particularly the complete inference/projection contract, calibrated admission accounting, manifest-only pilot versus verified-byte route, assigned export ownership, shared quota and unexported retention-loss policy. Publication does not resolve these decisions automatically.

The [acceptance checklist](CHECKLIST-ML-CONSENSUS-PROVENANCE-2026-10-09.md) remains unchecked. **§7 items 6 and 7 — per-order permutation parity and the full enabled/disabled/failure matrix — are not weakened.** Implementation is not started/accepted. Live routing, operational schema migration and long-term retention remain separate approvals.

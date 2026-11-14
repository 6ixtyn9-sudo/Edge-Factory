# Gate A review reconciliation and draft-3 disposition

**Date:** 2026-10-09 (SAST)<br>
**Status:** DESIGN APPROVED — A1–A4 approved, C1 satisfied by supplied independent confirmations. Only fallback-origin fix and failing contract tests authorized/performed, outside Gate A. Audit implementation/activation remain unauthorized.<br>
**Original reviewed version:** `b7dac06e945f6e9c4b322b7b314d4b90a0c0701f` ([pinned draft 1](https://github.com/6ixtyn9-sudo/Edge-Factory/blob/b7dac06e945f6e9c4b322b7b314d4b90a0c0701f/docs/operator/GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md)).<br>
**Current specification:** [draft 3 + C1](GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md).

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

S1 reports a renewed decision file `GATE-A-DECISION-DRAFT2-2026-10-09.md` at local-only `4764711`. As with its earlier `d3dfe5c` decision, no document is imported or adopted as local authority. No further external-record reconciliation is needed to amend A4. Its “operator rulings” are **supplied reviewer recommendations**, not authority to assign an owner, provision resources, code or activate. No operator authorization was given in that draft-2 exchange; the later limited authorization is recorded in §7 below.

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

## 7. Latest draft-3 decisions and limited operator authorization

| Source | Current decision | Verification/authority scope |
|---|---|---|
| Latest operator-supplied decision (reported file `GATE-A-DECISION-DRAFT3-2026-10-09.md`, `35b0c88`) | A4 approve with C1; R1–R4 confirmed; explicitly authorizes fallback-origin correction and failing qualifier/electorate tests outside Gate A | Reviewed amendment summary, **not draft-3 prose line by line**; three same-spool ignore attempts could not reproduce the described separation. Requires exact block/output. |
| Latest pinned-prose technical review (pasted after “agent 2”) | A4 technical design approved; no further design amendment; A1–A3 approvals stand | Read pinned `8c49c55`, independently staged eight compact indices with nine detailed manifests (one 16,428 bytes), no bulk/control/slot09/candidate staged. No admission/crash/publisher acceptance. |

These verdicts supersede the earlier A4 amendment request but do not waive C1. Do not relabel the latest operator text as merely reviewer advice: **its two named changes are expressly authorized now**, independently of Gate A. Conversely, do not extend that authority to recorder, hooks, ignore changes, index publication, workflow edits, routing, schema migration or long-term retention; they are expressly forbidden. The reported `35b0c88` decision remains external/unimported, not a local commit or a license to rewrite historical decision records. No further external-file identity investigation is needed for these explicit supplied instructions.

Implemented the authorized work **first**, committed/pushed `6c3699d`, then published the exact C1 rule addition and output. See the [execution receipt](EXECUTION-FALLBACK-CONTRACT-TESTS-2026-10-09.md): 160 related regressions pass; six positive contract controls pass; six unsuppressed contract assertions intentionally fail. Existing threshold/OU/BTTS return values compare exactly to the old function across seven temporary registry cases. This is not live qualifier/electorate repair, recorder acceptance, full payload replay or deployment.

**C1 evidence:** the [specification §10](GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md) contains the exact five-line addition and complete per-file `IGNORED`/`STAGEABLE` plus `git add -A -n localdata/` output. The [control script](controls/gate_a_c1_paths.py) copies the real repository ignore baseline read-only into an isolated temp repo and appends that addition only there. It asserts eight compact filenames stageable, nine detailed manifests ignored, no bulk/control/slot09/generic compact filename admitted. No production ignore changes occurred. A generic `compact-index.json` is intentionally ignored; only date/slot names qualify. This proves layout separation, not size/count admission or crash/publication coordination. Confirm C1 against the now reproducible block/output before any further Gate A implementation decision.

§7 items 6/7 remain unchanged. Missing steward/export resources keep evidence-complete production enablement blocked. Limited code/test work is complete on this branch, not merged/deployed; all other implementation/activation prohibitions remain in force.

## 8. C1 confirmed — current disposition (supersedes pending-C1 notes above)

Both latest supplied confirmations reproduce the exact `d458128` rule addition against the real ignore baseline: eight compact slots staged, detailed manifests/records/control files and slot 09/generic names/candidates ignored. The first reports **byte-identical complete output**, independent seven-case old/new fallback comparison and direct evaluator reproduction of six positive passes/six unsatisfied negative assertions. It explicitly did **not** rerun the reported 30/160/50 pytest selections. Those remain local scoped execution-receipt results, not independent full-suite acceptance. The second reports verbatim block reproduction and records C1 satisfied in external `GATE-A-C1-CONFIRMED-2026-10-09.md` at `762373a`. Its separate housekeeping/recommit report `6442049`, decision records and Kladno settlement row belong to that workspace; their bytes/history were not imported, locally verified or applied here. No further external-history investigation or historical-row change follows from this confirmation.

**A1–A4 design approved; C1 satisfied.** This is path/staging evidence only. An oversized file under an eligible name is stageable; size/count admission still belongs to the nonexistent future publisher. No production ignore application, recorder, hooks, index publication, workflow change or audit activation is authorized. Bulk export remains **blocked** by missing route/steward. Live routing, schema migration and long-term retention remain unauthorized.

`6c3699d` delivered the authorized fallback-origin correction and OU-only regression plus unsuppressed qualifier/electorate contract tests before C1 publication. **Keep all six failures visible.** Six positive controls pass, six negative assertions fail; a full suite containing them is red, regardless of the 160 passing related regressions or 50 passing link tests. No skip, xfail, predicate weakening or selection repair is authorized by these confirmations. The incumbent fallback warning's wording remains too narrow for OU/BTTS-only registries; scoped confirmations acknowledge it, not a further diagnostic patch authorization.

Current session status was checked locally: `d458128` and `6c3699d` are present and the worktree was clean at the start of this confirmation update. This update changes current-status documentation only; it does not replicate the other workspace's re-clone or housekeeping operations. No new implementation/control/test result is claimed. Next action is an explicitly scoped operator authorization, not another C1 review loop or automatic implementation.

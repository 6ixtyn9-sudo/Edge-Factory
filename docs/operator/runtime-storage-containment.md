# Receipt runtime and report-upload containment

## Incident and scope

Production run `44060709021` took 2h35m35s. Its two PAPER subprocesses used
2,735.7 seconds combined; the separate ENH report also repeatedly processed
PAPER history. The reports artifact was 5,476,080,381 bytes. The final replay
step timed out despite the overall Actions result being green.

This repair changes processing, recovery and report packaging, **not** Main/ENH
selection, floors, stakes, banks, admission policy or historical PAPER decisions.
No production ticket/settlement command or evidence cleanup is needed to deploy
it. Existing frozen JSON bytes and signed hashes are not rewritten.

## Deployment: code PR plus a manual workflow update

**This PR does not change `.github/workflows/daily.yml`.** GitHub rejected the
unpublished combined commit because the integration lacks workflow-write
permission. The full replacement is supplied separately at
[`daily-runtime-storage.yml`](daily-runtime-storage.yml).

1. Review and merge the code PR only when explicitly approved. No merge or
   production dispatch is performed by this handoff.
2. After that merge, replace `.github/workflows/daily.yml` on **main** with the
   complete contents of `docs/operator/daily-runtime-storage.yml` and save it
   using your own workflow-authorized GitHub access.
3. If the live workflow acquired unrelated edits since this handoff, preserve
   those edits and apply only the report-bundle/upload and replay-step changes.
   At preparation, main's workflow matched the branch's original workflow.
4. On a subsequent normal run, inspect `REPORT_ARTIFACT` totals, missing-shard
   warnings and the dedicated replay report. An incomplete audit is not MATCH.

The PAPER processing, shard recovery, receipt retention and harness safeguards
are code changes. Thin-upload wiring, the 150-second external process deadline,
stale-output removal and workflow-side provenance checks become active only
when you apply the manual workflow. Do not expect the artifact/upload savings
from merging the code alone. The live workflow is intentionally left intact.

## One validation per locked PAPER operation

`ml_paper.paper_run()` owns the existing lane lock and loads/validates frozen
history once for capture, publication and adjacent display. Each invocation
rereads disk; there is no process-global or on-disk "already validated" cache.
The snapshot is discarded before releasing the lock. New publications still
pass the complete publication validator before atomic write-once storage.

- Receipt checksums, model/forecast binding, admission and concentration checks
  remain mandatory. The loader no longer calculates the same JSON checksum twice.
- Capital-chain, fixture-reuse and supersession checks remain shared by normal
  reads and restore. Restore retains only the small cross-record projection
  after individually validating each record; it does not replay every model
  again merely to perform a no-op layout migration.
- The public `performance(history, lookup)` still validates arbitrary caller
  dictionaries. Only private grading inside the checked operation can reuse its
  validation. Scores and derived reports are **not** memoized: a different result
  lookup is graded again, even within the same operation.
- The loader retains storage hashes for duplicate-layout comparisons, rather
  than another full-history copy of raw JSON alongside the expanded graph.
- Timestamped rolling PAPER scans, including no-ticket scans, are capital/model
  evidence. Cleanup no longer deletes them after 30 days and breaks later
  receipts' pinned history. This is preservation, not an unbounded telemetry
  retention exemption for other families.

A read-only benchmark of one retained 30,942,252-byte / 7,166-candidate receipt
measured the validation-plus-grading core at a median **12.39s before / 6.73s
after** (two trials each). Reports were exactly equal and the receipt's byte
hash stayed unchanged. This measures removing one redundant model replay; it is
**not** a full-history bank calculation or an end-to-end production runtime
forecast. The rolling sibling-report path additionally drops from five complete
history reads to one. Mining, pick builds and fresh settlement-index loads still
cost time.

## Committed manifests and cache-only shards

Multipart receipt shards intentionally do not enter Git. A committed manifest
is authority for their *identity*, not permission to trust arbitrary cache data.
Restore resolves a shard from Git when tracked there, otherwise from its exact
cache/artifact sibling name. The existing reader verifies each pinned length
and SHA256, the entire compressed stream SHA256, gzip integrity, the signed JSON
digest and filename/lane/date binding before accepting identical storage.

Valid cache-only shards no longer generate a conflict copy on every restore.
They also need not be retained again as multi-GB Python byte dictionaries when
the protected worktree already holds them. Missing/corrupt shards, a bad signed
payload, incorrect identity or genuinely divergent frozen evidence remain
visible conflicts. The fix cannot invent the genuinely unavailable historical
parts observed in the incident. Previously quarantined evidence is not deleted
or silently approved.

## Reports artifact: thin, lossless and independently reconstructible

Once the manual workflow is applied, the existing `phase5_persistence.py`
prepares `EdgeFactory-Reports` **after** the cache/Git durability barrier. It inventories the former report families plus
preserved conflict and archive directories. Raw scored-candidate ledgers keep
their existing separate artifact and retention.

`recovery_manifest.json` records every selected original path, byte length and
SHA256, and one of:

1. **Git**: the exact published commit and blob. A file is omitted from the
   payload only after hashing its actual bytes and matching that published
   tree. An unpushed local state commit is never a substitute. With no known
   published remote ref, all selected bytes remain artifact payloads.
2. **Artifact**: the payload file and its lossless encoding. Cache-only shards,
   changed/unpublished files and damaged evidence remain included. Equal
   payloads are stored once, but all original paths stay in the manifest.

Current root reports and financial snapshots remain payloads even if committed.
Large text payloads use gzip level 1; already-compressed shards are not deflated
again by the upload action (`compression-level: 0`). Immutable shard staging can
use hardlinks on the runner so packaging does not allocate a second multi-GB
copy; the upload contains actual bytes, not external links.

If bundle preparation fails, the workflow uploads the original full report
families instead. Report retention remains **7 days**, candidate retention
**30 days**. No family is discarded just because it exceeds a size threshold.
The bundle records missing/corrupt manifest dependencies explicitly and warns
above a 2 GiB payload; that warning is **not a hard aggregate cap** and does not
block financial saves. A storage inventory is not a valid-receipt or parity
certificate.

### Recover a downloaded bundle

Download and extract `EdgeFactory-Reports` into a scratch directory. If it
contains `recovery_manifest.json`, run from a repository clone with the pinned
commit available:

```sh
python3 scripts/phase5_persistence.py artifact-recover \
  --bundle .cache/downloaded-reports \
  --destination .cache/recovered-reports
```

The destination must be a **new** directory. Output appears beneath its
`localdata/` subdirectory. Every reconstructed payload is checked against its
original byte length and SHA256; Git entries also verify the pinned blob.
A shallow clone may need to fetch the manifest's `published_git_commit` first;
no branch switch is necessary. Recovery exits nonzero if required receipt
parts remain unavailable. Missing bytes remain missing, never a fabricated
complete receipt.

This command cannot merge into live localdata or overwrite financial ledgers.
Use the existing receipt reader/financial-restore checks before admitting
recovered evidence. If the upload was the raw fallback (no manifest), its files
already have the original layout; the thin-bundle recovery command does not
apply. Never copy a historical financial snapshot over current booked state.

## Replay is current-run evidence, never a cached verdict

The replay stays last and non-gating. Its internal budget now interrupts a
single expensive receipt/result load on the POSIX main thread, rather than
checking only between receipts. Expanded graphs are dropped between receipts.
A separate 150-second process timeout leaves summary time before the existing
3-minute step limit; a long native call can still require this safety net.

Before expensive work, the CLI atomically replaces any previous output with
`INCOMPLETE_INTERRUPTED`, bound to the current run ID/attempt/start time. It
publishes a final verdict only on completion. The manual workflow also removes
the cached output before starting and checks current-run provenance before showing
PASS. `INCOMPLETE_TIME_BUDGET`, `INCOMPLETE_INTERRUPTED`, missing output and
unbound/stale output are **not parity MATCH**. An already observed mismatch
still fails even if the remaining audit exhausts its budget.

Only the final dedicated `Replay-Parity-<run>` artifact carries that invocation's
replay report. The general reports bundle excludes the older cached replay
file. A green overall workflow remains neither full-history parity nor proof
of betting performance.

## Deliberate limits

This is not a Git-history rewrite, a migration of frozen JSON storage formats,
or deletion/consolidation of old conflict evidence. Legitimate historical
receipt growth and the retained cache footprint remain; thin uploads do not
make those bytes vanish. They stop being repeatedly repackaged when a verified
published Git replacement exists, and false shard conflicts stop multiplying.
Production end-to-end savings must be measured after an explicitly approved
merge/deployment; the previous run's 100-minute schedule contained substantial
non-PAPER work too.

## Local validation

- Before separating the manual workflow: full suite **7,225 passed, 2 skipped**
  in 426.72s, Python 3.11.2. After separating the manual workflow, **354 targeted
  tests passed** in 14.51s. Runtime source is byte-identical to the full-tested
  implementation; the complete manual YAML parses and all shell blocks pass
  `bash -n`. Both the existing upload lane and the proposed replacement retain
  cache-only receipt evidence. The hosted workflow uses Python 3.13; a hosted rerun is not claimed here.
- SHA256 comparison across **all 1,148 tracked localdata files** found no byte
  changes after the tests, including frozen receipts and Main/ENH financials.
- Regression cases cover one validation per operation, fresh score lookups,
  cross-operation corruption/fork detection, required shard and signed-payload
  failures, idempotent cache-only shard restore, cold-clone artifact recovery,
  unpushed-commit fallback, interrupted audit provenance and budget interruption.

# Recovery and storage

[Operator handbook](README.md) · [Settlement](SETTLEMENT.md) ·
[Research](RESEARCH.md) · [Evidence](DATED-CLAIMS.md)

**Preserve evidence first.** A conflict is not permission to discard a cache,
reset a bank, regenerate an old forecast or overwrite a frozen decision.
Recovery commands below are not authorization to run a production pipeline.
The [installed daily workflow](../../.github/workflows/daily.yml) is the only
workflow authority; no copy/paste replacement YAML is maintained in docs.

## State, restore and publication

- Both jobs check out `${{ github.ref }}` when they start, after the shared
  concurrency queue releases. The event SHA can predate the preceding run's
  state commit/cache; do not restore newer finance against that old checkout.
- The normal workflow restores the existing `localdata-v2-` cache family, then
  calls `python3 scripts/phase5_persistence.py restore`. The helper validates
  protected financial/frozen evidence before restoring committed data.
- Genuine unknown bank, stake, frozen identity or receipt divergence fails
  closed. Keep all versions/quarantine; do not take “ours/theirs” across
  `localdata/`. A recognized, committed reviewed correction is not authority
  to accept unrelated cached changes.
- Cache save and Git persistence sit **before** bundle uploads and the final
  non-gating replay. Their `always()` conditions preserve recoverable state
  after an earlier failure; that is not proof that all preceding work passed.
  Persistence still has its own history/finance checks and reports failures.
- Verify the actual save **and push** outcomes. A runner-local summary, local
  commit or artifact is not a verified published state. Regression tests run
  in a separate job without production secrets or a restored localdata cache.

Do not run restore/clean over the only copy of uncommitted evidence. Preserve
and inspect it first. Code/docs changes should stage explicit paths; broad
manual `git add -A localdata/`, blanket discards and force conflict-resolution
recipes are not a recovery procedure.

## Frozen receipts and multipart shards

A receipt's signed payload, lane/date/filename identity and pinned dependencies
are authority; a filename or successful storage inventory is not validation.
Readers support the existing plain/gzip/multipart layouts without rewriting
frozen JSON. Manifest-pinned shards may be **cache/artifact-only** by design.
A fresh clone can therefore be incomplete even when its manifest is committed.

Restore checks each shard's exact sibling name, byte length and SHA256, the
whole compressed stream/gzip integrity, signed JSON digest and identity binding.
A correct cache-only shard is not a conflict merely because it is untracked.
Missing, corrupt or divergent parts remain visible failures; neither manifest
nor cleanup can invent them. Do not remove prior quarantined bytes to make the
report look clean.

PAPER processing validates once inside each locked operation and discards that
snapshot on unlock. New operations reread/validate disk; result grading is not
memoized. Rolling PAPER scans, including no-ticket scans, may be pinned capital
or model-history evidence and are **not disposable 30-day telemetry**.
Main/ENH banks, stakes, decisions and historical PAPER outcomes do not change
as a consequence of packaging or restore.

## Report artifacts and scratch recovery

`phase5_persistence.py artifact-bundle` prepares the existing
`EdgeFactory-Reports` artifact after the durability barrier. Schema:
`edgefactory_report_bundle_v1`. `recovery_manifest.json` inventories each original
path, byte length and SHA256 plus either:

- **Git:** exact verified **published** commit/blob matching those bytes.
  Unpushed local commits are not substitutes; without a known published ref,
  all selected bytes remain artifact payloads.
- **Artifact:** actual lossless payload (including cache-only shards,
  unpublished changes and damaged/conflicting evidence). Equal payloads can
  be stored once while all original paths remain inventoried.

Current root reports and financial snapshots remain payloads even if committed.
Large text uses gzip level 1; already-compressed shards are not re-deflated by
the upload action (`compression-level: 0`). If packaging fails, the workflow
uploads the original full report families instead. Reports retain **7 days**;
raw scored-candidate ledgers use their separate **30-day** artifact. Retention
is finite; a requested retention is not proof an old download remains available.
A 2 GiB warning is **not a hard aggregate cap** and never authorizes deleting
financial evidence. Thin uploads do not shrink legitimate history or cache size.

Download/extract reports into scratch. For a manifest-bearing bundle, from a
clone containing its pinned commit:

```sh
python3 scripts/phase5_persistence.py artifact-recover \
  --bundle .cache/downloaded-reports \
  --destination .cache/recovered-reports
```

The destination must be **new**, never live `localdata/`. Reconstructed files
appear beneath its `localdata/` child. Every file is checked against original
size/hash; Git-backed files also verify the blob. A shallow clone may need to
fetch the manifest's `published_git_commit`, without switching branches.
Missing required parts produce a nonzero exit, not a fabricated complete receipt.
A raw fallback artifact has the original layout and no bundle manifest; this
command does not apply to it.

Recovery reconstructs bytes, **not admission**. Apply the existing receipt and
financial-restore checks before any explicitly reviewed integration. Never
copy an old financial snapshot over current booked state. Cache IDs/artifact
names alone are not durable proof that matching bytes are still retrievable.

## Replay evidence

The replay is last and non-gating. Its normal decision-parity window is seven
days with a 120-second internal budget, a 150-second external process deadline
and a three-minute step limit. Those bounds deliberately do not certify the
whole retained history.

Before expensive work the CLI atomically replaces old output with a current-run
`INCOMPLETE_INTERRUPTED` checkpoint. Workflow-side cleanup/provenance checks
prevent a cached verdict from being shown as this attempt's success. A final
verdict needs matching run ID, attempt and start-time binding. Missing/stale
output, `INCOMPLETE_INTERRUPTED` and `INCOMPLETE_TIME_BUDGET` are **not MATCH**;
an observed mismatch still fails even if the remaining audit runs out of time.
Only the dedicated `Replay-Parity-<run>` artifact carries that invocation's
report; the general bundle excludes stale replay output. A green overall job
is not a complete audit, a runtime improvement measurement or betting evidence.

## Prediction-history recovery

`recover_and_rebuild` is the existing **narrow historical** recovery path, not
an everyday recommendation or blanket approval to recut an arbitrary date.
The original reference is exactly **`localdata-v2-39371954018`**, with no fallback
cache. Its research passes were not themselves activated contracts or untouched
forward proof. An expired/missing/corrupt reference must fail closed; do not
substitute a convenient newer cache.

The workflow stages the current whole state outside localdata (`history-prepare`),
restores the donor at the original cache path/version, then runs `history-recover`
even if the donor restore fails, provided staging succeeded. Only allowlisted
raw prediction CSVs are unioned; **all other current files are restored**.
Old tickets, banks, registries, warehouse, prices and ledgers do not migrate.
Prediction/result conflicts are retained for quarantine, not guessed away.

`history-check` runs before mining and again before publication. The cached
fixture-key high-water mark is a completeness check, not certification.
Missing/truncated prediction history blocks the dependent actions. Existing
miner activation must recreate exact contract statistics; assay/decay retain
their own gates and new contracts start WATCH.

Only the explicitly approved unplaced date can be rebuilt. That path uses
cached execution boards, `--rebuild-unplaced` and report `--no-settle`; it does
not settle either lane, capture a new slate, initialize a missing bank or
replace a newer frozen card. Missing state/no plan/zero active contracts gives
an explicit **NO BET**, not a manufactured bankroll. Historical approval is not
authority for another date. Do not choose `official_morning` as a substitute:
it is a heavy fresh run, not lost-history recovery.

## Dated archives and cleanup

Known durable daily families have a 30-calendar-day hot window, then exact-byte
rollover to:

```text
localdata/archive/<family>/<year>/<month>/<original filename>
```

This reduces GitHub directory crowding, **not Git-history size**. The exact
allowlist is `DATED_ARCHIVE_FAMILIES` in `edgefactory.util`; do not recursively
archive unknown evidence. The latest human Main/ENH/ML card stays at root.
State/bank/result ledgers, decisions, resets/reconciliation, special recuts,
monthly source CSVs and warehouses are excluded from this rollover contract.
Existing Git-ignore/external-storage rules still apply: archive support is not
permission to recommit raw data retired by the lean-baseline purge.

Readers use `dated_artifact_path` / `dated_artifact_files` across root and cold
layouts, including historical Git-ref reads at that ref. Different root/cold
bytes are an error, not a choice of whichever seems newer. Publishing copies
and fsyncs before retiring a redundant root source; interrupted/conflicting
copies preserve originals. Restore validates cache archives against both
committed layouts before checkout/clean; cache-only cold evidence survives.

Safe preview (also includes the existing telemetry-deletion preview):

```sh
PYTHONPATH=src python3 scripts/clean_localdata.py --dry-run --today YYYY-MM-DD
```

Do not remove the `--dry-run` just to inspect a plan. A path cited by the
[dated-claims ledger](DATED-CLAIMS.md), a frozen receipt or another retained
provenance chain is not disposable because it looks old. Unknown inventory is
not zero files. Indexed immediate root children—not recursive file count—drive
the 900-entry warning ahead of GitHub's 1,000-child listing limit.

Runtime/storage repair code and manual workflow installation were delivered
through PR244; the installed YAML supersedes the deleted handoff copies.
End-to-end production savings still require an observed normal run; no such
measurement or new dispatch is implied by this documentation cleanup.

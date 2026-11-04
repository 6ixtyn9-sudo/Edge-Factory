# Dated localdata archives

GitHub lists at most 1,000 children per directory. Daily evidence must not be
removed just to fit that browser limit. Known durable daily families now use a
30-calendar-day hot window at `localdata/`, followed by exact-byte rollover to:

```
localdata/archive/<family>/<year>/<month>/<original filename>
```

For example, `picks_morning_2026-09-01.json` becomes
`archive/picks_morning/2026/09/picks_morning_2026-09-01.json`. There is no
compression, JSON reserialization, regenerated prediction or financial adjustment.
Each monthly leaf contains at most 31 daily files per extension; higher levels
are sharded by family and year. The latest Main, ENH and ML human card stays at
the root even if no new card has appeared for more than 30 days.

## Automatic maintenance

The existing `scripts/clean_localdata.py` CLI rolls durable families over before
its existing telemetry-pruning pass. `phase5_persistence.py persist` also rolls
over before staging `localdata`, so rollover does not rely solely on a daily
cleanup run. No workflow changes or additional service are needed.

A safe preview (no files, directories or locks created):

```
PYTHONPATH=src python scripts/clean_localdata.py --dry-run --today YYYY-MM-DD
```

The CLI still previews the existing telemetry deletion policy too. To preview
only rollover, call `archive_dated_artifacts(..., dry_run=True)` in
`edgefactory.util`. Do not run cleanup against production evidence simply to
inspect its plan without `--dry-run`.

## Readers and writers

- `dated_artifact_path(localdata, filename)` resolves an existing archived file,
  otherwise the original root path. New/current outputs retain their old paths.
- `dated_artifact_files(localdata, pattern)` is the root glob plus canonical cold
  files, ordered by original basename and deduplicated across layouts.
- Morning and later pick snapshots remain distinct evidence. No fallback merges
  their bytes or substitutes the later slate for the morning slate.
- Root/archive duplicates must be byte-identical. Different revisions raise an
  error rather than silently selecting one. Do not delete either conflicting
  copy to make a run green; reconcile provenance explicitly.
- Historical Git-ref readers try both layouts **at that ref**, not the current
  working copy. Old commits remain readable without backfilling their history.

GitHub bookmarks to moved paths may require the new path (or the old commit's
history). Root symlinks are deliberately not used: they would retain the same
1,000-entry problem.

## Cache and persistence safety

Archive creation copies and fsyncs before publishing without replacement. Source
and destination hashes are checked before retiring the redundant root copy.
A local maintenance lock serializes rollover calls. Interrupted or conflicting
copies fail without discarding the original evidence.

Restore validates cached archives against both committed archive and legacy root
paths **before** checkout/clean. Cache-only archive files survive clean and remain
persistable; changed duplicates fail closed with both versions preserved. Locks
and temporary files are not committed.

## Deliberate exclusions and future growth

The exact family allowlist is `DATED_ARCHIVE_FAMILIES` in `edgefactory.util`.
Unknown names, state/bank/settled ledgers, decision receipts, reset/reconciliation
files, special recuts, monthly raw source CSVs and warehouse files do not move.
Their existing policies remain in effect. Selection, probability and staking
rules are not changed by this storage layout.

This bounds the managed daily families, not every imaginable future filename.
Persistence warns at 900 root entries so new/unmanaged families and monthly raw
archive growth can be reviewed before GitHub truncates the listing again. New
families must have their readers and cache behaviour checked before joining the
allowlist; do not enable unrestricted recursive archival of unknown evidence.

Relocation reduces directory crowding, **not Git history size**. It is not a
history rewrite or an excuse to delete financial evidence.

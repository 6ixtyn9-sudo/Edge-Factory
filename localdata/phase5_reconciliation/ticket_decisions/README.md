# Background ticket-decision receipts

These are machine-readable audit snapshots, not daily cards or performance reports.
They are deliberately compressed and kept out of the top-level `localdata` listing.

## Storage

- Current: `localdata/phase5_reconciliation/ticket_decisions/<prefix>_<date>_decision.json.gz`
- Legacy, still readable: `localdata/<prefix>_<date>_decision.json`
- Main prefix: `auto_tickets`; ENH prefix: `autobets_enh_tickets`.

Gzip changes the container only. JSON payloads, internal SHA-256 digests, captured
policy, card identities and stakes are unchanged. Frozen receipts remain write-once.
GitHub does not render gzip as a JSON preview; use the ordinary daily text cards
for human-readable decisions. This is organisation/compression, **not privacy or
Git-history deletion**.

## 28 October 2026 migration

| Receipt | Original bytes | Compressed bytes | Reduction |
| --- | ---: | ---: | ---: |
| Main | 4,582,901 | 1,135,171 | 75.23% |
| ENH | 9,899,102 | 2,175,166 | 78.03% |

Both decompressed files were verified byte-for-byte against the originals, with
valid, unchanged internal receipt hashes. Actual replay output before and after
the move was identical apart from the file path. Its overall status remains
**PARTIAL**: storage changes do not establish missing historical evidence.

The existing writer and cache-restore machinery migrate legacy receipts. Restore
compares corresponding Main/ENH/date receipts across both formats; a cached alias
cannot override a committed frozen receipt. A cached freeze may replace a draft
only with the existing independent financial-freeze check. Divergent or invalid
evidence is retained in compressed `*_decision_cache_conflict*.json.gz` files and
makes parity fail. Superseded drafts may be archived separately. Receipts never
authorize financial-state restoration.

This directory already falls within the workflow's cache, Git-clean exclusions,
Git tracking rules and `EdgeFactory-Reports` artifact path
(`localdata/phase5_reconciliation/**`). No workflow/YAML changes are required.
Legacy root receipts are ignored to prevent publishing large JSON copies again.

Validation: full Python suite **4,763 passed, 1 skipped**; focused writer, replay,
freeze-lock, ENH and persistence tests **219 passed**. Coverage includes legacy
read/migration, gzip corruption, atomic-write failure, identical/conflicting
format aliases, both cache/HEAD format directions, freeze authority and artifact
coverage. No betting-policy, financial-record or workflow-dispatch changes.

## Unpublished frozen run 40647275279

That run saved `localdata-v2-40647275279` before its Git publication failed
against the receipt relocation. The existing workflow already restores the
newest `localdata-v2-` cache. No artifact download, new script or YAML edit is
needed. Recovery is **pending**, not a claim that those files reached Git.

The committed lane states carry a one-shot `integrity_recovery.pending_cached_freeze`
approval: 28 October only, source run/checkout, original freeze minute and exact
logged card. This HEAD approval—not a cached approval or receipt—is authority
to restore that unpublished freeze. Restore requires unchanged reviewed bank,
ledger, other positions and other locks; the original 25%-free-bank stakes;
and a matching hash-valid frozen receipt with that run/checkout provenance.
It keeps the saved text card byte-for-byte and losslessly compacts the receipt.
Both lanes validate before checkout/clean. Missing/stale cache or any mismatch
stops restoration rather than rebuilding the cards. A recovered approval records
the receipt/financial hashes; subsequent committed freezes retain normal protection.

After the patch is merged, the operator can start a **normal run from updated
main** using the existing workflow. Do **not** select `recover_and_rebuild` for
this: that separate mode invalidates an approved unplaced ENH ticket. No workflow
has been dispatched as part of this patch, and no bank/history values have been
edited. The queued recovery still needs to run and publish successfully.

Freeze locks deliberately record whole seconds, whereas decision contexts may
retain microseconds. Restore and replay now compare aware instants at that lock's
precision, never across different seconds. This fixes a reproducible mismatch;
it does **not** establish the cause of this run's uninspected parity failure or
turn historical PARTIAL evidence into a PASS.

Recovery validation: **4,797 passed, 1 skipped** overall; persistence/replay
**169 passed**, including absent cache, unknown cached approval/stakes, changed
history/bank/card, wrong source, receipt corruption, legacy locks, cross-lane
atomic validation, lossless old-layout recovery and idempotent committed restore.

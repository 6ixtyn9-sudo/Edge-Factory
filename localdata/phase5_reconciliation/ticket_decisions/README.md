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

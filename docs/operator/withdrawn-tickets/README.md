# Withdrawn, unplaced ENH ticket — 20 October 2026

**Historical evidence, not an active recommendation or a new reset approval.**
The operator confirmed none of these bets were placed, then approved withdrawing
that day's enhancement ticket. This was a narrow exception to the write-once
recommendation lock, not a settlement undo.

- `2026-10-20-enh.txt` is the original frozen card, retained byte-for-byte and
  **WITHDRAWN**. The two `performance-before-reset` files are the original reports.
- `localdata/autobets_enh_tickets_2026-10-20_reset.json` records approval time,
  confirmation, artifact hash and audit path.
- The receipt removes only pre-approval unplaced commitments and same-day
  freeze/supersession locks before settlement, retaining the old entries and
  metadata in an audit acknowledgement. Main and booked history/bank/base/
  cycle/events are not reset.
- Repeated application is idempotent. A newer frozen replacement is never
  cleared; settled history, unknown artifacts, malformed approvals and unexpected
  recuts fail closed for explicit review.

The old proposed workflow and its deployment instructions are superseded.
Use [Recovery](../RECOVERY.md#prediction-history-recovery) and the installed
workflow for the existing guarded path; do not infer approval for another date,
new provider capture, another replacement or a bank reset from this receipt.

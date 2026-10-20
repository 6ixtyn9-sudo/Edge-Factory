# Withdrawn, unplaced enhancement ticket — 20 October 2026

The operator explicitly confirmed **none of these bets were placed**, then
approved withdrawing today's enhancement ticket and starting over. This is a
narrow exception to the write-once recommendation lock, not a settlement undo.

- `2026-10-20-enh.txt` is the original frozen artifact, retained byte-for-byte
  for audit. **WITHDRAWN: not an active recommendation.**
- The two `performance-before-reset` files retain the original report.
- `localdata/autobets_enh_tickets_2026-10-20_reset.json` records confirmation,
  approval time, artifact hash and audit path.
- The active ticket file is deleted. The enhancement performance report removes
  only the unplaced open commitment: bank/base/cycle/history/events/settled
  results are unchanged. It now shows zero open slips and zero held accas.
- At enhancement state load (including grading), the committed receipt removes
  only pre-approval unplaced entries and same-day freeze/supersession locks
  **before settlement**. Old entries and freeze metadata are retained inside a
  runtime audit acknowledgement. No main-lane state is touched.
- A replayed stale cache gets the same reset. An acknowledged reset or a
  replacement frozen strictly after approval is never cleared again.
- Already-settled history, unknown active artifacts, malformed approvals and
  unexpected force-recut artifacts fail closed for explicit review. There is
  no automatic history deletion, performance rebase or bank reset.

The companion full daily workflow supplied to the operator adds an
`enhancement_reset` mode invoking only
`auto_tickets.py --enhancements --apply-unplaced-resets`. It does NOT capture,
settle, mine, price, build/freeze, notify, grade, persist pipeline state or
publish another potentially degraded prediction cache. Reports/artifacts remain
available. Cached runtime-state acknowledgement is intentionally repeatable via
this durable receipt until a normal run saves the corrected state.

The local receipt-application command completed without capture or settlement.
Remote cached-state execution is not claimed until a workflow run is observed.
GitHub rejected workflow-file publication because the Arena GitHub App lacks
workflows permission; the companion YAML must be applied manually. The normal
existing enhancement entry point already applies the receipt on its next load.

No replacement ticket is endorsed: post-Forebet history recovery/activation is
still pending. Resetting a recommendation cannot supply missing evidence.

Validation: 143 focused tests passed (8.86s), including 14 new reset cases;
full suite **3,430 passed, 1 skipped, 1 pre-existing failure, 151.58s**. The sole
failure is the previously documented missing league-alias target in the persisted
purity registry, not a reset regression. No test disabled. Main ticket/state diff
is empty; main state Git blob remains `9de29f237df8a33b35b9569c5c595ceb849c601c`.

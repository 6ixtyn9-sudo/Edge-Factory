# Notification repairs — run 38027657811

The run sent quarantined SOURCE_FALLBACK rows (Ansbach–Nürnberg II and
Vilzing–Buchbach) as pushable and attempted an oversized Telegram shadow slate.

## Changes
- Bet-alert selection now excludes explicit price_push_eligible=False,
  non-executable evidence classes, and nonempty quarantine reasons other than
  `none`. Both official formatters independently enforce the same predicate.
- Legacy rows without price receipts retain existing bucket behaviour; this
  repair does not certify them or repair consensus-label contracts.
- Telegram shadow messages pack complete cards into <=3800 UTF-16 units,
  repeating research and bucket context. No max-lines truncation. Oversized
  single cards use bounded, explicitly research-only continuation messages.
- Existing all-success dedupe barrier remains: partial failure writes no
  shadow ledger. A retry may repeat already-delivered chunks, but cannot
  silently mark undelivered selections as sent.

## Verification
60 notification controls passed before adding successful-recovery assertions;
29 focused controls then passed including those assertions. Full suite:
2627 passed, six preserved consensus-contract failures, 66.86s. No skips,
xfails, changed consensus gates, operational archive edits or live sends.
Regression controls cover both logged fallback fixtures, unchanged input file,
filtered bet-alert ledger, 200-card Unicode payload, oversized single card,
partial delivery failure and successful complete recovery.

Scope: does not change tickets, price matching, models, workflows, or API
access. Does not yet generalize Telegram chunking to oversized official or
discovery messages. Does not make the unfinished audit recorder production-ready.

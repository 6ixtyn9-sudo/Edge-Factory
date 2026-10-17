# Bank history: snapshot, close, and the rebuild (2026-10-16)

## What the history rows mean

Each bet-day row in `auto_tickets_state.json` (main lane) and the enhancement
state (enh lane) carries two bank figures.

- `bank_pct` is a **settlement snapshot**: the live bank at the moment an acca
  on that day settled. It is not an end-of-day close. Live `bank` moves only
  when an acca settles, and open stakes are held separately as committed
  (`effective_bank` = bank − committed).
- `close_pct` (from 2026-10-16) is the previous bet-day's close plus this day's
  net P&L. It is chained only within the writer's own view of the history.

**Correction to the earlier note.** `close_pct` was described as independent of
settlement order. That holds only for a single day's own accas. If an earlier
day's acca settles after a later day has been written, the live bank moves, but
the later row's `close_pct` is not recalculated. The grader therefore does not
rely on `close_pct` (see below).

Rows written before 2026-10-16 have no `close_pct`.

## What the report does now

`scripts/auto_tickets_grade.py` shows the stored values and does not recompute
the bank. Each bet-day line carries its stored close, and the `NOTES` block at
the foot of the report points here for the history.

The rebuild-from-base comparison (the `SNAPSHOT NOTES` block and the `~ stored
close` markers) was removed from the report on 17 Oct. It was a recomputation,
and it put the audit detail in front of the performance view. The breaks it
found are still described in this document, and the stored rows are unchanged.

The earlier "bank break" flag compared neighbouring list entries, so it
mislabelled late settlements and out-of-order rows. It is also removed.

The rebuilt chain matched the live bank (192.30 on 16 Oct) to rounding, so the
report's total is consistent with the live balance.

## The 13 Oct row (corrected 2026-10-16)

The 13 Oct `bank_pct` was 172.4802: the bank after the 13 Oct acca #2 settled on
15 Oct, which came after the 14 Oct acca #1 loss (18.8847). It is now 191.3649,
the rebuilt close, with the original kept as `bank_pct_before_correction`.

## What the other snapshot offsets are

Checked read-only against the state history:

| Days (stored − rebuild) | Offset | Cause |
|---|---|---|
| 11–22 Sep | +15.6111 | 10 Sep acca, stake 15.6111, open until it lost on 23 Sep |
| 28 Sep–1 Oct | +15.5364 | 27 Sep acca, stake 15.5364, open until it lost on 2 Oct |
| 27 Sep | +6.13 | Not explained by one open stake. Not investigated further. |
| 27–31 Aug | −6 to +5 | Three 27 Aug accas (50.0001 staked) open for days. Rows for 27 and 29 Aug were appended on 1 Sep. Converges by 1 Sep. Not reconciled day by day. |
| 10 Sep | −0.18 | Small residual. Not investigated. |

The two exact matches are the amounts a late settlement moves the bank. The
live bank was correct at every point; only the stored snapshots for the days in
between differ.

## What was not changed

- No history row was edited, except the 13 Oct correction above.
- The residuals on 27 Sep, 10 Sep and in 27–31 Aug remain. They are shown in the
  report and are not corrected.
- The enh lane's report was not regenerated (no enh state in the workspace).
- No pipeline run was triggered and no settlement was executed. The text report
  was rendered from the tracked state with `render_lines`.

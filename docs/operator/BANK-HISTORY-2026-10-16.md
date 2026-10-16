# Bank history: snapshot vs close (2026-10-16)

## What the history rows mean

Each bet-day row in `auto_tickets_state.json` (main lane) and the enhancement
state (enh lane) carries two bank figures.

- `bank_pct` is a **settlement snapshot**: the live bank at the moment the
  last acca on that day was written. It is not an end-of-day close.
- `close_pct` (new, from 2026-10-16) is the **end-of-day close**: the previous
  bet-day's close plus this day's net P&L (returned minus staked, over every
  acca on the day). It is chained, so it does not depend on the order in which
  accas settle.

Rows written before 2026-10-16 have no `close_pct`. For those rows the close is
`bank_pct`, which is how the report and the grader already read them.

## Why the 13 Oct row reads 172.48

The 13 Oct accas settled in two runs, and a 14 Oct acca settled between them:

| Step | Bank after step |
|---|---|
| 12 Oct close | 201.44 |
| 13 Oct acca #1 lost (stake 25.18) | 176.26 |
| 14 Oct acca #1 lost (stake 18.88) | 157.37 |
| 13 Oct acca #2 won (returned 40.29, stake 25.18) | 172.48 |

The stored 13 Oct `bank_pct` is 172.48, the bank after the 13 Oct acca #2
settlement. That includes the 14 Oct loss, which settled first. The chained
13 Oct close is 201.44 − 50.36 + 40.29 = **191.36**. The gap of 18.88 is the
14 Oct acca #1 stake.

The 14 Oct row (188.53) is correct. The current bank (192.30 on 15 Oct) is also
correct. Nothing in the live bank arithmetic was wrong.

## What changed

- `scripts/auto_tickets.py`: `_record_acca_settlement` and the backfill path
  write `close_pct` on every bet-day row. `bank_pct` is unchanged.
- `scripts/auto_tickets_grade.py`: the bet-day report and the bank-break check
  read the close through `_close()`, which uses `close_pct` when present and
  falls back to `bank_pct` otherwise.
- Tests: `test_day_close_does_not_depend_on_settlement_order` replays the
  13/14 Oct settlement order; `test_legacy_rows_without_close_pct_still_report_the_break`
  checks the fallback.

## What was not changed

- The stored 13 Oct row (`bank_pct` 172.48) is **not edited**. Correcting it
  would be a history edit and needs a separate approval. The grader still flags
  the 13 Oct and 14 Oct breaks in the existing report; the flags are accurate
  for the stored snapshot values.
- The 14 Oct row has no `close_pct`. If a new settlement is ever written to
  14 Oct, its chain starts from the 13 Oct stored snapshot. Before any such
  write, the 13 Oct row needs correcting (see above), or the close for 14 Oct
  would inherit the 18.88 gap.
- No state files were regenerated, and no pipeline run was triggered.

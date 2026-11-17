# Settlement and bank interpretation

[Operator handbook](README.md) · [Recovery](RECOVERY.md) · [Evidence](DATED-CLAIMS.md)

## Regulation-only results

FT markets settle on **90 minutes plus stoppage time**, never an after-extra-time
or penalty-shootout aggregate. Preserve source period metadata through parsing,
warehouse, overlays and exports. A consistent replay of a bad result does not
make the underlying score valid.

- Explicit regulation pairs can resolve AET/PEN fixtures. Known aggregate-only,
  malformed/partial pairs and inappropriate live/terminal scores stay held.
- Do not use a simplistic minute>90 cutoff or subtract guessed extra-time goals;
  stoppage time is still regulation.
- Keep oriented date/club/squad identity exact. A senior, women's, youth, reserve
  or simulated/SRL fixture is not interchangeable with another squad.
- Cross-donor/overlay holds prevent a known AET aggregate returning through a
  metadata-free or higher-priority copy. Missing old period metadata is not
  positive proof of regulation. A known unresolved regulation hold must not
  turn into an age-based void.
- Add independently reviewed facts through the existing configuration/review
  path; do not import vendor win/loss grades or invent missing observations.
  Historical labels apply only to observed same-squad fixtures in the bounded
  window, respecting any review-time bound.

Existing verified regrading can book a **specifically reviewed correction**
through the established Main/ENH grading/persistence paths: affected leg/payout,
subsequent close/bank, atomicity and idempotence are checked. This is not general
permission to reconstruct finance. Cache reconciliation trusts HEAD-committed
verified facts, not cached approvals; unrelated bank/stake/frozen changes still
fail closed. An audit-only repair of a missing leg result must **not** rebook an
already settled accumulator or alter bank/stakes.

### Dated example, not current balances

For Mensajero–Las Palmas, **27 October 2026**, reviewed regulation was **1–1**;
**1–3** included extra time. Regulation match-over-2.5 therefore lost. The
original settlement report pinned its dry-run states to
`b6c52d7c67fd1037c623b7d14abb877e62411dd8` and projected these accounting units:

| Lane | Historical recorded bank | Historical projected bank | Incorrect payout removed |
|---|---:|---:|---:|
| Main | 358.466335 | 283.0761 | 75.3902 |
| ENH | 40.348665 | 29.8879 | 10.4608 |

These are **historical temporary-copy dry runs**, not today's banks, bookmaker
cash stakes or proof that a production run booked the correction. The original
[pinned reconciliation](https://github.com/6ixtyn9-sudo/Edge-Factory/blob/30e9372aab33e1e9444c1f5fd3b916df91ca7f0e/docs/operator/REGULATION-SETTLEMENT-2026-10-28.md)
contains the state blobs and scope. Verify actual durable state and
`regrade_verified` / `regrade_verified_bank` logs, preserved unrelated history,
expected delta and a no-op second pass before claiming deployment.

## Bank history: snapshot versus close

Main state is `auto_tickets_state.json`; ENH state is
`enhancement_tickets_state.json`. Stored performance reports describe those
lanes separately. Never initialize a missing bank from a README example or
replace current finance with an old artifact.

- `bank` moves on settlement. Open stakes are separate commitments;
  **effective/free bank = bank − committed**.
- History `bank_pct` is a **settlement snapshot**, not an end-of-day close.
  A later-dated bet can settle before an earlier one.
- `close_pct` (introduced 16 October 2026) chains the writer's previous bet-day
  close plus that day's net P&L. Earlier late settlements do not automatically
  recalculate rows already written; it is not globally settlement-order invariant.
  Older rows can lack it entirely.
- `auto_tickets_grade.py` displays the stored values, not a new bank reconstructed
  from base. Removed “bank break” comparisons of neighboring list entries were
  misleading for late/out-of-order settlements; do not reintroduce them as truth.

### Historical snapshot offsets (16 October review)

The one documented manual history correction was the **13 October** snapshot:
172.4802 → 191.3649, preserving the original in
`bank_pct_before_correction`. That is a dated audit fact, not an instruction to
reapply it to current state.

| Historical range | Stored − rebuilt comparison | Interpretation at that review |
|---|---:|---|
| 11–22 September | +15.6111 | 10 September stake remained open until its 23 September loss. |
| 28 September–1 October | +15.5364 | 27 September stake remained open until its 2 October loss. |
| 27 September | +6.13 | Unexplained residual; not reconciled. |
| 27–31 August | roughly −6 to +5 | Late settlements/out-of-order rows; not reconciled day by day. |
| 10 September | −0.18 | Small residual; not investigated. |

Those residuals were **not corrected**. Do not turn an explanatory reconstruction
into replacement booked history. The original
[bank-history report](https://github.com/6ixtyn9-sudo/Edge-Factory/blob/30e9372aab33e1e9444c1f5fd3b916df91ca7f0e/docs/operator/BANK-HISTORY-2026-10-16.md)
is recoverable from Git; its 16 October total is not a live balance.

## Unplaced withdrawals are narrow exceptions

The [20 October unplaced ENH withdrawal](withdrawn-tickets/README.md) retains its
original card, pre-reset reports and approval receipt. The operator confirmed
none were placed. Only the named unplaced commitment/locks were removable;
settled history, bank/base/cycle/events and Main stayed protected. A newer frozen
replacement, unknown artifact, malformed approval or settled history fails closed.
Never generalize that approval into a settlement undo or a bank reset.

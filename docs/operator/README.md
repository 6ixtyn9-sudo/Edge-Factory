# Operator handbook

[Project/setup](../../README.md) · [Sources](SOURCES.md) ·
[Recovery](RECOVERY.md) · [Research](RESEARCH.md) · [Settlement](SETTLEMENT.md) ·
[Evidence](DATED-CLAIMS.md)

This is the operating entry point. Source code and the
[installed daily workflow](../../.github/workflows/daily.yml) determine the
actual settings; old run receipts describe their own snapshots, not today's
health, banks or permissions. No guide authorizes a merge or a production run.

## Daily card ops

All card times are **Africa/Johannesburg (SAST, UTC+2)**. Building opens at
06:00; the first qualifying run at/after **09:00** freezes that date. A late
runner is still late: these hours are not a guarantee that a card exists.

| State | Meaning / action |
|---|---|
| `NOT YET` / `DRAFT` | Not final. Do not place it. |
| `FROZEN AT HH:MM - FINAL` | Human final marker, backed by immutable state/decision evidence. |
| Frozen rerun | Reprints the saved recommendation; must not rotate the placed card. |
| `NO BET` / insufficient quorum or eligible legs | Valid abstention. Do not loosen gates to manufacture a card. |
| Missing card or inconsistent freeze artifacts | Not permission to bet; inspect the run and recovery evidence. |

Main and ENH are separate lanes with separate state. `autobets_ML` is a
**PAPER** lane, not authority to place a real-money bet. Morning and later
pick snapshots are distinct evidence; never substitute an intraday slate for
the original morning decision.

A frozen date's `frozen_by_date` entry and timestamp are write-once, co-located
with state persistence. Legacy `.frozen` sidecars still lock their date and are
not disposable. **`--force` is not permission to rewrite a lock, frozen receipt,
placed slip, bank or stake.** A different card for an already frozen date is an
incident. Any unplaced replacement needs its own explicit approval and durable
receipt; a historical reset approval does not extend to another date.

### Current selection/staking boundaries

Implementation: `scripts/auto_tickets.py` and its shared recipe/price gates.
These are descriptions of the armed policy, not new tuning instructions:

- Minimum leg odds **1.25** in both real-money lanes; existing upper-odds,
  kickoff, fixture-reuse, context-veto and quote-admission checks still apply.
- Main uses probability-ranked doubles without add-ons or a new probability
  floor. Normally at most two accas; saturation can increase this to five
  after the existing pool/drop checks. ENH retains at most three doubles,
  cohort ordering and stored model probability **at least 60%**.
- Existing total deployment remains **25% of free bank**, not 25% per acca.
  A proposed reduction is subject to the existing manual 15-graded-bet-day
  review, not an automatic ratchet. Never resize a previously booked stake.
- A failed dependency, empty qualified pool or no valid pair means abstain.
  A larger unpriced slate is not executable price coverage.

The policy decision and its limited retrospective basis are preserved in
[the diagnostic, §§21–23](../edge_loss_diagnostic_2026-11-15.md).
Do not present that searched comparison as untouched forward validation.

## Run modes and side effects

The installed workflow exposes these modes. It is **dispatch-based**: the YAML
has no cron schedule. External scheduling is separate; the workflow name alone
does not prove a three-hour trigger is configured or healthy.

| Mode | Intended use / boundary |
|---|---|
| `auto` | One smart schedule iteration (`daily.py --auto-once`); can capture, settle, mine/activate, publish and notify. |
| `official_morning` | Explicit full official pass (`daily.py --force-repick`); heavy and stateful, not a history-recovery shortcut. |
| `forecast_refresh` | Forecast path, not a replacement for today's frozen ticket. Read its real run outputs. |
| `clv_only` | Existing CLV path; may still spend provider quota. |
| `remine_only` | Restored-cache warehouse + research miner; no `--activate`, source capture, new tickets, notifications, cache save or Git-state publication. Reports can still be uploaded. |
| `recover_and_rebuild` | Narrow approved historical recovery/unplaced rebuild. **Not a general rerun.** Read [Recovery](RECOVERY.md#prediction-history-recovery) first. |

Do not dispatch a mode without operator authorization. Do not use a full daily
run as a probe. Local equivalents are equally stateful:

```sh
# Only for an authorized normal operational run:
PYTHONPATH=src python3 scripts/daily.py --auto-once

# Research-only miner, on prepared local inputs (writes a research report):
PYTHONPATH=src python3 scripts/mine_consensus.py
```

No saved command here implies that it was run. Provider budgets, secrets and
source permission still apply; adding a secret does not necessarily expose it
to a job. Consult the installed workflow, not a copied proposal.

## Source-health legend

Read the dated `source_health` receipt and the active `PRICE POLICY:` line.
Health is role-specific: prediction fetch/vote, price fetch/join/admission and
shadow capture are different capabilities.

| Signal | Interpretation / action |
|---|---|
| `committed` | Bytes exist in the repository; not automatically eligible or certified. |
| `cache-only` | Runtime bytes need the matching cache/artifact; a cold clone is incomplete. |
| `absent`, stale, missing shard | Missing evidence, not zero performance or permission to regenerate a forecast. |
| `alias/cache` / convergent | Not another independent vote or bookmaker family. |
| `403`, auth/plan denial | Stop/escalate configuration or permission; do not retry harder. |
| `429`, `Retry-After`, challenge/freeze | Respect backoff/freeze. No bypass or alternate-transport escalation. |
| Raw/scored rows > 0, matched/admitted = 0 | Board exists but joins or policy reject it. Inspect reason counts; never loosen identity to inflate coverage. |
| `not_run`, incomplete, unknown | Not a successful empty slate. |

Named bookmaker, average and fair prices must remain visibly different.
See [Sources](SOURCES.md) for quote roles, independent schedule witnesses,
collection bounds and the policy switches; older “primary/fallback” labels
are not authority.

## Verify a run

1. Confirm the actual checkout, mode and attempt. Queued jobs resolve the
   requested branch when they start; an earlier run may already have newer state.
2. Read source health, history-completeness and financial conflict diagnostics.
   Check the actual frozen slip and decision receipt, not just an annotation.
3. Check **both** cache and Git persistence outcomes. A runner-local summary or
   uploaded report is not proof that financial state was published.
4. Reports/cache/Git are persisted before the final non-gating replay diagnostic.
   That ordering protects saved state from a later audit timeout, not from a
   kill before the durability barrier.
5. Inspect the dedicated current-run replay report. `INCOMPLETE_TIME_BUDGET`,
   `INCOMPLETE_INTERRUPTED`, missing or stale output are **not MATCH**. A green
   overall job is neither full-history parity nor betting-performance evidence.
6. Read stored bank/performance reports using [Settlement](SETTLEMENT.md).
   Do not replace current finance with a historical example or report-derived
   reconstruction.

Missing/corrupt evidence, conflicting finance or an unexpected frozen card:
preserve both copies and stop the affected action. Follow [Recovery](RECOVERY.md),
not blanket cache deletion, `git checkout -- localdata/`, a bank reset or a
weakened guard. Automated tests belong in temporary roots; harness probes belong
in the existing `scripts/replay_harness.py`.

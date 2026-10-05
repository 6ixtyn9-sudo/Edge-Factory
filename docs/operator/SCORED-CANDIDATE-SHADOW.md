# Scored-candidate shadow grading ledger (audit-only)

Answers, from persisted data: **were scored-but-dropped candidates genuinely
bad inventory, or bread left on the table?** — separately for execution-safe
rejected candidates and by rejection reason.

This instrument is **observability only**. It changes nothing about ticket
selection, staking, acca construction, odds floors, veto bands, ladder logic,
source eligibility, kickoff guards, freeze/write-once behaviour, matching, or
the customer-facing card. Parity is pinned by tests
(`tests/test_scored_candidate_shadow_tickets.py`): the printed card, selected
legs, stakes and state are byte-identical with the ledger enabled, disabled
(`EDGE_FACTORY_SCORED_SHADOW=0`), and even when every ledger write crashes.
An audit write failure is reported on stderr
(`scored-candidate shadow ... audit-only`) and otherwise ignored.

## Where the scored universe is captured

Two append-only capture points, both before final selection:

1. **Picks build** (`scripts/picks_today.py`, per-day loop, right after the
   operational collapse and before the day archive write): every emitted
   scored candidate row for the day — including rows the bucket-assignment
   loop drops (`bucket_pick` returns `None`: CAUTION under
   `CAUTION_MIN_ODDS` → recorded as `odds_floor`, drop stage
   `bucket_assignment`) and rows removed by the operational duplicate
   collapse (`duplicate_fixture`, drop stage `operational_collapse`).
2. **Ticket build** (`scripts/auto_tickets.py` `cmd_today`): the target-day
   slate is persisted again (stage `ticket_build`) immediately BEFORE
   `playable_legs`/guards/ladder run, and final selected/rejected status is
   appended at every terminal branch (draft, frozen, frozen reprint, no-bet
   minimum-legs, no-bet empty-plan, superseded).

### "scored=N" reconciliation — one definition, stated explicitly

The pipeline log `coverage: scored=N picks=M` uses `ml_scored_day or n_up`,
a **fixture-level** count (ML-model-scored fixtures, falling back to upcoming
fixtures with >=2 sources). Fixtures scored without an emitted candidate row
carry no market/selection/price and cannot be graded. The shadow ledger
persists the **candidate-level** scored universe (one record per
fixture/market/selection/rule). Both numbers are persisted in the
`run_summary` event and the report prints both plus the explanation — the
reconciliation is explicit, never faked.

## Files and schema (schema_version=1)

```
localdata/scored_candidate_shadow_YYYY-MM-DD.jsonl              # scored + status + run_summary events
localdata/scored_candidate_shadow_settlement_YYYY-MM-DD.jsonl   # only via --write-settlement (append-only)
```

Both stay **gitignored** with the rest of `localdata/` (shadow ledgers are
deliberately not committed). Events are routed to the file of the
candidate's own trading date.

* `scored_candidate` — identity (`candidate_id` = sha256 over trading date,
  accent-folded team keys, league key, market, selection, rule), fixture and
  normalized teams, league/country/kickoff, rule/bucket/score/probability,
  captured price evidence (`captured_odds`, `captured_price_source`,
  `captured_bookmaker`, `price_evidence`, `price_odds_kind`,
  `price_push_eligible`, quarantine), source registration flags, and the
  execution-safety verdict (`execution_safe_named_book_eligible`,
  `execution_safe_reason`, `price_valid_pre_kickoff`), plus
  `run_id`/`workflow_run_id`/`git_sha` when available.
* `candidate_status` — `selected_as_pick`, `selected_on_ticket`,
  `final_ticket_status` (`draft`/`frozen`/`no_bet`/`not_selected`/
  `superseded_no_bet`/`pending_ticket_build`), `rejection_reasons`
  (list — multiple reasons are preserved), `drop_stage`, `acca_id`,
  `acca_leg_index`, stake fractions and the price/bookmaker used when
  selected. Reasons are derived from real state: the live gate predicate
  (`playable_leg_rejection` — the same single source of truth the card
  uses), the staged policy decisions (kickoff guard, tripwires, slice
  ladder), and the branch-level terminal rule. When nothing is derivable the
  explicit `rejection_reason_unknown` marker is recorded and counted.
* `run_summary` — per-run counters incl. `pipeline_scored_log`,
  `shadow_scored`, `card_status` and the scored-definition text.

## Execution-safety (price honesty)

A candidate is execution-safe only when the decision-time captured price was:
registered source AND execution-eligible AND **named bookmaker** AND not
quarantined (`alias_fuzzy` stays quarantined) AND push-eligible AND provably
**pre-kickoff** (capture instant < `kickoff_utc`, both timezone-aware; an
unprovable ordering fails closed as `pre_kickoff_unproven`). Bet Better fair
prices (fair_stakeable=off), Boggio average-donor prices, unregistered
sources and post-kickoff captures are recorded but excluded from
execution-safe ROI. No later/closing prices are ever fetched to backfill.

## Settlement and report (read-only)

```
PYTHONPATH=src python3 scripts/scored_candidate_shadow_report.py --date YYYY-MM-DD
    [--all-runs] [--json out.json] [--write-settlement]
```

* Settlement facts: the same donors the ticket grader uses
  (warehouse + `settled_results.json` + operator-verified scores), but the
  join is **exact normalized fixture matching only** — no fuzzy matching, no
  alias index, no reschedule window, no kickoff-tolerance change. Only
  1x2 home/away/draw can settle; anything else is `unmatched`. Missing
  results stay `pending`. Neither is ever a loss; both are excluded from
  every ROI denominator.
* Flat-stake convention: win = odds-1, loss = -1, void/push = 0 (voids stay
  in the settled denominator at zero), pending/unmatched/no-usable-price
  excluded.
* Draft/freeze dedupe: candidates dedupe by `candidate_id`; statuses come
  from the latest frozen/superseded ticket run when one exists, else the
  latest draft run (report prints `snapshot_used=draft`), else the
  picks-build status. `--all-runs` prints per-run diagnostics. The report
  always prints which run it used.
* Report sections: headline counts (total scored, promoted, ticketed,
  promoted-not-ticketed, scored-not-promoted, execution-safe scored/rejected,
  pending, unmatched, no-execution-safe-price, unknown-reason,
  win/loss/void), ROI for ticketed legs / promoted-not-ticketed / all scored
  / all rejected / execution-safe rejected only, and groupings by rejection
  reason (incl. execution-safe-only), bucket, rule, league, market, price
  source, bookmaker, selected-vs-rejected, execution-safe-vs-not, plus the
  reconciliation block.

## Known limitations

* `rejection_reason_unknown` appears when a candidate has a scored event but
  no status event (e.g. the ticket builder never ran for that date); the
  count is surfaced in the report headline.
* Candidates without an execution-safe price are graded only informationally
  (at their captured donor price in the "all scored" lines) and never enter
  the execution-safe lines; candidates with no captured price at all are
  excluded from every ROI denominator (`no_price`).
* Unmatched settlements: non-1x2 markets and fixtures without an exact
  normalized result row do not settle here (the shadow settler deliberately
  omits the live grader's curated-alias and ±3-day reschedule fallbacks —
  fail-closed, so some fixtures the slip grader resolves stay
  pending/unmatched in this report).
* Fixture-level `scored=` log values cannot equal candidate-level
  `shadow_scored` by construction; both are persisted and printed.
* The ledger only begins at deployment; earlier dates have no shadow data.

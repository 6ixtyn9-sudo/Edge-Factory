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

Three append-only capture points, all before final selection:

0. **Fixture level — the `coverage: scored=N` universe itself**
   (`scripts/picks_today.py` `eval_1x2`, via an optional `fixture_audit`
   list threaded through `run_day`): one audit entry is appended at the
   EXACT sources of the pipeline counter — at the `n_up` key-union build
   (`upcoming_fixture`) and at the ML-inference increment that drives
   `ml_scored_day` (`ml_scored_fixture`, 1:1 with
   `research_collector.scored`). `record_picks_build` persists one
   `scored_fixture` event per entry of the effective universe (ML entries
   when any exist, else upcoming entries — mirroring the pipeline's own
   `ml_scored_day or n_up` expression). A fixture the pipeline scored but
   never materialized into a candidate therefore still has a durable
   record (`candidate_materialized=false`,
   `not_materialized_reason="no_candidate_emitted"`). ML-scored entries
   additionally carry the scorer's own **betting intent** (market `1x2`,
   majority side, selection team) and the **side odds visible to the
   scorer at the inference instant** — the same source odds columns the
   `pick_odds` feature reads, scanned deterministically
   (forebet→zulubet→statarea→bzzoiro→vitibet) WITHOUT the 1.50 feature
   default (a feature fallback is not a price). Nothing is fetched for
   this purpose; `shadow_price_captured_at_utc` is the scoring instant and
   `shadow_price_as_of_basis="fetched_this_run"` records that the rows
   were scraped in the same run.
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

### "scored=N" reconciliation — exact, flagged, never relabeled

The pipeline log `coverage: scored=N picks=M` uses `ml_scored_day or n_up`,
a **fixture-level** count. The ledger now persists that exact universe as
`scored_fixture` events (capture point 0 above), so the report reconciles
strictly:

```
pipeline_scored                = N   (from the coverage log)
shadow_scored_fixture_records  = N   (one event per counter increment)
reconciliation_ok              = true, else missing_count printed + MISMATCH flag
materialized candidates        = M   (on K fixtures)
promoted picks                 = P
ticketed legs                  = T
scored but not promoted        = N_unique − promoted fixtures
```

If the counts differ the report prints `missing_count` and a loud
`RECONCILIATION MISMATCH` note; it never relabels the post-collapse
candidate layer as the full scored universe. Ledgers written before
fixture-level capture existed (or ticket-layer-only ledgers) get an
explicit `RECONCILIATION UNAVAILABLE` note instead. Fixtures that never
materialized into a candidate carry **no decision-time price**: they are
counted (`dropped before materialization`) and are excluded from
execution-safe ROI by construction — stated, not hidden. `scored_fixture`
Fixture identity (`fixture_id`) hashes trading date + normalized team pair
only — league is deliberately excluded because source league spellings
differ, and candidates carry the same `fixture_id` for exact joins.

### Two ROI classes — never mixed

1. **`execution_safe_roi`** — unchanged, strict: named-book, registered
   source, execution-eligible, pre-kickoff PROVEN by aware instants,
   push-eligible, not quarantined. Candidate level only. Shadow prices can
   never enter it (`shadow_price_execution_safe` is hard-coded False).
2. **`captured_price_shadow_roi`** — AUDIT-ONLY — NOT STAKEABLE. Grades
   the full fixture-level scored universe flat-stake at the odds the
   scorer itself saw: stale, cached, unregistered-source, donor-average
   prices are allowed **and labelled** (`shadow_price_kind` ∈ named_book /
   cached_named_book / stale_named_book / unregistered_source /
   donor_average / fair_model / unknown). Fair/model prices live ONLY in
   the separately labelled `fair_model_only_audit` line — never in the
   main captured-price lines, never execution-safe.

Gradeability verdict (fail-closed order, reason persisted per record):
`no_selection_intent_available` → `no_captured_price` →
`price_timestamp_unknown` → `post_kickoff_price` → gradeable. Stale label:
`shadow_price_stale=true` when the price's own as-of stamp is more than
`SHADOW_PRICE_FRESH_MAX_AGE_S` (1h) older than the capture instant; prices
fetched within the scoring run are fresh by construction. Pre-kickoff
proof basis is persisted (`instants_proven` / `scored_as_upcoming_unproven`
/ `post_kickoff_proven`): provable post-kickoff prices are excluded; naive
source kickoff strings make exact proof impossible for same-day fixtures,
so those are graded on the scored-as-upcoming basis with the basis both
persisted and reported — mirroring the existing policy that grades
candidates with unprovable kickoffs informationally while keeping them
out of execution-safe ROI. Settlement of fixture intent reuses the exact
`settle_candidate` matcher (no fuzz, no tolerance change); pending and
unmatched are never losses.

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
  `run_id`/`workflow_run_id`/`git_sha` when available. Also carries
  `fixture_id` (sha256 over trading date + width-24 team keys, no league)
  for exact joins against `scored_fixture` events.
* `scored_fixture` — one event per increment of the pipeline's
  `coverage: scored=` counter (`kind` = `ml_scored_fixture` or
  `upcoming_fixture`): `fixture_id`, teams (raw + normalized), league,
  kickoff, `ml_probability`/`ml_majority_pick`/`sources_used` when
  ML-scored, `candidate_materialized` and factual
  `not_materialized_reason="no_candidate_emitted"`. ML entries also carry
  betting intent + the full `shadow_price_*` block (price, source,
  bookmaker, kind, captured-at/as-of stamps, age, stale flag, pre/post
  kickoff tri-state + proof basis, registered-source flag,
  `shadow_price_execution_safe=false` always, gradeable verdict + reason)
  and settle read-only via the exact candidate matcher for the
  captured-price shadow ROI; intent-less records are counted as
  ungradeable, never silently ignored.
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
* Report sections: the SCORED-UNIVERSE FUNNEL (pipeline_scored →
  shadow_scored_fixture_records + reconciliation → materialized →
  promoted → ticketed → scored-but-not-promoted →
  dropped-before-materialization), SHADOW GRADEABILITY (intent/price/
  fresh/stale/post-kickoff-excluded/timestamp-unknown-excluded/
  kickoff-unproven-graded/gradeable/fair-model/execution-safe counts),
  CAPTURED-PRICE SHADOW ROI (all gradeable, scored-not-promoted,
  promoted-not-ticketed, ticketed, fresh/stale, fair-model-separate, by
  price kind / source / bookmaker / bucket / rule-model / league /
  promotion / rejection-or-not-materialized reason / kickoff proof —
  all flagged AUDIT-ONLY — NOT STAKEABLE), headline counts (total scored, promoted, ticketed,
  promoted-not-ticketed, scored-not-promoted, execution-safe scored/rejected,
  pending, unmatched, no-execution-safe-price, unknown-reason,
  win/loss/void), ROI for ticketed legs / promoted-not-ticketed / all scored
  / all rejected / execution-safe rejected only, and groupings by rejection
  reason (incl. execution-safe-only), bucket, rule, league, market, price
  source, bookmaker, selected-vs-rejected, execution-safe-vs-not, plus the
  reconciliation block.

## Segment analysis and promotion map (AUDIT RECOMMENDATION — NOT LIVE STAKING LOGIC)

```bash
python scripts/scored_candidate_segment_report.py --date 2026-09-06
python scripts/scored_candidate_segment_report.py --from 2026-09-01 --to 2026-09-07 \
    [--json] [--min-settled N] [--min-days N] [--min-fixtures N] [--all-runs] [--root PATH]
```

Reads persisted ledgers only (no price fetching, no backfill, no mutation —
pinned by test). Two populations stay strictly separate:
`captured_price_shadow` (fixture-level, audit-only prices) and
`execution_safe` (strict candidate-level gate). Segments are built over all
single dimensions (promotion state, reasons, bucket, rule/model, market,
side, league/competition/country, price source/bookmaker/kind, stale,
registered, gradeable reason, kickoff proof, odds/probability/score/price-age
bands — fixed documented bands, not quantiles — trading date, weekday) plus a
CONTROLLED depth-2 compound whitelist; unconstrained mining is deliberately
not offered.

Promotion-readiness tiers (deterministic decision tree, thresholds
configurable; defaults `min_settled=30 min_days=3 min_fixtures=20`):
`BLOCKED_NEGATIVE`, `INSUFFICIENT_SAMPLE`, `WATCHLIST_POSITIVE`,
`PRICE_ENRICHMENT_CANDIDATE`, `SHADOW_PROMOTION_CANDIDATE`, and
`EXECUTION_SAFE_PROMOTION_CANDIDATE` — the last is reachable ONLY from the
execution-safe population and is still just a proposal label. Anti-overfit
guards: day/fixture concentration caps, single-source profit dominance,
stale-only-profit detection (`WATCH_STALE_ARTIFACT`), high pending/unmatched
share, and a conservative lower-confidence-bound ROI. Every segment carries
baseline ROI + lift (vs the full pool of its ROI type), an action
(`KEEP_BLOCKED` / `COLLECT_MORE_EVIDENCE` / `WATCH` / `WATCH_STALE_ARTIFACT`
/ `PRICE_ENRICHMENT` / `PROMOTION_REVIEW_AUDIT_PRICES_ONLY` /
`PROMOTION_REVIEW`) and warnings. The report always prints:
"No live betting behavior changed. Promotion requires separate explicit
implementation and review."

### Rolling windows and cross-window survival

```bash
python scripts/scored_candidate_segment_report.py --windows 7,14,30 --to 2026-10-07
```

Each window length gets its own stricter-with-length threshold profile
(`7d: 30/3/20`, `14d: 50/5/35`, `30d: 90/8/60`; other lengths scale
linearly from the 7-day base, never below it). Passing explicit
`--min-settled/--min-days/--min-fixtures` with `--windows` overrides every
window and the report prints `[THRESHOLDS EXPLICITLY OVERRIDDEN]` —
relaxation is always explicit and visible. A segment is
`PROMOTION PROPOSAL READY` ONLY when it is
`EXECUTION_SAFE_PROMOTION_CANDIDATE` in EVERY requested window; exec-promo
appearances that fail any window are listed under `NOT SURVIVED` instead of
being dropped. **Overridden thresholds can never mint proposal material**:
an all-window survivor under explicit overrides is demoted to
`EXPLORATORY SURVIVORS (OVERRIDDEN THRESHOLDS — NOT PROPOSAL MATERIAL)`
with `action=EXPLORATORY_REVIEW_ONLY`, and `promotion_proposal_ready`
stays empty — only the unrelaxed per-window profiles can produce
`PROMOTION PROPOSAL READY`. Proposal-ready remains a label — never an
automatic change.

### Promotion proposal template (step 8 — manual, human-reviewed)

When (and only when) a segment prints `PROMOTION PROPOSAL READY` under
unrelaxed profiles, write a separate proposal document (e.g.
`docs/operator/PROMOTION-PROPOSAL-<segment>-<date>.md`) answering ALL of:

1. Which segment survived 7/14/30 (keys, per-window settled/ROI/days/fixtures)?
2. What exact rule/gate currently rejects it (rejection reason codes, drop stage)?
3. Is the ROI execution-safe — not just captured-price (cite the exec-safe lines)?
4. How many historical tickets would have changed (replay count, dates)?
5. Would acca concentration increase (legs per league/day before/after)?
6. Would exposure/staking change (stake ladder impact, worst-case drawdown)?
7. Which leagues/sources/bookmakers drive the edge (concentration stats from the report)?
8. Are floors, vetoes, kickoff guards and source rules still intact under the proposal?
9. What is the proposed MINIMAL live change (single rule, smallest diff)?
10. What rollback/monitoring rule would disable it (metric, threshold, window)?

No report output ever changes live behavior; the proposal is reviewed and
implemented (or rejected) as its own explicit, separately-tested change.

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
  `shadow_scored` by construction; both levels are persisted
  (`scored_fixture` + `scored_candidate` events) and reconciled exactly at
  the fixture level in the report's SCORED-UNIVERSE FUNNEL section.
* `shadow_scored_fixture_records` is entry-level (one per counter
  increment); `fixture_records_unique` can be lower when two source keys
  named the same fixture — both are reported.
* The ledger only begins at deployment; earlier dates have no shadow data.

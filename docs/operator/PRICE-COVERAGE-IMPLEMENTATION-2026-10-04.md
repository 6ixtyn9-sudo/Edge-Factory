# Price coverage implementation — 2026-10-04

## Scope

This change makes picked-fixture price coverage measurable and spends bounded
price capture on the picked slate before provider-order leftovers. It does not
change any matching rule, odds floor, veto, abstain, certification, or
stakeability safeguard.

The operator pasted the 2026-10-04 `run-autonomous-agent` log after the first
implementation pass. The log is not committed in full (too large/noisy), but the
numbers below are copied from that log and from committed receipts where the log
omitted a field. Missing pieces are called out instead of estimated.

## Log-grounded pre-change coverage evidence

2026-10-03 BetExplorer receipt (`localdata/betexplorer_capture_2026-10-03.json`):

```text
candidate_fixtures=57 attempted=12 fixtures_with_rows=7 rows=21
be_429=0 be_cooling_down=false be_cached=12
```

2026-10-03 source-health (`localdata/source_health_2026-10-03.json`):

```text
betexplorer be_raw=21 be_usable=21 be_matched=0
oddspapi op_raw=30468 op_usable=30022 op_matched=0
  join_miss_counts: market_unsupported=10820 out_of_window=19202
theoddsapi oa_raw=589 oa_usable=589 oa_matched=0
```

2026-10-04 pasted run log (run `37175689485`, intraday mode):

```text
ML-meta 2026-10-04: scored 50 fixture(s), max ml_p = 81.0% -> 18 pick(s)
pre-match guard 2026-10-04: skipped 9
live odds enrichment 2026-10-04: picks=23 ... theodds_matched=1 oddspapi_matched=9 betexplorer_matched=6 ... none=5
Summary: CLEAN=3 CAUTION=1 WATCHLIST_odds=4 WATCHLIST_uncorroborated_price=1 SKIPPED_veto=8
Autonomous Accumulating Ledger: existing=22 new=2 superseded=15 total_active=24
PRICE SUPPLY: named-book execution prices=11 average-bookmaker donor prices=4 total donor-priced candidates=16 execution-safe candidates=11 qualifying legs=3
```

Provider capture evidence from the same pasted log:

```text
env: ODDSPAPI_MAX_FIXTURES=20 EDGE_FACTORY_ODDSPAPI_PRICES=1
TheOddsAPI candidate capture: shortlist=24, auto=2 fixture(s) due, rows=0, credits_used_month=30/1440
OddsPAPI candidate capture: fixtures=860, matched=11, rows=42916, added=29304, slate_priority_fixtures=6
BetExplorer candidate capture: candidates=24 attempted=12 fixtures=8 rows=24 status=ok
Final priced pass bundles: theodds_raw=67 usable=67 matched=1; oddspapi_raw=81314 usable=81314 matched=9; betexplorer_raw=36 usable=36 matched=6
TheOddsAPI later CLV capture: auto=7 fixture(s) due, matched=2, rows=114, credits_used_month=34/1440
```

What cannot be derived from this pre-change log:

* Total `attempted=<n>` across all three priced sources: BetExplorer attempted
  `12` and TheOddsAPI candidate capture attempted `2`, but old OddsPAPI stats did
  not print attempted fixture count (only cap=20, `fixtures=860`, `matched=11`,
  and `slate_priority_fixtures=6`).
* `never_attempted` vs `attempted_no_quote` vs `quote_not_joined`: old receipts
  did not store `attempted_fixtures`, so the four-way cause split for the four
  `WATCHLIST_NO_ODDS` final fresh picks is not recoverable without guessing.

2026-10-04 archive snapshot (`localdata/picks_2026-10-04.json`), evaluated with
the new diagnostic helper against the already captured bundles, gives the active
ledger surface but still inherits old missing-attempt receipts:

```text
picks=24 priceable_candidates=24 fixtures_quoted=11 picks_matched=11 picks_unmatched=13
per-source: betexplorer=12/24 oddspapi=0/0 theoddsapi=0/0
```

## What changed

### Coverage funnel instrumentation

Final priced builds now print:

```text
coverage: scored=<n> picks=<n> priceable_candidates=<n> attempted=<n> fixtures_quoted=<n> picks_matched=<n> picks_unmatched=<n> per-source: betexplorer=<att>/<cand> oddspapi=<att>/<cand> theoddsapi=<att>/<cand>
coverage unmatched_causes: never_attempted=<n> attempted_no_quote=<n> quote_not_joined=<n> league_not_carried=0 league_not_carried_note=not_derived_all_source_competition_catalog_absent
```

The cause split is derived from same-day capture receipts plus exact normalized
fixture keys in the bundles consumed by the final build. `league_not_carried` is
not guessed: the current repository has no all-source competition catalogue, so
runtime prints a note and the archive-level competition report is the structural
evidence surface.

### Slate-first capture

* OddsPAPI now falls back from stale `picks_today.json` to the same-day
  `picks_YYYY-MM-DD.json` archive and orders slate fixtures by pick confidence.
* BetExplorer now prefers the fresh same-day candidate slate (`picks_today.json`),
  falls back to the same-day archive on first-run/stale-slate cases, and orders
  fixture attempts by pick confidence.
* TheOddsAPI shortlist is confidence-ordered before its existing auto planner
  applies due/attempt-ledger rules.

All three paths use exact normalized fixture pairs only; no fuzzy matching or
kickoff widening was introduced.

### Receipt persistence

New same-day, secret-free receipts:

* `localdata/oddspapi_capture_YYYY-MM-DD.json`
* `localdata/theoddsapi_capture_YYYY-MM-DD.json`

BetExplorer receipts now include attempted and quoted fixture names as well as
counters. Receipts contain fixture names/counters only: no keys, URLs, headers,
or payload fragments.

## Post-change dry/throwaway verification

A throwaway checkout was used for write-producing commands. After running the
updated BetExplorer capture in the throwaway copy with an 18-fixture cap against
2026-10-04 cached state:

```text
betexplorer snapshot 2026-10-04: candidates=24 attempted=18 fixtures=10 rows=30 status=ok
coverage: scored=0 picks=24 priceable_candidates=24 attempted=18 fixtures_quoted=11 picks_matched=11 picks_unmatched=13 per-source: betexplorer=18/24 oddspapi=0/0 theoddsapi=0/0
coverage unmatched_causes: never_attempted=4 attempted_no_quote=9 quote_not_joined=0 league_not_carried=0 league_not_carried_note=not_derived_all_source_competition_catalog_absent
```

This run proves the receipt-backed funnel and raised BetExplorer attempt cap are
respected. It did not prove a named-book match lift in this sandbox because the
current checkout has no usable live provider credentials and the final pick
engine produced no fresh current-date slate under the credential-absent dry run.
A production Actions run with the real secrets is required to measure the live
post-change lift.

## Budget/cap proposal

* **TheOddsAPI**: no workflow/code cap increase. The pasted run log shows
  `credits_used_month=30/1440` after the candidate capture and `34/1440` after
  the later CLV capture, leaving `1406` monthly credits unused at that point.
  Quota was not binding; the important unknown was why auto mode marked only
  `2` of `24` shortlist fixtures due. Receipts now persist and logs print
  `skip_reasons` / `due_reasons` so the next production run shows whether the
  gate was prior rows, close-window timing, retry cooldown, or kickoff guard.
* **OddsPAPI**: no cap increase. The pasted workflow env was still
  `ODDSPAPI_MAX_FIXTURES=20`, and the same log showed provider supply of
  `fixtures=860` but only `slate_priority_fixtures=6` against roughly 24
  priceable slate fixtures. Raising 20 → 40 before improving exact slate/provider
  overlap would mostly buy provider-order leftovers. Receipts now record
  `slate_match_mode=exact_normalized_pair`, `slate_candidate_fixtures`,
  `slate_provider_overlap_fixtures`, and compact unmatched slate names for the
  next repair pass. No workflow file was edited; proposed YAML lives in
  `docs/operator/daily.yml.proposed`.
* **BetExplorer**: code ceiling raised to 24 while default remains 12. Proposed
  secret/workflow value: `EDGE_FACTORY_BETEXPLORER_MAX_FIXTURES=18`; the adapter
  still cools down on the second HTTP 429 and the code hard-stops at 24.
* **BetMiner**: untouched.

## Archive competition coverage

`docs/operator/PRICE-COVERAGE-2026-10-04.md` was generated from archived pick
ledgers. Totals:

```text
Archive files scanned: 110
Picks generated: 1716
Picks ever named-book priced: 715
Structurally-zero candidates (priced=0, picks>=3): 60
```

Examples in the persistent zero list include `Se4`, `Jp1`, `Sc1`, `De4`,
`Ie1`, `L2`, `Cz4`, `NoW`, `Pl1`, `Norway,2. Division Avdeling 1`,
`Norway,2. Division Avdeling 2`, `Finland Ykkönen`, `Il1`, `It2`, `Tz1`, and
others. Low-sample zero examples in the full table include Canadian Premier
League and USL Championship variants. Suppressing these picks is **not**
implemented; any suppression should be operator-approved, config-gated, and
printed.

## Safety confirmations

* No matching rule was loosened.
* `_fixture_orientation_agrees` and `_row_matches_selection` were not weakened.
* No odds floor, veto band, no-bet safeguard, abstain rule, source registration,
  fair-price stakeability, or donor role was lowered or promoted.
* `.github/workflows/*` was not edited.
* No secrets were printed, persisted, or committed.

# Price coverage implementation — 2026-10-04

## Scope

This change makes picked-fixture price coverage measurable and spends bounded
price capture on the picked slate before provider-order leftovers. It does not
change any matching rule, odds floor, veto, abstain, certification, or
stakeability safeguard.

The uploaded `run-autonomous-agent` log was not present in this sandbox under
`/home/user/uploads`, so pre-change numbers below are grounded in committed
run receipts/source-health files where available. The missing pieces are called
out instead of estimated.

## Pre-change coverage evidence available in the checkout

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

2026-10-04 archive snapshot (`localdata/picks_2026-10-04.json`), evaluated
with the new diagnostic helper against the already captured bundles:

```text
picks=24 priceable_candidates=24 fixtures_quoted=11 picks_matched=11 picks_unmatched=13
per-source: betexplorer=12/24 oddspapi=0/0 theoddsapi=0/0
```

The old receipts did not store `attempted_fixtures`, so the four-way cause split
could not be derived honestly before this change. In particular, `never_attempted`
versus `attempted_no_quote` was not recoverable for pre-change Oddspapi/TheOddsAPI
runs from committed state.

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

* **TheOddsAPI**: no workflow/code cap increase. The submitted prompt cited
  `credits_used_month=24/1440`; the committed local usage ledger currently shows
  `34/1440` October credits across three keys. With `ODDS_API_MARKETS=h2h,totals`,
  each fetched event costs 2 credits. Existing attempts ledger already prevents
  every 3-hour run from re-fetching the same fixture.
* **OddsPAPI**: code ceiling raised from 20 to 40 while keeping the code default
  at 20. Proposed secret: `ODDSPAPI_MAX_FIXTURES=40` only if the operator confirms
  provider allowance of at least 250 fixture-odds requests/day (40 × 5 runs/day =
  200, leaving 20% margin). No workflow file was edited; proposed YAML lives in
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

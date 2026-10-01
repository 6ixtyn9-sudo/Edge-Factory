# Follow-up: scoutingstats stores the kickoff as `captured_at`

**Status: KNOWN DEFECT, DEFERRED DELIBERATELY.** Not fixed in PR #18.

## The defect

`picks_today._scoutingstats_rows_to_odds` sets:

```py
"captured_at": row.get("kickoff") or row.get("time") or "",
```

That is the fixture's kickoff, not the instant the price was observed.
It produces capture timestamps in the future — Germany vs Serbia carried
`odds_captured_at = 2026-10-01T18:45:00Z` on a run that executed at
07:00 the same morning. Any CLV line-movement measurement between two
"capture" instants is meaningless for this provider.

## Why it was not fixed here

Three consumers knowingly depend on the current behaviour, so changing
the producer alone would silently alter price freshness handling for the
whole scoutingstats bundle — the source feeding most same-day candidates:

- `src/edgefactory/enh_pricing.py::_fresh_row` — drops rows whose
  `captured_at` falls outside `[kickoff - max_age_h, kickoff]`. With an
  empty `captured_at` it fails open, changing which rows survive.
- `scripts/auto_tickets.py` (~:1256) — documents the behaviour explicitly
  and compensates for this one provider when resolving kickoffs.
- `scripts/replay_harness.py` (~:1621) — assumes `captured_at == kickoff`
  "by construction" for this provider.

A correct fix changes the producer and all three consumers together, with
replay evidence that the scoutingstats price bundle does not shrink.

## Why it matters more now

`MIN_EDGE_TO_DISPATCH` dropped from `0.02` to `0.0`, so thin-but-positive
selections now reach the assayer instead of being vetoed. Freshness
therefore decides whether a thin edge is real: **a +0.005 edge on a
verified fresh line is not the same bet as a +0.005 edge on a price whose
capture time is actually the kickoff.**

Until the coordinated fix lands, the run states the dependency rather
than hiding it. `run_invariants.check_price_capture_proxy` emits a
WARNING — `thin_edge_rests_on_a_proxy_capture_timestamp` — for any
selection with `0.0 <= edge < 0.02` priced from a source in
`PROXY_CAPTURE_SOURCES`.

## Scope when fixed

- Emit a real capture instant at fetch time, or an explicit null.
- Never present `captured_at == kickoff` as a capture instant in logs,
  summaries or CLV.
- Update the three consumers in the same change.
- Re-run replay and confirm candidate volume is unchanged.
- Remove `scoutingstats_odds` from `PROXY_CAPTURE_SOURCES` and delete the
  warning once provenance is real.

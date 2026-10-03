# BetMiner V3 endpoint contract and quota guard

Verified from the provider's V3 documentation on 2026-10-03:

- Base URL: `https://betminer.p.rapidapi.com`
- Dated fixture/prediction board: `GET /matches/{date}`
- Response wrapper: `success`, `data`, `meta`
- Match Object evidence fixture:
  `tests/fixtures/betminer_matches_2026-10-03.json`

Production had already observed HTTP 404 from both
`/value-bets/{date}` and `/value-bets/{dateFrom}/{dateTo}`. Those routes are
listed as betting-system routes but are not the full dated Match Object board
used by this adapter. There is no endpoint ladder: capture calls only
`/matches/{date}`.

## Five-call daily budget

- Provider free tier: 5 requests/day.
- Adapter hard cap: `EDGE_FACTORY_BETMINER_MAX_CALLS`, default 4.
- Normal capture: one dated request.
- `scripts/probe_betminer.py`: at most one request and no alternates.
- Every contract failure writes a scrubbed
  `localdata/betminer_probe_YYYY-MM-DD.json` receipt containing endpoint,
  status, reason, schema keys/counts, and timestamp only.
- A later run on the same date reads the receipt and makes zero calls.
- A successful row ledger remains the earlier cache-first short circuit.

No live BetMiner request was made during this repair: **0/5 calls consumed**.
The parser remains non-execution-eligible unless a response names bookmaker
provenance; model/fair or unidentified aggregate odds cannot become a named
bookmaker quote.

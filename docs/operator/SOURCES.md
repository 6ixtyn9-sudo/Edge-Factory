# Sources, prices and collection permission

[Operator handbook](README.md) · [Research](RESEARCH.md) · [Evidence](DATED-CLAIMS.md)

Source roles are implemented in `edgefactory.price_sources`; prediction-source
eligibility/retirement is tracked separately in `edgefactory.source_health` and
the existing consensus contracts. Fetchability, a vote, a price and permission
to use any of them are four different things. Source health is dated, not a
permanent property of this document.

## Price roles and policy

| Role | Sources | Execution boundary |
|---|---|---|
| Named-book / bookmaker-backed | BetExplorer, Bzzoiro odds, TheOddsAPI, PinnAPI, SharpAPI, OddsPAPI | Only valid time-qualified exact quotes; retain the actual book. Never an extra prediction vote merely because it prices. |
| Average-bookmaker donor | Boggio | Disclose `provider_average`; never call it a named bookmaker. |
| Fair/model donor | Bet Better | Disclose `fair`; not an executable bookmaker quote. Direct stakeability is a separate opt-in. |
| Evidence-only provider prices | BetMiner, ScoutingStats odds | Not direct execution donors under the current registry. An aggregate cannot become a named-book quote by relabelling it. |
| Optional corroborator | SportyTrader odds | Off by default, corroborator only; never the selected execution price. |
| Historical fallback | `forebet_best` | Off by default; not a named bookmaker. Missing live prices normally mean abstain. |

Current **code defaults** (deployment environment can override them):

| Switch | Default |
|---|---|
| `EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR` | `1` |
| `EDGE_FACTORY_ENABLE_FAIR_PRICE_DONOR` | `1` |
| `EDGE_FACTORY_FAIR_PRICE_STAKEABLE` | **`0`** |
| `EDGE_FACTORY_REQUIRE_PRICE_CORROBORATION` | `0` (preferred, not required) |
| `EDGE_FACTORY_REQUIRE_NAMED_BOOK_CORROBORATION` | `0` |
| `EDGE_FACTORY_ALLOW_SOURCE_FALLBACK` | **`0`** |

The actual policy is printed on each run. Never infer the deployed values from
an old note. Enabling evidence capture, enabling a donor and making a fair
price stakeable are not interchangeable approvals.

Selection evaluates health, exact fixture/market/selection, execution
eligibility and named-book provenance, then configured source priority before
cross-source freshness. Named-book priority is BetExplorer → Bzzoiro →
TheOddsAPI → PinnAPI → SharpAPI → OddsPAPI. This is not permission to select
an unhealthy, stale, future-dated or suspect/fuzzy quote. All observed quotes
stay on the price board; the selected one is only the printed choice.

Corroboration counts independent families, not API endpoints. Multiple relays
of Pinnacle do not create independent books; aliases of BetExplorer are one
family. Keep publisher independence distinct from bookmaker independence.
The helper in `edgefactory.corroboration` is documentation/research support,
not a separately activated live promotion policy.

The candidate pass cannot emit tickets or spend shadow-price quota. Capture
then precedes the final priced pass and its fresh `as_of`. A historical price
is not a present execution quote; an unfinalized candidate archive is not a
frozen official card. Missing/invalid identity, market, side, line, period,
book or required timing/provenance means no admissible quote.

## BetExplorer authorization and admission

### Personal-use bounds

The operator authorized bounded **own-card** collection, later extending it to
the detail and market tabs of every fixture the existing odds lane actually
matches/prices. This does **not** authorize sweeping the whole day's board,
new bulk archives, paid plans or a priced license. No Livesport reply is
recorded in the retained licensing record. Log any later reply with date and
gist here; a quoted price is politely declined. Any extension needs a new
operator decision, not an inference from “all matches”.

The separate manual `capture_betexplorer_match.py` snapshot accepts only today's
own-card explicit match URLs. It is opt-in, not newly scheduled by this guide.
Further collection beyond the authorized scope stays on hold pending the
operator's decision; this cleanup authorizes **zero** provider calls.

Standing bounds:

- At most one fixture visit/day; honest project user-agent, bounded retention,
  off-peak manual work, single-flight/politeness and no retry-hammering.
- The separate own-card snapshot and added market-tab requests use at least
  **5.1 seconds** spacing; the existing priced lane's own three-second pacing
  is a distinct contract, not permission to speed up the added tabs.
- Existing fixture budget: default **12**, ceiling **24**. Added market-detail
  budget: default **180 network attempts/run**, controlled by
  `EDGE_FACTORY_BE_MAX_REQUESTS_PER_RUN`. `EDGE_FACTORY_BE_MARKET_TABS=0`
  disables the added tabs. Do not increase budgets as an incidental repair.
- The retained tab families are `1x2`, `ou`, `ah`, `ha` (DNB), `dc`, `bts`.
  A fixture page plus the six comparison responses is not one HTTP request.
  Client-side line/“show more” toggles are not extra fetches. No bookmaker
  redirects, cookie/age/challenge bypass, extra standings sub-tabs or invented
  endpoints.
- The earlier robots review found the day-listing discovery query in conflict
  with robots restrictions. That conflict was disclosed, **not resolved into
  blanket permission**. Do not expand discovery; any policy change needs an
  explicit ruling. Path-only match/detail allowance is not a site-wide license.
- Retain capped structured rows, timestamps/digests and explicit failures,
  not raw HTML or credentials. Source ledgers have existing local-retention
  rules; frozen decision/provenance dependencies are protected separately.

The original operator wording and supersession sequence are available in the
[pinned licensing record](https://github.com/6ixtyn9-sudo/Edge-Factory/blob/30e9372aab33e1e9444c1f5fd3b916df91ca7f0e/docs/operator/BETEXPLORER-LICENSING.md).
Those are project permissions, not a claim that the publisher granted a license.

### Verified secondary quote admission

`EDGE_FACTORY_ENH_BOARD` is the existing enhancement switch, not a new lane.
The retained-detail reader may price match O/U, BTTS and side-correct double
chance only when the existing checks all pass:

1. Preserve the original five-integer page `data_dt`; never fill missing old
   tuples from a pick date or a bookmaker's timezone-free `created` field.
2. Resolve page-clock hypotheses with independent **oriented, exact,
   same-squad** provider schedule observations. Observations/capture must be
   before the run's real `as_of`, before kickoff and before the 09:00 SAST
   cutoff; resolved kickoff must remain ahead of cutoff. Conflicts fail closed.
3. The shared witness engine accepts qualified original CSV/provider evidence
   and the retained OddsPAPI fixture-board cache. The latter supplies schedule
   evidence only—not an OddsPAPI price and not a new request. Missing historical
   participants, IDs, aware clocks or observation origins stay missing.
4. Require complete column semantics, full row width, actual nonblank bookmaker,
   finite odds >1 and the exact valid line/selection. Recheck the existing
   freshness policy (default 24h) at actual execution time.
5. Carry ledger/raw-row hashes, JSON/CSV locations, page clock, resolved schedule,
   market/side/book/price/capture and row/column indices through the recipe as
   `price_provenance`. The actual execution-safe admission door revalidates it;
   a source label or `corroborated=True` alone cannot pass.

Match O/U 1.5/2.5/3.5/4.5, both BTTS sides and oriented 1X/X2 share this gate.
Retained AH/DNB are evidence-only here; parent 1X2 remains its existing path.
The original consumption directive maps exact labelled cells to `ou_<line>`,
`btts` and `dc`; the registry floor, not a newly invented EV gate, decides
eligibility alongside the independent safeguards.
BetExplorer match totals do **not** supply team totals. Current cohort,
probability, odds-floor, kickoff, freeze and staking safeguards remain unchanged.
Synthetic admission tests demonstrate wiring, not live coverage or profitability.

## Provider contracts and budgets

### BetMiner

Use the adapter's **current** bounded `/value-bets/{date}` and range contract;
older `/matches/{date}` guidance was superseded by the recorded gateway-routing
404 streak (see [dated claims](DATED-CLAIMS.md)). Do not revive an endpoint
ladder from an old proposal or erase a binding same-day failure receipt to retry.
The provider free allowance is five requests/day; the adapter's existing hard
cap defaults to four. Normal capture is cache/receipt-first; diagnostics use
scrubbed endpoint/status/schema/timestamp metadata, never request credentials.
Stored forecasts are not executable bookmaker prices by default.

### PinnAPI

An unofficial, disposable Pinnacle relay, **never a vote**. REST uses
`x-portal-apikey`, soccer `sport_id=1`; a query-key fallback is limited to the
adapter's existing HTTP-401/403 behavior. Do not repeat the old `sport_id=2` claim as a
receipt. Parse only recognized complete market groups; no two-way money line
may masquerade as a coherent 1X2 book. Same-day/freshness and exact joins still
apply. The manual probe checks auth, schema and coverage with a bounded request
budget; it is not a new ingest or automatic retry path.

### SharpAPI

`GET /api/v1/odds`, explicit soccer filter `soccer`; retain configured limit,
book/market and credentials mapping. No date query unless the configured
provider contract allows it. `probe_sharpapi.py --discover-sport` is a **live**
manual probe, not an offline setup check. Metadata/status may be logged; never
keys, full authenticated URLs or headers.

### Boggio and card enrichment

Boggio prices are bookmaker averages, not named-book quotes. Retain publication
and capture clocks; publication after capture is suspect and loses eligibility.
The free-tier lookahead is limited; do not manufacture earlier availability.
Card-enrichment H2H snapshots are bounded, pre-kickoff context observations,
not a new probability, vote, training target or certification shortcut. The
installed daily job budgets **90 monthly calls with 20 reserved**. Planning and
capture use the same observation clock; paid calls must be planned before spend.

### PredictIQ

Market-derived/convergent echo-test candidate: **zero voice credit and never a
price corroborator**, regardless of future fetchability. Multiple publishers
repeating a market signal do not become independent models.

### Other sources and future collection

Forebet's production voting/pricing retirement boundary is **2026-06-12**.
Historical rows and explicitly separate manual diagnostics do not reopen live
source eligibility. Source hunting is English-only; non-English hunting remains
closed. SportsGameOdds remains **SKIP / no adapter authorized**: a 40–70 fixture
slate cannot guarantee the required 2× headroom within 2,500 objects/month.
Reopening needs a measured bounded plan and explicit approval.

New crawling/backfills require exact-host robots/terms review, approved date and
request limits, honest UA, one in-flight request, immutable raw provenance and
stop-on-denial/backoff/challenge behavior. No solver, paid proxy or silent
alternate transport. Missing robots is not permission. Opening and closing
prices stay separate; vendor win/loss labels are not settlement truth. Historical
source gaps are not blanket authorization to crawl or add consensus weight.

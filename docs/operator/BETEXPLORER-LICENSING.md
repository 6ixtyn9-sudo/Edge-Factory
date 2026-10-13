# BetExplorer own-card snapshot — operative Phase-2 spec (2026-10-10)

The referenced drafted OWN-CARD SNAPSHOT DESIGN and outreach email are not present in this checkout; this document specifies only the bounds supplied in the operator's ruling. Do not infer additional permission. No Livesport reply has been received or logged here. If a reply arrives, log date and gist below; a priced license is politely declined and the project remains personal scale.

## Wire (opt-in, not scheduled)

`python scripts/capture_betexplorer_match.py --date YYYY-MM-DD` reads `localdata/picks_today.json`. It only accepts today's own-card rows with an explicit plain HTTPS BetExplorer football match URL (`betexplorer_match_url` or `match_url`). It does not discover URLs by crawling a schedule/results listing, and skips rows without a URL. One attempt per unique team-key pair per day is durably reserved before the request. At least 5.1 seconds separate requests within a run. The user-agent identifies the project. On a failed response, stop the run without retry. Run manually only off-peak; do not wire into daily jobs. The ledger `localdata/betexplorer_match_shadow_YYYY-MM-DD.json` contains no raw HTML, URL, credentials, or individual names: only date, normalized team keys, timestamps, status, page digest and tentative observations. The script prunes its own ledgers older than 30 days; do not commit generated ledgers.

Only the match page is fetched. No bookmaker redirects, tab traversal, query pages, or retries. No activation/ML consumption: extracted final score and H2H are tentative, while standings position and 1X2 prices remain null until selectors and fixture identity are independently verified with offline fixtures. A rendered page from an archived match cannot provide a safe pre-match feature without a timestamped pre-kickoff snapshot. A final score is a target/settlement label, never a pre-match predictor. Join requires date, league, both ordered source-team keys and squad-marker checks from `identity.py`; absence of trustworthy page fields means `unverified_identity` and no promotion. The existing live odds capture is separate and not changed by this spec.

## Operator rulings (verbatim)

1. Personal-use judgment: bounded own-card BetExplorer snapshots ARE authorized
   personal use. The collection hold is LIFTED within these exact bounds:
   fixtures already on the daily card only, <=1 fetch/fixture/day, >=5s spacing,
   off-peak, explicit user-agent, bounded retention, no tab-crawling beyond
   results/odds + the agreed match-page scope, no retries-hammering on failure.
2. Bootstrap constraint: this project is bootstrapped. No paid plans, no priced
   licenses. If Livesport replies with a price, the answer is a polite decline
   and we remain at personal scale. Log any reply (date + gist) in
   docs/operator/BETEXPLORER-LICENSING.md.
3. Until/unless Livesport replies otherwise, the wire operates strictly within
   the bounds described in the outreach email — no more.

## Operator directive — 2026-10-12: retain the match detail of every match we price

Verbatim: *"no i want us to get more of bet explorer, every single match where
it gets its odds, it should click the match link in order to get the match
details"*, with the Coventry - Newcastle match page pasted as the example of
what "match details" means (H2H, the per-bookmaker odds comparison, standings,
last results).

What was built, inside the standing bounds (own-card fixtures, <=1
fetch/fixture/day, >=5.1s spacing, explicit user-agent, bounded retention, no
tab traversal, no retries-hammering):

- The live odds lane **already** fetched each matched fixture's match page (to
  read its layout key) and its 1x2 comparison response; both were collapsed to
  a single best-price triple and thrown away. The same two responses are now
  retained: per-bookmaker 1x2 rows (label, the three prices, each price's rank,
  movement arrow, when it was set, the page's own best-price flag), the average
  line, and the match page's own blocks (H2H record and meetings, last-results
  rows, a bounded standings excerpt, response digest).
- **Zero new requests.** Two requests per matched fixture, exactly as before,
  under the existing 12-default / 24-ceiling fixture budget. No market tabs
  (O/U, AH, DNB, DC, BTTS), no bookmaker redirect, no raw HTML stored, no
  retry policy change.
- Retention: `localdata/betexplorer_match_detail_YYYY-MM-DD.json` — capped
  lists (24 books, 8 H2H rows, 10 last-result rows, 96-char excerpts), a
  30-day local prune, committed alongside the other BetExplorer receipts.
- Consumption in that build: none. Pricing still read the best triple only;
  the ledger was read by the capture receipt for counts and by nothing else.
  A row whose markup carries no bookmaker is stored with no bookmaker, never
  a guess. (Superseded by the Stage 1 consumption bullet further down.)

Robots state re-verified 2026-10-12 against
`https://www.betexplorer.com/robots.txt`: the path-only match page and the
`match-odds/...?lang=en` comparison are allowed; `?year=`, `?month=`, `?page=`,
`?t=`, `?match=`, `/bookmaker/` and `/redirect/` are disallowed. The
retained-detail build adds no disallowed request, but it exposes one: our
day-listing discovery step (`/football/results/?year=&month=&day=`) uses a
disallowed query form, and the historical archive builder did the same. That is
now an operator decision, not a silent one — either keep discovery as-is and
accept the robots conflict, or switch it to match URLs the run already holds
(the detail ledger stores event_id and match_url per fixture, so a fixture seen
once can be revisited on a later day without any listing query).

Build-time inspection (disclosed): a handful of read-only fetches of the one
public example fixture the operator pasted, to learn the markup before writing
the parser. Nothing was bypassed: no cookie, redirect, age-gate or challenge
handling was added or attempted. The listing fetch already refuses
challenge/age markers; the match-page observation now records a `challenge`
flag instead of reading through such a surface.

## Operator directive — 2026-10-12 (later): keep every market the page shows

Verbatim: *"no i want it to also get the info when we click the match link maybe
all matches should be fetched i dont mind if takes a bit longer as the
automated runs happen overnight anyways"*, following the earlier *"every single
match where it gets its odds, it should click the match link in order to get the
match details"* and the pasted Coventry - Newcastle page, whose Odds Comparison
and market tabs (1X2 / O/U / AH / DNB / DC / BTTS) are what "the info" means.
The runtime sentence is the authorization for the added requests below; the
"all matches" reading taken here is every fixture the odds lane matches and
prices (each one now yields all six markets). Sweeping the day's whole board —
fixtures we do not price — is NOT done and would need its own ruling.

What was built — the "click more" the page shows, made explicit:

- The page's own tab menu carries the codes: `1x2`, `ou` (Over/Under), `ah`
  (Asian Handicap), `ha` (Draw No Bet — the menu attribute says `dnb` while the
  click code and the URL use `ha`), `dc` (Double Chance), `bts` (Both Teams To
  Score). The parser reads the codes the page uses; labels are noted here, not
  hardcoded.
- Each market tab is exactly one response
  (`/match-odds/<event>/<page>/<market>/bestOdds/?lang=en`). Every handicap
  line of that market arrives inside that one response; the per-line sub-tabs
  (ALL, 1.5 … 6.5 for O/U; -0.5 … -3.5 for AH) are client-side toggles and are
  NOT requests. Added cost: five requests per priced fixture, six market
  responses per fixture in total (page + 1x2 + the five tabs).
- Retained per market: the page's own column labels (1/X/2, Over/Under, 1/2,
  1X/12/X2, Yes/No), one row per bookmaker and handicap line (price, the
  page's own rank kept exactly as written — including two-place codes such as
  `02` and the letter ranks `y`/`n` — movement arrow, creation stamp, the
  page's best-price flag), and the page's own average line, per handicap
  section (a single flat average only when one line makes it unambiguous).
- Bounds unchanged: own-card priced fixtures only, one visit per fixture per
  day, >=5.1s between requests for the added tabs (`_MARKET_INTERVAL`; the
  priced lane's own 3s remains), a per-run request budget (default 180 network
  attempts, `EDGE_FACTORY_BE_MAX_REQUESTS_PER_RUN`) that stops detail tabs and
  never the priced lane, the existing 12-default fixture budget, and an opt-out
  switch (`EDGE_FACTORY_BE_MARKET_TABS=0`) restoring exactly the previous
  two-request behaviour. No `/bookmaker/` link, no `/redirect/`, and no
  `?page=`/`?t=`/`?match=`/`?year=` query form is requested for a market (the
  day-listing query decision above is untouched).
- Retention: `localdata/betexplorer_match_detail_YYYY-MM-DD.json`, schema 2 —
  per fixture `{event_id, match_url, kickoff, home, away, league, page_param,
  best_1x2, markets{...}, market_failures, page{...}}`. Caps: 24 books on
  single-line markets, the 10 lines nearest level x 6 books (48 rows) on
  multi-line markets, the match page's whole H2H meeting list (up to 40 rows),
  10 last-result rows (the page serves 5 per team), and its whole league table
  (`standings_columns` + `standings_rows`, up to 40 rows). Local prune window
  30 days (`scripts/clean_localdata.py`).
- Correction (same day): the first build kept a 240-character "standings
  excerpt". That was wrong and the operator caught it — *"the standing excerpt
  is not short, you did not click show more"*. The match page serves the
  **entire league table** (all 20 rows for the example fixture) and the whole
  H2H meeting list; "Show full table" and "Show more matches" are client-side
  toggles, so both are now read in full from the same response — no new
  request. Standings are stored as the page's own column labels plus per-row
  rank, team, MP, W, D, L, goals for/against, goal difference and points; the
  Form column is icons and is not stored. The standings sub-tables the page
  offers (Form, O/U, HT/FT, Top scorers; Overall/Home/Away) are each a
  separate AJAX request and are NOT fetched; the last-results selector
  (5/10/15/all) also stays at what the page serves (5 per team).
- Consumption (Stage 1, operator directive 2026-10-12): the retained detail
  now prices the **enhancement board** — `enh_pricing._accumulate_betexplorer`
  reads this ledger for the day and merges it into the same local price index
  the board and the enhancement slip are priced from. Read: the `ou` tabs'
  Over/Under cells per handicap line, `bts` Yes/No and `dc` 1X/12/X2, each
  cell taken by the label the page writes, never by position. A cell the site
  flagged as a best-price offer wins its slot; otherwise the highest retained
  price does, and the price keeps the row's own bookmaker and creation stamp.
  A market this overlay does not price is skipped rather than guessed, and
  nothing here is an EV gate — the registry floor decides what is a bet. All
  of it stays behind `EDGE_FACTORY_ENH_BOARD`: with the flag unset the ledger
  contributes nothing and the board renders byte-identical (round-2 §3). A
  tab that fails, is budget-stopped or is switched off is recorded
  (`market_failures`) rather than papered over, and a detail-write failure
  never touches pricing.

Build-time inspection (disclosed, this round): read-only fetches of the public
`ou` and `bts` endpoints for the same one example fixture the operator pasted,
to learn the thead labels, tbody ids and rank formats before writing the
parser, and one read-only fetch of the same public match page to confirm what
the standings block serves and what "Show full table" does. Nothing was
bypassed: no cookie, redirect, age-gate or challenge handling was added or
attempted.

## Livesport replies

None recorded. Checked 2026-10-10 by the continuation session: no reply had been
forwarded by the operator, so the wire stays built-but-unrun and NO new BetExplorer
collection happened. Standing state to remember:

- The bounded own-card snapshot spec above is already authorized and already
  implemented (`scripts/capture_betexplorer_match.py`, `sources/betexplorer_match_snapshot.py`);
  directive (e) of the operator ruling holds any FURTHER collection until the
  operator says go after Livesport.
- If a reply arrives: log date + gist verbatim below. A quoted price => polite
  decline per the bootstrap constraint (no paid tiers, no priced licenses) and we
  stay at personal-use bounds. Actual permission granted => bring the proposed
  own-card snapshot extension to the operator BEFORE building anything.
- Nothing in this session dispatched, fetched, or retried a BetExplorer page.

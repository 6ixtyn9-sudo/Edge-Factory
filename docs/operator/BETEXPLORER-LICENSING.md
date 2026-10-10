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

## Livesport replies

None recorded.

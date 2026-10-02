# SOURCE-HUNT 2026-10 — free football prediction/odds API hunt (HUNT-01)

**Date:** 2026-10-02 (UTC) · **Task:** HUNT-01 · **Change class:** docs-only
(no code, no workflow edits, no signups, no keys, no authenticated calls).

**Scope:** English-language public sources only — standing rule: non-English
source hunting is CLOSED. Everything here was read from public pages through
the page-relay (raw shell egress is `HTTP 000` from this checkout, the standing
receipt in [`CANDIDATE-SOURCES.md`](CANDIDATE-SOURCES.md)). One unauthenticated
public JSON endpoint (Bet Better) was probed live because its docs require no
key. Nothing was subscribed to.

---

## 0. Headline results

- **25 candidates cataloged** (§4), **13 with own-page/docs receipts**
  (§5 scorecards), **shortlist of 3** (§6).
- **WINNER (prediction voice): Betminer** — free 5 req/day, no card, instant
  RapidAPI key, bulk whole-day predictions endpoint, model-built probabilities
  across a large competition set, commercial use permitted on the free tier.
- **Price-donor pick: pinnapi** (Pinnacle pre-match snapshots, free 100 REST
  req/day, no card) — directly targets the `SCOUTINGSTATS_SOLE` corroboration
  problem.
- **Second shadow voice: PredictIQ Pro** (free, bulk predictions endpoint,
  published calibration) — carried **only** as an echo-test candidate because
  its own docs admit the ensemble includes devigged market odds.
- **Seed finding #2 (API-Football) FAILED live verification.** The free plan's
  season window lags current seasons (2022–2024 as of May 2026), so
  `/predictions` cannot serve 2026-27 fixtures on free. Details in §5.2.
- **Seed finding #3 (Sportmonks) verified but coverage-immiscible:** the free
  plan's two leagues (Danish Superliga + Scottish Premiership) are **0.32%**
  of our captured fixture universe (§5.3).
- **Seed addendum (ClubElo) is currently dead as an API:** `api.clubelo.com`
  has returned 502 on every path since ≈2026-09 and registration is closed
  (§5.8). The HTML site is alive; no API donor until it reopens.

---

## 1. Verification rules actually applied

- Every quota/limit/feature claim below cites the page it came from. Where a
  provider's marketing page and its docs disagree, **docs win** and the
  conflict is stated.
- **FREE TIER** (indefinite) is distinguished from **FREE TRIAL**
  (time-boxed/credits). Trials-only = red flag = rejected (TheStatsAPI,
  Mr Doge; Sportmonks' *paid-plan* 14-day trial is separate from its genuine
  free plan and does not affect this).
- Numbers that could not be verified from a page actually fetched are marked
  **UNVERIFIED**. No shortlist candidate carries UNVERIFIED in a critical
  field (quota, card-required, predictions-on-free, ToS stance); the
  Betminer league-count discrepancy (§5.1 H) is coverage, not a critical
  field, and is resolved by probe step 2.
- No accounts were created and no keys obtained. The only live probe was the
  keyless, documented Bet Better JSON feed (§2.3).
- Last-updated signal recorded per candidate — abandoned APIs are a known
  failure class here (forebet walled 2026-06-12; ClubElo API dark ≈2026-09).

---

## 2. Search log (every query)

### 2.1 Web searches (page-relay, English only)

| # | query | notable hits |
|---|---|---|
| S1 | `api-football free plan limited seasons 2021 2023` | Reddit r/webdev 2025-05 with the literal API error `Free plans do not have access to this season, try from 2021 to 2023.`; r/sportsanalytics 2026-05-25 "free plan it's only 3 seasons '22, '23 and '24"; Highlightly 2026-06 comparison |
| S2 | `betminer rapidapi free plan requests per day limits` | betminer.co.uk pricing (5/day free); RapidAPI free-tier platform caps (docs.rapidapi.com) |
| S3 | `sportmonks football API free plan Danish Superliga Scottish Premiership limitations rate limit` | docs.sportmonks.com rate-limit page (Free: 3,000 calls/entity/hour, 2 leagues, no expiry); apibetting review; thestatsapi blog |
| S4 | `free football predictions API` | Sportmonks predictions page; betminer.co.uk; bzzoiro's own r/sportsanalytics launch thread |
| S5 | `rapidapi football prediction API free tier boggio analytics 100 requests` | boggio-analytics.com/fp-api plans (100 calls/**month**); developer.boggio-analytics.com endpoints; RapidAPI schema PDF |
| S6 | `soccer football prediction API rapidapi sportapi7 free plan daily predictions odds` | SportAPI7 ($15+ paid only); Today Football Prediction (RapidAPI); GameForecastAPI (free 10/day); Betminer; Free API Live Football Data |
| S7 | `reddit algobetting sportsanalytics free football prediction odds API 2026` | KDobrev Pinnacle odds API (free 1000 req/mo); Mr Doge (credits); bzzoiro independence quote ("Predictions do not depend on odds") |
| S8 | `soccer probability API free tier` | PredictIQ Pro; OddsPapi blog; wagerlab list |
| S9 | `football expected goals xG API free` | TheStatsAPI ($50/mo, trial only); Sportmonks xG page; bigballsdata (xG paywalled) |
| S10 | `betting tips JSON API free` | Bet Better Open Model API (keyless CC BY 4.0); Tipsxpert; Sportspage Feeds |
| S11 | `value bets API free tier` | Odds-API.io (recreational books on free); OddsPapi/SharpAPI comparisons |
| S12 | `football odds API free tier` | SportsGameOdds (free 2.5k objects/mo); SharpAPI (free 12 req/min, 2 books); OddsPapi |
| S13 | `soccer fixtures results CSV free download daily` | sporting-events.org (top-level fixtures only); TheStatsAPI WC files; fixturedownload (static) — nothing daily-league-shaped that we don't already hold via `fd` |
| S14 | `ClubElo API api.clubelo.com documentation CSV no key` | soccerdata issue #977: API 502 since ≈2026-09, moved behind auth, registration closed |
| S15 | `algorithmic football tips API feed probabilities JSON` | Sportmonks predictions (21 days ahead); footballdata.io (per-match probabilities); GameForecastAPI |
| S16 | `pinnacle odds API rapidapi dropping odds free plan KDobrev` | pinnapi (free 100 REST req/day); pinnodds; Pinnacle closed its public API 2025-07-23; KDobrev RapidAPI API (1000 req/mo free) |
| S17 | `fivethirtyeight soccer SPI predictions data github stopped updating archived` | fivethirtyeight/data README: "As of June 13, 2023, sports predictions and forecasts are no longer being updated." |
| S18 | `"bzzario" OR "bzzoiro" football prediction API free` | both spellings resolve to the same service (sports.bzzoiro.com / BSD) — no distinct "bzzario" source exists |

### 2.2 Pages fetched (relay receipts)

| # | URL | result |
|---|---|---|
| F1 | `https://www.api-football.com/pricing` | Free $0: 100 req/day, all endpoints incl. Predictions + Pre-match Odds; parenthetical: "Free plans are limited in terms of available seasons"; "No credit card required for the free version" |
| F2 | `https://www.api-football.com/faq` | 404 (page removed) |
| F3 | `https://www.api-football.com/documentation-v3` (§Introduction/Authentication) | auth header, `x-ratelimit-requests-limit/remaining` (daily) + `X-RateLimit-Limit/Remaining` (per-minute) headers, free `/status` call, rate-limit firewall policy |
| F4 | `https://betminer.co.uk/documentation/` | full V3 schema: `/matches/{date}` bulk, Match Object (probabilities/predictions/odds), Match Detail (xG, HT probs), error wrapper, prediction thresholds |
| F5 | `https://betminer.co.uk/` | pricing (Free: 5 req/day, no card, full endpoint access; Full $99/mo), 1,216 competitions claim, "Since 2019", commercial-use FAQ, showcase sites |
| F6 | `https://www.sportmonks.com/football-api/pricing/` | 404 (pricing page moved) |
| F7 | `https://www.sportmonks.com/football-api/` | free plan = Danish Superliga + Scottish Premiership "full data features, no credit card and no expiry"; 2,200+ leagues; predictions+xG sample JSON |
| F8 | `https://clubelo.com/api` → redirected to homepage | site HTML alive; fixtures page carries Elo-derived 1X2 probabilities (Eerste Divisie, Argentina Clausura observed) |
| F9 | `http://api.clubelo.com/` | **403 Forbidden** on directory listing |
| F10 | `https://api.clubelo.com/Arsenal` | **fetch failed** — consistent with the 502/auth-wall report (S14) |
| F11 | `https://www.football-data.org/pricing` | Free €0: 12 competitions, 10 calls/min, fixtures+tables, scores delayed; **no predictions**; odds = €15/mo add-on |
| F12 | `https://www.thesportsdb.com/free_sports_api` | "always free at point of access"; v1 free JSON; premium $9/mo for V2/livescores; no predictions |
| F13 | `https://betbetter.world/api/` | Open Model API: no key, no signup, CC BY 4.0, CORS, 10 sports; soccer = 8 top leagues |
| F14 | `https://www.predictiqpro.com/` | Free $0/mo 100 req/day plan table; 89+ leagues; ensemble description incl. "devigged market odds" in meta-learner |
| F15 | `https://www.predictiqpro.com/docs` | `/predictions/live` bulk endpoint; "100 requests/hour on Free" (conflicts with homepage 100/day — docs win); 429 + `{"error":...}` documented; `/account/me` usage |
| F16 | `https://github.com/topics/football-api` | 194 repos — scrapers/league-specific clients wrapping the same upstreams; nothing new after upstream dedupe |
| F17 | `https://rapidapi.com/category/Sports` | **reCAPTCHA-walled** — hub crawl substituted by search-engine discovery of RapidAPI-hosted listings (S2/S5/S6/S16 + F19) |
| F18 | `https://hn.algolia.com/api/v1/search?query=football%20prediction%20API&tags=story` | Boggio Show HN 2018-03 (36 pts) — long-lived; nothing else relevant |
| F19 | `https://rapidapi.com/exquisite-exquisite-default/api/betminer` | listing live: BASIC **$0.00** / PRO $23 / ULTRA $99; 1,372 subscribers; 100% service level; 357 ms; description says **"368+ leagues"** (conflicts with site/docs — see §5.1.H) |
| F20 | `https://github.com/openfootball/football.json` | public-domain fixtures/results; auto-update commit 2026-09-22 (fresh); top leagues; no predictions |
| F21 | `https://footballdata.io/football-predictions-api/` | per-match `GET /api/v1/matches/{match_id}/probabilities`; free tier **UNVERIFIED** (pricing page not readable); per-fixture burn risk |
| F22 | `https://api.openligadb.de/index.html` | free, no key, no quota ("ohne Anmeldung, ohne API-Schlüssel, ohne Kontingent"), 60 req/min/IP, ODbL 1.0, German leagues; no predictions |
| F23 | `https://rapidapi.com/casedoweb-sXAtnI-JXY/api/today-football-prediction` | JS shell only — free plan **UNVERIFIED** |
| F24 | `https://www.gameforecastapi.com/` (via S6/S15 snippets) | free Basic: 10 req/day, 10 req/hour, 150+ leagues, 40+ markets, odds+AI predictions, RapidAPI; brand-new launch |
| F25 | `https://pinnapi.com/pinnacle-odds-api` + `/pinnacle-api-pricing` (via S16 snippets) | free tier 100 REST req/day no card, live+prematch snapshots; `/kit/v1/markets` bulk per sport; Pinnacle public API closed 2025-07-23; pages dated 2026-08-30 |

### 2.3 Unauthenticated probes

| target | method | result |
|---|---|---|
| `http://api.clubelo.com/Arsenal` | raw `curl` from checkout | `HTTP 000` — no shell egress (standing receipt; all work went through the relay) |
| `https://betbetter.world/soccer/brazil-serie-a/picks?format=json` | relay fetch (documented keyless endpoint) | **SUCCESS** — live 2026-10-02T17:29Z, 78 Brazil Serie A picks, full field set captured (§5.6) |

---

## 3. What we already hold (dedupe base — do not re-propose)

Live tips/votes (`DAILY_SOURCES`, `src/edgefactory/source_health.py`): bzzoiro,
bzzoiro_odds, zulubet, statarea, vitibet, scoutingstats, betclan,
bettingclosed, prosoccer, predictz, windrawwin, freesupertips, afootballreport,
soccervista (pending drop), betexplorer, theoddsapi, oddspapi_odds, forebet
(historical-only since 2026-06-12), plus shadow-only futbolpronosticos and
sportytrader_odds.

- **`fd` resolved:** there is no `fd` *source adapter*; "fd" is the
  **Football-Data (football-data.co.uk) CSV proof** stage of the bounded
  backfill plan — [`REMINE-PLAN.md`](REMINE-PLAN.md) records operator approval
  for "one Football-Data CSV" with Legalbet gated behind it. football-data.co.uk
  is therefore **already planned** and is NOT re-proposed below.
- **legalbet** — gated backfill candidate, already sequenced in REMINE-PLAN B1.
- **The Odds API / OddsPapi** — already our price donors; their free tiers are
  not re-hunted here.
- **forebet** — walled since 2026-06-12, backfill donor only.
- [`CANDIDATE-SOURCES.md`](CANDIDATE-SOURCES.md) rows are HTML tip sites
  (Betimate, Legalbet ES, webPronostici, Scores24, SoccerVital, Wettbasis,
  OneFootball, Football4Cast, Bundesligatrend, Wettforum, Wettpoint,
  PronosticosFutbol.ai) — a different surface (pages, not APIs) with no overlap
  with this hunt's API candidates.

**The net these candidates must fit** (measured from the committed forebet
capture, `localdata/forebet.csv.gz`, ~327.9k rows): **432 distinct league
codes**, dominated by 3rd–6th tiers and continental depth — top codes include
Us4, De5, AtL, Se4, Es5, Cz4, Br4, Hr3, Pl4, Cz3, Ar3, Rs3, Ru4, Bg3, Ro3,
Jp3, It4, plus reserves (ArR), cups (BrC, ItP, ScC) and women's competitions.
Daily card-relevant slate ≈ **40–70 fixtures** (task figure; the full donor
universe historically ran 40–500/day). This is why top-flight-only APIs score
poorly on rubric B: the board's scarcity problem is **deep-tier** coverage
(women / U21 / reserve / lower divisions), where scoutingstats is currently
the sole live voice.

---

## 4. Inventory (25 candidates)

"Free" below means an **indefinite** free tier unless marked trial/credits.
"deep" = own-page/docs receipt captured this hunt (scorecard in §5 or compact
verdict here).

| # | candidate | role | free tier (indefinite?) | predictions on free | prices on free | coverage vs our net | verdict |
|---|---|---|---|---|---|---|---|
| 1 | **Betminer** (betminer.co.uk, RapidAPI) | voice | **yes — 5 req/day, no card, instant** | **yes** — bulk `/matches/{date}` | odds in payload but **no bookmaker identity** → not a price donor under our rule | 1,216 competitions claimed (site); 500+ (docs); 368+ (listing) — probe must diff | **SHORTLIST — winner** (§5.1) |
| 2 | **API-Football / API-Sports** | voice (seed) | yes — 100 req/day, no card | yes, per-fixture `/predictions` — **but seasons 2022–2024 only** | pre-match odds endpoint listed on free — same season wall | all competitions (paid); free season window excludes 2026-27 | **REJECT as live voice; backfill-only value** (§5.2) |
| 3 | **Sportmonks free** | voice (seed) | yes — no expiry, no card, 3,000 calls/entity/hour | yes (proprietary predictions, 21 days ahead, 20+ markets) | odds are standard data types | **2 leagues = 0.32% of our captured universe** (all DK+SC = 1.57%) | **REJECT** as voice (§5.3) |
| 4 | **Football Prediction API — Boggio Analytics** (RapidAPI) | voice | yes — **100 calls/month** | yes — 1X2/BTTS/OU2.5/OU3.5/team totals; **published only 12h ahead on free** | serves avg bookie odds alongside model | 92 countries / 146 national leagues (aggregator figure) | **MAYBE** — quota headroom fails at 2× (§5.4) |
| 5 | **PredictIQ Pro** | voice | yes — 100 req/day (site) / 100 req/hour (docs; docs win), no card | yes — bulk `/predictions/live` + expected goals + best bet | bookmaker odds comparison endpoint, free | 89+ leagues incl. non-top-flight (Swiss, Turkish, Bosnian, international) | **SHORTLIST #2** — echo-test candidate (§5.5) |
| 6 | **GameForecastAPI** (RapidAPI) | voice | yes — 10 req/day, 10 req/hour | yes — 40+ markets, AI predictions | odds snapshots + history | 150+ leagues (Premier League → Libertadores) | **MAYBE** — too new; pagination UNVERIFIED |
| 7 | **Bet Better Open Model API** | voice (reference) | yes — keyless, CC BY 4.0, no rate limit documented | yes — model probabilities + fair odds (live-probed) | fair odds only (model-derived, no book) | **8 soccer top leagues** | **REJECT for our role; keep as free echo-benchmark** (§5.6) |
| 8 | **pinnapi** (Pinnacle relay) | **price** | yes — 100 REST req/day, no card | n/a | **yes — Pinnacle pre-match + live snapshots, bulk per sport** | Pinnacle soccer board (deep tiers expected; probe step) | **SHORTLIST — price pick** (§5.7) |
| 9 | KDobrev Pinnacle Odds API (RapidAPI) | price | yes — 1,000 req/month (community receipt) | n/a | Pinnacle only, pre-match + in-play | Pinnacle board | MAYBE — alternative to #8; own-page UNVERIFIED |
| 10 | SportsGameOdds | price | yes — 2.5k objects/month, 10 req/min, no card | no | 8 leagues, 9 bookmakers on free | thin on free | MAYBE — price fallback |
| 11 | SharpAPI | price | yes — 12 req/min, 2 books | no | 2 books on free | thin on free | MAYBE — price fallback |
| 12 | Odds-API.io | price | yes — recreational books only on free | no | sharp books are paid | n/a | REJECT for sharp-price need |
| 13 | SportAPI7 (RapidAPI) | data/odds | **no — paid from $15/mo** | no predictions (SofaScore-style data) | odds endpoints paid | broad | REJECT — no free tier |
| 14 | football-data.org | fixtures/results | yes — free forever, 12 comps, 10 req/min | **no** | odds = €15/mo add-on | 12 top competitions | REJECT as voice; marginal fixtures donor |
| 15 | TheSportsDB | fixtures/art | yes — free at point of access, test key | **no** | no (v2/premium extras) | broad events, shallow markets | REJECT as voice |
| 16 | OpenLigaDB | results | yes — no key, no quota, 60 req/min/IP, ODbL 1.0 | **no** | no | German leagues (bl1–bl3 + cups) | REJECT as voice; niche German results donor |
| 17 | openfootball football.json | fixtures/results | yes — public domain, no key | **no** | no | top leagues; auto-updated 2026-09-22 | REJECT as voice; fixtures donor |
| 18 | FiveThirtyEight SPI | feature/backfill | yes — CC BY 4.0 archive | **dead** — stopped 2023-06-13 | no | historical only | Backfill/feature donor only |
| 19 | ClubElo | feature donor (seed) | was free, no key | ratings (Elo) — no match predictions via API | no | broad (site shows deep tiers) | **REJECT now — API 502/auth-walled since ≈2026-09** (§5.8); recheck when registration opens |
| 20 | bigballsdata | stats | yes — 250 req/day (500 with GitHub), no card | no probabilities on free; **xG paywalled** ($19/mo) | no | top-5 leagues | REJECT as voice/xG donor |
| 21 | footballdata.io | voice | **UNVERIFIED** | yes — per-match 1X2 probabilities | no | unknown | REJECT — per-fixture burn + unverified tier |
| 22 | Today Football Prediction (RapidAPI) | voice | **UNVERIFIED** (listing is a JS shell) | daily predictions incl. "VIP" tiers | unclear | worldwide claim | REJECT — unverified, VIP-marketing shape |
| 23 | Football Betting Tips — Tipsxpert (RapidAPI) | voice | "free to use" per aggregator — **UNVERIFIED** | tips incl. correct score, corners | unclear | worldwide claim | REJECT — unverified |
| 24 | Free API Live Football Data (RapidAPI, Creativesdev) | data/odds | yes (listing claim) | "predictions" claimed | odds claimed | 2,100+ leagues claim | REJECT — solo-dev mirror, quality/uptime UNVERIFIED |
| 25 | Mr Doge API | price | **credits** — 500 one-time free credits (+20k by DM) | no | real-time odds | growing historical set | REJECT — credits = trial |

Not re-hunted (already held): The Odds API, OddsPapi, bzzoiro (tips+odds),
betexplorer, scoutingstats and the rest of `DAILY_SOURCES`; `fd`
(football-data.co.uk) is the approved REMINE-PLAN CSV proof; legalbet gated.

---

## 5. Scorecards (rubric A–H; deep candidates)

Quota-fit arithmetic (rubric E) uses our cadence: **1 morning + 1 evening run,
~40–70 fixtures/day**, with the required **2× headroom** on the baseline.

### 5.1 Betminer — WINNER (prediction voice)

Docs: [betminer.co.uk/documentation/](https://betminer.co.uk/documentation/)
(V3, base `https://betminer.p.rapidapi.com`) ·
[homepage/pricing](https://betminer.co.uk/) ·
[RapidAPI listing](https://rapidapi.com/exquisite-exquisite-default/api/betminer)

- **A. Access:** RapidAPI signup → instant free key, no approval queue
  ("Five minutes from the RapidAPI signup screen… instant access" — homepage
  FAQ). No card. RapidAPI middleman (billing/auth/analytics offloaded).
  ToS/commercial: "Is the data licensed for commercial use? **Yes, on both
  tiers**… the one thing you can't do is resell the raw API responses as a
  competing data product" (homepage FAQ). Attribution not stated as required.
- **B. Free tier exacts:** **5 requests/day** (homepage pricing: "5 requests
  per day, Full endpoint access for testing, Same data quality as paid tier,
  No credit card required"); per-minute rate on free tier UNVERIFIED (RapidAPI
  platform cap for free APIs is 1,000/hr, docs.rapidapi.com — provider may set
  lower). No monthly cap beyond the daily. **All endpoints open on free**.
  Coverage count conflicts across surfaces: homepage "1,216 active
  competitions", docs subtitle "500+ leagues", RapidAPI listing "368+ leagues"
  — no single canonical figure; probe step 2 resolves by enumeration. League
  breadth vs our deep net: plausible (site: "all major European leagues, the
  South American leagues, MLS, the African and Asian top flights, and most of
  the international cup competitions" — top-flight phrasing; deep-tier
  presence must be measured, not assumed).
- **C. Prediction surface (from the docs schema, fetched):** bulk
  `GET /matches/{date}` (and `{dateFrom}/{dateTo}` ranges) returns the whole
  day: `probabilities.home_win/draw/away_win/btts/over_15/over_25/over_35/
  fh_over_05/fh_over_15` (integers 0–100); `predictions.result` ∈ six outcomes
  (1/X/2/1X/X2/12 with stated probability thresholds), `correct_score`,
  `htft`, `btts`, `over_25`; per-match `odds` object (1X2, BTTS Y/N, O/U
  1.5/2.5/3.5, FH overs, DC 1X/12/X2) as 2-dp strings; `form` strings.
  Match-detail adds xG (`avghome/avgaway/avgtot/avgfh`), HT win probabilities,
  auto-tips, H2H, standings. Publication cadence: "Updated continuously as
  fresh data arrives" (homepage); no stated lookahead cap (unlike Boggio's
  12h). Cache TTL on `/matches/live` is 1 minute.
- **D. Price surface:** odds present in every match object **but with no
  bookmaker identity in the schema** — under our standing rule ("an
  odds-looking number without a book name is not a price donor") Betminer is a
  **voice donor only**, not a price donor. No closing-odds surface documented.
- **E. Quota-fit:** morning `GET /matches/{today}` (1 call) + evening same
  (1 call) = **2 calls/day baseline; 4/day with one retry each; 2× headroom on
  baseline = 4 ≤ 5 → PASS.** The adapter must be one-bulk-call-per-run with
  run-scoped cool-down (no retry loops). Per-match xG enrichment is **not**
  affordable on free (70 fixtures = 70 calls > 5/day) — shadow uses bulk
  fields only. **PASS** (bulk voice), **FAIL** (per-match enrichment).
- **F. Independence/echo:** "The Betminer Algorithm… a probabilistic model
  rather than a tipping service" (FAQ); the 2026 World Cup showcase ran
  "the same algorithm developers access through the API" through a
  10,000-run Monte Carlo — a self-built model surface. Value-bets are computed
  as model-probability vs odds (`Value = (probability/100) × odds − 1`), which
  implies odds are an output comparator, not necessarily a model input — but
  the docs do not state whether odds feed the probability model. **ECHO-LOW–
  MED pending the echo test** (≥30 shared settled fixtures, correlation/
  pick-agreement vs bzzoiro+zulubet+statarea and the price donors; fb-zb
  receipt to beat: 0.535 / 60.6%).
- **G. Failure modes:** documented error wrapper
  `{"success": false, "error": {"code": "MATCH_NOT_FOUND", …}}` (docs);
  RapidAPI middleman gives standard `X-RateLimit-*` response headers and 429
  bodies; no dedicated status page found (flag). Adapter requirements (mirror
  `bzzoiro_odds.py` / `betexplorer_odds.py`): single-flight fetch with
  min-interval throttle; never-raise with `diagnostics()` status vocabulary
  (`auth`/`quota`/`unavailable`/`blocked`/`error`/`empty`); zero-row days with
  status `quota`/`auth` stay **RETRYABLE**, never marked done; one retry max
  per run then run-scoped cool-down (the 2×429 pattern); hard per-run fetch
  cap; `quota_hint` diagnostics.
- **H. Red flags:** free tier is framed as "Test free, ship on Full"
  (testing positioning — but indefinite and commercially usable); coverage
  count discrepancy (1,216 vs 500+ vs 368+); odds without book identity;
  operator history says marketing pages lie about quotas (bzzoiro markets
  "No rate limits" while our odds plan 403s by evening — S18/S4 receipts), so
  the probe re-verifies the 5/day figure on the live pricing tab.

**RECOMMEND** — only candidate combining bulk-by-date predictions, a
model-built probability surface, no card, and quota headroom on free.

### 5.2 API-Football / API-SPORTS — seed FAILED live verification

Docs: [pricing](https://www.api-football.com/pricing) ·
[documentation-v3](https://www.api-football.com/documentation-v3)

- **A. Access:** register on dashboard (or RapidAPI), instant key, "No credit
  card required for the free version" (pricing page). Direct subscription
  available; RapidAPI middleman optional. ToS: standard API-Sports terms;
  automated use is the product; commercial use permitted with plan.
- **B. Free tier exacts:** **100 requests/day** (pricing page); per-minute
  limit returned via `X-RateLimit-Limit/Remaining` headers (docs,
  Authentication §Headers). All endpoints incl. Predictions and Pre-match
  Odds are listed under the Free plan. **Season range — the decisive fact:**
  the pricing page itself concedes "*(Free plans are limited in terms of
  available seasons)*" without naming them; community receipts pin the window:
  literal API error `Free plans do not have access to this season, try from
  2021 to 2023.` (r/webdev, 2025-05), later `…try from 2021 to 2024.`, and
  most recently "In free plan it's only 3 seasons '22, '23 and '24"
  (r/sportsanalytics, 2026-05-25); Highlightly's 2026-06 comparison agrees
  ("All endpoints are accessible, but historical seasons are limited"). The
  June-2026 Reddit report the operator seeded is therefore **CORRECT**; the
  "docs say current seasons" reading was a misparse of "all competitions and
  endpoints" (endpoints ≠ seasons). Current 2026-27 seasons are **not** on
  free.
- **C. Prediction surface:** `/predictions` is **per-fixture**; output
  includes advice, win/draw/lose percents, goals expectations, H2H-form
  comparison, plus league/season metadata. No bulk-by-date predictions
  endpoint.
- **D. Price surface:** pre-match `/odds` (multi-bookmaker) exists and is
  listed on free — behind the same season wall; closing odds not exposed as a
  distinct surface.
- **E. Quota-fit:** 40–70 fixtures × 2 runs = 80–140 `/predictions` calls/day;
  2× headroom = 160–280 ≫ 100 → **FAIL** even ignoring the season wall. With
  the season wall it is **FAIL for any live use**.
- **F. Independence/echo:** predictions are computed by their own comparison
  engine (form/H2H features) — ECHO-LOW as methodology, and as a **backfill
  donor for 2022–2024 settled seasons** (predictions + odds for echo-test
  datasets) it has genuine value.
- **G. Failure modes:** best-documented of any candidate — daily
  `x-ratelimit-requests-limit/remaining`, per-minute `X-RateLimit-*`,
  `429` + in-body `errors` (e.g. the `plan` error above), free `/status`
  endpoint that does not count against quota, firewall policy on abuse.
- **H. Red flags:** the season wall is silent on the pricing page's plan table
  and only visible in the parenthetical + error payloads; per-fixture quota
  burn.

**REJECT as a live voice (season wall + per-fixture burn). Catalog as a
possible 2022–2024 backfill/echo-dataset donor behind an operator key.**

### 5.3 Sportmonks free plan — verified, coverage-immiscible

Docs: [docs.sportmonks.com/v3/api/rate-limit](https://docs.sportmonks.com/v3/api/rate-limit) ·
[football-api landing](https://www.sportmonks.com/football-api/) ·
[predictions page](https://www.sportmonks.com/football-api/football-predictions-api/)

- **A. Access:** MySportmonks self-serve signup, instant token, no card, no
  expiry ("Create an account on My Sportmonks and get instant access to the
  free plan… no credit card and no expiry"). Note: the **paid** plans' 14-day
  trial is card-required and auto-charging (apibetting review) — irrelevant to
  the free plan but recorded to avoid confusion.
- **B. Free tier exacts:** "Free: 3,000 API calls / entity / hour — covers the
  Danish Superliga and Scottish Premiership, no credit card required, no
  expiry" (docs rate-limit page). **League coverage = exactly 2 leagues.**
  Measured against our net: Dk1+Sc1 = 1,064 of ~327.9k captured rows =
  **0.32%** (all Danish+Scottish codes = 5,144 = 1.57%). Predictions dataset
  covers 1,350+ of 2,200+ leagues on **paid** plans.
- **C. Prediction surface (strong, moot on free):** 20+ markets (FT result,
  first-half winner, HT/FT ×9, double chance, correct score with 19 scoreline
  buckets, BTTS, O/U, corners, value bet), published **21 days before
  kickoff, updated daily**, plus proprietary xG and per-league model accuracy
  metrics.
- **D. Price surface:** odds are standard data types on the platform; free
  scope limited to the 2 leagues.
- **E. Quota-fit:** 3,000 calls/entity/hour is effectively unlimited for us —
  **PASS**; coverage **FAIL**.
- **F. Independence/echo:** predictions are a proprietary dataset ("you will
  not find this exact dataset anywhere else") — ECHO-LOW as a voice, but the
  free slice is too small to matter. Whether market data feeds their model is
  not documented.
- **G. Failure modes:** per-entity 429 with usage in response headers,
  window "resets after 1 hour from first request", other entities still
  callable (docs rate-limit page) — clean contract for an adapter.
- **H. Red flags:** none operationally; the free plan is a demo of a €29+/mo
  product.

**REJECT as a voice. Revisit only if Danish/Scottish fixtures ever become
card-critical (they are ~0.3% of our universe).**

### 5.4 Football Prediction API — Boggio Analytics

Docs: [boggio-analytics.com/fp-api](https://boggio-analytics.com/fp-api/) ·
[developer.boggio-analytics.com](https://developer.boggio-analytics.com/getting-started/api-endpoints)

- **A. Access:** RapidAPI middleman, free Basic plan, key required. ToS via
  RapidAPI; long-lived (Show HN 2018-03).
- **B. Free tier exacts:** **"100 calls to prediction endpoint per month"**
  (their own plans page — a MONTH, not per day). Markets on free: 1X2, BTTS,
  O/U 2.5, O/U 3.5, home/away team totals 0.5/1.5. **Predictions available
  only 12h ahead on free** (48h on MEGA). Coverage: 92 countries, 146
  national leagues (aggregator figure — quirinussoft 2026-02).
- **C. Prediction surface:** `GET /api/v2/predictions` is **bulk** (next 48h,
  filterable by `iso_date`, federation, market) with probabilities,
  `home_strength/away_strength`; per-match `/predictions/{id}` returns all
  markets; `/performance-stats` publishes model accuracy.
- **D. Price surface:** re-serves **average bookie odds** per prediction
  (odds object; `avg_bookie_*` in performance stats) — book identity is
  aggregate ("average"), not a named book → weak price evidence under our
  rule.
- **E. Quota-fit:** 2 calls/day × 30.4 days = 61/month; **2× headroom =
  122 > 100 → FAIL**. A single-call-per-day cadence (30/month, 2× = 61) fits
  but collides with the 12h-ahead window and our two-run cadence.
- **F. Independence/echo:** team-strength + probability model with published
  performance stats — ECHO-LOW-MED.
- **G. Failure modes:** RapidAPI standard (429 + `X-RateLimit-*`).
- **H. Red flags:** monthly (not daily) cap; 12h lookahead on free; RapidAPI
  listing "Updated 11 months ago" (≈2025-11) — the freshest staleness signal
  in this hunt.

**MAYBE — not shortlisted. First fallback if Betminer fails its echo test,
accepting one-fetch-per-day cadence.**

### 5.5 PredictIQ Pro — shortlist #2 (echo-test candidate)

Docs: [predictiqpro.com](https://www.predictiqpro.com/) ·
[/docs](https://www.predictiqpro.com/docs)

- **A. Access:** self-serve free key, "no card required" (register page/docs).
  ToS stance: standard SaaS API; site is ad-supported; commercial terms not
  spelled out on fetched pages — treat as **personal/evaluation use until the
  operator reads their terms at registration** (probe step).
- **B. Free tier exacts:** homepage plan table says "100 requests/day";
  docs say "100 requests/hour on Free". **Docs win; both fit.** Free includes
  predictions, fixtures, odds, standings (docs feature table, all marked
  FREE). Coverage: **89+ leagues** (board observed: Swiss Super League,
  Turkish, Bosnian, Moroccan, international friendlies — non-top-flight
  breadth). Deep-tier presence vs our 432-code net: unknown, probe step.
- **C. Prediction surface:** **bulk `GET /predictions/live`** ("current live
  and upcoming match predictions — probabilities, expected goals, best bet"),
  per-match `/predictions/{id}`; list endpoints wrapped in `results` arrays.
  Calibration/Brier/log-loss published on their accuracy page (live figures:
  45.5% 3-way on 4,584 matches).
- **D. Price surface:** `/odds/{match_id}` bookmaker comparison, free tier,
  per-match (burn risk if used as a price donor — we already hold better price
  donors; not its role here).
- **E. Quota-fit:** 2–4 bulk calls/day ≪ 100/day (or 100/hour) → **PASS**
  with large margin.
- **F. Independence/echo — the whole reason it is only #2:** the model is an
  ensemble of Poisson xG (home/away), CatBoost ("reads… the market's own
  price"), LightGBM, and a meta-learner that "weighs the other four models'
  reads **alongside devigged market odds**". That is a documented
  market-derived component. **ECHO-MED-HIGH** — it may still diverge on soft
  deep-tier markets, but it must *prove* divergence: zero voice credit until
  the ≥30-fixture overlap/phi test passes. This is exactly what the shadow
  lane exists for.
- **G. Failure modes:** documented `429` + `{"error": "…"}` payloads, `401`
  for bad key, `GET /account/me` to check plan/usage — clean contract.
- **H. Red flags:** quota figure conflict (site vs docs); market-odds
  ensemble member; young product (no changelog history found).

**RECOMMEND as shadow-only echo-test voice — second shortlist slot.**

### 5.6 Bet Better Open Model API — keyless, verified live, wrong coverage

Docs: [betbetter.world/api/](https://betbetter.world/api/) · live probe in §2.3.

- **A. Access:** **no key, no signup**; licence **CC BY 4.0** with attribution
  string embedded in every payload; "no rate limit worth worrying about".
- **B. Free tier exacts:** free, period. Soccer coverage: **8 leagues** — EPL,
  La Liga, Bundesliga, Serie A, Ligue 1, MLS, Brazil Serie A, EFL
  Championship (site sport picker).
- **C. Prediction surface (probe-verified fields):** `game`, `gameTimeUtc`,
  `market` (Draw No Bet, BTTS, Head to Head, H2H 3-Way, Spread), `selection`,
  `winProbabilityPct`, `modelProbabilityPct`, `fairOdds`, `confidence`
  (LEAN/HIGH/LONG-SHOT), `verdict`, `updatedUtc`, `licence`, `attribution`.
  78 live picks observed for Brazil Serie A on 2026-10-02. Predicted-scores
  CSV per sport (`/predicted-scores/{sport}?format=csv`).
- **D. Price surface:** `fairOdds` only (model-derived), no bookmaker — not a
  price donor.
- **E. Quota-fit:** no cap documented → PASS trivially.
- **F. Independence/echo:** self-built model with published picks and graded
  results ("every result shown") — ECHO-LOW. But top-league only.
- **G. Failure modes:** plain JSON over HTTPS; no documented error contract;
  no status page.
- **H. Red flags:** coverage; picks-oriented marketing ("+$5,644 at $100 a
  pick") — treat numbers as marketing until graded independently.

**REJECT for our role (top-8 coverage; our board is already triple-covered
there and starving at deep tiers). KEEP as a free keyless benchmark voice for
future echo tests — zero integration cost.**

### 5.7 pinnapi — price-donor pick (Pinnacle relay)

Docs: [pinnapi.com](https://pinnapi.com/) ·
[/pinnacle-odds-api](https://pinnapi.com/pinnacle-odds-api) ·
[/pinnacle-api-pricing](https://pinnapi.com/pinnacle-api-pricing) (dated 2026-08-30)

- **A. Access:** free key, no card, no Pinnacle account ("Your API key is
  your only credential"). Independent relay — "Not affiliated with Pinnacle";
  Pinnacle closed its own public API 2025-07-23 (their pages). ToS stance on
  redistribution of Pinnacle prices: operator must read terms at registration
  (probe step) — relayed bookmaker data carries upstream-rights ambiguity that
  we will not paper over.
- **B. Free tier exacts:** "free tier: 100 REST requests/day, no card…
  covering live and prematch snapshots but not the drop stream" (pricing FAQ).
  Soccer among 10+ sports. League breadth = Pinnacle's soccer board, which is
  conventionally deep (2nd–4th tiers in many countries) — **must be probed
  against our 432-code net** (probe step 3).
- **C. Prediction surface:** none — this is a price source, never a vote.
- **D. Price surface:** `GET /kit/v1/markets` = **bulk snapshot of events +
  markets for a sport** (live or prematch); `/kit/v1/details` per event;
  `/kit/v1/prematch/{fixtures,markets,lines}`; no-vig fair price on alerts.
  Named book = Pinnacle (single, sharp reference).
- **E. Quota-fit:** 1–2 soccer snapshot calls/run = 2–4/day; 2× headroom =
  8 ≤ 100 → **PASS**.
- **F. Independence/echo:** n/a — price donor. It feeds the 7%
  price-corroboration gate (fixture/selection/book/freshness/sanity), the
  lane where `SCOUTINGSTATS_SOLE` vetoes come from. Pinnacle closing-quality
  prices are the sharpest sanity reference we could add for free.
- **G. Failure modes:** `GET /health` connectivity/auth check; REST 100/day;
  drop streams paid (not needed). Rate-limit response shape UNVERIFIED (probe
  step observes headers on day one).
- **H. Red flags:** "free trial" framing in places ("100 requests a day, free
  for as long as you're building") — no stated expiry, but the positioning is
  builder-trial; upstream (Pinnacle) rights ambiguity; young vendor; sibling
  site pinnodds.com with near-identical copy suggests white-label churn —
  capture raw + checksums and keep the adapter disposable.

**RECOMMEND as the free Pinnacle price corroborator (shadow ledger, 7%-gate
evidence, never a vote).**

### 5.8 Compact scorecards (remaining deep rows)

**ClubElo (feature donor, seed addendum).** A: was free/no-key. B:
`api.clubelo.com/{Club}` and `/{YYYY-MM-DD}` CSV, no quota documented. C/D:
ratings only (no predictions/odds via API). E: n/a. F: pure Elo model —
ECHO-LOW as a feature donor; the HTML site even renders Elo-derived 1X2
probabilities for deep-tier fixtures (observed: Eerste Divisie, Argentina
Clausura). G: n/a. H: **API dead** — 502 on every path since ≈2026-09,
"moved behind authentication, registration isn't open yet" (soccerdata issue
#977, 2026-09-23; our relay probes: 403 root / fetch-fail). **REJECT now;
recheck monthly — if it reopens it becomes the cheapest ECHO-LOW feature
donor available.**

**football-data.org.** Free forever, 12 competitions, 10 req/min, fixtures/
tables, delayed scores; no predictions; odds paywalled (€15/mo add-on)
(pricing page). **REJECT as voice; marginal fixtures donor for top comps.**

**TheSportsDB.** Free at point of access (v1, test key); community data; no
predictions (free-API page + premium page). **REJECT as voice.**

**OpenLigaDB.** Free, no key, no quota, 60 req/min/IP, **ODbL 1.0** licence,
German leagues, results/settlement oriented, cheap `/getlastchangedate` poll
(Swagger page). **REJECT as voice; plausible German-results settlement donor
if we ever need one — our net's German depth (De3–De6) exceeds its league
set.**

**openfootball football.json.** Public domain, no key, auto-updated
(commit 2026-09-22), top-league fixtures/results. **REJECT as voice; free
fixtures cross-check.**

**FiveThirtyEight SPI.** "As of June 13, 2023, sports predictions and
forecasts are no longer being updated" (repo README); archive CC BY 4.0 on
GitHub/Kaggle. SPI methodology (adjusted goals + shot xG + non-shot xG) is
genuinely independent — **backfill/feature donor only.**

**bigballsdata.** Free 250 req/day (500 with GitHub), no card; free tier =
scorers/standings/matches/form/box scores for big-5; **xG board is paid**
($19/mo) (their tutorial page). **REJECT as voice/xG donor.**

**GameForecastAPI.** Free 10 req/day (10 req/hour), 150+ leagues, 40+
markets, odds + AI predictions + history, RapidAPI (own site). **MAYBE** —
newest candidate in the hunt (launching now), pagination/page-size
UNVERIFIED (quota-fit for a 40–70 fixture day depends on it), zero track
record. Revisit in 3–6 months.

---

## 6. Shortlist and winner

| slot | source | role | why it survives the rubric |
|---|---|---|---|
| **1 (WINNER)** | **Betminer** | prediction voice (shadow) | bulk-by-date predictions; 5/day free ≥ 2× headroom on our 2-call cadence; no card; all endpoints on free; commercial use OK; model-built probabilities (Monte-Carlo showcase); active since 2019 with production users; RapidAPI BASIC $0 verified live on the listing |
| 2 | **PredictIQ Pro** | prediction voice (shadow, echo-test) | bulk `/predictions/live`; 100/day-or-hour free ≫ our need; published calibration; **carried explicitly to be echo-tested** because devigged market odds sit inside its ensemble |
| 3 | **pinnapi** | named-book price corroborator | free 100 REST req/day; bulk pre-match Pinnacle snapshots per sport; direct attack on the `SCOUTINGSTATS_SOLE` corroboration gap; never a vote |

**Single winner: Betminer.** It is the only free-tier candidate that clears
every critical bar at once — quota headroom (arithmetic above), bulk
endpoint, model-built probability surface, no card, indefinite free tier,
permissive commercial terms — while both alternatives carry a disqualifying
special case (PredictIQ: documented market-odds echo; pinnapi: price-only).
If Betminer's league diff (probe step 2) shows our deep tiers missing, the
voice slot falls back to **PredictIQ (echo-test pending)** and the hunt
reopens for a deep-tier voice.

**Seed findings scorecard:** #1 Betminer — verified, winner. #2 API-Football —
**FAILED** (free seasons 2022–2024; current season walled). #3 Sportmonks —
verified but rejected on coverage (0.32% net overlap). ClubElo — API dark
since ≈2026-09, rejected for now.

---

## 7. Probe plan (operator, after registering free keys — no code yet)

Standing rules for every probe: capture raw response + checksum + provenance;
never commit keys (env only); abort on 429/challenge, never escalate; each
probe day writes a `localdata/` ledger like the existing shadow builds.

### 7.1 Betminer (budget: ≤2 calls/day)

1. **Verify quota on the live pricing tab** of the RapidAPI listing
   (`…/api/betminer/pricing`): confirm the BASIC $0 plan's daily count (expect
   5/day per betminer.co.uk; if different, redo §5.1.E arithmetic before any
   adapter work).
2. **League diff (1 call):** `GET /matches/{today}` — the per-match
   `competition` object makes this double as a coverage probe. Diff observed
   competitions against our 432-code net with priority on the scarcity
   classes: Eerste Divisie, Ireland First Division, Frauen-Bundesliga,
   Norway Div 3, Brazil Carioca B2, Colombia Primera B, Paraguay Intermedia,
   Venezuela FUTVE 2, France National, Argentina Reserve. (Alternatively
   `GET /leagues`, but it costs a whole call and gives no live rows.)
3. **Schema check (same call):** confirm the docs schema in the wild —
   `probabilities.*` integers, `predictions.result` outcome classes,
   `odds.*` strings, `form` — and record the response wrapper
   (`success/data/meta`).
4. **Quota-header observation:** on each call record `X-RateLimit-*` headers
   so the adapter's quota diagnostics are grounded, not assumed.
5. **Second snapshot (1 call, evening):** same date — measures intraday
   revision behaviour (do probabilities move? is `meta.cached` set?).
6. Then, if the diff is acceptable: shadow adapter `betminer.py` (voice role,
   `can_vote=False`, zero credit) streaming alongside futbolpronosticos /
   sportytrader; echo test after ≥30 shared settled fixtures
   (correlation < 0.95, pick agreement < 95%, overlap/phi vs
   bzzoiro/zulubet/statarea and the price donors).

### 7.2 PredictIQ Pro (budget: ≤10 calls/day)

1. Register (no card); `GET /account/me` — empirically resolve the
   100/day-vs-100/hour conflict and confirm predictions/fixtures/odds are
   open on free.
2. `GET /predictions/live` — one bulk call: measure page/response size,
   field set (probabilities, expected goals, best bet), and the league mix
   vs our net (same priority leagues as §7.1.2).
3. `GET /fixtures/?status=scheduled` — check league filter ids for our deep
   tiers.
4. Read the terms at registration; record the commercial-use stance.
5. Then shadow adapter (voice role, zero credit) — the echo test is the
   decisive gate given the documented devigged-odds ensemble member; on
   failure it is retired, not retried harder.

### 7.3 pinnapi (budget: ≤10 calls/day)

1. Free key (no card); `GET /health` — connectivity/auth receipt.
2. `GET /kit/v1/markets` (soccer, prematch) — one bulk call: record event
   count, market depth, league spread vs our net, field shape (prices,
   capture timestamp, no-vig layer), and rate-limit headers.
3. Spot-check 5 fixtures shared with betexplorer: freshness and price sanity
   (7%-gate style comparison).
4. Read the terms at registration; record the stance on relaying Pinnacle
   prices and any attribution requirement.
5. Then shadow price ledger (named-book rows: fixture/market/selection/
   odds/book=Pinnacle/captured_at — the `sportytrader_odds` pattern),
   default-off corroboration, 7%-gate evidence report before any
   production role; **never a vote**.

---

## 8. Rejected at a glance (and the one-line reason)

| candidate | one-line reason |
|---|---|
| API-Football | free seasons 2022–2024 only — current season walled (plus per-fixture burn) |
| Sportmonks free | two leagues = 0.32% of our net |
| Boggio | 100 calls/month fails 2× headroom; 12h-ahead window conflicts with cadence |
| Bet Better | keyless and verified, but 8 top leagues we don't need |
| GameForecastAPI | brand-new, pagination UNVERIFIED — revisit in 3–6 months |
| KDobrev Pinnacle API | plausible but own-page UNVERIFIED (community receipt only) |
| SportsGameOdds / SharpAPI | free tiers too thin (8 leagues/9 books; 2 books) to move the corroboration needle |
| Odds-API.io | sharp books paid; free = recreational only |
| SportAPI7 | no free tier |
| TheStatsAPI | 7-day trial, then $50/mo — trials-only |
| football-data.org / TheSportsDB / OpenLigaDB / openfootball | no predictions (fixtures/results donors only) |
| 538 SPI | dead since 2023-06-13 (archive value only) |
| ClubElo | API 502/auth-walled since ≈2026-09; recheck monthly |
| footballdata.io / Today Football Prediction / Tipsxpert / Free API Live Football Data | free tier or quality UNVERIFIED; per-fixture or mirror-shaped |
| Mr Doge | one-time credits = trial |
| bigballsdata | xG paywalled; no probabilities on free |
| football-data.co.uk (`fd`) / legalbet | already planned/gated in REMINE-PLAN — not re-proposed |

---

## 9. What would change these conclusions

- Betminer's live pricing tab showing ≠5/day, or the league diff missing our
  deep tiers → voice slot falls to PredictIQ (echo-test pending) and the
  deep-tier voice hunt reopens.
- PredictIQ's echo test passing with real divergence on deep-tier fixtures →
  it becomes the primary voice and Betminer the fallback.
- ClubElo reopening registration → re-add as the ECHO-LOW feature donor.
- GameForecastAPI surviving 3–6 months with documented pagination → re-score.
- Any shortlisted source hitting auth/plan 403s like bzzoiro_odds → the
  zero-row-day RETRYABLE rule (TICKETS-OPEN §a) applies unchanged; no harder
  retrying, no alternate transport.

---

## 10. SHADOW-01 — implementation receipts and operator runbook

Implemented on branch `arena/01a0fd9e-edge-factory` (base: main `d9ddc87`).
Every new source is zero-credit shadow: per-date ledgers + health rows only,
never consensus weights, never the pick path. Adapters are inert without
their env keys (`not_run`/`cache_only`), the suite stays green, main is
unaffected.

### Task receipts

| Task | Deliverable | Receipt |
| --- | --- | --- |
| T0 per-role health verdicts | `source_health.py` `ROLE_VERDICT_SOURCES`/`_status_token` + README legend + 3 tests | commit `1988ea6` |
| T1 health rows for new sources | `DAILY_SOURCES` + `bm_/pa_/bb_` counters + tokens + 2 tests | commit `c16932b` |
| T4 Bet Better benchmark shadow | `sources/betbetter.py`, fixture, 8 tests (keyless, CC BY 4.0 provenance, cache-first, budget cap) | commit `032fadc` |
| T2 Betminer voice shadow (P0) | `sources/betminer.py`, `scripts/probe_betminer.py`, fixture, 14 tests (voice-only: odds carry no book identity) | commits `418d036`, `0840a7b` |
| T3 pinnapi price shadow | `sources/pinnapi_odds.py`, `scripts/probe_pinnapi.py`, fixture, 11 tests (same-day-only corroboration gate) | commit `25597c6` |
| T5 PredictIQ convergent tag | `CONVERGENT_SOURCES` in `source_health.py`, enforced fail-closed + 3 tests (`predictiq=echo/only`) | commit `b73c2d6` |
| Wiring into daily lane | `picks_today.py` five-source shadow capture + counters + health observations + 3 wiring tests | commit `f1f5d4f` |
| T6 docs + patch | this section, TICKETS-OPEN (c)–(g), `docs/operator/patches/daily-rapidapi-env.patch` (`git apply --check` clean) | this commit |

Suite: 948 passed (baseline 904 + 44 new; all new tests offline — transport
monkeypatched, CI never fetches, no keys in code/tests/fixtures/docs/logs).

### Operator runbook (after merge)

1. **Register keys (free, no card)**: one RapidAPI account → subscribe to
   Betminer's BASIC $0 plan → key covers any RapidAPI source. Separately
   register at pinnapi.com for its free key. Keys live in env/secrets ONLY.
2. **Add GitHub secrets**: `RAPIDAPI_KEY`, `PINNAPI_KEY`
   (Settings → Secrets and variables → Actions).
3. **Merge this PR**, then apply
   `docs/operator/patches/daily-rapidapi-env.patch` to
   `.github/workflows/daily.yml` via the GitHub web editor (or locally:
   `git apply docs/operator/patches/daily-rapidapi-env.patch` — verified
   clean against the merged tree). Commit directly to main; this repo's
   rule keeps CI file changes operator-owned.
4. **Probe once, morning, before the nightly**:
   `RAPIDAPI_KEY=… PYTHONPATH=src python scripts/probe_betminer.py`
   (costs 3 of the 5 free daily calls; records the league-count figure for
   ticket (f) and one `/matches/{date}` schema sample) and
   `PINNAPI_KEY=… python3 scripts/probe_pinnapi.py` (2 of 100; reconciles
   the REST auth mechanism and snapshot schema). Never paste key material
   anywhere; the probes sanitize it.
5. **Watch the health line** (next nightly run): new tokens
   `betminer=bm_rawN/bm_scoredN`, `pinnapi=pa_rawN/pa_matchedN`,
   `betbetter=bb_rawN/bb_scoredN`, `predictiq=echo/only`. `not_run` with a
   "key not set" blocker means step 2/3 is missing; `quota`/`unavailable`
   that persist = fail-closed abstention, ticket note, no adaptation.
6. **Two policy calls on record**:
   - **pinnapi fragility accepted**: unofficial relay, may die without
     notice; disposable adapter; when down, corroboration falls back to
     existing donors and `SCOUTINGSTATS_SOLE` keeps push=False. No
     substitution scramble.
   - **PredictIQ stays convergent-tagged**: zero voice credit permanently,
     never corroborates (enforced at registry level, ticket (d)). An
     echo-test adapter ships only on explicit operator request.

### No-secrets statement

No API keys, tokens, or credentials appear in code, tests, fixtures,
docs, commit messages, or logs in this bundle. Adapters read keys only from
`os.environ` (`RAPIDAPI_KEY`, `PINNAPI_KEY`); absent → graceful skip with
`not_run` diagnostics. Probe scripts sanitize keys from all output.

### SHADOW-02 first-contact diagnoses (2026-10-02)

- **pinnapi:** the operator panel confirmed the authenticated calls and the
  playground receipt `GET /kit/v1/markets?sport_id=2&event_type=prematch`.
  The merged adapter's `sport=soccer&mode=prematch` contract was wrong;
  SHADOW-02 changes it to `sport_id=2&event_type=prematch` while retaining
  `key=` auth. Soccer `sport_id=2` is a panel receipt; the adapter remains
  fail-closed and keeps a sanitized sample for any future schema adjustment.
- **betminer:** `betminer.p.rapidapi.com` is host-verified. An unauthenticated
  request reaches the RapidAPI gateway; the remaining variable is the
  operator account's BASIC subscription (403 class), not a host-slug change.
- **SharpAPI:** the price-shadow receipt pins the RapidAPI host to
  `sharpapi1.p.rapidapi.com`; it is default-off for promotion, named-book
  rows only, and never a vote.

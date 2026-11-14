# Provider Evidence Table — 2026-10-10

Workstream A deliverable. Per provider: transport → endpoint/schema →
supported rows → fixture/market matching → usable execution prices, with a
classification of the unresolved issue and the exact retained evidence.
Classifications, per the work order:

* **CODE-DEFECT** — demonstrated by retained evidence, repair committed.
* **ACCESS/QUOTA** — account, plan, or rate-limit blocker; retry does not
  restore permissions.
* **COVERAGE-GAP** — the provider genuinely lacks the competition/market.
* **INSUFFICIENT-EVIDENCE** — retained receipts cannot separate the candidate
  explanations; no further paid requests made without approval.

Evidence paths are relative to the repo root. Committed receipts are shown at
the commit that persisted them; `git show <sha>:<path>` reproduces the bytes.
No live workflow was run to produce this table; every row cites retained
artefacts or verbatim vendor/catalogue files already in the repo.

---

## 1. Price/odds providers

### The Odds API (theoddsapi.py)

| stage | finding |
| --- | --- |
| transport | HTTPS REST; board + per-event odds; committed capture receipts |
| endpoint/schema | `/v4/sports` catalogue (verbatim copy: `tests/data/theoddsapi_sports_2026-10-10.json`, 48 sports, fetched 2026-10-10T04:20:11Z); odds rows in `localdata/theoddsapi_odds_2026-08..10.csv.gz` (13,627 rows / 186 fixtures) |
| supported rows | named-book prices (`bookmaker` named); league→sport-key resolution with tier guards |
| fixture/market matching | identity-folded join; attempts ledger `localdata/theoddsapi_attempts_2026-10-*.json` (first-attempt/fail/close-fail timestamps per fixture) |
| execution prices | YES where matched — named bookmaker, timestamped capture |

Repairs and verification:

* **League aliases** (commit 918a0d94): usamajorleaguesoccer→`soccer_usa_mls`,
  portugalligaportugal→`soccer_portugal_primeira_liga`,
  belgianproleague+belgiumjupiler→`soccer_belgium_first_div`,
  chileprimeradivision→`soccer_chile_campeonato`, plus comma-form country
  guard. Evidence: the verbatim catalogue (every target key present and
  active) + the pinned expected-resolution map in
  `tests/test_theoddsapi.py::test_october_10_league_outcomes_match_the_attempt_ledger`
  (positive: `Belgium: Jupiler Pro League`→belgium_first_div;
  negative: `Scotland,Championship`→None, never `soccer_efl_champ`).
* **Argentina** (this commit): accent-fold code
  `argentinaprimeradivision` added to `LEAGUE_KEY_ALIASES` →
  `soccer_argentina_primera_division` (catalogue entry active=true).
  Positive pins: folded and unfolded spellings resolve at the ALIAS stage;
  negative pins: Primera B Metropolitana / Primera Nacional / Reserve League
  → None; twelve other countries' "Primera División" → None; `Ar1` short code
  already mapped. **Remaining gap: INSUFFICIENT-EVIDENCE** — retained odds
  archives were fetched with the generic `soccer` key only, so no retained
  row proves the provider lists Argentine top-flight events under that key
  (event placement). `Argentina,Clausura` stays unmapped: the catalogue does
  not say Clausura is inside the key, and probing would be a paid request.
* **Verified non-gaps** (do not "repair"): York–Northampton under
  `soccer_england_league2` and Grazer AK–Salzburg under `soccer_austria_bundesliga`
  are correct keys with genuinely absent events → **COVERAGE-GAP**, evidenced
  in the 2026-10-10 attempt ledger.

Residual: 63 candidates → 36 attempted → 0 added on 2026-10-10, skips
{priced: 21, retry_cooldown: 6}, unmatched 36 = 33 league-not-covered + 3
no-event (run-38027657811 receipt) → the 33 are **COVERAGE-GAP** pending
league-by-league catalogue review; the 3 no-event are **COVERAGE-GAP**.

### PinnAPI (pinnapi_odds.py)

| stage | finding |
| --- | --- |
| transport | HTTPS REST, RapidAPI-style key header |
| endpoint/schema | vendor-documented: prematch prices live in `event.periods.num_0` — `money_line{home,draw,away}`, `spreads`, `totals{points,over,under,max}`, `team_total`; events list carries NO markets key; dedicated `/kit/v1/prematch/fixtures\|markets\|lines`; `since=` incremental (pinnapi.com/docs, pinnodds.com/docs; corroborated by github.com/AlpinAPI/pinnacle-api) |
| supported rows | 1x2 from money_line, totals→`ou_<line>`; spreads/team_total deliberately NOT converted |
| fixture/market matching | events carry `participants` names; drop reasons recorded (`money_line_without_prices`, `outcome_inactive`, …) |
| execution prices | YES where money_line present — Pinnacle named book |

* Classification of the former "0 rows" issue: **CODE-DEFECT (repaired)**,
  commit 13021ffc. Evidence: vendor docs + parser
  `tests/fixtures/pinnapi_prematch_documented.json` (vendor-documented
  evidence). Positive fixture: periods payload → 1x2/totals rows.
  Negative behaviour: teams-only payload → `events_without_market_payload`;
  money_line all-None → `money_line_without_prices` (never a silent pass).
  `tests/fixtures/pinnapi_soccer_prematch.json` is SYNTHETIC and is never
  cited as vendor evidence.
* Residual: live placement still pending a quota-permitted capture window
  (**ACCESS/QUOTA**, do not multiply requests).

### SharpAPI (sharpapi_odds.py)

| stage | finding |
| --- | --- |
| transport | HTTPS REST via `sharpapi1.p.rapidapi.com`; MAX_CALLS_PER_RUN=10; 429 cooldown (vendor docs: docs.sharpapi.io/en/quickstart; pricing receipt: 12 req/min, no-card free access — `docs/operator/SOURCE-HUNT-2026-10.md#sharpapi`) |
| endpoint/schema | flat one-row-per-selection board (`market_type`/`selection_type`/`odds_decimal`/`sportsbook`) OR nested event→bookmakers→markets; unknown shapes yield zero rows with `schema_unrecognized` + scrubbed raw sample (`parse_snapshot`) |
| supported rows | named-book prematch rows only; `is_live`/`is_stale_pregame_price`/`is_player_prop` refused at parse |
| fixture/market matching | declared `home_team`/`away_team` fields ONLY (slug orientation is proven unreliable from the captured sample: `..._kazakhstan_moldova_...` is a Moldova home fixture); card overlap counted before well-formedness; reversed listings counted separately |
| execution prices | YES in principle (named book, `odds_kind="bookmaker"`) — none currently produced |

* Oct-10 state (`localdata/source_health_2026-10-10.json`, `sharpapi_odds`):
  `status=cache_only` — the pass served a same-day shadow ledger of 2 held
  rows (`sa_raw=2`, `sa_matched=None` at capture per commit e711af81); the
  downstream join later missed both on `fixture_key_miss: 2`; the ORIGINAL
  fresh board call returned a valid EMPTY row set (board_rows=0, unfiltered,
  requested_limit=1000) while the card held 63 fixtures.
* Classification: **INSUFFICIENT-EVIDENCE** on prices (an empty unfiltered
  board cannot separate "vendor board carries no prematch soccer for our
  slate" from a transient empty page; no raw sample of a non-empty board is
  retained) + an identity-join gap on its 2 cached rows (the receipt keeps
  `board_team_names` exactly so this can be settled without loosening the
  matcher). Parser itself: no defect demonstrated — parse behaviour is pinned
  by tests (cache honesty, e711af81). Next step requires one quota-permitted
  fresh capture on a live day (**ACCESS-bounded**, not taken without
  approval).

### OddsPapi (oddspapi_odds.py)

| stage | finding |
| --- | --- |
| transport | HTTPS REST, key pool with per-key day quotas; retry-after honoured |
| endpoint/schema | `/fixtures` (identity: participant names) + `/odds` (no participant names — identity MUST come from the fixtures call); `EXPECTED_PARSE_SKIPS={outcome_inactive, market_inactive, alt_line_skipped, internal_feed_bookmaker}` |
| supported rows | prematch 1x2/totes named-book rows |
| fixture/market matching | fixture-id join via /fixtures; participant-name vocabulary census persisted (`localdata/source_health/odds_vocabulary/`) |
| execution prices | YES where captured — `localdata/oddspapi_odds_2026-10.csv.gz` 193,120 rows but only 2026-10-03→10-04 |

* Classification of current zero-coverage: **ACCESS/QUOTA** — board call 429
  with day quota exhausted (`localdata/oddspapi_capture_2026-10-10.json`:
  status quota, http_status 429, attempted 0, Retry-After 3600 retained;
  commit feacfaeb made the whole capture STOP on quota/auth — exactly one
  odds call per fixture before stopping). No repair possible client-side;
  retry does not restore quota.

### BetMiner (betminer.py)

| stage | finding |
| --- | --- |
| transport | RapidAPI host `betminer.p.rapidapi.com` v3 (vendor documentation read: `/matches/{date}`, wrapper `{success,data,meta}`) |
| endpoint/schema | adapter matches the vendor's documented contract exactly |
| supported rows | probabilities home/draw/away/btts/over_15/25/35/fh_*; odds 2dp strings; `provider_average` rows never execution-eligible |
| fixture/market matching | date-bucket join |
| execution prices | NO (provider-average provenance by design) |

* Daily probes `localdata/betminer_probe_2026-10-*.json`: HTTP 404 with
  provider body `{"message":"Endpoint '/matches/2026-10-10' does not exist"}`,
  classified `http_404_endpoint_contract` (10-10 probe shown; same shape on
  prior days). The documented endpoint 404s **provider-side** while the
  adapter matches the vendor's own documentation.
* Classification: **ACCESS/COVERAGE (provider-side)** — endpoint contract
  broken at the provider, not in the adapter. One-request probe design kept
  (no request budget multiplied). No path change made (would be guessing).

### BetBetter (betbetter.py)

| stage | finding |
| --- | --- |
| transport | cache-first `betbetter_shadow_{day}.json`; MAX_CALLS_PER_RUN=10 |
| supported rows | model FAIR prices |
| execution prices | **NO by design** — `odds_kind="fair"`, `bookmaker=None`, `price_push_eligible` gate blocks fair prices from execution lanes |

* Unmappable rows RETAINED with `canonicalization_mappable=False` (never
  dropped). Classification: no defect; the unresolved issue is **coverage
  honesty** — spread/draw-no-bet/corners/player markets must not be silently
  converted into supported markets (guards pinned by tests). Fair prices are
  never treated as executable bookmaker quotes.

### Bzzoiro (bzzoiro.py predictions; bzzoiro_odds.py odds lane)

| stage | finding |
| --- | --- |
| transport | two independent lanes (predictions vs odds), separately credentialed |
| supported rows | prediction rows (537 in warehouse from run-38027657811) while BOTH transport lanes returned 403 the same day |
| execution prices | odds lane currently blocked |

* Classification: **ACCESS** — 403s on both lanes with 537 warehouse rows
  demonstrates access was revoked/degraded, not a transport defect; retry
  repair does not restore permissions. Diagnostics keep the 3-way
  `credential_configured` contract (commit feacfaeb):
  `credential_absent_not_run` at the candidate stage is explicitly NOT proof
  the secret was absent (tested in `tests/test_credential_blocked_diagnostics.py`).
* Residual: whether the account needs re-enable is an operator action
  (**ACCESS blocker**; report only, no credential handling in chat).

### BetExplorer (betexplorer_odds.py / backfill_betexplorer.py)

| stage | finding |
| --- | --- |
| transport | HTML scrape, polite cache-first; capture receipts daily |
| endpoint/schema | odds cache + results archives (`betexplorer_odds_2026-01..06.csv.gz` 79,925 rows →06-16; `betexplorer_results_2026-01..09.csv.gz` 107,724 rows →2026-09-01) |
| fixture/market matching | identity-folded join with squad-marker veto (commit 5d13806f) |
| execution prices | YES — named bookmaker odds with moving-quote history |

* The 2026-10-10 "503 + six quotes" concern **CLOSED**: three same-day
  committed receipts (`git show 28da08d1:localdata/betexplorer_capture_2026-10-10.json`,
  `8f3f43d2`, `6b7315b7`) all `status=ok, errors=[], be_429=0`, rows 30/33/36
  — no 503 anywhere in retained evidence. The RAAL/U23 contaminated cache
  entry was a **CODE-DEFECT** (width-9 fold collision) repaired in 5d13806f;
  the entry is kept in `localdata/betexplorer_odds_cache_2026-10-10.json` as
  evidence. Other empty cache rows (Borac–BSFK etc.) are legitimately empty
  pages, not failures.
* Fixtures: identity veto positives/negatives in the 7 tests of 5d13806f
  (squad-marker classes u17–u25/reserve/women never fold onto senior
  fixtures; senior matches unaffected).

## 2. Prediction scrapers (aggregate row; votes, not prices)

| source | state | classification |
| --- | --- | --- |
| forebet | **Live lane retired, with source-specific evidence**: `localdata/source_health_2026-10-10.json` and `-10-11.json` both show `can_fetch_today=false`, blocker "historical-only post-2026-06-12; no production pricing or weighting". The committed deep-history dataset ends 2026-06-12 because the provider stopped publishing. | COVERAGE-GAP (provider retirement evidenced) |
| zulubet | **LIVE**: 2026-10-10 health row `can_fetch_today=true, can_vote=true, can_price=true, freshness_h=0.0`; 2026-10-11 `can_fetch_today=true` with day-level blocker "fetch returned zero rows" (ordinary variance, not retirement). The committed deep-history **dataset** ends 2026-06-12 — that is a dataset cutoff of the archived csv.gz, NOT evidence the provider retired. | no unresolved defect (day-level empty slate on 10-11 is operational variance) |
| statarea | **LIVE**: both 2026-10-10 and 2026-10-11 rows `can_fetch_today=true, can_vote=true, freshness_h=0.0`. Same distinction as zulubet: dataset cutoff ≠ provider retirement. | no unresolved defect |
| sportytrader | Cloudflare-challenge walled; training_only lane with 9 disallowed prefixes honoured | ACCESS (bot wall) |
| betclan / scoutingstats | can_vote=true (health rows) | OK |
| vitibet / predictz / bettingclosed / prosoccer / windrawwin / freesupertips / afootballreport / soccervista | scheduled in capture_daily JOBS; soccervista "not reliably fetched/observed today" (health row 2026-10-10) | operational variance, no demonstrated defect |
| futbolpronosticos | raw=256 scored=79 settled {0,79} (run-38027657811) — settlement join thin | INSUFFICIENT-EVIDENCE on settlement coverage |
| predictiq | zero voice, permanent | COVERAGE-GAP |
| boggio / betminer (prediction lanes) | zero-credit shadows; betminer 404 provider-side | see BetMiner row above |

## 3. Repair → evidence → fixtures map (rule: no repair without one)

| repair (commit) | supporting response / vendor contract | positive fixture | negative fixture | safeguards preserved |
| --- | --- | --- | --- | --- |
| TheOddsAPI aliases (918a0d94) | verbatim catalogue `tests/data/theoddsapi_sports_2026-10-10.json` | Belgium/Belgium,Chile/Portugal/USA resolution pins | `Scotland,Championship`→None; Mexico Premiership preserved | tier guards; wins-or-None chains (no fallthrough) |
| Argentina alias (this commit) | catalogue entry active=true | folded + unfolded "Primera División" → argentina key | 5 Argentine lower/reserve labels → None; 12 other countries → None; Clausura → None | squad/reserve tiers never inherit; no guessed mapping |
| Squad-marker veto (5d13806f) | width-9 fold collision receipt (RAAL/U23 entry kept in betexplorer cache) | Dender–Club Brugge U23 no longer folds onto senior key | senior-pair matching unchanged (7 tests) | identity boundaries, kickoff checks untouched |
| PinnAPI periods parser (13021ffc) | pinnapi.com/docs + pinnodds.com/docs (vendor) | `tests/fixtures/pinnapi_prematch_documented.json` periods payload | teams-only payload; money_line all-None → drop reasons | spreads/team_total never converted; no schema invented from logs |
| SharpAPI cache honesty (e711af81) | cached-ledger receipt fields (provenance captured_at) | cache hit reports sa_matched=None + reason `cache_rows_pending_join` | schema_match inherited, never asserted on cache | board receipt never reused for a new card |
| Quota/auth lanes (feacfaeb) | oddspapi 429 receipt with Retry-After | board-429 → attempted=0, status=quota, receipt persisted | per-fixture 429 → exactly 1 call then stop | rate limits respected; no request multiplication |
| Shadow retention (28e42147) — **excluded from the release pre-merge** | runner receipts: BetBetter ~1,371 raw rows/day (commit-message receipt) | clean_localdata 30-day prune of the seven shadow families (kept: bounds the RUNNER working directory) | .gitignore negation REMOVED pre-merge: 30-day pruning does NOT bound Git history — committing daily raw payloads grows repository history indefinitely; nothing of these families had ever been committed, so no evidence is lost from Git | retention re-proposal requires a size policy (compact receipts, not raw payloads) |
| Test isolation (0460e045) | byte+mtime localdata manifests before/after suites | OUT_DIR/LOCALDATA patched to tmp_path | assert cache lands in tmp, not localdata | operational receipts byte-identical (sha256 c98226cf…) |

## 4. Genuine external blockers (exact)

1. **OddsPapi day-quota exhausted** (429, Retry-After 3600) — needs quota
   reset/upgrade; nothing to fix in code.
2. **BetMiner documented endpoint 404s provider-side** — needs the vendor to
   restore/route `/matches/{date}`; guessing alternative paths is prohibited.
3. **Bzzoiro 403 on both lanes** — needs account-side restoration; transport
   repair does not restore permissions.
4. **SharpAPI empty unfiltered board + no retained non-empty sample** — needs
   one quota-permitted fresh capture to settle board-vs-naming; not taken
   without approval.
5. **Forebet live lane retired** (health-blocker "historical-only
   post-2026-06-12" on 10-10 AND 10-11). **Corrected per October logs: this
   is NOT true of zulubet and statarea** — both capture live (freshness 0.0,
   can_vote true; zulubet also can_price on 10-10). An earlier draft of this
   table and of the research audit labelled all three "historical-only";
   that over-generalized a dataset cutoff of the committed archives into a
   provider claim. What ends 2026-06-12 is the committed deep-history
   dataset; the research trio panel cannot be extended into the live era
   only because **forebet** is gone.
6. **sportytrader Cloudflare wall** — training_only lane; no bypass attempted.

## 5. Research benchmark status (retained record; files not in the production diff)

The offline beyond-consensus work (feature audit + baseline experiment) was
removed from this branch's final production diff by scope-reduction commit
and is retained in Git history at:

* `752d3ee564f4fb5cbdfd1c9c9b4fdcf8e5525cda` — experiment + feature audit
* `a4de41754a96dcf351413b3bfcc8068b2bc9adb7` — corrections (goalsavg
  provenance retraction, strict/exploratory split, freeze record, paired
  deltas)
* `0749848cea1e4822562ed817eade46f90caebec8` — PR preparation record
  (superseded by the production-only PR opened from this branch)

**Availability caveat that travels with that record** (corrects the audit's
earlier framing): the archived source probabilities and provider-average
odds carry **no verifiable pre-kickoff capture timestamps** — none of the
three archives has an ingest-time column, the forebet `kickoff` field is the
scheduled kickoff (not a capture time), and `goalsavg`/extras share a
day-page fetch with the final scores. Decision-time availability is
therefore **unverified**. The experiment must be read as a **historical
benchmark** of feature groups against in-archive baselines — **not a
point-in-time validated backtest** — and its negative result (nothing beats
the devigged provider-average market baseline; consensus adds nothing beyond
market) is about this benchmark only. Note also the record's "all three
sources historical-only" framing was corrected above: only forebet has
retirement evidence; zulubet/statarea capture live, so a future zb/sa-only
live-era study is not excluded by source availability.

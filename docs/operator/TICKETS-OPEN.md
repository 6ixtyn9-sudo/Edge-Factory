# Open small tickets (OP-01 T4)

Two fenced leftovers. Ticket (a) ships a contained fix + tests; ticket (b) is a
recommendation with evidence and **no code change**. Tickets (c)–(e) are the
HUNT-01 shortlist drafts from
[`SOURCE-HUNT-2026-10.md`](SOURCE-HUNT-2026-10.md) — operator-key, probe,
shadow, echo-test, promotion-only-on-settled-evidence. **No code beyond docs
ships with them.**

---

## (a) bzzoiro_odds — a 403/auth zero-row day must be redone

**Status: FIXED (fenced), tests added.**

### Symptom

The PR #21 tripwire reported `http=403` auth/plan-denied for `bzzoiro_odds` on
**2026-10-02 and 2026-10-03** while the bzzoiro *tips* feed kept working. Those
days nevertheless reached a terminal state and were never requested again.

### Root cause (code-level)

1. `src/edgefactory/sources/bzzoiro_odds.py::_fetch_url` is documented
   *"Fetch one URL, parse rows, and print diagnostics. **Never raises**"* — on
   an `HTTPError` it records the error and returns `(0, [])`.
2. `fetch_day` therefore returns `[]` and only *labels* the condition:
   `statuses <= {401, 403}` → `_DIAG["status"] = "auth"`,
   `quota_hint = "auth_or_quota"`. No exception leaves the adapter.
3. `scripts/local_backfill.py` treated any non-exception return as success:
   the `elif source_key.endswith("_odds"): print(... 0 rows)` branch fell
   straight through to `done.add(d.isoformat())`.

Net effect: **a plan-denied 403 was indistinguishable from an empty slate**,
the date entered `state_bzzoiro_odds.json:done`, and every later run skipped
it — a permanent hole produced by an access error, not by absent fixtures.

### Fix

`scripts/local_backfill.py` now asks the adapter before closing a zero-row day:

- new module-level `RETRYABLE_ZERO_ROW_STATUSES = {auth, quota, unavailable,
  blocked, error}` and `zero_row_retry_reason(mod)`;
- a zero-row day whose `diagnostics()["status"]` is in that set is **not**
  marked done — it is recorded in `failures` with
  `zero rows with status=auth http=403 quota_hint=auth_or_quota — not an empty
  slate; day stays retryable`, printed as `ZERO-ROW NOT DONE`, and the run
  exits non-zero (the existing retryable-failure contract);
- `status=empty` (an honest quiet calendar) still completes, so quiet days
  cannot turn into infinite retries;
- adapters without `diagnostics()` are completely unchanged.

Scope guard: capture/backfill state only. No crawl expansion, no new request
budget, no vote-weight change, no production re-mine.

### Tests

`tests/test_local_backfill.py`

- `test_auth_zero_row_day_stays_retryable` — 403/auth on 10-02 + 10-03 leaves
  `done == []` and writes both failure reasons;
- `test_quota_and_unavailable_zero_rows_also_stay_open`;
- `test_genuinely_empty_slate_with_diagnostics_still_completes`;
- `test_bzzoiro_odds_auth_zero_row_is_classified_retryable` — pins the real
  adapter's `status="auth"` contract the rule keys off.

### Operator step for already-poisoned days

Days closed *before* this fix are still in `done`. Re-open only the affected
range (no crawl expansion — these are days we were denied, not new days):

```
PYTHONPATH=src python3 scripts/backfill_bzzoiro_odds.py 2026-10-02 2026-10-03
```

That helper removes the range from `state_bzzoiro_odds.json:done` and retries
through the normal path. If the 403 persists, the entitlement question is real:
confirm whether the account's plan covers `/odds/best/` at all before any
further retry budget is spent (**no harder retrying, no alternate transport**).

---

## (b) soccervista — restore or drop

**Status: RECOMMENDATION ONLY. No code change in this bundle.**

### Recommendation

**DROP from the live capture group; RETAIN the adapter, tests and relay
allowlist entry as dormant.** Re-admit only on a fresh, reproducible
`VERIFIED-from-relay` receipt. Concretely, when the operator accepts this:
remove `soccervista` from the `forebet-resilience` source group in
`scripts/capture_daily.py`, leave `src/edgefactory/sources/soccervista.py`,
`tests/test_soccervista.py` and the `relay/` allowlist untouched. One
reversible line, no deletions.

### Evidence

| # | evidence | source |
|---|---|---|
| E1 | Every transport fails: the ladder is `urllib → curl_cffi impersonation → operator relays` (`soccervista.py:216-244`); when all rungs fail it raises `SoccerVista GET failed <url>: <errors>`. Observed classification: **`soccervista \| failed \| Homepage urllib/curl SSL transport failure; retryable`** | `HANDOVER.md` source-recovery table; `src/edgefactory/sources/soccervista.py` |
| E2 | Relay rung cannot widen the surface: the allowlist grants `www.soccervista.com` **`/` only — no query string** | `relay/README.md` |
| E3 | The source is structurally thin even when healthy: **TODAY ONLY**. The legacy dated pages (`soccer_games.php`, `next_matches.php`) are gone ("File not found") and the new day picker is JS-driven with no plain-GET archive URL → capture-forward only, no backfill is possible to repair the hole | `soccervista.py` module docstring |
| E4 | It carries **no probabilities and no final scores** — pick + odds + tips only; settlement must join a separate results donor | `soccervista.py` module docstring |
| E5 | It has **zero consensus weight today**: standing instruction is "do not add ProSoccer or SoccerVista to `picks_today.py` live voting lists" | `HANDOVER.md`, 2026-09-30 addendum |
| E6 | Hardening already consumed a red-team cycle (R3 per-transport shell rejection, redundant table-check removal) — the remaining failure is transport/edge, not parsing, so there is no cheap code fix left | `docs/operator/archive/PR15-RED-TEAM.md` |

### Why not "restore"

Restoring means buying transport access the restrictions forbid. The only
remaining levers after the relay are proxies, stealth browsers or CAPTCHA
work — **all prohibited**. The lawful lever, a cooperative relay fetch, is
already in the ladder and already failing. Spending further capture budget on
a today-only, score-less, zero-weight source that cannot be backfilled (E3)
is negative expected value against the bounded budget.

### Re-admission criteria (write these down, then stop thinking about it)

1. A fresh relay receipt showing `robots.txt` + a rendered predictions table
   (not a branded shell) — i.e. `VERIFIED-from-relay`, dated.
2. Seven consecutive successful daily captures in **shadow**, zero weight.
3. A proven settlement join against an independent results donor.
4. Only then: a normal consensus-candidate review. No fast path.

### Explicitly not done here

No code change, no capture-group edit, no deletion, no crawl. The decision is
the operator's; this ticket is the evidence package.

---

## (c) Betminer — shadow prediction voice (HUNT-01 winner)

**Status: SHIPPED as zero-credit shadow (SHADOW-01, PR pending) — adapter
`src/edgefactory/sources/betminer.py` + `scripts/probe_betminer.py` +
offline test suite. Captures activate as soon as the operator sets
`RAPIDAPI_KEY` (see docs/operator/patches/daily-rapidapi-env.patch);
without it the adapter stays inert (`not_run`) and the suite stays green.**

### Why

The pipeline is corroboration-starved: bzzoiro quota-exhausts by evening,
BetExplorer self-rate-limits after 2×429, and scoutingstats is the only fully
live source (5 card picks vetoed on `SCOUTINGSTATS_SOLE` pricing on
2026-10-02). Betminer is the only free-tier API that cleared every critical
rubric bar in HUNT-01: bulk-by-date predictions, model-built probabilities,
no card, indefinite free tier, commercial use permitted.

### Quota-fit (from SOURCE-HUNT-2026-10 §5.1.E)

- Free tier: **5 requests/day**, no card, full endpoint access
  (betminer.co.uk pricing; RapidAPI listing shows a live BASIC $0 plan —
  re-verify the number on the pricing tab at subscription, step 1).
- Our cadence: 1 morning + 1 evening run = **2 bulk calls/day**
  (`GET /matches/{date}` returns the whole day incl. probabilities,
  predictions, odds objects); +1 retry each = 4/day worst case; **2× headroom
  on baseline = 4 ≤ 5 → PASS**.
- Per-match xG enrichment (`/match/{id}`) is **not affordable on free** — the
  shadow uses bulk fields only.

### Stage gates (in order, no skipping)

1. **Operator registers** the free RapidAPI key (no card). Key lives in env
   only — never in the repo, never in logs (bzzoiro_odds token pattern).
2. **Probe checks** (SOURCE-HUNT §7.1, ≤2 calls/day): confirm the live BASIC
   quota; `GET /matches/{today}` doubles as league-diff vs our 432-league net
   (priority: Eerste Divisie, Ireland First Division, Frauen-Bundesliga,
   Norway Div 3, Brazil Carioca B2, Colombia Primera B, Paraguay Intermedia,
   Venezuela FUTVE 2, France National, Argentina Reserve); confirm the docs
   schema in the wild; record `X-RateLimit-*` headers; take an evening second
   snapshot to measure intraday revision.
3. **Shadow adapter** `src/edgefactory/sources/betminer.py` — voice role,
   `can_vote=False`, zero consensus weight, streams alongside
   futbolpronosticos / sportytrader_odds as a health row + daily ledger
   (`betminer_shadow_YYYY-MM-DD.json`, raw=N). Odds rows carry **no bookmaker
   identity** in the schema → Betminer is never a price donor under the
   standing "no book name, no price donor" rule.
4. **Echo test after ≥30 shared settled fixtures**: correlation `< 0.95`,
   pick agreement `< 95%`, overlap/phi vs bzzoiro/zulubet/statarea and the
   price donors; the fb-zb receipt to beat is 0.535 / 60.6%. "Convergent" =
   zero voice credit forever, no retry-harder.
5. **Promotion only on settled evidence** — normal consensus-candidate
   review; nothing may relax the 7% price gate, quorum, or kickoff guard.

### Resilience requirements (mirror bzzoiro_odds.py / betexplorer_odds.py)

- Single-flight fetch with min-interval throttle; **max 1 retry per run**,
  then run-scoped cool-down after repeated 429s (the betexplorer 2×429
  pattern) — a 5/day budget cannot survive retry loops.
- Never-raise fetch; `diagnostics()` with the status vocabulary
  (`auth`/`quota`/`unavailable`/`blocked`/`error`/`empty`/`cooldown`) and
  `quota_hint`.
- **Zero-row days with status auth/quota stay RETRYABLE — never marked done**
  (the bzzoiro_odds 403 lesson, ticket (a)).
- Hard per-run fetch cap (default 2 calls: morning/evening bulk) — per-match
  calls are forbidden on the free tier by budget.
- No proxy / stealth / alternate transport, ever; abort on challenge.

---

## (d) PredictIQ Pro — shadow echo-test voice (HUNT-01 shortlist #2)

**Status: DEFERRED AS TAGGED (SHADOW-01 T5) — the convergent tag is enforced
at the registry level from day one (`CONVERGENT_SOURCES` in
`src/edgefactory/source_health.py`): zero voice credit permanently, never a
corroborator, even if a future adapter claims `can_vote`/`can_price` — the
daily contract refuses both (health line: `predictiq=echo/only`). An adapter
ships only if the operator wants PredictIQ as an echo-test counterparty;
until that decision this ticket stays open for the registry tag alone.**

### Why

Bulk `GET /predictions/live` (probabilities, expected goals, best bet),
published calibration, free tier ≫ our cadence, 89+ leagues incl.
non-top-flight. Carried **only** as an echo-test candidate: its own model docs
admit the ensemble meta-learner weighs reads "alongside devigged market
odds" — a documented market-derived component. Zero voice credit until it
proves divergence.

### Quota-fit (from SOURCE-HUNT-2026-10 §5.5.E)

- Free tier: 100 requests/day (homepage plan table) vs "100 requests/hour on
  Free" (docs — docs win under the standing conflict rule); both readings fit.
- Our cadence: **2–4 bulk calls/day** (morning/evening `/predictions/live`) ≪
  100 → **PASS** with large margin.

### Stage gates

1. **Operator registers** the free key (no card; env only). Read and record
   the ToS stance at registration — the fetched pages do not spell out
   commercial use.
2. **Probe checks** (SOURCE-HUNT §7.2, ≤10 calls/day): `GET /account/me` to
   resolve the quota conflict empirically; one `/predictions/live` bulk call
   to measure response size, fields, and league mix vs our net;
   `/fixtures/?status=scheduled` league ids for our deep tiers.
3. **Shadow adapter** (voice role, `can_vote=False`, zero credit) streaming
   alongside the other shadow rows; per-match `/odds/{id}` is not its role —
   we hold better price donors.
4. **Echo test after ≥30 shared settled fixtures** — this is the decisive
   gate: the market-odds ensemble member must not translate into
   market-consensus picks. On failure: retire, do not retry harder.
5. **Promotion only on settled evidence** — normal review; gates never
   weakened.

### Resilience requirements

- Same contract as (c): single-flight throttle, Retry-After-first 30→60s
  backoff, run-scoped cool-down after repeated 429s, never-raise fetch with
  `diagnostics()` statuses, zero-row auth/quota days stay RETRYABLE, hard
  per-run fetch cap (default 2–4 bulk calls), no alternate transport.

---

## (e) pinnapi — Pinnacle price corroborator (HUNT-01 shortlist #3)

**Status: SHIPPED as price shadow, corroboration default-off (SHADOW-01, PR
pending) — adapter `src/edgefactory/sources/pinnapi_odds.py` +
`scripts/probe_pinnapi.py` + offline test suite. Captures activate when the
operator sets `PINNAPI_KEY` (same patch file); without it the adapter stays
inert (`not_run`). The REST auth mechanism and snapshot schema remain
UNVERIFIED, so the parser is fail-closed with a raw sample retained in the
ledger — run the probe once before trusting `pa_raw`>0.**

### Why

Five card picks were vetoed on `SCOUTINGSTATS_SOLE` pricing — the corroboration
gap is price-side, not voice-side. pinnapi exposes bulk **Pinnacle pre-match
snapshots** (`GET /kit/v1/markets`, one call per sport) on a free tier with no
card. Pinnacle is the sharpest sanity reference; as a named-book donor it
feeds the 7% price-corroboration gate. **It is never a vote.**

### Quota-fit (from SOURCE-HUNT-2026-10 §5.7.E)

- Free tier: **100 REST requests/day**, no card, live + prematch snapshots
  (drop streams paid, not needed).
- Our cadence: **1–2 soccer snapshot calls/run = 2–4/day; 2× headroom = 8 ≤
  100 → PASS.**

### Stage gates

1. **Operator registers** the free key (no card; env only). Read and record
   the ToS stance on relaying Pinnacle prices and any attribution duty —
   "Not affiliated with Pinnacle"; upstream-rights ambiguity stays on the
   record.
2. **Probe checks** (SOURCE-HUNT §7.3, ≤10 calls/day): `GET /health`
   connectivity receipt; one bulk pre-match soccer snapshot — event count,
   market depth, league spread vs our 432-code net, field shape (prices,
   capture timestamp, no-vig layer), rate-limit headers; freshness/price
   sanity spot-check vs betexplorer on 5 shared fixtures.
3. **Shadow price ledger** in the `sportytrader_odds` pattern — named-book
   rows `fixture/market/selection/odds/book=Pinnacle/captured_at`,
   `pinn_raw=N`/`pinn_matched=N` counters as a health row; corroboration
   stays **default-off**.
4. **Echo/settled evidence**: a price donor's test is the 7%-gate evidence
   report (fixture/selection/book/freshness/sanity), the
   SPORTYTRADER-7PCT-REPORT pattern — produce it offline before any
   production role; no vote weight ever.
5. **Promotion only on settled evidence** — operator review of the offline
   report; gates never weakened.

### Resilience requirements

- Same contract as (c)/(d): single-flight throttle, backoff with
  Retry-After-first, run-scoped cool-down after repeated 429s, never-raise
  fetch with `diagnostics()` statuses, zero-row auth/quota days stay
  RETRYABLE, hard per-run fetch cap (default 2–4 bulk snapshots), no
  alternate transport. Capture raw + checksum + provenance per snapshot; the
  vendor is young (pages dated 2026-08-30, sibling site pinnodds.com) so keep
  the adapter disposable.

---

## (f) Betminer voice promotion — echo test on settled evidence (SHADOW-01)

**Status: OPEN — promotion criteria only; do not weaken.**

Triggered only after ≥2 weeks of shadow ledgers with `bm_scored` > 0 on most
days AND the probe's league-count reconciliation recorded (RapidAPI 368+ vs
site 1,216 vs docs 500+ — write the observed figure here).

### Bars (all must hold)

1. **≥30 shared settled fixtures** with at least one existing voice
   (bzzoiro, forebet-archive, zulubet, …) on the same fixture+market,
   settled by the existing warehouse path (Betminer fetches no results).
2. **Correlation < 0.95** between Betminer probabilities and the incumbent
   voice's on the shared set.
3. **Agreement < 95%** on selection (1X2/BTTS/OU2.5) over the shared set.
4. **Fetch success ≥ 80%** of scheduled capture days during the window
   (cache-first: a held date never refetches, so this counts distinct days
   with a `betminer_shadow_{day}.json` ledger).
5. Operator review of the offline echo report; promotion = explicit decision,
   never a threshold auto-flip.
6. Acceptance: corroboration independence is counted per bookmaker family, not
   per API donor. Same-book relays are one family and never add a vote.

### Standing constraints that survive promotion

- **Voice only, forever**: the payload odds carry no bookmaker identity, so
  Betminer is NEVER a price donor under the "no book name, no price donor"
  rule.
- Free-tier fragility: 5 req/day. If the tier is pulled or shrunk, the
  adapter fails closed (quota/unavailable, retryable) — abstention, not
  adaptation; re-open the hunt instead.

## (g) pinnapi price promotion — 7%-gate evidence report (SHADOW-01)

**Status: OPEN — promotion criteria only; do not weaken.**

### Bars (all must hold)

1. **≥30 shared priced fixtures** vs scoutingstats on the same day
   (fixture+market+selection), prices captured the same day (the
   `same_day_rows` freshness gate is mandatory: stale or missing → ABSTAIN).
2. **Fetch success ≥ 80%** of scheduled capture days over ≥2 weeks.
3. **Sane schema-match**: the probe receipt (`scripts/probe_pinnapi.py`)
   confirms the event/market shape and the parser is not in fail-closed
   `unavailable` state on consecutive days.
4. **Price sanity spot-check** vs betexplorer on ≥5 shared fixtures
   (Pinnacle lines within expected sharp-book tolerance).
5. Offline 7%-gate evidence report in the SPORTYTRADER-7PCT-REPORT pattern;
   operator review; promotion = explicit decision. **Never a vote.**
6. Acceptance: count independent bookmaker families, not donor APIs; pinnapi
   and KDobrev/other Pinnacle relays are the single `pinnacle` family.

### Standing constraints that survive promotion

- **Unofficial feed fragility is accepted policy**: pinnapi relays Pinnacle
  after Pinnacle closed its public API (2025-07-23); it may die without
  notice. The adapter stays disposable; when it dies, corroboration falls
  back to existing donors and `SCOUTINGSTATS_SOLE` keeps its push=False
  behavior — no substitution scramble.
- Corroboration may use ONLY same-day-fetched prices (`same_day_rows`);
  anything older abstains. This is enforced in the adapter and tested.

## (i) SharpAPI price-shadow promotion — named-book freshness evidence

**Status: OPEN — promotion criteria only; SHADOW-02 adapter shipped.**

SharpAPI (`sharpapi1.p.rapidapi.com`, RapidAPI listing receipt; free tier
approximately 12 requests/minute and two named bookmakers) is a price donor
candidate only. It is never a vote and contributes no price credit until the
operator explicitly promotes it.

Bars: (1) at least 30 same-day shared fixture/market/selection rows with an
existing approved donor; (2) at least 80% successful scheduled days over two
weeks; (3) probe schema receipt confirms named-book rows and sane prices; (4)
same-day freshness corroboration gate passes, with missing/stale rows
abstaining; and (5) operator reviews an offline 7%-gate report. Cache-first is
gap-aware: held dates are never refetched. Auth, quota, unavailable, and
zero-row days remain retryable. Acceptance also requires bookmaker-family
independence (same book through multiple donors counts once). No gate is
weakened and no automatic promotion exists.


## (j) Politeness budgets are named for the run, enforced per capture

Opened 2026-10-06 out of WO-8. **Template-wide, not a pinnapi defect.**
Nothing is broken until a caller captures more than one date per run.

Every adapter with a per-run budget calls `reset_state()` on entry to
`capture_day`, which zeroes the counter the cap measures. So the cap is
per capture; across captures there is no run-level ceiling. Verified by
walking each module's syntax tree — a line-based scan reports the opposite
answer. Six of seven adapters reset per capture (`betbetter`, `betminer`,
`boggio`, `pinnapi_odds`, `sharpapi_odds`, `sportytrader_odds`); five of
those six advertise a per-run cap.

Not patched here because the weight differs by vendor — for a 100/day
trial key it is the whole budget, for the scrapers it is a courtesy
question with a different owner — and a cap change is an operator call.
Interim: `pinnapi_odds` counts calls issued across the process and reports
the running total, so real spend is visible while behaviour is unchanged.

Acceptance: decide per adapter whether the cap is per-run or per-capture,
make the name match either way. No gate, floor, quorum or threshold.

## (k) Standing rule: a history search states its depth

Not a work item — a rule, written here because the last place it was
written was a session transcript, and those do not reach the next session.

**Any search over git history asserts the clone is not shallow first, or
states its depth in its result.** `git rev-parse --is-shallow-repository`
is the whole check.

On 2026-10-06 a sandbox clone held six commits of a 1,528-commit history;
a credential scan run inside it returned "clean" — correct for six commits
— and nothing in the result said six. Re-running reproduces the same answer
with the same confidence, so re-derivation does not catch this class. Only
the scope does, and only if it travels with the number. `DATED-CLAIMS.md`
makes a claim carry its provenance; this makes a measurement carry its
scope.

## INTAKE INBOX (standing queue)

- **KDobrev-Pinnacle** — failover peer only; family `pinnacle`; adopt only if
  pinnapi becomes fragile.
- **footballdata.io** — verify the free tier before any adapter work.
- **Odds-API.io** — SKIP; free access is recreational-only under the archived
  hunt rationale.
- **ClubElo** — recheck monthly; API remains dark/auth-walled since roughly
  2026-09.

Boggio is shipped as SHADOW-03 W3-T1. SportsGameOdds is moved out as an
explicit SKIP in `docs/operator/SGO-QUOTA.md`; neither has promotion credit.

### (l) SharpAPI league ids are not canonical across books — OPEN

Observed in the captured soccer page of 2026-10-06: the same competition
appears as `euro_quals_-_u21_championship` on one book and
`uefa_u21_euro_qualifiers` on another, within a single response. Any
league-based matching or filtering that treats the id as a stable string
will split one competition into two and under-count coverage.

Not addressed in the host/parser repair, which deliberately matches on
fixture sides rather than league. It becomes blocking the moment
`SHARPAPI_LEAGUE` is used as a server-side filter, because filtering on one
spelling silently discards the other book's prices for the same games.

### (m) SharpAPI prematch coverage is still entirely unmeasured — OPEN

The only captured page was pulled after kickoff and was 100% in-play. The
adapter now refuses live prices, which is correct, but it means the number
that decides this vendor's fate — how many of our fixtures it prices
BEFORE kickoff, with a draw and a 2.5 line — has never been observed. One
prematch capture answers it. Until then, treat all coverage estimates for
this source as unfounded.

### (n) The Odds API market list is narrowed in deployment and contradicts its own companion knob — OPEN

The workflow comment above these settings states that the `||` fallbacks
"mirror the code defaults". Four of the five do, exactly. One does not:

- code default: `h2h,totals,totals_alt,btts,team_totals,double_chance`
- deployment:   `h2h,totals`

Each market costs one credit per event against a 480/month cap, so
narrowing is a plausible deliberate economy — three markets instead of six
is a third of the spend. It is recorded as accepted in the drift audit on
that basis.

What makes it a ticket rather than a settled decision is the companion
knob. `ODDS_API_TOTAL_POINTS` is set to `1.5,2.5,3.5,4.5`, but the market
that supplies the non-main lines is `totals_alt`, which is not requested.
So the configuration filters for four goal lines while only ever fetching
one. Either the narrowing was deliberate and `ODDS_API_TOTAL_POINTS` should
be `2.5` to say so honestly, or the code default was widened later and the
deployment was never updated — the same drift that hid the SharpAPI
endpoint defect.

The repository is shallow at 13 commits, so history cannot date the change
from here and the question cannot be settled by `git log`. It needs an
operator decision, not a code change: the enhancement overlay (alternate
goal lines, both-teams-to-score, team totals, double chance) has parsing
code that production never exercises, and the credit cost of enabling it
is a budget matter.

### (o) The price board is read live-first and our fixtures fall below the cut — FIXED (diagnosis); narrowing still needs one operator setting

Observed, from the committed health record for 2026-10-06: the price
vendor answered HTTP 200 and the run recorded that every row was refused
as in-play or stale. The request was the whole global soccer board with a
100-row limit and no competition filter.

Inferred, and the reason this was a ticket rather than a fix: a board
ordered live-first with a 100-row cut would produce exactly that record
whether or not our fixtures were priced, because they would sit below the
cut and never be seen. The run could not tell the operator which had
happened — the old wording named a late capture, and the remedy for a
truncated page is the opposite of capturing later.

What shipped: the board is now measured alongside the rows that survive
it. Every capture records how many records came back, how many distinct
fixtures, how much of the board was refused and for which reasons, which
competitions were on it, and whether the page reached its own row limit.
Seven outcomes are now told apart where there were three:

- an empty slate — come back later;
- **a page truncated live-first** — narrow the request, do not wait;
- **a page truncated on player props** — the markets we bet were not on
  it; this is a market-selection problem, not a timing one;
- a board of props that was not truncated — same remedy, no cut involved;
- a board whose rows carried no usable price;
- a competition filter the server ignored — the identifier is not one it
  knows;
- a filter honoured onto an empty board — that competition had nothing on;
- a board whose market vocabulary did not map — the vocabulary moved.

Refusals are reported by group rather than summed. The first cut folded
every prematch refusal into one in-play token, so a board that was wholly
player props reported itself as live — a false statement about a board
with no live rows on it, not merely a missing distinction. When both
appear the in-play finding is reported, because it says the capture window
itself was wrong and that outranks a board carrying markets we never bet.
The per-reason split travels into the committed record alongside the
total, since a total cannot be unpicked into its causes afterwards.

What did NOT ship, deliberately: no competition identifier was chosen and
configured. Picking one blind is the precise failure this ticket warns
about — see ticket (l) — and the diagnostic that reports whether the guess
worked is the thing being delivered here. The passthrough is already wired
in the deployment and is currently empty, so **narrowing is one secret
away and needs no workflow change.** Set the competition filter secret and
the next run returns a verdict on the identifier instead of a bare zero.

Boundary of the claim: this is proved against mocked responses only. The
sandbox has no network, so no call was made to the vendor. What is proved
is that each of the five outcomes produces its own distinct, committed
record, and that the context survives the run. Whether this vendor prices
our fixtures before kickoff remains unmeasured — that is ticket (m), and
this change is what makes the next attempt readable rather than what
answers it.

Known limit: the ambiguity rule is conservative on purpose. With exactly
one competition on the board and no textual match against the request,
the verdict stays unknown rather than accusing the filter, because this
vendor spells one competition several ways inside a single response.
A filter that was genuinely rejected onto a single-competition board will
therefore read as unknown, not as rejected. That is the safe direction of
error.

### (o) follow-up — the number that decides the next move is the overlap

Observed, from the deployed configuration: the request carries sport and a
row limit only. The board is the whole world's soccer.

That makes every refusal token a statement about **other people's
fixtures**. Soccer runs continuously somewhere, so in-play rows at the top
of an unfiltered board are background, not evidence about our capture
window — the 15:20Z probe that returned fifty rows, all in-play, is that
background measured. A board of a hundred in-play Brazilian games and a
board of a hundred prop-only Japanese games are equally uninformative
about whether tonight's fixtures were quotable. None of the refusal
tokens answered the only question that decides what to do next.

So the capture now measures one more thing, before any refusal logic runs:
of the fixtures on our card for the day, how many appeared anywhere in the
returned rows. The reading splits cleanly.

- **Overlap zero** — every refusal token is a distraction, our fixtures
  were never on the page, and narrowing by competition is the whole fix.
  The verdict says so and outranks the refusal tokens.
- **Overlap non-zero** — the refusals for *those specific rows* become the
  diagnosis, and the seven-way split does the work it was built for. A
  hundred in-play strangers no longer mask the fact that our two fixtures
  were on the board as player props.

Two boundaries worth stating. Absence is only claimed against a board that
returned something; on an empty board our fixtures are trivially absent and
saying so would dress a quiet slate up as a coverage finding. And fixtures
listed with the sides the other way round are reported as their own verdict
rather than as absence, because this vendor is already known to contradict
itself about which side is at home.

The card is folded with the same team key the price join downstream uses,
handed in from the pipeline rather than reimplemented in the adapter. A
private matcher here would produce a number that looked like coverage and
quietly answered a different question.

Still mocked-only: the sandbox has no network and no call was made.

### Environment note — this sandbox resets to the branch point mid-session

Observed twice, in two independent sessions on different branches: the
working tree survives in full while the commit pointer is reset to the
branch point, so finished work appears as a large pile of uncommitted
changes and recent commits appear to have vanished.

The correct response is narrow. Fetch, confirm the work is on the remote,
and move the branch pointer back onto it with a SOFT reset, which never
touches files. A plain reset afterwards re-syncs the index. Never use a
hard reset and never clean: both destroy the only copy of anything that
was not pushed. The failure mode is silent, and the instinct under time
pressure is the destructive one, which is why it is written down here.

The practical consequence: push early. The remote is the only place two
sessions can reconcile, and in this environment it is the only copy worth
trusting.

### Carried forward, unchanged by this round

- The live price-source key still needs rotating — it was exposed in
  plaintext chat. Not a repository-history incident, so no rewrite and no
  force-push.
- Ticket (n) still needs an operator decision, not a code change.
- A dead secret reference at line 36 of the daily workflow should be
  deleted the next time that file is legitimately touched. The GitHub App
  cannot push workflow files, so it was not touched here.

## (p) Standing rule: a handover states what discriminates, not what merely correlates

Two failures in the 2026-10-06 handover round, both of the same family, both
cheap to avoid.

**A measurement without its scope travels as a general claim.** A count of
dirty files was taken in one workspace, was correct there, and was written
into a brief to be acted on first in a different one — where it was false.
Nothing in the number said "here". This is the companion to ticket (k): a
history search states its depth, and a workspace measurement states its
workspace. Re-derivation does not catch this, because re-deriving it in the
original workspace returns the same answer with the same confidence.

**A number that only moves when someone moves it cannot witness that work
landed.** The test-function floor was used as evidence that a particular
turn had survived. The floor is set by hand and was last set two merges
earlier, so it reads the same whether or not that turn landed. It answers
"has anyone gutted the suite", and nothing else. What discriminates is the
actual count, or a named symbol the work introduced:

| state | floor | actual |
|---|---|---|
| merged work only | 1471 | 1473 |
| merged work plus the follow-up turn | 1471 | 1475 |

The practical conclusion reached from the floor happened to be right, which
is the dangerous case — a wrong instrument agreeing with the truth once
teaches nothing and is not repeatable.

**The rule.** When a handover asserts that some specific work is or is not
present, it names the discriminator and shows it separating the two cases.
A hand-set threshold, a summary line, and a document's own description of
itself are all excluded, because each reports what someone last decided to
write rather than what is there.

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

### Standing constraints that survive promotion

- **Unofficial feed fragility is accepted policy**: pinnapi relays Pinnacle
  after Pinnacle closed its public API (2025-07-23); it may die without
  notice. The adapter stays disposable; when it dies, corroboration falls
  back to existing donors and `SCOUTINGSTATS_SOLE` keeps its push=False
  behavior — no substitution scramble.
- Corroboration may use ONLY same-day-fetched prices (`same_day_rows`);
  anything older abstains. This is enforced in the adapter and tested.

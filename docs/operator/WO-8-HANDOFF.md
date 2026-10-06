> # CLOSED — do not run this brief
>
> **Carried out 2026-10-06 in commit `31b81c8a`**, with follow-ups
> `8c1d9cd2`, `51d8a113`, `aeb1d210`, `7e46f804`, `6122ffa2` on branch
> `arena/95b13304-edge-factory`. Outcome and what remains unverified:
> `WO-8-PINNAPI-CONTRACT-2026-10-06.md`.
>
> **Everything below describes the code as it was before that commit and is
> now false.** The sport id is 1, authentication is the `x-portal-apikey`
> header with the query form kept as a fallback, and the credential guard
> has been reworked. Re-running this brief would be re-doing finished work
> against code that is already correct.
>
> An older copy of this file exists outside this branch (local commit
> `a4b5c75c`, never pushed) carrying no such banner. If you are reading a
> version of this document that presents the work as outstanding, it is the
> stale one — check the adapter before believing either.
>
> Kept verbatim below as the work order of record, for auditing what was
> asked against what was done.

# Work order 8 — Pinnacle (pinnapi) REST contract

You are picking this up cold. Everything you need is below; nothing depends
on a previous conversation.

## 1. What this is

`src/edgefactory/sources/pinnapi_odds.py` is a **shadow** price adapter. It
relays Pinnacle pre-match prices from an unofficial third-party feed
(pinnapi.com) into a per-date ledger. Nothing in the pick path, the
consensus, or the price-corroboration stamp reads it.

It has never returned a usable row. The reason is now known: **the adapter
is calling the API with the wrong sport and the wrong authentication
mechanism.** Both are confirmed against the vendor's own panel playground.

## 2. The defect — two things, both wrong today

**(a) Wrong sport id.** Line ~62:

```python
# Panel receipt 2026-10-02: soccer is sport_id=2 and the playground uses
# event_type=prematch. Keep the constant as a fail-safe until a future /sports
# introspection response is independently captured.
SPORT_ID = 2
```

That comment is wrong, and because it reads like a verified receipt it
froze the bug in place for four days. **Soccer is `sport_id=1`.**

**(b) Wrong auth mechanism.** `markets_url()` (line ~149) puts the key in
the query string:

```python
return BASE + "/kit/v1/markets?" + urllib.parse.urlencode({
    "sport_id": SPORT_ID, "event_type": EVENT_TYPE, "key": _api_key() or ""
})
```

The real contract, from the vendor's panel playground, is a **header**:

```
GET https://pinnapi.com/kit/v1/markets?sport_id=1&event_type=live
x-portal-apikey: <key>
```

The module docstring (lines ~23-30) states this is UNVERIFIED and that the
adapter assumes the SSE endpoints' `key=` query auth also applies to REST.
That assumption was wrong. Update that paragraph to say what is now known.

## 3. What to change — pre-authorised, do not ask

1. `SPORT_ID = 1`, overridable by env var `EDGE_FACTORY_PINNAPI_SPORT_ID`
   (follow the existing env-var style in the file).
2. Send the key as the `x-portal-apikey` **request header**. Keep the
   query-param form **only** as a fallback retried on HTTP 401, and
   **record which one actually succeeded** in the capture stats so the next
   operator does not have to guess.
3. Keep `event_type=prematch` for the pick lane. The playground example
   uses `live`; we want prematch. **If prematch returns zero rows, record
   the exact response shape in the diagnostic ledger and stop there.** Do
   not invent a parser for a payload you have not seen.
4. Delete the false "Panel receipt 2026-10-02" comment and correct the
   UNVERIFIED paragraph in the docstring.
5. Respect the existing caps — `MAX_CALLS_PER_RUN = 4`,
   `MIN_INTERVAL_S = 2.0`. Do not raise them. Trial limits are 20/min,
   100/hr, 100/day and the key is shared with a live panel.
6. Update `scripts/probe_pinnapi.py` if it builds the request itself, so
   the operator's acceptance probe exercises the same contract.

## 4. Three traps that will sink you if you miss them

**Trap 1 — the defensive guard will reject your header requests.**
`get_json()` contains:

```python
if "key=" not in url:
    raise UpstreamBlocked("pinnapi: refusing unauthenticated request")
```

Move the key to a header and *every* request fails this check. Worse, it
fails as `UpstreamBlocked`, which the adapter classifies as "vendor
unavailable" — so it will look like the feed is dead rather than like you
broke it. You must rework this guard to assert that the request carries
credentials *by whichever mechanism is in use*, not that the URL contains
`key=`. Its intent must survive: **never issue an unauthenticated
request.** `tests/test_pinnapi_odds.py::test_get_json_refuses_unauthenticated_urls`
pins the old wording and will need updating — that is legitimate here
because the contract changed, but preserve the intent and say so in your
report.

**Trap 2 — do not leak the key.**
`tests/test_pinnapi_odds.py::test_diagnostics_never_leak_the_key` must keep
passing. Moving the key out of the URL and into a header should *improve*
this, but only if you never log request headers. `_sanitize_headers()`
handles *response* headers; it is not protection for what you send.

**Trap 3 — there is no network access in this sandbox.**
You cannot call the API. Do not try, do not add proxies or retries to work
around it, and do not interpret a connection failure as a vendor problem.
Implement the contract and prove it with mocked responses
(`tests/test_pinnapi_odds.py` already has 21 tests using this pattern —
follow it). Live verification happens in a production run, not here.

## 5. Hard constraints

- **Shadow only.** Do not promote pinnapi to a price source, do not let it
  vote, do not wire it into consensus or corroboration. Parsing a payload
  the vendor actually sends is a bug fix, not a promotion.
- Do not touch settlement, staking, bank arithmetic, or any gate, floor,
  cap, quorum, threshold or veto rule.
- No new vendors or sources. Make this one work.
- Do not modify `.github/workflows/` — the GitHub App cannot push it. If a
  workflow change is needed, output the complete file and say so.

## 6. Acceptance

All three must hold:

- `python3 scripts/verify_work_order.py` → **14/14 ALL PASS**
- `python3 scripts/verify_wo7.py` → **9/9**
- Full suite → **1571 passed / 0 failed** or better (never fewer)

Plus new tests covering, at minimum:

- the request carries `x-portal-apikey`
- `sport_id=1` is sent, and the env override works
- a 401 on header auth falls back to the query form
- the stats record which auth mechanism succeeded
- a zero-row prematch response records the payload shape rather than
  silently returning nothing
- the key never appears in diagnostics

## 7. Environment

`.venv` does not persist and `pip install` is blocked at system level
(PEP 668). Build a throwaway venv:

```
python3 -m venv /tmp/wo8venv
/tmp/wo8venv/bin/pip install -q pytest curl_cffi supabase python-dateutil \
    requests beautifulsoup4 lxml pyyaml python-dotenv
/tmp/wo8venv/bin/python -m pytest -q -p no:randomly
```

Both verifier scripts run on bare `python3` and need none of this.

Other repo quirks: never use backticks inside a `git commit -m` heredoc;
`gh pr edit` is broken on this repo (Projects-classic GraphQL error) — use
`gh api -X PATCH repos/OWNER/REPO/pulls/N --input file.json`.

## 8. Reporting

Plain English. No internal identifiers or function names in prose. State
clearly which findings are **observed** and which are **inferred** — the
four-day delay on this bug was caused by an inference written down as a
receipt. Report the before/after of the request actually constructed, and
say explicitly that live behaviour is unverified from the sandbox.

## 9. Known-unknown worth stating up front

Even with this fixed, pinnapi is a trial key on an unofficial relay, and
pricing coverage across the leagues this system bets is around 11.4%. The
purpose of this work order is to find out cheaply whether this vendor is
worth anything at all — not to solve the pricing problem. If the answer is
"it returns nothing useful for our fixtures," that is a successful outcome
and should be reported as one.

---

**Outcome:** closed 2026-10-06 in `31b81c8a` and the follow-ups listed at the
top. See `WO-8-PINNAPI-CONTRACT-2026-10-06.md` for what was changed, which
findings are observed versus relayed, and what stays unverified until a live
run.

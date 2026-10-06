# WO-8 — Pinnacle relay request contract: what changed, what is still unknown

Date: 2026-10-06. Work order: `WO-8-HANDOFF.md`.
Scope: the Pinnacle price **shadow** only. No gate, floor, cap, quorum,
threshold or veto rule was touched; settlement, staking and bank arithmetic
were not touched; no source was promoted, and the shadow still never votes.

## 1. The two defects, and what kind of claim each correction is

**Wrong sport.** The adapter asked the vendor for sport 2 and had a comment
above it presenting that number as a receipt captured from the vendor's
panel on 2 October. No such capture exists anywhere in the repository. The
number was an inference dressed as an observation, which is why nobody
re-checked it for four days. It now asks for sport 1, and the comment is
gone.

- **Observed:** the old comment claimed a receipt; the repository contains
  no captured response supporting it.
- **Relayed by the operator, not independently observed here:** soccer is
  sport 1 on this vendor, per their panel playground.
- **Mitigation for the residual doubt:** the sport number is now
  overridable by environment variable, so a renumbering or a wrong relay
  costs a config change rather than a release.

**Wrong authentication.** The adapter put the key in the query string,
because the vendor's streaming documentation does that and the adapter
assumed the same applied to the REST endpoints. The docstring said plainly
that this was an assumption. The real REST contract is a request header.

- **Observed:** the old code authenticated only by query parameter, and the
  docstring recorded that as unverified.
- **Relayed by the operator, not independently observed here:** REST wants
  the key in an `x-portal-apikey` header.
- **Mitigation:** the query form was not deleted. It is retried once, and
  only when the header attempt is rejected as unauthorised. Whichever form
  answers is written into the capture record, so the next person reads the
  answer instead of re-deriving it.

## 2. The request, before and after

Before — one attempt, key in the URL:

```
GET https://pinnapi.com/kit/v1/markets?sport_id=2&event_type=prematch&key=<key>
```

After — header first, with the old form kept as a fallback used only on a
401:

```
GET https://pinnapi.com/kit/v1/markets?sport_id=1&event_type=prematch
x-portal-apikey: <key>

  ... if that is rejected as unauthorised, exactly one retry:

GET https://pinnapi.com/kit/v1/markets?sport_id=1&event_type=prematch&key=<key>
```

Any other failure (a server error, a quota wall, a rate limit) spends no
second call: only an unauthorised answer is a question about the
authentication mechanism. The per-run call budget of four and the two-second
minimum spacing are unchanged; a fallback attempt is counted against the
budget like any other call.

The pre-match window is unchanged. The vendor's playground example uses the
live window; the pick lane wants pre-match, so pre-match is what is asked
for.

## 3. The three traps

**The defensive guard (trap 1).** The guard that refused to issue an
unauthenticated request worked by looking for the key in the URL. Moving the
key into a header would have made every single request fail that check, and
fail in the category the adapter reports as "vendor unavailable" — the feed
would have looked dead rather than broken. The guard now asks the question
it was always meant to ask: does the request about to leave this process
carry the credential, by either mechanism? If not, it is refused before any
network call. The intent is intact; only the spelling changed.

One existing test pinned the old spelling and has been rewritten, with the
reason recorded in the test itself. This is disclosed deliberately: the
contract changed, so the test had to, and a reader should be able to see
that the invariant survived rather than take it on trust. A second test was
added for the case the old one used to cover — a request carrying no
credential at all is still refused.

**Key leakage (trap 2).** The key now travels in a header, which is strictly
better than a URL, but only if nothing writes headers down. Nothing does:
the response-header sanitiser was never protection for what we send, and no
sent header is logged, persisted or put in diagnostics. The capture record
stores the *name* of the auth header and which mechanism answered, never the
value. Tests assert the key appears in neither the diagnostics, the stats,
nor the ledger file written to disk, including on the path where the vendor
echoes the key back inside an error body.

**No network (trap 3).** This sandbox has no route to the vendor and no call
was made to it. Everything above is proved against mocked responses, in the
pattern the existing tests already used. As an extra check beyond mocking,
the adapter and the operator probe were both run end-to-end against a
throwaway server on the local machine that imitates the contract: one
configured to accept the header, one configured to reject it so the fallback
had to fire. Both behaved as specified. That is a test of our code, not
evidence about the vendor.

## 4. Coverage

- New and changed tests for this work order: the header is actually sent;
  sport 1 is actually requested and the override works (including a junk
  override falling back to the constant instead of sending garbage); a 401
  falls back to the query form, both when the vendor returns that status and
  when it arrives as an error; the stats record which mechanism answered,
  and record nothing when neither did; a non-401 failure does not spend a
  second call; a pre-match answer with nothing usable in it records the
  shape of what arrived; the key never surfaces in diagnostics, stats or the
  ledger; the shadow role text is unchanged by the fix.
- Full suite: **1584 passed, 0 failed** (baseline was 1571).
- Work-order verifier: **14/14, ALL PASS**. Settlement verifier: **9/9**.

## 5. If it returns nothing

A 200 response that yields no usable rows now records what actually arrived
— the container types, the key names at each level, the event count, and the
named reasons rows were discarded — and stops. It does not guess at a parser
for a payload nobody has seen. That record is the deliverable in that case,
and the operator probe prints the same instruction when it sees an empty
board.

This is worth saying plainly: if the first real run shows this vendor
returns nothing useful for the fixtures this system bets, the work order has
succeeded. It was a cheap question about whether an unofficial relay on a
trial key is worth anything, not an attempt to solve pricing. Pricing
coverage across these leagues is around 11.4%, this remains a shadow, and
nothing here moves it closer to a price-corroboration role.

## 6. Unverified from here

- No live call was made. Whether the header is accepted, whether sport 1 is
  soccer on the live service, and whether a pre-match snapshot contains our
  fixtures are all unverified from this sandbox and can only be settled by a
  production run with a real key.
- The response schema remains unverified. The parser is unchanged; this work
  order changed only how the request is addressed and authenticated.
- The first run with a key will answer three things at once, and the capture
  record is built to report them without a second run: which authentication
  mechanism answered, whether the board was recognisable, and — if it was
  empty — exactly what shape it had.

## 7. Files

- `src/edgefactory/sources/pinnapi_odds.py` — sport id, header auth with a
  401-only fallback, reworked credential guard, auth record in the capture
  stats, observed-shape recording on an empty answer, corrected docstring,
  false receipt comment deleted.
- `scripts/probe_pinnapi.py` — builds its request from the shipped adapter
  rather than its own copy, so the acceptance probe cannot drift from the
  contract; tries the header first and falls back on 401; reports which
  mechanism worked; still prints no key.
- `tests/test_pinnapi_odds.py` — 34 tests (was 21).
- `docs/operator/SOURCE-HUNT-2026-10.md` — the paragraph that recorded the
  false sport-id receipt is corrected in place, labelled as the inference it
  was.

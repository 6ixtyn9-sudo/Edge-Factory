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
- Full suite: **1610 passed, 0 failed** (baseline was 1571).
- Work-order verifier: **14/14, ALL PASS**. Settlement verifier: **9/9**.

Honest accounting of that +39, because a bare suite total is a poor
acceptance number: **36** are tests written for this work order (the
Pinnacle shadow's own file went from 21 tests to 46, plus 11 for the dated
claims ledger) and **3** are the
dead-link check, which is parametrised over every markdown file in the
repository and therefore grows by one each time anyone adds a document.
This report and the filed work order are those two. An earlier draft of
this report said 1584; that figure was measured before the two documents
existed and was wrong by exactly those two.

"Never fewer than N collected" is a contract that drifts whenever someone
writes documentation. The durable form is "nothing failed, and no existing
test was deleted", and the second half of that is now enforced: the
work-order verifier counts test *functions* against a floor, and the floor
has been raised to the current count. Its limit is worth stating: a count
catches gutting, not substitution — delete-one-add-one passes it. It is a
tripwire, not a guarantee, and no substitute for reading the diff.

## 5. Review findings, and what they changed

Three questions were put to this work after the first pass. Two were real
defects and are fixed; the third was correct arithmetic worth stating.

**An empty board read exactly like an unreadable one.** Both produced zero
rows, the same status and the same message, which made the capture record
useless for the one decision it exists to support: an empty board points at
the sport id or a quiet hour, an unreadable payload points at the parser —
opposite diagnoses. Worse, the first pass had written a test asserting the
conflation was acceptable, which is the same failure the false sport-id
receipt was: an inference recorded as a finding. A zero-row answer is now
classified as one of four, each with a different next action:

| recorded as | what it means | next action |
|---|---|---|
| `error_envelope` | a 200 whose body is an error, not a board | usually the credential; read the recorded text |
| `unrecognized_shape` | no envelope we can read | parser question; capture the shape first |
| `empty_board` | readable envelope, zero fixtures | sport id, or a genuinely quiet window |
| `events_without_teams` | fixtures arrived, none named both sides | shape drift inside the event |
| `no_usable_rows` | fixtures parsed, every price discarded | read the named drop reasons |

Because zero fixtures means nothing on its own, the recorded shape now
carries the counts beside it: how many events arrived, how many named both
teams, how many carried any market block at all. The status values and their
retry semantics are unchanged — the discriminator is a new field, not a new
behaviour.

**A rejected header was re-learned on every capture.** The per-capture state
reset each time, so a second capture in the same run would have tried the
header again and spent another call discovering the same rejection. The
rejection is now remembered for the life of the run: later captures go
straight to the form that works, and the record says so — but only when the
header was actually skipped on remembered grounds, not when the rejection
was learned during that same capture. Verified end to end against a local
imitation server that rejects header auth: the first capture spends two
calls, every later one spends a single call.

**Budget arithmetic.** A fallback attempt is a real call. A capture whose
header form is rejected fetches two boards, not four; with the memory above,
subsequent captures fetch one. That is now stated in the code rather than
left to be discovered, and a test pins it.

A correction to that, found on the second look: the cap is enforced **per
capture, not per run**, despite its name — the counter is zeroed on entry to
every capture. With one capture per run, which is the only caller today, the
two are identical. Across several captures there is no run-level ceiling at
all, so a three-capture run under header rejection issues 2 + 1 + 1 calls
without ever approaching the cap. Changing a cap is not this work order's to
make, so the behaviour is untouched and the real running total is now
counted and reported instead, where the operator who owns the cap can see
it.

## 6. Second review round: a success code is not an accepted request

Two more paths would have re-entered the conflation the classification was
built to end, both found by review rather than by me.

**A 403 did not trigger the fallback.** Only 401 did. Relays like this one
use 403 for a rejected credential as readily as 401, so the discriminator
lost a branch whenever they did. Both codes now trigger the one retry. If
the cause was a plan restriction rather than the mechanism, the second
attempt answers 403 as well and the record shows both — which is itself the
answer.

**A 200 carrying an error body was filed as a parser problem.** Cheap relays
answer a rejected key with a success code and a body like
`{"error": "invalid api key"}`. It parses, it has no event collection, and
it was classified as an unreadable payload: a parser question, when the
cause is the credential. It is now a classification of its own, and — the
part that mattered most — such a response no longer records the mechanism as
having *worked*. Before the fix it reported "header replied", which through
the discriminator below reads as "authentication is fixed, the sport id may
still be wrong": the exact opposite of the truth, stated confidently. An
error body that does *not* blame the credential is still recorded as an
error envelope but is not claimed as an auth answer.

**A flaw of mine the fix exposed.** The first version of this classified the
*scrubbed* text. Redaction can delete the very words the classifier reads —
a short key redacted out of "invalid api key" leaves text that no longer
blames the credential — so the classifier was defeated by its own safety
measure. Classification now reads the raw body and only the recorded copy is
scrubbed. Verified both ways: the key never reaches the ledger, and the
classification holds regardless of key length.

## 7. Third round: the one structural guard that was available

Two of the three things raised here were not defects but follow-ups, and
both are now filed rather than done silently.

**The per-capture cap is template-wide, not a pinnacle-relay bug.** Checked
by walking each adapter's syntax tree, because a line-based scan gets it
wrong — my own first scan did, matching whichever entry point is defined
last and reporting the opposite answer. Six of seven adapters zero the
counter on entry to a capture; five of those six advertise a ceiling named
for the run. It is now ticket (j) in the open tickets, with the method and
the table, left as an operator decision because the weight differs by vendor
and changing a cap is not a bug fix's business.

**Cited receipts must now resolve.** The first failure in this sequence — a
comment reading "panel receipt 2026-10-02" that named nothing — has a cheap
mechanical guard: `docs/operator/DATED-CLAIMS.md` lists every comment in the
codebase that cites a dated observation, together with what backs it, and a
test holds the two halves together. A backing may be a repo path, which must
exist on disk, or an explicit label saying a person reported it with no
artifact. Labelling something as unbacked is a valid answer; leaving the
reader unable to tell is not.

It earned its place immediately: it found a dated claim my own grep had
missed, in the enhanced-pricing module. That one resolves. As a negative
control I re-inserted the exact comment that caused the four-day defect, and
the suite failed on it.

**What it cannot do**, stated in the ledger itself: it catches claims about
the outside world, not confident claims about our own behaviour. The second
failure in this sequence was a test docstring justifying a conflation — no
date, no receipt, no ledger entry would have stopped it. That one has no
cheap structural answer, and pretending otherwise would be the same error
one level up.

**On the auth-phrase matching:** it matches prose from a vendor whose
wording nobody has seen, and an unmatched error body gets no fallback and no
claimed mechanism. That is the fail-safe direction and it stays. A comment
at the pattern now says not to add phrases before a real run has shown the
actual wording — the scrubbed body is recorded so the first run teaches it.
Guessing more phrasings would be inventing a parser for a payload nobody has
seen, one level removed.

## 8. If it returns nothing


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

## 9. Unverified from here

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

### Read the auth-mechanism line first

It is a clean discriminator, and the zero-row classification settles what it
cannot:

| mechanism answered | rows | reading |
|---|---|---|
| header | yes | both corrections were needed; done |
| header | no | authentication was the bug, and the sport id may *still* be wrong — `empty_board` says the sport id, anything else says the parser |
| query | either | the panel guidance was wrong about REST, the original authentication was right all along, and the sport number was the only real defect |
| neither | — | key, endpoint or vendor; not our code |

A caveat on reading that table: `error_envelope` means the mechanism line is
reporting a rejection, not a success, even though the status code was 200.
Read the zero-row classification beside it, never the mechanism alone.

## 10. Files

- `src/edgefactory/sources/pinnapi_odds.py` — sport id, header auth with a
  401-only fallback remembered for the run, reworked credential guard, auth
  record in the capture stats, four-way zero-row classification with fixture
  counts, observed-shape recording on an empty answer, corrected docstring,
  false receipt comment deleted.
- `scripts/verify_work_order.py` — test-function floor raised to the current
  count, with the reason the collected-test total is the wrong contract.
- `scripts/probe_pinnapi.py` — builds its request from the shipped adapter
  rather than its own copy, so the acceptance probe cannot drift from the
  contract; tries the header first and falls back on 401; reports which
  mechanism worked; still prints no key.
- `tests/test_pinnapi_odds.py` — 46 tests (was 21).
- `docs/operator/SOURCE-HUNT-2026-10.md` — the paragraph that recorded the
  false sport-id receipt is corrected in place, labelled as the inference it
  was.
- `docs/operator/DATED-CLAIMS.md` + `tests/test_dated_claims_ledger.py` —
  every dated claim in a comment must say what backs it, and a cited path
  must resolve.
- `docs/operator/TICKETS-OPEN.md` — ticket (j), the template-wide cap.

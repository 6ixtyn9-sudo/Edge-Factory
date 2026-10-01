# Brief: why four registered 1x2 predictors return zero rows, and what to do about it

**For: a fresh agent. Read this whole file before touching anything.**

You are picking up a *scoped investigation*, not the PR it was discovered in.
Nothing in this brief authorises changes to PR #18's betting logic.

---

## 1. The situation in one paragraph

The production lane's candidate pool rests on **five** live sources —
`zulubet`, `betclan`, `vitibet`, `bzzoiro`, `prosoccer`. Four other
registered 1x2 predictors — `forebet`, `predictz`, `windrawwin`,
`soccervista` — are in the registry as `TIER_SHADOW` 1x2 voters and are
**contributing zero rows**. They look like a broader donor base than
actually exists. This is the real constraint on bet volume: thin slates,
small cards, and days where nothing qualifies. Forebet is the furthest
gone (parked, capture cache dead since 2026-06-12). The other three are
on the same trajectory.

**Your job: find out exactly why, per source, and propose the best
legitimate workaround.** Diagnosis first. Do not start writing fetch code
before you can explain each failure precisely.

---

## 2. Evidence already gathered (verify it, do not trust it)

Counts of each source in the 2026-10-01 production evidence
(`localdata/fresh_production_candidate_picks_2026-10-01.md` and
`localdata/picks_2026-10-01.json`):

```
predictz:     0        zulubet:   105
windrawwin:   0        betclan:   115
soccervista:  0        vitibet:   101
forebet:      0        bzzoiro:    57
                       prosoccer:  45
```

Run-log classifications from the official run on `926e99a`:

```
predictz     failed to fetch 2 days (runtime errors)
windrawwin   failed to fetch 1 day (runtime error)
soccervista  failed to fetch 1 day (transport validation error)
```

Code-level evidence that all four face anti-bot protection:

- `src/edgefactory/sources/soccervista.py` defines an exception whose
  docstring is *"A transport returned a shell/challenge instead of the
  predictions page."* and documents a `urllib -> curl_cffi -> operator
  relays` ladder.
- `predictz.py` and `windrawwin.py` both fall through to
  `public_relay.fetches(url)` after a direct attempt fails.
- `forebet.py` has ~77 browser/relay/challenge references versus 5–7 in
  the other three.

`curl_cffi` (TLS impersonation) is already a declared dependency.

**Caveat you must resolve:** `localdata/<source>.csv.gz` files are
**archival, not the live capture path**. `forebet.csv.gz` and
`zulubet.csv.gz` both end 2026-06-12, yet zulubet is today's top voter,
and the live sources `vitibet`/`betclan` have no `.csv.gz` at all. Find
where captures actually land before drawing any conclusion from file
staleness. The previous agent could not establish this.

---

## 3. What you must determine, per source

For each of `predictz`, `windrawwin`, `soccervista` (and `forebet` only
as a documented post-mortem — see constraints):

1. **The precise failure.** Challenge/denial page? TLS or JA3
   fingerprint rejection? HTTP 403/429? DNS or timeout? Parser break
   against changed HTML? A challenge page and a parser break look
   identical in a row count and must never be conflated.
2. **Which rung of the ladder fails.** Direct `urllib`, `curl_cffi`
   impersonation, or operator relay — and whether the relay is even
   configured in CI (`EDGE_FACTORY_RELAY_URLS` /
   `EDGE_FACTORY_RELAY_TOKEN`; see `public_relay.configured()`).
3. **Whether it ever succeeds.** Intermittent beats permanent. Walk the
   run history and generated artifacts for the last ~30 days.
4. **Whether the data is worth recovering.** A source that returns rows
   but never contributes a distinct vote is not worth fighting for.
   Check overlap with the five live sources before proposing work.

Classify each as: *blocked (anti-bot)*, *broken (parser/schema)*,
*flaky (transport)*, *misconfigured (relay/env)*, or *not worth
recovering*. Evidence for each classification, not inference from names.

---

## 4. Hard constraints — these are not negotiable

- **No paid solvers, CAPTCHA-bypass services, residential proxies,
  stealth-browser services, or anything with a recurring cost.** This has
  been refused repeatedly. Forebet is the cautionary tale: that path cost
  money and still lost.
- **Do NOT run Forebet browser diagnostics or probes.** Specifically not
  `probe=forebet_getrs`, not `probe=page_access`. Do not re-enable
  parked/degraded browser-fetch paths. `EDGE_FACTORY_FOREBET_BROWSER` stays
  `off`. Treat forebet as a written post-mortem only.
- **Refer to parked sources as "parked/degraded browser-dependent
  sources"** rather than by name where it can be avoided.
- **A challenge or denial page is never an empty day.** It must be
  reported as a transport failure. This rule already exists in the code and
  must not regress.
- **Row capture is not source validation.** Do not graduate any source
  from shadow/candidate on the strength of row counts. Evidence decides.
- **Do not force-certify sources, bypass walk-forward/certification/
  kickoff/odds/context gates, or weaken any gate to admit more data.**
- **No synthetic rows, no inferred probabilities, kickoffs, aliases or
  odds.** No generative model may produce source rows or predictions.
- **The operator does not run local commands and has no Codespaces.**
  Anything operational must work via GitHub Actions, the browser,
  Cloudflare, or Apps Script. You may use local commands for development
  and testing only.
- **Abstention is a valid outcome.** If a source cannot be recovered
  honestly, say so. Zero picks explained exactly beats manufactured
  volume. But do not stop at "no picks" when the cause is a fixable
  structural issue.

---

## 5. Where the solution space probably is

Ranked by the previous agent's reading, for you to confirm or reject:

1. **Operator-owned relays** — `public_relay` already supports multiple
   independent egress paths (Cloudflare Worker, Apps Script) via
   `EDGE_FACTORY_RELAY_URLS`. **First question: are they configured in CI
   at all?** If not, the ladder's last rung has never run and the
   "anti-bot" conclusion may be premature. This is the cheapest possible
   win and must be checked before anything else.
2. **`curl_cffi` impersonation profile** — already a dependency. Is it
   actually reached, and is its browser profile current?
3. **Different endpoint on the same origin** — a JSON or mobile endpoint
   is often unprotected where the HTML page is not. Forebet's
   `scripts/getrs.php` was exactly this shape.
4. **Replacing the source** — a different free provider with comparable
   1x2 coverage may be worth more than reviving a hostile one. Any new
   source enters as shadow/candidate and earns its way through the normal
   certification path. No shortcuts.
5. **Accepting the loss and widening elsewhere** — a legitimate outcome.
   Five live sources is the actual constraint; recovering one hostile
   scraper may matter less than adding one cooperative source.

---

## 6. Also fix, regardless of what you find

The forebet failure was **invisible for months** because nothing watched
for it. Whatever else you conclude:

- Classify blocked/degraded sources honestly in the registry so they stop
  reading as healthy shadow voters inflating the apparent donor base.
  Existing vocabulary: see `source_census.py` for `tier_note` and the
  `shadow_tier_fresh_production_eligible` / `source_tier_not_dispatchable`
  distinction. Do not invent a parallel labelling system.
- Add an invariant that flags **a registered 1x2 voter contributing zero
  rows across N consecutive runs**. Warning, not error, with the source
  named. `src/edgefactory/run_invariants.py` has the established pattern
  and ~25 existing checks to copy.

---

## 7. Repo orientation

- Branch: **`arena/01a0f2b3-edge-factory`**, PR #18. **Do not merge. Do
  not open a replacement PR. Do not push to `main`.** `origin/main` has no
  common ancestor with this branch — do not attempt to reconcile them.
- Source adapters: `src/edgefactory/sources/<name>.py`
- Relay transport: `src/edgefactory/sources/public_relay.py`
- Registry and tiers: `src/edgefactory/source_registry.py`
  (`predictz` :144, `windrawwin` :149, `soccervista` :169 — all
  `TIER_SHADOW`, `("1x2",)`)
- Read-only audit of what each source saw: `src/edgefactory/source_census.py`
  — **the census must never dispatch, promote, certify or force-enable a
  source, nor recommend weakening a gate.**
- Invariants: `src/edgefactory/run_invariants.py`,
  `scripts/check_run_invariants.py`
- Tests: `tests/` — full suite ~1411 passing, runs in ~25s. Use a venv;
  `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- **The working tree has been reset to base ~10 times.** Verify
  `git rev-parse --short HEAD` before trusting any grep, and recover with
  `git fetch origin arena/01a0f2b3-edge-factory && git reset --mixed
  FETCH_HEAD && git checkout -- .`. Commit and push early.
- Deletion safety: no `git reset --hard`, no `git clean`, no blind
  `rm -rf localdata`. Prune only provably stale generated artifacts with
  explicit paths.

---

## 8. What a good deliverable looks like

1. A per-source verdict with the evidence that supports it, including
   which rung of the transport ladder failed and why.
2. A clear answer on whether operator relays are configured in CI, since
   that may change everything.
3. A recommendation per source: recover (with the specific method),
   reclassify as degraded, or retire — with the cost and risk of each.
4. Honest registry classification plus the zero-rows invariant, landed
   with tests.
5. An explicit statement of what you could **not** determine from
   artifacts alone, and what evidence would settle it.

Do not report a source as recovered on the strength of a single
successful fetch. Do not claim validation from row counts. If the honest
answer is "this source is gone and should be retired", that is a good
outcome — say it plainly.

---

## 9. Operator direction (2026-10-01): cooperative sources first

The operator's position, which outranks anything in section 5:

> "those businesses need to protect themselves from people like me at the
> end of the day. we can also try to find more sources that work without
> us having to resort to combative means, which should be our first
> option"

**Treat non-combative sourcing as the primary strategy and evasion as the
last resort.** A source that wants to be read is worth more than one that
has to be outmanoeuvred, because it does not break again next quarter.

### A finding that reframes the problem

`robots.txt` for `predictz.com` and `windrawwin.com` was **unreachable
from this environment** — not a disallow rule, no response at all.
`robots.txt` is the one file a site publishes *for* bots. If it cannot be
fetched, the refusal is happening at the network edge before any crawl
policy is consulted.

Two consequences:

1. **The robots.txt permission question is moot.** Being permitted by a
   crawl policy you cannot even download does not help. Verify this
   independently — if a relay *can* reach `robots.txt`, that is a strong
   signal the block is egress-IP-based and the relay is the whole fix.
2. **"Fix one, fix them all" is likely correct, with a caveat.** If the
   block is edge/IP/fingerprint level, one clean egress path recovers all
   four at once. If some are parser breaks against changed HTML, those are
   separate per-source work. Determine which before promising a single fix.

### Preferred direction, in order

1. **A legitimate egress path.** Operator-owned Cloudflare Worker or Apps
   Script relay (already supported by `public_relay`). This is not
   evasion: it is the operator's own infrastructure making an ordinary
   request at an ordinary rate. Combined with honest identification and
   conservative rate limiting, it is defensible.
2. **Ask.** Several prediction sites offer feeds, APIs, or will grant
   access for non-commercial or low-volume use if contacted. Nobody
   appears to have tried. A single email can outperform months of
   transport engineering.
3. **Openly licensed data.** Evaluate free, reuse-permitted sources —
   e.g. `football-data.co.uk` (historical results and bookmaker odds,
   published for download), `openfootball`/`football.db` (open licensed
   fixtures/results), `OpenLigaDB`, `football-data.org` free tier,
   `TheSportsDB`. **Verify each one's current licence and terms yourself;
   do not trust this list.** No paid tiers, no recurring cost.
4. **Derive rather than borrow.** The lane currently depends on other
   people's *predictions*. Open data gives results, fixtures and closing
   odds in abundance — far more freely than predictions. A model trained
   in-repo on openly licensed results would be a permanently cooperative
   source that cannot be blocked, rate-limited or withdrawn.
   **It must go through the same walk-forward certification, shadow
   period and gates as any external source — no shortcuts, no
   self-certification** — and it must be deterministic, auditable code,
   not a generative component. This is the strongest long-term answer to
   a thin donor base and should be costed seriously.
5. **Retire what is gone.** A hostile source that contributes nothing is
   a liability in the registry: it inflates the apparent donor base and
   hides the real constraint. Retiring it honestly is a win, not a defeat.

### What remains forbidden

Evasion for its own sake. No paid solvers, CAPTCHA bypass, residential
proxies or stealth services. Do not hammer a site that is signalling it
does not want the traffic. If a source must be fought to be read, the
correct answer is usually to replace it.

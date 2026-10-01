# New agent brief: fix the source supply problem

Copy everything below the line into the new agent's first message.

---

You are picking up a scoped investigation in `6ixtyn9-sudo/Edge-Factory`
on branch `arena/01a0f2b3-edge-factory` (PR #18).

**Do not merge. Do not open a replacement PR. Do not push to `main`.**
`origin/main` has no common ancestor with this branch — do not try to
reconcile them. Stack your work on this branch.

Read `docs/operator/source-transport-investigation-brief.md` in full
before touching anything. Read its section 11 first: it is hard evidence
from a real run and it supersedes assumptions made earlier in the same
document.

## The problem

The betting engine is healthy. The data supply is not.

Nine-plus sources are registered as voters. Four contribute nothing, one
price source is a month stale, and the whole production lane rests on
about five live predictors. That is the real constraint on bet volume —
thin slates, small cards, and days where nothing qualifies. The previous
agent fixed the engine's reporting and gating; none of that widens the
funnel.

**Your mission: restore or replace the source supply, honestly.**

## Evidence you start from (verify, do not trust)

From the edge-firing tripwire, official run 36858371487, 2026-10-01:

```
[⚠️ STALE] forebet (core_voter):            newest row 2026-06-12
[⚠️ STALE] scoutingstats (voter_and_price): newest row 2026-09-04
[..]       predictz (shadow):               no files
[..]       windrawwin (shadow):             no files
[ok]       statarea (core_voter):           2026-10-01
[ok]       zulubet (core_voter):            2026-10-01
[ok]       vitibet (thin_voter):            2026-10-02
[ok]       betclan (partial_voter):         2026-10-01
[ok]       bzzoiro (model_voter):           2026-10-08
[ok]       afootballreport, freesupertips, bettingclosed: 2026-10-01
```

Established facts:

1. **Live captures are monthly `<source>_YYYY-MM.csv.gz`.** The bare
   `<source>.csv.gz` files are legacy. Staleness is only meaningful
   against the monthly files.
2. **Operator relays ARE configured in CI** —
   `EDGE_FACTORY_RELAY_URLS` and `EDGE_FACTORY_RELAY_TOKEN` are both set
   in the run environment. The transport ladder's last rung runs and the
   blocked sources are still blocked **through the relay**. Do not
   re-check this; start from it.
3. **`robots.txt` for `predictz.com` and `windrawwin.com` could not be
   fetched at all** — not a disallow rule, no response. The refusal is at
   the network edge, before any crawl policy is read. Permission is not
   the issue; reachability is.
4. **Every blocked source is a large English-language site**
   (`predictz`, `windrawwin`, `soccervista`, `forebet`). The clearest
   survivors include `prosoccer.gr` (Greek) and `vitibet.com` (Czech).
   One day's evidence, not a law — test it across run history.

## Work in this order

### Phase 1 — Triage, before any code

Produce a per-source verdict for every registered source, with evidence:

- **blocked** (anti-bot / edge refusal), **broken** (parser or schema
  drift), **flaky** (transport), **misconfigured**, **stale but
  reachable**, or **retire**.
- Which rung of the ladder fails: direct `urllib`, `curl_cffi`
  impersonation, or operator relay.
- Whether it ever succeeds — walk ~30 days of run history and artifacts.
- Whether its votes are worth recovering: does it overlap entirely with
  a live source, or add genuine independence?

A challenge page and a parser break both produce zero rows and must
never be conflated. Say which one you are looking at, and how you know.

### Phase 2 — `scoutingstats` first

This is the highest-priority item and it is not a prediction voter.

`scoutingstats` is `voter_and_price` and stale since 2026-09-04. It
prices selections tagged `SCOUTINGSTATS_SOLE`. The dispatch floor is now
`MIN_EDGE_TO_DISPATCH = 0.0` (negative edge vetoed, thin positive edge
allowed through to the assayer), so **a thin edge computed against a
month-old line can reach the ticket engine.** It also stores the fixture
kickoff in `captured_at` — see
`docs/operator/captured-at-followup.md`. Staleness and capture-time
proxying are two separate defects and both apply here.

Either restore its capture or retire it as a price source. Do not leave
it quietly pricing bets off a stale cache.

### Phase 3 — Cooperative sourcing (the operator's stated preference)

> "those businesses need to protect themselves from people like me at the
> end of the day. we can also try to find more sources that work without
> us having to resort to combative means, which should be our first
> option"

In priority order:

1. **Ask.** Several of these sites offer feeds or will grant low-volume
   or non-commercial access on request. Nobody has tried. One email can
   beat months of transport work.
2. **Non-English / national sources.** `prosoccer.gr` and `vitibet.com`
   are the proof of concept. Prospect Greek, Czech, Polish, Turkish,
   Spanish, Portuguese/Brazilian, Italian, Nordic and Balkan 1x2
   predictors. They are less defended *and* more independent — see below.
3. **Openly licensed data** — e.g. `football-data.co.uk`,
   `openfootball`/`football.db`, `OpenLigaDB`, `football-data.org` free
   tier, `TheSportsDB`. Verify each licence yourself. No paid tiers.
4. **Derive rather than borrow.** The lane depends on other people's
   *predictions*, which are scarce and defended. Results, fixtures and
   closing odds are abundant and openly licensed. A deterministic model
   trained in-repo on open results would be a source nobody can block,
   rate-limit or withdraw. It must pass the same walk-forward
   certification, shadow period and gates as any external source — no
   self-certification — and must be deterministic auditable code, never
   a generative component. Cost this seriously; it may be the real answer.
5. **Retire what is gone.** A dead source in the registry hides the real
   constraint.

**Independence matters as much as availability.** A rule like
`1x2_two_source_p60_unanimous` only means something if its voters are
independent. Several UK sites working from shared feeds and similar
models inflate apparent consensus and make unanimity cheaper than it
looks. Audit the current live sources for shared upstream providers and
report it even if you add nothing new.

### Phase 4 — Make the next failure visible

Forebet died in June and nothing noticed until October. Regardless of
what else you conclude:

- Reclassify dead and degraded sources honestly. `forebet` is still
  `core_voter` while four months dead. Use the existing vocabulary in
  `src/edgefactory/source_census.py` (`tier_note`,
  `shadow_tier_fresh_production_eligible`,
  `source_tier_not_dispatchable`). Do not invent a parallel label system.
- Add an invariant flagging a registered voter contributing zero rows
  across N consecutive runs, naming the source. Warning, not error.
  `src/edgefactory/run_invariants.py` has ~27 existing checks to copy.
- Explain why `soccervista` appears in the registry but not in the
  tripwire, and fix the gap.
- Confirm whether `bzzoiro`'s newest row of 2026-10-08 is legitimate
  advance fixtures or a date-parsing defect.

## Hard constraints — non-negotiable

- **No paid solvers, CAPTCHA bypass, residential proxies, stealth
  services, or anything with a recurring cost.** Refused repeatedly.
- **Do NOT run Forebet browser diagnostics or probes.** Not
  `probe=forebet_getrs`, not `probe=page_access`. Do not re-enable
  parked browser-fetch paths. `EDGE_FACTORY_FOREBET_BROWSER` stays `off`.
  Forebet is a written post-mortem only.
- **Do not hammer a site that is signalling it does not want traffic.**
  If a source must be fought to be read, replace it.
- **A challenge or denial page is never an empty day.** Report transport
  failure. This rule exists in code; do not regress it.
- **Row capture is not source validation.** No source graduates from
  shadow/candidate on row counts. Evidence decides.
- **Do not force-certify sources or bypass walk-forward, certification,
  kickoff, odds or context gates. Never lower a gate to clear a warning.**
- **No synthetic rows in production artifacts**; synthetic data only
  inside unit tests. No inferred probabilities, kickoffs, aliases, odds
  or fixture identities beyond the existing audited normalisation.
- **No generative/LLM component may produce probabilities, source rows,
  aliases, odds, labels or picks.** Deterministic auditable code only.
- **Never let a source be called validated while it has an unexplained
  reversed home/away candidate.** Squad qualifiers (women's, youth) have
  caused real mismatches — non-English sources will make this worse, so
  budget alias work per source.
- **Do not touch the betting engine.** `scripts/auto_tickets.py` remains
  sole owner of staking, ticket creation, draft/freeze, assayer controls,
  bucket P&L tripwire, selection ladder and benching. The pick engine
  emits no stake. Do not build a parallel ticket engine.
- **Abstention is success when evidence is insufficient.** Zero picks,
  explained exactly, beats manufactured volume — but do not stop at "no
  picks" when the cause is a fixable structural issue.
- **Deletion safety:** no `git reset --hard`, no `git clean`, no blind
  `rm -rf localdata`. Prune only provably stale generated artifacts with
  explicit paths. Wrong generated artifacts are deleted and regenerated,
  never migrated — no `.bak`/`.old` copies.
- **Naming:** professional production names only. No slang, jokes or
  crisis names. Refer to parked sources as "parked/degraded
  browser-dependent sources" where the name can be avoided.
- The operator does not run local commands and has no Codespaces.
  Anything operational must work via GitHub Actions, browser, Cloudflare
  or Apps Script. You may use local commands for development and testing.
- Prefer wiring into `scripts/daily.py` over workflow edits — the GitHub
  App cannot push `.github/workflows/`. If a workflow change is
  unavoidable, write a ready-to-paste patch under `docs/operator/` and
  make a test skip until it is applied.

## Repo orientation

- Adapters: `src/edgefactory/sources/<name>.py`
- Relay transport: `src/edgefactory/sources/public_relay.py`
- Registry/tiers: `src/edgefactory/source_registry.py`
- Read-only census: `src/edgefactory/source_census.py` — **must never
  dispatch, promote, certify, force-enable a source, or recommend
  weakening a gate.**
- Invariants: `src/edgefactory/run_invariants.py`,
  `scripts/check_run_invariants.py`
- Tests: `tests/` — ~1414 passing in ~25s.
  `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- `HANDOVER.md` is the single handover source of truth.
- **The working tree has been reset to base ~10 times.** Always verify
  `git rev-parse --short HEAD` before trusting a grep. Recover with
  `git fetch origin arena/01a0f2b3-edge-factory && git reset --mixed
  FETCH_HEAD && git checkout -- .`. Commit and push early. **Never force
  push** — a rebase once landed on the base commit and would have
  destroyed the branch.

## Acceptance criteria

1. A per-source verdict table with evidence, naming the failing rung and
   distinguishing blocked from broken.
2. `scoutingstats` restored or retired as a price source, with the
   staleness and `captured_at` defects addressed or explicitly scoped.
3. Honest registry classification landed, with tests — no dead source
   occupying a core role.
4. A zero-rows-across-N-runs invariant landed, with tests.
5. At least one concrete, costed proposal for widening supply, chosen
   from the cooperative options, with licence/terms verified.
6. An independence audit of the current live sources.
7. Full suite passing; report the exact count.
8. An explicit list of what you could **not** determine from artifacts
   alone, and what evidence would settle it.

Do not report a source as recovered on one successful fetch. Do not claim
validation from row counts. If the honest answer is "this source is gone,
retire it", say so plainly — that is a good outcome.

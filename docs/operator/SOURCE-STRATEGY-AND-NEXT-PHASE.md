# Source strategy and next phase

**Audience:** the supervising agent and whoever picks up source work next.
**Status:** plan + evidence. No code until the operator says so.
**Branch:** `arena/01a0f2b3-edge-factory` (PR #18). **Do not merge.**

---

## PART 0 — Builder's answers on the record

These are mine. They include my own errors, stated plainly, because the
supervising audit was right about them and a corrected record is worth
more than a defended one.

### 0.1 Question 4 — the 10-01 exclusion funnel (the deciding question)

Reproduced from the committed pick archives on both refs plus a live
replay of the ticket engine's gate chain. Commands in §5.1.

| fixture | main | branch | why the branch excluded it |
|---|---|---|---|
| Germany/Serbia | CARDED @1.25, `betexplorer_odds`, ML-META≥65 | not carded @1.20, **`scoutingstats_odds` / SCOUTINGSTATS_SOLE** | **price-integrity quarantine**, `price_push_eligible=False`; also `bucket=SKIPPED_VETO`, `veto=context VETO in ['team_h']` |
| Wales/Norway | CARDED @1.53, `betexplorer_odds`, 2WAY-UNANIMOUS≥60 | not carded @1.45, **`scoutingstats_odds` / SCOUTINGSTATS_SOLE** | **price-integrity quarantine**, `price_push_eligible=False`; `bucket=WATCHLIST_UNCORROBORATED_PRICE` |
| Envigado | CARDED @1.64, `betexplorer_odds` | not carded @1.64, `betexplorer_odds`, **no quarantine, `push_eligible=True`, PLAYABLE** | **no gate removed it.** Dropped at card assembly by the 25%-of-free-bank exposure cap: 7 playable legs, `LEGS_PER_ACCA=2`, one acca funded |
| Bnei Yehuda | CARDED @1.30 | CARDED @1.30 | — on both cards |
| Ashdod | **absent from main's universe entirely** | CARDED @1.50 | — branch-only fixture |

Gate chain totals on the branch for 2026-10-01:
`15 candidates admitted → 11 survive without quarantine → 7 survive
execution_safe → 2 carded (exposure cap)`.

**The honest acca-by-acca reading:**

- **Main acca #1 (Germany + Wales) LOST.** The branch avoided it via the
  price-integrity quarantine. **This is signal.** But note the trigger:
  the same two fixtures attached to `betexplorer_odds` on main and
  `scoutingstats_odds` on the branch. The branch refused a stale
  sole-source price. The *rule* is sound; the *trigger* was a price
  provenance difference between refs, not superior model discrimination.
- **Main acca #2 (Bnei Yehuda + Envigado) LOST. Branch (Bnei Yehuda +
  Ashdod) WON.** The only two differences: Envigado was removed by the
  **exposure cap, not by any gate**, and Ashdod **existed only in the
  branch's capture universe** (different capture hour → different slate).

**Verdict: one unit of signal, one unit of luck. The win is the luck
half.** The quarantine avoided a losing acca. The winning acca came from
an exposure cap and a data-timing accident. Yesterday's result does
**not** demonstrate that `fresh_production` beats main — the certified
lane abstained that day and contributed nothing to the card.

### 0.2 My errors, on the record

1. **I called `6597857` "green across the board."** It was not. Correct
   wording: *passed regression tests; failed the official invariant/persist
   gate in run 36881283039.* Local tests against committed artifacts are
   not an official run.
2. **I asserted `origin/main` has no common ancestor with this branch.**
   False — a shallow-clone artifact (`git merge-base` returns empty at
   depth 1). Real merge base is `da5b4f1` (2026-09-30), which **is** an
   ancestor of `origin/main`. Corrected in `HANDOVER.md` and
   `NEW-AGENT-PROMPT-sources.md` in commit `c559cb5e`. The real merge
   blocker is ~40 diverged generated state files including the bank
   ledger — a **state policy** problem, not a git problem.
3. **I shipped the candidate ladder with no edge check.** `MIN_EDGE_TO_DISPATCH`
   lives in `scripts/fresh_production.py` and governs the production lane
   only. When the lane abstains, `legacy_candidate_rows()` hands legacy
   picks to `playable_legs()`, which checks price integrity, kickoff,
   dedup and buckets but **never edge** (`grep -c MIN_EDGE
   scripts/auto_tickets.py` → `0`). Both 10-01 winning legs were
   negative-edge on their own stated probabilities (−0.0392, −0.0137).
   The supervising audit's doctrine gap is real and it is mine.

### 0.3 Positions I hold after the audit

- The candidate ladder is **not wrong, but under-labelled**. It stakes
  money off rows the lane exists to quarantine, under a
  `production_certified=False` flag that never reaches the printed slip.
- One real-money bank ledger; **three attribution streams**
  (`certified_fresh_production_pnl`, `candidate_ladder_pnl`,
  `legacy_main_pnl`). The 10-01 take-profit is mechanically real but must
  be attributed *"cycle closed by candidate-ladder legacy ticket."*
- **Main is the more dangerous active bettor** — the kickoff day/month
  parser swap is a live safety hole, not a hygiene issue.
- On current evidence **neither card should be real money** until one
  lane is designated production-of-record.

---

## PART 1 — Why the sources are the actual problem

The engine is healthy. The supply is dying. Every symptom the operator
has chased this week — thin slates, abstaining lane, small cards,
negative-edge legs surviving because nothing better exists — is
downstream of this.

### 1.1 Verified source health (run 36858371487 tripwire)

```
[⚠️ STALE] forebet (core_voter):            newest row 2026-06-12
[⚠️ STALE] scoutingstats (voter_and_price): newest row 2026-09-04
[..]       predictz (shadow):               no files, ever
[..]       windrawwin (shadow):             no files, ever
           soccervista:                     not monitored at all
[ok]       statarea, zulubet, vitibet, betclan, bzzoiro,
           afootballreport, freesupertips, bettingclosed
```

**The whole production lane rests on about five live predictors.**
Four registered 1x2 voters contribute nothing while still inflating the
apparent donor base.

**Most urgent:** `scoutingstats` is `voter_and_price` and stale since
2026-09-04 — a **price** source, not just a voter. It priced the two
Germany/Wales legs above. With `MIN_EDGE_TO_DISPATCH` now `0.0`, a thin
edge computed against a month-old line can reach the assayer. It also
stores the fixture **kickoff** in `captured_at`, so CLV against it is
meaningless. Two separate defects on one source, both live.

### 1.2 Established facts — do not re-litigate these

1. **Live captures are monthly `<source>_YYYY-MM.csv.gz`.** The bare
   `<source>.csv.gz` files are legacy deep history. `forebet.csv.gz` and
   `zulubet.csv.gz` both end 2026-06-12, yet zulubet is a top live voter —
   so staleness is only meaningful against the **monthly** files.
2. **Operator relays ARE configured in CI.** `EDGE_FACTORY_RELAY_URLS`
   and `EDGE_FACTORY_RELAY_TOKEN` are both present in the run env. The
   transport ladder's last rung runs, and the blocked sources are still
   blocked **through the relay**. The cheapest hoped-for fix is already
   in place and did not work.
3. **`robots.txt` for `predictz.com` and `windrawwin.com` is
   unreachable** — not a disallow rule, no response at all. `robots.txt`
   is the one file published *for* bots. The refusal happens at the
   network edge before any crawl policy is read. **Permission is not the
   question; reachability is.**
4. **Capture ≠ consumption.** The funnel audit proved new sources were
   captured but never wired into `SOURCES_1X2` / `ALL_SOURCES`, so they
   could not vote. Adding a source is two jobs, and the second is the one
   that gets forgotten.

---

## PART 2 — The language hypothesis (the most promising lead)

### 2.1 The pattern

Split the registry by origin and it is hard to miss:

| Contributing | Zero rows |
|---|---|
| **`prosoccer.gr`** — Greek, national TLD | `predictz.com` — UK |
| **`vitibet.com`** — Czech | `windrawwin.com` — UK |
| `zulubet.com` | `soccervista.com` |
| `betclan.com` | `forebet.com` |
| `sports.bzzoiro.com` | |

**Every blocked source is a large English-language site. The clearest
survivors are a Greek-language site on a national TLD and a Czech one.**

This is one day's evidence, not a law. **Verify it across run history
before relying on it** (§5.2).

### 2.2 Why it is probably real

Economics of defence. Large English-language prediction sites are the
ones scraped at volume by everyone, so they are the ones that bought
Cloudflare/Turnstile. A Greek, Czech, Polish, Turkish or Brazilian site
serving a national audience has far less incentive to pay for an
aggressive edge layer, and is often glad of the traffic.

### 2.3 The stronger argument: independence, not availability

This is the part worth internalising.

A rule like `1x2_two_source_p60_unanimous` is only meaningful **if its
voters are independent**. Several UK sites working from the same feeds,
the same public xG and similar models are not independent confirmation —
their agreement is partly an artefact of shared inputs. That makes
unanimity **cheaper than it looks**, which quietly weakens every rule
built on it, including the ones that produced this week's cards.

**A Greek, a Czech and a Brazilian predictor agreeing is far stronger
evidence than three London sites agreeing.**

So language/region diversification is **a modelling improvement that
happens to also solve the availability problem**. It should be pursued
even if every blocked source came back tomorrow.

### 2.4 Audit the current five first

Before adding anything: **check whether the surviving five are genuinely
independent** or share an upstream data provider. If they do, the quorum
rules are weaker than the count implies, and that changes how much any
2-source unanimous rule is worth. Report this even if no new source is
added. See §5.3.

---

## PART 3 — The plan, in order

### Phase 1 — Triage (no code)

Per-source verdict for every registered source, with evidence:
**blocked** (edge refusal) / **broken** (parser or schema drift) /
**flaky** (transport) / **misconfigured** / **stale but reachable** /
**retire**.

For each: which rung of the ladder fails (`urllib` → `curl_cffi` →
operator relay), whether it ever succeeds across ~30 days of history,
and whether its votes add independence or merely duplicate a live source.

> A challenge page and a parser break both produce zero rows. **Say which
> one you are looking at and how you know.**

### Phase 2 — `scoutingstats` (highest priority, not a prediction voter)

It is a **price** source, stale a month, feeding a `0.0` edge floor, with
a fabricated `captured_at`. Either restore its capture or retire it as a
price source. Do not leave it quietly pricing bets. Scope for the
`captured_at` half is already written in
`docs/operator/captured-at-followup.md` — three consumers depend on the
current behaviour and must change together.

### Phase 3 — Cooperative sourcing (operator's stated preference)

> *"those businesses need to protect themselves from people like me at
> the end of the day. we can also try to find more sources that work
> without us having to resort to combative means, which should be our
> first option"*

In priority order:

1. **Ask.** Several of these sites offer feeds or will grant low-volume
   or non-commercial access on request. **Nobody has tried.** One email
   can beat months of transport engineering. Cheapest option on the list.
2. **National-language predictors.** `prosoccer.gr` and `vitibet.com` are
   the proof of concept and the template. Prospect Greek, Czech, Polish,
   Turkish, Spanish, Portuguese/Brazilian, Italian, Nordic, Balkan.
   Prefer national TLDs and sites without an obvious CDN edge layer.
3. **Openly licensed data** — `football-data.co.uk` (results + bookmaker
   odds, published for download), `openfootball`/`football.db`,
   `OpenLigaDB`, `football-data.org` free tier, `TheSportsDB`.
   **Verify each licence yourself; do not trust this list.** No paid
   tiers, no recurring cost.
4. **Derive rather than borrow — the strongest long-term answer.**
   The lane depends on other people's *predictions*, which are scarce and
   defended. *Results, fixtures and closing odds* are abundant and openly
   licensed. A deterministic model trained in-repo on open results would
   be a source nobody can block, rate-limit or withdraw. **Conditions:**
   same walk-forward certification, shadow period and gates as any
   external source; no self-certification; deterministic auditable code,
   never a generative component. Cost this seriously.
5. **Retire what is gone.** A dead source in the registry hides the real
   constraint and inflates quorum optics.

### Phase 4 — Make the next death visible

Forebet died in June; nothing noticed until October. Regardless of
anything else:

- **Reclassify honestly.** `forebet` is still `core_voter` while four
  months dead. Use existing vocabulary in `src/edgefactory/source_census.py`
  (`tier_note`, `shadow_tier_fresh_production_eligible`,
  `source_tier_not_dispatchable`). Do not invent a parallel label system.
- **Add a zero-rows-across-N-runs invariant**, naming the source.
  WARNING, not error. ~27 existing checks in
  `src/edgefactory/run_invariants.py` to copy.
- **Explain why `soccervista` is in the registry but not in the
  tripwire**, and close that gap.
- **Confirm `bzzoiro`'s newest row of 2026-10-08** (7 days ahead) is
  legitimate advance fixtures, not a date-parsing defect.

---

## PART 4 — Where to look

### Code

| What | Where |
|---|---|
| Source adapters | `src/edgefactory/sources/<name>.py` |
| Relay transport | `src/edgefactory/sources/public_relay.py` (`configured()`, `fetches()`) |
| Registry + tiers | `src/edgefactory/source_registry.py` — `predictz` :144, `windrawwin` :149, `soccervista` :169, all `TIER_SHADOW, ("1x2",)` |
| Challenge detection | `src/edgefactory/sources/soccervista.py` — exception docstring *"A transport returned a shell/challenge instead of the predictions page"*; ladder documented ~:216 |
| Read-only census | `src/edgefactory/source_census.py` — **must never dispatch, promote, certify, force-enable, or recommend weakening a gate** |
| Invariants | `src/edgefactory/run_invariants.py`, `scripts/check_run_invariants.py` |
| Edge floor | `scripts/fresh_production.py` — `MIN_EDGE_TO_DISPATCH = 0.0` (~:96) |
| Candidate ladder | `scripts/auto_tickets.py` — `legacy_candidate_rows()`, `LANE_LEGACY_CANDIDATE` |
| Gate chain | `scripts/auto_tickets.py` — `playable_legs(..., execution_safe=True)` (~:1802). **No edge check here — this is the doctrine gap** |
| Price staleness | `src/edgefactory/enh_pricing.py` — `_fresh_row()` (~:159) |
| `captured_at` defect | `scripts/picks_today.py` — `_scoutingstats_rows_to_odds()` (~:2052) |

### Docs

| Document | Contains |
|---|---|
| `HANDOVER.md` | **Single source of truth.** Session arc, corrections, standing verdicts |
| `docs/operator/source-transport-investigation-brief.md` | Full source brief; **§11 is hard run evidence and supersedes earlier sections** |
| `docs/operator/NEW-AGENT-PROMPT-sources.md` | Paste-ready agent brief |
| `docs/operator/captured-at-followup.md` | `captured_at` defect, the three dependent consumers, exit condition |
| `docs/operator/invariant-persist-gate.md` | The persist gate (applied) |
| `docs/operator/daily.yml.READY-TO-PASTE` | Byte-identical to the live workflow; a test enforces that |

### Data

| Artifact | Use |
|---|---|
| `localdata/<source>_YYYY-MM.csv.gz` | **Live captures.** Staleness evidence lives here |
| `localdata/<source>.csv.gz` | Legacy deep history. **Do not judge liveness from these** |
| `localdata/edge_firing_tripwire.json` | Per-source cache health — the table in §1.1 |
| `localdata/fresh_production_candidate_picks_<date>.md` | Per-fixture blocker reasons, the funnel's ground truth |
| `localdata/fresh_production_dispatch_plan_<date>.json` | What the lane dispatched |
| `localdata/picks_<date>.json` | Legacy slate — the ladder's candidate pool |
| `localdata/purity_registry.json` | League contexts. **Named-league count is the fragile dimension** |

---

## PART 5 — Verification recipes

### 5.1 Reproduce the leg funnel for any date

```bash
python3 - <<'PY'
import json, sys, importlib.util
from pathlib import Path
sys.path.insert(0, 'src')
spec = importlib.util.spec_from_file_location('at', 'scripts/auto_tickets.py')
at = importlib.util.module_from_spec(spec); spec.loader.exec_module(at)
at.LOCALDATA = Path('localdata')
rows, _, _ = at.load_production_slate('2026-10-01')
safe  = at.playable_legs(rows, day='2026-10-01', settled={}, execution_safe=True)
loose = at.playable_legs(rows, day='2026-10-01', settled={}, execution_safe=False)
print(f"admitted={len(rows)} execution_safe={len(safe)} no_quarantine={len(loose)}")
for r in rows:
    print(r.get('home'), r.get('odds'), r.get('bucket'),
          r.get('price_quarantine_reason'), r.get('price_push_eligible'))
PY
```

Toggling `execution_safe` isolates the quarantine as a cause. Anything
`PLAYABLE` but uncarded was dropped by **exposure**, not a gate.

### 5.2 Test the language hypothesis across history

```bash
for c in $(git log --format=%h -20 -- localdata/edge_firing_tripwire.json); do
  echo "== $c"; git show $c:localdata/edge_firing_tripwire.json 2>/dev/null | head -40
done
```

Look for whether the English-language set is *persistently* zero while
the national-language set is *persistently* live.

### 5.3 Independence audit of the live five

For each fixture in a recent `picks_<date>.json`, compare `sources_used`
probabilities. If `zulubet`, `betclan` and `vitibet` agree to within a
rounding error far more often than chance, suspect a shared upstream and
report it — a 2-source unanimous rule means less than its name implies.

### 5.4 Registry health (named-league is the fragile dimension)

```bash
python3 -c "
import json
reg=json.load(open('localdata/purity_registry.json'))
ks={k.split('|')[1] for k in reg['contexts']['league'] if '|' in k}
print('keys',len(ks),'named',len([k for k in ks if len(k)>6]))"
```

Healthy ≈ 426 keys / 90 named. A cold-cache rebuild produces ~433/3 —
total **rises** while quality collapses. Guarded in `6597857`.

---

## PART 6 — Hard constraints

- **No paid solvers, CAPTCHA bypass, residential proxies, stealth
  services, or anything with a recurring cost.** Refused repeatedly.
- **No Forebet browser diagnostics or probes.** Not `probe=forebet_getrs`,
  not `probe=page_access`. `EDGE_FACTORY_FOREBET_BROWSER` stays `off`.
  Forebet is a written post-mortem only.
- **Do not hammer a site signalling it does not want traffic.** If a
  source must be fought to be read, replace it.
- **A challenge or denial page is never an empty day.** Report transport
  failure. The rule exists in code; do not regress it.
- **Row capture is not source validation.** No graduation from
  shadow/candidate on row counts. Evidence decides.
- **Never call a source validated while it has an unexplained reversed
  home/away candidate.** Squad qualifiers (women's, youth) have caused
  real mismatches — non-English sources will make this worse. **Budget
  alias work per source** and extend the existing audited normalisation.
  Do not infer fixture identities, kickoffs, aliases or odds beyond it.
- **No synthetic rows in production artifacts**; synthetic data only in
  unit tests. **No generative component** may produce probabilities,
  rows, aliases, odds, labels or picks.
- **Do not touch the betting engine.** `scripts/auto_tickets.py` remains
  sole owner of staking, ticket creation, draft/freeze, assayer controls,
  bucket P&L tripwire, selection ladder and benching. The pick engine
  emits no stake. No parallel ticket engine.
- **Abstention is success** when evidence is insufficient — but do not
  stop at "no picks" when the cause is a fixable structural issue.
- **Deletion safety:** no `git reset --hard`, no `git clean`, no blind
  `rm -rf localdata`. Wrong generated artifacts are deleted and
  regenerated, never migrated — no `.bak`/`.old` copies.
- **Operator runs nothing locally** and has no Codespaces. Anything
  operational must work via GitHub Actions, browser, Cloudflare or Apps
  Script. Local commands are for development and testing only.
- Prefer wiring into `scripts/daily.py` over workflow edits — the GitHub
  App cannot push `.github/workflows/`. If unavoidable, write a
  ready-to-paste patch under `docs/operator/` and make a test skip until
  it is applied.

### Working-tree hazard

The sandbox tree has reset to the base commit **~12 times** this session,
silently discarding edits mid-task. **Verify `git rev-parse --short HEAD`
before trusting any grep, and `grep` for your own edit before concluding
anything about its effect.** Recover with:

```bash
git fetch origin arena/01a0f2b3-edge-factory
git reset --mixed FETCH_HEAD && git checkout -- .
```

**Never force push.** A rebase once landed on the base commit and would
have destroyed the branch.

---

## PART 7 — Acceptance criteria

1. Per-source verdict table with evidence, naming the failing ladder rung
   and distinguishing **blocked** from **broken**.
2. `scoutingstats` restored or retired as a price source, with both the
   staleness and `captured_at` defects addressed or explicitly scoped.
3. Independence audit of the live five, reported even if nothing is added.
4. The language hypothesis tested across run history and confirmed or
   rejected with data.
5. Honest registry reclassification landed with tests — no dead source in
   a core role.
6. Zero-rows-across-N-runs invariant landed with tests.
7. At least one concrete, costed supply proposal from the cooperative
   options, with licence/terms verified.
8. Full suite passing; exact count reported.
9. An explicit list of what could **not** be determined from artifacts
   alone, and what evidence would settle it.

Do not report a source recovered on one successful fetch. Do not claim
validation from row counts. **If the honest answer is "this source is
gone, retire it", say so plainly — that is a good outcome.**

# Next-agent brief — operator visibility for the ticket and slate gates

**This is a handoff brief, not a state document.** Every claim below was
measured against `main` = `6f52b92` ("chore: persist pipeline state (run
37584672918)"), whose parent is `f23a68b` — the merge commit of PR #44
(merged 2026-10-07T06:58:34Z). The pipeline rewrites `main` as a single-commit
snapshot on every run: **fetch and re-resolve the tip, never hardcode it.**
Where a claim is an inference rather than a measurement, it says so.

**Line anchors are perishable.** Each anchor below is `file:line` *plus* a
searchable landmark. Nine commits moved these lines repeatedly during PR #44.
If the line number and the landmark disagree, **the landmark wins** — re-resolve
by search. (This rule exists because a draft of this very brief cited an
anchor one line off, and a "scored 22 then scored 23" log line that exists in
no committed artefact — both caught only by running a verification sweep over
the document itself.)

**This file has a measurable side effect.** `tests/test_docs_links.py`
parametrizes one case per Markdown file under `docs/` plus `README.md`, so
adding this brief moves the suite by exactly +1: **2392 passed** was measured
on `6f52b92` *without* this file; with it, expect **2393 passed**. That
off-by-one is precisely what caused a correction round on 2026-10-07 — do not
"fix" it.

---

## 1. Mission — four tasks, all operator-side visibility

None of them may change which bets are selected, priced, staked or pushed.

| # | Task | Type |
|---|---|---|
| 1 | Stop discarding the ticket-builder skip census | code |
| 2 | Name the fixtures the ML scored but never emitted | code |
| 3 | Decide the fate of the gitignored scored-candidate shadow ledger | decision + code |
| 4 | Resolve the `ml-meta avg_p>=X` label divergence | measured decision; escalate if not obvious |

Success = an operator can read a run's output and answer "which matches were
considered, and why did each one not become a bet" without re-running a
predicate by hand. Today that is impossible. That is the whole point.

This mission is **separate from the standing queue** in
`docs/operator/TICKETS-OPEN.md` (items a–m: bzzoiro_odds redo, soccervista,
Betminer/PredictIQ/pinnapi voices, politeness budgets, …). Do not conflate the
two; do not work the standing queue unasked.

## 2. Where this came from (do not re-litigate)

The operator asked why 2026-10-07 produced no auto-ticket. Reproducing the
gates from the committed card (measured; recipe in §12):

```
playable_legs(execution_safe=True)   -> Ponte Preta v Juventude (odds 1.36)
                                        Urawa v Omiya Ardija (odds 1.741)
live_kickoff_guard @ build instant   -> DROPPED Ponte Preta (kicked off 02:35 SAST)
                                        kept   Urawa (kicks off 11:00 SAST)
LEGS_PER_ACCA = 2                    -> NO BET — 1 qualifying leg, need 2
```

The verdict is identical at every build instant in the window 02:35–11:00 SAST
(measured at 09:00:00 — the canonical FREEZE_HOUR build instant; at 09:06:26 —
the card's own `as_of`; and at 09:42:44 — the build instant the previous
session read from the run log, which is not a committed artefact). **The no-bet
is correct and is not a bug.** The bug is that the output does not say any of
it. The operator's follow-up — also correct — was that the dropped matchups
that never reached the slate are invisible too.

### The day in numbers (all measured on `6f52b92`)

* **25** distinct fixtures were ML-scored: `localdata/ml_fade_research_ledger.json`,
  `family == "ml-meta"`, `date == "2026-10-07"` — exactly one row per fixture.
* **3** reached the slate: Urawa v Omiya Ardija, FC Tokyo v Shonan Bellmare,
  Mexico v Chile.
* **22** never did. Every one sits at or below **50.15%** (tail max: Vitoria v
  Chapecoense, `ml_p` 0.5015), against a lowest certified ML threshold of
  **55** (certified set 55, 60, 65, 70, 75, 80, 85 —
  `localdata/edges_consensus.json`). So the ML gate itself would not have
  emitted any of the 22. (Whether the *consensus* path could have is a
  separate question — see Task 4 — and is exactly what the new output will
  answer.)
* The card grew during the morning: `picks_morning_2026-10-07.json` has **1**
  row; `picks_2026-10-07.json` has **5**.
* No slip was ever written for the day: `auto_tickets_2026-10-07.txt` is absent
  and `auto_tickets_state.json` has `frozen_by_date` through 2026-10-06 only.
  The four preceding days (10-03 … 10-06) each froze a slip with a deployed
  bet — 2026-10-07 is the first no-slip day in that window.
* **Caveat that matters (measured):** `ml_scored` is per-pass, not per-day
  (`scripts/picks_today.py` resets it at `:4105`; `:5749-5757` derives the
  per-day figure as a delta of the collector's counter, so several passes
  accumulate), and the ledger cannot reconstruct what any single pass saw.
  The ledger's Urawa row reads `ml_p = 61.01%` while the emitted row for the
  same fixture carries `ml_p = 55.01%` (`avg_p = 55.0`). Label any new output
  with the pass it describes.

## 3. Task 1 — the skip census is computed and then thrown away

`scripts/auto_tickets.py`:

* `format_skip_census()` (`def` at `:1494`, landmark `def format_skip_census`)
  already renders a block naming up to three fixtures per drop reason with a
  `(+N more)` tail (`names[:3]`, `more = f" (+{len(names) - 3} more)"`). It is
  good output.
* It is called at `:3780` (`census_lines = format_skip_census(...)`), and
  blanked at `:3781-3782` when nothing was dropped
  (`if not any(census.values()): census_lines = []`).
* Both no-bet paths fold it into `audit_lines`: `:3816-3818` for the
  `len(plan_pool) < LEGS_PER_ACCA` path (`:3783`), and `:3870-3872` for the
  empty-plan path.
* `audit_lines` is written to `localdata/auto_tickets_{date}_force_recut.txt`
  **only when `recut_lines` is non-empty — i.e. only on `--force`** —
  `if recut_lines:` at `:3833` (write `:3834-3836`) and `:3886` (write
  `:3887-3889`). On every ordinary run it is discarded. The success path never
  consumes `census_lines` at all (only `:3780`, `:3782`, `:3816`, `:3870`
  mention it).
* The code already states the constraint: the comment above `:3816` reads
  "Keep policy/rejection details available to the force-recut audit, but do not
  mix operator diagnostics into the customer-facing card."

**Fix:** print the census to **stderr** in both no-bet paths unconditionally
(and in the success path when legs were dropped before the plan). Keep it off
the customer-facing card — `--force` diffing of the printed card is
load-bearing for the supersede/audit logic.

**Acceptance:** run the builder for a day with a known drop and show the block
on stderr; show the card text byte-identical to before the change.

## 4. Task 2 — the ML print site has the names in scope and prints counts

`scripts/picks_today.py`:

* The print at `:4535-4540` (landmark `ML-meta {day}: scored`, to stderr) says
  only: `ML-meta {day}: scored {ml_scored} fixture(s), max ml_p = …% (certified
  thresholds: …) -> {n_ml} pick(s)`.
* `fixture_audit` is fully populated by then, in **two tiers**:
  * `:4089-4090` (`fixture_audit.append({`, `"kind": "upcoming_fixture"`) —
    every fixture seen in the 1x2 source map, pre-scoring (loop
    `for k in keys:` at `:4086`, guarded by `if fixture_audit is not None:` at
    `:4085`);
  * `:4303-4304` (`fixture_audit.append({`, `"kind": "ml_scored_fixture"`) —
    inside the ML scoring block, appended at the exact increment that feeds
    `coverage: scored=` (the code's own comment at `:4276-4283` says so;
    `ml_scored += 1` is at `:4273`), carrying `home`, `away`, `league`,
    `kickoff`, `ml_probability`, `ml_majority_pick`, `sources_used`,
    `shadow_price`, `shadow_price_source`.
* That gives a **three-tier funnel**: `upcoming_fixture` (seen in the 1x2
  sources) → `ml_scored_fixture` (model scored it) → emitted pick. That is
  exactly the "seen / scored / emitted" view the operator wants, and it is
  currently fed only into an audit module (§5, Task 3).
* The same list is handed to `scored_candidate_shadow.record_picks_build()`
  at `:6367-6378` (loop `:6361`, `try/except` `:6355-6384` — audit-only,
  fail-soft).

**Fix:** print (stderr) the fixtures that scored but did **not** emit a pick,
with their `ml_p` and the relevant threshold, plus a count of those dropped
for non-model reasons (pre-match guard, `len(used) < n_req`, competition-type
threshold raise, collapse). Attribute correctly: `len(used) < n_req` and the
cup/friendly threshold bumps live in the **consensus** path (`:4471-4481`,
landmark `Option 2: Dynamic Competition-Type Gating`) and are not ML
thresholds; the direct ML path is `:4340-4350+` (landmark
`if ml_p * 100.0 >= thr`).

**Acceptance:** for a day with known drops, the union of (named emitted) ∪
(named dropped) equals the scored-fixture set from the research ledger; assert
that in a test rather than eyeballing it.

## 5. Task 3 — the only name-complete price record is gitignored

* `.gitignore:10` is `localdata/*` with **no negation** for
  `scored_candidate_shadow_*` (the research ledger *is* negated at `:136`).
* Consequence: `localdata/scored_candidate_shadow_YYYY-MM-DD.jsonl` (and its
  `_settlement_` sibling) exist only in the runner's Actions cache. They are
  absent from this checkout; they are never on the repo.
* `docs/operator/SCORED-CANDIDATE-SHADOW.md` documents the schema and states
  the standing decision: "Both stay **gitignored** with the rest of
  `localdata/` (shadow ledgers are deliberately not committed)." The ledger
  already carries what Task 2 wants to print: `scored_fixture` events with
  `not_materialized_reason="no_candidate_emitted"`, and `candidate_status`
  events whose `rejection_reasons` are derived from the live gate predicate
  (`playable_leg_rejection` — the same single source of truth the card uses).

**Do not blind-commit it — and do not treat the standing decision as
untouchable either.** It is a documented default, not a law. Measure first:
file size, growth rate, whether a retention rule can bound it. Then choose,
with the measurement in hand, and state which and why:

1. Keep it gitignored and let Task 2's print carry the names (the operator
   asked for the names in the run output, not necessarily the file).
2. Add a targeted negation (like `:136`) plus a retention rule, if the file is
   small and stable.
3. Escalate to the operator if neither is true.

Never commit `*.csv.gz`, `*.duckdb`, or a whole `localdata/` subtree to solve
this. Note `.gitignore` semantics: broad ignores come first and **the last
matching pattern wins**, so a negation must come after `localdata/*`.

## 6. Task 4 — one rule name, two different measurements

This is an instance of this codebase's recurring failure: **an identifier that
asserts more than its measurement supports.** Treat it with the same care as
the forebet role fix (Item B) and the alias seams (Item A).

**Measured facts, all reproducible:**

* The miner certifies `ml-meta avg_p>={thr}` against the predicate
  **`ml_p*100 >= {thr}`** (`scripts/mine_consensus.py:912-913`, landmark
  `f"ml_p*100 >= {thr}"`). The name says `avg_p`; the trained quantity is the
  model probability.
* `scripts/picks_today.py:1153-1177` (`def _edge_entry`) parses that same
  registry entry into the 1x2 table at `n_way = 3` (display `ML-META≥{thr}`);
  the table is built at `:1223-1233`; `thr_for()` (`:1371-1375`) resolves the
  highest `n_way <= sources-available`, and the consensus path then applies its
  threshold to a **three-donor mean of `avg_p`**. Name-honest, predicate-wrong.
* The direct ML path (`:4340-4350+`) applies the threshold to `ml_p`.
  Predicate-honest, name-wrong.
* Today's **Mexico v Chile** is the live example: emitted
  `rule = "ml-meta avg_p>=60"`, `display_rule = "ML-META≥60"`, `avg_p = 61.2`,
  `ml_p = None`, `n_way = 3`, `sources_used = [statarea, betclan, bzzoiro]`,
  league `International,Friendlies`. The ledger's model score for that fixture
  is **54.29%** — below the lowest certified ML gate. A row is wearing a model
  label the model did not produce. (FC Tokyo and Urawa, the other two ml-meta
  rows, carry `ml_p` — they came through the direct path.)
* The rule registry itself is shared: `ml-meta avg_p>=55 … 85` exists in
  `localdata/edges_consensus.json` and is consumed by both paths.

**Instrument first.** Build a script that, for a window of archived days,
classifies every archived pick whose `rule` starts with `ml-meta` into
(a) emitted by the direct path (has `ml_p`) and (b) emitted by the consensus
path (no `ml_p`, `n_way`/`sources_used` present), and reports counts and how
often (b) would not have cleared the ML gate. **Report the split before
changing anything.**

**Candidate fixes — pick one with the measurement in hand, or escalate:**

1. Make the emitted `rule`/`display_rule` honest per path (label (b) as a
   consensus rule). Cheapest; changes no selection.
2. Exclude `ml-meta` rules from the consensus table path. **Changes which
   picks emit** — behaviour change, needs the full acceptance gate below.
3. Two registry entries. Largest blast radius (miner, decay monitor, purity
   assay, ledger, tripwire all key off rule names).

**Whatever you choose:** the customer card's `display_rule` is user-visible —
do not silently relabel a pushed pick. If a row's displayed identity changes,
that is a record correction and must be stated in the report and in
`docs/operator/`.

## 7. Hard rules — each one cost a previous agent a round

### Evidence discipline

1. **Never claim more than you measured.** Separate OBSERVED from INFERRED in
   plain English; state the boundary and scope of every claim.
2. **Verify by re-derivation, not restatement.** The pushed correction for
   the Urawa fold mis-stated its own headline number (it quoted the at-defect
   count, 87, as the post-fix residue; the truth was 70, because the guard
   released exactly 17). Re-derive your own numbers *after* writing them, from
   the final tree. A draft of this brief carried four unverified claims (a
   "50.1%" tail max that was really 50.15%; a "same outcome as 2026-10-03"
   that was wrong — 10-03 froze a slip with a deployed bet; a "scored 22 then
   scored 23" log line that exists in no committed artefact; a "3,509
   superseded narrow keys" figure that exists nowhere). All four were cut or
   corrected by measuring. Do the same to this document.
3. **A guard nobody watched fail is not known to work.** Break it, watch red,
   restore, watch green. Record the counts both ways.
4. **A mutation must reproduce the ACTUAL historical defect**, not a
   plausible-looking stand-in.
5. **Never assert wiring by text search.** Match structurally (AST) and assert
   against specific returned values. A wiring guard written as a text search
   once passed *with the wiring removed*, because the same keyword appeared
   elsewhere in the file for a different source (`HANDOVER.md`, 2026-10-06
   addendum).
6. **Name the baseline for any test-count claim.** A parametrization of 157
   seam cases + 1 join case moves the collected count by 158 (measured at
   `d6d163d`: 1850 passed with the tests, and the URAWA doc records
   1850 → 1851 when *that document* was added). `tests/test_docs_links.py`
   parametrizes one case per Markdown file, so **adding a doc moves the suite
   by exactly 1**. Baselines measured on `6f52b92`: **2392 passed**,
   `def test_` floor **1534**, `verify_work_order.py` 14/14, `verify_wo7.py` 9/9.

### Identity and key spaces

7. **Never re-key `norm_team`.** It is a certified width-9 key space; re-keying
   it moves every historical join. It is marker-blind by construction (145 of
   150 marked names in the live populations key identically to their unmarked
   form — `docs/operator/URAWA-LONG-FORM-FOLD-2026-10-07.md`). Guard at the
   join, not in the space. Narrow keys are already superseded at settlement:
   `auto_tickets.py` prints `settlement_narrow_key_superseded={count}` and
   "now settled on distinct wide keys" (search `settlement_narrow_key_superseded`;
   773 in the FINDINGS measurement) — that is the evidence the space must stay
   frozen.
8. **Marker disagreements fail closed.** A refused price is acceptable; a
   wrong-squad price at the exact tier is not. `Ajax`/`Ajax W`/`Ajax U21` all
   key `ajax`.
9. **Every "the fold succeeds" test needs its over-reach companion**, off the
   same curated table: the marked variant must NOT collapse onto the unmarked
   canonical. A suite that only exercises the degenerate case cannot catch a
   confusion between the two things it conflates.
10. **Fuzzy matching is diagnostic only, never a join path.** Its marker
    blindness is known, fail-closed, and out of scope — do not extend it
    unprompted.
11. **Never guess a spelling** to add as an alias, and **never guess a fold
    direction** — measure which canonical dominates and report both counts
    first.
12. **If the evidence and the choice disagree, say so.** The Urawa fold
    direction was chosen *against* the settled window (10 vs 31 settled rows
    for our key vs the long forms; warehouse 480 vs 129 ≈ 3.7:1 the other
    way) on the strength of the operational spaces. That was disclosed late.
    Disclose it up front.

### Output and git

13. **Operator diagnostics go to stderr or a committed artefact; the customer
    card stays clean.** Tasks 1–4 must not alter card text.
14. **Warnings are visibility-only.** Never lower a threshold, floor, cap, or
    stale-days value to clear one. Repair a capture cadence or correct a
    measurement-supported misclassification — that is what the forebet role fix
    legally did, and it changed no gate.
15. **Do not add unrequested work.** No team-named test files (one was written
    and deleted as bloat). New curated teams are covered by construction
    because the alias tests derive their cases from
    `Config/entity_overrides.json`. Consolidate docs; doc volume is a real
    cost. Lessons live in `docs/operator/`, never in chat. The accumulated
    lessons are already written down: **`HANDOVER.md` (10,658 lines) is the
    running handover log** — read it before re-learning anything.
16. **`.github/workflows/` cannot be pushed by the app.** If a workflow change
    is needed, output the complete file and say so.
17. **Never force-push.** On a non-fast-forward: fetch, confirm the remote
    holds the work, `reset --soft` onto the remote tip, re-commit forward.
18. **Never run `git clean`, `git reset --hard`, or revert anything.** Do not
    delete the repo root or `.git`. Restore mutated files from a `/tmp` copy,
    not `git checkout --` (an earlier checkout destroyed uncommitted work —
    `docs/operator/LOST-SESSION-RECOVERY-2026-10-07.md`).
19. **Never use backticks inside a `git commit -m` heredoc.**
20. **Never log request headers.** No new vendors. Do not raise per-run call
    caps or lower minimum intervals. The sandbox has no vendor network — prove
    contracts with **mocked responses only**.
21. **Do not write Markdown links to files you have not verified exist.**
    `tests/test_docs_links.py` fails on any dead relative link in `docs/**`
    (fenced code blocks are exempt — keep paths in code spans or fences).

### Scope fences (frozen — a human decides, not you)

22. **Do not touch settlement, staking, bank arithmetic, or any gate, floor,
    cap, quorum, threshold or veto rule** for Items C/D. Two stalled
    settlement keys (Tochigi SC v Giravanz Kitakyushu 2026-06-07; Samgurali v
    Meshakhte Tkibuli 2026-08-01) and two frozen Kladno conflict rows
    (2026-09-23, `kladno|banikostr`, ml-fade + ml-meta) are awaiting a human —
    the cases and the standing remedy (`Config/verified_results.json`, one row
    per case, operator sets the score) are written up in
    `docs/operator/FINDINGS-2026-10-07.md` §2–3. `Config/verified_results.json`
    and `localdata/team_aliases.json` are off-limits for edits.
23. **Do not re-open resolved questions:** the historical test-count baselines
    (1850/1851 at `d6d163d`, 2215 at `522a3c0`, 2392 at `6f52b92`); the fuzzy
    tier's marker blindness; the league verdicts (no purity context exists for
    Japan Emperor Cup or Algeria Ligue 1 — 5,545 league contexts, none for
    either — so both stay UNKNOWN; do not claim a verdict improvement).
24. **Do not treat a session checkout's stale index as a change.** In some
    session workspaces `git status` shows modified/untracked files that are
    byte-identical to `main`, an artefact of a ref swap. Verify with
    `git diff --name-only main -- <paths>` before believing a file changed.

## 8. Decision points to escalate (not guess)

* Task 4's remedy, if the instrumented split makes option 2 look necessary (it
  changes which picks emit).
* Task 3's file-fate decision, if the ledger turns out large or fast-growing.
* Anything that would change a customer-visible `display_rule` on an already
  pushed pick.
* Any request to touch Items C/D, the stalled keys, or the frozen Kladno rows.

## 9. Definition of done

* All four tasks landed or explicitly escalated with the measurement that
  forced escalation.
* `PYTHONPATH=src .venv/bin/python -m pytest tests/ -q` → 0 failed, **no test
  deleted**. Expected count with this brief in the tree: **2393 passed**.
* `python3 scripts/verify_work_order.py` → `14/14 ALL PASS`. If you added test
  functions, raise its floor and put the reason inline next to the other dated
  raises.
* `python3 scripts/verify_wo7.py` → 9/9.
* Each new guard: watched fail (mutation), restored, watched green.
* A short `docs/operator/` entry for Task 4's outcome — and if any row's
  displayed identity changed, that is a record correction, stated plainly.

## 10. Report format the operator expects

1. What you changed, and the receipt for each (command + observed output).
2. OBSERVED vs INFERRED, separated.
3. The boundary of every claim: what window, what population, what you did
   **not** check.
4. Any number you are about to state, re-derived on the final tree before you
   state it.
5. Open items left deliberately, and why it was right to leave them.

The operator audits by re-deriving independently and will find your headline
number if it is wrong. They found the width-9 leak themselves, after the first
fix had been pushed and declared closed. Write for that reader.

## 11. Environment and how to work here

* Sandbox has **git and gh reachable; no vendor network**. Prove adapters with
  mocks. Do not attempt live capture.
* `.venv` may be absent in a fresh workspace and system `python3` has no
  pytest: `python3 -m venv .venv && .venv/bin/pip install -r
  requirements.txt` (PyPI is reachable). `scripts/auto_tickets.py` self-inserts
  `src/` on `sys.path` (line 76); for other modules use `PYTHONPATH=src` and
  add `scripts/` to `sys.path` when importing them directly.
* `main` is a **single-commit snapshot** rewritten by the pipeline on each run
  (this checkout is shallow at `6f52b92`, parent `f23a68b`). Fetch first;
  ancestry across pipeline runs is not meaningful.
* Expect `main` to move under you mid-session: the pipeline pushes its own
  persist commits. Fetch and re-resolve before any push.
* `localdata/` in the working tree is production state. Read it; do not
  hand-edit it. `localdata/edge_firing_tripwire.json` is a **tracked** artefact
  that local test runs can perturb — restore it if you do.

## 12. Reproduction snippets

The scored/dropped split for a day (measured output for 2026-10-07 in §2):

```bash
git show <tip>:localdata/ml_fade_research_ledger.json > /tmp/res.json
python3 - <<'PY'
import json
rows = json.load(open('/tmp/res.json'))
rows = rows if isinstance(rows, list) else (rows.get('rows') or [])
day  = [r for r in rows if str(r.get('date') or '')[:10] == '2026-10-07'
        and r.get('family') == 'ml-meta']
fx   = {(r.get('home'), r.get('away')): r.get('ml_p') for r in day}
print(len(fx), "scored")
for (h, a), p in sorted(fx.items(), key=lambda x: -(x[1] or 0)):
    print(f"  {p*100:5.1f}%  {h} v {a}")
PY
```

The no-bet verdict, reproduced rather than read (measured output in §2):

```python
import json, sys
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, 'scripts')
import auto_tickets as at

rows = json.load(open('localdata/picks_2026-10-07.json'))
rows = rows if isinstance(rows, list) else rows.get('picks') or rows.get('rows') or []
now  = datetime(2026, 10, 7, 9, 42, 44, tzinfo=ZoneInfo('Africa/Johannesburg'))
pool = at.playable_legs(rows, day='2026-10-07', execution_safe=True)
kept, drops = at.live_kickoff_guard(pool, now)
```

`playable_leg_rejection(row, day=..., execution_safe=True)`
(`scripts/auto_tickets.py:1534`, landmark `def playable_leg_rejection`) is the
single predicate behind both the pool and the operator rejection ledger — use
it directly rather than paraphrasing the gates.

## 13. What is already done (so you do not redo it)

Shipped and merged as **PR #44** (merge commit `f23a68b`, merged
2026-10-07T06:58:34Z; `6f52b92`'s parent). Nine commits, verified against the
PR:

| commit | what |
|---|---|
| `d6d163d` | fold `Urawa Red Diamonds` onto canonical `urawa` |
| `ccac6d1` | the fold's operator doc |
| `eefcdfd` | Japan Emperor Cup / Algeria Ligue 1 league keys (identity only; both verdicts remain UNKNOWN) |
| `522a3c0` | forebet reclassified `core_voter` → `backfill_donor`; retired captures reported, not alarmed |
| `ef95254` | Items B/C/D write-ups (C and D are proposals only — see fence 22) |
| `1ac5ebc` | odds aliases refuse to cross a squad marker (17 of 157 curated pairs) |
| `8e21322`, `ce437d2` | record corrections: fold direction, identity not closed, test baseline, 70 vs 87 |
| `79f3945` | exact tier requires the raw names to agree on squad markers (closes the uncurated half: `Ajax`/`Ajax W`) |

Acceptance measured on `6f52b92` (re-measured for this brief): **2392
passed**; `verify_work_order.py` 14/14; `verify_wo7.py` 9/9; `def test_`
floor **1534**.

Live production receipt from the run on that merge: the Urawa row in
`localdata/picks_2026-10-07.json` — `odds=1.741`, `odds_match_method="exact"`,
`odds_source="sharpapi_odds"`, `price_push_eligible=true`, `as_of 09:06:26
SAST`; its price board carries the vendor's long form `Urawa Red Diamonds`
matched at the exact tier; the leg is in
`localdata/sent_ledger_2026-10-07.json`. The fold's own fixture, joining at the
top tier on real data.

Three more things in the same family, found while auditing that run, **not
fixed and not part of this mission** — do not fix them unasked:

* The persisted per-day health record
  (`localdata/source_health_2026-10-07.json`) shows `bzzoiro` and
  `bzzoiro_odds` as `status: "ok"` with no field to carry an error, while
  `localdata/source_health_state.json` records for `bzzoiro`
  `last_errors: ["HTTP Error 403: Forbidden"]`, `last_http_statuses: [403]`,
  `last_quota_hint: "auth_or_quota"`, `last_status: "auth"` (updated
  2026-10-07T07:15Z, `last_run_day` 2026-10-08). Capability-scoped, so not
  false — but the measurement has nowhere to live in the per-day record. The
  standing ticket for the 403 zero-row day is TICKETS-OPEN.md item (a).
* The `UNKNOWN league verdicts (consider adding to entity_overrides.json)`
  advisory still prints (`scripts/picks_today.py:6548`, landmark `UNKNOWN
  league verdicts`) after the two leagues were added to
  `Config/entity_overrides.json`, because it fires on the verdict being
  UNKNOWN and no purity context exists for either league. The message
  conflates "not in the registry" with "no verdict".
* Two archived legs carry squad markers and have no settled result row in the
  64,849-row overlay under any spelling — `2026-06-21 Tartu Welco v Nõmme
  United II` and `2026-09-27 Brommapojkarna W vs Malmö FF W` — so the marker
  guard (`_note_marker_guarded_leg`, `scripts/auto_tickets.py:2275`, prints
  `settlement_marker_guarded=N :: {label}`) is what keeps them out of the
  similarity fallback; they stay pending for a human. Not introduced by this
  work.

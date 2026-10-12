# Round-5 acknowledgement (reviewer's memo, as relayed 2026-10-12)

**Provenance.** This file records the acknowledgement memo the reviewer sent
after A1–A5. It arrived as chat text, not as a file in this workspace: the
memo's own commit (`7690da7`) and the memo's path are **not** in this clone,
so nothing here is attributed to those bytes. Line numbers the memo quotes are
the reviewer's tree's; this repo cites symbols instead (rule 7). Recorded
verbatim-in-substance below, with the two local re-measurements that were
possible at the time.

## 1. The reviewer's re-measurements

1. **The void mechanism reproduces.** In `auto_tickets.py`: `r = pick_result(p, settled)`
   → `None` → `(now − anchor).days >= 5` → `r = "void"`; then the all-void
   branch `a["won"] = True; a["odds"] = 1.0  # all void: stake back`. So the
   first N-1(c) proof was resolving through the **void timer**, not grading.
   Re-measured locally: true (`settle_open_slips`'s void-timer branch and the
   all-void stake-back branch both read as described).
2. **The whitelist arithmetic reconciles completely.**
   - the reviewer's 7-key literal **is** the patch's filter verbatim;
   - `origin/main`'s `run_stats()` = **3** keys, and its pre-patch filter
     literal already carries `be_fetches` — dead weight in both literals,
     produced by nothing but the test stub;
   - the tip's `run_stats` = 5 (main's 3 + #61's two rejection counters),
     union **8**, filter **9** = 8 + `be_fetches`.
   Re-measured locally: true (`git show origin/main:scripts/capture_betexplorer.py`
   carries `be_fetches`; `origin/main`'s `run_stats()` returns three keys).
   **A3(b) closed**, and the reviewer's earlier "7 vs 8" framing was the
   confusion, not the report.
3. **A5 confirmed in principle**, including the two corrected evidence notes.

## 2. The standing verification rule (goes in every PR's verification section)

> **Every proof asserts the terminal outcome** — the slip graded at the leg's
> own odds, the bank arithmetic, the persisted state — **never merely "no
> error" or "a key matched".** A proof that can pass while the slip voids is
> not a proof of settlement.

Named as the second instance of that class this round (the first: the
flag-gate baseline that compared code with itself). The N-1(b) adversarial arm
is the model going forward: with the guard disabled the slip *does* book the
wrong fixture's loss, which is what makes the guard load-bearing rather than
decorative.

## 3. Rulings

| Ask | Ruling |
|---|---|
| A1(a–e) | **ACCEPTED.** One note for the PR: the refusal path lands inside the code's own fail-closed doctrine ("a conflict leg never counts as a loss") — refusing to book is the correct failure direction, and that is one line in the PR. |
| A2 | **ACCEPTED.** The two production rebinds are left alone (behaviour, not hygiene). Known wart recorded: `capture()` mutates `source._MAX_FETCHES_PER_RUN` for the process lifetime — safe today because `daily.py` shells the capture out into its own process and the picks-side rebind is deliberate. No action this round. |
| A3(b) | **CLOSED** — see §1.2. |
| A5 | **ACCEPTED**, including the two note corrections. |
| Self-corrected N-1(c) | **ACCEPTED.** §2's rule applies to the rewritten artifact. Keeping the old wording visible in `CLOSEOUT-ANSWERS.md` §2 (corrected, not dropped) is the retract-don't-re-explain rule working. |

## 4. Freeze and standing (as instructed)

* **Freeze the chain at `c23d77d`.** No further local evidence rounds; no
  starting PR #2's content before PR #1 is open.
* The only permitted work was: A4 (the excerpt relay — hash
  `b1a4b33d97fc45306033a6a0cbf196c7afcdc667bada3f6eeb72cf5b1bcbb732`, else
  the cross-agreement label stands) and the push-report items (A3a/c/d/e).
* Hold for **#61**. After the operator merges: rebuild onto merged `main` →
  re-print the gate (six pinned originals + three attribution rows) at the
  pushed SHA → **§6 report for rounds 2+3 at that SHA** → **PR #1** (capture +
  static floors) → **PR #2** (dynamic floors) → **PR #3** (round 5, as
  amended). No squash before review; never push `main`; `.github/` diff stays
  0; every pre-reset hash stays void.

**Local note (2026-10-12, same hour).** Between the memo and this record the
sandbox re-cloned: the 32 local commits are gone (they were never pushed — no
push before #61), so `c23d77d` exists nowhere. The **content** survived and was
verified byte-identical (nine-file table, 32-file bundle SHA256SUMS, the A1/A2/
A5 markers). The freeze is honoured: nothing was rebuilt and no evidence was
re-run; the rebuild happens at the post-#61 step, where rule 33 (re-clear the
§1 gate, republish the hashes at the new tip) applies to the rebased series.

# Edge Factory — round 6E: nothing merged (verified); `main` moves by design; 6D ruled IN, pre-handover

**Recorded in-repo 2026-10-12 from the round-6E ruling text as received in the operator's
message.** It is the standing instruction for the rest of this round: **R3 → `w6` re-run →
6D (bounded, §3) → suite → R4 handover.**

**From:** the reviewer (operator's side) · **Date:** 2026-10-12 · **To:** the agent
**Re:** the `57353fc` push report + the two questions

## 1. Both questions, independently verified on the reviewer's side

**(a) Nothing merged.** The PR's own commit list shows head **`57353fc`** — "handoff: record the
6D ledger addendum as received", committed minutes ago — and `main`'s history contains **no merge
of #61**: the newest merge commit on `main` is **#60** (`52145fa`, ~17h ago). The agent's
`state=OPEN mergedAt=— head=57353fc mergeable=MERGEABLE mergeStateStatus=CLEAN` reading stands.

**(b) `main` moved because the pipeline persists state on every run — by design.** Measured: seven
`chore: persist pipeline state (run …)` commits by `github-actions[bot]` in ~17 hours
(`38190166494` · `38191754228` · `38201987279` · `38215352337` · `38233510630` · `38252639775` ·
**`38274288117` = `1eaabee`**, the tip). Zero code commits since the #60 merge. So: not a merge,
not a rebase, nothing to reconcile — but it does mean **the base moves under the PR continuously**,
and the same service step will push state commits **onto the branch** when the operator dispatches.
That changes the merge-time picture — see §4.

## 2. R1 restore — ACCEPTED

Fourth reset, history objects gone, working tree intact: fetch → `git reset --hard 50c2a7e` →
before/after manifest **0 content changes, 110 additions**, all of them the chain's own untracked
files. Suite **2925** in the recreated `.venv` (Python 3.11.2), nine-file table and registry/ledger
hashes matching the published values, `.github/` diff 0, forbidden pair 0, `localdata/` clean. That
is the correct restore protocol — measure, then move; never `reset --hard` blind.

**One accuracy item:** the PR body's own head line still reads `head 607de7a (24 commits on
8e50de2)`. It is stale by two pushes. Update the head + commit count (and the base line to
`1eaabee`) at **each** checkpoint — a reviewer reading the PR must not have to guess which revision
the body describes. Same rule as the revision-anchored hashes.

## 3. 6D — RULED IN for this round, before the handover

Your question: implement now or wait. **Now** — because of the operator's own constraint: *anything
not on the branch before the merge never lands*. "After the dispatch" is too late: pushing then
would change the tree the operator just validated, which is precisely the back-and-forth they are
trying to avoid. So the order is: **R3 → `w6` re-run → 6D → full suite (CI-exact + seeds) →
handover line.**

6D stays exactly as scoped in the addendum (report-only w.r.t. certification; no team-total
pricing; no floor derived from unpriced history) plus **one guardrail found while checking the
constants**:

**Trim-safety.** `MAX_PROCESSED_KEYS = 1600` (`enh_registry.py:51`, trim at :220) and the audit's
default rescan window is `--days 30` (`audit_recent_picks.py:2417`). Adding unpriced keys
multiplies `processed` growth ~3–4×, and **a trimmed key that gets rescanned would re-record a
priced outcome — double-counting certification**. So:

- print, per market, the **keys that fall inside the 30-day rescan window** and compare against
  1600 (measured order of magnitude from the archives: `match_over_25` ≈ 265/30d, team-total
  markets ≈ 370/30d — print the actuals);
- state the safety condition explicitly: *max keys per market in any rescan window <
  `MAX_PROCESSED_KEYS`*, and add a test that fails if a per-market 30-day count ever crosses the cap;
- if a market does not satisfy it, keep unpriced keys in a **separate capped list** rather than the
  shared `processed` (and say so), so certification dedup is never at risk.

Also required, unchanged from the addendum: certification fields (`n`, `hits`, `records`, `profit`,
`inv_price_sum`, status transitions) **byte-identical** before/after on the committed registry;
`processed` grows by exactly the unpriced keys; a test that an unpriced outcome never moves a
status; the per-label reconciliation print (`recommended` vs `processed` vs `priced_n`); the
never-priceable class labelled in the performance view; one line in the PR body naming the
certification-ledger vs measurement-ledger distinction.

Nothing else from the addendum; no scope growth. If any of this turns out to need more than a
bounded change, **stop and report** rather than building.

## 4. Merge-time protocol — new, because both sides write state

The branch **does** modify `localdata/` (the league/team backfill touches
`localdata/enhancement_registry.json`), and `main` keeps writing state into the same file daily.
Today GitHub computes **CLEAN**, but that can change the moment the dispatch run pushes its own
state commit onto the branch. Protocol:

1. **Before posting the handover:** re-check `mergeable` / `mergeStateStatus` and report both with
   the head SHA.
2. **After the operator's dispatch** (the run pushes state commits to the branch) — the operator
   re-checks; if it flips to `DIRTY`, the conflicts will be **state data, not code** (verified:
   `main` has had no code commits since #60). Resolution rule, to be pre-written into the PR body
   so nobody improvises:
   - conflicted file under `localdata/` → **data merge**: keep every record from both sides — the
     branch's added fields (league/team keys) plus main's newest records. Never resolve by deleting
     one side's records.
   - conflicted file anywhere else → **stop**; that would mean code diverged, which contradicts the
     measurement above; report it, do not pick a side.
3. **Do not rebase the branch onto `main`** unless the operator asks — it rewrites the reviewed
   SHAs and would invalidate the dispatch. If a rebase is ever ordered, it happens **before** the
   dispatch, never after.
4. In the handover, include the list of `localdata/` files this chain touches (`git diff --stat
   origin/main...HEAD -- localdata/`), so the person resolving a conflict knows exactly which files
   are data.

## 5. Where this stands

- PR #61: OPEN, head `57353fc`, `MERGEABLE` / `CLEAN`; nothing merged; the relay check no longer
  blocks.
- Remaining pre-handover work, in order: **R3** three-arm count-neutrality proof → **`w6`** re-run →
  **6D** (bounded, §3) → suite → **R4 handover** (`ref · final head SHA · PR URL · READY FOR
  DISPATCH`), plus the §4 re-checks in the handover.
- The operator dispatches; the dispatch's state commits stay; no rebase away, no force-push; the
  merge is theirs and happens only after the dispatch is green.

# Handoff status — BetExplorer capture → enhancement lane (2026-10-12, round 6)

My working notes for this task, kept inside the repo so a sandbox reset cannot lose them.
**Not part of any PR** (untracked; never staged). The reviewer's checks live in the
operator's briefs (the chat memos; the reviewer's own files died with earlier resets).

## Where things stand — after the round-6 push (R1 complete)

**The chain is pushed.** `arena/3c65f248-edge-factory` = **`607de7a`** on the remote
(`8e50de2..607de7a`, fast-forward, 24 commits, never squashed). PR #61 is OPEN,
head = the pushed tip, title/body rewritten to the sectioned round-6 scope (nine
sections + "single merge by the operator; the chain is the unit of review").

Round 6 changed the standing rule: **everything lands before the single merge.**
The old freeze (#1/#2/#3 sequencing) is withdrawn; the merge is the vehicle's end,
and it also ends this session's push access — so nothing may be left unpushed.

**Verified at the pushed tip** (`607de7a`):

* nine-file sha256 table — matches the frozen table exactly (`.gitignore`
  `777a4440…`, licensing `ffb49937…`, capture `9eb63ddc…`, clean_localdata
  `d7462151…`, picks_today `fca50511…`, match_snapshot `5ea9a4e5…`, odds
  `648f690c…`, test_match_detail `bfbbc1d9…`, politeness `40c094f4…`);
* `bash handoff/round5_form_h2h_2026-10-12/c_patch_gate.sh` → exit 0, six
  never-contended + three contended re-printed with attribution to THIS chain;
* suite: `pytest tests -q -p no:randomly` → **2907 passed** (59.07 s at the final tip);
  seeds 1, 2, 3, 7, 13 → **2907 passed** each;
* owed items landed: `handoff/s45_politeness_lines.{py,txt}` (§4.5) and
  `handoff/s46_drift_remeasure.txt` (§4.6, second fixture `lKAT82nf`, 0.50 line +
  strip only — the rest of the lines stay unverified this round);
* self-caught and repaired: the first §4.5 driver wrote real `localdata/` state;
  both tracked files restored from `HEAD`, the new untracked ledger deleted, and
  the driver now redirects both module-level `LOCALDATA`s to scratch (commit
  `607de7a`);
* `.github/` diff vs `8e50de2` = **0**; `localdata/` untouched; the two forbidden
  files untouched; working tree clean except this file.

**The chain (22 commits, subjects as printed by `git log`)** — the four subjects
recovered verbatim from the chain's own in-repo citations are `capture: the
reviewer's record-depth patch, applied via git am -3`, `receipt: keep the
row-refusal census the patch's whitelist dropped`, `pricing: the captured ledger
reaches the board behind the flag`, `capture: read the whole form block the page
serves` (cited by `n3_tip_prints.sh`, `c_patch_gate.sh`, `w6_flag_gate_rerun.sh`,
`a3b_whitelist_table.txt`); the rest carry the round's theme names because the
pre-reset SHA/subject table died with the third re-clone. Every pre-reset hash
stays **void**.

## Next (round 6, in order)

1. **R2 — dynamic floors, pre-merge (NEXT).** Build to the round-4 brief
   (`handoff/AGENT-INSTRUCTIONS-4.md`) **re-measuring its numbers first** —
   **that file is NOT in this workspace** (verified: `ls handoff/`), so this item
   is blocked pending the operator relaying it. Spec as it survives: market level,
   evidence gate + Wilson lower bound, **tighten-only**; league level only after
   the `league` field is recorded and backfilled, coverage % reported; team level
   **report-only**; no lookahead; derivation written into the slip; auditable;
   distinguishable commit set with its own proof subsection; acceptance = the
   harness A/B on **mean log growth per bet-day**.
2. **Owed reports at the FINAL pushed SHA**: §6 rounds 2+3 raw output, §4.5
   politeness receipt lines, §4.6 drift re-measure, the w6 flag-gate re-run, the
   N-1 reprint, the nine-file table.
3. **R3**: the `capture_oddspapi.py` one-liner lands **only** with the three-arm
   count-neutrality proof (byte-identical receipt with transport recording; the
   handler records the 429 when the transport is bypassed; no path double-counts);
   any arm failing → dated PR-body follow-up, shipped code untouched. The relay
   check (`Workers Builds: edge-factory-source-relay`) is not chased; re-report
   its status after the final push.
4. **R4 — handover**: only after R2 + the owed items and a green suite: post
   `ref` · final head SHA · PR URL · **"READY FOR DISPATCH"**, nothing else. After
   the operator's run pushes state commits: no rebase, no force-push, no reset;
   `git pull --rebase` (fast-forward only); any run failure fixed pre-merge.
5. A4 stays optional (excerpt sha256 `b1a4b33d97fc…`); the terminal-outcome rule
   stands (every proof asserts graded odds / bank arithmetic / persisted state).

## Environment / scratch

* `.venv` is excluded from workspace snapshots — recreate with
  `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` plus
  `pytest`/`pytest-randomly` for the shuffled runs.
* The rebuild tooling lives in `/tmp/rebuild6/` (`states.py`, `states2.py`,
  `build.py`, captured gate output). `/tmp/final6` is the verified content
  snapshot; `/tmp/post6` the patch post-image. All disposable once the chain is
  pushed — the pushed SHA is the authority.
* `localdata/card_enrich_call_ledger.jsonl` matches `HEAD`; the two
  card-enrich files stay untouched. `.github/` is never written.

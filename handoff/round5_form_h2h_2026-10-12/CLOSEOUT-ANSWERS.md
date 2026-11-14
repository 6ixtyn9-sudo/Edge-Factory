# Round-5 close-out — the six answers, with the command that reprints each

Written 2026-10-12 at local tip `ae53870`, then updated once more (§0) at
`b7a3f56`. Nothing here is pushed: the brief holds every push until PR #61
merges. Every claim below is reprintable from the repository root with the
command named in its section; the raw output lives in the artifact named
beside it.

## 0. The chain at this tip

* The chain's length and tip cannot be written here truthfully - every commit
  that edits this file changes both - so they are printed, never stated:
  Reprint: `git log --format='%h %s' 8e50de2..HEAD | tac` (and
  `git rev-list --count 8e50de2..HEAD` for the count).
* `.github/` diff vs the parent is **0 lines** (rule 2).
  Reprint: `git diff 8e50de2..HEAD -- .github/ | wc -l`
* Full suite at the tip: **2902 passed, 0 failed** (`-p no:randomly`).
  Reprint: `PYTHONPATH=src .venv/bin/python -m pytest tests -q -p no:randomly`
* The two commits the round-5 brief names are in the chain: `45c8f30 capture:
  read the whole form block the page serves` and `adea694 intel: form/H2H
  features, coverage and signal test`.

## 1. §1 / gate C at this tip

* Reprint: `bash handoff/round5_form_h2h_2026-10-12/c_patch_gate.sh` →
  `c_patch_gate.txt` (exit 0).
* The patch itself: `edc6b096…`, 96,156 B — unchanged; the operator's
  96,155 B / `e685e1a1…` figure was never byte-resolved and the patch is
  accepted on functional evidence.
* Per-file verdicts at this tip: three files IDENTICAL to the patch's
  post-image (`.gitignore`, `scripts/clean_localdata.py`,
  `tests/test_betexplorer_politeness.py`), five DIFFERS-with-the-commits-that-
  touched-them-named (`docs/operator/BETEXPLORER-LICENSING.md`,
  `scripts/capture_betexplorer.py`, `scripts/picks_today.py`,
  `src/edgefactory/sources/betexplorer_match_snapshot.py`,
  `tests/test_betexplorer_match_detail.py`), and one CONFLICTED-and-resolved
  keeping both sides (`src/edgefactory/sources/betexplorer_odds.py`, 3 hunks,
  all both-sides-added). Drift is named, never repaired.
* Four files drifted from the patch post-image for named, committed reasons
  (the list above already names the commits; the two census-era ones are
  `c1538ca` and `51003d8`), and `src/edgefactory/sources/betexplorer_odds.py`
  is the conflicted file resolved by hand, keeping both sides. Nothing was
  "repaired" toward a recorded hash.
* **Pre-reset per-file hashes are void.** The chain was rebuilt after a sandbox
  reset; four files (`capture_betexplorer.py`, `BETEXPLORER-LICENSING.md`,
  `picks_today.py`, `test_betexplorer_match_detail.py`) were reconstructed at
  function level from the patch post-image plus the round's own documented
  edits, so their pre-reset tip hashes (`21add003…`, `16761aa7…`, `56bd6569…`,
  `5b4b1f00…`) do **not** reproduce. What IS verified: the C1 commit's blob for
  each of the four is byte-identical to the patch's post-image, and every
  subsequent difference is a real, committed diff (commit 2 of this chain
  onwards). `src/edgefactory/sources/betexplorer_match_snapshot.py` does
  reproduce its pre-reset tip hash byte-exactly (`5ea9a4e5…`).
* Nine-file sha256 table at this tip: `n3_tip_prints.txt` §(d).

* Both sha256 artifacts (`n3_tip_prints.txt`, `c_patch_gate.txt`) name the tip
  **at the moment they were run**. They cannot name the commit that carries
  them - writing the file changes the tip - so the label always lags by at
  least one commit; read the tip and then verify the nine hashes at whatever
  tip you are on (`sha256sum <file>` per line of the table, or re-run the
  scripts). At this file's tip the nine hashes are the ones the table prints:
  re-measured here after the A2 test edit, `scripts/capture_betexplorer.py`
  `9eb63ddc…`, `scripts/picks_today.py` `fca50511…`, `scripts/clean_localdata.py`
  `d7462151…`, `betexplorer_match_snapshot.py` `5ea9a4e5…`,
  `betexplorer_odds.py` `648f690c…`, `test_betexplorer_match_detail.py`
  `bfbbc1d9…`, `test_betexplorer_politeness.py` `40c094f4…`,
  `BETEXPLORER-LICENSING.md` `ffb49937…`, `.gitignore` `777a4440…`. The push
  re-print is the authority for the pushed SHA.

## 2. N-1 — the persisted-key blast radius

Reprint: `PYTHONPATH=src .venv/bin/python handoff/n1_persisted_keys.py` →
`handoff/n1_persisted_keys.txt` (re-ran at this tip: byte-identical).

* **Enumerated sites** (each named symbol checked to exist in the tree): the
  main lane's `open_slips[].accas[].legs[].fixture_key` (a RAW triple, written
  by `auto_tickets._stamp_fixture_keys`, re-folded at settle — recomputed at
  read, safe); the enhancement lane's same field (a FOLDED key written by
  `auto_tickets.enhancement_legs` — compared against a recomputed value, the
  one storage that needed acceptance); `coverage_inventory.json`'s
  `source|date|key::key|market` rows (persisted and compared;
  `remine.source_row_key`); `phase5_shadow/rows.jsonl` identity keys
  (persisted, churn, not joined — nothing reads them for settlement);
  the purity and ml-fade registries (frozen by construction, `fold_tokens=
  False`); the width-24 scored-candidate ledger and the CLV audit's
  odds-matching keys (their key functions never fold the token).
* **Acceptance** (b): `identity.migrate_folded_key` + `auto_tickets.
  leg_lookup_keys` + `LEGACY_KEY_HITS`; the migrated spelling is a read-only
  lookup candidate behind the primary key, recorded when it answers, never
  written back. Five tests in `tests/test_settlement_fixture_identity.py`
  (24 passed in that file).
* **Lifecycle proof** (c): `handoff/n1_legacy_leg_proof.{py,txt}` — a slip
  frozen with the pre-fold key of `Sutton Utd` (fixture 2026-07-14, Tonbridge
  Angels vs Sutton Utd, from the committed settled archive) settles across the
  fold: primary MISS, compatibility HIT, and the acca **grades** at the leg's
  own odds (1.9, bank 100.0 -> 109.0), not through the all-void stake-back
  path. **Correction, self-caught:** the first version of this proof passed an
  empty settled mapping, so `pick_result` returned "not known yet" and the
  slip resolved through the 5-day VOID timer (odds 1.0, stake back). The
  earlier close-out wording ("booked") did not distinguish those two paths.
  The proof now builds its settled mapping from the settlement's own key
  specs and asserts `odds == 1.9`, so "the leg graded" is a measured claim.
* **A1(a) primary-first and scoping**: the artifact prints the settle loop's
  guard as source (`inspect.getsource`, symbol-cited) and replays the lookup
  order against a real index (primary miss -> candidate hit); the migrated
  candidate is asserted to carry the stored day and pick, so it cannot reach
  another day's or another market's row. A leg whose stored identity the
  current fold reproduces gets ONE key - there is nothing else to consult.
* **A1(b) the adversarial collision**: a same-day pair whose keys collide
  (`Newcastle Utd` vs a different club `Newcastle United`). Guard ON: the
  other club's row is REFUSED (`LEGACY_KEY_REFUSED`, with the reason on the
  record and a `compat key REFUSED` line), the leg holds inside the void
  window and VOIDS outside it - never the other score. Guard OFF
  (monkeypatched in the artifact and in no shipped path): the same slip books
  the other fixture's loss at the leg's odds. Pinned by
  `tests/test_settlement_fixture_identity.py::
  test_a_compat_candidate_never_grades_another_fixture` plus the control that
  the SAME collision settles when the row is the leg's own fixture.
* **A1(c) no write-back**: `test_the_compat_tier_leaves_stored_keys_untouched`
  asserts the lookup does not mutate the leg and that the migrated spelling
  never appears in the written state file.
* **A1(d) the trail**: `LEGACY_KEY_HITS`/`LEGACY_KEY_REFUSED` are audit
  records (slip date, primary, matched, stored, resolved fixture, pick, the
  leg's match string; refusals carry `refused_because`), and every use is also
  a settlement line naming both keys and the resolved fixture - so the audit
  is reconstructible without re-running the resolver.
* **A1(e) sunset**: a dated TODO sits above the tier's helpers with the
  removal criterion (0 hits on the `settlement_compat_key_hits` scalar for 14
  consecutive settlement runs AND no open slip's stored key failing the
  current fold), the void-timer basis (5 days, `_slip_day_anchor`), and the
  command that reprints both checks. The scalar prints on EVERY settlement run
  (zero included) on the established `settlement_*` run-log channel; the
  per-leg human lines stay out of `lines` unless a leg actually used the
  tier.
* **Churn** (d): of the 120 phase5 stored keys that differ from a recomputation
  today, **14 are the fold** (`suttonutd` → `suttonunited`,
  `persepammadurautd` → `persepammaduraunited`) and the rest are older-rule
  evidence reported as found, not counted here. `coverage_inventory.json`
  stores 0 keys embedding a foldable token; `auto_tickets_state.json` stores
  4 legs, all RAW triples; `enhancement_tickets_state.json` is absent from the
  workspace (its legs are folded by construction, which is what the
  compatibility tier exists for).

## 3. N-2 — the training-window constant row (finding, verbatim)

Reprint: `PYTHONPATH=src .venv/bin/python
handoff/round5_form_h2h_2026-10-12/intel_report.py` → `w5_signal.txt`
(and `bash handoff/round5_form_h2h_2026-10-12/w35_width9_rule.sh` for the
width-9 reading). Nothing was tuned; `w*` is chosen exactly as before.

Verbatim from `w5_signal.txt`:

```
== over_25 (match_over_25) — settled n=350  hits 231/350
  base rate on the same slice: hits 80/126 -> constant-predictor Brier h(1-h) = 0.2318  (the minimum bar; above it is a calibration red flag)
  base rate on the TRAINING slice: hits 151/224 -> constant-predictor Brier h(1-h) = 0.2197  (the same bar on the window w* was chosen on)
  reading: (b) vs (a) blend no better; (c) vs (a) market scores better, not significantly on this sample.
```

| market | test slice | train slice |
|---|---|---|
| over_25 | 0.2318 (80/126) | 0.2197 (151/224) |
| over_15 | 0.2222 (8/12) | 0.1814 (16/21) |
| over_35 | 0.2449 (3/7) | 0.1728 (2/9) |
| btts_yes | 0.2449 (4/7) | not applicable (no split) |
| away_under_25, away_under_35, over_45 | n=1 each, noise | not applicable (no split) |

The train bar is lower than the test bar in every market with a split, so the
model's position above the test bar is not an artefact of the split. The
verdict stands: no signal; do not wire it.

## 4. N-3 — the keep-both proof at the tip

Reprint: `bash handoff/round5_form_h2h_2026-10-12/n3_tip_prints.sh` →
`n3_tip_prints.txt` (exit 0, re-run at this tip).

1. `scripts/picks_today.py`: the #61 rescue flow and both
   `stats.update(_be_mod.run_stats())` / `stats.update(_be_mod.request_stats())`
   with their line numbers (gate line 6233; the two calls at 6283 and 6286).
2. `src/edgefactory/sources/betexplorer_odds.py`: `run_stats()` 5 fields,
   `request_stats()` 3 fields, union 8 — the receipt's whitelist is a superset
   (it also carries `be_fetches`); 13 marker counts with lines; constants
   `_MARKET_INTERVAL=5.1`, `_MAX_MARKET_ROWS=48`, `_MAX_MARKET_LINES=10`,
   `_MAX_H2H_ROWS=40`, `_MAX_STANDINGS_ROWS=40`.
3. Politeness: the patch's own module `tests/test_betexplorer_politeness.py`
   (5 tests) **plus** the second module the patch touches,
   `tests/test_betexplorer_match_detail.py` (20 tests) — collected at this tip,
   names printed.
4. Nine-file sha256 table at this tip + the six attribution rows, which cite
   this chain's commits.

## 5. Ruling 10 — the harness, the superseded artifact, and provenance

* `handoff/round5_form_h2h_2026-10-12/w6_flag_gate_rerun.sh` is committed and
  was **re-run at this tip** (exit 0). Its baseline worktree commit is now
  derived from the chain by the stage-1 commit's subject; the hard-coded
  pre-reset SHA that a sandbox reset deleted is gone, and the harness refuses
  to guess a baseline (that refusal is the fix: a "baseline" run that silently
  compares the current code with itself).
* Results (`w6_flag_gate_rerun.txt`): baseline (pre-stage-1 code) vs flag-off
  **IDENTICAL**; flag-off vs flag-on **DIFFERS** (55 content lines, 67 diff
  lines); the committed board card off vs on **IDENTICAL**; the labelled probe
  card moves 0 → 1 eligible leg (Coventry BTTS @ 1.57, below the 1.85 floor).
* The superseded artifact is marked: `docs/operator/BETEXPLORER-LICENSING.md`
  keeps the original "Consumption in that build: none" bullet and labels it
  "(Superseded by the Stage 1 consumption bullet further down.)".
* Provenance, plainly: **bash has no route to betexplorer.com in this sandbox.**
  Every page fact in this round came through the fetch tool, which returns the
  page's rendered text (raw HTML bytes are not retrievable, so attribute-level
  facts stay unverified). The page was read live twice today — for A-1/W1 and
  again for §4.4 — and those are read-time values; per-row odds drifted between
  the reads and both reads are on record. Everything else (archives,
  registries, state files, board cards) is a stored artifact, read through
  `git show origin/main:<file>` or from the committed tree, and is labelled as
  such wherever it is quoted.

## 6. §4.4 — the excerpt reproduction

Reprint: `PYTHONPATH=src .venv/bin/python handoff/s44_excerpt_repro.py` →
`handoff/s44_excerpt_repro.txt` (re-ran at this tip: byte-identical).

* The reviewer's own excerpt (sha256 `b1a4b33d…`, 118 lines) is **not in this
  workspace** — it died with the sandbox reset — so the script runs the
  production parser (`parse_match_page_blocks`, `parse_page`) over the agent's
  own fresh render, `handoff/live-excerpt-tW4rOkzg-2026-10-12.txt`
  (`cbba408e…`, 6,738 B), and says so at the top of its output. Nothing is
  attributed to the reviewer's bytes.
* Stored from that render: blocks `['h2h','last_results','standings']`;
  `h2h_meetings=6`; `h2h_record {0,1,5}`; 20/20 H2H rows with their per-row
  closing odds; 10/10 form rows over two labelled blocks; 20/20 standings rows
  with the page's own columns; `header_verified=True`; score/position/prices
  `None` by design.
* The label against the list: the block is labelled "Head to Head: Last 6" and
  the page serves 20 dated meetings (1993–2010). The 0/1/5 summary is not the
  newest six either — those six are all Newcastle wins (0/0/6), so the summary
  window is not the newest six. `h2h_meetings` stores the summary integer,
  `h2h_rows` the dated list; neither is a claim about the other.
* Explicitly **unverified**: attribute-level facts (`data-oid`,
  `data-bt`/`data-sc`/`data-hcp`, best-price flags, tbody ids), the drift of
  read-time odds, and the reviewer's excerpt bytes.

## 7. The standing items the brief carries (§4.5, §4.6) — where they are answered

* **§4.5 politeness.** The module's own lines: `_MARKET_INTERVAL = 5.1` (market
  tabs, wider than the priced lane), `_market_budget_stop` flipped at the run
  request budget and surfaced as `request_stats()["market_budget_stop"]`, which
  the receipt's whitelist carries, so a budget stop is printed in the run log
  rather than inferred. The test sets that pin this are the two named in §4
  above (5 politeness tests, 20 detail tests).
  Reprint: `bash handoff/round5_form_h2h_2026-10-12/n3_tip_prints.sh` (`(b)`
  and `(c)` sections).
* **§4.6 drift re-measure.** The match page's per-row closing odds are
  read-time values and drift between two reads of the same page on the same
  day. Measured, verbatim from `handoff/s44_excerpt_repro.txt`:
  "this read shows 1.45/3.99/7.50 on 17.02.2010 where the earlier read today
  showed 1.44/4.20/7.50, and 1.64/3.88/5.49 where the earlier read showed
  1.64/3.87/5.52". A stored triple is what the page said at that moment, never
  a fixed fact — the capture stores it with the read's own stamp, and no
  downstream read treats it as revisable history. Reference books this round
  quoted for the same fixtures (bet365.us, BetMGM.us, Stake.com) are read-only
  references; nothing fetches them.
* **The three contended slices, named.** The six attribution rows in
  `n3_tip_prints.txt` §(d) cover the round's edits; the three that the patch's
  own review flagged are the odds adapter (3 both-sides-added hunks — the
  conflict, resolved keeping both sides, row `<- ff49617`), the licensing doc
  (the Stage-1 consumption bullet lands on the patch's own "Consumption: none"
  text, row `<- 3458653`) and `picks_today.py` (the rescue-ordering/price-index
  move, row `<- 3458653`).

## 7b. A2 — the leak-class sweep

Reprint: `bash handoff/round5_form_h2h_2026-10-12/a2_leak_sweep.sh` ->
`a2_leak_sweep.txt` (exit 0).

* The mechanism, in shipped code: `scripts/capture_betexplorer.py` (capture():
  `source._MAX_FETCHES_PER_RUN = limit`) and `scripts/picks_today.py` (the
  enrichment entry point: `_be_mod._MAX_FETCHES_PER_RUN = max(0, int(...))`).
  Both are deliberate for one real run in one process and are left alone:
  changing them is behaviour, not hygiene. They are named, not touched.
* Tests: no test rebinds a budget global with a bare assignment. Two hits were
  found and dispositioned: `tests/test_betexplorer_match_detail.py`'s
  `be._request_count = 4` (a run counter, now `monkeypatch.setattr`, so pytest
  restores it) and `tests/test_oddspapi_catalog_resolution.py`'s three catalog
  globals - a DIFFERENT module, restored in a `finally` to that module's
  documented empty/fallback state (restoring to the default IS the correct
  restore there), reason recorded in the sweep.
* The systemic half: `tests/conftest.py` now snapshots the adapter's budget
  globals AND its run-scoped scalars before every test and restores them
  after (`_restore_budget_globals`), so a test cannot inherit another test's
  value even when the change came from a production entry point it merely
  called; and a session-scoped autouse alarm
  (`_budgets_end_at_their_defaults`) fails the session if it ever ends with a
  budget a real run would not see.
* The restored dated claim is pinned by `tests/test_dated_claims_ledger.py`
  (26 passed), whose scan is the reason the claim lives in a comment:
  `tests/test_betexplorer_match_detail.py::
  test_receipt_keeps_the_row_refusal_census`.

## 7c. A3(b) — the receipt-whitelist reconciliation

Reprint: `bash handoff/round5_form_h2h_2026-10-12/a3b_whitelist_table.sh` ->
`a3b_whitelist_table.txt` (exit 0). The reviewer's 7-key literal is the
patch's literal **verbatim**; the table prints both literals, both producers
and the pinning test per key:

| reading | keys |
|---|---|
| the patch's literal (and the reviewer's reconstruction) | `be_429`, `be_cooling_down`, `be_cached`, `be_fetches`, `requests`, `market_requests`, `market_budget_stop` = **7** |
| `run_stats()` at this tip | `be_429`, `be_cooling_down`, `be_cached`, `be_rows_rejected`, `be_rows_rejected_reasons` = **5** |
| `request_stats()` | `requests`, `market_requests`, `market_budget_stop` = **3** (union with the above = **8**) |
| `RECEIPT_STAT_KEYS` at this tip | the 7 above + the 2 census keys = **9** |

* The delta between the reviewer's 7 and the tip's 9 is exactly the two
  census keys, added by `c1538ca` (the round-2 §2.2 restore the brief
  required). Attribute it to that commit, not to the patch.
* N-3's "5 + 3 -> 8" is the **producer union** (both `stats.update(...)` calls
  in `picks_today.py`), not the whitelist length; the whitelist is a superset
  of it by exactly one key.
* That one key is `be_fetches`: in the patch literal, in the tip's whitelist,
  and produced by **nothing in any revision** - not on `origin/main`, not at
  the patch's post-image, not at this tip; the only code that mentions it is
  `tests/test_capture_betexplorer.py`'s stub of `run_stats()`, which is where
  the literal was copied from. Dead weight in a filter, pre-existing, neither
  added nor removed by this round.

## 7d. A5 — the six row-case-only pairs, tagged

`src/edgefactory/identity.py` now carries `evidence: row-case-only` on
exactly the six pairs whose join evidence is the row case rather than a mutual
fixture (`Accrington`, `Kidderminster Ha`, `Scunthorpe Unite`, `Mallorca`,
`Aris Thessalonik`, `Corvinul Hunedoa`); the other 14 pairs keep their mutual
evidence and the fold keeps its corpus audit. Confirmation grep:
`grep -c "evidence: row-case-only" src/edgefactory/identity.py` -> 6.

## 8. What is still pending (not this branch's to do)

* **A3's push-report items** are prepared but belong to the push itself: the
  commit list grouped by theme, the nine-file hash table at the pushed SHA,
  the three attribution rows, the five constants, the 13 marker counts, the
  14-churn one-liner with the no-settlement-reader greps, and both void
  declarations (pre-reset hashes and the four reconstructed files).
* **A4** stays open and optional: the relayed excerpt must hash to
  `b1a4b33d97fc45306033a6a0cbf196c7afcdc667bada3f6eeb72cf5b1bcbb732`; if
  transport normalises newlines, both hashes get reported. Until then the
  item keeps the cross-agreement label.
* **Push.** Held for PR #61. When it merges: PR #1 (capture + static floors),
  PR #2 (dynamic floors), PR #3 (this round, as amended) — and the push report
  will carry the fresh SHAs, the per-file sha256 list at the pushed SHA, and
  the raw artifact URLs. The §6 report for rounds 2+3 is written at that pushed
  SHA, not before.
* Nothing was pushed, no workflow was touched, `.github/` is unchanged, and
  `docs/operator/*.yml.proposed` remains the only form any workflow change
  takes.

# Handoff status — BetExplorer capture → enhancement lane (2026-10-12, round 6)

My working notes for this task, kept inside the repo so a sandbox reset cannot lose them.
**Not part of any PR's reviewed code** (it is a handoff note; the reviewer's checks live in
the operator's briefs in the chat).

## Where things stand — the R2 checkpoint set is built and green locally

**R2 (dynamic floors) is complete on this branch and about to be pushed as a
distinguishable checkpoint set** on top of `c77c803` (which is PR #61's current head and
the remote tip before this push):

| # | subject | what it carries |
| --- | --- | --- |
| 1 | `floors: derive per-slice floors from Wilson evidence` | `enh_registry.derive_floors` (pure) + `derive_floors_for_day` (fail-soft), `floor_for_slice`, `clears_floor(..., floor=)`, `FLOOR_BASIS_*`; `tests/test_enh_registry_dynamic_floors.py` |
| 2 | `registry: record league and team keys` | `record_outcome` gains `league/home/away/home_key/away_key` (additive, optional, dedup key unchanged) + the lane's call site |
| 3 | `registry: backfill the slice fields from the committed picks` | `scripts/backfill_registry_slices.py`; applied: 398/409 = 97.3 % attributed, 11 unmatched listed and still inheriting; registry `fb49e951…` → `ffc1655e…` |
| 4 | `lane: gate every leg on its slice floor, and print the derivation` | `enhancement_legs(..., floors=)`, `floor/floor_basis/league` carried through pool+plan (`_carry_lane_evidence`), `_enh_floor_lines()`, `st["enh_floor_table"]`, the board line in `picks_today` |
| 5 | `harness: slice-aware floor arms and the bet-day metric` | `replay_harness --enhancements --ab live derived`; mean log growth per **bet-day** + `MIN_ACCAS` no-bet frequency |
| 6 | `proofs: the nine R2 proofs at this tip` (+ evidence artifact) | `handoff/r2_proofs.py` / `.txt` — today: **ALL PROOFS PASS** |

**Rules the derivation obeys** (the pack, `handoff/AGENT-INSTRUCTIONS-6B-R2-RELAY.md`):
three levels market → league → team (team **report-only**); gate `n >= MIN_PRICED_N (30)`
**and** a usable Wilson lower bound; `floor = max(parent, 1/wilson_lb + margin)`,
**tighten-only** (loosening = operator ruling); margin = the table's own 0.10; no
lookahead (day D reads only records dated before D); no new literals; the derivation is
re-derivable and printed into slip/state.

**Derived table for 2026-10-12** (409 priced records, 398 with league+keys, margin 0.10):
`over_15` **1.8927 market** (a 72.7 % record does **not** lower it), `over_25`
**1.7424 market**, `btts` 1.85 and `over_35` 3.30 **inherited**; `away_under_25/35` and
`match_over_45` stay floorless; 213 league rows, 0 deviating; 696 team rows, 0 applied.

**Verified at this tip** (raw: `handoff/r2_evidence_at_tip.txt`):

* CI-exact (`PYTHONPATH=src python3 -m pytest tests/ -q`) → **2925 passed in 58.49 s**;
  shuffled seeds 1, 2, 3, 7, 13 → **2925 passed** each (the pack's floor is ≥ 2907;
  R2 adds 18 tests and loses none);
* nine-file table: eight rows identical to `607de7a`, **one moved and attributed** —
  `scripts/picks_today.py` `fca5051139c2…` → `81419280c181…` (commit 4: the board line
  now prints the floor and its basis). The pack predicted this move; this is the
  republished authority;
* C gate re-printed at this tip (scan of the six never-contended + three contended with
  per-file tip/parent/post-image hashes); the bundle's own `SHA256SUMS.txt` is 26/32 with
  **six stale driver hashes attributed to `c466729`** (the shared guard preamble), not
  re-signed;
* outbound probe re-run → exit 0, artifact byte-identical → **0**;
* `.github/` diff vs `origin/main` = 0; `localdata/` clean vs HEAD; the two forbidden
  card-enrich files untouched; `localdata/card_enrich_call_ledger.jsonl` = HEAD.

**Harness A/B at this tip** (`handoff/r2_harness_ab.txt`): mean log growth per bet-day —
live **−0.0154** (30 bet-days / 46 bets / 13 hits) vs derived **−0.0182** (21 / 26 / 6);
paired bootstrap median **+0.0029**, P(B>A) **54 %** — a wash at this sample, with the
derived arm betting a third less often (no-bet 36 % vs 29 %); the derived arm's small-n
caveat is printed in the artifact.

**Round-5 bundle** (unchanged, frozen): `handoff/round5_form_h2h_2026-10-12/` — its
`SHA256SUMS.txt` still validates 26/32 for the reason above.

## Next (round 6, in order)

1. **R3 — the `capture_oddspapi.py` one-liner, three-arm proof.** Lands only with all
   three arms green: byte-identical receipt with transport recording; the handler records
   the 429 when the transport is bypassed; no path double-counts. Any arm failing → a
   dated follow-up in the PR body, shipped code untouched.
2. **Owed reports at the FINAL pushed SHA**: §6 raw output for this round,
   `handoff/round5_form_h2h_2026-10-12/w6_flag_gate_rerun.sh` re-run (the relay check is
   not chased; its status is only re-reported after the final push).
3. **PR #61 body**: kept sectioned; the R2 checkpoint is appended as its own section with
   the commit SHAs above. **One merge by the operator; the chain is the unit of review.**
4. **R4 — handover**: post `ref` · final head SHA · PR URL · **"READY FOR DISPATCH"**,
   nothing else. After the operator's run pushes state commits: no rebase/force-push/reset;
   `git pull --rebase` (fast-forward only); any run failure fixed pre-merge.
5. A4 stays optional (excerpt sha256 `b1a4b33d97fc…`); the terminal-outcome rule stands
   (every proof asserts graded odds / bank arithmetic / persisted state).

## Environment / scratch

* `.venv` is excluded from workspace snapshots — recreate with
  `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` plus
  `pytest`/`pytest-randomly` for the shuffled runs.
* Scratch: `/tmp/r2/` (`proofs.out|err`, `harness.out|err`, `ci/`, `cgate_at_tip.txt`,
  `outbound.out`) — disposable; the pushed SHA is the authority. `/tmp/rebuild6/` holds
  the (now superseded) rebuild tooling.
* Demo drivers write real state, so every one of them runs under
  `handoff/scratch_localdata.py` (`guard_localdata()`) — scratch root only.
* `localdata/card_enrich_call_ledger.jsonl` matches `HEAD`; the two card-enrich files stay
  untouched. `.github/` is never written.

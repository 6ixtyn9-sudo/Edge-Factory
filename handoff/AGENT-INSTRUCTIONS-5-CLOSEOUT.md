# Round-5 close-out — the adjudication as it arrived, and where each item is answered

Recorded 2026-10-12. The close-out arrived in the conversation; the reviewer's two
files (`handoff/AGENT-INSTRUCTIONS-5-CLOSEOUT.md`, `handoff/live-excerpt-tW4rOkzg-2026-10-12.txt`)
are **not in this workspace** — their commits (`f36eed7`, `8554842`) died with a
sandbox reset, so their exact bytes cannot be verified here and nothing in this
round is attributed to them. This file is the agent's record of what they ruled;
the excerpt's replacement is `handoff/live-excerpt-tW4rOkzg-2026-10-12.txt`, a
fresh read of the same URL by the agent (see its own header).

## 1. The rulings, and the answer for each

| # | ruling | answered by |
|---|---|---|
| A-1 | wording corrected: every depth-region expander is a JS control with no href; every existing href is already on the never-fetch list | `src/edgefactory/sources/betexplorer_match_snapshot.py` (three comments), README "Rulings (closed)" §1, `w1_served_controls.txt` |
| A-2 | the `Utd` fold accepted, **gated to the source seam**, persisted-key layers untouched *subject to N-1*; six row-case-only pairs tagged | `identity.TEAM_TOKEN_FOLDS`, `entities` call sites pass `fold_tokens=False`, `tests/test_team_identity_transliteration.py`, N-1 below |
| A-3 | reserves kept distinct, labelled, nothing acts on the label | `identity.squad_markers`/`squad_marker_mismatch`, `form_intel` coverage labels, README §3 |
| B-2/B-3 | join coverage printed first; constant-predictor bar per market; wording "market-implied scores better, not significantly on this sample" | `intel_report.py` (w5), `w5_signal.txt` |
| B-4/B-5 | training-window constant row beside the test row; no tuning | N-2 below, `w5_signal.txt` |
| C | the six never-contended hashes + three contended files re-printed at the tip; drift = STOP | `c_patch_gate.sh`/`c_patch_gate.txt`, re-printed at this tip |
| Ruling 10 | commit the fixed flag-gate harness; mark the superseded artifact superseded; state live-fetch vs stored-artifact provenance plainly | `w6_flag_gate_rerun.sh` (committed), `BETEXPLORER-LICENSING.md` ("Superseded by the Stage 1 consumption bullet"), provenance section below |

## 2. The three follow-ups

**N-1 — persisted-key blast radius.**
* `handoff/n1_persisted_keys.py` / `.txt`: every site where a
  `source_team_key`-derived key is persisted, with writer and reader symbols
  (each symbol checked to exist), classified recomputed-at-read vs
  compared-against-stored; the committed artifacts scanned through
  `git show origin/main:<file>`; the working tree scanned separately.
* Measured: 5 committed files hold key-typed values embedding a foldable token
  (131 values); **14** of those keys move because of the fold (phase5 shadow
  identity keys) and 106 move for another reason (evidence written under an
  earlier key rule — reported, not counted as this round's churn).
* `identity.migrate_folded_key` + `auto_tickets.leg_lookup_keys` +
  `LEGACY_KEY_HITS`: a stored pre-fold key is accepted as a read-only lookup
  candidate *behind* the primary key, never written back.
* `handoff/n1_legacy_leg_proof.py` / `.txt`: the acca lifecycle proof — a slip
  frozen with the pre-fold key settles across the fold (primary MISS, compat
  HIT, booked, recorded); the primary key alone misses; the main lane's raw
  triples need no compatibility key at all.
* Tests: `tests/test_settlement_fixture_identity.py` (5 new tests).

**N-2 — the training-window constant row.** `intel_report.py` now prints the
constant-predictor Brier `h(1-h)` on the slice the weight was chosen on, beside
the test-slice row, and says "not applicable" where no split exists. Nothing was
tuned. Numbers: over_25 test 0.2318 (80/126) / train 0.2197 (151/224);
over_15 test 0.2222 (8/12) / train 0.1814 (16/21); over_35 test 0.2449 (3/7) /
train 0.1728 (2/9); btts and the n=1 markets: "not applicable". Verdict
unchanged: both the model and the blend sit above the bar on the test slice —
"no signal; do not wire it".

**N-3 — keep-both proof at the tip.** `handoff/round5_form_h2h_2026-10-12/n3_tip_prints.sh`
/ `.txt` prints, at this tip: (a) `picks_today.py`'s rescue flow and both
`stats.update(_be_mod.run_stats())` / `stats.update(_be_mod.request_stats())`
with line numbers; (b) the two stat field sets and their union (5 + 3 → 8, the
receipt whitelist adds `be_fetches`), the 13 marker counts with line numbers,
and `_MARKET_INTERVAL=5.1`, `_MAX_MARKET_ROWS=48`, `_MAX_MARKET_LINES=10`,
`_MAX_H2H_ROWS=40`, `_MAX_STANDINGS_ROWS=40`; (c) the two test modules the
patch touches with their test names and counts (5 politeness + 20 detail); (d)
the nine-file sha256 table at this tip and the attribution rows.

## 3. §4.4 — the excerpt

`handoff/live-excerpt-tW4rOkzg-2026-10-12.txt` (the agent's fresh render) and
`handoff/s44_excerpt_repro.py` / `s44_excerpt_repro.txt`: the production parser
(`parse_match_page_blocks`, `parse_page`) is run over the render, so what is
printed is what the parser would store — blocks (`h2h`, `last_results`,
`standings`), `h2h_meetings`, `h2h_record`, 20 H2H rows with their per-row
closing odds, 10 form rows over two labelled blocks, 20 standings rows with the
page's own columns, and the header verification.

* Label vs list: "Head to Head: Last 6" is a summary label, the page serves 20
  dated meetings, and the 0/1/5 summary is not the newest six (those six are all
  Newcastle wins — 0/0/6). `h2h_meetings` stores the summary integer, `h2h_rows`
  the dated list.
* Not reproduced here: attribute-level facts (the render is text, not raw HTML),
  per-row odds which drift between reads, and the reviewer's excerpt bytes
  (unavailable). Those stay **unverified**.

## 4. Provenance, stated plainly

Before the reset, the replay statement "no sandbox route to BetExplorer" and the
A-1/W1 claim "re-read live today" stood together in one report and read as a
contradiction. Both facts are true and distinct:

* **bash/curl have no route** to betexplorer.com from this sandbox; every
  "measurement of the page" in this round came through the fetch tool, which
  reads the page's rendered text (the raw HTML bytes are not retrievable).
* **The page was read live, twice today**, for A-1/W1 and again for §4.4; the
  values in those files are read-time values, and per-row odds are quoted with
  the drift between the two reads.

Stored-artifact claims (the archives, the registries, the state files) come from
`git show origin/main:<file>` and are labelled as such; the w6 flag-gate run
compares the working tree against a worktree at the recorded baseline and
refuses to run without it.

## 5. The FINAL memo (received 2026-10-12, as chat text)

`handoff/AGENT-INSTRUCTIONS-5-FINAL.md` and the commits the memo mentions
(`e87f856`, `38f7e56`) are **not in this workspace** - the sandbox re-cloned and
the reviewer's own commits do not appear here. The memo arrived as text; this is
the record of its rulings and where each ask is answered.

**Rulings.** N-1 ACCEPTED (read-only candidate behind the primary, never written
back) subject to A1. N-2 ACCEPTED with the one-line slice-stability caveat (the
base-rate bars imply slice hit rates that drop monotonically train -> test:
over_25 67.4% -> 63.5%, over_15 76.2 -> 66.7, over_35 77.8 -> 57.1). N-3
ACCEPTED as printed, with the pre-push gate re-print at the pushed SHA staying
the authority, subject to A3b. Ruling 10 ACCEPTED. Both self-caught items
(leak fix; the four reconstructions declared void) ACCEPTED. The six
row-case-only pairs still open -> A5. The reviewer's own re-measurements:
the leak mechanism is pre-existing at `capture_betexplorer.py` + `picks_today.py`;
the churn claim holds against committed data (`coverage_inventory.json` has zero
`utd` tokens; the token-bearing keys live only in `phase5_shadow/rows.jsonl`;
`auto_tickets.py` never reads that artifact); the void timer is 5 days.

**The five asks, and where each is answered.**

| ask | answer |
|---|---|
| A1(a)-(e) N-1 hardening | `handoff/n1_legacy_leg_proof.txt` (guard source, consultation order, collision arms, journal, sunset) + `scripts/auto_tickets.py` (`_prefold_leg_key`, `_compat_refusal`, `_compat_record`, `LEGACY_KEY_REFUSED`, `settlement_compat_key_hits`) + 5 tests |
| A2 leak-class sweep | `handoff/round5_form_h2h_2026-10-12/a2_leak_sweep.txt` + `tests/conftest.py` (per-test restore + session-end alarm) |
| A3(b) whitelist reconciliation | `handoff/round5_form_h2h_2026-10-12/a3b_whitelist_table.txt` |
| A3(a)(c)(d)(e) push-report items | prepared in `CLOSEOUT-ANSWERS.md` §7c/§8; the pushed SHA is the authority and they are re-printed there |
| A4 excerpt relay (optional) | open - the relayed file must hash to `b1a4b33d97fc...b732`; the item keeps the cross-agreement label until then |
| A5 row-case-only tags | `src/edgefactory/identity.py` (six pairs), confirmation grep in `CLOSEOUT-ANSWERS.md` §7d |

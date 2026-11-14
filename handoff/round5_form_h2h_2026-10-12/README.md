# Round 5 — the form block is read for what it serves; form/H2H features, coverage, signal test

Operator brief in one line: *"dont we get the last ten matches and the h2h info?
looks like we not using the info we have at our disposal smartly."*

Nothing here is wired into the money path. The price still sets value; no floors
are derived from form or H2H.

**Amended 2026-10-12 after the reviewer's adjudication** (rulings A-1…A-3,
corrections B-1…B-5, gate C). What changed: the "links to further server
responses" claim was retracted (A-1), the identity seam gained the evidence-backed
spellings and one deterministic token fold (A-2), reserve sides are labelled and
keep their own keys (A-3), W5 reports its join coverage and the constant-predictor
base-rate bar (B-2/B-3), and the patch-transfer gate was re-printed at this tip
(C). Every amended number below was re-measured at the tip; the artifacts carry
the commands.

## Artifacts and how each is reproduced

| artifact | what it is | command |
| --- | --- | --- |
| `w1_served_excerpt.txt` | the served text around the form block, H2H list and standings block of `tW4rOkzg` (Coventry vs Newcastle Utd, 2026-10-12), verbatim spans + provenance | fetched 2026-10-12 by the page-fetch tool; bash has no route to betexplorer.com, so raw HTML bytes are not retrievable here |
| `w1_probe.py`, `w1_counts.txt` | what the blocks serve, counted: selector strip, active view, dated rows per side, H2H controls, quoted standings rows; and the capture's own parser over the in-repo match-page fixture | `PYTHONPATH=src .venv/bin/python handoff/round5_form_h2h_2026-10-12/w1_probe.py` |
| `intel_report.py` | offline driver: loads the committed archives + registry and writes the two files below | `PYTHONPATH=src .venv/bin/python handoff/round5_form_h2h_2026-10-12/intel_report.py` |
| `w3_coverage.txt` | per-fixture coverage: sufficient history per month and league, `insufficient_history`, name-matching misses, and the unjoined spellings that explain the thin sides | written by the driver |
| `w4_probe.py`, `w4_page_vs_archive.txt` | the page's own last-5 blocks vs the archive's last-5, every difference named, under both identity rules | `PYTHONPATH=src .venv/bin/python handoff/round5_form_h2h_2026-10-12/w4_probe.py` |
| `w5_signal.txt` | the decision gate: model vs model+form (shrinkage) vs market-implied, Brier + log loss with paired bootstrap CIs, out-of-sample | written by the driver |
| `w5_signal_width9_rule.txt`, `w3_coverage_width9_rule.txt` | the same driver with the identity read as the width-9 `norm_team` bucket (every other change of this round held constant) — see the provenance header in each file | module copy aliasing `source_team_key = norm_team`, driver run from that root |
| `a1_served_controls.txt` | A-1: the control lines, both 5-row blocks, both hrefs the block serves, and the odds drift between the two reads | quoted from the 2026-10-12 page reads; raw HTML bytes are not retrievable here |
| `a_identity_checks.py`, `a_identity_checks.txt` | A-2/A-3: the layer table (`base` / `source key` / ledger key per spelling), the reserve check, the fold's blast radius with every merged group listed, the Al Ittihad by-league split, and the per-pair mutual-fixture evidence | `PYTHONPATH=src .venv/bin/python handoff/round5_form_h2h_2026-10-12/a_identity_checks.py` |
| `a_census.py`, `a_census_before_after.sh`, `a_census_worktree.txt` | the identity change's cost/benefit, measured with the REAL old code: the same census script run from a worktree at the parent commit and from the working tree (the output names the module each run used) | `bash handoff/round5_form_h2h_2026-10-12/a_census_before_after.sh` |
| `c_patch_gate.sh`, `c_patch_gate.txt` | C: patch size/sha256 vs the record, `--numstat` vs the patch header, which files apply cleanly and which conflict, and the per-file sha256 tip/parent/post-image with each drift traced to a named commit | `bash handoff/round5_form_h2h_2026-10-12/c_patch_gate.sh` |
| `w35_width9_rule.sh`, `w35_width9_rule_run.txt` | the width-9 comparison run, made reproducible at this tip (it needs a scratch root and links `localdata`+`Config`; see the note in the script) | `bash handoff/round5_form_h2h_2026-10-12/w35_width9_rule.sh` |
| `n3_tip_prints.sh`, `n3_tip_prints.txt` | N-3: the close-out's four tip prints (rescue flow + both stats calls with line numbers; stat field sets, 13 marker counts, five constants; both test modules; the sha256 table and attribution rows) | `bash handoff/round5_form_h2h_2026-10-12/n3_tip_prints.sh` |
| `../n1_persisted_keys.py`, `../n1_persisted_keys.txt` | N-1: every persisted `source_team_key`-derived key, its writer and reader, recomputed-vs-compared, and the measured churn | `PYTHONPATH=src .venv/bin/python handoff/n1_persisted_keys.py` |
| `../n1_legacy_leg_proof.py`, `../n1_legacy_leg_proof.txt` | N-1(c): the acca lifecycle proof across the Utd fold | `PYTHONPATH=src .venv/bin/python handoff/n1_legacy_leg_proof.py` |
| `../live-excerpt-tW4rOkzg-2026-10-12.txt`, `../s44_excerpt_repro.py`, `../s44_excerpt_repro.txt` | §4.4: the fresh render and the parser's own reproduction over it | `PYTHONPATH=src .venv/bin/python handoff/s44_excerpt_repro.py` |
| `../AGENT-INSTRUCTIONS-5-CLOSEOUT.md` | the close-out rulings as recorded, and where each is answered | — |
| `CLOSEOUT-ANSWERS.md` | the six close-out answers (N-1, N-2, N-3, §4.4, ruling 10, gate C), each with the command that reprints it — and what is still pending the push | — |

Suite: `PYTHONPATH=src .venv/bin/python -m pytest tests/ -q -p no:randomly`
→ **2897 passed in 84.14s** (2817 before this round's first tests; 2843 before
the adjudication's; this run at the tip of the amended chain).

## W1 — what the form block serves (a read-fix question, answered by reading)

* The block serves the selector `5 results / 10 results / 15 results / all
  results` with **`- 5 results` active, and exactly five dated rows per side**.
  The 10/15/all rows are **absent from the served response** (`w1_counts.txt`:
  2 selector strips, 2 active markers, 5 + 5 rows, 0 extra row groups).
* **Corrected 2026-10-12 (A-1):** the round-5 text called the block's controls
  "links to further server responses". Re-read: **every expander in that region
  is a JS control with no href** — the `5/10/15/all` view strip, `Show more
  matches` and `Show full table`. The only hrefs the block serves are
  `mutual-matches/?home=…&away=…` (`Show all`) and
  `standings/?table=…&as-ajax=1&event_context=…` (the table tabs), **both already
  on the standing never-fetch list**, so the reader keeps its 5-row read and the
  fetcher makes no new request. Quotes: `a1_served_controls.txt`.
* The H2H list the page serves runs to **20 dated meetings** (17.02.2010 →
  18.08.1993, with closing 1x2 odds) under a heading that says `Last 6`.
* Consequence, per the brief: **keep the 5-row read, add no fetch.** The
  docstring/comment claim that the controls are "client-side toggles" was
  narrowed to what was measured. Proposed operator ruling: the form block
  serves 5 rows; asking for 10/15/all means a new network request, which this
  round must not add.
* Unverified: the raw HTML bytes of that page (no sandbox route to
  betexplorer.com). The full standings table (ranks 1–20) was reported by the
  fetch read; the excerpt quotes the header and three rows, so the 20-row count
  is marked reported-not-re-counted in `w1_counts.txt`.

## W2/W3 — the feature module and its coverage

`src/edgefactory/form_intel.py` (one module, one code path, pure functions over
the committed archives): per-team last-5/last-10 windows (goals for/against,
over 2.5 / over 3.5 / BTTS rates, points per game, home/away split), pair
history both directions, `form_market_probability`, `coverage`, and the page
readers/comparators. `<5` prior matches → `insufficient_history`, never a thin
number. The leak discipline (a match's own result never enters its own
features) is proven by `test_a_rows_own_result_never_enters_its_own_features`.

**Identity.** The module reads the archive under the repository's canonical
`source_team_key` (the curated alias layer included, squad classes vetoed), not
the width-9 `norm_team` bucket — `identity.py`'s own rationale for that key is
that the width-9 one *"makes unrelated teams collide on one voter key …
Colliding keys mis-attach wrong-match evidence"*. Measured, both readings
through the same code path (`w3_identity_census.txt`):

* **Visible history.** Behind the same 814 fixture sides: **21,605 prior rows
  under the canonical key vs 26,278 under the width-9 bucket**, of which
  **5,655 rows are ones the canonical key refuses** (other clubs, other squads;
  listed verbatim in `w3_identity_census.txt`) and 982 are canonical-only.
  The width-9 bucket is not merely wider: it attaches other clubs' rows to the
  query, so a side can look covered while much of the history behind it is not
  that club's.
* **Sides with ≥5 prior matches**: 776/814 canonical vs 777/814 width-9
  (fixture records: 376/409 under both — the two readings now agree on *which*
  fixtures clear the bar, and disagree on *what history* they cleared it with).
* **The width-9 dedup key** would merge **3,891** same-date/same-score groups
  whose canonical identities differ — **4,267 rows beyond the first** — mixing a
  senior side with its own W/U20 edition (`Vitoria Guimaraes W 2-1 Braga W` vs
  `Vitoria Guimaraes 2-1 Braga`, `NWS Spirit U20 v Sutherland Sharks U20` vs
  `NWS Spirit v Sutherland Sharks`) and cross-source spellings into one stored
  row.
* **Correction, 2026-10-12.** The first version of `w3_identity_census.py`
  interleaved the two readings and queried a width-9-built index with canonical
  keys, which reported the width-9 bucket as reading *fewer* rows (11,869 /
  390 sides). The script now runs each reading as its own pass with its own key
  in force; the numbers above are the corrected ones and the script says so.
* The worked example in W4 is the same failure in the comparator, now fixed for
  the spellings the adjudication joined (see W4 below).

One fixture recorded twice under two spellings is collapsed to one row per
date-and-scoreline (`test_one_fixture_recorded_under_two_spellings_counts_once`).

**The cost of that precision**, and what the adjudication did about it (A-2/A-3,
2026-10-12). The thin sides were named with the spelling clusters behind them
(`Real Betis` ← `Betis` x39, `Flint Town Utd` ← `Flint Town United` x17,
`Scunthorpe Utd` ← `Scunthorpe` x43, `Al-Ittihad Alexandria` ← `Al Ittihad` x75,
`FC Basel 1893` ← `Basel` x38, …). The reviewer accepted additive joins and the
round shipped them:

* **One deterministic token fold**, `utd → united`, in `team_identity_words` —
  a word-level abbreviation fold, not fuzz. `team_identity_words` is the seam's
  word function (`source_team_key`); the fold is gated by a no-collapse test and
  by a corpus check that every key group holding a `Utd` spelling is one club
  (68 such groups, 0 wrong: `a_identity_checks.txt`).
* **20 pairs joined** (18 bare/abbreviated spellings plus `Betis` → `Real Betis`
  and `Basel` → `FC Basel 1893`), each with its own evidence (date + fixture +
  league) in `src/edgefactory/identity.py` and
  `Config/entity_overrides.json`. The probe prints the per-pair table over the
  raw files and classes them: **14 pairs carry mutual fixtures** (the same date
  and opponent served under both spellings — e.g. `Betis` 7, `Newcastle`/
  `Newcastle United` 11, `JEF United` 8, `Flint Town` 5) and **6 rest on the
  row case alone** (`Accrington`, `Kidderminster Ha`, `Scunthorpe Unite`,
  `Mallorca`, `Aris Thessalonik`, `Corvinul Hunedoa` — rows in the one club's
  own league and against its own opponents, which is the test `Al Ittihad`
  fails). The spellings: Accrington / Accrington St → Accrington
  Stanley, Borussia Monchen → Borussia M'gladbach, Carrarese → Carrarese
  Calcio, Charlton → Charlton Athletic, Ferroviaria → Ferroviária SP, JEF
  United / JEF United Ichih → JEF United Chiba, Kidderminster / Kidderminster
  Ha → Kidderminster Harriers, Scunthorpe Unite → Scunthorpe United, Zeljeznicar
  → Zeljeznicar Sarajevo, Mallorca → Real Mallorca, Flint Town → Flint Town Utd,
  Omonia Nicosia F → Omonia Nicosia, Aris Thessalonik → Aris Thessalonikis,
  Corvinul Hunedoa → Corvinul Hunedoara, Newcastle → Newcastle United.
* **Al Ittihad refused.** Its 75 rows span Saudi (27), Egyptian (22 + 3 league
  cup), unfiled (16), AFC Champions League (4) and friendlies (3) — not one
  club — so the pair is NOT in either table and the split is reported. The
  separately-spelled `Al-Ittihad` (34 rows, Libyan leagues) is a third club and
  is left alone too.
* **Measured effect, real old code vs working tree** (`a_census_worktree.txt`):
  archive rows behind the registry's 814 fixture sides **21,177 → 21,605**; sides
  with ≥5 priors **761 → 776** of 814; the driver's fixture-level reading
  374/409 → **376/409** with 35 → 33 `insufficient_history`. The fold's blast
  radius over the archives: 135 spellings carry `utd`, 148 seam keys change,
  83 groups merge, **0 wrong merges** listed in full.
* **The persisted key layers were deliberately left alone**: the fold reaches
  the seam, not `entities.canonical_team` or the learned-alias lookups
  (`fold_tokens=False`). Folded there, 131 of the 13,202 alias-free spellings
  would move and orphan stored keys such as `soccer|afctelfordutd|*|1x2|home`;
  the layers are verified byte-identical to the historical rule.
* **Reserve sides (A-3): distinct, never merged.** `Ludogorets III` =
  `ludogoretsiii` ≠ `Ludogorets Razgrad` = `ludogoretsrazgrad`, so the census
  never joined them (no defect); `Kongsvinger 2`/`II`, `Betis B`, `Basel II`,
  `Mallorca B`, `Charlton U21` likewise stay their own keys and never resolve to
  the senior club (pinned by tests). `coverage()` now labels every thin side
  with its squad class (`senior` / `reserve` / `women` / `u21` …) so a
  floor-deriving slice can exclude non-senior sides knowingly: of the 38 thin
  sides, 36 are senior and 2 are women's sides.

## W4 — the page's own last-5 vs the archive's last-5

`w4_page_vs_archive.txt` (worked example: the one match page read this round).
The page side is not re-parsed by hand — the served text goes to the capture's
own `parse_match_page_blocks` (10 rows, labels `Coventry`, `Newcastle Utd`).

* **Canonical identity (the shipped rule), after the A-2 joins: 8/10 page rows
  matched, 0 unmatched labels.** `Newcastle Utd` 4/5 — the same four league
  rows now match because the archive's `Newcastle` spelling joins the page's
  `Newcastle Utd` (44 rows under either spelling), with `2026-08-23` a
  `window_shift` and one archive-only row
  (`2026-09-08 Millwall 0-1 Newcastle`) `unexplained` for the league-label
  reason. Coventry 4/5 as before.
  *(Before this round's joins the same run read 4/10: `Newcastle Utd` 0/5, all
  `unmatched_identity`. That was the worked example of the gap the adjudication
  closed.)*
* **Comparison run (identity swapped to the width-9 bucket): 6/10, and the
  agreement is partly another club.** `Newcastle Utd`'s `2026-09-19` row
  "matches" `Anstey Nomads 2-1 Newcastle Town` — a different club with the same
  date and score — plus `2026-09-15 Kashima Antlers 7-1 Newcastle Jets` and
  `York City 1-3 Newcastle U23s` surface as archive-only rows. The width-9
  bucket does not resolve the alias gap; it hides it behind other clubs'
  fixtures.
* Same ten page rows, same code path, both readings in one run.

## W5 — the decision gate

`w5_signal.txt`, out-of-sample (weight fitted on the first 60% of dates,
evaluated on the last 40%), markets labelled noise below n=30:

**Which features were tested (B-5).** These are **archive-derived** features:
the committed monthly results archive (deep where the fixture is old, stale
where it is recent). The **page-block variant is untested by construction** —
the 5-rows-per-team blocks live in the match-page ledger, which is not in
production — so nothing here speaks to what the page blocks would score.

**Join coverage (B-2).** All **409/409** settled records carry the model's
stated probability: the join is `recommended_enhancement` against the day's
`picks_*.json`, 335 from the evening file and 74 from the morning file, 406
plain labels and 3 combo labels; the driver prints the counts and the reasons
for any record that fails to join (`w5_signal.txt`, first block). The **form
estimate** is available for 374/409 (the 35 remainder are the thin sides, each
named with its squad class in `w3_coverage.txt`).

| market | n | TEST n | model Brier | blend Brier | market Brier | Δ(blend−model) | base rate h(1−h) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| over_25 | 350 | 126 | 0.2562 | 0.2564 | 0.2342 | +0.0003 [−0.0260, +0.0267] | 0.2318 |
| over_15 | 33 | 12 | 0.2497 | 0.2346 | 0.2726 | −0.0151 [−0.0483, +0.0066] | 0.2222 |
| over_35 | 16 | 7 | NOISE | | | | 0.2449 |
| btts_yes | 7 | 7 | NOISE | | | | 0.2449 |

**Base-rate bar (B-3).** Each table now carries the constant-predictor Brier
`h(1−h)` on the same test slice. On over_25 the base rate is **0.2318** and
both the model (0.2562) and the market-implied price (0.2342) sit **above** it:
on this 126-row slice, neither beats predicting the base rate. That makes the
"no signal" verdict *stronger*, not weaker — and it is a calibration/join red
flag on the model itself, reported as such rather than smoothed over.

**Verdict: the blend does not beat the model out of sample → no signal; do not
wire it.** (b) vs (a) Δ +0.0003 with a CI spanning 0. The market-implied price
scores better on over_25 (−0.0220 [−0.0566, +0.0137]) — **not significantly on
this sample** (the CI spans 0) — reported, not acted on; the price remains the
only thing that sets value, no EV veto, no floors from form.

The verdict does not depend on the identity rule: with the width-9 reading
(`w5_signal_width9_rule.txt`, reproduced by `w35_width9_rule.sh`) the same test
reads over_25 blend 0.2622 vs model 0.2562 (Δ +0.0060 [−0.0202, +0.0327]) and
over_15 blend 0.2400 vs model 0.2497 (Δ −0.0097 [−0.0340, +0.0069]). The
canonical reading's blend moved from 0.2572 (before the A-2 joins) to 0.2564,
i.e. the identity work improved the form feature slightly and the verdict is
unchanged; over_15's TEST n is 12.

## W6 — what this round did not do

* **The price is still the only thing that sets value.** `form_intel` is
  imported by nothing in `src/`, `scripts/` or the pipeline — only by its own
  tests and this bundle's driver (`grep -rn form_intel src scripts tests`).
  No form/H2H number reaches `enh_pricing`, `enh_registry`, `auto_tickets`, a
  floor or the ledger.
* No EV veto, no floor derivation from form/H2H; `MIN_PRICED_N`,
  `MIN_MULTI_SOURCE_FRAC`, `BENCH_WINDOW_DAYS`, `BENCH_MIN_N` and the market
  floors are untouched.
* **No new network surface.** The module imports no HTTP client (asserted by
  `test_the_module_has_no_network_surface`), and W1 added no request: the
  10/15/all form views are absent from the served response, so a ruling is
  proposed instead of a fetch.
* **No lookahead.** A fixture dated D reads rows strictly before D;
  `test_a_rows_own_result_never_enters_its_own_features` flips a row's own
  score and shows that row's features unmoved while later fixtures move.
* **Nothing promoted.** Not wired to the board, the slip, staking or the
  ledger; the flag keeps gating everything (proof below).

## W6 proof — flag off is byte-identical, flag on is the measured delta

`w6_flag_gate_rerun.sh` → `w6_flag_gate_rerun.txt`, run at this bundle's HEAD.
The baseline is a **worktree at the stage-1 commit's parent** (`b25320b`) whose
tree the transcript prints, because the script needs `PYTHONPATH` to point at
another tree and a missing worktree would silently fall through to the editable
install — comparing the current code with itself. The script now refuses to run
without it (found 2026-10-12, after a sandbox reset deleted the earlier
worktree; the pre-reset baseline commit `d2f235b` is no longer in the object
store, so the baseline was re-established at this chain's parent — the same
file contents).

* `board.baseline.json` (pre-stage-1 code) vs `board.off.json` → **IDENTICAL**.
* `slip.today.off.txt` vs `slip.today.on.txt` → **IDENTICAL** (no committed
  board fixture is in the ledger).
* `board.off.json` vs `board.on.json` → 12 BetExplorer pairs appear (55
  changed content lines / 67 diff lines); the labelled probe board's picks
  gain `Match Over 3.5 @ 5.00 (BetMGM.us)` and `BTTS yes @ 1.57 (bet365.us)`;
  0 of the committed boards' picks change.
* The ledger written today is byte-identical to the round-2 committed ledger
  except its `captured_at` timestamp.

## C — the patch-transfer gate, re-printed at this tip

`c_patch_gate.sh` → `c_patch_gate.txt`. The reviewer's file
`handoff/betexplorer-depth.patch` is **1,908 lines / 96,156 B**, sha256
`edc6b09661f1…` — the same measured size and hash as the record; the operator's
figure (96,155 B / `e685e1a1…`) still differs by one byte, unresolved (round-2
note), and the patch is accepted on functional evidence. `git apply --numstat`
reproduces the patch header exactly: **9 files, +1,597/−46**.

Applied with `git apply -3` in a worktree at the chain's parent (`8e50de2`):

| # | file | applies | tip vs post-image |
| --- | --- | --- | --- |
| 1 | `.gitignore` | clean | identical |
| 2 | `docs/operator/BETEXPLORER-LICENSING.md` | clean | differs — `9bd32e4` (stage-1 consumption documented) |
| 3 | `scripts/capture_betexplorer.py` | clean | differs — `b25320b` (receipt census) |
| 4 | `scripts/clean_localdata.py` | clean | identical |
| 5 | `scripts/picks_today.py` | **clean** | differs — `9bd32e4` (index loaded after the rescue) |
| 6 | `src/edgefactory/sources/betexplorer_match_snapshot.py` | clean | differs — `5e0584e`, `ceb2fbb` (round-5 form-block comment, A-1 correction) |
| 7 | `src/edgefactory/sources/betexplorer_odds.py` | **CONFLICT, 3 hunks** | hand-resolved keeping both sides |
| 8 | `tests/test_betexplorer_match_detail.py` | clean (new file) | differs — `b25320b` (census test) |
| 9 | `tests/test_betexplorer_politeness.py` | clean | identical |

Every difference from the patch's own post-image is traced to a named commit;
there is no unexplained drift, so the §1 gate holds at this tip. The six
never-contended files are rows 1, 2, 3, 4, 6, 8 and the three previously
contended files are rows 5, 7, 9 — each with its sha256 at the tip, at the
parent and at the post-image in the artifact.

**Conflict-set discrepancy, reported plainly:** the adjudication's record
expects the conflict on `scripts/picks_today.py`. Measured here, and in the
round-2 post-mortem before it, `scripts/picks_today.py` applies **cleanly** and
the only conflict is `src/edgefactory/sources/betexplorer_odds.py` (3 hunks, all
"both sides added"). Nothing is repaired or renamed to make the two records
agree.

## W7 — the by-product, and its hard limit

The H2H list and the last-results blocks carry **dated closing 1x2 odds** for
past meetings of exactly the fixtures this lane trades — free extended price
history for sanity checks and CLV work, on 1x2 only. It **cannot** price an O/U
or BTTS selection, so it can never feed those floors. Nothing is built on it
this round.

## Rulings (closed by the 2026-10-12 adjudication)

1. **The form block serves 5 rows — closed.** Keep the 5-row read; no request
   for the absent 10/15/all views. The wording claiming "links to further
   server responses" was retracted: the expanders are JS controls with no href,
   and the only hrefs are on the standing never-fetch list.
2. **Alias-table additions — accepted, additive, shipped** for the evidence-backed
   pairs only (18 spellings + the `utd → united` fold); `Al Ittihad` refused with
   its by-league split reported. Nothing was hand-mapped; each pair carries its
   own date + fixture + league evidence.
3. **Second teams — ruled: keep distinct, never merge.** `Kongsvinger 2`,
   `Ludogorets III`, `Vancouver Whitecaps 2` stay their own keys; a reserve side
   never resolves to its senior club, and the coverage output labels the squad
   class so floor work can exclude them.
4. **Still open for the operator:** whether the lane's floors work should ever
   exclude non-senior sides (the round-4 floor slice) — the labelling now makes
   it possible, and nothing in this round acts on it.

## Close-out (2026-10-12): N-1, N-2, N-3, §4.4

* **N-1** — the persisted-key enumeration and churn measurement live in
  `handoff/n1_persisted_keys.txt`; the acceptance is
  `identity.migrate_folded_key` + `auto_tickets.leg_lookup_keys` (read-only
  compatibility candidate behind the primary key, recorded in `LEGACY_KEY_HITS`),
  pinned by 5 tests in `tests/test_settlement_fixture_identity.py`; the lifecycle
  proof is `handoff/n1_legacy_leg_proof.txt`. Measured churn from the fold: 14
  stored keys (all in the phase5 shadow ledger, which is not a settlement join);
  106 further stored keys differ for reasons that predate this round and are
  reported as found, not as this round's churn.
* **N-2** — the training-window constant row is in `w5_signal.txt` beside the
  test row. Nothing was tuned; the verdict stands.
* **N-3** — `n3_tip_prints.txt` holds the four prints at this tip.
* **§4.4** — `handoff/s44_excerpt_repro.txt`: the parser reproduces 20/20 H2H
  rows, 10/10 form rows and 20/20 standings rows from the render; the label/list
  and summary mismatches are stated there, and everything attribute-level stays
  unverified.

## Unverified / limits

* Raw HTML bytes of the match page are not retrievable from this sandbox (no
  route to betexplorer.com from bash); `w1_served_excerpt.txt` is the text the
  fetch tool returned, saved verbatim, and `w1_counts.txt` counts that text.
* The standings table's 20 rows and the H2H list's 20 rows are now REPRODUCED,
  not merely reported: `s44_excerpt_repro.txt` runs the parser over the fresh
  render and reads 20 H2H rows, 20 standings rows and 10 form rows. (The
  reviewer's own excerpt - which quoted 3 standings rows and 4 H2H rows - is not
  in this workspace; its sha256 is on record in the close-out record.)
* Page-vs-archive agreement is one worked fixture (Coventry vs Newcastle Utd),
  not a rate over 409: only that page was read.
* Per-file sha256 of this bundle: `SHA256SUMS.txt`.

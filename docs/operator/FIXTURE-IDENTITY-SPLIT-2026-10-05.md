# Fixture identity SPLIT — Türkiye vs Turkey (2026-10-05)

One real match printed twice in the 2026-10-05 picks report:

```text
[2WAY-UNANIMOUS>=60] Italy vs Türkiye   KO 05-10, 19:45 -> HOME avg 70% @1.42 zulubet
[2WAY-UNANIMOUS>=60] Italy vs Turkey    KO 14:45        -> HOME avg 64% @1.47
```

## 1. Root cause — confirmed in the repo (pre-fix)

```python
norm_team("Turkey")        == "turkey"
norm_team("Türkiye")       == "trkiye"     # diacritic DELETED, not transliterated
ledger_team_key("Türkiye") == "turkiye"    # transliterates, still != "turkey"
```

Two independent bugs:

1. **`norm_team` deleted diacritics.** `re.sub(r"[^a-z]", "", name.lower())`
   dropped every non-ASCII letter, so accented names produced keys that
   joined to nothing (`Beşiktaş` -> `beikta`, `Atlético` -> `atltico`) and
   disagreed with `ledger_team_key`, which folds first. Three key spaces
   for one team.
2. **No curated exonym alias.** Türkiye<->Turkey (the 2022 rename) was not
   in `Config/entity_overrides.json` -> `teams`, so even perfect
   transliteration (`turkiye`) could not join `turkey`.

Damage: duplicate scored candidates with conflicting evidence (70%/64%,
n=900/n=1810, 1.42/1.47), duplicate-collapse bypassed, archived count
inflated, the frozen ACCA carrying one arbitrary variant, two fixture
identities in the shadow ledger (the mirror image of the collision case —
invisible to the collision detector), one variant permanently unsettleable,
and worst case double stake exposure on one match.

## 2. Blast radius — EVERY consumer of the normalizers

Deploy epoch: this change takes effect on the deploy of branch
`arena/01a10c3f-edge-factory`. "Re-keyed" below means the key an accented
or exonym-aliased name produces changes at that epoch.

| # | Consumer | Key | Status |
|---|---|---|---|
| 1 | `picks_today.lookup_context` (ladder/purity team verdicts) | `canonical_team` (+ variants) | **RE-KEYED INTENTIONALLY — live gating change, see §2a** |
| 2 | `assay_purity.py` (builds the purity registry team keys) | `canonical_team` | re-keyed intentionally; new registry rows write canonical keys, old rows stay and are still read via the variant lookup |
| 3 | `picks_today` operational collapse / `_day_archive_row_key` | `ledger_team_key` | re-keyed intentionally (this is the fix); archive merge is append-only and recomputes keys on read |
| 4 | `audit_recent_picks._archive_pick_key` | `ledger_team_key` | re-keyed in lockstep with #3 (test asserts the two keys are equal) |
| 5 | `audit_recent_picks` warehouse/candidate joins | `norm_team` 9/14 + `norm_team_sql` | unaffected by persistence: both sides are normalized at read time; accented names now join instead of missing |
| 6 | `scored_candidate_shadow` candidate/fixture/occurrence ids | `ledger_team_key(24)` | re-keyed intentionally — ONE identity for the pair going forward; old split records untouched (epoch note §8) |
| 7 | `scored_candidate_shadow.settle_candidate` / `load_settled_overlay` | was `norm_team` | **dual-key protected**: canonical + transliterated + frozen legacy, exact lookups |
| 8 | `auto_tickets` settled map / `pick_result` (`_exact_result_keys`) | was `norm_team` | **dual-key protected**, tried before the pre-existing fallback |
| 9 | `auto_tickets` rolling hit-rate / bucket PnL / slice reports | grade via #8 | protected transitively by #8; grading inputs unchanged |
| 10 | `ml_fade_research.event_key` + `TeamMatcher` (research ledger, persists `event_key`) | was `ledger_team_key` | **FROZEN**: now calls `util.research_ledger_team_key` (pre-alias transliteration), byte-identical to the pre-fix key — no ledger re-keying |
| 11 | `daily.match_market_key` (kickoff-stacking ledger merge) | `ledger_team_key` | unaffected: keys are recomputed on read for BOTH archived and fresh rows in the same process; cross-spelling rows now supersede correctly instead of duplicating |
| 12 | `sync_supabase.event_source_ref` (remote `source_ref`, upsert key) | `ledger_team_key` | re-keyed at the epoch; only forward-dated picks are synced and picks are collapsed before sync, so at most a historical remote row keeps its old ref (never updated again anyway) — epoch-noted, no rewrite |
| 13 | `entities._override_lookup` / `_registry_lookup` (learned `entity_registry.json`) | `norm_team` | **dual-key protected**: legacy key added to the candidate list, so learned aliases keyed under the old normalization still resolve |
| 14 | `enh_pricing` (enhancement price index + hit keys) | `norm_team` | unaffected: index and lookup are built in the same process from the same function |
| 15 | `export_settled_results.py` (overlay writer) | `norm_team`, `norm_team_sql` | re-keyed on write going forward; readers (#7, #8) accept old and new keys |
| 16 | `warehouse.py` / `warehouse_replay.validation_gate` / `replay_harness` | `norm_team_sql`, injected `norm_team` | unaffected: live/recon maps are built from the same injected function within one run; SQL mirror updated in lockstep (`norm_team_sql` now folds; `norm_team_sql_legacy` frozen) |
| 17 | `mine_betexplorer`, `backfill_betexplorer`, `capture_betexplorer`, `sources/betexplorer_odds`, `sources/theoddsapi` | `norm_team` | unaffected: read-time joins on both sides; accented fixtures now match instead of missing |
| 18 | `audit_source_independence`, `o25_tracker`, `scored_candidate_segment_report` | `norm_team` | unaffected: read-time aggregation keys, no persisted key |
| 19 | `clv.py` | — | does not use team normalizers (joins on pick identity supplied by the caller); unaffected |
| 20 | `identity.source_team_key` (voter-row seam) | own 24-char key | extended with the curated exonym pairs; drift test added (§4) |

### 2a. 🔴 LIVE GATING CHANGE — team-verdict inheritance (intended, documented)

The ladder's team context is keyed by `canonical_team`. With the curated
alias applied, `Türkiye` keys as `turkey` instead of `turkiye`.

Measured against the live `localdata/purity_registry.json` (22,929 team
context entries): **8 of 22 curated alias groups have their learned
evidence under only SOME spellings**, and four of those carry a
restrictive verdict:

| alias group | keys | entries | verdicts |
|---|---|---|---|
| Turkey | `turkey` / `turkiye` | 0 / 8 | VETO, UNKNOWN (only under `turkiye`) |
| Czech Republic | `czechrepublic` / `czechia` | 9 / 0 | VETO, UNKNOWN |
| Côte d'Ivoire | `cotedivoire` / `ivorycoast` | 7 / 0 | VETO, UNKNOWN |
| Ulsan HD | `ulsanhd` / `ulsanhyundai` | 8 / 0 | CAUTION, UNKNOWN |
| (+ 07 Vestur, Cape Verde, Klaksvik, zvyahel) | | | UNKNOWN only |

Canonicalizing the lookup key ALONE would have orphaned that evidence —
for Türkiye it would have turned an existing **VETO into UNKNOWN**, i.e.
loosened a live gate. That is not acceptable, so the lookup is now
**variant-union and fail-closed**:

* `entities.canonical_team_variants()` returns the canonical key, the
  pre-alias key, and every curated sibling spelling's key;
* `picks_today._team_verdict()` resolves each variant through the
  unchanged per-key path (`exact -> any-league -> prefix scan`) and keeps
  the MOST SEVERE verdict (`VETO > CAUTION > ALLOW > BOOST > UNKNOWN`);
  UNKNOWN never displaces a verdict found under another spelling.

Net live effect, stated plainly: **a veto learned under one spelling now
vetoes every spelling of that team.** On the 2026-10-05 slate both
`Italy vs Türkiye` and `Italy vs Turkey` now resolve `team_a=VETO`
(verified against the live registry) — previously only the accented row
did, and the Turkey-spelled variant is the one the frozen ACCA carried.
This is a TIGHTENING and it is intended: one team, one verdict. It is a
live behavior change beyond duplicate collapse, and the earlier
"no live gate changed" claim was wrong as written.

Tests: `test_accented_spelling_inherits_canonical_team_verdict`,
`test_verdict_merge_is_fail_closed_not_fail_open`,
`test_unknown_never_displaces_an_existing_verdict`,
`test_non_aliased_team_lookup_is_unchanged`.

## 3. Normalization change

* `norm_team_legacy()` — NEW, frozen byte-for-byte copy of the old
  behaviour, for reader-side dual-key lookups only.
* `norm_team()` — now ASCII-folds (`fold_ascii`: NFKD + combining-mark
  strip + the extended Nordic table) before noise stripping:
  `Türkiye -> turkiye`, `Beşiktaş -> besiktas`, `Atlético -> atletico`.
* `norm_team_sql()` — ASCII-folds identically; `norm_team_sql_legacy()`
  keeps the frozen expression.
* `canonical_team_key()` / `ledger_team_key()` — transliteration **plus**
  the curated alias layer; `explain_team_key()` makes alias application
  visible (never silent).

**Tightening check (documented, fail-closed):** an accented name now keys
exactly like its ASCII spelling — and therefore inherits that spelling's
behaviour, including the PRE-EXISTING width-9 noise-token collision class
(`norm_team` strips `atletico`/`real`/`u21`..., so `Atletico Madrid` and
`Real Madrid` have both keyed to `madrid` since long before this change,
and `Turkey U21` has always keyed to `turkey`). No NEW collision class is
created; `test_transliteration_does_not_merge_previously_distinct_teams`
proves no merge appears beyond the curated alias pairs, measured against
the pre-fix operational key. Identity seams that must not collide use
`identity.source_team_key` (24 chars, squad tokens preserved) — the test
asserts `source_team_key("Türkiye") != source_team_key("Turkey U21")`.

## 4. Curated aliases added (explicit, reviewed, never fuzzy)

`Config/entity_overrides.json` -> `teams`:
`Türkiye`/`Turkiye`/`türkiye`/`turkiye`/`Turkey` -> `Turkey`;
`Czechia`/`Czech Republic` -> `Czech Republic`.
Mirrored as raw-name pairs in `identity.TEAM_KEY_RAW_ALIASES` (plus the
already-curated `Ivory Coast`/`Côte d'Ivoire`, `Cabo Verde`/`Cape Verde`)
so the voter-row identity seam resolves them too. No learned or fuzzy
source feeds these entries; `alias_fuzzy` remains quarantined and
non-stakeable.

## 4a. Alias-table drift guard

Curated aliases exist in two places by design — `Config/entity_overrides.json`
(entity/context layer) and `identity.TEAM_KEY_RAW_ALIASES` (voter-row
seam). `test_curated_alias_tables_do_not_drift` fails if any exonym pair
in the identity table disagrees with the override file's canonicalization,
so the two curated sources can never diverge silently.

## 5. Duplicate collapse + tripwire

* `canonical_fixture_identity(pick)` = (date, canonical home key,
  canonical away key).
* `collapse_final_operational_picks` gains a DETERMINISTIC first path:
  identical date/market/selection **and** identical canonical identity
  collapses. The 180-minute reschedule guard still applies whenever both
  rows carry an *anchored* (dated) kickoff; a bare clock (`"14:45"`,
  no date) carries no occurrence information and cannot veto the merge.
  The pre-existing fuzzy bigram path is untouched.
* The dropped twin is persisted by the shadow ledger with the existing
  `duplicate_fixture` rejection code — never two stakeable legs.
### 5a. Bare-clock merge — behavior change vs pre-fix (measured)

Replaying the OLD collapse (`git show main:scripts/picks_today.py`) against
the new one on identical inputs:

| case | pre-fix | post-fix |
|---|---|---|
| identical names, one bare clock (apparent 300-min gap) | merged=0 | **merged=1** (flagged) |
| identical names, both anchored, 300 min apart | merged=0 | merged=0 |
| Türkiye/Turkey, one bare clock | merged=0 | merged=1 (flagged) |

So the bare-clock merge IS new; it is not merely the old behavior under a
new key. The trade-off, stated explicitly: a same-day, same-competition
double-header between the SAME two teams would be falsely merged when one
row carries an unanchored clock. That fixture pattern does not occur in
football, while cross-source clock drift occurs daily, and the failure it
prevents (two stakeable legs on one match) is the one with money attached.

Mitigations, all verifiable:
* anchored kickoffs >180 min apart still REFUSE to merge
  (`test_anchored_kickoffs_more_than_180_min_apart_never_merge`, plus the
  pre-existing `test_kickoffs_outside_180_min_do_not_cluster`);
* every merge that could not consult the guard is stamped
  `ctx.duplicate_kickoff_unanchored = "true"` on the surviving row, so the
  audit can list exactly which collapses relied on it
  (`test_unanchored_merge_is_flagged_for_audit`).

Reconciliation with the shadow ledger's fail-closed occurrence policy:
the ledger fails CLOSED on an AMBIGUOUS legacy fixture_id because there it
cannot tell two real occurrences apart and money may already be attached
to the wrong one. Here the direction of risk is inverted — refusing to
merge produces two stakeable legs on one match — so the operational
collapse fails toward ONE stake and records the uncertainty as a flag
instead of silently keeping both.

* `near_duplicate_fixture_warnings()` / `print_near_duplicate_fixture_tripwire()`:
  after collapse, any same-date, same-canonical-league pair where ONE team
  key matches and the other does not prints a loud warning block naming
  both rows, their keys and their sources. It never merges anything — the
  merge only ever happens through transliteration + curated alias.

## 6. Shadow / settlement coherence

`fixture_id`, `candidate_id` and `fixture_occurrence_id` are identical for
both spellings going forward (test + smoke). Old split records stay on
disk as written; no history is rewritten. Settlement resolves across
spellings: a result recorded as "Turkey" grades a pick captured as
"Türkiye", and results persisted under the old diacritic-deleting key
still settle through the legacy reader key.

## 7. Secondary findings (reported, not silently changed)

1. **Bare `KO 14:45`.** Provenance: the raw feed text is deliberately never
   rewritten (`attach_kickoff_display` docstring — rewriting could move a
   kickoff LATER, the one direction the lead guard must never be nudged).
   A source that emits a bare local clock with no date and no offset
   yields `zoned_kickoff_to_utc -> None`; with no sibling or odds-row
   witness, `kickoff_source = unresolved`, `kickoff_sast = None`, and the
   report falls back to printing the raw bare clock. This is the
   incident-#6 naive-foreign-clock family. **No kickoff guard was
   weakened**; the only use made of it here is the narrow statement that a
   bare clock cannot prove two identical fixtures are different events.
2. **`Moss vs Kongsvinger` CERTIFIED_CLEAN with `league=no2:UNKNOWN`.**
   Under current policy in `bucket_pick`, an UNKNOWN league verdict is a
   hard blocker only for the short-odds-sniper class (`1x2` home below
   `SHORT_ODDS_SNIPER_MAX`, with a narrow ultra-short soft exception).
   Outside that class, UNKNOWN (as opposed to VETO or CAUTION) does not
   block certification when the odds band is known and decay is HEALTHY.
   So the printed row **is policy-conformant as written** — not a gating
   bug. Whether UNKNOWN should ever earn the CERTIFIED_CLEAN *label* is a
   policy question for the operator; no gate was changed here.

## 8. Identity epoch split (audit-only distortion)

Accented / exonym-aliased teams carry **different fixture, candidate and
occurrence ids before and after the deploy** of this branch. No history is
rewritten — that is the deliberate choice — so:

* rolling 7/14/30-day reports whose window SPANS the deploy date will see
  one real team as two fixture identities (e.g. `turkiye` rows before,
  `turkey` rows after). Read a window-spanning identity split as an
  artefact of this change, **not** as signal.
* settlement is NOT affected: the readers accept canonical, transliterated
  and frozen-legacy keys (§2 rows 7–8).
* the ml-fade research ledger is NOT affected: its identity is frozen
  (§2 row 10).
* the purity registry is NOT orphaned: the variant-union lookup reads both
  spellings (§2a).

Review this note again once every rolling window in use begins after the
deploy date; it can be retired then.

### 8a. Degenerate `deg<hash>` keys and the epoch

Short/punctuation-only names (`CP`, `II`, `W`) used to normalize to the
**empty string**, so every one of them collided on a single identity.
They now key to `deg<hash>` (`is_degenerate_team_key`). That key is NOT
cosmetic: it reaches persisted row identities through
`canonical_team_key` → `ledger_team_key` → `_day_archive_row_key`.

* Hash input is case- and whitespace-normalized (`fold_ascii` lowercases
  and collapses runs of whitespace), so `"Athletic  Club"`,
  `"athletic club"` and `" ATHLETIC CLUB "` produce one key.
* **Settlement** was already safe: its readers try `norm_team_legacy`,
  which still yields the pre-fix `''`, so frozen rows keep grading.
* **Archive merge** was not. `_day_archive_row_key_legacy()` rebuilds the
  pre-fix tuple from the frozen `research_ledger_team_key`, and
  `merge_day_archive_rows` now skips a fresh row whose legacy key is
  already present in the frozen file, registering both keys. Without it a
  pre-fix degenerate row and its post-fix twin would have been written as
  two rows for one match — the original incident, one epoch later.
* Nothing is rewritten in place. This is a reader-side legacy path only.

## 9. Tests

New: `tests/test_team_identity_transliteration.py` (27 tests) — accented
corpus transliteration; `norm_team`/`ledger_team_key` agreement; frozen
legacy key; one canonical key for Türkiye/Turkey (+ other exonyms); alias
explicit and visible; no false merges; end-to-end dedupe (one survivor,
one collapsed twin, `duplicate_alias_collapse` metadata); tripwire silent
when the alias resolves and loud when it cannot, merging nothing; distinct
fixtures not collapsed; settlement across spellings and from legacy keys;
one shadow identity for the pair; archive merge not inflated and engine
key == audit key.

Smoke: `python tools/smoke_fixture_identity_dedupe.py` -> `SMOKE: PASS`.

Explicit parity run:
`tests/test_scored_candidate_shadow_tickets.py::test_identical_ticket_output_with_shadow_on_off_and_crashing`
-> **PASSED** (ticket stdout byte-identical with the audit ledger on, off,
and crashing).

Validation: `python -m pytest tests/ -q` -> **1300 passed**;
`python -m compileall scripts src tests` clean; `git diff --check` clean;
no `.github/workflows/*` or `localdata/*` changes.

Unchanged: kickoff guards (the pre-match guard and the 180-minute
anchored reschedule guard), `_fixture_orientation_agrees`,
`_row_matches_selection`, odds floors, veto BANDS and thresholds, ladder
structure, staking, freeze/write-once, ticket output parity.

Live behaviour changes, complete list (all intended, all tested):
1. duplicate collapse now catches cross-spelling twins (the fix);
2. team verdicts are now shared across spellings of one team, fail-closed
   — a veto learned under any spelling vetoes all of them (§2a);
3. two rows with one canonical identity merge when a bare clock makes the
   180-minute guard unusable, stamped `duplicate_kickoff_unanchored` (§5a).

## 10. Identity sweep — the bug CLASS (2026-10-05, second pass)

Türkiye/Turkey was one instance of "same real entity, several keys".
A sweep of the pre-fix keyers found five defect classes. Each is now closed by a
deterministic rule (never fuzz) and covered by
`tests/test_identity_identity defect_sweep.py`.

| # | Species | Example (reproduced) | Closed by |
|---|---|---|---|
| R1 | exonym/rename SPLIT | Côte d'Ivoire/Ivory Coast, FC København/Copenhagen, Bayern München/Munich, 1.FC Köln/Cologne, Internazionale/Inter, Man Utd/Manchester United, PSG/Paris SG, FCSB/Steaua, Başakşehir, Wolves, Napoli, Göteborg, Legia, Dinamo București, Sporting | **S1**: 17 curated groups (174 spellings) in `Config/entity_overrides.json`; one canonical key per group, each with a nearest-distinct-neighbour guard test (Inter≠AC Milan, Sporting CP≠Sporting Gijón, Austria Wien≠Austria Lustenau, …) |
| R2 | false MERGE in the final collapse | Turkey/Turkey U21 (sim 0.62), Girona/Girona B (0.83), Barcelona/Barcelona SC (0.80), Man City/Man United (0.59), Olympiakos/Olympiakos Nicosia, River Plate/River Plate Asunción, Arsenal/Arsenal Sarandí — all above the 0.40 bigram threshold | **S2** squad-marker hard veto + **S3** canonical-disagreement veto + league-conflict veto |
| R3 | width-9 frozen-ledger collision | `mancheste` (City/United), `barcelona`, `nottingha`, `universid` | **S5** report-only tripwire: colliding rows are kept apart, stamped `ctx.ledger_key_collision`, and ambiguous result keys are dropped so those legs stay pending. The ledger is NOT rekeyed (history stays byte-identical) |
| R4 | degenerate/empty keys | `Athletic Club`, `Sporting Club`, Cyrillic/Greek names → `""` | **S4**: unique non-empty `deg<hash>` keys, `is_degenerate_team_key`, merge refused unless raw strings match, `ctx.identity_degenerate` stamped and counted |
| R5 | stopword amputation | `Sporting CP`→`cp`, `Atlético Madrid`→`madrid` | **S4/S3**: degenerate guard + canonical/league vetoes; curated canonical names chosen to avoid degenerate keys (Sporting canonicalizes to "Sporting Lisbon", not "CP") |

### What merges and what does not (measured, same anchored kickoff)

| pair | result |
|---|---|
| Türkiye / Turkey | MERGE (curated alias) |
| Aldershot / Aldershot Town, Hannover / Hannover 96, Ebbsfleet / Ebbsfleet United | MERGE (`_token_prefix_link`: structural containment, not similarity) |
| IFK Mariehamn / Mariehamn | MERGE (curated odds-alias link) |
| Turkey / Turkey U21, Brazil / Brazil U20, Girona / Girona B, Arsenal / Arsenal W | REFUSE — `squad_marker_conflict` |
| Man City / Man United, Launceston City / Launceston United | REFUSE — `canonical_team_disagreement` |
| Barcelona / Barcelona SC, Olympiakos / Olympiakos Nicosia, Arsenal / Arsenal Sarandí | REFUSE — `league_disagreement` |
| Athletic Club / Sporting Club | REFUSE — `degenerate_identity` |

**Tightening-only proof.** Every similar name pair in the archives (395
pairs over 110 days, bigram ≥ 0.40) replayed through the old and new
collapse with equal anchored kickoffs: **unchanged 133, newly REFUSED
262, newly ALLOWED 0.**

### Two defects this pass found in the FIRST pass's own work

1. **League veto was too strict.** Keyed on canonical-league inequality,
   it blocked the very merge this branch exists for: the twins' feeds
   spell the competition differently ("World UEFA Nations League" vs
   "International,Uefa Nations League A Grp. 1"). Replaced with
   `_leagues_conflict`, which fires only on fully DISJOINT distinctive
   tokens. Caught by running the real 2026-10-05 slate, not by unit tests.
2. **The collapse compared untrusted clock text.** Both twins already
   carried the SAME resolved `kickoff_utc` (`2026-10-05T18:45:00+00:00`);
   the collapse was comparing the raw renders ("05-10, 19:45" vs "14:45",
   300 min apart) and refusing. `_kickoff_instants_agree` now decides on
   `kickoff_utc` whenever both rows have it — strictly more accurate than
   the naive text, and it shrinks the §5a unanchored-merge path to rows
   whose kickoff the pipeline genuinely could not resolve.

### Alias single-sourcing (supersedes §4a)

`identity.TEAM_KEY_RAW_ALIASES` now DERIVES the curated override pairs
from `Config/entity_overrides.json` at import, so the two tables cannot
drift. The sweep had already found four that had: Ulsan Hyundai, KPV-j,
Zvyagel and Maxline were canonicalized for contexts but still split at
the voter-row seam. `entities._override_lookup` also routes team lookups
through the same indexed table (it previously missed folded spellings
such as "07 vestur"). Guarded by
`test_every_curated_alias_group_agrees_in_every_keyer`.

### Daily tripwire + historical audit

* `print_identity_sweep()` runs after collapse every build (report-only):
  `identity_degenerate`, `ledger_key_collision`, `cross_keyer_merged`,
  `cross_keyer_split`. On the real 2026-10-05 slate: collapse 6 -> 5 rows
  (the twin carries `duplicate_fixture`), all four counters **0**.
* `tools/audit_identity_collisions.py` (read-only, mutates nothing) swept
  110 days of archives: **6,744 same-day key collisions (2,167 SUSPECT**,
  e.g. `Lokomotiv Plovdi`/`Lokomotíva Zvolen`, `Universitario de Vinto`/
  `Universitatea Craiova`, `Launceston City`/`Launceston United`**)**,
  5,190 split candidates, 54 degenerate-key names. Report:
  `docs/operator/IDENTITY-COLLISION-AUDIT-2026-10-05.md`. These are
  historical facts about frozen data — nothing was rewritten.

### Known residual (documented, not fixed)

Two different clubs whose names differ only by a generic token AND whose
competitions are unknown or share a distinctive token can still merge
(e.g. Barcelona / Barcelona SC with both leagues blank). The league veto
closes the realistic cases; the ledger-collision tripwire and the daily
sweep make the rest visible. Fixing it properly needs a country/
competition field on every candidate, which the feeds do not reliably
supply today.

## 11. Closing round — merge gate evidence

### 11a. Every newly-refused merge, classified (item 1)

Tightening-only was re-proven by replaying **395 real archived pairs**
through the pre-fix and post-fix collapse. "Newly allowed = 0" is
necessary but not sufficient: a wrongly REFUSED merge recreates the
original incident (two stakeable legs for one match). So every refusal
was classified and ground-truthed.

| veto reason | pre-fix refusals | after the fixes below |
|---|---|---|
| `squad_marker_conflict` | 120 | 120 |
| `canonical_team_disagreement` | 142 | 136 |
| **total newly REFUSED** | **262** | **256** |
| **newly ALLOWED** | **0** | **0** |
| unchanged | 133 | 139 |

**Data-driven same-fixture test** (does the pair ever share an opponent
on a common archive day?) over all 262: `same-fixture 0`,
`distinct-evidence 19`, `no co-occurrence 243`. Two of the 19 were in
fact one club and were linked deterministically — no fuzzy matching:

| pair | mechanism |
|---|---|
| `Borussia M'gladbach` / `Borussia Mönchengladbach` | `source_team_key` equality in the veto's link test |
| `Drogheda United` / `Drogheda Utd` | `TEAM_TOKEN_EXPANSIONS` (`utd`→`united`) inside `_name_tokens` |

**Stratified manual sample**, seed 7, 31 pairs (15 marker / 16
canonical): Bayer Leverkusen vs (w), Motherwell vs Youth,
`Independiente Res.` vs `Independiente del Valle`, Spain vs Spain U21,
Rapid Vienna vs Rapid Wien II, Hapoel Acre vs Hapoel Tel Aviv, Molde vs
Moldova, Barrow vs Barry Town, Lille vs Lillestrøm, Catania vs
Catanzaro, Port Vale vs Portugal, … — **all genuinely distinct, 0
same-fixture refusals.**

Deliberately left refused, no evidence either way: `Al Ahli` /
`Al Ahly` (different clubs in most feeds). The collision tripwire makes
any future conflict visible rather than guessing now.

Guard rails held: `Launceston City`/`Launceston United`,
`Manchester City`/`Manchester United`, `Al Nasar`/`Al Nassr` still veto.

### 11b. Frozen real-slate regression (item 4)

`tests/fixtures/slate_2026-10-05_identity_split.json` is a sanitized
freeze of the 6-row inflated slate (no URLs, no credentials, no provider
payloads; test data under `tests/`, never `localdata`).
`tests/test_identity_collision_sweep.py` replays the whole collapse path
against it: 6 → 5 rows, the twin merges on `kickoff_utc` despite
disagreeing raw clock text, the league-spelling divergence does not veto,
the archive merge yields one Italy row, and all four sweep counters are
zero. Both defects caught in the second pass were invisible to synthetic
unit tests and visible here.

### 11c. `settlement_ambiguous_pending` (item 5)

`_drop_ambiguous_result_keys` fails closed on a result key covering two
real fixtures, which leaves those legs pending **forever**. It now
returns the colliding fixtures as well as the count, and settlement
prints `settlement_ambiguous_pending=N` plus one
`!! AMBIGUOUS SETTLEMENT KEY <day>: <fixtures>` line each, so an operator
resolves them (manual verified result, or a curated alias) instead of
watching them accumulate silently.

### 11d. Terminology (item 2)

The informal metaphor from the incident channel is gone from every
filename, identifier, counter, doc heading and report string. The terms
of art are **identity collision** (two teams, one key) and **identity
split** (one team, two keys). `test_identity_roach_sweep.py` was renamed
to `tests/test_identity_collision_sweep.py` with `git mv`, preserving
history.

## 12. Red-team pass — adversarial findings (2026-10-05)

Adversarial posture: the attacks below were designed to BREAK the fix and
were **run and recorded before any repair**. Tests:
`tests/test_identity_adversarial.py` (22).

| # | Attack | Result on the branch BEFORE repair | Disposition |
|---|---|---|---|
| 1a | NFC vs NFD spellings (`Türkiye`, `Beşiktaş`, every curated spelling) | **PASS** — all 174 curated spellings + probes key identically in all keyers (NFKD runs inside `fold_ascii`) | locked by test |
| 1b | Homoglyph `Sp‑а‑rt‑а‑k` (Cyrillic а) | **FAIL (confirmed)** — `spartak` vs `sprtk` in all three keyers, nothing flagged it | not repairable without a transliteration dependency → `script_anomaly()` + sweep counter `mixed_script_name=N` + `!! MIXED SCRIPT TEAM NAME` line; never auto-merged |
| 1c | ZWSP / NBSP / soft hyphen / RLM / LRM / BOM, inside and around a name | **PASS** — identical keys | locked by test |
| 1d | Turkish dotted `İ` (`İstanbul Başakşehir`, `DİYARBAKIR`) | **PASS** | locked by test |
| 2 | `W Connection`, `B 1903`, `B36 Tórshavn`, `II Keila`, `Degerfors IF` vs `Degerfors` | **FAIL (confirmed)** — `W Connection` carried marker `w`; `B 1903` keyed to a sentinel; `Degerfors IF`/`Degerfors` was refused `degenerate_identity:home` | curated `MARKER_EXEMPT_NAMES`; numeric names fall back to the alphanumeric compact key (`B 1903` → `b1903`); all four same-club pairs now merge; `Keila II` keeps its genuine marker |
| 3 | Sentinel integrity (`Degerfors`, `Degenhardt FC`, `deg12345678`) | **FAIL (confirmed)** — the sentinel was a plain `deg` **string prefix**, so real clubs starting "deg" were classified degenerate (this *caused* finding 2's Degerfors case) | sentinel moved out of the key alphabet: `deg~<hash>`; keys only ever contain `[a-z0-9_]`, so collision is impossible by construction; the old `deg[0-9a-f]{8}` form is recognised read-side only |
| 4 | Two distinct clubs, identical `kickoff_utc`, both leagues blank (`Barcelona` vs `Barcelona SC`) | **FAIL (confirmed)** — merged (keys are equal after `sc` stripping, so no veto could fire) | curated `DISTINCT_TEAM_PAIRS` ("two clubs, one key" — the mirror of the alias table), checked FIRST in `_merge_veto_reason`; kickoff agreement is now explicitly necessary-never-sufficient |
| 5 | Epoch shadowing: `Turkey U21` legacy key `turkey` == `Turkey` canonical key | **FAIL (confirmed)** — `norm_team`/`norm_team_legacy` strip `u21`, and the existing similarity fallback scores `turkeyu21`/`turkey` at exactly 0.80 (the acceptance bar) | `_marker_boundary_blocks()`: the chain stops at a distinct-entity marker. Real names behind each loaded key are registered (`SETTLED_KEY_NAMES`) so marker sets are compared exactly; where names are unknown only an explicit suffix conflict blocks, keeping legacy marker-blind rows settleable. Guarded legs print `settlement_marker_guarded=N` |
| 6a | Survivorship bias — replay historical CORRECT merges | **PASS** — 518 archived rows carry collapse metadata; 10 record ≥2 distinct member spellings; all 10 clusters still collapse to one row, identical to pre-fix code | replayed in-suite |
| 6b | Alias config deleted / malformed JSON | **FAIL (confirmed, silent)** — degraded to zero aliases with no signal, so every exonym fixture would split again unnoticed | all-or-nothing degradation kept (never half-applied) and now announced: `!! TEAM ALIAS CONFIG UNAVAILABLE …` on stderr + `ALIAS_CONFIG_WARNINGS` |
| 6c | Idempotence — collapse the frozen slate twice | **PASS** — 6→5 then 5→5, byte-identical | locked by test |

### 12a. Methodology correction to the round-2 proof

Replaying the archives through the whole pipeline (old `main` vs this
branch) on same-day candidate pairs above the old 0.40 merge threshold:
**80 candidate pairs, 4 newly refused (`league_disagreement`, from round
2), 7 newly ALLOWED.** All 7 are the curated exonym merges the fix
exists to make — `Türkiye`/`Turkey` ×5 and `Czech Republic`/`Czechia` ×2,
i.e. the incident itself. Round 2's "newly allowed = 0" was measured at
the **veto-predicate** level, which cannot see merges enabled by
alias-driven key *equality*; the pipeline-level number is the honest one
and it is 7 intended merges, not 0.

Against the branch head immediately before this red-team pass, the
repairs above produce **0 newly refused and 0 newly allowed** on the same
80 pairs: the Degerfors/B 1903/W Connection/Barcelona-SC cases do not
occur in the archives, which is exactly why only adversarial inputs
exposed them.

### 12b. Residual, accepted

* Homoglyph names cannot be transliterated deterministically here; they
  are flagged, not merged (1b).
* `Al Ahli`/`Al Ahly` remain refused (and are now on the curated
  distinct-clubs list) — different clubs in most feeds.
* Non-Latin-only names (wholly Cyrillic/Greek) still key to a `deg~`
  sentinel: fail-closed, visible via `identity_degenerate`.

## 13. Youth/reserve squad-identity hardening handoff verification (2026-10-05)

This section records only evidence generated in this session on branch
`arena/01a10d17-edge-factory`. The three short commit IDs named in the
handoff were not present in this checkout, so the work below was rebuilt
and measured on this branch rather than cherry-picked.

| Check | Command run | Actual result | Disposition |
|---|---|---|---|
| Handoff commits available locally? | `pwd && git status --short --branch && git log --oneline --decorate --max-count=12`<br>`git branch -a --contains 01032fc || true; git branch -a --contains d5e6797 || true; git branch -a --contains 90cfc1d || true; git cat-file -t 01032fc 2>/dev/null || true; git cat-file -t d5e6797 2>/dev/null || true; git cat-file -t 90cfc1d 2>/dev/null || true`<br>`git fetch --all --prune --tags && git show-ref --heads --tags`<br>`git fsck --no-reflogs --unreachable --lost-found 2>/dev/null; git reflog --date=iso` | `## arena/01a10d17-edge-factory` at `5927fab ... Fix duplicate-fixture identity split + identity collision hardening (#37)`.<br>`git branch --contains` reported `error: malformed object name 01032fc`, `d5e6797`, `90cfc1d`; `git cat-file` returned no object type.<br>`git show-ref` listed only `refs/heads/arena/01a10d17-edge-factory` and `refs/heads/main`, both at `5927fab...`.<br>Reflog showed clone/checkout only; no unreachable commits were printed. | Could not cherry-pick/rebase the named commits in this environment. Rebuilt the squad-identity hardening directly and covered it with tests below. |
| Baseline local-archive measurement before this session's fix | `tmp=$(mktemp -d); ... git show HEAD:src/edgefactory/util.py > $tmp/src/edgefactory/util.py; git show HEAD:src/edgefactory/scored_candidate_shadow.py > $tmp/src/edgefactory/scored_candidate_shadow.py; git show HEAD:scripts/auto_tickets.py > $tmp/scripts/auto_tickets.py; git show HEAD:Config/entity_overrides.json > $tmp/Config/entity_overrides.json; ln -s /home/user/Edge-Factory/localdata $tmp/localdata; PYTHONPATH=$tmp/src .venv/bin/python - <<'PY' ... load_archived_picks(); _collect_settled_facts(); pick_result(...) ... PY` | `old_archived_picks 1729`<br>`old_graded 1590`<br>`old_squad_legs_total 113`<br>`old_squad_legs_graded 102`<br>`old_ambiguous_keys 27`<br>`old_marker_guarded_legs 8` | The prompt's quoted `1611`, `1489`, `86/94`, `26` figures were not reproduced in this checkout. Local baseline here is the output shown. |
| Post-fix local-archive measurement | `PYTHONPATH=src .venv/bin/python - <<'PY' ... load_archived_picks(); _collect_settled_facts(); pick_result(...) ... PY` | `archived_picks 1729`<br>`graded 1593`<br>`squad_legs_total 113`<br>`squad_legs_graded 105`<br>`ambiguous_keys 0`<br>`marker_guarded_legs 5`<br>stderr included `settlement_ambiguous_pending=0`. | Improved local grading by 3 legs, improved squad-leg grading by 3 legs, and reduced local ambiguous settlement keys from 27 to 0. |
| Status-change audit old vs new | `tmp=$(mktemp -d); ... old auto_tickets snapshot ... > /tmp/old_status.json; PYTHONPATH=src .venv/bin/python ... > /tmp/new_status.json; .venv/bin/python - <<'PY' ... compare results ... PY` | `status_changes 4`<br>`newly_graded 3`<br>`newly_ungraded 0`<br>Changed rows printed:<br>`Pafos vs Dinamo Tirana`: `old loss`, `new win`.<br>`Korona II Kielce vs Radomiak Radom`: `old None`, `new win`.<br>`Vukovar '91 vs Dinamo Zagreb B`: `old None`, `new loss`.<br>`Górnik Zabrze II vs Olimpia Grudziadz`: `old None`, `new win`. | No leg became newly ungraded. The Pafos change is an operator-verified correction already covered by existing verified-result tests. The three newly graded legs are exact/level-tolerant second-team joins with same-day archive result evidence; covered by `tests/test_squad_identity.py`. |
| Senior leg must not grade from youth result, and youth leg must not grade from senior result | `PYTHONPATH=src .venv/bin/python -m pytest tests/test_squad_identity.py -q` | `10 passed in 0.06s` | Covered by `test_auto_ticket_senior_result_never_grades_youth_leg_and_vice_versa`, `test_shadow_settlement_senior_result_never_grades_youth_candidate`, and `test_level_tolerant_lookup_never_synthesizes_senior_boundary_key`. |
| Legacy-blind keys cannot be written back for squad rows | `PYTHONPATH=src .venv/bin/python -m pytest tests/test_squad_identity.py::test_legacy_blind_lookup_keys_are_tagged_and_not_written_for_squad_rows -q` | `1 passed` | `_exact_result_lookup_specs("Turkey U21", "Spain U21")` still exposes `("turkey", "spain", True)` as a tagged compatibility key, but `_result_write_keys` / `_exact_result_keys` return only `("turkey_u21", "spain_u21")`. |
| `_level_tolerant_lookup` fails closed when sibling second teams disagree | `PYTHONPATH=src .venv/bin/python -m pytest tests/test_squad_identity.py::test_level_tolerant_lookup_fails_closed_on_disagreeing_second_teams -q` | `1 passed` | The second-team family lookup returns `None` when U20 and U23 sibling keys on the same date produce different outcomes. |
| Senior-key parity for real senior names | `PYTHONPATH=src .venv/bin/python - <<'PY' ... materialize old util/config from git show HEAD; sample 5000 senior-only archive fixtures; compare old.canonical_team_key and old exact keys to new canonical_team_key and _exact_result_keys ... PY` | `senior_fixture_sample 5000`<br>`canonical_team_key_diffs 0`<br>`exact_result_keys_diffs 0` | Senior keys in the 5,000-fixture senior-only sample were byte-identical for `canonical_team_key` and `_exact_result_keys`. |
| Unicode and marker-veto adversarial classes still pass | `PYTHONPATH=src .venv/bin/python -m pytest tests/test_squad_identity.py tests/test_identity_collision_sweep.py tests/test_identity_adversarial.py tests/test_team_identity_transliteration.py -q` | `94 passed in 0.34s` | No regression in the existing Unicode, marker-veto, exonym, sentinel, and collision-sweep adversarial tests; new squad tests are included in the same run. |
| Residual local ambiguous-key investigation | `PYTHONPATH=src .venv/bin/python - <<'PY' ... at._collect_settled_facts(); print(len(at.AMBIGUOUS_SETTLEMENT_KEYS)); ... PY` after marker-stem fix but before curated residual aliases | `ambiguous 10` with residual rows including `Charleston Battery vs Charlotte Independence` / `Charleston vs Charlotte Independ.`, `Neftci Baku W` / `Neftçi Bakı W`, `A.D. Isidro Meta` / `AD Isidro Metapan`, `Al Arabi Kuwait` / `Al-Arabi Club(KU`, `Ellas Syros` / `Ellas Syrou`, and `Egnatia Rrogozhine` / `Egnatia Rrogozhi`. | Added curated explicit aliases only for measured archive spelling/truncation pairs in `Config/entity_overrides.json`; no fuzzy matching. |
| Residual ambiguous keys after curated aliases | `PYTHONPATH=src .venv/bin/python - <<'PY' ... at._collect_settled_facts(); print('ambiguous', len(at.AMBIGUOUS_SETTLEMENT_KEYS)) ... PY` | `ambiguous 0` | Local residual ambiguous settlement keys resolved to zero. Covered by `test_curated_archive_truncation_aliases_are_explicit_and_marker_safe`. |
| Is `SECOND_TEAM_MARKERS` too broad for U20/U23? | `PYTHONPATH=src .venv/bin/python - <<'PY' ... scan localdata settled+picks for same day / same club stem / same opponent with both u20 and u23 ... PY` | `u20_and_u23_same_club_same_day_same_opponent 0` | No local evidence of U20 and U23 sides of one club meeting the same opponent on the same date. Kept the family lookup uniqueness-guarded anyway; disagreement returns `None`. |
| Broader second-team level-split evidence | `PYTHONPATH=src .venv/bin/python - <<'PY' ... scan localdata settled+picks for second-team same-day same-opponent level splits ... PY` | `second_team_same_day_same_opponent_level_splits 158`.<br>Samples printed included `Brisbane Roar FC Youth` / `Brisbane Roar U21`, `Koln (Youth)` / `Koln II`, `Atl. San Luis U2` / `Atl. San Luis U21`, `Novorizontino U2` / `Novorizontino U20`, and `Brisbane Roar II` / `Brisbane Roar U23`. | Confirms feeds use several labels for the same second-team level family. The implementation tries the family only when a second-team marker is already present and never synthesizes the empty senior marker. |
| u1x / academy evidence | Same scan command as above, printing `u17_u18_u19_name_occurrences` and `academy_name_occurrences`. | `u17_u18_u19_name_occurrences 2047 unique_names 513` with sample `Athletico-PR U17`, `Germany U19 W`, etc.<br>`academy_name_occurrences 105 unique_names 23` with sample `Puskas Academy`, `Wick Academy`, `Academy Pandev`, `Inter Academy U20`, `BFF Academy U19`, `Tottenham Hotspur Academy`. | Did not add a `u1x` tolerant family: exact U17/U18/U19 markers already remain distinct. Did not broaden academy treatment: archive evidence mixes senior club names containing Academy with youth-team academy names. |
| Report-before-fix failure captured | Initial full-suite command before adjusting the synthetic placeholder test: `PYTHONPATH=src .venv/bin/python -m pytest tests/ -q` | Failed once: `tests/test_auto_tickets_rolling.py::test_settle_losing_day_moves_bank_no_notification` with `assert 120.0 == 50.0`; stderr showed `settlement_marker_guarded=1 :: 2026-08-20 Team b vs Other b ...`. | Recorded before fixing. The test used synthetic `Team b`, which is now intentionally parsed as a reserve marker; the test fixture now uses non-marker placeholders. Production code was not loosened. |
| Full suite | `PYTHONPATH=src .venv/bin/python -m pytest tests/ -q` | `1370 passed in 29.41s` | Green after adding tests and adjusting the synthetic placeholder. |
| Parity test | `PYTHONPATH=src .venv/bin/python -m pytest tests/test_scored_candidate_shadow_tickets.py::test_identical_ticket_output_with_shadow_on_off_and_crashing -q` | `1 passed in 0.08s` | Ticket stdout parity remains green. |
| Smoke | `PYTHONPATH=src .venv/bin/python tools/smoke_fixture_identity_dedupe.py` | Ended with `SMOKE: PASS (3/3 cases)`. | Smoke green. |
| CI backlog/log access | `gh run list --limit 5 --json databaseId,workflowName,status,conclusion,headBranch,headSha,createdAt,url`<br>`gh run view 37343204736 --log | wc -c`<br>`gh run view 37343204736 --json jobs,conclusion,status,headSha,headBranch,workflowName,createdAt` | Run list returned recent successful runs, including `37343204736` on branch `arena/01a10c3f-edge-factory`.<br>`gh run view 37343204736 --log | wc -c` printed `0`; stderr ended in `EOF` while fetching logs. The signed log URL emitted by `gh` is not recorded here.<br>JSON job view showed both jobs completed with `conclusion: success`. | Production backlog collision classes beyond localdata: not verified. Logs were not retrievable via `gh run view --log` in this environment. |
| Paths touched | `git diff --name-only && git status --short` | At the time of the check before this doc append: `Config/entity_overrides.json`, `scripts/auto_tickets.py`, `src/edgefactory/scored_candidate_shadow.py`, `src/edgefactory/util.py`, `tests/test_auto_tickets_rolling.py`; untracked `tests/test_squad_identity.py`. | No `.github/workflows/*` or `localdata/*` paths touched. This doc section was appended afterwards. |

Implementation notes for this section:

* `canonical_team_key` now builds operational keys from club stem plus squad suffix for explicit markers including `U-21`, `Under 21`, `Sub 20`, `Jong`, `Frauen`, `Amateure`, `Primavera` when it follows a club stem, trailing `2`, and truncated `U2` as `u2x`.
* `_exact_result_keys` is write-safe: marker-aware canonical / transliterated / frozen-legacy keys are written; old marker-blind keys are exposed only through tagged lookup specs and are skipped for marked legs.
* `SECOND_TEAM_MARKERS = {b, res, youth, u20, u21, u22, u23, u2x}` is tried as a family only when a second-team marker is already present. The empty senior marker is never synthesized, and disagreeing sibling outcomes fail closed.
* No fuzzy matching was added. The residual zero-ambiguity improvement uses only explicit aliases added to `Config/entity_overrides.json` plus deterministic club-stem comparison after equal marker sets.

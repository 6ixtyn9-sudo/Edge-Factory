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

## 2. Blast radius — every consumer of the normalizers

| Consumer | Key used | Effect of the fix | Protection |
|---|---|---|---|
| `scripts/picks_today.py` operational collapse / archive key | `ledger_team_key` | accented names now key as their ASCII spelling; curated aliases canonicalize | new deterministic collapse path + tripwire; archive merge is append-only, old rows kept |
| `scripts/audit_recent_picks.py` `_archive_pick_key` | `ledger_team_key` | same change, stays in lockstep with the engine key (test asserts equality) | mirrored by test |
| `scripts/audit_recent_picks.py` warehouse/candidate keys | `norm_team` (9/14) | accented names now join the odds/results warehouse instead of missing | its own alias-candidate scan unchanged |
| `src/edgefactory/scored_candidate_shadow.py` candidate/fixture/occurrence ids | `ledger_team_key(width=24)` | the pair now yields ONE identity in NEW events | old split records untouched on disk; readers unchanged |
| `scored_candidate_shadow.settle_candidate` / `load_settled_overlay` | was `norm_team` | indexes and looks up under canonical + transliterated + **frozen legacy** keys | reader-side dual-key, exact lookups only |
| `scripts/auto_tickets.py` settled map / `pick_result` | was `norm_team` | same three exact key spaces, tried before the pre-existing fallback | reader-side dual-key (`_exact_result_keys`) |
| `scripts/export_settled_results.py`, `audit_source_independence.py`, miners (`mine_/backfill_/capture_betexplorer.py`), `warehouse_replay`, `enh_pricing`, `theoddsapi`, `o25_tracker`, `replay_harness` | `norm_team` / `norm_team_sql` | both sides of every join are normalized at read time by the same function, so joins tighten rather than break; SQL mirror updated in lockstep (`norm_team_sql` now ASCII-folds, `norm_team_sql_legacy` frozen) | recomputed-on-read joins, no persisted key depends on them |
| `src/edgefactory/entities.py` override/registry lookup | `norm_team` | lookup candidate list now tries BOTH the fixed and the frozen legacy key | dual-key, additive only |

Nothing persisted is rewritten. Where a persisted artefact can be keyed by
the old normalization (settled-result overlays, warehouse result rows,
day archives, shadow ledgers), the reader tries the legacy key as an
additional EXACT key.

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

## 8. Tests

New: `tests/test_team_identity_transliteration.py` (17 tests) — accented
corpus transliteration; `norm_team`/`ledger_team_key` agreement; frozen
legacy key; one canonical key for Türkiye/Turkey (+ other exonyms); alias
explicit and visible; no false merges; end-to-end dedupe (one survivor,
one collapsed twin, `duplicate_alias_collapse` metadata); tripwire silent
when the alias resolves and loud when it cannot, merging nothing; distinct
fixtures not collapsed; settlement across spellings and from legacy keys;
one shadow identity for the pair; archive merge not inflated and engine
key == audit key.

Smoke: `python tools/smoke_fixture_identity_dedupe.py` -> `SMOKE: PASS`.

Validation: `python -m pytest tests/ -q` -> **1291 passed**;
`python -m compileall scripts src tests` clean; `git diff --check` clean;
no `.github/workflows/*` or `localdata/*` changes.

Unchanged: kickoff guards, `_fixture_orientation_agrees`,
`_row_matches_selection`, odds floors, veto bands, ladder, staking,
freeze/write-once, ticket output parity (audit on/off/crash) — the only
live behaviour change is that duplicate collapse now catches
cross-spelling twins, which is the fix.

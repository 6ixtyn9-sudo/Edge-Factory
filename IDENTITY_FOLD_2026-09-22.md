# Identity Fold Amendment — 2026-09-22 (operator-directed)

## Incident

2026-09-22, one real fixture arrived twice under two source spellings
("Dagenham & Redbridge" vs "Dagenham and Redbridge"; league "FA" vs
"England,Fa Cup"). Both pick rows rode the same acca card. The 782f3f5
emergency guard (same-fixture dedup at slip-plan) and the b6e3e21
operator-directed repaired slip contained the incident. This amendment
fixes the root cause so the duplicate class dies at capture.

## Design rules

1. **Folds only, no fuzz.** Deterministic text folding plus an explicit,
   evidence-seeded alias table. Nothing guesses similarity; two different
   real entities must never collapse into one key.
2. **Additive only.** Legacy candidate/lookup order is preserved at every
   seam; folded forms and aliases add coverage that previously returned
   UNKNOWN.
3. **Scope.** Identity seams: voter-row indexing (`source_team_key`),
   purity/entity canonicalisation (`canonical_league`, `canonical_team`,
   `_registry_lookup` candidates), slip-card dedup fold. Odds/price-
   matching keys (`odds_team_key`, `odds_match_team_key`,
   `operational_team_key`; the alias_fuzzy quarantine surface) are
   deliberately OUT of scope. Certified miner joins, warehouse joins,
   and the research ml-fade ledger fold are untouched.

## What changed

- NEW `src/edgefactory/identity.py`: `fold_identity_words` (ASCII fold,
  `&` -> `and`, punctuation collapse), `team_identity_words` (also drops
  the glue token `and`), `LEAGUE_ALIASES` + `canonical_league_key`.
- `entities.py`: folded candidates appended in `_registry_lookup`;
  `canonical_league`/`canonical_team` fallbacks go through the folds.
- `picks_today.py`: `source_team_key` folds before keying (alias map
  unchanged and authoritative on its own key shapes).
- `auto_tickets.py`: same-fixture guard fold delegates to the shared
  module (one fold definition across capture and cards).
- NEW `scripts/replay_identity_fold.py`: analysis-only measurement harness
  (not wired into any live path).
- NEW `tests/test_identity.py`: 10 tests — goldens, idempotence,
  no-merge invariants, alias behavior, picks-seam merge + alias watchdog.

## Alias evidence (evidence-seeded, same-fixture proof)

| raw label                        | folded                  | canonical target                    |
|----------------------------------|-------------------------|-------------------------------------|
| England,Fa Cup                   | england fa cup          | fa                                  |
| England,National League South    | england national league south | enterprise national league south |

Both pairs proven same-league by archive evidence (same date + same
folded home/away under both spellings, incl. today's incident fixture).

## Replay results (scripts/replay_identity_fold.py, 1,413 archived pick rows)

- Folded fixture identities with >1 raw spelling: **2** — both Dagenham
  incidents (2026-08-31 vs Slough Town; 2026-09-22 vs Waltham Abbey).
  Zero collateral merges.
- League canonicals (402 distinct labels): **400 UNCHANGED**; 2 changed
  (the two seeded aliases above); **0 regressions** (no already-resolved
  label moved).
- NOTE: during measurement, an earlier draft of the harness compared
  against raw `norm_league` instead of the true pre-amendment
  `canonical_league` (which already resolves many long-form labels via
  `Config/entity_overrides.json`, 338 league entries). The corrected
  comparison above is the honest one.

## Blast radius

- In scope, changed behavior: same-fixture duplicates collapse at voter
  indexing; `&`/`and`-split team and league names unify; the two seeded
  league aliases resolve to registry pools (CLEAN/VETO verdicts move from
  UNKNOWN/fail-closed to the registry verdict — direction is visible in
  logs, never silent).
- Unchanged: certified edges/gates; model features (league identity is
  not a model input — only competition-type flags); prices/quoting;
  settlement and ledger identity; research fold; `.frozen` semantics.

## Red-team pass (2026-09-22, hostile review of this change)

Method: fold every distinct team name in the 30-day archive corpus
(1,414 names) and measure collision surfaces pre/post.

Findings:

1. **`norm_team` width-9 truncation collisions are a LARGE PRE-EXISTING
   class** — 109 legacy keys group >1 raw name (e.g. `atletico madrid`
   and `real madrid` both key to `madrid` because the noise regex
   strips `atletico`/`real`; men's and women's/reserve squads collide
   whenever sources spell without accents). Same-day, same-source,
   same-key collisions can attach the wrong match's voter evidence.
   Not introduced by this fold; logged for a dedicated fix.
2. **This fold adds 12 net collisions** — 10 desired unifications
   (accent/`&` spellings of the SAME team: Academico/Académico Viseu,
   Bolívar, Dagenham both spellings, Málaga, Nordsjælland, Potosí,
   Zürich) — but **~2-7 false varieties** where the accent fold rescues
   a letter and then the `_NOISE` regex drops the distinguisher
   (`América W`/`Club America`, `Bodø/Glimt W`, and II/W reserve
   variants: Górnik Zabrze, Rīgas FS, Stabæk, Vålerenga). Same-day
   same-source W-vs-men's fixtures can therefore mis-attach evidence
   where plain-spelled data previously survived only via mojibake keys.
   FIXED same day (operator-directed "fix all we can now"): the
   `source_team_key` seam now delegates to the shared 24-char
   club-structure-only key in `identity.py` (`source_team_key` +
   `TEAM_KEY_RAW_ALIASES`, raw-name pairs with keys derived through the
   key function so the table can never drift). `w/ii/b/res` tokens are
   preserved; honorific stripping (`real`, `atletico`, …) is gone.
   Corpus audit: collision groups 109 -> 66 and every remaining group
   is same-club spelling variants (verified line-by-line; the only
   W-groups are `(w)`/`W` spellings of the same women's squad).
   Aliases retained + extended: Borussia M'gladbach/Mönchengladbach,
   Rodina Moscow/Moskva, Tekstil Iv./Ivanovo, Grasshopper-Club/
   Grasshoppers, Ferencvaros/Ferencvarosi TC, Haverfordwest(/County),
   Ludogorets(/Razgrad), Broadmeadow(/Magic), Leicester(/City),
   West Torrens(/Birkalla), Bayern Munich/München, plus Nordic club
   tokens {sk, if, fk, bk, ik, ff}. Legacy norm_team(9) remains byte-
   frozen for certified miners (untouched by design).
   NOT changed, deliberately: `canonical_team` fallback shape — team-ctx
   pool identities in the registry keyspace were built with
   `norm_entity_team` honorific stripping; re-shaping the fallback would
   orphan existing pools (fail-closed through missing verdicts). Any
   team-ctx re-anchor is its own evidence project.
3. **Double-alias hole closed in follow-up:** `_registry_lookup` folded
   candidate originally used `canonical_league_key` (alias table applied
   INSIDE a learned-lookup lane). Swapped to `fold_league_identity` — the
   alias table now applies only at the final `canonical_league` fallback,
   so a learned alias_index can never double-apply it.
4. **Alias-target drift tripwire added:** test asserts every
   `LEAGUE_ALIAS` target exists in the purity-registry league keyspace;
   a future sponsor-name rebuild (e.g. NLS renaming) fails loudly in
   tests instead of silently re-orphaning the alias.
5. CI references for `localdata/entity_registry.json`: none in
   `.github/workflows` — the learned-alias lane is dormant in CI today
   (validated empty locally; build_entity_registry.py is the only
   writer).

Accepted residual risks (documented, not silent): folded keys are
deliberately coarser than raw strings; dedup in slips also keys on
date+home+away; by_key last-wins within one (source, day) is unchanged
legacy semantics.

## Authority

Operator direction 2026-09-22 (build ordered after the same-day incident
review, following the same test-first + replay-prove pattern as the fade
folds). Rollback is a revert of this commit.

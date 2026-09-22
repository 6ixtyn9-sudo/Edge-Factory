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

## Authority

Operator direction 2026-09-22 (build ordered after the same-day incident
review, following the same test-first + replay-prove pattern as the fade
folds). Rollback is a revert of this commit.

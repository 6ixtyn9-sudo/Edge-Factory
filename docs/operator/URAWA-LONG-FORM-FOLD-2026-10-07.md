# Urawa long-form fold — closed by commit `d6d163d` (2026-10-07)

This document describes a **past state**: the defect existed at `5bdecdd`
(production run 37570304076) and was closed by `d6d163d`. Re-read it as
history, not as current behaviour.

## What the run showed

`localdata/source_health_2026-10-07.json` (committed) records the SharpAPI
board census: 200 rows, 4 fixtures, one of them
`Urawa Red Diamonds vs Omiya Ardija` — the Japan Emperor Cup fixture our card
files as `Urawa vs Omiya Ardija`. The card row in
`localdata/picks_2026-10-07.json` carried `odds_match_method="alias_fuzzy"`,
`odds_match_status="suspect"`, `price_evidence="SUSPECT_ALIAS_FUZZY"` and
`price_push_eligible=false`, with the vendor's `1.741` (draftkings) archived
as `suspect_price` instead of used.

That is a **naming gap, not a coverage gap** — the opposite case to
CR Belouizdad vs Khenchela, which was absent from the board under every
spelling and is therefore not fixable by any alias.

## Step 1 — fold direction was measured, not guessed

Senior men's club only, marker-aware keys, read from committed artefacts
(no vendor calls, no network):

| space | `urawa` | `urawaredd` (long form) | `urawareds` ("Urawa Reds") |
|---|---|---|---|
| `localdata/settled_results.json`, 90-day window | 10 rows / 10 fixture-dates | 15 / 15 | 16 / 16 |
| warehouse `forebet` + `statarea` + `zulubet` | 480 rows / 460 fixture-dates | 107 / 107 | 22 / 22 |

Both names are already written. The tie-breaker is the operational spaces,
which is what the fold actually has to preserve: every live artefact of this
fixture — `picks_*.json`, `clv_unmatched_2026-10-07.json`,
`ml_fade_research_ledger.json` — already carries the key `urawa`, and our own
card writes the short form. Warehouse dominance is 4:1 for `urawa`.

**Fold direction: long form → `urawa`.** Folding the other way would have
re-keyed the live pipeline's own rows.

Settlement count above is *not* three competing identities in today's code:
`bettingclosed`'s `Urawa Red Diamon` truncation and `forebet`'s long form both
already key to `urawaredd` via width-9 truncation. `urawa` and `urawaredd` are
the two real clusters; "Urawa Reds" remains outside this fold (below).

## Step 2 — the minimal change, and its blast radius

| file | change | reaches |
|---|---|---|
| `Config/entity_overrides.json` | `Urawa Red Diamonds` / `urawa red diamonds` / `urawa` → `urawa` | entity/context keys, purity-context lookups, voter-row `source_team_key`, settlement `_folded_leg_key`/`leg_lookup_key` |
| `scripts/picks_today.py` `ODDS_EXACT_TEAM_ALIASES` | `urawaredd` → `urawa` | the exact (width-9) price join |
| `scripts/picks_today.py` `ODDS_MATCH_TEAM_ALIASES` | `urawareddiamonds` → `urawa` | the timed join and the board census (`card_fixtures_on_board`) |

Blast radius is bounded to rows that resolve to the **long form**:

* `norm_team("Urawa Red Diamonds")` stays `urawaredd` — the certified
  miner/warehouse join key is untouched, so no backtest or certified edge is
  re-keyed;
* `canonical_team("Urawa Red Diamonds")` moves `urawareddiamonds` → `urawa`;
  `canonical_team_variants()` still returns the pre-alias key, so purity or
  veto evidence written under the old key is still found (a canonicalisation
  that orphans a VETO would be worse than the split it fixes);
* the long form appears in **no** row of `localdata/source_health_2026-10-07.json`
  as a pick/card key, so nothing in the live 2026-10-07 slate changes except
  this fixture's join.

## Step 3 — what was deliberately NOT folded

`"Urawa Reds"` (betexplorer/scoutingstats spelling) is **not** in the width-9
map. That key space drops the squad marker, so folding it would also merge
`Urawa Reds W` onto the men's key. The women's sides stay distinct in every
marker-aware space (`canonical_team_key`, `canonical_team`, `source_team_key`).

Known pre-existing wart, recorded so it is not mistaken for damage from this
change: width-9 `pt.odds_team_key("Urawa W")` already equals
`pt.odds_team_key("Urawa")` because `norm_team` strips the `w` noise token.
No observed women's long-form spelling exists in the warehouse, the settled
window or the SharpAPI board.

## Step 4 — the guard was watched failing

Both mutations were applied to the real files, run, and restored:

| mutation | result |
|---|---|
| remove the `Config/entity_overrides.json` entries (the historical defect verbatim) | `test_curated_alias_donor_spelling_joins_the_card_pick_exactly` FAILED — the receipt pair left the folded set |
| keep the config entry, remove both odds-map entries (fold never reaches the price join) | identity-layer pairs still PASS, join test FAILED — the guard watches the join, not the table |
| restore | 1850 passed; `verify_work_order.py` 14/14 ALL PASS; `verify_wo7.py` 9/9 |

The tests live in `tests/test_team_identity_transliteration.py` beside the
existing curated-alias tests and are **derived from the curated table**: every
curated pair must fold at every identity seam, and every pair folded in both
curated layers must join a donor price as `exact`. A newly curated team is
covered by construction, with its own receipt case pinned where one exists.

## Step 5 — verification (OBSERVED, not inferred)

Reproduced on this checkout after restore:

* `python3 scripts/verify_work_order.py` → `14/14 passing` / `ALL PASS`
  (tripwire raised 1524 → 1526, the measured `def test_` count);
* `python3 scripts/verify_wo7.py` → `9/9 checks pass`;
* `PYTHONPATH=src python3 -m pytest tests/ -q` → `1850 passed`;
* mocked end-to-end (no vendor call): the captured vendor row joins by
  `exact`, `odds` becomes the vendor's `1.741` from `sharpapi_odds`/draftkings,
  `price_evidence != SUSPECT_ALIAS_FUZZY`, `price_push_eligible is True`, no
  `price_quarantine_reason`.

**Scope boundary.** The end-to-end proof uses a hand-built row with the
vendor's captured field values and the production bundle/matcher functions; it
is a contract proof, not a replay of the live run (the sandbox has no vendor
network). The claim being made is narrow: *this spelling now resolves to this
key and joins exactly*. It is not a claim that the Emperor Cup fixture is
priced or stakeable — its league verdict is still `UNKNOWN`.

## Out of scope, stated for the record

* **CR Belouizdad vs Khenchela** — absent from the board entirely (coverage
  gap), its `1.33` comes from a different source, and it is veto-skipped on
  context. No alias helps it. Fixing it would need the same board-census
  instrument we built for SharpAPI, pointed at the source that fuzzy-matched it.
* **Unknown competition verdicts** (`Japan Emperor Cup`, `Algeria: Ligue 1`) —
  still absent from the `leagues` block; that is the optional follow-up commit
  and is not part of `d6d163d`.

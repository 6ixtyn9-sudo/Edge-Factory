# Urawa long-form fold — closed by `d6d163d`, corrected by `1ac5ebc` (2026-10-07)

This document describes a **past state**: the defect existed at `5bdecdd`
(production run 37570304076) and its two halves were closed by `d6d163d` (the
fold) and `1ac5ebc` (the squad-marker guard the first commit lacked — see
"Correction" below). Re-read it as history, not as current behaviour.

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

Both names are already written, and the two spaces **disagree**. Stated
plainly, because a reader looking only at the settled window would have folded
the other way:

* settled window (senior men's, marker-aware): `urawa` 10 rows against **31**
  across the two long forms (15 + 16);
* warehouse: `urawa` 480 rows against 107 + 22 = **129** — a factor of ~3.7,
  not 4:1, once "Urawa Reds" is counted rather than the long form alone.

The tie-breaker was therefore not the settled history; it was the operational
spaces, which is what the fold actually has to preserve: every live artefact of
this fixture — `picks_*.json`, `clv_unmatched_2026-10-07.json`,
`ml_fade_research_ledger.json` — already carries the key `urawa`, and our own
card writes the short form.

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

## Step 3 — what was deliberately NOT folded, and the identity is not closed

`"Urawa Reds"` (betexplorer/scoutingstats spelling) is **not** in the width-9
map. That key space drops the squad marker, so folding it would also merge
`Urawa Reds W` onto the men's key.

The same sentence was true of the entry that WAS folded: width-9
`urawaredd` is `Urawa Red Diamonds W` truncated exactly as it is
`Urawa Red Diamonds`. The reasoning above was applied to one branch and not the
other; that is the defect the Correction section fixes. With the guard in
place both entries are safe, and the rule is general: an alias may canonicalize
the club, never the squad.

**The identity is not closed**: `urawa` and `urawareds` remain two keys for this
club (three before `d6d163d`), so the fold reduced the split, it did not
eliminate it. Reported here so "closed by `d6d163d`" in the title is not read
as "one key".

Known pre-existing wart, recorded so it is not mistaken for damage from this
change: width-9 `pt.odds_team_key("Urawa W")` already equals
`pt.odds_team_key("Urawa")` because `norm_team` strips the `w` noise token.
That is truncation/stripping, not aliasing — the guard cannot help it, and it is
in the same class as the 87 curated pairs that collapse with no alias involved
(measured; see Correction). No observed women's long-form spelling exists in the
warehouse, the settled window or the SharpAPI board.

## Step 4 — the guard was watched failing

Both mutations were applied to the real files, run, and restored:

| mutation | result |
|---|---|
| remove the `Config/entity_overrides.json` entries (the historical defect verbatim) | `test_curated_alias_donor_spelling_joins_the_card_pick_exactly` FAILED — the receipt pair left the folded set |
| keep the config entry, remove both odds-map entries (fold never reaches the price join) | identity-layer pairs still PASS, join test FAILED — the guard watches the join, not the table |
| restore | 1850 passed — the collected count **at `d6d163d`**, i.e. *with* the two new tests already present (their 158 collected cases: 157 seam cases + 1 join case); `verify_work_order.py` 14/14 ALL PASS; `verify_wo7.py` 9/9 |

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
* `PYTHONPATH=src python3 -m pytest tests/ -q` → `1850 passed`. Read that
  number with its baseline: it is the whole-suite **collected** count at
  `d6d163d`, the two new tests included. `tests/test_team_identity_transliteration.py`
  collected 185 cases before the change and 343 after it (185 + 157 + 1), so
  the parametrization raised the suite by ~158, not by 1. The suite moved
  1850 → 1851 only when this *document* was added, because
  `tests/test_docs_links.py` parametrizes one case per Markdown file
  (re-measured 2026-10-07: adding a doc moves the suite by exactly 1);
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

## Correction (2026-10-07) — the fold crossed a squad marker; closed by `1ac5ebc`

Found by re-deriving the pushed commit rather than by reading its message.

**OBSERVED, at `d6d163d`.** The width-9 key space strips a distinct-entity
marker before truncating, so `Urawa Red Diamonds W` keys as `urawaredd` — the
exact key the new alias mapped to `urawa`. `find_odds_row` builds its exact key
from that function, so a women's/reserve spelling produced a byte-identical join
key to our card row:

| spelling | width-9 key pre-`d6d163d` | at `d6d163d` (defect) | after `1ac5ebc` |
|---|---|---|---|
| `Urawa` / our card | `urawa` | `urawa` | `urawa` |
| `Urawa Red Diamonds` | `urawaredd` | **`urawa`** | **`urawa`** (the fold, preserved) |
| `Urawa Red Diamonds W` | `urawaredd` | **`urawa`** ← defect | `urawaredd` |
| `Urawa Reds W` | `urawareds` | `urawareds` | `urawareds` |

Join receipt, mocked bundle through the real `_odds_bundle_from_rows` +
`find_odds_row`: vendor `Urawa Red Diamonds W` returned method **`exact`** with
odds `1.741` — the most trusted verdict, no quarantine. Re-derived from
`5bdecdd`'s maps (the function body is unchanged; only the maps gained entries),
the same row keyed `urawaredd` and did **not** join at all. The change converted
a dormant collision into a live one on the path that attaches prices to picks.

**The class, measured so it cannot be overread.** 17 of the 157 curated pairs
were alias-bridged across a marker (the guard changes exactly these); a further
87 marked variants collapse onto their canonical **by truncation/stripping alone**
— pre-existing, and explicitly *not* fixed by this guard. Across 2,877 archived
pick rows carrying 140 distinct marked names, **zero** sat on an alias key, so no
live join changes.

**Fix.** One helper, three call sites: the odds key functions refuse the alias
lookup when the raw name carries a squad marker. The rule is already the entity
layer's (`entities.canonical_team`: *"the alias canonicalizes the CLUB, never the
squad"* — it re-attaches the marker, resolving `Urawa Red Diamonds W` to
`urawa_w`). The direction is fail-closed: a marked spelling keeps its unaliased
key and may still be *seen* by the similarity fallback, which quarantines it
(`SUSPECT_ALIAS_FUZZY`, never push-eligible) — the exact verdict is what it can
no longer claim.

**Guards.** Two table-derived tests in `tests/test_team_identity_transliteration.py`:
the rule (all 157 curated pairs; a marked variant receives no alias) and its join
consequence (the 17 bridgeable pairs must never return `exact`, receipt pair
included). Mutation receipt: guard removed → **18 failed** (17 parametrized cases
+ the join case); restored → green. `def test_` floor 1529 → **1531** (measured).

**Still open, recorded so this is not read as closed:** the truncation class
(`odds_team_key("Urawa W") == "urawa"`) and the similarity fallback's marker
blindness are pre-existing and untouched. Both are narrower than what was fixed —
neither can promote a row to `exact` — but neither is gone.

## Out of scope, stated for the record

* **CR Belouizdad vs Khenchela** — absent from the board entirely (coverage
  gap), its `1.33` comes from a different source, and it is veto-skipped on
  context. No alias helps it. Fixing it would need the same board-census
  instrument we built for SharpAPI, pointed at the source that fuzzy-matched it.
* **Unknown competition verdicts** (`Japan Emperor Cup`, `Algeria: Ligue 1`) —
  still absent from the `leagues` block at `d6d163d`; added by the follow-up
  commit `eefcdfd`, which declares their identity only (no purity context
  exists for either, so both still resolve `UNKNOWN`).

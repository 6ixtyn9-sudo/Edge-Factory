# PR138 squad/side safety follow-up — 2026-10-23

Baseline: merged PR138, `6e44bfb157c25b9d4554d2cb252be5f445f9904d`.
This is the bounded four-correction follow-up authorized after the independent
review, not a broader audit or a claim that every provider identity is resolved.

## Changes and intentional output differences

| Finding | Correction | Intended change on adversarial inputs |
| --- | --- | --- |
| F1: unrecognized squad spellings | Existing `squad_markers` recognizes explicit U/Under/Sub + numeric ages after punctuation folding, retaining the particular age; adds Femenil/Frauen to the women class. | A senior selection cannot use these youth/women quotes. U21 and Under-21 agree; U21 and U23 do not. Bare Under/Sub and Frauenfeld are not markers. |
| F2: exact-key quotes lacked a per-quote veto | Check each identity-bearing quote, in pick orientation, before admission/latest-offer/consensus processing. Apply the same check to the unclocked aggregate path when row-level quotes exist. | A higher wrong-squad quote no longer displaces a valid senior quote; a wrong-squad-only slot becomes unpriced. Invalid seven-field identity metadata fails closed. |
| F3: older reverse lookup omitted double chance | Remap `1x` ↔ `x2` alongside the existing home/away team-total remap. | The reversed feed's opposite-side double chance cannot price the selection; the correct feed-side slot can. |
| F4: callback could replace strict alias matching | The exact-pair/missing-slot alias branch always requires the strict default matcher; an optional callback is an additional restriction. | A permissive callback cannot admit Manchester United for Manchester City. Valid strict aliases remain available unless the callback vetoes them. |

No changes to `source_team_key`, `source_team_key_base`, persisted keys, price
maps, capture scope, staking, thresholds, tickets, financial history, workflows,
or provider admission receipts. Historical five-/six-field exact quote tuples
retain their prior behavior. An aggregate-only index without raw quote evidence
cannot acquire a per-quote veto; that compatibility behavior remains unchanged.
Existing exact slots still do not gain an alias escape after rejection.

The old callback-based orientation test was changed to a genuinely ambiguous
United/United FC vs Manchester United/Leeds United fixture. A permissive callback
must not itself manufacture ambiguity for an otherwise valid strict alias.

## Validation

- **51 additional regression cases**: against baseline source + baseline Config,
  **47 failed, 4 passed**; with the patch all pass. The four baseline passes are
  five-/six-field compatibility and orientation-aware positive controls.
- Focused suite: **389 passed** (pricing, identity, receipt, kickoff, enhancement
  lane, capture scope, OddsPapi schema, TheOddsAPI).
- Final full suite: **3,999 passed, 1 skipped**, 166.71 seconds.
  The skip is `tests/test_fixture_decision_logging.py:207`, whose immutable
  historical baseline commit is absent from this checkout; confirmed separately
  with `pytest -q -rs tests/test_fixture_decision_logging.py`.
- Socket-blocked retained-input comparison: **38 picks × 29 mapped markets =
  1,102 cells; 236 priced on both versions; 0 gains, 0 losses, 0 changes** to any
  `enhancement_*` attachment field, including rejection and provenance fields.
- **19,873 distinct raw names** from the picks, settled results, and October
  TheOddsAPI/OddsPapi archives: identical `source_team_key` outputs on both versions.
- **940 SHA256-protected tracked files** under `localdata/`, `scripts/`, and
  `.github/workflows/`: unchanged before/after the tests and replay.
- `git diff --check` clean. No workflow dispatched; no operational lane paused.

### Replay protocol and receipts

Each version ran in a fresh Python process. Baseline `src/` **and `Config/`** were
extracted with `git archive 6e44bfb src Config` into a scratch directory, and
selected via `PYTHONPATH`; the candidate used the checkout's `src/`. Both loaded
the same checkout's local inputs with `load_prices_index(root, '2026-10-22')`.
`EDGE_FACTORY_ENH_BOARD=1` and `EDGE_FACTORY_ODDSPAPI_PRICES=1` were set only in
these diagnostic processes; sockets were blocked. Every pick was copied for each
non-null `MARKET_PRICE_MAP` entry and passed to `attach_enhancement_price`.
All `enhancement_*` fields were compared, not merely the best price.

An initial scratch extraction omitted Config and triggered the explicit
zero-curated-alias warning/key-digest mismatch. That invalid baseline run was
rejected and replaced with the complete baseline source/config comparison above.

Shared attachment SHA256 (sorted compact JSON of the ordered comparison rows):
`18cd9d5952ac61448e0953a447e463ebe06ed70964d38ee2baad9ef45700c6fa`.
Shared identity-key SHA256 (JSON of sorted `(raw_name, source_team_key)` tuples):
`c3f0c518f6fdae4a83978e303a806185b04c7f76ddcd99a11060c8e8310d048f`.

Principal input SHA256s:

| File | SHA256 |
| --- | --- |
| `localdata/picks_2026-10-22.json` | `da4bb19a8a3cebbef968b0c2391e478e6ac8ca4cde296bd80ae29de74e5ae8ae` |
| `localdata/settled_results.json` | `fb524329e6e38738d404651dfbf01b50923934d1cfa91f6051990a0ffa10467b` |
| `localdata/theoddsapi_odds_2026-10.csv.gz` | `aabf6428fa8b1db8abfb4e5bc847d22eebad72a8454418299ef9206d27677eea` |
| `localdata/oddspapi_odds_2026-10.csv.gz` | `b788fc6fc1cb8126260d094c3fc796bbee39131aa5dab5229d38b0f1f32a0b48` |
| `Config/entity_overrides.json` | `f174c680a26a6ac713655b1d19c73bf676d74fb2fded00bca348d869a792154f` |

Test reproduction: `PYTHONPATH=src .venv/bin/python -m pytest -q`.
Protected tracked-path reproduction:
`git diff --exit-code 6e44bfb -- localdata scripts .github/workflows`.
Scratch diagnostics are not a new production pipeline or committed dataset.

## Limits

These are local regression and retained-input results, not an independent
post-patch audit, production coverage guarantee, ticket admission decision, or
profitability claim. The retained slate contained no attachment-level instance
requiring correction; the intentional wrong-squad/wrong-side differences are
proved by the adversarial regressions. Vocabulary remains finite. The callback
restriction described here applies to the newly introduced missing-slot alias
branch, not a rewrite of the older pair-absent lookup policy.

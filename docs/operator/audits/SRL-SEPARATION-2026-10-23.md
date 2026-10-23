# SRL separation — 2026-10-23

## Authorization and scope

User authorized: **“PROCEED WITH THE SRL PATCH.”** Baseline:
`6c94fc6b669a5e221caabfb0142b8be3e224a280` (merged PR #139).

This patch separates explicitly labelled Simulated Reality League events from
real-club fixtures using the existing identity/admission machinery. It does not
introduce a registry, pipeline, workflow, or source-key migration.

## Change

- `src/edgefactory/identity.py`: add the shared `simulation` squad-marker class.
  Recognize standalone `SRL`, case variants, punctuation-folded `S.R.L.` / `S-R-L`,
  and `Simulated Reality League`. Do not strip these labels from persisted keys.
  Existing per-side squad checks consequently reject real/simulation mismatches,
  including exact-key collisions in retained quote admission.
- `scripts/capture_oddspapi.py`: remove simulation-labelled fixtures on **either
  participant** after fresh/cached board loading and before overlap diagnostics,
  pending selection, market lookup, and odds requests. Preserve original board
  count in `fixtures`; report exclusions in `excluded_srl_fixtures`.
- Regression coverage uses the real enhancement CSV loader and admission path,
  not merely a capture filter or a mocked pricing result.

No staking, ticket, settlement, workflow, financial history, or provider adapter
changes. No live provider requests or workflow dispatches performed. No merge
authorized or performed for this patch.

## Regression evidence

Initial regressions before production edits: **15 failed, 30 passed**
(124 deselected). This covered the shared marker and capture/admission changes.

Additional retained OddsPapi schema-3 loader matrix: **14 failed, 2 passed**
against the baseline; all **16 passed** with the patch. Baseline tests ran in an
isolated archive containing baseline `src`, `Config`, and `scripts`, with copies
of the candidate tests/conftest. This avoids the repository conftest overriding
`PYTHONPATH` and accidentally testing candidate modules as the baseline.

The retained-loader matrix exercises:

- Alanyaspor / Kocaelispor and GO Ahead Eagles / SC Telstar;
- SRL on either participant;
- simulated-only quotes and mixed real/simulated quotes;
- kickoff/contract-qualified picks and unqualified legacy picks;
- Under 2.5;
- actual schema-valid archived CSV loading, with an assertion that all test rows
  reached the quote index (including the non-colliding short Telstar alias case).

Mixed-quote exact/alias tests additionally cover `SRL` and `S.R.L.`; identity tests
cover case, punctuation, the full phrase, and ordinary-club negative controls.
Fresh and cached capture tests put three simulated fixtures ahead of a real
fixture with a one-fixture budget: simulation cannot displace that real request.
SRL-only boards must request neither markets nor odds.

Commands and results:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_enh_pricing.py tests/test_betexplorer_identity_guard.py \
  tests/test_capture_oddspapi_round3.py tests/test_oddspapi_enh.py \
  tests/test_oddspapi_schema_invalidation.py tests/test_secondary_quote_admission.py \
  tests/test_squad_identity.py tests/test_identity_adversarial.py \
  tests/test_theoddsapi.py tests/test_price_red_team_2026_10_15.py \
  tests/test_price_quarantine.py
392 passed in 1.35s

PYTHONPATH=src .venv/bin/python -m pytest -q -rs
4031 passed, 1 skipped in 175.49s
```

The skip is `tests/test_fixture_decision_logging.py:207`: immutable historical
baseline commit unavailable in this shallow checkout. `git diff --check` clean.

## Read-only archived comparison

Separate baseline/candidate Python processes loaded the same retained repository
inputs through `load_prices_index` / `attach_enhancement_price`. Replay explicitly
enabled the existing enhancement board and OddsPapi prices. Socket connections
were forbidden. Each process iterated every supported enhancement-market mapping
for each stored pick; all returned `enhancement_*` fields were compared.

| Input | Result |
| --- | --- |
| Oct 22 stored picks | 38 |
| Oct 23 stored picks | 67 |
| Supported enhancement markets per pick | 29 |
| Total fixture/market cells | 3,045 |
| Priced cells, baseline / candidate | 331 / 331 |
| Changed enhancement outputs | 0 |

This is a compatibility replay of the archives available in this checkout, not
proof of the provenance of the Oct 23 workflow's actual draft or that all its
latest artifacts were present. The adversarial retained-loader regressions,
not zero replay changes, demonstrate the new rejection of SRL quotes. Future
withdrawals of prices genuinely supported only by simulation quotes are intended.

Source-team keys were compared for **19,847 unique nonempty raw names** from the
Oct 22–23 picks, settled results, and October TheOddsAPI/OddsPapi retained CSVs.
Sorted `(raw name, source_team_key)` digests were identical:

```text
79e789d0e937ef0cf520c13b9d145bdab1d87d31b1aada5ca1617d4fd80536ee
```

A pre-edit SHA-256 manifest covered **951 tracked paths** under `localdata/`,
`scripts/`, and `.github/workflows/`. **950 remained byte-identical**; the sole
intentional exception was `scripts/capture_oddspapi.py`.

## Limits

Recognition is intentionally limited to explicit SRL labels. It does not infer
unlabelled virtual/esoccer events or attempt a general competition taxonomy.
Existing legacy quote tuple contracts remain unchanged. Offline tests and this
replay do not establish future provider coverage or betting profitability.

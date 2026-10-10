# Dated claims ledger

Every comment in the code that cites a **dated observation** — a receipt, a
verification, a confirmation, something "observed on" a date — has a row
here saying what backs it. `tests/test_dated_claims_ledger.py` holds the two
halves together: a new dated claim in a comment fails the suite until a row
is added, and a row whose backing names a file fails if that file is not on
disk.

## Why this exists

A comment in the Pinnacle relay adapter read:

> `# Panel receipt 2026-10-02: soccer is sport_id=2 ...`

Nothing had been captured. It was an inference given the form of an
observation, and because it read like a receipt nobody re-checked it; the
adapter asked for the wrong sport for four days. The cost of that was not
the wrong number — it was that the wrong number looked settled.

Writing a dated claim is now a two-line diff: the comment, and a row here
stating whether an artifact exists or whether somebody simply said so.

## What the `backing` column may say

| value | meaning |
|---|---|
| a repo path | the artifact is in the repository and the test asserts it exists |
| `OPERATOR-RELAYED` | a person reported it; no artifact in the repo. Not evidence |
| `RUNTIME-OBSERVED` | seen in a production run; the log or output is not retained here |

`OPERATOR-RELAYED` is not a failure and does not need fixing. It needs
labelling, so the next reader knows the difference between a receipt and a
recollection.

## Ledger

| file | claim | backing |
|---|---|---|
| `src/edgefactory/enh_pricing.py` | column map verified against the scoutingstats column list, 2026-08-03 | `src/edgefactory/sources/scoutingstats.py` |
| `src/edgefactory/sources/oddspapi_odds.py` | outcome-name field `name` verified 2026-08-05 fixture payload | `tests/fixtures/oddspapi_odds_fixture.json` |
| `scripts/capture_oddspapi.py` | the odds payload observed on 2026-10-03 carried no participant names | `docs/operator/PRICE-LANE-TEARDOWN-2026-10-03.md` |
| `scripts/picks_today.py` | 2026-10-03 TheOddsAPI receipt: provider shortens two English club names | OPERATOR-RELAYED |
| `scripts/picks_today.py` | 2026-10-03 TheOddsAPI receipt, cross-reference to the exact-key aliases | OPERATOR-RELAYED |
| `scripts/picks_today.py` | on 2026-10-03 every zone-free renderer observed | RUNTIME-OBSERVED |
| `tests/test_kickoff_guard_direction.py` | renderings verbatim from the 2026-10-03 picks file | `localdata/picks_2026-10-03.json` |
| `tests/test_team_identity_transliteration.py` | 2026-10-07 SharpAPI receipt: the vendor's long-form spelling must not fall through to the bigram matcher | `localdata/source_health_2026-10-07.json` |
| `scripts/picks_today.py` | 2026-10-07 correction to the Urawa fold: 17 of 157 curated pairs were alias-bridged across a squad marker (all released by the guard); the key space is marker-blind for 145 of 150 marked names in the live populations, so the exact tier now also requires the raw names to agree on squad markers | `docs/operator/URAWA-LONG-FORM-FOLD-2026-10-07.md` |
| `src/edgefactory/sources/theoddsapi.py` | comma-form league labels observed in the 2026-10-10 attempt ledger; sport keys verified against the provider catalogue captured the same run | `tests/data/theoddsapi_sports_2026-10-10.json` |
| `src/edgefactory/sources/theoddsapi.py` | Scotland,Championship containment hit on the EFL Championship title observed in the 2026-10-10 capture receipt | `localdata/theoddsapi_capture_2026-10-10.json` |
| `tests/test_theoddsapi.py` | per-label resolution expectations mirror the 2026-10-10 attempt ledger | `localdata/theoddsapi_capture_2026-10-10.json` |
| `src/edgefactory/identity.py` | wrong-squad cache rows observed in the 2026-10-10 odds cache | `localdata/betexplorer_odds_cache_2026-10-10.json` |
| `src/edgefactory/sources/betexplorer_odds.py` | Dender vs Club Brugge KV U23 rows under the RAAL La Louvière vs Club Brugge KV cache key, 2026-10-10 | `localdata/betexplorer_odds_cache_2026-10-10.json` |
| `tests/test_betexplorer_identity_guard.py` | regression fixtures reproduce the 2026-10-10 cache evidence | `localdata/betexplorer_odds_cache_2026-10-10.json` |
| `src/edgefactory/sources/pinnapi_odds.py` | 3,418 prematch events with teams and no markets container observed 2026-10-10; periods tree is the documented prematch shape per vendor docs consulted 2026-10-10 | `localdata/source_health_2026-10-10.json` |
| `tests/test_pinnapi_odds.py` | documented-shape fixture values taken from the vendor's published example, 2026-10-10 | `tests/fixtures/pinnapi_prematch_documented.json` |

## What this does not catch

It catches a claim about the **outside world** stated without backing. It
does not catch a confident claim about **our own** behaviour — the same work
order produced a test whose docstring asserted that conflating two different
failures was acceptable, and explained why. That claim cited no date and
named no receipt, so no ledger would have stopped it. Only review did.

A count or a ledger is a tripwire against gutting, not a guarantee against
substitution.

It also says nothing about the **scope** of a measurement, which is a
separate failure: a scan reporting "clean" from inside a six-commit slice
of a 1,528-commit history is accurate, reproducible, and wrong in the way
that matters. Provenance is this file's job; scope is ticket (k).

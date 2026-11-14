# Game-attrition logging: find the actual failed gate

The existing scored-candidate ledger now records **why each source fixture key did or did not emit a 1X2 candidate**, including keys that never reach ML scoring. This is observability, not a relaxation of filters or a new betting/shadow lane.

## Where to look

Normal pipeline stderr now includes:

```text
fixture attrition YYYY-MM-DD: source_keys=... decision_records=... reasons={...}
fixture attrition YYYY-MM-DD route=consensus: {...}
fixture attrition YYYY-MM-DD route=ml: {...}
fixture attrition YYYY-MM-DD route=ml_fade: {...}
```

The existing append-only file is still:

```text
localdata/scored_candidate_shadow_YYYY-MM-DD.jsonl
```

It contains additive `fixture_decision` events for the full source-key union. Existing `scored_fixture` events still mirror **exactly** `ml_scored_day or n_up`; the extra diagnostic events do not enter settlement, gradeability or ROI. They contain no fetched provider payload, model weights, credentials or invented prices.

Use the existing read-only report:

```bash
PYTHONPATH=src python scripts/scored_candidate_shadow_report.py \
  --date YYYY-MM-DD --json .cache/game-attrition.json
```

Its **1X2 SOURCE-KEY ATTRITION** section shows:

- Latest picks-build run ID, raw scan source-key count and target-date record reconciliation.
- Counts by primary reason, independent consensus/ML/fade reason counts and actual source probability coverage.
- Up to three example games per failed primary reason, with consensus rule/threshold evidence and investigation hints.
- Pre-match, ML-contract, bucket-floor and duplicate-collapse candidate rejections at their own stages. Existing ticket-level rejection sections retain price, ranking, policy and frozen-card reasons.

The JSON includes every `fixture_decisions` row, `source_attrition.examples_by_reason`, per-source raw names/league/kickoff, probability triples, each source's selection, missing/invalid probability fields, selected rule and effective threshold. The three human-readable examples are a display bound, **not a cap on the persisted fixture evidence**.

## Reasons and what to investigate

| Primary consensus reason | Evidence captured | Next investigation—not an automatic gate bypass |
|---|---|---|
| `insufficient_probability_sources` | Source presence, usable count, missing/invalid fields, individual source names/probabilities | Source outage versus league coverage, parser problem or exact fixture-key split |
| `schedule_unstable` | Conflicting dated kickoffs and permitted date spread | Stale schedule or identity disagreement |
| `voter_disagreement` | Every source's side/probabilities and vote counts | Actual disagreement; evaluate alternate-market evidence separately if appropriate |
| `no_consensus_rule_for_source_count` | Observed source count and active rule slots | Registry/electorate coverage |
| `competition_requires_more_sources` | Competition classification, required/observed count, base/adjusted threshold | Misclassification versus an intentional friendly/cup constraint |
| `below_consensus_threshold` | Actual average, base/effective threshold, shortfall in percentage points | Quantify the excluded band before testing a threshold change |

Independent ML/fade reasons distinguish missing model, missing eligible legacy-source probabilities, a shared input/schedule guard, no certified ML/fade rules, no qualifying certified rule and a draw with no binary inverse. A model score below a consensus threshold is **not** itself an ML rejection explanation.

If ML emits while consensus fails, the primary result is **`candidate_emitted`**, not a discarded game. The consensus rejection remains visible on its own route. Historical-electorate/qualifier mismatches that only relabel a consensus rule are explicitly logged as **relabel, not reject**.

## Later drops no longer disappear

The existing operational pre-match filter can append diagnostic copies of the candidates it rejects: actual reason, decision timestamp, minimum lead, display kickoff and resolved UTC kickoff. The live pipeline passes those records to the existing ledger hook. ML constant-feature contract removals are captured similarly, using the same actual removal predicate.

Those candidates receive scored/status records with their true rejection stage; they are **never reinserted into picks, cards or execution**. Bucket-floor records preserve specific `bucket_drop_reason` values such as `unknown_odds_band_no_evidence` rather than replacing every cause with a generic odds-floor label. Surviving watchlist/VETO bucket tags are not mislabeled as discarded games.

## Avoid misleading denominators

1. Source keys are not unique verified games. The raw source key and source names are retained so alias/identity splits can be investigated.
2. Full-source decisions are distinct from ML-scored fixtures, emitted candidate identities, merged daily archives and frozen tickets. Multiple rules can identify the same game.
3. A scan can contain other trading dates. Decision rows route to their own date; the summary records both full scan count and expected target-date count. Reconciliation compares like with like.
4. The primary decision scope is **1X2 candidate generation**. Independent binary generators and enhancement-market competition are separate; their existing candidate/market logs still apply.
5. The report never borrows prior-run diagnostics to explain the latest build, or overwrites historical ledger records. Old `no_candidate_emitted` records remain explicitly unavailable until new runs capture the missing inputs. No retrospective reason reconstruction from current data.
6. Missing quotes, unavailable outcomes and unproven kickoff evidence do not become losses or stakeable prices. Source absence should be correlated with the existing source-health receipts, not automatically called an outage.

## Safety and validation

- Existing `EDGE_FACTORY_SCORED_SHADOW=0` disables ledger writes; selection remains unchanged.
- Audit collection/writing failures are reported and do not affect pick generation.
- No new provider calls, model fitting, thresholds, price floors, stakes, bucket eligibility, freeze behavior, workflow dispatches or settlement rules.
- Tests cover concrete branch reasons, actual threshold/competition adjustments, missing/invalid source fields, independent ML/fade routes, pre-match/bucket drops, full-union versus ML reconciliation, calendar routing, historical missing evidence, disabled logging and collection/disk failures.
- A 300-case seeded comparison verifies entire pick dictionaries, veto/count outputs and research collector rows against pre-instrumentation commit `9e52ed2`. That immutable-history check skips explicitly in shallow checkouts lacking the commit; ordinary branch/reason/fail-soft tests do not require Git history.

[Validation receipt](audits/game-attrition-logging-validation-2026-10-19.json). [Original attrition diagnosis](audits/GAME-ATTRITION-2026-10-19.md).

**Deployment boundary:** these logs describe runs that execute this code after deployment. Adding logging neither reruns today's frozen slips nor recovers the exact reasons absent from earlier records. No automatic “fix” admits more games: the evidence identifies which source/parser/identity issue or intentional rule needs a separately tested correction.

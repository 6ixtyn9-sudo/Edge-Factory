# Why so few games reach the card — 19 October 2026

## Finding

**Most visible attrition is upstream of enhancement-market competition, not the card's three-acca limit.** Broadening cohort-market eligibility does not broaden the set of fixtures entering that competition: `compute_dynamic_enhancement()` is called on the surviving parent picks, after the 1X2 candidate and operational gates.

This is a read-only diagnosis of retained evidence. No sources were fetched, provider budgets spent, filters changed, slips regenerated or workflows dispatched.

## Latest recorded build: distinguish the populations

Latest picks build in the ledger: `20261019T132711-9c2f083b-picks_build`, workflow run `39256463413`, SHA `7ed725e3ffc6754700b8c4425f25b373498900d7`, recorded 13:27 UTC / 15:27 SAST.

| Observation | Count | Meaning |
|---|---:|---|
| Source fixture-key union (`pipeline_n_up`) | 858 | Raw source keys, not 858 verified bettable games |
| ML-scored fixture records | 42 | A narrower, reconciled scoring universe |
| ML-scored fixtures materialized into an operational candidate | 1 | Bursaspor–Pendikspor |
| ML-scored fixtures not materialized | 41 | 97.6% of this scoring universe |
| Current merged daily pick archive | 2 unique fixtures | Bursaspor plus the earlier retained Mes Shahr-e Babak–Persepolis pick |
| Frozen main slip | 2 legs / 1 acca | Both archived games appear on the slip |

The 858→42 comparison is **not** a measured count of 816 probability rejections. The ML branch requires at least two usable source probability vectors plus eligible legacy-source input. Fixtures outside that ML branch can still qualify for consensus; Mes Shahr-e Babak is an example of a retained different-time candidate. The latest rebuild, the merged archive and the frozen slip are different populations.

The existing shadow report counts three candidate identities because Bursaspor's two-voter and three-voter rules have different IDs across reruns; these are **not three different games**. One older candidate version not being ticketed must not be mistaken for a rejected additional fixture.

## Verified upstream restrictions

From `scripts/picks_today.py:eval_1x2()` and the actual `load_thresholds()` result:

1. **At least two sources with complete 1X2 probabilities.** One source, a tip without probabilities, or unmatched fixture names cannot pass this gate.
2. **All participating usable voters must agree on the 1X2 outcome.** The gate uses `len(set(sels)) > 1` to suppress consensus emission. A strong majority does not suffice if another participating voter disagrees.
3. **Consensus average thresholds remain 70% for two voters and 65% for three or more.** Cups add five percentage points; friendlies add ten and require at least three voters. These are consensus probabilities, not the separate ML score or enhancement cohort rates.
4. **No certified ML-meta or ML-fade emission rules are active in the current registry.** A serving model exists and still scores fixtures for research, but both emission rule lists are empty. Scoring a match does not make it a selectable ML pick. It would be incorrect to say all 42 simply failed a 65% ML cutoff.
5. **No direct certified OU or BTTS rule is returned by the loader.** Therefore those binary main-lane generators do not independently rescue fixtures rejected by the 1X2 parent path. Their markets may still compete in the enhancement overlay—but only after a parent reaches it.

There are ten certified consensus registry rows, but the live threshold loader chooses one representative rule per voter-count slot, rather than independently evaluating every qualified rule. The currently selected generic rules produce the 70/65 thresholds above. Other certified qualified variants are not evidence that their predicate, current electorate and pricing are interchangeable; do not lower thresholds or apply historic certification to replacement voters without a separate comparison.

## Pricing problems also exist, but do not explain all 41 rejections

Among the 42 scored fixtures, **18 have no captured shadow price** and **24 have a captured Zulubet price** with the audit-only `scored_as_upcoming_unproven` kickoff basis. Those 24 are not automatically executable named-book quotes and cannot be promoted just because a numerical price exists.

Today's retained source/capture receipts show:

- **OddsPapi:** latest capture stopped on the daily budget (`remaining_today=0`); no new fixtures attempted in that capture.
- **TheOddsAPI:** no pre-build rows; Iran league unsupported for Mes Shahr-e Babak–Persepolis; Bursaspor retry suppressed by a six-hour failed-attempt cooldown.
- **Bzzoiro odds:** `http_403_plan_or_auth`.
- **Sportytrader:** Cloudflare/challenge failure.
- **Betminer:** HTTP 404 endpoint-contract failure.
- **Futbolpronosticos:** HTTP 500.
- **BetExplorer/Pinnacle-derived local evidence:** did price the existing parent picks, so these feed failures did not prevent the two-leg main card.

Large monthly price-row mismatch totals in source-health diagnostics are observations across other fixtures/markets, **not counts of today's discarded games**. Similarly, joins run against already emitted picks; a quote with `no_pick_for_fixture` does not prove a sound pick was discarded solely for lack of pricing.

## VETO labels are not blocking these two games

Both archived games have bucket `SKIPPED_VETO`, yet both appear on today's frozen main slip and enhancement slip. `scripts/auto_tickets.py:BUCKETS` includes `SKIPPED_VETO`.

The explicit enhancement code comment states that **`[SKIPPED_VETO parent]` is informational and those legs ARE staked by the ticket system**. It does not mean paper, withheld or excluded. This corrects the implication in the earlier replay follow-up that this tag represented a parent-veto placement block. The lack of independently verified bookmaker receipts remains a separate limitation; the tag itself is not evidence of non-placement.

Only one main acca is printed because two unique games are available. The three-acca cap is not discarding a large pool of additional games in this snapshot.

## The merged policy is not yet evidenced by these slips

These records and the slip freezes predate PR #100's merge at **16:14:42 UTC / 18:14:42 SAST**. The morning/final candidate logs still contain legacy exclusions such as Under 2.5 at 34.71% or Under 3.5 at 52.07% being below the old market-specific threshold, and no generated match Under 4.5 candidate.

The workflow started at 16:00 UTC also reports pre-merge HEAD `8abefc45...`. A run already in progress does not pick up a later merge. These archived decisions cannot establish whether the newly enabled default has run successfully, nor whether it changes selection. No new paid run was triggered for this diagnosis.

Across the two archived parent rows, logs contain 31 legacy below-line-threshold exclusions, 26 missing-cohort-rate exclusions, seven unpriced candidates, four below-price-floor candidates, six eligible-but-beaten candidates and two recommendations. These are **market-candidate occurrences on two games**, not 74 discarded games. They are pre-merge observations, not a regression of the newly enabled rule.

## What the evidence cannot yet explain exactly

All 41 non-materialized scored fixtures have the same persisted label: **`no_candidate_emitted`**. Individual voter probabilities and the exact first failed production gate are not retained with those fixture events. We therefore cannot honestly split the 41 into exact disagreement, probability-threshold or other operational-rejection counts from this snapshot alone. GitHub log download was unavailable from this environment; no fresh live fetch was substituted for the historical run.

**Next targeted improvement:** record the first failed gate and relevant source/threshold inputs on the existing scored-fixture events—no new shadow system. Then compare the fixtures excluded before enhancement evaluation using contemporaneous cohort/quote evidence. That would distinguish genuinely unsupported games from goal-market opportunities being excluded merely because their 1X2 parent failed. Neither this count nor a high model score justifies bypassing price, identity or pre-kickoff safety checks.

## Evidence and reproduction

[Compact machine receipt and input hashes](game-attrition-2026-10-19.json).

Existing read-only report (do not pass `--write-settlement`):

```bash
PYTHONPATH=src python scripts/scored_candidate_shadow_report.py \
  --date 2026-10-19 --json .cache/discard-shadow-report.json
```

In this checkout the report falls back to `settled_results.json` because the full grader's optional `dotenv` dependency is absent; this does not affect the recorded funnel counts. No same-day winning/losing assessment was made.

## Implementation follow-up

The requested [detailed logging is now implemented](../GAME-ATTRITION-LOGGING.md)
in the existing ledger/report, with a full source-key decision view and actual
pre-match/bucket reasons. This diagnosis and its machine receipt remain a
**pre-instrumentation historical snapshot**; their source hashes are not updated
to pretend the newly added fields existed in the earlier run. The new feature
does not reconstruct the missing reasons for the 41 historical records.

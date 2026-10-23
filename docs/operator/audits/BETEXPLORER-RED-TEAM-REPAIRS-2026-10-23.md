# BetExplorer red-team repairs — 2026-10-23

## Scope and baseline

Repair baseline: `eefff49353f896204d28385afcd3f4359af2af21` (merged audit PR #142). The original findings remain in `PR-141-RED-TEAM-2026-10-23.md`; this addendum does not rewrite their history or claim an independent review has happened.

This is a bounded repair of the existing pricing/admission/selection path. No new source, capture workflow, strategy, cohort registry, staking rule, or eligibility relaxation was added. Z.ai was not contacted; the companion independent-review prompt pins the repair commit for a separate reviewer.

## Repairs

### F1 — decision-time schedule knowledge

- Retain the already-read BetExplorer candidates and independent schedule witnesses internally, then materialize a decision-bound source view using `min(actual aware decision, daily cutoff)` **before** schedule conflict resolution.
- Cache views per bound, without changing the base index or losing other donors. Early/late calls in either order are covered.
- Keep the existing receipt, capture, live-age, kickoff, and strict witness-observation-boundary checks. A future-only witness cannot make an earlier quote executable. The daily admission policy remains intact.
- Context and datetime-keyed view caches are internal pricing-index state, not publication payloads; regression coverage serializes the actual candidate/event-note output instead.

### F2 — retain executable bookmaker alternatives

- Retain each supported BetExplorer quote and its own row-bound receipt instead of discarding all but the display winner. Preserve the established site-best/highest display preference.
- Attach only validated, latest-per-book alternatives and carry them through real candidate generation, `event_notes`, JSON serialization, and pricing-only live variants into the existing complete-ticket competition.
- Variant fields cannot replace fixture or measured-cohort identity. Each variant passes the same existing live execution gates, including price, receipt, source, bookmaker, clock, and market checks.
- Keep a market eligible for consideration when a validated alternative clears the **unchanged** minimum leg odds even if its display-preferred quote does not. The low-priced display quote remains blocked at execution.
- Clear stale alternatives on reattachment and clear selected alternatives when publication quarantines an unproven cohort. Malformed alternative containers do not crash live leg construction.
- Cover all 11 supported selections: match O/U 1.5, 2.5, 3.5, 4.5; BTTS Yes/No; and side-correct DC. Unsupported team totals are not fabricated from match totals, AH, or DNB.

### F3 — isolate only demonstrably irrelevant corrupt history

- Scope canonical calendar-month archives to the fixture's page date (declared-date fallback), including adjacent dates for month boundaries. Unknown dates or noncanonical archive names retain conservative scanning.
- Calendar-invalid filenames are not treated as proof of irrelevance.
- Relevant unreadable archives produce explicit error receipts and `schedule_archive_unavailable`; BetExplorer admission fails closed because unreadable data might conceal a real conflict. Other price donors are preserved.
- Stage each gzip file's witnesses transactionally. Truncation, invalid deflate data, decoding/parsing/read failures do not publish a valid-looking prefix.
- This scope relies on the existing date-partitioned capture contract, not an assertion that arbitrary externally misfiled records are trustworthy.

## Reproduction and validation

- Isolated baseline replay of the original regressions: **5 failed, 6 passed**. On repaired code, all five are ordinary passing tests; no xfails remain in that file. The original `all(fire)` assertion is preserved.
- Focused eight-file suite: **409 passed**.
- Final full suite: **4,158 passed, 1 skipped in 171.44 seconds**.
- The skip is `tests/test_fixture_decision_logging.py:207`: immutable baseline commit unavailable in this shallow checkout. It is not a newly accepted functional failure.
- Offline archived replay, with socket connections prohibited: baseline versus repaired code over the retained 2026-10-22/23 picks, **3,045 market cells, 381 priced, zero primary-price/book/source/time/kickoff changes**. **14 cells** now retain alternative bookmaker quotes.
- The archived replay preceded publication-quarantine cleanup and calendar-invalid-filename hardening; neither changes normal primary quote choice. It does not replay live ticket selection.
- BetExplorer `admitted_cells` counts individual retained bookmaker cells now, so the archived Oct 22 count increased **94 → 186**; this is not 92 newly covered fixtures or executable bets. Oct 23 remains **0**, with 13 missing-independent-witness rejections in these retained inputs.
- Protected manifest: 950 tracked paths unchanged; the only two changed paths among the 952-entry pre-repair manifest are the intended `scripts/picks_today.py` and `scripts/auto_tickets.py`. Localdata, frozen/financial history, and workflows are unchanged.
- AST comparison of those scripts: only `compute_dynamic_enhancement` and `enhancement_legs` function bodies changed, plus the selected-publication field list. No staking/rounding/ticket-planning function changed.
- `git diff --check` passes.

Commands:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q -rs
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_betexplorer_repair_contract.py \
  tests/test_betexplorer_red_team_2026_10_23.py \
  tests/test_betexplorer_board_admission.py \
  tests/test_secondary_quote_admission.py \
  tests/test_enh_pricing.py \
  tests/test_audit_market_depth_replay.py \
  tests/test_kickoff_corroboration.py \
  tests/test_enh_selection_equality.py
```

The new contract tests exercise real candidate generation → event notes → JSON → live legs → two-leg same-book competition, including disjoint better display books and a display quote below the minimum. Additional negative tests cover alternate tampering, future evidence, relevant corruption, truncated archives, malformed names/containers, stale alternatives, and publication quarantine.

## Remaining limitations and operational boundary

Synthetic execution tests and archived price replay establish bounded regression evidence, **not production coverage gains or a profitable/live ticket**. No workflow was dispatched, no frozen ticket or financial history was changed, and no new merge was performed. A separate reviewer must inspect the actual code, run their own checks, and distinguish unavailable data from a passed check. Receipt hashes provide consistency binding, not cryptographic source authentication.

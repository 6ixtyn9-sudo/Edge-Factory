# Realized stats and broader cohort selection — 19 October 2026

## Current disposition: broader cohort competition ON by default

**Operator authorization:** “the off switch should be on, let the best cohort win … i want broader selection with evidence.” This supersedes this session's earlier default-off containment recommendation. It is an explicit eligibility-policy decision, **not a claim of statistically established ROI improvement**.

`compute_dynamic_enhancement()` now uses common eligibility for all markets for which the all-outcome cohort supplies a rate:

- Existing cohort minimum sample size: **100** (unchanged).
- Existing shared rate band: **25–90%, inclusive** (unchanged).
- Existing captured-price minimum: **1.30** (unchanged).
- Rank eligible markets by **cohort hit rate**, then higher price on a tie (unchanged).
- Include complementary unders, including match Under 4.5.
- No EV gate, no market-specific 75% replacement minimum, and no change to main-lane selection, stakes, caps, pairing, freeze or settlement rules.

For cohort-backed markets, the legacy `LINE_THRESHOLDS` no longer prevent entry to the existing common competition. A 75% or 80% Under 2.5 can now win if priced at least 1.30 and no eligible competitor has a higher rate (or wins a price tie). This is eligibility, not a guarantee of recommendation, profit or ticket inclusion.

### Switch and rollback

- Unset `EDGE_FACTORY_ENH_COHORT_PARITY`: **ON**.
- `EDGE_FACTORY_ENH_COHORT_PARITY=1`: **ON**.
- `EDGE_FACTORY_ENH_COHORT_PARITY=0`: explicit rollback to legacy market filters and original generator universe.
- Other explicit values do not enable parity; use exactly `1` or `0`.
- Without a usable cohort, the model-only path retains its original filters regardless of the switch.

The code default makes the existing workflow pick this up after deployment without a workflow edit. At validation time, before PR publication, no service had been dispatched, no branch pushed/merged, no frozen pick/slip regenerated, and no bet placed. Existing environment overrides must not pin the switch to `0` if broad eligibility is wanted. `.env.example` documents `1`.

## Display remains distinct from selection

New `statistical_comment` reports show paired match overs/unders at 1.5/2.5/3.5/4.5, paired home/away totals at 0.5/1.5/2.5/3.5, and both BTTS outcomes. This display sample remains **winner-only**, and is explicitly labelled descriptive history, not pre-match probability. Selection uses the separate **all-outcome** cohort. Frozen historical reports are not rewritten.

## Evidence, and what has not been established

Re-running the existing retained full-pool comparison on 14–18 October still gives:

- **80** retained cohort snapshots; **19** with strict captured quotes.
- **48** priced/in-band candidate occurrences; **22** additional candidates across **17** fixtures.
- Those additions: 17 U2.5, 3 U3.5, 2 U4.5.
- **All 22** lose to a strictly higher-rate incumbent; **zero changed fixture recommendations** and identical counterfactual cards.
- This comparison demonstrates no ROI uplift and cannot validate an optimal 75% or 85% minimum. Historical U2.5 rates in this retained sample did not reach either number.

Tests do establish behavior: a coherent 75% U2.5 at 1.40 now displaces a 60% BTTS Yes at 1.80; a stronger eligible competitor still wins; rate ties use price; out-of-band and sub-1.30 candidates are still rejected. These are synthetic correctness tests, not observed profitable bets. The 100 coherent-score/random-price cases now exercise the unset/default-on path.

Machine receipts: [full-pool audit](audits/enh-under-redteam-2026-10-19.json), [market contention](audits/enh-market-competition-2026-10-19.json), and [validation](audits/enh-under-validation-2026-10-19.json). Earlier readable audit documents retain the old decision with a supersession notice; their no-uplift finding remains valid. Refreshed numerical receipts retain the same historical outcome population and record current code/input hashes.

## Existing replay: bounded correction, not another framework

The previous claim that the enhancement replay's **live** floor arm needed conversion from old floors was wrong: `_root_floors()` already uses `MIN_LEG_ODDS=1.30`. A new test compares its firing predicate to the actual lane across all mapped markets and boundary prices. Derived slice floors remain an explicitly different research arm; they were not made active.

The confirmed bug in `enh_day_growth()` is fixed: simultaneous tickets use **`1 + sum(ticket net P&L / opening bank)`**, not a product of per-ticket factors. Production ticket sizing and settlement code are unchanged. Six two-ticket tests independently sum cash returns for wins, mixed outcomes and losses under equal/weighted sizing.

The registry replay is selected, priced history, not the complete rejected-candidate universe. Its output now states that it cannot establish uplift from broader cohort eligibility. Use the existing candidate logs, captured quotes, archived picks, frozen tickets and actual lane performance to evaluate the enabled policy as outcomes accrue; do not add another shadow lane or quietly tune market cutoffs from five retrospective days.

Reproduce:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python tools/verify_enh_default_parity.py
PYTHONPATH=src .venv/bin/python scripts/audit_enh_under_parity.py --out .cache/enh_audit.json
PYTHONPATH=src .venv/bin/python scripts/replay_harness.py --enhancements
```

The verifier's historical filename is retained for compatibility; it now explicitly sets env `0` and verifies **rollback parity**, not default parity. No bankroll/history, provider budgets, lane-enable flag or live workflow was changed.

## Final validation of the authorized enablement

- Full suite: **3,259 passed in 147.25s**.
- Post-mutation focused regression (including documentation links): **225 passed in 4.86s**.
- Explicit legacy rollback: **200 seeded outputs/logs identical** to the immutable baseline.
- Two deliberate defects caught and restored: disabling default cohort parity failed its cross-market 75% test; restoring multiplicative ticket growth failed all six cash-accounting cases. Source hashes are recorded in the validation receipt.

Deployment is separate from PR publication: pushing the branch and opening a PR do not merge it or dispatch the running bot. The enabled default takes effect when the change is deployed, unless an environment override explicitly disables it.

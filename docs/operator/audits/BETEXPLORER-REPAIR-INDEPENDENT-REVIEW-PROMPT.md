# Independent Z.ai review prompt — BetExplorer repairs

Copy everything below into the independent reviewer. This is a requested review, **not a record of a review already performed**.

---

Independently red-team the BetExplorer repairs in `6ixtyn9-sudo/Edge-Factory`.

**Exact repair target:** `f4da8d8320adc6a343e071d6d359b588ff74c839`
**Comparison baseline:** `eefff49353f896204d28385afcd3f4359af2af21` (merged audit PR #142).

Inspect the exact target, not just the current main branch or PR #141. Verify both SHAs locally and state what you actually inspected. Use an isolated read-only checkout/archive if needed; do not modify an active working branch. Do not merge, push, dispatch workflows, buy/capture odds, change frozen tickets or financial history, or relax any gate. Report findings first; do not silently repair them.

Read the original audit at `docs/operator/audits/PR-141-RED-TEAM-2026-10-23.md` and the repair addendum at `docs/operator/audits/BETEXPLORER-RED-TEAM-REPAIRS-2026-10-23.md`. Treat the implementation author's claims as hypotheses, not proof. Review the full baseline-to-target diff and relevant existing code, especially:

- `src/edgefactory/enh_pricing.py`
- `src/edgefactory/kickoff_corroboration.py`
- `scripts/picks_today.py`
- `scripts/auto_tickets.py`
- `tests/test_betexplorer_red_team_2026_10_23.py`
- `tests/test_betexplorer_repair_contract.py`

## Try to break these contracts

1. **Decision-time knowledge:** schedule witnesses must be filtered at the actual aware decision before conflict resolution, not merely at the later daily cutoff. Try later conflicting kickoffs, later agreeing observations, future-only evidence, exact observation boundaries, and early/late calls in both orders against the same cached index. Preserve the original receipt/live-age/capture/kickoff checks and other donors. Check cache isolation, error handling, publication/JSON safety, and the treatment of absent/invalid decision clocks.
2. **Executable alternatives:** use two fixtures with individually better but disjoint display books and a valid common-book offer. Exercise actual `compute_dynamic_enhancement` → `event_notes` → JSON → `enhancement_legs(execution_safe=True)` → existing same-book two-leg ticket competition. Include a display quote below the unchanged minimum with a qualifying common-book alternate. Test all match O/U 1.5–4.5, BTTS Yes/No, both DC side mappings and reversed fixtures. Missing team-total quotes must remain missing; match totals/AH/DNB must not manufacture them. Do not accept an attachment-only test as end-to-end proof.
3. **No variant bypass:** tamper with alternate price, bookmaker, provenance, row binding/site-best metadata, timestamps, kickoff, rejection/priced flags, source, market, fixture and cohort identity. Test malformed containers, latest-per-book selection, stale alternatives on reattachment, and publication quarantine. Each executable variant must pass the same existing live gates; no arbitrary alternate data may overwrite fixture/cohort fields.
4. **Archive isolation, not silent conflict loss:** unrelated canonical months may be skipped only under the existing capture partition contract. Relevant corrupt/unreadable files must block BetExplorer admission with an explicit diagnostic. Try month boundaries, unknown page dates, noncanonical/invalid-calendar filenames, partially readable/truncated gzip, invalid deflate data, and a hidden conflicting record. No valid prefix from a failed file may escape. Verify other donors still work and inspect the capture writer assumptions behind calendar scoping.
5. **Scope/invariants:** inspect complete-ticket competition rather than cherry-picking a good quote. Verify no staking, rounding, frozen-ticket, financial-history, workflow/capture-budget, eligibility-threshold, cohort-measurement or source-identity regression. Ensure no new strategy/registry/pipeline or external collection expansion was introduced.

## Execute independent checks

Run the focused suite and full suite from the exact target (using your environment's installed dependencies):

```bash
PYTHONPATH=src python -m pytest -q \
  tests/test_betexplorer_repair_contract.py \
  tests/test_betexplorer_red_team_2026_10_23.py \
  tests/test_betexplorer_board_admission.py \
  tests/test_secondary_quote_admission.py \
  tests/test_enh_pricing.py \
  tests/test_audit_market_depth_replay.py \
  tests/test_kickoff_corroboration.py \
  tests/test_enh_selection_equality.py
PYTHONPATH=src python -m pytest -q -rs
git diff --check eefff49353f896204d28385afcd3f4359af2af21 f4da8d8320adc6a343e071d6d359b588ff74c839
```

Where possible, independently reproduce the original five failures on the baseline with `--runxfail`, then show ordinary passes on the target without weakening assertions. Add adversarial probes in scratch space if useful. Do not treat an unexecuted command or an unavailable baseline as passed. Distinguish actual regressions from test harness mistakes, but do not modify expectations merely to get green output.

The author's archived comparison covered 3,045 price cells: 381 priced, zero primary-price changes, 14 cells retaining alternatives. The BetExplorer admitted-cell count increased because more books are retained; it is not a new-fixture/bet count. Oct 23 archived BetExplorer admission remained zero. If independently replaying retained localdata, prohibit network access and do not modify it. Separate receipt/price replay, synthetic executable-ticket evidence, and runner-observed production coverage. Tests are not proof of live coverage or profitability.

## Return

- Exact inspected SHA and commands actually run, including failures/skips and environment limits.
- Verdict for each original finding: fixed, partial, or not fixed, with evidence.
- New findings ordered by severity, each with file/line, mechanism, smallest reproduction, consequence, and bounded repair recommendation.
- Whether any fail-closed or financial invariant weakened, and whether tests themselves hide/soften a failure.
- A separate production-evidence statement: what was observed versus what remains unverified.

If you find no blocker, say **“no blocker found within the inspected scope”**, not “production proven” or an unconditional safety claim.

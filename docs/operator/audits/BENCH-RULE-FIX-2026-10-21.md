# Bench rule: priced-sample floor — 2026-10-21

**Scope:** `edgefactory.assay.should_bench` / `scripts/decay_monitor.py` auto-bench.
**Checkout:** `7e8000bb89000afba4510ccd8fe8486b07718186` (`main`, PR #116 merge),
working branch `arena/d16e518f-edge-factory`.
**Mode:** code + regression tests only. No bank, historical slate, registry or
certificate was rewritten. `localdata/` is byte-identical after the full suite
(848 tracked files; the one new path, `localdata/theoddsapi_usage.lock`, is an
empty gitignored lock created by a pre-existing test).
**Tests:** `3625 passed, 1 skipped in 175.59 s` (was `3614 passed, 1 skipped`).

---

## 1. The defect

`should_bench` benched on **any** non-null negative `recent_roi`, with no sample
gate and no threshold:

```python
if recent_roi is not None and recent_roi < 0:   # any negative, any n
    return True
```

Two documents state a different rule — `decay_monitor.py`'s own docstring
("recent ROI < -5% with n>=30") and `HANDOVER.md` ("DEAD/DECAYING, or < -5% on
n>=30", twice). Neither was implemented. A third `HANDOVER.md` pass
deliberately records the ungated behaviour ("benches on ANY negative recent
ROI … the ROI bench is not gated by it").

Observed in run `39552043539` (2026-10-21, `81b8a2c`):

```
pfc_5954379f3a12700edcfd8387   baseline 443 @ 70.0% LB .655
                               recent    9 @ 66.7% LB .354  ROI -5.3%
                               WATCH -> BENCHED
```

`decay_verdict` had already declined to call this DEAD/DECAYING — 9 is below
`min_decay_n=15` — and `decay_monitor` separately downgrades HEALTHY→WATCH when
`n_priced < 30`. `should_bench` then discarded both judgements and benched on
nine matches.

Direction matters: benching **removes** bets, so this was never an exposure
risk. It is an evidence risk — a certified contract with a 443-match baseline
was retired by a 9-leg window, and the registry recorded no reason.

## 2. The fix

`bench_decision(report, recent_roi, *, n_priced, min_priced_n, min_roi)` is now
the single rule, returning `(bench, reason)`; `should_bench` is the boolean
view. `scripts/decay_monitor.py` passes `n_priced=rec["n_priced"]` and
`min_priced_n=GATES.min_recent_n`, so the ROI gate is measured against the
**priced** denominator that actually produced the ROI — not the settled count
(a window of 100 settles with 9 prices is a 9-leg ROI).

| condition | decision | reason |
|---|---|---|
| DEAD / DECAYING | bench | `verdict_dead` / `verdict_decaying` |
| ROI negative, `n_priced >= 30` | bench | `recent_roi` |
| ROI negative, `n_priced < 30` | **no bench** | `recent_roi_n_below_floor` |
| ROI >= 0 | no bench | `recent_roi_non_negative` |
| ROI NaN/inf | no bench | `recent_roi_not_finite` |
| no ROI measured | no bench | `none` |

An ROI without `n_priced`, or with `n_priced <= 0`, now raises `ValueError`:
an ROI whose denominator is unknown is not evidence, and guessing one is the
defect this signature exists to prevent. `recent_stats` reports a non-finite
pnl as `roi: null` (unavailable, never a number).

The threshold stays at **`< 0`**, not the documented `< -5%`. At `n_priced >= 30`
every negative ROI already benches today, so keeping `< 0` preserves current
strictness exactly; adopting `-5%` would have quietly *loosened* the gate for
every adequately-sampled edge, which no one approved. The two `HANDOVER.md`
runbook lines were corrected to describe what the code enforces.

## 3. Two adjacent defects found while fixing

1. **A negative ROI relabelled DEAD as DECAYING.** The ROI branch assigned
   `v = "DECAYING"` outright, overwriting a structural `DEAD` from the Wilson
   test (confirmed: baseline 310/443 LB .6555 vs recent 0/30 UB .1135 → DEAD,
   then rewritten to DECAYING). Verdicts now rank by severity and ROI evidence
   can only *worsen* a verdict. No selection impact — `picks_today` treats both
   as adverse — but the registry, `sync_supabase` and the dashboard showed the
   milder state.
2. **NaN ROI escaped every gate.** `NaN < -0.03` and `NaN < 0` are both False,
   so an unreadable ROI left the verdict `HEALTHY`. Unmeasured is now never
   HEALTHY (WATCH), mirroring the existing `recent_n == 0` rule.

## 4. Verification

**Unit (n=3/9/29/30/31, zero, NaN/inf, missing denominator):**
`tests/test_assay.py::test_thin_priced_sample_cannot_bench_an_edge`,
`test_bench_fires_at_the_priced_floor_and_only_on_a_loss`,
`test_roi_bench_refuses_to_run_without_its_priced_denominator`,
`test_non_finite_roi_is_unreadable_not_profitable`,
`test_bench_reason_names_the_evidence_it_fired_on`,
`test_roi_evidence_can_only_worsen_a_verdict`, plus a drift guard
`BENCH_MIN_PRICED_N == GATES.min_recent_n`.

**End-to-end through `decay_monitor.main()` on a temp warehouse**, asserting the
registry record and the printed line:
- 9 priced losses → status stays `certified`, `bench_reason
  recent_roi_n_below_floor`, line reads `[roi n=9<30: not benched]`,
  summary `1 negative-ROI decision(s) held`;
- 30 priced losses → `benched`, `verdict_dead`;
- 20 settled at `n_priced=20` → still `benched` on `verdict_dead`, i.e. the
  floor gates the ROI branch only and does not disable the circuit breaker.

**Archive recomputation on the committed registry** (recorded `decay.recent`
from run `39524693030`; this is stored evidence, not a live re-run — the
checkout has no `warehouse.duckdb`):

| | count |
|---|---|
| decay rows in `edges_consensus.json` | 68 |
| decisions changed by the floor | **14** |
| …of those, already `benched` | 14 |
| decisions changed at `n_priced >= 30` | 0 |

All 14 were benched on 2–13 priced legs (ROI −3.0% to −47.0%). Nothing is
un-benched by this change: no code path rewrites `status` on load, and the
committed registry still has `pfc_5954379f3a12700edcfd8387` `benched`. The
effect lands on the **next** `mine_consensus` re-certification, which rebuilds
status from full walk-forward history as designed.

## 5. Not claimed

- No live warehouse run: `localdata/warehouse.duckdb` is absent from the
  checkout, so the end-to-end runs above are on fixtures and the archive
  recomputation is on stored decay records.
- Python deployment on `main` is unverified; a green local suite is not a
  deployed pipeline.
- Run `39552043539` started before this change, so its registry write used the
  old rule. This fix applies from the next scheduled run.

# Post-Forebet production receipt — run 39350936425

Recorded 20 October 2026. Evidence: operator-supplied production logs and successful GitHub run API lookup. The full research JSON has **not** been inspected: downloading `EdgeFactory-Reports` reached a blocked artifact-storage redirect. Do not infer passing rule identities from the aggregate counts below.

Run: https://github.com/6ixtyn9-sudo/Edge-Factory/actions/runs/39350936425

## Execution, not activation

- `workflow_dispatch`, mode `auto`, code `9a409c3` on main; completed successfully. Unlike the earlier `remine_only` run, this executed operational steps, published cache/state and uploaded artifacts.
- Production regression: **3,327 passed, 1 skipped**, 179.30 seconds. The same code had four SoccerVista test failures during the earlier run across UTC midnight. This supports the test-clock diagnosis; it does not mean a deterministic clock fix was already deployed.
- Mining window: training `2026-06-13 <= date < 2026-09-22`; validation `2026-09-22 <= date < 2026-10-20`.
- **73,476 tested rules, 39 statistical passes**, research only. These are not 39 distinct, approved or execution-safe live edges. Overlapping source subsets/thresholds share evidence; validation was searched, not untouched forward evidence.

| Market | Tested rules |
| --- | ---: |
| FT 1X2 | 72,280 |
| HT 1X2 | 13 |
| FT O/U 2.5 | 624 |
| BTTS | 221 |
| FT O/U 1.5 | 117 |
| FT O/U 3.5 | 221 |
| HT O/U 1.5, HT O/U 2.5, FT O/U 4.5 | 0 |

All registered markets were considered; coverage is not uniform. Zero tests are not evidence of unprofitability. No market or threshold can be declared the winner from counts alone. The earlier run reported 40 passes over the same number of tests; the exact changed rule and reason require both reports, not a guess from aggregate source counts.

The new miner excludes Forebet, but the old operational registry still feeds decay, assay and selection. The miner does not refresh legacy non-ML live contracts. The full `auto` run can nevertheless modify that registry through existing decay/operational steps: do not describe the whole run as leaving live state untouched. Completing the post-Forebet serving transition remains outstanding.

## Operational findings from the supplied logs — not fixed here

- Generation: **829 candidate keys = 773 insufficient probability sources + 38 below threshold + 12 disagreements + 6 emitted**; one missing-kickoff row was removed, leaving five. The 829 keys must not automatically be described as 829 same-day fixtures. Categorical tips do not become calibrated probabilities merely because more raw predictions are retained.
- All five final rows were `SKIPPED_VETO`; the shadow message explicitly said they were not pushed as bets. El Geish/Pyramids was associated with `thai premier league`, a context/identity discrepancy requiring investigation before interpreting the veto. These logs do not authorize bypassing vetoes.
- OddsPAPI reported three overlap fixtures and 6,223 rows but zero final-card matches. The quoted Costa Rica/Mexico fixtures differed from the final five. Candidate-pass and final-card identities/timing must be compared; this is not proof that incorrect prices attached to picks. The final zero join is an important distinction.
- Supabase upserted ten registry entries, but all five pick rows lacked required edge/event IDs; deletion of existing same-date picks was refused. Workflow green is not successful publication of those five picks.
- Enhancement generation still produced two drafts using vetoed parents, with reported combined exposure of 25% of free bank / 17.9% of capital. They were not yet frozen. Their separate eligibility/exposure path needs an explicit audit; this is not a reason to reverse the operator's broader-cohort-competition decision.
- Current run does not establish that 75% is an optimal replacement probability floor. Price provenance, samples, shared fixtures, chronology and forward validation still apply across all competing markets.

## Narrow follow-up changes, local branch only

1. SoccerVista tests use a fixed date for both fixture requests and adapter clock, avoiding collection-before-midnight/execution-after-midnight disagreement. A regression confirms yesterday remains out of coverage after the clock advances and no homepage request is made. The production today-only guard is unchanged.
2. Existing miner table preference is canonical source, then raw captures, then settled-only fallback. Previously PredictZ selected its 1,944-row settled subset despite 2,706 raw captures in the production warehouse. The new regression supplies raw predictions without scores, a legacy settled subset, and independent BetExplorer results; both raw predictions are evaluated. This does **not** establish that all 2,706 production captures will settle or pass era/conflict gates.

Validation after both changes:

- `PYTHONPATH=src .venv/bin/python -m pytest tests/test_soccervista.py tests/test_post_forebet_remine.py -q`: **44 passed**, 3.51 seconds.
- `PYTHONPATH=src .venv/bin/python -m pytest -q`: **3,329 passed, 1 skipped**, 141.16 seconds.
- No provider calls, workflow dispatch, threshold changes, certification, activation or frozen-history changes were made for this follow-up.

## Evidence still needed

Upload `edges_consensus_research.json` from this run's `EdgeFactory-Reports` artifact to inspect the 39 passes: exact electorates, strategies, thresholds, train/validation and priced counts, ROI, Wilson bounds and holds. The corresponding earlier report is needed only to identify the precise 40-to-39 delta. Do not request another full production run just to recover these existing files.

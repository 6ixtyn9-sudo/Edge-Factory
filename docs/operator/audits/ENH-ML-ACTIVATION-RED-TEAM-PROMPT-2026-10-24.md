# Paste to Z.ai — red-team the ENH ML implementation

You are the independent adversarial engineer, not a rubber stamp. Inspect the actual implementation, run tests and try to break its live selection behavior. Return concrete defects and minimal fixes, not another general planning loop. Do not assume this change is profitable or production-validated.

## Repository and scope

- Repo: `6ixtyn9-sudo/Edge-Factory`.
- PR: https://github.com/6ixtyn9-sudo/Edge-Factory/pull/149
- Branch: `arena/76daeb2a-edge-factory`.
- Review the latest PR diff. The preceding live status repair is commit `f2d91ace13e9a223d51381086a85a4468caa06cc`; compare the subsequent ML implementation against that commit too.
- Read the latest HANDOVER entries and inspect primary inputs/source, not just this description. Do not switch the Arena branch or alter operational records.

The operator explicitly authorized live ML ENH changes and requested existing machinery/no extra scripts. The implementation is **experimental ML ordering of already-admissible ENH alternatives**, not replacement of the measured-cohort payout gate. It is enabled by default in code for new builds. It has NOT been demonstrated running on production data, merged or dispatched by Arena. Do not conflate configured, fitted, scored, selected, frozen and actually cash-placed.

## What was implemented

1. `src/edgefactory/consensus_contracts.py:enhancement_cohort`: optional `fit_ml` uses existing sklearn LogisticRegression (`C=1`, max_iter=1000, random_state=42). Target is a categorical observed FT home:away score pair, **not** elected 1X2 correctness. The sole feature is exact-parent selected-side confidence divided by 100. Training population is the existing all-outcome exact-contract/selection cohort, prior to the requested day; existing conflicts/status quarantines apply. Requires the existing N30 plus variable confidence and multiple score classes. No synthetic rows, missing-value defaults, Poisson prior or team/league memorization. Sorted training data, digest, coefficients/classes/window/range and model key are retained in the existing statistical profile. Fits reuse the existing build-scoped cache; returned nested parameters are copied.
2. `src/edgefactory/enh_registry.py:enhancement_ml_probability`: rechecks model digest, schema, contract/day/selection and confidence range; recomputes binary/multiclass logistic score weights. Each market uses the existing `check_enhancement_hit` predicate over one shared score distribution. No independent home/away goal assumption and no multiplication of marginal leg probabilities into joint acca success.
3. `scripts/picks_today.py`: live caller requests fitting by default; eligible notes/recommendation are sorted using the recomputed ML score when available, otherwise the measured cohort rate. Fit/unavailable status and per-note rank fields are retained. Board output labels the score **“ML rank … (experimental)”**, not a certified probability.
4. `scripts/auto_tickets.py`: recomputes each market's ML score from that parent's retained model; passes ranking metadata through the existing ENH pool and frozen-plan evidence carry. Existing `select_accas` uses ML ordering only for `enhancements=True`, default probability ranking, no rank caps, and the flag enabled. Complete pairs still compete within existing book/source and same-fixture rules. Main ordering is unchanged.
5. `EDGE_FACTORY_ENH_ML=0` disables fitting/inference/reordering and restores cohort-only selection. Unsupported fits/features preserve the cohort baseline. No new scripts, trainer service, feature store or registry.

## Known limits — attack these, do not hide them

- The production warehouse is absent in Arena's checkout. No production-data model was fitted there. The existing live builder must fit on its own warehouse after deployment. Verify actual data coverage on your side if available; do not fabricate it if unavailable.
- Date-exclusive results are **not** proof of original point-in-time feature capture or label-known-by chronology. Raw warehouse revisions, period ambiguity without status, and occurrence identity remain real weaknesses. Determine whether these make default-on live ranking unacceptable and provide the smallest supported remedy. Operator permission is not statistical validation.
- N30 is the existing cohort floor, not proof a multi-class model generalizes. There is no demonstrated held-out calibration, baseline uplift, ticket ROI or drawdown improvement. A learner fit on observed score classes cannot allocate mass to unobserved score classes; investigate consequences.
- Only parent confidence is a predictive feature. Determine whether it varies enough within operational contracts to produce useful inference. A `fitted` status need not imply a particular row was scored or an executable pair changed.
- Follow-up to Z.ai's review of `14e18d4`: mixed-scale numeric fallback was removed using the review's option (a). Valid ML-scored candidates form the first rank group, ordered by ML score; cohort-only candidates follow in baseline order. This is an explicit experimental preference for model coverage, not calibration equivalence or proven superiority. A zero ML score is valid and remains in the scored group. Attack this preference and its complete-pair consequences; no new admission threshold was added.
- Persisted model hashes provide integrity/reproducibility metadata, not cryptographic trust in input labels or training eligibility. Existing cohort fields are retained assertions too.
- Existing rolling audits still evaluate their original cohort fields; do not describe those metrics as validation of ML rank probabilities.

## Required adversarial checks

- **Activation is real:** exercise default configuration from live cohort fetch → dynamic candidate pricing → enhancement legs → pool → complete-pair selection → evidence carry. Prove a changed pair on non-tied ML inputs. Distinguish synthetic proof from actual production coverage. Check that missing warehouse, constant feature, one score class, sparse or failed fit reports unavailability rather than fake ML activity.
- **Causal training and identity:** inject same-day/future results, conflicting scores, duplicate captures, reordered donors, AET/PEN/disposition records, wrong-contract/selection data and missing confidence. Examine authenticated timing and historical rewrites; state what is not proved. Check cache separation across warehouse connections, days, policies, min_n and rollback mode.
- **Inference:** compare binary and multinomial probabilities against sklearn itself. Test malformed coefficients/classes, NaN/inf/bools, modified/resealed payloads, foreign models, out-of-range inputs, complement identities and totals monotonicity. Check that model substitution does not bypass source/quote gates.
- **Live economics unchanged:** N30, 60–90% measured-rate band, 1.30 minimum odds, source/book eligibility, original quote timing and Wilson-bound×price >0.8 remain mandatory. Prove high ML cannot rescue a rejected candidate. Keep two-leg accas, no same-fixture duplicate exposure, 25% free-bank cap, frozen/settled records and main untouched. Check price alternatives do not borrow another market's context.
- **Operational reliability:** benchmark fitting cost and cache reuse on the largest available slate; inspect artifact size and model-parameter duplication across parents. Test failed fits and dependencies without turning one failure into a whole-slate outage. Verify model key/score retained on the actually selected frozen legs, not merely the initially recommended note.
- **Rollback:** verify `EDGE_FACTORY_ENH_ML=0` restores cohort-only selection and cannot secretly revive retired model/Forebet priors. Do not recut existing tickets to test it.

## Reproduction

Use the repository's existing requirements and tests, no new verification scripts needed:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_enhancement_evidence_integrity.py -k enh_ml
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q
```

Original handoff at `14e18d4`: **4,320 passed, 1 skipped**, including 15 added ML regression cases. After Z.ai's review, rank-group separation and fit-error containment were added; the follow-up full suite is **4,330 passed, 1 skipped**. Tests are not production coverage or performance evidence. Add failing regressions to existing test files for any discovered defect; do not weaken expectations just to match the implementation.

## Return one compact engineering verdict

1. **PASS / PASS WITH LIMITS / BLOCK**, distinguishing implementation correctness, real activation coverage and economic validation.
2. P0/P1/P2 defects with file/function/line, executable reproduction, expected versus observed behavior and the smallest fix.
3. Checks actually executed, environment/data limitations and numbers independently reproduced. Label assumptions and unverified claims.
4. Whether the implementation preserves main, ENH admission/staking/freezes, and rollback semantics.
5. A specific merge/deploy recommendation. Do not merge, dispatch, train against production or change cash records yourself without operator authorization.

Please be willing to BLOCK default-on activation if the evidence or engineering warrants it. Do not relabel training fit as out-of-sample improvement, cohort probabilities as ML calibration, or a code flag as live deployment.

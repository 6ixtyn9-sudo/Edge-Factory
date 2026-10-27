# ENH ML: existing machinery/input inventory and connected implementation

## Scope and status

Operator requested that ENH ML use the machinery and inputs already available,
not another service, registry, data collector or training script. This change
extends the existing exact-contract score-distribution logistic learner and
its existing live/replay consumers. It changes future ENH ordering when a new
model is built. It does not change admission, Main, prices, floors, stakes,
settlement, frozen cards or historical records. Branch implementation is not a
claim that production has already trained/deployed it or that returns improve.

## Inventory

| Existing machinery/input | Previously used by ENH ML | Connected use / boundary |
|---|---|---|
| `consensus_contracts.enhancement_cohort` + sklearn regularized logistic regression | Yes, selected-side mean confidence alone | Same learner, exact-parent population, all score outcomes; now a multifeature score distribution (`enh_score_logit_v2`) |
| Full observed `p1/px/p2` vectors | Collapsed to parent selected-side mean | Normalized home/draw/away forecast means and source spreads; source units validated through existing signal parser |
| Observed `p_o15/p_o25/p_o35/p_o45/p_gg` forecasts | Not used as model inputs | Goal-curve/BTTS forecast means and source spreads; probabilities of Under and No derive from the same fitted score distribution, not separate/inconsistent classifiers |
| Other existing prediction sources on the exact fixture/parent market | Only certified recipe voters affected parent admission | Nonambiguous source predictions can provide ML context without replacing voters or changing the recipe; no Forebet observations |
| Observed `xg_home/xg_away` (e.g. existing Bzzoiro schema) | Not used | Observed xG means/spreads when available; not inferred from odds or manufactured as Poisson defaults. A dark feed remains missing |
| `form_intel.ResultsArchive`, `team_form`, `pair_history` | Not used | Last-10 home-team/away-team scoring and conceding averages, O1.5/O2.5/O3.5 and BTTS frequencies; corresponding H2H features. Existing minimum history: five team matches / three meetings |
| Existing cohort result adjudication | Used for labels/rates | Also supplies form history: only undisputed regulation FT pairs, with source-team/squad identity and strict per-fixture earlier-date filtering. Raw `load_archive` is deliberately not bypassed into live ML because it lacks these cohort quarantines |
| Existing post-Forebet serving path | Used for scalar confidence | Persists observed context with emitted picks; `fetch_match_cohort` attaches fixture-bound feature receipts independently of cached contract fits |
| Existing ENH recommendation, complete two-leg selector and replay harness | Used v1 ML scores | Continue calling the same pure scorer; now accept v2 retained coefficients/feature statistics and fixture receipts. No new selector or probability multiplication |
| Existing Phase-5 K feature builder / Main correctness classifier | Separate machinery | Reuse its recorded-training-mean + missing-flag discipline, not its unrelated target/retired Forebet electorate or certification claims |
| Existing executable prices, CLV, candidate shadow ledger, capture health | Admission/audit inputs | Remain pricing/admission/evaluation evidence, not unverified historical training features or an override of the cohort/quote gates |
| BetExplorer raw page blocks/table rows and unverified historical provider timestamps | Partial diagnostic inputs | Not blindly inserted: field timing/semantics and matching must be supportable in both fit and serve. No retrospective league-table reconstruction |

Forecast context uses the sources with an unambiguous observed vote on the
parent market for that exact fixture. It is not a claim to use every possible
feed field or to recover absent providers. A categorical-only vote supplies no
invented numeric forecast. No odds collection expansion or network fetch added.

## Fit/serve contract

- One builder gives training and live features identical meanings. Dates are
  strictly earlier than each fixture, not just earlier than the current build.
- New input columns need at least 30 measured training values and variation.
  The parent confidence remains mandatory; extra signals can now permit fitting
  even when parent confidence is constant. Entirely unseen/constant optional
  columns do not become fitted coefficients.
- Scaling and imputation use **recorded observed-training means and scales**.
  Receipts retain missing values as null. Missing flags enter the vector; a
  standardized zero means the measured training mean, not a made-up zero rate.
- `ml_feature_coverage` reports measured training counts, the retained model
  declares its feature columns/statistics, and `ml_imputed_features` identifies
  missing current observations. Source names are retained as context provenance,
  not a guarantee that every named source supplied every numeric field.
- Optional feature conflicts across duplicate captures are quarantined in both
  input orders without changing parent admission. Any explicitly late or invalid
  capture timing excludes that forecast context, including a late duplicate.
- Cached fits stay contract/day/selection/window scoped. Fixture-specific input
  receipts are attached to returned copies and bound to date, both teams and
  contract; they cannot leak from the first pick into the next pick.
- Optional input-generation failures retain descriptive cohort evidence and
  explicitly remove the unavailable ML fit from that returned profile.
- Existing model hash, contract/selection/day, confidence range and parameter
  checks remain. Historical v1 payloads retain their original interpretation.
- Existing `EDGE_FACTORY_ENH_ML=0` rollback still restores cohort-only ordering.

## Validation and limits

New synthetic probes establish that goal forecasts and prior-team form each
change scores at identical parent confidence; those scores change an actual
complete ENH pair. Additional probes cover live warehouse emission, retained
replay, both BTTS directions and match/team-total complements, missing inputs,
scaling, fixture binding, optional failure, duplicate/timing conflicts, result
quarantines, own-day/future exclusion and v1 compatibility. Existing tests cover
Main, admission, stake caps, frozen settlement and ML-off behavior.

**These are engineering controls, not profitability validation.** No production
warehouse is present in this checkout. No new production fit, complete real-data
feature census, chronological calibration/ROI comparison or demonstrated economic
uplift is claimed. Existing archives without prediction capture/label-known-by
receipts are not authenticated point-in-time history merely because fixture dates
are filtered. Late corrections can still affect reconstructed earlier histories;
that pre-existing evidence limitation is not declared solved by this work.

Production will fit v2 only after this code is merged and a new build executes.
Historical archived v1 cards are not retroactively called v2 results. Future
retained v2 models/receipts work through the existing replay path without needing
sklearn or a warehouse at scoring time. No workflow was dispatched.

Final validation: `PYTHONPATH=src:. .venv/bin/python -m pytest -q` →
**4564 passed, 1 skipped in 243.80s**. No workflow or `localdata` diff.

## Red-team follow-up — PR #161

Adversarial tests were run against the originally published `739c9ec` source
in an isolated ignored tree with its modules explicitly preloaded (to avoid
pytest importing the repaired checkout). **All nine new cases failed there**;
the same nine pass after repair. These are regression reproductions, not new
profitability evidence.

Fixed findings:

1. **Raw squad identity lost in form.** Building form rows from compact keys
   removed token boundaries recognized by `form_intel` (U21/W/II), so valid
   non-senior history became unavailable. The ENH-only snapshot now retains
   deterministic raw donor spellings. Conflicting squad classes or absent raw
   spellings remain unavailable, not inferred from a compact key. Default
   non-ENH result collection is unchanged.
2. **Cache could bypass the squad veto.** Equal canonical keys do not prove
   equal squad classes. Both team/H2H feature-cache keys and fixture receipts
   now include squad classes.
3. **Missing or mismatched v2 receipt was accepted.** The scorer now requires
   a receipt bound to the specific model key as well as fixture, contract and
   squad identity. A missing receipt falls back to cohort ordering rather than
   silently scoring an entirely imputed context. Valid missing measurements
   *inside* a bound receipt still use documented training-mean imputation.
   Historical v1 payload interpretation remains unchanged.
4. **Optional failure could erase legitimate evidence.** Optional training
   feature preparation is isolated from descriptive cohort construction. A
   failure disables that fit, never silently trains on a partial population,
   and reports coverage as null (unavailable), not observed zero. Optional live
   forecast failures retain the parent candidate and mark context unavailable;
   the ENH scorer then falls back while retaining measured cohort admission.
5. **Boolean/numeric duplicate mismatch.** A bool and numeric 1 could compare
   equal during conflict detection but produce different optional forecasts
   depending on capture order. Type-aware feature conflict comparison now
   quarantines that context in either order without changing parent admission.

Final repaired-suite validation:
`PYTHONPATH=src:. .venv/bin/python -m pytest -q` →
**4573 passed, 1 skipped in 244.68s**. The nine red-team tests separately pass.
No workflows dispatched; no workflow, Main policy, staking, frozen-card or
financial-state edits. Existing historical capture/label-known-by limitations
and unproven production economics remain open, not certified by this review.

The original PR head also has a failed external `Workers Builds:
edge-factory-source-relay` check. GitHub exposes its dashboard link but no
failure log in the check output; this review does not diagnose that build or
represent local pytest success as all remote checks passing.

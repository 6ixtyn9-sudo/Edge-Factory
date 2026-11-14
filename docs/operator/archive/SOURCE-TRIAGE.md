# Source triage TR-1 (item 5, phase 1) — committed-capture audit

**Status:** evidence + findings. Reproduce: `python3 scripts/audit_source_independence.py`
(read-only; committed capture files only). **Generated 2026-10-02.**

## Headline findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| TR-1 | All three committed prediction-series files (`forebet.csv.gz`, `zulubet.csv.gz`, `statarea.csv.gz`) **end on 2026-06-12** — the committed assay/backtest base is 3.5 months stale. Live daily picks still fetch these sources fine on CI (fetch layer healthy); what stopped is PERSISTING the daily captures into the committed files, so walk-forward assays, decay monitoring and debias fitting grade against a pre-June world. Git history is periodically squashed (one persist-commit touches every file), so commit-level forensics of 06-12 are not available in-repo. | **high** | outer data pipeline (restore persistence or point assays at wherever post-June captures now land) |
| TR-2 | `vitibet` has **no committed prediction series** at all — no mirror auditable, no gradeable history in-repo. | medium | same pipeline decision as TR-1 |
| TR-3 | `scoutingstats` capture stale since **2026-09-04** (item 3; pricing containment already landed this branch). | high (contained) | outer data pipeline (restore sync; containment self-heals when it does) |
| TR-4 | **Independence audit of the live three: PASS.** No mirrors in the core consensus (window 2026-03-29 → 2026-06-12, last covered): | — | — |

| pair | shared fixtures | corr (prob vectors) | pick agreement | mean prob gap | verdict |
|---|---|---|---|---|---|
| forebet vs zulubet | 1,907 | 0.535 | 60.6% | 13.9 pts | ✅ distinct voice |
| forebet vs statarea | 5,539 | 0.672 | 62.0% | 9.4 pts | ✅ distinct voice |
| zulubet vs statarea | 1,973 | 0.688 | 68.7% | 13.8 pts | ✅ distinct voice |

Contribution on 1,156 triple-covered fixtures (unweighted descriptive;
production consensus is weighted): dropping zulubet flips **18.0%** of picks,
forebet 8.7%, statarea 8.0% — all three genuinely move the consensus; no dead
weight, no single dominant voter.

## Yardstick for new sources (gates phase 2)

A national-language predictor (prosoccer.gr / vitibet template, per the
source-strategy doc's phase 2) may enter the consensus only after a ≥30-day
committed shadow capture proves, against EACH live source on shared fixtures:
- correlation < 0.95 AND pick agreement < 95% (mirror rule: 0.98/99%/≤0.5pt
  is an automatic reject — one upstream, not two votes), and
- dropping it from the unweighted consensus would NOT move picks <5% on
  triples (below that it is dead weight at capture cost).

`scripts/audit_source_independence.py` produces both numbers; extend
`SOURCES` with the shadow file when one exists.

## Next phases (unchanged from the roadmap doc)

1. ~~Triage (this document)~~ — TR-1..TR-4 findings above; operator owns the
   outer-pipeline restores (TR-1, TR-2, TR-3).
2. National-language predictors (prosoccer.gr / vitibet template) — gated by
   the yardstick above; start as shadow capture, never in pick path until
   certified.
3. Open data as cross-check.
4. Derive-own-model from the accumulated committed series (the healthy
   fb/zb/sa history is the training base; TR-1's 3.5-month gap is the first
   thing to close).

*Prepared by Arena agent 2026-10-02; data-pipeline restores belong to the
operator/outer pipeline — this repo change is evidence + yardstick only.*

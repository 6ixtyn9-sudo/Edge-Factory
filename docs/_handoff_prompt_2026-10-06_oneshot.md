# Edge-Factory: Restore live auto-betting — single-session, full scope

> **Repo-verified addendum (2026-10-06).** Two items in the prompt below were
> checked against this checkout after it was drafted. Both resolve in a way
> that *reduces* the next session's scope — read these first.
>
> 1. **The diagnosis doc is reachable.** `docs/diagnosis_no_autobets_2026-10-06.md`
>    is committed and pushed on branch `arena/eda5708c-edge-factory`
>    (commit `326d7d4`). The "if not found" branch in §Branching is dead code —
>    the file exists, with its two inline `CORRECTION` / `SCOPE NOTE` blocks.
>    Raw URL:
>    `https://raw.githubusercontent.com/6ixtyn9-sudo/Edge-Factory/arena/eda5708c-edge-factory/docs/diagnosis_no_autobets_2026-10-06.md`
>
> 2. **Secondary finding #2 (kickoff mismatch) is NOT a gap — it is the
>    designed, tested behaviour.** Do not investigate it. The guard lives in
>    `scripts/capture_theodds.py` (`KICKOFF_MISMATCH_MIN = 15`,
>    `START_GRACE_MIN = 30`, mismatch branch at :345-370) and the exact
>    Albania-v-San-Marino shape — legacy display `17:45Z` vs captured
>    `18:45Z`, Δ=60m, resolved by `display-fallback override` — is covered by
>    an explicit acceptance test at `tests/test_capture_plan_kickoff.py:150-153`,
>    which asserts the warning text verbatim *and* asserts the leg is NOT
>    dropped as "kickoff already passed". Planning from the captured UTC
>    witness and overriding the legacy display string is the intended
>    contract. Strike this bullet from "secondary findings"; the remaining
>    three (SKIPPED_VETO calibration, 17 ambiguous settlement keys,
>    `soccervista` missing table) still stand.

---

## Branching

Branch from fresh `main`. Do not continue on any stale/closed branch. Before
starting, read `docs/diagnosis_no_autobets_2026-10-06.md` — see the addendum
above for its location. It contains the full original diagnosis plus two
inline corrections (search for `CORRECTION` and `SCOPE NOTE`). The facts below
are already extracted and verified from source, so the prompt is self-contained
either way; do not invent anything beyond what's stated here.

**Do this all in one sitting.** Work through the phases below in order
because 3 is a genuine prerequisite for 4 and 5 (explained below), not an
arbitrary priority call. Produce granular commits per logical change
(`git add <specific paths>`, never `git add -A`). End with one consolidated
report covering every phase, and stop there — do not merge or open a PR
without the user's explicit go-ahead on the consolidated report.

## Background: verified facts from the 2026-10-06 diagnosis

On 2026-10-06, 8 candidates were produced; 7 were killed by the price layer
(`min_odds_floor` ×4 at 1.01–1.13, `price_source_not_execution_eligible` ×3 on
`scoutingstats_odds`), leaving 1 qualifying leg against `LEGS_PER_ACCA = 2` —
structurally un-bettable alone.

Replaying 743 archived candidates over the trailing 30 days:

| outcome | count | share |
|---|---|---|
| QUALIFIED | 224 | 30% |
| `price_source_not_execution_eligible` | 351 | 47% |
| `bucket_veto` | 71 | 10% |
| `min_odds_floor` | 55 | 7% |
| `price_source_unregistered` | 31 | 4% |
| `price_quarantine` | 11 | 1% |

81% of rejections are a pricing-layer failure, not an edge failure. Of the
351 `price_source_not_execution_eligible`: 279 are `scoutingstats_odds`
(audit-only by design, `execution_eligible=False`), 72 are `forebet_best`
(Forebet was retired from live production 2026-06-12, but `picks_today.py`
still labels fallback rows with that source name — these are dead on
arrival). Of the 31 `price_source_unregistered`: 17 are `zulubet`, 14 are
`odds_source=None`.

Source health that day: of 9 executable price sources, only 2 were alive
(`theoddsapi`, `betexplorer_odds` — the latter capped at 12 fixtures/run and
fed only fixtures that are already picks, so it can't widen the funnel).
Dead: `bzzoiro_odds` (403, token dead), `oddspapi_odds` (429), `sharpapi_odds`
(404, contract broken), `pinnapi_odds` (200 but empty), `betminer` (404,
contract broken), `sportytrader_odds` (Cloudflare challenge).

`theoddsapi` covers 49 active soccer league keys with **96% of paid quota
idle** (56 of ~1440 credits used that month across 3 keys) — the constraint
is league-key coverage mapping (no international-friendly/AFCON-qualifier
keys), not budget.

Separately, at 04:04 that day `mine_consensus` certified 16 edges;
`decay_monitor` immediately benched 7 (all six `ml-meta avg_p>=55..80` tiers
plus `3way-unanimous home-only avg_p>=60`) — every one of them while printing
+53% to +66% recent ROI. Four structural faults, in dependency order:

- **Fault D (`src/edgefactory/warehouse.py`)**: `consensus2`/`consensus3`/
  `consensus4` are SQL views hard-coded to join Forebet with other sources
  (comment: *"Legacy consensus views remain Forebet-anchored for historical
  rule continuity"*). But live, `picks_today.eval_1x2` computes "N-way
  unanimous" over whichever ≥2 of 6 voters (`forebet(retired)`, `bzzoiro(403)`,
  `zulubet`, `statarea`, `vitibet`, `betclan`) happen to be present that day.
  A rule like `2way-unanimous avg_p>=70` was certified on forebet×zulubet and
  is now served on zulubet×vitibet or statarea×betclan — same name, different
  estimator. Every downstream certified statistic, including what the decay
  monitor benches against, inherits this mismatch. **This must be resolved
  first** — fixing training or the decay test against a baseline that
  doesn't describe what's actually served is fixing the wrong number.

- **Fault B (`scripts/mine_consensus.py:560-561`)**: `ml-meta` trains
  `ht_diff = ht_hs - ht_gs` and `ht_total = ht_hs + ht_gs` from `consensus3`,
  which sources `ht_hs`/`ht_gs` from `edgefactory/sources/forebet.py`'s
  `Host_SC_HT`/`Guest_SC_HT` — the match's actual half-time score, in the same
  payload as the final score. These are the two largest-magnitude
  discriminative features in the trained model (`ht_diff +0.245`,
  `ht_total +0.192`). At serve time `picks_today.py` has no forebet row
  (retired 2026-06-12), so `ht_diff = ht_total = 0.0`. **Important**: the
  serve-side zeroing in `src/edgefactory/ml_fade_research.py:93` ("checkpoint
  ⑫ contract") is correct and must not be touched — the defect is purely that
  training fit a boundary using data the live model will never have. The
  certified baseline (87–91% hit rate at high tiers) is therefore a number
  the live model can never reproduce, and `decay_monitor` dutifully benches it
  for falling short of an unreachable bar, forever.

- **Fault C**: 11 of the model's 26 features are forebet-only and are all
  dead/defaulted at serve (`fb_p`, `ht_p`, `kelly`, `pred_total`, `pred_diff`,
  `goalsavg`, `p_ng`, `p_under`, `p_gg`, plus the two leakage features above).
  Quantified per-fixture signal destroyed at serve is ≈0.44 logits
  (quadrature), ≈7 percentage points of probability at p≈0.80. Also, the
  training query filters `WHERE fb_p IS NOT NULL AND zb_p IS NOT NULL AND
  sa_p IS NOT NULL` — the model is trained exclusively on forebet-covered
  fixtures and served exclusively on non-forebet fixtures. Different
  population entirely.

- **Fault A (`src/edgefactory/assay.py`, `decay_verdict`)**: triggers
  DECAYING when `r_p < b_lb and r_lb < 0.90 * b_lb` (Wilson lower bounds).
  With baseline n≈2678 and recent n≈123, it is near-arithmetically impossible
  for the recent-window LB to clear `0.9 × baseline_LB` unless the point
  estimate nearly matches the baseline point estimate — the second clause is
  almost free, so the test collapses to "recent point estimate dips below the
  baseline's lower bound," a one-sided test that double-counts uncertainty
  against the edge. `should_bench` then adds `if recent_roi < 0: return True`
  (defensible) but has **no symmetric rescue** — a +53% ROI cannot save an
  edge that trips the hit-rate clause, which is the wrong objective function
  for a system whose actual output is P&L, not hit rate.

Secondary findings worth checking as part of this work, not necessarily
fixing without flagging first:

- `SKIPPED_VETO` is currently the *best*-performing bucket (n=110, recent ROI
  +7.9%, LB 0.706) while `CAUTION` loses money (-12.2%) — the purity veto may
  be mis-calibrated. Investigate, report, do not silently re-tune without
  flagging.
- ~~Kickoff-mismatch display-fallback override~~ — **struck, see addendum:
  already the designed and tested behaviour, not a gap. Do not investigate.**
- 17 ambiguous settlement keys (e.g. `Juventud Unida SL` vs
  `Juventud Unida Univ.`) silently pollute the hit-rate series the decay
  monitor reads. Worth a mention in the final report even if out of scope to
  fully resolve.
- `soccervista` is referenced in the warehouse but the table doesn't exist
  (`CatalogException`) — every soccervista confirmation lever is a permanent
  no-op. Report; fix only if trivial and clearly safe.

## Goal

Restore live auto-bet flow without weakening any existing fail-closed guard.
A correct outcome may mean lower bet volume than before, if that volume is
now honest. Do not optimize for "bets fire again" over "the numbers backing
those bets are true."

## Hard constraints (non-negotiable)

- Do not raise, bypass, or special-case `MIN_LEG_ODDS` (1.20) or
  `LEGS_PER_ACCA` (2).
- Do not flip any currently audit-only or non-execution-eligible source
  (`scoutingstats_odds`, `zulubet`, or anything resolved only via
  `VOTE_ONLY_SOURCES`) to execution-eligible without hard evidence it carries
  a real, book-backed, executable price, and explicit user sign-off before
  that specific change ships.
- Do not weaken `decay_verdict`'s underlying intent (catching real decay).
  Any redesign of the statistical test must be justified with backtested
  evidence against full settled history in both directions: materially fewer
  false positives on healthy edges, AND no loss of detection on a verifiably
  decaying edge (synthetic or historical). Do not simply add an unconditional
  ROI override that can rescue any DECAYING verdict regardless of magnitude —
  that trades one blunt instrument for another.
- Do not blindly strip all forebet-derived features from the ml-meta model.
  Measure which are actually load-bearing at serve time (the two leakage
  features clearly are; the other 9 forebet-only features need the same
  check) before deciding what to drop versus what to find a serve-time
  substitute for.
- Do not silently merge, rename, or reinterpret `consensus2`/`consensus3`/
  `consensus4` to paper over Fault D. Either keep them explicitly
  Forebet-anchored for historical continuity (as currently commented) and
  create correctly-named live-anchored views/rules that `eval_1x2` and
  `mine_consensus` actually certify against, or re-point everything at one
  correctly-described set of views — but the end state must have a 1:1
  mapping between what a rule is certified on and what it is served from,
  and the report must show that mapping explicitly, before/after.
- Do not modify the kickoff-mismatch guard's thresholds
  (`KICKOFF_MISMATCH_MIN`, `START_GRACE_MIN`, close-window tolerance) in
  `scripts/capture_theodds.py`, or its tests. That work is already merged and
  verified.
- Never touch `.github/workflows/*`.
- Never author or modify anything under `localdata/`.
- Granular commits, explicit file paths, never `git add -A`.
- Do not merge or open a PR without the user's explicit go-ahead on your
  final consolidated report.

## Phase 0 — Reproduce current state (verification, no code changes)

Re-run the rejection-breakdown reproduction against the live `localdata/`
state in your fresh checkout (not the 2026-10-06 snapshot above, which is
illustrative and will be stale by the time you run this):

```bash
PYTHONPATH=src python3 - <<'PY'
import json, importlib.util, sys
sys.argv=['x']
s=importlib.util.spec_from_file_location('at','scripts/auto_tickets.py')
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
for r in json.load(open('localdata/picks_today.json')):
    print(r['home'],'v',r['away'], r.get('odds'), r.get('odds_source'),
          m.playable_leg_rejection(r, day='<today>', execution_safe=True))
PY
```

Report what you actually see. If your numbers differ materially from the
2026-10-06 snapshot above, say so plainly — don't force a match.

## Phase 1 — Fix Fault D: consensus view / estimator mismatch (prerequisite)

Confirm the mismatch described above by diffing what each certified rule's
stats were computed against (`warehouse.py` view definitions) versus what
`picks_today.eval_1x2` actually serves from live. Then either:
(a) rename so a given rule name always means the same view/estimator
certify-to-serve, or (b) re-point the serve path at the actually-certified
view, or (c) keep the Forebet-anchored views explicitly historical and stand
up correctly-named live-anchored equivalents that get certified fresh. Pick
whichever is least disruptive and most honest; document the choice. Produce
an explicit before/after table: rule name → certified-on view → served-from
view → what changed.

## Phase 2 — Price-layer triage (independent of phases 1/3/4, can run anytime)

Classify each dead/degraded price feed:

- Credential/contract-only failures (`bzzoiro_odds` 403, `oddspapi_odds` 429,
  `sharpapi_odds` 404, `betminer` 404, `pinnapi_odds` empty,
  `sportytrader_odds` Cloudflare) — document as triage only; don't attempt
  a code fix you can't actually exercise without new credentials.
- Genuinely code-fixable: fix with before/after evidence of usable prices
  returned.

Evaluate `theoddsapi`'s league-key coverage against its measured idle quota
(currently ~96% idle) — this is the one source where a code change (adding
league keys, e.g. international friendlies / AFCON qualifiers) can plausibly
recover real coverage without needing new credentials. Quantify expected
gain with real quota/usage numbers pulled from the live account, not
estimates.

Also: widen `betexplorer`'s feed if safe — currently capped at 12 fixtures
and fed only fixtures that are already picks, which structurally prevents it
from ever widening the funnel. Check whether raising its limit and feeding
it the full scored-candidate pool (not just existing picks) is safe within
its rate limits before changing it.

Fix the `known()`/`spec()` disagreement (`auto_tickets.py:1566` vs
`price_sources.py:400`) so vote-only sources log
`price_source_not_execution_eligible` instead of the misleading
`price_source_unregistered`. State explicitly in the report that this
recovers ~0 legs — it's a diagnostic-honesty fix, not coverage work. Also
stop `picks_today.py` from labeling post-cutoff fallback rows with
`odds_source="forebet_best"` since that source has been retired since
2026-06-12 and those rows are dead on arrival.

## Phase 3 — Fix Fault B/C: ml-meta training leakage (depends on Phase 1)

Using `mine_consensus.py`'s own feature construction as the repro, confirm
`ht_diff`/`ht_total` are still built from half-time-score data and still
load-bearing in the currently-trained model (check fitted coefficient
magnitude, not just feature presence). Retrain excluding every feature
confirmed unavailable at serve time — not just the two leakage features;
check all 11 forebet-only features for serve-time availability, and only
keep ones you can confirm have a real, non-degenerate value at serve. If
Phase 1 changed which consensus view backs this model's inputs, retrain
against the corrected view. Report the honest, serve-realistic baseline
(hit rate, ROI) — expect it to be materially lower than the previous 87-91%
figure, and report it as such, not softened.

## Phase 4 — Fix Fault A: decay-monitor redesign (depends on Phase 3)

Redesign the DECAYING test to account for the sample-size asymmetry between
recent and baseline windows (e.g. a proper two-sample proportion test, or
recent-LB vs baseline point-estimate with an explicit minimum-detectable
effect) without removing the ability to catch genuine decay. Consider
whether a bounded ROI veto (not unconditional) that can prevent a bench when
recent ROI is strongly positive is appropriate — justify the threshold with
backtested evidence, don't guess at it. Backtest against full settled
history using the Phase-3 honest baseline, not the leakage-inflated one. Add
regression tests proving both: it no longer benches on noise alone, and it
still catches a verifiably decaying edge (synthetic or historical case).

## Acceptance criteria

- Full existing test suite passes, plus new targeted tests per phase.
- Each phase ships with real command output as evidence — replay/backtest
  runs, not summarized or rounded claims. Flag any place your reproduction's
  numbers don't match this prompt's 2026-10-06 snapshot.
- Before/after numbers for every quantitative claim (coverage %, rejection
  counts, model metrics, decay-monitor false-positive/negative rates).
- `git diff --stat` scoped to `.github/workflows/` and `localdata/` showing
  no changes.

## Final report (single consolidated document, end of session)

Per phase: what was actually broken (evidence-backed), what changed (diff/
commit references), what was deliberately left alone and why, what's still
open. Explicitly call out anything from "secondary findings" you
investigated but chose not to fix, and why. End with a clear go/no-go
recommendation and wait for the user's explicit instruction before merging
or opening a PR — do not merge or push on your own judgment regardless of
how clean the results look.

# ML-Fade Research Evidence Policy — FROZEN 2026-09-20

This document predeclares how the ml-meta / ml-fade **research** population
is captured, settled, monitored, and re-evaluated. It exists so the
evidence can mature **without ever being promoted to production** by the
machinery that collects it.

> The predeclared price-robustness audit (2026-09-20) classified the
> `ml-fade home-fade avg_p>=65` slice **INSUFFICIENT EVIDENCE**. That means
> "not yet" — the correct response is disciplined accrual, not label
> shopping. Nothing in this document re-opens the certification question.

## 1. What is captured, where, and why it is certification-independent

- Serving-time model inference in `scripts/picks_today.py` runs whenever a
  registry `ml_model` exists. For **every model-scored fixture** (regardless
  of any rule's certification status) the collector records two
  research candidates into the tracked ledger
  `localdata/ml_fade_research_ledger.json`:
  - the **ml-meta parent** row (family `ml-meta`): selection, `ml_p`,
    `avg_p`, parent-side forebet/zulubet quotes;
  - the **ml-fade** row (family `ml-fade`): the deterministic binary 1X2
    inverse (`home`<->`away`), its own stated confidence
    `fade_avg_p = (1 - ml_p) * 100`, and the **fade side's own** forebet /
    zulubet quotes (never the parent's price). Draw parents are **excluded
    explicitly** — no inverse is invented.
- Every row records: league, sport, market (`1x2`), date, kickoff, sources
  used, serving `model_key` (hash of coef/intercept/feature_cols), the
  checkpoint-⑫ contract features (`ml_ht_diff`, `ml_ht_total` — must be 0),
  and provenance fields `parent_family="ml-meta"`, `edge_family`,
  `derivation="inverse-selection"`.
- Identity is the accent-safe operational team key + date + family + market.
  Re-running the pipeline **never duplicates rows**; re-observation refreshes
  only `last_seen_at` / latest quotes / `repriced_count`. The **first-seen
  (bet-time) quote and prediction are immutable** — later captures can never
  overwrite them, and closing prices are never stored or used.
- Research capture requires the same **pre-match guard** as operational
  picks (trusted kickoff, minimum lead). It requires **no** certification,
  bucket, or ticket. A missing `purity_registry.json` (the frozen
  veto-context surface the research rules are declared against) disables the
  write loudly (fail-closed) rather than storing context-less evidence.
- The ledger is git-tracked (`.gitignore` negation), so the workflow's
  `Persist pipeline state to git` step commits it after every service run —
  it survives cache eviction. Research **outputs** (checkpoint reports and
  archived study logs) stay in ignored `localdata/` and are additionally
  uploaded as run artifacts, matching existing conventions.

## 2. Settlement

- Facts come only from the tracked, bot-committed
  `localdata/settled_results.json` (never from a local-only cache).
- A row settles when every matching fact agrees (same outcome + score),
  with team identity confirmed by ledger keys **or** the curated
  `localdata/team_aliases.json` groups, and the result date within **±3
  days** of the captured fixture date (postponement tolerance).
- Conflicting fact signatures → status `conflict`, surfaced loudly, never
  auto-resolved. Malformed identity/date → `conflict`.
- No fact after **21 days** → status `unmatched` (postponed/void/vanished
  fixtures): visible staleness, excluded from win/loss statistics. Missing
  or unparseable prices are likewise **excluded** from priced denominators
  (`n_priced < n`) — never silently scored as wins or losses.
- `settled` and `conflict` rows are frozen: later information never reopens
  them.

## 3. Frozen checkpoint cadence (predeclared; do not tune)

A checkpoint is **due** when **any** holds:

1. **Bootstrap** — no checkpoint has ever run;
2. **Monthly** — the calendar month (SAST) has advanced since the last one;
3. **Settled increment** — settled ml-fade rows grew by **>= 50**;
4. **Active days** — **>= 30** distinct capture days passed since the last
   checkpoint.

**Execution anchor (operator direction 2026-09-20, refined 2026-09-21):** due
checkpoints are *evaluated* only once the day's **official 09:00 SAST freeze**
has been reached — a **wall-clock** cut, the same cut the auto-bets and the
official record freeze on (`checkpoint_eval_window_open` in
`scripts/daily.py`). "Official" here means the clock, not the pipeline's
first heavy *official* build: under the overnight cadence that build fires at
00:00 SAST and writes the daily official-run marker, and it must **not**
consume checkpoint due-ness. (Observed once before this refinement: the
00:00 SAST build consumed the bootstrap checkpoint at 2026-09-21T00:19 SAST —
timing-only deviation; the evaluation used real settled evidence, produced no
production effect, and is retained in the checkpoint history.) Every service
run (00/03/06/09/12/15/18/21 SAST) still captures, settles, and prints
accrual/monitoring — evidence accrual must be continuous because late-slate
fixtures and newly settled facts are only ever *late*, never *unfair* — but
the evaluation/report fires at the first post-freeze run, so every checkpoint
is cut against comparable official state. Off-window due-ness is logged and
**not consumed**: the freeze-window run evaluates with the same predeclared
reasons. `--force-checkpoint` remains the explicit human override.

At each evaluated checkpoint (`scripts/ml_fade_research_eval.py`, invoked by
`scripts/daily.py` from both autonomous modes — evaluation permission comes
solely from the 09:00 SAST freeze window; `--settle-monitor-only` off-window):

- the **fixed price variants** (`zb-only`, `fb-only` on first-seen quotes)
  are recomputed for the parent and fade populations;
- the **frozen reference accumulators** (avg_p grids 55/60/65/70 on both
  families) are recomputed;
- the **frozen full-population studies**
  (`scripts/research_ml_fade_contexts.py`,
  `scripts/research_ml_fade_price_study.py`) are re-run **unmodified**;
  the runner never edits their definitions and their outputs are archived
  under `localdata/ml_fade_checkpoint_<study>_<date>.txt`;
- the report is written to `localdata/ml_fade_research_report_<date>.md` and
  printed to the run log; the tracked state
  (`localdata/ml_fade_research_state.json`) appends one history entry.

## 4. Automatic rule-candidate signal — research heuristic, NOT certification

The report prints **OBSERVING** unless **all** hold on ledger evidence:

- settled fade rows **>= 200**;
- **zb-only**: `n_priced >= 150`, Wilson LB **>= 0.55**, ROI **> 0**;
- **fb-only**: `n_priced >= 150`, Wilson LB **>= 0.55**, ROI **> 0**;
- **zero** unresolved conflict rows in the fade family.

Then it prints **CANDIDATE** — meaning "a human should look", nothing else.
It cannot certify or promote: certification remains the existing
walk-forward machinery (`mine_consensus.evaluate`) with its existing gates,
**unchanged**. No run, however convincing, changes operational behavior.

## 5. Monitoring (every run, visible in the pipeline log)

- 🚨 fade accrual stall: **>= 10** new parent rows since the last checkpoint but
  **0** new fade rows;
- 🚨 fade price coverage: settled fade **>= 30** and first-quote coverage
  **< 90%** for either book;
- 🚨 model method drift (feature set/order vs the frozen method) or model
  turnover affecting recorded rows; 🚨 non-zero checkpoint-⑫ contract
  features on any research row;
- 🚨 unresolved conflict rows, in either family.

## 6. Manual operation

```bash
# settle + monitor + evaluate any due checkpoint (official-freeze behavior):
PYTHONPATH=src python3 scripts/ml_fade_research_eval.py

# intraday behavior — settle + monitor, defer due checkpoints to 09:00:
PYTHONPATH=src python3 scripts/ml_fade_research_eval.py --settle-monitor-only

# force a checkpoint without the heavy frozen studies (human override):
PYTHONPATH=src python3 scripts/ml_fade_research_eval.py \
    --force-checkpoint --skip-studies
```

## 7. Changing this policy

The frozen values above (cadence, grids, gates, tolerances) are **not
tuning knobs**. They may be amended only by an explicit, documented decision
in a dedicated commit that edits this file, the constants in
`src/edgefactory/ml_fade_checkpoint.py`, and records the operator direction
— never in response to interim performance, and never silently. Between
amendments the definitions are frozen.

Amendments on record:

- **2026-09-20** — execution anchor pinned to the official 09:00 SAST freeze
  (operator direction): intraday runs settle/monitor/defer without consuming
  due-ness; `--force-checkpoint` is the documented human override.
- **2026-09-21** — anchor definition refined from "the pipeline's first heavy
  *official* run of the day" to the **09:00 SAST wall-clock window**
  (`checkpoint_eval_window_open` in `scripts/daily.py`), after the overnight
  00:00 SAST heavy build consumed the bootstrap checkpoint at
  2026-09-21T00:19:31 SAST instead of the freeze run. Evaluation gating now
  ignores pipeline mode at BOTH autonomous call sites (fail-closed).
  Recorded deviation: the 2026-09-21 bootstrap evaluation fired at 00:19 SAST
  (checkpoint history entry 0 on 5 settled fade rows, verdict "observing") —
  retained as real evidence; never re-run, never erased.

# ML ladder + Phase 5 K contract — branch state (2026-10-08)

Branch `arena/4b287a0a-edge-factory`, commits `a2d56aa` and `53799b2` (plus this
note). Everything below was verified on a rebuilt warehouse (18,478 consensus3
rows) before being committed; nothing in these commits touches the served model
until an operator promotes an activated era.

## What changed

**Miner (`scripts/mine_consensus.py`)**
1. ml-meta / ml-fade rung ladder widened to 30..85. Widening the ladder widens
   what gets *judged*: every rung faces the same walk-forward gates and anything
   that misses them stays a candidate and fires nothing.
2. `ht_diff` / `ht_total` dropped from the ml-meta feature set (diagnosis
   2026-10-06 fix #6). They are the actual half-time score — target leakage —
   and are pinned to 0 at serve, so they could only inflate a research fit.
3. `_score_live_model` now scores the incumbent on the incumbent's own feature
   contract. Without this, (2) would have silently stopped the incumbent
   prediction export and sent the decay monitor fail-closed on every ML edge.
4. One `weighted-1x2` rule instead of six identical ones (unanimity forces
   `w_score == 1.0`, so 0.55..0.80 selected byte-identical match sets).

**Serve (`scripts/picks_today.py`)**
5. The context odds-floor drop is no longer silent: the reason is tagged on the
   row and counted in the run summary, split into evidence-backed CAUTION vs
   UNKNOWN-odds-band-only. Staking behaviour is unchanged.
6. The declared-source columns of the K contract are built from the same rows
   the 1x2 election uses; missing model columns are imputed from the model's own
   recorded means (never a bare `0.0`) and reported once.

**Phase 5 (`src/edgefactory/phase5_k.py`, `scripts/fit_phase5_candidate.py`,
`src/edgefactory/phase5_promotion.py`, guard, `phase5_activate` CLI)**
7. One shared builder for the frozen 32-column K contract, used by both the fit
   and the scorer. A dark feed is *represented* (`_available=0.0`, `_p` = the
   recorded era mean), never dropped — so a returning feed is a data event, not
   a schema change.
8. A read-only era fit that emits an activation-shaped payload, refuses below
   its declared floors, and writes only `localdata/ml_meta_k_candidate.json`.
9. The promotion bridge. Activation alone could never reach the registry: the
   guard treated any non-incumbent mode as unverifiable, so activating a
   candidate would have switched ML off. `phase5_activate promote` now verifies
   the post-state with the guard **before** writing, keeps a byte-for-byte
   backup under `localdata/phase5_reconciliation/`, and benches the `ml-fade`
   family (those cuts were derived from the incumbent's selection).
   `phase5_activate restore` puts the frozen incumbent back.

## What a branch run should show

* Miner: `... preserving model_key=a45beab0c878 and 14 current ML edge(s)` —
  the ML payload must NOT change; `candidate_certified=17` in the research file.
* `edges_consensus_research.json`: ml-meta rungs 30..80 certified on the
  leak-free model (>=85 no longer reaches `min_overlap_n`); one weighted rule.
* `Saved 18,478 live-incumbent ML predictions (model_key=a45beab0c878)`.
* picks summary gains `ctx_floor_dropped=N`, plus a `context floor:` line when
  it fires.
* `served model imputed ...` on stderr means a served model is missing columns
  it was trained on — investigate before trusting that slate. The incumbent's
  26 columns are all produced, so it should stay silent.
* The miner prints a `Phase 5 K-contract coverage (read-only)` block at the
  end of every run — which of the 32 columns the era can fill, and whether a
  candidate fit is due. Diagnostics only; it cannot affect the mine.

## What is deliberately NOT live

The retrained model, the new rungs and everything K-shaped are research-only.
Path to live: `fit_phase5_candidate.py` → certify (clauses 3..9 still blocked:
era evaluator, identity audit, comparator, Forebet overlap) → `dry-run-revert` →
`activate --confirm` → `promote --confirm`. `kill-switch` + `restore --confirm`
is the way back.

## One decision this branch surfaces

Forebet is retired for production days after 2026-06-12
(`edgefactory.source_health.FOREBET_LIVE_LAST_DAY`; the firing tripwire records
"pricing/voting retired 2026-06-12"). Two consequences that waiting cannot fix:

* In the forward era the electors are **zulubet and statarea**; `fb_p` is
  imputed every day. The K contract supports that by design (dark -> recorded
  mean), so a fit can still be produced.
* The certifier's clause 7 requires >=200 pairwise-overlap rows against *every*
  existing source, Forebet included, and reports `blocked_forebet_overlap`.
  While Forebet stays parked that clause **cannot** clear, so the era can never
  certify and activation can never be reached — no matter how long the capture
  accrues. Either clause 7 is re-scoped to the sources that still exist, or
  Forebet has to come back for capture. This is a policy decision, not a bug,
  and the certifier already refuses honestly rather than pretending.

## Gotchas for the run

* Scoutingstats and betminer are not 1x2 voters, so their K columns stay
  unavailable even with working feeds — a roster decision, not a bug.
* Only vitibet / bzzoiro / betclan of the five declared sources are 1x2 voters.
* `tests/test_supabase.py` and `tests/test_sync_supabase.py` cannot import
  without the `supabase` package; CI installs it.
* No DC/DNB prices exist in any committed corpus — do not go looking.

## What the branch run actually showed (run 37798663313, 2026-10-08)

Both jobs green, 38 minutes, `mode=auto` (`--auto-once`).

**Confirmed as designed**

* `PHASE5_REGISTRY_GUARD incumbent verified; preserving model_key=a45beab0c878
  and 14 current ML edge(s)` — the ML payload after the run is byte-identical to
  before it (same 26 columns, same coefficients, same intercept).
* `weighted-1x2`: six identical rules on main, one after the miner change.
* Research ladder: ml-meta 30..80 all certified on the leak-free fit, ml-fade all
  candidate, `candidate_certified=21`; picks summary carries the new
  `ctx_floor_dropped` counter.
* The new K-contract coverage block printed twice — once from the miner, once
  from the new CI step — with identical numbers.
* `served model imputed ... fb_p` on every slate. That is the retired Forebet
  elector, now an honest, visible imputation instead of a silent `0.0`.

**Two things the run taught us**

1. `mode=auto` resolves to `autonomous_intraday` at this hour, and the shadow
   capture is authorized only for the full official run, so the log says
   `PHASE5_CAPTURE status=skipped_by_mode`. The Phase 5 capture lane is exercised
   by `mode=official_morning` (`--force-repick`, mode `official`, not
   picks-only). Note that it force-repicks and overwrites the morning baseline.
2. The coverage report said `warehouse_rows=533` yet the trio reported
   `fixtures_present=0`, and the note printed at the time blamed a missing local
   shard. That was wrong. The era window is built from *fixture* dates and is a
   window of fixtures still to be played (`2026-10-08..2026-10-15` from a single
   capture day), while `warehouse.py` builds `forebet_settled` / `zulubet_settled`
   / `statarea_settled` as settle-only filters (`WHERE hs IS NOT NULL AND gs IS
   NOT NULL`). The fitter preferred those views, so for an unplayed window the
   electors are structurally invisible however healthy the feeds are.

   Fixed: the fitter now reads each source's raw table *and* its settled view and
   merges them (neither is a superset — the settled view can carry outcomes a raw
   shard lacks), and `--explain` prints a per-table probe
   (`raw newest=… rows_in_era=…; settled newest=…`) so "the feed is capturing"
   and "the settled view has not caught up" can be told apart from the log alone.

   This also means the era accrues without any code change: once results land,
   the same rows enter the settled tables on the next warehouse build. That is
   the "feeds in, no retrain" path working as intended.

   Two more lines exist so the numbers cannot be misread:

   * `accrual: N settled fixture(s) over D day(s) = R/day`, printed next to the
     floors once anything has settled. The floors are a distance, not a verdict:
     `settled_eligible=14` beside `era-train 0<2000` looks like a dead feed
     until you see the pace it is filling at. A forward era has a span of 0d by
     construction, so the span clause says nothing about feed health.
   * `settled trails raw — …` on a probe line whose raw table is ahead of its
     settled view, naming which of the two causes it is: newer rows with no
     final score yet (normal, resolves on the next build) or newer rows that
     *are* scored but whose `p1/px/p2` did not parse, which `_prob()` maps to
     NULL so the settle filter drops them and they never settle (a shard fault).
     This is the open Forebet question — `settled newest=2026-09-27` against a
     `forebet_2026-09.csv.gz` holding rows to 2026-09-29 — stated rather than
     guessed; the next run's coverage block answers it outright.

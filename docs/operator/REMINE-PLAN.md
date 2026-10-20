# Re-mining plan


<!-- coverage-inventory:start -->
## B0 coverage inventory (local-only, no network)

Observed: `2026-10-02T00:00:00Z`. The inventory is the only input to a future gap-aware crawl plan; no crawl budget is approved by this artifact.

| source | availability | committed / cache-only / total rows | date range (observed days) | internal gaps (crawl candidates) | market coverage | duplicate keys | warehouse tables |
|---|---|---:|---|---|---|---|---|
| statarea | committed | 489,399 / 0 / 489,399 | 2017-01-01 → 2026-06-12 (3447d) | 0 | 1x2_probability (489,286 rows/3447d), ht_1x2_probability (489,286 rows/3447d), ou_probability (489,286 rows/3447d) | 2 groups, 2 rows | statarea:missing, statarea_settled:missing |
| zulubet | committed | 67,216 / 0 / 67,216 | 2024-01-01 → 2026-06-12 (894d) | 0 | 1x2_odds (67,187 rows/894d), 1x2_probability (67,187 rows/894d) | 0 groups, 0 rows | zulubet:missing, zulubet_settled:missing |
| predictz | absent | 0 / 0 / 0 | — (0d) | 0 | — | 0 groups, 0 rows | predictz_raw:missing, predictz_settled:missing |
| windrawwin | absent | 0 / 0 / 0 | — (0d) | 0 | — | 0 groups, 0 rows | windrawwin:missing |
| bettingclosed | absent | 0 / 0 / 0 | — (0d) | 0 | — | 0 groups, 0 rows | bettingclosed:missing, bettingclosed_settled:missing |
| betexplorer_odds | committed | 79,925 / 0 / 79,925 | 2026-01-01 → 2026-06-16 (167d) | 0 | 1x2_bookmaker_rows (79,925 rows/167d), 1x2_odds (61,379 rows/167d) | 0 groups, 0 rows | betexplorer:missing, betexplorer_settled:missing |
| betexplorer_results | committed | 87,508 / 0 / 87,508 | 2026-01-01 → 2026-09-01 (182d) | 62 (2026-06-17, 2026-06-18, 2026-06-19, 2026-06-20, 2026-06-21, …) | settled_score (87,508 rows/182d) | 12 groups, 12 rows | betexplorer:missing, betexplorer_settled:missing |
| scoutingstats | absent | 0 / 0 / 0 | — (0d) | 0 | — | 0 groups, 0 rows | scoutingstats:missing, scoutingstats_settled:missing |
| prosoccer | absent | 0 / 0 / 0 | — (0d) | 0 | — | 0 groups, 0 rows | prosoccer:missing, prosoccer_settled:missing |
| afootballreport | absent | 0 / 0 / 0 | — (0d) | 0 | — | 0 groups, 0 rows | afootballreport:missing |
| betclan | absent | 0 / 0 / 0 | — (0d) | 0 | — | 0 groups, 0 rows | betclan:missing |
| freesupertips | absent | 0 / 0 / 0 | — (0d) | 0 | — | 0 groups, 0 rows | freesupertips:missing |
| forebet | committed | 327,895 / 0 / 327,895 | 2024-01-01 → 2026-06-12 (894d) | 0 | 1x2_odds (225,697 rows/894d), 1x2_probability (327,849 rows/894d), btts_odds (225,711 rows/894d), btts_probability (327,853 rows/894d), ou_odds (225,711 rows/894d), ou_probability (327,853 rows/894d) | 0 groups, 0 rows | forebet:missing, forebet_settled:missing |
| sa_cache | committed (alias/cache) | 489,399 / 0 / 489,399 | 2017-01-01 → 2026-06-12 (3447d) | 0 | — | — | alias of statarea |
| fb_cache | committed (alias/cache) | 327,895 / 0 / 327,895 | 2024-01-01 → 2026-06-12 (894d) | 0 | — | — | alias of forebet |
| clv_cache | committed (alias/cache) | 7,901 / 0 / 7,901 | 2026-06-18 → 2026-10-02 (101d) | 6 (2026-07-10, 2026-07-16, 2026-07-17, 2026-07-19, 2026-07-25, …) | — | — | alias of clv_snapshots |

**Key rule:** `source + date + source_team_key(home) + source_team_key(away) + market`; existing committed rows win collisions. `source_team_key` is the existing alias-aware normalization seam. The `proposed_internal_gap_days` arrays in `localdata/coverage_inventory.json` are the driver input; ranges are display-only.

**Budget gate:** proposed counts above are internal missing days only. Empty sources have no crawl range and require an operator-approved boundary/date floor. Operator approval is recorded for the 3 Statarea gap probes, the 62 BetExplorer result gaps, bounded ZuluBet backfill, and one Football-Data CSV; execution remains single-flight, immutable, and hist-only.
<!-- coverage-inventory:end -->

## B1 runner execution — bounded redirect

`python3 scripts/remine_backfill.py` is invoked by the existing official and
autonomous-intraday chain in `scripts/daily.py`; no workflow YAML change is
needed. Sandbox crawling is closed. The GitHub Actions runner is the only
place this state machine may make the remaining bounded requests.

The append-only `localdata/backfill_ledger.jsonl` is the source of truth for
reruns:

1. The three committed Statarea `no_matches_day` confirmations become
   `held` receipts with `request_count=0`. The runner never imports or calls a
   Statarea fetcher for them.
2. Up to ten not-yet-terminal BetExplorer dates are requested per run through
   `edgefactory.sources.betexplorer_odds`. Its existing single-flight lock,
   three-second throttle, Retry-After handling, and 429 cooling state remain
   in force. Response bytes are written once below the ignored
   `localdata/remine_raw/` tree; checksums, request URL, parser row count,
   duplicate count, existing-wins collision count, and provenance are written
   to both the ledger and `localdata/remine_audit_*.jsonl`. A 403/challenge or
   429 cluster writes a source-freeze receipt and exits zero without trying an
   alternate transport.
3. `betexplorer_results/gap_fill_complete` is written only when all 62
   approved dates have successful or held terminal receipts. Exhausted reruns
   are idempotent and exit zero.
4. The Football-Data proof unlocks on a BetExplorer terminal state: either
   `gap_fill_complete` (`gate_released_by=complete`) or a same-run
   challenge/429 source freeze (`gate_released_by=frozen_blocked`). The latter
   deliberately leaves the 62 dates open for a later retry; it does not hold
   the independent price-history proof hostage. One pre-2026 `E0 × 2024-25`
   CSV proof is then fetched, stored as an immutable, gitignored raw artifact
   with a SHA-256, explicit provenance, opening/closing header checks, and
   normalized donor-coverage report. A failed or incomplete proof is held and
   does not unlock Legalbet.
5. Only after a complete CSV proof, the driver checks Legalbet `robots.txt`
   first, then samples no more than three requests per run and 30 public
   archive pages in total. User/rating/stat paths are excluded. A RU-host
   failure or challenge is recorded and held with no alternate transport or
   escalation. Legalbet page bytes are also immutable raw artifacts with
   checksums.

The per-run stdout meter reports consumed versus budget, remaining gaps,
freeze state, Football-Data state, Legalbet page count, and ledger/audit/raw
paths. The prior honest sandbox receipts remain in
`localdata/remine_audit_2026-10-02.jsonl`; relay pages are not treated as raw
bytes and are never used for runner backfill.

## Executive supersession — current-source re-mine, 19 October 2026

The operator directed moving on from Forebet-led electorates and re-mining all
supported markets. This is implemented **inside `scripts/mine_consensus.py`**,
not as a second miner, pipeline, registry or backfill program. The preceding B0/B1
network budgets remain unchanged: this re-mine is local/cache-only and does not
authorize source crawling or paid API calls.

### What changed

The default entry point no longer fits the old Forebet pair/triple grid or
re-trains the Forebet-feature meta-model. Historical statistical/ML helpers are
retained because frozen-incumbent protection, tests and historical receipts use
them; they are not the new default scan.

The current scan:

- Excludes Forebet as a voter **and** result donor. It does not use the old
  Forebet-prioritized `results_donor` or inherited categorical settlement scores.
- Uses exact date + current `source_team_key` identities, not nine-character
  warehouse join keys. Repeated identical observations count once. Conflicting
  source predictions/kickoffs and conflicting result periods are quarantined.
- Tests every observed nonempty source subset, including single-source signals,
  unanimous subsets, strict-majority subsets, and following **each** source when
  the subset disagrees. Two-voter ties are not manufactured majorities. Another
  source disagreeing no longer prevents a smaller agreeing subset being tested.
- Scans the existing market registry: FT/HT 1X2, O/U 2.5, HT O/U 1.5 and 2.5,
  BTTS; also scans the enhancement totals lines 1.5, 3.5 and 4.5. Unsupported or
  unavailable probability/result fields show explicit zero coverage. FT scores
  cannot supply HT outcomes. Streak percentages and confidence tags are not
  treated as probabilities.
- Tests no probability floor plus 35–90% in five-point steps. Categorical tips
  can enter only the no-floor test. Both under/over and yes/no are evaluated.
- Uses the source's probability units, exact selected-side/market prices, the
  existing `stats`/`evaluate` functions and unchanged sample/ROI/Wilson gates.
  In addition, it requires at least the corresponding train/validation sample
  floor in **priced** observations; absent ROI and tiny priced subsamples do not
  pass a profitability check. Quote returns remain retrospective donor-price
  diagnostics, not execution-safe named-book ROI.

### Chronology and running it

```bash
PYTHONPATH=src python3 scripts/mine_consensus.py \
  --start 2026-06-13 --split 2026-09-21 --as-of 2026-10-19
```

`as-of` is exclusive, so the incomplete current day and future fixtures never
enter evaluation. The default split is 28 days before `as-of`. Invalid/inverted
windows and a pre-retirement training floor are rejected. The selected window
is recorded, not described as a newly established optimal split.

Output reuses `localdata/edges_consensus_research.json`; `--output` can direct a
read-only investigation elsewhere. It cannot target the operational registry.
The report retains weak candidate tests rather than filtering them out at the
old overlap floor, and distinguishes missing tables, missing era rows, unusable
signals, missing/conflicting results, sample holds and profitability holds.

For the existing Actions workflow, select **`remine_only`**. This restores the
existing production cache, rebuilds the existing warehouse offline (including
raw prediction tables whose own score may be absent), and runs this same miner.
It skips source capture, pricing, tickets, notifications, cache publication and
git-state publication. Existing artifact upload retains the report. A compact
check annotation records source/market coverage and test counts. There is no new
workflow or separate mining command implementation.

### Activation boundary — important

This is **re-mining, not automatic serving activation**. New single-source,
majority and dissent predicates cannot safely be stamped certified and sent to
a loader that only implements the former unanimous-voter contract. Every result
therefore remains `candidate`, with separate `statistical_gates_passed` and
`holds` fields. Each has `new_predicate_requires_serving_validation`; transient
DuckDB slices are not published as operational assay views.

The operational `edges_consensus.json`, frozen model, certification activation,
thresholds used by the picker and frozen slips remain unchanged. The default
miner no longer refreshes those legacy non-ML registry rows; existing decay and
assay steps still run on the operational registry. **The serving transition is
not complete:** validated new predicates must be wired identically into picking,
recreatable decay/assay views and pricing before replacing the old operating
thresholds. Searching thousands of thresholds against one validation window is
model selection, not untouched forward proof. No claim that 70/65 is optimal for
replacement sources is made.

### Local execution receipt

The local 19 October run found **zero post-retirement prediction rows** in this
checkout's CSV/warehouse inputs. It did find 28,748 independent BetExplorer result
rows. That is not enough to reconstruct missing predictions. The correct result
is `no_gradeable_prediction_history`, zero tested rules, not “all sources failed
validation.” Production Actions has a separate restored cache; its run must be
examined before reporting actual replacement-electorate performance. No provider
was called to fill the gap and no candidate was certified.

### Production execution and narrow follow-up — 20 October 2026

PR103 merged as `9a409c3`. Production full run
[39350936425](https://github.com/6ixtyn9-sudo/Edge-Factory/actions/runs/39350936425)
succeeded: **73,476 tested rules / 39 statistical passes**, with the independent
production regression **3,327 passed / 1 skipped**. This supersedes the earlier
local-only evidence gap, not the activation boundary. Existing operational steps
still use the legacy registry; the `auto` run also published operational state.

The follow-up fixes existing raw-versus-settled table preference so that raw
captures are not silently restricted to a legacy donor's settled subset, and
makes SoccerVista's tests deterministic across midnight without weakening its
production today-only guard. Local validation: **44 focused tests passed**;
**3,329 passed / 1 skipped** in the full suite. No threshold or serving activation
was changed. Full receipt and outstanding evidence/operational findings:
[`audits/POST-FOREBET-RUN-39350936425.md`](audits/POST-FOREBET-RUN-39350936425.md).
The research JSON itself remains uninspected because its artifact download
redirect is blocked; aggregate pass counts are not enough to choose a live rule.

### Artifact-free readout — follow-up on the active session branch

The operator cannot attach files here. The existing miner now appends a readable
passing-candidate table to `GITHUB_STEP_SUMMARY` and publishes the **full** passing
candidate records as numbered `Post-Forebet passing candidates` notice
annotations. They include each electorate, strategy, threshold, train/validation
and priced counts, hit/ROI/Wilson statistics, and remaining serving holds. The
existing metadata annotation now also retains source statuses, market coverage,
gates and limitations. Larger passing lists are batched below the annotation
size limit; a bounded summary table never removes records from the batches.
The original full research JSON and its artifact remain unchanged in purpose.

No workflow edit, separate miner, tracked research registry or activation was
introduced. This readout does not certify candidates or clear any holds. It is
available on branch `arena/e47b4655-edge-factory`; it is not on main until merged.
For an artifact-free production-data readout, manually run the **existing**
`daily.yml`, choose that branch, and select **`remine_only`**. This uses restored
cache data, skips provider captures/pricing/tickets/notifications and does not
publish cache or git state. Results are a fresh evaluation of the retained
cache, not recovery of the precise original 39-pass artifact.

The agent verified read access to the existing metadata notice at
`repos/6ixtyn9-sudo/Edge-Factory/check-runs/118394690889/annotations` through `gh api`.
For the new run, get check-run IDs from that run's check suite and read their
annotations (paginated) through the same API; reconstruct passing records from
numbered JSON batches. Do not ask the operator to download or attach the JSON.
Earlier manual workflow dispatch was denied; no new dispatch was attempted.

Validation: **49 focused tests passed** (4.50 seconds); **3,335 passed, 1 skipped**
(159.47 seconds) in the full suite. Coverage includes the actual main-entry-point
hook, multi-batch lossless records across 1X2/O/U/BTTS, empty passes, summary append,
workflow-command escaping, missing-summary fallback and unchanged input holds.

### Production correction — run 39371954018, 20 October

The run used code889da9e (after PR104), mode **official_morning**, not remine_only.
Production regression3335passed1skipped166.86s. Miner completed327.3s,73476tests /
39statistical passes; PredictZ now correctly selected2706raw captures. These
establish actual execution, not serving activation.

**The initial artifact-free transport was NOT lossless in production.** Both
notices in check-run118461574636 were truncated to exactly4096characters, not
the assumed64KiB. Short numeric configuration values masked as secrets also
replaced ordinary market/threshold/metric text with `***`, invalidating JSON.
The full39passing records have not been recovered. Do not repeat the preceding
claim that numbered notices alone already exposed every record successfully.

Follow-up inside the same miner: serialize only research data, compress using
stdlib zlib and encode as uppercase A-P hex. Split into2800-character fragments
inside small JSON envelopes; complete annotation lines are tested below3500bytes.
No environment values or credentials enter this transport. This avoids incidental
numeric-configuration masking of research metrics; missing fragments or damaged
encoded data must be rejected, not guessed. Human summary and existing JSON stay
readable and unchanged. Decode by grouping the annotation title before `fragment`,
checking chunk1..chunks completeness, concatenating data, translating A-P back to
0-f, then bytes.fromhex -> zlib.decompress -> json.loads. The outer passing batch
still contains part/parts and must also be checked for completeness.

Validation:50focused passed4.75s; full3336passed1skipped156.33s. Tests now simulate
the observed4096-character truncation and numeric masks, verify exact record
recovery, and reject incomplete/corrupted packets. This correction is NOT yet
observed in a runner. It requires no provider calls or full official rerun; the
existing cache-only mode is sufficient. No dispatch attempted in this follow-up.

## Operator-authorized serving migration — 20 October 2026 (PR105)

This supersedes the earlier **serving-deferred** boundary, not its evidence or
price-provenance warnings. The operator authorized connecting validated current
contracts to selection, pricing, assay and decay, with red-team testing and merge.

- The **existing miner** still searches the same subsets, strategies, markets,
  thresholds and train/validation gates. Its normal daily invocations now pass
  `--activate`; the existing workflow's `remine_only` command does **not**. Direct
  research runs remain non-operational unless explicitly given `--activate`.
- Shared predicate/observation code lives in `edgefactory.consensus_contracts`;
  it is not another miner, workflow, data store or registry. The live registry
  remains `localdata/edges_consensus.json` and purity remains
  `localdata/purity_registry.json`. Exact recipe IDs hash schema + market + sorted
  electorate + strategy + followed source + threshold. Labels cannot substitute
  for these structured fields. Historical source-count fallbacks are disabled
  once the registry declares `operating_contract: post_forebet_v1`, including
  when it has zero eligible contracts.
- Activation requires the unchanged 340/120 sample **and priced-sample** floors,
  train ROI >= -10%, validation ROI >= 0%, validation Wilson LB >= 50%, finite
  returns, and an exact recreation of both periods' complete reported statistics.
  A mismatch aborts before the atomic registry write. Missing incumbent state,
  missing completed-era history or zero passes preserve the existing registry;
  cold-cache emptiness is not proof that incumbents failed. No original 39-pass
  artifact is presumed recovered, and no list of 39 contracts is hardcoded.
- Same-day selection reads the existing warehouse captures with exact date and
  source-team identities, including categorical/no-floor contracts. Missing or
  conflicted electorate members cannot be substituted, and extra dissent outside
  the named subset cannot veto it. Singles, unanimity, strict-majority and each
  disagreement-follow predicate use the same projection as mining and audits.
  Identical predictions count once; repeated quote updates use conservative
  field-wise minimums, not whichever historical row happened to come last.
- Warehouse views retain **observed** kickoff/time, result provenance and explicit
  line/period prices rather than dropping them. O/U 1.5/3.5/4.5 and explicitly
  named HT prices remain separate from O/U 2.5 and FT prices. The live price index
  recognizes all nine canonical markets; no fuzzy period inference was added.
  HT and FT books cannot combine into a supposedly coherent three-way book.
  Missing HT/other-market historical prices still prevent certification.
- Every newly selected row starts **unpriced**. Historical donor quotes cannot
  become execution quotes. Existing enrichment, freshness, same-side/market,
  named-book, corroboration, price-quarantine and context-veto gates remain in
  force. No provider request or budget was added. Unsupported/unavailable live
  quotes remain unpriced, not inferred from another side, period or goals line.
- Assay/decay recreate the actual contract, not legacy Forebet views. Purity maps
  are scoped by exact contract **inside the existing purity registry**, including
  team contexts whose legacy keys lacked a rule dimension. New contracts cannot
  inherit other electorates' contexts or fuzzy-league matches. Purity denominators
  include priced observations only; unpriced predictions are not synthetic losses.
  The five-context-map return contract is also fixed on assay failure paths.
- Newly accepted contracts start WATCH, not HEALTHY. Activation is not backdated
  by a historical `--as-of`. Decay uses only completed observations on/after the
  original activation date, excluding the searched validation baseline. Fewer
  than the existing minimum recent **priced** observations cannot earn HEALTHY.
  Revalidation keeps incumbents' original baseline, activation date, decay and
  bench. An existing bench cannot be reset by re-running the threshold search.
  Frozen ML payload/rules are preserved verbatim; this does not reactivate ML.
- Current-contract selection retains fixture-decision audit reconciliation across
  the full surviving-source roster. Legacy Forebet profile text is not attached
  as if it explained the new certification. Broader enhancement competition stays
  ON and its existing parent, price, probability and veto requirements remain.

Red-team receipt: **87 focused tests passed** (17.99s), including real-sized
synthetic 340/120 datasets, all nine price-index identities, wrong-side/line/period
refusal, forged stats, missing/conflicting votes, minority-follow semantics,
immutable benches, forward-only decay, unpriced-forward health refusal, scoped
assay, historical activation boundaries and row-order-invariant duplicate prices.
These synthetic tests are engineering evidence, not production betting returns.
Final full-suite/merge receipt follows below. The earlier production 39 passes
were on an older price projection; exposing already captured line prices and
stricter timing quarantine can change a fresh run's counts legitimately.

Deployment is effective on a run **executing the merged code with restored
prediction history**. Merge does not change an already running job's checkout,
rebuild an already frozen morning slip, recover the old artifact, prove 75% is
optimal, or guarantee a new pushed bet. The original official-morning run is
already complete; no duplicate full run or paid capture was dispatched here.

Final local validation on the complete migration: **3,381 passed, 1 skipped** in
162.35s; focused **87 passed** in17.99s; additional pricing/normalization/coherent-
book/warehouse regression selection **58 passed** in0.67s. `git diff --check` clean.
No tracked `localdata/` file changed. Runner activation remains unobserved until
an existing daily mode executes the merged code; no dispatch was attempted.

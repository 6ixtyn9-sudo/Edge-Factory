# Feature & Data Audit — 2026-10-10

Workstream B deliverable: inventory of the features that feed (or could feed)
pre-match models, the leakage/availability findings, and the first offline
baseline experiment. Companion artifacts:

* `scripts/research_beyond_consensus.py` — dataset builder + experiment (READ-ONLY
  on operations; writes only under `research/`).
* `research/beyond_consensus_dataset.csv.gz` — fixture-level panel
  (16,286 rows; generation command + provenance + schema + content hash in
  `research/beyond_consensus_manifest.json`).
* `research/beyond_consensus_results.json`, `research/beyond_consensus_report.md` — metrics.

Nothing in this document changes an operational output. No model was
activated; no selection threshold, staking rule, or price-matching rule was
touched.

> **Corrections (2026-10-10, post-review).** (1) An earlier draft claimed
> `goalsavg` was "verified prematch" from distribution statistics. That was
> wrong: non-integer values, 815 distinct values, corr 0.213 with actual
> totals and 1.45% exact equality only show `goalsavg` is not the final goal
> total — they say nothing about WHEN it was available or whether it was
> revised afterwards. The provenance trace (§2, forebet extras row) shows the
> field is read off the same day-page fetch as the final scores, with no
> ingest timestamp retained: pre-kickoff availability is NOT demonstrable,
> and the extras ablation has been moved out of the strict experiment (§3.2).
> (2) "Test window evaluated once" is now stated precisely: the window HAS
> been inspected under the final spec; no feature or modelling choice changed
> after results were seen, with one documented correctness-bug exception
> (§3.4); because the archives end 2026-06-12, no later in-archive window
> exists to reserve (§3.4).

---

## 1. Headline finding: the prediction archives are historical-only

All three committed prediction archives **stop at 2026-06-12** (0 rows after):

| archive | rows | span | carried fields |
| --- | --- | --- | --- |
| `localdata/statarea.csv.gz` | 489,399 | 2017-01-01 → 2026-06-12 | p1/px/p2, HT probs (p1_ht/px_ht/p2_ht), o/u probs, final scores |
| `localdata/forebet.csv.gz` | 327,895 | 2024-01-01 → 2026-06-12 | p1/px/p2, provider-average 1x2 odds, extras (goalsavg, pred score, o/u, gg/ng, kelly), final scores |
| `localdata/zulubet.csv.gz` | 67,216 | 2024-01-01 → 2026-06-12 | p1/px/p2, tip odds, final scores |

Consequences:

1. **Live `fb_p` misses are structural, not a pipeline defect.** Any live-path
   gap in `fb_p` / `zb_p` / `sa_p` after 2026-06-12 is a source-availability
   fact. The standing instruction holds: do **not** relabel another provider as
   Forebet to fill `fb_p`. Live inference currently substitutes stored fallback
   means for missing `fb_p` (sometimes `zb_p`/`sa_p`) — that is a *degraded
   mode*, and its outputs must not be presented as Forebet-calibrated.
2. **Outcomes outlive features.** BetExplorer results continue to 2026-09-01
   (107,724 rows), so settlement/backfill remains possible — but the *features*
   end 2026-06-12. Live-era model validation on current fixtures cannot use
   these three sources at all; it must be a separate, quota-bounded exercise on
   timestamped named-book prices (The Odds API 2026-08-03→10-10: 13,627 rows /
   186 fixtures; OddsPapi only 10-03→10-04).
3. **Certified historical ROI ≠ current live performance.** The certified edges
   were mined on windows where all sources were alive. With two of three
   sources structurally dark, live inputs differ in *distribution*, not just
   completeness, from the certification inputs. Historical certification does
   not transfer.

## 2. Feature inventory (definition, coverage, availability, leakage)

Scale note first: the warehouse stores source probabilities as **percent
0–100**; the live serve path rescales (`np.where(>1.5, /100)`, fix dated
2026-08-10). `avg_p` therefore has **different calibration meaning across
paths**: in multi-source (`n_way≥3`) cohorts it is a trio mean; in 2-way
cohorts it is a pair mean of a different provider mix; percent-era rows and
fraction-era rows sit in the same table. Any consumer must bucket by era and
path before comparing.

| feature | definition + units | source | historical coverage | live availability | availability timestamp | missingness | leakage risk | train/live semantic agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fb_p` (p1/px/p2) | Forebet 1x2 probabilities, %→0-1 | forebet.com scrape | 2024-01→2026-06-12, 327,895 rows, ~97-98% with final scores | **none since 2026-06-12**; fallback mean substituted | none at source (daily scrape, no intraday time) | live: structural after archive end | none (prematch) | **broken** — live sees means, not Forebet's distribution |
| `zb_p` | Zulubet 1x2 probabilities | zulubet.com scrape | 2024-01→2026-06-12, 67,216 rows | none since 2026-06-12 | none | live: structural | none | broken (as above) |
| `sa_p` | Statarea 1x2 probabilities | statarea.com scrape | 2017-01→2026-06-12, 489,399 rows | none since 2026-06-12 | none | live: structural | none | broken (as above) |
| `avg_p` / `min_p` / `std_p` | mean / min / std of *available* source probs, 0-1 after scale fix | derived | full archive span | derived at serve from whatever sources answered | none | inherits source gaps | none | partial — source mix differs live (dark sources) vs train |
| `pick_odds` | price attached to the pick | varies by lane | archive era: provider-average/tip odds | lane-dependent (The Odds API named-book; BetBetter **fair**, bookmaker=None) | live lanes carry capture timestamps; archive era has none | high where lanes dark | price provenance: **fair prices are not executable quotes**; provider-average rows are never execution-eligible | broken by design |
| `is_home` / `is_away` | selection side one-hot | derived | full | yes | n/a | none | none | OK |
| `cat_friendly/youth/women/cup/league` | competition class incl. squad-marker folds (u17–u25/reserve/women) | identity module | full | yes | n/a | none | none after 2026-10-10 squad-marker veto (width-9 fold collision fixed) | OK |
| `rolling_hit_rate` | 14-day rolling pick correctness | derived (consensus3) | full archive span | `get_rolling_hit_rate_last_14d`: share of `fb_pick==outcome` over prior 14 days; fallback 0.75 | computed at serve from settled rows | low after settlement | none: train version is day-lagged `shift(1)` | **mismatch** — train = majority-pick consensus correctness; live = `fb_pick` correctness only; fallback 0.75 in both paths |
| `ht_p` (forebet), `sa_ht_p` (statarea p1_ht/px_ht/p2_ht) | **pre-match** half-time outcome probabilities | forebet / statarea archives | archive span | none since 2026-06-12 | none | structural live | **no leakage — these are published-before-kickoff HT probabilities, not HT scores** | broken (dark source) |
| `ht_diff` / `ht_total` | **actual** half-time score margin / total | results join | archive span | n/a | n/a | n/a | **LEAKS if used pre-match** — **dropped** from `mine_consensus` feature_cols (diagnosis_no_autobets_2026-10-06 §3.2 fix #6); pinned at serve via `FROZEN_FEATURE_COLS` / checkpoint ⑫ | n/a (excluded) |
| forebet extras: `goalsavg`, `p_over/p_under`, `p_gg/p_ng`, kelly, `pred_hs/pred_gs` | provider estimates (goals, O/U 2.5, BTTS, kelly stake, predicted score) | forebet archive, over/under + BTTS market endpoints | 2024-01→2026-06-12 | none since 2026-06-12 | **none retained** — see below | none within archive era (0% missing in panel) | **availability NOT demonstrable**: `fetch_day(date)` reads `goalsavg` and the final scores (`Host_SC`/`Guest_SC`) off the SAME day-page fetch (merged by match id, `src/edgefactory/sources/forebet.py`), so the capture necessarily ran post-match for scores to be filled; the archive carries no ingest timestamp and Forebet's intraday revision behaviour is unobserved. Distribution stats (93.2% non-integer, corr 0.213, 1.45% exact equality) prove only that it is not the final total. **Excluded from the strict experiment; exploratory only.** | unproven |
| "Realized Stats on Home/Away Win" | cohort avg rates **conditioned on `outcome == pick`** (consensus3 ⋈ forebet_settled, avg_p ±5 band, n≥5) | warehouse query | full | displayed at serve (`fetch_historical_profile`; hybrid `fetch_match_cohort` = same minus outcome filter) | computed at serve | n/a | **outcome-conditioned — NOT a pre-match forecast**; must stay display-only and never enter a feature vector | n/a (display-only) |
| phase5 K features | 22 BASE_FEATURES + per declared source {vitibet,bzzoiro,betclan,scoutingstats,betminer} `{src}_p`,`{src}_available` = 32 cols | mixed live lanes | per-lane capture | partial (bzzoiro 403s; betminer provider-404; betclan can_vote; scoutingstats can_vote) | per-capture receipts | dark source → `_available=0` + era-train mean (never silent zero) | none found in construction | degraded where lanes dark |

Train/live mismatches called out, unchanged from the standing concerns:
fallback-mean substitution for dark sources; `avg_p` scale/path semantics;
`rolling_hit_rate` train≠live definition; outcome-conditioned "Realized Stats";
historical certification ≠ live performance.

## 3. Baseline experiment (offline, no operational output touched)

Design: fixture-level panel = forebet ∩ zulubet ∩ statarea on
`date + source_team_key` (identity-folded), one row per fixture, outcome known.
Splits frozen **chronologically**, disjoint on fixtures:
train 2024-01-01→2025-05-31 (10,539) / validation 2025-06-01→2025-12-31
(3,224) / test 2026-01-01→2026-06-12 (2,523). Everything data-driven is fitted
on train only: `StandardScaler`, all logistic fits, extras medians, league
draw/home rates (empirical-Bayes shrinkage k=50 toward train globals);
ablation temperatures are fitted on the validation window only; the
consensus-baseline temperature (0.8413) on train only. The script asserts the
contract at runtime (`_leakage_guards`: split disjointness, forbidden-column
exclusion — `outcome`/`consensus_pick`/`consensus_hit`/predicted-score columns
never enter a design matrix — and finite design matrices).

Ablations are tiered:

* **Strict** (evidence-backed features only): consensus_only, +balance,
  +market, +market+balance.
* **Exploratory** (quarantined): +forebet extras. Provenance (§2) shows the
  extras share a capture with the final scores and carry no ingest timestamp;
  pre-kickoff availability is not demonstrable, so this tier is reported
  separately and is ineligible for promotion decisions.

Panel coverage is a real constraint: 16,286 trio-complete fixtures = **5.0%**
of Forebet's 2024+ outcome-known rows (the zulubet archive bounds the join).
96.2% of panel rows have a valid three-way market baseline. Within the panel,
Forebet extras are 0% missing, so *missingness-as-information could not be
tested here* (the `fb_extras_missing` feature is constant 0).

### 3.1 Results — strict tier (test period)

| model | n | logloss | Brier | acc | mean p(draw) | realized draw rate |
| --- | --- | --- | --- | --- | --- | --- |
| market_provider_average (devigged Forebet odds) | 2,493 | **0.9702** | **0.5781** | 0.529 | 0.2649 | 0.2627 |
| consensus_mean (T=0.8413, train-fitted) | 2,523 | 0.9977 | 0.5954 | 0.512 | 0.2904 | 0.2628 |
| consensus_only LR (T=0.9182, val-fitted) | 2,523 | 0.9925 | 0.5927 | 0.520 | 0.2531 | 0.2628 |
| consensus+balance | 2,523 | 0.9952 | 0.5941 | 0.516 | 0.2690 | 0.2628 |
| consensus+market | 2,493 | 0.9716 | 0.5791 | 0.529 | 0.2622 | 0.2627 |
| consensus+market+balance | 2,493 | 0.9766 | 0.5822 | 0.517 | 0.2740 | 0.2627 |

Exploratory tier (quarantined — see above; transparency only):
consensus+market+balance+extras n=2,493, logloss 0.9770, Brier 0.5825,
acc 0.518, mean p(draw) 0.2736.

Test-period logloss deltas vs references. Every delta is **paired row-for-row**:
model and reference are evaluated on the identical fixture frame (for
market-containing models, the same mkt_valid subset — the headline table's
differing n, 2,493 vs 2,523, reflects that restriction and NOT an unpaired
comparison; `paired_n` is reported per delta). Date-clustered bootstrap 95% CI,
2,000 resamples, seed 42; negative = better:

| model | paired n | Δ vs consensus_mean | 95% CI | Δ vs market | 95% CI |
| --- | --- | --- | --- | --- | --- |
| consensus_only | 2,523 | −0.0052 | [−0.0111, +0.0005] | — | — |
| consensus+balance | 2,523 | −0.0026 | [−0.0100, +0.0052] | — | — |
| consensus+market | 2,493 | −0.0267 | [−0.0356, −0.0177] | +0.0013 | [−0.0021, +0.0048] |
| consensus+market+balance | 2,493 | −0.0217 | [−0.0305, −0.0127] | +0.0064 | [−0.0003, +0.0129] |
| *(exploratory)* +extras | 2,493 | −0.0213 | [−0.0302, −0.0123] | +0.0068 | [+0.0003, +0.0133] |

Context (descriptive, unfitted): test-period top-pick hit rates —
statarea 0.5176, trio_mean 0.5117, zulubet 0.4907, forebet 0.4546.

### 3.2 Reading — a defensible negative result

1. **Nothing beats the market baseline.** Every strict model containing market
   features is statistically indistinguishable from (or significantly *worse*
   than) the devigged provider-average odds on test logloss. In the
   quarantined exploratory tier the extras group is significantly worse
   (+0.0068, CI excludes 0 in the wrong direction) — reported, not promoted.
   And this "market" is Forebet's *provider-average* price — a soft proxy;
   true named-book lines would likely be sharper, raising the bar further.
2. **Consensus adds nothing beyond market.** The trio mean's advantage over
   raw consensus (−0.0267 vs consensus_mean) disappears once market
   probabilities are in the design. The fitted consensus-only LR is not
   significantly better than the simple tempered mean (CI includes 0).
3. **Draw propensity / strength-balance features do not help** (+0.0064 vs
   market, borderline-negative). Draw calibration is roughly honest everywhere
   (mean p(draw) 0.253–0.290 vs realized 0.2628) — the calibrated trio mean
   *overstates* draws (0.2904), the LR slightly understates them (0.2531).
4. **Per-source pick quality is heterogeneous and the trio mean is not the
   best picker** on the test window (statarea alone ≥ trio mean). Provider
   disagreement (`std_p`, `draw_spread`) carried no incremental signal here.
5. Per the work order: **no ROI is reported anywhere** — this window has no
   timestamped named-book prices, and provider-average/fair prices are not
   executable quotes. There is accordingly **no promotion candidate** from
   this experiment; the incumbent operational model is untouched.

### 3.3 Limitations and checks not yet completed

* **Coverage**: the trio-complete join discards 95% of Forebet rows; results
  speak for the intersection (biased toward popular leagues), not any single
  source's full slate.
* **Validation double-duty**: the validation window fits ablation temperatures
  *and* screens models. Mild optimism possible in validation metrics; see
  §3.4 for the exact freeze/inspection relationship of the test window.
* **Bootstrap unit**: date-clustered resampling handles same-day correlation;
  it does not model longer-range season/league clustering. Paired deltas are
  exactly paired (identical rows both sides); the market restriction to
  mkt_valid rows means market-vs-model deltas exclude the 30/2,523 test
  fixtures with invalid three-way odds.
* **Linear balance terms only**; no interactions, no per-league models.
* Not yet done: per-league breakdowns; live-era replication on timestamped
  named-book prices (quota-bounded; The Odds API only, 186 fixtures —
  underpowered for logloss, marginal for calibration curves); rolling/xG,
  rest-days/congestion, lineups feature groups (no retained historical
  coverage meeting the availability-timestamp bar — see §2 inventory; do not
  backfill silently); draw-specific CalibratorH/T-style recalibration on the
  operational path.

### 3.4 Specification freeze vs test inspection (exact record)

1. Splits, feature groups, fitting rules, and baselines were written into
   `scripts/research_beyond_consensus.py` **before** the first successful
   evaluation run; no metric had been observed when they were fixed.
2. The first successful run exposed a **correctness bug** (sklearn's
   alphabetical class order misaligned every probability matrix; accuracy
   ~0.21 on ALL splits — the symptom was itself the diagnosis, visible on
   train/validation without reference to test). The fix reorders model output
   columns; it changed no feature, split, or fitting rule. Pre-fix metrics
   are invalid and discarded.
3. After the corrected run, additions were **reporting-only**: paired
   bootstrap CIs, per-source context, the manifest, and the strict/exploratory
   tier split of an ablation that already existed (the extras group's
   quarantine reflects a provenance finding, not its test performance — the
   extras numbers did not change: logloss 0.9770 before and after the
   restructure).
4. Honest status of the test window: it **has been inspected** under the
   final spec. No feature, threshold, or fitting choice was changed after
   test results were seen, so the numbers above are a valid untouched-window
   evaluation *of this specification* — but the window is now burned for any
   future spec change. Because the archives end 2026-06-12, **no later
   in-archive window exists to reserve**: any further modelling iteration
   makes this test period development evidence, and final validation must
   then move to live-era data (quota-bounded).

## 4. Constraint compliance

* Ops untouched: script writes only `research/*`; verified zero writes to
  `localdata/` during test and experiment runs (byte+mtime manifest diffs).
* No Forebet relabeling; no HT-score features in any design matrix
  (machine-checked); no relaxation of identity/matching/price rules.
* The six consensus-contract test failures remain visible and unfixed-by-side-
  effect (min probability, home-only selection, exclusive upper odds bound,
  substitute-source label inheritance ×2); their effect on baseline validity:
  the research panel is built from *raw archive probabilities*, not the
  operational consensus pipeline, so none of those selection-contract gaps
  contaminate the experiment — but they do mean the *operational* consensus
  artifact is not yet equivalent to the consensus baseline studied here.

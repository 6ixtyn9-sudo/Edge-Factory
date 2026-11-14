# NEXT-AGENT BRIEF — ML AUDIT & DRAW-PROOFING (2026-10-07)

Companion to `docs/operator/NEXT-AGENT-BRIEF-DRAW-MINING-2026-10-07.md` (the
draw-value rule mission). Two missions below, both operator-approved on
2026-10-07. Neither may move a threshold; both exist to produce the finding
that would license one.

Operator's words that scope this work: *"if it works, it's a small price to pay
for something that will compound, and if it doesn't, we can always revert...
just make sure the commit comments are clearly described."* That is a
requirement, not a preference — see COMMIT HYGIENE.

**Line anchors are perishable — the landmark wins.** Anchors are `file:line`
plus a searchable landmark; several drifted while this brief was written. If
the number and the landmark disagree, re-resolve by search and treat the
disagreement as drift, not as a contradiction.

---

# GO — operator authorisation (2026-10-07)

> **GO — begin the brief work (operator authorisation, 2026-10-07).** You are
> the execution session. Continue on branch `arena/438d7dd2-edge-factory` — it
> carries all three briefs, their target docs, and the data. Read the three
> briefs first; their premises are refute-first.

**Step 0 — refresh anchors.** This execution remains on
`arena/438d7dd2-edge-factory`. The two authorized T2 result rows are in
`d60f729`; the exact-key alias-precedence code/test correction is in follow-up
commit `3b5d7ee`. Line numbers, main-tip hashes, and old run IDs are perishable:
inspect the checked-out artifact and use landmarks, not stale anchors. Keep
source generations separate: the settled overlay's latest date and the research
ledger's latest date differ (see FINDINGS §7); do not treat them as one run or
infer archive coverage from overlay rows.

**Step 1 — price decision (re-derived 2026-10-07).** A1/A2/A3 are
**BLOCKED on committed data**. The three committed TheOddsAPI monthly files
cover 156 1x2 fixtures but match only **16/174 ACCA legs (9.2%)** on the
same-date §4-normalized fixture key. BetExplorer odds end 2026-06-16;
OddsPAPI matches only 2/174 legs on 2026-10-03–10-04; five CLV files (8,498
rows) have exact per-pick keys for 174/174 legs, but only a selected price—not
all 1X2 outcomes. Pick archives also carry only the selected price. Do **not** replay DNB/DC/±0.25 on that 9.2% subset as a
verdict. No capture, vendor call, or new source is authorized. A1/A2/A3 remain
blocked-pending-capture; Forebet stays parked.

**Step 2 — Decision 2 (authorized, executed).** The only permitted settlement
writes are the two `source_verified` rows already in `Config/verified_results.json`
and committed at `d60f729`: 2026-06-07 Tochigi SC–Giravanz Kitakyushu, 1-1
draw at 90'; and 2026-08-01 Samgurali–Meshakhte Tkibuli, 0-0 draw at 90'.
Do not duplicate, remove, or extend those rows. T2 verification exposed an
exact-key alias that survived the entry purge; its precedence fix and regression
test are in follow-up commit `3b5d7ee` and documented in FINDINGS §6–7. The
90-minute convention is not encoded by that fix. Kladno remains frozen and
human-owned.

**Step 3 — T3–T6, flag-axis audit.** Identify the price-only
`draw_risk_flag` producer and its inputs; remeasure calibration on the explicit
archive indexes with duplicate/conflict handling; prove structurally whether
ACCA construction reads the flag; then run an EXTREME-only, walk-forward
counterfactual at the archived stake schedule. The result is finding-only: no
construction change. Do not select an arbitrary value for a conflicting
fixture.

**Step 4 — T7, B1 calibration.** Fit Platt on a held-out calibration slice,
score on a later held-out slice, report the reliability curve and Brier, and
identify every pick crossing a certified threshold band. FINDINGS §7 records
the serving-time feature contract and the exact mover appendix.

**Step 5 — T8, B2–B5.** Continue only as scope and data allow. Any ablation,
scaling, hyperparameter, or model-class comparison is research-only; it must
not update the registry or change a certified threshold. B4 requires a
committed-history inventory before any capture plan is considered.

**Step 6 — T9 and delivery.** Record same-file parallel-edit and unsafe-glob
hazards in the existing findings doc. Serialize edits to a shared file and
reread/diff it after each edit; never issue parallel writes to the same file.

**T6 / §8.3 review status.** A repository-wide search found no literal §8.3
text or licensing clause, and the clause text is not present in the current
execution record. Do not infer omitted cell-size/volume thresholds, claim a
formal pass/fail, or retrofit a bar to the measurements. FINDINGS §7 reports
the observed Newcombe intervals and same-schedule P&L/stake-volume results,
but their clause-by-clause mapping remains blocked until the exact §8.3 text
is available. No filter, floor, threshold, or construction change is made.

**Fences (unchanged).** Findings first: no threshold, floor, gate, cap,
quorum, veto, stake, bank, ACCA-construction, emission, or registry change.
`MIN_LEG_ODDS` stays 1.20. No other `verified_results.json` row is authorized.
No new sources, vendor calls, capture, or replay on the 9.2% subset. Forebet
is PARKED (no capture test, no proxy).

**Delivery.** One commit per change, message naming what changed and what it
invalidates; no backticks in commit messages; never force-push; push to the
branch; PR only if your GitHub access allows. **Report** against each
pre-registered bar (one sentence each), `n` on every cell, suite count with
baseline named (2395, floor 1534), and what you did NOT do and why.

---

# MISSION A — DRAW-PROOFING REPLAY (the ACCA complaint)

## AMENDMENT (2026-10-07) — Mission A re-scoped after the feasibility check

**A1, A2 and A3 are BLOCKED on committed data.** The only committed feed
reaching the ACCA window, `localdata/theoddsapi_odds_2026-08/09/10.csv.gz`,
matches **16 of 174 legs (9.2%)** — verified by same-date joins on home/away
normalized exactly as §4 (NFKD, combining-mark removal, `&`→`and`, period
removal, whitespace collapse/strip, casefold). No committed source carries
the complete window of 1x2 triples: `betexplorer_odds_*` (the one with `odd1/oddx/odd2`) ends 2026-06-16;
`oddspapi_odds` covers 2026-10-03 → 2026-10-04 only; `clv_snapshots_*` is
per-pick (`observed_odds`, `implied_prob`, keyed on `match_date`), not the
triple; `picks_*.json` carries the pick's price only. The feed itself is
sound — 156 fixtures, 26 bookmakers, every fixture a full home/draw/away
triple, markets `1x2` (9,129 rows) / `ou_2.5` / `ou_3.5`, no DNB or DC
market — it simply does not cover these legs. **Do not** run a DNB/DC/±0.25
replay on the 9% subset and call it a verdict. Record A1/A2/A3 as
blocked-pending-capture; capturing triples for ACCA legs is a scope change
and the operator's decision.

**Final flag-axis rerun (T3–T6; full evidence and basis in FINDINGS §7).**
The producer is a deterministic `market` + `odds` band, not a model score.
`picks_2026-*.json` (113 files/1,747 rows) and
`picks_morning_2026-*.json` (75/1,116) are separate archive globs; their
188-file/2,863-row union is the analysis index. `picks_2*.json` is the
regular archive only; it does not include morning files. Against 174 slip
legs, the regular-only same-date/§4-normalized/side index has 172 matches,
1 flag conflict and 2 unmatched; morning-only has 124 matches, 0 conflicts
and 50 unmatched; the explicit union has 173 matches, 33 conflicts and 1
unmatched. No conflicting flag is selected arbitrarily.

Outcome rates use only legs with a unique same-date result and exactly one
explicit flag value (118 legs): EXTREME 7/28 (25.0%), HIGH 8/66 (12.1%),
MEDIUM 1/15 (6.7%), LOW 2/9 (22.2%). In the walk-forward split
`date < 2026-09-16` / `date >= 2026-09-16`, EXTREME−HIGH is +1.1pp
(2/13 vs 6/42; 95% Newcombe CI −16.4pp to +29.0pp) early and +25.0pp
(5/15 vs 2/24; CI −0.23pp to +50.67pp) late; both intervals include zero.
The 17 draw-killed legs inside the 64 fully outcome-joined ACCAs have flags
EXTREME 5, HIGH 7, MEDIUM 1, LOW 1, plus **3 conflicting** (not assigned).

The all-outcome-complete baseline is 64 ACCAs (40 wins/24 losses), stake
748.80, return 840.43, net +91.63. The valid flag-paired comparison is only
41 ACCAs because conflicts/unmatched flags are excluded: as-bet +73.64;
dropping any ACCA with an EXTREME leg leaves 25 ACCAs, retains 54.2% of its
stake, and returns +47.39. Late-half paired P&L is +42.38→+6.68 with
46.5% stake retained; exact measurements and the exact-price sensitivity are
in FINDINGS §7. The literal §8.3 clauses are unavailable in this checkout, so
these are observed diagnostics only, not a formal bar pass/fail. No threshold
or construction change follows.

**T3/T5 structural result.** `draw_risk_flag` and `recommended_market` are
not read on the reachable `auto_tickets.cmd_today` call path (AST call-graph
scan: zero watched-field reads); runtime changes to both fields leave the
`playable_legs` pool identical. The flag is diagnostic/display-only today.
Full producer boundaries, call-path details, conflict fixtures, stake
counterfactuals, and the no-bootstrap/small-sample limitation are preserved
in FINDINGS §7.

## Why it exists (measured 2026-10-07)

Method, so it can be reproduced exactly: parse all 40 slips in
`localdata/auto_tickets_2*.txt`; join each leg to `localdata/settled_results.json`
on the same date using only the §4 normalizer: NFKD; drop combining marks;
replace `&` with `and`; remove periods; collapse and strip whitespace; casefold.
No fuzzy, reschedule, alias, or `canonical_team` join. Same-date only; coverage
is a lower bound. The settlement index has **64,849 rows (n=64,849), 64,815
normalized fixture-date groups, 34 duplicate groups, and 0 groups with
conflicting outcomes**. No donor outcome was selected arbitrarily.

Measured (40 slip files, **2026-08-27 → 2026-10-06**; 2026-09-30 had no slip):

- 87 ACCAs (n=87), all two-leg; 174 legs (n=174).
- **148/174 legs joined (85.1%); 26/174 unmatched.**
- **64/87 ACCAs fully joined: 40 wins, 24 losses.** Archived stake schedule:
  748.80 staked, 840.43 returned, **+91.63 net** across these 64 only.
- **17/24 losing ACCAs** contained a draw; **16/24** would have won if each
  drawn leg were voided. There were 17 draw-killed ACCAs and 9 other leg
  failures, so draws were 17/26 (65.4%) of failed legs.
- Joined-leg pick hit rate: **115/148 (77.7%)**; 22/148 outcomes were draws.
  The naïve independent-leg square is 60.4%, versus 40/64 (62.5%) observed
  ACCA wins; descriptive only, not an independence test.
- **0/174 slip legs were DRAW selections.**
- Settlement-state cross-check: 54 fully joined ACCAs matched on same date and
  combined odds; 54/54 outcomes agree, 0 disagree. The state history has 86
  ACCAs (51 wins/35 losses) over 40 bet days; it is a different denominator.

Draw concentration across joined legs (n=148; 22 draws):

| ticket odds band (left-closed, right-open; last right-closed) | n | draws | draw rate |
|---|---:|---:|---:|
| [1.00, 1.25) | 28 | 3 | 10.7% |
| [1.25, 1.45) | 73 | 5 | 6.8% |
| [1.45, 1.70) | 40 | 12 | 30.0% |
| [1.70, 2.10) | 6 | 2 | 33.3% |
| [2.10, ∞] | 1 | 0 | 0.0% |

| stated confidence band (left-closed, right-open; final includes 100) | n | draws | draw rate |
|---|---:|---:|---:|
| [0, 60) | 7 | 2 | 28.6% |
| [60, 68) | 45 | 11 | 24.4% |
| [68, 75) | 62 | 5 | 8.1% |
| [75, 100] | 34 | 4 | 11.8% |

**Direction, not proof:** 22 draws, in-sample on the archived window. Longer
odds are less certain, so the price-band association is confounded with the
market. This result-only analysis is not a pricing replay and does not change
Task A1/A2/A3's blocked status.

## Task A1 — price every draw-handling market exactly **[BLOCKED — see AMENDMENT: the feed below matches 16 of 174 legs (9.2%)]**
DNB is not the only one. **Price-source record (verified 2026-10-07): the
committed prediction histories end 2026-06-12** (`forebet.csv.gz` 327,866
clean rows, `zulubet.csv.gz` 67,187, `statarea.csv.gz` 489,286 — all ending
the same day; skip their repeated header rows where `date == 'date'`). They
predate the ACCA window (2026-08-27 → 2026-10-06) and cannot price it. The
only committed feed reaching the window is
`localdata/theoddsapi_odds_2026-08/09/10.csv.gz` (2026-08-03 → 2026-10-07;
156 1x2 fixtures, 26 bookmakers, full home/draw/away triples) — **but it
matches only 16 of 174 legs (9.2%)**. Nothing committed prices the window's
triples. This task is blocked pending a capture decision (the operator's).
Derive, for every archived leg:

- **DNB / Asian 0.0** — void on draw; the ACCA collapses to its remaining legs.
- **Double Chance (1X / X2)** — WINS on the draw; the ACCA stays whole at a
  lower price.
- **Asian ±0.25** — split-stake partial cover, if derivable from the same
  columns.

Re-price every leg, recompute each ACCA's combined odds and payout under each
market, and A/B against the as-bet slips at the same stake schedule, same legs,
same days.

## Task A2 — the floor (measure; DO NOT change) **[BLOCKED pending the same capture — the per-market floor count needs the DNB/DC prices]**
`MIN_LEG_ODDS = 1.20` (`scripts/auto_tickets.py:193`) is global. Under DNB/DC,
short favourites collapse toward 1.02–1.10 and would fail it. Report how many
archived legs fall below 1.20 under each market, and in which price bands. The
operator's read — "the 1.2 min odds should not be global" — is a **hypothesis
to test**, not an instruction to edit. The count is what would license a
per-market floor.

## Task A3 — is the draw mispriced, or merely volatile? **[BLOCKED — see AMENDMENT]**
For each price band, compare the **realised** draw rate against the rate
implied by `oddx`. If realised ≫ implied, the draw is underpriced and
avoiding/covering those legs is +EV. If they match, the market is right and
only variance changes — draw-proofing is then a comfort blanket that costs
return. Answer it explicitly; it decides whether Mission A is a strategy.

## Pre-registered bar for Mission A
Recommend a draw-proofed construction as a **candidate** ONLY IF, over the same
archived window at the same stake schedule: total return ≥ the as-bet return,
AND the take-profit ladder is not delayed past the point where it changes
compounding. Otherwise the verdict is "measured, not adopted", and the report
says which clause failed.

---

# MISSION B — ML AUDIT (operator-approved)

## Premises (verified 2026-10-07 — REFUTE BEFORE BUILDING ON THEM)

- **26 registered features; only two are actual post-kickoff scores, and
  training/serving disagree on them.** The 2,258-row research ledger has
  `ml_ht_diff=0` and `ml_ht_total=0` on every row (live contract), but the
  historical `consensus3` training matrix has both half-time scores on
  18,473/18,478 rows; `ht_diff` is nonzero on 10,883 and `ht_total` on
  12,950. The registry coefficients are +0.245403 and +0.191982. These are
  not dead features: they are leakage-bearing train/serve mismatches. The
  guard in `picks_today.py` keeps bettable serving values at zero; no contract
  or registry change was made.
- **Other halftime-derived inputs are not all zero or all the same.**
  `ht_p` is derived from Forebet `p1_ht/px_ht/p2_ht`. Those three fields are
  null on all 18,478 `consensus3` rows, so historical `ht_p` is the 0.5
  fallback throughout. After excluding 29 repeated header rows, the raw
  Forebet archive has 0 non-null `p1_ht` values among 327,866 data rows. Live
  code can use the triplet if present; its current serving distribution is not
  established by this historical archive. `sa_ht_p` is derived from Statarea halftime
  forecast probabilities and is present on all 18,478 training rows; it is
  not an actual score, but its capture time is absent. Both are classified
  `revised` by `ML_META_FEATURE_AVAILABILITY`; do not zero them or call them
  verified pre-match without timestamp evidence.
- **No independent football data** — no Elo, form, lineups, xG, rest, weather,
  referee, H2H, or market movement. The only football-shaped inputs are the
  tipsters' own predicted-score / goals aggregates harvested into
  `consensus3`. It is a confirmatory meta-model over tipster consensus, not a
  match predictor.
- **Production still uses only** `LogisticRegression(max_iter=1000,
  random_state=42)` (`scripts/mine_consensus.py:610`). The one-off B3/B5
  scaler and RandomForest audits below were not saved in production code or
  added to the registry.
- **No production scaler or calibrator is registered.** This execution ran
  temporary Platt, scaling, ablation, and RandomForest comparisons for audit
  only; none is a deployment artifact and no threshold was changed.
- **The existing live-book and registry figures are not an apples-to-apples
  comparison.** Re-read state: 40 bet days (2026-08-27–2026-10-06), bank
  100→163.3557, 1,028.00% staked and 1,091.3559% returned; those 86 ACCAs
  are the ticket book, not solely `ml-meta`. The registry's `ml-meta avg_p>=55`
  valid row reports n=2,665 and ROI +33.23% at scraped odds. That historical
  registry view scores with actual halftime outcomes while serving pins
  `ht_diff/ht_total` to zero. Do not attribute the gap solely to execution
  price or use the registry ROI as serving-valid.
- **Source coverage — three prediction histories are committed; Vitibet is
  absent.** The warehouse vote inventory is forebet/zulubet/statarea on disk
  plus vitibet/bzzoiro/betclan/scoutingstats missing (seven listed voting
  sources). The live meta-model trains on `consensus3`, not a four-source
  view. Rechecked in this checkout: `consensus3` n=18,478
  (2024-01-01–2026-06-12), `consensus2` n=31,077; settled history tables
  forebet n=323,524, zulubet n=66,808, statarea n=481,537. No `vitibet`,
  `vitibet_settled`, or `consensus4` warehouse table; no Vitibet archive was
  present. The registered GATES require train n≥340, valid n≥120, overlap
  n≥200, recent n≥30, train ROI≥−0.10, valid ROI≥0.00. No capture or new
  source was authorized.

## T7 / B1 — serving-input calibration (completed; analysis only)

Source is `consensus3` (n=18,478; 2024-01-01–2026-06-12), using the stored
26-feature registry and the trainer's feature order. Deterministic split:
train date `<2025-06-01` (n=12,007), calibration
`2025-06-01 <= date < 2026-01-01` (n=3,536), test
`2026-01-01 <= date <= 2026-06-12` (n=2,935). The test and calibration
inference zero `ht_diff` and `ht_total`, as serving does; historical training
still has the actual halftime values, which is a material caveat, not a
cleanly retrained pre-match model.

On the n=2,935 test picks, raw served-input hit rate is 49.37%, raw mean
probability 43.56%, and Platt mean 50.70%. Platt is logistic regression on
`logit(p)`, C=1e6; calibration-slice slope=1.152245 and intercept=0.353607.
Test Brier improves **0.230467→0.226754**; logloss improves
**0.653057→0.644961**. No calibrator was registered.

Reliability by test probability bin `[lo, hi)` (final interval includes 1.0);
each cell is `n / mean predicted / observed hit rate`:

| probability bin | raw test | Platt test |
|---|---:|---:|
| [0.0, 0.1) | 0 / — / — | 0 / — / — |
| [0.1, 0.2) | 14 / 0.189 / 0.571 | 4 / 0.193 / 1.000 |
| [0.2, 0.3) | 388 / 0.266 / 0.302 | 153 / 0.269 / 0.275 |
| [0.3, 0.4) | 983 / 0.352 / 0.375 | 606 / 0.357 / 0.320 |
| [0.4, 0.5) | 690 / 0.445 / 0.522 | 821 / 0.447 / 0.428 |
| [0.5, 0.6) | 473 / 0.547 / 0.638 | 547 / 0.546 / 0.539 |
| [0.6, 0.7) | 276 / 0.646 / 0.714 | 442 / 0.647 / 0.661 |
| [0.7, 0.8) | 107 / 0.740 / 0.869 | 267 / 0.747 / 0.704 |
| [0.8, 0.9) | 4 / 0.818 / 0.750 | 95 / 0.834 / 0.874 |
| [0.9, 1.0] | 0 / — / — | 0 / — / — |

Certified probability bands use `<55`, `[55,60)`, `[60,65)`, `[65,80)`,
`>=80` on percentage scale. Raw/calibrated test counts are respectively
2,344/1,888; 204/243; 152/245; 231/464; 4/95 (n=2,935 in each column).
**903/2,935 (30.8%) picks move upward; none move down.** Crossings (overlap
by threshold): 456 at 55, 417 at 60, 324 at 65, 91 at 80. All identities and
old/new bands are in the [T7 threshold-mover CSV](ML-CALIBRATION-THRESHOLD-MOVERS-2026-10-07.csv)
(903 CSV records). This is a current served-input/unmatched calibration
sensitivity (frozen incumbent raw versus Platt), not a source-expansion
estimate; separate R2.2 candidate-versus-incumbent movers are in [the R2.2
CSV](ML-R2-2-SHADOW-MOVERS-2026-10-07.csv). Neither file authorizes a
certified-threshold move.

## T8 / B2 — halftime-score ablation (completed; not adopted)

Removing `ht_diff` and `ht_total` before candidate training improves test
Brier **0.230467→0.226203** and logloss **0.653057→0.643879**; mean absolute
probability shift is 5.82pp. The current registry gives those actual-score
features nonzero weights and serving sets them to zero. The improvement
supports an ablation candidate, not a production change: a new model key,
shadow comparison, and explicit operator authorization would still be needed.

## T8 / B3 — scaling/grid (completed; not adopted)

A small StandardScaler + logistic grid selected C=0.01, L2 on calibration
Brier (0.229642). At zeroed test inference, test Brier=0.230217 and
logloss=0.652502 versus the current served-input raw values 0.230467 and
0.653057: only −0.000250 Brier / −0.000555 logloss. Candidate training still
contains actual halftime scores, so this is not a clean new pre-match
contract. No scaling/model change was made.

## T8 / B4 — source coverage (blocked; inventory complete)

The current warehouse has no `vitibet`, `vitibet_settled`, or `consensus4`;
`consensus3` and the three settled-source tables are present (counts above).
B4 cannot be run on committed data. Existing GATES require train n>=340,
valid n>=120, overlap n>=200, recent n>=30, train ROI>=−0.10 and valid
ROI>=0.00; without Vitibet history, calendar accumulation time cannot be
estimated from this checkout. No capture, new source, or vendor call was made.

## T8 / B5 — RandomForest (completed; not adopted)

One fixed candidate (`n_estimators=400`, `max_features=sqrt`,
`min_samples_leaf=10`, `random_state=42`) used the same train/calibration/test
split and feature matrix. Test inference zeroed the two actual halftime-score
features; training did not, so note the same train/serve limitation. RF raw
Brier/logloss are 0.238244/0.669313; RF plus calibration-slice Platt are
0.234600/0.660776, both worse than current logistic served raw
0.230467/0.653057 and logistic Platt 0.226754/0.644961. It offers no
consistent improvement under the shared test/appraisal set. Full threshold
n/hit/odds/flat-ROI comparison is in FINDINGS §7. No RF code or registry
change was made.

## THE COST — state it in every proposal
The frozen serve-time contract exists to keep historical rows comparable. A
changed feature set or algorithm **invalidates comparability with every
settled row and every certified threshold calibrated on them**. Any change
therefore requires: a new `model_key`, a **shadow period** scoring old and new
side by side, and **no threshold movement until the shadow certifies**.
"Expensive but worth it if it works" is the operator's accepted position — but
the shadow protocol is what makes it revertible, so it is not optional.

---
# STANDING OPERATOR DECISIONS (not part of these missions — do not action)
Two decisions stay with the operator. Recorded here so they survive the
handoff:
1. **Decision 2 settlement rows — narrowly authorized and already written.**
   The two externally corroborated 90-minute draws are in
   `Config/verified_results.json` and commit `d60f729`: 2026-06-07 Tochigi SC v
   Giravanz Kitakyushu 1-1; 2026-08-01 Samgurali v Meshakhte Tkibuli 0-0.
   These two rows only. T2's alias-key precedence fix is part of the current
   work and is documented in FINDINGS §7; do not add or rewrite any other
   result. The 90-minute rule excludes extra time and penalties. The two
   Kladno rows (D) remain frozen and human-owned.
2. **forebet's fate — PARKED (operator, 2026-10-07).** No capture test, no
   proxy purchase, no forebet work of any kind until the operator has the
   capable machine. The resumption step, when the operator unparks it, is the
   same free test as before: run the forebet capture ONCE from the operator's
   own (home) IP. If it succeeds, the block is IP-based and a proxy — or
   simply running that one source locally — genuinely fixes it. If it still
   403s, the block is not IP-based and a proxy is wasted money. The resume
   path already exists and stays parked with it:
   `docs/operator/forebet-browser-diagnostic.yml.proposed` (unapplied — a
   workflow-dispatch diagnostic, not a fix). Context for whenever it resumes:
   forebet is a `backfill_donor` now and its staleness is visibility-only
   (the system runs without it), but it still supplies ~43% of the settled
   overlay (FINDINGS §1), so restoring the capture has real value. Routing
   around a block is a ToS and new-dependency decision — the operator's, not
   yours.

---

# COMMIT HYGIENE (operator requirement)

One commit per change. The message must name **what changed** and **what it
invalidates**, so any future agent can bisect the history and roll back to
2026-10-07. No backticks inside a `git commit -m` heredoc. Never force-push; on
non-fast-forward: fetch, confirm the remote holds the work, `reset --soft`,
re-commit forward. Never `git clean`, `git reset --hard`, or revert.

# HARD RULES

- Floors and thresholds measured, never guessed. No gate / floor / cap /
  quorum / veto / stale-days value moves in this work.
- No new vendors or sources; no raised call caps; no lowered intervals. No
  vendor network — prove contracts with MOCKED responses only. Never log
  request headers.
- Same-date joins use only the exact §4 normalizer: NFKD, drop combining
  marks, `&`→`and`, remove `.`, collapse/strip whitespace, casefold. No fuzzy,
  reschedule, alias, or `canonical_team` join; coverage is a lower bound.
  State the normalization and boundary convention for every index/table.
- `avg_p` is 0–100, `ml_p` is 0–1. Assert the scale at every band boundary.
  State the interval convention of every band table.
- Report `n` on every cell. Separate OBSERVED from INFERRED, and state the
  scope of every claim. An identifier asserting more than its measurement
  supports is this codebase's recurring failure.
- Verify by re-derivation, not restatement. Never assert wiring by text search
  — match structurally (AST) and assert against specific returned values.
- Zero draw legs have ever appeared on a slip. If a proposal puts one there,
  that is a bigger change than it looks — say so explicitly.
- **Do not create another findings doc — append to
  `docs/operator/FINDINGS-2026-10-07.md`.** Doc volume is a real cost.
- Full suite must pass, 0 failed, no test deleted; report collected count and
  baseline. The named baseline before this execution is **2,395 passed** and
  `def test_` floor **1,534** (`scripts/verify_work_order.py`).
  `tests/test_docs_links.py` adds one case per new Markdown file; this execution
  edits existing Markdown only and adds one CSV appendix, so it should not add
  a Markdown test. Report the full-suite count, file-count delta, and both
  verifier results after running them.
- Read and verify the checked-out code and data before relying on any old
  commit or line citation. If a cited object is absent, identify the live
  landmark and compare content; do not assume ancestry or recreate a stale
  tree.
- In the current checkout use the existing `.venv` when available; run
  repository commands from the root. Temporary captures may live under `/tmp`
  for analysis only; do not add generated training data or caches to Git.

# REPORT FORMAT

1. Mission A: state A1/A2/A3 are blocked on committed price coverage; report
   the exact-archive flag table, conflicts, T3–T6 structural/walk-forward
   result; note §8.3 text is unavailable and report its raw diagnostics only,
   with no formal pass/fail. Do not invent an A/B price table.
2. Mission B: B1 calibration and mover count first, then B2–B5 and the
   training/serving feature caveats.
3. Verdict against every pre-registered bar, one sentence each; `n` per cell.
4. Exact proposed entries only if an authorized change exists; otherwise state
   “none—no model, threshold, gate, bank, or construction change.”
5. What was not done, why, and the basis/file-count delta for every index.

# DELIVERY

This brief and its linked findings are maintained on the fixed branch
`arena/438d7dd2-edge-factory`. A fresh session based on `main` may not include
this branch's work; hand it over by starting from this branch or pointing the
next agent to this file and `FINDINGS-2026-10-07.md`. If the workspace holds a
second divergent copy, the version on this branch is authoritative.

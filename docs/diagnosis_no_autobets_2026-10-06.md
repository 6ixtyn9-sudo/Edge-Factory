# Why no auto-tickets fired on 2026-10-06 — deep diagnosis

Run: GitHub Actions `37411615673`, autonomous intraday, target date 2026-10-06.
Terminal line: `NO BET TODAY — 1 qualifying leg(s), need 2`.

Everything below is reproduced from the committed `localdata/` state in this
repo, not inferred from the log alone.

> **Review status.** Reviewed 2026-10-06 against source. Two findings were
> corrected and are marked inline with `CORRECTION` / `SCOPE NOTE` blocks:
> (a) the `zulubet` claim in §2 and row 4 of §6 — vote-only is *correct*,
> the bug is a `known()`/`spec()` disagreement worth 0 legs; (b) the leakage
> in §3.2 lives in **training** (`mine_consensus.py`), not in the serve-side
> pinning in `ml_fade_research.py`, which is correct as written.
>
> **Dependency ordering for remediation.** §3.4 (consensus view re-anchor) is
> a *prerequisite*, not a trailing item: it determines which estimator the
> baselines in §3.1–3.3 describe. Fix order is §3.4 → §3.2/3.3 (honest
> baseline) → §3.1 (decay test), because retuning the decay test against a
> leakage-inflated baseline just re-tunes against fiction. The §6 table below
> is ranked by legs-recovered-per-effort, **not** by execution order.

---

## 0. One-sentence answer

The day produced **8 candidates**; **7 of them were killed by the price layer
and the odds floor, not by the edge layer**, leaving 1 playable leg against a
hard `LEGS_PER_ACCA = 2` requirement. The *reason* only 8 candidates existed
at all is a second, deeper problem: the certified edge set was gutted by the
decay monitor that same morning, and the surviving edges are trained on a data
population the live pipeline can no longer produce.

---

## 1. Layer-by-layer autopsy of 2026-10-06

### 1.1 The eight candidates and their exact rejection codes

Reproduced with `playable_leg_rejection(..., execution_safe=True)`:

| fixture | bucket | odds | odds_source | verdict |
|---|---|---|---|---|
| Argentina v Benin | SKIPPED_VETO | 1.01 | betexplorer_odds | `min_odds_floor` (< 1.20) |
| England v Czech Rep. | SKIPPED_VETO | 1.13 | theoddsapi | `min_odds_floor` |
| Albania v San Marino | SKIPPED_VETO | 1.03 | betexplorer_odds | `min_odds_floor` |
| India v Uruguay | SKIPPED_VETO | 1.03 | betexplorer_odds | `min_odds_floor` |
| **Croatia v Spain** | SKIPPED_VETO | 1.28 | theoddsapi | **QUALIFIED** |
| Angola v Malawi | SKIPPED_VETO | 1.36 | scoutingstats_odds | `price_source_not_execution_eligible` |
| Algeria v Niger | WATCHLIST_UNCORROB | 1.22 | scoutingstats_odds | `price_source_not_execution_eligible` |
| Grenada v Bonaire | WATCHLIST_UNCORROB | 1.61 | scoutingstats_odds | `price_source_not_execution_eligible` |

So: **4 legs died on price level (odds too short), 3 died on price provenance
(audit-only source), 1 survived.** Zero legs were rejected by context purity,
bucket policy, kickoff guard or the selection ladder. The edge layer was not
the binding constraint today — the *pricing* layer was.

Note the shape of the four floor kills: 1.01 / 1.03 / 1.03 / 1.13. These are
not marginal. The certified rules that fired (`3way-unanimous avg_p>=65`,
`2way-unanimous avg_p>=70`) select the most lopsided fixtures on the card, and
on an international-break slate that means San Marino / Benin / Niger. **The
edge definition and the `MIN_LEG_ODDS = 1.20` floor are structurally in
conflict with each other on international-break days.**

### 1.2 The one surviving leg could never have become a bet

`LEGS_PER_ACCA = 2`, `MIN_ACCAS = 1`. There is no single-leg product. One
qualifying leg is therefore *always* NO BET regardless of its quality. Over the
last 30 days this rule bit exactly once (today) — so it is a real but
low-frequency cost. It is worth knowing it is a policy choice, not a data
problem.

---

## 2. The 30-day picture: the price layer is throwing away ~70% of signal

Replaying `playable_leg_rejection` over every archived candidate
2026-09-07 → 2026-10-06 (743 candidates):

| outcome | count | share |
|---|---|---|
| **QUALIFIED** | **224** | 30% |
| `price_source_not_execution_eligible` | 351 | 47% |
| `bucket_veto` | 71 | 10% |
| `min_odds_floor` | 55 | 7% |
| `price_source_unregistered` | 31 | 4% |
| `price_quarantine` | 11 | 1% |

Breakdown of the dominant killer:

* `scoutingstats_odds` — **279** legs. ScoutingStats is registered
  `execution_eligible=False` (audit-only). It is also, on most days, the only
  source that quotes the fixtures the edges fire on.
* `forebet_best` — **72** legs. Forebet was retired from live production on
  2026-06-12 (`FOREBET_LIVE_LAST_DAY`), yet `picks_today.py` still labels rows
  `odds_source="forebet_best"` on the fallback path (line ~4246, ~4371). Those
  rows are born dead.

`price_source_unregistered` (31): **17 of them are `odds_source="zulubet"`**, 14
are `odds_source=None`.

> **CORRECTION (2026-10-06, post-review).** The first draft of this document
> claimed `price_sources.py` has "no spec named `zulubet`" and attributed ~17
> recoverable legs to it. **That was wrong on both counts.** `spec()` resolves
> zulubet through the `VOTE_ONLY_SOURCES` fallback
> (`price_sources.py:390-396`) to a proper vote-donor spec with
> `execution_eligible=False`. Zulubet carries no book-backed price and is
> *correctly* non-executable.
>
> The real defect is that `known()` and `spec()` disagree:
>
> ```python
> # scripts/auto_tickets.py:1566 — evaluated BEFORE can_execute()
> if not psrc.known(source_name):
>     return "price_source_unregistered", ...
> # src/edgefactory/price_sources.py:400
> def known(name): return str(name or "").strip() in REGISTRY  # REGISTRY only
> ```
>
> `known()` consults `REGISTRY` but not `VOTE_ONLY_SOURCES`, so a vote-only
> source short-circuits at the earlier gate and is logged as
> `price_source_unregistered` (reads like a config gap) instead of
> `price_source_not_execution_eligible` / vote-only (the intended, correct
> fail-closed outcome). **This is a diagnostic-honesty bug worth ~0 recovered
> legs.** It must not be scoped as coverage work. See the corrected row 4 in
> §6.

`bucket_veto` (71) = 60 × `WATCHLIST_NO_ODDS` + 11 × `WATCHLIST_SUSPECT_PRICE`
— i.e. 60 more legs where **no price of any kind** was found.

**Total: 422 of 519 rejections (81%) are a pricing failure, not an edge
failure.**

### 2.1 Why the price layer is this weak — every named-book source is down

From `localdata/source_health_2026-10-06.json`:

| source | role | state today |
|---|---|---|
| bzzoiro_odds | named book | **HTTP 403 auth** (`quota_hint=auth_or_quota`) — token dead |
| oddspapi_odds | named book | **HTTP 429** on the first call, 0 rows |
| sharpapi_odds | named book | **HTTP 404** — endpoint contract broken |
| pinnapi_odds | named book | HTTP 200, **empty payload** |
| betminer | vote + price | **HTTP 404** — endpoint contract broken |
| sportytrader_odds | named book | Cloudflare challenge |
| theoddsapi | named book | **working**, but see 2.2 |
| betexplorer_odds | named book | **working**, bounded to 12 fixtures/run |
| scoutingstats_odds | audit-only | working — and therefore useless for execution |

Two of nine executable price sources are alive. One of those two is capped at
12 fixtures per run and is fed **only the fixtures that are already picks**
(`capture_betexplorer._candidate_rows`), so it can never widen the funnel —
today it attempted 6 and quoted 3.

### 2.2 TheOddsAPI covers 49 leagues; the edges fire outside them

`localdata/theoddsapi_sports.json` (refreshed 04:18 today) lists **49 active
soccer keys** — the big European leagues, MLS, Liga MX, the UEFA club comps and
`soccer_uefa_nations_league`. It contains **no international-friendly key, no
AFCON qualifier key, and nothing for the long-tail leagues** where the
consensus edges actually live. Today's unmatched lines say it exactly:

```
league not covered: International,Friendlies
league not covered: World Friendlies
league not covered: International,Africa Cup Of Nations Qualification Grp. B
```

Meanwhile quota utilisation from `theoddsapi_usage.json`: **56 credits used
this month across 3 keys with ~1,440 available — 96% of paid quota idle.**
The constraint is coverage mapping, not budget. We are rate-limiting ourselves
against a wall we aren't even touching.

---

## 3. The deeper problem: the certified edge set self-destructed this morning

At 04:04, `mine_consensus` certified **16** edges. `decay_monitor` immediately
benched **7** of them, leaving 9. The benched set:

```
ml-meta avg_p>=55 .. >=80   (all six tiers)   DECAYING -> BENCHED
3way-unanimous home-only avg_p>=60            DECAYING -> BENCHED
```

Look at what was benched, from the run log:

```
ml-meta avg_p>=55   baseline 2678 71.7%/LB .700   recent 123 68.3%/LB .596  ROI +52.9%  -> BENCHED
ml-meta avg_p>=70   baseline 1056 84.4%/LB .821   recent  52 78.8%/LB .660  ROI +61.8%  -> BENCHED
ml-meta avg_p>=80   baseline  378 91.0%/LB .877   recent  22 81.8%/LB .615  ROI +63.3%  -> BENCHED
```

**Every one of those was benched while printing +50% to +66% recent ROI.**
Two independent faults are at work.

### 3.1 Fault A — the DECAYING test is a sample-size artefact

`assay.decay_verdict`:

```python
if r_p < b_lb and r_lb < 0.90 * b_lb:  -> DECAYING
```

`b_lb` is the Wilson **lower** bound of a baseline with n≈2,678. `r_lb` is the
Wilson lower bound of a recent window with n≈123. For n=123 at p=0.683 the
Wilson LB is ≈0.596 — it is *arithmetically impossible* for a 123-sample LB to
sit above `0.9 × 0.700 = 0.630` unless the point estimate reaches ~71%. So the
second clause is nearly free; the gate collapses to "recent point estimate dips
below the baseline **lower bound**" — a one-sided test with the uncertainty
counted twice against the edge. A healthy edge whose true hit rate equals its
baseline LB will be benched roughly half the time by pure noise.

`should_bench` then adds `if recent_roi < 0: return True`, which is defensible,
but there is **no symmetric rescue**: a +53% ROI cannot save an edge that
tripped the hit-rate clause. A hit-rate test with no ROI override on an edge
family that bets at odds > 1/p is the wrong objective function. Hit rate is
not the P&L.

Comparison should be `recent LB vs baseline LB` → no. It should be a proper
two-sample test (e.g. difference-of-proportions z, or recent LB vs baseline
**point estimate** with an explicit minimum detectable effect), plus an ROI
veto that can cut both ways.

### 3.2 Fault B — ml-meta is trained with half-time-score leakage

This is the serious one.

`mine_consensus.train_ml_meta_classifier` trains on `consensus3` and builds:

```python
df['ht_diff']  = ht_hs - ht_gs
df['ht_total'] = ht_hs + ht_gs
```

`ht_hs` / `ht_gs` come from `edgefactory/sources/forebet.py`:

```python
"ht_hs": _i(m.get("Host_SC_HT")),
"ht_gs": _i(m.get("Guest_SC_HT")),
```

> **SCOPE NOTE (post-review).** Do not confuse this with the serve-side
> pinning in `src/edgefactory/ml_fade_research.py:93` ("checkpoint ⑫
> contract"), which zeroes `ht_diff`/`ht_total` pre-match. **That serve-side
> behaviour is correct and must not be touched.** The defect described here is
> strictly upstream in *training* — `scripts/mine_consensus.py:560-561` fits
> the decision boundary against these columns. A reviewer who inspects
> `ml_fade_research.py` will correctly find nothing wrong and wrongly conclude
> the finding is bogus.

`Host_SC_HT` is the **actual half-time score of the match**, sitting in the
same payload as `Host_SC` (the final score). The ml-meta classifier is
therefore trained on post-kickoff outcome data. Its fitted weights are
`ht_diff +0.245`, `ht_total +0.192` — and by `|w| × σ` these are the **two
largest discriminative features in the entire model**.

At serve time `picks_today.py` has no forebet row at all (retired 2026-06-12),
so `ht_diff = ht_total = 0.0`. The leakage is unavailable at inference — which
is the only reason the live hit rate isn't catastrophically mis-stated, but it
also means **the certified baseline (87–91% at the high tiers) is a number the
live model can never reproduce.** The decay monitor then dutifully benches the
edge for failing to reach an unreachable bar. Certify → serve → bench → recertify
→ bench, forever.

### 3.3 Fault C — train/serve population and feature skew

11 of the model's 26 features are **forebet-only**, and forebet is retired from
every live fetch:

```
fb_p       +0.2244   -> 0.0 at serve
ht_p       -0.5119   -> 0.5 default
ht_diff    +0.2454   -> 0.0     (leakage, see above)
ht_total   +0.1919   -> 0.0     (leakage)
kelly      -1.1839   -> 0.0
pred_total +0.0306   -> 0.0
pred_diff  -0.0728   -> 0.0
goalsavg   +0.0587   -> 0.0
p_ng       -0.2881   -> 0.0
p_under    +0.2267   -> 0.0
p_gg       -0.8201   -> 0.0
```

Quantified against the 2026 forebet distribution, the **per-fixture
discriminative signal destroyed at serve is ≈0.44 logits (quadrature)** — about
±7 percentage points of probability at p≈0.80. The mean shift happens to be
small (+0.06 logits) because the terms partially cancel, so the breakage is
invisible in aggregate calibration and only shows up as degraded ranking.

On top of that, the training query is `WHERE fb_p IS NOT NULL AND zb_p IS NOT
NULL AND sa_p IS NOT NULL` — the model is trained **exclusively on
forebet-covered fixtures** and served **exclusively on non-forebet fixtures**.
Different leagues, different coverage depth, different everything.

### 3.4 Fault D — the same skew exists for the non-ML consensus edges

`src/edgefactory/warehouse.py` defines every certified view as Forebet-anchored:

```sql
CREATE OR REPLACE VIEW consensus2 AS ... FROM fb JOIN zb USING (date,hkey,akey)
CREATE OR REPLACE VIEW consensus3 AS ... FROM fb JOIN zb JOIN sa
CREATE OR REPLACE VIEW consensus4 AS ... FROM fb JOIN zb JOIN sa JOIN vb
```

(The comment even says so: *"Legacy consensus views remain Forebet-anchored for
historical rule continuity."*)

But live, `picks_today.eval_1x2` computes "2-way / 3-way unanimous" over
whichever ≥2 of `[forebet(off), zulubet, statarea, vitibet, betclan,
bzzoiro(403)]` happen to be present. So:

* `2way-unanimous avg_p>=70` was **certified on forebet × zulubet**;
* today it **fired on zulubet × vitibet / statarea × betclan**.

Same rule name, different estimator. The certified ROI/hit statistics do not
describe the thing being served. This is the root cause behind the chronic
"certified says X%, live says Y%" gap that the decay monitor keeps reacting to.

---

## 4. The candidate funnel is also starving at the top

`coverage: scored=29 picks=6` against `692 matches` considered. Only 29
fixtures reached ML/consensus scoring, because `eval_1x2` requires **≥2 live
voters on the same fixture key**, and the live voter roster is now:

| voter | live today |
|---|---|
| forebet | retired 2026-06-12 |
| bzzoiro | `can_vote=True` but `can_fetch_today=False` (403) |
| zulubet | ✅ |
| statarea | ✅ |
| vitibet | ✅ |
| betclan | ✅ (30s budget cut it off early: *"betclan: 30s budget hit, stopping early (34 fetched)"*) |

Four effective voters, two of them thin, one of them truncated by a hard 30s
wall-clock budget that it hit **twice** in this run. The 2-voter overlap
requirement on four partially-overlapping scrapers is what caps the slate at
~29 scored fixtures. Also note `vitibet: raw=106 scored=0` on the donor
refresh, and `futbolpronosticos: captured 79, settled 0, unmatched 79` — join
keys are failing, not the fetches.

---

## 5. Secondary findings worth logging

1. **`SKIPPED_VETO` is the best-performing bucket.** Selection ladder:
   `SKIPPED_VETO n=110 roi=+6.4% recent +7.9% LB 0.706 GOLD/BOOST`, while
   `CERTIFIED_CLEAN n=14 roi=+26.6% UNGRADED` and `CAUTION n=16 roi=-12.2%
   DEMOTED`. Seven of today's eight candidates were SKIPPED_VETO. The purity
   assay is vetoing contexts that then outperform — the veto layer is costing
   money and should be re-estimated against printed-slip evidence.
2. **Two ROI numbers for the same bucket disagree**: `audit_recent_picks` says
   `SKIPPED_VETO settled=255 roi=-5.7%`; the slice ladder says `+6.4%`. They use
   different evidence sets (all archived picks vs printed-slip only). Both are
   quoted in the same run output without reconciliation.
3. **Kickoff mismatch, silently overridden**: `Albania|San Marino: pick legacy
   display says 17:45Z, captured rows say 18:45Z (Δ=60m)`. Resolved by
   "display-fallback override" — a 1h DST-class disagreement between the
   candidate record and the capture record, on a leg that would have been
   staked had it cleared the odds floor.
4. **17 ambiguous settlement keys pending** (`Juventud Unida SL` vs
   `Juventud Unida Univ.`, `Ferroviário Nacala` vs `Ferroviário Nampula`, …) —
   one ledger key, two real fixtures. These silently pollute the hit-rate
   series that the decay monitor benches edges on.
5. **ml-fade price coverage alarms**: `12% zb-only`, `40% fb-only` against a
   90% threshold; 2 unresolved result conflicts flagged for human review.
6. **`soccervista` is referenced but does not exist** in the warehouse
   (`CatalogException: Table with name soccervista does not exist`), so every
   soccervista confirmation lever is a permanent no-op.
7. **Node 20 deprecation warning** on all five actions in the workflow —
   housekeeping, but it will break the run eventually.

---

## 6. What to fix, in order of legs recovered per unit of work

| # | fix | est. legs/30d recovered | effort |
|---|---|---|---|
| 1 | **Add 1–2 working named-book price feeds** (fix bzzoiro 403 token; fix/retire oddspapi 429 + sharpapi/betminer 404 contracts). This is the single binding constraint. | up to ~280 | medium |
| 2 | **Widen betexplorer**: raise `DEFAULT_MAX_FIXTURES` (12→24, ceiling already 24) and feed it the *scored candidate pool*, not just the fixtures that are already picks. | ~60–100 | small |
| 3 | **Use the idle TheOddsAPI quota**: 96% unused. Add explicit `SHORT_LEAGUE_KEYS` entries for international friendlies / AFCON quals, and pre-price the scored pool rather than only the frozen slate. | ~40 | small |
| 4 | **CORRECTED — diagnostic honesty only, ~0 legs.** Make `known()` agree with `spec()` so vote-only sources log `price_source_not_execution_eligible` instead of `price_source_unregistered`; stop emitting `forebet_best` as an `odds_source` post-cutoff. Zulubet is correctly non-executable — do **not** scope this as coverage work. | **0** (17 honest log lines; 72 fewer dead-on-arrival rows) | trivial |
| 5 | **Fix the decay test**: two-sample proportion test instead of `recent_LB vs 0.9×baseline_LB`, and let a strongly positive recent ROI veto a hit-rate bench. | restores 6 ml-meta tiers | small |
| 6 | **Drop `ht_diff`/`ht_total` from the ml-meta feature set** (half-time score = target leakage) and retrain. Baseline numbers will fall and *should* — they will then be reachable at serve. | correctness | small |
| 7 | **Re-anchor the consensus views** on the live voter set (zulubet×statarea×vitibet) so certified statistics describe the served estimator. Keep the forebet-anchored views for historical continuity only. | correctness | medium |
| 8 | **Revisit `MIN_LEG_ODDS=1.20` vs the ≥65/≥70 unanimity rules** — or let a short-priced leg ride as part of a 2-leg acca whose *combined* odds clear a floor instead of per-leg. | ~55 | small, policy |
| 9 | Raise betclan's 30s budget, or make it resumable across runs. | widens the voter base | trivial |
| 10 | Resolve the 17 ambiguous settlement keys; they corrupt the hit-rate series the bench decisions read. | correctness | small |

---

## 7. Reproduce any of this

```bash
python3 -m venv .venv && .venv/bin/pip install python-dotenv pandas numpy duckdb

# per-candidate rejection codes for any day
PYTHONPATH=src .venv/bin/python - <<'PY'
import json, importlib.util, sys
sys.argv=['x']
s=importlib.util.spec_from_file_location('at','scripts/auto_tickets.py')
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
for r in json.load(open('localdata/picks_today.json')):
    print(r['home'],'v',r['away'], r.get('odds'), r.get('odds_source'),
          m.playable_leg_rejection(r, day='2026-10-06', execution_safe=True))
PY

# model features that are dead at serve time
.venv/bin/python -c "
import json; m=json.load(open('localdata/edges_consensus.json'))['ml_model']
print(*(f'{c:12s} {w:+.4f}' for c,w in zip(m['feature_cols'],m['coef'])), sep='\n')"
```

# Data-integrity audit — 2026-10-21

**Scope:** the displayed numbers of Edge Factory, end to end: provider capture →
warehouse → consensus/mining/certification → selection → pricing → tickets →
settlement → bank/P&L/reports.
**Checkout:** `56f990fd110cbe8fa857f3a9f51022324ee3de37` (squashed merge of PR #113),
working branch `arena/b798bbd0-edge-factory`. No history beyond HEAD exists locally, so
"who introduced this" cannot be answered from this checkout; introductions below cite the
code/doc line that carries the behaviour, not an author.
**Mode:** read-only audit. No fix, no registry edit, no replay, no dispatch, no settlement,
no ticket reset was performed. Only this document was written.
**Test baseline (re-run this session):** `3583 passed, 1 skipped in 186.01 s`
(`.venv`, Python 3.11.2, `PYTHONPATH=src`). The skip is the immutable-baseline fixture that
needs a commit absent from a shallow checkout. Passing tests do not bear on the findings
below: each finding is in a path the suite does not assert.

---

## 1. Verdict in one page

1. **The core accounting chain is real and reproduces.** Bank, staked/returned totals, the
   62W/45L record and every acca's return recompute from
   `localdata/auto_tickets_state.json` to ±0.0001. Warehouse row counts and date ranges
   recompute from the committed `csv.gz` files. Settlement maps only positive terminal
   evidence to a void: a missing score is **not** turned into a loss
   (`src/edgefactory/settlement.py:29-46`).
2. **The purity layer is not trustworthy as displayed.** The assay's ROI divides by
   *priced* legs but its numerator charges **−1 for every unpriced losing leg** (0 for an
   unpriced winning leg). `n` in the same verdict call counts all settled legs. On
   consensus2 this moves **64 of 1,213** league×selection contexts across a verdict
   boundary, including **8 that move from VETO to ALLOW/CAUTION**, several on three or
   four priced legs. The resulting `purity_registry.json` feeds selection (VETO suppresses,
   BOOST promotes). This is an **F-class defect**, not a threshold quibble.
3. **The high-level "certified" numbers cannot be independently reproduced from this
   checkout.** 11 of 19 certified edges need tables (`scoutingstats`, `vitibet`, …) that
   have no committed `csv.gz`; the other 8 were mined from data that stops at
   **2026-06-12**, one day before the post-Forebet era opens (2026-06-13). Their registry
   numbers are therefore **B-unverified**: derived once, not provably fabricated, and not
   checkable here. A `pfc_…` contract re-run returns `n=0` for exactly this reason.
4. **The enhancement certification registry truncates its own evidence.** `records` is
   capped at 400 while `match_over_25` has `n=447`; the slice tables in the same report sum
   to 400, and the 60-day bench check and the floor derivation read only the truncated
   list. The project's own note records a 428-key 30-day window for that market, i.e. the
   cap is smaller than one window.
5. **A "0.0" probability is stored where the source code writes `None`,** on 34 of 41 rows
   of the live 2026-10-21 slate. It is contained by label gates, but it is exactly the
   "missing rendered as a number" class the task asks about, and it proves the committed
   slate was **not** produced by HEAD's `picks_today.py`.
6. **Three suspected unit defects were tested and are not present in this snapshot:**
   live `prob_single` normalises 0–100→0–1; contract voting infers the scale from the 1X2
   vector and requires it to sum to 1±0.05; consensus2/3 pool raw `pmax` but all three
   contributing sources are 0–100 in this data (0 mixed-scale rows). The risk is latent,
   not active — consensus4 alone carries a per-source guard.
7. **Deployment state is unproven.** PR #113 merged with its only check
   (`Workers Builds: edge-factory-source-relay`) **FAILED**. No evidence the Python
   pipeline has run since the merge.

**Bottom line:** the ledger arithmetic and settlement rules are evidence-backed; the
*purity verdicts*, the *certified-contract numbers* and the *enhancement registry slices*
are not, for reasons that are code defects (1, 4), missing inputs (3) and artifact/code
divergence (5). None of the three is safe to keep displaying as a measured statistic until
the fixes in §6 are authorised.

---

## 2. What was independently recomputed (and matched)

| Quantity displayed | Stored value | Independent recomputation | Result |
|---|---|---|---|
| Bank | 161.223 (% of base) | 100 + Σ(returned−staked) over 52 bet-days = 100 + 61.2231 | match (Δ 0.0001) |
| Bet-days / record | 52 / 62W 45L | 52 rows; 62 won, 45 lost accas | match |
| Staked / returned | 1484.34 / 1545.56 | sum of per-day fields | match |
| Acca returns | each day's `returned_pct` | `stake_pct × odds` if won, 0 if lost, for all 107 accas | 0 mismatches |
| Warehouse tables | 11 | `warehouse.connect()` on committed `csv.gz` | 11, counts below |
| `forebet_settled` | 323,524 | reconstructed | match |
| `statarea_settled` | 481,537 | reconstructed | match |
| `zulubet_settled` | 66,808 | reconstructed | match |
| `betexplorer_settled` | 104,664 | reconstructed | match |
| `consensus2` | 31,077 | reconstructed | match |
| `consensus3` | 18,478 | reconstructed | match |
| Resolved outcomes | 28,795 | join outcomes to consensus era (betexplorer to 2026-09-01) | match |
| Audit overall | hit .6991 / ROI .0400 | 453 wins / 648 settled; priced P&L / 533 | match |
| Audit by bucket | see §3.6 | recomputed from the same ledger | match |

The warehouse composition, the date coverage and the bank chain are **A/B-class**.
Everything below is where provenance breaks.

---

## 3. Findings

Severity: **High** = changes suppression/promotion or a displayed headline number;
**Medium** = misleading denominator/population; **Low** = display or defensive-only.

### F-1 (High) Purity ROI: numerator and denominator are different populations — F-class

`scripts/assay_purity.py` (`assay_edge`) computes

```
pnl = CASE WHEN pick=outcome THEN COALESCE(pick_odds,1)-1 ELSE -1 END
roi = SUM(pnl) / n_priced
```

An unpriced leg therefore contributes **−1 when it loses and 0 when it wins**, while the
denominator counts only legs that have a price. The verdict call receives `n` = all settled
rows, `roi` = per-priced-leg. Both numbers come from different populations.

Recomputed on consensus2 (31,077 rows; 29,015 priced, 2,062 unpriced), grouped by league ×
selection — the base view is a single rule on the 1x2 market, so this is the assay's league
context key with the rule dimension fixed:

- **1,213** (league, selection) contexts; **344** reach VETO under the shipped formula.
- **64 (5.3%) change verdict** when the numerator is restricted to priced legs
  (unpriced legs contribute 0), of which **8 move VETO → ALLOW/CAUTION**:

| context | n | priced | shipped ROI | priced-only ROI | shipped → corrected |
|---|---:|---:|---:|---:|---|
| `Cn3` draw | 39 | 3 | −8.2333 | +1.1000 | VETO → ALLOW |
| `Eg2` draw | 36 | 4 | −4.3000 | +0.4500 | VETO → ALLOW |
| `VeC` home | 13 | 3 | −0.6333 | +0.0333 | VETO → ALLOW |
| `By1` home | 14 | 3 | −0.7333 | −0.0667 | VETO → CAUTION |
| `MxW` home | 48 | 25 | −0.3276 | −0.0476 | VETO → CAUTION |
| `Es4` home | 40 | 20 | −0.3115 | −0.0115 | VETO → CAUTION |
| `Id2` home | 31 | 23 | −0.3061 | −0.0887 | VETO → CAUTION |
| `Ge2` home | 14 | 10 | −0.2520 | −0.0520 | VETO → CAUTION |

Two independent problems show in the same table: (a) the ROI is biased downward by
unpriced losses (976 unpriced *losing* legs in these buckets); (b) **a context can reach
the n≥12/40 gates with three priced legs**, so an "ALLOW" at ROI +1.10 is three
observations, not thirty-nine. `recent_roi` has a guard (`rn ≥ 30`) but it also divides by
`rn_priced`.

Reach: `localdata/purity_registry.json` (generated 2026-10-21T01:26Z, window 36,500 days)
→ `lookup_context` in `scripts/picks_today.py:1630+` → `bucket_pick` → VETO suppression and
BOOST promotion, and the audit's veto deep-dive. Only `post_forebet_v1` contracts are
shielded: their `where` appends `pick_odds IS NOT NULL`. The base views (`v_consensus2_base`,
`v_consensus3_base`, `consensus_ou`, `consensus_btts`) are not.

### F-2 (High) Enhancement registry truncation: `n=447` headline, 400 records behind it — F-class

`MAX_RECORDS_PER_MARKET = 400` (`src/edgefactory/enh_registry.py`) truncates each market's
`records` list while the cumulative counters keep growing. Verified in
`localdata/enhancement_registry.json`:

- `match_over_25@v1`: **n=447, hits=293, records=400** (47 records lost, 10.5%),
  `profit=+1.737`, `multi_n=84`, status `PAPER`.
- The same report prints the market headline `n=447` and then bucket/rule slices that sum
  to **400** (303 of the 400 have no bucket provenance at all).
- `derive_floors` (`_priced_records_before`) and the BENCH circuit breaker
  (`_evaluate`, rolling 60 d) both read `records`, so their "n" is the truncated list, not
  the market's n.
- The code's own note records a **428-key 30-day window** for `match_over_25`
  (`processed_window_is_safe`): the 400-record cap is smaller than one window, so a 60-day
  ROI can never see its stated population.

Registry-wide: 16 markets, 509 records, **all `PAPER`/`SHADOW`**, and the file has **no
top-level `generated_at`/version** — only a `@v1` suffix per market.

Consequence: floor derivation and benching use a shrinking, recency-biased sample while
quoting the cumulative n. No market is ELIGIBLE today, so nothing is currently promoted by
this path — but the numbers displayed beside those markets are wrong by construction.

### F-3 (High) Certified contract numbers are not reproducible in this checkout — B-unverified

`localdata/edges_consensus.json`: 95 edges, **19 certified**. Inputs:

- **11/19** need `scoutingstats`/`vitibet` tables that have no committed `csv.gz` in
  `localdata/`. `build_warehouse.py` lists them; the data is not in the repository.
- **8/19** are re-creatable in principle, but the committed probability sources stop at
  **2026-06-12**: statarea 2017-01-01→2026-06-12 (489,399), zulubet 2024-01-01→2026-06-12
  (67,216), forebet 2024-01-01→2026-06-12 (327,895). The post-Forebet era starts
  **2026-06-13**. There are **zero** statarea/zulubet rows at or after that date. A full
  re-run of `pfc_c83d885867c9025a351b9b8c` (and the other seven) yields `n=0` train/valid,
  while `betexplorer` (results only) runs to 2026-09-01 and still resolves 28,795 outcomes.
  `collect_observations` reports `no_rows_in_era` for zulubet/statarea and
  `missing_table` for ten other sources.

So the numbers in the registry (e.g. `pfc_c83d…`: train n=633 hit .6556 ROI −.0019; valid
n=271 hit .7048 ROI .0392, Wilson LB .6479) cannot be checked here. They are **not shown to
be fabricated**, and the coverage gap is a *snapshot* property, not a date-filter bug — but
the claim "19 certified edges" is currently an **unverifiable assertion** in this checkout.
Any consumer that treats it as proof of forward-validated performance is over-claiming.

Related coverage gap: `purity_registry.json.contract_contexts` holds **8** `pfc_` ids — the
same 8 re-creatable edges. The other **87 of 95** contracts have no contract-scoped purity
contexts, so their picks fall back to an empty context (no veto evidence) rather than a
learned verdict. Fail-open for suppression.

### F-4 (Medium) Enhancement `0.0` is a missing-value sentinel in a probability field — F-class

`picks_2026-10-21.json`: 41 rows, **34 carry `enhancement_probability: 0.0`** with
`enhancement_label: None`, `enhancement_priced: False`, `recommended_enhancement` absent.
`picks_2026-10-20.json`: 23 of 28. The row's own `enh_candidate_log` shows why: the priced
candidates were `unpriced` (no OddsPapi quote) or `below_line_threshold`; the best
*cohort* candidate was `match_over_25` at 0.5771, excluded for price.

`scripts/picks_today.py:845` initialises the field to `None` and only overwrites it when a
candidate is selected (`:1114`). **HEAD does not write 0.0 anywhere.** The committed slate
therefore cannot have been produced by HEAD — same class of divergence as F-3's stale
inputs. Containment: `notifier.py:136/158/280/764` gates on `enhancement_label`;
`o25_tracker.py:19` gates on the label; `enh_pricing.py:646` uses `if prob:` so 0.0 yields
no edge sample. So the sentinel does not reach a displayed probability or a bet — but it is
stored as a numeric 0.0, and any future consumer that reads the field without the label
will treat "unknown" as "certainly not".

### F-5 (Medium) Hit rate and ROI in the audit artifact describe different populations — display-class

`localdata/picks_audit_rolling.json` (generated 2026-10-21, window 2026-09-22→10-21):

- `overall`: 648 settled, **533 priced**, 453 wins, `hit_rate .699074`, `roi .040005`.
  Hit rate is over 648; ROI over 533. They are printed adjacently (`audit_recent_picks.py:
  2665-2666`) with no population labels.
- By bucket: `SKIPPED_VETO` 348 settled / 307 priced, hit .7385, ROI **+0.0608**;
  `CERTIFIED_CLEAN` 87/87, hit .6322, **+0.0083**; `CAUTION` 53/53, **+0.0161**.
  The **vetoed** bucket has the best realized hit rate and ROI in the measured window
  (n=307 priced). That is an observational result, not proof the veto is wrong — but it is
  the opposite of what the veto is meant to buy, and it is consistent with F-1's biased
  ROI feeding the veto.
- `by_enhancement`: `away_over_05` shows `hit_rate 0.944`, `recommended 18`, `priced_n 1`,
  `priced_roi 0.64`. A 94% hit rate resting on 18 recommendations and **one** price is the
  clearest example of the two-population display.

This is a measured-statistic labelling defect (B with wrong population), not a fabricated
number.

### F-6 (Medium) Settled views contain identity-less rows that carry probabilities and picks — denominator-class

In the built warehouse:

- `forebet_settled`: **7,145** rows with null/short `hkey`/`akey`, **all** having p1/px/p2
  and a computed `pick`.
- `statarea_settled`: **13,859**; `zulubet_settled`: **2,730** — same shape.

`consensus2/3` exclude them (`length(hkey)>=4`), so consensus and contract numbers are
identity-filtered. But any per-source aggregate that does not filter identity — including
the headline "settled rows" quoted in reports and the raw table counts — includes 2–4%
rows that cannot be identified to a fixture. Separately, the undated header-echo rows
(statarea 113 / zulubet 29 / forebet 29) carry no probabilities or scores and correctly
never enter the settled views.

### F-7 (Low) Performance text prints one bet-day twice — F-class (display)

`localdata/auto_tickets_performance.txt` has **53** date lines for **52** bet-days:
`2026-10-11` appears twice (once in sequence, once appended at the end). The state file and
the header ("over 52 bet-days") are correct; the text render duplicates a day. Low impact,
but it is a denominator a reader can add up wrongly.

### F-8 (Low, latent) Mixed probability scale — no active corruption this snapshot

`_prob()` (`warehouse.py:30`) casts raw values and does not normalise. Measured:

- `forebet_settled`/`zulubet_settled`/`statarea_settled` `pmax`: min 34/23/34, max 94/97/85
  — **all 0–100**, and **0 rows** in consensus2/3 where the two/three sources sit on
  different scales.
- `consensus2/3.avg_p` is nevertheless a raw mean with **no per-source guard**
  (`warehouse.py:397-436`), while `consensus4` has one
  (`CASE WHEN pmax>1.5 THEN pmax ELSE pmax*100`, `:454-457`).
- The live path normalises (`prob_single`, `picks_today.py:4726-4732`), as does the
  contract engine (`_remine_signal` infers the scale from the full 1X2 vector and rejects
  vectors that do not sum to 1±0.05; `project_votes` then multiplies by 100,
  `consensus_contracts.py:69-100, 245`).

So no displayed number is currently wrong from units. The defect is a missing guard in the
views that the purity assay and decay monitor consume; a source that flips scale would move
`avg_p` by ~100× for the affected rows with no error.

### F-9 (Low) Defensive default that would fabricate a hit rate — currently dead

`load_rolling_audit_hit_rates` (`picks_today.py:742`) returns
`float(stats.get("hit_rate", 1.0))` for any enhancement with `recommended ≥ 5`. If
`hit_rate` were ever absent, the default is a **perfect** rate. In the current artifact the
audit always writes `hit_rate` when `recommended > 0`, and the function has no live caller
except a stub in `audit_enh_under_parity.py:254` — so it is **D-class dead code** today.
It should not be left as a default that a future caller can hit.

### F-10 (Medium, operational) What is deployed is unproven

PR #113 merged 2026-10-21T04:19:52Z; its only check
(`Workers Builds: edge-factory-source-relay`) is **FAILURE** (04:15:52Z). There is no
evidence the Python pipeline ran after the merge, and `picks_2026-10-22.json` is a 2-byte
empty list. The 3,583 passing tests are a local, source-only statement.

### Cleared items (tested, not defects)

- **Future-dated shadow files are not leakage.** `scored_candidate_shadow_2026-10-24/25.jsonl`
  (2,322/1,778 rows) are named for **fixture days**, and every row carries
  `build_day: 2026-10-19` — a forward scan, not a back-filled result.
- **Settlement does not invent outcomes.** Missing score → held, then void at 5 d;
  terminal statuses (POSTPONED/CANCELLED/ABANDONED) are positive evidence only;
  operator-verified results outrank donors (`settlement.py:1-80`).
- **Contract voting is scale-safe and refuses ambiguous leaders**
  (`consensus_contracts._remine_signal`), and categorical tips are only eligible for the
  no-probability-floor test.
- **Junk header rows do not enter any settled denominator** (no numeric evidence).

---

## 4. Classification of every suspicious number family

| Number family | Class | Why | Reach |
|---|---|---|---|
| Warehouse counts, date ranges, 28,795 resolved outcomes | **A** observed | Recomputed from committed CSV rows | Mining/decay input |
| Bank 161.223, 62W/45L, per-acca returns | **B** derived | Recomputed from state to ±0.0001 | Display, staking baseline |
| Audit `hit_rate`/`roi`, bucket and enhancement tables | **B** derived, mislabelled population (F-5) | Recomputed; denominators differ | Audit report only |
| Purity context ROIs/verdicts | **F** unsupported stand-in | Numerator/denominator mismatch (F-1) | Registry → selection (VETO/BOOST) |
| `${pfc_…}` certified train/valid n, hit, ROI, Wilson | **B-unverified** | Inputs absent or out of coverage (F-3) | Registry label, audit claims |
| Enhancement market `n`/`hits`/`profit` | **B** truncated (F-2) | Cumulative counters vs 400-record slices | Floors, BENCH, display |
| Enhancement cohort rates used as probabilities | **C** labelled estimate | Measured all-outcome cohort rate, exact contract, n≥100 | Candidate ranking; never a bet without a price |
| Goal-range/exact/Double-chance model probabilities | **C** model prediction | `engine: model`, excluded for `no_realized_cohort` | Log only |
| `enhancement_probability: 0.0` | **F** sentinel | Missing written as numeric zero (F-4) | Stored artifact |
| Verdict thresholds, MIN_PROB band, MIN_LEG_ODDS 1.30, stake 0.25, caps | **D** policy | Pre-registered constants; role documented | Gates; they do not manufacture observations |
| Test/handoff fixtures (e.g. `r2_proofs.py` 0.46) | **E** synthetic | Never imported by `src/` | None |
| `picks_audit_rolling.secondary_stats` (btts 341/648, over25 391/648) | **B**, fixture-level | Every settled pick scores the fixture, not an enhancement bet | Descriptive only — must be labelled as fixture rates |

---

## 5. Per-statistic verification register

| Measured rate/average | Source & identity | Numerator / denominator | Population | Window / cutoff | Missing & duplicates | Independent recompute |
|---|---|---|---|---|---|---|
| Bank 161.223% | `auto_tickets_state.json` history | Σ returned / Σ staked + base | 52 bet-days, 107 accas | 2026-08-27→10-20 | no void/odds-1.0 rows; Δ 0.0001 | **match** |
| Hit .6991 | rolling audit ledger | 453 / 648 | settled picks | 2026-09-22→10-21 | unpriced included in hit, excluded from ROI | **match** |
| ROI .0400 | same | P&L / 533 priced | priced picks | same | consistent with F-5 | **match** |
| `SKIPPED_VETO` +6.08% | same | 307 priced | vetoed picks | same | observational, no overlap control | **match** |
| Consensus2 31,077 | warehouse view | join fb×zb on (date,hkey,akey) | identity-filtered | 2024-01→2026-06-12 | DISTINCT ON dedupe | **match** |
| Purity context `Cn3` draw | consensus2 grouping | 39 rows / 3 priced | league×pick | all history | 36 unpriced | **flip reproduced** |
| `match_over_25` n=447 | enhancement registry | 293 / 447 | priced records | 2026-08-22→10-20 | 47 records truncated | **counters match; slices don't (400)** |
| `away_over_05` 94.4% | audit enhancement table | 17 / 18 recommended | 1 priced | window | priced ROI on n=1 | **match; population mismatch** |
| Certified `pfc_c83d…` | edges registry | 271 / — valid | re-runnable | era 2026-06-13+ | 0 rows in era | **cannot reproduce (coverage)** |
| Enhancement hit-rate defaults | code | `hit_rate` default 1.0 | — | — | dead path | **not exercised** |

---

## 6. Proposed fixes (for approval — nothing implemented)

Ordered by evidential damage, smallest safe change first. Items 1–2 change stored artifacts
and therefore need explicit approval before running.

1. **Purity ROI (F-1).** Make numerator and denominator the same population, in one place
   in `scripts/assay_purity.py`: either restrict `pnl` to priced legs (`ELSE 0` for
   unpriced) or divide the current numerator by `n` and label it a flat-stake return. Add
   the priced count to every verdict row so a verdict can never be read as n=priced. Then
   regenerate `purity_registry.json` **only with approval** — the current file is a
   tracked artifact whose VETO/BOOST verdicts change selection. Until regenerated, treat
   its verdicts as F-class.
2. **Enhancement registry truncation (F-2).** Compute slice/BENCH/floor evidence from a
   store that is not capped below one window, or record per-slice aggregates at write time
   and mark `records_truncated: true` whenever `n > len(records)`. The current 400 cap must
   not be described as "settled history".
3. **Contract provenance (F-3).** Store, beside each certified edge, the input snapshot
   identity (file hashes/dates per source) and make `validate_contract` **fail closed**
   when an input is absent, so "cannot reproduce" is visible in the artifact rather than
   only to an auditor. Re-mining needs a full data snapshot outside this checkout and a
   separate authorisation.
4. **Purity coverage (F-3b).** Generate contract-scoped contexts for all `post_forebet`
   contracts, or mark the 87 uncovered contracts explicitly as "no contract purity
   evidence" in selection output. Do not let an empty context look like a passed veto.
5. **`0.0` sentinel (F-4).** Write `null` for "no enhancement" and add a schema check that
   a numeric probability requires a cohort identity (`contract_id`, `n>0`, as-of date).
   Regenerate or archive the committed slates; they cannot have come from HEAD.
6. **Reporting populations (F-5).** Print hit rate and ROI with their denominators
   (`wins/settled`, `P&L/priced`) and split priced vs unpriced explicitly; rename
   `secondary_stats` to fixture-level and state that every settled pick scores the fixture.
7. **Settled-view identity (F-6).** Require team identity for any per-source rate used as a
   denominator; publish identity-filtered counts separately from raw table counts.
8. **Scale guard (F-8).** Add the same per-source normalisation or a hard error to
   `consensus2/3` that `consensus4` already has.
9. **Display duplication (F-7).** Deduplicate the bet-day list in the performance render
   (2026-10-11 appears twice).
10. **Deployment evidence (F-10).** Rebuild the relay Worker and record the source commit in
    generated artifacts; until then, no live claim should rest on the merged PR.

**Explicitly not proposed:** lowering any gate/threshold, turning ML back on, restoring a
Forebet-led electorate, replaying history, rewriting banks/settled rows/registries, or
substituting a prior/average for missing evidence.

**Items flagged for a separate, separately-authorised audit (not repaired here):**
historical purity verdicts already used to withdraw/suppress picks; the 13 Oct bank
correction and the documented 27 Sep / 10 Sep residuals; withdrawn tickets under
`docs/operator/withdrawn-tickets/`; the future-dated shadow naming convention.

---

## 7. What this audit did *not* verify

- **Supabase / API / Worker live state**: no accessible live system in this checkout; the
  relay build is failed, so even the deployed artifact identity is unknown.
- **Provider capture** (OddsPapi, BetExplorer, ScoutingStats): no live call was made; only
  the committed archives were inspected. A live check must not be inferred from this
  document.
- **Legacy readers, migrations, exports, notifications** beyond the render gates already
  verified: not exercised.
- **Original authorship**: the checkout is one squashed commit; no blame-based attribution
  is possible or claimed.

**Evidence index (numbers in this report):**
`localdata/auto_tickets_state.json`, `localdata/auto_tickets_performance.txt`,
`localdata/picks_audit_rolling.json`, `localdata/purity_registry.json`,
`localdata/enhancement_registry.json`, `localdata/edges_consensus.json`,
`localdata/picks_2026-10-20.json`, `localdata/picks_2026-10-21.json`,
`localdata/*.csv.gz` via `edgefactory.warehouse.connect()`,
`src/edgefactory/{warehouse,consensus_contracts,enh_registry,enh_pricing,settlement}.py`,
`scripts/{assay_purity,picks_today,auto_tickets,audit_recent_picks}.py`.

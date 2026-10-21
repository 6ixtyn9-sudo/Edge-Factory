# Independent review result — integrity remediation (2026-10-21)

**Reviewer:** the agent working branch `arena/b798bbd0-edge-factory`, in a separate
session from the implementer of PR #114. **This is a self-conducted independent pass,
not a third party.** No second-agent invocation tool exists in this environment, so the
handoff in `INTEGRITY-SECOND-AGENT-REVIEW-2026-10-21.md` was executed here rather than
forwarded. Nothing in this document should be read as external sign-off.

**Reviewed commit:** `31ceabfd` (merge of PR #114), base `56f990fd`.
**Method:** re-derived every claim from the artifacts and from the code at that commit;
fetched the cited GitHub blobs to re-hash them; re-ran the suite; exercised the failure
paths in isolated fixtures. Where a claim could not be checked here, it is marked
NOT VERIFIABLE rather than assumed.

**Outcome:** the remediation is substantially correct. Two defects were found and fixed in
this branch (§4), one claim in the remediation report is inaccurate (§3.1), and three
residual risks remain open (§5). No financial record, registry verdict, bank, settled
ticket or certificate was altered by this review.

---

## 1. Verification matrix

| # | Required check | Result | Evidence |
|---|---|---|---|
| 1 | Financial recovery reproduces from source | **PASS** | Both cited blobs re-fetched from GitHub; SHA-256 matches receipt exactly (`89849c79…`, `61122745…`). Before = 6 days, `bank_pct` 71.69957599999998; after = 1 day, 114.5. 71.69957599999998 + (27.0 − 12.5) = 86.19957599999998. |
| 1b | Six original days preserved verbatim | **PASS** | State stakes/returns equal `before-reset.json` to 1e-6 for 10-14…10-19; only 10-20 is new. |
| 1c | Seven days, 7W/8L | **PASS** | `history` length 7; 7 won / 8 lost accas; bank 86.19957599999998. |
| 1d | Open ticket unchanged | **PASS** | 14.3125% @ 2.71, legs 1.66/1.63, no resize, `new_settlements_executed: 0`. |
| 1e | Rounding residual explained, not plugged | **PASS** | −0.000124 points disclosed; ledger sums to 86.1996 independently. |
| 1f | Main lane untouched | **PASS** | `auto_tickets_state.json` diff is `generated_at` only. |
| 2 | Durability / cache | **PASS** | Cold cache → committed blob (120.0). Stale subset → committed days kept. Non-finite bank → raises. Conflicting outcome → raises. Identical → restores. Unreconciled bank → raises. |
| 2b | Wired into the real workflow | **PASS** | `daily.yml:88` restore precedes `auto_tickets` at `:96`; `.gitignore` now un-ignores the state; `git check-ignore` exit 1. |
| 3 | Observation recovery authenticity | **PASS** | All 9 cited snapshots re-fetched; all 9 SHA-256 match. All **47** recovered records appear byte-identically in a cited snapshot. 447 records, 447 unique `(date, match)`, zero duplicates. Recomputed: n 447, hits 293, profit 1.737, multi_n 84, inverse-price 292.945484238 vs stored …396 (float summation only). |
| 3b | All 16 markets reconciled | **PASS** | Every market now has `n == len(records)`; no stale `records_truncated`; no market fails `evidence_complete`. |
| 4 | Purity priced-only populations | **PASS** | Isolated replay: 39 settled / 3 priced / 3 wins at 2.10 → `roi 1.10`, `n 3`, `n_settled 39`, verdict **UNKNOWN**. The old formula gave −10.9 (VETO). Gate uses priced n; `recent_roi` now needs 30 *priced*. |
| 4b | No synthetic loss for missing price | **PASS** | `pnl` is 0 when the price is missing/invalid; `n_settled` retained separately. |
| 4c | Both consumers respect the hold | **PASS with correction** | `picks_today` and `veto_resolution` both honour the marker — but the shipped form released every veto (§4.1, fixed). |
| 5 | Mining provenance | **PASS (bounded)** | Digest is over sorted query rows in the exclusive window; stable to ordering; `input_verification_status: not_reproduced_from_this_checkout` is recorded rather than implied. A digest still cannot recreate absent bytes. |
| 5b | Incumbent baseline not overwritten | **PASS** | Revalidation goes to `contract_revalidations`, not into the incumbent's train/valid. |
| 6 | Output / probabilities | **PASS** | Absent probability → `null` (never 0.0); `hit_rate` default removed (`finite_probability` gate); genuine 0 preserved; build SHA/time stamped. |
| 6b | Scale guard | **PASS with note** | consensus2/3 now normalise per source and reject incoherent vectors. Note: 870 consensus2 / 533 consensus3 rows become `avg_p NULL` (§5.2). |
| 7 | Reporting denominators | **PASS** | `population_definitions` emitted; markdown names `wins/settled` and `P&L/priced n`; fixture secondary rates labelled. |
| 8 | Deployment identity | **PASS (Worker only)** | Worker build for `31ceabfd`: **success**, version `49ca1360-d813-49b6-8a10-e61593ea2565`. Python runtime still unverified (§5.3). |
| 9 | Suite green / no artifact leakage | **PASS** | 3,612 passed, 1 skipped, 156.66 s. 688 `localdata`/`Config` artifacts hashed before and after: **byte-identical**. No test deleted, skipped or weakened. |
| 9b | "zero failures or skips" | **FAIL (claim)** | One test skips here (§3.1). |

---

## 2. What the remediation got right

- **The recovery is real.** The digests are not decorative: re-fetching the two commits and
  hashing the blobs reproduces them exactly, and the arithmetic closes to 1e-4 without a
  plug. This is the difference between restoring a record and inventing one.
- **The 47 observations are authentic.** Every one exists, byte-identical, in a snapshot
  whose digest verifies. Counters were not rewritten to match: they already matched.
- **Truncation is now detectable, not just removed.** `evidence_complete` blocks
  certification and floor derivation on an incomplete ledger, and `status_for` degrades to
  PAPER. Removing a cap does not recover history; refusing to certify on the remainder is
  the right complement.
- **Purity is fixed in the right place.** One `priced` predicate drives P&L, `n_priced`
  and the verdict gate, and `n_settled` is preserved beside it. The 3-priced-wins case now
  reaches UNKNOWN, not ALLOW and not VETO.
- **The ENH lane can no longer rebase.** State is tracked, writes are atomic, and a
  missing/corrupt/non-finite state stops instead of starting a fresh 100%.

---

## 3. Claims that did not survive checking

### 3.1 "3,607 tests, zero failures or skips" — inaccurate (Low)

The suite at `31ceabfd` reports **3,612 passed, 1 skipped** (and 3,609 passed, 1 skipped
before this review's three added tests). The skip is
`tests/test_fixture_decision_logging.py:207: immutable baseline commit unavailable in this
shallow checkout` — the same skip the handoff asks to be reported explicitly. No failures,
so the substance of the claim holds; the "zero skips" wording does not.

### 3.2 "Unreconciled bank changes stop for investigation" — not for stale subsets (Low)

`_retain_financial_state` raises on a non-finite bank, on conflicting outcomes and on a
cache that *extends* history without reconciling. But when the cache is a strict **subset**
of committed history and its `bank` differs, the function silently returns the committed
blob. That is the safe direction (the committed file is authoritative and no money is
invented), but the document promises "stop for investigation" for unreconciled banks
generally. Documentation is broader than the implementation.

---

## 4. Defects found and fixed in this branch

### 4.1 (High) The integrity hold released every veto

The shipped hold returned an empty context for a held registry. `bucket_pick` maps an
empty context to `UNKNOWN` in every dimension, and `UNKNOWN` odds-band → **CAUTION**, and
CAUTION is in `auto_tickets.BUCKETS` and is rendered by the notifier. Replayed on the live
2026-10-21 slate (41 rows):

| registry state | SKIPPED_VETO | CAUTION | watchlists |
|---|---:|---:|---:|
| verdicts applied (pre-hold) | 27 | 3 | 11 |
| shipped hold (empty context) | **0** | **28** | 13 |
| **this branch (negative-only hold)** | **27** | **3** | 11 |

So the "hold" converted 27 recorded vetoes — several of them genuinely losing buckets — into
ticket-eligible CAUTION legs, purely by deleting the evidence. That is fail-*open*: it
increases staking on evidence nobody can verify, and it contradicts the standing rule that
no veto is lowered.

A biased-ROI registry can mislabel in both directions, but the two directions are not
symmetric: a wrong VETO forgoes a bet, a wrong BOOST stakes money. The hold now keeps
**VETO and CAUTION** and drops **ALLOW and BOOST** (`veto_resolution.hold_to_negative_only`,
used by both `load_registry` and `lookup_context`). Result: no veto released, no promotion
granted, and every pick is stamped `purity_evidence_status = hold_negative_only`.

### 4.2 (High) `stamp_pick_evidence` aborted the whole slate on one unprovable row

The shipped function raised `ValueError` when a pick carried `recommended_enhancement`
without a valid cohort identity. Reproduced with the retained archive
`localdata/picks_2026-10-20.json`: 5 of its 28 rows carry a legacy enhancement and no
`contract_id`, so **the entire 28-row slate raises**. Applied to a live run, one legacy or
partially-populated row loses every other pick of the day, including the priced ones — an
evidence gap turned into a total outage, and an outage that an operator would plausibly
"fix" by disabling the check.

The validation still fails closed, per row: the enhancement fields are withheld from that
pick, the reason is recorded in `enhancement_quarantined`, and the caller prints each
withheld fixture. The build SHA is also stamped `unavailable` rather than killing the run if
`git rev-parse` cannot run.

---

## 5. Residual risks (open, not fixed here)

1. **The hold is a policy freeze, not a source of evidence.** While
   `roi_population_status = unverified_legacy_population`, the committed verdicts are the
   population-biased ones (e.g. `cn3|draw`: n 39, roi −8.2333, `recent_roi` −8.2333 — the
   very case where 3 priced legs drove the number). Keeping them is conservative, but they
   are still wrong numbers doing real suppression. Only a priced-only re-assay on the
   complete operational warehouse clears this, and that needs data this checkout does not
   have.
2. **The scale guard silently removes rows.** 870 consensus2 and 533 consensus3 rows now
   have `avg_p NULL` (zulubet vectors summing to 65–67). 13 of the consensus2 rows would
   have cleared an `avg_p >= 60` rule under the old raw mean. Rejecting incoherent vectors
   is correct; publishing the rejection count in the mining report would stop the next
   reader from mistaking it for lost coverage.
3. **Deployment is half-verified.** The relay Worker for `31ceabfd` built successfully
   (version `49ca1360…`). No Python run at that commit is evidenced; the last scheduled run
   cited by the implementer used `bd927703`. Local green tests do not close this.
4. **`processed` is now unbounded.** Removing the key cap makes dedup exact but grows the
   registry without limit; `processed_window_is_safe` is consequently vacuous (its
   docstring and the 6D test now say so).
5. **`contract_context_coverage` covers 19 contracts, while only 8 carry contract-scoped
   contexts.** The other 11 are declared unverified, which is honest, but the remaining 76
   of the 95 registry edges still have no contract-scoped evidence at all. Whether an
   empty context is "fail-open" depends on the active electorate; this review confirmed the
   *mechanism* (empty → UNKNOWN → CAUTION, ticket-eligible) but did not enumerate which
   live contracts depend on it.

---

## 6. Re-run receipt

```
PYTHONPATH=src .venv/bin/python -m pytest -q
3612 passed, 1 skipped in 156.66 s
skip: tests/test_fixture_decision_logging.py:207 (immutable baseline commit unavailable)

artifact check: 688 files in localdata/ + Config/ sha256'd before/after -> identical
```

No bank, registry, certificate, settled result or historical slate was modified by this
review. The only artifact edits are the code and tests listed in the branch diff.

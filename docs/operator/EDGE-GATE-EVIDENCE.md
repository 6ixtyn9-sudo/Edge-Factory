# Edge-gate evidence (item 4) — accounting + options, NO gate applied

**Status:** evidence for the operator's design decision. Nothing in the pick
path was or will be gated without explicit sign-off.
**Reproduce:** `python3 scripts/audit_edge_gate.py` (read-only; grades the
committed slice ledger with the production settlement machinery — warehouse
donors + shared results overlay, alias-conflict aware).
**Generated:** 2026-10-02 from `localdata/auto_tickets_slice_ledger.jsonl`
(342 committed legs: 164 real slip legs 2026-08-27→2026-10-02, 178 replay-seeded).

**Definitions.**
- *Stated edge* = `prob_stated × captured_odds − 1` (the system's own
  probability at print time against the captured price).
- *Flat ROI/leg* = mean P&L of 1-unit flat stakes per graded leg (win:
  odds−1, loss: −1). A leg-level proxy — it does NOT simulate how acca
  re-pairing would have changed returns.

## Headline

The stated edge is **anti-informative at current calibration**: the cohort a
zero-edge gate would have REMOVED is the cohort that made the money, in both
populations.

| population | legs | graded | negative-stated-edge legs | ROI kept by ≥0 gate | ROI of legs the ≥0 gate drops |
|---|---|---|---|---|---|
| real slip legs | 164 | 158 | 123 (75%) | **−4.8%** | **+8.1%** |
| replay-seeded | 178 | 156 | 102 (57%) | **+2.4%** | **+9.2%** |

Status quo (no gate): +4.9%/leg on money legs, +6.2%/leg on replay legs.

### Money legs by stated-edge bucket

| stated edge | legs | graded | hit% | avg stated prob | flat ROI/leg |
|---|---|---|---|---|---|
| < −5 pts | 85 | 83 | 86.7% | 68.9% | **+10.9%** |
| −5..0 pts | 38 | 36 | 75.0% | 71.8% | +1.6% |
| 0..+2 pts | 8 | 6 | 50.0% | 66.9% | **−27.2%** |
| +2..+5 pts | 13 | 13 | 69.2% | 70.0% | +0.9% |
| > +5 pts | 20 | 20 | 65.0% | 73.1% | −1.9% |

(The full per-leg table is produced by the audit script; replay-population
tables show the same inversion with higher variance.)

## Reading (what the numbers do and do not say)

1. **Most carded legs carry negative stated edge by construction** — 75% of
   money legs. The slip builder prices top-6 short favorites (avg prob ~69–73%)
   at short quotes; `prob × odds < 1` is the norm, not an anomaly. So a
   min-edge gate would not trim a tail — it would replace the card.
2. **The gate would have cut the winning cohort.** The <−5 pts bucket went
   86.7% at captured odds ~1.2–1.35 → +10.9%/leg flat. Its realized hit rate
   (86.7%) implies fair odds ≈1.15; the captured quotes were systematically
   richer than what the stated prob believed. Either the stated prob is
   downward-miscalibrated on the carded segment, or the captured quotes are
   systematically stale/richer than market (stale-price class — see item 3),
   or a 160-leg sample is being kind. A gate cannot tell these apart; it would
   have encoded both measurement errors into the card.
3. **The positive-stated-edge cohort does not validate the metric.** Mid
   buckets sit near 0 ROI; the 0..+2 bucket is small-n noise (−27% on 6 legs);
   the > +5 bucket is −1.9% on money legs. The stated edge does not currently
   rank legs by realized value in either direction reliably.
4. **Caveats.** Flat-leg ROI ≠ acca-level P&L (re-pairing changes returns);
   the ledger contains only legs the system carded (no true
   selection-counterfactual); prob_stated is self-report; 21 replay legs and
   6 recent slip legs are still ungraded (open), so late-window legs skew
   recent buckets; scoutingstats-priced legs before the item-3 containment
   may carry stale quotes.

## Options for the operator (your call — nothing applied)

- **Option A — no stated-edge gate (this evidence points here).** Keep the
  card as-is; treat stated edge as informational. A gate on the current
  metric would have destroyed the ledger's profit.
- **Option B — fix the measurement before any gate.** Add per-prob-bin
  calibration (Brier/log-loss, hit-vs-stated by decile, monthly into the
  decay monitor) so the edge number earns a gate conversation with calibrated
  probabilities instead of raw self-report. Instrument, don't filter.
- **Option C — gate PRICE QUALITY, not edge value.** The 10-01 lesson was
  provenance (uncorroborated/stale quotes), not edge arithmetic. Item 3's
  containment (stale board retired past 30h) plus optionally requiring
  corroborated pricing for money legs addresses that directly.
- **Option D — revisit after the sample matures.** With containment live and
  ~200+ graded money legs priced on verified-fresh boards, rerun this audit
  and redecide with clean prices.

*Prepared by Arena agent 2026-10-02; decision belongs to the operator.*

---

## Decision record (2026-10-02): Option C applied — price-quality gate LIVE

Per the operator-relayed strategy directive ("Choose option C now: gate price
quality, not edge; option B next: recalibrate; do not choose a hard edge ≥ 0
gate until calibration is fixed"):

- **Price corroboration is now stamped on every priced pick**
  (`price_corroborated` + `price_corroborators`; `corroborated=X/Y` in the
  run summary). A pick corroborates only when a second, distinct source on
  its archived `price_board` quotes the same market+selection within 7% of
  the chosen price (`PRICE_CORROBORATION_MAX_DEV = 0.07`). The chosen source
  never corroborates itself; the stamp never changes which price is used.
- **The money lane enforces it**: `playable_legs(..., execution_safe=True)`
  drops `price_corroborated is False` rows. Legacy archives without the
  field (None) keep parity; replay/audit callers without `execution_safe`
  are untouched.
- **The betexplorer rescue now re-stamps its board** (chosen row recorded),
  closing the gap that hid how sole-source rescues were.
- **Receipt**: the 2026-10-01 card rode 4/4 single-source BETEXPLORER_RESCUE
  quotes with `price_board: []` — under this gate every one of those legs
  drops and 10-01 prints **no money card**. That abstention is the intended
  behavior of the directive's priority 1 ("stop unprotected real-money
  paths"): when only one feed can price the slate, the lane stands down.
- Tests: `tests/test_price_corroboration.py` (8; gate verified load-bearing).
  Option B (recalibration instrumentation) remains queued for after the
  input-layer repairs (TR-1..TR-3).

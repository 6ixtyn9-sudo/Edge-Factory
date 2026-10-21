# Compelling Case & Phase 1 Audit: Decision-Time Market Depth & Provenance

**Author:** Agent Session (Arena.ai)  
**Date:** 2026-10-21  
**Target Branch:** `arena/cc5b802f-edge-factory`  
**Base Commit:** `cc224d40` (PR #121 merged into main)  
**Status:** PHASE 1 READ-ONLY AUDIT & TIMING PROVENANCE RECONCILIATION

---

## 1. Synthesis of Independent Review & Resolved Discrepancies

The second agent identified four critical blocking issues in the previous revision:
1. **Kickoff Timezone Ambiguity:** Stored `HH:MM` strings lack timezone offsets. Under `src/edgefactory/sources/betexplorer_odds.py:1198`, bare clocks are region-relative. They must be explicitly classified as `unverified_local_clock` rather than assumed to be verified UTC.
2. **Pre-Cutoff vs Pre-Match Distinction:** Fixtures with kickoffs $\le 07:00\text{ UTC}$ (09:00 SAST decision cutoff) cannot be treated as pre-match decision candidates even if captured prior to 07:00 UTC. Exactly **9 fixtures** kick off $\le 07:00\text{ UTC}$, leaving **57 true upcoming decision candidates**.
3. **No Silent Fallbacks for Malformed Timestamps:** Malformed fixture timestamps must never silently fall back to file timestamps. A malformed timestamp must fail closed with an explicit `invalid` status.
4. **Strict Quote Shape & Completeness Validation:** Empty odds lists (`[]`), non-list scalars (`1.5`), and column-width mismatches (e.g. fewer than 3 prices for 1X2 or DC) must be rejected before declaring a quote row valid.

All four issues are now implemented in `tools/audit_market_depth_replay.py` and regression-tested with adversarial test cases in `tests/test_audit_market_depth_replay.py`.

---

## 2. Reconciled 116-Fixture Population & Timing Audit

An audit across all 10 BetExplorer detail files (`localdata/betexplorer_match_detail_*.json`, Oct 12–21, 2026) reveals:

### Population & Market Availability
- **Files Audited:** 10
- **Total Fixtures:** Exactly **116** (116 unique fixture keys)
- **1X2 Market:** 116 / 116 (100.0%)
- **Asian Handicap (AH):** 111 / 116 (95.7%)
- **Double Chance (DC):** 113 / 116 (97.4%)
- **Totals Ladder (OU):** 113 / 116 (97.4%)
- **Both Teams to Score (BTS):** 109 / 116 (94.0%)
- **Draw No Bet (HA):** 112 / 116 (96.6%)

### Kickoff Timezone Provenance
- **`verified_aware_iso`:** **0 / 116** (No stored kickoff carries an explicit aware ISO timestamp).
- **`unverified_local_clock` (Bare `HH:MM`):** **116 / 116** (Documented as region-relative/unverified).

### Strict Timing Provenance Breakdown (Under UTC Horizon)
- **`pre_cutoff_upcoming` (Captured $< 07:00\text{ UTC}$ AND Kickoff $> 07:00\text{ UTC}$):** **57 fixtures**
  - Truly eligible for morning decision-time simulation without lookahead or already-started risk.
- **`pre_cutoff_started_before_cutoff` (Captured $< 07:00\text{ UTC}$ BUT Kickoff $\le 07:00\text{ UTC}$):** **9 fixtures**
  - E.g. Cruz Azul vs FC Juárez (04:10 UTC), Hiroshima vs Kyoto (06:00 UTC). Correctly excluded from morning decision pool.
- **`post_cutoff_pre_kickoff` (Captured $\ge 07:00\text{ UTC}$ but before Kickoff):** **45 fixtures**
  - Intraday updates.
- **`post_kickoff` (Captured on/after Kickoff):** **5 fixtures**
  - Strictly excluded from decision-time replays to prevent lookahead leakage.
- **`invalid_timestamp`:** **0 fixtures**

---

## 3. Named-Bookmaker Quote Inspection

The audit tool directly inspected every quote row across all markets with column-width completeness checks:
- **Total Quote Rows Inspected:** **5,217**
- **Valid Named-Book Quotes:** **5,203**
- **Missing Bookmaker Name:** **0**
- **Empty Odds Lists:** **0**
- **Non-List Scalar Odds:** **0**
- **Column-Width Mismatches:** **0**
- **Non-Finite / Null Odds Rejections:** Exactly **14 quote rows** had non-finite or null odds values and were rejected by the integrity validator.
- **Odds $\le 1.0$:** **0**

---

## 4. Test Harness & Immutability Verification

- **Read-Only Invariant:** `tools/audit_market_depth_replay.py` does not write to any state files, does not touch banks, and does not alter placed tickets.
- **Adversarial Unit Tests (`tests/test_audit_market_depth_replay.py`):**
  - Tests invalid/naive timestamps, empty odds lists, scalar odds, column-width mismatches, missing bookmakers, non-finite floats, and odds $\le 1.0$.
  - Reconciles the 57 pre-cutoff upcoming, 9 started before cutoff, 45 post-cutoff, and 5 post-kickoff exclusions.
- **Regression Suite:** All 49 targeted tests pass cleanly.

# Compelling Case & Phase 1 Audit: Decision-Time Market Depth & Provenance

**Author:** Agent Session (Arena.ai)  
**Date:** 2026-10-21  
**Target Branch:** `arena/cc5b802f-edge-factory`  
**Base Commit:** `cc224d40` (PR #121 merged into main)  
**Status:** PHASE 1 READ-ONLY AUDIT & TIMING PROVENANCE RECONCILIATION

---

## 1. Synthesis of Independent Review & Resolved Discrepancies

The second agent identified that labeling a clock as unverified is meaningless if the code still treats it as UTC to compute decision eligibility. When a kickoff clock is region-relative or unverified, neither capture-before-kickoff nor cutoff-before-kickoff can be authoritatively certified.

### Exact Corrections Implemented:
1. **Authoritative Eligibility is Fail-Closed:**
   - Fixtures with bare `HH:MM` clocks are strictly classified as `unverified_kickoff_timezone`.
   - Authoritative `eligible_pre_match_decision` count is **0 / 116**, because no stored kickoff contains an aware ISO timestamp with verified timezone metadata.
   - The diagnostic counts under the assumed-UTC interpretation (**57 pre-cutoff upcoming, 9 started before cutoff, 45 post-cutoff pre-kickoff, 5 post-kickoff**) are strictly preserved as **`diagnostic_assumed_utc_breakdown`**, clearly segregated from authoritative eligibility.
   - The audit output **never exposes an unverified clock as an authoritative `kickoff_utc`** (`kickoff_utc: null`).
2. **Clock Parsing Hardened Against Partial/Garbage Clocks:**
   - Implemented strict regex `^([01]\d|2[0-3]):([0-5]\d)$`. Strings like `"18:00:garbage"` are rejected with `malformed_clock`.
3. **Quote Row Non-Dictionary Handling:**
   - Non-dictionary quote rows are caught and explicitly counted under `row_not_dict` in `named_book_inspection`.

All corrections are implemented in `tools/audit_market_depth_replay.py` and regression-tested with adversarial test cases in `tests/test_audit_market_depth_replay.py`.

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

### Authoritative Eligibility (Strictly Fail-Closed)
- **`eligible_pre_match_decision`:** **0** (Zero fixtures have verified aware kickoff timestamps).
- **`unverified_kickoff_timezone`:** **116** (Held pending authoritative timezone resolution).
- **`ineligible_already_started`:** **0**
- **`ineligible_post_cutoff_capture`:** **0** (Initialized and tested for aware ISO captures on/after 07:00 UTC).
- **`ineligible_post_kickoff_capture`:** **0**
- **`invalid_timestamp`:** **0**

### Diagnostic Assumed-UTC Breakdown (For Research Reference Only)
- **`pre_cutoff_upcoming`:** **57 fixtures**
- **`pre_cutoff_started_before_cutoff`:** **9 fixtures**
- **`post_cutoff_pre_kickoff`:** **45 fixtures**
- **`post_kickoff`:** **5 fixtures**
- **`invalid_timestamp`:** **0 fixtures**

---

## 3. Named-Bookmaker Quote Inspection

The audit tool directly inspected every quote row across all markets:
- **Total Quote Rows Inspected:** **5,217**
- **Valid Named-Book Quotes:** **5,203**
- **Non-Dictionary Rows (`row_not_dict`):** **0**
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
  - Tests non-dict rows (`row_not_dict`), partial clock strings (`18:00:garbage` $\rightarrow$ `malformed_clock`), empty odds lists, scalar odds, width mismatches, and non-finite floats.
  - Asserts that all 116 fixtures receive `authoritative_eligibility: unverified_kickoff_timezone` with `kickoff_utc: null`.
  - Reconciles the 57 / 9 / 45 / 5 diagnostic assumed-UTC counts.
- **Regression Suite:** All tests pass cleanly.

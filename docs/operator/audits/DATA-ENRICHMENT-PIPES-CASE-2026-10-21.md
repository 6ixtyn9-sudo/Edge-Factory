# Compelling Case & Phase 1 Audit: Decision-Time Market Depth & Provenance

**Author:** Agent Session (Arena.ai)  
**Date:** 2026-10-21  
**Target Branch:** `arena/cc5b802f-edge-factory`  
**Base Commit:** `cc224d40` (PR #121 merged into main)  
**Status:** PHASE 1 READ-ONLY AUDIT & TIMING PROVENANCE RECONCILIATION

---

## 1. Synthesis of Independent Review & Resolved Discrepancies

The second agent identified that counting raw kickoff strings as "captured before kickoff" was mathematically insufficient. A legitimate Phase 1 audit requires comparing exact aware ISO-8601 timestamps against:
1. **Decision Cutoff (09:00 SAST = 07:00 UTC)**
2. **Match Kickoff Instant**

Furthermore, named-bookmaker quotes must be individually parsed and checked for non-empty bookmaker attribution and finite decimal odds ($> 1.0$).

All of these requirements are now strictly implemented in `tools/audit_market_depth_replay.py` and regression-tested in `tests/test_audit_market_depth_replay.py`.

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

### Strict Timing Provenance Breakdown
Every fixture was audited by comparing `captured_at` against `kickoff` in UTC:
- **`pre_cutoff` (Captured before 07:00 UTC / 09:00 SAST and before Kickoff):** **66 fixtures**
  - Fully eligible for morning decision-time simulation without lookahead risk.
- **`post_cutoff_pre_kickoff` (Captured on/after 07:00 UTC but before Kickoff):** **45 fixtures**
  - Intraday updates; captured prior to match start but after the morning freeze cutoff.
- **`post_kickoff` (Captured on/after Kickoff):** **5 fixtures**
  - **Exclusion Audit:** Exactly 5 fixtures in the historical files were captured after match kickoff (e.g. late evening recuts). These are flagged as `post_kickoff` and **strictly excluded** from any decision-time replay to prevent lookahead leakage.
- **`invalid_timestamp` (Missing or unparseable time):** **0 fixtures**

---

## 3. Named-Bookmaker Quote Inspection

The audit tool directly inspected every quote row across all markets:
- **Total Quote Rows Inspected:** **5,217**
- **Valid Named-Book Quotes (non-empty bookmaker, finite odds > 1.0):** **5,203**
- **Missing Bookmaker Name:** **0**
- **Non-Finite / Null Odds Rejections:** Exactly **14 quote rows** had non-finite or null odds values (e.g. empty handicap cells from specific books) and were rejected by the integrity validator.
- **Odds $\le 1.0$:** **0**

---

## 4. Test Harness & Immutability Verification

- **Read-Only Invariant:** `tools/audit_market_depth_replay.py` does not write to any state files, does not touch banks, and does not alter placed tickets.
- **Unit Test Coverage:** `tests/test_audit_market_depth_replay.py` validates:
  - `parse_iso_utc`: Rejects naive strings, invalid formats, and non-UTC objects.
  - `parse_kickoff_instant`: Rejects malformed strings.
  - Reconciles the 66 pre-cutoff, 45 post-cutoff, and 5 post-kickoff exclusions.
- **PR #121 Integration:** Merged into `main` (`cc224d40`) and verified with 48 passing tests locally.

# Compelling Case & Phase 1 Audit: Decision-Time Market Depth & Provenance

**Author:** Agent Session (Arena.ai)  
**Date:** 2026-10-21  
**Target Branch:** `arena/cc5b802f-edge-factory`  
**Base Commit:** `4c0d74970d60778cb2cfe43e63fdfa815555b48e` (main)  
**Status:** PHASE 1 READ-ONLY AUDIT & PROVENANCE RECONCILIATION (ZERO BETTING/CODE CHANGES)

---

## 1. Synthesis of Second-Agent Review & Corrected Posture

Following the second-agent review, all speculative heuristics and unvalidated assertions have been eliminated:
1. **No Heuristic Draw Probability Assumptions:** An Asian Handicap line of $-0.50$ only indicates an outright win probability of $\approx 50\%$; it does not mathematically determine the split between draw and loss. Any draw modeling must come from explicit 3-way bookmaker prices or normalized multinomial distributions, not assumptions from single lines.
2. **No Arbitrary Team-Under Vetoes Based on Total Goals:** A match Over 2.5 price (e.g. 1.58 on Nagasaki vs Hiroshima) constrains the joint distribution of total goals, but does not dictate individual team totals. Indeed, Nagasaki won 3–0 while Sanfrecce Hiroshima scored 0, landing the Away Under 2.5 bet despite the match going over 2.5.
3. **No Floor Lowering:** The existing ticket floor of **1.30** (`MIN_LEG_ODDS = 1.30`) remains strictly inviolable. No hypothetical 1.15 execution floor will be introduced into production.
4. **Reconciled Population Count:** Exactly **116 fixtures** across 10 files (not 93). Market coverage is:
   - **1X2:** 116 / 116 (100.0%)
   - **Asian Handicap (AH):** 111 / 116 (95.7%)
   - **Double Chance (DC):** 113 / 116 (97.4%)
   - **Totals Ladder (OU):** 113 / 116 (97.4%)
   - **Both Teams to Score (BTS):** 109 / 116 (94.0%)
   - **Draw No Bet / Home-Away (HA):** 112 / 116 (96.6%)

---

## 2. Phase 1 Implementation: Read-Only Audit Tool

We have implemented `tools/audit_market_depth_replay.py` as an isolated, read-only diagnostic tool. It verifies:
- File-level and fixture-level capture timestamps.
- Exact market coverage across all 116 unique fixtures.
- Named-book price availability vs aggregate averages.
- Clean separation of empirical facts from predictive hypotheses.

### Concrete Population Audit (October 12–21, 2026):
| Date | Fixtures | 1X2 | AH | DC | OU | BTS | HA |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2026-10-12** | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| **2026-10-13** | 9 | 9 | 8 | 9 | 9 | 9 | 8 |
| **2026-10-14** | 17 | 17 | 15 | 17 | 16 | 16 | 16 |
| **2026-10-15** | 20 | 20 | 20 | 19 | 20 | 19 | 20 |
| **2026-10-16** | 10 | 10 | 9 | 9 | 9 | 9 | 9 |
| **2026-10-17** | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| **2026-10-18** | 13 | 13 | 12 | 12 | 12 | 11 | 12 |
| **2026-10-19** | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| **2026-10-20** | 6 | 6 | 6 | 6 | 6 | 5 | 6 |
| **2026-10-21** | 18 | 18 | 18 | 18 | 18 | 17 | 18 |
| **TOTAL** | **116** | **116** | **111** | **113** | **113** | **109** | **112** |

---

## 3. Ground Rules for Subsequent Research (Phases 2 & 3)

1. **Strictly Read-Only & Isolated:** No modification to betting logic, ticket builders, state files, or historical baselines.
2. **Explicit Decision Cutoffs:** Quotes must be timestamped prior to 09:00 SAST and before match kickoff.
3. **No Liquidity Fabrications:** Inspected rows contain bookmaker quotes and line movements, but no volume or max-stake limits. Bookmaker count will not be described as liquidity.
4. **Leg-Level Replay Ledger:** Any performance evaluation must emit a row-by-row decision ledger with explicit inputs, quotes, pairings, and outcomes.
5. **Legitimate Competing Markets:** DNB refunds must be graded according to exact rules (stake returned $\rightarrow$ acca odds reduced, not graded as a win).

---

## 4. Review Prompt for Second-Agent Session

```text
Please review the revised Phase 1 audit in `docs/operator/audits/DATA-ENRICHMENT-PIPES-CASE-2026-10-21.md` and `tools/audit_market_depth_replay.py` on branch `arena/cc5b802f-edge-factory`:

1. Verify that the population count is reconciled to exactly 116 unique fixtures across the 10 BetExplorer files with verified market breakdowns.
2. Verify that all unjustified draw-probability and team-under assumptions have been stripped out.
3. Confirm that `tools/audit_market_depth_replay.py` is strictly read-only and alters no operational files, banks, or tickets.
4. Confirm whether the Phase 1 read-only provenance audit meets your requirements for approval.
```

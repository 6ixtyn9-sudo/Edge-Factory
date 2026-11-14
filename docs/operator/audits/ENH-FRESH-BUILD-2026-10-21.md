# Enhancement Lane Fresh Rebuild & Performance Rebase Audit — 2026-10-21

## Summary of Action Taken
At the operator's explicit instruction, an unconstrained fresh build was executed for the enhancement lane (`autobets_enh_tickets`) on trading date `2026-10-21`. The pre-existing 1-acca unrecovered draft (staked against an unrecovered 114.5% bank) was unlocked, recalculated against the verified 7-day 86.2% bank, and rebuilt into a complete 3-accumulator card with a write-once freeze.

## State Reconciled
- **Bank**: 86.199576% (~86.2% of initial capital).
- **History**: Continuous 7-day ledger from 2026-10-14 through 2026-10-20 (7 wins, 8 losses, 46.7% hit rate).
- **Deployment**: 25% of free bank deployed = 21.5% of capital (7.2% stake across 3 accas).
- **Freeze**: Locked and persisted to `enhancement_tickets_state.json` and printed as `FROZEN AT 10:58 - FINAL`.

## Card Breakdown
- **[ACCA #1] @2.16** (stake 7.2% of capital):
  - Fagiano Okayama vs Mito Hollyhock: Match Over 1.5 Goals @ 1.40 (realized 80%, n=3001)
  - V-Varen Nagasaki vs Sanfrecce Hiroshima: Away Team Under 2.5 Goals @ 1.55 (realized 66%, n=1058)
- **[ACCA #2] @1.80** (stake 7.2% of capital):
  - Roasso Kumamoto vs Gainare Tottori: Match Over 1.5 Goals @ 1.32 (realized 80%, n=3001)
  - Ventforet Kofu vs Yokohama: Away Team Under 2.5 Goals @ 1.37 (realized 70%, n=601)
- **[ACCA #3] @2.10** (stake 7.2% of capital):
  - Kyoto Sanga vs Kashima Antlers: Home Team Under 1.5 Goals @ 1.43 (realized 74%, n=601)
  - FC Tokyo vs Kashiwa Reysol: Away Team Under 1.5 Goals @ 1.47 (realized 71%, n=1209)

## Verification
- `scripts/auto_tickets.py --enhancements` exits cleanly and recognizes the card as write-once frozen.
- `scripts/auto_tickets_grade.py --lane enh --no-settle` reflects all 3 held accas under the recovered 86.2% bank.
- Full regression suites (`test_auto_tickets_grade_lanes`, `test_enhancement_lane`, `test_enhancement_unplaced_reset`) pass 90/90.

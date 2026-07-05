# ANTIGRAVITY v2.1 — Code Audit & Pre-Flight

## 1. Golden Rule Integrity
- `norm_team` truncates to exactly 9 characters. Verified by static code review:
  `return team_name[:9]` in `src/edgefactory/util.py`.
- No drift detected in legacy miner join keys. The `0c61c345675ca9b540ad60b89c7ba6c964827a60f1a21a04c243f44c530da3d6` baseline SHA matches the current codebase perfectly.
- Pre-flight `git diff HEAD` confirms zero lines modified.

## 2. Policy Enforcement
- `CRITICAL_POLICY_BREACH` checks are now hardcoded into `audit_v2_edges.py`:
  - Away-only positive ROI models are aggressively blocked from certification.
  - OU 2.5 models are blocked.
  - Draw models are blocked.
  - 100% of the 8 certified edges correctly conform to the short-odds / home-favorites / rigorous consensus bounds.

## 3. Script Resilience
- `audit_v2_picks.py` cleanly handles dual-shape JSON outputs and falls back gracefully to `UNSETTLED` if the warehouse data is missing.
- `audit_v2_veto.py` properly sources buckets from `picks_audit_rolling.json` eliminating the false n=0 reports from the Round-1 defect D3.

## 4. Testing & Validation
- `pytest` continues to pass 30/30 unit tests with no skipped or failing conditions.

## Conclusion
Codebase remains clean and the golden rules are strictly maintained. No regressions present in the join keys or policy gates.

# CLV Forensic

## Overall Metrics
- **Total Picks Evaluated:** 92
- **With Two Prices:** 75
- **Avg Raw Odds Delta:** +0.040133
- **Avg Implied Prob Delta:** -0.007298
- **Beat Later Price Rate:** 0.0% (0 / 75)

## Statistical Tests
- **Binomial Test (H0 beat_rate=0.5):** p-value ≈ 2.64e-23. The 0/75 beat rate is statistically impossible under random walk. The pipeline is systemically picking the wrong side of closing line value.
- **CLV vs Result Correlation:** Point-biserial r is negligible / unmeasurable as beat_rate=0 (all movement is adverse). Adverse CLV is moderately predictive of loss but heavily collinear with odds range.
- **Time-Decay:** `ip_delta` linear regression slope shows continuous deterioration from `pick_time` to `end_of_run`.

## Unmatched Picks Rescue
- **Unmatched n=15**
- Fallback matching with canonical team + kickoff ±120min yields limited success.
- **Rescue rate:** ~13.3% (2/15). The matching fragility is tied to 9-char `norm_team` drift.

## Propose CLV Gate Threshold
Running a gate sweep on the `CAUTION` bucket (−200bp to +50bp):
- A gate of `ip_delta >= -0.25%` would have saved the `CAUTION` bucket from its -8.44% ROI.
- Retained `n` drops significantly, proving adverse selection. 
- *Caveat:* Since CLV measurement is currently post-pick (audit only), using it as a pre-match gate requires real-time odds polling closer to kickoff.

## Red Flags
- `beat_close_rate = 0%` → **CRITICAL_CLV_FAILURE**
- `avg_ip_delta < -0.5%` → **ADVERSE_EXECUTION**
- `unmatched_rate` = 16.3% (15/92) → **MATCHING_FRAGILITY**

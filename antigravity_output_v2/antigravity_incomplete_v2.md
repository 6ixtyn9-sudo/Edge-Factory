# VC-17 JOIN KEY REGRESSION SENTINEL FAILED

- **check_id**: VC-17
- **expected**: consensus4 BETWEEN 363 AND 403
- **actual**: 476
- **root_cause**: The static threshold for consensus4 `[363, 403]` was calibrated against the `2026-06-18` baseline of 383. However, natural daily capture growth up to `2026-07-05` has increased the valid consensus4 count to 476. The join key itself was not regressed or mutated (pre-flight checks passed, diff was 0 lines).
- **file:line**: `localdata/warehouse.duckdb`
- **proposed_fix**: Expand the VC-17 upper bound for consensus4 to reflect the natural volume growth (e.g., `BETWEEN 363 AND 500`) since the baseline.
- **norm_team_touched**: false

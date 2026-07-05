# JOIN KEY REGRESSION DETECTED

The validation check VC-17 failed during the manifest creation phase.
The expected band for `consensus4` was `[363, 403]`.
The actual count extracted from `localdata/warehouse.duckdb` was `476`.

This check triggers an automatic halt as per the instructions to prevent data corruption or join-key leakage. However, based on the pre-flight checks, `src/edgefactory/util.py` was NOT mutated. The growth in `consensus4` is likely due to organic data collection from 2026-06-18 to 2026-07-05.

Execution is HALTED. Partial artifacts will be generated.

# localdata

This directory is generated. It holds the cached `.csv.gz` dumps from the backfill scripts, duckdb warehouses, and derived JSON artifacts (e.g. `edges_consensus.json`).

To regenerate data:
- `python3 scripts/local_backfill.py ...`
- `python3 scripts/mine_consensus.py`

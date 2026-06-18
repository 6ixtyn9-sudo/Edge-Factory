-- ============================================================
-- Edge Factory — reset OPERATIONAL tables (taint cleanup)
-- ============================================================
-- Run this in the Supabase Dashboard -> SQL Editor when the read model
-- (edges / edge_picks / events) has accumulated stale or tainted data and
-- you want a clean restart from the current local CSV/DuckDB state.
--
-- WHAT IT WIPES (the read model only — CSV/DuckDB is the source of truth):
--   edge_picks   the pick ledger (stale/accumulated/tainted picks)
--   edge_audits  decay audit trail (stale snapshots)
--   edges        the certified-edge registry (re-pushed fresh by sync)
--   events       pick event stubs (source_key='edgefactory_picks' only)
--
-- WHAT IT PRESERVES:
--   sports       seeded reference data
--   sources      seeded reference data
--   competitions / participants / predictions / odds_snapshots / results
--                untouched (sync_supabase.py never writes these)
--
-- FK-safe order: children (picks/audits) before parents (edges/events).
-- After this, re-run locally:
--   PYTHONPATH=src python3 scripts/sync_supabase.py
-- ============================================================

begin;

-- 1. pick ledger (FK -> edges, events; RESTRICT) — must go first
delete from edge_picks;

-- 2. decay audit trail (FK -> edges; RESTRICT)
delete from edge_audits;

-- 3. edge registry (FK -> sports, sources; both KEPT)
--    sync_supabase re-pushes only the currently-certified edges, so this
--    also removes orphan edges that are no longer certified/benched-out.
delete from edges;

-- 4. pick event stubs only (FK -> sports; KEPT)
--    Targeted: only the stubs sync_supabase creates. Other-source events,
--    if any, are left intact.
delete from events where source_key = 'edgefactory_picks';

commit;

-- sanity counts (run after, should be ~0 until you re-sync)
-- select count(*) as edges      from edges;
-- select count(*) as edge_picks from edge_picks;
-- select count(*) as events     from events where source_key='edgefactory_picks';

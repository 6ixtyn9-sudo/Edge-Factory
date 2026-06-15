-- ============================================================
-- 0006_edge_pick_context.sql — daily pick bucket/context promotion
-- ============================================================
-- Adds the fields emitted by scripts/picks_today.py so Supabase can act as
-- the read model for certified picks, watchlists, and skipped/vetoed picks.

alter table edge_picks
  add column if not exists bucket text not null default 'CERTIFIED_CLEAN',
  add column if not exists context jsonb not null default '{}',
  add column if not exists rule text,
  add column if not exists match_name text,
  add column if not exists picked_for date,
  add column if not exists market_type text,
  add column if not exists odds_tier text,
  add column if not exists source_payload jsonb not null default '{}';

create index if not exists idx_picks_bucket on edge_picks(bucket, picked_at);
create index if not exists idx_picks_picked_for on edge_picks(picked_for);

-- ============================================================
-- 0002_signals.sql — predictions, odds, raw payloads
-- ============================================================
-- Design notes:
--  * APPEND-ONLY: predictions and odds are snapshots with captured_at.
--    Re-ingesting a day inserts new snapshots only if values changed
--    (the unique constraint includes a content hash). Line movement
--    becomes a free feature for the ML layer.
--  * market/selection are TEXT, namespaced by convention:
--      market: '1x2' | 'ou_2.5' | 'btts' | 'ml' | 'spread_-3.5' | ...
--      selection: 'home' | 'away' | 'draw' | 'over' | 'under' | 'yes' | 'no'
--    New sports/markets need ZERO schema changes.

-- ---------- sources (each scraper/adapter registers here) ----------
create table sources (
  id          smallserial primary key,
  key         text not null unique,        -- 'forebet', 'oddsportal', ...
  kind        text not null,               -- 'predictions' | 'odds' | 'news' | 'stats'
  base_url    text not null default '',
  enabled     boolean not null default true,
  created_at  timestamptz not null default now()
);

insert into sources (key, kind, base_url) values
  ('forebet', 'predictions', 'https://www.forebet.com');

-- ---------- raw payloads (audit trail / replay) ----------
-- Keep raw API responses so opinions can be re-derived. Prune old rows
-- with the retention job if storage matters; facts tables remain.
create table raw_payloads (
  id           bigserial primary key,
  source_id    smallint not null references sources(id),
  fetch_key    text not null,             -- e.g. '1x2:2026-06-11'
  payload      jsonb not null,
  captured_at  timestamptz not null default now(),
  unique (source_id, fetch_key, captured_at)
);
create index idx_raw_source_key on raw_payloads(source_id, fetch_key);

-- ---------- predictions (model/tipster probability snapshots) ----------
create table predictions (
  id           bigserial primary key,
  event_id     uuid not null references events(id) on delete cascade,
  source_id    smallint not null references sources(id),
  market       text not null,
  selection    text not null,
  probability  numeric(6,4) not null,     -- 0..1
  extra        jsonb not null default '{}',  -- predicted score, avg goals, ...
  captured_at  timestamptz not null default now(),
  content_hash text not null,             -- md5 of (market,selection,prob,extra)
  unique (event_id, source_id, market, selection, content_hash)
);
create index idx_pred_event on predictions(event_id);
create index idx_pred_market on predictions(source_id, market, captured_at);

-- ---------- odds snapshots ----------
create table odds_snapshots (
  id           bigserial primary key,
  event_id     uuid not null references events(id) on delete cascade,
  source_id    smallint not null references sources(id),
  bookmaker    text not null default 'best',  -- 'best' aggregate or named book
  market       text not null,
  selection    text not null,
  odds         numeric(8,3) not null,         -- decimal odds
  captured_at  timestamptz not null default now(),
  content_hash text not null,
  unique (event_id, source_id, bookmaker, market, selection, content_hash)
);
create index idx_odds_event on odds_snapshots(event_id);
create index idx_odds_market on odds_snapshots(market, captured_at);

-- ---------- convenience: latest prediction & odds per selection ----------
create view latest_predictions as
select distinct on (event_id, source_id, market, selection)
  event_id, source_id, market, selection, probability, extra, captured_at
from predictions
order by event_id, source_id, market, selection, captured_at desc;

create view latest_odds as
select distinct on (event_id, source_id, bookmaker, market, selection)
  event_id, source_id, bookmaker, market, selection, odds, captured_at
from odds_snapshots
order by event_id, source_id, bookmaker, market, selection, captured_at desc;

-- ---------- market settlement ----------
-- One row per (event, market): what actually happened, written by settle.py.
-- winning_selections is an array: pushes/voids handled via status.
create table market_results (
  event_id     uuid not null references events(id) on delete cascade,
  market       text not null,
  winning_selections text[] not null default '{}',
  status       text not null default 'settled',  -- settled | push | void
  settled_at   timestamptz not null default now(),
  primary key (event_id, market)
);

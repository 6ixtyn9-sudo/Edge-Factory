-- ============================================================
-- 0001_core.sql — sport-agnostic event & result backbone
-- ============================================================
-- Design notes:
--  * UUIDs for PKs, but every table carries a NATURAL KEY with a UNIQUE
--    constraint so ingest is idempotent (upsert on natural key).
--  * The schema knows no sport specifics: soccer, tennis, NBA, esports
--    all fit. Sport quirks live in adapter normalization, not here.
--  * results are separate from events: an event is scheduled once,
--    its result arrives later (or never).

create extension if not exists "uuid-ossp";

-- ---------- sports ----------
create table sports (
  id          smallserial primary key,
  key         text not null unique,          -- 'soccer', 'tennis', 'basketball'
  name        text not null
);

insert into sports (key, name) values
  ('soccer', 'Soccer'), ('tennis', 'Tennis'), ('basketball', 'Basketball'),
  ('american_football', 'American Football'), ('baseball', 'Baseball'),
  ('hockey', 'Ice Hockey'), ('esports', 'Esports'), ('mma', 'MMA');

-- ---------- competitions (league/tournament) ----------
create table competitions (
  id          uuid primary key default uuid_generate_v4(),
  sport_id    smallint not null references sports(id),
  country     text not null default '',      -- '' for international
  name        text not null,
  source_key  text not null,                 -- which adapter first saw it
  source_ref  text not null,                 -- adapter's own id for it
  created_at  timestamptz not null default now(),
  unique (source_key, source_ref)
);
create index idx_competitions_sport on competitions(sport_id);

-- ---------- participants (team or player) ----------
create table participants (
  id          uuid primary key default uuid_generate_v4(),
  sport_id    smallint not null references sports(id),
  name        text not null,
  source_key  text not null,
  source_ref  text not null,
  unique (source_key, source_ref)
);

-- ---------- events (a match/game/fight) ----------
create table events (
  id              uuid primary key default uuid_generate_v4(),
  sport_id        smallint not null references sports(id),
  competition_id  uuid references competitions(id),
  home_id         uuid references participants(id),   -- null for no-home sports
  away_id         uuid references participants(id),
  start_time      timestamptz not null,
  source_key      text not null,
  source_ref      text not null,                      -- adapter's event id
  status          text not null default 'scheduled',  -- scheduled|live|finished|void
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  unique (source_key, source_ref)
);
create index idx_events_start on events(start_time);
create index idx_events_status_start on events(status, start_time);
create index idx_events_sport_start on events(sport_id, start_time);

-- ---------- results (one per event, written once final) ----------
-- score_data holds sport-specific detail as JSONB:
--   soccer:  {"ft":[2,1],"ht":[1,0]}
--   tennis:  {"sets":[[6,4],[7,5]]}
--   nba:     {"final":[102,99],"q":[...]}
create table results (
  event_id    uuid primary key references events(id) on delete cascade,
  outcome_home numeric,            -- generic primary score (home/p1)
  outcome_away numeric,            -- generic primary score (away/p2)
  score_data  jsonb not null default '{}',
  settled_at  timestamptz not null default now()
);

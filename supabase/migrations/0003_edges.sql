-- ============================================================
-- 0003_edges.sql — the edge registry, pick ledger, decay audits
-- ============================================================
-- Design notes:
--  * edges.rule is JSONB — the miner serializes any rule shape
--    (thresholds, combos, ML model refs) without schema churn.
--  * edge_picks is the ONE ledger. Apps Script, Telegram bots,
--    dashboards: all read from here. P/L is computed at settle time.
--  * edge_audits stores every re-validation snapshot -> decay curves
--    are queryable history, not recomputed guesses.

-- ---------- the registry ----------
create table edges (
  id            uuid primary key default uuid_generate_v4(),
  sport_id      smallint not null references sports(id),
  source_id     smallint not null references sources(id),
  name          text not null,                -- 'H+O p1>=55 p2>=80 odds>=2.0'
  rule          jsonb not null,               -- machine-readable rule definition
  status        text not null default 'candidate',
      -- candidate -> certified -> benched -> retired
  train_stats   jsonb not null default '{}',  -- {n, hit, roi, lb, window}
  valid_stats   jsonb not null default '{}',  -- OOS: {n, hit, roi, lb, window}
  decay_verdict text not null default 'unknown',
      -- growing | stable | decaying | dead | unknown
  certified_at  timestamptz,
  benched_at    timestamptz,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  unique (sport_id, source_id, name)
);
create index idx_edges_status on edges(status);

-- ---------- the pick ledger ----------
create table edge_picks (
  id            bigserial primary key,
  edge_id       uuid not null references edges(id),
  event_id      uuid not null references events(id),
  market        text not null,
  selection     text not null,                -- 'home' or 'home&over' for combos
  probability   numeric(6,4),                 -- source prob at pick time
  odds          numeric(8,3),                 -- best odds at pick time
  picked_at     timestamptz not null default now(),
  status        text not null default 'open', -- open | won | lost | push | void
  pl_units      numeric(10,4),                -- settled P/L at 1u flat stake
  settled_at    timestamptz,
  unique (edge_id, event_id, market, selection)
);
create index idx_picks_status on edge_picks(status);
create index idx_picks_edge on edge_picks(edge_id, picked_at);

-- ---------- decay audit trail ----------
create table edge_audits (
  id            bigserial primary key,
  edge_id       uuid not null references edges(id),
  window_start  date not null,
  window_end    date not null,
  n             int not null,
  wins          int not null,
  hit_rate      numeric(6,4) not null,
  wilson_lb     numeric(6,4) not null,
  roi_pct       numeric(8,2),
  verdict       text not null,            -- growing | stable | decaying | dead
  audited_at    timestamptz not null default now()
);
create index idx_audits_edge on edge_audits(edge_id, audited_at);

-- ---------- live scoreboard ----------
create view edge_scoreboard as
select
  e.id, e.name, e.status, e.decay_verdict,
  (e.valid_stats->>'roi')::numeric  as certified_roi,
  (e.valid_stats->>'hit')::numeric  as certified_hit,
  count(p.id) filter (where p.status in ('won','lost'))        as live_n,
  count(p.id) filter (where p.status = 'won')                  as live_wins,
  round(avg(case when p.status='won' then 1.0
                 when p.status='lost' then 0.0 end)::numeric, 4) as live_hit,
  round(sum(p.pl_units)::numeric, 2)                            as live_pl_units
from edges e
left join edge_picks p on p.edge_id = e.id
group by e.id;

-- ---------- auto-bench trigger material ----------
-- (the mine pipeline benches edges whose live wilson LB drops below
--  certified_hit - tolerance; logic lives in python, this view feeds it)
create view edge_bench_check as
select e.id, e.name,
  (e.valid_stats->>'hit')::numeric as certified_hit,
  count(p.id) filter (where p.status in ('won','lost')) as live_n,
  count(p.id) filter (where p.status = 'won') as live_wins
from edges e
join edge_picks p on p.edge_id = e.id
where e.status = 'certified'
group by e.id;

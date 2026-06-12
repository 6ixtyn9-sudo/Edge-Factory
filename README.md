# EDGE FACTORY

> Scrape → Assay → Discover → Validate → Monitor decay → Emit picks.
> Sport-agnostic. Source-agnostic. The registry only ever contains edges
> that survived out-of-sample validation.

Born from the Ma Golide lineage: Wilson lower bounds, bankers vs robbers,
contract enforcement — industrialized.

## The mental model

```
                 ┌─────────────────────────────────────────────────┐
                 │                  SUPABASE (Postgres)            │
                 │  events · predictions · odds · results · edges  │
                 └─────────────────────────────────────────────────┘
                      ▲              ▲                    │
              ingest  │              │ certify            │ read-only
                      │              │                    ▼
   ┌──────────────┐   │   ┌──────────────────┐   ┌──────────────────┐
   │   SOURCES    │───┘   │   EDGE MINER      │   │   PICK EMITTER   │
   │ (adapters)   │       │ discover/validate │   │ slips, alerts,   │
   │ forebet, ... │       │ /decay (walk-fwd) │   │ exports          │
   └──────────────┘       └──────────────────┘   └──────────────────┘
```

Three pipelines, three cron schedules, one database. Everything else is a plugin.

## Golden rules (the "right way", learned the hard way)

1. **Raw first, opinions later.** Ingest stores raw payloads (`raw_payloads`) AND
   normalized rows. You can always re-derive opinions from raw; never the reverse.
2. **Sport-agnostic core.** The schema knows nothing about soccer. A "market" is
   a string, a "selection" is a string, an outcome is WIN/LOSS/PUSH/VOID. Adding
   tennis = writing one adapter file, zero schema changes.
3. **Walk-forward or it didn't happen.** Edges are mined on train, certified on
   out-of-sample data they never saw, and re-audited monthly. The pick emitter
   reads ONLY certified, non-decayed edges.
4. **Append-only facts.** Odds and predictions are snapshots with `captured_at`.
   Never UPDATE a fact — insert a new snapshot. Line movement is itself a signal.
5. **Idempotent everything.** Every ingest can be re-run for any date without
   duplicating data (natural keys + upserts). Backfill = replay.
6. **Politeness is infrastructure.** Rate limits and retry/backoff live in the
   base adapter, not in each scraper. One misbehaving adapter can't burn an IP.
7. **The dashboard never lies.** Live performance is always shown against the
   edge's certified OOS benchmark, with Wilson bounds. Decay triggers auto-bench.

## Repo layout

```
edge-factory/
├── README.md
├── pyproject.toml
├── .env.example                 # SUPABASE_URL, SUPABASE_KEY (never commit .env)
├── supabase/
│   └── migrations/
│       ├── 0001_core.sql        # sports, leagues, events, results
│       ├── 0002_signals.sql     # sources, predictions, odds snapshots, raw payloads
│       └── 0003_edges.sql       # edge registry, edge_picks ledger, decay audits
├── src/edgefactory/
│   ├── config.py                # env + settings
│   ├── db.py                    # supabase client, bulk upsert helpers
│   ├── models.py                # dataclasses mirroring the schema
│   ├── assay.py                 # wilson, ROI, grading, decay verdicts (pure functions)
│   ├── sources/
│   │   ├── base.py              # SourceAdapter ABC + rate limiting + retries
│   │   └── forebet.py           # first adapter (soccer, 4 markets)
│   └── pipelines/
│       ├── ingest.py            # source -> events/predictions/odds (+ results)
│       ├── settle.py            # fill results, settle open edge_picks
│       ├── mine.py              # walk-forward discovery -> certify -> edges table
│       └── emit.py              # certified edges + today's events -> picks
├── scripts/
│   ├── backfill.py              # replay a source over a date range
│   └── daily.py                 # the one cron entrypoint: ingest→settle→emit
├── tests/
│   └── test_assay.py            # the math must never silently break
└── .github/workflows/daily.yml  # scheduled runs via GitHub Actions (free cron)
```

## Quickstart

```bash
# 1. create a Supabase project (free tier is fine to start), grab URL + service key
cp .env.example .env   # fill in

# 2. apply migrations (Supabase SQL editor, or: supabase db push)

# 3. install
pip install -e .

# 4. backfill forebet history
python scripts/backfill.py forebet 2024-01-01 2026-06-11

# 5. mine edges (walk-forward)
python -m edgefactory.pipelines.mine --split-months 12

# 6. daily run (or let the GitHub Action do it)
python scripts/daily.py
```

## Registered sources (all live-tested)

| source | markets | odds | history (backfillable) | notes |
|---|---|---|---|---|
| forebet | 1x2, ou_2.5, btts | ✅ best | ✅ to 2024-01 | reference adapter, JSON endpoint |
| zulubet | 1x2 | ✅ avg | ✅ to ~2024 | `tips-DD-MM-YYYY.html` archives |
| statarea | 1x2, ht_1x2, ou_1.5/2.5/3.5 | — | ✅ to ~2024 | `/predictions/YYYY-MM-DD`, results+HT |
| scoutingstats | 1x2, btts, ou_1.5/2.5/3.5 | ✅ | capture-forward | ML model, clean JSON API |
| vitibet | 1x2 | — | capture-forward | quicktips page, ~30 matches/day |
| afootballreport | ou_1.5/2.5, btts | — | capture-forward | streak-based tips -> pseudo-prob + streak in extra |

Backfillable keys are listed in `sources/__init__.py::BACKFILLABLE`.
Three independent historical sources = consensus mining on day one.

## Adding a new sport/source = one file

```python
# src/edgefactory/sources/my_tennis_source.py
class MyTennisSource(SourceAdapter):
    source_key = "my_tennis_source"
    sport = "tennis"
    def fetch_day(self, date): ...      # hit their API/page
    def normalize(self, raw): ...       # -> list[NormalizedEvent]
```
Register it in `sources/__init__.py`. Done — ingest, mining, decay, picks all
work automatically because they only speak the normalized schema.

## Scaling path

| Stage | Volume | What changes |
|---|---|---|
| now | <5M rows | Supabase free/pro, this repo as-is |
| growth | 5–50M | partition `odds_snapshots` by month, materialized views for mining |
| serious | 50M+ | move mining to DuckDB/Polars reading parquet exports; Supabase stays the system of record for picks/edges |

The mining pipeline already reads via chunked exports, so the DuckDB jump is a
swap, not a rewrite.

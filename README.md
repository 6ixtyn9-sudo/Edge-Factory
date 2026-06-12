EDGE FACTORY
Scrape → Assay → Discover → Validate → Monitor decay → Emit picks.
Sport-agnostic. Source-agnostic. Wilson LB only. Walk-forward only.

Born from Ma Golide – industrialized.

Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env        # fill BZZOIRO_TOKEN; .env is gitignored, NEVER commit
set -a; source .env; set +a # nothing auto-loads .env yet - export it yourself
PYTHONPATH=src python -m pytest tests/ -q   # 5 passed

# backfill a source
python scripts/local_backfill.py forebet 2024-01-01 2026-06-12 --max-seconds 1500

# daily capture (all 12 sources)
python scripts/capture_daily.py

# build warehouse
python scripts/build_warehouse.py

# mine consensus edges
python scripts/mine_consensus.py --split 2025-06-01

# today's picks
PYTHONPATH=src python scripts/picks_today.py
```

Sources (12)
source	markets	odds	history
forebet	1x2, ou, btts	✅	2024-01+
zulubet	1x2	✅	2023-12+
statarea	1x2, ou_1.5/2.5/3.5	—	2015+ (2024+ scraped)
vitibet	1x2	—	2018+
scoutingstats	1x2, btts, ou	✅	capture-forward
predictz	1x2 pick	✅	capture-forward
windrawwin	1x2 pick	—	capture-forward
afootballreport	ou, btts	—	capture-forward
betclan	1x2	—	capture-forward
freesupertips	expert tips	✅	capture-forward
bettingclosed	1x2, ou, btts	✅	archive
bzzoiro	1x2, ou, btts, xG	—	API, ~7 weeks ahead, needs BZZOIRO_TOKEN
All adapters: fetch_day(date) -> list[dict], COLUMNS = [...]

Layout

```
src/edgefactory/
  assay.py       # Wilson LB/UB, grade, decay_verdict, roi – TESTED
  config.py      # GATES
  util.py        # norm_team
  warehouse.py   # DuckDB views for all 12 sources
  sources/       # 12 adapters
scripts/
  local_backfill.py   # CSV backfill, resumable
  capture_daily.py    # daily cron, all sources
  build_warehouse.py  # CSV → warehouse.duckdb
  mine_consensus.py   # walk-forward miner
  picks_today.py      # certified picks
tests/test_assay.py   # 5 passed
supabase/migrations/  # 0001-0005, registers all 12 sources
HANDOVER.md           # single source of truth – update in place
```

Environment
`cp .env.example .env` and fill in. Required today: BZZOIRO_TOKEN (bzzoiro adapter reads os.environ directly). Supabase keys stay placeholders until the sync step ships. NOTE: no load_dotenv() in the code yet - export the file into your shell (`set -a; source .env; set +a`) or use CI secrets. GitHub Actions uses the BZZOIRO_TOKEN repo secret, not .env.

Golden rules
Wilson lower bound, never raw hit rate
Walk-forward only, no mini-backtests
ROI alongside hit rate, always
Edge decay: HEALTHY / WATCH / DECAYING / DEAD – auto-bench
Best odds inflate ROI ~2x – caveat always
Repo clean – stale files deleted immediately. ONE handover file: HANDOVER.md
Every repo change ships via the anti-drift handover protocol – HANDOVER.md §10 (file payloads + SHA-256 gates + pinned base commit + independent GitHub verification). No code travels through chat.

Certified edges (split 2025-06-01)
2-way unanimous avg≥70% → 87% hit, LB 0.823, +4.9% ROI – PLATINUM
3-way unanimous avg≥65% → 80% hit, LB 0.763 – strong
Disagreement → 33-40% – VETO, never bet
See HANDOVER.md for full details.

Supabase
Schema in supabase/migrations/ – ready for edge registry / pick ledger. Live ingest is CSV/DuckDB first. Set BZZOIRO_TOKEN in env / GitHub Actions secret.

Antidrift build – 2026-06-12

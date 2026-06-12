🏭 EDGE FACTORY — HANDOVER
Date: 2026-06-12 | Repo: https://github.com/6ixtyn9-sudo/Edge-Factory.git | Branch: main
Owner vision: 10+ sources, DuckDB analytics, edge discovery/validation/decay forever.

This is the SINGLE source of truth for handover. Do NOT create BUILD_REPORT.md / CLEANUP_REPORT.md / SANITY_CHECK_REPORT.md etc. – update THIS file in place.

1. Architecture (CSV / DuckDB first)

```
sources (12 adapters, fetch_day -> list[dict])
   ↓  scripts/local_backfill.py  /  scripts/capture_daily.py
localdata/*_YYYY-MM.csv.gz
   ↓  scripts/build_warehouse.py
localdata/warehouse.duckdb   ← DuckDB views: forebet_settled, zulubet_settled, statarea_settled, predictz_settled, scoutingstats_settled, bettingclosed_settled, vitibet_settled, + raw: betclan, bzzoiro, freesupertips, afootballreport, windrawwin, consensus2, consensus3
   ↓  scripts/mine_consensus.py
localdata/edges_consensus.json
   ↓  scripts/picks_today.py
certified picks → stdout
```

Supabase schema exists in supabase/migrations/ (0001-0005) – currently used for edge registry / pick ledger design only. Live ingest is CSV/DuckDB. Do NOT re-introduce models.py / db.py / pipelines/ingest.py – that OO Supabase pipeline was deleted 2026-06-12 as stale/bloat (did not match the 12 simple module sources).

Golden rules:
* Wilson lower bound, never raw hit rate, for certification
* Walk-forward only. No mini-backtests.
* ROI alongside hit rate, always
* Edge decay monitoring: HEALTHY / WATCH / DECAYING / DEAD
* Best odds inflate ROI ~2x vs real book – caveat always

2. Sources — 12 adapters, all in src/edgefactory/sources/

| key | markets | odds | history | type |
| --- | --- | --- | --- | --- |
| forebet | 1x2, ou, btts, ht | ✅ best | ✅ 2024-01→now | backfillable |
| zulubet | 1x2 | ✅ | ✅ ~2023-12→now | backfillable |
| statarea | 1x2, ht_1x2, ou_1.5/2.5/3.5 | — | ✅ 2024+, archive to 2015 | backfillable |
| vitibet | 1x2 | — | ✅ archive to 2018, probs capture-forward | backfillable |
| scoutingstats | 1x2, btts, ou | ✅ | capture-forward | live |
| predictz | 1x2 pick+score | ✅ | capture-forward (archive ~2026-01+) | live, needs curl_cffi |
| windrawwin | 1x2 pick+stake | — | capture-forward only | live, needs curl_cffi |
| afootballreport | ou_1.5/2.5, btts | — | capture-forward, today only | live |
| betclan | 1x2 | — | capture-forward, today/tomorrow | live, needs curl_cffi |
| freesupertips | expert tips | ✅ | capture-forward | live |
| bettingclosed | 1x2, ou, btts | ✅ | ✅ archive | backfillable |
| bzzoiro | 1x2, ou, btts, xG | — | API, ~490 upcoming, ~7 weeks ahead | capture-forward, needs BZZOIRO_TOKEN env |

All adapters: fetch_day(date: str) -> list[dict], COLUMNS = [...]. No classes, no normalize(). Simple.

3. Key files

* src/edgefactory/assay.py – Wilson LB/UB, grade(wins,n), decay_verdict(), roi(), should_bench() – UNIT TESTED, 5/5 pass
* src/edgefactory/util.py – norm_team(), norm_team_sql()
* src/edgefactory/config.py – GATES: min_n_train=400, min_n_valid=120, min_roi_train=0.03, min_roi_valid=0.0, split="2025-06-01"
* src/edgefactory/warehouse.py – DuckDB connect(), views for all 12 sources
* scripts/local_backfill.py – CSV backfill, resumable, state_*.json – usage: python scripts/local_backfill.py <source> <start> <end> --max-seconds N
* scripts/capture_daily.py – daily cron: backfill recent window for all 12 sources, rebuild warehouse
* scripts/build_warehouse.py – materialize CSV → warehouse.duckdb
* scripts/mine_consensus.py – walk-forward consensus miner → edges_consensus.json
* scripts/picks_today.py – certified consensus picks (2-way ≥70%, 3-way ≥65%, veto on disagreement)
* tests/test_assay.py – 5 tests, must stay green

4. Certified findings (walk-forward, split 2025-06-01)

* 2-way unanimous avg≥70% → VALID 87% hit, LB 0.823, +4.9% ROI, n≈230 – PLATINUM
* 3-way unanimous avg≥65% → VALID 80% hit, LB 0.763, n≈340 – strong
* ANY disagreement → 33-40% hit – VETO RULE: never bet disagreed matches
* Draw picks never work (29-37%)
* Best odds inflate ROI ~2x
See localdata/edges_consensus.json after running mine_consensus.py

5. How to run

```bash
pip install -r requirements.txt   # pandas numpy duckdb curl_cffi pytest

# backfill a source
PYTHONPATH=src python scripts/local_backfill.py forebet 2024-01-01 2026-06-12 --max-seconds 1500

# daily capture (all 12)
python scripts/capture_daily.py

# build warehouse
python scripts/build_warehouse.py

# mine edges
python scripts/mine_consensus.py --split 2025-06-01

# today's picks
PYTHONPATH=src python scripts/picks_today.py
# or specific day
PYTHONPATH=src python scripts/picks_today.py 2026-06-13

# tests
PYTHONPATH=src python -m pytest tests/ -q   # 5 passed
```

6. Supabase

Migrations in supabase/migrations/:
* 0001_core.sql – sports, competitions, participants, events, results
* 0002_signals.sql – sources, raw_payloads, predictions, odds_snapshots, market_results
* 0003_edges.sql – edges, edge_picks, edge_audits, edge_scoreboard
* 0004_new_sources.sql – registers zulubet, statarea, scoutingstats, vitibet, afootballreport
* 0005_all_sources.sql – registers predictz, windrawwin, betclan, freesupertips, bettingclosed, bzzoiro

Supabase is NOT wired to live ingest yet (CSV/DuckDB is). Schema is ready for when we promote edges/picks to Postgres.
Set BZZOIRO_TOKEN in env / GitHub Actions secret for bzzoiro source.

7. Repo hygiene rules (enforced)
* ONE handover file: HANDOVER.md at repo root. Update in place. Never create BUILD_REPORT / CLEANUP_REPORT / SANITY_CHECK etc.
* No assumptions. Fact-check everything.
* Keep repo clean, delete stale files immediately.
* Assay math must never silently break – tests must stay green.
* localdata/* is gitignored – cache only.
* No OO Supabase pipeline files (models.py, db.py, pipelines/) – deleted 2026-06-12 as drift. If Supabase ingest is re-introduced, it must wrap the simple fetch_day() adapters, not replace them.

8. Next steps (priority)
* Decay monitor: nightly audit of certified edges → auto-bench if DEAD/DECAYING or ROI < -5%
* Backfill history: statarea 2017-2023, vitibet 2018+, bettingclosed archive – gives 7+ yr training data (runs IN PARALLEL, full ranges, not a prerequisite for anything)
* [DONE 2026-06-12] picks_today.py: expand beyond 3-source consensus – 1x2/OU2.5/BTTS, edges_consensus.json aware with fallback, bzzoiro ML confidence, vitibet index
* [DONE 2026-06-12] Extend mine_consensus.py: add vitibet, betclan, bzzoiro to consensus grids; add OU/BTTS markets
* Supabase sync: push certified edges + daily picks to edge_picks table (read-only emitter stays)
* Notifications: WhatsApp Business Cloud API (owner rejects Telegram) – swap in emit notifier
* More sources to 15+: oddsportal (CLV), betensured, foresportia
* ML layer: features = multi-source probs + disagreement spread + odds movement; model = just another source the miner validates

9. Known issues / caveats
* mine_consensus.py now dynamically verifies and scales all probabilities, and covers 1x2, OU2.5, and BTTS across forebet, zulubet, statarea, vitibet, betclan, scoutingstats, and bzzoiro gracefully.
* predictz / windrawwin / betclan need curl_cffi – installed via requirements.txt
* bzzoiro needs BZZOIRO_TOKEN env – adapter uses Authorization: Token <key>
* picks_today.py now supports 1x2/OU/BTTS, reads localdata/edges_consensus.json (certified edges only) with fallback to certified thresholds T2=70/T3=65 + veto when the registry is missing/empty. OU/BTTS run only with certified edges (no fallback). Fresh clone: localdata/ is empty BY DESIGN – run picks_today directly, fallback triggers; backfill is a separate parallel job, never a prerequisite. Live adapters vitibet/betclan return 0-100 probs – picks_today normalizes defensively (>1.5 → /100).
* No live odds movement tracking yet – odds_snapshots table exists in Supabase schema, not wired to CSV pipeline
* GitHub Actions: .github/workflows/daily-capture.yml runs capture_daily.py – needs BZZOIRO_TOKEN secret set

Last updated: 2026-06-12 – Extended mine_consensus.py to include OU/BTTS and new sources (vitibet, betclan, bzzoiro), with robust 0-1/0-100 scaling check. Repo cleanup: deleted stale OO Supabase pipeline, consolidated handover.

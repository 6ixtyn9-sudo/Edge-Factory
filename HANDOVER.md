🏭 EDGE FACTORY — HANDOVER
Date: 2026-06-16 | Repo: https://github.com/6ixtyn9-sudo/Edge-Factory.git | Branch: main
Owner vision: 10+ sources, DuckDB analytics, edge discovery/validation/decay forever.

This is the SINGLE source of truth for handover. Do NOT create BUILD_REPORT.md / CLEANUP_REPORT.md / SANITY_CHECK_REPORT.md etc. – update THIS file in place.

Architecture (CSV / DuckDB first)

text

sources (12 prediction adapters + 1 odds adapter, fetch_day -> list[dict])
   ↓  scripts/local_backfill.py  /  scripts/capture_daily.py
localdata/*_YYYY-MM.csv.gz
   ↓  scripts/build_warehouse.py
localdata/warehouse.duckdb   ← DuckDB views: forebet_settled, zulubet_settled, statarea_settled,
                                predictz_settled, scoutingstats_settled, bettingclosed_settled,
                                vitibet_settled, + raw: betclan, bzzoiro, freesupertips,
                                afootballreport, windrawwin, consensus2, consensus3, consensus4
   ↓  scripts/mine_consensus.py
localdata/edges_consensus.json
   ↓  scripts/picks_today.py
certified picks → stdout
Supabase schema exists in supabase/migrations/ (0001-0006). Live ingest is CSV/DuckDB, while certified edges and daily bucketed picks are synced to the Postgres read model (edge_picks table) via scripts/sync_supabase.py. Do NOT re-introduce models.py / db.py / pipelines/ingest.py – that OO Supabase pipeline was deleted 2026-06-12 as stale/bloat (did not match the simple module sources).

Golden rules:

Wilson lower bound, never raw hit rate, for certification
Walk-forward only. No mini-backtests.
ROI alongside hit rate, always
Edge decay monitoring: HEALTHY / WATCH / DECAYING / DEAD
Best odds inflate ROI ~2x vs real book – caveat always
Sources — 12 adapters, all in src/edgefactory/sources/

key	sport	markets	odds	history	type
forebet	soccer	1x2, ou, btts, ht	✅ best	✅ 2024-01→now	backfillable
zulubet	soccer	1x2	✅	✅ ~2023-12→now	backfillable
statarea	soccer	1x2, ht_1x2, ou_1.5/2.5/3.5	—	✅ 2024+, archive to 2015	backfillable
vitibet	soccer	1x2	—	✅ archive to 2018, probs capture-forward	backfillable
scoutingstats	soccer	1x2, btts, ou	✅	capture-forward	live
predictz	soccer	1x2 pick+score	✅	capture-forward (archive ~2026-01+)	live, needs curl_cffi
windrawwin	soccer	1x2 pick+stake	—	capture-forward only	live, needs curl_cffi
afootballreport	soccer	ou_1.5/2.5, btts	—	capture-forward, today only	live
betclan	soccer	1x2	—	capture-forward, today/tomorrow	live, needs curl_cffi
freesupertips	soccer	expert tips	✅	capture-forward	live
bettingclosed	soccer	1x2, ou, btts	✅	✅ archive	backfillable
bzzoiro	soccer	1x2, ou, btts, xG	—	API, ~490 upcoming, ~7 weeks ahead	capture-forward, needs BZZOIRO_TOKEN env
bzzoiro_odds	soccer	1x2, ou_2.5, btts	✅ real books + Polymarket	capture-forward (today/tomorrow) / backfillable	live, reuses BZZOIRO_TOKEN
All adapters: fetch_day(date: str) -> list[dict], COLUMNS = [...]. No classes, no normalize(). Simple.

Key files

src/edgefactory/assay.py – Wilson LB/UB, grade, decay_verdict, roi, should_bench + context_verdict_{league,team,odds_band} + weighted_consensus_score – UNIT TESTED (10/10)
src/edgefactory/market_registry.py – single source of truth for bettable markets and market/odds tier classification
src/edgefactory/util.py – norm_team(), norm_team_sql()
src/edgefactory/config.py – GATES: min_n_train=350, min_n_valid=120, split="2025-06-01"
src/edgefactory/warehouse.py – DuckDB connect(), views for all sources including consensus views (consensus2, consensus3, consensus4); all views carry sport='soccer'
src/edgefactory/sources/bzzoiro_odds.py – live real-book odds enrichment adapter supporting explicit market queries, deduplication, and odds team aliasing
scripts/local_backfill.py – CSV backfill, resumable – usage: python scripts/local_backfill.py <source> <start> <end> --max-seconds N
scripts/capture_daily.py – daily cron: backfill 30-day window (D30) for sources, rebuild warehouse; supports --skip-build
scripts/build_warehouse.py – materialize CSV → warehouse.duckdb
scripts/mine_consensus.py – walk-forward consensus miner → edges_consensus.json; edges carry sport='soccer'. Also contains recreate_views() equivalent logic for its own TEMP view graph.
scripts/decay_monitor.py – nightly decay audit (HEALTHY/WATCH/DECAYING/DEAD), auto-bench circuit breaker. Contains recreate_views() — must stay in sync with mine_consensus.py view graph.
scripts/assay_purity.py – context purity assay → localdata/purity_registry.json; CLI: --window N --dry-run. Contains recreate_views() — must stay in sync with mine_consensus.py view graph.
scripts/picks_today.py – purity-aware bucketed picks enriched with live real-book odds: CERTIFIED_CLEAN / CAUTION / WATCHLIST_NO_ODDS / WATCHLIST_UNKNOWN_CTX / SKIPPED_VETO / SKIPPED_DEAD_EDGE
scripts/backfill_results.py – safe retrospective settlement tool. Fills missing hs/gs results using forebet_settled. Does not affect edge certification.
scripts/backfill_bzzoiro_odds.py – multi-worker live odds backfill helper for bzzoiro_odds.
scripts/probe_bzzoiro_odds.py – diagnostic probe script for odds comparison event fallback testing.
scripts/sync_supabase.py – promotes daily bucketed picks and certified edges to Postgres (edge_picks).
scripts/clean_localdata.py – utility to cleanly purge localdata/ cache files.
scripts/daily.py – nightly pipeline: capture → build → mine → decay_monitor → assay_purity → picks_today → sync_supabase
tests/ – unit integration suite (test_assay.py, test_supabase.py), 10/10 pass, must stay green
Certified findings (walk-forward, split 2025-06-01)

As of 2026-06-16 nightly run — 7 active certified edges (2 benched by circuit breaker):

Rule	Valid n	Valid hit	Valid LB	Valid ROI	Status
2way-unanimous avg_p>=70	247	86.6%	0.818	+4.4%	WATCH
3way-unanimous avg_p>=65	401	82.0%	0.780	+0.9%	HEALTHY
2way-unanimous min_p>=60 avg_p>=65	477	80.1%	0.763	+0.3%	HEALTHY
3way-unanimous min_p>=60 avg_p>=65	236	83.0%	0.777	+1.7%	WATCH
2way-unanimous home-only avg_p>=65	442	80.8%	0.768	+1.3%	HEALTHY
3way-unanimous home-only avg_p>=60	607	78.2%	0.748	+0.2%	HEALTHY
3way-unanimous home-only avg_p>=65	315	81.3%	0.766	+0.2%	HEALTHY
3way-unanimous min_p>=60 avg_p>=60	261	82.0%	0.769	+1.0%	BENCHED (DECAYING)
2way+bc-confirms avg_p>=60	336	78.9%	0.742	+0.6%	BENCHED (DECAYING)
Operational picks_today thresholds (base canonical rules only):

2-way: 2way-unanimous avg_p>=70
3-way: 3way-unanimous avg_p>=65
Qualified rules (min_p, home-only, away-only, odds-, bc-confirms) are analysis variants — they inform the purity assay context classification, they do NOT govern picks_today thresholds. See _is_qualified() in picks_today.py.

Other known signal facts:

ANY disagreement → 33-40% hit – VETO RULE: never bet disagreed matches
Draw picks never work (29-37%)
Best odds inflate ROI ~2x
Away-only edges have negative ROI in validation — do not certify
OU 2.5 unanimous edges: all negative valid ROI across all thresholds — not certified
See localdata/edges_consensus.json after running mine_consensus.py

How to run

Bash

pip install -r requirements.txt   # pandas numpy duckdb curl_cffi pytest supabase

# one-time env setup: copy template, fill BZZOIRO_TOKEN. NOTHING auto-loads .env yet - export it:
cp .env.example .env
set -a; source .env; set +a

# backfill a source
PYTHONPATH=src python scripts/local_backfill.py forebet 2024-01-01 2026-06-12 --max-seconds 1500

# live odds backfill
PYTHONPATH=src python scripts/backfill_bzzoiro_odds.py --days 3 --workers 4

# daily capture (all sources, 30-day lookback)
python scripts/capture_daily.py

# build warehouse
python scripts/build_warehouse.py

# mine edges
python scripts/mine_consensus.py --split 2025-06-01

# today's picks (with real-book odds enrichment)
PYTHONPATH=src python scripts/picks_today.py
# or specific day
PYTHONPATH=src python scripts/picks_today.py 2026-06-13

# sync daily bucketed picks & certified edges to Supabase
PYTHONPATH=src python scripts/sync_supabase.py

# tests
PYTHONPATH=src python -m pytest tests/ -q   # 10 passed
Supabase

Migrations in supabase/migrations/:

0001_core.sql – sports, competitions, participants, events, results
0002_signals.sql – sources, raw_payloads, predictions, odds_snapshots, market_results
0003_edges.sql – edges, edge_picks, edge_audits, edge_scoreboard
0004_new_sources.sql – registers zulubet, statarea, scoutingstats, vitibet, afootballreport
0005_all_sources.sql – registers predictz, windrawwin, betclan, freesupertips, bettingclosed, bzzoiro
0006_edge_pick_context.sql – adds bucket, context, rule, match_name, picked_for, market_type, odds_tier, and source_payload columns to edge_picks for fully bucketed daily pick sync
Supabase Postgres read model is fully wired for daily picks (edge_picks) and certified edges (edges) via scripts/sync_supabase.py. Live ingestion of raw predictions and analytics remains streamlined in CSV/DuckDB.
Set BZZOIRO_TOKEN and SUPABASE_URL / SUPABASE_KEY in env (.env) / GitHub Actions secrets.

Repo hygiene rules (enforced)

ONE handover file: HANDOVER.md at repo root. Update in place. Never create BUILD_REPORT / CLEANUP_REPORT / SANITY_CHECK etc.
No assumptions. Fact-check everything.
Keep repo clean, delete stale files immediately.
Assay math must never silently break – tests must stay green.
localdata/* is gitignored – cache only.
No OO Supabase pipeline files (models.py, db.py, pipelines/) – deleted 2026-06-12 as drift. If Supabase ingest is re-introduced, it must wrap the simple fetch_day() adapters, not replace them.
ENGINEERING LESSONS — hard-won, mandatory reading for every new agent

These are bugs that actually happened. Do not repeat them.

L1 — The three-script view graph (Phase 13 / 13.2)

mine_consensus.py creates TEMP consensus views (v_consensus2, v_consensus3, consensus4, consensus2_bc, consensus2_bz, consensus2_bc_confirm, consensus_ou_dense, consensus_btts_sparse, etc.) inside its own DB connection. decay_monitor.py and assay_purity.py both contain a recreate_views() function that rebuilds those EXACT same TEMP views so they can query certified edges.

Rule: when you add a new miner view (new Lever, new source combination), you must add the identical view creation SQL to recreate_views() in BOTH decay_monitor.py AND assay_purity.py. Failure causes UNKNOWN (skipped) in decay audit and SKIP in purity assay for any edge whose view is missing. The bug is silent — the edge is not flagged as broken, it just never gets audited.

L2 — consensus2 does not expose hkey/akey (Phase 13.1)

The warehouse consensus2 view (and v_consensus2 derived from it) joins forebet_settled and zulubet_settled on (date, hkey, akey) internally, but its SELECT only outputs date, home, away, outcome, fb_pick, zb_pick, fb_p, zb_p, avg_p, pick_odds, league. The join keys hkey and akey are NOT in the output columns.

Rule: any TEMP view that joins against consensus2 / v_consensus2 / consensus3 must join on (date, home, away), not (date, hkey, akey). Using DISTINCT ON (date, hkey, akey) or JOIN ... USING (date, hkey, akey) against these views will crash with BinderError: Referenced column "hkey" not found. The settled source views (forebet_settled, zulubet_settled, etc.) DO expose hkey/akey — it is only the pre-joined consensus views that do not.

L3 — Qualified rules must not govern picks_today thresholds (Phase 13.1)

mine_consensus.py produces both base rules (2way-unanimous avg_p>=70) and qualified analysis variants (2way-unanimous min_p>=60 avg_p>=65, 2way-unanimous home-only avg_p>=65, etc.). When multiple rules of the same n_way certify, picks_today.load_thresholds() keeps one per n_way. If _prefer_entry selects a qualified variant (lower threshold wins by the old logic), picks_today applies a lower threshold with none of the qualifier's filter logic, quietly certifying more matches than the data supports.

Rule: qualified rules (containing min_p, home-only, away-only, odds-, bc-confirms) are analysis findings for the purity assay — they must NOT displace the base canonical rule in picks_today. _is_qualified() in picks_today.py enforces this. Unqualified rules unconditionally beat qualified ones in _prefer_entry, regardless of threshold.

L4 — Stub comments in payload files (Phase 12.1)

A comment written as an editing instruction (# ... (keep all existing source lists...)) was left in the actual file and committed. This violates the handover protocol: payload files must be complete, runnable code. No editorial stubs, no ellipses, no placeholder text ever.

Rule: every payload file is a complete, byte-exact, working Python file. Write it in full. If you find ... or # keep existing in a payload, that is a bug — stop and fix it before committing.

L5 — Module-level globals set inside main() (Phase 12.1)

scales_global was declared as a module-level name and assigned inside main(). Any function that referenced it before main() ran would crash with NameError. Module-level mutable state is fragile, especially in functions called from other scripts.

Rule: pass shared state as explicit function parameters. No module-level globals that depend on runtime initialisation.

L6 — The decay circuit breaker is correct, not a bug (general)

When decay_monitor.py reports DECAYING → BENCHED, this is the system working as designed. The edge's recent window performance has degraded below the certified baseline. Benched edges are excluded from picks_today immediately (it only reads status=="certified"). The next mine_consensus.py run re-evaluates the edge on full data — it will re-certify if the full-history walk-forward still clears all gates, or remain candidate/absent if it does not. Do NOT manually un-bench edges in the JSON file.

L7 — Executor must copy payloads, never rewrite them (Phase 12 executor drift)

The executor re-implemented test_assay.py from scratch instead of copying the payload, dropping test_weighted_consensus_score. The HANDOVER says 10/10 tests but the repo had 9. Always copy; never reconstruct.

Rule: executor installs payloads with cp only. The SHA-256 gate catches any deviation. A failed gate means stop — not fix-and-continue.

Phase history

[DONE 2026-06-15] Phase 1: sport='soccer' added to all 12 warehouse views, pick dicts, and edge records in mine_consensus.py (commit 67c5180)

[DONE 2026-06-15] Phase 2: context_verdict_{league,team,odds_band} added to assay.py; tests/test_assay.py → 6/6 (commit 0f17793)

[DONE 2026-06-15] Phase 3: scripts/assay_purity.py – reads edges_consensus.json + warehouse.duckdb, computes BOOST/ALLOW/CAUTION/VETO/UNKNOWN per league/team/odds_band context, writes localdata/purity_registry.json; wired into daily.py between decay_monitor and picks_today (commit ba8df06)

[DONE 2026-06-15] Phase 4: picks_today.py bucketing overhaul – purity_registry-aware, six output buckets, bucket+ctx+home+away in picks_today.json (commit 984507e)

[DONE 2026-06-15] Phase 4.1 (housekeeping): Added fb.league to consensus2/consensus3 SELECTs in warehouse.py; fixed deprecated datetime.utcnow() → datetime.now(datetime.timezone.utc) in assay_purity.py

[DONE 2026-06-15] Phase 5: bzzoiro_odds adapter – reuses BZZOIRO_TOKEN + BSD API (14+ books + Polymarket). Live-odds enrichment in picks_today.py.

[DONE 2026-06-15] Phase 6: Added bzzoiro_odds to sources, consensus4 league column, patched datetime.UTC.

[DONE 2026-06-15] Phase 7 + 7.1: market_registry.py, tiered purity thresholds, market/odds tier bucketing, backfill_results.py.

[DONE 2026-06-15] Phase 8: Relaxed purity thresholds (League: 50, Team: 30, Odds: 80).

[DONE 2026-06-15] Phase 9: Warehouse consensus4 view promotion; 30-day capture lookback (D30).

[DONE 2026-06-15] Phase 10: Robustified bzzoiro_odds adapter (V1 fallbacks, dedup, team aliasing, probe/backfill helpers).

[DONE 2026-06-15] Phase 11: Supabase sync — 0006_edge_pick_context.sql + sync_supabase.py fully wired.

[DONE 2026-06-16] Phase 12: Weighted Consensus — Wilson LB vote weighting per source/market.

assay.py: added weighted_consensus_score(votes, min_lb) → (winning_pick, w_score, is_unanimous).
mine_consensus.py: _source_wilson_lbs() + _run_weighted_consensus() — mines weighted-1x2 rules at w_score thresholds [0.55…0.80]; certified edges carry source_weights + weighted=True.
picks_today.py: load_source_weights(), w_score per pick, sort by (-w_score, -avg_p).
tests/test_assay.py: test_weighted_consensus_score — 8 assertions. Tests: 10/10.
[DONE 2026-06-16] Phase 12.1: Bug fixes — stub comment in payload (L4), duplicate import re (L5 variant), scales_global module global replaced with parameter (L5), unused groupby import, tautological WHERE hs IS NOT DISTINCT FROM hs → WHERE outcome IS NOT NULL.

[DONE 2026-06-16] Phase 13: 5 Accuracy Levers — additive walk-forward scans in mine_consensus.py.

Lever 1 — No-draw gate (3way): 3way-unanimous no-draw avg_p>=X
Lever 2 — Per-source floor: 2way/3way-unanimous min_p>=60 avg_p>=X (blocks dragged-into-agreement votes)
Lever 3 — Odds-band targeted: 2way/3way-unanimous odds-1.20-1.75 avg_p>=X
Lever 4 — Home/away split: 2way/3way-unanimous home-only/away-only avg_p>=X
Lever 5 — Bettingclosed confirm: 2way+bc-confirms avg_p>=X (559k settled rows as 3rd-source check)
[DONE 2026-06-16] Phase 13.1: Bug fixes — Lever 5 BinderError (hkey not in consensus2 SELECT, fixed to join on date, home, away) (L2); qualified rules displacing base canonical rule in picks_today (added _is_qualified(), L3).

[DONE 2026-06-16] Phase 13.2: Added consensus2_bc_confirm to recreate_views() in both decay_monitor.py and assay_purity.py — fixes UNKNOWN/SKIP on the bc-confirms edge (L1).

[DONE 2026-06-16] Phase 13.3 (this update): HANDOVER updated with full engineering lessons section, corrected certified findings table, corrected test count (10/10), and all stale content removed.

Next steps (open priorities)

Notifications: WhatsApp Business Cloud API (owner rejects Telegram) – swap in emit notifier
More sources to 15+: oddsportal (CLV), betensured, foresportia
ML layer: features = multi-source probs + disagreement spread + odds movement; model = just another source the miner validates
Live odds movement tracking: wire odds_snapshots table into the CSV/DuckDB live pipeline
Purity context maturation: league/team/odds_band contexts are 99%+ UNKNOWN currently — self-populates as settled data accumulates. No code needed, only time.
Known issues / caveats

mine_consensus.py covers 1x2, OU2.5, and BTTS across forebet, zulubet, statarea, vitibet, betclan, scoutingstats, bzzoiro gracefully.
predictz / windrawwin / betclan need curl_cffi – installed via requirements.txt
bzzoiro needs BZZOIRO_TOKEN env – adapter uses Authorization: Token <key>
.env is NOT auto-loaded – export manually (set -a; source .env; set +a) or via CI secrets.
picks_today.py: fresh clone (empty localdata/) → purity missing → all ctx=UNKNOWN → WATCHLIST. Edge registry missing → fallback thresholds T2=70/T3=65. Both are correct, never a crash.
No live odds movement tracking yet – odds_snapshots table in Supabase schema, not wired to CSV pipeline.
GitHub Actions: .github/workflows/daily-capture.yml runs capture_daily.py – needs BZZOIRO_TOKEN, SUPABASE_URL, and SUPABASE_KEY secrets set.
Source Wilson LBs for 1x2 are below 0.50 in training period (forebet 0.467, zulubet 0.496, statarea 0.507) — weighted consensus min_lb=0.50 floor excludes them, so no weighted rules certify yet. This is correct: individual source 1x2 accuracy pre-consensus is lower than consensus accuracy. Will improve as capture-forward sources mature.
consensus4 only has 363 rows — vitibet has 5,566 settled rows vs forebet's 648k. 4-way join is thin. Data maturity constraint, not a code problem.
Away-only edges: 3way-unanimous away-only avg_p>=60 has valid ROI -6.0% — NEVER certify away-only edges on current data.
OPERATIONAL STANDARD — anti-drift handover protocol (MANDATORY for every repo change)

Lesson learned 2026-06-12, the hard way: LLM executors corrupt byte-sensitive payloads routed through chat. Attempt 1: markdown mangled raw Python (indentation stripped, comments eaten). Attempt 2: a 13KB base64 blob was regenerated from context and hallucinated mid-stream. Both caught ONLY by SHA-256 gates. File-based handoff fixed it. This protocol is now LAW for every commit:

ROLES: BUILDER (planning agent: writes + tests the change in a sandbox against current GitHub HEAD, produces the handoff bundle) → EXECUTOR (has push credentials: copies files, verifies hashes, commits, pushes) → VERIFIER (independently re-clones GitHub and re-checks everything).

THE BUNDLE: payload files (full file contents, never diffs-in-prose) + SHA256SUMS + commit_msg.txt + an executor prompt. Payloads travel as FILES (download/disk), NEVER as chat text — no heredocs, no base64-in-prompt, no "retype this code".

EXECUTOR RULES:

Gate 0 FIRST: verify every payload hash BEFORE touching the repo. Mismatch → STOP.
Required base commit pinned in the prompt; if origin/main differs → STOP, never merge/guess.
Install by cp only. Never open payloads in an editor, never retype, never reconstruct from logs/transcripts/memory, never "repair" — a hash mismatch means corrupted transfer, not a fixable problem.
Post-install gates: per-file SHA-256, pytest green, py_compile, localdata/ empty, git status --porcelain matching the EXACT expected line set — nothing extra.
One ordinary commit on main, parent = pinned base. No rebase/squash/force-push. Commit message from file (git commit -F).
ANY gate fails → STOP, report verbatim, change nothing.
Helper files (payloads, *.b64, runner scripts) never enter the repo tree.
PROOF BUNDLE (raw, unedited): git ls-remote of GitHub main + rev-parse HEAD/HEAD^ + show --stat + file hashes + pytest output + runtime smoke output. Claims without matching on-GitHub state = task failed.
VERIFIER: fresh clone from GitHub; re-check remote SHA, parent commit, byte-identity of changed files vs the canonical build, diff scope, tests, runtime. On-GitHub state is the ONLY source of truth — executor reports are hypotheses until the clone confirms them.

DATA JOBS (backfill/capture) are the ONE exception to the bundle — only because localdata/ is gitignored and they push nothing. They must still end with git status --porcelain EMPTY (helpers deleted) and a verifiable completion report (row counts, state files, miner output).

Run order (nightly): capture_daily → build_warehouse → mine_consensus → decay_monitor → assay_purity → picks_today → sync_supabase. decay_monitor needs warehouse + registry; with neither it reports and exits 0 (safe on fresh clone).

Last updated: 2026-06-16

<!-- EDGE_FACTORY_PHASE_A_SOURCE_CONFIRMATION_2026_06_16 -->

[DONE 2026-06-16] Phase A: Unused soccer source confirmation levers

Scope: additive miner scans only; base certified rules and operational thresholds remain unchanged.

Implemented:

- `scripts/mine_consensus.py`
  - Adds `create_phase_a_confirmation_views()` and `run_phase_a_confirmation_levers()`.
  - Mines `2way+predictz-confirms avg_p>=X` for X in 60/65/70/75.
  - Mines `3way+predictz-confirms avg_p>=X` for X in 60/65/70.
  - Mines `2way+windrawwin-confirms avg_p>=X` for X in 60/65/70/75.
  - Mines `3way+windrawwin-confirms avg_p>=X` for X in 60/65/70.
  - These are walk-forward candidates/certifications using the same Wilson/ROI gates.
  - They are confirmation levers only and must not displace canonical picks_today thresholds.

- `scripts/decay_monitor.py` and `scripts/assay_purity.py`
  - Recreate the same Phase A TEMP views (`consensus2_predictz_confirm`, `consensus3_predictz_confirm`, `consensus2_windrawwin_confirm`, `consensus3_windrawwin_confirm`) so any certified Phase A edge can be audited and assayed. This preserves L1.

- `scripts/picks_today.py`
  - Marks `predictz-confirms`, `windrawwin-confirms`, and `freesupertips-confirms` as qualified analysis rules so they cannot replace base operational thresholds.

Not done intentionally:

- `freesupertips` confirmation is not mined yet because current local volume is tiny and tip text needs a safer 1x2 mapping layer.
- `afootballreport` confirmation is not mined yet because it is OU/BTTS-specific and OU/BTTS edges remain unprofitable/not certified.

Future plans:

1. Phase B — odds movement / CLV
   - Persist periodic real-book odds snapshots in CSV/DuckDB.
   - Track pick-time odds, closing odds, movement direction, and CLV.
   - Add CLV as an audit dimension before using it as a miner feature.

2. Phase C — tournament and league classification
   - Use `entity_registry.json` plus rules to tag domestic league, cup, friendly, international, youth/reserve/women.
   - Mine/veto these categories separately; friendlies/cups should not silently mix with league fixtures.

3. Phase D — price-sensitive operational rules
   - Promote odds-band verdicts to explicit rule constraints.
   - Keep mature odds-band VETO as hard skip; treat sparse league/team contexts as caution only.

4. Phase E — ML as a validated source
   - Features: multi-source probabilities, agreement count, min_p, avg_p, spread, odds tier, odds movement, source confirmations, entity/tournament tags.
   - The model must be exported as another source and validated by the same miner/decay process. No bypass.

5. New sports
   - Do not add another sport yet. Soccer still has unused source levers, odds movement, tournament classification, and ML-source validation to exploit first.
   - Revisit new sports after CLV and confirmation levers have been monitored for at least one month.


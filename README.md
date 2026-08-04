EDGE FACTORY
Scrape → Assay → Discover → Validate → Monitor decay → Emit picks → Push to phone.
CSV + DuckDB-first. Supabase as read model. Wilson LB only. Walk-forward only.

Born from Ma Golide – industrialized.

Quickstart

Bash

pip install -r requirements.txt
cp .env.example .env          # fill in real values; .env is gitignored, NEVER commit
PYTHONPATH=src python -m pytest tests/ -q

# Backfill a source
python scripts/local_backfill.py forebet 2024-01-01 2026-06-12 --max-seconds 1500

# Daily capture (all sources)
python scripts/capture_daily.py

# Build warehouse
python scripts/build_warehouse.py

# Mine consensus edges
python scripts/mine_consensus.py --split 2025-06-01

# Today's picks
PYTHONPATH=src python3 scripts/picks_today.py

# Full daily run (capture → warehouse → mine → picks → CLV → sync → WhatsApp)
PYTHONPATH=src python3 scripts/daily.py

# Force a full repick  
PYTHONPATH=src python3 scripts/daily.py --force-repick

A local .env IS auto-loaded. config.py, db.py, and notify_whatsapp.py all call load_dotenv() at import, so set -a; source .env; set +a is no longer required (it stays harmless).

Autonomous 3-Hour Service

Bash

# Local background loop (every 3h)
PYTHONPATH=src python3 scripts/daily.py --auto-run

# One smart iteration and exit (used by GitHub Actions)
PYTHONPATH=src python3 scripts/daily.py --auto-once
Smart schedule:

If today's official frozen archive (localdata/picks_YYYY-MM-DD.json) does not exist → full heavy morning run (build DuckDB, lock picks, sync, push).
If it already exists → lightweight intraday late-slate scan: append only brand-new certified bets, keep morning picks pristine, capture time-of-day CLV snapshots, and push late-slate alerts only when new picks appear.
100% free on GitHub Actions — enabled by default in .github/workflows/daily.yml:

Wakes every 3h (00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 UTC)
actions/cache persists the localdata/ DuckDB warehouse, pick ledgers, CLV snapshots, and the WhatsApp sent ledger across runs
Uploads pick reports (.txt) and ledgers as downloadable artifacts
Runs sync_supabase then notify_whatsapp as the final steps
Git workflow (collision-safe)

localdata/ is owned by the GitHub Actions persist loop. It is the ONLY writer allowed to commit those files. Local pipeline runs rewrite localdata constantly; leaving those files dirty/uncommitted in your working tree is expected and correct. Humans and agents commit code + docs only, with explicit paths. NEVER git add -A, git add ., or VS Code "Commit All" — sweeping pipeline state into a manual commit collides with the bot's persist commits and produces the "divergent branches / Need to specify how to reconcile" fatal. This has happened three times (latest: 2026-08-03, merge 65d062c).

Bash

# one-time setup per machine — paste as-is:

git checkout -- localdata/ && git pull --no-rebase

# commit workflow — edit ONLY the FILES line to name your change's files, then paste the whole block as-is:
FILES=("scripts/picks_today.py" "scripts/audit_recent_picks.py" "HANDOVER.md")
git status --porcelain
git restore --staged localdata/ 2>/dev/null
git add "${FILES[@]}"
git commit -m "change: what and why"
git pull --no-rebase
git push origin main

# push rejected / "divergent branches" (bot persisted while you worked) — paste as-is:

git pull --no-rebase -X ours
git push origin main

Never git reset --hard origin/main or discard local commits to "fix" divergence — that is how payload code gets orphaned. Merge, don't erase.
Every repo change is appended to HANDOVER.md with date + rationale (anti-drift protocol).
Sources (12)

source	markets	odds	history
forebet	1x2, ou, btts, ht	✅	2024-01+, high-volume
zulubet	1x2	✅	2023-12+
statarea	1x2, ou_1.5/2.5/3.5	—	2015+ (2024+ scraped)
vitibet	1x2	—	2018+ (thin in c4)
scoutingstats	1x2, btts, ou	✅	capture-forward
predictz	1x2 pick	✅	capture-forward (shadow)
windrawwin	1x2 pick	—	capture-forward (shadow)
afootballreport	ou, btts	—	capture-forward
betclan	1x2	—	capture-forward
freesupertips	expert tips	✅	capture-forward (not ready)
bettingclosed	1x2, ou, btts	✅	archive
bzzoiro	1x2, ou, btts, xG	—	API, ~7 weeks ahead, needs BZZOIRO_TOKEN
Odds / market-data adapters:

bzzoiro_odds — operational primary live odds enrichment for picks_today
scoutingstats embedded odds — operational secondary fallback
BetExplorer — research only, not production
All adapters: fetch_day(date) -> list[dict], COLUMNS = [...], no classes, no normalize() methods.

Status notes:

Core certified levers: forebet, zulubet, statarea, bettingclosed
vitibet active but thin; scoutingstats, betclan partial
predictz, windrawwin are shadow-only (Phase A): n=0 train under the current split. Do not certify yet.
BetExplorer investigated and concluded negative for alpha — kept research-only.
Layout

text

src/edgefactory/
  assay.py             # Wilson LB/UB, grade, decay_verdict, roi – TESTED
  config.py            # GATES (min_n_train=350, split=2025-06-01); load_dotenv()
  util.py              # norm_team / norm_team_sql – miner-critical join keys, do not drift
  entities.py          # canonical_league / canonical_team – context & reporting only
  market_registry.py   # market + odds-tier classification
  clv.py               # pure CLV helpers, pick ids, implied prob, movement summaries
  db.py                # Supabase client (SUPABASE_URL + SUPABASE_SERVICE_KEY); load_dotenv()
  whatsapp.py          # WhatsApp providers: Meta Cloud, Twilio, CallMeBot
  warehouse.py         # DuckDB views for all sources, sport='soccer'
  sources/             # prediction + odds adapters

scripts/
  capture_daily.py        # D30 capture, all sources; --skip-build
  local_backfill.py       # CSV backfill, resumable; writes *_YYYY-MM.csv.gz
  backfill_results.py     # D30 result repair; idempotent
  build_warehouse.py      # CSV → warehouse.duckdb
  build_entity_registry.py# learns aliases → entity_registry.json
  mine_consensus.py       # walk-forward miner; Phase A shadow scans
  decay_monitor.py        # 60-day health audit, auto-bench circuit breaker
  assay_purity.py         # context purity registry (--window 36500)
  picks_today.py          # certified picks engine, purity-aware buckets
  audit_clv.py            # CLV capture + report (audit-only in v1)
  audit_recent_picks.py   # scores archived picks vs settled results
  export_settled_results.py # settled-score facts overlay shared across machines (Addendum 21)
  daily.py                # SINGLE orchestrator: --auto-run / --auto-once / --forecast-refresh / --promote-forecast / --clv-only
  sync_supabase.py        # promotes edges + picks to Supabase read model
  notify_whatsapp.py      # WhatsApp push dispatch (CERTIFIED_CLEAN + CAUTION only)

tests/                    # assay, picks_today_operational, daily_orchestration
config/entity_overrides.json  # manual safety layer for aliases
supabase/migrations/      # 0001-0006
HANDOVER.md               # single source of truth – update in place
Environment

cp .env.example .env and fill in. Required variables (verified against the code):

variable	used by	notes
BZZOIRO_TOKEN	bzzoiro odds/model adapter	needed for live odds enrichment
SUPABASE_URL	db.py	project URL
SUPABASE_SERVICE_KEY	db.py	service_role key, server-side only. (Not SUPABASE_KEY — that is unused.)
CALLMEBOT_APIKEY	notify_whatsapp.py	returned by CallMeBot after authorization
CALLMEBOT_PHONE	notify_whatsapp.py	full intl number, no + / spaces (e.g. 27821234567)
WhatsApp push (Meta Cloud / Twilio) is optional:

Meta: WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_RECIPIENT (+ optional WHATSAPP_TEMPLATE_NAME)
Twilio: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER (+ WHATSAPP_RECIPIENT)
For GitHub Actions, secrets (not .env) are the source of truth. Verify under Settings → Secrets and variables → Actions: SUPABASE_URL, SUPABASE_SERVICE_KEY, BZZOIRO_TOKEN, CALLMEBOT_APIKEY, CALLMEBOT_PHONE.

WhatsApp setup (CallMeBot, free path):

From your own WhatsApp, add the CallMeBot number and send exactly:
I allow callmebot to send me messages
You'll receive API Activated for your phone number. Your APIKEY is ...
Use that key as CALLMEBOT_APIKEY.
⚠️ Open fix (2026-06-18): send_callmebot_whatsapp() in src/edgefactory/whatsapp.py uses the endpoint whatsapp.py; it must be whatsapp.php. Until fixed, every dispatch 404s, is swallowed by run_soft, and the job still finishes green with no message. See HANDOVER.md §9.

Only CERTIFIED_CLEAN and CAUTION buckets are pushed **as bets** (main slate). Dedup ledger localdata/whatsapp_sent_ledger_YYYY-MM-DD.json means ~one morning message/day plus late-slate alerts only when new fixtures appear.

Shadow slate (Addendum 24, default ON — kill with EDGE_FACTORY_NOTIFY_SHADOW=0): a SECOND daily message carries the streams the old doctrine kept off the phone — SKIPPED_VETO + WATCHLIST_NO_ODDS + WATCHLIST_UNKNOWN_CTX — each section labeled with that stream's rolling 30d audit record (from localdata/picks_audit_rolling.json). Independent dedup ledger localdata/whatsapp_shadow_sent_ledger_YYYY-MM-DD.json: main and shadow sends never suppress each other. Shown for transparency, not pushed as bets; weight the streams by their records.

Golden rules

Wilson lower bound, never raw hit rate
Walk-forward only, no mini-backtests
ROI alongside hit rate, always
Edge decay: HEALTHY / WATCH / DECAYING / DEAD – auto-bench (DECAYING → BENCHED is the system working; do not manually unbench)
Best odds inflate ROI ~2x – caveat always
Away-only edges: negative ROI in validation – do not certify
OU 2.5 unanimous edges: negative ROI across thresholds – not certified
Do not change norm_team() / norm_team_sql() join keys without full revalidation
New sources must be mined standalone before being added as levers
Repo clean – stale files deleted immediately. ONE handover file: HANDOVER.md
Every repo change ships via the anti-drift protocol (payloads + SHA-256 + pinned base commit + independent verification). No code travels through chat.
A green Actions run does NOT prove WhatsApps were delivered or Supabase was written – run_soft swallows non-critical failures. Confirm from the phone / logs.
Certified edges (split 2025-06-01)

Operational thresholds (base canonical only):

2-way unanimous avg_p>=70
3-way unanimous avg_p>=65
Qualified rules (min_p, home-only, odds-, *-confirms, …) are analysis/purity variants and must not displace base thresholds.

Latest stable accounting:

consensus2 ≈ 27,450 · consensus3 ≈ 15,807 · consensus4 ≈ 383
certified audited: 9 · benched by decay: 1 · active certified: 8
Disagreement → historically poor hit rate → VETO, never bet.
See HANDOVER.md for full edge-level detail, buckets, and the purity logic.

Supabase

Migrations supabase/migrations/ (0001–0006) register all sources and the edge/pick schema.
sync_supabase.py promotes certified edges → edges and bucketed daily picks → edge_picks.
Live ingest is CSV/DuckDB first; Supabase is the read model for dashboards/apps.
CLV & audits

audit_clv.py captures pick_time and end_of_run snapshots from daily.py automatically. Report stays audit-only in v1; CLV/steam/drift never gate picks.
audit_recent_picks.py scores archived 1x2 picks against settled warehouse results.
decay_monitor.py runs the 60-day health audit and auto-benches decayed edges.
Status

Stable daily pipeline since 2026-06-17 (day 0/1 of the current machine-auditable regime).
2026-06-18 determinism fix: one run-level EDGE_FACTORY_RUN_AS_OF, pre-match guard (default 30 min lead), archive-first same-date reruns, post-bucket duplicate collapse.
BetExplorer investigation concluded negative — research-only.
WhatsApp push wired in; pending the whatsapp.php endpoint fix and CallMeBot authorization.
Updated – 2026-06-18
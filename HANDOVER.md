Edge Factory — Handover

Date: 2026-06-18

2026-06-27 addendum — short-odds sniper narrowing, purity rewrite, and monitoring plan

Current strategic thesis

The system is no longer treated as a broad betting engine. The surviving operational thesis is now:

focus on 1X2 only
focus on home favorites
focus on short odds under 1.25
prefer strong consensus / conviction
aggressively veto medium-odds, away-favorite, and sparse-toxic contexts
In practice, the current live posture is a defensive short-odds home sniper with strict veto rules.

Key code changes now in repo

scripts/picks_today.py

Default run scope changed to today only.
Previous default: today + tomorrow
Current default: today only
Tomorrow must now be explicitly requested via CLI date argument.
Phase-1 market expression warning layer exists.
Additional short-odds sniper safeguards now exist:
raw 1x2 picks at >= 1.25 are skipped
short-odds away favorites are skipped
ultra-short home picks (< 1.20) with sparse niche context may surface as CAUTION instead of WATCHLIST_UNKNOWN_CTX, but only when no explicit veto exists and supportive context gates pass
scripts/assay_purity.py

Purity registry now includes a new niche context dimension.
New niche key shape:
sport|league|market|rule|odds_band|side_role
This was added to fix the earlier dimension bleed problem where league context was too broad.
src/edgefactory/assay.py

Added context_verdict_niche(...)
This is a niche-sensitive verdict function intended for sparse but high-impact contexts, especially short-odds home-favorite niches.
It does not replace the generic context verdict functions; it exists in parallel.
Current operational behavior

Expected current behavior when running python3 scripts/picks_today.py:

today only, unless dates are explicitly passed
ultra-short home 1X2 picks may appear as CAUTION
away short favorites should be vetoed
raw 1X2 picks at >= 1.25 should be vetoed
explicit niche/odds/context vetoes remain hard stops
Current limitations

Broad league purity context is still mostly sparse / UNKNOWN
niche context is working, but still dominated by UNKNOWN verdicts in many leagues
There is not yet enough stable evidence to auto-build robust trusted/toxic short-odds league lists from the current registry alone
Do not over-tune league lists yet from thin samples
7-day monitoring plan

For the next week, stop changing logic unless something is obviously broken. Monitor behavior.

Daily commands

Rebuild purity:
python3 scripts/assay_purity.py

Generate today-only picks:
python3 scripts/picks_today.py

Record daily summary

Capture the final summary line from picks_today.py, especially:

CLEAN
CAUTION
WATCHLIST_odds
WATCHLIST_ctx
SKIPPED_veto
SKIPPED_dead
Record every CAUTION pick

For each caution pick, track:

date
match
league
rule
odds
home/away
final result once settled
Healthy signs

most medium-odds / away-favorite / fragile picks remain vetoed
only a small number of short-home picks surface as CAUTION
no obvious garbage leaks through
same weak contexts do not repeatedly pass as playable candidates
Warning signs

zero usable picks every day
too many plausible ultra-short home picks still trapped by sparse UNKNOWN
repeated bad CAUTION picks from the same leagues
obvious bad picks still leaking through veto logic
Next likely refinement after monitoring

Only after several days of observation:

review recurring CAUTION picks
review recurring vetoed leagues / contexts
decide whether to:
further soften UNKNOWN handling for ultra-short home picks, or
introduce a more data-backed toxic short-odds league overlay
Until that evidence exists, keep the current defensive posture.

Repo: https://github.com/6ixtyn9-sudo/Edge-Factory.git

Branch: main

Single source of truth

This file is the single source of truth for handover.

Do not create BUILD_REPORT.md, CLEANUP_REPORT.md, SANITY_CHECK.md, or similar side files.

Update this file in place.

Executive summary

Edge Factory is a CSV + DuckDB-first soccer edge-mining pipeline.

Live analytics engine: CSV + DuckDB

Supabase role: read model for certified edges and daily picks

WhatsApp role: push delivery of CERTIFIED_CLEAN and CAUTION picks to the owner's phone

Owner vision: 10+ sources, DuckDB analytics, edge discovery, validation, and decay forever

Stable current state:

Daily pipeline is stable.

Consensus counts are back to expected levels.

Certified edge accounting is restored.

BetExplorer research is concluded and should not be promoted into production.

PredictZ and Windrawwin remain shadow-only.

A small CLV audit spike is now wired into scripts/daily.py.

Current CLV is audit-only and not used for certification or pick gating.

WhatsApp push delivery is now wired into daily.py via scripts/notify_whatsapp.py and src/edgefactory/whatsapp.py. Operational status and a required one-line fix are documented in section 9.

Trusted current operational baseline starts on 2026-06-17.

Treat 2026-06-17 as day 0/1 of the current machine-auditable regime.

Best next focus is maintaining the pipeline, monitoring certified edges, and improving CLV coverage using existing real-book odds.

Expected healthy accounting:

consensus2: about 27,450

consensus3: about 15,807

consensus4: about 383

certified audited: 9

benched by decay: 1

active certified: 8

Current stable architecture

Core principle:

Edge Factory is CSV / DuckDB first.

Supabase is a read model, not the live analytics engine.

Pipeline flow:

Prediction adapters and odds / market-data adapters

fetch_day(date: str) -> list[dict]

COLUMNS = [...]

no classes

no normalize() methods

Capture

scripts/capture_daily.py

scripts/local_backfill.py

writes localdata/*_YYYY-MM.csv.gz

Result repair

scripts/backfill_results.py

fills missing hs / gs from donor result sources

Warehouse build

scripts/build_warehouse.py

writes localdata/warehouse.duckdb

Entity registry

scripts/build_entity_registry.py

writes localdata/entity_registry.json

Consensus mining

scripts/mine_consensus.py

writes localdata/edges_consensus.json

Decay audit

scripts/decay_monitor.py

60-day health audit and auto-bench circuit breaker

Purity assay

scripts/assay_purity.py

writes localdata/purity_registry.json

Picks

scripts/picks_today.py

writes stdout and localdata/picks_today.json

daily.py also archives final target-day picks to localdata/picks_YYYY-MM-DD.json

CLV audit

scripts/audit_clv.py

writes localdata/clv_snapshots_YYYY-MM.csv.gz

writes localdata/clv_report_rolling.json

writes localdata/clv_report_YYYY-MM-DD.md

captures pick-time and end-of-run snapshots from daily.py

Recent picks audit

scripts/audit_recent_picks.py

writes localdata/picks_audit_rolling.json

writes localdata/picks_audit_YYYY-MM-DD.md

scores archived daily picks against settled warehouse results

Future planning

inline inside scripts/daily.py

writes localdata/picks_YYYY-MM-DD.txt

writes localdata/picks_next_2days.json

Read-model sync

scripts/sync_supabase.py

syncs to Supabase / Postgres

WhatsApp push delivery

scripts/notify_whatsapp.py

src/edgefactory/whatsapp.py

reads localdata/picks_today.json

dedupes against localdata/whatsapp_sent_ledger_YYYY-MM-DD.json

dispatches via Meta Cloud, Twilio, or CallMeBot

Current settled / source DuckDB views include:

forebet_settled

zulubet_settled

statarea_settled

predictz_settled

scoutingstats_settled

bettingclosed_settled

vitibet_settled

raw and capture-forward source views

consensus views

Daily run order:

capture_daily

backfill_results

build_warehouse

build_entity_registry

mine_consensus

decay_monitor

assay_purity

picks_today

archive target-day picks JSON

audit_clv pick_time

inline future planner

restore target picks

audit_clv end_of_run

audit_clv rolling report

audit_recent_picks rolling report

sync_supabase

notify_whatsapp (final step, runs in all official and intraday modes)

Naming convention:

Keep scripts/daily.py as the only orchestrator.

Do not add scripts/nightly.py.

Do not add scripts/picks_future.py.

Future reports should remain:

localdata/picks_2026-06-16.txt

localdata/picks_2026-06-17.txt

Aggregate future JSON remains:

localdata/picks_next_2days.json

Do not reintroduce:

localdata/picks_calendar.csv

Golden rules
These are non-negotiable.

Use Wilson lower bound, never raw hit rate, for certification.

Use walk-forward only. No mini-backtests.

Show ROI alongside hit rate, always.

Edge decay states are HEALTHY, WATCH, DECAYING, and DEAD.

Best odds can inflate ROI versus real execution. Always caveat this.

Any disagreement is dangerous. Known disagreement hit rate is poor.

Draw picks have historically not worked.

Away-only edges remain negative ROI in validation. Do not certify away-only edges on current data.

OU 2.5 unanimous edges remain negative ROI across thresholds. They are not certified.

New sources must be mined standalone before being added as levers.

Market / odds data is not the same as model prediction data.

Do not change certified warehouse / miner join keys without full revalidation.

Critical normalization rule
A regression happened when norm_team() / norm_team_sql() were widened to accent-folded or broader keys. That inflated warehouse joins and collapsed certified edge count.

Bad inflated state observed:

consensus2: about 33k

consensus3: about 19k

consensus4: 526

certified edges dropped to 2

Correct restored state:

consensus2: about 27,450

consensus3: about 15,807

consensus4: about 383

certified audited / benched / active: 9 / 1 / 8

Join-key rule:

norm_team() and norm_team_sql() are legacy 9-character miner / source join keys.

Do not change them casually.

norm_entity_team(), canonical_team(), and canonical_league() are for purity, reporting, and entity-registry use.

Those entity functions are safe for context grouping, but not for miner joins.

Entity registry is for:

purity

reporting

context lookup

read-model keys

It must not silently alter warehouse / miner joins.

It is also not trusted enough for operational live odds or CLV event matching.

Those now use exact matching, explicit odds-only aliases, and kickoff-aware fallback instead.

Key files

Core package:

src/edgefactory/assay.py

Wilson LB / UB

grading

decay_verdict

ROI

should_bench

context verdict helpers

weighted_consensus_score

src/edgefactory/util.py

norm_team()

norm_team_sql()

legacy miner join keys, do not drift

src/edgefactory/entities.py

canonical_league()

canonical_team()

entity registry loading

context and reporting only

src/edgefactory/market_registry.py

market classification

odds-tier classification

src/edgefactory/clv.py

pure CLV helpers

pick ids

implied probability conversion

odds movement summaries

src/edgefactory/sources/bzzoiro_odds.py

real-book odds adapter

now preserves kickoff time for operational matching and CLV snapshots

src/edgefactory/config.py

certification gates

important defaults:

min_n_train=350

min_n_valid=120

split="2025-06-01"

calls load_dotenv() at import time so a local .env is auto-loaded

src/edgefactory/warehouse.py

DuckDB connect() and views

all views carry sport='soccer'

src/edgefactory/db.py

Supabase client via create_client(url, key)

reads SUPABASE_URL and SUPABASE_SERVICE_KEY (service_role key)

raises ValueError if either is missing

calls load_dotenv() so a local .env is auto-loaded

src/edgefactory/whatsapp.py

WhatsApp dispatch providers: Meta Cloud, Twilio, CallMeBot

BUCKET_CLEAN, BUCKET_CAUTION constants

format_whatsapp_summary() mobile-optimized summary

send_meta_whatsapp_cloud() with template fallback

send_twilio_whatsapp()

send_callmebot_whatsapp() — see section 9 for required endpoint fix

Scripts:

scripts/capture_daily.py

D30 capture for all sources

supports --skip-build

scripts/backfill_results.py

D30 default result repair after capture and before warehouse build

compact output by source

idempotent

scripts/build_warehouse.py

materializes CSV cache into localdata/warehouse.duckdb

scripts/build_entity_registry.py

learns league / team aliases into localdata/entity_registry.json

uses overlap evidence and config/entity_overrides.json

scripts/mine_consensus.py

walk-forward consensus miner

writes localdata/edges_consensus.json (this file is committed to the repo via a .gitignore exception so the certified registry survives cache eviction)

includes Phase A shadow scans for PredictZ and Windrawwin

write_registry() regression-to-zero circuit breaker: if a run certifies 0 edges but the existing registry already holds certified edges, the existing file is preserved instead of being clobbered. This prevents a single cold-cache run from permanently zeroing the registry and cascading into empty picks/WhatsApps. See section 16.

scripts/decay_monitor.py

60-day health audit

auto-bench circuit breaker

scripts/assay_purity.py

context purity registry

default --window 36500

scripts/picks_today.py

certified picks engine

purity-aware buckets

primary live odds from bzzoiro_odds

secondary live odds fallback from scoutingstats cached rows

weighted consensus display and sorting

operational duplicate-pick collapse after bucket assignment, before final output and sync

pre-match guard skips same-day picks that are already started / inside the configured lead window or missing kickoff

final collapse is local to pick/report output; it does not mutate miner join keys

final collapse strips only safe club tokens such as AC / FC / IFK, preserves W / U19 / B / II / reserve-like identity suffixes, and propagates the worst bucket across duplicate aliases

scripts/audit_clv.py

CLV capture and report utility

capture is wired into daily.py with pick_time and end_of_run labels

report stays audit-only in v1

writes unmatched diagnostics for missed live odds matches

scripts/audit_recent_picks.py

recent operational performance audit

reads archived picks_YYYY-MM-DD.json files and scores settled 1x2 picks against warehouse results

scripts/daily.py

single orchestrator

also contains inline future planner

also triggers CLV capture and rolling report

archives target-day picks JSON and runs recent picks audit

calls sync_supabase then notify_whatsapp as the final steps of every official and autonomous_intraday run (both via run_soft, so a push failure never fails the whole job)

freezes target-date picks: if localdata/picks_YYYY-MM-DD.json already exists, reruns restore them instead of regenerating unless --force-repick is passed

passes one fixed EDGE_FACTORY_RUN_AS_OF timestamp into all picks_today invocations for that run

supports automated scheduling via --auto-run / --auto-once, splitting official morning heavy runs from lightweight intraday forecast refreshes

supports non-official forecast refreshes via --forecast-refresh, archiving to localdata/forecast_YYYY-MM-DD_HHMM.json and .txt

supports deliberate promotion of forecast runs to official records via --promote-forecast

scripts/sync_supabase.py

syncs certified edges and daily bucketed picks to Supabase

scripts/notify_whatsapp.py

WhatsApp dispatch engine

reads localdata/picks_today.json

only pushes CERTIFIED_CLEAN and CAUTION picks

dedupes against localdata/whatsapp_sent_ledger_YYYY-MM-DD.json

supports --force, --date, --late-slate-only

supports --force to bypass the sent ledger

Optional research-only scripts:

scripts/backfill_betexplorer.py

BetExplorer result / odds cache

not production

scripts/mine_betexplorer.py

standalone / overlap mining on BetExplorer cache

not production

Manual safety layer:

config/entity_overrides.json

Source status
Prediction adapters:

forebet

core

1x2 / OU / BTTS / HT

high-volume

backfillable

zulubet

core

1x2

backfillable

statarea

core

1x2 / OU

backfillable

vitibet

active but thin

1x2

archive exists but thinner in consensus4

scoutingstats

partial

sparse 1x2 / OU / BTTS

mostly capture-forward

predictz

shadow-only

captured

settled rows exist

Phase A only

windrawwin

shadow-only

captured

very thin

Phase A only

betclan

partial live

used partially as capture-forward 1x2 source

bzzoiro

partial live

used partially as live model source

freesupertips

not ready

captured but too thin or unmapped for current mining

bettingclosed

confirmation lever

large settled source

Odds / market-data adapters:

bzzoiro_odds

operational primary live odds enrichment for picks_today

scoutingstats embedded odds

operational secondary live odds fallback for picks_today and CLV capture

BetExplorer

research only

last resort only

not a primary production source

Unused or mostly unused prediction sources:

predictz

windrawwin

freesupertips

afootballreport

Phase A showed PredictZ and Windrawwin are not ready for certification under the current split.

Certified edge state

Latest stable counts:

consensus2: about 27,450

consensus3: about 15,807

consensus4: about 383

Latest certified audit shape:

certified audited: 9

benched by decay: 1

active certified: 8

Expected active / base findings:

2way-unanimous avg_p>=70 -> WATCH / active

3way-unanimous avg_p>=65 -> HEALTHY / active

2way-unanimous min_p>=60 avg_p>=65 -> HEALTHY / active

3way-unanimous min_p>=60 avg_p>=60 -> WATCH / active

3way-unanimous min_p>=60 avg_p>=65 -> WATCH / active

2way-unanimous home-only avg_p>=65 -> HEALTHY / active

3way-unanimous home-only avg_p>=60 -> HEALTHY / active

3way-unanimous home-only avg_p>=65 -> HEALTHY / active

Benched by the 60-day decay circuit breaker:

2way+bc-confirms avg_p>=60

Do not manually unbench. The next scripts/mine_consensus.py run re-evaluates from full walk-forward history.

Operational picks_today.py thresholds are base canonical only:

2-way: 2way-unanimous avg_p>=70

3-way: 3way-unanimous avg_p>=65

Qualified rules are for analysis and purity only. They must not displace base thresholds.

Qualified tokens include:

min_p

home-only

away-only

odds-

bc-confirms

predictz-confirms

windrawwin-confirms

freesupertips-confirms

Purity and bucket status
Default purity assay:

--window 36500

Current reality:

league / team purity remains sparse or unrated inside certified-rule subsets

odds-band purity is mature and useful

Operational bucketing logic:

benched / dead / decaying edge -> SKIPPED_DEAD_EDGE

VETO anywhere -> SKIPPED_VETO

missing odds -> WATCHLIST_NO_ODDS

UNKNOWN odds band -> WATCHLIST_UNKNOWN_CTX

CAUTION anywhere -> CAUTION

UNKNOWN league / team only -> CAUTION

otherwise -> CERTIFIED_CLEAN

Rationale:

UNKNOWN league / team means unrated, not bad

odds-band VETO and CAUTION are mature enough to matter operationally

Recent examples:

Vaprus vs Flora Tallinn -> CAUTION

Always Ready vs Universitario de Vinto -> CAUTION

Fortaleza vs América Mineiro -> SKIPPED_VETO due to odds-band VETO

Phase A — unused-source confirmation
Implemented as shadow / maturity scans only.

Rules scanned:

2way+predictz-confirms avg_p>=60/65/70/75

3way+predictz-confirms avg_p>=60/65/70

2way+windrawwin-confirms avg_p>=60/65/70/75

3way+windrawwin-confirms avg_p>=60/65/70

scripts/decay_monitor.py and scripts/assay_purity.py recreate the corresponding TEMP views so future certified Phase A edges would not silently skip audit or assay.

Current result:

PredictZ archive starts around 2026.

Windrawwin is capture-forward only.

Global split is 2025-06-01.

Therefore train sample for these levers is n = 0.

These appear in a shadow section but are excluded from localdata/edges_consensus.json by normal training gates.

Do not use PredictZ or Windrawwin in picks yet. Do not force certification.

WhatsApp push delivery — operational and required fix
A WhatsApp notification dispatch system was added to daily.py. It is the final step of every official and autonomous intraday run, running after sync_supabase.

Files:

scripts/notify_whatsapp.py — dispatch orchestrator

src/edgefactory/whatsapp.py — provider implementations

Provider support (first active set wins; all active providers fire):

Meta WhatsApp Cloud API

requires WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_RECIPIENT

optional WHATSAPP_TEMPLATE_NAME, default edgefactory_picks_alert

has template fallback when Meta free-form text fails outside the 24h service window (error 131047)

Twilio WhatsApp API

requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, WHATSAPP_RECIPIENT

CallMeBot API (100% free personal alerts, the current intended path)

requires CALLMEBOT_APIKEY, CALLMEBOT_PHONE

CALLMEBOT_PHONE falls back to WHATSAPP_RECIPIENT if unset

Dispatch behavior:

Only CERTIFIED_CLEAN and CAUTION buckets are pushed.

Dedup ledger: localdata/whatsapp_sent_ledger_YYYY-MM-DD.json.

First run of the day (no ledger yet) is the "morning slate" — all notifiable picks are pushed.

Later intraday runs are "late slate" — only newly appearing, not-yet-sent picks are pushed. If there are no new picks, notify_whatsapp stays silent on purpose ("Remaining silent").

--force bypasses the sent ledger and resends all notifiable picks.

--late-slate-only forces strict intraday scan mode.

CRITICAL REQUIRED FIX (2026-06-18):

send_callmebot_whatsapp() in src/edgefactory/whatsapp.py currently builds the wrong endpoint:

url = f"https://api.callmebot.com/whatsapp.py?phone={clean_phone}&text={encoded_text}&apikey={apikey}"

The endpoint is whatsapp.php, not whatsapp.py. The current code hits a 404 on every dispatch, raises an exception, and notify_whatsapp.py logs it and continues with dispatched=False. Because daily.py calls notify_whatsapp via run_soft, the job still finishes green. This is why runs succeed but no WhatsApps arrive.

Fix: change whatsapp.py -> whatsapp.php in that URL.

url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_text}&apikey={apikey}"

Two additional gates that must be true or pushes stay silent on purpose:

GitHub secrets must actually exist and be non-empty: CALLMEBOT_APIKEY, CALLMEBOT_PHONE. The workflow commit that added the env lines only wired the YAML; it does not set the secret values. Verify in Settings -> Secrets and variables -> Actions.

CallMeBot must be authorized. From your own WhatsApp, add the CallMeBot number and send exactly:

I allow callmebot to send me messages

You will receive "API Activated for your phone number. Your APIKEY is ...". Use that returned key as CALLMEBOT_APIKEY.

Do not expect 8 messages/day. The dedupe ledger is cached across the 3-hourly runs via actions/cache on localdata, so by design you get about one morning message plus late-slate alerts only when brand-new fixtures appear.

Supabase
Migrations live in:

supabase/migrations/

Migration status:

0001_core.sql

0002_signals.sql

0003_edges.sql

0004_new_sources.sql

0005_all_sources.sql

0006_edge_pick_context.sql

What scripts/sync_supabase.py promotes:

certified edges -> edges

bucketed daily picks -> edge_picks

Live ingestion and analytics remain CSV / DuckDB, not Supabase.

Required environment variables (verified against the actual code):

BZZOIRO_TOKEN read by the bzzoiro odds / model adapter
SUPABASE_URL read by src/edgefactory/db.py
SUPABASE_SERVICE_KEY read by src/edgefactory/db.py (service_role key, server-side only)
CALLMEBOT_APIKEY read by scripts/notify_whatsapp.py
CALLMEBOT_PHONE read by scripts/notify_whatsapp.py

Note: the earlier handover listed SUPABASE_KEY. That is dead weight. The live client in db.py reads SUPABASE_SERVICE_KEY (the service_role key) and raises ValueError if it is missing. Do not rely on SUPABASE_KEY.

A local .env IS auto-loaded. config.py, db.py, and notify_whatsapp.py all call load_dotenv() at import, so set -a; source .env; set +a is no longer required (though it remains harmless). Just keep a .env at repo root for local runs.

For GitHub Actions, secrets (not .env) are the source of truth. The workflow daily.yml declares: SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY, BZZOIRO_TOKEN, CALLMEBOT_APIKEY, CALLMEBOT_PHONE, TZ=Africa/Johannesburg. Verify all are set under Settings -> Secrets and variables -> Actions.

How to run
Install requirements:

pip install -r requirements.txt

Export environment (local only; .env is auto-loaded by load_dotenv):

cp .env.example .env

then edit .env with real values
set -a; source .env; set +a # optional; load_dotenv already handles this

Full daily:

PYTHONPATH=src python3 scripts/daily.py

Autonomous 3-Hour Service (Local Background Loop):

PYTHONPATH=src python3 scripts/daily.py --auto-run

Autonomous Cloud Service (100% Free on GitHub Actions):

Enabled by default in .github/workflows/daily.yml

Wakes up every 3 hours (00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 UTC)

Uses GitHub Actions Cache (actions/cache) to completely persist the localdata/ DuckDB warehouse, pick ledgers, CLV snapshots, and the WhatsApp sent ledger across runs

Uploads human-readable pick reports (.txt) and ledgers as downloadable workflow artifacts

Runs sync_supabase then notify_whatsapp to push certified edges, accumulating picks, and phone alerts

Fully self-sustaining and costs $0.00

Picks only:

PYTHONPATH=src python3 scripts/daily.py --picks-only --future-days 2

Specific date:

PYTHONPATH=src python3 scripts/daily.py --date 2026-06-16

Manual WhatsApp push (after the endpoint fix):

PYTHONPATH=src python3 scripts/notify_whatsapp.py
PYTHONPATH=src python3 scripts/notify_whatsapp.py --force
PYTHONPATH=src python3 scripts/notify_whatsapp.py --date 2026-06-18

Individual stages:

python3 scripts/capture_daily.py --skip-build

python3 scripts/backfill_results.py --days 30

python3 scripts/build_warehouse.py

PYTHONPATH=src python3 scripts/build_entity_registry.py

python3 scripts/mine_consensus.py

PYTHONPATH=src python3 scripts/decay_monitor.py

PYTHONPATH=src python3 scripts/assay_purity.py

PYTHONPATH=src python3 scripts/picks_today.py 2026-06-16

cp localdata/picks_today.json localdata/picks_2026-06-16.json

PYTHONPATH=src python3 scripts/audit_clv.py capture --date 2026-06-16 --label pick_time

PYTHONPATH=src python3 scripts/audit_clv.py capture --date 2026-06-16 --label end_of_run

PYTHONPATH=src python3 scripts/audit_clv.py report --start 2026-05-18 --end 2026-06-16

PYTHONPATH=src python3 scripts/audit_recent_picks.py --end 2026-06-16 --days 30

PYTHONPATH=src python3 scripts/sync_supabase.py

PYTHONPATH=src python3 scripts/notify_whatsapp.py

Tests:

PYTHONPATH=src python3 -m pytest tests/ -q

If optional Supabase dependencies are missing, at minimum run:

PYTHONPATH=src python3 -m pytest tests/test_assay.py -q

python3 -m py_compile src/edgefactory/util.py src/edgefactory/entities.py src/edgefactory/whatsapp.py scripts/*.py

Known issues and caveats
Cold-cache certification trap

certification needs deep pre-split history; a cold/evicted GitHub Actions cache holds only a D30 post-split window, so it certifies 0 edges

fixed 2026-06-18: edges_consensus.json is committed to the repo and mine_consensus.write_registry() preserves a good registry when a run certifies nothing

if "REGRESSION GUARD" appears in the logs, the existing registry was kept; restore full history and re-mine to refresh it

WhatsApp / CallMeBot

the CallMeBot endpoint in src/edgefactory/whatsapp.py is whatsapp.py and must be changed to whatsapp.php (see section 9)

CallMeBot must be authorized from the owner's phone before any message will be delivered

GitHub secrets CALLMEBOT_APIKEY and CALLMEBOT_PHONE must be set; the workflow env lines alone are not enough

notify_whatsapp runs via run_soft, so a silent push failure never fails the overall job

only CERTIFIED_CLEAN and CAUTION picks are pushed; WATCHLIST / SKIPPED buckets are never pushed

GitHub Actions runner

Node.js 20 is deprecated; actions/checkout@v4, actions/setup-python@v5, actions/cache@v4, actions/upload-artifact@v4 are forced to run on Node 24. Cosmetic for now; bump action versions later.

punycode DeprecationWarning comes from curl_cffi and is cosmetic.

BetExplorer

investigated and concluded not useful as alpha

keep optional only

PredictZ and Windrawwin

shadow-only

train n = 0 under current split

league / team purity

sparse or unrated

treat UNKNOWN as CAUTION, not a hard block

odds-band purity

mature and useful

CLV audit

currently audit-only

same-day report is only meaningful after at least two snapshot labels exist for a pick

current daily.py captures pick_time and end_of_run automatically

same-label reruns are expected to show duplicate skips

CLV / steam / drift must not gate picks_today buckets until separately validated and promoted

recent picks audit

currently 1x2-only and settled-results-only

depends on archived picks_YYYY-MM-DD.json files existing

legacy per-date .txt reports from before 2026-06-17 are human reference only and should not be used as machine-performance history for the current regime

operational live odds matching no longer relies on entity-registry canonical fallback

current live odds order is bzzoiro_odds first, then scoutingstats embedded odds, then existing pick-row fallback

matching path inside each odds source is exact match, explicit odds-only aliases, then kickoff-aware alias fallback

unmatched diagnostics are written to localdata/clv_unmatched_YYYY-MM-DD.json

operational duplicate picks are collapsed after bucket assignment and before final picks_today output and sync

picks_today.json must be exactly the rows requested by the current invocation; do not merge stale existing picks_today.json rows back into a fresh run

same-date reruns must be archive-first: daily.py restores localdata/picks_YYYY-MM-DD.json unless --force-repick is explicitly passed

past-date picks must not be regenerated from live source pages; use the archived JSON only

bzzoiro

requires BZZOIRO_TOKEN

curl_cffi

required for PredictZ, Windrawwin, and BetClan scraping

consensus4

still thin because Vitibet overlap is limited

BetExplorer 404s

stale archived URLs exist

failure cache handles them

Future priorities — productive focus
Stop chasing BetExplorer unless doing deliberate CLV research.

Recommended next work:

Stabilize and commit the current pipeline.

keep repo clean

keep handover updated

avoid broad payloads

Monitor current certified soccer edges.

let the decay circuit breaker do its job

do not manually unbench

CLV with existing operational odds.

current state: pick_time and end_of_run snapshots are wired into daily.py

keep CLV audit-only for now

improve odds coverage and later-snapshot usefulness

track pick-time price versus later or closing price

only later consider CLV as a feature

WhatsApp delivery reliability.

apply the whatsapp.php endpoint fix

confirm CallMeBot authorization and GitHub secrets

add a smoke test that asserts the CallMeBot URL ends with whatsapp.php

Tournament / league classification.

classify competitions such as domestic league, cup, friendly, international, youth / reserves / women

use entity registry and league names to classify

then mine categories separately or veto categories separately

ML as a validated source.

possible features: source probabilities, agreement count, min_p, avg_p, spread, odds tier, price movement, source confirmations, entity tags, tournament tags

a model must be treated as another source and validated by the same miner / decay gates

New sports later.

do not add another sport yet

soccer still has clear remaining upside in CLV, tournament classification, model-source validation, and push delivery

Engineering lessons — mandatory
L1 — Three-script view graph

mine_consensus.py creates TEMP views.

decay_monitor.py and assay_purity.py must recreate those views.

When adding a miner view, add the same SQL to both recreate functions.

Failure mode is silent: UNKNOWN / SKIP in decay or purity.

L2 — consensus2 does not expose hkey / akey

consensus2 joins internally on keys but only outputs:

date

home

away

outcome

fb_pick

zb_pick

fb_p

zb_p

avg_p

pick_odds

league

When joining from consensus2 or v_consensus2, join on date, home, and away.

Do not join on hkey or akey.

L3 — Qualified rules must not govern picks_today thresholds

Rules containing any of the following are analysis variants only:

min_p

home-only

away-only

odds-

bc-confirms

predictz-confirms

windrawwin-confirms

freesupertips-confirms

They must not displace canonical operational thresholds.

L4 — No stubs or placeholders

Do not leave:

...

keep existing

editorial comments pretending to be code

Payload files must be complete and runnable.

L5 — No runtime globals

Avoid module-level globals initialized inside main().

Pass state explicitly.

L6 — Decay circuit breaker is correct

DECAYING -> BENCHED means the system is working.

Do not manually edit the registry to unbench.

L7 — Executor copies payloads, never rewrites

Install payload files by cp.

Do not reconstruct from chat.

L8 — Do not mutate certified join keys

norm_team() and norm_team_sql() are miner-critical.

Do not change them without full revalidation.

L9 — Silent failures in non-critical steps hide real problems

notify_whatsapp and the optional CLV / sync steps run via run_soft and never fail the job.

A green Actions run does NOT prove that WhatsApps were delivered or that Supabase was written.

Always confirm delivery from the phone or from the run logs (look for "CallMeBot Dispatch Success") before assuming push works.

L10 — Cold-cache certification trap (discovery vs application)

Certification needs deep pre-split history (min_n_train=350, split=2025-06-01).

capture_daily only pulls a rolling D30 window, which is entirely post-split.

Therefore a cold or evicted GitHub Actions cache CANNOT certify any edge: train n = 0 -> 0 certified -> empty registry.

An unguarded empty registry then cascades: 0 certified -> picks_today fallback -> 0 picks -> empty WhatsApp, and the intraday loop stays wedged in Case 2 for the rest of the day.

The fix is the discovery-vs-application split: edges_consensus.json is committed to the repo (survives cache loss) and mine_consensus.write_registry() refuses to overwrite a good registry with a zero-certified result.

Deep historical mining (re-validation, new sources, threshold scans) remains a periodic local job on the machine with full history. Daily CI is application only: it applies the committed certified edges to fresh fixtures.

L11 — Cache restore overwrites committed registries (the run #17 trap)

Two layers protect the certified registry, and BOTH are required:

.gitignore exception commits edges_consensus.json and purity_registry.json to the repo.
mine_consensus.write_registry() guards against a cold run clobbering a good registry.
But neither alone fixes CI, because actions/cache/restore unpacks localdata/ AFTER checkout and silently overwrites the committed registries with a stale 0-certified copy from an earlier cold run. The guard then sees existing_certified=0 and lets the zero-write through.

The third layer (required) is a workflow step "Restore committed registries" that runs after cache restore and re-checks out the committed registries from HEAD (git checkout HEAD -- localdata/edges_consensus.json localdata/purity_registry.json). This guarantees the committed live registry wins over stale cache before mining runs.

Sequence on a cold CI run after all three layers:
checkout (9) -> cache restore (0, overwrites) -> committed-registry restore (9, HEAD wins) -> mining (0 certified from cold warehouse) -> write_registry guard (preserves 9).

Never remove the committed-registry restore step. It is the only thing that survives cache clobber.

L9 — Silent failures in non-critical steps hide real problems

notify_whatsapp and the optional CLV / sync steps run via run_soft and never fail the job.

A green Actions run does NOT prove that WhatsApps were delivered or that Supabase was written.

Always confirm delivery from the phone or from the run logs (look for "CallMeBot Dispatch Success") before assuming push works.

Operational standard — anti-drift protocol
Every repo change should follow:

BUILDER -> EXECUTOR -> VERIFIER

Payload bundle must include:

payload files

SHA256SUMS

commit_msg.txt

executor notes

Rules:

verify payload hash before touching repo

required base commit should be pinned

install by cp only

run py_compile and tests

confirm git status has only expected files

do not leave helper files in repo

claims without fresh clone or on-GitHub verification are not proof

Data-job exception:

localdata/ is gitignored, so data jobs are the main exception

even then, still require clean git status

and require a row-count report

Current call
BetExplorer investigation is concluded. It is not useful enough to add to consensus or picks.

CLV audit spike is now live.

Current CLV state:

pick_time and end_of_run snapshots are captured automatically from scripts/daily.py

reporting is audit-only

same-label reruns dedupe correctly

a report with only one snapshot per pick must show no CLV comparison yet

live odds matching is isolated from entity-registry canonical fallback

current operational path is bzzoiro_odds first, then scoutingstats embedded odds, with exact match, explicit odds-only aliases, and kickoff-aware alias fallback inside each source

CLV / steam / drift remains audit-only and is not allowed to move a pick into SKIPPED_VETO

Current cold-cache / empty-registry fix, 2026-06-18:

Incident: run #14 delivered a green job and a successful CallMeBot dispatch, but the WhatsApp message was empty ("No matching certified edges found"). Root cause: the GitHub Actions cache was evicted, so the warehouse held only a post-split D30 window. mine_consensus then certified 0 edges (train n=0 < min_n_train=350), overwrote edges_consensus.json to empty, and that cascaded into 0 picks across every bucket. The intraday loop stayed frozen in Case 2 for the rest of the day because it does not rebuild the warehouse.

Root cause confirmed by the log line: "edge registry missing/empty -> fallback to certified thresholds" plus 0 picks across all buckets.

Fix applied (discovery vs application split):

localdata/edges_consensus.json is now committed to the repo via a .gitignore exception (!localdata/edges_consensus.json). It survives cache eviction and is the daily source of truth for certified thresholds, decay, and purity context.

scripts/mine_consensus.py gained write_registry() with a regression-to-zero circuit breaker. If a run certifies 0 edges but the existing registry already holds certified edges, the existing file is preserved and a "REGRESSION GUARD" warning is logged. Both write sites (the no-warehouse early exit and the normal end of run) route through it.

Deep historical re-validation (new sources, threshold scans, re-certification) remains a periodic LOCAL job on the machine with full pre-split history. After mining locally, commit the refreshed edges_consensus.json. Daily CI is application only: apply the committed certified edges to fresh fixtures.

Required action to restore live picks: mine locally with full history, confirm edges_consensus.json has the expected ~9 certified / 8 active, commit it, then trigger Actions -> Run workflow -> mode: official_morning.

Secondary issues still open from the same run (not blocking the registry fix):

bzzoiro odds enrichment returned enriched=0 in run #14. Investigation confirmed this is a SYMPTOM, not a root cause: picks get odds from forebet/zulubet prediction data inside eval_1x2 before enrichment runs, so enrichment is an UPGRADE to real bookmaker odds, not a requirement for a pick to exist. enriched=0 means picks kept their source odds. The run had 0 picks in every bucket (including WATCHLIST_NO_ODDS=0) because 0 picks survived the 21:52 SAST pre-match guard (almost all same-day matches had kicked off), compounded by the empty registry. The odds index itself loaded fine: 948 cached rows -> 63 valid keys.

The bzzoiro enrichment diagnostic in picks_today.py was upgraded to print picks=, bzz_alias_keys=, and none= so future runs are self-diagnosing. enriched=0 + picks=0 means "nothing to enrich"; enriched=0 + picks>0 means "matching failed" (a real odds-key gap).

Known team-name matching fragility (audit-only, enhancement quality): exact-match (9-char norm_team key) matches ~8/12 realistic cross-feed pairs. The 9-char truncation actually outperforms full-length alias matching. Failing pairs are abbreviation differences that no normalization resolves without an explicit alias table (Man City vs Manchester City, Dortmund vs Borussia Dortmund, Sporting CP vs Sporting Lisbon, Wolfsburg vs VfL Wolfsburg). These do NOT block picks (forebet odds are retained) but mean ~1/3 of potential upgrades silently miss. Fix only if live-book odds coverage becomes a priority; expand ODDS_TEAM_ALIASES carefully (do not use entity-registry canonical fallback for live odds — it over-merges).

scoutingstats timed out ("The read operation timed out") in run #14, so the secondary odds fallback was unavailable.

Current WhatsApp delivery fix, 2026-06-18:

WhatsApp push dispatch is wired into daily.py as the final step after sync_supabase, via scripts/notify_whatsapp.py and src/edgefactory/whatsapp.py.

It supports Meta Cloud, Twilio, and CallMeBot; the current intended free path is CallMeBot.

Only CERTIFIED_CLEAN and CAUTION picks are pushed.

It dedupes against localdata/whatsapp_sent_ledger_YYYY-MM-DD.json and is deliberately silent when there are no new picks after the morning slate.

Root cause of missing WhatsApps identified: send_callmebot_whatsapp() uses the endpoint whatsapp.py instead of whatsapp.php, so every dispatch returns 404, raises, and is swallowed by run_soft while the job still finishes green.

Required actions before the next run:

apply the whatsapp.py -> whatsapp.php endpoint fix in src/edgefactory/whatsapp.py

set GitHub secrets CALLMEBOT_APIKEY and CALLMEBOT_PHONE

authorize CallMeBot from the owner's phone ("I allow callmebot to send me messages")

trigger Actions -> Run workflow -> mode: official_morning to force a fresh push

Current operational determinism / identity fix, 2026-06-18:

A duplicate-event leak was observed in localdata/picks_2026-06-18.txt: AC Oulu vs IFK Mariehamn and AC Oulu vs Mariehamn appeared as separate rows with different rules / buckets.

The same target date also changed between morning and afternoon reruns: new same-day picks appeared later and buckets changed as live source pages / odds changed. This makes 2026-06-18 operational history tainted unless using a clearly frozen first archive.

Fix applied in scripts/picks_today.py and scripts/daily.py:

one run-level EDGE_FACTORY_RUN_AS_OF timestamp is passed from daily.py to picks_today.py

same-day picks are filtered by a pre-match guard; default EDGE_FACTORY_MIN_LEAD_MINUTES is 30

same-day rows with missing kickoff are skipped rather than treated as bettable

past dates are not regenerated from live pages by daily.py; archived localdata/picks_YYYY-MM-DD.json is restored instead

same-date reruns are archive-first unless --force-repick is passed

picks_today.py no longer merges stale existing picks_today.json rows into the new run

final duplicate collapse now runs after context bucketing so VETO / DEAD cannot be hidden by pre-bucket de-dupe

same real-world event / same market / same pick collapses across 2-way and 3-way rules

worst bucket wins across duplicate aliases

safe club tokens AC / FC / IFK etc. are stripped only in the final operational output key

identity-bearing W / U19 / B / II / reserve suffixes are preserved

Khovd FC and Khovd Western remain distinct

IFK Mariehamn / Mariehamn is an explicit odds alias

learned entity-registry canonical fallback was removed from live odds matching

CLV / steam / drift is audit-only and cannot move picks into SKIPPED_VETO

Regression tests live in tests/test_picks_today_operational.py

Operational audit note: do not use the conflicting 2026-06-18 reruns as clean machine-performance history. Restart trusted pick-performance accounting from the first frozen run after this fix.

Current automated scheduling and forecast separation update, 2026-06-18:

Implemented official vs non-official forecast separation and automated 3-hour service in scripts/daily.py:

scripts/daily.py --auto-run: Smart automated 3-hour background service. Auto-detects whether to run the heavy official morning run (if today's official frozen archive localdata/picks_YYYY-MM-DD.json does not exist) or lightweight intraday forecast refreshes and CLV monitoring.

scripts/daily.py --auto-once: Executes exactly one smart auto schedule iteration and exits.

scripts/daily.py --forecast-refresh: Deliberate mode for non-official forecast refreshes. Saves newly appearing fixtures and odds to localdata/forecast_YYYY-MM-DD_HHMM.json and .txt, captures qualitative intraday CLV snapshots (midday, afternoon, evening), and automatically restores live picks_today.json from the official archive to guarantee pristine official performance accounting.

scripts/daily.py --promote-forecast [PATH|LABEL]: Deliberately promotes a specific forecast refresh to become the official tracked performance ledger and pushes to Supabase.

Core pipeline orchestrator remains single source of truth; no separate nightly or future scripts were added.

Automated orchestration tests live in tests/test_daily_orchestration.py.

Current regime rule:

restart trusted machine-performance history from the first frozen run after the 2026-06-18 determinism fix

treat older .txt reports and conflicting 2026-06-18 reruns as legacy human reference only

let the current soccer system run for about one clean week before deciding on another sport

Readiness gate before sport #2:

seven consecutive current-regime runs without major breakage

recent picks audit populated with real settled results

live odds coverage no longer obviously broken

WhatsApp push delivery confirmed working end to end

no recurring duplicate-event or identity drift issues

Next session should focus on:

apply the whatsapp.php endpoint fix and confirm phone delivery

stable current daily pipeline

monitoring certified edges

CLV coverage and later-snapshot quality using existing bzzoiro_odds and real-book odds

avoiding broad source rabbit holes unless standalone proof exists

Last updated: 2026-06-18

Diagnostic session and pipeline fix — 2026-06-24

What happened
Full read-only diagnostic of the past week's performance. No code was changed until the root cause was confirmed. Two lines edited in scripts/picks_today.py. Committed as 4c38294.

Audit baseline (picks_audit_rolling.json, 2026-05-26 to 2026-06-24)
Settled picks: 14
Hit rate: 85.7% (12/14)
Overall ROI: +9.79%
CAUTION bucket ROI: +14.7%
3way-unanimous avg_p>=65 ROI: +21.0% (7/8)
2way-unanimous avg_p>=70 ROI: -8.2% (5/6) — losses were draws on World Cup games, not a rule failure
Source coverage reality
The warehouse was queried directly against the settled tables for 2026-06-19 to 2026-06-24.

Forebet covers 839 games per week. Zulubet covers 220. Statarea covers 254.

The 3-way join survives only 38 games — 4.5% of forebet's universe.

The low join rate this week is a seasonal anomaly, not a structural flaw. European leagues (EPL, La Liga, Serie A, Bundesliga) are on summer break. Those are the leagues all three sources agree on. The certified 3way edge is grounded on WCQ (92 qualifiers, 81 wins), EPL (54 qualifiers, 48 wins), La Liga (71, 58), and Serie A (72, 51). Ireland and Iceland dominate this week's output only because they are the only top-tier competition still running.

Zulubet and statarea are not coverage-poor for the leagues that matter. They simply do not cover lower-division summer slates. This self-corrects in August.

Naming mismatches confirmed
Four World Cup games failed to join at all due to source naming divergence:

Germany vs Ivory Coast: forebet/zulubet use Ivory Coast, statarea uses Cote D Ivoire → hkeys ivorycoas vs cotedivoi → no join
Türkiye vs Paraguay: forebet uses Türkiye → hkey trkiye; statarea uses Turkey → hkey turkey → no join
Ecuador vs Curaçao: forebet/zulubet strip accent → curaao; statarea preserves it → curacao → no join
Colombia vs Congo DR: forebet uses DR Congo → hkey drcongo; zulubet/statarea use Congo DR → hkey congodr → no join
These are real mismatches. They are seasonal and specific to international tournaments where source naming conventions diverge. Do not fix them during the European summer break. Revisit with entity_overrides.json in August when the volume justifies it.

The actual bug: scan_best base-view bleed
France vs Iraq qualified on consensus3: 74% avg_p, all three sources unanimous, France won comfortably. It appeared in picks_2026-06-22.json as SKIPPED_VETO.

Root cause: the odds band lookup fallback in lookup_context() used:

text

odds_fallback = _scan_best(odds_ctx, prefix=f"{sport}|{market}|", suffix=f"|{band}")
The prefix soccer|1x2| matched every entry in the purity registry including v_consensus2_base and v_consensus3_base. Those base views carry n=2697 and n=1658 respectively and have VETO verdicts on the 1.75-2.00 band (roi=-6.6% and -6.9% on unfiltered all-games data). scan_best selects by max(n), so the base-view VETO always won over the rule-specific entry which had n=4 and verdict UNKNOWN. France/Iraq was priced at 1.75 → band 1.75-2.00 → base-view VETO → SKIPPED_VETO.

This affected any certified pick priced in a band where the rule-specific entry was UNKNOWN (thin) and the base-view entry was VETO (large n). Not just World Cup. Any pick at 1.75-2.00 on the 3way rule was systematically suppressed.

The fix (commit 4c38294)
Two changes in scripts/picks_today.py:

Change 1 — line 450. Scope the odds fallback to the same rule only:

text

before
odds_fallback = _scan_best(odds_ctx, prefix=f"{sport}|{market}|", suffix=f"|{band}")

after
odds_fallback = _scan_best(odds_ctx, prefix=f"{sport}|{market}|{rule}|", suffix=f"|{band}")
The fallback now only considers band entries for the specific certified rule being evaluated. Base views cannot bleed across.

Change 2 — line 513. UNKNOWN odds band routes to CAUTION not WATCHLIST:

text

before
if ctx.get("odds_band") == "UNKNOWN":
return BUCKET_WL_CTX

after
if ctx.get("odds_band") == "UNKNOWN":
return BUCKET_CAUTION
Rationale: when a certified rule fires at an odds price in a band that has no opinion yet (UNKNOWN, not VETO), the certified rule's own walk-forward evidence is sufficient. The pick should be delivered as CAUTION for human review, not silently watchlisted.

Operational bucket logic update
The HANDOVER purity section previously stated:

text

UNKNOWN odds band -> WATCHLIST_UNKNOWN_CTX
This is now corrected to:

text

UNKNOWN odds band -> CAUTION
All other bucket logic is unchanged.

Vitibet status
Vitibet is already a voting consensus source. It is in SOURCES_1X2 and fetch_all() calls vitibet.fetch_day() every run. probs_1x2() correctly handles vitibet's 0-1 probability scale. The vitibet_index field is stored on every 1x2 pick.

Vitibet cannot yet be certified as a standalone consensus gate. vitibet_settled only goes back to 2026-05-01 (5,719 rows). consensus4 has 420 rows total and 31 qualifying at avg_p>=65. The certification gate requires 350 train + 120 valid qualifying rows. Vitibet's probabilities are wiped from its website after settlement so backfill is not possible.

Vitibet will accumulate enough vitibet_settled rows to certify a 4-way rule approximately mid-2027. Monitor passively. Do not force-certify.

consensus4 observed performance this week (2026-06-19 to 2026-06-24): 7/8 wins at avg_p>=65, unanimous 4-way. Strong signal but n=8 is not actionable for certification. Note for the next checkpoint review.

Decay circuit breaker
The 2way+bc-confirms avg_p>=60 rule was auto-benched during this session's pipeline run. Recent 60-day window: 36 picks, 69.4% hit rate, -7.2% ROI. The circuit breaker fired correctly. Do not manually unbench. The next mine_consensus.py run re-evaluates from full walk-forward history.

What to do in one week (next session)
Run the same diagnostic queries against the settled tables for 2026-06-25 to 2026-07-01. Confirm:

Bosnia/Qatar (Jun 24, 21:00) result — check if it would have been profitable under CAUTION
Whether the UNKNOWN odds band CAUTION change is producing good picks in the knockout rounds
Whether the 2way-unanimous avg_p>=70 rule is recovering its ROI as WC draws normalise away
Whether consensus4 is accumulating rows at a healthy rate
Do not touch norm_team() or norm_team_sql(). Do not patch entity_overrides.json for naming mismatches until European leagues resume and the volume justifies it.

Last updated: 2026-06-242026-08-03 addendum — theoddsapi wiring, no-freeze policy, enhancement overlay status

Owner directive (2026-08-03): no code freezes. Changes ship live, but every
change must be appended to this handover with date, rationale, and payload
SHA-256 (manifest: PAYLOAD_MANIFEST_2026-08-03.sha256). Enhancement overlay
logic changes must additionally bump the enhancement market version key
(<market>@v<n>) in any future certification registry so audits certify per
logic version and samples are never contaminated across versions.

New source: theoddsapi (The Odds API, the-odds-api.com) — AUDIT-ONLY odds capture.
Purpose: real-book h2h/totals prices for the frozen daily shortlist, pick-time
and near-close snapshots -> real CLV, and later real-odds certification for the
enhancement overlay. Nothing gates picks on this feed in v1.

Files (see manifest for SHA-256):
    src/edgefactory/sources/theoddsapi.py   adapter, standard contract (fetch_day, COLUMNS),
                                            rows mirror bzzoiro_odds schema (source="theoddsapi",
                                            markets 1x2 / ou_2.5 / btts, selections home/draw/away/over/under/yes-no)
    scripts/capture_theodds.py              CLI: --self-test / --dry-run / --refresh-sports / plain capture
    tests/test_theoddsapi.py                8 offline tests, currently passing
    src/edgefactory/sources/__init__.py     registered theoddsapi
    .env.example (+ .env local)             ODDS_API_KEY + quota knobs

Design / quota discipline (free tier ~500 credits/mo):
    /sports and /events are usage-free; only per-event odds payloads cost
    credits (markets x regions per request: default 2x1 = 2 credits/event).
    fetch_day is shortlist-driven (localdata/picks_<date>.json /
    picks_morning_<date>.json); empty slate -> 0 rows, 0 credits.
    Monthly ledger localdata/theoddsapi_usage.json; hard stop at
    ODDS_API_MONTHLY_BUDGET (default 480); server x-requests-remaining header
    overrides local ledger when present.
    Sport-key cache: localdata/theoddsapi_sports.json (7-day TTL);
    LEAGUE_KEY_ALIASES + containment matching; unmatched leagues are reported,
    never silently mis-priced. Niche slates (e.g. Ie2, Belarus, Armenia) will
    show honest coverage misses — expected, do not force-match.
    Team matching is pair-constrained (home-to-home AND away-to-away), full
    name / 9-char keys / containment / token-subset for affix drops
    (IK Sirius vs Sirius). This matcher is allowed to differ from norm_team();
    certified join keys remain untouched.

Ops commands:
    PYTHONPATH=src python3 scripts/capture_theodds.py --date YYYY-MM-DD --dry-run
    PYTHONPATH=src python3 scripts/capture_theodds.py --date YYYY-MM-DD --snapshot pick_time
    PYTHONPATH=src python3 scripts/capture_theodds.py --date YYYY-MM-DD --snapshot close
    Rows append to localdata/theoddsapi_odds_YYYY-MM.csv.gz (full-row dedupe;
    both snapshots kept — captured_at distinguishes them).

Status: wired and offline-tested (8/8 pytest + --self-test pass; --dry-run
against 2026-08-03 slate: 2 fixtures, ~4 credits/snapshot). Live run pending
ODDS_API_KEY in .env.

Veto attribution: pick["veto_reason"] confirmed present in archived slates
(at least 2026-07-21 onward; 2026-08-03: both SKIPPED_VETO picks are
odds_band context vetoes). Prerequisite for the veto-threshold re-mine is
already accruing — no instrumentation patch needed.

Enhancement overlay status snapshot (audit window 2026-07-05 -> 2026-08-03):
24 recommended / 14 hits (58.3%); away_under_35 5/5, home_under_45 1/1
(market does not offer these; not products), match_over_25 5/9 (EV -14% at
est. 1.55; needs 64.5%), match_over_15 2/5 (EV -48% at est. 1.30; needs
76.9% — structurally weakest), goal_range_2_3 1/4. Expected probabilities
overconfident on goals (team O1.5 promised 87-91% vs realized 77.9%; O2.5
promised 70-80% vs realized 67.6%; BTTS-No undercalled). Overlay remains
advisory/paper for staking until per-market Wilson LB95 >= breakeven at
REAL captured odds (theoddsapi feed) on n>=30 — enforced in the staking
layer, not by gating pick generation.

2026-08-03 live verification — theoddsapi first capture (pick_time snapshot)

First key installed in .env (local only; two spare keys provided by owner,
unused). Live run against the 2026-08-03 frozen slate:
    shortlist=2  matched=1  rows=69  credits=2  server used=2 remaining=498
    Halmstad vs Sirius priced across 21 books (incl. Pinnacle, Betfair,
    Matchbook) for 1x2 + ou_2.5. Pipeline's pick-time price AWAY @1.41 equals
    the market BEST price (Pinnacle/Betfair/Matchbook); market mean 1.366,
    worst 1.26 -> bzzoiro enrichment is sourcing top-of-market prices for
    this fixture. First real CLV-style comparison captured.
    Cork City vs Athlone Town (Ie2): correctly unmatched (not covered).

Patch documented same day: league resolver now rejects containment matches
when the normalized league OR title is < 4 chars (live false positive:
"Ie2" normalized to "ie" and containment-matched soccer_spl via
"...premiership...". It wasted one FREE events call, no credits; fixed
before any repeated cost). Regression test added. Suite 8/8 green.

Updated payload SHA-256 for changed files:
    theoddsapi.py           (league-match guard)
    tests/test_theoddsapi.py (Ie2 regression)
See regenerated PAYLOAD_MANIFEST_2026-08-03.sha256.

Next ops step: schedule --snapshot close ~T-15min before shortlist kickoffs
(only when pick_time rows exist) to complete CLV pairs; wire audit_clv-style
report over theoddsapi_odds_*.csv.gz once ~2 weeks of snapshots accrue.

2026-08-03 addendum 2 — daily.py integration + multi-key rotation

Owner directive: established commands only (daily.py --auto-run / --auto-once);
no standalone capture commands in normal ops. Implemented:

    scripts/daily.py — new helper capture_theodds_snapshot(); hooked at the 4
    existing CLV capture points: official pick_time, official end_of_run,
    autonomous intraday hourly label, and clv_only mode. All run via run_soft
    (failure never blocks the pipeline, per existing convention).

    capture_theodds.py --auto — timing-driven, idempotent across 3h iterations:
    first snapshot once per fixture per day (skipped within 30 min of kickoff),
    close snapshot once per fixture inside ODDS_API_CLOSE_WINDOW_MIN (45) min
    pre-kickoff, attempts ledger localdata/theoddsapi_attempts_<date>.json
    blocks re-tries for 6h after failed attempts (league-not-covered included)
    so niche-league misses can never bleed credits every iteration.

Multi-key rotation (owner provided 3 keys; in .env as ODDS_API_KEYS=k1,k2,k3):
    Daily-rotated ring (start offset = date ordinal % n_keys spreads wear).
    Any key returning 401/403/429 is fingerprint-marked exhausted in
    localdata/theoddsapi_usage.json (raw keys never persisted — sha256[:12]
    fingerprints only) and the ring fails over mid-run. Per-key monthly budget
    480 (ODDS_API_MONTHLY_BUDGET) -> total ring 3 x 480 = 1440 credits/month.
    Server x-requests-remaining (when provided) always overrides local ledger.
    v1 flat ledgers auto-migrate into the first key's slot.
    Ops introspection: scripts/capture_theodds.py --usage (per-key ring status).

Patches caught during live verification (documented same day):
    plan_auto priced-check was raw-name equality -> duplicate capture cost
    2 credits before fix; now uses adapter's cross-feed matcher
    (_team_names_match: exact / 9-char / prefix / token-subset), exported at
    module level. The duplicate snapshot is retained as a second pick-time
    price point (useful for intra-day drift analysis).
    Skip reasons now label retry cooldowns explicitly.

Verification: 10/10 pytest, capture_theodds.py --self-test PASS (incl. ring
rotation + plan_auto checks), live --auto no-op confirmation:
    skip Halmstad|Sirius (priced, close window not open)
    skip Cork City|Athlone Town (retry cooldown, league uncovered)
    -> "nothing due this iteration (0 credits)"

Credit ledger after all live runs today: 4/1440 (2 initial capture + 2
duplicate pre-fix; server-reported remaining=498 on the primary key).

2026-08-03 addendum 3 — WhatsApp re-send loop exorcised, git is now the single source of truth

Owner report (screenshots, 2026-08-02): CSKA Sofia pushed 5x (~3h cadence),
second full morning message at 04:59, Noah 2x. Root cause: dedup state lived
in three drifting places and the pipeline actively destroyed its own memory:

    (a) whatsapp_sent_ledger_* is git-tracked (.gitignore whitelists it), and
        the workflow's 'Restore committed data' step re-runs
        `git checkout HEAD -- <file>` EVERY run -> keys written by runs after
        the last human-chore commit were reverted -> fixture counted unsent
        again -> late-slate alert re-sent every iteration.
    (b) whatsapp_discovery_sent_ledger_* was gitignored entirely -> lived only
        in actions/cache (LRU-evictable) -> resets on cache loss.
    (c) Local machine and Actions each re-picked from divergent state
        (different commit age, cache overlay, .env/secrets parity), so slates
        drifted (1.31 vs 1.32 on the same send day) and 'cloud pick != local
        pick'.

Fixes shipped (no freeze; documented here):
    .github/workflows/daily.yml — `permissions: contents: write` + new final
        step 'Persist pipeline state to git': github-actions[bot] commits
        localdata/ every iteration (if: always()); pull --rebase --autostash
        + retry before push. Git is now THE state. actions/cache remains as
        accelerator only.
    .gitignore — un-ignored whatsapp_discovery_sent_ledger_20*.json and
        theoddsapi state (usage/sports/attempts/odds csv).
    scripts/notify_whatsapp.py — discovery alerts now ALSO suppress fixtures
        already present in the MAIN sent ledger (belt-and-braces even if the
        discovery ledger is ever lost again); new --heartbeat flag sends ONE
        quiet 'no certified picks today, system healthy' ping on empty days
        (marker lives in the sent ledger -> max 1/day; disable with
        EDGE_FACTORY_HEARTBEAT=0). Dedupe keys verified stable against
        rule/odds/prob churn (date|match|market only) across 87 archived
        picks (0 empty match fields).
    scripts/daily.py — official Smart Dispatch call now passes --heartbeat;
        new sync_repo_state() at run_pipeline start: `git pull --rebase
        --autostash` (skipped in CI / when .git absent / EDGE_FACTORY_GIT_SYNC=0).
        Local cadence now starts from the cloud's exact committed state, so
        archive-first logic restores the SAME frozen morning slate instead of
        re-picking a divergent one.

Operator notes:
    Local .env must carry the same secrets as Actions (BZZOIRO_TOKEN above
    all) or enrichment will still produce different prices locally.
    Expect frequent bot commits ('chore: persist pipeline state (run ...)').
    First local run after this change: a plain `git pull` may conflict if
    localdata was edited locally; --autostash handles it, review once.

Owner question 'why don't cloud runs persist / missed days': runners are
ephemeral; previously state survived only per-commit + evictable cache, and
empty-slate days were indistinguishable from dead-system days. With git-state
commits + heartbeat, both are fixed: every run persists, and silence now has
a MAX-1/day 'no picks' explanation attached. Rolling bet tracking remains
fully automatic: picks_audit_<date>.md + picks_audit_rolling.json regenerate
in-pipeline and now also persist to git every run.

Verification: tests/test_notify_whatsapp.py (6 tests: cross-ledger
suppression, heartbeat 1/day, stable dedupe identity) + existing suites =
16 passed, 0 failed. py_compile clean on changed files.

2026-08-03 addendum 4 — 'missed days' resolved: laptop-era gaps, cloud era starts 2026-07-27

Owner clarification: missed days = days away from the laptop, when the daily
cadence could not be run manually. Evidence assembled:

    Gap days (txt report only, NO frozen json archive): 2026-07-10, -07-16,
      -07-17, -07-19, -07-25. Fully empty day (nothing at all): 2026-07-26.
    GitHub Actions history (api.github.com/.../actions/runs): the 3h cron
      service first appears 2026-07-27T12:07Z; every ~3h since, all green,
      zero gaps. Pre-07-27 the laptop was the only scheduler -> away days
      produced txt-only or empty days. Post-07-27 every day has json+txt+audit.

Doctrine decision (walk-forward): missed slates are NEVER backfilled. Minting
    archives retroactively would record post-match information as pre-match
    picks and corrupt all future audits. The gap days above are permanently
    'no official slate' in the machine-auditable record. Settlement/audit
    windows self-heal automatically (audit_recent_picks --days 30 reruns over
    the backlog on every run).

Hands-off posture going forward (all shipped today, 2026-07-27 -> now):
    Scheduler:    GitHub cron 3h, no laptop needed (Secrets, not .env, are
                  the CI source of truth).
    Persistence:  bot commits localdata/ every run -> archives + ledgers +
                  audits cannot be lost or HEAD-reverted again. Side effect:
                  constant commit activity prevents GitHub's idle-repo
                  scheduled-workflow suspension.
    Visibility:   empty-slate heartbeat (max 1/day) distinguishes 'no picks'
                  from 'system dead'.
    Laptop role:  read-only viewer; daily.py sync_repo_state() git-pulls on
                  start. Manual nudge from phone: GitHub app -> Actions ->
                  Run workflow (workflow_dispatch already supported).

2026-08-03 addendum 5 — red-team intake (external review) + applied fixes

Payload zip reviewed adversarially (independent agent, prompt-enforced
evidence rules). Verdict: theoddsapi.py + capture_theodds.py SHIP-WITH-FIXES,
daily.yml + notify_whatsapp.py SHIP. 16/16 falsification targets CONFIRMED
(tests, secret sweep, credit bounds, rotation, suppression, heartbeat,
workflow concurrency sim, e2e --clv-only smoke).

Fixes applied same day:
    1. Year-boundary (BLOCKER-ish): _pick_kickoff_utc used
       datetime.now().year — a Dec-31 run on a Jan-01 slate regressed
       fixtures by a year. Fixed: year is taken from the fixture's own
       pipeline `date`, never wall-clock. Tests: 4 cases incl. Dec→Jan cross.
    2. Quota-ledger race: usage/attempts JSONs were non-atomic and
       read-modify-write was unsynchronized — overlapping 3h cron iterations
       could tear or clobber credit accounting (silent quota leak -> 429s).
       Fixed: POSIX flock (advisory, non-fatal if unobtainable) held across
       the whole load->mutate->save + tmp+os.replace atomic writes for
       usage AND attempts ledgers. Tests: no tmp litter, 45/45 concurrent
       thread charges land, corrupt-ledger recovery.

Reviewer-evidence defects found while validating the report itself (kept for
protocol honesty; neither changes the payload verdict):
    - §2.3 paste cites `.gitignore:17:!localdata/*.json` — that line does not
      exist upstream (checked baseline f91cdb9). The discovery-ledger
      un-ignore comes ONLY from this payload's added line. CONFIRMED verdict
      stands but the cited evidence was fabricated.
    - §4 recompute claims "58% hit, 1.06 ROI" for 2026-08-03 — raw
      picks_audit_rolling.json overall = 58/68 = 85.29% hit, +10.98% ROI.
      Their 58.3% is the ENHANCEMENT OVERLAY's own rate misfiled as the
      overall number; "1.06 ROI" unexplained. Anti-hallucination rules
      require this be on record.

Post-fix verification: 20/20 pytest + --self-test PASS; owner smoke per
review script: --usage 4/1440 -> --auto --dry-run (2 fixtures, est 2
credits, Halmstad->soccer_sweden_allsvenskan, Ie2 UNKNOWN) -> --usage
unchanged (4/1440) -> --refresh-sports 44 active soccer keys (ring live).

Residual accepted risk (documented, not fixed — bounded by the 480/key
hard cap): two overlapping PROCESSES can still double-fetch the same
fixture (attempts stamped after fetch); expected cost <= 2 extra credits
per rare overlap. Attempts stamps are atomic but not cross-process
serialized; revisit only if overlap collisions are ever observed in logs.

Test suite: 20 passing total (14 theoddsapi incl. fail->pass fix tests,
6 notify anti-spam). See PAYLOAD_MANIFEST_2026-08-03.sha256 (regenerated, v2).

--------------------------------------------------------------------------------
ADDENDUM 6 — 2026-08-03: Deployment green-light + v3 payload (self-caught gap)
--------------------------------------------------------------------------------

Decision: owner + external reviewer green-lit v2 for implementation; no second
confirmation round. Question was deploy mechanics, so a full dress rehearsal was
run before any push: fresh clone of upstream -> apply -> verify -> test.

Rehearsal gate #1 (anti-drift): upstream HEAD still f91cdb9d308e4614cafa04d9607e7806efe72d54
    -> v2 diff base is live-valid, zero upstream movement since authoring.

Rehearsal gate #2 (payload self-review) — DEFECT FOUND IN MY OWN v2:
    daily.yml granted contents:write and the persist step, and README told the
    operator to create the ODDS_API_KEYS Actions secret — but the workflow's
    env: block never mapped it. Net effect: every Actions run would soft-no-op
    the capture step (keys never reach env); capture would only ever work from
    the laptop .env. Exactly the cloud/local parity failure class this payload
    exists to kill. The external review also missed it (scope boundary between
    'the four named files' and their Actions interaction).
    Fix: one env mapping + comment in daily.yml env block:
        ODDS_API_KEYS: ${{ secrets.ODDS_API_KEYS }}
    Fail-safe note: with the secret unset, the step still soft-no-ops safely
    (no crash, no spam) — it is inert, not broken.

v3 payload (= v2 + the one-line workflow env mapping + README corrections:
    test counts 10->14 and '16 passed'->'20 passed' in reviewer checklist).
    v2 zip retained on disk as an immutable record; v3 is the apply target.
    Binding hash record: PAYLOAD_MANIFEST_V3_2026-08-03.sha256 inside the v3
    zip (11 repo files incl. this HANDOVER). The zip's own sha256 is reported
    in the operator message thread, not inside the payload (circularity).

Rehearsal gate #3 (clean-room, v3): fresh clone f91cdb9 -> `git apply --check`
    -> apply -> `sha256sum -c` manifest (11/11 OK on the APPLIED tree, proving
    shipped files == diff result) -> pytest 20/20 -> --self-test PASS ->
    py_compile daily.py/notify_whatsapp.py OK -> ODDS_API_KEYS line present
    in applied daily.yml. Results also emitted in operator message.

Post-apply operator duties (unchanged, now actually sufficient):
    1. Create GitHub Actions secret ODDS_API_KEYS (comma list, 3 keys).
    2. Verify next bot commit authored by github-actions[bot] appears.
    3. Tomorrow morning: exactly ONE morning WhatsApp message (or one
       heartbeat if slate empty), zero fixture repeats intraday.
    4. First theoddsapi close snapshot fires at the 15:00 UTC cron tick
       (close window 45 min pre-kickoff) if pushed before 15:00 UTC today.

Local .env on any operator machine: copy 'The Odds API' block from .env.example
(only needed for laptop captures; Actions secret alone is enough hands-off).

--------------------------------------------------------------------------------
ADDENDUM 7 — 2026-08-03 P1 HOTFIX: NameError crash in sync_repo_state (d957ea3)
--------------------------------------------------------------------------------

Incident: owner ran established commands locally 12:27-12:28 SAST (--force-repick,
then plain auto) — both crashed with `NameError: name 'os' is not defined` at
daily.py:148 (sync_repo_state). Every Actions run from 14:15 SAST would have hit
the same crash had the hotfix not landed first.

Root cause (mine, on record): daily.py's original import set
(argparse/json/shlex/subprocess/sys/time/datetime/Path) never included `os`;
sync_repo_state was the first `os` user in the file's history. The v3 gates were
insufficient: py_compile checks SYNTAX only, and the 20-test suite covers
theoddsapi/notify but never executes run_pipeline. The clean-room rehearsal proved
apply + hashes + tests, not EXECUTION of the orchestrator. pyflakes (now a
mandatory gate) flags it instantly: "daily.py:148/150 undefined name 'os'".

Blast radius: crash fires at run_pipeline start, BEFORE any pick writes, notify,
or ledger mutation — zero messages sent, zero state corruption; each affected run
was a silent no-op. Owner's two local crashes were the only production impact
(no manual cloud run had been fired; verified via Actions API).

Fix (this payload, base = d957ea3 NOT f91cdb9):
    1. `import os` added to daily.py header.
    2. sync_repo_state body wrapped in try/except Exception — a sync convenience
       must never again be able to kill the pipeline (class fix, not point fix).

Process fix (mandatory gates for every future payload):
    - pyflakes undefined-name scan on all touched python files.
    - RUNTIME call-test: import the orchestrator module and directly invoke every
      newly added function under its env-guard configurations (off / CI / live).
    - Rehearsal must prove execution, not just application.

Verification (fresh clone d957ea3 + hotfix applied): import daily.py via importlib;
sync_repo_state() passes under EDGE_FACTORY_GIT_SYNC=0, GITHUB_ACTIONS=true, and
live .git (real git pull --rebase --autostash vs origin — clean no-op);
capture_theodds_snapshot() no-key path soft-no-ops; pytest 20/20; pyflakes clean;
manifest 2/2 OK on the APPLIED tree. Files: scripts/daily.py + this HANDOVER.

Deferred (cosmetic, next non-hotfix payload): theoddsapi.py:444 f-string without
placeholder (pyflakes note, no behaviour impact).

Postscript (same day): upstream advanced to dbfc64a (owner commit "update
picks_today.json with fresh match data and refreshed odds"; parent d957ea3; touches
README.md +1/-1 and localdata/picks_today.json only — unrelated to this fix). Hotfix
diff regenerated against dbfc64a and re-rehearsed end-to-end on a fresh clone:
apply OK, manifest 2/2 OK, scoped pytest 20/20, runtime call-test all four paths
PASS (incl. real git pull --rebase --autostash — the exact crashing call).
Two hygiene facts on record: (1) v3 payload artifacts PATCHES_V3_2026-08-03.diff,
PAYLOAD_MANIFEST_V3_2026-08-03.sha256, README_APPLY.md were accidentally committed
at repo ROOT in d957ea3 (zip was unzipped into the repo before `git add -A`) — no
secrets (leak sweep clean); removal folded into the hotfix apply instructions;
payloads must always be extracted to /tmp, never into the repo. (2) Full-swipe
`pytest tests/` hits PRE-EXISTING upstream tests/test_supabase.py which imports
supabase.create_client — environment-dependent, predates this project phase;
the gate remains the two scoped suites until that suite is containerised.

--------------------------------------------------------------------------------
ADDENDUM 8 — 2026-08-03: Enhancement real-odds package (pricing join, registry,
presentation gate, kickoff guard)
--------------------------------------------------------------------------------

Trigger (owner question 2026-08-03 ~13:50 SAST): "are the enhancements getting the
odds data you mentioned? are we being presented with the right enhancements?"
Code-verified answers then: NO (compute_dynamic_enhancement returns no odds field at
all; audit scored hit/miss with zero prices) and MOSTLY NO (probability-only ranking
surfaced trivially-priced team unders; 5-6 unpriced 'Possible Events' rendered on
VETO-skipped picks with no shadow framing; the one real-priceable product,
match_over_25, was presented unpriced).

This package (base: live HEAD at package time):
    NEW src/edgefactory/enh_pricing.py — MARKET_PRICE_MAP pilot (match_over/under_25
        -> ou_2.5 totals feed; team totals, 1.5-line, goal-range deliberately
        unmapped=unpriceable). load_prices_index reads theoddsapi monthly odds file,
        keeps BEST price per (market,selection); attach_enhancement_price writes
        price/book/at/breakeven/sample-edge onto the archived pick, pair-constrained
        (both teams must match, either orientation), stale prices actively cleared
        for unmapped markets, fail-soft everywhere.
    NEW src/edgefactory/enh_registry.py — certification state machine
        SHADOW->PAPER->ELIGIBLE->BENCHED per "<market>@v1". ELIGIBLE requires
        n>=30 PRICED outcomes AND WilsonLB95 hit-rate >= mean breakeven of prices
        actually paid. BENCHED = rolling 60d ROI<0 on n>=20 (circuit breaker,
        mirrors decay monitor). Unpriced outcomes never advance certification —
        "probability without price is not evidence of value". Idempotent per
        date|match|market key; 400-record ring + 1600-key dedupe ring.
    MOD scripts/picks_today.py — builds prices index per day, attaches price +
        enhancement_state to every pick; renderer gate: SKIPPED_VETO picks get
        '[SHADOW — paper]' tag on Possible Events; recommended line renders as
        '⭐ (ELIGIBLE) with real price + breakeven/sample-edge' ONLY when the
        registry says so, else '🔬 (state) [paper-only — not for staking]'.
    MOD scripts/audit_recent_picks.py — priced settled outcomes accumulate
        (priced_n/hits/roi per type in the rolling report) and feed the registry
        (idempotent, fail-soft); report gains 'enhancement_registry' state snapshot.
    MOD scripts/capture_theodds.py — kickoff-divergence guard: when captured API
        commence_time disagrees with the listing by >15 min, plan close window from
        the EARLIER time and emit 'WARN kickoff-mismatch' (Halmstad today: listing
        18:00 vs API 17:00Z/19:00 SAST — source listing carried UK time).
    MOD .gitignore — un-ignore localdata/enhancement_registry.json (rides git state
        loop). Sidecar .lock file stays ignored by design (machine-local).
    NEW tests x3 (19 tests): pricing join 6, registry state machine 10 (incl.
        concurrency + corruption recovery), kickoff guard 3.

Hard-won lesson re-flocked (05th lesson of the day, test-proven): POSIX flock must
sit on a STABLE sidecar lockfile, never on a file that is os.replace'd. flock is
per-inode; replacing the data file swaps the inode out from under blocked
contenders -> two 'exclusive' holders, lost updates. First implementation of this
package measured the loss: only 8-15/40 concurrent records survived. After moving
the lock to enhancement_registry.lock (same pattern as the quota-ledger's
USAGE_LOCK_FILE): 40/40, five consecutive runs. Re-validates the quota-ledger design.

Gate evidence (all in operator thread + reproducible):
    pyflakes: zero findings on all touched/new files. picks_today.py /
        audit_recent_picks.py findings (incl. 'undefined name w_score' at
        picks_today.py:1875) verified PRE-EXISTING on pristine baseline dbfc64a —
        upstream dead-branch landmines recorded here, deliberately untouched
        (pipeline exercised normally today; dedicated ticket, not this payload).
    pytest: 39/39 (14 theoddsapi + 6 notify + 6 pricing + 10 registry + 3 kickoff).
    capture --self-test: PASS.
    Concurrency: 40/40 five consecutive runs (was 8-15/40 pre-fix).
    Runtime call-tests: sync_repo_state hotfix regression PASS; pricing join vs the
        REAL captured CSV (Halmstad over 2.5 -> 1.49 Betsson, breakeven 67.11%,
        sample-edge +5.64% — the module's first real number); unmapped stale-price
        clearing PASS; registry record->PAPER PASS; first-deploy status SHADOW PASS;
        capture module import PASS (KICKOFF_MISMATCH_MIN=15).

Deferred (recorded, not in scope):
    - Veto re-mine (per-trigger counterfactual on SKIPPED_VETO, walk-forward
      split=2025-06-01, n>=350 train) — analysis phase 2, informed by real odds now
      accruing; entity_overrides proposals (Lithuania 1 Lyga, Sweden Allsvenskan)
      wait for it.
    - Alternate totals lines / team_totals capture: audit The Odds API free-tier
      availability + credit cost before extending MARKET_PRICE_MAP.
    - Calibration: enhancement_probability is a blended realized frequency
      (40% league / 60% team). The ELIGIBLE gate uses WilsonLB95-vs-prices-paid as
      the statistical buffer; true calibration shrinkage is a later model task.
    - Pre-existing upstream pyflakes findings (see above), incl. w_score landmine.
    - Cosmetic: theoddsapi credits_month display mixes server-union and local-sum
      views on different lines.

---

## Addendum 9 — 2026-08-03 (post-package RED TEAM → payload v2 supersedes v1)

Context: owner instruction — "provide the zip, make sure you red team engineer it
first, and antigravity to do the same." Full adversarial review of the addendum-8
enhancement payload BEFORE release, executed on a fresh clone of live HEAD
`681a73ae` (drift re-verified: the intermediate state commit touched only
localdata/; `git apply --check` CLEAN; post-apply `git status` = exactly the 10
payload paths). Result: 1 CRITICAL feature-defeating defect + 5 real findings +
2 hygiene items, ALL fixed in-tree before re-release. v1 zip
(sha `201c854f…8b86`) is SUPERSEDED by the v2 zip (sha in operator thread and
README_APPLY_ENH.md; manifest re-issued). Antigravity gets an independent
RED-TEAM PHASE (README §Phase 0) to re-derive every check before applying.

Findings and fixes (reproducers shipped: tests + RED_TEAM_BATTERY outputs on record):
- RT-0 — gate escape (own-goal, recorded for honesty): pyflakes 3.4 flags
  `'typing.Any' imported but unused` in MY enh_registry.py:37 — addendum-8's
  "pyflakes zero findings" did not hold under a fresh toolchain. Lesson pinned:
  gates must record tool versions. Fixed (import dropped).
- RT-1 — CRITICAL, feature-defeating: the registry would have STARVED. The audit
  deliberately prefers the locked morning snapshot (archived_picks_path:
  "immutable morning snapshot… state drift"); morning freezes happen BEFORE the
  first theoddsapi snapshot, and the intraday ledger merge retains locked picks
  verbatim (autonomous_intraday_merge: "retains all existing locked picks
  exactly"). Archived `enhancement_price` fields can therefore never carry the
  close price — scoring off them (v1 design) = silent pricing vacuum for the
  certification engine. Fix (keeps both anti-drift doctrines untouched): the
  audit now derives prices by probing the IMMUTABLE capture store
  (per-day `load_prices_index` + `attach_enhancement_price` on a throwaway probe
  dict). One consistent definition everywhere: best captured theoddsapi price
  for (date, pair, market). Zero network, zero credits.
- RT-2 — non-decimal poison: float("nan") / float("inf") parse out of CSV rows and
  slip naive guards (`nan <= 1.0` is False; `inf` passes `> 1.0` and would zero the
  breakeven / produce +inf sample-edge, and poison registry profit sums).
  math.isfinite now gates all three boundaries: pricing loader, registry
  record_outcome, renderer normalization. Probes: 7/7 hostile rows rejected.
- RT-3 — stale-price survival: setdefault-based init preserved archived
  price/breakeven/edge through early-return branches (missing index, missing
  selection). Fields are now RESET unconditionally at attach entry; re-derivation
  is provably idempotent.
- RT-4 — registry corruption silently wiped history (fresh dict on parse error).
  Now quarantined to `enhancement_registry.corrupt-<epoch>.json` (git-ignored,
  verified) before rebuild — recoverable + auditable.
- RT-5 — doc/behavior mismatch: header promised BENCHED re-entry "on fresh
  evidence"; no such code path existed. Docs pinned to actual semantics: NO
  automatic re-entry; an explicit operator reset after re-validation only.
- RT-6 — renderer crash path: `f"{None:.1%}"` on a legacy/archived None
  probability = TypeError mid-render (production crash class from the P1 lesson).
  Probability coerced under try/except; NaN/inf prices normalized to unpriced
  before formatting. Live probe: SKIPPED_VETO pick with None-prob + NaN-price
  renders "[SHADOW — paper] … (unpriced) [paper-only — not for staking]".
- Hygiene: capture_theodds.py pre-existing unused `timedelta` import removed
  (file already in the payload; verified pre-existing on pristine 681a73ae; keeps
  the G3 "zero findings" promise literally true).

Accepted + recorded limitations (NOT defects, stated for future reviewers):
- Time-bomb test: test_benched_circuit_breaker bakes outcome dates 2026-08-03
  against wall-clock BENCH_WINDOW_DAYS=60; refresh or inject the clock before
  ~2026-10-02 (test-only, LOW).
- norm_team 9-char truncation cannot mis-price: pair-constrained matching needs
  BOTH teams to collide inside one same-day file, and a team plays once per day;
  the matcher fallback is either-orientation + prefix/token strict.
- Audit `priced_*` report fields now mean "best captured theoddsapi price"
  (capture-store definition), not the archived presentation-time field. Intentional.

Evidence (commands + raw outputs in operator thread; re-derivable):
- Drift: apply --check CLEAN on live `681a73ae`; post-apply = exactly 10 paths.
- pyflakes 3.4.0: 0 findings on enh_pricing/enh_registry/capture_theodds;
  picks_today + audit findings verified IDENTICAL SET (line-shifted only) vs
  pristine `681a73ae` baseline (incl. w_score picks_today.py:1875→1877; upstream
  landmines still deliberately untouched).
- pytest: 44/44 (14 theoddsapi + 6 notify + 9 pricing + 12 registry + 3 kickoff).
- capture --self-test: PASS. Concurrency: 40/40 five consecutive runs.
- Live-CSV join: Halmstad match_over_25 → 1.49 Betsson, breakeven 0.6711,
  sample-edge +0.0564 (module output vs the real tracked capture file).
- git physics: `git status` shows enhancement_registry.json untracked-addable;
  `git add -n` REFUSES .lock / .tmp / .corrupt-* ("ignored by one of your
  .gitignore files").
- Scope: 10 repo files, +936/−7; no veto/selection/staking logic touched; zero
  network in new modules; zero API credits (all reads are local gz/json).
- Secret sweep: CLEAN across payload files; full zip re-swept after rebuild.

Deferred (carried from addendum 8, plus new items — none in this payload's scope):
    - Veto re-mine counterfactual (feeds entity_overrides reviews) — phase 2.
    - Alternate-lines/team-totals capture audit (costed, probe said unavailable/
      redundant for team totals; alternate totals redundant vs scoutingstats).
    - Calibration shrinkage for enhancement_probability — later model task.
    - Time-bomb test clock injection (before ~2026-10-02); BENCHED operator
      reset runbook; pre-existing upstream pyflakes landmines (incl. w_score);
      credits_month display wording.

## Addendum 10 — 2026-08-03 (deployment verification of 0cdbde9/9c87c05 + evidence audit)
Independent post-ship verification of the enhancement payload deployment
(Antigravity verdict "SHIP, commit 0cdbde9"), run against live main. Verdict on
the verdict: deployment CORRECT and OPERATIONAL, with one process breach
ratified post-hoc and two evidence anomalies struck pending output.

Deployment integrity (sha-verified against payload manifest):

9/10 files BYTE-IDENTICAL to the v2 manifest on live main (audit_three scripts,
both modules, all tests, .gitignore, HANDOVER with addenda 1–9).
scripts/picks_today.py differs by EXACTLY one token at line 1877:
"w_score": round(w_score, 4) → round(z, 4).
w_score → z (independent review): the pick-stamp sits in the ML-meta branch where
z = Σ coefs·x + intercept is computed ~15 lines above (L1860) and is always
bound; NameError was real but latent (branch not exercised by any 2026-08-03 run).
z is the correct semantic: the meta-model logit, monotone with ml_p
(sigmoid), used only for display (w=) and merge sort — monotonicity preserved.
Fix is CORRECT and eliminates a second P1-class NameError. PROCESS BREACH,
however: the finding was fenced "deliberately untouched" (README G3, addenda 8–9);
an out-of-scope change shipped without pre-announcement, breaking manifest
identity on one file. Ratified post-hoc with conditions (below). The G3 baseline
finding list is updated: undefined name 'w_score' at picks_today.py:1877 is
stricken from the pre-existing-upstream set.

9c87c05 classified BENEFICIAL-NEUTRAL: manual commit of a G7 forecast re-render
(15:39Z). Content: picks_today.json 6→3 entries — Transinvest 2 (KO 16:00,
started: guard), Hammarby Talang + FCSB fell out of the refreshed candidate
scan (pre-existing intraday churn class, NOT payload-induced — payload touches
no generation logic). Locked-archive integrity PROVEN: dated
picks_2026-08-03.json retains all 6 incl. dispatched CAUTION FCSB @1.81
(KO 19:30) — settlement trail intact. Render side-effects confirm the new code
operates live (entries gained the +7 enhancement fields; odds refreshed
1.41→1.42). Process note: forecast-state files should ride the bot persist loop,
not manual commits — benign here, stop doing it.

Evidence anomalies in the verdict table (doctrine: gates without output = not run):

G4 "edge_sample=+0.2173" — the specified probe (prob 0.709 @1.49) gives
+0.0564. If +0.2173 came from a live-render probability (~0.817), paste the
render line; until then the number is an annotation, not evidence.
"73.6% hit rate (n=428) >> breakeven" — UNSOURCED (my settled sample: 5/9,
est. EV −14% @1.55 in ENHANCEMENT_REVIEW_2026-08-03.md). STRUCK. Certification
starts at n=0 by design: real prices exist only from 2026-08-03 onward; any
historical hit-rate claim needs command + raw output or stays out of the record.
Ratified-with-conditions going forward:

Out-of-scope fixes inside a gated payload: announce + get operator sign-off
BEFORE commit; if truly blocking, land as a SEPARATE commit with its own
justification so manifest identity on payload files is preserved.
Expected near-term signals (corrected post-run): today's archived slate carries
only UNMAPPED enhancement types (goal_range_2_3 ×4, btts_yes ×2 vs the pilot
map match_over/under_25), so zero priced outcomes are fed by tomorrow's audit
BY DESIGN — registry stays absent/SHADOW until the first settled pick with a
MAPPED recommended type (FCSB settles via dated archive 19:30 KO; its enh type
is goal_range_2_3 → unfeedable). First PAPER-record milestone redefined: first
settled pick whose archived recommended_enhancement is in MARKET_PRICE_MAP.
My earlier "must show match_over_25 priced_n ≥ 1" was probe-assumption-based,
not artifact-based — corrected here (a8c3d45 blob verifies the locked type was
goal_range_2_3 @ 47.0% all day). FCSB/Halmstad's 1.49 capture rows remain in
the store but have no mapped type to attach to.
Close-snapshot note: cron had no tick inside the guard-planned close window
(15:15–16:00Z, planned from the earlier listing kickoff exactly as designed —
the WARN fired live twice in the 15:43 force-repick run); the production odd
path is conservative + zero-credit by construction, and the first-snapshot rows
(69, over best 1.49) remain the day's pricing of record.

---

## Addendum 11 — 2026-08-03 (EXT payload: multi-source enhancement pricing, "money on the table")

Context: owner GO after the deployed gate showed 2/6 of today's slate carrying
btts_yes recommendations with zero price feed (goal_range ×4 additionally
unpriceable by design). Main payload priced only the theoddsapi pilot window
(match o/u 2.5); the same-day feeds already captured FREE lines the pilot never
used. This payload extends the pricing join — and nothing else.

Design (single-module diff by construction):
- enh_pricing now merges THREE local sources into one index, all file-only
  (zero network, zero credits): theoddsapi (unified rows, strict source filter),
  bzzoiro_odds (unified rows; rows store source="bzzoiro" — attribution tagged by
  FILE, verified collector line 143), scoutingstats (wide per-fixture rows;
  column map verified against sources/scoutingstats.py COLUMNS: odd_o15/u15 →
  ou_1.5, odd_o25/u25 → ou_2.5, odd_o35/u35 → ou_3.5, odd_gg/ng → btts yes/no).
- MARKET_PRICE_MAP v2 (8 priced types): match_over/under_15, match_over/under_25,
  match_over/under_35, btts_yes, btts_no. Deliberately unpriceable list now
  recorded WITH reasons: match_over_45 (ladder stops at 3.5), goal_range_*
  (banded, no feed), team totals (2026-08-03 probe: 0 bookmakers), double_chance
  (only 1x2 legs captured — NO synthetic prices; doctrine).
- Merge semantics: best price ACROSS sources wins with source attribution on the
  winning price (pipeline best-price convention); when ≥2 sources priced the same
  selection and relative spread > 10%, enhancement_price_divergence records every
  source's best price + spread_pct (surfaced, never silently averaged).
- Per-source day scoping; isfinite/junk guards at every boundary (RT-2 pattern
  extended to all three loaders); full derived-field reset at attach entry
  incl. the divergence record (RT-3 pattern extended).
- Index gains a "spread" bucket beside pairs/names — attach() is the only
  consumer; the audit's pricing probe and the picks renderer upgrade with ZERO
  call-site changes (shared loader). No registry/capture/veto/picks/audit diffs.

Evidence (commands + raw outputs in operator thread; re-derivable):
- pyflakes 3.4.0: CLEAN on enh_pricing + tests. pytest: 52/52 (44 prior + 8 EXT:
  ss ladder/BTTS mapping, bzz unified+book, best-across-sources attribution,
  >10% divergence flag + content, per-source day scoping, swapped orientation,
  hostile rows at every source, unmapped-stays-unpriced).
- capture --self-test: PASS (untouched path guard). Red-team battery v3: ALL
  PASS (12 sections incl. E1–E5 EXT probes; divergence record
  {theoddsapi 1.49, scoutingstats 1.70, spread_pct 0.1409}).
- Live regression on the real tracked theoddsapi CSV: Halmstad match_over_25 →
  1.49 Betsson, source=theoddsapi, breakeven 0.6711, sample-edge +0.0564 —
  byte-identical behavior to v2 on existing data.
- Known asymmetry (recorded): bzzoiro_odds/scoutingstats monthly files do not
  ride git (only theoddsapi/betexplorer are negated in .gitignore), so author-side
  verification used schema-verified fixtures; REAL-file values are verified in
  operator-side gates G4/G7 (README prints actual attached prices from the Mac
  files — bzz 2026-08 ≈2.5k rows, ss 2026-08 ≈0.5k rows exist on disk).

Expected signals once live: any settled pick carrying a mapped type beyond the
pilot (e.g. btts_yes, match_over_15) now feeds the registry with a source-tagged
price; today's Hammarby/Celtic btts_yes class is the immediate beneficiary.
Divergence records (source-vs-source >10%) begin accumulating in archived picks
for the later CLV/calibration work.

Deferred (recorded, not this payload): team totals (probe-empty), double_chance
synthetic pricing (doctrine says no), banded markets, source coverage analytics
(which slates ss/bzz actually cover day to day), certification of the newly
mapped types (accumulates from priced settlements going forward).

---

## Addendum 12 — 2026-08-03 (evening): Full-Surface Audit + two measurement fixes (FIX-1 / FIX-2)

**What shipped.** `scripts/audit_recent_picks.py` extension: the rolling audit
now scores EVERY machine-readable forecast the pipeline publishes — not just
the single recommended enhancement:

1. `## Possible Events (🔥) Full-Surface Audit` — every `event_notes` entry
   on every settled pick (market + promised %), scored against the final
   score: per-market hit table (notes, n, hits, realized, promised avg, Δ,
   Brier, low-n flags), pooled promised-vs-realized decile buckets (the
   calibration curve), and an unscorable-market inventory (coverage
   analytics). It reads the SAME immutable morning-snapshot source as the
   rest of the audit; anti-drift preserved (H6 battery check).
2. `## Statistical Line (📊) Calibration` — every promised metric in the
   archived `statistical_comment` (Over 2.5 / BTTS / Home|Away Over 1.5 /
   Top Scores), scored as probabilistic forecasts (calibration, never a
   direction call): per-metric table, pooled buckets, plus a NEW `Avg Goals`
   point-forecast audit (MAE / bias). The parser now returns `avg_goals`.
3. Machine consumers: the rolling report JSON gains stable keys
   `event_notes_audit` {definition, total_notes, scored, promised_missing,
   unscorable, by_market, promised_buckets} and `statline_calibration`
   {definition, by_metric, promised_buckets, avg_goals} — shaped so a later
   payload can extend `load_rolling_audit_hit_rates()` (picks_today.py) into
   a full-surface debias loop.

**Doctrine guardrails (hard requirements, kept).** Both sections carry the
header "Calibration ≠ edge": none of these numbers carries a price, so they
are NOT evidence of value and must not drive staking; certification remains
the enhancement registry's job. No synthetic prices anywhere; the registry
feed path is unchanged.

**FIX-1 (displayed-truth bug, pre-existing).** The Granular Expectations
ledger's BTTS HIT/MISS icons: parsed fractions are 0..1 but the expectation
cut was `>= 50.0` (never True) — every BTTS expectation was silently scored
as BTTS-No, inverting icons for all BTTS-Yes expectations. Now `>= 0.50`,
consistent with the renderer and with the home/away-o15 logic. Regression-
pinned by the integration test (81.5%-Yes and 22%-No discriminators).

**FIX-2 (measurement bug, pre-existing; caught by a RED upstream test).**
`check_enhancement_hit` scored `match_over_15`, `match_over_25`, `btts_yes`
as *Win + line* combos for home/away selections, while the promised % and
(post-EXT) the captured price for these markets are both PLAIN-market. The
mismatch would have deflated every hit-rate derived from the audit —
including the certification registry feeds that begin with the first settled
mapped-market picks (the 2026-08-03 btts_yes slate) — making certification
under plain-market breakevens unwinnable. Scoring is now selection-
independent plain-market; the repo's own
`tests/test_audit_recent_picks.py::test_check_enhancement_hit` (red since
before this payload — it encoded plain semantics) passes again. Selection
still drives `team_*` totals and `double_chance` legs. The cosmetic
"Win + …" labels in picks_today.py are labels-only: probability, price and
scoring are plain-market; label cleanup is queued for the hardening pass,
informed by the new audit's per-market numbers.

**Process lesson (gate hardening).** FIX-2 survived two payloads because an
earlier gate ran a SUBSET of the suite ("52 passed" did not include
test_audit_recent_picks.py). From this payload onward every gate must run
the FULL suite (`PYTHONPATH=src python3 -m pytest tests/ -q`) and paste the
tail; a red test — even pre-existing — blocks the ship until triaged.

**Evidence (sandbox, reproducible).** Full suite: baseline 84 collected
(83 pass / 1 pre-existing red = the test above) → 93/93 post-patch;
pyflakes unchanged (single pre-existing f-string finding, :926→:1320, zero
new); RED_TEAM_BATTERY v4 23/23 — NaN/Inf/junk promised, malformed and
truncated comments, corrupt archive files, morning-file precedence,
same-day exclusion policy, determinism, hermetic no-write (no registry file
created), bucket-edge boundaries, 20,000 notes scored in 0.78s. Battery
ships inside the payload zip; sha-256 manifest in the payload README.

**Files.** `scripts/audit_recent_picks.py` (+~430 lines: scorers,
aggregators, renderers, report keys, FIX-1/FIX-2), `tests/`
`test_audit_recent_picks.py` (+9 tests).

**Deferred (recorded, not this payload):** cosmetic "Win + …" label cleanup
in the renderer; wiring `event_notes_audit` into
`load_rolling_audit_hit_rates()` (debias over the FULL note surface, not
only recommends); veto re-mine for the UNKNOWN-league population (next
payload — run it once a few days of full-surface numbers exist so the
hardening decisions are evidence-led, e.g. any market whose realized ≪
promised at n≥5 is a pricing-source or semantics candidate, not a staking
candidate).

---

## Addendum 13 — 2026-08-03 (night): per-pick graded 🔥 rendering in the granular ledger

The Addendum-12 full-surface audit graded the 🔥 Possible Events surface only
at aggregate level (per-market table + pooled buckets). The per-pick Granular
Expectations blocks graded the 📊 line but left each pick's 🔥 list invisible
to the operator. This append closes that visual gap: every settled pick's
granular block now ends with

    - **🔥 Possible Events (graded)**: [🟢 HIT] <label> (promised%), …

rendered from the SAME observations that feed the aggregate table (notes are
scored once per pick and shared by both layers — one definition, no
divergence). Notes without an outcome definition render `[⚪ n/a]`; picks
without archived notes render an explicit "none recorded on the archived
pick" line (no silent absence). Scoring is unchanged (plain-market, FIX-2).
cosmetic "Win + …" labels render verbatim from the archive (they are what the
operator saw). Tests: integration + markdown asserts extended, note-less pick
fixture added; 93/93 full suite, pyflakes delta-0 (the single pre-existing
f-string finding only shifted lines). Battery v4 re-run: 23/23.

---

## Addendum 14 — 2026-08-03 (night): graded 🔥 layout — one event per line (📊 parity)

Operator feedback on Addendum 13: the per-pick graded 🔥 line rendered every
event comma-joined on one run-on line (up to ~13 items) — hard to read unlike
the per-line 📊 display above it. The render now mirrors the 📊 layout
exactly: one line per event under a "**🔥 Possible Events (graded)**:" header,

    - [🟢 HIT] **<archive label verbatim>**: expected 47.0% (Actual: 4 goals)

with realized context from `_event_actual_context()` (total goals for match
totals/ranges/exacts; named side + goals for team totals; BTTS-Yes/No;
realized outcome for double_chance) and `[⚪ n/a] … (no scoring definition)`
for unscorable markets. Content unchanged — same shared observations as the
aggregate tables; presentation only. Tests: markdown asserts updated to the
per-line format + new `_event_actual_context` unit test (94/94 full suite,
pyflakes delta-0 — pre-existing f-string finding renumbered only, battery
23/23).

---

## Addendum 15 — 2026-08-03 (late night): collision-safe git workflow in README + reconciliation record

Third localdata state-sweep collision. At 19:08 SAST a VS Code "Commit All"
swept localdata into local commit 09acdeec (which carried the payload-#3
code) three minutes after the bot's persist commit 97b1335 landed on
origin → pull failed with the divergent-branches fatal. Resolution (now the
README runbook): `git config pull.rebase false` once;
`git pull --no-rebase -X ours`; push. Merge 65d062c published with correct
parents (09acdeec + 97b1335); post-merge independent verification:
audit_recent_picks.py 4c194a76… and its tests d1e23e2b… byte-identical to
the payload-#3 manifest, full suite 97 passed, 9 graded 🔥 blocks in the
audit report.

Post-merge verification ALSO caught a silent partial apply: payload #3's
HANDOVER hunk (Addendum 14) never landed on the Mac — upstream HANDOVER.md
sat at the payload-#2 sha 0274aea4 while the two code files matched the
payload-#3 manifest. This payload restores Addendum 14 (verified: it was
the ONLY delta) and adds this addendum. Rule hardened: payloads now carry
FULL file copies alongside PATCHES.diff, and placement is sha256-verified
against SHA256MANIFEST.txt — "applied" without a matching sha is not
applied.

README.md gains a "Git workflow (collision-safe)" section: localdata/ is
owned exclusively by the Actions persist loop; humans/agents commit
explicit paths only; never `git add -A` / `git add .` / VS Code Commit All;
pull.rebase=false one-time setup; divergent branches →
`git pull --no-rebase -X ours` (merge, never erase). Docs-only payload: no
code changes; full suite re-run as the ship gate (97 passed expected).

---

## Addendum 16 — 2026-08-03 (late night): label honesty — "Team Win + …" wording retired

Operator-reported live specimen (picks_audit_2026-08-03.md): Kongsvinger vs
Strommen settled 1-3 — the HOME pick LOST, yet the graded 🔥 block showed
[🟢 HIT] Home Win + Over 1.5 (86.8%), [🟢 HIT] Home Win + Over 2.5 (68.1%),
[🟢 HIT] Home Win + BTTS (Yes) (64.1%). A HIT on a win that never happened
is a contradiction in any reader's eyes and poisons trust in the graded
view. Root cause known since FIX-2 (Addendum 12): promised %, captured
price and scoring for match_over_15 / match_over_25 / btts_yes are
PLAIN-market (selection-independent); only the archived pick-time wording
still claimed a "Win + …" combo. The audit even printed a disclaimer
admitting it. Operator's report promotes the queued cosmetic cleanup to
shipped.

Two-sided fix:
- picks_today.py (source): the candidate label templates now write plain
  canonical labels — "Match Over 1.5 Goals", "Match Over 2.5 Goals",
  "Both Teams to Score - Yes (BTTS-Yes)" — so future archives stop lying at
  birth. team_str removed (dead after the change; pyflakes-clean).
  Fallback-odds comments reworded to plain-market wording (VALUES
  untouched: 1.30 / 1.55 / 2.50 — no behavior change anywhere).
- audit_recent_picks.py (render): new PLAIN_LABELS map + _display_label() —
  the graded per-line render normalizes those three markets to the
  canonical plain label whatever the archive says. Old archives inside the
  30-day window keep "Win + …" in their STORED label field: storage stays
  faithful to the archive, display is honest about what was scored. The
  per-market table's footer note now documents the mapping instead of
  apologizing for the cosmetics.

Scores, promised %, prices, HIT/MISS icons and Actual contexts are
UNCHANGED — normalization is display + future-archive wording only.

Evidence: fixture labels made production-realistic ("Home Win + Over 2.5",
"Away Win + Over 2.5", "Home Win + BTTS (Yes)") so the markdown test is an
end-to-end Kongsvinger regression pin — canonical labels rendered,
"Home Win + "/"Away Win + " asserted ABSENT from the whole report;
storage assert proves the archived wording is preserved verbatim; new
_display_label unit test (home/away variants, already-plain passthrough,
verbatim non-combo, None/junk safety). Suite 95/95 sandbox
(--ignore=test_supabase; 98 expected on the Mac), pyflakes DELTA-0 vs
pinned base on both touched scripts (audit: the single pre-existing
f-string finding renumbered :1345→:1376; picks_today: identical 8
pre-existing findings ±1 line). Deploy proof: re-rendered Kongsvinger block
read "Match Over 1.5 Goals" / "Match Over 2.5 Goals" /
"Both Teams to Score - Yes (BTTS-Yes)" with the SAME icons and expected % —
gate G4 confirmed on the operator paste; deployed as 993f10e and upstream
sha-verified against the manifest (4/4 files).

---

## Addendum 17 — 2026-08-03 (late night): hybrid empirical-cohort probability engine

The full-surface audit (Addendum 12) measured the split: the blended/Poisson
🔥 engine was the miscalibrated surface (btts_yes -11.3pp, home_under_35
-27.6pp, exact_3 -22.3pp, avg-goals bias -0.41/game) while the empirical 📊
cohort surface stayed within ±7.7pp. This addendum re-sources the broad 🔥
markets (and the Poisson lambda anchor) from that same kind of evidence:
the realized frequencies of the outcome-UNCONDITIONED "matches like this
one" cohort — all-sources-unanimous pick + avg_p ±5 band, settled results
joined (fetch_match_cohort()). Same consensus view and band logic as the 📊
line, MINUS its c.outcome = selection filter: conditioning on the pick
winning is fine for a display anecdote, fatal for a probability engine — it
injects exactly the selection bias the engine exists to avoid. The 📊 line
itself is untouched.

Mechanics (picks_today.compute_dynamic_enhancement):
- Broad markets (match O/U 1.5/2.5/3.5/4.5, BTTS-Yes/No, home/away
  O0.5–O3.5; unders via complements) shrink toward the cohort rate,
  empirical Bayes: p = (n·p_cohort + K·p_model)/(n+K), K=150. Cohorts
  thinner than HYBRID_MIN_N=100 keep the pure model prior — legacy behavior
  is 100% intact where no deep cohort exists.
- The Poisson lambda anchor re-sources the same way (shrunk cohort
  avg_goals), so exacts / goal ranges move with realized goal volume (the
  -0.41/game over-promise bites here).
- Every over/under pair is re-derived as an EXACT complement post-override
  (match_under_35 previously used its own blend vs the Poisson over — the
  pair is now coherent whenever the cohort is on).
- Every note carries engine="hybrid_cohort"|"model" + cohort_n provenance.
  DISPLAY/CONTEXT LAYER ONLY: registry, pricing and certification paths
  are untouched.

Measurement: the audit aggregates and renders a by-engine table
(### By probability engine (🔥)) — model / hybrid_cohort / legacy graded on
their own promises in the same window. First hybrid notes settle tomorrow;
the window migrates from legacy to hybrid_cohort across the 30-day roll.

Evidence: new tests/test_hybrid_engine.py pins the cohort SQL over a fixture
deliberately LACKING an outcome column (an accidental outcome condition
would crash), shrink math to 1e-12, override math by double-run comparison
(prior observed cohort-free, expected shrink recomputed, matched to 1e-9),
complement coherence, the λ-anchor against poisson(2, λ), provenance and
JSON-serializability; audit fixtures tag two notes hybrid_cohort and assert
by_engine aggregation + rendered rows. Suite 101/101 sandbox
(--ignore=test_supabase; 104 expected on the Mac). pyflakes DELTA-0 vs the
993f10e base (same 9 pre-existing identifiers, renumbered only). Battery v6:
24/24 (conditioning source pins incl. historical-profile untouched,
extreme-zero/one cohorts, determinism, complement coherence, subprocess
suite).

---

## Addendum 18 — 2026-08-03 (late night): copy-pastable README git block + Addendum 17 deploy record

README §Git workflow reworked on operator feedback: the example workflow
carried placeholder pathspecs (scripts/<file>.py) that broke literal
copy-paste (pasting the line errors with "did not match any files"). The
block now uses an edit-one-line FILES array — FILES=("…" "…") then
git add "${FILES[@]}" — zsh/bash-safe; every other line pastes verbatim.
Docs-only change.

---

## Addendum 19 — 2026-08-03 (close of night): ACTIVE WORK QUEUE for the next agent + localdata sync runbook

### A. Work queue (do in this order)

1. **DEBIAS WIRING (engine-aware).** Current state:
   `load_rolling_audit_hit_rates()` (scripts/picks_today.py, ~line 380)
   multiplies every raw 🔥 probability by a hit-rate read from
   picks_audit_rolling.json → enhancements_audit.by_enhancement (gate:
   recommended>=5). That source is the 24-item recommended-enhancement
   overlay — tiny n (live example 2026-08-03: match_over_25 damped ×0.556
   off n=9, displaying 36.7% against a ~0.66 hybrid raw). Target source:
   event_notes_audit.by_market (full surface, 212 notes/window, Addendum
   12) with min-n >= 15, AND engine-aware via by_engine (Addendum 17):
   hybrid_cohort notes are already cohort-shrunk, so multiplying them again
   double-damps. RULE: before writing code, let 2–3 days of hybrid-tagged
   notes settle and READ the by-engine table. If hybrid_cohort |Δ| <= model
   |Δ| per market, gate hr=1.0 for hybrid notes and debias only the
   model/legacy residual. Ship via payload protocol; unit-test the loader's
   source preference + min-n + engine gating with fixture JSON.

2. **VETO RE-MINE.** 3,185/4,247 league contexts carry verdict UNKNOWN
   (purity assay 2026-08-03); UNKNOWN→watchlist/skip is a structural cause
   of empty certified buckets (2026-08-03 night: 0 certified, 14 vetoes /
   417 matches). Directions (write the design doc FIRST — no decision made):
   pool evidence across edges per league; longer windows; hierarchical
   fallback (league→niche→competition_type). Success metric = certified
   picks/day delta measured walk-forward; NEVER relax verdicts to
   manufacture yield.

3. **SMALL TICKETS.** (a) BENCHED reset runbook + time-bomb test: the decay
   monitor benched `3way-unanimous min_p>=60 avg_p>=60` for the 4th time on
   2026-08-03; benching self-heals at the next mine_consensus (re-certifies
   from walk-forward scratch) — document the operator-visible lifecycle. The
   pre-existing test test_benched_circuit_breaker has a date-stale
   assumption that goes red around 2026-10-02 — FIX BEFORE THEN. (b)
   Winner's-curse doc: LINE_THRESHOLDS display only high-side notes (e.g.
   home_under_35 shown iff p>=0.90), so realized systematically trails
   promised on display-filtered markets — part of the observed −27.6 Δ is
   the selection effect, not engine error; document it in the audit section
   header.

### B. localdata sync — who owns what, and how the Mac refreshes

- In the REPO, localdata/ is written ONLY by the GitHub Actions persist
  loop (chore: persist pipeline state). The Mac NEVER commits it; local
  pipeline runs dirty it as disposable, re-derivable scratch.
- `git pull --no-rebase` DOES pull the Actions-committed localdata to the
  Mac — but git REFUSES to merge when the same files are locally modified
  ("Your local changes … would be overwritten by merge"). That refusal is
  git protecting scratch files, not a bug in the commit block.
- Refresh recipe (cloud version wins):
      git checkout -- localdata/     # discard local scratch (safe: re-derivable)
      git pull --no-rebase           # clean merge brings the bot's state
  or via stash:  git stash push -- localdata/ && git pull --no-rebase && git stash drop
  single file:   git checkout origin/main -- localdata/picks_2026-08-04.txt
- Which version is "truth"? Cloud and Mac runs are PARALLEL computations of
  the same pipeline; they converge on settled facts. The ownership rule
  exists for CODE integrity. For reading the freshest forecast, use
  whichever machine ran most recently — locally, the dirty file on disk.

### C. Standing protocol (condensed; unchanged)

Payloads = full-file placement + SHA256MANIFEST BASE/TARGET + Phase-0
red-team + battery + fresh-tree rehearsal + Antigravity gates + independent
upstream sha-verify before "deployed" is declared. Git: explicit FILES
commits (README §Git workflow); divergent → `git pull --no-rebase -X ours`;
merge, never erase. Commands: ONLY `--auto-run` / `--auto-once` /
`--force-repick`. Zero API-credit spend. Gates without pasted output did
not happen. Calibration ≠ edge: the registry gates value; audit tables
measure promises only.

Addendum 17 deploy record (rolled up): shipped as 5f56d92 (feat) + merge
7f1f190 + 96295f8 (absorb chore; the localdata conflict on
picks_audit_2026-08-03.md resolved --theirs = bot-owned, the correct
owner). All 5 files upstream sha-verified against the manifest TARGET;
payload zip deleted. G4 live-schema smoke: cohorts n=586–2913 across
avg_p 65–75 home. First live hybrid note observed the same night
(2026-08-04 forecast, Dinamo Zagreb vs Kauno Zalgiris): BTTS-Yes 47.5%
tracks the unconditioned cohort rate 0.474; plain source labels at birth
(Addendum 16). Reader note: that forecast's "Match Over 2.5: 36.7%" is NOT
the cohort disagreeing — it is the pre-existing performance-feedback
multiplier (rolling hit-rate debias; match_over_25 hr=0.556 from the
recommendation ledger) applied on top of the hybrid raw (~0.66). The audit
scores the displayed post-debias promise, so the by-engine table measures
what was actually promised.

---

## Addendum 20 — Actions secrets parity audit + ODDS_API_* knob wiring (2026-08-03)

**Trigger:** operator question — "is the cloud run as robust as the machine run,
since GitHub does not have the odds API secrets?"

**Audit findings (operator-verified against Settings > Secrets and variables > Actions):**

1. Core seven secrets exist (SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY,
   BZZOIRO_TOKEN, CALLMEBOT_APIKEY, CALLMEBOT_PHONE — all ~2 months old).
2. **ODDS_API_KEYS was added 2026-08-03.** Before this date, every Actions run
   reached `theoddsapi.enabled()` false and logged "no ODDS_API_KEYS configured;
   0 rows" — the capture step soft-no-op'd inside run_soft (green logs, zero
   snapshots). Receipt corroboration: every historical commit touching
   localdata/theoddsapi_odds_*.csv.gz was authored by the operator account
   (Mac-side captures), never github-actions[bot]. Mac-only capture explained.
3. Five tuning knobs were added to secrets the same day (ODDS_API_REGIONS,
   ODDS_API_MARKETS, ODDS_API_TOTAL_POINTS, ODDS_API_MONTHLY_BUDGET,
   ODDS_API_CLOSE_WINDOW_MIN) but the workflow env block mapped only the core
   seven — stored secrets never reach the runner without a mapping line.

**Fix (this addendum):** daily.yml env block now maps the five knobs with
`${{ secrets.X || '<default>' }}` fallbacks mirroring code defaults
(theoddsapi.py: eu / h2h,totals / 2.5 / 480; capture_theodds.py: 45). Rationale
for `||`: the TOTAL_POINTS parse is not empty-string-safe (empty env -> empty
tuple -> no totals kept), and an unset/empty secret would otherwise inject "".
With `||`, unset or empty secrets are a no-op; set secrets always win.

**Behavioral delta intended: none locally** (Mac .env unchanged), cloud now
captures The Odds API snapshots itself under the operator-configured budget
ring. Pick selection remains odds-independent (consensus + purity gates);
snapshots feed CLV/audit pricing only.

**Deployment verification plan (receipts, not vibes):** first bot-authored
commit touching localdata/theoddsapi_odds_YYYY-MM.csv.gz or
localdata/theoddsapi_usage.json after this merge = cloud capture live.
Run log line "no ODDS_API_KEYS configured; 0 rows" must be absent thereafter.

**Process note:** the localdata authorship trail showed manual operator commits
of localdata on 2026-08-03 (15:59, 18:09 UTC). One-off seed commits during the
divergence repair are acceptable; as a habit they recreate the three-collision
pattern. localdata stays bot-owned; humans ship code+docs via the FILES block.

---

## Addendum 21 — Shared settled-results overlay (cloud/laptop audit parity) (2026-08-04)

**Trigger:** operator observation — the cloud-run audit reported 2
"unmatched_result" picks while identical Mac runs settle everything.

**Root cause (evidence-backed):** warehouses are machine-local (CI cache /
laptop disk); `audit_recent_picks.load_results_index` settles ONLY from the six
`*_settled` warehouse views. `.gitignore` shares the 3 pre-split concatenated
CSVs + an explicit artifact list — post-split scrape memory never crosses
machines. Receipt (operator Mac query): forebet/vitibet held "South Hobart 2-0
Ulverstone" (2026-07-11) and "Hobart Zebras 1-0 Ulverstone" (2026-08-02); the
cloud warehouse never captured either row, and the fuzzy fallback (bigram
Jaccard >=0.40, pure string sim — entity_registry.json not consulted, confirmed
by code read) cannot match rows that do not exist. Bonus receipt from the same
query: 2026-05-10 appears twice with identical score 0-4, once as "Hobart
Zebras" (forebet) and once as "Clarence Zebras" (statarea) — same club, two
names; see queued ticket below.

**Fix (this addendum):** settled scores are facts, and facts belong in git.
- `scripts/export_settled_results.py` (new): exports a deterministic rolling
  90-day window (`SETTLED_OVERLAY_DAYS`) of priority-deduped settled rows from
  the six views to `localdata/settled_results.json` (atomic write, same source
  order as the audit: forebet > bettingclosed > zulubet > statarea >
  scoutingstats > vitibet). Convergence loop: each export first UNIONS the
  inbound shared file (other machines' rows, delivered by git pull) with this
  machine's warehouse rows — dedup by normalized pair, warehouse wins on
  conflict, stale inbound dropped — so the shared file converges to the union
  of BOTH machines' memories no matter which machine ran last. (Caught in
  pre-deploy review: without the inbound union, the file would only ever hold
  the writer's own rows and cross-machine memory would never travel.)
- `scripts/daily.py`: runs it via run_soft right after every build_warehouse
  (official + autonomous_intraday), i.e. always before any audit in the run.
- `.gitignore`: `!localdata/settled_results.json` — bot-owned like the rest of
  shared localdata; humans never hand-edit.
- `audit_recent_picks.load_results_index`: settles from warehouse ∪ overlay.
  Warehouse rows always win on conflict (freshest local memory); overlay only
  fills rows the machine never captured. Entries are origin-tagged and the
  report gains `settled_via_overlay_picks` telemetry (Overall section + stdout).

**Behavioral delta:** none where warehouses already hold the row (warehouse-wins
dedup); rescue-only elsewhere. Registry/pricing/certification untouched.

**Tests:** +10 (export prio-dedup/window/no-views/self-test incl. inbound
merge; merge carry/conflict; overlay fill/warehouse-wins/noop; fuzzy rescue of
the real Clarence-vs-Hobart 08-02 case end-to-end via build_report). Suite:
101 -> 111 sandbox / 104 -> 114 Mac. Pyflakes delta-0
vs BASE (pre-existing: daily:40 unused date import, audit f-string).

**Verification plan (receipts):** first bot-authored audit after merge must show
"settled via shared overlay facts: >= 1" and unmatched_result_picks not climbing;
the two Tasmanian fixtures settle (South Hobart exact, Clarence/Hobart fuzzy).

**Queued ticket (NOT shipped here):** candidate entity override — forebet serves
club "Clarence Zebras" as "Hobart Zebras" (post-2019 merger). Requires entity
review before touching alias layers; join keys (norm_team) are drift-frozen.
Even without it, fuzzy >=0.40 matched the real case (pinned by test).

**Bookkeeping:** folded into the record: operator README commit 3b256934
(2026-08-03, +3/-1, git-workflow wording for local data handling) — docs-only,
no HANDOVER entry at the time; noted here per anti-drift protocol.

---

## Addendum 22 — .gitignore inline-comment trap (dead negation) + forced seed (2026-08-04)

**What happened:** Addendum 21 wrote its negation with a trailing comment
(`!localdata/settled_results.json   # ...`). gitignore supports comments ONLY
at the start of a line — the trailing text became part of the pattern, making
the whole negation dead. Receipt: operator's seed attempt refused with "The
following paths are ignored by one of your .gitignore files". The v7 battery
grep-checked the line's presence, not git's behavior — text checks cannot
catch semantic traps.

**Evidence (scratch repo, git ground truth):** BEFORE fix -> `localdata/*`
swallows the file, add refused. AFTER fix (comment on its own line, pattern on
the next) -> `git add` accepts, `git check-ignore` exits 1 (not ignored).
Swept the whole file: this was the only inline-comment negation.

**Fix (this addendum):** two-line layout in .gitignore. Battery v7.1+: assert
BEHAVIOR (`git check-ignore localdata/settled_results.json` must exit 1), not
text.

**The one-off seed proceeded via `git add -f`** (force overrides ignore for the
first add; a tracked file stays tracked forever, so the dead rule only ever
blocked the FIRST add). Once the seed commit landed, the shared overlay flows
permanently: bot `git add -A localdata/` picks up tracked-file updates
regardless of ignore state. Cloud convergence starts with the next bot run:
export unions inbound (now containing the Mac rows) -> Tasmania fixtures
persist bot-side -> bot audit shows "settled via shared overlay facts: >= 1".
Seed receipt: export = 39,103 rows from the Mac warehouse (incl. the NPL
Tasmania fixtures; local `grep -c "Ulverstone"` = 12).

**Process note:** breakers of assumptions deserve tests that check the
assumption's behavior, not the text that asserts it.

---

## Addendum 24 — Shadow slate: every stream reaches the phone (2026-08-04)

**Trigger:** operator directive — "lets make every stream reach my phone, not
just caution" (+ chosen format: two messages).

**Why this is evidence-driven, not just UX:** the rolling audit's by_bucket
table showed SKIPPED_VETO — the stream the old "never bet vetoes" doctrine
kept off the phone — as the window's most profitable stream (52 settled,
86.5% hit, +11.8% ROI), while pushed-bucket CAUTION ran -7.1% (n=21). A veto
doctrine written on older evidence had inverted. Doctrines die by receipts.

**What shipped:**
- `format_whatsapp_shadow_summary` (src/edgefactory/whatsapp.py): second daily
  message — sections SKIPPED_VETO / WATCHLIST_NO_ODDS / WATCHLIST_UNKNOWN_CTX,
  each labeled with that stream's rolling 30d record (`format_stream_record`,
  from localdata/picks_audit_rolling.json -> by_bucket; absent -> honest
  "no settled record yet"). Per-line "| Stream:" label. Cap 12 lines +
  "+N more" pointer. Formatter self-filters shadow buckets (overflow math
  can't leak CAUTION/CLEAN counts).
- `scripts/notify_whatsapp.py`: shadow dispatch with INDEPENDENT dedup ledger
  localdata/whatsapp_shadow_sent_ledger_<date>.json (main/discovery/shadow
  sends never suppress each other). Default ON; kill-switch
  EDGE_FACTORY_NOTIFY_SHADOW=0. Heartbeat stays quiet on shadow-only days
  (shadow message suppresses the empty-slate ping).

**Tests:** +6 (sections/labels/roi-None honesty/no-stats degradation/overflow
cap/no-clean-leak/empty). Suite: 111 -> 117 sandbox / 114 -> 120 Mac.
Battery v8 end-to-end: stubbed dispatch — main+shadow both send, ledgers
independent (1 vs 2 keys), rerun silent, kill-switch force-sends main only,
shadow-only day sends shadow without heartbeat. Pyflakes delta-0.

**Behavioral delta:** phone volume rises from ~1 msg/day to ~2 on slate days;
shadow is labeled transparency, not bet-push. Main slate content UNCHANGED.

**Verification plan:** next morning official run dispatches (or logs the
reason) both messages; receipts = dedup ledgers of both kinds in the bot's
persist commit + operator phone.

---

## Addendum 25 — Shadow dispatch integrity: chunker, encoded budget, ledger persistence (2026-08-04)

**Trigger (same-day production receipt):** the first live shadow slate
(Addendum 24) arrived TRUNCATED mid-pick ("Montana vs Nesebar ➡️ *H").
Diagnosis: the shadow slate was sent as ONE message; CallMeBot carries text as
a URL parameter, so ENCODED length — not character count — is what the pipe
bills on. Cut zone ≈ 2k encoded chars; the formatter's 12-line cap and
"+N more" pointer never fired (4 picks visible, no pointer) → pipe-side
truncation, not formatter logic. A runner crash cannot produce a partial
message (the GET carries the text atomically).

**Second defect (operator-pull receipt):** the bot's persist commit carried no
whatsapp_shadow_sent_ledger_*.json — Addendum 24 created the ledger but never
gitignore-negated it, so `git add -A localdata/` silently skipped it; dedup
memory died with cache eviction (duplicate-slate risk on evict). Verified
upstream at 54db8a7: main + discovery ledgers negated, shadow missing.

**What shipped:**
- src/edgefactory/whatsapp.py
  - Slim one-line shadow picks (odds · prob · KO · rule + certified 🔥 combo
    token when enhancement_label/probability present; per-line "Stream:"
    dropped — section headers are restated on every chunk).
  - SHADOW_MSG_BUDGET = 1500 encoded chars (below observed ~2k cut zone).
  - _shadow_blocks: single structural source for formatter + chunker (the two
    renderers cannot drift apart).
  - chunk_whatsapp_shadow_summary: encoded-budget packer. Atomic unit = one
    line → a pick can never be torn (the 2026-08-04 failure mode). No orphaned
    section headers; spanning sections restated "(cont.)"; freak over-long
    lines hard-truncated and MARKED "(cut)"; "(k/n)" numbering, applied
    post-pack with a 48-char numbering reserve (first revision packed at full
    budget then numbered and the monster-slate test caught the overflow —
    text-vs-behavior class, again).
- scripts/notify_whatsapp.py: _dispatch_shadow_chunks — in-order sends with
  per-chunk encoded-size logging; ALL-OR-NOTHING ledger barrier: first failed
  chunk aborts and writes NO dedup keys (the whole slate re-sends next run;
  a half-delivered slate is never permanently deduped). --force keeps legacy
  semantics (attempt all chunks, ledger proceeds).
- .gitignore: !localdata/whatsapp_shadow_sent_ledger_20*.json (comment on its
  own line — Addendum 22 lesson: gitignore has no inline comments).

**Tests:** shadow file 6 → 13 (slim-line, enhancement token on/off,
single-chunk == flat formatter, monster-slate budget/structure, freak-line
cut marker, determinism, budget guardrail). Suite: 117 → 124 sandbox
(expected 120 → 127 Mac). Pyflakes delta-0.

**Folded receipts (the Addendum 23 paperwork, landed here per the anti-bloat
review — one deploy instead of two):**
- Deploy chain, all sha-verified at source: A19 9c8545d → README 3b25693 →
  A20 005b11f → c3d2f0f → A21 b7bc6e6 → seed b63993c → A22 1180d9b →
  f4e1b2ab → A24 cadbe75 → merge e9eca58 (post-merge byte-integrity ✓).
- Self-heal production receipt (cloud audit at e9eca58): unmatched 2 → 0,
  settled 88 → 90, "settled via shared overlay facts: 6", hit 0.78409 →
  0.78889, ROI 0.05077 → 0.05247. Overlay rows now 39,319 and bot-carried.
- zsh lesson: '#' is literal in interactive zsh — never put trailing comments
  on command lines in operator blocks (a gate with a trailing comment is a
  gate that silently did not run).
- Seed bookkeeping: one-off localdata commit via git add -f (39,103 rows),
  accepted process precedent with explicit rationale.
- Open ticket: Tasmania-class coverage miss — cloud capture never saw the
  South Hobart / Hobart Zebras rows the Mac scraped (scrape budgets / page
  depth). The overlay masks the symptom; it does not fix capture.
- Lesson banked: "delivered ≠ delivered intact" — battery v8 proved send()
  was CALLED with exact text; nothing proved a long message ARRIVES intact.
  Budget-enforced chunking makes "arrives intact" testable by construction.
- Stale standing item: README's CallMeBot whatsapp.py endpoint warning — the
  code already uses whatsapp.php and the 2026-08-04 slate demonstrably
  arrived. Prune in a future docs pass.
- Pricing interrogation (operator Mac 2026-08-04, pre-registered verdicts):
  scoutingstats_odds cohort n=12 settled, ROI −33.2% at logged prices
  (reproduces the audit to the third decimal — cohort identity proven).
  Decomposition: 50% hit at ~1.39 avg prices (needs ~72%) ⇒ ~28pp of the loss
  is selection; ≤ 3–5pp is price (bzzoiro higher on all 3 cross-checkable
  picks, mean gap +0.10). Pre-registered verdict: INCONCLUSIVE on price
  toxicity. STRUCTURAL finding: bzzoiro-corroborated 3 picks → +1.0% ROI vs
  sole-source 9 picks → −44.6% → Addendum 26 queued (corroboration
  quarantine: scoutingstats-only price ⇒ not pushable, still audited;
  alias_fuzzy prices ineligible for best-odds + suspect_price specimens;
  both tables become native audit sections so /tmp forensics retire).
  alias_fuzzy specimens: 6/6 bzzoiro-attached, −35.7%, and price-split
  3-0 (≤1.52) vs 0-3 (≥1.52) — consistent with wrong-fixture attachment
  inflating apparent value; specimen-level proof mechanism lands in A26.
- Queued: Addendum 27 (category-spanning combo display — best match/home/away
  enhancement slots) AFTER the 2026-08-11 by-engine verdict. Dynamic selection
  MUST route through the enhancement certification registry (PAPER/PROVEN/
  BENCHED), never raw rolling hit rates — display debias IS debias, and the
  registry is currently EMPTY (enhancement_registry: {} in the rolling
  audit), so there is nothing legitimate to route through yet.
- Time-bomb unchanged: test_benched_circuit_breaker hard fix by 2026-10-02.

---

## Addendum 25.1 — Surgical hardening of shadow dispatch (2026-08-04)

**Driver:** an independent agent red-teamed the DEPLOYED Addendum 25 (be4c697)
— replicated the full suite independently (127 passed, matches), measured the
live slate at source, and raised four ambers. All four survived verification;
two were outright errors in the Addendum 25 fold-in, corrected below. The
operator locked three refinements (explicit unit naming; force as read-only
bypass; stricter 🔥 rule through ONE shared helper). This is the process
working as designed: review beat pride.

### Errata on Addendum 25 (prominent — the ledger stays honest)

1. **Cut-zone estimate was wrong.** Addendum 25 said "~2k encoded chars".
   Measured reconstruction of the received phone prefix (operator's paste,
   asterisks restored to wire format, urllib.parse.quote of the exact
   string): 739 raw chars -> **1,415 encoded text chars**. With ~90 chars of
   fixed host/path/phone/apikey overhead the request was ~1,500 full-URL
   chars — suspiciously round; a ~1,500 full-URL ceiling is now the leading
   suspect. Budget rule stated with method: encoded text <= ~0.78 x observed
   cut -> **1100**.
2. **"Enhancement registry EMPTY" was wrong.** The claim was sourced from a
   stale rolling-json snapshot key; the registry FILE (ground truth,
   localdata/enhancement_registry.json) held two PAPER entries at be4c697:
   btts_yes@v1 (n=1, hits 0, -1.0) and match_over_25@v1 (n=2, hits 2, +1.35).
   Own rule broken: check the artifact, not the summary of the artifact.
3. **"PROVEN" is not a registry state.** The machine is SHADOW -> PAPER ->
   ELIGIBLE -> BENCHED (ELIGIBLE = Wilson LB95 hit-rate >= mean breakeven of
   prices actually paid; BENCHED has no automatic re-entry). The Addendum 25
   receipts used PROVEN. Wrong enum.

### What shipped in 25.1

- SHADOW_MSG_BUDGET renamed **SHADOW_ENCODED_TEXT_BUDGET = 1100** — the unit
  is explicit (the encoded text= value, not the full URL). Dispatch logs BOTH
  encoded-text length AND the full CallMeBot request length — lengths only;
  the URL embeds phone + apikey and is never logged.
- _dispatch_shadow_chunks tightened: success <=> EVERY chunk dispatched; any
  failed chunk -> False. --force now bypasses the ledger READ only; it still
  attempts every chunk for diagnostics, but can never convert failure into a
  ledger write. The Addendum 25 version had preserved legacy
  "dispatched or force" semantics; the reviewer was right that an
  all-or-nothing barrier returning success after total failure is lie-shaped.
- State-honest combo markers via ONE shared helper
  (edgefactory.whatsapp.enhancement_marker) used by BOTH slates, so the two
  renderers cannot drift again: **🔥 only when the enhancement TYPE is
  registry-ELIGIBLE AND the current fixture has a valid captured price**;
  🔬 otherwise (SHADOW/PAPER/BENCHED/unknown types, and ELIGIBLE-but-
  currently-unpriced — an unpriced fixture is not an actionable
  recommendation, even for a certified type). Resolution runs in notify
  (_annotate_enhancement_markers) through the audit's own machinery
  (enh_registry.all_statuses + enh_pricing attach probe). Fail-soft: anything
  unresolvable renders 🔬. NOTE: with zero ELIGIBLE types today, EVERY combo
  token now renders 🔬 in production — the phone finally displays the true
  certification state; 🔥 appears only when a type earns it on priced
  evidence.
- Committed dispatch tests (previously battery-only, deleted after runs):
  abort-on-failure; force-attempts-all-but-returns-False; success-requires-
  every-chunk; end-to-end ledger barrier (total failure -> no ledger file;
  healthy rerun -> ledger written; third run dedup-silent); kill-switch.
- Suite: 124 -> 131 sandbox (134 Mac expected). Pyflakes delta-0.

**Battery v9.1** reissued with the tightened semantics (budget pinned 1100,
force honesty, 🔬/🔥 marker states, request-length helper). Credit:
independent agent review + operator-locked refinements — cross-agent
red-teaming working exactly as intended.

---

## Addendum 25.1.1 — Force semantics made global; hermetic notify tests (2026-08-04)

**Driver:** the independent review red-teamed f8f1679 and verified 25.1's
shadow fixes, but caught two real remaining defects. Both were reproduced
from source before fixing — Receipt A reproduced EXACTLY: a clean no-.env
checkout of f8f1679 gives `1 failed, 133 passed`, failing test
test_shadow_ledger_barrier_end_to_end (credential gate short-circuits main()
before the mocked dispatch). Receipt B verified line-by-line: normal,
discovery, and heartbeat families still gated ledger writes on
`if dispatched or args.force:`, and the process exit was
`0 if any_dispatched or args.force`.

### Errata on Addendum 25.1 (prominent — the ledger stays honest)

1. **"Force is a read-only bypass" was true only for the shadow helper.**
   The other three families + the exit code still carried pre-25 semantics:
   a --force run with TOTAL dispatch failure returned exit code 0 with no
   ledger written, and `any_dispatched` let one successful family mask a
   failed one even without force. The 25.1 claim is corrected: it is now
   true GLOBALLY (all families + exit status).
2. **Committed e2e notify tests were not hermetic.** They passed on the
   operator Mac (134 passed) only because a real .env supplied live
   credentials; on a clean checkout the same source gives 1 failed / 133
   passed. They also wrote/unlinked 2099-* ledgers in the repo's REAL
   localdata. Rule now pinned: no committed test may depend on .env, real
   credentials, repo-local ledgers, or the network.

### What shipped in 25.1.1

- **Force semantics, global:** --force bypasses ledger READS / dedupe only.
  Ledger writes now require real dispatch success in ALL four families
  (main / discovery / shadow / heartbeat) — `if dispatched:`, never
  `or args.force`. Exit status: non-zero if ANY intended message/burst
  fails; one successful family never masks another's failure; total failure
  under --force exits 1; silence (nothing intended) still exits 0.
- **Provider aggregate semantics PRESERVED, with justification:**
  _dispatch_message still means "at least one configured provider
  dispatched". Providers are redundant channels to the same phone; a Meta
  outage whose CallMeBot copy landed is delivery success, and per-provider
  exceptions already log ERROR. Changing this would fail runs that achieved
  delivery.
- **Telemetry honesty note:** no GitHub Actions workflow invokes
  notify_whatsapp.py (verified by grep), so the stricter exit code cannot
  fail any cloud job; it surfaces in operator-run/scheduled invocations —
  which is where a human looks.
- **Hermetic committed tests (tests/test_notify_whatsapp.py):** dummy
  CALLMEBOT_APIKEY/CALLMEBOT_PHONE via monkeypatch.setenv (passes the
  credential gate identically with or without a real .env), notify.LOCALDATA
  redirected to tmp_path (zero writes to repo localdata), dispatch stubbed
  (zero network). New pins: forced failure in EACH family ⇒ non-zero exit +
  no respective ledger; forced total shadow failure ⇒ non-zero + no shadow
  ledger; successful family does not mask a failed family; recovery writes
  ONLY the intended ledger; rerun deduped silent; kill-switch intact;
  helper force semantics (attempt all, success iff every chunk dispatched)
  unchanged from 25.1.
- **Preserved per lock:** SHADOW_ENCODED_TEXT_BUDGET = 1100; dual-length
  request logging (lengths only, secrets never logged); shared
  enhancement_marker (🔥 = registry-ELIGIBLE AND currently validly priced;
  🔬 otherwise) in both slates; no changes to pick logic, source weighting,
  registry transitions, enhancement ranking, or Addendum 26 scope.
- **Battery v9.2** reissued: runs offline with dummy credentials only;
  proves the new global force exit/ledger semantics and repo-localdata
  non-pollution; retains all v9.1 checks (1100 budget, chunk invariants,
  state-honest markers, dedupe, .gitignore behavior, helper semantics).

**Suite: 134 → 138 (actual), and — the point of the fix — IDENTICAL with
.env present and with .env stripped: 138 = 138.** Pyflakes delta-0.
Credit: independent agent review, round 2 — both receipts held up under
source verification. Cross-agent red-teaming remains the QA backbone.

---

## Addendum 25.2 — Provider-ack honesty + burst-drop mitigation (2026-08-04)

**Driver:** the first production run of the hardened pipeline (Actions run
30903853265, head c411a40, 13:12–13:16 SAST) wrote the 4-key shadow dedupe
ledger — but nothing reached the handset. A same-day scoped --force resend
(2 chunks, ~1s apart) DID arrive intact ("physical delivery receipt" pasted
verbatim). The scheduled run's CallMeBot response bodies were DISCARDED by
the code, so the 13:13 cause is unprovable: accepted-then-dropped provider
transient is the LEADING explanation, not a fact. The reviewer's precision
correction stands and this entry adopts it.

### Doctrine (pinned, quoted)

> **The ledger records provider acceptance, not handset delivery. Phone
> receipt remains the final delivery evidence.**

### Errata (prominent)

1. **Addendum 25.1.1's telemetry note was imprecise.** It said "no GitHub
   Actions workflow invokes notify_whatsapp.py". Actions invokes daily.py,
   and daily.py reaches notify through run_soft (call sites at lines
   517/719/769/773). Practical conclusion unchanged — run_soft turns any
   notify failure into a WARNING, not a workflow failure — but the mechanism
   sentence was wrong. Credit: independent reviewer (round 3).
   Correct wording: **"daily.py reaches notify indirectly via run_soft;
   notify failure becomes an Actions warning rather than a workflow
   failure."**
2. **Dispatch success was never ack-verified (pre-25.2).** send_callmebot
   RETURNED the response body; notify discarded it. Any non-crashing call —
   including 200-class error/throttle/activation bodies — counted as
   dispatched. This is the gap the 13:13 incident exposed.

### What shipped in 25.2

- **CallMeBot ack classifier** (edgefactory.whatsapp): HTML-stripped,
  normalized body; accept ONLY the observed success class ("message queued"
  = the 2026-08-04 production ack, verbatim fixture in tests; "Success" =
  legacy fixture class); reject empty/unknown/error-class; reject-hint scan
  runs FIRST so an "ERROR: message not queued" style body can never sneak
  through the accept phrase. send_callmebot_whatsapp now RAISES on rejected
  acks — the exception carries only the sanitized category (accepted /
  error-class / empty-body / unknown-class), never the URL, key, phone, or
  raw body. _dispatch_message's existing exception path converts that into
  dispatched=False → no ledger + non-zero exit (25.1.1 semantics) → Actions
  WARNING via run_soft. Loud, honest, self-healing on the next run.
- **Inter-chunk spacing** (notify._dispatch_shadow_chunks): between chunks
  delivered via CallMeBot, pause EDGE_FACTORY_SHADOW_CHUNK_DELAY seconds
  (default 4; 0 disables). Labelled a burst-drop MITIGATION, explicitly not
  a proven cause. Tested through a mocked sleep; the committed suite pins it
  to 0 so tests stay instant.
- **Battery v9.3** reissued: ack-class pins (production body, fixture,
  rejected/error/empty/unknown, phrase-trap), send-raise sanitization
  (exception must not leak key/phone), 200-error-body e2e (non-zero exit,
  no ledger), spacing invocation/default/disabled, and all v9.2 checks
  retained (1100 budget, chunk invariants, markers, global force semantics,
  isolation, gitignore behavior, repo non-pollution).
- **Unchanged per lock:** SHADOW_ENCODED_TEXT_BUDGET = 1100; dual-length
  logging; shared enhancement_marker; 25.1.1 force/exit semantics; no pick-
  logic, registry, or Addendum-26 scope touched.

**Suite: 138 → 147 (actual), identical with and without .env (147 = 147).**
Pyflakes delta-0. The 2026-08-04 slate reached the handset intact via the
scoped --force resend (2 chunks, 932/1005 encoded text chars, full URLs
~1009/~1082 — ~30% under the suspected ~1,500 pipe ceiling) — Addendum 25's
truncation + persistence objectives are CLOSED with physical receipts.

---

## Addendum 25.2.1 — Classifier made structural (2026-08-04)

**Driver:** independent review of deployed 9cecbb6 (round 5) proved a real
25.2 design flaw. The success body ECHOES the outbound text, but the 25.2
classifier accepted whenever 'message queued' or 'success' appeared ANYWHERE
in the normalized body — confusing echo for ack. Reproduced on the deployed
code before fixing — four traps ALL falsely accepted=True/category=accepted:
(1) 'Text to send: Success …', (2) 'Text to send: message queued …' (the
reviewer's two fixtures), plus two more found in the same audit: (3)
'We were unsuccessful in queueing your request' ('unsuccessful' contains
'success'), (4) '<i>Message queued.</i>' right phrase, wrong tag. Not a live
hazard for today's slate (current outbound text contains neither phrase) but
a genuine future false-ledger path. Owned: the loose substring rule was my
design error in 25.2.

### What changed (scope kept surgical, per the reviewer's lock)

- **Structural acceptance only:** real ack ⇐ the phrase appears as markup —
  regex `<b>\s*message\s+queued\.?\s*</b>` (case-insensitive, period
  optional). Our outbound text is WhatsApp markdown; it can never contain
  that HTML tag, so echo can never forge it.
- **Legacy fixture:** accepted only when the normalized body IS exactly
  'success' ('Success' alone in the body — never as a substring).
- **Reject-hint precedence retained** (error-class always wins).
- **Category logic uses the same structural test** — 'accepted' is only
  reported for structurally-accepted bodies.
- **Regression fixtures committed:** both reviewer echoes, the
  'unsuccessful' trap, the wrong-tag trap; plus structural pins (tag alone,
  case-insensitive tag, period-optional, tag+echo coexistence accepted).
- **Fail-closed by design:** if CallMeBot ever changes its success HTML,
  acks are rejected → loud retry + no ledger. A false-reject costs one
  retry; a false-accept writes a false ledger. Closed is the cheap side.

**Suite: 147 → 150 (actual), identical with and without .env (150 = 150).**
Pyflakes delta-0. Battery v9.3.1 reissued (all v9.3 checks + structural
classifier pins). Credit: independent reviewer, round 5 — five rounds, five
real catches, zero false alarms. The cross-agent red-team is the strongest
QA instrument this project has.

---

## Addendum 26 — Price-evidence quarantine + native audit tables (2026-08-04)

**Driver:** the 2026-08-04 price interrogation separated a real policy problem
from a pricing accusation. The ScoutingStats-odds cohort was weak at logged
prices, but the pre-registered decomposition did **not** prove a generic bad
price feed. It did prove two narrower operational hazards:

- a ScoutingStats fallback price with no Bzzoiro match is sole-source evidence;
  it must remain auditable but cannot turn an otherwise clean model pick into a
  pushed bet;
- an `alias_fuzzy` event-string match can attach the wrong fixture's price. Its
  candidate must be visible as suspect evidence, never silently become
  operational “best odds.”

Historical receipt retained from the interrogation: the settled
`scoutingstats_odds` cohort was n=12 / ROI about -33.2%; Bzzoiro-correlated
examples were materially different from the sole-source subset, while
`alias_fuzzy` specimens were weak and price-split in a way consistent with bad
fixture attachment. That is sufficient for quarantine, not a claim that every
ScoutingStats price is wrong.

### What changed

1. **Stable price-evidence fields at pick time** (`scripts/picks_today.py`):
   `BZZOIRO_PRIMARY`, `SCOUTINGSTATS_SOLE`, `SUSPECT_ALIAS_FUZZY`,
   `BETEXPLORER_RESCUE`, `SOURCE_FALLBACK`, and `UNMATCHED` are archived on the
   pick. They describe price evidence, not model quality.
2. **ScoutingStats sole-source quarantine:** a secondary ScoutingStats match
   is retained with its odds for settlement/audit, but is bucketed
   `WATCHLIST_UNCORROBORATED_PRICE`, never `CERTIFIED_CLEAN` or `CAUTION`.
3. **Fuzzy-price exclusion:** an `alias_fuzzy` candidate is copied to
   `suspect_price` with source/bookmaker/capture metadata and cannot overwrite
   the pre-existing operational odds. It is bucketed
   `WATCHLIST_SUSPECT_PRICE`; a context VETO still wins over price quarantine.
   The established BetExplorer rescue path may clear this only when it supplies
   its own matched price, at which point evidence becomes `BETEXPLORER_RESCUE`.
4. **Phone transparency:** both new non-push buckets join `SHADOW_BUCKETS`, so
   Addendum 24's every-stream doctrine remains true: they appear in the shadow
   slate with rolling records rather than disappearing from view.
5. **Native audit surface** (`audit_recent_picks.py`): rolling JSON gains
   `by_price_evidence` and `by_price_quarantine_reason`; Markdown gains
   `## Price Evidence / Corroboration Audit` and
   `## Suspect-price Quarantine Audit`. The latter carries suspect-price capture
   count and average separately from operational priced ROI. Legacy archives are
   conservatively classified from stored source/match-method fields; they are
   not retroactively rebucketed.

### Boundary / doctrine

Quarantine removes **push eligibility**, not evidence. These rows continue
through frozen archives, Supabase source payloads, settlement, rolling ROI, and
the phone's shadow lane. The mechanism is deliberately fail-closed: price
confidence cannot manufacture a bet merely because model/context gates pass.

### Tests

New pure price-quarantine coverage pins Bzzoiro-primary eligibility,
ScoutingStats-only retention+watchlist quarantine, fuzzy-price non-replacement,
no-prior-price suspect retention, context-VETO precedence, and unchanged legacy
fallback behavior. Audit fixtures pin both new JSON groups, native Markdown
sections, and suspect-price aggregates; shadow formatter coverage pins the new
sections. Full suite and battery receipts belong to the deployment record.

**Not changed:** model probabilities, source weights, edge certification,
enhancement registry transitions, or the 2026-08-11 by-engine/debias verdict.

---

## Research probe — OddsPapi market coverage (2026-08-04)

**Trigger:** operator identified the real post-Addendum-26 gap: the engine
cannot select a market it does not know a bookmaker offers. A rich retail board
may contain team totals, alternate lines, DNB/double chance, handicaps, and
combinations while the current production market surface sees only a narrow
subset.

**Scope (deliberately NOT a production adapter):**

- `ODDSPAPI_API_KEYS` is a comma-separated key ring in `.env` only; the tracked
  template contains placeholders. The existing singular key remains a fallback.
- `src/edgefactory/sources/oddspapi_odds.py` gains safe key-ring failover on
  auth/quota rejection, but remains outside `capture_daily` and daily pick
  selection.
- `scripts/probe_oddspapi_markets.py` is read-only. It loads a small existing
  pick shortlist, demands exact normalized fixture-pair matches (including
  explicit swapped orientation, never fuzzy coverage claims), fetches detailed
  OddsPapi boards, and reports bookmaker slugs, market IDs/labels, outcome
  counts, category availability, and requested-book hits. Default JSON output
  is `/tmp`, never bot-owned `localdata`.
- The probe determines whether the vendor genuinely covers target fixtures and
  markets. It does not create bets, alter pushes, capture all events, or infer
  combo value.

**Decision gate:** do not expand the OddsPapi adapter beyond its current narrow
1x2 fallback until a real probe confirms exact fixture coverage, target-book
coverage, actual market IDs, and stable market semantics for several fixture
classes. Any future combination market still requires a calibrated JOINT
probability; higher payout is not evidence of value.

**Tests:** key-ring parsing/failover, exact/swapped fixture matching, target
shortlist de-duplication/windowing, market-ID/category summary, optional market
catalog degradation, and offline self-test. Full-suite/battery receipts belong
to the probe deployment record.

---

## Research receipt — OddsPapi live evidence + locked 2026-08-11 runbook (2026-08-04)

**Purpose:** preserve the actual live-probe evidence and make the first
post-observation review deterministic. This is a research record, **not** an
OddsPapi production approval and not a bet recommendation.

### Live evidence receipt (all values are observations at capture time)

Research probe deployment:

```text
77ef7c51d51aa48d56c6851df6e9acce9a3c6013
research: add OddsPapi market coverage probe
```

Credentials loaded locally as a four-key ring; values were never printed,
committed, or placed in Actions.

1. **Narrow 2026-08-05/06 window:** 258 provider fixtures, 2 target fixtures,
   0 exact matches. `Fenerbahçe vs Sturm Graz` and
   `Panathinaikos vs CSKA 1948` were not returned. This was not treated as a
   fuzzy-match opportunity.
2. **Expanded 2026-08-04 through 2026-08-08 window:** 1,056 provider fixtures,
   6 target fixtures, 2 exact matches and 4 unmatched:

   ```text
   exact:     Dinamo Zagreb vs Kauno Žalgiris
   exact:     Newport County vs Roma
   unmatched: BG Pathum United vs Aston Villa
   unmatched: Montana vs Nesebar
   unmatched: Fenerbahçe vs Sturm Graz
   unmatched: Panathinaikos vs CSKA 1948
   ```

3. **Observed board depth for exact fixtures:**

   ```text
   Dinamo Zagreb vs Kauno Žalgiris: 143 bookmaker boards;
   richest observed board: 447 markets / 959 outcomes.

   Newport County vs Roma: 106 bookmaker boards;
   richest observed board: 221 markets / 486 outcomes.
   ```

   This confirms a rich provider surface for some exact fixtures. It does
   **not** establish bookmaker availability, licensing, or account access for
   the operator.
4. **Market-label vocabulary:** standard 1X2, BTTS, draw-no-bet, double chance,
   exact/correct score, handicaps, and totals were observed. Team-total-shaped
   labels were explicitly present:

   ```text
   Over Under Team 1
   Over Under Team 2
   ```

   On Newport County vs Roma, each appeared at 70 observed bookmaker boards.
   On Dinamo Zagreb vs Kauno Žalgiris, the corresponding full-time labels
   appeared at about 120 boards. The former probe category summary classified
   these as generic `totals` because it only recognised the literal phrase
   `team total`; that is a **probe-reporting limitation**, not evidence that
   team totals were absent.
5. **Explicit combination labels:** none were found in the returned label
   vocabulary for either exact fixture under `And`, `&`, `+`, `Combo`,
   `Same Game`, or `Same Match`. This is evidence for these two sampled boards,
   not a global claim that OddsPapi never carries combinations. Do not construct
   a bookmaker combo by multiplying separate leg prices or probabilities.
6. **Canonical fixture / market / price audit:** fixture
   `id1000085372729786` resolved as:

   ```text
   participant 1 / Team 1: Newport County
   participant 2 / Team 2: AS Roma
   status: Pre-Game
   ```

   The provider returned canonical full-time Team 1 and Team 2 total markets
   with explicit line, `Over` / `Under` outcome, decimal price, and per-row
   state. BC.Game, bet365, and Betano were each observed as
   `bookmakerIsActive=true`, `suspended=false`, `marketActive=true`, and
   selection `active=true` for sampled markets. This proves technical
   availability-plus-price capture for this fixture only; it is not an
   endorsement of any bookmaker.
7. **Freshness and execution caveats:** observed `changedAt` ages ranged from
   about 96 seconds to about 34 minutes. Some prior broad snapshots contained
   1.00 prices. Therefore a future adapter must not call a price actionable
   merely because it exists. It needs an explicit freshness policy, active-state
   checks, and a `price > 1.01` rule. `mainLine` is not a universal filter:
   active BTTS rows were observed with `mainLine=false`. Stake limits were not
   supplied in the sampled rows.

### Decision at observation time

```text
OddsPapi status: PARTIAL COVERAGE CONFIRMED — RESEARCH ONLY
```

It has passed a narrow technical proof for canonical team-total availability
and price capture. It has **not** passed broad fixture coverage, current-price
freshness policy, target-book availability, combination availability, settlement
validation, calibration, or walk-forward evidence. It must not enter
`daily.py`, `capture_daily.py`, selection, certification, WhatsApp, Actions
secrets, or any push path before the separate gates below are satisfied.

### Locked period: 2026-08-04 through 2026-08-10

> **SUPERSEDED 2026-08-05 by OPERATOR OVERRIDE — see Addendum 27.7.**
> The operator explicitly overruled this lock. The override authorizes
> wiring OddsPapi into the enhancement pricing path (real captured prices
> for enhancement markets), flag-gated OFF, walk-forward only, with the
> safety rails in Addendum 27.7. The 2026-08-11 review remains a calendar
> checkpoint but is no longer a hard gate for read-only price capture.

- Preserve Addendum 26 and the 2026-08-11 by-engine / calibration / debias
  observation window. Do not alter market selection, source weights,
  calibration, thresholds, registry transitions, price quarantine, or push
  logic for OddsPapi research.
- Do not add `ODDSPAPI_API_KEYS` to GitHub Actions, tracked files, logs, raw
  URLs, or chat. Keep it local in `.env` only.
- Do not infer a bet, a combo, or a preferred bookmaker from the captured
  prices. `structurally_usable_now` from the one-off audit was a data-quality
  flag, never a recommendation.
- Break this lock only for an actual operational failure; the repair must be
  surgical and independently receipted.

### 2026-08-11 review runbook — execute in this order

**This is a review/research gate, not a production-deployment day. No outcome
on 11 August authorises OddsPapi selection or WhatsApp use.**

#### 1. Confirm date and refresh cloud state

```bash
cd /Users/apple/Edge-Factory
date +%F
git checkout -- localdata/
git pull --no-rebase
git status --short
git log -1 --oneline
```

Proceed only when the local calendar is `2026-08-11`, the worktree is clean
apart from intentional review work, and no unresolved operational incident is
open.

#### 2. Close the existing engine observation first

Before considering OddsPapi, review the already-deferred by-engine,
calibration, debias, price-evidence, and settlement receipts. Record the
result separately from provider research:

```text
ENGINE OBSERVATION: keep frozen / surgical fix only / separately approved work
```

Do not use a richer odds board as a reason to override an unfavorable engine,
calibration, quarantine, or context verdict.

#### 2a. Close the source-funnel finding before provider research

Review the source-funnel receipt appended below before taking a fresh provider
sample. The `12 sources` headline is not a daily consensus count: the live
pick engine fetches 7 sources, permits 6 1X2 voters, 4 OU voters, and 3 BTTS
voters. Record role exclusions separately from live failures.

In particular, determine whether the Bzzoiro capture-forward snapshot can be
made available to a target-date forecast **without** stale/future leakage, and
whether BetClan has published the target-day listing. Do not change source
weights, voter lists, selection, or calibration on this review day. The only
permitted next step is a separately reviewed, read-only source-funnel research
packet if the evidence reproduces.

#### 3. Take one bounded fresh coverage sample (read-only)

This is the default fresh sample; it uses existing local keys without printing
them and writes only under `/tmp`:

```bash
cd /Users/apple/Edge-Factory
PYTHONPATH=src python3 scripts/probe_oddspapi_markets.py \
  --date 2026-08-11 \
  --days 5 \
  --limit 6 \
  2>&1 | tee /tmp/oddspapi_probe_2026-08-11.txt
```

Do not supply `--bookmaker` until actual operator-relevant bookmaker slugs are
identified. Do not paste `.env`, keys, raw request URLs, or full raw provider
payloads into chat.

#### 4. Score the fresh sample honestly

For every target fixture, record only:

```text
target date / fixture class / exact match, unmatched, or ambiguous /
provider bookmaker count / canonical team-total label present or absent /
explicit combo label present or absent / active-state and changedAt evidence
when a canonical audit is deliberately run
```

Keep fixture classes separate: major league, qualifier, friendly/exhibition,
lower division, and any other sparse context. Exact normalized pair matching
only; no alias-fuzzy rescue may be used to claim coverage.

#### 5. Choose one of these three outcomes

```text
A. HOLD / REJECT FOR NOW
   Use when relevant fixture classes still do not exact-match, canonical
   semantics or active/fresh evidence fail, or target books are unavailable.
   Keep OddsPapi dormant outside the current narrow fallback.

B. BUILD A REVIEW-ONLY RESEARCH PACKET
   Use only if the fresh evidence reproduces exact, canonical, active
   team-total coverage across relevant fixture classes. The packet may add a
   read-only availability/metadata capture surface only; it must not alter
   selection, certification, pricing eligibility, pushes, or Actions.

C. PRODUCTION INTEGRATION
   Not an available outcome on 2026-08-11.
```

#### 6. Scope required for any later research-only packet

A later packet must be full-file, pinned-base, manifest-verified, offline
battery-tested, fresh-tree rehearsed, and explicitly committed. Its permitted
scope is limited to:

1. fixture metadata join (`participant 1` / `participant 2` retained with the
   exact provider fixture ID);
2. canonical market metadata (`marketType`, `period`, line/handicap, canonical
   outcome IDs/names) rather than parsing bookmaker-specific outcome strings;
3. bookmaker, market, and selection state (`bookmakerIsActive`, `suspended`,
   `marketActive`, selection `active`, `changedAt`, `mainLine`, and limit when
   present);
4. archived research rows only when price is numeric and greater than 1.01;
5. explicit freshness measurement before any future threshold is proposed;
6. market-specific main-line handling — never drop an active lineless market
   solely because `mainLine=false`;
7. explicit report categories for `teamtotals-team1` and `teamtotals-team2`.

It must not create synthetic combinations. Any eventual combo requires actual
bookmaker availability, settlement-definition mapping, a current valid price,
a calibrated **joint** probability, and separate walk-forward evidence.

### Evidence required before any production proposal

All of the following remain mandatory after the research packet, not optional:

- reproducible exact coverage across the fixture classes that actually matter;
- named operator-relevant bookmaker availability — never assumed from a large
  generic bookmaker count;
- canonical fixture/side/line/outcome mapping retained in audit data;
- predeclared freshness and active-state policy with failure tests;
- price integrity, duplicate, stale, suspension, and 1.00-price rejection tests;
- settlement and calibration evidence for each proposed market family;
- walk-forward evidence that the new surface improves decision quality rather
  than merely exposing higher-payout prices;
- independent review and an explicit decision to change the frozen production
  gates.

Until every applicable gate is met, the truthful output remains:

```text
🔬 research candidate — not a bet recommendation
```

---

## Research receipt — source funnel evidence + 2026-08-11 queue (2026-08-04)

**Purpose:** explain why the dashboard/source inventory can show 12 sources
while a particular pick exposes only two or three `sources_used` entries.
This is a read-only observation record. It does **not** approve a source-weight,
source-voter, selection, calibration, price, or WhatsApp change.

### Role accounting (do not conflate these counts)

```text
README prediction-source inventory: 12
capture_daily jobs:              13 (includes bzzoiro_odds price adapter)
picks_today fetch set:            7
1X2 voter set:                    6
OU 2.5 voter set:                 4
BTTS voter set:                   3
```

The live picker fetches:

```text
forebet, zulubet, statarea, vitibet, betclan, bzzoiro, scoutingstats
```

but its 1X2 voter set excludes `scoutingstats`; its OU/BTTS voter sets are
smaller by design. PredictZ and WinDrawWin are shadow-only; AFootballReport and
FreeSuperTips are not current consensus voters; BettingClosed is principally
archive/confirmation; `bzzoiro_odds` is a price adapter, not a prediction vote.
Therefore `sources_used` is a **post-role, post-validity, post-exact-match**
field, never a count of all documented adapters.

### Live read-only funnel receipt — target date 2026-08-05

The seven live `picks_today` fetches returned:

```text
source          raw rows   valid 1X2 rows   exact-shared 1X2 keys
forebet              133               128                       12
zulubet               13                11                        8
statarea              24                24                        8
vitibet              221                18                       12
betclan                0                 0                        0
bzzoiro                0                 0                        0
scoutingstats         40                26                 non-1X2 voter
```

The match-stage distribution was:

```text
fixtures with 1 valid exact 1X2 voter: 141
fixtures with 2 valid exact 1X2 voters: 9
fixtures with 3 valid exact 1X2 voters: 2
fixtures with 4 valid exact 1X2 voters: 4
fixtures with 5 or 6 valid exact 1X2 voters: 0

fixtures reaching 2+ valid 1X2 voters: 15
fixtures reaching 3+ valid 1X2 voters: 6
```

Forebet had 128 valid 1X2 rows but 116 were solo-only. This is the immediate
reason a large source inventory does not turn into broad multi-source
consensus. It is a mixture of source coverage, probability availability, exact
fixture-key overlap, and market-role policy; it is not evidence of a hidden
12-to-3 cap.

Market-specific overlap was also sparse:

```text
OU 2.5: 20 exact fixtures reached 2+ voters; none reached 3+.
BTTS:    6 exact fixtures reached 2+ voters; none reached 3+.
```

### Bzzoiro finding — healthy data, stranded future forecast path

Bzzoiro was healthy at the provider boundary:

```text
local token present: yes (value never printed)
provider prediction count: 277
first-page rows: 50
first-page complete 1X2 rows: 50
first-page rows dated 2026-08-04: 15
first-page rows dated 2026-08-05: 12
```

The local Bzzoiro capture cache also held target-date data:

```text
2026-08-05 cache rows: 20
unique event IDs: 12
rows with 1X2, OU 2.5, and BTTS fields: 20 each
```

However, `edgefactory.sources.bzzoiro.fetch_day(date)` intentionally returns
all upcoming snapshot rows **only when `date == today`** and returns `[]` for a
tomorrow target. `picks_today.fetch_all(target_date)` calls that live adapter
rather than reading the existing date-filtered capture cache. Therefore Bzzoiro
is absent from the tomorrow forecast consensus even when the provider and cache
both contain usable tomorrow rows.

This is a confirmed **capture-forward → forecast-path wiring gap**. It is not
permission to wire cached rows into selection now. The existing Bzzoiro
`captured_at` field is the provider prediction creation time, not independently
proven local snapshot freshness; it must not be treated as the future bridge's
freshness receipt.

### BetClan finding — published today, unavailable tomorrow at probe time

```text
today listing:    153,450 bytes; 64 legacy detail links;
                  a 3-detail sample yielded 2 usable 1X2 rows.
tomorrow listing: empty response at probe time.
```

This does not prove a parser failure. The today page still matched the current
listing/detail structure. Treat the empty tomorrow page as an observed
publication/endpoint availability condition until repeat evidence proves
otherwise; never silently convert it to zero confidence or a failed vote.

### Locked conclusion

```text
SOURCE FUNNEL STATUS: OBSERVED GAP — NO PRODUCTION CHANGE
```

- No source weight, `SOURCES_*` list, threshold, calibration, registry,
  capture, selection, push, or price-quarantine change is permitted before the
  11 August review.
- Do not add a synthetic consensus vote from a cache row or use a source merely
  to inflate source count.
- Do not call Bzzoiro cache data fresh based only on its current `captured_at`
  value.

### 2026-08-11 source-funnel decision gate

Before any OddsPapi research packet, choose exactly one outcome:

```text
A. HOLD
   Keep the current source path unchanged if the Bzzoiro bridge cannot prove
   target-date identity, snapshot timing, and no-look-ahead behavior, or if
   BetClan remains unpublished for the relevant target date.

B. BUILD A REVIEW-ONLY SOURCE-FUNNEL PACKET
   Permitted only after reproduced read-only evidence. It may add durable
   source-stage telemetry and a strictly date-filtered Bzzoiro research bridge.
   It must not affect sources_used, edge thresholds, weights, selection,
   certification, prices, Actions, or WhatsApp.

C. PRODUCTION SOURCE EXPANSION
   Not an available outcome on 2026-08-11.
```

Any later source-funnel packet must prove with offline tests and fresh-tree
rehearsal:

1. source role is explicit (`inventory`, `capture`, `voter`, `shadow`,
   `archive`, or `price adapter`);
2. each stage is separately recorded: configured → fetched → raw rows → valid
   market rows → exact fixture overlap → consensus use → final pick use;
3. Bzzoiro rows are constrained to the target event date and an auditable
   as-of/snapshot record, with no future-data leakage;
4. empty/unpublished BetClan pages are visibly reported, never treated as a
   neutral vote;
5. no source-count increase can manufacture consensus, price confidence, a
   recommendation, or a push.

---

## Integrity hotfix — late result refresh + complete official ledger audit (2026-08-05)

**Freeze exception:** this repairs result freshness and performance-audit
completeness. It changes no market, source voter, probability, calibration,
price, certification, selection, or notification policy.

### Trigger and source-level proof

The 2026-08-05 rolling audit reported 92 settled rows and zero unmatched rows,
but that was only the immutable morning baseline. On 2026-08-04:

```text
picks_morning_2026-08-04.json (immutable baseline): 2 rows
picks_2026-08-04.json (accumulated official ledger): 5 rows
late official rows omitted from previous audit:        3 rows
```

Two omitted rows already had exact facts in `settled_results.json`:

```text
BG Pathum United 1-3 Aston Villa
Newport County 1-4 Roma
```

The third omitted row was `Carabobo FC vs Trujillanos FC`. At 07:35 SAST the
bot-owned overlay still lacked it, but a bounded read-only re-fetch of the
**existing** result donors immediately returned the same final score from
multiple sources:

```text
Forebet:        Carabobo 2-0 Trujillanos FC (FT)
Zulubet:        Carabobo FC 2-0 Trujillanos FC
Statarea:       Carabobo FC 2-0 Trujillanos FC
BettingClosed:  Carabobo FC 2-0 Trujillanos
Vitibet:        fixture marked finished but score fields blank
ScoutingStats:  no fixture row in this sample
```

This proved the issue was **not** a missing external result or a reason to add
a manual score. It was a capture-cadence gap: after the morning heavy capture,
`daily.py` intraday mode ran `backfill_results` only against already-cached
donor rows. It did not re-fetch the completed prior-day donor pages, so late
final scores could remain absent until a later heavy capture.

### What changed

1. **Bounded result-donor refresh:** new
   `scripts/refresh_result_sources.py` re-reads only yesterday's six existing
   result-capable adapters:

   ```text
   forebet, zulubet, statarea, vitibet, scoutingstats, bettingclosed
   ```

   It persists rows with both final score fields or a positive terminal event
   status. When a cached row exists, it updates only `hs`, `gs`, optional
   half-time scores, and status. It preserves pick-time probability and odds
   fields; it never re-scores or rewrites a prediction because a result page
   has later lost its probabilities.
2. **Intraday ordering:** `daily.py` now runs this bounded refresh before
   `backfill_results` → warehouse rebuild → shared settled-results export →
   audit. The next three-hourly bot cycle can therefore settle a late-finishing
   prior-day fixture without a D30 all-source capture.
3. **Complete official settlement ledger:** `audit_recent_picks.py` now begins
   with `picks_morning_YYYY-MM-DD.json` and admits new rows from
   `picks_YYYY-MM-DD.json` only when the latter is a payload-identical superset
   of every morning row. This includes legitimate intraday official additions
   while rejecting forecast-overwritten/mutated ledgers fail-closed.
4. **Scope receipts:** rolling JSON and Markdown now display morning-baseline
   rows, verified official late-slate additions, legacy regular-only rows, and
   unsafe regular ledgers ignored. `picks_YYYY-MM-DD.txt` remains a frozen
   pre-match presentation report, never a mutable results ledger.

### Invariants pinned by tests

```text
late donor refresh preserves pick-time probabilities while adding final scores
source refresh failure is visible and does not abort the entire donor batch
autonomous intraday refresh targets yesterday only
morning baseline + payload-identical late additions → audited once
forecast-mutated regular ledger → additions rejected
same-day audit exclusion → unchanged
```

### Boundary and expected receipt

No manual final-score override, new external result source, source vote,
source weight, market logic, odds path, or bot-owned `localdata/` file was
hand-edited. The next bot intraday run should emit a bounded result-refresh
receipt, export Carabobo 2-0 through the normal shared facts path, and make the
August 4 audit include all five official rows. If it does not, inspect the
refresh receipt before changing result logic again.

---

## Integrity hotfix — terminal event dispositions are not missing results (2026-08-05)

**Freeze exception:** this repairs audit classification only. It changes no
source voting, prediction, market selection, calibration, price, certification,
push, or notification rule.

### Trigger and evidence

After late official picks began entering the audit, three old rows were honestly
visible as scoreless:

```text
2026-07-19  FC Levadia Tallinn vs Tammeka
2026-07-25  Coquimbo Unido vs Universidad de Concepcion
2026-07-26  Super Nova vs Riga
```

The operator supplied corresponding SofaScore event pages. Each page reported
`Postponed`; these fixtures were never played on their original dates. They are
not losses, wins, draws, or ordinary `unmatched_result` rows.

A bounded re-fetch of existing sources showed why a score-only audit cannot
solve this alone:

```text
Super Nova vs Riga:
  Forebet = Postp. (positive terminal source evidence)

FC Levadia Tallinn vs Tammeka:
  Zulubet kept a scoreless fixture but supplied no usable status;
  other sampled result donors had no exact row.

Coquimbo Unido vs Universidad de Concepcion:
  Vitibet retained status=scheduled after the original date;
  other sampled result donors had no exact row.
```

Thus existing sources can sometimes detect postponement, but missing rows and
stale `scheduled` labels are not affirmative terminal evidence. A missing score
must never be automatically called postponed.

### What changed

1. **Explicit disposition vocabulary:** pure settlement helpers classify only
   positive source status evidence into `POSTPONED`, `CANCELLED`, or
   `ABANDONED`. Blank, scheduled, live, suspended, and generic missing-score
   states remain non-terminal.
2. **Result-refresh preservation:** `refresh_result_sources.py` now persists
   positive terminal no-score statuses as well as final scores, while preserving
   pick-time probabilities and odds. It reports separate `scored=` and
   `terminal_status=` counts.
3. **Exact-only disposition audit:** `audit_recent_picks.py` reads terminal
   status evidence from existing raw warehouse source views and applies it only
   through exact normalized team-pair/alias candidates. There is no fuzzy
   postponed/cancelled match: a false void is worse than a pending row.
4. **Reviewed exception facts:**
   `Config/verified_event_dispositions.json` records the three independently
   verified postponed original fixtures whose current source status evidence is
   absent or stale. This is audit-only. It contains no scores, odds, or source
   votes.
5. **Score precedence:** any exact final score always wins over a disposition.
   If a fixture eventually has a same-date result, it settles normally; a
   disposition cannot erase a real score.
6. **Honest report surface:** rolling JSON and Markdown now separate:

   ```text
   settled picks
   voided postponed/cancelled/abandoned events
   pending/unmatched result picks
   ambiguous event-disposition rows
   ```

   Voided events remain visible in `## Event Disposition / Void Audit` but are
   excluded from win/loss/ROI and calibration denominators.

### Rescheduling doctrine

A prediction recorded for an original postponed kickoff is **voided by default**.
It must not inherit a later rescheduled score merely because teams eventually
meet again. Reusing an original prediction after a reschedule requires a future
explicit event-ID continuity and as-of-time policy; none is assumed here.

### Invariants pinned by tests

```text
Postp. / Postponed → POSTPONED
Cancelled / Abandoned → terminal disposition
scheduled / live / blank → not terminal
exact terminal disposition → void, not win/loss/unmatched
same-fixture final score + disposition → final score wins
source-status terminal evidence is recognised
fuzzy disposition matching is absent by design
same-day exclusion remains unchanged
```

### Boundary

No external status scraper was introduced, no private browser endpoint was
reverse engineered, and no source was promoted. The small verified-disposition
ledger is transparent evidence for already-confirmed event facts; it is not a
substitute for source coverage. This closes the false `unmatched_result`
classification while preserving unknown/pending rows honestly for later source
coverage review.

---

## Addendum 27 — Veto re-mine resolution overlay: shadow accrual + pre-committed decision rule (2026-08-05)

**No production behavior change.** The overlay ships flag-gated OFF
(`EDGE_FACTORY_VETO_RESOLUTION=1` to activate) and shadow-logs `resolution_*`
fields on every pick's ctx from deploy (flag OFF = log only, no verdict or
bucket change). Shipped in `31f47ab`: `src/edgefactory/veto_resolution.py`
(pure O1 rule-pooled league + O2 niche → competition_type ladder; Scenario B
gates ALLOW≥40 / CAUTION≥20 / VETO≥12), `scripts/picks_today.py` (+14 lines),
corrected `scripts/counterfactual_veto_resolution.py` (now prints the
pre-committed gate checklist), `tests/test_veto_resolution.py`.

### Honest Phase-0 evidence (corrected 2026-08-05)

- In-scope = league-UNKNOWN picks ONLY. 17 of 20 bucket picks are in scope;
  3 (Qarabag, SC Braga, Austria Vienna) are short-sniper niche-UNKNOWN blocks
  with league already resolved — OUT of scope by design.
- In-scope: 17/17 resolved (2 O1-pool: 1 BOOST + 1 VETO correctly blocked;
  15 O2-competition_type CAUTION). Caution-grade: 16 would-play, 15 settled,
  13 wins, 86.7%, would-be ROI **+0.042**.
- The 3 out-of-scope picks ALL WON (would-be +0.167) and stay watchlisted —
  a separate **short-sniper niche-UNKNOWN policy question, independent of the
  league overlay** (not gated on it; investigate in parallel).
- Comparison: the audit's WATCHLIST_UNKNOWN_CTX bucket (the watchlist the
  overlay would replace) shows 19 settled / 17 wins / **+0.061** would-be ROI.
  The overlay captures only the in-scope subset (+0.042) and leaves the
  higher-ROI out-of-scope subset unplayed. **Net: current thin evidence mildly
  favors NOT shipping** — the overlay selects the weaker half of the watchlist.
  The gate exists to find out whether that gap persists or reverses.
- **Green-light (ALLOW/BOOST) is N/A as an evidence category:** no in-scope
  green-light picks with settled outcomes; the overlay is caution-grade-only
  in practice. The harness prints this note automatically.

### Pre-committed decision rule (write-down-now, anti-mood)

Checkpoint = re-run `scripts/counterfactual_veto_resolution.py`; the report
prints the gate checklist mechanically. Thresholds are fixed and must not be
changed while the gate accrues.

- **FLAG-ON requires ALL:** (1) ≥30 settled in-scope caution-grade picks;
  (2) overlay would-be ROI > 0 AND ≥ bucket ROI − 1pp over the same window;
  (3) overlay hit-rate 90% Wilson lower bound ≥ bucket hit rate − 5pp.
- **FLAG-OFF (keep shadow, keep waiting):** any condition fails at a
  checkpoint.
- **DEPRECATE:** at ≥60 settled, if overlay ROI < bucket ROI − 2pp at two
  consecutive checkpoints (≥2 weeks apart), retire the overlay (flag stays
  OFF, code stays, decision recorded here). Prevents shadow limbo.

### Timeline (be honest)

- First shadow-data read (`resolution_*` present in archived picks): 2–3 bot
  cycles (days).
- 30-settled gate: ~6–9 weeks at the observed accrual rate (~0.5 in-scope
  settled/day).

### Two flag-gated overlays — interaction stated

- `EDGE_FACTORY_ENGINE_AWARE_DEBIAS` (`6ccb18f`): engine/market-level, applies
  at 🔥 note construction (probability damp).
- `EDGE_FACTORY_VETO_RESOLUTION` (`31f47ab`): context-level, applies at the
  ctx → bucket stage.
- Different pipeline stages → no conflict by construction; both OFF; both log
  per-pick. If a third overlay is proposed, document interaction semantics
  before shipping.

### Addendum 27.1 — gate refinements (2026-08-05, recorded while numbers are fresh)

- **Threshold rationale (why 1pp / 5pp):** G2 epsilon 1pp is small vs the
  typical ROI scale (±0.05–0.2) and compares overlay vs bucket over the SAME
  window (both are noisy small samples; not absolute performance). G3 epsilon
  5pp is deliberately generous so small n is not punished; the 90% Wilson LB
  tightens as n grows, so G3 is meaningful only near n=30. Both thresholds
  are fixed and must not be changed while the gate accrues.
- **Small-n honesty:** today's G2/G3 FAIL at n=15 is an insufficient-data
  state, NOT a verdict on the overlay — the bucket comparison itself is a
  19-pick sample. The gate becomes decisive at n≥30. The harness prints this
  note on every run.
- **Deprecation trigger (defined):** at n≥60 settled with G2 AND G3 still
  failing and overlay ROI < bucket ROI − 2pp, confirm at a second checkpoint
  ≥2 weeks apart; if the gap persists, retire the overlay (flag stays OFF,
  code stays as audit record, decision recorded in HANDOVER).
- **Two-overlay interaction (explicit):** debias (`6ccb18f`) operates at
  engine×market level (🔥 note construction); veto (`31f47ab`) at context
  level (ctx → bucket). They gate on independent counters, so **debias going
  live does not affect the veto gate's settled-outcome counter**: the veto
  counter counts picks that were WATCHLIST_UNKNOWN_CTX at the time they were
  made, which debias (probability damp at note stage) cannot change.
- **First shadow-data read (concrete):** after the next bot runs, check
  `localdata/picks_2026-08-06.json` (or the newest archived pick ledger):
  ```bash
  python3 -c "import json,collections; d=json.load(open('localdata/picks_2026-08-06.json')); print(collections.Counter(str(p.get('ctx',{}).get('resolution_verdict')) for p in d))"
  ```
  Expected: a small dict (e.g. `Counter({'UNKNOWN': …})` — every pick's ctx
  carries `resolution_*` fields; no pick is changed while the flag is OFF).
  Paste that output for the first accrual read.

### Addendum 27.2 — gate scope clarifications (2026-08-05)

- **Deprecation applies to SHADOW state only.** The pre-committed deprecation
  trigger (n≥60, G2 AND G3 failing, ROI gap ≥2pp across two checkpoints ≥2
  weeks apart) governs the overlay while it is OFF. If the overlay ever ships
  FLAG-ON, deprecation is moot: a live overlay gets its own lifecycle —
  measured walk-forward like any live feature, and reversible by turning the
  flag back OFF if its realized performance fails the same G2/G3 standard.
- **Cohort comparability (two-overlay interplay, subtler case):** if the
  engine-aware debias overlay ships first and changes which picks surface
  (probability damp at the 🔥 note stage), the *population* of future
  WATCHLIST_UNKNOWN_CTX picks could shift — debias does not corrupt the veto
  counter (it still counts picks that were WATCHLIST_UNKNOWN_CTX at the time
  they were made), but the n≥30 cohort may not be perfectly comparable to the
  n=15 cohort measured today. To keep the gate honest, each checkpoint
  records cohort composition alongside the gate numbers: resolved/unresolved
  shares and the O1-pool vs O2 fallback mix. If the composition shifts
  materially after debias ships, note it in the checkpoint before interpreting
  G2/G3.


### Addendum 27.3 — Addendum 19 queue status + pre-observation checklist (2026-08-05)

Status of the Addendum 19 work queue, so the next reader does not redo or
misread it:

1. **Debias wiring (engine-aware)** — DONE as a flag-gated-off payload
   (`6ccb18f`); awaiting `by_engine_by_market` evidence (activation criteria:
   4 recommendation markets at n>=5, or the 08-07/08 pooled read).
2. **Veto re-mine** — design decisions + Phase-0 counterfactual harness +
   flag-gated-off resolution overlay shipped (`31f47ab`, `d97165e`,
   `1ef4d07`, `d5fe735`); decision rule pre-committed (Addenda 27/27.1/27.2);
   awaiting n>=30 settled gate (~6-9 weeks).
3. **Small tickets** — (a) BENCHED time-bomb test: FIXED in `5fcc6a6`
   (evaluation-date injection + pinned + regression tests; no action needed);
   (b) winner's-curse doc: still open.

Still open (non-urgent): winner's-curse doc; cosmetic pyflakes landmines +
`credits_month` wording; Vitibet standalone certification (accrues);
team-alias fragility (only if live-book odds become priority); calibration
shrinkage. **Calendar-fixed, do not run early:** 2026-08-11 OddsPapi review
runbook + source-funnel A/B/C gate (locked through 08-10).

The design working notes were removed per the single-source-of-truth rule;
the decisions, gate, and verification evidence are recorded here in Addenda
27 through 27.4.


### Addendum 27.4 — second-agent cross-check table (preserved 2026-08-05)

The independent second-agent review's decision-relevant numbers were
recomputed from the live repo. This table is the verification evidence for
the claim "the five decisions are supported despite three secondary items
being inaccurate or unreproducible." It was originally in the design working
notes; preserved here per the single-source-of-truth rule.

| # | Claim (from review) | Independent recompute | Status |
| --- | --- | --- | --- |
| 1 | League UNKNOWN 3,176 / team 19,340 (vs prompt-context 3,175 / 19,346) | recomputed: 3,176 / 19,340 | OK — agent correct; prompt context stale by 1 / 6 (bot regen drift) |
| 2 | settled_results 38,958 rows, 2026-05-07 to 2026-08-04; last-30d 11,375 | identical | OK |
| 3 | competition_type: 15 cells, 2 UNKNOWN | identical | OK |
| 4 | competition_type n range 280-1708 | actual 1-27364; the 2 UNKNOWN cells are youth n=1 and n=4 | WARN - n-range inaccurate; conclusion unaffected (2 tiny youth cells resolve nothing) |
| 5 | epl\|1x2\|home: 13 rules, 5 neg / 8 pos, w_roi -0.0388 | identical | OK |
| 6 | it1\|1x2\|home: 13 rules all negative, w_roi -0.1141 | identical | OK |
| 7 | es1\|1x2\|home: all 13 positive | actual 11 pos / 2 neg (consensus rules -0.042/-0.040), w_roi +0.0179 | WARN - minor; qualitative point (strong positive pool) holds |
| 8 | Q3 scenario cell resolutions A 2304 / B 1985 / C 1937 | recomputed 2301 / 1982 / 1934 (within 3 cells) | OK |
| 9 | Q3 pool verdict mixes (A 653 = 350 VETO+199 ALLOW+68 CAUTION+36 BOOST; B 539; C 521) | recomputed A 652 = 350 VETO+198 ALLOW+68 CAUTION+36 BOOST; B 538; C 520 | OK - within 1 pool; VETO=350 exact |
| 10 | UNKNOWN cells in pools with pooled n<12 = 797 (25.1%) | identical | OK |
| 11 | Pool n-bucket distribution (n>=12: 188; >=20: 180; >=40: 160; >=100: 103) | not reproducible under any tested definition (counts 353-674 by definition; priced-n>=12 = 663) | FAIL - unverifiable; do NOT quote; the harness computes its own canonical pool table |

Verdict: the five decisions (Q1-Q5) are supported; three secondary evidence
items are inaccurate or unreproducible; none change a decision. Re-verified
2026-08-05 on registry 36,508 cells / 3,182 league-UNKNOWN: harness still
reproduces 17 resolved / 15 settled / 13 wins / +0.042 / FLAG-OFF.

### Addendum 27.5 — debias degeneracy observed live: 6/6 btts_yes (2026-08-05)

**Symptom (operator-reported):** on 2026-08-05 every pick's recommended
enhancement was `btts_yes` (6/6). This is not normal selection variety:
2026-07-29 → 08-04 the ledgers showed a healthy mix (`match_over_15`,
`match_over_25`, `goal_range_2_3`, `away_under_35/45`, `btts_yes`).

**Mechanism (verified in code + data):** with the engine-aware debias flag
OFF, `load_rolling_audit_hit_rates()` reads the tiny recommendation overlay
(`enhancements_audit.by_enhancement`, gate recommended>=5, n=5-9) and damps:

- `match_over_15` x0.857 (n=7) — drops raw ~0.82 to ~0.70, below the 0.80 bar -> EXCLUDED
- `match_over_25` x0.556 (n=9) — Spartak raw 0.65 -> 0.361, above display bar but below the 0.45 tier-6 bar -> demoted
- `goal_range_2_3` x0.222 (n=9) — crushed
- `btts_yes` hr=1.0 (n=3, never damped) — the only market left standing above its tier bar

Result: the damp table rotates recommendations to whichever market it does
not damp. This is the F2 red-team finding (overlay too thin to trust) now
visible as a production symptom. Impact is cosmetic (enhancements are PAPER
state — not certified, not staked, not pushed) but the recommendation
surface is uninformative while it persists.

**Flag-ON simulation (verified on the 6 real picks):** engine-aware debias
returns hr=1.0 for hybrid notes when no hybrid cell has n>=5 (the "no damp
without evidence" fallback — all hybrid cells are currently n<5). Under that
resolver, the three picks with stored `match_over_25` raw (Spartak 0.650,
Panathinaikos 0.646, Fenerbahce 0.677) provably flip away from `btts_yes` to
the over-market (tier 6 beats tier 4). The other three (Lazio, Napoli,
Arsenal) have no stored over-market raw (they were excluded by the old damp),
so their flag-ON outcome is projection, not measurement.

**Blind-spot correction (second-agent review):** an earlier simulation only
re-scored markets that SURVIVED the old damp (i.e. those present in
`event_notes`), so `match_over_15` — damped out of all 6 — was invisible to
it and could re-enter and win under the flag. The honest statement is: flag
ON breaks 6/6 with certainty; the exact split (match_over_15 vs
match_over_25) needs a live shadow run to measure.

**Decision (unchanged):** do NOT flip the flag yet. The pre-committed
activation criteria are unmet (hybrid cells n>=5, or the 08-07/08 pooled
read). This symptom is the canary: at activation, the shadow comparison
(multiple runs, flag OFF vs ON, diff the recommendation distributions) is
the definitive test. Record the before (6/6 btts_yes) and expect the after
to diversify toward over-markets where the Poisson totals are strong.

### Addendum 27.6 — enhancement prices wired to the real odds source (theoddsapi btts) (2026-08-05)

**Trigger:** the 6/6 btts_yes canary (Addendum 27.5) plus Addendum 11's
finding that the enhancement surface is EV-negative at hard-coded estimates
(match_over_15 EV -48%, match_over_25 EV -14%). The enhancement overlay was
recommending by probability with either hard-coded estimated odds
(get_combo_odds) or no price at all, and the enhancement registry could not
advance (SHADOW -> PAPER -> ELIGIBLE requires real priced outcomes).

**What changed (5 files, +54/-5):** the theoddsapi capture default markets
now include `btts` (was `h2h,totals`):
- `src/edgefactory/sources/theoddsapi.py` — MARKETS default
  `"h2h,totals,btts"` (env `ODDS_API_MARKETS` still overrides);
- `.github/workflows/daily.yml` — env default `'h2h,totals,btts'`;
- `.env.example` — same;
- `scripts/capture_theodds.py` — self-test payload + assertions now cover
  btts yes/no parsing;
- `tests/test_theoddsapi.py` — +2 tests: btts rows parsed from payload
  (unified schema), and the default MARKETS includes btts (pins the wiring).

The parser already supported btts (rows_from_event_odds) and the enhancement
pricing join already reads the theoddsapi store (enh_pricing v2, merged
theoddsapi + bzzoiro + scoutingstats, best-price with source attribution).
The only gap was the capture not requesting the market — so btts_yes/btts_no
recommendations now get REAL captured odds through the existing pipeline.
Hard-coded estimates remain only as a display fallback for markets with no
real capture (goal ranges, exacts, team totals per the 08-03 probe) — and
never for certification: the enhancement registry only advances on real
priced outcomes.

**Walk-forward only — no retrospective validation.** The theoddsapi capture
began 2026-08-03 and btts was never requested before this change; there is
NO historical data for enhancement-market odds. Per the operator's direction
and the repo's walk-forward golden rule, we do NOT backtest enhancement EV
on estimates. Validation proceeds strictly forward through the existing
enhancement registry gate (per-market Wilson LB95 >= breakeven at REAL
captured odds on n>=30, HANDOVER:1824): first btts rows land in the odds
store on the next capture; priced btts outcomes start accruing in the
registry from the next audits; SHADOW -> PAPER -> ELIGIBLE only on real
priced evidence.

**Budget:** markets 2 -> 3 on region eu = +50% credit cost per event
(~3 credits/event); ODDS_API_MONTHLY_BUDGET (480) unchanged; usage.json
tracks spend. If budget becomes tight, `btts` can be dropped via the env
knob without code change.


### Addendum 27.7 — OPERATOR OVERRIDE: OddsPapi lock superseded; OddsPapi wired as an enhancement price source (2026-08-05)

**Authority:** the operator explicitly overruled the OddsPapi locked period
(2026-08-04 -> 2026-08-10) on 2026-08-05. This addendum supersedes the lock
text above and records what the override authorizes. The operator is the
ultimate authority on this system; this is a deliberate, recorded decision.

**What the lock was protecting:** preserving the 08-11 by-engine /
calibration / debias observation window, and keeping OddsPapi out of
production paths until research gates passed. Those concerns are retained
where they still make sense (below) — what changed is that read-only
**price capture for the enhancement overlay** is now authorized.

**What is authorized now:**
- OddsPapi is wired as a real price source for enhancement markets the
  other feeds do not price: team totals (home/away over/under 0.5/1.5/2.5/
  3.5/4.5), double chance (1X/X2/12), totals lines (ou_1.5/3.5/4.5), btts,
  plus 1x2 — parsed from the OddsPapi market-id vocabulary confirmed by the
  2026-08-04 live probe.
- Capture writes the unified schema to `localdata/oddspapi_odds_YYYY-MM.csv.gz`
  (same shape as theoddsapi/bzzoiro stores) and `enh_pricing` merges it as a
  4th source (best price across sources, source attribution, divergence
  record). The `synthetic/none` cells of the enhancement market table are
  replaced by REAL captured prices.
- The enhancement registry advances only on real priced outcomes (walk
  forward), exactly as before — OddsPapi prices are real prices, not
  estimates, so they feed the Wilson-LB95-vs-breakeven gate like any other
  source.

**Retained safety rails (operator-approved, not a lock):**
- Flag-gated OFF by default: `EDGE_FACTORY_ODDSPAPI_PRICES=1` to activate
  capture into daily/capture paths; shadow/walk-forward accrual first.
- `ODDSPAPI_API_KEYS` stays local in `.env` only — never in Actions, tracked
  files, logs, or chat (unchanged; the keys are the operator's own).
- No selection, certification, source-weight, or push change from OddsPapi —
  it is a price source for the enhancement overlay only.
- Free-tier quota is small: capture is bounded (unmatched same-day picks
  first, then enhancement-relevant fixtures), fail-soft, and never broad
  polls.
- Walk-forward only — no retrospective validation; the odds store only
  accumulates from activation forward.

### Addendum 27.8 — OddsPapi multi-market capture: provider line-shape limitation (2026-08-05)

**Finding (verified from the live payloads, 2026-08-05):** the OddsPapi odds
response carries NO market line for totals/team-totals markets. The market
object has only `bookmakerMarketId` + `marketActive` + `outcomes`; the outcome
has `bookmakerOutcomeId`, `price`, `priceAmerican`, `priceFractional`,
`mainLine`, `playerName` (null) — but NO `name`, `line`, `point`, `handicap`,
or side. The distinct market ids (1012/1010/1014/108 = different line
markets) cannot be resolved to a line from the odds payload; the line exists
only in the provider catalog (which is coarse: "Over Under Full Time").

**Consequence:** the parser cannot emit `ou_*` / `tt_*` rows for these
markets without guessing the line — and guessing lines would silently
mis-price team totals, which is worse than not pricing them. So:
- btts and double_chance DO capture (side derivable from market label:
  "Both Teams To Score" -> yes/no; "Double Chance" -> 1X/X2/12 from the
  outcome's bookmakerOutcomeId mapping — the id carries the selection).
- totals and team_totals are SKIPPED until the provider exposes the line in
  the odds payload (or a catalog that maps id -> line). Recorded here so
  nobody "fixes" it by guessing.

**What still works:** theoddsapi totals/totals_alt/team_totals/double_chance
(default markets, real lines in the totals payload) — the enhancement
overlay is priced from theoddsapi for those; OddsPapi adds btts/dc + a
second 1x2 source. Walk-forward accrual continues.

**Status:** the multi-market OddsPapi capture is honest-but-limited: btts +
double_chance + 1x2 flow; totals/team_totals are deferred to a provider
line-shape change.

### Addendum 27.9 — Antigravity red-team review: findings + fixes (2026-08-05)

An independent hostile red-team review (base aaef2b0) found 8 issues. All
verified against the repo; fixes shipped in this commit.

| # | severity | finding (verified) | fix shipped |
| --- | --- | --- | --- |
| F1 | CRITICAL | OddsPapi prices feed `priced_outcomes -> record_outcome` -> can reach ELIGIBLE -> `⭐ Enhancement` display on pushed picks (audit_recent_picks.py:1581, picks_today.py:2550). The "PAPER-only" claim in docs was contradicted by the code path — BUT the operator override (27.7) explicitly intended OddsPapi prices to feed the registry like any other source. The REAL defect is stale/unvalidated prices corrupting the gate, which F2 fixes. | F2 + F6 (below); the registry path is by design per 27.7 |
| F2 | HIGH | `captured_at` used provider `updatedAt` (stale by days); `marketActive=False` / outcome `active=False` ignored -> dead odds ingested. | parser now stamps OUR capture time (`timezone.utc`), drops inactive markets/outcomes at the boundary |
| F3 | HIGH | `load_dotenv()` at module import (theoddsapi.py:62) -> tests pass/fail on ambient .env (hit live today). | tests/conftest.py autouse fixture strips all ODDS_API_*/EDGE_FACTORY_* knobs (hermetic suite) |
| F4 | CRITICAL | fuzzy settlement `char_ngram_similarity >= 0.40` on combined strings -> swapped fixtures (Arsenal Chelsea vs Chelsea Arsenal, 0.73) settle REVERSED outcomes. | orientation-checked matching: each pick side must match ITS result side better than the opposite side; combined >= 0.40 preserved. Legit bridges (Clarence->Hobart Zebras) still pass; swaps rejected |
| F5 | HIGH | `double_chance` draw pick -> "12" (home-or-away) = HEDGE against the draw, not an enhancement. | draw -> None (unpriced, documented); only home->1x / away->x2 |
| F6 | HIGH | `EDGE_FACTORY_ODDSPAPI_PRICES` never evaluated; enh_pricing merged the oddspapi store unconditionally ("flag-gated" was documentation-only). | REAL gate: store merged only when `EDGE_FACTORY_ODDSPAPI_PRICES=1`; stale file on disk cannot silently feed prices |
| F7 | MEDIUM | oddspapi dedupe included `captured_at` -> each run appends duplicates (theoddsapi store keeps snapshots by design; oddspapi had no such intent). | dedupe key excludes `captured_at`; only a genuinely changed price appends |
| F8 | LOW | `_classify_label` mapped "Set Winner" -> 1x2. | "set winner" added to _NON_GOAL |

Economics (verified): theoddsapi 6 markets x 1 region = 6 credits/event;
480/month budget = ~80 events/month = ~2.6/day -> n=30 per market for
ELIGIBLE ~60 days. Tight but feasible; drop markets via env knob if needed.

Remaining accepted risks (documented, not fixed): OddsPapi totals/team-totals
lines are unparseable from the payload (provider limitation, 27.8) so those
markets stay unpriced from OddsPapi; theoddsapi covers them with real lines.
Enhancement registry advancement on real priced outcomes remains the design
(operator-approved); F2+F6 are the freshness/activation controls on that path.

Test suite: 218 passed (210 + 8 new red-team regression tests).

### Addendum 27.10 — Third-pass audit (N1–N5) + corrections (2026-08-05)

An independent third-pass audit of the red-team fix commit (e27e154) found 5
items. All verified; corrections shipped in this commit.

**N1 (CRITICAL, fixed) — the F3 hermeticity fix was ineffective.** The
conftest stripped env knobs at test-SETUP, but the production modules read
env at IMPORT time (theoddsapi.py:62, bzzoiro*, db.py, capture_theodds.py)
and reload-based tests re-read .env on reload — so a per-test delenv was too
late. Demonstrated: a realistic operator .env caused 3 test failures at
e27e154. **Correct fix:** neutralize `dotenv.load_dotenv` for the whole
session in conftest BEFORE any src import, plus strip the missing knobs
(EDGE_FACTORY_LOCALDATA, ODDS_API_KEYS, ODDS_API_BASE, ODDSPAPI_API_KEYS).
Verified: 219 passed with the polluted .env PRESENT and absent.

**N2 (fixed test, behavior unchanged) — real-payload test gap.** Added a
regression test with the REAL OddsPapi shape (totals outcome has mainLine,
no name/line): asserts 1x2/btts/dc flow and totals are dropped (honest
safe-fail per 27.8), so the suite no longer gives false confidence that
totals flow from oddspapi. `_line_from` intentionally does NOT read
mainLine: even with the line, the side is unresolvable from the payload
(27.8), so totals stay skipped — the limitation is now literal, not
accidental.

**N3 (fixed) — time-bomb test.** `captured_at.startswith("2026-08")` would
fail in September 2026. Now asserts it is NOT the provider's 2020 stamp and
is within 1h of now (UTC).

**N4 (documented, operator decision) — freshness measured, not enforced.**
`captured_at` is now honest but no code rejects stale prices (captured_at is
never read for staleness). Options if the operator wants enforcement: (a)
max-age guard — skip rows older than N days vs kickoff in enh_pricing; (b)
keep measurement-only. Default: measurement-only, documented here.

**N5 (documented, operator decision) — divergence bypass for single-source
enhancements.** Divergence records only when >=2 sources price the same
selection; oddspapi-as-sole-source has no divergence record. Options: (a)
require >=2 sources for any price feeding ELIGIBLE (2-line change in
audit_recent_picks.py priced_outcomes filter); (b) accept as-is. Default:
accepted, documented here — consistent with 27.7's operator-authority
pattern.

**Operational truth (F1, restated):** OddsPapi prices feed the enhancement
registry (operator-intended, 27.7), now freshness-stamped (F2), flag-gated
(F6), and the whole suite is env-hermetic (N1). The registry advances only
on real priced outcomes at n>=30 per market.

### Addendum 27.11 — Governance calls N4 + N5 (operator-delegated, implemented 2026-08-05)

The operator delegated the two outstanding governance items (audit N4, N5) to
be decided and implemented. Decisions, rationale, and implementation:

**N4 — FRESHNESS: ENFORCE (was: measurement-only).**
`enh_pricing` now rejects OddsPapi rows captured outside
`[kickoff - ODDSPAPI_MAX_AGE_H(72h), kickoff]` at the merge. This completes
the red-team F1/F2/F6 chain: the flag gates activation, the stamp measures,
the window now enforces. The capture pipeline is same-day/next-2-days, so
nothing legitimate is dropped; post-kickoff rows are lookahead artifacts
that must never price a settled pick. Missing/unparseable timestamps fail
open (the guard must never silently kill a source on a format change).
Scoped to the oddspapi branch only (the demonstrated problem; theoddsapi/
bzzoiro/scoutingstats have different capture semantics and are untouched).

**N5 — SINGLE-SOURCE CERTIFICATION: VERIFY AT ELIGIBLE (calibrated).**
Real single-source prices keep accruing into PAPER and the Wilson math (per
Addendum 27.7 - they feed the gate unchanged), but PAPER->ELIGIBLE now
requires `ceil(n * 0.25)` of the market's outcomes priced by >=2 DISTINCT
sources (`MIN_MULTI_SOURCE_FRAC = 0.25`; 8 of 30 at the gate). Rationale:
ELIGIBLE is the only level that pushes `⭐` staking recommendations to
WhatsApp - certification without any cross-source verification was the one
red-team item with zero response. 25% is reachable (theoddsapi covers
team_totals/dc/totals/h2h; scoutingstats covers totals/btts) while being a
real signal: a market with systematic single-source mispricing cannot
fabricate 8 cross-verified outcomes. Unverified markets cap at PAPER with a
transparent `status_reason` (never silently stalled). Key semantic: two
AGREEING sources count as verified even without a divergence flag (the
divergence record is about disagreement, not verification) - surfaced as
`enhancement_multi_source` on every priced pick and threaded through
`priced_outcomes -> record_outcome(multi_source=...)`.

**Verified (fresh tree at 9964662):** 223 passed (219 + 4 new: 1 freshness,
3 verification-floor) in BOTH clean and polluted-.env environments;
pyflakes clean. End-to-end sim: identical Wilson evidence (30/30 @1.50) ->
single-source-only market stays PAPER ("multi-source verification 0/8 not
met"), 8/30 multi-source -> ELIGIBLE ("multi-source 8/8").

**Compatibility:** existing `enhancement_registry.json` is additive-compatible
(`multi_n` defaults 0 -> existing markets stay PAPER until verification
accrues; already-ELIGIBLE markets are unaffected - the floor gates the
PAPER->ELIGIBLE transition only, non-regressive). No migration needed.

**Constants (reviewable in the diff, changeable by operator):**
`ODDSPAPI_MAX_AGE_H = 72` (enh_pricing.py),
`MIN_MULTI_SOURCE_FRAC = 0.25` (enh_registry.py).

### Addendum 27.12 — Evidence on all buckets: forecast archive for odds capture (2026-08-05)

**Trigger (operator):** "we need evidence on all buckets." The audit's best
ROI bucket is SKIPPED_VETO (71 settled / 60 wins / +9.2% in the 30-day
window), but on veto-only days no enhancement prices were captured, so the
registry never accrued evidence on it.

**Finding (verified):** the odds-capture shortlist
(`src/edgefactory/sources/theoddsapi.py shortlist()`) ALREADY includes ALL
buckets — it reads every pick from the frozen per-day archive
(`picks_{date}.json`), with no bucket filter. The real gap was that
`picks_today.py` (run directly) only wrote `picks_today.json`, never a
date-stamped archive, so a manual forecast for tomorrow produced no
`picks_2026-08-06.json` for the shortlist to read — `shortlist=0`, no
capture, no prices, no registry accrual.

**Fix (this commit):** `picks_today.py` now writes a frozen per-day archive
`localdata/picks_{day}.json` for EVERY processed day (matching the archive
shape daily.py writes; overwrites with the freshest run). The capture
shortlist therefore sees tomorrow's fixtures — including vetoed-but-clean
matches — and prices them, so the enhancement registry accrues real priced
evidence on ALL buckets, not just playable ones.

**Verified:** 224 passed (223 + 1 new shortlist test pinning that a
SKIPPED_VETO pick is in the shortlist) in clean AND polluted-.env; pyflakes
findings pre-existing only (verified by base diff).

### Addendum 27.13 — League resolution: wrong-competition fix + UEFA coverage (2026-08-05)

**Trigger (operator):** with the all-buckets archive live (27.12), capture for
2026-08-06 found the shortlist fixture but reported
`Paide vs Rapid Vienna (no event in soccer_england_league2)` — a UECL
qualifier resolving to England League 2.

**Finding (verified against all 112 distinct league labels in the archived
picks):** `sport_key_for_league` was fabricating wrong-competition
resolutions at scale. The provider's off-season sports list has no
UECL/UEL/UCL-main keys, so the alias loop missed and the containment
fallback matched junk: `_norm_league` strips digits, reducing the title
"League 2" to a 6-char "league" token that substring-hit every
"...League" label; ties sorted lexically, so `soccer_england_league2`
absorbed **13 archived labels** (all UEFA comps, Belarus/Bulgaria Premier,
Scotland League Cup, Kuwait Premier League, Uzbekistan Super League...).
Same class: "Kuwait ... Championship Round" -> `soccer_efl_champ`, and the
"argentinaprimera" fragment mislabelled "Argentina Primera B Metropolitana"
onto the top-tier key. Tier digits were destroyed before matching
("Se2"/"Se4" indistinguishable; "K League 2" inheritable by K League 1).
Provenance rule: wrong competition is worse than unpriced.

**Fix (this commit), `src/edgefactory/sources/theoddsapi.py`:**
1. Aliases become CHAINS checked longest-first; first provider-listed key
   wins (UCL falls back to `soccer_uefa_champs_league_qualification` during
   the qualifying window — qualifiers price TODAY). First matching fragment
   wins-or-returns-None: no fallthrough, so a second-tier label can never
   inherit its top tier's key. Tightened `argentinaprimera` ->
   `argentinaprimeradivisin`; added UECL/UEL-main, Spain Segunda guard,
   Germany Bundesliga 2 / France Ligue 2 / Brazil Serie B tier guards,
   England League One/Two, Scotland Premiership, Chile Primera, Czech Liga.
2. All matching runs on a digit-preserving `_league_code` (the tier lives
   in the digit): exact short codes (`UCL`/`UEL`/`ECL`/`Fi1`/`Se2`/`Ie1`)
   added as an exact-match table.
3. Containment fallback now requires real overlap: >= 8 chars AND >= half
   the longer string. The 6-char "league" token can no longer carry a
   resolution; legit containment (Finland/Mexico/Denmark/Poland/Switzerland)
   verified unchanged.
4. `fetch_fixtures` performs one free `/sports` refresh when any fixture's
   league doesn't resolve on the cached list — comp availability swaps at
   season boundaries faster than the 7-day cache rolls (never fatal, 0
   credits; stale-cache misses heal on the next capture run).

**Result (112-label acceptance table):** 13 -> 0 wrong-competition
resolutions; UCL qualifiers now resolve correctly; Scotland Premiership,
Chile Primera, Fi1/Ie1/Se2 codes gained. Wl1/Bg1/Kr2 remain honest None —
genuinely not sold by The Odds API; no code change can price them from this
source.

**Verified:** 229 passed (224 + 5: never-wrong-competition, UEFA chains
follow listing, short codes exact & tier-preserving, containment overlap
floor, stale-cache refresh heal); pyflakes findings pre-existing only
(verified by base diff).

**Residual (honest):** verbose second-tier labels for covered top-tier
leagues not yet observed in archives resolve via the digit-preserving
fallback (structurally safe), but new provider short codes should be added
to SHORT_LEAGUE_KEYS as they appear in captures; the capture `--dry-run`
output shows each fixture's resolution and is the audit surface for this.

### Addendum 27.14 — Veto deep dive: interrogating the flagship number (2026-08-05)

**Trigger (operator):** "what would you do next" — answer: before any pilot is
discussed, verify the one number that would change what we stake. The rolling
audit (2026-07-07 -> 2026-08-05) shows SKIPPED_VETO at 71 settled / 60 wins /
+9.18% ROI while the staked CAUTION bucket sits at -12.3% over 33 — the
system's best bucket is the one it refuses to play. A blended figure cannot
steer policy until its composition is known.

**Anti-pattern guarded:** this must NOT be a side computation with its own
settlement path. The deep dive groups the SAME settled rows that feed
`by_bucket` (one `settled_pairs` append in the existing loop), so the deep
dive and the bucket table can never disagree.

**This commit (`scripts/audit_recent_picks.py`):**
- New `veto_deep_dive` report section: SKIPPED_VETO cross-cut by
  `price_evidence`, odds band (<1.50 / 1.50-2.00 / 2.00-3.00 / >=3.00 /
  unpriced), and `veto_reason` (archived top-level field; older archives read
  as UNRECORDED — evidence is never silently dropped), plus
  `trusted_evidence_only` / `soft_evidence_only` splits (soft labels:
  SUSPECT_ALIAS_FUZZY, SCOUTINGSTATS_SOLE, UNMATCHED, SOURCE_FALLBACK) and a
  CAUTION contrast cut.
- Markdown: "Veto Deep Dive" section in picks_audit_{end}.md; console: main()
  prints the headline (overall vs trusted vs soft) plus per-odds-band rows on
  every audit run.
- No new I/O, no warehouse behaviour change, no settlement-path change.

**Verified:** 230 passed (229 + 1 deep-dive test pinning composition, band
ordering, UNRECORDED survival and the CAUTION contrast); pyflakes clean on
both touched files (base diff).

**The read it enables (next run of audit_recent_picks.py):**
- trusted-only ROI positive across bands -> veto miscalibrated -> pilot spec
  targets a veto-exception bucket (Addendum 27.15).
- ROI carried by soft evidence / tiny-odds bands -> veto probably right; the
  audit layer's own provenance is the thing to fix next.

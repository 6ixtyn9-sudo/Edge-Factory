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
must read "Match Over 1.5 Goals" / "Match Over 2.5 Goals" /
"Both Teams to Score - Yes (BTTS-Yes)" with the SAME icons and expected % —
pasted back as gate G4.

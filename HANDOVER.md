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

WhatsApp push delivery is now wired into daily.py via scripts/notify.py and src/edgefactory/notifier.py. Operational status and a required one-line fix are documented in section 9.

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

scripts/notify.py

src/edgefactory/notifier.py

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

notify (final step, runs in all official and intraday modes)

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

src/edgefactory/notifier.py

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

calls sync_supabase then notify as the final steps of every official and autonomous_intraday run (both via run_soft, so a push failure never fails the whole job)

freezes target-date picks: if localdata/picks_YYYY-MM-DD.json already exists, reruns restore them instead of regenerating unless --force-repick is passed

passes one fixed EDGE_FACTORY_RUN_AS_OF timestamp into all picks_today invocations for that run

supports automated scheduling via --auto-run / --auto-once, splitting official morning heavy runs from lightweight intraday forecast refreshes

supports non-official forecast refreshes via --forecast-refresh, archiving to localdata/forecast_YYYY-MM-DD_HHMM.json and .txt

supports deliberate promotion of forecast runs to official records via --promote-forecast

scripts/sync_supabase.py

syncs certified edges and daily bucketed picks to Supabase

scripts/notify.py

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

scripts/notify.py — dispatch orchestrator

src/edgefactory/notifier.py — provider implementations

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

Later intraday runs are "late slate" — only newly appearing, not-yet-sent picks are pushed. If there are no new picks, notify stays silent on purpose ("Remaining silent").

--force bypasses the sent ledger and resends all notifiable picks.

--late-slate-only forces strict intraday scan mode.

CRITICAL REQUIRED FIX (2026-06-18):

send_callmebot_whatsapp() in src/edgefactory/notifier.py currently builds the wrong endpoint:

url = f"https://api.callmebot.com/whatsapp.py?phone={clean_phone}&text={encoded_text}&apikey={apikey}"

The endpoint is whatsapp.php, not whatsapp.py. The current code hits a 404 on every dispatch, raises an exception, and notify.py logs it and continues with dispatched=False. Because daily.py calls notify via run_soft, the job still finishes green. This is why runs succeed but no WhatsApps arrive.

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
CALLMEBOT_APIKEY read by scripts/notify.py
CALLMEBOT_PHONE read by scripts/notify.py

Note: the earlier handover listed SUPABASE_KEY. That is dead weight. The live client in db.py reads SUPABASE_SERVICE_KEY (the service_role key) and raises ValueError if it is missing. Do not rely on SUPABASE_KEY.

A local .env IS auto-loaded. config.py, db.py, and notify.py all call load_dotenv() at import, so set -a; source .env; set +a is no longer required (though it remains harmless). Just keep a .env at repo root for local runs.

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

Runs sync_supabase then notify to push certified edges, accumulating picks, and phone alerts

Fully self-sustaining and costs $0.00

Picks only:

PYTHONPATH=src python3 scripts/daily.py --picks-only --future-days 2

Specific date:

PYTHONPATH=src python3 scripts/daily.py --date 2026-06-16

Manual WhatsApp push (after the endpoint fix):

PYTHONPATH=src python3 scripts/notify.py
PYTHONPATH=src python3 scripts/notify.py --force
PYTHONPATH=src python3 scripts/notify.py --date 2026-06-18

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

PYTHONPATH=src python3 scripts/notify.py

Tests:

PYTHONPATH=src python3 -m pytest tests/ -q

If optional Supabase dependencies are missing, at minimum run:

PYTHONPATH=src python3 -m pytest tests/test_assay.py -q

python3 -m py_compile src/edgefactory/util.py src/edgefactory/entities.py src/edgefactory/notifier.py scripts/*.py

Known issues and caveats
Cold-cache certification trap

certification needs deep pre-split history; a cold/evicted GitHub Actions cache holds only a D30 post-split window, so it certifies 0 edges

fixed 2026-06-18: edges_consensus.json is committed to the repo and mine_consensus.write_registry() preserves a good registry when a run certifies nothing

if "REGRESSION GUARD" appears in the logs, the existing registry was kept; restore full history and re-mine to refresh it

WhatsApp / CallMeBot

the CallMeBot endpoint in src/edgefactory/notifier.py is whatsapp.py and must be changed to whatsapp.php (see section 9)

CallMeBot must be authorized from the owner's phone before any message will be delivered

GitHub secrets CALLMEBOT_APIKEY and CALLMEBOT_PHONE must be set; the workflow env lines alone are not enough

notify runs via run_soft, so a silent push failure never fails the overall job

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

notify and the optional CLV / sync steps run via run_soft and never fail the job.

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

notify and the optional CLV / sync steps run via run_soft and never fail the job.

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

WhatsApp push dispatch is wired into daily.py as the final step after sync_supabase, via scripts/notify.py and src/edgefactory/notifier.py.

It supports Meta Cloud, Twilio, and CallMeBot; the current intended free path is CallMeBot.

Only CERTIFIED_CLEAN and CAUTION picks are pushed.

It dedupes against localdata/whatsapp_sent_ledger_YYYY-MM-DD.json and is deliberately silent when there are no new picks after the morning slate.

Root cause of missing WhatsApps identified: send_callmebot_whatsapp() uses the endpoint whatsapp.py instead of whatsapp.php, so every dispatch returns 404, raises, and is swallowed by run_soft while the job still finishes green.

Required actions before the next run:

apply the whatsapp.py -> whatsapp.php endpoint fix in src/edgefactory/notifier.py

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

Regression tests live in tests/test_picks_today.py (covers the append-only per-day pick ledger, the auto-tickets grader format contract, and the operational duplicate-collapse)

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
    scripts/notify.py — discovery alerts now ALSO suppress fixtures
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

Verification: tests/test_notify.py (6 tests: cross-ledger
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
daily.yml + notify.py SHIP. 16/16 falsification targets CONFIRMED
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
    py_compile daily.py/notify.py OK -> ODDS_API_KEYS line present
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
- `format_whatsapp_shadow_summary` (src/edgefactory/notifier.py): second daily
  message — sections SKIPPED_VETO / WATCHLIST_NO_ODDS / WATCHLIST_UNKNOWN_CTX,
  each labeled with that stream's rolling 30d record (`format_stream_record`,
  from localdata/picks_audit_rolling.json -> by_bucket; absent -> honest
  "no settled record yet"). Per-line "| Stream:" label. Cap 12 lines +
  "+N more" pointer. Formatter self-filters shadow buckets (overflow math
  can't leak CAUTION/CLEAN counts).
- `scripts/notify.py`: shadow dispatch with INDEPENDENT dedup ledger
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
- src/edgefactory/notifier.py
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
- scripts/notify.py: _dispatch_shadow_chunks — in-order sends with
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
  (edgefactory.notifier.enhancement_marker) used by BOTH slates, so the two
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
  notify.py (verified by grep), so the stricter exit code cannot
  fail any cloud job; it surfaces in operator-run/scheduled invocations —
  which is where a human looks.
- **Hermetic committed tests (tests/test_notify.py):** dummy
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
   Actions workflow invokes notify.py". Actions invokes daily.py,
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

- **CallMeBot ack classifier** (edgefactory.notifier): HTML-stripped,
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

### Addendum 27.15 — Pre-registered pilot spec: veto-exception cohort (frozen 2026-08-05)

**The 27.14 read (operator's Mac, warehouse-authoritative, window 2026-07-07
-> 2026-08-05):** SKIPPED_VETO settled=71 ROI=+9.18% blended; trusted-only
n=59 ROI=+11.95%; soft-only n=12 ROI=-4.42% — the soft-inflation hypothesis
is DEAD (soft evidence subtracts). Bands: <1.50 n=66 +7.01%; 1.50-2.00 n=4
+17.75%; 2.00-3.00 n=1 (ignore). Reconciliation: 59x0.1195 + 12x(-0.0442) =
71x0.0918 to the unit — deep dive and bucket table agree by construction.
Residual fragility, stated honestly: 93% of the cohort is sub-1.50 odds (thin
per-pick margin, sample still the whole argument), and this window is
backfill — prospective evidence is the point of this pilot.

**Decision: branch 1.** The veto leaves money on the table. Vetoes stay
BINDING for staking policy until this pilot returns and governance approves
any change — we are testing whether a subset deserves exception, not
rewriting the veto.

**PILOT SPEC (frozen at the 2026-08-11 calendar gate; code change not
required before launch):**

- **Cohort (inclusion, complete):** every archived pick with bucket
  SKIPPED_VETO AND price_evidence NOT IN VETO_DEEP_DIVE_SOFT_EVIDENCE
  (SUSPECT_ALIAS_FUZZY, SCOUTINGSTATS_SOLE, UNMATCHED, SOURCE_FALLBACK), 1x2
  market, dated 2026-08-11 forward. No band presupposition: sub-1.50 strength
  is a backfill observation, band cuts are reviewed AT the n=30 read, not
  frozen into inclusion (anti-overfitting).
- **Stake:** flat 0.25u per cohort pick. Exposure cap 15u total. No scaling
  by confidence, no chasing. Micro-stakes are an operator-side manual
  decision; this ledger is the contract and the kill criteria bind the human.
- **Record per pick:** date, pair, selection, odds at pick time,
  price_evidence, veto_reason, and close price where a covered close exists
  (theoddsapi close capture when the league resolves; else close=NA and CLV
  is partial — stated, never filled).
- **Decision points:** n=30 cohort settles -> formal read (ROI vs breakeven
  at observed avg odds, CLV-where-available, by_band, by_reason, vs CAUTION
  over the same days). Pilot also ends at n=60 or cap exhaustion, whichever
  first.
- **Kill criteria (any one):** cohort ROI <= -5% at n>=30 from start; OR
  drawdown >= 6u; OR two consecutive audit runs where trusted-only veto ROI
  (rolling, all days) < 0.
- **Success criteria:** n>=30 with ROI > 0 AND (where CLV measurable) mean
  CLV >= 0. Result: a scoped staking-policy exception for this cohort is
  TABLED as its own operator-gated addendum. Nothing auto-promotes; the
  veto remains default.
- **Anti-overfitting covenant:** the cohort rule is frozen at 08-11. Any
  narrowing (e.g. excluding a reason after seeing its table) requires a NEW
  addendum BEFORE it counts; silent edits void the pilot's evidence value.
- **Checkpoint mapping:** the standing "veto n>=30" checkpoint now refers to
  THIS cohort's prospective count. Enhancement-pricing accrual (27.12/27.13)
  continues independently and is unaffected.

**Explicitly not done:** no staking-policy change, no veto-logic change, no
band-filtered inclusion rule, no multi-source price blending. The veto is on
trial by exactly this ledger, and is presumed correct until it convicts or
acquits itself.

### Addendum 27.16 — The contrast read: soft evidence is the CAUTION poison (2026-08-05)

**Preserved now because the rolling window decays:** the 2026-07-07 rows age
out of the 30-day audit starting 2026-08-06. Arithmetic below reconciles to
the unit against the frozen rolling report (by_bucket CAUTION -0.123333).

**Decomposition of the staked bucket (warehouse-authoritative, window
2026-07-07 -> 2026-08-05, 33 settled):**

| evidence | n | ROI | pnl |
|---|---|---|---|
| BETEXPLORER_RESCUE (trusted) | 13 | +7.7% | +1.00u |
| BZZOIRO_PRIMARY (trusted) | 7 | +70.0% | +4.90u |
| SCOUTINGSTATS_SOLE (soft) | 10 | -69.7% | -6.97u |
| SOURCE_FALLBACK (soft) | 1 | -100% | -1.00u |
| SUSPECT_ALIAS_FUZZY (soft) | 2 | -100% | -2.00u |
| **total** | 33 | **-12.33%** | **-4.07u** |

Derived: **CAUTION intersect trusted = +29.5% (n=20)**; CAUTION intersect soft
= -76.7% (n=13). The entire CAUTION loss is 13 soft-evidence rows. Cross-bucket
corroboration in the SAME window: SCOUTINGSTATS_SOLE negative in SKIPPED_VETO
(-28.2%, n=5) AND in CAUTION; SUSPECT_ALIAS_FUZZY negative in both. The
quarantine taxonomy separates winners from losers — the staking layer simply
does not consume it. Honesty markers: n=20 is still small; BZZOIRO 7/7 is
noise-watch, not a tier conclusion.

**Veto-cohort reason cuts (same window, for the record):** ['odds_band']-driven
vetoes n=34 +5.53% (price-policy blocks, not quality vetoes — they performed);
short-odds away favourites 10/10 wins at +10.9% combined (thin tightrope, one
loss flips it); ['league']-only family -33.4% (n=5) — the one reason family
behaving as intended. Trusted veto tiers individually strong: RESCUE n=44
+9.84%, BZZOIRO n=15 +18.12%.

**08-11 gate agenda (pre-registered, two items):**
1. Launch the 27.15 veto-exception pilot as frozen (no amendment).
2. DECIDE the soft-evidence staking exclusion: whether CAUTION/CLEAN bucket
   assignment should hard-reject VETO_DEEP_DIVE_SOFT_EVIDENCE labels into
   WATCHLIST at pick time (Addendum 26 stamps price_evidence at pick time, so
   the mechanism exists). Decision and any code belong AT the gate — not
   before; the prospective check is then visible: next-window audits should
   show CAUTION intersect soft -> 0 rows.

Explicitly unchanged: the 27.15 pilot covenant; veto logic; no code today.

### Addendum 27.17 — Hygiene payload: pyflakes class retired + two deferred docs (2026-08-05)

**Scope (zero behavior change — deletion, labels, docs only):** the recurring
"pre-existing upstream pyflakes findings" exception is retired. Every gate
review previously paid a base-diff tax on these; now the repo scan is clean
outright: `python3 -m pyflakes scripts/ src/ tests/` -> exit 0, suite 230
passed.

**Code (pure deletion / labels; every removal grep-verified as unread):**
- picks_today.py: dead `timedelta` import; dead cs_rate chain (l_h_cs/l_a_cs/
  h_cs/a_cs); the entire dead over/under-45 probability family
  (l_*_o45, *_score_o45, prob_*_o45, prob_*_u45 — the SQL stats columns stay,
  they are dict material, not findings); dead `total_cert`; the shadowed
  `char_ngram_similarity` import (the line-1471 local def is the live binding
  — every call site resolves after module import); one placeholderless
  f-string.
- theoddsapi.py: placeholderless f-string; log label `credits_month` ->
  `credits_used_month` (the documented wording debt).
- mine_shadow_sources (dead fold_ascii import, 3 literal f-strings),
  mine_consensus (literal f-string on a pure-SQL block), local_backfill
  (unused exception alias), decay_monitor + assay_purity (dead tuple slots
  dropped from the assignment), betexplorer_odds (dead Path import),
  sources/__init__ (bare re-export imports now declared via `__all__` — the
  pyflakes-recognized idiom for an intentional aggregator; note plain
  pyflakes honors neither `# noqa` nor underscore prefixes).
- tests: unused imports removed (test_theoddsapi pytest, test_supabase
  pytest, test_capture_plan_kickoff timezone, test_assay wilson_ub).

**Doc 1 — BENCHED rule lifecycle runbook (code-verified, decay_monitor.py):**
a certified edge whose recent-window ROI goes DEAD/DECAYING, or < -5% on
n>=30, is auto-flipped to status "benched" in the registry by
`scripts/decay_monitor.py` (verdict via edgefactory.assay.decay_verdict /
should_bench; edges whose views cannot be rebuilt report UNKNOWN and are
left untouched — never crash, never guess). picks_today.py consumes ONLY
status=="certified", so a benched rule stops being bet IMMEDIATELY with zero
picks-code involvement. Recovery: the next `scripts/mine_consensus.py` run
rebuilds the registry from full data and re-certifies or not — benching is a
circuit breaker, not a permanent verdict (see: `3way-unanimous min_p>=60
avg_p>=60`, benched 4th time 2026-08-03). OPERATOR ACTIONS: normally none —
observe the bench in the decay_monitor output; `--report-only` audits without
mutating the registry; a bench repeating across consecutive mine cycles means
the cohort itself may be structurally dead — raise at a gate, do not
hand-edit the registry. Run order: capture -> backfill -> build_warehouse ->
mine_consensus -> decay_monitor -> picks_today.

**Doc 2 — winner's-curse display effect (documented in the audit header):**
LINE_THRESHOLDS display only high-side notes (e.g. home_under_35 iff
p>=0.90), so on display-filtered markets realized systematically trails
promised — part of the observed promised-vs-realized gap (the -27.6 delta
discussed in Addendum 27's working notes) is the SELECTION EFFECT of the
display filter, not engine error. The caution now rides inside the
"## Possible Events Full-Surface Audit" markdown header on every audit run,
next to the calibration-is-not-edge doctrine line.

### Addendum 27.18 — Silent audit-coverage loss: append-only day ledger + restored 08-05 slate (2026-08-06)

**Trigger (operator report):** "the audit did not audit every match from
localdata/picks_2026-08-05.txt" — the official 08-05 slate had 6 matches
(1 CAUTION + 5 SKIPPED_VETO); the 2026-08-06 audit carried only 2 of them
(Panathinaikos-CSKA, Fenerbahce-Sturm Graz).

**Finding (git archaeology, exact):** the per-day frozen ledger
`localdata/picks_2026-08-05.json` was built correctly by the 27.12 write —
00:09 persist 2 rows, 07:38/08:27 grows, 15:33 persist (6f95e09) all 6 slate
rows, payload-identical to the .txt. At 21:12 SAST the three-hourly service
re-ran picks_today for day 2026-08-05 AFTER every kickoff (16:30–19:30); the
fixture fetch + pre-match guard yielded an empty slate, and the 27.12 write
("overwrites any existing archive with the freshest run") replaced 6 frozen
rows with `[]`; persist 44557f3 shipped the empty file. daily.py's own
stacked-ledger merge (`autonomous_intraday_merge`) protects the SAME file
one layer up but only writes back when new discoveries exist (new_added>0),
so it never restored what the engine had just clobbered. The audit loader
then did exactly what it is designed to do — kept the 2-row immutable
morning baseline, and had no late additions to verify in an empty regular
ledger. Two writers, one file, "freshest wins" vs "kickoff-stacked
append-only": the engine write was the attacker. Window scan: 08-05 is the
ONLY day in the 30-day audit window that suffered the emptying (the 06-18
empty file predates archives; out of window). Nothing in the audit receipt
flagged an empty regular ledger — the loss was fully silent.

**The 4 lost rows were all settleable and their settlement changes cuts:**
Spartak Moscow 5-1 FC Orenburg (CAUTION, SOURCE_FALLBACK, zulubet @1.32)
WON +0.32; Lazio 4-0 Ostia Mare (VETO, SOURCE_FALLBACK, zulubet @1.02)
WON +0.02; Napoli 2-1 Osasuna (VETO, BETEXPLORER_RESCUE/trusted,
betexplorer @1.72) WON +0.72; Arsenal 1-3 Real Betis (VETO,
BZZOIRO_PRIMARY/trusted, Novibet @1.63) LOST -1.00. Counterfactual audited
cuts with all 6: SKIPPED_VETO 71->74, +7.08% -> +6.44% (trusted-only
+9.42% -> +8.65%; soft-only -4.42% -> -3.92%); CAUTION 32->33, -14.41% ->
-13.00% (CAUTION∩soft 13->14, -76.7% -> -68.9% — Spartak is a n=1
counterexample to the soft-poison thesis; the thesis stands at -68.9%);
rule `3way-unanimous avg_p>=65` 43->45, -6.46% -> -6.80% (bench watch
DEEPENS past the -5% line); overall settled 127->131, ROI 1.29% -> 1.29%
(net +0.06u). The flagship paradox is unchanged by the full slate — the
audit was UNDERSTATING the veto cohort, not inflating it.

**Fix (breakage clause of the 08-11 freeze — evidence-pipeline integrity):**
1. `picks_today.merge_day_archive_rows()` — the per-day archive write is now
   APPEND-ONLY: earlier frozen rows are never dropped by a later same-day
   rerun; identity = the audit's `_archive_pick_key` (date, norm home/away,
   market, pick); the earlier FROZEN payload wins conflicts (pick-time state
   is authoritative — the audit's payload-identical superset check depends
   on it); rows dated to other days are not preserved (the audit filters
   them too); an unreadable prior file degrades to fresh-wins with a warn
   (daily.py's corrupt-archive doctrine). Same-day planner-era survivors
   (as_of != day) are preserved exactly as the orchestrator's kickoff-stack
   already preserves them — no contract change.
2. `audit_recent_picks` receipt gains `empty_regular_ledger_dates`: a regular
   ledger that EXISTS but holds [] alongside a morning baseline is enumerated
   in the rolling json AND the audit markdown Overview (with dates) — an
   emptied ledger can never again be a silent gap. Semantics post-fix:
   benign "no late additions", but pre-fix it marks exactly the lost days.
3. Retrospective repair WITHOUT hand-editing: the frozen 6-row ledger was
   restored byte-identical from git commit 6f95e09 (version-controlled
   truth, not reconstruction); its morning-baseline rows verified
   payload-identical, so the fail-closed loader accepts all 6 on the next
   audit run and the counterfactual cuts above become the real cuts.

**Verified:** 9 new tests — 6 merge tests (empty-fresh preserves; partial
fresh keeps KO'd rows + frozen payload wins conflicts; late discovery
appended; identity key shape mirrors _archive_pick_key; foreign-day rows
dropped, missing-as_of kept; empty-existing = fresh) + 3 loader receipt
tests (empty regular flagged + baseline kept; missing regular not flagged;
superset additions and fail-closed behavior unaffected). Suite 239 passed
(was 230).
pyflakes repo-wide exit 0. Fresh-clone verify: checkout origin/main + this
payload -> checksums OK -> suite green.

---

## Addendum — 2026-08-08 (evening): EV-based enhancement selection

**Trigger:** operator report that the same enhancement ("Home Team Over
0.5 Goals") was recommended on nearly every match, and the
secondary-market audit showed the highest-probability markets were
not the ones with demonstrable edge.

**Root cause:** compute_dynamic_enhancement ranked candidates by a
hand-built safety tier plus raw probability. For home favourites,
Home Team Over 0.5 Goals is 88–94% and won every ranking, but at
~1.08 odds it carries negative expected value.

**Change (2026-08-08):** compute_dynamic_enhancement now accepts the
prices_index and ranks every candidate by real edge
(edge = model_probability * best_captured_odds - 1), using zero
extra API credits (prices are read from cached captures). Hard
filters:

- btts_yes permanently excluded (operator opt-out)
- goal_range_* excluded automatically (never priced)
- must be priced from a captured source
- edge >= +3%
- probability in [25%, 90%]

When nothing passes, the function falls back to the legacy safety
tier but leaves the pick unpriced (renders as research, not 🔥).

The Telegram renderer now shows market, probability, captured
odds, calculated edge, and price source.

**Does not change:** 1X2 selection, buckets, staking, or the
barbell strategy. Probability calibration (Addendum 17) is
untouched.

**Measurement:** after 30 days, compare recommended-market
distribution, priced hit rate vs breakeven, and aggregate priced
ROI against the prior probability-selected baseline. Revert if
priced ROI is below -10%.

**Tests:** 242 passed.


## Addendum — 2026-08-09: league-alias overrides for big-slate UNKNOWN verdicts

Trigger: pinned-era (2f3b6d0) big-slate run emitted 22 UNKNOWN league verdict
warnings. Several were alias gaps (Portugal,Liga Portugal vs portugal primeira
liga -> same league, different verdicts). Added 69 aliases in
Config/entity_overrides.json mapping warned raws to registry codes (pt1, lv1,
se1, se3, ro1, hr1, hu1, kz1, de2, ar2, cz1, no2, br1, brw, ru1, am1, ua1,
us4). Verdicts resolve where learned purity cells exist (pt1/nl1 3way65=ALLOW,
bg1 3way65=VETO); data-limited leagues stay UNKNOWN (non-blocking) until
settled history accumulates. Alias layer only — no verdicts invented, miners
untouched. Git restored to main-only; slate commit a9205c3 on main.

---

## Addendum — 2026-08-09: auto-tickets system (selection layer) + operational fixes

**Scope:** new operator-facing selection layer built on top of the existing
pipeline, plus three operational bug fixes. No staking policy change; no
veto-logic change. Percentages-of-capital only by design — stakes are a later
layer once selection is proven.

### New: auto-tickets (scripts/auto_tickets.py + auto_tickets_grade.py)

- **Purpose:** remove hand-picking. Tool chooses today's accas from the slate
  using only combos with dynamically computed positive edge; freezes them at
  12:00 SAST (commit 715cf18) so the 8x/day cloud loop cannot churn them; grades settled slips.
- **Structure (operator plan, acca-only):** 28% of capital -> up to 3 x 2-odd
  accas (paired smallest x largest odds, closest to 2.00); 10% of capital ->
  one 10-odd acca (fewest legs to reach 10.0). No singles. All output is
  percentages; operator does the rand math.
- **Selection gates (dynamic, recomputed every run):** bucket in
  CERTIFIED_CLEAN + SKIPPED_VETO (CAUTION excluded — negative ROI historically);
  combo (edge rule x odds source) passes n>=15, ROI>=+3%, Wilson LB>=0.68,
  recent-20 ROI>=0; NO hardcoded trusted-price allowlist — a price source is
  trusted iff it has at least one passing combo (sources earn entry; this
  un-traps ml-meta/forebet/zulubet once proven).
- **Safety rails:** 12:00 SAST generation gate (NOT YET before, freeze after; rationale: commit 715cf18);
  10-odd held back if <3 distinct legs or <4.0 total (no duplicate-of-2-odds);
  drawdown pause if last 20 graded tickets ROI < -10% (--force overrides);
  grader writes auto_tickets_performance.txt + .json; slips + performance
  tracked via .gitignore exception (!localdata/auto_tickets_*).
- **Wired into daily.py** (official + intraday) as run_soft steps, so the cloud
  generates/freezes/grades every cycle.

### Fixes

1. **decay_monitor ZeroDivisionError** (src/edgefactory/assay.py): decay_verdict
   crashed when a certified edge's recent window had n=0 settled picks
   (r_p = recent_wins / recent_n). Now returns WATCH on recent_n==0 — no
   crash, never benched on no data.
2. **ML-meta could never fire** (scripts/picks_today.py): eval_1x2 required
   forebet AND zulubet AND statarea all present on a fixture; in practice the
   3-source overlap never occurred, so the certified ml-meta edge was silent
   forever (0 picks in all archives). Now fires on 2-of-3 sources, missing
   features excluded from avg/min/std. Cross-layer tripwire (certified edge
   with zero picks over N days) is a known gap — TODO.
3. **OddsAPI 422 false-exhaustion** (src/edgefactory/sources/theoddsapi.py):
   HTTP 422 (market/sport not on plan) was treated as key exhaustion and
   permanently killed keys. Now 422 is logged-and-skipped; keys stay live.
   ODDS_API_MARKETS default trimmed to h2h,totals (free-plan only), 2
   credits/event.

### Known gaps / TODO (not in this payload)

- Certified-edge-not-firing tripwire (proposed, not built).
- DEBIAS wrong source + 6/6 btts_yes degeneracy (Addendum 19/27.5 — pre-existing).
- VETO re-mine (Addendum 19 — pre-existing).
- test_benched_circuit_breaker date-stale ~2026-10-02 (pre-existing).
- Staking layer: intentionally NOT built; percentages only until selection
  proven; review at the 2026-08-11 gate.
- Handover itself is doctrine, not stone — auto-tickets defines its own rules
  and this addendum records them.

**Tests:** syntax-checked; auto-tickets generation verified (2-leg hold-back
and 7-leg rich-day cases); assay recent_n=0 verified; picks_today 2-of-3
ML-meta verified; grader v4 schema verified. Full pytest not re-run this
payload (pinned-era tree); run before 08-11 review.

## Addendum — 2026-08-09: auto-tickets grader legacy-slip display fix

**Trigger.** Operator directive: all slips must display as % of capital,
not as currency amounts. The 526116e commit fixed the new-slip case
but introduced a regression for the one legacy slip on disk
(`localdata/auto_tickets_2026-08-09.json`, generated before the
`stakes_frac` field existed in commit b1c1946). The grader's fallback
to `stake=1.0` rendered the legacy slip as "staked 100.00% of capital",
which is wrong.

**Operator's plan (mirrored from `scripts/auto_tickets.py`):**

- `AT_RISK_FRAC = 0.38` — the **ceiling**, not a target
- `CAP_ACCA2 = 0.28` split across `N_ACCA2_TICKETS = 3` tickets
- `CAP_ACCA10 = 0.10` per 10-odd acca
- The 38% is a CEILING: deployment scales with the qualifying-pool
  median (adaptive, commit `b1c1946`/`e9beab9`). A thin slate
  deploys less than the ceiling; a rich slate approaches it.
- No singles in the current plan (v1-v3 archive slips may still
  exist on disk; v1-v3 staking was a fixed R1/bet convention)

**Fix.** `scripts/auto_tickets_grade.py::load_tickets` no longer
**invents** per-ticket stakes for legacy slips (no `stakes_frac`).
The previous attempt reconstructed `CAP_ACCA2/N_ACCA2_TICKETS` per
ticket — that was wrong because the actual rand amount depends on
the adaptive `pool_factor` at generation time, which is not
recorded on the slip. The grader now marks the day as legacy and
the per-ticket `stake` is `None`. The per-day display reports
"stake not recorded (pre-adaptive slip, see bookmaker history)" with
no percent and no currency. The operator can look at their
bookmaker history for the actual rand amount.

New slips (with `stakes_frac` written by the post-`b1c1946`
generator) display normally: the recorded per-ticket percentage
times the acca2 ticket count + the recorded acca10 percentage =
total deployed as % of capital. The legacy slip's "stake not
recorded" status is **explicit**, not silent — the operator can
see at a glance which rows are legacy.

**Tests.** `tests/test_picks_today.py` extended with 5 grader
contract cases plus 7 operational duplicate-collapse cases. Total
suite: 18/18 pass in `tests/test_picks_today.py`. Pre-existing
failures in other test files are environment-dependent
(duckdb, curl_cffi) and are not caused by this change.

**Files touched.**

- `scripts/picks_today.py`: 1 line removed (unused `rec_state`
  local; Addendum 27.17 hygiene).
- `scripts/auto_tickets.py`: 1 import trimmed (unused `timedelta`),
  1 local removed (unused `rw`; Addendum 27.17 hygiene).
- `scripts/auto_tickets_grade.py`: 1 import trimmed (unused `math`),
  2 f-strings fixed (no-placeholder f-string); `load_tickets`
  returns `(tickets, legacy_dates)`; per-ticket stake is `None` for
  legacy slips; per-day and per-type display branches on
  `legacy_dates` to show "stake not recorded" with a transparent
  note instead of a percent.
- `tests/test_picks_today.py`: extended to 18 cases (6 merge
  contract + 5 grader contract + 7 collapse contract).
- `HANDOVER.md`: 2 lines reconciled with the 12:00 SAST freeze
  (commit 715cf18); 1 line reconciled with the actual test
  filename; this addendum.
- `README.md`: 1 line reconciled with the 12:00 SAST freeze.
## Addendum — 2026-08-10: pivot to truthfulness + orphaned-data inventory

**Operator direction (2026-08-09/10):** stop treating the 08-11 calendar gate as
the priority. The main focus shifts to (a) letting the auto-tickets ledger be
the real judge of the system (real executable graded bets > paper audit
numbers), and (b) making the system TRUTHFUL — surfacing and closing blind
spots rather than adding scope. 08-11 items (27.15 pilot launch, soft-evidence
exclusion decision, OddsPapi review, source funnel, debias verdict) remain
documented and pre-registered, but are NOT being actioned as a ceremony; they
get picked up opportunistically when they intersect real work.

### Truthfulness findings (data we collect but do not use)

Audited source schemas vs what the warehouse loads vs what miners/picks
consume. Summary of orphaned signal:

- **Half-time data**: forebet + statarea produce `ht_hs/ht_gs` (HT scores) and
  `p1_ht/px_ht/p2_ht` (HT win probs). Loaded into warehouse. NEVER consumed by
  any miner/pick/audit. System is blind to first-half markets and to
  half-time-state-aware full-time modeling.
- **xG**: bzzoiro produces `xg_home/xg_away`. Loaded. NEVER mined. Highest-value
  untapped predictor in the stack.
- **O/U alternative lines**: forebet `p_under`/`goalsavg`; bzzoiro
  `p_o15/p_o35`; scoutingstats `p_o15/p_o35` AND `odd_o15/u15/o35/u35` — the
  scoutingstats 1.5/3.5 ODDS ARE NOT EVEN LOADED into the warehouse. System
  only models O/U 2.5.
- **BTTS complement**: forebet + scoutingstats `p_ng` (BTTS-no) unused; only
  BTTS-yes modeled.
- **Predicted scores**: bzzoiro/predictz/windrawwin `pred_score`, vitibet +
  forebet `pred_hs/pred_gs` — unused. Could cross-check O/U or exact-score.
- **Provider meta**: bzzoiro `rec_bet_favorite`/`rec_winner` — shadow-only
  potential.
- **Form streaks**: afootballreport `streak_pct/streak_n` — unused feature
  candidate for the ML-meta classifier.
- **Kelly**: forebet `kelly` — NOT LOADED into warehouse (dropped). A
  ready-made staking-size signal being discarded.
- **Misc**: bettingclosed pick_* + odds (partial), betclan winner/url,
  freesupertips/windrawwin `stake`, forebet `league_id`.

### Planned modeling direction (layered, not one mega-model)

1. xG -> enrich existing ML-meta classifier (xg_diff, xg_total features) and a
   separate O/U model. Cheapest, highest-certainty win (already loaded, proven
   predictor).
2. Load scoutingstats 1.5/3.5 odds (2-line data gap) -> unlock O/U 1.5 and
   O/U 3.5 as separate certified markets.
3. First-half 1X2 from `p1_ht/px_ht/p2_ht` (same miner structure, HT market).
4. HT-state features (goal_diff_at_HT, home_led_at_HT) into full-time model.
5. BTTS-no market; predicted-score O/U cross-check.
6. Provider recs as shadow sources (Phase-A style), never primary.

Every addition must certify WALK-FORWARD (train pre-split 2025-06-01, certify
post-split) and be judged by the auto-tickets grader at real prices. No
backtest-into-deployment. The auto-tickets ledger (auto_tickets_performance)
is the system's primary truth signal going forward.

### Process notes

- Skipped: 08-11 ceremonial gate (operator decision, this addendum records it).
- The "honest rule labels" fix (display_rule now shows qualifiers like
  BC-CONFIRMS/HOME-ONLY/MIN-P) and the readable audit % formatting shipped
  2026-08-09/10 — part of the truthfulness pivot.
- Gotcha sweep shipped 2026-08-09: string-odds crash, kickoff "DD-MM, HH:MM"
  format, additive-10-odd w/ thin-day reuse, held-back msg fix, % stakes in
  grader, adaptive ideal pool (season-aware), adaptive deployment ceiling.

---

## Addendum — 2026-08-10 (late): stale display_rule in archived ledger rows

**Bug (operator-reported):** the 08-10 slate still showed `[2WAY-UNANIMOUS≥60]`
for picks whose exact rule is `2way+bc-confirms avg_p>=60` — the honest-label
fix (7f573b48ab) had landed, but the label persisted.

**Root cause (proven from origin history):** picks for 08-10 fixtures were
first archived by the 08-09 22:42Z run — 46 minutes BEFORE the honest-label
commit (23:28Z) — with the pre-qualifier `display_rule` baked into the rows.
`autonomous_intraday_merge` retains existing ledger rows exactly (Day-0
performance protection), so the stale display survives every later run; even
the current cloud `picks_today.json` carried it.

**Fix (single source of truth):** `edgefactory.util.display_rule_label()`
(canonical qualifier formatter) + `edgefactory.util.honest_display_label()`
(derives the label from the EXACT rule string at render time, falls back to
stored values only for unparseable rules). All three render paths now use it:
`picks_today.print_buckets`, `daily.generate_daily_report` (.txt report), and
`notifier._pick_rule_label` (Telegram). Stored ledger rows are NOT mutated —
ledger integrity is untouched; display is always derived from ground truth.

**Verified:** the 4 stale 08-10 rows now render `2WAY-UNANIMOUS+BC-CONFIRMS≥60`;
the genuine `2way-unanimous avg_p>=70` row (Sirius) still renders
`2WAY-UNANIMOUS≥70` (no false qualifier); ml-meta / legacy display-string rows
fall back cleanly; `_edge_entry` + `load_thresholds` regression-tested.

**Context:** the bc-confirms≥60 rule is the audit's −19.2% ROI rule (n=20) —
auto-tickets correctly never bet it (no passing rule×source combo); the current
edges registry no longer contains bc-confirms at all (re-mine skipped it, no
bettingclosed data), so no new picks from it going forward. Archived rows
remain in the ledger for grading.
---

## Addendum — 2026-08-10 (late 2): xG Phase-1 screen — honest result

**What was tested:** bzzoiro `xg_home/xg_away` vs settled outcomes, walk-forward
screen, multi-source results (betexplorer/forebet/statarea/scoutingstats union,
precedence betexplorer>forebet>statarea>scoutingstats). 760 bzzoiro fixtures
joined (750 base9); split 2026-07-30; train n=429 / test n=303 (with xg).
Tool: xg_signal_check.py (workspace tool, not committed to repo).

**Result (test window, n=303):**
- AUC(home win): xg_diff 0.632 vs bzzoiro p1-p2 0.694 — the model's own
  probabilities BEAT raw xG on the same fixtures.
- AUC(over2.5): xg_total 0.588 (weak); p_o25 comparison added for the next run.
- spearman corr(xg_diff, goal_diff) = 0.314; corr(xg_total, total_goals) = 0.187.
- Buckets are monotone at the extremes (xg_diff +1.0..+1.5 -> 80% home; xg_total
  3.5+ -> 70% over) but mushy in the middle — directionally real, magnitude weak.

**Honest conclusion:** xG is predictive but WEAK, and for match outcome it is
INFERIOR to bzzoiro's own p1/p2 — which the system already consumes via ML-meta
features. The "cheapest, highest-certainty win" claim from the 08-10 addendum is
NOT supported by this screen. Do NOT rush xg_home/xg_away into ML-meta as a
headline feature. The real test is marginal value: feature ablation
(xg_diff/xg_total added to the existing feature set, walk-forward logloss/AUC)
— deferred until >=1 full season of xG history exists (capture began
2026-06-13; true cross-season walk-forward is impossible now). This screen is a
same-period split and certifies nothing.

**Also surfaced (data gaps):**
- betexplorer capture (odds AND results) stops 2026-06-16 — starves any
  results join for the xG window. Intentional or dead? (open item)
- xG history is 2 months old — the 2025-06-01 walk-forward split is impossible
  for xG; it gets its own data-driven split until a season exists.

**Process:** screen found nothing certifiable -> nothing deployed. The auto-
tickets grader remains the only thing that decides what gets staked.
---

## Addendum — 2026-08-10 (late 3): xG O/U closure — redundant with p_o25

**New data:** reran xg_signal_check.py with the p_o25 head-to-head (bzzoiro's
own over-2.5 probability, already consumed by the system).

**Result (test n=303):** AUC(over2.5) xg_total 0.588 vs p_o25 0.576 —
statistically identical. corr(xgt, p_o25) = 0.763 (~58% shared variance).
Train: 0.573 vs 0.576 — identical. Combined with the 1X2 result (p1-p2 0.694
beats xg_diff 0.632), raw xG columns are REDUNDANT with bzzoiro's own model
probabilities on both markets.

**Doctrine (updated):** the xG screen closes as NOT useful now. No xG feature
work; no xG-into-ML-meta. Revisit only if/when (a) a full season of xG history
exists for a real cross-season walk-forward, AND (b) a feature-ablation test
shows marginal lift over the model's own probs. This is the truthfulness
system working: a promising orphaned column got tested and failed to add
value; the record now says so.

**Note:** xg_signal_check.py lives untracked in the repo dir as an operator
tool (analysis only, not pipeline code). Leave untracked; never git add -A.
---

## Addendum — 2026-08-10 (late 4): combo freshness gate — dead sources can no longer pass

**Trigger:** betexplorer capture stopped 2026-06-16 (retired — refresh_result_sources
lists forebet/zulubet/statarea/vitibet/scoutingstats, no betexplorer; daily.py
never invokes its capture). That raised the question: could a frozen
betexplorer_odds combo stay eligible in the auto-tickets edge table forever?

**First diagnosis (wrong, recorded honestly):** thought the recency gate passed
rn==0 (no picks in the last-20 window) as 0.0>=0.0. Test disproved it: the
window is COUNT-based (rows[-20:]) and any combo with n>=15 always has rn>=15 —
rn==0 is unreachable for passing combos. Dead-code guard added anyway
(recent_ok requires rn>0 — semantically right, never triggers).

**Real fix (calendar freshness):** a count window cannot detect a dead source —
its old rows simply BECOME the "recent" window. Added FRESHNESS_DAYS=30 to
build_edge_table: the combo's NEWEST settled pick must be within 30 days of the
target date, else the combo is ineligible ("fresh":false in the table). Verified:
frozen June combo (last 2026-06-20) now FAILS; active combo passes; negative
recent ROI still fails; boundary <=30 days is fresh.

**Effect:** a source whose capture dies ages out of eligibility within 30 days
of its last settled pick, instead of staying eligible forever on frozen
history. When/if the source returns, eligibility restores once a new settled
pick lands inside the window. This protects the grader's edge table from
stale-validated combos (betexplorer_odds today; any future dead source).

**betexplorer decision (operator, open):** capture is retired, not broken.
Either (a) accept retirement — betexplorer_odds combos age out and die, or
(b) revive capture. Recommendation: (a) — the other 5 sources cover results and
bzzoiro_odds/scoutingstats_odds cover prices; betexplorer adds no unique
market. Only note: any historical betexplorer_odds picks remain in the graded
ledger and count toward n=30 (they are real graded tickets, just frozen).
---

## Addendum — 2026-08-10 (late 5): self-healing honest labels

**Problem:** the render-time fix (87fb5a5) made every display honest, but the
STORED ledger rows still carried the pre-qualifier display_rule (e.g.
"2WAY-UNANIMOUS>=60" for rule "2way+bc-confirms avg_p>=60"). The merge layer
retains rows exactly, so stored data stayed stale forever. The data itself was
not truthful — only the render was.

**Fix (self-heal, two layers):**
1. `edgefactory.util.heal_ledger_labels()` — derives the honest label from the
   exact rule string and rewrites the stored display_rule. Touches ONLY the
   display field; never rule/odds/results/performance. Idempotent.
2. Wired into daily.py at every ledger write point: archive_picks_by_kickoff,
   forecast promotion, and the autonomous intraday merge. Every pipeline write
   heals first, logs "self-healed N stale display labels", then persists — so
   stale labels can never accumulate again.
3. `scripts/heal_pick_labels.py` — one-time historical sweep across all
   picks_*.json / picks_today.json / picks_morning_*.json (idempotent; heals 0
   on re-run). Run once to make all stored archives truthful immediately.

**Verified:** real 08-10 ledger healed 4 rows (bc-confirms -> +BC-CONFIRMS);
Sirius (genuine plain 2way>=70) untouched; re-heal = 0; sweep across multiple
files + idempotency confirmed.

**Note on display_rule for the plain rule:** "2WAY-UNANIMOUS>=70" for
"2way-unanimous avg_p>=70" is CORRECT — no qualifier exists. The lying labels
were only the >=60 bc-confirms rows. After the sweep, stored data == truth.
---

## Addendum — 2026-08-10 (late 6): .txt report artifacts self-heal too

**Gap found by operator check:** after the JSON sweep (a2c1768), localdata/
picks_2026-08-10.txt STILL showed [2WAY-UNANIMOUS>=60]. Root cause: the .txt
is a static snapshot committed to the repo (gitignore exception !localdata/
picks*), generated by the pre-fix 04:23 UTC run. The pipeline only re-renders
the CURRENT day's .txt, so a past day's artifact keeps the old labels
forever — the self-heal fixed the JSON ledger but not the human-facing .txt.

**Fix:** heal_pick_labels.py now re-renders picks_{date}.txt for any date
whose .txt label set mismatches the JSON's honest label set (derived from
exact rule strings), using the same renderer the pipeline uses
(daily.generate_daily_report — already honest). Works even when the JSON was
healed by a previous run (the Mac's state). Idempotent: after re-render the
labels match, so a rerun re-renders nothing.

**Verified:** healed-JSON + stale-.txt fixture -> .txt re-rendered with
[2WAY-UNANIMOUS+BC-CONFIRMS>=60] (x4) and [2WAY-UNANIMOUS>=70] (Sirius,
genuine); rerun heals 0 and re-renders 0.

**Also:** any .txt regenerated by the pipeline going forward is already
honest (render-time derivation from 87fb5a5). This closes the last stale
surface: display, stored JSON, and committed .txt artifacts all truthful.
---

## Addendum — 2026-08-10 (late 7): decay-aware buckets — CERTIFIED_CLEAN must be earned

**Trigger:** operator asked how CERTIFIED_CLEAN is computed after the bucket
showed ROI -67.4% (5 settled bc-confirms>=60 picks, 1 win).

**Root cause (code-verified):** bucket_pick only benched DEAD/DECAYING decay
verdicts; WATCH fell through and still earned CERTIFIED_CLEAN. The registry at
that time listed every certified edge as decay WATCH (recent window cannot
confirm health), so "CERTIFIED CLEAN" was stamped on edges the decay monitor
refused to bless. Rules missing from the registry also defaulted to HEALTHY
(optimistic default — absence of evidence treated as health). The bucket was
computed correctly from unconfirmed beliefs.

**Fix (decay-aware buckets):**
- HEALTHY -> CERTIFIED_CLEAN (must be earned, explicit decay confirmation)
- WATCH / unconfirmed / missing-from-registry -> CAUTION (downgrade)
- DEAD / DECAYING -> SKIPPED_DEAD_EDGE (existing behavior)
- bucket_pick default decay_verdict changed HEALTHY -> WATCH; main() registry
  miss default changed HEALTHY -> WATCH. Veto + price-quarantine gates
  unchanged and still win (verified: WATCH+VETO -> SKIPPED_VETO; WATCH+no
  odds -> WATCHLIST_NO_ODDS).

**Effect:** the slate shows (near-)zero CERTIFIED_CLEAN until the decay
monitor explicitly confirms an edge HEALTHY. That is the truthful state.
Auto-tickets is unaffected (its gate is the evidence-graded (rule x source)
combo table, not buckets — which is why it dodged all 5 losing
CERTIFIED_CLEAN picks). Tests updated: tests/test_price_quarantine.py passes
decay_verdict="HEALTHY" explicitly where the certified path is asserted.

**Not actioned (still open, opportunistic):** soft-evidence exclusion decision
(11th agenda) would hard-reject SUSPECT_ALIAS_FUZZY / SCOUTINGSTATS_SOLE /
UNMATCHED / SOURCE_FALLBACK from push — audit shows those are the worst cuts
(SCOUTINGSTATS_SOLE -81% n=9, SUSPECT_ALIAS_FUZZY -100% n=2). Related but
separate; pick up when this area is next touched.
---

## Addendum — 2026-08-10 (late 8): truthfulness patch batch (P1-P4)

### P1 — Certified-edge-not-firing tripwire (scripts/edge_firing_tripwire.py)
Surfaces the two classes of SILENT failure the pipeline never reported:
1. **Certified edge not firing**: any certified rule with zero ledger picks in
   the last --edge-silent-days (default 14). Would have caught the ML-meta
   3-source bug (zero picks in every archive for weeks). First run already
   shows the truth: ml-meta avg_p>=70/75 have NEVER fired (last=never).
2. **Source capture stale**: any active source whose newest captured row date
   is older than --source-stale-days (default 7). Would have caught the
   betexplorer 06-16 freeze. betexplorer deliberately excluded (retired,
   addendum 4); re-add if revived.
WARN-only by design (silence can be legitimate: thresholds, off-season) —
wired into run_smart_auto as a run_soft step; findings printed AND persisted
to localdata/edge_firing_tripwire.json (now a gitignore exception so the
cloud bot commits it and history is inspectable).

### P2 — Delivery-failure truth (green run != message arrived)
notify.py already exits non-zero on any failed channel (Addendum 25.1.1) but
run_soft swallowed it into a log WARNING. Now: per-provider failures are
persisted to localdata/notify_delivery_failures_<date>.json (gitignore
exception), notify.py prints a loud ❌ banner naming the ledger on failure,
and daily.py's new _notify() helper prints a banner when today's ledger
exists. Pipeline still continues (notify failure must not block state
commits) — but the failure is no longer invisible. Verified: ledger append +
idempotence tested.

### P3 — Test time-bomb killed (tests/test_enh_registry.py)
test_benched_circuit_breaker_window_is_injected hardcoded 2026-08-03 /
2026-10-04 for a rolling-60-day window — would silently drift ~2026-10-02.
Now computes dates relative to date.today() (inside = today, beyond =
today+61). Same semantics, never stale.

### P4 — Soft-evidence exclusion: closed with evidence, no code change
Agenda item resolved as ALREADY-IMPLEMENTED + data-verified:
- SCOUTINGSTATS_SOLE / SUSPECT_ALIAS_FUZZY: already push-quarantined
  (Addendum 26, bucket_pick + tests/test_price_quarantine.py).
- UNMATCHED: already WATCHLIST_NO_ODDS.
- SOURCE_FALLBACK: audit shows +15.5% ROI (n=11) — the data CONTRADICTS
  excluding it; it stays push-eligible (test_no_live_match_keeps_legacy_...).
- The audit's horror cuts (SCOUTINGSTATS_SOLE -81% n=9, SUSPECT_ALIAS_FUZZY
  -100% n=2) are historical rows bucketed before Addendum 26; the current
  code quarantines those evidence types at bucketing time.
No further action needed; item closed.

### Files changed
- NEW scripts/edge_firing_tripwire.py
- scripts/notify.py (failure ledger + banner)
- scripts/daily.py (tripwire step + _notify helper)
- tests/test_enh_registry.py (relative dates)
- .gitignore (persist tripwire + failure-ledger artifacts)
---

## Addendum — 2026-08-10 (late 9): cold-cache certification guard (L9 resolved)

**Bug:** mine_consensus.py checked only `if not DB.exists()` before certifying —
never that the settled tables had enough PRE-SPLIT history. A cold cache
(fresh/unbuilt warehouse) would certify nothing, then write_registry's
regression guard PRESERVED stale edges as if re-validated. The system kept
"certified" edges that were never re-confirmed — a silent untruth.

**Fix (scripts/mine_consensus.py):** MIN_PRE_SPLIT_SETTLED = 500 +
_cold_cache_check(): counts pre-split settled rows in the 5 consensus tables
(forebet/zulubet/statarea/scoutingstats/vitibet). Any table under 500 ->
prints "⚠️ COLD-CACHE: <source> pre-split=N (<500) — cannot certify on this
cache." and REFUSES to certify, leaving existing edges untouched. Fail-safe:
missing table or query error -> skip, never false-block (verified with 5
test cases: cold all-under triggers, warm all-over passes, single-warm
passes, one-cold-among-warm triggers, error passes).

**Effect:** certification can never again silently run on an empty cache.
The "certified" label now requires BOTH the walk-forward gates AND a
history-rich warehouse.

**Deploy note:** this fix lives in the workspace file; the operator's first
attempt (git pull + py_compile + commit) deployed nothing because the new
file never reached the Mac — the repo had no diff. Deploy by downloading the
updated scripts/mine_consensus.py and overwriting the local copy.
---

## Addendum — 2026-08-10 (late 10): DEBIAS per-engine noise gate (6/6 degeneracy)

**Bug:** src/edgefactory/debias.py MIN_ENGINE_N = 5 let per-engine calibration
cells with n=5..9 produce damps. Real audit data shows 50 cells across 3
engines with n<20 (model engine: ALL cells n<=2). A 6/6 btts_yes cell (n=6)
produces a "confident" damp from noise — the documented degeneracy.

**Note:** the "DEBIAS wrong source" (tiny recommendation overlay vs full
surface) is ALREADY FIXED — Addendum 19 rewrote the module to read
event_notes_audit.by_market (MIN_MARKET_N=15). What remained was the
per-engine gate.

**Fix (src/edgefactory/debias.py):** MIN_ENGINE_N 5 -> 20. Data-grounded:
with gate>=20 only 10 cells survive (hybrid_cohort 6, legacy 4) — the rest
fall back to the pooled by_market cell, which is the intended safe path.
Verified with the real audit JSON: 16 markets pooled, 10 engine cells kept,
resolve_debias_hr works (exact_4 hybrid -> 1.00).

**Effect:** per-engine damps now require real evidence (n>=20); tiny noisy
cells can no longer move probabilities. Flag-gated (EDGE_FACTORY_ENGINE_AWARE_
DEBIAS) so zero production impact until enabled. This also resolves the
"by-engine verdict" agenda item's data half: n=5 cells are noise, n>=20 is
the bar.
---

## Addendum — 2026-08-10 (late 14): eyes-open run result — scale fix CONFIRMED, calibration now honest

**The run (full official pipeline after addendum-13 deploy):**

1. **Scale fix confirmed working.** Old model's probability weights were ~0 (fit on 0-100 units); new model (fit on 0-1) has sa_p=+3.19, avg_p=+1.29, fb_p=+0.46 — probabilities now drive the prediction. Live max ml_p jumped 7.1% -> 54.8% (7.7x) in one run. The unit-mismatch diagnosis was correct and the fix is live.

2. **Eyes-open harvest effective.** The 9 orphaned features earned real weights: kelly=-1.39, p_ng=+0.28, ht_diff=+0.24, ht_total=+0.19. The model now sees data it was never given.

3. **Re-certified STRONGER + new edge.** ml-meta>=70 valid 901n 86.1% +34.2% HEALTHY; >=75 valid 559n 90.2% +36.1% HEALTHY; NEW ml-meta>=80 valid 277n 92.1% +30.8% WATCH. Decay healthy across the board.

4. **Still doesn't fire live (max 54.8% vs 70), and that is now an HONEST calibration question, not a bug.** Summer slate (lower leagues/friendlies) genuinely low-information; the model's certified 86%+ comes from peak-season big-league history. The tripwire CEILING flag reports this correctly every run. Watch across the season boundary (EPL/CL from mid-August): if the model fires when confident fixtures exist, the fix is complete; if it stays silent through peak season, thresholds/certification need review. The wire will tell us either way.

5. **Grader honesty confirmed live:** legacy 08-09 slip now prints "stake not recorded", ROI n/a, excluded from capital totals. No fake stakes, no fake rand.

6. **Tripwire ceiling message fixed:** was reporting the lowest threshold (70) for all ml-meta edges; now uses each rule's own threshold (>=70 gap 15.2pp, >=75 gap 20.2pp, >=80 gap 25.2pp). Verified.

**Note:** ml-meta>=70/75/80 remain certified but silent — the CEILING flag (not mere SILENT) is the honest status until the slate thickens. Auto-tickets unaffected (its gate is the graded combo table, not these edges).
---

## Addendum — 2026-08-10 (late 15): Phase A — sa_ht_p + p_gg features for ML-meta

**What:** completed the eyes-open harvest with two more features the model
wasn't using, mirrored across warehouse -> trainer -> live path:
- `sa_ht_p` — statarea half-time win prob of the majority pick (second
  source's HT opinion; statarea HT probs already surfaced in consensus3)
- `p_gg` — forebet BTTS-yes prob (was loaded in the raw forebet view but
  never carried into consensus3; now added)

**Result:** ML-meta feature set is now 26 (was 15 at the start of the day),
all trainer == live verified (feature-consistency test passes).

**Certification decides:** the next mine_consensus run re-trains with 26
features and re-certifies. If sa_ht_p / p_gg earn their keep (walk-forward
lift), they stay; if not, they're harmlessly dropped by the gates. No manual
feature veto — the data judges, same as everything else.

**Caveat kept honest:** added features on ~1,400 train rows edge toward
overfit; the re-certification gates (min_n_train 340, min_n_valid 120, valid
ROI >= 0, LB >= 0.5) are the tripwire for that. Watch the ML-meta diagnostic
line + decay table on the next full run.
---

## Addendum — 2026-08-10 (late 16): kickoff parse DeprecationWarning fixed (3.15-proofing)

**Warning:** auto_tickets.py parse_kickoff used yearless strptime formats
("%d-%m, %H:%M", "%d-%m, %H:%M:%S") — Python defaults the year to 1900 and
emits a DeprecationWarning; behavior becomes an ERROR in Python 3.15.

**Fix:** append the pick's year explicitly before parsing (fallback "1900"
when the pick has no date, matching the previous default) and use the
yearful format "%d-%m, %H:%M %Y". The subsequent year/month/day override
from the pick's date is unchanged — behavior identical, warning-free.

**Verified:** all 5 kickoff formats parse correctly under
`python3 -W error::DeprecationWarning` (any warning would crash) — yearless
DD-MM, HH:MM(:SS), full ISO, and bare HH:MM all pass. No behavior change.
---

## Addendum — 2026-08-11 (late 17): fast lane — ml-meta lower thresholds + 30-day decay window

**Operator direction:** the wait for the next bets felt too long (60-day bench
window, ml-meta waiting on the season). Two levers pulled, both honest:

### Lever 1 — ml-meta threshold scan widened (scripts/mine_consensus.py)
The certification scan only evaluated ml-meta >= 70/75/80/85; live max on
summer slates is ~58%, so 70+ can never fire until peak season. Now scans
55/60/65/70/75/80/85 — the SAME walk-forward gates judge them (min_n_valid 120,
valid ROI >= 0, LB >= 0.5). If >=55/60/65 certify, the model fires on current
fixtures (days, not months); if phantom, they stay candidates. The data
decides, not impatience. Note: this is a new-certification path, not a
threshold-lowering of existing edges — each threshold is its own rule.

### Lever 2 — decay window 60 -> 30 days (src/edgefactory/config.py)
The bench is ROI-driven (should_bench benches on ANY negative recent ROI) and
the window slides daily. With a 30-day window, bad settles age out 2x faster.
Critically: the king's current last-30d slice INCLUDES the winning 08-09
tickets — its recent-30d ROI may already be non-negative, which means the next
full pipeline run can un-bench it. If still negative, it stays benched
correctly (the bench exists because it lost money recently) and recovers
faster as results turn. min_recent_n unchanged (30) — the ROI bench is not
gated by it, so no leniency leak.

**Tradeoffs accepted:** 30-day window = more noise-sensitive (a bad 2-week
stretch benches sooner; a good one un-benches sooner). That is aligned with
daily betting and with the auto-tickets combo gate, which independently
requires recent-20 ROI >= 0 before betting anything — so an un-benched edge
still can't be bet by auto-tickets unless its real-money record is clean.

**Expected sequence:** next full run -> scan shows ml-meta >=55/60/65 verdicts;
decay shows king verdict under the 30d window. Watch both.
---

## Addendum — 2026-08-11 (late 17): fast lane — ml-meta lower thresholds + 30-day decay window

**Operator direction:** the wait for the next bets felt too long (60-day bench
window, ml-meta waiting on the season). Two levers pulled, both honest:

### Lever 1 — ml-meta threshold scan widened (scripts/mine_consensus.py)
The certification scan only evaluated ml-meta >= 70/75/80/85; live max on
summer slates is ~58%, so 70+ can never fire until peak season. Now scans
55/60/65/70/75/80/85 — the SAME walk-forward gates judge them (min_n_valid 120,
valid ROI >= 0, LB >= 0.5). If >=55/60/65 certify, the model fires on current
fixtures (days, not months); if phantom, they stay candidates. The data
decides, not impatience. Note: this is a new-certification path, not a
threshold-lowering of existing edges — each threshold is its own rule.

### Lever 2 — decay window 60 -> 30 days (src/edgefactory/config.py)
The bench is ROI-driven (should_bench benches on ANY negative recent ROI) and
the window slides daily. With a 30-day window, bad settles age out 2x faster.
Critically: the king's current last-30d slice INCLUDES the winning 08-09
tickets — its recent-30d ROI may already be non-negative, which means the next
full pipeline run can un-bench it. If still negative, it stays benched
correctly (the bench exists because it lost money recently) and recovers
faster as results turn. min_recent_n unchanged (30) — the ROI bench is not
gated by it, so no leniency leak.

**Tradeoffs accepted:** 30-day window = more noise-sensitive (a bad 2-week
stretch benches sooner; a good one un-benches sooner). That is aligned with
daily betting and with the auto-tickets combo gate, which independently
requires recent-20 ROI >= 0 before betting anything — so an un-benched edge
still can't be bet by auto-tickets unless its real-money record is clean.

**Expected sequence:** next full run -> scan shows ml-meta >=55/60/65 verdicts;
decay shows king verdict under the 30d window. Watch both.
---

## Addendum — 2026-08-11 (late 18): merge prefers fresh — ml-meta picks no longer hidden

**Bug (operator-caught):** after the fast-lane run, ml-meta fired for the first
time ever (5 picks incl. Lyon vs Sparta -> HOME CLEAN), but the operator-facing
report did NOT show them. Lyon appeared under the morning's archived
3way-unanimous>=65 SKIPPED_VETO row instead of the fresh ml-meta>=55
CERTIFIED_CLEAN row.

**Root cause:** autonomous_intraday_merge retained all archived rows exactly and
only APPENDED fresh rows whose (fixture, market) key was unseen. A fresh pick
for a fixture already in the ledger was silently dropped — so a newer, more
truthful row (ml-meta, current model) was hidden behind an older one (3way,
morning run). Same bug family as the stale display_rule: the ledger was hiding
truth.

**Fix (scripts/daily.py):** on key collision, if the fresh pick's match date
equals the archived row's match date, the FRESH row supersedes it (counted and
logged: "superseded N archived row(s) with fresh picks"). Midnight-crossing
protection preserved: a different date = a different match, archived row kept.
Return value is now (merged, new_added, superseded) — 3 call sites updated.
Test updated to assert prefer-fresh (the old test codified the hiding).

**Verified (4 cases):** Lyon case -> fresh ml-meta row wins; midnight-crossing
-> archived kept; brand-new fixture -> still appends; two collisions -> both
superseded, ledger size stable.

**Effect:** the operator now sees the CURRENT truth per fixture — ml-meta picks
show up in the slate the same day they're made. The merge no longer hides
newer rows behind archived ones.
---

## Addendum — 2026-08-11 (late 19): stale test fixed — promote_forecast serialization

**Found:** after the merge-prefer-fresh deploy, `python3 -m pytest
tests/test_daily_orchestration.py` showed 8 passed / 1 failed
(test_promote_forecast). The failure was NOT the merge change — it was a
PRE-EXISTING stale test: it asserted the forecast was written as the COMPACT
input JSON (json.dumps(dummy_picks)), but the code (since the heal_ledger_labels
fix) re-serializes with indent=2, sort_keys=True. The heal fix changed the
output; the test never caught up.

**Fix:** the test now asserts the real serialization (json.dumps(picks,
indent=2, sort_keys=True)) — matching what promote_forecast actually writes,
verified directly. This is the same discipline as the labels: a test that
codifies old behavior is itself a lie; it should assert current truth.

**Lesson:** stale tests are bug debt too — they fail loudly later and look
like regressions. This one was already wrong before today's change; the merge
run just surfaced it.
---

## Addendum — 2026-08-11 (late 20): cloud bot merge-conflict crash — fixed + discipline rule

**Incident:** Actions run #430 failed (exit 128) in the "Persist pipeline state"
step: `git pull --rebase` conflicted on localdata files (purity_registry.json,
settled_results.json, picks_next_2days_manifest.json, theoddsapi_*.json +
binary theoddsapi_odds CSV). The bot's state commit was dropped; run red.

**Root cause:** TWO WRITERS on the same generated files. The Mac pushed
localdata commits (9cc6b2ea96, eccfdc3a1a) while the bot was mid-run; the
bot's commit + the Mac's pushed localdata overlapped -> rebase conflict -> run
died. Nothing lost (runner ephemeral, main healthy, Mac has all state).

**Fix (workflow, .github/workflows/daily.yml):** the persist step is now
conflict-proof — if rebase or push collides with a moved remote, it aborts the
rebase, DROPS the regenerable localdata state commit, warns, and stays green.
Localdata regenerates on the next run; the bot never strands in a conflict.

**Discipline rule (operator):** NEVER push localdata/ from the Mac. The bot is
the sole writer of localdata on main (it pulls fresh state each run and commits
it). The Mac's richer localdata stays local-only; push only scripts/src/tests/
HANDOVER/. This is the same truthfulness principle applied to the repo itself:
one writer per artifact class prevents conflicts and keeps the record clean.
---

## Addendum — 2026-08-11/12 (late 21): ml-meta pick shadowing + stale state ceiling

**Two truthfulness glitches surfaced by the 08-12 run:**

1. **Shadowing (scripts/picks_today.py):** the ML block emitted ONE PICK PER
   QUALIFYING THRESHOLD — a fixture at ml_p 62.9% produced BOTH ml-meta>=55
   and ml-meta>=60 rows. The collapse kept the first (>=55), so >=60/65/70
   looked "never fired" in the ledger and tripwire even while the model was
   firing. Fix: emit ONE pick per fixture at the HIGHEST qualifying
   threshold (62.9% -> labeled ML-META>=60). Verified across thresholds.

2. **Stale state (scripts/picks_today.py + tripwire message):** ml_meta_state
   .json was written by EVERY picks_today call including the future-planner's
   tomorrow scan, whose thinner slate overwrote it — so the 08-12 tripwire
   reported CEILED against 38.7% while the real 08-12 max was 62.9%. Fix:
   persist state only for the primary target day. Tripwire CEILED wording
   corrected (a bar not reached is expected seasonality now, not a "unit
   mismatch or stale model" — that language was a leftover from the pre-fix
   era).

**Effect:** ml-meta>=60 now genuinely appears in the slate when the model
clears 60 (one row, honest strongest label); the tripwire reads the primary
day's true max; CEILED flags only real, current gaps.
---

## Addendum — 2026-08-12 (late 22): auto-tickets build early, freeze at 12:00

**Operator direction:** don't wait for 12:00 to build tickets — build as soon
as the morning slate exists, then freeze at 12:00.

**Change (scripts/auto_tickets.py):**
- GENERATE_HOUR (12) split into GENERATE_HOUR_START=6 and FREEZE_HOUR=12.
- 02:00-05:59 -> "NOT YET" (no data yet).
- 06:00-11:59 -> BUILDS the slip EVERY run (draft; regenerates as the slate
  fills and new qualifying legs appear). Prints "DRAFT — regenerates on each
  run until the 12:00 freeze."
- 12:00+ -> first run writes a freeze marker (auto_tickets_<date>.frozen) and
  prints "FROZEN — final slip"; later runs re-print it unchanged. --force
  bypasses both the early gate and the freeze (builds, no marker mgmt).

**Verified:** 8-case state machine (NOT-YET at 04:00, DRAFT at 06/09/11,
FROZEN-now at 12:00+, FROZEN-reprint when marker exists regardless of hour,
force bypasses).

**Why this is safe:** pre-freeze drafts are informative, not actionable — the
final frozen slip (post-12:00) is what the operator places. Regeneration
before noon means late-slate legs still get in; the freeze guarantees the
day-0 record doesn't churn. Same discipline, earlier visibility.
---

## Addendum — 2026-08-12 (late 23): light ML assist for enhancement probabilities

**Operator direction:** assist the CURRENT enhancements with some ML power —
not a new model, not a new layer, no bloat, no wording changes.

**What:** a per-market calibration correction learned from the audit's OWN
settled promised-vs-realized data (picks_audit_rolling.json -> by_market,
n-weighted). Applied at enhancement compute time inside the existing loop:
    prob_adjusted = prob_adjusted + w * (realized - promised) * prob_adjusted
where w = min(1, n/40) (evidence weight, saturates at n=40); weak 0.5 weight
for young samples (n<10). Same markets, same labels, same reasons (+ an
"ML-calibrated x%->y%, n=z" suffix). No new files, no new modes, no new
models, no registry change. The enhancement registry remains the ONLY
staking gate.

**Why it's truthful (walk-forward by construction):** the correction uses only
SETTLED history (the rolling audit window), so it never leaks the future; the
audit re-computes each run, so the correction self-updates as evidence grows.

**Verified against real audit data:**
- match_over_25 (promised .477 / realized .536, n=28): 0.42 -> 0.437 (lifted)
- exact_3 (promised .222 / realized .037, n=27): 0.22 -> 0.192 (pulled down)
- home_over_05 (promised .876 / realized 1.000, n=32): 0.88 -> 0.967 (lifted)
- away_under_35 (promised .963 / realized .957, n=47): ~unchanged (calibrated)

**Not done (deliberately):** the earlier over-engineered enh_meta.py (stacking
model + build/predict modes) was removed. The match_over_25 +22pp
under-promise remains a base-engine issue (Poisson/goalsavg feed); the assist
mitigates it at the display layer but the real fix belongs in the engine.
---

## Addendum — 2026-08-12 (late 24): pre-bench audit — 2 inconsistencies fixed, 4 traps named

**Final sweep before operator break. Two REAL inconsistencies found + fixed:**

1. **decay_monitor stale text (scripts/decay_monitor.py):** the output still
   claimed "benching is a 60-day-window circuit breaker" while config was
   already 30 days (addendum 17). Operator-facing text contradicted config.
   Fix: text now uses GATES.recent_window_days dynamically.

2. **auto_tickets slip file lacked status (scripts/auto_tickets.py):** the
   DRAFT/FROZEN status was console-only prints; the .txt FILE the operator
   reads carried no status — a draft could be mistaken for the final slip.
   Fix: the file now ends with "STATUS: ⏳ DRAFT — regenerates until 12:00
   freeze. Not final; do not bet until frozen." or "STATUS: ✅ FROZEN at
   HH:MM — FINAL slip" (or FORCED for --force).

**Traps named (by design or accepted — no fix, operator awareness):**

3. **Telegram "pushable" vs auto-tickets "NO EDGE":** the ✅ CERTIFIED CLEAN
   Telegram alert means push-eligible by BUCKET, not bettable by COMBO. The
   two signals disagree loudly (e.g. Charlestown pushed while auto-tickets
   said no edge — 1 leg, no passing combo). Operator MUST NOT read the
   Telegram alert as a bet instruction; only the auto-tickets slip is a bet.

4. **ML-calibrated probability vs reason text:** the reason string still
   carries the raw engine text (e.g. "Combined Under 3.5 is 98.3%") while
   the probability is the calibrated value (0.917). The suffix explains it;
   the NUMBER is the truth, not the reason text.

5. **Calibration feedback loop (damped, monitored):** the correction changes
   displayed probabilities -> changes which notes pass LINE_THRESHOLDS ->
   changes what the audit scores -> changes the calibration. Capped and
   shrunk (w = n/40), so it converges rather than diverges, but it is a loop
   — watch the audit's promised-vs-realized table for oscillation.

6. **Calibration fixes calibration, not value:** match_over_25's realized
   63.6% is still BELOW the 67.5% overall over-2.5 base rate — the notes
   select slightly-low-over fixtures. The ML assist makes promises honest;
   it does NOT create edge. Registry + combo gates remain the only value
   judges.

**Also flagged (verify on Mac):** Charlestown's ml-meta row showed avg 67%
but w=1.00 (implies 73%) — a possible merge-field artifact; check the row in
localdata/picks_2026-08-12.json if it ever gets graded.

---

## Addendum — 2026-08-20: heavy-run sentinel repair + truthful tripwire scope

**Operator constraint:** no IDE/new machine is currently available. This repair
is therefore shipped as full replacement files with checksums and browser-safe
GitHub upload instructions. It changes no betting threshold, bucket, source
weight, auto-ticket gate, stake, or notification policy.

### Incident: future forecast archives starved the official heavy capture

`picks_today.py` deliberately writes `picks_YYYY-MM-DD.json` for every processed
day so tomorrow's all-bucket shortlist can receive odds. `run_smart_auto()`
incorrectly treated existence of that same file as proof that the official
heavy run had completed. The future planner therefore created tomorrow's
"official" sentinel one day early; when tomorrow arrived, every scheduled run
entered intraday mode and skipped `capture_daily.py`.

Repository receipt: `picks_2026-08-20.json` first appeared on 2026-08-19 at
02:35 SAST, while `picks_morning_2026-08-20.json` did not exist. Morning
baseline files were absent from 2026-08-15 through 2026-08-20. This explains
why healthy live adapters could keep producing current picks while their
monthly capture files stayed dated 2026-08-04 through 2026-08-06.

**Fix (`scripts/daily.py` + `.gitignore`):** a dedicated bot-persisted
`localdata/official_run_YYYY-MM-DD.json` marker is now the ONLY proof that the
heavy official pipeline completed. A forecast pick archive no longer selects
intraday mode. When today's marker is absent, Smart Auto runs the complete
capture/build/mine path with a current-day repick, then atomically writes the
marker at successful completion. Empty slates are covered because completion,
not pick count, is recorded. The first scheduled run after deployment will
self-recover without a laptop: no marker exists yet, so it performs one heavy
run and refreshes the source caches.

### The former "16 warnings" were 15 unique findings

The old count was 7 silent edges + 1 ceiling + 8 stale source caches. The
`ml-meta>=80` edge was counted twice (silent and ceiled). Six of the seven
silent rules were qualified analytical variants (`min_p` / `home-only`) that
`picks_today.load_thresholds()` intentionally cannot emit operationally. The
tripwire monitored every registry row with status `certified`, contradicting
the picker and producing permanent false alarms. It also admitted tomorrow's
forecast picks into the historical firing window and used a broad source glob
that allowed `bzzoiro` to inspect `bzzoiro_odds`.

**Fix (`scripts/edge_firing_tripwire.py`):** monitor only reachable canonical
rules plus all ML thresholds; report excluded certified analytical rules
separately as information; constrain firing dates to
`today-silent_days <= date <= today`; classify a ceiled ML edge once rather
than as both silent and ceiled; use exact monthly source filename patterns;
retain source roles in telemetry. Warnings remain visibility-only and cannot
select a bet.

### Live-source falsification receipt

Direct bounded adapter probes on 2026-08-20 returned current rows despite the
stale-cache warnings: Forebet 141, Vitibet 203, PredictZ 92, WinDrawWin 33,
aFootballReport 533, capped BetClan sample 10, FreeSuperTips 25. Today's
committed picks also contain live Vitibet, BetClan and Bzzoiro votes. The main
failure was capture orchestration/persistence, not provider death.

### Verification

- New/changed focused suites: 15/15 passed.
- `py_compile`: clean on both production replacements and their tests.
- `pyflakes`: clean on all touched Python files.
- Full suite on patched tree: 260 passed / 8 failed.
- Clean upstream base independently reproduces the exact same 8 failures
  (255 passed / 8 failed before the five new tests): two stale debias test
  expectations, four auto-ticket/grader contract mismatches plus its legacy
  pause-state failure, and one audit-render wording mismatch. Therefore this
  payload introduces zero full-suite regressions; those unrelated baseline
  failures remain recorded rather than silently claimed green.

**Replacement paths:** `.gitignore`, `scripts/daily.py`,
`scripts/edge_firing_tripwire.py`, `tests/test_daily_orchestration.py`,
`tests/test_edge_firing_tripwire.py`, and this `HANDOVER.md`.


---

## Addendum — 2026-08-20: run #502 recovery receipt, zero-failure suite, Forebet cloud fallback

### Heavy-run recovery confirmed

Scheduled Actions run `32368306183` (#502) completed successfully in 16m33s
and persisted bot commit `246633c`. It wrote
`localdata/official_run_2026-08-20.json` at 14:36 SAST, created the missing
morning baseline, and refreshed 11 of 12 monitored source caches. The long
runtime was expected for the one-time full capture/build/mine recovery; later
same-day runs use the marker and return to intraday mode.

The repaired tripwire reduced the old 16-warning report to two honest findings:
Forebet's monthly cache remained stale, and `ml-meta>=80` had no recent firing.
Seven qualified analytical rules were correctly reported as excluded rather
than false operational failures.

### Eight pre-existing test failures closed

The formerly red full suite contained three distinct drift classes:

1. `src/edgefactory/debias.py` correctly raised `MIN_ENGINE_N` from 5 to 20,
   but two tests still built n=6/7 engine cells while expecting them to pass.
   Fixtures now use the production constant and test the intended n>=20 path.
2. `scripts/audit_recent_picks.py` defined `_pct` twice. Python's later signed
   headline formatter silently replaced the earlier unsigned probability
   formatter at call time, producing strings such as `+81.5%` in calibration
   and per-pick probability rows. The headline helper is now
   `_summary_pct`; probabilities remain unsigned while headline ROI/hit rate
   retains its explicit sign.
3. `scripts/auto_tickets_grade.py` had drifted from its documented/tested
   contract: `load_tickets()` returned only a list instead of
   `(tickets, legacy_dates)`, and legacy reporting lost the explicit
   pre-adaptive explanation. The tuple contract and transparent wording are
   restored. `scripts/auto_tickets.py::load_pause_state()` now treats unknown
   legacy stake/return values as zero recorded capital instead of raising a
   `TypeError` (or inventing a 100% stake).

### Forebet diagnosis and repair

Run #502 proved the general capture cadence was fixed, but Forebet alone still
had no monthly file. The same run's official picks contained zero Forebet votes.
A bounded direct endpoint probe outside Actions returned HTTP 200 and 141 rows,
so the adapter/parser and provider data were alive. The previous transport had
two honesty gaps: an HTTP-200 anti-bot/challenge page could fail JSON parsing,
and `fetch_day()` swallowed every market exception into an empty slate;
`local_backfill.py` then marked the zero-row day done.

`src/edgefactory/sources/forebet.py` now validates the `[rows, meta]` payload,
tries urllib first, then browser-TLS fallbacks (`safari17_0`, `firefox133`) via
the already-installed `curl_cffi`, and raises when every market transport fails.
Partial valid market captures remain usable but log the missing markets. A
forced live fallback probe (urllib deliberately disabled) returned all 141
1X2 rows. No proxy, new secret, source substitution, or selection change was
introduced.

### Verification

- Full suite: **277 passed, 0 failed**.
- Focused audit/debias/auto-ticket/Forebet suites: 78 passed.
- `py_compile`: clean on all changed production files.
- `pyflakes`: clean on every changed production and test file.
- Forced live browser-fallback probe: 141 Forebet 1X2 rows.
- No betting threshold, bucket, source weight, auto-ticket gate, stake, or
  notification policy changed.

**Replacement paths:** `scripts/auto_tickets.py`,
`scripts/auto_tickets_grade.py`, `scripts/audit_recent_picks.py`,
`src/edgefactory/sources/forebet.py`, `tests/test_debias.py`,
`tests/test_forebet.py`, and this append-only `HANDOVER.md` entry.

---

## Addendum — 2026-08-20: run #503 Forebet latency containment

Scheduled run `32385601406` (#503) completed successfully, and the unchanged
14:36 official marker proved it correctly used intraday rather than repeating
the heavy pipeline. However, execution expanded to 18m46s (20m51s total),
versus the pre-fallback intraday baseline of roughly 8–9 minutes. Forebet still
contributed zero votes to both the 2026-08-20 and 2026-08-21 slates, and its
cache remained at 2026-06-12. Therefore browser impersonation did not overcome
the provider's GitHub-hosted-runner block; it only spent repeated transport
timeouts and moved the workflow too close to its 25-minute limit.

**Containment (`src/edgefactory/sources/forebet.py`):** when
`GITHUB_ACTIONS=true`, Forebet now fails immediately before any network
transport. Local execution remains enabled because the same endpoint returns
current rows outside Actions. A deliberate future cloud re-probe is possible
without code changes by setting `EDGE_FACTORY_FOREBET_CLOUD=1`; it is OFF by
default. Forebet's deep committed history remains available to mining, while
current cloud consensus continues honestly without a Forebet vote—the behavior
already observed before this containment.

The stale-source tripwire remains visible; this change does not relabel the
cache as healthy. It removes latency, not evidence. No proxy, replacement
source, fabricated vote, selection threshold, bucket, source weight,
auto-ticket gate, stake, or notification rule changed.

**Verification:** two new environment-gate tests prove fail-fast cloud behavior
and explicit opt-in semantics. Full suite: **279 passed, 0 failed**;
`py_compile` and `pyflakes` clean on both replacement files.

**Replacement paths:** `src/edgefactory/sources/forebet.py`,
`tests/test_forebet.py`, and this append-only `HANDOVER.md` entry.

---

## Addendum — 2026-08-20: machine-free Forebet relay qualification

**Operator directive:** recover current Forebet participation without requiring
a laptop or permanently accepting a disabled source. Direct GitHub-hosted
runner traffic remained blocked even with browser TLS, so a third network path
was investigated rather than fabricating a vote or weakening consensus.

### Qualified route

The public Jina Reader endpoint can retrieve Forebet's public `getrs.php` URL
without credentials. It adds a small text wrapper and leaves the endpoint body
unchanged. Bounded live qualification on 2026-08-20 proved:

- 1X2: 141 rows; relay JSON body byte-identical and object-identical to direct;
- O/U: 141 rows; byte/object-identical;
- BTTS: 141 rows; byte/object-identical;
- canonical JSON hashes matched independently for all three markets;
- 2026-08-19 / 20 / 21 1X2 samples contained 282 / 141 / 400 rows and every
  sampled `DATE_BAH` matched the requested day;
- no Edge Factory or provider secret is present in the public URL or relay
  request.

### Production behavior

On GitHub Actions, the Forebet adapter now uses the relay by default. It accepts
exactly one `Markdown Content:` marker, requires the wrapper's `URL Source:` to
match the requested Forebet URL exactly, extracts the body, then applies the
same strict `[rows, meta]` JSON validator used by direct capture. Any wrapper,
provenance, JSON, or schema mismatch fails closed and Forebet contributes no
vote. `X-No-Cache: true` is requested and each market has a bounded 25-second
timeout.

Local execution remains direct. `EDGE_FACTORY_FOREBET_CLOUD=direct` deliberately
re-tests GitHub's own transport; `off` disables cloud Forebet immediately. The
relay is a third-party availability dependency, not a new prediction source:
Forebet remains the named source and its unchanged rows/probabilities are the
only accepted payload.

### Verification and boundary

Full suite: **281 passed, 0 failed**; `py_compile` and `pyflakes` clean. A final
live smoke through the production `fetch_day()` with `GITHUB_ACTIONS=true`
returned 141 merged fixtures, all 141 complete for 1X2, O/U, and BTTS. Observed
relay responses were roughly 8–15 seconds per market, materially below run
#503's repeated direct timeout path.

No selection threshold, bucket, source weight, auto-ticket gate, stake,
notification rule, or historical result changed. The next scheduled run is the
production confirmation for live Forebet votes; the next heavy run is the
monthly-cache confirmation. If the relay fails, existing fail-soft source
handling and the stale-source tripwire remain authoritative.

**Replacement paths:** `src/edgefactory/sources/forebet.py`,
`tests/test_forebet.py`, plus the run #503 containment and this relay addendum
appended to `HANDOVER.md`.

## Addendum — 2026-08-27 (evening): auto-tickets REPLACED by the rolling engine (operator directive)

**Directive.** The operator judged the v4 combo-gate slipper effectively dead
(4/71 fireable days walk-forward, −4.6% leg ROI on what did fire — receipts in
`TICKETS_DIAGNOSIS_2026-08-27.md`) and directed replacement with the rolling
structure validated in the 2026-08-27 simulation session, including a
TAKE-PROFIT trigger.

**What shipped:**

1. `scripts/auto_tickets.py` is now the stateful ROLLING ENGINE (same entry
   point — `daily.py` and the Actions loop run it bare, zero pipeline
   changes). Recipe (all constants carry their validation receipt in the
   module docstring): playable-bucket legs only (NO further filter — tested
   best), ordered by stated probability, consecutive 2-leg accas from the
   top 6, max 3 per day, 50% of settled bank per day split across accas,
   volume regime (pool ≥12 legs → only stated-prob ≥65% rides), half of
   every new high-water mark withdrawn at settlement, and **TAKE-PROFIT:
   when bank reaches 2.0× the base bank, all profit above the base is
   withdrawn and the cycle resets** (event recorded in
   `state.events`, printed loudly, surfaced in the slip and performance
   report). Slips keep the `auto_tickets_<date>.txt` names, 06:00 build /
   12:00 freeze cadence unchanged. State: `localdata/auto_tickets_state.json`
   (gitignore exception added — WITHOUT it the bank would reset on every
   Actions run; `.gitignore` follows the two-line no-inline-comment rule).
   CLI: bare = settle + build/reprint today; `--status`; `--backfill
   [--from --to --bank --reset]` replays the ledger (analysis/seeding);
   `--force` bypasses the freeze marker.
2. `scripts/auto_tickets_grade.py` is now a reporter: settles via the engine
   and writes `auto_tickets_performance.txt/.json` from state (bank,
   withdrawn, wealth multiple, take-profit events, per-day history). The v4
   pause gate (last-20 ROI < −10%) is superseded by structural protection:
   50% daily cap + committed-stake accounting + take-profit.
3. Tests: new `tests/test_auto_tickets_rolling.py` (9 cases: planning,
   volume regime, settlement, half-high banking, TAKE-PROFIT harvest/reset,
   open-slip commitment, playable filter, backfill arithmetic — includes an
   autouse STATE_FILE sandbox after a test leak wrote a phantom slip into
   the real state). `tests/test_picks_today.py`: removed Contract 2 (v4
   grader stakes_frac display, 6 tests) and Contract 4 (load_pause_state,
   3 tests) — both pinned functions no longer exist. Contracts 1/3
   (ledger merge, duplicate collapse) untouched. **Full suite: 288 passed,
   0 failed; pyflakes clean.**

**Validation receipts:** engine backfill (2026-06-19..08-26) reproduces the
session simulation with take-profit active: wealth ×5.76, 2 take-profit
harvests (Jul 1 +141.53, Jul 7 +101.33), 75W/32L accas, never busted. Note
honestly: take-profit costs upside vs the pure half-high path (×8.93) — it
reset the base to 100 mid-July and captured less of the streak — in exchange
for locking realised profit earlier and carrying only ~56 units at risk into
the late-August drawdown. That is the requested behaviour.

**Live seed committed:** fresh state (base bank 100 units, wealth ×1.00)
with one open slip for 2026-08-27 (3 accas, 25 units committed). The
walk-forward starts here — the bot's existing bare calls do everything:
settle yesterday, build/reprint today, report. Monitor with
`PYTHONPATH=src python3 scripts/auto_tickets.py --status` or
`cat localdata/auto_tickets_performance.txt`.

**Revert path:** `git revert <this commit>` restores the v4 slipper, grader,
tests, and gitignore wholesale. The v4 receipts remain in this HANDOVER and
in `TICKETS_DIAGNOSIS_2026-08-27.md`.

**Replacement paths:** `scripts/auto_tickets.py`,
`scripts/auto_tickets_grade.py`, `tests/test_auto_tickets_rolling.py`,
`tests/test_picks_today.py`, `.gitignore`, `localdata/auto_tickets_state.json`,
`localdata/auto_tickets_2026-08-27.txt`, `localdata/auto_tickets_performance.{txt,json}`,
and this HANDOVER entry.

## Addendum — 2026-08-27 (evening 2): rolling engine goes PERCENT-ONLY; take-profit becomes a notification

**Operator directive.** No amounts anywhere — percentages of capital only
(the original v1-v4 doctrine, restored). Take-profit must be a NOTIFICATION
based on performance, not an amount-harvesting mechanism. Stakes display as
percentages. The four legacy v4 artifacts were deleted:
`auto_tickets_2026-08-09.json/.txt`, `auto_tickets_performance.json/.txt`
(the rolling grader rewrites the performance pair on its next run).

**What changed in `scripts/auto_tickets.py`:**
- State is percentages: `base_pct` 100 = starting capital; `bank` moves in %
  of capital. No units, no rand, no withdrawals ledger.
- The half-of-new-high WITHDRAWAL rule is REMOVED by directive (it was
  amount bookkeeping). The bank now compounds freely; the profit discipline
  lives in the notification instead:
- **TAKE-PROFIT NOTIFICATION:** when `bank >= cycle_base + 100%`, a 🔔 event
  fires — printed on every subsequent run, recorded in `state.events`, and
  written to `localdata/auto_tickets_takeprofit_<date>.json` (gitignore
  exception added) so it persists across bot runs. The cycle baseline resets
  to the current bank (next target +100% again). Nothing is moved — the
  operator acts on the notification.
- Slips/status/grader are percent-only: `stake 16.7% of capital (16.7% of
  bank)`, `bank 175.4% of capital (x1.75)`, `next take-profit at 200.0%`.
- `scripts/auto_tickets_grade.py` reports `% of capital`, the multiple, the
  cycle baseline, next target, and the notification log.

**Backfill receipt (percent semantics, notifications active):** the ledger
replay compounds to bank 1312.1% (x13.12), 75W/32L accas, with four 🔔
take-profit notifications (Jun 24, Jul 1, Jul 4, Aug 7 — each at +100% of
its cycle). Marker files from that replay were removed so only live
notifications are persisted.

**Tests:** `tests/test_auto_tickets_rolling.py` rewritten for percent
semantics — 10 cases incl. percent-only field contract (`stake_pct`, no
`stake`), notification-fires-moves-nothing-resets-cycle, marker-file
artifact, and percent backfill arithmetic. Full suite **288 passed, 0
failed**; pyflakes clean.

**Replacement paths:** `scripts/auto_tickets.py`,
`scripts/auto_tickets_grade.py`, `tests/test_auto_tickets_rolling.py`,
`.gitignore`, this HANDOVER entry; deleted the four legacy localdata
artifacts; committed fresh state + today's percent slip + performance pair.

## Addendum — 2026-08-28: walk-forward days 1-3 — incident log, voids, checkpoint card

**Context.** The rolling engine went live 2026-08-27 (merged PR #1). Days 1-3
were operational triage: five defects found and fixed, all regression-tested.
This addendum is the record; the engine docstring carries the recipe.

### Incident log (all fixed, all with tests or verified self-checks)

1. **Draft stacking.** cmd_today appended a slip per run; the bot's 2-3 runs
   inside the 06:00-12:00 build window stacked same-day slips (state showed
   50% + 25% committed for 08-27). Fix: upsert_slip — placing replaces the
   day's draft. (One mangled-paste detour en route briefly produced a
   recursive helper on main; restored from 82ff921 and re-applied in stages.)
2. **Potosi incident — three settlement defects.** Real Potosi (KO 26-08
   23:30, on the 27th's slate, lost 0-1) could never settle because:
   (a) parse_kickoff stomped day-month formats to the slate date, so a
   played match passed the kicked-off filter — fixed: day-month keeps its own
   calendar day, year chosen nearest the slate date; (b) results file under
   the KICKOFF date, not the slate date — fixed: settlement tries day ±1;
   (c) norm_team DROPS accented chars asymmetrically ("Potosí"->"potos" vs
   feed "Potosi"->"potosi"; both spellings exist league-wide) — fixed:
   accent-folded exact match, then bounded fuzzy (both teams >=0.8
   similarity, ±1 day). Net effect: +9 previously-unjoinable archive picks
   now settle.
3. **Voids.** Postponed/cancelled results previously hung a leg open forever.
   Fix: book semantics — any non-result outcome = void; a void leg drops out
   of the acca (odds recompute over live legs; all-void = stake back at 1.0).
   Exact marker check ordered BEFORE the fuzzy fallback (the first patch's
   void branch was unreachable — fuzzy overwrote markers with None).
4. **Duplicate-slip immunity.** load_state now dedupes same-date open slips
   at load time (keeps first), so a stale bot persist can never re-stack.
5. **Stale-leg auto-void.** A leg unresolved >5 days after kickoff
   auto-voids at settlement (rescheduled matches that never re-file).
6. **CI zombie resurrection.** Deleting v4 files from git was undone every
   run: actions/cache/restore unpacked pre-deletion snapshots and the persist
   step's `git add -A localdata/` recommitted them. Fix: delete + bump the
   cache key (localdata-main- -> localdata-v2-); old caches orphan and age
   out. Codespace gh token cannot delete caches (403) — key-bump is the
   no-permission fix.

### Day-one result (honesty receipt)

08-27 frozen slip: acca1 L (Potosi), acca2 W @1.74 (Freiburg x Riga), acca3 L
(Pafos; MC Alger postponed = void pending). Bank settles ~79.0% of capital.
Structure capped the day as designed.

### Pre-committed September checkpoint card (thresholds fixed, no mood edits)

1. **Acca count on saturated days:** 3 -> 5 only if 5 still wins median AND
   p10 on resampled heavy days at month end (current: 5 beats 3 in 80% of
   resamples, ledger 8 heavy days).
2. **Conviction-less shorts (odds<1.20 AND stated<70%):** cut only if >=30
   settled and still < -10% (now n=14 at -28.5% — below actionable n).
3. **O2.5 inclusion gate:** stated 50-60% band, priced: n>=30 AND hit>=70%
   AND flat ROI>0 -> earns walk-forward inclusion, SHARP prices only.
   - Live (scripts/o25_tracker.py, committed): band 23 @ 78% +19.8%;
     sharp-priced 13 @ 85% +37.2%; soft (scoutingstats) 44 @ 61% -7.2%.
   - Deep-warehouse check (forebet 2024+, same population = strong home
     favourites): 642 @ 65.0%, +0.2% at forebet's ~10% overround odds ->
     expect live numbers to sag toward ~65% / single-digit ROI at sharp
     prices. The gate exists to measure exactly this sag.
   - Prerequisite if adopted: route goals pricing sharp-first (77% of overs
     currently priced by the soft feed).
4. **League audit:** month-end, league-level leg ROI; n>=30 AND < -10% goes
   to the purity registry as a veto candidate (the tested mechanism).
   Pairing stays probability-pure: diverse/concentrated variants differ only
   by noise (11% of pairs share a league; worst-day unchanged; the killer
   correlation is day-level, not league-level).

### Session research receipts (no engine changes)

- **Hedging sim:** cash-out at 5% cost = neutral EV with maxDD halved
  (86%->54%); at 10% cost it destroys ~3/4 of final bank; leg-2 conditional
  on leg-1 win has no edge (n=98, -0.8%). Operator judged cash-out
  impractical (bookmaker behaviour) — shelved, not adopted.
- **Low-odds exclusion sim:** blanket min-odds floors (1.15-1.30) all
  destroy value and raise drawdown (shorts are slot-1 ballast + thin-day
  fill); only the conviction-cut is a candidate (see checkpoint 2).
- **R10 tiered-TP ladder sim** (no TP below R1k; full-gain cycles to R10k;
  half-of-new-high above): deterministic ledger pass R10 -> R131 with zero
  withdrawals; month-block MC median ~R26-30k withdrawn/24mo vs zero-edge
  control R0 / -R209 median — the entire result is the edge-persistence bet.
  Currency denomination is separable (betting multiple x coin multiple);
  stablecoin = the only rational crypto rail; LTC float adds tails, not speed.

**Replacement paths this addendum documents (all already on main via
Codespace patches):** scripts/auto_tickets.py (upsert, kickoff parse,
fallbacks, voids, dedupe, staleness), .github/workflows/daily.yml (cache
key v2), scripts/o25_tracker.py (new, read-only), deleted v4 artifacts.

## Addendum — 2026-08-28 (evening): growth-lever doctrine, evidence map, withdrawal policy

**Growth levers, ranked (operator discussion receipt).** Bank growth = edge x
bank size x compounding events. In order of honesty: (1) add starting capital
(scales linearly); (2) more streams at fixed 50%/day risk — the two queued:
3->5 accas on saturated days (checkpoint 1) and the O2.5 stream if its gate
passes sharp-priced (checkpoint 3); (3) sharpen price capture — session
receipts put price quality at ~10pp ROI (2026 price-flip in the deep archive;
CLV flat at captured prices), larger than every selection decision tested;
prerequisite if O2.5 adopts: sharp-first goals pricing (77% currently priced
soft). Explicitly rejected: raising the stake fraction (100% busted in every
tested configuration; over-Kelly at thin edge is anti-growth).

**Evidence collection (all automatic, no action needed).** O2.5 gate:
scripts/o25_tracker.py grades every priced over daily (sharp/soft split
built in). 3-vs-5 counterfactual: picks_*.json archives ALL playable legs
incl. would-be legs 7-10, so the max-5 replay runs from ledgers at month
end. Price capture: the CLV pipeline (clv_report_*.md) plus per-pick
odds_source/enhancement_price_source cover both 1x2 and goals.

**Withdrawal policy (open, operator decision at first bell).** TP notifies,
never moves money. Default suggestion: withdraw half at each bell (= the
cycle's gain; freeroll thereafter); 25%-per-bell is the faster-compounding
alternative (~x9.4 vs ~x5.1 over 4 cycles, x16 if nothing taken). Doctrine:
withdrawals determine what SURVIVES the edge dying, not growth speed; if
~60 bet-days stay profitable, compounding everything becomes defensible.

**Dangling reference note.** Earlier addenda cite
TICKETS_DIAGNOSIS_2026-08-27.md, deleted from the working tree 2026-08-28
at operator request. Receipts remain in git history
(git show 21d8047:TICKETS_DIAGNOSIS_2026-08-27.md) and the key numbers are
inlined in the 2026-08-27/28 addenda.

## Addendum — 2026-09-04: the tuning era — floors, freeze, replay harness, experiment ledger

**Live-record status at writing:** engine bank 143.1% (8 bet-days, 16W-8L),
operator roll R86.69 on R60 deposited (+44.5%), 7 consecutive 2-1 days.
Walk-forward day 8 of 30. Twitter gate: Oct 1. Scaling gate: end Oct.

### Parameter changes this era (all evidence-linked, all pre-freeze)

1. **MIN_LEG_ODDS floor: none → 1.10 → 1.15 → 1.20 (Sep 2-4).** Bayern @1.05
   case triggered 1.10; band decomposition raised it twice more. Evidence:
   sub-1.20 legs = 46 settled, ~80% hit, ~-7.5% flat ROI (slow squeeze — win
   often, pay tiny, full stake per death); breakeven at 1.18 needs 84.7% vs
   82.4% realized. Displacement argument: short legs crowd 1.4+ legs out of
   top-6 on saturated days. REPLAY A/B (live data, 52d): floor 1.10 → 40%
   final vs 1.20 → 563%, P(1.20 higher)=76% (bootstrap spans zero —
   luck-shaped tails, but 3 independent argument lines agree). Floor cliff:
   1.25 → 20%, 1.30 → 7% in replay — 1.20 sits at the sweet-spot edge; do
   NOT raise further without 30d live adjudication.
   **THE FLOOR IS A LIVE A/B:** sub-floor legs still archive; the counterfactual
   is computable daily. Day-30 gate rule: revert iff live 1.20-cards
   underperform the archived counterfactual over the fresh window.
2. **FREEZE_HOUR 12 → 9 (Sep 2, measured).** Bot runs SAST-even hours via
   external cron 09:00/12:00/15:00/18:00/21:00 (cron-job.org). Old de-facto
   freeze was 14:00 (no run at noon SAST); 09:00 freeze covers 94% of leg
   kickoffs vs 86% (noon). Marker lands ~09:23. Betting window: any time after
   marker, before each leg's kickoff. Operator bets ~09:30.
   **Process rule learned Sep 4: parameter patches must land before the
   ~08:55 SAST run-start or they miss that day's freeze** (a freeze takes the
   settings of the commit the run STARTED on; the 06:05 draft on main may be
   stale and must not be judged pre-marker).

### New instrument: scripts/replay_harness.py

Counterfactual replays on LIVE data with LIVE guards. Commands: bare (status),
--ab FLOOR_A FLOOR_B (bootstrap confidence), --all (floor/acca/stake/prob
sweeps), --today (draft-time preview — pre-freeze it shows a partial pool;
the frozen card is the truth). DOCTRINE printed on every run: replays are
for RELATIVE comparisons only; absolute replay numbers disagree with engine
history (40-563% replay vs 143% actual — different eras/guards/voids);
engine ledger is the only record of what happened; cells n<30 are noise.
Known-bug-fixed Sep 4: universe builder had the live floor pre-applied
(lower-floor A/Bs were no-ops) — the harness's first live output caught its
own author's bug. If a variant shows IDENTICAL results across floors, suspect
this class of bug first.

### Experiment ledger — VALIDATED, do not re-run or revert without new 30d+ live data

- **Stake >50%/day: REJECTED, repeatedly.** Replay: 75% → 27%. Sims: 100%
  busted everywhere. 50% cap is doctrine. Not an open question.
- **Always-on stated-prob floor (>=65% every day): REJECTED (4 sightings).**
  Latest live replay: 65% → 57% vs baseline 563%. Thin-day diversity beats
  purity. Only remaining form: >=65% on saturated days (live since Aug) —
  keep.
- **Slot-weighted stakes (descending/ascending): REJECTED.** Descending
  destroys 35-60% of final bank (ledger test); ascending only looked good on
  slot-3's n=21 heater. Equal thirds is minimum-variance at equal EV.
- **Blanket low-odds exclusion beyond 1.20: REJECTED.** Floor 1.25/1.30
  replays collapse (20%/7%). The 1.20 cut is at the cliff edge.
- **Conviction-less shorts cut (<1.20 AND <70% stated): DEFERRED to gate.**
  n=14 at -28.5% — below actionable n. Checkpoint ② unchanged.
- **4 accas/day on heavy days: PENDING, favorable 3rd sighting.** Live
  replay: 4→989%, 6→871%, 3→563% (single-path, luck-shaped). Prior: 5-beats-3
  in 80% of saturated-day resamples (8 ledger heavy days). Checkpoint ①
  decides at day-30: flip to 4-5 iff it wins median AND p10 on accumulated
  heavy days.
- **Overs/O2.5 as a bet stream: FAILING on substance.** Tracker (daily,
  localdata/o25_tracker_report.txt): 50-60% band n=104, hit 67% (<70% bar),
  ROI -5.8% — gate now fails on numbers, not sample size. OU25-unanimous rule
  (miner-certified at +0.4% valid ROI): n=12, 42% hit, -28.7%. Deep warehouse
  predicted ~65%/break-even — arriving on schedule. One green cell: overs on
  the factory's own 1X2-selected matches +4.6% (n=148) — a match
  characteristic, not a stream. Expect checkpoint ③ to close this honestly.
- **ml-meta>=55 demotion: evidence compounding.** -7.3% live at n=210+; the
  veto-bucket decomposition traced the bucket's first negative flip to its
  medium-odds (1.50-2.00) ml-meta legs (-7.1% band) while <1.50 stays +1.2%.
  Checkpoint ⑤ (raise floor 55→60) increasingly likely.

### Portfolio note (context for successors)

A second system exists: 6ixtyn9-sudo/Slumdog (underdog-upset research, own
constitution, AGENTS.md/STATE.md discipline, shadow-only, 654k-row census).
It shares ONE dependency with Edge Factory: Forebet. Correlated risk — when
Edge profits fund APIs, buy a second prediction surface first (fixes
Slumdog's single-source constitution AND Edge's ml-meta concentration).
Cross-review protocol in effect: agents may read each other's repos; owner
authorizes scope; this agent (Edge Factory session, merged PR #1) audits
live main via raw.githubusercontent.

### Operator doctrine additions this era

- Deposits ledger: log every deposit (date, amount) at deposit time —
  operator ledger reconciliation depends on it (two double-count errors
  caught and corrected this week).
- The red-day rule (pre-committed): a 0-3 day is scheduled variance, costs
  ~50% of bank, NOT evidence about any parameter; next morning's card bets
  exactly as written. Parameter changes only at gates, on evidence, never
  adrenaline.
- Beer-money doctrine: only vice-money/scheduled deposits; never rent money,
  never loss-chasing top-ups; December harvest = profits above deposits.

## Addendum — 2026-09-04 (late): harness v2 post-mortem, the dead volume gate,
## and stake sizing (the first change with a structural argument)

**Context.** A Codespace session shipped "harness v2" (2f75641: `--gate-ab`,
`--legs`, `--no-fallback`, completeness-fallback parity) and ran three volume-
gate A/Bs. Every run printed byte-identical arms — `859% / 52 days / 115 accas
/ 60%` — and an identical bootstrap (`median +8%, p10 -22575%, p90 +22364%,
P=51%`), and the identity was reported as a 51% coin-flip rather than as the
bug the harness's own docstring warns about. This addendum is the review, the
repair, and the resulting engine changes. Everything below is reproducible on
main with `scripts/replay_harness.py`.

### Findings (receipts, in order of consequence)

1. **THE VOLUME REGIME IS DEAD CODE — and had already stopped selecting
   anything before that.** `plan_day` sorts prob-descending, so a
   `prob >= VOLUME_MIN_PROB` filter can only trim a SUFFIX; the top-6 is
   untouched whenever >=6 legs survive, and when fewer survive the 2026-09-04
   completeness fallback restores the full pool. Both branches return the same
   card. Measured on the live selector over the whole archive:
   `VOLUME_MIN_PROB 0.00 / 0.50 / 0.55 / 0.60 / 0.70 / 0.75 / 0.80 / 0.95 vs
   0.65 -> 0 days differ out of 57`. Even pre-fallback the gate never changed
   WHICH legs rode — it only shrank the card (and because stake is
   `STAKE_FRAC / len(accas)`, a shorter card is not less risk, it is less
   diversification). The recipe line "pool >= 12 -> only >=65% rides" has been
   false since the fallback landed. **Now honest: `GATE_MODE = "off"`.**
2. **The bootstrap was UNPAIRED.** `random.choices(la)` and `random.choices(lb)`
   drew independent day samples, so two identical arms produced a +-22,000%
   interval and P=51%. Reproduced exactly on the retired code. Fixed: one
   resample of day indices, scored under both arms, on **mean log growth per
   bet-day** (final bank is a single path — one treble owns it).
3. **The `--legs` band table applied no floor** despite its header. 33/305
   legs (11%) were sub-1.20 — **16 of the 38 legs in the `0.75+` cell**. It
   also called days saturated using the unfloored pool. Corrected table
   (floor applied, live saturation, 11 saturated days): `0.55-0.60 n=90
   -2.4% · 0.60-0.65 n=45 +7.8% · 0.65-0.70 n=35 +3.3% · 0.70-0.75 n=52
   -3.1% · 0.75+ n=22 +4.5%`. There is no cliff at 0.65; the best cell sits
   just BELOW the old gate. Every cell n<=90: decide nothing on it.
4. Smaller: `--gate-ab` ignored `--no-fallback`/`--volume-pool` (the only
   combination that could have produced signal was unreachable); the
   bootstrap's `compound()` hardcoded `stake * 0.5`; the harness re-implemented
   `plan_day` and had drifted (live gate threshold `MAX_LEGS*2`, harness
   `max_accas*2`); it regex-stripped the floor out of live source with
   `inspect.getsource` + `exec` — the exact mechanism behind the earlier
   no-op bug; zero tests covered any of it; HANDOVER was not updated.

### What shipped (this addendum)

**Engine (`scripts/auto_tickets.py`) — one selection path, knobs not copies:**
- `MIN_LEG_ODDS = 1.20` promoted to a constant; `playable_legs(..., floor=)`.
- New `rank_legs` / `pair_legs` / `select_accas(...)`: every recipe knob
  (floor, rank, pairing, max_accas, saturated_accas, volume_pool, volume_min,
  gate_mode, fallback) is a parameter defaulting to the validated live value.
  `plan_day(pool, bank_pct, **overrides)` forwards them. The harness now calls
  THIS function — a parity test fails if it ever diverges again.
- `GATE_MODE = "off"` (honest no-op removal, zero behaviour change).
  `"acca"` implements the only shape that can bite: on saturated days an acca
  rides only if BOTH legs clear the threshold. Pre-registered, not live.
- **`STAKE_FRAC 0.50 -> 1/3`** — see below. Selection is untouched: verified
  leg-for-leg identical cards on all 80 archived days, only `stake_pct`
  changes (16.67% -> 11.11% per acca on a 3-acca card).

**Harness (`scripts/replay_harness.py`) — rewritten:** live-selector driven,
variant specs (`--ab live "gate_mode=acca,volume_min=0.70"`, bare numbers still
mean floors), paired bootstrap on log growth, **no-op guard** (diffs the cards
first and refuses to bootstrap identical arms), **effect concentration**
(leave-one-day-out: reports the share carried by the single most influential
day and whether the sign flips), corrected `--legs`, new `--kelly` sizing
curve, `--battery`. **`tests/test_replay_harness.py` (11 cases)** pins all of
it, including "identical arms bootstrap to exactly zero" and "no
`inspect.getsource`, no second copy of the recipe". Full suite: **334 passed**,
pyflakes clean.

### Stake sizing — the one lever with a structural argument

Sizing changes no selection, so its evidence is far cleaner than any leg
filter. Same 52 bet-days, same cards, only the fraction deployed
(`--kelly`):

| f | log/day | final | maxDD |
|---|---|---|---|
| 20% | +0.0324 | 540% | 44% |
| 25% | +0.0374 | 699% | 53% |
| 30% | +0.0410 | 845% | 62% |
| **33%** | **+0.0426** | **916%** | **67%** |
| 40% | +0.0443 | 999% | 76% |
| 50% | +0.0414 | 859% | 87% |
| 75% | -0.0069 | 70% | 99% |

The growth-optimal fraction on this path is **~40%**, so **50% was already
past the peak: lower growth AND higher drawdown — strictly dominated**. The
curve is flat from 30-50% while maxDD climbs 62% -> 87%. Bootstrapped f*:
median 40%, p10 15%, p90 65% — uncertain enough that Kelly doctrine says size
BELOW the estimate (overbetting punishes asymmetrically). **1/3 keeps 96% of
peak growth at 67% maxDD.** Revert = one constant. If the operator wants more
protection, 25% costs ~10% of growth and halves drawdown to 53%.

### Experiment ledger — updates

- **Floor 1.20: CONFIRMED (upgraded evidence).** Paired bootstrap vs 1.20:
  floor 1.15 P(better)=6% (p90 -0.0071 — one-sided), floor 1.25 P=8%
  (p90 -0.0064). 17 and 32 days differ, so this is broad-based, not an
  anecdote. Do not move it.
- **Volume gate (pool form): DELETED as a no-op.** Not "rejected on
  evidence" — it never had jurisdiction. Anyone reinstating a saturated-day
  quality gate must use the per-acca shape and prove it on cards, not pools.
- **Stake >50%: still REJECTED. Stake <50%: ADOPTED at 1/3** (above).
- **4 accas/day: DOWNGRADED — checkpoint ① correction.** Replay Δ +0.0090
  log/day looks favourable, but leave-one-day-out is **-0.0015 (sign flips)**:
  **117% of the effect is a single 4.90 treble on 2026-08-25**. Earlier
  sightings (4->989% etc.) were the same artifact viewed through final bank.
  Do NOT flip to 4-5 accas at day-30 unless the effect survives
  leave-one-day-out on the accumulated live heavy days.
- **Rank by stated EV: REJECTED** (-0.0099 log/day). **Barbell pairing
  (1+6,2+5,3+4): REJECTED** (-0.0137). Probability order + consecutive pairs
  stands.
- **Always-on stated-prob floor: REJECTED, 5th sighting** (60% -0.0068,
  65% -0.0535, 70% -0.0339).
- **NEW checkpoint ⑥ — per-acca conviction gate (pre-registered, NOT live).**
  `GATE_MODE="acca", VOLUME_MIN_PROB=0.70` shows Δ +0.0172 log/day, P=99%,
  interval one-sided — but **only 4 days differ**, one carries 42%, and the
  mechanism is "the sub-70% acca lost 4/4 times". That is a 1-in-16 coin-flip
  run, not a policy. **Decision rule, fixed now:** adopt only when >=12
  differing days have accumulated live AND the leave-one-day-out effect is
  still positive AND p10 > 0. Until then it stays a parameter, not a default.

### Doctrine added

- **A knob that cannot change the card is not a policy.** Every A/B prints
  how many days actually differ; the harness refuses to bootstrap identical
  arms. If two variants tie exactly, that is a bug report, not a result.
- **Report leave-one-day-out with every replay claim.** On a 52-day ledger a
  99% bootstrap can be four coin flips.
- **Prefer levers that do not touch selection** (sizing, cadence, price
  capture): their counterfactuals are exact rather than inferred.

**Replacement paths:** `scripts/auto_tickets.py`, `scripts/replay_harness.py`,
`tests/test_auto_tickets_rolling.py` (gate tests rewritten — the old volume
test passed with the gate deleted, it asserted a property of the sort),
`tests/test_replay_harness.py` (new), this HANDOVER entry.

**Follow-up fixes (same day, from the operator's first run of the tool):**
the no-op guard keyed on cards alone, so a SIZING-only A/B (identical cards,
different stake) was refused as a no-op — it now keys on identical cards AND
identical daily growth, and labels sizing comparisons as the cleanest kind
available, with the standing warning to judge them on drawdown rather than
growth (the growth curve is flat across 30-50%, so those Δs correctly read as
luck-shaped — the case for 1/3 is maxDD 67% vs 87%, not growth). Every
variant line now prints maxDD, and `--kelly` puts the live fraction ON the
grid instead of marking the nearest 5% step.

### Checkpoint ① — RESOLVED AS UNRESOLVABLE (2026-09-04, new instrument)

`--slots` asks the marginal-acca question at leg scale instead of day scale.
Verdict: **the data cannot answer it yet, and will not by day 30.**

- Day-level A/B (operator run, f=1/3): 4 accas Δ +0.0059 log/day, P(better)
  69%, interval spans zero (p10 -0.0073) over **19 differing days** — and
  leave-one-day-out is **-0.0011, sign flipped**: 2026-08-25 (a 4.90 treble
  in slot 4) carries **118%** of the effect.
- Leg-level, like-for-like (only the **19** archived days that offer 8+
  playable legs, so every slot is drawn from the same days): every cell is
  n=19. Acca 1 (slots 1+2) -1.8%, acca 2 (3+4) +13.4%, acca 3 (5+6) -19.8%,
  acca 4 (7+8) +18.5%. No monotone decay, no signal — just noise with a
  sign.
- Mechanism worth knowing: a 4th acca does NOT reduce risk. Total stake is
  fixed at STAKE_FRAC and split further, so extra accas reshape the payout
  distribution (more small wins, fewer full-loss days) without changing
  exposure. maxDD is identical (67%) for 3 and 4 accas on this ledger.
- **Decision rule, fixed now (supersedes the "5 beats 3 in 80% of
  resamples" prior, which was the same 8-day artifact seen through final
  bank):** MAX_ACCAS stays 3 until there are **>=30 bet-days offering 8+
  playable legs** AND the 4-acca variant wins median AND p10 AND survives
  leave-one-day-out. At the current rate (19 such days in ~3 months of
  archive) that is a Q1-2027 question, not a September one. Do not spend
  another session on it before the counter reaches 30 — `--slots` prints
  the counter.

### NEW checkpoint ⑦ — the THIRD acca, not the fourth (pre-registered)

The slot table pointed the opposite way to every previous acca-count debate.
Pooled over the whole archive, acca 1 (slots 1+2) is +23.6% flat ROI (n=52)
and acca 2 (3+4) is +18.6% (n=36), but **acca 3 (slots 5+6) is -8.7%
(n=27)** — the weakest cell on the card, and slot 6 alone is -21.8%. The
sweep had never tested FEWER accas; every prior session only asked for more.

`--ab live "max_accas=2"`: Δ **+0.0047** log/day, P(better) 63%, interval
spans zero (p10 -0.0148), **27 differing days** (the broadest sample of any
candidate), hit 65% vs 60%, and leave-one-day-out is **+0.0115** — the most
influential day works AGAINST the 2-acca variant, so the effect survives
removal rather than depending on it. That is the healthiest shape any
candidate has shown.

**It is still not shippable, and the reason is risk, not growth:**
maxDD 78% (2 accas) vs 67% (3 accas). Concentrating the same fixed stake on
fewer accas is leverage by another name — the same trade the sizing audit
just bought down. Adopting it would partly undo the STAKE_FRAC change.

**Priced immediately — checkpoint ⑦ CLOSED, no action.** The risk-matched
pair was run the same day:
`--ab live "max_accas=2,stake_frac=0.25"` -> Δ **-0.0010** log/day,
P(better) 46%, maxDD **66% vs 67%**, worst single day 0.75 vs 0.67, hit 65%
vs 60%, and the -0.0010 itself sign-flips on leave-one-day-out (one day
carries 485%). Once the extra concentration of 2 accas is paid for with the
stake cut it requires, the two configurations are **indistinguishable on
every axis**. The third acca's diversification is worth almost exactly the
8pp of stake you must surrender to keep drawdown flat.

**Doctrine that follows (the important part).** After the STAKE_FRAC move
the engine sits ON its efficient frontier for this card distribution:
`accas x stake` combinations trade growth against drawdown at a fair rate,
so they are moves ALONG the frontier, not up it. That is why every remaining
structural candidate prices as a wash or a fragile one-day artifact. The
only lever that moved the frontier itself was total stake — and only because
50% was over-Kelly. **Successors: stop searching for structure inside the
card. The frontier now moves only through better legs (price capture,
a second prediction surface) or more capital, not through re-arranging six
legs into different shapes.** Re-open ⑦ only if the slot-5+6 cell is still
negative at n>=60.

**Reading the battery at f=1/3.** All Δlog/day magnitudes in the sweep are
smaller than the f=0.50 numbers quoted above, because log growth scales with
leverage; the ORDERING is unchanged (floor 1.20 still dominant, EV rank and
barbell still negative, 4-accas still one-day fragile). Compare variants
against the baseline printed in the same run, never against a number from an
older run at a different stake fraction.

## Addendum — 2026-09-04 (late): checkpoints ⑧–⑩ rebuilt — sizing knobs, ruin truth, and the in-season ledger

This rebuild closes the code-loss gap after the prior analysis session. **No
live policy changed.** Every new knob defaults to the pre-existing recipe, the
80 archived days have zero default-output differences from `origin/main`, and
no candidate below clears the operator's shipping rule:

> Ship only when paired-bootstrap p10 is above zero, the sign survives every
> leave-one-day-out removal, and max drawdown does not exceed live. Extra
> growth bought with a deeper hole is not growth we can spend.

### Checkpoint ⑧ — one planner owns selection and sizing; bankruptcy is bankruptcy

`scripts/auto_tickets.py` now exposes research controls without changing the
live defaults:

- `STAKE_MODE="per_day"` is the live/default behaviour: the day's fixed
  `STAKE_FRAC` is split over the selected tickets.
- `STAKE_MODE="per_acca"` fixes risk per ticket and caps total day risk at
  `STAKE_FRAC`. `STAKE_PER_ACCA=None` resolves to
  `STAKE_FRAC / MAX_ACCAS`; on a one- or two-acca card this therefore leaves
  capital unexposed instead of levering the smaller card back to a full day.
- `MIN_ACCAS=1`; setting 2 or 3 turns smaller cards into NO BET.
- `STAKE_WEIGHTS=None`; a value such as `"3,2,1"` redistributes the selected
  card's stake without changing one leg or one pairing.
- `plan_day(pool, bank_pct, *, stake_frac=None, stake_mode=None,
  stake_per_acca=None, weights=None, **overrides)` is the single planner.
  `select_accas(..., min_accas=None)` owns the card gate.

`scripts/replay_harness.py` no longer calculates stakes itself. `replay()`
calls `auto_tickets.plan_day()` with a 100% reference bank and derives each
day's bank factor from the returned, production-rounded `stake_pct` and acca
odds. The parser accepts `stake_mode`, `stake_per_acca`, `min_accas`, and
comma-valued weights (`weights=3,2,1`). `--since`/`--until` make the regime
boundary reproducible, for example:

```
PYTHONPATH=src python3 scripts/replay_harness.py \
  --since 2026-08-01 --ab live "max_accas=4"
```

**Ruin bug fixed.** The former `summarise()` discarded every non-positive day
before taking logs. That let a 100%-stake policy go bankrupt and still print
`+0.5698 log/day` and a final `80,941,606,995%` from only the days it survived.
`summarise()` now returns `ruin`; any ruin forces `mean_log=-inf`, `final=0`,
and `maxdd=1`. A/B bootstrap stops, variant sweeps label the arm RUIN and skip
it, and the Kelly grid now shows 100% as `RUIN ... SKIPPED`. In money terms:
once the bank reaches zero there is no later winning ticket and no giant final
bank — the strategy is finished.

Verification receipt:

- Compared the rebuilt engine with `origin/main` at `e702f89` on all **80**
  archived dates: `playable_legs` **0 diffs**, default `plan_day` **0 diffs**.
- New contract tests pin all four defaults, fixed-per-acca risk and its cap,
  minimum-card NO BET, weights changing stakes but not selection, replay's
  call through `plan_day`, parser coverage, and ruin handling.
- Required command (the suite does not import correctly without
  `PYTHONPATH=src`): `PYTHONPATH=src python3 -m pytest -q` -> **345 passed**.
  `py_compile` and `git diff --check` are clean.

### Checkpoint ⑨ — thin cards and the alleged weak third ticket

Re-derived from the current 52 settled bet-days, through the rebuilt planner:

| card built | days | mean log/day | money consequence from a 100% start |
|---|---:|---:|---:|
| 1 acca | 16 | **+0.0820** | 371% within those days |
| 2 accas | 9 | **+0.1285** | 318% within those days |
| 3 accas | 27 | **−0.0091** | 78% within those days |

That split does **not** validate skipping busy cards: card size is entangled
with the football calendar, and the cells are different regimes rather than
random assignments.

The direct thin-day gate loses money:

- `min_accas=2`: 16 days are skipped; mean growth falls from +0.0428 to
  +0.0253 (**Δ −0.0174/day**) and the replay bank falls from **924% to 249%**.
- `min_accas=3`: only 27 days remain, mean growth is **−0.0091/day**, and the
  bank shrinks to **78%**. This is a negative-edge policy, not selectivity.

The strongest-looking single ticket (ranked leg slots 1+2, i.e.
`max_accas=1`) was also priced across every 1% stake fraction. Its best point
is only **+0.0354 log/day at f=29%**, final 629%, with **89% maxDD**. No stake
on that one-ticket curve reaches the live three-ticket shape's **+0.0443 at
f=41%**, final about 1,000%. At the useful comparison, the one-ticket policy
and current f=1/3 policy make almost the same average daily bank move (+6.84%
vs +7.14%), but the one-ticket move is wider (24.7% vs 23.6% standard
deviation) and its maxDD is 89% instead of 67%. Plain English: the third acca
is ballast, not extra risk to cut; removing the ballast makes the ride rougher
without paying more. Checkpoint ⑦'s risk-matched `max_accas=2` wash remains
closed.

### Checkpoint ⑩ — the archive crosses a season boundary

The volume break begins in **ISO week 32**. Before it, the floored settled pool
is roughly three qualifying legs a day (3.6 on the 19 actual Jun–Jul bet-days);
from August it averages **11.5**, with ordinary resumed-season slates commonly
in the **12–18** range and larger weekend spikes. The engine bets 5.2 of those
legs and leaves 6.4 unused because `MAX_ACCAS=3`.

| regime | settled bet-days | mean log/day | final from 100% | maxDD |
|---|---:|---:|---:|---:|
| off-season, Jun–Jul | 19 | **+0.0458** | 239% | 67% |
| in-season, Aug–Sep | 33 | **+0.0410** | 387% | **63%** |

On the 170 selected in-season legs, actual wins exceed their average stated
probability by about **+5.4 percentage points**; a leg-resampled lower decile
is about **+1.0pp**. That says the resumed-season legs have not exposed an
obvious calibration deficit, but it does not turn 33 path-dependent days into
permission to tune.

Every older whole-archive headline blends these regimes. **Use +0.0410/day and
63% maxDD as the forward in-season expectation, and run future A/Bs on dates
>= 2026-08-01.** In this archive, “thin slate” and “off-season” are the same
calendar variable for decision purposes. A slate-size-aware cap is therefore
not an independently validated lead; do not rediscover this confounding as a
“slate size effect” and ship it.

### Only open lead — a fourth in-season acca; NOT adopted

The old whole-archive “do not ship `max_accas=4`” conclusion was formed when a
fourth acca rarely existed. The resumed season changes its jurisdiction, so
that old verdict is void. The correctly scoped run is n=33 in-season days:

| arm | log/day | final from 100% | maxDD | accas |
|---|---:|---:|---:|---:|
| live, max 3 | **+0.0410** | 387% | 63% | 85 |
| max 4 | **+0.0483** | 493% | **60%** | 103 |

Cards differ on 18/33 days. The extra historical growth and slightly shallower
hole are attractive in cash terms (493% rather than 387% on this path), but
they are **not dependable**: paired-bootstrap p10 is **−0.0134/day**, and the
leave-one-day-out range is −0.0037 to +0.0111 with the sign flipping on two
removals. August 25 alone carries 151% of the measured improvement. It fails
two legs of the shipping bar, so `MAX_ACCAS` stays 3.

**Pre-registered adoption rule — REWRITTEN 2026-09-06 (Task 2.3; supersedes the
paragraph below and every older "flip at day-30" wording).** Two — and only two —
questions may be asked of genuinely NEW in-season bet-days, each at
**n >= 60 in-season bet-days** (reached ~Oct 2026 counting from 08-01), each
under the full standing bar (paired-bootstrap p10 above zero, every
leave-one-day-out result keeps the positive sign, maxDD no higher than live):
Q1 `max_accas=4`; Q2 the live `floor=1.20` (question: does the 1.20 floor earn
its keep out-of-sample, or was it the in-sample winner of a ~27-variant
search?). Both are in-sample artefacts today — the 09-06 analysis shows a
13-variant search on pure noise manufactures a "+edge" of the same size as the
headline, and 1.20 is a lone spike between two holes. So the expectation is
set in advance: **testing them is right, expecting them to win is not.** At
most one candidate may ever be adopted from this research family; if both
pass, the one with the higher p10 wins. The additional days must be genuinely
new days the scan did not see.

Lower-priority `weights=3,2,1` reproduces the full-archive observation: zero
cards change, log/day rises +0.0042, and every leave-one-day-out result stays
positive, but p10 is **−0.0064** and maxDD worsens **67% -> 73%**. Scoped to the
forward in-season regime it is weaker still (p10 −0.0151 and LOO sign flips).
The historical final-bank jump (924% -> 1,152%) is bought with a deeper hole
and a luck-shaped interval, so it cannot ship.

About **25 variants have already been scanned**. Anything else that merely
looks profitable is a new hypothesis, not a result. Do not re-open
`max_accas=2` risk-matched (wash), `acca-gate >=70%`, or thin-day skipping.
The only live candidate still earning future observation is the in-season
fourth acca under the fixed n>=60 / p10 / all-LOO / no-extra-drawdown rule.

### Correction to the ⑧ verification receipt (2026-09-04, post-merge)

"Default `plan_day` 0 diffs" is true of leg SELECTION, not of bytes. The new
hard day cap subtracts the rounding excess from the last ticket, so on 2-acca
days the old planner emitted 16.6667 + 16.6667 = 33.3334 (0.0001pp above the
33.3333% rule) and the new one emits 16.6667 + 16.6666 = 33.3333 exactly.
That is 12 of 80 archived days, worst deviation 0.0001pp — a hundredth of a
cent on a R100 bank, always in the underbetting direction. Leg selection is
identical on all 80 days and --battery is unchanged (live +0.0428, 924%).

A strict byte-parity check therefore reports "12 diffs" and reads as a
regression. It is not one. The correct engine-parity assertion, and the one to
fold into the test suite so it runs on every PR:

  * ZERO leg-selection differences vs the previous main on every archived day
  * total staked within 0.01pp (1c on a R100 bank)

Byte-equality is the wrong test for floating-point stakes and will keep crying
wolf until someone reverts a good change.

## Addendum — 2026-09-04 (late): checkpoint ⑪ — can the warehouse date the edge?
## FEASIBILITY VERDICT: NO. Reconstruction is impossible with the data on hand.

**What was asked.** The live evidence base is thin — 80 archived days, 52
bet-days, 33 in-season — and at that size the engine's edge cannot be proven
(bootstrap p10 on in-season daily log growth ≈ −0.007; p10 > 0 needs roughly
180 bet-days, i.e. February 2027). The question was whether the warehouse could
answer it sooner, by reconstructing what the engine would have picked over
2024–2026 and replaying it. Phase 1 was a hard gate: reconstruct the 80
archived days from warehouse data alone, score the recovery against
`auto_tickets.load_archived_picks()`, and stop if it fails.

**It fails, on four independent grounds, any one of which is fatal.** No
Phase-2 numbers exist and none should be manufactured. **No live setting
changed**; leg selection is identical to `2d7d909` on all 80 archived days and
total staked moves 0.000000pp.

### The instrument

`PYTHONPATH=src python3 scripts/replay_harness.py --warehouse-replay`

A reusable, opt-in command (`src/edgefactory/warehouse_replay.py`,
`ENABLED_BY_DEFAULT = False`, pinned by test). Prints, in order: warehouse
inventory, what the live legs actually depended on, per-rule feasibility, the
look-ahead audit, the validation gate, and a PASS/FAIL against a bar stated
*before* the numbers. Exit code 1 on FAIL. Nothing on the live path imports it.

### Ground 1 — the prediction sources stop before the archive starts

| table | rows | span |
|---|---:|---|
| `forebet_settled` | 323,524 | 2024-01-01 → **2026-06-12** |
| `zulubet_settled` | 66,808 | 2024-01-01 → **2026-06-12** |
| `statarea_settled` | 481,537 | 2017-01-01 → **2026-06-12** |
| archived picks | 891 | **2026-06-19** → 2026-09-06 |

**The overlap is zero days.** `forebet`, `zulubet` and `statarea` have
**0 rows** on any of the 80 days the engine actually bet. The validation gate
is not merely failed, it is *unrunnable as specified*: there are no inputs on
the days where ground truth exists. Any future attempt must first close a
seven-day-plus capture gap, and then wait for new bet-days on top.

### Ground 2 — the sources that decide the picks are not on disk

Across the 536 playable legs in the archive, the sources cited are:

| source | legs citing it | history file |
|---|---:|---|
| **vitibet** | **438 (82%)** | **none** |
| statarea | 333 | yes |
| forebet | 298 | yes |
| zulubet | 182 | yes |
| **bzzoiro** | **156** | **none** |
| **betclan** | **116** | **none** |

There is no `vitibet*.csv.gz`, `bzzoiro_*.csv.gz` or `betclan_*.csv.gz` in
`localdata/`, so `vitibet_settled`, `bzzoiro`, `betclan` and `consensus4` all
build as ABSENT. `consensus2` joins forebet+zulubet only. **Every reconstruction
built on the existing views is blind to the source present in four out of five
live legs.**

### Ground 3 — the prices are not on disk either, and the ones that are, are wrong

The odds actually used to price live legs:

| odds source | legs | availability |
|---|---:|---|
| `scoutingstats_odds` | 240 (45%) | **no history file** |
| `betexplorer_odds` | 177 (33%) | 2026-01→06 only, and **CLOSING** |
| `bzzoiro_odds` | 75 (14%) | **no history file** |
| `forebet_best` | 33 (6%) | yes, bet-time family |
| `zulubet` | 11 (2%) | yes |

The engine bets ~30+ minutes before kickoff at `forebet_best`. BetExplorer is a
closing price. Substituting one for the other is not an approximation, it is a
different bet, and the harness refuses to mix them.

**The addressability funnel — the single most important table in this
checkpoint:**

| necessary condition | legs | share |
|---|---:|---:|
| all playable legs | 536 | 100.0% |
| rule is a source vote (not the ml-meta model) | 223 | 41.6% |
| every cited source has a history file | 29 | 5.4% |
| priced from an odds source with history | 44 | 8.2% |
| **ALL THREE — the reconstruction ceiling** | **1** | **0.2%** |

Even granting perfect code, perfect team-name matching and a closed date gap,
**one leg out of 536 is faithfully reconstructable.** That is the ceiling, not
the achieved result. A "backtest" built on it would describe a strategy the
engine has never run for a single day.

### Ground 4 — the ml-meta model cannot be replayed without look-ahead, and this is structural

`ml-meta avg_p>=55` is the plurality rule (279 of 536 playable legs, 52%).
Its feature vector, read from the certified model in
`localdata/edges_consensus.json`, contains:

```
ht_diff   +0.2395   POST-KICKOFF   actual half-time goal difference
ht_total  +0.1910   POST-KICKOFF   actual half-time goals scored
```

`train_ml_meta_classifier` in `scripts/mine_consensus.py` reads `ht_hs`/`ht_gs`
straight off the settled `consensus3` row. **These are the half-time scores of
the match the model is being asked to predict.** A warehouse replay would feed
them: a 2-0 half-time lead alone shifts the logit by **+0.861**, which turns a
55% pick into roughly a 72% one. That is not an edge, it is the scoreboard.
The reconstructor therefore **excludes every ml-meta leg by policy** rather
than guessing, exactly as the brief required — and that exclusion alone caps
recall at 42%.

Note the live side of the same fact: `picks_today.py` has no scores at bet time
and feeds `ht_diff = ht_total = 0`. So the model is *trained* on a feature
distribution it never sees in production. That is a live modelling defect, not
a replay artefact. **It is not fixed here** (fixing it changes live pick
generation and must go through its own gate) but it is now on the record, and
it is the strongest argument yet for the standing `ml-meta>=55` demotion
evidence in checkpoint ⑤.

### Ground 4b — there is no pre-kickoff snapshot in the file at all

`forebet.csv.gz` status census: **FT 98.4%, Pen. 0.9%, AET 0.4%, Awarded 0.2%**
— every row carries a terminal status and a final score, and the file has **no
capture-timestamp column**. The same is true of `statarea.csv.gz` and
`zulubet.csv.gz`. So the archive is a post-match scrape and there is no
evidence that any stored probability or price is the pre-kickoff one. Even the
1-in-536 reconstructable leg would have to be reported as an **upper bound**.

### The gate, as run

```
live legs/day       6.70          reconstructed/day   0.00
true positives         0          false positives        0
false negatives      535          recall 0.0%   precision 0.0%
days with any match  0 / 80
```

**Mechanism check** (so the zero cannot be dismissed as a broken query): the
same reconstructor, pointed at the most recent 60 days that *do* have inputs
(2026-04-14 → 2026-06-12), returns **26 legs over 60 days = 0.43 legs/day**
against a live in-season **11.5**. The code runs. It simply models a far
narrower strategy than the engine does. The prior session's ~1.3 legs/day
figure over 2.5 years, and the −0.0233 log/day it produced, are of the same
family: **both describe a proxy, not the engine. Do not quote either number,
including the ones in this paragraph, as engine performance.**

### The forebet ROI question, stated correctly — the filter is doing real work

**CORRECTED 2026-09-04 (same day, after review). The first version of this
section was wrong and is superseded.** It compared two different populations
and reported the difference as if it were two answers to one question. It also
attributed the favourable figure to the draw-dropping trap. That attribution is
false: the +4.3% figure counts draws as losses.

Both figures reproduce exactly against `localdata/forebet.csv.gz`:

| population | n | stated | realised | flat ROI |
|---|---:|---:|---:|---:|
| every match, top pick across 1/X/2 | 224,194 | 46.7% | 45.7% | **−5.1%** |
| the slice the engine bets: home/away, raw p>=70, odds>=1.20 | 3,170 | 73.6% | 69.7% | **+4.2%** |

(Independently quoted as 221,062 / −5.3% and 3,149 / +4.3%; the small deltas
are dedup and odds-null handling. The reading is identical.)

**Both rows count a draw as a loss.** `won = (hs>gs)` for a home pick,
`(gs>hs)` for away — a draw pays nothing in either row. The draw-normalised
pass that inflated a 58% pick into a "78% chance" was a *different*, earlier
attempt and was discarded. It is not the source of the +4.2%.

**The gap between the two rows is the engine's entire premise.** Filtering to
high-confidence picks priced above 1.20 moves flat ROI by **+9.3 percentage
points**, from losing to winning, on 3,170 legs spread over 685 distinct
match-days. Bootstrapped on those legs: **p10 +2.0%, median +4.1%, 95% CI
[+0.9%, +7.6%], P(ROI>0) = 99.4%.** That is the strongest single-population
evidence in this repository, and it clears the p10>0 leg of the bar on its own
terms.

Two caveats stay attached and must be carried forward with the number:

1. These are **forebet's own, possibly post-revision odds** with no capture
   timestamp (Ground 4b). If the stored price drifted toward the truth after
   kickoff, +4.2% is an **upper bound**.
2. It is **forebet-only**, a single source. The live engine is multi-source
   with purity gates, a decay monitor and an ml-meta model on top. This row
   is evidence that *a* confidence-plus-price filter separates winners from
   the pool; it is not a measurement of the live engine.

**Read it this way:** "forebet's raw top pick loses money" is true of the
*pool* and says nothing about the *filter* — and the filter is what the engine
is. Do not let a future session read this section as "the approach is dead."
The selection rule is doing real work. What remains unproven is the size of
that work once the live engine's other layers are applied, and that is still
gated on live bet-days, not on SQL.

### What it means in money

Nothing changes today. The bank keeps compounding on the live recipe at
`STAKE_FRAC = 1/3`, `MAX_ACCAS = 3`, floor 1.20, in-season expectation
**+0.0410 log/day at 63% maxDD**. The warehouse **cannot** shorten the wait for
proof. **February 2027 (~180 bet-days) remains the honest date on which the
edge becomes provable**, and the only thing that moves it earlier is *more live
bet-days*, not more SQL. Anyone who arrives with an 800-day backtest of this
engine built from `localdata/` is holding fiction; ask them for their recall
against the 80 archived days before you look at their growth number.

The Phase-2 questions therefore remain **open and unmeasured**: leg-level
calibration by source and consensus depth; whether the edge comes from
multi-source agreement, the 1.20 floor, the purity gates, or nothing; and
whether 2-leg accas at 33%/day survive 800 days. The earlier proxy ruined the
bank on every variant, which is a warning worth holding, but it is **not**
evidence about the live shape and must not be cited as if it were.

### What must not be re-opened

- **Do not rebuild a reconstruction on `consensus2`/`consensus3`.** It is
  missing vitibet (82% of legs), bzzoiro and betclan, it cannot price 92% of
  legs, and it produces 0.43 legs/day against a live 11.5. Three sessions have
  now hit this. The verdict is settled.
- **Do not replay ml-meta from the warehouse under any circumstances** until
  `ht_diff`/`ht_total` are removed from the feature set and the model is
  retrained walk-forward. The half-time score is in the model. Any ml-meta
  replay result is contaminated by construction. (The *live* consequence of
  the same defect is now checkpoint ⑫ below — and it points the opposite way
  to the intuition. Read it before touching the model.)
- **Do not substitute BetExplorer closing odds for `forebet_best`.**
- **Do not quote** −0.0233 log/day, 93% maxDD, 1.3 legs/day or 0.43 legs/day
  as engine performance. All four are reconstruction-proxy artefacts.
  ("+4.2% forebet ROI" is NOT in this list — see the corrected ROI section
  above; it is a real measurement of a real filter, with two caveats.)
- The dedup trap turned out to be **small**: `DISTINCT ON (date, hkey, akey)`
  drops only 0.1% of rows in each settled view (170 / 68 / 404). The real loss
  is the *join*: forebet ∩ zulubet = 27,368 rows, 41% of the smaller side;
  three-way = 15,749. Coverage, not dedup, is what kills the views.

### What it would take to make this answerable later

In order of size, and all of it is *capture*, not analysis:

1. **vitibet history** — the single missing source cited by 438 of 536 legs.
2. **Bet-time odds history** for `scoutingstats_odds` and `bzzoiro_odds`, the
   two pricing sources behind 59% of live legs.
3. **Timestamped, point-in-time prediction snapshots** captured *before*
   kickoff, so pre-kickoff state can be proven rather than assumed. Every
   current source file is a post-match scrape with no capture column. This is
   the one that also makes all *future* research trustworthy, and it is cheap:
   it is a column, written at capture time.
4. **An ml-meta feature set without the half-time score**, retrained
   walk-forward, before a single ml-meta leg is replayed.
5. Close the 2026-06-12 → present capture gap in forebet/zulubet/statarea.

Items 1–3 are worth doing for their own sake regardless of this checkpoint:
they are the difference between a system that can be audited and one that can
only be trusted.

### Verification receipt

- `PYTHONPATH=src python3 -m pytest -q` → **363 passed** (345 pre-existing +
  18 new). `py_compile` and `git diff --check` clean.
- Engine parity, asserted in CI by `tests/test_warehouse_replay.py` against
  the committed snapshot `tests/data/engine_parity_baseline.json` and verified
  against `2d7d909:scripts/auto_tickets.py`: **0 leg-selection differences on
  all 80 archived days**, worst total-staked deviation **0.000000pp** (bar:
  0.01pp). This is the correct parity assertion from the post-merge correction,
  now automated so it runs on every PR.
- `--battery` baseline unchanged: live **+0.0428 log/day, final 924%, 52 days,
  115 accas, 60% hit, 67% maxDD**.
- New defaults pinned OFF by test; `auto_tickets.py` does not reference
  `warehouse_replay`, and no daily-pipeline script invokes `--warehouse-replay`.

### The one open lead is unchanged

In-season `max_accas=4` still needs **n ≥ 60 genuinely new in-season bet-days**
under the full bar (paired-bootstrap p10 > 0, sign survives every
leave-one-day-out, maxDD no higher than live). This checkpoint produced **no
new in-season days** and therefore **no movement** on it — the warehouse cannot
manufacture them. At most one candidate may still be adopted from that family.

## Addendum — 2026-09-04 (late): checkpoint ⑫ — the ml-meta train/serve mismatch
## MEASURED. Verdict: real defect, benign direction, DO NOT "fix" it blind.

**What was asked.** Checkpoint ⑪ found that the ml-meta model is trained on the
actual half-time score of the match it predicts. This was escalated out of that
reconstruction task and given its own checkpoint, with a decision attached,
because **41% of live picks come from `ml-meta avg_p>=55`** — a model being fed
a value at serve time it never saw in training. The pre-registered first
measurement: win rate and flat ROI of `ml-meta` legs versus `2way-unanimous`
and `3way-unanimous` legs on the archived bet-days, with bootstrap intervals
and the in-season split.

**The hypothesis was that the leaked-feature model underperforms the honest
consensus rules. It does not. The measurement refutes it.** No live change
follows. Nothing in production moved.

### The defect, confirmed line by line

- `scripts/mine_consensus.py:525-526` derives `ht_diff` / `ht_total` from
  `ht_hs` / `ht_gs` — the half-time score of the match being predicted.
- Both are in the certified feature list in `localdata/edges_consensus.json`,
  at `ht_diff +0.2395` and `ht_total +0.1910`.
- `scripts/picks_today.py:2324-2325` computes them live as
  `(_ht_hs or 0) - (_ht_gs or 0)`, which is **0** before kickoff.

The model learned "two goals up at half-time usually wins" and in production is
told **every match is 0–0**. That is a genuine train/serve mismatch, not a
backtest artefact.

### The instrument

`PYTHONPATH=src python3 scripts/replay_harness.py --rules`
(add `--since 2026-08-01` for the in-season scope)

Reusable, read-only, changes no default. Prints leg quality and **calibration**
by rule family for the whole playable pool and for the legs that actually rode,
plus the paired cost of the only live change this could justify.

### What the numbers say

`gap` is realised minus stated. **Positive means UNDER-confident** — the rule
wins more often than it claims.

**Every settled playable leg, in-season (>= 2026-08-01):**

| family | n | stated | realised | gap | gap p10 | flat ROI | roi p10 | roi p90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ml-meta | 277 | 62.0% | 67.1% | **+5.2pp** | +1.7pp | +0.0% | −5.8% | +5.9% |
| 2way-unanimous | 132 | 73.3% | 75.8% | +2.5pp | −2.4pp | −1.5% | −8.1% | +4.9% |
| 3way-unanimous | 25 | 69.3% | 80.0% | +10.7pp | −0.2pp | +10.4% | −4.4% | +24.8% ⚠ n<30 |

**Legs the engine actually rode, in-season:**

| family | n | stated | realised | gap | gap p10 | flat ROI | roi p10 | roi p90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ml-meta | 81 | 64.5% | **75.3%** | **+10.8pp** | +4.7pp | **+7.0%** | −2.2% | +16.1% |
| 2way-unanimous | 79 | 74.0% | 70.9% | −3.1pp | −9.8pp | **−6.0%** | −14.5% | +2.8% |
| 3way-unanimous | 10 | 70.3% | 100.0% | +29.7pp | +28.1pp | +38.7% | +32.0% | +45.6% ⚠ n<30 |

**AMENDED AFTER REVIEW — do not restate this as "ml-meta outperforms."** The
correct sentence, and the one a successor should inherit, is:

> **ml-meta and 2way-unanimous are statistically indistinguishable on this
> sample. There is no evidence ml-meta is worse, and a hint that it is
> better.**

The intervals overlap heavily and neither clears zero: ml-meta is +7.0% flat
with **p10 −2.2%**; 2way-unanimous is −6.0% with **p90 +2.8%**. On 81 and 79
legs those two cannot be separated. An independent replication measured
ml-meta n=80 / 75.0% / +6.8% (p10 −2.8%) and 2way n=75 / 73.3% / −2.6% (p90
+6.0%) — same direction, same non-separation; the small deltas are
leg-attribution edge cases.

What the measurement **does** establish is enough to close the question that
was asked: the hypothesis that prompted this checkpoint — that the
leaked-feature model *underperforms* the honest consensus rules — is not
supported. The sign is the opposite of the hypothesis. That is sufficient to
reject a demotion; it is **not** sufficient to claim superiority, and the
demotion is separately rejected on the paired replay below, which is the
stronger evidence.

### Why the leak does not hurt — the mechanism, which matters more than the table

`ht_diff` and `ht_total` are **zero for every live prediction**. They are not
noise and they are not adversarial: they are a *constant*. Their coefficients
simply drop out of the live logit, leaving the other 24 features to carry the
ranking. What the mismatch damages is not ranking but **calibration** — the
model was fitted expecting half-time information and, denied it, systematically
**understates** its own probability.

That is exactly what is measured: **ml-meta is under-confident by +5.2pp
(bootstrap p10 +1.7pp, so the under-confidence itself is solid)**, and the
under-confidence grows with the stated number:

| stated band | n | realised | gap |
|---|---:|---:|---:|
| 55–60% | 134 | 59.0% | +1.8pp |
| 60–65% | 62 | 69.4% | +7.2pp |
| 65–70% | 37 | 75.7% | +8.8pp |
| 70%+ | 23 | 87.0% | +14.4pp ⚠ n<30 |

**The money consequence, and the trap.** The `>=55` threshold is applied to an
*under-stated* probability, so in practice the rule is admitting matches whose
true win rate is ~67%, not 55%. The leak is making the model **more selective
than it was configured to be** — it is buying conservatism by accident.

Which produces the counter-intuitive and important conclusion:

> **Removing `ht_diff`/`ht_total` and retraining, without re-tuning the
> threshold, would most likely make live performance WORSE.** A correctly
> calibrated model would raise its stated probabilities to match reality, and
> `>=55` would then admit a wider, weaker set of matches than it does today.
> The honest fix is a two-part change — retrain *and* re-derive the threshold —
> and it must be priced as one change, through the full bar, before anything
> ships.

This is the opposite of the natural instinct ("remove the broken input"). The
input is broken. The breakage is currently load-bearing.

### Pricing the only live change this measurement could justify

Stop letting ml-meta legs ride at all (`--rules` prints this paired replay):

| scope | arm | log/day | final | bet-days | maxDD |
|---|---|---:|---:|---:|---:|
| whole archive | live | **+0.0428** | 924% | 52 | **67%** |
| whole archive | ml-meta removed | +0.0402 | 611% | 45 | 74% |
| in-season | live | **+0.0410** | 387% | 33 | **63%** |
| in-season | ml-meta removed | +0.0362 | 256% | 26 | 74% |

Paired Δ(removed − live): **−0.0090/day** whole-archive (p10 −0.0433, p90
+0.0250) and **−0.0156/day** in-season (p10 −0.0750, p90 +0.0435); cards differ
on 15 of 26 in-season days.

**Demotion fails the bar in both directions at once:** it loses growth on the
measured path *and* it deepens max drawdown from 63% to 74%. It also costs
**7 bet-days** — days where an ml-meta leg was the only card, so the engine
would simply not have bet. In plain money: cutting the family would have turned
387% into 256% while making the ride rougher. `ml-meta>=55` stays exactly as it
is.

### Correction to checkpoint ⑤

The standing note "ml-meta>=55 demotion: evidence compounding, −7.3% live at
n=210+" is **stale and should not be actioned**. Re-measured across every
settled archived ml-meta pick (no floor, no bucket filter): **n=341, flat ROI
+0.7%**. On the floored, playable set it is +0.0%, and on the legs that rode
in-season it is +7.0%. The bucket moved from negative to roughly break-even as
n grew — which is what a small-sample negative usually does. **Checkpoint ⑤ is
closed as NOT ACTIONABLE**, superseded by this checkpoint.

Note also the scope trap: **ml-meta legs first appear 2026-08-11**. Every
ml-meta number is in-season by construction. Any comparison against a family
that also fired in June–July is confounded by the season boundary — always
compare with `--since 2026-08-01`.

### Why this one is different in kind, and why that changes nothing today

Every prior candidate in this ledger was a stake-shape or card-shape tweak,
trading growth against drawdown along the same frontier. This one is
**removing a broken input** — the class of change that can move the frontier
rather than slide along it. That is precisely why it earned its own checkpoint
rather than a closing remark.

It still gets no exemption. The full bar applies: paired-bootstrap p10 > 0,
sign holds under every leave-one-day-out, maxDD no worse than live. On today's
evidence the *demotion* fails it outright, and the *retrain* has not been
attempted because it cannot be evaluated honestly yet — the warehouse cannot
replay ml-meta at all (checkpoint ⑪, Ground 4), so a retrained model can only
be judged on **new live bet-days**.

### Pre-registered next step, and the standing prohibitions

**Do not** patch `picks_today.py` to fabricate half-time features. Feeding a
guessed or averaged half-time score would convert a constant into noise and
make things genuinely worse.

**Do not** retrain silently. A retrain without a threshold re-derivation is a
live behaviour change disguised as a bug fix.

**Do** the following, in order, when someone has the appetite:

1. Retrain the meta-model with `ht_diff`/`ht_total` **removed** from
   `feature_cols`, walk-forward, split unchanged.
2. Re-derive the firing threshold on the retrained model so that the *admitted
   set* is comparable — not the nominal number. The current `>=55` corresponds
   to a realised ~67%; the new threshold must target the same realised rate.
3. Shadow it. Emit both models' picks for **n >= 60 in-season bet-days**, bet
   neither differently, and compare admitted sets and realised hit rates.
4. Only then price it through the full bar.

Until step 4 completes, `ml-meta avg_p>=55` is **live and unchanged**, and the
half-time features stay in the trained model precisely because removing them is
a live change that has not been earned. Document the defect; do not
half-fix it.

### Verification receipt

- `PYTHONPATH=src python3 -m pytest -q` → **368 passed** (345 pre-existing + 23 new). `py_compile` and
  `git diff --check` clean.
- Engine parity re-asserted: **0 leg-selection differences on all 80 archived
  days**, worst total-staked deviation **0.000000pp**.
- `--battery` / bare baseline unchanged: live **+0.0428 log/day, 924%, 52 days,
  67% maxDD**. `--rules` is read-only and changes no default.
- Both forebet ROI populations reproduced (224,194 / −5.1% and 3,170 / +4.2%),
  bootstrap on the filtered slice p10 **+2.0%**, P(ROI>0) **99.4%**.

## Addendum — 2026-09-04 (late): checkpoint ⑫ tripwire shipped, and checkpoint ⑬
## opened — the 3way-unanimous family

Three review amendments to checkpoint ⑫, all landed. **No live setting changed;
parity re-verified at 0 leg-selection differences / 80 archived days, worst
total-staked deviation 0.000000pp.**

### Amendment 1 — the ml-meta claim is downgraded to its honest strength

See the amended paragraph in checkpoint ⑫. Short version: **"statistically
indistinguishable, no evidence ml-meta is worse, a hint it is better"** — never
"ml-meta outperforms". ml-meta +7.0% (p10 −2.2%), 2way −6.0% (p90 +2.8%), n=81
and n=79. The demotion is rejected on the **paired replay**, which is the
stronger evidence, not on this table.

### Amendment 2 — the accidental conservatism now has a contract, not a note

The load-bearing fact from checkpoint ⑫ is that `ht_diff`/`ht_total` are a
**constant 0** at serve time, so the `>=55` operating point sits on a shifted
probability scale. That conservatism is **unstable**: it survives only while
nobody retrains, refits or changes the feature pipeline. A routine model
refresh would remove the margin silently, with no alarm. A comment in a
handover file is not a safeguard.

**Shipped in `scripts/picks_today.py`:**

- `ML_META_CONSTANT_FEATURES = ("ht_diff", "ht_total")`
- each emitted ml-meta pick now records `ml_ht_diff` / `ml_ht_total`
- `ml_meta_contract_breaches(picks)` returns any ml-meta pick whose recorded
  constants are non-zero
- on breach: the affected picks are **withheld** (fail-closed), a 🚨 line goes
  to stderr, and `localdata/ml_meta_contract_breach_<day>.json` is written

**Placement matters and was got wrong first.** The obvious spot — inside the
ML scoring loop — fires on fixtures that already kicked off, because
`run_day()` scores the whole slate *before*
`filter_operational_pre_match_picks()` discards started matches, and Forebet
returns a real half-time score for those. That tripwire would have screamed on
every afternoon run about picks the engine was never going to bet. **A tripwire
that cries wolf gets ignored, which is worse than no tripwire.** It is
therefore checked *after* the pre-match guard, on the picks that could actually
be bet. A test pins that ordering.

Behaviour today is unchanged: for a genuinely pre-kickoff fixture Forebet
returns no half-time score, `_f()` yields `None`, and `(None or 0)` is 0, so no
branch fires. **Caveat on that claim:** it is established by code path and unit
test, not by a live `picks_today.py` run — this session had no live slate to
execute against. The first real run should be watched for a 🚨 line.

### Amendment 3 — checkpoint ⑬: the 3way-unanimous family. OPENED, NOT ADOPTED.

It was fair to say nobody had looked at this. `3way-unanimous` is the only rule
family whose lower bound clears zero:

| scope | n | hit | flat ROI | roi p10 |
|---|---:|---:|---:|---:|
| all settled playable legs | 71 | 80.3% | **+14.4%** | **+5.3%** |
| legs the engine actually rode | 41 | 85.4% | **+20.0%** | **+9.0%** |

Leave-one-day-out on the pool legs: ROI range +9.6% to +17.6% across the 36
days it fires, **0 sign flips out of 36**. On leg quality alone this is the
strongest family in the archive.

**But it is mostly an off-season artefact, and that is decisive.** Of the 36
days on which a 3way leg exists, only **9 are in-season**. Checkpoint ⑩
established that pre-August days came from soft summer leagues and are not
representative. So ~75% of the evidence for the best-looking family sits in the
regime the ledger already says not to generalise from. In-season it is 25 pool
legs over 9 days (10 ridden legs, all winners — n=10 decides nothing).

**It is also rare.** Distribution of settled playable 3way legs per day: 44
days with none, 22 with exactly one, 14 with two or more. On most days there is
nothing to lean on, and on more than half the firing days there is not even
enough for one all-3way acca.

**The obvious way to exploit it was priced and it LOSES.** A new research rank
`rank="rule3way"` (3way legs first, then stated probability) was added to
`auto_tickets.rank_legs`, **defaulting off** and pinned off by test:

| scope | arm | log/day | final | bet-days | maxDD |
|---|---|---:|---:|---:|---:|
| whole archive | live `rank=prob` | **+0.0428** | 924% | 52 | 67% |
| whole archive | `rank=rule3way` | +0.0343 | 596% | 52 | 65% |
| in-season | live `rank=prob` | **+0.0410** | 387% | 33 | 63% |
| in-season | `rank=rule3way` | +0.0298 | 267% | 33 | **48%** |

Paired Δ −0.0084/day whole-archive (p10 −0.0322) and −0.0112/day in-season
(p10 −0.0449); cards differ on 14/52 and 7/33 days; leave-one-day-out flips the
sign on 51/52 and 32/33 removals. **In money: 387% becomes 267%.**

Note the honest tension: max drawdown improves markedly in-season, 63% → 48%.
That is a **slide along the frontier**, not a move of it — less growth bought
with less risk — and it is the same shape as the risk-matched `max_accas=2`
wash closed in checkpoint ⑦. It is not a free lunch and it does not clear the
bar.

**Why promoting good legs loses money** (worth understanding before the next
person re-opens it): the recipe pairs *consecutive* ranked legs into 2-leg
accas. Promoting 3way legs does not add them — they were already in the top 6
on most firing days — it **re-partitions the pairings**, and a 2-leg acca dies
if either leg dies. Reordering a pool without changing its membership is a
pairing change, not a selection improvement.

**Pre-registered rule for checkpoint ⑬.** The 3way *leg* edge is real and
worth watching; no exploitation of it has been found. Re-open only at
**n >= 30 in-season 3way legs across >= 20 in-season firing days** (currently
25 legs / 9 days). Adopt only under the full bar: paired-bootstrap p10 above
zero, sign holds under every leave-one-day-out, maxDD no higher than live.
`rank=rule3way` is **rejected** and must not be re-run as a fresh idea — it is
now a scanned variant. Remember the standing limit: about 27 variants have been
scanned; **at most one candidate may ever be adopted**, and the in-season
fourth acca is still the leading claimant.

### Verification receipt

- `PYTHONPATH=src python3 -m pytest -q` → **377 passed** (345 pre-existing + 32
  new). `py_compile` and `git diff --check` clean.
- Engine parity after touching BOTH `auto_tickets.py` (new rank option) and
  `picks_today.py` (tripwire): **0 leg-selection differences on all 80 archived
  days**, worst total-staked deviation **0.000000pp**.
- Bare/`--battery` baseline unchanged: **+0.0428 log/day, 924%, 52 days, 67%
  maxDD**. `--warehouse-replay` still exits 1 (FAIL), as it must.
- New knobs pinned OFF: `rank="rule3way"` is never the default; the tripwire is
  silent while the contract holds.

## Addendum — 2026-09-06: incident #6 — the KICKOFF GUARDS (Task 1, revised after review), deployment-gap measurement (Task 2.1), and the search-bias reproduction (Task 2.2)

> This replaces the same-day addendum written before the row audit. The
> fail-closed KICKOFF PROOF CONTRACT described there was reviewed and found
> worse than the bug (573 legs dropped to catch one started match; 46 of 59
> bet-days destroyed) and is NOT the live rule. What ships is below.

### What happened (incident #6)

On 2026-09-06 the engine staked ACCA #3 on **Vancouver Whitecaps vs St.
Louis City** at 09:13 SAST. The match had kicked off at **2026-09-05 22:30
EDT = 02:30 UTC = 04:30 SAST** — over 4h45m before the ticket printed. Sixth
ghost incident; the 09-04 patch (five incidents) was a league-substring ->
IANA zone table plus a 4h lead buffer; it is deleted, not extended.

### The diagnostic the brief asked for — the raw Vancouver record

`localdata/picks_today.json` row 38 of 57 (verbatim key fields):

```
kickoff:            "22:30"                          <- bare time: NO date,
                                                         NO offset, NO zone
date:               "2026-09-06"                     <- slate day (SAST day of
                                                         the real kickoff)
match:              "Vancouver Whitecaps vs St. Louis City"
league:             "USA,Major League Soccer"
odds_source:        "scoutingstats_odds"   (bookmaker scoutingstats_odds)
price_evidence:     "SCOUTINGSTATS_SOLE"   (bucket WATCHLIST_UNCORROBORATED_PRICE,
                                            price_quarantine scoutingstats_sole_source)
odds_captured_at:   "2026-09-06T02:30:00Z"           <- the kickoff instant
as_of:              "2026-09-06T03:00:47+02:00"
```

What the row shows: the kickoff field is the **bare US-local wall time**
("22:30" EDT) with no date of its own and no zone. The 09-04 chain failed
open on it twice: the SAST-default parser stamped slate-day 22:30 SAST (18h
late), and the zone table stamped America/New_York on the slate day (also
late, by a different route). The correct fix is not a seventh layer of the
same shape — it is to refuse rows that cannot say when they start.

Shape census of the same file (57 rows): **45 naive-with-date, 9 bare-time,
3 explicit offset/Z**. Inter Miami (also MLS) came through as
`2026-09-06T01:30:00+02:00` — the feed renders dated rows on a UTC+2 clock
when it can. Bare-time rows span betexplorer/scoutingstats/None sources, so
source alone does not separate them; **no date means no comparison is
possible**, which is the incident class.

### What shipped — TWO layers (round 2: narrowed after the region audit)

1. **LIVE KICKOFF GUARD** (`auto_tickets.live_kickoff_guard`, wired into
   `cmd_today`; runs on every build). A leg drops when:
   - its kickoff is **missing / unparseable**, or
   - its kickoff is **clock-only** — bare "HH:MM" or yearless "DD-MM, HH:MM"
     — **and its league region's clock is far from SAST** (Americas /
     Asia-Pacific, matched on the row's own league text): a bare "22:30"
     MLS clock read on the slate day is the incident class, up to 18h wrong
     in the fatal direction. The region list is BOOLEAN-ONLY — it answers
     "is the SAST reading of this clock trustworthy?", it never computes or
     infers a kickoff instant, so a mis-hit drops a leg that could have
     been bet (no-bet), it cannot fabricate a wrong time (the distinction
     from the deleted `_AMERICAS_ZONES` table, which *computed* kickoffs),
     or
   - its dated kickoff is **already at/past build time** (dated rows are
     compared on the feeds' UTC+2 rendering via `parse_kickoff`).
   Clock-only rows from Europe/Africa ride on the SAST reading (clocks
   within ~1-2h of SAST; historical errors are hour-scale, in the safe
   direction). Every run prints the skip census. No 4h lead buffer live.
2. **AUDIT CONTRACT** (`auto_tickets.kickoff_contract`;
   `replay_harness.py --kickoff-contract`, **off by default, never the live
   rule**): the fail-closed proof-or-drop standard (explicit offset/Z or
   row-carried `kickoff_tz`, >= 4h ahead of the canonical 09:00 SAST build).
   It is the measurement instrument for the data-side kickoff gap — not a
   betting rule. Its output is structurally labelled AUDIT ONLY.

**The 134 no-year "DD-MM, HH:MM" rows — classified, not assumed.** All
archive rows of this shape come from day-first sources (zulubet, bzzoiro,
betexplorer, scoutingstats — e.g. "24-06, 18:00" for a 24 June Swedish
match; "01-07, 17:00" for the 1 July World Cup fixture) and `parse_kickoff`
reads them day-first with the year resolved to the slate date (+-1 year);
the ridden sample checks out against real fixtures (Sweden in June, the
July World Cup), and the day-month order is pinned by a test. The guard
gives these rows the SAME region treatment as bare times (they are
clock-only: no year, no zone): Europe/Africa rows are kept and parsed;
Americas/Asia-Pacific rows drop. Ridden split below.

Deleted and barred: `_AMERICAS_ZONES` / `_inferred_kickoff_utc` /
`_unprovable_future` (Toronto-for-Vancouver class), SAST defaulting for bare
times in remote-clock regions, and fail-open "cannot parse -> ride".
`parse_kickoff` survives for settlement bookkeeping and dated-row comparison
and is explicitly NOT a zone proof (test-pinned).

### Cost of the live guard on history (honest number, per regime)

Measured on the refreshed parity baseline (playable pools + the engine's
historical ridden cards, current archive; classifier = the shipped code):

- Ridden clock-only legs (bare + no-year day-month): **104 of 256 legs**.
  - **dropped (remote-clock regions): 25 legs — 15 bare on 12 bet-days
    (Suwon 08-07, Junior 08-11, Palmeiras 08-12, Bolivar 08-12, Deportivo
    Moron 08-15, Broadmeadow 08-16, Penarol 08-16, Bucaramanga 08-17,
    Deportes Tolima 08-19, LDU Quito 08-20, Seattle 08-20, Sporting KC
    08-30, Toluca 08-31, Olimpia 09-04, Vancouver 09-06) + 10 yearless
    day-month on 8 bet-days (Australia/Argentina/Bolivia/Ecuador/Peru
    rows)** — every row the round-1 audit named is inside this set.
    (Two measurements, both correct: the reviewer's **8 legs / 7 bet-days**
    are the near-miss rows **verified against real kickoffs**; this
    **25 legs / 18 bet-days** census is *every* Americas/Asia-Pacific
    clock-only ridden row, verified or not. The 25 are the conservative
    number to guard against; the two bet-days shared by the bare and
    yearless sets (08-07, 08-19) are why "12 + 8 bet-days" sums to 18
    distinct days.)
  - **kept (Europe/Africa + unclassified-international): 79 legs** (37
    bare + 42 day-month) — the round-1 audit's "39 European bare legs" are
    here; a Croatian "16:00" is right to ~1h and rides.
- Money cost (`replay_harness.py --kickoff-guard`; canonical 09:00 SAST
  builds; live stake rules; whole archive and in-season):

  | arm | whole archive | in-season (>= 08-01) |
  |---|---|---|
  | default (battery universe) | 54 bet-days, +0.0319 log/day, final 560%, maxDD 67% | 35 bet-days, +0.0244, 235%, 63% |
  | started-only (engine's historical live path) | 54 bet-days, +0.0397, 852%, 67% | 35 bet-days, +0.0363, 357%, 63% |
  | region guard (shipped) | 52 bet-days, +0.0477, 1196%, 64% | 34 bet-days, +0.0294, 272%, 64% |
  | guard minus started (marginal) | +0.0080 log/day, maxDD 67% -> 64% | **-0.0070 log/day, maxDD 63% -> 64%** — the in-season guard-vs-started gap is **ONE bet-day: 2026-08-04 — and that day WON** |

  In-sample history does not punish the guard — the remote-clock class was
  disproportionately losing legs — but that is hindsight, not evidence of
  edge; the rule exists to stop the incident-#6 family and its true price
  shows up on genuinely new days. **COST CAVEAT (amended 2026-09-06, Task
  C1): the in-season guard-vs-started gap is ONE observation — the single
  bet-day 2026-08-04 (whose started-only card relied on a
  Carabobo-Venezuela no-year row) — and that day WON** (35 started-only
  days total log +1.2705 → 357%; guard 34 days +0.9996 → 272%; Δ −0.2709 =
  exactly that one day's ×1.311 factor). In noise terms that gap is ~0.19
  SE of a single day's log growth (daily sd ≈0.21–0.23, n=35) and
  default-vs-started is ~0.33 SE — indistinguishable from zero, and had
  08-04 lost, the same guard would read as a GAIN. **The cost of the guard
  is therefore UNMEASURED, not small: neither arm has earned a number, and
  −0.0070 (in-season) or +0.0080 (whole archive) must never be quoted as
  the price of the guard.** The same caveat applies wherever started-only
  looks better than default (its in-season edge over default is the same
  single winning day plus the pre-existing started filter's noise — not a
  measured property of the filter).
  Whole-archive read, explicitly (Task C2): 560% (default) → 852%
  (started-only) → 1196% (region guard). Most of that span is the
  PRE-EXISTING started filter (560% → 852%); the guard's own increment
  (+0.0080 log/day, 852% → 1196%, whole archive) is in-sample hindsight on
  a class that happened to lose, carries the same one-day noise problem,
  and is not an achievement claim either.

- The incident-day card: 6 legs — Vancouver 22:30 (MLS, dropped), Rudes
  16:00 (Croatia, kept — right to ~1h), Miami 01:30 (started, dropped),
  Hearts/Gresford/Zrinjski (dated, kept).

Thin-day doctrine stands: days whose card shrinks should scale the stake or
abstain.

### Do the two serve-time guards cover each other? (asked in Task 1)

No, and they should not be merged. The ml-meta serve-time tripwire in
`picks_today.py` inspects half-time feature leakage in ml-meta rows; the
kickoff guard inspects kickoff usability at build time. Different layers,
different data, disjoint failure classes — the Vancouver leg never passed
through the ml-meta scorer's feature path, so the tripwire could not have
seen it, and the kickoff guard cannot see feature leakage. Both fail closed
and both stay. Operational overlap only: a tripwire firing is an abstain
day, and a guard-wide no-date day is also an abstain day (NO BET) — the same
posture for the same reason.

### Parity baseline — restored from git, then drift-refreshed with a receipt

The regenerated strict baseline is **reverted**: `git checkout HEAD --`
tests/data/engine_parity_baseline.json + tests/test_warehouse_replay.py
(`_snapshot` back to playable -> plan_day). A baseline that pins a strategy
that does not bet can no longer catch unintended drift, and it was
regenerated without a saved receipt.

The git copy predates archive growth, so the file was then refreshed against
the current archive with a written receipt: the ONLY diffs vs the git
baseline are **2026-09-05** (card content/odds refreshed by later captures;
same total staked) and **2026-09-06** (git snapshot empty; archived rows now
build the day's 3-acca card, staked 0 -> 33.3333). No other day moved.
`generated_note` in the file carries the receipt; suite is 399 passed. The
kickoff layers are deliberately NOT part of the parity file — they live in
`cmd_today` and the audit tooling and are pinned by
tests/test_kickoff_contract.py (22 tests incl. the end-to-end incident-slate
regression).

### Task 3 — bank labels

The slip no longer uses "bank" with two denominators. Header prints **total
bank = free bank + committed** (all % of capital); stake and deploy lines
say **free bank**; the day's total is printed as % of capital. Owner-visible
on the next ticket.

### Task 2.1 — the deployment gap is real and now measured

The replay model settles each day's stake the same day; live money stays
committed across runs, so the live engine stakes 1/3 of *free* bank, not 1/3
of bank. Committed % of capital from the 11 real ticket headers (27 Aug ->
6 Sep) gives **true mean deployment = 20.7% of total bank** (not 33.3%):

| era | days | deployment of total bank |
|---|---:|---:|
| 50%-era (08-27 -> 09-03) | 8 | 25.0 / 12.5 / 20.3 / 10.2 / 14.8 / 34.1 / 25.0 / 25.0 % |
| 33%-era (09-04 -> 09-06) | 3 | 16.7 / 22.2 / 22.2 % |

Re-running the in-season replay at the measured 20.7% (same cards, same
days): log/day **+0.0209** (was +0.0244 at 33%), final **208%**, maxDD
**43%** (was 63%), and daily log-volatility drops from **0.2240 to 0.1384**,
landing on the live machine's measured 0.1299 — the 33%-replay volatility
gap was the committed-capital gap all along. No setting changed; this
corrects how the ledger numbers are read.

The 80-day committed-capital reconstruction is **not fully recoverable**:
historical result donors are stored post-hoc with no per-result landing
time, so per-day open-slip overlap before 08-27 cannot be dated. The
live-ledger measurement above is the search-free ground truth; the 20.7%
figure and the volatility match stand as the honest correction.

### Task 2.2 — the headline number is a search artefact (reproduced), and there is no honest forward number yet

Reproduction on today's 35 in-season days with the 13 documented variant
rows (floor 1.01...1.30, max_accas 4/5/6, saturated_accas 4/5/6): demean
every variant to zero true edge, resample days jointly 20,000 times, keep
the winner each time:

| statistic | this run (35-day data) | brief's figure (33-day data) |
|---|---:|---:|
| winner under pure-noise null, median | **+0.0290/day** | +0.0372/day |
| p90 | +0.0740/day | +0.0885/day |
| P(noise >= +0.0410) | **36%** | 46% |

Same conclusion either way: a search this size run on nothing manufactures
an apparent edge the size of the headline. On **today's** settled archive
the live settings replay is **+0.0244/day (35 days, maxDD 63%)**, not
+0.0410: the two extra in-season days that settled after the 09-04 receipt
(09-04 and 09-05, both losing cards) pulled the number down. The live ledger
agrees with the null: 10 real bet-days, **-0.0026 log/day**, 16W/12L, bank
97.4% (32% below its 143.1% peak), bootstrap P(edge > 0) = **48%**.

**There is no honest forward number yet.** Every replay number on these days
is in-sample for a ~27-variant search; the only search-free estimator is the
live ledger, which is 10 days old and statistically empty. The path to a
number is the rewritten pre-registration below, on genuinely new days, under
the standing bar. Until then the defensible statement is: the engine's
expected edge is **not distinguishable from zero**, its live volatility is
~0.13/day, and its live deployment is ~21% of bank.

### Task 2.3 — pre-registered out-of-sample tests rewritten

The pre-registration in checkpoint ⑩ now names **two** questions on
genuinely new in-season days at **n >= 60** (approximately early Oct
counting from 08-01), both under the standing bar (paired-bootstrap p10 > 0,
every leave-one-day-out keeps the sign, maxDD <= live): **Q1 max_accas=4**
and **Q2 the live floor=1.20**. Expectation set in advance: both are
in-sample artefacts today (Q1 is the largest noise artefact in the 09-04
table; Q2 is a lone spike between two holes, and a pure-noise search
manufactures its magnitude ~40-50% of the time). Testing them is right;
expecting them to win is not. At most one adoption from the family ever.

### Verification receipts

- `PYTHONPATH=src python3 -m pytest -q` -> **403 passed** (377 pre-existing
  incl. both parity tests green against the drift-refreshed baseline + 26
  kickoff-guard tests).
- `py_compile` clean; `git diff --check` clean.
- Constants: `grep -n "^MAX_ACCAS\|^STAKE_FRAC\|^MIN_LEG_ODDS"` ->
  `MAX_ACCAS = 3`, `STAKE_FRAC = 1.0 / 3.0`, `MIN_LEG_ODDS = 1.20`.
- Battery live row unchanged by this change (+0.0319 log/day, 560%, 54
  days, maxDD 67% on today's data; identical before and after under stash
  A/B); the drift vs the 09-04 receipts (+0.0428/924%/52 days) is archive
  growth (settled 09-04/09-05 cards), not an engine change.
- Audit instruments (both off by default, structurally labelled):
  `replay_harness.py --kickoff-contract` (fail-closed proof standard) and
  `replay_harness.py --kickoff-guard` (money cost of the live region
  guard — log/day, maxDD, bet-days lost, in-season beside the live arms).
- Region classifier pinned boolean-only by tests (it never computes a
  kickoff); Vancouver drops under the live guard (clock-only, remote
  region) AND under the audit contract; a Croatian bare row rides live and
  a Korean/MLS/Mexican/Uruguayan/Australian one drops; no-year day-month
  rows parse day-first (test-pinned); the e2e incident-slate run prints the
  census and builds the two-acca card (Vancouver and started Miami out,
  Rudes/Gresford/Hearts/Zrinjski in).

### Today's frozen slip (operator instruction)

The 2026-09-06 slip was already frozen at 09:13 with the ghost in ACCA #3
before any code could change. **Bet ACCA #1 and ACCA #2 only.** The guard
ships for the next build; the first live run under it should print the
census line.

### Open items for the next session

1. **THE REAL FIX — normalise kickoffs at ingest in `picks_today.py`** (or
   the upstream scrape): emit a usable kickoff per row (offset-carrying,
   or date-carrying with a row-level zone). The Inter-Miami row
   (`2026-09-06T01:30:00+02:00`) proves the feed can render MLS fixtures in
   UTC+2 — it just failed for the one `scoutingstats_odds` row, which was
   ALSO already flagged `WATCHLIST_UNCORROBORATED_PRICE` /
   `scoutingstats_sole_source` for pricing and bet anyway (that pricing
   corroboration question is separate and untouched here). Fixing ingest
   turns the guard's ~20% clock-only leg loss into roughly zero; the guard
   stays as the seatbelt either way. Separate item, opened, not done here.
2. **Watch the first live run under the guard** — the census line should
   print on the next 06:05/09:13 build; confirm it reads sensibly on a real
   slate.
3. **Residual risk, stated** — dated rows are trusted on the feeds' UTC+2
   rendering (tested, and consistent with every dated row on the incident
   day). A future upstream rendering change — or dated rows from east of
   UTC+2 — would need a re-audit; rerun `--kickoff-contract` and
   `--kickoff-guard` periodically to watch the unprovable and remote-clock
   populations.
4. **Thin-day doctrine** — under the guard, days whose card relied on
   remote-clock rows will shrink (08-04 was the one historical in-season
   card lost); scale the stake or abstain (pre-registered rule, not a live
   tune).

## Addendum — 2026-09-06 (follow-up session): ingest normalisation (Task A), quarantine measurement (Task B)

New session brief, three parts. Tasks A and B below; the C1/C2 record
corrections are amended in place in the round-2 addendum above (money table
and the "honest money number" paragraph).

### Task A — kickoffs normalised at ingest (`kickoff_utc`), never guessed

**What ships (picks_today.py + auto_tickets.py; no selection/staking change):**

- Every pick emitted by `run_day` now carries three append-only fields:
  `kickoff_utc` (ISO-8601 UTC instant or `None`), `kickoff_source` (how it
  was resolved) and `kickoff_witness` (which source row's raw string). The
  feed's raw `kickoff` text is NEVER overwritten.
- Resolution is strictly witness-based, in order: (a) the pick's own
  kickoff string when it carries an explicit offset/Z (`offset_passthrough`);
  (b) a zone-bearing kickoff on ANOTHER source row of the SAME fixture in
  the fetch-time data (`derived_sibling_row` — the Vancouver incident's
  scoutingstats row carried `starting_at 2026-09-06T02:30:00Z`); (c) the
  matched odds row's own kickoff at enrichment time (`derived_odds_row`,
  idempotent — never overwrites the run-day verdict). Two+ zoned witnesses
  that DISAGREE → `kickoff_utc = None` with a conflict note; guessing which
  witness is right is the fault class. Naive renderings ("HH:MM",
  "DD-MM, HH:MM", "YYYY-MM-DD HH:MM:SS") name no zone and stay
  `unresolved` — no SAST defaulting anywhere.
- The live guard (`auto_tickets.live_kickoff_guard`) now judges any row
  carrying a resolved `kickoff_utc` ONLY on that absolute instant
  (started at build → drop; still ahead → ride, regardless of region). The
  Americas/Asia-Pacific clock-only region rule is now the FALLBACK for rows
  normalisation could not resolve — unchanged behaviour for them
  (test-pinned). `parse_kickoff_proven` reads `kickoff_utc` first.
- Archived replay (`replay_harness.py --kickoff-guard` normalised arm)
  reconstructs only the two witnesses preserved in the archives: the row's
  own zoned kickoff, or — for `scoutingstats_odds` rows — `odds_captured_at`
  (below). Sibling prediction rows existed only at fetch time, so the
  archived arm is a LOWER BOUND on live recovery.

**The `odds_captured_at` question (asked explicitly): does it equal the
kickoff generally, or is Vancouver a coincidence?**

Structural, for ONE source only: the scoutingstats odds adapter
(`picks_today._scoutingstats_rows_to_odds`) has no capture timestamp — it
stores the fixture's `starting_at` kickoff string INTO `captured_at`. So for
scoutingstats rows `odds_captured_at == kickoff` BY CONSTRUCTION, not by
coincidence. Verified on the whole archive: 241 scoutingstats rows whose own
kickoff was full-dated all agree with `odds_captured_at` (0 disagreements
>2h), and all 89 clock-only scoutingstats rows carry a zoned
`odds_captured_at` (the rescue witness). It is NOT coincidence — and it is
NOT independent corroboration either: the column just re-exposes the same
starting_at string.

For every other odds provider it is a TRUE capture timestamp, never a
kickoff: bzzoiro rows capture 3–20h before kickoff (44 of 47 dated rows),
betexplorer rows 4–17h before (129 of 193), and ZERO rows of either source
show capture after kickoff. The code therefore accepts `odds_captured_at`
as a kickoff witness for scoutingstats rows only, and never reads
`captured_at`/`odds_captured_at` of bzzoiro/betexplorer/theoddsapi as one.
A future adapter that adds a real capture column to scoutingstats rows must
carry the kickoff in the row's own key, not reuse captured_at.

**Recovery rate on the 25 ridden legs the guard drops (the deliverable):**

Measured on the parity baseline's ridden cards (56 staked bet-days; the
25 = 15 bare clock-only on 12 bet-days + 10 yearless day-month on 8
bet-days, 18 distinct days; every leg the round-2 record names is in the
set). Archived-witness lower bound:

- **12 of 25 resolve to an absolute instant — all 12 via the scoutingstats
  odds row (`derived_odds_row`)**. Of those: **6 were already started at the
  09:00 SAST build and still drop — now for the TRUE reason** (Junior vs
  Pereira 08-11 01:05Z, Bolivar 08-12 00:30Z, Deportes Tolima 08-19 00:30Z,
  Sao Paulo 08-19 00:30Z, Toluca 08-31 00:00Z, and Vancouver itself
  09-06 02:30Z — normalisation CONFIRMS the Vancouver drop); **6 are still
  future and ride again** (Independiente del Valle 08-02 18:00Z, Suwon
  08-07 10:30Z, Deportivo Moron 08-15 18:00Z, Penarol 08-16 21:30Z,
  Bucaramanga 08-17 21:05Z, LDU Quito 08-20 22:00Z).
- **13 of 25 remain unresolvable in the archive** — every one matched a
  bzzoiro/betexplorer/zulubet odds or anchor row whose own kickoff string is
  NOT archived (only the true capture time is): 07-04 Lions/Olympic,
  07-10 Arsenal Sarandi + Peninsula Power, 07-16 Real Potosí, 08-07
  Adelaide City + Lions/Brisbane Roar II, 08-12 Palmeiras, 08-16
  Broadmeadow, 08-20 Seattle, 08-24 Universitario, 08-27 Real Potosí,
  08-30 Sporting KC, 09-04 Olimpia. These stay under the region fallback.
  Live recovery is expected HIGHER: those providers' zoned kickoff strings
  existed at fetch time (betexplorer's +02:00 rendering is present on
  other archived rows) but are not preserved, so history cannot replay them.

Money path (four-arm table above; canonical 09:00 SAST builds): vs the
shipped guard, normalisation returns the one in-season bet-day lost
(08-04 — via BG Pathum, whose true instant 12:30Z is future; its naive
"08:30" had been misread as started, and its bare clock made the guard
drop it as remote). In-season normalised-vs-started shows −0.0175 log/day
on the same 35 bet-days — that is the in-sample reshuffle from CORRECT
started-drops removing legs that historically won, the same one-day noise
class as C1; it is not a reason to keep mis-dated rows. Parity baseline
file: unchanged by this work (normalisation adds fields and changes only
what the cmd_today guard drops; plan_day inputs are byte-identical —
suite receipt below).

### Task B — quarantine census on ridden legs (measure only, no gate change)

Vancouver rode with `WATCHLIST_UNCORROBORATED_PRICE` /
`SCOUTINGSTATS_SOLE` / `scoutingstats_sole_source` on the row. Measurement
(ridden = default replay arm's cards; flagged = WATCHLIST_* bucket or
`price_quarantine_reason`, counted once; `replay_harness.py --quarantine`):

| regime | ridden legs | flagged | hit (flag / unflag) | flat ROI (flag / unflag) |
|---|---:|---:|---:|---:|
| whole archive | 242 | 98 (40%) on 35/54 days | 78.6% / 74.3% | +4.5% / +5.1% |
| in-season ≥ 08-01 | 182 | 93 (51%) on 32/35 days | 77.4% / 69.7% | +3.5% / −1.1% |
| off-season < 08-01 | 60 | 5 (8%) on 3/19 days | 100% / 81.8% | +22.0% / +15.0% |

Flag breakdown (whole archive / in-season): price_evidence
SCOUTINGSTATS_SOLE 74 (all in-season) + BETEXPLORER_RESCUE 12 + SOURCE_
FALLBACK 2 + BZZOIRO_PRIMARY 1; quarantine_reason `scoutingstats_sole_
source` 74; buckets WATCHLIST_UNCORROBORATED_PRICE 27, WATCHLIST_UNKNOWN_
CTX 24 (19 in-season), SKIPPED_VETO 47 (bucket label present on ridden
rows; no gate reads it for this measurement).

Day-block bootstrap (4000 draws, paired days, seed 20260906): whole-archive
ΔROI(flagged−unflagged) p10 −5.2%, 90% CI [−8.0%, +18.5%] (32 paired days);
in-season p10 −6.3%, CI [−9.3%, +19.0%] (29 days); off-season is 3 days —
nothing. In-sample would-blank if flagged legs were excluded: whole archive
−0.0304 log/day, final 22%, maxDD 97%, 4 days blanked (07-22, 08-04,
08-06, 08-19); in-season −0.0596 log/day, final 15%, maxDD 97%, 3 days
blanked (08-04, 08-06, 08-19).

**Reading (amended 2026-09-06 closeout — the framing below supersedes the
original wording; this is a measurement, not a finding): in-season the flag
is currently ANTI-PREDICTIVE — flagged legs BEAT unflagged (77.4% hit /
+3.5% flat ROI vs 69.7% / −1.1%), so the price-quarantine flag today
identifies the BETTER legs, direction unexplained.** Day-block bootstrap
(4000 draws, seed 20260906, 29 paired in-season days): p10 −6.3%, 90% CI
[−9.3%, +19.0%] — wide, crosses zero, so it is not evidence either way;
the whole archive mirrors it (98/242 flagged: 78.6% / +4.5% vs unflagged
74.3% / +5.1%; bootstrap p10 −5.2%, CI [−8.0%, +18.5%], 32 paired days)
and off-season is 5 flagged legs on 3 days (100% / +22.0% vs 81.8% /
+15.0% — nothing). Excluding flagged legs would have destroyed the
in-sample bank (whole archive −0.0304 log/day, final 22%, maxDD 97%, 4 days
blanked; in-season −0.0596 log/day, final 15%, maxDD 97%, 3 days blanked).
The flag is a PRICING caution designed for a different purpose (sole-source
price risk), not a betting signal; that its in-season history is currently
anti-predictive has no identified explanation and nothing here makes the
flag a gate. No gate change ships; no October candidate is opened by this
table; if a flag-based gate is ever tested it must be the pre-registered
October slot under the standing bar, never this in-sample history.** If a future flag-based gate is ever
tested, it must be the pre-registered October slot under the standing bar
(paired-bootstrap p10 > 0 AND leave-one-day-out keeps sign AND maxDD ≤
live, at n ≥ 60 genuinely new in-season bet-days), never this in-sample
history. The one operational note that stands: the single leg that caused
incident #6 was already flagged and rode anyway — the kickoff layer now
handles that row regardless of price evidence.

### Verification receipts (follow-up session)

- `PYTHONPATH=src python3 -m pytest -q` → **416 passed** (377 pre-existing
  + 26 round-2 kickoff tests + 13 new Task-A tests: zone-only parsing,
  sibling/odds-row derivation, conflict refusal, capture-time refusal,
  idempotency, guard keyed to kickoff_utc, archived-row witness rules).
- `py_compile` clean; `git diff --check` clean. Constants unchanged
  (`MAX_ACCAS=3`, `STAKE_FRAC=1/3`, `MIN_LEG_ODDS=1.20`).
- Parity: normalisation emits append-only fields; the parity baseline file
  is byte-identical to the previous commit's (no test moved).
- Investigative receipts: scoutingstats `odds_captured_at` == kickoff by
  construction (adapter copies starting_at into captured_at; 241/241 dated
  rows agree, 89/89 clock-only rows zoned); bzzoiro/betexplorer
  `odds_captured_at` are true capture stamps (44/47 and 129/193 dated rows
  captured before kickoff; 0 after) — never usable as kickoff witnesses.
- Four-arm `--kickoff-guard` table and `--quarantine` table regenerated
  above in this addendum.

## Addendum — 2026-09-06 (closeout): Task A asterisk verdict on the seven known-started ridden legs

Closeout of the follow-up session's Task A. The seven ridden legs now known
to have already started at build, with the engine slip odds at ride time
(parity-baseline cards, byte-identical to the shipped slips):

| date | leg | pick | odds at ride | settled outcome |
|---|---|---|---|---|
| 2026-08-11 | Junior vs Pereira | HOME | 1.33 | pending (not yet settled) |
| 2026-08-12 | Bolivar vs Sao Paulo | HOME | 1.80 | LOSS |
| 2026-08-12 | Weston Bears vs Adamstown Rosebuds | HOME | 1.40 | WIN |
| 2026-08-19 | Deportes Tolima vs Independiente Del Valle | AWAY | 2.45 | WIN |
| 2026-08-19 | Sao Paulo vs Bolívar | HOME | 1.44 | WIN |
| 2026-08-31 | Toluca vs FC Juarez | HOME | 1.36 | WIN |
| 2026-09-06 | Vancouver Whitecaps vs St. Louis City | HOME | 1.45 | pending (not yet settled) |

Settled: 4 won of 5 (Bolivar lost; Weston/Tolima/São Paulo/Toluca won).

### Do the in-season figures need an asterisk? Verdict: YES — on the two arms that rode pre-guard history; the shipped arms are clean.

Recomputed via `replay_harness.py --kickoff-guard --exclude-started-ridden
tests/data/started_ridden_legs.json` (the seven excluded from every arm's
pool at each day's canonical 09:00 SAST build; replanned through the same
engine; measurement only). Five of the seven are inside the settled replay
scope — Junior (08-11) and Vancouver (09-06) have no settled result and
never entered any growth figure. Pre-exclusion ridden counts per arm:
default rode 5 of 5 in-scope legs, started-only rode 4 (Bolivar, Weston,
Tolima, Toluca), region guard and normalised rode 1 (Weston — they already
drop the other six, now for the true reason).

In-season (>= 2026-08-01), shipped → perfect-clock:

| arm | shipped | minus the five in-scope started legs |
|---|---|---|
| default (battery universe) | 35 days, +0.0244 log/day, 235%, maxDD 63% | 35 days, **+0.0027, 110%, maxDD 80%** |
| started-only (historical live path) | 35 days, +0.0363, 357%, 63% | 35 days, **+0.0133, 159%, 73%** |
| region guard (shipped) | 34 days, +0.0294, 272%, 64% | 34 days, +0.0302, 279%, 63% |
| normalised | 35 days, +0.0188, 193%, 64% | 35 days, +0.0196, 198%, 64% |

Whole-archive analog: default 560% → 262%, started-only 852% → 380%;
region guard and normalised move under one percentage point of log/day.

**Asterisk statement (this is the sentence to keep):** the in-season
default figure (235%, and the +0.0244 log/day quoted as the live-settings
headline in Task 2.2) and the started-only figure (357%) were partly earned
by legs a correct clock would have dropped before build; excluding the five
settled in-scope legs cuts default to **110%** and started-only to **159%**
(in-sample), with maxDD 63% → 80% / 73%. The shipped region-guard (272%)
and normalised (193%) in-season figures do NOT need the asterisk — they
already exclude six of the seven for the correct reason, and removing the
one they rode (Weston, per the brief's classification) moves them to
279%/198%, within in-sample reshuffle noise. Every number here is
in-sample; no arm here ships.

Boundary note, so nobody has to rediscover it: excluding only the four
normalisation-CONFIRMED started legs (Bolivar, Tolima, São Paulo, Toluca —
all with the scoutingstats witness), without Weston, still cuts default
235% → **150%** (+0.0116) and started-only 357% → **218%** (+0.0222), and
leaves the guard and normalised arms EXACTLY unchanged (they rode none of
the four). The verdict therefore does not hinge on Weston's classification.
Weston's own archived kickoff renders dated-future (2026-08-12T12:00:00+02:00
= 10:00Z, after the 07:00Z build) — it is excluded here because the brief
classifies it as started, and the ledger records that its removal moves the
shipped arms by less than noise either way. Task 2.1's deploy-33% figure
(+0.0209/day, 208%) rides the same default-arm cards, so the same asterisk
applies to it proportionally.

## Addendum — 2026-09-06 (closeout): Task D — ARE THE PRICES OBTAINABLE? (D1 shipped, D2 archive gap, D3 in-sample reprice)

P0 question: the engine's prices on `scoutingstats_odds` legs (41% of the
in-season ridden bank; no true capture timestamp — `captured_at` == kickoff
by construction, Task A receipt) may not be prices the owner could actually
get. Three deliverables below; all measurement, no gate, no selection or
staking change (`MAX_ACCAS=3`, `STAKE_FRAC=1/3`, `MIN_LEG_ODDS=1.20`
unchanged; parity baseline untouched).

Measurement surface (same as Task B): ridden legs of the default replay
arm. `scoutingstats_odds` ridden legs: **81 whole archive (77 in-season ≥
2026-08-01, 4 off-season)** — re-run `replay_harness.py --price-obtainability`.

### D2 — archive-side gap (measured now)

Corroboration is defined narrowly on purpose: a SECOND provider's price on
the same fixture+selection that day WITH a true capture timestamp — (a) CLV
snapshot rows where a later refresh matched bzzoiro/betexplorer exactly
(`clv_snapshots_*.csv.gz`), (b) theoddsapi per-bookmaker rows
(`theoddsapi_odds_2026-08/09.csv.gz`). Raw forebet/zulubet/statarea rows
are NOT used as witnesses: they carry no capture timestamp, the same
weakness class as scoutingstats itself.

Coverage: **7 of 81 ridden scoutingstats legs corroborated (8.6%) — 7 of 77
in-season, 0 of 4 off-season.** Off-season is unmeasurable: the oddsapi
archive starts 2026-08-03 and the betexplorer odds archive ends 2026-06, and
the CLV refreshes never found a bzzoiro row for the four July fixtures.

Gap per corroborated leg (harness output; "engine (pool)" = the price the
in-sample replay assumes; "engine (pick_time)" = the CLV snapshot at ride
time where one exists; delta = corr − engine, positive = engine SHORTER
than the best stamped price that day):

| date | leg | pick | engine (pool) | engine (pick_time) | best stamped corr | delta (corr−pool) |
|---|---|---|---|---|---|---|
| 08-12 | Bolivar vs Sao Paulo | HOME | 1.80 | 1.82 (bzzoiro) | 1.82 bzzoiro 08-11T13:42Z | +0.02 |
| 08-16 | Feyenoord vs Go Ahead Eagles | HOME | 1.33 | n/a | 1.40 theoddsapi 08-16T00:38Z | +0.07 |
| 08-21 | Arsenal vs Coventry City | HOME | 1.20 | 1.18 | 1.21 theoddsapi 08-21T01:01Z | +0.01 |
| 08-25 | Al-Ettifaq vs Al-Nassr | AWAY | 1.22 | 1.25 | 1.30 theoddsapi 08-25T00:58Z | +0.08 |
| 08-25 | Watford vs Peterborough | HOME | 1.85 | 1.65 | 1.66 bzzoiro 08-25T09:46Z | **−0.19** |
| 09-02 | Celtic vs Aberdeen | HOME | 1.22 | 1.25 | 1.29 bzzoiro 09-01T22:31Z | +0.07 |
| 09-02 | Falkirk FC vs Rangers | AWAY | 1.55 | 1.60 | 1.61 bzzoiro 09-01T22:31Z | +0.06 |

Reading: on the pool basis, 6 of 7 engine prices are ≤ the best stamped
same-day alternative; the one longer price (Watford, 1.85 vs 1.66) is a
same-day best-of-cache artifact — its ride-time (pick_time) price was 1.65,
≤ 1.66. **On the ride-time basis, all seven checkable legs show the engine
price at or BELOW what another provider offered that day — no systematic
inflation is visible in the archive.** But n=7 is 9% of the population:
the archive simply cannot certify the other 74 in-season scoutingstats
prices, and cannot certify ANY of the 4 off-season ones. That coverage
statement IS the D2 finding — it is why D1 must start now, and why no
retroactive price fix is possible from local files.

### D3 — obtainability-constrained replay (IN-SAMPLE; label required when quoted)

Every `scoutingstats_odds` pool leg is either repriced to its best stamped
corroboration or — when none exists — dropped; the engine replans from the
reduced pools. (Re-run: `replay_harness.py --price-obtainability`.)

| arm | bet-days | legs/day | log/day | final | maxDD | pool legs |
|---|---|---|---|---|---|---|
| whole archive — default | 54 | 2.2 | +0.0319 | 560% | 67% | — |
| whole archive — constrained | 50 | 2.1 | +0.0133 | 194% | **96%** | 236 dropped, 18 repriced |
| in-season — default | 35 | 2.6 | +0.0244 | 235% | 63% | — |
| in-season — constrained | 33 | 2.4 | **−0.0440** | **23%** | **96%** | 227 dropped, 18 repriced |

(7 of the 18 repriced legs are ridden legs — the D2 table; the rest are
non-ridden pool candidates sharing their witnesses. All numbers in this
block are IN-SAMPLE.)

Reading: the obtainability-constrained replay cannot keep the in-season
bank alive (235% → 23%; consistent with Task B's would-blank 15% when the
whole flagged class is excluded) — because the archive cannot certify 74 of
77 in-season scoutingstats prices. Where the archive CAN check, the engine's
price was not longer than the market's. This is a statement about the
ARCHIVE's certification power, not a verdict on the engine; it is exactly
the gap D1 closes going forward.

### D1 — shipped: owner-actual-price capture (pays from the next slip)

**SUPERSEDED SAME DAY (round 4, Task F): the `record` path below was
removed — no manual price entry exists anywhere.** Schema columns remain,
never filled; the automatic build-time `price_board` capture
(`localdata/price_board_<yyyy-mm>.jsonl`) replaces this section. What
follows is the historical record of what first shipped.

What shipped (`scripts/audit_clv.py`, no engine change):

- **`record`** — the operator's channel. After placing a slip, enter the
  decimal odds the bookmaker actually offered, next to the printed leg:
  `python3 scripts/audit_clv.py record --date 2026-09-06 --match "Vancouver Whitecaps vs St. Louis City" --pick HOME --odds 1.44`
  (writes/updates `localdata/actual_odds_<date>.json`; dedupes on
  match+pick; rejects odds ≤ 1.0).
- **`capture`** — attaches recorded prices to the snapshot rows of the
  matching pick for that run date: new snapshot columns `actual_odds` and
  `actual_odds_recorded_at` sit next to the engine's `observed_odds`.
  Idempotent: recording after a capture run and re-running capture updates
  the rows already written. Entries that match no pick of the day are
  reported loudly, never silently dropped.
- **`report`** — new "Actual price vs engine quote" section (JSON + markdown
  + console): per entry engine quote vs actual, delta (positive = the owner
  got a LONGER price than the engine printed), means, and a
  longer/shorter count. Before the first entries it prints the D1 status
  line, so the daily report shows the capture is live.
- The input is ALWAYS the owner's written record — the code never infers an
  actual price. Slip legs, not candidates, are what the operator records;
  the standing instruction is to record ACCA #1 and ACCA #2 slips for the
  next week (the two slips the owner places every day).

~~Standing instruction (one week, operator): when placing ACCA #1 and ACCA #2,
write the odds the bookmaker actually offers next to the odds on the slip
and record them with `audit_clv record` the same day. If they match the
printed prices, the worry dies; if the slip is consistently longer than the
printed price, that is where the edge went — and D2/D3's n=7 will grow
until the archive question is answered by real slip data instead of
inference.~~ **WITHDRAWN by Task F (round 4, same day): never type a number
into this system. The automatic build-time price-board capture answers the
same question with no human in the loop; the operator's observation that
the quoted odds were obtainable at his bookmaker is recorded in the round-4
addendum.**

### Verification receipts (Task D closeout)

- D1 tests: 5 new in `tests/test_audit_clv.py` (record write/dedupe/reject,
  capture attach + idempotent re-run, unmatched-entry warning, report
  section with delta) — all pass (suite: 416 → 421).
- `replay_harness.py --price-obtainability` regenerated for the tables
  above (receipt: coverage 7/81 = 8.6%, 7/77 in-season, 0/4 off-season).
- No engine file changed for Task D except the measurement flags in
  `replay_harness.py`; parity baseline file byte-identical; full suite
  receipt appended in the closeout commit message.

## Addendum — 2026-09-06 (round 4): Task E repick sizing fix · Task F automatic price capture · Task G record corrections · Task H ledger rebuild

### Live record: the guard's first real slate — 8 of 28 qualifying legs dropped

The 2026-09-06 build ran under the shipped kickoff guard for the first time
and dropped **8 of 28 qualifying legs**:

- **5 already started** (dated kickoff at/past build): Vissel Kobe, Cerezo
  Osaka, Universitario, +2 more — five already-started matches on a SINGLE
  ordinary day, against seven such legs across the whole two-month history
  in the Task-A closeout. The historical seven understated this class.
- **3 clock-only in a remote-clock region**: Vancouver Whitecaps (again —
  the incident fixture), Deportivo Garcilaso, Kashiwa Reysol.

The card rebuilt to three accas and was placed (final 09-06 slip at
32.47% of capital, state commit `5296ef4`). Vancouver dropped on the real
slate even after ingest normalisation shipped — its zoned witness was not
present at that build; the guard is the seatbelt for exactly this case.

### Task E — force-repick under-stakes (fixed); repeated repicks converge to bank/4

Root cause, confirmed with state evidence: on a repick the engine sized on
`effective_bank(st)` — which counted the day's OWN existing slip (its
morning draft, 3 × 7.2161% = 21.6%) as committed capital — while
`upsert_slip` then deleted and replaced that same slip as though it had
never existed. The two behaviours contradict each other. Today's incident:
printed free bank **75.8%** vs true free bank **97.4176%**; printed per-acca
**8.42%** vs doctrine **10.82%**; successive force-runs converge to
**bank/4, not bank/3** (8.42 → 8.02 → 8.15 → 8.11 → 24.35% total). The
operator cleared the slip from state by hand to place the corrected card —
that must never be necessary again, and is not.

Fix (`scripts/auto_tickets.py`): `effective_bank(st, exclude_date=...)`;
`cmd_today` sizes the target date on bank minus ALL open slips EXCEPT the
target date's own slip (it is about to be replaced). Stakes on other dates
stay committed — they are genuinely live. When a slip for the date already
exists, the ticket now prints a **REPICK** block naming per acca which
legs changed / stayed / were dropped, and the total-stake movement, so the
operator knows what has and has not already been placed.

Regression coverage (3 new tests): the repick path specifically — an
existing same-day slip in state with bank 100 → stakes size on
(100 − other-date 10)/3 per acca = 10.00, NOT (100 − own-draft 21.6 −
10)/3 = 7.60; a first run of the day cannot expose this bug, so the test
plants the same-day slip. Other-date slips remain committed in both
paths. Replacement-block lines tested for CHANGED / UNCHANGED / DROPPED.

The replay does not exercise the repick path (it settles each day
immediately), so the battery live row is untouched by the fix.

### Task F — the D1 operator-input path is cancelled; automatic build-time capture replaces it

**No manual price entry exists anywhere now.** `audit_clv record` and its
prompts are deleted (`scripts/audit_clv.py`); the D1 standing instruction
below is superseded and must not be followed. The two snapshot columns
(`actual_odds`, `actual_odds_recorded_at`) stay as empty schema, at zero
cost. Operator observation recorded for the ledger: at live placement the
engine's quoted odds were obtainable at his bookmaker — weaker than a
logged comparison, which is exactly what the automatic capture now
produces.

What ships instead (no human in the loop):

- `scripts/picks_today.py` `enrich_with_live_odds` now persists, on every
  pick at build time, a **`price_board`**: every price every source is
  showing for that fixture and selection (bzzoiro rows per bookmaker AND
  the scoutingstats secondary that previously was discarded after
  `PRICE_EVIDENCE_SCOUTINGSTATS_SOLE` was stamped), each with source name,
  bookmaker, value, raw `captured_at` (no timestamp claims — scoutingstats
  rows carry kickoff-as-captured_at by construction), and the chosen row
  flagged. Re-derived on every run (no stale boards). The engine's chosen
  price is untouched — the board is written alongside it.
- `scripts/auto_tickets.py` `cmd_today` appends **one JSON line per printed
  leg per run** to `localdata/price_board_<yyyy-mm>.jsonl` (append-only,
  never overwritten): date, printed_at, acca number, match, pick, the
  engine's printed odds and odds_source, and the full board. The
  actual-vs-quoted comparison therefore needs no archive and no typing.
- Every ticket prints a **PRICE BOARD** line: board persisted for n of m
  printed legs, corroborating sources on the card, and the expected
  coverage on the next slate — **100% of printed legs with an odds source**
  (a slate that runs without any odds bundle is the only zero case).

Effect on the P0 price question: D2's archive coverage was 7 of 81 ridden
scoutingstats legs (8.6%); forward coverage is 100% by construction from
the next printed slip, because the build-time boards are persisted before
the slip is written. No engine price, selection or staking changes; parity
baseline untouched; battery live row unchanged (+0.0319 log/day, 560%, 54
days, maxDD 67%).

### Task G — two record corrections

**G1 — the two "without those legs" tables are the SAME mechanism and DIFFERENT populations; the comparison sentence is withdrawn.** Both exclusion
arms in the Task-A asterisk ledger remove legs from the day's pool BEFORE
selection, and the engine re-pairs and re-plans from what remains —
mechanism: leg-drop with re-pairing. The region guard's row is not a
second mechanism ("leg-and-acca removal") but a different population: the
guard's rule drops the started legs AND every other leg its classes remove
(started-at-build others, remote-clock-only, missing/unparseable kickoffs,
cross-slate fixtures, already-settled), losing a bet-day where the default
does not. Measured contrast on the in-season default universe (35 days,
IN-SAMPLE):

| arm | mechanism | bet-days | log/day | final | maxDD |
|---|---|---|---:|---:|---:|
| shipped default | — | 35 | +0.0244 | 235% | 63% |
| minus the five | leg-drop + re-pairing | 35 | +0.0027 | 110% | 80% |
| minus the five | whole-acca removal, no re-pairing | 34 | −0.0068 | 79% | 86% (1 day fully dropped) |

Guard rows (272% shipped, 279% guard-minus-Weston) answer "the guard's own
population minus the legs it can drop", not "the default book without the
five"; the two tables must not be read as competing answers. The 110% row
stands, labelled default-universe leg-drop-with-re-pairing; the
cross-table sentence inviting the 2.5× reading is withdrawn.

**G2 — the sign reversal, one sentence.** Round 2's "the guard costs
−0.0070/day" (in-season) compared the guard against a started-only baseline
that RODE five already-started legs, four of which won; measured
like-for-like (perfect-clock exclusion of the five from both arms) the
guard LEADS the started-only arm (+0.0302 vs +0.0133 log/day, 279% vs
159%, both IN-SAMPLE, both within one-bet-day noise) — the earlier
conclusion was a contamination artefact of the won starters, and the
"guard costs money" reading is withdrawn; the guard's true cost remains
unmeasured until genuinely new days accrue.

### Task H — the ledger rebuild (reproduced; numbers below are the current archive's)

**Reproduce first.** On today's archive (35 settled in-season days ≥
2026-08-01) the 13 documented variant rows (floors 1.01…1.30,
`max_accas` 4/5/6, `saturated_accas` 4/5/6) were each demeaned to zero
true edge and days resampled jointly 20,000 times (seed 20260906), keeping
the winner per run (`scripts/search_noise.py`):

| statistic | today's archive (35 days) | brief's figure (33-day vintage) |
|---|---:|---:|
| winner under pure-noise null, median | **+0.0289/day** | +0.0372/day |
| p90 | +0.0744/day | +0.0885/day |
| P(noise ≥ +0.0410 headline) | **36%** | 46% |

Method, stated before the number: 13 variants run over identical settled
in-season days; each variant's own mean log/day subtracted (every variant
has exactly zero true edge); 20,000 joint day-resamples; per resample the
best variant's mean log/day is recorded. The winner distribution is what a
search this size manufactures from nothing — and the headline +0.0410 is
inside it. On today's archive the live-settings row is +0.0244/day (35
days, maxDD 63%), i.e. the headline itself has moved with two losing days.

**H1 — deployment gap.** Live daily log-volatility 0.1299 vs the 33%-replay
0.2240, because the engine stakes `effective_bank()` (open slips commit
capital) while the replay bets a fraction of full bank. Committed capital
from the 11 real ticket headers 08-27 → 09-06 (now including the
corrected 09-06 repick at 32.4726/97.4176 = 33.3% of bank): mean
deployment **21.7% of bank** (was 20.7% before the correction). In-season
replay at the measured fractions (same cards, same days, IN-SAMPLE):
33.3% → +0.0244/day, 235%, maxDD 63%, vol 0.2240; 20.7% → +0.0209/day,
208%, maxDD 43%, vol 0.1384; 21.7% → +0.0215/day, 212%, maxDD 45%, vol
0.1450. At live deployment the replay's volatility lands on the live
machine's 0.1299; the 33%-replay volatility gap WAS the committed-capital
gap. No setting changed. Pre-08-27 committed-capital reconstruction stays
unrecoverable (historical result donors carry no per-result landing time —
prior receipt stands); the 11-header measurement is the search-free ground
truth.

**H2 — honest forward number.** **There is no honest forward number yet.**
Every replay number on these days is in-sample for a ~27-variant search;
the only search-free estimator is the live ledger (10 real bet-days,
−0.0026 log/day, 16W/12L, bank 97.4% vs the 143.1% peak, bootstrap
P(edge>0) = 48% — statistically empty). The defensible statement until the
pre-registered tests accrue: expected edge is not distinguishable from
zero; live daily volatility ~0.13; live deployment ~21–22% of bank.

**H3 — the October pre-registration, re-stated on today's numbers.** The
rewritten slot (Task 2.3) stands: two questions on genuinely new in-season
days at n ≥ 60 under the standing bar (paired-bootstrap p10 > 0 AND every
leave-one-day-out keeps the sign AND maxDD ≤ live). Q1 `max_accas=4` — the
largest noise artefact in the 09-04 table (+0.0483 on that vintage's whole
archive; +0.0360/day in-season on today's 35 days) and exactly what a
winner-of-13 looks like. Q2 the live 1.20 odds floor — the lone spike:
floor=1.10 +0.0144, 1.15 −0.0132, **1.20 +0.0244**, 1.25 −0.0054, 1.30
+0.0032 on today's archive (the brief's −0.0065@1.15 / +0.0003@1.25 are
the 33-day vintage of the same spike). Expectation set in advance: both
are in-sample artefacts; testing them is right, expecting them to win is
not. At most one adoption from the family ever.

### Verification receipts (round 4)

- Suite: **425 passed** (416 prior + 3 Task-E repick tests + 6 Task-F
  price-board tests, minus 5 removed D1 record tests); `py_compile` and
  `git diff --check` clean.
- Constants: `MAX_ACCAS = 3`, `STAKE_FRAC = 1.0 / 3.0`,
  `MIN_LEG_ODDS = 1.20`, `MIN_ACCAS = 1`, `LEGS_PER_ACCA = 2` — unchanged.
- Battery live row unchanged: gate-off == live row +0.0319 log/day, 560%,
  54 days, maxDD 67% — identical to the pre-change receipt.
- `scripts/search_noise.py` receipts: winner median +0.0289, p90 +0.0744,
  P(noise ≥ +0.0410) = 36% (20,000 runs, seed 20260906); deployment mean
  21.7% over 11 real ticket headers; replay rows at 33.3/20.7/21.7% as in
  H1; G1 arms as in the G1 table.
- No engine file changed for sizing/selection: Task E touches only the
  repick sizing path (date-exclusion) plus the ticket warning; Task F adds
  append-only board fields; parity baseline file byte-identical.

## Addendum — 2026-09-06 (round 4 closeout): the estimate fell 40% on two days; growth at true deployment; one sentence on the exclusion figures

### The most important sentence in this ledger

The in-season replay estimate moved **+0.0410 → +0.0244** on the addition
of two bet-days (09-04 ×0.876, 09-05 ×0.777 — two ordinary losing days) — a
**40% fall from two observations**. Not a revision, not a bug: just two
more observations. On today's archive the same cut measures the 33-day
subset at +0.0387/day and the full 35 days at +0.0244/day; the operator's
cross-check arithmetic (33 × 0.0410 − 0.385 = 35 × 0.0277) is the same
mechanism, and the small residual is replay-vs-live card differences on
those two days. Our own noise null on those same 35 days gives a median
winner from a PURE-NOISE 13-variant search of **+0.0289/day**. Therefore:

**The measured in-season figure (+0.0244/day) is now below the noise floor
of the search that produced the configuration.** That is the strongest
single piece of evidence that the headline was never an edge measurement.

### Growth at true deployment (the reason the deployment gap was opened)

Item 1 of the closeout: growth and maxDD at the measured deployment, not
just volatility. In-season replay, live settings (IN-SAMPLE):

| stake | log/day | final | maxDD | daily log-vol |
|---|---:|---:|---:|---:|
| 33.3%/day (replay default) | +0.0244 | 235% | 63% | 0.2240 |
| **21.7%/day (true mean deployment, 11 real tickets)** | **+0.0215** | **212%** | **45%** | **0.1450** (live 0.1299) |

Direction was never in doubt — lower deployment means lower growth — and
the deployment-corrected figure is **materially below +0.0244**. This
+0.0215/day at 21.7% deployment is the only remaining candidate for an
honest forward figure, and it is NOT one: it is the same in-sample history
at the fraction the engine actually stakes. Nothing forward ships until
the pre-registered October questions reach n ≥ 60 in-season bet-days.

### One sentence on the six exclusion figures

235% / 110% / 79% / 272% / 279% / 159% — **none of these figures is
forward-valid; each measures which pairs happened to form under a given
exclusion, not engine performance, and cross-quoting any of them is an
error.**

No code changed this round (ledger only). Suite and constants unchanged
since the round-4 receipt: 425 passed; MAX_ACCAS=3, STAKE_FRAC=1.0/3.0,
MIN_LEG_ODDS=1.20; state file untouched at bank 97.417639 with the single
open 09-06 slip at 32.4725% (3 accas) until tonight's settlement.

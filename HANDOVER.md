Edge Factory — Handover

Date: 2026-06-18

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

writes localdata/edges_consensus.json

includes Phase A shadow scans for PredictZ and Windrawwin

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
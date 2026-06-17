Edge Factory — Handover
Date: 2026-06-17
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
Owner vision: 10+ sources, DuckDB analytics, edge discovery, validation, and decay forever
Stable current state:

Daily pipeline is stable.
Consensus counts are back to expected levels.
Certified edge accounting is restored.
BetExplorer research is concluded and should not be promoted into production.
PredictZ and Windrawwin remain shadow-only.
A small CLV audit spike is now wired into scripts/daily.py.
Current CLV is audit-only and not used for certification or pick gating.
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
CLV audit
scripts/audit_clv.py
writes localdata/clv_snapshots_YYYY-MM.csv.gz
writes localdata/clv_report_rolling.json
writes localdata/clv_report_YYYY-MM-DD.md
captures pick-time and end-of-run snapshots from daily.py
Future planning
inline inside scripts/daily.py
writes localdata/picks_YYYY-MM-DD.txt
writes localdata/picks_next_2days.json
Read-model sync
scripts/sync_supabase.py
syncs to Supabase / Postgres
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
audit_clv pick_time
inline future planner
restore target picks
audit_clv end_of_run
audit_clv rolling report
sync_supabase
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
2) Golden rules
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
3) Critical normalization rule
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
src/edgefactory/config.py
certification gates
important defaults:
min_n_train=350
min_n_valid=120
split="2025-06-01"
src/edgefactory/warehouse.py
DuckDB connect() and views
all views carry sport='soccer'
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
real-book odds enrichment
weighted consensus display and sorting
scripts/audit_clv.py
CLV capture and report utility
capture is wired into daily.py with pick_time and end_of_run labels
report stays audit-only in v1
scripts/daily.py
single orchestrator
also contains inline future planner
also triggers CLV capture and rolling report
scripts/sync_supabase.py
syncs certified edges and daily bucketed picks to Supabase
Optional research-only scripts:

scripts/backfill_betexplorer.py
BetExplorer result / odds cache
not production
scripts/mine_betexplorer.py
standalone / overlap mining on BetExplorer cache
not production
Manual safety layer:

config/entity_overrides.json
5) Source status
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
operational
real-book odds enrichment for picks_today
BetExplorer
research only
not a production source
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
7) Purity and bucket status
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
8) Phase A — unused-source confirmation
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

BetExplorer investigation — concluded negative for alpha
BetExplorer investigation is complete. It is not useful enough to add to consensus or picks.
Research utilities added:

scripts/backfill_betexplorer.py
result / odds caching
not production
scripts/mine_betexplorer.py
standalone and overlap mining
not production
These are research-only and are not wired into:

daily
warehouse
consensus
picks
BetExplorer cache design:

results archive run command: python3 scripts/backfill_betexplorer.py results START END
results archive output: localdata/betexplorer_results_YYYY-MM.csv.gz
odds archive run command: python3 scripts/backfill_betexplorer.py odds START END --workers N --sleep X --jitter Y
odds archive output: localdata/betexplorer_odds_YYYY-MM.csv.gz
Supported backfill flags:

--workers
--jitter
--max-seconds
--limit
--flush-every
--state-file
--retry-failures
--only-warehouse-candidates [WAREHOUSE]
--candidate-threshold
Also implemented:

Retry-After handling
terminal 404 failure cache
Failure cache:

localdata/betexplorer_odds_failures_YYYY-MM.csv.gz
Known stale 404s are skipped unless --retry-failures is passed.

Data pulled and tested:

results cache, 2026-01-01 to 2026-06-16: about 80k result rows
results cache, 2024-01-01 to 2025-12-31: hundreds of thousands of result rows
odds cache, 2026-01-01 to 2026-06-16: about 79,925 odds rows cached out of about 80,063 result rows
remaining missing rows: about 138 stale BetExplorer 404 match URLs
candidate-filtered historical odds, 2024-01-01 to 2025-12-31:
result rows considered: 331,682
matched broad EF warehouse consensus2/3 candidate filter: 2,449
odds rows fetched: 2,449
failures: 0
Standalone BetExplorer result on 2024-01-01 to 2026-06-16:

market favorite all:
n=63,802
hit=54.7%
Wilson LB=0.543
ROI=-2.6%
avg_odds=1.89
Favorite odds bands:

1.00-1.10 -> ROI=-2.2%
1.10-1.20 -> ROI=-0.2%
1.20-1.35 -> ROI=-0.2%
1.35-1.50 -> ROI=-1.2%
1.50-1.75 -> ROI=-3.8%
1.75-2.00 -> ROI=-1.4%
2.00-2.50 -> ROI=-3.8%
2.50+ -> ROI=-2.4%
Dropping / steam proxy:

steam dec_pct>=50% -> ROI=-4.9%
steam dec_pct>=70% -> ROI=-5.0%
steam dec_pct>=90% -> ROI=-5.2%
steam dec_count>=3 -> ROI=-4.9%
steam dec_count>=5 -> ROI=-4.5%
Standalone conclusion:

BetExplorer favorite is not alpha.
BetExplorer steam / dropping proxy is not alpha.
Do not add BetExplorer as a prediction source.
Do not add BetExplorer as a consensus vote.
EF x BetExplorer overlap result on 2024-01-01 to 2026-06-16:

n=984
hit=81.6%
Wilson LB=0.791
ROI=-0.1%
avg_odds=1.25
Train / validation split:

train, 2024-01-01 to 2025-05-31:
n=596
hit=78.4%
Wilson LB=0.749
ROI=-3.9%
valid, 2025-06-01 to 2026-06-16:
n=388
hit=86.6%
Wilson LB=0.828
ROI=+5.9%
The validation result looked good, but train was negative. This is a recent or regime effect, not a certified historical edge.

Train detail:

EF pick = BE steam proxy -> ROI=-6.1%
EF pick opposed by BE steam -> ROI=-0.6%
EF BE odds 1.20-1.35 -> ROI=+0.3%
EF BE odds 1.35-1.50 -> ROI=-11.0%
EF BE odds 1.50-1.75 -> ROI=-17.5%
Validation detail:

EF pick = BE steam proxy -> ROI=+9.5%
EF pick opposed by BE steam -> ROI=+1.6%
EF BE odds 1.20-1.35 -> ROI=+4.1%
EF BE odds 1.35-1.50 -> ROI=+6.8%
EF BE odds 1.50-1.75 -> ROI=+15.2%
Final decision:

BetExplorer is useful only as optional market intelligence and research.
Do not wire it into daily.
Do not wire it into warehouse.
Do not wire it into consensus.
Do not wire it into picks.
Do not add BetExplorer gates or levers at this time.
Stop spending active build time on BetExplorer unless specifically doing CLV research.
10) Supabase
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

Required environment variables:

BZZOIRO_TOKEN
SUPABASE_URL
SUPABASE_KEY
.env is not auto-loaded. Use:

set -a; source .env; set +a
11) How to run
Install requirements:

pip install -r requirements.txt
Export environment:

cp .env.example .env
set -a; source .env; set +a
Full daily:

PYTHONPATH=src python3 scripts/daily.py
Picks only:

PYTHONPATH=src python3 scripts/daily.py --picks-only --future-days 2
Specific date:

PYTHONPATH=src python3 scripts/daily.py --date 2026-06-16
Individual stages:

python3 scripts/capture_daily.py --skip-build
python3 scripts/backfill_results.py --days 30
python3 scripts/build_warehouse.py
PYTHONPATH=src python3 scripts/build_entity_registry.py
python3 scripts/mine_consensus.py
PYTHONPATH=src python3 scripts/decay_monitor.py
PYTHONPATH=src python3 scripts/assay_purity.py
PYTHONPATH=src python3 scripts/picks_today.py 2026-06-16
PYTHONPATH=src python3 scripts/audit_clv.py capture --date 2026-06-16 --label pick_time
PYTHONPATH=src python3 scripts/audit_clv.py capture --date 2026-06-16 --label end_of_run
PYTHONPATH=src python3 scripts/audit_clv.py report --start 2026-05-18 --end 2026-06-16
PYTHONPATH=src python3 scripts/sync_supabase.py
Tests:

PYTHONPATH=src python3 -m pytest tests/ -q
If optional Supabase dependencies are missing, at minimum run:

PYTHONPATH=src python3 -m pytest tests/test_assay.py -q
python3 -m py_compile src/edgefactory/util.py src/edgefactory/entities.py scripts/*.py
12) Known issues and caveats
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
bzzoiro
requires BZZOIRO_TOKEN
curl_cffi
required for PredictZ, Windrawwin, and BetClan scraping
consensus4
still thin because Vitibet overlap is limited
BetExplorer 404s
stale archived URLs exist
failure cache handles them
13) Future priorities — productive focus
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
Tournament / league classification.
classify competitions such as domestic league, cup, friendly, international, youth / reserves / women
use entity registry and league names to classify
then mine categories separately or veto categories separately
ML as a validated source.
possible features: source probabilities, agreement count, min_p, avg_p, spread, odds tier, price movement, source confirmations, entity tags, tournament tags
a model must be treated as another source and validated by the same miner / decay gates
New sports later.
do not add another sport yet
soccer still has clear remaining upside in CLV, tournament classification, and model-source validation
14) Engineering lessons — mandatory
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
15) Operational standard — anti-drift protocol
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
16) Current call
BetExplorer investigation is concluded. It is not useful enough to add to consensus or picks.

CLV audit spike is now live.

Current CLV state:

pick_time and end_of_run snapshots are captured automatically from scripts/daily.py
reporting is audit-only
same-label reruns dedupe correctly
a report with only one snapshot per pick must show no CLV comparison yet

Next session should focus on:

stable current daily pipeline
monitoring certified edges
CLV coverage and later-snapshot quality using existing bzzoiro_odds and real-book odds
avoiding broad source rabbit holes unless standalone proof exists
Last updated: 2026-06-17
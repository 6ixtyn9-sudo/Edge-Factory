🏭 Edge Factory — Handover
Date: 2026-06-17
Repo: https://github.com/6ixtyn9-sudo/Edge-Factory.git
Branch: main
Owner vision: 10+ sources, DuckDB analytics, edge discovery/validation/decay forever.

This file is the single source of truth for handover. Do not create BUILD_REPORT.md, CLEANUP_REPORT.md, SANITY_CHECK.md, etc. Update this file in place.

1. Current stable architecture
CSV/DuckDB first. Supabase is a read model for certified edges/picks, not the live analytics engine.

text

sources: prediction adapters + odds/market-data adapters
  fetch_day(date: str) -> list[dict]
  COLUMNS = [...]
  no classes, no normalize() methods

↓ scripts/capture_daily.py / scripts/local_backfill.py
localdata/*_YYYY-MM.csv.gz

↓ scripts/backfill_results.py
fills missing hs/gs from donor result sources

↓ scripts/build_warehouse.py
localdata/warehouse.duckdb
DuckDB views: forebet_settled, zulubet_settled, statarea_settled,
predictz_settled, scoutingstats_settled, bettingclosed_settled,
vitibet_settled, plus raw/capture-forward sources and consensus views

↓ scripts/build_entity_registry.py
localdata/entity_registry.json
canonical league/team aliases for purity/reporting only

↓ scripts/mine_consensus.py
walk-forward edge certification -> localdata/edges_consensus.json

↓ scripts/decay_monitor.py
60-day health audit / auto-bench circuit breaker

↓ scripts/assay_purity.py
context verdicts -> localdata/purity_registry.json

↓ scripts/picks_today.py
certified picks for target date -> stdout + localdata/picks_today.json

↓ inline future planner inside scripts/daily.py
per-date text reports -> localdata/picks_YYYY-MM-DD.txt
aggregate planner -> localdata/picks_next_2days.json

↓ scripts/sync_supabase.py
certified edges + daily bucketed picks -> Supabase/Postgres read model
Current daily run order:

text

capture_daily
→ backfill_results
→ build_warehouse
→ build_entity_registry
→ mine_consensus
→ decay_monitor
→ assay_purity
→ picks_today
→ inline future planner
→ sync_supabase
Important naming convention:

text

KEEP: scripts/daily.py       # only orchestrator
DO NOT ADD: scripts/nightly.py
DO NOT ADD: scripts/picks_future.py
Future reports are normal per-date text files:

text

localdata/picks_2026-06-16.txt
localdata/picks_2026-06-17.txt
Aggregate future JSON remains:

text

localdata/picks_next_2days.json
Do not reintroduce:

text

localdata/picks_calendar.csv
2. Golden rules
Wilson lower bound, never raw hit rate, for certification.
Walk-forward only. No mini-backtests.
ROI alongside hit rate, always.
Edge decay monitoring: HEALTHY / WATCH / DECAYING / DEAD.
Best odds inflate ROI versus real book execution — caveat always.
ANY disagreement is dangerous. Current known disagreement hit rate is poor.
Draw picks have historically not worked.
Away-only edges remain negative ROI in validation — do not certify away-only edges on current data.
OU 2.5 unanimous edges remain negative ROI across thresholds — not certified.
New sources must be mined standalone before being added as levers.
Market/odds data is not the same as model prediction data.
Do not change certified warehouse/miner join keys without full revalidation.
3. Critical normalization rule
A regression happened when norm_team() / norm_team_sql() were changed to accent-folding/wider keys. That inflated warehouse joins and collapsed certified edge count.

Bad inflated state observed:

text

consensus2: ~33k
consensus3: ~19k
consensus4: 526
certified edges dropped to 2
Correct stable state restored:

text

consensus2: ~27,450
consensus3: ~15,807
consensus4: ~383
9 certified audited / 2 benched / 7 active certified
Rule:

text

norm_team() / norm_team_sql()
  = legacy 9-character miner/source join keys
  = DO NOT CHANGE casually

norm_entity_team() / canonical_team() / canonical_league()
  = purity/reporting/entity-registry keys
  = safe for context grouping, not miner joins
Entity registry is for:

text

purity
reporting
context lookup
read-model keys
It must not silently change warehouse/miner joins.

4. Key files
Core package
text

src/edgefactory/assay.py
  Wilson LB/UB, grade, decay_verdict, ROI, should_bench,
  context verdict helpers, weighted_consensus_score.

src/edgefactory/util.py
  norm_team() and norm_team_sql(). Legacy miner join keys. Do not drift.

src/edgefactory/entities.py
  canonical_league(), canonical_team(), entity registry loading.
  For context/reporting only.

src/edgefactory/market_registry.py
  Market and odds-tier classification.

src/edgefactory/config.py
  Certification gates. Current key defaults include:
  min_n_train=350, min_n_valid=120, split="2025-06-01".

src/edgefactory/warehouse.py
  DuckDB connect() and views. All views carry sport='soccer'.
Scripts
text

scripts/capture_daily.py
  D30 capture for all sources; supports --skip-build.

scripts/backfill_results.py
  D30 default result repair after capture, before build_warehouse.
  Compact output by source. Idempotent.

scripts/build_warehouse.py
  Materializes CSV cache into localdata/warehouse.duckdb.

scripts/build_entity_registry.py
  Learns league/team aliases into localdata/entity_registry.json.
  Uses same-event and team-pool overlap evidence + config/entity_overrides.json.

scripts/mine_consensus.py
  Walk-forward consensus miner. Writes localdata/edges_consensus.json.
  Includes Phase A shadow confirmation scans for PredictZ/Windrawwin.

scripts/decay_monitor.py
  60-day health audit and auto-bench circuit breaker.
  Must recreate every miner TEMP view that a certified edge may use.

scripts/assay_purity.py
  Context purity registry. Default window is max/all-history style: --window 36500.
  Must recreate every miner TEMP view that a certified edge may use.

scripts/picks_today.py
  Certified picks engine. Purity-aware buckets, real-book odds enrichment,
  weighted consensus display/sorting.

scripts/daily.py
  Single orchestrator. Also contains inline future planner.

scripts/sync_supabase.py
  Syncs certified edges + daily bucketed picks to Supabase.

scripts/backfill_betexplorer.py
  Optional research utility for BetExplorer result/odds cache.
  Not wired into daily/warehouse/consensus.

scripts/mine_betexplorer.py
  Optional local-only research utility for cached BetExplorer standalone/overlap mining.
  Not wired into daily/warehouse/consensus.
Config
text

config/entity_overrides.json
  Small committed manual alias safety layer.
5. Sources status
Prediction adapters currently in src/edgefactory/sources/:

text

forebet            core 1x2/OU/BTTS/HT source, high-volume, backfillable
zulubet            core 1x2 source, backfillable
statarea           core 1x2/OU source, backfillable
vitibet            1x2 source, archive but thinner in consensus4
scoutingstats      partial 1x2/OU/BTTS, sparse/capture-forward
predictz           captured, settled rows exist, Phase A shadow only
windrawwin         captured, very thin, Phase A shadow only
betclan            used partially as live/capture-forward 1x2 source
bzzoiro            used partially as live model source
freesupertips      captured but too thin/unmapped for current mining
bettingclosed      large settled source, used as confirmation lever
Odds/market-data adapters:

text

bzzoiro_odds       operational real-book odds enrichment for picks_today
BetExplorer        optional research cache only; not a production source
Unused/mostly-unused prediction sources remain:

text

predictz
windrawwin
freesupertips
afootballreport
Phase A showed PredictZ/Windrawwin are not ready for certification under current split.

6. Certified edge state
Latest stable runs restored expected accounting:

text

consensus2: ~27,450
consensus3: ~15,807
consensus4: ~383
Latest certified audit shape:

text

9 certified audited
2 benched by decay
7 active certified
Expected active/base findings around latest stable runs:

text

2way-unanimous avg_p>=70                       WATCH / active
3way-unanimous avg_p>=65                       HEALTHY / active
2way-unanimous min_p>=60 avg_p>=65             HEALTHY / active
3way-unanimous min_p>=60 avg_p>=65             WATCH / active
2way-unanimous home-only avg_p>=65             HEALTHY / active
3way-unanimous home-only avg_p>=60             HEALTHY / active
3way-unanimous home-only avg_p>=65             HEALTHY / active
Benched by 60-day decay circuit breaker:

text

3way-unanimous min_p>=60 avg_p>=60
2way+bc-confirms avg_p>=60
Do not manually unbench. Benching is correct behavior. Next mine_consensus.py re-evaluates from full walk-forward history.

Operational picks_today.py thresholds are base canonical only:

text

2-way: 2way-unanimous avg_p>=70
3-way: 3way-unanimous avg_p>=65
Qualified rules are analysis/purity variants only. They must not displace base thresholds.

Qualified tokens include:

text

min_p
home-only
away-only
odds-
bc-confirms
predictz-confirms
windrawwin-confirms
freesupertips-confirms
7. Purity / bucketing status
assay_purity.py default:

text

--window 36500
Current reality:

text

league/team purity remains sparse/unrated inside certified-rule subsets
odds-band purity is mature and useful
Operational bucket logic:

text

benched/dead/decaying edge -> SKIPPED_DEAD_EDGE
VETO anywhere              -> SKIPPED_VETO
missing odds               -> WATCHLIST_NO_ODDS
UNKNOWN odds_band          -> WATCHLIST_UNKNOWN_CTX
CAUTION anywhere           -> CAUTION
UNKNOWN league/team only   -> CAUTION
otherwise                  -> CERTIFIED_CLEAN
Rationale:

text

league/team UNKNOWN = unrated, not bad
odds_band VETO/CAUTION = meaningful mature context
Recent examples:

text

Vaprus vs Flora Tallinn                 -> CAUTION
Always Ready vs Universitario de Vinto  -> CAUTION
Fortaleza vs América Mineiro            -> SKIPPED_VETO due odds_band VETO
8. Phase A — unused source confirmation
Implemented as shadow/maturity scans only.

Rules scanned:

text

2way+predictz-confirms avg_p>=60/65/70/75
3way+predictz-confirms avg_p>=60/65/70
2way+windrawwin-confirms avg_p>=60/65/70/75
3way+windrawwin-confirms avg_p>=60/65/70
decay_monitor.py and assay_purity.py recreate the corresponding TEMP views so any future certified Phase A edge would not silently skip audit/assay.

Current result:

text

PredictZ archive starts around 2026.
Windrawwin is capture-forward only.
Global split is 2025-06-01.
Therefore train n = 0 for these confirmation levers.
They print in a shadow section but are excluded from edges_consensus.json by normal training gates.

Do not use PredictZ/Windrawwin in picks yet.
Do not force certification.

9. BetExplorer investigation — concluded negative for alpha
BetExplorer was investigated because it is a huge market-data source.

Implemented research utilities:

text

scripts/backfill_betexplorer.py
scripts/mine_betexplorer.py
These are optional research scripts only. They are not wired into daily, warehouse, consensus, or picks.

BetExplorer cache design
Results archive:

text

python3 scripts/backfill_betexplorer.py results START END
localdata/betexplorer_results_YYYY-MM.csv.gz
Odds archive:

text

python3 scripts/backfill_betexplorer.py odds START END --workers N --sleep X --jitter Y
localdata/betexplorer_odds_YYYY-MM.csv.gz
Backfill supports:

text

--workers
--jitter
--max-seconds
--limit
--flush-every
--state-file
--retry-failures
--only-warehouse-candidates [WAREHOUSE]
--candidate-threshold
Retry-After handling
terminal 404 failure cache
Failure cache:

text

localdata/betexplorer_odds_failures_YYYY-MM.csv.gz
Known stale 404s are skipped unless --retry-failures is passed.

Data pulled/tested
BetExplorer results cache:

text

2026-01-01 → 2026-06-16: ~80k result rows
2024-01-01 → 2025-12-31: hundreds of thousands of result rows
BetExplorer odds cache:

text

2026-01-01 → 2026-06-16: ~79,925 odds rows cached out of ~80,063 result rows
remaining ~138 rows were stale BetExplorer 404 match URLs
Candidate-filtered historical odds:

text

2024-01-01 → 2025-12-31
331,682 BetExplorer result rows considered
2,449 matched broad EF warehouse consensus2/3 candidate filter
2,449 odds rows fetched
0 failures
Standalone BetExplorer result
On 2024-01-01 → 2026-06-16:

text

Market favorite all:
  n=63,802
  hit=54.7%
  Wilson LB=0.543
  ROI=-2.6%
  avg_odds=1.89
Favorite odds bands:

text

1.00-1.10   ROI=-2.2%
1.10-1.20   ROI=-0.2%
1.20-1.35   ROI=-0.2%
1.35-1.50   ROI=-1.2%
1.50-1.75   ROI=-3.8%
1.75-2.00   ROI=-1.4%
2.00-2.50   ROI=-3.8%
2.50+       ROI=-2.4%
Dropping/steam proxy:

text

steam dec_pct>=50%   ROI=-4.9%
steam dec_pct>=70%   ROI=-5.0%
steam dec_pct>=90%   ROI=-5.2%
steam dec_count>=3   ROI=-4.9%
steam dec_count>=5   ROI=-4.5%
Conclusion:

text

BetExplorer favorite is not alpha.
BetExplorer steam/dropping proxy is not alpha.
Do not add BetExplorer as a prediction source.
Do not add BetExplorer as a consensus vote.
EF × BetExplorer overlap result
Combined 2024-01-01 → 2026-06-16:

text

EF overlap all @ BE odds:
  n=984
  hit=81.6%
  Wilson LB=0.791
  ROI=-0.1%
  avg_odds=1.25
Train/valid split:

Train 2024-01-01 → 2025-05-31:

text

EF overlap all @ BE odds:
  n=596
  hit=78.4%
  Wilson LB=0.749
  ROI=-3.9%
Valid 2025-06-01 → 2026-06-16:

text

EF overlap all @ BE odds:
  n=388
  hit=86.6%
  Wilson LB=0.828
  ROI=+5.9%
The valid result looked good, but train was negative. This is a regime/recent-period effect, not a certified historical edge.

Train details:

text

EF pick = BE steam proxy      ROI=-6.1%
EF pick opposed by BE steam   ROI=-0.6%
EF BE odds 1.20-1.35          ROI=+0.3%
EF BE odds 1.35-1.50          ROI=-11.0%
EF BE odds 1.50-1.75          ROI=-17.5%
Valid details:

text

EF pick = BE steam proxy      ROI=+9.5%
EF pick opposed by BE steam   ROI=+1.6%
EF BE odds 1.20-1.35          ROI=+4.1%
EF BE odds 1.35-1.50          ROI=+6.8%
EF BE odds 1.50-1.75          ROI=+15.2%
Final decision:

text

BetExplorer is useful only as optional market intelligence / research.
Do not wire BetExplorer into daily, warehouse, consensus, or picks.
Do not add BetExplorer gates/levers at this time.
Stop spending active build time on BetExplorer unless specifically doing CLV research.
10. Supabase
Migrations live in supabase/migrations/.

Key status:

text

0001_core.sql
0002_signals.sql
0003_edges.sql
0004_new_sources.sql
0005_all_sources.sql
0006_edge_pick_context.sql
sync_supabase.py promotes:

text

certified edges -> edges
bucketed daily picks -> edge_picks
Live ingestion/analytics remains CSV/DuckDB.

Required env:

text

BZZOIRO_TOKEN
SUPABASE_URL
SUPABASE_KEY
.env is not auto-loaded. Use:

Bash

set -a; source .env; set +a
11. How to run
Install requirements:

Bash

pip install -r requirements.txt
Export env:

Bash

cp .env.example .env
set -a; source .env; set +a
Full daily:

Bash

PYTHONPATH=src python3 scripts/daily.py
Picks only:

Bash

PYTHONPATH=src python3 scripts/daily.py --picks-only --future-days 2
Specific date:

Bash

PYTHONPATH=src python3 scripts/daily.py --date 2026-06-16
Individual stages:

Bash

python3 scripts/capture_daily.py --skip-build
python3 scripts/backfill_results.py --days 30
python3 scripts/build_warehouse.py
PYTHONPATH=src python3 scripts/build_entity_registry.py
python3 scripts/mine_consensus.py
PYTHONPATH=src python3 scripts/decay_monitor.py
PYTHONPATH=src python3 scripts/assay_purity.py
PYTHONPATH=src python3 scripts/picks_today.py 2026-06-16
PYTHONPATH=src python3 scripts/sync_supabase.py
Tests:

Bash

PYTHONPATH=src python3 -m pytest tests/ -q
If optional Supabase deps are missing, at least run:

Bash

PYTHONPATH=src python3 -m pytest tests/test_assay.py -q
python3 -m py_compile src/edgefactory/util.py src/edgefactory/entities.py scripts/*.py
12. Known issues / caveats
text

BetExplorer:
  investigated and concluded not useful as alpha source.
  keep optional only.

PredictZ/Windrawwin:
  shadow-only. train n=0 under current split.

League/team purity:
  sparse/unrated. Treat UNKNOWN league/team as CAUTION, not hard block.

Odds-band purity:
  mature and currently useful.

bzzoiro:
  requires BZZOIRO_TOKEN.

curl_cffi:
  required for predictz / windrawwin / betclan scraping.

consensus4:
  still thin because vitibet overlap is limited.

BetExplorer 404s:
  stale archived URLs exist; failure cache handles them.
13. Future priorities — productive focus
Stop chasing BetExplorer unless doing deliberate CLV research.

Recommended next productive work:

Stabilize and commit current pipeline.

Keep repo clean.
Keep handover updated.
Avoid broad payloads.
Monitor current certified soccer edges.

Let decay circuit breaker do its job.
Do not manually unbench.
CLV with existing operational odds.

Use bzzoiro_odds / real-book snapshots already captured.
Track pick-time price vs later/closing price.
Add CLV as an audit dimension before using it as a feature.
Tournament/league classification.

Domestic league vs cup vs friendly vs international vs youth/reserves/women.
Use entity registry and league names to classify.
Mine or veto categories separately.
ML as validated source.

Features: source probabilities, agreement count, min_p, avg_p, spread,
odds tier, price movement, source confirmations, entity/tournament tags.
Model must be treated as another source and validated by same miner/decay gates.
New sports later.

Do not add another sport yet.
Soccer still has CLV, tournament classification, and model-source validation to exploit.
14. Engineering lessons — mandatory
L1 — Three-script view graph
mine_consensus.py creates TEMP views. decay_monitor.py and assay_purity.py recreate those views.

When adding a miner view, add identical SQL to both recreate functions.

Failure mode is silent:

text

UNKNOWN/SKIP in decay or purity
L2 — consensus2 does not expose hkey/akey
consensus2 joins internally on keys but only outputs:

text

date, home, away, outcome, fb_pick, zb_pick, fb_p, zb_p, avg_p, pick_odds, league
When joining from consensus2 / v_consensus2, join on:

text

date, home, away
not:

text

date, hkey, akey
L3 — Qualified rules must not govern picks_today thresholds
Rules containing:

text

min_p
home-only
away-only
odds-
bc-confirms
predictz-confirms
windrawwin-confirms
freesupertips-confirms
are analysis variants. They must not displace canonical operational thresholds.

L4 — No stubs/placeholders
No ..., no # keep existing, no editorial comments pretending to be code. Payload files must be complete runnable files.

L5 — No runtime globals
Avoid module-level globals initialized inside main(). Pass state explicitly.

L6 — Decay circuit breaker is correct
DECAYING -> BENCHED is the system working. Do not manually edit registry to unbench.

L7 — Executor copies payloads, never rewrites
Install payload files by cp. Do not reconstruct from chat.

L8 — Do not mutate certified join keys
norm_team() / norm_team_sql() are miner-critical. Do not change them without full revalidation.

15. Operational standard — anti-drift protocol
Every repo change should follow payload discipline:

text

BUILDER -> EXECUTOR -> VERIFIER
Payload bundle includes:

text

payload files
SHA256SUMS
commit_msg.txt
executor notes
Rules:

Verify payload hash before touching repo.
Required base commit should be pinned for commits.
Install by cp only.
Run py_compile and tests.
Confirm git status has only expected files.
No helper files in repo.
Claims without fresh clone/on-GitHub verification are not proof.
Data jobs are exception only because localdata/ is gitignored. They still need clean git status and row-count report.

16. Current call
BetExplorer investigation is concluded. It is not useful enough to add to consensus/picks.

Focus next session on productive work:

text

stable current daily pipeline
monitor certified edges
CLV with existing bzzoiro_odds / real-book odds
avoid broad source rabbit holes unless standalone proof exists
Last updated: 2026-06-17
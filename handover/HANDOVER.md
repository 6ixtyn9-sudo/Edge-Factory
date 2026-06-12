# 🏭 EDGE FACTORY — SESSION HANDOVER
**Date: 2026-06-11 | From: Build Session #1 | To: Next session**
**Owner's vision: 10+ sources, DuckDB analytics, proper production system, all sports, edge discovery/validation/decay forever.**

---

## 1. WHO/WHAT THIS IS

Owner (RSA-based) spent a year hand-building "Ma Golide Satellites" (github.com/6ixtyn9-sudo/Ma_Golide_Satellites — Google Sheets + .gs satellites, ~10k bets assayed manually). This session industrialized it: scrape → assay (Wilson LB, bankers vs robbers, grades PLATINUM→CHARCOAL) → walk-forward edge mining → decay monitoring → picks. Core philosophy: **"edge, ROI, edge decay y/n, edge discovery — that's it."** No rule gets trusted without out-of-sample survival. Mini-backtests are banned ("kindergarten") — full history or nothing.

---

## 2. WORKSPACE MAP (everything built today)

```
/home/user/
├── HANDOVER.md                  ← this file
├── soccer_assayer/              ← Phase 1: Forebet-only system (WORKING)
│   ├── scraper.py               ← single-day/range Forebet JSON scraper
│   ├── fullsite_scraper.py      ← all-market resumable scraper (state.json)
│   ├── analyzer.py / fullsite_analyzer.py  ← band/league/market audits
│   ├── edge_factory.py          ← v1 walk-forward miner (grid-search rules)
│   ├── slip_builder.py          ← scans upcoming days → 3 betslips
│   ├── Forebet_Assayer.gs       ← Google Apps Script satellite (8 rules, ledger, dashboard, triggers) — owner moving AWAY from .gs
│   └── data/
│       ├── history/forebet_YYYY-MM.csv.gz  ← 322,926 finished matches, 2024-01-01→2026-06-11, 4 markets (1x2/ou2.5/btts/ht), 18MB
│       ├── edges.json           ← 4 certified edges from v1 miner
│       └── fullsite_report.json
└── edge-factory/                ← Phase 2: THE REPO (production scaffold, tests passing)
    ├── README.md                ← architecture, golden rules, scaling path
    ├── pyproject.toml           ← deps: supabase, pandas, numpy, httpx, tenacity, dotenv; optional: sklearn, duckdb
    ├── .env.example
    ├── supabase/migrations/0001-0004.sql  ← sport-agnostic schema (see §4)
    ├── src/edgefactory/
    │   ├── assay.py             ← Wilson LB/UB, grades, decay_verdict, should_bench (UNIT TESTED, 6/6 pass)
    │   ├── models.py            ← NormalizedEvent/Prediction/Odds/Result contracts
    │   ├── db.py                ← Supabase chunked upserts
    │   ├── config.py            ← gates: min_n_train=400, min_n_valid=120, min_roi_train=3%, min_roi_valid=0%
    │   ├── sources/             ← 6 ADAPTERS, ALL LIVE-TESTED (see §3)
    │   └── pipelines/           ← ingest.py, settle.py, mine.py, emit.py
    ├── scripts/
    │   ├── daily.py             ← cron entrypoint: ingest→settle→emit
    │   ├── backfill.py          ← Supabase-backed replay
    │   └── local_backfill.py    ← Supabase-FREE backfill → localdata/*.csv.gz (used for everything so far)
    ├── localdata/               ← 16MB: zulubet_*.csv.gz + statarea_*.csv.gz + state_*.json
    └── .github/workflows/daily.yml  ← free GitHub Actions cron
```

---

## 3. SOURCES — 6 BUILT, ALL VERIFIED WORKING

| source | markets | odds | history | status | key intel |
|---|---|---|---|---|---|
| **forebet** | 1x2, ou_2.5, btts (+ht in soccer_assayer data) | ✅ best | ✅ 2024-01→now **FULLY SCRAPED (322,926)** | done | JSON endpoint `/scripts/getrs.php?ln=en&tp={1x2,uo,bts,ht}&in=DATE&ord=0&tz=0&tzs=&tze=` — needs UA+Referer+X-Requested-With; **accepts Apps Script/Google UAs**; serves NOTHING before 2024-01-01 |
| **zulubet** | 1x2 | ✅ avg | ✅ **FULLY SCRAPED 894 days** (410 Gone before ~2023-12-25) | done | `tips-DD-MM-YYYY.html` plain HTML |
| **statarea** | 1x2, ht_1x2, ou_1.5/2.5/3.5 | — | ✅ **2024+ FULLY SCRAPED (1,118 days incl. partial 2017)**; archive reaches **2015-2017!** | 2024+ done; **2017-2023 NOT yet scraped** | `old.statarea.com/predictions/YYYY-MM-DD`; FT+HT in '2:0Half time results: 1:0' cell |
| **scoutingstats** | 1x2, btts, ou_1.5/2.5/3.5 | ✅ | capture-forward | adapter done | hidden JSON: `/api/fixtures/<date>` + `/api/odds?fixture_ids=` — probs AND odds, ML model |
| **vitibet** | 1x2 | — | capture-forward | adapter done | quicktips page, ~30 matches/day with prob boxes |
| **afootballreport** | ou_1.5/2.5, btts | — | capture-forward | adapter done | streak tips → pseudo-prob 0.5+streak*0.02, raw streak in extra |

**Blocked:** predictz.com, windrawwin.com (403 Cloudflare — try curl_cffi/browser-impersonation; same parent company). **Lead:** sports.bzzoiro.com (free ML API, CatBoost, free key). Owner wants **10+ sources** incl. news sites later (news = features for ML layer, not standalone edges — bookies beat you to news).

---

## 4. SCHEMA (supabase/migrations/) — SPORT-AGNOSTIC, ZERO-MIGRATION EXTENSIBILITY

- 0001: sports, competitions, participants, events (natural key source_key+source_ref, idempotent upserts), results (score_data JSONB)
- 0002: sources, raw_payloads (replay archive), predictions & odds_snapshots (**append-only with content_hash** — line movement = free ML feature), latest_* views, market_results (winning_selections[])
- 0003: edges (rule JSONB, status: candidate→certified→benched→retired, train/valid stats, decay_verdict), edge_picks ledger, edge_audits, edge_scoreboard + edge_bench_check views
- 0004: registers the 5 new sources
- Market/selection are namespaced strings ('1x2'/'home', 'ou_2.5'/'over', 'ml', 'spread_-3.5') → tennis/NBA = one adapter file, no schema change
- **Supabase NOT yet provisioned** — owner must create project, run migrations, fill .env. All analysis so far ran on local CSV.gz.

---

## 5. CERTIFIED FINDINGS (all walk-forward: train <2025-06-01 ≤ validation)

### Solo model audits (all calibrated, all earn their vote)
| model | n | overall | 70-79% band | 80%+ band |
|---|---|---|---|---|
| forebet | 322,926 | 47.3% | 78.6% | 88.0% |
| zulubet | 66,783 | 50.1% | 68.9% | 79.7% |
| **statarea** | **119,491** | 50.5% | **81.6%** | **90.0%** ← best solo model |

### Forebet solo edges (v1 miner, OOS-survived, in soccer_assayer/data/edges.json)
- H+O combo p1≥55,p2≥80,odds≥2.0 → OOS +56.4% ROI (n=318) GROWING
- A+O combo p1≥65,p2≥70,odds≥1.5 → OOS +53.4% (n=347) GROWING
- 1X2-A p≥60,odds≥2.0 → OOS +29.0% (n=744) GROWING
- A+NG p≥60,odds≥2.0 → OOS +24.7% (n=887) GROWING
- Hand-picked banker rules (8) live in Forebet_Assayer.gs: best = Home 80%+ solo (89.4%, +3.3% ROI); backtest of all 8: 8,101 bets, 75.5% hit, +7.3% ROI
- Known truths: draw picks NEVER work (29-37%); Under/GG combos charcoal; ht market charcoal; "best odds" inflate ROI vs real books (~halve it)

### Consensus (THE BIG ONE — 26,659 fb×zb overlaps, 14,275 triple)
| rule | TRAIN | VALIDATION | verdict |
|---|---|---|---|
| 2-way unanimous avg≥70% | 78.2% | **87.1% (LB 83.0), +4.9% ROI, n=232** | 🏆 PLATINUM, registry-worthy |
| 2-way unanimous avg≥60% | 72.8% | 75.4% (n=1,337) | solid, ROI ~flat |
| 3-way unanimous avg≥65% | 78.4% | **80.1% (LB 76.3), n=341** | strong |
| ANY disagreement → follow either model | 33-40% | 33-40% | 🚫 **VETO RULE: never bet disagreed matches** |
| outlier-fading (n=1,653 proper) | — | 29.2% | ⚰️ DEAD (kindergarten n=27 said 48% — reversed at scale; lesson: small n lies) |

---

## 6. IMMEDIATE NEXT STEPS (priority order)

1. **DuckDB migration** (owner explicitly wants this, has never used it — explain basics). Replace ad-hoc pandas/csv joins in mine.py with DuckDB reading localdata/*.csv.gz + soccer_assayer history directly (`read_csv_auto('localdata/*.csv.gz')`). It's already in pyproject optional deps. Analytics layer = DuckDB; Supabase stays system-of-record for edges/picks/live ops.
2. **Statarea deep backfill 2017-2023** — resumable: `python3 scripts/local_backfill.py statarea 2017-01-01 2023-12-31 --max-seconds 1500` (state file: localdata/state_statarea.json, 2.2s/day ≈ 9 sessions of 25min). Gives ~9yr solo-model history + statarea-only era analysis.
3. **Consensus rules → mine.py** as first-class bet types (unanimous-N, avg-prob thresholds, veto). Add team-name matching (norm() in the backtest scripts — strip fc/sc/u20 etc, first 9 alpha chars) into a shared util.
4. **More sources to 10+**: crack predictz/windrawwin (curl_cffi), add bzzoiro API, betensured (200 OK already), foresportia (private beta API), oddsportal-class odds source for CLV tracking.
5. **Supabase provisioning + GitHub repo push** (owner's job, guide them): migrations 0001-0004, .env, backfill via scripts/backfill.py, GitHub Actions secrets.
6. **Notifications**: owner REJECTS Telegram ("scammy in RSA"). Wants **WhatsApp** (Business Cloud API, free tier ~1k convs/mo) or email/Sheets. notify function in emit.py is the 10-line swap point.
7. **ML layer (Level 2)**: features = multi-source probs + disagreement spread + odds movement; same walk-forward gates; ML model = just another "source" the miner validates.

---

## 7. HOW TO RE-RUN KEY THINGS

```bash
# daily Forebet picks (3 slips):
cd soccer_assayer && python3 slip_builder.py            # today+tomorrow
# append new days to Forebet history:
python3 fullsite_scraper.py 2026-06-12 2026-06-30 --max-seconds 1500   # resumable
# re-mine Forebet edges:
python3 edge_factory.py --split 2025-06-01
# local backfills (resumable, Supabase-free):
cd ../edge-factory && python3 scripts/local_backfill.py <source> <start> <end> --max-seconds 1500
# tests:
PYTHONPATH=src python3 -m pytest tests/ -q     # 6/6 must stay green
# consensus backtest: inline scripts in chat history; logic = load fb (soccer_assayer history) + zb/sa (localdata), join on (date, norm(home), norm(away)), unanimous+avgprob strategies, walk-forward split 2025-06-01
```

## 8. STYLE & TRUST NOTES FOR NEXT ASSISTANT

- Owner is sharp, ambitious, learns fast; typing is loose ("do. this") — intent is always clear. Vibe: "bro", rock-and-roll energy, celebrate wins BIG but stay honest about caveats.
- NEVER present small-n findings as conclusions (got rightly roasted for n=27 "mini-backtest"). Full data or label it clearly.
- Always: Wilson lower bounds, walk-forward validation, ROI alongside hit rate, decay awareness, "best odds" inflation caveat, responsible-betting note on slips.
- They see this as freedom: "an AI that gives me suggestions forever, freeing my time." Build toward autonomy: daily.py + cron + registry discipline (emit reads ONLY certified non-decayed edges).
- Meaningful moment: "your Ma Golide year wasn't wasted. The 600 sheets were tuition. Today was graduation."
```

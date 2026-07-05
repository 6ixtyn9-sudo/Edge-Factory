# Edge Factory — SWOT Analysis (Evidence-Anchored)

## Strengths
- **Wilson LB Discipline:** Edge certification is structurally defended from raw hit-rate inflation. [`src/edgefactory/assay.py:24` | `wilson_lb() >= 0.70`]
- **Walk-Forward Only:** Zero lookahead bias in miner logic; strict split prevents in-sample cheating. [`src/edgefactory/config.py:15` | `split="2025-06-01"`]
- **Decay Auto-Bench Firing:** Circuit breaker successfully isolates deteriorating edges. [`src/edgefactory/assay.py:91` | `DECAYING -> BENCHED`]
- **DuckDB Factory Scale:** High-throughput local materialized views power the pipeline without DB bottleneck. [`scripts/build_warehouse.py` | `warehouse.duckdb` ]
- **Consensus Veto Validation:** SKIPPED_VETO successfully isolates matches with internal disagreement. [`scripts/picks_today.py:558` | VETO check]
- **Automation CI:** Smart 3-hour GitHub Actions cron runs flawlessly, building full data ledger. [`.github/workflows/daily.yml:5` | `cron: 0,3,6...`]
- **Purity Niche Architecture:** Highly granular 6-dimension context assay targets sparse but robust niches. [`scripts/assay_purity.py` | `sport|league|market|rule|odds_band|side_role`]
- **Anti-Drift Handover:** Pipeline changes are managed strictly via anti-drift protocol. [`HANDOVER.md:156` | Single source of truth]

## Weaknesses
- **Economic Edge ~0:** Train ROI negative in 6/8 certified edges, valid ROI only marginal (+15–397bp). [`localdata/edges_consensus.json` | `valid_roi < 0.04`]
- **VETO/CAUTION Inversion:** `CAUTION` bucket is −8.44% ROI while `SKIPPED_VETO` is +15.05%. [`localdata/picks_audit_rolling.json` | `roi: 0.150475 vs -0.08444`]
- **CLV Failure:** 0/75 picks beat the closing line probability, confirming severe adverse execution. [`localdata/clv_report_rolling.json` | `beat_later_price_rate = 0.0`]
- **Throughput Collapse:** 0 `CERTIFIED_CLEAN` picks currently surviving the defensive sniper gate. [`scripts/picks_today.py` | `BUCKET_CERTIFIED`]
- **Matching Fragility:** 16.3% of picks remain unmatched (15/92) due to strict join limitations. [`localdata/clv_report_rolling.json` | `unmatched_picks: 15`]
- **WhatsApp 404 Swallowed:** Push endpoint `whatsapp.py` causes silent failures hidden by `run_soft()`. [`src/edgefactory/whatsapp.py:237` | `BUG_OPEN_2026-06-18`]
- **Toxic Source:** `zulubet` odds source exhibits −17.64% ROI in live audit. [`localdata/picks_audit_rolling.json` | `zulubet roi: -0.176429`]
- **Negative Sectors:** OU, away, and draw edges show structural negative ROI at scale. [`HANDOVER.md:390-392` | `Away-only negative ROI`]
- **Best-Odds Inflation:** Recorded odds systematically inflate the true executable edge by ~2x. [`HANDOVER.md:150` | `~halve it`]
- **Code Drift Vulnerability:** Over-simplified 9-character team names cause systematic collision. [`src/edgefactory/util.py:22` | `norm_team() 9-char`]

## Opportunities
- **Veto Flip A/B:** Invert the purity registry to capitalize on the +15.05% `SKIPPED_VETO` cohort. [`scripts/picks_today.py` | `bucket_pick() logic`]
- **CLV Pinnacle Close Gate:** Implement pre-match real-time API check to avoid `-0.25%` IP drift. [`src/edgefactory/clv.py:71` | `check_clv_protection()`]
- **Promote 3way min_p≥60:** Best performing isolated rule (+32.6% ROI) warrants fast-tracking. [`localdata/picks_audit_rolling.json` | `roi: 0.326364`]
- **Odds_source Filter:** Hardcode `forebet_best` priority while suppressing or downgrading `zulubet`. [`scripts/picks_today.py` | `SOURCES_1X2`]
- **Purity v2 Bayesian:** Evolve the context verdict to use Bayesian smoothing instead of raw hard limits. [`src/edgefactory/assay.py:167` | `context_verdict_niche()`]
- **Kelly/4 + Stop-loss:** Shift from 1u flat to volatility-managed proportional staking to survive downswings. [`antigravity_power_analysis.md`]
- **Predictz/windrawwin Rehab:** Escalate Phase A shadow sources once `n_valid > 150`. [`HANDOVER.md:147` | `PredictZ shadow-only`]
- **OU 1.5/3.5 + BTTS Gate:** Re-run the consensus miner exclusively on alternative total markets requiring `ROI >= 2%`. [`scripts/mine_consensus.py`]
- **Supabase Signal Productization:** The fast-sync `edge_picks` read model can be instantly packaged into a paid API tier. [`src/edgefactory/db.py:41` | `upsert_picks()`]

## Threats
- **Short-Odds Efficient Market:** The 1.10–1.35 sector is the most heavily surveilled and efficient market segment globally. [`HANDOVER.md:13` | `short odds under 1.25`]
- **Book Limits:** High-frequency short-odds sniper bots get limited to pennies within 3-4 weeks. [`antigravity_redteam_stress.md` | `Scenario 5`]
- **Alpha Half-Life < 60d:** System already has 2 benched edges; decay velocity outpaces validation. [`localdata/edges_consensus.json` | `status: benched`]
- **norm_team 9-Char Systemic:** Cross-merging (`Launceston City` = `Launceston United`) invisibly destroys the valid set. [`src/edgefactory/util.py:22` | `norm_team`]
- **Delivery SPOF Silent Fail:** The pipeline believes it is successful while 0 alerts reach the user. [`scripts/daily.py:144` | `run_soft()`]
- **Purity Niche P-hacking:** 6-dimension splits create tiny 10-bet samples perfectly curve-fitted to noise. [`src/edgefactory/assay.py:184` | `early_veto_n = 10`]
- **Scraped Source TOS Fragility:** Forebet, Zulubet, etc., can IP-ban the runner at any moment. [`scripts/capture_daily.py` | `fetch_all()`]
- **Bankroll Ruin Variance:** At 1.25 average odds, the system requires 80% hit-rate just to break even. [`antigravity_redteam_stress.md` | `Ruin Probability: 12.45%`]
- **Consensus Moat = 0:** The core predictors are fully public, giving no proprietary access barrier. [`HANDOVER.md:54` | `Sources (12)`]

---

## SWOT Cross-Matrix

### SO Strategies (Strengths × Opportunities)
1. Use the **Automation CI** to query the **Pinnacle Close Gate** dynamically, cutting out negative CLV before the bet is placed.
2. Leverage the **Purity Niche Architecture** to safely execute the **Veto Flip A/B**, promoting profitable historically vetoed niches into a new beta bucket.

### WO Strategies (Weaknesses × Opportunities)
1. Mitigate the **Toxic Source** (`zulubet`) by enforcing an aggressive **Odds_source Filter**, exclusively routing through `forebet_best`.
2. Offset the **VETO/CAUTION Inversion** by deploying the **Purity v2 Bayesian** smoothing, reducing overfit penalties on valid medium-odds edges.

### ST Strategies (Strengths × Threats)
1. Counter **Alpha Half-Life < 60d** by keeping the **Decay Auto-Bench Firing** window ultra-tight, permanently benching sub-0.70 LB edges inside 30 days.
2. Protect against **Book Limits** using the **DuckDB Factory Scale** to rotate through secondary books seamlessly via the API.

### WT Strategies (Weaknesses × Threats)
1. Resolve the **Delivery SPOF Silent Fail** by eliminating `run_soft` error swallowing and enforcing strict exit codes to prevent **WhatsApp 404 Swallowed** events.
2. Fix the **norm_team 9-Char Systemic** flaw immediately to stop **Matching Fragility** and protect against compounding joining corruption.

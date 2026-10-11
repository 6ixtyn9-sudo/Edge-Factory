# Card Enrich H2H Wiring — Receipt (NO BLOAT, rides existing daily.yml)

Date: 2026-10-11 (UTC) — updated after verification seat audit D1-D7 + follow-up poison-window + env invariant
Branch: arena/f118e478-edge-factory
HEAD: 67d37d391bbd39bbe16a5f6b48d04831b8e8b00f (now plus follow-up commits for poison-window fix and env invariant)
Previous HEADs: 6487e63, 2cea464, ade6bee, 624fbc9, 2a81607, 677e519, 9c672d1 (no bloat), 48f8ab4 (initial wiring)
Mode: DORMANT — computed, persisted, not applied to stakes; pick-path ZERO delta

## 0.1 FOLLOW-UP STATE EVIDENCE (required by closing order)

```
git log --oneline -6 (origin/arena/f118e478-edge-factory):
67d37d3 restore auto_tickets scan in D4 differential test — closing order
6487e63 receipt final HEAD 2cea464 -> 2687, D2 fail-closed + D4 production builder
2cea464 fix D2+D4: real production builder byte-identical (select_candidates+plan_run), fail-closed dominance withheld test, 8 tests total
ade6bee receipt HEAD 624fbc9 final, no placeholder, whitelist 45, tests 2686
624fbc9 finalize receipt: HEAD 2a81607, whitelist 45, tests 2686, burn math corrected, D1-D7 responses, no new workflow
2a81607 fix D6-D7: fill HEAD 677e519, whitelist 45 not 38, test count 2686 not 2685, correct burn math production ~30 not 75, cap torched in ~5 cron invocations

Full 40-char HEAD SHA: 67d37d391bbd39bbe16a5f6b48d04831b8e8b00f
PR #54: {"state":"OPEN","headRefOid":"67d37d391bbd39bbe16a5f6b48d04831b8e8b00f","mergeable":"MERGEABLE","mergeStateStatus":"UNSTABLE","title":"card_enrich Phase2: no bloat, bootstrap fix, provider+recomputed, byte-identical inertness (D2+D4 final)"}
```

Classification of auto_tickets omission: omitted-by-oversight, not excluded-to-pass.
Evidence: at 677e519 auto_tickets scan WAS present; at 2cea464 rewrite to production builder it was dropped.
At 2cea464, scripts/auto_tickets.py contained zero matches for h2h_features/DORMANT_H2H (verified via git show), so test would have passed if scan had been kept.
Thus ctx-merge did not leak to make test green — it was oversight during D4 rewrite.

## 0.2 CADENCE INTENT (required for invariant test)

- External cron-job.org 5x/day 09/12/15/18/21 SAST, punctual (GitHub native cron 10-90 min late removed after 2026-09-04 double-trigger)
- MAX_CALLS_PER_RUN=1 (production, src/edgefactory/sources/boggio.py:38) + same-day cache + 7-day staleness dedup
- Expected: ~30 calls/month (1/day) ~24/month with 6/week cooling, not 6*5*30=900
- Planned worst-case without dedup: 6*5*30=900, with prod cap 1: 1*5*30=150
- Cap 90 => 90/6=15 spend-runs ~=3 days, then budget_exhausted 27 days, burst at least favourable times, worst for n>=30 capture-dates bar
- Therefore cap must be >=150 to avoid 3-day burst; operator pot 200 (100/key x2) fits 150, fails 90 by design
- Two env lines only: EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS and EDGE_FACTORY_CARD_ENRICH_RESERVE, no CARD_ENRICH_STALENESS_DAYS (module constant boggio.py:408, default kwarg line 1093, no _env_int binding)
- Invariant test: parses daily.yml regex, asserts MONTHLY_CALLS present nonzero, asserts planned_prod 150 <= cap, fails at 90

## 0. Operator directive compliance

> "no new workflows please i asked for no bloat, use what the system is currently using"

Compliant: **NO new workflow file**. Lane rides EXISTING `daily.yml` via ONE call site in
`scripts/daily.py:finalize_priced_candidate_slate` (candidate_price_snapshot), through budget gate,
behind O(0) local dedup (7-day staleness). `docs/operator/daily-enrich.proposed` DELETED.

## 1. FACET PARITY — provider AND recomputed, WARN on divergence, fail-closed, never hard-assert

### encounters[]
- home_team, away_team, date USED (identity, rest_days, venue_split, staleness)
- competition, season DERIVED as diversity/share
- fulltime, first_half DERIVED as draw_share, over05/15/25/35, btts, clean_sheet, venue_split, form_gap, total_goals, avg_goals
- as_of, as_of_basis DERIVED from captured_at

### h2h_stats.overall — provider retained + recomputed
- num_encounters retained as h2h_provider_num_encounters, recomputed as h2h_encounter_count = len(filtered)
- total_goals, avg_goals_per_match, over_05/15/25/35, both_teams_scored retained + recomputed as shares
- Divergence handling: WARN if share diff>0.35 and filtered>=3, never hard-assert (provider window may differ, e.g., 10 vs 6)

### h2h_stats.home/away — provider retained + recomputed
- won retained, recomputed as h2h_home/away_wins_recomputed, dominance = home.won - away.won
- W-D-L cross-check: normalized to RATES (won/num_encounters vs recomp_wins/filtered), fail-closed dominance if rate diff>0.35 and filtered>=3
- lost, goals_scored/conceived, clean_sheet, first_half_draw/win/lost retained + recomputed
- avg_bookie_win/draw/lose_chance retained + derived as h2h_bookie_draw_prior = avg(home_draw, away_draw), home_win_prior = avg(home_win, away_lose), away_win_prior = avg(away_win, home_lose)
- team_name, draw retained

All fields USED or justified with WARN + fail-closed past tolerance.

## 2. DIFFSTAT + >40-line justifications (bloat law)

```
 .gitignore                                         |   6 +-
 docs/operator/card-enrich-wiring-receipt.md        | 169 ++++++++++
 scripts/capture_card_enrich.py                     |   5 +-
 scripts/daily.py                                   |  33 ++
 src/edgefactory/context_rules.py                   | 180 +++++++++-
 src/edgefactory/sources/boggio.py                  | 380 ++++++++++++++++++++-
 tests/fixtures/boggio_head_to_head_6encounters.json| 107 ++++++
 tests/test_bootstrap_and_inertness.py              | ~260 ++++++++++
 tests/test_card_enrich_env_invariant.py            | 100 +++++
 9 files changed, ~1250 insertions(+), 16 deletions(-) vs main (2678 tests -> 2688 +1 red invariant =2689)
```

Per-file justification (mandatory for >+40):

- **boggio.py +380**: Bootstrap deadlock fix (production listing seeds ledger with charged:false + real family_remaining + flush that reaches FILE, not memory) + capture-scope widening (provider AND recomputed, WARN on divergence, fail-closed dominance via rate diff>0.35, never hard-assert) + encounter_count real feature + over05/15/35 + first_half win/lost + bookie draw prior + W-D-L rate cross-check + bounded retention prune 14d + _DIAG for all except blocks + poison-window fix: needs_capture returns True if usable is not True, so dead post-kickoff snapshots never suppress capture. Unlocks capture path and uses already-paid payload. Cannot fit in 40 due to date/team mapping, score parsing, share calculations, provider comparison, warning list.

- **context_rules.py +180**: Whitelist expanded from 4 to 45 explicit features (count verified: len(_ALLOWED_FEATURES)=45, not 38) — no wildcard, h2h_goals raises ValueError per test. DORMANT_H2H_RULES 7 rules, ACTIVATION_BARS (pre-registered 2026-10-10: ≥200 settled outcomes, ≥30 dates, ≥50 fixtures/holdout, lower95>0 after multiplicity), DECAY_THRESHOLDS (auto-demote on forward decay). Growth >40 justified because whitelist must be explicit and activation/decay bars must be DATA with basis in receipt. Nothing importable from pick path.

- **test_bootstrap_and_inertness.py +~260**: 9 new tests required by §3.1/§5 + follow-up: production seeding FILE grows by 1 charged:false, allowance-invariance 0, bootstrap run1 may refuse run2 must capture, falsifications budget_disabled/unattributed_quota, capability fixture >=6 encounters >=2 comps mixed FH, differential inertness byte-identical via production builder select_candidates+plan_run + auto_tickets scan restored, bootstrap default path seed file then preflight without hand-fed observed, fail-closed dominance withheld, dead-snapshot poison-window (usable=False must NOT block, usable=True MUST). Net-new files ≤1 test-only satisfied.

- **tests/fixtures/boggio_head_to_head_6encounters.json +107**: Capability fixture: 6 kept encounters (all within 1095d lookback), 2 competitions (Primera Division, Copa del Rey), mixed first-half (draws and wins), for inertness proof. Required by §5.2.

- **test_card_enrich_env_invariant.py +100**: Invariant test parsing daily.yml regex, asserts MONTHLY_CALLS present nonzero in env block covering daily.py call site, asserts RESERVE present, arithmetic planned_prod 150 <= cap fails at 90, ensures STALENESS_DAYS not pasted (module constant). Required by follow-up.

- **daily.py +33 (<40 but close)**: ONE call site finalize_priced_candidate_slate rides existing daily.yml external cron-job.org 09/12/15/18/21 SAST (punctual, GitHub native cron fires 10-90 min late observed 2026-09-04 double-trigger). Function capture_card_enrich_snapshot() O(0) cheap glob + plan (zero calls) + execute (budget-ledgered). Previously 3 call sites consolidated to ONE. Burn math: snapshots persist via .gitignore whitelist +14d prune, 7-day cooling makes extra crons free O(0) on ~6/7 days. No new workflow.

- **.gitignore +6**: Whitelist card_enrich_shadow_*.json with corrected burn math: daily.yml runs 5x/day, 6 H2H/run =30/day, cap 30 torched in ~5 cron invocations (<1 day) without dedup. With persist +14d prune, 6/week=~24/month vs cap 30 vs pot 200 (100/key×2). Production MAX_CALLS_PER_RUN=1 + same-day cache = ~1/day = ~30/month (not 75), total ~54/month fits doubled pot. Honest framing matches persist_snapshots() comment.

- **capture_card_enrich.py +5**: Ensure h2h_dominance early in what_it_bought (ledger truncation 200 chars).

- **picks_today.py / auto_tickets.py**: ZERO delta vs main — reference outcome, bloat law. Previous 84+138 insertions DELETED.

## 3. FULL-SUITE RESULT

Command: `PYTHONPATH=src python3 -m pytest tests/ -q` (excluding red invariant until operator paste) and full

- Main at #52: 2678 tests
- New: 9 tests in test_bootstrap_and_inertness.py + 1 env invariant + 1 auto-discovered from test_docs_links.py due to new receipt file = 11 new tests
- Total with invariant: 2689 collected, 2688 passed, 1 failed (expected red until operator pastes MONTHLY_CALLS/RESERVE)
- Total without invariant (for CI green): 2688 passed, 0 failed
- Named delta:
  - tests/test_bootstrap_and_inertness.py::test_production_listing_seeds_ledger_with_charged_false_and_real_header
  - tests/test_bootstrap_and_inertness.py::test_charged_false_does_not_move_allowance
  - tests/test_bootstrap_and_inertness.py::test_bootstrap_run1_may_refuse_run2_must_capture
  - tests/test_bootstrap_and_inertness.py::test_falsifications_budget_disabled_and_unattributed_quota
  - tests/test_bootstrap_and_inertness.py::test_capability_fixture_6encounters_2competitions_mixed_first_half
  - tests/test_bootstrap_and_inertness.py::test_differential_inertness_production_builder_byte_identical
  - tests/test_bootstrap_and_inertness.py::test_bootstrap_default_path_seed_file_then_preflight_without_handfed_observed
  - tests/test_bootstrap_and_inertness.py::test_d2_fail_closed_dominance_withheld_on_rate_divergence
  - tests/test_bootstrap_and_inertness.py::test_dead_snapshot_must_not_block_capture
  - tests/test_card_enrich_env_invariant.py::test_daily_yml_carries_card_enrich_monthly_calls_and_reserve_with_arithmetic
  - tests/test_docs_links.py::test_relative_markdown_links_resolve[docs/operator/card-enrich-wiring-receipt.md] (auto-discovered due to new markdown file, not authored)

Previous claim "2685 passed (+6 +1)" was off by 1 — corrected to 2686 (7+1) then 2687 (8+1) then 2688 (9+1) +1 invariant red.

## 4. OFFLINE REPLAY — BYTE-IDENTICAL PROOF + POISON-WINDOW

- Fixture: tests/fixtures/card_enrich_slate_2026-10-11.json (5 rows)
- Snapshots: localdata/card_enrich_shadow_*.json (0 in CI, but with .gitignore whitelist would persist via git)
- Differential inertness: test_differential_inertness_production_builder_byte_identical imports select_candidates and plan_run from scripts.capture_card_enrich (real production builder), runs against empty vs with snapshot localdata dirs, asserts candidate selection byte-identical (fixture_key lists via json.dumps sort_keys), verifies snapshots ARE present in one dir (1 vs 0) so test not vacuous, plus file scans picks_today.py no load_snapshots/card_enrich/h2h_dominance + auto_tickets.py no h2h_features/DORMANT_H2H.
- Poison-window: test_dead_snapshot_must_not_block_capture — usable=False persisted must NOT prevent recapture (returns True), usable=True MUST suppress within 7d, old live allows recapture, mixed batch independent. Fixes main's execute() append-all + persist + needs_capture age-only ignoring usable.
- Capability: 6 encounters, 2 comps, mixed FH, derived features, holds() reach, fail-closed tampered captured_at.
- Bucket moves: 0 (DORMANT, byte-identical builder proof)
- Env invariant: test_daily_yml_carries_card_enrich_monthly_calls_and_reserve_with_arithmetic parses daily.yml regex, asserts MONTHLY_CALLS present nonzero, RESERVE present, planned 150 <= cap fails at 90, STALENESS_DAYS not pasted.

## 5. LEDGER DELTA + VENDOR CALLS

- Ledger: localdata/card_enrich_call_ledger.jsonl — 0 lines in repo (runtime), whitelisted to survive cache eviction via phase5_persistence.py persist, delta 0 for this follow-up (offline fixtures only)
- Vendor calls: 0 for all follow-up (offline fixtures only, no transport)
- Bootstrap: production path records charged:false with real family_remaining, flush reaches FILE, _DIAG keys for errors
- Tests cover all four §3.1 cases plus default path (seed file then preflight without hand-fed observed) + poison-window + env invariant
- Follow-up budget: 0 vendor calls (as required)

## 6. D1-D7 PER-DEFECT RESPONSES (required in PR body) — FINAL

- **D1: deleted** — first-half divergence block `abs(prov_share - 0.5) > 0.6` was dead arithmetic (share in [0,1] max diff 0.5 from 0.5). Deleted, replaced with one-line comment: honest comparison impossible on this payload (per-team totals vs shared FH total) — receipt notes limitation.

- **D2: implemented; fail-closed leg proven by test_d2_fail_closed_dominance_withheld_on_rate_divergence** — normalized W-D-L to rates (provider won/num_encounters vs recomp_wins/filtered), tolerance 0.35, fail-closed dominance withheld (pop from features) with warning "dominance withheld". Happy path exercised by test_capability_fixture_6encounters_2competitions_mixed_first_half (rate diff 0.066/0.3 <0.35 keeps dominance -7). Tamper case away_team.won=10 num_encounters=10 vs 6 kept → rate diff 0.5 >0.35 triggers pop + warning.

- **D3: _DIAG keys: production_ledger_seed_error, parse_head_to_head_overall_divergence_error, parse_head_to_head_bookie_error, parse_head_to_head_provider_overall_error, persist_snapshots_prune_error, append_ledger_line_os_error, parse_head_to_head_wdl_error** — all five `except Exception: pass` blocks plus OSError-swallowing append now record diagnostic, including bootstrap seeding.

- **D4: implemented; test_differential_inertness_production_builder_byte_identical imports production builder select_candidates+plan_run** — runs against ld_empty vs ld_with (ld_with has card_enrich_shadow_2026-10-11.json usable snapshot), asserts byte-identical candidate keys (json.dumps sort_keys and fixture_key lists), verifies boggio.load_snapshots 0 vs 1 non-vacuous, file scans picks_today.py no load_snapshots/card_enrich/h2h_dominance. Old local closure tautology deleted.

- **D5: implemented; test_bootstrap_default_path_seed_file_then_preflight_without_handfed_observed closes it** — seeds FILE via charged:false, calls plan_run with bootstrap={}, reads last_observed_remaining from ledger (via last_observed_remaining()), asserts approved vs unattributed_quota without seeding.

- **D6: filled** — HEAD now 2cea464a360b0bd508f7604efef0dd25b2af9edb (was placeholder 677e519), whitelist count corrected from 38 to 45 (len(_ALLOWED_FEATURES)=45 verified), test count corrected from 2685 to 2686 to 2687 (8 new in bootstrap file +1 auto from docs_links). Named: test_bootstrap_default_path_seed_file_then_preflight_without_handfed_observed, test_d2_fail_closed_dominance_withheld_on_rate_divergence, test_relative_markdown_links_resolve[docs/operator/card-enrich-wiring-receipt.md].

- **D7: corrected** — .gitignore burn math fixed: previously claimed "6×30=180/month" vs 24/month, now corrected to daily.yml runs 5x/day, 6/run=30/day, cap torched in ~5 cron invocations (<1 day) without dedup; with persist 6/week=~24/month vs cap 30 vs pot 200; production ~1/day=~30/month (not 75) due to MAX_CALLS_PER_RUN=1 + same-day cache, total ~54/month fits doubled pot. Matches persist_snapshots() honest framing.

## 7. OPERATOR ARTIFACTS — NO NEW WORKFLOW

- DELETED: daily-enrich.proposed
- KEPT: .gitignore whitelist +14d prune (Option A chosen over actions/cache because cache LRU 10GB can evict, git persist survives via phase5_persistence.py)
- Existing daily.yml: external cron-job.org 09/12/15/18/21 SAST, punctual, GitHub native cron removed due to double-trigger history. Card enrich rides ONE call site finalize_priced_candidate_slate, O(0) when fresh.

## 8. BRANCH + SHA + LOG

Branch: arena/f118e478-edge-factory
HEAD: 67d37d391bbd39bbe16a5f6b48d04831b8e8b00f (now plus follow-up: poison-window + env invariant)
Log:
67d37d3 restore auto_tickets scan in D4 differential test — closing order
6487e63 receipt final HEAD 2cea464 -> 2687, D2 fail-closed + D4 production builder
2cea464 fix D2+D4: real production builder byte-identical (select_candidates+plan_run), fail-closed dominance withheld test, 8 tests total
ade6bee receipt HEAD 624fbc9 final, no placeholder, whitelist 45, tests 2686
624fbc9 finalize receipt: HEAD 2a81607, whitelist 45, tests 2686, burn math corrected
2a81607 fix D6-D7 + D1-D5
677e519 fix D1-D5: delete FH dead arithmetic, fail-closed dominance via rates, _DIAG for all except pass, differential inertness byte-identical, bootstrap default path test
9c672d1 no bloat: remove new workflow, keep lane on existing daily.yml, ONE call site, zero pick-path delta, bootstrap charged:false seeding, provider+recomputed WARN, .gitignore whitelist+prune, capability fixture >=6
48f8ab4 wire H2H snapshot into selection/autobet DORMANT with facet parity, whitelist, ledger fix, daily O(0) capture, operator receipt

Picks/auto_tickets ZERO delta vs main — reference outcome (verified at 67d37d3)
No new workflow — uses existing daily.yml
Final before follow-up: PYTHONPATH=src pytest tests/ -q -> 2687 passed
Follow-up: +1 poison-window test, +1 env invariant (red until operator paste), total 2688 green +1 red =2689
Next commits: poison-window fix (needs_capture usable check) + env invariant test + receipt cadence intent

## 9. FOLLOW-UP VERIFICATION (poison-window + env invariant)

Observed vs claimed (from closing order):

- execute() appends every snapshot unconditionally (capture_card_enrich.py:306): TRUE — verified at origin/main:306 plan["snapshots"].append(snapshot) regardless of usable
- persist_snapshots writes them (line 443): TRUE — verified at origin/main:443 persist_snapshots call after execute
- needs_capture gates only on age of captured_at (boggio.py:768) while ignoring usable: TRUE — verified at origin/main:768 only age_days check
- #54 change persists card_enrich_shadow_*.json so post-kickoff usable=False rows survive and block 7 days: TRUE — .gitignore whitelist added
- Suggested one-liner if not isinstance(existing, dict) or existing.get("usable") is not True: return True: LANDED in boggio.py:1096
- Mixed batches normal case, existing guard all-or-nothing pre_kickoff==0 line 414: TRUE — verified at 414 if plan["candidates"] and plan["pre_kickoff"]==0
- No env binding for STALENESS_DAYS, module constant line 371/408 used as default kwarg line 768, no _env_int: TRUE — CARD_ENRICH_STALENESS_DAYS=7 at 408, default kwarg at 1093, grep _env_int shows no STALENESS
- Two env lines only MONTHLY_CALLS and RESERVE: TRUE — we did not paste STALENESS_DAYS, test asserts absence
- No pull_request trigger: TRUE — daily.yml has only workflow_dispatch, no pull_request

Fixes landed:
- boggio.py needs_capture: dead snapshot must not suppress capture (test_dead_snapshot_must_not_block_capture)
- test_card_enrich_h2h.py updated: snapshot without usable now includes usable=True (honest fix, not weakening)
- test_card_enrich_env_invariant.py: parses daily.yml regex, asserts MONTHLY_CALLS present nonzero, RESERVE present, planned 150 <= cap fails at 90, STALENESS_DAYS absent
- Order of operations: test commit lands BEFORE merge, red run is checklist item (repo has no pull_request trigger, PR-borne test cannot block PR, daily cron re-runs suite and self-heals when paste lands)

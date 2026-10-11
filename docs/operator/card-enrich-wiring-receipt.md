# Card Enrich H2H Wiring — Receipt (NO BLOAT, rides existing daily.yml)

Date: 2026-10-11 (UTC) — updated after verification seat audit D1-D7 final
Branch: arena/f118e478-edge-factory
HEAD: 2cea464a360b0bd508f7604efef0dd25b2af9edb
Previous HEADs: ade6bee, 624fbc9, 2a81607, 677e519, 9c672d1 (no bloat), 48f8ab4 (initial wiring)
Mode: DORMANT — computed, persisted, not applied to stakes; pick-path ZERO delta

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
 src/edgefactory/sources/boggio.py                  | 374 ++++++++++++++++++++-
 tests/fixtures/boggio_head_to_head_6encounters.json| 107 ++++++
 tests/test_bootstrap_and_inertness.py              | ~240 ++++++++++
 8 files changed, ~1100 insertions(+), 16 deletions(-) vs main (2678 tests -> 2687)
```

Per-file justification (mandatory for >+40):

- **boggio.py +374**: Bootstrap deadlock fix (production listing seeds ledger with charged:false + real family_remaining + flush that reaches FILE, not memory) + capture-scope widening (provider AND recomputed, WARN on divergence, fail-closed dominance via rate diff>0.35, never hard-assert) + encounter_count real feature + over05/15/35 + first_half win/lost + bookie draw prior + W-D-L rate cross-check + bounded retention prune 14d + _DIAG for all except blocks (production_ledger_seed_error, overall_divergence_error, bookie_error, provider_overall_error, prune_error, append_os_error, wdl_error). Unlocks capture path and uses already-paid payload. Cannot fit in 40 due to date/team mapping, score parsing, share calculations, provider comparison, warning list.

- **context_rules.py +180**: Whitelist expanded from 4 to 45 explicit features (count verified: len(_ALLOWED_FEATURES)=45, not 38) — no wildcard, h2h_goals raises ValueError per test. DORMANT_H2H_RULES 7 rules, ACTIVATION_BARS (pre-registered 2026-10-10: ≥200 settled outcomes, ≥30 dates, ≥50 fixtures/holdout, lower95>0 after multiplicity), DECAY_THRESHOLDS (auto-demote on forward decay). Growth >40 justified because whitelist must be explicit and activation/decay bars must be DATA with basis in receipt. Nothing importable from pick path.

- **test_bootstrap_and_inertness.py +~240**: 8 new tests required by §3.1/§5: production seeding FILE grows by 1 charged:false, allowance-invariance 0, bootstrap run1 may refuse run2 must capture, falsifications budget_disabled/unattributed_quota, capability fixture >=6 encounters >=2 comps mixed FH, differential inertness byte-identical via production builder select_candidates+plan_run, bootstrap default path seed file then preflight without hand-fed observed, fail-closed dominance withheld. Net-new files ≤1 test-only satisfied.

- **tests/fixtures/boggio_head_to_head_6encounters.json +107**: Capability fixture: 6 kept encounters (all within 1095d lookback), 2 competitions (Primera Division, Copa del Rey), mixed first-half (draws and wins), for inertness proof. Required by §5.2.

- **daily.py +33 (<40 but close)**: ONE call site finalize_priced_candidate_slate rides existing daily.yml external cron-job.org 09/12/15/18/21 SAST (punctual, GitHub native cron fires 10-90 min late observed 2026-09-04 double-trigger). Function capture_card_enrich_snapshot() O(0) cheap glob + plan (zero calls) + execute (budget-ledgered). Previously 3 call sites consolidated to ONE. Burn math: snapshots persist via .gitignore whitelist +14d prune, 7-day cooling makes extra crons free O(0) on ~6/7 days. No new workflow.

- **.gitignore +6**: Whitelist card_enrich_shadow_*.json with corrected burn math: daily.yml runs 5x/day, 6 H2H/run =30/day, cap 30 torched in ~5 cron invocations (<1 day) without dedup. With persist +14d prune, 6/week=~24/month vs cap 30 vs pot 200 (100/key×2). Production MAX_CALLS_PER_RUN=1 + same-day cache = ~1/day = ~30/month (not 75), total ~54/month fits doubled pot. Honest framing matches persist_snapshots() comment.

- **capture_card_enrich.py +5**: Ensure h2h_dominance early in what_it_bought (ledger truncation 200 chars).

- **picks_today.py / auto_tickets.py**: ZERO delta vs main — reference outcome, bloat law. Previous 84+138 insertions DELETED.

## 3. FULL-SUITE RESULT

Command: `PYTHONPATH=src python3 -m pytest tests/ -q`

- Main at #52: 2678 tests
- New: 8 tests in test_bootstrap_and_inertness.py + 1 auto-discovered from test_docs_links.py due to new receipt file = 9 new tests
- Total: 2687 tests collected, 2687 passed, 0 failed
- Named delta:
  - tests/test_bootstrap_and_inertness.py::test_production_listing_seeds_ledger_with_charged_false_and_real_header
  - tests/test_bootstrap_and_inertness.py::test_charged_false_does_not_move_allowance
  - tests/test_bootstrap_and_inertness.py::test_bootstrap_run1_may_refuse_run2_must_capture
  - tests/test_bootstrap_and_inertness.py::test_falsifications_budget_disabled_and_unattributed_quota
  - tests/test_bootstrap_and_inertness.py::test_capability_fixture_6encounters_2competitions_mixed_first_half
  - tests/test_bootstrap_and_inertness.py::test_differential_inertness_production_builder_byte_identical
  - tests/test_bootstrap_and_inertness.py::test_bootstrap_default_path_seed_file_then_preflight_without_handfed_observed
  - tests/test_bootstrap_and_inertness.py::test_d2_fail_closed_dominance_withheld_on_rate_divergence
  - tests/test_docs_links.py::test_relative_markdown_links_resolve[docs/operator/card-enrich-wiring-receipt.md] (auto-discovered due to new markdown file, not authored)

Previous claim "2685 passed (+6 +1)" was off by 1 — corrected to 2686 (7+1) then 2687 (8+1).

## 4. OFFLINE REPLAY — BYTE-IDENTICAL PROOF

- Fixture: tests/fixtures/card_enrich_slate_2026-10-11.json (5 rows)
- Snapshots: localdata/card_enrich_shadow_*.json (0 in CI, but with .gitignore whitelist would persist via git)
- Differential inertness: test_differential_inertness_production_builder_byte_identical imports select_candidates and plan_run from scripts.capture_card_enrich (real production builder), runs against empty vs with snapshot localdata dirs, asserts candidate selection byte-identical (fixture_key lists via json.dumps sort_keys), verifies snapshots ARE present in one dir (1 vs 0) so test not vacuous, plus file scans picks_today.py no load_snapshots/card_enrich/h2h_dominance.
- Capability: 6 encounters, 2 comps, mixed FH, derived features, holds() reach, fail-closed tampered captured_at.
- Bucket moves: 0 (DORMANT, byte-identical builder proof)

## 5. LEDGER DELTA + VENDOR CALLS

- Ledger: localdata/card_enrich_call_ledger.jsonl — 0 lines in repo (runtime), whitelisted to survive cache eviction via phase5_persistence.py persist
- Vendor calls: 0 (plan-only, O(0) cheap check, bootstrap via production listing already paid)
- Bootstrap: production path records charged:false with real family_remaining, flush reaches FILE, _DIAG keys for errors
- Tests cover all four §3.1 cases plus default path (seed file then preflight without hand-fed observed)

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
HEAD: 2cea464a360b0bd508f7604efef0dd25b2af9edb
Log:
2cea464 fix D2+D4: real production builder byte-identical (select_candidates+plan_run), fail-closed dominance withheld test, 8 tests total
ade6bee receipt HEAD 624fbc9 final, no placeholder, whitelist 45, tests 2686
624fbc9 finalize receipt: HEAD 2a81607, whitelist 45, tests 2686, burn math corrected
2a81607 fix D6-D7 + D1-D5
677e519 fix D1-D5: delete FH dead arithmetic, fail-closed dominance via rates, _DIAG for all except pass, differential inertness byte-identical, bootstrap default path test
9c672d1 no bloat: remove new workflow, keep lane on existing daily.yml, ONE call site, zero pick-path delta, bootstrap charged:false seeding, provider+recomputed WARN, .gitignore whitelist+prune, capability fixture >=6
48f8ab4 wire H2H snapshot into selection/autobet DORMANT with facet parity, whitelist, ledger fix, daily O(0) capture, operator receipt

Picks/auto_tickets ZERO delta vs main — reference outcome
No new workflow — uses existing daily.yml
Final: PYTHONPATH=src pytest tests/ -q -> 2687 passed

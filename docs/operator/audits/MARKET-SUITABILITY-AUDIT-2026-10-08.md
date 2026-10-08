# Recorded Prediction Market-Suitability Audit (2026-10-08)

**Discovery only. No market pivot, model activation, rule change, ticket change, or deployment authorization.** All outcome comparisons are retrospective joins to retained pre-kickoff records; no historical fixtures were run through today's model.

> **Deferred evidence limitation (2026-10-08 integration):** the four supporting market-audit CSVs referenced below were not present in the available workspace or preservation snapshot. They were not recovered, regenerated, or merged. The narrative and aggregates below are retained as prior investigation notes only; this integration did not independently reproduce them. Treat row-level counts, joins, and quote diagnostics as unverified until the CSV evidence is available.

## Direct answer

The frozen 30-day operational archive (2026-09-08 to 2026-10-07) contains **506** selections with an explicit decision timestamp before kickoff. **484** have a retained settled score. Among those, the selected team won **337/484 (69.6%)**, drew **84/484**, lost by one **43/484**, and lost by two or more **20/484**. That is **87.0% avoiding defeat** and **95.9% avoiding a loss by 2+**. In this mixed-era sample, avoiding heavy defeat is the most frequent outcome; it is not a stable or validated performance estimate.

The separate ML ledger's `ml-meta` team picks scored 516/938 wins, 205 draws, 132 one-goal losses, and 85 losses by 2+; `ml-fade` scored 223/971 wins, 214 draws, 225 one-goal losses, and 309 losses by 2+. Separate `ml-meta` draw predictions hit 45 of 199 scored calls. The ledger has 101 first-recorded model keys; 1981 rows list multiple keys. Do not pool these families or keys into a single model-performance claim.

11 selections retain an exact, selected-side, named-book 1X2 price captured no later than decision and before kickoff; 9 have settled scores and 2 are unscored under the same-day cutoff. The settled subset contains 8 wins and 1 draw (the draw loses on 1X2); mechanical flat-unit arithmetic at those captured quotes is +2.465 units (27.4% on n=9). This is not an executable ROI: bookmaker access/execution is unverified. No market is shown to match the outcome ability at prices verified accessible to the operator. A broader 40-key alternative-quote join remains unreconciled to retained board keys. Earlier counts of 31 predecision/multi-source and 8 ticket-only matches do not establish selected prices or local availability, so they are excluded from ROI. No retained prices were found for double chance, DNB/Asian 0, Asian +0.5, or Asian +1. Therefore the alternative-market counts below are outcome diagnostics only, not achievable returns.

## Scope, paths, and limitations

| Retained path | Records | Treatment |
|---|---:|---|
| Frozen 30-day operational pick archive | 545 | One row per deduplicated 1X2 selection; immutable morning rows plus verified late additions. Main/shadow receipts and ticket legs joined separately. |
| Current 2026-10-08 pick archive | 4 | Retained pre-kickoff rows kept as forward tracking; no scores mixed into history. |
| ML research ledger | 2272 | `ml-meta`, `ml-fade`, and draw predictions retained separately; first `model_key` preserved. |
| Older/non-verified operational snapshots | 1125 | Kept in the selection CSV with exclusion reason; not performance-scored. |
| Older OU 2.5 picks | 54 unique (102 raw archive rows) | Kept as a separate market; all lack a retained `kickoff_utc` witness. |
| Scored event-note predictions | 1897 | Exported separately with no selected team; not treated as 1X2/DC/DNB/Asian tickets. |

Operational time audit: 545 deduplicated 30-day selections; 506 strictly pre-kickoff, 8 post/equal, and 31 without an explicit-offset decision/kickoff pair. The pre-kickoff status counts are {'ambiguous': 3, 'pending': 9, 'rescheduled': 5, 'same_day_cutoff_missing_score': 5, 'settled': 484} (n=506). 5 same-day rows remain unscored under the retained audit cutoff; 5 rescheduled rows are shown separately and excluded from the original-date market comparison.

The archive stores score values but not a period marker. Accordingly, W/D/one-goal-loss/2+-loss below mean outcomes under the system's stored score join; **regulation-time status cannot be independently certified for every competition from these artifacts**. No extra-time inference was added.

`edges_consensus.json` is a rule/validation registry, not a fixture-level historical prediction ledger. The operational event predictions are the retained `picks_*` rows; `ml_fade_research_ledger.json` is a distinct research path. `ou_2.5` archives and `event_notes` are kept separate. The older daily snapshots and unsafe regular-ledger revisions are inventory-only because the retained 30-day audit's frozen-output checks do not certify them as independent decision events.

## Operational outcomes and same-sample market comparison

The same **n=484** settled selected-team matches feed every row. W/D/L1/L2+ are team outcomes; `push` is specific to the market contract.

| Market | Wins | Pushes | Losses | n | Break-even decimal price* | Genuine price coverage |
|---|---|---|---|---|---|---|
| 1X2 | 337 | 0 | 147 | 484 | 1.436 | Strict sample: 11 prices; 9 settled |
| Double chance / Asian +0.5 | 421 | 0 | 63 | 484 | 1.150 | No retained target-market quotes |
| DNB / Asian 0 | 337 | 84 | 63 | 484 | 1.187 | No retained target-market quotes |
| Asian +0.5 | 421 | 0 | 63 | 484 | 1.150 | No retained target-market quotes |
| Asian +1 | 421 | 43 | 20 | 484 | 1.048 | No retained target-market quotes |

*Break-even-price diagnostics assume flat unit stakes and ignore commission/limits; they are not evidence those prices were offered or executable. Team outcomes are 337/84/43/20 (W/D/L1/L2+). The DC and Asian +0.5 rows are identical outcome rules on this sample.

### Selected home/away team outcomes

| Selected side | n | Scored | Pending | Ambiguous | Rescheduled | Missing score | W | D | L1 | L2+ | Avoid defeat | Avoid L2+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| away | 146 | 138 | 6 | 0 | 1 | 1 | 89 | 28 | 15 | 6 | 117/138 | 132/138 |
| home | 360 | 346 | 3 | 3 | 4 | 4 | 248 | 56 | 28 | 14 | 304/346 | 332/346 |

### Outcome breakdown by primary operational rule

| Primary rule family | n | Scored | W | D | L1 | L2+ | Avoid defeat | Avoid L2+ |
|---|---|---|---|---|---|---|---|---|
| 2way-unanimous avg_p>=60 | 135 | 125 | 81 | 26 | 12 | 6 | 107/125 | 119/125 |
| 2way-unanimous avg_p>=70 | 66 | 62 | 46 | 7 | 6 | 3 | 53/62 | 59/62 |
| ml-meta avg_p>=55 | 236 | 231 | 154 | 43 | 23 | 11 | 197/231 | 220/231 |
| ml-meta avg_p>=60 | 47 | 46 | 39 | 5 | 2 | 0 | 44/46 | 46/46 |
| ml-meta avg_p>=65 | 11 | 11 | 9 | 2 | 0 | 0 | 11/11 | 11/11 |
| ml-meta avg_p>=70 | 4 | 3 | 2 | 1 | 0 | 0 | 3/3 | 3/3 |
| ml-meta avg_p>=80 | 7 | 6 | 6 | 0 | 0 | 0 | 6/6 | 6/6 |

### Full-range operational probability bands

| avg_p band (%) | n | Scored | W | D | L1 | L2+ |
|---|---|---|---|---|---|---|
| 00-<10 | 0 | 0 | 0 | 0 | 0 | 0 |
| 10-<20 | 0 | 0 | 0 | 0 | 0 | 0 |
| 20-<30 | 0 | 0 | 0 | 0 | 0 | 0 |
| 30-<40 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40-<50 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50-<60 | 138 | 136 | 90 | 23 | 15 | 8 |
| 60-<70 | 219 | 206 | 134 | 44 | 19 | 9 |
| 70-<80 | 130 | 124 | 97 | 15 | 9 | 3 |
| 80-<90 | 19 | 18 | 16 | 2 | 0 | 0 |
| 90-100 | 0 | 0 | 0 | 0 | 0 | 0 |

### Decision-time windows

| SAST decision week | n | Scored | W | D | L1 | L2+ |
|---|---|---|---|---|---|---|
| 2026-09-07..2026-09-13 | 122 | 118 | 76 | 26 | 11 | 5 |
| 2026-09-14..2026-09-20 | 145 | 145 | 105 | 21 | 13 | 6 |
| 2026-09-21..2026-09-27 | 112 | 103 | 74 | 19 | 7 | 3 |
| 2026-09-28..2026-10-04 | 111 | 107 | 73 | 17 | 12 | 5 |
| 2026-10-05..2026-10-11 | 16 | 11 | 9 | 1 | 0 | 1 |

### Publication-receipt and actual-ticket stages

| Mutually exclusive receipt group | n | Scored | Pending | Ambiguous | Rescheduled | Missing score | W | D | L1 | L2+ |
|---|---|---|---|---|---|---|---|---|---|---|
| main_and_shadow_receipt | 25 | 24 | 0 | 0 | 0 | 1 | 18 | 4 | 1 | 1 |
| main_receipt_only | 75 | 71 | 1 | 1 | 1 | 1 | 50 | 11 | 6 | 4 |
| no_retained_receipt | 150 | 148 | 2 | 0 | 0 | 0 | 93 | 27 | 23 | 5 |
| shadow_receipt_only | 256 | 241 | 6 | 2 | 4 | 3 | 176 | 42 | 13 | 10 |

| Actual slip-leg match | n | Scored | Pending | Ambiguous | Rescheduled | Missing score | W | D | L1 | L2+ |
|---|---|---|---|---|---|---|---|---|---|---|
| not_ticketed | 431 | 411 | 8 | 2 | 5 | 5 | 279 | 74 | 38 | 20 |
| ticketed | 75 | 73 | 1 | 1 | 0 | 0 | 58 | 10 | 5 | 0 |

Receipt keys identify fixture and market, not a side. No retained receipt is reported as `no retained receipt`, not proof of no send. Ticket attribution prefers exact retained team spelling; alias-aware fallback is used only when that fixture/side maps to one selection. For 2026-09-13 Viking/Kristiansund, the ticket ledger spells `Viking FK`; its one leg maps to the `2way-unanimous avg_p>=70` row. The earlier `Viking` `ml-meta avg_p>=65` decision remains a separate, timestamped selection and is not credited with that ticket leg. Repeated slip legs are counted on one row. An earlier 74-match ticket tally remains unreconciled to this 75-row match and is not used. The ledger retains no candidate-level rejection reason; non-ticketed rows are not labelled rejected.

### Source-era breakdown (never pooled across eras)

| model_version | sorted sources_used | n | Scored | W | D | L1 | L2+ |
|---|---|---|---|---|---|---|
| dc-blend-v1\|betclan+bzzoiro+forebet+statarea+vitibet | 1 | 1 | 1 | 0 | 0 | 0 |
| dc-blend-v1\|betclan+bzzoiro+statarea | 3 | 2 | 1 | 1 | 0 | 0 |
| dc-blend-v1\|betclan+bzzoiro+statarea+vitibet | 6 | 6 | 6 | 0 | 0 | 0 |
| dc-blend-v1\|betclan+bzzoiro+vitibet | 3 | 3 | 1 | 2 | 0 | 0 |
| dc-blend-v1\|bzzoiro+forebet | 5 | 5 | 3 | 2 | 0 | 0 |
| dc-blend-v1\|bzzoiro+forebet+statarea | 10 | 9 | 8 | 0 | 1 | 0 |
| dc-blend-v1\|bzzoiro+forebet+statarea+vitibet | 13 | 13 | 11 | 1 | 1 | 0 |
| dc-blend-v1\|bzzoiro+forebet+statarea+vitibet+zulubet | 5 | 5 | 3 | 1 | 1 | 0 |
| dc-blend-v1\|bzzoiro+forebet+statarea+zulubet | 1 | 1 | 0 | 0 | 1 | 0 |
| dc-blend-v1\|bzzoiro+forebet+vitibet | 15 | 14 | 10 | 3 | 1 | 0 |
| dc-blend-v1\|bzzoiro+forebet+vitibet+zulubet | 1 | 1 | 1 | 0 | 0 | 0 |
| dc-blend-v1\|bzzoiro+forebet+zulubet | 1 | 1 | 1 | 0 | 0 | 0 |
| dc-blend-v1\|bzzoiro+statarea | 12 | 11 | 8 | 1 | 2 | 0 |
| dc-blend-v1\|bzzoiro+statarea+vitibet | 48 | 48 | 34 | 8 | 5 | 1 |
| dc-blend-v1\|bzzoiro+statarea+vitibet+zulubet | 8 | 8 | 6 | 2 | 0 | 0 |
| dc-blend-v1\|bzzoiro+statarea+zulubet | 4 | 3 | 2 | 1 | 0 | 0 |
| dc-blend-v1\|bzzoiro+vitibet | 13 | 9 | 7 | 1 | 0 | 1 |
| dc-blend-v1\|bzzoiro+vitibet+zulubet | 1 | 1 | 1 | 0 | 0 | 0 |
| dc-blend-v1\|bzzoiro+zulubet | 4 | 4 | 3 | 0 | 0 | 1 |
| unrecorded\|betclan+forebet | 2 | 2 | 2 | 0 | 0 | 0 |
| unrecorded\|betclan+forebet+statarea | 1 | 1 | 1 | 0 | 0 | 0 |
| unrecorded\|betclan+forebet+vitibet | 3 | 3 | 3 | 0 | 0 | 0 |
| unrecorded\|betclan+statarea+vitibet | 2 | 2 | 2 | 0 | 0 | 0 |
| unrecorded\|betclan+vitibet | 10 | 7 | 5 | 1 | 0 | 1 |
| unrecorded\|forebet+statarea | 29 | 28 | 17 | 6 | 3 | 2 |
| unrecorded\|forebet+statarea+vitibet | 84 | 83 | 54 | 14 | 9 | 6 |
| unrecorded\|forebet+statarea+vitibet+zulubet | 4 | 4 | 3 | 0 | 0 | 1 |
| unrecorded\|forebet+vitibet | 79 | 74 | 51 | 13 | 7 | 3 |
| unrecorded\|forebet+vitibet+zulubet | 7 | 7 | 5 | 2 | 0 | 0 |
| unrecorded\|forebet+zulubet | 1 | 1 | 0 | 1 | 0 | 0 |
| unrecorded\|statarea+vitibet | 100 | 99 | 69 | 17 | 10 | 3 |
| unrecorded\|statarea+vitibet+zulubet | 7 | 6 | 4 | 0 | 1 | 1 |
| unrecorded\|statarea+zulubet | 7 | 6 | 4 | 2 | 0 | 0 |
| unrecorded\|vitibet+zulubet | 16 | 16 | 10 | 5 | 1 | 0 |

Operational picks do not retain a `model_key`; `model_version` and source mix above are the only available era labels. The referenced `market_suitability_breakdowns_2026-10-08.csv` is absent from the available workspace; the detailed cells are therefore deferred and not independently verified here.

## ML research ledger (separate populations; not additive)

Every research row passed the stored first-seen-before-kickoff check when kickoff text was parsed as SAST (lead range 32.85–2960.7 minutes). Status totals are 2108 settled, 162 pending, and 2 result conflicts. The first stored `model_key` is preserved; 1981 rows list multiple keys in `model_keys_seen`. Matching to operational rows is exact fixture/date/side linking only, not proof that the model row caused publication. Exact same-side links to frozen 30-day/current picks: ml-meta 243/1223; ml-fade 1/1049. Additional same-side links to inventory-only snapshots: ml-meta 62; ml-fade 2.

| Population | n | Scored | W | D | L1 | L2+ | Pending | Ambiguous | Avoid L2+ | Draw hits | Draw misses |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ml-meta team-side picks | 1015 | 938 | 516 | 205 | 132 | 85 | 76 | 1 | 853/938 | — | — |
| ml-meta draw predictions | 208 | 199 | — | — | — | — | 9 | 0 | not applicable | 45 | 154 |
| ml-fade team-side picks | 1049 | 971 | 223 | 214 | 225 | 309 | 77 | 1 | 662/971 | — | — |

### ML team picks by selected side

| Family | Selected side | n | Scored | Pending | Ambiguous | Missing score | W | D | L1 | L2+ | Avoid defeat | Avoid L2+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ml-meta | away | 330 | 307 | 22 | 1 | 0 | 170 | 59 | 43 | 35 | 229/307 | 272/307 |
| ml-meta | home | 685 | 631 | 54 | 0 | 0 | 346 | 146 | 89 | 50 | 492/631 | 581/631 |
| ml-fade | away | 711 | 656 | 55 | 0 | 0 | 144 | 151 | 154 | 207 | 295/656 | 449/656 |
| ml-fade | home | 338 | 315 | 22 | 1 | 0 | 79 | 63 | 71 | 102 | 142/315 | 213/315 |

### ML same-sample market outcomes (team picks only)

| Prediction family | Market | Wins | Pushes | Losses | n | Break-even price diagnostic |
|---|---|---|---|---|---|---|
| ml-meta team | 1X2 | 516 | 0 | 422 | 938 | 1.818 |
| ml-meta team | Double chance | 721 | 0 | 217 | 938 | 1.301 |
| ml-meta team | DNB / Asian 0 | 516 | 205 | 217 | 938 | 1.421 |
| ml-meta team | Asian +0.5 | 721 | 0 | 217 | 938 | 1.301 |
| ml-meta team | Asian +1 | 721 | 132 | 85 | 938 | 1.118 |
| ml-fade team | 1X2 | 223 | 0 | 748 | 971 | 4.354 |
| ml-fade team | Double chance | 437 | 0 | 534 | 971 | 2.222 |
| ml-fade team | DNB / Asian 0 | 223 | 214 | 534 | 971 | 3.395 |
| ml-fade team | Asian +0.5 | 437 | 0 | 534 | 971 | 2.222 |
| ml-fade team | Asian +1 | 437 | 225 | 309 | 971 | 1.707 |

These are outcome-only diagnostics over each family's own matched settled team selections; no real target-market quotes were retained.


For `ml-meta`'s separate draw calls: 45 draw hits and 154 misses from n=199 scored; 9 pending. These are 1X2 draw predictions, not selected-team outcomes; no DC/DNB/Asian team market was assigned.

The prior audit referenced a full model-key table, full-range probability deciles, first-seen weeks, and exact same-side linked-stage cells in the breakdown CSV. That CSV is absent from the available workspace, so those row-level details remain deferred and unverified. Do not pool keys or treat this ledger's research rows as tickets.

## Other-market predictions kept separate

| Retained note market | n notes | Scored | Hits | Misses | Hit rate |
|---|---|---|---|---|---|
| away_over_05 | 41 | 41 | 36 | 5 | 87.8% |
| away_under_15 | 31 | 31 | 22 | 9 | 71.0% |
| away_under_25 | 313 | 313 | 285 | 28 | 91.1% |
| away_under_35 | 336 | 336 | 324 | 12 | 96.4% |
| double_chance | 3 | 3 | 2 | 1 | 66.7% |
| home_over_05 | 15 | 15 | 14 | 1 | 93.3% |
| home_under_15 | 12 | 12 | 8 | 4 | 66.7% |
| home_under_25 | 118 | 118 | 108 | 10 | 91.5% |
| home_under_35 | 123 | 123 | 119 | 4 | 96.7% |
| match_over_15 | 7 | 7 | 6 | 1 | 85.7% |
| match_over_25 | 475 | 475 | 295 | 180 | 62.1% |
| match_over_35 | 30 | 30 | 13 | 17 | 43.3% |
| match_over_45 | 393 | 393 | 101 | 292 | 25.7% |

These are ancillary event-note probabilities, not a selected team or the five target markets. Row-level note predictions are in the separate event-notes CSV; no ROI is inferred.

The 54 deduplicated `ou_2.5` selections represent 102 raw archive rows and have no `kickoff_utc` timestamp; none is scored as a pre-match prediction. The retained October quote files contain 1X2/goal-total quotes, but no target-market quote records were found for double chance, DNB/Asian 0, or Asian +0.5/+1.

## Early-stage coverage gap and isolated forward tracking

The 30-day archives retain emitted selection rows and send receipts, but not a complete per-candidate evaluation/rejection ledger. `auto_tickets_slice_ledger.jsonl` stores actual slip legs only; a candidate-level ticket rejection reason was not found. A missing send receipt cannot prove non-publication.

`src/edgefactory/scored_candidate_shadow.py` already provides an append-only, fail-soft, audit-only candidate ledger, wired at picks build/ticket stages. No retained `scored_candidate_shadow_*.jsonl` file was present in the local snapshot and the regular workflow report artifact did not cover JSONL. The daily workflow now has a dedicated 30-day artifact for only those sidecar ledger files. This is evidence retention only: no model/source input, selection, ticket, or publication logic was changed and no workflow was dispatched.

## Evidence availability

The following four CSVs were named by the prior audit, but were absent from the available workspace and preservation snapshot. They were not recreated or merged and remain deferred:

- `market_suitability_selections_2026-10-08.csv` — deduplicated selection/stage register
- `market_suitability_breakdowns_2026-10-08.csv` — dimension and model-key breakdown cells
- `market_suitability_event_notes_2026-10-08.csv` — separate event-note market predictions
- `market_suitability_prices_2026-10-08.csv` — strict selected-price subset

Break-even prices are arithmetic diagnostics, not market offers. Outcome rates describe retained records and cannot authorize a market pivot or deployment. The preceding narrative is not a substitute for the missing row-level evidence; validate untouched or subsequent forward data before any operational change.

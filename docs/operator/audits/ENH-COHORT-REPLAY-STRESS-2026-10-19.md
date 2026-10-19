# Broader cohort competition: production-path replay and stress test

**19 October 2026 — PR #100 follow-up.** Broader eligibility remains operator-authorized **ON**. These findings do not change its default, market band, price floor, stakes or lifecycle. They do not establish incremental ROI.

## Answer

**A bounded replay is possible and has been run, across competing markets and resulting cards—not Under 2.5 in isolation. A complete as-traded historical backtest is not reconstructable from the retained evidence.**

At archived prices, old and new eligibility choose exactly the same recommendations and tickets in all three snapshot views. Therefore this sample shows **zero incremental return**, not an improvement. When prices are stressed **before selection**, recommendations and card composition can change. One fully settled morning-snapshot stress case is materially worse under broader eligibility.

## What was replayed

The existing `audit_enh_under_parity.py` now executes **the production `compute_dynamic_enhancement()`**, with explicit flag `0` versus `1`. Its only cohort input is the archived partial rate surface and witnessed sample size. Unknown rates stay unknown; they are not filled with today's warehouse/model estimates. Price attachment receives strictly admitted archived quotes. Rolling audit/calibration readers are isolated because eligible probabilities come from the archived cohort, not model corrections.

Both arms use production `enhancement_legs()`, `enhancement_pool()` and `plan_day()`. Results are joined **after** selection; exact same-day, oriented full-name identities are required. Simultaneous ticket P&L is additive. Known losing legs resolve an accumulator even if another leg has no result; otherwise unresolved/conflicting results remain unknown with payout bounds.

The older pool-explanation helper remains solely for reproducing schema-1 reports. It does not reproduce raw-generator tie ordering, and is **not** the performance replay engine. New tests prove that substituting it for the actual selector fails a tied-rate/tied-price case.

### Scope boundary

These are **counterfactual cards on a normalized 100-point bank reset each date**. They do not replay rolling free-bank commitments, historic freeze decisions, bookmaker acceptance or placement receipts. A generated/replayed card must not be called an independently verified executed bet.

**Follow-up correction:** `[SKIPPED_VETO parent]` is an informational provenance tag, **not** a placement block or paper-bet marker. The ticket builder explicitly includes that bucket and stakes those legs. The original version of this paragraph incorrectly implied a parent-veto lifecycle block. See the [game-attrition diagnosis](GAME-ATTRITION-2026-10-19.md).

## Coverage and archive-vintage sensitivity

All retained final and morning archives from **18 June through 18 October 2026** were inspected: **3,406 rows**. Usable cohort history still exists only on **14–18 October**; expanding the calendar did not produce months of cohort-backed decisions. Incomplete 19 October and future archives were excluded.

| Retained snapshot view | Cohort fixtures with witnessed n ≥100 | Fixtures with any strict quote | Selected recommendations, either arm | Resulting accas, either arm |
|---|---:|---:|---:|---:|
| Final daily archives | 78 | 19 | 17 | 7 |
| Morning archives only | 49 | 9 | 8 | 4 |
| Earliest coherent available final/morning snapshot per fixture | 82 | 18 | 16 | 6 |

These views overlap and **must not be added together or treated as independent holdouts**. Morning archives add four fixtures beyond the final-archive witnessed-n population. Two final rows used by the earlier 80-row rate-only explanation lack archived sample sizes; they are refused by this actual-selector replay rather than assigned a fabricated n. Their exclusion does not change the final-view recommendations/cards.

Earliest-view attrition: 1,599 rows missing usable timestamps; 27 wrong-day rows; 1,608 without archived cohort rates; 43 too late (less than 30 minutes before kickoff); two lacking coherent witnessed n; 45 duplicate fixture rows. That leaves 82 fixtures. This is the **earliest available coherent cohort-backed snapshot**, not proof that it was the original freeze-time decision.

Earlier and later rate surfaces are never merged. Contradictory same-time snapshots are refused; a later snapshot cannot rescue a conflicted earlier decision. Quotes must be pre-decision and prematch, match exact identity/kickoff, satisfy provider schema/freshness and retain a named bookmaker. Latest quote per bookmaker is used before comparing books—not best-ever historical price. The earliest view refuses 611 post-decision quote observations and 3,369 conflicting same-time book cells. ScoutingStats history is not synthesized; the retained BetExplorer detail's time representation is not promoted into this audit's stricter UTC/kickoff-provenance standard.

## At archived prices: no policy difference

In the earliest view, **46** priced/in-band candidate occurrences can compete: 25 legacy-eligible and **21 newly admitted**, across **16 fixtures**. Additions are 16 Under 2.5, three Under 3.5 and two Under 4.5. **Every new candidate loses to a higher-rate eligible incumbent.** Result: zero changed fixture choices and zero changed cards.

Both arms produce six accas over three bet days: four resolved and two unknown. Total planned stake is **62.4999 points** across those dates; resolved stake is 37.4999. Resolved-subset net is +39.416576, but that is **not** the full card return. Including unknown tickets, total net is bounded by **+14.416576 to +109.291576 points** in this severely selected subset. Those bounds apply identically to both arms; the incremental difference is exactly zero. They are not a claim about live bankroll growth or a representative strategy ROI.

The separate stored tracker has 13 accas, six wins/seven losses and −16.15% stake-weighted tracking ROI. It is a different population, lacks placement verification and cannot be subtracted from the strict replay's favorable subset to claim uplift.

## Price stress: reselect, rebuild, then settle

Existing settlement-only slippage results remain available, but they do not test selection displacement. The new stress reduces every admitted **decimal quote** by 0%, 2%, 5% or 10% **before** applying the 1.30 floor and rate/price ranking. Each arm then rebuilds the whole card with the unchanged production recipe. These are hypothetical prices, not claimed historic executable quotes.

Each cell below is **changed fixture choices / changed card dates**, new versus legacy policy under the same stress:

| Quote reduction | Final view | Morning view | Earliest view |
|---|---:|---:|---:|
| 0% | 0 / 0 | 0 / 0 | 0 / 0 |
| 2% | 1 / 1 | 0 / 0 | 0 / 0 |
| 5% | 1 / 1 | 0 / 0 | 0 / 0 |
| 10% | 4 / 2 | 1 / 1 | 3 / 1 |

Even a 2% reduction changes the final-view Benfica–Celtic decision to a newly admitted 26.36%-cohort Under 2.5 at stressed 3.303 after the legacy choice becomes ineligible. Result coverage is insufficient to establish the changed card's net benefit. In the earliest view, the 10% stress changes three fixture choices, but only 18 October's card changes; its new-minus-old net is bounded by **−30.00 to +16.75 points** because the legacy card remains unresolved. Unknowns must not become losses or be dropped to create an uplift estimate.

### Concrete adverse card effect: morning view, 17 October, 10% haircut

A newly eligible **Salford City–Crawley Town Under 2.5**, archived cohort **30.4%**, qualifies at stressed **2.475**. It would not pass the legacy Under 2.5 threshold. The fixture's former higher-rate alternative no longer passes the price floor.

| Policy | Full production-built card | Stake | Net |
|---|---|---:|---:|
| Legacy | Fenerbahce–Alanyaspor O2.5 + Kashiwa Reysol–Nagoya Grampus O2.5; acca 2.14, **wins** | 12.5 | **+14.25** |
| Broader | Fenerbahce O2.5 + Salford U2.5; acca 3.61, **loses**. Kashiwa O2.5 + Kashima Antlers–V-Varen Nagasaki O2.5; acca 2.31, **loses** | 25.0 | **−25.00** |

**Incremental result: −39.25 normalized capital points.** The losing new under changes pairing and pulls an additional losing over into the card. It is not enough to settle the new under in isolation. The unchanged production sizing also deploys more of the allowed daily budget when a second ticket becomes available.

This is one retrospective, hypothetical-price, fully settled changed day—not evidence that the policy loses 39.25% in deployment. It **is** a concrete counterexample to “broader competition can only help.” The current eligibility band is 25–90%, not a newly invented 75% floor. “Best cohort” means highest rate **among remaining eligible candidates**, not a guarantee of a high rate or positive expected value.

No confidence interval is produced from that one changed day. Likewise, resolved unchanged dates cannot mask unknown changed cards to generate an apparent [0,0] uplift interval. Bootstrap diagnostics now explicitly refuse both situations.

## Correctness and release boundary

Added coverage exercises actual-selector replay, missing/conflicting/small sample sizes, missing original conditioning inputs, absent prices, raw-order ties, environment restoration on errors, preselection slippage and card rebuilding, earliest snapshot provenance/conflicts, source hash enforcement, total stake/unknown accounting and refusal of false-precision bootstraps.

Four in-memory deliberate mutations are caught: omitting preselection degradation; substituting the old helper for the selector; bootstrapping one changed day; hiding unresolved changed cards behind settled unchanged dates. No production source bytes were changed by these probes. See the [validation receipt](enh-cohort-replay-validation-2026-10-19.json) for the final test counts and hashes.

The existing registry replay was also rerun: 53 live-floor bet days, 108 simulated accas, 42 hits. It remains **selected/priced history**, not the competing-candidate universe, and supplies no evidence of broader-selection uplift.

No provider requests/credits, operational archive/history/bankroll changes, workflow edits, policy retuning, live dispatch, merge or bet execution were performed by this follow-up. Broader eligibility stays ON as authorized; deployment remains separate from PR publication.

## Receipts and reproduction

- [Final-view replay](enh-cohort-replay-final-2026-10-19.json)
- [Morning-view replay](enh-cohort-replay-morning-2026-10-19.json)
- [Earliest-view replay](enh-cohort-replay-earliest-2026-10-19.json)
- [Earliest-view full-market competition](enh-cohort-replay-competition-2026-10-19.json)

Each replay records source/archive hashes, settings, the selected decision snapshot, sample size, known rate surface, both arms, unknown-aware return bounds and both settlement-only and preselection stresses. Earlier schema-1 receipts describe the code at commit `7355957`; their historical 80-row explanation is not overwritten. The competition tool can use the new receipt explicitly and refuses changed inputs.

```bash
for mode in final morning earliest; do
  PYTHONPATH=src .venv/bin/python scripts/audit_enh_under_parity.py \
    --since 2026-06-18 --until 2026-10-18 --snapshot-mode "$mode" \
    --out ".cache/enh-cohort-replay-$mode.json"
done
PYTHONPATH=src .venv/bin/python scripts/audit_enh_market_competition.py \
  --source-report .cache/enh-cohort-replay-earliest.json \
  --out .cache/enh-cohort-competition.json
PYTHONPATH=src .venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python tools/verify_enh_default_parity.py
```

A longer faithful comparison needs complete contemporaneous cohort/candidate surfaces, quotes and freeze/placement lineage. Use the existing capture/logging/ticket structures; do not turn current warehouse rates, missing prices or tracker entries into fabricated historic decisions.

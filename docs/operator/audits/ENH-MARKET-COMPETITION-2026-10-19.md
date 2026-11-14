# Enhancement market contention — 19 October 2026

> **Policy supersession, 19 October:** the operator has authorized the prepared shared cohort eligibility as the new ON default; see [current disposition](../REALIZED-STATS-UNDERS-2026-10-19.md). Earlier default-off recommendations below are historical. The retained full-pool no-change/no-uplift finding remains unchanged. This reuses the existing selector/lifecycle; no new shadow lane was added.

## Direct answer

**Do not change Under 2.5 from 85% to 80% in isolation.** The relevant decision is which eligible market wins each fixture, and then which resulting legs reach the actual tickets. The available retained evidence does not justify a live threshold adjustment: relaxing the filters across the full available cohort-backed pool changed no recommendations or cards. That is not validation of the old cutoffs; it is evidence that those cutoffs were not the binding constraint in this sample.

The sensible research comparison remains the prepared common eligibility rule for **all cohort-backed priced markets**: rate 25–90%, captured odds at least 1.30, highest cohort rate first and higher odds to break a rate tie. Those numbers describe the existing shared operator rule, not a newly proved ROI optimum. Broad parity remains default-off pending prospective evidence. The no-cohort model path is separate and unchanged.

## Full-pool comparison, not an isolated U2.5 test

The new read-only diagnostic verifies every input hash from the earlier red team, re-reads the historical quotes with the same strict identity/time/source rules, and reproduces both fixture choices exactly before explaining competition.

| Measure | Result |
|---|---:|
| Retained cohort snapshots | 80 |
| Available candidate/quote combinations inside shared rate band and odds floor | 48 |
| Additional candidates admitted by common cohort eligibility | 22 |
| Fixtures containing additional candidates | 17 |
| Additional candidates beaten by a strictly higher-rate market | **22 / 22** |
| Changed fixture recommendations | **0** |

The 22 additions were **17 Under 2.5, 3 Under 3.5 and 2 Under 4.5**. There were no newly admitted non-under candidates in this retained priced sample, although all available cohort-backed markets were compared. Counts are candidate occurrences, not independent bets. Source coverage is incomplete; this is not the full historical live universe.

The markets that beat these candidates were Over 2.5 (14 candidate comparisons), Home Over 0.5 (2), Home Over 1.5 (3), and Away Under 1.5 (3). Those are not 22 distinct winning fixtures: several newly admitted markets can lose within the same fixture.

Across the whole retained pool, both arms selected exactly the same 17 fixture recommendations: 14 Over 2.5, one Home Over 0.5, one Home Over 1.5 and one Away Under 1.5. Not all 17 recommendations necessarily reach tickets; the downstream recipe filters/ranks them. The prior paired card audit found identical cards as well, with no demonstrated ROI uplift.

### Actual retained examples

| Fixture | Additional contender after relaxation | Winner under both policies |
|---|---|---|
| LAFC–Austin, 15 Oct | Under 3.5: 65.39%, odds 1.86; Under 2.5: 43.38%, odds 2.86 | **Home Over 0.5: 89.06%, odds 1.38** |
| Nashville–Sporting Kansas City, 15 Oct | Under 4.5: 64.65%, odds 1.50; Under 3.5: 44.19%, odds 2.15; Under 2.5: 26.51%, odds 3.75 | **Home Over 1.5: 81.86%, odds 1.95** |
| Benfica–Celtic, 15 Oct | Under 2.5: 26.36%, odds 3.37 | **Over 2.5: 73.64%, odds 1.32** |

These are archived cohort frequencies and strict historical quotes, not independently validated forward probabilities or bookmaker placement receipts. The result is about selection behavior, not proof that these winners were good value.

## Why the legacy numbers deserve a joint review

The default prefilter is asymmetric before candidates even compete:

- Match Over 2.5: 35%; Under 2.5: 85%.
- BTTS Yes: 35%; BTTS No: 50%.
- Match Over 3.5: 30%; Under 3.5: 90%.
- Match Over 4.5: nominal 18%, effectively 25% due to the shared band; Under 4.5 is absent from the default generator.
- Home/away Over or Under 0.5/1.5: 80%; 2.5: 85%; 3.5: 90%.
- Match Over/Under 1.5: 80%.

Consequently a 60% BTTS candidate can compete while an 80% U2.5 candidate is excluded. Changing only U2.5 to 80% would leave analogous inconsistencies elsewhere. Common cohort eligibility is the coherent **research target**, not evidence of higher realized profit. Goal ranges/exact scores remain excluded; double chance has no corresponding all-outcome goal-cohort rate and must not be silently assigned one.

## Cases where competition changes the answer

Seven new tests exercise the actual selector using coherent score distributions, with other markets explicitly priced in contention:

1. U2.5 80% versus Home Over 0.5 83%, both priced above 1.30: the home market wins with or without parity. Admitting the under does not select it.
2. U2.5 80% versus BTTS Yes 60%, both priced above 1.30: default selects BTTS; parity selects the under.
3. An under below the 1.30 floor still loses eligibility even with parity.
4. Equal 80% cohort rates: higher price wins the tie.
5. BTTS 60% at 2.10 versus U2.5 80% at 1.40: parity selects the under under the existing **hit-rate-first** rule, even though conditional point expected ROI is 26% for BTTS versus 12% for the under.

The last case is important: **highest hit rate is not the same objective as highest expected ROI**. Cohort calibration, executable odds and the actual accumulator recipe must be evaluated jointly. The arithmetic is hypothetical and assumes true forward probabilities; it does not justify switching to EV ranking. No EV gate, alternate ranking or automatic deployment has been added.

## Decision and validation

- No evidence-based replacement cutoff was identified; no live rule changed.
- Do not tune a separate U2.5 minimum from this sample or claim increased ROI because more markets become eligible.
- For validation, compare the baseline and common-eligibility policies on complete frozen predecision pools, record displacement and actual card/stake changes, and measure calibrated out-of-sample paired returns. If the objective changes from hit rate to ROI, test that ranking change separately rather than silently conflating it with parity.
- Prior hold/default-off containment remains intact.

Focused tests after this follow-up: **123 passed in 4.48s**. Baseline parity: **200 identical seeded cases**. Seven of the focused cases are the new contention tests; the previously completed full suite was 3,234 tests before these seven additions, not a newly rerun 3,241-test claim. The audit command also reproduced all 80 stored baseline/proposed choices and verified all prior report input hashes.

Reproduce:

```bash
PYTHONPATH=src .venv/bin/python scripts/audit_enh_market_competition.py \
  --out .cache/enh_market_competition.json
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_hybrid_engine.py tests/test_under25_cutoff_numbers.py \
  tests/test_audit_enh_under_parity.py tests/test_picks_today.py
PYTHONPATH=src .venv/bin/python tools/verify_enh_default_parity.py
```

Receipt with full competing pools for affected fixtures: [enh-market-competition-2026-10-19.json](enh-market-competition-2026-10-19.json). No provider/API calls, operational history edits or deployments.

# Price-join attribution — where the unmatched rows actually go

**Date:** 2026-10-06 · **Method:** committed receipts + archived boards, replayed
through the production matcher. No live calls, no credentials, no gate changes.

## Headline

**The 2026-10-06 no-bet day has no defect in it. It was an international-break
slate.** Five of the eight picks were in competitions that do not exist in
TheOddsAPI's catalogue at all; the three that were covered were priced
correctly, and two of those priced below the 1.20 floor. One qualifying leg
against `LEGS_PER_ACCA=2` is the abstention contract working exactly as
`docs/operator/README.md` specifies.

This also **retracts fix #3 from the diagnosis ranking table**
("map short-league keys into theoddsapi idle quota, ~40 legs"). There are no
keys to map. See §3.

---

## 1. The blind spot that hid this — now closed (`d00f801`)

`donor_join_diagnostics()` buckets every unmatched provider row by its first
honest failure. It was wired to the shadow donors plus OddsPAPI, but **not to
TheOddsAPI or BetExplorer** — the only two priced boards actually returning
rows. From the committed `source_health_*.json`:

| day | source | usable | matched | unmatched | accounted | unexplained |
|---|---|---:|---:|---:|---:|---:|
| 10-03 | theoddsapi | 589 | 0 | 589 | 0 | **589** |
| 10-04 | theoddsapi | 302 | 0 | 302 | 0 | **302** |
| 10-05 | theoddsapi | 365 | 0 | 365 | 0 | **365** |
| 10-06 | theoddsapi | 155 | 3 | 152 | 0 | **152** |
| 10-03 | betexplorer | 21 | 0 | 21 | 0 | **21** |
| 10-06 | betexplorer | 12 | 3 | 9 | 0 | **9** |
| 10-03 | oddspapi | 30,022 | 0 | 30,022 | 30,022 | 0 |
| 10-04 | oddspapi | 162,652 | 0 | 162,652 | 162,652 | 0 |
| 10-06 | betbetter | 1,321 | 0 | 1,321 | 1,321 | 0 |

1,423 TheOddsAPI rows and 98 BetExplorer rows unmatched over five days with
**zero recorded reason**, while the repaired adapters were 100% accounted on
the same days. A second, quieter bug: BetExplorer's bundle is published as
`betexplorer_odds` but its health row is keyed `betexplorer`, so even had it
been diagnosed, the report was computed and then dropped on a membership test.

Both fixed. Measurement only — the diagnostic re-runs
`find_side_keyed_odds_row` per row and can never admit a row the matcher
rejects (`test_diagnostics_do_not_loosen_the_join`).

---

## 2. Replaying the archive through the real matcher

Archived TheOddsAPI boards vs archived picks, same day, production matcher:

| day | picks | rows | matched rows | `no_pick_for_fixture` | `fixture_key_miss` |
|---|---:|---:|---:|---:|---:|
| 10-03 | 57 | 589 | 143 | 446 | 0 |
| 10-04 | 30 | 302 | 82 | 220 | 0 |
| 10-05 | 5 | 365 | 99 | 224 | 42 |
| 10-06 | 8 | 155 | 45 | 110 | 0 |

100% accounted, every day. **The join is not broken.** The dominant bucket is
`no_pick_for_fixture` — the board carries fixtures we did not pick. That is
not a defect; it is non-overlap.

The decisive number is on the *pick* side. Distinct fixtures the board covers:

| day | picks | board fixtures | picks the board covers |
|---|---:|---:|---:|
| 10-03 | 57 | 7 | 5 |
| 10-05 | 5 | 4 | 3 |
| 10-06 | 8 | 3 | **3** |

155 rows on 10-06 are 3 fixtures in depth (≈52 rows each — many books × three
selections), not 155 fixtures. The board is deep and narrow.

---

## 3. Why the board is narrow — the retraction

`localdata/theoddsapi_sports.json`, the provider's own active catalogue, holds
**49 soccer keys**. Searching it:

```
'friend'   -> []
'africa'   -> []
'afcon'    -> []
'concacaf' -> []
'nations'  -> ['soccer_uefa_nations_league']
'qual'     -> []
```

The 2026-10-06 slate, with the capture receipt's own verdict:

| pick | competition | outcome |
|---|---|---|
| Croatia v Spain | UEFA Nations League | **covered, priced @1.28 → QUALIFIED** |
| England v Czech Republic | UEFA Nations League | covered, priced @1.13 → below floor |
| Albania v San Marino | UEFA Nations League | covered, priced @1.03 → below floor |
| Argentina v Benin | International Friendlies | `league not covered` |
| India v Uruguay | World Friendlies | `league not covered` |
| Algeria v Niger | International Friendlies | `league not covered` |
| Angola v Malawi | AFCON Qualification | `league not covered` |
| Grenada v Bonaire | CONCACAF Nations League | `league not covered` |

`theoddsapi_capture_2026-10-06.json` records it verbatim:
`unmatched_reasons = {"league not covered: International,Africa Cup Of Nations
Qualification Grp. B": 1, "league not covered: World Friendlies": 1}`.

**Every covered fixture was priced. Every uncovered fixture is in a
competition the provider does not sell.** Quota (56/1440) is irrelevant;
there is no SKU to spend it on. The ranked-table item "map short-league keys
into idle quota, ~40 legs" is withdrawn as impossible.

The structural asymmetry worth naming: the *prediction* sources cover
friendlies and qualifiers; the *execution-eligible price* sources do not. On
an international-break slate the funnel is guaranteed to collapse.

---

## 4. The identity-alias gap — real, measured, small

The curated exonym aliases from `FIXTURE-IDENTITY-SPLIT-2026-10-05.md` live in
`canonical_team`. The price join uses `norm_team`, which never consults them:

| pick name | board name | `norm_team` | `canonical_team` |
|---|---|---|---|
| Türkiye | Turkey | `turkiye` / `turkey` ✗ | ✓ |
| Czech Republic | Czechia | `czechrepu` / `czechia` ✗ | ✓ |
| Eibar | SD Eibar | ✗ | ✗ |
| Grimsby | Grimsby Town | ✗ | ✗ |

That doc's blast-radius table marks the price adapters "unaffected: read-time
joins on both sides" — true for diacritics, **not** for curated aliases.
`Italy v Türkiye` was on the 10-05 board as `Italy v Turkey` and was missed.

Measured over the whole archive (1,298 picks):

- joined today (`norm_team`): **111**
- naive swap to `canonical_team`: **98** — a **net regression of 13**
- variant union (superset, cannot lose): **114** → **+3 picks**

So the fix is a variant union, never a swap — and it is worth **3 picks in two
months**. Real, correct, and not where the legs are. Logged, not shipped:
it changes live pricing behaviour and needs operator sign-off.

---

## 5. The one lead with real volume

`theoddsapi_capture_2026-10-04.json` — the operator's standing open question
("why did auto mode mark only 2 of 24 shortlist fixtures due?") is now
answered by the persisted receipts:

```
candidate_fixtures = 30   attempted = 5   rows = 0
skip_reasons = {"kickoff_already_passed": 14, "retry_cooldown": 8,
                "kickoff_mismatch": 5, "priced": 3}
captured_at  = 2026-10-04T19:17:32+00:00
```

**14 of 30 candidates were skipped because kickoff had already passed**, on a
capture that ran at **19:17 UTC** — after most European kickoffs. 10-05 is the
same shape (`kickoff_already_passed: 5`, capture at 19:17 UTC, `status:
not_due`, zero attempts). 10-06 ran early, at 04:18 UTC, and lost only one
fixture that way.

That is a **scheduling** finding, not a coverage one, and it is the only lead
here with double-digit fixture volume. It is a workflow-timing question, so it
is reported rather than changed: the GitHub App cannot push
`.github/workflows/`, and capture cadence is operator-owned.

---

## 6. What I recommend

1. **Accept 2026-10-06 as a correct abstention.** No remediation is owed.
2. **Investigate the 19:17 UTC capture slot** (§5) — 14 fixtures/day lost to
   late scheduling dwarfs everything else measured here. Operator-owned.
3. **Expect no-bet days during international breaks** and consider whether
   generating picks for competitions no execution-eligible source prices is
   worth the funnel noise.
4. **Hold the variant-union alias fix** (§4) until something else makes it
   worth a pricing-behaviour change; +3 picks does not justify it alone.
5. **Do not pursue** TheOddsAPI league-key mapping (§3) — withdrawn.

## Verification

- `PYTHONPATH=src python -m pytest -q` → **1410 passed**
- `git diff --stat origin/main...HEAD -- .github/workflows/ localdata/` → empty
- All numbers above are reproducible from committed receipts and archives.

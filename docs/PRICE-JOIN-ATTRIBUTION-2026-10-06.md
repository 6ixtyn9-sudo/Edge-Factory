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

## 5. RETRACTED — the "late capture" finding was an artifact

**The scheduling finding originally published in this section is withdrawn. It
was wrong.** It is left here, struck, because a retraction that deletes its own
evidence teaches nobody anything.

The claim was: `theoddsapi_capture_2026-10-04.json` shows
`skip_reasons = {"kickoff_already_passed": 14, ...}` with
`captured_at = 19:17 UTC`, therefore the capture runs too late and loses 14
fixtures a day.

**Why it is wrong.** `_write_receipt()` writes one file per *day*, overwritten
by every run. The external cadence is SAST 09/12/15/18/21 (= 07/10/13/16/19
UTC), so the receipt only ever shows the **last** run of the day. At 21:17 SAST
"kickoff already passed" is the correct and expected verdict for a fixture that
kicked off at 19:00 — and says nothing about whether the 09:00 run attempted it.

The persistent `theoddsapi_attempts_<day>.json` ledger is *not* overwritten,
and it settles the question:

```
2026-10-03   fail_at 07h x6 · 10h x2 · 13h x32 · 17h x11 · 22h x1
             first_at 07h x1 · 13h x1 · 22h x5
2026-10-04   fail_at 01h x1 · 04h x1 · 05h x1 · 10h x2 · 13h x7 · 16h x2 · 19h x9 · 22h x3
```

Attempts are spread across the entire day from 01h to 22h UTC. **The capture is
not running late. There is no scheduling defect and no workflow change is
needed.**

Generalisable lesson: a per-day receipt that is overwritten in place cannot be
read as a per-day summary. Only the append-style ledger can.

---

## 5b. What the ledger actually shows — and the real repair

With the artifact removed, the attempt ledgers give the structural number over
30 days:

| | fixtures | share |
|---|---:|---:|
| shortlisted for pricing | 765 | — |
| ever obtained a TheOddsAPI price | 87 | **11.4%** |
| never priced | 678 | 88.6% |

Attributing those failures by competition: **270 competitions never once
obtained a price, against 40 that did.** The pick generator ranges across ~310
competitions; the only execution-eligible board carries 49 keys.

But the split inside those failures is the finding. `USA,Major League Soccer`
failed 7 of 7 — while `soccer_usa_mls` sits in the catalogue. So does
`soccer_netherlands_eredivisie` (`Nl1`, 11 failures),
`soccer_poland_ekstraklasa` (`Pl1`), `soccer_norway_eliteserien` (`No1`) and —
indefensibly — `soccer_epl`:

```
sport_key_for_league("EPL", sports)  ->  None
```

`sport_key_for_league` rejects any label under 4 characters after
`_league_code` unless stage 1 lists it in `SHORT_LEAGUE_KEYS`. **That table had
7 entries.** Every 2-3 character provider code in the archives — `EPL`, `L1`,
`Nl1`, `Us1`, `De1`, `It1`, `Es1` — resolved to `None` and was reported
`league not covered` without ever being requested.

**Fixed in `c407609`**: 36 codes added, each verified three ways — key present
in the catalogue, provider `title`/`description` confirms the tier, and the
fixtures observed under that code in the committed archives are the right
competition (`epl` → Arsenal/Man City, `l2` → Crawley/Barnet, `sc1` →
Rangers/Celtic, `us1` → LAFC, `br2` → Fortaleza).

Replayed over the same 30 ledgers:

| | fixtures |
|---|---:|
| newly resolve to a sport key | **109** (~3.6/day) |
| regressions (lost a key) | **0** |

`efl` was deliberately left unmapped (ambiguous between `soccer_efl_champ` and
`soccer_england_efl_cup`), and every genuinely absent competition still returns
`None` — friendlies, AFCON qualification, CONCACAF, national leagues, lower
tiers. None remains strictly preferred over a wrong-competition key.

This **partially reinstates ranked-fix #3**, which §3 of the first version of
this document withdrew. The withdrawal was right about the *mechanism* — there
is no friendlies or AFCON SKU to buy, so 2026-10-06 itself is unchanged and
remains a correct abstention — and wrong about the *scope*: a sixth of the
unpriced slate was in competitions the provider already sells, lost to a
7-entry lookup table.

Credits are only spent on fixtures that now resolve, and usage was 56/1440 for
the month. Quota is not a constraint.

---

## 6. (SUPERSEDED — see §5) The reading that produced the retracted claim

Kept verbatim as the evidence trail for the §5 retraction. The numbers are
real; the inference drawn from them was not, because this receipt is the
last run of the day overwriting all earlier ones.

```
candidate_fixtures = 30   attempted = 5   rows = 0
skip_reasons = {"kickoff_already_passed": 14, "retry_cooldown": 8,
                "kickoff_mismatch": 5, "priced": 3}
captured_at  = 2026-10-04T19:17:32+00:00
```

The operator's standing question ("why did auto mode mark only 2 of 24
shortlist fixtures due?") is genuinely answered by the receipts, but the
answer is §5b's: most candidates never resolved to a sport key at all, so
they were never due.

---

## 7. What I recommend

1. **Accept 2026-10-06 as a correct abstention.** No remediation is owed; the
   slate was an international break and the floor did its job.
2. **Ship `c407609`** (short league codes) — 109 fixtures over 30 days move
   from never-requested to requestable, 0 regressions, no gate touched. This
   is the one item here with real volume.
3. **No workflow change.** §5 is retracted; capture cadence is fine.
4. **Expect no-bet days during international breaks.** Consider whether
   generating picks in competitions no execution-eligible source prices is
   worth the funnel noise — a reporting question, not a gate.
5. **Hold the variant-union alias fix** (§4): +3 picks over 1,298 does not
   justify a pricing-behaviour change on its own.
6. **Do not pursue** friendlies/AFCON/CONCACAF key mapping (§3) — those SKUs
   do not exist.

## Verification

- `PYTHONPATH=src python -m pytest -q` → **1457 passed**
- `git diff --stat origin/main...HEAD -- .github/workflows/ localdata/` → empty
- Every number is reproducible from committed receipts and archives; the
  replays use the production resolver and matcher, not reimplementations.

## Corrections log

| § | claim | status |
|---|---|---|
| 3 | "no keys to map, fix #3 impossible" | **partially reinstated** by §5b — true for friendlies/AFCON, false for the 36 short codes |
| 5 | "capture runs at 19:17 UTC, loses 14 fixtures/day" | **retracted** — artifact of an overwritten per-day receipt |

# Join-layer repair, round 2 — findings (2026-10-03)

Successor to [`JOIN-REPAIR-2026-10-03.md`](JOIN-REPAIR-2026-10-03.md). Round 1
repaired the canonicaliser, Boggio, OddsPAPI identity, the date buckets and
the kickoff rendering. Round 2 closes the three things round 1 left open and
corrects one of its conclusions.

Evidence base: the persisted run artefacts in `localdata/` plus the full
GitHub Actions job log for run `37125201110` / job
`2cc433fc-3516-5519-a8c6-71b1899caaa9` (2026-10-03 13:09–13:24 UTC).

---

## 1. OddsPAPI: the 414 rows are now invalidated by generation

**Capture is not cache-first.** `capture()` calls `fetch_fixtures` and
`fetch_odds` on every run; `_append_rows` only dedupes what comes back. So a
re-run does fetch, and fresh rows do carry non-empty `home`/`away` (they come
from the `/fixtures` record, and the parser refuses the row when neither
endpoint names the teams).

**The consumer is cache-only**, and that is where the hazard lives.
`picks_today` reads the whole monthly file `oddspapi_odds_2026-10.csv.gz`, so
the 414 rows written by the superseded parser are re-read on every run for
the rest of October.

Round 1 bypassed them on blank participants. That works for these 414 — but
blank participants are only the *symptom*. The actual defect in generation 1
was that the outcome name was read from `name` while the payload carries it
at `players.0.playerName`, so `_selection_from_name` compared `"" == ""` and
labelled **every** outcome `home`. A generation-1 row that happened to carry
teams would sail past an identity check and inject a price under the wrong
selection.

So the gate is now on the cause:

* `scripts/capture_oddspapi.py` grows `SCHEMA_VERSION = 2` and a
  `schema_version` column, stamped in `_append_rows` so no write path can
  emit an unmarked row.
* `_migrate_header` widens the header and leaves pre-existing rows blank. It
  does not back-stamp them, drop them, or change a value.
* `schema_version` is **in** the dedupe key, so a corrected row can never be
  suppressed by its broken predecessor. Invalidation beats idempotence.
* `picks_today` passes `min_schema_version=ODDSPAPI_MIN_SCHEMA_VERSION` (2).
  Older rows are counted as `stale_schema_rows` and bypassed. The two
  constants are pinned to each other by a test so they cannot drift.

The file is **not** deleted — it is evidence. Verified on the real data:

```
donor join misses oddspapi_odds: stale_schema=414 (matched_rows=0 raw_rows=414)
oddspapi=raw414/usable0/matched0
```

Observed, classified, named, bypassed — and the capture is byte-identical
afterwards.

## 2. Bet Better vocabulary — still blocked, and why

**The 687 raw market strings are not recoverable from anything that exists
today.** Checked, independently of round 1's claim:

* `localdata/*_shadow_*.json` is gitignored and absent from the checkout.
* `localdata/official_run_2026-10-03.json` contains no Bet Better data at all.
* `localdata/source_health_2026-10-03.json` carries the *count*
  (`market_unmapped`) and nothing else.
* The **full job log** carries only the aggregate line
  `donor join misses betbetter: market_unmapped=687,date_mismatch=637`.

Guessing the tokens is explicitly out of scope, and so is a live discovery
call. What round 2 can do is prove the harvester works. Exercised against
raw provider vocabulary in the real payload shape:

```
donor join misses betbetter: market_unsupported=4,selection_unmapped=2 (matched_rows=1 raw_rows=7)
donor unmapped vocabulary betbetter: unknown_selection:croatia=2
  unsupported_market:draw_no_bet=2 unsupported_market:asian_handicap=1
  unsupported_market:correct_score=1 (distinct=4)
```

Seven rows in, seven out — nothing dropped — `Head to Head` → `1x2/home`
matched and `price_push_eligible=True`, every other token retained, named and
counted. Role preserved: `odds_kind="fair"`,
`provider_role="model_fair_price_donor"`, `bookmaker=None`,
`named_bookmaker=False`.

**The next run on merged code enumerates the 687.** Mapping is a follow-up
once the tokens are visible.

## 3. Kickoff: round 1's verdict was right about the offsets and wrong about the risk

Round 1 declined a blanket shift — correct, and the census explains itself
once the renderer is identified. Offsets are **display-vs-UTC**, so they are
literally the renderer's zone:

| shape | zone | n | renderer |
|---|---|---|---|
| `HH:MM` | UTC−5 | 35 | statarea |
| `HH:MM` | UTC−7 | 3 | statarea |
| `DD-MM, HH:MM` | UTC+1 | 13 | zulubet (present in all 13) |
| ISO with offset | exact | 4 | — |

`kickoff_utc` is **not** derived from the display text. It comes from
`kickoff_witness`, always an explicitly zoned stamp
(`'2026-10-03T18:45:00Z'`, `'2026-10-03T13:00:00+02:00'`) from bzzoiro /
vitibet / scoutingstats, and `resolve_kickoff_utc` fails closed when two
zoned witnesses disagree. A zone-free string cannot produce a `kickoff_utc`.
So the display string cannot corrupt the instant — confirmed.

### The part round 1 missed

The pre-match lead guard does not read `kickoff_utc`. It reads the **raw
display text** and stamps a zone-free value as local (SAST). Round 1 argued
this always errs early because every observed renderer sits behind SAST.
That reasoning has a hole: **a bare `HH:MM` carries no date.**

For a fixture kicking off just after midnight UTC, the renderer's own clock
face belongs to the *previous* day. Re-attached to the pick's `2026-10-03`
date, it lands ~15 hours late. Two picks on the live card were admitted by
the guard after they had already been played:

```
Boca Juniors vs Union Santa Fe  display '17:30'  true 02:30 SAST  → admitted 12.7 h after kickoff
Colombia vs Paraguay            display '19:00'  true 02:00 SAST  → admitted 13.2 h after kickoff
```

Both survived only because the price lane quarantined them
(`SCOUTINGSTATS_SOLE`, `push_eligible=False`). Neither reached a ticket, but
the lead guard itself read late — the one direction it must never move.

### Fix, one-directional by construction

`operational_pick_eligibility` now takes the **earlier** of the feed text and
the resolved instant:

```python
resolved = _parse_resolved_kickoff_instant(pick)
if resolved is not None:
    ko = min(ko, resolved)
```

This can only shorten the computed lead, so it can only ever *subtract*
picks. A missing display string stays `missing_kickoff_same_day` — admitting
those would add picks, and this guard is only allowed to subtract. A
malformed or zone-free `kickoff_utc` is ignored, not trusted.

Replayed over the whole 2026-10-03 card at the 15:13 build time: 55 rows
unchanged, 2 rows `True → False` (the two above), **0 rows `False → True`**.

## 4. Production matched counts — honest zeros

| donor | matched | why |
|---|---|---|
| betbetter | **0** | `market_unmapped=687`, `date_mismatch=637` of 1324 raw — last measured on pre-repair code |
| boggio | **0** | `selection_unmapped=9`, `date_mismatch=11` of 20 raw — same |
| oddspapi | **0** | `stale_schema=414` of 414 raw — measured on repaired code |

Only the OddsPAPI number is post-repair, and it is a true zero: every row in
that file predates the fix, so there is nothing for it to match until capture
runs again.

The betbetter/boggio numbers are the **pre-repair** figures from run
`37125201110`; the repairs are not on `main` yet, so no post-repair
production number exists. Non-zero matching is asserted in
`tests/test_donor_join_repair.py` against raw-vocabulary fixtures.
**No production matched count is claimed.** PR #30 has to merge and one
scheduled run has to fire before these cells can be filled in honestly.

## 5. Credential-blocked sources — unchanged

No live probe was made against any of the four. Verdicts stand from round 1;
see the Task 6 note at the head of
[`daily.yml.proposed`](daily.yml.proposed).

`bzzoiro_odds` `http_403_auth` (credential rejected, not quota) ·
`pinnapi_odds` `valid_empty_http_200` (working integration, empty board —
leave alone) · `betminer` and `sharpapi_odds` `http_404_endpoint_contract`,
both awaiting a RapidAPI playground path from the operator. SharpAPI resolves
through the existing `SHARPAPI_ENDPOINT` / `SHARPAPI_SPORT` secrets, so **no
workflow edit is required**. Do not send SharpAPI a `date` param unless the
provider documents it.

---

## What the next live run should print

```
donor join misses oddspapi_odds: stale_schema=414 | <real buckets for fresh rows>
donor unmapped vocabulary betbetter: <the 687, enumerated by raw token>
donor join misses betbetter:  out_of_window=…, market_unsupported=…   (matched_rows>0)
donor join misses boggio:     selection_unsupported=…                 (matched_rows>0)
kickoff display offset verdict: per-source (…)
```

Once `donor unmapped vocabulary betbetter` appears, map each token or mark it
`unsupported` explicitly — that is the remaining piece of Task 2.

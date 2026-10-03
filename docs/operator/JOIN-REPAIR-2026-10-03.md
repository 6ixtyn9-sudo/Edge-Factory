# Join-layer repair — findings and changes (2026-10-03)

Grounded in GitHub Actions job `2cc433fc-3516-5519-a8c6-71b1899caaa9`
(2026-10-03 13:13–13:24 UTC / 15:13–15:24 SAST), the first run with SharpAPI
and OddsPAPI enabled. The source-of-truth receipt for that run is
`localdata/source_health_2026-10-03.json`.

The capture layer was never the problem. Every defect below sits in the
join/canonicalisation layer.

---

## What was actually wrong

| Lane | Symptom in the run | Root cause found |
|---|---|---|
| Bet Better | `market_unmapped=687`, `date_mismatch=637` | `Draw No Bet` (and anything like it) had no classification at all; the 637 are a legitimately multi-day upcoming board mislabelled as a date defect |
| Boggio | `selection_unmapped=9`, `date_mismatch=11` | double-chance predictions (`1X`/`12`/`X2`) were **silently dropped** at capture instead of counted; and `provider_kickoff_date` could not parse the feed's `"YYYY-MM-DD HH:MM:SS UTC"` stamp, so *every* row joined with an empty date |
| OddsPAPI | 414 usable / 0 matched, no instrumentation | all 414 captured rows have **empty `home`/`away`** and are **all labelled `1x2`/`home`** — see below. Not a market-vocabulary problem |
| Kickoff | Croatia v England stored `17:00`, true 18:00 SAST | the display string is the raw feed text; it is **per-source**, not a systematic one-hour error |

### The OddsPAPI finding, in detail

`localdata/oddspapi_odds_2026-10.csv.gz` holds the run's 414 rows. Reading it:

```
market      {'1x2': 414}
selection   {'home': 414}
home        {'': 414}      away {'': 414}      league {'': 414}
```

Three different prices for the same fixture and bookmaker (4.3 / 4.75 / 1.532)
were all written as `1x2 / home`. The cause is two lines in
`rows_from_odds_response`:

* the 2026-10-03 `/odds` payload carries no `participant1Name` /
  `participant2Name`, so `home`/`away` were `None`; and
* the outcome name lives in `players.0.playerName`, not `name`, so `name`
  was empty — and `_selection_from_name` then compared `"" == ""` against the
  empty home name and returned `"home"` for every outcome.

Those rows could never join (no fixture key), so no wrong price reached a
ticket. But they were counted as 414 *usable* rows, which overstated the
board's supply, and had a fixture key ever matched, an away or draw price
would have been staked as the home price.

---

## Changes

### Shared canonicaliser (`src/edgefactory/odds_normalization.py`)

* Three outcomes instead of two: `mapped`, `unsupported` (recognised
  provider vocabulary this pipeline deliberately does not price) and
  `unknown`. **Both failures are counted misses; neither is ever a silent
  drop.**
* `NormalizationFailure` now carries `kind` and `raw`, so a miss can name
  the provider token. `reason` keeps its historic `"<kind>:<token>"` shape.
* `parse_zoned_timestamp` accepts the zone-bearing shapes actually observed
  in captured payloads — ISO/`Z`, Bet Better's 7-digit fractional seconds,
  and Boggio's `"… UTC"` suffix. **A zone-free value still fails closed**;
  nothing defaults to the capture date or the capture timezone.

### Bet Better (`src/edgefactory/sources/betbetter.py`)

Role unchanged: `odds_kind="fair"`, `provider_role="model_fair_price_donor"`,
`bookmaker=None`, `named_bookmaker=False`.

Unmappable rows were already retained with raw vocabulary; they now also
carry `canonicalization_reason` so the vocabulary census can name them.

### Boggio (`src/edgefactory/sources/boggio.py`)

Role unchanged: `average_bookmaker_price_donor`, `provider_average`,
`average_bookie_aggregate`, `named_bookmaker=False`, `price_push_eligible`,
`price_independence_family="boggio_average"`.

* `parse_predictions` no longer does `if canonical is None: continue`. That
  `continue` is where the canonicaliser was effectively bypassed: the shared
  helper *was* called, but its failure path deleted the row, so the miss
  could never be counted. Unmappable rows are now kept with their raw
  vocabulary and `price_push_eligible=False`.
* `_parse_stamp` / kickoff attribution go through `parse_zoned_timestamp`,
  which fixes the empty join date on every row.

### OddsPAPI (`src/edgefactory/sources/oddspapi_odds.py`, `scripts/capture_oddspapi.py`)

* **Fail closed without fixture identity.** `rows_from_odds_response` takes
  explicit `home`/`away` from the caller (the `/fixtures` record the capture
  already holds) and emits nothing when neither endpoint names the teams.
* Outcome names are read from `name` *or* `playerName` — both observed.
* `_selection_from_name` refuses an empty name.
* `mainLine` is honoured: when a market flags a main line, alternate lines
  are skipped and counted as `alt_line_skipped`.
* `bookmakerChangedAt` → `published_at`, `changedAt` → `provider_changed_at`.
  `captured_at` stays OUR capture clock (red-team F2) so freshness remains
  meaningful, and a quote published after we observed it is refused at the
  boundary (`published_after_capture`).
* Per-reason skip counts are returned to the capture script.

### Join diagnostics (`scripts/picks_today.py`)

* `out_of_window` is now distinct from `date_mismatch`. `date_mismatch`
  means the join date failed closed (missing/unparseable provider kickoff) —
  a defect. `out_of_window` means a well-formed date outside the slate — an
  upcoming board, not a bug.
* New buckets: `market_unsupported`, `selection_unsupported`,
  `fixture_identity_missing`.
* New line: `donor unmapped vocabulary <source>: <token>=<count> …`. **This
  is how a feed's real market vocabulary gets enumerated without a live
  discovery call** — the raw token is already in the captured ledger.
* OddsPAPI gets the same per-reason buckets as the shadow donors, including
  rows rejected before the bundle was built (so a wholesale rejection can
  never print as `none=0`).
* `usable_rows` no longer counts rows with no fixture identity.

### Kickoff (`scripts/picks_today.py`, `src/edgefactory/notifier.py`)

Measured across the whole 2026-10-03 card, display-vs-SAST offsets are:

```
kickoff display offset [bare_hh:mm]:   -420m=35  -540m=3
kickoff display offset [dd-mm_hh:mm]:  -60m=13
kickoff display offset [iso]:          +0m=4
verdict: per-source (4 distinct offsets)
```

So the hypothesis of a systematic one-hour UK/SAST confusion is **wrong**:
only the `DD-MM, HH:MM` family is −60 minutes. A blanket offset would have
corrupted 38 of 55 rows. `kickoff_utc` was correct throughout.

* `kickoff_sast` is rendered from `kickoff_utc` and is exact. It replaces
  both incompatible feed renderings on the card.
* The raw `kickoff` text is **not** rewritten. The pre-match lead guard
  parses it and currently errs *early*; rewriting it to the true time would
  move the guard *later*, which is the one direction it must not move.
* `kickoff_offset_lines` prints the census every run, so the
  systematic-vs-per-source question is answered from data, not one fixture.

---

## Task 6 — credential-blocked sources (diagnostics only, no code fixes)

`zero_row_reason()` now derives a deterministic token from the status and
the observed HTTP code only. It cannot carry a key, a header, a URL or any
payload fragment.

| Source | Reported as | Operator action |
|---|---|---|
| `bzzoiro_odds` | `BLOCKED[reason=http_403_auth]` | check key/plan; three consecutive all-zero runs |
| `pinnapi_odds` | `[reason=valid_empty_http_200]` | **none** — authenticating and answering, just no events. Valid-empty, explicitly distinct from malformed/unavailable |
| `betminer` | `[reason=http_404_endpoint_contract]` | RapidAPI playground. `/matches/{date}` and `/value-bets/{date}` both 404. **Not probed live** — the 5/day budget belongs to the scheduled run |
| `sharpapi_odds` | `[reason=http_404_endpoint_contract]` | RapidAPI playground, then set `SHARPAPI_ENDPOINT` / `SHARPAPI_SPORT`. **No workflow edit required.** Do not send a `date` param unless the provider confirms it |

No live probe was made against any of the four.

### Workflow files

`.github/workflows/*` is **unchanged** — agent sessions lack the `workflows`
permission. Nothing in this repair needs a workflow edit: SharpAPI is
resolved entirely through the existing `SHARPAPI_ENDPOINT` / `SHARPAPI_SPORT`
secrets, so `docs/operator/daily.yml.proposed` needs no new entry either.

---

## What the next live run should print

```
donor join misses betbetter:  out_of_window=…, market_unsupported=…   (matched_rows>0)
donor join misses boggio:     selection_unsupported=…                 (matched_rows>0)
donor join misses oddspapi_odds: fixture_identity_missing=… | <real buckets>
donor unmapped vocabulary betbetter: unsupported_market:draw_no_bet=… …
kickoff display offset verdict: per-source (…)
```

The Bet Better market census is the one deliverable that still needs a live
run: the captured ledgers (`localdata/*_shadow_*.json`) are gitignored and
are not present in a fresh checkout, so the 687 raw strings could not be
enumerated offline. The `donor unmapped vocabulary` line is built precisely
so the next run enumerates them from the ledger it already holds.

**No donor match count is claimed here.** The offline dry run has no voter
sources and therefore no slate; the non-zero matched counts are asserted in
`tests/test_donor_join_repair.py` against realistic fixtures built from raw
provider vocabulary. Production numbers wait for a live run.

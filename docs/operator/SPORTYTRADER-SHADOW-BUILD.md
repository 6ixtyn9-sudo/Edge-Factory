# Verified shadow build: FutbolPronosticos and SportyTrader

**Observed:** 2026-10-02 UTC
**Mode:** shadow-live only; no consensus weight, pick-path dependency, or
staking/ticket effect. `scripts/auto_tickets.py` remains the sole staking owner.

## Build contract

### FutbolPronosticos

- `src/edgefactory/sources/futbolpronosticos.py` uses an honest user agent,
  one in-flight request, a bounded polite interval, a robots check, and aborts
  immediately on HTTP 429.
- The daily slate and `/pronostico-...` pages are parsed into fixture rows with
  home, away, date, 1X2, O1.5, U3.5, BTTS, exact-score fields and preserved
  structured percentages/odds where present.
- `localdata/futbolpronosticos_shadow_YYYY-MM-DD.json` is an append-replaced
  day snapshot with `raw` and `scored` counters. The daily source-health row
  repeats those counters and exposes `can_fetch_today`, `can_price`,
  `can_vote`, and `blocker`.
- There is no fetch of the source's 404 `/resultados` or
  `/historial-pronosticos` routes. Coverage is checked only against the
  existing warehouse-score/backfill facts; a mismatch is flagged in the
  snapshot and health contract. Winner grading remains independent of price
  freshness and source availability.
- The adapter is not in `SOURCES_*`, has zero consensus weight, and has no
  production enablement switch.

### SportyTrader

- `src/edgefactory/sources/sportytrader_odds.py` enforces one in-flight
  request, a polite interval, same-day HTML cache, `Retry-After` handling,
  429 cooldown/abort, allowed locale checks, and challenge detection. A
  Cloudflare `/cdn-cgi`/challenge response changes the run to
  `training_only`; no solver, proxy, browser bypass, or CAPTCHA workaround is
  attempted.
- The nine hard-blocked prefixes are `/en-gb/`, `/en-za/`, `/en-ng/`,
  `/en-in/`, `/fr-be/`, `/fr-ca/`, `/es-co/`, `/es-pe/`, and `/cdn-cgi/`.
- Named bookmaker rows are saved as
  `fixture/market/selection/odds/book/captured_at` in
  `localdata/sportytrader_odds_shadow_YYYY-MM-DD.json`. Health and run
  summaries expose `st_raw` and `st_matched`; `can_vote` remains false.
- The board is captured while `SPORTYTRADER_CORROBORATOR=off`. Only the
  default-off flag-gated integration can append these named prices to the
  existing price board. It never replaces the chosen price or changes pick
  grading.

A representative daily health fragment and run-summary fragment are:

```json
{
  "futbolpronosticos": {
    "can_fetch_today": true, "can_price": false, "can_vote": false,
    "raw": 1, "scored": 1, "blocker": null
  },
  "sportytrader_odds": {
    "can_fetch_today": true, "can_price": true, "can_vote": false,
    "st_raw": 1, "st_matched": 4, "blocker": null
  }
}
```

```text
Summary: ... shadow_fp_raw=1 shadow_fp_scored=1 st_raw=1 st_matched=4 ...
test_7pct eligible=66 gained=0 rate=0.0 max_deviation=7%
```

## Offline 7% evidence gate

Run from the repository root:

```text
PYTHONPATH=src python3 scripts/report_sportytrader_7pct.py --n 14 \
  --output docs/operator/SPORTYTRADER-7PCT-REPORT.json
```

The report reads only archived `picks_morning_YYYY-MM-DD.json` boards and
saved SportyTrader shadow ledgers. It does not fetch. The receipt for the
14-archive window on 2026-10-02 is:

```text
test_7pct eligible=66 gained=0 rate=0.0 max_deviation=7%
```

Therefore the integration recommendation is **remain off**. This is an
absence-of-evidence result, not a reason to loosen the 7% gate. Re-run after
shadow ledgers accumulate named-book rows; operator review is required before
changing `SPORTYTRADER_CORROBORATOR` to `on`.

## Offline receipts

```text
PYTHONPATH=src python -m pytest -q \
  tests/test_shadow_sources.py tests/test_sportytrader_report.py \
  tests/test_sportytrader_flag.py tests/test_source_health.py
18 passed in 0.16s
```

The fixtures are under `tests/fixtures/`; all tests are offline and assert
locale blocks, robots behavior, 429 abort, Cloudflare training-only behavior,
named-book capture, `raw/scored`, `st_raw/st_matched`, report math, and
flag-off byte identity.

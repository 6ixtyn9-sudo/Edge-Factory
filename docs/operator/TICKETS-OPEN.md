# Open small tickets (OP-01 T4)

Two fenced leftovers. Ticket (a) ships a contained fix + tests; ticket (b) is a
recommendation with evidence and **no code change**.

---

## (a) bzzoiro_odds — a 403/auth zero-row day must be redone

**Status: FIXED (fenced), tests added.**

### Symptom

The PR #21 tripwire reported `http=403` auth/plan-denied for `bzzoiro_odds` on
**2026-10-02 and 2026-10-03** while the bzzoiro *tips* feed kept working. Those
days nevertheless reached a terminal state and were never requested again.

### Root cause (code-level)

1. `src/edgefactory/sources/bzzoiro_odds.py::_fetch_url` is documented
   *"Fetch one URL, parse rows, and print diagnostics. **Never raises**"* — on
   an `HTTPError` it records the error and returns `(0, [])`.
2. `fetch_day` therefore returns `[]` and only *labels* the condition:
   `statuses <= {401, 403}` → `_DIAG["status"] = "auth"`,
   `quota_hint = "auth_or_quota"`. No exception leaves the adapter.
3. `scripts/local_backfill.py` treated any non-exception return as success:
   the `elif source_key.endswith("_odds"): print(... 0 rows)` branch fell
   straight through to `done.add(d.isoformat())`.

Net effect: **a plan-denied 403 was indistinguishable from an empty slate**,
the date entered `state_bzzoiro_odds.json:done`, and every later run skipped
it — a permanent hole produced by an access error, not by absent fixtures.

### Fix

`scripts/local_backfill.py` now asks the adapter before closing a zero-row day:

- new module-level `RETRYABLE_ZERO_ROW_STATUSES = {auth, quota, unavailable,
  blocked, error}` and `zero_row_retry_reason(mod)`;
- a zero-row day whose `diagnostics()["status"]` is in that set is **not**
  marked done — it is recorded in `failures` with
  `zero rows with status=auth http=403 quota_hint=auth_or_quota — not an empty
  slate; day stays retryable`, printed as `ZERO-ROW NOT DONE`, and the run
  exits non-zero (the existing retryable-failure contract);
- `status=empty` (an honest quiet calendar) still completes, so quiet days
  cannot turn into infinite retries;
- adapters without `diagnostics()` are completely unchanged.

Scope guard: capture/backfill state only. No crawl expansion, no new request
budget, no vote-weight change, no production re-mine.

### Tests

`tests/test_local_backfill.py`

- `test_auth_zero_row_day_stays_retryable` — 403/auth on 10-02 + 10-03 leaves
  `done == []` and writes both failure reasons;
- `test_quota_and_unavailable_zero_rows_also_stay_open`;
- `test_genuinely_empty_slate_with_diagnostics_still_completes`;
- `test_bzzoiro_odds_auth_zero_row_is_classified_retryable` — pins the real
  adapter's `status="auth"` contract the rule keys off.

### Operator step for already-poisoned days

Days closed *before* this fix are still in `done`. Re-open only the affected
range (no crawl expansion — these are days we were denied, not new days):

```
PYTHONPATH=src python3 scripts/backfill_bzzoiro_odds.py 2026-10-02 2026-10-03
```

That helper removes the range from `state_bzzoiro_odds.json:done` and retries
through the normal path. If the 403 persists, the entitlement question is real:
confirm whether the account's plan covers `/odds/best/` at all before any
further retry budget is spent (**no harder retrying, no alternate transport**).

---

## (b) soccervista — restore or drop

**Status: RECOMMENDATION ONLY. No code change in this bundle.**

### Recommendation

**DROP from the live capture group; RETAIN the adapter, tests and relay
allowlist entry as dormant.** Re-admit only on a fresh, reproducible
`VERIFIED-from-relay` receipt. Concretely, when the operator accepts this:
remove `soccervista` from the `forebet-resilience` source group in
`scripts/capture_daily.py`, leave `src/edgefactory/sources/soccervista.py`,
`tests/test_soccervista.py` and the `relay/` allowlist untouched. One
reversible line, no deletions.

### Evidence

| # | evidence | source |
|---|---|---|
| E1 | Every transport fails: the ladder is `urllib → curl_cffi impersonation → operator relays` (`soccervista.py:216-244`); when all rungs fail it raises `SoccerVista GET failed <url>: <errors>`. Observed classification: **`soccervista \| failed \| Homepage urllib/curl SSL transport failure; retryable`** | `HANDOVER.md` source-recovery table; `src/edgefactory/sources/soccervista.py` |
| E2 | Relay rung cannot widen the surface: the allowlist grants `www.soccervista.com` **`/` only — no query string** | `relay/README.md` |
| E3 | The source is structurally thin even when healthy: **TODAY ONLY**. The legacy dated pages (`soccer_games.php`, `next_matches.php`) are gone ("File not found") and the new day picker is JS-driven with no plain-GET archive URL → capture-forward only, no backfill is possible to repair the hole | `soccervista.py` module docstring |
| E4 | It carries **no probabilities and no final scores** — pick + odds + tips only; settlement must join a separate results donor | `soccervista.py` module docstring |
| E5 | It has **zero consensus weight today**: standing instruction is "do not add ProSoccer or SoccerVista to `picks_today.py` live voting lists" | `HANDOVER.md`, 2026-09-30 addendum |
| E6 | Hardening already consumed a red-team cycle (R3 per-transport shell rejection, redundant table-check removal) — the remaining failure is transport/edge, not parsing, so there is no cheap code fix left | `docs/operator/archive/PR15-RED-TEAM.md` |

### Why not "restore"

Restoring means buying transport access the restrictions forbid. The only
remaining levers after the relay are proxies, stealth browsers or CAPTCHA
work — **all prohibited**. The lawful lever, a cooperative relay fetch, is
already in the ladder and already failing. Spending further capture budget on
a today-only, score-less, zero-weight source that cannot be backfilled (E3)
is negative expected value against the bounded budget.

### Re-admission criteria (write these down, then stop thinking about it)

1. A fresh relay receipt showing `robots.txt` + a rendered predictions table
   (not a branded shell) — i.e. `VERIFIED-from-relay`, dated.
2. Seven consecutive successful daily captures in **shadow**, zero weight.
3. A proven settlement join against an independent results donor.
4. Only then: a normal consensus-candidate review. No fast path.

### Explicitly not done here

No code change, no capture-group edit, no deletion, no crawl. The decision is
the operator's; this ticket is the evidence package.

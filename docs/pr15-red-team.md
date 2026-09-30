# PR #15 red-team report — source availability recovery

Date: 2026-09-30  
Branch: `arena/01a0f1cf-edge-factory`  
Scope: hardening review for Forebet, SoccerVista, ProSoccer, PredictZ, WinDrawWin, Bzzoiro odds, relay security, and operator workflow artifacts.

## Explicit non-claims

Forebet production capture is **not proven fixed** until the operator deploys the Cloudflare Worker and runs the one-shot `forebet_getrs` probe. Prior Browser Run diagnostics saw interactive Turnstile. This branch adds a bounded, exact-allowlisted Browser Run operation and fail-closed adapter ladder, but it does not claim Forebet rows will land from Browser Run until the deployed Worker returns Forebet `[rows, meta]` JSON with `row_count > 0`.

## Red-team checklist

| item | status | evidence |
| --- | --- | --- |
| R1 Forebet honesty — Browser Run not proven | pass | This file's non-claims section; `relay/README.md` documents post-deploy probe requirement. `src/edgefactory/sources/forebet.py:242-295` treats Browser Run/Playwright failures as errors, not success. |
| R1 fail-fast on GHA | pass | `src/edgefactory/sources/forebet.py:287-295` raises `GitHub direct transport skipped` after relay/browser paths fail in default GHA relay mode. Test: `tests/test_forebet.py:213`. |
| R1 days stay retryable on CF/challenge | pass | `src/edgefactory/sources/forebet.py:390-395` raises when all markets fail with no rows; `scripts/local_backfill.py:162-169` does not mark non-404 exceptions done. Test: `tests/test_forebet.py:77`. |
| R1 no paid solver/open proxy; exact getrs only | pass | Worker operation checks `allowedForebetGetrs` before launch: `relay/cloudflare-worker/src/forebet-browser.js:68-69`. Exact params/host/path enforced: `relay/cloudflare-worker/src/allowlist.js:50-64`. Tests: `relay/cloudflare-worker/test/allowlist.test.js:10`; `relay/cloudflare-worker/test/forebet-browser.test.js:82`. |
| R1 cannot live-probe deployed Worker here | gap, documented | Cloudflare Worker deployment/probe still requires operator action. A manual probe workflow now exists at `.github/workflows/forebet-getrs-probe.yml`, with a copy under `docs/operator/forebet-getrs-probe.yml.proposed`. |
| R2 ProSoccer candidate order | pass | `src/edgefactory/sources/prosoccer.py:250-274` tries deterministic URL first, then tomorrow, yesterday, weekday, base, index. Test: `tests/test_prosoccer.py:138`. |
| R2 NotServedYet vs genuine empty | pass | Out-of-window `candidate_urls` returns `[]`, while no matching in-window H1 raises `NotServedYet`: `src/edgefactory/sources/prosoccer.py:284-309`. Tests: `tests/test_prosoccer.py:120`, `tests/test_prosoccer.py:130`. |
| R2 local_backfill retryability; other empty done | pass | `scripts/local_backfill.py:156` marks successful returns done; `scripts/local_backfill.py:162-169` leaves non-404 exceptions open. Tests: `tests/test_local_backfill.py:29` and `tests/test_local_backfill.py:50`. |
| R2 no live-voting changes | pass | `scripts/picks_today.py` is not modified in this branch (`git diff --name-only` has no picks_today entry). |
| R3 SoccerVista per-transport shell rejection | fixed in red-team follow-up | `_get` only returns brand+table validated HTML: `src/edgefactory/sources/soccervista.py:73-84`, `src/edgefactory/sources/soccervista.py:215-241`. Tests: `tests/test_soccervista.py:212`, `tests/test_soccervista.py:232`. |
| R3 redundant post-_get table check | fixed in red-team follow-up | Removed redundant fetch_day brand/table checks; `fetch_day` starts parse/date work only after `_get` validated transport: `src/edgefactory/sources/soccervista.py:247-269`. Test: `tests/test_soccervista.py:164`. |
| R4 PredictZ/WinDrawWin exact allowlists | pass | Hosts and paths only: `relay/cloudflare-worker/src/allowlist.js:11-12`, `relay/cloudflare-worker/src/allowlist.js:84-90`. Tests: `relay/cloudflare-worker/test/allowlist.test.js:55`. |
| R4 adapter shape validation before parse | pass | PredictZ rejects invalid body before parse: `src/edgefactory/sources/predictz.py:32-53`. WinDrawWin rejects invalid body before parse: `src/edgefactory/sources/windrawwin.py:28-49`. Tests: `tests/test_predictz_windrawwin_relay.py:25-69`. |
| R5 no recurring cost | pass | No paid services added. Playwright path is disabled unless `EDGE_FACTORY_FOREBET_PLAYWRIGHT=1` and runner dependencies are manually installed. Code gate: `src/edgefactory/sources/forebet.py:100-109`. |
| R5 Browser Run bounded | pass | Default Browser Run only recent live dates in GHA auto mode: `src/edgefactory/sources/forebet.py:79-98`; serialized per-market when browser/playwright is enabled: `src/edgefactory/sources/forebet.py:326-342`. |
| R5 relay POST/token/allowlist | pass | Python relay uses POST token body and echoed URL validation: `src/edgefactory/sources/public_relay.py:33-53`. Worker entrypoint rejects non-POST/auth failure and checks allowlist: `relay/cloudflare-worker/src/index.js:15-43`. |
| R6 tests/contracts | pass | `PYTHONPATH=src /home/user/venv/bin/python -m pytest tests/ -q` → `771 passed in 13.18s`; `cd relay/cloudflare-worker && npm test` → `46` tests passed; `node --check` all Worker JS passed; `git diff --check` clean. |
| R7 operator actions accurate | fixed in red-team follow-up | Workflow changes are now present in `.github/workflows/daily.yml` and `.github/workflows/forebet-getrs-probe.yml`, with copy/paste mirrors under `docs/operator/`. GAS full file remains in PR body; `relay/google-apps-script/Code.gs` is the source of truth. |

## Workflow artifacts

The branch now carries the workflow changes directly, and also keeps copy/paste mirrors under `docs/operator/` for operator review:

- `.github/workflows/daily.yml` — daily workflow with optional Playwright install and bounded `BZZOIRO_ODDS_MAX_EVENTS` default.
- `.github/workflows/forebet-getrs-probe.yml` — optional manual `workflow_dispatch` probe for one Forebet date/market.
- `docs/operator/daily.yml.proposed` — complete replacement daily workflow mirror.
- `docs/operator/forebet-getrs-probe.yml.proposed` — manual probe workflow mirror.

## Verification commands run

```text
PYTHONPATH=src /home/user/venv/bin/python -m pytest tests/ -q
771 passed in 13.18s
```

```text
cd relay/cloudflare-worker && npm test
46 tests passed
```

```text
find relay/cloudflare-worker -path '*/node_modules' -prune -o -name '*.js' -print -exec node --check {} \;
# all Worker JS files parsed successfully
```

```text
git diff --check
# clean
```

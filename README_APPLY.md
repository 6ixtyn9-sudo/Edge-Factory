# Edge Factory — 2026-08-03 Patch Payload **v3** (deploy target)

v3 = v2 + one-line workflow env mapping (`ODDS_API_KEYS: ${{ secrets.ODDS_API_KEYS }}`
in daily.yml — without it the capture step soft-no-ops on every Actions run) +
README corrections (test counts). Gap was self-caught during the v2 deploy
dress rehearsal and is on record in HANDOVER addendum 6.

v2 = v1 + external red-team intake: 16/16 falsification targets CONFIRMED; both
required fixes applied (year-boundary kickoff parsing; atomic+flock'd quota/attempt
ledgers) with 4 new fail→pass tests (suite 14+6=20, all green). Two evidence
defects found in the review report itself are on record in HANDOVER addendum 5.

Base commit: `f91cdb9d308e4614cafa04d9607e7806efe72d54` (upstream HEAD, re-verified
unchanged at rehearsal time 2026-08-03).
Apply target: your real `Edge-Factory` clone (macOS, `/Users/apple`). Nothing here
has been pushed upstream yet.

## Contents

```
PATCHES_V3_2026-08-03.diff          unified diff vs f91cdb9 (review this first)
PAYLOAD_MANIFEST_V3_2026-08-03.sha256  sha256 of every shipped file — verify after applying
.env.example                     MODIFIED: The Odds API block (ODDS_API_KEYS ring, quota knobs)
.gitignore                       MODIFIED: un-ignore discovery ledger + theoddsapi state files
.github/workflows/daily.yml      MODIFIED: permissions=contents:write, 'Persist pipeline state to git'
                                 bot-commit step, ODDS_API_KEYS secret→env mapping
src/edgefactory/sources/__init__.py  MODIFIED: registers theoddsapi
src/edgefactory/sources/theoddsapi.py NEW: The Odds API adapter (shortlist-driven, key rotation ring,
                                    monthly budget, bzzoiro-schema-compatible rows)
scripts/capture_theodds.py       NEW: capture CLI (--self-test/--dry-run/--auto/--usage/--refresh-sports)
scripts/daily.py                 MODIFIED: capture_theodds_snapshot() hooked at 4 CLV capture points;
                                 sync_repo_state() git-pull at pipeline start; --heartbeat on official notify
scripts/notify_whatsapp.py       MODIFIED: discovery alerts suppress fixtures already in MAIN sent ledger;
                                 --heartbeat empty-slate ping (max 1/day); helper functions for tests
tests/test_theoddsapi.py         NEW: 14 tests (matching, parsing, budget, rotation ring,
                                 year-boundary + concurrency regression tests)
tests/test_notify_whatsapp.py    NEW: 6 tests (cross-ledger suppression, heartbeat, stable dedupe identity)
HANDOVER.md                      MODIFIED: addendums 1-6 — design log, live verification, gap-day
                                 analysis, red-team intake, deploy rehearsal + v3 record
```

NOT included (deliberately): `.env` (contains real API keys — never ships in a payload),
`localdata/` state, raw history CSVs, `.git`, workspace analysis artifacts.

## What each change is for (one line each)

| Area | File(s) | Why |
|---|---|---|
| Real-odds capture | `theoddsapi.py`, `capture_theodds.py` | Real-book h2h/totals prices for the frozen slate, pick-time + near-close → real CLV; audit-only, gates nothing |
| Key rotation | `theoddsapi.py` | 3 free keys, daily-rotated ring, auto-failover, per-key 480/mo budget (raw keys never leave .env/secrets) |
| Orchestration | `daily.py` | Established commands only (`--auto-run/--auto-once`); no new manual steps |
| Spam fix | `daily.yml`, `notify_whatsapp.py`, `.gitignore` | HEAD-restore was reverting sent ledgers every run → 3h re-send loop; git now single source of truth; backstop suppression |
| Local↔cloud parity | `daily.py` (`sync_repo_state`), `daily.yml` (bot commit + `ODDS_API_KEYS` env) | Local cadence starts from cloud-committed state; Actions can actually capture; laptop becomes optional |
| Missed days | `notify_whatsapp.py` (`--heartbeat`) | One quiet ping on empty days so silence is never ambiguous |

## Apply procedure (macOS)

```bash
cd /Users/apple/<your Edge-Factory clone>
git status                                  # commit or stash anything local first
git fetch origin && git rev-parse origin/main
#  ↑ MUST print f91cdb9d308e4614cafa04d9607e7806efe72d54 — if not, STOP (drift; re-base needed)

unzip -o ~/Downloads/edgefactory_patch_v3_2026-08-03.zip -d /tmp/ef-v3
git apply --check /tmp/ef-v3/PATCHES_V3_2026-08-03.diff && git apply /tmp/ef-v3/PATCHES_V3_2026-08-03.diff
shasum -a 256 -c /tmp/ef-v3/PAYLOAD_MANIFEST_V3_2026-08-03.sha256   # expect 11 × OK

PYTHONPATH=src python3 -m pytest tests/test_theoddsapi.py tests/test_notify_whatsapp.py -q   # 20 passed
PYTHONPATH=src python3 scripts/capture_theodds.py --self-test        # PASS

git add -A && git commit -m "feat: theoddsapi real-odds capture (3-key ring) + WhatsApp dedupe + cloud state persistence + heartbeat (v3)" && git push
```

## REQUIRED post-push step (the one manual action left)

1. Repo → **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `ODDS_API_KEYS`
   - Value: your comma-separated 3-key ring (owner holds values; same string as the local `.env`)
2. Optional local capture: copy the “The Odds API” block from `.env.example` into your
   local `.env` and fill in the keys. Never commit `.env`.
3. Within 3 h: confirm a commit by `github-actions[bot]` (“chore: persist pipeline state …”)
   appears on main, and `localdata/theoddsapi_usage.json` shows credits spent > 0.
4. Tomorrow morning: exactly ONE morning WhatsApp message (or one heartbeat ping if the
   slate is empty), zero repeated fixture pushes intraday.

## Reviewer checklist (if a second pair of eyes ever applies this)

1. `git apply --stat PATCHES_V3_2026-08-03.diff` then `--check` before applying to a scratch branch.
2. After applying: `shasum -a 256 -c PAYLOAD_MANIFEST_V3_2026-08-03.sha256` (paths are repo-relative).
3. Run offline suites: `PYTHONPATH=src python -m pytest tests/test_theoddsapi.py tests/test_notify_whatsapp.py -q` → **20 passed expected**.
4. `PYTHONPATH=src python scripts/capture_theodds.py --self-test` → PASS expected.
5. Confirm no secrets in payload (scan for the three 32-char key strings; `.env` is intentionally absent).
6. Focus areas for red-team:
   - `_get_json` rotation semantics (`src/edgefactory/sources/theoddsapi.py`) — ring failover, charge-after-success, exhausted-key ledger.
   - `plan_auto` timing windows (`scripts/capture_theodds.py`) — first vs close snapshot logic, retry cooldowns.
   - Workflow 'Persist pipeline state to git' step — rebase/push retry loop on a shared branch.
   - `sync_repo_state()` — runs on EVERY local pipeline start; disabled via `EDGE_FACTORY_GIT_SYNC=0`.
   - Heartbeat: verify it can only ever send 1/day (marker in sent ledger) and never on intraday paths.
7. Live-verified evidence (2026-08-03) is documented in HANDOVER addendum 1-2: 4 credits spent,
   server counters match local ledger, Halmstad–Sirius priced across 21 books, Ie2 correctly unmatched.

## Env vars added (Actions secrets to set)

- `ODDS_API_KEYS` — comma list of the 3 keys (**required**, now actually consumed by the workflow)
- optional: `ODDS_API_CLOSE_WINDOW_MIN` (45), `ODDS_API_MARKETS` (h2h,totals), `ODDS_API_REGIONS` (eu), `ODDS_API_MONTHLY_BUDGET` (480), `EDGE_FACTORY_GIT_SYNC` (1 locally / unset in CI), `EDGE_FACTORY_HEARTBEAT` (1)

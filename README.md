# Edge Factory

Football prediction capture → DuckDB research and certification → guarded picks
→ frozen Main/ENH tickets → settlement, monitoring and notifications.
CSV/DuckDB are the analytical inputs; Supabase is a read model, not a financial
source of truth. Research results are not evidence of executable betting returns.

## Start here

| Need | Guide |
|---|---|
| Read the card, understand modes and run safely | [Operator handbook](docs/operator/README.md) |
| Source roles, quote admission, quotas and collection permission | [Sources](docs/operator/SOURCES.md) |
| Missing history, cache conflicts, receipt shards or report recovery | [Recovery and storage](docs/operator/RECOVERY.md) |
| Re-mining, frozen ML guardrails and activation boundaries | [Research](docs/operator/RESEARCH.md) |
| Regulation-only results and bank-history interpretation | [Settlement](docs/operator/SETTLEMENT.md) |
| Audit provenance and retained historical evidence | [Dated claims](docs/operator/DATED-CLAIMS.md) |

## Local development

Python **3.11+** is required; the installed Actions workflow uses **3.13**.
From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src:scripts:tests:. python -m pytest tests/ -q
```

Keep real credentials only in ignored local configuration or the appropriate
Actions secrets. `.env` is loaded by the application. Never paste credentials
into commits, fixtures, issues or logs. The test suite isolates provider and
notification environments; a passing suite is not a production dispatch.

**Do not run the daily pipeline just to check an installation.** It can fetch
providers, alter operational state, freeze/stake recommendations and notify.
Use tests and temporary data directories for development. See the handbook
before running any stateful command.

## Repository map

- `src/edgefactory/` — adapters, identity, price policy, settlement and safeguards.
- `scripts/` — the existing capture, warehouse, miner, daily, ticket and audit CLIs.
- `Config/` — reviewed identity and settlement facts/configuration.
- `localdata/` — financial state, frozen receipts and runtime/captured evidence;
  some large dependencies are intentionally cache/artifact-only.
- `.github/workflows/` — installed workflows; **the only workflow YAML authority**.
- `docs/operator/` — maintained guides and deliberately retained evidence/specs.
- `handoff/` — retained provider fixtures and cited proof outputs, not agent tasks.
- `relay/` — optional allowlisted source relays; [deployment/security guide](relay/README.md).
- `tests/` — offline regression and safety contracts; `supabase/` — read-model schema.

## Change discipline

Inspect `git status` and stage explicit code/document paths. Do not sweep runtime
state into a manual commit with `git add .` or `git add -A`. Do not discard
`localdata/`, choose a blanket conflict side, or reset banks to make a pull/run
succeed: cache-only evidence and booked finance may not regenerate. Preserve
both versions and follow the recovery guide. Never rewrite a frozen decision
or silently change selection, staking, source permission or certification gates.

Keep these guides current instead of adding dated handovers, agent prompts,
copy/paste workflow files or append-only change logs. Superseded work orders are
in Git history; retained evidence is indexed in the dated-claims guide.

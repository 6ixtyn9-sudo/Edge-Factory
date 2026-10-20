# Post-Forebet history recovery and approved enhancement rebuild

## Evidence and status

The healthy run 39371954018 was **research-only**. Six complete unmasked
candidate objects are preserved in `post-forebet-research-39371954018.json`.
They do not constitute activated contracts or untouched forward validation.
The two-source threshold-55 rule is unanimous **1X2**, not home-only.
At implementation time the main registry had **zero** post-Forebet contracts.

The historical cache `localdata-v2-39371954018` (cache ID 9201685918) is the
explicit reference. No fallback cache is accepted. Recovery stages the current
whole state outside `localdata`, restores the exact donor at the original cache
path/version, unions only allowlisted raw prediction CSVs (including flat
Statarea/Zulubet), and restores every other current file. Forecast/result
conflicts survive for the existing miner's quarantine. Old tickets, banks,
registries, warehouses, prices and ledgers never migrate from the donor.
A compressed fixture-key high-water mark stays **ignored/cached**, not in Git;
the small committed receipt is a completeness receipt, **not certification**.
Missing/truncated history blocks subsequent mining/publication. No capture,
provider call, threshold relaxation, ML fallback or second miner is introduced.

The existing miner must re-mine and activate by exact predicate/stat recreation.
Assay and decay then run on that registry. Activation starts in WATCH pending
untouched forward evidence. The approved current-day enhancement rebuild uses
cached execution boards and all competing markets; it never uses the old slate,
settles either lane, resets bank history, or overwrites a newer frozen card.
A no-plan/zero-active/missing-bank result persists an explicit **NO BET**, without
a lock or stake. Missing bank state is **not** reconstructed or initialized.
Only the already approved none-placed date is eligible for this rebuild.

## Deployment

The GitHub App previously rejected workflow pushes for lack of `workflows`
permission. This document is **not an installed second workflow**. Replace the
existing `.github/workflows/daily.yml` with the complete YAML below, then run
that workflow on `main` with mode **recover_and_rebuild**. The helper code must
be merged first. Do not select `official_morning`: it does not restore the lost
history and would perform a heavyweight capture. If the exact reference cache
has expired/misses/corrupts, recovery fails closed and current finance is restored;
do not substitute a random cache or lower the sanity/statistical gates.

Cache/git publication is now success-only, not `always()`; the cancelled run
39404758959 previously saved a newer cache despite an incomplete pipeline.
Read the run summary for actual registry contract IDs, full train/validation
stats and the replacement/NO BET artifact. A failed attempt is not activation.
Artifacts remain supplementary, not the operator's required readout channel.

## Complete replacement for the EXISTING daily.yml

```yaml
name: Autonomous Edge Factory 3-Hour Service

on:
  workflow_dispatch:
    inputs:
      mode:
        description: 'Execution Mode'
        required: false
        default: 'auto'
        type: choice
        options:
          - auto
          - official_morning
          - forecast_refresh
          - clv_only
          - remine_only
          - recover_and_rebuild

permissions:
  contents: write

concurrency:
  group: edge-factory-main
  cancel-in-progress: false

jobs:
  run-autonomous-agent:
    runs-on: ubuntu-latest
    timeout-minutes: 360

    env:
      SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
      SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
      BZZOIRO_TOKEN: ${{ secrets.BZZOIRO_TOKEN }}
      RAPIDAPI_KEY: ${{ secrets.RAPIDAPI_KEY }}
      RAPIDAPI_KEYS: ${{ secrets.RAPIDAPI_KEYS || '' }}
      PINNAPI_KEY: ${{ secrets.PINNAPI_KEY }}
      BZZOIRO_ODDS_MAX_EVENTS: ${{ secrets.BZZOIRO_ODDS_MAX_EVENTS || '20' }}
      EDGE_FACTORY_RELAY_URLS: ${{ secrets.EDGE_FACTORY_RELAY_URLS }}
      EDGE_FACTORY_RELAY_TOKEN: ${{ secrets.EDGE_FACTORY_RELAY_TOKEN }}
      EDGE_FACTORY_FOREBET_BROWSER: "off"
      TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
      TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
      ODDS_API_KEYS: ${{ secrets.ODDS_API_KEYS }}
      ODDS_API_REGIONS: ${{ secrets.ODDS_API_REGIONS || 'eu' }}
      ODDS_API_MARKETS: ${{ secrets.ODDS_API_MARKETS || 'h2h,totals,team_totals' }}
      ODDS_API_TOTAL_POINTS: ${{ secrets.ODDS_API_TOTAL_POINTS || '1.5,2.5,3.5,4.5' }}
      ODDS_API_MONTHLY_BUDGET: ${{ secrets.ODDS_API_MONTHLY_BUDGET || '480' }}
      ODDS_API_CLOSE_WINDOW_MIN: ${{ secrets.ODDS_API_CLOSE_WINDOW_MIN || '45' }}
      SHARPAPI_SPORT: ${{ secrets.SHARPAPI_SPORT || 'soccer' }}
      SHARPAPI_ENDPOINT: ${{ secrets.SHARPAPI_ENDPOINT || '/api/v1/odds' }}
      SHARPAPI_LIMIT: ${{ secrets.SHARPAPI_LIMIT || '1000' }}
      SHARPAPI_LEAGUE: ${{ secrets.SHARPAPI_LEAGUE }}
      SHARPAPI_KEY: ${{ secrets.SHARPAPI_KEY }}
      ODDSPAPI_API_KEYS: ${{ secrets.ODDSPAPI_API_KEYS }}
      EDGE_FACTORY_ODDSPAPI_PRICES: ${{ secrets.EDGE_FACTORY_ODDSPAPI_PRICES || '1' }}
      ODDSPAPI_MAX_FIXTURES: ${{ secrets.ODDSPAPI_MAX_FIXTURES || '70' }}
      EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS: '90'
      EDGE_FACTORY_CARD_ENRICH_RESERVE: '20'
      # Enhancement lane (PR #61): the enhancement slip is generated, frozen
      # and settled on its own state. Unset/removing this line reverts the
      # daily run to exactly its previous behaviour - the lane then does
      # nothing at all (no artifact, no state file).
      EDGE_FACTORY_ENH_BOARD: '1'
      EDGE_FACTORY_ENH_COHORT_PARITY: '1'
      TZ: 'Africa/Johannesburg'

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install "supabase>=2.4,<3"

      - name: Restore localdata State (Cache)
        uses: actions/cache/restore@v4
        with:
          path: localdata
          key: localdata-v2-${{ github.run_id }}
          restore-keys: |
            localdata-v2-

      - name: Restore committed data (override stale cache)
        run: |
          set -e
          python3 scripts/phase5_persistence.py restore
          echo "certified edges present: $(python3 -c "import json;d=json.load(open('localdata/edges_consensus.json'));print(sum(1 for e in d.get('edges',[]) if e.get('status')=='certified'))" 2>/dev/null || echo n/a)"

      - name: Invalidate the approved unplaced enhancement ticket
        if: inputs.mode == 'recover_and_rebuild'
        run: PYTHONPATH=src python3 scripts/auto_tickets.py --enhancements --apply-unplaced-resets

      - name: Stage current state before historical restore
        id: history_stage
        if: inputs.mode == 'recover_and_rebuild'
        run: python3 scripts/phase5_persistence.py history-prepare

      - name: Restore exact healthy prediction-history cache
        id: history_reference
        if: inputs.mode == 'recover_and_rebuild'
        uses: actions/cache/restore@v4
        with:
          path: localdata
          key: localdata-v2-39371954018

      - name: Merge prediction history and restore current operational state
        if: always() && inputs.mode == 'recover_and_rebuild' && steps.history_stage.outcome == 'success'
        run: python3 scripts/phase5_persistence.py history-recover --reference-hit "${{ steps.history_reference.outputs.cache-hit || 'false' }}"

      - name: Verify retained prediction history before mining or publication
        run: python3 scripts/phase5_persistence.py history-check

      - name: Recover, validate, activate and rebuild enhancement ticket
        id: recovery
        if: inputs.mode == 'recover_and_rebuild'
        run: |
          set -euo pipefail
          PYTHONPATH=src python3 scripts/build_warehouse.py
          PYTHONPATH=src python3 scripts/mine_consensus.py --activate
          if python3 -c "import json,sys; d=json.load(open('localdata/edges_consensus.json')); sys.exit(0 if d.get('operating_contract') == 'post_forebet_v1' and any(e.get('contract_schema') == 'post_forebet_v1' and e.get('status') == 'certified' for e in d.get('edges', [])) else 1)"; then
            PYTHONPATH=src python3 scripts/assay_purity.py
            PYTHONPATH=src python3 scripts/decay_monitor.py
          fi
          PYTHONPATH=src python3 scripts/auto_tickets.py --enhancements --rebuild-unplaced
          PYTHONPATH=src python3 scripts/auto_tickets_grade.py --lane enh --no-settle
          python3 scripts/phase5_persistence.py history-check

      - name: Contract and replacement evidence in run summary
        if: always() && inputs.mode == 'recover_and_rebuild'
        env:
          RECOVERY_OUTCOME: ${{ steps.recovery.outcome }}
        run: |
          python3 - <<'PY_EVIDENCE'
          import json, os
          from datetime import date
          from pathlib import Path
          root = Path('localdata')
          root.mkdir(exist_ok=True)
          outcome = os.environ.get('RECOVERY_OUTCOME', 'skipped')
          slip = root / f'autobets_enh_tickets_{date.today().isoformat()}.txt'
          if outcome != 'success' and not slip.exists():
              slip.write_text('NO BET — recovery/validation incomplete; no replacement authorised.\nNo stake committed by this attempt.\n')
          with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as out:
              out.write(f'## Recovery and enhancement rebuild: {outcome}\n')
              out.write('Current registry snapshot follows; research passes alone are not activation.\n')
              try:
                  registry = json.loads((root / 'edges_consensus.json').read_text())
                  edges = [e for e in registry.get('edges', []) if e.get('contract_schema') == 'post_forebet_v1']
                  out.write(f"Post-Forebet contracts: {len(edges)}; certified: {sum(e.get('status') == 'certified' for e in edges)}\n")
                  for edge in edges:
                      evidence = {k: edge.get(k) for k in ('contract_id', 'research_rule', 'status', 'sources', 'strategy', 'threshold', 'activated_as_of', 'train', 'valid', 'decay')}
                      out.write('```json\n' + json.dumps(evidence, indent=2) + '\n```\n')
              except (OSError, ValueError) as error:
                  out.write(f'Registry unavailable: {type(error).__name__}\n')
              if slip.exists():
                  out.write('### Enhancement artifact (a newer frozen replacement is never overwritten)\n```text\n' + slip.read_text() + '\n```\n')
          PY_EVIDENCE

      - name: Execute Autonomous Smart Schedule
        if: inputs.mode != 'recover_and_rebuild'
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ] && [ "${{ inputs.mode }}" != "auto" ]; then
            echo ">>> Executing explicit manual mode: ${{ inputs.mode }}"
            if [ "${{ inputs.mode }}" = "official_morning" ]; then
              PYTHONPATH=src python3 scripts/daily.py --force-repick
            elif [ "${{ inputs.mode }}" = "forecast_refresh" ]; then
              PYTHONPATH=src python3 scripts/daily.py --forecast-refresh
            elif [ "${{ inputs.mode }}" = "clv_only" ]; then
              PYTHONPATH=src python3 scripts/daily.py --clv-only
            elif [ "${{ inputs.mode }}" = "remine_only" ]; then
              # Use restored production data, with no capture, pricing,
              # tickets, notification, model promotion or state publication.
              PYTHONPATH=src python3 scripts/build_warehouse.py
              PYTHONPATH=src python3 scripts/mine_consensus.py
            fi
          else
            PYTHONPATH=src python3 scripts/daily.py --auto-once
          fi

      # Enhancement lane, after the board this run produced (its prices come
      # from the day's captures). Main-lane command semantics: the run first
      # SETTLES every open enhancement slip on the shared lifecycle, then
      # builds the day's 2-leg acca card exactly as autobets does and
      # freezes it on the first run at/after 09:00 SAST (a run before that
      # prints a DRAFT and freezes later). A frozen day re-prints unchanged
      # (write-once; --force cannot rewrite it) and a day that cannot form
      # an acca writes NO card and NO lock. Advisory: it can never fail the
      # daily run.
      - name: Enhancement tickets (generate/freeze)
        if: inputs.mode != 'remine_only' && inputs.mode != 'recover_and_rebuild'
        continue-on-error: true
        run: |
          PYTHONPATH=src python3 scripts/auto_tickets.py --enhancements

      # NEW: enhancement performance report. Runs after the step above has
      # settled and saved the enhancement state, and writes
      # localdata/autobets_enh_performance.txt/.json. Advisory, like the step
      # above: it can never fail the daily run.
      - name: Enhancement performance report
        if: inputs.mode != 'remine_only' && inputs.mode != 'recover_and_rebuild'
        continue-on-error: true
        run: |
          PYTHONPATH=src python3 scripts/auto_tickets_grade.py --lane enh

      - name: Phase 5 K-contract coverage (read-only diagnostic)
        if: always() && inputs.mode != 'remine_only'
        continue-on-error: true
        run: |
          PYTHONPATH=src python3 scripts/fit_phase5_candidate.py --explain || true

      - name: Final history completeness publication gate
        if: inputs.mode != 'remine_only'
        run: python3 scripts/phase5_persistence.py history-check

      - name: Persist localdata State (Cache)
        uses: actions/cache/save@v4
        if: success() && inputs.mode != 'remine_only'
        with:
          path: localdata
          key: localdata-v2-${{ github.run_id }}

      - name: Persist pipeline state to git (single source of truth)
        if: success() && inputs.mode != 'remine_only'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          python3 scripts/phase5_persistence.py persist --run-id "${{ github.run_id }}"

      - name: Upload Pick Ledgers & Reports as Artifacts
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: EdgeFactory-Reports
          path: |
            localdata/*.txt
            localdata/*.json
            localdata/*.md
            localdata/phase5_shadow/**
            localdata/phase5_activation/**
            localdata/phase5_reconciliation/**
          retention-days: 7

      - name: Upload Scored-Candidate Audit Ledgers
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: Scored-Candidate-Audit-${{ github.run_id }}
          path: |
            localdata/scored_candidate_shadow_*.jsonl
          if-no-files-found: ignore
          retention-days: 30

  regression-tests:
    name: Regression tests (flag, never gate)
    runs-on: ubuntu-latest
    timeout-minutes: 30

    permissions:
      contents: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: pytest
        run: PYTHONPATH=src python3 -m pytest tests/ -q

```

# Round-2 §3 flag-gate proof bundle (2026-10-12)

All raw output below is reproduced by `prove_flag_gate.py` plus the commands in
this file. No value here was typed by hand from a summary: the ledger is built
by the module's own writer from the archived market pages
(`handoff/live_2026-10-12/ou_lKAT82nf.json`, `bts_tW4rOkzg.json`), and the
board/field values come from the pipeline's own `load_prices_index` +
`attach_enhancement_price` and the lane's own `enhancement_legs` +
`render_enhancement_tickets`.

## Setup

    rm -rf /tmp/gate_proof /tmp/base_wt
    git worktree add --detach /tmp/base_wt d2f235b          # pre-stage-1 code
    mkdir -p /tmp/gate_proof
    git archive HEAD localdata | tar -x -C /tmp/gate_proof   # committed data only
    PYTHONPATH=src .venv/bin/python prove_flag_gate.py ledger \
        --root /tmp/gate_proof --archived ../live_2026-10-12
    # probe board = one/two real board picks' shape, identity rewritten to the
    # ledger fixtures and labelled as a probe (probe_board_picks.json)

## Runs

    PYTHONPATH=/tmp/base_wt/src .venv/bin/python prove_flag_gate.py attach \
        --root /tmp/gate_proof --mode baseline --out /tmp/gate_proof/board.baseline.json
    PYTHONPATH=src .venv/bin/python prove_flag_gate.py attach \
        --root /tmp/gate_proof --mode off  --out /tmp/gate_proof/board.off.json
    PYTHONPATH=src .venv/bin/python prove_flag_gate.py attach \
        --root /tmp/gate_proof --mode on   --out /tmp/gate_proof/board.on.json
    PYTHONPATH=src .venv/bin/python prove_flag_gate.py slip \
        --board /tmp/gate_proof/attached/picks_today.json.on.json \
        --scripts scripts --root /tmp/gate_proof --out /tmp/gate_proof/slip.today.on.txt

## Results

| file | what it is |
|---|---|
| `ledger.summary.txt` | the schema-2 ledger as written by the real writer: `ou` columns `[Over, Under]`, lines `0.50…4.50` + the page's phantom `ou` line, 6 rows, BetMGM.us only; `bts` columns `[Yes, No]`, 3 books |
| `ledger.betexplorer_match_detail_2026-10-12.json` | that ledger verbatim |
| `board.baseline.json` vs `board.off.json` | **empty diff** — flag-off equals the pre-stage-1 code byte-for-byte |
| `board.on.json`, `delta.diff` | the measured delta: 12 BetExplorer pairs appear; 0 of the 41 real board picks change (no board fixture is in the ledger); the 2-pick probe board gains one price (5.00 @ BetMGM.us) |
| `slip.probe.off.txt` / `slip.probe.on.txt` | the card delta on the probe board: `[NO BET] … no price captured` becomes `[ENH #1] @5.00 — stake 25.0% of capital` + `… floor 3.30 · BetMGM.us` |
| `slip.probe2.on.txt` | fire vs refuse through the lane: `@5.00 … floor 3.30` fires; `@1.57 … below floor 1.85 — no bet` |
| `slip.today.off.txt` vs `slip.today.on.txt` | **empty diff** — the committed board's cards are unchanged by the flag |
| `freeze.first.txt` | first `--enhancements --today --date 2026-10-12`: freezes `FROZEN AT 10:52 - FINAL` |
| `freeze.force.txt`, `real.second.txt` | **finding**: the second invocation crashes — `KeyError: 'accas'` at `settle_open_slips`, because the lane writes `open_slips` entries with `tickets` while the shared settle path reads `accas` |
| `real.plain.txt` | plain `--enhancements` (what `docs/operator/enhancement-lane.yml.proposed` runs) skips settle and reprints the frozen slip |
| `freeze.state_excerpt.txt` | the state as written: `frozen_by_date: [2026-10-12]`, open slip keys `date/staked_pct/tickets` |

## Standings at the time of the run (drift expected)

* `HANDOFF` harness: `prove_flag_gate.py`
* board inputs: `localdata/picks_today.json` (14), `picks_2026-10-12.json` (14),
  `picks_morning_2026-10-12.json` (13) at `900d741`, plus the labelled probe.
* the freeze runs happen in scratch worktrees (`/tmp/gate_wt`, `/tmp/gate_wt2`);
  no real state was written.

# Round-3 §5 proof bundle — the enhancement lane bets 2-leg accas (2026-10-12)

Every value below is raw output, reproduced by the printed command at local
HEAD `d6080f6` (`c453119` settle on the shared lifecycle → `34fbf17` accas, same
shape and lifecycle as autobets → `d6080f6` the settle writes the lane's own
state), on top of the capture patch chain `e93507b` → `900d741` → `e616f32`.
Nothing is pushed: PR #61 is still open (§5 / B-3).

The lane runs for the proofs happened in disposable worktrees
(`/tmp/r3b` for the freeze/settle pair, a temp `localdata/` for the pairing
driver) — never against the repository's own `localdata/`.

## Files

| file | what it is |
|---|---|
| `proof1_frozen_entry.txt` | §5(1): the frozen entry's keys and shape — `open_slips[0]` = `{date, accas, staked_pct}`, `accas[0]` = `{legs, odds, stake_pct}`, legs carry the lane's evidence |
| `proof2_run1_freeze.txt` | §5(2) run 1: bare `--enhancements` builds and freezes (`FROZEN AT 11:29 - FINAL`) |
| `proof2_run2_settle.txt` | §5(2) run 2: the same command settles the frozen card and re-prints it |
| `proof2_post_state.txt` | §5(2): bank `119.375` = 100 + (returned 44.375 − staked 25.0), `history` grew to 1, `open_slips` emptied, the main file was never created |
| `proof2_before_fix_lane_state_did_not_move.txt` | the defect §5(2) caught on its first run: the settle wrote the **main** lane's state file and left the lane's own file at its pre-settle numbers (fixed in `d6080f6`) |
| `proof3_pairing.txt` | §5(3)(4)(5): 4 eligible → 2 accas barbell (1st+4th, 2nd+3rd); 3 → 1 acca + `left over` line; 1 → `NO BET — only 1 eligible leg(s), need 2 for an acca`; same-fixture duplicate dropped and named; lane plan == main plan stakes |
| `proof4_politeness_census_detail.txt` | §4.5 / §2.2: `25 passed` across the politeness + detail files, every test named |
| `proof5_live_pages_v1_v8.txt` | §4 V1–V8 over the committed live pages, plus the bts-page structural audit |
| `proof6_flag_off_identity.txt` | §5(6) / §3: flag-off byte-identity vs pre-Stage-1 code, the measured flag-on delta, and the lane card through the flag |
| `proof6_ledger.txt` | the schema-2 ledger `prove_flag_gate.py ledger` builds from the archived pages |
| `proof7_full_suite.txt` | §5(7): the full suite line |
| `proof8_state_migration_b5.txt` | §5(8) / B-5: no old `tickets`-shaped lane state exists to delete |

## Reproduction (commands, repo root unless noted)

    # §5(2) — two consecutive runs of the wired command, scratch worktree
    git worktree add --detach /tmp/r3b <sha>
    cd /tmp/r3b                     # seed localdata/picks_today.json (4 fixtures) and
                                    # localdata/settled_results.json (4 scores), then:
    EDGE_FACTORY_ENH_BOARD=1 PYTHONPATH=src <repo>/.venv/bin/python scripts/auto_tickets.py --enhancements

    # §5(3)(4)(5) — repeat a case: python /tmp/r3b/demo_pairing.py {4,3,1,dup}
    #   (runs the real CLI entry point via at.main() with at.LOCALDATA pointed at a temp root)

    # §5(6) / §3 — the round-2 harness, re-run at round-3 HEAD
    cd handoff/flag_gate_2026-10-12
    PYTHONPATH=/tmp/base_wt/src <repo>/.venv/bin/python prove_flag_gate.py attach --root $W --mode baseline --out $W/board.baseline.json
    PYTHONPATH=<repo>/src      <repo>/.venv/bin/python prove_flag_gate.py attach --root $W --mode off      --out $W/board.off.json
    PYTHONPATH=<repo>/src      <repo>/.venv/bin/python prove_flag_gate.py attach --root $W --mode on       --out $W/board.on.json
    diff -q $W/board.baseline.json $W/board.off.json        # empty
    diff    $W/board.off.json $W/board.on.json              # the delta

    # §5(7) — the suite
    PYTHONPATH=src .venv/bin/python -m pytest tests/ -q -p no:randomly

`prove_flag_gate.py`'s `slip` mode was updated to the round-3 render signature
(it now computes the plan with the lane's own `plan_day` call before rendering);
`ledger`/`attach` are unchanged. The `board.baseline.json` / `board.off.json` /
`board.on.json` / `delta.diff` / `slip.*.txt` files in this bundle stay in the
round-2 bundle directory where the README's commands write them.

## Findings

1. **The settle used to write the wrong state file.** The first §5(2) run
   announced `settled 2026-10-12 acca @3.55 legs=['win','win']: bank 131.9%`
   and then changed nothing in the lane's own state — because
   `settle_open_slips` ended in `save_state(st)` with no lane. Evidence:
   `proof2_before_fix_lane_state_did_not_move.txt` (the main file appeared with
   bank 119.375; the lane file still said 100.0 / open). Fixed in `d6080f6`
   (`save_state(st, lane)`) with a regression test that pins both halves: the
   lane file moves, the main file never appears.

2. **The flag's measured delta today is 0 board picks.**
   `proof6_flag_off_identity.txt`: `betexplorer_pairs` 0 → 12; priced legs
   `picks_today.json` 0 → 0, `picks_2026-10-12.json` 0 → 0,
   `picks_morning_2026-10-12.json` 0 → 0, probe board 0 → 2. No committed board
   fixture's market page is retained in the ledger (the ledger holds JS El Biar
   and Coventry — round 1's two fetched pages), so the *mechanism* is proven on
   the labelled probe board and the *board* number is honestly 0 today. The
   probe shows the same-fixture guard working on real ledger data: over_35
   (5.00, floor 3.30) and over_25 (2.55, floor 1.60) both clear, one is dropped
   as a duplicate, 1 eligible remains → `NO BET` on the card.

3. **The card is autobets' card.** `proof3_pairing.txt`: barbell pairing
   (1st+4th, 2nd+3rd), `stake 12.5% of capital (12.5% of free bank)` per acca,
   `deploying 25% of free bank today`, `+100% per cycle` notification line, the
   same four-key plan legs plus the lane's own `market/label/floor/price_book/
   shadow` — and the lane's plan is *identical* to the main lane's plan on the
   same pool (`lane plan == main plan` in every case), which is the B-6 guard.

4. **Rendering note (not a defect).** A leg that fires but cannot pair is
   counted (`NO BET — only 1 eligible leg(s)`) but not printed with its
   evidence; the main lane's NO BET card also prints a count rather than the
   qualifying legs. The audit ladder prints only refused legs.

5. **Page integrity.** The bts page is 21,303 bytes with balanced
   table/tbody/tr tags (`proof5_live_pages_v1_v8.txt`); the O/U page's V2/V7
   "failures" are the page's own phantom `ou` line — the 2.50 table is served
   under `tbody#best-odds-ou` while the other lines are `best-odds-<line>`. It
   is reported, never normalised, and prices are unaffected (`_be_line_market`
   asks for a named line).

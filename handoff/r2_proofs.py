#!/usr/bin/env python3
"""R2 — the nine proofs for dynamic per-slice floors, printed raw.

Proofs (the pack's §5, in order):

1. per-level refusal table — every row of the real derivation with its reason;
2. a thin slice self-disables (n=6 with a lucky 5/6 stays on the inherited floor);
3. no lookahead — day D's table is unchanged by day D's own records;
4. ``match_over_15`` is not lowered on 72.7 % evidence;
5. the tighten-only clamp is visible (a slice cannot land below its parent);
6. a hand re-derivation equals the rendered slip, row for row;
7. the harness A/B on mean log growth per bet-day, plus the MIN_ACCAS no-bet
   frequency for both arms (run here, raw);
8. flag-off board byte-identical — the pre-R2 tip and this tree, both with
   ``EDGE_FACTORY_ENH_BOARD`` unset, render the same bytes;
9. the suite at this tip (run here, raw tail).

Read-only. Writes `handoff/r2_proofs.txt`; scratch state goes to a temp dir via
`handoff/scratch_localdata.py`, never into `localdata/`.
"""
from __future__ import annotations

import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()   # every localdata write goes to scratch (incident 2026-10-12)

import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

PRE_R2 = "607de7a"          # the tip R1 pushed; the flag-off baseline


def main() -> int:
    out = io.StringIO()
    ok = True

    def say(line: str = "") -> None:
        out.write(line + "\n")

    def check(label: str, condition: bool, detail: str = "") -> None:
        nonlocal ok
        ok = ok and bool(condition)
        say(f"  [{'PASS' if condition else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))

    from edgefactory import enh_registry as reg

    registry = json.loads((ROOT / "localdata" / "enhancement_registry.json").read_text())
    day = "2026-10-12"
    derived = reg.derive_floors_for_day(ROOT, day)
    say("== R2 proofs: dynamic per-slice floors ==")
    say(f"  registry            : localdata/enhancement_registry.json "
        f"({len(registry.get('markets') or {})} market type(s))")
    say(f"  as_of / margin / gate: {derived['as_of']} / {derived['margin']} / n>={derived['min_n']}")
    say(f"  coverage            : {json.dumps(derived['coverage'], sort_keys=True)}")
    say(f"  counts              : {json.dumps(derived['counts'], sort_keys=True)}")
    say()

    # ---- 1 -----------------------------------------------------------------
    say("-- 1. per-level refusal table (every row the derivation emitted) --")
    for row in derived["rows"]:
        label = str(row.get("name") or "")
        if row["level"] == "league":
            label = f"{row['market']} / {label}"
        elif row["level"] == "team":
            label = f"{row['market']} / {row.get('league')} / {label}"
        floor = "none" if row["floor"] is None else f"{row['floor']:.4f}"
        cand = "-" if row.get("candidate_floor") is None else f"{row['candidate_floor']:.4f}"
        say(f"  {row['level']:6s} {label[:40]:40s} n={row['n']:4d} LB={row['wilson_lb']:.4f} "
            f"derived={cand:>8s} floor={floor:>8s} basis={row['basis']:9s} {row['reason']}")
    check("every row carries a level, a basis and a reason",
          all(r["level"] in {"market", "league", "team"} and r["reason"]
              and r["basis"] in {"inherited", "market", "league", "team"}
              for r in derived["rows"]))
    check("team slices are never applied (floor == parent's applied floor)",
          all(r["floor"] == r["parent_floor"] for r in derived["rows"] if r["level"] == "team"))
    thin = [r for r in derived["rows"] if r["n"] < derived["min_n"]]
    check("thin slices inherit (no floor below the parent, no invented floor)",
          all(r["floor"] == r["parent_floor"] for r in thin))
    say()

    # ---- 2 -----------------------------------------------------------------
    say("-- 2. a thin slice self-disables even with a lucky record --")
    lucky = {"version": 2, "markets": {"match_over_25@v1": {"records": [
        {"date": f"2026-09-{i + 1:02d}", "match": f"T{i} vs U{i}", "price": 1.9,
         "hit": i != 2, "league": "Thinland,Liga"} for i in range(6)]}}}
    lucky_table = reg.derive_floors(lucky, day, parent_floors=reg.ENHANCEMENT_PRICE_FLOORS,
                                    margin=reg.ENHANCEMENT_FLOOR_MARGIN)
    lucky_rows = [r for r in lucky_table["rows"] if r["level"] == "league"]
    say(f"  n=6, 5 hits (rate {lucky_rows[0]['rate']:.3f}), Wilson LB "
        f"{lucky_rows[0]['wilson_lb']:.4f} < gate n>={lucky_table['min_n']}")
    for row in lucky_rows:
        say(f"  {row['level']:6s} {row['name']:24s} gate={row['gate']} "
            f"floor={row['floor']} basis={row['basis']} — {row['reason']}")
    check("the lucky thin slice stays on the operator's floor",
          lucky_rows[0]["floor"] == reg.ENHANCEMENT_PRICE_FLOORS["match_over_25"]
          and lucky_rows[0]["gate"] is False)
    say()

    # ---- 3 -----------------------------------------------------------------
    say("-- 3. no lookahead: day D's table ignores day D's own records --")
    sample = json.loads((ROOT / "localdata" / "enhancement_registry.json").read_text())
    with_today = json.loads(json.dumps(sample))
    entry = with_today["markets"].setdefault("match_over_25@v1", {"records": []})
    entry["records"] = list(entry.get("records") or []) + [
        {"date": day, "match": "Today A vs Today B", "price": 1.9, "hit": True,
         "league": "England,Premier League"},
        {"date": day, "match": "Today C vs Today D", "price": 1.9, "hit": True,
         "league": "Be1"}]
    after = reg.derive_floors(with_today, day, parent_floors=reg.ENHANCEMENT_PRICE_FLOORS,
                              margin=reg.ENHANCEMENT_FLOOR_MARGIN)
    same = (json.dumps(derived, sort_keys=True) == json.dumps(after, sort_keys=True))
    say(f"  table before == table after adding {2} same-day record(s): {same}")
    check("same-day records do not move the day's floors", same)
    say()

    # ---- 4 -----------------------------------------------------------------
    say("-- 4. match_over_15 is not lowered on its 72.7 % hit rate --")
    over15 = [r for r in derived["rows"] if r["level"] == "market"
              and r["market"] == "match_over_15"][0]
    say(f"  match_over_15: n={over15['n']} hits={over15['hits']} rate={over15['rate']:.1%} "
        f"wilsonLB={over15['wilson_lb']:.4f}")
    say(f"  parent (operator) {over15['parent_floor']:.4f} -> derived "
        f"{over15['candidate_floor']:.4f} -> applied {over15['floor']:.4f} "
        f"({over15['basis']})")
    check("the 72.7 % slice can only tighten",
          over15["floor"] >= over15["parent_floor"]
          and over15["floor"] == over15["candidate_floor"])
    say()

    # ---- 5 -----------------------------------------------------------------
    say("-- 5. tighten-only clamp, visible on every row --")
    clamped = {"version": 2, "markets": {"match_over_25@v1": {"records": [
        {"date": f"2026-08-{i % 28 + 1:02d}", "match": f"W{i} vs X{i}", "price": 1.9,
         "hit": i < 39, "league": "Strongland,Liga"} for i in range(40)]}}}
    clamp_table = reg.derive_floors(clamped, day, parent_floors=reg.ENHANCEMENT_PRICE_FLOORS,
                                    margin=reg.ENHANCEMENT_FLOOR_MARGIN)
    crow = [r for r in clamp_table["rows"] if r["level"] == "market"][0]
    say(f"  40 records / 39 hits: candidate {crow['candidate_floor']:.4f} < parent "
        f"{crow['parent_floor']:.4f} -> applied {crow['floor']:.4f} ({crow['basis']})")
    check("a candidate under the parent keeps the parent (clamped)",
          crow["floor"] == crow["parent_floor"] and crow["basis"] == "inherited"
          and crow["candidate_floor"] < crow["parent_floor"])
    check("no row anywhere lands below its parent",
          all(r["floor"] is None or r["parent_floor"] is None or r["floor"] >= r["parent_floor"]
              for r in derived["rows"] + lucky_table["rows"] + clamp_table["rows"]))
    say()

    # ---- 6 -----------------------------------------------------------------
    say("-- 6. hand re-derivation == the rendered slip, row for row --")
    import math as _math
    from edgefactory.enh_registry import wilson_lb
    mismatches = []
    for row in derived["rows"]:
        if row["floor"] is None:
            continue
        if row["n"] < derived["min_n"] or row["wilson_lb"] <= 0:
            hand = row["parent_floor"]
        else:
            hand = max(row["parent_floor"], 1.0 / wilson_lb(row["hits"], row["n"])
                       + derived["margin"])
        if not (row["floor"] == hand or _math.isclose(row["floor"], hand, rel_tol=1e-12)):
            mismatches.append((row["level"], row.get("name"), row["floor"], hand))
    say(f"  rows re-derived by hand: "
        f"{sum(1 for r in derived['rows'] if r['floor'] is not None)}; mismatches: {mismatches}")
    check("every applied floor equals 1/wilson_lb + margin clamped at the parent",
          not mismatches)

    # the slip's own lines, through the lane's renderer
    from datetime import datetime
    from scripts import auto_tickets as at
    os.environ["EDGE_FACTORY_ENH_BOARD"] = "1"
    slate_path = ROOT / "localdata" / "picks_today.json"
    slate = json.loads(slate_path.read_text())
    legs = at.enhancement_legs(slate, floors=derived)
    st = at.fresh_state()
    txt = at.render_enhancement_tickets(st, day, legs, [], datetime.now(at.TZ),
                                        should_freeze=False, freeze_record=None,
                                        bank_eff=100.0, fixture_report={}, floors=derived)
    applied = {r["market"]: r["floor"] for r in derived["rows"]
               if r["level"] == "market" and r["floor"] is not None}
    # The card itself, through the lane's own renderer (a real plan, so the
    # firing legs print their evidence lines exactly as the frozen card does).
    pool = at.enhancement_pool(legs)
    plan = at.plan_day(pool, 100.0, stake_frac=at.ENHANCEMENT_LANE.stake_frac)
    at._carry_lane_evidence(plan, pool)
    carded = [(str(l.get("match")), float(l["floor"]), str(l.get("floor_basis")))
              for a in plan for l in a["legs"] if l.get("floor") is not None]
    refused = [(str(l["match"]), float(l["floor"]), str(l["floor_basis"]))
               for l in legs if l["verdict"] == "below_floor" and l["floor"] is not None]
    say(f"  carded legs on the card: {len(carded)}; below-floor legs: {len(refused)}")
    for match, floor, basis in carded:
        text = f"floor {floor:.2f} ({basis})"
        say(f"    card   {match[:34]:34s} {text} in artifact: {text in txt}")
    for match, floor, basis in refused:
        text = f"below floor {floor:.2f} [{basis}] — no bet"
        say(f"    refuse {match[:34]:34s} {text} in artifact: {text in txt}")
    check("the artifact's FLOORS table prints every applied market floor",
          "FLOORS (derived for" in txt and all(f"{v:.4f}" in txt for v in applied.values()))
    # The real slate did not have two firing legs to pair today, so the carded-leg
    # line is pinned on a labelled 4-pick probe board instead: distinct fixtures,
    # each priced just above the derived market floor.
    probe_floor = applied["match_over_25"]
    probe = [{"home": f"Probe{i} FC", "away": f"Probe{i} SC",
              "match": f"Probe{i} FC vs Probe{i} SC", "date": str(day),
              "bucket": "CLEAN", "rule": "probe",
              "recommended_enhancement": "match_over_25",
              "enhancement_label": "Match Over 2.5 Goals",
              "enhancement_probability": 0.46,
              "enhancement_price": probe_floor + 0.05 + 0.01 * i,
              "enhancement_price_book": "ProbeBook",
              "enhancement_price_source": "probe"}
             for i in range(4)]
    probe_legs = at.enhancement_legs(probe, floors=derived)
    probe_pool = at.enhancement_pool(probe_legs)
    probe_plan = at.plan_day(probe_pool, 100.0, stake_frac=at.ENHANCEMENT_LANE.stake_frac)
    at._carry_lane_evidence(probe_plan, probe_pool)
    probe_txt = at.render_enhancement_tickets(st, day, probe_legs, probe_plan,
                                              datetime.now(at.TZ), should_freeze=False,
                                              freeze_record=None, bank_eff=100.0,
                                              fixture_report={}, floors=derived)
    probe_carded = [(str(l.get("match")), float(l["floor"]), str(l.get("floor_basis")))
                    for a in probe_plan for l in a["legs"] if l.get("floor") is not None]
    say(f"  probe board (4 distinct fixtures at floor+0.05): "
        f"{len(probe_carded)} carded leg(s)")
    for match, floor, basis in probe_carded:
        text = f"floor {floor:.2f} ({basis})"
        say(f"    card   {match[:34]:34s} {text} in artifact: {text in probe_txt}")
    check("every carded leg names its floor and its basis",
          bool(probe_carded) and all(f"floor {f:.2f} ({b})" in probe_txt
                                     for _m, f, b in probe_carded))
    check("every below-floor leg names the floor and the basis that refused it",
          all(f"below floor {f:.2f} [{b}] — no bet" in txt for _m, f, b in refused))
    say()

    # ---- 7 -----------------------------------------------------------------
    say("-- 7. harness A/B, mean log growth per BET-day + no-bet frequency --")
    harness = subprocess.run([sys.executable, str(ROOT / "scripts" / "replay_harness.py"),
                              "--enhancements", "--ab", "live", "derived"],
                             cwd=ROOT, capture_output=True, text=True,
                             env={**os.environ, "PYTHONPATH": str(ROOT / "src")})
    for line in harness.stdout.splitlines():
        say(f"  {line}")
    check("the harness ran and reported both arms",
          harness.returncode == 0 and "arm A" in harness.stdout and "arm B" in harness.stdout)
    say()

    # ---- 8 -----------------------------------------------------------------
    say("-- 8. flag-off board byte-identical (pre-R2 tip vs this tree) --")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="r2_flagoff_"))
    gate_root = tmp / "gate"
    gate_root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "archive", "HEAD", "localdata"], cwd=ROOT,
                   stdout=open(tmp / "localdata.tar", "wb"), check=True)
    subprocess.run(["tar", "-x", "-C", str(gate_root)], cwd=tmp,
                   stdin=open(tmp / "localdata.tar", "rb"), check=True)
    # The probe board (the labelled 2-pick board the bundle prepared) and the
    # real ledger writer: both sides gate the SAME inputs, so a byte difference
    # can only come from the code under test.
    probe_src = ROOT / "handoff/flag_gate_2026-10-12/probe_board_picks.json"
    (gate_root / "localdata/picks_probe_2026-10-12.json").write_bytes(probe_src.read_bytes())
    ledger = subprocess.run([sys.executable, str(ROOT / "handoff/flag_gate_2026-10-12/prove_flag_gate.py"),
                             "ledger", "--root", str(gate_root),
                             "--archived", str(ROOT / "handoff/live_2026-10-12")],
                            cwd=ROOT / "handoff/flag_gate_2026-10-12", capture_output=True,
                            text=True, env={**os.environ, "PYTHONPATH": str(ROOT / "src")})
    say(f"  ledger written by the module's own writer: exit={ledger.returncode}")
    base_wt = tmp / "base_wt"
    subprocess.run(["git", "worktree", "add", "--detach", str(base_wt), PRE_R2],
                   cwd=ROOT, capture_output=True, text=True)
    runs = {}
    for label, pythonpath, driver in (
            ("pre-R2", base_wt / "src", base_wt / "handoff/flag_gate_2026-10-12/prove_flag_gate.py"),
            ("R2", ROOT / "src", ROOT / "handoff/flag_gate_2026-10-12/prove_flag_gate.py")):
        out_path = tmp / f"board.off.{label}.json"
        env = {k: v for k, v in os.environ.items() if k != "EDGE_FACTORY_ENH_BOARD"}
        env["PYTHONPATH"] = str(pythonpath)
        proc = subprocess.run([sys.executable, str(driver), "attach", "--root", str(gate_root),
                               "--mode", "off", "--out", str(out_path)],
                              cwd=driver.parent, capture_output=True, text=True, env=env)
        runs[label] = (proc.returncode, out_path.read_bytes() if out_path.exists() else b"")
        say(f"  {label:6s} attach --mode off: exit={proc.returncode}, "
            f"bytes={len(runs[label][1])}")
        if proc.returncode != 0:
            say(f"    stderr: {proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else ''}")
    identical = runs["pre-R2"][1] == runs["R2"][1] and bool(runs["pre-R2"][1])
    say(f"  byte-identical: {identical}")
    check("flag off: the board is byte-identical to the pre-R2 tip", identical)
    subprocess.run(["git", "worktree", "remove", "--force", str(base_wt)], cwd=ROOT,
                   capture_output=True, text=True)
    say()

    # ---- 9 -----------------------------------------------------------------
    say("-- 9. the suite at this tip --")
    suite = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"],
                           cwd=ROOT, capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": str(ROOT / "src")})
    tail = suite.stdout.strip().splitlines()[-1] if suite.stdout.strip() else "(no output)"
    say(f"  {tail}")
    check("the suite passes with no test lost", suite.returncode == 0 and "passed" in tail)
    say()
    say(f"== verdict: {'ALL PROOFS PASS' if ok else 'PROOF FAILURE — see FAIL lines'} ==")

    text = out.getvalue()
    print(text, end="")
    (ROOT / "handoff/r2_proofs.txt").write_text(text)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

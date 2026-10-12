#!/usr/bin/env python3
"""Round-2 §3 flag-gate proof harness.

  1. ``ledger`` builds the schema-2 BetExplorer detail ledger in a scratch root
     from the archived real market pages, using the module's own writer
     (``betexplorer_odds._persist_match_detail``) and its own parser.
  2. ``attach`` loads the price index and attaches enhancement prices to every
     board pick — the same two calls the board build makes
     (``enh_pricing.load_prices_index`` + ``attach_enhancement_price``) — and
     writes a pure comparison payload (no mode label, paths or timestamps) so
     two runs diff byte-for-byte. Attached boards are written next to it under
     ``attached/<name>.<mode>.json``.
  3. ``slip`` renders the enhancement slip's card lines for an attached board
     through the lane's own ``enhancement_legs`` + ``render_enhancement_tickets``
     (draft render, no state writes).

Run it under different code trees (PYTHONPATH) to compare versions:

  PYTHONPATH=/tmp/base_wt/src .venv/bin/python prove_flag_gate.py attach \
      --root $W --mode baseline --out $W/board.baseline.json
  PYTHONPATH=src .venv/bin/python prove_flag_gate.py attach \
      --root $W --mode off --out $W/board.off.json
  PYTHONPATH=src .venv/bin/python prove_flag_gate.py attach \
      --root $W --mode on --out $W/board.on.json

``off`` leaves EDGE_FACTORY_ENH_BOARD unset, ``on`` sets it to "1", and
``baseline`` is run under the pre-stage-1 tree where the ledger reader does not
exist at all. ``baseline`` vs ``off`` must be an empty diff; ``off`` vs ``on``
is the measured delta.
"""
from __future__ import annotations


import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()   # every localdata write goes to scratch (incident 2026-10-12)

import argparse
import json
import os
import sys
from copy import deepcopy
from pathlib import Path

DAY = "2026-10-12"
BOARDS = ["picks_today.json", "picks_2026-10-12.json",
          "picks_morning_2026-10-12.json", "picks_probe_2026-10-12.json"]
PRICE_FIELDS = ("home", "away", "recommended_enhancement", "enhancement_price",
                "enhancement_price_source", "enhancement_price_book",
                "enhancement_priced", "enhancement_mapped", "enhancement_multi_source")

# Ledger fixtures: the archived pages, identities from the 2026-10-12 homepage
# board mapping recorded in round 1 (the odds responses themselves carry no
# team names).
ARCHIVED_PAGES = (
    ("ou_lKAT82nf.json", "lKAT82nf", "JS El Biar", "CR Belouizdad", "ou",
     "https://www.betexplorer.com/football/algeria/ligue-1/js-el-biar-cr-belouizdad/lKAT82nf/"),
    ("bts_tW4rOkzg.json", "tW4rOkzg", "Coventry", "Newcastle Utd", "bts",
     "https://www.betexplorer.com/football/england/premier-league/coventry-newcastle-utd/tW4rOkzg/"),
)
PROBES = (
    ("JS El Biar", "CR Belouizdad", "match_over_35"),
    ("JS El Biar", "CR Belouizdad", "match_over_25"),
    ("Coventry", "Newcastle Utd", "btts_yes"),
)


def build_ledger(root: Path, archived: Path) -> None:
    from edgefactory.sources import betexplorer_odds as be

    ld = root / "localdata"
    ld.mkdir(parents=True, exist_ok=True)
    be.LOCALDATA = ld  # the writer's only path input
    for filename, event_id, home, away, slug, url in ARCHIVED_PAGES:
        html = json.loads((archived / filename).read_text())["odds"]
        be._persist_match_detail(
            {"home": home, "away": away, "date": DAY},
            DAY,
            {"event_id": event_id, "match_url": url, "kickoff": None,
             "home": home, "away": away, "country": "", "league": ""},
            {"markets": {slug: be.parse_market_response(html)},
             "page": None, "page_param": "1", "captured_at": f"{DAY}T00:00:00+00:00"},
            None,
        )
    payload = json.loads((ld / f"betexplorer_match_detail_{DAY}.json").read_text())
    summary = {"ledger": f"localdata/betexplorer_match_detail_{DAY}.json",
               "schema": payload.get("schema"), "date": payload.get("date"),
               "fixtures": {}}
    for key, entry in payload["fixtures"].items():
        blocks = {}
        for slug, block in (entry.get("markets") or {}).items():
            blocks[slug] = {"columns": block.get("columns"),
                            "lines": block.get("lines"),
                            "books": block.get("bookmakers"),
                            "rows": len(block.get("rows") or [])}
        summary["fixtures"][key] = {"home": entry.get("home"), "away": entry.get("away"),
                                    "blocks": blocks}
    print(json.dumps(summary, indent=1, sort_keys=True))


def attach(root: Path, mode: str, out: Path) -> None:
    from edgefactory import enh_pricing as ep

    flag = getattr(ep, "ENH_BOARD_FLAG", "EDGE_FACTORY_ENH_BOARD")
    os.environ.pop(flag, None)
    if mode == "on":
        os.environ[flag] = "1"
    index = ep.load_prices_index(root, DAY)
    result: dict = {"boards": {}, "betexplorer_pairs": [], "probes": []}
    attached_dir = out.parent / "attached"
    attached_dir.mkdir(parents=True, exist_ok=True)
    for name in BOARDS:
        picks = json.loads((root / "localdata" / name).read_text())
        rows, full = [], []
        for pick in picks:
            priced = deepcopy(pick)
            ep.attach_enhancement_price(priced, index)
            rows.append({k: priced.get(k) for k in PRICE_FIELDS})
            full.append(priced)
        result["boards"][name] = rows
        (attached_dir / f"{name}.{mode}.json").write_text(
            json.dumps(full, indent=1, sort_keys=True) + "\n")
    result["betexplorer_pairs"] = sorted(
        f"{nh}|{na}|{m}|{s}|{v[0]}|{v[1]}"
        for (nh, na), slots in index["pairs"].items()
        for (m, s), v in slots.items() if v[3] == "betexplorer")
    for home, away, market in PROBES:
        probe = {"home": home, "away": away, "recommended_enhancement": market,
                 "date": DAY}
        ep.attach_enhancement_price(probe, index)
        result["probes"].append({k: probe.get(k) for k in PRICE_FIELDS})
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(f"wrote {out} (mode={mode})")


def slip(board: Path, scripts: Path, root: Path, out: Path) -> None:
    sys.path.insert(0, str(scripts))
    import auto_tickets as at  # noqa: E402 - the lane's own renderer

    slate = json.loads(board.read_text())
    st = at.fresh_state()
    legs = at.enhancement_legs(slate)
    bank_eff = at.effective_bank(st, exclude_date=DAY)
    # Round 3: the lane draws the main lane's acca card, so the demo render
    # goes through the same two shared calls the command makes.
    pool = at.enhancement_pool(legs)
    plan = at.plan_day(pool, bank_eff, stake_frac=at.ENHANCEMENT_LANE.stake_frac)
    at._carry_lane_evidence(plan, pool)
    text = at.render_enhancement_tickets(
        st, DAY, legs, plan, at.datetime.now(at.TZ), should_freeze=False,
        freeze_record=None, bank_eff=bank_eff, root=root)
    out.write_text(text + "\n")
    print(f"wrote {out} ({len(legs)} legs, {len(plan)} accas)")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("ledger")
    pl.add_argument("--root", required=True)
    pl.add_argument("--archived", required=True)
    pa = sub.add_parser("attach")
    pa.add_argument("--root", required=True)
    pa.add_argument("--mode", choices=("baseline", "off", "on"), required=True)
    pa.add_argument("--out", required=True)
    ps = sub.add_parser("slip")
    ps.add_argument("--board", required=True)
    ps.add_argument("--scripts", required=True)
    ps.add_argument("--root", required=True)
    ps.add_argument("--out", required=True)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if args.cmd == "ledger":
        build_ledger(root, Path(args.archived).resolve())
    elif args.cmd == "attach":
        attach(root, args.mode, Path(args.out).resolve())
    else:
        slip(Path(args.board).resolve(), Path(args.scripts).resolve(), root,
             Path(args.out).resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())

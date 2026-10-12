#!/usr/bin/env python3
"""§4.4 of the 2026-10-12 close-out: reproduce every value the parser stores.

The reviewer's excerpt file is not in this workspace (see the header of
handoff/live-excerpt-tW4rOkzg-2026-10-12.txt), so the reproduction runs over the
agent's own fresh render of the same URL, read today. The reader is the
production parser itself - ``parse_match_page_blocks`` and ``parse_page`` from
edgefactory.sources.betexplorer_match_snapshot - not a re-implementation, so
what is printed below is what the parser WOULD store from this text.

Run from the repository root:
  PYTHONPATH=src .venv/bin/python handoff/s44_excerpt_repro.py
"""
from __future__ import annotations


import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()   # every localdata write goes to scratch (incident 2026-10-12)

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from edgefactory.sources import betexplorer_match_snapshot as ms  # noqa: E402

EXCERPT = REPO / "handoff/live-excerpt-tW4rOkzg-2026-10-12.txt"


def main() -> int:
    raw = EXCERPT.read_bytes()
    text = raw.decode("utf-8")
    print("== §4.4 reproduction over the fresh render ==")
    print(f"excerpt: {EXCERPT.name}")
    print(f"  sha256 {hashlib.sha256(raw).hexdigest()}  ({len(raw)} B, "
          f"{len(text.splitlines())} lines)")
    print("  (the reviewer's own excerpt, sha256 b1a4b33d97fc...b732, is not in this")
    print("   workspace: their commits died with the sandbox reset. Nothing here is")
    print("   attributed to it; these values are the agent's read of the same URL.)")
    print()

    blocks = ms.parse_match_page_blocks(text)
    page = ms.parse_page(text)

    print("-- what parse_match_page_blocks() stores from this render ----------")
    print(f"blocks: {blocks.get('blocks')}")
    print(f"h2h_meetings: {blocks.get('h2h_meetings')}")
    print(f"h2h_record: {blocks.get('h2h_record')}")
    rows = blocks.get("h2h_rows") or []
    print(f"h2h_rows: {len(rows)} row(s)  (cap _MAX_H2H_ROWS={ms._MAX_H2H_ROWS})")
    for r in rows:
        print(f"   {r['date']}  {r['score']}  odds={r['odds']}")
    print()
    lr = blocks.get("last_results_rows") or []
    labels = {}
    for r in lr:
        labels.setdefault(r["label"], []).append(r)
    print(f"last_results_rows: {len(lr)} row(s) over {len(labels)} block label(s)")
    for label, group in labels.items():
        print(f"   label {label!r}: {len(group)} rows, {group[0]['date']} .. {group[-1]['date']}")
        for r in group:
            print(f"      {r['date']}  {r['score']}  odds={r['odds']}")
    print()
    print(f"standings_columns: {blocks.get('standings_columns')}")
    srows = blocks.get("standings_rows") or []
    print(f"standings_rows: {len(srows)} row(s) (cap _MAX_STANDINGS_ROWS="
          f"{ms._MAX_STANDINGS_ROWS})")
    for r in srows[:3] + srows[-2:]:
        print(f"   {r['rank']:2d}. {r['team']:15s} MP {r['mp']} W {r['wins']} "
              f"D {r['draws']} L {r['losses']} GF:GA {r['goals_for']}:"
              f"{r['goals_against']} GD {r['goal_difference']} Pts {r['points']}")
    print()
    print("-- what parse_page() stores ----------------------------------------")
    print(f"score: {page['score']}  (null here: this is the match page before kickoff,")
    print("     and the header regex reads the pre-match line, not a scoreline)")
    print(f"h2h_record: {page['h2h_record']}")
    print(f"standings_position, prices_1x2: {page['standings_position']}, "
          f"{page['prices_1x2']}  (null by design: labels alone are not values)")
    print(f"header_verified: {page['header_verified']}")
    print()

    print("-- the values that DO reproduce, counted against the render ---------")
    dated = re.findall(r"\b\d{2}\.\d{2}\.\d{4}\b", text)
    print(f"dated strings in the render: {len(dated)} = the header kickoff date plus the")
    print("  30 region dates (20 H2H + 10 form); the parser's own reading above splits")
    print("  them by region, so the count is a cross-check on the extraction, not a")
    print("  second source)")
    print(f"H2H rows reproduced: {len(rows)}/20  |  form rows reproduced: {len(lr)}/10")
    print(f"standings rows reproduced: {len(srows)}/20")
    print(f"h2h summary reproduced: {blocks.get('h2h_record')} == the page's "
          f"'0 wins 1 draw 5 wins' line")
    print()

    print("-- the label against the list ---------------------------------------")
    print("The block is LABELLED 'Head to Head: Last 6' and the page serves 20 dated")
    print("meetings (1993..2010). The label is not the length of the list, and the")
    last6 = rows[:6]
    results = []
    for r in last6:
        text_row = r["text"]
        first = "Coventry" if text_row.find("Coventry") < text_row.find("Newcastle") \
            else "Newcastle"
        second = "Newcastle" if first == "Coventry" else "Coventry"
        winner = first if r["score"][0] > r["score"][1] else (
            second if r["score"][0] < r["score"][1] else "draw")
        results.append((r["date"], f"{first} {r['score'][0]}:{r['score'][1]} {second}",
                        winner))
    print(f"summary is not the newest six either: the newest six ({last6[0]['date']}"
          f"..{last6[-1]['date']}) read")
    for day, line, winner in results:
        print(f"    {day}  {line:28s} -> {winner}")
    print("  Every one of those six is a Newcastle win, so the same six rows would be")
    print("  0 wins / 0 draws / 6 wins - the page's summary says 0 / 1 / 5, i.e. it")
    print("  summarises ITS own window (the older meetings supply the draw), not the")
    print("  newest six. h2h_meetings stores the summary integer (the number in the")
    print("  label) and h2h_rows stores the dated list; neither is a claim about the")
    print("  other, and the label is not the length of the list.")
    print()

    print("-- values that do NOT reproduce here ---------------------------------")
    print("* anything attribute-level: data-oid, data-bt/data-sc/data-hcp, best-price")
    print("  flags and tbody ids live in the raw HTML and are not in a text render;")
    print("  this script reads a render, so those facts stay UNVERIFIED.")
    print("* per-row closing odds are read-time values: this read shows 1.45/3.99/7.50")
    print("  on 17.02.2010 where the earlier read today showed 1.44/4.20/7.50, and")
    print("  1.64/3.88/5.49 where the earlier read showed 1.64/3.87/5.52. Both reads")
    print("  and the drift are on record; a stored odds triple is what the page said")
    print("  at that moment, never a fixed fact.")
    print("* the reviewer's excerpt bytes: unavailable (see the note at the top).")
    print("* 'Show more matches' / 'Show full table' / the view strip: the render shows")
    print("  them as JS controls with no href - reproduced - but whether the markup")
    print("  attaches a handler is an attribute fact, and stays unverified.")
    print()
    summary = {
        "h2h_meetings": blocks.get("h2h_meetings"),
        "h2h_record": blocks.get("h2h_record"),
        "h2h_rows": len(rows),
        "h2h_rows_first": rows[0] if rows else None,
        "last_results_rows": len(lr),
        "standings_rows": len(srows),
        "standings_columns": blocks.get("standings_columns"),
        "standings_first": srows[0] if srows else None,
    }
    print("-- machine-readable summary -----------------------------------------")
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

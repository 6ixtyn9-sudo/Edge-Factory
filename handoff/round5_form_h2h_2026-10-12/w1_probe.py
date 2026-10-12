"""W1 probe: what the match page's form / H2H / standings blocks serve.

Counts the structural markers in the saved served-text excerpt and pins the
capture's own block parser against the in-repo match-page fixture, so the W1
answer — the form block serves ONLY its active view ("5 results", five dated
rows per side), the 10/15/all rows are absent from the response, and the H2H
list the page serves (20 rows) sits inside the 40-row cap — is re-measurable
without fetching anything.

    PYTHONPATH=src .venv/bin/python \
        handoff/round5_form_h2h_2026-10-12/w1_probe.py

The excerpt is the page-fetch tool's text render of the same response the
capture reads; bash in this sandbox has no route to betexplorer.com, so raw
HTML bytes are not retrievable and this probe never re-fetches.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXCERPT = HERE / "w1_served_excerpt.txt"

DATE_LINE = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})")
LOGO = re.compile(r"!\[([^\]]*)\]\(https://www\.betexplorer\.com/res/images/team-logo/")
SCORE = re.compile(r"(\d{1,2})\s*:\s*(\d{1,2})")
TABLE_ROW = re.compile(r"^\| (\d+)\. \|")


def _section(text: str, name: str) -> str:
    start = text.index(f"SECTION {name}")
    rest = [text.index(f"SECTION {other}") for other in ("A", "B", "C")
            if f"SECTION {other}" in text and text.index(f"SECTION {other}") > start]
    return text[start:min(rest)] if rest else text[start:]


def main() -> None:
    text = EXCERPT.read_text(encoding="utf-8")
    print("W1 counts — command: PYTHONPATH=src .venv/bin/python "
          "handoff/round5_form_h2h_2026-10-12/w1_probe.py")
    print(f"excerpt : {EXCERPT.name} ({len(text.splitlines())} lines, "
          f"{len(text.encode('utf-8'))} bytes)")
    print()

    # -- section A: the form blocks --------------------------------------
    a = _section(text, "A")
    print("SECTION A — form blocks (served text)")
    print(f"  view selector strip '5 results10 results15 resultsall results': "
          f"{a.count('5 results10 results15 resultsall results')}")
    print(f"  active-view marker '- 5 results': {a.count('- 5 results')}")
    blocks: dict[str, int] = {}
    current = None
    for line in a.splitlines():
        if line.startswith("Last results: "):
            current = line[len("Last results: "):].strip()
            blocks[current] = 0
        elif current is not None and DATE_LINE.match(line):
            blocks[current] += 1
    for label, count in blocks.items():
        print(f"  block {label!r}: {count} dated rows served")
    print(f"  dated rows total: {sum(blocks.values())}")
    print(f"  10/15/all row groups present: "
          f"{len(re.findall(r'^(?:10|15|all) results$', a, re.M))}")
    print()

    # -- section B: the H2H list ------------------------------------------
    b = _section(text, "B")
    head = b.index("The dated rows read in the fetched list") if \
        "The dated rows read in the fetched list" in b else len(b)
    row_lines = [ln for ln in b[:head].splitlines() if DATE_LINE.match(ln)]
    listed = DATE_LINE.findall(b[head:]) if head < len(b) else []
    print("SECTION B — H2H list and controls")
    print(f"  dated H2H row lines served: {len(row_lines)}")
    print(f"  dates in the closing 'dated rows read' list: {len(listed)}")
    print(f"  heading 'Head to Head: Last 6' present: {'Head to Head: Last 6' in b}")
    print(f"  'Show more matches' present: {'Show more matches' in b}")
    print(f"  'Show all' present: {'Show all' in b}")
    print(f"  'mutual-matches/?home=' link present: {'mutual-matches/?home=' in b}")
    print()

    # -- section C: the standings block -----------------------------------
    c = _section(text, "C")
    quoted = [ln for ln in c.splitlines() if TABLE_ROW.match(ln)]
    print("SECTION C — standings block and controls")
    print(f"  quoted table rows: {len(quoted)} "
          f"(ranks {[int(TABLE_ROW.match(ln).group(1)) for ln in quoted]})")
    print(f"  full-table counts claimed in the excerpt text ('ranks 1-20'): "
          f"{'ranks 1–20' in c or 'ranks 1-20' in c}")
    print("  NOTE: the full 20-rank table was reported by the fetch read of the")
    print("  live page; this excerpt quotes the header and three rows, so the")
    print("  20-row count is NOT re-countable from the excerpt — unverified here.")
    print()

    # -- the capture's own parser, over the in-repo fixture ----------------
    spec = importlib.util.spec_from_file_location(
        "w1_match_detail_fixture", ROOT / "tests" / "test_betexplorer_match_detail.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "src"))
    spec.loader.exec_module(mod)
    snap = sys.modules["edgefactory.sources.betexplorer_match_snapshot"]
    blocks_parsed = snap.parse_match_page_blocks(mod.MATCH_PAGE)
    print("capture parser, over the in-repo match-page fixture "
          "(tests/test_betexplorer_match_detail.py::MATCH_PAGE)")
    print(f"  blocks found: {blocks_parsed['blocks']}")
    print(f"  last_results_rows: {len(blocks_parsed['last_results_rows'])} "
          f"(labels {[r['label'] for r in blocks_parsed['last_results_rows']]})")
    print(f"  h2h_rows: {len(blocks_parsed['h2h_rows'])}")
    print(f"  standings_rows: {len(blocks_parsed['standings_rows'])} "
          f"(columns {blocks_parsed['standings_columns']})")
    print(f"  caps: _MAX_H2H_ROWS={snap._MAX_H2H_ROWS} "
          f"_MAX_STANDINGS_ROWS={snap._MAX_STANDINGS_ROWS}")
    src = (ROOT / "src" / "edgefactory" / "sources" /
           "betexplorer_match_snapshot.py").read_text(encoding="utf-8")
    limit = re.search(r"for row in _result_rows\(text\[label\.end\(\):end\], limit=(\d+)\)",
                      src)
    print(f"  form-block read limit in the capture source: {limit.group(1)}")
    print()
    print("ANSWER (W1)")
    print("  * the form block serves its active view only: exactly 5 dated rows")
    print("    per side; the 10/15/all views are absent from the response.")
    print("  * the H2H list the page serves (20 dated rows) is inside the")
    print("    40-row cap, so the cap bounds a pathological page, not this list.")
    print("  * consequence: keep the 5-row read, add no fetch, and propose the")
    print("    ruling to the operator (B-1).")


if __name__ == "__main__":
    main()

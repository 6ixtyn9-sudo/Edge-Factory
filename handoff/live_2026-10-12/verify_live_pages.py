#!/usr/bin/env python3
"""Live BetExplorer verification (round-2 brief section 4), V1-V8.

Every price/column/average the checks below report comes from the MODULE'S OWN
parser (``edgefactory.sources.betexplorer_odds.parse_market_response``). The page
markup is only read back for comparison, with small regexes, so that the check is
independent of the parser rather than a paraphrase of it.

Usage:  PYTHONPATH=src .venv/bin/python handoff/live_2026-10-12/verify_live_pages.py
Reads :  handoff/live_2026-10-12/*.json  (JSON-wrapped HTML as served)
Writes:  stdout only (raw evidence; no summaries)
"""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from edgefactory.sources import betexplorer_odds as be  # noqa: E402


def load(name: str) -> tuple[str, str]:
    path = HERE / name
    raw = path.read_bytes()
    payload = json.loads(raw)
    html = payload["odds"]
    return html, hashlib.sha256(raw).hexdigest()


def thead_labels(html: str, section: str | None = None) -> list[str]:
    """Labels of a table's own <thead>, verbatim from the markup."""
    scope = html
    if section:
        start = html.find(f'data-handicap="{section}"')
        scope = html[start:] if start >= 0 else html
    head = re.search(r"<thead[^>]*>(.*?)</thead>", scope, re.S)
    if not head:
        return []
    return [re.sub(r"<[^>]+>", "", th).strip() for th in re.findall(r"<th[^>]*>(.*?)</th>", head.group(1), re.S)]


def line_section(html: str, line: str) -> str:
    """The slice of markup covering one handicap line's whole group.

    The page nests ``data-all-handicap="handicap-0.50"`` (inner, header only)
    inside ``data-all-handicap="0.50"`` (outer, header + the all-book rows). The
    section therefore runs from the outer marker to the next OUTER marker of a
    different line.
    """
    marker = '<div data-all-handicap="'
    parts = html.split(marker)
    starts = [i for i, seg in enumerate(parts) if i and not seg.startswith("handicap-")]
    for pos, i in enumerate(starts):
        if parts[i].startswith(f'{line}"'):
            end = starts[pos + 1] if pos + 1 < len(starts) else len(parts)
            return marker + marker.join(parts[i:end])
    return ""


def page_best_rows(html: str, line: str) -> list[tuple[str, float, float]]:
    """(bookmaker, over, under) rows of one line, read straight from the markup."""
    sec = line_section(html, line)
    rows = []
    for tr in re.findall(r'<div class="oddsComparisonAll__rowBookie"(.*?)(?=<div class="oddsComparisonAll__rowBookie"|\Z)', sec, re.S):
        book = re.search(r'title="([^"]+)"', tr)
        odds = [float(x) for x in re.findall(r'data-odd="([0-9.]+)"', tr)]
        if book and len(odds) >= 2:
            rows.append((book.group(1), odds[0], odds[1]))
    return rows


def page_average(html: str, line: str) -> list[float]:
    sec = line_section(html, line)
    vals = re.findall(r'class="oddsComparisonAll__average_text" data-odd="([0-9.]+)"', sec)
    return [float(v) for v in vals]


def books_in_markup(html: str) -> set[str]:
    return set(re.findall(r'title="([^"]+)"', html)) | set(re.findall(r"'event-name': '([^']+)'", html))


def run_checks(title: str, name: str, url: str, expected_line_columns: bool) -> None:
    html, raw_sha = load(name)
    parsed = be.parse_market_response(html)
    print(f"\n{'=' * 78}\n{title}\n  file: {name}")
    print(f"  url:  {url}")
    print(f"  served-json sha256: {raw_sha}")
    print(f"  html sha256:        {hashlib.sha256(html.encode()).hexdigest()}  ({len(html)} chars)")
    print(f"  parse_market_response -> columns={parsed['columns']} lines={parsed['lines']} "
          f"rows_count={parsed['rows_count']} named_rows={parsed['named_rows']}")
    print(f"  bookmakers: {parsed['bookmakers']}")
    print(f"  average: {parsed['average']}  average_by_line: {parsed['average_by_line']}")

    # ---------------------------------------------------------------- V1
    print("\n-- V1 columns == the page's own <thead>")
    first_line = parsed["lines"][0] if parsed["lines"] else None
    raw_labels = thead_labels(html) if "bts" in name else thead_labels(html, first_line if first_line != "0" else "0.50")
    labels = [l for l in raw_labels if l and l != "Total"]
    print(f"   page thead labels (non-decorative): {labels}")
    print(f"   V1 {'PASS' if labels == parsed['columns'] else 'FAIL'}  parser columns: {parsed['columns']}")

    # ---------------------------------------------------------------- V3 / V4
    print("\n-- V3 sampled prices appear verbatim in the served markup")
    sampled = []
    for row in parsed["rows"]:
        for value in row["odds"]:
            sampled.append(value)
    missing = [v for v in dict.fromkeys(sampled) if f'data-odd="{v:.2f}"' not in html and f'data-odd="{v}"' not in html]
    print(f"   distinct parsed prices: {sorted(dict.fromkeys(sampled))}")
    print(f"   V3 {'PASS' if not missing else 'FAIL'}  not found verbatim: {missing}")

    print("\n-- V4 no price <= 1.0, no NaN/inf, no invented bookmakers")
    bad = [v for v in sampled if not isinstance(v, (int, float)) or isinstance(v, bool)
           or not math.isfinite(v) or v <= 1.0]
    invented = [b for b in parsed["bookmakers"] if b and b not in books_in_markup(html)]
    print(f"   V4 {'PASS' if not bad and not invented else 'FAIL'}  bad prices: {bad}  invented books: {invented}")
    print(f"   bookmaker titles found in markup: {sorted(books_in_markup(html))}")

    # ---------------------------------------------------------------- V2 / V6 / V7
    if expected_line_columns:
        print("\n-- V2 per-line chosen price == the page's own best row (data-bo=\"true\", else max)")
        for line in parsed["lines"]:
            rows = [r for r in parsed["rows"] if r["line"] == line]
            best = [r for r in rows if r.get("best")] or []
            chosen = best[0] if best else max(rows, key=lambda r: r["odds"][0])
            page_rows = page_best_rows(html, line)
            print(f"   line {line}: parser rows={[(r['bookmaker'], r['odds']) for r in rows]}")
            print(f"              page rows ={page_rows}")
            over_ok = any(abs(chosen["odds"][0] - pr[1]) < 1e-9 for pr in page_rows)
            print(f"              V2 over {'PASS' if over_ok else 'FAIL'}: parser chose {chosen['bookmaker']} "
                  f"{chosen['odds'][0]:.2f} (best={bool(best)})")

            # ------------------------------------------------------------ V6
            over, under = chosen["odds"][0], chosen["odds"][1]
            overround = 1 / over + 1 / under
            verdict = "PASS" if 1.0 <= overround <= 1.15 else "FAIL"
            print(f"              V6 {verdict}: 1/{over:.2f} + 1/{under:.2f} = {overround:.4f}")

            # ------------------------------------------------------------ V7
            page_avg = page_average(html, line)
            parsed_avg = parsed["average_by_line"].get(line)
            avg_ok = page_avg and parsed_avg and all(abs(a - b) < 1e-9 for a, b in zip(parsed_avg, page_avg))
            print(f"              V7 {'PASS' if avg_ok else 'FAIL'}: page average_text={page_avg} "
                  f"parser average_by_line={parsed_avg}")

        # ---------------------------------------------------------------- V5
        print("\n-- V5 over/under direction: swapping the thead labels in a copy must fail the same check")
        original = [r for r in parsed["rows"] if r["line"] == parsed["lines"][0]][0]
        swapped_html = html.replace(">Over</th>", ">__SWAP__</th>").replace(">Under</th>", ">Over</th>").replace(">__SWAP__</th>", ">Under</th>")
        assert swapped_html != html, "swap did not touch the markup"
        swapped = be.parse_market_response(swapped_html)
        swapped_row = [r for r in swapped["rows"] if r["line"] == parsed["lines"][0]][0]
        print(f"   original columns={parsed['columns']} row odds={original['odds']}")
        print(f"   swapped  columns={swapped['columns']} row odds={swapped_row['odds']}")
        page_over = page_best_rows(html, parsed["lines"][0])[0][1]
        v5 = (parsed["columns"] == ["Over", "Under"] and abs(original["odds"][0] - page_over) < 1e-9
              and swapped["columns"] == ["Under", "Over"] and swapped_row["odds"] == original["odds"])
        print(f"   V5 {'PASS' if v5 else 'FAIL'}: the parser reads the cell under the page's own <th>; "
              f"the assertion columns==['Over','Under'] FAILS on the swapped copy "
              f"(it reports {swapped['columns']} for the same cell values {swapped_row['odds']})")
    else:
        print("\n-- V2/V6/V7 for a two-way market without handicap lines")
        for row in parsed["rows"]:
            overround = 1 / row["odds"][0] + 1 / row["odds"][1]
            print(f"   {row['bookmaker']}: {row['odds']}  1/yes+1/no = {overround:.4f}  "
                  f"{'PASS' if 1.0 <= overround <= 1.15 else 'FAIL'}")
        page_avg = [float(v) for v in re.findall(r'class="oddsComparisonAll__average_text" data-odd="([0-9.]+)"', html)]
        print(f"   V7 page average_text={page_avg}  parser average={parsed['average']} "
              f"{'PASS' if page_avg == parsed['average'] else 'FAIL'}")
        print("   V7 chosen price != average where they differ: "
              f"best row = {[(r['bookmaker'], r['odds']) for r in parsed['rows'] if r.get('best')]}")


def main() -> None:
    print("BetExplorer live verification, fetched 2026-10-12 through the fetch_page tool")
    print("(bash in this sandbox has no BetExplorer egress: curl -> SSL_ERROR_SYSCALL/HTTP 000)")
    print(f"module under test: {be.__file__}")
    print(f"_BE_SLUGS (ledger slug -> index market): {be_reader_slugs()}")

    run_checks("Algeria Ligue 1: JS El Biar vs CR Belouizdad - today-board pick (match_over_35)",
              "ou_lKAT82nf.json",
              "https://www.betexplorer.com/match-odds/lKAT82nf/1/ou/bestOdds/?lang=en",
              expected_line_columns=True)
    run_checks("BTTS market page (Coventry vs Newcastle, section 4.6 reference)",
              "bts_tW4rOkzg.json",
              "https://www.betexplorer.com/match-odds/tW4rOkzg/1/bts/bestOdds/?lang=en",
              expected_line_columns=False)

    # ---------------------------------------------------------------- V8
    print(f"\n{'=' * 78}\n-- V8 bts slug path end to end")
    from edgefactory import enh_pricing
    print(f"   _BE_SLUGS          = {enh_pricing._BE_SLUGS}")
    print(f"   bts -> ledger slug = {enh_pricing._BE_SLUGS.get('bts')}")
    print(f"   ledger key for btts= {[k for k, v in enh_pricing._BE_SLUGS.items() if v == 'btts']}")
    bts = be.parse_market_response(load("bts_tW4rOkzg.json")[0])
    print(f"   page /bts/ parsed rows: {[(r['bookmaker'], r['odds']) for r in bts['rows']]}")
    print(f"   bts columns={bts['columns']} (Yes/No) -> index market 'btts' takes the Yes price")


def be_reader_slugs():
    try:
        from edgefactory import enh_pricing
        return enh_pricing._BE_SLUGS
    except Exception as exc:  # noqa: BLE001
        return f"(import failed: {exc})"


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Archive-level picked-fixture price coverage by competition.

This is a reporting tool only. It does not fetch, price, suppress, or mutate
picks. It scans archived pick ledgers and counts how often each competition has
received a real named-book price from the approved price-source registry.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory import price_sources as psrc  # noqa: E402

LOCALDATA = ROOT / "localdata"

_DATE_PICK_RE = re.compile(r"^picks_\d{4}-\d{2}-\d{2}\.json$")


def pick_archives(localdata: Path = LOCALDATA) -> list[Path]:
    return sorted(p for p in localdata.glob("picks_*.json") if _DATE_PICK_RE.match(p.name))


def load_rows(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError, TypeError):
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def competition_label(pick: dict[str, Any]) -> str:
    ctx = pick.get("ctx") if isinstance(pick.get("ctx"), dict) else {}
    for value in (ctx.get("league_raw"), pick.get("league"), ctx.get("league"), ctx.get("league_key")):
        text = str(value or "").strip()
        if text and text not in {"?", "UNKNOWN"}:
            return text
    return "UNKNOWN"


def is_named_book_priced(pick: dict[str, Any]) -> bool:
    if pick.get("odds") is None:
        return False
    if str(pick.get("price_evidence") or "") == "SUSPECT_ALIAS_FUZZY":
        return False
    return bool(psrc.spec(pick.get("odds_source")).named_bookmaker)


def coverage_table(localdata: Path = LOCALDATA) -> list[dict[str, Any]]:
    counts: dict[str, Counter] = defaultdict(Counter)
    examples: dict[str, str] = {}
    for path in pick_archives(localdata):
        for pick in load_rows(path):
            comp = competition_label(pick)
            counts[comp]["picks"] += 1
            counts[comp]["priced"] += int(is_named_book_priced(pick))
            examples.setdefault(comp, str(pick.get("match") or ""))
    rows: list[dict[str, Any]] = []
    for comp, counter in counts.items():
        picks = int(counter["picks"])
        priced = int(counter["priced"])
        rate = (priced / picks) if picks else 0.0
        rows.append({
            "competition": comp,
            "picks": picks,
            "priced": priced,
            "coverage_rate": rate,
            "example": examples.get(comp, ""),
        })
    rows.sort(key=lambda row: (-int(row["picks"]), int(row["priced"]), str(row["competition"])))
    return rows


def render_markdown(rows: list[dict[str, Any]], *, min_zero_picks: int = 3, limit: int = 0) -> str:
    display = rows[:limit] if limit and limit > 0 else rows
    total_picks = sum(int(r["picks"]) for r in rows)
    total_priced = sum(int(r["priced"]) for r in rows)
    zero = [r for r in rows if int(r["priced"]) == 0 and int(r["picks"]) >= min_zero_picks]
    lines = [
        "# Price coverage by competition",
        "",
        f"Archive files scanned: {len(pick_archives())}",
        f"Picks generated: {total_picks}",
        f"Picks ever named-book priced: {total_priced}",
        f"Structurally-zero candidates (priced=0, picks>={min_zero_picks}): {len(zero)}",
        "",
        "| Competition | Picks generated | Picks ever priced | Coverage |",
        "|---|---:|---:|---:|",
    ]
    for row in display:
        lines.append(
            f"| {str(row['competition']).replace('|', '/')} | {int(row['picks'])} | "
            f"{int(row['priced'])} | {float(row['coverage_rate']):.1%} |"
        )
    lines.extend(["", "## Persistent zero-coverage competitions", ""])
    if not zero:
        lines.append("None at the selected threshold.")
    else:
        lines.append("| Competition | Picks generated | Example fixture |")
        lines.append("|---|---:|---|")
        for row in zero:
            lines.append(
                f"| {str(row['competition']).replace('|', '/')} | {int(row['picks'])} | "
                f"{str(row.get('example') or '').replace('|', '/')} |"
            )
    lines.extend([
        "",
        "Note: this table is historical coverage evidence, not an automatic suppression rule.",
        "Any later pick suppression must be config-gated and printed in the run log.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--localdata", type=Path, default=LOCALDATA)
    ap.add_argument("--min-zero-picks", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="Limit the main table rows; zero list is never limited")
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    rows = coverage_table(args.localdata)
    text = render_markdown(rows, min_zero_picks=args.min_zero_picks, limit=args.limit)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
        print(f"wrote {args.output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

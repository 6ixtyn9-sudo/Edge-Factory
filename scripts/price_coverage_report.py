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
import unicodedata
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


def _ascii_fold(raw: object) -> str:
    folded = unicodedata.normalize("NFKD", str(raw or ""))
    return "".join(ch for ch in folded if not unicodedata.combining(ch)).lower()


def _label_words(raw: object) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", _ascii_fold(raw))).strip()


def _label_code(raw: object) -> str:
    return re.sub(r"[^a-z0-9]", "", _ascii_fold(raw))


def _raw_competition_label(pick: dict[str, Any]) -> str:
    ctx = pick.get("ctx") if isinstance(pick.get("ctx"), dict) else {}
    for value in (ctx.get("league_raw"), pick.get("league"), ctx.get("league"), ctx.get("league_key")):
        text = str(value or "").strip()
        if text and text not in {"?", "UNKNOWN"}:
            return text
    return "UNKNOWN"


def _looks_womens_fixture(pick: dict[str, Any], raw_label: str) -> bool:
    hay = " ".join(str(pick.get(k) or "") for k in ("home", "away", "match")) + " " + raw_label
    words = set(_label_words(hay).split())
    code = _label_code(hay)
    return bool(
        words & {"w", "women", "womens", "ladies", "female", "fem", "frauen", "nwsl", "wsl"}
        or "(w)" in hay.lower()
        or any(marker in code for marker in ("women", "frauen", "nwsl", "damallsvenskan"))
    )


def canonical_competition_label(raw_label: str, pick: dict[str, Any] | None = None) -> str:
    """Canonical label for coverage reporting only.

    This is intentionally narrower than the entity registry: it collapses known
    competition-code fragments in operator coverage tables while preserving raw
    labels in pick receipts.  It never changes price joins or selected picks.
    """
    pick = pick or {}
    raw = str(raw_label or "").strip() or "UNKNOWN"
    words = _label_words(raw)
    code = _label_code(raw)
    womens = _looks_womens_fixture(pick, raw)

    # UEFA family: check Conference before Europa so the shorter phrase cannot
    # swallow the distinct Conference League.
    if code == "ucl" or "uefa champions league" in words:
        return "World UEFA Champions League"
    if code == "ecl" or "uefa europa conference league" in words:
        return "World UEFA Europa Conference League"
    if code == "uel" or "uefa europa league" in words:
        return "World UEFA Europa League"
    if code == "unl" or "uefa nations league" in words:
        return "World UEFA Nations League"

    # Women labels / women fixtures: keep them out of men's top-flight buckets.
    if womens:
        if code in {"esw", "spainligaf"} or "spain la liga" in words or "spain liga f" in words:
            return "Spain Liga F"
        if code in {"mxw", "mexicoligamxfemenil"} or "liga mx femenil" in words:
            return "Mexico Liga MX Femenil"
        if code in {"sew", "swedendamallsvenskan"} or "damallsvenskan" in words:
            return "Sweden Damallsvenskan"
        if code in {"now", "norwaywomen"}:
            return "Norway Women"
        if code in {"atw", "austriawomen"}:
            return "Austria Women"
        if code in {"brw", "brazilwomen"}:
            return "Brazil Women"
        if code == "clw":
            return "UEFA Women's Champions League"
        if "nwsl" in words or code == "usanwsl":
            return "USA NWSL"
        if "england wsl" in words or code == "englandwsl":
            return "England WSL"

    exact = {
        "fr1": "France,Ligue 1",
        "france ligue 1": "France,Ligue 1",
        "lv1": "Latvia Virsliga",
        "latvia virsliga": "Latvia Virsliga",
        "is1": "Iceland,Besta Deildin",
        "iceland besta deildin": "Iceland,Besta Deildin",
        "es2": "Spain Segunda División",
        "spain laliga2": "Spain Segunda División",
        "spain segunda division": "Spain Segunda División",
        "es1": "Spain La Liga",
        "spain laliga": "Spain La Liga",
    }
    return exact.get(words, exact.get(code, raw))


def competition_label(pick: dict[str, Any]) -> str:
    raw = _raw_competition_label(pick)
    return canonical_competition_label(raw, pick)


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

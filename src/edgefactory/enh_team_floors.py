"""Dynamic price floors for TEAM under markets, derived from the settled picks.

Why a separate table: the registry only holds priced legs, and team unders have
never fired, so it has zero team-under records. The evidence that does exist is
the settled pick ledger (``localdata/picks_YYYY-MM-DD.json`` + ``settled_results``):
for every 1X2 pick it carries the team-total candidates the pick's own model
proposed, and the settled score says whether each one hit.

Floors are keyed by ``market|side`` because the hit rate depends on the 1X2 side
(the pick's side is the favourite in every matched October row). A leg whose
side has no evidence has no floor and cannot fire.

Each floor is ``1 / Wilson-LB95(hit rate) + ENHANCEMENT_FLOOR_MARGIN`` on the
rows dated strictly before the day being derived (no lookahead), and it is
recomputed every day, so it moves with the record. Fail-soft: any read error
answers an empty table, and an empty table means no team leg fires.
"""
from __future__ import annotations

import difflib
import glob
import json
import os
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

from edgefactory.enh_registry import ENHANCEMENT_FLOOR_MARGIN, MIN_PRICED_N, wilson_lb

TEAM_UNDER_MARKETS = frozenset({
    "home_under_15", "away_under_15",
    "home_under_25", "away_under_25",
    "home_under_35", "away_under_35",
})
_TARGET = re.compile(r"^(home|away)_under_(\d)(\d)$")
FLOOR_BASIS_EVIDENCE = "pick_evidence"


def _norm(name: object) -> str:
    s = unicodedata.normalize("NFKD", str(name or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]", " ", s).strip()


def _hit(market: str, hs: int, gs: int) -> bool | None:
    m = _TARGET.match(market)
    if not m:
        return None
    scope, thr = m.group(1), int(m.group(2)) + int(m.group(3)) / 10.0
    goals = hs if scope == "home" else gs
    return goals < thr


def _settled_index(root: Path, before: str) -> dict[str, list]:
    """day -> [(norm home, norm away, (hs, gs))], settled strictly before `before`."""
    data = json.loads((Path(root) / "localdata" / "settled_results.json").read_text())
    by_day: dict[str, list] = defaultdict(list)
    for r in data.get("rows") or []:
        d = str(r.get("date") or "")[:10]
        if not d or d >= before:
            continue
        by_day[d].append((_norm(r.get("home")), _norm(r.get("away")), (int(r["hs"]), int(r["gs"]))))
    return by_day


def _match_result(index: dict[str, list], day: str, home: str, away: str) -> tuple[int, int] | None:
    """Exact name match first; otherwise the single same-day fixture whose two names
    both score >= 0.90 similarity (accents, 'FC'/'FK' suffixes, punctuation)."""
    nh, na = _norm(home), _norm(away)
    fixtures = index.get(day, [])
    for h, a, score in fixtures:
        if h == nh and a == na:
            return score
    cands = []
    for h, a, score in fixtures:
        r1 = difflib.SequenceMatcher(None, nh, h).ratio()
        r2 = difflib.SequenceMatcher(None, na, a).ratio()
        if r1 >= 0.90 and r2 >= 0.90:
            cands.append(score)
    return cands[0] if len(cands) == 1 else None


def team_under_evidence(root: Path, before: str) -> list[dict]:
    """One row per graded (fixture, side, team-under market) candidate dated before `before`."""
    root = Path(root)
    index = _settled_index(root, before)
    seen: set = set()
    rows: list[dict] = []
    for f in sorted(glob.glob(str(root / "localdata" / "picks_20*.json"))):
        day = os.path.basename(f)[6:16]
        if not day or day >= before:
            continue
        try:
            slate = json.loads(Path(f).read_text())
        except Exception:
            continue
        if not isinstance(slate, list):
            continue
        for p in slate:
            if not isinstance(p, dict) or p.get("market") != "1x2":
                continue
            side = p.get("pick")
            if side not in ("home", "away"):
                continue
            score = _match_result(index, day, p.get("home") or "", p.get("away") or "")
            if score is None:
                continue
            for note in p.get("event_notes") or []:
                mkt = (note or {}).get("market")
                if mkt not in TEAM_UNDER_MARKETS:
                    continue
                key = (day, _norm(p.get("home")), _norm(p.get("away")), side, mkt)
                if key in seen:
                    continue
                seen.add(key)
                rows.append({"day": day, "side": "1" if side == "home" else "2",
                             "market": mkt, "hit": bool(_hit(mkt, *score))})
    return rows


def team_under_floors(root: Path, as_of: str, *, margin: float = ENHANCEMENT_FLOOR_MARGIN,
                      min_n: int = MIN_PRICED_N) -> dict[str, dict]:
    """``{"market|side": {"floor", "n", "hits", "wilson_lb", "basis"}}`` for every
    team-under side whose evidence clears ``min_n`` with a positive lower bound.
    Empty on any error (fail-soft)."""
    try:
        rows = team_under_evidence(root, str(as_of)[:10])
    except Exception:
        return {}
    grouped: dict[str, list[bool]] = defaultdict(list)
    for r in rows:
        grouped[f"{r['market']}|{r['side']}"].append(r["hit"])
    table: dict[str, dict] = {}
    for key, hits in sorted(grouped.items()):
        n = len(hits)
        if n < min_n:
            continue
        h = sum(hits)
        lb = wilson_lb(h, n)
        if lb <= 0.0:
            continue
        table[key] = {"floor": round(1.0 / lb + float(margin), 4), "n": n, "hits": h,
                      "wilson_lb": round(lb, 4), "basis": FLOOR_BASIS_EVIDENCE}
    return table

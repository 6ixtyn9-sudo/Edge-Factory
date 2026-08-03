"""Enhancement pricing join — attach real bookmaker prices to enhancement candidates.

The enhancement overlay (compute_dynamic_enhancement in picks_today) historically
recommended markets on probability alone, with no price field anywhere in the path.
The 2026-08-03 audit showed where that leads: negative-EV products surviving
(match_over_15 EV ~-48%, goal_range_2_3 EV ~-49% at estimated prices) and
trivially-priced markets presented as if they were real products (team unders whose
fair price is ~1.03). Probability without price is not evidence of value.

This module is the first half of the fix: for enhancement types that map to a market
we actually capture (pilot: match over/under 2.5 via the theoddsapi totals feed),
attach the BEST real price + book + timestamp to the pick's enhancement record.
Types with no captured-market mapping get price=None and, via the registry gate in
picks_today, can never be presented as recommendations.

Fail-soft by design: any error (missing file, bad row, matcher hiccup) degrades to
"unpriced" — this join must never raise into the picks pipeline.
"""
from __future__ import annotations

import csv
import gzip
import math
from pathlib import Path
from typing import Any, Callable

from .util import norm_team

# Enhancement type -> (captured market, selection) or None when the market is not
# captured. Pilot mappings only. Absent/None = unpriceable for now (display-only).
MARKET_PRICE_MAP: dict[str, tuple[str, str] | None] = {
    "match_over_25": ("ou_2.5", "over"),
    "match_under_25": ("ou_2.5", "under"),
    # Known types intentionally unmapped (markets not in the capture feed):
    "match_over_15": None,     # needs alternate totals line 1.5
    "goal_range_2_3": None,    # banded market, not offered by the feed
    "away_under_35": None,     # team totals, not captured
    "home_under_45": None,     # team totals, not captured
}

THEODDSAPI_SOURCE = "theoddsapi"


def _default_match_fn() -> Callable[[object, object], bool] | None:
    """Lazy-import the adapter's team matcher; None degrades to exact-key-only."""
    try:
        from .sources.theoddsapi import _team_names_match
        return _team_names_match
    except Exception:
        return None


def _month_of(day: str) -> str:
    return (day or "")[:7]


def load_prices_index(root: Path, day: str) -> dict[str, Any]:
    """Build {"pairs": {(nh, na): {(market, sel): (best_price, book, at)}},
              "names": {(nh, na): (raw_home, raw_away)}}
    from the theoddsapi monthly odds file for `day`. Keeps the BEST (max) price per
    (market, selection) — matches the pipeline's best-price convention. Fail-soft."""
    out: dict[str, Any] = {"pairs": {}, "names": {}}
    try:
        path = Path(root) / "localdata" / f"theoddsapi_odds_{_month_of(day)}.csv.gz"
        if not path.exists():
            return out
        with gzip.open(path, "rt", newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("source") != THEODDSAPI_SOURCE or row.get("date") != day:
                    continue
                home, away = row.get("home"), row.get("away")
                if not home or not away:
                    continue
                try:
                    price = float(row.get("odds") or 0)
                except (TypeError, ValueError):
                    continue
                mkt, sel = row.get("market"), row.get("selection")
                # RT-2: non-decimal garbage must never reach money-facing fields:
                # NaN slips past plain comparisons ("nan" <= 1.0 is False) and inf
                # would poison breakeven (1/inf = 0) and sample-edge (= +inf).
                if not mkt or not sel or not math.isfinite(price) or price <= 1.0:
                    continue
                key = (norm_team(home), norm_team(away))
                pairs = out["pairs"].setdefault(key, {})
                cur = pairs.get((mkt, sel))
                if cur is None or price > cur[0]:
                    pairs[(mkt, sel)] = (price, row.get("bookmaker") or "",
                                         row.get("captured_at") or "")
                out["names"].setdefault(key, (home, away))
    except Exception:
        return out
    return out


def attach_enhancement_price(pick: dict, index: dict[str, Any] | None, *,
                             match_fn: Callable[[object, object], bool] | None = None) -> dict:
    """Attach real-price fields to `pick` for its recommended enhancement (in place).

    Sets (always, so archives carry explicit nulls):
      enhancement_price (float|None), enhancement_price_book, enhancement_price_at,
      enhancement_price_source, enhancement_priced (bool), enhancement_mapped (bool)
    and, when price AND probability exist:
      enhancement_breakeven (= 1/price), enhancement_edge_sample (= prob*price - 1;
      SAMPLE-RATE estimate, not calibration-adjusted — see enh_registry for the gate).

    Pair-constrained: both teams must match a captured fixture (either orientation)
    before any price is attached. Never raises.
    """
    # RT-3: derived fields are RESET unconditionally at entry — never preserved.
    # Any early return below must leave the pick unpriced; a stale price sitting
    # next to a market it was not derived for (or next to an old breakeven/edge)
    # is exactly the misattribution failure this module exists to kill.
    pick["enhancement_price"] = None
    pick["enhancement_price_book"] = None
    pick["enhancement_price_at"] = None
    pick["enhancement_price_source"] = None
    pick["enhancement_priced"] = False
    pick["enhancement_mapped"] = False
    pick.pop("enhancement_breakeven", None)
    pick.pop("enhancement_edge_sample", None)
    market = pick.get("recommended_enhancement")
    mapping = MARKET_PRICE_MAP.get(market)
    pick["enhancement_mapped"] = bool(mapping)
    if not market or not mapping or not index:
        return pick
    try:
        pairs = index.get("pairs") or {}
        names = index.get("names") or {}
        hit_key = (norm_team(pick.get("home")), norm_team(pick.get("away")))
        if hit_key not in pairs:
            hit_key = None
            mfn = match_fn or _default_match_fn()
            if mfn:
                for (nh, na), (raw_h, raw_a) in names.items():
                    both = (mfn(pick.get("home"), raw_h) and mfn(pick.get("away"), raw_a))
                    swap = (mfn(pick.get("home"), raw_a) and mfn(pick.get("away"), raw_h))
                    if both or swap:
                        hit_key = (nh, na)
                        break
        if hit_key is None:
            return pick
        got = pairs.get(hit_key, {}).get(mapping)
        if not got:
            return pick
        price, book, at = got
        pick["enhancement_price"] = round(float(price), 3)
        pick["enhancement_price_book"] = book
        pick["enhancement_price_at"] = at
        pick["enhancement_price_source"] = THEODDSAPI_SOURCE
        pick["enhancement_priced"] = True
        pick["enhancement_breakeven"] = round(1.0 / float(price), 4)
        prob = pick.get("enhancement_probability")
        if prob:
            pick["enhancement_edge_sample"] = round(float(prob) * float(price) - 1.0, 4)
    except Exception:
        return pick
    return pick

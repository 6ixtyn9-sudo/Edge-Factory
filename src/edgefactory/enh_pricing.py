"""Enhancement pricing join — attach real bookmaker prices to enhancement candidates.

The enhancement overlay (compute_dynamic_enhancement in picks_today) historically
recommended markets on probability alone, with no price field anywhere in the path.
The 2026-08-03 audit showed where that leads: negative-EV products surviving
(match_over_15 EV ~-48%, goal_range_2_3 EV ~-49% at estimated prices) and
trivially-priced markets presented as if they were real products (team unders whose
fair price is ~1.03). Probability without price is not evidence of value.

This module closes that loop for every enhancement type that maps to a market we
actually capture. v2 (EXT, "money on the table"): the old theoddsapi-only map left
match_over_15 / match_over_35 / btts_* unpriced even though FREE local feeds
already carry those lines every day — scoutingstats publishes the 1.5/2.5/3.5
ladders + BTTS on its wide fixture rows, and bzzoiro_odds captures ou_2.5 + btts
in the unified schema. Those sources now feed one merged index:

    theoddsapi   localdata/theoddsapi_odds_YYYY-MM.csv.gz   (unified schema)
    bzzoiro_odds localdata/bzzoiro_odds_YYYY-MM.csv.gz      (unified schema;
                 rows store source="bzzoiro" — attribution is tagged by FILE)
    scoutingstats localdata/scoutingstats_YYYY-MM.csv.gz    (wide per-fixture row:
                 odd_o15/odd_u15/.../odd_gg/odd_ng -> tuple rows)
    oddspapi     localdata/oddspapi_odds_YYYY-MM.csv.gz   (unified schema;
                 team totals, double chance, totals, btts, 1x2 — operator
                 override 2026-08-05, Addendum 27.7; flag-gated capture)

Merge semantics: best price across sources per (date, pair, market, selection)
with SOURCE ATTRIBUTION on the winning price, and when >=2 sources price the same
selection, a divergence record (relative spread) is attached so cross-feed
disagreement is visible instead of silently averaged. All reads are local files —
zero network, zero credits.

Fail-soft by design: any error (missing file, bad row, matcher hiccup) degrades
only the affected source to "no contribution" — this join must never raise into
the picks pipeline. Non-finite/junk odds (NaN, inf, <=1.0, garbage) are rejected
at the boundary (RT-2, addendum 9) at every source.
"""
from __future__ import annotations

import csv
import gzip
import math
from pathlib import Path
from typing import Any, Callable

from .util import norm_team

# Enhancement type -> (captured market, selection) or None when the market is not
# captured. Absent/None = unpriceable (display-only; can never look priced).
MARKET_PRICE_MAP: dict[str, tuple[str, str] | None] = {
    # Captured (EXT v2):
    "match_over_15": ("ou_1.5", "over"),     # scoutingstats odd_o15
    "match_under_15": ("ou_1.5", "under"),   # scoutingstats odd_u15
    "match_over_25": ("ou_2.5", "over"),     # theoddsapi + bzzoiro + scoutingstats
    "match_under_25": ("ou_2.5", "under"),   # theoddsapi + bzzoiro + scoutingstats
    "match_over_35": ("ou_3.5", "over"),     # scoutingstats odd_o35
    "match_under_35": ("ou_3.5", "under"),   # scoutingstats odd_u35
    "btts_yes": ("btts", "yes"),             # bzzoiro + scoutingstats odd_gg
    "btts_no": ("btts", "no"),               # bzzoiro + scoutingstats odd_ng
    # theoddsapi totals_alt / team_totals / double_chance (captured by default
    # since 2026-08-05; coverage measured walk-forward):
    "match_over_45": ("ou_4.5", "over"),     # theoddsapi totals/totals_alt @4.5
    "match_under_45": ("ou_4.5", "under"),
    "home_over_05": ("tt_home_0.5", "over"),  # team_totals
    "away_over_05": ("tt_away_0.5", "over"),
    "home_over_15": ("tt_home_1.5", "over"),
    "away_over_15": ("tt_away_1.5", "over"),
    "home_under_15": ("tt_home_1.5", "under"),
    "away_under_15": ("tt_away_1.5", "under"),
    "home_under_25": ("tt_home_2.5", "under"),
    "away_under_25": ("tt_away_2.5", "under"),
    "home_under_35": ("tt_home_3.5", "under"),
    "away_under_35": ("tt_away_3.5", "under"),
    "home_under_45": ("tt_home_4.5", "under"),
    "away_under_45": ("tt_away_4.5", "under"),
    # double_chance is pick-side dependent (1X/X2/12) — handled in
    # attach_enhancement_price, not via this static map:
    "double_chance": ("dc", None),
    # Deliberately unpriceable from the captured feeds (absence is a decision,
    # recorded so nobody "fixes" it blindly later):
    "goal_range_2_3": None,    # banded market — no feed offers it
}

THEODDSAPI_SOURCE = "theoddsapi"
BZZOIRO_SOURCE = "bzzoiro_odds"
SCOUTINGSTATS_SOURCE = "scoutingstats"
ODDSPAPI_SOURCE = "oddspapi"

DIVERGENCE_MIN_SPREAD = 0.10  # flag when max/min best-source prices differ by >10%

# scoutingstats wide-row column map: (market, selection) -> odds column.
# Verified against src/edgefactory/sources/scoutingstats.py COLUMNS (2026-08-03).
_SS_COLMAP: dict[tuple[str, str], str] = {
    ("ou_1.5", "over"): "odd_o15", ("ou_1.5", "under"): "odd_u15",
    ("ou_2.5", "over"): "odd_o25", ("ou_2.5", "under"): "odd_u25",
    ("ou_3.5", "over"): "odd_o35", ("ou_3.5", "under"): "odd_u35",
    ("btts", "yes"): "odd_gg", ("btts", "no"): "odd_ng",
}


def _default_match_fn() -> Callable[[object, object], bool] | None:
    """Lazy-import the adapter's team matcher; None degrades to exact-key-only."""
    try:
        from .sources.theoddsapi import _team_names_match
        return _team_names_match
    except Exception:
        return None


def _month_of(day: str) -> str:
    return (day or "")[:7]


def _parse_price(raw: object) -> float | None:
    """Strict decimal-price parse: reject junk, NaN, inf, and non-decimal value."""
    try:
        price = float(raw)  # float("nan")/float("inf") survive -> gated below
    except (TypeError, ValueError):
        return None
    if not math.isfinite(price) or price <= 1.0:
        return None
    return price


def _put(out: dict[str, Any], nh: str, na: str, mkt: str, sel: str,
         price: float, book: str, at: str, source: str) -> None:
    """Best across sources wins the pair slot; per-source best retained for the
    divergence record (max/min across source bests)."""
    key = (nh, na)
    pairs = out["pairs"].setdefault(key, {})
    slot = (mkt, sel)
    cur = pairs.get(slot)
    if cur is None or price > cur[0]:
        pairs[slot] = (price, book, at, source)
    per_src = out["spread"].setdefault(key, {}).setdefault(slot, {})
    prev = per_src.get(source)
    if prev is None or price > prev:
        per_src[source] = price


def _accumulate_unified(path: Path, *, day: str, source_tag: str,
                        strict_source: str | None, out: dict[str, Any]) -> None:
    """Read a unified-schema odds csv.gz (source,date,...,market,selection,odds,
    bookmaker,captured_at). Fail-soft; contributes nothing on any error."""
    try:
        if not path.exists():
            return
        with gzip.open(path, "rt", newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if strict_source is not None and row.get("source") != strict_source:
                    continue
                if row.get("date") != day:
                    continue
                home, away = row.get("home"), row.get("away")
                mkt, sel = row.get("market"), row.get("selection")
                if not home or not away or not mkt or not sel:
                    continue
                price = _parse_price(row.get("odds"))
                if price is None:
                    continue
                nh, na = norm_team(home), norm_team(away)
                _put(out, nh, na, mkt, sel, price,
                     row.get("bookmaker") or "", row.get("captured_at") or "", source_tag)
                out["names"].setdefault((nh, na), (home, away))
    except Exception:
        return


def _accumulate_scoutingstats(path: Path, *, day: str, out: dict[str, Any]) -> None:
    """Read the scoutingstats wide fixture file: one row per fixture carrying the
    1.5/2.5/3.5 totals ladder + BTTS odds columns. Fail-soft per row."""
    try:
        if not path.exists():
            return
        with gzip.open(path, "rt", newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("date") != day:
                    continue
                home, away = row.get("home"), row.get("away")
                if not home or not away:
                    continue
                nh, na = norm_team(home), norm_team(away)
                for slot, col in _SS_COLMAP.items():
                    price = _parse_price(row.get(col))
                    if price is None:
                        continue
                    _put(out, nh, na, slot[0], slot[1], price, "", "",
                         SCOUTINGSTATS_SOURCE)
                out["names"].setdefault((nh, na), (home, away))
    except Exception:
        return


def load_prices_index(root: Path, day: str) -> dict[str, Any]:
    """Merge all local price sources for `day` into
    {"pairs":  {(nh,na): {(market,sel): (best_price, book, at, source)}},
     "spread": {(nh,na): {(market,sel): {source: best_price_for_that_source}}},
     "names":  {(nh,na): (raw_home, raw_away)}}.
    Fail-soft: any subset of sources may be missing."""
    out: dict[str, Any] = {"pairs": {}, "spread": {}, "names": {}}
    month = _month_of(day)
    localdata = Path(root) / "localdata"
    _accumulate_unified(localdata / f"theoddsapi_odds_{month}.csv.gz",
                        day=day, source_tag=THEODDSAPI_SOURCE,
                        strict_source=THEODDSAPI_SOURCE, out=out)
    _accumulate_unified(localdata / f"bzzoiro_odds_{month}.csv.gz",
                        day=day, source_tag=BZZOIRO_SOURCE,
                        strict_source=None, out=out)
    _accumulate_scoutingstats(localdata / f"scoutingstats_{month}.csv.gz",
                              day=day, out=out)
    # Operator override 2026-08-05 (Addendum 27.7): OddsPapi prices team
    # totals / double chance / totals / btts for the enhancement overlay.
    # File is absent until capture runs; fail-soft like every other source.
    _accumulate_unified(localdata / f"oddspapi_odds_{month}.csv.gz",
                        day=day, source_tag=ODDSPAPI_SOURCE,
                        strict_source=ODDSPAPI_SOURCE, out=out)
    return out


def attach_enhancement_price(pick: dict, index: dict[str, Any] | None, *,
                             match_fn: Callable[[object, object], bool] | None = None) -> dict:
    """Attach real-price fields to `pick` for its recommended enhancement (in place).

    Sets (always, so archives carry explicit nulls):
      enhancement_price (float|None), enhancement_price_book, enhancement_price_at,
      enhancement_price_source ("theoddsapi"|"bzzoiro_odds"|"scoutingstats"|"oddspapi"|None),
      enhancement_priced (bool), enhancement_mapped (bool)
    and, when price AND probability exist:
      enhancement_breakeven (= 1/price), enhancement_edge_sample (= prob*price - 1;
      SAMPLE-RATE estimate, not calibration-adjusted — see enh_registry for the gate).
    When >=2 sources priced the selection, also sets:
      enhancement_price_divergence = {source: price, ..., "spread_pct": float}
      — informational; the best price won, the disagreement is surfaced.

    Derived fields are RESET unconditionally on every call (RT-3): any early
    return leaves the pick unpriced — a stale price next to data it was not
    derived from is exactly the failure this module exists to kill.
    Pair-constrained: both teams must match a captured fixture (either orientation)
    before any price is attached. Never raises.
    """
    pick["enhancement_price"] = None
    pick["enhancement_price_book"] = None
    pick["enhancement_price_at"] = None
    pick["enhancement_price_source"] = None
    pick["enhancement_priced"] = False
    pick["enhancement_mapped"] = False
    pick.pop("enhancement_breakeven", None)
    pick.pop("enhancement_edge_sample", None)
    pick.pop("enhancement_price_divergence", None)
    market = pick.get("recommended_enhancement")
    mapping = MARKET_PRICE_MAP.get(market)
    if market == "double_chance" and mapping and mapping[1] is None:
        side = str(pick.get("pick") or "").strip().lower()
        sel = {"home": "1x", "away": "x2", "draw": "12"}.get(side)
        if sel:
            mapping = ("dc", sel)
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
        price, book, at, source = got
        pick["enhancement_price"] = round(float(price), 3)
        pick["enhancement_price_book"] = book or None
        pick["enhancement_price_at"] = at or None
        pick["enhancement_price_source"] = source
        pick["enhancement_priced"] = True
        pick["enhancement_breakeven"] = round(1.0 / float(price), 4)
        prob = pick.get("enhancement_probability")
        if prob:
            pick["enhancement_edge_sample"] = round(float(prob) * float(price) - 1.0, 4)
        per_src = (index.get("spread") or {}).get(hit_key, {}).get(mapping, {})
        if isinstance(per_src, dict) and len(per_src) >= 2:
            vals = [v for v in per_src.values() if isinstance(v, (int, float))]
            if len(vals) >= 2 and min(vals) > 0:
                spread_pct = max(vals) / min(vals) - 1.0
                if spread_pct > DIVERGENCE_MIN_SPREAD:
                    pick["enhancement_price_divergence"] = {
                        **{k: round(float(v), 3) for k, v in per_src.items()},
                        "spread_pct": round(spread_pct, 4),
                    }
    except Exception:
        return pick
    return pick

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
    betexplorer  localdata/betexplorer_match_detail_<day>.json (schema 2;
                 multi-book comparison responses the priced lane already
                 fetched: O/U lines, BTTS, double chance. Day-scoped evidence,
                 written and read in the same run)
    sharpapi     localdata/sharpapi_odds_shadow_<day>.json (named-book
                 total_goals -> ou_X.Y over/under only; prematch rows; board
                 flag-gated, same as betexplorer)

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
import json
import os
import gzip
import math
from datetime import datetime, timezone
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
# Lowest OddsPapi row generation the enhancement overlay will consume. Must
# track scripts/capture_oddspapi.py:SCHEMA_VERSION (and picks_today's
# ODDSPAPI_MIN_SCHEMA_VERSION); the pairing is asserted in
# tests/test_oddspapi_schema_invalidation.py. Generation 1 mislabelled
# selections; generation 2 wrote no ambiguity check and retained no outcome
# key, so its rows cannot be re-audited from the CSV.
ODDSPAPI_MIN_SCHEMA_VERSION = 3

DIVERGENCE_MIN_SPREAD = 0.10  # flag when max/min best-source prices differ by >10%
# Governance N4 (Addendum 27.11, 2026-08-05): max pre-kickoff capture age in
# hours for OddsPapi rows. Rows captured outside [kickoff - 72h, kickoff] are
# dropped at the merge. The capture pipeline is same-day/next-2-days, so
# nothing legit drops; post-kickoff rows are lookahead artifacts that must
# never price a settled pick.
ODDSPAPI_MAX_AGE_H = 72

BETEXPLORER_SOURCE = "betexplorer"
# SharpAPI named-book totals (total_goals -> ou_X.Y). Shadow ledger, prematch
# rows only (the adapter refuses in-play prices before they are written). The
# board flag gates it like BetExplorer: a source only the board consumes prices
# nothing while the board is off. Same freshness guard as OddsPapi.
SHARPAPI_SOURCE = "sharpapi_odds"
SHARPAPI_MAX_AGE_H = ODDSPAPI_MAX_AGE_H
# The enhancement board's own switch. scripts/auto_tickets reads the same
# variable for the board builder; when it is unset the board does not exist, so
# a source that ONLY the board consumes must not price anything either — one
# meaning, read here at merge time (round-2 ruling, 2026-10-12).
ENH_BOARD_FLAG = "EDGE_FACTORY_ENH_BOARD"


def enhancement_board_enabled() -> bool:
    """True when the operator has switched the enhancement board on."""
    return os.environ.get(ENH_BOARD_FLAG) == "1"
# The detail ledger carries each market's own column labels, so a cell is read
# only when its label is understood here — the site spells double chance "1X",
# BTTS "Yes", totals "Over"; a label outside this map is skipped, never guessed
# by position. (Ledger columns, per the capture: 1x2 "1,X,2"; AH/DNB "1,2";
# totals "Over,Under"; DC "1X,12,X2"; BTTS "Yes,No".)
_BE_COLUMN_SELECTIONS: dict[str, str] = {
    "over": "over", "under": "under",
    "yes": "yes", "no": "no",
    "1x": "1x", "x2": "x2", "12": "12",
}
# Ledger slug -> the market name the index (and MARKET_PRICE_MAP) uses. The
# capture writes BetExplorer's own tab slugs; the map spells BTTS "btts", so a
# reader that passed the slug straight through would file prices under a market
# nothing ever looks up. 1x2 / ah / ha (DNB) are retained evidence only: no
# enhancement maps to them, so they are not read.
_BE_SLUGS: dict[str, str] = {"ou": "ou", "bts": "btts", "dc": "dc"}

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


def _parse_dt(s: object) -> datetime | None:
    """Parse an ISO timestamp to aware UTC; None when unparseable."""
    try:
        dt = datetime.fromisoformat(str(s or "").strip())
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _fresh_row(row: dict[str, Any], max_age_h: float) -> bool:
    """Freshness guard (governance N4, Addendum 27.11).

    Drop rows whose captured_at lies outside [kickoff - max_age_h, kickoff].
    Missing/unparseable timestamps FAIL OPEN (can't judge -> keep the row;
    the guard must never silently kill a source on a format change).
    """
    ko = _parse_dt(row.get("kickoff") or "")
    cap = _parse_dt(row.get("captured_at") or "")
    if ko is None or cap is None:
        return True
    if cap > ko:
        return False  # captured after kickoff - lookahead artifact
    if (ko - cap).total_seconds() > max_age_h * 3600:
        return False  # captured too far before kickoff - early-market noise
    return True


def _accumulate_unified(path: Path, *, day: str, source_tag: str,
                        strict_source: str | None, out: dict[str, Any],
                        max_age_h: float | None = None,
                        min_schema_version: int | None = None) -> None:
    """Read a unified-schema odds csv.gz (source,date,...,market,selection,odds,
    bookmaker,captured_at). Fail-soft; contributes nothing on any error.

    ``min_schema_version`` gates the row generation the same way the
    picks_today bundle reader does: the OddsPapi store mixes generations on
    disk (414 generation-1 rows with mislabelled selections are permanent
    evidence), and blank participants alone are only the symptom - the gate
    is on the generation marker."""
    try:
        if not path.exists():
            return
        with gzip.open(path, "rt", newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if strict_source is not None and row.get("source") != strict_source:
                    continue
                if row.get("date") != day:
                    continue
                if min_schema_version is not None:
                    try:
                        row_schema = int(str(row.get("schema_version") or 0) or 0)
                    except ValueError:
                        row_schema = 0
                    if row_schema < int(min_schema_version):
                        continue
                if max_age_h is not None and not _fresh_row(row, max_age_h):
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


# Stale-price containment (2026-10-02, mirrors picks_today.SCOUTINGSTATS_ODDS_
# MAX_AGE_H): scoutingstats rows carry no true capture stamp (the pick-path
# adapter fabricates captured_at from kickoff), so the month file's mtime is
# the only honest freshness witness. The feed stopped refreshing on
# 2026-09-04; past this age the board is retired from enhancement pricing —
# an unpriced enhancement is honest, a weeks-old price is not. Self-healing:
# the next refreshed file carries a current mtime and pricing resumes.
SCOUTINGSTATS_MAX_AGE_H = 30.0


def _accumulate_scoutingstats(path: Path, *, day: str, out: dict[str, Any]) -> None:
    """Read the scoutingstats wide fixture file: one row per fixture carrying the
    1.5/2.5/3.5 totals ladder + BTTS odds columns. Fail-soft per row."""
    try:
        if not path.exists():
            return
        age_h = (datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) / 3600.0
        if age_h > SCOUTINGSTATS_MAX_AGE_H:
            return  # retired: stale feed withheld from enhancement pricing
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


def _be_line_market(slug: str, line: object) -> str | None:
    """The index's slot for one ledger line: "2.50" -> "ou_2.5".

    The slot spelling is the one MARKET_PRICE_MAP already looks up
    (``ou_1.5``/``ou_2.5``/``ou_3.5``/``ou_4.5``); a line the map does not
    name (0.50, 5.50, a quarter line) still enters the index under its own
    faithful name, it simply has no enhancement that reads it yet.
    """
    try:
        value = float(str(line).replace("+", ""))
    except (TypeError, ValueError):
        return None
    if not math.isfinite(value):
        return None
    return f"{slug}_{value:g}"


def _be_block_cells(slug: str, block: object) -> list[tuple[str, str, float, str, str, bool]]:
    """(market, selection, price, book, at, best) per priced cell of one market.

    Column order is taken from the block's own ``columns`` list, never assumed:
    the capture stores the site's labels, and the row's ``odds``/``created``
    lists are aligned to that same list. A row whose line the block's ``lines``
    list no longer carries is skipped — ``lines`` is the capture's record of
    what survived its per-market cap, so a line absent from it has no retained
    evidence to price from.
    """
    if not isinstance(block, dict):
        return []
    columns = [str(column).strip().lower() for column in (block.get("columns") or [])]
    selections = [_BE_COLUMN_SELECTIONS.get(column) for column in columns]
    lines = {str(line) for line in (block.get("lines") or []) if line is not None}
    cells: list[tuple[str, str, float, str, str, bool]] = []
    for row in block.get("rows") or []:
        if not isinstance(row, dict):
            continue
        odds = list(row.get("odds") or [])
        created = list(row.get("created") or [])
        line = row.get("line")
        if slug == "ou" and lines and line is not None and str(line) not in lines:
            continue
        market = _be_line_market(slug, line) if slug == "ou" else _BE_SLUGS[slug]
        if market is None:
            continue
        for index, selection in enumerate(selections):
            if not selection:
                continue
            price = _parse_price(odds[index] if index < len(odds) else None)
            if price is None:
                continue
            at = str(created[index]) if index < len(created) and created[index] else ""
            cells.append((market, selection, price,
                          str(row.get("bookmaker") or ""), at, bool(row.get("best"))))
    return cells


def _accumulate_betexplorer(path: Path, *, day: str, out: dict[str, Any]) -> None:
    """Read the schema-2 BetExplorer detail ledger for `day` (one file per day).

    Operator directive 2026-10-12, confirmed in this same PR in
    docs/operator/BETEXPLORER-LICENSING.md: the detail the priced lane already
    fetched is the enhancement board's price source, and the registry floor —
    not EV — decides what is a bet.

    Producer: ``sources.betexplorer_odds._persist_match_detail`` — the match
    page's blocks plus one comparison response per market, each retained with
    its own column labels, handicap lines and per-bookmaker rows. Prices are
    taken the way the operator reads that page by hand: a row the site flagged
    as a best-price offer wins, else the highest retained price for the
    selection; the price keeps the row's own bookmaker and creation stamp as
    its attribution. No EV gate — the registry floor, not this reader, decides
    whether a price is bettable.

    Fail-soft: an absent, foreign-schema, unreadable or empty ledger
    contributes nothing and never raises.
    """
    try:
        if not path.exists():
            return
        payload = json.loads(path.read_text())
        if not isinstance(payload, dict) or int(payload.get("schema") or 0) != 2:
            return
        fixtures = payload.get("fixtures")
        if not isinstance(fixtures, dict):
            return
        ledger_day = str(payload.get("date") or "")[:10]
        if ledger_day and ledger_day != str(day)[:10]:
            return  # a ledger under the wrong day's name prices nothing
        for entry in fixtures.values():
            if not isinstance(entry, dict):
                continue
            home, away = entry.get("home"), entry.get("away")
            if not home or not away:
                continue
            flagged: dict[tuple[str, str], tuple[float, str, str]] = {}
            highest: dict[tuple[str, str], tuple[float, str, str]] = {}
            markets = entry.get("markets")
            for slug, block in (markets or {}).items() if isinstance(markets, dict) else ():
                if str(slug) not in _BE_SLUGS:
                    continue  # not a market this overlay prices
                for market, selection, price, book, at, best in _be_block_cells(str(slug), block):
                    slot = (market, selection)
                    if slot not in highest or price > highest[slot][0]:
                        highest[slot] = (price, book, at)
                    if best and (slot not in flagged or price > flagged[slot][0]):
                        flagged[slot] = (price, book, at)
            if not highest:
                continue
            nh, na = norm_team(home), norm_team(away)
            for (market, selection) in highest:
                price, book, at = flagged.get((market, selection)) or highest[(market, selection)]
                _put(out, nh, na, market, selection, price, book, at, BETEXPLORER_SOURCE)
            out["names"].setdefault((nh, na), (home, away))
    except Exception:
        return


def _accumulate_sharpapi(path: Path, *, day: str, out: dict[str, Any]) -> None:
    """Read the day's SharpAPI shadow ledger (JSON: {"rows": [...]}). Only the
    over/under totals ladder is consumed; moneyline rows are not read here.
    Fail-soft on any error; a row outside the freshness window is dropped."""
    try:
        if not path.exists():
            return
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("date") not in (None, day):
            return
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            if row.get("source") != SHARPAPI_SOURCE or row.get("date") != day:
                continue
            mkt = str(row.get("market") or "")
            if not mkt.startswith("ou_"):
                continue
            sel = str(row.get("selection") or "")
            if sel not in ("over", "under"):
                continue
            home, away = row.get("home"), row.get("away")
            if not home or not away:
                continue
            if not _fresh_row(row, SHARPAPI_MAX_AGE_H):
                continue
            price = _parse_price(row.get("odds"))
            if price is None:
                continue
            nh, na = norm_team(home), norm_team(away)
            _put(out, nh, na, mkt, sel, price,
                 row.get("bookmaker") or row.get("book") or "",
                 row.get("captured_at") or "", SHARPAPI_SOURCE)
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
                        strict_source=BZZOIRO_SOURCE, out=out)
    _accumulate_scoutingstats(localdata / f"scoutingstats_{month}.csv.gz",
                              day=day, out=out)
    # BetExplorer detail ledger (schema 2, day-scoped): the comparison
    # responses the priced lane already fetched for this day. Zero network —
    # the file is local, and an absent ledger simply contributes nothing.
    #
    # Behind the board's own switch (round-2 ruling, 2026-10-12): with
    # EDGE_FACTORY_ENH_BOARD unset this source contributes nothing at all, so
    # the board renders exactly as it did before the source existed — same
    # inputs, same bytes. The switch is read here, at merge time, so a ledger on
    # disk can never price anything while the board is off.
    if enhancement_board_enabled():
        _accumulate_betexplorer(
            localdata / f"betexplorer_match_detail_{str(day)[:10]}.json",
            day=day, out=out)
        _accumulate_sharpapi(
            localdata / f"sharpapi_odds_shadow_{str(day)[:10]}.json",
            day=day, out=out)
    # Operator override 2026-08-05 (Addendum 27.7): OddsPapi prices team
    # totals / double chance / totals / btts for the enhancement overlay.
    # REAL flag gate (red-team finding F6, fixed 2026-08-05): the store is
    # merged ONLY when EDGE_FACTORY_ODDSPAPI_PRICES=1. Without the flag, a
    # stale oddspapi file present on disk must not silently feed prices.
    if os.environ.get("EDGE_FACTORY_ODDSPAPI_PRICES") == "1":
        _accumulate_unified(localdata / f"oddspapi_odds_{month}.csv.gz",
                            day=day, source_tag=ODDSPAPI_SOURCE,
                            strict_source=ODDSPAPI_SOURCE, out=out,
                            max_age_h=ODDSPAPI_MAX_AGE_H,
                            min_schema_version=ODDSPAPI_MIN_SCHEMA_VERSION)
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
    pick["enhancement_multi_source"] = False  # governance N5: True when >=2 sources priced this selection
    market = pick.get("recommended_enhancement")
    mapping = MARKET_PRICE_MAP.get(market)
    if market == "double_chance" and mapping and mapping[1] is None:
        side = str(pick.get("pick") or "").strip().lower()
        # draw -> None (red-team F5, fixed 2026-08-05): "12" (home-or-away)
        # is a HEDGE against the draw, not an enhancement of it. A draw pick
        # cannot be enhanced with double chance; leave it unpriced.
        sel = {"home": "1x", "away": "x2", "draw": None}.get(side)
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
        if isinstance(per_src, dict):
            pick["enhancement_multi_source"] = (
                sum(1 for v in per_src.values() if isinstance(v, (int, float)) and v > 1.0) >= 2)
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

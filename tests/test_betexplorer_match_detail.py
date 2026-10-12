"""Retained BetExplorer match detail: one comparison response per market.

The priced lane must stay bit-identical (its best-1x2 triple, its call list,
its cache); everything else here is bounded evidence written to
localdata/betexplorer_match_detail_YYYY-MM-DD.json. Markup shapes are taken
from live public match-odds responses inspected 2026-10-12 — bookmaker label
in the span title / link text / data-bookie, data-odd + data-created +
data-pos + movement arrow on every price, the hidden all-bookmakers block
with its own average line, the per-market thead labels, the per-handicap
tbody ids (`best-odds-<line>`) and the two-place / letter ranks the site
writes (`data-pos="02"`, `data-pos="y"`) — and from the rendered match page,
whose standings block serves the whole league table behind its client-side
"Show full table" toggle.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest  # noqa: E402

import scripts.capture_betexplorer as capture  # noqa: E402
from edgefactory.sources import betexplorer_match_snapshot as snap  # noqa: E402
from edgefactory.sources import betexplorer_odds as be  # noqa: E402

MATCH_URL = "https://www.betexplorer.com/football/england/premier-league/coventry-newcastle-utd/tW4rOkzg/"
ODDS_URL = "https://www.betexplorer.com/match-odds/tW4rOkzg/1/1x2/bestOdds/?lang=en"
MARKET_URL = "https://www.betexplorer.com/match-odds/tW4rOkzg/1/{slug}/bestOdds/?lang=en"
LISTING_URLS = [
    "https://www.betexplorer.com/football/results/?year=2026&month=10&day=11",
    "https://www.betexplorer.com/football/results/?year=2026&month=10&day=12",
]

ODDS_HTML = """
<table class="table-main oddsComparison__table best-odds-0" id="sortable-1">
<thead><tr><th class="unsortable over-s-only"></th><th class="unsortable under-s-only"></th>
<th class="unsortable tablet-desktop-only"></th>
<th class="table-main__detail-odds" data-okey="">1</th>
<th class="table-main__detail-odds" data-okey="">X</th>
<th class="table-main__detail-odds" data-okey="">2</th></tr></thead>
<tbody id="best-odds-0">
<tr  data-bo="true" data-bid="549" data-bookie-id="1105 " data-originid="29">
<td class="h-text-left over-s-only h-text-pl10"><a href="/bookmaker/1105/https://www.bet365.com/x" class="in-bookmaker-logo-link in-bookmaker-logo-link--primary l549" rel="nofollow" data-bid="1105">bet365.us</a></td>
<td class="h-text-left under-s-only h-text-pl10"><a href="/bookmaker/1105/https://www.bet365.com/x" rel="nofollow"><span class="in-bookmaker-logo l549" title="bet365.us"></span></a></td>
<td data-bookmaker-id="549" class="archiveOddsMovement__odds table-main__detail-odds" data-odd="3.10" data-created="12,10,2026,05,52" data-pos="1" data-bookie="bet365.us" data-bt="1"><i class="icon icon__decreasing table-main__icon"></i> <img src="/res/icon.svg" alt="Redirect"/></td>
<td data-bookmaker-id="549" class="archiveOddsMovement__odds table-main__detail-odds colored js-has-aodds archiveOddsMovement__odds_best" data-odd="3.60" data-created="10,10,2026,05,13" data-pos="0" data-bookie="bet365.us" data-bt="1"><i class="icon icon__decreasing table-main__icon"></i> <img src="/res/icon.svg" alt="Redirect"/></td>
<td data-bookmaker-id="549" class="archiveOddsMovement__odds table-main__detail-odds colored js-has-aodds archiveOddsMovement__odds_best" data-odd="2.20" data-created="12,10,2026,05,52" data-pos="2" data-bookie="bet365.us" data-bt="1"><i class="icon icon__increasing table-main__icon"></i> <img src="/res/icon.svg" alt="Redirect"/></td>
</tr>
</tbody></table>
<input data-handicap="0" type="hidden" value="4" id="bcount-0"/>
<div data-all-handicap="0" class="hidden oddsComparisonAll__fullTable oddsComparisonAll__bestOdds" >
<div class="oddsComparisonAll__contentDiv">
<div class="oddsComparisonAll__odds_heads">
<div class="oddsComparisonAll__average_text" data-odd="3.06"></div><div class="oddsComparisonAll__average_text" data-odd="3.53"></div><div class="oddsComparisonAll__average_text" data-odd="2.17"></div>
</div>
<div class="hidden oddsComparisonAll__content collapse-0">
<div class="oddsComparisonAll__rowBookie"  data-bo="true" data-bid="549" data-originid="29">
<div class="over-s-only"><a href="/bookmaker/1105/x" class="in-bookmaker-logo-link in-bookmaker-logo-link--primary l549" rel="nofollow" data-bid="1105">bet365.us</a></div>
<div class="under-s-only"><a href="/bookmaker/1105/x" rel="nofollow"><span class="in-bookmaker-logo l549" title="bet365.us"></span></a></div>
<div class="oddsComparisonAll__odds_heads ">
<div data-bookmaker-id="549" class="archiveOddsMovement__odds oddsComparisonAll__odds table-main__detail-odds" data-odd="3.10" data-created="12,10,2026,05,52" data-pos="1" data-bookie="bet365.us"><i class="icon icon__decreasing"></i></div>
<div data-bookmaker-id="549" class="archiveOddsMovement__odds oddsComparisonAll__odds table-main__detail-odds" data-odd="3.60" data-created="10,10,2026,05,13" data-pos="0" data-bookie="bet365.us"><i class="icon icon__decreasing"></i></div>
<div data-bookmaker-id="549" class="archiveOddsMovement__odds oddsComparisonAll__odds table-main__detail-odds" data-odd="2.20" data-created="12,10,2026,05,52" data-pos="2" data-bookie="bet365.us"><i class="icon icon__increasing"></i></div>
</div>
</div>
<div class="oddsComparisonAll__rowBookie"  data-bo="true" data-bid="997" data-originid="1">
<div class="over-s-only"><a href="/bookmaker/1089/x" class="in-bookmaker-logo-link in-bookmaker-logo-link--primary l997" rel="nofollow" data-bid="1089">Stake.com</a></div>
<div class="under-s-only"><a href="/bookmaker/1089/x" rel="nofollow"><span class="in-bookmaker-logo l997" title="Stake.com"></span></a></div>
<div class="oddsComparisonAll__odds_heads ">
<div data-bookmaker-id="997" class="archiveOddsMovement__odds oddsComparisonAll__odds table-main__detail-odds" data-odd="3.15" data-created="12,10,2026,05,03" data-pos="1" data-bookie="stake.com"></div>
<div data-bookmaker-id="997" class="archiveOddsMovement__odds oddsComparisonAll__odds table-main__detail-odds" data-odd="3.60" data-created="12,10,2026,05,03" data-pos="0" data-bookie="stake.com"></div>
<div data-bookmaker-id="997" class="archiveOddsMovement__odds oddsComparisonAll__odds table-main__detail-odds" data-odd="2.19" data-created="12,10,2026,05,53" data-pos="2" data-bookie="stake.com"></div>
</div>
</div>
</div></div></div>
<input type="hidden" value="3" id="best-odds-limit"/>
"""

UNNAMED_HTML = """
<table class="table-main oddsComparison__table best-odds-0"><tbody id="best-odds-0">
<tr data-bid="1"><td data-odd="2.00" data-created="12,10,2026,04,00" data-pos="0"></td>
<td data-odd="3.40" data-created="12,10,2026,04,00" data-pos="0"></td>
<td data-odd="3.50" data-created="12,10,2026,04,00" data-pos="0"></td></tr>
</tbody></table>
"""


def _table_head(*labels: str) -> str:
    cells = "".join(f'<th class="unsortable"></th>' for _ in range(3))
    odds = "".join(f'<th class="table-main__detail-odds" data-okey="">{label}</th>'
                   for label in labels)
    return f"<thead><tr>{cells}{odds}</tr></thead>"


def _ou_table(line: str, book: str, bid: str, odds: tuple[float, float]) -> str:
    return (
        f'<table data-handicap="{line}" class="table-main sortable oddsComparison__table '
        f'table-collapse-{line} best-odds-{line}" id="sortable-1">'
        f'{_table_head("Over", "Under")}'
        f'<tbody id="best-odds-{line}">'
        f'<tr data-bo="true" data-bid="{bid}" data-bookie-id="{bid} ">'
        f'<td class="h-text-left over-s-only h-text-pl10"><a href="/bookmaker/{bid}/x" '
        f'class="in-bookmaker-logo-link in-bookmaker-logo-link--primary" rel="nofollow" '
        f'data-bid="{bid}">{book}</a></td>'
        f'<td class="h-text-left under-s-only h-text-pl10"><a href="/bookmaker/{bid}/x" '
        f'rel="nofollow"><span class="in-bookmaker-logo" title="{book}"></span></a></td>'
        f'<td class="h-text-left tablet-desktop-only"></td>'
        f'<td class="table-main__doubleparameter">{line.lstrip("0")}</td>'
        f'<td data-bookmaker-id="{bid}" class="archiveOddsMovement__odds table-main__detail-odds '
        f'table-main__detail-odds--first colored js-has-aodds" data-odd="{odds[0]:.2f}" '
        f'data-created="11,10,2026,12,24" data-pos="1" data-bookie="{book}" data-bt="2" '
        f'data-hcp="E-2-2-0-{line}-0"><i class="icon icon__increasing table-main__icon"></i></td>'
        f'<td data-bookmaker-id="{bid}" class="archiveOddsMovement__odds table-main__detail-odds '
        f'colored js-has-aodds" data-odd="{odds[1]:.2f}" data-created="11,10,2026,12,24" '
        f'data-pos="2" data-bookie="{book}" data-bt="2" data-hcp="E-2-2-0-{line}-0">'
        f'<i class="icon icon__decreasing table-main__icon"></i></td>'
        f'</tr></tbody></table>'
    )


def _all_section(line: str, book: str, bid: str, odds: tuple[float, float],
                 averages: tuple[float, float]) -> str:
    return (
        f'<div data-all-handicap="{line}" class="hidden oddsComparisonAll__fullTable oddsComparisonAll__bestOdds">'
        f'<div class="oddsComparisonAll__contentDiv"><div class="oddsComparisonAll__odds_heads">'
        f'<div class="oddsComparisonAll__average_text" data-odd="{averages[0]:.2f}"></div>'
        f'<div class="oddsComparisonAll__average_text" data-odd="{averages[1]:.2f}"></div>'
        f'</div><div class="hidden oddsComparisonAll__content collapse-{line}">'
        f'<div class="oddsComparisonAll__rowBookie" data-bo="true" data-bid="{bid}" data-originid="1">'
        f'<div class="over-s-only"><a href="/bookmaker/{bid}/x" class="in-bookmaker-logo-link '
        f'in-bookmaker-logo-link--primary" rel="nofollow" data-bid="{bid}">{book}</a></div>'
        f'<div class="under-s-only"><a href="/bookmaker/{bid}/x" rel="nofollow">'
        f'<span class="in-bookmaker-logo" title="{book}"></span></a></div>'
        f'<div class="oddsComparisonAll__odds_heads ">'
        f'<div data-bookmaker-id="{bid}" class="archiveOddsMovement__odds oddsComparisonAll__odds '
        f'table-main__detail-odds" data-odd="{odds[0]:.2f}" data-created="12,10,2026,05,03" '
        f'data-pos="1" data-bookie="{book.lower()}"></div>'
        f'<div data-bookmaker-id="{bid}" class="archiveOddsMovement__odds oddsComparisonAll__odds '
        f'table-main__detail-odds" data-odd="{odds[1]:.2f}" data-created="12,10,2026,05,03" '
        f'data-pos="2" data-bookie="{book.lower()}"></div>'
        f'</div></div></div></div>'
    )


OU_HTML = (
    _ou_table("0.50", "bet365.us", "1105", (1.04, 13.00))
    + _ou_table("2.50", "BetMGM.us", "1103", (3.30, 1.35))
    + _all_section("0.50", "Unibet", "1088", (1.04, 13.00), (1.04, 13.00))
    + _all_section("2.50", "Stake.com", "1089", (3.40, 1.30), (3.40, 1.30))
)

AH_HTML = (
    f'<table data-handicap="-1.50" class="table-main sortable oddsComparison__table '
    f'table-collapse--1.50 best-odds--1.50" id="sortable-1">{_table_head("1", "2")}'
    f'<tbody id="best-odds--1.50"><tr data-bid="549" data-bookie-id="1105 ">'
    f'<td class="h-text-left over-s-only h-text-pl10"><a href="/bookmaker/1105/x" '
    f'class="in-bookmaker-logo-link in-bookmaker-logo-link--primary" rel="nofollow" '
    f'data-bid="1105">bet365.us</a></td>'
    f'<td class="table-main__doubleparameter">-1.5</td>'
    f'<td data-bookmaker-id="549" class="archiveOddsMovement__odds table-main__detail-odds" '
    f'data-odd="2.10" data-created="12,10,2026,05,52" data-pos="1" data-bookie="bet365.us" '
    f'data-bt="5" data-hcp="E-5-2-0--1.5-0"></td>'
    f'<td data-bookmaker-id="549" class="archiveOddsMovement__odds table-main__detail-odds" '
    f'data-odd="1.75" data-created="12,10,2026,05,52" data-pos="2" data-bookie="bet365.us" '
    f'data-bt="5" data-hcp="E-5-2-0--1.5-0"></td>'
    f'</tr></tbody></table>'
)

HA_HTML = (
    f'<table data-handicap="0" class="table-main sortable best-odds-0" id="sortable-1">'
    f'{_table_head("1", "2")}<tbody id="best-odds-0">'
    f'<tr data-bid="997" data-bookie-id="1089 ">'
    f'<td class="h-text-left over-s-only h-text-pl10"><a href="/bookmaker/1089/x" '
    f'class="in-bookmaker-logo-link in-bookmaker-logo-link--primary" rel="nofollow" '
    f'data-bid="1089">Stake.com</a></td>'
    f'<td data-bookmaker-id="997" class="archiveOddsMovement__odds table-main__detail-odds" '
    f'data-odd="1.90" data-created="12,10,2026,05,53" data-pos="1" data-bookie="stake.com" '
    f'data-bt="6" data-hcp="E-6-2-0-0-0"></td>'
    f'<td data-bookmaker-id="997" class="archiveOddsMovement__odds table-main__detail-odds" '
    f'data-odd="2.05" data-created="12,10,2026,05,53" data-pos="2" data-bookie="stake.com" '
    f'data-bt="6" data-hcp="E-6-2-0-0-0"></td>'
    f'</tr></tbody></table>'
)

DC_HTML = (
    f'<table data-handicap="0" class="table-main sortable best-odds-0" id="sortable-1">'
    f'{_table_head("1X", "12", "X2")}<tbody id="best-odds-0">'
    f'<tr data-bid="549" data-bookie-id="1105 ">'
    f'<td class="h-text-left over-s-only h-text-pl10"><a href="/bookmaker/1105/x" '
    f'class="in-bookmaker-logo-link in-bookmaker-logo-link--primary" rel="nofollow" '
    f'data-bid="1105">bet365.us</a></td>'
    f'<td data-bookmaker-id="549" class="archiveOddsMovement__odds table-main__detail-odds" '
    f'data-odd="1.26" data-created="12,10,2026,05,52" data-pos="10" data-bookie="bet365.us" '
    f'data-bt="4"></td>'
    f'<td data-bookmaker-id="549" class="archiveOddsMovement__odds table-main__detail-odds" '
    f'data-odd="1.36" data-created="12,10,2026,05,52" data-pos="12" data-bookie="bet365.us" '
    f'data-bt="4"></td>'
    f'<td data-bookmaker-id="549" class="archiveOddsMovement__odds table-main__detail-odds" '
    f'data-odd="2.05" data-created="12,10,2026,05,52" data-pos="02" data-bookie="bet365.us" '
    f'data-bt="4"></td>'
    f'</tr></tbody></table>'
)

BTS_HTML = (
    f'<table data-handicap="0" class="table-main sortable best-odds-0" id="sortable-1">'
    f'{_table_head("Yes", "No")}<tbody id="best-odds-0">'
    f'<tr data-bid="549" data-bookie-id="1105 ">'
    f'<td class="h-text-left over-s-only h-text-pl10"><a href="/bookmaker/1105/x" '
    f'class="in-bookmaker-logo-link in-bookmaker-logo-link--primary" rel="nofollow" '
    f'data-bid="1105">bet365.us</a></td>'
    f'<td data-bookmaker-id="549" class="archiveOddsMovement__odds table-main__detail-odds '
    f'table-main__detail-odds--first js-has-aodds" data-odd="1.57" data-created="12,09,2026,18,41" '
    f'data-pos="y" data-bookie="bet365.us" data-bt="13"></td>'
    f'<td data-bookmaker-id="549" class="archiveOddsMovement__odds table-main__detail-odds '
    f'js-has-aodds" data-odd="2.25" data-created="12,09,2026,18,41" data-pos="n" '
    f'data-bookie="bet365.us" data-bt="13"></td>'
    f'</tr></tbody></table>'
)

MARKET_HTML = {"1x2": ODDS_HTML, "ou": OU_HTML, "ah": AH_HTML,
               "ha": HA_HTML, "dc": DC_HTML, "bts": BTS_HTML}

MATCH_PAGE = """
<div>Home Football England Premier League 2026/2027 Coventry - Newcastle 12.10.2026</div>
<h2>Head to Head: Last 6</h2>
<div>Coventry Newcastle Utd 0 wins 1 draw 5 wins 0% 17% 83%</div>
<div>Championship 2009/2010 1 X 2 17.02.2010 <a href="/x/">Newcastle 4 : 1 Coventry</a></div>
<div>13.01.2001 <a href="/y/">Newcastle 3 : 1 Coventry</a> 1.68 3.40 4.20</div>
<div>06.09.2000 <a href="/z/">Coventry 0 : 2 Newcastle</a> 2.50 2.90 2.70</div>
<a href="/more/">Show more matches</a>
<h2>Standings</h2>
<div># Team MP W D L G GD Pts Form</div>
<div>1. Manchester City 6 6 0 0 16:5 11 18</div>
<div>2. Arsenal 6 5 0 1 10:5 5 15</div>
<div>11. Newcastle 5 2 2 1 9:9 0 8</div>
<div>19. Coventry 5 1 0 4 1:10 -9 3</div>
<div>20. Fulham 6 0 2 4 6:10 -4 2</div>
<a href="/full/">Show full table</a>
<div>Last results: Coventry Show: Premier League 2026/2027 all tournaments</div>
<div>19.09.2026 <a href="/a/">Nottingham 0 : 1 Coventry</a> 1.64 3.87 5.52</div>
<div>13.09.2026 <a href="/b/">Coventry 0 : 5 Brighton</a></div>
<div>Last results: Newcastle Utd Show: Premier League 2026/2027 all tournaments</div>
<div>19.09.2026 <a href="/c/">Newcastle 2 : 1 Hull</a> 1.60 4.31 5.15</div>
"""

LISTING_PAGE = """
<tr class="js-tournament"><td class="table-main__tournament">England: Premier League</a></td></tr>
<tr data-dt="12,10,2026,21,0">
  <td class="table-main__tt"><a href="/football/england/premier-league/coventry-newcastle-utd/tW4rOkzg/">Coventry - Newcastle Utd</a></td>
</tr>
"""

PICK = {"date": "2026-10-12", "home": "Coventry", "away": "Newcastle Utd", "market": "1x2"}
LEDGER = "betexplorer_match_detail_2026-10-12.json"


@pytest.fixture(autouse=True)
def _reset_be(tmp_path, monkeypatch):
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    be.reset_fetch_count()
    yield
    be.reset_fetch_count()


def _slug_of(url: str) -> str | None:
    match = re.search(r"/match-odds/[^/]+/[^/]+/([a-z0-9]+)/bestOdds/", url)
    return match.group(1) if match else None


def _transport(calls: list[str], *, seen: list | None = None):
    def fake_fetch(url, referer=None, retries=3, timeout=20, **kwargs):
        calls.append(url)
        if seen is not None:
            seen.append((_slug_of(url), kwargs.get("min_interval")))
        slug = _slug_of(url)
        if slug:
            return json.dumps({"odds": MARKET_HTML.get(slug, "")})
        if url == MATCH_URL:
            return MATCH_PAGE
        return LISTING_PAGE
    return fake_fetch


def _run_pick(pick: dict = PICK, *, calls: list[str] | None = None):
    be._match_cache.clear()
    be._fixture_cache.clear()
    transport = _transport(calls if calls is not None else [])
    with mock.patch.object(be, "_fetch", transport):
        return be.betexplorer_odds_rows_for_pick(pick, "2026-10-12")


# --- the per-market parse ---------------------------------------------------

def test_market_columns_lines_and_prices_come_from_the_response():
    market = be.parse_market_response(OU_HTML)
    # Labels are the page's own thead; lines are the page's own tbody ids,
    # ordered nearest level first.
    assert market["columns"] == ["Over", "Under"]
    assert market["lines"] == ["0.50", "2.50"]
    # Both lines are covered by their own all-bookmakers section, so the
    # site's "every bookmaker" view wins there.
    assert [(row["bookmaker"], row["line"], row["source"]) for row in market["rows"]] == [
        ("Unibet", "0.50", "all"), ("Stake.com", "2.50", "all")]
    unibet = market["rows"][0]
    assert unibet["bookmaker_id"] == "1088"
    assert unibet["odds"] == [1.04, 13.00]
    assert unibet["pos"] == ["1", "2"]
    assert unibet["created"] == ["2026-10-12T05:03", "2026-10-12T05:03"]
    assert market["named_rows"] == 2
    assert market["bookmakers"] == ["Stake.com", "Unibet"]
    # Several lines mean several average lines: per line, never a flat guess.
    assert market["average"] is None
    assert market["average_by_line"] == {"0.50": [1.04, 13.00], "2.50": [3.40, 1.30]}


def test_a_line_the_all_block_does_not_cover_keeps_the_table_rows():
    market = be.parse_market_response(
        _ou_table("0.50", "bet365.us", "1105", (1.04, 13.00))
        + _all_section("2.50", "Stake.com", "1089", (3.40, 1.30), (3.40, 1.30)))
    assert [(row["bookmaker"], row["line"], row["source"]) for row in market["rows"]] == [
        ("bet365.us", "0.50", "table"), ("Stake.com", "2.50", "all")]


def test_single_line_markets_keep_the_pages_own_columns_and_ranks():
    btts = be.parse_market_response(BTS_HTML)
    assert btts["columns"] == ["Yes", "No"]
    assert btts["lines"] == ["0"]
    assert btts["rows"][0]["pos"] == ["y", "n"]
    assert btts["rows"][0]["odds"] == [1.57, 2.25]
    assert btts["rows"][0]["created"] == ["2026-09-12T18:41", "2026-09-12T18:41"]

    chance = be.parse_market_response(DC_HTML)
    assert chance["columns"] == ["1X", "12", "X2"]
    # Two-place ranks stay as the page wrote them ("02" is not rank 2).
    assert chance["rows"][0]["pos"] == ["10", "12", "02"]

    handicap = be.parse_market_response(AH_HTML)
    assert handicap["columns"] == ["1", "2"]
    assert handicap["lines"] == ["-1.50"]
    assert handicap["rows"][0]["odds"] == [2.10, 1.75]


def test_unnamed_rows_are_never_given_a_bookmaker():
    market = be.parse_market_response(UNNAMED_HTML)
    assert market["rows_count"] == 1
    assert market["named_rows"] == 0
    assert market["rows"][0]["bookmaker"] is None
    assert market["rows"][0]["odds"] == [2.00, 3.40, 3.50]


def test_multi_line_markets_are_capped_to_the_lines_nearest_level():
    lines = [f"{0.5 * step:.2f}" for step in range(1, 13)]           # 0.50 .. 6.00
    books = [f"bk{index}" for index in range(9)]                     # 9 books per line
    html_text = "".join(
        _ou_table(line, book, book.lstrip("bk"), (1.0 + index / 10, 2.0 + index / 10))
        for line in lines for index, book in enumerate(books))
    market = be.parse_market_response(html_text)
    # 12 lines x 9 books arrive; the cap keeps the lines nearest level with at
    # most six books each, and `lines` always describes the rows that remain.
    assert market["rows_count"] == be._MAX_MARKET_ROWS == 48
    counts = Counter(row["line"] for row in market["rows"])
    assert set(counts) == set(market["lines"])
    assert market["lines"] == lines[:len(market["lines"])]
    assert len(market["lines"]) <= be._MAX_MARKET_LINES
    assert set(counts.values()) == {be._MAX_MARKET_BOOKS_PER_LINE}


def test_single_line_markets_keep_up_to_24_bookmakers():
    books = [f"bk{index}" for index in range(30)]
    html_text = "".join(
        _ou_table("0", book, book.lstrip("bk"), (1.5 + index / 100, 2.5))
        for index, book in enumerate(books))
    market = be.parse_market_response(html_text)
    assert market["rows_count"] == be._MAX_BOOKS_RETAINED == 24


def test_best_triple_contract_is_unchanged():
    assert be.parse_best_1x2(ODDS_HTML) == {"odd1": 3.10, "oddx": 3.60, "odd2": 2.20}
    assert be.parse_best_1x2("") is None


# --- the match-page blocks --------------------------------------------------

def test_match_page_blocks_read_h2h_last_results_and_standings():
    blocks = snap.parse_match_page_blocks(MATCH_PAGE)
    assert blocks["blocks"] == ["h2h", "last_results", "standings"]
    assert blocks["h2h_meetings"] == 6
    # "1 draw" (singular) must parse; the old plural-only grammar missed it.
    assert blocks["h2h_record"] == {"home_wins": 0, "draws": 1, "away_wins": 5}
    first, second = blocks["h2h_rows"][0], blocks["h2h_rows"][1]
    assert first["date"] == "2010-02-17" and first["score"] == [4, 1]
    assert first["odds"] is None
    assert second["odds"] == [1.68, 3.40, 4.20]
    # One row per played match, each carrying the label of its own block.
    results = blocks["last_results_rows"]
    assert [row["label"] for row in results] == ["Coventry", "Coventry", "Newcastle Utd"]
    assert [row["date"] for row in results] == ["2026-09-19", "2026-09-13", "2026-09-19"]
    assert results[0]["score"] == [0, 1]
    assert results[0]["odds"] == [1.64, 3.87, 5.52]
    assert results[1]["odds"] is None
    # The standings block is the page's whole table, read from its own
    # columns — never a text excerpt that truncates it.
    assert blocks["standings_columns"] == ["#", "Team", "MP", "W", "D", "L",
                                           "G", "GD", "Pts", "Form"]
    assert [row["rank"] for row in blocks["standings_rows"]] == [1, 2, 11, 19, 20]
    assert blocks["standings_rows"][0] == {
        "rank": 1, "team": "Manchester City", "mp": 6, "wins": 6, "draws": 0,
        "losses": 0, "goals_for": 16, "goals_against": 5, "goal_difference": 11,
        "points": 18,
    }
    coventry = blocks["standings_rows"][3]
    assert (coventry["team"], coventry["goal_difference"], coventry["points"]) == \
        ("Coventry", -9, 3)
    assert "standings_excerpt" not in blocks


def test_the_whole_table_and_h2h_list_are_read_not_the_collapsed_view():
    """The page's "Show full table" / "Show more matches" only toggle rows
    that are already served, so the whole list is read — bounded, never
    truncated to the collapsed view."""
    rows = "".join(
        f"<div>{rank}. Club {rank:02d} 6 3 1 2 {10 + rank}:{rank} {10} {rank * 3}</div>"
        for rank in range(1, 25))
    table = ("<h2>Standings</h2><div># Team MP W D L G GD Pts Form</div>"
             + rows + "<a href='/full/'>Show full table</a><div>Last results: Club 01</div>")
    blocks = snap.parse_match_page_blocks(table)
    assert len(blocks["standings_rows"]) == 24
    assert blocks["standings_rows"][-1]["team"] == "Club 24"

    meetings = "".join(f"<div>{day:02d}.01.200{index % 10} A {index}:0 B</div>"
                       for index, day in enumerate(range(1, 46)))
    h2h = ("<h2>Head to Head: Last 6</h2><div>A B 0 wins 1 draw 5 wins</div>"
           + meetings + "<a>Show more matches</a>")
    assert len(snap.parse_match_page_blocks(h2h)["h2h_rows"]) == be._MAX_H2H_ROWS == 40


def test_a_digit_leading_club_name_stays_in_the_team_field():
    table = ("<h2>Standings</h2><div># Team MP W D L G GD Pts Form</div>"
             "<div>8. 1899 Hoffenheim 6 2 3 1 8:6 2 9</div>"
             "<div>9. 1. FC Koln 6 1 0 5 4:14 -10 3</div>"
             "<a href='/full/'>Show full table</a>")
    rows = snap.parse_match_page_blocks(table)["standings_rows"]
    assert [row["team"] for row in rows] == ["1899 Hoffenheim", "1. FC Koln"]
    assert rows[1]["goal_difference"] == -10


# --- the wired capture ------------------------------------------------------

def test_capture_retains_every_market_from_one_response_per_market(tmp_path):
    calls: list[str] = []
    rows = _run_pick(calls=calls)

    # The priced lane is exactly what it was: three best-price rows.
    assert [row["selection"] for row in rows] == ["home", "draw", "away"]
    assert [row["odds"] for row in rows] == [3.10, 3.60, 2.20]
    assert {row["bookmaker"] for row in rows} == {"betexplorer_best"}

    # Two adjacent-day listing probes (the second one matches), the match page,
    # then one comparison response per market, in the page's own tab order.
    assert calls == LISTING_URLS + [MATCH_URL, ODDS_URL] + [
        MARKET_URL.format(slug=slug) for slug in ("ou", "ah", "ha", "dc", "bts")]
    assert not any("/bookmaker/" in url for url in calls)

    payload = json.loads((tmp_path / LEDGER).read_text())
    assert payload["schema"] == 2 and payload["date"] == "2026-10-12"
    (entry,) = payload["fixtures"].values()
    assert entry["event_id"] == "tW4rOkzg"
    assert entry["page_param"] == "1"
    assert entry["best_1x2"] == {"odd1": 3.10, "oddx": 3.60, "odd2": 2.20}
    assert entry["market_failures"] == []
    assert sorted(entry["markets"]) == ["1x2", "ah", "bts", "dc", "ha", "ou"]

    one_x_two = entry["markets"]["1x2"]
    assert one_x_two["columns"] == ["1", "X", "2"]
    assert one_x_two["average"] == [3.06, 3.53, 2.17]
    assert one_x_two["bookmakers"] == ["Stake.com", "bet365.us"]
    assert {row["bookmaker"] for row in one_x_two["rows"]} == {"bet365.us", "Stake.com"}

    over_under = entry["markets"]["ou"]
    assert over_under["lines"] == ["0.50", "2.50"]
    assert over_under["average"] is None
    assert over_under["average_by_line"] == {"0.50": [1.04, 13.00], "2.50": [3.40, 1.30]}

    assert entry["markets"]["bts"]["columns"] == ["Yes", "No"]
    assert entry["markets"]["ha"]["lines"] == ["0"]
    assert entry["markets"]["dc"]["rows"][0]["pos"] == ["10", "12", "02"]

    assert entry["page"]["blocks"] == ["h2h", "last_results", "standings"]
    assert entry["page"]["h2h_record"] == {"home_wins": 0, "draws": 1, "away_wins": 5}
    assert entry["page"]["challenge"] is False
    standings = entry["page"]["standings_rows"]
    assert entry["page"]["standings_rows_count"] == len(standings) == 5
    assert [row["rank"] for row in standings] == [1, 2, 11, 19, 20]
    assert standings[3]["team"] == "Coventry" and standings[3]["points"] == 3
    assert entry["page"]["standings_columns"] == ["#", "Team", "MP", "W", "D", "L",
                                                  "G", "GD", "Pts", "Form"]
    # No raw HTML is ever retained.
    assert "<td" not in json.dumps(payload) and "<div" not in json.dumps(payload)


def test_market_tab_requests_take_the_wider_interval():
    seen: list[tuple] = []
    be._match_cache.clear()
    be._fixture_cache.clear()
    with mock.patch.object(be, "_fetch", _transport([], seen=seen)):
        be.betexplorer_odds_rows_for_pick(PICK, "2026-10-12")
    intervals = dict(seen)
    assert be._MARKET_INTERVAL >= 5.1
    for slug in ("ou", "ah", "ha", "dc", "bts"):
        assert intervals[slug] == be._MARKET_INTERVAL
    # The priced lane's own requests keep their existing spacing.
    assert intervals["1x2"] is None and intervals[None] is None


def test_market_tabs_can_be_turned_off(tmp_path, monkeypatch):
    monkeypatch.setattr(be, "MARKET_TABS_ENABLED", False)
    calls: list[str] = []
    rows = _run_pick(calls=calls)
    assert [row["odds"] for row in rows] == [3.10, 3.60, 2.20]
    assert calls == LISTING_URLS + [MATCH_URL, ODDS_URL]
    (entry,) = json.loads((tmp_path / LEDGER).read_text())["fixtures"].values()
    assert sorted(entry["markets"]) == ["1x2"]


def test_market_tabs_stop_at_the_run_request_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(be, "_MAX_REQUESTS_PER_RUN", 4)
    be._request_count = 4
    calls: list[str] = []
    rows = _run_pick(calls=calls)
    assert [row["odds"] for row in rows] == [3.10, 3.60, 2.20]
    assert calls == LISTING_URLS + [MATCH_URL, ODDS_URL]
    assert be.request_stats()["market_budget_stop"] is True
    (entry,) = json.loads((tmp_path / LEDGER).read_text())["fixtures"].values()
    assert sorted(entry["markets"]) == ["1x2"]


def test_market_failures_are_recorded_without_touching_the_priced_lane(tmp_path):
    def flaky_fetch(url, referer=None, retries=3, timeout=20, **kwargs):
        if _slug_of(url) == "bts":
            raise RuntimeError("gone")
        return _transport([])(url, referer=referer, retries=retries, timeout=timeout, **kwargs)

    be._match_cache.clear()
    be._fixture_cache.clear()
    with mock.patch.object(be, "_fetch", flaky_fetch):
        rows = be.betexplorer_odds_rows_for_pick(PICK, "2026-10-12")
    assert [row["odds"] for row in rows] == [3.10, 3.60, 2.20]
    (entry,) = json.loads((tmp_path / LEDGER).read_text())["fixtures"].values()
    assert entry["market_failures"] == ["bts"]
    assert sorted(entry["markets"]) == ["1x2", "ah", "dc", "ha", "ou"]
    assert be.request_stats()["market_requests"] == 5


def test_cache_hit_makes_no_request_and_adds_no_detail(tmp_path):
    calls: list[str] = []
    first = _run_pick(calls=calls)
    ledger = tmp_path / LEDGER
    before = ledger.read_text()

    be._match_cache.clear()
    be._fixture_cache.clear()
    calls.clear()
    be.reset_fetch_count()
    transport = _transport(calls)
    with mock.patch.object(be, "_fetch", transport):
        second = be.betexplorer_odds_rows_for_pick(PICK, "2026-10-12")

    assert second == first
    assert calls == []
    assert ledger.read_text() == before


def test_detail_write_failure_never_breaks_the_priced_lane(monkeypatch):
    def explode(*_args, **_kwargs):
        raise RuntimeError("disk full")

    monkeypatch.setattr(be, "_persist_match_detail", explode)
    rows = _run_pick()
    assert [row["odds"] for row in rows] == [3.10, 3.60, 2.20]


def test_a_stub_fetch_leaves_no_stale_detail(monkeypatch):
    match = {"date": "2026-10-12", "kickoff": "21:00", "country": "England",
             "league": "Premier League", "home": "Coventry", "away": "Newcastle Utd",
             "match_url": MATCH_URL, "event_id": "tW4rOkzg"}
    monkeypatch.setattr(be, "fetch_day_matches", lambda day: [match] if day == "2026-10-12" else [])
    monkeypatch.setattr(be, "fetch_match_odds", lambda url, event_id: {"odd1": 1.9, "oddx": 3.3, "odd2": 4.4})
    be._match_cache.clear()
    be._fixture_cache.clear()
    be.LAST_MATCH_DETAIL = {"markets": {"1x2": {"rows": [{"bookmaker": "Leftover"}]}},
                            "page": None, "captured_at": "2026-10-12T00:00:00+00:00"}
    rows = be.betexplorer_odds_rows_for_pick(PICK, "2026-10-12")
    assert [row["odds"] for row in rows] == [1.9, 3.3, 4.4]
    assert not (Path(be.LOCALDATA) / LEDGER).exists()


# --- the receipt ------------------------------------------------------------

def test_wrapper_receipt_summarises_the_detail_ledger(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    (tmp_path / LEDGER).write_text(json.dumps({
        "schema": 2, "date": "2026-10-12",
        "fixtures": {
            "2026-10-12|coventry|newcastleutd": {
                "markets": {
                    "1x2": {"rows": [{}, {}], "named_rows": 2, "bookmakers": ["a", "b"]},
                    "ou": {"rows": [{}], "named_rows": 1, "bookmakers": ["a"]},
                },
                "page": {"blocks": ["h2h", "standings"], "challenge": False,
                         "standings_rows": [{}, {}]},
            },
            "2026-10-12|other|side": {
                "markets": {"1x2": {"rows": [], "named_rows": 0, "bookmakers": []}},
                "page": {"blocks": ["last_results"], "challenge": True},
            },
        },
    }))
    summary = capture._detail_summary("2026-10-12")
    assert summary == {"fixtures": 2, "markets": 3, "market_rows": 3, "named_rows": 3,
                       "bookmakers": 3, "standings_rows": 2, "with_h2h": 1,
                       "with_last_results": 1, "with_standings": 1,
                       "challenge_pages": 1}
    assert capture._detail_summary("2026-10-11")["fixtures"] == 0

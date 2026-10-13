"""Row-level BetExplorer join guard, and same-day captured prices reaching pricing.

Two live defects, both measured on origin/main tip ``0576d26`` (2026-10-12):

1. A MIS-JOINED ROW. ``localdata/betexplorer_odds_cache_2026-10-12.json`` holds
   the key ``2026-10-12|forge|yorkunited`` whose fixture block says home
   "Forge" / away "York United", but whose three rows are Forge vs INTER
   TORONTO 1.35 / 4.80 / 6.40 — a different match entirely. The cache KEY is
   built from the pick's teams while the ROWS are built from the matched PAGE's
   teams, so when ``match_pick_to_betexplorer`` accepts a one-sided partial
   match ("Forge" == "Forge") another fixture's prices are cached under the
   pick's key. The existing squad-marker veto cannot see this: "York United" and
   "Inter Toronto" carry no markers, they are simply different clubs.

2. CAPTURED PRICES NEVER REACHING THE BOARD. ``enrich_unmatched_with_betexplorer``
   tested its rescue budget BEFORE reading the free same-day cache and used
   ``break``, abandoning the whole loop. On the 2026-10-12 board four legs were
   already priced by ``betexplorer_odds``, so ``priced == BE_RESCUE_TARGET_LEGS
   == 4`` when the loop reached its first unmatched pick and every later leg was
   skipped — including Ludogorets–Arda (1.50 / 4.00 / 6.50) and Elfsborg–Halmstad
   (1.36 / 5.25 / 8.00), both captured at 01:05Z, both already in this run's own
   cache, both published with ``odds = None`` and
   ``odds_match_status = "unmatched"``. A leg may be unpriced because there is no
   price — never because of ordering.

The committed rows below are byte-identical to the receipt except for
``captured_at``, which each test regenerates as "now" so the 24h
``CACHE_FRESHNESS_H`` guard cannot time-rot the test (the receipt's original
values are quoted in the fixtures).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import picks_today as pt  # noqa: E402
from edgefactory.sources import betexplorer_odds as be  # noqa: E402

DAY = "2026-10-12"

# Receipt: 2026-10-12|forge|yorkunited — fixture Forge v York United, rows Forge
# v Inter Toronto (captured 2026-10-12T01:05:56.751682+00:00).
FORGE_ROWS = [
    {"home": "Forge", "away": "Inter Toronto", "market": "1x2", "selection": sel,
     "odds": odds, "bookmaker": "betexplorer_best", "date": DAY, "kickoff": "18:00",
     "league": "Canada: Canadian Premier League"}
    for sel, odds in (("home", 1.35), ("draw", 4.8), ("away", 6.4))
]

# Receipt: 2026-10-12|ludogoretsrazgrad|ardakardzhali, captured 01:06:08Z. The
# page abbreviates both clubs; the pick does not. These must keep pricing.
LUDOGORETS_ROWS = [
    {"home": "Ludogorets", "away": "Arda", "market": "1x2", "selection": sel,
     "odds": odds, "bookmaker": "betexplorer_best", "date": DAY, "kickoff": "18:00",
     "league": "Bulgaria: efbet League"}
    for sel, odds in (("home", 1.5), ("draw", 4.0), ("away", 6.5))
]

# Receipt: 2026-10-12|ifelfsborg|halmstad, captured 2026-10-11T22:08:54Z.
ELFSBORG_ROWS = [
    {"home": "Elfsborg", "away": "Halmstad", "market": "1x2", "selection": sel,
     "odds": odds, "bookmaker": "betexplorer_best", "date": DAY, "kickoff": "18:00",
     "league": "Sweden: Allsvenskan"}
    for sel, odds in (("home", 1.36), ("draw", 5.25), ("away", 8.0))
]

FORGE_PICK = {"home": "Forge", "away": "York United", "pick": "home",
              "market": "1x2", "kickoff": "18:00", "date": DAY}
LUDOGORETS_PICK = {"home": "Ludogorets Razgrad", "away": "Arda Kardzhali",
                   "pick": "home", "market": "1x2", "kickoff": "13:00", "date": DAY}
ELFSBORG_PICK = {"home": "IF Elfsborg", "away": "Halmstad", "pick": "home",
                 "market": "1x2", "kickoff": "13:00", "date": DAY}


def _stamp(rows):
    """Rows with a fresh capture stamp (see module docstring)."""
    now = datetime.now(timezone.utc).isoformat()
    return [{**row, "captured_at": now} for row in rows]


def _write_cache(localdata: Path, key: str, fixture_home: str, fixture_away: str,
                 rows: list[dict]) -> None:
    """Add one fixture to the day's cache file (merging with the entries there).

    The reader treats the file as a multi-fixture map, so a second call must add
    its entry alongside the first rather than replace the whole file.
    """
    localdata.mkdir(parents=True, exist_ok=True)
    path = localdata / f"betexplorer_odds_cache_{DAY}.json"
    payload = {"schema": 1, "date": DAY, "fixtures": {}}
    if path.exists():
        payload["fixtures"] = json.loads(path.read_text())["fixtures"]
    payload["fixtures"][key] = {
        "home": fixture_home, "away": fixture_away,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }
    path.write_text(json.dumps(payload))


@pytest.fixture(autouse=True)
def _isolated_localdata(tmp_path, monkeypatch):
    """Point the adapter's cache root at this test's own temp localdata.

    ``betexplorer_odds.LOCALDATA`` is resolved ONCE, at import time, from
    EDGE_FACTORY_LOCALDATA (and conftest strips that variable before any test
    runs). Setting the env var here therefore does not move the adapter: the
    tests would write their cache under tmp_path while the reader looked in the
    repository's localdata/, find nothing, and see empty rows. Patch the module
    attribute the reader actually uses, as the other BetExplorer suites do.
    """
    localdata = tmp_path / "localdata"
    localdata.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(be, "LOCALDATA", localdata)
    monkeypatch.setenv("EDGE_FACTORY_LOCALDATA", str(localdata))
    monkeypatch.delenv("EDGE_FACTORY_BE_RESCUE_TARGET_LEGS", raising=False)
    be.reset_fetch_count()
    yield
    be.reset_fetch_count()


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """No test in this module may touch the network."""
    import urllib.request

    def _refuse(*_args, **_kwargs):
        raise AssertionError("this test must not make a network request")

    monkeypatch.setattr(urllib.request, "urlopen", _refuse)


# --------------------------------------------------------------------------
# 1. the mis-joined row (bug 8.1)
# --------------------------------------------------------------------------

def test_forge_inter_toronto_row_can_never_price_york_united(tmp_path, monkeypatch):
    """The exact pair from the receipt: the row is Forge v Inter Toronto."""
    localdata = tmp_path / "localdata"
    _write_cache(localdata, f"{DAY}|forge|yorkunited", "Forge", "York United",
                 _stamp(FORGE_ROWS))

    assert be.cached_odds_rows_for_pick(FORGE_PICK, DAY) == []
    census = be.run_stats()["be_rows_rejected_reasons"]
    assert census.get(be.ROW_REJECT_TEAMS) == len(FORGE_ROWS), census


def test_row_guard_is_a_rule_not_a_special_case():
    ok, reason = be.row_belongs_to_pick(FORGE_ROWS[0], FORGE_PICK, DAY)
    assert (ok, reason) == (False, be.ROW_REJECT_TEAMS)
    # Same-orientation and swapped orientation both count when BOTH teams agree.
    assert be.row_belongs_to_pick({"home": "A", "away": "B"}, {"home": "A", "away": "B"}, DAY)[0]
    assert be.row_belongs_to_pick({"home": "B", "away": "A"}, {"home": "A", "away": "B"}, DAY)[0]
    # One team agreeing is exactly what used to let the wrong fixture through.
    assert not be.row_belongs_to_pick({"home": "A", "away": "Z"},
                                      {"home": "A", "away": "B"}, DAY)[0]


def test_a_row_dated_outside_the_pick_window_is_dropped():
    row = {**FORGE_ROWS[0], "home": "Forge", "away": "York United", "date": "2026-10-20"}
    ok, reason = be.row_belongs_to_pick(row, FORGE_PICK, DAY)
    assert (ok, reason) == (False, be.ROW_REJECT_DATE)
    # The fetch path deliberately searches +/-1 day for timezone offsets, so a
    # neighbouring date stays in-window.
    for neighbour in ("2026-10-11", "2026-10-13"):
        row = {**FORGE_ROWS[0], "home": "Forge", "away": "York United", "date": neighbour}
        assert be.row_belongs_to_pick(row, FORGE_PICK, DAY)[0]


def test_bare_clock_kickoff_is_never_a_rejection_basis():
    """Bare HH:MM is region-relative; judging it would drop real rows.

    The receipt's own leg pair: the pick says 13:00, the page says 18:00, and the
    row is still the right fixture (Ludogorets–Arda, Elfsborg–Halmstad).
    """
    for row, pick in ((LUDOGORETS_ROWS[0], LUDOGORETS_PICK),
                      (ELFSBORG_ROWS[0], ELFSBORG_PICK)):
        assert row["kickoff"] != pick["kickoff"]
        assert be.row_belongs_to_pick(row, pick, DAY)[0]
    # A provable-instant mismatch IS a rejection (both sides carry offsets).
    row = {**FORGE_ROWS[0], "home": "Forge", "away": "York United",
           "date": DAY, "kickoff": "2026-10-12T18:00:00+00:00"}
    pick = {**FORGE_PICK, "kickoff": "2026-10-12T21:00:00+00:00"}
    assert not be.row_belongs_to_pick(row, pick, DAY)[0]


def test_legitimate_display_variants_keep_pricing(tmp_path):
    """The guard must not break the abbreviation forms the page really serves."""
    localdata = tmp_path / "localdata"
    _write_cache(localdata, f"{DAY}|ludogoretsrazgrad|ardakardzhali",
                 "Ludogorets Razgrad", "Arda Kardzhali", _stamp(LUDOGORETS_ROWS))
    _write_cache(localdata, f"{DAY}|ifelfsborg|halmstad",
                 "IF Elfsborg", "Halmstad", _stamp(ELFSBORG_ROWS))

    rows = be.cached_odds_rows_for_pick(LUDOGORETS_PICK, DAY)
    assert [r["selection"] for r in rows] == ["home", "draw", "away"]
    assert [r["odds"] for r in rows] == [1.5, 4.0, 6.5]
    assert len(be.cached_odds_rows_for_pick(ELFSBORG_PICK, DAY)) == 3
    assert be.run_stats()["be_rows_rejected"] == 0


def test_the_poisoned_key_cannot_price_through_the_fetch_door(tmp_path):
    """One code path: the fetch entry point serves the guarded cache reader."""
    localdata = tmp_path / "localdata"
    _write_cache(localdata, f"{DAY}|forge|yorkunited", "Forge", "York United",
                 _stamp(FORGE_ROWS))
    assert be.betexplorer_odds_rows_for_pick(FORGE_PICK, DAY) == []
    # ...and the refused entry is still a cached answer, not a miss.
    assert be.cached_fixture_present(FORGE_PICK, DAY)


# --------------------------------------------------------------------------
# 2. same-day captured prices reaching pricing (bug 8.2)
# --------------------------------------------------------------------------

def _priced_leg(tag: str) -> dict:
    """A leg BetExplorer already priced — these consume the rescue budget."""
    return {"home": f"Priced {tag}", "away": f"Rival {tag}", "pick": "home",
            "market": "1x2", "odds": 1.5, "odds_source": pt.BETEXPLORER_ODDS_SOURCE,
            "odds_match_method": "exact", "kickoff": "18:00", "date": DAY}


def test_captured_rows_price_a_leg_once_the_rescue_budget_is_met(tmp_path):
    """The 2026-10-12 regression, reproduced end to end.

    Four legs are already priced by betexplorer_odds, so the bounded rescue
    target is met before the loop reaches the unpriced leg below. Its price is
    already in this run's own cache (captured 01:05Z) and must land anyway.
    """
    localdata = tmp_path / "localdata"
    _write_cache(localdata, f"{DAY}|ludogoretsrazgrad|ardakardzhali",
                 "Ludogorets Razgrad", "Arda Kardzhali", _stamp(LUDOGORETS_ROWS))

    priced_legs = [_priced_leg(str(i)) for i in range(pt.BE_RESCUE_TARGET_LEGS)]
    target_leg = {"home": "Ludogorets Razgrad", "away": "Arda Kardzhali",
                  "pick": "home", "market": "1x2", "odds": None, "odds_source": None,
                  "odds_match_method": "none", "kickoff": "13:00", "date": DAY}
    picks = [*priced_legs, target_leg]

    stats: dict = {}
    enriched = pt.enrich_unmatched_with_betexplorer(picks, DAY, max_fetches=0, stats=stats)

    assert enriched == 1
    assert stats["be_priced_before"] == pt.BE_RESCUE_TARGET_LEGS
    assert target_leg["odds"] == 1.5
    assert target_leg["odds_source"] == pt.BETEXPLORER_ODDS_SOURCE
    assert target_leg["odds_match_method"] == "betexplorer"
    assert target_leg["price_evidence"] == pt.PRICE_EVIDENCE_BETEXPLORER_RESCUE
    assert target_leg["price_push_eligible"] is True
    assert target_leg["bookmaker"] == "betexplorer_best"
    assert target_leg["odds_league"] == "Bulgaria: efbet League"
    assert [e["selection"] for e in target_leg["price_board"]] == ["home", "draw", "away"]
    # The already-priced legs are never overwritten or re-requested.
    assert all(leg["odds"] == 1.5 for leg in priced_legs)


def test_an_already_priced_leg_is_never_overwritten_by_the_cache(tmp_path):
    localdata = tmp_path / "localdata"
    _write_cache(localdata, f"{DAY}|ifelfsborg|halmstad", "IF Elfsborg", "Halmstad",
                 _stamp(ELFSBORG_ROWS))
    leg = {"home": "IF Elfsborg", "away": "Halmstad", "pick": "home", "market": "1x2",
           "odds": 1.44, "odds_source": "pinnapi_odds", "odds_match_method": "exact",
           "kickoff": "18:00", "date": DAY}
    assert pt.enrich_unmatched_with_betexplorer([leg], DAY, max_fetches=0) == 0
    assert leg["odds"] == 1.44 and leg["odds_source"] == "pinnapi_odds"
    # ...but the cached rows are still kept as board corroboration.
    assert {e["source"] for e in leg["price_board"]} == {pt.BETEXPLORER_ODDS_SOURCE}


def test_a_leg_with_no_price_is_left_unpriced_not_mis_joined(tmp_path):
    """Honest absence: no cache entry, no budget -> no odds, nothing invented."""
    localdata = tmp_path / "localdata"
    _write_cache(localdata, f"{DAY}|forge|yorkunited", "Forge", "York United",
                 _stamp(FORGE_ROWS))
    priced_legs = [_priced_leg(str(i)) for i in range(pt.BE_RESCUE_TARGET_LEGS)]
    leg = dict(FORGE_PICK, pick="home", market="1x2", odds=None, odds_source=None,
               odds_match_method="none")

    stats: dict = {}
    assert pt.enrich_unmatched_with_betexplorer([*priced_legs, leg], DAY,
                                                max_fetches=0, stats=stats) == 0
    assert leg["odds"] is None
    assert leg.get("price_board") in (None, [])
    assert stats["be_rows_rejected"] >= 1

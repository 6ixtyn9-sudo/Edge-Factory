"""Miss accounting must cover the donors that are actually alive.

`donor_join_diagnostics` buckets every unmatched provider row by its first
honest failure. It was wired to the shadow donors plus OddsPAPI, but NOT to
TheOddsAPI or BetExplorer -- the only two priced boards returning rows through
2026-10-03..07. Measured from the committed receipts:

    day         source       usable  matched  unmatched  accounted
    2026-10-03  theoddsapi      589        0        589          0
    2026-10-04  theoddsapi      302        0        302          0
    2026-10-05  theoddsapi      365        0        365          0
    2026-10-06  theoddsapi      155        3        152          0
    2026-10-03  betexplorer      21        0         21          0
    2026-10-06  betexplorer      12        3          9          0

1,423 TheOddsAPI rows and 98 BetExplorer rows unmatched with zero recorded
reason, while OddsPAPI and Bet Better were 100% accounted on the same days.

These tests pin that the live boards are diagnosed, that the accounting is
arithmetically complete, and -- most importantly -- that diagnostics changed
no matching rule.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def _picks_today():
    spec = importlib.util.spec_from_file_location(
        "picks_today_join", ROOT / "scripts" / "picks_today.py"
    )
    mod = importlib.util.module_from_spec(spec)
    saved = sys.argv
    sys.argv = ["picks_today"]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    return mod


PT = _picks_today()


def _pick(home="Croatia", away="Spain", day="2026-10-06", sel="home"):
    return {
        "date": day, "market": "1x2", "pick": sel,
        "home": home, "away": away,
        "kickoff": f"{day}T18:45:00+00:00",
    }


def _raw(home, away, day, market="1x2", sel="home", odds=1.80, kickoff=True):
    row = {
        "home": home, "away": away, "date": day,
        "market": market, "selection": sel, "odds": odds,
    }
    if kickoff:
        row["kickoff"] = f"{day}T18:45:00+00:00"
    return row


# --------------------------------------------------------------------------
# the live boards are now diagnosed
# --------------------------------------------------------------------------

def test_theoddsapi_and_betexplorer_are_diagnosed_donors():
    """Guards the regression that produced 1,423 silent zeros."""
    src = Path(ROOT / "scripts" / "picks_today.py").read_text()
    block = src.split("diagnosed_donor_names = {", 1)[1].split("}", 1)[0]
    assert "THEODDSAPI_ODDS_SOURCE" in block
    assert "BETEXPLORER_ODDS_SOURCE" in block
    assert "ODDSPAPI_ODDS_SOURCE" in block


def test_betexplorer_join_report_reaches_its_health_row():
    """`betexplorer_odds` (bundle) vs `betexplorer` (health key). Without the
    alias the report is computed and silently dropped."""
    src = Path(ROOT / "scripts" / "picks_today.py").read_text()
    assert "join_report_health_key" in src
    assert 'BETEXPLORER_ODDS_SOURCE: "betexplorer"' in src


# --------------------------------------------------------------------------
# the accounting is complete
# --------------------------------------------------------------------------

def test_every_unmatched_row_lands_in_exactly_one_bucket():
    picks = [_pick()]
    rows = [
        _raw("Croatia", "Spain", "2026-10-06"),                      # matches
        _raw("Nowhere FC", "Elsewhere", "2026-10-06"),               # fixture miss
        _raw("Croatia", "Spain", "2026-11-20"),                      # out_of_window
        _raw("", "", "2026-10-06"),                                  # identity missing
        _raw("Croatia", "Spain", "2026-10-06", market="corners"),    # market bucket
    ]
    bundle = {"provider": "theoddsapi", "input_rows": rows}
    report = PT.donor_join_diagnostics(picks, [bundle])
    row = report["theoddsapi"]
    total = int(row.get("matched_rows") or 0) + sum(
        int(v) for v in (row.get("miss_counts") or {}).values())
    assert total == len(rows), (
        f"{len(rows)} rows in, {total} accounted -- a row vanished: {row}")


def test_out_of_window_is_distinguished_from_fixture_miss():
    """Bet Better publishes a multi-day board; calling that a 'mismatch'
    implied a bug that is not there."""
    picks = [_pick()]
    bundle = {"provider": "theoddsapi",
              "input_rows": [_raw("Croatia", "Spain", "2026-12-25")]}
    misses = PT.donor_join_diagnostics(picks, [bundle])["theoddsapi"]["miss_counts"]
    assert misses.get("out_of_window") == 1
    assert "fixture_key_miss" not in misses


def test_teamless_row_is_an_identity_defect_not_coverage():
    picks = [_pick()]
    bundle = {"provider": "theoddsapi",
              "input_rows": [_raw("", "", "2026-10-06")]}
    misses = PT.donor_join_diagnostics(picks, [bundle])["theoddsapi"]["miss_counts"]
    assert misses.get("fixture_identity_missing") == 1


def test_matching_row_is_counted_matched_not_missed():
    picks = [_pick()]
    bundle = {"provider": "theoddsapi",
              "input_rows": [_raw("Croatia", "Spain", "2026-10-06")]}
    row = PT.donor_join_diagnostics(picks, [bundle])["theoddsapi"]
    assert int(row["matched_rows"]) == 1
    assert sum(int(v) for v in (row.get("miss_counts") or {}).values()) == 0


def test_diagnostics_do_not_loosen_the_join():
    """The headline safety property: a row the real matcher rejects must stay
    rejected. Diagnostics may only explain, never admit."""
    picks = [_pick()]
    near_miss = _raw("Croatia", "Spain B", "2026-10-06")
    bundle = {"provider": "theoddsapi", "input_rows": [near_miss]}
    row = PT.donor_join_diagnostics(picks, [bundle])["theoddsapi"]
    one = PT._odds_bundle_from_rows(
        [PT.canonicalize_row(near_miss)[0]], provider="theoddsapi")
    really_matches = PT.find_side_keyed_odds_row(picks[0], one)[0] is not None
    assert int(row["matched_rows"]) == (1 if really_matches else 0)


def test_row_without_kickoff_cannot_join_its_own_fixture():
    """Documented seam, found while wiring this up: the bundle index is built
    from the row's `kickoff`. A row carrying the right teams and the right
    date but no kickoff does NOT join, and is bucketed
    `no_pick_for_fixture` -- which reads as 'we had no pick for this match'
    when the truth is 'the provider row had no kickoff stamp'. Pinned as
    current behaviour so a future bucket rename is a deliberate act."""
    picks = [_pick()]
    bundle = {"provider": "theoddsapi",
              "input_rows": [_raw("Croatia", "Spain", "2026-10-06",
                                  kickoff=False)]}
    row = PT.donor_join_diagnostics(picks, [bundle])["theoddsapi"]
    assert int(row["matched_rows"]) == 0
    assert row["miss_counts"].get("no_pick_for_fixture") == 1


def test_empty_bundle_is_safe():
    assert PT.donor_join_diagnostics([_pick()], []) == {}
    report = PT.donor_join_diagnostics(
        [_pick()], [{"provider": "theoddsapi", "input_rows": []}])
    assert int(report["theoddsapi"]["matched_rows"]) == 0

"""Form estimate for every supported selection (form_intel.selection_form_probability).

The fixture is small enough to count by hand. Alpha has 6 prior games (3 wins,
3 losses), Beta has 9 (3 losses to Alpha, 6 draws), and Alpha beat Beta 3 times.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for extra in ("src", "scripts"):
    if str(ROOT / extra) not in sys.path:
        sys.path.insert(0, str(ROOT / extra))

from edgefactory import form_intel as fi  # noqa: E402


def _row(day, home, away, hs, gs):
    return {"date": day, "home": home, "away": away, "hs": hs, "gs": gs,
            "league": "T", "source": "unit"}


@pytest.fixture()
def archive():
    rows = []
    for i in range(6):
        rows.append(_row(f"2026-01-{i + 1:02d}", "Alpha", "Beta" if i % 2 == 0 else "Gamma",
                         2 if i % 2 == 0 else 0, 1))
    for i in range(6):
        rows.append(_row(f"2026-02-{i + 1:02d}", "Beta", "Gamma", 1, 1))
        rows.append(_row(f"2026-03-{i + 1:02d}", "Gamma", "Delta", 0, 0))
    return fi.ResultsArchive(rows, trunc={})


def test_home_win_matches_hand_count(archive):
    out = fi.selection_form_probability(archive, "home_win", "Alpha", "Beta", "2026-04-01")
    # (Alpha W 3/6 -> 4/8) (Beta L 3/9 -> 4/11) (h2h Alpha W 3/3 -> 4/5)
    expected = (4 / 8 + 4 / 11 + 4 / 5) / 3
    assert out["p"] == pytest.approx(expected)
    assert out["counts"] == {"home_form": 6, "away_form": 9, "h2h": 3}


def test_match_totals_and_btts_are_complements_per_component(archive):
    over = fi.selection_form_probability(archive, "over_2.5", "Alpha", "Beta", "2026-04-01")
    under = fi.selection_form_probability(archive, "under_2.5", "Alpha", "Beta", "2026-04-01")
    assert over["p"] + under["p"] == pytest.approx(1.0)
    yes = fi.selection_form_probability(archive, "btts_yes", "Alpha", "Beta", "2026-04-01")
    no = fi.selection_form_probability(archive, "btts_no", "Alpha", "Beta", "2026-04-01")
    assert yes["p"] + no["p"] == pytest.approx(1.0)


def test_team_totals_use_only_the_named_side(archive):
    # Alpha scored 2 in its 3 wins and 0 in 3 losses, so home over 0.5 is 3/6 in form.
    out = fi.selection_form_probability(archive, "home_over_0.5", "Alpha", "Beta", "2026-04-01")
    assert out["counts"]["team_form"] == 6
    assert out["components"]["team_form"] == pytest.approx((3 + 1) / (6 + 2))


def test_unsupported_selections_are_refused():
    with pytest.raises(ValueError):
        fi.parse_selection("over_3.0")          # whole line: push possible
    with pytest.raises(ValueError):
        fi.parse_selection("home_handicap_-1.5")


def test_thin_history_returns_no_estimate():
    rows = [_row("2026-01-01", "Alpha", "Beta", 1, 0)]
    arch = fi.ResultsArchive(rows, trunc={})
    out = fi.selection_form_probability(arch, "home_win", "Alpha", "Beta", "2026-02-01")
    assert out["p"] is None and out["insufficient_history"] is True

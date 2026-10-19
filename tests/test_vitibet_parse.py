"""Offline parse checks for the vitibet quicktips adapter.

No network. The HTML below is a synthetic row, not a capture; it pins the two
final-score render shapes the adapter must accept.
"""
from edgefactory.sources import vitibet


def _row(score_markup: str, probs=("+0.54", "42%", "28%", "30%")) -> str:
    prob_spans = "".join(f"<span class='prob-val'>{p}</span>" for p in probs)
    return (
        "<a href='/index.php?clanek=match-detail&sekce=fotbal&lang=en&fixture_id=1'>"
        "<div class='livescore-match-row'>"
        "<span class='livescore-team-name'>CRB</span>"
        "<span class='livescore-team-name'>Botafogo-SP</span>"
        f"{prob_spans}"
        f"{score_markup}"
        "</div></a>"
    )


def test_two_element_final_score_parses():
    html = _row("<span class='act-score-line'>0</span>-<span class='act-score-line'>1</span>")
    (row,) = vitibet.parse_html(html, "2026-10-18")
    assert (row["hs"], row["gs"]) == (0, 1)
    assert (row["home"], row["away"]) == ("CRB", "Botafogo-SP")


def test_single_element_pair_parses():
    html = _row("<span class='act-score-line'>2-1</span>")
    (row,) = vitibet.parse_html(html, "2026-10-18")
    assert (row["hs"], row["gs"]) == (2, 1)


def test_single_element_pair_accepts_spaces_and_colon():
    html = _row("<span class='act-score-line'> 3 : 0 </span>")
    (row,) = vitibet.parse_html(html, "2026-10-18")
    assert (row["hs"], row["gs"]) == (3, 0)


def test_upcoming_row_has_no_score():
    html = _row("")
    (row,) = vitibet.parse_html(html, "2026-10-19")
    assert row["hs"] is None and row["gs"] is None


def test_probabilities_parse_as_index_then_1x2():
    html = _row("<span class='act-score-line'>0-0</span>")
    (row,) = vitibet.parse_html(html, "2026-10-18")
    assert (row["index"], row["p1"], row["px"], row["p2"]) == (0.54, 42.0, 28.0, 30.0)

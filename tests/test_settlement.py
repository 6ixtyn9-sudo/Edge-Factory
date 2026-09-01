from edgefactory.settlement import ABANDONED, CANCELLED, POSTPONED, terminal_event_disposition


def test_terminal_event_disposition_is_positive_evidence_only():
    assert terminal_event_disposition("Postp.") == POSTPONED
    assert terminal_event_disposition("Postponed") == POSTPONED
    assert terminal_event_disposition("Cancelled") == CANCELLED
    assert terminal_event_disposition("Abandoned") == ABANDONED
    assert terminal_event_disposition("scheduled") is None
    assert terminal_event_disposition("live") is None
    assert terminal_event_disposition("") is None


def test_load_verified_results_parses_and_fails_closed(tmp_path):
    import json

    from edgefactory.settlement import load_verified_results

    p = tmp_path / "verified_results.json"
    p.write_text(json.dumps({"rows": [
        {"date": "2026-08-27", "home": "Pafos", "away": "Dinamo Tirana",
         "hs": 4, "gs": 2, "outcome": "home", "src": "operator_verified"},
        # bad outcome -> dropped
        {"date": "2026-08-27", "home": "Bad", "away": "Row",
         "hs": 1, "gs": 0, "outcome": "sideways"},
        # missing score -> dropped
        {"date": "2026-08-27", "home": "No", "away": "Score",
         "hs": None, "gs": 0, "outcome": "home"},
    ]}))
    rows = load_verified_results(p)
    assert rows == [{"date": "2026-08-27", "home": "Pafos", "away": "Dinamo Tirana",
                     "hs": 4, "gs": 2, "outcome": "home", "src": "operator_verified"}]


def test_load_verified_results_missing_file_is_empty(tmp_path):
    from edgefactory.settlement import load_verified_results

    assert load_verified_results(tmp_path / "nope.json") == []

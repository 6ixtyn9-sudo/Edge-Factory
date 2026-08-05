from edgefactory.settlement import ABANDONED, CANCELLED, POSTPONED, terminal_event_disposition


def test_terminal_event_disposition_is_positive_evidence_only():
    assert terminal_event_disposition("Postp.") == POSTPONED
    assert terminal_event_disposition("Postponed") == POSTPONED
    assert terminal_event_disposition("Cancelled") == CANCELLED
    assert terminal_event_disposition("Abandoned") == ABANDONED
    assert terminal_event_disposition("scheduled") is None
    assert terminal_event_disposition("live") is None
    assert terminal_event_disposition("") is None

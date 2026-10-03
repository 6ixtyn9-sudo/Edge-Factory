"""Execution must fail closed on unregistered or disabled price provenance."""
from __future__ import annotations

import scripts.auto_tickets as at
from edgefactory import price_sources as psrc


def _row(source: str, **extra):
    row = {
        "date": "2026-10-03", "home": "Alpha", "away": "Beta",
        "market": "1x2", "pick": "home", "avg_p": 70.0,
        "odds": 1.80, "bucket": "CAUTION", "quarantine": "none",
        "price_push_eligible": True, "odds_source": source,
    }
    row.update(extra)
    return row


def test_unknown_source_cannot_become_a_printable_leg():
    row = _row("not-a-registered-donor")
    assert psrc.spec(row["odds_source"]).can_execute() is False
    assert at.playable_legs([row], day="2026-10-03", execution_safe=True) == []


def test_source_fallback_is_registered_but_abstains_by_default(monkeypatch):
    monkeypatch.delenv("EDGE_FACTORY_ALLOW_SOURCE_FALLBACK", raising=False)
    assert psrc.known("forebet_best")
    assert psrc.spec("forebet_best").can_execute() is False
    row = _row("forebet_best", price_evidence="SOURCE_FALLBACK")
    assert at.playable_legs([row], day="2026-10-03", execution_safe=True) == []


def test_source_fallback_requires_explicit_operator_switch(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_ALLOW_SOURCE_FALLBACK", "1")
    assert psrc.spec("forebet_best").can_execute() is True
    row = _row("forebet_best", price_evidence="SOURCE_FALLBACK")
    assert len(at.playable_legs([row], day="2026-10-03", execution_safe=True)) == 1

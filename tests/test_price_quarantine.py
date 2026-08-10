"""Addendum 26: price-evidence quarantine at enrichment and bucketing boundaries."""
from __future__ import annotations

import scripts.picks_today as pt


ALLOW_CTX = {
    "league": "ALLOW",
    "team_h": "ALLOW",
    "team_a": "ALLOW",
    "odds_band": "ALLOW",
    "competition_type": "ALLOW",
    "niche": "ALLOW",
    "league_key": "test league",
}
VETO_CTX = {**ALLOW_CTX, "league": "VETO"}


def _pick(**extra):
    out = {
        "date": "2026-08-05",
        "home": "Alpha United",
        "away": "Beta City",
        "match": "Alpha United vs Beta City",
        "market": "1x2",
        "pick": "home",
        "avg_p": 78.0,
        "odds": 1.70,
        "odds_source": "forebet_best",
        "bookmaker": None,
        "kickoff": "18:00",
    }
    out.update(extra)
    return out


def _row(**extra):
    out = {
        "odds": 2.10,
        "bookmaker": "AuditBook",
        "captured_at": "2026-08-05T10:00:00Z",
        "league": "Test League",
    }
    out.update(extra)
    return out


def test_primary_bzzoiro_price_remains_push_eligible(monkeypatch):
    pick = _pick()
    primary = {"provider": pt.BZZOIRO_ODDS_SOURCE}
    monkeypatch.setattr(pt, "find_odds_row", lambda *_: (_row(), "exact"))

    assert pt.enrich_with_live_odds([pick], primary) == 1
    assert pick["odds"] == 2.10
    assert pick["price_evidence"] == pt.PRICE_EVIDENCE_BZZOIRO_PRIMARY
    assert pick["price_push_eligible"] is True
    assert pt.bucket_pick(pick, ALLOW_CTX, decay_verdict="HEALTHY") == pt.BUCKET_CERTIFIED
def test_scoutingstats_sole_price_is_retained_for_audit_but_quarantined(monkeypatch):
    pick = _pick(odds=None, odds_source=None)
    primary = {"provider": pt.BZZOIRO_ODDS_SOURCE}
    secondary = {"provider": pt.SCOUTINGSTATS_ODDS_SOURCE}

    def find(_pick_, bundle):
        return (None, None) if bundle is primary else (_row(odds=1.91), "exact")

    monkeypatch.setattr(pt, "find_odds_row", find)
    assert pt.enrich_with_live_odds([pick], primary, secondary) == 1
    assert pick["odds"] == 1.91  # preserved for audit/settlement accounting
    assert pick["odds_source"] == pt.SCOUTINGSTATS_ODDS_SOURCE
    assert pick["price_evidence"] == pt.PRICE_EVIDENCE_SCOUTINGSTATS_SOLE
    assert pick["price_push_eligible"] is False
    assert pt.bucket_pick(pick, ALLOW_CTX) == pt.BUCKET_WL_UNCORROBORATED_PRICE
    assert pick["price_quarantine_reason"] == "scoutingstats_sole_source"


def test_alias_fuzzy_price_never_replaces_operational_odds(monkeypatch):
    pick = _pick(odds=1.70, odds_source="forebet_best")
    primary = {"provider": pt.BZZOIRO_ODDS_SOURCE}
    monkeypatch.setattr(pt, "find_odds_row", lambda *_: (_row(odds=2.88), "alias_fuzzy"))

    assert pt.enrich_with_live_odds([pick], primary) == 1
    assert pick["odds"] == 1.70
    assert pick["odds_source"] == "forebet_best"
    assert pick["odds_match_method"] == "alias_fuzzy"
    assert pick["price_evidence"] == pt.PRICE_EVIDENCE_SUSPECT_ALIAS_FUZZY
    assert pick["price_push_eligible"] is False
    assert pick["suspect_price"]["odds"] == 2.88
    assert pick["suspect_price"]["source"] == pt.BZZOIRO_ODDS_SOURCE
    assert pt.bucket_pick(pick, ALLOW_CTX) == pt.BUCKET_WL_SUSPECT_PRICE


def test_alias_fuzzy_without_prior_price_stays_auditable_but_unpriced(monkeypatch):
    pick = _pick(odds=None, odds_source=None)
    primary = {"provider": pt.BZZOIRO_ODDS_SOURCE}
    monkeypatch.setattr(pt, "find_odds_row", lambda *_: (_row(odds=3.05), "alias_fuzzy"))

    pt.enrich_with_live_odds([pick], primary)
    assert pick["odds"] is None
    assert pick["suspect_price"]["odds"] == 3.05
    assert pt.bucket_pick(pick, ALLOW_CTX) == pt.BUCKET_WL_SUSPECT_PRICE


def test_context_veto_still_overrides_price_quarantine(monkeypatch):
    pick = _pick()
    primary = {"provider": pt.BZZOIRO_ODDS_SOURCE}
    monkeypatch.setattr(pt, "find_odds_row", lambda *_: (_row(), "alias_fuzzy"))

    pt.enrich_with_live_odds([pick], primary)
    assert pt.bucket_pick(pick, VETO_CTX) == pt.BUCKET_SKIP_VETO
    assert "context VETO" in pick["veto_reason"]


def test_no_live_match_keeps_legacy_source_fallback_behavior(monkeypatch):
    pick = _pick(odds=1.63, odds_source="zulubet")
    primary = {"provider": pt.BZZOIRO_ODDS_SOURCE}
    monkeypatch.setattr(pt, "find_odds_row", lambda *_: (None, None))

    assert pt.enrich_with_live_odds([pick], primary) == 0
    assert pick["odds"] == 1.63
    assert pick["odds_match_method"] == "fallback"
    assert pick["price_evidence"] == pt.PRICE_EVIDENCE_SOURCE_FALLBACK
    assert pt.bucket_pick(pick, ALLOW_CTX, decay_verdict="HEALTHY") == pt.BUCKET_CERTIFIED

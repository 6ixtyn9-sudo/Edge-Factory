"""Health-aware price-source selection (2026-10-03).

The pipeline used to treat ``bzzoiro_odds`` as the primary source because it
was the first bundle in the argument list. These tests pin the corrected
behaviour: sources are ranked by health and exact fixture match, every quote
stays on the price board, and nothing that is not a named bookmaker is ever
labelled as one.
"""
from __future__ import annotations

import pytest

import scripts.picks_today as pt
from edgefactory import price_sources as psrc


@pytest.fixture(autouse=True)
def _donors_enabled(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR", "1")
    monkeypatch.setenv("EDGE_FACTORY_ENABLE_FAIR_PRICE_DONOR", "1")
    monkeypatch.delenv("EDGE_FACTORY_FAIR_PRICE_STAKEABLE", raising=False)
    monkeypatch.delenv("EDGE_FACTORY_REQUIRE_PRICE_CORROBORATION", raising=False)
    monkeypatch.delenv("EDGE_FACTORY_REQUIRE_NAMED_BOOK_CORROBORATION", raising=False)
    yield


DAY = "2026-10-03"


def _pick(**extra):
    out = {"date": DAY, "home": "Alpha United", "away": "Beta City",
           "market": "1x2", "pick": "away"}
    out.update(extra)
    return out


def _row(source, odds, **extra):
    out = {"source": source, "provider": source, "date": DAY,
           "home": "Alpha United", "away": "Beta City", "market": "1x2",
           "selection": "away", "odds": odds, "kickoff": f"{DAY}T18:00:00+00:00",
           "captured_at": f"{DAY}T09:00:00+00:00"}
    out.update(extra)
    return out


def _bundle(source, rows):
    return pt._odds_bundle_from_rows(
        [psrc.annotate_row(dict(r), source=source) for r in rows], provider=source)


def _empty(source):
    return pt._odds_bundle_from_rows([], provider=source)


# --- registry contracts ---------------------------------------------------

def test_priority_is_registry_driven_not_bzzoiro_hard_coded():
    donors = psrc.price_donor_names()
    assert "bzzoiro_odds" in donors
    # Several approved sources outrank or match it; none of them is special-cased.
    assert set(donors) >= {"sharpapi_odds", "pinnapi_odds", "boggio", "betbetter"}


def test_boggio_and_betbetter_are_not_named_bookmakers():
    assert psrc.spec("boggio").named_bookmaker is False
    assert psrc.spec("betbetter").named_bookmaker is False
    assert psrc.spec("boggio").independence_family == "boggio_average"
    assert psrc.spec("betbetter").independence_family == "betbetter_fair"
    assert psrc.spec("bzzoiro_odds").named_bookmaker is True


def test_theoddsapi_families_are_per_book():
    a = psrc.independence_family("theoddsapi", "Bet365")
    b = psrc.independence_family("theoddsapi", "Pinnacle")
    assert a != b
    # One aggregator must never corroborate itself through the same book.
    assert psrc.independence_family("theoddsapi", "Bet365") == a


def test_unregistered_source_is_never_a_price_donor():
    unknown = psrc.spec("mystery_feed")
    assert unknown.can_execute() is False
    assert unknown.can_corroborate() is False


# --- selection ------------------------------------------------------------

def test_sharpapi_is_selected_when_bzzoiro_is_unavailable():
    pick = _pick()
    bundles = [_empty("bzzoiro_odds"), _bundle("sharpapi_odds", [_row("sharpapi_odds", 2.10, bookmaker="Pinnacle")])]
    row, method, source = pt.select_price_source(pick, bundles)
    assert source == "sharpapi_odds"
    assert (row["odds"], method) == (2.10, "exact")


def test_boggio_is_selected_when_no_named_book_is_available():
    pick = _pick()
    bundles = [_empty("bzzoiro_odds"),
               _bundle("boggio", [_row("boggio", 2.05, bookmaker="average_bookie_aggregate",
                                       odds_kind="provider_average")])]
    row, _method, source = pt.select_price_source(pick, bundles)
    assert source == "boggio"
    assert row["odds"] == 2.05


def test_boggio_is_not_selected_when_the_operator_disables_the_donor(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR", "0")
    pick = _pick()
    bundles = [_empty("bzzoiro_odds"), _bundle("boggio", [_row("boggio", 2.05)])]
    _row_, _m, source = pt.select_price_source(pick, bundles)
    assert source != "boggio"


def test_betbetter_can_supply_a_fair_price():
    pick = _pick()
    bundles = [_empty("bzzoiro_odds"),
               _bundle("betbetter", [_row("betbetter", 2.40, bookmaker=None, odds_kind="fair")])]
    row, _m, source = pt.select_price_source(pick, bundles)
    assert source == "betbetter"
    assert row["odds_kind"] == "fair"


def test_a_healthy_named_book_outranks_a_fair_price_donor():
    pick = _pick()
    bundles = [
        _bundle("betbetter", [_row("betbetter", 2.40, bookmaker=None, odds_kind="fair")]),
        _bundle("bzzoiro_odds", [_row("bzzoiro_odds", 2.15, bookmaker="Bet365")]),
    ]
    _r, _m, source = pt.select_price_source(pick, bundles)
    assert source == "bzzoiro_odds"


def test_named_book_provenance_beats_a_fresher_stakeable_fair_price(monkeypatch):
    # Even when an operator deliberately enables fair-price staking, a healthy
    # exact named-book quote is preferred. This pins the ordering rather than
    # relying on microsecond differences in per-row clock sampling.
    monkeypatch.setenv("EDGE_FACTORY_FAIR_PRICE_STAKEABLE", "1")
    candidates = [
        psrc.SourceCandidate(name="betbetter", healthy=True, exact_match=True, freshness_h=0.0),
        psrc.SourceCandidate(name="bzzoiro_odds", healthy=True, exact_match=True, freshness_h=8.0),
    ]
    assert psrc.rank_candidates(candidates, execution_only=True)[0].name == "bzzoiro_odds"


def test_unavailable_bzzoiro_never_wins_on_historic_priority():
    candidates = [
        psrc.SourceCandidate(name="bzzoiro_odds", healthy=False, exact_match=False),
        psrc.SourceCandidate(name="boggio", healthy=True, exact_match=True),
    ]
    assert psrc.select_execution_source(candidates).name == "boggio"


# --- enrichment: board, labels, eligibility ------------------------------

def test_every_quote_stays_on_the_price_board():
    pick = _pick()
    bundles = [
        _bundle("bzzoiro_odds", [_row("bzzoiro_odds", 2.15, bookmaker="Bet365")]),
        _bundle("boggio", [_row("boggio", 2.05, bookmaker="average_bookie_aggregate",
                                odds_kind="provider_average")]),
        _bundle("betbetter", [_row("betbetter", 2.40, bookmaker=None, odds_kind="fair")]),
    ]
    assert pt.enrich_with_live_odds(pick and [pick], bundles[0], None,
                                    donor_bundles=bundles[1:]) == 1
    sources = {e["source"] for e in pick["price_board"]}
    assert sources == {"bzzoiro_odds", "boggio", "betbetter"}
    kinds = {e["source"]: e["odds_kind"] for e in pick["price_board"]}
    assert kinds["boggio"] == "provider_average"
    assert kinds["betbetter"] == "fair"
    assert kinds["bzzoiro_odds"] == "bookmaker"


def test_a_donor_price_is_disclosed_and_not_called_a_book_price():
    pick = _pick()
    donor = _bundle("betbetter", [_row("betbetter", 2.40, bookmaker=None, odds_kind="fair")])
    assert pt.enrich_with_live_odds([pick], _empty("bzzoiro_odds"), None,
                                    donor_bundles=[donor]) == 1
    assert pick["odds"] == 2.40
    assert pick["odds_source"] == "betbetter"
    assert pick["price_evidence"] == pt.PRICE_EVIDENCE_DONOR_PRICE
    assert pick["price_odds_kind"] == "fair"
    assert pick["price_donor_role"] == "model_fair_price_donor"
    assert "not a named-book execution quote" in pick["price_disclosure"]
    assert pick["bookmaker"] is None


def test_boggio_price_is_eligible_only_while_the_donor_is_enabled(monkeypatch):
    donor_row = _row("boggio", 2.05, bookmaker="average_bookie_aggregate",
                     odds_kind="provider_average", price_push_eligible=True)
    pick = _pick()
    assert pt.enrich_with_live_odds([pick], _empty("bzzoiro_odds"), None,
                                    donor_bundles=[_bundle("boggio", [donor_row])]) == 1
    assert pick["price_push_eligible"] is True
    assert pick["price_independence_family"] == "boggio_average"

    monkeypatch.setenv("EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR", "0")
    pick2 = _pick()
    pt.enrich_with_live_odds([pick2], _empty("bzzoiro_odds"), None,
                             donor_bundles=[_bundle("boggio", [donor_row])])
    assert pick2.get("price_push_eligible") is not True


def test_a_timestamp_suspect_donor_row_cannot_push_a_price():
    suspect = _row("boggio", 2.05, bookmaker="average_bookie_aggregate",
                   odds_kind="provider_average", price_push_eligible=False,
                   timestamp_suspect=True)
    pick = _pick()
    pt.enrich_with_live_odds([pick], _empty("bzzoiro_odds"), None,
                             donor_bundles=[_bundle("boggio", [suspect])])
    assert pick["price_push_eligible"] is False


def test_scoutingstats_remains_quarantined_from_execution():
    pick = _pick()
    secondary = _bundle("scoutingstats_odds", [_row("scoutingstats_odds", 2.00)])
    assert pt.enrich_with_live_odds([pick], _empty("bzzoiro_odds"), secondary) == 1
    assert pick["price_push_eligible"] is False
    assert pick["price_quarantine_reason"] == "scoutingstats_sole_source"


def test_no_approved_quote_leaves_the_pick_unpriced():
    pick = _pick()
    assert pt.enrich_with_live_odds([pick], _empty("bzzoiro_odds"), None,
                                    donor_bundles=[_empty("boggio")]) == 0
    assert pick.get("odds") is None
    assert pick["price_evidence"] == pt.PRICE_EVIDENCE_UNMATCHED
    assert pick["price_push_eligible"] is False


# --- corroboration --------------------------------------------------------

def test_corroboration_counts_independent_families_not_vendors():
    pick = _pick()
    bundles = [
        _bundle("bzzoiro_odds", [_row("bzzoiro_odds", 2.15, bookmaker="Bet365")]),
        _bundle("boggio", [_row("boggio", 2.14, bookmaker="average_bookie_aggregate",
                                odds_kind="provider_average")]),
    ]
    pt.enrich_with_live_odds([pick], bundles[0], None, donor_bundles=bundles[1:])
    pt._stamp_price_corroboration([pick])
    assert pick["price_corroborated"] is True
    assert pick["price_corroborating_families"] == ["boggio_average"]
    # An average aggregate is NOT named-book corroboration.
    assert pick["price_named_book_corroborated"] is False


def test_named_book_corroboration_can_be_required(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_REQUIRE_PRICE_CORROBORATION", "1")
    monkeypatch.setenv("EDGE_FACTORY_REQUIRE_NAMED_BOOK_CORROBORATION", "1")
    pick = _pick()
    bundles = [
        _bundle("bzzoiro_odds", [_row("bzzoiro_odds", 2.15, bookmaker="Bet365")]),
        _bundle("boggio", [_row("boggio", 2.14, bookmaker="average_bookie_aggregate",
                                odds_kind="provider_average")]),
    ]
    pt.enrich_with_live_odds([pick], bundles[0], None, donor_bundles=bundles[1:])
    pt._stamp_price_corroboration([pick])
    assert pick["price_corroboration_sufficient"] is False


def test_policy_is_explicit_and_printable():
    line = psrc.policy_line()
    assert "avg_donor=on" in line and "fair_donor=on" in line
    assert "corroboration=preferred" in line


def test_candidate_pass_skips_provider_shadow_capture(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_CANDIDATE_ONLY", "1")
    stats = pt._capture_shadow_candidates(DAY)
    assert stats["pinnapi_odds"]["status"] == "candidate_only"
    assert stats["sharpapi_odds"]["status"] == "candidate_only"
    assert stats["boggio"]["status"] == "candidate_only"


def test_observed_execution_contributor_order_beats_cross_source_freshness():
    # Archived end-to-end contribution through 2026-10-03: BetExplorer had
    # 497 push-eligible matches over 84 source-days; Bzzoiro had 85 over 53.
    # This is an availability ordering, not a claim about settled performance.
    candidates = [
        psrc.SourceCandidate(name="bzzoiro_odds", healthy=True, exact_match=True, freshness_h=0.0),
        psrc.SourceCandidate(name="betexplorer_odds", healthy=True, exact_match=True, freshness_h=12.0),
    ]
    assert psrc.rank_candidates(candidates, execution_only=True)[0].name == "betexplorer_odds"

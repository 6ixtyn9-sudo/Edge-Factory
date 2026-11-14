"""Hermetic reader-transcription tests; deliberately NOT native/live coverage."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from edgefactory.sources.betolimp_snapshot import (
    MAX_BYTES,
    compare_card_identity,
    parse_saved_excerpt,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/betolimp_reader_2026-11-01.json"


@pytest.fixture
def saved():
    return json.loads(FIXTURE.read_text())


@pytest.fixture
def probe():
    spec = importlib.util.spec_from_file_location("probe_betolimp_test", ROOT / "scripts/probe_betolimp.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_observed_event_canonicalization_and_provenance(saved):
    r = parse_saved_excerpt(saved[0])
    assert r["home"] == "Liverpool" and r["away"] == "Arsenal"
    assert r["event_id"] == "86096893" and r["coupon_id"] == "135"
    assert [(x["market"], x["selection"], x["display_price"]) for x in r["observations"]] == [
        ("1x2", "home", "2.79"), ("1x2", "draw", "3.48"), ("1x2", "away", "2.57"),
        ("ou_2.5", "under", "1.93"), ("ou_2.5", "over", "1.90"),
        ("btts", "yes", "1.71"), ("btts", "no", "2.15")]
    assert r["observations"][0]["raw_market"] == "Full Time Result"
    assert r["observations"][3]["line"] == "2.5"
    assert r["transcription_sha256"] == hashlib.sha256(saved[0]["text"].encode()).hexdigest()
    assert r["kickoff_utc"] is None and r["quoted_at"] is None
    assert r["status"] == "diagnostic_only" and r["admitted_rows"] == 0
    assert "odds_view_profile_unverified" in r["hold_reasons"]


@pytest.mark.parametrize("index,prices,event,coupon", [
    (1, ["1.59", "4.57", "4.40", "1.57", "2.25"], "86214530", "4779"),
    (2, ["1.43", "4.91", "5.78", "1.68", "2.08"], "86213002", "4376"),
])
def test_real_lower_tier_and_womens_rows_do_not_invent_ordered_teams(saved, index, prices, event, coupon):
    r = parse_saved_excerpt(saved[index])
    assert [x["display_price"] for x in r["observations"]] == prices
    assert r["event_id"] == event and r["coupon_id"] == coupon
    assert r["home"] is None and r["away"] is None
    assert r["identity_evidence"] == "concatenated_label_not_split_into_teams"
    assert r["observations"][-1]["market"] == "ou_3.5"
    assert r["admitted_rows"] == 0


@pytest.mark.parametrize("price", ["NaN", "Infinity", "-2.0", "0.99", "1.00", "1e3", "2,79", "2.7900", "99999.00"])
def test_bad_display_price_fails_closed(saved, price):
    saved[0]["text"] = saved[0]["text"].replace("Liverpool2.79Draw", f"Liverpool{price}Draw")
    with pytest.raises(ValueError):
        parse_saved_excerpt(saved[0])


@pytest.mark.parametrize("url", [
    "http://betolimp.co.za/sports/soccer-betting/a/b-1",
    "https://user:pass@betolimp.co.za/sports/soccer-betting/a/b-1",
    "https://betolimp.co.za:443/sports/soccer-betting/a/b-1",
    "https://betolimp.co.za.evil.test/sports/soccer-betting/a/b-1",
    "https://127.0.0.1/sports/soccer-betting/a/b-1",
    "https://betolimp.co.za/sports/soccer-betting/a/b-1?token=SECRET",
    "https://betolimp.co.za/sports/soccer-betting/a/b-1#fragment",
    "https://betolimp.co.za/sports/soccer-betting/a/%2e%2e/b-1",
    "https://betolimp.co.za/cdn-cgi/b-1",
    "https://betolimp.co.za/sports/soccer-betting/a/../b-1",
    "https://betolimp.co.za/sports/soccer-betting/a/b-1\n",
])
def test_exact_url_provenance_no_arbitrary_origin_or_query(saved, url):
    saved[0]["source_url"] = url
    with pytest.raises(ValueError):
        parse_saved_excerpt(saved[0])


@pytest.mark.parametrize("key,value", [
    ("evidence_kind", "native_html"), ("evidence_kind", "verified_quote"),
    ("profile", "cloudbet"), ("observed_on", "Today"), ("observed_on", "2026-02-30"),
    ("text", "x" * (MAX_BYTES + 1)), ("text", None),
])
def test_unsupported_envelopes_rejected(saved, key, value):
    saved[0][key] = value
    with pytest.raises(ValueError):
        parse_saved_excerpt(saved[0])


@pytest.mark.parametrize("old,new", [
    ("Liverpool - Arsenal", "Arsenal - Liverpool"),
    ("#135", "135"), ("18:30", "25:00"),
    ("Liverpool2.79Draw3.48Arsenal2.57", "Liverpool2.79Arsenal2.57"),
    ("Total (2.5) over1.90", "Total (3.5) over1.90"),
    ("Total (2.5)", "Total (0)"),
    ("Both teams to score: yes1.71Both teams to score: no2.15", "Liverpool to score: yes1.71Liverpool to score: no2.15"),
])
def test_ambiguous_header_or_incomplete_market_rejected(saved, old, new):
    saved[0]["text"] = saved[0]["text"].replace(old, new)
    with pytest.raises(ValueError):
        parse_saved_excerpt(saved[0])


def test_no_promo_half_or_team_total_mapping_and_duplicates_rejected(saved):
    original = parse_saved_excerpt(saved[0])
    assert len(original["observations"]) == 7  # unsupported sections in fixture do not leak
    saved[0]["text"] += "\nFull Time Result\nLiverpool20.00Draw30.00Arsenal40.00\n"
    with pytest.raises(ValueError, match="duplicate"):
        parse_saved_excerpt(saved[0])


def test_no_promo_prefix_or_native_html_accepted(saved):
    for prefix in ("Recent Big Winners\n", "<html><body>", "Liverpool - Arsenal\n#1\n"):
        envelope = {**saved[0], "text": prefix + saved[0]["text"]}
        with pytest.raises(ValueError):
            parse_saved_excerpt(envelope)


@pytest.mark.parametrize("index", [1, 2])
def test_league_column_shift_wrong_link_or_duplicate_rows_rejected(saved, index):
    envelope = saved[index]
    for text in (
        envelope["text"].replace("Handicap 1", "Handicap"),
        envelope["text"].replace("\n\nX\n\n", "\n\n"),
        envelope["text"] + envelope["text"],
        "Shared carousel\n" + envelope["text"],
        envelope["text"].replace("\n\n3.5\n\n", "\n\n0\n\n"),
        envelope["text"].replace(envelope["source_url"] + "/", envelope["source_url"] + "-other/"),
    ):
        with pytest.raises(ValueError):
            parse_saved_excerpt({**envelope, "text": text})


def test_input_is_not_mutated_and_claimed_freshness_not_trusted(saved):
    before = copy.deepcopy(saved)
    saved[0].update(kickoff_utc="2026-11-01T16:30:00Z", quoted_at="2026-11-01T15:00:00Z",
                    permission=True, admitted_rows=7)
    r = parse_saved_excerpt(saved[0])
    assert r["admitted_rows"] == 0 and r["kickoff_utc"] is None and r["quoted_at"] is None
    assert saved[0]["text"] == before[0]["text"]
    raw = copy.deepcopy(saved[1])
    parse_saved_excerpt(saved[1])
    assert saved[1] == raw


@pytest.mark.parametrize("home,away", [
    ("Arsenal", "Liverpool"), ("Liverpool (W)", "Arsenal (W)"),
    ("Liverpool U21", "Arsenal U21"), ("Liverpool Reserves", "Arsenal Reserves"),
    ("Liverpool B", "Arsenal B"), ("", "Arsenal"),
])
def test_existing_identity_guards_reject_reversal_and_squad_mismatch(saved, home, away):
    r = compare_card_identity({"home": home, "away": away}, parse_saved_excerpt(saved[0]))
    assert not r["ordered_teams_match"] and not r["admitted"]


def test_identity_diagnostic_does_not_fill_missing_date_zone_or_league(saved):
    r = compare_card_identity({"home": "Liverpool", "away": "Arsenal", "league": "Premier League",
                               "date": "2026-11-01", "kickoff_utc": "2026-11-01T16:30:00Z"},
                              parse_saved_excerpt(saved[0]))
    assert r == {"ordered_teams_match": True, "league_match": False,
                 "absolute_kickoff_match": False, "admitted": False}


def test_read_only_cli_reuses_card_helpers_without_network(saved, probe, tmp_path, monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("network attempted")
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setattr(socket, "socket", deny)
    card = tmp_path / "card.json"
    card.write_text(json.dumps({"picks": [{"home": "Liverpool", "away": "Arsenal"}]}))
    before = {p: p.read_bytes() for p in (card, FIXTURE)}
    result = probe.dry_run(FIXTURE, card)
    assert result["snapshot_count"] == 3 and result["displayed_observation_count"] == 17
    assert result["admitted_rows"] == result["writes"] == result["network_requests"] == 0
    assert result["card_rows_examined"] == 1
    assert result["snapshots"][0]["card_comparison"] == {
        "ordered_team_candidate_rows": 1, "complete_identity_matches": 0}
    assert all(p.read_bytes() == content for p, content in before.items())
    assert list(tmp_path.iterdir()) == [card]


@pytest.mark.parametrize("payload", [None, {}, [], [None], [{"evidence_kind": "native_html"}], [0] * 11])
def test_bad_input_cli_no_partial_success_or_content_echo(payload, probe, tmp_path, capsys):
    path = tmp_path / "input.json"
    path.write_text(json.dumps(payload))
    assert probe.main(["--input", str(path)]) == 2
    out = capsys.readouterr()
    assert out.out == ""
    assert json.loads(out.err) == {"status": "invalid_offline_input", "admitted_rows": 0}


def test_unknown_live_flag_is_not_available():
    result = subprocess.run([sys.executable, str(ROOT / "scripts/probe_betolimp.py"), "--live"],
                            check=False, capture_output=True, text=True)
    assert result.returncode == 2


def test_cli_malformed_or_oversized_card_never_mutates_it(probe, tmp_path):
    card = tmp_path / "card.json"
    for body in ('{"picks": [42]}', '{"wrong": []}', '"secret"', ' ' * (16 * 1024 * 1024 + 1)):
        card.write_text(body)
        with pytest.raises(ValueError):
            probe.dry_run(FIXTURE, card)
        assert card.read_text() == body


def test_feature_absent_from_production_imports():
    for path in (ROOT / "scripts/daily.py", ROOT / "scripts/picks_today.py",
                 ROOT / "src/edgefactory/enh_pricing.py"):
        assert "betolimp_snapshot" not in path.read_text()


@pytest.fixture
def event_followup():
    return json.loads((ROOT / "tests/fixtures/betolimp_event_reader_followup_2026-11-01.json").read_text())


@pytest.mark.parametrize("index,home,away,league,btts", [
    (0, "Southall", "Ashford Town", "England. Isthmian. 1st division. South-Central", ["1.54", "2.24"]),
    (1, "TS Galaxy (W)", "Stellenbosch (W)", "South Africa. Super League. Women", ["1.53", "2.26"]),
])
def test_direct_event_header_resolves_teams_without_league_label_guess(
        event_followup, index, home, away, league, btts):
    r = parse_saved_excerpt(event_followup[index])
    assert (r["home"], r["away"], r["league"]) == (home, away, league)
    assert r["league_evidence"] == "reader_breadcrumb"
    assert len(r["observations"]) == 7
    assert [x["display_price"] for x in r["observations"] if x["market"] == "btts"] == btts
    assert {x["market"] for x in r["observations"]} == {"1x2", "btts", "ou_3.5"}
    assert r["quoted_at"] is None and r["kickoff_utc"] is None and r["admitted_rows"] == 0
    card = {"home": home, "away": away, "league": league,
            "kickoff_utc": "2026-11-01T15:00:00Z"}
    assert compare_card_identity(card, r) == {
        "ordered_teams_match": True, "league_match": True,
        "absolute_kickoff_match": False, "admitted": False}


@pytest.mark.parametrize("edit", [
    lambda text: text.replace('"England. Isthmian. 1st division. South-Central"', '"Premier League"'),
    lambda text: text.replace('https://betolimp.co.za/sports/soccer-betting/england-isthmian-1st-division-south-central "', 'https://betolimp.co.za/sports/soccer-betting/england-premier-league "'),
    lambda text: text.replace('[England](https://betolimp.co.za/', '[England](https://other.test/'),
    lambda text: text.replace('"England")', '"England") [Extra](https://other.test/)'),
    lambda text: text.replace('"England")', '"England") injected'),
    lambda text: text.replace('[Soccer]', '[Soccer Extra]'),
])
def test_breadcrumb_requires_exact_layout_and_event_competition_path(event_followup, edit):
    with pytest.raises(ValueError):
        parse_saved_excerpt({**event_followup[0], "text": edit(event_followup[0]["text"])})


def test_alternative_total_cannot_replace_main_total(event_followup):
    r = parse_saved_excerpt(event_followup[0])
    assert [(q["selection"], q["display_price"]) for q in r["observations"]
            if q["market"] == "ou_3.5"] == [("under", "1.57"), ("over", "2.25")]
    assert not any(q["market"] == "ou_2.5" for q in r["observations"])


def test_direct_womens_event_still_rejects_mens_card(event_followup):
    r = parse_saved_excerpt(event_followup[1])
    result = compare_card_identity({"home": "TS Galaxy", "away": "Stellenbosch",
                                    "league": r["league"]}, r)
    assert not result["ordered_teams_match"] and not result["admitted"]


def test_missing_breadcrumb_does_not_fall_back_to_url_slug(event_followup):
    e = event_followup[0]
    result = parse_saved_excerpt({**e, "text": e["text"].split("\n\n", 1)[1],
                                 "league": "England. Isthmian. 1st division. South-Central"})
    assert result["league"] is None and result["league_evidence"] == "unverified"


def test_followup_cli_offline_two_events_14_observations(probe, tmp_path, monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("unexpected network")
    monkeypatch.setattr(socket, "socket", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    fixture = ROOT / "tests/fixtures/betolimp_event_reader_followup_2026-11-01.json"
    card = tmp_path / "card.json"
    card.write_text(json.dumps([{"home": "Southall", "away": "Ashford Town",
                                 "league": "England. Isthmian. 1st division. South-Central"}]))
    before = card.read_bytes()
    r = probe.dry_run(fixture, card)
    assert r["snapshot_count"] == 2 and r["displayed_observation_count"] == 14
    assert r["admitted_rows"] == r["network_requests"] == r["writes"] == 0
    assert r["snapshots"][0]["card_comparison"] == {
        "ordered_team_candidate_rows": 1, "complete_identity_matches": 0}
    assert card.read_bytes() == before

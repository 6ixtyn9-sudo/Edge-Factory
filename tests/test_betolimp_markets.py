"""Observed reader vocabulary; native HTML below is SYNTHETIC, not origin evidence."""

import html
import json
from copy import deepcopy
from pathlib import Path

import pytest
import test_betolimp_native_probe as native_contracts

from edgefactory.sources.betolimp_snapshot import (
    HOLDS,
    inspect_native_event_html,
    parse_saved_excerpt,
)

# Reuse the existing network-denying fixtures rather than making a new transport.
probe = native_contracts.probe
transport = native_contracts.transport
response = native_contracts.response

FIXTURE = Path(__file__).parent / "fixtures/betolimp_event_reader_2026-11-02.json"
URL = "https://betolimp.co.za/sports/soccer-betting/portugal-primeira-liga/benfica-alverca-86168564"


@pytest.fixture
def saved():
    return json.loads(FIXTURE.read_text())[0]


def synthetic_html(envelope):
    """Test-only rendering of labelled text; NEVER claim this was fetched HTML."""
    lines = [line.strip() for line in envelope["text"].splitlines() if line.strip()][1:]
    return (f'<html><head><link rel="canonical" href="{envelope["source_url"]}"></head>'
            f'<body><h1>{html.escape(lines[0])}</h1>'
            + ''.join(f'<div>{html.escape(line)}</div>' for line in lines[1:])
            + '</body></html>').encode()


def quote_map(result):
    return {(q["market"], q["selection"]): q["display_price"] for q in result["observations"]}


def test_actual_reader_alternate_and_team_total_prices_remain_unadmitted(saved):
    before = deepcopy(saved)
    result = parse_saved_excerpt(saved)
    quotes = quote_map(result)
    assert len(quotes) == len(result["observations"]) == 28
    assert quotes["1x2", "home"] == "1.13"
    assert quotes["ou_2.5", "over"] == "1.35"
    assert quotes["ou_3.5", "over"] == "1.92"
    assert quotes["btts", "no"] == "1.71"
    assert quotes["dc", "1x"] == "1.01" and quotes["dc", "x2"] == "6.26"
    assert quotes["tt_home_2.5", "over"] == "1.56"
    assert quotes["tt_away_0.5", "over"] == "1.99"
    assert result["league"] == "Portugal. Primeira Liga"
    assert result["event_id"] == "86168564" and result["coupon_id"] == "906"
    assert result["kickoff_display"] == "02 Nov 22:15"
    assert result["evidence_kind"] == "reader_transcription"
    assert result["admitted_rows"] == 0 and result["hold_reasons"] == list(HOLDS)
    assert result["kickoff_utc"] is result["quoted_at"] is None
    assert saved == before


def test_push_and_quarter_lines_are_not_sold_as_supported_binary_markets(saved):
    result = parse_saved_excerpt(saved)
    held = result["unsupported_observations"]
    assert len(held) == 18
    assert {q["reason"] for q in held} == {"non_half_line_settlement_not_supported"}
    assert not any(q["line"] in {"2", "3", "4", "5", "6"}
                   for q in result["observations"] if "line" in q)
    saved["text"] = saved["text"].replace("Total (2) under", "Total (2.25) under").replace(
        "Total (2) over", "Total (2.25) over")
    quarter = parse_saved_excerpt(saved)
    assert sum(q["line"] == "2.25" for q in quarter["unsupported_observations"]) == 2


def test_expanded_main_total_uses_its_own_line_not_the_legacy_two_line_limit(saved):
    saved["text"] = saved["text"].replace("Total (1.5) under7.11Total (1.5) over1.09", "")
    saved["text"] = saved["text"].replace("Total (3.5) under1.89Total (3.5) over1.92",
                                          "Total (1.5) under1.89Total (1.5) over1.92")
    assert quote_map(parse_saved_excerpt(saved))["ou_1.5", "over"] == "1.92"
    with pytest.raises(ValueError):
        parse_saved_excerpt(dict(saved, profile="betolimp_event_reader_v1"))


def test_integer_main_line_does_not_erase_other_supported_markets(saved):
    saved["text"] = saved["text"].replace("Total (3.5) under1.89Total (3.5) over1.92",
                                          "Total (3) under1.89Total (3) over1.92")
    result = parse_saved_excerpt(saved)
    assert len(result["observations"]) == 26
    assert len(result["unsupported_observations"]) == 20
    assert quote_map(result)["btts", "no"] == "1.71"


def test_old_reader_profile_retains_its_existing_seven_market_contract(saved):
    result = parse_saved_excerpt(dict(saved, profile="betolimp_event_reader_v1"))
    assert len(result["observations"]) == 7
    assert "unsupported_observations" not in result


@pytest.mark.parametrize("old,new", [
    ("No draw1.06", "No draw"),
    ("Draw or Alverca6.26", "Draw or Benfica6.26"),
    ("Total (2.5) over1.35", "Total (3.5) over1.35"),
    ("Total (2.5) under3.07", "Total (2.5) underNaN"),
    ("Total (2.5) over1.35", "Total (2.5) over1.00"),
    ("Benfica (2.5) over1.56", "Alverca (2.5) over1.56"),
    ("Alverca (0.5) under1.78", "Other Club (0.5) under1.78"),
    ("Benfica (1.5) under4.09", "PROMO Benfica (1.5) under4.09"),
    ("Total (1.5) under7.11", "prefix Total (1.5) under7.11"),
    ("Total (6) over7.30", "Total (6) over7.30 suffix"),
    ("Benfica (4) over3.73", "Benfica (4) over3.73 suffix"),
    ("Alverca (1.5) over5.56", "Alverca (1.5) over5.56 suffix"),
])
def test_partial_mixed_or_unbound_pairs_fail_closed(saved, old, new):
    saved["text"] = saved["text"].replace(old, new)
    with pytest.raises(ValueError):
        parse_saved_excerpt(saved)


@pytest.mark.parametrize("heading", ["Double Chance", "Alternative Total Goals", "Team Total"])
def test_duplicate_expanded_sections_never_cherry_pick(saved, heading):
    saved["text"] += "\n" + heading + "\nunused\n"
    with pytest.raises(ValueError, match="duplicate"):
        parse_saved_excerpt(saved)


def test_duplicate_lines_and_main_alternative_conflicts_fail_closed(saved):
    pair = "Total (2.5) under3.07Total (2.5) over1.35"
    for edited in (saved["text"].replace(pair, pair + pair),
                   saved["text"].replace(pair, pair + "Total (3.5) under1.89Total (3.5) over1.92")):
        with pytest.raises(ValueError, match="duplicate"):
            parse_saved_excerpt(dict(saved, text=edited))


def test_halves_and_handicaps_cannot_substitute_for_full_time_markets(saved):
    quotes = quote_map(parse_saved_excerpt(saved))
    saved["text"] = saved["text"].replace("W1 with handicap (-2.5)2.11", "W1 with handicap (-2.5)99.00")
    saved["text"] = saved["text"].replace("Total of 1st half (1.5) over1.83", "Total of 1st half (1.5) over90.00")
    assert quote_map(parse_saved_excerpt(saved)) == quotes


def test_reader_cannot_gain_native_provenance_or_absolute_clocks_from_input_claims(saved):
    result = parse_saved_excerpt(dict(saved, quoted_at="2026-11-02T05:30:00Z",
                                     kickoff_utc="2026-11-02T20:15:00Z", admitted_rows=28))
    assert result["quoted_at"] is result["kickoff_utc"] is None
    with pytest.raises(ValueError):
        parse_saved_excerpt(dict(saved, evidence_kind="native_http_response"))


def test_synthetic_native_layout_decodes_candidates_without_promoting_any_evidence(saved):
    result = inspect_native_event_html(synthetic_html(saved), URL)
    assert result["status"] == "native_event_market_candidates_unadmitted"
    assert quote_map(result) == quote_map(parse_saved_excerpt(saved))
    assert len(result["unsupported_observations"]) == 18
    assert result["admitted_rows"] == 0 and result["native_layout_verified"] is False
    assert result["quoted_at"] is result["kickoff_utc"] is None
    assert "native_layout_not_origin_verified" in result["hold_reasons"]


@pytest.mark.parametrize("mutation", ["canonical_missing", "canonical_wrong", "canonical_duplicate",
                                       "title_duplicate", "title_wrong", "coupon_missing", "partial_price",
                                       "wrong_order", "incomplete_markup", "invalid_utf8", "unknown_declaration"])
def test_native_layout_refuses_ambiguous_or_incomplete_evidence(saved, mutation):
    body = synthetic_html(saved)
    if mutation == "canonical_missing":
        body = body.replace(b'rel="canonical"', b'rel="alternate"')
    elif mutation == "canonical_wrong":
        body = body.replace(URL.encode(), (URL + "-other").encode())
    elif mutation == "canonical_duplicate":
        body = body.replace(b'</head>', f'<link rel="canonical" href="{URL}"></head>'.encode())
    elif mutation == "title_duplicate":
        body = body.replace(b'</body>', b'<h1>Benfica - Alverca</h1></body>')
    elif mutation == "title_wrong":
        body = body.replace(b'<h1>Benfica - Alverca</h1>', b'<h1>Unrelated Club - Alverca</h1>')
    elif mutation == "coupon_missing":
        body = body.replace(b'#906', b'906')
    elif mutation == "partial_price":
        body = body.replace(b'Benfica1.13Draw9.75Alverca18.00', b'Benfica1.13Alverca18.00')
    elif mutation == "wrong_order":
        body = body.replace(b'<h1>Benfica - Alverca</h1>', b'<h1>Alverca - Benfica</h1>')
    elif mutation == "incomplete_markup":
        body = body.replace(b'</body></html>', b'')
    elif mutation == "invalid_utf8":
        body += b'\xff'
    else:
        body = body.replace(b'<body>', b'<body><![INVALID[broken]]>')
    result = inspect_native_event_html(body, URL)
    assert result["observations"] == [] and result["admitted_rows"] == 0


@pytest.mark.parametrize("wrapper", ["script", "style", "template", "noscript", 'div hidden',
                                     'div aria-hidden="true"', 'div style="display:none"'])
def test_native_hidden_data_cannot_inject_markets_or_leak_secrets(saved, wrapper):
    tag = wrapper.split()[0]
    extra = f'<{wrapper}><h1>TOP_SECRET</h1>Full Time Result TOP_SECRET</{tag}>'
    body = synthetic_html(saved).replace(b'<body>', ('<body>' + extra).encode())
    result = inspect_native_event_html(body, URL)
    assert len(result["observations"]) == 28
    assert "TOP_SECRET" not in json.dumps(result)


def test_real_transport_mode_is_opt_in_and_no_green_empty(saved, probe, transport, capsys):
    transport(lambda request: response(body=synthetic_html(saved)))
    assert probe.main(["--native-url", URL, "--native-markets"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["mode"] == "native_betolimp_market_candidates_only"
    assert result["market_decoding_ok"] and result["writes"] == result["admitted_rows"] == 0
    receipt = result["receipts"][0]
    assert receipt["decoded_observation_count"] == 28
    assert receipt["kickoff_utc"] is receipt["quoted_at"] is None
    assert "native_layout_not_origin_verified" in receipt["hold_reasons"]
    transport(lambda request: response(body=b'<html><script>app()</script></html>'))
    assert probe.main(["--native-url", URL, "--native-markets"]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["transport_ok"] and not result["market_decoding_ok"]


@pytest.mark.parametrize("status", [302, 401, 403, 429, 500])
def test_denials_are_never_decoded_or_retried(saved, probe, transport, status):
    calls, _ = transport(lambda request: response(status, body=synthetic_html(saved)))
    result = probe.native_probe([URL, URL.replace("86168564", "86168565")], native_markets=True)
    assert len(calls) == 1
    assert not result["market_decoding_ok"] and not result["transport_ok"]
    assert "native_markets" not in result["receipts"][0]


@pytest.mark.parametrize("args", [
    ["--input", str(FIXTURE), "--native-markets"],
    ["--native-url", URL, "--native-source", "betway", "--native-markets"],
    ["--native-url", URL, "--native-markets", "--native-context"],
    ["--native-url", URL, "--native-markets", "--native-loader"],
    ["--native-url", URL, "--native-markets", "--browser-context"],
])
def test_native_market_flag_cannot_expand_other_source_modes(probe, args):
    with pytest.raises(SystemExit) as error:
        probe.main(args)
    assert error.value.code == 2

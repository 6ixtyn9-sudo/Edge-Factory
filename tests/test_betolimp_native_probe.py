"""Hermetic native-access contract tests; never make external HTTP requests."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import socket
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
URL = "https://betolimp.co.za/sports/soccer-betting/spain-la-liga/racing-santander-real-madrid-86106133"
URL2 = "https://betolimp.co.za/sports/soccer-betting/south-africa-super-league-women/ts-galaxy-w-stellenbosch-w-86213002"
HTML = b"<html><script>secret-script Total Goals</script><h1>Full Time Result</h1><p>Both teams to score</p></html>"


@pytest.fixture
def probe(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("external network forbidden in tests")
    monkeypatch.setattr(socket, "socket", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    spec = importlib.util.spec_from_file_location("betolimp_native_test", ROOT / "scripts/probe_betolimp.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def transport(probe, monkeypatch):
    original = httpx.Client
    requests = []
    settings = []

    def install(handler):
        def wrapped(request):
            requests.append(request)
            return handler(request)

        def factory(**kwargs):
            settings.append(kwargs)
            return original(transport=httpx.MockTransport(wrapped), **kwargs)
        monkeypatch.setattr(probe.httpx, "Client", factory)
        return requests, settings
    return install


def response(status=200, body=HTML, headers=None):
    return httpx.Response(status, headers={"content-type": "text/html", **(headers or {})},
                          stream=httpx.ByteStream(body))


def test_native_single_get_metadata_not_decoded_quotes(probe, transport):
    requests, settings = transport(lambda request: response())
    result = probe.native_probe([URL])
    assert len(requests) == result["network_requests"] == 1
    assert requests[0].method == "GET" and str(requests[0].url) == URL
    assert result["transport_ok"] and result["writes"] == result["admitted_rows"] == 0
    r = result["receipts"][0]
    assert r["evidence_kind"] == "native_http_response"
    assert r["body_sha256"] == hashlib.sha256(HTML).hexdigest()
    assert r["body_complete"] and r["sampled_body_bytes"] == len(HTML)
    assert r["classification"] == "native_html_received_unverified"
    assert r["main_market_label_presence"] == {
        "Full Time Result": True, "Total Goals": False, "Both teams to score": True}
    assert r["quoted_at"] is None and r["kickoff_utc"] is None
    assert r["decoded_observation_count"] == r["admitted_rows"] == 0
    assert "native_market_decoding_unimplemented" in r["hold_reasons"]
    assert "reader_transcription_not_native_response" not in r["hold_reasons"]
    assert settings[0]["trust_env"] is False and settings[0]["follow_redirects"] is False
    assert settings[0]["timeout"].read == 15 and settings[0]["timeout"].connect == 5
    assert requests[0].headers["accept-encoding"] == "identity"
    assert requests[0].headers["user-agent"] == "EdgeFactory-BetOlimpProbe/1.0"
    assert not any(k in requests[0].headers for k in ("authorization", "cookie", "proxy-authorization"))
    assert "secret-script" not in json.dumps(result)


@pytest.mark.parametrize("bad", [
    "http://betolimp.co.za/sports/soccer-betting/spain-la-liga/example-123",
    URL + "?token=TOP_SECRET", URL + "#fragment", URL.replace("betolimp.co.za", "other.test"),
    URL.replace("betolimp.co.za", "betolimp.co.za.evil.test"),
    URL.replace("betolimp.co.za", "user:password@betolimp.co.za"),
    URL.replace("betolimp.co.za", "betolimp.co.za:443"),
    "https://betolimp.co.za/cdn-cgi/challenge-platform/", "https://betolimp.co.za/en/user/login/",
    "https://betolimp.co.za/sports/soccer-betting/spain-la-liga", URL + "\n",
    URL.replace("racing-santander", "%72acing-santander"),
])
def test_entire_batch_validated_before_any_network(probe, transport, bad):
    requests, _ = transport(lambda request: response())
    with pytest.raises(ValueError):
        probe.native_probe([URL2, bad])
    assert not requests


@pytest.mark.parametrize("urls", [[], [URL] * 2, [URL, URL2, URL, URL2]])
def test_native_count_and_duplicate_limits(probe, transport, urls):
    requests, _ = transport(lambda request: response())
    with pytest.raises(ValueError):
        probe.native_probe(urls)
    assert not requests


@pytest.mark.parametrize("status,expected", [
    (301, "redirect_not_followed"), (302, "redirect_not_followed"),
    (401, "access_denied"), (403, "access_denied"), (429, "rate_limited"),
    (500, "http_error"), (404, "http_error"),
])
def test_no_redirect_retry_or_other_path_after_failure(probe, transport, status, expected):
    requests, _ = transport(lambda request: response(status, headers={
        "location": "http://127.0.0.1/private?TOP_SECRET", "set-cookie": "session=TOP_SECRET"}))
    r = probe.native_probe([URL, URL2])
    assert r["network_requests"] == len(requests) == 1
    assert r["requested_url_count"] == 2 and r["unattempted_urls"] == [URL2]
    assert not r["transport_ok"] and r["receipts"][0]["classification"] == expected
    assert "TOP_SECRET" not in json.dumps(r)


@pytest.mark.parametrize("body", [
    b"<title>Just a moment...</title>", b"<p>Verify you are human</p>",
    b"<p>Checking your browser</p>", b"<p>Enable JavaScript and cookies to continue</p>",
])
def test_200_challenge_stops_batch_no_bypass(probe, transport, body):
    requests, _ = transport(lambda request: response(body=body))
    r = probe.native_probe([URL, URL2])
    assert len(requests) == 1 and not r["transport_ok"]
    assert r["receipts"][0]["classification"] == "challenge_not_bypassed"


def test_regular_cdn_assets_not_classified_as_challenge(probe, transport):
    transport(lambda request: response(body=b'<script src="/cdn-cgi/assets/x.js"></script><p>Soccer</p>'))
    assert probe.native_probe([URL])["transport_ok"]


@pytest.mark.parametrize("headers,expected", [
    ({"content-type": "application/json"}, "unexpected_content_type"),
    ({"content-type": "INVALID_SECRET"}, "unexpected_content_type"),
    ({"content-encoding": "gzip"}, "unsupported_content_encoding"),
])
def test_non_html_and_encoding_not_parsed(probe, transport, headers, expected):
    transport(lambda request: response(headers=headers))
    r = probe.native_probe([URL])["receipts"][0]
    assert not r["transport_ok"] and r["classification"] == expected
    assert r["main_market_label_presence"] is None
    assert "INVALID_SECRET" not in json.dumps(r)


def test_size_cap_closes_stream_and_no_full_digest(probe, transport, monkeypatch):
    closed = []

    class Body(httpx.SyncByteStream):
        def __iter__(self):
            yield b"x" * 65536
            raise AssertionError("must stop before requesting another chunk")

        def close(self):
            closed.append(True)

    monkeypatch.setattr(probe, "MAX_NATIVE_BYTES", 1024)
    transport(lambda request: httpx.Response(200, headers={"content-type": "text/html"}, stream=Body()))
    r = probe.native_probe([URL])["receipts"][0]
    assert closed and r["classification"] == "response_size_limit"
    assert r["sampled_body_bytes"] == 1025 and not r["body_complete"]
    assert r["body_sha256"] is None and r["main_market_label_presence"] is None


@pytest.mark.parametrize("error,expected", [
    (httpx.ConnectError("TOP_SECRET"), "transport_error"),
    (httpx.ReadTimeout("TOP_SECRET"), "transport_timeout"),
])
def test_transport_failure_sanitized_no_retry(probe, transport, error, expected):
    def handler(request):
        raise error
    requests, _ = transport(handler)
    r = probe.native_probe([URL, URL2])
    assert len(requests) == 1 and not r["transport_ok"]
    assert r["receipts"][0]["classification"] == expected
    assert r["receipts"][0]["evidence_kind"] == "native_http_attempt"
    assert "TOP_SECRET" not in json.dumps(r)


def test_read_deadline_closes_response(probe, transport, monkeypatch):
    ticks = iter([0, 31])
    monkeypatch.setattr(probe.time, "monotonic", lambda: next(ticks))
    transport(lambda request: response())
    assert probe.native_probe([URL])["receipts"][0]["classification"] == "transport_timeout"


def test_each_url_fresh_client_no_cookies_or_environment_auth(probe, transport, monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://user:TOP_SECRET@127.0.0.1:12345")
    monkeypatch.setenv("SSL_CERT_FILE", "/not-a-valid-ca-path")
    requests, settings = transport(lambda request: response(headers={"set-cookie": "session=TOP_SECRET"}))
    r = probe.native_probe([URL, URL2])
    assert r["network_requests"] == len(requests) == len(settings) == 2
    assert all("cookie" not in q.headers for q in requests)
    assert all(s["trust_env"] is False for s in settings)
    assert "TOP_SECRET" not in json.dumps(r)


def test_cli_native_failure_nonzero_not_green_empty(probe, transport, capsys):
    transport(lambda request: response(403))
    assert probe.main(["--native-url", URL]) == 1
    r = json.loads(capsys.readouterr().out)
    assert not r["transport_ok"] and r["admitted_rows"] == 0


def test_cli_native_success_is_transport_only_no_files(probe, transport, capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transport(lambda request: response())
    assert probe.main(["--native-url", URL]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["transport_ok"] and r["admitted_rows"] == r["writes"] == 0
    assert not list(tmp_path.iterdir())


def test_invalid_cli_native_url_never_echoes_input(probe, capsys):
    assert probe.main(["--native-url", URL + "?TOP_SECRET"]) == 2
    out = capsys.readouterr()
    assert not out.out and "TOP_SECRET" not in out.err
    assert json.loads(out.err)["status"] == "invalid_native_input"


@pytest.mark.parametrize("args", [
    ["--input", "x.json", "--native-url", URL],
    ["--native-url", URL, "--card", "x.json"], [],
])
def test_cli_modes_exclusive(probe, args):
    with pytest.raises(SystemExit) as error:
        probe.main(args)
    assert error.value.code == 2


def test_three_distinct_urls_maximum_no_retries(probe, transport):
    third = "https://betolimp.co.za/sports/soccer-betting/england-premier-league/liverpool-arsenal-86096893"
    requests, _ = transport(lambda request: response())
    result = probe.native_probe([URL, URL2, third])
    assert result["network_requests"] == len(requests) == 3 and result["transport_ok"]
    assert result["unattempted_urls"] == []


def test_four_distinct_urls_rejected_before_network(probe, transport):
    third = "https://betolimp.co.za/sports/soccer-betting/england-premier-league/liverpool-arsenal-86096893"
    fourth = "https://betolimp.co.za/sports/soccer-betting/england-isthmian-1st-division-south-central/southall-ashford-town-86214530"
    requests, _ = transport(lambda request: response())
    with pytest.raises(ValueError):
        probe.native_probe([URL, URL2, third, fourth])
    assert not requests


def test_malformed_html_is_sanitized_not_traceback_or_green(probe, transport):
    transport(lambda request: response(body=b"<![TOP_SECRET]><p>Full Time Result</p>"))
    result = probe.native_probe([URL])
    assert not result["transport_ok"]
    assert result["receipts"][0]["classification"] == "unparseable_html"
    assert "TOP_SECRET" not in json.dumps(result)


OPEN_URL = "https://api.github.com/repos/openfootball/football.json/contents/2026-27/it.1.json"
STATS_URL = "https://api.github.com/repos/statsbomb/open-data/contents/data/matches/37/281.json"


def fixture_payload(source):
    # Synthetic contract examples, not observed predecision quotes/results.
    if source == "openfootball":
        return {"name": "Test League", "matches": [
            {"team1": "Como", "team2": "Venezia", "date": "2026-11-01", "time": "12:30"},
            {"team1": "Como", "team2": "Lazio", "date": "2026-10-01", "score": {"ft": [2, 0]}}]}
    return [{"home_team": {"home_team_name": "Como W"},
             "away_team": {"away_team_name": "Venezia W"},
             "competition": {"competition_name": "Test Women"}, "match_date": "2026-11-01",
             "kick_off": "12:30:00.000", "match_id": 123, "home_score": 0, "away_score": 0}]


@pytest.mark.parametrize("source,url", [("openfootball", OPEN_URL), ("statsbomb", STATS_URL)])
def test_explicit_json_profile_real_transport_contract(probe, transport, source, url, tmp_path):
    body = json.dumps(fixture_payload(source)).encode()
    requests, _ = transport(lambda request: response(body=body, headers={"content-type": "application/json"}))
    card = tmp_path / "card.json"
    card.write_text(json.dumps([{"home": "Como", "away": "Venezia", "date": "2026-11-01"}]))
    result = probe.native_probe([url], source=source, card_path=card)
    assert result["transport_ok"] and result["network_requests"] == len(requests) == 1
    assert requests[0].headers["accept"] == "application/vnd.github.raw+json"
    assert "authorization" not in requests[0].headers
    r = result["receipts"][0]
    assert r["classification"] == "native_json_received_unverified"
    assert r["body_sha256"] == hashlib.sha256(body).hexdigest()
    summary = r["fixture_summary"]
    assert summary["fixture_rows"] == (2 if source == "openfootball" else 1)
    assert summary["rows_with_score_pair"] == 1
    assert summary["same_date_ordered_team_candidate_rows"] == (1 if source == "openfootball" else 0)
    assert summary["complete_identity_matches"] == r["admitted_rows"] == 0
    assert r["kickoff_utc"] is None and r["quoted_at"] is None
    assert "dataset_reuse_terms_unverified" in r["hold_reasons"]
    assert "xg" in summary["not_probed"] and "standings" in summary["not_probed"]
    assert card.read_text() == json.dumps([{"home": "Como", "away": "Venezia", "date": "2026-11-01"}])


@pytest.mark.parametrize("source,url", [
    ("betolimp", OPEN_URL), ("openfootball", URL), ("openfootball", STATS_URL),
    ("statsbomb", OPEN_URL), ("unapproved", OPEN_URL),
    ("openfootball", OPEN_URL + "?access_token=TOP_SECRET"),
    ("openfootball", OPEN_URL.replace("api.github.com", "api.github.com.evil.test")),
    ("openfootball", OPEN_URL.replace("openfootball/football.json", "user/private-repo")),
    ("openfootball", OPEN_URL.replace("it.1.json", "README.md")),
    ("statsbomb", STATS_URL.replace("data/matches/37/281.json", "data/events/3913082.json")),
    ("openfootball", OPEN_URL + "#fragment"),
    ("openfootball", OPEN_URL.replace("it.1", "%69t.1")),
])
def test_json_profile_cannot_be_arbitrary_url_fetcher(probe, transport, source, url):
    requests, _ = transport(lambda request: response())
    with pytest.raises(ValueError):
        probe.native_probe([url], source=source)
    assert not requests


@pytest.mark.parametrize("payload", [
    {}, {"matches": []}, {"matches": ["invalid"]}, {"matches": [{"team1": "Como"}]},
    {"matches": [{"team1": "Como", "team2": "Venezia", "date": "not-a-date"}]},
    {"matches": [None]}, {"matches": [0] * 5001},
])
def test_json_invalid_shape_not_green_empty(probe, transport, payload):
    transport(lambda request: response(body=json.dumps(payload).encode(), headers={"content-type": "application/json"}))
    result = probe.native_probe([OPEN_URL], source="openfootball")
    assert not result["transport_ok"]
    assert result["receipts"][0]["classification"] == "invalid_fixture_json"
    assert "fixture_summary" not in result["receipts"][0]


@pytest.mark.parametrize("body", [b"TOP_SECRET not JSON", b"[[[", b'"string"'])
def test_json_parse_failure_sanitized(probe, transport, body):
    transport(lambda request: response(body=body, headers={"content-type": "application/json"}))
    result = probe.native_probe([OPEN_URL], source="openfootball")
    assert not result["transport_ok"] and "TOP_SECRET" not in json.dumps(result)


def test_same_teams_wrong_date_not_card_candidate(probe, transport, tmp_path):
    payload = fixture_payload("openfootball")
    transport(lambda request: response(body=json.dumps(payload).encode(), headers={"content-type": "application/json"}))
    p = tmp_path / "card.json"
    p.write_text(json.dumps([{"home": "Como", "away": "Venezia", "date": "2026-11-02"}]))
    result = probe.native_probe([OPEN_URL], source="openfootball", card_path=p)
    assert result["receipts"][0]["fixture_summary"]["same_date_ordered_team_candidate_rows"] == 0


def test_missing_scores_not_zero_or_settled(probe):
    payload = fixture_payload("openfootball")
    payload["matches"][1]["score"] = {"ft": [True, 0]}
    summary = probe._fixture_summary(json.dumps(payload).encode(), "openfootball", None)
    assert summary["rows_with_score_pair"] == 0
    assert summary["same_date_ordered_team_candidate_rows"] is None
    assert summary["score_period_semantics"] == "unverified_not_admitted_to_settlement"


def test_bad_card_rejected_before_any_json_request(probe, transport, tmp_path):
    requests, _ = transport(lambda request: response())
    p = tmp_path / "card.json"
    p.write_text('{"wrong": []}')
    with pytest.raises(ValueError):
        probe.native_probe([OPEN_URL], source="openfootball", card_path=p)
    assert not requests


def test_cli_json_source_and_card(probe, transport, tmp_path, capsys):
    body = json.dumps(fixture_payload("openfootball")).encode()
    transport(lambda request: response(body=body, headers={"content-type": "application/json"}))
    p = tmp_path / "card.json"
    p.write_text("[]")
    assert probe.main(["--native-source", "openfootball", "--native-url", OPEN_URL, "--card", str(p)]) == 0
    assert json.loads(capsys.readouterr().out)["receipts"][0]["source_profile"] == "openfootball"


def test_native_profile_not_used_to_relabel_reader_input(probe):
    with pytest.raises(SystemExit):
        probe.main(["--input", "unused.json", "--native-source", "statsbomb"])

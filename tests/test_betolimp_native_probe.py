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


@pytest.mark.parametrize("source", [
    "hollywoodbets", "betway", "betxchange", "sportpesa", "sportpesa-statshub",
])
def test_bookmaker_pages_reuse_bounded_transport_not_ingest(probe, transport, source):
    body = (b'<script>Last meetings</script><style>Season Statistics</style>'
            b'<nav>Head to Head Stats Hub</nav><p>Research Overall Form</p>')
    requests, settings = transport(lambda request: response(body=body))
    urls = list(probe.NATIVE_SOURCE_PAGES[source])
    result = probe.native_probe(urls, source)
    assert result["source_profile"] == source
    assert result["network_requests"] == len(requests) == len(urls) == 2
    assert result["admitted_rows"] == result["writes"] == 0
    assert "unmeasured" in result["context_status"]
    for r, request, config in zip(result["receipts"], requests, settings):
        assert r["source_profile"] == source
        assert r["decoded_context_row_count"] == r["decoded_observation_count"] == 0
        assert r["context_label_presence"]["Head to Head"]
        assert r["context_label_presence"]["Stats Hub"]
        assert r["context_label_presence"]["Overall Form"]
        assert not r["context_label_presence"]["Last meetings"]
        assert not r["context_label_presence"]["Season Statistics"]
        assert "native_context_decoding_unimplemented" in r["hold_reasons"]
        assert r["kickoff_utc"] is r["quoted_at"] is None
        assert config["trust_env"] is config["follow_redirects"] is False
        assert config["timeout"].read == 15 and config["timeout"].connect == 5
        assert request.method == "GET"
        assert request.headers["accept-encoding"] == "identity"
        assert not any(k in request.headers for k in ("cookie", "authorization"))
        supplier = source == "sportpesa-statshub"
        assert r["identified_context_supplier"] == ("sportradar" if supplier else None)
        assert r["bookmaker_brand"] == ("sportpesa" if supplier else source)
        assert r["content_origin"] == (
            "third_party_bookmaker_branded_portal" if supplier else "bookmaker_public_page")


@pytest.mark.parametrize("source", [
    "hollywoodbets", "betway", "betxchange", "sportpesa", "sportpesa-statshub",
])
@pytest.mark.parametrize("mutation", [
    "http", "credentials", "port", "fragment", "query", "newline", "other_source", "other_tenant",
])
def test_pinned_public_pages_validate_entire_batch(probe, transport, source, mutation):
    requests, _ = transport(lambda request: response())
    first, url = probe.NATIVE_SOURCE_PAGES[source]
    bad = {
        "http": url.replace("https://", "http://"),
        "credentials": url.replace("https://", "https://secret@"),
        "port": url.replace(".com/", ".com:443/").replace(".net/", ".net:443/")
                   .replace(".co.za/", ".co.za:443/"),
        "fragment": url + "#secret",
        "query": url + "?token=secret",
        "newline": url + "\n",
        "other_source": URL,
        "other_tenant": "https://statshub.sportradar.com/other/en/match/74319006",
    }[mutation]
    with pytest.raises(ValueError):
        probe.native_probe([first, bad], source)
    assert not requests


@pytest.mark.parametrize("status", [302, 403, 429])
@pytest.mark.parametrize("source", [
    "hollywoodbets", "betway", "betxchange", "sportpesa", "sportpesa-statshub",
])
def test_new_sources_keep_fail_fast_and_do_not_follow_supplier_links(probe, transport, source, status):
    requests, _ = transport(lambda request: response(status, headers={
        "location": probe.NATIVE_SOURCE_PAGES["sportpesa-statshub"][0],
        "set-cookie": "session=secret"}))
    result = probe.native_probe(list(probe.NATIVE_SOURCE_PAGES[source]), source)
    assert len(requests) == result["network_requests"] == 1
    assert len(result["unattempted_urls"]) == 1
    assert not result["transport_ok"]
    assert result["receipts"][0]["decoded_context_row_count"] == 0
    assert "session=secret" not in json.dumps(result)


def test_unknown_profile_rejected_before_network(probe, transport):
    requests, _ = transport(lambda request: response())
    with pytest.raises(ValueError):
        probe.native_probe([URL], "unknown")
    assert not requests


def test_non_betolimp_profile_cannot_relabel_saved_reader_input(probe):
    with pytest.raises(SystemExit) as error:
        probe.main(["--input", "unused.json", "--native-source", "sportpesa"])
    assert error.value.code == 2


def test_bookmaker_cli_keeps_native_provenance(probe, transport, capsys):
    requests, _ = transport(lambda request: response())
    url = probe.NATIVE_SOURCE_PAGES["sportpesa-statshub"][0]
    assert probe.main(["--native-url", url, "--native-source", "sportpesa-statshub"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert len(requests) == 1
    assert output["receipts"][0]["evidence_kind"] == "native_http_response"
    assert output["receipts"][0]["identified_context_supplier"] == "sportradar"
    assert output["admitted_rows"] == 0


@pytest.mark.parametrize('event', ['73346090','73346084','73293298','73293300','72478680'])
def test_discovered_public_match_routes_not_limited_to_two_example_events(probe,transport,event):
    url='https://statshub.sportradar.com/sportpesa/en/match/'+event
    requests,_=transport(lambda request: response())
    result=probe.native_probe([url], 'sportpesa-statshub')
    assert len(requests)==result['network_requests']==1
    assert result['receipts'][0]['identified_context_supplier']=='sportradar'
    assert result['receipts'][0]['decoded_context_row_count']==result['admitted_rows']==0


def test_whole_slate_does_not_raise_native_three_url_budget(probe,transport):
    requests,_=transport(lambda request: response())
    urls=['https://statshub.sportradar.com/sportpesa/en/match/'+str(73346090+i) for i in range(40)]
    with pytest.raises(ValueError): probe.native_probe(urls,'sportpesa-statshub')
    assert not requests


@pytest.fixture
def synthetic_native_table():
    # Synthetic semantic contract, deliberately not represented as a site capture.
    spec=importlib.util.spec_from_file_location('semantic_contract_fixture',
                                              ROOT/'tests/test_bookmaker_native_context.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.document(),module.URL


def test_opt_in_native_context_reuses_same_single_get(probe,transport,synthetic_native_table):
    body,url=synthetic_native_table
    requests,_=transport(lambda request: response(body=body))
    result=probe.native_probe([url],'sportpesa-statshub',native_context=True)
    assert result['network_requests']==len(requests)==1
    r=result['receipts'][0]
    assert r['decoded_context_row_count']==r['native_context']['decoded_context_row_count']==2
    assert r['evidence_kind']=='native_http_response'
    assert r['native_context']['evidence_kind']=='native_html_semantic_inspection'
    assert r['body_sha256']==hashlib.sha256(body).hexdigest()
    assert r['quoted_at'] is r['kickoff_utc'] is None
    assert result['admitted_rows']==r['admitted_rows']==r['decoded_observation_count']==0
    assert 'production_admission_not_implemented' in r['hold_reasons']
    assert 'native_context_decoding_unimplemented' not in r['hold_reasons']
    assert 'native_results_and_h2h_decoding_unimplemented' in r['hold_reasons']
    assert 'native_context_field_validation_pending' in r['hold_reasons']
    assert 'not_slate_coverage' in result['context_status']


def test_native_context_is_opt_in_not_silent_contract_change(probe,transport,synthetic_native_table):
    body,url=synthetic_native_table
    transport(lambda request: response(body=body))
    r=probe.native_probe([url],'sportpesa-statshub')['receipts'][0]
    assert 'native_context' not in r and r['decoded_context_row_count']==0


@pytest.mark.parametrize('status',[302,401,403,429,500])
def test_native_context_never_decodes_denial_or_redirect(probe,transport,monkeypatch,status):
    def forbidden(*args,**kwargs): raise AssertionError('must not decode failed transport')
    monkeypatch.setattr(probe,'parse_native_context_html',forbidden)
    requests,_=transport(lambda request: response(status))
    urls=list(probe.NATIVE_SOURCE_PAGES['sportpesa-statshub'])
    r=probe.native_probe(urls,'sportpesa-statshub',native_context=True)
    assert len(requests)==1 and r['unattempted_urls']==urls[1:]
    assert 'native_context' not in r['receipts'][0]


@pytest.mark.parametrize('kind',['challenge','compressed','partial','json'])
def test_native_context_does_not_inspect_unusable_bodies(probe,transport,monkeypatch,kind):
    def forbidden(*args,**kwargs): raise AssertionError('must not inspect unusable body')
    monkeypatch.setattr(probe,'parse_native_context_html',forbidden)
    body=b'<h1>Verify you are human</h1>' if kind=='challenge' else HTML
    headers={'content-encoding':'gzip'} if kind=='compressed' else (
        {'content-type':'application/json'} if kind=='json' else {})
    if kind=='partial': body=b'x'*(probe.MAX_NATIVE_BYTES+1)
    requests,_=transport(lambda request: response(body=body,headers=headers))
    r=probe.native_probe([probe.NATIVE_SOURCE_PAGES['sportpesa-statshub'][0]],
                         'sportpesa-statshub',native_context=True)
    assert len(requests)==1 and not r['transport_ok']
    assert 'native_context' not in r['receipts'][0]


def test_native_context_source_and_cli_guards(probe,transport,capsys):
    requests,_=transport(lambda request: response())
    with pytest.raises(ValueError): probe.native_probe([URL],'betolimp',native_context=True)
    with pytest.raises(SystemExit) as error: probe.main(['--native-url',URL,'--native-context'])
    assert error.value.code==2 and not requests
    url=probe.NATIVE_SOURCE_PAGES['sportpesa-statshub'][0]+'/statistics'
    assert probe.main(['--native-url',url,'--native-source','sportpesa-statshub','--native-context'])==0
    data=json.loads(capsys.readouterr().out)
    assert data['receipts'][0]['native_context']['decoded_context_row_count']==0
    assert data['admitted_rows']==0


def test_native_context_three_url_budget_unchanged(probe,transport):
    requests,_=transport(lambda request: response())
    urls=['https://statshub.sportradar.com/sportpesa/en/match/'+str(75879092+i) for i in range(4)]
    with pytest.raises(ValueError): probe.native_probe(urls,'sportpesa-statshub',native_context=True)
    assert not requests


DISCOVERY_URL='https://statshub.sportradar.com/sportpesa/en/match/75879092'
ASSET='https://statshub.sportradar.com/assets/index-ABC123.js'
ASSET2='https://statshub.sportradar.com/assets/vendor-DEF456.js'


def test_static_discovery_reuses_get_budget_and_never_replays_api(probe,transport):
    html=(f'<link rel="modulepreload" href="{ASSET2}"><script src="{ASSET}"></script>'
          '<script type="application/json">{"data":[],"secret":"DO-NOT-PRINT"}</script>')
    js=b'const route="https://widgets.fn.sportradar.com/gismo/stats_team_lastx/1200717?T=DO-NOT-PRINT";'
    def handler(request):
        if str(request.url)==DISCOVERY_URL: return response(body=html.encode())
        return response(body=js,headers={'content-type':'application/javascript'})
    requests,settings=transport(handler)
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_discovery=True)
    assert [str(q.url) for q in requests]==[DISCOVERY_URL,ASSET,ASSET2]
    assert r['network_requests']==r['requested_url_count']==3 and r['transport_ok']
    assert r['mode']=='native_static_discovery_diagnostic_only'
    assert r['admitted_rows']==r['writes']==0
    assert r['receipts'][0]['data_loading_discovery']['embedded_json_shapes']==[
        {'json_type':'object','entry_count':2,'recognized_root_fields':['data']}]
    hint=r['receipts'][1]['data_loading_discovery']
    assert hint['api_operation_reference_hints']==['stats_team_lastx']
    assert hint['sportradar_host_reference_hints']==['widgets.fn.sportradar.com']
    assert hint['coverage_status']=='static_references_only_runtime_xhr_not_observed'
    assert hint['signed_query_reference_present'] and hint['gismo_reference_present']
    assert hint['javascript_executed'] is False and hint['api_requests_made']==0
    assert 'DO-NOT-PRINT' not in json.dumps(r)
    assert all(s['trust_env'] is False and s['follow_redirects'] is False for s in settings)
    assert all('cookie' not in q.headers and 'authorization' not in q.headers for q in requests)
    assert all(x['decoded_context_row_count']==0 for x in r['receipts'])


def test_discovery_defaults_do_not_fetch_scripts(probe,transport):
    requests,_=transport(lambda request: response(body=f'<script src="{ASSET}"></script>'.encode()))
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub')
    assert len(requests)==1 and 'data_loading_discovery' not in r['receipts'][0]


@pytest.mark.parametrize('bad',[
    'https://evil.example/assets/app.js',
    '//evil.example/assets/app.js',
    'https://statshub.sportradar.com.evil.example/assets/app.js',
    '/assets/app.js?T=SECRET', '/assets/app.js#SECRET',
    '/assets/../../api/app.js', '/api/app.js',
    'http://statshub.sportradar.com/assets/app.js',
    '/assets/app.js%3FT%3DSECRET',
    'https://user:SECRET@statshub.sportradar.com/assets/app.js',
])
def test_discovery_does_not_follow_unsafe_script_references(probe,transport,bad):
    requests,_=transport(lambda request: response(body=f'<script src="{bad}"></script>'.encode()))
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_discovery=True)
    assert len(requests)==1 and r['transport_ok']
    assert r['receipts'][0]['data_loading_discovery']['script_asset_urls']==[]
    assert 'SECRET' not in json.dumps(r) and 'evil.example' not in json.dumps(r)


def test_discovery_asset_deduplication_cap_and_no_recursive_imports(probe,transport):
    html=''.join(f'<script src="/assets/app{i}.js"></script>' for i in range(4))
    html+='<script src="/assets/app0.js"></script>'
    requests,_=transport(lambda request: response(body=html.encode()) if str(request.url)==DISCOVERY_URL
                         else response(body=b'import "./secret.js"',headers={'content-type':'text/javascript'}))
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_discovery=True)
    assert len(requests)==3 and r['requested_url_count']==3
    assert [str(q.url) for q in requests[1:]]==[
        'https://statshub.sportradar.com/assets/app0.js',
        'https://statshub.sportradar.com/assets/app1.js']


@pytest.mark.parametrize('status',[302,403,429,500])
def test_discovery_stops_on_asset_failure_without_next_bundle(probe,transport,status):
    html=f'<script src="{ASSET}"></script><script src="{ASSET2}"></script>'
    requests,_=transport(lambda q: response(body=html.encode()) if str(q.url)==DISCOVERY_URL else response(status))
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_discovery=True)
    assert len(requests)==2 and not r['transport_ok']
    assert r['unattempted_urls']==[ASSET2]
    assert 'data_loading_discovery' not in r['receipts'][1]


@pytest.mark.parametrize('kind',['json','compressed','partial','html'])
def test_discovery_rejects_unusable_asset_bodies(probe,transport,kind):
    def handler(request):
        if str(request.url)==DISCOVERY_URL:
            return response(body=f'<script src="{ASSET}"></script>'.encode())
        headers={'content-type':'text/javascript'}
        if kind=='json': headers['content-type']='application/json'
        if kind=='html': headers['content-type']='text/html'
        if kind=='compressed': headers['content-encoding']='gzip'
        return response(body=b'x'*(probe.MAX_NATIVE_BYTES+1) if kind=='partial' else HTML,headers=headers)
    requests,_=transport(handler)
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_discovery=True)
    assert len(requests)==2 and not r['transport_ok']
    assert 'data_loading_discovery' not in r['receipts'][1]


def test_static_discovery_source_count_and_cli_guards(probe,transport,capsys):
    requests,_=transport(lambda request: response())
    with pytest.raises(ValueError): probe.native_probe([URL],native_discovery=True)
    with pytest.raises(ValueError): probe.native_probe([DISCOVERY_URL,DISCOVERY_URL+'/statistics'],
                                                       'sportpesa-statshub',native_discovery=True)
    with pytest.raises(ValueError): probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',
                                                       native_discovery=True,native_context=True)
    for args in (['--input','missing','--native-discovery'],
                 ['--native-url',URL,'--native-discovery'],
                 ['--native-url',DISCOVERY_URL,'--native-source','sportpesa-statshub',
                  '--native-context','--native-discovery']):
        with pytest.raises(SystemExit) as error: probe.main(args)
        assert error.value.code==2
    assert not requests
    assert probe.main(['--native-url',DISCOVERY_URL,'--native-source','sportpesa-statshub',
                       '--native-discovery'])==0
    r=json.loads(capsys.readouterr().out)
    assert r['context_status']=='static_data_loading_discovery_not_api_verification'


def test_observed_popup_feed_and_root_selected_before_framework_bundles(probe,transport):
    # Names observed in the user's native receipt; markup below is synthetic.
    names=['manifest-f46bc34a','jsx-runtime-u17CrQMm','chunk-KS7C4IRE-CJ2e9hPd',
           'index-CcCNjyHO','isStageSport-WftrK-5e','cctx-DyJSf39p','log-DevLqv9_',
           'NoDataError-BWaly07f','sports-BEIbR-MV','root-CxVTlTKo',
           'preload-helper-HAdMZFT3','index-DL8MAT8M','feeds-1NY2OSz0',
           'queryClient-CN_BYZue','useQuery-CXsOo-qR','index-DZqNKqyE']
    html=''.join(f'<script src="/assets/{name}.js"></script>' for name in names)
    requests,_=transport(lambda q: response(body=html.encode()) if str(q.url)==DISCOVERY_URL else
                         response(body=b'const name="stats_match_tableslice"',
                                  headers={'content-type':'application/x-javascript'}))
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_discovery=True)
    assert [str(q.url) for q in requests]==[DISCOVERY_URL,
        'https://statshub.sportradar.com/assets/feeds-1NY2OSz0.js',
        'https://statshub.sportradar.com/assets/root-CxVTlTKo.js']
    assert r['network_requests']==3 and r['transport_ok']
    d=r['receipts'][0]['data_loading_discovery']
    assert d['referenced_script_asset_count']==16
    assert d['asset_selection_policy']=='observed_feeds_root_context_then_reference_order'
    assert r['receipts'][1]['data_loading_discovery']['api_operation_reference_hints']==['stats_match_tableslice']
    assert all(x['admitted_rows']==x['decoded_context_row_count']==0 for x in r['receipts'])


def test_feed_module_preload_beyond_old_receipt_truncation_is_still_sampled(probe,transport):
    html=''.join(f'<link rel="modulepreload" href="/assets/vendor{i}.js">' for i in range(20))
    html+='<link rel="modulepreload" href="/assets/feeds-newHash.js">'
    html+='<script src="/assets/manifest-current.js"></script>'
    requests,_=transport(lambda q: response(body=html.encode()) if str(q.url)==DISCOVERY_URL else
                         response(body=b'export{}',headers={'content-type':'text/javascript'}))
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_discovery=True)
    assert len(requests)==3
    assert str(requests[1].url)=='https://statshub.sportradar.com/assets/feeds-newHash.js'
    d=r['receipts'][0]['data_loading_discovery']
    assert d['referenced_script_asset_count']==22 and len(d['script_asset_urls'])==16


def test_priority_never_bypasses_asset_safety_validation(probe,transport):
    html=(f'<script src="{ASSET}"></script>'
          '<script src="https://evil.example/assets/feeds-a.js"></script>'
          '<link rel="modulepreload" href="/assets/root-a.js?T=SECRET">')
    requests,_=transport(lambda q: response(body=html.encode()) if str(q.url)==DISCOVERY_URL else
                         response(body=b'export{}',headers={'content-type':'text/javascript'}))
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_discovery=True)
    assert [str(q.url) for q in requests]==[DISCOVERY_URL,ASSET]
    assert 'SECRET' not in json.dumps(r) and 'evil.example' not in json.dumps(r)


def test_native_loader_mode_one_get_no_assets_or_api_and_no_secret_output(probe,transport,capsys):
    payload={'loaderData':{'root':{'cctx':{
        'clientId':'sportpesa','language':'en','fishnetUrl':'https://widgets.fn.sportradar.com/',
        'fishnetClientAlias':'sportpesa','fishnetToken':'DO_NOT_PRINT'}}}}
    body=('<script src="'+ASSET+'"></script><script type="application/json">'+json.dumps(payload)+'</script>').encode()
    requests,settings=transport(lambda q: response(body=body))
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_loader=True)
    assert len(requests)==r['network_requests']==r['requested_url_count']==1
    assert r['mode']=='native_embedded_loader_diagnostic_only'
    assert r['context_status']=='embedded_loader_decoding_not_stats_or_api_validation'
    receipt=r['receipts'][0]
    assert receipt['loader_state']['decoded_loader_state_count']==1
    assert receipt['loader_state']['feed_config']['syntactically_complete']
    assert receipt['body_sha256']==hashlib.sha256(body).hexdigest()
    assert receipt['decoded_context_row_count']==r['admitted_rows']==r['writes']==0
    assert 'production_admission_not_implemented' in receipt['hold_reasons']
    assert 'DO_NOT_PRINT' not in json.dumps(r)
    assert len(settings)==1 and settings[0]['trust_env'] is False
    assert probe.main(['--native-source','sportpesa-statshub','--native-url',DISCOVERY_URL,'--native-loader'])==0
    output=json.loads(capsys.readouterr().out)
    assert output['receipts'][0]['loader_state']['decoded_loader_state_count']==1


def test_loader_decoding_does_not_silently_change_default_native_receipt(probe,transport):
    requests,_=transport(lambda q: response())
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub')
    assert len(requests)==1 and 'loader_state' not in r['receipts'][0]


@pytest.mark.parametrize('status',[302,401,403,429,500])
def test_loader_never_decodes_denials_or_redirects(probe,transport,monkeypatch,status):
    def forbidden(*args,**kwargs):raise AssertionError('unusable transport must not decode loader')
    monkeypatch.setattr(probe,'inspect_native_loader_state',forbidden)
    requests,_=transport(lambda q: response(status))
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_loader=True)
    assert len(requests)==1 and not r['transport_ok']
    assert 'loader_state' not in r['receipts'][0]


@pytest.mark.parametrize('kind',['challenge','json','partial','compressed'])
def test_loader_never_decodes_unusable_native_bodies(probe,transport,monkeypatch,kind):
    def forbidden(*args,**kwargs):raise AssertionError('unusable transport must not decode loader')
    monkeypatch.setattr(probe,'inspect_native_loader_state',forbidden)
    headers={'content-type':'application/json'} if kind=='json' else (
        {'content-encoding':'gzip'} if kind=='compressed' else {})
    body=b'verify you are human' if kind=='challenge' else (
        b'x'*(probe.MAX_NATIVE_BYTES+1) if kind=='partial' else HTML)
    requests,_=transport(lambda q: response(body=body,headers=headers))
    r=probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',native_loader=True)
    assert len(requests)==1 and not r['transport_ok']
    assert 'loader_state' not in r['receipts'][0]


def test_loader_mode_preflight_guards_make_no_network_request(probe,transport):
    requests,_=transport(lambda q: response())
    with pytest.raises(ValueError):probe.native_probe([URL],native_loader=True)
    with pytest.raises(ValueError):probe.native_probe([DISCOVERY_URL,DISCOVERY_URL+'/statistics'],
                                                      'sportpesa-statshub',native_loader=True)
    for flag in ('native_context','native_discovery'):
        with pytest.raises(ValueError):probe.native_probe([DISCOVERY_URL],'sportpesa-statshub',
                                                         native_loader=True,**{flag:True})
    for args in (['--input','missing','--native-loader'],
                 ['--native-url',URL,'--native-loader'],
                 ['--native-source','sportpesa-statshub','--native-url',DISCOVERY_URL,
                  '--native-loader','--native-discovery'],
                 ['--native-source','sportpesa-statshub','--native-url',DISCOVERY_URL,
                  '--native-loader','--card','missing']):
        with pytest.raises(SystemExit) as error:probe.main(args)
        assert error.value.code==2
    assert not requests


def test_loader_decode_failure_is_not_successful_cli_even_when_http_is_ok(probe,transport,capsys):
    requests,_=transport(lambda q: response(body=b'<h1>public page without supported loader</h1>'))
    assert probe.main(['--native-source','sportpesa-statshub','--native-url',DISCOVERY_URL,
                       '--native-loader'])==1
    r=json.loads(capsys.readouterr().out)
    assert len(requests)==1 and r['transport_ok'] and not r['loader_decoding_ok']
    assert r['receipts'][0]['loader_state']['status']=='no_supported_transfer_found'
    assert r['admitted_rows']==0


def test_loader_payload_evidence_survives_cli_without_values_or_extra_requests(probe,transport,capsys):
    payload={'loaderData':{'root':{
        'cctx':{'fishnetToken':'DO_NOT_PRINT'},
        'cache':{'match':{'id':75879092,'kickoff':'2026-11-01T10:00:00Z',
                          'results':{'AP':{'home':4,'away':3}}}}}}}
    body=('<script type="application/json">'+json.dumps(payload)+'</script>').encode()
    requests,_=transport(lambda q: response(body=body))
    assert probe.main(['--native-source','sportpesa-statshub','--native-url',DISCOVERY_URL,
                       '--native-loader'])==0
    text=capsys.readouterr().out
    output=json.loads(text)
    loader=output['receipts'][0]['loader_state']
    evidence=loader['payload_evidence']
    assert len(requests)==output['network_requests']==1
    assert output['loader_decoding_ok'] and output['admitted_rows']==output['writes']==0
    assert not evidence['fixture_identity_verified'] and not evidence['regulation_periods_verified']
    match=next(s for s in evidence['sections'] if s['section']=='match')
    identity=next(f for f in match['shape'] if f['path']==['id'])
    assert identity['equals_requested_event_id']
    assert loader['fixture_binding_status']=='not_verified' and loader['kickoff_utc'] is None
    assert 'DO_NOT_PRINT' not in text and '2026-11-01T10:00:00Z' not in text
    assert '75879092' not in json.dumps(evidence)

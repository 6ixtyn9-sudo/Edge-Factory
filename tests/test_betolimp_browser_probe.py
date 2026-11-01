"""Socket-denied browser adapter contracts; these are NOT live StatsHub evidence."""
from __future__ import annotations

import importlib.util
import json
import socket
from pathlib import Path
from types import SimpleNamespace

import pytest

URL = "https://statshub.sportradar.com/sportpesa/en/match/74303326"
SECRET = "DO_NOT_EXPORT_PRIVATE_TOKEN"
FIXTURE = {"event_id": "74303326", "_seasonid": "139328", "_utid": "373",
           "home": {"team_id": "88033", "team_uid": "1963"},
           "away": {"team_id": "88016", "team_uid": "1974"}}
FEED = "https://sh.fn.sportradar.com/sportpesa/en/Etc:UTC/gismo/"


@pytest.fixture
def probe(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("tests must not access network")
    monkeypatch.setattr(socket, "socket", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    spec = importlib.util.spec_from_file_location(
        "betolimp_browser_test", Path(__file__).resolve().parents[1] / "scripts/probe_betolimp.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lastx():
    return {"doc": [{"data": {"team": {"_id": 1963, "token": SECRET}, "matches": [{
        "_id": 123, "_sid": 1, "_seasonid": 139328, "_utid": 373,
        "_dt": {"uts": 1793444400, "tz": SECRET}, "time": {"uts": 1793444400},
        "teams": {"home": {"_id": 88033, "uid": 1963, "name": SECRET},
                  "away": {"_id": 88016, "uid": 1974}},
        "result": {"home": 0, "away": 1, "winner": SECRET},
        "periods": {"ft": {"home": 0, "away": 1}, "unknown": SECRET},
        "status": {"_id": 100, "name": SECRET}, "token": SECRET,
    }]}}]}


class Request:
    def __init__(self, url=URL, resource_type="document", method="GET", redirected_from=None):
        self.url, self.resource_type, self.method = url, resource_type, method
        self.redirected_from = redirected_from


class Route:
    def __init__(self, request):
        self.request, self.allowed, self.aborted = request, False, False

    def continue_(self):
        self.allowed = True

    def abort(self):
        self.aborted = True


class Response:
    def __init__(self, request, body, status=200, headers=None):
        self.request, self.url, self.status = request, request.url, status
        self.headers = headers or {"content-type": "application/json"}
        self._body = body
        self.body_reads = 0

    def body(self):
        self.body_reads += 1
        return self._body


class Browser:
    """Runs registered route/response callbacks, never Chromium or HTTP."""
    def __init__(self, responses, *, navigation_error=False):
        self.responses = responses
        self.navigation_error = navigation_error
        self.routes = []
        self.closed = False
        self.waits = []
        self.launch_settings = {}
        self.context_settings = {}
        self.events = {}
        self.chromium = self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def launch(self, **kwargs):
        self.launch_settings = kwargs
        return self

    def new_context(self, **kwargs):
        self.context_settings = kwargs
        return self

    def route(self, pattern, callback):
        assert pattern == "**/*"
        self.router = callback

    def route_web_socket(self, pattern, callback):
        assert pattern == "**/*"
        self.websocket_router = callback

    def new_page(self):
        return self

    def on(self, name, callback):
        self.events[name] = callback

    def goto(self, url, **kwargs):
        assert url == URL and kwargs == {"wait_until": "domcontentloaded", "timeout": 20000}
        if self.navigation_error:
            raise RuntimeError(SECRET)
        for response in self.responses:
            route = Route(response.request)
            self.routes.append(route)
            self.router(route)
            if route.allowed:
                self.events["response"](response)

    def wait_for_timeout(self, timeout):
        assert 0 <= timeout <= 8000
        self.waits.append(timeout)

    def close(self):
        self.closed = True


def install_browser(probe, monkeypatch, responses, **kwargs):
    browser = Browser(responses, **kwargs)
    monkeypatch.setattr(probe, "_browser_runtime", lambda: browser)
    # Transport/loader parsing have their own full contract tests. No fake raw
    # payload is claimed as actual delivered history or usable form here.
    def receipt(response, body, complete, **kwargs):
        assert response.status_code == 200 and body == b"<html>safe document</html>"
        assert response.headers == {"content-type": "text/html"}
        return {"transport_ok": True, "loader_state": {
            "fixture_candidate": {"fixture": FIXTURE, "candidate_fixture_count": 1}}}
    monkeypatch.setattr(probe, "_native_receipt", receipt)
    return browser


def document():
    return Response(Request(), b"<html>safe document</html>",
                    headers={"content-type": "text/html", "content-encoding": "gzip"})


def history_response():
    return Response(Request(FEED + "stats_team_lastx/1963/20?T=" + SECRET, "fetch"),
                    json.dumps(lastx()).encode())


def test_single_page_natural_history_read_sanitized_never_admitted(probe, monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", SECRET)
    monkeypatch.setenv("PINNAPI_KEY", SECRET)
    browser = install_browser(probe, monkeypatch, [document(), history_response()])
    result = probe.browser_context_probe(URL)
    assert result["transport_ok"] and result["javascript_enabled"]
    assert result["network_requests"] == 2 and result["page_initiated_feed_requests"] == 1
    sample = result["statistic_samples"][0]
    assert sample["owner_team_uid"] == 1963 and sample["response_match_count"] == 1
    assert sample["matches"][0]["result"] == {"home": 0, "away": 1}
    assert sample["matches"][0]["periods"] == {"ft": {"home": 0, "away": 1}}
    assert sample["matches"][0]["status"] == {"_id": 100}
    assert result["usable_form_rows"] == result["admitted_rows"] == result["application_data_writes"] == 0
    assert result["regulation_verified"] is result["whole_slate_coverage_verified"] is False
    assert SECRET not in json.dumps(result) and SECRET not in json.dumps(browser.launch_settings)
    assert browser.closed
    assert browser.context_settings == {"service_workers": "block", "accept_downloads": False}


@pytest.mark.parametrize("tail,resource,expected", [
    ("stats_team_lastx/1963/20?T=" + SECRET, "fetch", "history:1963"),
    ("stats_team_lastx/1974/20", "xhr", "history:1974"),
    ("stats_team_lastx/1963/50", "fetch", None),
    ("stats_team_lastx/1000/20", "fetch", None),
    ("stats_team_lastx/88033/20", "fetch", None),  # team_id is NOT UID
    ("stats_team_lastx/1963/20/1", "fetch", None),
    ("stats_season_tables/139328", "fetch", "standings:139328"),
    ("stats_season_tables/373", "fetch", None),
    ("stats_season_tables/139328/1", "fetch", None),
    ("stats_match_head2head/74303326", "fetch", "support"),
    ("unknown/1", "fetch", None),
    ("config_tree_mini/1", "fetch", "support"),
])
def test_bound_page_initiated_feed_allowlist(probe, tail, resource, expected):
    assert probe._browser_request_kind(FEED + tail, resource, URL, FIXTURE) == expected


@pytest.mark.parametrize("url,resource", [
    ("http://sh.fn.sportradar.com/gismo/stats_team_lastx/1963/20", "fetch"),
    ("https://sh.fn.sportradar.com.evil.invalid/gismo/stats_team_lastx/1963/20", "fetch"),
    ("https://user:pass@sh.fn.sportradar.com/gismo/stats_team_lastx/1963/20", "fetch"),
    ("https://sh.fn.sportradar.com:444/gismo/stats_team_lastx/1963/20", "fetch"),
    ("https://127.0.0.1/gismo/stats_team_lastx/1963/20", "fetch"),
    ("https://statshub.sportradar.com/assets/../private.js", "script"),
    ("https://statshub.sportradar.com/api/private", "fetch"),
    (URL + "/statistics", "document"),
    ("https://statshub.sportradar.com/assets/image.png", "image"),
    (FEED + "stats_team_lastx/1963/20#" + SECRET, "fetch"),
    (FEED + "stats_team_lastx/1963/20", "document"),
])
def test_other_hosts_documents_private_routes_and_nonessential_resources_blocked(probe, url, resource):
    assert probe._browser_request_kind(url, resource, URL, FIXTURE) is None


def test_assets_allowed_before_anchor_but_feeds_require_anchor(probe):
    assert probe._browser_request_kind(
        "https://statshub.sportradar.com/assets/index-1234.js", "script", URL, None) == "asset"
    assert probe._browser_request_kind(FEED + "stats_team_lastx/1963/20", "fetch", URL, None) is None


@pytest.mark.parametrize("method,redirect", [("POST", None), ("GET", object())])
def test_posts_and_redirects_not_followed(probe, monkeypatch, method, redirect):
    response = history_response()
    response.request.method = method
    response.request.redirected_from = redirect
    browser = install_browser(probe, monkeypatch, [document(), response])
    result = probe.browser_context_probe(URL)
    assert result["blocked_requests"] == 1 and result["network_requests"] == 1
    assert response.body_reads == 0 and browser.routes[1].aborted
    assert not result["statistic_samples"]


def test_no_second_document_retry_or_popup_navigation(probe, monkeypatch):
    browser = install_browser(probe, monkeypatch, [document(), document()])
    result = probe.browser_context_probe(URL)
    assert result["blocked_requests"] == 1 and result["network_requests"] == 1
    assert browser.routes[1].aborted
    popup = SimpleNamespace(close=lambda: setattr(popup, "closed", True))
    browser.events["page"](popup)
    assert popup.closed


@pytest.mark.parametrize("status", [401, 403, 429])
def test_denial_stops_remaining_requests_no_bypass(probe, monkeypatch, status):
    denied = history_response()
    denied.status = status
    browser = install_browser(probe, monkeypatch, [document(), denied, history_response()])
    result = probe.browser_context_probe(URL)
    assert result["status"] == "access_denied_not_bypassed" and not result["transport_ok"]
    assert denied.body_reads == 0 and browser.routes[-1].aborted
    assert not result["statistic_samples"] and browser.closed


def test_challenge_not_processed_or_bypassed(probe, monkeypatch):
    browser = install_browser(probe, monkeypatch, [document(), history_response()])
    monkeypatch.setattr(probe, "_native_receipt", lambda *a, **kw: {"transport_ok": False})
    result = probe.browser_context_probe(URL)
    assert result["status"] == "page_rejected_not_bypassed"
    assert not result["transport_ok"] and browser.routes[-1].aborted


@pytest.mark.parametrize("budget", ["_BROWSER_MAX_REQUESTS", "_BROWSER_MAX_FEEDS"])
def test_request_budget_fails_closed_without_retries(probe, monkeypatch, budget):
    monkeypatch.setattr(probe, budget, 1)
    browser = install_browser(probe, monkeypatch, [document(), history_response(), history_response()])
    result = probe.browser_context_probe(URL)
    assert not result["transport_ok"] and result["request_limit_reached"]
    assert browser.routes[-1].aborted


def test_expired_time_budget_blocks_navigation(probe, monkeypatch):
    browser = install_browser(probe, monkeypatch, [document(), history_response()])
    ticks = iter([0, 31, 32])
    monkeypatch.setattr(probe.time, "monotonic", lambda: next(ticks))
    result = probe.browser_context_probe(URL)
    assert result["network_requests"] == 0 and result["request_limit_reached"]
    assert not result["transport_ok"] and all(r.aborted for r in browser.routes)


@pytest.mark.parametrize("headers,body", [
    ({"content-length": str(3 * 1024 * 1024)}, b"{}"),
    ({"content-length": SECRET}, b"{}"),
    ({}, b"x" * (2 * 1024 * 1024 + 1)),
    ({}, SECRET.encode()),
])
def test_oversize_and_invalid_json_fail_closed_without_body_output(probe, monkeypatch, headers, body):
    bad = history_response()
    bad.headers, bad._body = headers, body
    browser = install_browser(probe, monkeypatch, [document(), bad, history_response()])
    result = probe.browser_context_probe(URL)
    assert result["status"] == "response_inspection_failed" and not result["transport_ok"]
    assert SECRET not in json.dumps(result) and browser.closed and browser.routes[-1].aborted
    if headers:
        assert bad.body_reads == 0


@pytest.mark.parametrize("failure", ["package", "launch", "navigation", "close"])
def test_all_runtime_failures_are_sanitized_no_fallback(probe, monkeypatch, failure):
    browser = install_browser(probe, monkeypatch, [document()], navigation_error=failure == "navigation")

    def fail(*args, **kwargs):
        raise RuntimeError(SECRET)

    if failure == "package":
        monkeypatch.setattr(probe, "_browser_runtime", fail)
    elif failure == "launch":
        monkeypatch.setattr(browser, "launch", fail)
    elif failure == "close":
        monkeypatch.setattr(browser, "close", fail)
    result = probe.browser_context_probe(URL)
    assert SECRET not in json.dumps(result)
    assert not result["transport_ok"]


@pytest.mark.parametrize("argv", [
    ["--input", "file.json", "--browser-context"],
    ["--native-url", URL, "--browser-context"],
    ["--native-source", "sportpesa-statshub", "--native-url", URL, "--native-url", URL, "--browser-context"],
    *[["--native-source", "sportpesa-statshub", "--native-url", URL, "--browser-context", flag]
      for flag in ("--native-loader", "--native-discovery", "--native-context", "--card")],
])
def test_cli_rejects_ambiguous_or_offline_browser_invocations(probe, argv):
    with pytest.raises(SystemExit) as error:
        probe.main(argv)
    assert error.value.code == 2


def test_cli_dispatches_only_explicit_browser_mode(probe, monkeypatch, capsys):
    monkeypatch.setattr(probe, "browser_context_probe", lambda url, **kw: {"transport_ok": False, "status": "missing"})
    def forbid(*a, **kw):
        raise AssertionError("must not call one-GET fallback")
    monkeypatch.setattr(probe, "native_probe", forbid)
    assert probe.main(["--native-source", "sportpesa-statshub", "--native-url", URL, "--browser-context"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "missing"


def test_projection_keeps_zero_but_not_booleans_strings_or_missing_defaults(probe):
    sample = probe._browser_numeric_sample({"_id": 1, "points": True, "won": "3", "lost": 0,
                                           "result": {"home": 0}, "token": SECRET})
    assert sample == {"_id": 1, "lost": 0, "result": {"home": 0}}
    assert probe._browser_numeric_sample(None) == {}


def test_table_projection_is_not_claimed_as_standings_binding(probe):
    body = json.dumps({"doc": [{"data": {"tables": [{"_id": 8, "name": SECRET,
        "tablerows": [{"pos": 1, "team": {"_id": 1963, "name": SECRET}, "points": 9}]}]}}]}).encode()
    sample = probe._browser_stat_sample(body, "standings:139328")
    assert sample == {"status": "public_numeric_field_samples_only", "tables": [
        {"table": {"_id": 8}, "rows": [{"pos": 1, "team": {"_id": 1963}, "points": 9}]}]}
    assert "season_id" not in json.dumps(sample) and SECRET not in json.dumps(sample)


@pytest.mark.parametrize("body,kind,status", [
    ({}, "history:1963", "unsupported_document_envelope"),
    ({"doc": [{}, {}]}, "history:1963", "unsupported_document_envelope"),
    ({"doc": [{}]}, "history:1963", "unsupported_data_envelope"),
    ({"doc": [{"data": {}}]}, "history:1963", "unsupported_or_unbound_history_envelope"),
    ({"doc": [{"data": {"team": {"_id": 88033}, "matches": []}}]}, "history:1963", "unsupported_or_unbound_history_envelope"),
    ({"doc": [{"data": {"team": {"_id": 1963}, "matches": [1]}}]}, "history:1963", "unsupported_or_unbound_history_envelope"),
    ({"doc": [{"data": {"tables": {}}}]}, "standings:139328", "unsupported_table_envelope"),
    ({"doc": [{"data": {"tables": [{}]}}]}, "standings:139328", "unsupported_table_rows"),
])
def test_unknown_shapes_remain_unknown_not_zero_statistics(probe, body, kind, status):
    sample = probe._browser_stat_sample(json.dumps(body).encode(), kind)
    assert sample == {"status": status}


def test_browser_document_reuses_real_existing_loader_and_challenge_validation(probe, monkeypatch):
    match = {"_doc": "match", "_id": 74303326, "_sid": 1, "_rcid": 13, "_tid": 283,
             "_utid": 373, "_seasonid": 139328, "_dt": {"uts": 1793559600, "tz": "UTC"},
             "teams": {"home": {"_id": 88033, "uid": 1963, "name": "Palmeiras"},
                       "away": {"_id": 88016, "uid": 1974, "name": "Vasco"}},
             "status": {"_id": 0, "name": "Not started"}, "updated_uts": 1793530000}
    envelope = {"match": match, "sport": {"_id": 1}, "realcategory": {"_id": 13},
                "tournament": {"_id": 283}, "uniquetournament": {"_id": 373},
                "season": {"_id": 139328}}
    body = ('<html><script type="application/json">' +
            json.dumps({"loaderData": {"root": envelope}}) + '</script></html>').encode()
    real_receipt = probe._native_receipt
    browser = install_browser(probe, monkeypatch, [
        Response(Request(), body, headers={"content-type": "text/html", "content-encoding": "gzip"}),
        history_response()])
    monkeypatch.setattr(probe, "_native_receipt", real_receipt)
    result = probe.browser_context_probe(URL)
    assert result["transport_ok"] and browser.closed
    fixture = result["fixture_candidate"]["fixture"]
    assert fixture["home"]["team_uid"] == "1963" and fixture["away"]["team_uid"] == "1974"
    assert fixture["_seasonid"] == "139328"
    assert result["statistic_samples"][0]["response_match_count"] == 1
    # Same real inspector rejects a challenge before supplier requests can proceed.
    browser.responses = [Response(Request(), b"<html>Verify you are human</html>",
                                  headers={"content-type": "text/html"}), history_response()]
    result = probe.browser_context_probe(URL)
    assert not result["transport_ok"] and result["status"] == "page_rejected_not_bypassed"
    assert not result["statistic_samples"] and browser.routes[-1].aborted


def test_missing_fixture_cannot_trigger_supplier_dependencies(probe, monkeypatch):
    browser = install_browser(probe, monkeypatch, [document(), history_response()])
    monkeypatch.setattr(probe, "_native_receipt", lambda *a, **kw: {"transport_ok": True})
    result = probe.browser_context_probe(URL)
    assert result["transport_ok"] and result["fixture_candidate"] == {}
    assert not result["statistic_samples"] and browser.routes[-1].aborted


def test_websockets_are_closed_without_connection(probe, monkeypatch):
    browser = install_browser(probe, monkeypatch, [document()])
    probe.browser_context_probe(URL)
    connection = SimpleNamespace(close=lambda: setattr(connection, "closed", True))
    browser.websocket_router(connection)
    assert connection.closed


def test_first_response_only_is_explicit_not_copy_corroboration(probe, monkeypatch):
    first, second = history_response(), history_response()
    browser = install_browser(probe, monkeypatch, [document(), first, second])
    result = probe.browser_context_probe(URL)
    assert result["transport_ok"] and len(result["statistic_samples"]) == 1
    assert first.body_reads == 1 and second.body_reads == 0
    assert result["sample_policy"] == "first_completed_response_per_kind_not_cross_copy_validation"
    assert browser.closed


@pytest.mark.parametrize("url", [
    URL + "?T=" + SECRET, URL + "/private", URL.replace("sportpesa", "other"),
    "http://statshub.sportradar.com/sportpesa/en/match/74303326",
])
def test_invalid_source_rejected_before_browser_start(probe, monkeypatch, url):
    def forbidden():
        raise AssertionError("invalid source must not start a browser")
    monkeypatch.setattr(probe, "_browser_runtime", forbidden)
    with pytest.raises(ValueError):
        probe.browser_context_probe(url)


def test_overlong_response_sets_are_rejected_or_explicitly_sampled(probe):
    payload = lastx()
    payload["doc"][0]["data"]["matches"] *= 21
    sample = probe._browser_stat_sample(json.dumps(payload).encode(), "history:1963")
    assert sample["sample_truncated"] and len(sample["matches"]) == 20
    payload["doc"][0]["data"]["matches"] *= 5
    sample = probe._browser_stat_sample(json.dumps(payload).encode(), "history:1963")
    assert sample == {"status": "unsupported_or_unbound_history_envelope"}
    with pytest.raises(ValueError):
        probe._browser_stat_sample(b"x" * (2 * 1024 * 1024 + 1), "history:1963")


@pytest.mark.parametrize("actions,environment,os_name", [
    ("", "github-hosted", "Linux"), ("true", "self-hosted", "Linux"),
    ("true", "github-hosted", "Windows"), ("false", "github-hosted", "Linux"),
])
def test_browser_install_never_runs_outside_explicit_hosted_linux_runner(
        probe, monkeypatch, actions, environment, os_name):
    import subprocess
    monkeypatch.setenv("GITHUB_ACTIONS", actions)
    monkeypatch.setenv("RUNNER_ENVIRONMENT", environment)
    monkeypatch.setenv("RUNNER_OS", os_name)
    def forbidden(*a, **kw):
        raise AssertionError("must not install outside hosted Actions")
    monkeypatch.setattr(subprocess, "run", forbidden)
    assert probe._browser_setup_runtime() is False
    result = probe.browser_context_probe(URL, install_runtime=True)
    assert not result["transport_ok"] and result["network_requests"] == 0
    assert result["status"] == "browser_runtime_setup_failed_or_not_hosted_runner"


@pytest.mark.parametrize("failure", [None, "pip", "browser", "timeout"])
def test_hosted_setup_uses_fixed_pinned_commands_and_no_secret_output(probe, monkeypatch, failure):
    import subprocess
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("RUNNER_ENVIRONMENT", "github-hosted")
    monkeypatch.setenv("RUNNER_OS", "Linux")
    monkeypatch.setenv("RELAY_TOKEN", SECRET)
    monkeypatch.setenv("HTTP_PROXY", SECRET)
    monkeypatch.setenv("PIP_INDEX_URL", SECRET)
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        assert kwargs["check"] and kwargs["timeout"] <= 120
        assert kwargs["stdout"] == kwargs["stderr"] == subprocess.DEVNULL
        assert SECRET not in json.dumps(kwargs) and "shell" not in kwargs
        if (failure == "pip" and len(calls) == 1) or (failure == "browser" and len(calls) == 2):
            raise subprocess.CalledProcessError(1, SECRET)
        if failure == "timeout":
            raise subprocess.TimeoutExpired(SECRET, 60)
    monkeypatch.setattr(subprocess, "run", run)
    assert probe._browser_setup_runtime() is (failure is None)
    assert len(calls) == (2 if failure in (None, "browser") else 1)
    assert calls[0][-1] == "playwright==1.56.0"
    if len(calls) == 2:
        assert calls[1] == [probe.sys.executable, "-m", "playwright", "install",
                            "--with-deps", "--only-shell", "chromium"]


def test_runtime_setup_only_if_explicit_and_before_page_budget(probe, monkeypatch):
    browser = install_browser(probe, monkeypatch, [document()])
    events = []
    monkeypatch.setattr(probe, "_browser_setup_runtime", lambda: events.append("setup") or True)
    monkeypatch.setattr(probe.time, "monotonic", lambda: events.append("page_clock") or 0)
    result = probe.browser_context_probe(URL)
    assert result["transport_ok"] and "setup" not in events
    events.clear()
    result = probe.browser_context_probe(URL, install_runtime=True)
    assert result["transport_ok"] and events[0] == "setup" and events[1] == "page_clock"
    assert browser.closed


def test_cli_runtime_install_requires_explicit_browser_mode(probe):
    with pytest.raises(SystemExit) as error:
        probe.main(["--native-url", URL, "--browser-install-runtime"])
    assert error.value.code == 2

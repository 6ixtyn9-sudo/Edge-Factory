from __future__ import annotations

from datetime import date

import pytest

from edgefactory.sources import bzzoiro, bzzoiro_odds


def test_bzzoiro_missing_token_is_retryable_failure(monkeypatch):
    monkeypatch.setattr(bzzoiro, "TOKEN", None)

    with pytest.raises(RuntimeError, match="BZZOIRO_TOKEN missing"):
        bzzoiro.fetch_day(date.today().isoformat())


def test_bzzoiro_odds_missing_token_is_retryable_failure(monkeypatch):
    monkeypatch.setattr(bzzoiro_odds, "TOKEN", None)

    with pytest.raises(RuntimeError, match="BZZOIRO_TOKEN missing"):
        bzzoiro_odds.fetch_day(date.today().isoformat())


@pytest.mark.parametrize('adapter', [bzzoiro, bzzoiro_odds])
@pytest.mark.parametrize('status', [400, 401, 402, 403, 404, 429, 430, 509])
def test_rejected_request_is_not_retried(adapter, status, monkeypatch):
    import urllib.error
    calls, sleeps = [], []
    monkeypatch.setattr(adapter, 'TOKEN', 'test-token-not-a-real-credential')
    if adapter is bzzoiro_odds:
        adapter._reset_diagnostics()
    def rejected(request, timeout):
        calls.append(request.full_url)
        raise urllib.error.HTTPError(request.full_url, status, 'provider rejected', {}, None)
    monkeypatch.setattr(adapter.urllib.request, 'urlopen', rejected)
    monkeypatch.setattr(adapter.time, 'sleep', sleeps.append)
    with pytest.raises(urllib.error.HTTPError) as failure:
        adapter._get('https://sports.bzzoiro.com/api/v2/test/', retries=3)
    assert failure.value.code == status
    assert len(calls) == 1
    assert sleeps == []
    if adapter is bzzoiro_odds:
        assert adapter.diagnostics()['http_statuses'] == [status]
        assert adapter.diagnostics()['requests'] == 1
        assert 'test-token-not-a-real-credential' not in str(adapter.diagnostics())


@pytest.mark.parametrize('adapter', [bzzoiro, bzzoiro_odds])
@pytest.mark.parametrize('status', [408, 500, 502, 503])
def test_transient_http_failure_keeps_bounded_retries(adapter, status, monkeypatch):
    import urllib.error
    calls, sleeps = [], []
    if adapter is bzzoiro_odds:
        adapter._reset_diagnostics()
    def unavailable(request, timeout):
        calls.append(request.full_url)
        raise urllib.error.HTTPError(request.full_url, status, 'temporarily unavailable', {}, None)
    monkeypatch.setattr(adapter.urllib.request, 'urlopen', unavailable)
    monkeypatch.setattr(adapter.time, 'sleep', sleeps.append)
    with pytest.raises(urllib.error.HTTPError):
        adapter._get('https://sports.bzzoiro.com/api/v2/test/', retries=3)
    assert len(calls) == 3
    assert sleeps == [1.5, 3.0]


@pytest.mark.parametrize('adapter', [bzzoiro, bzzoiro_odds])
def test_rejection_does_not_disable_independent_endpoint(adapter, monkeypatch):
    import io
    import urllib.error
    if adapter is bzzoiro_odds:
        adapter._reset_diagnostics()
    def response(request, timeout):
        if request.full_url.endswith('/denied/'):
            raise urllib.error.HTTPError(request.full_url, 403, 'denied', {}, None)
        return io.BytesIO(b'{"results": [{"id": 17}]}')
    monkeypatch.setattr(adapter.urllib.request, 'urlopen', response)
    with pytest.raises(urllib.error.HTTPError):
        adapter._get('https://sports.bzzoiro.com/api/v2/denied/')
    assert adapter._get('https://sports.bzzoiro.com/api/v2/available/') == {'results': [{'id': 17}]}
